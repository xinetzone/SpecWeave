---
id: "docker-image-offline-export-distribution"
title: "Docker镜像离线构建-验证-导出-分发六步标准流程"
type: code-pattern
date: 2026-07-27
maturity: L2-validated
maturity_note: "本次caffe-cpu:jupyter构建导出任务完整验证通过，G1-G3质量门全部满足"
source:
  - "../../reports/build-engineering/retrospective-caffe-jupyter-docker-build-export-20260727/README.md#模式-p1docker镜像构建-验证-导出-分发六步标准流程"
related_patterns:
  - "compiled-wheel-runtime-image-build.md"
  - "docker-container-session-raii.md"
  - "wsl-distro-install-migration-guide.md"
  - "wsl-docker-command-safety.md"
  - "../architecture-patterns/docker-modular-build-orchestration.md"
tags: ["docker", "image-export", "offline-distribution", "docker-save", "docker-load", "quality-gate", "md5", "wsl", "image-verification", "deployment"]
validation_count: 1
reuse_count: 0
---

# Docker镜像离线构建-验证-导出-分发六步标准流程

## 触发场景

- 需要将Docker镜像导出为离线分发包（tar文件）
- 目标环境无法访问Docker镜像仓库（内网隔离、无网络、新机器部署）
- 需要确保镜像文件经传输/存储后仍可正确加载和运行
- 交付Docker镜像给无Docker经验的用户（需配套完整操作链）
- CI/CD流水线中的镜像归档与异地迁移

**识别信号**：
- "把镜像保存下来拷给我"
- "目标机器上不了网/没装Docker"
- "怎么把这个镜像导出成文件"
- `docker save`之后需要确认文件可用

**不适用场景**：
- 镜像仓库可用且可直接push/pull → 直接用registry，无需tar分发
- 镜像仅在本机使用不迁移 → 无需导出
- 使用OCI容器运行时（Podman等） → 命令类似但有细微差异，需对应调整

## 问题背景

### Docker镜像导出的常见陷阱

`docker save`看似简单，但实践中存在多个"虚假成功"陷阱：

1. **只检查文件存在即认为成功**：docker save可能因磁盘IO错误、文件系统满等原因写出损坏文件，但文件大小非零
2. **虚拟大小≠导出大小**：`docker images`显示的是解压后各层虚拟大小总和（含共享基础层），docker save输出是压缩tar，大小通常为虚拟大小的1/4到1/5。预期错误会导致错误判断文件是否完整
3. **docker save成功不代表tar可加载**：极端情况下（如存储驱动bug、磁盘静默错误），save写出的文件可能无法load
4. **docker load成功不代表功能可用**：load成功只是元数据和层写入存储，不代表镜像内的二进制、Python包、服务配置正确
5. **缺少校验值**：文件传输（U盘拷贝、网盘同步）过程中可能发生损坏，没有校验值无法在接收方验证完整性

### 镜像分层与压缩原理

Docker使用overlay2存储驱动，镜像由多个只读层组成：
- `docker images`的SIZE列：各层解压后虚拟大小的累加（基础层被多个镜像共享时会重复计算）
- `docker save`输出：各层的tar包集合，每层内部gzip压缩
- 典型压缩比：含大量二进制库和系统文件的镜像，压缩比通常为4:1到6:1

## 核心步骤（六步法）

### 步骤1：环境预检

在构建前检查环境状态，避免无效操作：

```bash
# Docker daemon状态
docker info >/dev/null 2>&1 || { echo "Docker daemon not running"; exit 1; }

# 磁盘空间（导出文件通常需要2倍虚拟大小的临时空间）
df -h .

# 构建上下文完整性（关键文件存在）
test -f Dockerfile && echo "Dockerfile exists"
# 检查是否有同名运行中容器需要清理
docker ps -a --filter "name=<container-name>" --format "{{.Names}}"
```

### 步骤2：执行构建

使用多阶段构建的target参数，明确镜像标签：

```bash
docker build \
  -t <image-name>:<tag> \
  --target <stage-name> \
  -f <dockerfile-path> \
  <build-context>

# 示例：
docker build -t caffe-cpu:jupyter --target runtime-jupyter \
  -f docker/origin/Dockerfile.jupyter-ssh .
```

