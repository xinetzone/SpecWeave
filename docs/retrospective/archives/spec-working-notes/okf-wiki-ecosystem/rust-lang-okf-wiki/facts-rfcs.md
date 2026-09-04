# facts-rfcs.md — rust-lang/rfcs 事实清单
> 仓库基线：master @ 354518a8c9025f40be6f730452c1bfe71a12dc22（2026-08-15）；路径前缀 external/libs/rust-lang/rfcs/
> 采集原则：零推测，仅记录文档中写明的内容（标题、元数据字段值、章节名、Summary/设计要点原文摘要）。每条事实可经 Read/Grep 验证。

## A. 流程与模板

- F-rfcs-001: README.md 首行标题为 "Rust RFCs - [RFC Book](https://rust-lang.github.io/rfcs/) - [Active RFC List](https://rfcbot.rs/)"（源：README.md L1）
- F-rfcs-002: README.md 将 RFC（request for comments）流程表述为"为 Rust 变更（如新特性）提供一致且受控的路径，使所有利益相关者对项目方向有信心"（源：README.md L5-7）
- F-rfcs-003: README.md 列出的"substantial"变更示例：非 bugfix 的语言语义或语法变更、移除语言特性（含 feature-gated 的）、`std` 的大型新增（源：README.md L43-45）
- F-rfcs-004: README.md 列出的无需 RFC 的变更：改变形状不改变含义的改写/重组、严格改善客观数值质量标准的添加（警告移除、提速、平台覆盖等）、仅被 Rust 开发者（而非用户）注意到的添加、`std` 小型新增（仅需 ACP，链接 std-dev-guide 的 feature-lifecycle 页）（源：README.md L47-56）
- F-rfcs-005: RFC 提交流程（README.md "What the process is" 节）：fork 仓库 → 复制 `0000-template.md` 为 `text/0000-my-feature.md` → 填写并提交 PR → 以 PR 编号重命名文件前缀（0000- 改为该编号）并更新文件顶部 "RFC PR" 链接（源：README.md L105-118）
- F-rfcs-006: RFC 编号分配规则：提交时不预先分配 RFC 编号，编号即 PR 编号，RFC 被接受时文件相应重命名（源：README.md L106-108、L116-118）
- F-rfcs-007: FCP（最终评论期）机制：subteam 成员提出 "motion for final comment period" 并附处置意见（merge/close/postpone）；进入 FCP 前所有 subteam 成员必须 sign off；FCP 持续十个日历日（至少 5 个工作日），在 This Week in Rust 等处公布；FCP 期间出现实质性新论点可取消 FCP 使 RFC 回到开发模式（源：README.md L135-160）
- F-rfcs-008: RFC 生命周期：RFC 以 markdown 文件合并进 RFC 仓库后即为 "active"，作者可实现它并向 Rust 仓库提 PR；"active" 不是橡皮章，不意味着功能最终合并，也不蕴含实现优先级或开发人员分配（源：README.md L162-177）
- F-rfcs-009: README.md 规定已接受的 RFC 不应被实质性修改，仅极小变更可作为修正案提交；更重大的变更应写成新 RFC 并在原 RFC 上加注（"very minor change" 的判定归 sub-team）（源：README.md L179-189）
- F-rfcs-010: RFC Postponement：被 "postponed" 标签关闭的 RFC 表明团队在将来之前既不想评估也不想实现该特性；历史上 postponed 被用于推迟到 1.0 之后；postponed 的 PR 可在时机合适时重开，无正式流程（源：README.md L227-243）
- F-rfcs-011: RFC 提交前的常见准备：官方 Zulip 服务器（rust-lang.zulipchat.com）、开发者讨论论坛（internals.rust-lang.org）、偶尔发 "pre-RFC"；本仓库的 issue 可用于讨论但团队不主动查看（源：README.md L87-91、L271-272）
- F-rfcs-012: 许可证状态：仓库正在按 Apache License 2.0 或 MIT 双许可的过渡过程中，部分内容已按此许可；详情指向 RFC 2044 及其 tracking issue（rust#43461）；除非明确声明，贡献按 Apache-2.0 定义双许可（源：README.md L254-268）
- F-rfcs-013: `0000-template.md` 的元数据头部共 4 个字段：Feature Name（唯一标识符如 `my_awesome_feature`）、Start Date（YYYY-MM-DD）、RFC PR（rust-lang/rfcs#0000 链接）、Rust Issue（rust-lang/rust#0000 链接）（源：0000-template.md L1-4）
- F-rfcs-014: `0000-template.md` 正文共 9 个章节：Summary、Motivation、Guide-level explanation、Reference-level explanation、Drawbacks、Rationale and alternatives、Prior art、Unresolved questions、Future possibilities（源：0000-template.md L6-103）
- F-rfcs-015: 模板对 Guide-level explanation 的指引：像功能已包含在语言中那样向其他 Rust 程序员讲解，主要靠示例；实现导向 RFC（编译器内部）该节聚焦编译器贡献者视角；政策 RFC 该节提供政策示例驱动的介绍（源：0000-template.md L22-34）
- F-rfcs-016: 模板对 Reference-level explanation 的定位："This is the technical portion of the RFC"，要求详尽到与其他特性的交互清晰、实现方式清楚、角落案例以示例剖析（源：0000-template.md L36-45）
- F-rfcs-017: 模板 Prior art 节列举可含内容：其他语言中该特性及其社区经验、其他社区的做法、发表论文；并声明"其他语言的先例本身不足以构成 RFC 的动机"（源：0000-template.md L60-75）
- F-rfcs-018: generate-book.py 的自述功能：基于文件系统布局自动生成 mdBook 的 SUMMARY.md 文件，基于 `text` 目录内容生成 `src` 目录（源：generate-book.py L3-6）
- F-rfcs-019: generate-book.py 文档化的多章节布局约定：RFC 通常保持单章节，特殊情况下用同名子目录放置额外页面（`0123-my-awesome-feature.md` + `0123-my-awesome-feature/extra-material.md`），静态内容（图片等）建议同样布局；章节按排序顺序呈现（源：generate-book.py L8-20）
- F-rfcs-020: generate-book.py 执行逻辑：先删除并重建 `src` 目录（清除切换分支后的陈旧链接）；对 `text/` 下每个条目及 compiler_changes.md、lang_changes.md、libs_changes.md、README.md（符号链接名为 introduction.md）创建符号链接；写入 src/SUMMARY.md；最后调用 `mdbook build`（源：generate-book.py L27-47）
- F-rfcs-021: SUMMARY.md 生成结构：`[Introduction](introduction.md)` + 三行 guidelines 链接（compiler/language/library changes）+ collect() 递归收集 text/ 下 .md 条目（链接路径去掉前 5 个字符 "text/" 前缀，条目名去 .md 后缀）（源：generate-book.py L40-59）
- F-rfcs-022: book.toml 配置：书名 "The Rust RFC Book"；output.html 设置 smart-punctuation = true、no-section-label = true、git-repository-url = "https://github.com/rust-lang/rfcs"、site-url = "/rfcs/"；搜索 heading-split-level = 0；playground runnable = false；build extra-watch-dirs = ["text"]（源：book.toml L1-17）
- F-rfcs-023: .github/workflows/deploy.yml：push 到 master 分支触发；环境变量 MDBOOK_VERSION 为 0.5.4（由 renovate 管理，datasource=crate）；流程为 checkout（fetch-depth: 0）→ 安装 mdbook → 运行 ./generate-book.py → 上传 ./book 产物 → 部署到 github-pages 环境（源：.github/workflows/deploy.yml L1-45）
- F-rfcs-024: .github/PULL_REQUEST_TEMPLATE.md 的要求：由于 RFC 涉及大量并行的难以跟随的对话，请使用对文本变更的 review comment threads（可点 diff 右上 "Comment on this file"）而非对 RFC 的直接评论（源：.github/PULL_REQUEST_TEMPLATE.md L1-6）
- F-rfcs-025: lang_changes.md 规定：语言层面几乎每个变更都需要 RFC；新 lint（或对现有 lint 的重大变更）视为语言变更；语言 RFC 由语言子团队管理并标记 `T-lang`；新 PR 在提交一周内完成初始 triage（结果为指派 shepherding / 以 postponed 关闭 / 以"明确不该做"关闭）（源：lang_changes.md L1-15）
- F-rfcs-026: lang_changes.md 修正案规则：实现中所需的小变更（本质 bug fix、与已接受 RFC 精神一致）通过 RFC PR 修正原 RFC；变更剧烈时创建独立新 RFC 并在原 RFC 加注释引用；判定指引为"变更影响 RFC 多于一处（非局部）/ 影响原 RFC 对动机用例的适用性 / 存在多种新方案"则不算 minor（源：lang_changes.md L18-38）
- F-rfcs-027: compiler_changes.md 规定：编译器 RFC 由编译器子团队管理并标记 `T-compiler`，一周内初始 triage；文档明确"大多数超出简单 PR 范围的编译器决策使用 MCP 而非 RFC"，MCP 链接指向 rust-lang/compiler-team issues（源：compiler_changes.md L1-12）
- F-rfcs-028: compiler_changes.md 列出的需 RFC 变更：复杂设计空间且涉及其他团队的重大用户可见编译器变更（示例为 path sanitization，链至 rfcs PR 3127）、造成编译器/语言/库 stable 行为重大向后不兼容的其他变更；不需 RFC 的包括：bug 修复与错误消息改进、小重构、大型内部重构（需 MCP）、实现已有接受 RFC 的语言特性、新 lint（归 lang 团队，建议先在 clippy 试用后 uplift）、稳定编译器 flag 变更（需在某处 FCP）（源：compiler_changes.md L14-39）
- F-rfcs-029: libs_changes.md Motivation 节列出的 RFC 开销事实：RFC 从发帖到落地最少 2 周，争议性变更实际可达数月量级；RFC 需要多数 subteam 审查与正式投票；RFC 不能按复杂度降级（"Full process always applies"）；PR 可被任何 rust-lang 贡献者 insta-merge、可经 bors/buildbot/trains 乐观接受（源：libs_changes.md L3-35）
- F-rfcs-030: libs_changes.md 的总体哲学："do whatever is easiest"——若写 RFC 比实现工作量小则是需要 RFC 的信号；预期争议可直接走 RFC；新 API 几乎必然值得 RFC（"new APIs almost certainly merit an RFC"）（源：libs_changes.md L45-51）
- F-rfcs-031: libs_changes.md 的 PR/RFC 判定清单——提交 PR：bugfix、docfix、明显 API 空缺修补（对称类型补 API，例 `Vec<T> -> Box<[T]>` 推出 `String -> Box<str>`）、不稳定 API 微调、实现 Clone/Debug 等"明显" trait；提交 RFC：新 API、稳定 API 语义变更、稳定 API 泛化（例 Pattern/Borrow）、稳定 API 弃用、非平凡 trait impl（源：libs_changes.md L53-66）
- F-rfcs-032: libs_changes.md 关于 insta-stable 的表述：以 unstable 合并的非 RFC PR 需有 feature gate 与 tracking issue，但 "trait impls and docs are insta-stable and thus have no tracking issue"，因此对此类变更需要更高审查强度（源：libs_changes.md L81-85）
- F-rfcs-033: libs_changes.md 描述的稳定化周期：每个发布周期结束时 libs team 评估当前不稳定 API 并选择部分在下周期 FCP 稳定化；FCP 后 API 的三条路径为 Stabilize / Deprecate / Extend the FCP（仍无法达成共识时考虑要求新 RFC 或以 "too controversial for std" 弃用）；beta 期发现新稳定 API 的问题时强烈倾向于回退稳定（源：libs_changes.md L94-113）

