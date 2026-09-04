# xmnn-whl-builder 干净重编译模式 - Product Requirement Document

## Overview
- **Summary**: 为 xmnn-whl-builder 新增「干净重编译」模式（`--clean-rebuild/-C`），通过禁用 ccache C/C++编译缓存并同时绕过 Docker 层缓存，确保 tvm/vta/xmnn 三个 Python 包均从源码经 Nuitka 完整重新编译为 C 扩展，不命中任何已有编译缓存。
- **Purpose**: 当前 `--no-cache/-F` 仅绕过 Docker 镜像层缓存，但 BuildKit 的 `type=cache` ccache 挂载独立于层缓存持久化，即使加了 `--no-cache` 仍可能命中旧的 C 编译结果，导致 wheel 包并非真正全新编译。需要一个显式的、可验证的「完全重编译」入口。
- **Target Users**: XMNN 开发者、CI 系统、需要验证编译器/工具链变更或确保产物新鲜度的场景。

## Goals
- 新增 `--clean-rebuild/-C` 命令行选项到 build.sh
- 干净模式下自动禁用 ccache（通过 `CCACHE_DISABLE=1` 官方机制，不清空已有缓存，不影响后续快速构建）
- 干净模式下自动追加 `--no-cache`（绕过 Docker 层缓存）
- Dockerfile 层支持通过 build-arg `CLEAN_REBUILD=1` 透传控制
- 容器内 build-wheel.sh 识别干净模式并打印明确的状态日志
- 构建完成后 verify-wheel.sh 11/11 全部 PASS（与普通构建相同的质量门禁）
- 默认构建行为不变（仍使用 ccache 加速）

## Non-Goals (Out of Scope)
- 不重新编译 TVM C++ 原生库（libtvm.so 来自 bind mount 的 npu_tvm 预编译产物，不属于 Nuitka Python 编译范畴）
- 不更改 pip 下载缓存（pip cache 只缓存依赖 wheel 下载，不影响 tvm/vta/xmnn 编译结果）
- 不引入新的构建依赖
- 不更改默认构建行为（默认仍使用 ccache 快速构建）
- 不修改 xmnn-runtime 或下游镜像
- 不实现 `make clean` 风格的全目录清理（Docker builder 阶段每次在干净容器中运行，中间产物不跨构建持久化）

## Background & Context
- xmnn-whl-builder 使用两阶段 Docker 构建，builder 阶段用 Nuitka 将 tvm/vta/xmnn 编译为 C 扩展，再通过 CMake+scikit-build-core 打包为 wheel
- Nuitka 调用系统 C 编译器（clang）时通过 ccache 加速重复构建，ccache 目录通过 BuildKit `--mount=type=cache,id=xmnn-nuitka-ccache` 持久化
- Docker 的 `--no-cache` 只影响 Dockerfile 中 RUN/COPY 等指令的层缓存复用，不影响 BuildKit `type=cache` 挂载——这是 BuildKit 的设计：cache mount 是显式声明的持久化卷，与层缓存生命周期独立
- build.sh 已有源码快照检测机制（npu_tvm/npuusertools SHA256），源码变化时自动加 `--no-cache`，但该机制同样无法处理 ccache
- ccache 官方提供 `CCACHE_DISABLE=1` 环境变量，设置后 ccache 直接透传编译器调用，不查缓存也不写缓存，是 bypass ccache 最优雅的方式（不污染已有缓存，下次普通构建缓存仍然可用）

## Functional Requirements
- **FR-1**: build.sh 新增 `--clean-rebuild/-C` 命令行选项
- **FR-2**: 指定 `--clean-rebuild` 时，自动设置 `NO_CACHE=1`（即隐含 `--no-cache`，绕过 Docker 层缓存）
- **FR-3**: 指定 `--clean-rebuild` 时，向 `docker build` 追加 `--build-arg CLEAN_REBUILD=1`
- **FR-4**: Dockerfile 新增 `ARG CLEAN_REBUILD=0` 和对应 `ENV CLEAN_REBUILD=${CLEAN_REBUILD}`，默认 0（不启用）
- **FR-5**: build-wheel.sh 在容器内检测到 `CLEAN_REBUILD=1` 时，设置 `CCACHE_DISABLE=1`，并打印醒目的干净模式提示日志
- **FR-6**: build-wheel.sh 在干净模式下执行 `ccache -z` 清零统计计数器（便于事后查看 ccache 日志确认零命中）
- **FR-7**: build.sh 的 usage/help 文档同步更新，说明 `--clean-rebuild/-C` 的用途和与 `--no-cache/-F` 的区别
- **FR-8**: build.sh 的配置日志（log_kv 区域）显示是否处于干净重编译模式
- **FR-9**: 干净模式构建完成后，verify-wheel.sh 11项验证全部通过（与普通构建一致）

