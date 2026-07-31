---
id: "ai-powershell5-hell-wiki-07-checklists"
title: "兼容性预检+安全审查Checklist"
source: "internal:ai-powershell5-research-rfive"
date: "2026-07-31"
category: "learning"
tags: ["powershell", "powershell-5.1", "ai-coding", "checklist", "compatibility", "security-audit", "preflight"]
---

# 兼容性预检+安全审查Checklist

本章提供经过V阶段加固的兼容性预检和安全审查Checklist，用于AI生成PowerShell 5.1脚本后的验证工作。

---

## Checklist版本信息

```
# PS5.1兼容性&安全审查Checklist v1.0
# 最后更新: 2026-07-31
# 基于PowerShell 7.4差异清单，经过V阶段对抗审查加固
# 更新触发条件: PS7新版本发布/微软更新差异文档/发现新陷阱
# 更新检查URL: https://learn.microsoft.com/en-us/powershell/scripting/whats-new/differences-from-windows-powershell
```

---

## 第一部分：兼容性预检Checklist（模式2）

按三级优先级组织检查项：P0（阻断项，不通过则禁止执行）、P1（高危项，可能静默失败或数据损坏）、P2（建议项，提升健壮性）。

### P0 阻断项检查（必须全部通过，共8项）

| 检查项ID | 检查内容 | 检查方法 | 不通过时修复 |
|---------|---------|---------|------------|
| P0-01 | PS7+禁用语法检测 | 运行PS7语法检测脚本；或在PS5.1中用PSParser解析 | 按语法转换映射表替换为PS5兼容写法 |
| P0-02 | WMI cmdlet检测 | `Select-String -Path script.ps1 -Pattern 'Get-WmiObject|Invoke-WmiMethod|Remove-WmiObject|Set-WmiInstance|Register-WmiEvent'` | 全部替换为对应CIM cmdlet：Get-WmiObject→Get-CimInstance |
| P0-03 | Workflow关键字检测 | `Select-String -Path script.ps1 -Pattern '^\s*workflow\s'` | 重构为普通PowerShell函数，并行逻辑用Start-Job |
| P0-04 | Add-PSSnapin检测 | `Select-String -Path script.ps1 -Pattern 'Add-PSSnapin'` | 使用Import-Module替代；如模块不存在需先检测 |
| P0-05 | pwsh.exe路径检测 | `Select-String -Path script.ps1 -Pattern 'pwsh\.exe'` | 替换为`$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe`或检测后分支处理 |
| P0-06 | Invoke-Expression/iex检测 | `Select-String -Path script.ps1 -Pattern 'Invoke-Expression|\biex\b'`（排除注释行） | 重构为直接cmdlet调用或scriptblock + &调用 |
| P0-07 | class关键字检测（CLM环境） | `Select-String -Path script.ps1 -Pattern '^\s*class\s+\w+'` | 替换为[PSCustomObject]@{}或New-Object PSObject + Add-Member |
| P0-08 | Add-Type检测（CLM环境） | `Select-String -Path script.ps1 -Pattern 'Add-Type'` | 用纯PowerShell重写，或使用预编译签名程序集 |

### P1 高危项检查（强烈建议修复，共9项）

