---
id: "jupyter-image-cache"
title: "镜像缓存与增量重建"
source: "bin/jpman, Containerfile"
---
# 镜像缓存与增量重建

本项目提供两种优化开发体验的机制：
1. **镜像缓存**：使用 podman save/load 快速备份恢复镜像，避免重复构建
2. **增量重建**：`jpman rebuild` 基于主 Containerfile 层缓存，配置变更仅重建 Layer 4/5（<10秒）

## 镜像缓存

镜像缓存功能通过 `jpman save` 和 `jpman load` 命令实现，将构建好的镜像保存为压缩归档，方便在不同环境间传输或快速恢复。

### 保存镜像

```bash
bash bin/jpman save
```

该命令会：
1. 获取当前镜像 ID
2. 生成带时间戳的文件名：`jupyter-podman-rootless-<image-id>-<YYYYMMDD-HHMMSS>.tar.gz`
3. 使用 pigz（如已安装）进行多线程压缩，否则使用 gzip
4. 创建/更新 `jupyter-podman-rootless-latest.tar.gz` 软链接
5. 生成 `manifest.txt` 记录元数据
6. 验证 gzip 完整性

输出位置：`.image-cache/` 目录（已在 .gitignore 中忽略）。

### 加载镜像

```bash
bash bin/jpman load
```

从 `.image-cache/jupyter-podman-rootless-latest.tar.gz` 加载镜像。如指定了其他归档，jpman 会自动查找最新的时间戳归档。

### 缓存目录结构

```
.image-cache/
├── manifest.txt                                    # 镜像元数据清单
├── jupyter-podman-rootless-latest.tar.gz           # 最新版本软链接
└── jupyter-podman-rootless-abc123def456-20260827-143022.tar.gz  # 带时间戳的归档
```

### manifest.txt 格式

```
# Jupyter Podman Rootless Image Cache
IMAGE_NAME=localhost/jupyter-podman-rootless:latest
IMAGE_ID=abc123def456
IMAGE_FILE=jupyter-podman-rootless-abc123def456-20260827-143022.tar.gz
SIZE=1.2G
SHA256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
SAVED=2026-08-27T14:30:22Z
SAVE_TOOK=45s
```

### 典型使用场景

1. **WSL 重置后快速恢复**：WSL 重置后 Podman 镜像会丢失，使用 `jpman load` 2-5分钟即可恢复（对比重新构建20-40分钟）
2. **多环境同步**：在一台机器构建后，将 .image-cache/ 复制到其他机器直接加载
3. **CI/CD 缓存**：在 CI 流水线中缓存归档，加速后续构建
4. **版本回滚**：保留多个时间戳归档，需要时加载旧版本

## 增量重建

当只修改配置文件（如 jupyter_notebook_config.py）时，无需重新构建整个镜像，使用增量重建可以在10秒内完成更新。

### 增量重建原理

配置文件（如 `config/jupyter_notebook_config.py`）位于主 Containerfile 的 **Layer 4**（独立成层、变化频率高）。修改配置后重新构建时，Stage 1-3 与 Layer 2/3 缓存全部命中，仅 Layer 4/5 重建，因此秒级完成——无需单独的增量补丁文件。

### 使用增量重建

```bash
bash bin/jpman rebuild
```

该命令会：
1. 如容器正在运行，先停止并删除
2. 从项目根目录的主 Containerfile 构建（`--format docker` + tuna 三镜像源，与 rebuild-all 一致）
3. 层缓存命中时秒级完成
4. 自动启动新容器

> ⚠️ **注意**：增量重建的提速依赖层缓存有效（首次构建或缓存被清理后即为全量速度）。若修改了 Containerfile、conda 环境、apt 包等，同样使用 `jpman rebuild` 或 `jpman rebuild-all`，区别仅在于 rebuild 会自动重启容器。

### 何时使用哪种构建方式

| 变更类型 | rebuild | rebuild-all |
|----------|---------|-------------|
| config/jupyter_notebook_config.py | ✅（秒级） | ✅（秒级，但不自动重启容器） |
| config/sshd_config | ✅（秒级） | ✅（秒级，但不自动重启容器） |
| config/supervisord.conf | ✅（秒级） | ✅（秒级，但不自动重启容器） |
| conda-lock/environment.yml | ❌ 全量耗时 | ✅ |
| Containerfile（apt/pip 包） | ❌ 全量耗时 | ✅ |
| entrypoint.sh | ❌ 全量耗时 | ✅ |
| tasks/*.py（invoke 任务） | ❌ 无需构建，直接生效 | ❌ |

## jpman 构建相关命令对比

| 命令 | 速度 | 适用场景 | 说明 |
|------|------|----------|------|
| `jpman rebuild` | <10秒 | 仅配置文件变更 | 主 Containerfile 层缓存构建，自动重启容器 |
| `jpman rebuild-all` | 20-40分钟 | 首次构建或重大变更 | 完整构建，默认使用清华源 |
| `invoke build` | 20-40分钟 | 需要自定义镜像源 | 支持 --apt-mirror/--conda-mirror/--pip-mirror 选择源 |
| `jpman load` | 2-5分钟 | 有缓存归档 | 从 .image-cache/ 加载 |

## 缓存目录管理

`.image-cache/` 和 `.wsl-cache/` 目录已在 `.gitignore` 中配置，不会被提交到 Git：

```gitignore
# Image cache (podman save archives for backup/recovery)
.image-cache/

# WSL distro cache (VHDX files and rootfs exports)
.wsl-cache/
```

如需清理缓存，直接删除这两个目录即可：

```bash
rm -rf .image-cache/ .wsl-cache/
```

## 与 docker-cache-cmd Skill 的关系

本项目的镜像缓存机制与 SpecWeave 全局的 [docker-cache-cmd](../../../../.agents/skills/docker-cache-cmd/SKILL.md) Skill 设计理念一致：
- 镜像归档到 Windows 文件系统（持久化）
- WSL 重置后快速恢复
- 智能构建（基于 checksum 判断缓存命中）
- 并发安全（文件锁）
- 多线程压缩（pigz 优先）

但本项目的 `jpman save/load` 是针对 jupyter-podman-rootless 的专用实现，额外支持：
- 自动 manifest 生成
- 软链接到 latest
- 与 wsl-export 集成
- gzip 完整性验证
