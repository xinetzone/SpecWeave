# Caffe 客户分发 Docker 镜像 - The Implementation Plan (Decomposed and Prioritized Task List)

## [ ] Task 1: 创建目录结构和基础配置文件
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 在 `d:\spaces\SpecWeave\projects\xuanspace\vendor\caffe\docker\standalone\` 下创建 `pycaffe-customer/` 目录
  - 创建子目录：`config/`, `config/supervisor/conf.d/`, `scripts/`, `examples/resnet50/`
  - 创建 `.dockerignore` 文件，排除无关文件（.git、__pycache__、*.pyc、caffex/ 等）
  - 从 pycaffe-jupyter-ssh/config/ 复制配置文件（supervisord.conf、sshd_config、jupyter_notebook_config.py、supervisor/conf.d/jupyter.conf、sshd.conf）并做必要调整
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录结构存在且包含所有必要子目录
  - `programmatic` TR-1.2: .dockerignore 文件存在且包含必要排除规则
  - `human-judgement` TR-1.3: 配置文件语法正确，与 pycaffe-jupyter-ssh 保持兼容但适配客户分发场景
- **Notes**: 配置文件需调整：Jupyter 默认 token 为 `caffe-token`，sshd 配置禁止 root 登录

## [ ] Task 2: 编写自包含多阶段 Dockerfile
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 基于 pycaffe/Dockerfile 的前3阶段（base-system → base-builder → caffe-builder）构建编译环境
  - 新增 customer-runtime-setup 阶段：从 caffe-builder 复制构建产物，安装 SSH/Jupyter/supervisor/tini/gosu 等运行时包
  - 新增 customer-runtime 最终阶段：仅包含运行时依赖，不包含构建工具链
  - 使用官方 Ubuntu apt 源（默认），支持通过 build-arg APTPROXY 替换
  - 默认 locale 为 C.UTF-8，时区为 UTC（可通过 TZ 环境变量覆盖）
  - 内置 ResNet50 示例文件（COPY 到 /opt/caffe-examples/resnet50/）
  - 安装 caffe-verify 自检脚本到 /usr/local/bin/
  - 添加完整 LABEL 元数据（maintainer、version、description、source、vendor）
  - 每个阶段添加清晰注释，标注关键软件版本
  - 写入 /etc/caffe-customer-release 构建信息文件
  - 固定所有 pip 包版本（==）
  - 构建时执行 apt-get upgrade 安装安全更新
  - 清理所有缓存和临时文件（apt lists、pip cache、/tmp/*）
  - 配置 HEALTHCHECK 检测 SSH 和 Jupyter
  - ENTRYPOINT 使用 tini，CMD 启动 supervisord
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-13, AC-14
- **Test Requirements**:
  - `programmatic` TR-2.1: Dockerfile 语法正确，可被 docker build 解析
  - `programmatic` TR-2.2: docker build 成功完成，无错误
  - `programmatic` TR-2.3: 镜像中不包含 gcc/g++/cmake/ninja/git/build-essential 等构建工具
  - `programmatic` TR-2.4: 镜像中不存在 /var/lib/apt/lists/ 目录内容（apt缓存已清理）
  - `programmatic` TR-2.5: docker inspect 显示 LABEL 元数据完整
  - `human-judgement` TR-2.6: Dockerfile 注释清晰，每个阶段有说明，软件版本标注明确
- **Notes**: 关键区别：不使用 FROM caffe-cpu:standalone-pycaffe，而是将编译和运行时整合为一个自包含镜像的多阶段构建。参考 pycaffe/Dockerfile 阶段 0-2 的构建逻辑，将其融入客户镜像的 Dockerfile 中。

## [ ] Task 3: 编写 entrypoint.sh 启动脚本
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 基于 pycaffe-jupyter-ssh/entrypoint.sh 改造
  - 设置默认凭证：SSH 密码 `caffepass`（可通过 USER_PASSWORD 覆盖），Jupyter token `caffe-token`（可通过 JUPYTER_TOKEN 覆盖）
  - 默认禁止 root SSH 登录（ALLOW_ROOT_SSH=no）
  - 打印清晰的欢迎 banner，包含：镜像版本、Jupyter URL 和 token、SSH 连接信息、自检命令提示（caffe-verify）、安全提示（修改默认密码）
  - entrypoint 启动时重新生成 SSH host keys（不使用构建时生成的）
  - 支持命令模式（docker run ... bash 直接执行命令，不启动服务）
  - 使用 gosu 降级到 builder 用户运行服务
  - tini 作为 PID 1
- **Acceptance Criteria Addressed**: AC-4, AC-10, AC-15
- **Test Requirements**:
  - `programmatic` TR-3.1: entrypoint.sh 语法正确（bash -n 检查通过）
  - `programmatic` TR-3.2: 容器启动后 10 秒内 Jupyter 和 SSH 服务正常运行
  - `programmatic` TR-3.3: Jupyter/SSH 进程以 builder 用户（UID 1000）运行
  - `programmatic` TR-3.4: docker exec 可正常执行命令
  - `human-judgement` TR-3.5: docker logs 输出的 banner 信息清晰完整，包含所有必要信息
- **Notes**: 确保在容器启动时（而非构建时）生成 SSH host keys，避免所有镜像使用相同的 host key。

## [ ] Task 4: 编写 caffe-verify 自检脚本
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 创建 /usr/local/bin/caffe-verify 脚本（bash）
  - 检查项：
    1. pycaffe import 成功
    2. pycaffe.__version__ 正确 (1.0.0-slim)
    3. pycaffe.Net 类可用
    4. LeNet 网络创建和 forward 成功（不抛异常）
    5. Jupyter HTTP 端口 8888 可连接（curl 检查，返回 200/302/401/403 均算正常）
    6. SSH 端口 22 可连接（nc 或 ss 检查）
    7. ResNet50 demo 推理成功（使用内置示例文件）
  - 输出清晰的 PASS/FAIL/SKIP 报告
  - 任何核心项 FAIL 返回非零退出码
  - 辅助项（如完整分类结果展示）标记为 INFO
- **Acceptance Criteria Addressed**: AC-8, AC-9
- **Test Requirements**:
  - `programmatic` TR-4.1: caffe-verify 脚本可执行
  - `programmatic` TR-4.2: 在运行的容器中执行 caffe-verify 返回 0 退出码
  - `programmatic` TR-4.3: 所有核心检查项报告 PASS
  - `human-judgement` TR-4.4: 输出格式清晰易读，客户可理解
- **Notes**: 参考 pycaffe/scripts/verify-pycaffe.sh 的检查逻辑，扩展加入服务检查和 demo 推理检查。

## [ ] Task 5: 编写 healthcheck.sh 健康检查脚本
- **Priority**: medium
- **Depends On**: Task 2
- **Description**: 
  - 创建 /usr/local/bin/healthcheck.sh
  - 同时检测：
    1. SSH 端口 22 是否在监听
    2. Jupyter HTTP 端口 8888 是否响应（curl -f 或检查返回码）
  - 两个服务都正常返回 0，否则返回 1
  - 超时设置合理（5秒）
- **Acceptance Criteria Addressed**: AC-4, AC-17
- **Test Requirements**:
  - `programmatic` TR-5.1: healthcheck.sh 语法正确
  - `programmatic` TR-5.2: 容器运行正常时 healthcheck 返回 0
  - `programmatic` TR-5.3: 服务异常时 healthcheck 返回非零
- **Notes**: 基于 pycaffe-jupyter-ssh/scripts/healthcheck.sh 改造。

## [ ] Task 6: 编写 build.sh 一键构建脚本
- **Priority**: medium
- **Depends On**: Task 2
- **Description**: 
  - 创建 build.sh（bash 脚本，可在 Linux/WSL/Git Bash 中执行）
  - 自动检查构建上下文是否在 vendor/ 目录
  - 自动检查子模块是否初始化（caffe-slim/ 和 tvm-ffi/）
  - 支持参数：镜像标签（默认 caffe-cpu:customer）、是否使用 BuildKit、apt 代理
  - 执行 docker build 命令，输出构建日志
  - 构建成功后打印镜像大小和快速验证命令
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-6.1: build.sh 可执行
  - `programmatic` TR-6.2: 脚本可正确检查前置条件（子模块、目录位置）
  - `human-judgement` TR-6.3: 脚本输出信息清晰，错误提示明确
- **Notes**: 脚本需有 set -euo pipefail 严格模式。

## [ ] Task 7: 编写 export.sh 导出脚本
- **Priority**: medium
- **Depends On**: Task 6
- **Description**: 
  - 创建 export.sh 脚本
  - 支持参数：镜像名（默认 caffe-cpu:customer）、输出文件名（默认 caffe-cpu-customer-<version>-<date>.tar）
  - 执行 docker save 将镜像导出为 tar 文件
  - 可选：计算 SHA256 校验和，输出校验和文件
  - 导出完成后打印文件大小和 docker load 命令示例
- **Acceptance Criteria Addressed**: AC-11
- **Test Requirements**:
  - `programmatic` TR-7.1: export.sh 可执行
  - `programmatic` TR-7.2: 执行后生成 tar 文件
  - `programmatic` TR-7.3: tar 文件可通过 docker load -i 成功加载
  - `human-judgement` TR-7.4: 输出信息包含客户需要的 load 命令
- **Notes**: 导出的 tar 文件应包含完整镜像（所有层），客户 docker load 后无需额外依赖。

## [ ] Task 8: 准备内置 ResNet50 示例
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 从 pycaffe-jupyter-ssh/examples/resnet50/ 复制示例文件到 pycaffe-customer/examples/resnet50/
  - 确保以下文件存在：ResNet-50-deploy.prototxt、ResNet-50-model.caffemodel、demo.png、config.toml、dataset.txt
  - 复制 infer.py 推理脚本，适配内置路径（/opt/caffe-examples/resnet50/）
  - 如有 notebook 文件，一并不入
  - 在 Dockerfile 中将这些文件 COPY 到 /opt/caffe-examples/resnet50/，并创建符号链接到 /workspace/examples/
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-8.1: 所有示例文件在构建后存在于镜像中
  - `programmatic` TR-8.2: infer.py 可成功执行推理
  - `programmatic` TR-8.3: notebook（如有）可在 Jupyter 中打开运行
- **Notes**: 先检查 ResNet-50-model.caffemodel 是否真实存在（不是 LFS 指针）。如模型文件不存在，需要标记 Open Question 并调整方案（可能需要下载或提供下载脚本）。

## [ ] Task 9: 编写客户使用文档 README.md
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4
- **Description**: 
  - 创建 README.md（英文主文档，关键术语可附中文）
  - 章节结构：
    1. **Quick Start**（3步快速开始：docker load → docker run → 访问URL）
    2. **What's Inside**（镜像包含内容：Caffe版本、Python包、Jupyter/Lab、SSH）
    3. **Loading the Image**（docker load -i 详细说明，含校验和验证）
    4. **Running the Container**（docker run 命令，端口映射、volume挂载、环境变量）
    5. **Default Credentials**（默认用户名/密码/token，强烈建议修改的安全警告）
    6. **Verifying the Installation**（caffe-verify 命令使用）
    7. **Running the Demo**（ResNet50 示例运行方法）
    8. **Environment Variables**（所有可用环境变量列表：TZ、USER_PASSWORD、JUPYTER_TOKEN、GRANT_SUDO、ALLOW_ROOT_SSH 等）
    9. **Security Considerations**（安全最佳实践：修改默认密码、不要暴露SSH到公网、定期更新等）
    10. **Troubleshooting**（常见问题：端口冲突、内存不足、无法连接Jupyter等）
    11. **Building from Source**（从源码构建的说明，面向需要定制的高级用户）
    12. **Version & Maintainer Information**（版本号、维护者联系方式、许可证）
- **Acceptance Criteria Addressed**: AC-12
- **Test Requirements**:
  - `human-judgement` TR-9.1: 文档结构清晰，非技术人员按 Quick Start 章节可成功启动镜像
  - `human-judgement` TR-9.2: 所有命令示例可复制粘贴执行
  - `human-judgement` TR-9.3: 安全警告醒目，默认凭证标注明确
  - `human-judgement` TR-9.4: 常见问题覆盖实际可能遇到的问题
- **Notes**: README.md 是客户接触到的第一份文档，必须清晰、简洁、可操作。

## [ ] Task 10: 集成测试与验证
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5, Task 8
- **Description**: 
  - 构建镜像：执行 build.sh
  - 启动容器：映射 8888 和 2222 端口
  - 验证 AC-4 到 AC-11 的所有 programmatic 检查项：
    - 容器启动和健康状态
    - Jupyter HTTP 访问和 token 认证
    - SSH 连接和密码认证
    - pycaffe import 和版本
    - caffe-verify 自检命令
    - ResNet50 demo 推理
    - 非 root 用户运行检查
    - 构建工具不存在检查
    - 安全检查（无 .git、无构建密钥、sshd 禁止 root）
  - docker save/load 往返测试：导出为 tar，在干净环境 load 后验证可用
  - 修复测试中发现的问题
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-10, AC-11, AC-14
- **Test Requirements**:
  - `programmatic` TR-10.1: 所有 programmatic 验收标准通过
  - `programmatic` TR-10.2: docker save/load 往返测试成功
  - `human-judgement` TR-10.3: 容器启动日志的 banner 信息完整清晰
- **Notes**: 这是最终验证任务，需确保所有功能正常工作。如果 Docker 环境不可用，至少进行静态分析和语法检查。
