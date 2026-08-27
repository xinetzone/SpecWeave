---
id: "jupyter-containerfile-rules"
title: "Containerfile 编写规范"
source: "AGENTS.md#核心约束 + README.md#镜像架构"
---
# Containerfile 编写规范（jupyter-podman-rootless）

## 基础约定

- 文件名为 `Containerfile`（Podman标准命名）
- 基础镜像：`ubuntu:26.04`（固定版本，不使用`latest`）
- Python版本：`3.14`，构建类型：`cp314t`（free-threading，无GIL）
- Python发行版：Miniforge3 (conda-forge)，使用libmamba solver
- 构建注释/日志使用**英文**（避免编码问题）
- 启用 `SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]`，管道中任何命令失败立即终止
- 非root用户：`devuser` (UID 1000)，sudo默认关闭（GRANT_SUDO=yes启用）
- 中文环境：`zh_CN.UTF-8` locale + `Asia/Shanghai` 时区

## 7层构建设计

按变化频率从低到高组织7层：

### Layer 1/7: 系统包 + locale + Podman + Toolbx依赖（变化频率：最低）
- ubuntu:26.04基础
- openssh-server, supervisor, podman/crun, libcap2-bin(capsh)
- fuse-overlayfs, slirp4netns, tini
- zh_CN.UTF-8 locale生成 + Asia/Shanghai时区
- Toolbx LABELs: `com.github.containers.toolbox=true`
- Podman二进制strip
- APT清理

### Layer 2/7: Miniforge3安装 + .condarc（变化频率：低）
- 架构自动检测(x86_64/aarch64)
- Miniforge3安装 + libmamba solver配置
- 镜像源回退机制（official/tuna/aliyun）
- 二进制strip + anaconda-anon-usage移除
- 权限设置

### Layer 3/7: main conda环境 + ML工具（变化频率：中）
- Python 3.14 cp314t (free-threading)
- JupyterLab ≥4.4 + Notebook ≥7.3
- ipykernel, ipywidgets
- omlmd + olot[oras-py]（ML模型OCI工具，--ignore-requires-python兼容cp314t）
- mamba单次solve
- tk/tcl清理
- free-threading验证：`sysconfig.get_config_var('Py_GIL_DISABLED') == 1`

### Layer 4/7: 用户创建 + subuid/subgid + Podman配置 + Toolbx markers
- devuser(UID 1000)创建 + docker组
- subuid/subgid配置：`devuser:100000:65536`
- fuse-overlayfs storage.conf配置
- sudo NOPASSWD配置（GRANT_SUDO控制）
- /run/host目录预创建（Toolbx bind-mount点）
- /.toolboxenv + /.containerenv marker文件
- capsh工具验证

### Layer 5/7: 配置文件COPY + 权限 + 语法验证（变化频率：高）
- sshd_config, supervisord.conf, jupyter_config
- entrypoint.sh复制 + 执行权限
- CRLF→LF转换（跨平台兼容）
- 4项语法检查：`sshd -t`, `bash -n entrypoint.sh`, supervisord配置验证, jupyter配置验证

### Layer 6/7: 最终元数据 + 清理 + 验证（变化频率：最低）
- build-info写入（构建时间、版本、镜像源）
- apt清理 + /tmp清理
- 15项二进制验证（python, pip, conda, jupyter, sshd, podman, crun, capsh, tini, omlmd, olot等）
- Toolbx markers检查
- Free-threading二次确认
- 构建耗时汇总表输出

### Layer 7/7: 运行时声明（元数据）
- WORKDIR /workspace
- EXPOSE 22 8888
- HEALTHCHECK配置（30秒间隔）
- CMD执行

## 层缓存优化

- 使用BuildKit `--mount=type=cache`挂载apt/conda/pip缓存，加速重复构建
- 先安装不常变化的系统包和conda环境，再复制经常变化的配置文件
- 多个RUN指令合并为一个（用`&& \`连接），减少镜像层数
- apt-get update和install在同一个RUN中，避免缓存过期

## Toolbx兼容规范

镜像必须满足以下Toolbx自定义镜像规范：

| 兼容项 | 实现要求 |
|--------|---------|
| LABEL标记 | `com.github.containers.toolbox=true` |
| /run/host挂载点 | 预创建空目录 |
| Marker文件 | `/run/.toolboxenv` + `/run/.containerenv` |
| capsh工具 | libcap2-bin包提供 |
| sudo NOPASSWD | devuser无密码sudo（GRANT_SUDO=yes时启用） |
| UID匹配 | devuser固定UID 1000（与Linux主机默认用户UID一致） |

## Rootless Podman配置

容器内预装rootless Podman环境，devuser可在容器内运行容器（DinP模式）：

- 存储驱动：fuse-overlayfs（需要宿主机传`--device /dev/fuse`）
- 运行时：crun
- Cgroup管理器：cgroupfs
- subuid/subgid：`devuser:100000:65536`
- 安全选项：`--security-opt label=disable`（禁用SELinux标签，避免FUSE权限问题）
- Cgroup命名空间：`--cgroupns=host`

## 安全规范

- 禁止在Containerfile中硬编码密码、密钥、token
- 敏感信息通过环境变量（-e）或build-arg传入
- SSH主机密钥在容器启动时生成，不打包到镜像中
- 所有透传配置均为opt-in，默认保持隔离
- SSH keys/gitconfig默认只读挂载

## 中文环境配置

```dockerfile
ENV TZ=Asia/Shanghai
ENV LANG=zh_CN.UTF-8
ENV LANGUAGE=zh_CN:zh
ENV LC_ALL=zh_CN.UTF-8

RUN sed -i 's/^# *zh_CN.UTF-8 UTF-8/zh_CN.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen zh_CN.UTF-8 && \
    update-locale LANG=zh_CN.UTF-8 && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone
```

## 体积优化

- 每个apt-get install后立即执行`rm -rf /var/lib/apt/lists/*`
- 使用`--no-install-recommends`减少不必要的依赖
- conda/pip安装后清理缓存
- 二进制文件strip（Podman/conda等）
- 移除tk/tcl等GUI依赖

## 验证清单

构建后必须验证：
- [ ] `podman build`无错误，构建日志有清晰的Layer标记和耗时汇总
- [ ] 镜像中`locale -a`显示zh_CN.UTF-8
- [ ] 镜像中`date`显示Asia/Shanghai时区
- [ ] `id devuser`显示uid=1000，groups包含docker
- [ ] `python -c "import sysconfig; assert sysconfig.get_config_var('Py_GIL_DISABLED') == 1"`通过（free-threading）
- [ ] Podman在devuser下可运行：`su - devuser -c "podman info"`
- [ ] Toolbx markers存在：`test -f /run/.toolboxenv && test -f /run/.containerenv`
- [ ] capsh可用：`capsh --print`
- [ ] 15项核心二进制文件存在且可执行
