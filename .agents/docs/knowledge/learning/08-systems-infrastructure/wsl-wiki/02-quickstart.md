---
id: wsl-wiki-02-quickstart
title: "快速开始"
source: "spec:create-wsl-wiki-tutorial"
date: "2026-07-20"
category: "learning"
tags: ["wsl", "quickstart", "getting-started", "basic-commands", "interop"]
---

# 快速开始

本章帮助你在安装完成后快速上手 WSL，掌握基本命令、运行第一个 Linux 程序，并体验 Windows 与 Linux 的无缝互操作。

## 1. 5 分钟快速上手指南

如果你已经按照上一章完成了安装，按照以下步骤可以在 5 分钟内开始使用 WSL：

| 步骤 | 操作 | 预计时间 |
|-----|------|---------|
| 1 | 从开始菜单启动 Ubuntu（或你安装的发行版） | 10 秒 |
| 2 | 首次启动时设置 Linux 用户名和密码 | 1 分钟 |
| 3 | 更新软件包列表：`sudo apt update && sudo apt upgrade -y` | 2 分钟 |
| 4 | 验证互操作：在 WSL 中运行 `notepad.exe` | 10 秒 |
| 5 | 验证文件互访：`explorer.exe .` 打开当前目录 | 10 秒 |
| 6 | 运行第一个 Linux 命令：`echo "Hello WSL!"` | 即刻 |

完成后你就拥有了一个可用的 Linux 环境！

## 2. 基本命令

### 2.1 启动 WSL

启动默认发行版（直接进入 Linux Shell）：

```powershell
wsl
```

或从开始菜单点击你安装的发行版图标启动。

### 2.2 启动指定发行版

如果你安装了多个发行版，可以指定启动某一个：

```powershell
wsl -d Ubuntu-24.04
```

或使用长参数：

```powershell
wsl --distribution Ubuntu-24.04
```

### 2.3 查看运行中的发行版

列出当前正在运行的 WSL 发行版：

```powershell
wsl --list --running
```

输出示例：

```
  NAME            STATE
* Ubuntu          Running
```

### 2.4 关闭 WSL

关闭所有正在运行的 WSL 发行版（立即终止虚拟机）：

```powershell
wsl --shutdown
```

这在需要重启 WSL 以应用配置更改时非常有用。

### 2.5 终止指定发行版

只关闭某一个特定的发行版，不影响其他发行版：

```powershell
wsl --terminate Ubuntu
```

或短别名：

```powershell
wsl -t Ubuntu
```

### 2.6 在 WSL 中运行单个 Linux 命令

不进入交互式 Shell，直接在 WSL 中执行 Linux 命令并返回结果：

```powershell
wsl ls -la
```

例如：查看当前目录下的文件列表：

```powershell
wsl ls -la ~
```

查找包含特定文本的文件：

```powershell
wsl grep "pattern" file.txt
```

运行复杂命令（注意引号转义）：

```powershell
wsl bash -c "sudo apt update && sudo apt upgrade -y"
```

### 2.7 在 Windows 中使用 WSL 命令

在 PowerShell 或 cmd 中，你可以直接使用 `wsl` 前缀调用任何 Linux 命令：

```powershell
wsl uname -a
wsl whoami
wsl pwd
wsl cat /etc/os-release
```

## 3. 第一个 Linux 程序

### 3.1 设置 Linux 用户和密码

首次启动 WSL 发行版时，系统会提示你创建一个 Linux 用户账户：

```
Installing, this may take a few minutes...
Please create a default UNIX user account. The username does not need to match your Windows username.
For more information visit: https://aka.ms/wslusers
Enter new UNIX username: yourname
New password:
Retype new password:
passwd: password updated successfully
Installation successful!
```

**注意**：
- Linux 用户名和密码与 Windows 账户独立，可以不同
- 输入密码时屏幕不会显示任何字符，这是正常的安全设计
- 这个用户默认拥有 sudo（管理员）权限

### 3.2 更新包管理器

首次进入 Linux 后，建议先更新软件包列表和已安装的软件：

```bash
sudo apt update && sudo apt upgrade -y
```

- `sudo`：以管理员权限执行命令（需要输入你刚设置的 Linux 密码）
- `apt update`：更新软件包索引
- `apt upgrade -y`：升级所有可升级的软件包，`-y` 表示自动确认

> **提示**：对于 Ubuntu/Debian 系发行版，`apt` 是包管理器；如果你使用的是 Fedora，用 `dnf`；Arch Linux 用 `pacman`。

### 3.3 安装并运行 Hello World

让我们写一个简单的 C 语言 Hello World 程序来验证环境：

1. **安装 GCC 编译器**：

```bash
sudo apt install -y gcc
```

2. **创建 Hello World 程序**：

```bash
cat > hello.c << 'EOF'
#include <stdio.h>

int main() {
    printf("Hello, WSL!\n");
    printf("Welcome to Linux on Windows!\n");
    return 0;
}
EOF
```

3. **编译程序**：

```bash
gcc hello.c -o hello
```

4. **运行程序**：

```bash
./hello
```

你应该看到输出：

```
Hello, WSL!
Welcome to Linux on Windows!
```

恭喜！你已经在 WSL 中成功编译并运行了第一个 Linux 程序。

### 3.4 安装常用工具

安装一些开发常用的基础工具：

```bash
sudo apt install -y git curl wget vim build-essential
```

