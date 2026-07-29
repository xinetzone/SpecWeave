---
id: "establish-four-region-routing-system-checklist"
version: "1.0"
---
# 建立四大区域路由体系 - Verification Checklist

## 结构完整性检查
- [x] apps/.agents/ 目录已创建
- [x] apps/.agents/README.md 已创建且包含 frontmatter
- [x] apps/AGENTS.md 已创建
- [x] apps/AGENTS.md 包含 YAML frontmatter（id, version, source）

## apps/AGENTS.md 章节完整性
- [x] 包含「区域性质」章节，明确 apps 是主仓库内应用、可直接修改
- [x] 包含「应用路由表」，列出所有现有应用
- [x] 包含「嵌套优先级」说明
- [x] 包含 Mermaid 路由流程图
- [x] 包含「可用资产索引」章节
- [x] 包含「边界声明」表格
- [x] 包含「跨应用调用规范」章节
- [x] 包含「异常处理分支」章节
- [x] 包含「新增应用说明」章节

## 结构对称性验证
- [x] apps/AGENTS.md 章节结构与 projects/AGENTS.md 一致
- [x] apps/AGENTS.md 章节结构与 vendor/AGENTS.md 一致
- [x] apps/README.md 顶部包含 AGENTS.md 入口引用（与 projects/README.md 风格一致）
- [x] apps/.agents/README.md 模式与 projects/.agents/、vendor/.agents/ 一致

## 根 AGENTS.md 更新验证
- [x] 添加了「四大顶层区域」对比表
- [x] 对比表包含 .agents/、apps/、projects/、vendor/ 四个区域
- [x] 对比表包含目录、用途、维护方式、版本控制、是否可直接修改、AGENTS.md入口列
- [x] 启动协议步骤 2.1 已重构为通用区域路由判断
- [x] 步骤 2.1 按顺序判断 apps/ → projects/ → vendor/
- [x] 启动协议包含统一的三层路由说明
- [x] 步骤 3.5 自检清单已更新，包含 apps/projects 检查项
- [x] 核心规范入口表包含三个区域 AGENTS.md 链接

## 上下文路由表更新验证
- [x] .agents/context-routing.md 包含 apps/AGENTS.md 条目
- [x] .agents/context-routing.md 包含 app-development-workflow.md 引用（已有，无需重复添加）

## 链接与语法验证
- [x] 所有新增链接无断链（我们新创建的文件中）
- [x] 所有相对路径引用正确
- [x] Mermaid 图表语法正确无错误
- [x] 运行链接检查验证通过（我们创建/修改的文件无断链）

## 边界定义清晰度
- [x] 新人能在 30 秒内通过对比表理解四个区域的区别
- [x] apps 与 projects 的本质差异（主仓库内 vs git submodule）明确说明
- [x] 跨区域调用规范清晰
- [x] 异常处理分支（路由表未找到、链接指向不存在文件等）有处理方案

## 向后兼容性
- [x] 未修改 projects/ 或 vendor/ 内部内容
- [x] 未重构 .agents/ 内部现有体系
- [x] 未改变现有应用生命周期流程（.temp→apps）
- [x] 未修改任何业务代码

## 提交验证
- [x] 原子提交完成，提交信息符合 Conventional Commits 规范（commit db3848d5）
- [x] 8 个文件变更，630 行新增，19 行删除
