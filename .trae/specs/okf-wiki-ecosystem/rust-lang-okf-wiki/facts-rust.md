# facts-rust.md — rust-lang/rust 事实清单
> 仓库基线：main @ e457a7b0d326d67b4322ef0d11bd715cfaeda48f（2026-08-27）；路径前缀 external/libs/rust-lang/rust/
> 采集方式：只读源码（Grep/Glob/Read），零推测；行号为采集时快照。

## A. 仓库总览

- F-rust-001: README.md 第 13-14 行原文："This is the main source code repository for [Rust]. It contains the compiler, standard library, and documentation."（源：README.md）
- F-rust-002: README.md 第 59-61 行：Rust "primarily distributed under the terms of both the MIT license and the Apache License (Version 2.0), with portions covered by various BSD-like licenses."（源：README.md）
- F-rust-003: README.md 第 68-69 行："The Rust Foundation owns and protects the Rust and Cargo trademarks and logos (the 'Rust Trademarks')."（源：README.md）
- F-rust-004: x.py 第 5 行注释："This file is only a 'symlink' to bootstrap.py, all logic should go there."；x.py 末尾将 `src/bootstrap` 插入 `sys.path` 后 `import bootstrap` 并调用 `bootstrap.main()`（源：x.py）
- F-rust-005: 根 Cargo.toml 为 `[workspace] resolver = "2"`，members 含 `compiler/rustc`、`src/build_helper`、`src/rustc-std-workspace/rustc-std-workspace-{alloc,core,std}`、`src/rustdoc-json-types`、`src/shim_utils` 及 34 个 `src/tools/*` 成员（含 clippy、compiletest、miri、rustfmt、tidy、x 等）（源：Cargo.toml）
- F-rust-006: 根 Cargo.toml `exclude` 列表为：`"build"`、`"compiler/rustc_codegen_cranelift"`、`"compiler/rustc_codegen_gcc"`、`"src/bootstrap"`、`"tests/rustdoc-gui"`、`"obj"`（源：Cargo.toml）
- F-rust-007: 根 Cargo.toml 中 `[profile.release.package.lld-wrapper]` 与 `[profile.release.package.wasm-component-ld-wrapper]` 均设 `debug = 0`、`strip = true`，注释称二者是 "very thin wrappers around executing lld"（源：Cargo.toml）
- F-rust-008: `src/version` 文件内容为单行 `1.100.0`（源：src/version）
- F-rust-009: `src/` 顶层子目录共 11 个：bootstrap、build_helper、ci、doc、etc、gcc、librustdoc、llvm-project、rustc-std-workspace、rustdoc-json-types、shim_utils、tools（实测 12 项含 tools）（源：src/ 目录列表）
- F-rust-010: `compiler/` 目录含 70 个子目录：rustc（二进制壳）+ 69 个 rustc_* crate（rustc_abi、rustc_arena、rustc_ast、rustc_ast_ir、rustc_ast_lowering、rustc_ast_passes、rustc_ast_pretty、rustc_attr_ir、rustc_attr_parsing、rustc_baked_icu_data、rustc_borrowck、rustc_builtin_macros、rustc_codegen_cranelift、rustc_codegen_gcc、rustc_codegen_llvm、rustc_codegen_ssa、rustc_const_eval、rustc_crate_store、rustc_data_structures、rustc_driver、rustc_driver_impl、rustc_error_codes、rustc_error_messages、rustc_errors、rustc_expand、rustc_feature、rustc_fs_util、rustc_graphviz、rustc_hashes、rustc_hir、rustc_hir_analysis、rustc_hir_id、rustc_hir_pretty、rustc_hir_typeck、rustc_incremental、rustc_index、rustc_index_macros、rustc_infer、rustc_interface、rustc_lexer、rustc_lint、rustc_lint_defs、rustc_llvm、rustc_log、rustc_macros、rustc_metadata、rustc_middle、rustc_mir_build、rustc_mir_dataflow、rustc_mir_transform、rustc_monomorphize、rustc_next_trait_solver、rustc_parse、rustc_parse_format、rustc_passes、rustc_pattern_analysis、rustc_privacy、rustc_proc_macro、rustc_public、rustc_public_bridge、rustc_query_impl、rustc_resolve、rustc_sanitizers、rustc_serialize、rustc_session、rustc_span、rustc_structures、rustc_symbol_mangling、rustc_target、rustc_thread_pool、rustc_trait_selection、rustc_traits、rustc_transmute、rustc_ty_utils、rustc_ty_walk、rustc_type_ir、rustc_type_ir_macros、rustc_windows_rc）（源：compiler/ 目录列表）
- F-rust-011: `tests/` 顶层子目录 26 个：assembly-llvm、auxiliary、build-std、codegen-llvm、codegen-units、coverage、coverage-run-rustdoc、crashes、debuginfo、incremental、mir-opt、pretty、run-make、run-make-cargo、rustdoc-gui、rustdoc-html、rustdoc-js、rustdoc-js-std、rustdoc-json、rustdoc-ui、ui、ui-fulldeps（源：tests/ 目录列表）
- F-rust-012: 仓库根存在 AGENTS.md，内容为 LLM 使用政策与编辑门槛规则（外部仓库路由、禁止文本、reviewer 门槛、soundness 分类等），并声明 "`x.py` is the build tool for this repository… Invoke it as `./x`"（源：AGENTS.md）
- F-rust-013: 根 Cargo.toml `[profile.dev.package.test-float-parse]` 与 `[profile.release.package.test-float-parse]` 均设 `opt-level = 3`，注释 "Bigint libraries are slow without optimization"（源：Cargo.toml）

## B. bootstrap 构建系统

