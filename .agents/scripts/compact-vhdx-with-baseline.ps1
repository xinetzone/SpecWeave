#!/usr/bin/env pwsh
#Requires -Version 7.4
<#
.SYNOPSIS
  SpecWeave · WSL2 VHDX 基线 → fstrim → wsl --shutdown → 原生 compact → 双基线复测 → 恢复原态 的 8 步原子脚本。
  对应 Skill: .agents/skills/wsl-vhdx-compact-cmd/SKILL.md
.DESCRIPTION
  输出：pipeline 友好对象（BeforeVhdxGiB / AfterVhdxGiB / SavedVhdxGiB / BeforeFreeGiB / AfterFreeGiB / DeltaHostFreeGiB / FstrimSummary / OriginalStates / DegradedToAdminScript / ExitCode）。
  验收依据：只信数值 + ExitCode；绝不解析 wsl.exe 的 UTF-16 stdout 文本。
.NOTES
  历史踩坑（见 SKILL.md Gotchas 8 条）：
    - wsl --shutdown 是全局命令，会关停所有发行版 → 必须先快照原态后按 RestoreOriginalState/RestorePodman 恢复
    - Trae 沙箱 Remove-Item 只进回收站 → 本脚本不提供删文件能力，避免用户误以为"释放了空间"
    - wsl.exe 输出 UTF-16 LE，常带 � 乱码 → 用 ExitCode + Get-Item/CimInstance 数值
    - podman-machine-default 正确恢复是 podman machine start，不是 wsl -d ...
    - PCMClawUbuntu 永远别碰 → 硬匹配 ABORT
.EXAMPLE
  # 0 只读基线（推荐先跑）
  .\compact-vhdx-with-baseline.ps1 -Distro podman-machine-default -DriveLetter D -BaselineOnly

  # 1 podman 默认发行版（原态 Running）：compact 后自动恢复 podman machine start
  .\compact-vhdx-with-baseline.ps1 -Distro podman-machine-default -DriveLetter D -RestorePodman

  # 2 openKylin（原态 Stopped，自定义 D:\WSL\<x>\ext4.vhdx）：只按原态保持 Stopped
  .\compact-vhdx-with-baseline.ps1 -Distro openKylin-3.0-desktop -DriveLetter D -VhdxPath "D:\WSL\openKylin-3.0-desktop\ext4.vhdx" -RestoreOriginalState
#>

[CmdletBinding(SupportsShouldProcess = $false)]
param(
  [Parameter(Mandatory = $false)][string]$Distro,
  [Parameter(Mandatory = $false)][string]$VhdxPath,
  [Parameter(Mandatory = $false)][string[]]$Mounts = @('/', '/home', '/workspace'),
  [Parameter(Mandatory = $false)][char]$DriveLetter = "`0",
  [Parameter(Mandatory = $false)][switch]$BaselineOnly,
  [Parameter(Mandatory = $false)][switch]$SkipFstrim,
  [Parameter(Mandatory = $false)][switch]$RestoreOriginalState,
  [Parameter(Mandatory = $false)][switch]$RestorePodman,
  [Parameter(Mandatory = $false)][switch]$JsonOnly,
  [Parameter(Mandatory = $false)][string]$JsonOutFile
)

$ErrorActionPreference = 'Continue'
$nl = [Environment]::NewLine
$ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'

# ----------------------------------------------------------------------
# 工具函数
# ----------------------------------------------------------------------
function private:GiB([decimal]$x) { [math]::Round($x / 1GB, 2) }
function private:Write-Step([string]$msg) { Write-Host "$nl== [$ts] $msg ==" -ForegroundColor Cyan }
function private:Write-Warn([string]$msg) { Write-Host "WARN: $msg" -ForegroundColor Yellow }
function private:Write-Err([string]$msg) { Write-Host "ERR : $msg" -ForegroundColor Red }

