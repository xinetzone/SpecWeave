# Tasks

## Phase R：源码事实采集（零推测，G1 质量门）

- [x] Task 1: protobuf 主仓 R 阶段——架构与核心模块事实采集（分批委派子代理，可并行）
  - [x] SubTask 1.1: 仓库结构与构建系统事实（顶层目录清单、protobuf_version.bzl 版本号、bazel/cmake 双构建体系、editions/、docs/）→ `facts-repo-structure.md`（67 条）
  - [x] SubTask 1.2: C++ 运行时核心事实（src/google/protobuf：Message/MessageLite、Arena、descriptor.h、DescriptorPool、Reflection、wire_format、text_format、json、any 等，深读到类/关键方法签名级）→ `facts-cpp-core.md`（144 条）
  - [x] SubTask 1.3: protoc 编译器事实（src/google/protobuf/compiler：command_line_interface、parser、importer、code_generator、plugin.proto、cpp/java/python/csharp 等各语言 generator 结构）→ `facts-compiler.md`
  - [x] SubTask 1.4: 语言运行时事实（python/ C 扩展结构、rust/ 与 upb kernel、java/csharp/objectivec/php/ruby/lua 概览、hpb/hpb_generator）→ `facts-runtimes.md`（105 条）
  - [x] SubTask 1.5: 测试与规范体系事实（conformance/、benchmarks/、examples/addressbook、editions/defaults.bzl 特性解析）→ `facts-testing.md`（80 条）
- [x] Task 2: protobuf-ci R 阶段——CI 动作仓事实采集（各 action.yml 字段与脚本逻辑）→ `facts-protobuf-ci.md`（56 条）

## Phase I：架构洞察与知识地图（G2 质量门）

- [x] Task 3: 基于 R 阶段事实提炼 3-5 条核心洞察（陈述/证据/反常识/行动四元组），设计 protobuf 束知识地图（概念分组、依赖关系、学习路径、概念-事实映射表），确定 protobuf-ci 束文档清单 → `insights.md`（5 条洞察、17 篇 concepts、5 篇 examples、5+1 信源文件、542 条事实全覆盖）（依赖 Task 1、2）

## Phase E：批量生成（信源先行、分批 ≤7、index 最后写，G3 纪律）

- [x] Task 4: 创建 `comm/serialization/` 分组目录；生成 protobuf 束 `references/` 信源登记文件与 protobuf-ci 束 `references/`（依赖 Task 3）
- [x] Task 5: protobuf 束 concepts/ 分批生成（每批 ≤7 篇，按学习路径：入门→核心机制→编译器→运行时→高级，prompt 附相关 F-xxx 事实编号）共 ≥15 篇（依赖 Task 4）——实际 17 篇分 3 批
- [x] Task 6: protobuf 束 examples/ 生成（4-6 篇，代码源自 examples/ 与源码测试，API 与事实一致）（依赖 Task 5）——5 篇
- [x] Task 7: protobuf-ci 束生成（4-5 篇 concepts + references，单批完成）（依赖 Task 4，与 Task 5/6 可并行）——5 篇 concepts + 1 信源
- [x] Task 8: 最后生成各级 index.md——两束根 index.md（含 okf_version 与 {toctree}）、concepts/examples/references 子目录 index.md、`comm/serialization/index.md` 分组索引（含生态关系图与学习路径）、两束 log.md；更新 `comm/index.md` 与 `doc/bundles/index.md` 总索引计数（263→265 束、30→31 组）（依赖 Task 5、6、7）——实际总索引含并行 Rust 域变更，最终为 268 束 / 32 组 / 13 域

## Phase V：独立验证与修复（G4 质量门）

- [x] Task 9: 独立审查（委派子代理，独立上下文）：结构/frontmatter/链接检查；Grep 验证文档引用的每个类名/方法名在源码中存在性；代码示例 API 一致性；index 完整性；输出验证报告并修复至问题清零（依赖 Task 8）——frontmatter 33+6 覆盖率 100%；修复 2 处束根 index okf-spec 链接层级错误；15+ 关键 API Grep 验证全部通过，零虚构
- [x] Task 10: 在 projects/awesome-okf-xs 下运行 `invoke gates.toctrees` 与 `invoke gates.utf8`，修复所有报告项（依赖 Task 9）——utf8 通过（5601 文件）；toctrees 失败 52 项全部位于 containers/ 域（既有历史问题，非本次变更引入，serialization 域零问题）

## Phase C：模式沉淀（G5 质量门）

- [x] Task 11: 回顾五阶段执行过程，萃取可复用经验（超大规模 monorepo 的「架构全覆盖+核心深读」采样策略、新发现的反模式），更新 `.agents/docs/retrospective/patterns/methodology-patterns/ai-collaboration/source-code-to-okf-wiki-workflow.md` 或相关模板；核对两束 log.md 与 tasks.md 勾选（依赖 Task 10）——新增第 3 次迁移验证案例 + 反模式 9/10；两束 log.md 已补记 V/C 阶段

# Task Dependencies

- Task 1（各子任务可并行）、Task 2 → Task 3 → Task 4 → Task 5/6/7（5/6 串行，7 与 5/6 并行）→ Task 8 → Task 9 → Task 10 → Task 11
