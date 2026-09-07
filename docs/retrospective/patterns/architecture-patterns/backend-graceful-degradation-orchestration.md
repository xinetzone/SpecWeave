---
id: "backend-graceful-degradation-orchestration"
title: "后端优雅降级编排模式"
type: "architecture-pattern"
date: "2026-09-07"
maturity: "L2-validated"
source:
  - "apps/containers/jupyter-podman-rootless 应用（R→I→E 七概念知识沉淀链路）"
  - "tasks/build.py 三层后端实现（compose → sdk → cli）"
  - "docs/09-three-tier-backend.md 架构文档"
related_patterns:
  - "multi-mode-network-redundancy"
  - "docker-modular-build-orchestration"
  - "three-tier-eval-scaling-orchestration"
tags: ["graceful-degradation", "backend-orchestration", "compatibility", "podman", "invoke", "sdk", "cli", "fallback", "cross-platform"]
validation_count: 2
reuse_count: 0
---

# 后端优雅降级编排模式

## 触发场景

同一个上层业务命令（构建镜像、启动容器、推送模型等）需要调用底层执行能力，但底层执行能力在不同用户环境中可用性差异极大：
- 有的用户安装了完整 SDK + 声明式编排工具（最完整能力）
- 有的用户只安装了 SDK 包，未配置声明式编排
- 有的用户什么 Python 包都没装，只在 PATH 里有 CLI 命令

核心矛盾：**用户环境碎片化不可控**，但业务命令必须"拿到就能跑"，不能因为缺某个 Python 包就直接抛异常退出。

**适用于**：
- DevOps / CLI 工具类项目：`invoke`、`make`、`fabric` 等上层任务系统
- 同一件事有多种技术实现路径（SDK / CLI / REST / Compose / YAML），路径之间语义等价但依赖不同
- 目标用户覆盖从"零配置尝鲜"到"深度集成生产使用"的宽范围频谱

**不适用于**：
- 只有一条正确实现路径的场景（强行加降级反而增加复杂度）
- 降级后语义不等价（如 SDK 支持流式输出但 CLI fallback 不支持，需在文档中明确标注能力差异）
- 安全敏感场景（降级路径绕过了关键安全检查会造成漏洞）

## 核心公理

模式基于以下不可再分的公理成立：

1. **用户环境碎片公理**：依赖越重，用户能直接跑通的概率越低。完整依赖包（`[full]` extra）的配置成功率通常 < 基础依赖（CLI 可用）的 1/3。
2. **能力阶梯公理**：声明式编排（Compose/K8s YAML）> SDK（REST API）> CLI（subprocess）是能力递减、兼容性递增的严格偏序——能力越强的方式依赖越重，越难跑通。
3. **语义等价公理**：降级路径的输入输出必须与主路径语义等价，即"同样的参数 → 同样的最终结果"（允许性能、日志颗粒度、监控能力不同）。
4. **静默降级公理**：降级应自动发生，用户无需显式指定 `--backend=cli`。用户只需要看到 `[Backend] Using xxx（Tier N）` 的一行日志，不需要知道 Tier 是什么。

## 核心做法（七要素降级编排）

### 1. 能力阶梯分层（3-4 层，从强到弱）

严格按「声明式 > SDK > CLI」顺序分层：

```
┌─────────────────────────────────────────────────┐
│  invoke 任务层（统一入口：build / run / push）  │
└──────────────┬──────────────────────────────────┘
               │  自动检测
               ▼
┌─────────────────────────────────────────────────┐
│  Tier 1: 声明式 YAML（优先）                     │
│  podman-compose / docker-compose / kubectl       │
│  能力：profiles、多文件覆盖、环境变量自动加载    │
└──────────────┬──────────────────────────────────┘
               │  失败 / 未安装
               ▼
┌─────────────────────────────────────────────────┐
│  Tier 2: 官方 SDK（REST API）                    │
│  podman-py / docker-py / kubernetes-python       │
│  能力：流式日志、事件监听、类型安全              │
└──────────────┬──────────────────────────────────┘
               │  失败 / 未安装 / socket 不可达
               ▼
┌─────────────────────────────────────────────────┐
│  Tier 3: CLI fallback（保底）                    │
│  subprocess 调用 podman/docker/kubectl           │
│  能力：零依赖、最通用、任何有 PATH 的环境可跑     │
└─────────────────────────────────────────────────┘
```

