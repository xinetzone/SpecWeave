# jupyter-podman-client 变更日志（原子提交汇总）

> 本文件只记录消费端特有改动；SpecWeave 工作区根级、apps/containers 组级、构建端（jupyter-podman-rootless）的改动
> 不在本文件范围内。按七概念方法论每次 C（原子提交）阶段完成后追加一条；每条必须：
> ①可追溯（对应根工作区 git commit hash）②关联七概念场景（里程碑复盘/问题解决/重构优化/知识沉淀/创新突破）③说明验收点

## [Unreleased]

### 2026-09-07 · `feat:` Windows 11 WSL2 SDK 全链路支持 + AI 自治规范容器初始化

**关联七概念场景**：场景3「重构优化」（I→F→A→C 链路）+ 场景4「知识沉淀」（从 podman-py OKF v0.2 bundles 萃取跨平台模式）

**验收点**（原子提交 C4 单一职责，可独立验证）：

A. **tasks/ 层代码改动（podman-py SDK Windows 兼容）**
   - `utils.py`：新增 SDK 逃生舱常量、`sdk_strategy_from_env()` 归一化、`_has_wsl_host_support()` 双门卫、`wsl_distro_name()` 3 级回退 UTF-16 LE 解析、`_wsl_user_uid()` 探测缓存、`BaseUrlCandidate` 数据类、`sdk_base_url_candidates()` P0→P3 序列生成、`windows_diagnose_hint()` W-I1~W-I3 速查匹配
   - `client_core.py`：重写 `get_client()` 上下文管理器接入多候选 ping 循环、失败汇总表、诊断文案叠加；CLI fallback 行为零回归（全部失败仍 `yield None`）
   - `manage.py`：`_load_env_overrides()` 修复核心 Bug——新增 `load_dotenv(override=False, encoding="utf-8")` 把 .env 同步到 os.environ，保证 SDK 级逃生舱读到 .env 变量；import 清理未使用的常量
   - 静态验证：`python -m py_compile tasks/*.py` exit_code=0；VS Code `GetDiagnostics` 三文件零告警

B. **人类文档层改动（README.md + .env.example）**
   - `README.md` 新增 §5「Windows 11 × WSL2 支持」：§5.1 三路径矩阵、§5.2 四级连接优先级、§5.3 四策略逃生舱、§5.4 W-I1~W-I3 速查表、§5.5 A/B 维度分离表；原 §5→§6 / §6→§7 / §7→§8 / §8→§9 编号顺延
   - `README.md` §8「.env 配置完整清单」拆 8.1 容器级（9 项） + 8.2 SDK 级（4 项）两张表，明确优先级链：命令行 > shell export > .env > 默认
   - `.env.example` 追加 Windows WSL 专属 4 个 SDK 级变量：`PODMAN_CLIENT_SDK_STRATEGY`（含四策略注释）/ `WSL_DISTRO_NAME` / `CONTAINER_HOST` / `DOCKER_HOST`（兜底注释）
   - 双向锚点：README§5.4 ⇄ `utils.py::windows_diagnose_hint` ⇄ `.agents/rules/windows-wsl.md §5` 三处 W-I1~W-I3 条目 1:1 对应

C. **AI 协作者自治规范容器初始化（AGENTS.md + .agents/）**
   - `AGENTS.md`：消费端专属启动协议（嵌套路由 + 文档边界 + 内容敏感度预检）；项目概述；嵌套路由关系树；上下文路由表（10+ 条目）；10 条 P0 硬约束 C1~C10 违反打回清单；快速开始最小验证路径；父级引用声明；变更日志倒排
   - `.agents/README.md`：AI 资产容器索引；6 目录结构 + 3 规则文件；源代码真源表；人类文档↔AI 规则双向对应表；父级继承 7 层；新增规则 4 步流程；变更日志倒排
   - `.agents/rules/invoke-tasks.md`：消费端 invoke 开发规范；模块职责边界 4×4 禁止跨层表；两层后端架构 8 条不可变行为契约；CLI fallback 7 函数等价实现表；命名空间根 + container.* 双入口；6 条 P0 安全约束；3 条修改后必跑冒烟
   - `.agents/rules/sdk-connection.md`：6 合法 scheme 白名单 + npipe 严禁；Windows base_url 必显式约束；四策略逃生舱矩阵；多候选优先级序列（strategy × platform）；P1 WSL9P 生成契约（distro 3 级/UID 探测）；P3 tcp 兜底；8 条错误输出格式不可变；ImportError 降级安全
   - `.agents/rules/windows-wsl.md`：A/B 两维度分离表（核心差异）；两种用户画像；WSL 发行版名 3 级回退；UTF-16 LE 编码硬规定；_has_wsl_host_support 双门卫；UID 严禁硬编码 1000；W-I1~W-I3 三处同步对齐；.env 加载语义 override=False 红线；4 条必跑验证脚本
   - `.agents/{CHANGELOG.md,README.md,rules/*}` 其余子目录（roles/skills/scripts/workflows/templates/docs）预留 .gitkeep 占位（父级回退路径）

D. **治理承诺（七概念 G1~G4 质量门）**
   - G1（事实无因果）：所有 podman-py 行为陈述均有 OKF v0.2 bundles 原文锚定，无"应该/可能"类推断
   - G2（洞察四元组）：上一轮 WSL SDK 改造的根因分析四元组见 AGENTS.md 项目约束速览 C1~C10 后附的根因段
   - G3（模式可迁移）：从 bundles 萃取 2 个模式已落地——「Windows Podman 连接多候选自动降级」+「WSL2 发行版名 3 级回退」
   - G4（行动项原子化）：本次变更拆 A/B/C 三大原子块，可单独 revert 任意一块不影响其他块

**根仓库 git commit**（执行原子提交后回填此处 commit hash）：`[<TBD>](#)`