## B. 精读 RFC 事实

### 0114-closures（闭包与 Fn trait 统一）
- F-rfcs-034: 元数据：Start Date 2014-07-29；RFC PR rust-lang/rfcs#114；Rust Issue rust#16095；头部无 Feature Name 字段（早期 RFC 格式）（源：text/0114-closures.md L1-3）
- F-rfcs-035: Summary 列出的核心变更：函数调用 `a(b, ..., z)` 经 `Fn<A,R>`、`FnShare<A,R>`、`FnOnce<A,R>` 三个 trait 变为可重载操作符（A 为参数类型元组、R 为返回类型，三 trait 区别在 self 参数 `&mut self`/`&self`/`self`）；移除 `proc` 表达式形式与类型；移除闭包类型（闭包形式保留为语法糖）（源：text/0114-closures.md L7-14）
- F-rfcs-036: 闭包表达式新语法：`ref |...| expr` 按引用捕获 upvar（保持当时行为），`|...| expr` 按值捕获（Copy 或 move）；receiver 模式前缀 `|&mut: ...|` 对应 Fn、`|&: ...|` 对应 FnShare、`|: ...|` 对应 FnOnce；类型位置语法糖 `|T1,...,Tn| -> R` 翻译为 `Fn<(T1,...,Tn),R>` 等对应形式（源：text/0114-closures.md L15-35）
- F-rfcs-037: Motivation 核心理念小节标题为 "The core idea: unifying closures and traits"；`a(b, c, d)` 脱糖为 `Fn::call(&mut a, (b, c, d))` / `FnShare::call_share(&a, ...)` / `FnOnce::call_once(a, ...)` 三者之一；闭包表达式翻译为实现三 trait 之一的新鲜 struct；文档给出 `&mut Fn<(int,),int>`（虚分派）与 `<F:Fn<(int,),int>>`（静态分派）对照示例（源：text/0114-closures.md L60-106）
- F-rfcs-038: 章节结构：Summary、Motivation（The core idea: unifying closures and traits、Bind by reference vs bind by value）、Detailed design（Closure expression syntax、Closure sugar in trait references）、Drawbacks、Alternatives、Transition plan、Unresolved questions（含小节 Closures that are quantified over lifetimes）（源：text/0114-closures.md，Grep `^#{1,3} ` 计 12 个标题，L5-L422）

### 3137-let-else（let-else 语句）
- F-rfcs-039: 元数据：Feature Name: `let-else`；Start Date 2021-05-31；RFC PR rust-lang/rfcs#3137；Rust Issue rust#87335（源：text/3137-let-else.md L1-4）
- F-rfcs-040: Summary：引入 `let PATTERN: TYPE = EXPRESSION else DIVERGING_BLOCK;` 构造（非正式名称 let-else 语句），是 if-let 表达式的对应物；匹配成功时绑定引入外围作用域，失败时必须发散（返回 `!`，如 return 或 break）；表达式有限制——不得以 `}` 结尾或仅为 LazyBooleanExpression（源：text/3137-let-else.md L9-15）
- F-rfcs-041: 文档声明本 RFC 是 2015 年 RFC（pull request 1303）中几乎相同特性的"现代化"（modernization）（源：text/3137-let-else.md L17）
- F-rfcs-042: Motivation 要点：`let else` 简化常见错误处理模式；if-let 只能在其 body 内创建绑定，导致右移漂移、过度嵌套、条件与错误路径分离；let-else 将"失败"情形移入 body 块而"成功"情形在外围上下文继续；对非 Option/Result 枚举（无 ok_or() 可用）尤其有价值（源：text/3137-let-else.md L22-39）
- F-rfcs-043: 章节结构：Summary、Motivation（Examples、A practical refactor with `match`）、Guide-level explanation、Reference-level explanations（Desugaring example）、Drawbacks（The diverging block、`let PATTERN = if {} else {} else {};`）、Rationale and alternatives（Alternatives）、Prior art、Unresolved questions（Readability in practice、Conflicts with if-let-chains、Amount of special cases、Grammar clarity）、Future possibilities（if-let-chains、Fall-back assignment、`||` in pattern-matching、let-else within if-let）（源：text/3137-let-else.md，Grep 计 23 个标题，L6-L628）

