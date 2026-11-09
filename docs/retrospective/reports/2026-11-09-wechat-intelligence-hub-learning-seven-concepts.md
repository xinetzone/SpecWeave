---
id: "learning-20261109-wechat-intelligence-hub-seven-concepts"
title: "wechat-intelligence-hub 全面学习 · 七概念知识沉淀报告"
type: "Report"
source: "外部公开仓库 external/dao/wechat/wechat-intelligence-hub（AGPL-3.0-only，v0.9.2-preview.2）"
x-toml-ref: "../../../.meta/toml/docs/retrospective/reports/2026-11-09-wechat-intelligence-hub-learning-seven-concepts.toml"
methodology: "seven-concepts (R→I→E→V→C)"
scenario: "知识沉淀（V 对抗审查强制）"
gates_passed: ["G1", "G2", "G3", "G4", "V"]
---

# wechat-intelligence-hub 全面学习 · 七概念知识沉淀报告

> **分析对象**：`D:\spaces\SpecWeave\external\dao\wechat\wechat-intelligence-hub`（微信个人情报库，公开 AGPL-3.0-only 仓库）
> **方法论**：七概念方法论编排（知识沉淀场景，标准链路 `R → I → E → V → C`，V 强制）
> **深度**：deep（全仓受控文件扫描 + 机械计数 + 关键点精读 + 四视角对抗审查）
> **内容级别**：Public（公开）→ 产出物落根 `docs/`
> **编排日期**：2026-11-09
> **闭环状态**：✅ 事实清单 → 四元组洞察 → 可迁移模式 → 四视角对抗审查 → 原子行动项，五阶段闭环完成

***

## 〇、执行摘要

本次任务以 `/七概念` 元指令对外部仓库 `wechat-intelligence-hub` 做全面学习并沉淀为可审计、可复用的知识成果。前置阶段完成启动协议回读、斜杠别名解析、能力注册行核对、内容敏感度预检与同类产出物定位；采集阶段覆盖 126 个受控文件中的架构、Skill 门面、CLI 命令面、信号规则、评估指标、安全边界、发布门禁、接入诊断与演进记录；收尾阶段完成 R/I/E/V/C 全链路。

**核心发现**：该项目的可迁移价值不在「微信情报」这个具体领域，而在三条工程契约——

1. **只读边界不是声明，是构建期会失败的机械约束**（架构分层 + `validate.sh` 负向扫描双重保证）；
2. **情报系统可信度取决于覆盖诚实，而非命中率**（显式区分「没采到」与「没有」）；
3. **接入验收按阶段分离**（模拟测试全绿 ≠ 真机首次取钥成功）。

此外，本次任务自身发现一条**元层面的规范风险**：同类七概念先例报告仍把复盘报告归档到 `.agents/docs/retrospective/`，而磁盘 `AGENTS.md` 第 119 行已声明该路径于 2026-08-31 废止。照抄先例会直接违反文档边界，故本次落盘以磁盘原文为准，并把该核验动作萃取为可执行模式（P-02）。

**产出物**：本报告 1 份、配套 TOML 元数据 1 份、`reports/index.md` toctree 追加 1 行、工作日志追加 1 节。**未执行 git 提交**。

---

## 一、前置判定（Preflight）

### 1.1 启动协议三锚点

按 `AGENTS.md` 启动协议（PRIORITY ZERO）从磁盘原文回读，确认三个锚点同时存在：

| 锚点 | 磁盘位置 | 结论 |
|------|---------|------|
| 「启动协议」位于文件首部醒目标题块 | `AGENTS.md:7` 引用、文件首部 | ✅ |
| 「文档边界」声明根 `docs/` 为唯一文档中心 | `AGENTS.md:119` | ✅ 明确「不是 `.agents/docs/`」 |
| 「内容敏感度预检」声明公开内容产出物入根 `docs/` | `AGENTS.md:7`、`:119` | ✅ |

### 1.2 斜杠别名解析

`/七概念` 不是 Skill 名，而是仓库斜杠指令别名。按「别名 → 指令文件 → Skill 门面 → 登记行」四步解析：

| 步骤 | 结果 |
|------|------|
| 别名 | `/七概念` → `seven-concepts` |
| 指令文件 | `.agents/commands/seven-concepts.md`（定义 R/F/I/E/V/A/C 与 G1–G4/V 质量门） |
| Skill 门面 | `.agents/skills/seven-concepts-cmd/SKILL.md`（`scenario=auto`、CMD-LOG 规范） |
| 登记行 | `.agents/capability-registry/03-commands-workflows-protocols-rules.md` 指令行；`02-skills.md` 技能行 |

运行时编译方法论 `.agents/skills/seven-concepts-cmd/references/compiled-methodology.md` 中「场景4：知识沉淀」标准链路为 `R → I → E → V → C（入库）`，V 强制。

### 1.3 内容敏感度预检

| 判据 | 观测 |
|------|------|
| 许可与发布形态 | `LICENSE` 为 `GNU AFFERO GENERAL PUBLIC LICENSE Version 3`；`COMMERCIAL-LICENSE.md` 声明 AGPL-3.0-only |
| 第三方资产隔离 | `NOTICE.md` 声明独立实现，不含 Tencent/WeChat 源码、凭据、用户数据库、旧第三方 CLI 二进制 |
| 仓库内容 | `git ls-files` 全为公开文档、脚本、测试与虚构数据；无真实聊天记录、姓名、ID |
| 访问控制 | 公开 GitHub 镜像，无访问控制 |

