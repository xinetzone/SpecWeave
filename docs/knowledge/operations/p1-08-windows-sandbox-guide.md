---
id: p1-08-windows-sandbox-guide
title: Windows 沙盒安装与配置操作手册摘要
source: d:\spaces\chaos\.trae\documents\Windows 沙盒安装与配置操作手册.md
source_type: file
category: operations
tags:
  - windows-sandbox
  - virtualization
  - wsb-config
  - troubleshooting
  - workspace-operations
archive_status: archived
archive_priority: P1
created_at: 2026-08-02T00:00:00Z
updated_at: 2026-08-02T11:30:00Z
version: v0.1.0
reviewer: chaos-validation-agent
review_notes: approved：来源 Windows 沙盒操作手册、正文为运维操作摘要、元数据与 operations 分类映射核对通过
summary: Windows 沙盒从零到可用的安装与配置手册，覆盖版本检查、虚拟化启用、图形界面/PowerShell 启用、隔离验证、网络与共享策略、.wsb 一键启动模板及常见故障排查。
target_path: D:\spaces\SpecWeave\.agents\docs\knowledge\operations\p1-08-windows-sandbox-guide.md
archived_at: 2026-08-02T03:18:05Z
source_version: v0.1.0
archive_version: v0.1.0
last_error: 
archive_history:
  - 2026-08-02T03:18:05Z archived from d:\spaces\chaos\.agents\knowledge\temp\operations\p1-08-windows-sandbox-guide.md to D:\spaces\SpecWeave\.agents\docs\knowledge\operations\p1-08-windows-sandbox-guide.md
---

# Windows 沙盒安装与配置操作手册摘要

## 来源

- 源文件：[Windows 沙盒安装与配置操作手册.md](file:///d:/spaces/chaos/.trae/documents/Windows%20沙盒安装与配置操作手册.md)
- 官方参考：Microsoft Learn「安装 Windows 沙盒」「使用与配置 .wsb 文件」
- 上游分析：[workspace-archive-priority-analysis.md](file:///d:/spaces/chaos/tasks/business-domains/knowledge-archive/workspace-archive-priority-analysis.md)

## 归档目标

正式分类：`operations`
正式目录：`d:\spaces\SpecWeave\.agents\docs\knowledge\operations\`

## 正文摘要

### 前置条件

- Windows 10 ≥ 1903 或 Windows 11 受支持版本，且为专业版/企业版/教育版（家庭版不支持）
- BIOS/UEFI 已开启虚拟化（VT-x/AMD-V），建议 ≥4GB 内存、≥1GB 磁盘、≥2 核 CPU

### 启用路径（二选一）

- 图形界面：启用或关闭 Windows 功能 → 勾选「Windows 沙盒」→ 确定 → 重启
- PowerShell（自动化/批量部署）：

```powershell
Enable-WindowsOptionalFeature -FeatureName "Containers-DisposableClientVM" -All -Online
```

### 隔离验证清单

- 沙盒内为临时系统环境（默认账户 WDAGUtilityAccount）
- 沙盒内新建文件关闭后消失（证明不持久化）
- 沙盒内安装/修改设置不影响宿主

### 网络与共享策略（安全基线）

- 默认网络启用；测试未知样本时禁用网络，需要在线安装时临时启用
- 共享目录只映射专用目录（如 `C:\Users\Public\Downloads`），默认 `ReadOnly=true`，不映射含敏感信息的目录

### .wsb 一键启动模板（要点）

- 高安全「未知文件测试」：`<VGpu>Disable</VGpu>` + `<Networking>Disable</Networking>` + 只读映射下载目录 + `LogonCommand` 自动打开
- 受控联网「临时安装/调试」：`<Networking>Enable</Networking>` + 只读 Input + 可写 Output 双映射
- 可选强化：禁用剪贴板/打印机/音频输入重定向、`<ProtectedClient>Enable</ProtectedClient>`、`<MemoryInMB>4096</MemoryInMB>`

### 常见故障排查速查

| 现象 | 主要原因与处理 |
|---|---|
| 功能列表无「Windows 沙盒」 | 家庭版/系统过旧/未启用虚拟化 → 升级版本、更新系统、开启 BIOS 虚拟化 |
| 已启用但启动失败/闪退 | 虚拟化未真正启用或 VM 内未开嵌套虚拟化 → 开启后重试 |
| .wsb 报「配置文件无效」 | XML 格式错误或 HostFolder 路径错误 → 用最小配置验证再逐项添加 |
| 联网异常/共享目录不可见 | `.wsb` 中 Networking 或 MappedFolders 配置问题 → 先默认方式启动验证基线 |

- 虚拟机内使用需先开启嵌套虚拟化：`Set-VMProcessor -VMName <VMName> -ExposeVirtualizationExtensions $true`

## 动作边界

本轮为 P1 运维条目。正式归档时以启用路径、安全基线与排错速查为核心正文，不搬运操作手册中的全部逐步截图式说明。