# 把 JSON 结果写到 JsonOutFile（在任何 exit 前调）——解决 BaselineOnly 先 exit 导致落盘丢失
function private:Write-JsonOutIfNeeded {
  param([Parameter(Mandatory = $true)][hashtable]$Result,
        [Parameter(Mandatory = $false)][string]$OutPath)
  if ([string]::IsNullOrWhiteSpace($OutPath)) { return }
  try {
    $resolved = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutPath)
    $dir = Split-Path -Parent $resolved
    if (-not [string]::IsNullOrWhiteSpace($dir) -and -not (Test-Path -LiteralPath $dir)) {
      New-Item -ItemType Directory -Path $dir -Force -ErrorAction Stop | Out-Null
    }
    $payload = ([pscustomobject]$Result) | ConvertTo-Json -Depth 5 -Compress
    [System.IO.File]::WriteAllText($resolved, $payload, [System.Text.Encoding]::UTF8)
    if (-not (Test-Path -LiteralPath $resolved)) {
      Set-Content -LiteralPath $resolved -Value $payload -Encoding utf8NoBOM -Force
    }
  }
  catch {
    Write-Warn "写 JsonOutFile=$OutPath 失败：$($_.Exception.Message)"
  }
}

# 取 WSL 状态：UTF-16 LE 解码 wsl.exe 输出（从根源消 null 字节）
function private:Get-WslStates {
  [CmdletBinding()]
  param()
  # 1) 优先：独立 Process + Unicode(UTF-16LE) 显式解码，避免 PowerShell 内置 & 机制的编码猜测
  $raw = $null
  try {
    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName               = 'wsl.exe'
    $psi.Arguments              = '-l -v'
    $psi.RedirectStandardOutput = $true
    $psi.StandardOutputEncoding = [System.Text.Encoding]::Unicode
    $psi.UseShellExecute        = $false
    $psi.CreateNoWindow         = $true
    $p = [System.Diagnostics.Process]::Start($psi)
    if ($null -ne $p) {
      $raw = $p.StandardOutput.ReadToEnd()
      [void]$p.WaitForExit(5000)
      if (-not $p.HasExited) { try { $p.Kill() } catch {} }
    }
  }
  catch {
    # 2) Fallback：消 null 字节的老路（wsl -l -v 重定向偶尔会出现 0x00 间隙）
    $lines = @(& wsl.exe -l -v 2>$null) -join "`n"
    $raw   = $lines -replace "`0", ''
  }
  if ([string]::IsNullOrWhiteSpace($raw)) { return ,@() }

  # 3) 按行切分，跳过空行/纯表头
  $rows = [System.Collections.Generic.List[object]]::new()
  foreach ($ln in ($raw -split "`r?`n")) {
    $t = ($ln ?? '').Trim()
    if ([string]::IsNullOrWhiteSpace($t)) { continue }
    # 跳过表头（NAME STATE VERSION）
    if ($t -match '^\*?\s*NAME\s+STATE\s+VERSION\s*$') { continue }
    # 必须出现 Running / Stopped（否则是中文环境表头、错误信息等）
    if ($t -notmatch 'Running|Stopped') { continue }

    # 4) Running/Stopped 位置锚定切分：NAME=之前 / STATE=匹配 / VERSION=之后第一个 token
    $m = [regex]::Match($t, '(?<state>Running|Stopped)', [System.Text.RegularExpressions.RegexOptions]::None)
    if (-not $m.Success) { continue }
    $state  = $m.Groups['state'].Value
    $before = $t.Substring(0, $m.Index).Trim()
    $after  = $t.Substring($m.Index + $m.Length).Trim()

    # IsDefault 只看行首是否为 *（before 段末尾不带 *）
    $isDefault = $false
    if ($before -match '^\*\s*(?<rest>.*)$') { $isDefault = $true; $before = $Matches['rest'].Trim() }

    # 第一个 token 就是 VERSION（=WSL 1/2）；剩下的 after 内容忽略
    $ver = if ($after -match '^\s*(?<v>[0-9]+)\b') { $Matches['v'] } else { $null }
    if ([string]::IsNullOrWhiteSpace($before) -or
        [string]::IsNullOrWhiteSpace($state)  -or
        [string]::IsNullOrWhiteSpace($ver)) {
      continue
    }
    # NAME 可能含空格（Ubuntu 24.04 LTS / podman-machine-default / openKylin-3.0-desktop），直接保留 before 段本体
    $rows.Add([pscustomobject]@{
      Name      = $before
      State     = $state
      Version   = $ver
      IsDefault = $isDefault
    })
  }
  return ,$rows.ToArray()
}

