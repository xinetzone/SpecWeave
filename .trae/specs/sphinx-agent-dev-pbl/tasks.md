# 用 Sphinx 实现 AI 智能体开发 — 实施任务队列（tasks.md）

> methodologies applied: TRAE-spec-mode（Plan/Implement）→ seven-concepts（A 原子化 拆分任务）
> 说明：以下任务是**学生在 PBL 中按阶段执行的原子化工作项**；状态为 `pending` 表示设计态（尚未由学生执行）。每条任务映射 spec.md 的验收标准（AC），并含任务级测试要求（TR，类型仅 `rule`/`rubric`）。

---

## Task 1: 环境搭建与 Sphinx 初始化
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建项目目录并初始化 Python 虚拟环境：`python -m venv .venv && source .venv/bin/activate`（Windows: `.venv\Scripts\activate`）。
  - 安装依赖：`pip install sphinx myst-parser sphinx-design sphinx-copybutton python-dotenv openai`。
  - 运行 `sphinx-quickstart docs`（选"分离源与构建目录"、项目名/作者按需填）。
  - **非交互式一键初始化（推荐，规避交互式提问卡壳）**：
    ```bash
    sphinx-quickstart docs --no-sep -q -p "AI Agent Docs" -a "学生姓名" \
      -v 1.0 --language zh_CN --ext-autodoc --ext-viewcode --makefile --batchfile
    ```
    （`--no-sep` 源与构建分离；`-q` 静默；`--language zh_CN` 中文界面。若 Sphinx < 7.0，`--no-sep` 需改为手动选择。）
  - 在 `docs/conf.py` 启用扩展与主题：`extensions = ["myst_parser", "sphinx_design", "sphinx_copybutton", "sphinx.ext.autodoc"]`；`html_theme = "furo"`（或 `sphinx_book_theme`）。
  - 创建 `.gitignore` 写入 `.venv/`、`_build/`、`__pycache__/`、`.env`。
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `rule` TR-1.1: 执行 `sphinx-build -b html docs docs/_build/html` 退出码为 0 且生成 `docs/_build/html/index.html`；Evidence: 终端输出 + 文件存在。
  - `rule` TR-1.2: `.gitignore` 含 `.env` 与 `.venv/`；Evidence: 文件内容。
- **Notes**: 准备 `requirements.txt`（`pip freeze > requirements.txt`）便于复现。

## Task 2: 文档工程化 — 文档先行 + 内容编写与站点构建
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - **【文档先行·经 V 审查修正 I-1】** 在写任何 Agent 实现代码之前，先用 MyST Markdown 写出设想中的 API 与用例：`api-draft.md` 描述"我打算提供哪些函数、参数是什么、怎么调用"。此文档是**理解的检验**，不是实现的事后记录。
  - 用 MyST Markdown（`.md`）编写内容页：`index.md`（项目简介+toctree）、`usage.md`（使用指南）、`architecture.md`（Agent 设计）、`glossary.md`（术语表）。
  - **【术语表·经 V 审查修正 A-4】** `glossary.md` 须用 Sphinx `glossary` 指令定义：`reST`、`MyST`、`Doc-as-Code`、`autodoc`、`Agent Loop`、`tool_call`、`venv`。跨学科背景学生须能读懂。
  - 在 `conf.py` 设 `myst_enable_extensions = ["colon_fence", "deflist"]`；`source_suffix = {".rst": "restructuredtext", ".md": "markdown"}`。
  - 构建并本地预览 `make html`（在 docs 目录），核对导航、代码高亮、copybutton 生效。
- **Acceptance Criteria Addressed**: AC-1, AC-3
- **Test Requirements**:
  - `rule` TR-2.1: `make html` 无报错，`index.html` 可打开；Evidence: 构建输出。
  - `rule` TR-2.2: `glossary.md` 含 ≥7 个术语条目且能被构建渲染；Evidence: 站点 glossary 页截图。
  - `rubric` TR-2.3: 文档工程质量（结构清晰/导航完整/含使用指南）；scale 1–5；anchors 1=仅空壳,3=有页面但缺指南,5=结构完整含示例；threshold ≥ 4；Evidence: 本地站点截图。
  - `rubric` TR-2.4: 文档先行的落实度（`api-draft.md` 是否先于代码存在、后续实现是否与之对照修正）；scale 1–5；anchors 1=事后补写,3=有草稿但未对照,5=草稿明确指导了实现并记录偏差；threshold ≥ 4；Evidence: `api-draft.md` + Git 提交时序。
- **Notes**: **必须手写完成本任务，禁止使用 AI 生成内容**——经 V 对抗审查（A-8/I-3），能力建构期须先建立基础表达能力，AI 协作留到 Task 6。

## Task 3: 文档即代码 — Git + CI 自动部署
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - 初始化 Git 仓库，提交源码（不含 `.env`/`.venv`/`_build`）。
  - 添加 `.github/workflows/docs.yml`：监听 push 到 main，安装依赖并执行 `sphinx-build`，用 `actions/upload-pages-artifact` + `deploy-pages` 部署到 GitHub Pages（或接 Read the Docs 拉取仓库）。
  - **【一致性硬约束·经 V 审查修正 I-2】** CI 中除构建文档外，须额外执行一次 `sphinx-build -W`（把警告视为错误）与 `sphinx.ext.autodoc` 导入校验——确保"文档描述的 API"与"代码真实 API"不漂移。文档—代码一致性即项目的硬验收条件。
  - 验证部署 URL 可公开访问。
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `rule` TR-3.1: push 后 CI 绿，部署 URL 返回 200；Evidence: Actions 运行记录 + curl 结果。
  - `rule` TR-3.2: 部署产物中不含任何明文 API Key；Evidence: 页面源码搜索。

