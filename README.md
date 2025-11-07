# PR Review with Gemini

GeminiのLLMエージェントを使用してGitHubのPull Requestを自動レビューするツールです。

## 機能

- GitHub Pull Requestの差分情報を自動取得
- Gemini 2.5 Proを使用したコード品質、可読性、ベストプラクティスの分析
- GitHub APIを通じた自動レビューコメント投稿

## セットアップ

### 1. 依存関係のインストール

```bash
python3 -m venv .venv
pip3 install -r requirements.txt
# GCPで実行する場合は以下、ローカルで実行できる場合は、おそらくbinのところがScriptになります。
source .venv/bin/activate
```

### 2. 環境変数の設定

`.env`ファイルを作成し、以下の環境変数を設定してください：

```bash
GITHUB_TOKEN=your_github_personal_access_token
GOOGLE_API_TOKEN=googleのAPIトークン
```

GitHub Personal Access Tokenの取得方法：
1. GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
2. "Generate new token"をクリック
3. 以下の権限を付与：
   - `repo` (リポジトリへのフルアクセス)
   - `pull_requests:write` (Pull Requestへの書き込み権限)

## 使用方法

1. エージェントを起動します
2. 「こんにちは」のような汎用文言を入れると、Pull RequestのURLが聞かれるので、レビュー対象のPull RequestのURLを入力します
   - 例: `https://github.com/owner/repo/pull/123`
3. エージェントが自動的に以下を実行します：
   - PR差分の取得
   - コード分析
   - レビューコメントの生成
   - GitHubへのコメント投稿

## プロジェクト構造

```
pr-review-with-gemini/
├── pr_review_agent/
│   ├── agent.py          # メインエージェント
│   └── .env             # 環境変数設定
├── requirements.txt      # Python依存関係
└── README.md            # このファイル
```

## エージェントの仕組み

### 1. Pull Request情報の抽出
URLから以下の情報を抽出：
- オーナー名 (owner)
- リポジトリ名 (repo) 
- PR番号 (pr_number)

### 2. 差分取得
`get_pull_request_diff`関数を使用して、GitHubから差分情報を取得します。

### 3. レビュー分析
Gemini 2.5 Proが以下の観点でコードを分析：
- コード品質
- 可読性
- パフォーマンス
- セキュリティ
- ベストプラクティス

### 4. コメント投稿
`post_review_comments`関数を使用して、GitHub APIにレビューコメントを投稿します。

## ツール仕様

### get_pull_request_diff(owner, repo, pr_number)
Pull Requestの差分情報を取得します。

**パラメータ:**
- `owner` (str): リポジトリオーナー名
- `repo` (str): リポジトリ名
- `pr_number` (int): Pull Request番号

**戻り値:**
- `str`: 差分情報のテキスト

### post_review_comments(owner, repo, pr_number, body, comments, event)
GitHub Pull Requestにレビューコメントを投稿します。

**パラメータ:**
- `owner` (str): リポジトリオーナー名
- `repo` (str): リポジトリ名
- `pr_number` (int): Pull Request番号
- `body` (str): レビューの本文
- `comments` (list[dict]): 行ごとのコメントリスト
- `event` (str): レビューのタイプ (デフォルト: "COMMENT")

**戻り値:**
- `str`: 投稿結果のメッセージ

## レビューコメント形式

```json
[
  {
    "path": "src/main/App.java",
    "position": 5,
    "body": "ここ、タイポしています。"
  }
]
```

## 注意事項

- GitHub Personal Access Tokenは適切に管理してください
- レビュー対象のリポジトリに対する適切な権限が必要です
- API利用制限に注意してください

## ライセンス

MIT License
