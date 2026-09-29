# 用 Sphinx 实现 AI 智能体开发 — 跨学科 PBL 项目设计规范（spec.md）

>  methodologies applied: TRAE-spec-mode（Specify）→ seven-concepts（F 第一性原理 驱动设计）
> 自然语言：简体中文（与用户请求一致）
>
> 📎 配套文件：`tasks.md`（任务队列与验收标准）、`insight.md`（V 对抗审查与洞察）、`review.md`（独立审查与检查点）、**`retrospective.md`（里程碑复盘报告 — R1–R10 全周期事实/洞察/行动项，R11 新增）**、**`decisions.md`（决策记录 — 原 Open Questions 的落定依据）**、`handbook/`（学生操作手册）、`templates/`（Task4/5 代码模板）、`warmup-docs/`（Task0 脚手架）、**`starters/`（Task1/3 配置类文件实物 — 依赖清单 / .gitignore / CI 工作流，R10 补全）**、**`teacher/`（教师实施包 — 课时编排 / 可打印评分表 / 机房准备清单 / 课堂应答手册，NFR-1 的落地依据）**、**`patterns/`（可迁移模式 — 配置实物化）**、**`scripts/`（一致性审计脚本 — NFR-4 的可验证手段）**。

## 一、Overview

- **Summary**：设计一个面向中高等教育阶段的跨学科项目式学习（PBL）方案，让学生在真实工程流程中**同时掌握 AI 智能体开发（计算机科学）与文档工程化（文档工程），并通过"教会 AI 解释自己"达成元认知（教育学）**。
- **Purpose**：解决当前 AI/编程教学中"重代码、轻文档、缺反思"的断层——学生能跑通代码却说不清原理、写不出说明。本项目以 Sphinx 文档站点为强制交付物，使"可解释性"成为项目一等公民。
- **Target Users（最终学习者）**：高中高年级 / 大学低年级学生（建议 3–6 人小组）；本项目文档的读者为一线教师与课程设计者。

## 二、Goals（项目目标）

- G1 **知识目标**：学生能解释 Agent Loop（感知—思考—行动—观察）原理，能独立用 Sphinx 搭建可部署的文档站点，理解 reST/MyST Markdown、Doc-as-Code 与 CI 文档构建。
- G2 **能力目标**：学生能调用 LLM API 实现一个最小可运行智能体（含≥1 个工具调用），能用 Sphinx 把代码自动抽取进文档（autodoc），能用 Git + CI 发布文档站。
- G3 **素养目标（教育学）**：通过"让智能体生成自身文档草稿"的闭环任务，培养元认知与工程文档素养——把"写文档"从负担转化为"理解自己"的手段。

## 三、Non-Goals（非目标）

- 不深入讲授 LangGraph / CrewAI / Claude Agent SDK / AutoGen 等框架源码（仅作概念扫盲与选型对比，避免认知过载）。
- 不要求训练/微调模型，仅使用现成 LLM API。
- 不追求生产级多智能体编排或高并发部署。

## 四、Background & Context（背景与依据）

- **事实依据（R 复盘层输入）**：AI 编程助手普及后，"能调 API 跑通 demo"的门槛降低，但"能工程化、能解释、能协作"的能力缺口扩大；Sphinx 是 Python 生态事实标准的文档工具（Doc-as-Code 范式），与代码同源、可版本化、可 CI。
- **设计决策**：以"文档站"作为硬交付物倒逼工程规范；以"agent 生成文档草稿"作为高阶闭环，使三种学科视角（CS / 文档工程 / 教育学）真正咬合而非拼贴。

## 五、Methodology Note — 第一性原理（F）

> 本 PBL 的设计从第一性原理推导，而非经验拼凑：

