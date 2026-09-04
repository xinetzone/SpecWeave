---
spec: jupyter-okf-wiki-group-spec
version: 1.0.0
created: 2026-08-22
---

# Jupyter 分组 OKF Wiki 全量处理 - 任务分解

## Phase 0: 准备阶段

- [ ] **T0.1**: 盘点源码本地状态
  - 检查 `external/libs/jupyter/` 下已有哪些 bundle 的源码
  - 对照 67 个 bundle 清单，列出缺失的源码仓库
  - 记录已有源码的版本/最后 commit（如有）

- [ ] **T0.2**: 克隆/更新 Jupyter 生态源码
  - 将缺失的源码仓库克隆到 `external/libs/jupyter/<bundle-name>/`
  - 对已有源码执行 `git pull` 更新到最新稳定版本
  - 对没有独立 GitHub 仓库的 bundle（如 governance 类、meta 类），确认源码来源（jupyter/meta 仓库、子目录、或文档仓库）
  - 输出源码就绪清单

- [ ] **T0.3**: 建立进度追踪文档
  - 创建 `.trae/specs/okf-wiki-ecosystem/jupyter-okf-wiki-group/progress.md`
  - 按批次记录每个 bundle 的处理状态（pending/R-done/I-done/V-done）
  - 以 cockle/binderhub 为质量基准模板，确认 facts.md 和 insights.md 的格式标准

- [ ] **T0.4**: 全量 bundle 状态复查
  - 对 67 个 bundle 重新执行完成度检查脚本
  - 精确分类：已完成（有完整 facts+insights）、部分完成（有其一）、待补全（全无）
  - 更新状态分类（之前分析的 14/2/51 可能需要根据实际复查结果微调）

---

## Phase 1: 协议层 + 格式层（Batch 1，约 5 个 bundle）

**架构层**: 协议层与格式层是 Jupyter 生态的基础，优先处理以建立底层理解。

- [ ] **T1.1**: jupyter-core — 核心路径/配置/规范
  - R 阶段：采集目录结构、核心模块（paths.py、application.py 等）、配置系统、路径规范事实
  - I 阶段：分析 jupyter-core 在生态中的基础地位、路径查找算法、配置层级设计
  - V 阶段：抽样验证 facts、检查 sources 路径

- [ ] **T1.2**: jupyter-client — 内核通信协议
  - R 阶段：采集 KernelManager、KernelClient、消息协议（ZMQ/Wire Protocol）、session 管理事实
  - I 阶段：分析内核生命周期管理、消息通道（shell/iopub/control/stdin）、协议版本演进
  - V 阶段：抽样验证

- [ ] **T1.3**: nbformat — .ipynb 格式规范
  - R 阶段：采集 Notebook 节点结构、JSON Schema、验证器、版本迁移（v3→v4→v4.5）事实
  - I 阶段：分析 Notebook 格式设计哲学、节点类型系统、验证机制、与 nbconvert 的协作
  - V 阶段：抽样验证

- [ ] **T1.4**: jupyter — 元仓库/IPython 兼容层
  - R 阶段：采集元仓库结构、子包组织、兼容性 shim、命令行入口事实
  - I 阶段：分析 jupyter 元包的历史演进、从 big split 到 metapackage 的设计
  - V 阶段：抽样验证

- [ ] **T1.5**: ipython — 交互式 Python 内核
  - R 阶段：采集 IPython 核心架构（InteractiveShell、Magics、Completer、Display、History）事实
  - I 阶段：分析 IPython 作为内核的执行模型、魔法命令系统、显示协议、与 jupyter-client 的集成
  - V 阶段：抽样验证

---

## Phase 2: 服务层核心（Batch 2，约 5 个 bundle）

**架构层**: 服务层是 Jupyter Web 应用的后端基础。

- [ ] **T2.1**: jupyter_server — 后端核心服务
  - R 阶段：采集 Tornado 服务器架构、ExtensionApp、认证授权（IdentityProvider）、内核管理（MappingKernelManager）、内容管理（ContentsManager）、Session 管理、REST API 端点、WebSocket 通信事实
  - I 阶段：分析 ServerApp 启动流程、扩展加载机制、内核生命周期管理、认证模型演进（jupyter_server 2.x 的 Identity 模型）
  - V 阶段：抽样验证

