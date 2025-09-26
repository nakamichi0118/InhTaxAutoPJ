# 🚀 デプロイメントガイド

## 🔧 事前準備

### 必要なアカウント

1. **GitHubアカウント**
2. **Railwayアカウント** - https://railway.app/
3. **Cloudflareアカウント** - https://dash.cloudflare.com/
4. **Google Cloudアカウント** - Gemini APIキー取得用

## 📁 GitHubリポジトリの作成

### 1. GitHubで新しいリポジトリを作成

```bash
# GitHubで"InhTaxAutoPJ"という名前のリポジトリを作成
# https://github.com/new
```

### 2. ローカルリポジトリをGitHubにプッシュ

```bash
# リモートリポジトリを追加
git remote add origin https://github.com/nakamichi0118/InhTaxAutoPJ.git

# プッシュ
git push -u origin main
```

## 🚂 Railwayデプロイ（バックエンド）

### 1. Railwayプロジェクトの作成

1. [Railway](https://railway.app/)にログイン
2. "New Project" をクリック
3. "Deploy from GitHub repo" を選択
4. GitHubアカウントを連携
5. "InhTaxAutoPJ" リポジトリを選択

### 2. 環境変数の設定

Railwayダッシュボードで以下の環境変数を設定：

```env
GEMINI_API_KEY=your_gemini_api_key_here
PORT=8000
PYTHON_VERSION=3.11
```

### 3. デプロイの確認

- Railwayは自動的に `railway.toml`を検出してデプロイを開始
- デプロイ完了後、提供されたURLでアクセス可能
- 例: `https://inhtaxautopj.up.railway.app`

## ☁️ Cloudflare Pagesデプロイ（フロントエンド）

### 1. Cloudflare Pagesプロジェクトの作成

1. [Cloudflare Dashboard](https://dash.cloudflare.com/)にログイン
2. "Workers & Pages" を選択
3. "Create application" をクリック
4. "Pages" タブを選択
5. "Connect to Git" を選択

### 2. GitHubリポジトリの接続

1. GitHubアカウントを認証
2. "InhTaxAutoPJ" リポジトリを選択
3. 以下の設定を入力：
   - **プロジェクト名**: `inhtaxautopj`
   - **ビルドコマンド**: （空欄）
   - **ビルド出力ディレクトリ**: `frontend`
   - **ルートディレクトリ**: `/frontend`

### 3. バックエンドURLの更新

デプロイ後、`frontend/config.js`を更新：

```javascript
const config = {
    API_BASE_URL: window.location.hostname === 'localhost' 
        ? 'http://localhost:8000/api'
        : 'https://YOUR-RAILWAY-APP.up.railway.app/api'  // RailwayのURLに更新
};
```

## 🌐 カスタムドメインの設定（オプション）

### Railwayのカスタムドメイン

1. Railwayダッシュボードで"Settings" > "Domains"
2. "Add Domain" をクリック
3. ドメイン名を入力（例: `api.yourdomain.com`）
4. DNS設定を更新

### Cloudflare Pagesのカスタムドメイン

1. Pagesダッシュボードで"Custom domains"
2. "Set up a custom domain" をクリック
3. ドメイン名を入力（例: `app.yourdomain.com`）

## 🔄 自動デプロイの設定

### GitHub Actionsを使用した自動デプロイ

GitHubリポジトリの"Settings" > "Secrets and variables" > "Actions"で以下を設定：

- `CLOUDFLARE_API_TOKEN`: Cloudflare APIトークン
- `CLOUDFLARE_ACCOUNT_ID`: CloudflareアカウントID
- `RAILWAY_TOKEN`: Railway APIトークン（オプション）

## 📦 デプロイコマンド

### 手動デプロイ

```bash
# GitHubにプッシュ（自動デプロイがトリガーされる）
git push origin main
```

### Railway CLIを使ったデプロイ

```bash
# Railway CLIのインストール
curl -fsSL https://railway.app/install.sh | sh

# ログイン
railway login

# デプロイ
railway up
```

## 🎯 エンドポイント一覧

### プロダクションURL

- **フロントエンド**: https://inhtaxautopj.pages.dev
- **バックエンドAPI**: https://inhtaxautopj.up.railway.app
- **APIドキュメント**: https://inhtaxautopj.up.railway.app/docs

### ヘルスチェック

```bash
# バックエンドヘルスチェック
curl https://inhtaxautopj.up.railway.app/api/health

# フロントエンド確認
curl https://inhtaxautopj.pages.dev
```

## 🔍 トラブルシューティング

### Railwayの問題

1. **ビルド失敗**:

   - `requirements.txt`の依存関係を確認
   - Pythonバージョンを確認
2. **環境変数が認識されない**:

   - Railwayダッシュボードで環境変数を再設定

### Cloudflare Pagesの問題

1. **ビルド失敗**:

   - ビルド出力ディレクトリが `frontend`に設定されているか確認
2. **CORSエラー**:

   - RailwayバックエンドのCORS設定を確認
   - `backend/core/config.py`にCloudflare PagesのURLを追加

## 📊 モニタリング

### Railwayモニタリング

- Railwayダッシュボードで"Observability"タブ
- ログ、メトリクスを確認

### Cloudflare Analytics

- Cloudflare Pagesダッシュボードで"Analytics"タブ
- トラフィック、パフォーマンスを確認

## 🛡️ セキュリティ

### 環境変数の管理

- **絶対に** `.env`ファイルをGitHubにコミットしない
- Railway/Cloudflareの環境変数管理機能を使用
- APIキーは定期的にローテーション

### HTTPSの強制

- Cloudflare PagesはデフォルトでHTTPS
- RailwayもデフォルトでHTTPSを提供

---

✅ **デプロイ完了チェックリスト**

- [ ] GitHubリポジトリ作成
- [ ] Railwayプロジェクト作成
- [ ] Railway環境変数設定
- [ ] Cloudflare Pagesプロジェクト作成
- [ ] バックエンドデプロイ確認
- [ ] フロントエンドデプロイ確認
- [ ] API接続テスト
