---
version: 1.0
---

# WSL 完整 Wiki 教程 - PRD

## Overview
- **Summary**: 基于已有的 WSL 学习计划和 CLI/架构参考手册，在 `.agents/docs/knowledge/learning/08-systems-infrastructure/` 下创建原子化多章节的 WSL wiki 教程目录 `wsl-wiki/`。
- **Purpose**: 当前知识库中 WSL 相关内容仅有两份单文件文档，缺少面向开发者的系统性、原子化、可循序学习的教程。通过知识沉淀链路，将现有知识重组为结构化教程，参考 tvm-ffi-wiki 的 16 章原子化编号结构。
- **Target Users**: 需要学习 WSL 的开发者、在 Windows 上使用 Linux 开发环境的工程师、集成 WSL Container API（WSLC）的应用开发者、需要理解 WSL 底层架构的系统工程师。

## Goals
- 在 `08-systems-infrastructure/` 下创建 `wsl-wiki/` 原子化教程目录（README.md + 12-15 个编号章节）
- 教程覆盖：WSL 概述与安装、核心架构、CLI 命令详解、Linux 侧核心进程、文件系统互操作、Container API（C/C#/C++ 三语言投影）、网络互操作、配置管理、systemd 集成、调试诊断、开发环境搭建、最佳实践、FAQ/术语表/资源
- 整合现有 wsl-learning-plan.md 和 wsl-cli-and-architecture-wiki.md 的内容
- 每个章节包含标准 YAML frontmatter（id/title/source/date/category/tags）
- 遵循项目文档规范：相对路径引用、双向导航（上一章/下一章/返回目录）、源码锚点溯源
- 包含至少 3 张 Mermaid 架构图（整体架构、hvsocket 通道拓扑、Container API 对象模型）
- 包含 C/C#/C++ 三语言 WSLC API 完整可运行代码示例

## Non-Goals
- 不修改或删除现有的两份 WSL 单文件文档（wsl-learning-plan.md、wsl-cli-and-architecture-wiki.md）
- 不构建 WSL 源码或执行编译操作
- 不深入 WSL1 实现细节（仅在对比时简要提及）
- 不涉及第三方非官方 WSL 工具（如 WSL2 Manager、LxRunOffline 等）
- 不创建 TOML 元数据文件（使用 YAML frontmatter）
- 不包含 WSLg（GUI 应用支持）的深度实现细节（仅在概述中提及）

## Background & Context
- 项目已有成熟的原子化 wiki 教程体系（tvm-ffi-wiki 16 章、idl-wiki、interface-api-abi-protocol-wiki 等），形成了标准化的章节编号、双向导航、frontmatter 规范
- 已存在两份 WSL 单文件文档：
  - wsl-learning-plan.md：基于源码+官方文档的系统学习计划，含架构、进程、文件系统、API、实操练习
  - wsl-cli-and-architecture-wiki.md：深度核实的 CLI 命令树、四层架构模型、官方 Mermaid 架构图、interop/systemd 细节
- WSL 是 Microsoft 官方开源项目（github.com/microsoft/WSL），官方开发者文档在 wsl.dev，用户文档在 learn.microsoft.com/windows/wsl
- WSL Container API（WSLC）目前处于 preview 阶段，正式 GA 计划 2026 年秋季，提供 C/C#/C++（WinRT）三语言投影，遵循 Session→Container→Process 三层模型
- WSL2 核心通信机制：Windows 侧 COM（wsl.exe↔wslservice.exe）+ Windows↔Linux 侧 hvsocket（5 条独立通道，含 wsl.exe→relay 直接 IO 中继）

## Functional Requirements
- **FR-1**: 系统 SHALL 在 `.agents/docs/knowledge/learning/08-systems-infrastructure/wsl-wiki/` 下创建原子化教程目录，包含 README.md 导航入口 + 12-15 个编号章节文件（00-overview.md 到 14/15-resources.md）
- **FR-2**: 系统 SHALL 确保教程内容覆盖 WSL 全部核心知识领域：概述安装、整体架构、CLI 完整参考、Linux 侧核心进程、文件系统互操作、Container API（三语言投影）、网络、配置管理、systemd、调试诊断、开发环境、最佳实践、FAQ、术语表、资源
- **FR-3**: 系统 SHALL 整合现有 wsl-learning-plan.md 和 wsl-cli-and-architecture-wiki.md 的所有核心内容，避免知识丢失
- **FR-4**: 系统 SHALL 为每个 md 文件添加标准 YAML frontmatter，包含字段：id、title、source（固定为 "spec:create-wsl-wiki-tutorial"）、date、category、tags
- **FR-5**: 系统 SHALL 在所有章节之间使用相对路径进行交叉引用，每章末尾包含双向导航链接（上一章/下一章/返回目录）
- **FR-6**: 系统 SHALL 标注关键技术细节的信息来源（源码文件锚点或官方文档 URL），遵循四源验证法（源码/本地 doc/在线 wsl.dev/learn.microsoft.com）
- **FR-7**: 系统 SHALL 包含至少 3 张 Mermaid 架构图：整体组件架构图、hvsocket 通道拓扑图、WSLC Container API 对象模型图
- **FR-8**: 系统 SHALL 包含 C/C#/C++ 三语言的 WSLC API 代码示例，展示完整的 Session→Container→Process 生命周期