- F-rust-014: src/bootstrap 本身是一个 Rust crate：Cargo.toml `name = "bootstrap"`、`version = "0.0.0"`、`edition = "2024"`；定义三个 bin target：`bootstrap`（src/bin/main.rs）、`rustc`（src/bin/rustc.rs）、`rustdoc`（src/bin/rustdoc.rs）（源：src/bootstrap/Cargo.toml）
- F-rust-015: bootstrap crate 的 features：`build-metrics`（依赖 sysinfo）与 `tracing`（依赖 tracing/tracing-chrome/tracing-subscriber/chrono）（源：src/bootstrap/Cargo.toml）
- F-rust-016: bootstrap Cargo.toml 中 cc 与 cmake 以精确版本锁定：`cc = "=1.2.62"`、`cmake = "=0.1.54"`，注释称更新这些依赖通常需要修改 bootstrap 代码（源：src/bootstrap/Cargo.toml）
- F-rust-017: src/bootstrap/src/lib.rs 模块级文档第一行："Implementation of bootstrap, the Rust build system."；其模块为 `cli_main`、`core`、`utils`（源：src/bootstrap/src/lib.rs）
- F-rust-018: src/bootstrap/src/core/mod.rs 声明 11 个模块：android、backend、build_steps、builder、compiler、config、debuggers、download、metadata、sanity、session（源：src/bootstrap/src/core/mod.rs）
- F-rust-019: src/bootstrap/src/core/build_steps/mod.rs 声明 18 个模块：check、clean、clippy、compile、dist、doc、format、gcc、install、llvm、perf、run、setup、synthetic_targets、test、tool、toolstate、vendor（源：src/bootstrap/src/core/build_steps/mod.rs）
- F-rust-020: `Builder<'a>` 结构体（src/bootstrap/src/core/builder/mod.rs:44）字段：`sess: &'a Session`、`top_stage: u32`、`kind: Kind`、`cache: Cache`、`stack: RefCell<Vec<Box<dyn AnyDebug>>>`、`time_spent_on_dependencies: Cell<Duration>`、`paths: Vec<PathBuf>`、`submodule_paths_cache: OnceLock<Vec<String>>`、`log_cli_step_for_tests`（源：src/bootstrap/src/core/builder/mod.rs）
- F-rust-021: `pub enum Kind`（builder/mod.rs:626，derive ValueEnum）变体：Build、Check、Clippy、Fix、Format、Test、Miri、MiriSetup、MiriTest、Bench、Doc、Clean、Dist、Install、Run、Setup、Vendor、Perf；其中 Build/Check/Test/Doc/Run 带单字母 alias（b/c/t/d/r）（源：src/bootstrap/src/core/builder/mod.rs）
- F-rust-022: `pub struct Compiler`（src/bootstrap/src/core/compiler.rs:11）字段：`stage: u32`、`host: TargetSelection`、`forced_compiler: bool`；其 Hash/PartialEq 只使用 stage 与 host 字段（源：src/bootstrap/src/core/compiler.rs）
- F-rust-023: src/bootstrap/src/core/build_steps/compile.rs 中的 Step 结构体：`Std`(L47)、`StdLink`(L724)、`StartupObjects`(L896)、`BuiltRustc`(L981)、`Rustc`(L995)、`GccDylibSet`(L1575)、`GccCodegenBackend`(L1663)、`CraneliftCodegenBackend`(L1740)、`Sysroot`(L1912)（源：src/bootstrap/src/core/build_steps/compile.rs）
- F-rust-024: src/bootstrap/src/core/config/mod.rs 中的枚举：CompilerBuiltins、Allocator、DebuginfoLevel、StringOrBool、StringOrInt、LlvmLibunwind、SplitDebuginfo、CompressDebuginfo、ReplaceOpt、DryRun、RustcLto、GccCiMode、LlvmCiMode、DebuggerPath（源：src/bootstrap/src/core/config/mod.rs）
- F-rust-025: src/stage0 文件头部键值：`dist_server=https://static.rust-lang.org`、`artifacts_server=https://ci-artifacts.rust-lang.org/rustc-builds`、`artifacts_with_llvm_assertions_server=https://ci-artifacts.rust-lang.org/rustc-builds-alt`、`git_merge_commit_email=bors@rust-lang.org`、`nightly_branch=main`（源：src/stage0 L1-5）
- F-rust-026: src/stage0 记录 bootstrap 编译器：`compiler_date=2026-08-18`、`compiler_version=beta`、`compiler_git_commit_hash=f47d5bb13648d5c859f5b438eb7dc834b9729961`、`compiler_channel_manifest_hash=7c8035eccd259661acc845afb33fb40892f4722327f7d8d8c49feda172d1a159`（源：src/stage0 L16-19）
- F-rust-027: src/stage0 记录 rustfmt：`rustfmt_date=2026-08-18`、`rustfmt_version=nightly`、`rustfmt_git_commit_hash=8fa1c96cfd489e4c27654c144ae871ce2c4db6c6`（源：src/stage0 L20-23）
- F-rust-028: src/stage0 第 10-11 行注释："The section below is generated by `./x.py run src/tools/bump-stage0`"；该节其余内容列出了 `dist/2026-08-18/` 下各目标三元组的 rustc-beta/rust-std-beta tar.gz 与 tar.xz 的 sha256 哈希（源：src/stage0）
- F-rust-029: src/bootstrap/README.md「Build phases」一节列出三步：1) 入口脚本（unix 用 `x`、windows 用 `x.ps1`、跨平台 `x.py`）下载 stage0 编译器/Cargo 二进制并编译构建系统自身再调用 bootstrap 二进制；2) bootstrap 二进制读取配置并做 sanity 检查后用预编译 stage0 编译器准备构建 stage 1；3) stage 0 编译器与标准库构建 stage 1 编译器（链接 stage 0 标准库），stage 1 编译器构建 stage 1 标准库，随后 stage 1 编译器产出 stage 2 编译器（链接 stage 1 标准库）（源：src/bootstrap/README.md L22-38）
- F-rust-030: src/bootstrap/README.md 描述构建输出位于 `build/` 目录，子目录含 cache/（按日期缓存 stage0 下载的 tarball）、bootstrap/（debug、release）、misc-tools/、node_modules/、dist/、tmp/ 及按 host triple 命名的目录（源：src/bootstrap/README.md L43-99）
- F-rust-031: src/bootstrap/defaults/ 下存在 4 个默认配置文件：bootstrap.compiler.toml、bootstrap.dist.toml、bootstrap.library.toml、bootstrap.tools.toml（源：src/bootstrap/defaults/ 目录）
- F-rust-032: src/bootstrap/src/core/builder/cli_paths/snapshots/ 目录含约 70 个 `.snap` 快照文件，对应 `x build`/`x check`/`x test`/`x doc`/`x dist`/`x clean`/`x miri`/`x run`/`x setup`/`x vendor`/`x fix`/`x fmt`/`x clippy`/`x install`/`x bench` 等命令行路径解析测试（源：src/bootstrap/src/core/builder/cli_paths/snapshots/）
- F-rust-033: 仓库根的 `x` 是 POSIX shell 脚本：按 `OSTYPE` 选择解释器搜索顺序（cygwin/msys 下 `py python3 python python2 uv`，其余 `python3 python py python2 uv`），找到后以该解释器执行同目录 `x.py`（源：x L1-40）
- F-rust-034: src/bootstrap 目录同时存在 `bootstrap.py`、`bootstrap_test.py`、`configure.py`、`build.rs`、`download-ci-llvm-stamp`、`download-ci-gcc-stamp`、`stdlib-semver-check-stamp`（源：src/bootstrap/ 目录列表）
- F-rust-035: src/tools/x 是独立 Rust crate：`name = "x"`、`version = "0.1.1"`、`description = "Run x.py slightly more conveniently"`（源：src/tools/x/Cargo.toml）

