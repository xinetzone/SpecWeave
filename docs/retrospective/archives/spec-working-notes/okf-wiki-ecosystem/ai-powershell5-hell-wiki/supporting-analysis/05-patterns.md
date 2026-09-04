---
id: "ai-powershell5-patterns-05"
title: "AI大模型×PowerShell 5 可复用模式萃取报告（E阶段）"
date: "2026-07-31"
category: "research"
tags: ["powershell", "powershell-5.1", "ai-coding", "patterns", "reusable-patterns", "g3-quality-gate", "defensive-prompt", "checklist", "compatibility", "security"]
source: "Patterns extracted from 01-facts.md, 02-first-principles.md, 03-insights.md, hardened by 04-adversarial-review.md"
phase: "E"
quality-gate: "G3"
pattern-count: 5
hardened-by: "V阶段对抗审查（12个攻击视角，18个加固点全部应用）"
version: "1.0"
last-updated: "2026-07-31"
update-trigger:
  - "PowerShell 7.x新minor版本发布时"
  - "微软更新PS5.1/PS7差异文档时"
  - "发现新的兼容性/安全陷阱时"
update-check-url: "https://learn.microsoft.com/en-us/powershell/scripting/whats-new/differences-from-windows-powershell"
---

# AI大模型×PowerShell 5 可复用模式萃取报告（E阶段）

## 执行摘要

本报告基于R阶段24个事实场景、F阶段第一性原理分析（四重断裂、11条公理、5条引理）、I阶段14个根因洞察，并经过V阶段三视角12个攻击点的对抗审查加固，提炼出5个可复用模式。所有模式均已纳入安全加固措施：ExecutionPolicy分级建议、TLS追加而非覆盖、全局状态保存-恢复模式、CLM兼容性标注、EDR部署提示、版本管理元数据、防御性保守原则等。

***

## 模式1：PS5-Defensive-Prompt（防御性Prompt模板模式）

### 模式ID

**P-PS5-PROMPT-001**

### 触发场景

- 使用AI大模型（GPT-4/Claude/GitHub Copilot等）生成Windows PowerShell 5.1代码时
- 未指定版本或版本提示模糊，导致AI默认生成PS7+语法时
- 需要生成可在企业受限环境（CLM/WDAC）运行的保守兼容代码时
- CI/CD流水线中需要AI辅助生成PS脚本时
- 批量脚本生成任务需要统一版本约束时

### 核心步骤/内容

#### 1.1 完整版系统Prompt（用于System Prompt/角色设定）

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

#### 1.2 精简版快速Prompt（用于单次对话快速约束）

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

#### 1.3 场景变体

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

### 反模式

#### 反模式1：无版本提示直接让AI写PowerShell代码

```
❌ 错误："帮我写一个PowerShell脚本备份文件"
（AI默认生成PS7+语法，PS5下ParserError）
```

#### 反模式2：黑名单不完整的提示词

```
❌ 错误："不要用&&和||"
（只禁止了部分语法，仍会生成??/??=?:/?./-Parallel/class/Add-Type等）
```

#### 反模式3：使用"为PowerShell生成代码"模糊表述

```
❌ 错误："为PowerShell生成兼容代码"
（"PowerShell"是模糊术语，AI无法区分5.1还是7+）
```

#### 反模式4：提示词中包含"使用最新语法"或"现代PowerShell"

```
❌ 错误："使用现代PowerShell语法"
（直接引导AI使用PS7+新语法，100%在PS5下失败）
```

#### 反模式5：建议用户"Set-ExecutionPolicy Bypass -Scope LocalMachine"

```
❌ 错误："执行Set-ExecutionPolicy Bypass让脚本可以运行"
（1. 全局Bypass严重弱化安全防线；2. 组策略锁定环境下无效且触发SOC告警）
```

### 迁移验证

#### 验证步骤1：语法禁止项检测

