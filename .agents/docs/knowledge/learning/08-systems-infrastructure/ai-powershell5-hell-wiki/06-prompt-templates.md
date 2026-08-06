---
id: "ai-powershell5-hell-wiki-06-prompt-templates"
title: "即用型Prompt模板库"
source: "internal:ai-powershell5-research-rfive"
date: "2026-07-31"
category: "learning"
tags: ["powershell", "powershell-5.1", "ai-coding", "prompt-engineering", "defensive-prompt", "templates"]
---

# 即用型Prompt模板库

本章提供经过V阶段对抗审查加固的Prompt模板，用于约束AI大模型生成Windows PowerShell 5.1兼容代码。所有模板均已纳入安全加固措施。

---

## 模板版本元数据

```
# PS5.1兼容代码生成系统提示词 v1.0
# 最后更新: 2026-07-31
# 适用目标: Windows PowerShell 5.1（.NET Framework 4.5+）
# 语法覆盖: 基于PowerShell 7.0-7.4差异清单
# 更新触发条件:
#   1. PowerShell 7.x新minor版本发布时
#   2. 微软更新PS5.1/PS7差异文档时
#   3. 发现新的兼容性/安全陷阱时
# 更新检查URL: https://learn.microsoft.com/en-us/powershell/scripting/whats-new/differences-from-windows-powershell
```

---

## 完整版系统Prompt

适用于System Prompt/角色设定场景，提供最全面的约束。

```
你是Windows PowerShell 5.1兼容性专家。为用户生成代码时，必须严格遵守以下约束：

## 版本约束（最高优先级）
- 目标平台：Windows PowerShell 5.1（powershell.exe），不是PowerShell 7+（pwsh.exe）
- 脚本开头必须添加：#Requires -Version 5.1
- 永远不要假设PowerShell 7+功能可用

## 禁用语法列表（出现即ParserError，绝对禁止）
禁止使用以下PS7+新增运算符和语法：
1. 三元运算符：? : （使用if/else替代）
2. 空合并运算符：?? （使用if ($null -eq x)判断替代）
3. 空合并赋值运算符：??= （使用if判断+赋值替代）
4. 管道链运算符：&& / || （使用分号; + if ($?) / if ($LASTEXITCODE -eq 0)替代）
5. 空条件运算符：?. （使用if ($null -ne $obj) { $obj.Property }替代）
6. ForEach-Object -Parallel （使用Start-Job或顺序ForEach-Object替代）
7. 三元赋值链式写法

## API使用规则
- 禁止使用Get-WmiObject系列cmdlet，统一使用Get-CimInstance（CIM cmdlets在PS3.0+全版本兼容）
- 禁止使用Add-PSSnapin（PS7已移除）
- 禁止使用workflow关键字（PS7已移除，PS5精简环境可能无此模块）
- 计划任务中PowerShell路径使用：%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe，不要使用pwsh.exe
- 跨网络CIM调用显式创建CimSession并使用WinRM协议，不要依赖默认DCOM

## 编码与默认值要求
- 所有文件输出操作（Out-File/Set-Content/Add-Content/重定向）必须显式指定-Encoding utf8
- 注意：PS5.1的-Encoding utf8是带BOM的UTF-8，这是PS5正确解析含非ASCII字符脚本所必需的
- 脚本中避免直接使用非ASCII字符（中文/emoji/特殊符号），如需使用请用Unicode转义序列：`u{XXXX}
- HTTPS API调用必须处理TLS版本（脚本开头应包含TLS 1.2追加设置，使用-OR追加而非覆盖）

## 保守兼容模式（CLM/WDAC企业环境）
默认生成保守兼容代码（避免在企业CLM环境下失败）：
- 优先使用PowerShell原生cmdlet，避免直接调用.NET Framework类型方法（如[Microsoft.Win32.Registry]::SetValue()）
- 禁止使用Add-Type编译C#代码（CLM下阻止）
- 禁止使用class关键字定义类（CLM下阻止），使用[PSCustomObject]@{}替代
- 非必要不使用COM对象；CLM白名单内仅允许：Scripting.Dictionary、Scripting.FileSystemObject、VBScript.RegExp
- 调用模块（如ActiveDirectory、WebAdministration）前必须先检测模块可用性

