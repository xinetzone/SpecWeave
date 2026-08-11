#requires -Version 7.0
<#
.SYNOPSIS
    检查所有子模块 .agents/rules/*.md 文件的 frontmatter id 字段唯一性。
.DESCRIPTION
    扫描 apps/ 下所有子模块的 .agents/rules/ 目录，提取每个 .md 文件的 YAML frontmatter 中的 id 字段，
    检测重复/缺失/格式不规范的 id，并输出报告。
.PARAMETER RootDir
    SpecWeave 根目录路径，默认为脚本所在位置向上3层（scripts/→.agents/→项目根）。
.PARAMETER Strict
    严格模式：缺失id字段视为错误（默认仅警告）。
.EXAMPLE
    # 从项目根目录运行
    powershell -ExecutionPolicy Bypass -File .agents/scripts/check-rules-id-uniqueness.ps1
.EXAMPLE
    # 严格模式（缺失id报错）
    powershell -ExecutionPolicy Bypass -File .agents/scripts/check-rules-id-uniqueness.ps1 -Strict
#>
param(
    [string]$RootDir,
    [switch]$Strict
)

$ErrorActionPreference = 'Stop'

# ── 确定根目录 ──
if (-not $RootDir) {
    $RootDir = Split-Path (Split-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) -Parent) -Parent
}
$RootDir = (Resolve-Path $RootDir).Path
Write-Host "=== Rules Frontmatter ID Uniqueness Checker ===" -ForegroundColor Cyan
Write-Host "Root directory: $RootDir" -ForegroundColor Gray
Write-Host ""

# ── 收集所有 .agents/rules/*.md 文件 ──
$appsDir = Join-Path $RootDir "apps"
$rulesFiles = @()
if (Test-Path $appsDir) {
    # Use wildcard matching for cross-platform path separator compatibility
    $rulesFiles = Get-ChildItem -Path $appsDir -Recurse -Filter "*.md" -File | Where-Object {
        $_.FullName -match '\.agents[/\\]rules[/\\]'
    }
}

if (-not $rulesFiles) {
    Write-Host "[WARN] No .agents/rules/*.md files found under apps/" -ForegroundColor Yellow
    exit 0
}

Write-Host "Scanning $($rulesFiles.Count) rules files..." -ForegroundColor Gray
Write-Host ""

# ── 提取 id 字段 ──
$idMap = @{}        # id → list of file paths
$missingId = @()    # files missing id field
$badFormat = @()    # files with malformed frontmatter or id

foreach ($file in $rulesFiles) {
    $relPath = $file.FullName.Substring($RootDir.Length + 1).Replace('\', '/')

    try {
        $content = Get-Content -Path $file.FullName -Raw -Encoding utf8
    } catch {
        Write-Host "[ERROR] Cannot read $relPath : $_" -ForegroundColor Red
        $badFormat += $relPath
        continue
    }

    # Check YAML frontmatter: starts with --- and has closing ---
    if ($content -notmatch '^---\s*\r?\n') {
        Write-Host "[WARN] No YAML frontmatter (---) at start of $relPath" -ForegroundColor Yellow
        if ($Strict) { $badFormat += $relPath }
        $missingId += $relPath
        continue
    }

    # Extract id field from frontmatter (simple regex, no full YAML parser needed)
    if ($content -match '(?s)^---\s*\r?\n(.*?)\r?\n---') {
        $fm = $Matches[1]
        if ($fm -match '(?m)^id:\s*["'']?([^"'':\r\n]+)["'']?\s*$') {
            $id = $Matches[1].Trim()
            if (-not $idMap.ContainsKey($id)) {
                $idMap[$id] = [System.Collections.Generic.List[string]]::new()
            }
            $idMap[$id].Add($relPath)
        } else {
            Write-Host "[WARN] Missing 'id:' field in frontmatter of $relPath" -ForegroundColor Yellow
            if ($Strict) { $missingId += $relPath }
        }
    } else {
        Write-Host "[WARN] Malformed frontmatter (no closing ---) in $relPath" -ForegroundColor Yellow
        $badFormat += $relPath
    }
}

# ── 检查重复 ──
$duplicates = $idMap.GetEnumerator() | Where-Object { $_.Value.Count -gt 1 } | Sort-Object Name

# ── 输出结果 ──
$errorCount = 0
$warnCount = 0

if ($duplicates) {
    Write-Host "`n[FAIL] DUPLICATE IDs FOUND:" -ForegroundColor Red
    Write-Host ("=" * 70) -ForegroundColor Red
    foreach ($dup in $duplicates) {
        Write-Host ""
        Write-Host "  id: `"$($dup.Key)`"" -ForegroundColor Red
        Write-Host "  used in $($dup.Value.Count) files:"
        foreach ($path in $dup.Value) {
            Write-Host "    - $path" -ForegroundColor Red
        }
        $errorCount++
    }
    Write-Host ""
} else {
    Write-Host "[PASS] All IDs are unique." -ForegroundColor Green
}

if ($missingId.Count -gt 0) {
    Write-Host ""
    Write-Host "[WARN] Files missing 'id:' field ($($missingId.Count)):" -ForegroundColor Yellow
    foreach ($path in $missingId) {
        Write-Host "  - $path" -ForegroundColor Yellow
    }
    $warnCount += $missingId.Count
}

if ($badFormat.Count -gt 0) {
    Write-Host ""
    Write-Host "[ERROR] Files with malformed frontmatter ($($badFormat.Count)):" -ForegroundColor Red
    foreach ($path in $badFormat) {
        Write-Host "  - $path" -ForegroundColor Red
    }
    $errorCount += $badFormat.Count
}

# ── 汇总表 ──
Write-Host ""
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan

# All IDs table
$sortedIds = $idMap.GetEnumerator() | Sort-Object Name
Write-Host ""
Write-Host "All rule file IDs ($($sortedIds.Count) total):" -ForegroundColor White
Write-Host ("-" * 70) -ForegroundColor Gray
foreach ($entry in $sortedIds) {
    $dup = if ($entry.Value.Count -gt 1) { " [DUPLICATE!]" } else { "" }
    Write-Host "  $($entry.Key)$dup" -ForegroundColor $(if ($dup) { "Red" } else { "Gray" })
    Write-Host "    → $($entry.Value[0])" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "Total files scanned: $($rulesFiles.Count)" -ForegroundColor White
Write-Host "Unique IDs found:    $($sortedIds.Count)" -ForegroundColor White
Write-Host "Duplicate IDs:       $($duplicates.Count)" -ForegroundColor $(if ($duplicates.Count -gt 0) { "Red" } else { "Green" })
Write-Host "Missing ID warnings: $($missingId.Count)" -ForegroundColor $(if ($missingId.Count -gt 0) { "Yellow" } else { "Green" })
Write-Host "Malformed errors:    $($badFormat.Count)" -ForegroundColor $(if ($badFormat.Count -gt 0) { "Red" } else { "Green" })

if ($errorCount -gt 0) {
    Write-Host "`n[RESULT] FAILED with $errorCount error(s)" -ForegroundColor Red
    exit 1
} elseif ($warnCount -gt 0 -and $Strict) {
    Write-Host "`n[RESULT] FAILED (strict mode): $warnCount warning(s)" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "`n[RESULT] PASSED" -ForegroundColor Green
    exit 0
}
