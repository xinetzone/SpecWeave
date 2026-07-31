---
id: "ps5-security-audit"
source: "../../../../../.trae/specs/ai-powershell5-hell-wiki/supporting-analysis/05-patterns.md#模式3ps5-security-audit安全代码审查checklist模式"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/ps5-security-audit.toml"
maturity: "L1"
validation_count: 1
reuse_count: 0
documentation_level: "standard"
pattern_id: "P-PS5-SECAUDIT-001"
tags: ["powershell", "powershell-5.1", "security-audit", "code-review", "clm", "command-injection", "credential", "execution-policy", "defensive-programming"]
related_patterns:
  - "ps5-defensive-prompt"
  - "ps5-compat-preflight"
  - "ps5-safe-defaults"
  - "command-injection-prevention"
  - "path-traversal-guard"
---
> **提炼自**：[05-patterns.md#模式3](../../../../../.trae/specs/ai-powershell5-hell-wiki/supporting-analysis/05-patterns.md#模式3ps5-security-audit安全代码审查checklist模式) —— AI大模型×PowerShell 5兼容安全研究E阶段萃取

# PS5安全代码审查Checklist模式（PS5-Security-Audit）

## 模式类型

代码模式（PowerShell/安全审查/代码审计）

## 成熟度

L1 实验性（AI×PowerShell 5.1专题研究验证）

## 适用场景

- AI生成PS5脚本后进行安全审查时
- 代码审查（Code Review）阶段进行安全维度检查时
- 脚本上线前的安全审计时
- 接收外部来源脚本（AI/第三方/互联网）后的安全检查时
- 企业安全团队对PowerShell脚本进行合规检查时

**不适用场景**：PowerShell 7+跨平台脚本（部分检查项如CLM/COM/.NET Framework有差异）；完全可信的内部简单脚本可简化审查。

## 问题背景

AI生成PowerShell代码时存在独特的安全风险，这些风险不是因为AI"恶意"，而是因为模型不知道企业环境的安全边界：
1. **CLM兼容性盲区**：AI默认生成Full Language Mode代码（`Add-Type`、`class`、.NET直接调用），在企业Constrained Language Mode环境下100%失败且可能触发EDR告警
2. **命令注入隐患**：AI倾向于使用`Invoke-Expression`（iex）和字符串拼接构造命令，这是PowerShell中最危险的反模式
3. **凭证硬编码**：AI在示例代码中常硬编码密码/API Key，且不提示使用Windows Credential Manager或SecretManagement模块
4. **执行策略误区**：AI常建议`Set-ExecutionPolicy Bypass -Force`全局设置，在组策略锁定环境下无效且触发SOC告警
5. **TLS安全降级**：AI常直接赋值`SecurityProtocol = Tls12`覆盖系统设置，在支持TLS 1.3的系统上造成安全降级
6. **irm|iex下载执行**：AI生成的安装脚本常用`irm https://xxx | iex`一行模式，存在中间人/DNS劫持/CDN入侵风险

## 核心内容

安全审查分为6个维度，每个维度按严重度P0（阻断）/P1（高危）/P2（建议）分级。

### 维度1：CLM/Constrained Language Mode兼容性

| 检查项ID | 检查内容 | 严重度 | 检查方法 | 修复方案 |
|---------|---------|--------|---------|---------|
| SEC-CLM-01 | 是否使用Add-Type？ | P0 | `Select-String -Pattern 'Add-Type'` | 用纯PowerShell重写；或使用预编译签名程序集 |
| SEC-CLM-02 | 是否定义了PowerShell class？ | P0 | `Select-String -Pattern '^\s*class\s+\w+'` | 替换为[PSCustomObject]@{} |
| SEC-CLM-03 | 是否调用非白名单COM对象？ | P0 | 检查New-Object -ComObject参数，白名单仅：Scripting.Dictionary、Scripting.FileSystemObject、VBScript.RegExp | 移除COM调用；或使用白名单内COM；或申请企业WDAC白名单 |
| SEC-CLM-04 | 是否直接调用.NET Framework类型方法？ | P0 | 检查`[Namespace.Class]::Method()`调用，特别是：[Microsoft.Win32.Registry]、[System.Reflection.*]、[System.Runtime.InteropServices.*]等 | 使用PowerShell原生cmdlet替代 |
| SEC-CLM-05 | 是否使用XAML/WPF？ | P1 | `Select-String -Pattern 'XamlReader|System\.Windows'` | CLM下XAML被阻止，考虑使用WinForms或原生主机UI |
| SEC-CLM-06 | 是否有语言模式检测？ | P2 | 检查是否查询`$ExecutionContext.SessionState.LanguageMode` | 在需要Full Language功能时添加检测和友好提示 |

### 维度2：命令注入防护

| 检查项ID | 检查内容 | 严重度 | 检查方法 | 修复方案 |
|---------|---------|--------|---------|---------|
| SEC-INJ-01 | **是否使用Invoke-Expression/iex？** | P0 | `Select-String -Pattern 'Invoke-Expression|\biex\b'`（排除注释） | **永远不要使用**。重构为：1)直接cmdlet调用；2)scriptblock + &调用；3)参数绑定 |
| SEC-INJ-02 | 参数是否有类型约束？ | P0 | 检查param()块参数是否有[string]/[int]等类型约束 | 为所有用户输入参数添加强类型约束 |
| SEC-INJ-03 | 用户输入是否直接拼接进命令？ | P0 | 检查字符串拼接后执行的模式：`"Get-Process $userInput"` | 使用参数绑定：Get-Process -Id $ProcId（参数绑定器自动验证） |
| SEC-INJ-04 | 是否使用irm|iex/Invoke-WebRequest|iex模式？ | P0 | `Select-String -Pattern '\|\s*iex\b'` | 拆分为下载→检查→执行三步；或使用已签名的脚本包 |
| SEC-INJ-05 | 动态命令是否使用scriptblock？ | P1 | 如需动态命令，检查是否使用{ param(...) ... } + &调用 | 如必须动态构造命令，使用scriptblock而非字符串拼接 |
| SEC-INJ-06 | cmd /c或外部进程调用是否有转义问题？ | P1 | 检查cmd/c调用中的引号嵌套和路径变量 | 使用PowerShell原生cmdlet替代cmd.exe调用；使用LiteralPath |

