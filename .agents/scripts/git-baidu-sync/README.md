# Git+百度网盘同步脚本集

配合 [完整文档目录](../../docs/knowledge/learning/08-systems-infrastructure/git-baidu-sync/README.md) 使用。

## 脚本清单

| 脚本名 | 用途 |
|--------|------|
| `init-sync-dir.ps1/sh` | 初始化百度网盘同步根目录结构（repos/locks/backups/logs/meta/archive） |
| `setup-git-config.ps1/sh` | 配置Git全局参数与跨平台兼容设置 |
| `register-repo.ps1/sh` | 将本地工作仓库注册到同步空间（创建裸仓库） |
| `clone-repo.ps1/sh` | 从同步空间裸仓库克隆工作副本到本地 |
| `lock-utils.ps1/sh` | 分布式锁函数库（供其他脚本source调用） |
| `force-unlock.ps1/sh` | 强制解除仓库锁（紧急情况使用） |
| `git-sync-push.ps1/sh` | 安全push到网盘裸仓库并等待同步完成 |
| `git-sync-pull.ps1/sh` | 安全pull最新变更 |
| `git-sync.ps1/sh` | 一键同步（自动pull+push一体化） |
| `check-conflicts.ps1/sh` | 检测网盘冲突副本和潜在冲突风险 |
| `git-doctor.ps1/sh` | 仓库健康检查与自动修复工具 |
| `git-backup.ps1/sh` | 创建Git bundle备份快照 |
| `git-diag.ps1/sh` | 问题诊断工具，一键收集诊断信息 |

## Quick Start

```powershell
# 1. 初始化同步目录（首次使用）
.\init-sync-dir.ps1 -SyncPath "D:\BaiduSync\git-sync"

# 2. 配置Git环境（每台设备一次）
.\setup-git-config.ps1

# 3. 日常同步（在本地工作仓库目录执行）
git-sync
```
