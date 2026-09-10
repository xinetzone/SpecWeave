---
id: "jupyter-build-test-rules"
title: "构建与测试规范"
source: "README.md#快速开始 + README.md#常见问题"
---

# 构建与测试规范（jupyter-podman-rootless）

## 前置条件

### 宿主机要求

- **容器运行时**：Podman（推荐，≥4.0）或 Docker（≥20.10）
- **Python**：≥3.14（用于运行invoke任务）
- **Linux宿主机**：需要FUSE支持（fuse-overlayfs需要）
- **WSL2**：自动路径转换支持
- **可选依赖（宿主机 invoke 三层后端用，pip 安装）**：
  - `podman-compose`（推荐，声明式编排）：`pip install podman-compose`
  - `podman-py`（SDK后端）：`pip install podman`
  - `omlmd` + `olot[oras-py]`（宿主机ML命令）：`pip install omlmd 'olot[oras-py]'`
  - 注：这三个工具与镜像内嵌的同名工具相互独立、版本各自固定（内嵌见 [17-upstream-tools.md](../../docs/17-upstream-tools.md)），互不影响

### 上游源树要求（构建内嵌编排工具的前提）

- Containerfile 在构建时引用 `upstream/{podman-compose,podman-py,toolbox}` 源树（conda-builder 本地 pip 安装、toolbox-builder go build），它们来自 SpecWeave 根工作区 `vendor/` 下的三个 third_party git submodule（固定 pin commit）
- **构建前必须先初始化并 pin 这三个 submodule**（在 SpecWeave 根目录执行）：

```bash
git submodule update --init vendor/podman-compose vendor/podman-py vendor/toolbox
```

- 未初始化时构建前置 stage 会报错并提示该命令；submodule 请保持 gitlink pin（勿随意切分支/改 commit）

## 构建镜像

### 使用invoke构建（推荐）

```bash
# 基础构建
invoke build

# 使用国内镜像源加速
invoke build --apt-mirror tuna --conda-mirror tuna --pip-mirror tuna

# 阿里云镜像源
invoke build --apt-mirror aliyun --conda-mirror aliyun --pip-mirror aliyun

# 不使用缓存（完全重新构建）
invoke build --no-cache

# 自定义标签
invoke build --tag my-jupyter:v1
```

> **构建前自动 stage 上游源树**：`invoke build`（src/jpman_builder/tasks/build.py）与 `jpman rebuild`/`jpman rebuild-all`（bin/jpman）在真正构建前都会先执行 stage 机制（`stage_upstream_sources`），把 SpecWeave 根 `vendor/` 下 podman-compose/podman-py/toolbox 三个 submodule 源树复制到 `<应用根>/upstream/<name>`（git-ignored 的构建上下文临时目录，机制详见 [17-upstream-tools.md](../../docs/17-upstream-tools.md)）。源树缺失（submodule 未 init）时构建会报错并给出修复命令，不会静默构建出缺工具的镜像。

build参数：

| 参数               | 默认值                              | 说明                            |
| ---------------- | -------------------------------- | ----------------------------- |
| `--tag`          | `jupyter-podman-rootless:latest` | 镜像标签                          |
| `--apt-mirror`   | `official`                       | APT镜像源：official/tuna/aliyun   |
| `--conda-mirror` | `official`                       | Conda镜像源：official/tuna/aliyun |
| `--pip-mirror`   | `official`                       | PIP镜像源：official/tuna/aliyun   |
| `--no-cache`     | `false`                          | 不使用构建缓存                       |

### 直接使用Podman/Docker构建

```bash
# Podman
podman build -t jupyter-podman-rootless \
  --build-arg APT_MIRROR=tuna \
  --build-arg CONDA_MIRROR=tuna \
  --build-arg PIP_MIRROR=tuna \
  .

# Docker（兼容）
docker build -t jupyter-podman-rootless \
  --build-arg APT_MIRROR=tuna \
  --build-arg CONDA_MIRROR=tuna \
  --build-arg PIP_MIRROR=tuna \
  .
```

> ⚠️ 直接 `podman build`/`docker build` **不会**自动 stage 上游源树：若 `<应用根>/upstream/` 尚不存在或已过期，`COPY upstream/...` 会失败或装入旧源。请先运行一次 `invoke build`（或 `jpman rebuild`/`rebuild-all`）生成/刷新 `upstream/`，再直接构建；否则请优先使用上述会自动 stage 的构建入口。

构建时环境变量（--build-arg）：

| 变量              | 默认值      | 说明                                                |
| --------------- | -------- | ------------------------------------------------- |
| APT\_MIRROR     | official | APT镜像源                                            |
| CONDA\_MIRROR   | official | Conda镜像源                                          |
| PIP\_MIRROR     | official | PIP镜像源                                            |
| PYTHON\_VERSION | 3.14     | Python版本                                          |
| PYTHON\_BUILD   | cp314t   | Python构建类型（cp314t = free-threading，cp314 = 标准GIL） |