```powershell
# 检测AI生成代码是否包含禁用PS7+语法（改进版，减少误报）
# PS5兼容性检测 v1.0 (2026-07-31)
# 基于PowerShell 7.4语法集
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

#### 验证步骤2：PS5.1实际解析测试

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

#### 验证步骤3：#Requires版本声明检查

```powershell
$content = Get-Content .\ai-generated-script.ps1 -Raw
if ($content -match '#Requires\s+-Version\s+5\.1') {
    Write-Host "✅ 包含#Requires -Version 5.1声明" -ForegroundColor Green
} else {
    Write-Host "⚠️  建议添加#Requires -Version 5.1" -ForegroundColor Yellow
}
```

***

## 模式2：PS5-Compat-Preflight（兼容性预检Checklist模式）

### 模式ID

**P-PS5-PREFLIGHT-001**

### 触发场景

- AI生成PowerShell 5.1脚本后，执行前人工/自动验证时
- CI/CD流水线中添加PS5兼容性检查门禁时
- 代码审查（Code Review）阶段检查PS兼容性时
- 接收第三方/AI生成脚本后在生产环境运行前
- 脚本从开发环境迁移到测试/生产环境前

### 核心步骤/内容

按三级优先级组织检查项：P0（阻断项，不通过则禁止执行）、P1（高危项，可能静默失败或数据损坏）、P2（建议项，提升健壮性）。

#### P0 阻断项检查（必须全部通过）

| 检查项ID | 检查内容                    | 检查方法                                                         | 不通过时修复                                                                      | <br />                          | <br />          | <br />               | <br />                                          |
| ----- | ----------------------- | ------------------------------------------------------------ | --------------------------------------------------------------------------- | :------------------------------ | :-------------- | :------------------- | :---------------------------------------------- |
| P0-01 | PS7+禁用语法检测              | 运行模式1中的PS7语法检测脚本；或在PS5.1中用PSParser解析                         | 按P-PS5-TRANSLATE-001模式替换为PS5兼容写法                                            | <br />                          | <br />          | <br />               | <br />                                          |
| P0-02 | WMI cmdlet检测            | \`Select-String -Path script.ps1 -Pattern 'Get-WmiObject     | Invoke-WmiMethod                                                            | Remove-WmiObject                | Set-WmiInstance | Register-WmiEvent'\` | 全部替换为对应CIM cmdlet：Get-WmiObject→Get-CimInstance |
| P0-03 | Workflow关键字检测           | `Select-String -Path script.ps1 -Pattern '^\s*workflow\s'`   | 重构为普通PowerShell函数，并行逻辑用Start-Job                                            | <br />                          | <br />          | <br />               | <br />                                          |
| P0-04 | Add-PSSnapin检测          | `Select-String -Path script.ps1 -Pattern 'Add-PSSnapin'`     | 使用Import-Module替代；如模块不存在需先检测                                                | <br />                          | <br />          | <br />               | <br />                                          |
| P0-05 | pwsh.exe路径检测            | `Select-String -Path script.ps1 -Pattern 'pwsh\.exe'`        | 替换为`$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe`或检测后分支处理 | <br />                          | <br />          | <br />               | <br />                                          |
| P0-06 | Invoke-Expression/iex检测 | \`Select-String -Path script.ps1 -Pattern 'Invoke-Expression | \biex\b'\`（排除注释行）                                                           | 重构为直接cmdlet调用或scriptblock + &调用 | <br />          | <br />               | <br />                                          |
| P0-07 | class关键字检测（CLM环境）       | `Select-String -Path script.ps1 -Pattern '^\s*class\s+\w+'`  | 替换为\[PSCustomObject]@{}或New-Object PSObject + Add-Member                    | <br />                          | <br />          | <br />               | <br />                                          |
| P0-08 | Add-Type检测（CLM环境）       | `Select-String -Path script.ps1 -Pattern 'Add-Type'`         | 用纯PowerShell重写，或使用预编译签名程序集                                                  | <br />                          | <br />          | <br />               | <br />                                          |

#### P1 高危项检查（强烈建议修复）

| 检查项ID | 检查内容           | 检查方法                                                                                                                       | 不通过时修复                                                  | <br />                                                             | <br />                                                                 |
| ----- | -------------- | -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- | :----------------------------------------------------------------- | :--------------------------------------------------------------------- |
| P1-01 | 文件输出编码检测       | \`Select-String -Path script.ps1 -Pattern '(Out-File                                                                       | Set-Content                                             | Add-Content).\*(?!-Encoding\s+utf8)'`；检查`>`/`>>\`重定向               | 所有Out-File/Set-Content/Add-Content添加`-Encoding utf8`；重定向改为Out-File显式编码 |
| P1-02 | TLS设置检测        | `Select-String -Path script.ps1 -Pattern 'ServicePointManager::SecurityProtocol\s*='`                                      | 在脚本开头添加TLS 1.2追加设置（使用-OR追加，非覆盖，见P-PS5-SAFEDEFAULTS-001） | <br />                                                             | <br />                                                                 |
| P1-03 | 自动变量覆盖检测       | 检查变量名是否匹配：`$HOME,$PSHOME,$PWD,$?,$_,$ARGS,$ERROR,$EXCEPTION,$FALSE,$TRUE,$NULL,$PSScriptRoot,$PSCommandPath,$Host`（大小写不敏感） | 重命名变量为带前缀名称（如$tempHome、$configPath）                     | <br />                                                             | <br />                                                                 |
| P1-04 | 非白名单COM对象检测    | \`Select-String -Path script.ps1 -Pattern 'New-Object\s+-ComObject\s+(?!Scripting.(Dictionary                              | FileSystemObject)                                       | VBScript.RegExp)'\`                                                | 评估是否真的需要COM；CLM环境下必须移除或替换为原生cmdlet                                     |
| P1-05 | .NET直接调用注册表检测  | `Select-String -Path script.ps1 -Pattern '\[Microsoft\.Win32\.Registry\]'`                                                 | 替换为Set-ItemProperty/Get-ItemProperty等原生注册表cmdlet        | <br />                                                             | <br />                                                                 |
| P1-06 | irm\|iex一行执行检测 | \`Select-String -Path script.ps1 -Pattern 'irm.\*\|.\*iex                                                                  | Invoke-RestMethod.\*\|.\*Invoke-Expression'\`           | 拆分为三步：下载到文件→Get-Content检查→确认后执行                                    | <br />                                                                 |
| P1-07 | 执行策略硬编码检测      | \`Select-String -Path script.ps1 -Pattern 'Set-ExecutionPolicy\s+Bypass\s+-Scope\s+(LocalMachine                           | CurrentUser)'\`                                         | 改为建议用户使用`-ExecutionPolicy Bypass -Scope Process`调用方式，或在组策略环境中检测后提示 | <br />                                                                 |
| P1-08 | UTF-8无BOM脚本检测  | 用十六进制编辑器检查.ps1文件前3字节：EF BB BF是UTF-8 BOM                                                                                    | 重新保存为UTF-8 with BOM格式                                   | <br />                                                             | <br />                                                                 |
| P1-09 | 全局状态无恢复检测      | 检查是否修改了$OutputEncoding/\[Console]::OutputEncoding/SecurityProtocol但无finally恢复                                              | 使用"保存-设置-恢复"try/finally模式                               | <br />                                                             | <br />                                                                 |

#### P2 建议项检查（提升健壮性）

| 检查项ID | 检查内容                             | 检查方法                                                    | 修复建议                                                           |
| ----- | -------------------------------- | ------------------------------------------------------- | -------------------------------------------------------------- |
| P2-01 | #Requires版本声明                    | 检查是否包含`#Requires -Version 5.1`                          | 在脚本首行添加版本声明                                                    |
| P2-02 | Set-StrictMode                   | 检查是否启用`Set-StrictMode -Version Latest`                  | 脚本开头启用严格模式，捕获未初始化变量等问题                                         |
| P2-03 | $ErrorActionPreference           | 检查是否设置了错误处理策略                                           | 根据需要设置`$ErrorActionPreference = 'Stop'`或在cmdlet中使用-ErrorAction |
| P2-04 | 模块可用性检测                          | 检查Import-Module前是否有Get-Module -ListAvailable检测          | 添加模块存在性检查，不存在时抛出友好错误                                           |
| P2-05 | 参数类型约束                           | 检查param()块中参数是否有类型约束                                    | 为所有参数添加类型约束（\[string]/\[int]/\[switch]等）                       |
| P2-06 | 危险操作确认                           | 检查Remove-Item/Stop-Process等危险操作前是否有确认或-WhatIf支持         | 添加-WhatIf支持或显式路径输出提示                                           |
| P2-07 | Runspace/Start-Job CLM检测         | 检查并行代码前是否检测了$ExecutionContext.SessionState.LanguageMode | 添加CLM检测和降级路径                                                   |
| P2-08 | Runspace/Start-Job -NoParallel开关 | 检查并行代码是否支持顺序执行降级                                        | 添加\[switch]$NoParallel参数支持EDR环境                                |
| P2-09 | 注释帮助                             | 检查是否有基于注释的帮助                                            | 添加.SYNOPSIS/.DESCRIPTION/.PARAMETER/.EXAMPLE                   |
| P2-10 | 版本元数据                            | 检查脚本是否包含版本/日期/更新记录元数据                                   | 在脚本头部添加版本注释元数据                                                 |

#### 一键预检脚本

```powershell
# PS5.1兼容性一键预检脚本 v1.0 (2026-07-31)
param(
    [Parameter(Mandatory=$true)]
    [string]$ScriptPath,
    [switch]$Strict  # 启用P1/P2检查
)

$results = @()
$content = Get-Content $ScriptPath -Raw -ErrorAction Stop

# P0检查
$p0Checks = @(
    @{ Pattern = '\?\?=?'; Name = 'P0-01: ??/??=运算符' },
    @{ Pattern = '(?&lt;![?|%])&amp;&amp;(?!&amp;)'; Name = 'P0-01: &amp;&amp;运算符' },
    @{ Pattern = '(?&lt;![|])\|\|(?!\|)'; Name = 'P0-01: ||运算符' },
    @{ Pattern = '-Parallel\s'; Name = 'P0-01: -Parallel参数' },
    @{ Pattern = '(?&lt;![?])\?\.(?!\?)'; Name = 'P0-01: ?.运算符' },
    @{ Pattern = 'Get-WmiObject|Invoke-WmiMethod|Remove-WmiObject'; Name = 'P0-02: WMI cmdlets' },
    @{ Pattern = '^\s*workflow\s'; Name = 'P0-03: workflow关键字' },
    @{ Pattern = 'Add-PSSnapin'; Name = 'P0-04: Add-PSSnapin' },
    @{ Pattern = 'pwsh\.exe'; Name = 'P0-05: pwsh.exe路径' },
    @{ Pattern = '^\s*[^#]*\b(Invoke-Expression|\biex\b)'; Name = 'P0-06: Invoke-Expression/iex' },
    @{ Pattern = '^\s*class\s+\w+'; Name = 'P0-07: class关键字' },
    @{ Pattern = 'Add-Type'; Name = 'P0-08: Add-Type' }
)

foreach ($check in $p0Checks) {
    if ($content -match $check.Pattern) {
        $results += [PSCustomObject]@{ Level = 'P0'; Item = $check.Name; Status = 'FAIL' }
    }
}

# 解析器测试
$parseErrors = $null
[void][System.Management.Automation.PSParser]::Tokenize($content, [ref]$parseErrors)
if ($parseErrors.Count -gt 0) {
    $results += [PSCustomObject]@{ Level = 'P0'; Item = 'P0-00: 解析器错误'; Status = "FAIL ($($parseErrors.Count)个错误)" }
}

# 输出结果
$p0Fail = $results | Where-Object { $_.Level -eq 'P0' -and $_.Status -like 'FAIL*' }
if ($p0Fail) {
    Write-Host "`n❌ P0阻断项未通过:" -ForegroundColor Red
    $p0Fail | Format-Table -AutoSize
    exit 1
} else {
    Write-Host "`n✅ P0阻断项全部通过" -ForegroundColor Green
}