## Task 4: 智能体最小循环实现
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 设计最小 Agent Loop：`messages = [用户输入]` → 调 LLM → 若返回 tool_call 则执行工具并把结果追加进 messages → 循环至文本回复。
  - 用 `openai` 兼容 SDK 接入（示例用混元/OpenAI；本地可用 ollama）。密钥从 `.env` 经 `python-dotenv` 读取，提供 `.env.example` 模板。
  - 入口 `agent.py` 支持命令行交互。
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-4.1: 运行 `python agent.py` 输入测试指令，返回合理文本且无异常；Evidence: 运行日志。

## Task 5: 工具调用 + autodoc 文档自动抽取
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 实现 ≥1 个工具（如 `get_time()`、`calculator(expr)`），用函数 + docstring 描述；在 LLM 调用时传入 tools schema。
  - 在 `docs/conf.py` 确保 `autodoc` 已启用；新建 `api.md` 用 ````{eval-rst} .. automodule:: agent .. members:: ```` 把代码自动抽取进文档。
  - 重建文档站，核对 API 页显示函数签名与 docstring。
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-5.1: 给定"现在几点"类问题，agent 经工具调用返回正确结果；Evidence: 运行日志。
  - `rule` TR-5.2: 文档站 API 页含 agent 模块函数签名/docstring；Evidence: 站点截图。

## Task 6: 元文档闭环（进阶）— agent 生成文档草稿
- **Status**: `pending`
- **Priority**: low
- **Depends On**: Task 5
- **Description**:
  - 设计一个"文档生成"工具/模式：让 agent 读取自身代码或功能说明，输出一段 MyST Markdown 草稿（如某个功能的用法说明），写入 `docs/drafts/`。
  - **【差异记录·经 V 审查修正 A-2/I-3】** 学生须记录"AI 草稿 vs 我的最终版"的差异清单（`docs/drafts/diff-notes.md`），说明哪些地方 AI 写错了、为什么错、我如何修正。**AI 草稿质量不佳属于正常预期**，不得因草稿可用就跳过人工审校。
  - 学生人工审校后并入正式文档，体现"人机协作写文档"。
  - **【成本控制·经 V 审查修正 A-5】** 若 API 配额有限，本任务可改为"全班共演一次 + 各组基于同一草稿做差异分析"。
- **Acceptance Criteria Addressed**: AC-4, AC-6
- **Test Requirements**:
  - `rubric` TR-6.1: 跨学科融合深度（元文档使三视角咬合）；scale 1–5；anchors 1=孤立,3=拼贴,5=闭环咬合；threshold ≥ 4；Evidence: draft 文件 + 学生反思。
  - `rule` TR-6.2: `diff-notes.md` 存在且含 ≥3 条具体差异（AI 草稿的问题 + 修正方式）；Evidence: 文件内容。

## Task 7: 展示与反思 + 同伴互评
- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 2, Task 5, (Task 6)
- **Description**:
  - 路演：演示可运行智能体 + 展示已部署文档站 URL。
  - **【现场答辩·经 V 审查修正 I-4/A-6】** 教师随机指定代码库中任一函数，学生须现场口头解释其输入、输出、实现逻辑与为何如此设计。此项与 Git 提交历史共同构成"过程证据"，防止 AI 代写导致的评价失真。
  - 提交反思报告（为何文档重要、我在哪一步厘清了模糊模块、AI 草稿与我的最终版差异）。
  - 同伴互评：按量规（AC-3/AC-4/AC-6）交叉评分。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-6
- **Test Requirements**:
  - `rubric` TR-7.1: 反思报告质量（真实洞察 vs 套话）；scale 1–5；anchors 1=套话,3=描述过程,5=真实盲点洞察；threshold ≥ 4；Evidence: 反思报告 + 差异清单。
  - `rule` TR-7.2: Git 提交历史含 ≥5 次原子提交（非单次大提交）；Evidence: `git log --oneline` 输出。
  - `rule` TR-7.3: 现场口头解释任一指定函数，学生能说清其输入/输出/逻辑；Evidence: 教师答辩记录表。
  - `rubric` TR-7.4: 展示完成度（demo 流畅 + 文档站可访问）；scale 1–5；threshold ≥ 4；Evidence: 路演记录 + URL。

---

## 任务依赖图（原子化拆分依据）

```text
Task1(环境) ──┬──> Task2(文档先行+术语表) ──> Task3(CI部署+一致性校验)
              └──> Task4(最小循环) ──> Task5(工具+autodoc) ──> Task6(元文档+差异记录·进阶)
                                                                         │
                                    Task2,Task5,(Task6) ──> Task7(展示答辩+反思)
```

> A（原子化）原则：每个 Task 单一职责、可独立验证、有明确验收；Task6 为进阶选做不影响主干闭环。
>
> **顺序约束（经 V 对抗审查修正）**：
> - Task2 必须**先于** Task4/Task5 完成（文档先行，I-1）
> - Task2 必须**手写**，Task6 才引入 AI 协作（先手写后 AI，I-3）
> - Task6 的差异记录（TR-6.2）是 AC-6 过程证据的一部分（I-4）
