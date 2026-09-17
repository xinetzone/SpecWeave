#!/usr/bin/env pwsh
# xmnn-runtime 开发仓库便捷入口（薄转发壳，零业务逻辑）
#
# 真实交付脚本位于客户交付包根 release/xmnnctl.ps1；它启动时
# Set-Location 自身目录，故 .env / workspace / 容器操作全部落在
# release/ 侧，本壳所在的叠加层根目录不产生任何运行时文件。
# 交付包打包（relpack）只取 release/，本壳不会到达客户机器。
#
# 两套 compose 同名（project/容器名/端口一致），开发栈与交付栈
# 天然互斥——同一时刻只运行其一，up 会替换同 project 容器。

$real = Join-Path $PSScriptRoot 'release\xmnnctl.ps1'
& $real @args
exit $LASTEXITCODE
