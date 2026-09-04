# PowerShell 5 Wiki 代码示例语法验证报告

> 生成时间: 2026-07-31 20:23:40
> 验证环境: Windows PowerShell 5.1
> 验证方式: `[scriptblock]::Create()` 静态语法解析（不执行代码）

## 统计摘要

| 指标 | 数量 |
|------|------|
| 扫描Markdown文件 | 11 |
| PowerShell代码块总数 | 84 |
| 💻 完整可执行代码 | 30 |
| 📝 代码片段/伪代码（跳过验证） | 3 |
| ⚠️ 反模式/错误示例 | 51 |
| ✅ 语法验证通过 | 74 |
| ❌ 语法错误（含反模式预期失败） | 7 |
| ⏭️ 跳过验证（片段） | 3 |

---

## 验证结论

✅ **所有代码示例验证通过！**

- 所有标记为「完整可执行」的PS5兼容代码均通过 PowerShell 5.1 语法验证
- PS7+ 特有语法（`?:`、`??`、`&&`、`||`、`?.`、`-Parallel`）仅出现在明确标记的错误演示/反模式示例中
- 检测脚本中使用的正则表达式模式匹配（如 `\?\?`）属于字符串字面量，不属于实际代码语法，已正确排除
- 反模式/错误示例按预期展示语法错误，符合文档设计目的

---

## 详细验证结果

### 文件: `01-ps5-ps7-differences.md`

#### 块 #1 (行 29)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
# ❌ && 运算符（PS5 不支持）
# dotnet build && dotnet test

# ✅ PS5 兼容写法（cmdlet 用 $?，外部 exe 用 $LASTEXITCODE）
dotnet build; if ($LASTEXITCODE -eq 0) { dotnet test }

# ❌ ?: 三元运算符（PS5 不支持）
# $status = $hasError ? 'ERROR' : 'OK'

# ✅ PS5 兼容写法
$status = if ($hasError) { 'ERROR' } else { 'OK' }

# ❌ ?? 空合并（PS5 不支持）
# $username = $user ?? "Unknown"

# ✅ PS5 兼容写法
$username = if ($null -eq $user) { "Unknown" } else { $user }

# ❌ ForEach-Object -Parallel（PS5 不支持）
# 1..10 | ForEach-Object -Parallel { Start-Sleep 1; $_ }

# ✅ PS5 兼容写法（顺序执行）
1..10 | ForEach-Object { Start-Sleep 1; $_ }

# ✅ PS5 并行方案（Start-Job，CLM 兼容）
$jobs = 1..10 | ForEach-Object { Start-Job -ScriptBlock { Start-Sleep 1; $using:_ } }
$jobs | Wait-Job | Receive-Job; $jobs | Remove-Job
```

#### 块 #2 (行 75)

- 分类: 📝 代码片段/伪代码
- 语法: ⏭️ 跳过

```powershell
# ❌ WMI cmdlets（PS7 已移除，不推荐在 PS5 使用）
# Get-WmiObject -Class Win32_OperatingSystem

# ✅ CIM cmdlets（PS3.0+ 全版本兼容，推荐使用）
Get-CimInstance -ClassName Win32_OperatingSystem

# ❌ 计划任务调用 pwsh.exe（纯 PS5 环境不存在）
# $psPath = "pwsh.exe"

# ✅ PS5 正确路径
$psPath = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"

# ❌ workflow 关键字（PS7 已移除）
# workflow Deploy-Servers { parallel { ... } }

# ✅ 普通函数 + Start-Job/Runspace
function Deploy-Servers { param([string[]]$servers) $servers | ForEach-Object { ... } }
```

> 说明：不完整片段，跳过语法验证

#### 块 #3 (行 110)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
# ❌ 裸重定向（PS5 默认 UTF-16LE，其他工具读取乱码）
# echo "Build → Deploy" > output.txt

# ✅ 显式指定编码（PS5 的 -Encoding utf8 是带 BOM 的 UTF-8，PS5 正确解析所需）
"Build → Deploy" | Out-File -FilePath output.txt -Encoding utf8

# ❌ 假设 TLS 1.2 已启用（PS5/.NET Framework 4.5 默认未启用）
# Invoke-RestMethod -Uri https://api.example.com/data

# ✅ PS5 TLS 1.2 追加设置（V 阶段 A2 加固：追加而非覆盖，保留系统已有协议）
$originalTls = [Net.ServicePointManager]::SecurityProtocol
try {
    $tls12 = [Net.SecurityProtocolType]::Tls12
    if (($originalTls -band $tls12) -ne $tls12) {
        [Net.ServicePointManager]::SecurityProtocol = $originalTls -bor $tls12
    }
    Invoke-RestMethod -Uri https://api.example.com/data
} finally {
    [Net.ServicePointManager]::SecurityProtocol = $originalTls
}
```

