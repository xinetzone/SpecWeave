# DevContainer Base - Conda-LLVM 依赖说明 (Dependencies)

> 本说明描述 `devcontainer-base:conda-llvm` 镜像的完整依赖结构，包括依赖链、系统依赖、工具链包、镜像源配置与运行时依赖。
> 目标是让使用者/维护者清晰理解镜像"由什么构成、依赖什么、如何升级"。

## 1. 依赖链总览

```
┌─────────────────────────────────────────────────────────────┐
│ ① 基础镜像 devcontainer-base:${BASE_TAG}（默认 latest）      │
│    Ubuntu 26.04 LTS + SSH + Docker DinD + Podman + Jupyter  │
│    + Miniforge3（conda-forge，Python 3.14.6 cp314t main 环境）│
├─────────────────────────────────────────────────────────────┤
│ ② conda-llvm 变体（本镜像）                                  │
│    LLVM 工具链 + 构建工具，安装于 conda main 环境，            │
│    /opt/conda/envs/main/bin 置于 PATH 最前                   │
└─────────────────────────────────────────────────────────────┘
```

依赖关系（`VARIANTS` 声明）：`conda-llvm` → 直接依赖基础镜像 `devcontainer-base`（无中间变体）。

> 历史变更：本变体曾经由 conda 变体（Miniconda3 + base 环境）间接依赖基础镜像；conda 变体已从 `build.sh` 构建注册表移除，工具链随之迁移至 main 环境（Python 3.14t free-threading）。

## 2. 系统级依赖（继承自基础镜像）

| 类别 | 组件 | 说明 |
|------|------|------|
| 操作系统 | Ubuntu 26.04 LTS | 基础系统 |
| 环境 | zh_CN.UTF-8 + Asia/Shanghai | 中文本地化 + 中国时区 |
| 进程管理 | supervisord | 服务统一管理 |
| SSH | sshd（端口 22） | 远程登录 |
| 容器运行时 | Docker DinD（端口 2375）、Podman（rootless） | 容器内再运行容器 |
| Notebook | Jupyter（端口 8888，main 环境） | 开发环境 |
| 用户 | devuser（UID 1000，非 root） | 默认工作用户 |
| Conda 发行版 | Miniforge3（conda-forge 官方，libmamba solver） | `/opt/conda`，main 环境为默认用户环境 |
| Python | 3.14.6 cp314t free-threading | main 环境（`/opt/conda/envs/main`），GIL 默认禁用 |

## 3. 工具链包依赖（conda main 环境）

所有 LLVM 相关包**统一锁定**到 `${LLVM_VERSION}`（默认 22.1.8），安装于 `/opt/conda/envs/main`（main 环境，默认用户环境）。python 显式锁定 `*=*cp314t` 构建作为 free-threading 回归防线。

| 包 | 版本 | 作用 | 来源 |
|----|------|------|------|
| `llvmdev` | 22.1.8 | LLVM 核心库 + 头文件 | conda-forge |
| `clangdev` | 22.1.8 | Clang 开发头文件 | conda-forge |
| `clang` | 22.1.8 | C/C++/Objective-C 编译器 | conda-forge |
| `lld` | 22.1.8 | LLVM 链接器 | conda-forge |
| `python` | 3.14.6 (`*=*cp314t`) | 显式锁定 free-threading 构建（回归防线） | conda-forge |
| `cmake` | latest | 跨平台构建系统 | conda-forge |
| `ninja` | latest | 快速构建系统 | conda-forge |
| `make` | latest | GNU Make | conda-forge |
| `libgcc` | latest | GCC 运行时（clang 链接器 `-lgcc` 依赖） | conda-forge |
| `libstdcxx-ng` | latest | GCC C++ 运行时（`-lstdc++` 依赖） | conda-forge |

> 版本锁定策略：LLVM 系列包统一 `=22.1.8` 保证 ABI/版本一致性；cmake/ninja/make/libgcc/libstdcxx-ng 采用 `latest` 跟随 conda-forge 最新稳定版，实际版本以 build-info 为准。

### 安装分组（Stage 2 conda_install_group）

| 分组 | 包 | 说明 |
|------|-----|------|
| G1: LLVM Core | llvmdev/clangdev/clang/lld（锁定版本）+ python=`*=*cp314t` | 工具链 + free-threading 防线 |
| G2: Build Tools | cmake/ninja/make | 构建系统工具 |
| G3: GCC Runtime | libgcc/libstdcxx-ng | conda-forge clang 链接器必需 |

