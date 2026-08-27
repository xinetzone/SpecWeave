---
type: Concept
title: "视角155：Wheel 分发包"
description: "分析 tvm-ffi 的 Wheel 分发包构建，包括 cibuildwheel 多平台矩阵、scikit-build-core 打包内容、动态库随包分发、平台架构与用户下载预测。"
tags:
  - build
  - wheel
  - packaging
  - cibuildwheel
generated: 2026-08-23
verified: true
status: draft
sources:
  - facts: F-329, F-330, F-331
  - code:
    - pyproject.toml
    - .github/workflows/publish_wheel.yml
    - python/tvm_ffi/libinfo.py
---

# 视角155：Wheel 分发包

## 概述

Wheel 分发包是 tvm-ffi 面向 Python 生态交付的标准形态。它以 `pyproject.toml` 的 `[tool.cibuildwheel]` 与 `.github/workflows/publish_wheel.yml` 为驱动，将 CMake 编译的共享库与 Cython 扩展、纯 Python 模块一起打成可安装的 Wheel，实现"开箱即用"的二进制分发。逐版本（非 abi3）标签与多平台架构矩阵是其两大特征。

## 打包内容

`[tool.scikit-build]` 的 `wheel.packages = ["python/tvm_ffi"]` 声明刀包内 Python 包目录（`pyproject.toml:146`）。CMake 会将 `tvm_ffi_shared` 动态库安装到 `lib/`，Python 则通过 `libinfo` 的 `RECORD` 探测定位（见视角154），最终共享库作为包数据随 Wheel 一起进入 `python/tvm_ffi` 下的 `lib`，从而让 `import tvm_ffi` 时 ctypes 能直接加载，无需用户另行设置 `LD_LIBRARY_PATH`。

## cibuildwheel 矩阵

`[tool.cibuildwheel]`（`pyproject.toml:249-270`）定义构建矩阵：

- **Python 版本**：`build = ["cp39-*", ..., "cp313-*", "cp314-*", "cp314t-*"]`，覆盖 CPython 3.9 至 3.14 及自由线程 cp314t（`pyproject.toml:253`）。因扩展按逐版本 ABI 构建，每个版本产出一个独立 Wheel。
- **平台跳过与测试**：`skip = ["*musllinux*"]`；`test-skip` 使 cp39-cp311 复用 cp312 测试（`pyproject.toml:254-256`）。
- **架构**：Linux 为 `x86_64, aarch64`，macOS 为 `x86_64, arm64`，Windows 为 `AMD64`（`pyproject.toml:261-270`）。
- **Windows 修复**：`repair-wheel-command = "delvewheel repair ..."`（`pyproject.toml:270`），使用 delvewheel 修复依赖 DLL，将共享库一并嵌入目标 wheel。
- **构建前端**：`build-frontend = "build[uv]"`（`pyproject.toml:257`）。
- **测试命令**：`pytest {package}/tests/python -vvs`（`pyproject.toml:258`），在构建产物上跑 python 测试套件。

## 发布工作流

`.github/workflows/publish_wheel.yml` 定义"手动触发"发布（`workflow_dispatch`，`publish_wheel.yml:20-26`），矩阵覆盖 ubuntu（x86_64, manylinux_2_28）、ubuntu-24.04-arm（aarch64）、windows（AMD64）、macos-14（arm64）（`publish_wheel.yml:32-37`）。构建出的 Wheel 由 `actions/upload-artifact` 收集（`publish_wheel.yml:53-62`），最终经 `pypa/gh-action-pypi-publish` 发布到 PyPI，并用 `actions/attest-build-provenance` 生成构建溯源证明（`publish_wheel.yml:81-88`）。

## 用户侧安装体验

Wheel 免去了用户自行编译 C 的步骤：`python -m pip install apache-tvm-ffi` 即可获得与目标平台/版本匹配的二进制。由于 Wheel 自带 `libtvm_ffi.so`/`.dll`，`libinfo._find_library_by_basename` 的 RECORD 探测路径（`libinfo.py:280-295`）能直接命中，实现"装完即用"。这与源代码构建 + 编译 + `LD_LIBRARY_PATH` 的传统 workflow 形成鲜明对比。

## 设计分析

Wheel 分发包的设计价值在于把"编译问题"从用户端转移到分发端：cibuildwheel 在托管平台矩阵上离线完成各平台/各 Python 版本的编译，用户仅按配置拉取对应 Wheel。逐版本非 abi3 标签虽增加了 Wheel 数量，却换来对自由线程 Python 与完整 Python C API 的支持；delvewheel/manylinux 处理则保证动态库依赖在 Wheel 内自洽。这种"分发端重、消费端轻"的模式符合成熟二进制分发生态的主流实践。

## NPU建议

针对 NPU 场景的 Wheel 分发包，建议：

1. **NPU 专用 Wheel/额外索引**：NPU 厂商内核（自带 device 库）与 tvm-ffi 基础 Wheel 版本强耦合。建议 tvm-ffi 保持"无设备依赖"的干净基础 Wheel，将 NPU 设备相关二进制（算子库、驱动 so/dll）拆到独立扩展包，避免把厂商私有二进制塞入公共 PyPI Wheel。

2. **平台矩阵扩展与设备库检测**：NPU Wheel 建议按目标设备架构细化架构交叉（如新增 `aarch64-npu` 或对应 SOC 架构），利用 `cibuildwheel` 的 `archs` 配置与平台 `repair` 步骤，将与 NPU 深度绑定且无法 `pip repair` 的动态库显式纳入 Wheel 并校验存在性。

3. **协议版本与固件协商**：NPU Wheel 内建议同时放入「基础 tvm-ffi ABI 版本 + NPU 设备固件版本」的元数据；安装后由 `libinfo` 探测并在运行时经版本查询 API 校验，避免 Wheel 与设备固件升级错位。

4. **构建溯源与合规**：对 NPU 相关 Wheel 建议沿用 `attest-build-provenance` 的溯源机制，并明确 license/export control 分类；设备接近底层、安全敏感，构建证明尤其重要。

5. **测试矩阵覆盖设备**：cibuildwheel 的 `test-command` 目前只跑 CPU 测试。建议 NPU 场景新增 GPU 锁机制（参考 `tvm_ffi.testing.run_with_gpu_lock`）串行化设备测试，在发布前对目标 NPU 架构跑冒烟测试。

## 相关概念

- [004 共享库目标](154-shared-library-target.md)：Wheel 内动态库的定位
- [006 One Wheel 策略](156-one-wheel-strategy.md)：打包产物取舍
- [007 多 Python 版本支持](157-multi-python-version.md)：cp39-cp314/t 矩阵
- [008 依赖管理](158-dependency-management.md)：运行期依赖与分组