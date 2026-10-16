"""密码访问门页面（upstream: apps/api/src/share-gate-page.ts 1:1）。"""

from .share_head import share_page_favicon_link
from .share_page import ShareFooterAuthor, build_share_author_html
from .share_sanitize import escape_html, share_page_csp_meta


# upstream: share-gate-page.ts:6-122
def build_share_gate_html(
    share_id: str,
    title: str,
    error: str | None = None,
    author: ShareFooterAuthor | None = None,
) -> str:
    safe_title = escape_html(title or "Markdown 分享")
    if error == "rate_limited":
        error_message = "尝试次数过多，请稍后再试。"
    elif error == "invalid":
        error_message = "密码错误，请重试。"
    else:
        error_message = ""

    author_block = (
        build_share_author_html(author)
        if author is not None
        else "由 doocs/md 分享"
    )
    error_block = (
        f'<div class="error">{escape_html(error_message)}</div>'
        if error_message
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="noindex, nofollow" />
  {share_page_csp_meta()}
  {share_page_favicon_link()}
  <title>{safe_title} - 需要密码</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background: #f5f5f5;
      color: #333;
    }}
    .gate-card {{
      width: 100%;
      max-width: 400px;
      background: #fff;
      border-radius: 12px;
      padding: 32px 28px;
      box-shadow: 0 8px 30px rgb(0 0 0 / 8%);
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 20px;
      font-weight: 600;
      line-height: 1.4;
    }}
    p {{
      margin: 0 0 24px;
      font-size: 14px;
      color: #666;
    }}
    label {{
      display: block;
      margin-bottom: 8px;
      font-size: 14px;
      font-weight: 500;
    }}
    input[type="password"] {{
      width: 100%;
      padding: 10px 12px;
      border: 1px solid #ddd;
      border-radius: 8px;
      font-size: 16px;
    }}
    input[type="password"]:focus {{
      outline: none;
      border-color: #07c160;
      box-shadow: 0 0 0 3px rgb(7 193 96 / 15%);
    }}
    button {{
      width: 100%;
      margin-top: 16px;
      padding: 10px 16px;
      border: none;
      border-radius: 8px;
      background: #07c160;
      color: #fff;
      font-size: 15px;
      font-weight: 600;
      cursor: pointer;
    }}
    button:hover {{ background: #06ad56; }}
    .error {{
      margin-bottom: 16px;
      padding: 10px 12px;
      border-radius: 8px;
      background: #fef2f2;
      color: #b91c1c;
      font-size: 13px;
    }}
    .footer {{
      margin-top: 24px;
      text-align: center;
      font-size: 12px;
      color: #999;
    }}
  </style>
</head>
<body>
  <div class="gate-card">
    <h1>{safe_title}</h1>
    <p>此分享链接已设置访问密码，请输入密码后查看。</p>
    {error_block}
    <form method="POST" action="/s/{escape_html(share_id)}/unlock">
      <label for="password">访问密码</label>
      <input id="password" name="password" type="password" autocomplete="current-password" required autofocus />
      <button type="submit">查看内容</button>
    </form>
    <div class="footer">
      {author_block}
    </div>
  </div>
</body>
</html>"""
