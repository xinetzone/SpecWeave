---
id: "jupyter-wsl-export"
title: "WSL2 发行版导出与使用"
source: "bin/jpman"
---
# WSL2 发行版导出与使用

jpman 提供一键将容器镜像导出为独立 WSL2 发行版的功能，无需运行 Podman 即可直接使用 Jupyter 环境。导出的发行版包含完整的 Conda/Python 环境，并自动配置默认用户和 Conda 激活。

## 快速开始

```bash
# 1. 先确保镜像已构建或已缓存
bash bin/jpman rebuild-all   # 或 bash bin/jpman load（从缓存加载）

# 2. 一键导出为 WSL2 发行版
bash bin/jpman wsl-export

# 3. 验证环境（可选，自动在导出后运行）
bash bin/jpman wsl-verify

# 4. 进入 WSL 发行版
wsl -d jupyter-podman-rootless
```

## 导出流程

`wsl-export` 命令自动执行以下 5 个步骤：

1. **加载镜像**：从 `.image-cache/` 加载镜像到 Podman（如已存在则跳过）
2. **导出 rootfs**：创建临时容器，导出为 gzip 压缩的 rootfs tarball
3. **导入 WSL**：使用 `wsl --import` 导入到指定目录
4. **配置系统**：写入 `/etc/wsl.conf`，配置默认用户和 Conda 激活
5. **验证环境**：运行冒烟测试，检查基础环境、Python/Conda、Jupyter 等

## 命令选项

```bash
# 指定发行版名称
bash bin/jpman wsl-export --distro-name my-jupyter
# 或
bash bin/jpman wsl-export -n my-jupyter

# 指定安装目录（默认 .wsl-cache/<distro-name>/）
bash bin/jpman wsl-export --install-dir /mnt/d/wsl/my-jupyter
# 或
bash bin/jpman wsl-export -d /mnt/d/wsl/my-jupyter

# 强制覆盖已存在的发行版
bash bin/jpman wsl-export --force
# 或
bash bin/jpman wsl-export -f
```

## 使用导出的 WSL 发行版

### 进入环境

```bash
wsl -d jupyter-podman-rootless
```

默认以 `devuser` 身份登录，Conda base 环境自动激活。

### 启动服务

在 WSL 发行版中，supervisord 不会自动启动，需手动启动：

```bash
# 方式一：先进入WSL发行版（交互式shell，Conda自动激活），再运行命令
wsl -d jupyter-podman-rootless
# 进入后执行：
jupyter lab --no-browser --ip=0.0.0.0
# 或启动 SSH + Jupyter（以 root 运行 supervisord）
sudo supervisord -c /etc/supervisor/supervisord.conf

# 方式二：直接从Windows命令行运行（使用登录shell -l 加载profile）
# 启动 Jupyter Lab
wsl -d jupyter-podman-rootless -- sh -l -c "jupyter lab --no-browser --ip=0.0.0.0"
# 启动 SSH + Jupyter（以 root 运行 supervisord）
wsl -d jupyter-podman-rootless -u root -- sh -l -c "supervisord -c /etc/supervisor/supervisord.conf"
```

> ⚠️ **重要**：直接使用 `wsl -d DISTRO -- CMD` 是非登录shell，不会加载 `/etc/profile.d/conda.sh`，会导致 `jupyter: command not found` 错误。必须使用 `-l`（login shell）参数，或先进入交互式shell。

### Windows 驱动器挂载

WSL 发行版默认挂载 Windows 驱动器：
- C: 盘 → `/mnt/c/`
- D: 盘 → `/mnt/d/`
- 等等...

`automount` 配置在 `/etc/wsl.conf` 中设置，启用 `metadata` 选项支持 Linux 权限。

## 环境验证

`wsl-verify` 命令运行一系列冒烟测试，确保环境正常：

```bash
bash bin/jpman wsl-verify
# 或验证指定发行版
bash bin/jpman wsl-verify my-jupyter
```

### 检查项

| 类别 | 检查项 |
|------|--------|
| 基础环境 | Startup、User（devuser）、Writable、Home dir |
| 驱动器挂载 | C: drive、D: drive（如存在） |
| Python/Conda | Conda 版本、Python 版本（3.14+）、Python 路径（/opt/conda） |
| Free-threading | GIL 禁用状态（sys._is_gil_enabled() == False） |
| 工具 | Pip、JupyterLab、Git、Bash、Locale（zh_CN.UTF-8） |