## 运行容器

### 使用invoke运行（推荐）

```bash
# 默认启动（自动生成密码和token，端口2222:22, 8888:8888）
invoke run

# 授予sudo权限
invoke run --grant-sudo

# 自定义端口
invoke run --ssh-port 2222 --jupyter-port 8889

# 设置自定义密码/token
invoke run --user-password mypassword --jupyter-token mytoken

# 注入SSH公钥
invoke run --ssh-public-key "$(cat ~/.ssh/id_ed25519.pub)"

# 前台运行（不后台）
invoke run --no-detach

# 指定工作目录挂载
invoke run --workspace /path/to/your/project
```

run参数：

| 参数                     | 默认值                              | 说明               |
| ---------------------- | -------------------------------- | ---------------- |
| `--name`               | `jupyter-podman`                 | 容器名              |
| `--tag`                | `jupyter-podman-rootless:latest` | 使用的镜像            |
| `--ssh-port`           | `2222`                           | SSH映射端口          |
| `--jupyter-port`       | `8888`                           | Jupyter映射端口      |
| `--workspace`          | `./workspace`                    | 工作目录挂载路径         |
| `--user-password`      | 自动生成16位                          | devuser密码        |
| `--jupyter-token`      | 自动生成32位                          | Jupyter访问token   |
| `--ssh-public-key`     | 无                                | SSH公钥内容          |
| `--grant-sudo`         | `false`                          | 授予devuser无密码sudo |
| `--detach/--no-detach` | `detach`                         | 后台/前台运行          |

### 直接使用Podman/Docker运行

```bash
podman run -d \
  --name jupyter-podman \
  --device /dev/fuse \
  --security-opt label=disable \
  --cgroupns=host \
  -p 2222:22 \
  -p 8888:8888 \
  -v ./workspace:/workspace \
  -e USER_PASSWORD=yourpassword \
  -e JUPYTER_TOKEN=yourtoken \
  jupyter-podman-rootless
```

关键参数（必须）：

- `--device /dev/fuse`：fuse-overlayfs需要
- `--security-opt label=disable`：禁用SELinux标签
- `--cgroupns=host`：rootless Podman需要

### 调试模式（不启动服务，直接进入bash）

```bash
podman run -it --rm \
  --device /dev/fuse \
  --security-opt label=disable \
  jupyter-podman-rootless bash
```

## 容器交互

```bash
# 查看容器状态
invoke status

# 查看日志
invoke logs
invoke logs --follow --tail 50

# 进入容器shell（默认devuser）
invoke shell

# 以root进入
invoke shell --user root

# 在容器中执行命令
invoke exec --command "python --version"
invoke exec --command "pip list | grep jupyter"

# SSH方式进入
ssh -p 2222 devuser@localhost
```

## 停止与清理

```bash
# 停止并删除容器
invoke stop

# 清理（删除容器）
invoke clean

# 清理并删除镜像
invoke clean --image

# 清理未使用的卷
invoke clean --volume
```

## 7步验证流程（构建后必做）

构建完成后，执行以下验证确保镜像正常工作：

### 1. 基础系统验证

```bash
# 进入容器
invoke shell

# 验证locale
locale -a | grep zh_CN.UTF-8
date  # 应显示Asia/Shanghai时区

# 验证用户
id devuser  # uid=1000，groups包含docker
whoami  # 默认devuser
```

### 2. Python验证

```bash
# 验证Python版本和free-threading
python --version  # Python 3.14.x
python -c "import sysconfig; assert sysconfig.get_config_var('Py_GIL_DISABLED') == 1; print('Free-threading OK')"
python -c "import sys; assert not sys._is_gil_enabled(); print('GIL disabled OK')"

# 验证conda
conda --version
which python  # 应在/opt/conda/bin/python
```

### 3. Jupyter验证

```bash
# 验证Jupyter安装
jupyter lab --version
jupyter notebook --version

# 验证Jupyter可访问（宿主机执行）
curl -s http://localhost:8888/api | head -c 100
```

### 4. SSH验证

```bash
# 容器内验证sshd
pgrep sshd
sshd -t  # 配置语法检查

# 宿主机SSH连接
ssh -p 2222 devuser@localhost "echo SSH OK"
```

### 5. Podman验证

```bash
# 容器内验证Podman（devuser下）
podman --version
podman info
podman run --rm docker.io/library/hello-world

# 容器内验证内嵌编排工具（镜像内置，版本固定自 vendor/ 子模块，详见 docs/17-upstream-tools.md）
podman-compose --version                      # podman-compose（main env，本地源 pip 安装）
python -c "import podman; print('[OK] podman SDK importable')"   # podman-py SDK（main env）
toolbox --version                             # toolbox 二进制活性（/usr/local/bin，golang aux 阶段构建；容器内裸跑需宿主 Toolbx 启动器）
```

### 6. ML工具验证

