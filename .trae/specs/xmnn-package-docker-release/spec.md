# xmnn-package v1.0.0 Docker 镜像发布 - Product Requirement Document

## Overview
- **Summary**: 从已构建的 `xmnn-runtime:latest` 镜像导出 Docker 镜像 tar 文件，使用 `bin/package.sh` 生成完整的自洽用户分发包（含镜像、文档、示例、version.json、tar.gz 归档），完成 xmnn-package v1.0.0 的首次公开发布。
- **Purpose**: xmnn-package 是六层镜像矩阵中推荐的终端用户分发方式（Docker-only模式），目前脚本和文档已齐备，但 docker/ 目录为空（仅 .gitkeep），缺少实际的 Docker 镜像 tar 文件。本次发布将填充镜像文件并生成可分发包。
- **Target Users**: 终端用户（AI 推理部署工程师）、客户侧运维人员

## Goals
- 从本地 `xmnn-runtime:latest` 导出 Docker 镜像 tar 到 `docker/xmnn-runtime-v1.0.0.tar`
- 生成 `version.json` 元数据（含版本、构建日期、镜像ID、文件大小）
- 生成 `xmnn-package-v1.0.0.tar.gz` 归档文件便于分发
- 验证导出的镜像可正常加载并通过 10 项自检
- 模拟用户快速开始流程，确认 README 文档与实际一致
- 生成 tar 文件 sha256 校验和供完整性验证

## Non-Goals (Out of Scope)
- 不修改 package.sh、docker-setup.sh 等任何脚本代码
- 不推送镜像到 Docker Registry（离线 tar 分发模式）
- 不提取 whl 到 xmnn-releases（那是并行的 whl 分发路径）
- 不创建 git tag 或提交（tar/tar.gz 在 .gitignore 中，不纳入版本控制）
- 不编写 release notes markdown 文件（package.sh 不自动生成，后续人工补充）
- 不升级或重新构建 xmnn-runtime 镜像（使用现有已验证的镜像）

## Background & Context
- 六层镜像矩阵已完整构建：Dev(L0) → whl-builder(L1) → runtime(L2) → releases(L3, whl) → client(L5, 旧版) → package(L6, 新版Docker-only)
- xmnn-runtime:latest 镜像已存在于 WSL2 Docker 中，10 项自检全部 PASS（Python 3.14.6, tvm 0.19.0, xmnn 1.2.1.dev0）
- xmnn-package 已包含完整的用户工具链：bin/docker-setup.sh（一键加载+验证+运行）、bin/package.sh（开发者打包）、3 篇文档、hello-world.py 示例
- package.sh 支持两种模式：从本地 Docker 镜像 save（默认），或从已有 tar 复制（--from-image-tar）
- Docker 操作必须在 WSL2 中执行（Windows 主机无 docker 命令），路径需使用 `/mnt/d/...` 格式

## Functional Requirements
- **FR-1**: 执行 `bash bin/package.sh --version v1.0.0 --archive` 在 WSL2 中完成打包
- **FR-2**: 打包后 `docker/` 目录包含 `xmnn-runtime-v1.0.0.tar` 文件
- **FR-3**: 包根目录生成 `version.json` 元数据文件
- **FR-4**: 包根目录生成 `xmnn-package-v1.0.0.tar.gz` 归档文件
- **FR-5**: 验证导出的 tar 可通过 `docker load` 加载并标记为 `xmnn-runtime:latest`
- **FR-6**: 加载后运行 `/opt/verify-runtime.sh` 自检 10/10 PASS
- **FR-7**: 按 README 快速开始流程模拟用户操作（docker-setup.sh → hello-world.py）
- **FR-8**: 生成 docker tar 文件的 sha256 校验和并记录

## Non-Functional Requirements
- **NFR-1**: 打包过程在 WSL2 中执行，所有路径正确映射 `/mnt/d/...`
- **NFR-2**: 打包产物在 Windows 资源管理器中可直接访问（WSL 路径互通）
- **NFR-3**: version.json 为合法 JSON，字段完整
- **NFR-4**: 打包后不遗留 dangling Docker 镜像（或明确标记为可接受）
- **NFR-5**: tar.gz 归档大小合理（预期 3-4GB，取决于镜像压缩率）

