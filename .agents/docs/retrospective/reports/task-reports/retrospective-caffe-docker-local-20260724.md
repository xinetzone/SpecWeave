---
id: "retrospective-caffe-docker-local-20260724"
title: "Caffe docker/local 目录全面复盘报告"
source: "projects/xuanspace/vendor/caffe/docker/local/"
date: "2026-07-24"
updated: "2026-07-24"
category: "retrospective"
scope: "task"
tags: ["caffe", "docker", "conda", "python-3.14", "boost-python", "multi-stage-build", "configuration-audit", "bugfix"]
fix_status: "phase1-complete"
---

# Caffe docker/local 目录全面复盘报告

> **生成日期**：2026-07-24
> **修复更新日期**：2026-07-24（阶段一+二部分完成）
> **分析范围**：`projects/xuanspace/vendor/caffe/docker/local/` 全目录
> **方法论**：retrospective-cmd 四步法（事实→分析→洞察→报告）
> **详细程度**：standard（标准版）
> **修复进度**：✅ P0全部修复（3/3），✅ P1部分修复（2/4），✅ P2部分修复（1/6）

---

## 修复状态快速参考

| 问题编号 | 问题描述 | 状态 | 修复日期 |
|---------|---------|------|---------|
| P0-1 | build-conda.sh 版本号 py313→py314 | ✅ 已修复 | 2026-07-24 |
| P0-2 | _check_proto.sh/_test_proto.sh 镜像名 py313→py314 | ✅ 已修复 | 2026-07-24 |
| P0-3 | entrypoint_test.sh 引用不存在文件 | ✅ 已修复（删除） | 2026-07-24 |
| P1-1 | Dockerfile.conda UID/GID 1001→1000 | ✅ 已修复 | 2026-07-24 |
| P1-2 | _write_dockerfile.py 已过时 | ✅ 已修复（删除） | 2026-07-24 |
| P1-3 | runtime-conda 重复编译 Boost.Python | ⏳ 待修复（架构优化） | - |
| P1-4 | RUNTIME_IMAGE_USAGE.md 目录结构过时 | ⏳ 待修复 | - |
| P2-1 | generate-makefile-config.sh 注释 Ubuntu 版本 | ✅ 已修复 | 2026-07-24 |
| P2-2 | verify-runtime.sh 路径不一致 | ⏳ 待修复 | - |
| P2-3 | verify-runtime.sh 包名不一致 | ⏳ 待修复 | - |
| P2-4 | runtest.sh 与 test_new_features.sh 重叠 | ⏳ 待修复 | - |
| P2-5 | build-conda.sh 未使用共享库 | ⏳ 待修复 | - |
| P2-6 | _check_py314.sh 环境名 | ℹ️ 设计如此（保留py314test测试环境） | - |
| P3-1~P3-7 | 镜像体积/CI/配置清理等 | ⏳ 待规划 | - |

---

## 第1章 · 执行概览

### 基本信息

| 属性 | 值（修复后） |
|------|-----|
| 分析对象 | `docker/local/` 目录（vendor 子模块内） |
| 对应项目 | Caffe Docker 镜像构建系统（CPU-only） |
| 文件总数 | 20（修复后，删除2个失效/过时文件） |
| 顶层目录 | 2（`conda/`、`lib/`） |
| Dockerfile 数量 | 2（`Dockerfile` + `Dockerfile.conda`） |
| Shell 脚本数量 | 11（修复后，删除2个） |
| 配置文件数量 | 4（condarc / pip.conf / 2 个 .gitignore） |
| 文档数量 | 1（`RUNTIME_IMAGE_USAGE.md`） |
| Python 脚本数量 | 0（修复后，删除 `_write_dockerfile.py`） |

### 关键数据一览

| 指标 | 数值（修复后） |
|------|------|
| 识别问题总数 | 20（P0:3 / P1:4 / P2:6 / P3:7） |
| 已修复问题 | 6（P0:3 / P1:2 / P2:1） |
| 待修复问题 | 13（P1:2 / P2:4 / P3:7） |
| 设计豁免问题 | 1（P2-6） |
| 双轨 Dockerfile 行数 | 356（Dockerfile）+ 422（Dockerfile.conda） |
| 构建脚本数量 | 4（build.sh / build-multistage.sh / build-conda.sh / export-image.sh） |
| 共享库函数数量 | 14（log.sh:9 + check_env.sh:5） |
| Dockerfile 构建阶段数 | 6（Dockerfile）+ 2（Dockerfile.conda） |

### 亮点与挑战

| 亮点 | 挑战 |
|------|------|
| 双轨 Dockerfile 并行支持 Python 3.10 与 3.14 | 双轨间版本号、环境名、镜像名不一致 |
| 多阶段构建设计清晰（base→builder→runtime） | runtime 基于-builder 导致镜像体积偏大 |
| 共享 Shell 函数库（log.sh/check_env.sh）规范日志 | build-conda.sh 未复用共享库 |
| generate-makefile-config.sh 自动检测 Boost.Python 命名 | 自动检测列表未覆盖 Python 3.12/3.13/3.14 |
| 详细的多阶段构建日志（耗时统计、错误诊断） | 文档与实际目录结构存在偏差 |
| 支持 wslc/docker 双容器工具 | 部分脚本仅适配 docker（如 export wheel） |

---

## 第2章 · 目录结构与文件功能

### 2.1 完整目录树

