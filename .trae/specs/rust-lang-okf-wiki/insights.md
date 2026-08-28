---
source:
  - .trae/specs/rust-lang-okf-wiki/facts-rust.md（133 条，rust-lang/rust main @ e457a7b0，2026-08-27）
  - .trae/specs/rust-lang-okf-wiki/facts-cargo.md（144 条，rust-lang/cargo master @ 75d17360，2026-08-26）
  - .trae/specs/rust-lang-okf-wiki/facts-rfcs.md（177 条，rust-lang/rfcs master @ 354518a8，2026-08-15）
stage: I（架构洞察，G2 质量门）
next: E（按第二部分知识地图生成三 bundle 概念文档）
---

# insights.md — rust-lang 三仓库架构洞察与知识地图

> 铁律遵循：本文全部论断与规划仅锚定三份事实清单中的编号（F-rust-xxx / F-cargo-xxx / F-rfcs-xxx），不引入清单之外的 API、路径或结论。行号均为采集时快照。

---

## 第一部分：核心洞察（每仓库 4 条，共 12 条四元组）

### rust-lang/rust（4 条）

#### R1. 单仓库、双 workspace、三世界：编译器 70 个 crate、标准库 23 个目录、工具 46 个目录分属不同构建域，版本号由 `src/version` 单行文件承载

- **陈述**：rust-lang/rust 用根 Cargo.toml workspace（`resolver = "2"`）编组 `compiler/rustc` + 69 个 `rustc_*` crate 与 34 个 `src/tools/*` 成员；`library/` 是第二个独立 workspace（`resolver = "1"`）；当前版本 `1.100.0` 记录在 `src/version` 单行文件（而非任何 Cargo.toml）中，构成 bootstrap 与发行链的版本真源。
- **证据**：F-rust-005（根 workspace members 与 resolver="2"）、F-rust-010（compiler/ 含 70 个子目录：rustc 壳 + 69 个 rustc_* crate）、F-rust-097（library 独立 workspace，resolver="1"，exclude stdarch/windows_link）、F-rust-008（src/version 内容为单行 `1.100.0`）。
- **反常识**：三个通行认知被打破：①「一个仓库 = 一个 workspace」——实际双 workspace 并存，且 cranelift/gcc 后端、`build/`、`src/bootstrap` 等 6 项被根 workspace 显式 exclude（F-rust-006）；②「版本号在 Cargo.toml」——实际在 `src/version` 单行文件，供构建系统读取；③「tools 目录都参与主构建」——磁盘 46 个 tools 目录只有 34 个是 workspace 成员，rust-analyzer 等外部维护工具自带独立 Cargo.toml/AGENTS.md（F-rust-130、F-rust-131）。连测试专用 crate 也有 `opt-level = 3` 的性能调优（F-rust-013），仓库的构建拓扑远比「一个大 crate」精细。
- **行动**：读者的第一张地图必须是「仓库解剖图」：根 workspace / library workspace / exclude 区三个圈层 + 70-crate 联邦 + 46/34 工具差集；读任何源码前先判定目标属于哪个构建域，查版本一律看 `src/version`。

#### R2. 三阶段自举的「蛇吞尾」：构建从不信任本机工具链，起点是 `src/stage0` 锁定的固定哈希 beta 编译器（2026-08-18）

- **陈述**：`x.py` 自述只是 bootstrap.py 的「symlink」，bootstrap 本身是一个 Rust crate（三个 bin：bootstrap/rustc/rustdoc）；构建从 CI 下载的 stage0 **beta** 编译器起步——stage0 编译器与标准库构建 stage1，stage1 再产出 stage2；当前 stage0 为 2026-08-18 的 beta（commit `f47d5bb1…`），由 `src/stage0` 以 sha256 清单锁定。
- **证据**：F-rust-026（src/stage0：`compiler_date=2026-08-18`、`compiler_version=beta`、commit hash 与 manifest hash）、F-rust-029（README 三阶段构建：stage0 下载 → stage1 → stage2）、F-rust-022（bootstrap 的 `Compiler` 身份仅 stage+host 两字段，Hash/PartialEq 只用这两字段）、F-rust-016（cc/cmake 以 `=1.2.62`/`=0.1.54` 精确锁版）。
- **反常识**：直觉是「先装 rustc 再 make」或「构建脚本是 Python」；实际本机 rustc 完全不参与，起点是带哈希校验的 beta 二进制（F-rust-025/028：dist_server 与 sha256 清单，由 `bump-stage0` 工具生成）；「哪个编译器」在 bootstrap 语义里只是 `(stage, host)` 二元组；cc/cmake 被精确锁死的原因是升级它们通常要改 bootstrap 代码（F-rust-016）。
- **行动**：学编译器流水线前先跑一次 `x check` 并观察 `build/` 输出结构（F-rust-030）；诊断构建问题先查 `src/stage0` 的日期与哈希，再谈源码。

#### R3. rustc 是 query 驱动的懒求值系统而非顺序流水线：`rustc_queries!` 宏全仓库唯一一处，各阶段 crate 以 `provide()` 注册 provider

