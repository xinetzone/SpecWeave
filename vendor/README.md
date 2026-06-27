+++
# 此文件由 check-vendor 自动生成，请根据实际情况完善
+++

# Vendor 依赖总览

本目录存放项目引入的第三方依赖库。
- **git 子模块**：通过 `.gitmodules` 管理，会提交 gitlink 至版本控制
- **手动管理依赖**：通过 `.gitignore` 忽略（vendor/* 排除白名单），不提交源码

## 依赖清单

| 库名称 | 版本 | 引入日期 | 用途 |
|---|---|---|---|
| flexloop | 子模块 | - | 外部依赖（git submodule） |

## 使用说明

1. 新增 git 子模块：`git submodule add <url> vendor/<name>`
2. 新增手动管理依赖：运行 `python .agents/scripts/repo-check.py vendor --fix` 创建标准模板
3. 手动管理依赖的每个子目录必须包含 `README.md` 元数据文件
4. 所有依赖版本需同步更新至 `VERSION.md`
5. 定期运行 `python .agents/scripts/repo-check.py vendor --scan-refs` 检查未使用依赖

## 管理规范

详见 [临时依赖管理流程](../.agents/protocols/dependency-management.md)
