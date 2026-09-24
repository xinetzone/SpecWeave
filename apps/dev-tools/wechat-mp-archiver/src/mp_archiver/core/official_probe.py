"""官方源真实联调分阶段探针（TR-8.1）。

按"配置 → 网络 → access_token → batchget 单页 → biz 身份一致性"五段
逐步取证，任一段失败即给出精确处置建议，避免把网络/白名单问题误判为
凭证或代码问题。除 batchget 阶段消耗 1（异常裁剪时 2）次日配额计数外，
探针不写数据库、不下载正文。
"""

import logging
import re
from dataclasses import dataclass, field
from urllib.parse import parse_qs, unquote, urlsplit

from ..adapters.official_api import (
    API_BASE,
    DailyQuotaGuard,
    OfficialApiAdapter,
    OfficialApiPermissionError,
    PAGE_SIZE,
    parse_freepublish_page,
)
from ..config import Settings
from ..db import get_account_biz_by_alias
from ..exceptions import ApiRetError, PayloadError

logger = logging.getLogger(__name__)

# token 端点常见 errcode → 面向用户的处置建议
_TOKEN_HINTS = {
    40001: "access_token 无效（探针场景不应出现，请重试）",
    40013: "AppID 不合法：请核对 MP_ARCHIVER_WECHAT_APP_ID（wx 开头 18 位）",
    40125: "AppSecret 不正确：请在公众号后台「基本配置」重置后更新 .env",
    40164: "调用方出口 IP 不在白名单：请将该 IP 加入公众号后台 IP 白名单",
    48001: "该主体无接口权限（官方文档仅列认证服务号；订阅号以后台权限页为准）",
    45009: "接口调用频率超限：请稍后重试",
    40102: "AppID 或 AppSecret 为空：请检查 .env",
}

_IP_RE = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3})")


@dataclass(frozen=True, slots=True)
class StageResult:
    stage: str
    status: str  # ok / warn / fail / skip
    message: str
    details: tuple[str, ...] = ()


@dataclass(slots=True)
class ProbeReport:
    stages: list[StageResult] = field(default_factory=list)
    biz: str = ""

    @property
    def ok(self) -> bool:
        return all(s.status != "fail" for s in self.stages)

    @property
    def passed_network(self) -> bool:
        return any(s.stage == "network" and s.status == "ok" for s in self.stages)

    def add(self, stage: str, status: str, message: str,
            details: tuple[str, ...] = ()) -> None:
        self.stages.append(StageResult(stage, status, message, details))


def normalize_biz(value: str) -> str:
    """URL 解码并去除空白；兼容 MzA..%3D%3D 与 MzA..== 两种形态。"""
    return unquote((value or "").strip())


def probe_config(settings: Settings, account_alias: str,
                 conn) -> tuple[ProbeReport, str]:
    """第 0 段：凭证形态与 biz 解析（不触网）。"""
    report = ProbeReport()
    app_id = settings.wechat_app_id.strip()
    secret = settings.wechat_app_secret.get_secret_value().strip()

    if not app_id:
        report.add("config", "fail",
                   "未配置 MP_ARCHIVER_WECHAT_APP_ID（在项目根 .env 填写）")
    elif not re.fullmatch(r"wx[0-9a-f]{16}", app_id):
        report.add("config", "warn",
                   f"AppID 形态异常（期望 wx 开头共 18 位）：{app_id[:4]}…")
    else:
        report.add("config", "ok", f"AppID 形态正常：{app_id[:6]}…（已脱敏显示）")

    if not secret:
        report.add("config", "fail",
                   "未配置 MP_ARCHIVER_WECHAT_APP_SECRET（在项目根 .env 填写）")
    elif not re.fullmatch(r"[0-9a-f]{32}", secret):
        report.add("config", "warn",
                   "AppSecret 形态异常（通常为 32 位十六进制串），"
                   "若刚在后台重置过可忽略此提示")
    else:
        report.add("config", "ok", "AppSecret 已配置且形态正常（内容不显示）")

    biz = normalize_biz(settings.wechat_official_biz)
    if biz:
        report.add("config", "ok", f"biz 来自显式配置：{biz[:8]}…（已脱敏）")
    else:
        resolved = get_account_biz_by_alias(conn, account_alias) or ""
        if resolved:
            biz = normalize_biz(resolved)
            report.add("config", "ok",
                       f"biz 按别名「{account_alias}」从 R2 已同步数据解析成功")
        else:
            report.add(
                "config", "warn",
                f"无法解析 biz：未配置 MP_ARCHIVER_WECHAT_OFFICIAL_BIZ，"
                f"且库中无账号「{account_alias}」的 R2 记录；"
                "token 阶段仍可测试，但 batchget 身份核对需要 biz",
            )
    report.biz = biz
    return report, biz


