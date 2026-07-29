#Requires -Version 5.1
<#
.SYNOPSIS
    Clean up Trae IDE cache and index database to free disk space
.DESCRIPTION
    Safely clean index cache, log files, and temporary data for Trae/Trae CN/TRAE SOLO/Qoder.
    Will NOT delete user settings, keybindings, snippets, chat history, or other important data.
    Automatically detects running processes and prompts to close them first.
    Supports DryRun preview mode.
.PARAMETER DryRun
    Preview what will be cleaned without actually deleting anything
.PARAMETER Force
    Skip user confirmation prompts
.PARAMETER IncludeAllVersions
    Clean all Trae variants (Trae, Trae CN, TRAE SOLO, TRAE SOLO CN, Qoder)
.EXAMPLE
    .\cleanup-trae-cache.ps1 -DryRun
    Preview space that can be freed
.EXAMPLE
    .\cleanup-trae-cache.ps1
    Run cleanup (only the largest detected variant by default)
.EXAMPLE
    .\cleanup-trae-cache.ps1 -IncludeAllVersions
    Clean cache for all Trae variants
.NOTES
    Safety: Only deletes cache/index/logs, preserves user config and data
#>

param(
    [switch]$DryRun,
    [switch]$Force,
    [switch]$IncludeAllVersions
)

$ErrorActionPreference = 'Continue'

$roamingPath = $env:APPDATA
$localPath = $env:LOCALAPPDATA

$traeVariants = [ordered]@{
    'Trae'          = 'Trae'
    'Trae CN'       = 'Trae CN'
    'TRAE SOLO'     = 'TRAE SOLO'
    'TRAE SOLO CN'  = 'TRAE SOLO CN'
    'Qoder'         = 'Qoder'
}

$safeCleanupTargets = [ordered]@{
    'User\globalStorage\.ckg'                    = 'Code index database (.ckg, will rebuild)'
    'logs'                                       = 'Log files'
    'monitor'                                    = 'Process monitor logs'
    'Cache'                                      = 'General cache'
    'CachedData'                                 = 'Cached data'
    'CachedExtensionVSIXs'                       = 'Extension VSIX cache'
    'GPUCache'                                   = 'GPU render cache'
    'WebStorage'                                 = 'Web storage cache'
    'VideoDecodeStats'                           = 'Video decode stats'
    'shared_proto_db'                            = 'Protocol cache DB'
    'Partitions\cache'                           = 'Partitions cache'
    'aha'                                        = 'Temporary data'
    'SharedClientCache'                          = 'Qoder shared client cache'
}

$localCleanupTargets = [ordered]@{
    'Trae'                                       = 'Trae local cache'
    'Trae CN'                                    = 'Trae CN local cache'
    'TRAE SOLO'                                  = 'TRAE SOLO local cache'
    'TRAE SOLO CN'                               = 'TRAE SOLO CN local cache'
    'qoder'                                      = 'Qoder local cache'
}

$protectedPaths = @(
    'User\settings.json',
    'User\keybindings.json',
    'User\snippets',
    'User\globalStorage\state.vscdb',
    'User\globalStorage\storage.json',
    'extensions',
    'Workspaces'
)

function Get-DirectorySize {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return 0 }
    try {
        $files = Get-ChildItem -LiteralPath $Path -Recurse -Force -File -ErrorAction SilentlyContinue
        return ($files | Measure-Object -Property Length -Sum).Sum
    }
    catch { return 0 }
}

function Format-Size {
    param([long]$Bytes)
    if ($Bytes -ge 1GB) { return "$([math]::Round($Bytes/1GB,2)) GB" }
    if ($Bytes -ge 1MB) { return "$([math]::Round($Bytes/1MB,2)) MB" }
    if ($Bytes -ge 1KB) { return "$([math]::Round($Bytes/1KB,2)) KB" }
    return "$Bytes B"
}