## C. 编译器流水线（compiler/）

### 入口：rustc / rustc_driver / rustc_interface / rustc_session

- F-rust-036: compiler/rustc 的 Cargo.toml `name = "rustc-main"`，其 src/main.rs 是 rustc 二进制入口；依赖 rustc_driver、rustc_driver_impl、rustc_public、rustc_public_bridge、rustc_codegen_ssa（后两者的注释说明它们需进入 sysroot 供稳定 MIR 消费者与代码gen 后端使用）（源：compiler/rustc/Cargo.toml）
- F-rust-037: rustc_driver crate `[lib] crate-type = ["dylib"]`，唯一依赖 rustc_driver_impl，build-dependencies 为 rustc_windows_rc（源：compiler/rustc_driver/Cargo.toml）
- F-rust-038: rustc_driver_impl 的 crate 文档首行为 `//! The Rust compiler.`，并注明 "This API is completely unstable and subject to change."（源：compiler/rustc_driver_impl/src/lib.rs L1-5）
- F-rust-039: `pub fn run_compiler(at_args: &[String], callbacks: &mut (dyn Callbacks + Send))` 位于 rustc_driver_impl/src/lib.rs:173，其文档注释为 "This is the primary entry point for rustc."（源：compiler/rustc_driver_impl/src/lib.rs）
- F-rust-040: rustc_driver_impl 的 features：check_only、jemalloc、llvm、llvm_offload、max_level_info、rustc_randomized_layouts（源：compiler/rustc_driver_impl/Cargo.toml）
- F-rust-041: rustc_interface/src/lib.rs 声明模块 callbacks、diagnostics、interface、limits、passes、queries、util；再导出 `interface::{Config, run_compiler}`、`passes::{DEFAULT_QUERY_PROVIDERS, create_and_enter_global_ctxt, parse}`、`queries::Linker`（源：compiler/rustc_interface/src/lib.rs）
- F-rust-042: `pub struct Config`（rustc_interface/src/interface.rs:318）字段包括：opts（config::Options）、crate_cfg、crate_check_cfg、input、output_dir、output_file、ice_file、file_loader、lint_caps、psess_created、track_state、register_lints、override_queries、extra_symbols、make_codegen_backend、using_internal_features（源：compiler/rustc_interface/src/interface.rs L318-374）
- F-rust-043: `pub fn run_compiler<R: Send>(config: Config, f: impl FnOnce(&Compiler) -> R + Send) -> R`（rustc_interface/src/interface.rs:378），函数体先调用 `rustc_data_structures::sync::set_dyn_thread_safe_mode` 与 `jobserver::initialize`（源：compiler/rustc_interface/src/interface.rs）
- F-rust-044: rustc_interface/src/passes.rs 顶层函数：`parse`(L54)、`configure_and_expand`(L134)、`write_dep_info`(L828)、`write_interface`(L878)、`create_and_enter_global_ctxt`(L936)、`emit_delayed_lints`(L1077)、`run_required_analyses`(L1094)、`analysis`(L1201)、`get_crate_name`(L1357)（源：compiler/rustc_interface/src/passes.rs）
- F-rust-045: rustc_interface/src/queries.rs 定义 `pub struct Linker`(L18)、`pub fn codegen_and_build_linker`(L29)、`pub fn link`(L49)（源：compiler/rustc_interface/src/queries.rs）
- F-rust-046: `pub struct Session`（rustc_session/src/session.rs:328），字段含 `target: Target`、`host: Target`、`opts: config::Options`、`target_tlib_path: SearchPath`（源：compiler/rustc_session/src/session.rs L328-334）
- F-rust-047: rustc_session/src/config.rs:2686 `pub fn build_session_options(early_dcx: &mut EarlyDiagCtxt, matches: &getopts::Matches) -> Options`；session.rs:1257 `pub fn build_session`（源：compiler/rustc_session/src/config.rs、session.rs）

### 解析与宏展开

- F-rust-048: rustc_parse/src/lib.rs 顶层项：`pub mod parser`(L30)、`pub mod lexer`(L35)、`pub fn new_parser_from_source_str`(L94)、`pub fn new_parser_from_file`(L111)、`pub fn source_str_to_stream`(L243)、`pub fn parse_in`(L277)、`pub fn fake_token_stream_for_item`(L291)、`pub fn fake_token_stream_for_crate`(L371)（源：compiler/rustc_parse/src/lib.rs）
- F-rust-049: rustc_parse/src/parser/ 子模块：asm、attr、expr、item、pat、path、stmt、ty、tests（源：compiler/rustc_parse/src/parser/ 目录）
- F-rust-050: rustc_lexer/src/lib.rs 顶层项：`pub struct Token`(L59)、`pub enum TokenKind`(L72)、`pub enum DocStyle`(L209)、`pub enum LiteralKind`(L221)、`pub struct GuardedStr`(L251)、`pub enum RawStrError`(L258)、`pub enum Base`(L271)、`pub fn strip_shebang`(L284)、`pub fn validate_raw_str`(L311)、`pub fn tokenize`(L327)、`pub fn is_whitespace`(L341)、`pub fn is_id_start`(L387)、`pub fn is_id_continue`(L395)、`pub fn is_ident`(L400)、`pub enum FrontmatterAllowed`(L409)、`pub struct Cursor<'a>`(L418)（源：compiler/rustc_lexer/src/lib.rs）
- F-rust-051: rustc_expand/src/lib.rs 模块：build、diagnostics、mbe、placeholders、proc_macro_server、stats（私有），base、config、expand、module、proc_macro（pub）；`pub fn provide(providers: &mut rustc_middle::query::Providers)`(L27)（源：compiler/rustc_expand/src/lib.rs）
- F-rust-052: `pub struct ExtCtxt<'a>`（rustc_expand/src/base.rs:1189）是宏展开上下文结构（源：compiler/rustc_expand/src/base.rs）
- F-rust-053: rustc_expand/src/mbe/ 目录含 quoted.rs（macro-by-example 规则解析）（源：compiler/rustc_expand/src/mbe/ 目录）
- F-rust-054: rustc_ast/src/lib.rs 模块：util、ast、ast_traits、attr、entry、expand、format、mut_visit、node_id、token、tokenstream、visit；`pub use self::ast::*` 将 ast 模块整体再导出（源：compiler/rustc_ast/src/lib.rs）
- F-rust-055: rustc_ast/src/ast.rs 定义：`pub struct Crate`(L550)、`pub enum PatKind`(L871)、`pub enum ExprKind`(L1742)、`pub enum TyKind`(L2518)、`pub enum ItemKind`(L4126)（源：compiler/rustc_ast/src/ast.rs）
- F-rust-056: rustc_builtin_macros/src/lib.rs 的私有模块清单（前 20 个）：alloc_error_handler、assert、autodiff、cfg、cfg_accessible、cfg_eval、cfg_select、compile_error、concat、concat_bytes、define_opaque、derive、deriving、diagnostics、direct_const_arg、edition_panic、eii、env、format、format_foreign（源：compiler/rustc_builtin_macros/src/lib.rs）

