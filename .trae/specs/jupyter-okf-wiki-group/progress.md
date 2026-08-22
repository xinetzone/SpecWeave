# Jupyter 分组 OKF Wiki 全量处理 - 进度追踪

> 创建时间：2026-08-22
> 最终完成：2026-08-22
> 总计：68 个 bundle（源码映射表覆盖 68 个；含 4 个非任务范围 bundle：anywidget / sphinx-demo / jupyterlite-sphinx / jupyter-chat）
> 任务范围：65 个 bundle 全部完成（facts.md + insights.md + frontmatter 校验通过）

## 源码映射表

| Bundle 名称 | 本地源码目录 | 状态 |
|---|---|---|
| accessibility (无bundle) | external/libs/jupyter/accessibility/ | 额外仓库（未建 bundle） |
| binderhub | external/libs/jupyter/binderhub/ | ✅ 已完成 |
| cockle | external/libs/jupyter/cockle/ | ✅ 已完成 |
| cookiecutter-docker-stacks | external/libs/jupyter/cookiecutter-docker-stacks/ | ✅ 已完成 |
| demo → jupyterlite-demo | external/libs/jupyter/demo/ | ✅ 已完成 |
| docker-stacks → jupyter-docker-stacks | external/libs/jupyter/docker-stacks/ | ✅ 已完成 |
| echo-kernel | external/libs/jupyter/echo-kernel/ | ✅ 已完成 |
| enterprise-gateway | external/libs/jupyter/enterprise_gateway/ | ✅ 已完成 |
| extension-cookiecutter | external/libs/jupyter/extension-cookiecutter/ | ✅ 已完成 |
| extension-examples | external/libs/jupyter/extension-examples/ | ✅ 已完成 |
| extension-template | external/libs/jupyter/extension-template/ | ✅ 已完成 |
| fps | external/libs/jupyter/fps/ | ✅ 已完成 |
| frontends-team-compass | external/libs/jupyter/frontends-team-compass/ | ✅ 已完成 |
| governance | external/libs/jupyter/governance/ | ✅ 已完成 |
| ipython | external/libs/jupyter/ipython/ | ✅ 已完成 |
| javascript-kernel | external/libs/jupyter/javascript-kernel/ | ✅ 已完成 |
| jupyter | external/libs/jupyter/jupyter/ | ✅ 已完成 |
| jupyter-ai | external/libs/jupyter/jupyter-ai/ | ✅ 已完成 |
| jupyter-chat | external/libs/jupyter/jupyter-chat/ | ⛔ 非任务范围（已排除） |
| jupyter-client | external/libs/jupyter/jupyter_client/ | ✅ 已完成 |
| jupyter-collaboration | external/libs/jupyter/jupyter-collaboration/ | ✅ 已完成 |
| jupyter-core | external/libs/jupyter/jupyter_core/ | ✅ 已完成 |
| jupyter-docker-stacks | external/libs/jupyter/docker-stacks/ | ✅ 已完成 |
| jupyter-notebook | external/libs/jupyter/notebook/ | ✅ 已完成 |
| jupyter-renderers | external/libs/jupyter/jupyter-renderers/ | ✅ 已完成 |
| jupyter-resource-usage | external/libs/jupyter/jupyter-resource-usage/ | ✅ 已完成 |
| jupyter-scheduler | external/libs/jupyter/jupyter-scheduler/ | ✅ 已完成 |
| jupyter-server-terminals | external/libs/jupyter/jupyter_server_terminals/ | ✅ 已完成 |
| jupyter_releaser | external/libs/jupyter/jupyter_releaser/ | ✅ 已完成 |
| jupyter_server | external/libs/jupyter/jupyter_server/ | ✅ 已完成 |
| jupyter_server_fileid | external/libs/jupyter/jupyter_server_fileid/ | ✅ 已完成 |
| jupyterhub | external/libs/jupyter/jupyterhub/ | ✅ 已完成 |
| jupyterlab | external/libs/jupyter/jupyterlab/ | ✅ 已完成 |
| jupyterlab-demo | external/libs/jupyter/jupyterlab-demo/ | ✅ 已完成 |
| jupyterlab-desktop | external/libs/jupyter/jupyterlab-desktop/ | ✅ 已完成 |
| jupyterlab-git | external/libs/jupyter/jupyterlab-git/ | ✅ 已完成 |
| jupyterlab-github | external/libs/jupyter/jupyterlab-github/ | ✅ 已完成 |
| jupyterlab-latex | external/libs/jupyter/jupyterlab-latex/ | ✅ 已完成 |
| jupyterlab-probot | external/libs/jupyter/jupyterlab-probot/ | ✅ 已完成 |
| jupyterlab-pygments | external/libs/jupyter/jupyterlab_pygments/ | ✅ 已完成 |
| jupyterlab-translate | external/libs/jupyter/jupyterlab-translate/ | ✅ 已完成 |
| jupyterlab-webrtc-docprovider | external/libs/jupyter/jupyterlab-webrtc-docprovider/ | ✅ 已完成 |
| jupyterlab_server | external/libs/jupyter/jupyterlab_server/ | ✅ 已完成 |
| jupyterlite | external/libs/jupyter/jupyterlite/ | ✅ 已完成 |
| ai → jupyterlite-ai | external/libs/jupyter/ai/ | ✅ 已完成 |
| jupyterlite-demo | external/libs/jupyter/demo/ | ✅ 已完成 |
| jupyterlite-lsp | external/libs/jupyter/jupyterlite-lsp/ | ✅ 已完成 |
| jupyterlite-sphinx | external/libs/jupyter/jupyterlite-sphinx/ | ⛔ 非任务范围（已排除） |
| jupyverse | external/libs/jupyter/jupyverse/ | ✅ 已完成 |
| language-packs | external/libs/jupyter/language-packs/ | ✅ 已完成 |
| litegitpuller | external/libs/jupyter/litegitpuller/ | ✅ 已完成 |
| lumino | external/libs/jupyter/lumino/ | ✅ 已完成 |
| nbconvert | external/libs/jupyter/nbconvert/ | ✅ 已完成 |
| nbformat | external/libs/jupyter/nbformat/ | ✅ 已完成 |
| nbviewer | external/libs/jupyter/nbviewer/ | ✅ 已完成 |
| nbdime (无bundle) | external/libs/jupyter/nbdime/ | 额外仓库（未建 bundle） |
| nbgrader (无bundle) | external/libs/jupyter/nbgrader/ | 额外仓库（未建 bundle） |
| p5-kernel | external/libs/jupyter/p5-kernel/ | ✅ 已完成 |
| papyri | external/libs/jupyter/papyri/ | ✅ 已完成 |
| plugin-playground | external/libs/jupyter/plugin-playground/ | ✅ 已完成 |
| pr-triage-board-bot | external/libs/jupyter/pr-triage-board-bot/ | ✅ 已完成 |
| pyodide-kernel | external/libs/jupyter/pyodide-kernel/ | ✅ 已完成 |
| pytest-jupyter | external/libs/jupyter/pytest-jupyter/ | ✅ 已完成 |
| repo2jupyterlite | external/libs/jupyter/repo2jupyterlite/ | ✅ 已完成 |
| sphinx-demo | external/libs/jupyter/sphinx-demo/ | ⛔ 非任务范围（已排除） |
| surveys | external/libs/jupyter/surveys/ | ✅ 已完成 |
| team-compass | external/libs/jupyter/team-compass/ | ✅ 已完成 |
| terminal | external/libs/jupyter/terminal/ | ✅ 已完成 |
| the-littlest-jupyterhub | external/libs/jupyter/the-littlest-jupyterhub/ | ✅ 已完成 |
| try-jupyter | external/libs/jupyter/try-jupyter/ | ✅ 已完成 |
| ui-profiler | external/libs/jupyter/ui-profiler/ | ✅ 已完成 |
| xeus | external/libs/jupyter/xeus/ | ✅ 已完成 |
| xeus-lite-demo | external/libs/jupyter/xeus-lite-demo/ | ✅ 已完成（无源码仓库，sources 缺省可接受） |
| anywidget | external/libs/jupyter/anywidget/ | ⛔ 非任务范围（已排除） |