### 0160-if-let（if let 表达式）
- F-rfcs-044: 元数据：Start Date 2014-08-26；RFC PR rust-lang/rfcs#160（字段名写作 "RFC PR #"）；Rust Issue rust#16779；头部无 Feature Name 字段（源：text/0160-if-let.md L1-3）
- F-rfcs-045: Summary：引入 `if let PAT = EXPR { BODY }` 构造，允许 refutable 模式匹配而无完整 `match` 的语法与语义开销及额外右移漂移；非正式名称 "if-let statement"（源：text/0160-if-let.md L7-9）
- F-rfcs-046: Motivation 对比的两类既有写法：`match optVal { Some(x) => ..., None => {} }`（必须写 None 臂、引入两级缩进）与 `if optVal.is_some() { let x = optVal.unwrap(); ... }`（值被测试两次、unwrap 是可能失败的方法调用、需要预先存在的 let 绑定）（源：text/0160-if-let.md L26-56）
- F-rfcs-047: Detailed design：构造基于 Swift 的 if let 先例（Swift 中直接绑定 optional，本提案等价形式为 `if let Some(var) = expr`）；语法产出 `if-cond = 'let' pattern '=' expression`；条件表达式与普通 if 一样禁止尾随 braced block；编译器应对 irrefutable 模式的 if let 发出警告并建议改为普通 let；该构造可在语法 lowering pass 变换为等价 match（else 块成为 `_ => {}` 臂的 body）（源：text/0160-if-let.md L66-100）
- F-rfcs-048: 章节结构：Summary、Motivation、Detailed design（Examples）、Drawbacks、Alternatives、Unresolved questions（源：text/0160-if-let.md，Grep 计 7 个标题，L5-L221）

### 0214-while-let（while let 循环）
- F-rfcs-049: 元数据：Start Date 2014-08-27；RFC PR rust-lang/rfcs#214；Rust Issue rust#17687（源：text/0214-while-let.md L1-3）
- F-rfcs-050: Summary：引入 `while let PAT = EXPR { BODY }` 构造，允许将 refutable 模式匹配（含可选变量绑定）作为循环条件（源：text/0214-while-let.md L7-8）
- F-rfcs-051: Motivation：Swift 也支持 while let（在 if let RFC 完成后才发现，太迟未纳入）；文档给出 for 循环可映射为 `match &mut EXPR { i => { while let Some(PAT) = i.next() { BODY } } }` 的脱糖示意；支持 while let 恢复 if 与 while 两构造间的条件等价性（源：text/0214-while-let.md L12-35）
- F-rfcs-052: Detailed design：`['ident:] while let PAT = EXPR { BODY }` 脱糖为 `['ident:] loop { match EXPR { PAT => BODY, _ => break } }`；irrefutable 模式给 while let 是错误（源于脱糖后 match 出现不可达模式，此错误未来可能以向后兼容方式抑制）；以 feature gate（名为 `while_let`）引入（源：text/0214-while-let.md L39-64）
- F-rfcs-053: 章节结构：Summary、Motivation、Detailed design、Drawbacks、Alternatives、Unresolved questions（内容为 "None."）；全文 84 行（源：text/0214-while-let.md，Grep 计 6 个标题）

### 0132-ufcs（统一函数调用语法）
- F-rfcs-054: 元数据：Start Date 2014-03-17；RFC PR rust-lang/rfcs#132；Rust Issue rust#16293（源：text/0132-ufcs.md L1-3）
- F-rfcs-055: Summary 列出的三项扩展：`path::method()` 记法从固有方法扩展到 trait 方法（`T::size_of()`、`T::default()` 合法）；函数式语法从"静态方法"扩展到任何方法（静态方法与其他方法的区分被完全消除，依据 RFC PR #48 的方法查找）；引入 `<T as TraitRef>::item` 记号在一式中精确指定 trait 方法及其 receiver 类型（源：text/0132-ufcs.md L5-29）
- F-rfcs-056: Motivation 列出的三种调用形式（按显式程度递增）：`T::size_of()`（简写，仅 T 为 path 时可用）、`<T>::size_of()`（按作用域内 trait 推断，如同方法调用）、`<T as SizeOf>::size_of()`（完全无歧义）；动机场景包括多 trait 同名方法歧义、`clone()` 的精确类型指定、`Deref` 智能指针方法与指涉对象方法的区分（源：text/0132-ufcs.md L31-57）
- F-rfcs-057: Detailed design 路径语法：`TYPE_SEGMENT = '<' TYPE '>'`、`ASSOC_SEGMENT = '<' TYPE 'as' TRAIT_REFERENCE '>'`；文档指出 `ToStr::to_str`（从 trait 选择成员）与 `<ToStr>::to_str`（从类型选择成员）的细微区别，源于 trait 名同时指示类型与 trait 自身引用的双关（源：text/0132-ufcs.md L61-110）
- F-rfcs-058: 章节结构：Summary、Motivation、Detailed design（Path syntax、Normalization of path that reference types、Paths that begin with a TYPE_SEGMENT、Paths that begin with an ASSOC_SEGMENT）、Alternatives、Unresolved questions（源：text/0132-ufcs.md，Grep 计 9 个标题，L5-L191）

### 0135-where（where 子句）
- F-rfcs-059: 元数据：Start Date 2014-09-30；RFC PR rust-lang/rfcs#135；Rust Issue rust#17657（此 RFC 的 PR/Issue 字段值为完整 URL 形式）（源：text/0135-where.md L1-3）
- F-rfcs-060: Summary：添加 where 子句——在泛型项（impl、struct 定义等）声明之后指定 bounds 列表，类型参数取定值后必须证明这些 bounds；现有 bounds 记法保持为 where 子句的语法糖；示例将 `impl<K:Hash+Eq,V> HashMap<K, V>` 改写为 `impl<K,V> HashMap<K, V> where K : Hash + Eq`（源：text/0135-where.md L5-29）
- F-rfcs-061: Motivation 列出现有 bounds 语法三个局限（原文加粗）：不能表达类型参数以外的 bounds（`Option<T> : MyTrait`、`(int, T) : MyTrait` 不可写）；与关联类型配合不佳（无空间指定关联类型值）；"It's just plain hard to read"（bounds 增多后难读难排版）（源：text/0135-where.md L41-57）
- F-rfcs-062: Motivation 场景小节：Partially generic types（改编自 rustc 的 Table/Key/Value 例子：`fn example<T,K:Key<Option<T>>>(table: &Table<Option<T>, K>)` 因无法声明 `Option<T> : Value` 而编译失败）；Multidispatch traits（多分派/Haskell 多参数 type class，以 `Add` 等二元操作符 trait 为例）（源：text/0135-where.md L61-120）
- F-rfcs-063: 章节结构：Summary、Motivation（Bounds are insufficiently expressive、Associated types、Readability）、Detailed design（Where can where clauses appear?、Where clause grammar、Semantics）、Drawbacks、Alternatives（源：text/0135-where.md，Grep 计 11 个标题，L5-L420）

### 0911-const-fn（const 函数）
- F-rfcs-064: 元数据：Feature Name: const_fn；Start Date 2015-02-25；RFC PR rust-lang/rfcs#911；Rust Issue rust#24111（源：text/0911-const-fn.md L1-4）
- F-rfcs-065: Summary：允许将自由函数与固有方法标记为 `const`，使其可在常量上下文中以常量参数调用（源：text/0911-const-fn.md L8-9）
- F-rfcs-066: Motivation 要点：`UnsafeCell` 的公有字段是稳定性与安全隐患（static 初始化 atomics/mutexes 的需要迫使字段公有）；`AtomicPtr<T>`、`Cell<T>` 完全无法在常量上下文初始化；移除 `static mut` 的 pre-RFC 获正面反馈但有前提条件（抽象可在 const 与 static 项中创建使用）；`size_of` 等 intrinsic 用于常量表达式（源：text/0911-const-fn.md L13-46）
- F-rfcs-067: 文档明确声明："This RFC explicitly does not introduce a general CTFE mechanism. In particular, conditional branching and virtual dispatch are still not supported in constant expressions"（源：text/0911-const-fn.md L57-60）
- F-rfcs-068: 设计约束：traits、trait 实现及其方法不能是 const；参数仅允许简单按值绑定（`x: T`）；函数体按 const 块检查；文档列出的 const 表达式集合——原始字面量、ADT（元组/数组/结构/枚举变体）、原始类型一元/二元操作、casts、字段访问/索引、无捕获闭包、引用与块（仅 item 语句加尾表达式）；无副作用（赋值、非 const 函数调用、inline assembly）；实现 `Drop` 的类型不允许构造 struct/enum 值（不传递生效）（源：text/0911-const-fn.md L83-110）
- F-rfcs-069: 章节结构：Summary、Motivation、Detailed design、Drawbacks、Alternatives、Unresolved questions、History、Updates since being accepted（源：text/0911-const-fn.md，Grep 计 8 个标题，L6-L240）