每层用一个独立的 `_tierN_xxx()` 函数封装，避免 if/else 嵌套地狱。

### 2. 每层独立可用性检测（布尔谓词）

每层独立写 `tierN_available()` 纯函数，返回 True/False，检测失败打日志不抛异常：

```python
def compose_available() -> bool:
    try:
        import podman_compose  # noqa: F401
        return True
    except ImportError:
        return False

def sdk_available() -> bool:
    try:
        import podman  # noqa: F401
        return True
    except ImportError:
        return False
```

**检测点必须在真正调用之前**，避免"import 成功但 socket 挂了"这种静默失败——如果 SDK 可用但连不上，也算 Tier 2 失败，继续降级。

### 3. 早失败 + 显式降级日志

每层调用包一层 try/except，失败后打印 `[Backend] xxx failed, falling back...` 再进入下一层：

```python
if _should_use_compose():
    print("[Backend] Using podman-compose (Tier 1)")
    if compose_build(...):  return  # 成功直接返回
    print("[Compose] Build failed, falling back to SDK/CLI...")

# Tier 2 + 3
if not _build_via_sdk(...):
    _build_via_cli(...)   # Tier 3 fallback：保底必须成功
```

关键原则：**Tier 3 不允许有任何 try/except 再降级**——到了 Tier 3 就直接裸跑，让底层错误暴露出来，方便用户排查。

### 4. 输入参数归一化接口（统一签名）

所有 tier 的函数签名必须相同，参数语义完全一致：

```python
# 三个函数的签名完全一致
def compose_build(project_root, no_cache, build_args): ...
def sdk_build    (project_root, tag, apt_mirror, conda_mirror, pip_mirror, no_cache): ...
def cli_build    (project_root, tag, apt_mirror, conda_mirror, pip_mirror, no_cache): ...
```

禁止在任务层写"如果 Tier 1 就传参数 A，如果 Tier 3 就传参数 B"。统一签名能保证 5 行任务层代码调用 100 行降级逻辑。

### 5. 结果格式兼容（输出归一化）

主路径（Tier 1/2）可能返回结构化对象，但 fallback（Tier 3）通常返回字符串 stdout。统一用「对象 + 打印日志」模式：
- SDK 成功：`client.images.build()` 返回 Image 对象，再 print 一行 build complete
- CLI 成功：`run_cmd()` 直接 stdout 打印 build 日志，不用解析

用户只关心日志里有「Build complete」和退出码 0，不关心返回的是 Image 对象还是 None。

### 6. 平台差异在最低公共层处理

Windows pty、路径转换、9p 文件系统 CRLF、WSL 发行版检测等**平台差异**，一律放到 **Tier 3（CLI fallback）** 层或共享工具库（utils.py）处理，不能让 Tier 1/2 的代码里出现大量 `if platform.system() == "Windows"` 分支。

示例：`run_cmd()` 封装里自动降级 Windows pty：
```python
use_pty = pty and platform.system() != "Windows"
```

### 7. 不可降级能力显式标注 Not Support

如果某个能力 Tier 1 支持但 Tier 3 不支持（事件监听、实时 streaming、compose profiles），在函数 docstring 中用 **Tier Required: Tier 1+** 标注，Tier 3 运行到此处直接 `raise NotImplementedError("xxx 功能需要 Tier 1（podman-compose）支持")`，不允许静默返回伪造结果。

## 反模式（实际踩坑教训，至少 3 条）

### 反模式 1：跳过可用性检测，直接 try/except 大包裹
直接 `try: compose_build() except Exception: cli_build()` 大包裹——compose 内部的构建逻辑异常（不是 ImportError，是 Containerfile 写错了）也会被当成"compose 不可用"吃进去，导致明明 Tier 1 应该报的编译错误被 Tier 3 再报一遍同样的错误，日志重复混乱。
**对策**：可用性检测（import 检查）+ 真实执行分离，只有检测失败才降级。