def probe_network(client) -> StageResult:
    """第 1 段：到 api.weixin.qq.com 的 TLS/网络可达性（不使用真实凭证）。

    以无效 access_token 请求稳定的 getcallbackip：平台返回 JSON 40001
    即证明 DNS/TLS/网关链路正常。
    """
    try:
        response = client.get(
            f"{API_BASE}/getcallbackip",
            params={"access_token": "probe-invalid-token"},
        )
    except Exception as exc:  # httpx 超时/连接错误族
        return StageResult(
            "network", "fail",
            f"无法连接 api.weixin.qq.com：{exc.__class__.__name__}: {exc}",
            ("检查本机网络/DNS；如需代理请配置 MP_ARCHIVER_PROXY_URL",
             "公司网络可能拦截境外 443，请换网或走代理后重试"),
        )
    try:
        payload = response.json()
    except ValueError:
        return StageResult(
            "network", "fail",
            f"HTTP {response.status_code} 但响应非 JSON（前 80 字节："
            f"{response.text[:80]!r}），链路可能被代理/防火墙劫持",
        )
    if not isinstance(payload, dict):
        return StageResult("network", "fail", f"响应不是 JSON 对象：{payload!r}")
    errcode = int(payload.get("errcode") or 0)
    if errcode == 40001:
        return StageResult(
            "network", "ok",
            "网络链路正常（平台以 40001 正确应答探针 token，"
            "证明 DNS/TLS/网关可达）",
        )
    if errcode == 0:
        # 极小概率：平台放宽了该端点；同样证明链路正常
        return StageResult("network", "ok", "网络链路正常（平台返回 errcode=0）")
    return StageResult(
        "network", "warn",
        f"链路可达但返回意外 errcode={errcode}: {payload.get('errmsg')}",
    )


def probe_token(client, app_id: str, secret: str) -> tuple[StageResult, str]:
    """第 2 段：真实换取 access_token。返回 (结果, token 或空串)。"""
    adapter = OfficialApiAdapter(client, app_id, secret)
    try:
        adapter._request_token()  # noqa: SLF001：探针需要直接观测 token 生命周期
    except OfficialApiPermissionError as exc:
        return StageResult("token", "fail",
                           f"权限被拒：{exc}",
                           (_TOKEN_HINTS[48001],)), ""
    except ApiRetError as exc:
        hint = _TOKEN_HINTS.get(exc.ret, "请对照官方全局错误码表排查")
        ip_match = _IP_RE.search(exc.errmsg or "")
        details = (hint,)
        if exc.ret == 40164 and ip_match:
            details = (
                _TOKEN_HINTS[40164],
                f"平台记录的本机出口 IP：{ip_match.group(1)}（白名单填这个）",
            )
        elif exc.ret == 40164:
            details = (
                _TOKEN_HINTS[40164],
                "可在公众号后台白名单页看到平台记录的出口 IP",
            )
        return StageResult("token", "fail",
                           f"换取 access_token 失败 ret={exc.ret}: {exc.errmsg}",
                           details), ""
    except Exception as exc:  # 传输/解析类
        return StageResult("token", "fail",
                           f"token 请求异常：{exc.__class__.__name__}: {exc}"), ""

    token = adapter._token  # noqa: SLF001
    return StageResult(
        "token", "ok",
        f"access_token 换取成功（有效期约 7200 秒，脱敏显示：{token[:6]}…）",
        ("工具已按提前 300 秒过期管理，无需手动维护",),
    ), token


