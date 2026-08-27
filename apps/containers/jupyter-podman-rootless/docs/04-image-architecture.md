---
id: "jupyter-image-architecture"
title: "镜像架构"
source: "README.md#镜像架构"
---
# 镜像架构

## 7层构建设计（Containerfile）

镜像按变化频率从低到高分为7层，最大化构建缓存复用：

```mermaid
flowchart BT
    L7["Layer 7/7: 运行时声明（元数据）<br/>WORKDIR /workspace | EXPOSE 22 8888<br/>HEALTHCHECK | CMD"]
    L6["Layer 6/7: 最终元数据 + 清理 + 验证（变化频率：最低）<br/>build-info写入 | apt清理 | /tmp清理<br/>15项二进制验证 | Toolbx markers检查<br/>Free-threading二次确认<br/>构建耗时汇总表"]
    L5["Layer 5/7: 配置文件COPY + 权限 + 语法验证（变化频率：高）<br/>sshd_config | supervisord | jupyter_config | entrypoint<br/>CRLF→LF转换 | sshd -t | bash -n<br/>4项语法检查"]
    L4["Layer 4/7: 用户创建 + subuid/subgid + Podman配置 + Toolbx markers<br/>devuser(UID1000) | docker组<br/>subuid:100000:65536<br/>fuse-overlayfs storage.conf<br/>sudo NOPASSWD | /run/host目录<br/>/.toolboxenv+/.containerenv markers"]
    L3["Layer 3/7: main conda环境 + ML工具（变化频率：中）<br/>Python 3.14 cp314t | JupyterLab<br/>ipykernel | ipywidgets | omlmd | olot<br/>mamba单次solve | tk/tcl清理<br/>free-threading验证"]
    L2["Layer 2/7: Miniforge3安装 + .condarc（变化频率：低）<br/>架构自动检测(x86_64/aarch64)<br/>镜像源回退 | libmamba<br/>二进制strip | anaconda-anon-usage移除<br/>权限设置"]
    L1["Layer 1/7: 系统包 + locale + Podman + Toolbx依赖（变化频率：最低）<br/>ubuntu:26.04 | openssh-server<br/>supervisor | podman/crun | libcap2-bin(capsh)<br/>fuse-overlayfs | slirp4netns<br/>tini | zh_CN.UTF-8<br/>Toolbx LABELs | Podman二进制strip | APT清理"]
    L1 --> L2 --> L3 --> L4 --> L5 --> L6 --> L7
```

Containerfile编写规范详见 [.agents/rules/containerfile.md](../.agents/rules/containerfile.md)。

## 7步启动流程（entrypoint.sh）

容器启动时entrypoint.sh按以下7步初始化：

```
print_banner()
  │
  ├─ [1/7] setup_passwords()     → 配置用户密码（支持环境变量/随机生成）
  ├─ [2/7] generate_host_keys()  → 生成 SSH host keys（ed25519 + rsa）
  ├─ [3/7] configure_sshd()      → 配置 sshd（PermitRootLogin 控制）
  ├─ [4/7] setup_podman()        → 初始化 rootless Podman 环境
  │    ├─ /dev/fuse 权限
  │    ├─ ~/.config/containers/ 配置
  │    ├─ XDG_RUNTIME_DIR 设置
  │    └─ podman info 触发初始化
  ├─ [5/7] setup_ssh_keys()      → 注入 SSH 公钥（SSH_PUBLIC_KEY）
  ├─ [6/7] setup_jupyter()       → 生成 Jupyter 运行时配置
  │    ├─ 密码 hash（JUPYTER_PASSWORD）或 token
  │    ├─ 端口/根目录/CORS 配置
  │    └─ 运行时配置写入 jupyter_server_config.d/
  ├─ [7/7] print_access_info()   → 打印访问信息（SSH/Jupyter/Podman/ML工具）
  │
  └─ exec supervisord -n         → 启动 supervisord（sshd + jupyter）
```

Entrypoint编写规范详见 [.agents/rules/entrypoint.md](../.agents/rules/entrypoint.md)。

## 服务管理（supervisord）

通过supervisord管理多个服务，tini作为PID 1处理信号转发：

| 服务 | 用户 | 优先级 | 端口 | 说明 |
|------|------|--------|------|------|
| sshd | root | 100 | 22 | SSH 守护进程 |
| jupyter | root（su到devuser） | 200 | 8888 | Jupyter Lab，工作目录 /workspace |

关键特性：
- `tini` 作为 PID 1 处理信号转发和僵尸进程回收
- `supervisord` nodaemon 模式运行，日志输出到 stdout/stderr
- 服务异常自动重启（autorestart=true，startretries=3）

服务配置规范详见 [.agents/rules/services.md](../.agents/rules/services.md)。

## Compose 服务架构

podman-compose定义两个服务：

| 服务 | Profile | 端口 | 说明 |
|------|---------|------|------|
| `jupyter` | 默认 | 2222:22, 8888:8888 | JupyterLab + SSHd + Podman 主服务 |
| `model-registry` | `registry` | 5000:5000 | 本地 OCI registry（zot 镜像），用于 OMLMD/OLOT 开发测试 |

使用profile控制服务启动：
```bash
# 仅启动jupyter（默认）
podman-compose up -d

# 启动jupyter + model-registry
podman-compose --profile registry up -d
```

Compose编排规范详见 [.agents/rules/compose.md](../.agents/rules/compose.md)。