### HIR

- F-rust-057: rustc_hir/src/lib.rs 模块：arena、def（pub）、hir、intravisit（pub）、lints（pub）、pat_util（pub）、stable_hash_impls、target_impls；再导出 `pub use hir::*`、`pub use rustc_hir_id::*`、`pub use crate::arena::Arena`（源：compiler/rustc_hir/src/lib.rs）
- F-rust-058: `pub enum TyKind<'hir, Unambig = ()>`（rustc_hir/src/hir.rs:3562）（源：compiler/rustc_hir/src/hir.rs）
- F-rust-059: rustc_ast_lowering/src/lib.rs：`pub fn provide`(L99)、`struct LoweringContext<'a, 'hir>`(L147)、`struct SpanLowerer`(L307)、`fn index_ast`(L498)、`fn lower_to_hir(tcx: TyCtxt<'_>, def_id: LocalDefId) -> hir::MaybeOwner<'_>`(L659)；子模块 asm、block、contract、delegation、diagnostics、expr、format、index、item、pat、path、stability(pub)（源：compiler/rustc_ast_lowering/src/lib.rs）
- F-rust-060: rustc_hir_analysis/src/lib.rs 模块：check(pub)、autoderef(pub)、check_unused、coherence、collect、constrained_generic_params、delegation(pub)、diagnostics(pub)、hir_ty_lowering(pub)、hir_wf_check(pub)、impl_wf_check、outlives、variance；`pub fn provide`(L129)、`pub fn check_crate`(L148)、`pub fn lower_ty`(L242)、`pub fn lower_const_arg_for_rustdoc`(L254)（源：compiler/rustc_hir_analysis/src/lib.rs）
- F-rust-061: rustc_hir_analysis/README.md 内容为两行：指向 rustc-dev-guide 的 hir typeck 章节链接（源：compiler/rustc_hir_analysis/README.md）
- F-rust-062: rustc_hir_typeck/src/lib.rs 子模块（前 20）：_match、autoderef、callee、cast(pub)、check、closure、coercion、demand、diagnostics、diverges、expectation、expr、inline_asm、expr_use_visitor(pub)、fallback、fn_ctxt、gather_locals、intrinsicck、loops、method（源：compiler/rustc_hir_typeck/src/lib.rs）

### 类型系统

- F-rust-063: rustc_middle/src/lib.rs 的 pub 模块：arena、dep_graph、diagnostics、hir、hooks、ich、infer、lint、metadata、middle、mir、mono、ptrauth、queries、query、thir、traits、ty、util、verify_ich（源：compiler/rustc_middle/src/lib.rs）
- F-rust-064: rustc_middle/src/ty/context.rs 定义：`CtxtInterners<'tcx>`(L134)、`CommonTypes<'tcx>`(L304)、`CommonLifetimes<'tcx>`(L379)、`CommonConsts<'tcx>`(L400)、`TyCtxtFeed<'tcx, K>`(L571)、`GlobalCaches<'tcx>`(L663)、`TyCtxt<'tcx>`(L710)、`GlobalCtxt<'tcx>`(L733)、`CurrentGcx`(L815)（源：compiler/rustc_middle/src/ty/context.rs）
- F-rust-065: rustc_middle/src/ty/mod.rs 通过 `pub use self::sty::{...}` 再导出 TyKind、Binder、EarlyBinder、FnSig、PolyFnSig、TypingMode、ParamTy、ParamConst、Alias、AliasTy、AliasTyKind 等（L102-109）（源：compiler/rustc_middle/src/ty/mod.rs）
- F-rust-066: rustc_middle/src/ty/ 的 pub 子模块：abstract_const、adjustment、cast、codec、error、fast_reject、inhabitedness、layout、normalize_erasing_regions、offload_meta、pattern、print、relate、significant_drop_order、sty、trait_def、typetree、util、vtable（源：compiler/rustc_middle/src/ty/mod.rs L130-148）
- F-rust-067: `pub enum TyKind<I: Interner>` 定义于 rustc_type_ir/src/ty_kind.rs:147（编译器中共出现 4 处同名 TyKind：rustc_ast/src/ast.rs:2518、rustc_hir/src/hir.rs:3562、rustc_type_ir/src/ty_kind.rs:147、rustc_public/src/ty/tys.rs:319）（源：Grep 全 compiler/ 检索）
- F-rust-068: rustc_infer/src/lib.rs 模块：diagnostics（私有）、infer（pub）、traits（pub）（源：compiler/rustc_infer/src/lib.rs）
- F-rust-069: rustc_infer/src/infer/mod.rs 定义：`InferCtxtInner<'tcx>`(L97)、`InferCtxt<'tcx>`(L246)、`InferCtxtBuilder<'tcx>`(L588)（源：compiler/rustc_infer/src/infer/mod.rs）
- F-rust-070: rustc_trait_selection/src/lib.rs 的 pub 模块：diagnostics、error_reporting、infer、opaque_types、regions、solve、traits（源：compiler/rustc_trait_selection/src/lib.rs）
- F-rust-071: rustc_type_ir/src/lib.rs 的 pub 模块：data_structures、elaborate、error、fast_reject、inherent、intern、ir_print、lang_items、lift、outlives、region_constraint、relate、search_graph、solve、sty、walk（源：compiler/rustc_type_ir/src/lib.rs）
- F-rust-072: rustc_next_trait_solver/src/lib.rs 的 pub 模块：canonical、coherence、delegate、normalize、placeholder、solve（源：compiler/rustc_next_trait_solver/src/lib.rs）

