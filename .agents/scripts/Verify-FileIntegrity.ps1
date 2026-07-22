<#
.SYNOPSIS
    File integrity triple-defense verification script
.DESCRIPTION
    Performs three-layer verification: size check + magic number validation + SHA256 hash check
.NOTES
    Version: 1.1
    Author: SpecWeave Knowledge Base
    Date: 2026-07-22
#>
param(
    [Parameter(Mandatory=$true, Position=0)][string]$FilePath,
    [Parameter(Mandatory=$false)][int]$MinSizeMB = 1,
    [Parameter(Mandatory=$false)]
    [ValidateSet("gzip","zip","7z","tar","exe","pdf","png","jpg","ignore")]
    [string]$ExpectedFileType = "ignore",
    [Parameter(Mandatory=$false)][string]$ExpectedHash = ""
)

$ErrorActionPreference = "Stop"

$script:results = @{
    SizeCheck    = "Pending"
    MagicCheck   = "Pending"
    HashCheck    = "Skipped"
    FileSizeMB   = 0
    FileSizeBytes= 0
    DetectedType = "Unknown"
    ActualHash   = ""
}

function Write-Step {
    param([string]$Message, [string]$Level = "info")
    $colorMap = @{ success="Green"; warning="Yellow"; error="Red"; info="Cyan" }
    $c = if ($colorMap.ContainsKey($Level)) { $colorMap[$Level] } else { "White" }
    Write-Host ("  " + $Message) -ForegroundColor $c
}

function Get-FileTypeByMagic {
    param([byte[]]$Bytes)
    $header = [System.BitConverter]::ToString($Bytes[0..3])
    $typeMap = @(
        @{ Bytes = @(0x1F,0x8B); Type = "gzip"; Desc = "GZIP archive (WSL image/tar.gz)" },
        @{ Bytes = @(0x50,0x4B,0x03,0x04); Type = "zip"; Desc = "ZIP archive" },
        @{ Bytes = @(0x50,0x4B,0x05,0x06); Type = "zip"; Desc = "ZIP archive (empty)" },
        @{ Bytes = @(0x37,0x7A,0xBC,0xAF); Type = "7z"; Desc = "7-Zip archive" },
        @{ Bytes = @(0x75,0x73,0x74,0x61); Type = "tar"; Desc = "TAR archive" },
        @{ Bytes = @(0x4D,0x5A); Type = "exe"; Desc = "Windows executable (EXE/DLL)" },
        @{ Bytes = @(0x25,0x50,0x44,0x46); Type = "pdf"; Desc = "PDF document" },
        @{ Bytes = @(0x89,0x50,0x4E,0x47); Type = "png"; Desc = "PNG image" },
        @{ Bytes = @(0xFF,0xD8,0xFF); Type = "jpg"; Desc = "JPEG image" }
    )
    foreach ($entry in $typeMap) {
        $match = $true
        for ($i = 0; $i -lt $entry.Bytes.Count; $i++) {
            if ($Bytes[$i] -ne $entry.Bytes[$i]) { $match = $false; break }
        }
        if ($match) {
            return @{ Type=$entry.Type; Desc=$entry.Desc; Header=$header }
        }
    }
    $ascii4 = [System.Text.Encoding]::ASCII.GetString($Bytes[0..3])
    if ($ascii4 -match "^<!|^<ht|^<HT|^\{" -or $Bytes[0] -eq 0x3C) {
        return @{ Type="html"; Desc="HTML error page (NOT a binary file!)"; Header=$header }
    }
    return @{ Type="unknown"; Desc="Unknown file type"; Header=$header }
}

# === Header ===
Write-Host ""
Write-Host ("=" * 51) -ForegroundColor Magenta
Write-Host "  File Integrity Triple-Defense Verification" -ForegroundColor Magenta
Write-Host ("=" * 51) -ForegroundColor Magenta
Write-Host ""

if (-not (Test-Path $FilePath)) {
    Write-Host ("[FAIL] File not found: " + $FilePath) -ForegroundColor Red
    exit 1
}

$file = Get-Item $FilePath
$script:results.FileSizeBytes = $file.Length
$script:results.FileSizeMB = [math]::Round($file.Length / 1MB, 2)
Write-Host ("[*] File: " + $FilePath)
$sizeLine = "[*] Size: {0} MB ({1} bytes)" -f $script:results.FileSizeMB, $script:results.FileSizeBytes
Write-Host $sizeLine
Write-Host ""

# === Layer 1: Size check ===
Write-Host "[1/3] Layer 1: File Size Check" -ForegroundColor Cyan
Write-Host ("  Requirement: >= " + $MinSizeMB + " MB")

if ($script:results.FileSizeMB -lt $MinSizeMB) {
    $failMsg = "[FAIL] File too small ({0} MB < threshold {1} MB)" -f $script:results.FileSizeMB, $MinSizeMB
    Write-Step $failMsg "error"
    if ($script:results.FileSizeMB -lt 0.01) {
        $sizeKB = [math]::Round($script:results.FileSizeBytes / 1KB, 2)
        Write-Step ("   File is only " + $sizeKB + " KB, likely an HTML error page") "warning"
        Write-Host ""
        Write-Host "   First 200 bytes preview:" -ForegroundColor Yellow
        try {
            $content = Get-Content $FilePath -Raw -ErrorAction SilentlyContinue
            if ($content) {
                $previewLen = [Math]::Min(200, $content.Length)
                Write-Host ("   " + $content.Substring(0, $previewLen)) -ForegroundColor Red
            }
        } catch {}
    }
    $script:results.SizeCheck = "Fail"
    Write-Host ""
    Write-Host ("=" * 51) -ForegroundColor Red
    Write-Host "  Result: FAILED (size check)" -ForegroundColor Red
    Write-Host ("=" * 51) -ForegroundColor Red
    exit 1
}

