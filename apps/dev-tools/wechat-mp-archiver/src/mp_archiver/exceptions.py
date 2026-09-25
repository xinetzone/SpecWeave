"""跨层共享异常（adapters 解析层与 core 归档层通用）。"""


class PayloadError(ValueError):
    """采集响应或页面无法解析。"""


class ApiRetError(RuntimeError):
    """平台返回非 0 ret。"""

    def __init__(self, ret: int, errmsg: str) -> None:
        super().__init__(f"微信接口返回 ret={ret}: {errmsg or '(无 errmsg)'}")
        self.ret = ret
        self.errmsg = errmsg


class CredentialExpiredError(ApiRetError):
    """登录态失效（需重新扫码）。"""


class RiskControlError(RuntimeError):
    """账号/环境级风控信号，继续逐篇请求大概率同败（AC-10：不继续猛打）。

    kind 取值：
    - ``risk_control``：文章页 403/429 重试用尽，或命中验证码/环境异常页面；
    - ``transport``：连续传输故障（超时/连接错误）达到批次熔断阈值。
    """

    def __init__(self, kind: str, reason: str) -> None:
        super().__init__(f"[{kind}] {reason}")
        self.kind = kind
        self.reason = reason
