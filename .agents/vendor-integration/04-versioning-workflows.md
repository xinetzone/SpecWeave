---
id: "vendor-versioning-workflows"
title: "04 版本控制与子模块流程"
source: "VENDOR-INTEGRATION.md#versioning-workflows"
x-toml-ref: "../../.meta/toml/.agents/vendor-integration/04-versioning-workflows.toml"
---
# 04 版本控制与子模块流程

## 第5章 版本控制策略

**跟踪策略**：默认**跟踪 flexloop 仓库的 main 分支**，通过 `git submodule update --remote` 按需拉取最新版本。不自动更新，所有更新必须经过人工审核和验证。

**版本标识格式**：使用分支名 + commit 短哈希的组合格式，便于人类阅读和精确追溯：
- 格式：`main@d618849a`
- 含义：main 分支，commit 哈希前缀 d618849a
- 可选附加 tag 信息：`main@d618849a (v0.7.1-270-gd618849)`

**当前锁定版本**：
- 分支：`main`
- 完整 commit：`d618849a0742772dd9d4ffb472c3e1f7e7f3ab4e`
- 版本标识：`main@d618849a`
- 记录位置：[vendor/VERSION.md](../../vendor/VERSION.md)

**更新频率**：按需更新，不做定期自动更新。触发更新的场景：
- flexloop PR 合并后需要同步到 SpecWeave
- 发现 flexloop 有需要的新特性
- 发现 flexloop 有重要的 Bug 修复
- 需要参考 flexloop 的最新实现模式

**兼容性评估**：更新前必须查看 flexloop 的 `CHANGELOG.md`，检查：
- 是否有破坏性变更（Breaking Changes）
- 目录结构是否发生变化（影响文档引用路径）
- 脚本接口是否变更（影响萃取脚本和条件导入的兼容性）

**回滚机制**：
- 快速回滚：`git submodule update vendor/flexloop` 恢复到 VERSION.md 中记录的 commit
- 指定版本回滚：`cd vendor/flexloop && git checkout <prev-commit>`
- 回滚后必须重新验证关键引用、萃取脚本和条件导入的正确性

## 第6章 子模块更新与开发流程

子模块更新必须严格遵循以下 4 步法，确保过程可控、可追溯、可回滚。

### 6.1 子模块更新流程（同步上游）

#### 步骤1：更新前检查

确认工作树清洁，记录当前版本：

```bash
git status
git submodule status vendor/flexloop
```

如有未提交的变更，先处理完毕再开始更新。

#### 步骤2：执行更新

方式一：进入子模块目录，拉取 main 分支最新代码：

```bash
cd vendor/flexloop
git fetch
git checkout main
git pull origin main
cd ../..
```

方式二（推荐）：使用 submodule 命令直接更新到远程跟踪分支：

```bash
git submodule update --remote vendor/flexloop
```

`--remote` 会拉取上游 main 分支的最新 commit，必须经过兼容性评估和验证后才能提交。

#### 步骤3：更新后验证

完成版本切换后，执行以下验证：

1. 更新 [vendor/VERSION.md](../../vendor/VERSION.md) 中的分支名和 commit 哈希
2. 检查文档引用：验证所有指向 vendor/flexloop/ 的相对路径是否仍然有效
3. 检查萃取脚本：确认从 flexloop 萃取的脚本与新版本兼容
4. 检查条件导入：验证通过 conditional_import 导入的模块接口未发生变化
5. 人工抽查：对照 flexloop CHANGELOG，抽查关键功能和目录结构

#### 步骤4：提交更新

将子模块指针变更和版本元数据一并提交：

```bash
git add vendor/flexloop vendor/VERSION.md
git commit -m "chore(vendor): update flexloop to main@<commit-hash>"
```

提交信息应清晰说明更新到的 commit 哈希和更新原因。

### 6.2 子模块开发流程（向 flexloop 贡献代码）

在 vendor/flexloop/ 内开发新功能或修复 Bug，必须遵循以下流程：

1. **进入子模块目录**：
   ```bash
   cd vendor/flexloop
   ```

2. **创建功能分支**：
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **编辑代码**：在子模块内进行开发，遵循 flexloop 的代码规范。

4. **在 flexloop 环境中测试**：
   ```bash
   cd apps/chaos
   uv sync
   uv run pytest
   cd ../..
   ```

5. **Commit 并 push 到 flexloop 远程仓库**：
   ```bash
   git add .
   git commit -m "feat: describe your changes"
   git push -u origin feature/your-feature-name
   ```

6. **在 gitcode.com 创建 PR**：访问 `gitcode.com:flexloop/flexloop` 创建 Pull Request，等待代码审查和合并。

7. **PR 合并后同步到 SpecWeave**：回到 SpecWeave 根目录，更新子模块指针：
   ```bash
   cd /path/to/SpecWeave
   git submodule update --remote vendor/flexloop
   ```

8. **更新版本记录**：更新 [vendor/VERSION.md](../../vendor/VERSION.md) 中的版本记录。

9. **提交 gitlink 更新**：
   ```bash
   git add vendor/flexloop vendor/VERSION.md
   git commit -m "chore(vendor): update flexloop after PR merge"
   ```

**重要**：禁止在 vendor/flexloop/ 内有未 commit 的修改时就提交到 SpecWeave 主仓库。所有子模块内的修改必须先 push 到 flexloop 仓库并合并到 main 分支后，才能更新 SpecWeave 的 gitlink 指针。
---

## 相关模式

- [双模式子模块治理](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/dual-mode-submodule-governance.md)
- [Vendor生命周期治理](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/vendor-lifecycle-governance.md)
- [子模块元数据外部化](../../docs/retrospective/patterns/architecture-patterns/submodule-metadata-externalization.md)
---

← 上一章: [03 交互接口规范](03-interfaces.md) | **[返回索引](../VENDOR-INTEGRATION.md)** | 下一章: [05 测试隔离与模式萃取](05-testing-extraction.md) →
