$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ScriptDir "common.ps1")

$parsed = Parse-Arguments -Arguments $args -Defaults @{ format = "markdown" }
$Format = Get-Format $parsed

$helpData = @{
    tool = "loop-engineering-cmd"
    version = "1.0.0"
    description = "Loop Engineering设计验证与知识查询命令行工具"
    return_codes = @{
        "0" = "检查通过"
        "1" = "检查失败/错误"
        "2" = "有警告"
    }
    commands = @(
        @{
            name = "help"
            aliases = @("-h", "--help", "/?")
            description = "显示所有可用子命令与使用说明"
            parameters = @(
                @{ name = "--format"; type = "string"; values = @("markdown", "json"); default = "markdown"; description = "输出格式" }
            )
        },
        @{
            name = "verify-three-elements"
            aliases = @("verify", "three-elements")
            description = "三要素验证（验证器、状态文件、停止条件）"
            parameters = @(
                @{ name = "--config"; type = "string"; description = "JSON配置文件路径" },
                @{ name = "--format"; type = "string"; values = @("markdown", "json"); default = "markdown"; description = "输出格式" }
            )
        },
        @{
            name = "check-applicability"
            aliases = @("applicability", "apply")
            description = "四项适用标准判定"
            parameters = @(
                @{ name = "--config"; type = "string"; description = "JSON配置文件路径" },
                @{ name = "--format"; type = "string"; values = @("markdown", "json"); default = "markdown"; description = "输出格式" }
            )
        },
        @{
            name = "check-loop-design"
            aliases = @("loop-design", "design")
            description = "循环设计完整性检查（五步法）"
            parameters = @(
                @{ name = "--config"; type = "string"; description = "JSON配置文件路径" },
                @{ name = "--format"; type = "string"; values = @("markdown", "json"); default = "markdown"; description = "输出格式" }
            )
        },
        @{
            name = "assess-risks"
            aliases = @("risks", "risk")
            description = "风险评估（理解债+认知让渡）"
            parameters = @(
                @{ name = "--config"; type = "string"; description = "JSON配置文件路径" },
                @{ name = "--format"; type = "string"; values = @("markdown", "json"); default = "markdown"; description = "输出格式" }
            )
        },
        @{
            name = "query-knowledge"
            aliases = @("query", "knowledge", "search")
            description = "知识库查询（核心概念、数据、案例、风险）"
            parameters = @(
                @{ name = "--keyword"; type = "string"; required = $true; description = "检索关键词" },
                @{ name = "--category"; type = "string"; values = @("concept", "data", "case", "risk", "all"); default = "all"; description = "分类筛选" },
                @{ name = "--format"; type = "string"; values = @("markdown", "json"); default = "markdown"; description = "输出格式" }
            )
        }
    )
}

if ($Format -eq "json") {
    $helpData | ConvertTo-Json -Depth 10
    exit 0
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Loop Engineering CMD v1.0.0" -ForegroundColor Cyan
Write-Host "  设计验证与知识查询工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "用法: loop-engineering-cmd <command> [options]" -ForegroundColor White
Write-Host ""
Write-Host "返回码规范:" -ForegroundColor Yellow
Write-Host "  0 = 检查通过" -ForegroundColor Green
Write-Host "  1 = 检查失败/错误" -ForegroundColor Red
Write-Host "  2 = 有警告" -ForegroundColor Yellow
Write-Host ""
Write-Host "可用子命令:" -ForegroundColor Yellow
Write-Host ""

foreach ($cmd in $helpData.commands) {
    $aliases = if ($cmd.aliases.Count -gt 0) { " [" + ($cmd.aliases -join ", ") + "]" } else { "" }
    Write-Host "  $($cmd.name)$aliases" -ForegroundColor Green
    Write-Host "    $($cmd.description)" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "示例:" -ForegroundColor Yellow
Write-Host "  loop-engineering-cmd help" -ForegroundColor White
Write-Host "  loop-engineering-cmd verify-three-elements --config loop-config.json" -ForegroundColor White
Write-Host "  loop-engineering-cmd check-applicability --frequency yes --verifiable true --budget true --environment true" -ForegroundColor White
Write-Host "  loop-engineering-cmd query-knowledge --keyword 验证器 --category concept" -ForegroundColor White
Write-Host ""
Write-Host "使用 'loop-engineering-cmd <command>' 执行对应子命令" -ForegroundColor Gray

exit 0