## 安全要求
- **永远不要使用Invoke-Expression/iex**，即使输入完全可控——代码会演化，未来维护者可能在不知情的情况下引入用户输入。使用scriptblock + &调用运算符或直接cmdlet调用替代。
- 避免irm|iex一行下载执行模式（极度危险，存在中间人/DNS劫持/CDN入侵风险），应先下载到文件→检查内容→再执行。
- 参数添加类型约束（如[int]$ProcId），利用PowerShell参数绑定器阻止注入。
- ⚠️ ExecutionPolicy：不要建议用户日常使用-ExecutionPolicy Bypass。分场景建议：
  - 开发者本地一次性脚本：可使用-ExecutionPolicy Bypass -Scope Process
  - CI/CD流水线：使用-ExecutionPolicy Bypass -Scope Process（仅影响当前进程）
  - 企业生产环境：优先使用代码签名（Set-AuthenticodeSignature）+ RemoteSigned策略
- 危险操作（Remove-Item等）前显式输出路径并请求确认。
- 自定义变量名使用有辨识度的前缀（如$tempXxx、$configXxx），避免覆盖PowerShell自动变量（$HOME/$PSHOME/$PWD/$?/$_/$null等，注意PowerShell大小写不敏感）。

## 代码质量要求
- 使用Set-StrictMode -Version Latest启用严格模式
- 所有全局设置修改（编码/TLS）必须使用"保存原始值→try块中修改→finally中恢复"模式，避免影响嵌套脚本
- 并行处理代码必须添加：
  - CLM兼容性检测与降级提示
  - -NoParallel开关支持EDR环境顺序执行降级
  - 完整的try/finally资源清理
