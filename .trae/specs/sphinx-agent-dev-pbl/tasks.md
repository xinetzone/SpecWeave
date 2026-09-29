# 用 Sphinx 实现 AI 智能体开发 — 实施任务队列（tasks.md）

> methodologies applied: TRAE-spec-mode（Plan/Implement）→ seven-concepts（A 原子化 拆分任务）
> 说明：以下任务是**学生在 PBL 中按阶段执行的原子化工作项**；状态为 `pending` 表示设计态（尚未由学生执行）。每条任务映射 spec.md 的验收标准（AC），并含任务级测试要求（TR，类型仅 `rule`/`rubric`）。

---

## Task 0: 热身 — 30 分钟零代码文档站成功体验
- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - **【设计意图·源自 V 攻击 A-1】** 初学者的第一次失败点集中在 Task1 的环境搭建（venv/依赖/初始化全是黑箱报错）。本任务在接触任何命令行之前，先让学生**手写一篇 MyST Markdown 文档并看到浏览器里的成果**，建立"我能做出东西"的正反馈，再上难度。
  - **【零代码约束】** 全程不写一行 Python、不碰 venv、不碰 pip、不碰 Git。只用两样东西：文本编辑器 + 一条构建命令（或直接用在线预览替代）。
  - **操作路径（推荐：沙盒一键方案，零安装）**：
    - 教师预先在机房/共享盘放好一个**已初始化的最小 Sphinx 项目模板**（含 `conf.py`、`index.md`、已装好依赖的环境），学生直接复制，跳过安装。
    - 学生只做一件事：编辑 `docs/index.md`，用 MyST Markdown 写一页介绍自己（含一个标题、一段正文、一个列表、一段行内代码）。
    - 教师演示一条命令完成构建：`sphinx-build -b html docs docs/_build/html`，学生亲眼看到自己的文字变成网页。
  - **【降级方案·无环境时】** 若机房连 Sphinx 都无法预装，改用"纯 Markdown → 任一在线 Markdown 预览器"完成同样的"写作即成果"体验，仅演示一次 Sphinx 构建效果（教师机投屏）。
  - **【必须有正反馈】** 结束时每人产出 1 个能在浏览器打开的 HTML 页面，并截图留存。
  - **【与 Task1 的边界】** 本任务**不追求**理解 conf.py、不要求会安装、不要求 Git 提交——这些全部留给 Task1。若学生在本任务就开始纠结配置文件，说明教师过度教学，应打断。
- **Acceptance Criteria Addressed**: AC-1（预备性达成，非正式验收）, AC-3
- **Test Requirements**:
  - `rule` TR-0.1: 学生在 30 分钟内产出一个可在浏览器打开的 HTML 页面（自写内容 ≥100 字，含标题+列表+行内代码）；Evidence: 页面截图 + 源 `.md` 文件。
  - `rule` TR-0.2: 确认学生**未**使用命令行之外的安装操作（venv/pip），即零配置门槛；Evidence: 教师观察记录。
  - `rubric` TR-0.3: 热身任务的"成功体验"达成度（学生是否能说出"原来写文档就是写文字，不是搞环境"）；scale 1–5；anchors 1=仍感困惑,3=勉强跑通,5=明确感受到写作即成果；threshold ≥ 4；Evidence: 课后一句话反馈（问卷或口头）。
- **Notes**: 本任务是 **V 攻击 A-1 的 advisory 落地项**，不纳入正式评分权重（避免加分主义），只作为能力铺垫。教师须严守"不教配置"的纪律——此任务的唯一 KPI 是**正反馈**，不是知识量。

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
  - **【部署平台三档·经 DQ-2 决策，见 `decisions.md`】** 按机房条件选一档，三档共用同一份 `docs.yml` 主体：
    - **① 默认（GitHub Pages·学生个人账号）**：添加 `.github/workflows/docs.yml`，监听 push 到 main，安装依赖并执行 `sphinx-build`，用 `actions/upload-pages-artifact` + `deploy-pages` 部署。**用学生本人账号**——课程结束后仓库与站点仍归学生所有，且零审批。
    - **② 离线降级（内网 Git 服务）**：内网 Gitea/GitLab（或 `git init --bare` + `git daemon`）+ 自托管 runner，同一份 `docs.yml` 仅替换部署 action。**不使用"自建 Read the Docs"**——其运维成本对教师不可承受。
    - **③ 托管替代（Read the Docs·学生个人账号）**：关联同一仓库自动构建。仅当学生不想管 CI 细节时启用；代价是失去编写 `docs.yml` 的教具，TR-3.1 改为验证 RTD 构建记录。
  - **【一致性硬约束·经 V 审查修正 I-2】** **三档均不豁免**：CI 中除构建文档外，须额外执行一次 `sphinx-build -W --keep-going`（把警告视为错误）——确保"文档描述的 API"与"代码真实 API"不漂移。文档—代码一致性即项目的硬验收条件。
  - 验证部署 URL 可公开访问。
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `rule` TR-3.1: 对应档位的构建流水线成功，部署 URL 返回 200；Evidence: CI/RTD 运行记录 + curl 结果。
  - `rule` TR-3.2: 部署产物中不含任何明文 API Key；Evidence: 页面源码搜索。

