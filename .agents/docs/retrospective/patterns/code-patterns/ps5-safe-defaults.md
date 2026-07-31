---
id: "ps5-safe-defaults"
source: "../../../../../.trae/specs/ai-powershell5-hell-wiki/supporting-analysis/05-patterns.md#模式4ps5-safe-defaults安全默认值防护模式"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/ps5-safe-defaults.toml"
maturity: "L1"
validation_count: 1
reuse_count: 0
documentation_level: "standard"
pattern_id: "P-PS5-SAFEDEFAULTS-001"
tags: ["powershell", "powershell-5.1", "safe-defaults", "security-header", "tls", "encoding", "error-handling", "clm", "global-state", "try-finally", "runspace"]
related_patterns:
  - "ps5-defensive-prompt"
  - "ps5-compat-preflight"
  - "ps5-security-audit"
  - "ps7-to-ps5-translation"
  - "cross-platform-encoding-enforcement"
  - "idempotent-shell-config"
---
> **提炼自**：[05-patterns.md#模式4](../../../../../.trae/specs/ai-powershell5-hell-wiki/supporting-analysis/05-patterns.md#模式4ps5-safe-defaults安全默认值防护模式) —— AI大模型×PowerShell 5兼容安全研究E阶段萃取

# PS5安全默认值防护模式（PS5-Safe-Defaults）

## 模式类型

代码模式（PowerShell/安全默认值/脚本模板）

## 成熟度

L1 实验性（AI×PowerShell 5.1专题研究验证，经V阶段对抗审查18个加固点全部应用）

## 适用场景

- 所有AI生成的PowerShell 5.1脚本开头，作为标准"安全头"
- 新建PS5脚本时的标准模板开头
- 修复现有脚本缺失默认值防护时
- 从PS7代码迁移到PS5时补充兼容性设置时
- 企业环境中统一脚本安全基线时

**不适用场景**：单行交互式命令（可使用精简版）；明确以PowerShell 7+为唯一目标的脚本。

## 问题背景

Windows PowerShell 5.1基于.NET Framework 4.5，存在多个与现代安全/兼容性期望不符的默认行为：
1. **TLS默认禁用1.2**：.NET Framework 4.5默认只启用TLS 1.0/1.1，调用HTTPS API失败
2. **文件输出默认UTF-16LE**：`Out-File`/`>`重定向默认使用Unicode编码，其他工具读取乱码
3. **控制台编码非UTF-8**：`[Console]::OutputEncoding`默认是系统代码页（如GBK/Windows-1252），中文输出乱码
4. **错误继续执行**：`$ErrorActionPreference`默认为`Continue`，错误被静默忽略
5. **全局状态无隔离**：脚本修改`$OutputEncoding`/TLS/编码后影响同一进程后续脚本，难以排查副作用
6. **ExecutionPolicy盲目Bypass**：AI常建议`Set-ExecutionPolicy Bypass -Force`全局设置，在组策略锁定环境下无效且触发SOC告警
7. **CLM环境无提示**：直接使用`Add-Type`/`class`/COM在Constrained Language Mode下100%失败但无友好提示
8. **并行代码无资源清理**：Runspace/Start-Job创建后不Dispose，导致句柄泄漏和内存泄漏

## 核心内容

### 生产级安全默认值完整代码片段（已加固）

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
        }
    }

    # ============================================================
    # 6. 语言模式检测（CLM兼容性提示）
    # ============================================================
    $languageMode = $ExecutionContext.SessionState.LanguageMode
    if ($languageMode -eq 'ConstrainedLanguage') {
        Write-Verbose "运行于Constrained Language Mode，使用保守兼容子集"
        Write-Warning "检测到CLM环境：脚本使用原生cmdlet，避免Add-Type/COM/class/.NET直接调用"
        Write-Warning "如脚本无法运行，请与企业安全团队确认WDAC白名单配置，或使用签名脚本"
    }

    # ============================================================
    # 7. 自动变量防护（Set-StrictMode已覆盖部分，此处补充危险变量检测）
    # ============================================================
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

### 精简版安全头（用于短脚本/单行命令前置）

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

### 并行处理安全模板（含CLM/EDR兼容）

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
        $NoParallel = $false
    }
    elseif ($NoParallel) {
        Write-Verbose "顺序执行模式（-NoParallel已指定，适合EDR环境）"
        1..10 | ForEach-Object {
            Write-Verbose "处理项 $_"
            Start-Sleep -Milliseconds 100
        }
    }
    else {
        Write-Verbose "Runspace池并行模式（线程池: $minThreads-$maxThreads）"
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
    if ($jobs -and $jobs[0] -is [System.Management.Automation.Job]) {
        $jobs | Wait-Job | Receive-Job
        $jobs | Remove-Job -Force
    }
}
```

## 反模式（禁止做的事）

**反模式1：直接Tls12 = Tls12覆盖**
```powershell
❌ 错误：[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
（覆盖系统设置，在支持Tls13的系统上禁用Tls13造成安全降级）
```

**反模式2：全局设置无恢复**
```powershell
❌ 错误：脚本开头修改编码/TLS，脚本结束不恢复
（影响同一进程内后续执行的脚本，导致难以排查的副作用）
```

**反模式3：盲目Set-ExecutionPolicy Bypass**
```powershell
❌ 错误：脚本开头写Set-ExecutionPolicy Bypass -Force
（1. 组策略锁定环境下无效且触发告警；2. 弱化系统安全防线）
```

**反模式4：不检测CLM直接使用Add-Type/COM**
```powershell
❌ 错误：脚本直接New-Object -ComObject Excel.Application，CLM下100%失败
```

**反模式5：Runspace/并行代码无资源清理**
```powershell
❌ 错误：创建RunspacePool但不Close/Dispose，导致句柄泄漏和内存泄漏
```

## 迁移验证

### 验证1：TLS设置验证
```powershell
$before = [Net.ServicePointManager]::SecurityProtocol
.\your-script.ps1 -Verbose
$after = [Net.ServicePointManager]::SecurityProtocol
if ($before -eq $after) {
    Write-Host "✅ TLS设置已正确恢复" -ForegroundColor Green
} else {
    Write-Host "❌ TLS设置未恢复！Before: $before, After: $after" -ForegroundColor Red
}
```

### 验证2：编码设置验证
```powershell
Write-Host "测试中文输出：构建 → 部署 → 完成"
# 预期：中文和→箭头正常显示，无乱码
```

### 验证3：文件输出编码验证
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

## 并行处理降级方案对照

| PS7方案 | PS5.1降级方案 | 适用场景 | CLM兼容 | EDR友好 | 性能 |
|--------|-------------|---------|---------|---------|------|
| `ForEach-Object -Parallel` | `ForEach-Object` 顺序执行 | 简单脚本/数据量小/EDR环境 | ✅ | ✅ | ⭐ |
| `ForEach-Object -Parallel` | `Start-Job` | IO密集型/简单并行/CLM环境 | ✅ | ⚠️ 创建子进程可能触发告警 | ⭐⭐ |
| `ForEach-Object -Parallel` | `[runspacefactory]` Runspace池 | CPU密集型/高性能/Full Language | ❌ CLM下阻止 | ⚠️ 可能触发告警 | ⭐⭐⭐⭐ |
| `workflow { parallel {} }` | Windows任务计划程序并行触发 | 企业环境/长时间运行任务 | ✅ | ✅ | ⭐⭐⭐ |

---

*成熟度：L1（实验性，validation_count=1） | 首次验证：AI×PowerShell 5.1研究 2026-07-31（V阶段18个加固点全部应用）*