判定：**Public / 公开内容** → 走标准工作流，最终产出物入根 `docs/`（不是 `playground/`）。

### 1.4 落盘前三查

| 检查项 | 结论 |
|--------|------|
| 目标目录是否在根 `docs/` 下 | ✅ `docs/retrospective/reports/` |
| 同类产出物现有位置 | ✅ `docs/retrospective/reports/2026-08-03-animejs-threejs-adapter-learning-seven-concepts.md`（同为「外部技术学习 + 七概念复盘」单文件报告） |
| 路径规则是否来自磁盘原文 | ⚠️ **发现冲突**：先例报告仍写 `.agents/docs/retrospective/`；磁盘 `AGENTS.md:119` 明确该路径已废止。以磁盘原文为准 |

> 该冲突在 I-4、E 阶段 P-02、V 阶段 A-02 中进一步处理，是本次任务最重要的自反发现。

### 1.5 采集方式回退

初始计划按「子代理职责分层」把 126 个受控文件分给四路 `Explore` 子代理采集客观事实，四路调用全部被服务端 502 中断。回退策略：**主代理直接扫描 + 结构提取 + 机械计数 + 关键点精读**，覆盖目标仓库全部顶层区域。该回退及其对事实可追溯性的影响在 V 阶段 A-05 中登记。

---

## 二、R（Retrospective）：客观事实清单

### 2.1 仓库元信息

| 编号 | 客观事实 |
|------|---------|
| F01 | 目标路径为 `external/dao/wechat/wechat-intelligence-hub` |
| F02 | `README.md:7` 记载当前首发版本为 `v0.9.2-preview.2` |
| F03 | `LICENSE` 头部为 `GNU AFFERO GENERAL PUBLIC LICENSE Version 3, 19 November 2007`；`COMMERCIAL-LICENSE.md` 声明 AGPL-3.0-only，闭源集成/专有发行/OEM/白标需单独商业授权 |
| F04 | `NOTICE.md` 声明为独立实现，不附 Tencent/WeChat 源码、凭据、用户数据库、旧第三方 CLI 代码或二进制，不提供进程内存取钥、重签名、注入、Hook |
| F05 | 顶层条目共 11 个：`COMMERCIAL-LICENSE.md`、`CONTRIBUTING.md`、`LICENSE`、`NOTICE.md`、`README.md`、`SECURITY.md`、`docs/`、`projects/`、`providers/`、`scripts/`、`skills/` |
| F06 | 产品形态为「一个产品两个 Skill」：`wechat-cli`（Reader 依赖层）与 `wechat-intelligence-hub`（Hub 情报层） |

### 2.2 机械计数（2026-11-09 实测，含口径）

| 编号 | 指标 | 数值 | 统计口径 |
|------|------|------|---------|
| F07 | 受控文件 | 126 | `git ls-files \| wc -l` |
| F08 | Markdown / Python / Shell | 43 / 38 / 12 | `git ls-files '*.md' / '*.py' / '*.sh'` |
| F09 | Python + Shell 总行数 | 22,251 | `git ls-files '*.py' '*.sh' \| xargs wc -l` |
| F10 | 测试文件 | 20 | 路径匹配 `test_*.py` |
| F11 | 测试函数 | 316 | 全仓 `grep -rhoE 'def test_[A-Za-z0-9_]+' --include='*.py' .` |
| F12 | `SKILL.md` 门面 | 2 | `git ls-files \| grep -c 'SKILL.md'` |
| F13 | Hub CLI `add_parser(` 调用 / 唯一子命令名 | 37 处 / 33 个 | `wechat_intelligence_hub.py` 内 `add_parser("...")` 计数与去重 |
| F14 | Reader CLI `add_parser(` 调用 / 唯一子命令名 | 43 处 / 37 个 | `projects/rion-wechat-reader/` 下 `*.py` 计数与去重 |

**F11 口径分解**：`projects/wechat-intelligence-hub/` 158 个 + `projects/rion-wechat-reader/` 155 个 = 313；`providers/wxkey/tests/test_prepare.py` 3 个；合计 316。前期记录的 313 是「仅两个 `projects/` 子项目」口径，非计数错误，属范围差异。

**F13 唯一子命令名清单（33）**：`brief`、`chat-history`、`chat-search`、`cleanup`、`common-groups`、`compat-check`、`daily`、`db-index`、`db-links`、`db-search`、`db-status`、`feedback-add`、`feedback-list`、`group-daily`、`home`、`inbox`、`opportunities`、`opportunity-sync`、`opportunity-update`、`person`、`prioritize`、`profile-status`、`reactivation`、`render-report`、`reply`、`scan`、`today`、`topic`、`triage`、`vault-scan`、`vault-status`、`wechat-labels`、`wechat-scan`。

### 2.3 架构与只读边界

| 编号 | 客观事实 |
|------|---------|
| F15 | `projects/wechat-intelligence-hub/docs/architecture.md:5-8` 定义四层：`Reader`（`wechat-cli` 或兼容只读适配器读取本地微信数据）→ `Index`（SQLite、FTS、message hashes、run metadata）→ `Intelligence`（group threads、contact state、signals、candidates、opportunities）→ `Interface`（Codex 直接回答、Markdown、可选 HTML） |
| F16 | `architecture.md:33` 原文：`The project may update its own SQLite database, reports, feedback and local configuration. It must not send messages, click WeChat controls, add contacts or initiate payments.` |
| F17 | 个性化 Profile 归属 Intelligence 层，`wechat-cli` 保持中立只读适配；无个人上下文时状态为 `needs_context` |
| F18 | `projects/rion-wechat-reader/CAPABILITY_MATRIX.md` 记录 29 项工具/266 字段的能力对齐、本机实读验证、月度实跑与循环验收门槛，并提供 `scripts/live_parity.py --strict --pretty` 对照命令 |
| F19 | `README.md:69` 说明 Reader 核心不获取密钥、不重签名、不注入、不 Hook；notification-only 模式只覆盖入站预览 |