## Non-Functional Requirements
- **NFR-1**: 不影响默认构建速度——不指定 `--clean-rebuild` 时行为与之前完全一致，ccache 正常工作
- **NFR-2**: 不破坏已有缓存——干净模式通过 `CCACHE_DISABLE=1` 禁用，不删除/清空 ccache 目录，后续普通构建仍可命中已有缓存
- **NFR-3**: 可验证性——构建日志中必须有明确标识可确认 ccache 确实被禁用，而非依赖"我加了参数所以应该生效"的信念
- **NFR-4**: 向后兼容——所有已有构建命令（`./build.sh --cn`, `./build.sh -v` 等）继续正常工作，无需修改

## Constraints
- **Technical**: 必须遵循现有 Dockerfile 规范（两阶段构建、bind mount 源码不进镜像、Nuitka 参数固化在 ENV/ARG）；必须使用 BuildKit syntax=docker/dockerfile:1.7-labs；构建上下文仍为 external/chaos/
- **Business**: 默认快速构建体验不能受影响（日常开发依赖 ccache 将 10-30 分钟的编译压到分钟级）
- **Dependencies**: ccache 已在 builder 阶段安装，`CCACHE_DISABLE` 是 ccache 标准环境变量，无需额外安装

## Assumptions
- ccache 版本支持 `CCACHE_DISABLE=1`（ccache 3.x+ 均支持，当前镜像中为标准 conda-forge 版本）
- `CCACHE_DISABLE=1` 不仅禁用缓存查找，也禁用缓存写入（即干净模式下不会污染缓存，同时也不会从缓存读取——这是所需行为）
- Nuitka 通过 `NUITKA_CCACHE_BINARY` 调用 ccache，ccache 再调用 clang；设置 `CCACHE_DISABLE=1` 后 ccache 成为透明透传，Nuitka 无感知
- tvm C++ 原生库（libtvm.so）来自 bind mount 的 npu_tvm，已预编译完成，用户说的"tvm/vta/xmnn 全是重新编译的"指 Nuitka 对这三个 Python 包的编译

## Acceptance Criteria

### AC-1: clean-rebuild 选项可用且 help 文档完整
- **Given**: 用户在 xmnn-whl-builder 目录下执行 `./build.sh -h`
- **When**: 查看帮助输出
- **Then**: 帮助信息中包含 `--clean-rebuild, -C` 选项，说明其作用为"干净重编译：禁用 ccache + 绕过 Docker 层缓存，确保 tvm/vta/xmnn 全量重新编译"
- **Verification**: `programmatic`
- **Notes**: 同时需说明与 `-F/--no-cache` 的区别

### AC-2: 干净模式自动启用 --no-cache
- **Given**: 用户执行 `./build.sh --clean-rebuild`
- **When**: 构建开始前的配置日志输出
- **Then**: 日志中显示"干净重编译模式: 是 (--clean-rebuild)"和"docker build 已追加 --no-cache"
- **Verification**: `programmatic`

### AC-3: CLEAN_REBUILD build-arg 正确透传到容器
- **Given**: 用户执行 `./build.sh --clean-rebuild -v`
- **When**: 查看 docker build 命令输出
- **Then**: docker build 命令行包含 `--build-arg CLEAN_REBUILD=1`
- **Verification**: `programmatic`

### AC-4: 容器内 ccache 被禁用
- **Given**: 以 `--clean-rebuild` 模式执行构建
- **When**: 容器内 build-wheel.sh 执行到 Environment Check / ccache 初始化阶段
- **Then**: 构建日志中出现醒目的干净模式标识（如"=== CLEAN REBUILD MODE: ccache DISABLED ==="），且 ccache 统计显示缓存命中为 0
- **Verification**: `programmatic`

### AC-5: 默认构建行为不变
- **Given**: 用户执行普通 `./build.sh --cn`（不带 --clean-rebuild）
- **When**: 构建完成
- **Then**: ccache 正常启用，第二次构建时若源码未变可命中缓存加速；构建产物 verify-wheel.sh 11/11 PASS
- **Verification**: `programmatic`

### AC-6: 干净构建产物验证通过
- **Given**: 以 `--clean-rebuild` 模式完成构建
- **When**: 自动执行 verify_image 4步验证
- **Then**: 基础 import 通过、/opt/xmnn-dist/ 存在 wheel、verify-wheel.sh 11/11 PASS、构建工具存在
- **Verification**: `programmatic`

### AC-7: 干净模式不破坏已有 ccache
- **Given**: 先执行一次普通构建填充 ccache，再执行 `./build.sh --clean-rebuild`，最后再执行一次普通构建
- **When**: 观察第三次普通构建的 ccache 命中率
- **Then**: 第三次普通构建仍能命中第一次构建留下的 ccache（证明干净模式未清空/破坏缓存）
- **Verification**: `programmatic`
- **Notes**: 此为缓存隔离验证

### AC-8: Dockerfile 规范更新
- **Given**: 开发者查看 .agents/rules/dockerfile.md
- **When**: 阅读 Dockerfile 规范
- **Then**: 规范中包含 CLEAN_REBUILD 参数说明，注明其用途、默认值和与 ccache 的关系
- **Verification**: `human-judgment`

## Open Questions
- 无（方案经过第一性原理分析和对抗审查，设计已收敛）
