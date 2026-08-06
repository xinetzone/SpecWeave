---
id: "ps5-compat-preflight"
source: "../../../../../.trae/specs/ai-powershell5-hell-wiki/supporting-analysis/05-patterns.md#模式2ps5-compat-preflight兼容性预检checklist模式"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/ps5-compat-preflight.toml"
maturity: "L1"
validation_count: 1
reuse_count: 0
documentation_level: "standard"
pattern_id: "P-PS5-PREFLIGHT-001"
tags: ["powershell", "powershell-5.1", "preflight-check", "compatibility", "ci-gate", "checklist", "code-review", "clm"]
related_patterns:
  - "ps5-defensive-prompt"
  - "ps5-security-audit"
  - "ps5-safe-defaults"
  - "ps7-to-ps5-translation"
  - "runtime-version-enforcement"
  - "preflight-checks-script"
---
> **提炼自**：[05-patterns.md#模式2](../../../../../.trae/specs/ai-powershell5-hell-wiki/supporting-analysis/05-patterns.md#模式2ps5-compat-preflight兼容性预检checklist模式) —— AI大模型×PowerShell 5兼容安全研究E阶段萃取

# PS5兼容性预检Checklist模式（PS5-Compat-Preflight）

## 模式类型

代码模式（PowerShell/兼容性验证/CI门禁）

## 成熟度

L1 实验性（AI×PowerShell 5.1专题研究验证）

## 适用场景

- AI生成PowerShell 5.1脚本后，执行前人工/自动验证时
- CI/CD流水线中添加PS5兼容性检查门禁时
- 代码审查（Code Review）阶段检查PS兼容性时
- 接收第三方/AI生成脚本后在生产环境运行前
- 脚本从开发环境迁移到测试/生产环境前

**不适用场景**：纯PowerShell 7+项目无需兼容5.1；简单单行命令无需预检。

## 问题背景

AI生成的PowerShell代码在5.1环境下失败的原因是多层次的，不仅仅是语法ParserError：
1. **语法层**：PS7+新运算符（`??` `?:` `&&` `||` `?.` `-Parallel` `class`）导致ParserError，脚本根本无法加载
2. **API层**：`Get-WmiObject`虽在PS5可用但已废弃、`Add-PSSnapin`/`workflow`在PS7已移除、`pwsh.exe`路径不存在
3. **运行时行为层**：编码默认UTF-16LE、TLS 1.2默认不启用、CIM默认DCOM协议被防火墙阻止
4. **安全层**：CLM环境阻止`Add-Type`/`class`/.NET直接调用/非白名单COM
5. **编码层**：无BOM的UTF-8脚本被按ANSI解析导致非ASCII字符乱码/ParserError

单纯的语法检查（红色波浪线）只能发现第1层问题，2-5层问题在语法上完全正确但运行时必然失败。AI模型自身也无法可靠检测自己生成代码的版本兼容性问题（"AI你帮我检查一下你生成的代码有没有兼容性问题"是无效请求）。

## 核心内容

按三级优先级组织检查项：**P0（阻断项，不通过则禁止执行）、P1（高危项，可能静默失败或数据损坏）、P2（建议项，提升健壮性）**。

### P0 阻断项检查（必须全部通过）

| 检查项ID | 检查内容 | 检查方法 | 不通过时修复 |
|---------|---------|---------|------------|
| P0-01 | PS7+禁用语法检测 | 运行PS7语法检测脚本；或在PS5.1中用PSParser解析 | 按P-PS5-TRANSLATE-001模式替换为PS5兼容写法 |
| P0-02 | WMI cmdlet检测 | `Select-String -Path script.ps1 -Pattern 'Get-WmiObject|Invoke-WmiMethod|Remove-WmiObject|Set-WmiInstance|Register-WmiEvent'` | 全部替换为对应CIM cmdlet：Get-WmiObject→Get-CimInstance |
| P0-03 | Workflow关键字检测 | `Select-String -Path script.ps1 -Pattern '^\s*workflow\s'` | 重构为普通PowerShell函数，并行逻辑用Start-Job |
| P0-04 | Add-PSSnapin检测 | `Select-String -Path script.ps1 -Pattern 'Add-PSSnapin'` | 使用Import-Module替代；如模块不存在需先检测 |
| P0-05 | pwsh.exe路径检测 | `Select-String -Path script.ps1 -Pattern 'pwsh\.exe'` | 替换为`$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe`或检测后分支处理 |
| P0-06 | Invoke-Expression/iex检测 | `Select-String -Path script.ps1 -Pattern 'Invoke-Expression|\biex\b'`（排除注释行） | 重构为直接cmdlet调用或scriptblock + &调用 |
| P0-07 | class关键字检测（CLM环境） | `Select-String -Path script.ps1 -Pattern '^\s*class\s+\w+'` | 替换为[PSCustomObject]@{}或New-Object PSObject + Add-Member |
| P0-08 | Add-Type检测（CLM环境） | `Select-String -Path script.ps1 -Pattern 'Add-Type'` | 用纯PowerShell重写，或使用预编译签名程序集 |

### P1 高危项检查（强烈建议修复）

| 检查项ID | 检查内容 | 检查方法 | 不通过时修复 |
|---------|---------|---------|------------|
| P1-01 | 文件输出编码检测 | `Select-String -Path script.ps1 -Pattern '(Out-File|Set-Content|Add-Content).*(?!-Encoding\s+utf8)'`；检查`>`/`>>`重定向 | 所有Out-File/Set-Content/Add-Content添加`-Encoding utf8`；重定向改为Out-File显式编码 |
| P1-02 | TLS设置检测 | `Select-String -Path script.ps1 -Pattern 'ServicePointManager::SecurityProtocol\s*='` | 在脚本开头添加TLS 1.2追加设置（使用-OR追加，非覆盖，见P-PS5-SAFEDEFAULTS-001） |
| P1-03 | 自动变量覆盖检测 | 检查变量名是否匹配：`$HOME,$PSHOME,$PWD,$?,$_,$ARGS,$ERROR,$EXCEPTION,$FALSE,$TRUE,$NULL,$PSScriptRoot,$PSCommandPath,$Host`（大小写不敏感） | 重命名变量为带前缀名称（如$tempHome、$configPath） |
| P1-04 | 非白名单COM对象检测 | `Select-String -Path script.ps1 -Pattern 'New-Object\s+-ComObject\s+(?!Scripting\.(Dictionary|FileSystemObject)|VBScript\.RegExp)'` | 评估是否真的需要COM；CLM环境下必须移除或替换为原生cmdlet |
| P1-05 | .NET直接调用注册表检测 | `Select-String -Path script.ps1 -Pattern '\[Microsoft\.Win32\.Registry\]'` | 替换为Set-ItemProperty/Get-ItemProperty等原生注册表cmdlet |
| P1-06 | irm\|iex一行执行检测 | `Select-String -Path script.ps1 -Pattern 'irm.*\|.*iex|Invoke-RestMethod.*\|.*Invoke-Expression'` | 拆分为三步：下载到文件→Get-Content检查→确认后执行 |
| P1-07 | 执行策略硬编码检测 | `Select-String -Path script.ps1 -Pattern 'Set-ExecutionPolicy\s+Bypass\s+-Scope\s+(LocalMachine|CurrentUser)'` | 改为建议用户使用`-ExecutionPolicy Bypass -Scope Process`调用方式，或在组策略环境中检测后提示 |
| P1-08 | UTF-8无BOM脚本检测 | 用十六进制编辑器检查.ps1文件前3字节：EF BB BF是UTF-8 BOM | 重新保存为UTF-8 with BOM格式 |
| P1-09 | 全局状态无恢复检测 | 检查是否修改了$OutputEncoding/[Console]::OutputEncoding/SecurityProtocol但无finally恢复 | 使用"保存-设置-恢复"try/finally模式 |

### P2 建议项检查（提升健壮性）

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
    @{ Pattern = '(?<![?|%])&&(?!&)'; Name = 'P0-01: &&运算符' },
    @{ Pattern = '(?<![|])\|\|(?!\|)'; Name = 'P0-01: ||运算符' },
    @{ Pattern = '-Parallel\s'; Name = 'P0-01: -Parallel参数' },
    @{ Pattern = '(?<![?])\?\.(?!\?)'; Name = 'P0-01: ?.运算符' },
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

## 反模式（禁止做的事）

**反模式1："在我机器上能跑"就上线**
```
❌ 错误：在开发机（Full Language Mode、已设ExecutionPolicy、已装所有模块）测试通过就认为脚本没问题
（企业CLM环境、CI服务账户、干净Windows安装环境下必然失败）
```

**反模式2：只测试语法不测试运行**
```
❌ 错误：只看脚本有没有红色波浪线（ParserError）就认为没问题
（编码乱码、TLS失败、CLM阻止、WMI→CIM问题都是运行时错误，语法可能完全正确）
```

**反模式3：依赖AI自我检查**
```
❌ 错误："AI你帮我检查一下你生成的代码有没有兼容性问题"
（模型自身无法可靠检测自己生成代码的版本兼容性问题，必须用外部工具/Checklist）
```

**反模式4：使用旧的PS版本（如PS3/PS4）测试PS5代码**
```
❌ 错误：在PS4上测试通过就认为PS5.1也能跑
（虽然PS5向下兼容，但部分行为和cmdlet可用性仍有差异）
```

## 迁移验证

### 验证命令1：执行一键预检脚本
```powershell
.\ps5-preflight-check.ps1 -ScriptPath .\your-script.ps1 -Strict
# 预期输出：✅ P0阻断项全部通过
```

### 验证命令2：PS5.1实际执行测试（-WhatIf模拟）
```powershell
# 在干净的PS5.1环境（非开发机）中执行
powershell -ExecutionPolicy Bypass -Scope Process -Command "& { .\your-script.ps1 -WhatIf }"
```

### 验证命令3：CLM环境模拟测试（可选）
```powershell
# 在启用了WDAC/AppLocker的测试环境或使用__PSLockdownPolicy模拟
$env:__PSLockdownPolicy = '4'  # 启用CLM
powershell -ExecutionPolicy Bypass -Scope Process -File .\your-script.ps1
Remove-Item Env:__PSLockdownPolicy
```

---

*成熟度：L1（实验性，validation_count=1） | 首次验证：AI×PowerShell 5.1研究 2026-07-31*
