# Hermes Conda 环境创建与源码安装 - The Implementation Plan

## [x] Task 1: 定位 conda 并验证可用性
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 通过完整路径 `C:\ProgramData\miniconda3\Scripts\conda.exe` 验证 conda 可执行
  - 检查可用的 Python 版本（`conda search python` 或直接尝试创建 3.11 环境）
  - 确认 conda 环境目录权限
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: `& 'C:\ProgramData\miniconda3\Scripts\conda.exe' --version` 成功输出版本号
  - `programmatic` TR-1.2: `& 'C:\ProgramData\miniconda3\Scripts\conda.exe' info --envs` 成功列出已有环境
- **Notes**: conda 未在 PATH 中，所有 conda 命令需使用完整路径或先初始化 shell

## [x] Task 2: 创建 conda 虚拟环境（Python 3.13）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 使用 conda 创建名为 `hermes` 的虚拟环境，Python 版本 3.13
  - 命令：`conda create -n hermes python=3.13 -y`
  - 验证环境中 pip 可用
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-2.1: `conda env list` 中出现 `hermes` 环境
  - `programmatic` TR-2.2: 激活环境后 `python --version` 输出 3.13.x
  - `programmatic` TR-2.3: 激活环境后 `pip --version` 正常输出
- **Notes**: Windows 下 conda activate 需要先初始化 shell 或使用 `conda run -n hermes`；Python 3.13 是 hermes 项目 type-check 目标版本，pydantic-core 等 Rust 扩展已提供 cp313 wheels

## [x] Task 3: 在 conda 环境中安装 hermes-agent（editable 模式 + 核心 extras）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 激活 hermes conda 环境
  - 切换到源码目录 `.chaos/hermes-agent`
  - 升级 pip/setuptools/wheel（防止旧版本导致安装问题）
  - 执行 editable 安装：`pip install -e ".[web,mcp]"`
  - 若网络超时或依赖冲突，尝试使用 uv pip install 替代
  - Windows 平台特定依赖（pywinpty、pywin32、tzdata、concurrent-log-handler）应随核心依赖自动安装
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-3.1: 安装过程无致命错误（exit code 0）
  - `programmatic` TR-3.2: `pip show hermes-agent` 显示 Location 指向源码目录（editable 模式）
  - `programmatic` TR-3.3: `pip list | findstr fastapi` 显示 fastapi 已安装
  - `programmatic` TR-3.4: `pip list | findstr mcp` 显示 mcp 已安装
- **Notes**: 
  - `nemo-relay` 在 Windows AMD64 上有 wheel 支持，应正常安装
  - `python-olm`（matrix extra）不安装，避免 Windows 编译问题
  - 若 cryptography 编译失败，可能需要 Visual C++ Build Tools，但 wheel 应该可用

## [x] Task 4: 验证 hermes CLI 可用性
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 在 hermes conda 环境中运行 `hermes --version` 验证命令可用
  - 运行 `hermes --help` 验证帮助信息输出
  - 运行 `python -c "from hermes_cli.main import main; print('import ok')"` 验证 Python 导入
  - 验证 `hermes doctor` 命令可运行（可能会报告未配置 API Key，但不应崩溃）
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-4.1: `hermes --version` 输出包含版本号 0.20.0，exit code 0
  - `programmatic` TR-4.2: `hermes --help` 输出帮助文本，包含 model/config/setup 等子命令
  - `programmatic` TR-4.3: Python import hermes_cli 无 ModuleNotFoundError
  - `programmatic` TR-4.4: `hermes doctor` 可启动并输出诊断信息（可接受配置警告）
- **Notes**: hermes 首次运行可能会创建 `~/.hermes/` 配置目录

## [x] Task 5: 输出环境使用说明
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 记录激活环境的命令
  - 记录首次配置步骤（`hermes setup` 或 `hermes model`）
  - 记录启动 Web Dashboard 的命令
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `human-judgement` TR-5.1: 输出的使用说明清晰、可操作，包含激活/配置/启动三个核心步骤
- **Notes**: 纯文档输出，无代码变更
