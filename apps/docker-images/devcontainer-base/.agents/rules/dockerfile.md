---
id: "devcontainer-dockerfile-rules"
title: "Dockerfile 多阶段构建规范"
source: "AGENTS.md#项目特有约束"
---
# Dockerfile 多阶段构建规范（devcontainer-base）

<a id="基础约定"></a>
## 基础约定

- 文件名为 `Dockerfile`（使用 BuildKit 1.7-labs 语法：`# syntax=docker/dockerfile:1.7-labs`）
- 基础镜像：`ubuntu:26.04`（固定版本，不使用 `latest`）
- 构建注释/日志使用**英文**（避免 PowerShell/Shell 编码问题）
- 每个 Stage/关键步骤输出构建日志：`echo "[BUILD] ..."`
- 启用 `SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]`，管道中任何命令失败立即终止

## 多阶段结构

单 Dockerfile 7 Stage 构建（v2.2+ 架构：Miniforge3 + Python 3.14.6 cp314t 直接集成，无独立 builder stage 复制 venv）：

1. **Stage 1/7**：系统包安装 + APT 镜像源切换 + locale/timezone 配置（变化频率：最低）
2. **Stage 2/7**：Docker CE 安装（变化频率：低）
3. **Stage 3/7**：Podman rootless 安装（变化频率：低）
4. **Stage 4/7**：Miniforge3 安装 + Conda 环境创建（Python 3.14.6 cp314t + libmamba 求解器 + 核心包，变化频率：中）
5. **Stage 5/7**：用户/组 + subuid/subgid + 运行时目录 + daemon.json（变化频率：中）
6. **Stage 6/7**：配置文件 COPY + 权限 + 语法验证（变化频率：高）
7. **Stage 7/7**：build-info + 9步激进清理 + 最终验证（变化频率：最低）

## 层缓存优化

- 使用 BuildKit `--mount=type=cache` 挂载 apt/pip 缓存，跨构建复用：
  ```dockerfile
  RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
      --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
      apt-get update && apt-get install -y --no-install-recommends ...
  ```
- pip 安装同样使用缓存挂载：`--mount=type=cache,target=/root/.cache/pip,sharing=locked`
- Conda 包缓存使用 BuildKit 缓存挂载：`--mount=type=cache,target=/opt/conda/pkgs,sharing=locked`
- libmamba 求解器缓存挂载：`--mount=type=cache,target=/root/.cache/conda,sharing=locked`
- 多个 RUN 指令合并为一个（用 `&& \` 连接），减少镜像层数
- apt-get update 和 install 在同一个 RUN 中，避免缓存过期
- COPY 指令尽量放在靠后阶段，优先复制不常变化的文件
- 变化频率高的配置文件 COPY 集中在 Stage 6，避免前面层缓存失效

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

## 构建计时

每个 Stage 输出 `[TIMER]` 日志：本阶段耗时 + 累计耗时，最终 Stage 7 输出汇总表。
时间戳写入 `/tmp/.build-timer`，格式 `S<N>=<unix-timestamp>`。

## 镜像源切换

通过 `APT_MIRROR` 和 `PIP_MIRROR` 构建参数支持国内镜像：
- `APT_MIRROR=official|aliyun|tuna`（默认 official）
- `PIP_MIRROR=official|aliyun|tuna`（默认 official）
- 镜像源配置在每个阶段的首个 RUN 中完成，条件替换 sources.list 和 pip.conf

<a id="安全规范"></a>
## 安全规范

- 禁止在 Dockerfile 中硬编码密码、密钥、token
- 敏感信息通过环境变量（`-e`）或 build-arg 传入
- SSH 主机密钥在容器启动时生成，不打包到镜像中
- 密码哈希在 entrypoint 运行时动态生成（`chpasswd`）

<a id="体积优化"></a>
## 体积优化

- Runtime 阶段使用 `--no-install-recommends` 减少不必要的依赖
- 单镜像架构：Miniforge3 直接在 Stage 4 安装，无独立 builder stage 复制 venv；Conda 环境即最终运行时环境
- Stage 7 执行 9 步激进清理：
  1. 删除 `/usr/share/doc`、`/usr/share/man`、`/usr/share/info` 文档
  2. 删除所有 `__pycache__` 目录和 `*.pyc`/`*.pyo` 文件
  3. apt 清理：`apt-get clean && rm -rf /var/lib/apt/lists/*`
  4. conda 清理：`conda clean -yafq && conda build purge-all`
  5. pip 安装使用 `--no-cache-dir`
  6. 删除 `/opt/conda/pkgs` 下的 tar 包和缓存
  7. 删除静态库 `*.a`/`*.la`
  8. 对二进制执行 `strip --strip-unneeded`
  9. 清理 `/tmp/*` `/var/tmp/*`
- Docker/Podman 客户端与服务端版本匹配

<a id="非-root-用户规范"></a>
## 非 root 用户规范

- 固定用户名 `devuser`，UID 优先 1000（被占用时自动分配）
- 默认加入 `docker` 组（访问 DinD socket）
- 默认无 sudo 权限，通过 `GRANT_SUDO=yes` 环境变量启用 NOPASSWD sudo
- HOME 目录为 `/home/devuser`
- subuid/subgid 配置为 100000-165535（Podman rootless 所需）
- WORKDIR 设置为 `/workspace`，支持作为其他项目的基础镜像（FROM devcontainer-base）

## 验证清单

- [ ] `bash scripts/build.sh` 无错误，构建日志有清晰的 Stage 标记和 [TIMER] 计时
- [ ] 镜像中 `locale -a` 显示 zh_CN.UTF-8
- [ ] 镜像中 `date` 显示 Asia/Shanghai 时区
- [ ] `id devuser` 显示 uid=1000，groups 包含 docker
- [ ] Conda 环境在 `/opt/conda`，`/opt/conda/bin/python` 可用且为 Python 3.14.6 cp314t（free-threading）
- [ ] Docker CLI 和 Podman CLI 均已安装
- [ ] `dockerd --version` 与 Docker CLI 版本匹配
- [ ] JupyterLab 通过 `/opt/conda/bin/jupyter lab` 启动
