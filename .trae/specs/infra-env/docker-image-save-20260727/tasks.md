# Docker 镜像导出归档 - Implementation Plan

## [x] Task 1: 前置检查（磁盘空间 + 镜像存在 + 目录可写）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 确认 Docker 服务运行中
  - 确认镜像 `caffe-cpu:standalone-jupyter-test` 存在且 ID 正确
  - 确认目标目录 `D:\BaiduSyncdisk\docker\` 可写
  - 检查目标磁盘可用空间（需 >5GB）
- **Acceptance Criteria Addressed**: AC-1 前置条件
- **Test Requirements**:
  - `programmatic` TR-1.1: `docker images` 显示 `caffe-cpu:standalone-jupyter-test` 存在 ✅
  - `programmatic` TR-1.2: 目标目录存在且可通过 WSL 路径 `/mnt/d/BaiduSyncdisk/docker/` 访问 ✅
  - `programmatic` TR-1.3: D 盘可用空间 >5GB（64GB available）✅
- **Status**: COMPLETED
- **Notes**: Docker 29.6.1 运行中，镜像 2.2GB（ID: 3998b17e0696），D盘可用64GB

## [x] Task 2: 执行 docker save 导出镜像（gzip 压缩）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 使用 WSL 执行 `docker save | gzip` 导出并压缩镜像
  - 输出文件路径: `/mnt/d/BaiduSyncdisk/docker/caffe-cpu-standalone-jupyter_20260727.tar.gz`
  - 完整命令: `wsl bash -c "docker save caffe-cpu:standalone-jupyter-test | gzip > /mnt/d/BaiduSyncdisk/docker/caffe-cpu-standalone-jupyter_20260727.tar.gz"`
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: 命令退出码为 0 ✅（输出 SAVE_DONE）
  - `programmatic` TR-2.2: 目标文件存在 ✅
  - `human-judgement` TR-2.3: 文件名格式 `caffe-cpu-standalone-jupyter_20260727.tar.gz` 清晰可识别 ✅
- **Status**: COMPLETED
- **Notes**: 2.2GB 镜像压缩至 490MB（压缩率 ~22%），耗时约 3 分钟

## [x] Task 3: 验证导出文件完整性
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 检查文件大小 > 100MB（gzip压缩后）
  - 使用 `gzip -t` 验证 gzip 完整性
  - 使用 `tar -tzf` 验证 tar.gz 文件可读且包含 `manifest.json`
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-3.1: 文件大小 490MB > 100MB ✅
  - `programmatic` TR-3.2: gzip 完整性校验通过（GZIP_OK）✅
  - `programmatic` TR-3.3: tar.gz 包含 manifest.json、oci-layout、index.json、blobs/sha256/（共40个文件）✅
  - `programmatic` TR-3.4: 旧文件 caffe-cpu-jupyter_20260727.tar（754MB）保留未被覆盖 ✅
- **Status**: COMPLETED
- **Notes**: 镜像格式为 OCI 标准布局，非传统 Docker save 格式；百度网盘已自动开始同步

## [x] Task 4: 输出结果汇总
- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 输出文件绝对路径
  - 输出文件大小（MB/GB）
  - 输出可用于加载的命令: `docker load -i <path>`
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `human-judgement` TR-4.1: 汇总信息清晰，包含路径、大小、加载命令 ✅
- **Status**: COMPLETED
