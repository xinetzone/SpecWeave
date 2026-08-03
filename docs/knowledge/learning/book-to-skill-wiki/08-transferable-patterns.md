# 可复用工程模式

这些模式可以从 book-to-skill 迁移到 SpecWeave 和其他 Agent 工具项目。

---

## 模式 1：编译时付费架构（Compile-time Payment Architecture）

**触发场景**：反复访问的结构化知识（规范、API 文档、领域知识）

**核心思想**：一次性支付预处理成本（解析、结构化、索引），运行时按需加载，避免 Discovery Loop Tax。就像编译型语言一次性编译为机器码，运行时直接执行而不是每次都解释执行；结构化知识在首次导入时完成所有昂贵的解析工作，后续会话只加载需要的片段。

**核心步骤**：

1. **识别高复用知识**：找出会被反复访问、且每次重新解析成本高的内容（如书籍、规范文档、大型代码库 API）
2. **预编译为结构化格式**：将原始非结构化内容转换为带索引、分章节的结构化 Markdown 或其他可快速检索的格式
3. **运行时只加载所需片段**：通过 Topic Index、Chapter Index 快速定位到相关章节，只加载该部分到上下文窗口
4. **源文件保留用于验证**：原始文件保留，用于验证预编译结果的准确性或在需要时直接查询

