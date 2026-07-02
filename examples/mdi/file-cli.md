---
name: file-cli
version: "1.0.0"
description: 文件操作命令行工具，提供文件列出、复制、删除等常用文件管理功能
type: clitool
authors:
  - SpecWeave Team
license: MIT
tags:
  - cli
  - file
  - utility
---

# 文件操作 CLI 工具

一个轻量级的跨平台文件操作命令行工具，支持文件列出、复制、删除等常用文件管理功能。

## 工具概述

file-cli 提供了一套简洁的命令行接口，用于日常文件管理操作。所有命令支持递归操作、通配符匹配和 dry-run 预览模式。

## 安装

```bash
pip install file-cli
```

## 命令列表

### list - 列出目录内容

列出指定目录下的文件和子目录，支持过滤和排序。

```{endpoint} CMD list
:summary: 列出目录内容
:param path: string - 目标目录路径，默认为当前目录
:param recursive?: boolean = false - 是否递归列出子目录
:param pattern?: string - 文件名通配符过滤模式（如 *.py）
:param sort_by?: string = name - 排序方式：name/size/modified
:param show_hidden?: boolean = false - 是否显示隐藏文件
:response 0: 成功 - 命令执行成功，输出文件列表
:error 1: PATH_NOT_FOUND - 指定路径不存在
:error 2: PERMISSION_DENIED - 无权限访问该目录
```

### copy - 复制文件或目录

将文件或目录从源路径复制到目标路径，支持覆盖确认和递归复制。

```{endpoint} CMD copy
:summary: 复制文件或目录
:param source: string - 源文件或目录路径（必填）
:param destination: string - 目标路径（必填）
:param recursive?: boolean = false - 是否递归复制目录
:param force?: boolean = false - 强制覆盖已存在的目标文件
:param preserve_metadata?: boolean = true - 保留文件元数据（时间戳、权限）
:response 0: 成功 - 文件复制成功
:error 1: SOURCE_NOT_FOUND - 源文件不存在
:error 2: DEST_EXISTS - 目标已存在（使用 --force 覆盖）
:error 3: PERMISSION_DENIED - 无写入权限
```

### delete - 删除文件或目录

删除指定的文件或目录，支持交互式确认和递归删除。

```{endpoint} CMD delete
:summary: 删除文件或目录
:param target: string - 要删除的文件或目录路径（必填）
:param recursive?: boolean = false - 是否递归删除非空目录
:param force?: boolean = false - 强制删除（不提示确认）
:param dry_run?: boolean = false - 预览模式，仅显示将被删除的文件
:response 0: 成功 - 文件删除成功
:error 1: TARGET_NOT_FOUND - 目标文件不存在
:error 2: DIR_NOT_EMPTY - 目录非空（使用 --recursive 递归删除）
:error 3: PERMISSION_DENIED - 无删除权限
```

## 配置

### 环境变量

| 变量名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| FILE_CLI_CONFIG | string | ~/.file-cli.toml | 配置文件路径 |
| FILE_CLI_VERBOSE | boolean | false | 是否启用详细输出 |

### 配置文件

配置文件使用 TOML 格式，支持以下选项：

```toml
default_sort_by = "name"
show_hidden = false
confirm_before_delete = true
```
