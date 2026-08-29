# Agent Skills 开放标准 & skills-ref 参考实现 —— 架构洞察（I 阶段产出）

> 本文件的洞察、知识地图与差异化判断均基于同目录 `facts.md`（F-001 ~ F-068）登记的事实。事实与推断严格分离：facts.md 只登记"信源里有什么"，本文件承载"这意味着什么、该怎么用"。

---

## 一、核心洞察

### 洞察 1：description 不是文档字段，而是整个标准的"路由函数"——渐进式披露把触发判断的全部负担压在 1024 字符之内

**陈述**：Agent Skills 的三层加载契约（Catalog ~100 tokens → Instructions <5000 tokens → Resources 按需）在架构上把"技能是否被使用"的决定权完全交给模型对 `description` 的匹配。规范、创作指南、评估方法论三份文档从不同层面围绕同一个机制展开：description 是唯一常驻上下文的技能表面，它写得不好，技能等于不存在；写得过宽，则污染每一次任务的路由决策。

**证据**：F-012（三阶段 token 预算，name+description 启动时全量加载）、F-007（description 应同时写明 what 与 when，需含触发关键词）、F-035（description 是首要触发机制；欠规定不触发、过宽误触发）、F-036（四条写作原则，含"宁可 pushy"）、F-037~F-040（专门的触发评估方法论：20 条查询、3 次运行、0.5 阈值、60/40 训练验证切分）、F-049（目录中 location 的存在也服务于激活与相对路径解析）、F-016（quickstart 明言 description 是"智能体决定是否激活的依据"）。

**反常识点**：直觉上 description 是"技能介绍"，但其真实角色是路由键。文档甚至承认一个反直觉事实：简单的单步请求即使 description 完全匹配也可能不触发——因为智能体只在任务超出自身能力时才查询技能（F-035）。这意味着 description 优化的目标函数不是"相关性"而是"超出基线能力时的可召回性"，且存在系统性的过拟合风险，官方为此搬出了 train/validation split 这种 ML 实验方法来保护一个 YAML 字段（F-040）。

**行动建议**：为任何技能撰写 description 时，按"祈使句 + 用户意图 + 显式适用场景（含不点名领域的情形）+ 1024 字符内"四要素成稿；发布前至少跑一轮触发率测试（8-10 正例 + 8-10 近失负例，各 3 次），用验证集而非训练集选择定稿版本；把 description 变更视同接口变更纳入评审。

### 洞察 2：规范本体刻意极小，标准的真正资产是"加载契约"而非"文件格式"——目录位置、发现、激活全部下放为生态惯例

**陈述**：整个格式规范只约束一件事：一个含 SKILL.md 的目录长什么样（6 个 frontmatter 字段 + 无限制的正文 + 三个推荐子目录）。规范不规定技能目录住在哪里、如何被发现、如何被注册——这些全部由客户端实现指南以"惯例 + 建议"的形式承接，其中 `.agents/skills/` 是被标注为"广泛采用"的事实惯例而非规范要求。

**证据**：F-001（AGENTS.md 声明 specification.mdx 唯一权威，且实现不构成规范）、F-002（目录结构仅 4 项）、F-004（仅 6 个字段）、F-004/F-009（唯一实验性字段 allowed-tools 明言各实现支持度不一）、F-044（"规范本身不强制技能目录住在哪里"；`.agents/skills/` 为跨客户端惯例；`.claude/skills/`、git 根祖先、XDG 均为可选附加位置）、F-046（项目级覆盖用户级是"现有实现的普遍惯例"而非规范条款）、F-042（开放标准由 Anthropic 发起、46 家客户端采纳，F-041）。

**反常识点**：一个"开放标准"仓库里，真正被 46 家客户端统一遵守的部分（三层加载契约、`.agents/skills/` 路径）大部分不在规范文件里，而在指南与惯例里；反过来，规范里最严格的约束（name 必须与目录名一致）在客户端指南里却被明确建议放宽（见洞察 3）。标准的"硬"与"软"分布与直觉相反——格式硬、生态软，且 AGENTS.md 明文禁止把实现行为反向当作规范。

**行动建议**：在本工作区自建技能时，格式严格遵守 specification.mdx（name 与目录名一致、6 字段白名单）；存放位置跟随 `.agents/skills/` 惯例以获得跨客户端可见性；不要把某个客户端（包括 skills-ref）的行为差异当作标准差异上报，应回到 specification.mdx 裁决（F-001）。

### 洞察 3：同一仓库内并存"严格校验器"与"宽松客户端"两套互相矛盾的行为标准——这是有意设计的两极，测试文件是张力的仲裁记录

