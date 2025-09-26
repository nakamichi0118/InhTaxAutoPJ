#!/usr/bin/env python3
"""実際のPDFファイルでGemini OCRをテスト"""

import os
import sys
import base64
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_gemini_pdf():
    """三井住友銀行のPDFでテスト"""
    pdf_path = "/mnt/c/Users/iwanaga/Development/InhTaxAutoPJ/test/通帳/三井住友銀行.pdf"

    print(f"📄 Testing PDF: {pdf_path}")
    print("=" * 60)

    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        return

    # Import Gemini
    try:
        import google.generativeai as genai
    except ImportError:
        print("❌ google-generativeai not installed")
        print("Run: pip install google-generativeai")
        return

    # Set API key (get from environment or .env file)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Try loading from .env
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")
        except:
            pass

    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        print("Set environment variable or create .env file")
        return

    print(f"✅ API Key found: {api_key[:10]}...")

    # Configure Gemini
    genai.configure(api_key=api_key)

    # Try different models
    models_to_try = [
        "gemini-2.0-flash-exp",  # Latest experimental
        "gemini-1.5-flash",      # Stable version
        "gemini-1.5-pro",        # Pro version
        "gemini-2.5-flash"       # If available
    ]

    for model_name in models_to_try:
        try:
            print(f"\n🤖 Trying model: {model_name}")
            model = genai.GenerativeModel(model_name)

            # Read PDF file
            with open(pdf_path, 'rb') as f:
                pdf_content = f.read()

            print(f"📊 PDF Size: {len(pdf_content):,} bytes")

            # Upload file to Gemini
            print("📤 Uploading to Gemini...")

            # Method 1: Direct upload
            try:
                pdf_file = genai.upload_file(pdf_path, mime_type="application/pdf")
                print(f"✅ File uploaded: {pdf_file.name}")

                # Generate content
                prompt = """
                このPDFファイルから以下の情報を抽出してください：
                1. すべてのテキスト内容
                2. 取引日、取引内容、金額、残高などの構造化データ
                3. 金融機関名、支店名、口座番号など

                できるだけ詳細に、表形式のデータは構造を保って出力してください。
                """

                response = model.generate_content([prompt, pdf_file])
                print("\n✅ Response received:")
                print("-" * 40)
                print(response.text[:1000])
                if len(response.text) > 1000:
                    print(f"\n... (total {len(response.text)} characters)")

                # Delete uploaded file
                genai.delete_file(pdf_file.name)
                return True

            except Exception as e1:
                print(f"⚠️ Upload method failed: {e1}")

                # Method 2: Base64 encoding
                print("\n📝 Trying base64 method...")
                pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')

                prompt = """
                このPDFから全てのテキストを抽出してください。
                特に以下の情報を含めてください：
                - 金融機関名
                - 取引記録（日付、内容、金額、残高）
                - その他の重要情報
                """

                try:
                    # Try with inline data
                    response = model.generate_content([
                        prompt,
                        {
                            "mime_type": "application/pdf",
                            "data": pdf_base64
                        }
                    ])

                    print("\n✅ Response received (base64 method):")
                    print("-" * 40)
                    print(response.text[:1000])
                    return True

                except Exception as e2:
                    print(f"⚠️ Base64 method failed: {e2}")

        except Exception as e:
            print(f"❌ Model {model_name} failed: {e}")
            continue

    print("\n❌ All methods failed")
    return False

if __name__ == "__main__":
    test_gemini_pdf()