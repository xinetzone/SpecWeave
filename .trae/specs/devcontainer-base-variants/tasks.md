# devcontainer-base 镜像变体目录结构 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 创建 variants/ 基础目录结构和共享资源
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 创建 `apps/devcontainer-base/variants/` 目录结构
  - 创建 `variants/README.md`（变体索引和使用指南）
  - 创建 `variants/_template/` 模板目录（供新增变体复制使用）
  - 创建 `variants/shared/` 共享资源目录（共享脚本片段、配置模板）
  - 目录结构规划：
    ```
    variants/
    ├── README.md
    ├── build.sh              # 统一构建脚本
    ├── _template/            # 新变体模板
    │   ├── Dockerfile
    │   ├── .env.example
    │   ├── README.md
    │   └── .agents/
    │       └── rules/
    │           └── dockerfile.md
    ├── shared/               # 共享资源
    │   └── lib/
    │       └── logging.sh    # 复用日志库
    ├── conda/                # conda 变体
    │   ├── Dockerfile
    │   ├── .env.example
    │   ├── README.md
    │   └── .agents/
    │       └── rules/
    │           └── dockerfile.md
    └── conda-llvm/           # conda+llvm 变体
        ├── Dockerfile
        ├── .env.example
        ├── README.md
        └── .agents/
            └── rules/
                └── dockerfile.md
    ```
- **Acceptance Criteria Addressed**: AC-1, AC-6, AC-8
- **Test Requirements**:
  - `programmatic` TR-1.1: 验证所有目录和占位文件已创建
  - `human-judgement` TR-1.2: 目录结构与设计一致，README 包含变体列表和快速开始
- **Notes**: 先创建骨架和占位文件，内容在后续任务填充

## [x] Task 2: 实现 variants/build.sh 统一构建脚本
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 编写 `variants/build.sh` 统一构建脚本，复用 `scripts/lib/logging.sh`
  - 支持参数：
    - `--variant <name>`: 构建指定变体
    - `--all`: 构建所有变体（按依赖顺序）
    - `--list`: 列出可用变体
    - `--no-cache`: 禁用缓存
    - `--cn`: 使用国内镜像源（预设 APT_MIRROR=aliyun, CONDA_MIRROR=tuna, PIP_MIRROR=aliyun）
    - `--build-arg KEY=VALUE`: 传递自定义构建参数
  - 变体依赖关系：conda-llvm 依赖 conda，conda 依赖 devcontainer-base:latest
  - 构建前检查基础镜像是否存在，不存在则提示先构建基础镜像
  - 输出构建计时器汇总
  - 构建后自动执行基础验证（docker run --rm 检查关键命令）
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-5
- **Test Requirements**:
  - `programmatic` TR-2.1: `bash variants/build.sh --list` 正确列出 conda 和 conda-llvm
  - `programmatic` TR-2.2: `bash variants/build.sh --variant conda` 能正确调用 docker build
  - `programmatic` TR-2.3: 脚本有基础镜像存在性检查，不存在时给出清晰提示
  - `human-judgement` TR-2.4: 日志格式与现有 build.sh 一致，使用 [INFO]/[OK]/[ERROR]/[TIMER] 标记
- **Notes**: 参考现有 scripts/build.sh 和 pytorch-base/build.sh 的日志和参数处理模式

## [x] Task 3: 实现 conda 变体 Dockerfile 和配置
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 编写 `variants/conda/Dockerfile`，基于 devcontainer-base:latest
  - Dockerfile 阶段设计（继承基础镜像后追加）：
    - Stage 1/5: 复制 conda 配置相关文件 + 安装 Miniconda3（参考 pytorch-base 模式）
    - Stage 2/5: 配置 conda/pip 镜像源（支持 CONDA_MIRROR 构建参数：tuna/official）
    - Stage 3/5: 创建基础 conda 环境（可选，默认仅安装 Miniconda，不创建额外环境；或创建 base 环境的 Python 版本对齐）
    - Stage 4/5: 配置 conda 激活脚本（/etc/profile.d/conda-init.sh）+ 用户权限
    - Stage 5/5: 元数据 + 清理 + 最终验证（conda --version, python 版本检查等）
  - 编写 `variants/conda/.env.example`（构建参数模板）
  - 编写 `variants/conda/README.md`（使用说明）
  - 编写 `variants/conda/.agents/rules/dockerfile.md`（变体特有规范）
- **Acceptance Criteria Addressed**: AC-2, AC-4, AC-7
- **Test Requirements**:
  - `programmatic` TR-3.1: Dockerfile 使用 `# syntax=docker/dockerfile:1.7-labs` 和 `FROM devcontainer-base:latest`
  - `programmatic` TR-3.2: 支持 APT_MIRROR 和 CONDA_MIRROR 构建参数
  - `programmatic` TR-3.3: 镜像构建后 `docker run --rm devcontainer-base:conda /opt/conda/bin/conda --version` 成功
  - `programmatic` TR-3.4: `/opt/venv` 仍然存在且可访问（jupyter 等可用）
  - `programmatic` TR-3.5: `/etc/profile.d/conda-init.sh` 存在且包含 conda 初始化逻辑
  - `human-judgement` TR-3.6: Dockerfile 遵循7阶段构建模式，有 [TIMER] 计时器和 [VALIDATION CHECKPOINT]
- **Notes**: 
  - Miniconda 路径固定 /opt/conda，不修改系统 PATH 默认（保持 venv 优先）
  - 参考 pytorch-base/Dockerfile 的 Miniconda 安装和镜像源配置逻辑
  - 不自动激活 conda 环境，避免干扰系统 venv 的 Jupyter 服务

