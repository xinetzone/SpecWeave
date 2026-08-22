# Jupyter 分组 OKF Wiki 全量处理 - 进度追踪

> 创建时间：2026-08-22
> 总计：68 个 bundle

## 源码映射表

| Bundle 名称 | 本地源码目录 | 状态 |
|---|---|---|
| accessibility (无bundle) | external/libs/jupyter/accessibility/ | 额外仓库 |
| binderhub | external/libs/jupyter/binderhub/ | 待补全 |
| cockle | external/libs/jupyter/cockle/ | ✅ 已完成 |
| cookiecutter-docker-stacks | external/libs/jupyter/cookiecutter-docker-stacks/ | 待补全 |
| demo → jupyterlite-demo | external/libs/jupyter/demo/ | ✅ 已完成 |
| docker-stacks → jupyter-docker-stacks | external/libs/jupyter/docker-stacks/ | 待补全 |
| echo-kernel | external/libs/jupyter/echo-kernel/ | 待补全 |
| enterprise-gateway | external/libs/jupyter/enterprise_gateway/ | 待补全 |
| extension-cookiecutter | external/libs/jupyter/extension-cookiecutter/ | 待补全 |
| extension-examples | external/libs/jupyter/extension-examples/ | 待补全 |
| extension-template | external/libs/jupyter/extension-template/ | 待补全 |
| fps | external/libs/jupyter/fps/ | ✅ 已完成 |
| frontends-team-compass | external/libs/jupyter/frontends-team-compass/ | 待补全 |
| governance | external/libs/jupyter/governance/ | 待补全 |
| ipython | external/libs/jupyter/ipython/ | ✅ 已完成(无index) |
| javascript-kernel | external/libs/jupyter/javascript-kernel/ | ✅ 已完成 |
| jupyter | external/libs/jupyter/jupyter/ | 待补全 |
| jupyter-ai | external/libs/jupyter/jupyter-ai/ | 待补全 |
| jupyter-chat | external/libs/jupyter/jupyter-chat/ | 待补全 |
| jupyter-client | external/libs/jupyter/jupyter_client/ | 待补全 |
| jupyter-collaboration | external/libs/jupyter/jupyter-collaboration/ | 待补全 |
| jupyter-core | external/libs/jupyter/jupyter_core/ | 待补全 |
| jupyter-docker-stacks | external/libs/jupyter/docker-stacks/ | 待补全 |
| jupyter-notebook | external/libs/jupyter/notebook/ | 待补全 |
| jupyter-renderers | external/libs/jupyter/jupyter-renderers/ | 待补全 |
| jupyter-resource-usage | external/libs/jupyter/jupyter-resource-usage/ | 待补全 |
| jupyter-scheduler | external/libs/jupyter/jupyter-scheduler/ | ✅ 已完成 |
| jupyter-server-terminals | external/libs/jupyter/jupyter_server_terminals/ | 待补全 |
| jupyter_releaser | external/libs/jupyter/jupyter_releaser/ | ✅ 已完成 |
| jupyter_server | external/libs/jupyter/jupyter_server/ | 待补全 |
| jupyter_server_fileid | external/libs/jupyter/jupyter_server_fileid/ | 待补全 |
| jupyterhub | external/libs/jupyter/jupyterhub/ | 待补全 |
| jupyterlab | external/libs/jupyter/jupyterlab/ | 待补全 |
| jupyterlab-demo | external/libs/jupyter/jupyterlab-demo/ | 待补全 |
| jupyterlab-desktop | external/libs/jupyter/jupyterlab-desktop/ | 待补全 |
| jupyterlab-git | external/libs/jupyter/jupyterlab-git/ | 待补全 |
| jupyterlab-github | external/libs/jupyter/jupyterlab-github/ | 待补全 |
| jupyterlab-latex | external/libs/jupyter/jupyterlab-latex/ | 待补全 |
| jupyterlab-probot | external/libs/jupyter/jupyterlab-probot/ | 待补全 |
| jupyterlab-pygments | external/libs/jupyter/jupyterlab_pygments/ | 待补全 |
| jupyterlab-translate | external/libs/jupyter/jupyterlab-translate/ | 待补全 |
| jupyterlab-webrtc-docprovider | external/libs/jupyter/jupyterlab-webrtc-docprovider/ | 待补全 |
| jupyterlab_server | external/libs/jupyter/jupyterlab_server/ | ⚠️ 缺insights |
| jupyterlite | external/libs/jupyter/jupyterlite/ | 待补全 |
| ai → jupyterlite-ai | external/libs/jupyter/ai/ | 待补全 |
| jupyterlite-demo | external/libs/jupyter/demo/ | ✅ 已完成 |
| jupyterlite-lsp | external/libs/jupyter/jupyterlite-lsp/ | 待补全 |
| jupyterlite-sphinx | external/libs/jupyter/jupyterlite-sphinx/ | 待补全 |
| jupyverse | external/libs/jupyter/jupyverse/ | 待补全 |
| language-packs | external/libs/jupyter/language-packs/ | 待补全 |
| litegitpuller | external/libs/jupyter/litegitpuller/ | ✅ 已完成 |
| lumino | external/libs/jupyter/lumino/ | 待补全 |
| nbconvert | external/libs/jupyter/nbconvert/ | 待补全 |
| nbformat | external/libs/jupyter/nbformat/ | 待补全 |
| nbviewer | external/libs/jupyter/nbviewer/ | 待补全 |
| nbdime (无bundle) | external/libs/jupyter/nbdime/ | 额外仓库 |
| nbgrader (无bundle) | external/libs/jupyter/nbgrader/ | 额外仓库 |
| p5-kernel | external/libs/jupyter/p5-kernel/ | ✅ 已完成 |
| papyri | external/libs/jupyter/papyri/ | 待补全 |
| plugin-playground | external/libs/jupyter/plugin-playground/ | ✅ 已完成 |
| pr-triage-board-bot | external/libs/jupyter/pr-triage-board-bot/ | 待补全 |
| pyodide-kernel | external/libs/jupyter/pyodide-kernel/ | ✅ 已完成 |
| pytest-jupyter | external/libs/jupyter/pytest-jupyter/ | 待补全 |
| repo2jupyterlite | external/libs/jupyter/repo2jupyterlite/ | ✅ 已完成 |
| sphinx-demo | external/libs/jupyter/sphinx-demo/ | 待补全 |
| surveys | external/libs/jupyter/surveys/ | 待补全 |
| team-compass | external/libs/jupyter/team-compass/ | 待补全 |
| terminal | external/libs/jupyter/terminal/ | ✅ 已完成 |
| the-littlest-jupyterhub | external/libs/jupyter/the-littlest-jupyterhub/ | ✅ 已完成 |
| try-jupyter | external/libs/jupyter/try-jupyter/ | 待补全 |
| ui-profiler | external/libs/jupyter/ui-profiler/ | 待补全 |
| xeus | external/libs/jupyter/xeus/ | ✅ 已完成 |
| xeus-lite-demo | external/libs/jupyter/xeus-lite-demo/ | ✅ 已完成(模板) |

