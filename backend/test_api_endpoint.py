#!/usr/bin/env python3
"""API エンドポイントを直接テスト"""

import asyncio
import aiohttp
import base64
from pathlib import Path

async def test_api():
    # PDFファイルのパス
    pdf_path = "/mnt/c/Users/iwanaga/Development/InhTaxAutoPJ/test/通帳/三井住友銀行.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ File not found: {pdf_path}")
        return
    
    # APIエンドポイント
    url = "http://localhost:8000/api/ocr/process-batch"
    
    # ファイルを読み込み
    with open(pdf_path, 'rb') as f:
        pdf_content = f.read()
    
    print(f"📄 Testing PDF: {pdf_path}")
    print(f"📊 File size: {len(pdf_content):,} bytes")
    
    # FormDataを作成
    data = aiohttp.FormData()
    data.add_field('files',
                   pdf_content,
                   filename='三井住友銀行.pdf',
                   content_type='application/pdf')
    data.add_field('auto_classify', 'true')
    
    # APIリクエスト送信
    async with aiohttp.ClientSession() as session:
        try:
            print("📤 Sending to API...")
            async with session.post(url, data=data) as response:
                result = await response.json()
                
                print(f"📬 Response status: {response.status}")
                
                if response.status == 200:
                    print("✅ Success!")
                    print(f"Processed: {result.get('processed_count', 0)} files")
                    print(f"Failed: {result.get('failed_count', 0)} files")
                    
                    if result.get('documents'):
                        for doc in result['documents']:
                            print(f"\n📄 Document: {doc.get('original_filename')}")
                            print(f"   Category: {doc.get('category')}")
                            print(f"   Extracted data preview:")
                            extracted = doc.get('extracted_data', {})
                            if isinstance(extracted, dict):
                                text = extracted.get('extracted_text', '')
                                if text:
                                    print(f"   {text[:200]}...")
                else:
                    print(f"❌ Error: {result}")
                    
        except Exception as e:
            print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    # サーバーが起動していることを確認
    print("⚠️  Make sure the backend server is running:")
    print("    cd backend && uvicorn main:app --reload")
    print()
    
    asyncio.run(test_api())