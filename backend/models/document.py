from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class DocumentCategory(str, Enum):
    """書類区分"""
    LAND_BUILDING = "L"  # 土地・建物
    LISTED_STOCK = "S"  # 上場株式・投資信託
    OTHER_INVESTMENT = "OI"  # その他出資金
    PUBLIC_BOND = "PB"  # 公社債
    DEPOSIT = "D"  # 預貯金
    LIFE_INSURANCE = "I"  # 生命保険
    DEATH_RETIREMENT = "DR"  # 死亡退職金
    OTHER_PROPERTY = "O"  # その他財産
    DEBT = "C"  # 債務
    FUNERAL_EXPENSE = "F"  # 葬式費用
    PASSBOOK = "T"  # 通帳
    PROCEDURE_DOC = "P"  # 手続き関係書類
    UNKNOWN = "U"  # 不明書類

class LandBuildingData(BaseModel):
    """土地・建物データ"""
    prefecture: Optional[str] = Field(None, description="都道府県")
    city: Optional[str] = Field(None, description="市区町村")
    address: Optional[str] = Field(None, description="大字・丁目")
    lot_number: Optional[str] = Field(None, description="地番")
    house_number: Optional[str] = Field(None, description="家屋番号")
    registered_land_category: Optional[str] = Field(None, description="登記地目")
    taxed_land_category: Optional[str] = Field(None, description="課税地目")
    ownership_ratio: Optional[str] = Field(None, description="持分")
    area: Optional[float] = Field(None, description="地積")
    site_right_ratio: Optional[str] = Field(None, description="敷地権割合")
    fixed_asset_tax_value: Optional[int] = Field(None, description="固定資産税評価額")

class StockData(BaseModel):
    """株式・投資信託データ"""
    stock_name: str = Field(..., description="銘柄名")
    securities_company: str = Field(..., description="証券会社")
    branch_name: Optional[str] = Field(None, description="支店名")
    valuation: int = Field(..., description="評価額")
    quantity: Optional[float] = Field(None, description="株式数or口数")

class DepositData(BaseModel):
    """預貯金データ"""
    financial_institution: str = Field(..., description="金融機関")
    branch: str = Field(..., description="支店")
    account_type: str = Field(..., description="種類（普通預金、定期預金等）")
    account_number: Optional[str] = Field(None, description="口座番号")
    balance: int = Field(..., description="残高")
    accrued_interest: Optional[int] = Field(None, description="既経過利子")

class PassbookTransaction(BaseModel):
    """通帳取引データ"""
    transaction_date: datetime = Field(..., description="取引日")
    withdrawal: Optional[int] = Field(None, description="出金額")
    deposit: Optional[int] = Field(None, description="入金額")
    balance: Optional[int] = Field(None, description="残高")
    description: str = Field(..., description="取引内容")

class ProcessedDocument(BaseModel):
    """処理済み書類データ"""
    id: str = Field(..., description="一意識別子")
    original_filename: str = Field(..., description="元ファイル名")
    category: DocumentCategory = Field(..., description="書類区分")
    renamed_filename: Optional[str] = Field(None, description="リネーム後ファイル名")
    extracted_data: Dict[str, Any] = Field(default_factory=dict, description="抽出データ")
    ocr_confidence: Optional[float] = Field(None, description="OCR信頼度")
    processed_at: datetime = Field(default_factory=datetime.now, description="処理日時")
    manual_edits: Dict[str, Any] = Field(default_factory=dict, description="手動修正内容")
    error_message: Optional[str] = Field(None, description="エラーメッセージ")

class DocumentUploadRequest(BaseModel):
    """書類アップロードリクエスト"""
    files: List[str] = Field(..., description="ファイルのBase64エンコード文字列リスト")
    include_handwriting: bool = Field(False, description="手書き文字を含めるか")
    auto_classify: bool = Field(True, description="自動分類を行うか")

class DocumentProcessResponse(BaseModel):
    """書類処理レスポンス"""
    success: bool = Field(..., description="処理成功フラグ")
    processed_count: int = Field(..., description="処理済み件数")
    failed_count: int = Field(0, description="失敗件数")
    documents: List[ProcessedDocument] = Field(default_factory=list, description="処理済み書類リスト")
    errors: List[str] = Field(default_factory=list, description="エラーメッセージリスト")

class CSVExportRequest(BaseModel):
    """CSV出力リクエスト"""
    document_ids: List[str] = Field(..., description="出力対象書類IDリスト")
    include_categories: List[DocumentCategory] = Field(default_factory=list, description="含める書類区分")
    output_format: str = Field("csv", description="出力形式（csv/excel）")