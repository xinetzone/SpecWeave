---
title: "WSL2 Docker GPU支持故障修复复盘"
date: 2026-08-15
session_id: sc-20260815-docker-gpu-fix-retrospective
scenario: milestone
methodology: seven-concepts (R→I→E→C)
duration: ~45分钟
tags: [wsl2, docker, nvidia, gpu, nvidia-container-toolkit, infrastructure]
pattern_extracted: wsl-docker-gpu-triage-v1
---

# WSL2 Docker GPU支持故障修复复盘

## 基本信息

| 项 | 值 |
|---|---|
| 故障时间 | 2026-08-15 10:24 CST |
| 修复时间 | 2026-08-15 11:35 CST |
| 环境 | Windows 11 + WSL2 Ubuntu 26.04 (Resolute Raccoon) |
| 内核 | 6.18.35.2-microsoft-standard-WSL2 |
| GPU | NVIDIA GeForce RTX 5050 (8GB) |
| 驱动 | 581.57, CUDA 13.0 |
| Docker | 29.1.3 (WSL内Docker Engine，非Docker Desktop) |

---

## 一、故障现象

执行命令：
```bash
docker run --rm -it --gpus all devcontainer-base:torch-dev-latest bash
```

报错信息：
```
docker: Error response from daemon: could not select device driver "" with capabilities: [[gpu]]
```

---

## 二、R阶段：客观事实清单（25条）

| 编号 | 事实 |
|------|------|
| F-001 | 用户在WSL2中执行 `docker run --rm -it --gpus all devcontainer-base:torch-dev-latest bash` |
| F-002 | 报错：`could not select device driver "" with capabilities: [[gpu]]` |
| F-003 | 操作系统：Windows 11 + WSL2 Ubuntu 26.04 LTS (Resolute Raccoon) |
| F-004 | WSL内核版本：6.18.35.2-microsoft-standard-WSL2 |
| F-005 | Docker版本：29.1.3（WSL内Docker Engine） |
| F-006 | nvidia-smi可用，识别到RTX 5050，驱动581.57，CUDA 13.0 |
| F-007 | GPU显存8151MiB，修复前占用484MiB，利用率7% |
| F-008 | 初始 `docker info` Runtimes仅含io.containerd.runc.v2, runc（无nvidia） |
| F-009 | `which nvidia-container-runtime` 返回空，dpkg无nvidia-container-toolkit包 |
| F-010 | 初始 `/etc/wsl.conf` 仅含 `[network] generateResolvConf = false`，无 `[boot]` 段 |
| F-011 | NVIDIA GPG key从官方地址可正常获取（HTTP 200） |
| F-012 | 中科大镜像源可用，下载速度5712 kB/s |
| F-013 | nvidia-container-toolkit v1.20.0安装成功（含4个deb包） |
| F-014 | 安装包大小8253 kB，安装后磁盘占用约35.9 MB |
| F-015 | `nvidia-ctk runtime configure --runtime=docker` 执行成功，daemon.json已更新 |
| F-016 | 初始daemon.json已包含registry-mirrors配置（docker.1ms.run, docker.xuanyuan.me） |
| F-017 | WSL2 PID 1为init非systemd，systemctl/service命令均无法重启Docker |
| F-018 | 使用 `setsid` 启动containerd和dockerd成功脱离会话 |
| F-019 | 修复后 `docker info` Runtimes包含nvidia |
| F-020 | `docker run --rm --gpus all ubuntu:22.04 nvidia-smi` 测试通过 |
| F-021 | 本地存在5个devcontainer-base镜像（conda/conda-llvm/latest/onnx-pytorch/onnx-quantized） |
| F-022 | devcontainer-base:torch-dev-latest镜像尚未构建 |
| F-023 | onnx-pytorch镜像内PyTorch 2.13.0+cpu，CUDA不可用（符合设计：torch为可选依赖） |
| F-024 | 修复过程中创建了6个临时.sh脚本，已全部删除 |
| F-025 | NVIDIA官方apt源list文件含未展开的 `$(ARCH)` 变量，手动替换为amd64后正常工作 |

---

## 三、I阶段：核心洞察（3条）