1. **学习的本质 = 抽象 + 组合 + 可解释性**。会写代码只是"组合"，能写文档才是"抽象与可解释"的外化证据。
2. **智能体的最小不可约单元 = 一个循环**：输入 → LLM 推理 →（工具调用）→ 观察 → 输出。去掉任何一环都不是 Agent。
3. **文档不是代码的附属，而是认知的副产品**：当学生必须为 Sphinx 写清"这个智能体做什么、怎么用"，他被迫澄清自己其实没想清楚的模块——文档即调试。
4. **闭环设计（元文档）**：让 agent 反过来生成文档草稿，把"可解释性"从人类单向输出变为人机协作，是本项目区别于普通编程课的本质创新点。
5. **文档的定位（经 V 对抗审查修正）**：文档不是"理解的来源"，而是"理解的**检验**"。原表述隐含因果倒置风险（先想清再记录，文档沦为事后粉饰）。修正为**文档先行**——先写出设想的 API 与用法，再实现，实现与文档的偏差即为理解盲点的显影。
6. **AI 协作的顺序约束（经 V 对抗审查修正）**：必须"先手写、后 AI 协作"。在能力建构期，工具提效会抑制能力形成，顺序颠倒导致基础表达能力发育不良。
7. **可评估性是前置约束（经 V 对抗审查修正）**：引入 AI 的教学设计若无"过程证据"（Git 提交历史、现场答辩），其评估结果不可信，课程无法持续开设。

## 六、面向学生群体与先修基础（需求）

- **FR-A 群体适配**：方案须明确标注适用学段、小组规模、建议周课时与总时长。
- **FR-B 先修声明**：方案须列出先修基础——Python 基础（函数/类/模块/异常）、命令行基础、HTTP/API 概念、英语文档阅读能力；可选 Git 基础。教师须据此做分层任务。

## 七、Functional Requirements（功能/内容需求）

- **FR-1（驱动问题）**：方案须给出一条真实、有挑战性、可操作的驱动问题（Driving Question）。
- **FR-2（跨学科融合矩阵）**：须以矩阵形式列出计算机科学 / 文档工程 / 教育学三视角的核心知识点与融入方式，且三者在项目流程中有逻辑关联。
- **FR-3（分阶段流程）**：须覆盖四阶段——①环境搭建 ②基于 Sphinx 的文档工程化 ③智能体功能设计与实现 ④展示与反思；每阶段含目标、活动、产出物。
- **FR-4（环境搭建可落地）**：须给出可复现的环境步骤（Python venv、`pip install sphinx`、主题与扩展选型、`sphinx-quickstart`）。
- **FR-5（文档工程化可落地）**：须给出 Sphinx 配置要点（MyST / autodoc / 主题）、`make html` 构建、以及 Git + CI 部署到 GitHub Pages / Read the Docs 的路径。
- **FR-6（智能体实现可落地）**：须给出最小 Agent Loop 设计、LLM API 接入方式（含密钥安全管理）、≥1 个工具调用示例、以及 autodoc 把代码纳入文档的做法。
- **FR-7（最终交付物）**：须明确列出两类硬交付物——可运行智能体代码仓库 + 配套 Sphinx 文档站点（源码 + 已部署 URL）；并附学生反思报告与路演材料。
- **FR-8（评估标准）**：须给出过程性评价 + 终结性评价的量规（rubric），且覆盖三学科视角。

## 八、Non-Functional Requirements（质量需求）

- **NFR-1（可操作性）**：教师拿到方案后无需额外查资料即可落地；所有命令行/配置给出可直接复制的片段。→ **落地载体：[`teacher/`](teacher/TEACHER-GUIDE.md) 教师实施包**（课时编排、可打印评分表、机房准备清单、课堂应答手册 4 件套），教师侧不再需要外部检索。
- **NFR-2（安全性）**：方案须强制要求 API Key 通过 `.env` + `python-dotenv` 管理，且 `.env` 必须被 `.gitignore` 排除（不可入库）。
- **NFR-3（差异化）**：须提供基础 / 进阶（元文档闭环）两档任务，照顾不同水平学生。**元文档闭环须进一步提供"教学化形态"（教师预置草稿样例，零 Token 成本）作为**必做**核心，"全自动形态"（真实调用 API 生成草稿）作为选做加分，另设"无配额降级通道"以保证 AC-6 可达——见 `decisions.md` DQ-3。
- **NFR-4（跨文档一致性）**：同一事实在方案的多处出现时，**操作性事实（可复制命令、文件路径）须逐字一致，数值性事实（行数、张数、版本号）须与实测一致**。派生数字必须可被脚本复核；能从实物派生的内容不得手写。审计方式见 [`review.md`](review.md) §九（R8）。→ **该需求由 R8 完整性审计新增**：NFR-1 承诺"教师无需额外查资料即可落地"，而"文件都在但说法互相打架"同样会导致落地失败，故单列为可验收需求。

