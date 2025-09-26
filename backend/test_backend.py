#!/usr/bin/env python3
"""
Backend test script
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test if all modules can be imported"""
    print("🗺️ Testing imports...")
    
    try:
        from core.config import settings
        print("✅ Core config imported")
        
        from models.document import DocumentCategory, ProcessedDocument
        print("✅ Models imported")
        
        from services.gemini_ocr import GeminiOCRService
        print("✅ Gemini OCR service imported")
        
        from services.document_classifier import DocumentClassifier
        print("✅ Document classifier imported")
        
        from api import health, ocr, documents
        print("✅ API modules imported")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import error: {e}")
        return False

def test_config():
    """Test configuration"""
    print("\n🔧 Testing configuration...")
    
    from core.config import settings
    
    if not settings.GEMINI_API_KEY:
        print("⚠️  Warning: GEMINI_API_KEY not set")
    else:
        print(f"✅ GEMINI_API_KEY configured (length: {len(settings.GEMINI_API_KEY)})")
    
    if not settings.AZURE_FORM_RECOGNIZER_KEY:
        print("⚠️  Warning: AZURE_FORM_RECOGNIZER_KEY not set")
    else:
        print(f"✅ AZURE_FORM_RECOGNIZER_KEY configured")
    
    print(f"✅ Upload path: {settings.UPLOAD_PATH}")
    print(f"✅ Output path: {settings.OUTPUT_PATH}")
    print(f"✅ Max upload size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB")
    
    return True

def test_document_categories():
    """Test document category definitions"""
    print("\n📝 Testing document categories...")
    
    from models.document import DocumentCategory
    
    categories = [
        DocumentCategory.LAND_BUILDING,
        DocumentCategory.LISTED_STOCK,
        DocumentCategory.DEPOSIT,
        DocumentCategory.PASSBOOK,
        DocumentCategory.UNKNOWN
    ]
    
    for cat in categories:
        print(f"✅ Category: {cat.name} = {cat.value}")
    
    return True

def main():
    print("🚀 Starting backend tests...\n")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_document_categories
    ]
    
    all_passed = True
    for test in tests:
        if not test():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All tests passed! Backend is ready.")
        print("\n💡 Next steps:")
        print("1. Run the server: python backend/main.py")
        print("2. Access API docs: http://localhost:8000/docs")
        print("3. Test with sample documents in /test folder")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())