```
docker/local/
├── .gitignore                          # 保留 lib/ 目录（!lib/）
├── lib/                                # 共享 Shell 函数库
│   ├── log.sh                          # 日志辅助函数（9个函数）
│   └── check_env.sh                    # 环境检查函数（5个函数）
└── conda/                              # 主构建目录
    ├── .gitignore                      # 保留 build/ 目录（!build/）
    ├── Dockerfile                      # Python 3.10 + Ubuntu 22.04 主 Dockerfile（356行）
    ├── Dockerfile.conda                # Python 3.14 + Conda 备选 Dockerfile（422行，UID/GID已修复为1000）
    ├── RUNTIME_IMAGE_USAGE.md          # 使用指南文档（230行，目录结构待更新）
    ├── _check_py314.sh                 # Python 3.14 conda 环境结构检查脚本（py314test独立测试环境）
    ├── build.sh                        # 开发镜像构建入口（默认 builder-dev）
    ├── run.sh                          # 开发容器启动脚本（挂载源码）
    ├── runtest.sh                      # 容器内 pycaffe 测试脚本
    ├── test_new_features.sh            # pycaffe 新功能测试脚本
    ├── build/
    │   ├── _check_proto.sh             # protobuf 导入顺序测试（已修复为py314）
    │   ├── _test_proto.sh              # protobuf 单独导入测试（已修复为py314）
    │   ├── build-conda.sh              # Conda 镜像构建脚本（已修复为py314）
    │   ├── build-multistage.sh         # 多阶段构建主脚本（580行，含日志）
    │   ├── check_builder.sh            # builder 镜像依赖检查脚本
    │   └── export-image.sh             # 镜像导出脚本（tar/tar.gz）
    ├── config/
    │   ├── condarc                     # conda 镜像源配置（清华源）
    │   └── pip.conf                    # pip 镜像源配置（阿里云）
    └── scripts/
        ├── generate-makefile-config.sh # Makefile.config 自动生成（Boost 检测，注释已修正为22.04）
        ├── verify-caffe.sh             # Caffe 安装验证脚本
        └── verify-runtime.sh           # 运行时完整验证脚本（9步验证，路径/包名待修复）
```

> **变更记录**：修复过程中删除了 `entrypoint_test.sh`（引用不存在的文件，已失效）和 `_write_dockerfile.py`（已过时，与手动维护的Dockerfile.conda冲突）。

### 2.2 文件功能矩阵

| 文件 | 类型 | 功能 | 调用方 | 依赖 | 状态 |
|------|------|------|--------|------|------|
| `Dockerfile` | 配置 | 6阶段多阶段构建（base-system→base-builder→builder-dev→builder→pycaffe-builder→runtime），Python 3.10 | build.sh / build-multistage.sh | scripts/generate-makefile-config.sh, scripts/verify-caffe.sh | ✅ 正常 |
| `Dockerfile.conda` | 配置 | 2阶段构建（pycaffe-builder-conda→runtime-conda），Python 3.14 + 源码编译 Boost.Python，UID/GID已统一为1000 | build-conda.sh | 依赖 caffe-cpu:builder 阶段 | ✅ 已修复UID |
| `build.sh` | 脚本 | 开发镜像构建入口，默认 builder-dev 目标 | 用户直接调用 | lib/log.sh, lib/check_env.sh | ✅ 正常 |
| `build/build-multistage.sh` | 脚本 | runtime 镜像一键构建（580行，含日志/验证/导出） | 用户直接调用 | lib/log.sh, lib/check_env.sh, export-image.sh | ✅ 正常 |
| `build/build-conda.sh` | 脚本 | Conda Python 3.14 镜像构建（版本号已修复为py314） | 用户直接调用 | 无（未使用共享库，待改进） | ✅ 版本号已修复 |
| `build/export-image.sh` | 脚本 | 镜像导出为 tar/tar.gz | build-multistage.sh 或用户 | lib/log.sh, lib/check_env.sh | ✅ 正常 |
| `run.sh` | 脚本 | 开发容器启动，挂载源码到 /workspace | 用户直接调用 | lib/log.sh, lib/check_env.sh | ✅ 正常 |
| `runtest.sh` | 脚本 | 容器内 pycaffe 导入+工具函数+LeNet 测试 | 容器内手动执行 | conda 环境 | ⚠️ 与test_new_features重叠 |
| `test_new_features.sh` | 脚本 | pycaffe 新功能测试（与 runtest.sh 重叠） | 容器内手动执行 | conda 环境 | ⚠️ 与runtest重叠 |
| `_check_py314.sh` | 脚本 | Python 3.14 conda 环境结构检查（py314test独立测试环境） | 开发调试 | conda 环境 py314test | ℹ️ 设计如此 |
| `build/_check_proto.sh` | 脚本 | protobuf 导入顺序测试（已修复为py314镜像） | 开发调试 | caffe-cpu:conda-py314 | ✅ 已修复 |
| `build/_test_proto.sh` | 脚本 | protobuf 单独导入测试（已修复为py314镜像） | 开发调试 | caffe-cpu:conda-py314 | ✅ 已修复 |
| `build/check_builder.sh` | 脚本 | builder 镜像 gflags/glog 依赖检查 | 开发调试 | caffe-cpu:builder | ✅ 正常 |
| `scripts/generate-makefile-config.sh` | 脚本 | Makefile.config 自动生成（Boost.Python 检测，注释已修正为22.04） | Dockerfile builder 阶段 | ldconfig | ✅ 注释已修复 |
| `scripts/verify-caffe.sh` | 脚本 | Caffe 安装验证（导入+proto+tools） | Dockerfile runtime 阶段 | python3 | ✅ 正常 |
| `scripts/verify-runtime.sh` | 脚本 | 运行时完整验证（9步，路径/包名不一致） | 手动执行 | /host-caffe 挂载点 | ⏳ 待修复 |
| `lib/log.sh` | 库 | 日志函数（header/section/step/info/warn/error/success/kv/blank/troubleshoot） | 所有脚本 source | 无 | ✅ 正常 |
| `lib/check_env.sh` | 库 | 环境检查（detect_container_tool/check_command/check_directory/check_file/check_docker_running/check_build_environment） | build.sh / run.sh 等 | lib/log.sh | ✅ 正常 |
| `config/condarc` | 配置 | conda 清华镜像源 | 未在 Dockerfile 中使用 | 无 | ⏳ 待清理或使用 |
| `config/pip.conf` | 配置 | pip 阿里云镜像源 | 未在 Dockerfile 中使用 | 无 | ⏳ 待清理或使用 |
| ~~`entrypoint_test.sh`~~ | ~~脚本~~ | ~~容器入口测试（引用不存在的文件）~~ | - | - | 🗑️ 已删除 |
| ~~`_write_dockerfile.py`~~ | ~~Python~~ | ~~Dockerfile.conda 生成器（已过时）~~ | - | - | 🗑️ 已删除 |