### 2.4 Skill 门面与命令面

| 编号 | 客观事实 |
|------|---------|
| F20 | `skills/wechat-intelligence-hub/SKILL.md` 定义 Mission、Non-Negotiables、Intent Router、9 步 Execution Protocol、Group Digest Delivery、State And Corrections、Output Contract；约束包括只读微信、原消息为证据、默认 24 小时窗口、HTML 仅通过内置安全渲染器、`delivery=auto`、`WECHAT_HUB_HOME` |
| F21 | 同文件原文约束：`索引过旧或采集失败时，明确说明覆盖缺口，不得把"没采到"写成"没有"` |
| F22 | `skills/wechat-cli/SKILL.md` 定义 `reader.sh` 为默认入口、`RION_WECHAT_CLI_BIN` 显式选择兼容 CLI、`diagnose`、五步 onboarding、`live_database_read_ok=true`；notification-only 模式须标记 `incoming_preview_only` |
| F23 | `scripts/install.sh` 支持 `--with-sqlcipher` 与 `--with-html`；默认安装两个 Skill，仅指定 Hub 时自动补齐 CLI；预检不覆盖已存在目录；正常调用无需设置 `WECHAT_HUB_HOME` |
| F24 | Hub 常用命令包含 `home/today/inbox/triage/opportunities/cleanup/person/reply/topic/brief/contact-daily`；`profile-init` 接收 `--owner-alias`、`--personal-doc`、`--plan-doc`、`--priority-label`、`--commercial-label`、`--creator-label` |
| F25 | `cleanup --raw-days 7 --report-days 30` 为项目 README 给出的清理参数示例 |

### 2.5 Intelligence 语义与输出诚实性

| 编号 | 客观事实 |
|------|---------|
| F26 | 商业生命周期状态机：`signal` → `candidate` → `opportunity` → `stale` / `archived`；candidate 默认 14 天无新证据过期；`triage pursue/wait/won` 晋级并保存反馈，`ignore` 保存抑制 |
| F27 | `references/signal-rules.md` 定义四级证据 `已确认` / `高概率` / `待核实` / `仅供存档`；机会类型 Brand Deal、Training/Consulting/Project Cooperation、Resource/Referral |
| F28 | 同文件定义跟进状态 `待回复` / `待兑现承诺` / `等待对方` / `临近截止` / `已发布待数据跟进` / `已发布待结算` / `已收款`，并规定同一 URL 只出现一次、高活跃不等于高价值 |
| F29 | Delivery Router 取值为 `auto/text/md/html/all`；单对象默认 text，多会话日报默认 HTML 并保留 Markdown；机器初筛文件不是最终交付 |
| F30 | `group_daily_digest.md` 为机器初筛；须读取 `group_daily_editorial_packet.json` 做第二遍语义编辑，生成 `group_daily_topics.md` 与 `group_daily_groups.md` |
| F31 | `docs/evaluation.md` 指标包含 Top-10 precision ≥8/10、duplicate rate、stale rate、missed-opportunity recall、feedback reuse、3 分钟 digest 阅读时间、topic usefulness、format parity、coverage honesty；真实 transcript 不进公开测试套件 |

### 2.6 安全与发布边界

| 编号 | 客观事实 |
|------|---------|
| F32 | `projects/wechat-intelligence-hub/report_security.py` 提供 `require_sanitizer()`、`safe_href()`、`sanitize_fragment()`、`protect_document()`；缺少 `nh3` 时 `require_sanitizer()` 抛 `RuntimeError`，提示 Markdown 仍可用、不安全 HTML 降级被禁用 |
| F33 | 同文件 CSP 为 `default-src 'none'; base-uri 'none'; object-src 'none'; frame-src 'none'; connect-src 'none'; img-src 'none'; media-src 'none'; form-action 'none';` + hash-based `script-src` + `style-src 'unsafe-inline'`；Pandoc raw HTML 关闭，外部图片与自动网络请求禁用 |
| F34 | `scripts/validate.sh` 依次执行 Skill `quick_validate.py`、Hub/Reader 单元测试、白名单发布候选构建、临时 Reader sibling 安装测试、`py_compile`、`bash -n`、旧名称扫描、私有标识扫描 |
| F35 | `validate.sh` 中若 `rg -n 'command -v wechat-cli' skills/wechat-cli/scripts/reader.sh` 命中则 `exit 1`，提示公开 wrapper 不得静默发现旧 `wechat-cli` 安装 |
| F36 | `validate.sh` 私有标识扫描正则包含 `wxid_[A-Za-z0-9_-]{8,}`、`[A-Za-z0-9_-]{8,}@chatroom`、`/Users/rion`、`BEGIN (RSA \|EC \|OPENSSH )?PRIVATE KEY`，排除 `release-manifest.json`、`build_release.py`、`validate.sh`、`test_compatibility.py` |
| F37 | `docs/release-checklist.md` 规定公开树不得含真实姓名、微信 ID、聊天室 ID、路径、token、截图、数据库、访问材料、报告；不得提交 `output/`、`tmp/`、`wechat-deal-radar/`、`config/profile.local.json`；须从干净 clone 验证安装 |
| F38 | `scripts/build_release.py` 使用公开白名单生成本地发布候选；`release-manifest.json` 为检查对象 |

