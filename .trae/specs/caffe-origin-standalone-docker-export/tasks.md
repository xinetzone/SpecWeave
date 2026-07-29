---
version: 1.0
date: 2026-07-27
---

# Caffe Origin 独立 Docker 镜像构建与分发 - The Implementation Plan

## [x] Task 1: 更新构建脚本和镜像标签
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 修改 `build.sh` 脚本，支持构建两个明确命名的镜像标签：`caffe-cpu:origin-runtime`（基础运行时）和 `caffe-cpu:origin-jupyter`（Jupyter+SSH 环境）
  - 保持现有构建逻辑不变，仅调整默认标签和添加一键构建两个镜像的选项
  - 添加 `--all` 参数可一次性构建两个镜像
  - 确保构建上下文正确，不依赖开发者本地路径假设
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-1.1: 运行 `./build.sh` 默认构建 origin-runtime 镜像
  - `programmatic` TR-1.2: 运行 `./build.sh --jupyter` 构建 origin-jupyter 镜像
  - `programmatic` TR-1.3: 运行 `./build.sh --all` 按顺序构建两个镜像
  - `human-judgement` TR-1.4: 脚本帮助信息清晰，参数说明明确
- **Notes**: 修改现有 build.sh 而非创建新脚本，保持向后兼容

## [x] Task 2: 增强镜像内验证脚本 (verify-caffe.sh)
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 增强现有的 `scripts/verify-caffe.sh` 脚本，使其作为容器内可用的独立验证工具
  - 验证项包括：Python 版本检查、核心 Python 包导入（numpy, scipy, google.protobuf）、caffe 模块导入、libcaffe.so 动态库加载、简单 Blob 创建和前向计算测试
  - 输出带颜色的 PASS/FAIL 结果和汇总统计
  - 支持非交互式运行（退出码表示成功/失败）
  - 将脚本路径加入容器内 PATH 环境变量
- **Acceptance Criteria Addressed**: AC-1, AC-7
- **Test Requirements**:
  - `programmatic` TR-2.1: 在已构建的 runtime 镜像内运行 verify-caffe.sh 全部检查通过
  - `programmatic` TR-2.2: `docker run --rm caffe-cpu:origin-runtime verify-caffe.sh` 退出码为 0
  - `programmatic` TR-2.3: 脚本输出包含各检查项的明确 PASS/FAIL 状态
  - `programmatic` TR-2.4: 至少包含 5 项核心验证检查（Python导入、protobuf、caffe导入、动态库、简单计算）

## [x] Task 3: 创建独立运行脚本 (run-standalone.sh)
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `run-standalone.sh` 脚本，用于最终用户运行独立镜像
  - 关键特性：**不挂载宿主机目录**，确保镜像自包含运行
  - 支持两个子命令：`runtime`（基础镜像）和 `jupyter`（Jupyter镜像）
  - runtime 模式支持：交互式 bash、一次性命令执行、工作目录设置
  - jupyter 模式：自动端口映射（8888/22）、环境变量传递（密码、Token）、显示访问信息
  - 自动检测 Docker 是否可用，提供友好的错误提示
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5
- **Test Requirements**:
  - `programmatic` TR-3.1: `./run-standalone.sh runtime -- python3 -c "import caffe"` 成功执行
  - `programmatic` TR-3.2: `./run-standalone.sh jupyter` 启动后端口 8888 和 2222 可访问
  - `human-judgement` TR-3.3: 脚本启动后清晰显示访问 URL、Token、SSH 连接命令
  - `programmatic` TR-3.4: 运行时不包含 `-v` 挂载参数（通过 docker inspect 验证）

