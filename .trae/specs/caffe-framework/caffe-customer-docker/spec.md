# Caffe 客户分发 Docker 镜像 - Product Requirement Document

## Overview
- **Summary**: 在 `d:\spaces\SpecWeave\projects\xuanspace\vendor\caffe\docker\standalone\` 下创建 `pycaffe-customer/` 目录，包含一个自包含、可直接分发给客户的 Docker 镜像构建方案。该镜像基于现有 `pycaffe-jupyter-ssh/` 改造，客户通过 `docker load` 即可加载使用，无需额外安装依赖或构建基础镜像。
- **Purpose**: 解决现有开发镜像依赖本地预构建基础镜像链、面向国内环境配置、缺少客户使用文档和内置验证等问题，提供企业级可交付的客户分发包。
- **Target Users**: 需要部署 PyCaffe 推理环境的外部客户、非开发人员（运维/实施工程师）、需要开箱即用 Jupyter Notebook 环境的终端用户。

## Goals
- 创建单镜像、自包含的客户分发 Dockerfile（不依赖任何本地预构建镜像）
- 确保镜像完整性：所有运行时依赖、配置、示例文件内置，零外部依赖
- 实施镜像优化：多阶段构建减小体积，移除构建工具和临时文件
- 安全性增强：非 root 用户运行、安全补丁更新、移除敏感信息
- 可维护性：清晰注释、版本元数据、维护者信息、构建说明
- 可移植性：官方源、标准 locale、可通过环境变量配置时区
- 提供完整交付物：Dockerfile + .dockerignore + 构建脚本 + 导出脚本 + 客户使用文档 + 自检命令
- 内置 ResNet50 示例用于开箱验证
- 提供 `docker save` 导出为 tar 文件的说明

## Non-Goals (Out of Scope)
- 不修改现有 `pycaffe/` 和 `pycaffe-jupyter-ssh/` 目录的任何文件
- 不引入 GPU/CUDA 支持（保持 CPU-only）
- 不添加训练功能（Solver 等，保持 slim 推理-only 版本）
- 不提供 docker-compose 编排（客户可自行编排）
- 不包含私有的模型权重或商业机密数据
- 不创建 Helm Chart 或 Kubernetes 部署清单
- 不修改 caffe-slim/ 或 tvm-ffi/ 源码

## Background & Context
现有 Caffe standalone Docker 镜像体系：
- `pycaffe/`: 4阶段多阶段构建（base-system → base-builder → caffe-builder → runtime），从零编译 caffe-slim + tvm-ffi，但纯推理运行时无交互界面
- `pycaffe-jupyter-ssh/`: 基于 `caffe-cpu:standalone-pycaffe` 镜像扩展（FROM依赖），添加 Jupyter + SSH + supervisord，但：
  1. 依赖本地预构建的 `standalone-pycaffe` 镜像，客户需先构建/加载两个镜像
  2. 使用阿里云 apt/pip 源，对国际客户不友好
  3. 默认中文 locale 和上海时区
  4. 无内置示例模型用于验证
  5. 无自检命令
  6. 默认密码随机生成，客户首次使用可能困惑
  7. 无构建/导出脚本
  8. 无客户使用文档
  9. 构建上下文必须在 vendor/ 目录

核心约束（继承自现有项目）：
- 基础镜像固定为 `ubuntu:26.04`（非 latest）
- 零 caffex/ 依赖，仅使用 caffe-slim/ + tvm-ffi/
- Python 3（Ubuntu 26.04 系统 Python），numpy >= 2
- scikit-build-core + CMake + Ninja 构建系统
- PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
- 多阶段构建（base-system → base-builder → caffe-builder → customer-runtime）
- 构建上下文必须是 vendor/ 目录

## Functional Requirements
- **FR-1**: 新目录 `pycaffe-customer/` 包含完整的客户分发镜像构建方案
- **FR-2**: Dockerfile 为自包含单镜像，FROM ubuntu:26.04 开始完整构建，不依赖任何本地预构建镜像
- **FR-3**: 多阶段构建（5阶段：base-system → base-builder → caffe-builder → customer-runtime-setup → customer-runtime），runtime 阶段不包含构建工具链
- **FR-4**: 包含 Jupyter Notebook/Lab 和 SSH 服务，通过 supervisord 管理（沿用 pycaffe-jupyter-ssh 架构）
- **FR-5**: 使用官方 Ubuntu apt 源和官方 PyPI 源（无地域偏见），客户可通过 build-arg 替换镜像源
- **FR-6**: 默认 locale 为 C.UTF-8（国际通用），默认时区为 UTC，支持通过 TZ 环境变量配置
- **FR-7**: 内置 ResNet50 示例（prototxt + caffemodel + 推理脚本 + Notebook），客户开箱即可验证
- **FR-8**: 提供 `caffe-verify` 命令（/usr/local/bin/caffe-verify）用于客户自检镜像功能完整性
- **FR-9**: 非 root 用户（builder, UID 1000）运行 Jupyter/SSH 服务；通过 gosu 进行权限降级
- **FR-10**: 设置文档化的默认凭证（SSH 密码: `caffepass`，Jupyter token: `caffe-token`），文档中强调必须修改
- **FR-11**: 提供 .dockerignore 文件排除无关文件
- **FR-12**: 提供 build.sh 一键构建脚本
- **FR-13**: 提供 export.sh 脚本导出为 tar 文件供客户分发
- **FR-14**: 提供 README.md 客户使用文档（含 load/run/verify/访问凭证/常见问题）
- **FR-15**: Dockerfile 包含完整 LABEL 元数据（maintainer/version/description/source/vendor）
- **FR-16**: 容器启动时打印清晰的欢迎 banner，包含访问 URL、凭证信息、自检命令提示
- **FR-17**: HEALTHCHECK 同时检测 SSH(22) 和 Jupyter(8888) 服务状态
- **FR-18**: ENTRYPOINT 使用 tini 作为 PID 1，CMD 启动 supervisord

## Non-Functional Requirements
- **NFR-1（体积优化）**: 最终 runtime 镜像体积应控制在合理范围（目标 < 2.5GB），移除所有构建工具（gcc/g++/cmake/ninja/build-essential/git 等）
- **NFR-2（安全性）**: 
  - 构建时执行 `apt-get upgrade` 安装安全更新
  - 清理 /var/lib/apt/lists/*、/tmp/*、/var/tmp/*、pip cache
  - 不包含任何 SSH 私钥/密钥材料（构建时的 host key 在 entrypoint 重新生成）
  - 不包含 .git 目录或源代码仓库元数据
  - 非 root 用户运行，禁止 root SSH 登录（默认 ALLOW_ROOT_SSH=no）
  - 固定所有 pip 包版本（==），确保可复现构建
- **NFR-3（可复现性）**: 所有基础镜像、apt 包、pip 包均固定版本；Dockerfile 中明确标注所有软件版本号
- **NFR-4（可维护性）**: Dockerfile 每个阶段和关键步骤都有中文/英文注释；构建信息写入 /etc/caffe-customer-release
- **NFR-5（性能）**: 容器启动时间 < 10 秒；Jupyter 页面加载时间 < 5 秒；推理验证脚本执行时间 < 30 秒
- **NFR-6（可移植性）**: 在标准 Docker 20.10+ 环境中可运行；不依赖特定主机挂载或内核模块；支持 linux/amd64 架构

## Constraints
- **Technical**: 
  - 必须使用 ubuntu:26.04 基础镜像
  - 必须继承现有 caffe-slim + tvm-ffi 构建逻辑（参考 pycaffe/Dockerfile 阶段 0-2）
  - 构建上下文必须是 vendor/ 目录（需要访问 caffe/caffe-slim/ 和 tvm-ffi/）
  - Python 包使用 pip --break-system-packages（PEP 668 合规）
  - 零 caffex/ 依赖（铁律）
- **Business**: 
  - 镜像需可直接交付客户，无额外许可问题（所有组件开源/BSD/Apache/MIT 许可）
  - 交付物包含完整文档，非技术客户可按文档操作
- **Dependencies**: 
  - caffe/caffe-slim/ 源码（git submodule）
  - tvm-ffi/ 源码（git submodule）
  - Docker 20.10+ (BuildKit 支持)
  - ResNet50 示例模型文件（现有 examples/resnet50/ 目录）

## Assumptions
- 客户已安装 Docker 20.10+ 环境
- 客户收到 tar 文件后可执行 `docker load -i`
- 客户至少暴露 8888 端口用于 Jupyter 访问（SSH 22端口为可选）
- ResNet50 caffemodel 文件大小可接受（~100MB），包含在镜像内用于演示
- 现有 examples/resnet50/ 目录中的模型文件完整可用

## Acceptance Criteria

### AC-1: 目录结构完整
- **Given**: 构建工作完成
- **When**: 检查 `pycaffe-customer/` 目录
- **Then**: 目录包含 Dockerfile、.dockerignore、build.sh、export.sh、README.md、config/、scripts/ 等必要文件
- **Verification**: `programmatic`
- **Notes**: 参考现有 pycaffe-jupyter-ssh/ 目录结构，新增 export.sh 和更完善的文档

### AC-2: Dockerfile 自包含构建成功
- **Given**: 子模块已初始化（caffe-slim/ 和 tvm-ffi/ 存在）
- **When**: 在 vendor/ 目录下执行 `docker build -t caffe-cpu:customer -f caffe/docker/standalone/pycaffe-customer/Dockerfile .`
- **Then**: 构建成功无错误，生成 caffe-cpu:customer 镜像
- **Verification**: `programmatic`
- **Notes**: 不需要预先构建任何基础镜像

### AC-3: 镜像体积优化
- **Given**: 构建完成
- **When**: 执行 `docker images caffe-cpu:customer`
- **Then**: 镜像体积小于 3GB（目标 < 2.5GB），不包含 gcc/cmake/ninja/git 等构建工具
- **Verification**: `programmatic`
- **Notes**: 通过多阶段构建和清理确保 runtime 镜像不含构建工具链

### AC-4: 容器启动正常
- **Given**: 镜像已构建
- **When**: 执行 `docker run -d -p 8888:8888 -p 2222:22 --name caffe-test caffe-cpu:customer`
- **Then**: 容器在 10 秒内进入 healthy 状态，无异常退出
- **Verification**: `programmatic`

### AC-5: Jupyter 可访问
- **Given**: 容器已启动
- **When**: 访问 http://localhost:8888/ 并使用默认 token `caffe-token` 登录
- **Then**: Jupyter Notebook 页面正常加载，可创建/运行 notebook
- **Verification**: `programmatic`
- **Notes**: HTTP 返回 200/302，使用 token 认证成功

### AC-6: SSH 可连接
- **Given**: 容器已启动
- **When**: 使用 `ssh builder@localhost -p 2222` 并输入默认密码 `caffepass`
- **Then**: SSH 登录成功，可进入交互 shell
- **Verification**: `programmatic`

### AC-7: PyCaffe 功能正常
- **Given**: 容器已启动
- **When**: 在容器内执行 `python -c "import pycaffe; print(pycaffe.__version__)"`
- **Then**: 成功导入 pycaffe，版本号为 `1.0.0-slim`
- **Verification**: `programmatic`

### AC-8: 内置 ResNet50 示例可运行
- **Given**: 容器已启动
- **When**: 执行 `caffe-verify` 或在 Jupyter 中打开 resnet50 示例 notebook
- **Then**: 推理成功完成，输出分类结果，无错误
- **Verification**: `programmatic`

### AC-9: 自检命令可用
- **Given**: 容器已启动
- **When**: 执行 `caffe-verify`
- **Then**: 自检脚本运行并报告所有检查项 PASS（import/version/Net/forward/Jupyter/SSH/demo）
- **Verification**: `programmatic`

### AC-10: 非 root 用户运行
- **Given**: 容器正在运行
- **When**: 执行 `docker exec caffe-test ps aux`
- **Then**: Jupyter 和 SSH 进程以 builder 用户（UID 1000）运行，非 root
- **Verification**: `programmatic`

### AC-11: docker save 导出正常
- **Given**: 镜像已构建
- **When**: 执行 `./export.sh` 或 `docker save -o caffe-cpu-customer.tar caffe-cpu:customer`
- **Then**: 生成 tar 文件；在干净环境中 `docker load -i caffe-cpu-customer.tar` 可成功加载镜像
- **Verification**: `programmatic`

### AC-12: 客户文档完整可用
- **Given**: 交付物已生成
- **When**: 阅读 README.md
- **Then**: 文档包含 docker load 命令、docker run 命令、访问 URL/凭证、自检方法、环境变量配置、常见问题排查等章节；新人按文档可独立完成镜像加载和运行
- **Verification**: `human-judgment`
- **Notes**: 非技术人员视角检查文档清晰度

### AC-13: Dockerfile 注释和元数据完整
- **Given**: Dockerfile 已完成
- **When**: 审阅 Dockerfile
- **Then**: 每个阶段有清晰注释说明用途；包含 LABEL maintainer/version/description；标注关键软件版本；包含构建说明注释
- **Verification**: `human-judgment`

### AC-14: 安全加固验证
- **Given**: 镜像已构建
- **When**: 扫描镜像内容
- **Then**: 不包含 .git 目录；不包含 gcc/cmake 等构建工具；不包含 /var/lib/apt/lists/ 缓存；不存在硬编码的私钥/密钥；sshd 配置禁止 root 登录
- **Verification**: `programmatic`

### AC-15: 启动 banner 信息清晰
- **Given**: 容器启动
- **When**: 查看 `docker logs caffe-test`
- **Then**: 日志包含欢迎 banner，明确显示 Jupyter URL、token、SSH 用户名/密码、自检命令提示
- **Verification**: `human-judgment`

## Open Questions
- [x] ~~ResNet50 caffemodel 文件是否在 examples/resnet50/ 中已存在且完整？~~ → 已确认：ResNet-50-model.caffemodel 存在（~97MB），文件完整可用
- [ ] 是否需要支持 build-arg 切换 apt/pip 镜像源（阿里云/官方/其他）？→ 建议支持 APTPROXY 和 PIP_INDEX_URL build-arg
- [ ] 默认凭证策略：使用固定默认密码（文档提示必须修改）还是首次启动随机生成（打印到日志）？→ 建议固定默认密码（caffepass/caffe-token）+ 文档醒目警示修改，同时支持环境变量覆盖
- [ ] 是否需要禁用 SSH 服务（仅保留 Jupyter）以减小攻击面？→ 默认保留 SSH 便于调试，客户可通过环境变量 DISABLE_SSH=yes 禁用
- [ ] 是否需要添加中文文档版本？→ README.md 提供英文主文档（面向国际客户），脚本/Dockerfile 注释使用中英双语