- `git`：版本控制工具
- `curl` / `wget`：网络下载工具
- `vim`：文本编辑器
- `build-essential`：包含 GCC、Make 等编译工具链

## 4. 互操作初体验

WSL 最强大的特性之一是 Windows 与 Linux 之间的无缝互操作。

### 4.1 Linux 中调用 Windows 程序

在 WSL 的 Linux Shell 中，你可以直接运行任何 Windows 可执行程序（`.exe` 文件）：

**打开记事本**：

```bash
notepad.exe
```

**在文件资源管理器中打开当前目录**：

```bash
explorer.exe .
```

> **提示**：`.` 代表当前目录，这是快速在 Windows 中浏览/编辑 WSL 文件的好方法。

**打开 VS Code 编辑当前目录**（如果你安装了 VS Code）：

```bash
code .
```

**调用 Windows cmd 命令**：

```bash
cmd.exe /c "dir C:\\"
```

**使用 Windows 的 PowerShell**：

```bash
powershell.exe -Command "Get-Process | Select-Object -First 5"
```

> **原理**：WSL 将 Windows 的 `C:\Windows\System32` 等路径加入了 Linux 的 PATH 环境变量，因此可以直接找到 `.exe` 文件。运行 Windows 程序时，WSL 会自动处理路径转换和工作目录。

### 4.2 Windows 中调用 Linux 命令

在 Windows PowerShell 或 cmd 中，使用 `wsl` 前缀可以直接调用 Linux 命令：

**列出 Linux 主目录的文件**：

```powershell
wsl ls -la ~
```

**使用 Linux 的 grep 搜索文件内容**（比 Windows 的 findstr 更强大）：

```powershell
wsl grep "search pattern" *.txt
```

**使用 Linux 的管道和工具链**：

```powershell
wsl bash -c "cat /var/log/syslog | tail -20"
```

**用 Linux 命令处理 Windows 文件**：

```powershell
wsl wc -l C:\Windows\WindowsUpdate.log
```

### 4.3 跨文件系统访问

WSL 允许双向访问对方的文件系统。

#### 4.3.1 Windows 访问 Linux 文件

在 Windows 的文件资源管理器地址栏输入以下路径访问 WSL 内的文件：

```text
\\wsl.localhost\Ubuntu\
```

或旧格式（仍兼容）：

```text
\\wsl$\Ubuntu\
```

- 将 `Ubuntu` 替换为你的发行版名称
- 你可以像访问本地磁盘一样浏览、复制、编辑 WSL 中的文件
- 你也可以直接在 PowerShell 中访问：

```powershell
cd \\wsl.localhost\Ubuntu\home\
dir
```

> **性能建议**：如果你在 WSL 中进行开发工作（如运行 npm、编译代码），**务必将项目文件放在 Linux 文件系统（`\\wsl.localhost\`）中**，而不是 `/mnt/c/` 下，这会获得数倍到数十倍的性能提升。

#### 4.3.2 Linux 访问 Windows 文件

Windows 的所有驱动器会自动挂载到 Linux 的 `/mnt/` 目录下：

- `C:` 盘 → `/mnt/c/`
- `D:` 盘 → `/mnt/d/`
- `E:` 盘 → `/mnt/e/`
- 以此类推...

**列出 C 盘根目录内容**：

```bash
ls /mnt/c/
```

**访问 Windows 桌面**：

```bash
ls /mnt/c/Users/$USER/Desktop/
```

（注意：`$USER` 这里是 Linux 的用户名，如果 Windows 用户名不同请替换）

**在 WSL 中编辑 Windows 文件**：

```bash
notepad.exe /mnt/c/Users/YourName/Documents/note.txt
```

## 5. 快速检查清单

完成安装后，用以下清单确认你的 WSL 环境运行正常：

### 5.1 确认 WSL2 正在运行

在 PowerShell 中执行：

```powershell
wsl -l -v
```

检查输出：
- [ ] `VERSION` 列显示 `2`（不是 1）
- [ ] 你的发行版显示在列表中
- [ ] 带星号的是你期望的默认发行版

### 5.2 确认互操作可用

在 WSL 的 Linux Shell 中执行：

```bash
notepad.exe
```

检查：
- [ ] Windows 记事本成功弹出
- [ ] 没有报错信息

### 5.3 确认文件互访正常

**从 Linux 访问 Windows**：

```bash
ls /mnt/c/Users/
```

- [ ] 能看到 Windows 用户目录列表

**从 Windows 访问 Linux**：

在 PowerShell 中执行：

```powershell
dir \\wsl.localhost\Ubuntu\home\
```

- [ ] 能看到 Linux 用户目录

### 5.4 确认基础命令工作

```bash
pwd
whoami
uname -a
cat /etc/os-release
```

- [ ] 所有命令正常执行，无报错
- [ ] `uname -a` 显示 Linux 内核版本

### 5.5 确认 sudo 权限正常

```bash
sudo -v
```

输入密码后：
- [ ] 没有报错
- [ ] 说明你的用户拥有正确的 sudo 权限

---

全部检查通过？恭喜！你的 WSL 环境已经就绪，可以开始 Linux 开发之旅了。下一章我们将详细介绍 WSL 的完整 CLI 命令参考。

---

- ← [上一章：安装与发行版管理](01-installation.md) | [返回目录](README.md) | [下一章：CLI 完整命令参考](03-cli-reference.md) →
