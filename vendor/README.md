+++
# 此文件由 check-vendor 自动生成，请根据实际情况完善
+++

# Vendor 依赖总览

本目录存放项目引入的外部依赖库。
- **git 子模块**：通过 `.gitmodules` 管理，会提交 gitlink 至版本控制
- **手动管理依赖**：通过 `.gitignore` 忽略（vendor/* 排除白名单），不提交源码

子模块分为两种类型：
- **third_party（第三方只读）**：外部项目，固定 commit，禁止本地修改
- **owned_collab（自有协作）**：团队拥有完全控制权的项目，允许子模块内开发，跟踪分支

## 依赖清单

| 库名称 | 版本 | 类型 | 引入日期 | 用途 |
|---|---|---|---|---|
| flexloop | main@d618849a (子模块) | owned_collab | 2026-06-27 | AgentForge AI Agent 协作框架（自有协作子模块，跟踪 main 分支） |

## 使用说明

1. 新增 git 子模块：`git submodule add <url> vendor/<name>`
2. 新增手动管理依赖：运行 `python .agents/scripts/repo-check.py vendor --fix` 创建标准模板
3. 手动管理依赖的每个子目录必须包含 `README.md` 元数据文件
4. 所有依赖版本需同步更新至 `VERSION.md`（标注类型和跟踪分支）
5. 定期运行 `python .agents/scripts/repo-check.py vendor --scan-refs` 检查未使用依赖
6. 自有协作子模块开发详见 [VENDOR-INTEGRATION.md](../docs/knowledge/VENDOR-INTEGRATION.md)

## 管理规范

详见 [临时依赖管理流程](../.agents/protocols/dependency-management.md) 和 [VENDOR-INTEGRATION.md](../docs/knowledge/VENDOR-INTEGRATION.md)