## Task 4: 智能体最小循环实现
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 设计最小 Agent Loop：`messages = [用户输入]` → 调 LLM → 若返回 tool_call 则执行工具并把结果追加进 messages → 循环至文本回复。
  - **【SDK 统一·经 DQ-1 决策，见 `decisions.md`】** 统一使用 `openai` Python SDK，**不做 provider 抽象层**。厂商切换成本被压到一个环境变量——各主流厂商（混元/DeepSeek/通义）及本地 ollama 均已提供 OpenAI 兼容端点，"多厂商差异"已由上游抹平，自研中间层是净增排错负担的预防性抽象。
    ```bash
    # .env —— 同一份代码，只改这三行即可换厂商
    LLM_API_KEY=your-key
    LLM_BASE_URL=https://api.openai.com/v1      # 或兼容端点
    LLM_MODEL=gpt-4o-mini                        # 或 hunyuan / deepseek-chat ...

    # 本地 ollama（无需真实 Key）
    LLM_API_KEY=ollama
    LLM_BASE_URL=http://localhost:11434/v1
    LLM_MODEL=qwen2.5:7b
    ```
  - 密钥从 `.env` 经 `python-dotenv` 读取，提供 `.env.example` 模板。**客户端须延迟初始化**（在 `get_client()` 内首次调用时创建），使"未配 `.env` 也能先写代码、先跑测试"，且 import 阶段不抛 `OpenAIError`。
  - 入口 `agent.py` 支持命令行交互。骨架模板见 `templates/agent.py`（三区划分：预填样板／留空考点／引导提示）。
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-4.1: 运行 `python agent.py` 输入测试指令，返回合理文本且无异常；Evidence: 运行日志。
  - `rule` TR-4.2: 未配置 `.env` 时 `import agent` 不抛异常，仅在实际调用时给出含排查步骤的 `ValueError`；Evidence: 导入测试输出。

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

## Task 6: 元文档闭环 — agent 生成文档草稿【三档制】
- **Status**: `pending`
- **Priority**: high（档 A 必做）／ low（档 B 选做）
- **Depends On**: Task 5
- **性质说明（经 DQ-3 决策，见 `decisions.md`）**：**原"必做 vs 选做"曾被表述为布尔开关，现修正为三档**——因为该问题把"教学价值"与"Token 配额"两个独立维度压成了单一开关，且其承载的 **AC-4 是 rubric ≥4 的硬门槛**，选做化会使 AC-4 结构性不可达。
- **Description**:
  - **核心认知目标**：让学生体会到"**AI 看不到我代码背后的设计意图**"。触发条件是"看到 AI 误解我的代码"，而**不要求代码真的被 AI 读过**——这是三档并存可行的根本原因。
  - **【档 A·教学化形态 — 必做，零 Token 成本】** 教师**预置**一份草稿样例（其中刻意含 3 处典型误解：类型注解误读、设计意图缺失、编造不存在的异常类），学生以其为对象完成差异分析。学生仍可自行实现 `draft_doc()` 工具以理解其原理，只是**不真实调用 API 产出草稿**。
  - **【档 B·全自动形态 — 默认选做，加分】** 学生真实调用 LLM 生成草稿：实现"文档生成"工具/模式，让 agent 读取自身代码或功能说明，输出 MyST Markdown 草稿写入 `docs/drafts/`。
  - **【差异记录·经 V 审查修正 A-2/I-3 — 三档共用同一判定口径】** 学生须记录"AI 草稿 vs 我的最终版"的差异清单（`docs/drafts/diff-notes.md`），说明哪些地方 AI 写错了、为什么错、我如何修正。**AI 草稿质量不佳属于正常预期**，不得因草稿可用就跳过人工审校。
  - **【档 C·降级通道 — 保 AC-6 可达】** 配额耗尽或无外网时，改用 **Task2 已产出的 `api-draft.md`** 与最终代码做差异分析（"我当初设想" vs "我实际实现"）。仅 AC-4 折半计分，**AC-6 完整可达**。
  - **【诚实性红线·三档共同适用】** 使用档 A 或档 C 者，**必须在 `diff-notes.md` 中如实标注草稿来源**（"来自教师预置样例"／"来自我自己的 API 草图"）。**谎报为"我调用 AI 生成的"属于学术诚信问题，本项直接判 0。** 红线的作用是让降级没有动机伪装成满配——降级本身完全正当，伪装才不正当。
  - 学生人工审校后并入正式文档，体现"人机协作写文档"。