## [x] Task 4: 创建镜像导出脚本 (export.sh)
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `export.sh` 镜像导出脚本
  - 功能：将构建好的镜像导出为 tar 文件，便于分发
  - 默认导出两个镜像到 `dist/` 目录
  - 支持指定导出目录、选择导出单个镜像、可选 gzip 压缩
  - 文件命名格式：`caffe-cpu-origin-runtime_{YYYYMMDD}.tar` 和 `caffe-cpu-origin-jupyter_{YYYYMMDD}.tar`
  - 导出后自动校验：检查文件存在、大小合理、可通过 docker load 识别
  - 导出完成后打印 SHA256 校验和供用户验证
  - 创建 dist/.gitkeep 确保目录可提交
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-4.1: 执行 `./export.sh` 在 dist/ 目录生成两个 tar 文件
  - `programmatic` TR-4.2: tar 文件大小 > 1GB（runtime）和 > 1.5GB（jupyter）
  - `programmatic` TR-4.3: `./export.sh --compress` 生成 .tar.gz 文件
  - `programmatic` TR-4.4: 导出的 tar 文件包含 manifest.json（OCI 格式验证）
  - `human-judgement` TR-4.5: 导出完成后显示文件大小、路径、SHA256 校验和

## [x] Task 5: 创建镜像加载辅助脚本 (load-and-verify.sh)
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 创建 `load-and-verify.sh` 脚本，提供给最终用户使用
  - 功能：加载 tar 镜像、自动验证镜像完整性、输出使用提示
  - 支持从本地 tar 文件或 tar.gz 压缩包加载
  - 加载后自动运行 verify-caffe.sh 验证镜像功能
  - 加载成功后打印快速开始命令示例
  - 处理加载错误（文件损坏、Docker 未运行等）并给出解决方案
- **Acceptance Criteria Addressed**: AC-4, AC-7
- **Test Requirements**:
  - `programmatic` TR-5.1: 先 `docker rmi` 删除镜像，执行 load-and-verify.sh 可成功加载并验证
  - `programmatic` TR-5.2: 加载后 verify-caffe.sh 自动运行且全部通过
  - `human-judgement` TR-5.3: 脚本输出包含下一步操作指引（如何运行、如何访问 Jupyter）

## [x] Task 6: 为运行时镜像添加 HEALTHCHECK
- **Priority**: medium
- **Depends On**: Task 1, Task 2
- **Description**:
  - 在 Dockerfile 的 runtime 阶段添加 HEALTHCHECK 指令
  - Jupyter 镜像 HEALTHCHECK 检查 SSH 和 Jupyter 服务是否响应
  - 基础 runtime 镜像 HEALTHCHECK 检查 caffe Python 模块能否导入
  - 健康检查间隔：30 秒，超时 10 秒，启动等待 10 秒，重试 3 次
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-8
- **Test Requirements**:
  - `programmatic` TR-6.1: runtime 镜像 `docker inspect` 显示 Health 配置存在
  - `programmatic` TR-6.2: 容器运行 30 秒后 `docker inspect` 显示 health 状态为 healthy
  - `programmatic` TR-6.3: Jupyter 镜像健康检查验证 8888 端口和 22 端口可访问

## [x] Task 7: 编写用户使用指南 (USER_GUIDE.md)
- **Priority**: high
- **Depends On**: Task 3, Task 4, Task 5
- **Description**:
  - 在 docker/origin/ 目录下创建 USER_GUIDE.md，面向最终用户（非开发者）
  - 文档结构：
    1. 简介：这是什么，包含什么
    2. 前置要求：Docker 安装（各平台简要说明或链接）
    3. 快速开始（3 步以内）：加载镜像 → 运行 → 验证
    4. 使用基础镜像：交互式使用、运行 Python 脚本、常用命令示例
    5. 使用 Jupyter 镜像：启动、访问 Notebook、SSH 登录、密码/Token 配置
    6. 验证镜像：运行验证脚本、预期输出
    7. 文件传输：如何与容器交换文件（docker cp 示例，避免挂载术语）
    8. 常见问题（FAQ）：至少覆盖 8 个常见问题（端口冲突、内存不足、加载失败、权限问题、Jupyter Token 找不到、import caffe 失败、容器退出、磁盘空间）
    9. 卸载镜像：如何删除镜像释放空间
  - 语言要求：中文，通俗易懂，避免"挂载"、"构建上下文"、"多阶段构建"等内部术语，使用"文件映射"、"生成过程"等通俗表达或直接给出操作步骤
  - 所有命令示例可直接复制粘贴
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `human-judgement` TR-7.1: 快速开始章节 ≤ 3 步即可运行第一个 import caffe 命令
  - `human-judgement` TR-7.2: 所有代码块/命令可直接复制执行
  - `human-judgement` TR-7.3: FAQ 章节包含 ≥ 8 个问题和解决方案
  - `human-judgement` TR-7.4: 文档无内部开发术语，面向完全不了解 Docker 的用户也能按步骤操作
  - `human-judgement` TR-7.5: Jupyter 访问步骤包含 URL 示例、Token 位置说明