# 从注册表猜 ext4.vhdx 路径
function private:Infer-VhdxPath([string]$d) {
  $items = Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss\*" -ErrorAction SilentlyContinue
  foreach ($it in $items) {
    if ($it.DistributionName -eq $d) {
      $candidate = Join-Path $it.BasePath 'ext4.vhdx'
      if (Test-Path $candidate) { return $candidate }
      return (Join-Path $it.BasePath 'ext4.vhdx')
    }
  }
  return $null
}

# ----------------------------------------------------------------------
# 参数校验
# ----------------------------------------------------------------------
if ([string]::IsNullOrWhiteSpace($Distro) -and [string]::IsNullOrWhiteSpace($VhdxPath)) {
  throw "ERR: -Distro 与 -VhdxPath 至少填一项"
}

# Gotcha7：PCMClawUbuntu 永远黑名单
if ($Distro -match '^PCMClawUbuntu$') {
  throw "ERR: Distro=PCMClawUbuntu 属于管家自管理发行版，本技能禁止操作（Gotcha7）。"
}

# 推断 VhdxPath
if ([string]::IsNullOrWhiteSpace($VhdxPath)) {
  $VhdxPath = Infer-VhdxPath $Distro
  if ([string]::IsNullOrWhiteSpace($VhdxPath)) {
    throw "ERR: 无法从注册表推断 Distro=$Distro 的 VHDX 路径，请显式传 -VhdxPath 'D:\WSL\xxx\ext4.vhdx'"
  }
  Write-Host "INF : 推断 VhdxPath=$VhdxPath"
}

# 推断 DriveLetter
if ($DriveLetter -eq "`0") {
  $root = Split-Path -Qualifier $VhdxPath
  if ($root -match '^([A-Za-z]):\\?$') { $DriveLetter = [char]::ToUpper($Matches[1][0]) }
  else { throw "ERR: VhdxPath=$VhdxPath 不含盘符，必须显式传 -DriveLetter D" }
}

# 结果对象骨架
$r = [ordered]@{
  Distro                = if ([string]::IsNullOrWhiteSpace($Distro)) { "<from path>" } else { $Distro }
  VhdxPath              = $VhdxPath
  DriveLetter           = $DriveLetter
  Mode                  = if ($BaselineOnly) { 'BaselineOnly' } else { 'FullCompact' }
  BeforeVhdxGiB         = $null
  AfterVhdxGiB          = $null
  SavedVhdxGiB          = $null
  BeforeFreeGiB         = $null
  AfterFreeGiB          = $null
  DeltaHostFreeGiB      = $null
  FstrimSummary         = @()
  OriginalStates        = @()
  RestoredStates        = @()
  DegradedToAdminScript = $null
  ExitCode              = -1
}

# ----------------------------------------------------------------------
# 1. 发行版合法性 + 原态快照
# ----------------------------------------------------------------------
Write-Step '1/8 发行版状态快照（wsl -l -v，消 UTF-16 null 字节）'
$states = Get-WslStates
$r.OriginalStates = $states
$states | Format-Table -AutoSize | Out-Host

if (-not [string]::IsNullOrWhiteSpace($Distro)) {
  $hit = $states | Where-Object { $_.Name -eq $Distro }
  if (-not $hit) {
    Write-Err "Distro=$Distro 不存在，可用发行版：$($states.Name -join '、')"
    $r.ExitCode = 2
    [pscustomobject]$r
    exit 2
  }
}

# ----------------------------------------------------------------------
# 2+3. Before 宿主盘 FreeGiB + VHDX Length
# ----------------------------------------------------------------------
Write-Step '2/8 Before 宿主盘 FreeGiB（Win32_LogicalDisk，唯一权威）'
$beforeDisk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='$($DriveLetter):'" | Select-Object DeviceID, Size, FreeSpace
if (-not $beforeDisk) {
  Write-Err "找不到 DriveLetter=$DriveLetter 的逻辑盘"
  $r.ExitCode = 3
  Write-JsonOutIfNeeded -Result $r -OutPath $JsonOutFile
  [pscustomobject]$r; exit 3
}
$r.BeforeFreeGiB = GiB $beforeDisk.FreeSpace
$beforeDisk | Select-Object DeviceID,
  @{n = 'SizeGiB';  e = { [math]::Round($_.Size / 1GB, 2) } },
  @{n = 'FreeGiB';  e = { [math]::Round($_.FreeSpace / 1GB, 2) } },
  @{n = 'FreePct';  e = { [math]::Round(100 * $_.FreeSpace / $_.Size, 2) } } |
  Format-List | Out-Host

