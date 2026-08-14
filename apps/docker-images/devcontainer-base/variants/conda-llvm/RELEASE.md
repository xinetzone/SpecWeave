# DevContainer Base - Conda-LLVM 镜像发布清单 (Release Manifest)

> 本清单基于已构建并验证通过的 `devcontainer-base:conda-llvm-1.0` 镜像生成（对应**旧架构**：conda 变体依赖链 + base 环境安装）。
> 运行时元数据源：容器内 `/etc/devcontainer-variant-conda-llvm-build-info`（构建时自动写入）。
> 验证依据：[test-conda-llvm.sh](../scripts/test-conda-llvm.sh) 21 项测试全部 PASS（0 FAIL）。

> **⚠️ 架构变更公告（2026-08）**：自 main 环境迁移合入后，本变体**直接基于 `devcontainer-base:${BASE_TAG}`**（conda 中间变体已从构建注册表移除），LLVM 工具链安装于 conda **main 环境**（Python 3.14.6 cp314t free-threading），`lldb` 被排除（cp314t 缺失会引发 GIL 回归），新增 `libgcc`/`libstdcxx-ng` 依赖。
> 下方章节 1-8 为 **1.0 历史发布记录**，其中依赖链、版本矩阵（lldb 行）、验证结论均对应旧架构，**不可直接套用于新架构镜像**；新镜像发布前需按 [RELEASE-GUIDE.md](./RELEASE-GUIDE.md) 重新构建与验证，并确认测试脚本已适配 main 环境路径（T14/T19）。

## 1. 镜像标识（1.0 历史记录）

| 项目 | 值 |
|------|-----|
| 镜像名称 | `devcontainer-base` |
| 变体标签 | `conda-llvm-1.0`（正式） / `conda-llvm-latest`（滚动） |
| 完整引用 | `devcontainer-base:conda-llvm-1.0` |
| 镜像大小 | 6.17 GB |
| 架构 | x86_64 (amd64) |
| 基础系统 | Ubuntu 26.04 LTS |

## 2. 发布元数据（1.0 历史记录）

| 项目 | 值 |
|------|-----|
| 构建日期 | 2026-08-07T10:17:59Z（UTC） |
| 构建环境 | WSL2 / Linux + Docker BuildKit（`--progress=plain`） |
| 构建命令 | `bash variants/scripts/build-conda-llvm.sh --tag 1.0` |
| 验证状态 | ✅ 21/21 测试通过（0 FAIL，旧架构镜像） |
| Build-Info 路径 | `/etc/devcontainer-variant-conda-llvm-build-info` |
| 构建计时 | 启用（[TIMER] 各阶段耗时记录） |

## 3. 版本矩阵（1.0 历史记录，base 环境安装）

> `PACKAGES_INSTALLED=llvmdev,clangdev,clang,lld,lldb,cmake,ninja,make`（安装于 conda base 环境）
> 新架构下 `PACKAGES_INSTALLED=llvmdev,clangdev,clang,lld,cmake,ninja,make,libgcc,libstdcxx-ng`（main 环境，无 lldb）

| 组件 | 请求版本 | 实际版本 | 类型 |
|------|---------|---------|------|
| LLVM (llvmdev) | 22.1.8 | 22.1.8 | 编译工具链 |
| Clang (clang) | 22.1.8 | 22.1.8 | 编译器 |
| Clang Dev (clangdev) | 22.1.8 | 22.1.8 | 头文件/开发库 |
| lld | 22.1.8 | 22.1.8 | 链接器 |
| ~~lldb~~ | ~~22.1.8~~ | ~~22.1.8~~ | 调试器（**新架构已排除**） |
| CMake | latest | 4.4.2 | 构建系统 |
| Ninja | latest | 1.13.2 | 构建系统 |
| Make | latest | 4.4.1 | 构建工具 |
| Conda | - | 26.7.0 | 包管理器 |

> ⚠️ 注意：`clang-tools-extra` 包在 conda-forge 通道不存在（`PackagesNotFoundInChannelsError`），已从安装列表移除，不纳入版本矩阵。

## 4. 依赖链（1.0 历史记录）

