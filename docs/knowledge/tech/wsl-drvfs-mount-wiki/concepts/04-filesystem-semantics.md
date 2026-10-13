---
type: Concept
id: C-04
title: 不同底层文件系统的 DrvFs 语义差异
description: FAT 不区分大小写且不支持硬链接/符号链接；网络文件系统权限位恒报 0777、不区分大小写、不支持符号链接，实际可访问性只能靠尝试打开判断
tags: [wsl, drvfs, fat, network-filesystem, permissions, case-sensitivity, symlink]
generated:
  by: agent-trae
  at: "2026-10-13T20:20:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-13T20:40:00+08:00"
status: draft
stale_after: "2027-10-13"
sources:
  - id: S-001
    resource: /references/00-sources.md
    title: File System Improvements to the Windows Subsystem for Linux（微软官方归档博文）
  - id: S-003
    resource: /references/00-sources.md
    title: 博文评论区社区反馈
  - id: S-005a
    resource: /references/00-sources.md
    title: 跨 Windows 和 Linux 文件系统工作（现代官方文档）
---

# 不同底层文件系统的 DrvFs 语义差异

本节对应博文 *DrvFs behavior for different file systems* 一节。drvfs 是适配层，其行为随底层文件系统的能力而变化：底层没有的语义，drvfs 无法凭空提供（F-022）。

## 语义支持矩阵（博文原文）

| 语义 | 固定 NTFS | FAT | 网络文件系统 |
|---|---|---|---|
| 大小写敏感 | 按 NTFS/Windows 配置 | **不区分**（F-023） | **不区分**（F-026） |
| 硬链接 | 支持 | **不支持**（F-023） | 未承诺 |
| 符号链接 | 支持 | **不支持**（F-023） | **不支持**（F-026） |
| Linux 权限位 | drvfs 呈现 | 降级呈现 | **恒报 0777**（F-024） |
| 可访问性判断 | 元数据可用 | 元数据可用 | **只能尝试打开**（F-025） |

## 网络文件系统：权限位 0777 与「打开才知道」

在网络挂载上，drvfs 不设置正确的 Linux 权限位，所有文件（含本应受限的文件）都报告为完全访问权限 `0777`；要判断当前是否真能访问某个文件，**唯一方法是实际尝试打开它**（F-024/F-025）。

### 对 Linux 工作流的具体影响（洞察 I-2）

Linux 工具链普遍把权限位当作**真实元数据**来做安全与行为决策，在 0777 的网络挂载上这些决策全部基于失真信息：

- **SSH 客户端**要求私钥权限严格（拒绝组/其他可读），在恒报 0777 的挂载上会直接拒绝使用该密钥；
- `find -perm`、`test -x`、脚本可执行位判断等全部失去区分度；
- 反向问题同样存在：`ls -l` 显示 `rwxrwxrwx` **不代表真能访问**——先打开再下结论（F-025）。

**实践规则**：安全敏感或依赖权限位的工作负载（密钥、凭据、git 仓库的权限钩子）放在 WSL 原生 ext4 根文件系统，不要放网络挂载。

## 大小写不敏感

FAT 与网络文件系统均不区分大小写（F-023/F-026）：

- 同一目录下 `README.md` 与 `readme.md` 不能共存，跨平台同步代码仓库时可能发生文件互相覆盖；
- 在区分大小写的 ext4 上创建的两类文件，复制到这类挂载时会冲突，操作前应有预期。

## 链接语义缺失

- FAT：硬链接、符号链接均不支持（F-023）；
- 网络文件系统：符号链接不支持（F-026）。

依赖符号链接布局的工具链（node_modules 结构、venv、版本管理软链、git 的链接检出）在这些挂载上会失效或降级，应迁回 ext4。

## 性能注意（小文件密集 I/O）

博文评论区有多位读者报告主观基准：在 drvfs 访问的 Windows 文件系统上执行 tar/解压大量小文件、`make` 无变更依赖检查等操作，速度明显慢于同机传统虚拟机；亦有评论指出杀毒软件实时扫描对大量小文件访问有可观影响（F-029，C 级信源，测量方法不统一，仅作现象记录）。

现代官方文档给出明确的性能布局建议（F-034）：**让文件待在正在使用的系统那一侧**——纯 WSL/Linux 工作负载放 ext4 根文件系统（如 `/home/<user>/`，或从 Windows 侧经 `\\wsl$` 访问），需与 Windows 工具共享的文件放 `/mnt/<drive>`。详见 [05 版本边界与现代 WSL 演进](05-version-and-modern-wsl.md)。

## 相关概念

- [02 挂载 UNC 网络位置与凭据边界](02-network-mount.md)
- [05 版本边界与现代 WSL 演进](05-version-and-modern-wsl.md)