- **陈述**：所有 query 集中定义于 `rustc_middle/src/queries.rs:141` 的唯一一处 `rustc_queries!` 宏调用，每个 query 对应 `Providers` 结构的一个函数指针字段与 `TyCtxt` 上的方法；rustc_expand、rustc_hir_analysis、rustc_mir_transform、rustc_borrowck 等各阶段 crate 通过 `pub fn provide(providers: &mut Providers)` 把实现挂进系统，缓存策略（cache_on_disk/arena_cache/eval_always）逐 query 声明。
- **证据**：F-rust-091（`rustc_queries! {` 全仓库唯一出现于 rustc_middle/src/queries.rs:141，注释说明 query↔Providers 字段对应关系）、F-rust-092（query 定义实例：`derive_macro_expansion` cache_on_disk、`env_var_os` eval_always 等）、F-rust-044（rustc_interface/passes.rs 的 parse→configure_and_expand→…→analysis 函数序列）、F-rust-051（rustc_expand 的 `pub fn provide`）。
- **反常识**：来自 gcc 的直觉是「前端→优化→后端」顺序执行；passes.rs 的函数名（F-rust-044）确实像流水线，但那只是驱动 query 图的骨架——真正的执行模型是 `TyCtxt` 按需触发 query，系统还内建循环检测、增量缓存与自我剖析（F-rust-090 rustc_query_impl 的 job/cycle/incremental/self_profile 模块；F-rust-093 的 QueryJob/QueryCycle）。不先立 query 心智模型，就无法理解为什么每个阶段 crate 都长着同一个 `provide()` 模式（另见 F-rust-060/073/076 的同类签名）。
- **行动**：阅读任何流水线阶段 crate 都先问「它注册了哪些 query」；把 `rustc_middle/src/queries.rs` 的宏体当作编译器能力总清单来读。

#### R4. 四个 `TyKind` 与一个中央数据仓库：AST/HIR/type_ir/public 各持一份同名定义，MIR/THIR 的数据结构在 rustc_middle 而非 `rustc_mir_*` crate

- **陈述**：同名 `TyKind` 在编译器中有 4 处定义（rustc_ast/ast.rs、rustc_hir/hir.rs、rustc_type_ir/ty_kind.rs、rustc_public/ty/tys.rs），分别服务语法表示、编译器 IR、泛型于 Interner 的类型内核、稳定外部接口；rustc_middle 同时是 `TyCtxt`/`GlobalCtxt`（ty/context.rs）与 `Thir`（thir.rs）、MIR `Body`/`BasicBlockData`（mir/mod.rs）的宿主——mir_build 只负责构建、mir_transform 只负责 pass 改写。
- **证据**：F-rust-067（4 处 TyKind 的精确路径与行号：ast.rs:2518、hir.rs:3562、ty_kind.rs:147、tys.rs:319）、F-rust-064（CtxtInterners/TyCtxt/GlobalCtxt/CurrentGcx 全在 rustc_middle/src/ty/context.rs）、F-rust-075（`pub struct Thir<'tcx>` 定义于 rustc_middle/src/thir.rs:63 而非 rustc_mir_build）、F-rust-079（Body/Local/LocalDecl/BasicBlockData 定义于 rustc_middle/src/mir/mod.rs）。
- **反常识**：两个直觉被打破：①「类型只有一个权威定义」——实际 4 个，靠 lowering 逐层传递（rustc_ast_lowering 的 `lower_to_hir` 即其中一环，F-rust-059），直接 grep `TyKind` 会在四个 crate 间迷路；②「MIR crate 定义 MIR」——实际数据结构在 middle，构建逻辑在 mir_build（F-rust-074），优化编排（run_analysis_to_runtime_passes 等四组函数与 sroa/gvn/inline 等 pass，F-rust-076/077）在 mir_transform，三者分工是「数据 / 构建 / 改写」。
- **行动**：为读者制作「四 TyKind 坐标卡」；读 MIR 先去 rustc_middle 认数据结构，再分别进 mir_build 与 mir_transform；讲类型系统时先画 type_ir（Interner 泛型内核，F-rust-071）到 rustc_middle ty 的映射关系。

### rust-lang/cargo（4 条）

#### C1. 此基线已静默完成结构大重组：主源码上提至 `src/`、`Config` 更名 `GlobalContext`、SourceId/PackageId 移驻 `workspace/` 模块、根 Cargo.toml 身兼 package 与 workspace 双职

- **陈述**：master @ 75d17360 的 cargo 主 crate 源码位于 `src/`（不再是旧版 `src/cargo/`），八大模块为 compiler/context/diagnostics/ops/resolver/sources/util/workspace；配置语境类型更名为 `GlobalContext`（定义于 src/context/mod.rs:209，util 仍 re-export 保持可用）；`PackageId` 与 `SourceId` 定义于 src/workspace/ 模块（package_id.rs/source_id.rs）；根 Cargo.toml 同时声明 `[workspace]` 与 `[package]`。
- **证据**：F-cargo-010（src 目录布局：`src/{lib.rs,macros.rs,version.rs}` 与八大模块目录）、F-cargo-043（`pub struct GlobalContext` 位于 src/context/mod.rs:209，字段含 shell/OnceLock 缓存群/jobserver/CacheLocker）、F-cargo-083（PackageId 及其 `&'static PackageIdInner` + PACKAGE_ID_CACHE 定义于 src/workspace/package_id.rs）、F-cargo-001（根 Cargo.toml `[workspace]` 段 members/exclude）与 F-cargo-003（同文件 `[package]` 段 name="cargo"）。
- **反常识**：网络上绝大多数 cargo 源码导读仍使用 `src/cargo/` 布局、`Config` 类型乃至 `util/config.rs` 路径；按旧资料导航会直接迷路——配置子系统已独立为 `context/` 模块（F-cargo-041 的两层反序列化文档、F-cargo-046 的内部模块）。另一反直觉：「包身份」类型不在独立的 id 模块而在 workspace 子系统内，靠 `&'static` 内部指针 + 全局缓存实现廉价克隆与自定义相等（F-cargo-083 的 full_eq/full_hash）。
- **行动**：所有路径引用一律使用重组后坐标；建立「旧名→新名」对照（src/cargo/→src/、Config→GlobalContext、配置→context 模块、SourceId/PackageId→workspace 模块）；旧文档只取架构思想、不取路径。