## Non-Functional Requirements
- **NFR-1**: 单章节文件不超过 500 行代码，遵循单一职责原则，每章聚焦一个核心主题
- **NFR-2**: 全文使用中文编写，技术术语保留英文原文并在首次出现时给出中文解释（如 hvsocket「虚拟机套接字」、Plan9「9号协议文件服务」）
- **NFR-3**: 不使用任何 file:/// 绝对路径引用，所有代码块标注语言类型（```c、```csharp、```cpp、```bash、```powershell、```mermaid 等）
- **NFR-4**: 代码示例完整可运行，注明前提条件（如 NuGet 包安装、SDK 链接、WSL 版本要求），错误码引用 WSLC_E_* 标准定义

## Constraints
- **Technical**: 纯 Markdown 产出，Mermaid 语法符合规范，严格遵循现有 tvm-ffi-wiki 格式参考
- **Business**: 内容基于现有两份文档 + 公开官方文档（wsl.dev、learn.microsoft.com），无外部付费资源依赖
- **Dependencies**: 依赖已有两份 WSL 文档作为主要内容基础，依赖 tvm-ffi-wiki 作为格式参考模板
- **Path**: 最终产出物路径固定为 `.agents/docs/knowledge/learning/08-systems-infrastructure/wsl-wiki/`

## Assumptions
- external/WSL 源码目录在当前环境不可用，主要基于已有两份文档 + 公开官方文档（wsl.dev、learn.microsoft.com）编写
- 读者具备基本的 Linux 和 Windows 使用经验，了解容器概念，教程定位为系统性进阶学习教程而非零基础入门
- WSL Container API 处于 preview 阶段，内容标注 preview 状态并提示 GA 时间计划

## Acceptance Criteria

### AC-1: 目录结构完整
- **Given**: 教程创建完成
- **When**: 检查 `wsl-wiki/` 目录结构
- **Then**: 包含 README.md 导航入口 + 12 个以上编号章节文件（00-*.md 格式）
- **Then**: 每个 md 文件包含合法的 YAML frontmatter，字段完整（id/title/source/date/category/tags）
- **Verification**: programmatic

### AC-2: 内容覆盖核心领域
- **Given**: 所有章节已创建完成
- **When**: 通读完整教程
- **Then**: 内容覆盖 WSL2 核心架构、CLI 完整命令树（含主名/别名）、Linux 侧五大进程（mini_init/init/plan9/gns/relay）、文件系统互操作（DrvFs/Plan9/双命名空间）、WSLC Container API、网络模式（NAT/Mirrored/DNS隧道）、配置文件（.wslconfig/wsl.conf）、systemd 启动流程、调试诊断方法、开发环境搭建、最佳实践、FAQ、术语表
- **Verification**: human-judgment

### AC-3: 知识体系关联与整合
- **Given**: 教程涉及交叉概念且引用现有文档
- **When**: 检查交叉引用和文档关联
- **Then**: README.md 关联到现有两份 WSL 文档（wsl-learning-plan.md、wsl-cli-and-architecture-wiki.md）作为扩展阅读
- **Then**: 现有两份文档的核心内容（架构、CLI、进程、文件系统、API、实操、错误码）均已整合到对应章节
- **Then**: 术语表定义统一，标签体系与现有知识库一致
- **Verification**: human-judgment

### AC-4: 格式规范合规
- **Given**: 所有章节编写完成
- **When**: 检查文档格式与链接
- **Then**: 无 file:/// 绝对路径引用
- **Then**: 所有内部链接使用相对路径
- **Then**: 每章末尾包含标准导航链接（← 上一章 | ↑ 返回目录 | 下一章 →）
- **Then**: Mermaid 图表语法正确可渲染，代码块均标注语言类型
- **Then**: 更新 08-systems-infrastructure/README.md 添加新 wiki 索引条目
- **Verification**: programmatic + human-judgment

### AC-5: 图表与代码质量
- **Given**: 教程包含 Mermaid 图表和代码示例
- **When**: 审查图表与代码
- **Then**: 包含至少 3 张 Mermaid 架构图（整体架构图、hvsocket 通道拓扑图、WSLC API 对象模型图）
- **Then**: 包含 C、C#、C++（WinRT）三语言的 WSLC API 完整可运行代码示例
- **Then**: 代码示例标注前提条件（链接库、NuGet 包、头文件）
- **Verification**: human-judgment

## Open Questions
- [ ] external/WSL 源码目录在编写时是否可用？（当前假设不可用，基于已有文档+公开资料）
- [ ] 是否需要包含 WSLg（GUI 应用支持）章节？（当前 Non-Goals 排除深度内容，仅概述提及）
- [ ] WSLC API GA 后是否需要更新 preview 标注？（教程中注明当前 preview 状态即可）
