---
id: "ai-powershell5-hell-wiki-02-ai-failure-cases"
title: "三大领域 24 个 AI 失败案例集"
source: "internal:ai-powershell5-research-rfive"
date: "2026-07-31"
category: "learning"
tags: ["powershell", "powershell-5.1", "ai-coding", "failure-cases", "compatibility-errors", "parsererror"]
---

# 三大领域 24 个 AI 失败案例集

本章收录 AI 大模型为 PowerShell 5.1 生成代码时的 24 个典型失败案例，按三大应用领域分组。每个案例包含：AI 生成的典型错误代码、PS5 下实际报错信息、问题描述、PS5 兼容正确写法。所有注入示例已按 V 阶段 S-01 加固要求脱敏。

---

## 领域一：脚本开发辅助（日常脚本兼容性错误）

### 案例 1-1：&& 运算符错误

- **AI 生成典型错误代码**：
  ```powershell
  dotnet build && dotnet test
  ```
- **PS5 下报错**：`ParserError: "标记'&&'不是此版本中的有效语句分隔符"`
- **问题描述**：AI 按 Bash/Linux 语法生成管道链命令，PS5.1 不支持 `&&` 运算符
- **PS5 兼容正确写法**：
  ```powershell
  dotnet build; if ($LASTEXITCODE -eq 0) { dotnet test }
  ```

### 案例 1-2：三元运算符 ? : 错误

- **AI 生成典型错误代码**：
  ```powershell
  $status = $hasError ? 'ERROR' : 'OK'
  ```
- **PS5 下报错**：`ParserError: "表达式或语句中包含意外的标记'?'"; "语句块或类型定义中缺少右'}'"`
- **问题描述**：AI 生成 C#/PS7 风格三元运算符，PS5.1 解析器将 `?` 识别为非法标记
- **PS5 兼容正确写法**：
  ```powershell
  if ($hasError) { $status = 'ERROR' } else { $status = 'OK' }
  ```

### 案例 1-3：空合并运算符 ?? 错误

- **AI 生成典型错误代码**：
  ```powershell
  $username = $user ?? "Unknown"
  ```
- **PS5 下报错**：`ParserError: "意外标记'??'"`
- **问题描述**：AI 生成 PS7+ 空合并运算符，PS5.1 无此语法
- **PS5 兼容正确写法**：
  ```powershell
  $username = if ($null -eq $user) { "Unknown" } else { $user }
  ```

### 案例 1-4：ForEach-Object -Parallel 错误

- **AI 生成典型错误代码**：
  ```powershell
  1..10 | ForEach-Object -Parallel { Start-Sleep 1; $_ }
  ```
- **PS5 下报错**：`ParameterBindingException: "找不到参数"Parallel"的参数"`
- **问题描述**：AI 生成 PS7 并行处理参数，PS5.1 ForEach-Object 无 `-Parallel` 参数集
- **PS5 兼容正确写法**：
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

### 案例 1-5：UTF-8 无 BOM 脚本解析错误

- **AI 生成典型错误代码**：AI Write 工具创建含非 ASCII 字符（如中文、emoji、→ 箭头）的 .ps1 文件，保存为 UTF-8 无 BOM
- **PS5 下报错**：`ParserError: "UnexpectedToken"` 在 Unicode 字符位置；输出乱码如"â†'"替代"→"
- **问题描述**：AI 生成的脚本文件以 UTF-8 无 BOM 保存，PS5.1 按 ANSI 代码页解析含多字节 UTF-8 序列时出现乱码或解析错误
- **PS5 兼容正确写法**：
  - 脚本文件保存为 **UTF-8 with BOM** 格式
  - 脚本开头设置编码：
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
  - 或避免在脚本中直接使用非 ASCII 字符，使用 Unicode 转义序列

### 案例 1-6：$HOME 变量大小写冲突

- **AI 生成典型错误代码**：
  ```powershell
  $home = Join-Path $env:TEMP 'build'
  if (Test-Path $home) { Remove-Item $home -Recurse -Force }
  ```
- **PS5 下报错**：执行 Remove-Item 作用于用户配置文件目录 $HOME，抛出"目录非空"错误或开始删除用户文件
- **问题描述**：AI 声明局部变量 `$home`（小写）覆盖了 PowerShell 内置自动变量 `$HOME`（大小写不敏感），Remove-Item 作用于用户目录
- **V 阶段 S-02 加固**：补充检测方法——使用 `Get-Variable | Where-Object { $_.Options -match 'ReadOnly|Constant' }` 检查只读变量
- **PS5 兼容正确写法**：
  ```powershell
  $tempBuildHome = Join-Path $env:TEMP 'build'
  if (Test-Path $tempBuildHome) {
      Write-Host "准备删除: $tempBuildHome" -ForegroundColor Yellow
      Remove-Item $tempBuildHome -Recurse -Force
  }
  ```

