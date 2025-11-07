from google.adk.agents import LlmAgent
import requests
import json
import os


def get_pull_request_diff(owner: str, repo: str, pr_number: int) -> str:
    """
    指定されたURLからPull Requestの差分情報を取得します。
    """

    url = f"https://patch-diff.githubusercontent.com/raw/{owner}/{repo}/pull/{pr_number}.diff"

    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTPエラーがあった場合に例外を発生させる
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error fetching pull request diff: {e}"
    

def post_review_comments(owner: str, repo: str, pr_number: int, body: str, comments: list[dict], event: str = "COMMENT") -> str:
    """
    指定されたPull Requestにレビューコメントを投稿します。
    """    

    # GitHub APIのURL
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
    
    # ヘッダー（トークンは環境変数から取得）
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"
    }
    
    # リクエストボディ
    data = {
        "body": body,
        "event": event
    }

    if comments:
        data["comments"] = comments
        
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return f"Successfully posted review to PR #{pr_number} in {owner}/{repo}"
    except requests.exceptions.RequestException as e:
        return f"Error posting review comments: {e}"

root_agent = LlmAgent(
    model="gemini-2.5-pro",
    name="get_review_comments_agent",
    instruction="""あなたは優秀なコードレビュアーです。
    以下の手順に沿ってレビューを進めてください。
    1. ユーザーにレビュー対象のGitHubプルリクエストのURLを尋ねてください。
    2. URLを受け取ったら、そのURLからオーナー名、リポジトリ名、PR番号を抽出して、`pr_info`として辞書形式で出力します。
    - 例：
        - 入力: https://github.com/owner1/repo1/pull/123
        - 出力: {{"owner":  "owner1", "repo": "repo1", "pr_num": "123"}}
    3.  `pr_info` 辞書から `owner`, `repo`, `pr_num` の値を取得し、`get_pull_request_diff` ツールを呼び出してPRの差分情報を取得します。
    4.  取得した差分情報を分析し、コードの品質、可読性、ベストプラクティスなどの観点でレビューコメントを生成します。
    5.  レビューコメントを`review_comments`という名前で以下の形式の辞書型リストとして出力します。
    出力形式：
    
    ```json
    [
        {{
            "path": "レビューコメントの対象ファイル名",
            "position": "diff内での行番号",
            "body": "レビュー内容"
        }}
    ]
    ```
    6. `pr_info` と `review_comments` を使って、`post_review_comments` ツールを呼び出し、GitHubにレビューコメントを投稿します。
    - `pr_info` から `owner`, `repo`, `pr_number` を取得します。
    - `body`引数には "生成AIのコードレビュー結果です" という文字列を渡します。
    - `review_comments` を `comments` 引数として渡します。
    """,
    tools=[get_pull_request_diff, post_review_comments],
)