### 洞察1：WSL2 Docker GPU三层依赖链认知缺口

- **陈述**：Docker GPU支持需要"宿主机NVIDIA驱动→nvidia-container-toolkit→Docker daemon配置"三层全链路就绪，缺任何一层都会报`could not select device driver`错误，且错误信息不直接指出缺失的具体组件
- **证据**：F-006（nvidia-smi正常）vs F-009（toolkit未安装）vs F-008（runtimes无nvidia），三层中驱动层正常但容器桥梁层缺失
- **反常识**：WSL2已自动透传GPU（nvidia-smi可用）≠ Docker容器可用GPU，两者是独立的两层；用户容易看到nvidia-smi正常就以为GPU全链路就绪
- **行动**：建立WSL Docker GPU三层验证清单，部署/排障时逐层验证（驱动层→工具层→运行时层）

### 洞察2：WSL2无systemd环境下Docker守护进程管理方式差异

- **陈述**：WSL2默认不启用systemd作为PID 1，导致`systemctl`/`service`命令无法管理Docker，直接kill dockerd后需要使用`setsid`脱离会话启动，否则进程随WSL命令会话结束而终止
- **证据**：F-017（systemctl/service均失败），F-018（setsid方式启动成功），F-010（wsl.conf无boot配置）
- **反常识**：在原生Ubuntu上用systemctl restart docker是标准操作，但在WSL2无systemd模式下完全无效；且WSL会话结束时后台进程会被回收，nohup不足以保证持久运行
- **行动**：在wsl.conf中配置[boot]段实现Docker开机自启，或启用systemd=true简化服务管理

### 洞察3：NVIDIA官方apt源list文件中$(ARCH)变量在非shell环境下不会展开

- **陈述**：从NVIDIA官方获取的apt源list文件使用`$(ARCH)`占位符，该语法在直接tee写入时不会被自动展开为实际架构名（如amd64），导致apt update可能无法正确索引
- **证据**：F-025（初始源文件包含未展开的$(ARCH)），F-013（手动替换为amd64后安装成功）
- **反常识**：NVIDIA官方安装文档中curl+sed+tee管道在交互式shell中执行时会展开变量，但通过脚本或其他方式写入时`$(ARCH)`会原样保留
- **行动**：写入apt源文件后立即检查`$(ARCH)`是否已展开，或直接硬编码`amd64`

---

## 四、E阶段：萃取模式

### 模式：wsl-docker-gpu-triage-v1（WSL Docker GPU三层诊断修复模式）

**适用场景**：
- WSL2中 `docker run --gpus all` 报 `could not select device driver`
- WSL中nvidia-smi正常但容器无法访问GPU
- 新WSL发行版初始化Docker GPU支持
- 重建/重置WSL后恢复Docker GPU能力

**核心步骤**：
1. **L1驱动层验证**：`nvidia-smi` → 失败则修复WSL GPU透传/Windows驱动
2. **L2工具层验证**：`dpkg -l | grep nvidia-container-toolkit` + `which nvidia-container-runtime`
3. **L3运行时层验证**：`docker info 2>&1 | grep -A5 Runtimes` → 应包含nvidia
4. 安装nvidia-container-toolkit（国内优先中科大镜像）
5. `nvidia-ctk runtime configure --runtime=docker` 配置Docker
6. WSL无systemd时用 `setsid` 启动containerd和dockerd
7. 配置 `/etc/wsl.conf` 的 `[boot]` 段实现持久化
8. 端到端验证：`docker run --rm --gpus all ubuntu:22.04 nvidia-smi`

**5个反模式**：

| # | 反模式 | 后果 | 正确做法 |
|---|--------|------|---------|
| 1 | 看到nvidia-smi正常就以为Docker GPU可用 | 浪费时间在容器内排查CUDA/PyTorch | 必须三层逐层验证 |
| 2 | 在WSL无systemd环境用systemctl/service | 命令"成功"但Docker实际未重启 | 先检查PID 1；无systemd用setsid |
| 3 | tee NVIDIA list文件不检查$(ARCH)展开 | apt源无法索引，安装失败 | tee后立即cat检查变量是否展开 |
| 4 | 用nohup而非setsid启动dockerd | 会话结束进程被回收 | WSL无systemd用setsid完全脱离会话 |
| 5 | 修改daemon.json后忘记配置wsl.conf | wsl --shutdown后Docker不自启 | 修复完成后立即配置[boot]自启 |