- [ ] **T2.2**: jupyter_server_fileid — 文件 ID 服务
  - R 阶段：采集文件 ID 映射机制、CRDT 支持、数据库存储事实
  - I 阶段：分析文件 ID 在协作场景中的作用、与 jupyter-collaboration 的关系
  - V 阶段：抽样验证

- [ ] **T2.3**: jupyter-server-terminals — 终端管理
  - R 阶段：采集终端后端实现、PTY 管理、WebSocket 终端协议事实
  - I 阶段：分析终端服务的架构、与 jupyter_server 的集成方式
  - V 阶段：抽样验证

- [ ] **T2.4**: enterprise-gateway — 企业级网关
  - R 阶段：采集远程内核管理、Kubernetes/YARN 集成、内核生命周期委托、负载均衡事实
  - I 阶段：分析 EG 与 jupyter_server 的区别、多租户内核调度、企业级扩展点
  - V 阶段：抽样验证

- [ ] **T2.5**: jupyverse + fps — 新一代异步后端框架
  - R 阶段：jupyverse 采集 FPS 插件架构、FastAPI 集成、异步内核管理事实；fps 采集插件系统、FPS API 设计事实
  - I 阶段：分析 jupyverse/fps 与 jupyter_server 的设计差异、基于 FastAPI 的现代化重构思路
  - V 阶段：抽样验证（注意 fps 可能已有部分内容）

---

## Phase 3: 应用层核心（Batch 3，约 4 个 bundle）

**架构层**: 用户直接交互的主要应用。

- [ ] **T3.1**: jupyterlab + jupyterlab_server — 主前端 IDE
  - R 阶段：jupyterlab 采集 Lumino 应用架构、插件系统（JupyterFrontEndPlugin）、命令面板、文档注册表、布局系统、扩展点事实；jupyterlab_server 采集 Lab 后端服务、工作区管理、设置管理、清单（listing）API 事实
  - I 阶段：分析 JupyterLab 插件架构设计、文档-视图-渲染器模型、应用 Shell 布局系统、扩展生态系统
  - V 阶段：抽样验证（jupyterlab_server 已有部分内容需检查）

- [ ] **T3.2**: jupyter-notebook（nbclassic）— Notebook v7+ / Classic
  - R 阶段：采集 Notebook v7 基于 jupyterlab 的重构、经典界面兼容模式事实
  - I 阶段：分析 Notebook v7 与 JupyterLab 的关系、经典用户的迁移路径
  - V 阶段：抽样验证

- [ ] **T3.3**: jupyterhub — 多用户 Hub
  - R 阶段：采集 Spawner/Authenticator/Proxy 三大核心抽象、用户管理、服务管理、API Token、OAuth 集成事实
  - I 阶段：分析 Hub 架构（Hub-Proxy-Spawner 三段式）、可扩展认证/启动机制、与 binderhub/the-littlest-jupyterhub 的关系
  - V 阶段：抽样验证

- [ ] **T3.4**: binderhub — 从 Git 到可交互环境
  - R 阶段：已有 binderhub，复查/更新 facts.md（RepoProvider 插件、SSE 事件流、repo2docker 集成、Docker Registry、Kubernetes 调度事实）
  - I 阶段：已有 insights.md，复查/更新架构洞察
  - V 阶段：独立验证（已有内容抽样核对 + 修正）

---

## Phase 4: JupyterLite（WebAssembly 生态）（Batch 4，约 6 个 bundle）

**架构层**: 浏览器端 Jupyter，基于 Pyodide/Xeus。

- [ ] **T4.1**: jupyterlite — 浏览器端 Jupyter 主项目
  - R 阶段：采集 Lite 架构、Service Worker 驱动、Emscripten 内核、内容管理（浏览器存储）、静态部署事实
  - I 阶段：分析 JupyterLite 与传统 Jupyter Server 的架构差异、浏览器端内核模型、静态站点部署方案
  - V 阶段：抽样验证