#### C2. 版本双轨制：库永久 0.x、CLI 显示 1.x——`0.101.0` 的包对外自称 `1.100.0`，并与 rustc 版本同步

- **陈述**：主 crate 的 Cargo.toml version 为 `0.101.0`，但 `cargo --version` 输出 `1.100.0`——非 bootstrap 构建时由 `CARGO_PKG_VERSION_MINOR - 1` 推导；版本声明明言库永久不稳定（恒 0 主版本），CLI 从 1.26 起报告稳定 1.x 且与 rustc 同步；commit 信息由 build.rs 从 git 注入。
- **证据**：F-cargo-040（原文 "The library is permanently unstable, so it always has a 0 major version. However, the CLI now reports a stable 1.x version (starting in 1.26)"）、F-cargo-144（版本推导链：`CARGO_PKG_VERSION_MINOR - 1` → 1.100.0，或 bootstrap 注入的 CFG_RELEASE）、F-cargo-003（[package] version = "0.101.0"）、F-cargo-137（build.rs 从 git log 或源码 tarball 读取 commit hash 并注入环境变量）。
- **反常识**：直觉认为 `--version` 打印的就是 Cargo.toml 的 version；实际二者刻意脱钩——0.x 警示库用户「API 可发生重大变更」（F-cargo-009 README 原文 "This crate may make major changes to its APIs."），1.x 服务工具链视角的版本同步。MSRV 也是双标：workspace rust-version = "1.95"、主 crate rust-version = "1.98"（F-cargo-002）。有趣的巧合：rust 仓库的 `src/version` 恰好同为 `1.100.0`（F-rust-008）——两条独立版本链在同一数值汇合。
- **行动**：把 cargo 当库使用前必读 F-cargo-040 的永久不稳定声明；讨论版本时始终区分「包版本」（0.101.0）与「工具链版本」（1.100.0）两个语境，`cargo -vV` 的完整诊断链见 F-cargo-032。

#### C3. 命令分发是「三级推断 + 别名递归」的决策树：builtin（39 个）→ manifest command（`cargo run main.rs`）→ external（磁盘扫描），外部子命令没有注册表

- **陈述**：`cli::main()` 的执行序为 clap 解析 → `-C` 处理 → `expand_aliases`（递归展开、内置优先）→ 分支处理 `-Z help/--version/--explain/--list` → `Exec::infer` 三级推断（builtin_exec → is_manifest_command → External）→ `init_git` → 执行；外部子命令靠扫描 `cargo-*` 可执行文件发现，`$CARGO_HOME/bin` 前插到 PATH 目录列表。
- **证据**：F-cargo-022（`enum Exec { Builtin, Manifest, External }` 与 infer 匹配顺序，注释原文 "1. built-ins xor manifest-command 2. aliases 3. external subcommands"）、F-cargo-021（cli::main() 完整执行序）、F-cargo-028（is_manifest_command 判定：路径分量 >1 或扩展名为 .rs）、F-cargo-018（third_party_subcommands 磁盘扫描，search_directories 把 $CARGO_HOME/bin 前插 PATH）。
- **反常识**：三个直觉被打破：①`cargo run main.rs` 不是 run 的参数而是走了 manifest-command 分支，判定仅凭「像不像路径」（F-cargo-028），且 stable 上需要 `-Zscript`（F-cargo-029 的报错原文）；②外部命令（cargo-foo）的发现机制是运行时扫描可执行文件而非插件注册表，找不到时错误码 101 并提示 `cargo --list`（F-cargo-019）；③内置命令与 manifest 命令的歧义由测试强制守护——`avoid_ambiguity_between_builtins_and_manifest_commands` 断言所有 builtin 名不满足 is_manifest_command（F-cargo-030）。别名还有递归检测与内置 shadow 规则（F-cargo-031）与 6 个内置短别名（F-cargo-016）。
- **行动**：读 CLI 层先画完整分发树（含 main() 前置流程 F-cargo-014：setup_logger → GlobalContext::default → nightly 补全 → fix 代理 → jobserver → cli::main）；给 cargo 写插件时命名避开 39 个 builtin 名（F-cargo-026）。

#### C4. 「39 个命令皆薄壳，BuildRunner 是世界的中心」：业务全在 ops 与 compiler，cargo 与 rustc 存在官方明认的结构同构

- **陈述**：lib.rs 文档明言 "Each command is a thin wrapper around ops"，编译族命令共享 `ops::cargo_compile` 单一入口；compiler 模块自述把 `BuildRunner` 称为 "the center of the world, coordinating a running build"，并将 `ops::cargo_compile::compile` 类比为 rustc 侧的 driver、compiler 模块类比为 rustc_interface；`Unit`/`UnitInner` 携带 pkg/target/profile/kind/mode/features/rustflags 的完整构建语义，是调度图的节点。
- **证据**：F-cargo-037（lib.rs 文档：ops 为 "Every major operation is implemented here"、cargo_compile 为 "the entry point for all the compilation commands"）、F-cargo-107（compiler/mod.rs 文档原文：BuildContext 静态上下文 / BuildRunner 世界中心 / rustc_interface 类比）、F-cargo-109（`Unit`/`UnitInner` 完整字段：pkg、target、profile、kind、mode、features、rustflags、dep_hash 等）、F-cargo-060（cargo_compile 的 compile/compile_with_exec/create_bcx/print/resolve_all_features 入口族）。
- **反常识**：直觉认为每个子命令（build/test/doc/run）各自独立实现；实际它们共用 cargo_compile 入口，差异被吸收进 CompileOptions/CompileMode/Unit（F-cargo-052 的 ops re-export 清单显示 test/doc/run 的选项结构）。更反直觉的是 cargo 内部复刻了 rustc 的分层叙事——官方文档自己做了这个类比（F-cargo-107），把 rustc 架构知识直接迁移到 cargo 阅读居然可行。
- **行动**：按子系统而非命令组织学习；遇到任何命令先问「它的 ops 函数是什么、Unit 图长什么样」；编译调度篇用 F-cargo-109 的字段表与 F-cargo-106 的 25 个模块清单展开，并显式给出 rustc↔cargo 结构类比表。

