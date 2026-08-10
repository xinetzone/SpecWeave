# Docker 镜像本地缓存管理系统 - Product Requirement Document

## Overview
- **Summary**: 在 SpecWeave 项目中构建一套 Docker 镜像本地缓存管理系统，通过 `docker save/load` 将构建好的开发镜像（devcontainer-base 变体系列 + chaos-ai-npu + xmnn-whl-builder）以 tar.gz 格式存档到项目内的 `.docker-cache/` 目录，并提供统一的 shell 脚本 `docker-cache` 实现自动化的 save/load/build/list/clean/doctor 操作，加速 WSL2 环境下的开发迭代。
- **Purpose**: 当前 Docker 镜像存储在 WSL2 虚拟磁盘中，WSL 重置或 Docker 数据损坏后需要从头重建整个6层依赖链（约20-40分钟），严重影响开发效率。本系统通过在 Windows 持久化文件系统中保存镜像存档，实现镜像的快速备份与恢复，将环境重建时间从数十分钟缩短到2-5分钟。
- **Target Users**: SpecWeave 项目开发者（在 WSL2/Linux 环境下使用 Docker 进行 devcontainer 构建）。

## Goals
- 提供统一的 `docker-cache` CLI 工具，支持 save/load/build/list/clean/doctor 子命令
- 镜像存档持久化到 Windows 文件系统 `.docker-cache/images/` 目录，WSL 重置后不丢失
- 智能构建：`docker-cache build <variant>` 自动优先从缓存 load，不存在则从 Dockerfile 构建，构建后自动 save
- 维护 `manifest.json` 记录镜像元数据（名称、标签、大小、构建时间、存档路径、依赖关系）
- 提供 `doctor` 命令检查环境一致性和磁盘空间
- 提供 `clean` 命令按年龄/数量清理过期存档，支持 `--dry-run`
- 与现有构建脚本集成：`variants/build.sh`、`local-build.sh`、`chaos/ai/build.sh` 支持 `--use-cache` 参数
- 多线程压缩（pigz）加速 save/load，支持配置压缩级别
- 文件锁防止并发操作导致损坏，原子写入保证一致性

## Non-Goals (Out of Scope)
- 不搭建本地 Docker Registry（保持零依赖，仅用 docker save/load 标准命令）
- 不修改 Docker daemon 的 data-root 配置（避免 WSL2 环境复杂性）
- 不处理跨机器镜像分发（仅本地缓存，如需分发可手动拷贝 tar 文件）
- 不缓存 Dockerfile 构建过程中的中间层缓存（中间层由 Docker 内部 BuildKit 缓存管理，本系统只缓存最终镜像）
- 不替代 CI/CD 镜像仓库
- 不自动缓存所有镜像，默认只缓存用户显式 save 或通过 `docker-cache build` 构建的镜像

## Background & Context
- 当前存在的镜像（截图中）：
  - devcontainer-base:latest (~1.35GB)
  - devcontainer-base:conda-latest (~2.53GB)
  - devcontainer-base:conda-llvm-latest (~6.17GB)
  - devcontainer-base:onnx-pytorch-latest (~7.7GB)
  - devcontainer-base:onnx-quantized-latest (~7.7GB)
  - devcontainer-base:chaos-ai-npu-latest (~7.82GB)
  - xmnn-whl-builder:latest (~9.35GB)
- 镜像依赖链：base → conda → conda-llvm → onnx-pytorch → onnx-quantized → chaos-ai-npu → xmnn-whl-builder
- 全量构建耗时：约20-40分钟（取决于网络和CPU）
- docker load 单个7-9GB镜像耗时：约2-5分钟（使用 pigz 多线程解压）
- 构建脚本位置：
  - apps/devcontainer-base/scripts/build.sh（base镜像）
  - apps/devcontainer-base/variants/build.sh（变体镜像）
  - apps/devcontainer-base/scripts/local-build.sh（本地CI一键构建）
  - external/chaos/ai/build.sh（chaos-ai-npu变体）
  - external/chaos/ai/xmnn-whl-builder/build-wheel.sh（含镜像构建）
- 环境：WSL2 Ubuntu 24.04/26.04 + Docker（dockerd 或 Docker Desktop）
- 之前有一个简单的单次导出任务（docker-image-save-20260727），但未形成系统化工具