- [ ] **T4.2**: pyodide-kernel — Pyodide Python 内核
  - R 阶段：采集 Pyodide 内核实现、comlink 通信、包管理（micropip）事实
  - I 阶段：分析 Pyodide 内核在浏览器中的执行模型、与 IPython 内核的差异
  - V 阶段：抽样验证

- [ ] **T4.3**: jupyterlite-lsp + jupyterlite-sphinx + jupyterlite-ai
  - R 阶段：分别采集 LSP 集成、Sphinx 嵌入、AI 集成的事实
  - I 阶段：分析 Lite 生态扩展模式
  - V 阶段：抽样验证

- [ ] **T4.4**: litegitpuller + repo2jupyterlite
  - R 阶段：采集 Git 内容拉取、仓库转换为 Lite 站点事实
  - I 阶段：分析内容分发机制
  - V 阶段：抽样验证

- [ ] **T4.5**: xeus + xeus-lite-demo
  - R 阶段：xeus 采集 C++ 内核框架、内核协议原生实现事实；xeus-lite-demo 采集 Xeus 在浏览器中的编译运行事实
  - I 阶段：分析 Xeus 作为原生内核实现的架构、与 ipykernel 的对比
  - V 阶段：抽样验证

---

## Phase 5: 前端 UI 框架与渲染（Batch 5，约 5 个 bundle）

- [ ] **T5.1**: lumino — JupyterLab 底层 UI 工具包
  - R 阶段：采集 Widget 基类、Signal/Slot 机制、布局系统（DockPanel/TabPanel/BoxPanel）、CommandRegistry、数据模型事实
  - I 阶段：分析 Lumino 与 Phosphor 的关系、虚拟 DOM 与命令模式的融合、为什么 JupyterLab 选择 Lumino
  - V 阶段：抽样验证

- [ ] **T5.2**: jupyter-renderers — 输出渲染器
  - R 阶段：采集 MIME 渲染器注册、内置渲染器（geojson/plotly/Vega 等）、扩展机制事实
  - I 阶段：分析 MIME 渲染架构与插件系统的集成
  - V 阶段：抽样验证

- [ ] **T5.3**: ui-profiler — UI 性能分析
  - R 阶段：采集 Profiler 扩展、渲染性能测量、FPS 监控事实
  - I 阶段：分析 JupyterLab 性能优化工具链
  - V 阶段：抽样验证

- [ ] **T5.4**: jupyterlab-desktop — 桌面应用
  - R 阶段：采集 Electron 封装、内置 Python/conda、系统集成事实
  - I 阶段：分析桌面端架构与 Web 版的差异
  - V 阶段：抽样验证

- [ ] **T5.5**: terminal + cockle
  - R 阶段：terminal 采集 Jupyter 终端扩展事实；cockle 已有 facts.md，复查更新
  - I 阶段：terminal 分析终端前端实现；cockle 已有 insights.md，复查验证
  - V 阶段：cockle 独立验证；terminal 抽样验证

---

## Phase 6: 内核生态（Batch 6，约 4 个 bundle）

- [ ] **T6.1**: echo-kernel + javascript-kernel + p5-kernel
  - R 阶段：采集各参考内核的实现结构、内核协议最简实现事实
  - I 阶段：分析这些内核作为参考实现的教学价值、最简内核模式
  - V 阶段：抽样验证

- [ ] **T6.2**: jupyterlab-webrtc-docprovider — WebRTC 协作
  - R 阶段：采集 WebRTC 驱动的协作编辑、Yjs CRDT 集成事实
  - I 阶段：分析实时协作的技术选型（Yjs + WebRTC vs 中央服务器）
  - V 阶段：抽样验证

- [ ] **T6.3**: jupyter-collaboration — 官方协作扩展
  - R 阶段：采集 RTC 协作、文档共享、用户感知事实
  - I 阶段：分析协作编辑架构、CRDT 同步机制
  - V 阶段：抽样验证（可能有部分已有内容）

---

## Phase 7: 工具链（Batch 7，约 8 个 bundle）

