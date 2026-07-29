# WSL Wiki 教程 - 验证清单

## 一、目录结构完整性

- [ ] `wsl-wiki/` 目录已创建在 `.agents/docs/knowledge/learning/08-systems-infrastructure/` 下
- [ ] 目录包含 README.md 导航入口文件
- [ ] 包含 12 个以上编号章节文件（00-overview.md 到 14/15-*.md）
- [ ] 所有章节文件使用两位数字编号前缀（00-、01-、02-...）

## 二、YAML Frontmatter 规范

- [ ] 每个 md 文件包含 YAML frontmatter（--- 包裹）
- [ ] frontmatter 包含 `id` 字段（与文件名对应，如 wsl-wiki-00-overview）
- [ ] frontmatter 包含 `title` 字段（章节中文标题）
- [ ] frontmatter 包含 `source` 字段（固定值："spec:create-wsl-wiki-tutorial"）
- [ ] frontmatter 包含 `date` 字段（创建/更新日期，格式 YYYY-MM-DD）
- [ ] frontmatter 包含 `category` 字段（值为 "learning"）
- [ ] frontmatter 包含 `tags` 字段（数组，包含 wsl、相关技术标签）

## 三、路径与链接规范

- [ ] 无 file:/// 绝对路径引用
- [ ] 所有内部文档链接使用相对路径（如 ../wsl-learning-plan.md）
- [ ] 每章末尾包含标准双向导航链接：
  - [ ] ← 上一章（相对路径链接）
  - [ ] ↑ 返回目录（链接到 README.md）
  - [ ] 下一章 →（相对路径链接）
- [ ] README.md 中的章节链接正确指向对应章节文件
- [ ] 对现有两份 WSL 文档的链接正确（wsl-learning-plan.md、wsl-cli-and-architecture-wiki.md）
- [ ] 外部 URL 链接格式正确（使用 https://）

## 四、Mermaid 图表要求

