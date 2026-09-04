# jupyter-podman-rootless WSL 桥接转换 - 实施计划

## [x] Task 1: 核心问题解答与原理说明
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 直接回答用户问题：**不能直接使用 `wsl -d` 启动那个 tar.gz**
  - 解释两种 tar.gz 格式的本质区别：
    - `podman save` 输出：OCI 分层镜像（docker-archive），含 whiteout 标记、多层叠加、元数据
    - `wsl --import` 需要：flat rootfs（单层文件系统快照，容器运行时的完整文件树）
  - 说明直接导入的后果：`.wh.*` 垃圾文件、权限错误、无法正常启动
  - 指出 `seven-concepts-cmd` 是 AI Skill 不是镜像
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `human-judgement` TR-1.1: 回答清晰明确，"不能"二字在显眼位置
  - `human-judgement` TR-1.2: 原理解释易懂，不要求用户预先了解 OCI 格式
  - `human-judgement` TR-1.3: 明确区分 seven-concepts-cmd（Skill）与镜像文件
- **Notes**: 本任务无需代码修改，直接在对话中回答即可

## [x] Task 2: 提供基于 docker-wsl-bridge-cmd 的手动转换指南
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 适配 docker-wsl-bridge-cmd 的 convert 流程到 jupyter-podman-rootless 镜像
  - 针对 jupyter 镜像定制参数：
    - 默认用户：devuser（UID=1000）
    - Conda 路径：/opt/conda（需要配置 /etc/profile.d/conda.sh）
    - systemd：false
  - 提供完整的 PowerShell 分步脚本
  - 包含验证步骤（Smoke Test）
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: 脚本中的路径转换正确（Windows → /mnt/）
  - `programmatic` TR-2.2: 使用 rootful podman（sudo podman）避免 UID 偏移
  - `programmatic` TR-2.3: 包含 conda 激活配置
  - `human-judgement` TR-2.4: 步骤清晰可复制执行
- **Notes**: 参考 docker-wsl-bridge-cmd SKILL.md 第 5.2 节

## [x] Task 3: 为 bin/jpman 添加 wsl-export 命令
- **Priority**: high (用户确认需要 CLI 增强)
- **Depends On**: Task 2
- **Description**:
  - 在 `bin/jpman` bash 脚本中添加 `wsl-export` 命令
  - 功能：从 .image-cache 中的镜像 tar.gz 一键转换为 WSL2 发行版
  - 实现步骤：
    1. WSL 环境检测（in_wsl + wsl.exe 可用）
    2. 镜像缓存定位与检查
    3. rootful podman 检测（sudo -n 非交互优先，rootless 回退带警告）
    4. wslpath 路径转换（WSL ↔ Windows）
    5. podman load → podman create → podman export（flat rootfs, gzip -1）
    6. wsl --import 注册为 WSL2 发行版
    7. 配置 /etc/wsl.conf（default=devuser, systemd=false, automount metadata）
    8. 配置 /etc/profile.d/conda.sh（非交互 shell conda 激活）
    9. wsl --terminate 应用配置
    10. 默认用户验证 + 调用 wsl-verify 执行 Smoke Test
  - 支持参数：`--distro-name/-n`, `--install-dir/-d`, `--force/-f`
  - 临时容器 EXIT trap 清理
  - **命名修正**：脚本从 `jupyter` 重命名为 `jpman`，避免与 Python jupyter CLI 冲突
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-3.1: 命令可通过 `bash bin/jpman wsl-export` 执行
  - `programmatic` TR-3.2: 幂等检查正常（已存在则提示先 unregister）
  - `programmatic` TR-3.3: 转换后默认用户是 devuser（非 root）
  - `programmatic` TR-3.4: conda 在非交互 shell 中可用（`wsl -d <name> -- sh -l -c "conda --version"`）
  - `programmatic` TR-3.5: bash -n 语法检查通过
  - `human-judgement` TR-3.6: 错误提示清晰友好