### 2.3 依赖关系图

```
                    ┌─────────────────────────────────────────┐
                    │  lib/log.sh + lib/check_env.sh (共享库)  │
                    └────────────┬────────────────────────────┘
                                 │ source
        ┌────────────┬───────────┼───────────┬─────────────┐
        ▼            ▼           ▼           ▼             ▼
    build.sh   build-multistage  run.sh   export-image.sh  (build-conda.sh 未使用)
        │            │           │           │
        │            │           │           │
        ▼            ▼           ▼           ▼
    Dockerfile   Dockerfile   挂载源码    docker save
    (builder-dev) (runtime)   /workspace
                                 │
                    ┌────────────┴────────────┐
                    │  Dockerfile 内部阶段    │
                    │  base-system           │
                    │    └→ base-builder     │
                    │       └→ builder-dev   │
                    │       └→ builder       │
                    │          └→ pycaffe-builder
                    │          └→ runtime    │
                    └─────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │  Dockerfile.conda       │
                    │  caffe-cpu:builder (外部依赖)
                    │    └→ pycaffe-builder-conda
                    │    └→ runtime-conda    │
                    └─────────────────────────┘
```

---

## 第3章 · Dockerfile 分析

### 3.1 Dockerfile（Python 3.10 主 Dockerfile）

**6 个构建阶段**：

| 阶段 | 基础镜像 | 主要内容 | 用户 | UID/GID |
|------|---------|---------|------|---------|
| base-system | ubuntu:22.04 | apt 换源、CA 证书、基础工具 | root | - |
| base-builder | base-system | 编译工具链、Caffe 系统依赖、Python 3.10 + 科学计算包 | builder | 1000:1000 |
| builder-dev | base-builder | 复制 generate-makefile-config.sh 和 verify-caffe.sh | builder | 1000:1000 |
| builder | base-builder | 复制 caffex 源码，编译 Caffe（make all/pycaffe/tools/distribute） | builder | 1000:1000 |
| pycaffe-builder | base-builder | 从 builder 复制产物，用 scikit-build-core 构建 pycaffe wheel | builder | 1000:1000 |
| runtime | base-builder | 从 builder + pycaffe-builder 复制产物，安装 wheel 并验证 | builder | 1000:1000 |

**关键设计决策**：
- 使用 Ubuntu 22.04 系统自带 Python 3.10，避免 conda 开销
- protobuf 锁定 `3.20.3`（兼容 caffe.pb.h）
- numpy 限制 `<2.0`（兼容 Caffe 1.0）
- runtime 复用 base-builder 层（注释标注"后续可优化为独立最小运行时层"）

### 3.2 Dockerfile.conda（Python 3.14 Conda Dockerfile）

**2 个构建阶段**：

| 阶段 | 基础镜像 | 主要内容 | UID/GID |
|------|---------|---------|---------|
| pycaffe-builder-conda | caffe-cpu:builder | 安装 Miniforge3、创建 py314 环境、源码编译 Boost.Python、构建 pycaffe wheel | **1001:1001** |
| runtime-conda | caffe-cpu:builder | 安装 Miniforge3、创建 py314 环境、**再次**源码编译 Boost.Python、安装 wheel | **1001:1001** |

**关键技术决策**：
- conda-forge 无 cp314 构建，从源码编译 Boost 1.87.0 的 Boost.Python 组件
- 显式约束 `python_abi=*_cp314`（标准 GIL，非 free-threaded cp314t）
- 不安装 conda cxx-compiler，使用系统 g++ 11.4（与编译 libcaffe 一致，ABI 兼容）
- 不安装 conda protobuf，使用系统 C++ protobuf 3.12.4 + pip protobuf（`PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python`）
- Boost.Python 源码补丁：`->ob_refcnt` 替换为 `Py_REFCNT()` 宏（Python 3.14 兼容）

### 3.3 两份 Dockerfile 对比

| 维度 | Dockerfile | Dockerfile.conda |
|------|-----------|-----------------|
| Python 版本 | 3.10（系统） | 3.14（conda） |
| 基础镜像 | ubuntu:22.04 | caffe-cpu:builder（依赖 Dockerfile） |
| Boost.Python | apt 安装 libboost-all-dev | 源码编译 Boost 1.87.0 |
| protobuf | pip 3.20.3 | pip >=3.20,<6 + 纯 Python 实现 |
| 构建阶段数 | 6 | 2 |
| UID/GID | 1000:1000 | **1001:1001**（不一致） |
| 镜像标签 | caffe-cpu:latest/runtime | caffe-cpu:conda-py314 |
| runtime 体积 | 较大（含编译工具链） | 更大（含 Miniforge3 + Boost 源码编译产物） |