### 1444-union（union 类型）
- F-rfcs-070: 元数据：Feature Name: `union`；Start Date 2015-12-29；RFC PR rust-lang/rfcs#1444；Rust Issue rust#32836；头部含注记 "Note: This RFC has been partially superseded by `unions-and-drop`"（源：text/1444-union.md L1-13）
- F-rfcs-071: Summary：提供 C 兼容 union 的原生支持，经新的"上下文关键字"（contextual keyword）`union` 定义，不破坏现有将 `union` 用作标识符的代码（源：text/1444-union.md L9-11）
- F-rfcs-072: Motivation：许多 FFI 接口含 union，当前须定义多个 struct 并经 `std::mem::transmute` 转换，须小心平台特定的 size 与 alignment；文档记载 Niko Matsakis 的实验证明以此方式识别 `union` 在 Rust 语法中零冲突（zero conflicts）；安全表述："To preserve memory safety, accesses to union fields may only occur in unsafe code"（源：text/1444-union.md L18-42）
- F-rfcs-073: 设计要点：union 声明使用与 struct 相同的字段声明语法；默认布局未指定，`#[repr(C)]` 下与等价 C union 布局相同；union 必须至少一个字段（空声明为语法错误）；实例化必须恰好指定一个字段（多字段为编译错误）；安全代码可实例化 union（不安全行为仅在访问字段时发生）；读写字段均在 unsafe 代码中进行（点语法与 struct 相同）（源：text/1444-union.md L47-110）
- F-rfcs-074: 章节结构：Summary、Motivation、Detailed design（Declaring a union type、Contextual keyword、Instantiating a union、Reading fields、Writing fields、Pattern matching、Borrowing union fields、Union and field visibility、Uninitialized unions、Unions and traits、Generic unions、Unions and undefined behavior、Union size and alignment）、Drawbacks、Alternatives、Unresolved questions、Edit History（源：text/1444-union.md，Grep 计 20 个标题，L6-L424）

### 0401-coercions（类型强制转换）
- F-rfcs-075: 元数据：Start Date 2014-10-30；RFC PR rust-lang/rfcs#401；Rust Issue rust#18469（源：text/0401-coercions.md L1-3）
- F-rfcs-076: Summary 四项：描述 Rust 中可用的各类类型转换并建议若干调整；提供智能指针参与 DST 强制系统的机制；改革函数到闭包的强制；`transmute` intrinsic 及其他 unsafe 转换方法不在本 RFC 覆盖范围（源：text/0401-coercions.md L5-15）
- F-rfcs-077: 转换分类：subtyping 与 coercion 隐式无语法，casting 显式（`e as U`）；转换与类型相等按强度构成全序——`T == U` 则 T 是 U 的子类型，T 是 U 的子类型则 T 强制到 U，T 强制到 U 则 T 可 cast 到 U；另有 receiver 表达式隐式强制一类不在此全序中（源：text/0401-coercions.md L30-50）
- F-rfcs-078: 强制点（coercion sites）基础情形清单：带显式类型的 `let` 语句、statics 与 consts、函数调用的实参位置、struct/variant 字段实例化、函数结果（块尾非分号表达式或 return 语句中的表达式）；强制传播表达式：数组字面量、重复语法数组、元组、box 表达式、括号子表达式（源：text/0401-coercions.md L66-109）
- F-rfcs-079: 章节结构：Summary、Motivation、Detailed design（Subtyping、Coercions、Coercions of receiver expressions、Casts、Function type polymorphism、Changes required）、Drawbacks、Alternatives、Amendments、Unresolved questions（源：text/0401-coercions.md，Grep 计 13 个标题，L5-L452）

### 0221-panic（panic 术语重命名）
- F-rfcs-080: 元数据：Start Date 2014-09-23；RFC PR rust-lang/rfcs#221；Rust Issue rust#17489（源：text/0221-panic.md L1-3）
- F-rfcs-081: Summary：将 "task failure" 重命名为 "task panic"，`fail!` 重命名为 `panic!`（源：text/0221-panic.md L7）
- F-rfcs-082: Detailed design 术语三分：可用 "failure" 指产生 `Err` 或 `None` 的操作、"panic" 指任务级 unwinding、"abort" 指中止整个进程；`panic` 选择的出处为 discuss 线程与 workweek 讨论（均附链接），语言先例为 Go，词源可溯至 Kernel panics（源：text/0221-panic.md L27-46）
- F-rfcs-083: Alternatives 列出的备选关键字：`throw!`/`unwind!（暗示通用异常处理、强调机制而非策略）`、`abort!`（与进程 abort 歧义）、`die!`（不明显什么被杀死）；Drawbacks 节指出 "panic" 一词略不正式且改名工作量大（源：text/0221-panic.md L48-67）
- F-rfcs-084: 章节结构：Summary、Motivation、Detailed design、Drawbacks、Alternatives——5 个二级章节的短文档（源：text/0221-panic.md，Grep 计 5 个标题）

### 1859-try-trait（Try trait）
- F-rfcs-085: 元数据：Feature Name: `try_trait`；Start Date 2017-01-19；RFC PR rust-lang/rfcs#1859；Rust Issue rust#31436（源：text/1859-try-trait.md L1-4）
- F-rfcs-086: Summary：引入 trait `Try`，定制 `?` 操作符应用于 `Result` 以外类型时的行为（源：text/1859-try-trait.md L9-10）
- F-rfcs-087: Motivation：`try_opt!` 宏的存在与流行印证 `Option` 等类型上的类似模式；RFC 总体目标是让 rustfmt 中 `try_opt!(width.checked_sub(...))` 这类行写成 `width.checked_sub(...)?`；futures 的三态（成功结果/"not ready yet"/错误）以 `enum Poll<T, E> { Ready(T), NotReady, Error(E) }` 表达后可将 `try_ready!(self.stream.poll())` 替换为 `self.stream.poll()?`（源：text/1859-try-trait.md L15-72）
- F-rfcs-088: Motivation 记载的既有转换行为：现有 `try!` 宏与 `?` 操作符已允许错误侧经 `From` trait 的类型转换（`F: From<E>`，错误时返回 `F::from(err)`），示例为把多种错误上转到公共错误类型如 `Box<Error>`（源：text/1859-try-trait.md L74-84）
- F-rfcs-089: 章节结构：Summary、Motivation（Using `?` with types other than `Result`、Support interconversion, but with caution）、Detailed design（Playground、Desugaring and the `Try` trait、Initial impls、Interaction with type inference）、How We Teach This（Where and how to document it、Error messages）、Drawbacks、Alternatives（The "essentialist" approach、Traits implemented over higher-kinded types、What to name the trait）、Unresolved questions（源：text/1859-try-trait.md，Grep 计 18 个标题，L6-L488）

### 2388-try-expr（try 关键字与 try 表达式）
- F-rfcs-090: 元数据：Feature Name: `try_expr`；Start Date 2018-04-04；RFC PR rust-lang/rfcs#2388；Rust Issue rust#50412（源：text/2388-try-expr.md L1-4）
- F-rfcs-091: Summary 三项决定：在 edition 2018 保留 `try` 为关键字；将 `do catch { .. }` 替换为 `try { .. }`；不保留 `catch` 为关键字；本 RFC 解决 RFC 243（trait-based-exception-handling）遗留的 `catch { .. }` 表达式关键字选择问题（源：text/2388-try-expr.md L9-16）
- F-rfcs-092: Motivation 论证：所选关键字不能是 contextual 的——语法形式 `<word> { .. }` 与名为 `<word>` 的 struct 冲突；文档给出 Rust 2015 中合法的 `struct try; fn main() { try {}; }` 代码示例及 `warning: type 'try' should have a camel case name` 警告（该警告降低生态中存在名为 try 的类型的概率）（源：text/2388-try-expr.md L28-55）
- F-rfcs-093: Drawbacks 三个小节：Association with exception handling（利弊兼有，引 Niko Matsakis 关于利用其他语言直觉的引文）、Breakage of the `try!` macro、Inverse semantics of `?`（源：text/2388-try-expr.md L87-171）
- F-rfcs-094: Rationale and alternatives 含 8 个备选方案小节：reserving `catch`、keeping `do catch { .. }`、`do try { .. }`、using `do { .. }`、reserving `trap`、reserving `wrap`、reserving `result`、a smattering of other possible keywords；另有 Rationale for `try` 与 Review 小节（源：text/2388-try-expr.md，Grep L172-L555）
- F-rfcs-095: 章节结构：Summary、Motivation（For reserving a keyword、For reserving `try` specifically）、Guide-level explanation、Reference-level explanation、Drawbacks、Rationale and alternatives、Prior art、Unresolved questions（源：text/2388-try-expr.md，Grep 计 24 个标题，L6-L913）

