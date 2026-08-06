---
id: "ai-powershell5-hell-wiki-05-defense-patterns"
title: "防御性模式与最佳实践总览"
source: "internal:ai-powershell5-research-rfive"
date: "2026-07-31"
category: "learning"
tags: ["powershell", "powershell-5.1", "ai-coding", "defensive-patterns", "best-practices", "reusable-patterns"]
---

# 防御性模式与最佳实践总览

本章介绍 5 个可复用防御模式，所有模式均已纳入 V 阶段三视角 12 个攻击点的对抗审查加固。每个模式解决特定场景下的 AI×PS5 兼容性问题，可单独使用也可组合使用。

## 模式总览

| 模式 ID | 模式名称 | 核心解决问题 | 触发时机 |
|---------|---------|-------------|---------|
| P-PS5-PROMPT-001 | PS5-Defensive-Prompt（防御性 Prompt 模板） | 从源头预防 AI 生成 PS7 语法/不兼容代码 | 使用 AI 生成 PS5 代码前 |
| P-PS5-PREFLIGHT-001 | PS5-Compat-Preflight（兼容性预检 Checklist） | AI 生成代码后执行前进行兼容性检查 | 代码生成后、执行前、CI/CD 门禁 |
| P-PS5-SECAUDIT-001 | PS5-Security-Audit（安全代码审查 Checklist） | 检查安全漏洞和 CLM 兼容性 | 代码审查、上线前安全审计 |
| P-PS5-SAFEDEFAULTS-001 | PS5-Safe-Defaults（安全默认值防护） | 脚本开头标准安全头，处理编码/TLS/错误处理 | 所有 PS5 脚本开头 |
| P-PS5-TRANSLATE-001 | PS7-to-PS5-Translation（PS7 语法降级转换） | 将 PS7 代码转换为 PS5 兼容写法 | 遇到 PS7 代码需要在 PS5 运行时 |

---

## 模式 1：PS5-Defensive-Prompt（防御性 Prompt 模板模式）

### 模式定位

这是**源头预防**模式——在 AI 生成代码前通过精心设计的 Prompt 约束 AI 行为，从根本上减少不兼容代码的产生。

### 核心内容

完整版系统 Prompt、精简版快速 Prompt、3 种场景变体（脚本开发/CI-CD/系统管理），包含：
- 版本约束（最高优先级：明确目标是 Windows PowerShell 5.1）
- 禁用语法列表（7 种 PS7+ 运算符）
- API 使用规则（WMI→CIM、不使用 pwsh.exe 等）
- 编码与默认值要求（显式 -Encoding utf8、TLS 追加设置）
- 保守兼容模式（CLM 兼容：原生 cmdlet、禁止 Add-Type/class）
- 安全要求（永远不用 Invoke-Expression、ExecutionPolicy 分级建议、变量前缀规范）
- 代码质量要求（Set-StrictMode、全局状态保存-恢复、错误处理）

完整 Prompt 模板参见 [06-prompt-templates.md](06-prompt-templates.md)。

### 反模式

- ❌ 无版本提示直接让 AI 写 PowerShell 代码（"帮我写一个 PowerShell 脚本"）
- ❌ 黑名单不完整的提示词（只禁止 `&&` 不禁止 `??`/`?:`/`-Parallel`）
- ❌ 使用模糊表述（"为 PowerShell 生成兼容代码"——AI 无法区分 5.1 还是 7+）
- ❌ 提示词中包含"使用最新语法"或"现代 PowerShell"

---

## 模式 2：PS5-Compat-Preflight（兼容性预检 Checklist 模式）

### 模式定位

这是**执行前验证**模式——即使使用了防御性 Prompt，AI 仍可能生成不兼容代码（模型非 100% 可靠），需要通过 Checklist 和自动检查脚本在执行前拦截问题。

### 核心内容

按三级优先级组织 27 个检查项：
- **P0 阻断项**（8 项）：必须全部通过，否则禁止执行。包括 PS7+ 禁用语法检测、WMI cmdlet 检测、Workflow/Add-PSSnapin/pwsh.exe/Invoke-Expression 检测、class/Add-Type 检测
- **P1 高危项**（9 项）：强烈建议修复。包括文件输出编码、TLS 设置、自动变量覆盖、非白名单 COM、.NET 直接调用注册表、irm|iex 检测、执行策略硬编码、UTF-8 无 BOM 检测、全局状态无恢复检测
- **P2 建议项**（10 项）：提升健壮性。包括 #Requires 版本声明、Set-StrictMode、$ErrorActionPreference、模块检测、参数类型约束、危险操作确认、CLM 检测、-NoParallel 开关、注释帮助、版本元数据