---

## 第4章 · 脚本功能分析

### 4.1 构建脚本

**build.sh（开发镜像构建入口）**：
- 默认目标 `builder-dev`，标签 `caffe-cpu:latest`
- 支持 `-t`/`-f`/`--target`/`--no-cache`/`--build-arg` 参数
- 复用 lib/log.sh 和 lib/check_env.sh，输出格式化日志
- 构建失败时输出排查建议（6 类常见原因）

**build/build-multistage.sh（runtime 镜像构建主脚本）**：
- 580 行，最复杂的构建脚本
- 支持 `--verify`/`--export`/`--compress`/`--verbose`/`--log-file`/`--jobs` 参数
- 阶段计时（declare -A 关联数组）、磁盘空间检查、已有镜像检查
- 构建日志同时输出到终端和文件（tee）
- 失败时自动分析日志中的 error 行

**build/build-conda.sh（Conda 镜像构建）**：
- **未使用共享库**（lib/log.sh, lib/check_env.sh）
- **版本号错误**：注释、RUNTIME_IMAGE、verify_inference 均使用 py313
- 支持 `--verify`/`--export`/`--target` 参数
- 缺少日志格式化和错误诊断

**build/export-image.sh（镜像导出）**：
- 支持 `--tag`/`--output`/`--compress` 参数
- 默认输出到 `docker/local/dist/`
- 复用共享库，输出导入命令提示

### 4.2 运行时脚本

**run.sh（开发容器启动）**：
- 挂载项目目录到 `/workspace`
- 设置 CAFFE_ROOT/PYTHONPATH/LD_LIBRARY_PATH 环境变量
- 支持 `-i`/`-n`/`--rm`/`--no-rm`/`--non-interactive` 参数
- 默认交互式 bash

**runtest.sh / test_new_features.sh（功能重叠）**：
- 两个脚本均激活 pycaffe-py314 环境
- 均测试 pycaffe 导入 + resize_image/oversample + LeNet
- test_new_features.sh 输出更详细，runtest.sh 更简洁
- **建议合并**

**entrypoint_test.sh（失效脚本）**：
- 引用 `/test_data_processor.py`（不存在）
- 引用 `python/pycaffe/test_pycaffe.py`（路径相对 /workspace）
- **建议删除或修复**

### 4.3 验证脚本

**scripts/verify-caffe.sh**：
- 6 步验证：环境→库文件→Python 依赖→Caffe 导入→Proto→Tools
- 被 Dockerfile runtime 阶段调用
- 使用 `python3` + `import caffe`（Python 3.10 路径）

**scripts/verify-runtime.sh**：
- 9 步完整验证：环境变量→挂载目录→编译产物→Python 依赖→Caffe 导入→Proto→Tools→LeNet 网络→总结
- **路径不一致**：引用 `/host-caffe` 挂载点，但 run.sh 挂载到 `/workspace`
- **包名不一致**：使用 `import caffe`，但 conda 镜像安装的是 `pycaffe`
- 未被任何 Dockerfile 或脚本自动调用

### 4.4 共享库

**lib/log.sh**：
- 9 个日志函数：log_header/log_section/log_step/log_info/log_warn/log_error/log_success/log_kv/log_blank/log_troubleshoot
- TTY 自动检测颜色（非 TTY 禁用）
- 时间戳格式：HH:MM:SS

**lib/check_env.sh**：
- 5 个检查函数：detect_container_tool/check_command/check_command_version/check_directory/check_file/check_docker_running/check_build_environment
- 优先检测 wslc，其次 docker
- check_build_environment 检查 make/cmake/python3 + docker

### 4.5 配置文件

**config/condarc**：
- 清华镜像源（channels: conda-forge + defaults）
- 超时配置：connect 60s / read 300s / retries 10
- **未被 Dockerfile.conda 使用**（Dockerfile.conda 直接 conda config 设置）

**config/pip.conf**：
- 阿里云镜像源
- **未被 Dockerfile 使用**（Dockerfile 通过 ENV PIP_INDEX_URL 设置）

---

## 第5章 · 问题清单

### 5.1 问题总览

| 优先级 | 数量 | 类别 | 已修复 |
|--------|------|------|--------|
| P0（阻断性） | 3 | 版本号错误、引用不存在文件 | ✅ 3/3 |
| P1（严重） | 4 | UID 不匹配、文档过时、重复编译 | ✅ 2/4 |
| P2（中等） | 6 | 注释错误、路径不一致、脚本重叠 | ✅ 1/6（1个设计豁免） |
| P3（优化） | 7 | 镜像体积、风格统一、CI 集成 | ⏳ 0/7 |

### 5.2 P0 问题（阻断性，必须立即修复）

#### P0-1: build-conda.sh Python 版本号错误（py313 vs py314） ✅ 已修复

- **文件**：`build/build-conda.sh`
- **现象**：
  - 第 2-3 行注释：`Python 3.13`
  - 第 23 行：`RUNTIME_IMAGE="caffe-cpu:conda-py313"`
  - 第 98 行：`echo "=== Verifying pycaffe inference (Python 3.13) ==="`
  - 第 102-105 行：`conda activate pycaffe-py313`
- **实际**：Dockerfile.conda 使用 Python 3.14，环境名 `pycaffe-py314`，镜像标签 `conda-py314`
- **影响**：build-conda.sh 构建的镜像标签与 Dockerfile.conda 不匹配，验证步骤会失败（激活不存在的 py313 环境）
- **修复**：全局替换 py313 → py314，RUNTIME_IMAGE 改为 `caffe-cpu:conda-py314`，conda activate 改为 `pycaffe-py314`
- **修复日期**：2026-07-24