def probe_batchget(client, settings: Settings, biz: str,
                   alias: str) -> StageResult:
    """第 3 段：零写库拉取一页并核对结构与 biz 一致性（消耗 1 次配额计数）。"""
    guard = DailyQuotaGuard(
        settings.db_path.parent / "official_api_quota.json",
        settings.official_daily_call_cap,
    )
    if guard.remaining == 0:
        return StageResult(
            "batchget", "warn",
            "当日配额计数已达本地阈值，跳过实页探测；UTC 0 点后重跑",
        )

    adapter = OfficialApiAdapter(
        client, settings.wechat_app_id.strip(),
        settings.wechat_app_secret.get_secret_value().strip(),
    )
    try:
        raw = adapter.batchget_page(offset=0, guard=guard)
        page = parse_freepublish_page(raw, biz=biz, alias=alias)

        # no_content 裁剪自检：有组无条目时以 0 重取（与正式同步同策略）
        retried = False
        if page.group_count > 0 and len(page.groups) == 0:
            if guard.remaining == 0:
                return StageResult("batchget", "warn",
                                   "首页被裁剪且配额已耗尽，无法以 no_content=0 复核")
            raw = adapter.batchget_page(offset=0, guard=guard, no_content=0)
            page = parse_freepublish_page(raw, biz=biz, alias=alias)
            retried = True
            if page.group_count > 0 and len(page.groups) == 0:
                return StageResult(
                    "batchget", "fail",
                    "no_content=0 重取后仍无图文条目，响应结构疑似平台变更",
                )
    except OfficialApiPermissionError as exc:
        return StageResult("batchget", "fail", f"权限被拒：{exc}",
                           (_TOKEN_HINTS[48001],))
    except ApiRetError as exc:
        return StageResult("batchget", "fail",
                           f"batchget 返回 ret={exc.ret}: {exc.errmsg}",
                           (_TOKEN_HINTS.get(exc.ret,
                                             "请对照官方全局错误码表排查"),))
    except PayloadError as exc:
        return StageResult("batchget", "fail", f"响应解析失败：{exc}")
    except Exception as exc:  # 传输类
        return StageResult("batchget", "fail",
                           f"batchget 请求异常：{exc.__class__.__name__}: {exc}")

    details = [
        f"平台群发总数 total_count={page.total_groups}，本页 {page.group_count} 组，"
        f"展开图文 {len(page.groups)} 篇"
        + ("（首页经历 no_content=1 裁剪，已自动以 0 重取成功）" if retried else ""),
        f"单页上限 {PAGE_SIZE} 组；账号历史量大时正式同步按日配额分天完成",
    ]

    # biz 一致性核对：图文 URL 的 __biz 必须与配置/解析结果相同
    if biz and page.groups:
        url_biz_values = {
            normalize_biz(parse_qs(urlsplit(r.url or "").query).get("__biz", [""])[0])
            for r in page.groups
            if r.url
        }
        url_biz_values.discard("")
        if not url_biz_values:
            details.append("本页图文 URL 均未携带 __biz，无法做跨源身份核对（不影响入库）")
        elif url_biz_values == {normalize_biz(biz)}:
            details.append(f"biz 一致性核对通过：图文 URL __biz 与配置一致")
        else:
            return StageResult(
                "batchget", "fail",
                f"biz 不一致：配置/解析为 {normalize_biz(biz)[:8]}…，"
                f"图文 URL 实际为 {sorted(url_biz_values)}",
                ("说明 AppID 与目标账号/MP_ARCHIVER_WECHAT_OFFICIAL_BIZ 不属于同一主体，"
                 "请核对后重试",),
            )

    if page.total_groups == 0:
        return StageResult(
            "batchget", "warn",
            "接口连通但该号已发布图文总数为 0（新号或从未发布）；结构链路本身正常",
            tuple(details),
        )
    return StageResult("batchget", "ok",
                       "batchget 首页探测成功，响应结构与解析器匹配",
                       tuple(details))


# 短链/页面提取：og:url、页面内链接、内嵌变量
# 微信内置浏览器 UA：非微信 UA 触发人机验证码页（wappoc_appmsgcaptcha），
# 验证码页的 JS 模板占位符 __biz=${window.biz} 不是真实 biz 值
_MICROMESSENGER_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
    "MicroMessenger/8.0.49(0x18003131) NetType/WIFI Language/zh_CN"
)
_OG_URL_RE = re.compile(
    r'<meta[^>]+property=["\']og:url["\'][^>]+content=["\']([^"\']+)',
    re.IGNORECASE,
)
# 匹配 __biz=xxx，但 xxx 不得是 JS 模板占位符（含 $ 或 { ）
_BIZ_IN_TEXT_RE = re.compile(r"__biz=([^&\"'\s<>]+)")
_VAR_BIZ_RE = re.compile(
    r"""(?:var\s+biz|window\[['"]biz['"]\]|window\.biz)\s*=\s*["']([^"']+)["']"""
)
# 真实 biz 形态：Base64 串，至少 12 位字符，结尾 0-2 个 = 填充
# 实测 biz 形如 MzAxMjM0NTY3OA==（15 位 + 2 填充），下限 12 留余量
_VALID_BIZ_RE = re.compile(r"^[A-Za-z0-9+/]{12,}={0,2}$")


