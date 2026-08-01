$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ScriptsDir = Join-Path $ScriptDir "scripts"

. (Join-Path $ScriptsDir "common.ps1")

if ($args.Count -eq 0) {
    & (Join-Path $ScriptsDir "help.ps1")
    exit 0
}

$Command = $args[0]
$SubArgs = @()
if ($args.Count -gt 1) {
    $SubArgs = $args[1..($args.Count - 1)]
}

$switches = @("-h", "--help", "/?")
if ($switches -contains $Command) {
    & (Join-Path $ScriptsDir "help.ps1") @SubArgs
    exit 0
}

switch -Regex ($Command.ToLower()) {
    "^help$" { & (Join-Path $ScriptsDir "help.ps1") @SubArgs }
    "^verify-three-elements$|^verify$|^three-elements$" { & (Join-Path $ScriptsDir "verify-three-elements.ps1") @SubArgs }
    "^check-applicability$|^applicability$|^apply$" { & (Join-Path $ScriptsDir "check-applicability.ps1") @SubArgs }
    "^check-loop-design$|^loop-design$|^design$" { & (Join-Path $ScriptsDir "check-loop-design.ps1") @SubArgs }
    "^assess-risks$|^risks$|^risk$" { & (Join-Path $ScriptsDir "assess-risks.ps1") @SubArgs }
    "^query-knowledge$|^query$|^knowledge$|^search$" { & (Join-Path $ScriptsDir "query-knowledge.ps1") @SubArgs }
    default {
        Write-Host "错误: 未知子命令 '$Command'" -ForegroundColor Red
        Write-Host ""
        & (Join-Path $ScriptsDir "help.ps1")
        exit 1
    }
}

exit $LASTEXITCODE