Write-Step '3/8 Before VHDX Length（Get-Item -Force，唯一权威）'
if (-not (Test-Path $VhdxPath)) {
  Write-Err "VhdxPath=$VhdxPath 不存在"
  $r.ExitCode = 4
  Write-JsonOutIfNeeded -Result $r -OutPath $JsonOutFile
  [pscustomobject]$r; exit 4
}
$beforeFile = Get-Item $VhdxPath -Force
$r.BeforeVhdxGiB = GiB $beforeFile.Length
$beforeFile | Select-Object FullName,
  @{n = 'LengthGiB'; e = { [math]::Round($_.Length / 1GB, 2) } },
  LastWriteTime | Format-List | Out-Host

# ----------------------------------------------------------------------
# BaselineOnly 提前退出
# ----------------------------------------------------------------------
if ($BaselineOnly) {
  Write-Step 'BaselineOnly：在进行任何写操作（fstrim / shutdown / compact）前返回，零副作用。'
  $r.ExitCode = 0
  Write-JsonOutIfNeeded -Result $r -OutPath $JsonOutFile
  if ($JsonOnly) {
    [Console]::Out.WriteLine(([pscustomobject]$r | ConvertTo-Json -Depth 5 -Compress))
  } else {
    [pscustomobject]$r
  }
  exit 0
}

# ----------------------------------------------------------------------
# 4. Linux 内 fstrim
# ----------------------------------------------------------------------
Write-Step "4/8 Linux 内 fstrim（SkipFstrim=$SkipFstrim，Mounts=$($Mounts -join ','))"
$fstrimPassed = $false
if (-not $SkipFstrim -and -not [string]::IsNullOrWhiteSpace($Distro)) {
  $linesAll = @()
  try {
    $out = & wsl.exe -d $Distro -u root -- bash -lc "/sbin/fstrim -Av 2>&1 ; echo FSTRIM_DONE=\$?" 2>&1
    $linesAll = @($out) -join "`n" -replace "`0", '' -split "`r?`n" | Where-Object { $_ -match '\S' }
    if ($linesAll -match 'FSTRIM_DONE=0') { $fstrimPassed = $true }
    $r.FstrimSummary = @($linesAll | Where-Object { $_ -match 'trimmed|bytes|FSTRIM_DONE' })
  }
  catch {
    Write-Warn "fstrim -Av 失败（$($_.Exception.Message)），退回逐个挂载点"
  }

  if (-not $fstrimPassed) {
    $r.FstrimSummary = @()
    foreach ($m in $Mounts) {
      try {
        $o = & wsl.exe -d $Distro -u root -- bash -lc "/sbin/fstrim -v '$m' 2>&1 ; echo M_DONE=\$?" 2>&1
        $clean = @($o) -join "`n" -replace "`0", ''
        $r.FstrimSummary += $clean -split "`r?`n" | Where-Object { $_ -match '\S' }
      }
      catch { Write-Warn "fstrim $m 跳过：$($_.Exception.Message)" }
    }
    $fstrimPassed = $r.FstrimSummary.Count -gt 0
  }

  if ($r.FstrimSummary.Count) { Write-Host ($r.FstrimSummary -join $nl) }
  if (-not $fstrimPassed) { Write-Warn "fstrim 全失败；如果 Distro 无法启动，请加 -SkipFstrim" }
}
else {
  Write-Host "SKIP: SkipFstrim=$SkipFstrim 或 Distro 未填"
}