### 2094-nll（非词法生命周期）
- F-rfcs-096: 元数据：Feature Name: nll；Start Date 2017-08-02；RFC PR rust-lang/rfcs#2094；Rust Issue rust#43234（源：text/2094-nll.md L1-4）
- F-rfcs-097: Summary：扩展 Rust 借用系统以支持非词法生命周期（non-lexical lifetimes）——基于控制流图而非词法作用域的生命周期；RFC 详细描述如何推断这些更灵活的 region、如何调整错误消息，并描述借用检查器的其他几项扩展，总体效果是消除许多"小型、函数局部的代码修改才能通过借用检查"的常见情形（源：text/2094-nll.md L9-17）
- F-rfcs-098: Motivation 的术语区分：lifetime 一词在文中区分两种用法——引用的 lifetime（引用被使用的代码跨度）与值的 scope（值被释放/析构函数运行前的跨度）；引用的 lifetime 不能超过所指值的 scope；文档以 `data` 向量被可变借用传给 `capitalize` 的代码示例区分两者（源：text/2094-nll.md L22-73）
- F-rfcs-099: Motivation 列出四个问题案例小节：Problem case #1: references assigned into a variable、#2: conditional control flow、#3: conditional control flow across functions、#4: mutating `&mut` references（源：text/2094-nll.md，Grep L97-L421）
- F-rfcs-100: Detailed design采用六层分层结构（小节名原文）：Layer 0: Definitions、Layer 1: Control-flow within a function、Layer 2: Avoiding infinite loops、Layer 3: Accommodating dropck、Layer 4: Named lifetimes、Layer 5: How the borrow check works（源：text/2094-nll.md，Grep L458-L1716）
- F-rfcs-101: 文档含附录小节 "Appendix: What this proposal will not fix"（列举本提案不修复的借用检查器局限）与 Endnotes；How We Teach This 含小节 Terminology、Leveraging intuition: framing errors in terms of points 等；全文二级/三级标题共 29 个（源：text/2094-nll.md，Grep L6-L2178）

### 2349-pin（Pin 与 Unpin）
- F-rfcs-102: 元数据：Feature Name: `pin`；Start Date 2018-02-19；RFC PR rust-lang/rfcs#2349；Rust Issue rust#49150（源：text/2349-pin.md L1-4）
- F-rfcs-103: Summary：向 libcore/libstd 引入新 API，作为不能安全移动的数据的安全抽象；Motivation：长期存在的问题是处理不应被移动的类型——struct 含指向自身表示的指针（自引用类型），generators 工作使该用例变得重要（generator 将栈帧具象化为对象）（源：text/2349-pin.md L9-25）
- F-rfcs-104: Guide-level explanation 核心目标原文："provide a reference type where the referent is guaranteed to never move before being dropped"，且"without *any* type system changes"；关键设计：新库类型 `Pin<'a, T>` 同时涵盖可移动与不可移动 referent，配对 auto trait `Unpin`——`T: Unpin`（默认）时 `Pin<'a, T>` 完全等价于 `&'a mut T`；`T: !Unpin` 时安全地只提供 `&'a T` 访问且保证 referent 永不被移动，获得 `&'a mut T` 访问是 unsafe 的（`mem::replace` 等可经 `&mut` 移出数据）（源：text/2349-pin.md L29-44）
- F-rfcs-105: 类型定义（Reference-level explanation）：`pub unsafe auto trait Unpin { }` 加入 `core::marker` 与 `std::marker`（是 lang item，仅为某些 generators 生成 negative impls，语义完全经库 API 实施）；`#[fundamental] pub struct Pin<'a, T: ?Sized + 'a> { data: &'a mut T }` 加入 `core::mem` 与 `std::mem`；`Pin` 实现 `Deref`，仅当 `T: Unpin` 时实现 `DerefMut`（使得 `mem::swap`/`mem::replace` 对非 Unpin 类型不可安全调用）；`PinBox<T>` 作为 `Box` 的 pinned 类比（源：text/2349-pin.md L63-110、L59）
- F-rfcs-106: 文档给出的 Future trait 新定义：`trait Future { type Item; type Error; fn poll(self: Pin<Self>, cx: &mut task::Context) -> Poll<Self::Item, Self::Error>; }`；默认实现等价于今天接受 `&mut self` 的定义，需要自引用的 future 只需退出 `Unpin`（源：text/2349-pin.md L46-57）
- F-rfcs-107: Rationale and alternatives 小节：Comparison to `?Move`、Comparison to using `unsafe` APIs、Anchor as a wrapper type and `StableDeref`、Stack pinning API (potential future extension)、Making `Pin` a built-in type (potential future extension)、Having both `Pin` and `PinMut`（源：text/2349-pin.md，Grep L276-L392）

### 2592-futures（futures API 稳定化）
- F-rfcs-108: 元数据：Feature Name: `futures_api`；Start Date 2018-11-09；RFC PR rust-lang/rfcs#2592；Rust Issue rust#59113（源：text/2592-futures.md L1-4）
- F-rfcs-109: Summary：提议稳定一等 async/await 语法的库组件——`std` 级任务系统全部 API（`std::task::*`）与核心 `Future` API（`core::future::Future` 与 `std::future::Future`）；不提议稳定 async/await 语法本身（另行单独步骤）；不覆盖 `Pin` API 的稳定化（已另行提议）；文档自述为更早 futures RFC（PR 2418）的修订精简版，后者被推迟至 nightly 获得更多经验（源：text/2592-futures.md L9-17）
- F-rfcs-110: Historical context 节的时间线：`Future` trait 起源于 futures crate，0.1 发布于 2016 年 8 月（确立 task/polling 模型核心思想）；2018 年初 futures-rfcs 修订核心 API（产出 0.2）；pinning API（PR 2349）是 "game-changer"，使跨 yield 借用无需使核心 future API 不安全；语法 RFC（PR 2394）2018 年 5 月合并而 API RFC 关闭（约定在 nightly 迭代后以稳定化 RFC 跟进，即本 RFC）；API 于 2018 年 5 月底落地 `std`（rust PR 51263）；Google Fuchsia 项目在操作系统场景大规模使用这些特性（源：text/2592-futures.md L50-73）
- F-rfcs-111: Guide-level explanation：`Future` trait 表示异步惰性计算（最终产出值而不阻塞当前线程）；`async fn read_frame(socket: &TcpStream) -> Result<Frame, io::Error>` 的签名等价于 `fn read_frame<'sock>(socket: &'sock TcpStream) -> impl Future<Output = Result<Frame, io::Error>> + 'sock`；task 比作轻量级线程，executor 从 `()`-producing `Future` 创建任务并 pin 之（源：text/2592-futures.md L79-110）
- F-rfcs-112: 章节结构：Summary、Motivation（Why `Future`s in `std`?、How does this step fit into the bigger picture?）、Historical context、Guide-level explanation、Reference-level explanation（`core::task` module、`core::future` module、Relation to futures 0.1）、Rationale, drawbacks, and alternatives（removing built-in errors、core trait design wrt `Pin`、wakeup design `Waker` 三小节）、Prior art、Unresolved questions（源：text/2592-futures.md，Grep 计 16 个标题，L6-L613）

