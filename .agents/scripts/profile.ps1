#Requires -Version 5.1
<#
.SYNOPSIS
    SpecWeave 项目级PowerShell配置文件 - UTF-8编码环境设置。
.DESCRIPTION
    设置控制台编码为UTF-8，确保中文输出正常。
    可通过 Install-Profile.ps1 安装到用户PowerShell Profile自动加载。
.NOTES
    编码: UTF-8 BOM + CRLF
    兼容: PowerShell 5.1 / 7.x
#>

cmd /c chcp 65001 > $null

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'

Write-Host "[UTF-8] 编码环境已就绪" -ForegroundColor Green
