---
id: "vendor-troubleshooting"
title: "06 常见问题与故障排查"
source: "VENDOR-INTEGRATION.md#troubleshooting"
x-toml-ref: "../../.meta/toml/.agents/vendor-integration/06-troubleshooting.toml"
---
# 06 常见问题与故障排查

## 第9章 常见问题与故障排查

### Q: `git status` 显示 `modified: vendor/flexloop (modified content)`？

A: 说明 submodule 工作树内有未提交的本地修改。

**如果是正在进行的开发工作**：遵循 6.2 子模块开发流程，在功能分支上继续开发，完成后 commit 并 push 到 flexloop 仓库，通过 PR 合并。

**如果是意外修改或运行脚本生成的临时文件**：
```bash
cd vendor/flexloop
git checkout .
git clean -fd
```

或者如果需要保留本地修改做参考，可以暂存：
```bash
cd vendor/flexloop
git stash
```

**重要**：提交到 SpecWeave 主仓库前必须确认 `git status vendor/flexloop` 不显示 modified content。子模块内的修改必须先 push 到 flexloop 仓库并合并到 main 分支后，才能通过 `git submodule update --remote` 更新 gitlink 指针。

### Q: 克隆后 vendor/flexloop 是空目录？

A: Git 克隆默认不会自动初始化和检出 submodule 内容。需要手动初始化：

```bash
git submodule update --init vendor/flexloop
```

首次克隆完整命令（自动初始化所有 submodule）：

```bash
git clone --recurse-submodules <repository-url>
```

### Q: 更新 submodule 后出现冲突？

A: submodule 本身作为一个 gitlink 指针，不会产生传统的文件合并冲突。可能的冲突场景：

- 如果 `vendor/VERSION.md` 有冲突：手动解决冲突，确认 commit 哈希与实际 submodule 指针一致
- 如果 submodule 处于 detached HEAD 状态：
  ```bash
  cd vendor/flexloop
  git checkout <expected-commit>
  ```

冲突解决后运行 `git submodule status` 确认指针正确。

### Q: 想直接运行 flexloop 的某个脚本？

A: **推荐使用沙箱工具运行**（见 4.6 节）：

```python
from lib.vendor_sandbox import run_flexloop_script
result = run_flexloop_script(".agents/scripts/check_gitignore.py", ["--fix"])
```

或者 cd 到 vendor/flexloop 对应目录，使用其自有环境运行：

```bash
cd vendor/flexloop/apps/chaos
uv run python .agents/scripts/check_gitignore.py
```

不要在 SpecWeave 根目录直接调用 vendor/ 内的脚本，避免路径和环境污染。

### Q: CI 中需要 submodule 吗？

A: 如果 CI 任务涉及条件导入或沙箱运行 flexloop 功能，需要初始化 submodule。需在 CI 脚本中添加：

```bash
git submodule update --init
```

条件导入模式下，FLEXLOOP_AVAILABLE 为 False 时功能会优雅降级，因此非关键路径的 CI 检查也可以不初始化 submodule。
---

## 相关模式

- [双模式子模块治理](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/dual-mode-submodule-governance.md)
- [Vendor生命周期治理](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/vendor-lifecycle-governance.md)
- [子模块元数据外部化](../../docs/retrospective/patterns/architecture-patterns/submodule-metadata-externalization.md)
---

← 上一章: [05 测试隔离与模式萃取](05-testing-extraction.md) | **[返回索引](../VENDOR-INTEGRATION.md)** | 下一章: [07 检查清单与体系定位](07-checklist-architecture.md) →