### rust-lang/rfcs（4 条）

#### F1. RFC 编号 = PR 编号：仓库没有独立编号机构，text/ 目录 639 个文件横跨 0001~3984，编号空洞本身就是提案存活率的化石记录

- **陈述**：提交流程是从 `0000-template.md` 复制出 `text/0000-my-feature.md` 并提 PR，编号即 PR 编号、RFC 被接受时文件重命名并更新头部链接；text/ 顶层实存 639 个 .md（递归 648 个、含 3 个多章节子目录），编号从 `0001-private-fields` 到 `3984-libs-team-refactor`。
- **证据**：F-rfcs-006（「提交时不预先分配 RFC 编号，编号即 PR 编号，被接受时文件重命名」）、F-rfcs-165（text/ 顶层 639 个 .md，递归 648 个）、F-rfcs-167（编号范围 0001~3984）、F-rfcs-005（提交四步流程：复制模板 → 填写 → 提 PR → 以 PR 编号重命名）。
- **反常识**：直觉以为 RFC 编号像 RFC 编辑部那样预分配；实际是 GitHub PR 机制的自然结果——「RFC 3137」先是「PR #3137」。639 个文件对 3984 个编号位，约 84% 的编号位置没有对应文件，每个空洞大致对应一个被关闭的 PR；命名模式统一为 4 位零填充 + kebab-case（F-rfcs-168），多章节 RFC 用同名子目录（F-rfcs-166）。
- **行动**：读编号时把它理解为「第 N 号 PR 曾存活」；用编号粗定位时代——从精读样本看编号与 Start Date 大体单调对应（0114 为 2014-07-29 即 F-rfcs-034，3137 为 2021-05-31 即 F-rfcs-039，3984 为 2026-07-15 即 F-rfcs-174）。

#### F2. `active` 只是入场券：FCP 十个日历日、批准后仍可部分拒绝——RFC 生命周期远比「通过即定案」宽松

- **陈述**：README 明文规定 RFC 合并进仓库即为 active，但「不意味着功能最终合并，也不蕴含实现优先级或开发人员分配」；FCP（最终评论期）要求全体 subteam 成员 sign off 后持续十个日历日（至少 5 个工作日），期间出现实质性新论点可取消；RFC 3192-dyno 的头部声明 "This RFC was previously approved, but part of it later rejected"——Provider 接口被 libs team 会议拒绝，剩余的 Demand 类型重命名为 Request。
- **证据**：F-rfcs-008（active 语义三连否定原文）、F-rfcs-007（FCP 机制：motion → 全员 sign off → 十个日历日 → 实质新论点可取消）、F-rfcs-125（3192-dyno 的「先批准后部分拒绝」声明与 Demand→Request 更名）、F-rfcs-009（已接受 RFC 不应实质性修改，重大变更走新 RFC 并加注）。
- **反常识**：直觉「RFC 通过 = 官方承诺实现」；文档明说 active 只是入场券。已接受的 RFC 不应实质修改（F-rfcs-009）；postponed 的 PR 可在时机合适时重开且无正式流程（F-rfcs-010）；甚至存在「批准后部分拒绝」的活标本（3192-dyno，F-rfcs-125）；0243 与 1859 共享同一 tracking issue（F-rfcs-172），提案间的取代与继承关系比编号所示更纠缠。
- **行动**：评估任何语言特性现状时，先查 RFC 的后续命运（tracking issue、修正案、拒绝注记）而非只读正文；把 3192-dyno 作为「接受≠定案」的警示案例嵌入生命周期篇。

#### F3. RFC 只是四条通道之一：lang/compiler/libs 三团队的分流策略截然不同，「RFC 成本」本身是架构决策的输入

- **陈述**：语言团队几乎每个变更都需 RFC（含新 lint，标记 T-lang，新 PR 一周内完成初始 triage）；编译器团队「大多数超出简单 PR 范围的决策使用 MCP 而非 RFC」（标记 T-compiler）；库团队哲学是 "do whatever is easiest"——若写 RFC 比实现工作量小，这本身就是需要 RFC 的信号，新 API 几乎必然值得 RFC；RFC 从发帖到落地最少 2 周、争议性变更可达数月量级。
- **证据**：F-rfcs-025（lang 准则：新 lint 视为语言变更、一周 triage）、F-rfcs-027（compiler 准则原文 "most compiler-side change proposals use MCPs rather than RFCs"）、F-rfcs-030（libs 哲学原文 "do whatever is easiest" 与 "new APIs almost certainly merit an RFC"）、F-rfcs-029（RFC 成本：最少 2 周、争议可达数月、"Full process always applies"）。
- **反常识**：直觉「重要变更都走 RFC」；实际生态是分流的：RFC 仓库明说自己不是编译器决策主场（MCP 在 rust-lang/compiler-team issues，F-rfcs-027）；库团队大量变更直接 PR insta-merge（F-rfcs-029）；「RFC 太贵」反过来成为「值不值得」的判定信号（F-rfcs-030）；trait impl 与文档是 insta-stable 的（无 feature gate、无 tracking issue），因此需要更高审查强度（F-rfcs-032）；判定清单见 F-rfcs-031（对称 API 补缺走 PR、稳定 API 语义变更/泛化/弃用走 RFC）。
- **行动**：给 Rust 贡献变更前先做「通道判定」：对照三份准则文档（lang/compiler/libs changes）找到自己变更的类型；这也是理解 rust 仓库（编译器主场）与 rfcs 仓库（语言/库主场）分工的钥匙。

