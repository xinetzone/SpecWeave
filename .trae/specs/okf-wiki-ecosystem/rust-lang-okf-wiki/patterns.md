# patterns.md — rust-lang OKF Wiki 生成模式沉淀（C 阶段 / G5 门）

> 源自 spec `rust-lang-okf-wiki` 实战萃取。触发场景：为超大规模开源 monorepo（rust-lang/rust 62,286 文件）生成 OKF 知识包。

## 模式一：超大规模 monorepo 分层采样（Mega-Monorepo Layered Sampling）

**触发场景**：源码仓库 >5 万文件、核心模块 >50 个 crate，命中 source-code-to-okf-wiki 适用性决策树「超大规模源码」分支。

**核心步骤**：
1. R 阶段不逐 crate 精读，按**编译流水线阶段横向切片**（driver→parse→HIR→typeck→borrowck/MIR→codegen），每阶段只读 3-6 个核心 crate 的 lib.rs 层（crate 描述、pub 结构、模块清单）
2. 标准库按**分层架构纵切**（core/alloc/std 三层），每层读目录组织 + 2-4 个代表性源文件
3. tests/、llvm-project 等巨型子模块只登记角色，不精读
4. E 阶段概念文档与采样切片一一对应（一篇文档 = 一个流水线阶段或一个分层）

**反模式（本次实战验证）**：
- ❌ **计数凭印象**：AI 对"compiler/ 有几个子目录""tools/ 有几个工具"的估计系统性漂移（本次 70→79、46→45、26→22、37→42 共 15 类计数虚构，全部经 Grep 枚举修正）——数字类事实必须以目录枚举命令实测，不得来自模型估计
- ❌ **用过时二手资料校准路径**：网上教程说 cargo 主 crate 在 `src/cargo/`，master 基线已重组到 `src/`，且 `Config` 已更名 `GlobalContext`——结构坐标必须以本次 R 阶段实测为准
- ❌ 把 62k 文件仓库当常规仓库全量精读——上下文预算必然爆炸，采信分层采样
- ❌ 域索引计数与并行任务冲突时强行覆盖——工作区存在并行 spec 任务（protobuf/containers）时，根索引计数以"磁盘实际 + 导航表格自洽"为准（本次 268/32/13），不用本任务的理论值（266/31/12）

**迁移验证**：✅ 已在 rust-lang/rust（编译器+标准库+bootstrap 三世界）验证；可迁移至 llvm/llvm-project、gcc 等同量级仓库。

## 模式二：三仓库一域的锚点束组织（Anchor-Bundle Domain Organization）

**触发场景**：一个技术域含"编译器+构建工具+设计决策档案"多仓库组合（如 rust 的 rust/cargo/rfcs，可类比 Python 的 cpython+pip+peps）。

**核心步骤**：
1. 语言实现仓库作**锚点束**（rust/rust 镜像 python/cpython 定位），文档量最大（12 篇 concepts）
2. 生态工具仓库（cargo）按命令数据流组织；流程档案仓库（rfcs）按主题家族分组
3. 跨 bundle 呼应在洞察阶段显式登记（如 rust 的 HIR/MIR 篇 ↔ rfcs 的编译器架构演进篇），E 阶段写入"相关概念"
4. 域索引单文件汇总三束，根总索引只加一行

**反模式**：
- ❌ 三仓库事实清单混编一个 facts.md——按仓库分文件（facts-rust/cargo/rfcs.md），编号前缀隔离（F-rust-/F-cargo-/F-rfcs-），V 阶段才能分源 Grep 验证
- ❌ 把 RFC 档案库当代码库读——rfcs 的"API 验证"退化为 RFC 编号↔文件存在性验证，验证策略随信源类型调整

## 质量门通过记录（G1-G5）

- G1：454 条事实零推断词（三个子代理独立自检通过）
- G2：12 条洞察四元组完整，454 事实 100% 映射
- G3：三 bundle 均信源先行、分批 ≤7、index 最后
- G4：~112 API 验证点、15 类虚构全部修复、utf8 门通过、rust 域 toctree 零问题（containers 域 52 处不可达为并行任务存量，不在本 spec 范围）
- G5：本文档（2 模式、6 反模式 ≥5 达标）
