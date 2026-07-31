---
id: "volcengine-agentkit-wiki-05"
title: "快速入门指南"
source: "seven-concepts: volcengine-agentkit-wiki"
category: "learning"
tags: ["AgentKit", "快速入门", "HelloWorld", "安装部署", "FAQ"]
date: "2026-07-31"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "AgentKit 快速入门五步法：前置条件清单、5 步标准 HelloWorld 流程（安装→初始化→配置→本地启动→云端部署）、3 个典型场景最小代码片段、5 条常见报错 FAQ 与下一步进阶路径推荐。"
last_verified: "2026-07-31"
wiki_version: "1.0"
agentkit_version_target: "2026Q3"

---

# 05 快速入门指南

## 前置条件清单

在开始第一个 AgentKit 智能体开发之前，请确认以下环境与账号已准备就绪。每项都提供对应的验证命令，确保每一项检查通过后再进入后续步骤：

| 项目 | 要求 | 验证命令 |
|------|------|---------|
| Python 版本 | ≥ 3.10（推荐 3.11.x 稳定版） | `python --version` 或 `python3 --version` |
| pip 包管理器 | 最新稳定版（≥ 24.0） | `pip --version` 或 `pip3 --version` |
| 火山引擎账号 | 已注册账号并完成实名认证，已开通 AgentKit 服务权限 | 登录控制台 `console.volcengine.com/agentkit` 检查开通状态 |
| API Key | 已创建 Access Key（AK/SK），或使用子账号凭据并授予 AgentKit 管理员权限 | `cat ~/.volcengine/config` 查看配置文件 |
| 网络访问 | 能够访问火山引擎 API 域名与 PyPI 镜像源，无代理或防火墙阻断 | `ping open.volcengineapi.com -n 4` 检查连通性 |

若以上验证项未通过，请先完成对应环境配置：Python 版本不足请前往 python.org 下载安装；pip 版本过旧请运行 `python -m pip install --upgrade pip`；火山引擎账号与 AK/SK 请参考控制台「访问控制」页面完成创建与权限配置。

## 5 步完整 HelloWorld 流程

本流程将引导您从零开始构建第一个智能体应用，完成本地启动调试与云端部署全链路。每步均提供完整可复制命令、预期输出示例与常见排错提示。

### Step 1：安装 AgentKit SDK 与 CLI
**操作**：使用 pip 安装完整 SDK 包（含 CLI、示例模板与所有可选依赖），推荐使用清华镜像源加速下载：
```bash
pip install "agentkit[all]" -i https://pypi.tuna.tsinghua.edu.cn/simple
```
**预期输出**（最后 5 行摘要）：
```
Successfully installed agentkit-0.2.20 veadk-python-0.2.20 pydantic-2.7.0 fastapi-0.111.0 uvicorn-0.30.1
WARNING: You are using pip version 23.3; however, version 24.1 is available.
  Consider upgrading via the 'python -m pip install --upgrade pip' command.
Installing collected packages: ..., agentkit
```
**排错提示**：若出现权限错误请追加 `--user` 参数或使用虚拟环境（`python -m venv .venv && source .venv/bin/activate`）；若网络超时请切换镜像源或检查代理配置。

### Step 2：初始化项目脚手架
**操作**：使用 `agentkit init` 基于 starter 模板生成第一个智能体项目，项目名称为 `my-first-agent`：
```bash
agentkit init my-first-agent --template starter --region cn-beijing && cd my-first-agent
```
**预期输出**（生成的目录树结构）：
```
my-first-agent/
├── agent.py                  # 智能体主入口代码（已含示例 Tool 与 Entrypoint）
├── requirements.txt          # 依赖声明文件
├── config.yaml               # 应用配置文件（模型参数/工具权限等）
├── .agentignore              # 构建忽略规则
├── Dockerfile                # 标准容器构建文件
└── tests/
    └── test_agent.py         # 单元测试骨架
```
**排错提示**：若提示命令未找到请确认 Step 1 安装成功（运行 `agentkit --version` 验证）；若目录已存在请追加 `--force` 覆盖或更换项目名称。