#### F4. 模板强制「双解释」文体且自身在演化：4 个元数据字段 + 9 章节结构、Guide/Reference 双解释分写、他语言先例明文不足以构成动机、头部格式随时代演变

- **陈述**：0000-template.md 头部仅 4 个字段（Feature Name/Start Date/RFC PR/Rust Issue），正文 9 章（Summary、Motivation、Guide-level explanation、Reference-level explanation、Drawbacks、Rationale and alternatives、Prior art、Unresolved questions、Future possibilities）；Guide 节要求「像功能已包含在语言中那样向其他程序员讲解、以示例为主」，Reference 节自述 "This is the technical portion of the RFC"；头部格式经历了 2014 三字段 → 2015 增 Feature Name → 晚期锚点链接定义的演变。
- **证据**：F-rfcs-013（模板 4 个元数据字段）、F-rfcs-014（9 章节清单原文）、F-rfcs-016（Reference 节定位原文 "This is the technical portion of the RFC"）、F-rfcs-170（头部格式演变：2014 年 RFC 仅三字段无锚点，2015-02 起增 Feature Name，晚期带 `[summary]: #summary` 式锚点）。
- **反常识**：直觉认为 RFC 是纯技术规格书；实际模板要求作者同时扮演「教程作者」（Guide 节）与「规格作者」（Reference 节，F-rfcs-015 还区分编译器导向/政策导向变体），必须诚实写 Drawbacks 与 Unresolved questions（哪怕内容是 "None."，见 F-rfcs-053、F-rfcs-161）。「Swift 有所以我们要有」式论证被模板预先封死（F-rfcs-017：其他语言先例本身不足以构成 RFC 的动机）。模板本身也是历史文献：读 2014~2015 年的 RFC 要宽容格式差异（F-rfcs-170）。
- **行动**：读 RFC 按「Summary 定位 → Motivation 估值 → Guide 建直觉 → Reference 核细节 → Drawbacks/Alternatives 求平衡」的顺序推进；写 RFC 前把 9 章当检查清单逐项过。

---

## 第二部分：知识地图（三个 bundle 的文档规划）

### rust/rust/ bundle（12 篇 concepts + 2 篇 examples + 2 篇 references）

组织原则：**学习路径按编译器流水线阶段递进**（00-02 立地图与构建认知 → 03-07 沿数据流推进 → 08 标准库独立纵队 → 09-11 高级横切面）。事实分配 F-rust-001~133 完备无遗漏；02 篇讲解流水线时前向引用 query 模型（主覆盖在 09）。

| 编号 | 文件名（concepts/） | 标题 | 覆盖的 F-xxx 事实编号 | 前置依赖文档编号 |
|------|---------------------|------|----------------------|----------------|
| 00 | 00-intro-repo-navigation.md | 简介与仓库导航：单仓库、双 workspace、三世界 | F-rust-001~013 | — |
| 01 | 01-bootstrap-build-system.md | bootstrap 构建系统：Python 壳、Rust 芯与三阶段自举 | F-rust-014~035 | 00 |
| 02 | 02-compiler-pipeline-overview.md | 编译器流水线总览：入口链与 query 心智模型 | F-rust-036~047（query 细节交叉引用 F-rust-090~093） | 00、01 |
| 03 | 03-parsing-macro-expansion.md | 解析与宏展开：从字节流到 AST | F-rust-048~056 | 02 |
| 04 | 04-hir-ast-lowering.md | HIR 与 AST Lowering：面向编译器的第二个 AST | F-rust-057~062 | 03 |
| 05 | 05-type-system-trait-solving.md | 类型系统与 trait 求解：TyCtxt、InferCtxt 与下一代求解器 | F-rust-063~072 | 04 |
| 06 | 06-mir-borrow-checking.md | MIR 与借用检查：THIR→MIR 构建与 NLL | F-rust-073~075、078~079 | 05 |
| 07 | 07-mir-optimization-codegen.md | MIR 优化与代码生成：pass 流与三大后端 | F-rust-076~077、080~085 | 06 |
| 08 | 08-std-layered-architecture.md | 标准库分层架构：core→alloc→std 洋葱与平台分发 | F-rust-097~120 | 00 |
| 09 | 09-rustc-infrastructure.md | rustc 基础设施：span、query 系统、元数据与名称解析 | F-rust-086~088、090~096 | 02（建议在 05 之后、06 之前穿插阅读） |
| 10 | 10-rustdoc-toolchain.md | rustdoc 与工具链：46 个工具目录与测试套件 | F-rust-121~133 | 00、02 |
| 11 | 11-diagnostics-error-system.md | 诊断与错误体系：DiagCtxt 与贯穿各阶段的 diagnostics 模式 | F-rust-089（主锚）；交叉引用 F-rust-010（rustc_error_codes/rustc_error_messages 两个 crate）、042、046、051、060、062、068、070、073、080、094、096 | 09 |

要点说明：
- 02 是「总览篇」：先立 passes.rs 的函数序列骨架（F-rust-044），再引入「query 按需求值」的执行模型（交叉引用 F-rust-091/092，深入在 09），为 03-07 每篇定基调（洞察 R3）。
- 08 为大篇（24 条事实）：内层 core（零依赖宣言与外部符号诚实清单）→ alloc → std facade → sys/pal/os 平台分发 → sysroot 聚合与 panic 运行时，可分节组织。
- 11 以「诊断贯穿模式」立篇：核心是 rustc_errors 的 Diagctx 体系（F-rust-089），辅以各阶段 crate 均带 diagnostics 模块的统一模式（交叉引用九处），主题由模式支撑而主锚集中。