### 维度3：凭证与敏感信息处理

| 检查项ID | 检查内容 | 严重度 | 检查方法 | 修复方案 |
|---------|---------|--------|---------|---------|
| SEC-CRED-01 | 凭证是否硬编码在脚本中？ | P0 | 搜索明文密码/API Key/Token/ConnectionString等模式 | 使用Get-Credential、SecretManagement模块、或DPAPI加密存储 |
| SEC-CRED-02 | 是否使用-credential参数传递明文密码？ | P0 | 检查`ConvertTo-SecureString -AsPlainText -Force`后直接构造PSCredential | 使用Get-Credential交互式获取；或从Windows Credential Manager读取 |
| SEC-CRED-03 | 凭证是否输出到日志/控制台？ | P1 | 检查Write-Host/Out-File/日志中是否输出$credential或密码变量 | 禁止输出凭证对象；日志中对敏感字段打码 |
| SEC-CRED-04 | 临时凭证文件是否安全清理？ | P2 | 检查是否导出凭证到磁盘文件且无清理 | 使用try/finally确保临时凭证文件被安全删除；优先使用内存存储 |
| SEC-CRED-05 | 是否使用SSL/TLS加密传输凭证？ | P1 | 检查HTTP（非HTTPS）端点是否传输凭证 | 所有凭证传输必须使用HTTPS；脚本开头追加TLS 1.2设置 |

### 维度4：执行策略与权限控制