**陈述**：skills-ref 的 `validate()` 拒绝一切白名单外字段、强制 name 与目录名 NFKC 归一化后完全一致、接受 i18n 名称；而客户端实现指南建议的解析策略是"name 不匹配或超长→警告但加载、仅缺 description 或 YAML 不可解析才跳过"。两者对同一名为 `MySkill` 的技能给出相反的处理。仓库 AGENTS.md 预先声明了裁决规则：规范权威，实现只是 demonstration artifact。

**证据**：F-059（validator 六条 name 规则 + NFKC + 目录匹配 + i18n docstring）、F-060（未知字段报错 "Unexpected fields..."）、F-061（validate() 四个早退分支）、F-047（客户端宽松校验四规则：name 不匹配/超长→警告加载；仅 description 缺失与 YAML 不可解析→跳过；Note 自述"有意放宽规范约束"）、F-054（README："demonstration purposes only, not meant to be used in production"）、F-053（作者为 Anthropic 员工的 0.1.0 版参考库）、F-001（实现不构成规范）。

**反常识点**：宽松校验的四条规则把"必填"与"装饰性"区分开——只有 description 缺失才跳过，因为它是披露层的最小必需品；name 错误只是警告。这与 skills-ref 的全量拒绝形成教科书式的两种失败策略（fail-fast 校验器 vs best-effort 运行时）。更微妙的是 skills-ref 自身也不完全同构于规范：规范文本写 "a-z, 0-9"，validator 却用 `isalnum()` 接受全 Unicode 小写字母（中文、俄文名可通过，F-068）——文档、实现、测试三层各差半步，测试目录（特别是 NFKC 用例）成了唯一精确记录实现语义的地方。

**行动建议**：产出物管线（CI 门禁）采用 skills-ref 式严格校验（`skills-ref validate`，退出码 0/1 明确）；客户端式加载采用宽松策略并把诊断写入日志。遇到"技能在 A 工具能加载、B 工具报错"类问题，先判断该属性属于格式硬约束还是客户端宽松层，再决定是修技能还是报兼容性问题。

### 洞察 4：这个仓库把"技能"当作需要 eval 驱动迭代的软件资产来治理——评估文档的篇幅超过规范本体，且方法论直接移植自 ML 实验

**陈述**：skill-creation 四篇指南中，评估与 description 优化两篇合计覆盖了双臂对照运行、断言分级（PASS 必须附证据）、benchmark delta 分析、盲比较、人工反馈闭环、训练/验证切分——一套完整的实验方法学。文档还给出了明确的停止条件与"过度约束时删指令"的反向操作，其治理姿态与代码资产的 CI/评审流程同构。

**证据**：F-027~F-034（evals.json schema、with/without 双臂、干净上下文、timing.json、断言原则、grading.json、benchmark.json delta、五条模式分析规则、迭代闭环与 skill-creator 自动化）、F-019（一轮 execute-then-revise 即显著提升）、F-033（"恒通过的断言要删除"——防止指标虚高）、F-022（500 行/5000 token 上限）、F-025（gotchas 段是迭代改进最直接的落点）。

**反常识点**：三个反直觉要点——① 恒通过的断言不是"安全"而是噪音，会夸大技能价值，必须删除；② 通过率停滞时首选动作是**减少**指令而非增加（over-constrained 假设）；③ 解释 why 的指令比 ALWAYS/NEVER 刚性指令更可靠——这三条都与"往 SKILL.md 里堆更多规则"的自然倾向相反。此外，评估要求每次运行从干净上下文开始，暗示技能效果与会话历史强耦合，单次"看起来能用"的验证不可信。

**行动建议**：为本工作区每个自建 Skill 建 `evals/evals.json`（先 2-3 个用例），沿用 iteration-N 工作区结构与 delta 分析；gotchas 段作为每次纠正智能体错误后的固定回写点；若引入 anthropics/skills 的 skill-creator，可自动化该循环（F-034）。

### 洞察 5：skills-ref 是一份"最小完整闭环"的架构样本——8 个符号、4 个模块、3 个 CLI 子命令覆盖客户端集成的全部三个接触点