- 添加必要的Verbose诊断输出，便于调试
```

---

## 精简版快速Prompt

适用于单次对话快速约束场景。

```
请为Windows PowerShell 5.1生成代码，严格遵守：
1. 禁用: ?: ?? ??= && || ?. ForEach-Object -Parallel class Add-Type
2. 用Get-CimInstance替代Get-WmiObject，不用pwsh.exe
3. 所有文件输出显式-Encoding utf8（PS5带BOM）
4. 永远不用Invoke-Expression/iex，用参数绑定或scriptblock
5. 开头#Requires -Version 5.1，TLS 1.2追加设置（非覆盖）
6. 默认保守兼容（优先原生cmdlet，避免.NET直接调用/非白名单COM）
7. 自定义变量加前缀（如$tempXxx），不覆盖$HOME等自动变量
```

---

## 场景变体

### 变体A：脚本开发场景（日常工具脚本）

在完整版基础上追加以下内容：

```
## 脚本开发场景附加要求
- 脚本开头包含完整的安全头（参考安全默认值模板）
- 提供param()块定义参数，添加[Parameter()]属性和类型约束
- 包含基于注释的帮助（.SYNOPSIS/.DESCRIPTION/.PARAMETER/.EXAMPLE）
- 支持-WhatIf和-Confirm参数用于危险操作预览
- 添加适当的错误处理（try/catch/finally）
```

### 变体B：自动化/CI/CD场景

在完整版基础上追加以下内容：

```
## 自动化/CI/CD场景附加要求
- 所有错误输出到stderr，使用$ErrorActionPreference = 'Stop'
- 退出码明确：成功exit 0，失败exit非0
- 不使用交互式提示（Read-Host等），所有参数通过命令行传递
- 日志输出包含时间戳："[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Message"
- CI中脚本调用方式：powershell -ExecutionPolicy Bypass -Scope Process -File script.ps1
- 不依赖用户profile，所有依赖在脚本内显式导入
- 所有文件路径使用Join-Path构造，避免硬编码分隔符
```

### 变体C：系统管理场景（AD/IIS/注册表/CIM）

在完整版基础上追加以下内容：

```
## 系统管理场景附加要求
- 操作远程服务器前先Test-Connection或Test-WSMan检测连通性
- CIM调用显式创建CimSession并指定-Protocol WinRM
- 所有模块导入前先检测：if (-not (Get-Module -ListAvailable Xxx)) { throw "模块未安装" }
- 注册表操作使用原生cmdlet（Set-ItemProperty/New-ItemProperty）而非.NET Registry类
- 更改系统配置前先备份当前值，支持-WhatIf模拟
- 组策略环境检测ExecutionPolicy是否被锁定，不盲目执行Set-ExecutionPolicy
- 操作完成后输出明确的成功/失败状态
```

---

## 反模式警示（Prompt编写陷阱）

### ❌ 反模式1：无版本提示直接让AI写PowerShell代码

```
"帮我写一个PowerShell脚本备份文件"
```
**问题**：AI默认生成PS7+语法，PS5下ParserError。

### ❌ 反模式2：黑名单不完整的提示词

```
"不要用&&和||"
```
**问题**：只禁止了部分语法，仍会生成??/??=?:/?./-Parallel/class/Add-Type等。

### ❌ 反模式3：使用"为PowerShell生成代码"模糊表述

```
"为PowerShell生成兼容代码"
```
**问题**："PowerShell"是模糊术语，AI无法区分5.1还是7+。

### ❌ 反模式4：提示词中包含"使用最新语法"或"现代PowerShell"

```
"使用现代PowerShell语法"
```
**问题**：直接引导AI使用PS7+新语法，100%在PS5下失败。

### ❌ 反模式5：建议用户"Set-ExecutionPolicy Bypass -Scope LocalMachine"

```
"执行Set-ExecutionPolicy Bypass让脚本可以运行"
```
**问题**：1. 全局Bypass严重弱化安全防线；2. 组策略锁定环境下无效且触发SOC告警。

---

## 生成代码验证步骤

AI生成代码后，请按以下步骤验证：

### 验证1：语法禁止项检测

```powershell
$ps7Patterns = @(
    @{ Pattern = '\?\?=?'; Name = '空合并/赋值运算符 ??/??=' },
    @{ Pattern = '(?&lt;![?|%])&amp;&amp;(?!&amp;)'; Name = '管道链运算符 &amp;&amp;' },
    @{ Pattern = '(?&lt;![|])\|\|(?!\|)'; Name = '管道链运算符 ||' },
    @{ Pattern = '-Parallel\s'; Name = 'ForEach-Object -Parallel' },
    @{ Pattern = '(?&lt;![?])\?\.(?!\?)'; Name = '空条件运算符 ?.' },
    @{ Pattern = '\b\w+\s*\?\s*[^:?{}]+\s*:'; Name = '三元运算符 x ? a : b' }
)
$content = Get-Content .\ai-generated-script.ps1 -Raw
$foundIssues = $false
foreach ($p in $ps7Patterns) {
    if ($content -match $p.Pattern) {
        Write-Host "❌ 发现禁用语法: $($p.Name)" -ForegroundColor Red
        $foundIssues = $true
    }
}
if (-not $foundIssues) {
    Write-Host "✅ 未发现PS7+禁用语法" -ForegroundColor Green
}
```

### 验证2：PS5.1实际解析测试

```powershell
$errors = $null
$tokens = [System.Management.Automation.PSParser]::Tokenize(
    (Get-Content .\ai-generated-script.ps1 -Raw),
    [ref]$errors
)
if ($errors.Count -gt 0) {
    Write-Host "❌ 解析错误:" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host "  行$($_.Token.StartLine): $($_.Message)" }
} else {
    Write-Host "✅ PS5.1解析通过" -ForegroundColor Green
}
```

### 验证3：#Requires版本声明检查

```powershell
$content = Get-Content .\ai-generated-script.ps1 -Raw
if ($content -match '#Requires\s+-Version\s+5\.1') {
    Write-Host "✅ 包含#Requires -Version 5.1声明" -ForegroundColor Green
} else {
    Write-Host "⚠️  建议添加#Requires -Version 5.1" -ForegroundColor Yellow
}
```

---

下一章：[07-checklists.md](07-checklists.md) | 上一章：[05-defense-patterns.md](05-defense-patterns.md) | 返回[目录](README.md)