#### P0-2: _check_proto.sh 和 _test_proto.sh 引用过时镜像名 ✅ 已修复

- **文件**：`build/_check_proto.sh`、`build/_test_proto.sh`
- **现象**：两脚本均引用 `caffe-cpu:conda-py313` 和 `pycaffe-py313` 环境
- **实际**：Dockerfile.conda 产出 `caffe-cpu:conda-py314`，环境名 `pycaffe-py314`
- **影响**：脚本无法运行（镜像不存在）
- **修复**：替换 `conda-py313` → `conda-py314`，`pycaffe-py313` → `pycaffe-py314`
- **修复日期**：2026-07-24

#### P0-3: entrypoint_test.sh 引用不存在的文件 ✅ 已修复（删除）

- **文件**：`entrypoint_test.sh`
- **现象**：第 7 行 `python /test_data_processor.py`
- **实际**：`/test_data_processor.py` 在镜像中不存在
- **影响**：脚本必然失败
- **修复**：删除该脚本（引用的测试文件不存在，脚本已失效）
- **修复日期**：2026-07-24

### 5.3 P1 问题（严重，短期修复）

#### P1-1: Dockerfile.conda UID/GID 与 builder 镜像不匹配 ✅ 已修复

- **文件**：`Dockerfile.conda`
- **现象**：
  - 第 35-36 行：`ARG BUILDER_UID=1001` / `ARG BUILDER_GID=1001`
  - 第 264-265 行（runtime-conda）：`ARG BUILDER_UID=1001` / `ARG BUILDER_GID=1001`
- **实际**：Dockerfile（builder 阶段）使用 `BUILDER_UID=1000` / `BUILDER_GID=1000`
- **影响**：基于 caffe-cpu:builder 时，builder 用户 UID=1000，但 Dockerfile.conda 声明 1001，导致 `${WORKSPACE_DIR}/caffex/build` 等复制产物所有权不匹配，可能引发权限错误
- **修复**：将 Dockerfile.conda 中所有 `BUILDER_UID=1001`/`BUILDER_GID=1001` 改为 `1000`/`1000`（两处均已修复）
- **修复日期**：2026-07-24

#### P1-2: _write_dockerfile.py 生成的 Dockerfile.conda 已过时 ✅ 已修复（删除）

- **文件**：`_write_dockerfile.py`
- **现象**：生成的 Dockerfile.conda：
  - 使用 `FROM condaforge/miniforge3:latest AS pycaffe-builder-conda`（实际用 `FROM caffe-cpu:builder`）
  - 使用 `conda create ... boost>=1.85 boost-cpp`（实际从源码编译）
  - 缺少 Python 3.14 兼容性补丁（ob_refcnt → Py_REFCNT）
  - 缺少 PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python 配置
  - 缺少 python_abi=*_cp314 约束
- **影响**：若误执行 `_write_dockerfile.py`，会覆盖手动维护的 Dockerfile.conda，导致 Python 3.14 构建失败
- **修复**：删除 `_write_dockerfile.py`（手动维护的 Dockerfile.conda 已包含复杂补丁，生成器无法覆盖）
- **修复日期**：2026-07-24

#### P1-3: runtime-conda 阶段重复编译 Boost.Python ⏳ 待修复（架构优化）

- **文件**：`Dockerfile.conda`
- **现象**：`pycaffe-builder-conda`（第 125-177 行）和 `runtime-conda`（第 328-370 行）均执行完整的 Boost.Python 源码编译
- **影响**：
  - 构建时间翻倍（Boost 编译约 5-10 分钟）
  - runtime-conda 镜像体积增大（含编译工具链残留）
  - 违反 DRY 原则
- **修复**：引入共享中间层 `boost-builder-conda`，编译一次 Boost.Python，两个阶段通过 `COPY --from=boost-builder-conda` 复用
- **备注**：此为架构级优化，需要重构 Dockerfile.conda 多阶段结构，建议在独立PR中处理

#### P1-4: RUNTIME_IMAGE_USAGE.md 目录结构文档不完整 ⏳ 待修复

- **文件**：`RUNTIME_IMAGE_USAGE.md`
- **现象**：目录结构仅列出 7 个文件，遗漏 9 个实际文件（修复后为7个文件）
- **影响**：文档与实际不一致，新协作者无法通过文档了解完整目录结构
- **修复**：更新目录结构章节，按"用户可见脚本"vs"开发调试脚本"分类，并反映已删除的文件

### 5.4 P2 问题（中等，中期修复）

#### P2-1: generate-makefile-config.sh 注释写错 Ubuntu 版本 ✅ 已修复

- **文件**：`scripts/generate-makefile-config.sh` 第 60 行
- **现象**：`# Makefile.config for BVLC Caffe - Auto-generated for Docker (Ubuntu 26.04)`
- **实际**：Dockerfile 使用 `ubuntu:22.04`
- **修复**：`26.04` → `22.04`
- **修复日期**：2026-07-24

#### P2-2: verify-runtime.sh 路径与 run.sh 不一致 ⏳ 待修复

- **文件**：`scripts/verify-runtime.sh`
- **现象**：引用 `/host-caffe` 挂载点（第 22-25, 88 行）
- **实际**：run.sh 挂载到 `/workspace`，CAFFE_ROOT=`/workspace/caffex`
- **影响**：verify-runtime.sh 无法在 run.sh 启动的容器中运行
- **修复**：`/host-caffe` → `/workspace`，或参数化挂载点路径

#### P2-3: verify-runtime.sh 包名不一致 ⏳ 待修复