**要点**：
- 构建成功的标志是看到 `naming to docker.io/library/<name>:<tag>: done`
- 记录输出的镜像ID（`docker images <name>:<tag> --format "{{.ID}}"`）

### 步骤3：功能验证（G1质量门）

运行临时容器验证核心功能，避免构建了"表面成功但内部损坏"的镜像：

```bash
# 基础命令验证（根据镜像内容调整）
docker run --rm <image-name>:<tag> python -c "import caffe; print(caffe.__version__)"
docker run --rm <image-name>:<tag> which caffe
docker run --rm <image-name>:<tag> bash -n /entrypoint.sh  # 脚本语法检查

# 服务类镜像验证（启动后检查）
docker run -d --name <test-container> -p <port>:<port> <image-name>:<tag>
sleep 5  # 等待服务启动
docker exec <test-container> <healthcheck-command>
# 验证后清理
docker stop <test-container> && docker rm <test-container>
```

**验证维度**：
- 核心二进制/库可导入/执行
- CLI工具可用
- 配置文件语法正确
- 服务能正常启动（非必须绕过entrypoint，优先验证完整启动链）
- 元数据正确（用户、环境变量、工作目录）

### 步骤4：导出镜像

```bash
# 生成带日期戳的文件名，避免覆盖历史版本
TODAY=$(date +%Y%m%d)
TAR_FILE="<image-name>-<tag>_${TODAY}.tar"

# 导出（WSL中注意路径格式为/mnt/盘符/路径）
docker save -o "/path/to/output/${TAR_FILE}" <image-name>:<tag>

# 计算校验值（MD5或SHA256）
md5sum "/path/to/output/${TAR_FILE}" > "/path/to/output/${TAR_FILE}.md5"
# 或：sha256sum "/path/to/output/${TAR_FILE}" > "/path/to/output/${TAR_FILE}.sha256"

# 记录文件大小和镜像ID
ls -lh "/path/to/output/${TAR_FILE}"
docker images <image-name>:<tag> --format "ImageID: {{.ID}}, Size: {{.Size}}"
```

**关键质量门（G2）**：
- 文件存在且大小 > 预期最小值（通常不小于虚拟大小的1/10）
- MD5/SHA256校验文件已生成
- 在Windows资源管理器/Finder中确认文件可见（路径无编码问题）

### 步骤5：完整性闭环验证（G3质量门·不可省略）

**这是最容易被跳过但最重要的一步**——删除本地镜像后从tar重新加载，验证分发包可用：

```bash
# 1. 删除本地镜像（确认tar文件已写入磁盘后再操作）
docker rmi <image-name>:<tag>
# 确认删除成功
docker images <image-name>:<tag>  # 应无输出

# 2. 从tar加载
docker load -i "/path/to/output/${TAR_FILE}"
# 成功标志：看到 "Loaded image: <image-name>:<tag>"

# 3. 验证镜像ID一致性
LOADED_ID=$(docker images <image-name>:<tag> --format "{{.ID}}")
echo "Loaded image ID: ${LOADED_ID}"
# 应与构建时记录的镜像ID一致

# 4. 重新执行功能验证（同步骤3）
docker run --rm <image-name>:<tag> <verify-command>
```

**为什么这步不可省略**：
- 只有docker load成功，才能证明tar格式完整
- 只有功能验证通过，才能证明层数据未损坏
- 镜像ID一致证明元数据和manifest完整
- 提前在构建方发现问题，远比交付到用户现场后发现成本低

### 步骤6：分发交付

交付物清单：
1. **tar镜像文件**：`<image-name>-<tag>_<date>.tar`
2. **校验文件**：`<image-name>-<tag>_<date>.tar.md5`（或.sha256）
3. **接收方操作指南**（README.txt），包含：

