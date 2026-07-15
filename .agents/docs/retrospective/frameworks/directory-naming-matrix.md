> **来源**：从 `docs/retrospective/knowledge-extraction.md` 五、可复用决策框架 拆分

# 目录命名决策矩阵

## 来源
`libs/` → `vendor/` 重命名决策

## 决策矩阵

| 目录用途 | 推荐命名 | 理由 |
|---------|---------|------|
| 第三方依赖 | `vendor/` | Go 社区惯例，跨语言通用 |
| 项目自身库 | `src/` 或 `pkg/` | 明确非第三方代码 |
| 构建产物 | `dist/` 或 `build/` | 行业标准 |
| 文档 | `docs/` | 通用惯例 |
| 配置 | `config/` 或 `.config/` | 按需选择是否隐藏 |
| 脚本 | `scripts/` | 通用惯例 |
| 临时文件 | `.temp/` | 隐藏目录，避免误提交 |

## 决策原则
优先使用行业惯例命名，降低认知负担。

> **关联模块**：
> - `frameworks/dependency-management-matrix.md`