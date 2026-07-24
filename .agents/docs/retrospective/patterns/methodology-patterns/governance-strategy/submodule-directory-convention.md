---
id: "submodule-directory-convention"
source: "retrospective-xuanspace-mono-repo-20260724/insight-extraction.md#洞察2"
---

# 子模块目录约定模式（Submodule Directory Convention）

## 模式类型

方法论模式（项目治理/目录规范）

## 成熟度

L1 首次提炼（xuanspace 子模块从 external/ → projects/ 迁移验证）

## 适用场景

monorepo 或主仓库需要纳入外部 Git 仓库作为子模块，且存在 `.gitignore` 排除规则的场景。

## 问题背景

在 monorepo 中，`.gitignore` 通常包含 `external/` 或 `vendor/` 等目录的排除规则，目的是避免将第三方源码重复提交到主仓库。但当需要将一个 Git 子模块放置在这些目录下时，会出现**目录语义与 Git 跟踪规则的隐性冲突**：

- 目录命名（`external/`）表达的是人类意图："这里是外部依赖"
- `.gitignore` 表达的是 Git 行为："不要跟踪这个目录的内容"
- 子模块的 gitlink 文件需要被 Git 跟踪，但被 `.gitignore` 排除了

xuanspace 项目最初将子模块放在 `external/xuanspace/`，因 `external/` 被 `.gitignore` 忽略，导致子模块无法被 Git 跟踪，浪费了一次迁移成本。

## 解决方案

### 核心原则

1. **目录语义 ≠ Git 语义**：目录命名和 `.gitignore` 规则必须一致
2. **子模块目录白名单**：被忽略的目录如需放置子模块，需显式 `!` 白名单
3. **放置前检查**：在 `git submodule add` 之前，先验证目标路径不被 `.gitignore` 排除

### 实施步骤

1. **选择子模块目录**：
   - 推荐 `projects/`（自建项目子模块）
   - 或 `vendor/`（需在 `.gitignore` 中白名单：`!/vendor/*/.git`）
   - 避免使用已被 `.gitignore` 完全排除的目录

2. **放置前检查清单**：
   ```bash
   # 检查目标路径是否被 gitignore 排除
   git check-ignore -v projects/xuanspace/

   # 如果被排除，添加白名单
   echo "!projects/" >> .gitignore
   ```

3. **`.gitignore` 白名单规则**：
   ```gitignore
   # 排除 vendor 目录内容
   vendor/*
   # 但保留子模块的 gitlink
   !vendor/*/
   !vendor/*/.git
   ```

4. **子模块注册验证**：
   - `.gitmodules` 文件正确记录子模块路径和 URL
   - `git submodule status` 显示正确的 commit 指针
   - 主仓库的 `git status` 显示子模块为正常状态

## 反模式

- **习惯性放置**：不检查 `.gitignore` 就直接 `git submodule add`
- **事后补救**：子模块已添加但未被跟踪，通过修改 `.gitignore` 再重新添加
- **混用语义**：同一目录既放被忽略的第三方源码，又放需要跟踪的子模块

## 关联模式

- [环境多样性设计](../../architecture-patterns/environment-diversity-design.md) — 本模式是"环境多样性"在 Git 规则维度的具体应用