- [ ] **T7.1**: nbconvert — Notebook 格式转换
  - R 阶段：采集 Exporter 体系、模板系统、Preprocessor 管线、NbConvertApp 事实
  - I 阶段：分析 nbconvert 的转换管线设计、Exporter 插件机制、与 pandoc/Jinja2 的集成
  - V 阶段：抽样验证

- [ ] **T7.2**: nbviewer — Notebook 在线查看器
  - R 阶段：采集 nbviewer 架构、缓存机制、GitHub/Gist URL 渲染、渲染后端事实
  - I 阶段：分析 nbviewer 作为静态渲染服务的架构设计
  - V 阶段：抽样验证

- [ ] **T7.3**: papyri — 文档生成工具
  - R 阶段：采集 papyri 文档生成架构、AST 解析、交叉引用事实
  - I 阶段：分析 papyri 与 Sphinx 的差异、Jupyter 生态文档工具链
  - V 阶段：抽样验证（注意 papyri 源码在 external/libs/jupyter/papyri/）

- [ ] **T7.4**: jupyter_releaser — 发布自动化
  - R 阶段：采集发布流程、checklist 系统、npm/PyPI 双发布事实
  - I 阶段：分析 Jupyter 标准化发布流程设计
  - V 阶段：抽样验证

- [ ] **T7.5**: jupyterlab-translate + language-packs — 国际化
  - R 阶段：采集翻译提取、crowdin 集成、语言包结构事实
  - I 阶段：分析 JupyterLab 国际化方案
  - V 阶段：抽样验证

- [ ] **T7.6**: pytest-jupyter — 测试工具
  - R 阶段：采集 pytest fixtures、临时 Jupyter 环境、内核测试工具事实
  - I 阶段：分析 Jupyter 生态的测试策略
  - V 阶段：抽样验证

- [ ] **T7.7**: jupyterlab-pygments — 语法高亮
  - R 阶段：采集 Pygments 主题、CSS 变量集成、代码单元高亮事实
  - I 阶段：分析语法高亮与 JupyterLab 主题系统的集成
  - V 阶段：抽样验证

---

## Phase 8: 扩展项目（Batch 8，约 10 个 bundle）

- [ ] **T8.1**: jupyterlab-git + jupyterlab-github
  - R 阶段：采集 Git 扩展架构、GitHub 浏览器集成事实
  - I 阶段：分析版本控制集成模式
  - V 阶段：抽样验证

- [ ] **T8.2**: jupyterlab-latex + jupyter-resource-usage
  - R 阶段：采集 LaTeX 编辑、资源监控扩展事实
  - I 阶段：分析扩展实现模式
  - V 阶段：抽样验证

- [ ] **T8.3**: jupyter-scheduler — 任务调度
  - R 阶段：采集调度器后端、定时任务、作业管理事实
  - I 阶段：分析调度服务的扩展架构
  - V 阶段：抽样验证

- [ ] **T8.4**: jupyter-ai + jupyter-chat
  - R 阶段：采集 AI 扩展架构、LangChain/LiteLLM 集成、聊天界面事实
  - I 阶段：分析 AI 在 Notebook 中的集成模式、聊天 UI 组件设计
  - V 阶段：抽样验证（jupyter-ai 源码已在 external/libs/jupyter/ai/ 和 jupyter-ai/）

- [ ] **T8.5**: jupyter-docker-stacks + cookiecutter-docker-stacks
  - R 阶段：采集 Docker 镜像层级、镜像构建系统、cookiecutter 模板事实
  - I 阶段：分析 Docker Stacks 的镜像分层设计、版本管理策略
  - V 阶段：抽样验证

- [ ] **T8.6**: extension-cookiecutter + extension-template + extension-examples + plugin-playground
  - R 阶段：采集扩展开发模板、示例扩展、插件 playground 事实
  - I 阶段：分析 JupyterLab 扩展开发的学习路径设计
  - V 阶段：抽样验证

---

## Phase 9: 部署/运维/演示（Batch 9，约 8 个 bundle）