## 批次进度

### Phase 0: 准备阶段
- [x] T0.1 盘点源码本地状态
- [x] T0.2 克隆/更新缺失源码（ipython 已克隆）
- [x] T0.3 建立进度追踪文档
- [x] T0.4 全量 bundle 状态复查：16 done, 1 partial, 51 pending

### Phase 1: 协议层+格式层 (Batch 1)
- [x] jupyter-core
- [x] jupyter-client
- [x] nbformat
- [x] jupyter
- [x] ipython (已有facts/insights，V验证通过)

### Phase 2: 服务层核心 (Batch 2)
- [x] jupyter_server
- [x] jupyter_server_fileid
- [x] jupyter-server-terminals
- [x] enterprise-gateway
- [x] jupyverse + fps

### Phase 3: 应用层核心 (Batch 3)
- [x] jupyterlab
- [x] jupyterlab_server (facts+insights 均已补全)
- [x] jupyter-notebook
- [x] jupyterhub
- [x] binderhub

### Phase 4: JupyterLite (Batch 4)
- [x] jupyterlite
- [x] pyodide-kernel
- [x] jupyterlite-lsp
- [x] jupyterlite-sphinx (排除)
- [x] jupyterlite-ai (ai/)
- [x] litegitpuller
- [x] repo2jupyterlite
- [x] xeus
- [x] xeus-lite-demo

### Phase 5: 前端 UI (Batch 5)
- [x] lumino
- [x] jupyter-renderers
- [x] ui-profiler
- [x] jupyterlab-desktop
- [x] terminal
- [x] cockle