### 1191-hir（高层中间表示）
- F-rfcs-113: 元数据：Feature Name: N/A；Start Date 2015-07-06；RFC PR rust-lang/rfcs#1191；Rust Issue: N/A（源：text/1191-hir.md L1-4）
- F-rfcs-114: Summary：向编译器添加高层中间表示（HIR）——"basically a new (and additional) AST more suited for use by the compiler"；文档声明这是纯编译器实现细节、对语言无影响，且添加 HIR 不排除未来添加 MIR 或 LIR（源：text/1191-hir.md L9-15）
- F-rfcs-115: Motivation：把当时同时服务于 libsyntax、编译器与语法扩展的 AST 拆分为 libsyntax 版本（语法操作，最终稳定供语法扩展与工具使用）与完全编译器内部的 HIR；语言构造的语法扩展（如 `for` 循环、`if let`）从 AST 操作移到 AST→HIR lowering 步骤；lifetime elision 也拟移入 lowering（源：text/1191-hir.md L20-40）
- F-rfcs-116: Detailed design：初始 HIR 将是（几乎）与 AST 相同的副本，lowering 步骤仅为复制操作；macros、`for` 循环等已在 libsyntax 中展开的构造不属于 HIR；Alternatives：维持现状，或跳过 HIR 直接 lower 到 MIR（更复杂的重构且错失稳定 AST 供工具与语法扩展使用的好处）（源：text/1191-hir.md L43-72）
- F-rfcs-117: 章节结构：Summary、Motivation、Detailed design、Drawbacks、Alternatives、Unresolved questions——6 个二级章节（源：text/1191-hir.md，Grep L7-L75）

### 1211-mir（中层中间表示）
- F-rfcs-118: 元数据：Feature Name: N/A；Start Date 2015-07-14；RFC PR rust-lang/rfcs#1211；Rust Issue rust#27840（源：text/1211-mir.md L1-4）
- F-rfcs-119: Summary：向编译器引入"中层 IR"（MIR）；MIR 脱糖（desugars）大部分 Rust 表面表示，留下适合类型检查与翻译的更简单形式；文档描述 MIR "radically simpler"——不含 "match" 语句，将 `ref` 绑定与 `&` 表达式转换为单一形式（源：text/1211-mir.md L8-23）
- F-rfcs-120: Motivation 六点（原文编号）：1. 编译器复杂度增加（所有 pass 须针对完整 Rust 语言编写；闭包/for 循环/if let/while let/box 表达式/重载操作符/方法调用等脱糖示例；box patterns 与非词法生命周期在当前表示下几乎不可实现）；2. AST 上推理细粒度控制流困难（MIR 基于 CFG）；3. 安全分析可靠性降低（分析对象 AST 与执行对象 bitcode 差距大）；4. 安全证明可靠性（MIR 足够简单，最终可基于 MIR 本身做证明）；5. Rust 特定优化有挑战（可在翻译到 bitcode 前于 MIR 上优化）；6. 脱离 LLVM 迁移几乎不可能（Rust 语义嵌入在 trans 步骤，MIR 设计下语义改由 AST→MIR 翻译描述）（源：text/1211-mir.md L14-81）
- F-rfcs-121: Motivation 列出编译器中现有模拟 MIR 效果的三种结构：Adjustments（类型检查器计算、后续分析读取）、CFG（建于 AST 之上，仅是控制流近似）、`ExprUseVisitor`（与 CFG 配合，向安全分析回调 borrow/move 等动作，"effectively a kind of MIR, but it is not complete enough to do translation"）（源：text/1211-mir.md L83-116）
- F-rfcs-122: Detailed design 小节（14 个）：What is *really* being proposed here?、Prototype、Overview of the MIR、Assignments, values, and rvalues、Constants、Aggregates and further lowering、Bounds checking、Overflow checking、Matches、Drops、Shallow drops and Box、Phasing、Representing scopes、Monomorphization、Unchecked assertions（源：text/1211-mir.md，Grep L183-L716）
- F-rfcs-123: 全文二级/三级标题共 23 个，从 Summary 到 Unresolved questions；Motivation 下另含 Goals 与 Which analyses are well-suited to the MIR? 两个小节（源：text/1211-mir.md，Grep L6-L800）

### 3192-dyno（基于类型的数据访问）
- F-rfcs-124: 元数据：Feature Name: `provide_any`；Start Date 2021-11-04；RFC PR rust-lang/rfcs#3192；Rust Issue rust#96024（源：text/3192-dyno.md L1-4）
- F-rfcs-125: 文档头部有专节声明（标题原文）："This RFC was previously approved, but part of it later **rejected**"——`Provider` 接口被 libs team 会议拒绝；剩余部分为 `Demand` 类型（在 rust PR 113464 中重命名为 `Request`）；由于 `error_generic_member_access` 是当时唯一已知使用 `Demand`/`Request` 的特性，决定由该特性跟踪并将本 RFC 标记为 rejected for now（源：text/3192-dyno.md L6-12）
- F-rfcs-126: Summary：提议扩展核心库 `any` 模块，提供对象按类型访问数据的通用 API（与既有类型驱动 downcast API 相对，本扩展将 downcast 集成进数据访问）；示例：`let s: String = object.request();`、`let s = object.request_field::<str>();`（源：text/3192-dyno.md L14-27）
- F-rfcs-127: Notes 节：主要动机是 `Error` trait 的 'generic member access'（此前由 RFC 2895 提议，本 RFC 以 Error 为驱动示例但明确不提议修改 Error）；概念验证实现在 nrc/provide-any；本工作改编自 mystor/dyno；早期迭代暴露的 type tags 概念仍用于实现但不再暴露于 API（源：text/3192-dyno.md L29-34）
- F-rfcs-128: 章节结构：头部拒绝声明节、Summary（Notes）、Motivation、Guide-level explanation、Reference-level explanation（Demand）、Drawbacks、Rationale and alternatives、Prior art、Unresolved questions、Future possibilities、Appendix 1: using newtypes、Appendix 2: plugin example（源：text/3192-dyno.md，Grep 计 14 个标题，L6-L236）

### 2052-epochs（Rust Edition 机制）
- F-rfcs-129: 元数据：Feature Name: N/A；Start Date 2017-06-26；RFC PR rust-lang/rfcs#2052；Rust Issue rust#44581（源：text/2052-epochs.md L1-4）
- F-rfcs-130: Summary：提议每两到三年声明一个 edition；edition 以发生年份命名，代表多项要素汇聚的发布：自上一 edition 以来稳定的一组显著连贯的新特性与 API、围绕这些特性的错误消息与用户体验的完全打磨、工具（IDE/rustfmt/Clippy 等）更新、新特性指南、书的更新、标准库与核心生态 crate 更新、Rust Cookbook 新版（源：text/2052-epochs.md L9-18）
- F-rfcs-131: 向后兼容机制表述：需要向后不兼容变更的功能（如引入新关键字）只能通过显式选择（opting in）新 edition 获得；现有代码继续编译；使用不同 edition 的 crate 可自由混合作依赖（源：text/2052-epochs.md L20）
- F-rfcs-132: Motivation 记录的现状三机制：nightly/stable 发布通道分裂、快速（六周）发布过程、弃用（Deprecation）；三个缺口：演化故事缺乏清晰"章节"（chapters）、缺乏社区集结点（rallying points）、角落案例的破坏性变更（例证：`catch` 关键字因不能加入而被迫写成 `do catch` 语法）（源：text/2052-epochs.md L25-89）
- F-rfcs-133: 章节结构：Summary、Motivation（The status quo、What's missing）、Detailed design（The basic idea、Edition timing, stabilizations, and the roadmap process、A broad policy on edition changes、The full mechanics）、How We Teach This、Drawbacks、Alternatives（Within the basic edition structure、Alternatives to editions）、Unresolved questions（源：text/2052-epochs.md，Grep 计 15 个标题，L6-L538）

