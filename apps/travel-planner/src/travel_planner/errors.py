"""受控异常体系。

所有面向用户的错误一律携带中文信息；未被本体系覆盖的异常视为缺陷，
由 Web 层统一兜底为通用中文错误页。
"""


class TravelPlannerError(Exception):
    """应用受控异常基类。"""


class ConfigError(TravelPlannerError):
    """配置或数据目录问题。"""


class ValidationError(TravelPlannerError):
    """数据校验失败（信息含字段路径定位）。"""


class StorageError(TravelPlannerError):
    """存储读写问题。"""


class LLMError(TravelPlannerError):
    """AI 生成层问题（未配置/网络/超时/解析/校验）。"""


class LockError(TravelPlannerError):
    """单实例锁冲突。"""
