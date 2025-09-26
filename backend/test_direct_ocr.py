#!/usr/bin/env python3
"""OCRサービスを直接テスト"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.gemini_ocr import GeminiOCRService
from core.config import settings

async def test_direct():
    """直接OCRサービスをテスト"""
    
    pdf_path = "/mnt/c/Users/iwanaga/Development/InhTaxAutoPJ/test/通帳/三井住友銀行.pdf"
    
    print(f"📄 Testing PDF: {pdf_path}")
    print("=" * 60)
    
    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return
    
    # GeminiOCRServiceをインスタンス化
    try:
        print("🔧 Initializing GeminiOCRService...")
        ocr_service = GeminiOCRService()
        print("✅ Service initialized")
        
        # PDFファイルを読み込み
        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()
        
        print(f"📊 PDF Size: {len(pdf_content):,} bytes")
        
        # OCR処理を実行
        print("🤖 Calling extract_text_from_pdf...")
        result = await ocr_service.extract_text_from_pdf(pdf_content)
        
        # 結果を表示
        if result.get("success"):
            print("\n✅ OCR Success!")
            print("-" * 40)
            
            # extracted_text を表示
            extracted_text = result.get("extracted_text", "")
            if extracted_text:
                print("Extracted text (first 500 chars):")
                print(extracted_text[:500])
                if len(extracted_text) > 500:
                    print(f"\n... (total {len(extracted_text)} characters)")
            
            # document_type を表示
            doc_type = result.get("document_type", "Unknown")
            print(f"\nDocument type: {doc_type}")
            
            # key_information を表示
            key_info = result.get("key_information", {})
            if key_info:
                print("\nKey information:")
                for key, value in key_info.items():
                    print(f"  {key}: {value}")
        else:
            print(f"❌ OCR Failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 環境変数を設定
    if not os.getenv("GEMINI_API_KEY"):
        # .envファイルから読み込み
        from dotenv import load_dotenv
        load_dotenv()
    
    # 非同期関数を実行
    asyncio.run(test_direct())