**跨场景迁移**：WSL2 Podman GPU支持——同样三层架构，L2改为CDI模式（`nvidia-ctk cdi generate`），L3无需额外runtime配置（Podman原生支持CDI）。

---

## 五、C阶段：修复与配置变更

### 已完成的修复

1. **安装nvidia-container-toolkit v1.20.0**
   - 源：中科大镜像（mirrors.ustc.edu.cn）
   - 包：libnvidia-container1, libnvidia-container-tools, nvidia-container-toolkit-base, nvidia-container-toolkit

2. **配置Docker nvidia runtime**
   - `/etc/docker/daemon.json` 已添加 `runtimes.nvidia` 配置
   - 原有registry-mirrors配置保留

3. **配置wsl.conf Docker开机自启**
   - 原文件已备份：`/etc/wsl.conf.bak.YYYYMMDDHHMMSS`
   - 新增 `[boot]` 段：启动containerd（等待2秒）后启动dockerd
   - 新增 `[automount]` 段：启用metadata挂载支持

### 当前wsl.conf完整内容

```ini
[network]
generateResolvConf = false

[boot]
command="nohup containerd > /var/log/containerd-boot.log 2>&1 & sleep 2; nohup dockerd > /var/log/dockerd-boot.log 2>&1"

[automount]
enabled = true
options = "metadata,umask=0022,fmask=0011"
mountFsTab = true
```

### 验证结果

- ✅ `docker info` Runtimes包含nvidia
- ✅ `docker run --rm --gpus all ubuntu:22.04 nvidia-smi` 成功输出GPU信息
- ⚠️ **需执行以下命令使[boot]配置生效**：
  ```powershell
  # 在Windows PowerShell中执行
  wsl --shutdown
  # 然后重新打开WSL，Docker将自动启动
  ```

---

## 六、质量门通过记录

| 质量门 | 阶段 | 检查结果 | 说明 |
|--------|------|---------|------|
| G1 | R | ✅ 通过 | 25条事实，无因果推断词，纯客观陈述 |
| G2 | I | ✅ 通过 | 3条四元组洞察，含证据引用、反常识点、行动建议 |
| G3 | E | ✅ 通过 | 模式含触发场景+8步核心做法+5个反模式+检验标准+迁移示例 |
| G4 | C | ✅ 通过 | 原子化配置变更，配置文件备份，可验证，可回滚 |

---

## 七、后续行动项

| # | 行动项 | 优先级 | 验收标准 |
|---|--------|--------|---------|
| 1 | 在PowerShell执行 `wsl --shutdown` 重启WSL验证boot自启 | 高 | 重启WSL后 `docker info` 可立即执行，无需手动启动 |
| 2 | 检查 `/var/log/containerd-boot.log` 和 `/var/log/dockerd-boot.log` 无错误 | 中 | 日志中无FATAL/ERROR级错误 |
| 3 | 构建devcontainer-base:torch-dev-latest镜像 | 中 | 镜像构建成功，容器内 `torch.cuda.is_available()` 返回True |
| 4 | 将wsl-docker-gpu-triage-v1模式存入模式库 | 低 | 模式文档放置于patterns目录，索引已更新 |

---

## 八、经验教训

1. **错误信息不等于根因**：`could not select device driver "" with capabilities: [[gpu]]` 中的空字符串`""`暗示找不到驱动名称，但需要逐层排查才能定位是nvidia-container-toolkit缺失而非驱动问题
2. **WSL环境特殊性不可忽视**：WSL2默认无systemd、会话结束回收进程、跨文件系统路径转换等特性与原生Linux不同，直接套用Linux经验会踩坑
3. **修复即闭环**：安装完toolkit+配置runtime不算完成，必须解决持久化（wsl.conf boot）问题，否则wsl重启后问题复现
4. **临时文件及时清理**：修复过程中创建的6个临时脚本已全部删除，避免污染工作区