### Step 3：配置火山引擎凭据
**操作**：运行 `agentkit config set` 将 AK/SK 与区域配置写入本地配置文件，激活默认 profile：
```bash
agentkit config set ak=AKLTY2JhNzE5NTRhOGMyNGYzxxxx sk=WVdSaFptWm1OakZoTjJWaE56Sxxxx region=cn-beijing
```
**预期输出**：
```
√ Profile [default] saved to C:\Users\YourName\.agentkit\config.yaml
  - Access Key: AKLTY2Jh****（已脱敏保存）
  - Region: cn-beijing
  - Runtime: auto-detect on deploy
√ Verification passed: credentials valid (account: 1234567890)
```
**排错提示**：若验证失败请检查 AK/SK 是否正确复制（注意无前后空格），确认子账号已授予 `AgentKitFullAccess` 策略；配置文件位置：Windows 为 `%USERPROFILE%\.agentkit\config.yaml`，Linux/Mac 为 `~/.agentkit/config.yaml`。

### Step 4：本地启动调试
**操作**：使用 `agentkit launch` 本地模式启动智能体服务，监听 8080 端口并开启文件变更自动重载：
```bash
agentkit launch --mode local --port 8080 --env dev --watch
```
**预期输出**：
```
√ Configuration loaded (env=dev, mode=local)
√ 1 tool registered: calculate_tax
√ 1 entrypoint registered: main_entry
√ Local server started at 0.0.0.0:8080
  Swagger UI    : http://localhost:8080/docs
  Health check  : http://localhost:8080/health
  Watch mode    : enabled (auto-reload on .py changes)
  Ready for requests...
```
**排错提示**：若端口被占用请更换 `--port` 参数或释放占用进程；浏览器访问 `http://localhost:8080/docs` 打开 Swagger UI 即可在线调试，点击 `Try it out` 输入用户问题后执行，验证 Tool 调用与回答生成是否正常。

### Step 5：云模式部署上线
**操作**：本地验证通过后，执行云模式部署命令将应用推送到 AgentKit Runtime，指定生产环境与 2 副本配置：
```bash
agentkit deploy --mode cloud --env prod --replicas 2 --cpu 1 --memory 2Gi --traffic 100%
```
**预期输出**：
```
√ Build phase: image built and pushed (digest: sha256:a1b2c3...)
√ Deploy phase: deployment created successfully
  Rolling update: 2/2 replicas ready, health check passed
  Traffic split: 100% → v1.0.0
√ SUCCESS: Your agent is live!
  Access URL   : https://agent-rt-abc12345.cn-beijing.agentkit.volces.com
  Dashboard    : https://console.volcengine.com/agentkit/runtime/rt-abc12345
  Observability: https://console.volcengine.com/apmplus/service/agent-rt-abc12345
```
**排错提示**：若构建失败请检查 Dockerfile 与依赖声明是否正确；若部署超时请检查配额是否充足（控制台「配额管理」页面查看）；部署成功后复制 Access URL 可直接访问智能体 API，Swagger UI 路径同本地调试。

## 典型场景最小代码片段

以下三个典型场景为最小可运行代码，保存为 `.py` 后可直接 `agentkit launch` 运行。

### 场景一：调用内部业务工具（REST API → Tool）
```python
from agentkit import App, ToolResult
from agentkit.adapters import RESTToolAdapter
import os
app = App(name="order-assistant", version="1.0.0", region="cn-beijing")
order_api = RESTToolAdapter(
    base_url="https://internal.company.com/order/api",
    auth_header={"Authorization": f"Bearer {os.getenv('ORDER_API_TOKEN')}"},
    timeout=15
)
@app.tool(name="query_order", description="根据订单号查询订单详情与物流状态")
def query_order(order_id: str) -> ToolResult:
    endpoint = f"/v1/orders/{order_id}"
    resp = order_api.get(endpoint)
    if resp.status_code != 200:
        return ToolResult(success=False, message=f"订单查询失败: {resp.text}")
    order = resp.json()
    summary = {"order_id": order["id"], "status": order["status"],
        "amount": order["total_amount"],
        "logistics": order.get("tracking", {}).get("status", "待发货")}
    return ToolResult(success=True, data=summary, message="订单查询成功")
@app.entrypoint(name="handle_customer_query")
def handle_customer_query(user_question: str, context) -> str:
    return app.run_harness(query=user_question, context=context).final_answer
if __name__ == "__main__":
    app.launch(mode="local", port=8081)
```

