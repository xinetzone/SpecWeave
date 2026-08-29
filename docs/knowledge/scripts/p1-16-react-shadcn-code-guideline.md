---
id: p1-16-react-shadcn-code-guideline
title: React + TypeScript + shadcn/ui 项目代码规范
source: d:\spaces\chaos\daoApps\dao-yan\CodeGuideline.md
source_type: file
category: scripts
tags:
  - react
  - typescript
  - shadcn-ui
  - tailwind
  - code-convention
  - project-structure
archive_status: archived
archive_priority: P1
created_at: 2026-08-02T12:30:00Z
updated_at: 2026-08-02T12:50:00Z
version: v0.1.0
reviewer: chaos-coordinator
review_notes: approved - React+shadcn 项目结构规范清晰，可复用性高
summary: React 19 + TypeScript + Vite + Tailwind + shadcn/ui 技术栈的项目目录结构与编码规范指南
target_path: D:\spaces\SpecWeave\.agents\docs\knowledge\scripts\p1-16-react-shadcn-code-guideline.md
archived_at: 2026-08-02T04:55:39Z
source_version: v0.1.0
archive_version: v0.1.0
last_error: 
archive_history:
  - 2026-08-02T04:55:39Z archived from d:\spaces\chaos\.agents\knowledge\temp\scripts\p1-16-react-shadcn-code-guideline.md to D:\spaces\SpecWeave\.agents\docs\knowledge\scripts\p1-16-react-shadcn-code-guideline.md
---

# React + TypeScript + shadcn/ui 项目代码规范

## 项目结构标准

```
project-root/
  ├── public/                # 静态资源（favicon, robots.txt 等）
  ├── src/
  │   ├── components/        # 可复用 UI 组件
  │   │   └── ui/            # shadcn/ui 基础组件 + 自定义原子组件
  │   ├── hooks/             # 自定义 React Hooks
  │   ├── lib/               # 工具函数与库
  │   ├── pages/             # 路由级页面
  │   ├── App.tsx            # 根组件，配置全局 Provider
  │   ├── router.tsx         # 路由配置
  │   ├── main.tsx           # React 应用入口
  │   └── index.css          # 全局样式
  ├── package.json           # 项目元数据与脚本
  ├── tailwind.config.ts     # Tailwind CSS 配置
  └── ...                    # 其他配置与锁文件
```

## 目录职责

### public/
直接提供服务的静态文件，放置图片、图标、robots.txt 等。

### src/components/
所有 UI 组件。
- **ui/**：原子组件和复合组件，按功能分组
- 相关组件可创建子目录（如 `form/`、`charts/`）
- 仅在特定页面使用的组件，放在对应页面子目录下

### src/hooks/
自定义 React Hooks，每个文件导出单一职责的一个 Hook。

### src/lib/
非 React 组件/Hook 的工具函数和库。

### src/pages/
所有路由级页面。
- 如果页面包含多个文件或相关逻辑/组件，应为其创建子目录
- 子目录内放置页面特定组件

### src/App.tsx
设置全局 Provider（如 ThemeProvider、AuthProvider、I18nProvider 等）。

### src/router.tsx
设置路由，为每个路由生成语义化名称。

### src/main.tsx
应用入口点。

> **重要**：添加/删除模块（组件、Hook、工具）或页面时，**必须立即更新本文档**以反映当前结构。

## 新增代码指南

### 1. 添加新页面

- 在 `src/pages/` 下为每个新页面**创建子目录**
  - 示例："Dashboard" 页面 → `src/pages/dashboard/`
- 将主页面组件作为子目录内的 `index.tsx`
- 将页面特定组件/逻辑放在同一子目录
- 在 `src/router.tsx` 中注册新路由并生成语义化名称

```tsx
// router.tsx 示例
import Dashboard from "./pages/dashboard";
// ...
{
  path: "/dashboard",
  name: 'dashboard',
  element: <Dashboard />
}
```

### 2. 添加新组件

- 如果添加一组相关组件，创建子目录（如 `form/`、`charts/`）
- 如果组件仅在特定页面使用，放在 `src/pages/` 下对应页面子目录中
- 每个组件应专注于单一职责
- 鼓励小文件（单个组件 < 100 行）

### 3. 添加新 Hook

- 在 `src/hooks/` 创建以 Hook 命名的文件（如 `use-feature.ts`）
- 每个文件只导出一个 Hook
- Hook 应尽可能小且职责单一

### 4. 添加工具函数

- 添加到 `src/lib/`
- 相关工具可分组到同一文件或子目录

## 编码最佳实践

| 原则 | 说明 |
|------|------|
| **一个模块，一个职责** | 每个文件（组件、Hook、工具）只做一件事 |
| **高内聚，低耦合** | 相关逻辑放在一起，避免模块间不必要的依赖 |
| **命名约定** | 组件/页面目录用 `PascalCase`；Hook/工具函数用 `camelCase`；页面子目录/文件以路由或功能命名 |
| **组件结构** | 保持组件小而专注；过大时提取子组件 |
| **页面结构** | 页面特定的逻辑/Hook/组件放在其子目录；真正可复用的才放到 `components/`、`hooks/` 或 `lib/` |
| **文档** | 复杂逻辑添加注释；模块用途不明显时在文件顶部文档化 |

## 示例：添加"Profile"页面

1. **创建目录**：`src/pages/profile/`
2. **添加主页面组件**：`src/pages/profile/index.tsx`
3. **添加页面特定组件**：`ProfileHeader.tsx`、`ProfileDetails.tsx`
4. **注册路由**：
   ```tsx
   import Profile from "./pages/profile";
   // ...
   <Route path="/profile" element={<Profile />} />
   ```
5. **如需可复用按钮**，添加到 `src/components/ui/button.tsx`

---

**来源参考**：
- [CodeGuideline.md](file:///d:/spaces/chaos/daoApps/dao-yan/CodeGuideline.md)
- 相关项目：[DaoYan 项目](file:///d:/spaces/chaos/daoApps/dao-yan/)
