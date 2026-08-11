---
id: "pytorch-dockerfile-rules"
title: "Dockerfile 多阶段构建规范"
source: "AGENTS.md#项目特有约束"
---
# Dockerfile 多阶段构建规范（pytorch-base）

<a id="基础约定"></a>
## 基础约定

- 文件名为 `Dockerfile`，首行声明 BuildKit 语法：`# syntax=docker/dockerfile:1.7-labs`
- 基础镜像：`ubuntu:26.04`（固定版本，通过 `BASE_IMAGE` ARG 可覆盖）
- 构建注释/日志使用**英文**（避免 PowerShell/Shell 编码问题）
- 启用 `SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]`，管道中任何命令失败立即终止
- 结构化日志前缀：`[STAGE]`/`[ACTION]`/`[OK]`/`[WARN]`/`[ERROR]`/`[TIMER]`
- 每个Stage输出 `[TIMER]` 耗时统计，最终Stage输出汇总表

## 构建参数

| ARG | 默认值 | 说明 |
|-----|--------|------|
| BASE_IMAGE | ubuntu:26.04 | 基础镜像 |
| USE_GPU | 0 | 0=CPU版, 1=CUDA版 |
| PYTHON_VERSION | 3.14 | Python版本（3.10-3.14） |
| PYTORCH_VERSION | 2.13.0 | PyTorch版本 |
| CUDA_VERSION | 12.6 | CUDA版本（GPU模式） |
| MINICONDA_VERSION | latest | Miniconda版本 |
| QUIET | 0 | 安静模式 |

## 7阶段结构（Runtime Logical Layering v1.3）

按变化频率从低到高排列，最大化缓存命中率：

1. **Stage 1/7**：系统包 + locale/timezone + APT镜像源配置（变化频率：最低）
2. **Stage 2/7**：Miniconda3 安装到 `/opt/conda`（变化频率：低）
3. **Stage 3/7**：conda + pip 镜像源配置（国内源切换）（变化频率：低）
4. **Stage 4/7**：conda环境创建（pytorch环境）+ PyTorch安装（变化频率：中，主要耗时阶段）
5. **Stage 5/7**：非root用户 `ai`(UID 1000) 创建 + sudo配置 + 权限设置（变化频率：中）
6. **Stage 6/7**：entrypoint安装 + profile.d脚本COPY + 语法验证（变化频率：高）
7. **Stage 7/7**：build-info写入 + 最终验证（torch版本/python版本/conda环境）+ 耗时汇总表（变化频率：最低）

## 层缓存优化

- 使用 BuildKit `--mount=type=cache` 缓存 apt/conda/pip：
  ```dockerfile
  RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
      --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
      apt-get update -qq && apt-get install -y --no-install-recommends -qq ...
  ```
- conda缓存：`--mount=type=cache,target=/opt/conda/pkgs,sharing=locked`
- pip缓存：`--mount=type=cache,target=/root/.cache/pip,sharing=locked`
- 多个RUN指令合并为一个（用 `&& \` 连接），减少镜像层数
- apt-get update 和 install 在同一个RUN中，避免缓存过期
- COPY指令放在靠后阶段

## 中文环境配置

```dockerfile
ENV TZ=Asia/Shanghai
ENV LANG=zh_CN.UTF-8
ENV LANGUAGE=zh_CN:zh
ENV LC_ALL=zh_CN.UTF-8
```

与其他项目一致，使用sed修改locale.gen后生成locale。

## Conda环境规范

- Miniconda安装路径：`/opt/conda`
- 环境名：`pytorch`
- 环境路径：`/opt/conda/envs/pytorch/`
- Python版本：默认3.14（通过PYTHON_VERSION ARG控制）
- 自动激活：通过 `/etc/profile.d/conda.sh` 和 `.bashrc` 实现
- conda安装失败自动fallback到pip（网络容错）

## 离线资源支持

所有离线资源统一存放在 `offline/` 目录（始终包含在构建上下文中）：

| 子目录 | 内容 | 对应安装阶段 |
|--------|------|-------------|
| `offline/miniconda/` | Miniconda安装脚本(.sh) | Stage 2 |
| `offline/wheels/` | pip wheel包 | Stage 4 |
| `offline/conda-pkgs/` | conda包缓存 | Stage 4 |

Dockerfile中通过检测文件是否存在实现条件离线安装（COPY + shell条件判断）。
准备离线资源：`./build.sh --prepare-offline`。

<a id="安全规范"></a>
## 安全规范

- 禁止在Dockerfile中硬编码密码、密钥、token
- 默认以非root用户 `ai` 运行（通过USER指令或entrypoint su切换）
- sudo权限通过NOPASSWD配置（可通过环境变量控制）
- APT配置5次重试，wget配置5次重试/120秒超时

<a id="非-root-用户规范"></a>
## 非root用户规范

- 固定用户名 `ai`，UID 1000
- 默认配置 NOPASSWD sudo
- HOME 目录为 `/home/ai`
- WORKDIR 设置为 `/workspace`
- 支持作为其他项目的基础镜像（FROM pytorch-base）

<a id="网络容错"></a>
## 网络容错

- APT：`Acquire::Retries "5"` 配置5次重试
- wget：`--tries=5 --timeout=120` 5次重试/120秒超时
- conda安装失败自动fallback到pip安装PyTorch
- 支持国内镜像源（通过build-arg控制）

## 镜像源切换

通过构建参数支持国内镜像：
- APT源：阿里云/清华TUNA
- conda源：清华TUNA
- pip源：阿里云

## 验证清单

- [ ] `bash build.sh` 无错误，构建日志有清晰的Stage标记和[TIMER]耗时
- [ ] `bash build.sh --prepare-offline` 可下载离线资源
- [ ] `bash build.sh --offline` 可离线构建
- [ ] 镜像中 `locale -a` 显示 zh_CN.UTF-8
- [ ] 镜像中 `date` 显示 Asia/Shanghai 时区
- [ ] `id ai` 显示 uid=1000，groups包含sudo
- [ ] `source /opt/conda/etc/profile.d/conda.sh && conda activate pytorch && python -c "import torch; print(torch.__version__)"` 正常
- [ ] conda环境pytorch在 `/opt/conda/envs/pytorch/`
- [ ] GPU模式下torch.cuda.is_available()为True（需要nvidia-docker2）
- [ ] entrypoint.sh语法正确（bash -n检查通过）
