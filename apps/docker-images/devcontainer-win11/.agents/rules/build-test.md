# 构建和测试规范

## 构建前提条件

### 环境要求
1. Windows 10/11 Pro/Enterprise 或 Windows Server 2019+
2. Docker Desktop 4.0+ 已安装
3. **Docker Desktop 切换到 Windows 容器模式**
4. PowerShell 7+（推荐，build.ps1 使用 PowerShell 编写）
5. 网络访问：mcr.microsoft.com、github.com、conda-forge、pypi.org

### 切换到 Windows 容器
```powershell
# 右键 Docker Desktop 托盘图标 -> Switch to Windows containers...
# 或命令行：
& "C:\Program Files\Docker\Docker\DockerCli.exe" -SwitchWindowsEngine
```

## 构建命令

### PowerShell 构建（推荐）
```powershell
# 标准构建
.\scripts\build.ps1

# 使用国内镜像源
.\scripts\build.ps1 -Cn

# 指定标签
.\scripts\build.ps1 -Tag myregistry/devcontainer-win11:v1.0

# 快速模式（减少验证步骤）
.\scripts\build.ps1 -VerifyMode fast

# 无缓存构建
.\scripts\build.ps1 -NoCache
```

### Bash/WSL 构建
```bash
# 在 WSL 或 Git Bash 中
bash scripts/build.sh

# 使用国内镜像
bash scripts/build.sh --cn

# 快速模式
bash scripts/build.sh --fast
```

## 启动命令

### PowerShell 启动
```powershell
# 默认启动（自动生成密码和token）
.\scripts\start.ps1

# 自定义端口和密码
.\scripts\start.ps1 -SshPort 2222 -JupyterPort 8888 -Password "mypassword" -Token "mytoken"

# 指定工作区目录
.\scripts\start.ps1 -Workspace "D:\myproject"
```

### docker run 手动启动
```powershell
docker run -d `
    --name devcontainer-win11 `
    -p 2222:22 `
    -p 8888:8888 `
    -e USER_PASSWORD=devpass `
    -e JUPYTER_TOKEN=mysecret `
    -v //./pipe/docker_engine://./pipe/docker_engine `
    -v ${PWD}/workspace:C:\workspace `
    devcontainer-win11:latest
```

## 验证流程

### 1. 构建验证
构建日志末尾 `[VALIDATION CHECKPOINT]` 必须显示所有检查通过：
- Python free-threading 验证（Py_GIL_DISABLED=1、SOABI 含 t、_is_gil_enabled()=False）
- C 编译器可用（gcc.exe 存在）
- 核心 C 扩展导入成功
- sshd/jupyter/docker/git/conda 命令可用

### 2. 运行验证
```powershell
# 检查容器状态（healthy）
docker ps

# 检查 SSH 连接
ssh devuser@localhost -p 2222

# 检查 Jupyter
curl http://localhost:8888/

# 检查 Docker DooD
docker exec devcontainer-win11 docker ps

# 检查 free-threading
docker exec devcontainer-win11 C:\conda\envs\main\python.exe -c "import sys; print('GIL enabled:', sys._is_gil_enabled())"

# 运行 free-threading demo
docker exec devcontainer-win11 C:\conda\envs\main\python.exe C:\workspace\examples\free_threading_demo.py
```

### 3. 冒烟测试脚本
```powershell
# 进入容器
docker exec -it devcontainer-win11 pwsh.exe

# 验证 Python free-threading
python -c "import sys, sysconfig; print(sys._is_gil_enabled()); print(sysconfig.get_config_var('SOABI'))"

# 验证 pip 源码编译（测试 C 编译器配置）
pip install --no-binary :all: markupsafe
python -c "import markupsafe; print('markupsafe OK')"
```

## 国内镜像配置

### 构建时使用 -Cn 参数
build.ps1 -Cn 会设置：
- Conda mirror: 清华 tuna（mirrors.tuna.tsinghua.edu.cn）
- Pip mirror: 阿里云（mirrors.aliyun.com/pypi/simple）

### 运行时手动配置
容器内已在构建阶段配置国内镜像（若使用 -Cn 构建）。如需运行时修改：
```powershell
# conda
conda config --set default_channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/

# pip
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
```

## 常见问题排查

### 构建失败
1. **网络超时**：使用 `-Cn` 参数或检查网络
2. **Windows 容器模式未切换**：切换 Docker Desktop 到 Windows 容器
3. **磁盘空间**：Windows 容器基础镜像较大（~2.8GB），确保磁盘空间充足
4. **conda solver 卡住**：构建使用 libmamba solver，耐心等待；首次构建 conda 下载包较慢

### 容器启动失败
1. **端口冲突**：更换 -SshPort/-JupyterPort 参数
2. **命名管道不可用**：确保 Docker Desktop 正在运行
3. **查看日志**：`docker logs devcontainer-win11`

### free-threading 相关问题
1. **GIL 未禁用**：检查 `Py_GIL_DISABLED=1` 系统环境变量
2. **C 扩展编译失败**：确认 m2w64-toolchain 已安装，gcc.exe 在 PATH 中
3. **某些包重新启用 GIL**：这是预期行为——不兼容 free-threading 的 C 扩展会在导入时自动重新启用 GIL（会打印警告），这是 Python 3.14 Phase II 的安全机制

## Free-Threading 注意事项

1. **Windows 支持状态**：Python 3.14 free-threading 在 Windows 上为 Phase II 正式支持
2. **性能开销**：单线程性能损耗约 7-10%，内存开销约 15-20%
3. **C 扩展兼容性**：部分包可能无 cp314t Windows wheels，pip 会从源码编译；不兼容的包会自动回退到 GIL 模式
4. **环境变量**：`Py_GIL_DISABLED=1` 必须在系统级别设置，不能仅在用户 profile 中设置