- **Acceptance Criteria Addressed**: AC-4（档 A/B 完整；档 C 折半）, AC-6
- **Test Requirements**:
  - `rubric` TR-6.1: 跨学科融合深度（元文档使三视角咬合）；scale 1–5；anchors 1=孤立,3=拼贴,5=闭环咬合；threshold ≥ 4（档 C 折半计分）；Evidence: draft 文件 + 学生反思。
  - `rule` TR-6.2: `diff-notes.md` 存在且含 ≥3 条具体差异（问题 + 原因 + 修正）；Evidence: 文件内容。
  - `rule` TR-6.3: `diff-notes.md` 首部如实声明草稿来源档位；Evidence: 文件首行声明 + 与教师记录比对。

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
Task0(热身·零代码·30min)
   │  ← 建立正反馈，切断首次失败点
   ↓
Task1(环境) ──┬──> Task2(文档先行+术语表) ──> Task3(CI部署+一致性校验·三档平台)
              └──> Task4(最小循环·openai SDK统一) ──> Task5(工具+autodoc) ──> Task6(元文档·三档制)
                                                                                       │
                                          Task2,Task5,(Task6) ──> Task7(展示答辩+反思)
```

> A（原子化）原则：每个 Task 单一职责、可独立验证、有明确验收。
>
> **顺序约束（经 V 对抗审查修正）**：
> - **Task0 必须先于 Task1**（先建立正反馈，再上环境难度；对应 V 攻击 A-1）
> - Task2 必须**先于** Task4/Task5 完成（文档先行，I-1）
> - Task2 必须**手写**，Task6 才引入 AI 协作（先手写后 AI，I-3）
> - Task6 的差异记录（TR-6.2）是 AC-6 过程证据的一部分（I-4）
>
> **决策落定（经 DQ-1~DQ-3，见 [`decisions.md`](decisions.md)）**：
> - Task4 统一 `openai` SDK + `base_url` 参数化，**不自研 provider 抽象层**（DQ-1）
> - Task3 部署平台三档并行，**默认 GitHub Pages 学生个人账号**（DQ-2）
> - **Task6 档 A（教学化形态）为必做，档 B（全自动）选做，档 C 为降级通道**——因其承载 AC-4 硬门槛，不可整体选做化（DQ-3）
>
> **任务编号说明**：Task0 为编号外插入的热身任务（源自 V 攻击 A-1 的 advisory），**不纳入正式评分权重**，仅作能力铺垫；其验收以"正反馈达成"为准（TR-0.3），而非知识掌握度。Task6 则**相反**——其档 A 承载 AC-4 硬门槛，**必须纳入正式评分权重**。

---

## Teacher Track（非学生任务，教师侧落地包）

> ⚠️ 以下**不是**学生的任务，因此不进入 `Task0–Task7` 编号与评分权重；
> 它们是 NFR-1"教师可立即落地"的交付载体，供**开课教师**使用。
> 当教学团队首次承接本方案时，应把 T-A~T-D 视为一次性的"备课准备"。

| 编号 | 交付物 | 对应教师动作 | 文件 |
|---|---|---|---|
| **T-A** | 课时编排 | 决定用哪套课时方案（标准 12 / 紧凑 8 / 集训 4–5 天），并把 8 个学生任务映射到节次 | [`teacher/TEACHER-GUIDE.md`](teacher/TEACHER-GUIDE.md) §二 |
| **T-B** | 评分表 | 打印、逐格记录、Task7 汇总 | [`teacher/SCORING-SHEET.md`](teacher/SCORING-SHEET.md) |
| **T-C** | 机房准备 | 课前 30 分钟按清单核验环境（软件版本 / 脚手架 / 部署平台 / 素材） | [`teacher/SETUP-CHECKLIST.md`](teacher/SETUP-CHECKLIST.md) |
| **T-D** | 课堂应答 | 学生质疑与技术故障的即时应答 | [`teacher/FAQ.md`](teacher/FAQ.md) |
| **T-E** | 一致性复核 | **每次修改本方案后**，跑一遍审计脚本，确认派生数字/命令/文件引用未漂移 | [`scripts/audit_consistency.py`](scripts/audit_consistency.py) |

> **验收（教师侧）**：一位未参与本方案设计的教师，在**仅有 4 份文件**的情况下，
> 能在开课前完成环境核验、并按课时方案上完第一节——无需任何额外检索。
> 该验收由 `review.md` R6 记录（评分表算术自检 + 12 处引用可达性全部通过）。
>
> **T-E 的由来（R8 完整性审计）**：R6 的验收只覆盖了"教师包内部"的引用可达性，
> 未能发现跨文档的命令不一致——`spec.md` AC-1 里的构建命令本身就是错的，
> 手册忠实抄写后同样错误（详见 `review.md` §九 A-1/A-5）。
> 因此 T-E 是 R8 之后新增的**持续性**动作：不是"开课前做一次"，而是"每次改动后都做"。
> 运行方式：`python scripts/audit_consistency.py --root .`（退出码 0 = 通过）。