### 案例 1-7：Invoke-Expression 注入漏洞

- **AI 生成典型错误代码**：
  ```powershell
  Invoke-Expression "Get-Process -Id $ProcId"
  ```
- **PS5 下风险**：当 $ProcId 包含 `; <任意恶意命令>` 等注入内容时，额外命令被执行
- **问题描述**：AI 直接使用 Invoke-Expression 拼接字符串，用户输入可注入任意命令
- **V 阶段 S-01/S-03 加固**：注入示例已脱敏；安全最佳实践——**永远不要使用 Invoke-Expression/iex**
- **PS5 兼容正确写法**：
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

### 案例 1-8：输出重定向编码乱码

- **AI 生成典型错误代码**：
  ```powershell
  echo "Build → Deploy" > output.txt
  ```
- **PS5 下实际行为**：output.txt 以 UTF-16LE 编码保存，其他工具按 UTF-8 读取时出现乱码
- **问题描述**：AI 未指定编码，PS5.1 重定向默认 UTF-16LE，PS7 默认 UTF-8
- **PS5 兼容正确写法**：
  ```powershell
  "Build → Deploy" | Out-File -FilePath output.txt -Encoding utf8
  # 注意：PS5.1 的 -Encoding utf8 是带 BOM 的 UTF-8
  ```

---

## 领域二：自动化任务（CI/CD、计划任务、批量部署）

### 案例 2-1：irm | iex 远程脚本执行语法错误

- **AI 生成典型错误代码**：
  ```powershell
  irm https://example.com/install.ps1 | iex
  ```
- **PS5 下报错**：`ParserError: "var关键字不支持"、"缺少右括号"、"'in'关键字报错"` 等 JavaScript 语法错误
- **问题描述**：AI 生成 irm|iex 一行安装命令，网络重定向/拦截场景下下载内容为 HTML 页面而非脚本，PS 解析器尝试解析 HTML/JS
- **V 阶段 S-06 加固**：⚠️ **安全警告**：任何形式的 `curl URL | sh`/`irm URL | iex` 一行下载执行模式都是极度危险的安全反模式
- **PS5 兼容正确写法**：
  ```powershell
  # 安全：先下载到文件检查内容，确认后再执行
  $installScript = Join-Path $env:TEMP 'install.ps1'
  Invoke-RestMethod -Uri https://example.com/install.ps1 -OutFile $installScript
  Get-Content $installScript  # 人工检查内容
  # 确认无误后执行
  powershell -ExecutionPolicy Bypass -Scope Process -File $installScript
  ```

### 案例 2-2：TLS 协议版本不匹配

- **AI 生成典型错误代码**：
  ```powershell
  Invoke-RestMethod -Uri https://api.example.com/data
  ```
- **PS5 下报错**：`WebException: "请求被中止: 未能创建SSL/TLS安全通道"`
- **问题描述**：AI 未设置 TLS 1.2，PS5.1/.NET Framework 4.5 默认可能使用旧 TLS 版本，现代 API 拒绝连接
- **V 阶段 A2/C2 加固**：TLS 设置使用追加模式，保留系统已有协议，不强制覆盖
- **PS5 兼容正确写法**：
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

### 案例 2-3：执行策略阻止脚本运行

- **AI 生成典型错误代码**：脚本直接执行无执行策略设置提示
- **PS5 下报错**：`PSSecurityException: "在此系统上禁止运行脚本"`
- **问题描述**：AI 生成的脚本未考虑 PS 默认执行策略为 Restricted，阻止所有脚本运行
- **V 阶段 A1/B2 加固**：分场景建议，不推荐日常全局 Bypass，优先 -Scope Process
- **PS5 兼容正确写法**：
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

### 案例 2-4：cmd /c 路径转义错误

- **AI 生成典型错误代码**：
  ```powershell
  cmd /c "rmdir /s /q "$path""
  ```
- **PS5 下风险**：路径被截断为单个反斜杠 `\`，被 Windows 解释为当前盘根目录，执行目录删除
- **问题描述**：AI 在 cmd /c 调用中使用反斜杠转义引号，路径变量解析时转义逻辑冲突
- **PS5 兼容正确写法**：
  ```powershell
  # 使用 PowerShell 原生 Cmdlet 替代 cmd 调用
  Remove-Item -Path $path -Recurse -Force -LiteralPath

  # 如必须调用 cmd，使用 Start-Process 并正确传递参数
  Start-Process -FilePath cmd.exe -ArgumentList "/c rmdir /s /q `"$path`"" -Wait -NoNewWindow
  ```

