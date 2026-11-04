"""HTTP 客户端工厂：统一处理「环境代理」这个隐形杀手。

## 为什么需要这个模块

httpx 的 ``Client`` 默认 ``trust_env=True``，会自动读取 ``HTTP_PROXY`` /
``HTTPS_PROXY`` / ``NO_PROXY`` 等环境变量。这在访问**公网**时是对的，但在
**本机回环**上是灾难性的：

    代理把请求转发到目标时，request-target 会变成
    ``GET http://127.0.0.1:8787/api/health HTTP/1.1``
    （绝对 URI 形式）。而 uvicorn/h11 只认 origin 形式
    ``GET /api/health HTTP/1.1``，于是它把整串 URL 当成路径去匹配路由，
    404。

这个缺陷有一个恶劣特征：**它逃过了所有进程内测试**。FastAPI 的
``TestClient`` 直接调用 ASGI callable，根本不经过网络层，所以
``POST /api/items`` 在测试里返回 201，在真实 uvicorn 服务器上却返回 404。
凡是「测试全绿但服务起不来」的线上事故，都要先查这一条。

## 判定规则

回环地址（localhost / 127.0.0.0/8 / ::1）**永远不走代理**——本机服务
不需要代理，走了必然出错。公网地址**尊重环境代理**——企业网/CI 环境里
这往往正是访问外网的唯一通路，不能一刀切掉。

## 用法

所有对外 HTTP 请求都经由 :func:`http_client` 创建客户端，不要直接
``httpx.Client(...)``。
"""

import httpx

#: 判定为「本机」的地址前缀。``localhost`` 与整个 ``127.0.0.0/8`` 都在内：
# Docker 容器里的 ``127.0.0.1`` 指向容器自身，同样不该走代理。
LOOPBACK_HOSTS = frozenset({"localhost", "127.0.0.1", "::1", "[::1]"})


def is_loopback_host(host: str) -> bool:
    """判断主机是否属于回环地址（不应走代理）。"""
    if not host:
        return False
    cleaned = host.strip().lower()
    if cleaned in LOOPBACK_HOSTS:
        return True
    # 127.0.0.0/8 整段都是回环
    if cleaned.startswith("127."):
        return True
    return False


def trust_env_for(url: str) -> bool:
    """给定 URL，返回 httpx 是否应当信任环境代理变量。

    回环 → ``False``（禁用代理）；其余 → ``True``（尊重环境代理）。
    """
    host = httpx.URL(url).host
    return not is_loopback_host(host)


def http_client(url: str, timeout: float) -> httpx.Client:
    """按目标地址创建客户端，自动决定是否信任环境代理。"""
    return httpx.Client(timeout=timeout, trust_env=trust_env_for(url))