### Phase 6: 内核生态 (Batch 6)
- [x] echo-kernel
- [x] javascript-kernel
- [x] p5-kernel
- [x] jupyterlab-webrtc-docprovider
- [x] jupyter-collaboration

### Phase 7: 工具链 (Batch 7)
- [x] nbconvert
- [x] nbviewer
- [x] papyri
- [x] jupyter_releaser
- [x] jupyterlab-translate
- [x] language-packs
- [x] pytest-jupyter
- [x] jupyterlab-pygments

### Phase 8: 扩展项目 (Batch 8)
- [x] jupyterlab-git
- [x] jupyterlab-github
- [x] jupyterlab-latex
- [x] jupyter-resource-usage
- [x] jupyter-scheduler
- [x] jupyter-ai
- [x] jupyter-chat (排除)
- [x] jupyter-docker-stacks (docker-stacks/)
- [x] cookiecutter-docker-stacks
- [x] extension-cookiecutter
- [x] extension-template
- [x] extension-examples
- [x] plugin-playground

### Phase 9: 部署/运维/演示 (Batch 9)
- [x] the-littlest-jupyterhub
- [x] jupyterlab-demo
- [x] jupyterlite-demo
- [x] try-jupyter
- [x] sphinx-demo (排除)

### Phase 10: 治理/团队 (Batch 10)
- [x] governance
- [x] team-compass
- [x] frontends-team-compass
- [x] jupyterlab-probot
- [x] pr-triage-board-bot
- [x] surveys
- [x] jupyter

### Phase 11: 全量验证+收尾
- [x] T11.1 全量验证脚本（65/65 通过，0 错误，2 可接受告警）
- [x] T11.2 抽样对抗审查（核心层 14 bundle 深度 V 验证，7 条事实 Grep 源码核对一致）
- [x] T11.3 log.md 更新（30 追加 + 35 新建，共 65 个 bundle）
- [x] T11.4 进度文档最终化（本文件）
- [x] T11.5 模式萃取（C 阶段）

> **T11.5 收尾补充（2026-08-22）**：3 个 L1 模式已入库并更新两索引；复盘报告已登记至 `reports/competitive-analysis/retrospective-jupyter-okf-wiki-group-20260822/`；.temp 临时脚本（fix_jupyter_frontmatter.py / verify_jupyter_okf.py / summary_jupyter_okf.py / update_jupyter_logs.py）已清理删除。

## 统计（最终）

- 总 bundle 目录数：69
- 任务范围 bundle：65（已全部完成）
- 非任务范围（排除）：4（anywidget / sphinx-demo / jupyterlite-sphinx / jupyter-chat）
- 额外源码仓库（无 bundle）：3（accessibility / nbdime / nbgrader）
- 已完成 facts.md + insights.md：65 / 65
- facts 条目总数：505
- insights 章节总数：69
- frontmatter 校验：0 错误，2 可接受告警（xeus-lite-demo 缺 sources，因无本地源码仓库）
- 抽样对抗审查：7 条事实 Grep 源码核对全部一致，无虚构 API
- log.md 覆盖：65 / 65（30 个更新 + 35 个新建）

## 处理问题与经验（T11.4 记录）

### frontmatter 五类缺失（T11.1 发现）
批量生成的 facts.md/insights.md frontmatter 存在五类缺失：缺 `type`、缺 `okf_version`、缺 `title`、缺 `generated`、缺 `sources`。修复脚本按「正文 F- 行提取路径 ∪ 现有 sources → 规范化 → 拼正确前缀 → 存在性过滤」重建，全部修复。

### sources 前缀层级（5 级 `../`）
bundle 目录位于 `projects/awesome-okf-xs/bundles/jupyter/<bundle>/`，源码位于 `external/libs/jupyter/<src>/`，从 bundle 目录回退到 SpecWeave 根需要 5 级 `../`。此前错误前缀（层级不足或含 bundle 子目录）导致 sources 路径解析失败。

### 正则字符类陷阱
修复脚本中路径提取正则的字符类不能包含 `.`（如 `[A-Za-z0-9_/\-]+`），否则贪婪吞掉扩展名前的点（如 `app.py` 会被截成 `appp` 或吃掉扩展名）。这是批量处理中容易踩坑的隐蔽 bug。

### 源码目录命名差异
部分 bundle 名与源码目录名不一致（如 jupyter-docker-stacks → docker-stacks、jupyterlite-ai → ai、jupyterlab-pygments → jupyterlab_pygments、jupyter-server-terminals → jupyter_server_terminals），需要 bundle→源码目录映射表（48 个异常项）逐一映射，无法靠同名推断。

### 无源码仓库 bundle
xeus-lite-demo 无独立本地源码仓库，sources 字段无法指向真实文件（2 个可接受告警）。此类 bundle 建议在 log.md 标注「无源码仓库」豁免。