### 2.7 接入阶段与演进记录

| 编号 | 客观事实 |
|------|---------|
| F39 | `docs/first-access-pilot.md` 把测试前条件、通过标准、失败分流错误码列为表格，包含 `candidate_not_default`；原文写明模拟授权与虚构加密库不能代替真实微信取钥验收；Windows 获取为独立路线 |
| F40 | `docs/followup-reliability-2026-10-17.md` 记录 hybrid 联系人日报、取消当轮交付、承诺按会话/项目/轮次保守匹配、消息 hash 加入 reader 会话 ID、旧 hash 惰性升级、30 天回看；给出 `test_followup_regressions.py` 等回归命令 |
| F41 | `projects/wechat-intelligence-hub/message_identity.py` 使用 reader provenance 构造 `conversation_key(chat, source_chat_id)` |
| F42 | `docs/releases/v0.9.2-preview.2.md:40-43` 记载 29 项只读工具/266 个公开输入字段、97 个会话/4,479 条消息、104 位重点联系人/229 个活跃群/约 7.9 万条群消息、119 项 Hub 测试与 43 项 Reader 测试通过 |
| F43 | `docs/access-upgrade-2026-09-22.md`、`docs/upgrade-2026-09-14.md`、`SECURITY.md` 记录接入能力升级、授权边界与安全上报方式 |

### 2.8 本次会话元事实

| 编号 | 客观事实 |
|------|---------|
| F44 | 启动协议三锚点已在磁盘 `AGENTS.md` 原文确认（见 §1.1） |
| F45 | `/七概念` 解析结果为 `seven-concepts` 指令 → `seven-concepts-cmd` Skill 门面（见 §1.2） |
| F46 | 内容敏感度判定为 Public，产出物落根 `docs/`（见 §1.3） |
| F47 | 四路 `Explore` 子代理采集调用全部返回服务端 502，采集改为主代理直接扫描 |
| F48 | 同类先例 `docs/retrospective/reports/2026-08-03-animejs-threejs-adapter-learning-seven-concepts.md` 的 I-3、C 章节写明复盘报告归档至 `.agents/docs/retrospective/`；磁盘 `AGENTS.md:119` 声明该路径于 2026-08-31 整体迁移后废止 |
| F49 | 本次会话在撰写本报告前未产生任何文件写入、编辑或 git 提交，全部前置操作为只读 |
| F50 | F42 中的运行规模与测试数量均为目标仓库文档自述，本次会话未复跑其测试套件 |

**G1 质量门验证**：✅ 50 条事实均为客观描述，无「因为/所以/导致」等因果推断词；所有数字均标注统计口径或来源文件行号；仓库自述数字（F42）与本次实测数字（F07–F14）分区登记，未混用。

---

## 三、I（Insight）：核心洞察

### I-1：「只读」不是声明，而是构建期会失败的机械约束

- **陈述**：目标仓库把「只读微信」实现为架构分层与发布期负向扫描两道可机械验证的约束，而非仅停留在 README 的一句承诺。
- **证据**：F15/F16 定义四层与明确写入禁区；F22 的 `reader.sh` 单一公开入口与 `incoming_preview_only` 标记；F35 使「静默发现旧 CLI」在 `validate.sh` 中直接 `exit 1`；F36 使私有标识进入公开树即构建失败；F37 规定公开树禁含真实数据并须从干净 clone 验证。
- **反常识**：常见做法是写一句「本项目只读」并依赖开发者自觉；声明本身不产生约束力。真正起作用的是让越界行为**在门禁中报错**——约束强度不取决于措辞，而取决于是否有可执行的失败路径。
- **下次行动**：SpecWeave 中任何「只读 / 不得写 / 禁止外发」类约束，除文档声明外必须配套一条可在门禁中执行的负向检查（正则或路径扫描），并把该检查列入发布清单。

### I-2：情报系统的可信度取决于「覆盖诚实」，而非命中率

- **陈述**：项目把「没采到」与「没有」显式区分，并将证据等级、上下文缺失状态、采集模式标记写进输出契约与评估指标。
- **证据**：F21 明确禁止把采集失败写成「没有」；F27 的四级证据；F17 的 `needs_context`；F19/F22 的 `incoming_preview_only`；F31 把 `coverage honesty` 列为评估指标；F30 要求机器初筛后必须做第二遍语义编辑。
- **反常识**：评估检索/情报系统时通常看 Top-K precision，但一个把索引过时或采集失败静默渲染成「无结果」的系统，precision 数字可以很高却完全不可信——**缺失可观测性比低命中率更危险**，因为它让错误看起来像结论。
- **下次行动**：SpecWeave 的知识检索、资料库查询与自动化报告输出统一携带 coverage 字段（时间窗、已索引量、缺口说明）；空结果必须区分「确实无」与「未覆盖」，禁止静默等价。

### I-3：「安装成功」不等于「数据可用」——阶段分离与独立验收门槛

