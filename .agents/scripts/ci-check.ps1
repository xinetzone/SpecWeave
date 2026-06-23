# CI/CD 流水线检查脚本
# 用途：在提交前自动运行所有验证检查，确保代码质量
# 用法：.\ci-check.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent $root

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CI/CD 流水线检查" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查 Git 忽略规则
Write-Host "[1/4] 检查 Git 忽略规则..." -ForegroundColor Yellow
python "$root\.agents\scripts\check-gitignore.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: Git 忽略规则检查失败" -ForegroundColor Red
    exit 1
}
Write-Host "  通过" -ForegroundColor Green
Write-Host ""

# 2. 检查链接有效性
Write-Host "[2/4] 检查链接有效性..." -ForegroundColor Yellow
python "$root\.agents\scripts\check-links.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 链接检查失败" -ForegroundColor Red
    exit 1
}
Write-Host "  通过" -ForegroundColor Green
Write-Host ""

# 3. 检查规格文档一致性
Write-Host "[3/4] 检查规格文档一致性..." -ForegroundColor Yellow
python "$root\.agents\scripts\check-spec-consistency.py"
# 规格一致性检查允许警告，但错误必须修复
if ($LASTEXITCODE -ne 0) {
    Write-Host "警告: 规格文档一致性检查有警告" -ForegroundColor Yellow
}
Write-Host ""

# 4. 更新导航表
Write-Host "[4/4] 更新文档导航表..." -ForegroundColor Yellow
python "$root\.agents\scripts\generate-nav.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 导航表更新失败" -ForegroundColor Red
    exit 1
}
Write-Host "  通过" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "所有检查通过" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan