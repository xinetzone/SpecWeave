---
spec_version: "0.2"
spec: jupyterlab-okf-wiki-completion
created: 2026-08-23
---

# JupyterLab OKF Wiki 补全任务清单

## Task 1: 源码深度阅读与 API 验证（R 阶段补充）

**目标**：阅读关键 TypeScript 源码文件，验证 concepts 中将要引用的 API 名称

- [ ] 1.1 阅读 `packages/application/src/lab.ts`，确认 JupyterLab 类、JupyterFrontEnd 基类、start() 方法
- [ ] 1.2 阅读 `packages/application/src/shell.ts`，确认 ILabShell 接口、LabShell 类、区域常量
- [ ] 1.3 阅读 `packages/application/src/tokens.ts`，确认 ILayoutRestorer、IRouter、JupyterFrontEnd.IPaths 等 Token
- [ ] 1.4 阅读 `packages/application/src/frontend.ts`，确认 JupyterFrontEnd 插件激活机制
- [ ] 1.5 阅读 `packages/services/src/index.ts`，确认 ServiceManager 及其子管理器
- [ ] 1.6 阅读 `packages/docregistry/src/`，确认 DocumentRegistry、Context、WidgetFactory、ModelFactory
- [ ] 1.7 阅读 `packages/notebook/src/panel.ts` 和 `widget.ts`，确认 NotebookPanel、NotebookActions
- [ ] 1.8 阅读 `packages/cells/src/widget.ts`，确认 Cell/CodeCell/MarkdownCell/RawCell
- [ ] 1.9 阅读 `examples/` 目录，确认扩展示例的真实代码模式
- [ ] 1.10 阅读 `packages/application-extension/src/index.ts`，确认核心插件注册模式

## Task 2: 生成 references/source-code-map.md

**目标**：先于 concepts 生成信源文件，供后续文档引用

- [ ] 2.1 编写源码文件地图，覆盖 Python 后端和前端 packages
- [ ] 2.2 整理 103 个 packages 的分类速查表（核心/功能/MIME/扩展/构建）
- [ ] 2.3 添加完整 frontmatter

## Task 3: 生成 concepts 01-03（架构基础层）

**目标**：生成架构概览、应用框架、插件系统三章

- [ ] 3.1 生成 01-architecture-overview.md（Monorepo、技术栈、五层架构、Mermaid图、依赖链）
- [ ] 3.2 生成 02-application-shell.md（JupyterLab类、ILabShell、8区域、启动流程、Widget生命周期）
- [ ] 3.3 生成 03-plugin-system.md（Token、JupyterFrontEndPlugin、DI、激活顺序、通信模式）

## Task 4: 生成 concepts 04-06（核心机制层）

**目标**：生成服务层、文档系统、Notebook架构三章

- [ ] 4.1 生成 04-service-layer.md（ServiceManager、14个子管理器、REST/WS、Kernel Protocol）
- [ ] 4.2 生成 05-document-widget-system.md（DocumentRegistry、Factory模式、Context、文件类型链）
- [ ] 4.3 生成 06-notebook-cells.md（NotebookPanel/Notebook/Cell三层、Cell类型、执行流程、窗口化）

## Task 5: 生成 concepts 07-09（扩展与生态层）

**目标**：生成扩展生态、构建系统、关键子系统三章

- [ ] 5.1 生成 07-extension-ecosystem.md（Federated扩展、ExtensionManager、CLI、entry point）
- [ ] 5.2 生成 08-build-and-modes.md（Core/Dev/App三模式、Rspack、jlpm、singletonPackages）
- [ ] 5.3 生成 09-key-subsystems.md（PageConfig、CommandRegistry、StateDB、SettingRegistry、Router）

## Task 6: 生成 examples 01-02

**目标**：生成两个实战示例

- [ ] 6.1 生成 01-minimal-extension.md（插件骨架、命令注册、菜单/命令面板、安装运行）
- [ ] 6.2 生成 02-custom-file-type.md（文件类型注册、WidgetFactory、DocumentRegistry集成、工具栏）

## Task 7: 更新导航索引

- [ ] 7.1 更新 concepts/index.md，包含01-09导航
- [ ] 7.2 更新 examples/index.md，包含01-02导航
- [ ] 7.3 更新 references/index.md，包含source-code-map导航
- [ ] 7.4 更新 bundle index.md，补充frontmatter和统计

## Task 8: V阶段验证

- [ ] 8.1 Grep级API真实性验证（关键类名/函数名/接口名）
- [ ] 8.2 内部链接有效性检查
- [ ] 8.3 frontmatter完整性检查
- [ ] 8.4 代码示例语法合理性检查

## Task 9: Review独立审查与修复

- [ ] 9.1 独立审查文档质量
- [ ] 9.2 修复发现的问题
- [ ] 9.3 更新 log.md
