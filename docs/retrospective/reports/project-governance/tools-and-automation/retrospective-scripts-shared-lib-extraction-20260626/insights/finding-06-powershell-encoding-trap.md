+++
id = "finding-powershell-encoding-trap"
date = "2026-06-28"
type = "insight"
scope = "powershell,encoding,windows,ci"
source = "../insight-extraction.md#发现-6windows-powershell-编码陷阱"
+++

# 发现6：Windows PowerShell 编码陷阱

## 事件发现

`ci-check.ps1` 使用UTF-8无BOM+LF换行写入后，PowerShell 5.x报语法错误"字符串缺少终止符"和"意外的}"。

## 规律

Windows PowerShell 5.x 对脚本文件有两个隐含要求：

1. **UTF-8 with BOM**：含中文字符的脚本如果使用UTF-8无BOM编码，中文可能被误解析为控制字符，导致字符串解析错误
2. **CRLF 换行符**：LF-only换行在某些情况下会导致PowerShell的块结构解析错误（花括号匹配失败）

## 复现条件

- Windows系统 + PowerShell 5.x（Windows 10/11默认版本）
- 脚本中包含中文字符（注释、输出字符串）
- 文件编码为UTF-8无BOM 或 换行符为LF

## 对策

| 方案 | 操作 | 适用场景 |
|------|------|---------|
| 显式写入BOM+CRLF | 生成.ps1时使用 `encoding='utf-8-sig'` 并写CRLF | 兼容PS 5.x |
| 声明PS7+ | 在脚本首行添加 `#requires -Version 7` | 项目统一使用PS7+ |
| 避免中文输出 | 脚本中不使用中文/特殊字符 | 临时规避（不推荐） |

本次采用方案1（显式写入UTF-8 BOM + CRLF）修复。

## 关联洞察

- [finding-02-refactoring-bug-finder.md](finding-02-refactoring-bug-finder.md) — 重构暴露了此隐藏bug
- [finding-07-tool-self-validation.md](finding-07-tool-self-validation.md) — CI集成验证时发现此问题

---
*来源：[脚本共享库提取复盘](../README.md)*
