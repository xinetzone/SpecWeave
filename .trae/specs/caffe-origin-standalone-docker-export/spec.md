---
version: 1.0
date: 2026-07-27
source: "用户请求: docker/origin 独立 Docker 镜像构建与导出"
---

# Caffe Origin 独立 Docker 镜像构建与分发 - Product Requirement Document

## Overview
- **Summary**: 为 `projects/xuanspace/vendor/caffe/docker/origin` 目录的 Caffe CPU-only 环境构建一个完全自包含、可独立分发的 Docker 镜像，包含基础运行时镜像和 Jupyter+SSH 镜像两个变体。镜像需确保在不同环境（Linux/Windows/macOS + Docker）中无需额外配置即可直接加载运行，提供标准化的导出流程和面向最终用户的使用说明文档。
- **Purpose**: 解决现有开发模式依赖宿主机目录挂载导致镜像无法独立分发的问题，使 Caffe 环境可作为开箱即用的工具交付给用户，无需用户从源码编译或配置依赖。
- **Target Users**: 需要使用 Caffe 深度学习框架的研究人员、学生、开发者；希望快速获得可运行 Caffe 环境的用户；在隔离环境中需要 Caffe 的 CI/CD 系统。

## Goals
- 基于现有 `docker/origin/Dockerfile` 和 `Dockerfile.jupyter-ssh` 构建两个可独立运行的镜像（基础运行时、Jupyter+SSH 交互式环境）
- 确保镜像完全自包含：所有编译产物、Python 依赖、系统库内置在镜像中，不依赖宿主机挂载
- 提供标准化镜像导出流程，生成可分发的 tar 归档文件
- 提供镜像加载验证脚本，用户加载镜像后可一键验证功能完整性
- 编写面向最终用户的使用说明文档（非开发者文档），包含加载、运行、验证、常见问题
- 提供镜像构建和导出的一键化脚本

## Non-Goals (Out of Scope)
- 不修改 Caffe 源码（caffex/ 目录保持只读）
- 不构建 GPU 版本镜像（仅 CPU-only）
- 不推送到公共 Docker Registry（仅本地导出 tar 文件）
- 不修改现有 Dockerfile 的核心构建逻辑（仅优化运行时自包含性）
- 不重构为 scikit-build-core/pycaffe wheel 模式（保持原始 Make 构建方式）
- 不包含 PyTorch/TensorFlow 等额外深度学习框架

## Background & Context
- 现有 `docker/origin/` 已具备 4 阶段多阶段构建的 Dockerfile，基础镜像大小约 3.36GB
- 现有 `run.sh` 脚本会将宿主机目录挂载到容器 `/workspace`，这会覆盖镜像内已编译的 Caffe 产物，导致镜像无法独立使用
- 镜像内已正确配置 `CAFFE_ROOT`、`PYTHONPATH`、`LD_LIBRARY_PATH` 环境变量，但现有文档面向开发者而非最终用户
- 缺少镜像导出（docker save）和加载后验证的标准化流程
- 已有一个早期的简单导出 spec，但仅涉及单个已有镜像的导出，不涵盖构建、自包含性优化、文档等完整流程

## Functional Requirements
- **FR-1**: 构建 `caffe-cpu:origin-runtime` 基础运行时镜像，完全自包含，不依赖外部挂载即可 `import caffe`
- **FR-2**: 构建 `caffe-cpu:origin-jupyter` Jupyter+SSH 镜像，内置 SSH 服务、Jupyter Notebook/Lab，自包含不依赖挂载
- **FR-3**: 提供 `export.sh` 镜像导出脚本，将两个镜像导出为 tar 文件，文件命名包含版本和日期
- **FR-4**: 提供 `verify-image.sh` 镜像验证脚本，容器启动后可一键验证 Caffe 功能完整性
- **FR-5**: 提供不挂载宿主机目录的 `run-standalone.sh` 运行脚本，供最终用户使用
- **FR-6**: 编写 USER_GUIDE.md 用户使用指南，包含镜像加载、运行、验证、Jupyter 访问、常见问题
- **FR-7**: 导出的 tar 文件可通过标准 `docker load -i` 命令在任意 Docker 环境中加载
- **FR-8**: 镜像内置健康检查或入口验证，启动时可确认 Caffe 可正常导入

## Non-Functional Requirements
- **NFR-1**: 镜像自包含性：不挂载任何宿主机目录时，`docker run --rm caffe-cpu:origin-runtime python3 -c "import caffe; print(caffe.__version__)"` 必须成功
- **NFR-2**: 跨环境兼容性：导出的镜像在标准 Docker 环境（Linux、Windows WSL2、macOS）中均可正常加载运行
- **NFR-3**: 镜像导出完整性：导出的 tar 文件包含完整镜像层，加载后镜像 ID/标签与构建时一致
- **NFR-4**: 用户体验：从 `docker load` 到成功运行 Caffe 示例命令，用户操作步骤不超过 3 步
- **NFR-5**: 文档清晰性：USER_GUIDE.md 面向非开发者，避免内部开发术语，提供可直接复制粘贴的命令示例
- **NFR-6**: 构建可复现性：提供构建脚本和锁版本机制，相同源码可重复构建出功能一致的镜像

