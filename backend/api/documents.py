from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import csv
import io
import pandas as pd
from datetime import datetime
from fastapi.responses import StreamingResponse
from loguru import logger

from models.document import (
    DocumentCategory,
    ProcessedDocument,
    CSVExportRequest
)

router = APIRouter()

# In-memory storage for now (should be replaced with database)
documents_storage = {}

@router.get("/list")
async def list_documents(
    category: Optional[DocumentCategory] = Query(None, description="書類カテゴリでフィルタ")
) -> List[ProcessedDocument]:
    """処理済み書類の一覧を取得"""
    docs = list(documents_storage.values())
    
    if category:
        docs = [doc for doc in docs if doc.category == category]
    
    return docs

@router.get("/{document_id}")
async def get_document(document_id: str) -> ProcessedDocument:
    """特定の書類を取得"""
    if document_id not in documents_storage:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return documents_storage[document_id]

@router.put("/{document_id}")
async def update_document(
    document_id: str,
    updates: dict
) -> ProcessedDocument:
    """書類情報を更新（手動編集用）"""
    if document_id not in documents_storage:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc = documents_storage[document_id]
    
    # Update manual edits field
    doc.manual_edits.update(updates)
    
    # Apply updates to extracted data
    for key, value in updates.items():
        if key in doc.extracted_data:
            doc.extracted_data[key] = value
    
    return doc

@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """書類を削除"""
    if document_id not in documents_storage:
        raise HTTPException(status_code=404, detail="Document not found")
    
    del documents_storage[document_id]
    return {"success": True, "message": "Document deleted"}

@router.post("/export/csv")
async def export_csv(request: CSVExportRequest):
    """
    書類データをCSV形式でエクスポート
    財産目録Excelに取り込める形式
    """
    try:
        # Filter documents
        docs = []
        for doc_id in request.document_ids:
            if doc_id in documents_storage:
                doc = documents_storage[doc_id]
                if not request.include_categories or doc.category in request.include_categories:
                    docs.append(doc)
        
        if not docs:
            raise HTTPException(status_code=404, detail="No documents found")
        
        # Create CSV data based on document type
        csv_data = []
        
        for doc in docs:
            if doc.category == DocumentCategory.PASSBOOK:
                # 通帳データの出力
                for transaction in doc.extracted_data:
                    csv_data.append({
                        "区分": "通帳",
                        "取引日": transaction.get("取引日", ""),
                        "出金額": transaction.get("出金額", 0),
                        "入金額": transaction.get("入金額", 0),
                        "残高": transaction.get("残高", 0),
                        "取引内容": transaction.get("取引内容", ""),
                        "元ファイル": doc.original_filename
                    })
            
            elif doc.category == DocumentCategory.DEPOSIT:
                # 預金データの出力
                csv_data.append({
                    "区分": "預貯金",
                    "金融機関": doc.extracted_data.get("financial_institution", ""),
                    "支店": doc.extracted_data.get("branch", ""),
                    "種類": doc.extracted_data.get("account_type", ""),
                    "口座番号": doc.extracted_data.get("account_number", ""),
                    "残高": doc.extracted_data.get("balance", 0),
                    "既経過利子": doc.extracted_data.get("accrued_interest", 0),
                    "元ファイル": doc.original_filename
                })
            
            elif doc.category == DocumentCategory.LISTED_STOCK:
                # 株式データの出力
                csv_data.append({
                    "区分": "上場株式",
                    "銘柄名": doc.extracted_data.get("stock_name", ""),
                    "証券会社": doc.extracted_data.get("securities_company", ""),
                    "支店名": doc.extracted_data.get("branch_name", ""),
                    "評価額": doc.extracted_data.get("valuation", 0),
                    "株式数": doc.extracted_data.get("quantity", 0),
                    "元ファイル": doc.original_filename
                })
            
            elif doc.category == DocumentCategory.LAND_BUILDING:
                # 土地・建物データの出力
                csv_data.append({
                    "区分": "土地・建物",
                    "都道府県": doc.extracted_data.get("prefecture", ""),
                    "市区町村": doc.extracted_data.get("city", ""),
                    "大字・丁目": doc.extracted_data.get("address", ""),
                    "地番": doc.extracted_data.get("lot_number", ""),
                    "家屋番号": doc.extracted_data.get("house_number", ""),
                    "登記地目": doc.extracted_data.get("registered_land_category", ""),
                    "課税地目": doc.extracted_data.get("taxed_land_category", ""),
                    "持分": doc.extracted_data.get("ownership_ratio", ""),
                    "地積": doc.extracted_data.get("area", 0),
                    "敷地権割合": doc.extracted_data.get("site_right_ratio", ""),
                    "固定資産税評価額": doc.extracted_data.get("fixed_asset_tax_value", 0),
                    "元ファイル": doc.original_filename
                })
            
            else:
                # その他の書類
                csv_data.append({
                    "区分": doc.category.value,
                    "データ": str(doc.extracted_data),
                    "元ファイル": doc.original_filename
                })
        
        # Create CSV
        if not csv_data:
            raise HTTPException(status_code=404, detail="No data to export")
        
        # Convert to DataFrame for easier CSV creation
        df = pd.DataFrame(csv_data)
        
        # Create CSV in memory
        stream = io.StringIO()
        df.to_csv(stream, index=False, encoding='utf-8-sig')  # UTF-8 with BOM for Excel
        
        # Return as streaming response
        output = io.BytesIO()
        output.write(stream.getvalue().encode('utf-8-sig'))
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=inheritance_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
        
    except Exception as e:
        logger.error(f"CSVエクスポートエラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/store")
async def store_document(document: ProcessedDocument):
    """処理済み書類を保存（一時的）"""
    documents_storage[document.id] = document
    return {"success": True, "document_id": document.id}