| 检查项ID | 检查内容 | 检查方法 | 不通过时修复 |
|---------|---------|---------|------------|
| P1-01 | 文件输出编码检测 | `Select-String -Path script.ps1 -Pattern '(Out-File|Set-Content|Add-Content).*(?!-Encoding\s+utf8)'`；检查`>`/`>>`重定向 | 所有Out-File/Set-Content/Add-Content添加`-Encoding utf8`；重定向改为Out-File显式编码 |
| P1-02 | TLS设置检测 | `Select-String -Path script.ps1 -Pattern 'ServicePointManager::SecurityProtocol\s*='` | 在脚本开头添加TLS 1.2追加设置（使用-OR追加，非覆盖） |
| P1-03 | 自动变量覆盖检测 | 检查变量名是否匹配：`$HOME,$PSHOME,$PWD,$?,$_,$ARGS,$ERROR,$EXCEPTION,$FALSE,$TRUE,$NULL,$PSScriptRoot,$PSCommandPath,$Host`（大小写不敏感） | 重命名变量为带前缀名称（如$tempHome、$configPath） |
| P1-04 | 非白名单COM对象检测 | `Select-String -Path script.ps1 -Pattern 'New-Object\s+-ComObject\s+(?!Scripting\.(Dictionary|FileSystemObject)|VBScript\.RegExp)'` | 评估是否真的需要COM；CLM环境下必须移除或替换为原生cmdlet |
| P1-05 | .NET直接调用注册表检测 | `Select-String -Path script.ps1 -Pattern '\[Microsoft\.Win32\.Registry\]'` | 替换为Set-ItemProperty/Get-ItemProperty等原生注册表cmdlet |
| P1-06 | irm\|iex一行执行检测 | `Select-String -Path script.ps1 -Pattern 'irm.*\|.*iex|Invoke-RestMethod.*\|.*Invoke-Expression'` | 拆分为三步：下载到文件→Get-Content检查→确认后执行 |
| P1-07 | 执行策略硬编码检测 | `Select-String -Path script.ps1 -Pattern 'Set-ExecutionPolicy\s+Bypass\s+-Scope\s+(LocalMachine|CurrentUser)'` | 改为建议用户使用`-ExecutionPolicy Bypass -Scope Process`调用方式，或在组策略环境中检测后提示 |
| P1-08 | UTF-8无BOM脚本检测 | 用十六进制编辑器检查.ps1文件前3字节：EF BB BF是UTF-8 BOM | 重新保存为UTF-8 with BOM格式 |
| P1-09 | 全局状态无恢复检测 | 检查是否修改了$OutputEncoding/[Console]::OutputEncoding/SecurityProtocol但无finally恢复 | 使用"保存-设置-恢复"try/finally模式 |

### P2 建议项检查（提升健壮性，共10项）

| 检查项ID | 检查内容 | 检查方法 | 修复建议 |
|---------|---------|---------|---------|
| P2-01 | #Requires版本声明 | 检查是否包含`#Requires -Version 5.1` | 在脚本首行添加版本声明 |
| P2-02 | Set-StrictMode | 检查是否启用`Set-StrictMode -Version Latest` | 脚本开头启用严格模式，捕获未初始化变量等问题 |
| P2-03 | $ErrorActionPreference | 检查是否设置了错误处理策略 | 根据需要设置`$ErrorActionPreference = 'Stop'`或在cmdlet中使用-ErrorAction |
| P2-04 | 模块可用性检测 | 检查Import-Module前是否有Get-Module -ListAvailable检测 | 添加模块存在性检查，不存在时抛出友好错误 |
| P2-05 | 参数类型约束 | 检查param()块中参数是否有类型约束 | 为所有参数添加类型约束（[string]/[int]/[switch]等） |
| P2-06 | 危险操作确认 | 检查Remove-Item/Stop-Process等危险操作前是否有确认或-WhatIf支持 | 添加-WhatIf支持或显式路径输出提示 |
| P2-07 | Runspace/Start-Job CLM检测 | 检查并行代码前是否检测了$ExecutionContext.SessionState.LanguageMode | 添加CLM检测和降级路径 |
| P2-08 | Runspace/Start-Job -NoParallel开关 | 检查并行代码是否支持顺序执行降级 | 添加[switch]$NoParallel参数支持EDR环境 |
| P2-09 | 注释帮助 | 检查是否有基于注释的帮助 | 添加.SYNOPSIS/.DESCRIPTION/.PARAMETER/.EXAMPLE |
| P2-10 | 版本元数据 | 检查脚本是否包含版本/日期/更新记录元数据 | 在脚本头部添加版本注释元数据 |

### 一键预检脚本