```bash
# 容器内验证OMLMD/OLOT
omlmd --version
olot --version
```

### 7. 健康检查验证

```bash
# 手动执行健康检查
podman exec jupyter-podman /usr/local/bin/healthcheck.sh
echo $?  # 应返回0

# 查看健康状态
podman healthcheck run jupyter-podman
```

## 常见问题排查

### Q: 构建时下载Miniforge很慢？

使用国内镜像源构建：

```bash
invoke build --conda-mirror tuna --apt-mirror tuna --pip-mirror tuna
```

### Q: Podman报错"fuse: device not found"？

运行容器时必须添加`--device /dev/fuse`参数。invoke的`run`命令已自动添加。直接使用podman run时需要手动添加。

### Q: WSL2下挂载路径不对？

invoke的`utils.to_posix_path()`会自动将Windows路径（如`D:\project`）转换为WSL2路径（`/mnt/d/project`）。直接使用podman命令时需手动转换。

### Q: 如何在容器中使用sudo？

启动时添加`--grant-sudo`参数：

```bash
invoke run --grant-sudo
```

### Q: 如何设置SSH公钥登录？

```bash
invoke run --ssh-public-key "$(cat ~/.ssh/id_ed25519.pub)"
```

### Q: 容器内的Podman无法拉取镜像？

确保宿主机已配置`--device /dev/fuse`和`--security-opt label=disable`。某些环境可能需要`--cgroupns=host`。

### Q: 如何使用开发透传模式（SSH agent/GUI）？

使用`compose.dev.yaml`覆盖文件：

```bash
podman-compose -f compose.yaml -f compose.dev.yaml up -d
```

### Q: 如何启动本地模型仓库？

```bash
podman-compose --profile registry up -d
```

然后使用`localhost:5000`作为OMLMD/OLOT的registry地址。

### Q: model.push/pack报错omlmd/olot未安装？

omlmd和olot已预装在容器镜像内。如果通过invoke调用宿主机Python直接执行，需要安装：

```bash
pip install omlmd 'olot[oras-py]'
# 或
pip install -e ".[model]"
```

### Q: compose.dev.yaml中的透传安全吗？

所有透传均为opt-in（默认不启用）。SSH keys和gitconfig以只读方式挂载，/run/host逃生口默认关闭。

### Q: 构建报错"上游源树缺失或为空"或找不到 upstream/？

说明 SpecWeave 根 `vendor/` 下三个 submodule 未初始化或未 pin。在 SpecWeave 根目录执行：

```bash
git submodule update --init vendor/podman-compose vendor/podman-py vendor/toolbox
```

然后重新 `invoke build`（或 `jpman rebuild`/`rebuild-all`）；构建前置 stage 会自动重建 `<应用根>/upstream/`。

### Q: 容器内 podman-compose / podman SDK / toolbox 不可用或版本不对？

- `upstream/` 是构建前由 stage 机制临时生成的构建上下文目录，**已被 `.gitignore` 忽略**，且每次构建前清空重建——不要手动向其中添加文件、也不要将其提交入库
- `.containerignore` 的 `*.md` 规则对 `upstream/` 内层的根 README.md 做了**反白放行**（`!upstream/podman-compose/README.md`、`!upstream/podman-py/README.md`）——本地 pip 构建需要其作为 long_description 元数据，**不要删除这两条放行规则**
- 若镜像仍是旧版本，先确认三 submodule 已 pin 到目标 commit（`git submodule status vendor/podman-compose vendor/podman-py vendor/toolbox`），再 `jpman rebuild-all` 全量重建并重跑三项内嵌工具检查（`podman-compose --version` / `python -c "import podman"` / `toolbox --version`）

## 验证清单

构建测试完成后必须确认：

- [ ] `invoke build`构建成功，构建日志清晰（3 阶段 + toolbox-builder aux 阶段，final 内 5 层运行时分层）
- [ ] 构建前 `upstream/` 已被 stage 到 `<应用根>/upstream/`（含 podman-compose/podman-py/toolbox 三个源树）
- [ ] 容器内三项内嵌工具检查通过：`podman-compose --version`、`python -c "import podman"`、`toolbox --version`（toolbox 仅验二进制活性，容器内裸跑需宿主 Toolbx 启动器）
- [ ] `invoke run`启动成功，打印SSH/Jupyter访问信息
- [ ] SSH可连接（密码或公钥认证）
- [ ] Jupyter Lab可在浏览器访问
- [ ] devuser下`podman info`正常，可运行hello-world
- [ ] Python free-threading验证通过
- [ ] `invoke status`显示容器运行中
- [ ] `invoke logs`可查看日志
- [ ] `invoke shell`可进入容器
- [ ] `invoke exec`可执行命令
- [ ] `invoke stop`可停止容器
- [ ] `invoke clean --image`可清理资源
- [ ] 健康检查通过
- [ ] 国内镜像源构建正常（tuna/aliyun）
- [ ] WSL2路径自动转换工作正常