| 检查项ID | 检查内容 | 严重度 | 检查方法 | 修复方案 |
|---------|---------|--------|---------|---------|
| SEC-EP-01 | 是否建议用户全局Bypass执行策略？ | P0 | 搜索`Set-ExecutionPolicy Bypass -Scope LocalMachine`或`-Scope CurrentUser`且无组策略检测 | ⚠️ 安全警告：Bypass仅应在完全信任脚本来源时使用，且推荐`-Scope Process` |
| SEC-EP-02 | 是否检测组策略锁定状态？ | P1 | 检查Set-ExecutionPolicy前是否检测MachinePolicy/UserPolicy | 添加组策略锁定检测，锁定时提示联系IT部门而非盲目设置 |
| SEC-EP-03 | 脚本是否要求管理员权限但无检测？ | P1 | 检查是否有需要提升权限的操作但无#Requires -RunAsAdministrator | 需要管理员权限时添加`#Requires -RunAsAdministrator` |
| SEC-EP-04 | CI脚本是否使用-Scope Process？ | P1 | CI场景中检查-ExecutionPolicy Bypass是否带-Scope Process | CI中始终使用-ExecutionPolicy Bypass -Scope Process，不影响其他进程 |

### 维度5：编码安全与数据保护

| 检查项ID | 检查内容 | 严重度 | 检查方法 | 修复方案 |
|---------|---------|--------|---------|---------|
| SEC-ENC-01 | TLS设置是否正确（追加而非覆盖）？ | P1 | 检查SecurityProtocol赋值是否使用-bor追加而非直接赋值 | 使用P-PS5-SAFEDEFAULTS-001中的追加模式，保留系统已有协议 |
| SEC-ENC-02 | 是否禁用证书验证（-SkipCertificateCheck不存在于PS5）？ | P1 | 检查是否设置`[Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}` | 生产环境不要禁用证书验证；如必须（测试环境）添加明确警示和范围限制 |
| SEC-ENC-03 | 文件输出是否显式指定编码？ | P1 | 检查Out-File/Set-Content是否带-Encoding参数；重定向是否改为显式编码 | 所有文件输出显式指定-Encoding utf8（PS5带BOM） |
| SEC-ENC-04 | 临时文件是否在系统临时目录且安全清理？ | P2 | 检查临时文件是否在$env:TEMP创建，是否用try/finally清理 | 使用Join-Path $env:TEMP创建临时文件，finally中Remove-Item清理 |

### 维度6：安全默认值与防御性编程

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

## 反模式（禁止做的事）

**反模式1：只检查显式恶意代码**
```
❌ 错误：只检查有没有Remove-Item C:\ -Recurse等明显恶意代码
（合法脚本中的Invoke-Expression、硬编码凭证、TLS覆盖等"正常"代码才是主要安全风险）
```

**反模式2："AI生成的代码应该是安全的"**
```
❌ 错误：认为AI训练数据过滤了恶意代码，所以AI生成的代码安全
（AI会生成有安全漏洞的代码——不是因为它恶意，而是因为它不知道安全边界）
```

**反模式3：禁用脚本块日志或AMSI**
```
❌ 错误：为了让脚本"顺利运行"建议用户禁用脚本块日志或AMSI
（这是恶意软件常用的反检测手段，合法脚本永远不应建议禁用安全防护）
```

**反模式4：在脚本中添加隐藏的后门/持久化**
```
❌ 错误：AI生成的脚本中意外包含（或被投毒加入）计划任务持久化、启动项写入等代码
（审查时必须检查所有非预期的系统修改操作）
```

## 迁移验证

### 验证方法1：使用PSScriptAnalyzer官方规则
```powershell
# 安装PSScriptAnalyzer（如未安装）
Install-Module PSScriptAnalyzer -Scope CurrentUser -Force

# 运行安全相关规则扫描
Invoke-ScriptAnalyzer -Path .\your-script.ps1 -IncludeRule PSAvoidUsingInvokeExpression,PSAvoidUsingPlainTextForPassword,PSUsePSCredentialType,PSAvoidUsingUsernameAndPasswordParams,PSAvoidUsingInternalURLs
```

### 验证方法2：执行AmsiScanBuffer测试（企业环境）
```powershell
# 确保AMSI集成启用（默认启用），脚本应能正常被AMSI扫描
# 如脚本触发AMSI告警，说明存在可疑特征需要审查
```

### 验证方法3：安全审查Checklist验证
人工逐项过本模式Checklist，填写评分模板，P0问题数=0方为通过。

---

*成熟度：L1（实验性，validation_count=1） | 首次验证：AI×PowerShell 5.1研究 2026-07-31*
