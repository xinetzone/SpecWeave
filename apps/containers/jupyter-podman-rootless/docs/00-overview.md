---
id: "jupyter-features-overview"
title: "特性一览"
source: "README.md#特性一览"
---
# 特性一览

| 特性 | 说明 |
|------|------|
| **基础镜像** | Ubuntu 26.04 |
| **Python** | 3.14 cp314t (free-threading，无GIL)，Miniforge3 + libmamba solver |
| **Jupyter** | JupyterLab ≥4.4 + Notebook ≥7.3，端口 8888 |
| **SSH** | OpenSSH Server，端口 22，支持密码/公钥认证 |
| **Podman** | Rootless 模式（fuse-overlayfs + crun），容器内可运行容器（DinP） |
| **服务管理** | supervisord 管理 sshd + jupyter，tini 作为 PID 1 |
| **非root用户** | devuser (UID 1000)，sudo 默认关闭（`--grant-sudo`/`GRANT_SUDO=yes` 开启） |
| **中文环境** | zh_CN.UTF-8 locale + Asia/Shanghai 时区 |
| **镜像源** | APT/Conda/PIP 均支持 official / tuna / aliyun |
| **构建优化** | 7层镜像分层（按变化频率），内置计时器 + 语法验证 |
| **运行时检测** | 自动检测 podman/docker，WSL2 路径自动转换 |
| **编排方式** | 三层后端自动降级：podman-compose 声明式（优先）→ podman-py SDK → CLI；也可直接使用 `podman-compose up -d` |
| **配置管理** | `.env` 环境变量文件 + `compose.yaml` 标准声明式配置，自动生成密码/token |
| **ML 模型分发** | OMLMD 集成：`model.push`/`model.pull`/`model.config` 实现 OCI artifact 版本化模型管理 |
| **ModelCar 打包** | OLOT 集成：`model.pack`/`model.extract` 遵循 KServe ModelCar 标准，模型作为 OCI 镜像层分发 |
| **模型仓库** | 内置 `model-registry` 服务（compose profile: `registry`），本地 OCI 仓库用于开发测试 |
| **Toolbx 兼容** | 镜像满足 Toolbx 规范（LABEL + /run/host + markers + capsh），可直接 `toolbox create/enter` |
| **开发透传** | `compose.dev.yaml` 覆盖文件：一键透传 SSH agent、git config、SSH keys、X11 GUI、pip cache（opt-in） |
