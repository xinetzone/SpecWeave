# Docker 镜像导出归档 - Product Requirement Document

## Overview
- **Summary**: 使用 `docker save` 命令将已构建好的 `caffe-cpu:standalone-jupyter-test` 镜像（2.2GB）导出为 tar 归档文件，保存到 `D:\BaiduSyncdisk\docker\` 目录，便于离线分发和备份。
- **Purpose**: 镜像已构建并验证通过，需要导出为本地文件以便在无网络环境中部署或长期归档。
- **Target Users**: 项目开发者/运维人员（本地操作）。

## Goals
- 将 `caffe-cpu:standalone-jupyter-test` 镜像完整保存为 tar 文件
- 文件命名清晰可识别（包含镜像名和日期）
- 保存过程无损坏，文件可被 `docker load` 正确加载
- 文件位于 `D:\BaiduSyncdisk\docker\` 目录

## Non-Goals (Out of Scope)
- 不导出 `caffe-cpu:standalone-pycaffe-test` 镜像（用户未要求）
- 不压缩镜像（docker save 默认 tar 格式，gzip 压缩由用户决定）
- 不推送到远程镜像仓库
- 不同时导出其他已存在的镜像

## Background & Context
- 镜像 `caffe-cpu:standalone-jupyter-test`（ID: 3998b17e0696, 2.2GB）已在之前的 standalone caffex 依赖移除任务中构建并验证通过
- 目标目录 `D:\BaiduSyncdisk\docker\` 已存在，且已有一个历史归档 `caffe-cpu-jupyter_20260727.tar`（790MB，可能是早期版本或压缩版本）
- Docker 运行在 WSL2 中，需要通过 WSL 路径访问 Windows 磁盘（`/mnt/d/BaiduSyncdisk/docker/`）

## Functional Requirements
- **FR-1**: 使用 `docker save -o` 命令将镜像导出为 tar 文件
- **FR-2**: 输出文件名包含镜像标识和日期，格式建议 `caffe-cpu-standalone-jupyter_YYYYMMDD.tar`
- **FR-3**: 保存到指定路径 `D:\BaiduSyncdisk\docker\`
- **FR-4**: 保存完成后验证文件存在、大小合理（>2GB，镜像压缩层后）
- **FR-5**: 使用 `docker save` 输出进度或验证 tar 完整性

## Non-Functional Requirements
- **NFR-1**: 保存过程不中断（2.2GB 镜像预计需要 1-3 分钟）
- **NFR-2**: 文件命名一致，与现有归档 `caffe-cpu-jupyter_20260727.tar` 风格统一
- **NFR-3**: 磁盘空间检查：确保目标磁盘有至少 5GB 可用空间

## Constraints
- **Technical**: Docker 通过 WSL2 运行，Windows 路径需转换为 WSL 挂载路径（`/mnt/d/...`）
- **Platform**: Windows + WSL2 + Docker Desktop
- **Dependencies**: Docker Desktop 必须运行中

## Assumptions
- 目标目录 `D:\BaiduSyncdisk\docker\` 已存在且有写入权限
- Docker Desktop 正在运行且镜像 `caffe-cpu:standalone-jupyter-test` 存在
- 磁盘有足够空间保存 ~2.2GB 的 tar 文件

## Acceptance Criteria

### AC-1: 镜像文件成功保存到指定目录
- **Given**: Docker 镜像 `caffe-cpu:standalone-jupyter-test` 存在且 Docker 服务运行中
- **When**: 执行 `docker save -o <path>/<filename>.tar caffe-cpu:standalone-jupyter-test`
- **Then**: 目标路径下生成 tar 文件，命令退出码为 0
- **Verification**: `programmatic`

### AC-2: 文件命名规范可识别
- **Given**: 导出操作完成
- **When**: 检查生成的文件名
- **Then**: 文件名包含镜像标识（caffe-cpu-standalone-jupyter）和日期（20260727），格式统一
- **Verification**: `human-judgment`

### AC-3: 文件大小合理且非空
- **Given**: 导出操作完成
- **When**: 检查文件大小
- **Then**: 文件大小 > 1GB（原始镜像 2.2GB，docker save 后通常略小或接近）
- **Verification**: `programmatic`

### AC-4: 归档文件可被 docker load 识别（可选验证）
- **Given**: 导出的 tar 文件存在
- **When**: 执行 `docker load -i <file>` 验证（dry-run 或验证 tar 结构）
- **Then**: docker 能识别文件格式（manifest.json 存在）
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要 gzip 压缩以减小文件体积？（当前未要求，默认不压缩）
- [ ] 历史文件 `caffe-cpu-jupyter_20260727.tar` 是否需要覆盖或保留？
