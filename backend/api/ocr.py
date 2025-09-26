from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
import base64
from loguru import logger
from datetime import datetime

from services.gemini_ocr import GeminiOCRService
from models.document import DocumentCategory, ProcessedDocument, DocumentProcessResponse
from services.document_classifier import DocumentClassifier

router = APIRouter()
ocr_service = GeminiOCRService()
classifier = DocumentClassifier()

@router.post("/process-passbook")
async def process_passbook(
    file: UploadFile = File(...),
    include_handwriting: bool = Form(False)
):
    """通帳のOCR処理"""
    try:
        # Read and encode file
        contents = await file.read()
        base64_encoded = base64.b64encode(contents).decode('utf-8')
        
        # Process with Gemini OCR
        transactions = await ocr_service.process_passbook(
            base64_encoded,
            include_handwriting
        )
        
        return {
            "success": True,
            "filename": file.filename,
            "transactions": transactions,
            "count": len(transactions)
        }
        
    except Exception as e:
        logger.error(f"通帳処理エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-document")
async def process_document(
    file: UploadFile = File(...),
    document_type: Optional[DocumentCategory] = Form(None),
    auto_classify: bool = Form(True)
):
    """一般書類のOCR処理"""
    try:
        # Read and encode file
        contents = await file.read()
        base64_encoded = base64.b64encode(contents).decode('utf-8')
        
        # Auto-classify if needed
        if auto_classify and not document_type:
            document_type = await classifier.classify_document(base64_encoded)
            logger.info(f"書類分類結果: {file.filename} -> {document_type}")
        
        if not document_type:
            document_type = DocumentCategory.UNKNOWN
        
        # Process based on document type
        if document_type == DocumentCategory.PASSBOOK:
            extracted_data = await ocr_service.process_passbook(base64_encoded)
        else:
            extracted_data = await ocr_service.process_general_document(
                base64_encoded,
                document_type
            )
        
        # Create processed document record
        processed_doc = ProcessedDocument(
            id=f"{document_type}_{file.filename}_{datetime.now().timestamp()}",
            original_filename=file.filename,
            category=document_type,
            extracted_data=extracted_data,
            ocr_confidence=0.95  # Geminiは通常高精度
        )
        
        return {
            "success": True,
            "document": processed_doc.dict()
        }
        
    except Exception as e:
        logger.error(f"書類処理エラー: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-batch")
async def process_batch(
    files: List[UploadFile] = File(...),
    auto_classify: bool = Form(True)
):
    """複数書類の一括処理"""
    results = DocumentProcessResponse(
        success=True,
        processed_count=0,
        failed_count=0,
        documents=[],
        errors=[]
    )
    
    for file in files:
        try:
            logger.info(f"Processing file: {file.filename}, type: {file.content_type}")
            
            # Read file content
            contents = await file.read()
            logger.info(f"File size: {len(contents)} bytes")
            
            # Check file type and process accordingly
            filename_lower = file.filename.lower()
            
            if filename_lower.endswith('.pdf'):
                # Process PDF with new method
                logger.info(f"Processing as PDF: {file.filename}")
                ocr_result = await ocr_service.extract_text_from_pdf(contents)
                
            elif filename_lower.endswith(('.jpg', '.jpeg', '.png', '.heic', '.heif')):
                # Process image with new method
                logger.info(f"Processing as image: {file.filename}")
                ocr_result = await ocr_service.extract_text_from_image(contents)
                
            else:
                logger.warning(f"Unsupported file type: {file.filename}")
                raise ValueError(f"Unsupported file type: {file.filename}")
            
            # Check if extraction was successful
            if not ocr_result.get("success", False):
                raise Exception(f"OCR failed: {ocr_result.get('error', 'Unknown error')}")
            
            # Extract document type from result
            extracted_text = ocr_result.get("extracted_text", "")
            document_type = DocumentCategory.UNKNOWN
            
            # Auto-classify if needed
            if auto_classify and extracted_text:
                # Create base64 for classification (if needed)
                base64_encoded = base64.b64encode(contents).decode('utf-8')
                document_type = await classifier.classify_document(base64_encoded)
                logger.info(f"Document classified as: {document_type}")
            
            # Create processed document record
            processed_doc = ProcessedDocument(
                id=f"{document_type}_{file.filename}_{datetime.now().timestamp()}",
                original_filename=file.filename,
                category=document_type,
                extracted_data=ocr_result,
                ocr_confidence=0.95
            )
            
            results.documents.append(processed_doc)
            results.processed_count += 1
            logger.info(f"Successfully processed: {file.filename}")
            
        except Exception as e:
            logger.error(f"ファイル処理エラー ({file.filename}): {str(e)}")
            results.errors.append(f"{file.filename}: {str(e)}")
            results.failed_count += 1
    
    logger.info(f"Batch processing complete: {results.processed_count} succeeded, {results.failed_count} failed")
    return results.dict()