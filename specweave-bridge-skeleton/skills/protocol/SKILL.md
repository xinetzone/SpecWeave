---
name: specweave-protocol
description: SpecWeave 工作区启动协议、上下文路由与子区域路由参考。用于在 SpecWeave 工作区内按规范执行任务。
---

# SpecWeave 协议参考

本技能由 `specweave-bridge` 插件提供，为 Hermes 提供 SpecWeave 工作区规范的核心参考。

## 启动协议（PRIORITY ZERO）

在任何 SpecWeave 工作区内执行任务前，必须先：

1. 读取根目录 `AGENTS.md` 全文
2. 按「上下文路由表」确定需读取的规范文件（任务类型预检：是否命中 vendor 方法论资产）
3. 读取对应的规范文件（角色定义 / 复盘模板 / 知识库等）
4. 在规范指导下选择 Skill 工具并执行任务

自检清单（步骤 3.5）：任务是否命中 vendor 资产、内容敏感度预检、是否读取相关入口、
是否有相关 Skill、是否在 apps/projects/vendor 子区域内。

## 上下文路由（context-routing）

- 主权区（SpecWeave 根）：直接按 `.agents/` 规范执行
- `apps/` 子区域：先读 `apps/AGENTS.md`，再按「应用路由表」进入对应应用
- `projects/` 子区域：先读 `projects/AGENTS.md`，再按「子项目路由表」进入对应子项目
- `vendor/` 子区域：先读 `vendor/AGENTS.md`，再按「子模块路由表」进入对应子模块

## 内容敏感度预检

- **公开内容（Public）**：标准工作流，Spec 目录 `.trae/specs/`，产出 `docs/`
- **私域内容（Private）**：跳过 `.trae/specs/`，产出直接放 `playground/` 对应用户目录
- 判定依据：URL 特征、域名特征、用户标注、内容主题；不确定默认按私域处理

## 工具

- `specweave_route <task>`：查询任务对应的规范路径（支持子区域路由）
- `specweave_check <script>`：在 `.agents/scripts/` 下运行验证脚本
- `/specweave`：斜杠命令查看工作区状态与路由
