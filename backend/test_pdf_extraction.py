#!/usr/bin/env python3
"""Test PDF text extraction with Gemini API"""

import os
import sys
import base64
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_pdf_extraction(pdf_path: str):
    """Test PDF text extraction using Gemini"""
    print(f"\n📄 Testing PDF: {pdf_path}")
    print("=" * 60)

    try:
        # Import after path is set
        import google.generativeai as genai
        from core.config import settings

        # Configure Gemini
        if not settings.GEMINI_API_KEY:
            print("❌ GEMINI_API_KEY not set in environment")
            return False

        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')

        # Read PDF file
        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()

        print(f"📊 PDF Size: {len(pdf_content):,} bytes")

        # Convert to base64
        pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')

        # Create prompt for text extraction
        prompt = """
        このPDFファイルからテキストを抽出してください。
        表や項目がある場合は、構造を保持して読みやすい形式で出力してください。

        抽出したテキスト:
        """

        # Send to Gemini
        print("🤖 Sending to Gemini 2.5 Flash...")
        response = model.generate_content([
            prompt,
            {"mime_type": "application/pdf", "data": pdf_base64}
        ])

        # Get extracted text
        extracted_text = response.text

        print("\n✅ Extracted Text (first 500 chars):")
        print("-" * 40)
        print(extracted_text[:500])
        if len(extracted_text) > 500:
            print(f"\n... (total {len(extracted_text)} characters)")
        print("-" * 40)

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Test PDF extraction with sample files"""

    # Set environment variable if not set
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️ GEMINI_API_KEY not found in environment")
        print("Please set it or create a .env file with:")
        print("GEMINI_API_KEY=your_api_key_here")
        return

    test_dir = "/mnt/c/Users/iwanaga/Development/InhTaxAutoPJ/test"

    # Find PDF files
    pdf_files = []
    for root, dirs, files in os.walk(test_dir):
        for file in files:
            if file.endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))

    print(f"📁 Found {len(pdf_files)} PDF files in test directory")

    # Test first 3 PDFs
    for pdf_file in pdf_files[:3]:
        success = test_pdf_extraction(pdf_file)
        if not success:
            print(f"⚠️ Failed to extract from {pdf_file}")
            break

    print("\n✅ Test completed!")

if __name__ == "__main__":
    main()