- **陈述**：项目把安装完成、数据库可读、首次取钥、官方微信恢复、媒体资源覆盖、日报生成拆为不同验收阶段，每阶段有独立通过标准与失败分流。
- **证据**：F39 的 `first-access-pilot.md` 通过标准表、错误码、`candidate_not_default` 与「模拟授权不能代替真实取钥验收」原文；F18 的 `live_parity.py --strict` 循环验收；F22 的 `live_database_read_ok=true` 布尔门槛；F43 的接入升级记录。
- **反常识**：模拟测试全绿常被当作接入完成；但该项目明确写出，虚构加密库与模拟授权只证明验证与配置流程正确。测试覆盖的是**代码路径**，真机验收覆盖的是**环境事实**，二者不可互相替代。
- **下次行动**：SpecWeave 外部依赖（SDK / CLI / 数据库 / 凭据）接入清单按阶段拆表，逐阶段给出通过标准、失败码与回退动作；禁止用单元测试结果代替真机或真实凭据验收结论。

### I-4：先例报告沉淀的是「当时的规范快照」，落盘依据必须是磁盘原文

- **陈述**：同类七概念先例报告中的路径规范已与当前磁盘规范冲突，照抄先例会直接违反文档边界。
- **证据**：F48（先例 I-3/C 章节写 `.agents/docs/retrospective/`）与 `AGENTS.md:119`（该路径 2026-08-31 废止、禁止写入、落盘前三查第 3 项要求核对磁盘原文）构成直接冲突；F44 显示本次以磁盘原文回读规避。
- **反常识**：「照抄一份刚通过的同类报告」通常被认为最安全，因为它代表已验证的实践；但规范迁移后，**先例本身就是最大的错误源**——它的「正确性」绑定在生成时点，而不是当前时点。
- **下次行动**：把「落盘前三查」第 3 项固化为可执行步骤：定位规范文件 → 读取原文 → 核对废止声明与迁移日期 → 在产出物内登记所用规范的文件路径与行号；跨 30 天以上的先例只作结构参考，不作规范依据。

**G2 质量门验证**：✅ 4 条洞察均包含「陈述 / 证据 / 反常识 / 下次行动」四元组；证据均指向 §二 的事实编号或磁盘文件行号。

---

## 四、E（Extraction）：可迁移模式

### P-01：只读情报系统的 BCA 三层契约（Boundary / Coverage / Acceptance）

| 维度 | 内容 |
|------|------|
| **模式ID** | `read-only-intelligence-system-bca-contract` |
| **触发场景** | 构建「读取外部私有数据源 → 本地索引 → 生成判断/报告」的系统，且必须保证不对源端产生副作用 |
| **成熟度** | L1（首次萃取，validation_count=1） |
| **核心问题** | 只读承诺容易写在文档里，却缺少可执行约束；采集缺口容易被渲染成「无结果」；模拟测试容易被当作接入完成 |

**三层契约**：

1. **B — Boundary（边界层）**
   - 架构上把「读取」与「决策」分层，`Reader` 保持中立可替换，个性化与判断只放在上层；
   - 单一公开入口，禁止静默发现历史/替代实现；
   - 发布门禁中加入负向扫描（私有标识、旧名称、越权调用），命中即失败，不降级。

2. **C — Coverage（覆盖层）**
   - 输出契约强制携带 coverage：时间窗、已索引量、采集状态、缺口说明；
   - 证据分级（已确认/高概率/待核实/仅供存档）；上下文缺失时显式返回 `needs_context` 类状态；
   - 部分采集模式（如仅通知预览）必须标记为 partial，不得冒充全量；
   - 机器初筛与语义编辑分离，初筛物不得作为最终交付。

3. **A — Acceptance（验收层）**
   - 接入按阶段拆表：安装 → 可读性 → 凭据/授权 → 真机恢复 → 媒体覆盖 → 端到端产物；
   - 每阶段独立通过标准、失败码与回退动作；
   - 评估指标同时包含质量类（Top-10 precision）与诚实类（coverage honesty、duplicate rate、stale rate）。

**反模式**：
- ❌ README 写「只读」但无构建期检查；
- ❌ 空结果、采集失败、未索引三者共用一个「无」字面量；
- ❌ 模拟/虚构数据测试通过即宣布接入完成；
- ❌ 把个性化上下文塞进 Reader 适配层，导致适配器不可替换；
- ❌ HTML 渲染缺净化库时降级为不安全页面（应 fail-closed）；
- ❌ 机器初筛产物直接当作最终报告交付。

**检验标准**：① 越界提交能否让门禁自动失败；② 任意一次输出能否回答「这次覆盖了什么、缺了什么」；③ 是否存在至少一个阶段，单测全绿但真机仍会失败；④ 缺依赖时系统是否明确失败而非静默降级。

**迁移验证**：
- ✅ 可迁移到代码库/文档库只读分析 Agent；
- ✅ 可迁移到日志与监控数据的本地索引与日报系统；
- ✅ 可迁移到任何涉及个人数据、需要 fail-closed 安全渲染的报告生成器；
- ✅ 与 SpecWeave 的「内容敏感度预检」互补：预检管产出物去向，BCA 管系统行为边界。

### P-02：先例规范时效性核验（Precedent Spec Freshness Check，PSFC）

| 维度 | 内容 |
|------|------|
| **模式ID** | `precedent-spec-freshness-check` |
| **触发场景** | 需要在已有多份同类产出物的仓库中新增报告/知识包/文档，并打算「参考先例结构」时 |
| **成熟度** | L1（首次萃取，validation_count=1） |
| **核心问题** | 先例沉淀的是生成时点的规范快照，规范迁移后先例会持续输出过期路径与过期规则 |