### 场景二：知识库问答（Knowledge Base 检索 + 回答）
```python
from agentkit import App
from agentkit.services import KnowledgeClient
from agentkit.types import SessionContext
app = App(name="kb-assistant", version="1.0.0", region="cn-beijing")
knowledge_base = KnowledgeClient.from_env(
    base_id="kb-company-handbook-v2", top_k=5, rerank_enabled=True
)
@app.entrypoint(name="qa_entry", description="基于员工手册知识库回答员工问题")
def qa_entry(user_question: str, context: SessionContext) -> str:
    search_result = knowledge_base.search(query=user_question)
    if not search_result.docs:
        return "抱歉，员工手册中暂未找到相关内容，请咨询 HR。"
    context_parts = [f"[{i+1}] {doc.title}\n{doc.snippet}" for i, doc in enumerate(search_result.docs)]
    prompt = f"基于员工手册回答问题，引用来源编号 [1][2]，禁止编造。\n参考内容：\n{chr(10).join(context_parts)}\n员工问题：{user_question}"
    answer = app.llm.generate(prompt, temperature=0.1, max_tokens=800)
    citations = [f"[{i+1}] {doc.title}" for i, doc in enumerate(search_result.docs)]
    return f"{answer}\n\n参考来源：\n{chr(10).join(citations)}"
if __name__ == "__main__":
    app.launch(mode="local", port=8082)
```

### 场景三：多 Agent 协作（A2A 主从协作 2 Agent）
基于 A2A 协议构建主从式架构：主 Agent 分发任务，子 Agent 回传结果：
```python
from agentkit import App, A2AClient, SessionContext
research_agent = A2AClient(agent_id="agent-rt-research001", region="cn-beijing",
    endpoint="https://research-agent.internal.agentkit.volces.com")
code_agent = A2AClient(agent_id="agent-rt-code002", region="cn-beijing",
    endpoint="https://code-agent.internal.agentkit.volces.com")
app = App(name="orchestrator-agent", version="1.0.0", region="cn-beijing")
@app.entrypoint(name="dispatch", description="主 Agent：意图识别后分发给子 Agent 协作")
def dispatch(user_task: str, context: SessionContext) -> str:
    intent = app.llm.classify(text=user_task,
        labels={"research": "信息搜集/市场调研/竞品分析", "code": "代码编写/Bug修复/技术方案"})
    if intent.label == "research":
        sub = research_agent.invoke(task=user_task, context=context.message_history, timeout=120)
        prefix = "【研究 Agent 报告】\n"
    elif intent.label == "code":
        sub = code_agent.invoke(task=user_task, context=context.message_history, timeout=120)
        prefix = "【代码 Agent 输出】\n"
    else:
        return "任务类型不匹配，请描述研究类或代码类需求。"
    summary = app.llm.summarize(sub.content, max_sentences=3, focus="可执行结论")
    return f"{prefix}{sub.content}\n\n【主 Agent 摘要】\n{summary}"
if __name__ == "__main__":
    app.launch(mode="local", port=8083)
```

## 常见报错 FAQ

以下 5 类错误按出现频率排序，每条均包含错误特征、可能原因与解决步骤：

### FAQ-1："PermissionDenied: 403" 错误
**错误信息片段**：`agentkit.errors.PermissionDenied: HTTP 403 Forbidden: AccessKey is not authorized for action agentkit:DeployApplication`
**可能原因**：① AK/SK 对应用户未授予 AgentKit 相关 IAM 策略；② 使用了子账号凭据但缺少关键权限；③ 凭据对应的账号未在目标区域开通 AgentKit 服务。
**解决步骤**：
1. 登录火山引擎「访问控制」→「策略管理」，为目标用户绑定 `AgentKitFullAccess` 系统策略；
2. 若使用自定义策略，确保包含 `agentkit:*` 与 `vefaas:*` 两类资源的读写权限；
3. 切换到 `cn-beijing` 区域重新配置后重试，确认当前区域已开通 AgentKit 服务。

### FAQ-2："ModuleNotFoundError: No module named 'agentkit'"
**错误信息片段**：`ModuleNotFoundError: No module named 'agentkit'` 或 `'agentkit' is not recognized as an internal or external command`
**可能原因**：① 安装 agentkit 的 Python 环境与当前执行环境不一致（多版本 Python 或虚拟环境未激活）；② pip 安装过程出现静默失败但未提示；③ 命令行使用的 python 与 pip 不属于同一路径。
**解决步骤**：
1. 运行 `python -m pip install "agentkit[all]"` 强制关联当前 Python 解释器安装；
2. 使用 `python -m agentkit --version` 替代裸 `agentkit` 命令验证安装，确保模块可加载；
3. 创建并激活虚拟环境后重新安装：`python -m venv .venv` → Windows 执行 `.venv\Scripts\activate`，Linux/Mac 执行 `source .venv/bin/activate`。