#### 块 #4 (行 148)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
# ❌ CLM 下失败的写法
# [Microsoft.Win32.Registry]::SetValue("HKLM:\SOFTWARE\...", "Key", "Value")  # .NET 直接调用
# Add-Type -TypeDefinition "public class Win32 { ... }"  # Add-Type 被阻止
# $excel = New-Object -ComObject Excel.Application  # 非白名单 COM 被阻止
# class ServerConfig { [string]$Name; [string]$IP }  # class 关键字被阻止

# ✅ CLM 兼容写法
Set-ItemProperty -Path "HKLM:\SOFTWARE\MyApp" -Name "Setting" -Value "Value"  # 原生 cmdlet
[PSCustomObject]@{ Name = 'server01'; IP = '192.168.1.1' }  # PSCustomObject 替代 class

# CLM 白名单 COM 对象（仅三个）：
# - Scripting.Dictionary
# - Scripting.FileSystemObject
# - VBScript.RegExp
```

#### 块 #5 (行 167)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
# ❌ 不推荐：日常全局 Bypass（弱化安全防线）
# Set-ExecutionPolicy Bypass -Scope LocalMachine -Force

# ✅ 开发者本地一次性脚本（Process 级作用域，不影响其他进程）
powershell -ExecutionPolicy Bypass -Scope Process -File .\dev-script.ps1

# ✅ CI/CD 流水线
powershell -ExecutionPolicy Bypass -Scope Process -File .\build.ps1

# ✅ 企业生产环境（优先代码签名而非 Bypass）
# Set-AuthenticodeSignature 签名脚本后执行，使用 RemoteSigned 策略

# ⚠️ 组策略检测（V 阶段 B2 加固）
$lockedPolicies = Get-ExecutionPolicy -List | Where-Object {
    $_.Scope -in 'MachinePolicy', 'UserPolicy' -and $_.ExecutionPolicy -ne 'Undefined'
}
if ($lockedPolicies) {
    Write-Warning "ExecutionPolicy 由组策略锁定: $($lockedPolicies.ExecutionPolicy -join ', ')"
    Write-Warning "请联系 IT 部门请求权限，或使用 -ExecutionPolicy Bypass -Scope Process"
}
```

### 文件: `02-ai-failure-cases.md`

#### 块 #1 (行 21)

- 分类: ⚠️ 反模式/错误示例
- 语法: ❌ 失败
- 错误: `Exception calling "Create" with "1" argument(s): "At line:1 char:14
+ dotnet build && dotnet test
+              ~~
The token '&&' is not a valid statement separator in this version."`
- PS7语法: 管道链与 (&&) （错误演示，预期出现）

```powershell
dotnet build && dotnet test
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #2 (行 27)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
dotnet build; if ($LASTEXITCODE -eq 0) { dotnet test }
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #3 (行 34)

- 分类: ⚠️ 反模式/错误示例
- 语法: ❌ 失败
- 错误: `Exception calling "Create" with "1" argument(s): "At line:1 char:21
+ $status = $hasError ? 'ERROR' : 'OK'
+                     ~
Unexpected token '?' in expression or statement."`

```powershell
$status = $hasError ? 'ERROR' : 'OK'
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #4 (行 40)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
if ($hasError) { $status = 'ERROR' } else { $status = 'OK' }
```

#### 块 #5 (行 47)

- 分类: ⚠️ 反模式/错误示例
- 语法: ❌ 失败
- 错误: `Exception calling "Create" with "1" argument(s): "At line:1 char:19
+ $username = $user ?? "Unknown"
+                   ~~
Unexpected token '??' in expression or statement."`
- PS7语法: 空合并运算符 (??) （错误演示，预期出现）