安装后执行 **free-threading 完整性检查（GUARD）**：python build string 必须为 `cp314t` 且 `sys._is_gil_enabled()` 必须为 `False`，否则构建失败。

### 已排除包

- **`lldb`**：python 绑定在 conda-forge 无 cp314t（free-threading）构建，安装会使求解器静默将 python 从 `cp314t` 切换为 `cp314 + python-gil`（GIL 回归），故显式排除。如需 lldb，请在独立环境（非 main）中安装。
- **`clang-tools-extra`**：conda-forge 通道不存在该包（`PackagesNotFoundInChannelsError`），已从安装列表移除。若需 `clang-tidy`/`clang-format` 请评估 conda-forge 实际可用包名后另行安装。

## 4. 镜像源依赖（构建期）

| 源 | 可选值 | 默认 | 说明 |
|----|--------|------|------|
| APT | `official` / `aliyun` / `tuna` | `official` | Ubuntu 系统包源 |
| Conda | `bfsu` / `tuna` / `aliyun` / `official` | `bfsu` | conda-forge 频道镜像（北外镜像） |
| PyPI | `aliyun` / `tuna` / `official` | `aliyun` | pip 镜像 |

- 基础镜像（V2）已内置默认镜像源；变体构建时按 `CONDA_MIRROR` 重写 `/opt/conda/.condarc`（custom_channels + `default_channels_alias` 指向所选镜像，并显式配置 conda-forge 频道、`channel_priority: strict`、libmamba solver）。
- 国内环境推荐 `--cn`（apt=aliyun, conda=tuna, pip=aliyun，为 `build.sh --cn` 的实际传参；不传参时 Dockerfile 内部默认 `CONDA_MIRROR=bfsu`）。

## 5. PATH 优先级（运行时）

`conda-llvm` 变体将 `/opt/conda/envs/main/bin` 置于 PATH **最前**，保证工具链开箱即用：

```
/opt/conda/envs/main/bin  >  /opt/conda/bin  >  ...
   (LLVM/clang/cmake/ninja/make + Python 3.14t + Jupyter 直接可用)
```

- `llvm-config`、`clang`、`clang++`、`cmake`、`ninja`、`make` 直接可用。
- 默认 `python`/`pip` 指向 conda main 环境（Python 3.14.6 cp314t free-threading）。
- 服务（Jupyter 等）由 supervisord 用 main 环境 **绝对路径**（`/opt/conda/envs/main/bin/jupyter`）启动，不受 PATH 变更影响。

## 6. 关键路径与文件

| 路径 | 说明 |
|------|------|
| `/opt/conda` | Miniforge3 安装根目录 |
| `/opt/conda/envs/main` | main 环境（默认用户环境，工具链 + Python 3.14t + Jupyter） |
| `/opt/conda/envs/main/bin` | main 环境 bin（PATH 最前） |
| `/etc/profile.d/conda-init.sh` | 基础镜像默认激活脚本（激活 main 环境） |
| `/etc/profile.d/conda-llvm-init.sh` | 备选激活脚本（激活 main 环境，向后兼容） |
| `/etc/devcontainer-variant-conda-llvm-build-info` | 构建元数据（发布清单数据源） |

## 7. 升级依赖指引

1. **升级 LLVM 版本**：修改 `.env.example` / `--build-arg LLVM_VERSION=<new>`，并确认该版本在 conda-forge 全部可用（llvmdev/clangdev/clang/lld）。注意 **不要** 添加 lldb（见"已排除包"）。
2. **升级 cmake/ninja/make**：无需改动，`latest` 自动跟随 conda-forge。
3. **升级基础链**：依次重建基础镜像 → conda-llvm 变体（`build.sh` 自动处理依赖顺序，conda 中间变体已下线）。
4. **镜像源变更**：通过 `APT_MIRROR`/`CONDA_MIRROR`/`PIP_MIRROR` 构建参数切换。
5. **Python 版本约束**：main 环境 python 必须保持 cp314t（free-threading）构建；任何引入 GIL 构建 python 的包变更都会被构建期 GUARD 拦截。

## 8. 相关规范

- [构建编排规范](../.agents/rules/build-orchestration.md)
- [测试规范](../.agents/rules/testing.md)
- [变体约定](../.agents/rules/variant-conventions.md)
- [Dockerfile 规范](./.agents/rules/dockerfile.md)
- [发布清单](./RELEASE.md)