function Test-TraeProcesses {
    $processNames = @('Trae', 'Trae CN', 'TRAE SOLO', 'TRAE SOLO CN', 'Qoder', 'trae-sandbox')
    $running = @()
    foreach ($p in (Get-Process -ErrorAction SilentlyContinue)) {
        foreach ($name in $processNames) {
            if ($p.Name -eq $name -or $p.Name -like "*$name*") {
                $running += [PSCustomObject]@{Name=$p.Name; Id=$p.Id}
                break
            }
        }
    }
    return $running | Sort-Object Name -Unique
}

function Get-VariantPath {
    param([string]$VariantName)
    return Join-Path $roamingPath $VariantName
}

function Get-CleanupPlan {
    param([string]$BasePath, [hashtable]$Targets)
    $plan = @()
    foreach ($entry in $Targets.GetEnumerator()) {
        $fullPath = Join-Path $BasePath $entry.Key
        if (Test-Path $fullPath) {
            $size = Get-DirectorySize $fullPath
            if ($size -gt 0) {
                $plan += [PSCustomObject]@{
                    Path = $fullPath
                    RelativePath = $entry.Key
                    Description = $entry.Value
                    Size = $size
                }
            }
        }
    }
    return $plan
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Trae IDE Cache Cleanup Tool" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[Check] Detecting running Trae processes..." -ForegroundColor Yellow
$runningProcs = Test-TraeProcesses
if ($runningProcs.Count -gt 0) {
    Write-Host ""
    Write-Host "WARNING: The following Trae processes are running:" -ForegroundColor Red
    $runningProcs | Format-Table Name, Id -AutoSize | Out-String | Write-Host
    Write-Host "Please close all Trae windows first to avoid file locking issues." -ForegroundColor Red
    Write-Host ""
    
    if (-not $Force) {
        $answer = Read-Host "Press Y after closing all Trae windows, any other key to exit"
        if ($answer -notmatch '^[Yy]') {
            Write-Host "Cancelled." -ForegroundColor Gray
            exit 0
        }
        $runningProcs = Test-TraeProcesses
        if ($runningProcs.Count -gt 0) {
            Write-Host "Some processes still running, will attempt cleanup but may fail..." -ForegroundColor Yellow
        }
    }
}
else {
    Write-Host "OK: No running Trae processes detected" -ForegroundColor Green
}

Write-Host ""

$variantsToClean = @()
if ($IncludeAllVersions) {
    $variantsToClean = @($traeVariants.Keys)
}
else {
    $existing = @()
    foreach ($v in $traeVariants.Keys) {
        $vp = Get-VariantPath $v
        if (Test-Path $vp) {
            $size = Get-DirectorySize $vp
            $existing += [PSCustomObject]@{Name=$v; Path=$vp; Size=$size}
        }
    }
    if ($existing.Count -eq 0) {
        Write-Host "ERROR: No Trae configuration directories found" -ForegroundColor Red
        exit 1
    }
    $existing = $existing | Sort-Object Size -Descending
    $variantsToClean = @($existing[0].Name)
    Write-Host "[Info] Detected versions:" -ForegroundColor White
    $existing | ForEach-Object { Write-Host "  - $($_.Name): $(Format-Size $_.Size)" }
    Write-Host "  Will clean: $($variantsToClean[0]) (largest)" -ForegroundColor White
    Write-Host "  Use -IncludeAllVersions to clean all versions" -ForegroundColor Gray
}

Write-Host ""

Write-Host "[Scan] Analyzing cleanup targets..." -ForegroundColor Yellow
$allPlans = @()
foreach ($vName in $variantsToClean) {
    $vPath = Get-VariantPath $vName
    if (Test-Path $vPath) {
        $plan = Get-CleanupPlan -BasePath $vPath -Targets $safeCleanupTargets
        foreach ($p in $plan) {
            $p | Add-Member -MemberType NoteProperty -Name 'Variant' -Value $vName -Force
            $allPlans += $p
        }
    }
}

foreach ($entry in $localCleanupTargets.GetEnumerator()) {
    $fullPath = Join-Path $localPath $entry.Key
    if (Test-Path $fullPath) {
        $size = Get-DirectorySize $fullPath
        if ($size -gt 100MB) {
            $allPlans += [PSCustomObject]@{
                Variant = 'LocalAppData'
                Path = $fullPath
                RelativePath = $entry.Key
                Description = $entry.Value
                Size = $size
            }
        }
    }
}

if ($allPlans.Count -eq 0) {
    Write-Host "OK: No cleanable cache found" -ForegroundColor Green
    exit 0
}

$totalSize = ($allPlans | Measure-Object -Property Size -Sum).Sum
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Cleanup Preview ($($allPlans.Count) items, ~$(Format-Size $totalSize) to free)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
$allPlans | Sort-Object Size -Descending | Format-Table `
    @{N='Variant';E={$_.Variant}},
    @{N='Type';E={$_.Description}},
    @{N='Size';E={Format-Size $_.Size}},
    @{N='Path';E={$_.Path.Replace($env:USERPROFILE, '~')}} `
    -AutoSize | Out-String | Write-Host

Write-Host ""
Write-Host "SAFETY: The following user data will be PRESERVED:" -ForegroundColor Green
Write-Host "  - User settings (settings.json)"
Write-Host "  - Keybindings (keybindings.json)"
Write-Host "  - Code snippets (snippets/)"
Write-Host "  - Installed extensions"
Write-Host "  - Chat history and global state"
Write-Host ""

if ($DryRun) {
    Write-Host "[DryRun Mode] Preview complete, no files deleted." -ForegroundColor Yellow
    Write-Host "Run without -DryRun to perform actual cleanup." -ForegroundColor Gray
    exit 0
}

if (-not $Force) {
    Write-Host ""
    $confirm = Read-Host "Confirm cleanup? Will free ~$(Format-Size $totalSize) (Y/N)"
    if ($confirm -notmatch '^[Yy]') {
        Write-Host "Cancelled." -ForegroundColor Gray
        exit 0
    }
}

Write-Host ""
Write-Host "[Execute] Starting cleanup..." -ForegroundColor Yellow
Write-Host ""

$successCount = 0
$failCount = 0
$freedBytes = 0

foreach ($item in ($allPlans | Sort-Object Size -Descending)) {
    $p = $item.Path
    $desc = $item.Description
    $size = $item.Size
    
    Write-Host "  [Clean] $($item.Variant) | $desc ($(Format-Size $size)) ... " -NoNewline
    
    try {
        if (Test-Path $p) {
            $isProtected = $false
            foreach ($prot in $protectedPaths) {
                if ($p -like "*$prot*") {
                    $isProtected = $true
                    break
                }
            }
            if ($isProtected) {
                Write-Host "Skipped (protected)" -ForegroundColor DarkYellow
                continue
            }
            
            Remove-Item -LiteralPath $p -Recurse -Force -ErrorAction Stop
            $freedBytes += $size
            $successCount++
            Write-Host "Done" -ForegroundColor Green
        }
        else {
            Write-Host "Not found (skipped)" -ForegroundColor Gray
        }
    }
    catch {
        $failCount++
        $errMsg = $_.Exception.Message
        if ($errMsg.Length -gt 80) { $errMsg = $errMsg.Substring(0, 80) + "..." }
        Write-Host "FAILED: $errMsg" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Cleanup Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Successfully cleaned: $successCount items" -ForegroundColor Green
if ($failCount -gt 0) {
    Write-Host "  Failed: $failCount items" -ForegroundColor Red
}
Write-Host "  Space freed: $(Format-Size $freedBytes)" -ForegroundColor Green
Write-Host ""

try {
    $drive = Get-PSDrive -Name C -ErrorAction SilentlyContinue
    if ($drive) {
        $freeGB = [math]::Round($drive.Free / 1GB, 2)
        Write-Host "  C: drive free space: $freeGB GB" -ForegroundColor White
    }
}
catch {}

Write-Host ""
Write-Host "Tips:" -ForegroundColor Yellow
Write-Host "  1. Restart Trae after cleanup - indexes will rebuild automatically (first load may be slow)" -ForegroundColor Gray
Write-Host "  2. To clean all versions: .\cleanup-trae-cache.ps1 -IncludeAllVersions" -ForegroundColor Gray
Write-Host "  3. If index files are locked, ensure all Trae processes are fully closed and retry" -ForegroundColor Gray
Write-Host ""