### 1044-io-fs-2.1（std::fs 扩展）
- F-rfcs-134: 元数据：Feature Name: `fs2`；Start Date 2015-04-04；RFC PR rust-lang/rfcs#1044；Rust Issue rust#24796（源：text/1044-io-fs-2.1.md L1-4）
- F-rfcs-135: Summary：扩展 `std::fs` 模块的范围——增强既有功能、暴露底层表示、添加少量新函数；Motivation 列出当时 stable Rust 不可用的操作：检查文件修改/访问时间、读取 `libc::stat` 类低层信息、检查 unix 权限位、整体设置权限位、利用 `DirEntry` 额外元数据、读取 symlink 本身的元数据、解析路径中全部 symlink（源：text/1044-io-fs-2.1.md L8-23）
- F-rfcs-136: Non-goals 节明确排除：增强 `copy` 支持递归目录复制或复制配置、增强或稳定化 `walk`、临时文件或目录（留待未来 RFC）（源：text/1044-io-fs-2.1.md L32-41）
- F-rfcs-137: os 模块组织愿景（Lowering APIs 节）：层级 `os/unix/{io,fs,net,env,process,...}`、`os/linux/...`、`os/macos/...`、`os/windows/...`；平台特定 API 仅在 `std::os` 层级提供；文档声明 `std::os::*` 模块的目标不是绑定各平台全部系统 API（留给外部 crate），而是 1. 经 "lowering"（如 `AsRawFd` 扩展 trait 从 `File`/`TcpStream` 等 std 类型提取底层表示）促进互操作，2. 提供高级但平台特定、风格与 std 其余部分一致的 API（源：text/1044-io-fs-2.1.md L51-110）
- F-rfcs-138: 章节结构：Summary、Motivation（Non-goals of this RFC）、Detailed design（Lowering APIs、Constructing `Permissions`、Creating directories with permissions、Adding `FileType`、Enhancing symlink support、Binding `realpath`、Tweaking `PathExt`、Expanding `DirEntry`）、Drawbacks、Alternatives、Unresolved questions（源：text/1044-io-fs-2.1.md，Grep 计 15 个标题，L6-L555）

### 3128-io-safety（I/O 安全）
- F-rfcs-139: 元数据：Feature Name: `io_safety`；Start Date 2021-05-24；RFC PR rust-lang/rfcs#3128；Rust Issue rust#87074（源：text/3128-io-safety.md L1-4）
- F-rfcs-140: Summary：通过引入 I/O 安全（I/O safety）概念与一组新类型和 trait，为 `AsRawFd` 及相关 trait 的用户提供关于原始资源句柄的保证，以此关闭 Rust 封装边界（encapsulation boundaries）的漏洞（源：text/3128-io-safety.md L9-11）
- F-rfcs-141: Motivation 漏洞描述：`FromRawFd::from_raw_fd` 是 unsafe 的（阻止 `File::from_raw_fd(7)`），但 `AsRawFd` 不限制 `as_raw_fd` 的返回值——`pub fn do_some_io<FD: AsRawFd>(input: &FD)` 可对任意 `RawFd` 做 I/O，`do_some_io(&7)` 甚至合法（`RawFd` 自身实现 `AsRawFd`）；特殊情况下违反 I/O 安全可导致违反内存安全（`memfd_create` + `mmap` 安全包装例）；RFC 引入内容：I/O 安全概念文档、新类型与 trait 集、`from_raw_fd`/`from_raw_handle`/`from_raw_socket` 的新文档（源：text/3128-io-safety.md L16-59）
- F-rfcs-142: I/O 安全概念的类比表述（原文）："Protection from raw pointer hazards is called memory safety, so protection from raw handle hazards is called *I/O safety*"；raw handle 类比 raw pointer——获取（obtain）安全、使用（用于 I/O）可能出危险（源：text/3128-io-safety.md L66-82）
- F-rfcs-143: 引入的 API（Guide-level explanation 小节名）：`OwnedFd` 与 `BorrowedFd<'fd>` 类型；`AsFd`、`Into<OwnedFd>`、`From<OwnedFd>` trait；另有 Gradual adoption（渐进采纳）小节；Rationale and alternatives 含三个小节：Concerning "unsafe is for memory safety"、I/O Handles as plain data、The `IoSafe` trait (and `OwnsRaw` before it)（源：text/3128-io-safety.md L135-L327）
- F-rfcs-144: 章节结构：Summary、Motivation、Guide-level explanation、Reference-level explanation（各 4 小节）、Drawbacks、Rationale and alternatives、Prior art、Unresolved questions（Formalizing ownership）、Future possibilities、Thanks（源：text/3128-io-safety.md，Grep 计 22 个标题，L6-L410）

### 1506-adt-kinds（ADT 种类模型）
- F-rfcs-145: 元数据：Feature Name: clarified_adt_kinds；Start Date 2016-02-07；RFC PR rust-lang/rfcs#1506；Rust Issue rust#35626（源：text/1506-adt-kinds.md L1-4）
- F-rfcs-146: Summary 三项：提供描述 struct 与 variant 三种类别及其关系的简单模型；提供不分类别匹配 struct/variant 的模式方式（`S{..}`）；允许零字段的 tuple struct 与 tuple variant（`TS()`）；Motivation 自述"This RFC can also serve as a piece of documentation"（源：text/1506-adt-kinds.md L9-20）
- F-rfcs-147: 三种类别定义：Braced structs（0 或多用户命名字段，仅在类型命名空间定义，支持 FRU 与 struct 模式）；Unit structs（可视为 `struct US {}` 与 `const US: US = US{}` 的单一声明，同时定义于类型命名空间与值命名空间）；Tuple structs（可视为带编号字段 `0: Type0` 的基本 struct 与同名构造器函数的单一声明）（源：text/1506-adt-kinds.md L28-110）
- F-rfcs-148: 章节结构：Summary、Motivation、Detailed design（Braced structs、Unit structs、Tuple structs、Summary of the changes.）、Drawbacks、Alternatives、Unresolved questions（源：text/1506-adt-kinds.md，Grep 计 10 个标题，L6-L178）

### 0953-op-assign（复合赋值 trait）
- F-rfcs-149: 元数据：Feature Name: op_assign；Start Date 2015-03-08；RFC PR rust-lang/rfcs#953；Rust Issue rust#28235（源：text/0953-op-assign.md L1-4）
- F-rfcs-150: Summary：添加 `[Op]Assign` trait 族允许重载 `a += b` 类赋值操作；Motivation：已允许重载二元操作，赋值版本是下一步；该语法糖使数学库更易接受（源：text/0953-op-assign.md L8-15）
- F-rfcs-151: trait 清单（添加到 libcore 并在 libstd re-export，初始 unstable，共 10 个）：`AddAssign`（`+=`，带 `#[lang = "add_assign"]`）、`BitAndAssign`（`&=`）、`BitOrAssign`（`|=`）、`BitXorAssign`（`^=`）、`DivAssign`（`/=`）、`MulAssign`（`*=`）、`RemAssign`（`%=`）、`ShlAssign`（`<<=`）、`ShrAssign`（`>>=`）、`SubAssign`（`-=`）；签名模式 `trait AddAssign<Rhs=Self> { fn add_assign(&mut self, Rhs); }`（源：text/0953-op-assign.md L19-39）
- F-rfcs-152: 实现约束：原始数值类型的实现不含重载（仅 `impl AddAssign<i32> for i32` 类同型实现）；添加 `op_assign` feature gate，未启用时编译器维持 `a`/`b` 必须同类型原语的原有检查；稳定化可在 1.0 后进行（向后兼容变更）（源：text/0953-op-assign.md L41-51）
- F-rfcs-153: Unresolved questions 两条：是否为 `ShlAssign`/`ShrAssign` 重载（如 `impl ShlAssign<u8> for i32`，因 `Shl`/`Shr` 已重载）；是否为引用重载（如 `impl<'a> AddAssign<&'a i32> for i32` 以允许 `x += &0;`）；Drawbacks 节内容为 "None that I can think of."（源：text/0953-op-assign.md L70-89）

### 0048-traits（trait 系统清理）
- F-rfcs-154: 元数据：Start Date 2014-06-10；RFC PR rust-lang/rfcs#48；Rust Issue rust#5527（源：text/0048-traits.md L1-3）
- F-rfcs-155: Summary 四项变更：泛化显式 self 类型至 `&self`/`&mut self` 之外（使 `self: Rc<Self>` 类声明成为可能）；扩展 coherence 规则以递归操作并更仔细区分孤儿（orphans）；将 vtable 解析算法修订为渐进式（gradual）；以 vtable 解析表述方法解析算法；本 RFC 排除关联类型与多维 type class（留作后续 RFC 主题）（源：text/0048-traits.md L7-19）
- F-rfcs-156: Motivation 开篇表述："The current trait system is ill-specified and inadequate. Its implementation dates from a rather different language."；Use cases 各小节带 "*Addressed by:*" 标注（Poor interaction with overloadable deref and index → New method resolution algorithm；Lack of backtracking → New method resolution algorithm；Overly conservative coherence → Expanded coherence rules）（源：text/0048-traits.md L23-110）
- F-rfcs-157: 章节结构：Summary、Motivation（Use cases、Properties）、Detailed design（Method self-type syntax、Coherence、Method resolution、Interaction with vtables and type inference、Ensuring crate concatenation）、Implementation details（The "resolve" algorithm）、Alternatives and downsides（Autoderef and ambiguity）、Footnotes（源：text/0048-traits.md，Grep 计 15 个标题，L5-L708）