### 案例 2-5：工作流(Workflow)不存在

- **AI 生成典型错误代码**：
  ```powershell
  workflow Deploy-Servers { ... }
  ```
- **PS5 下报错**：PS7 中直接报"workflow 关键字不支持"；PS5.1 精简环境若无 PSWorkflow 模块也报错
- **问题描述**：AI 生成 PowerShell Workflow 代码，PS7 完全移除 Workflow 支持，部分精简 PS5.1 环境无此模块
- **PS5 兼容正确写法**：
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

### 案例 2-6：计划任务 PowerShell 版本不匹配

- **AI 生成典型错误代码**：注册计划任务执行 pwsh.exe 命令，但在仅 PS5.1 环境执行
- **PS5 下报错**：任务计划程序报错"系统找不到指定的文件"；任务启动失败返回 0x1 错误码
- **问题描述**：AI 生成的计划任务配置默认调用 pwsh.exe，纯 Windows 环境可能只有 powershell.exe
- **PS5 兼容正确写法**：
  ```powershell
  $psPath = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
  # 计划任务操作中使用 $psPath 完整路径
  $action = New-ScheduledTaskAction -Execute $psPath -Argument '-ExecutionPolicy Bypass -Scope Process -File "C:\scripts\task.ps1"'
  ```

### 案例 2-7：GitHub Copilot && 语法 CI 命令

- **AI 生成典型错误代码**：
  ```powershell
  dotnet build --configuration Release && dotnet test --no-build
  ```
- **PS5 下报错**：Visual Studio 2022 GitHub Copilot 生成的测试命令在 PS5.1 终端执行失败，标记 `&&` 为无效标记
- **问题描述**：Copilot 默认生成 Bash 风格链式命令，Windows PS5.1 终端不支持
- **PS5 兼容正确写法**：
  ```powershell
  dotnet build --configuration Release
  if ($LASTEXITCODE -eq 0) { dotnet test --no-build }
  ```

### 案例 2-8：CI 中相对路径与执行策略

- **AI 生成典型错误代码**：CI 脚本中直接调用 `.\script.ps1` 无执行策略 bypass
- **PS5 下报错**：CI 服务账户下执行策略为 Restricted 时，脚本完全不执行
- **问题描述**：AI 生成的 CI 脚本未考虑 CI agent 运行账户的执行策略
- **PS5 兼容正确写法**：
  ```powershell
  powershell -ExecutionPolicy Bypass -Scope Process -File .\script.ps1
  ```

---

## 领域三：系统管理（AD 管理、IIS 配置、注册表、WMI/CIM）

### 案例 3-1：Get-WmiObject 在 PS7 中不存在

- **AI 生成典型错误代码**：
  ```powershell
  Get-WmiObject -Class Win32_OperatingSystem
  ```
- **PS5 下行为**：PS5.1 正常执行；PS7 中报 `CommandNotFoundException: "Get-WmiObject不是cmdlet名称"`
- **问题描述**：AI 按旧教程生成 WMI cmdlet，PS7 已完全移除 WMI cmdlets 仅保留 CIM
- **PS5 兼容正确写法**：
  ```powershell
  # CIM cmdlets 在 PS3.0+ 及 PS7 均可用（推荐）
  Get-CimInstance -ClassName Win32_OperatingSystem
  ```

### 案例 3-2：IIS Administration Cmdlets 兼容性

- **AI 生成典型错误代码**：
  ```powershell
  Import-Module WebAdministration; Get-Website
  ```
- **PS5 下报错**：模块未找到错误；在 32 位/64 位 PowerShell 不一致时出现空引用
- **问题描述**：AI 生成 IIS 管理脚本未区分 PS 位数、IIS 版本、模块加载路径
- **PS5 兼容正确写法**：
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

### 案例 3-3：注册表操作 .NET 方法在 CLM 下被阻止

- **AI 生成典型错误代码**：
  ```powershell
  [Microsoft.Win32.Registry]::SetValue("HKLM:\SOFTWARE\MyApp", "Key", "Value")
  ```
- **PS5 下报错**：`ConstrainedLanguage 模式下："Cannot invoke method. Method invocation is supported only on core types in this language mode."`
- **问题描述**：AI 直接调用 .NET Registry 类方法，WDAC/AppLocker 环境下 CLM 阻止非白名单 .NET 类型调用
- **V 阶段 B1 加固**："CLM 兼容"改为"保守兼容"，需在目标环境测试，与企业安全团队确认白名单
- **PS5 兼容正确写法**：
  ```powershell
  # 使用 PowerShell 原生 cmdlet（CLM 兼容）
  Set-ItemProperty -Path "HKLM:\SOFTWARE\MyApp" -Name "Key" -Value "Value"
  ```