- [ ] **T9.1**: the-littlest-jupyterhub (TLJH)
  - R 阶段：采集 TLJH 单服务器部署、Docker-less 设计、用户环境管理事实
  - I 阶段：分析 TLJH 与 Z2JH（Zero to JupyterHub on K8s）的定位差异
  - V 阶段：抽样验证

- [ ] **T9.2**: jupyterlab-demo + jupyterlite-demo + try-jupyter + sphinx-demo
  - R 阶段：采集各 demo 部署配置、内容组织事实
  - I 阶段：分析 Jupyter 演示/try 站点的部署策略
  - V 阶段：抽样验证

---

## Phase 10: 治理/团队/元项目（Batch 10，约 7 个 bundle）

- [ ] **T10.1**: governance — Jupyter 治理文档
  - R 阶段：采集治理结构、决策流程、子项目治理事实
  - I 阶段：分析 Jupyter 开源治理模式
  - V 阶段：抽样验证

- [ ] **T10.2**: team-compass + frontends-team-compass
  - R 阶段：采集团队运作、会议记录、周会流程事实
  - I 阶段：分析 Jupyter 团队协作模式
  - V 阶段：抽样验证

- [ ] **T10.3**: jupyterlab-probot + pr-triage-board-bot
  - R 阶段：采集 Probot 配置、PR triage 机器人、自动化管理事实
  - I 阶段：分析 GitHub 自动化运维策略
  - V 阶段：抽样验证

- [ ] **T10.4**: surveys
  - R 阶段：采集用户调查结构、调查流程事实
  - I 阶段：分析社区反馈机制
  - V 阶段：抽样验证

---

## Phase 11: V 阶段全量验证 + C 阶段收尾（Batch 11）

- [ ] **T11.1**: 全量验证脚本执行
  - 编写/运行自动验证脚本：检查所有 67 个 bundle 的 facts.md/insights.md frontmatter 合规性
  - 检查 sources 路径存在性
  - 检查内部交叉链接有效性
  - 输出验证报告

- [ ] **T11.2**: 抽样对抗审查
  - 对核心层（协议层/格式层/服务层/应用层）14 个 bundle 执行深度 V 验证
  - 随机抽取 20% 的事实条目 Grep 源码核对
  - 修正发现的不准确事实和空洞洞察

- [ ] **T11.3**: log.md 更新
  - 为每个处理过的 bundle 在 log.md 中追加 R/I/V 阶段完成记录
  - 记录处理时间、验证结果、修正项

- [ ] **T11.4**: 进度文档最终化
  - 更新 progress.md 标记所有 bundle 完成
  - 输出最终统计：总 bundle 数、总 facts 条目数、总 insights 章节数
  - 记录处理过程中的问题和经验

- [ ] **T11.5**: 模式萃取（C 阶段）
  - 提炼 Jupyter 生态架构的跨 bundle 通用模式（如扩展机制模式、内核通信模式、插件注册模式）
  - 将通用模式沉淀到 `.agents/docs/retrospective/patterns/` 或对应知识库位置
  - 生成本次批量处理的复盘报告

---

## 任务依赖关系

```
Phase 0 (准备) → Phase 1 (协议/格式层) → Phase 2 (服务层) → Phase 3 (应用层)
                                                    ↓
                                              Phase 4 (JupyterLite)
                                              Phase 5 (前端 UI)
                                              Phase 6 (内核生态)
                                              Phase 7 (工具链)
                                              Phase 8 (扩展项目)
                                              Phase 9 (部署/运维)
                                              Phase 10 (治理/团队)
                                                    ↓
                                              Phase 11 (全量验证+收尾)
```

Phase 4-10 内部可以按依赖关系适度并行，但建议按顺序以保持上下文连贯性。

## 质量门（Quality Gates）

- **QG0**: Phase 0 完成后，确认所有源码已克隆/更新，进度文档就绪
- **QG1**: 每批完成后，该批所有 bundle 均有 facts.md + insights.md，且抽样验证通过率 ≥95%
- **QG2**: Phase 11 完成后，67 个 bundle 全部达标，无 P0 错误，交叉链接有效
- **QG3**: 对抗审查通过，核心 bundle 洞察有深度，事实可 Grep 验证
