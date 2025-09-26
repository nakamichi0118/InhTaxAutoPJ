# 相続税申告書類処理システム - Backend

## 🚀 セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルに以下のキーを設定:

```env
GEMINI_API_KEY=your_gemini_api_key
AZURE_FORM_RECOGNIZER_ENDPOINT=your_azure_endpoint  # オプション
AZURE_FORM_RECOGNIZER_KEY=your_azure_key  # オプション
```

### 3. サーバー起動

```bash
# プロジェクトルートから
sh run_backend.sh

# または直接
cd backend
python main.py
```

## 📚 APIエンドポイント

サーバー起動後、以下のURLでAPIドキュメントを確認:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要エンドポイント

#### 🎯 OCR処理

- `POST /api/ocr/process-passbook` - 通帳のOCR処理
- `POST /api/ocr/process-document` - 一般書類のOCR処理
- `POST /api/ocr/process-batch` - 複数書類の一括処理

#### 📄 書類管理

- `GET /api/documents/list` - 処理済み書類一覧
- `GET /api/documents/{id}` - 特定書類の取得
- `PUT /api/documents/{id}` - 書類情報の更新
- `POST /api/documents/export/csv` - CSVエクスポート

## 📁 プロジェクト構造

```
backend/
├── main.py              # アプリケーションエントリーポイント
├── api/                 # APIエンドポイント
│   ├── health.py        # ヘルスチェック
│   ├── ocr.py           # OCR関連API
│   └── documents.py     # 書類管理API
├── core/                # コア設定
│   └── config.py        # アプリ設定
├── models/              # データモデル
│   └── document.py      # 書類モデル定義
├── services/            # ビジネスロジック
│   ├── gemini_ocr.py    # Gemini OCRサービス
│   └── document_classifier.py  # 書類分類エンジン
└── test_backend.py      # テストスクリプト
```

## 📝 書類区分

| コード | 区分 | 説明 |
|------|------|------|
| L | 土地・建物 | 登記簿謄本、名寄帳等 |
| S | 上場株式 | 証券会社の報告書 |
| D | 預貯金 | 残高証明書 |
| T | 通帳 | 通帳・取引履歴 |
| I | 生命保険 | 保険証券 |
| C | 債務 | 借入金残高証明書 |
| F | 葬式費用 | 領収書 |
| O | その他財産 | 骨董品等 |
| P | 手続き書類 | 戸籍謄本等 |
| U | 不明 | 分類不能 |

## 🤖 技術仕様

- **OCRエンジン**: Gemini 2.0 Flash
- **フレームワーク**: FastAPI
- **データ処理**: pandas, openpyxl
- **PDF処理**: PyPDF2

## 🔧 テスト

```bash
# バックエンドのテスト
python backend/test_backend.py

# APIテストはサーバー起動後に/docsで実施可能
```

## 🚶 今後の実装予定

- [ ] データベース連携（現在はメモリ保存）
- [ ] 認証・認可機能
- [ ] バッチ処理の非同期化
- [ ] Azure Document Intelligenceの統合