```text
=== 部署指南 ===

1. 安装Docker（目标机器）
   Ubuntu:  sudo apt update && sudo apt install docker.io
   Windows: 安装Docker Desktop
   macOS:   安装Docker Desktop

2. 验证文件完整性（在tar文件所在目录执行）
   md5sum -c <image-name>-<tag>_<date>.tar.md5
   # 应输出: <filename>: OK

3. 加载镜像
   docker load -i <image-name>-<tag>_<date>.tar
   # 应输出: Loaded image: <image-name>:<tag>

4. 验证镜像
   docker run --rm <image-name>:<tag> <verify-command>

5. 启动容器（根据实际端口和卷调整）
   docker run -d --name <container-name> \
     -p <host-port>:<container-port> \
     -v <host-data-dir>:<container-data-dir> \
     <image-name>:<tag>

6. 查看日志确认服务正常
   docker logs <container-name>
```

## WSL环境特殊说明

在Windows WSL中执行docker save时，注意**三层Shell嵌套**问题（PowerShell → wsl.exe → bash）：

```powershell
# ✅ 正确：直接传路径，不用bash -c包裹变量
wsl -d Ubuntu-24.04 -- docker save -o /mnt/d/BaiduSyncdisk/docker/image_tag.tar image:tag

# ❌ 错误：$VAR在PowerShell中被提前展开为空字符串
wsl -d Ubuntu-24.04 -- bash -c "TAR_FILE=/path/to/file.tar && docker save -o $TAR_FILE image:tag"
# 实际执行：docker save -o image:tag（缺少输出路径参数）

# ✅ 替代：如需复杂逻辑，写成.sh脚本在WSL内执行
wsl -d Ubuntu-24.04 -- bash /mnt/d/path/to/export-script.sh
```

详见 [wsl-docker-command-safety.md](wsl-docker-command-safety.md)。

## 反模式

| 反模式 | 风险 | 正确做法 |
|--------|------|---------|
| docker save后只看文件存在即成功 | 文件可能损坏，交付到现场才发现 | 执行步骤5的删除-加载-验证闭环 |
| 用`docker images`的SIZE预期导出文件大小 | 虚拟大小≠压缩大小，错误判断文件完整性 | 了解压缩比通常4:1~6:1，设置合理最小大小阈值 |
| 导出后用gzip二次压缩tar | docker save已是压缩tar，二次压缩收益<5%但增加加载解压步骤 | 直接分发tar，如需更小体积用xz（但增加接收方解压步骤） |
| 绕过entrypoint直接`docker run --rm img cmd`验证服务 | 缺少运行时初始化（密钥生成、权限修复等） | 优先`docker run -d`启动完整容器后`docker exec`验证 |
| 不生成MD5/SHA校验值 | 传输损坏后无法定位问题 | 每次导出必生成校验文件 |
| 用`docker commit`保存运行中容器状态 | 不可复现、无Dockerfile、层膨胀 | 始终用Dockerfile构建，docker save导出 |
| 交付tar时不提供操作指南 | 用户不知道怎么加载启动，增加沟通成本 | 配套提供完整README.txt |

## 质量门检查清单

- [ ] **G1-构建验证**：镜像构建成功，核心功能临时容器验证通过
- [ ] **G2-导出验证**：tar文件存在、大小合理、校验值已生成
- [ ] **G3-加载验证**：删除镜像→从tar加载→镜像ID一致→功能验证通过（不可省略）
- [ ] **交付物完整**：tar文件 + 校验文件 + 操作指南

## 验证案例

| 案例 | 镜像 | 虚拟大小 | tar大小 | 压缩比 | 验证结果 |
|------|------|---------|---------|--------|---------|
| caffe-cpu:jupyter | caffe-cpu:jupyter (ffedc7f18597) | 3.59 GB | 754 MB | 4.8:1 | ✅ G1-G3全通过 |

## 相关模式

- [wsl-docker-command-safety.md](wsl-docker-command-safety.md) — WSL环境Docker命令安全模式（步骤4的WSL陷阱详解）
- [docker-container-session-raii.md](docker-container-session-raii.md) — Docker容器会话RAII模式（步骤3验证容器的自动清理）
- [compiled-wheel-runtime-image-build.md](compiled-wheel-runtime-image-build.md) — 编译型Python Wheel运行时镜像构建
- [../architecture-patterns/docker-modular-build-orchestration.md](../architecture-patterns/docker-modular-build-orchestration.md) — Docker模块化构建编排
