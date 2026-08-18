# devcontainer-win11 - Implementation Plan

## Task 1: 创建应用目录结构和 AGENTS.md 入口
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `apps/docker-images/devcontainer-win11/` 目录
  - 创建 `AGENTS.md`（遵循 SpecWeave 工作区发现协议，包含启动协议、上下文路由表、规范入口）
  - 创建 `.agents/rules/` 目录结构
  - 创建子目录：`config/`、`scripts/`、`scripts/dockerfile/`（外部脚本）、`examples/`
  - 更新 `apps/AGENTS.md` 应用路由表，注册 devcontainer-win11 应用
- **Acceptance Criteria Addressed**: AC-1, AC-11
- **Test Requirements**:
  - ✅ TR-1.1: `apps/docker-images/devcontainer-win11/AGENTS.md` 存在且包含"启动协议"关键词
  - ✅ TR-1.2: AGENTS.md 正确引用父级 `../../AGENTS.md`
  - ✅ TR-1.3: 子目录结构完整（config/, scripts/, scripts/dockerfile/, examples/）
  - ✅ TR-1.4: `apps/AGENTS.md` 中已添加 devcontainer-win11 条目（路由表+路由图+资产索引+边界声明）
- **Notes**: AGENTS.md 参考 devcontainer-base/AGENTS.md 的结构，适配 Windows 特有内容

