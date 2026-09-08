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

## 构建架构与运行时层

Containerfile 采用「3 阶段运行时链 + toolbox-builder aux 阶段」的多阶段构建（dockerfile-runtime-logical-layering 模式），final 阶段内再按变化频率从低到高组织运行时层：

| 阶段 | 基础镜像 | 职责 | 是否进 final |
|------|---------|------|------------|
| Stage 1/3 `base-runtime` | ubuntu:26.04 | 系统包 + locale/tz + Podman（strip） | 是（final 继承的基础层） |
| Stage (aux) `toolbox-builder` | golang:1.26-bookworm | 独立 Go 构建 toolbox 二进制 | 仅二进制经 `COPY --from` 进入 |
| Stage 2/3 `conda-builder` | ubuntu:26.04 | 构建 /opt/conda（main env + ML/编排工具 + 深度清理） | 仅 `/opt/conda` 经 `COPY --from` 进入 |
| Stage 3/3 `final` | base-runtime | 运行时镜像组装 + 用户/配置 + 最终验证 | 最终镜像 |

### Stage (aux): toolbox-builder（内嵌 toolbox 二进制构建，不进 final）
- 基础镜像 `golang:1.26-bookworm`：glibc 2.36 ≤ final ubuntu:26.04（二进制向下兼容）；官方镜像自带 gcc/libc6-dev/make（cgo 就绪）
- 额外安装 `libsubid-dev`：提供 shadow/subid.h 头文件，供 toolbox 的 cgo subid wrapper 编译（libsubid 运行时 dlopen 懒加载，不静态链接）
- `COPY upstream/toolbox/src` 后执行 `go build -trimpath -buildvcs=false -ldflags "-s -w"`，产物 `/out/toolbox`（`-X` 注入版本 0.3），随后清理 Go module/构建缓存与源树
- 产物仅由 final 阶段 `COPY --from=toolbox-builder /out/toolbox /usr/local/bin/toolbox`（chmod 755）；Go 工具链、源树、libsubid-dev 均不进入最终镜像

### Stage 2/3: conda-builder（构建 /opt/conda，含 podman-py/podman-compose 本地源安装）
- Miniforge3 下载安装 + `.condarc`（official/tuna/aliyun）+ libmamba solver + anaconda-anon-usage 移除
- `mamba create` main env：Python 3.14 cp314t (free-threading) + JupyterLab ≥4.4 + Notebook ≥7.3 + ipykernel/ipywidgets，mamba 单次 solve
- pip 安装 omlmd + olot[oras-py]（`--ignore-requires-python` 兼容 cp314t）
- **podman-py/podman-compose 本地源安装段**：构建前置 stage 机制已将 `upstream/podman-py`、`upstream/podman-compose`（SpecWeave 根 `vendor/` 三个 third_party 子模块的源树快照，见 [17-upstream-tools.md](../../docs/17-upstream-tools.md)）放入构建上下文；`COPY` 后 pip 装入 main env（运行时依赖经 pip 拉取），cp314t 下直装失败时降级为 mamba 装 pyyaml/python-dotenv/requests/urllib3 + `pip --no-deps`；源树与 pip 日志安装后即删除
- 深度清理：tk/tcl、nbclassic、test 目录、`conda clean -a`、全量 strip、.pyc；free-threading 验证：`sysconfig.get_config_var('Py_GIL_DISABLED') == 1`
- 本阶段层不进入 final，仅 `/opt/conda` 经 `COPY --from=conda-builder /opt/conda` 进入

### Stage 3/3: final 运行时分层（按变化频率从低到高）

#### Layer 1/5: 系统层（继承 base-runtime，变化频率：最低）
- ubuntu:26.04 基础 + openssh-server/supervisor/podman/crun/conmon/uidmap/fuse-overlayfs/slirp4netns/passt/libcap2-bin(capsh)/tini 等系统包
- zh_CN.UTF-8 locale 生成 + Asia/Shanghai 时区
- Toolbx LABELs: `com.github.containers.toolbox=true`
- Podman 二进制 strip + APT 清理

#### Layer 2/5: COPY builder 产物（变化频率：低）
- `COPY --from=conda-builder /opt/conda /opt/conda`
- `COPY --from=toolbox-builder /out/toolbox /usr/local/bin/toolbox`（chmod 755 + `command -v toolbox` 确认在 PATH）

#### Layer 3/5: 用户 + subuid/subgid + Podman 配置 + Toolbx markers（变化频率：中）
- devuser(UID 1000) 创建 + docker 组；subuid/subgid：`devuser:100000:65536`
- /workspace 等目录与权限；/etc/profile.d/conda-init.sh + devuser .bashrc；/etc/environment PATH
- containers.conf.d/rootless.conf + user storage.conf（fuse-overlayfs）；sudo NOPASSWD
- Toolbx markers：/run/host 预创建 + /run/.toolboxenv + /run/.containerenv；capsh 验证

#### Layer 4/5: 配置文件 COPY + 权限 + 语法验证（变化频率：高）
- sshd_config、supervisord.conf、supervisor/conf.d/、jupyter_notebook_config.py（root+devuser）、containers/storage.conf、entrypoint.sh、healthcheck.sh、olot_car.py
- CRLF→LF 转换（跨平台兼容）+ 执行权限
- 6 项 [VALIDATE] 检查：`sshd -t`、`bash -n entrypoint.sh`、`bash -n healthcheck.sh`、`py_compile olot_car.py`、supervisord.conf 存在性、jupyter allow_hidden 配置

#### Layer 5/5: 最终元数据 + 清理 + 验证（变化频率：最低）
- build-info 写入（/etc/jupyter-podman-build-info）+ apt//tmp 清理
- **最终验证块共 23 项 [OK] 检查**（tini/supervisord/sshd/python/pip/conda/jupyter/omlmd/olot/olot_car.py/Toolbx markers/capsh/podman/crun/pasta/entrypoint.sh/healthcheck.sh/free-threading 等），其中**新增三项内嵌工具检查**：
  - `podman-compose --version`（main env）
  - `python -c "import podman"`（podman SDK / podman-py 可导入）
  - `toolbox --help`（/usr/local/bin/toolbox）
- Free-threading 二次确认 + 构建耗时汇总表输出

#### 运行时声明（元数据，不产生镜像层）
- WORKDIR /workspace + VOLUME
- EXPOSE 22 8888
- HEALTHCHECK（30秒间隔）
- ENTRYPOINT/CMD 执行

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
- [ ] 最终验证 23 项 [OK] 检查全部通过（含三项内嵌工具检查：`podman-compose --version`、`python -c "import podman"`、`toolbox --help`）
- [ ] 构建上下文 `upstream/` 已由 stage 机制生成（git-ignored，.containerignore 放行其根 README.md），避免误删/误提交
