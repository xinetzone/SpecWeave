"""doocs/md 的 Python 3.14 复刻（doocs-md-py）。

提供四个通道：

- 渲染库：将 Markdown 渲染为微信公众号兼容的 HTML（对齐上游 packages/core）；
- 自托管 API：FastAPI 复刻 Cloudflare Workers 后端（账号/同步/上传/分享/市场/表情/通知）；
- 上传器：14 家图床的纯 Python 签名上传实现；
- MCP/CLI：stdio MCP Server 与 mdpy 命令行工具。

上游：doocs/md（WTFPL v2），源树 d:\\AI\\.chaos\\libs\\md。
"""

__version__ = "0.1.0"