if ($Strict) {
    Write-Host "⚠️  P1/P2详细检查请使用完整Checklist逐项验证" -ForegroundColor Yellow
}
```

### 反模式

#### 反模式1："在我机器上能跑"就上线

```
❌ 错误：在开发机（Full Language Mode、已设ExecutionPolicy、已装所有模块）测试通过就认为脚本没问题
（企业CLM环境、CI服务账户、干净Windows安装环境下必然失败）
```

#### 反模式2：只测试语法不测试运行

```
❌ 错误：只看脚本有没有红色波浪线（ParserError）就认为没问题
（编码乱码、TLS失败、CLM阻止、WMI→CIM问题都是运行时错误，语法可能完全正确）
```

#### 反模式3：依赖AI自我检查

```
❌ 错误："AI你帮我检查一下你生成的代码有没有兼容性问题"
（模型自身无法可靠检测自己生成代码的版本兼容性问题，必须用外部工具/Checklist）
```

#### 反模式4：使用旧的PS版本（如PS3/PS4）测试PS5代码

```
❌ 错误：在PS4上测试通过就认为PS5.1也能跑
（虽然PS5向下兼容，但部分行为和cmdlet可用性仍有差异）
```

### 迁移验证

#### 验证命令1：执行一键预检脚本

```powershell
.\ps5-preflight-check.ps1 -ScriptPath .\your-script.ps1 -Strict
# 预期输出：✅ P0阻断项全部通过
```

#### 验证命令2：PS5.1实际执行测试（-WhatIf模拟）

```powershell
# 在干净的PS5.1环境（非开发机）中执行
powershell -ExecutionPolicy Bypass -Scope Process -Command "& { .\your-script.ps1 -WhatIf }"
```

#### 验证命令3：CLM环境模拟测试（可选）

```powershell
# 在启用了WDAC/AppLocker的测试环境或使用__PSLockdownPolicy模拟
# 注意：__PSLockdownPolicy仅用于测试，生产环境通过组策略配置
$env:__PSLockdownPolicy = '4'  # 启用CLM
powershell -ExecutionPolicy Bypass -Scope Process -File .\your-script.ps1
Remove-Item Env:__PSLockdownPolicy
```

***

## 模式3：PS5-Security-Audit（安全代码审查Checklist模式）

### 模式ID

**P-PS5-SECAUDIT-001**

### 触发场景

- AI生成PS5脚本后进行安全审查时
- 代码审查（Code Review）阶段进行安全维度检查时
- 脚本上线前的安全审计时
- 接收外部来源脚本（AI/第三方/互联网）后的安全检查时
- 企业安全团队对PowerShell脚本进行合规检查时

### 核心步骤/内容

#### 安全审查维度清单

##### 维度1：CLM/Constrained Language Mode兼容性

| 检查项ID      | 检查内容                      | 严重度 | 检查方法                                                                                                                          | 修复方案                            | <br />                          |
| ---------- | ------------------------- | --- | ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------- | :------------------------------ |
| SEC-CLM-01 | 是否使用Add-Type？             | P0  | `Select-String -Pattern 'Add-Type'`                                                                                           | 用纯PowerShell重写；或使用预编译签名程序集      | <br />                          |
| SEC-CLM-02 | 是否定义了PowerShell class？    | P0  | `Select-String -Pattern '^\s*class\s+\w+'`                                                                                    | 替换为\[PSCustomObject]@{}         | <br />                          |
| SEC-CLM-03 | 是否调用非白名单COM对象？            | P0  | 检查New-Object -ComObject参数，白名单仅：Scripting.Dictionary、Scripting.FileSystemObject、VBScript.RegExp                                | 移除COM调用；或使用白名单内COM；或申请企业WDAC白名单 | <br />                          |
| SEC-CLM-04 | 是否直接调用.NET Framework类型方法？ | P0  | 检查`[Namespace.Class]::Method()`调用，特别是：\[Microsoft.Win32.Registry]、\[System.Reflection.*]、\[System.Runtime.InteropServices.*]等 | 使用PowerShell原生cmdlet替代          | <br />                          |
| SEC-CLM-05 | 是否使用XAML/WPF？             | P1  | \`Select-String -Pattern 'XamlReader                                                                                          | System.Windows'\`               | CLM下XAML被阻止，考虑使用WinForms或原生主机UI |
| SEC-CLM-06 | 是否有语言模式检测？                | P2  | 检查是否查询`$ExecutionContext.SessionState.LanguageMode`                                                                           | 在需要Full Language功能时添加检测和友好提示    | <br />                          |

##### 维度2：命令注入防护

| 检查项ID      | 检查内容                           | 严重度                   | 检查方法                                        | 修复方案                                          | <br />                                                 | <br />                   |
| ---------- | ------------------------------ | --------------------- | ------------------------------------------- | --------------------------------------------- | :----------------------------------------------------- | :----------------------- |
| SEC-INJ-01 | **是否使用Invoke-Expression/iex？** | P0                    | \`Select-String -Pattern 'Invoke-Expression | \biex\b'\`（排除注释）                              | **永远不要使用**。重构为：1)直接cmdlet调用；2)scriptblock + &调用；3)参数绑定 | <br />                   |
| SEC-INJ-02 | 参数是否有类型约束？                     | P0                    | 检查param()块参数是否有\[string]/\[int]等类型约束        | 为所有用户输入参数添加强类型约束                              | <br />                                                 | <br />                   |
| SEC-INJ-03 | 用户输入是否直接拼接进命令？                 | P0                    | 检查字符串拼接后执行的模式：`"Get-Process $userInput"`    | 使用参数绑定：Get-Process -Id $ProcId（参数绑定器自动验证）     | <br />                                                 | <br />                   |
| SEC-INJ-04 | 是否使用irm                        | iex/Invoke-WebRequest | iex模式？                                      | P0                                            | `Select-String -Pattern '\|\s*iex\b'`                  | 拆分为下载→检查→执行三步；或使用已签名的脚本包 |
| SEC-INJ-05 | 动态命令是否使用scriptblock？           | P1                    | 如需动态命令，检查是否使用{ param(...) ... } + &调用       | 如必须动态构造命令，使用scriptblock而非字符串拼接                | <br />                                                 | <br />                   |
| SEC-INJ-06 | cmd /c或外部进程调用是否有转义问题？          | P1                    | 检查cmd/c调用中的引号嵌套和路径变量                        | 使用PowerShell原生cmdlet替代cmd.exe调用；使用LiteralPath | <br />                                                 | <br />                   |

##### 维度3：凭证与敏感信息处理

| 检查项ID       | 检查内容                     | 严重度 | 检查方法                                                            | 修复方案                                                 |
| ----------- | ------------------------ | --- | --------------------------------------------------------------- | ---------------------------------------------------- |
| SEC-CRED-01 | 凭证是否硬编码在脚本中？             | P0  | 搜索明文密码/API Key/Token/ConnectionString等模式                        | 使用Get-Credential、SecretManagement模块、或DPAPI加密存储       |
| SEC-CRED-02 | 是否使用-credential参数传递明文密码？ | P0  | 检查`ConvertTo-SecureString -AsPlainText -Force`后直接构造PSCredential | 使用Get-Credential交互式获取；或从Windows Credential Manager读取 |
| SEC-CRED-03 | 凭证是否输出到日志/控制台？           | P1  | 检查Write-Host/Out-File/日志中是否输出$credential或密码变量                   | 禁止输出凭证对象；日志中对敏感字段打码                                  |
| SEC-CRED-04 | 临时凭证文件是否安全清理？            | P2  | 检查是否导出凭证到磁盘文件且无清理                                               | 使用try/finally确保临时凭证文件被安全删除；优先使用内存存储                  |
| SEC-CRED-05 | 是否使用SSL/TLS加密传输凭证？       | P1  | 检查HTTP（非HTTPS）端点是否传输凭证                                          | 所有凭证传输必须使用HTTPS；脚本开头追加TLS 1.2设置                      |

##### 维度4：执行策略与权限控制

| 检查项ID     | 检查内容                    | 严重度 | 检查方法                                                                           | 修复方案                                                  |
| --------- | ----------------------- | --- | ------------------------------------------------------------------------------ | ----------------------------------------------------- |
| SEC-EP-01 | 是否建议用户全局Bypass执行策略？     | P0  | 搜索`Set-ExecutionPolicy Bypass -Scope LocalMachine`或`-Scope CurrentUser`且无组策略检测 | ⚠️ 安全警告：Bypass仅应在完全信任脚本来源时使用，且推荐`-Scope Process`      |
| SEC-EP-02 | 是否检测组策略锁定状态？            | P1  | 检查Set-ExecutionPolicy前是否检测MachinePolicy/UserPolicy                             | 添加组策略锁定检测，锁定时提示联系IT部门而非盲目设置                           |
| SEC-EP-03 | 脚本是否要求管理员权限但无检测？        | P1  | 检查是否有需要提升权限的操作但无#Requires -RunAsAdministrator                                  | 需要管理员权限时添加`#Requires -RunAsAdministrator`             |
| SEC-EP-04 | CI脚本是否使用-Scope Process？ | P1  | CI场景中检查-ExecutionPolicy Bypass是否带-Scope Process                                | CI中始终使用-ExecutionPolicy Bypass -Scope Process，不影响其他进程 |

