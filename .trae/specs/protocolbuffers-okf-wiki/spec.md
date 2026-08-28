# Protocol Buffers 生态 OKF Wiki 教程 Spec

## Why

`external/libs/protocolbuffers/` 下已有完整克隆的 protobuf 生态源码（`protobuf` 主仓 v37.0 + `protobuf-ci` CI 动作仓），但目前 awesome-okf-xs 知识库（263 束）中没有任何 protobuf 相关知识包。团队成员在序列化选型、protoc 编译器扩展、多语言运行时行为排查时缺乏可溯源的中文源码级教程，AI 智能体也容易凭训练数据虚构 protobuf API。

## What Changes

- 新建分组 `doc/bundles/comm/serialization/`（序列化与数据交换生态），含 2 个 OKF v0.2 知识束：
  - `protobuf/`：完整束（concepts/ + examples/ + references/ + index.md + log.md），概念文档 ≥15 篇，覆盖 C++ 运行时核心、wire format、descriptor/reflection、protoc 编译器管线、代码生成插件、Editions 特性系统、Python/upb/Rust 等运行时、hpb、conformance 测试体系
  - `protobuf-ci/`：精简束（概念文档 4-5 篇），覆盖 GitHub Actions composite actions（bash/bazel/ccache/sccache/docker/checkout）的 CI 基础设施模式
- 更新 `doc/bundles/comm/index.md`（comm 域新增 serialization 分组）与 `doc/bundles/index.md` 总索引（束数 263→265、分组 30→31）
- 遵循 source-code-to-okf-wiki 五阶段工作流（R→I→E→V→C）：编号事实采集 → 架构洞察 → 信源先行分批生成 → Grep 级 API 独立验证 → 模式沉淀
- 更新 awesome-okf-xs 的 `doc/bundles/` 相关索引后必须通过 `invoke gates.toctrees` 与 `invoke gates.utf8` 质量门

## Impact

- Affected specs: awesome-okf-xs OKF v0.2 规范（`projects/awesome-okf-xs/.agents/rules/frontmatter.md`）
- Affected code:
  - 新增：`projects/awesome-okf-xs/doc/bundles/comm/serialization/protobuf/**`、`projects/awesome-okf-xs/doc/bundles/comm/serialization/protobuf-ci/**`、`projects/awesome-okf-xs/doc/bundles/comm/serialization/index.md`
  - 修改：`projects/awesome-okf-xs/doc/bundles/comm/index.md`、`projects/awesome-okf-xs/doc/bundles/index.md`
  - 只读信源：`external/libs/protocolbuffers/protobuf/**`（约 v37.0）、`external/libs/protocolbuffers/protobuf-ci/**`
- 工作产物（facts/insights）存放于 `.trae/specs/protocolbuffers-okf-wiki/`

## ADDED Requirements

### Requirement: protobuf 主仓知识束

系统 SHALL 以源码事实为基础（零推测），生成覆盖 protobuf v37.0 主仓核心子系统的中文概念文档。

#### Scenario: 覆盖全部核心子系统
- **WHEN** 审查 concepts/ 文档清单
- **THEN** 至少覆盖：仓库结构与构建系统（bazel/cmake 双轨）、wire format 编码、descriptor 与反射体系、Message 生命周期与 Arena 内存管理、protoc 编译器管线（parser→descriptor pool→code generator）、插件机制（plugin.proto/CodeGenerator）、Editions 特性系统、文本格式与 JSON、Python C 扩展运行时、upb 运行时、Rust 运行时、其他语言运行时概览（Java/C#/ObjC/PHP/Ruby）、hpb、conformance 测试体系、well-known types
- **NOTE** 主仓子目录（src、python、java、csharp、objectivec、php、ruby、rust、hpb、editions、conformance、benchmarks、examples、docs、cmake、bazel）均须在 references/ 信源登记并在 concepts/ 中至少被一篇文档覆盖

#### Scenario: 事实可溯源
- **WHEN** 检查任意概念文档中的 API 引用（类名/方法名/函数签名）
- **THEN** 均可在 `external/libs/protocolbuffers/protobuf/` 源码中 Grep 验证存在，零虚构 API

### Requirement: protobuf-ci 知识束

系统 SHALL 为 protobuf-ci 仓库生成精简知识束，覆盖其作为 protobuf 官方 CI 基础设施的角色。

#### Scenario: 精简覆盖
- **WHEN** 审查 protobuf-ci 束
- **THEN** 包含 4-5 篇概念文档（仓库定位、composite actions 结构、bazel 构建动作与缓存策略 ccache/sccache、docker 动作），全部基于源码事实

### Requirement: OKF v0.2 合规与质量门

#### Scenario: 结构合规
- **WHEN** 检查两个知识束
- **THEN** 束根 index.md 含 `okf_version: "0.2"` 与 `{toctree}`（引用全部内容文档）；子目录 index.md 无 frontmatter；所有内容文档含完整 frontmatter（type/title/description/tags/generated/verified/status/stale_after/sources）；sources 指向已存在的 references/ 文件；交叉链接使用 `/` 开头 bundle-relative 路径；总索引计数同步更新

#### Scenario: 构建质量门通过
- **WHEN** 在 projects/awesome-okf-xs 下运行 `invoke gates.toctrees` 与 `invoke gates.utf8`
- **THEN** 两项检查全部通过，无断链、无孤立文档、无编码问题

### Requirement: 五阶段方法论质量门

#### Scenario: R 阶段（G1）
- **WHEN** 检查 facts 文件
- **THEN** 事实编号 F-xxx、指向具体源码路径、无"用于/目的是/设计为"等推断词

#### Scenario: I 阶段（G2）
- **WHEN** 检查 insights 文件
- **THEN** 3-5 条核心洞察均含陈述/证据（引用 F-xxx）/反常识/行动四元组，附知识地图与学习路径

#### Scenario: E 阶段（G3）
- **WHEN** 检查生成顺序
- **THEN** references/ 先于 concepts/ 生成，concepts 分批（每批 ≤7），各级 index.md 最后生成

#### Scenario: V 阶段（G4）
- **WHEN** 独立验证执行完毕
- **THEN** Grep API 验证、链接检查、frontmatter 检查、index 完整性检查全部通过并输出验证报告

#### Scenario: C 阶段（G5）
- **WHEN** 工作流收尾
- **THEN** 模式/经验沉淀（含新发现的反模式）存入 `.agents/docs/retrospective/patterns/methodology-patterns/ai-collaboration/` 或更新 skill 模板；两束 log.md 记录生成信息

## Constraints

- protobuf 主仓为超大规模 monorepo：R 阶段采用「架构全覆盖 + 核心深读」策略——所有顶层子目录至少信源登记+架构级覆盖，C++ 核心（src/google/protobuf）、compiler/、python/、rust/upb 深读到类/方法签名级
- 源码目录只读，禁止任何修改
- 正文中文，文件名 kebab-case 纯英文；`stale_after` 设 2027-06-30（活跃迭代项目）
- 分批并行委派子代理时，每个子任务必须独立携带完整格式规范与相关事实清单