**四步核验**：
1. **结构参考、规范不参考**：先例仅用于确定文档骨架、frontmatter 形态、章节粒度；路径、目录名、字段要求一律不采信。
2. **定位权威文件**：从磁盘原文（如 `AGENTS.md`）找到当前规范条款，记录文件路径 + 行号。
3. **核对废止声明**：检索「已废止 / 迁移 / 禁止新建 / 历史路径」等关键词与迁移日期；若先例生成日期早于迁移日期，其路径规范一律判为过期。
4. **在产出物内留痕**：新产出物登记「所用规范文件 + 行号 + 核对日期」，并把发现的冲突写成事实项（本次为 F48）与洞察（I-4）。

**反模式**：
- ❌ 直接复制先例的 frontmatter 与路径字段；
- ❌ 以「同类报告都放这里」替代磁盘规范核对；
- ❌ 发现冲突后擅自修改规范文本以迁就先例（应登记为未决项）；
- ❌ 冲突只口头说明、不落入事实清单与洞察（无法审计）。

**检验标准**：产出物中能否指出至少一处「规范文件路径 + 行号」；若存在过期先例，是否被显式登记而非静默忽略。

**迁移验证**：
- ✅ 可迁移到 OKF 知识包新建（今日日志中已有「归档路径按磁盘原文优先」的同构经验）；
- ✅ 可迁移到 CI 配置、模板文件、脚手架生成；
- ✅ 可迁移到跨仓库复用 Skill / Agent 定义时的版本核对。

**G3 质量门验证**：✅ 两个模式均给出模式 ID、触发场景、成熟度、核心问题、可执行步骤、反模式、检验标准与至少 3 个跨领域迁移场景；P-01 与 P-02 分别来自目标仓库机制与本次任务自身过程，覆盖面互补。

---

## 五、V（Adversarial Review）：四视角对抗审查

| 视角 | 核心质问 | 关注点 |
|------|---------|--------|
| 视角 1 · 魔鬼代言人 | 「是不是把 README 的自述当成了验证过的事实？」 | 事实来源分级 |
| 视角 2 · 新人 | 「这些数字我能不能自己复现？」 | 口径与可追溯性 |
| 视角 3 · 老板 | 「学完对 SpecWeave 有什么用，值不值？」 | 知识落地与投入产出 |
| 视角 4 · 未来维护者 | 「半年后这份报告还成立吗？」 | 时效性与许可边界 |

### 审查意见与采纳情况

| 编号 | 视角 | 审查意见 | 处理 |
|------|------|---------|------|
| A-01 | 新人 | 前期记录 313 个测试函数，实测 316；同类数字还有 37/33、38/37 两组差异，报告若只写单一数字会被误读 | ✅ **采纳**：§2.2 全表增加「统计口径」列，F11 给出 158+155+3 分解并说明 313 属范围差异；F13/F14 区分「调用次数」与「唯一子命令名」 |
| A-02 | 魔鬼代言人 | 先例报告仍指向已废止的 `.agents/docs/`；若按同类先例落盘会违反 `AGENTS.md:119` | ✅ **采纳**：落盘改至根 `docs/retrospective/reports/`；§1.4、F48、I-4、P-02 四处留痕，并萃取 P-02 模式 |
| A-03 | 魔鬼代言人 | F42 的 119/43 项测试、97 会话/4,479 消息等均为仓库文档自述，本次未复跑，不可与实测数字并列 | ✅ **采纳**：F42 与 F50 明确标注「仓库自述，本次未复跑」，与 §2.2 实测区物理分离 |
| A-04 | 老板 | 报告若只讲对方架构，不回答「与我何干」，等于信息搬运 | ✅ **采纳**：新增 §八「知识落地判断」，给出可直接应用 / 触发条件适用 / 不适用三档结论及具体行动点 |
| A-05 | 未来维护者 | 四路子代理 502 失败属于执行环境异常，若不登记，后来者会误以为全部 126 文件经独立复核 | ✅ **采纳**：F47 与 §1.5 登记回退策略，明确「主代理直接扫描」这一口径限制 |
| A-06 | 老板 | AGPL-3.0-only 是强 copyleft；若报告暗示可直接移植代码，会带来合规风险 | ✅ **采纳**：§八 增加许可边界条款，明确仅迁移设计思想、代码片段仅作机制说明、代码级移植需合规评估或商业授权 |
| A-07 | 新人 | 既然 C 是「原子化」，是否应把报告拆成多册？ | ❌ **不采纳**：七概念 C 阶段在复盘语境下的 G4 要求是**行动项原子化**（animejs 先例 C 章节即为原子行动项表）；`external-learning/` 下的分册是另一种归档形态，与本次单文件七概念报告先例不一致。保持单文件 + 原子行动项表 |
| A-08 | 未来维护者 | CMD-LOG 前期只以自然语言描述，未输出结构化日志链，链路不完整 | ✅ **采纳**：§十 补齐 10 条结构化 CMD-LOG（S0 `CMD_START` → 各 `GATE_PASSED` → `SEVEN_CONCEPTS_COMPLETED` → S9 `CMD_COMPLETE` 闭环），并登记本会话未做 git 提交 |

审查意见共 **8 条**，采纳 **7 条**修正、明确驳回 1 条并给出依据（≥5 条意见、≥2 条采纳，满足 V 门）。

### 反常识假设验证表