```powershell
param(
    [Parameter(Mandatory=$true)]
    [string]$ScriptPath,
    [switch]$Strict
)

$results = @()
$content = Get-Content $ScriptPath -Raw -ErrorAction Stop

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

$parseErrors = $null
[void][System.Management.Automation.PSParser]::Tokenize($content, [ref]$parseErrors)
if ($parseErrors.Count -gt 0) {
    $results += [PSCustomObject]@{ Level = 'P0'; Item = 'P0-00: 解析器错误'; Status = "FAIL ($($parseErrors.Count)个错误)" }
}

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

---

## 第二部分：安全代码审查Checklist（模式3）

### 维度1：CLM/Constrained Language Mode兼容性（6项）

| 检查项ID | 检查内容 | 严重度 | 检查方法 | 修复方案 |
|---------|---------|--------|---------|---------|
| SEC-CLM-01 | 是否使用Add-Type？ | P0 | `Select-String -Pattern 'Add-Type'` | 用纯PowerShell重写；或使用预编译签名程序集 |
| SEC-CLM-02 | 是否定义了PowerShell class？ | P0 | `Select-String -Pattern '^\s*class\s+\w+'` | 替换为[PSCustomObject]@{} |
| SEC-CLM-03 | 是否调用非白名单COM对象？ | P0 | 检查New-Object -ComObject参数，白名单仅：Scripting.Dictionary、Scripting.FileSystemObject、VBScript.RegExp | 移除COM调用；或使用白名单内COM；或申请企业WDAC白名单 |
| SEC-CLM-04 | 是否直接调用.NET Framework类型方法？ | P0 | 检查`[Namespace.Class]::Method()`调用，特别是：[Microsoft.Win32.Registry]、[System.Reflection.*]、[System.Runtime.InteropServices.*]等 | 使用PowerShell原生cmdlet替代 |
| SEC-CLM-05 | 是否使用XAML/WPF？ | P1 | `Select-String -Pattern 'XamlReader|System\.Windows'` | CLM下XAML被阻止，考虑使用WinForms或原生主机UI |
| SEC-CLM-06 | 是否有语言模式检测？ | P2 | 检查是否查询`$ExecutionContext.SessionState.LanguageMode` | 在需要Full Language功能时添加检测和友好提示 |

### 维度2：命令注入防护（6项）

| 检查项ID | 检查内容 | 严重度 | 检查方法 | 修复方案 |
|---------|---------|--------|---------|---------|
| SEC-INJ-01 | **是否使用Invoke-Expression/iex？** | P0 | `Select-String -Pattern 'Invoke-Expression|\biex\b'`（排除注释） | **永远不要使用**。重构为：1)直接cmdlet调用；2)scriptblock + &调用；3)参数绑定 |
| SEC-INJ-02 | 参数是否有类型约束？ | P0 | 检查param()块参数是否有[string]/[int]等类型约束 | 为所有用户输入参数添加强类型约束 |
| SEC-INJ-03 | 用户输入是否直接拼接进命令？ | P0 | 检查字符串拼接后执行的模式 | 使用参数绑定：Get-Process -Id $ProcId |
| SEC-INJ-04 | 是否使用irm|iex/Invoke-WebRequest|iex模式？ | P0 | `Select-String -Pattern '\|\s*iex\b'` | 拆分为下载→检查→执行三步；或使用已签名的脚本包 |
| SEC-INJ-05 | 动态命令是否使用scriptblock？ | P1 | 如需动态命令，检查是否使用{ param(...) ... } + &调用 | 如必须动态构造命令，使用scriptblock而非字符串拼接 |
| SEC-INJ-06 | cmd /c或外部进程调用是否有转义问题？ | P1 | 检查cmd/c调用中的引号嵌套和路径变量 | 使用PowerShell原生cmdlet替代cmd.exe调用；使用LiteralPath |

### 维度3：凭证与敏感信息处理（5项）

| 检查项ID | 检查内容 | 严重度 | 检查方法 | 修复方案 |
|---------|---------|--------|---------|---------|
| SEC-CRED-01 | 凭证是否硬编码在脚本中？ | P0 | 搜索明文密码/API Key/Token/ConnectionString等模式 | 使用Get-Credential、SecretManagement模块、或DPAPI加密存储 |
| SEC-CRED-02 | 是否使用-credential参数传递明文密码？ | P0 | 检查`ConvertTo-SecureString -AsPlainText -Force`后直接构造PSCredential | 使用Get-Credential交互式获取；或从Windows Credential Manager读取 |
| SEC-CRED-03 | 凭证是否输出到日志/控制台？ | P1 | 检查Write-Host/Out-File/日志中是否输出$credential或密码变量 | 禁止输出凭证对象；日志中对敏感字段打码 |
| SEC-CRED-04 | 临时凭证文件是否安全清理？ | P2 | 检查是否导出凭证到磁盘文件且无清理 | 使用try/finally确保临时凭证文件被安全删除；优先使用内存存储 |
| SEC-CRED-05 | 是否使用SSL/TLS加密传输凭证？ | P1 | 检查HTTP（非HTTPS）端点是否传输凭证 | 所有凭证传输必须使用HTTPS；脚本开头追加TLS 1.2设置 |

### 维度4：执行策略与权限控制（4项）

| 检查项ID | 检查内容 | 严重度 | 检查方法 | 修复方案 |
|---------|---------|--------|---------|---------|
| SEC-EP-01 | 是否建议用户全局Bypass执行策略？ | P0 | 搜索`Set-ExecutionPolicy Bypass -Scope LocalMachine`或`-Scope CurrentUser`且无组策略检测 | ⚠️ Bypass仅应在完全信任脚本来源时使用，且推荐`-Scope Process` |
| SEC-EP-02 | 是否检测组策略锁定状态？ | P1 | 检查Set-ExecutionPolicy前是否检测MachinePolicy/UserPolicy | 添加组策略锁定检测，锁定时提示联系IT部门而非盲目设置 |
| SEC-EP-03 | 脚本是否要求管理员权限但无检测？ | P1 | 检查是否有需要提升权限的操作但无#Requires -RunAsAdministrator | 需要管理员权限时添加`#Requires -RunAsAdministrator` |
| SEC-EP-04 | CI脚本是否使用-Scope Process？ | P1 | CI场景中检查-ExecutionPolicy Bypass是否带-Scope Process | CI中始终使用-ExecutionPolicy Bypass -Scope Process，不影响其他进程 |

