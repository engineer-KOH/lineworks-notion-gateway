# 🚀 lineworks-notion-gateway

## 📌 概要（Overview）
   ・本システムは、LINE WORKS Botをセキュアな認証ゲートウェイとして機能させ、特定権限を持つユーザーからのメッセージ入力に対して プライベートなNotionポートフォリオURLを安全に案内するWebアプリケーションです。  
   ・ユーザーIDによるアクセス制限と、LINE WORKS Server API v2.0に基づくJWT（RS256）認証を組み合わせることで、許可された関係者のみにポートフォリオへのアクセス権限を付与します。

## 🎯 主な目的（Objective）
- **セキュアなアクセス制御**: LINE WORKSのユーザーID判定により、認証された特定の関係者のみに限定コンテンツ（Notion）を開放

- **OAuth 2.0 / JWT 認証の実装**: LINE WORKS Server API v2.0に準拠したRS256（非対称暗号鍵）署名によるアクセストークン自動発行の実現

- **インタラクティブな応答機能**: Webhookイベントの受信から非同期でのメッセージ返送までを自動パイプライン化

## 🛠️ 使用技術（Tech Stack）
- **言語・フレームワーク**: Python 3.14, FastAPI, Uvicorn
- **インフラ・常時稼働**: AWS EC2 (Amazon Linux 2023), `systemd` (プロセス管理)
- **認証・セキュリティ**: PyJWT, cryptography (RS256暗号化署名)
- **API・通信**: LINE WORKS Bot API v2.0 (Server API), Webhook (HTTP POST), requests
- **ネットワーク・トンネリング**: ngrok (外部公開トンネル)
- **連携ターゲット**: Notion (ポートフォリオ)

## ⚙️ システム構成・処理フロー（Workflow）
1. **Webhook受信**: ユーザーがLINE WORKSのBot（1:1トーク）へメッセージを送信すると、ngrok経由でAWS EC2上のFastAPIの `/webhook` エンドポイントへイベントデータが到達

2. **ユーザー検証**: リクエストに含まれる `userId` を検証し、許可リスト（`ALLOWED_USER_IDS`）に登録されているか判定

3. **JWT生成 & トークン取得**: ローカルの秘密鍵（`.key`）を用いて `RS256` 形式で署名したJWTを生成し、LINE WORKS認証サーバーよりアクセストークンを取得

4. **応答メッセージ送信**: 認証成功時にはNotionポートフォリオURL、失敗時には権限エラーメッセージをLINE WORKS API経由でユーザーへ自動返信

## 🚀 使い方（Quick Start）

### 💻 1. セットアップ手順
1. **リポジトリの配置**:
   `/home/ec2-user/lineworks-notion/` にプロジェクトを配置します。
2. **依存ライブラリのインストール**:
   ```bash
   pip install fastapi uvicorn requests pyjwt cryptography python-dotenv
   ```
3. **環境変数（`.env`）の設定**:
   ルートフォルダに `.env` ファイルを作成し、各種認証情報を設定します。
   ```env
   LINEWORKS_CLIENT_ID=your_client_id
   LINEWORKS_CLIENT_SECRET=your_client_secret
   LINEWORKS_BOT_ID=your_bot_id
   ```
4. **秘密鍵（Private Key）の配置**:<br>
   LINE WORKS Developer Consoleからダウンロードした秘密鍵ファイルをルートフォルダに配置します。

### 👤 2. バックグラウンド常時稼働管理 (systemd & ngrok)

1. **FastAPI サービスの操作**:
# ステータス確認
   ```bash
sudo systemctl status lineworks-notion

# 再起動
sudo systemctl restart lineworks-notion

# ngrok トンネリングの常時稼働（screen等を利用）
   ```bash
screen -S ngrok -d -m ./ngrok http 8000
   ```
### 👤 2. 3. LINE WORKSでの実行
LINE WORKSで「ポートフォリオ閲覧ゲート」Botにメッセージを送信すると、認証結果に応じてポートフォリオURLが返信されます。

```text
lineworks-notion-gateway/
├── main.py                     # Webhook受信、ユーザー判定、JWT生成、メッセージ送信のメイン処理
├── .env                        # LINE WORKS API等の資格情報（※.gitignore対象）
├── .gitignore                  # 機密情報・秘密鍵・キャッシュファイルの除外設定
├── private_**************.key  # LINE WORKS Server API認証用のRS256秘密鍵（※.gitignore対象）
└── README.md                   # プロジェクト仕様書・ドキュメント
```