### 借用检查与 MIR

- F-rust-073: rustc_borrowck/src/lib.rs 模块清单：borrow_set、borrowck_errors、constraints、dataflow、def_use、diagnostics、handle_placeholders、implied_bounds、nll、path_utils、place_ext、places_conflict、polonius、prefixes、region_infer、renumber、root_cx、session_diagnostics、type_check、universal_regions、used_muts、consumers(pub)；`pub fn provide`(L110)、`fn mir_borrowck`(L117)（源：compiler/rustc_borrowck/src/lib.rs）
- F-rust-074: rustc_mir_build/src/lib.rs：mod builder、check_tail_calls、check_unsafety、diagnostics；`pub mod thir`；`pub fn provide`(L19)（源：compiler/rustc_mir_build/src/lib.rs）
- F-rust-075: `pub struct Thir<'tcx>` 定义于 rustc_middle/src/thir.rs:63（THIR 数据结构在 rustc_middle 而非 rustc_mir_build 中）（源：compiler/rustc_middle/src/thir.rs）
- F-rust-076: rustc_mir_transform/src/lib.rs：`pub fn provide`(L214)；其提供的 query provider 函数包括 `mir_keys`(L327)、`mir_const_qualif`(L360)、`mir_built`(L391)、`mir_promoted`(L432)、`mir_for_ctfe`(L492)、`mir_drops_elaborated_and_const_checked`(L537)；pass 编排函数 `pub fn run_analysis_to_runtime_passes`(L597)、`run_analysis_cleanup_passes`(L631)、`run_runtime_lowering_passes`(L644)、`run_runtime_cleanup_passes`(L671)（源：compiler/rustc_mir_transform/src/lib.rs）
- F-rust-077: rustc_mir_transform/src/lib.rs 的 pass 模块（部分）：pass_manager、check_pointers、cost_checker、cross_crate_inline、deduce_param_attrs、elaborate_drop、ffi_unwind_calls、lint、lint_tail_expr_drop_order、liveness、patch、shim、ssa、trivial_const、gvn.rs、inline.rs、sroa.rs（源：compiler/rustc_mir_transform/src/ 目录与 lib.rs）
- F-rust-078: rustc_mir_dataflow/src/lib.rs：pub 模块 debuginfo、impls、move_paths、points、rustc_peek、value_analysis；私有模块 drop_flag_effects、framework、un_derefer；`pub struct MoveDataTypingEnv<'tcx>`(L36)（源：compiler/rustc_mir_dataflow/src/lib.rs）
- F-rust-079: rustc_middle/src/mir/mod.rs 定义：`pub struct Body<'tcx>`(L206)、`pub struct Local`(L866)、`pub enum LocalKind`(L889)、`pub struct LocalDecl<'tcx>`(L967)、`pub enum LocalInfo<'tcx>`(L1074)、`pub struct BasicBlock`(L1300)、`pub struct BasicBlockData<'tcx>`(L1319)（源：compiler/rustc_middle/src/mir/mod.rs）

### 代码生成

- F-rust-080: rustc_codegen_ssa/src/lib.rs 的 pub 模块：assert_module_sources、back、base、codegen_attrs、common、debuginfo、diagnostics、meth、mir、mono_item、size_of_val、target_features、traits；结构体 `ModuleCodegen<M>`(L58)、`CompiledModule`(L123)、`NativeLib`(L215)、`SymbolExport`(L237)（源：compiler/rustc_codegen_ssa/src/lib.rs）
- F-rust-081: `pub trait CodegenBackend`（rustc_codegen_ssa/src/traits/backend.rs:37）、`pub trait BackendTypes`(L21)、`pub trait ExtraBackendMethods`(L164)；traits/ 目录共定义约 20 个 codegen 后端需实现的 trait（含 AbiBuilderMethods、AsmBuilderMethods、AsmCodegenMethods、BuilderMethods、ConstCodegenMethods、CoverageInfoBuilderMethods、DebugInfoCodegenMethods、DebugInfoBuilderMethods、IntrinsicCallBuilderMethods、MiscCodegenMethods、ModuleBufferMethods、PreDefineCodegenMethods、StaticCodegenMethods、StaticBuilderMethods、WriteBackendMethods）（源：compiler/rustc_codegen_ssa/src/traits/）
- F-rust-082: rustc_codegen_llvm/src/lib.rs 模块清单：abi、allocator、asm、attributes、back、base、builder、callee、common、consts、context、coverageinfo、debuginfo、declare、diagnostics、intrinsic、llvm、llvm_util、macros、mono_item 等（源：compiler/rustc_codegen_llvm/src/lib.rs）
- F-rust-083: rustc_codegen_cranelift 的 Cargo.toml：`name = "rustc_codegen_cranelift"`、`version = "0.1.0"`、`edition = "2024"`、`crate-type = ["dylib"]`；依赖 cranelift-codegen/frontend/module/native/jit/object 均为 0.134.0；被根 workspace exclude（源：compiler/rustc_codegen_cranelift/Cargo.toml 与根 Cargo.toml）
- F-rust-084: rustc_codegen_gcc 的 Cargo.toml：`name = "rustc_codegen_gcc"`、`version = "0.1.0"`、`authors = ["Antoni Boucher <bouanto@zoho.com>"]`、`crate-type = ["dylib"]`；依赖 `gccjit = { version = "3.3.0", features = ["dlopen"] }`；features `master = ["gccjit/master"]`、`default = ["master"]`；被根 workspace exclude（源：compiler/rustc_codegen_gcc/Cargo.toml）
- F-rust-085: rustc_monomorphize/src/lib.rs：mod collector、diagnostics、graph_checks、mono_checks、offload、partitioning、util；`pub fn provide`(L54)、`fn custom_coerce_unsize_info`(L27)（源：compiler/rustc_monomorphize/src/lib.rs）