## [x] Task 4: 实现 conda-llvm 变体 Dockerfile 和配置
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 编写 `variants/conda-llvm/Dockerfile`，基于 devcontainer-base:conda（或 FROM devcontainer-base:latest 后重新走 conda 安装流程，考虑缓存优化）
  - 策略选择：直接 FROM devcontainer-base:conda 以利用层缓存
  - Dockerfile 阶段设计：
    - Stage 1/4: 配置 conda 频道（添加 conda-forge 优先级）
    - Stage 2/4: 通过 conda 安装 LLVM 22.1.8、clang 22.1.8、cmake、ninja（参考 caffe-ffi-jupyter 配置）
    - Stage 3/4: 配置环境变量（LLVM_CONFIG、PATH 包含 conda 环境 bin）
    - Stage 4/4: 元数据 + 清理 + 最终验证（llvm-config --version, clang --version, cmake --version, ninja --version）
  - 编写 `variants/conda-llvm/.env.example`
  - 编写 `variants/conda-llvm/README.md`
  - 编写 `variants/conda-llvm/.agents/rules/dockerfile.md`
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-4.1: Dockerfile FROM devcontainer-base:conda（或正确的基础镜像引用）
  - `programmatic` TR-4.2: 镜像构建后 `docker run --rm devcontainer-base:conda-llvm llvm-config --version` 返回 22.1.8
  - `programmatic` TR-4.3: clang --version 返回 22.1.8
  - `programmatic` TR-4.4: cmake 和 ninja 命令可用
  - `programmatic` TR-4.5: conda 命令可用，基础镜像服务（SSH/Jupyter）不受影响
  - `human-judgement` TR-4.6: LLVM/clang 安装使用 conda-forge 频道，版本锁定为 22.1.8
- **Notes**: 
  - LLVM 版本必须是 22.1.8（与项目 caffe-ffi 约束一致）
  - conda 安装命令参考：`conda install -y -c conda-forge llvmdev=22.1.8 clangdev=22.1.8 clang=22.1.8 cmake ninja`
  - 需要验证 llvm-config 符号链接正确

## [x] Task 5: 实现 _template/ 模板目录内容
- **Priority**: medium
- **Depends On**: Task 3, Task 4
- **Description**:
  - 基于 conda 变体的实现，提炼通用模板填充到 `variants/_template/`
  - 模板 Dockerfile 使用占位符（如 `__VARIANT_NAME__`、`__BASE_IMAGE__`、`__EXTRA_INSTALL__`）
  - 模板 README.md 包含新变体创建 Checklist
  - 模板 .env.example 包含所有可配置构建参数
  - 在 variants/README.md 中添加"如何新增变体"章节，说明复制模板+修改配置流程
- **Acceptance Criteria Addressed**: AC-1, AC-8
- **Test Requirements**:
  - `human-judgement` TR-5.1: 模板 Dockerfile 结构清晰，注释说明哪些部分需要修改
  - `human-judgement` TR-5.2: 新增变体指南包含：复制模板→重命名→修改 Dockerfile→修改 README→更新变体列表 5步流程
- **Notes**: 模板在 Task 3/4 完成后提炼，确保模板与实际实现一致

## [x] Task 6: 更新 devcontainer-base 主 AGENTS.md 添加 variants 路由
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 在 `apps/devcontainer-base/AGENTS.md` 的嵌套路由关系图中添加 variants/ 目录
  - 在上下文路由表中添加"变体构建/变体开发"路由条目指向 variants/README.md
  - 在核心规范入口表中添加 variants 相关入口
  - 在快速开始部分添加变体构建示例命令
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `human-judgement` TR-6.1: AGENTS.md 中 variants/ 目录结构正确展示
  - `human-judgement` TR-6.2: 路由表包含变体构建入口
  - `programmatic` TR-6.3: 所有内部链接有效（无断链）
- **Notes**: 使用相对路径链接，遵循现有的 AGENTS.md 格式

## [x] Task 7: 端到端验证（静态验证 + Docker构建待用户执行）
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4
- **Description**:
  - 执行端到端验证流程：
    1. 确认 devcontainer-base:latest 已构建（如果没有则先构建）
    2. 执行 `bash variants/build.sh --variant conda` 构建 conda 变体
    3. 运行 conda 变体容器，验证：conda --version、python --version、/opt/venv 存在、jupyter 可导入、sshd 配置有效
    4. 执行 `bash variants/build.sh --variant conda-llvm` 构建 conda-llvm 变体
    5. 运行 conda-llvm 变体容器，验证：llvm-config --version、clang --version、cmake --version、ninja --version、基础服务正常
    6. 执行 `bash variants/build.sh --list` 验证列表功能
  - 修复发现的问题
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-7
- **Test Requirements**:
  - `programmatic` TR-7.1: conda 镜像构建成功，关键命令验证通过
  - `programmatic` TR-7.2: conda-llvm 镜像构建成功，LLVM/clang/cmake/ninja 版本正确
  - `programmatic` TR-7.3: 两个变体都继承了 SSH/Docker/Jupyter 服务，可通过健康检查
  - `programmatic` TR-7.4: conda 与系统 venv 共存无冲突
  - `human-judgement` TR-7.5: 构建日志清晰，错误提示友好
- **Notes**: 这是集成验证任务，需要在 Docker 环境中实际执行构建和运行