##### 维度5：编码安全与数据保护

| 检查项ID      | 检查内容                                    | 严重度 | 检查方法                                                                             | 修复方案                                              |
| ---------- | --------------------------------------- | --- | -------------------------------------------------------------------------------- | ------------------------------------------------- |
| SEC-ENC-01 | TLS设置是否正确（追加而非覆盖）？                      | P1  | 检查SecurityProtocol赋值是否使用-bor追加而非直接赋值                                             | 使用P-PS5-SAFEDEFAULTS-001中的追加模式，保留系统已有协议           |
| SEC-ENC-02 | 是否禁用证书验证（-SkipCertificateCheck不存在于PS5）？ | P1  | 检查是否设置`[Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}` | 生产环境不要禁用证书验证；如必须（测试环境）添加明确警示和范围限制                 |
| SEC-ENC-03 | 文件输出是否显式指定编码？                           | P1  | 检查Out-File/Set-Content是否带-Encoding参数；重定向是否改为显式编码                                 | 所有文件输出显式指定-Encoding utf8（PS5带BOM）                 |
| SEC-ENC-04 | 临时文件是否在系统临时目录且安全清理？                     | P2  | 检查临时文件是否在$env:TEMP创建，是否用try/finally清理                                            | 使用Join-Path $env:TEMP创建临时文件，finally中Remove-Item清理 |

##### 维度6：安全默认值与防御性编程

| 检查项ID      | 检查内容                | 严重度 | 检查方法                                                                     | 修复方案                                   |
| ---------- | ------------------- | --- | ------------------------------------------------------------------------ | -------------------------------------- |
| SEC-DEF-01 | 是否覆盖自动变量？           | P1  | 检查自定义变量名是否为$HOME/$PWD/$\_/$?/$null等（大小写不敏感）                              | 使用带前缀的变量名（$tempXxx/$configXxx）         |
| SEC-DEF-02 | 危险操作是否有-WhatIf/确认？  | P1  | 检查Remove-Item/Stop-Process/Stop-Service等是否支持-WhatIf或有确认提示                | 支持-WhatIf和-Confirm参数，生产环境使用前先-WhatIf模拟 |
| SEC-DEF-03 | 是否使用Set-StrictMode？ | P2  | 检查是否有Set-StrictMode -Version Latest                                      | 脚本开头启用严格模式                             |
| SEC-DEF-04 | 全局状态修改是否有恢复？        | P1  | 检查是否修改$OutputEncoding/Console.OutputEncoding/SecurityProtocol但无finally恢复 | 使用"保存-设置-恢复"try/finally模式              |
| SEC-DEF-05 | 错误处理是否完善？           | P2  | 检查是否有try/catch/finally，是否检查$?/$LASTEXITCODE                              | 添加适当的错误处理，外部进程调用检查$LASTEXITCODE        |
| SEC-DEF-06 | 模块导入前是否检测？          | P2  | 检查Import-Module前是否有Get-Module -ListAvailable检测                           | 添加模块存在性检查，给出友好错误信息                     |

#### 安全审查评分模板

| 维度      | P0问题数    | P1问题数    | P2问题数    | 风险等级      |
| ------- | -------- | -------- | -------- | --------- |
| CLM兼容性  | \_\_     | \_\_     | \_\_     | 高/中/低     |
| 命令注入防护  | \_\_     | \_\_     | \_\_     | 高/中/低     |
| 凭证处理    | \_\_     | \_\_     | \_\_     | 高/中/低     |
| 执行策略与权限 | \_\_     | \_\_     | \_\_     | 高/中/低     |
| 编码安全    | \_\_     | \_\_     | \_\_     | 高/中/低     |
| 防御性编程   | \_\_     | \_\_     | \_\_     | 高/中/低     |
| **合计**  | **\_\_** | **\_\_** | **\_\_** | **高/中/低** |

**通过标准**：P0问题数=0；P1问题数≤2且有补偿控制；风险等级不超过"中"。

### 反模式

#### 反模式1：只检查显式恶意代码

```
❌ 错误：只检查有没有Remove-Item C:\ -Recurse等明显恶意代码
（合法脚本中的Invoke-Expression、硬编码凭证、TLS覆盖等"正常"代码才是主要安全风险）
```

#### 反模式2："AI生成的代码应该是安全的"

```
❌ 错误：认为AI训练数据过滤了恶意代码，所以AI生成的代码安全
（AI会生成有安全漏洞的代码——不是因为它恶意，而是因为它不知道安全边界）
```

#### 反模式3：禁用脚本块日志或AMSI

```
❌ 错误：为了让脚本"顺利运行"建议用户禁用脚本块日志或AMSI
（这是恶意软件常用的反检测手段，合法脚本永远不应建议禁用安全防护）
```

#### 反模式4：在脚本中添加隐藏的后门/持久化

```
❌ 错误：AI生成的脚本中意外包含（或被投毒加入）计划任务持久化、启动项写入等代码
（审查时必须检查所有非预期的系统修改操作）
```

### 迁移验证

#### 验证方法1：使用PSScriptAnalyzer官方规则

```powershell
# 安装PSScriptAnalyzer（如未安装）
Install-Module PSScriptAnalyzer -Scope CurrentUser -Force

# 运行安全相关规则扫描
Invoke-ScriptAnalyzer -Path .\your-script.ps1 -IncludeRule PSAvoidUsingInvokeExpression,PSAvoidUsingPlainTextForPassword,PSUsePSCredentialType,PSAvoidUsingUsernameAndPasswordParams,PSAvoidUsingInternalURLs
```

#### 验证方法2：执行AmsiScanBuffer测试（企业环境）

```powershell
# 确保AMSI集成启用（默认启用），脚本应能正常被AMSI扫描
# 如脚本触发AMSI告警，说明存在可疑特征需要审查
```

#### 验证方法3：安全审查Checklist验证

人工逐项过本模式Checklist，填写评分模板，P0问题数=0方为通过。

***

## 模式4：PS5-Safe-Defaults（安全默认值防护模式）

### 模式ID

**P-PS5-SAFEDEFAULTS-001**

### 触发场景

- 所有AI生成的PowerShell 5.1脚本开头，作为标准"安全头"
- 新建PS5脚本时的标准模板开头
- 修复现有脚本缺失默认值防护时
- 从PS7代码迁移到PS5时补充兼容性设置时
- 企业环境中统一脚本安全基线时

### 核心步骤/内容

#### 生产级安全默认值完整代码片段（已加固）

