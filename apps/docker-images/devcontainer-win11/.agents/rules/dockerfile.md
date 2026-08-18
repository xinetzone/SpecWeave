# Windows Dockerfile 编写规范

## 基础规范

### 1. 转义字符
Dockerfile 第一行必须设置 Windows 转义字符：
```dockerfile
# escape=`
```
使用反引号 `` ` `` 作为续行符，而非 Linux 的 `\`。

### 2. SHELL 指令
Windows 容器默认使用 `cmd.exe`，必须显式切换到 PowerShell：
```dockerfile
# 初始阶段使用 Windows PowerShell 5.1
SHELL ["powershell", "-Command", "$ErrorActionPreference = 'Stop'; ..."]

# 安装 PowerShell 7 后切换
SHELL ["C:\\Program Files\\PowerShell\\7\\pwsh.exe", "-Command", "..."]
```

### 3. 路径规范
- Windows 路径使用反斜杠 `\`，在 Dockerfile 中需要双写 `\\`
- 工作目录约定：`C:\workspace`
- Conda 安装路径：`C:\conda`
- 配置文件路径：`C:\ProgramData\devcontainer\`

## Stage 架构

Windows Dockerfile 采用 7 Stage 分层设计（等价 Linux 版设计原则）：

| Stage | 内容 | 变化频率 |
|-------|------|---------|
| 1/7 | 基础环境 + PowerShell配置 + 中文编码/时区 | 最低 |
| 2/7 | PowerShell 7 + Git for Windows | 低 |
| 3/7 | OpenSSH Server 安装配置 | 低 |
| 4/7 | Miniforge3 + Python free-threading + Jupyter + C编译器 (3子层) | 中 |
| 5/7 | Docker CLI + Compose (DooD) | 低 |
| 6/7 | 用户devuser + 配置文件COPY + entrypoint | 中 |
| 7/7 | build-info + 清理 + 最终验证 + 计时汇总 | 最低 |

### 分层设计原则

- **P1 变化频率分层**: 同频率同层，低频在前，高频在后
- **P2 缓存保护**: conda create 等高耗时操作必须独立成层
- **P5 脚本外置**: >50行的 PowerShell 逻辑抽取到 `scripts/dockerfile/` 目录
- **P7 同层修改**: 文件创建、权限设置、清理在同一 RUN 层完成（Windows 也适用 COW 原则）

## Python Free-Threading 配置

### 安装方式
通过 conda-forge `python-freethreading` 元包安装：
```powershell
conda create -n main -y --channel conda-forge python=3.14 python-freethreading jupyterlab ipykernel
```

**关键注意事项**：
1. 必须同时指定 `python=3.14` 和 `python-freethreading`，避免 solver 切换回标准 GIL 版本
2. `python-freethreading` 是 conda-forge noarch 元包，会拉取 cp314t 版本的 Python 解释器

### Py_GIL_DISABLED 环境变量
必须在**系统级别（Machine scope）**设置 `Py_GIL_DISABLED=1`：
```powershell
[Environment]::SetEnvironmentVariable('Py_GIL_DISABLED', '1', 'Machine')
$env:Py_GIL_DISABLED = '1'
```

此环境变量的作用：
1. **运行时**: Python 启动时默认禁用 GIL
2. **编译时**: pip/setuptools 从源码编译 C 扩展时自动定义 `Py_GIL_DISABLED=1` 宏

### C 编译器工具链
必须安装 C 编译器以支持 pip 从源码编译 free-threading C 扩展：
- **首选**: conda-forge `m2w64-toolchain`（MinGW-w64 GCC，轻量 ~200MB）
- **备选**: MSVC Build Tools（体积大 ~8GB，兼容性最好但安装复杂）

```powershell
conda install -n main -y --channel conda-forge m2w64-toolchain m2w64-gcc m2-make
```

### Free-Threading 验证命令
构建阶段必须执行验证：
```powershell
# 1. 检查编译时标记
python -c "import sysconfig; assert sysconfig.get_config_var('Py_GIL_DISABLED') == 1"

# 2. 检查 SOABI 包含 t 后缀（cp314t）
python -c "import sysconfig; soabi=sysconfig.get_config_var('SOABI'); assert 't' in soabi"

# 3. 检查运行时 GIL 状态
python -c "import sys; assert not sys._is_gil_enabled()"

# 4. 检查系统环境变量
# [Environment]::GetEnvironmentVariable('Py_GIL_DISABLED', 'Machine') 应为 '1'
```

## Docker DooD 配置

Windows 容器不支持 DinD（Docker-in-Docker），使用 DooD（Docker-out-of-Docker）：
1. 仅安装 Docker CLI 静态二进制（不安装 dockerd）
2. 挂载宿主命名管道：`-v //./pipe/docker_engine://./pipe/docker_engine`
3. 设置 DOCKER_HOST：`npipe:////./pipe/docker_engine`

Docker CLI 下载地址：`https://download.docker.com/win/static/stable/x86_64/docker-<version>.zip`
Docker Compose v2 作为 CLI plugin 安装到 `cli-plugins/docker-compose.exe`

## 计时日志规范

每个 Stage 结束时输出 `[TIMER]` 日志，格式：
```
[TIMER] Stage X/7 (description) took NNs | Cumulative: NNs
```

最终输出 BUILD TIMING SUMMARY 表格，与 Linux 版格式对齐。

## 验证检查点

Stage 6（配置COPY后）和 Stage 7（最终验证）必须执行 `[VALIDATION CHECKPOINT]`：
- sshd 配置验证
- entrypoint.ps1 PowerShell 语法检查（无 bash -n 等价物，需使用 `[scriptblock]` 解析）
- free-threading Python 验证（4项检查，见上）
- C 编译器可用验证
- 核心 C 扩展导入验证（sqlite3、ssl、zlib、hashlib、json）
- docker CLI / git / conda / jupyter 命令可用性

## 清理策略

Stage 7 清理遵循「只删除不修改」原则（避免 COW 膨胀）：
1. 删除临时文件（C:\temp\*、C:\Windows\Temp\*）
2. conda clean -a -y
3. pip cache purge
4. 删除 __pycache__ 目录和 .pyc 文件
5. 删除 Windows 更新日志缓存

Windows 容器不支持 Linux 的 strip 操作（Go 二进制 strip 可在同层执行，但 Python 相关文件不做 strip）。

## 常见陷阱

1. **换行符问题**: PowerShell 脚本可能从 Linux 环境带来 CRLF，Windows 原生环境无此问题
2. **路径空格**: 路径包含空格时使用引号包裹（如 `"C:\Program Files\PowerShell\7\pwsh.exe"`）
3. **执行策略**: PowerShell 脚本执行前必须设置 `Set-ExecutionPolicy Bypass`
4. **ProgressPreference**: 长下载操作设置 `$ProgressPreference = 'SilentlyContinue'` 加速
5. **TLS 1.2**: 下载文件前必须启用 TLS 1.2：`[Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12`
6. **conda activate**: 在 Dockerfile RUN 中 conda activate 不生效，需直接使用 `C:\conda\envs\main\python.exe` 完整路径
7. **Py_GIL_DISABLED 必须 Machine 级别**: 仅设置进程级环境变量不会传递到后续 RUN 层