- [ ] 包含至少 3 张 Mermaid 架构图
- [ ] 图1：WSL2 整体组件架构图（Windows 侧 + Linux 侧 + 通信通道）
- [ ] 图2：hvsocket 5通道拓扑图（标注每条通道的端点与用途）
- [ ] 图3：WSLC Container API 对象模型图（Session→Container→Process 三层）
- [ ] 可选图：CLI 命令执行流程图
- [ ] 所有 Mermaid 图表语法正确可渲染（使用 ```mermaid 代码块）

## 五、代码示例要求

- [ ] 包含 C 语言 WSLC API 完整端到端示例（7步生命周期）
- [ ] 包含 C# 语言 WSLC API 示例（异步、事件订阅）
- [ ] 包含 C++/WinRT 语言 WSLC API 投影示例
- [ ] C 示例标注链接库要求（wslcsdk.lib、ole32.lib）
- [ ] C# 示例标注 NuGet 包要求（Microsoft.WSL.Containers）
- [ ] 所有代码块标注语言类型（```c、```csharp、```cpp、```bash、```powershell、```ini 等）
- [ ] PowerShell 命令标注 powershell 语言类型
- [ ] Bash/Linux 命令标注 bash 语言类型
- [ ] 配置文件示例标注 ini 或 toml 语言类型
- [ ] 代码示例注明前提条件和预期输出

## 六、内容覆盖验证

### 6.1 基础章节
- [ ] 00-overview.md：WSL 概述、WSL1 vs WSL2 对比、核心特性、WSLC preview 标注
- [ ] 01-installation.md：系统要求、安装步骤、发行版管理、升级
- [ ] 02-quickstart.md：快速上手、基本命令、第一个程序、互操作初体验

### 6.2 核心架构
- [ ] 03-cli-reference.md：wsl.exe 完整命令树、wslc.exe 容器 CLI、主名/别名说明、CLI四层架构
- [ ] 04-architecture.md：Windows侧组件、Linux侧五大进程（mini_init/init/plan9/gns/relay）、COM+hvsocket通信机制
- [ ] 05-filesystem-interop.md：Windows→Linux访问（\\wsl.localhost + plan9）、Linux→Windows访问（DrvFs）、双mount命名空间

### 6.3 Container API
- [ ] 06-wslc-api.md：Preview状态说明、三层模型、三语言投影对照、C/C#/C++代码示例、WSLC_E_*错误码表

### 6.4 高级功能
- [ ] 07-networking.md：NAT vs Mirrored模式、DNS隧道、GNS、端口转发、网络诊断
- [ ] 08-configuration.md：.wslconfig全局配置、/etc/wsl.conf分发版配置、组策略
- [ ] 09-systemd.md：启用方法、fork启动流程、用户会话同步、配置保护、问题排查

### 6.5 实用指南
- [ ] 10-debugging-diagnostics.md：日志收集、ETL追踪、WinDbg/gdb调试、崩溃转储、诊断脚本
- [ ] 11-development-env.md：VS Code Remote、跨编译环境、Git配置、Docker/GPU、性能优化
- [ ] 12-best-practices.md：文件系统性能、内存管理、网络配置、安全实践、开发工作流
- [ ] 13-faq-troubleshooting.md：安装/网络/文件/内存/systemd/容器/镜像/崩溃各类问题排查

### 6.6 附录
- [ ] 14-glossary.md：核心术语表（≥20个术语，中英文对照）
- [ ] 15-resources.md：官方资源、源码索引、学习路径、项目内交叉引用

## 七、知识整合验证

- [ ] wsl-learning-plan.md 的核心内容已整合到对应章节：
  - [ ] 整体架构（§2.1）→ 04-architecture.md
  - [ ] Linux核心进程（§2.2）→ 04-architecture.md
  - [ ] 文件系统互操作（§2.3）→ 05-filesystem-interop.md
  - [ ] WSLC API（§2.4）→ 06-wslc-api.md
  - [ ] 配置与组策略（§2.6）→ 08-configuration.md
  - [ ] 诊断调试（§2.7）→ 10-debugging-diagnostics.md
  - [ ] 5个实操练习 → 融入对应章节或作为示例
  - [ ] FAQ（§4.2）→ 13-faq-troubleshooting.md
  - [ ] 学习路径（§4.3）→ 15-resources.md
  - [ ] 关键源码索引（§5.1）→ 15-resources.md
  - [ ] 外部资源（§5.2）→ 15-resources.md
- [ ] wsl-cli-and-architecture-wiki.md 的核心内容已整合：
  - [ ] CLI命令名误判修正（§1.1）→ 03-cli-reference.md（主名/别名说明）
  - [ ] root级命令名称冲突（§1.2）→ 03-cli-reference.md
  - [ ] 完整CLI命令树（§2）→ 03-cli-reference.md
  - [ ] CLI架构四层模型（§3）→ 03-cli-reference.md
  - [ ] 命令执行流程图（§3.1）→ 03-cli-reference.md（Mermaid）
  - [ ] 官方架构Mermaid源图（§4）→ 04-architecture.md
  - [ ] wsl.exe→relay直接hvsocket通道（§4）→ 04-architecture.md
  - [ ] wslservice COM接口（§5.1）→ 04-architecture.md
  - [ ] interop binfmt机制（§5.2）→ 05-filesystem-interop.md
  - [ ] systemd fork启动（§5.3）→ 09-systemd.md
  - [ ] hvsocket完整5通道拓扑（§5.4）→ 04-architecture.md（Mermaid图）
  - [ ] C API完整清单（§6）→ 06-wslc-api.md

## 八、知识库导航更新

- [ ] `.agents/docs/knowledge/learning/08-systems-infrastructure/README.md` 已更新
- [ ] 索引中添加了 wsl-wiki/ 条目
- [ ] 条目包含简要说明和相对路径链接
- [ ] 现有其他条目未被破坏

## 九、文档质量标准

- [ ] 单文件不超过 500 行（遵循单一职责）
- [ ] 全文中文编写，技术术语首次出现时给出中文解释
- [ ] 关键技术细节标注信息来源（源码锚点或官方文档URL）
- [ ] WSLC 相关内容明确标注 preview 状态及 GA 计划
- [ ] 内容准确，已修正"ls是主名"等先前误判（list/remove是主名，ls/ps/rm/delete是别名）
- [ ] 包含 wsl.exe→relay 直接hvsocket通道（先前学习计划遗漏的关键通信路径）
- [ ] 无敏感信息、无内部链接泄漏

## 十、最终验收

- [ ] 所有复选框均已勾选
- [ ] 链接检查通过（无死链）
- [ ] Mermaid图表可正常渲染
- [ ] 代码示例语法正确
- [ ] 目录结构符合原子化wiki规范（与tvm-ffi-wiki格式一致）
- [ ] 满足所有 Acceptance Criteria（AC-1 到 AC-5）
