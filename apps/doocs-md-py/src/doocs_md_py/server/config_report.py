"""启动配置体检（FR-15：启动时报告"哪些功能启用"；密钥不入日志）。

体检报告只含布尔、枚举与计数，绝不含任何密钥/口令值——所有凭据字段一律降级为
「是否已配置」；PAT / token 列表只暴露数量。报告结构对密钥免疫，是"密钥不入日志"
的可机械断言基础（见 tests/server/test_config_report.py）。
"""

import logging

from .config import Config
from .upload_config import (
    get_upload_backend,
    is_upload_backend_ready,
    is_upload_enabled,
)

LOGGER_NAME = "doocs_md_py.config"


def _switch(flag: bool) -> str:
    return "on" if flag else "off"


def build_config_report(config: Config) -> dict:
    """构造配置体检报告（纯布尔/枚举/计数/路径，无凭据）。"""
    return {
        "oauth": config.is_oauth_configured(),
        "jwt": config.is_jwt_configured(),
        "afdian": config.is_afdian_configured(),
        "upload": {
            "enabled": is_upload_enabled(config),
            "backend": get_upload_backend(config),
            "ready": is_upload_backend_ready(config),
        },
        "emoji": {"backend": config.emoji_backend},
        # 管理员白名单只报数量，不回显名单
        "adminLogins": len(config.admin_github_logins),
        "storage": {
            "sqlite": config.sqlite_path,
            "localDir": config.storage_local_dir,
        },
    }


def format_config_report(report: dict) -> str:
    """把体检报告压成单行日志文本。"""
    upload = report["upload"]
    return (
        f"oauth={_switch(report['oauth'])}"
        f" jwt={_switch(report['jwt'])}"
        f" afdian={_switch(report['afdian'])}"
        f" upload={upload['backend']} enabled={_switch(upload['enabled'])}"
        f" ready={_switch(upload['ready'])}"
        f" emoji={report['emoji']['backend']}"
        f" admin={report['adminLogins']}"
        f" sqlite={report['storage']['sqlite']}"
    )


def log_config_report(
    config: Config, logger: logging.Logger | None = None
) -> dict:
    """输出启动体检日志并返回报告（供调用方/测试复用）。"""
    report = build_config_report(config)
    (logger or logging.getLogger(LOGGER_NAME)).info(
        "启动配置体检：%s", format_config_report(report)
    )
    return report
