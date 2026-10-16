"""分享页 favicon（upstream: apps/api/src/share-head.ts 1:1）。

静态文件由 T19 静态托管从前端产物 public/images/ 提供。
"""

# upstream: share-head.ts:1
SHARE_FAVICON_PATH = "/images/favicon-32x32.png"


def share_page_favicon_link() -> str:
    """upstream: share-head.ts:4-6。"""
    return (
        f'<link rel="icon" type="image/png" sizes="32x32" '
        f'href="{SHARE_FAVICON_PATH}" />'
    )