## Constraints
- **Technical**:
  - 保持 Ubuntu 22.04 基础镜像、Python 3.10、Make 构建系统不变
  - 不修改 caffex/ 源码目录（只读第三方依赖）
  - Docker 必须是标准 Docker Engine/Desktop，兼容 OCI 镜像格式
  - 镜像内固定 protobuf==3.20.3（Caffe 1.0 兼容性要求）
- **Business**:
  - 镜像需可离线分发，不依赖网络下载额外依赖
  - 用户无需具备编译 C++ 代码的能力即可使用
- **Dependencies**:
  - Docker 20.10+ 或兼容版本
  - 构建时需要网络访问（apt/pip 源已配置国内镜像）
  - 磁盘空间：构建需 ≥10GB，导出 tar 文件约 3-4GB

## Assumptions
- 用户已安装 Docker（Docker Desktop for Windows/macOS，Docker Engine for Linux）
- 用户在加载镜像时可以访问本地文件系统（用于加载 tar 文件）
- 国内用户访问阿里云镜像源正常，国外用户可修改构建参数或使用默认源
- Jupyter 镜像默认配置的 Token/密码仅用于示例，用户可通过环境变量自定义
- 镜像主要用于 CPU-only 推理和学习，不涉及大规模 GPU 训练

## Acceptance Criteria

### AC-1: 基础运行时镜像构建成功且自包含
- **Given**: 源码完整，Docker 服务运行中
- **When**: 在 caffe/ 根目录执行构建命令，使用 runtime 目标阶段
- **Then**: 镜像 `caffe-cpu:origin-runtime` 构建成功，无挂载运行验证命令退出码为 0
- **Verification**: `programmatic`
- **Notes**: 验证命令 `docker run --rm caffe-cpu:origin-runtime python3 -c "import caffe; import numpy; print('Caffe OK')"` 必须成功

### AC-2: Jupyter+SSH 镜像构建成功且自包含
- **Given**: 基础运行时镜像已构建或可从缓存获取
- **When**: 构建 runtime-jupyter 目标阶段
- **Then**: 镜像 `caffe-cpu:origin-jupyter` 构建成功，不挂载目录启动后 Jupyter 和 SSH 服务正常
- **Verification**: `programmatic`
- **Notes**: 容器启动后端口映射正常，`docker ps` 显示健康，curl 访问 Jupyter 端口返回 200/302

### AC-3: 镜像导出脚本正常工作
- **Given**: 两个镜像均已成功构建
- **When**: 执行 export.sh 脚本
- **Then**: 在指定输出目录生成两个 tar 文件（基础镜像和 Jupyter 镜像），文件非空且大小合理
- **Verification**: `programmatic`
- **Notes**: 文件命名格式 `caffe-cpu-origin-{variant}_{YYYYMMDD}.tar`，输出目录默认为 docker/origin/dist/

### AC-4: 导出的镜像可在干净环境中加载并运行
- **Given**: 导出的 tar 文件存在，目标机器有 Docker 环境且未加载过该镜像
- **When**: 执行 `docker load -i <tar-file>` 然后运行验证命令
- **Then**: 镜像加载成功，标签正确，验证 Caffe 导入命令成功
- **Verification**: `programmatic`
- **Notes**: 可通过 `docker rmi` 先删除本地镜像模拟干净环境

### AC-5: 提供独立运行脚本（不挂载宿主机）
- **Given**: 镜像已加载
- **When**: 执行 run-standalone.sh 脚本
- **Then**: 启动容器，Caffe 可正常使用，不依赖任何宿主机目录挂载
- **Verification**: `programmatic` + `human-judgment`
- **Notes**: 脚本同时支持交互式 bash 和一次性命令模式

### AC-6: 用户使用文档完整清晰
- **Given**: 所有脚本和镜像已准备完毕
- **When**: 用户阅读 USER_GUIDE.md 并按步骤操作
- **Then**: 新用户可在无 prior knowledge 的情况下成功加载镜像、运行 Caffe、访问 Jupyter
- **Verification**: `human-judgment`
- **Rubric**:
  - [ ] 文档有快速开始章节，3 步以内可运行第一个 Caffe 命令
  - [ ] 所有命令可直接复制粘贴执行
  - [ ] 包含常见问题排障章节（至少覆盖 5 个常见问题）
  - [ ] 包含 Jupyter 访问和 SSH 登录的明确说明
  - [ ] 避免内部开发术语（如"多阶段构建"、"挂载点"等术语需解释或不使用）

### AC-7: 镜像验证脚本功能正常
- **Given**: 容器已启动或镜像可运行
- **When**: 在容器内执行 verify-caffe.sh 或通过 docker run 调用
- **Then**: 自动执行一系列验证检查（Python 导入、核心库加载、简单前向计算），输出 PASS/FAIL 汇总
- **Verification**: `programmatic`

## Open Questions
- [ ] 导出的镜像文件是否需要 gzip 压缩？（建议提供压缩选项，默认不压缩以加快加载速度）
- [ ] 镜像标签是否需要包含版本号（如 caffe-cpu:origin-runtime-v1.0）？
- [ ] 是否需要在镜像中预置 MNIST/CIFAR10 等示例数据和模型？（当前 examples/ 目录在源码中，不内置到镜像）
- [ ] 导出目录默认位置是 docker/origin/dist/ 还是用户主目录或其他位置？