| 反常识假设 | 验证结果 |
|-----------|---------|
| 「README 写了只读，就等于系统只读」 | ❌ 推翻：需架构分层 + 门禁负向扫描才产生约束力（I-1） |
| 「precision 高就说明情报系统可信」 | ❌ 推翻：覆盖不诚实会让缺失伪装成结论（I-2） |
| 「模拟测试全绿 = 接入完成」 | ❌ 推翻：代码路径与环境事实是两类验收（I-3） |
| 「照抄刚通过的同类报告最安全」 | ❌ 推翻：先例携带过期规范快照（I-4） |
| 「313 与 316 必有一个是错的」 | ⚠️ 限定：两者口径范围不同（子项目 vs 全仓），不是错误，但必须标注 |
| 「C 阶段要求文档拆分成原子分册」 | ❌ 推翻：G4 约束的是行动项，非文档物理结构 |

---

## 六、C（Atomic Commit）：原子行动项

| 优先级 | 原子行动项 | 验收标准 | 状态 |
|--------|-----------|---------|------|
| 高 | 在根 `docs/` 下创建七概念主报告 | `docs/retrospective/reports/2026-11-09-wechat-intelligence-hub-learning-seven-concepts.md` 存在，含完整 R/I/E/V/C 章节 | ✅ 本次完成 |
| 高 | 创建配套 TOML 元数据 | `.meta/toml/docs/retrospective/reports/` 下同名 `.toml` 存在，`x-toml-ref` 可解析 | ✅ 本次完成 |
| 高 | 在 `docs/retrospective/reports/index.md` toctree 追加本报告条目 | toctree 包含 `2026-11-09-wechat-intelligence-hub-learning-seven-concepts` | ✅ 本次完成 |
| 高 | 事实清单全表标注统计口径与来源 | §2.2 含口径列；F42/F50 明确标注仓库自述 | ✅ 本次完成 |
| 中 | 把「过期先例规范」登记为事实 + 洞察 + 模式 | F48 / I-4 / P-02 三处留痕 | ✅ 本次完成 |
| 中 | 补齐结构化 CMD-LOG 链 | §十 首条为 S0 `CMD_START`、末条为链路完成事件 | ✅ 本次完成 |
| 中 | 追加当日工作日志 | `.workbuddy-ai/memory/2026-11-09.md` 追加本节任务记录 | ✅ 本次完成 |
| 中 | 为 SpecWeave 输出增加 coverage 字段的设计提案 | 交回文档/检索链路 Owner；产出独立提案，不改现有代码 | ⏳ 待 Owner 认领 |
| 中 | 为「只读/禁写」类约束补充门禁负向检查清单 | 交回治理 Owner；逐条对应到可执行的正则或路径扫描 | ⏳ 待 Owner 认领 |
| 低 | 复核其他外部学习报告是否残留 `.agents/docs/` 路径 | 交回文档治理 Owner；仅登记不代改存量 | ⏳ 待 Owner 认领 |
| 低 | 评估 AGPL-3.0-only 组件引入 SpecWeave 的合规边界 | 交回合规 Owner；仅在设计思想层迁移，不涉及代码复制 | ⏳ 待 Owner 认领 |

**边界声明**：C 阶段本次仅产出文档与行动项，**不执行 git 提交**、不修改 `external/` 下任何目标仓库文件、不代其他 Owner 修改存量资产。

**G4 质量门验证**：✅ 11 项行动项均为单一职责、可独立执行与独立验证，无复合大任务；7 项本次完成，4 项明确交回 Owner。

---

## 七、质量门总体验证

| 质量门 | 要求 | 验证结果 |
|--------|------|---------|
| **G1** | 事实无因果词、可追溯、数量与口径一致 | ✅ 50 条事实纯客观；数字附口径；实测与仓库自述分区 |
| **G2** | 洞察含陈述/证据/反常识/行动四元组 | ✅ 4 条洞察全部满足 |
| **G3** | 模式含触发场景、步骤、反模式、检验标准、跨领域迁移 | ✅ 2 个模式全部满足 |
| **G4** | 行动项原子化 | ✅ 11 项单一职责，状态与 Owner 明确 |
| **V** | 四视角、≥5 条意见、≥2 条采纳修正 | ✅ 8 条意见 / 7 条采纳 / 1 条附依据驳回 |

---

## 八、知识落地判断（对 SpecWeave 的自应用）

| 判断维度 | 结论 |
|---------|------|
| **可直接应用** | ✅ **P-02 先例规范时效性核验**：可立即并入「落盘前三查」第 3 项，本次任务已实际验证其必要性（F48）。<br>✅ **coverage 字段设计思想**：适用于资料库查询、知识包检索与自动化报告的空结果表达。<br>✅ **门禁负向扫描思路**：适用于「禁止向 `.agents/docs/` 写入」等既有规则，可补一条构建期检查。 |
| **触发条件适用** | 当 SpecWeave 新增「读取外部私有数据源并生成报告」类组件时启用 P-01 的 BCA 三层契约；当接入 SDK/CLI/凭据类外部依赖时启用 §I-3 的阶段分离验收表。 |
| **不适用 / 需限定** | ❌ 目标项目的微信数据模型、信号规则、机会状态机属于其业务域语义，与 SpecWeave 的知识包治理无直接对应关系，不迁移。<br>❌ `nh3` + hash-based CSP 的具体实现针对 HTML 日报渲染，SpecWeave 报告走 Sphinx/Markdown 链路，暂不需要该实现。 |
| **许可边界** | ⚠️ 目标仓库为 **AGPL-3.0-only**（F03）。本报告仅迁移**设计思想与治理模式**，正文引用的少量代码片段仅用于说明机制、不构成可复用实现；任何代码级移植、闭源集成或专有发行须先做合规评估或取得商业授权（`COMMERCIAL-LICENSE.md`）。 |