### 基础设施

- F-rust-086: rustc_span/src/lib.rs：pub 模块 source_map、edition、hygiene、def_id、edit_distance、symbol、fatal_error、profiling；结构体 `Spanned<T>`(L97)、`SessionGlobals`(L114)、`MetavarSpansMap`(L200)、`RealFileName`(L305)；函数 `create_session_globals_then`(L144)、`with_session_globals`(L182)（源：compiler/rustc_span/src/lib.rs）
- F-rust-087: `pub struct Span` 定义于 rustc_span/src/span_encoding.rs:82（源：compiler/rustc_span/src/span_encoding.rs）
- F-rust-088: `pub struct Symbol(SymbolIndex)`（rustc_span/src/symbol.rs:2674）；文件中引用 `PREDEFINED_SYMBOLS_COUNT` 常量（L3054）（源：compiler/rustc_span/src/symbol.rs）
- F-rust-089: rustc_errors/src/lib.rs：pub 模块 annotate_snippet_emitter_writer、codes、emitter、formatting、json、markdown、timings；结构体 `CodeSuggestion`(L157)、`Substitution`(L193)、`ExplicitBug`(L263)、`DelayedBugPanic`(L267)、`DiagCtxt`(L272)、`DiagCtxtHandle<'a>`(L277)、`DiagCtxtFlags`(L415)（源：compiler/rustc_errors/src/lib.rs）
- F-rust-090: rustc_query_impl/src/lib.rs：私有模块 dep_kind_vtables、diagnostics、execution、handle_cycle_error、incremental、job、query_vtables、self_profile；`pub fn query_system<'tcx>`(L29)、`pub fn provide(providers: &mut rustc_middle::util::Providers)`(L50)（源：compiler/rustc_query_impl/src/lib.rs）
- F-rust-091: `rustc_queries! {` 宏调用出现在 compiler/rustc_middle/src/queries.rs:141，是全仓库唯一一处；其上方注释说明每个 query 对应 `Providers` 结构的一个函数指针字段与 `tcx: TyCtxt` 上的方法（源：compiler/rustc_middle/src/queries.rs L130-141）
- F-rust-092: rustc_queries! 中定义的 query 示例（含描述）：`derive_macro_expansion`（"expanding a derive (proc) macro"，cache_on_disk）、`trigger_delayed_bug`、`registered_attr_tools`（arena_cache）、`registered_lint_tools`、`early_lint_checks`（"perform lints prior to AST lowering"）、`env_var_os`（eval_always，"get the value of an environment variable"）、`resolutions`（"getting the resolver outputs"）、`resolver_for_lowering_raw`（eval_always + no_hash）（源：compiler/rustc_middle/src/queries.rs L141-203）
- F-rust-093: rustc_middle/src/query/ 目录结构：caches.rs（`DefaultCache<K,V>`L43、`SingleCache<V>`L86、`DefIdCache<V>`L128）、calls.rs（`TyCtxtAt<'tcx>`L16、`TyCtxtEnsureOk`L31、`TyCtxtEnsureResult`L37、`TyCtxtEnsureDone`L43）、erase.rs、keys.rs（`LocalCrate`L26）、job.rs（`QueryJobId`L15、`QueryJob<'tcx>`L19、`QueryState<'tcx,K>`L76、`QueryStackFrame<'tcx>`L90、`QueryCycle<'tcx>`L102）、on_disk_cache、query_api、modifiers、into_query_key（源：compiler/rustc_middle/src/query/）
- F-rust-094: rustc_metadata/src/lib.rs：私有模块 dependency_format、eii、foreign_modules、host_dylib、native_libs、rmeta；pub 模块 creader、diagnostics、fs、locator（源：compiler/rustc_metadata/src/lib.rs）
- F-rust-095: rustc_metadata/src/rmeta/mod.rs:63 `const METADATA_VERSION: u8 = 10;`；L70 `pub const METADATA_HEADER: &[u8] = &[b'r', b'u', b's', b't', 0, 0, 0, METADATA_VERSION];`；L212 注释"If you do modify this struct, also bump the [`METADATA_VERSION`] constant."（源：compiler/rustc_metadata/src/rmeta/mod.rs）
- F-rust-096: rustc_resolve/src/lib.rs：私有模块 build_reduced_graph、check_unused、def_collector、diagnostics、effective_visibilities、ident、imports、late、macros；`pub mod rustdoc`；结构体 `ModuleData<'ra>`(L678)、`Module<'ra>`(L718)、`LocalModule<'ra>`(L723)、`ExternModule<'ra>`(L728)（源：compiler/rustc_resolve/src/lib.rs）

## D. 标准库（library/）

