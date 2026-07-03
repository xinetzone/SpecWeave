"""forum-bot — forum.trae.cn 论坛自动化操作工具。

基于 Playwright 实现 forum.trae.cn（Discourse 论坛）的自动化操作，
支持读取帖子、编辑正文、发布回复、清理草稿等功能。

拆分结构（遵循单一职责原则）：
- constants: 常量定义（URL、超时、ANSI颜色、CSS选择器）
- logger: 日志系统与彩色输出工具
- browser: Playwright浏览器自动化原语（延迟导入playwright）
- content: AI发布声明处理
- auth: 登录检测与首次登录流程（延迟导入playwright）
- operations/: 业务操作模块（延迟导入playwright）
  - read: 读帖
  - edit: 编辑帖子
  - reply: 发布回复
  - drafts: 草稿管理
- cli: argparse命令行入口（延迟导入playwright依赖）

使用方式：
  # 首次登录（打开有头浏览器，手动登录后按 Enter 保存状态）
  python -m forum_bot login

  # 读取帖子内容
  python -m forum_bot read 44601

  # 编辑帖子（从文件读取内容替换正文）
  python -m forum_bot edit 44601 --file new-content.md

  # 试运行（不实际提交写操作）
  python -m forum_bot edit 44601 --content "测试" --dry-run
"""


def main() -> None:
    from .cli import main as _main
    _main()


__all__ = ["main"]