## [ ] Task 8: 构建两个镜像并执行自包含验证
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 6
- **Description**:
  - 执行构建脚本，实际构建 origin-runtime 和 origin-jupyter 两个镜像
  - 验证：不挂载任何目录时，两个镜像均可正常运行 caffe
  - 记录构建时间、镜像大小等信息
  - 修复构建过程中发现的任何问题
  - **注意**：本任务需要在装有 Docker 的机器上执行，当前 AI 执行环境无 Docker 守护进程
  - **执行步骤**：
    1. 进入 `docker/origin/` 目录
    2. 执行 `./build.sh --all` 构建两个镜像
    3. 构建完成后执行 `docker run --rm caffe-cpu:origin-runtime verify-caffe.sh` 验证
    4. 执行 `./run-standalone.sh jupyter` 启动 Jupyter 容器
    5. 等待 30 秒后执行 `docker inspect --format='{{.State.Health.Status}}' caffe-jupyter` 验证健康状态为 healthy
    6. 执行 `docker exec caffe-jupyter verify-caffe.sh` 验证 Jupyter 容器内 caffe 可用
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-8.1: 两个镜像构建成功，docker images 中可见
  - `programmatic` TR-8.2: `docker run --rm caffe-cpu:origin-runtime verify-caffe.sh` 全部通过
  - `programmatic` TR-8.3: Jupyter 容器启动后健康状态变为 healthy
  - `programmatic` TR-8.4: Jupyter 容器内 `docker exec` 可成功 import caffe

## [ ] Task 9: 导出镜像并执行加载-运行闭环验证
- **Priority**: high
- **Depends On**: Task 4, Task 5, Task 8
- **Description**:
  - 执行 export.sh 导出两个镜像到 dist/ 目录
  - 删除本地镜像，模拟干净环境
  - 使用 load-and-verify.sh 加载导出的 tar 文件
  - 验证加载后的镜像可正常运行，功能与构建时一致
  - 记录导出文件大小、SHA256 等信息
  - **注意**：本任务需要在装有 Docker 的机器上执行，需 Task 8 完成后进行
  - **执行步骤**：
    1. 执行 `./export.sh` 导出两个镜像到 dist/ 目录
    2. 记录输出中的 SHA256 校验和
    3. 执行 `docker rmi caffe-cpu:origin-runtime caffe-cpu:origin-jupyter` 删除本地镜像
    4. 执行 `./load-and-verify.sh` 自动检测 dist/ 中的 tar 文件并加载验证
    5. 验证通过后，执行 `./run-standalone.sh runtime -- python3 -c "import caffe; print('Caffe version:', caffe.__version__)"` 做最终运行验证
    6.（可选）执行 `./export.sh --compress` 生成压缩版本并验证加载
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-9.1: dist/ 目录生成两个 tar 文件
  - `programmatic` TR-9.2: docker rmi 删除镜像后，load-and-verify.sh 加载成功
  - `programmatic` TR-9.3: 加载后的镜像 verify-caffe.sh 全部通过
  - `programmatic` TR-9.4: SHA256 校验和在导出和加载后一致（或 tar 文件校验正确）

## [x] Task 10: 更新 README.md 分发说明
- **Priority**: medium
- **Depends On**: Task 7, Task 9
- **Description**:
  - 在现有 README.md 中添加"镜像分发"章节
  - 说明如何构建独立可分发镜像、如何导出、最终用户如何获取和使用
  - 添加指向 USER_GUIDE.md 的链接
  - 保持现有开发者文档不变，仅新增面向分发的章节
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `human-judgement` TR-10.1: README.md 包含清晰的分发包构建和导出说明
  - `human-judgement` TR-10.2: 明确区分开发者模式（run.sh 挂载）和用户模式（run-standalone.sh 不挂载）
  - `programmatic` TR-10.3: USER_GUIDE.md 链接正确
