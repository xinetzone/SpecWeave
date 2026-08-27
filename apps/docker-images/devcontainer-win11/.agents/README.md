# devcontainer-win11 - AI 资产容器

本目录包含 devcontainer-win11 项目的 AI 协作者规范资产。

## 目录结构

- `rules/` - 项目特有规则
  - [dockerfile.md](rules/dockerfile.md) - Windows Dockerfile 编写规范（含 free-threading 配置）
  - [entrypoint.md](rules/entrypoint.md) - entrypoint.ps1 编写规范
  - [services.md](rules/services.md) - 服务配置规范（sshd/jupyter/docker dood）
  - [build-test.md](rules/build-test.md) - 构建和测试规范

## 核心约束速查

| 约束 | 值 |
|------|-----|
| 基础镜像 | mcr.microsoft.com/windows/servercore:ltsc2022 |
| Python 版本 | 3.14 (cp314t free-threading via conda-forge python-freethreading) |
| Py_GIL_DISABLED | 必须设为 1（Machine 级别系统环境变量） |
| C 编译器 | conda-forge m2w64-toolchain (MinGW-w64 GCC) |
| Docker 模式 | DooD（仅 CLI，通过 npipe:////./pipe/docker_engine 连接宿主） |
| 非管理员用户 | devuser（禁止加入 Administrators 组） |
| Shell | PowerShell 7 (pwsh.exe) |
| 工作目录 | C:\workspace |
| 端口 | SSH 22, Jupyter 8888 |
| 时区 | China Standard Time (UTC+8) |
| 编码 | UTF-8 (chcp 65001) |
| 构建环境 | Windows 宿主 + Docker Desktop Windows 容器模式 |