examples/ 设计（2 篇，覆盖编号为交叉引用，不承担主覆盖）：

| 文件名（examples/） | 标题 | 覆盖的 F-xxx 事实编号 | 前置依赖文档编号 |
|---------------------|------|----------------------|----------------|
| x-py-build-walkthrough.md | x.py 构建流程剖析 | 交叉引用 F-rust-004、014、017~032 | 01 |
| std-module-anatomy.md | std 模块结构剖析 | 交叉引用 F-rust-097~120（重点 105~117） | 08 |

references/ 设计（2 篇，信源登记，覆盖编号均为交叉引用）：

| 文件名（references/） | 标题 | 内容 |
|----------------------|------|------|
| rustc-source-map.md | rustc 编译器信源登记 | 基线 commit、70 crate 清单（F-rust-010）、入口链与流水线各 crate 的关键文件/行号坐标、tests/ 26 个套件索引（F-rust-011、133） |
| std-source-map.md | 标准库信源登记 | library/ 23 目录清单（F-rust-098）、core/alloc/std 关键 lib.rs 与 sys/pal/os 坐标、sysroot/rtstartup/panic 运行时坐标、构建特殊配置（F-rust-099~102） |

### rust/cargo/ bundle（9 篇 concepts + 2 篇 examples + 1 篇 reference）

组织原则：**沿一条命令的数据流推进**（00-01 进入与分发 → 02-03 数据模型与语境 → 04-05 解析与下载 → 06-07 操作与编译调度 → 08-09 横切纵队）。

⚠️ **结构基线声明（E 阶段必须遵守）**：此基线（master @ 75d17360）主 crate 源码位于 `src/`（非旧版 `src/cargo/`），`Config` 已更名 `GlobalContext`（F-cargo-043），SourceId/PackageId 位于 src/workspace/（F-cargo-083/085），根 Cargo.toml 为 package+workspace 合一（F-cargo-001/003）；所有路径引用一律使用重组后坐标。

| 编号 | 文件名（concepts/） | 标题 | 覆盖的 F-xxx 事实编号 | 前置依赖文档编号 |
|------|---------------------|------|----------------------|----------------|
| 00 | 00-intro-architecture-overview.md | 简介与架构总览：src/ 重组基线与组件地图 | F-cargo-001~013、033~040、144 | — |
| 01 | 01-crate-organization-cli-dispatch.md | Crate 组织与 CLI 分发：19+5 个子 crate 与三级命令决策树 | F-cargo-014~032、113~123 | 00 |
| 02 | 02-workspace-package-model.md | Workspace 与 Package 模型：从 Cargo.toml 到包身份 | F-cargo-077~088 | 00 |
| 03 | 03-global-context-config.md | GlobalContext 配置系统：两层反序列化与 Definition 优先级 | F-cargo-041~050 | 00、02 |
| 04 | 04-dependency-resolver.md | 依赖解析 resolver：Resolve 图与版本演进 | F-cargo-062~067 | 02、03 |
| 05 | 05-sources-registry.md | Sources 与 registry：五种包源与 crates.io 协议 | F-cargo-068~076 | 02 |
| 06 | 06-ops-command-implementation.md | ops 命令实现：39 个薄壳下的业务核心 | F-cargo-051~061 | 02、03 |
| 07 | 07-build-scheduling-unit-graph.md | 编译调度与 unit 图：BuildRunner 的世界 | F-cargo-106~112 | 06 |
| 08 | 08-auth-credential.md | 认证与 credential：JSON 协议与 5 个平台实现 | F-cargo-124~130 | 03、05 |
| 09 | 09-util-infrastructure.md | util 基础设施：37 个子模块与构建支撑 | F-cargo-089~105、135~138 | 00 |

要点说明：
- 00 是「地图篇」：根 Cargo.toml 双重身份与 feature/平台特定依赖（001~013）+ lib.rs 八大模块与组件职责原文（033~040，含 F-cargo-037 的 thin-wrapper 宣言与 F-cargo-038 的 File Overview）+ 版本推导链（144）。
- 01 为大篇（30 条事实）：CLI 分发决策树（014~032）与 crates/ 19 个 + credential/ 5 个子 crate 家族（113~123）两大块，可分节组织。
- 03 依赖 02：Workspace 构造需要 `&GlobalContext`（F-cargo-079 字段 `gctx: &'gctx GlobalContext`）。

examples/ 设计（2 篇，覆盖编号为交叉引用，不承担主覆盖）：

| 文件名（examples/） | 标题 | 覆盖的 F-xxx 事实编号 | 前置依赖文档编号 |
|---------------------|------|----------------------|----------------|
| cargo-new-source-trace.md | cargo new 源码路径追踪 | 交叉引用 F-cargo-021、022、026、027、057、077~080 | 01、02、06 |
| cargo-toml-parsing-flow.md | Cargo.toml 解析流程 | 交叉引用 F-cargo-037、038、041、048、077~081 | 02、03 |

references/ 设计（1 篇，承担文档资产与测试坐标类事实的主覆盖）：

| 文件名（references/） | 标题 | 覆盖的 F-xxx 事实编号 | 内容 |
|----------------------|------|----------------------|------|
| cargo-source-map.md | cargo 信源登记 | F-cargo-131~134、139~143 | doc/man 37 个手册与 doc/book 四大部分、doc/contrib 贡献指南、.cargo/config.toml 的 xtask 别名、testsuite 120+ 测试模块、benches 三类基准、CI/workflow 坐标；附「旧名→新名」迁移对照（src/cargo/→src/、Config→GlobalContext） |