- **Notes**:
  - 通过 wsl.exe interop 直接在 WSL 内管理 Windows 侧 WSL 发行版
  - 默认安装目录：$PROJECT_ROOT/.wsl-cache/<distro-name>/
  - .wsl-cache/ 已加入 .gitignore

## [x] Task 4: 为 bin/jpman 添加 wsl-verify 命令
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 添加 `wsl-verify` 命令执行 14 项 Smoke Test
  - 检查项（4 类）：
    - Basic Environment: Startup, User, Writable, Home dir
    - Drive Mounts: C: drive, D: drive（best-effort，不存在则 SKIP）
    - Python/Conda: Conda, Python 3.14, Python path, Free-threading (GIL disabled), Pip
    - Jupyter & Tools: JupyterLab, Git, Bash, Locale (zh/en UTF-8)
  - 彩色 PASS/FAIL/SKIP 输出，最终汇总 pass/fail 计数
  - 全部通过返回 0，有失败返回 1
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-4.1: 所有检查项通过时返回 exit code 0
  - `programmatic` TR-4.2: 失败项清晰标记（红色 ❌ FAIL）
  - `programmatic` TR-4.3: Free-thread 检查引号正确（单独处理避免嵌套转义问题）
  - `human-judgement` TR-4.4: 输出格式易读（分节+颜色+结果汇总）
- **Notes**:
  - 所有远程命令使用 `wsl -d <distro> -- sh -l -c`（login shell 确保 conda 加载）
  - wsl.exe UTF-16 输出空字符和 CR 通过 tr 过滤

## [x] Task 5: 新增 PowerShell 7 (pwsh) 原生版本 jpman.ps1
- **Priority**: high
- **Depends On**: Task 3, Task 4
- **Description**:
  - 在 `bin/` 目录新增 `jpman.ps1`，PowerShell 7 原生 CLI
  - 设计模式：混合架构——容器生命周期命令委托给 WSL 中 bash jpman，wsl-export/wsl-verify 在 pwsh 中原生实现
  - pwsh 原生实现功能：
    - wsl.exe 互操作（自动定位 wsl.exe）
    - Windows ↔ WSL 路径转换（wslpath + 手动 fallback）
    - .env 文件加载（共享 JUPYTER_* 配置）
    - wsl-export：5步一键转换（rootful 优先 rootless 回退、临时文件传递 wsl.conf/conda.sh、EXIT 清理、用户一致性）
    - wsl-verify：14项 Smoke Test（彩色输出、UTF-16 解码、临时 Python 文件避免引号嵌套）
    - $PSStyle 彩色输出
  - 委托命令：start/stop/restart/status/shell/logs/exec/root/info/url/save/load/rebuild/rebuild-all/keepalive/install → 通过 wsl.exe 调用 bash jpman
  - 修复的问题（V 阶段）：
    - Invoke-Check 嵌套函数作用域 bug（$script:_check_pass/_check_fail）
    - rootful/rootless podman 用户上下文一致性（$podmanUser 变量追踪）
    - Free-threading 检查使用临时 .py 文件避免多层引号转义
- **Acceptance Criteria Addressed**: AC-3, AC-4 (pwsh 原生)
- **Test Requirements**:
  - `programmatic` TR-5.1: pwsh AST 语法解析通过，无 parser errors
  - `programmatic` TR-5.2: help 命令正常输出完整命令列表
  - `programmatic` TR-5.3: bash jpman 帮助文本包含 pwsh 版本使用说明
  - `human-judgement` TR-5.4: 参数命名与 bash 版本一致（-n/-d/-f 长选项 --distro-name/--install-dir/--force）
- **Notes**:
  - 三个入口共存：jpman（bash/WSL）、jpman.cmd（cmd wrapper）、jpman.ps1（pwsh7 原生）
  - `#Requires -Version 7.0` 确保 pwsh7+ 运行
  - 委托模式确保功能对等——bash 版本新增命令自动可用