### 反模式 2：Tier 3 保底路径也用了 try/except 静默吞错
```python
# ❌ 错误
try:
    run_cmd(...)
except Exception as e:
    print("cli failed:", e)   # 吞掉了真实错误栈
# 用户只看到 "cli failed"，不知道是 CRLF / 9p / 密码错 / 镜像不存在
```
**对策**：Tier 3 不允许兜底——让它把最原始、最底层的异常直接抛给用户。

### 反模式 3：降级后继续"升级"回上层
```python
# 伪代码：Tier 1 失败降级 Tier 3，Tier 3 代码里又去 import Tier 1
def cli_build():
    import podman_compose  # 莫名其妙回到 Tier 1
```
**后果**：循环调用，栈溢出 / 无限重试。
**对策**：每层函数的依赖只比它自己"更底层"——Tier 2 SDK 可以调 Tier 3 CLI 做部分事，Tier 3 CLI 绝不 import Tier 1/2 的任何东西。

### 反模式 4：检测函数有副作用
```python
def sdk_available():
    client = podman.PodmanClient()   # 副作用：连接 socket，需 3 秒超时
    return client.ping()
```
连续调用 3 次 `sdk_available()` 等于连 3 次 socket，白白等 9 秒。
**对策**：检测函数纯函数化，只做 import；连接失败算 Tier 执行失败，不算检测失败。

### 反模式 5：用户显式指定后端与自动降级冲突
代码提供了 `--backend=compose` 参数，但用户环境里 compose 没装，代码还是降级到 CLI。用户传了 `--backend=compose` 就等于说"如果 Tier 1 不行请直接报错，不要自作主张降级"。
**对策**：存在显式 backend 参数时，禁用自动降级；跑不起来直接抛 Exit，明确告诉用户"指定的 backend 不可用，请安装 xxx"。

## 检验标准

做完怎么知道做对了？以下 6 条全部满足：

1. [ ] 环境缺失检测：在空 venv 里执行任务（`pip install invoke` 只装基础依赖），Tier 3 CLI 路径成功退出码 0，无需安装 SDK/Compose。
2. [ ] 降级日志可见：运行时能看到一行 `[Backend] Using xxx（Tier N）`，失败降级时有 `[Backend] xxx failed, falling back to yyy...` 的明确日志。
3. [ ] 输出一致：分别在 Tier 1 / Tier 2 / Tier 3 独立环境跑同一个命令（如 `build --apt-mirror=tuna`），产物字节级等价（镜像 ID 相同、SHA256 相同）。
4. [ ] 错误栈不丢失：Tier 1 遇到真正的业务错误（Containerfile 语法错），原错误栈完整输出，不被 fallback 吞掉，不重复报两次。
5. [ ] 显式 backend 模式：传 `--backend=compose` 在无 compose 环境里直接报错，不降级；错误消息包含"请安装 xxx"指导。
6. [ ] 无重复代码：3 个 tier 函数之间不出现复制粘贴的参数解析/构建步骤，共享逻辑抽到 utils。

## 迁移验证（非当前领域）

这个模式可以横向迁移到完全不同的领域：

**迁移 1：LLM API 多供应商客户端（非容器领域）**
- Tier 1：官方 Python SDK（OpenAI SDK、Anthropic SDK）
- Tier 2：OpenRouter / OneAPI 统一兼容 SDK（供应商中转）
- Tier 3：`requests.post()` 裸 HTTP 调用（任何能上网的环境都能跑）
- 典型场景：用户公司网络封锁了 OpenAI API 直连，但开放了代理中转——Tier 1 超时失败自动降级 Tier 2 再 Tier 3，不用改代码。

**迁移 2：数据库迁移工具（非 DevOps 领域）**
- Tier 1：声明式迁移（Alembic autogenerate + compare metadata）
- Tier 2：SQLAlchemy ORM 执行原生迁移脚本（engine.execute）
- Tier 3：`subprocess.run(["mysql", "-e", source_file])` 直接跑 SQL（DBA 最喜欢的保底）
- 典型场景：线上只有 mysql 客户端，没装 Python DB driver。

两个迁移领域都满足：「依赖越重能力越强 → 能力越弱兼容性越高」的阶梯公理，证明模式抽象层级正确，不绑定容器场景。