### 案例 3-4：Active Directory 模块未检测

- **AI 生成典型错误代码**：
  ```powershell
  Get-ADUser -Filter *
  ```
- **PS5 下报错**：`CommandNotFoundException` 在未安装 RSAT-AD-PowerShell 功能的系统上
- **问题描述**：AI 生成 AD 管理脚本，未检测 ActiveDirectory 模块是否存在
- **PS5 兼容正确写法**：
  ```powershell
  if (Get-Module -ListAvailable ActiveDirectory) {
      Import-Module ActiveDirectory
      Get-ADUser -Filter *
  } else {
      throw "ActiveDirectory 模块未安装，请先安装 RSAT-AD-PowerShell 功能"
  }
  ```

### 案例 3-5：Add-Type C# 编译在 CLM 下被阻止

- **AI 生成典型错误代码**：
  ```powershell
  Add-Type -TypeDefinition "public class Win32 { ... }" -Name Win32
  ```
- **PS5 下报错**：`ConstrainedLanguage 模式下："不允许使用Add-Type"`
- **问题描述**：AI 生成 Add-Type 调用编译 C# 代码，CLM 环境下 Add-Type 被禁用
- **PS5 兼容正确写法**：
  ```powershell
  # 使用 PowerShell 原生方式或预编译签名程序集
  # 用纯 PowerShell 实现相同功能，避免 Add-Type
  ```

### 案例 3-6：COM 对象调用在 CLM 下被阻止

- **AI 生成典型错误代码**：
  ```powershell
  $excel = New-Object -ComObject Excel.Application
  ```
- **PS5 下报错**：`ConstrainedLanguage 模式下："不允许创建COM对象"`
- **问题描述**：AI 生成 COM 对象调用，CLM 白名单外 COM 对象被阻止
- **PS5 兼容正确写法**：
  ```powershell
  # CLM 白名单仅允许三个 COM 对象：
  # - Scripting.Dictionary
  # - Scripting.FileSystemObject
  # - VBScript.RegExp

  # 其他 COM 对象在 CLM 下不可用，需使用原生 cmdlet 替代
  # Excel 自动化建议使用 ImportExcel 模块（如已签名/允许）或 CSV 格式
  ```

### 案例 3-7：CIM Session 协议不兼容

- **AI 生成典型错误代码**：
  ```powershell
  Get-CimInstance -ClassName Win32_Service -ComputerName $server
  ```
- **PS5 下报错**：跨网络/防火墙环境下 DCOM 被阻止，`CimException: "RPC服务器不可用"`
- **问题描述**：AI 生成 CIM 调用使用默认 DCOM 协议，现代环境/PS7 优先使用 WinRM
- **PS5 兼容正确写法**：
  ```powershell
  # 显式创建 CimSession 使用 WinRM 协议
  $cimSession = New-CimSession -ComputerName $server -SessionOption (New-CimSessionOption -Protocol WinRM)
  Get-CimInstance -CimSession $cimSession -ClassName Win32_Service
  Remove-CimSession -CimSession $cimSession
  ```

### 案例 3-8：class 关键字在 CLM 下不允许

- **AI 生成典型错误代码**：
  ```powershell
  class ServerConfig { [string]$Name; [string]$IP }
  ```
- **PS5 下报错**：`ConstrainedLanguage 模式下："不允许使用class关键字"`
- **问题描述**：AI 生成 PS class 定义，CLM 环境下 class 关键字被禁用
- **PS5 兼容正确写法**：
  ```powershell
  # 使用 PSCustomObject 替代（CLM 兼容）
  [PSCustomObject]@{
      Name = 'server01'
      IP = '192.168.1.1'
  }
  ```

---

## 案例根本原因分类统计

| 根本原因分类 | 案例编号 | 数量 | 占比 |
|------------|----------|------|------|
| 语法污染（PS7/Bash/C# 语法迁移） | 1-1,1-2,1-3,1-4,1-6,2-1,2-4,2-7 | 8 | 33.3% |
| API 断层（移除/不存在 API） | 2-5,2-6,3-1,3-2,3-7 | 5 | 20.8% |
| CLM/安全策略阻止 | 2-3,2-8,3-3,3-5,3-6,3-8 | 6 | 25.0% |
| 默认配置冲突（编码/TLS/重定向） | 1-5,1-8,2-2 | 3 | 12.5% |
| 低资源导致最佳实践缺失 | 1-7,3-4 | 2 | 8.3% |

---

**下一章**：[03-first-principles-analysis.md](03-first-principles-analysis.md) — 第一性原理本质矛盾分析，解构两个隐含假设，推导四重断裂结论。
