# Conda 变体 Dockerfile 规范

## 基础信息

- **基础镜像**：`devcontainer-base:${BASE_TAG}`（默认为 `devcontainer-base:latest`）
- **Dockerfile 语法版本**：`# syntax=docker/dockerfile:1.7-labs`
- **Miniconda 安装路径**：固定为 `/opt/conda`
- **SHELL 指令**：`["/bin/bash", "-e", "-o", "pipefail", "-c"]`（显式声明，不依赖继承）

## 核心约束

### 1. PATH 优先级（强制执行）

- **不修改**系统默认 `PATH` 环境变量
- `/opt/venv/bin` 必须保持在 conda 之前（实际上 `/opt/conda/bin` 不加入默认 PATH）
- 系统服务（Jupyter、supervisord、SSH 等）始终使用 `/opt/venv` 中的 Python
- Conda 仅通过 `source /etc/profile.d/conda-init.sh` 手动激活

### 2. 不自动激活 Conda

- `auto_activate_base` 必须设置为 `false`（系统级）
- 不在 `/etc/profile.d/` 中自动 source conda.sh
- 用户 `.bashrc` 中 conda 相关行默认**注释掉**，仅提供使用示例
- 不修改 `/etc/environment` 中的 PATH

### 3. 继承基础镜像设置（禁止覆盖）

以下指令由基础镜像设置，**不得在变体 Dockerfile 中重新定义**：

- `ENTRYPOINT`（保持 `/usr/bin/tini -- /usr/local/bin/entrypoint.sh`）
- `CMD`（保持 `[]`）
- `USER`（构建过程用 root，最终用户由基础镜像决定）
- `WORKDIR`（保持 `/workspace`）
- `HEALTHCHECK`（保持基础镜像的健康检查）
- `EXPOSE`、`VOLUME`（保持基础镜像声明）

### 4. 激活脚本

- 路径：`/etc/profile.d/conda-init.sh`
- 权限：`chmod +x`
- 功能：source `/opt/conda/etc/profile.d/conda.sh`，**不自动 activate base**
- 使用方式：用户手动执行 `source /etc/profile.d/conda-init.sh && conda activate base`

## 追加层 5 阶段结构

Conda 变体在基础镜像的 7 个阶段之上，追加 5 个阶段（编号 VS1-VS5）：

### Stage 1/5：系统包检查 + 计时器初始化

- 检查 `wget`、`curl`、`bzip2`、`ca-certificates` 是否已安装（基础镜像通常已有）
- 仅在缺失时安装，使用 `--no-install-recommends`
- 支持 `APT_MIRROR` 参数配置 APT 源
- 初始化追加层计时器：`/tmp/.variant-build-timer`
- 验证基础镜像关键组件存在（devuser、/opt/venv、python）
- 输出 `[TIMER]`

### Stage 2/5：Miniconda3 安装

- 安装路径：`/opt/conda`（`CONDA_DIR`）
- 安装方式：`bash miniconda.sh -b -p /opt/conda`（批处理模式，无交互）
- 支持 `MINICONDA_VERSION` 参数（默认 `latest`）
- 支持架构检测：`x86_64` 和 `aarch64`
- 支持 `CONDA_MIRROR` 参数：
  - `tuna`：从 `mirrors.tuna.tsinghua.edu.cn` 下载
  - `official`：从 `repo.anaconda.com` 下载
- 安装后执行：
  - `conda config --system --set auto_activate_base false`
  - `conda install -y -n base python=${PYTHON_VERSION}`（设置 base 环境 Python 版本）
- 验证：`/opt/conda/bin/conda --version`
- 清理：删除安装脚本 `/tmp/miniconda.sh`
- 输出 `[TIMER]`

### Stage 3/5：镜像源配置

- Conda 源：写入 `${CONDA_DIR}/.condarc`（系统级）
  - `tuna`：配置清华 TUNA 镜像（default_channels + custom_channels/conda-forge）
  - `official`：默认 channels（conda-forge, defaults）
  - 包含 `auto_activate_base: false`
- Pip 源：
  - 写入 `/root/.config/pip/pip.conf`
  - 复制到 `/home/devuser/.config/pip/pip.conf`
  - 支持 `PIP_MIRROR`：`aliyun`/`tuna`/`official`
  - 同时配置 conda base 环境的 pip：`/opt/conda/bin/pip config set`