配套一键预检脚本，可在 CI/CD 中作为门禁使用。

完整 Checklist 和脚本参见 [07-checklists.md](07-checklists.md)。

---

## 模式 3：PS5-Security-Audit（安全代码审查 Checklist 模式）

### 模式定位

这是**安全审计**模式——从安全维度审查脚本，覆盖 CLM 兼容性、命令注入防护、凭证处理、执行策略、编码安全、防御性编程 6 个维度共 29 个检查项。

### 核心内容

- **维度 1：CLM 兼容性**（6 项）：Add-Type/class/非白名单 COM/.NET 直接调用/XAML/语言模式检测
- **维度 2：命令注入防护**（6 项）：Invoke-Expression 禁用、类型约束、字符串拼接、irm|iex、scriptblock 使用、cmd 转义
- **维度 3：凭证与敏感信息处理**（5 项）：硬编码凭证、明文密码、凭证输出、临时文件清理、HTTPS 传输
- **维度 4：执行策略与权限控制**（4 项）：全局 Bypass 检测、组策略检测、管理员权限检测、CI 中 -Scope Process
- **维度 5：编码安全与数据保护**（4 项）：TLS 追加模式、证书验证禁用、文件编码、临时文件清理
- **维度 6：安全默认值与防御性编程**（6 项）：自动变量覆盖、危险操作 -WhatIf、Set-StrictMode、全局状态恢复、错误处理、模块检测

配套安全审查评分模板。

完整 Checklist 参见 [07-checklists.md](07-checklists.md)。

---

## 模式 4：PS5-Safe-Defaults（安全默认值防护模式）

### 模式定位

这是**脚本模板**模式——所有 PS5 脚本开头的标准"安全头"，统一处理错误处理、编码设置、TLS 兼容性、执行策略检测、CLM 检测、自动变量防护等默认值问题。

### 核心内容

生产级安全默认值完整代码片段（已纳入全部 V 阶段加固）：
1. 错误处理与严格模式：`$ErrorActionPreference = 'Stop'`、`Set-StrictMode -Version Latest`
2. 保存原始全局状态（用于 finally 恢复，B3 加固）
3. 编码设置（UTF-8 支持）
4. TLS 协议兼容性设置（追加而非覆盖模式，A2/C2 加固：Tls13 枚举值硬编码兼容旧 .NET、Verbose 日志）
5. 执行策略检测与友好提示（B2 加固：检测组策略锁定，不盲目 Set-ExecutionPolicy）
6. 语言模式检测（CLM 兼容性提示，B1 加固：保守兼容而非保证 CLM 运行）
7. 自动变量防护检测
8. try/catch/finally 包裹业务逻辑，finally 中恢复原始全局状态（B3 加固）

还提供：
- 精简版安全头（适合短脚本）
- 并行处理安全模板（含 CLM/EDR 兼容、`-NoParallel` 开关、完整资源清理，A3/B4/C3 加固）

完整安全头模板请参考模式详细说明，核心原则已融入后续各章节代码示例。

---

## 模式 5：PS7-to-PS5-Translation（PS7 语法降级转换模式）

### 模式定位

这是**代码转换**模式——当遇到 PS7 代码（AI 生成的或网上找到的示例）需要在 PS5.1 中运行时，提供系统化的转换映射表和降级方案。

### 核心内容

4 张映射表：

1. **语法转换映射表**（运算符与语言结构）：`&&`/`||`/`?:`/`??`/`??=`/`?.`/`-Parallel`/`class` 等的 PS5 替代写法
2. **API 转换映射表**（Cmdlet 与 .NET API）：WMI→CIM、workflow→普通函数、pwsh.exe→powershell.exe 完整路径等
3. **行为差异处理映射表**（默认行为与编码）：重定向编码、BOM、TLS、Write-Host 流、CIM 默认协议等
4. **并行处理降级方案对照表**：按场景（CLM 兼容性、EDR 友好、性能）选择 ForEach-Object 顺序/Start-Job/Runspace/任务计划程序

还提供自动转换辅助正则脚本（注意误报风险，转换后需人工审查）。

映射表核心内容已融入 [01-ps5-ps7-differences.md](01-ps5-ps7-differences.md)。

---

## 模式选择指南