## 批次进度

### Phase 0: 准备阶段
- [x] T0.1 盘点源码本地状态
- [x] T0.2 克隆/更新缺失源码（ipython 已克隆）
- [x] T0.3 建立进度追踪文档
- [x] T0.4 全量 bundle 状态复查：16 done, 1 partial, 51 pending

### Phase 1: 协议层+格式层 (Batch 1)
- [ ] jupyter-core
- [ ] jupyter-client
- [ ] nbformat
- [ ] jupyter
- [ ] ipython (已有facts/insights，待V验证)

### Phase 2: 服务层核心 (Batch 2)
- [ ] jupyter_server
- [ ] jupyter_server_fileid
- [ ] jupyter-server-terminals
- [ ] enterprise-gateway
- [ ] jupyverse + fps(fps已完成)

### Phase 3: 应用层核心 (Batch 3)
- [ ] jupyterlab
- [ ] jupyterlab_server (已有facts，缺insights)
- [ ] jupyter-notebook
- [ ] jupyterhub
- [ ] binderhub

### Phase 4: JupyterLite (Batch 4)
- [ ] jupyterlite
- [ ] pyodide-kernel (已完成)
- [ ] jupyterlite-lsp
- [ ] jupyterlite-sphinx
- [ ] jupyterlite-ai (ai/)
- [ ] litegitpuller (已完成)
- [ ] repo2jupyterlite (已完成)
- [ ] xeus (已完成)
- [ ] xeus-lite-demo (已完成)

### Phase 5: 前端 UI (Batch 5)
- [ ] lumino
- [ ] jupyter-renderers
- [ ] ui-profiler
- [ ] jupyterlab-desktop
- [ ] terminal (已完成)
- [ ] cockle (已完成)

### Phase 6: 内核生态 (Batch 6)
- [ ] echo-kernel
- [ ] javascript-kernel (已完成)
- [ ] p5-kernel (已完成)
- [ ] jupyterlab-webrtc-docprovider
- [ ] jupyter-collaboration

### Phase 7: 工具链 (Batch 7)
- [ ] nbconvert
- [ ] nbviewer
- [ ] papyri
- [ ] jupyter_releaser (已完成)
- [ ] jupyterlab-translate
- [ ] language-packs
- [ ] pytest-jupyter
- [ ] jupyterlab-pygments

### Phase 8: 扩展项目 (Batch 8)
- [ ] jupyterlab-git
- [ ] jupyterlab-github
- [ ] jupyterlab-latex
- [ ] jupyter-resource-usage
- [ ] jupyter-scheduler (已完成)
- [ ] jupyter-ai
- [ ] jupyter-chat
- [ ] jupyter-docker-stacks (docker-stacks/)
- [ ] cookiecutter-docker-stacks
- [ ] extension-cookiecutter
- [ ] extension-template
- [ ] extension-examples
- [ ] plugin-playground (已完成)

### Phase 9: 部署/运维/演示 (Batch 9)
- [ ] the-littlest-jupyterhub (已完成)
- [ ] jupyterlab-demo
- [ ] jupyterlite-demo (已完成)
- [ ] try-jupyter
- [ ] sphinx-demo

### Phase 10: 治理/团队 (Batch 10)
- [ ] governance
- [ ] team-compass
- [ ] frontends-team-compass
- [ ] jupyterlab-probot
- [ ] pr-triage-board-bot
- [ ] surveys
- [ ] jupyter

### Phase 11: 全量验证+收尾
- [ ] 全量验证脚本
- [ ] 抽样对抗审查
- [ ] log.md 更新
- [ ] 进度最终化
- [ ] 模式萃取

## 统计

- 总 bundle 数：68
- 已有完整 facts+insights：16
- 部分完成（缺 insights）：1
- 待补全：51
- 源码就绪：68/68