```powershell
$username = $user ?? "Unknown"
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #6 (行 53)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
$username = if ($null -eq $user) { "Unknown" } else { $user }
```

#### 块 #7 (行 60)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过
- PS7语法: ForEach-Object -Parallel （错误演示，预期出现）

```powershell
1..10 | ForEach-Object -Parallel { Start-Sleep 1; $_ }
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #8 (行 66)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
# 顺序执行（简单场景）
  1..10 | ForEach-Object { Start-Sleep 1; $_ }

  # Start-Job 并行（CLM 兼容，IO 密集型）
  $jobs = 1..10 | ForEach-Object {
      $item = $_
      Start-Job -ScriptBlock { Start-Sleep 1; $using:item }
  }
  $jobs | Wait-Job | Receive-Job; $jobs | Remove-Job
```

#### 块 #9 (行 86)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
$originalOutputEncoding = $OutputEncoding
    $originalConsoleEncoding = [Console]::OutputEncoding
    try {
        $OutputEncoding = [System.Text.Encoding]::UTF8
        [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
        # 业务逻辑
    } finally {
        $OutputEncoding = $originalOutputEncoding
        [Console]::OutputEncoding = $originalConsoleEncoding
    }
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #10 (行 103)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
$home = Join-Path $env:TEMP 'build'
  if (Test-Path $home) { Remove-Item $home -Recurse -Force }
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #11 (行 111)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
$tempBuildHome = Join-Path $env:TEMP 'build'
  if (Test-Path $tempBuildHome) {
      Write-Host "准备删除: $tempBuildHome" -ForegroundColor Yellow
      Remove-Item $tempBuildHome -Recurse -Force
  }
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #12 (行 122)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
Invoke-Expression "Get-Process -Id $ProcId"
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #13 (行 129)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
# 安全：直接调用 cmdlet，利用 PowerShell 参数绑定器
  Get-Process -Id $ProcId

  # 更安全：添加类型约束
  param([Parameter(Mandatory=$true)][int]$ProcId)
  Get-Process -Id $ProcId

  # 如需动态命令，使用 scriptblock 而非字符串
  $command = { param($id) Get-Process -Id $id }
  & $command -Id $ProcId
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #14 (行 145)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
echo "Build → Deploy" > output.txt
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #15 (行 151)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
"Build → Deploy" | Out-File -FilePath output.txt -Encoding utf8
  # 注意：PS5.1 的 -Encoding utf8 是带 BOM 的 UTF-8
```

#### 块 #16 (行 163)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
irm https://example.com/install.ps1 | iex
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #17 (行 170)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
# 安全：先下载到文件检查内容，确认后再执行
  $installScript = Join-Path $env:TEMP 'install.ps1'
  Invoke-RestMethod -Uri https://example.com/install.ps1 -OutFile $installScript
  Get-Content $installScript  # 人工检查内容
  # 确认无误后执行
  powershell -ExecutionPolicy Bypass -Scope Process -File $installScript
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #18 (行 182)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
Invoke-RestMethod -Uri https://api.example.com/data
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #19 (行 189)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
$originalTls = [Net.ServicePointManager]::SecurityProtocol
  try {
      $tls12 = [Net.SecurityProtocolType]::Tls12
      if (($originalTls -band $tls12) -ne $tls12) {
          [Net.ServicePointManager]::SecurityProtocol = $originalTls -bor $tls12
      }
      Invoke-RestMethod -Uri https://api.example.com/data
  } finally {
      [Net.ServicePointManager]::SecurityProtocol = $originalTls
  }
```

#### 块 #20 (行 209)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
# 推荐调用方式（Process 级作用域，不影响其他进程）
  powershell -ExecutionPolicy Bypass -Scope Process -File .\script.ps1

  # 非管理员用户设置（检测组策略锁定后再设置）
  $lockedPolicies = Get-ExecutionPolicy -List | Where-Object {
      $_.Scope -in 'MachinePolicy', 'UserPolicy' -and $_.ExecutionPolicy -ne 'Undefined'
  }
  if (-not $lockedPolicies) {
      Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
  } else {
      Write-Warning "ExecutionPolicy 由组策略锁定，请使用 -ExecutionPolicy Bypass -Scope Process 方式调用"
  }
```

#### 块 #21 (行 227)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
cmd /c "rmdir /s /q "$path""
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #22 (行 233)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
# 使用 PowerShell 原生 Cmdlet 替代 cmd 调用
  Remove-Item -Path $path -Recurse -Force -LiteralPath

  # 如必须调用 cmd，使用 Start-Process 并正确传递参数
  Start-Process -FilePath cmd.exe -ArgumentList "/c rmdir /s /q `"$path`"" -Wait -NoNewWindow
```

#### 块 #23 (行 244)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
workflow Deploy-Servers { ... }
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #24 (行 250)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
# 使用普通 PowerShell 函数 + ForEach-Object/Start-Job 实现
  function Deploy-Servers {
      param([string[]]$servers)
      $servers | ForEach-Object {
          # 部署逻辑
          Write-Host "Deploying to $_"
      }
  }
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #25 (行 267)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
$psPath = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
  # 计划任务操作中使用 $psPath 完整路径
  $action = New-ScheduledTaskAction -Execute $psPath -Argument '-ExecutionPolicy Bypass -Scope Process -File "C:\scripts\task.ps1"'
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #26 (行 276)

- 分类: ⚠️ 反模式/错误示例
- 语法: ❌ 失败
- 错误: `Exception calling "Create" with "1" argument(s): "At line:1 char:38
+ dotnet build --configuration Release && dotnet test --no-build
+                                      ~~
The token '&&' is not a valid statement separator in this version."`
- PS7语法: 管道链与 (&&) （错误演示，预期出现）

```powershell
dotnet build --configuration Release && dotnet test --no-build
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #27 (行 282)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
dotnet build --configuration Release
  if ($LASTEXITCODE -eq 0) { dotnet test --no-build }
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #28 (行 293)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
powershell -ExecutionPolicy Bypass -Scope Process -File .\script.ps1
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #29 (行 304)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
Get-WmiObject -Class Win32_OperatingSystem
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #30 (行 310)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
# CIM cmdlets 在 PS3.0+ 及 PS7 均可用（推荐）
  Get-CimInstance -ClassName Win32_OperatingSystem
```

#### 块 #31 (行 318)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
Import-Module WebAdministration; Get-Website
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #32 (行 324)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
# 检测模块可用性
  if (Get-Module -ListAvailable WebAdministration) {
      Import-Module WebAdministration
      Get-Website
  } elseif (Get-Module -ListAvailable IISAdministration) {
      Import-Module IISAdministration
      # 使用 IISAdministration 模块
  } else {
      throw "IIS 管理模块未安装，请先安装 IIS 管理工具"
  }
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #33 (行 340)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
[Microsoft.Win32.Registry]::SetValue("HKLM:\SOFTWARE\MyApp", "Key", "Value")
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #34 (行 347)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
# 使用 PowerShell 原生 cmdlet（CLM 兼容）
  Set-ItemProperty -Path "HKLM:\SOFTWARE\MyApp" -Name "Key" -Value "Value"
```

#### 块 #35 (行 355)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
Get-ADUser -Filter *
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #36 (行 361)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
if (Get-Module -ListAvailable ActiveDirectory) {
      Import-Module ActiveDirectory
      Get-ADUser -Filter *
  } else {
      throw "ActiveDirectory 模块未安装，请先安装 RSAT-AD-PowerShell 功能"
  }
```

#### 块 #37 (行 373)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
Add-Type -TypeDefinition "public class Win32 { ... }" -Name Win32
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #38 (行 379)

- 分类: 📝 代码片段/伪代码
- 语法: ⏭️ 跳过

```powershell
# 使用 PowerShell 原生方式或预编译签名程序集
  # 用纯 PowerShell 实现相同功能，避免 Add-Type
```

> 说明：不完整片段，跳过语法验证

#### 块 #39 (行 387)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
$excel = New-Object -ComObject Excel.Application
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #40 (行 393)

- 分类: 📝 代码片段/伪代码
- 语法: ⏭️ 跳过

```powershell
# CLM 白名单仅允许三个 COM 对象：
  # - Scripting.Dictionary
  # - Scripting.FileSystemObject
  # - VBScript.RegExp

  # 其他 COM 对象在 CLM 下不可用，需使用原生 cmdlet 替代
  # Excel 自动化建议使用 ImportExcel 模块（如已签名/允许）或 CSV 格式
```

> 说明：不完整片段，跳过语法验证

#### 块 #41 (行 406)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
Get-CimInstance -ClassName Win32_Service -ComputerName $server
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #42 (行 412)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
# 显式创建 CimSession 使用 WinRM 协议
  $cimSession = New-CimSession -ComputerName $server -SessionOption (New-CimSessionOption -Protocol WinRM)
  Get-CimInstance -CimSession $cimSession -ClassName Win32_Service
  Remove-CimSession -CimSession $cimSession
```

#### 块 #43 (行 422)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
class ServerConfig { [string]$Name; [string]$IP }
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #44 (行 428)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
# 使用 PSCustomObject 替代（CLM 兼容）
  [PSCustomObject]@{
      Name = 'server01'
      IP = '192.168.1.1'
  }
```

### 文件: `06-prompt-templates.md`

#### 块 #1 (行 207)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

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

#### 块 #2 (行 231)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

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

#### 块 #3 (行 247)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
$content = Get-Content .\ai-generated-script.ps1 -Raw
if ($content -match '#Requires\s+-Version\s+5\.1') {
    Write-Host "✅ 包含#Requires -Version 5.1声明" -ForegroundColor Green
} else {
    Write-Host "⚠️  建议添加#Requires -Version 5.1" -ForegroundColor Yellow
}
```

### 文件: `07-checklists.md`

#### 块 #1 (行 76)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

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
    @{ Pattern = 'Add-Type'; N
... (截断)
```

### 文件: `08-pitfalls-anti-patterns.md`

#### 块 #1 (行 21)

- 分类: ⚠️ 反模式/错误示例
- 语法: ❌ 失败
- 错误: `Exception calling "Create" with "1" argument(s): "At line:1 char:14
+ dotnet build && dotnet test
+              ~~
The token '&&' is not a valid statement separator in this version."`
- PS7语法: 管道链与 (&&) （错误演示，预期出现）

```powershell
dotnet build && dotnet test
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #2 (行 27)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
dotnet build; if ($?) { dotnet test }
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #3 (行 34)

- 分类: ⚠️ 反模式/错误示例
- 语法: ❌ 失败
- 错误: `Exception calling "Create" with "1" argument(s): "At line:1 char:21
+ $status = $hasError ? 'ERROR' : 'OK'
+                     ~
Unexpected token '?' in expression or statement."`

```powershell
$status = $hasError ? 'ERROR' : 'OK'
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #4 (行 39)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
if ($hasError) { $status = 'ERROR' } else { $status = 'OK' }
```

#### 块 #5 (行 46)

- 分类: ⚠️ 反模式/错误示例
- 语法: ❌ 失败
- 错误: `Exception calling "Create" with "1" argument(s): "At line:1 char:19
+ $username = $user ?? "Unknown"
+                   ~~
Unexpected token '??' in expression or statement."`
- PS7语法: 空合并运算符 (??) （错误演示，预期出现）

```powershell
$username = $user ?? "Unknown"
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #6 (行 51)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
if ($null -eq $user) { $username = "Unknown" } else { $username = $user }
```

#### 块 #7 (行 58)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过
- PS7语法: 空条件运算符 (?.) （错误演示，预期出现）

```powershell
$name = $user?.Name
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #8 (行 63)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
if ($null -ne $user) { $name = $user.Name } else { $name = $null }
```

#### 块 #9 (行 70)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过
- PS7语法: ForEach-Object -Parallel （错误演示，预期出现）

```powershell
1..10 | ForEach-Object -Parallel { Start-Sleep 1; $_ }
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #10 (行 83)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
Get-WmiObject -Class Win32_Process
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #11 (行 88)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
Get-CimInstance -ClassName Win32_Process
```

#### 块 #12 (行 95)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
workflow Backup-Workflow { parallel { ... } }
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #13 (行 104)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
Add-PSSnapin Microsoft.Exchange.Management.PowerShell.SnapIn
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #14 (行 109)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
if (-not (Get-Module -ListAvailable Xxx)) { throw "模块未安装" }
Import-Module Xxx
```

#### 块 #15 (行 117)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
pwsh.exe -File script.ps1
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #16 (行 122)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
& "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -File script.ps1
```

#### 块 #17 (行 133)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
"内容" | Out-File output.txt
"内容" > output.txt
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #18 (行 139)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
"内容" | Out-File -FilePath output.txt -Encoding utf8
```

#### 块 #19 (行 154)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
$original_Tls = [Net.ServicePointManager]::SecurityProtocol
try {
    [Net.ServicePointManager]::SecurityProtocol = $original_Tls -bor [Net.SecurityProtocolType]::Tls12
    # API调用...
} finally {
    [Net.ServicePointManager]::SecurityProtocol = $original_Tls
}
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #20 (行 169)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
$session = New-CimSession -ComputerName $server -SessionOption (New-CimSessionOption -Protocol WinRM)
Get-CimInstance -ClassName Win32_OperatingSystem -CimSession $session
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #21 (行 181)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
Invoke-Expression "Get-Process -Id $ProcId"
iex $commandString
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #22 (行 194)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
irm https://example.com/install.ps1 | iex
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #23 (行 199)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
$tempFile = Join-Path $env:TEMP "install.ps1"
Invoke-RestMethod -Uri https://example.com/install.ps1 -OutFile $tempFile
# Get-Content检查文件内容...
# 确认后执行：& $tempFile
Remove-Item $tempFile -Force
```

#### 块 #24 (行 210)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
Set-ExecutionPolicy Bypass -Scope LocalMachine -Force
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #25 (行 225)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #26 (行 239)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
$HOME = "C:\MyHome"  # 危险！
$PWD = Get-Location
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #27 (行 249)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
$password = ConvertTo-SecureString "P@ssw0rd" -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential("admin", $password)
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #28 (行 263)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
class MyClass { [string]$Name }
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

#### 块 #29 (行 297)

- 分类: ⚠️ 反模式/错误示例
- 语法: ✅ 通过

```powershell
$lockedPolicies = Get-ExecutionPolicy -List | Where-Object {
    $_.Scope -in 'MachinePolicy', 'UserPolicy' -and $_.ExecutionPolicy -ne 'Undefined'
}
if ($lockedPolicies) {
    Write-Warning "ExecutionPolicy由组策略锁定，请联系IT部门或使用 -ExecutionPolicy Bypass -Scope Process"
}
```

> 说明：这是错误/反模式示例，预期可能包含语法错误或展示不推荐写法

### 文件: `09-resources-references.md`

#### 块 #1 (行 93)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
Install-Module PSScriptAnalyzer -Scope CurrentUser -Force
```

#### 块 #2 (行 164)

- 分类: 💻 完整可执行
- 语法: ✅ 通过

```powershell
$env:__PSLockdownPolicy = '4'
   powershell -ExecutionPolicy Bypass -Scope Process -File .\script.ps1
   Remove-Item Env:__PSLockdownPolicy
```

---

## 验证方法说明

1. **语法验证**: 调用 Windows PowerShell 5.1 的 `[scriptblock]::Create()` 进行纯静态语法解析，临时脚本使用 UTF-8 BOM 编码确保中文正确处理，不执行任何代码
2. **智能分类**:
   - 检测代码块前30行的上下文标记（❌/错误/不支持/反模式 vs ✅/正确/推荐/兼容写法）判断是否为错误演示
   - 通过括号平衡、省略标记（`...`）判断代码完整性
3. **PS7+语法检测**:
   - 先移除字符串字面量和注释（避免正则表达式检测脚本中的模式字符串误报）
   - 仅对非错误演示区域的代码报告问题
   - 自动识别语法检测脚本（包含 Pattern/Name/ps7Patterns 的代码块）并豁免
4. **检查项**:
   - 三元运算符 `? :`
   - 空合并/赋值 `??` / `??=`
   - 管道链 `&&` / `||`
   - 空条件 `?.`
   - `ForEach-Object -Parallel`
5. **允许特性**: `Get-WmiObject`、`Add-PSSnapin`、`workflow` 关键字在PS5中可用，不标记为问题