验证输出示例：

```
🔍 WSL Distro Verification: jupyter-podman-rootless

  Basic Environment
  [Startup]      ✅ PASS → OK
  [User]         ✅ PASS → devuser
  [Writable]     ✅ PASS → WRITABLE
  [Home dir]     ✅ PASS → /home/devuser

  Drive Mounts
  [C: drive]     ✅ PASS → C-MOUNT-OK
  [D: drive]     ✅ PASS → D-MOUNT-OK

  Python/Conda Environment
  [Conda]        ✅ PASS → conda 24.x.x
  [Python]       ✅ PASS → Python 3.14.0
  [Python path]  ✅ PASS → /opt/conda/bin/python
  [Free-thread]  ✅ PASS → GIL disabled (free-threading active)
  [Pip]          ✅ PASS → pip 24.x

  Jupyter & Tools
  [JupyterLab]   ✅ PASS → 4.4.x
  [Git]          ✅ PASS → git version 2.x
  [Bash]         ✅ PASS → GNU bash 5.x
  [Locale]       ✅ PASS → LANG=zh_CN.UTF-8

  Results: 16 passed, 0 failed
```

## 配置说明

### /etc/wsl.conf

自动生成的 wsl.conf 配置：

```ini
[user]
default=devuser

[boot]
systemd=false

[automount]
enabled=true
mountFsTab=true
options="metadata,umask=0022,fmask=0011,dmask=0000"

[network]
generateHosts=true
generateResolvConf=true
```

### Conda 激活

自动创建 `/etc/profile.d/conda.sh`，登录时自动激活 base 环境：

```bash
. /opt/conda/etc/profile.d/conda.sh
conda activate base
```

## 管理 WSL 发行版

```bash
# 列出所有 WSL 发行版
wsl -l -v

# 终止发行版（重启时应用配置变更）
wsl --terminate jupyter-podman-rootless

# 关闭 WSL（完全重启）
wsl --shutdown

# 删除发行版
wsl --unregister jupyter-podman-rootless
```

## 常见问题

### Q: 默认用户不是 devuser？

A: 运行 `wsl --shutdown` 完全关闭 WSL 后重试，或手动检查 `/etc/wsl.conf` 中的 `default` 设置。

### Q: Conda 没有自动激活？

A: 检查 `/etc/profile.d/conda.sh` 是否存在且可执行，或手动运行 `source /opt/conda/etc/profile.d/conda.sh && conda activate base`。

### Q: 驱动器没有挂载？

A: 确保 WSL Interop 已启用，检查 `/etc/wsl.conf` 中的 `[automount]` 设置。

### Q: 运行 `wsl -d jupyter-podman-rootless -- jupyter lab` 报错 "command not found"？

A: 这是因为 `wsl -- CMD` 使用非登录shell，不会加载profile文件，Conda没有被激活。解决方案：

1. **推荐**：先进入交互式shell再运行命令：
   ```bash
   wsl -d jupyter-podman-rootless
   jupyter lab --no-browser --ip=0.0.0.0
   ```

2. 使用登录shell参数 `-l`：
   ```bash
   wsl -d jupyter-podman-rootless -- sh -l -c "jupyter lab --no-browser --ip=0.0.0.0"
   ```

3. 或手动source Conda激活脚本：
   ```bash
   wsl -d jupyter-podman-rootless -- bash -c "source /opt/conda/etc/profile.d/conda.sh && conda activate base && jupyter lab --no-browser --ip=0.0.0.0"
   ```

### Q: 与直接运行容器的区别？

| 特性 | Podman 容器 | WSL 发行版 |
|------|------------|-----------|
| 需要 Podman | ✅ 是 | ❌ 否 |
| 服务自动启动 | ✅ supervisord | ❌ 需手动启动 |
| 资源隔离 | ✅ 容器隔离 | ❌ 共享 WSL 内核 |
| systemd | ❌ | ❌（默认禁用） |
| 跨发行版网络 | ✅ 容器网络 | ✅ localhost |
| 适合场景 | 开发服务器、多实例 | 交互式使用、快速启动 |