### 维度5：编码安全与数据保护（4项）

| 检查项ID | 检查内容 | 严重度 | 检查方法 | 修复方案 |
|---------|---------|--------|---------|---------|
| SEC-ENC-01 | TLS设置是否正确（追加而非覆盖）？ | P1 | 检查SecurityProtocol赋值是否使用-bor追加而非直接赋值 | 使用追加模式，保留系统已有协议 |
| SEC-ENC-02 | 是否禁用证书验证？ | P1 | 检查是否设置`[Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}` | 生产环境不要禁用证书验证；如必须（测试环境）添加明确警示和范围限制 |
| SEC-ENC-03 | 文件输出是否显式指定编码？ | P1 | 检查Out-File/Set-Content是否带-Encoding参数；重定向是否改为显式编码 | 所有文件输出显式指定-Encoding utf8（PS5带BOM） |
| SEC-ENC-04 | 临时文件是否在系统临时目录且安全清理？ | P2 | 检查临时文件是否在$env:TEMP创建，是否用try/finally清理 | 使用Join-Path $env:TEMP创建临时文件，finally中Remove-Item清理 |

### 维度6：安全默认值与防御性编程（6项）

| 检查项ID | 检查内容 | 严重度 | 检查方法 | 修复方案 |
|---------|---------|--------|---------|---------|
| SEC-DEF-01 | 是否覆盖自动变量？ | P1 | 检查自定义变量名是否为$HOME/$PWD/$_/$?/$null等（大小写不敏感） | 使用带前缀的变量名（$tempXxx/$configXxx） |
| SEC-DEF-02 | 危险操作是否有-WhatIf/确认？ | P1 | 检查Remove-Item/Stop-Process/Stop-Service等是否支持-WhatIf或有确认提示 | 支持-WhatIf和-Confirm参数，生产环境使用前先-WhatIf模拟 |
| SEC-DEF-03 | 是否使用Set-StrictMode？ | P2 | 检查是否有Set-StrictMode -Version Latest | 脚本开头启用严格模式 |
| SEC-DEF-04 | 全局状态修改是否有恢复？ | P1 | 检查是否修改$OutputEncoding/Console.OutputEncoding/SecurityProtocol但无finally恢复 | 使用"保存-设置-恢复"try/finally模式 |
| SEC-DEF-05 | 错误处理是否完善？ | P2 | 检查是否有try/catch/finally，是否检查$?/$LASTEXITCODE | 添加适当的错误处理，外部进程调用检查$LASTEXITCODE |
| SEC-DEF-06 | 模块导入前是否检测？ | P2 | 检查Import-Module前是否有Get-Module -ListAvailable检测 | 添加模块存在性检查，给出友好错误信息 |

### 安全审查评分模板

| 维度 | P0问题数 | P1问题数 | P2问题数 | 风险等级 |
|------|---------|---------|---------|---------|
| CLM兼容性 | __ | __ | __ | 高/中/低 |
| 命令注入防护 | __ | __ | __ | 高/中/低 |
| 凭证处理 | __ | __ | __ | 高/中/低 |
| 执行策略与权限 | __ | __ | __ | 高/中/低 |
| 编码安全 | __ | __ | __ | 高/中/低 |
| 防御性编程 | __ | __ | __ | 高/中/低 |
| **合计** | **__** | **__** | **__** | **高/中/低** |

**通过标准**：P0问题数=0；P1问题数≤2且有补偿控制；风险等级不超过"中"。

---

下一章：[08-pitfalls-anti-patterns.md](08-pitfalls-anti-patterns.md) | 上一章：[06-prompt-templates.md](06-prompt-templates.md) | 返回[目录](README.md)