---

## 九、附录：事实来源索引

| 主题 | 目标仓库内路径 |
|------|--------------|
| 产品入口 / 版本 / 双 Skill | `README.md`、`COMMERCIAL-LICENSE.md`、`LICENSE`、`NOTICE.md`、`SECURITY.md` |
| 四层架构 / 只读边界 | `projects/wechat-intelligence-hub/docs/architecture.md` |
| Hub 命令面 / Profile | `projects/wechat-intelligence-hub/README.md`、`wechat_intelligence_hub.py` |
| Skill 门面 | `skills/wechat-intelligence-hub/SKILL.md`、`skills/wechat-cli/SKILL.md` |
| 信号与证据规则 | `skills/wechat-intelligence-hub/references/signal-rules.md` |
| 交付与日报编辑 | `skills/wechat-intelligence-hub/SKILL.md`（Group Digest Delivery、Output Contract） |
| 评估指标 | `projects/wechat-intelligence-hub/docs/evaluation.md` |
| HTML 安全 | `projects/wechat-intelligence-hub/report_security.py` |
| 发布门禁 / 隐私边界 | `scripts/validate.sh`、`projects/wechat-intelligence-hub/docs/release-checklist.md`、`scripts/build_release.py` |
| 安装 / 首次接入 | `scripts/install.sh`、`docs/first-access-pilot.md` |
| Reader 能力对齐 | `projects/rion-wechat-reader/CAPABILITY_MATRIX.md` |
| 跟进可靠性 / 消息身份 | `docs/followup-reliability-2026-10-17.md`、`projects/wechat-intelligence-hub/message_identity.py` |
| 版本说明 / 演进 | `docs/releases/v0.9.2-preview.2.md`、`docs/access-upgrade-2026-09-22.md`、`docs/upgrade-2026-09-14.md` |
| 本次落盘规范依据 | `D:\spaces\SpecWeave\AGENTS.md:7`、`:119`；`docs/retrospective/reports/index.md`；`2026-08-03-animejs-threejs-adapter-learning-seven-concepts.md` |

---

## 十、CMD-LOG 与遗留项

```
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20261109-wechat-intelligence-hub-learning | msg=方法论编排开始：全面学习 wechat-intelligence-hub | ctx={"scenario":"knowledge","topic":"wechat-intelligence-hub-comprehensive-learning","depth":"deep"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S1 | event=SCENARIO_DETECTED | session=sc-20261109-wechat-intelligence-hub-learning | msg=场景识别为知识沉淀，内容敏感度 Public | ctx={"scenario":"knowledge","sensitivity":"public","output_root":"docs/"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S2 | event=CHAIN_SELECTED | session=sc-20261109-wechat-intelligence-hub-learning | msg=链路选定 R→I→E→V→C，V 强制 | ctx={"chain":["R","I","E","V","C"],"v_mandatory":true}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S3 | event=GATE_PASSED | session=sc-20261109-wechat-intelligence-hub-learning | msg=G1 通过：50 条事实，数字附口径 | ctx={"gate":"G1","facts":50}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S4 | event=GATE_PASSED | session=sc-20261109-wechat-intelligence-hub-learning | msg=G2 通过：4 条四元组洞察 | ctx={"gate":"G2","insights":4}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S5 | event=GATE_PASSED | session=sc-20261109-wechat-intelligence-hub-learning | msg=G3 通过：2 个可迁移模式 | ctx={"gate":"G3","patterns":2}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S6 | event=GATE_PASSED | session=sc-20261109-wechat-intelligence-hub-learning | msg=V 通过：8 条意见，7 条采纳修正 | ctx={"gate":"V","perspectives":4,"review_items":8,"adopted":7}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S7 | event=GATE_PASSED | session=sc-20261109-wechat-intelligence-hub-learning | msg=G4 通过：11 项原子行动项 | ctx={"gate":"G4","action_items":11,"completed":7}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S8 | event=SEVEN_CONCEPTS_COMPLETED | session=sc-20261109-wechat-intelligence-hub-learning | msg=R-I-E-V-C 链路闭环完成，产出物落根 docs/，未执行 git 提交 | ctx={"scenario":"knowledge","facts":50,"insights":4,"patterns_extracted":2,"perspectives_reviewed":4,"action_items":11,"gates_passed":["G1","G2","G3","G4","V"],"git_commit":false,"output":"docs/retrospective/reports/2026-11-09-wechat-intelligence-hub-learning-seven-concepts.md"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S9 | event=CMD_COMPLETE | session=sc-20261109-wechat-intelligence-hub-learning | msg=命令执行完毕 | ctx={"cmd":"seven-concepts","scenario":"knowledge","result":"success","gates_passed":5,"log_entries":10}
```

**遗留项**：
1. 四路子代理采集因服务端 502 全部失败，事实采集由主代理独立完成，未获得独立第二方交叉复核（F47、A-05）。
2. 目标仓库测试套件、真实首次取钥、HTML 渲染本次均未实跑，相关数字取仓库文档自述（F42、F50）。
3. §六 中 4 项行动项交回各 Owner，本会话不越界修改存量资产。
