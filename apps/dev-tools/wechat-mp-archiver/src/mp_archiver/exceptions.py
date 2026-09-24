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