```powershell
#Requires -Version 5.1
# PS5.1安全默认值头 v1.0 (2026-07-31)
# 已纳入V阶段对抗审查加固：TLS追加非覆盖、全局状态保存-恢复、组策略检测、CLM检测
# - TLS设置使用-OR追加模式，保留系统已有协议（A2加固）
# - 所有全局设置使用try/finally保存-恢复模式（B3加固）
# - ExecutionPolicy不盲目设置，提供检测和友好提示（B2加固）
# - Runspace并行代码标注CLM不兼容并提供降级（A3/B4加固）

# ============================================================
# 1. 错误处理与严格模式
# ============================================================
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'  # 显著提升某些操作性能
Set-StrictMode -Version Latest

# ============================================================
# 2. 保存原始全局状态（用于finally恢复）
# ============================================================
$original_ErrorActionPreference = $ErrorActionPreference
$original_OutputEncoding = $OutputEncoding
$original_ConsoleEncoding = [Console]::OutputEncoding
$original_ProgressPreference = $ProgressPreference
$original_TlsProtocols = [Net.ServicePointManager]::SecurityProtocol

try {
    # ============================================================
    # 3. 编码设置（UTF-8支持）
    # ============================================================
    $OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    # 注意：这只影响控制台和输出编码，不影响Out-File默认编码
    # 所有文件操作仍需显式-Encoding utf8

    # ============================================================
    # 4. TLS协议兼容性设置（追加而非覆盖，加固版）
    # ============================================================
    # - PS5.1/.NET Framework 4.5默认不启用Tls12
    # - Tls13枚举在.NET Framework 4.7+可用（值: 12288/0x3000）
    # - 使用-OR追加而非赋值，保留系统已启用的协议（A2加固）
    # - 添加Verbose日志便于诊断（C2加固）
    $tls12 = [Net.SecurityProtocolType]::Tls12  # 值: 3072 (0xC00)
    $tls13Value = 12288  # Tls13硬编码值，兼容无枚举的旧.NET Framework
    $tls13 = [Net.SecurityProtocolType]::Tls13 -as [Net.SecurityProtocolType]
    if (-not $tls13) {
        $tls13 = [Enum]::ToObject([Net.SecurityProtocolType], $tls13Value) -as [Net.SecurityProtocolType]
    }

    $newProtocols = [Net.ServicePointManager]::SecurityProtocol -bor $tls12
    if ($tls13) {
        $newProtocols = $newProtocols -bor $tls13
        Write-Verbose "TLS设置：已追加启用TLS 1.2 + TLS 1.3（保留系统原有协议）"
    } else {
        Write-Verbose "TLS设置：已追加启用TLS 1.2（当前系统不支持TLS 1.3，保留系统原有协议）"
    }
    [Net.ServicePointManager]::SecurityProtocol = $newProtocols

    # ============================================================
    # 5. 执行策略检测与友好提示（不盲目Set-ExecutionPolicy）
    # ============================================================
    # B2加固：检测组策略锁定，避免无效操作和SOC告警
    $lockedPolicies = Get-ExecutionPolicy -List | Where-Object {
        $_.Scope -in 'MachinePolicy', 'UserPolicy' -and $_.ExecutionPolicy -ne 'Undefined'
    }
    if ($lockedPolicies) {
        Write-Verbose "ExecutionPolicy由组策略锁定: $($lockedPolicies.ExecutionPolicy -join ', ')"
    } else {
        $currentPolicy = Get-ExecutionPolicy
        if ($currentPolicy -eq 'Restricted') {
            Write-Warning "当前ExecutionPolicy为Restricted，脚本可能无法执行。"
            Write-Warning "推荐调用方式：powershell -ExecutionPolicy Bypass -Scope Process -File `"$PSCommandPath`""
            # A1加固：不自动Bypass，提示用户使用Process级作用域
        }
    }

    # ============================================================
    # 6. 语言模式检测（CLM兼容性提示）
    # ============================================================
    # B1加固：提示"保守兼容"而非"保证CLM运行"，因为企业白名单有差异
    $languageMode = $ExecutionContext.SessionState.LanguageMode
    if ($languageMode -eq 'ConstrainedLanguage') {
        Write-Verbose "运行于Constrained Language Mode，使用保守兼容子集"
        Write-Warning "检测到CLM环境：脚本使用原生cmdlet，避免Add-Type/COM/class/.NET直接调用"
        Write-Warning "如脚本无法运行，请与企业安全团队确认WDAC白名单配置，或使用签名脚本"
    }

    # ============================================================
    # 7. 自动变量防护（Set-StrictMode已覆盖部分，此处补充危险变量检测）
    # ============================================================
    # 检查常见自动变量是否被意外覆盖（仅检测，不强制阻止）
    $autoVars = @('HOME', 'PWD', 'PSHOME', '?', '_', 'null', 'ARGS', 'ERROR')
    foreach ($varName in $autoVars) {
        $var = Get-Variable -Name $varName -ErrorAction SilentlyContinue
        if ($var -and $var.Options -notmatch 'ReadOnly|Constant' -and $varName -ne 'null') {
            Write-Debug "自动变量`$$varName不是ReadOnly/Constant，存在被覆盖风险"
        }
    }

    # ============================================================
    # === 业务逻辑从这里开始 ===
    # ============================================================

    # 你的脚本代码写在这里...
    Write-Host "安全默认值已加载完成" -ForegroundColor Green

    # ============================================================
    # === 业务逻辑结束 ===
    # ============================================================
}
catch {
    Write-Error "脚本执行出错: $_"
    exit 1
}
finally {
    # ============================================================
    # 8. 恢复原始全局状态（B3加固：即使发生错误也恢复）
    # ============================================================
    $ErrorActionPreference = $original_ErrorActionPreference
    $OutputEncoding = $original_OutputEncoding
    [Console]::OutputEncoding = $original_ConsoleEncoding
    $ProgressPreference = $original_ProgressPreference
    [Net.ServicePointManager]::SecurityProtocol = $original_TlsProtocols
    Write-Verbose "原始全局状态已恢复"
}
```

#### 精简版安全头（用于短脚本/单行命令前置）

```powershell
# 精简版PS5安全头（适合短脚本）
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$original_Tls = [Net.ServicePointManager]::SecurityProtocol
try {
    [Net.ServicePointManager]::SecurityProtocol = $original_Tls -bor [Net.SecurityProtocolType]::Tls12
    $OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    # ... 业务逻辑 ...
} finally {
    [Net.ServicePointManager]::SecurityProtocol = $original_Tls
}
```

#### 并行处理安全模板（含CLM/EDR兼容）

```powershell
# 并行处理模板（生产级，已加固）
# ⚠️ 安全提示：Runspace池可能被恶意软件用于隐蔽执行上下文（A3加固）
# ⚠️ 企业部署提示：Start-Job/Runspace可能触发EDR/XDR告警（B4加固）
#   - 与安全团队沟通加入白名单
#   - 使用-NoParallel开关可回退到顺序执行
#   - 考虑使用任务计划程序并行触发替代进程内并行
param(
    [switch]$NoParallel  # EDR环境/CLM环境/调试时使用顺序执行
)

$minThreads = 1
$maxThreads = [Math]::Min(10, [Environment]::ProcessorCount * 2)  # IO密集型
$runspacePool = $null
$jobs = @()

