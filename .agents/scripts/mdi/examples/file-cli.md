---
name: file-cli
version: "2.1.0"
description: File manipulation CLI tool for batch operations on files and directories.
argument-hint: "[command] [options] [arguments]"
type: clitool
title: "File CLI Tool"
---
# File CLI Tool

A command-line file manipulation tool providing batch file operations including copying, moving, searching, and batch renaming. Designed for automation scripts and power users.

## Overview

`filecli` provides fast, reliable file operations with support for:
- Recursive directory operations
- Glob pattern matching
- Dry-run mode for safe previews
- Parallel processing for large batches
- Cross-platform support (Linux, macOS, Windows)

## Global Options

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--verbose`, `-v` | flag | no | Enable verbose output (default: false) |
| `--config`, `-c` | string | no | Path to config file (default: ~/.filecli.toml) |
| `--dry-run` | flag | no | Show what would be done without making changes |
| `--help`, `-h` | flag | no | Show help message |

## Commands

### copy

Copy files or directories from source to destination. Supports recursive copy, pattern matching, and overwrite control.

```{command} copy <source> <destination>
:summary: 复制文件或目录
:arg source: string - Source file or directory path (required)
:arg destination: string - Destination path (required)
:flag --recursive, -r: Copy directories recursively (default: false)
:option --pattern?: string - Glob pattern to filter files (e.g. "*.txt")
:option --exclude?: string - Glob pattern to exclude files
:flag --force, -f: Overwrite existing files without confirmation (default: false)
:flag --preserve: Preserve file permissions and timestamps (default: true)
:option --concurrency?: integer - Number of parallel copy workers (default: 4)
:exit 0: Copy completed successfully
:exit 1: General error (syntax error, source not found)
:exit 2: Permission denied
:exit 3: Destination already exists (without --force)
```

#### Examples

Copy a single file:

```bash
filecli copy document.txt backup/document.txt
```

Copy directory recursively with pattern filter:

```bash
filecli copy ./photos ./backup/photos --recursive --pattern "*.jpg"
```

Dry run to preview copy operations:

```bash
filecli copy ./data ./archive --recursive --dry-run
```

### move

Move files or directories from source to destination. Similar to copy but removes source after successful transfer.

```{command} move <source> <destination>
:summary: 移动文件或目录
:arg source: string - Source file or directory path (required)
:arg destination: string - Destination path (required)
:flag --force, -f: Overwrite existing files (default: false)
:flag --create-dirs: Create destination directories if missing (default: true)
:exit 0: Move completed successfully
:exit 1: Source not found or invalid path
:exit 2: Permission denied
:exit 3: Destination already exists
```

#### Examples

Move a file:

```bash
filecli move ./downloads/report.pdf ./documents/2026/
```

Move multiple files matching a pattern:

```bash
filecli move ./temp/*.log ./archive/logs/ --create-dirs
```

### search

Search for files matching a pattern in a directory tree. Supports regex patterns, content search, and size/date filters.

```{command} search <directory>
:summary: 搜索文件和目录
:arg directory: string - Root directory to search (required)
:option --name?: string - Filename glob pattern (e.g. "*.py")
:option --content?: string - Search file content for regex pattern
:option --type?: string - File type filter: file/dir/link/symlink
:option --min-size?: string - Minimum file size (e.g. "10MB", "500KB")
:option --max-size?: string - Maximum file size
:option --modified-after?: string - Only files modified after date (YYYY-MM-DD)
:option --modified-before?: string - Only files modified before date
:flag --case-sensitive: Case-sensitive search (default: false)
:flag --hidden: Include hidden files (default: false)
:option --max-depth?: integer - Maximum directory depth to search
:exit 0: Search completed (results may be empty)
:exit 1: Invalid pattern or directory not found
:exit 2: Permission denied on some paths
```

#### Examples

Find Python files larger than 1MB:

```bash
filecli search ./src --name "*.py" --min-size 1MB
```

Search file content for TODO comments:

```bash
filecli search ./project --content "TODO|FIXME" --type file
```

Find recently modified files:

```bash
filecli search . --modified-after 2026-06-01 --type file
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Permission denied |
| 3 | Resource conflict |
