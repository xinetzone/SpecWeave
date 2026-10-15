"""个人信息管家 Agent（info-butler）。

后端是 Python 3.14 的 FastAPI 服务（云端常驻），前端是由 Sphinx 构建的静态站
（GitHub Pages）。两者通过 ``/api/*`` 契约解耦，任一侧单独演进都不破坏另一侧。

分层：

    config      环境变量 → 强类型配置，缺项即降级
    similarity  中英混合相似度，零依赖、免向量
    llm         OpenAI 兼容端点封装，可请求级 BYOK 覆盖
    store       Supabase（PostgREST）优先，内存回退
    pipeline    录入归类 / 关联 / 问答 / 提取 / 待办 / 总结
    api         FastAPI 路由与鉴权
"""

__version__ = "0.2.0"

__all__ = ["__version__"]