# ----------------------------------------------------------------------
# 5. wsl --shutdown（⚠️ 全局关停）
# ----------------------------------------------------------------------
Write-Step '5/8 wsl --shutdown（⚠️ 所有发行版会停；最多轮询 15 秒全 Stopped）'
& wsl.exe --shutdown
$deadline = (Get-Date).AddSeconds(15)
do {
  Start-Sleep -Seconds 2
  $st = Get-WslStates
  $stillRun = @($st | Where-Object { $_.State -ne 'Stopped' })
  if ($stillRun.Count -eq 0) { break }
} while ((Get-Date) -lt $deadline)
$st = Get-WslStates
$stillRun = @($st | Where-Object { $_.State -ne 'Stopped' })
if ($stillRun.Count -gt 0) {
  Write-Warn "以下发行版 shutdown 15 秒后仍非 Stopped：$($stillRun.Name -join '、')；考虑手动 Stop-Process -Name wsl,wslhost -Force（管理员）"
}
else { Write-Host 'OK  : 所有发行版已 Stopped' }

# ----------------------------------------------------------------------
# 6. 原生 compact
# ----------------------------------------------------------------------
Write-Step '6/8 原生 wsl --manage --compact（只信 ExitCode，绝不信 stdout 乱码）'
$nativeOk = $false
if (-not [string]::IsNullOrWhiteSpace($Distro)) {
  $out = & wsl.exe --manage $Distro --compact 2>&1
  $ec = $LASTEXITCODE
  Write-Host "wsl --manage $Distro --compact ExitCode=$ec"
  if ($ec -eq 0) { $nativeOk = $true }
  else { Write-Warn "原生 compact ExitCode=$ec，将降级到管理员 compress-wsl-vhdx.ps1（方案B）" }
}
else {
  Write-Warn "未传 Distro，跳过原生 compact；如需走方案B 请手动执行下面 DegradedToAdminScript"
}

if (-not $nativeOk) {
  $scriptResolved = Join-Path $PSScriptRoot 'compress-wsl-vhdx.ps1'
  $r.DegradedToAdminScript = @"
# ====== 请在 TRAE 外的独立管理员 PowerShell 7 窗口执行 ======
pwsh -File "$scriptResolved" -DistroName "$($r.Distro)" -VhdxPath "$VhdxPath" $(if ($SkipFstrim -or -not $fstrimPassed) { '-SkipFstrim' })
# ====== 然后回到本脚本的脚本目录跑一次 BaselineOnly 对比 ======
# pwsh -File "$PSCommandPath" -Distro "$($r.Distro)" -DriveLetter $DriveLetter -VhdxPath "$VhdxPath" -BaselineOnly
"@
}

# ----------------------------------------------------------------------
# 7. After 双基线复测
# ----------------------------------------------------------------------
Write-Step '7/8 After 双基线复测（宿主 FreeGiB + VHDX Length）'
$afterDisk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='$($DriveLetter):'" | Select-Object DeviceID, Size, FreeSpace
$r.AfterFreeGiB = if ($afterDisk) { GiB $afterDisk.FreeSpace } else { $null }
if ($afterDisk) {
  $afterDisk | Select-Object DeviceID,
    @{n = 'SizeGiB'; e = { [math]::Round($_.Size / 1GB, 2) } },
    @{n = 'FreeGiB'; e = { [math]::Round($_.FreeSpace / 1GB, 2) } },
    @{n = 'FreePct'; e = { [math]::Round(100 * $_.FreeSpace / $_.Size, 2) } } |
    Format-List | Out-Host
}
$afterFile = if (Test-Path $VhdxPath) { Get-Item $VhdxPath -Force } else { $null }
$r.AfterVhdxGiB = if ($afterFile) { GiB $afterFile.Length } else { $null }
if ($afterFile) {
  $afterFile | Select-Object FullName,
    @{n = 'LengthGiB'; e = { [math]::Round($_.Length / 1GB, 2) } },
    LastWriteTime | Format-List | Out-Host
}

$r.SavedVhdxGiB = if ($null -ne $r.BeforeVhdxGiB -and $null -ne $r.AfterVhdxGiB) { [math]::Round(($r.BeforeVhdxGiB - $r.AfterVhdxGiB), 2) } else { $null }
$r.DeltaHostFreeGiB = if ($null -ne $r.BeforeFreeGiB -and $null -ne $r.AfterFreeGiB) { [math]::Round(($r.AfterFreeGiB - $r.BeforeFreeGiB), 2) } else { $null }