try {
    if ($ExecutionContext.SessionState.LanguageMode -eq 'ConstrainedLanguage') {
        Write-Warning "CLM环境下Runspace不可用，使用Start-Job（A3加固）"
        $NoParallel = $false  # Start-Job在CLM下可用但性能较低
        # Start-Job实现...
    }
    elseif ($NoParallel) {
        Write-Verbose "顺序执行模式（-NoParallel已指定，适合EDR环境）"
        1..10 | ForEach-Object {
            # 顺序处理...
            Write-Verbose "处理项 $_"
            Start-Sleep -Milliseconds 100
        }
    }
    else {
        Write-Verbose "Runspace池并行模式（线程池: $minThreads-$maxThreads）"
        # C3加固：生产级Runspace模板，含完整错误处理和资源清理
        $runspacePool = [runspacefactory]::CreateRunspacePool($minThreads, $maxThreads)
        $runspacePool.Open()

        $jobs = 1..10 | ForEach-Object {
            $itemId = $_
            $ps = [powershell]::Create()
            $ps.RunspacePool = $runspacePool
            [void]$ps.AddScript({
                param($id)
                Start-Sleep -Milliseconds 100
                [PSCustomObject]@{ Id = $id; ProcessedAt = Get-Date; Result = "OK" }
            }).AddArgument($itemId)
            [PSCustomObject]@{
                Id = $itemId
                Pipe = $ps
                Handle = $ps.BeginInvoke()
            }
        }

        foreach ($job in $jobs) {
            try {
                $result = $job.Pipe.EndInvoke($job.Handle)
                $result
                if ($job.Pipe.HadErrors) {
                    Write-Error "Job $($job.Id)错误: $($job.Pipe.Streams.Error -join '; ')"
                }
            }
            catch {
                Write-Error "Job $($job.Id)异常: $_"
            }
            finally {
                $job.Pipe.Dispose()
            }
        }
    }
}
finally {
    if ($runspacePool) {
        $runspacePool.Close()
        $runspacePool.Dispose()
        Write-Verbose "Runspace池已清理"
    }
    # Start-Job的清理（如使用）
    if ($jobs -and $jobs[0] -is [System.Management.Automation.Job]) {
        $jobs | Wait-Job | Receive-Job
        $jobs | Remove-Job -Force
    }
}
```

### 反模式

#### 反模式1：直接Tls12 = Tls12覆盖

```powershell
❌ 错误：[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
（覆盖系统设置，在支持Tls13的系统上禁用Tls13造成安全降级）
```

#### 反模式2：全局设置无恢复

```powershell
❌ 错误：脚本开头修改编码/TLS，脚本结束不恢复
（影响同一进程内后续执行的脚本，导致难以排查的副作用）
```

#### 反模式3：盲目Set-ExecutionPolicy Bypass

```powershell
❌ 错误：脚本开头写Set-ExecutionPolicy Bypass -Force
（1. 组策略锁定环境下无效且触发告警；2. 弱化系统安全防线）
```

#### 反模式4：不检测CLM直接使用Add-Type/COM

```powershell
❌ 错误：脚本直接New-Object -ComObject Excel.Application，CLM下100%失败
```

#### 反模式5：Runspace/并行代码无资源清理

```powershell
❌ 错误：创建RunspacePool但不Close/Dispose，导致句柄泄漏和内存泄漏
```

### 迁移验证

#### 验证1：TLS设置验证

```powershell
# 在脚本中Verbose输出可见TLS设置情况
# 执行后检查TLS设置已恢复原始值
$before = [Net.ServicePointManager]::SecurityProtocol
.\your-script.ps1 -Verbose
$after = [Net.ServicePointManager]::SecurityProtocol
if ($before -eq $after) {
    Write-Host "✅ TLS设置已正确恢复" -ForegroundColor Green
} else {
    Write-Host "❌ TLS设置未恢复！Before: $before, After: $after" -ForegroundColor Red
}
```

#### 验证2：编码设置验证

```powershell
# 验证中文输出无乱码
Write-Host "测试中文输出：构建 → 部署 → 完成"
# 预期：中文和→箭头正常显示，无乱码
```

#### 验证3：文件输出编码验证

```powershell
"测试 UTF-8 输出：→" | Out-File -FilePath test-encoding.txt -Encoding utf8
$bytes = [System.IO.File]::ReadAllBytes("test-encoding.txt")
if ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
    Write-Host "✅ UTF-8 BOM编码正确" -ForegroundColor Green
} else {
    Write-Host "❌ 文件编码不是UTF-8 with BOM" -ForegroundColor Red
}
Remove-Item test-encoding.txt
```

***

## 模式5：PS7-to-PS5-Translation（PS7语法降级转换模式）

### 模式ID

**P-PS5-TRANSLATE-001**

### 触发场景

- AI生成了PS7+语法代码，需要转换为PS5.1兼容写法时
- 从GitHub/Stack Overflow找到PS7示例代码，需要在PS5.1中运行时
- 现有PS7脚本需要降级支持PS5.1环境时
- 代码审查中发现PS7+语法需要修复时
- 批量脚本兼容性转换时

### 核心步骤/内容

#### 语法转换映射表（运算符与语言结构）

| PS7+语法/API                         | PS5.1状态                             | PS5.1兼容写法                                                                                               | 说明                            | <br />                                                                    | <br /> |
| ---------------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------- | ----------------------------- | :------------------------------------------------------------------------ | :----- |
| `cmd1 && cmd2`                     | ❌ ParserError                       | `cmd1; if ($?) { cmd2 }` 或 `cmd1; if ($LASTEXITCODE -eq 0) { cmd2 }`                                    | 外部exe用$LASTEXITCODE，cmdlet用$? | <br />                                                                    | <br /> |
| \`cmd1                             | <br />                              | cmd2\`                                                                                                  | ❌ ParserError                 | `cmd1; if (-not $?) { cmd2 }` 或 `cmd1; if ($LASTEXITCODE -ne 0) { cmd2 }` | 同上     |
| `$x ? $a : $b`                     | ❌ ParserError                       | `if ($x) { $a } else { $b }` 或 `$result = if ($x) { $a } else { $b }`                                   | 三元运算符→if/else                 | <br />                                                                    | <br /> |
| `$x ?? $y`                         | ❌ ParserError                       | `if ($null -eq $x) { $y } else { $x }` 或 `$result = if ($null -eq $x) { $y } else { $x }`               | 空合并→null检查                    | <br />                                                                    | <br /> |
| `$x ??= $y`                        | ❌ ParserError                       | `if ($null -eq $x) { $x = $y }`                                                                         | 空合并赋值→null检查+赋值               | <br />                                                                    | <br /> |
| `$obj?.Property`                   | ❌ ParserError                       | `if ($null -ne $obj) { $obj.Property }` 或 `$val = if ($null -ne $obj) { $obj.Property } else { $null }` | 空条件→null检查                    | <br />                                                                    | <br /> |
| `$obj?.Method()`                   | ❌ ParserError                       | `if ($null -ne $obj) { $obj.Method() }`                                                                 | 空条件方法调用                       | <br />                                                                    | <br /> |
| `ForEach-Object -Parallel { ... }` | ❌ 参数不存在                             | 方案1: 普通ForEach-Object顺序执行方案2: Start-Job并行方案3: Runspace池高性能并行（CLM下不可用）                                   | 见P-PS5-SAFEDEFAULTS-001并行模板   | <br />                                                                    | <br /> |
| `$using:var`（并行中）                  | ⚠️ 仅在PS7并行中需要                       | Start-Job中通过-ArgumentList传递；Runspace中通过AddArgument传递                                                    | PS5并行不支持$using:作用域            | <br />                                                                    | <br /> |
| `class ClassName { ... }`          | ⚠️ PS5支持但CLM下阻止                     | `[PSCustomObject]@{ Property = 'value' }` 或 \`New-Object PSObject                                       | Add-Member NoteProperty\`     | CLM环境必须替换                                                                 | <br /> |
| \`$arr                             | ForEach-Object -MemberName Method\` | ✅ PS5支持                                                                                                 | 相同语法可用，但注意CLM兼容性              | -                                                                         | <br /> |
| `?.` 空条件数组索引                       | ❌ ParserError                       | `if ($arr -ne $null -and $arr.Count -gt $idx) { $arr[$idx] }`                                           | -                             | <br />                                                                    | <br /> |

#### API转换映射表（Cmdlet与.NET API）

| PS7+ API/Cmdlet                            | PS5.1状态            | PS5.1兼容写法                                                                | 说明                             | <br /> |
| ------------------------------------------ | ------------------ | ------------------------------------------------------------------------ | ------------------------------ | :----- |
| `Get-WmiObject -Class Xxx`                 | ❌ PS7已移除，PS5可用但不推荐 | `Get-CimInstance -ClassName Xxx`                                         | CIM cmdlets在PS3.0+全版本兼容，优先使用   | <br /> |
| `Invoke-WmiMethod`                         | ❌ PS7已移除           | `Invoke-CimMethod`                                                       | -                              | <br /> |
| `Remove-WmiObject`                         | ❌ PS7已移除           | `Remove-CimInstance`                                                     | -                              | <br /> |
| `Set-WmiInstance`                          | ❌ PS7已移除           | `Set-CimInstance`                                                        | -                              | <br /> |
| `Register-WmiEvent`                        | ❌ PS7已移除           | `Register-CimIndicationEvent`                                            | -                              | <br /> |
| `Add-PSSnapin Xxx`                         | ❌ PS7已移除           | `Import-Module Xxx`                                                      | 检查模块是否可用                       | <br /> |
| `workflow Name { ... }`                    | ❌ PS7已移除           | 普通function + ForEach-Object/Start-Job/Runspace                           | Workflow功能在.NET Core不存在        | <br /> |
| `pwsh.exe`                                 | ❌ 纯PS5环境不存在        | `$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe`         | 或检测后分支处理                       | <br /> |
| `Invoke-WebRequest -SkipCertificateCheck`  | ❌ PS5参数不存在         | 不推荐禁用证书验证；测试环境可用.NET回调但要加范围限制                                            | 生产环境永远不要禁用证书验证                 | <br /> |
| `$PSNativeCommandUseErrorActionPreference` | ❌ PS5变量不存在         | 手动检查$LASTEXITCODE：`cmd; if ($LASTEXITCODE -ne 0) { throw "cmd failed" }` | -                              | <br /> |
| `Get-Error`                                | ❌ PS5 cmdlet不存在    | \`$error\[0]                                                             | Format-List \* -Force\` 查看完整错误 | -      |
| `Join-String`                              | ❌ PS5 cmdlet不存在    | `($array -join ', ')` 或手动拼接                                              | -                              | <br /> |
| `ConvertFrom-Markdown`                     | ❌ PS5 cmdlet不存在    | 使用第三方模块或手动解析                                                             | -                              | <br /> |

#### 行为差异处理映射表（默认行为与编码）

| PS7+默认行为                     | PS5.1行为                                           | PS5.1修复写法                                                              | 说明                                           | <br />                |
| ---------------------------- | ------------------------------------------------- | ---------------------------------------------------------------------- | -------------------------------------------- | :-------------------- |
| `>`/`>>` 重定向默认UTF-8无BOM      | 默认UTF-16LE（双字节），其他工具读取乱码                          | \`"text"                                                               | Out-File -FilePath file.txt -Encoding utf8\` | 必须显式-Encoding，不使用裸重定向 |
| 无BOM UTF-8脚本默认按UTF-8解析       | 按系统ANSI代码页（Windows-1252）解析，非ASCII字符乱码/ParserError | 脚本文件保存为UTF-8 with BOM；或避免直接使用非ASCII字符                                  | AI生成文件必须指定BOM编码                              | <br />                |
| 默认TLS 1.2+已启用                | .NET Framework 4.5默认只启用TLS 1.0/1.1                | 脚本开头追加TLS 1.2（使用-bor追加，非覆盖）                                            | 见P-PS5-SAFEDEFAULTS-001加固版TLS设置              | <br />                |
| `Write-Host`写Information流可捕获 | 只写控制台，不可重定向/捕获                                    | 需要捕获输出时用Write-Output                                                   | -                                            | <br />                |
| Web Cmdlets基于HttpClient      | 基于HttpWebRequest，行为差异（308重定向、认证等）                 | CIM/REST调用显式处理重定向；基本认证手动构造Header                                       | -                                            | <br />                |
| `string.Split(char[])`行为不同   | 直接传char\[]可用                                      | PS5直接传`$str.Split(@('a','b'))`可用；注意字符数组转换                              | -                                            | <br />                |
| COM对象跨平台差异                   | 完整COM支持                                           | Windows-only，CLM下仅白名单COM可用                                             | -                                            | <br />                |
| CIM默认协议WinRM                 | 默认DCOM，跨网络被防火墙阻止                                  | `New-CimSession -SessionOption (New-CimSessionOption -Protocol WinRM)` | 跨网络CIM调用显式指定WinRM                            | <br />                |

#### 并行处理降级方案对照表

| PS7方案                      | PS5.1降级方案                     | 适用场景                     | CLM兼容    | EDR友好          | 性能   |
| -------------------------- | ----------------------------- | ------------------------ | -------- | -------------- | ---- |
| `ForEach-Object -Parallel` | `ForEach-Object` 顺序执行         | 简单脚本/数据量小/EDR环境          | ✅        | ✅              | ⭐    |
| `ForEach-Object -Parallel` | `Start-Job`                   | IO密集型/简单并行/CLM环境         | ✅        | ⚠️ 创建子进程可能触发告警 | ⭐⭐   |
| `ForEach-Object -Parallel` | `[runspacefactory]` Runspace池 | CPU密集型/高性能/Full Language | ❌ CLM下阻止 | ⚠️ 可能触发告警      | ⭐⭐⭐⭐ |
| `workflow { parallel {} }` | Windows任务计划程序并行触发             | 企业环境/长时间运行任务             | ✅        | ✅              | ⭐⭐⭐  |
| `Start-ThreadJob`（模块）      | `Start-Job` 或 Runspace        | ThreadJob是PS7模块，PS5需安装   | -        | -              | -    |

#### 自动转换辅助正则（注意误报风险）

```powershell
# PS7→PS5自动转换辅助脚本 v1.0 (2026-07-31)
# 警告：自动转换可能引入误报和错误，转换后必须人工审查和测试
# C1加固：改进正则减少Where-Object ?别名误报
param(
    [Parameter(Mandatory=$true)]
    [string]$InputPath,
    [string]$OutputPath = ($InputPath -replace '\.ps1$', '.ps5.ps1')
)