## 九、Constraints（约束）

- **Technical**：依赖 Python ≥ 3.10、网络可访问 LLM API、**GitHub 个人账号**（用于 CI 部署）。**离线降级**：无外网机房可用本地 `ollama` 模型替代 LLM API（`LLM_BASE_URL=http://localhost:11434/v1`）；文档站可用内网 Git 服务（Gitea/GitLab 自建，或 `git init --bare` + `git daemon`）+ 自托管 runner 部署，或用静态托管（`python -m http.server _build/html`）替代 GitHub Pages，不阻断主干闭环。详见 `decisions.md` DQ-2。
- **Business/教学**：单项目建议 4–8 周、每周 2 课时；需机房或学生自带设备。
- **Dependencies**：Sphinx、myst-parser、sphinx-design、sphinx-copybutton、sphinx.ext.autodoc、python-dotenv、**`openai` Python SDK**（统一依赖；通过 `LLM_BASE_URL` 参数化兼容混元/DeepSeek/通义/ollama 等 OpenAI 兼容端点，不自研 provider 抽象层——见 `decisions.md` DQ-1）。

## 十、Assumptions（假设）

- 学生已具备 FR-B 所列先修基础，或教师已安排前置微课。
- 学校/学生有可用的 LLM API 配额（或本地 ollama 替代）。

## 十一、Acceptance Criteria（验收标准）

### AC-1: 文档站点可成功构建
- **Type**: `rule`
- **Given**: 学生按方案完成 Sphinx 初始化与内容编写
- **When**: 在项目根目录执行 `sphinx-build -b html docs docs/_build/html`（或等价写法 `python -m sphinx -b html docs docs/_build/html`）
- **Then**: 命令退出码为 0，且 `docs/_build/html/index.html` 存在
- **Pass Condition**: 构建无报错，`docs/_build/html/index.html` 可打开
- **Evidence**: 构建终端输出 + `docs/_build/html/index.html` 文件存在
- **备注**: 源文件目录为 `docs/`（`conf.py` 与 `index.md` 均在其中）；**勿写成 `sphinx-build -b html . _build/html`**——那会在根目录找 `conf.py` 并报 `Configuration error!`（R8 审计修正 A-1/A-5）。

### AC-2: 智能体可运行且含工具调用
- **Type**: `rule`
- **Given**: 已完成智能体代码与 `.env` 配置
- **When**: 运行入口脚本并输入一条测试指令
- **Then**: 智能体返回合理响应，且至少一次经过工具调用链路（如查询时间/计算）
- **Pass Condition**: 程序无异常退出，输出与工具结果一致
- **Evidence**: 运行日志 / 录屏

### AC-3: 文档工程质量（rubric）
- **Type**: `rubric`
- **Dimension**: 文档站点专业性（结构清晰、导航完整、含 API/使用指南、autodoc 生效）
- **Scale**: 1–5
- **Anchors**: 1 = 仅默认空壳；3 = 有基本页面但缺 API 文档或导航零散；5 = 结构完整、autodoc 生效、核心函数均有非空且有意义的 docstring、含使用指南与示例
- **Pass Threshold**: ≥ 4
- **Evidence**: 部署后的文档站 URL + 截图

