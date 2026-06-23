---
title: "ADR: libs/ 目录重命名为 vendor/"
category: "decisions"
tags: ["architecture", "naming", "directory", "vendor", "convention"]
date: "2026-06-23"
status: reviewed
author: ""
summary: "记录将第三方依赖目录从 libs/ 重命名为 vendor/ 的架构决策及其理由"
---

# ADR: libs/ 目录重命名为 vendor/

## 背景

项目中 `libs/` 目录用于存放第三方库依赖。该目录名称过于宽泛，`libs` 在软件工程中可指代任意类型的库文件（包括项目内部自研库），无法准确表达"这是第三方依赖"的语义。随着项目规模增长和依赖数量增多，需要选择一个更清晰、更符合行业惯例的目录名称。

## 问题/场景

需要为存放第三方依赖的目录选择一个更准确的名称，要求满足以下条件：

1. **语义明确**：名称能直观表达"第三方依赖"的含义
2. **行业惯例**：主流技术生态中有广泛使用的先例
3. **工具兼容**：与现有工具链（如静态分析、CI/CD）的默认配置兼容

备选方案包括：`vendor/`、`third_party/`、`deps/`、`external/`。

## 决策

**采用 `vendor/` 作为第三方依赖目录的新名称。**

### 决策理由

| 维度 | vendor/ | third_party/ | deps/ | external/ |
|------|---------|-------------|-------|-----------|
| 语义明确度 | 高 | 高 | 中 | 中 |
| 行业惯例 | 广泛 | 较少 | 一般 | 较少 |
| 工具兼容性 | 优秀 | 一般 | 一般 | 一般 |
| 名称长度 | 短 | 长 | 短 | 一般 |

`vendor/` 的主要优势：

1. **PHP Composer 标准**：Composer 将依赖安装到 `vendor/` 目录，这是 PHP 生态的核心约定，数百万 PHP 项目遵循此规范
2. **Go modules 支持**：Go 1.11+ 的 `go mod vendor` 命令将依赖拷贝到 `vendor/` 目录，Go 工具链对此目录有原生支持
3. **Node.js 生态认可**：虽然 npm 默认使用 `node_modules/`，但在 monorepo 场景中，`vendor/` 常用于存放非 npm 的第三方脚本和库
4. **简洁性**：相比 `third_party/`（12 个字符），`vendor/`（7 个字符）更短，命令行操作更便捷
5. **语义准确**：`vendor` 在软件工程中特指"外部供应商提供的组件"，与"第三方依赖"的含义高度吻合

### 影响范围

- 所有引用 `libs/` 路径的配置文件、脚本、文档均需同步更新
- CI/CD 流水线中的路径引用需要调整
- 开发者本地环境需要重新同步依赖

## 参考

- [PHP Composer - vendor 目录规范](https://getcomposer.org/doc/04-schema.md#vendor-dir)
- [Go Modules - vendoring](https://go.dev/ref/mod#vendoring)