- **文件**：`scripts/verify-runtime.sh` 第 50, 89 行
- **现象**：`import caffe`
- **实际**：Dockerfile.conda 安装的是 `pycaffe` 包（`pip install pycaffe`）
- **影响**：在 conda 镜像中运行会 ImportError
- **修复**：根据镜像类型选择 `import caffe`（Dockerfile）或 `import pycaffe`（Dockerfile.conda）

#### P2-4: runtest.sh 与 test_new_features.sh 功能重叠 ⏳ 待修复

- **文件**：`runtest.sh`、`test_new_features.sh`
- **现象**：两脚本均测试 pycaffe 导入 + resize_image/oversample + LeNet
- **影响**：维护负担加倍，修改时容易遗漏其一
- **修复**：合并为单一测试脚本，或明确分工（如 runtest.sh=快速冒烟，test_new_features.sh=详细回归）

#### P2-5: build-conda.sh 未使用共享库 ⏳ 待修复

- **文件**：`build/build-conda.sh`
- **现象**：未 source lib/log.sh 和 lib/check_env.sh，使用 echo 而非 log_info
- **影响**：日志风格不统一，缺少环境检查和错误诊断
- **修复**：source 共享库，替换 echo 为 log_* 函数

#### P2-6: _check_py314.sh 使用非正式环境名 ℹ️ 设计如此（豁免）

- **文件**：`_check_py314.sh` 第 4 行
- **现象**：`CONDA_PREFIX_PATH="/opt/conda/envs/py314test"`
- **实际**：正式环境名为 `pycaffe-py314`
- **分析**：该脚本以 `_` 前缀标识为开发调试脚本，使用独立的 `py314test` 环境是有意设计——用于在隔离环境中检查 Python 3.14 的 sysconfig 结构，避免污染正式的 `pycaffe-py314` 环境
- **结论**：设计合理，无需修改

### 5.5 P3 问题（优化，长期改进）

#### P3-1: runtime 镜像基于 base-builder 导致体积偏大

- **文件**：`Dockerfile` 第 288 行
- **现象**：`FROM base-builder AS runtime`
- **影响**：runtime 镜像包含编译工具链（build-essential/cmake/git/gdb/vim 等），体积约 2-3 GB
- **建议**：创建独立 `runtime-base` 阶段，仅包含运行时依赖（libatlas/libboost/libgflags/libglog/libhdf5 等），不含编译工具

#### P3-2: Dockerfile.conda 重复安装 Miniforge3

- **文件**：`Dockerfile.conda`
- **现象**：pycaffe-builder-conda（第 48-53 行）和 runtime-conda（第 277-282 行）均下载并安装 Miniforge3
- **影响**：下载两次（约 100MB），构建时间增加
- **建议**：引入 `conda-base` 共享阶段，安装一次 Miniforge3

#### P3-3: config/ 目录未被 Dockerfile 使用

- **文件**：`config/condarc`、`config/pip.conf`
- **现象**：Dockerfile 通过 ENV 设置 pip 镜像源，Dockerfile.conda 通过 conda config 设置 conda 镜像源，均未 COPY config/ 目录
- **影响**：config/ 目录成为死代码，维护者可能误以为已使用
- **建议**：在 Dockerfile 中 `COPY config/pip.conf /etc/pip.conf`，或删除 config/ 目录

#### P3-4: protobuf 版本约束不一致

- **文件**：`Dockerfile` vs `Dockerfile.conda`
- **现象**：
  - Dockerfile 第 118 行：`protobuf==3.20.3`（精确版本）
  - Dockerfile.conda 第 104, 317 行：`'protobuf>=3.20,<6'`（版本范围）
- **影响**：两份 Dockerfile 的 protobuf 版本策略不一致，可能引发行为差异
- **建议**：统一版本约束策略，或在注释中说明差异原因

#### P3-5: 缺少 CI/CD 集成配置

- **现象**：无 `.github/workflows/`、`Makefile`、`justfile` 等 CI/CD 入口
- **影响**：构建验证依赖手动执行，无法保证每次提交的镜像可构建性
- **建议**：添加 GitHub Actions 或 Makefile，至少验证 `./build.sh` 和 `./build/build-multistage.sh --target runtime`

#### P3-6: .gitignore 规则可能误导

- **文件**：`docker/local/conda/.gitignore`（`!build/`）、`docker/local/.gitignore`（`!lib/`）
- **现象**：使用 `!` 否定规则保留目录，但缺少父级忽略规则
- **影响**：规则可能无效（gitignore 否定规则需配合父级 `*` 或具体忽略规则）
- **建议**：明确忽略规则（如 `dist/`、`logs/`），或删除 .gitignore

#### P3-7: build-conda.sh 不支持 wslc 卷挂载

- **文件**：`build/build-conda.sh` 第 122-124 行
- **现象**：`echo "WARNING: wslc does not support volume mounts. Skipping wheel export."`
- **影响**：wslc 用户无法导出 wheel
- **建议**：使用 `wslc cp` 或其他方式替代卷挂载

---

## 第6章 · 改进建议与实施优先级

### 6.1 实施优先级矩阵

