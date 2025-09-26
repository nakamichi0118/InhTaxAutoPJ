import google.generativeai as genai
import base64
import json
import tempfile
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger
import asyncio
import re

from core.config import settings
from models.document import DocumentCategory, PassbookTransaction

class GeminiOCRService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Use the latest and most capable model for PDF processing
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
    async def process_passbook(self, image_base64: str, include_handwriting: bool = False) -> List[Dict[str, Any]]:
        """
        通帳画像を処理して取引データを抽出
        既存の通帳.jsのロジックをPythonに移植
        """
        try:
            current_year = datetime.now().year
            reiwa_start_year = 2019
            current_reiwa_year = current_year - reiwa_start_year + 1
            
            handwriting_instruction = (
                "手書きの文字や数字も認識に含めてください。" if include_handwriting
                else "手書きと思われる文字や数字は無視し、印字された文字を中心に認識してください。"
            )
            
            dakuten_instruction = """日本語の文字認識、特に濁点（゛）や半濁点（゜）の識別は非常に重要です。
例えば、「シ」と「ジ」、「ハ」と「バ」と「パ」、「カ」と「ガ」、「タ」と「ダ」などを正確に見分けてください。"""
            
            prompt = f"""この通帳の画像から取引明細を抽出してください。画像の最下部まで、全ての行を注意深く読み取ってください。
{dakuten_instruction}

以下のJSONスキーマに厳密に従って結果を返してください。
各取引について、取引日（yyyy-mm-dd形式、不明な場合はnull）、出金額（半角整数、該当なければ0）、入金額（半角整数、該当なければ0）、残高（半角整数、不明な場合はnull）、取引内容（文字列、摘要など、不明な場合は空文字）を抽出してください。

日付の年は西暦 (yyyy-mm-dd形式) でお願いします。
現在の西暦年は {current_year}年 (令和{current_reiwa_year}年) です。

金額が「***」や「---」のようにマスクされている場合は0としてください。
繰り越し行など、出金額と入金額が両方とも0になるような実質的な取引ではない行は抽出対象外としてください。
{handwriting_instruction}

出力形式:
[
  {{
    "取引日": "yyyy-mm-dd",
    "出金額": 0,
    "入金額": 0,
    "残高": 0,
    "取引内容": ""
  }}
]"""
            
            # Prepare the image
            image_data = base64.b64decode(image_base64)
            
            # Call Gemini API
            response = self.model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": image_data}
            ], generation_config={
                "temperature": 0.1,
                "response_mime_type": "application/json"
            })
            
            # Parse response
            result = json.loads(response.text)
            
            # Filter out zero transactions
            filtered_result = [
                item for item in result
                if not (item.get("出金額", 0) == 0 and item.get("入金額", 0) == 0)
            ]
            
            # Verify balances
            if not self._verify_balances(filtered_result):
                logger.warning("残高検算が一致しませんでした。再分析を試みます。")
                # 再分析ロジックをここに実装可能
            
            return filtered_result
            
        except Exception as e:
            logger.error(f"通帳OCR処理エラー: {str(e)}")
            raise
    
    def _verify_balances(self, transactions: List[Dict[str, Any]]) -> bool:
        """残高検算を行う"""
        if not transactions or len(transactions) < 2:
            return True
            
        for i in range(1, len(transactions)):
            current = transactions[i]
            previous = transactions[i-1]
            
            if current.get("残高") is None or previous.get("残高") is None:
                continue
                
            expected_balance = (
                previous["残高"] +
                current.get("入金額", 0) -
                current.get("出金額", 0)
            )
            
            if abs(current["残高"] - expected_balance) > 1:  # 1円の誤差を許容
                logger.warning(
                    f"残高不一致: 行{i+1} "
                    f"期待値={expected_balance}, 実際={current['残高']}"
                )
                return False
                
        return True
    
    async def extract_text_from_pdf(self, pdf_content: bytes) -> Dict[str, Any]:
        """
        PDFファイルからテキストを抽出（Geminiのファイルアップロード機能を使用）
        """
        import tempfile
        import os

        try:
            logger.info(f"Processing PDF, size: {len(pdf_content)} bytes")

            # Create temporary file for PDF
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(pdf_content)
                tmp_path = tmp_file.name

            try:
                # Upload PDF to Gemini
                logger.info(f"Uploading PDF to Gemini...")
                pdf_file = genai.upload_file(tmp_path, mime_type="application/pdf")
                logger.info(f"PDF uploaded: {pdf_file.name}")

                prompt = """このPDFファイルから以下の情報を抽出してJSON形式で返してください：
                1. 文書の種類（登記簿謄本、残高証明書、保険証券、通帳など）
                2. 主要な情報（金額、日付、名前、住所、取引記録など）
                3. その他重要と思われる情報

                特に数値データは正確に抽出してください。

                出力形式:
                {
                    "document_type": "文書種類",
                    "extracted_text": "抽出したテキスト全体",
                    "key_information": {
                        // 文書に応じた重要情報
                    }
                }"""

                # Generate content with uploaded file
                response = self.model.generate_content([prompt, pdf_file])

                # Delete uploaded file from Gemini
                genai.delete_file(pdf_file.name)
                logger.info("PDF deleted from Gemini")

            finally:
                # Clean up temporary file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

            # Try to parse JSON response
            try:
                import json
                result = json.loads(response.text)
                result["success"] = True
            except:
                # If not JSON, return as text
                result = {
                    "document_type": "PDF",
                    "extracted_text": response.text,
                    "success": True
                }

            logger.info("PDF processing completed successfully")
            return result

        except Exception as e:
            logger.error(f"PDF処理エラー: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "extracted_text": ""
            }

    async def extract_text_from_image(self, image_content: bytes) -> Dict[str, Any]:
        """
        画像ファイルからテキストを抽出
        """
        import tempfile
        import os

        try:
            logger.info(f"Processing image, size: {len(image_content)} bytes")

            # Create temporary file for image
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.jpg', delete=False) as tmp_file:
                tmp_file.write(image_content)
                tmp_path = tmp_file.name

            try:
                # Upload image to Gemini
                logger.info(f"Uploading image to Gemini...")
                image_file = genai.upload_file(tmp_path, mime_type="image/jpeg")
                logger.info(f"Image uploaded: {image_file.name}")

                prompt = """この画像から全てのテキストを抽出してJSON形式で返してください。
                特に金額、日付、名前などの重要情報を正確に抽出してください。

                出力形式:
                {
                    "extracted_text": "抽出したテキスト",
                    "document_type": "推測される文書タイプ"
                }"""

                # Generate content with uploaded file
                response = self.model.generate_content([prompt, image_file])

                # Delete uploaded file from Gemini
                genai.delete_file(image_file.name)
                logger.info("Image deleted from Gemini")

            finally:
                # Clean up temporary file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

            # Try to parse JSON response
            try:
                import json
                result = json.loads(response.text)
                result["success"] = True
            except:
                # If not JSON, return as text
                result = {
                    "document_type": "IMAGE",
                    "extracted_text": response.text,
                    "success": True
                }

            logger.info("Image processing completed successfully")
            return result

        except Exception as e:
            logger.error(f"画像処理エラー: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "extracted_text": ""
            }

    async def process_general_document(self, image_base64: str, document_type: DocumentCategory) -> Dict[str, Any]:
        """
        一般的な書類のOCR処理
        """
        prompts = {
            DocumentCategory.DEPOSIT: self._get_deposit_prompt(),
            DocumentCategory.LISTED_STOCK: self._get_stock_prompt(),
            DocumentCategory.LIFE_INSURANCE: self._get_insurance_prompt(),
            DocumentCategory.LAND_BUILDING: self._get_land_building_prompt(),
            # 他の書類タイプのプロンプトも追加
        }
        
        prompt = prompts.get(document_type)
        if not prompt:
            raise ValueError(f"未対応の書類タイプ: {document_type}")
        
        try:
            image_data = base64.b64decode(image_base64)
            
            response = self.model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": image_data}
            ], generation_config={
                "temperature": 0.1,
                "response_mime_type": "application/json"
            })
            
            return json.loads(response.text)
            
        except Exception as e:
            logger.error(f"書類OCR処理エラー ({document_type}): {str(e)}")
            raise
    
    def _get_deposit_prompt(self) -> str:
        return """この残高証明書の画像から以下の情報を抽出してJSON形式で返してください：
- 金融機関名
- 支店名
- 預金種類（普通預金、定期預金等）
- 口座番号
- 残高
- 既経過利子（定期預金の場合）

出力形式:
{
  "financial_institution": "金融機関名",
  "branch": "支店名",
  "account_type": "預金種類",
  "account_number": "口座番号",
  "balance": 残高金額,
  "accrued_interest": 既経過利子
}"""
    
    def _get_stock_prompt(self) -> str:
        return """この証券会社の報告書・残高証明書から以下の情報を抽出してJSON形式で返してください：
- 銘柄名
- 証券会社名
- 支店名
- 評価額
- 株式数または口数

出力形式:
{
  "stock_name": "銘柄名",
  "securities_company": "証券会社名",
  "branch_name": "支店名",
  "valuation": 評価額,
  "quantity": 株式数または口数
}"""
    
    def _get_insurance_prompt(self) -> str:
        return """この保険証券・解約返戻金証明書から以下の情報を抽出してJSON形式で返してください：
- 保険会社名
- 証券番号
- 契約者
- 被保険者
- 保険金受取人
- 受取年月日
- 保険金額
- 解約返戻金額

出力形式:
{
  "insurance_company": "保険会社名",
  "policy_number": "証券番号",
  "policyholder": "契約者",
  "insured": "被保険者",
  "beneficiary": "保険金受取人",
  "receipt_date": "受取年月日",
  "insurance_amount": 保険金額,
  "surrender_value": 解約返戻金額
}"""
    
    def _get_land_building_prompt(self) -> str:
        return """この登記簿謄本・名寄帳・固定資産税通知書から以下の情報を抽出してJSON形式で返してください：
- 所在地（都道府県、市区町村、大字・丁目）
- 地番
- 家屋番号
- 登記地目（登記簿の場合）
- 課税地目（名寄帳等の場合）
- 持分
- 地積
- 敷地権割合（マンションの場合）
- 固定資産税評価額
- 所有者名または名義人名（可能な場合）

出力形式:
{
  "prefecture": "都道府県",
  "city": "市区町村",
  "address": "大字・丁目",
  "lot_number": "地番",
  "house_number": "家屋番号",
  "registered_land_category": "登記地目",
  "taxed_land_category": "課税地目",
  "ownership_ratio": "持分",
  "area": 地積,
  "site_right_ratio": "敷地権割合",
  "fixed_asset_tax_value": 固定資産税評価額,
  "owner_names": ["所有者名1", "所有者名2"]
}"""