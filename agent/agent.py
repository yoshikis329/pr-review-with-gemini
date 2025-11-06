from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    model="gemini-2.5-pro",
    name="pr_review_agent",
    instructions="""
        あなたは優秀なPull Requestレビューアです。コードの品質、可読性、パフォーマンス、セキュリティ、ベストプラクティスに基づいてPRを評価し、建設的なフィードバックを提供します。
        以下の手順でレビューをします。
          1. PRのURLを受け取ります。
          2. 受け取ったURLからリポジトリ作成者、リポジトリ名、PR番号を抽出します。
            - 例：
                - 入力：
                    - URL: https://github.com/owner/repo/pull/123
                - 抽出結果：
                    - リポジトリ作成者: owner
                    - リポジトリ名: repo
                    - PR番号: 123

          3. get_pull_request_diffツールを呼び出し、PRの詳細情報を取得します。
          4. 取得したPRの差分情報を分析し、以下の観点でレビューを行います。
              - コードの品質
              - 可読性
              - パフォーマンス
              - セキュリティ
              - ベストプラクティス
        5. post_review_commentsツールを呼び出し、レビューコメントを投稿します。
    """,
    tools=["get_pull_request_diff", "post_review_comments"],
)

def get_pull_request_diff(owner: str, repo: str, pr_number: int) -> str:
    """
    指定されたURLからPull Requestの差分情報を取得します。
    """
    import requests

    url = f"https://patch-diff.githubusercontent.com/raw/{owner}/{repo}/pull/{pr_number}.diff"

    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTPエラーがあった場合に例外を発生させる
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error fetching pull request diff: {e}"
    

def post_review_comments(owner: str, repo: str, pr_number: int, body: str, event: str = "COMMENT", comments: list = None) -> str:
    """
    指定されたPull Requestにレビューコメントを投稿します。
    """
    import requests
    import json
    import os
    
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
    
    # コメントがある場合は追加
    if comments:
        data["comments"] = comments
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return f"Successfully posted review to PR #{pr_number} in {owner}/{repo}"
    except requests.exceptions.RequestException as e:
        return f"Error posting review comments: {e}"