| 优先级 | 问题编号 | 行动项 | 验收标准 | 预期收益 | 状态 |
|--------|---------|--------|---------|---------|------|
| **P0** | P0-1 | 修复 build-conda.sh 版本号 py313→py314 | `./build-conda.sh --verify` 成功执行 | conda 构建链路可用 | ✅ 已完成 |
| **P0** | P0-2 | 修复 _check_proto.sh / _test_proto.sh 镜像名 | 两脚本可成功运行 | proto 测试可用 | ✅ 已完成 |
| **P0** | P0-3 | 删除失效的 entrypoint_test.sh | 文件已删除 | 消除失效脚本 | ✅ 已完成 |
| **P1** | P1-1 | 修复 Dockerfile.conda UID/GID 1001→1000 | runtime-conda 镜像构建无权限错误 | 消除权限风险 | ✅ 已完成 |
| **P1** | P1-2 | 删除 _write_dockerfile.py | 文件已删除，Dockerfile.conda 不受影响 | 消除覆盖风险 | ✅ 已完成 |
| **P1** | P1-3 | 引入 boost-builder-conda 共享阶段 | Boost.Python 仅编译一次，两阶段复用 | 构建时间减少 5-10 分钟 | ⏳ 待实施 |
| **P1** | P1-4 | 更新 RUNTIME_IMAGE_USAGE.md 目录结构 | 文档列出所有实际存在的文件 | 文档与实现一致 | ⏳ 待实施 |
| **P2** | P2-1 | 修复 generate-makefile-config.sh 注释 | 注释显示 Ubuntu 22.04 | 消除误导 | ✅ 已完成 |
| **P2** | P2-2 | 修复 verify-runtime.sh 路径 | 脚本可在 run.sh 容器中运行 | 验证脚本可用 | ⏳ 待实施 |
| **P2** | P2-3 | 修复 verify-runtime.sh 包名 | 支持 caffe/pycaffe 双模式 | 验证脚本通用 | ⏳ 待实施 |
| **P2** | P2-4 | 合并 runtest.sh 和 test_new_features.sh | 单一测试脚本覆盖所有用例 | 减少维护负担 | ⏳ 待实施 |
| **P2** | P2-5 | build-conda.sh 接入共享库 | 使用 log_info/log_error 替代 echo | 风格统一 | ⏳ 待实施 |
| **P2** | P2-6 | 修复 _check_py314.sh 环境名 | 使用 pycaffe-py314 | 测试环境一致 | ℹ️ 设计豁免 |
| **P3** | P3-1 | 创建独立 runtime-base 阶段 | runtime 镜像体积减少 30%+ | 镜像精简 | ⏳ 待规划 |
| **P3** | P3-2 | 引入 conda-base 共享阶段 | Miniforge3 仅下载一次 | 构建时间减少 | ⏳ 待规划 |
| **P3** | P3-3 | 清理或使用 config/ 目录 | config/ 被 COPY 或已删除 | 消除死代码 | ⏳ 待规划 |
| **P3** | P3-4 | 统一 protobuf 版本约束 | 两 Dockerfile 版本策略一致 | 行为一致 | ⏳ 待规划 |
| **P3** | P3-5 | 添加 CI/CD 配置 | 每次提交自动验证构建 | 质量保障 | ⏳ 待规划 |
| **P3** | P3-6 | 修复 .gitignore 规则 | 规则有效或已删除 | 消除误导 | ⏳ 待规划 |
| **P3** | P3-7 | build-conda.sh 支持 wslc 导出 | wslc 用户可导出 wheel | 功能完善 | ⏳ 待规划 |

### 6.2 实施路线图

```
阶段一（立即，P0）—— ✅ 已完成 2026-07-24:
  ├── ✅ 修复 build-conda.sh 版本号 (P0-1)
  ├── ✅ 修复 _check_proto.sh / _test_proto.sh 镜像名 (P0-2)
  └── ✅ 删除失效的 entrypoint_test.sh (P0-3)

阶段二（短期，P1）—— 🔶 部分完成:
  ├── ✅ 修复 Dockerfile.conda UID/GID (P1-1) [已完成]
  ├── ✅ 删除 _write_dockerfile.py (P1-2) [已完成]
  ├── ⏳ 引入 boost-builder-conda 共享阶段 (P1-3) [待实施-架构优化]
  └── ⏳ 更新 RUNTIME_IMAGE_USAGE.md (P1-4) [待实施]

阶段三（中期，P2）—— 🔶 部分完成:
  ├── ✅ 修复 generate-makefile-config.sh 注释 (P2-1) [已完成]
  ├── ℹ️ _check_py314.sh 环境名 (P2-6) [设计豁免]
  ├── ⏳ 修复 verify-runtime.sh 路径和包名 (P2-2/P2-3) [待实施]
  ├── ⏳ 合并 runtest.sh 和 test_new_features.sh (P2-4) [待实施]
  └── ⏳ build-conda.sh 接入共享库 (P2-5) [待实施]

阶段四（长期，P3）—— ⏳ 待规划:
  ├── 创建独立 runtime-base 阶段 (P3-1)
  ├── 引入 conda-base 共享阶段 (P3-2)
  ├── 清理 config/ 目录 (P3-3)
  ├── 统一 protobuf 版本约束 (P3-4)
  ├── 添加 CI/CD 配置 (P3-5)
  ├── 修复 .gitignore 规则 (P3-6)
  └── build-conda.sh 支持 wslc 导出 (P3-7)
```

---

## 第7章 · 系统性问题洞察

### 7.1 洞察1：文档-实现一致性漂移

**现象**：RUNTIME_IMAGE_USAGE.md 的目录结构与实际不符，遗漏 9 个文件。

**根因**：文档在目录结构演进时未同步更新。文档作者倾向于记录"用户应使用的入口"，而忽略了开发调试脚本（`_*.sh`、`test_*.sh`），但这些文件确实存在于目录中。

**可复用模式**：
- **文档-实现一致性检查清单**：每次目录结构变更后，执行 `ls -R` 对比文档中的目录树
- **脚本分类标注**：在文档中明确区分"用户入口脚本"vs"开发调试脚本"，前者进文档，后者标注为内部使用

### 7.2 洞察2：版本号分散声明导致漂移