### rust/rfcs/ bundle（8 篇 concepts + 1 篇 reference，examples 省略）

组织原则：**流程治理先行，精读 RFC 按语言特性主题家族分组**。精读事实（F-rfcs-034~164）+ 抽样事实（171~177）共 138 条分配到 01~07 七篇主题篇；02（类型系统演进）为最大篇（41 条，覆盖九篇 RFC），可分节组织。最终 8 篇 concepts，落在任务允许的 6-8 篇区间内。

| 编号 | 文件名（concepts/） | 标题 | 覆盖的 F-xxx 事实编号 | 前置依赖文档编号 |
|------|---------------------|------|----------------------|----------------|
| 00 | 00-rfc-process-and-template.md | RFC 流程与模板：PR 即编号、9 章双解释文体 | F-rfcs-001~007、013~017、165~170、171 | — |
| 01 | 01-lang-evolution-expr-pattern.md | 语言演进：表达式与模式 | F-rfcs-034~053、176 | 00 |
| 02 | 02-type-system-evolution.md | 类型系统演进 | F-rfcs-054~079、145~157、175、177 | 01 |
| 03 | 03-error-safety-evolution.md | 错误处理与安全演进 | F-rfcs-080~095、139~144、158~161、172 | 01 |
| 04 | 04-async-and-borrowing.md | 异步与借用：NLL、Pin 与 futures | F-rfcs-096~112、173 | 02、03 |
| 05 | 05-compiler-arch-evolution.md | 编译器架构演进：HIR、MIR 与 dyno | F-rfcs-113~128 | 00 |
| 06 | 06-std-ecosystem-evolution.md | 标准库与生态演进：Edition 与 fs/平台 API | F-rfcs-129~138 | 01、02 |
| 07 | 07-rfc-lifecycle-governance.md | RFC 生命周期与团队治理：三团队分流与关键字保留 | F-rfcs-008~012、025~033、162~164、174 | 00 |

要点说明：
- 00 覆盖流程（001~007）+ 模板结构与指引（013~017）+ 目录统计与头部格式演变（165~170）+ 抽样 0002-rfc-process（171，流程定义的源头 RFC），是全部精读篇的「文体透镜」。
- 01 表达式与模式家族：0114-closures / 3137-let-else / 0160-if-let / 0214-while-let 四篇精读 + 抽样 2497-if-let-chains（176）。
- 02 类型系统家族（大篇）：0132-ufcs / 0135-where / 0911-const-fn / 1444-union / 0401-coercions / 1506-adt-kinds / 0953-op-assign / 0048-traits 八篇精读 + 抽样 1522-conservative-impl-trait（175）、2195-really-tagged-unions（177）。
- 03 错误处理与安全家族：0221-panic / 1859-try-trait / 2388-try-expr / 3128-io-safety / 0050-assert 五篇精读 + 抽样 0243-trait-based-exception（172，? 与 catch 的起源，与 1859 共享 tracking issue）。
- 04 异步与借用家族：2094-nll / 2349-pin / 2592-futures 三篇精读 + 抽样 2394-async_await（173，2592 的姊妹 RFC）。
- 05 编译器架构家族：1191-hir / 1211-mir / 3192-dyno 三篇精读，可回指 rust bundle 的 04/06 篇实现坐标（F-rust-057/079）交叉印证。
- 06 标准库与生态：2052-epochs（Edition 机制）+ 1044-io-fs（os 层级愿景与 lowering API）；Edition 与 cargo 的 features.rs（F-cargo-086 Edition 枚举）构成跨 bundle 呼应。
- 07 治理收束：active/FCP/修正案/postponed/许可（008~012）+ 三团队准则（025~033）+ 0342-keywords 关键字保留（162~164）+ 抽样 3984-libs-team-refactor（174，团队重组 RFC，流程至今活跃）。

examples 省略说明：按任务允许省略。E 阶段如需可追加「how-to-read-an-rfc」实操篇（覆盖编号均为交叉引用：F-rfcs-013~017、039~043、170），不承担主覆盖。

references/ 设计（1 篇，承担仓库工具链事实的主覆盖）：

| 文件名（references/） | 标题 | 覆盖的 F-xxx 事实编号 | 内容 |
|----------------------|------|----------------------|------|
| rfcs-source-map.md | rfcs 信源登记 | F-rfcs-018~024 | generate-book.py 的布局约定与执行逻辑、SUMMARY.md 生成结构、book.toml 配置、GitHub Pages 部署流程、PR review 约定；另登记基线 commit、仓库根文件清单（交叉引用 F-rfcs-169）、26 篇精读与 7 篇抽样 RFC 的文件路径 |

---

## 第三部分：概念-事实映射校验

### 覆盖统计总表

| bundle | 事实总量 | concepts 主覆盖 | references 主覆盖 | examples 覆盖口径 | 未覆盖编号 |
|--------|---------|----------------|------------------|------------------|-----------|
| rust/rust/ | 133（F-rust-001~133） | 133（12 篇） | 0（纯登记，交叉引用） | 交叉引用不计数 | 无 |
| rust/cargo/ | 144（F-cargo-001~144） | 135（9 篇） | 9（cargo-source-map.md） | 交叉引用不计数 | 无 |
| rust/rfcs/ | 177（F-rfcs-001~177） | 170（8 篇） | 7（rfcs-source-map.md） | 无 examples | 无 |

**三份清单覆盖率均为 100%**（454/454），优于任务允许的 <15% 边缘事实不入库上限；未覆盖事实编号清单为空。

### 逐篇分配明细（供 E 阶段核对）

