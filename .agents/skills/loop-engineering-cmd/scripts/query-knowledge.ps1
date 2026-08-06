$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ScriptDir "common.ps1")

$parsed = Parse-Arguments -Arguments $args -Defaults @{
    format = "markdown"
    category = "all"
    keyword = ""
}

$Format = Get-Format $parsed
$Category = "all"
if ($parsed.ContainsKey("category")) { $Category = [string]$parsed["category"] }

$Keyword = ""
if ($parsed.ContainsKey("keyword")) { $Keyword = [string]$parsed["keyword"] }

if ([string]::IsNullOrEmpty($Keyword)) {
    Write-Host "错误: 必须提供 --keyword 参数指定检索关键词" -ForegroundColor Red
    Write-Host "用法: loop-engineering-cmd query-knowledge --keyword <关键词> [--category <分类>]" -ForegroundColor Yellow
    exit 1
}

$KnowledgePath = Join-Path (Split-Path -Parent $ScriptDir) "data\knowledge.json"

if (-not (Test-Path $KnowledgePath)) {
    Write-Host "错误: 知识库文件不存在: $KnowledgePath" -ForegroundColor Red
    exit 1
}

try {
    $knowledge = Get-Content $KnowledgePath -Raw -Encoding UTF8 | ConvertFrom-Json
} catch {
    Write-Host "错误: 无法读取知识库: $_" -ForegroundColor Red
    exit 1
}

$keywordLower = $Keyword.ToLower()
$matched = @()

function Search-Category {
    param($Items, $CategoryName)
    foreach ($item in $Items) {
        $kw = @($item.keywords) -join " "
        $text = ($item.title + " " + $kw + " " + $item.content + " " + $item.id).ToLower()
        if ($text -like "*$keywordLower*") {
            $script:matched += @{
                id = $item.id
                category = $CategoryName
                title = $item.title
                keywords = $item.keywords
                content = $item.content
            }
        }
    }
}

switch ($Category.ToLower()) {
    "concept" { Search-Category $knowledge.concepts "概念" }
    "data" { Search-Category $knowledge.data "数据" }
    "case" { Search-Category $knowledge.cases "案例" }
    "risk" { Search-Category $knowledge.risks "风险" }
    "all" {
        Search-Category $knowledge.concepts "概念"
        Search-Category $knowledge.data "数据"
        Search-Category $knowledge.cases "案例"
        Search-Category $knowledge.risks "风险"
    }
    default {
        Write-Host "错误: 未知分类 '$Category'，可选值: concept/data/case/risk/all" -ForegroundColor Red
        exit 1
    }
}

if ($Format -eq "json") {
    $output = @{
        command = "query-knowledge"
        keyword = $Keyword
        category = $Category
        total = $matched.Count
        results = $matched
    }
    $output | ConvertTo-Json -Depth 10
    exit 0
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Loop Engineering - 知识库查询" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "关键词: $Keyword" -ForegroundColor White
Write-Host "分类: $Category" -ForegroundColor White
Write-Host "找到 $($matched.Count) 条结果" -ForegroundColor $(if ($matched.Count -gt 0) { "Green" } else { "Yellow" })
Write-Host ""

if ($matched.Count -eq 0) {
    Write-Host "[!] 未找到匹配的知识点。" -ForegroundColor Yellow
    Write-Host "  建议：尝试使用更通用的关键词，或使用 --category all 搜索全部分类。" -ForegroundColor Gray
    Write-Host ""
    Write-Host "热门关键词参考：" -ForegroundColor Yellow
    Write-Host "  三要素、验证器、状态文件、停止条件" -ForegroundColor Gray
    Write-Host "  适用标准、频率、预算、环境" -ForegroundColor Gray
    Write-Host "  五步法、探索、评分、变更" -ForegroundColor Gray
    Write-Host "  理解债、认知让渡、风险、ROI" -ForegroundColor Gray
    Write-Host "  正面案例、反面案例、作弊" -ForegroundColor Gray
    Write-Host ""
    exit 0
}

$grouped = $matched | Group-Object category
foreach ($group in $grouped) {
    Write-Host "[$($group.Name)]" -ForegroundColor Yellow
    foreach ($item in $group.Group) {
        Write-Host "  [*] $($item.title)" -ForegroundColor Green
        Write-Host "     ID: $($item.id)" -ForegroundColor DarkGray
        Write-Host "     关键词: $($item.keywords -join ', ')" -ForegroundColor Gray
        Write-Host ""
        Write-Host "     $($item.content)" -ForegroundColor White
        Write-Host ""
    }
}

Write-Host "提示: 使用 --category 参数可筛选特定分类（concept/data/case/risk）" -ForegroundColor Gray
Write-Host ""

exit 0