**现象**：Python 版本号（3.13 vs 3.14）在多个文件中分散声明：
- Dockerfile.conda：`python=3.14`、`CONDA_ENV=pycaffe-py314`
- build-conda.sh：`py313`（错误）
- _check_proto.sh：`py313`（错误）
- _test_proto.sh：`py313`（错误）

**根因**：版本号作为字面量散落在脚本中，无单一真相源。Python 版本从 3.13 升级到 3.14 时，Dockerfile.conda 已更新但配套脚本未同步。

**可复用模式**：
- **版本号集中声明模式**：在 Dockerfile 顶部 `ARG PYTHON_VERSION=3.14`，脚本通过 `docker build --build-arg` 或环境变量传递，避免字面量散落
- **版本号一致性检查脚本**：`grep -r "py3[0-9][0-9]" docker/local/` 定位所有版本号引用

### 7.3 洞察3：多阶段构建的中间层复用缺失

**现象**：Dockerfile.conda 中 `pycaffe-builder-conda` 和 `runtime-conda` 两个阶段各自独立完成：
- 下载并安装 Miniforge3
- 创建 conda Python 3.14 环境
- 从源码编译 Boost.Python（含下载、解压、补丁、bootstrap、b2 install）

**根因**：两阶段基于同一基础镜像 `caffe-cpu:builder`，但未提取共享的 Boost.Python 编译步骤为独立阶段。

**可复用模式**：
- **多阶段构建共享中间层模式**：当多个阶段需要相同的复杂构建步骤（如源码编译）时，提取为独立阶段（如 `boost-builder-conda`），其他阶段通过 `COPY --from=boost-builder-conda` 复用产物
- **判断标准**：若两个阶段的 RUN 指令有超过 5 行重复且涉及下载/编译，应提取共享层

---

## 第8章 · 风险评估

| 风险 | 概率 | 影响 | 缓解措施 | 状态 |
|------|------|------|---------|------|
| build-conda.sh 执行失败 | ~~高~~ → 已消除 | 中 | ✅ 已修复版本号（P0-1） | ✅ 已缓解 |
| _write_dockerfile.py 误执行覆盖 Dockerfile.conda | ~~低~~ → 已消除 | 高 | ✅ 已删除该脚本（P1-2） | ✅ 已缓解 |
| UID/GID 不匹配导致权限错误 | ~~中~~ → 已消除 | 高 | ✅ 已统一为 1000:1000（P1-1） | ✅ 已缓解 |
| Boost.Python 编译失败（Python 3.14 兼容性） | 中 | 高 | 已有 ob_refcnt 补丁，关注 Boost 上游更新 | ⚠️ 存在 |
| conda-forge 镜像源不可用 | 低 | 中 | 已配置重试 3 次 + 清华镜像源 | ⚠️ 存在 |
| 镜像体积过大影响分发 | 中 | 低 | P3-1 创建独立 runtime-base | ⏳ 待规划 |
| 文档误导新协作者 | 中 | 中 | P1-4 更新目录结构文档 | ⏳ 待修复 |
| verify-runtime.sh 路径/包名不一致导致验证失败 | 中 | 低 | P2-2/P2-3 修复路径和包名 | ⏳ 待修复 |

---

## 第9章 · 总结

### 9.1 整体评价

`docker/local` 目录实现了一套功能完整的 Caffe Docker 镜像构建系统，支持 Python 3.10（系统）和 Python 3.14（conda）双轨并行，包含开发、构建、运行时、验证、导出全流程脚本。共享 Shell 函数库（log.sh/check_env.sh）设计良好，日志格式统一。

主要不足在于**版本号一致性管理**（P0 问题集中在此）和**文档-实现同步**（P1-4）。这些是典型的"单点修改未联动"问题，通过引入版本号集中声明和文档一致性检查可系统性解决。

### 9.2 修复执行总结（2026-07-24）

**已完成修复（6项）**：
- ✅ **P0 全部修复**（3项）：build-conda.sh 版本号、proto 测试脚本镜像名、删除失效 entrypoint_test.sh
- ✅ **P1 部分修复**（2项）：Dockerfile.conda UID/GID 统一为 1000、删除过时的 _write_dockerfile.py
- ✅ **P2 部分修复**（1项）：generate-makefile-config.sh 注释修正为 Ubuntu 22.04
- ℹ️ **P2-6 设计豁免**：_check_py314.sh 使用 py314test 独立测试环境是合理设计

**修复效果**：
- 消除了所有 P0 阻断性问题，conda 构建链路版本号一致性已恢复
- 消除了 UID/GID 权限不匹配风险
- 消除了 _write_dockerfile.py 意外覆盖 Dockerfile.conda 的风险
- 删除了 2 个失效/过时文件，目录更清洁

**待完成工作（13项）**：
- P1 剩余 2 项（Boost.Python 共享层、文档更新）
- P2 剩余 4 项（verify-runtime 路径/包名、脚本合并、共享库接入）
- P3 全部 7 项（镜像优化、CI/CD 等长期改进）

### 9.3 建议优先执行

1. **~~立即修复 P0 三项~~** ✅ 已完成（2026-07-24）
2. **~~短期修复 P1 中高优先级项~~** 🔶 UID/GID 和生成器已修复，剩余 Boost 共享层和文档待实施
3. **中期推进 P2 剩余四项**（verify-runtime 修复、脚本合并、风格统一）
4. **长期规划 P3 七项**（镜像精简、CI/CD）

### 9.4 可复用模式沉淀

本次复盘萃取的 3 个系统性模式（文档-实现一致性检查、版本号集中声明、多阶段共享中间层）已具备跨场景通用性，建议沉淀至 `docs/retrospective/patterns/` 模式库。