**在 book-to-skill 中的实现**：
- 提取阶段一次性完成文档解析、Unicode 清理、格式转换，输出 `full_text.txt` 和结构化元数据 [file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/cli.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/cli.py)
- 生成阶段将书籍拆分为独立的章节文件、glossary、patterns、cheatsheet，并在 SKILL.md 中建立完整索引 [file:///d:/spaces/SpecWeave/external/libs/book-to-skill/SKILL.md](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/SKILL.md)
- REPL 式分片访问：大文件通过 grep/sed 或 Read 的 offset/limit 按需读取，避免一次性加载全文 [SKILL.md:210-236](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/SKILL.md#L210-L236)

**反模式**：
- 每次会话都重新解析原始文档，重复支付相同的预处理成本
- 将大上下文窗口当作免费午餐，把整本书/整个代码库塞进去而不做分层
- 没有建立索引结构，每次都从头扫描全文寻找相关信息

**迁移到 SpecWeave 示例**：
- **规范文档预索引**：`.agents/` 下的所有规范在首次使用时建立导航表，后续直接通过 docgen-cmd 刷新，无需每次手动遍历
- **AGENTS.md 分层加载**：根 AGENTS.md 只包含路由表，具体角色定义、规则、工作流在需要时按需读取，避免启动时加载所有规范
- **Skill 按需激活**：Skill 门面模式只在触发关键词命中时才加载对应 Skill 的完整定义

---

## 模式 2：规范驱动生成（Spec-driven Generation）

**触发场景**：需要生成结构化产出物但逻辑不应硬编码

**核心思想**：用可执行的规范文档（如 SKILL.md）定义生成流程，而不是在代码中硬编码步骤。Agent 本身成为规范解释器，规范文档既是人类可读的工作说明，也是机器可执行的指令，避免实现与流程的耦合。

**核心步骤**：

1. **将工作流编码为 Markdown 规范**：把步骤、检查点、质量规则都写在 Markdown 文档中，而不是散落在代码里
2. **规范包含步骤、预算、质量规则**：每个步骤明确做什么、输入输出是什么、token 预算是多少、质量验收标准是什么
3. **Agent 作为规范解释器执行**：Agent 读取规范文档，按顺序执行其中描述的步骤，根据规则调整行为
4. **规范本身可被 Agent 读取和遵循**：规范使用清晰的结构化格式，包含明确的触发条件和指令，Agent 无需额外代码就能理解并执行

**在 book-to-skill 中的实现**：
- 整个转换流程定义在 [SKILL.md](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/SKILL.md) 中，包含 Step 0 到 Step 10 的完整工作流
- 每个步骤明确触发条件、执行动作、输出格式、质量规则
- Token 预算矩阵（BOOK_TYPE × DEPTH）直接写在规范中，Agent 根据输入特征选择预算 [SKILL.md:337-356](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/SKILL.md#L337-L356)
- 章节模板、支持文件格式也都在规范中明确定义，无需在 Python 代码中硬编码

**反模式**：
- 在 Python/JS 代码中硬编码提示词模板，修改流程需要改代码重新发布
- 生成逻辑与实现耦合，无法在运行时调整或查看流程
- 工作流只存在于代码注释或开发者头脑中，Agent 无法直接读取执行

**迁移到 SpecWeave 示例**：
- **.agents/commands/ 下的命令规范**：每个命令（如复盘、原子化、导出报告）都是一个 Markdown 规范，定义执行步骤和输出格式，Cmd 门面作为解释器
- **Skill 门面模式**：Skill 通过标准化的 frontmatter 和描述定义触发条件和能力，Agent 根据描述决定是否加载和如何使用
- **角色定义文件**：`.agents/roles/` 下的每个角色是一个 Markdown 文档，定义职责、能力边界、协作方式，而不是硬编码在系统提示词中

---

## 模式 3：文档供应链安全分层防御（Document Supply Chain Layered Defense）

**触发场景**：处理来自不可信来源的文档输入（PDF/EPUB/DOCX 等）

**核心思想**：纵深防御（Defense in Depth），每层独立过滤一类攻击，不依赖单一防护。就像网络安全的多层防火墙，即使一层被绕过，其他层仍能阻止攻击。在文档→Agent 供应链中，从文本提取到生成产出再到 CI 门禁，每一层都有独立的安全控制。

**核心步骤（5 层）**：

1. **Unicode 注入清理**：在文本提取阶段移除零宽字符、Unicode 标签块等用于隐写和提示注入的不可见字符
2. **解析器级防护（XXE 等）**：在解析 DOCX/EPUB 等结构化文档时，在调用解析器之前扫描并拒绝 DTD/ENTITY 声明等危险结构
3. **参数注入防护**：调用外部子进程时，对文件路径进行绝对化处理，防止以 `-` 开头的文件名被当作命令行 flag
4. **生成后扫描**：所有生成的产出物在发布/加载前进行模式扫描，检测提示注入、数据外泄、权限提升等可疑模式
5. **CI SAST**：在代码合并和发布流程中，使用静态代码分析工具（CodeQL、Bandit、Zizmor）进行自动化安全门禁

**在 book-to-skill 中的实现**：
- Layer 1: Unicode 清理实现在 [sanitize.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/sanitize.py)，所有解析器输出后立即调用
- Layer 2: DOCX XXE/Billion-Laughs 防护在 [parsers/docx.py:71-92](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/parsers/docx.py#L71-L92)，在任何 XML 解析前执行扫描
- Layer 3: 子进程参数防护在 [parsers/pdf.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/parsers/pdf.py) 和 [parsers/calibre.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/parsers/calibre.py) 中通过 `os.path.abspath()` 实现
- Layer 4: 生成 Skill 扫描在 [tools/scan_generated_skill.py](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/tools/scan_generated_skill.py)，检测 7 类提示注入和其他安全问题
- Layer 5: CI 配置在 [.github/workflows/ci.yml](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/.github/workflows/ci.yml) 和 [.github/workflows/codeql.yml](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/.github/workflows/codeql.yml)

**反模式**：
- 信任单一过滤层，一旦被绕过整个系统就失守
- 只在输入点检查，不检查生成后的产出物
- 用黑名单而非白名单策略，无法防护 0-day 攻击
- 扫描结果输出匹配的恶意文本，导致扫描报告本身成为注入载体

**迁移到 SpecWeave 示例**：
- **外部文档解析**：使用 content-parser 或 defuddle 提取外部网页/文档内容时，同样需要 Unicode 清理和内容扫描
- **forum-posting 输入清理**：处理用户提交的论坛内容时，分层过滤 XSS、提示注入、恶意链接
- **代码扫描**：ci-check-cmd 中的重复代码检测、链接检查、模式成熟度检查等多层门禁，构成代码质量的纵深防御

---

## 模式 4：优雅降级与依赖探测（Graceful Degradation & Dependency Probing）

**触发场景**：有多种可选依赖/工具可完成同一任务，环境不可控

**核心思想**：探测可用依赖，自动选择最佳可用路径，提供合理降级而非直接失败。就像网页的渐进增强——在功能最全的环境中提供最佳体验，在缺少依赖的环境中仍能完成核心功能，保证工具在各种环境下都能用。

**核心步骤**：

1. **定义依赖矩阵（最佳→可用→fallback）**：为每个功能列出从最佳到降级的多个可选依赖路径，明确标注哪些是可选的、哪些是必需的
2. **启动时探测可用性**：运行时通过 `importlib.util.find_spec()` 检测 Python 模块，通过 `shutil.which()` 检测系统命令
3. **三态安装模式（yes/no/ask）**：支持 `--install-missing yes|no|ask` 三种模式，交互式环境询问用户，非交互式环境默认使用 fallback
4. **每个路径独立失败不影响整体**：某个依赖安装失败或不可用时，自动回退到下一个可用路径，不因为单个可选依赖缺失导致整个工具无法运行

**在 book-to-skill 中的实现**：
- 依赖矩阵定义在 [dependencies.py:14-68](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/dependencies.py#L14-L68)，每个格式组标注了 modules、system tools、satisfaction 语义和 fallback 说明
- 依赖探测使用 `python_module_available()` 和 `shutil.which()` [dependencies.py:71-72](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/dependencies.py#L71-L72)
- 三态安装模式由 `normalize_install_mode()` 处理 [dependencies.py:102-116](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/dependencies.py#L102-L116)，支持环境变量和命令行参数
- `--check` 预检查模式可以输出所有依赖的状态报告和安装命令，不实际处理文件 [dependencies.py:216-289](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/book_to_skill/dependencies.py#L216-L289)
- 示例：EPUB 有 ebooklib+bs4 时最佳解析，都没有时回退到 stdlib zipfile 解析器；DOCX 有 python-docx 时最佳，没有时回退到 stdlib ZIP/XML 解析

**反模式**：
- 硬依赖单一工具，该工具未安装时直接报错退出
- 安装失败直接退出，不尝试 fallback 路径
- 静默降级不告知用户，用户不知道使用了低质量路径
- 不提供预检查模式，用户在转换到一半才发现缺少依赖

**迁移到 SpecWeave 示例**：
- **多解析器支持**：OCR 功能优先使用 local-ocr-npu（本地 NPU 加速），不可用时回退到云端 OCR 服务，都没有时提示用户
- **浏览器自动化多后端**：TRAE-browseruse 和 agent-browser 作为可选后端，根据环境可用性自动选择，都不可用时提示安装
- **文档生成多格式导出**：导出报告时优先使用 pandoc（最佳质量），没有时使用 Python 原生库生成基础格式

---

## 模式 5：Token 预算自适应矩阵（Token Budget Adaptive Matrix）

**触发场景**：LLM 生成任务需要控制成本，不同输入类型需要不同预算

**核心思想**：基于输入特征（内容类型、深度要求）建立二维预算矩阵，而非固定 token 限制。一刀切的 token 限制要么浪费（小任务给大预算）要么质量不足（复杂任务给小预算），自适应矩阵根据内容特征动态分配预算。

**核心步骤**：

1. **定义分类维度**：识别影响生成质量和成本的关键维度，如内容类型（technical/text）、深度要求（reference/study）、长度规模（小/中/大）
2. **每个单元格有明确预算**：为维度的每个组合定义明确的 token 预算范围（最小值-目标值-上限），并说明如何"挣得"更高预算
3. **生成前估算并确认**：在开始生成前，根据输入特征估算总 token 用量，告知用户成本和时间，等待确认后再继续
4. **超预算触发 REPL 式分片处理**：对于超出单次处理预算的大输入，采用分片策略，每次只处理一部分，通过 grep/sed 按需提取相关片段

**在 book-to-skill 中的实现**：
- 二维预算矩阵：`BOOK_TYPE`（technical/text）× `DEPTH`（reference/study）[SKILL.md:339-345](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/SKILL.md#L339-L345)
- 预算范围：text/reference 800-1200 tokens，text/study 1000-1800，technical/reference 1200-1800，technical/study 2000-3000
- "挣得"预算规则：study 深度必须通过添加 Worked Example、扩展框架步骤、补充失败模式说明来获得更多 token，而不是靠注水 padding [SKILL.md:350-355](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/SKILL.md#L350-L355)
- Step 2.5 预飞行成本估算：读取 metadata.json 后向用户展示预估 token 用量、成本、时间，等待确认后继续 [SKILL.md:174-206](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/SKILL.md#L174-L206)
- REPL 式分片：>50k tokens 的书籍不一次性读入，而是用 grep/sed 定位章节偏移，按需读取相关片段 [SKILL.md:210-236](file:///d:/spaces/SpecWeave/external/libs/book-to-skill/SKILL.md#L210-L236)
- 支持文件独立预算：glossary ≤1500，patterns ≤2000，cheatsheet ≤1200，SKILL.md body ≤4000 tokens

**反模式**：
- 一刀切的 token 限制，所有章节/所有文档用同样的预算
- 不估算就开始生成，做到一半才发现超出预算或成本失控
- 小任务用大预算浪费 token，大任务预算不足导致生成质量差
- 通过注水和废话来凑够 token 数，密度低下
- 大文件一次性读入上下文，在多轮处理中反复支付输入 token 成本

**迁移到 SpecWeave 示例**：
- **文档生成预算控制**：根据文档类型（技术文档/管理文档/会议记录）和长度要求分配不同的生成预算
- **代码分析深度自适应**：简单代码 review 用小预算快速反馈，架构级深度分析用大预算并分片处理
- **任务执行分级**：简单问答直接回答，复杂任务先估算步骤和成本，用户确认后再执行

---

**事实来源**：本章节基于以下事实编号 F-042, F-043, F-044, F-045, F-046
