---
id: "windows-powershell-heredoc"
title: "Windows PowerShell 不支持 heredoc 语法"
x-toml-ref: "../../../.meta/toml/docs/knowledge/operations/windows-powershell-heredoc.toml"
category: "operations"
tags: ["windows", "powershell", "shell", "heredoc", "git"]
date: "2026-06-23"
status: reviewed
author: ""
summary: "记录 Windows PowerShell 环境下 heredoc 语法不可用的替代方案"
---
# Windows PowerShell 不支持 heredoc 语法

## 背景

本项目开发环境为 Windows，使用 PowerShell 7+ 作为终端。在日常开发中，经常需要执行 `git commit` 命令提交代码变更，并编写多行提交消息。在 Linux/macOS 的 Bash 环境中，通常使用 heredoc 语法（`<<'EOF' ... EOF`）来传递多行文本，但在 Windows PowerShell 环境下，该语法并不被支持。

## 问题/场景

在执行 `git commit -m "$(cat <<'EOF' ... EOF)"` 时，PowerShell 报错：

```
Missing file specification after redirection operator.
```

这是因为 PowerShell 的 `<<` 操作符语义与 Bash 不同，PowerShell 无法识别 heredoc 语法，导致命令解析失败。

## 解决方案/经验

在 PowerShell 环境下，有以下几种替代方案：

### 方案一：使用双 `-m` 参数（推荐）

`git commit` 支持多次指定 `-m` 参数，第一个 `-m` 作为标题，后续 `-m` 作为正文段落：

```powershell
git commit -m "feat(vendor): 将 libs/ 目录重命名为 vendor/" -m "说明：采用业界标准命名约定，与 PHP Composer、Go modules 等生态保持一致。"
```

**优点**：无需额外文件，命令简洁，适合提交消息较短（2-3 段）的场景。

**缺点**：消息较长时命令行可读性较差。

### 方案二：使用 `-F` 参数从文件读取

先将要提交的消息写入临时文件，再通过 `-F` 参数读取：

```powershell
@"
feat(vendor): 将 libs/ 目录重命名为 vendor/

说明：
- 采用业界标准命名约定
- 与 PHP Composer、Go modules 等生态保持一致
- 语义更明确，表明目录存放的是第三方依赖
"@ | Out-File -FilePath tempfile.txt -Encoding utf8

git commit -F tempfile.txt
Remove-Item tempfile.txt
```

**优点**：支持任意长度的多行消息，格式清晰。

**缺点**：需要创建和清理临时文件，步骤较多。

### 方案三：使用 PowerShell Here-String

PowerShell 本身提供了 `@"..."@` 和 `@'...'@` 两种 here-string 语法，可用于构建多行字符串变量：

```powershell
$msg = @"
feat(vendor): 将 libs/ 目录重命名为 vendor/

说明：
- 采用业界标准命名约定
- 与 PHP Composer、Go modules 等生态保持一致
"@

git commit -m $msg
```

**优点**：利用 PowerShell 原生特性，无需临时文件。

**缺点**：`$msg` 变量的全部内容会被合并为一个 `-m` 参数，标题和正文之间没有 Git 层面的分隔。

## 参考

- [PowerShell about_Quoting_Rules - Here-Strings](https://learn.microsoft.com/zh-cn/powershell/module/microsoft.powershell.core/about/about_quoting_rules?view=powershell-7.4#here-strings)
- [Git Documentation - git-commit](https://git-scm.com/docs/git-commit)