- 验证：`conda config --show-sources`
- 输出 `[TIMER]`

### Stage 4/5：激活脚本 + 权限配置

- 创建 `/etc/profile.d/conda-init.sh`（使用 heredoc 确保内容正确）
  - 检测 `/opt/conda/etc/profile.d/conda.sh` 是否存在
  - source conda.sh，**不执行 conda activate**
  - 错误处理：找不到时输出 WARN 到 stderr
- 更新 `/home/devuser/.bashrc`：
  - 追加 conda 使用说明注释块
  - 提供 `source /etc/profile.d/conda-init.sh` 和 `conda activate base` 示例（注释状态）
- 更新 `/root/.bashrc`：类似配置
- 设置 `/opt/conda` 权限：
  - `chown -R root:root /opt/conda`
  - `chmod -R a+rX /opt/conda`
  - 目录权限 `755`
- 验证 PATH 优先级：
  - `which python` 必须指向 `/opt/venv/bin/python`
  - 默认 python 是系统 venv 的，不是 conda 的
- 验证激活脚本可用：`bash -c 'source /etc/profile.d/conda-init.sh && conda --version'`
- 恢复 devuser 对 `.bashrc` 和 `pip.conf` 的所有权
- 输出 `[TIMER]`

### Stage 5/5：构建元数据 + 清理 + 最终验证

- 写入构建信息：`/etc/devcontainer-variant-conda-build-info`
  - 包含：BUILD_DATE、VARIANT、BASE_IMAGE、MINICONDA_VERSION、CONDA_VERSION、PYTHON_VERSION、CONDA_DIR、镜像源配置、PATH_PRIORITY 等
- 清理：
  - `conda clean -ya`
  - `pip cache purge`（venv 的 pip）
  - `apt-get clean`
  - 删除 `/tmp/*`、`/var/tmp/*`、`/var/lib/apt/lists/*`
- **[VALIDATION CHECKPOINT]** 语法 + 可用性验证（7项）：
  1. `bash -n /etc/profile.d/conda-init.sh`（脚本语法）
  2. `/opt/conda/bin/conda` 可执行
  3. `/opt/venv` 存在且有 python
  4. 默认 python 来自 `/opt/venv/bin/python`（PATH 优先级正确）
  5. Jupyter 仍可通过 venv 使用
  6. docker、supervisord 仍存在（服务未被破坏）
  7. devuser 可读取/执行 conda
- **[FINAL VERIFICATION]** 登录 shell 激活测试：
  - `bash -l -c 'source /etc/profile.d/conda-init.sh && conda activate base && python --version'`
- 输出 **BUILD TIMING SUMMARY** 表格（5个追加阶段的耗时）
- 清理计时器文件
- 输出构建完成提示
- 输出 `[TIMER]`

## 构建参数

| 参数 | 默认值 | 说明 |
|------|-------|------|
| `BASE_TAG` | `latest` | 基础镜像标签 |
| `APT_MIRROR` | `official` | APT 源：official/aliyun/tuna |
| `CONDA_MIRROR` | `tuna` | Conda 源：tuna/official |
| `PIP_MIRROR` | `aliyun` | Pip 源：aliyun/tuna/official |
| `MINICONDA_VERSION` | `latest` | Miniconda 版本 |
| `PYTHON_VERSION` | `3.14` | Base 环境 Python 版本 |

## 服务继承

基础镜像的所有服务在 conda 变体中保持可用：

- **sshd**：SSH 服务（端口 22）
- **dockerd**：Docker DinD（端口 2375）
- **podman**：Podman rootless（按需）
- **jupyter**：Jupyter Notebook/Lab（端口 8888），使用 `/opt/venv` 中的 Python 和 jupyter 包
- **supervisord**：进程管理，配置不变

## 日志/输出规范

- 阶段开始：`echo "########################################################################"` 和 `# [CONDA VARIANT STAGE N/5] ...`
- 动作标记：`[ACTION]`、`[INFO]`、`[OK]`、`[WARN]`、`[ERROR]`
- 计时器：`[TIMER] Stage N/5 (...) took Xs | Variant cumulative: Ys`
- 验证框：使用 `┌─┐││└─┘` 边框绘制 `[VALIDATION CHECKPOINT]`
- 汇总表：使用 `╔═╗║║╠═╣╚═╝` 边框绘制 BUILD TIMING SUMMARY
- 错误处理：`[ERROR]` 后必须 `exit 1`
