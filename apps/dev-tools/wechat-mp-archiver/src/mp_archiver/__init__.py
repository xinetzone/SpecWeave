"""wechat-mp-archiver —— 微信公众号全量内容归档工具。

模块分层：
- config：环境变量/.env 配置（pydantic-settings）
- models：领域枚举与数据模型
- logging_utils：凭证脱敏日志
- naming：跨平台安全文件名
- http_client：保守限速 + 指数退避 HTTP 客户端
- db：SQLite 元数据库（五表状态机）
- adapters：采集服务/官方接口适配器（Task 3+）
- core / exporters：归档管线与 RAG/报表导出（Task 4+）
- cli：mp-archiver 命令行
"""

__version__ = "0.1.0"
