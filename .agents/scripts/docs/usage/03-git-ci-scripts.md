---
id: "scripts-usage-git-ci-scripts"
title: "Git与CI脚本使用说明"
source: "README.md#使用说明"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/docs/usage/03-git-ci-scripts.toml"
---
# Git与CI脚本使用说明

本文档描述 `.agents/scripts/` 目录下Git提交和CI流水线相关脚本的用法。

---

## git-commit-utf8.py

Windows 环境下安全提交中文 commit message 的工具。解决 GBK 终端通过 `git commit -m "中文"` 产生乱码（如"鏂板姛鑳"）的核心问题。

**原理**：通过 `git commit -F -` 从 stdin 读取 message，以原始 UTF-8 bytes 写入 stdin，完全绕过 shell 和 Git 命令行参数的编码转换层。

**自动模式**（默认）：检测到非ASCII字符自动走bytes通道，纯ASCII走普通`-m`快速路径（零开销）。

```bash
# 直接提交中文message（自动检测，安全模式）
python .agents/scripts/git-commit-utf8.py -m "fix: 修复中文乱码问题"

# add + commit 一步完成
python .agents/scripts/git-commit-utf8.py -m "feat: 新增功能" file1.py docs/README.md

# 从文件读取commit message
python .agents/scripts/git-commit-utf8.py -F commit-msg.txt

# 从stdin管道读取
echo "feat: xxx" | python .agents/scripts/git-commit-utf8.py --stdin

# 透传git参数（如--amend）
python .agents/scripts/git-commit-utf8.py -m "修正提交信息" --amend

# 预览模式（不实际提交）
python .agents/scripts/git-commit-utf8.py -m "测试" --dry-run

# 强制使用bytes通道（即使纯ASCII）
python .agents/scripts/git-commit-utf8.py -m "fix bug" --force-bytes
```

---

## ci-check.ps1

一键运行所有验证检查（Git 忽略规则、链接有效性、规格一致性、导航表更新）。适用于 CI/CD 流水线或手动提交前检查。

```powershell
.\ci-check.ps1
```

---

## scan-git-index-view.sh

并行会话共享工作区时的**只读**诊断工具：高频采样同一路径的 `git status --porcelain`、
`git ls-files` 计数与 `.git/index` 的 mtime，判定工作视图是否振荡（同一路径在两套视图下
是否出现不一致），并列出同时在跑的 git 进程辅助归因。配套规则见
[commit-staging-integrity.md](../../../rules/commit-staging-integrity.md)。

**纯只读**：不写入工作区、不修改索引、不创建文件。

```bash
# 采样仓库根 12 次（间隔 0.5s）
bash .agents/scripts/scan-git-index-view.sh

# 只采样某个目录，3 次、间隔 0.2s
bash .agents/scripts/scan-git-index-view.sh .trae/specs/okf-wiki-ecosystem -n 3 -i 0.2
```

退出码：`0` 视图稳定；`1` 观察到振荡；`2` 参数或环境错误（不在 git 仓库内 / 非法参数）。

> 由 `.temp/experiments/poll-index-20260917.sh`（2026-09-17 loopx OKF wiki 任务诊断探针）
> 泛化而来：路径/次数/间隔参数化、仓库根自动解析；采样三轴逻辑原样保留。

---

## 相关模式

- [工具工作流组合](../../../../docs/retrospective/patterns/methodology-patterns/tools-automation/tool-workflow-composition.md)
- [工具链成熟度](../../../../docs/retrospective/patterns/methodology-patterns/tools-automation/toolchain-maturity.md)

---

← 上一章: [生成与构建脚本](02-generate-build-scripts.md) | **[返回索引](../../README.md)**
