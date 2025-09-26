import google.generativeai as genai
import base64
import json
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
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
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