# 相続税申告書類処理システム (InhTaxAutoPJ)

相続税関連書類を自動的にAI OCRで読み取り、財産種類別に分類し、Excelの財産目録にインポート可能なCSVを出力するシステムです。

## 主な機能

- **AI OCR処理**: Gemini 2.5 Flash APIを使用した高精度な文書読み取り
- **自動分類**: 13種類の財産カテゴリへの自動振り分け
- **バッチ処理**: 複数書類の一括アップロード・処理
- **CSV出力**: Excel財産目録へのインポート対応
- **Web UI**: ドラッグ&ドロップ対応の使いやすいインターフェース

## 技術スタック

### バックエンド
- Python 3.11
- FastAPI
- Gemini 2.5 Flash API
- pandas / openpyxl

### フロントエンド
- HTML5 / JavaScript
- Tailwind CSS

### デプロイメント
- Railway (バックエンド)
- Cloudflare Pages (フロントエンド)
- GitHub Actions (CI/CD)

## ローカル開発環境のセットアップ

### 1. 環境変数の設定

`.env`ファイルを作成：

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. バックエンドの起動

```bash
# 依存関係のインストール
pip install -r requirements.txt

# サーバー起動
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. フロントエンドの起動

```bash
cd frontend
# Python組み込みサーバーを使用
python -m http.server 3000
```

ブラウザで `http://localhost:3000` にアクセス

## 対応書類カテゴリ

| コード | カテゴリ | 説明 |
|--------|----------|------|
| L | 土地・建物 | 不動産関連書類 |
| S | 上場株式 | 株式・証券関連 |
| D | 預貯金等 | 銀行預金・定期預金 |
| T | 通帳 | 取引履歴の解析 |
| I | 生命保険 | 保険証券・解約返戻金 |
| C | 債務 | 借入金・未払金 |
| F | 葬式費用 | 葬儀関連費用 |
| O | その他財産 | 上記以外の財産 |
| P | 手続き書類 | 申告関連書類 |

## デプロイメント

詳細は[デプロイメントガイド](DEPLOYMENT.md)を参照してください。

### クイックデプロイ

1. **GitHub リポジトリの作成**
```bash
gh repo create InhTaxAutoPJ --public
git remote add origin https://github.com/YOUR_USERNAME/InhTaxAutoPJ.git
git push -u origin main
```

2. **Railway デプロイ**
- [Railway](https://railway.app/)でプロジェクト作成
- GitHubリポジトリを接続
- 環境変数を設定

3. **Cloudflare Pages デプロイ**
- [Cloudflare Pages](https://pages.cloudflare.com/)でプロジェクト作成
- GitHubリポジトリを接続
- ビルド設定: ルートディレクトリ`/frontend`

## API エンドポイント

- `POST /api/ocr/process-passbook` - 通帳処理
- `POST /api/ocr/process-document` - 単一書類処理
- `POST /api/ocr/process-batch` - バッチ処理
- `POST /api/documents/export/csv` - CSV出力
- `GET /api/health` - ヘルスチェック

## プロジェクト構造

```
InhTaxAutoPJ/
├── backend/
│   ├── api/          # APIエンドポイント
│   ├── services/     # ビジネスロジック
│   ├── models/       # データモデル
│   └── core/         # 設定・ユーティリティ
├── frontend/
│   ├── index.html    # メインページ
│   ├── app.js        # アプリケーションロジック
│   └── config.js     # 環境設定
├── Docs/             # ドキュメント
├── railway.toml      # Railway設定
└── requirements.txt  # Python依存関係
```

## ライセンス

MIT License

## 開発者

iwanaga

## サポート

問題や質問がある場合は、GitHubのIssuesで報告してください。