## Functional Requirements
- **FR-1**: 提供 `scripts/docker-cache`（bash脚本）作为统一入口，支持子命令：save/load/build/list/clean/doctor
- **FR-2**: `save <image> [--compress <level>]` - 将指定镜像保存到 `.docker-cache/images/` 目录，自动处理路径转换（WSL路径↔Windows路径）
- **FR-3**: `load <image>` - 从存档加载镜像到 Docker daemon，加载前检查完整性
- **FR-4**: `build <variant> [--cn] [--tag TAG] [--no-cache]` - 智能构建：先检查本地存档是否有对应镜像，有则 load 并验证，无则调用现有构建脚本构建，构建成功后自动 save
- **FR-5**: `list [--format table|json]` - 列出本地存档中的所有镜像，显示名称、标签、大小、构建日期
- **FR-6**: `clean [--age <days>] [--keep <n>] [--dry-run]` - 清理旧存档，默认保留最近3个版本，支持按天数保留
- **FR-7**: `doctor` - 检查 Docker 是否运行、缓存目录是否存在、manifest一致性、磁盘空间、pigz可用性
- **FR-8**: 维护 `.docker-cache/manifest.json`，记录每个存档的元数据（image, tag, size, created_at, archive_path, checksum）
- **FR-9**: 使用 flock 文件锁防止并发 save/load 操作
- **FR-10**: 原子写入：先写入临时文件再 mv 到最终路径，防止中途中断导致损坏
- **FR-11**: 支持环境变量 `DOCKER_CACHE_DIR` 自定义缓存根目录（默认：项目根目录 `.docker-cache/`）
- **FR-12**: `.docker-cache/` 加入项目 `.gitignore`
- **FR-13**: 压缩使用 pigz（多线程gzip），如果 pigz 不可用则降级为 gzip；支持 `--compress 0`（不压缩，最快）到 `--compress 9`（最高压缩）
- **FR-14**: 在现有构建脚本中增加缓存集成点（或提供 wrapper 方式，不破坏原有脚本独立性）

## Non-Functional Requirements
- **NFR-1**: `docker-cache load` 一个 8GB 镜像在 WSL2 原生文件系统上耗时 ≤5 分钟（使用 pigz -1）
- **NFR-2**: `docker-cache list` 响应时间 ≤1 秒
- **NFR-3**: 脚本零额外依赖（仅使用 bash + docker 标准命令 + 可选 pigz）
- **NFR-4**: 脚本兼容 bash 4.0+，支持 WSL2 和原生 Linux
- **NFR-5**: 所有错误消息清晰可操作（指出问题原因和修复建议）
- **NFR-6**: 彩色输出（TTY时），非TTY时自动禁用颜色（兼容CI/脚本调用）
- **NFR-7**: 缓存损坏不致命：load 失败时自动 fallback 到从 Dockerfile 构建

## Constraints
- **Technical**: Docker 运行在 WSL2 中，存档目录通过 `/mnt/d/` 跨文件系统访问（性能比原生慢但持久可靠）
- **Platform**: WSL2 Linux（主要）+ 原生 Linux（兼容）
- **Dependencies**: 仅依赖 docker 命令；pigz 为可选依赖（自动检测，缺失时降级）
- **Project**: 脚本放在 `scripts/docker-cache` 或 `.agents/scripts/` 下？考虑到这是项目级开发工具，放在 `scripts/docker-cache` 更合适（与 bundle-project.ps1 同级）；或者放在 `apps/devcontainer-base/scripts/` 下，因为主要服务于 devcontainer 构建。考虑到需要服务多个子目录（apps/devcontainer-base + external/chaos/ai + xmnn-whl-builder），放项目根 `scripts/` 下更统一。
- **Naming**: 镜像存档命名规范：`<repository-sanitized>_<tag>.tar.gz`（例如 `devcontainer-base_chaos-ai-npu-latest.tar.gz`）
- **Storage**: .docker-cache/ 默认在项目根，可能占用较大空间（~50GB 全量存档），用户通过 DOCKER_CACHE_DIR 可指定到其他盘

## Assumptions
- Docker daemon 正在运行且用户有权限执行 docker 命令
- WSL2 中可以访问 /mnt/d/（Windows D盘）
- 用户有足够的磁盘空间存储镜像存档
- pigz 通过 apt 可安装（`sudo apt install pigz`），或用户可接受 gzip 单线程压缩
- 存档放在 Windows 文件系统（/mnt/d/）是可接受的——虽然跨 FS 读写较慢，但持久化是首要需求，且 save/load 不是高频操作

## Acceptance Criteria

