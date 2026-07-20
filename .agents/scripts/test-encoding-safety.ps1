#Requires -Version 5.1
param([switch]$Cleanup)
$ErrorActionPreference = "Stop"
. (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "lib\encoding-safety.ps1")
$testDir = Join-Path ([System.IO.Path]::GetTempPath()) "encoding-test-$(Get-Date -Format 'yyyyMMddHHmmss')"
New-Item -ItemType Directory -Path $testDir -Force | Out-Null
$testContent = "# 编码安全测试 / Encoding Test`n`n你好世界！Hello World!`n`n特殊字符：，。！？✅❌⚠️🚀日本語テスト한국어`n`nEND"
Write-Host "Encoding Test - pwsh $($PSVersionTable.PSVersion)" -ForegroundColor Cyan
Write-Host "Dir: $testDir" -ForegroundColor Gray
$script:results = @()
function Run-Test {
    param([string]$Name,[string]$File,[scriptblock]$Action)
    $fp = Join-Path $testDir $File
    Write-Host "[TEST] $Name ..." -ForegroundColor Yellow
    try {
        & $Action $fp
        Start-Sleep -Milliseconds 50
        $info = Test-Utf8File $fp
        $rb = Read-Utf8File $fp -Raw
        $garbled = $rb -match [char]0xFFFD
        $hasCN = $rb -match "你好世界"
        $hasEmoji = $rb -match "🚀"
        $b = [IO.File]::ReadAllBytes($fp)
        $bom = ($b.Length -ge 3 -and $b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF)
        $ok = (-not $garbled) -and $hasCN -and $hasEmoji -and (-not $bom)
        $c = if ($ok){"PASS"}else{"FAIL"}
        $col = if ($ok){"Green"}else{"Red"}
        Write-Host "  [$c] BOM=$bom Garbled=$garbled CN=$hasCN Emoji=$hasEmoji Size=$($b.Length)" -ForegroundColor $col
        $script:results += [PSCustomObject]@{Name=$Name;Passed=$ok;HasBom=$bom;HasGarbled=$garbled;Size=$b.Length}
    } catch {
        Write-Host "  [ERROR] $($_.Exception.Message)" -ForegroundColor Red
        $script:results += [PSCustomObject]@{Name=$Name;Passed=$false;HasBom=$false;HasGarbled=$true;Size=0}
    }
}
Run-Test "Write-Utf8File (safe lib)" "01-safe.md" { param($f) Write-Utf8File $f $testContent -NoNewline }
Run-Test ".NET Utf8NoBomSingleton" "02-nobom.md" { param($f) [IO.File]::WriteAllText($f,$testContent,$Utf8NoBomSingleton) }
Run-Test ".NET Encoding.UTF8 (BOM)" "03-bom.md" { param($f) [IO.File]::WriteAllText($f,$testContent,[Text.Encoding]::UTF8) }
Run-Test "Set-Content -Encoding UTF8" "04-sc-utf8.md" { param($f) Set-Content $f $testContent -Encoding UTF8 -NoNewline }
Run-Test "Out-File -Encoding UTF8" "05-of-utf8.md" { param($f) $testContent | Out-File $f -Encoding UTF8 -NoNewline }
Run-Test "Set-Content (default)" "06-sc-def.md" { param($f) Set-Content $f $testContent -NoNewline }
Run-Test "Out-File (default)" "07-of-def.md" { param($f) $testContent | Out-File $f -NoNewline }
Write-Host ""
$p = ($results|?{$_.Passed}).Count
$f = ($results|?{-not $_.Passed}).Count
Write-Host "Passed: $p / $($results.Count)  Failed: $f" -ForegroundColor $(if($f -eq 0){"Green"}else{"Yellow"})
foreach($r in $results){
    $m = if($r.Passed){"OK"}else{"FAIL"}
    $col = if($r.Passed){"Green"}else{"Red"}
    Write-Host "  $m $($r.Name)" -ForegroundColor $col
}
Write-Host "`nTest dir: $testDir" -ForegroundColor Gray
if($Cleanup){ Remove-Item $testDir -Recurse -Force; Write-Host "Cleaned up." -ForegroundColor Gray }
exit $(if($f -eq 0){0}else{1})