### FAQ-3："Timeout: Tool execution exceeded 30s"
**错误信息片段**：`agentkit.errors.ToolTimeoutError: Tool 'xxx' execution exceeded 30s timeout limit`
**可能原因**：① 被调用的后端 API 响应慢或网络延迟高；② Tool 默认超时阈值（30 秒）不满足业务需求；③ Tool 内部存在长轮询或大文件处理逻辑。
**解决步骤**：
1. 在 Tool 装饰器中显式设置 `timeout` 参数：`@app.tool(name="xxx", timeout=120)` 延长超时至 120 秒；
2. 检查 Tool 内部调用的外部 API 是否正常响应，单独用 curl/postman 验证接口延迟；
3. 对耗时任务改用异步 Tool 或任务队列模式：先返回「任务处理中」再通过回调通知结果。

### FAQ-4："ConfigNotFound: Cannot read credentials"
**错误信息片段**：`agentkit.errors.ConfigNotFound: Cannot read credentials from any of: ~/.agentkit/config.yaml, environment variables, IMDS metadata`
**可能原因**：① 未执行 `agentkit config set` 初始化配置；② 配置文件路径因系统差异未找到；③ 希望通过环境变量注入但未正确设置。
**解决步骤**：
1. 重新执行 `agentkit config set ak=xxx sk=xxx region=cn-beijing` 并确认输出验证成功；
2. 手动检查配置文件是否存在：Windows 路径 `C:\Users\用户名\.agentkit\config.yaml`，Linux/Mac 路径 `~/.agentkit/config.yaml`；
3. 如需环境变量方式注入，设置 `AGENTKIT_AK`、`AGENTKIT_SK`、`AGENTKIT_REGION` 三个环境变量即可自动读取。

### FAQ-5："Harness ValidationError: 工具未注册"
**错误信息片段**：`agentkit.errors.HarnessValidationError: Tool 'query_crm' referenced in harness config is not registered in current App context`
**可能原因**：① Harness 配置中引用了 Tool 名称但实际未用 `@app.tool` 装饰器注册；② Tool 名称拼写不一致（含大小写差异）；③ 使用外部 Gateway Tool 但未在 App 初始化时绑定 Tool Registry ID。
**解决步骤**：
1. 运行 `agentkit doctor` 命令执行自检，列出当前 App 已注册的 Tool 与 Entrypoint 清单，确认名称一致；
2. 检查 `@app.tool(name="query_crm")` 的 name 参数与 Harness 配置引用名完全一致，区分大小写；
3. 若使用 Gateway 托管的外部 Tool，在 App 初始化时传入 `tool_registry_ids=["tr-abc123"]` 参数绑定注册中心。

## 下一步进阶建议

根据您的角色与目标选择合适的进阶路径：

- **深入开发路线**（开发者/平台工程师）：[07 核心功能深度解析](./07-core-features-detailed.md)，掌握 Identity/Gateway/A2A/Session-Memory/Knowledge 五大模块集成模式。
- **场景学习路线**（产品/架构师）：[06 应用场景与落地方案](./06-application-scenarios.md)，学习四大典型场景架构与三大行业落地框架。
- **最佳实践路线**（投产团队）：[09 FAQ 与最佳实践](./09-faq-best-practices.md)，查阅 15+ FAQ、8 条最佳实践与 Demo→生产 12 项检查清单。

## 本章小结

本章提供了 AgentKit 从环境准备到云端上线的完整快速入门路径：前置条件清单逐项验证环境与账号；5 步标准 HelloWorld 流程（安装→初始化→配置→本地启动→云端部署）确保 15 分钟端到端跑通；三个典型场景代码片段（业务工具/知识库问答/多 Agent 协作）可作为二次开发起点；5 条高频 FAQ 覆盖常见错误 SOP 排障；三条进阶路线引导读者按角色深入学习。

← [04 SDK & CLI](./04-agentkit-sdk-cli.md) | [README](./README.md) | → [06 应用场景](./06-application-scenarios.md)