# 警告：油水小
if ($r.SavedVhdxGiB -le 0 -and $r.DeltaHostFreeGiB -le 0.05) {
  Write-Warn "VHDX 与宿主盘几乎 0 变化。可能原因：1) df Used 已接近 VHDX Length，没油水；2) 其他进程在 shutdown→compact 期间写入了该盘；3) 原生 compact 失败，需要 DegradeToAdminScript（管理员模式）。"
}

# ----------------------------------------------------------------------
# 8. 按原态恢复（RestoreOriginalState / RestorePodman）
# ----------------------------------------------------------------------
Write-Step "8/8 恢复原态（RestoreOriginalState=$RestoreOriginalState, RestorePodman=$RestorePodman）"
$restored = @()

# podman 优先（Gotcha4：podman 必须用 podman machine start）
$podmanBefore = $r.OriginalStates | Where-Object { $_.Name -eq 'podman-machine-default' -and $_.State -eq 'Running' }
$needRestorePodman = [bool]$RestorePodman -or [bool]($RestoreOriginalState -and $podmanBefore)
if ($needRestorePodman) {
  Write-Host "INF : 调用 podman machine start（幂等）"
  $pmOut = & podman.exe machine start 2>&1
  $pmEc = $LASTEXITCODE
  Write-Host ($pmOut -join $nl)
  if ($pmEc -ne 0) { Write-Warn "podman machine start ExitCode=$pmEc" }
  $restored += [pscustomobject]@{Name = 'podman-machine-default'; Via = 'podman machine start'; ExitCode = $pmEc }
}

# 其他原态 Running 的发行版，按 RestoreOriginalState 开关唤醒（用 wsl -d xxx echo ready）
if ($RestoreOriginalState) {
  foreach ($s in $r.OriginalStates) {
    if ($s.State -ne 'Running') { continue }
    if ($s.Name -eq 'podman-machine-default' -and $needRestorePodman) { continue } # 已处理
    Write-Host "INF : 唤醒原态 Running 的 $($s.Name) → wsl -d $($s.Name) echo ready"
    $null = & wsl.exe -d $s.Name -- echo "ready"
    $restored += [pscustomobject]@{Name = $s.Name; Via = 'wsl -d <name> echo ready'; ExitCode = $LASTEXITCODE }
  }
}

# 最终状态快照
$r.RestoredStates = $restored
Write-Host "$nl-- 最终状态（$($ts)）--"
Get-WslStates | Format-Table -AutoSize | Out-Host

# ----------------------------------------------------------------------
# 结果表 + 最终 ExitCode
# ----------------------------------------------------------------------
Write-Step '结果汇总表（可直接粘贴到回复）'
$md = @"
| 指标 | Before | After | Δ（Saved/Delta） |
|---|---:|---:|---:|
| VHDX Length（GiB） | {0} | {1} | **{2}** |
| $($DriveLetter): FreeGiB | {3} | {4} | **{5}** |
| compact 通道 | Native= {6} | 降级脚本生成？ {7} | — |
| 恢复动作数（原态） | — | {8} | 列表见 RestoredStates |
"@ -f $r.BeforeVhdxGiB, $r.AfterVhdxGiB, $r.SavedVhdxGiB,
  $r.BeforeFreeGiB, $r.AfterFreeGiB, $r.DeltaHostFreeGiB,
  $nativeOk, ($null -ne $r.DegradedToAdminScript), $restored.Count
Write-Host $md

if (-not [string]::IsNullOrWhiteSpace($r.DegradedToAdminScript)) {
  Write-Host "$nl-- 降级管理员命令（复制到 Trae 外独立管理员 pwsh 7 窗口）--" -ForegroundColor Yellow
  Write-Host $r.DegradedToAdminScript
}

$r.ExitCode = if ($nativeOk -or $null -ne $r.DegradedToAdminScript) { 0 } else { 1 }

Write-JsonOutIfNeeded -Result $r -OutPath $JsonOutFile
$jsonPayload = [pscustomobject]$r | ConvertTo-Json -Depth 5 -Compress
if ($JsonOnly) {
  [Console]::Out.WriteLine($jsonPayload)
  exit ([int]$r.ExitCode)
}
[pscustomobject]$r
exit ([int]$r.ExitCode)