### AC-4: 跨学科融合深度（rubric）
- **Type**: `rubric`
- **Dimension**: 三视角（CS/文档工程/教育学）在项目中是否真正咬合
- **Scale**: 1–5
- **Anchors**: 1 = 学科各自孤立；3 = 有融合但偏拼贴；5 = 元文档闭环使三视角自然咬合
- **Pass Threshold**: ≥ 4
- **Evidence**: 项目文档中"agent 生成文档草稿"功能实现（**教学化形态或全自动形态皆可**，见 `decisions.md` DQ-3）+ 学生反思提及跨视角理解
- **备注**: 本项对应 Task6 的**核心必做部分**（档 A 教学化形态）——AC-4 为硬门槛，故其载体不可为选做；若使用降级通道（档 C），本项按 anchored rubric 折半计分并须在 `diff-notes.md` 中如实标注草稿来源。

### AC-5: 密钥安全管理
- **Type**: `rule`
- **Given**: 项目含 LLM API 调用
- **When**: 检查仓库
- **Then**: 存在 `.env.example` 且 `.env` 出现在 `.gitignore`；仓库内无明文 Key
- **Pass Condition**: 无任何 API Key 明文提交
- **Evidence**: `.gitignore` 内容 + 仓库搜索结果

### AC-6: 元认知与反思质量（rubric）
- **Type**: `rubric`
- **Dimension**: 元认知与过程证据质量（对"为何文档重要 / 我如何厘清模块"的表达深度，且须有过程证据支撑）
- **Scale**: 1–5
- **Anchors**: 1 = 套话且无过程证据；3 = 描述过程并有提交历史；5 = 体现对自身理解盲点的真实洞察，且含"AI 草稿 vs 最终版"差异分析
- **Pass Threshold**: ≥ 4
- **Evidence**: 反思报告文本 + Git 提交历史（须多次原子提交，禁止单次大提交）+ 路演现场口头解释任一函数的记录
- **备注**: 本项经 V 对抗审查 A-6 修正——原标准仅看报告文本，存在"AI 代写"导致评价失真的 P0 风险，故增加过程证据要求。

## 十二、Resolved Decisions（原 Open Questions — 已决）

> 三项待决问题已于 session `sc-20260929-open-questions` 落定。**完整论证、被否选项、可证伪信号与回滚条件见 [`decisions.md`](decisions.md)**（该文件为决策的单一事实源）。

- [x] **DQ-1 LLM SDK 形态**：统一使用 `openai` Python SDK，通过 `LLM_BASE_URL` 参数化兼容混元/DeepSeek/通义/ollama。**不自研 provider 抽象层**——各厂商已提供 OpenAI 兼容端点，"多厂商差异"已被上游抹平，自研中间层消解的是已不存在的差异，净增排错负担且偏离 G2「能调用 LLM API」的目标表述。属性：`可覆盖`（教师可覆盖，但须同步回改 `decisions.md`）。
- [x] **DQ-2 CI 部署平台**：默认 **GitHub Pages（学生个人账号）**；离线用**内网 Git 服务 + 自托管 runner**；Read the Docs 降为"托管替代"（仅当学生不想管 CI 细节时启用）。排序第一键是**"项目结束后资产归属谁"**——学生个人账号使作品在课程结束后仍归学生所有；且零审批，服务 NFR-1。三档均**不豁免** `sphinx-build -W` 一致性硬约束。属性：`可覆盖`。
- [x] **DQ-3 元文档闭环强制属性**：**三档制**——档 A「教学化形态」（教师预置草稿样例 + 强制差异分析，**零 Token 成本，必做**）／档 B「全自动形态」（真实调用 API，**默认选做、加分**）／档 C「降级通道」（用 Task2 的 `api-draft.md` 与最终代码做差异分析，**保 AC-6 可达**）。原"必做 vs 选做"是假二分：它把"教学价值"与"Token 配额"两个独立维度压成了单一开关；AC-4 为硬门槛，故其载体不可为选做。**诚实性红线**：使用档 A 须如实标注草稿来源，谎报按学术诚信处理、本项判 0。属性：**`不可覆盖`**（涉及 AC-4/AC-6 的评估结构完整性）。

---
