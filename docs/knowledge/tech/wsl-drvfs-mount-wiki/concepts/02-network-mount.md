---
type: Concept
id: C-02
title: 挂载 UNC 网络位置与凭据边界
description: drvfs 支持直接挂载 \\server\share；UNC 路径须单引号包裹或双写反斜杠；凭据只能在 Windows 侧建立，可经 net.exe use 经 interop 预认证
tags: [wsl, drvfs, unc, smb, network, credentials, interop]
generated:
  by: agent-trae
  at: "2026-10-13T20:16:00+08:00"
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
---

# 挂载 UNC 网络位置与凭据边界

本节对应博文 *Mounting network locations* 一节。网络共享有两种接入路径，关键陷阱是**凭据不在挂载命令中提供**。

## 两种挂载路径

**路径 A：先在 Windows 映射网络驱动器，再按盘符挂载**

把共享映射成盘符后，它就是一个普通 Windows 驱动器，按 [01 DrvFs 手动挂载驱动器](01-drvfs-manual-mount.md) 的方式挂载即可（F-012）。

**路径 B：直接以 UNC 路径挂载（无需占用盘符）**

```bash
sudo mkdir /mnt/share
sudo mount -t drvfs '\\server\share' /mnt/share
```

## 反斜杠的两种写法（二选一）

```bash
# 写法 1：单引号包裹（推荐，路径原样保留）
sudo mount -t drvfs '\\server\share' /mnt/share

# 写法 2：不加引号，每个反斜杠双写转义
sudo mount -t drvfs \\server\share /mnt/share
```

Shell 中反斜杠是转义符；不写单引号又不双写，路径会被破坏（F-014）。多层路径同理：`'\\server\share\dir1\dir2'`。

## 凭据边界：WSL 挂载命令不接受凭据

博文明示：**WSL 没有任何方式为网络共享连接指定凭据**（F-015）。需要以非当前 Windows 身份连接时，凭据必须在 **Windows 侧**建立，途径有三（F-016）：

1. 在**文件资源管理器**中访问一次 `\\server\share`，弹出认证框时输入并选择记住凭据；
2. 使用 **Windows 凭据管理器**（Credential Manager）预先保存；
3. 使用 **`net use`** 命令。

`net use` 可通过 WSL interop 直接在 Bash 内调用（程序名写作 `net.exe`，F-017）：

```bash
# 查看用法
net.exe help use

# 典型用法：先在 Windows 侧建立带凭据的会话（参数以 net.exe help use 为准）
net.exe use \\server\share /user:DOMAIN\username *
# 随后再在 WSL 侧挂载
sudo mount -t drvfs '\\server\share' /mnt/share
```

> 洞察（I-3）：Linux 用户预期的 `mount.cifs` 式 `username=`/`password=` 选项在 drvfs 中**刻意不存在**。drvfs 只复用 Windows 已有的认证会话，自身不发起认证。

## 典型失败症状与排查顺序

评论区记录了这样一个案例（F-018，C 级信源）：对需要凭据的共享执行挂载，**命令无任何报错**，但挂载点不可访问：

```text
$ sudo mount -t drvfs '\fsfs\ddb' /mnt/ddb
$ ls /mnt/ddb
ls: cannot access '/mnt/ddb': No such file or directory
```

重复执行还会在 mount 列表中留下多条记录。这属于「Windows 侧尚未建立认证会话」时的表现，而非挂载器损坏。

排查顺序：

1. **先在 Windows 侧验证可达与认证**——资源管理器能否打开 `\\server\share`；不能则先用上述三途径之一建立凭据；
2. 回到 WSL 执行 drvfs 挂载；
3. 挂载后用实际访问验证，不要只看挂载命令是否报错。

## 语义降级提示

网络文件系统上权限位恒报 `0777`、不区分大小写、不支持符号链接，实际访问权限要靠尝试打开判断——详见 [04 不同底层文件系统的语义差异](04-filesystem-semantics.md)。这意味着把 SSH 私钥、git 仓库等依赖权限位的工作负载放在网络挂载上会出现语义失真。

## 相关概念

- [01 DrvFs 手动挂载驱动器](01-drvfs-manual-mount.md)
- [04 文件系统语义差异](04-filesystem-semantics.md)
- [05 版本边界与现代 WSL 演进](05-version-and-modern-wsl.md)