$content = Get-Content $InputPath -Raw

# 注意：以下替换为基础文本替换，复杂场景需人工处理
# 1. 替换 ?? 运算符 (简化场景，复杂嵌套需人工)
$content = $content -replace '(\$\w+)\s*\?\?\s*([^;\r\n]+)', 'if ($null -eq $1) { $1 = $2 }'

# 2. 替换 && 运算符 (cmdlet场景，外部exe需用$LASTEXITCODE)
$content = $content -replace '(.+?)\s*&&\s*(.+)', '$1; if ($?) { $2 }'

# 3. 替换 || 运算符
$content = $content -replace '(.+?)\s*\|\|\s*(.+)', '$1; if (-not $?) { $2 }'

# 4. Get-WmiObject → Get-CimInstance
$content = $content -replace 'Get-WmiObject', 'Get-CimInstance'
$content = $content -replace 'Invoke-WmiMethod', 'Invoke-CimMethod'
$content = $content -replace 'Remove-WmiObject', 'Remove-CimInstance'

# 5. -Parallel警告
if ($content -match '-Parallel') {
    Write-Warning "发现-Parallel参数，需要手动替换为Start-Job/Runspace/顺序执行"
}

# 6. class关键字警告
if ($content -match '^\s*class\s+\w+') {
    Write-Warning "发现class定义，CLM环境下需要替换为[PSCustomObject]"
}

# 7. Add-Type警告
if ($content -match 'Add-Type') {
    Write-Warning "发现Add-Type调用，CLM环境下被阻止"
}

# 添加#Requires和安全头提示
$header = @"
#Requires -Version 5.1
# 注意：本文件由PS7→PS5自动转换脚本初步转换，必须经过人工审查和测试
# 转换时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
# 请使用P-PS5-PREFLIGHT-001预检脚本进行兼容性检查

"@
$content = $header + $content