**rust/rust/ bundle**（12 篇 concepts，主覆盖 133 条）：

| 篇 | 主覆盖编号 | 条数 |
|----|-----------|------|
| 00 | F-rust-001~013 | 13 |
| 01 | F-rust-014~035 | 22 |
| 02 | F-rust-036~047 | 12 |
| 03 | F-rust-048~056 | 9 |
| 04 | F-rust-057~062 | 6 |
| 05 | F-rust-063~072 | 10 |
| 06 | F-rust-073~075、078~079 | 5 |
| 07 | F-rust-076~077、080~085 | 8 |
| 08 | F-rust-097~120 | 24 |
| 09 | F-rust-086~088、090~096 | 10 |
| 10 | F-rust-121~133 | 13 |
| 11 | F-rust-089 | 1（主锚）+ 9（交叉引用） |

编号连续性检查：001~133 无断链。区间切分点（013/014、035/036、047/048、056/057、062/063、072/073、075/076、079/080、085/086、096/097、120/121、089 单列）均与事实清单的章节边界（A 仓库总览 / B bootstrap / C 编译器流水线 / D 标准库 / E rustdoc 与工具）对齐；唯一例外是 089（rustc_errors）从 C 段「基础设施」移出、单独主归于 11-诊断与错误体系，以支撑任务指定的独立诊断篇。

**rust/cargo/ bundle**（9 篇 concepts 主覆盖 135 条 + reference 主覆盖 9 条）：

| 篇 | 主覆盖编号 | 条数 |
|----|-----------|------|
| 00 | F-cargo-001~013、033~040、144 | 22 |
| 01 | F-cargo-014~032、113~123 | 30 |
| 02 | F-cargo-077~088 | 12 |
| 03 | F-cargo-041~050 | 10 |
| 04 | F-cargo-062~067 | 6 |
| 05 | F-cargo-068~076 | 9 |
| 06 | F-cargo-051~061 | 11 |
| 07 | F-cargo-106~112 | 7 |
| 08 | F-cargo-124~130 | 7 |
| 09 | F-cargo-089~105、135~138 | 21 |
| reference | F-cargo-131~134、139~143 | 9 |

编号连续性检查：001~144 无断链。02/03 与 04/06 的编号交错（077~088 在 02 而 041~050 在 03）源于文档主题序（数据模型先于配置语境）与事实清单章节序（D-1 context 先于 D-5 workspace）不同，属规划性重排而非遗漏；131~134/139~143（文档资产与测试坐标）主归 references 篇，因信源登记是其本职工位。

**rust/rfcs/ bundle**（8 篇 concepts 主覆盖 170 条 + reference 主覆盖 7 条）：

| 篇 | 主覆盖编号 | 条数 |
|----|-----------|------|
| 00 | F-rfcs-001~007、013~017、165~170、171 | 19 |
| 01 | F-rfcs-034~053、176 | 21 |
| 02 | F-rfcs-054~079、145~157、175、177 | 41 |
| 03 | F-rfcs-080~095、139~144、158~161、172 | 27 |
| 04 | F-rfcs-096~112、173 | 18 |
| 05 | F-rfcs-113~128 | 16 |
| 06 | F-rfcs-129~138 | 10 |
| 07 | F-rfcs-008~012、025~033、162~164、174 | 18 |
| reference | F-rfcs-018~024 | 7 |

编号连续性检查：001~177 无断链。A 段（001~033）按主题拆分到 00/07/reference 三处（流程与模板→00、生命周期与团队准则→07、book 构建工具链→reference）；B 段精读 26 篇（034~164）按语言特性家族分到 01~06；C 段抽样 7 篇（171~177）按各自主题归入对应篇（171→00、172→03、173→04、174→07、175/177→02、176→01）。

### 口径说明

1. **主覆盖 vs 交叉引用**：每个事实编号有且仅有一个主归属篇（上表「条数」列只计主覆盖，合计分别为 133/144/177，与清单总量精确相等）；一篇文档可在行文中交叉引用别篇主覆盖的编号（如 02 篇引用 F-rust-091/092），交叉引用不重复计数。
2. **examples 不承担主覆盖**：三 bundle 的 examples 篇均为实操走读，其引用编号全部来自已主覆盖的编号集合。
3. **references 的两种口径**：cargo 与 rfcs 的 references 篇各承担 9/7 条「信源坐标类」事实的主覆盖（文档资产、测试布局、构建工具链——登记本身即其主题）；rust 的两篇 references 为纯登记（全部交叉引用），因为其候选编号（010/011/098/099~102 等）已在 concepts 篇主覆盖。
4. **大篇预警**：rust 08（24 条）、cargo 00/01/09（22/30/21 条）、rfcs 02（41 条）为主锚密集篇，E 阶段写作时应内部分节；rfcs 02 覆盖九篇 RFC 精读，若单篇体量失控，可在保持 6-8 篇总量约束下将 145~157 与 175/177（后五篇精读+两抽样）并入 01 或独立成篇的替代方案留待 E 阶段裁量（本文规划维持 8 篇）。
5. **跨 bundle 呼应点**（E 阶段可埋链接）：rust 08 标准库 ↔ rfcs 06（1044-io-fs 的 os 层级愿景 ↔ F-rust-112/113 实现）；rust 04/06 ↔ rfcs 05（HIR/MIR RFC ↔ rustc_hir/rustc_middle 实现）；cargo 04（resolver）↔ rust 09（query 系统同为按需求值架构的对照参考——仅作学习类比，二者无实现关联）；cargo 02（features.rs Edition 枚举 F-cargo-086）↔ rfcs 06（2052-epochs）。

> 洞察证据编号已逐条对照三份 facts 文件核实，均真实存在；行号引用以采集时快照为准。