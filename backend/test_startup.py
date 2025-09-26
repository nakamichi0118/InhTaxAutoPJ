#!/usr/bin/env python3
"""Test script to check if the backend can start properly"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing imports...")
    from main import app
    print("✅ Successfully imported FastAPI app")

    from core.config import settings
    print("✅ Successfully imported settings")

    from api import health, documents, ocr
    print("✅ Successfully imported API modules")

    from services.gemini_ocr import GeminiOCRService
    print("✅ Successfully imported Gemini OCR service")

    print("\n🎉 All imports successful! Backend should start properly.")

except Exception as e:
    print(f"❌ Error during import: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)