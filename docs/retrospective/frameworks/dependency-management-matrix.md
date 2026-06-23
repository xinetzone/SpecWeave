> **来源**：从 `docs/retrospective/knowledge-extraction.md` 五、可复用决策框架 拆分

# 临时依赖管理决策矩阵

## 来源
`dependency-management.md`

## 决策矩阵

| 文件类型 | 存放位置 | Git 跟踪 | 清理策略 |
|---------|---------|---------|---------|
| 第三方库源码 | `vendor/` | 忽略 | 定期检查，移除无用 |
| 任务中间产物 | `.temp/` | 忽略 | 任务完成后清理 |
| 虚拟环境 | `.venv/` | 忽略 | 项目归档时删除 |
| 编译缓存 | `__pycache__/` | 忽略 | 自动生成，无需手动管理 |
| 包管理器依赖 | `node_modules/` | 忽略 | 通过 lock 文件恢复 |
| 环境变量 | `.env` | 忽略 | 提供 `.env.example` 模板 |

## 保障措施
`.gitignore` + `pre-commit hook` + `CI 校验` 三层防护。

> **关联模块**：
> - `frameworks/directory-naming-matrix.md`
> - `patterns/code-patterns/gitignore-validation.md`