import google.generativeai as genai
import base64
import json
from typing import Optional
from loguru import logger

from core.config import settings
from models.document import DocumentCategory

class DocumentClassifier:
    """書類分類エンジン"""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    async def classify_document(self, image_base64: str) -> DocumentCategory:
        """
        画像から書類タイプを判定
        """
        prompt = """この画像の書類タイプを判定してください。

以下の書類タイプの中から最も適切なものを選んでください：
1. LAND_BUILDING: 登記簿謄本、名寄帳、固定資産税通知書、評価証明書
2. LISTED_STOCK: 証券会社の報告書、株式・投資信託の残高証明書
3. OTHER_INVESTMENT: 出資証明書、非上場株式の証明書
4. PUBLIC_BOND: 国債・社債の証券、債券証明書
5. DEPOSIT: 銀行・郵便局の預金残高証明書
6. LIFE_INSURANCE: 生命保険証券、解約返戻金証明書
7. DEATH_RETIREMENT: 死亡退職金支払調書
8. OTHER_PROPERTY: 骨董品鑑定書、車検証、その他財産証明書
9. DEBT: 借入金残高証明書、未払金通知、病院の領収書
10. FUNERAL_EXPENSE: 葬儀費用領収書、お布施メモ
11. PASSBOOK: 通帳、取引履歴
12. PROCEDURE_DOC: 戸籍謄本・抄本、法定相続情報一覧図、印鑑証明書、住民票
13. UNKNOWN: 上記のどれにも該当しない書類

判定基準：
- 書類のタイトルやヘッダー情報を重視
- 表形式のデータがある場合、その内容を確認
- 金融機関名、保険会社名、不動産情報などの特定キーワードを確認

出力形式:
{
  "document_type": "書類タイプ名",
  "confidence": 0.0-1.0,
  "detected_keywords": ["検出キーワード1", "検出キーワード2"]
}"""
        
        try:
            image_data = base64.b64decode(image_base64)
            
            response = self.model.generate_content([
                prompt,
                {"mime_type": "image/jpeg", "data": image_data}
            ], generation_config={
                "temperature": 0.1,
                "response_mime_type": "application/json"
            })
            
            result = json.loads(response.text)
            document_type = result.get("document_type", "UNKNOWN")
            
            # Map to DocumentCategory enum
            category_map = {
                "LAND_BUILDING": DocumentCategory.LAND_BUILDING,
                "LISTED_STOCK": DocumentCategory.LISTED_STOCK,
                "OTHER_INVESTMENT": DocumentCategory.OTHER_INVESTMENT,
                "PUBLIC_BOND": DocumentCategory.PUBLIC_BOND,
                "DEPOSIT": DocumentCategory.DEPOSIT,
                "LIFE_INSURANCE": DocumentCategory.LIFE_INSURANCE,
                "DEATH_RETIREMENT": DocumentCategory.DEATH_RETIREMENT,
                "OTHER_PROPERTY": DocumentCategory.OTHER_PROPERTY,
                "DEBT": DocumentCategory.DEBT,
                "FUNERAL_EXPENSE": DocumentCategory.FUNERAL_EXPENSE,
                "PASSBOOK": DocumentCategory.PASSBOOK,
                "PROCEDURE_DOC": DocumentCategory.PROCEDURE_DOC,
                "UNKNOWN": DocumentCategory.UNKNOWN
            }
            
            return category_map.get(document_type, DocumentCategory.UNKNOWN)
            
        except Exception as e:
            logger.error(f"書類分類エラー: {str(e)}")
            return DocumentCategory.UNKNOWN
    
    def get_rename_format(self, category: DocumentCategory, content: str, date: Optional[str] = None) -> str:
        """
        書類タイプに応じたリネーム形式を生成
        
        形式: {区分コード}_{連番}_{内容}_{機関名}_{基準日}.pdf
        """
        import datetime
        
        # Get current timestamp for sequence
        seq = datetime.datetime.now().strftime("%Y%m%d%H%M%S")[:3]
        
        # Format date if provided
        if date:
            try:
                dt = datetime.datetime.strptime(date, "%Y-%m-%d")
                date_str = dt.strftime("R%y%m%d")
            except:
                date_str = "R05"
        else:
            date_str = "R05"
        
        # Generate filename based on category
        if category == DocumentCategory.LAND_BUILDING:
            return f"L{seq}_土地建物_{content}_{date_str}.pdf"
        elif category == DocumentCategory.LISTED_STOCK:
            return f"S{seq}_株式_{content}_{date_str}.pdf"
        elif category == DocumentCategory.DEPOSIT:
            return f"D{seq}_預金_{content}_{date_str}.pdf"
        elif category == DocumentCategory.PASSBOOK:
            return f"T{seq}_通帳_{content}_{date_str}.pdf"
        elif category == DocumentCategory.LIFE_INSURANCE:
            return f"I{seq}_保険_{content}_{date_str}.pdf"
        elif category == DocumentCategory.DEBT:
            return f"C{seq}_債務_{content}_{date_str}.pdf"
        elif category == DocumentCategory.FUNERAL_EXPENSE:
            return f"F{seq}_葬式費用_{content}_{date_str}.pdf"
        elif category == DocumentCategory.OTHER_PROPERTY:
            return f"O{seq}_その他財産_{content}_{date_str}.pdf"
        elif category == DocumentCategory.PROCEDURE_DOC:
            return f"P{seq}_手続き書類_{content}_{date_str}.pdf"
        else:
            return f"U{seq}_不明_{content}_{date_str}.pdf"