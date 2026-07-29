# WSL2 Docker 环境配置模板

> 将本模板复制到你的项目部署文档中，根据项目实际情况调整安装命令和推荐版本。

## Docker 环境

WSL2 中有两种 Docker 方案，根据使用场景选择：

### 方案 A：Docker Desktop for Windows（推荐新手/桌面开发）

1. 下载安装 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
2. 安装时勾选 "Use WSL 2 instead of Hyper-V"
3. 在 Settings → Resources → WSL Integration 中启用你的 WSL2 发行版
4. 在 WSL 中验证：

```bash
docker --version
docker compose version
docker run --rm hello-world
```

> **注意**：如果在 WSL 中遇到 `docker-credential-desktop.exe: exec format error`，编辑 `~/.docker/config.json`，删除或修改 `credsStore` 字段。

### 方案 B：WSL2 原生 Docker（推荐 CI/生产环境/性能敏感场景）

```bash
# 在 WSL Ubuntu 中执行（Ubuntu 24.04+ 推荐使用 systemd）
sudo apt update
sudo apt install -y docker.io

# 确保 /etc/wsl.conf 启用 systemd（Ubuntu 24.04+ 默认启用）：
# [boot]
# systemd=true
# 然后在 PowerShell 中执行: wsl --shutdown 重启WSL

sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
# 重新登录 WSL 使权限生效
```

> ⚠️ **两种方案二选一**，不要同时启用！否则会导致客户端/守护进程/凭证来源混乱。

### 性能对比（实测基准）

> **TODO**：在你的硬件环境中运行基准测试，替换以下数据为实际测量值。

| 指标 | Docker Desktop (WSL2后端) | WSL2 原生 Docker | 说明 |
|------|--------------------------|-------------------|------|
| **镜像构建时间** | ~X-Y 分钟 | ~A-B 分钟 | 原生 Docker 快约 N%（无跨VM IPC开销） |
| **容器启动时间** | ~X-Y 秒 | ~A-B 秒 | 差异较小 |
| **磁盘 I/O（编译）** | 基线（1x） | 快 N-M% | 原生Docker直接访问ext4 |
| **内存占用** | 额外 XXX MB-X GB | 仅守护进程 ~XXX MB | Desktop有Windows端GUI+代理进程开销 |
| **CPU 性能** | 基线（1x） | 快 N-M% | Desktop有轻微虚拟化开销 |
| **卷挂载性能（/mnt/d）** | 较好（SMB直连） | 一般（9p协议） | Desktop的Windows文件挂载性能更好 |
| **网络端口转发** | 自动绑定Windows端口 | 需手动配置 | Desktop自动处理localhost转发 |
| **首次安装配置** | ⭐⭐⭐⭐⭐（图形界面） | ⭐⭐⭐（命令行） | Desktop安装更简单 |
| **Kubernetes集成** | 一键启用 | 需手动安装 | Desktop内置K8s支持 |

### 方案选择建议

| 使用场景 | 推荐方案 | 理由 |
|----------|----------|------|
| 新手入门、桌面开发 | **Docker Desktop** | 一键安装、GUI管理、自动端口转发 |
| 性能敏感（频繁编译C++/Go/Rust） | **原生Docker** | 构建速度更快，编译I/O优势明显 |
| CI/CD 流水线（WSL runner） | **原生Docker** | 低内存占用、可脚本化、服务化管理 |
| 需要同时运行Windows容器 | **Docker Desktop** | 原生Docker仅支持Linux容器 |
| 代码放在Windows盘（/mnt/d/） | **Docker Desktop** | 9p协议在某些场景下I/O性能较差 |
| 代码放在WSL文件系统（~/projects） | **两者均可** | 原生Docker略快 |
| 需要Docker Desktop GUI功能 | **Docker Desktop** | Dashboard、Logs、Extensions等 |
| 低内存机器（≤16GB） | **原生Docker** | Desktop额外内存开销显著 |

> **推荐配置**：如果代码在WSL文件系统（`~/projects/`）内且有编译任务，**原生Docker性能更好**；如果代码在Windows挂载盘（`/mnt/d/`）或需要GUI功能，Docker Desktop更方便。