**陈述**：skills-ref 用不足 500 行 Python 完整覆盖了客户端集成指南中的三个程序化接触点：发现后的元数据读取（`read_properties`/`find_skill_md`/`parse_frontmatter`，strictyaml 保证 YAML 子集安全）、Tier 1 目录生成（`to_prompt` 输出 Anthropic 推荐的 `<available_skills>` XML，含 html.escape 转义与 SKILL.md 绝对路径）、质量门禁（`validate` 返回错误列表而非抛异常）。其公开 API 与内部函数的边界（`__all__` 8 个导出 vs `_validate_name` 等私有函数）、错误分类（ParseError vs ValidationError）、退出码约定（0/1）都可作为自研 Skill 客户端的接口设计模板。

**证据**：F-055（8 导出符号 + `__version__`）、F-056（异常层级与 SkillProperties/to_dict 序列化规则：None 剔除、allowed-tools 连字符键、空 metadata 省略）、F-057（parser 四类 ParseError 与 strictyaml、metadata 值强制 str 化）、F-058（read_properties 不做全量校验的职责切分）、F-059~F-061（validator 常量、规则序列、validate_metadata 核心函数避免重复 I/O 的设计）、F-062（to_prompt 精确输出格式与 Anthropic 推荐 note）、F-063~F-064（click 骨架、`_is_skill_md_file` 容错、三子命令与退出码）、F-065~F-068（41 个测试锁定的全部行为，含 XML 转义、NFKC、i18n）。

**反常识点**：① 校验 API 返回 `list[str]`（空列表=有效）而读取 API 抛异常——同一库内两种错误风格按用途分工（校验面向 CI 聚合错误，读取面向快速失败），与常见"统一抛异常"直觉相反；② `to_prompt` 的 XML 里 name/description 走 html.escape 而 location 不转义，且输出格式在 docstring 中自我声明"仅 Anthropic 推荐、其他客户端可自行格式化"——官方参考实现主动放弃输出格式的规范性；③ `read_properties` 对 metadata 值做了隐式 `str()` 归一（YAML 数字 1.0 变 "1.0"），这一行为只被测试（F-065）而非文档记录。

**行动建议**：SpecWeave 自研 Skill 加载器时直接复用该闭环分工——发现层用 `find_skill_md` + 宽松解析、披露层用 `to_prompt` 同构 XML（或按模型调整格式）、门禁层用 `validate` 进 CI；错误处理沿用"校验返回列表、读取抛异常"的分工；注意 metadata 值的字符串化行为在序列化时保持一致。

---

## 二、知识地图

### concepts/ 文档列表（按学习路径排序：入门 → 核心 → 高级）

| 序号 | 提议文件 | 标题 | 覆盖事实 | 路径层级 | 说明 |
|---|---|---|---|---|---|
| 1 | `concepts/01-skill-anatomy.md` | Skill 目录解剖与 SKILL.md 格式 | F-002 ~ F-015 | 入门 | 目录结构、frontmatter+正文、六个字段、可选目录约定、文件引用、validate 命令 |
| 2 | `concepts/02-progressive-disclosure.md` | 渐进式披露：Agent Skills 的组织性原理 | F-012, F-013, F-016, F-017, F-022, F-035, F-043 | 入门→核心 | 三层加载契约、token 预算、Discovery→Activation→Execution 生命周期 |
| 3 | `concepts/03-frontmatter-fields.md` | 六个 frontmatter 字段详解与约束对照 | F-004 ~ F-010, F-059, F-060 | 核心 | 逐字段的规范约束 × validator 实现规则双栏对照（含 allowed-tools 实验性标注） |
| 4 | `concepts/04-authoring-principles.md` | 创作原则：上下文经济学与控制校准 | F-018 ~ F-026 | 核心 | 真实专业-knowhow 来源、add-what-agent-lacks、划界、gotchas/模板/checklist/验证循环/plan-validate-execute 五模式 |
| 5 | `concepts/05-eval-driven-iteration.md` | 评估驱动迭代：把 ML 实验方法用于技能治理 | F-027 ~ F-034 | 高级 | evals.json、双臂对照、断言分级、grading/benchmark/feedback 三 JSON、五条模式分析、迭代闭环 |
| 6 | `concepts/06-description-optimization.md` | description 触发优化与防过拟合 | F-035 ~ F-040 | 高级 | 触发机制、四写作原则、触发率测量脚本、60/40 切分、五轮循环 |
| 7 | `concepts/07-client-integration.md` | 客户端集成生命周期：发现→披露→激活→长会话管理 | F-044 ~ F-052 | 高级 | 扫描位置与上界、命名冲突/信任/云端、宽松校验、目录构建、双激活路径、结构化包裹与压缩豁免 |
| 8 | `concepts/08-skills-ref-reference-implementation.md` | skills-ref 参考实现：最小完整闭环的架构样本 | F-053 ~ F-068 | 高级 | 包元数据、公开 API 全签名、parser/validator/prompt/cli 分工、异常与错误风格、41 测试行为锁定 |