- F-rust-097: library/Cargo.toml：`[workspace] resolver = "1"`，members = `["std", "sysroot", "coretests", "alloctests"]`；exclude = `["stdarch", "windows_link"]`（各自有独立 workspace，注释说明）（源：library/Cargo.toml）
- F-rust-098: library/ 顶层子目录完整清单（23 个）：alloc、alloctests、backtrace、compiler-builtins、core、coretests、panic_abort、panic_unwind、portable-simd、proc_macro、profiler_builtins、rtstartup、rustc-std-workspace-alloc、rustc-std-workspace-core、rustc-std-workspace-std、std、std_detect、stdarch、sysroot、test、unwind、windows_link、windows-sys（源：library/ 目录列表）
- F-rust-099: library/Cargo.toml `[profile.release.package.compiler_builtins] codegen-units = 10000`，注释："place every single intrinsic into its own object file to avoid symbol clashes with the system libgcc"（源：library/Cargo.toml）
- F-rust-100: library/Cargo.toml 定义 `[profile.dist]`：`inherits = "release"`、`codegen-units = 1`、`debug = 1`，rustflags 含 `"-Cembed-bitcode=yes"`、`"-Zunstable-options"`、`"-Cforce-frame-pointers=non-leaf"`；注释说明该 profile 由 bootstrap 用于预构建 libstd 产物（源：library/Cargo.toml）
- F-rust-101: library/Cargo.toml `[patch.crates-io]` 将 rustc-std-workspace-core/alloc/std 与 windows-sys 指向 library/ 下的本地路径（源：library/Cargo.toml）
- F-rust-102: library/Cargo.toml 对 panic_abort 设置 `[profile.dev.package.panic_abort] rustflags = ["-Cpanic=abort"]` 与 `[profile.release.package.panic_abort] rustflags = ["-Cpanic=abort"]`，注释"panic_abort must always be compiled with panic=abort, even when the rest of the sysroot is panic=unwind"（源：library/Cargo.toml）
- F-rust-103: library/sysroot/Cargo.toml：`name = "sysroot"`、`version = "0.0.0"`、`edition = "2024"`；注释"this is a dummy crate to ensure that all required crates appear in the sysroot"；依赖 proc_macro（public）、profiler_builtins（optional）、std（public）、test（public）；`default = ["panic-unwind"]`，其余 feature 均转发给 std（源：library/sysroot/Cargo.toml）
- F-rust-104: library/std/Cargo.toml：`name = "std"`、`version = "0.0.0"`、`edition = "2024"`；另有 [[test]] targets：pipe-subprocess、sync、thread_local（源：library/std/Cargo.toml）
- F-rust-105: library/core/src/lib.rs crate 文档："The Rust Core Library is the dependency-free foundation of The Rust Standard Library… It links to no upstream libraries, no system libraries, and no libc."；"The core library is *minimal*: it isn't even aware of heap allocation, nor does it provide concurrency or I/O."（源：library/core/src/lib.rs L1-14）
- F-rust-106: library/core/src/lib.rs 内部属性：`#![stable(feature = "core", since = "1.6.0")]`、`#![no_core]`、`#![rustc_coherence_is_core]`、`#![rustc_preserve_ub_checks]`（源：library/core/src/lib.rs L46-66）
- F-rust-107: library/core/src/lib.rs 文档列出 core 依赖的已存在符号：`memcpy`、`memmove`、`memset`、`memcmp`、`bcmp`、`strlen`（由 codegen 后端或 compiler-builtins 提供）、panic handler（`#[panic_handler]`）、`rust_eh_personality`（源：library/core/src/lib.rs L21-44）
- F-rust-108: library/core/src/lib.rs 顶层 pub 模块清单：prelude、f128、f16、f32、f64、num、hint、intrinsics、mem、profiling、ptr、ub_checks、borrow、clone、cmp、convert、default、error、field、index、marker、ops、any、array、ascii、asserting、async_iter、bstr、cell、char、ffi、io、iter、net、option、os、panic、panicking、pat、pin、process、random、range、result、sync、unsafe_binder、fmt、hash、slice、str、time、wtf8、unicode、future、task、alloc、view、primitive、arch、simd、from、autodiff、offload、contracts（源：library/core/src/lib.rs L199-389）
- F-rust-109: library/core/src 与 library/alloc/src、library/std/src 各含一个 `lib.miri.rs` 文件（源：library/{core,alloc,std}/src/ 目录）
- F-rust-110: library/std/src/lib.rs crate 文档："The Rust Standard Library is the foundation of portable Rust software, a set of minimal and battle-tested shared abstractions for the broader Rust ecosystem."；"std is available to all Rust crates by default."（源：library/std/src/lib.rs L1-12）
- F-rust-111: library/std/src/lib.rs 顶层 pub 模块清单：prelude、rt、f128、f16、f32、f64、thread、ascii、backtrace、bstr、collections、env、error、ffi、fs、hash、io、net、num、os、panic、pat、path、process、random、sync、time、view、simd、autodiff、offload、task、arch、sys、alloc、from（另有私有模块 macros、std_float、panicking、backtrace_rs）（源：library/std/src/lib.rs L459-782）
- F-rust-112: library/std/src/sys/mod.rs 模块：私有 configure_builtins、helpers、pal、personality；pub 模块 alloc、args、backtrace、cmath、env、env_consts、exit、fd、fs、io、net 等（源：library/std/src/sys/mod.rs）
- F-rust-113: library/std/src/os/ 平台子目录清单：aix、android、cygwin、darwin、dragonfly、espidf、fd、freebsd、fuchsia、haiku、hermit、horizon、hurd、illumos、ios、l4re、linux、macos、motor、net、netbsd、nto、nuttx、openbsd、raw、redox、rtems、solaris、solid、trusty、uefi、unix、vita、vxworks、wasi、wasip2、windows、xous（源：library/std/src/os/ 目录）
- F-rust-114: library/std/src/env.rs 顶层 pub 项：`current_dir`(L53)、`set_current_dir`(L80)、`vars`(L135)、`vars_os`(L160)、`var`(L228)、`var_os`(L264)、`split_paths`(L483)、`join_paths`(L578)、`home_dir`(L646)、`temp_dir`(L706)、`current_exe`(L757)；结构体 `Vars`(L90)、`VarsOs`(L100)、`SplitPaths<'a>`(L447)、`JoinPathsError`(L511)（源：library/std/src/env.rs）
- F-rust-115: library/std/src/fs.rs 顶层 pub 项：结构体 `File`(L135)、`Dir`(L189)、`Metadata`(L202)、`ReadDir`(L220)、`DirEntry`(L239)、`OpenOptions`(L279)、`FileTimes`(L285)、`Permissions`(L298)、`FileType`(L305)、`DirBuilder`(L313)；函数 `read`(L346)、`read_to_string`(L389)、`write`(L427)、`set_times`(L470)、`set_times_nofollow`(L511)（源：library/std/src/fs.rs）
- F-rust-116: library/std/src/rt.rs：`pub use crate::panicking::{begin_panic, panic_count}` 与 `pub use core::panicking::{panic_display, panic_fmt}`；定义宏 `rtprintpanic!`(L40)、`rtabort!`(L53)、`rtassert!`(L62)、`rtunwrap!`(L70)；`unsafe fn init(argc: isize, argv: *const *const u8, sigpipe: u8)`(L111)、`fn lang_start<T: crate::process::Termination + 'static>(main: fn() -> T, …)`(L199)、`fn lang_start_internal`(L152)（源：library/std/src/rt.rs）
- F-rust-117: library/std/src/pat.rs 全文两行：`//! Helper module for exporting the 'pattern_type' macro` 与 `pub use core::pattern_type;`（源：library/std/src/pat.rs）
- F-rust-118: library/std/src 存在 build.rs；library/rtstartup 含 rsbegin.rs 与 rsend.rs（源：library/std/ 与 library/rtstartup/ 目录）
- F-rust-119: library/alloc/src 顶层源文件清单：alloc.rs、borrow.rs、boxed.rs、bstr.rs、fmt.rs、intrinsics.rs、lib.rs、lib.miri.rs、macros.rs、panicking.rs、rc.rs、slice.rs、str.rs、string.rs、sync.rs、task.rs 及 boxed/、ffi/、io/、raw_vec/、vec/、wtf8/ 子目录（源：library/alloc/src/ 目录）
- F-rust-120: library/panic_unwind/src 含平台实现文件：dummy.rs、gcc.rs、lib.rs、miri.rs、seh.rs；library/panic_abort/src 含 lib.rs 与 zkvm.rs（源：library/panic_unwind/src/、library/panic_abort/src/ 目录）

