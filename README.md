# 🏛️ 相続税申告書類処理システム

相続税申告に関する書類をAI OCRで自動読み取りし、財産区分別に分類・リネーム、財産目録Excelに取り込めるCSVで出力するシステムです。

## ✨ 特徴

- 🤖 **Gemini 2.0 Flash** による高精度OCR
- 📁 **13種類の書類自動分類**
- 📊 **CSV/Excelエクスポート**機能
- ✏️ **Web UIでのOCR結果編集**
- 🚀 **サーバーレスアーキテクチャ**

## 📦 対応書類

| 区分 | 書類種別 | 状態 |
|------|----------|------|
| 土地・建物 | 登記簿謄本、名寄帳、固定資産税通知書 | ✅ 実装済み |
| 上場株式 | 証券会社の報告書・残高証明書 | ✅ 実装済み |
| 預貯金 | 銀行・郵便局の残高証明書 | ✅ 実装済み |
| 通帳 | 通帳コピー、取引履歴 | ✅ 実装済み |
| 生命保険 | 保険証券、解約返戻金証明書 | ✅ 実装済み |
| 債務 | 借入金残高証明書、未払金 | ✅ 実装済み |
| 葬式費用 | 領収書、お布施メモ | ✅ 実装済み |
| その他 | 車検証、骨董品鑑定書等 | ✅ 実装済み |

## 🚀 クイックスタート

### 1. 環境設定

```bash
# リポジトリのクローン
git clone https://github.com/yourusername/InhTaxAutoPJ.git
cd InhTaxAutoPJ

# 環境変数の設定 (.envファイルを編集)
cp .env.example .env
# GEMINI_API_KEYを設定
```

### 2. バックエンドの起動

```bash
# Python依存パッケージのインストール
pip install -r requirements.txt

# サーバー起動
sh run_backend.sh
# または
cd backend && python main.py
```

サーバーはhttp://localhost:8000で起動します。

APIドキュメント: http://localhost:8000/docs

### 3. フロントエンドの起動

```bash
# 簡易版 (HTML直接開く)
open frontend/index.html

# またはローカルサーバーで
cd frontend
python -m http.server 3000
# http://localhost:3000でアクセス
```

## 📁 プロジェクト構造

```
InhTaxAutoPJ/
├── backend/                  # FastAPIバックエンド
│   ├── api/                  # APIエンドポイント
│   ├── core/                 # コア設定
│   ├── models/               # データモデル
│   ├── services/             # ビジネスロジック
│   └── main.py               # エントリーポイント
├── frontend/                 # Web UI
│   ├── index.html            # メインHTML
│   └── app.js                # JavaScript
├── Docs/                     # 設計書・仕様書
├── test/                     # テストデータ
├── uploads/                  # アップロードファイル
├── outputs/                  # 出力ファイル
├── requirements.txt          # Python依存パッケージ
└── .env                      # 環境変数
```

## 🔧 技術スタック

### バックエンド
- **Python 3.8+**
- **FastAPI** - Webフレームワーク
- **Gemini 2.0 Flash** - OCRエンジン
- **pandas** - データ処理
- **openpyxl** - Excel処理

### フロントエンド
- **HTML/JavaScript** - シンプルUI
- **Tailwind CSS** - スタイリング
- **Fetch API** - API通信

### インフラ
- **Cloudflare Pages** - フロントエンドホスティング
- **Railway** - バックエンドホスティング

## 📝 API使用例

### 通帳OCR処理

```bash
curl -X POST "http://localhost:8000/api/ocr/process-passbook" \
  -F "file=@passbook.jpg" \
  -F "include_handwriting=false"
```

### 書類一括処理

```bash
curl -X POST "http://localhost:8000/api/ocr/process-batch" \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.jpg" \
  -F "auto_classify=true"
```

### CSVエクスポート

```bash
curl -X POST "http://localhost:8000/api/documents/export/csv" \
  -H "Content-Type: application/json" \
  -d '{"document_ids": ["doc1", "doc2"]}' \
  --output inheritance_data.csv
```

## 🌟 今後の実装予定

- [ ] React/Next.jsへの移行
- [ ] データベース連携 (PostgreSQL)
- [ ] ユーザー認証機能
- [ ] PDFバインダー生成
- [ ] Azure Document Intelligence統合
- [ ] 相続税2割加算自動判定

## 🔒 環境変数

`.env`ファイルに以下を設定:

```env
# 必須
GEMINI_API_KEY=your_gemini_api_key

# オプション (将来の拡張用)
AZURE_FORM_RECOGNIZER_ENDPOINT=your_azure_endpoint
AZURE_FORM_RECOGNIZER_KEY=your_azure_key
```

## 🛠️ テスト

```bash
# バックエンドテスト
python backend/test_backend.py

# APIテストは/docsでインタラクティブに実施可能
```

## 👥 コントリビューション

IssueやPull Requestは大歓迎です！

## 📜 ライセンス

MIT License

## 📧 お問い合わせ

問題がある場合はGitHub Issuesで報告してください。

---

🎆 **開発者**: ClaudeCode + Codexによる自律的実装