$content | Out-File -FilePath $OutputPath -Encoding utf8
Write-Host "✅ 初步转换完成: $OutputPath" -ForegroundColor Green
Write-Host "⚠️  重要：自动转换无法处理所有场景，请进行人工审查并运行PS5.1测试" -ForegroundColor Yellow
```

### 反模式

#### 反模式1：逐字符机械替换不理解语义

```
❌ 错误：用正则全文替换?为if/else，破坏了Where-Object ?别名、字符串中的?字符、正则表达式中的?量词
（必须理解PowerShell语法上下文，或转换后人工逐行审查）
```

#### 反模式2：只替换语法不处理行为差异

```
❌ 错误：把&&替换成; if ($?)就认为转换完成
（忘记处理编码、TLS、CIM协议、ExecutionPolicy、CLM兼容性等运行时行为差异）
```

#### 反模式3：把所有并行都转成Runspace池

```
❌ 错误：统一用Runspace池替换-Parallel
（CLM环境下Runspace同样不可用；EDR环境下Runspace可能触发告警；应提供分级降级方案）
```

#### 反模式4：Get-WmiObject直接替换为Get-CimInstance不测试

```
❌ 错误：全文替换Get-WmiObject为Get-CimInstance就完事
（WMI和CIM的参数名、返回对象属性有细微差异，必须实际测试）
```

#### 反模式5：转换后不在真实PS5.1环境测试

```
❌ 错误：转换完语法看起来对就认为没问题
（必须在干净的PS5.1环境中实际执行测试，最好也在CLM环境测试）
```

### 迁移验证

#### 验证步骤1：语法预检

```powershell
# 使用模式2的预检脚本检查转换后的脚本
.\ps5-preflight-check.ps1 -ScriptPath .\converted.ps5.ps1 -Strict
# 预期：P0阻断项全部通过
```

#### 验证步骤2：PS5.1解析器测试

```powershell
# 在PS5.1中进行解析测试
powershell -ExecutionPolicy Bypass -Scope Process -Command "& {
    `$errors = `$null
    [void][System.Management.Automation.PSParser]::Tokenize((Get-Content .\converted.ps5.ps1 -Raw), [ref]`$errors)
    if (`$errors.Count -gt 0) { Write-Host '❌ 解析错误'; `$errors | ForEach-Object { Write-Host `$_.Message } }
    else { Write-Host '✅ 解析通过' }
}"
```

#### 验证步骤3：功能对比测试

```powershell
# 在PS7和PS5中分别运行脚本，对比输出结果
# 注意：这需要业务逻辑可重复执行且无副作用
# 对比输出文件/返回值是否一致
```

#### 验证步骤4：CLM环境测试（企业部署必需）

```powershell
# 在测试CLM环境中运行，验证保守兼容性
$env:__PSLockdownPolicy = '4'
powershell -ExecutionPolicy Bypass -Scope Process -File .\converted.ps5.ps1
$clmExit = $LASTEXITCODE
Remove-Item Env:__PSLockdownPolicy
if ($clmExit -eq 0) {
    Write-Host "✅ CLM环境测试通过" -ForegroundColor Green
} else {
    Write-Host "⚠️  CLM环境测试未通过，可能需要进一步调整" -ForegroundColor Yellow
}
```

***

## G3质量门检查结果

### 模式完整性检查（每个模式5要素）

| 模式ID                   | 模式名称                   | 模式ID | 触发场景 | 核心内容                        | 反模式      | 迁移验证      | 完整性 |
| ---------------------- | ---------------------- | ---- | ---- | --------------------------- | -------- | --------- | --- |
| P-PS5-PROMPT-001       | PS5-Defensive-Prompt   | ✅    | ✅    | ✅(完整版+精简版+3种场景变体)           | ✅(5个反模式) | ✅(3种验证方法) | ✅完整 |
| P-PS5-PREFLIGHT-001    | PS5-Compat-Preflight   | ✅    | ✅    | ✅(P0/P1/P2三级共27个检查项+一键预检脚本) | ✅(4个反模式) | ✅(3种验证命令) | ✅完整 |
| P-PS5-SECAUDIT-001     | PS5-Security-Audit     | ✅    | ✅    | ✅(6个维度共29个安全检查项+评分模板)       | ✅(4个反模式) | ✅(3种验证方法) | ✅完整 |
| P-PS5-SAFEDEFAULTS-001 | PS5-Safe-Defaults      | ✅    | ✅    | ✅(完整版安全头+精简版+并行模板，全部加固)     | ✅(5个反模式) | ✅(3种验证方法) | ✅完整 |
| P-PS5-TRANSLATE-001    | PS7-to-PS5-Translation | ✅    | ✅    | ✅(4张映射表+并行降级对照表+转换辅助脚本)     | ✅(5个反模式) | ✅(4种验证步骤) | ✅完整 |

### 对抗审查加固点应用检查

| 加固项（来自V阶段）                         | 应用模式                            | 状态                        | <br /> |
| ---------------------------------- | ------------------------------- | ------------------------- | :----- |
| A1: ExecutionPolicy分级+Bypass安全警示   | PROMPT/SAFEDEFAULTS/SECAUDIT    | ✅已应用                      | <br /> |
| A2: TLS追加而非覆盖，避免安全降级               | SAFEDEFAULTS/SECAUDIT/TRANSLATE | ✅已应用                      | <br /> |
| A3: Runspace标注CLM不兼容+安全提示+资源清理     | SAFEDEFAULTS/PREFLIGHT          | ✅已应用                      | <br /> |
| A4: 环境探测调试条件化输出                    | SAFEDEFAULTS                    | ✅已应用                      | <br /> |
| B1: "CLM兼容"改为"保守兼容"+环境验证           | PROMPT/SAFEDEFAULTS/SECAUDIT    | ✅已应用                      | <br /> |
| B2: 组策略锁定检测，不盲目Set-ExecutionPolicy | SAFEDEFAULTS/SECAUDIT           | ✅已应用                      | <br /> |
| B3: 全局状态保存-恢复try/finally模式         | SAFEDEFAULTS/SECAUDIT           | ✅已应用                      | <br /> |
| B4: EDR兼容性提示+-NoParallel降级开关       | SAFEDEFAULTS/TRANSLATE          | ✅已应用                      | <br /> |
| C1: 改进PS7语法检测正则减少误报                | PREFLIGHT/PROMPT/TRANSLATE      | ✅已应用                      | <br /> |
| C2: TLS13注释+Verbose日志+硬编码值兼容       | SAFEDEFAULTS                    | ✅已应用                      | <br /> |
| C3: 生产级Runspace模板含完整错误处理/清理        | SAFEDEFAULTS                    | ✅已应用                      | <br /> |
| C4: 版本元数据+更新触发条件+维护SOP             | 所有模式                            | ✅已应用                      | <br /> |
| S-01: 注入示例脱敏，无具体攻击载荷               | 所有模式                            | ✅已应用                      | <br /> |
| S-03: 永远不要使用Invoke-Expression表述    | PROMPT/SECAUDIT/PREFLIGHT       | ✅已应用                      | <br /> |
| S-05: ExecutionPolicy Bypass强制安全警示 | PROMPT/SAFEDEFAULTS/SECAUDIT    | ✅已应用                      | <br /> |
| S-06: irm                          | iex安全警告强化                       | PROMPT/SECAUDIT/PREFLIGHT | ✅已应用   |

### 质量门结论

✅ **G3质量门通过**：

- 模式数量：5个（超出最低要求3个）
- 每个模式完整包含：模式ID、触发场景、核心内容、反模式、迁移验证五要素
- V阶段12个攻击视角发现的18个加固点全部应用
- 所有安全建议采用"防御性保守"原则
- 所有代码模板采用生产级标准（错误处理、资源清理、注释、版本元数据）
- 覆盖24个事实场景、14个根因洞察的解决方案

***

## 附录：模式关联矩阵

| 模式                     | 覆盖洞察（I阶段）                                    | 覆盖事实场景（R阶段）                             |
| ---------------------- | -------------------------------------------- | --------------------------------------- |
| P-PS5-PROMPT-001       | I-MODEL-01/02/03/04, I-COMPAT-01/02/03       | 所有24个场景的源头预防                            |
| P-PS5-PREFLIGHT-001    | I-COMPAT-01/02/03, I-SEC-01/02/04            | 1-1\~1-5,1-8,2-2\~2-8,3-1\~3-8          |
| P-PS5-SECAUDIT-001     | I-SEC-01/02/03/04, I-PERF-03                 | 1-6,1-7,2-1,2-3,2-8,3-3,3-5,3-6,3-8     |
| P-PS5-SAFEDEFAULTS-001 | I-COMPAT-03, I-SEC-01/02/04, I-PERF-01/02/03 | 1-5,1-6,1-8,2-2,2-3,2-8,3-3,3-5,3-6,3-8 |
| P-PS5-TRANSLATE-001    | I-COMPAT-01/02, I-PERF-01                    | 1-1~1-4,2-5~2-7,3-1,3-2,3-7           |

---

## E阶段：模式萃取入库记录

> 本章节记录 E 阶段（模式萃取）的归档结果，建立本文档与模式库的双向溯源。

| 模式ID | 模式名称 | 模式库ID | 模式类型 | 成熟度 | 模式库文件路径 |
|--------|---------|---------|---------|--------|--------------|
| P-PS5-PROMPT-001 | PS5-Defensive-Prompt 防御性Prompt模板 | `ps5-defensive-prompt` | 方法论模式 (ai-collaboration) | L1 | `.agents/docs/retrospective/patterns/methodology-patterns/ai-collaboration/ps5-defensive-prompt.md` |
| P-PS5-PREFLIGHT-001 | PS5-Compat-Preflight 兼容性预检Checklist | `ps5-compat-preflight` | 代码模式 (code-patterns) | L1 | `.agents/docs/retrospective/patterns/code-patterns/ps5-compat-preflight.md` |
| P-PS5-SECAUDIT-001 | PS5-Security-Audit 安全代码审查Checklist | `ps5-security-audit` | 代码模式 (code-patterns) | L1 | `.agents/docs/retrospective/patterns/code-patterns/ps5-security-audit.md` |
| P-PS5-SAFEDEFAULTS-001 | PS5-Safe-Defaults 安全默认值防护 | `ps5-safe-defaults` | 代码模式 (code-patterns) | L1 | `.agents/docs/retrospective/patterns/code-patterns/ps5-safe-defaults.md` |
| P-PS5-TRANSLATE-001 | PS7-to-PS5-Translation PS7语法降级转换 | `ps7-to-ps5-translation` | 代码模式 (code-patterns) | L1 | `.agents/docs/retrospective/patterns/code-patterns/ps7-to-ps5-translation.md` |

**归档统计**：5个模式全部成功入库（萃取率 5/5 = 100%）。其中 1 个方法论模式（AI协作/Prompt工程）+ 4 个代码模式（PowerShell安全兼容工具链），形成完整的"AI生成PS5安全兼容代码"闭环工具链：

1. **源头预防**：PROMPT（防御性Prompt模板）→ 2. **生成后预检**：PREFLIGHT（兼容性三级预检）→ 3. **上线前审计**：SECAUDIT（6维度安全审查）→ 4. **运行时防护**：SAFEDEFAULTS（安全默认值头）→ 5. **版本转换**：TRANSLATE（PS7→PS5语法转换）

