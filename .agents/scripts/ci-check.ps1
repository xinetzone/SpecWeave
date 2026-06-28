# CI/CD 流水线检查脚本
# 用途：在提交前自动运行所有验证检查，确保代码质量
# 用法：.\ci-check.ps1

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$agentsDir = Split-Path -Parent $scriptDir
$root = Split-Path -Parent $agentsDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CI/CD 流水线检查" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查 Git 忽略规则
Write-Host "[1/10] 检查 Git 忽略规则..." -ForegroundColor Yellow
python "$root\.agents\scripts\check-gitignore.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: Git 忽略规则检查失败" -ForegroundColor Red
    exit 1
}
Write-Host "  通过" -ForegroundColor Green
Write-Host ""

# 2. 检查 vendor 目录合规性
Write-Host "[2/10] 检查 vendor 目录合规性..." -ForegroundColor Yellow
python "$root\.agents\scripts\check-vendor.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "警告: vendor 目录合规性检查发现问题（如无第三方依赖可忽略）" -ForegroundColor Yellow
}
Write-Host ""

# 3. 检查链接有效性
Write-Host "[3/10] 检查链接有效性..." -ForegroundColor Yellow
python "$root\.agents\scripts\check-links.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 链接检查失败" -ForegroundColor Red
    exit 1
}
Write-Host "  通过" -ForegroundColor Green
Write-Host ""

# 4. 检查 Mermaid 语法安全
Write-Host "[4/10] 检查 Mermaid 语法安全..." -ForegroundColor Yellow
python "$root\.agents\scripts\check-mermaid.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: Mermaid 语法检查失败，请修复渲染问题" -ForegroundColor Red
    exit 1
}
Write-Host "  通过" -ForegroundColor Green
Write-Host ""

# 5. 检查规格文档一致性
Write-Host "[5/10] 检查规格文档一致性..." -ForegroundColor Yellow
python "$root\.agents\scripts\check-spec-consistency.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "警告: 规格文档一致性检查有警告" -ForegroundColor Yellow
}
Write-Host ""

# 6. 检查模式成熟度字段
Write-Host "[6/10] 检查模式成熟度字段..." -ForegroundColor Yellow
python "$root\.agents\scripts\pattern-maturity-stats.py" --check
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 模式成熟度字段检查失败" -ForegroundColor Red
    exit 1
}
Write-Host "  通过" -ForegroundColor Green
Write-Host ""

# 7. 检查文件名规范
Write-Host "[7/10] 检查文件名规范..." -ForegroundColor Yellow
python "$root\.agents\scripts\check-filename-convention.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 文件名规范检查失败" -ForegroundColor Red
    exit 1
}
Write-Host "  通过" -ForegroundColor Green
Write-Host ""

# 8. 更新 Spec 执行进度看板
Write-Host "[8/10] 更新 Spec 执行进度看板..." -ForegroundColor Yellow
python "$root\.agents\scripts\generate-dashboard.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: Spec 看板更新失败" -ForegroundColor Red
    exit 1
}
Write-Host "  通过" -ForegroundColor Green
Write-Host ""

# 9. 更新导航表
Write-Host "[9/10] 更新文档导航表..." -ForegroundColor Yellow
python "$root\.agents\scripts\generate-nav.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 导航表更新失败" -ForegroundColor Red
    exit 1
}
Write-Host "  通过" -ForegroundColor Green
Write-Host ""

# 10. 检查脚本重复代码
Write-Host "[10/10] 检查脚本重复代码..." -ForegroundColor Yellow
python "$root\.agents\scripts\check-duplication.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "警告: 检测到跨文件重复代码块，建议提取到共享库" -ForegroundColor Yellow
    Write-Host "  参考: .agents/scripts/lib/README.md" -ForegroundColor Yellow
}
else {
    Write-Host "  通过" -ForegroundColor Green
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "所有检查通过" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