$passMsg = "[PASS] Size check passed ({0} MB >= {1} MB)" -f $script:results.FileSizeMB, $MinSizeMB
Write-Step $passMsg "success"
$script:results.SizeCheck = "Pass"

# === Layer 2: Magic number check ===
Write-Host ""
Write-Host "[2/3] Layer 2: Magic Number Validation" -ForegroundColor Cyan

if ($ExpectedFileType -eq "ignore") {
    Write-Step "[SKIP] Skipped per user request" "warning"
    $script:results.MagicCheck = "Skipped"
} else {
    Write-Host ("  Expected type: " + $ExpectedFileType)
    $bytes = [System.IO.File]::ReadAllBytes($FilePath)
    $det = Get-FileTypeByMagic -Bytes $bytes
    $script:results.DetectedType = $det.Type
    Write-Host ("  Magic header: " + $det.Header)
    Write-Host ("  Detected: " + $det.Desc)

    if ($det.Type -eq "html") {
        Write-Step "[FAIL] Downloaded an HTML error page, NOT a binary file!" "error"
        Write-Host ""
        Write-Host "   File preview:" -ForegroundColor Yellow
        $previewText = [System.Text.Encoding]::UTF8.GetString($bytes[0..499])
        $previewLen2 = [Math]::Min(300, $previewText.Length)
        Write-Host ("   " + $previewText.Substring(0, $previewLen2)) -ForegroundColor Red
        $script:results.MagicCheck = "Fail"
        Write-Host ""
        Write-Host ("=" * 51) -ForegroundColor Red
        Write-Host "  Result: FAILED (HTML page detected)" -ForegroundColor Red
        Write-Host ("=" * 51) -ForegroundColor Red
        exit 1
    }

    if ($det.Type -ne $ExpectedFileType) {
        $typeFail = "[FAIL] Type mismatch (expected: {0}, got: {1})" -f $ExpectedFileType, $det.Type
        Write-Step $typeFail "error"
        $script:results.MagicCheck = "Fail"
        Write-Host ""
        Write-Host ("=" * 51) -ForegroundColor Red
        Write-Host "  Result: FAILED (type mismatch)" -ForegroundColor Red
        Write-Host ("=" * 51) -ForegroundColor Red
        exit 1
    }

    Write-Step ("[PASS] File type matches: " + $ExpectedFileType) "success"
    $script:results.MagicCheck = "Pass"
}

# === Layer 3: SHA256 hash check ===
Write-Host ""
Write-Host "[3/3] Layer 3: SHA256 Hash Verification" -ForegroundColor Cyan

if ([string]::IsNullOrWhiteSpace($ExpectedHash)) {
    Write-Step "[SKIP] No expected hash provided" "warning"
    $script:results.HashCheck = "Skipped"
    $actualHash = (Get-FileHash $FilePath -Algorithm SHA256).Hash.ToLower()
    $script:results.ActualHash = $actualHash
    Write-Step ("[INFO] Actual SHA256: " + $actualHash) "info"
    Write-Step "[INFO] Save this hash for future verification" "info"
} else {
    Write-Host ("  Expected: " + $ExpectedHash)
    $actualHash = (Get-FileHash $FilePath -Algorithm SHA256).Hash.ToLower()
    $script:results.ActualHash = $actualHash
    Write-Host ("  Actual:   " + $actualHash)

    if ($actualHash -ne $ExpectedHash.ToLower().Trim()) {
        Write-Step "[FAIL] Hash mismatch! File may be corrupted or tampered!" "error"
        $script:results.HashCheck = "Fail"
        Write-Host ""
        Write-Host ("=" * 51) -ForegroundColor Red
        Write-Host "  Result: FAILED (hash mismatch)" -ForegroundColor Red
        Write-Host ("=" * 51) -ForegroundColor Red
        exit 1
    }
    Write-Step "[PASS] SHA256 hash matches perfectly" "success"
    $script:results.HashCheck = "Pass"
}

# === Summary ===
Write-Host ""
$allPassed = ($script:results.SizeCheck -eq "Pass") -and
             ($script:results.MagicCheck -eq "Pass" -or $script:results.MagicCheck -eq "Skipped") -and
             ($script:results.HashCheck -ne "Fail")

$sepColor = if ($allPassed) { "Green" } else { "Red" }
$resultMsg = if ($allPassed) { "  Result: PASSED - File is intact and trustworthy" } else { "  Result: FAILED" }
Write-Host ("=" * 51) -ForegroundColor $sepColor
Write-Host $resultMsg -ForegroundColor $sepColor
Write-Host ("=" * 51) -ForegroundColor $sepColor
Write-Host ""
Write-Host "Summary:"
Write-Host ("  - Size:     {0} MB -> {1}" -f $script:results.FileSizeMB, $script:results.SizeCheck)
Write-Host ("  - Type:     {0} -> {1}" -f $script:results.DetectedType, $script:results.MagicCheck)
Write-Host ("  - SHA256:   " + $script:results.HashCheck)
if ($script:results.ActualHash) {
    Write-Host ("  - Hash:     " + $script:results.ActualHash)
}
Write-Host ""

if ($allPassed) { exit 0 } else { exit 1 }