```
开始使用 AI 生成 PS5 代码
    │
    ▼
┌─────────────────────────────────────┐
│  是否已有防御性 Prompt 模板？        │
│  （模式1: PS5-Defensive-Prompt）    │
└───────────┬─────────────────────────┘
            │ 否 → 使用模式1 Prompt
            │ 是
            ▼
┌─────────────────────────────────────┐
│  AI 生成代码后，执行前              │
│  （模式2: PS5-Compat-Preflight）    │
└───────────┬─────────────────────────┘
            │ 运行预检脚本/P0 Checklist
            │ P0 不通过 → 修复/重新生成
            │ P0 通过
            ▼
┌─────────────────────────────────────┐
│  代码审查/上线前                    │
│  （模式3: PS5-Security-Audit）      │
└───────────┬─────────────────────────┘
            │ 安全审查 Checklist
            │ P0 问题=0 方可上线
            ▼
┌─────────────────────────────────────┐
│  编写新脚本时                       │
│  （模式4: PS5-Safe-Defaults）       │
└───────────┬─────────────────────────┘
            │ 脚本开头使用安全头模板
            ▼
┌─────────────────────────────────────┐
│  遇到 PS7 代码需在 PS5 运行         │
│  （模式5: PS7-to-PS5-Translation）  │
└───────────┬─────────────────────────┘
            │ 使用映射表转换
            │ 转换后重新过模式2预检
            ▼
        可执行/上线
```

## V 阶段加固点应用验证

所有 18 个 V 阶段加固项已应用于对应模式：

| 加固项 | 应用模式 | 状态 |
|--------|---------|------|
| A1: ExecutionPolicy 分级+Bypass 安全警示 | PROMPT/SAFEDEFAULTS/SECAUDIT | ✅ |
| A2: TLS 追加而非覆盖，避免安全降级 | SAFEDEFAULTS/SECAUDIT/TRANSLATE | ✅ |
| A3: Runspace 标注 CLM 不兼容+安全提示+资源清理 | SAFEDEFAULTS/PREFLIGHT | ✅ |
| A4: 环境探测调试条件化输出 | SAFEDEFAULTS | ✅ |
| B1: "CLM 兼容"改为"保守兼容"+环境验证 | PROMPT/SAFEDEFAULTS/SECAUDIT | ✅ |
| B2: 组策略锁定检测，不盲目 Set-ExecutionPolicy | SAFEDEFAULTS/SECAUDIT | ✅ |
| B3: 全局状态保存-恢复 try/finally 模式 | SAFEDEFAULTS/SECAUDIT | ✅ |
| B4: EDR 兼容性提示+-NoParallel 降级开关 | SAFEDEFAULTS/TRANSLATE | ✅ |
| C1: 改进 PS7 语法检测正则减少误报 | PREFLIGHT/PROMPT/TRANSLATE | ✅ |
| C2: TLS13 注释+Verbose 日志+硬编码值兼容 | SAFEDEFAULTS | ✅ |
| C3: 生产级 Runspace 模板含完整错误处理/清理 | SAFEDEFAULTS | ✅ |
| C4: 版本元数据+更新触发条件+维护 SOP | 所有模式 | ✅ |
| S-01: 注入示例脱敏，无具体攻击载荷 | 所有模式 | ✅ |
| S-03: 永远不要使用 Invoke-Expression 表述 | PROMPT/SECAUDIT/PREFLIGHT | ✅ |
| S-05: ExecutionPolicy Bypass 强制安全警示 | PROMPT/SAFEDEFAULTS/SECAUDIT | ✅ |
| S-06: irm\|iex 安全警告强化 | PROMPT/SECAUDIT/PREFLIGHT | ✅ |

---

## 关键原则总结

使用所有模式时应遵循以下核心原则：

1. **防御性默认原则**：默认假设最保守环境（CLM、Restricted 策略、TLS 1.2 未启用），渐进式启用功能
2. **版本提示是必要前提**：没有版本提示的 AI PS 代码请求 = 随机结果
3. **预检优于调试**：执行前用 Checklist/脚本拦截问题，比运行后调试成本低 10 倍
4. **永远不要使用 Invoke-Expression**：即使输入完全可控，代码会演化
5. **全局状态必须恢复**：脚本修改的编码/TLS/错误处理设置必须在 finally 中恢复
6. **企业环境是默认现实**：从"企业默认受限"出发设计，而非"开发者本地管理员"
7. **文档和代码需要维护意识**：版本标记、注释、错误处理不是锦上添花而是生存必需

---

**下一章**：[06-prompt-templates.md](06-prompt-templates.md) — 即用型 Prompt 模板库，包含完整版系统 Prompt、精简版快速 Prompt、3 种场景变体。
