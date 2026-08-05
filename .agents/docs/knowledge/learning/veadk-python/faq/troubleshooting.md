---
id: troubleshooting
title: 常见问题排查
source: veadk-python codebase analysis
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
---


# 常见问题排查

本文档收集 VeADK 使用过程中常见的问题、症状、排查步骤和解决方案。

---

## 一、API Key 配置问题

### 问题 1.1：模型调用返回 401 Unauthorized

**症状**：
- 调用Agent时返回401错误
- 日志显示 `Authentication failed` 或 `Invalid API key`
- 错误码 `401` 或 `403`

**可能原因**：
1. API Key未设置或设置错误
2. API Key过期或被禁用
3. API Key与模型endpoint不匹配
4. BytePlus/火山引擎环境切换问题

**排查步骤**：
1. 检查环境变量是否正确设置：
   ```bash
   echo $MODEL_AGENT_API_KEY
   echo $ARK_API_KEY
   ```
2. 确认显式传参优先级：显式传参 `model_api_key` > 环境变量 > config.yaml
   参考：[API Key四级优先级](../faq/best-practices.md#61-api-key四级优先级)
3. 如果使用 `model_api_key_name`，确认ARK Token服务可达
4. 检查 `CLOUD_PROVIDER` 环境变量是否正确
   - 国内火山引擎：`CLOUD_PROVIDER=volcengine`（默认）
   - BytePlus海外：`CLOUD_PROVIDER=byteplus`

**解决方案**：
```bash
# 设置正确的API Key
export MODEL_AGENT_API_KEY=your_valid_api_key
# 或在代码中显式传入
agent = Agent(model_api_key="your_valid_api_key", ...)
```

### 问题 1.2：工具调用返回403 Forbidden

**症状**：调用web_search等内置工具时返回403错误

**可能原因**：
- 火山引擎Access Key/Secret Key不正确
- 工具专属环境变量未设置
- IAM权限不足

**排查步骤**：
1. 检查工具专属环境变量：
   ```bash
   echo $TOOL_WEB_SEARCH_ACCESS_KEY
   ```
2. 检查全局凭证环境变量：
   ```bash
   echo $VOLCENGINE_ACCESS_KEY
   echo $VOLCENGINE_SECRET_KEY
   ```
3. 如果是BytePlus用户，确认已设置`CLOUD_PROVIDER=byteplus`

参考：[web_search.py凭证链](file:///d:/AI/.chaos/libs/veadk-python/veadk/tools/builtin_tools/web_search.py#L40-L65)

---

## 二、模型连接问题

### 问题 2.1：模型请求超时

**症状**：
- 调用Agent长时间无响应
- 日志显示 `timeout` 或 `ConnectionError`
- 流式输出中断

**可能原因**：
1. 网络连接问题（防火墙、代理）
2. 模型endpoint配置错误
3. 请求体过大（上下文超长）
4. 模型服务端过载

**排查步骤**：
1. 测试网络连通性：
   ```bash
   curl -I https://ark.cn-beijing.volces.com
   ```
2. 检查 `model_endpoint_id` 是否正确
3. 检查上下文长度是否超出模型限制
4. 查看是否需要配置代理：
   ```bash
   echo $HTTP_PROXY
   echo $HTTPS_PROXY
   ```

**解决方案**：
- 配置fallback模型链提高可用性：
  ```python
  model_name=["doubao-pro", "doubao-lite"]
  ```
- 检查网络和防火墙配置
- 缩短上下文窗口

### 问题 2.2：模型不存在（ModelNotFoundError）

**症状**：
- 错误提示模型不存在
- 返回404或model_not_found

**可能原因**：
- `model_name` 拼写错误
- 使用了未开通的模型
- endpoint配置错误

**排查步骤**：
1. 确认模型名称拼写正确（如`doubao-pro-32k`而非`doubao-pro`）
2. 确认已在火山引擎方舟控制台开通对应模型
3. 如果使用自定义endpoint，检查`model_endpoint_id`

**可用模型**：
- doubao-pro / doubao-pro-32k / doubao-pro-128k
- doubao-lite / doubao-lite-32k
- deepseek-v3 / deepseek-r1

---

## 三、依赖安装问题

### 问题 3.1：psycopg2 安装失败

**症状**：
- `pip install veadk` 时报错 `pg_config executable not found`
- 构建psycopg2失败

**可能原因**：缺少PostgreSQL开发库

**解决方案**：

**Windows**:
```bash
pip install psycopg2-binary
```

**macOS**:
```bash
brew install postgresql
pip install psycopg2
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install libpq-dev python3-dev
pip install psycopg2
```

> 不需要PostgreSQL功能时，可跳过此依赖。veadk默认使用SQLite作为短期记忆后端。

### 问题 3.2：Milvus/pymilvus 安装失败

**症状**：安装pymilvus时报编译错误

**解决方案**：
```bash
# 确保有cmake和C++编译器
pip install pymilvus>=2.4.0
# 或使用conda
conda install -c conda-forge pymilvus
```

### 问题 3.3：volcenginesdk 系列包冲突

**症状**：火山引擎SDK版本冲突

**解决方案**：使用pip的约束文件或在干净虚拟环境中安装：
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install veadk
```

### 问题 3.4：Python版本不兼容

**症状**：安装时提示Python版本不匹配

**解决方案**：VeADK要求Python 3.10+
```bash
python --version  # 确认 >= 3.10
```

---

## 四、记忆/知识库初始化失败

### 问题 4.1：PostgreSQL连接失败

**症状**：
- 短期记忆初始化报错
- 日志显示`connection refused`或`password authentication failed`

**排查步骤**：
1. 确认PostgreSQL服务运行中：
   ```bash
   # Windows
   net start postgresql
   # Linux/macOS
   pg_isready
   ```
2. 检查连接参数：host、port、database、user、password
3. 检查pg_hba.conf认证配置

**解决方案**：
- 开发环境可使用默认SQLite后端，无需配置PostgreSQL：
  ```python
  from veadk.memory import ShortTermMemory
  stm = ShortTermMemory()  # 默认SQLite后端
  ```
- 或正确配置PostgreSQL连接：
  ```python
  stm = ShortTermMemory(
      backend=PostgresqlBackend(
          host="localhost", port=5432,
          database="veadk", user="postgres",
          password="your_password",
      )
  )
  ```

### 问题 4.2：Milvus连接失败

**症状**：知识库初始化报错，连接Milvus失败

**排查步骤**：
1. 确认Milvus服务运行：
   ```bash
   docker ps | grep milvus
   ```
2. 检查host和port配置（默认19530）
3. 检查Milvus版本兼容性（pymilvus >= 2.4.0）

**解决方案**：
- 开发环境使用in_memory后端（无需Milvus）：
  ```python
  from veadk.knowledgebase import KnowledgeBase
  kb = KnowledgeBase()  # 默认in_memory，重启数据丢失
  ```
- 启动Milvus：
  ```bash
  # 使用docker-compose
  wget https://github.com/milvus-io/milvus/releases/download/v2.4.0/milvus-standalone-docker-compose.yml -O docker-compose.yml
  docker-compose up -d
  ```

### 问题 4.3：Redis连接失败

**症状**：长期记忆Redis后端连接失败

**排查步骤**：
1. 确认Redis服务运行
2. 检查redis_url格式：`redis://:password@host:port/db`
3. 检查Redis版本（建议6.0+）

**解决方案**：
```bash
# 启动Redis（开发）
docker run -d -p 6379:6379 redis:7-alpine
```

---

## 五、工具调用失败

### 问题 5.1：工具参数验证失败

**症状**：
- LLM调用工具时返回参数错误
- 日志显示`ValidationError`或`Missing required parameter`

**可能原因**：
1. 工具参数类型提示不清晰
2. 工具docstring描述不够详细
3. LLM没有正确理解参数格式

**解决方案**：
- 工具参数使用明确的类型注解
- docstring中详细描述每个参数的含义、格式、示例
- 复杂参数考虑使用pydantic模型
- 参考：[工具参数类型系统](../extensions/custom-tool.md#四工具参数类型系统)

### 问题 5.2：异步工具阻塞事件循环

**症状**：
- Agent响应极慢
- 并发调用时串行执行
- 日志中无明显错误但性能差

**可能原因**：同步阻塞操作在async函数中直接调用

**排查步骤**：检查工具实现中是否有：
- `time.sleep()` → 应使用 `await asyncio.sleep()`
- 同步 `requests.get()` → 应使用 `httpx.AsyncClient` 或 `await asyncio.to_thread(requests.get, ...)`
- CPU密集型计算 → 使用 `await asyncio.to_thread(...)` 包装

**解决方案**：参考[工具错误处理](../extensions/custom-tool.md#六错误处理)中的异步最佳实践

### 问题 5.3：ToolContext为None导致AttributeError

**症状**：访问`tool_context.state`时报`'NoneType' object has no attribute 'state'`

**可能原因**：工具函数参数中`tool_context`没有默认值`None`，或LLM调用时未传入

**解决方案**：
```python
# ✅ 正确：设置默认值None并检查
def my_tool(param: str, tool_context: ToolContext | None = None):
    if tool_context:
        state = tool_context.state
    else:
        state = {}
    ...
```

---

## 六、内存泄漏或性能问题

### 问题 6.1：进程内存持续增长

**症状**：
- Agent运行时间越长内存占用越高
- 内存不释放

**可能原因**：
1. 使用in-memory后端存储大量历史数据
2. Tracing数据未清理（使用InMemoryExporter时）
3. 长期记忆持续累积未清理

**排查步骤**：
1. 检查使用的memory backend类型（生产环境不要用in-memory）
2. 检查是否启用了InMemoryExporter跟踪
3. 检查是否定期清理过期会话

**解决方案**：
- 生产环境使用持久化后端（PostgreSQL/Redis/Milvus）
- Tracing使用TlsExporter上报而非内存存储
- 配置会话过期清理策略

### 问题 6.2：首次调用响应慢

**症状**：第一次调用Agent耗时很长，后续调用变快

**可能原因**：
- 懒加载：首次调用时才初始化LLM客户端、数据库连接等
- 模型冷启动

**解决方案**：
- 预热机制：启动时发送一个空请求完成初始化
- 部署时配置预热探针

### 问题 6.3：RunProcessor导致事件丢失

**症状**：
- 使用自定义RunProcessor后Agent响应不完整
- 没有输出或输出被截断

**可能原因**：RunProcessor的`async for`循环中没有`yield event`

**排查步骤**：检查RunProcessor实现：
```python
async def wrapper():
    async for event in event_generator_func():
        # 在这里处理event
        yield event  # ⚠️ 必须yield所有事件！
```

**解决方案**：参考[RunProcessor开发注意事项](../extensions/custom-run-processor.md#七开发注意事项)

---

## 七、部署问题（VeFaaS）

### 问题 7.1：VeFaaS部署超时

**症状**：`engine.deploy()` 长时间无响应或超时

**可能原因**：
- 代码包过大
- 依赖安装耗时过长
- 网络问题
- APIG网关配置冲突

**排查步骤**：
1. 检查项目目录大小：排除不必要的文件（.git、node_modules、__pycache__、.venv）
2. 检查`requirements.txt`是否有大量重依赖
3. 确认VeFaaS服务在目标区域可用
4. 查看日志获取详细错误信息

**解决方案**：
- 创建 `.veignore` 文件排除不需要打包的文件：
  ```
  .git/
  .venv/
  __pycache__/
  *.pyc
  tests/
  docs/
  .env
  ```
- 减少不必要的依赖

参考：[vefaas.mdx:223-228](file:///d:/AI/.chaos/libs/veadk-python/docs/content/docs/framework/vefaas.mdx#L223-L228)

### 问题 7.2：部署后访问返回502 Bad Gateway

**症状**：访问VeFaaS函数URL返回502

**可能原因**：
- 函数启动失败
- 依赖缺失
- 端口配置错误
- 运行时错误

**排查步骤**：
1. 查看VeFaaS控制台日志
2. 本地测试能否正常运行：
   ```bash
   python -m your_agent_module
   ```
3. 检查入口点配置是否正确
4. 检查requirements.txt是否完整

**解决方案**：
- 本地先跑通再部署
- 确认所有依赖都在requirements.txt中
- 检查VeFaaS运行时版本（Python 3.10+）

### 问题 7.3：config.yaml包含凭证导致安全警告

**症状**：
- 部署时检测到config.yaml包含明文密钥
- 文档警告不要提交config.yaml

**解决方案**：
- `config.yaml`加入`.gitignore`和`.veignore`
- 生产环境通过环境变量注入凭证
- 本地开发使用`.env`文件（也加入忽略列表）

参考：[vefaas.mdx:129-131](file:///d:/AI/.chaos/libs/veadk-python/docs/content/docs/framework/vefaas.mdx#L129-L131)

### 问题 7.4：APIG网关名称已存在

**症状**：部署时报错APIG gateway已存在

**可能原因**：之前部署创建过同名网关

**解决方案**：
- 使用不同的gateway_name
- 或在VeFaaS控制台删除旧网关后重试

---

## 八、Extension/Channel问题

### 问题 8.1：飞书消息不响应

**症状**：配置FeishuChannel后消息发送无反应

**排查步骤**：
1. 检查飞书应用配置：App ID、App Secret、Verification Token、Encrypt Key
2. 确认飞书事件订阅URL配置正确
3. 检查是否启用了所需权限（im:message、im:chat等）
4. 检查飞书机器人已加入对应群组

**参考**：[feishu_channel.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/extensions/feishu_channel.py)

### 问题 8.2：Extension注册后不生效

**症状**：调用`register()`后Extension没有被加载

**排查步骤**：
1. 确认在`agent.run()`之前注册
2. 检查Extension名称是否唯一
3. 确认Extension的setup方法正确挂载所需组件

**解决方案**：参考[Extension生命周期](../extensions/custom-extension.md#五extension生命周期钩子)

---

## 九、Tracing/Observability问题

### 问题 9.1：TLS日志上报失败

**症状**：TlsExporter报错无法连接

**排查步骤**：
1. 确认TLS服务endpoint正确
2. 检查Access Key/Secret Key有TLS写入权限
3. 检查网络策略是否允许出站连接

**解决方案**：
- 开发调试时使用InMemoryExporter在控制台查看trace
- 生产环境配置正确的TLS topic_id和AK/SK

---

## 十、通用排查流程

遇到未列出的问题时，按以下顺序排查：

1. **查看日志**：设置日志级别为DEBUG获取详细信息
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **最小复现**：用最简单的Agent配置复现问题，排除自定义逻辑干扰
   ```python
   from veadk.agents.llm_agent import Agent
   agent = Agent(
       model_name="doubao-pro",
       model_api_key="your_key",
       instruction="你好",
   )
   ```

3. **检查版本**：确认veadk版本最新
   ```bash
   pip show veadk
   pip install --upgrade veadk
   ```

4. **检查Python版本**：确认Python >= 3.10
   ```bash
   python --version
   ```

5. **隔离环境**：在新虚拟环境中测试，排除依赖冲突
   ```bash
   python -m venv test_env
   source test_env/bin/activate
   pip install veadk
   ```

6. **查阅文档**：
   - 官方文档：docs/ 目录
   - 代码示例：examples/ 目录
   - 架构洞察：[11-architecture-insights.md](../supporting-analysis/11-architecture-insights.md)
