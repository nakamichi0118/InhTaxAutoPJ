# Cloudflare Pages デプロイ設定修正ガイド

## エラーの原因
Cloudflare Pagesが「frontend/frontend」ディレクトリを探していますが、実際のディレクトリ構造は「frontend」だけです。

## 修正手順

### Cloudflare Pages ダッシュボードで設定を修正

1. [Cloudflare Dashboard](https://dash.cloudflare.com/) にログイン
2. **Workers & Pages** を選択
3. **inhtaxautopj** プロジェクトをクリック
4. **Settings** → **Builds & deployments** を選択
5. **Build configurations** セクションの **Edit** をクリック

### 正しい設定値に更新

以下の設定に変更してください：

| 設定項目 | 現在の値（誤り） | 正しい値 |
|---------|----------------|----------|
| **Root directory (Advanced)** | `/frontend` | `/` (空欄またはスラッシュのみ) |
| **Build command** | （空欄） | （空欄のまま） |
| **Build output directory** | `frontend` | `frontend` |

### 詳細説明

- **Root directory**: プロジェクトのルートディレクトリを指定（GitHubリポジトリのルート）
- **Build output directory**: ビルド出力先（静的ファイルがある場所）= `frontend`

## 設定変更後の手順

1. **Save** をクリックして設定を保存
2. **Deployments** タブに移動
3. **Retry deployment** をクリックして再デプロイ

## 代替案（もし上記が動作しない場合）

### オプション A: ルートディレクトリを変更せず、出力ディレクトリのみ修正
- **Root directory**: `/frontend` のまま
- **Build output directory**: `.` (ドット = カレントディレクトリ)

### オプション B: wrangler.toml を追加
プロジェクトのルートに `wrangler.toml` を作成：

```toml
name = "inhtaxautopj"
compatibility_date = "2024-01-01"

[site]
bucket = "./frontend"
```

その後GitHubにプッシュ：
```bash
git add wrangler.toml
git commit -m "Add wrangler.toml for Cloudflare Pages"
git push origin main
```

## 検証方法

デプロイ成功後：
1. Cloudflare Pagesの提供URLにアクセス
2. `https://inhtaxautopj.pages.dev` でページが表示されることを確認
3. コンソールでエラーがないことを確認

## トラブルシューティング

### ビルドログの確認
1. **Deployments** タブで失敗したデプロイをクリック
2. **View build log** で詳細なエラーメッセージを確認

### よくある問題
- **404エラー**: index.htmlが正しい場所にない
- **空白ページ**: JavaScriptファイルのパスが間違っている
- **CORS エラー**: backend URLの設定ミス（config.js確認）

## 推奨設定（最終的にこれで動作するはず）

```
Root directory: /
Build command: （空欄）
Build output directory: frontend
```

これで Cloudflare Pages が正しく frontend ディレクトリ内の静的ファイルを見つけてデプロイできます。