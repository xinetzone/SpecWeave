---
id: "ps5-defensive-prompt"
source: "../../../../../../.trae/specs/ai-powershell5-hell-wiki/supporting-analysis/05-patterns.md#模式1ps5-defensive-prompt防御性prompt模板模式"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/retrospective/patterns/methodology-patterns/ai-collaboration/ps5-defensive-prompt.toml"
maturity: "L1"
validation_count: 1
reuse_count: 0
documentation_level: "standard"
pattern_id: "P-PS5-PROMPT-001"
tags: ["powershell", "powershell-5.1", "defensive-prompt", "ai-coding", "version-compatibility", "clm", "security", "prompt-engineering"]
related_patterns:
  - "ps5-compat-preflight"
  - "ps5-security-audit"
  - "ps5-safe-defaults"
  - "ps7-to-ps5-translation"
  - "bilingual-prompt-engineering"
---
> **提炼自**：[05-patterns.md#模式1](../../../../../../.trae/specs/ai-powershell5-hell-wiki/supporting-analysis/05-patterns.md#模式1ps5-defensive-prompt防御性prompt模板模式) —— AI大模型×PowerShell 5兼容安全研究E阶段萃取

# PS5防御性Prompt模板模式（PS5-Defensive-Prompt）

## 模式类型

方法论模式（AI协作/提示词工程/版本兼容性）

## 成熟度

L1 实验性（AI×PowerShell 5.1专题研究验证，单项目）

## 适用场景

- 使用AI大模型（GPT-4/Claude/GitHub Copilot等）生成Windows PowerShell 5.1代码时
- 未指定版本或版本提示模糊，导致AI默认生成PS7+语法时
- 需要生成可在企业受限环境（CLM/WDAC）运行的保守兼容代码时
- CI/CD流水线中需要AI辅助生成PS脚本时
- 批量脚本生成任务需要统一版本约束时

**不适用场景**：明确目标为PowerShell 7+（pwsh.exe）且无需兼容5.1的项目；非PowerShell语言的代码生成。

## 问题背景

AI大模型训练数据混合了PowerShell 5.1和PowerShell 7+的语法示例，在未明确版本约束时，默认倾向于生成PS7+新语法（三元运算符`?:`、空合并`??`、管道链`&&`/`||`、空条件`?.`、`ForEach-Object -Parallel`、`class`关键字等），这些语法在Windows自带的PowerShell 5.1（powershell.exe）中直接报ParserError，无法执行。

更严重的是，简单的版本提示（如"为PowerShell生成代码"）存在模糊性问题——"PowerShell"这个术语无法让模型区分5.1还是7+，导致兼容性问题反复出现。此外，企业环境中的CLM（Constrained Language Mode）会阻止`Add-Type`、`class`、非白名单COM对象、.NET直接调用等，这些安全约束也需要在Prompt中明确。

## 核心内容

### 完整版系统Prompt（用于System Prompt/角色设定）

```
# PS5.1兼容代码生成系统提示词 v1.0
# 最后更新: 2026-07-31
# 适用目标: Windows PowerShell 5.1（.NET Framework 4.5+）
# 语法覆盖: 基于PowerShell 7.0-7.4差异清单
# 更新触发条件: PS7新版本发布/微软更新差异文档/发现新陷阱
# 更新检查URL: https://learn.microsoft.com/en-us/powershell/scripting/whats-new/differences-from-windows-powershell

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

### 精简版快速Prompt（用于单次对话快速约束）

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

### 场景变体

**变体A：脚本开发场景**（日常工具脚本）

在完整版基础上追加：
```
## 脚本开发场景附加要求
- 脚本开头包含完整的安全头（参考P-PS5-SAFEDEFAULTS-001模式）
- 提供param()块定义参数，添加[Parameter()]属性和类型约束
- 包含基于注释的帮助（.SYNOPSIS/.DESCRIPTION/.PARAMETER/.EXAMPLE）
```

**变体B：自动化/CI/CD场景**

在完整版基础上追加：
```
## 自动化/CI/CD场景附加要求
- 所有错误输出到stderr，使用$ErrorActionPreference = 'Stop'
- 退出码明确：成功exit 0，失败exit非0
- 不使用交互式提示（Read-Host等），所有参数通过命令行传递
- 日志输出包含时间戳："[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Message"
- CI中脚本调用方式：powershell -ExecutionPolicy Bypass -Scope Process -File script.ps1
- 不依赖用户profile，所有依赖在脚本内显式导入
```

**变体C：系统管理场景**（AD/IIS/注册表/CIM）

在完整版基础上追加：
```
## 系统管理场景附加要求
- 操作远程服务器前先Test-Connection或Test-WSMan检测连通性
- CIM调用显式创建CimSession并指定-Protocol WinRM
- 所有模块导入前先检测：if (-not (Get-Module -ListAvailable Xxx)) { throw "模块未安装" }
- 注册表操作使用原生cmdlet（Set-ItemProperty/New-ItemProperty）而非.NET Registry类
- 更改系统配置前先备份当前值，支持-WhatIf模拟
- 组策略环境检测ExecutionPolicy是否被锁定，不盲目执行Set-ExecutionPolicy
```

## 反模式（禁止做的事）

**反模式1：无版本提示直接让AI写PowerShell代码**
```
❌ 错误："帮我写一个PowerShell脚本备份文件"
（AI默认生成PS7+语法，PS5下ParserError）
```

**反模式2：黑名单不完整的提示词**
```
❌ 错误："不要用&&和||"
（只禁止了部分语法，仍会生成??/??=?:/?./-Parallel/class/Add-Type等）
```

**反模式3：使用"为PowerShell生成代码"模糊表述**
```
❌ 错误："为PowerShell生成兼容代码"
（"PowerShell"是模糊术语，AI无法区分5.1还是7+）
```

**反模式4：提示词中包含"使用最新语法"或"现代PowerShell"**
```
❌ 错误："使用现代PowerShell语法"
（直接引导AI使用PS7+新语法，100%在PS5下失败）
```

**反模式5：建议用户"Set-ExecutionPolicy Bypass -Scope LocalMachine"**
```
❌ 错误："执行Set-ExecutionPolicy Bypass让脚本可以运行"
（1. 全局Bypass严重弱化安全防线；2. 组策略锁定环境下无效且触发SOC告警）
```

## 迁移验证

### 验证步骤1：语法禁止项检测
```powershell
# 检测AI生成代码是否包含禁用PS7+语法（改进版，减少误报）
$ps7Patterns = @(
    @{ Pattern = '\?\?=?'; Name = '空合并/赋值运算符 ??/??=' },
    @{ Pattern = '(?<![?|%])&&(?!&)'; Name = '管道链运算符 &&' },
    @{ Pattern = '(?<![|])\|\|(?!\|)'; Name = '管道链运算符 ||' },
    @{ Pattern = '-Parallel\s'; Name = 'ForEach-Object -Parallel' },
    @{ Pattern = '(?<![?])\?\.(?!\?)'; Name = '空条件运算符 ?.' },
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

### 验证步骤2：PS5.1实际解析测试
```powershell
# 在PS5.1环境中进行解析测试（不执行）
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

### 验证步骤3：#Requires版本声明检查
```powershell
$content = Get-Content .\ai-generated-script.ps1 -Raw
if ($content -match '#Requires\s+-Version\s+5\.1') {
    Write-Host "✅ 包含#Requires -Version 5.1声明" -ForegroundColor Green
} else {
    Write-Host "⚠️  建议添加#Requires -Version 5.1" -ForegroundColor Yellow
}
```

## 配套模式

本模式与以下4个模式构成完整的"AI生成PS5安全兼容代码"工具链：
- [ps5-compat-preflight](../../code-patterns/ps5-compat-preflight.md)（P-PS5-PREFLIGHT-001）：生成后兼容性预检
- [ps5-security-audit](../../code-patterns/ps5-security-audit.md)（P-PS5-SECAUDIT-001）：安全代码审查
- [ps5-safe-defaults](../../code-patterns/ps5-safe-defaults.md)（P-PS5-SAFEDEFAULTS-001）：安全默认值头模板
- [ps7-to-ps5-translation](../../code-patterns/ps7-to-ps5-translation.md)（P-PS5-TRANSLATE-001）：PS7→PS5语法转换

---

*成熟度：L1（实验性，validation_count=1） | 首次验证：AI×PowerShell 5.1研究 2026-07-31*