## E. rustdoc 与工具

- F-rust-121: src/librustdoc/Cargo.toml：`name = "rustdoc"`、`version = "0.0.0"`、`edition = "2024"`（源：src/librustdoc/Cargo.toml）
- F-rust-122: src/librustdoc/ 子目录：clean（含 cfg、types、utils）、doctest、formats、html（含 escape、highlight、layout、length_limit、markdown、render、static、templates、toc、url_parts_builder）、json、passes（含 lint）、theme（源：src/librustdoc/ 目录）
- F-rust-123: src/librustdoc/lib.rs 模块清单：calculate_doc_coverage、clean、config、core、display、docfs、doctest、error、externalfiles、fold、formats、html(pub)、json、markdown、passes、scrape_examples、theme、visit、visit_ast、visit_lib（源：src/librustdoc/lib.rs L99-120）
- F-rust-124: src/librustdoc/lib.rs:122 `pub fn main() -> ExitCode`；L805 `fn main_args(early_dcx: &mut EarlyDiagCtxt, at_args: &[String])`（源：src/librustdoc/lib.rs）
- F-rust-125: src/tools/rustdoc/main.rs 全文 13 行：`#![feature(rustc_private)]`、`extern crate rustc_driver;`、调用 `rustc_driver::override_c_allocator_in_binary!()`，`fn main() -> ExitCode { rustdoc::main() }`（源：src/tools/rustdoc/main.rs）
- F-rust-126: src/tools/miri/Cargo.toml：`description = "An experimental interpreter for Rust MIR (core driver)."`、`name = "miri"`、`version = "0.1.0"`（源：src/tools/miri/Cargo.toml）
- F-rust-127: src/tools/miri/ 目录结构：src/（alloc、bin、concurrency、intrinsics、shims/unix、shims/windows、machine.rs、eval.rs、operator.rs、provenance_gc.rs、sym.rs 等）、cargo-miri/、miri-script/、priroda/、genmc-sys/、test-cargo-miri/、tests/（fail、panic、pass、utils、ui.rs）（源：src/tools/miri/ 目录）
- F-rust-128: src/tools/miri/src/lib.rs：`pub mod sym`(L99)、`pub mod native_lib`(L113)（源：src/tools/miri/src/lib.rs）
- F-rust-129: src/tools/ 顶层目录完整清单（46 个）：build-manifest、bump-stage0、cargo、cargotest、clippy、collect-license-metadata、compiletest、coverage-dump、enzyme、error_index_generator、features-status-dump、generate-copyright、generate-windows-sys、html-checker、jsondocck、jsondoclint、libcxx-version、linkchecker、lint-docs、lld-wrapper、llvm-bitcode-linker、miri、miropt-test-tools、nix-dev-shell、opt-dist、remote-test-client、remote-test-server、replace-version-placeholder、run-make-support、rust-analyzer、rust-installer、rustbook、rustc-perf、rustdoc、rustdoc-gui-test、rustdoc-js、rustdoc-themes、rustfmt、test-float-parse、tidy、tier-check、unicode-table-generator、unstable-book-gen、wasm-component-ld、x（源：src/tools/ 目录列表）
- F-rust-130: 根 Cargo.toml workspace members 中的 src/tools 成员共 34 个（含 clippy/clippy_dev、miri/cargo-miri 双成员）；而 src/tools/ 磁盘目录共 46 个，两者差集（如 cargo、enzyme、rust-analyzer、rustc-perf、rustbook、error_index_generator 等）不在根 workspace members 中（源：Cargo.toml 与 src/tools/ 目录对照）
- F-rust-131: src/tools/rust-analyzer/ 含独立 Cargo.toml、Cargo.lock、rust-version、josh-sync.toml、AGENTS.md、AI_POLICY.md 等文件，是 subtree/submodule 型外部维护工具（源：src/tools/rust-analyzer/ 目录）
- F-rust-132: src/bootstrap/src/bin/ 存在 main.rs、rustc.rs、rustdoc.rs 三个 bin 源文件，对应 bootstrap crate 的三个二进制（源：src/bootstrap/src/bin/ 目录与 src/bootstrap/Cargo.toml）
- F-rust-133: tests/ui、tests/rustdoc-*（gui/html/js/js-std/json/ui）、tests/debuginfo、tests/incremental、tests/mir-opt、tests/run-make 等测试套件目录均存在于 tests/ 下；src/tools/compiletest（含 src/runtest/、directives.rs、executor.rs 等）是测试执行器 crate 且在根 workspace members 中（源：tests/ 目录、src/tools/compiletest/）

---
### 采集覆盖说明（非事实条目）
- 实读文件：README.md、x.py、Cargo.toml（根/library/sysroot/std/bootstrap/rustc/rustc_driver/rustc_driver_impl/rustc_interface/rustc_session/rustc_codegen_cranelift/rustc_codegen_gcc/librustdoc）、src/version、src/stage0（前 120 行）、src/bootstrap/{README.md,src/lib.rs,src/core/mod.rs,src/core/compiler.rs,src/core/builder/mod.rs（节选）,src/core/build_steps/mod.rs,src/core/config/mod.rs（grep）,Cargo.toml}、compiler 各 crate 的 lib.rs/关键文件（grep 定位）、library/{core,std}/src/lib.rs（节选）、library/std/src/{env,fs,rt,pat}.rs（grep）、src/librustdoc/{lib.rs,Cargo.toml}、src/tools/rustdoc/main.rs、x（根脚本）。
- 行号均为采集时快照，后续提交可能漂移；每条事实可经所示路径 + 符号名复核。