## Task 2: 编写 Dockerfile（Stage 1-3：基础镜像 + 系统配置 + SSH）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于 `mcr.microsoft.com/windows/servercore:ltsc2022`
  - Stage 1: 设置环境变量、PowerShell 执行策略、SHELL 指令
  - Stage 2: 安装系统更新和常用工具（通过 PowerShell 安装）
  - Stage 3: 安装 OpenSSH Server（Add-WindowsCapability），配置 sshd_config，设置自动启动
  - 设置中文编码（UTF-8 code page 65001）和时区（China Standard Time）
  - 安装 PowerShell 7（通过 GitHub 发布页下载 MSI 静默安装）
  - 每个阶段输出 [TIMER] 日志
  - 使用 BuildKit 缓存（若 Windows 容器支持）
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-7, AC-10, AC-12
- **Test Requirements**:
  - `rule` TR-2.1: Dockerfile 首行设置 escape=` （Windows 容器转义字符）
  - `rule` TR-2.2: SHELL 指令设置为 PowerShell
  - `rule` TR-2.3: OpenSSH Server 安装命令正确（Add-WindowsCapability 或离线安装）
  - `rule` TR-2.4: 时区设置命令正确（Set-TimeZone 或 tzutil）
  - `rule` TR-2.5: 每个 Stage 输出 [TIMER] 标记
  - `rule` TR-2.6: 语法检查：在 Windows 上 `docker build` 无语法错误
- **Notes**: 参考 Linux 版 Dockerfile 的 Stage 1/2 结构，适配 Windows 命令；注意 Windows 容器中 RUN 命令默认使用 cmd.exe，需要显式切换到 PowerShell

## Task 3: 编写 Dockerfile（Stage 4-5：Miniforge3 + Python free-threading + Jupyter + 编译工具链）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - Stage 4: 下载并静默安装 Miniforge3-Windows-x86_64.exe 到 C:\conda
  - 配置 conda（.condarc），设置 conda-forge 源和国内镜像支持
  - 创建主环境（`conda create -n main python=3.14 python-freethreading -c conda-forge`），安装 Python 3.14 free-threading (cp314t)
  - 设置系统环境变量 `Py_GIL_DISABLED=1`（[Environment]::SetEnvironmentVariable，Machine 级别）
  - 安装 JupyterLab/ipykernel 到主环境（验证 free-threading 兼容）
  - 配置 Jupyter（token、工作目录 C:\workspace、CORS 设置）
  - Stage 4b: 安装 C/C++ 编译工具链（优先使用 conda m2w64-toolchain，或 MSVC Build Tools 最小安装），支持 pip 从源码编译 free-threading C 扩展
  - Stage 5: 安装 Docker CLI 和 Compose Plugin（通过 Docker 官方静态二进制或 choco/手动下载）
  - 配置 Docker CLI 连接宿主命名管道
  - 安装 git for Windows（静默安装）
  - 每个阶段输出 [TIMER] 日志
- **Acceptance Criteria Addressed**: AC-2, AC-4, AC-5, AC-6, AC-10, AC-14, AC-15
- **Test Requirements**:
  - `rule` TR-3.1: Miniforge3 安装路径为 C:\conda
  - `rule` TR-3.2: conda --version 和 python --version 在构建验证中可执行
  - `rule` TR-3.3: `python -c "import sysconfig; assert sysconfig.get_config_var('Py_GIL_DISABLED') == 1"` 验证 free-threading
  - `rule` TR-3.4: 系统环境变量 `Py_GIL_DISABLED=1` 已设置（Machine 级别）
  - `rule` TR-3.5: JupyterLab 安装在 conda 环境中，jupyter --version 可执行
  - `rule` TR-3.6: docker --version 和 docker compose version 可执行
  - `rule` TR-3.7: git --version 可执行
  - `rule` TR-3.8: PATH 环境变量包含 conda 和 Docker CLI 路径
  - `rule` TR-3.9: C 编译器可执行（`cl.exe` 或 `gcc.exe` 可用），支持 pip 从源码编译
  - `rubric` TR-3.10: 包安装可观测性（分组安装、版本输出、冲突检测、free-threading 标识）；scale 1-5；anchors 1=一次性安装无输出, 3=有分组但缺诊断, 5=pip/conda分组+版本汇总+free-threading验证+check；threshold >= 4
- **Notes**: Miniforge3 Windows 版使用 `/InstallationType=JustMe /RegisterPython=0 /S /D=C:\conda` 静默安装参数；`python-freethreading` 是 conda-forge noarch 元包，它会拉取 cp314t 版本的 Python 解释器；Docker CLI 可下载 static 二进制；编译工具优先尝试 conda-forge 的 `m2w64-toolchain`（轻量），若不满足要求则退回到 MSVC Build Tools（体积大但兼容性好）；注意 Windows 路径分隔符

## Task 4: 编写 Dockerfile（Stage 6-7：用户配置 + 元数据 + 验证）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - Stage 6: 创建非管理员用户 devuser（使用 net user 或 New-LocalUser）
  - 创建工作目录 C:\workspace，设置权限
  - 配置 devuser 的 PowerShell profile（conda 初始化，确保 Py_GIL_DISABLED 对用户可见）
  - 复制配置文件（sshd_config、jupyter 配置、PowerShell profile）
  - Stage 7: 写入构建元数据到 C:\ProgramData\devcontainer-build-info（包含 PYTHON_FLAVOR=freethreading 字段）
  - 执行清理（删除临时文件、WinSxS 清理、包缓存、编译工具临时文件）
  - [VALIDATION CHECKPOINT] 最终验证：python、conda、docker、git、jupyter 命令可用，sshd 配置正确，free-threading 验证（Py_GIL_DISABLED==1、sys._is_gil_enabled()==False），编译器可用
  - 输出 BUILD TIMING SUMMARY 表格
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-8, AC-10, AC-12, AC-14, AC-15
- **Test Requirements**:
  - `rule` TR-4.1: devuser 用户存在且不在 Administrators 组
  - `rule` TR-4.2: C:\workspace 目录存在，devuser 有读写权限
  - `rule` TR-4.3: 构建元数据文件存在且包含 BASE_IMAGE、BUILD_DATE、PYTHON_FLAVOR=freethreading 字段
  - `rule` TR-4.4: [VALIDATION CHECKPOINT] 所有验证命令通过（含 free-threading 验证和编译器验证）
  - `rule` TR-4.5: BUILD TIMING SUMMARY 表格在构建日志末尾输出
  - `rule` TR-4.6: ENTRYPOINT 设置为 entrypoint.ps1，CMD 为空
  - `rule` TR-4.7: free-threading 验证：`python -VV` 输出包含 "free-threading"，`sys._is_gil_enabled()` 返回 False
  - `rule` TR-4.8: 编译器验证：`cl.exe` 或 `gcc.exe` 在 PATH 中可执行
- **Notes**: 清理策略参考 Linux 版 9 步清理但适配 Windows（Cleanmgr、Dism 等）

## Task 5: 编写 entrypoint.ps1 启动脚本
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 编写 PowerShell 启动脚本 `entrypoint.ps1`，功能等价于 Linux 版 entrypoint.sh
  - 解析环境变量（USER_PASSWORD、JUPYTER_TOKEN、GRANT_SUDO 等）
  - 设置用户密码（若提供 USER_PASSWORD）
  - 启动 sshd 服务
  - 启动 JupyterLab（以 devuser 身份，后台进程）
  - 处理信号（SIGTERM 优雅关闭）
  - 输出启动日志和连接信息
  - 支持命令模式（docker run ... <command> 覆盖默认行为）
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-8
- **Test Requirements**:
  - `rule` TR-5.1: entrypoint.ps1 设置 `Set-StrictMode -Version Latest` 和 `$ErrorActionPreference = 'Stop'`
  - `rule` TR-5.2: 容器启动后 sshd 服务正在运行
  - `rule` TR-5.3: 容器启动后 JupyterLab 进程正在运行且监听 8888
  - `rule` TR-5.4: USER_PASSWORD 环境变量可设置 devuser 密码
  - `rule` TR-5.5: 传入命令（如 powershell）时直接执行而非启动服务
  - `rule` TR-5.6: bash -n 等价的 PowerShell 语法检查通过
- **Notes**: Windows 容器中进程管理使用 Start-Process 和 Wait-Process；信号处理在 Windows 上有限，使用 CTRL_EVENT 处理

## Task 6: 编写配置文件
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - `config/sshd_config`: OpenSSH 配置（禁用 root 登录等价的 Administrator 限制、启用密码认证、端口 22）
  - `config/jupyter_notebook_config.py`: Jupyter 配置（ip=0.0.0.0、port=8888、token 从环境变量读取、no-browser）
  - `config/supervisord.conf` 替代方案：编写 `config/services.ps1`（PowerShell 服务启动辅助脚本）
  - `config/Microsoft.PowerShell_profile.ps1`: PowerShell profile（conda 初始化、环境变量设置）
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-6.1: sshd_config 语法正确（sshd -t 等价检查）
  - `rule` TR-6.2: Jupyter 配置监听 0.0.0.0:8888
  - `rule` TR-6.3: 所有配置文件 COPY 到容器内正确路径
- **Notes**: Windows OpenSSH 的 sshd_config 路径为 C:\ProgramData\ssh\sshd_config

## Task 7: 编写构建脚本和启动脚本
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - `scripts/build.ps1`: PowerShell 构建脚本，支持 `--cn` 参数（国内镜像源）、`--tag` 参数、BuildKit 缓存配置
  - `scripts/build.sh`: bash 版本（在 WSL/Git Bash 中调用 powershell.exe 或直接 docker build，供 WSL 用户使用）
  - `scripts/start.ps1`: 一键启动脚本，映射端口、设置密码、挂载卷、等待健康检查
  - `scripts/healthcheck.ps1`: 健康检查脚本，检查 sshd 端口监听和 Jupyter HTTP 响应
  - 可选：`scripts/test-smoke.ps1` 冒烟测试脚本
- **Acceptance Criteria Addressed**: AC-9, AC-13
- **Test Requirements**:
  - `rule` TR-7.1: `.\scripts\build.ps1` 可在 PowerShell 中执行并成功构建镜像
  - `rule` TR-7.2: `.\scripts\build.ps1 --cn` 使用国内镜像源
  - `rule` TR-7.3: `.\scripts\start.ps1` 启动容器，输出 SSH 和 Jupyter 连接信息
  - `rule` TR-7.4: healthcheck.ps1 返回 0 当服务正常，返回 1 当服务异常
  - `rubric` TR-7.5: 开发者体验一致性（命令模式、参数命名、输出格式与 Linux 版对齐）；scale 1-5；anchors 1=完全不同, 3=核心对齐, 5=高度一致；threshold >= 4
- **Notes**: 参考 devcontainer-base/scripts/build.sh 和 start.sh 的参数设计；PowerShell 脚本需处理执行策略问题

## Task 8: 编写 .agents/rules/ 规范文件
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - `.agents/README.md`: 规范目录索引
  - `.agents/rules/dockerfile.md`: Windows Dockerfile 编写规范（escape、SHELL、路径、缓存、清理、验证）
  - `.agents/rules/entrypoint.md`: entrypoint.ps1 编写规范
  - `.agents/rules/build-test.md`: 构建和测试规范
  - `.agents/rules/services.md`: 服务配置规范（sshd、jupyter、docker dood）
- **Acceptance Criteria Addressed**: AC-11
- **Test Requirements**:
  - `rule` TR-8.1: .agents/rules/ 包含 dockerfile.md、entrypoint.md、build-test.md、services.md
  - `rule` TR-8.2: 规范文件中记录了 Windows 容器特有的约束和最佳实践
- **Notes**: 参考 devcontainer-base 的 .agents/rules/ 结构，内容适配 Windows

## Task 9: 构建验证和测试
- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 在 Windows + Docker Desktop (Windows 容器模式) 上执行完整构建
  - 运行容器，验证 SSH 连接
  - 验证 JupyterLab 可访问
  - 验证 Python/conda/Docker CLI/git 可用
  - **验证 free-threading**：`python -c "import sys; assert not sys._is_gil_enabled()"`、`Py_GIL_DISABLED=1` 环境变量、`python -VV` 输出
  - **验证编译器可用**：测试 pip 从源码编译一个小的 C 扩展包
  - 验证健康检查通过
  - 验证中文显示和时区
  - 验证 devuser 权限
  - 记录镜像大小
  - 修复发现的问题
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-10, AC-14, AC-15
- **Test Requirements**:
  - `rule` TR-9.1: docker build 成功完成
  - `rule` TR-9.2: 容器启动后 `docker ps` 显示 healthy
  - `rule` TR-9.3: SSH 连接测试通过（ssh 命令登录成功）
  - `rule` TR-9.4: curl http://localhost:8888 返回 Jupyter 页面
  - `rule` TR-9.5: docker exec 验证 python/conda/docker/git/jupyter 命令
  - `rule` TR-9.6: DooD 模式 docker ps 显示宿主容器列表
  - `rule` TR-9.7: 时区为 China Standard Time
  - `rule` TR-9.8: 镜像大小 ≤ 6GB（压缩后）
  - `rule` TR-9.9: free-threading 验证通过：`sys._is_gil_enabled()` 返回 False，Py_GIL_DISABLED=1
  - `rule` TR-9.10: pip 从源码编译 C 扩展成功（验证编译器配置正确）
- **Notes**: 需要 Windows 环境实际构建测试；若当前环境无法构建 Windows 容器，此任务需在 Windows 机器上执行

## Task 10: 更新 apps/AGENTS.md 和 README 文档
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 9
- **Description**:
  - 在 `apps/AGENTS.md` 应用路由表中添加 devcontainer-win11 条目
  - 在 `apps/AGENTS.md` 嵌套路由图中添加 devcontainer-win11
  - 在 `apps/AGENTS.md` 可用资产索引/边界声明中添加 devcontainer-win11
  - 创建 `.env.example` 文件（已完成，不主动创建 README.md，遵循"不主动创建文档"规则）
- **Acceptance Criteria Addressed**: AC-1, AC-11
- **Test Requirements**:
  - ✅ TR-10.1: apps/AGENTS.md 中包含 devcontainer-win11 条目（路由表+路由图+资产索引+边界声明）
  - ⏭️ TR-10.2: README.md 按需创建（遵循"不主动创建文档"规则，AGENTS.md 已包含快速开始和构建命令）
  - ✅ TR-10.3: AGENTS.md 明确标注 v1.0 功能范围和已知限制
- **Notes**: AGENTS.md 中已包含快速开始命令，.env.example 已创建

## Task 11: 更新 apps/docker-images 分组 README
- **Status**: `completed` (skipped - no grouping README exists)
- **Priority**: low
- **Depends On**: Task 10
- **Description**:
  - 检查 `apps/docker-images/` 是否有 README.md，若有则更新添加 devcontainer-win11 条目
  - 若存在 docker-images 级别的 AGENTS.md，更新路由
- **Acceptance Criteria Addressed**: AC-11
- **Test Requirements**:
  - `rule` TR-11.1: docker-images 分组索引包含 devcontainer-win11 引用（如适用）
- **Notes**: 若 docker-images/ 没有 README 或 AGENTS.md，此任务可取消