### 0050-assert（debug_assert 宏）
- F-rfcs-158: 元数据：Start Date 2014-04-18；RFC PR rust-lang/rfcs#50；Rust Issue rust#13789（源：text/0050-assert.md L1-3）
- F-rfcs-159: Summary：断言对 release 构建太昂贵且妨碍内联（mess up inlining），必须有办法关闭；提议宏 `debug_assert!` 与 `assert!`；测试用例应使用 `assert!`（源：text/0050-assert.md L5-7）
- F-rfcs-160: Detailed design：debug 构建中（无 `--cfg ndebug`）`debug_assert!()` 与 `assert!()` 相同；release 构建中（`--cfg ndebug`）`debug_assert!()` 编译为空；`assert!()` 的定义为 `if (!EXPR) { fail!("assertion failed ({}, {}): {}", file!(), line!(), stringify!(expr) }`（源：text/0050-assert.md L15）
- F-rfcs-161: 章节结构：Summary、Motivation、Detailed design、Alternatives、Unresolved questions（内容 "None."）；全文 25 行，5 个二级章节（源：text/0050-assert.md，Grep L5-L25）

### 0342-keywords（保留关键字）
- F-rfcs-162: 元数据：Start Date 2014-10-07；RFC PR rust-lang/rfcs#342；Rust Issue rust#17862（源：text/0342-keywords.md L1-3）
- F-rfcs-163: Summary：保留 `abstract`、`final`、`override` 为可能的关键字；Motivation：意图为 Rust 添加更高效的继承机制（引用 RFC PR #245、#250 及 discuss 线程），任何实现都可能使用 `virtual`（已使用、保持保留）、`abstract`、`final`、`override`；Detailed design 全文："Make `abstract`, `final`, and `override` reserved keywords."（源：text/0342-keywords.md L7-22）
- F-rfcs-164: 章节结构：Summary、Motivation、Detailed design、Drawbacks、Alternatives、Unresolved questions（内容 "N/A"）；全文 35 行，6 个二级章节（源：text/0342-keywords.md，Grep L5-L35）

## C. 目录统计与抽样

### 目录统计
- F-rfcs-165: `text/` 目录顶层 `.md` 文件共 639 个；递归（含子目录）`.md` 文件共 648 个（源：text/ 目录 PowerShell Get-ChildItem 计数，2026-08-28 实测）
- F-rfcs-166: `text/` 下存在 3 个子目录：`2856-project-groups`、`3392-leadership-council`、`3606-temporary-lifetimes-in-tail-expressions`（与 generate-book.py 文档化的多章节 RFC 子目录布局一致）（源：text/ 目录列表）
- F-rfcs-167: 文件编号范围：按文件名排序最小为 `0001-private-fields.md`，最大为 `3984-libs-team-refactor.md`（源：text/ 目录排序）
- F-rfcs-168: 命名模式为 4 位零填充编号 + 连字符 + 小写 kebab-case 描述名（如 `3137-let-else.md`、`0135-where.md`、`0953-op-assign.md`）；部分文件名含下划线或点（如 `0001-private-fields.md` 同级存在 `2592-futures.md`、`1506-adt-kinds.md` 等，编号统一 4 位）（源：text/ 文件列表）
- F-rfcs-169: 仓库（排除 `.git/`）总文件数 665；根目录文件：README.md、0000-template.md、book.toml、generate-book.py、compiler_changes.md、lang_changes.md、libs_changes.md、LICENSE-APACHE、LICENSE-MIT、.gitattributes、.gitignore、renovate.json5；另有 .github/（PULL_REQUEST_TEMPLATE.md、workflows/deploy.yml）（源：仓库根目录列表与 Get-ChildItem 计数）
- F-rfcs-170: 头部格式演变（可验证对比）：2014 年 RFC（0114/0160/0132/0214 等）头部仅 Start Date/RFC PR/Rust Issue 三字段且无锚点链接定义；2015-02 起的 RFC（0911）增加 Feature Name 字段；较晚的 RFC（3137 等）章节头带 `[summary]: #summary` 式锚点链接定义（源：对比 text/0114-closures.md L1-3、text/0911-const-fn.md L1-4、text/3137-let-else.md L6-7、text/0214-while-let.md L5）

### 抽样浏览（未列入精读清单的 RFC，仅记录标题要点与状态）
- F-rfcs-171: `0002-rfc-process.md`：Start Date 2014-03-11；RFC PR 链接两个（rust-lang/rfcs#2 与 #6）；Rust Issue: N/A；内容为 RFC 流程本身的定义——"provide a consistent and controlled path for new features to enter the language and standard libraries"（源：text/0002-rfc-process.md L1-10）
- F-rfcs-172: `0243-trait-based-exception-handling.md`：头部字段为 Feature-gates: `question_mark`, `try_catch`；Start Date 2014-09-16；Rust Issue rust#31436（与 RFC 1859 同一 issue）；提议添加 `?` 操作符与 `catch { ... }` 表达式；`?` 操作符想法源自 RFC PR 204（@aturon）（源：text/0243-trait-based-exception-handling.md L1-22）
- F-rfcs-173: `2394-async_await.md`：Feature Name: async_await；Start Date 2018-03-30；Rust Issues 两个（rust#50547、rust#62290 `#!feature(async_closure)`）；提议添加 async 与 await 语法；文档内嵌指向 companion RFC 的相对链接 `2592-futures.md`（源：text/2394-async_await.md L1-14）
- F-rfcs-174: `3984-libs-team-refactor.md`（目录中编号最大的 RFC）：Feature Name: N/A；Start Date 2026-07-15；Rust Issue: N/A；提议重新组织库团队——重定义并重命名成员资格类别、改变团队成员选择方式、文档化成员与维护者期望、定义团队的 FCP 处理方式；Motivation 引用 team 仓库 PR 588（2021 年设定的现有结构）（源：text/3984-libs-team-refactor.md L1-27）
- F-rfcs-175: `1522-conservative-impl-trait.md`：Feature Name: conservative_impl_trait；Start Date 2016-01-31；Rust Issue rust#34511；提议保守形式的抽象返回类型（impl Trait），初始限制为仅自由函数或固有函数、仅函数返回类型位置（源：text/1522-conservative-impl-trait.md L1-14）
- F-rfcs-176: `2497-if-let-chains.md`：Feature Name: `let_chains_2`；Start Date 2018-07-13；头部含两个 Rust Issue 链接（rust#53667、rust#53668）；提议扩展 if let 与 while let 表达式的链式写法，示例以 `&&` 连接多个 `let` 与 bool 条件（源：text/2497-if-let-chains.md L1-12）
- F-rfcs-177: `2195-really-tagged-unions.md`：Feature Name: really_tagged_unions；Start Date 2017-10-30；Rust Issue: N/A；提议形式化定义 enum 的 `#[repr(u32, i8, etc..)]` 与 `#[repr(C)]` 属性以强制非 C-like enum 拥有定义布局（动机含 Firefox 开发中的两个例子）（源：text/2195-really-tagged-unions.md L1-15）

---

## 采集统计
- 事实总数：177 条（A 流程与模板 33 条；B 精读 RFC 106 条；C 目录统计与抽样 13 条）
- 精读 RFC：26 篇（每篇 3-6 条事实）
- 抽样浏览：7 篇（0002、0243、2394、3984、1522、2497、2195）
- 目录统计：text/ 顶层 639 个 .md、含 3 个子目录递归 648 个；编号范围 0001-3984；仓库总文件（排除 .git）665 个
