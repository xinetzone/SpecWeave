# DevContainer Base - Conda-LLVM 依赖说明 (Dependencies)

> 本说明描述 `devcontainer-base:conda-llvm` 镜像的完整依赖结构，包括依赖链、系统依赖、工具链包、镜像源配置与运行时依赖。
> 目标是让使用者/维护者清晰理解镜像"由什么构成、依赖什么、如何升级"。

## 1. 依赖链总览

```
┌─────────────────────────────────────────────────────────────┐
│ ① 基础镜像 devcontainer-base:1.0                           │
│    Ubuntu 26.04 LTS + SSH + Docker DinD + Podman + Jupyter │
├─────────────────────────────────────────────────────────────┤
│ ② conda 变体 devcontainer-base:conda-1.0                   │
│    Miniconda3 (/opt/conda) + 镜像源配置 + venv 优先 PATH    │
├─────────────────────────────────────────────────────────────┤
│ ③ conda-llvm 变体（本镜像）                                  │
│    LLVM 工具链 + 构建工具，/opt/conda/bin 置于 PATH 最前     │
└─────────────────────────────────────────────────────────────┘
```

依赖关系（`VARIANTS` 声明）：`conda-llvm` → 依赖 `conda` → 依赖基础镜像 `devcontainer-base`。

## 2. 系统级依赖（继承自基础镜像）

| 类别 | 组件 | 说明 |
|------|------|------|
| 操作系统 | Ubuntu 26.04 LTS | 基础系统 |
| 环境 | zh_CN.UTF-8 + Asia/Shanghai | 中文本地化 + 中国时区 |
| 进程管理 | supervisord | 服务统一管理 |
| SSH | sshd（端口 22） | 远程登录 |
| 容器运行时 | Docker DinD（端口 2375）、Podman（rootless） | 容器内再运行容器 |
| Notebook | Jupyter（端口 8888） | 开发环境 |
| 用户 | devuser（UID 1001，非 root） | 默认工作用户 |
| 系统 Python | `/opt/venv` | 服务使用，绝对路径访问 |

> 版本参考（容器内 `docker run --rm <img> bash -c 'docker --version; podman --version'`）：Docker 29.7.2、Podman 5.7.0。

## 3. 工具链包依赖（conda base 环境）

所有 LLVM 相关包**统一锁定**到 `${LLVM_VERSION}`（默认 22.1.8），安装于 `/opt/conda` base 环境，未创建独立 conda 环境。

| 包 | 版本 | 作用 | 来源 |
|----|------|------|------|
| `llvmdev` | 22.1.8 | LLVM 核心库 + 头文件 | conda-forge |
| `clangdev` | 22.1.8 | Clang 开发头文件 | conda-forge |
| `clang` | 22.1.8 | C/C++/Objective-C 编译器 | conda-forge |
| `lld` | 22.1.8 | LLVM 链接器 | conda-forge |
| `lldb` | 22.1.8 | LLVM 调试器 | conda-forge |
| `cmake` | latest (4.4.2) | 跨平台构建系统 | conda-forge |
| `ninja` | latest (1.13.2) | 快速构建系统 | conda-forge |
| `make` | latest (4.4.1) | GNU Make | conda-forge |

> 版本锁定策略：LLVM 系列包统一 `=22.1.8` 保证 ABI/版本一致性；cmake/ninja/make 采用 `latest` 跟随 conda-forge 最新稳定版。

### 已排除包

- **`clang-tools-extra`**：conda-forge 通道不存在该包（`PackagesNotFoundInChannelsError`），已从安装列表移除。若需 `clang-tidy`/`clang-format` 请评估 conda-forge 实际可用包名后另行安装。

## 4. 镜像源依赖（构建期）

| 源 | 可选值 | 默认 | 说明 |
|----|--------|------|------|
| APT | `official` / `aliyun` / `tuna` | `official` | Ubuntu 系统包源 |
| Conda | `tuna` / `official` | `tuna` | conda-forge/default 频道镜像 |
| PyPI | `aliyun` / `tuna` / `official` | `aliyun` | pip 镜像 |

- 国内环境推荐 `--cn`（apt=aliyun, conda=tuna, pip=aliyun）。
- 配置写入：`.condarc`（conda 频道）、`pip.conf`（root + devuser），由共享脚本 `variants/shared/scripts/conda-mirror-setup.sh` 统一处理。

## 5. PATH 优先级（运行时）

`conda-llvm` 变体将 `/opt/conda/bin` 置于 PATH **最前**，保证工具链开箱即用：

```
/opt/conda/bin  >  ...  >  /opt/venv/bin  >  ...
   (LLVM/clang/cmake/ninja/make 直接可用)
```

- `llvm-config`、`clang`、`clang++`、`cmake`、`ninja`、`make` 直接可用。
- 默认 `python`/`pip` 指向 conda base 环境。
- 服务（Jupyter 等）由 supervisord 用 `/opt/venv/bin/jupyter` **绝对路径**启动，不受 PATH 变更影响。

## 6. 关键路径与文件

| 路径 | 说明 |
|------|------|
| `/opt/conda` | Miniconda3 安装根目录 |
| `/opt/conda/bin` | base 环境 bin（PATH 最前） |
| `/opt/venv` | 系统 Python venv（服务使用） |
| `/etc/profile.d/conda-llvm-init.sh` | 备选激活脚本 |
| `/etc/profile.d/conda-init.sh` | 原始 conda 激活脚本 |
| `/etc/devcontainer-variant-conda-llvm-build-info` | 构建元数据（发布清单数据源） |

## 7. 升级依赖指引

1. **升级 LLVM 版本**：修改 `.env.example` / `--build-arg LLVM_VERSION=<new>`，并确认该版本在 conda-forge 全部可用（llvmdev/clangdev/clang/lld/lldb）。
2. **升级 cmake/ninja/make**：无需改动，`latest` 自动跟随 conda-forge。
3. **升级基础链**：依次重建基础镜像 → conda 变体 → conda-llvm 变体（`build.sh` 自动处理依赖顺序）。
4. **镜像源变更**：通过 `APT_MIRROR`/`CONDA_MIRROR`/`PIP_MIRROR` 构建参数切换。

## 8. 相关规范

- [构建编排规范](../.agents/rules/build-orchestration.md)
- [测试规范](../.agents/rules/testing.md)
- [变体约定](../.agents/rules/variant-conventions.md)
- [Dockerfile 规范](./.agents/rules/dockerfile.md)
- [发布清单](./RELEASE.md)