## Constraints
- **Technical**: 必须在 WSL2 中执行 bash 和 docker 命令；Windows PowerShell 无法直接运行
- **Business**: 首次公开发布，分发包版本 v1.0.0；内部 xmnn 版本为 1.2.1.dev0
- **Dependencies**: 依赖已构建的 xmnn-runtime:latest 镜像（10/10 PASS）
- **Path**: 包根目录为 `/mnt/d/spaces/SpecWeave/external/chaos/ai/xmnn-package`（WSL 路径）

## Assumptions
- xmnn-runtime:latest 镜像是正确的待发布版本（10项自检已通过作为证据）
- WSL2 中 Docker daemon 正在运行（已有 healthy 容器证明）
- 磁盘空间充足（tar 文件约 3-4GB，tar.gz 约 1.5-2GB）
- package.sh 脚本功能正常（已代码审查确认逻辑正确）
- 分发包版本 v1.0.0 是首次面向用户的公开发布版本

## Acceptance Criteria

### AC-1: 打包脚本执行成功
- **Given**: WSL2 中 Docker daemon 运行中，xmnn-runtime:latest 存在
- **When**: 执行 `cd /mnt/d/spaces/SpecWeave/external/chaos/ai/xmnn-package && bash bin/package.sh --version v1.0.0 --archive`
- **Then**: 脚本退出码为 0，输出 "Package Build Complete"
- **Verification**: `programmatic`

### AC-2: Docker 镜像 tar 文件生成
- **Given**: 打包脚本执行成功
- **When**: 检查 `docker/` 目录
- **Then**: 存在 `xmnn-runtime-v1.0.0.tar` 文件，大小 > 1GB，非空
- **Verification**: `programmatic`

### AC-3: version.json 元数据完整
- **Given**: 打包脚本执行成功
- **When**: 读取 version.json
- **Then**: 包含 version, build_date, docker_image, docker_image_id, docker_tar, docker_tar_size_bytes 字段；version 值为 "v1.0.0"；docker_tar 值为 "xmnn-runtime-v1.0.0.tar"
- **Verification**: `programmatic`

### AC-4: tar.gz 归档生成
- **Given**: 打包脚本执行成功
- **When**: 检查包根目录
- **Then**: 存在 `xmnn-package-v1.0.0.tar.gz` 文件，大小 > 500MB
- **Verification**: `programmatic`

### AC-5: 导出的镜像可加载并通过自检
- **Given**: tar 文件已生成
- **When**: 执行 `docker load -i docker/xmnn-runtime-v1.0.0.tar` 然后 `docker run --rm xmnn-runtime:latest /opt/verify-runtime.sh`
- **Then**: 镜像加载成功，10 项自检全部 PASS
- **Verification**: `programmatic`

### AC-6: sha256 校验和生成
- **Given**: tar 文件已生成
- **When**: 计算 sha256 哈希值
- **Then**: 输出 64 位十六进制哈希字符串，记录于验证结果中
- **Verification**: `programmatic`

### AC-7: 用户快速开始流程验证
- **Given**: 镜像已加载
- **When**: 按 README 执行 docker-setup.sh 流程，运行 hello-world.py
- **Then**: 流程无报错，示例输出正常（无 ModuleNotFoundError 等）
- **Verification**: `programmatic`

### AC-8: Windows 可访问性
- **Given**: 打包在 WSL2 中完成
- **When**: 检查 Windows 路径 `d:\spaces\SpecWeave\external\chaos\ai\xmnn-package\docker\`
- **Then**: tar 文件和 tar.gz 文件在 Windows 资源管理器中可见
- **Verification**: `programmatic`

### AC-9: 包结构完整性
- **Given**: 打包完成
- **When**: 检查包目录结构
- **Then**: 包含 README.md、bin/、docs/、examples/、docker/、version.json 所有必要文件
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要在打包后删除本地旧的 xmnn-runtime:latest 再重新 load 以模拟全新用户环境？（建议：是，更贴近用户真实场景）
- [ ] 是否需要将 sha256 校验和写入一个文件（如 docker/xmnn-runtime-v1.0.0.tar.sha256）？（建议：记录在验证结果中即可，不强制写入文件）