（另注：脚本工程细节——uvx/pipx/npx/bunx/deno/go 运行器、PEP 723 内联依赖、stdout/stderr 分离、`--dry-run`、输出截断阈值 10-30K——信源为 `docs/skill-creation/using-scripts.mdx`，建议并入 04 号 concepts 的附录节而非独立成篇，避免超出 6-9 篇上限。）

### examples/ 文档列表（2 篇）

| 提议文件 | 标题 | 覆盖事实 | 说明 |
|---|---|---|---|
| `examples/01-first-skill-roll-dice.md` | 创建第一个 Skill 实战：从空目录到 VS Code 里掷骰子 | F-015, F-016, F-017 | 按官方 quickstart 复刻：`.agents/skills/roll-dice/SKILL.md`（<20 行）→ `/skills` 验证发现 → 触发激活 → 用 `skills-ref validate` 收尾门禁；穿插 name=目录名、description 触发依据两个格式要点 |
| `examples/02-skills-ref-cli.md` | skills-ref CLI 实战：校验、读属性、生成技能目录 | F-053, F-054, F-061 ~ F-066 | 三子命令全流程：`validate`（含 SKILL.md 文件路径容错与退出码）、`read-properties`（JSON 输出与 to_dict 序列化规则）、`to-prompt`（多技能 XML 与转义行为）；附 Windows/uv 安装与"demonstration only"定位说明 |

### references/ 文件划分（2 份登记表）

| 提议文件 | 内容 | 登记对象 |
|---|---|---|
| `references/spec-sources.md` | 规范文档信源登记 | `AGENTS.md`、根 `README.md`、`docs/specification.mdx`、`docs/home.mdx`、`docs/clients.mdx`、`docs/snippets/clients.jsx`、`docs/skill-creation/` 5 篇、`docs/client-implementation/adding-skills-support.mdx` —— 共 12 个信源文件，逐个登记：角色（权威规范/指南/数据）、关键章节、对应 F-xxx 编号段 |
| `references/skills-ref-sources.md` | skills-ref 源码登记 | `pyproject.toml`、`README.md`、`src/skills_ref/` 7 个模块、`tests/` 3 个测试 —— 共 12 个文件，逐个登记：模块职责、公开/私有 API 签名、异常类型、被测试锁定的行为、对应 F-xxx 编号段 |

---

## 三、与 anthropics-skills 既有知识束的差异化要点

| 维度 | 本知识束（agentskills 标准仓库） | 既有知识束（anthropics/skills 官方技能库） |
|---|---|---|
| 对象层级 | **协议层**：开放标准规范 + 参考校验实现，回答"SKILL.md 必须长什么样、如何被校验、客户端如何集成" | **资产层**：官方维护的具体技能集合（含 skill-creator 等成品），回答"有哪些现成技能、怎么用、怎么被 skill-creator 自动生成" |
| 核心内容 | 6 字段格式契约、渐进式披露三层模型、宽松/严格双校验策略、客户端集成五步生命周期、eval 驱动迭代方法论 | 具体技能的功能面、prompt 工程实例、skill-creator 对评估与 description 优化流程的自动化封装 |
| 权威性来源 | specification.mdx 为格式唯一权威源；AGENTS.md 明文禁止把实现行为当规范（F-001） | 技能本身即最佳实践示范，但没有规范地位 |
| 不可替代的独有事实 | i18n/NFKC 名称语义（文档 a-z、实现 isalnum、测试锁定三方差异，F-005/F-059/F-068）；`<available_skills>` XML 精确格式与转义规则（F-062/F-066）；46 客户端生态名录（F-041）；`.agents/skills/` 跨客户端惯例与扫描上界（F-044/F-045） | skill-creator 的自动化能力本身（评估、评分、基准聚合、description 优化的端到端封装，本知识束仅在 F-034/F-040 处引用其存在） |
| 互补关系 | 本知识束的评估方法论（concepts/05、06）与 anthropics-skills 的 skill-creator 构成"方法 ↔ 工具"对应：先理解方法再看工具，或在无工具环境手搓该方法 | 学完本知识束后使用 anthropics-skills 时，能识别每个成品技能对格式约束与渐进式披露的具体兑现方式 |

**一句话定位**：anthropics-skills 教你"用别人写好的技能"，本知识束教你"标准是什么、怎么写、怎么验、怎么集成"——两者以 F-034 的 skill-creator 引用为衔接点，互为上下游。