### AC-1: docker-cache 脚本存在且可执行
- **Given**: 项目根目录 scripts/ 下
- **When**: 运行 `bash scripts/docker-cache --help`
- **Then**: 显示帮助信息，列出所有子命令（save/load/build/list/clean/doctor），退出码 0
- **Verification**: `programmatic`

### AC-2: save 命令能正确保存镜像
- **Given**: Docker 中存在镜像 devcontainer-base:chaos-ai-npu-latest
- **When**: 运行 `bash scripts/docker-cache save devcontainer-base:chaos-ai-npu-latest`
- **Then**: 在 `.docker-cache/images/` 下生成 tar.gz 文件，manifest.json 更新，命令输出显示大小和耗时
- **Verification**: `programmatic`

### AC-3: load 命令能正确恢复镜像
- **Given**: `.docker-cache/images/` 中存在某个镜像的存档
- **When**: 先 `docker rmi` 删除本地镜像，再运行 `bash scripts/docker-cache load <image>`
- **Then**: 镜像被重新加载到 Docker daemon，`docker images` 可见，镜像ID/标签一致
- **Verification**: `programmatic`

### AC-4: build 命令智能判断缓存
- **Given**: 本地无存档，Docker 中有基础镜像
- **When**: 运行 `bash scripts/docker-cache build chaos-ai-npu --cn`
- **Then**: 调用构建脚本构建镜像，构建成功后自动 save 到缓存
- **Verification**: `programmatic`

### AC-5: build 命令能从缓存恢复
- **Given**: 本地有存档但 Docker 中无该镜像（模拟 WSL 重置后场景）
- **When**: 运行 `bash scripts/docker-cache build chaos-ai-npu`
- **Then**: 自动从存档 load 镜像，跳过 Dockerfile 构建，输出 "Loaded from cache"
- **Verification**: `programmatic`

### AC-6: list 命令显示存档列表
- **Given**: 有若干镜像存档
- **When**: 运行 `bash scripts/docker-cache list`
- **Then**: 以表格形式显示镜像名、标签、大小、创建日期
- **Verification**: `human-judgment`

### AC-7: clean 命令正确清理旧存档
- **Given**: 存在多个标签相同但日期不同的存档
- **When**: 运行 `bash scripts/docker-cache clean --keep 2 --dry-run`
- **Then**: 列出将被删除的文件但不实际删除；不加 --dry-run 时实际删除，只保留最近2个
- **Verification**: `programmatic`

### AC-8: doctor 命令诊断环境
- **Given**: 正常环境（Docker运行中, 磁盘充足）
- **When**: 运行 `bash scripts/docker-cache doctor`
- **Then**: 逐项检查并输出 OK/WARN/FAIL，最终给出总结
- **Verification**: `human-judgment`

### AC-9: 并发安全
- **Given**: 两个终端同时运行 save 同一个镜像
- **When**: 并行执行两次 save
- **Then**: 第二个等待锁释放后执行，不会产生损坏文件
- **Verification**: `programmatic`

### AC-10: .gitignore 排除缓存目录
- **Given**: .docker-cache/ 有文件
- **When**: 运行 `git status`
- **Then**: .docker-cache/ 不出现在未跟踪文件列表中
- **Verification**: `programmatic`

### AC-11: 缓存损坏自动降级
- **Given**: 某个 tar.gz 文件被手动截断损坏
- **When**: 运行 load 或 build 命令使用该损坏文件
- **Then**: 检测到损坏（checksum 不匹配或 docker load 失败），报告警告，自动 fallback 到 Dockerfile 构建
- **Verification**: `programmatic`

### AC-12: 帮助信息完整且对新人友好
- **Given**: 无经验的新开发者
- **When**: 阅读 --help 输出和脚本头部注释
- **Then**: 能理解每个命令的用途，有快速开始示例
- **Verification**: `human-judgment`

## Open Questions
- [ ] 存档目录默认放在项目根 `.docker-cache/` 还是放在项目外（如 `D:\docker-cache\SpecWeave/`）？——项目内更自包含，但会占用项目所在盘空间；建议默认项目内，通过 DOCKER_CACHE_DIR 支持自定义
- [ ] 是否需要在构建时自动 save 所有依赖链镜像（如 build chaos-ai-npu 时也自动 save onnx-quantized、onnx-pytorch 等）？——建议默认只 save 目标镜像，提供 `--save-deps` 选项递归 save 所有依赖
- [ ] 压缩级别默认值：0（不压缩最快）还是1（快速压缩，体积减小约30-40%）？——建议默认1，平衡速度和体积；提供 `--fast` 别名等于 --compress 0