```
【旧架构（1.0 及之前）】
devcontainer-base:1.0            # 基础镜像（Ubuntu 26.04 + SSH + Docker + Podman + Jupyter）
        │
        ▼ (FROM)
devcontainer-base:conda-1.0      # conda 变体（Miniconda3 → /opt/conda，已下线）
        │
        ▼ (FROM)
devcontainer-base:conda-llvm-1.0 # 本镜像（LLVM/Clang 工具链，base 环境）

【新架构（main 环境迁移后）】
devcontainer-base:${BASE_TAG}    # 基础镜像（Miniforge3 + main 环境 Python 3.14.6 cp314t）
        │
        ▼ (FROM)
devcontainer-base:conda-llvm-*   # 本镜像（LLVM/Clang 工具链，main 环境）
```

- 构建依赖校验：`build.sh` 通过 `check_dependency_image()` 在构建前校验依赖镜像存在。
- 基础镜像构建信息（容器内 `docker run --rm <img> cat /etc/devcontainer-build-info`）：
  - `BASE_IMAGE=ubuntu:26.04`、`NON_ROOT_USER=devuser`
  - `SERVICES=sshd,dockerd,podman,jupyter`、`SUPERVISOR=enabled`
  - `DOCKER_DIND=enabled`、`PODMAN_ROOTLESS=enabled`

## 5. 构建参数（1.0 历史记录）

| 参数 | 本次值 | 当前默认值 |
|------|-------|-----------|
| `BASE_TAG` | `1.0`（conda 变体标签） | `latest`（基础镜像标签） |
| `APT_MIRROR` | `aliyun` | `official` |
| `CONDA_MIRROR` | `tuna` | `bfsu` |
| `PIP_MIRROR` | `aliyun` | `aliyun` |
| `LLVM_VERSION` | `22.1.8` | `22.1.8` |

## 6. 验证结果（1.0 历史记录，21 项测试）

| 层级 | 测试范围 | 结果 |
|------|---------|------|
| L1 工具链 | llvm-config / clang / clang++ / cmake / ninja / make 版本与可用性 | ✅ PASS |
| L2 功能编译 | C++ Hello World 编译 + 执行、CMake+Ninja 工程 | ✅ PASS |
| L3 组件深度 | llvm-config components/includedir、基础服务保留 | ✅ PASS |
| 基础服务 | sshd / dockerd / podman / jupyter / supervisord | ✅ PASS |

> 运行验证：`bash variants/scripts/test-conda-llvm.sh --tag 1.0`
> ⚠️ 新架构注意：测试脚本 T14（`/opt/conda/bin/jupyter`）与 T19（python 指向 `/opt/conda/bin/python`）检查的是旧 base 环境路径；新架构镜像中 Jupyter/python 位于 `/opt/conda/envs/main/bin`，发布前需先适配测试脚本。

## 7. 使用方式

```bash
# 交互式进入容器
docker run -it --rm --privileged devcontainer-base:conda-llvm-1.0 bash

# DinD 开发模式
docker run -d --privileged -p 2222:22 -p 2375:2375 -p 8888:8888 \
  -v $(pwd)/workspace:/workspace -v docker-storage:/var/lib/docker \
  -e USER_PASSWORD=devpass -e JUPYTER_TOKEN=mysecret \
  devcontainer-base:conda-llvm-1.0

# 查看构建元数据
docker run --rm devcontainer-base:conda-llvm-1.0 \
  cat /etc/devcontainer-variant-conda-llvm-build-info
```

## 8. 变更记录

| 日期 | 变更 | 关联 |
|------|------|------|
| 2026-08-14 | 架构变更：直接基于 devcontainer-base，工具链迁移至 main 环境（Python 3.14t free-threading），排除 lldb，新增 libgcc/libstdcxx-ng，CONDA_MIRROR 默认改为 bfsu | main 环境迁移 |
| 2026-08-07 | 首次发布验证：构建成功 + 21 项测试全部 PASS | 🔴 高行动项闭环 |
| 2026-08-07 | 移除 conda-forge 不存在的 `clang-tools-extra` 包 | 缺陷修复 #1 |
| 2026-08-07 | T4 cmake 断言支持 4.x 并修正版本提取逻辑 | 缺陷修复 #2 |
| 2026-08-07 | 修复 `FROM` 后未重声明 `ARG BASE_TAG`，build-info 的 `BASE_IMAGE` 标签缺失 | 缺陷修复 #3 |

## 9. 相关文档

- [Conda-LLVM 变体 README](./README.md)
- [依赖说明](./DEPENDENCIES.md)
- [发布操作指南](./RELEASE-GUIDE.md)
- [基础镜像 README](../../README.md)
- [构建编排规范](../.agents/rules/build-orchestration.md)
- [测试规范](../.agents/rules/testing.md)
