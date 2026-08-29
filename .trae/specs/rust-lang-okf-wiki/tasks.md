# Tasks

> 执行顺序：R → I → E → V → C。E 阶段内：references 先行、concepts 分批（≤7）、examples、index 最后。

## R 阶段：源码事实采集（零推测，G1 门）

- [x] Task 1: rust 仓库事实采集——编译器流水线
  - [x] Task 1.1: 读取仓库结构（x.py、Cargo.toml、compiler/ 90+ crates 清单、README），采集版本与目录布局事实
  - [x] Task 1.2: 按流水线阶段阅读核心 crates：rustc_driver/rustc_interface（入口）、rustc_parse/rustc_lexer/rustc_expand（解析与宏展开）、rustc_hir/rustc_ast_lowering（HIR）、rustc_infer/rustc_trait_selection/rustc_type_ir（类型系统与 trait 求解）、rustc_borrowck/rustc_mir_*（借用检查与 MIR）、rustc_codegen_ssa/rustc_codegen_llvm（代码生成）、rustc_middle/rustc_span/rustc_errors（基础设施）
  - [x] Task 1.3: 采集标准库事实：library/ 目录分层（core/alloc/std/proc_macro/sysroot）、std 关键模块（env/fs/rt/pat）、Cargo.toml workspace 组织
  - [x] Task 1.4: 采集 bootstrap 构建系统事实：src/bootstrap、stage0、构建阶段（stage0/stage1/stage2）、tools/ 清单
  - [x] 产出：`.trae/specs/rust-lang-okf-wiki/facts-rust.md`（编号 F-rust-xxx，每条含源码路径，无"用于/目的是"等推断词）——133 条

- [x] Task 2: cargo 仓库事实采集
  - [x] Task 2.1: 读取 cargo 目录结构（src/bin、src/cargo/lib.rs、crates/），采集 crate 组织事实——注：master 基线已重组，主 crate 位于 src/（根 Cargo.toml package+workspace 合一）
  - [x] Task 2.2: 按模块阅读：context/（配置 schema）、ops/（cargo_new/run/test/doc、resolve、lockfile）、resolver/、sources/、workspace/、util/（auth/graph/progress 等）、compiler/（links/lto/unit）——注：Config 已更名 GlobalContext（src/context/mod.rs）
  - [x] Task 2.3: 采集 CLI 层（cli.rs/main.rs 子命令分发）、doc/man 手册、credential 机制事实
  - [x] 产出：`.trae/specs/rust-lang-okf-wiki/facts-cargo.md`（F-cargo-xxx）——144 条

- [x] Task 3: rfcs 仓库事实采集
  - [x] Task 3.1: 读取 README.md、0000-template.md、generate-book.py，采集 RFC 流程事实（状态、编号、合并机制）
  - [x] Task 3.2: 精读代表性 RFC（26 篇），采集其核心决策事实
  - [x] Task 3.3: 采集 text/ 目录规模与分类分布事实——639 个顶层 .md，编号 0001~3984
  - [x] 产出：`.trae/specs/rust-lang-okf-wiki/facts-rfcs.md`（F-rfcs-xxx）——177 条

## I 阶段：架构洞察与知识地图（G2 门）

- [x] Task 4: 基于三份事实清单各提炼 3-5 个洞察四元组（陈述+证据+反常识+行动），设计每个 bundle 的概念分组、学习路径与概念-事实映射
  - [x] 产出：`.trae/specs/rust-lang-okf-wiki/insights.md`（含三仓库洞察与知识地图）——12 条洞察，454 事实 100% 映射

## E 阶段：批量生成 OKF 文档（G3 门，信源先行、分批 ≤7、index 最后）

- [x] Task 5: 生成 `rust/rust/` bundle（rustc 编译器与标准库，锚点束）
  - [x] Task 5.1: 先生成 references/（rustc 源码信源、标准库信源）及 references/index.md
  - [x] Task 5.2: 分批生成 concepts/（12 篇，两批 00-05/06-11）
  - [x] Task 5.3: 生成 examples/（x.py 构建流程走读、std 模块结构剖析）
  - [x] Task 5.4: 最后生成子目录 index.md、根 index.md（含 okf_version 与 toctree）、log.md——共 21 文件，133 事实全覆盖，84 处交叉链接

- [x] Task 6: 生成 `rust/cargo/` bundle
  - [x] Task 6.1: 先生成 references/（cargo 源码信源）及 index
  - [x] Task 6.2: 分批生成 concepts/（10 篇 00-09，两批，insights 规划表实列 10 行以保证 144 事实 100% 覆盖）
  - [x] Task 6.3: 生成 examples/（cargo new 源码路径追踪、Cargo.toml 解析流程）
  - [x] Task 6.4: 最后生成各级 index.md 与 log.md——共 18 文件，144 事实全覆盖，68 处交叉链接

- [x] Task 7: 生成 `rust/rfcs/` bundle
  - [x] Task 7.1: 先生成 references/（rfcs 信源：仓库结构+精选 RFC 清单）及 index
  - [x] Task 7.2: 分批生成 concepts/（8 篇 00-07，两批）
  - [x] Task 7.3: 最后生成各级 index.md 与 log.md——共 13 文件，177 事实全覆盖，160 处 F 编号引用

- [x] Task 8: 生成 `rust/index.md` 域索引（含 toctree 引用三个 bundle）并更新 `bundles/index.md` 根总索引（mermaid 图、入门路径、十二域导航表、计数 266/31/12、toctree 追加 rust/index）

## V 阶段：独立验证与修复（G4 门）

- [x] Task 9: 结构与格式验证：bundle 目录结构、frontmatter 字段完整性、sources 指向存在文件、`/` 开头交叉链接无断裂、子目录 index 无 frontmatter——10/10 项通过（38 个内容文档九字段 frontmatter 齐全、52 文件 UTF-8 无 BOM、链接零断裂）
- [x] Task 10: API 真实性 Grep 验证：约 112 个验证点，发现并修复 15 类虚构（rust 8 类计数漂移：compiler/ 70→79、tools 46→45 等；cargo 3 类：util 子模块 37→42、BUILTIN_ALIASES 帮助文本等），修复后零残留
- [x] Task 11: 在 awesome-okf-xs 内运行 `invoke gates.toctrees` 与 `invoke gates.utf8`——utf8 通过（5601 文件）；toctrees 报 52 处不可达全部位于 containers/ 域（并行任务存量问题，与 rust 变更无关），rust 域经 `check-toctrees.py | Select-String rust` 过滤验证零问题

## C 阶段：模式沉淀（G5 门）

- [x] Task 12: 回顾流程，将超大规模 monorepo（rust-lang/rust）分层采样经验沉淀到 `.trae/specs/rust-lang-okf-wiki/patterns.md`（2 个模式、6 个实战反模式）；spec 目录三件套齐备、tasks 勾选完整

# Task Dependencies

- Task 1/2/3 相互独立，可并行委派
- Task 4 依赖 Task 1-3
- Task 5/6/7 依赖 Task 4，三者可并行（每个 bundle 独立闭环）
- Task 8 依赖 Task 5-7
- Task 9-11 依赖 Task 8
- Task 12 依赖 Task 9-11
