from __future__ import annotations

from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = SCRIPTS_DIR.parents[1]

DEFAULT_TEMPLATE = (
    PROJECT_ROOT / "docs" / "retrospective" / "templates" / "xlsx-test-report-template.md"
)
DEFAULT_SUMMARY_TEMPLATE = (
    PROJECT_ROOT
    / "docs"
    / "retrospective"
    / "templates"
    / "release-gate-summary-template.md"
)

METRIC_KEY_MAP = {
    "总用例": "total_cases",
    "所有用例": "total_cases",
    "PASS": "pass",
    "FAIL": "fail",
    "NOTEST": "notest",
    "NOT TEST": "notest",
    "NT": "notest",
    "BLOCK": "block",
    "DI": "di",
    "DI值": "di",
    "严重问题数": "serious_issues",
    "所有严重问题": "serious_issues",
}

STATUS_VALUE_MAP = {
    "PASS": "pass",
    "FAIL": "fail",
    "NT": "notest",
    "NOTEST": "notest",
    "NOT TEST": "notest",
    "BLOCK": "block",
}

RISK_KEYWORDS = {
    "重启恢复": ("重启", "死机", "崩溃", "异常恢复", "软启", "断电恢复"),
    "弱网": ("弱网", "穿墙", "丢包", "重连", "断流", "网络异常"),
    "存储回放": ("TF卡", "TF", "存储", "录像", "回放", "文件损坏"),
    "音频": ("底噪", "回声", "啸叫", "破音", "吞字", "无声", "杂音"),
    "升级稳定性": ("升级失败", "升级后", "版本回退", "升级重启"),
    "预览稳定性": ("卡顿", "丢帧", "花屏", "黑屏", "拉流失败", "拉流", "延迟", "不同步"),
}

RISK_PRIORITY = (
    "重启恢复",
    "弱网",
    "存储回放",
    "音频",
    "升级稳定性",
    "预览稳定性",
)

PLATFORM_SEMANTIC_DEFAULTS = {
    "ha_domain": "tuya",
    "entity_scope": "camera",
}

PLATFORM_RISK_PROFILES = {
    "重启恢复": {
        "integration_traits": ("hub", "cloud_push"),
        "observation_surfaces": ("status", "status_range", "diagnostics"),
        "diagnostic_focus": "优先核对设备在线状态恢复、关键 DP 状态刷新与诊断导出中的异常恢复痕迹。",
    },
    "弱网": {
        "integration_traits": ("hub", "cloud_push"),
        "observation_surfaces": ("status", "function", "diagnostics"),
        "diagnostic_focus": "结合实体状态刷新延迟、云侧推送连续性与诊断字段，复核弱网下的重连与状态同步风险。",
    },
    "存储回放": {
        "integration_traits": ("hub", "cloud_push"),
        "observation_surfaces": ("status", "function", "status_range"),
        "diagnostic_focus": "重点映射录像、回放和存储相关能力字段，确认平台侧是否能观测到存储异常。",
    },
    "音频": {
        "integration_traits": ("hub", "cloud_push"),
        "observation_surfaces": ("status", "function", "status_range"),
        "diagnostic_focus": "结合摄像头实体能力与诊断字段，复核音视频相关功能项是否存在异常状态或能力缺口。",
    },
    "升级稳定性": {
        "integration_traits": ("hub", "cloud_push"),
        "observation_surfaces": ("status", "diagnostics", "token_info"),
        "diagnostic_focus": "复核升级后的在线状态恢复、云侧令牌续期与设备诊断信息是否保持稳定。",
    },
    "预览稳定性": {
        "integration_traits": ("hub", "cloud_push"),
        "observation_surfaces": ("status", "function", "status_range"),
        "diagnostic_focus": "重点关注实时预览相关实体能力、状态变化和功能范围，确认平台侧是否能反映画面链路异常。",
    },
}

RETEST_SUGGESTION_MAP = {
    "音频": "复测音频：底噪/回声/啸叫/吞字/连续性",
    "预览传输": "复测预览：弱网/长时预览/帧率与延迟/同步性",
    "预览稳定性": "复测预览：弱网/长时预览/帧率与延迟/同步性",
    "存储回放": "复测存储：TF 卡兼容/卡录首检/回放稳定/文件可用性",
    "弱网": "复测网络：穿墙/丢包/重连/码率自适应",
    "升级稳定性": "复测升级：升级成功率/断电恢复/版本回滚",
}

BASIC_INFO_KEY_MAP = {
    "项目": "项目",
    "设备型号": "设备型号",
    "固件版本": "固件版本",
    "APP版本": "APP版本",
    "APP": "APP版本",
    "测试时间": "测试时间",
    "测试完成时间": "测试时间",
    "测试人员": "测试人员",
}

RELEASE_THRESHOLD = "DI &lt;= 12 且 致命+严重 &lt;= 2"