def _is_valid_biz(value: str) -> bool:
    """校验 biz 形态：Base64 串，排除 JS 模板占位符（${...}）等无效值。"""
    if not value:
        return False
    if any(ch in value for ch in "${}()"):
        return False
    return bool(_VALID_BIZ_RE.match(value))


def _identity_from_url(url: str) -> dict[str, str]:
    query = parse_qs(urlsplit(url).query)
    return {
        "biz": normalize_biz(query.get("__biz", [""])[0]),
        "mid": (query.get("mid", [""])[0] or "").strip(),
        "idx": (query.get("idx", [""])[0] or "").strip(),
        "sn": (query.get("sn", [""])[0] or "").strip(),
    }


def resolve_article_identity(client, article_url: str) -> dict[str, str]:
    """从公众号文章短链（/s/xxxx）解析 biz 等身份参数。

    微信短链通常不 302 跳转而是直接返回文章页 HTML，身份参数内嵌在
    页面中，故按"最终 URL → og:url → 正文 __biz 字面量 → var biz"
    四级依次提取。返回含 biz/mid/idx/sn/source 的字典；biz 缺失时抛错。

    非微信 UA 会触发人机验证码页（wappoc_appmsgcaptcha），验证码页的
    JS 模板占位符 ``__biz=${window.biz}`` 不是真实 biz；故强制使用
    MicroMessenger UA 绕过验证码，并对提取值做形态校验（Base64 串，
    排除 ``${...}`` 占位符）。
    """
    response = client.get(
        article_url,
        follow_redirects=True,
        headers={"User-Agent": _MICROMESSENGER_UA},
    )
    final_url = str(response.url)
    html = response.text or ""

    # 验证码页拦截：UA 仍被识别为非微信环境（少见，如 IP 被风控）
    if "wappoc_appmsgcaptcha" in final_url or "wappoc" in final_url:
        raise PayloadError(
            "微信返回人机验证码页（wappoc_appmsgcaptcha），无法提取 __biz；"
            "可能 IP 被风控或该链接已被删除，可换一篇历史文章重试"
        )

    candidates: list[tuple[str, str]] = [("最终 URL", final_url)]
    og_match = _OG_URL_RE.search(html)
    if og_match:
        candidates.append(("页面 og:url", og_match.group(1)))
    for match in _BIZ_IN_TEXT_RE.finditer(html):
        candidates.append(("页面内嵌链接", f"https://x/?__biz={match.group(1)}"))

    for source, candidate in candidates:
        identity = _identity_from_url(candidate)
        if _is_valid_biz(identity["biz"]):
            identity["source"] = source
            return identity

    # 最后手段：页面 JS 变量 var biz = "MzA..."
    var_match = _VAR_BIZ_RE.search(html)
    if var_match:
        biz = normalize_biz(var_match.group(1))
        if _is_valid_biz(biz):
            return {"biz": biz, "mid": "", "idx": "", "sn": "",
                    "source": "页面 var biz"}

    raise PayloadError(
        "无法从该链接提取 __biz（页面可能要求微信环境打开或已被删除）；"
        "可换一篇该号的历史文章重试"
    )


def run_full_probe(settings: Settings, client, *, account_alias: str,
                   conn) -> ProbeReport:
    """五段串行取证；前段失败时后段按依赖关系跳过。"""
    report, biz = probe_config(settings, account_alias, conn)

    net = probe_network(client)
    report.add(net.stage, net.status, net.message, net.details)
    if net.status == "fail":
        report.add("token", "skip", "网络不可达，跳过 token 探测")
        report.add("batchget", "skip", "网络不可达，跳过实页探测")
        return report

    app_id = settings.wechat_app_id.strip()
    secret = settings.wechat_app_secret.get_secret_value().strip()
    if not app_id or not secret:
        report.add("token", "skip", "缺少 AppID/AppSecret，跳过真实 token 探测")
        report.add("batchget", "skip", "凭证缺失，跳过实页探测",
                   ("在项目根 .env 配置后重跑 mp-archiver official-doctor",))
        return report

    token_stage, _ = probe_token(client, app_id, secret)
    report.add(token_stage.stage, token_stage.status, token_stage.message,
               token_stage.details)
    if token_stage.status != "ok":
        report.add("batchget", "skip", "token 无效，跳过实页探测")
        return report

    if not biz:
        report.add("batchget", "skip", "biz 未解析，跳过实页探测（先 list 同步或显式配置）")
        return report

    page_stage = probe_batchget(client, settings, biz, account_alias)
    report.add(page_stage.stage, page_stage.status, page_stage.message,
               page_stage.details)
    return report
