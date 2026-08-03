# XMNN (xmtools) 全面复盘报告

**复盘日期**: 2026-08-03
**复盘对象**: `d:\spaces\SpecWeave\external\chaos\xmtools`
**方法论**: 七概念方法论编排（R→I→E→V→A→C）
**复盘类型**: 里程碑复盘 + 构建/打包/部署闭环
**Session**: `sc-20260803-xmnn-retrospective`

---

## 一、复盘范围与目标

本复盘针对 XMNN NPU 推理工具包（xmtools）进行系统性审视，覆盖：

- **代码结构审查**：pyproject.toml / CMakeLists.txt / tasks.py / docker 三层镜像 / scripts / sdk 工具
- **功能模块评估**：构建链路、Nuitka 打包、wheel 组装、镜像体系、SDK CLI、验证体系
- **潜在问题识别**：按 P0/P1/P2 分级
- **性能优化建议**：镜像体积、wheel 体积、构建耗时、运行时加载

复盘完成后执行两类交付操作：
1. whl 打包为符合 Python 标准的安装包
2. 构建并导出生产级 Docker 镜像

---

## 二、执行环境确认（R 阶段前置）

| 检查项 | 结果 |
|---|---|
| 已有 wheel | `dist/xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`（177MB，2026-07-27 构建） |
| WSL Docker | 可用（Docker 29.6.1） |
| 兄弟目录 | `npu_tvm`、`npuusertools` 存在 |
| 构建镜像 | `xmnn-dev:llvm22`（2.07GB 内容） |
| 运行时镜像 | `xmnn:1.2.1-alpha`（1.35GB 内容） |
| miniconda.sh | dev-llvm22 目录存在（197MB） |

---

## 三、事实清单（R 阶段产出，F-xxx，无因果词）

> 质量门 G1：事实阶段不包含因果推断词，纯客观描述。

### 3.1 构建配置（pyproject.toml）

- **F-001**: `pyproject.toml` 使用 `scikit-build-core` 作为 PEP 517 构建后端，`build-system.requires` 声明 `scikit-build-core>=0.5`、`cmake>=3.18`、`ninja>=1.10`
- **F-002**: 项目名 `xmnn`，版本 `1.2.1-dev0`，`requires-python = ">=3.14"`
- **F-003**: 核心依赖共 19 项：numpy、scipy、pandas、matplotlib、Pillow、onnx、protobuf、openpyxl、tabulate、rich、tqdm、tomlkit、decorator、attrs、psutil、cloudpickle、typing_extensions、pytest、telnetlib3
- **F-004**: 可选依赖组 4 个：`dev`（pytest/build/scikit-build-core）、`examples`（opencv-python-headless）、`torch`（torch/torchvision/onnx2pytorch）、`full`（聚合）
- **F-005**: `[tool.scikit-build]` 配置 `cmake.build-type="Release"`、`wheel.install-dir="."`、`cmake.source-dir="."`

### 3.2 CMake 安装规则（CMakeLists.txt）

- **F-006**: 入口校验 Python 版本，`<3.14` 触发 `FATAL_ERROR`
- **F-007**: 配置路径变量：`NUITKA_OUTPUT_DIR`、`TVM_BUILD_DIR`、`TVM_ROOT_DIR`、`XMN_PYTHON_DIR`、`LLVM_LIB_DIR`、`XMN_NUITKA_OUT`
- **F-008**: 第 39-55 行存在一段被注释掉的 `xmnn` 源码安装块（dead code，历史遗留）
- **F-009**: 安装 `_xmnn_bootstrap.py` 与 `xmnn_bootstrap.pth` 到 wheel 根目录 `.`
- **F-010**: 安装 Nuitka 编译产物 `tvm.cpython-*.so`、`vta.cpython-*.so`、`xmnn.cpython-*.so` 到 wheel 根目录
- **F-011**: 安装 `libtvm.so` 到 `_libs/` 目录
- **F-012**: `install_real_lib` 函数将 LLVM 依赖（libLLVM.so.22.1、libz.so.1、libzstd.so.1、libxml2.so.16、libiconv.so.2、libicuuc.so.78、libicudata.so.78）解析 REALPATH 后安装到 `_libs/` 并创建符号链接
- **F-013**: VTA 仿真库 `libvta_fsim*.so` 安装到 `_libs/`
- **F-014**: 数据目录 `autolibs`、`tools_cpp`、`fonts` 从 `${XMN_PYTHON_DIR}/xmnn/` 安装到 `xmnn/<dname>`，使用 `USE_SOURCE_PERMISSIONS`
- **F-015**: `vta_hw/config` 安装到 `vta_hw/`，`tvm/relay/std` 的 `.rly` 文件安装到 `tvm/relay/`
- **F-016**: 使用 `patchelf --set-rpath '$ORIGIN'` 对 `_libs/*.so*` 设置 RPATH
- **F-017**: 对 `xmnn/tools_cpp/bin/` 下所有文件执行 `chmod +x`

### 3.3 构建任务链（tasks.py）

- **F-018**: `build_all` 的依赖链为 `clean → build_tvm → nuitka_tvm → nuitka_vta → nuitka_xmnn → build_wheel`
- **F-019**: `_inject_preamble` 将 bootstrap 代码注入 `tvm/vta/xmnn` 的 `__init__.py`，备份为 `.bak_xmnn`
- **F-020**: bootstrap 包含 Python 3.14 AST 兼容补丁（NameConstant/Num/Str/Bytes/Index/ExtSlice）
- **F-021**: `nuitka_tvm` 使用 `--include-data-dir=relay/std`，`nuitka_vta` 使用 `--include-data-dir=vta_hw/config`，`nuitka_xmnn` 无数据目录参数
- **F-022**: `build_wheel` 通过 `python -m build --config-setting=cmake.define.*` 传递路径变量
- **F-023**: `verify` 任务选择 `dist/` 最新 wheel，调用 `scripts/verify_wheel.py` 在临时 venv 中验证

### 3.4 Docker 镜像体系（docker/**）

- **F-024**: 三层镜像：`dev-llvm22`（构建）→ `runtime`（用户部署）→ `serve`（REST API）
- **F-025**: dev-llvm22 基于 `ubuntu:26.04`，Conda 安装 `llvm=22.1`、`clang=22.1`、`lld=22.1`、`cmake`、`ninja`、`python=3.14` 及 19 个数据科学依赖
- **F-026**: dev-llvm22 pip 安装 `torch/torchvision`（CPU，带 `--index-url`）、`nuitka`、`invoke`、`build`、`scikit-build-core`、`auditwheel` 等
- **F-027**: dev-llvm22 配置北外 conda-forge 镜像 + `default_channels: []`，清华 PyPI 镜像
- **F-028**: dev-llvm22 设置 `TZ=Asia/Shanghai`、`LLVM_CONFIG`、`CC/CXX=clang`、`PIP_USER=0`、`CCACHE_DIR=/workspace/.ccache`
- **F-029**: runtime 基于 `ubuntu:26.04`，Conda 安装 `python=3.14+numpy+scipy`，pip 安装 `pytest+opencv-python-headless`
- **F-030**: runtime 安装 wheel 后注册 `_libs` 到 `/etc/ld.so.conf.d/xmnn.conf` 并 `ldconfig`
- **F-031**: runtime `ENTRYPOINT []`、`CMD python -c "import tvm..."`，`TZ=Asia/Shanghai`
- **F-032**: `run-build.sh` 在容器内 patch pyproject.toml（移除 cmake/ninja 的 requires 与版本），复用系统 cmake/ninja
- **F-033**: `run-build.sh` 的 Nuitka 命令额外 `--nofollow-import-to=torch/torchvision/onnx2pytorch`

### 3.5 验证体系（scripts/**）

- **F-034**: `verify_wheel.py` 创建临时 venv，安装 wheel，执行 8 项功能检查 + auditwheel 合规检查
- **F-035**: 检查项覆盖 import tvm/vta/xmnn、relay、libtvm 加载、relay/std、vta_hw/config、tvm.build(llvm)
- **F-036**: `verify-wheel.sh` 在容器内执行 9 项测试（import/_libs/libtvm/tvm.build/relay.std/.pth/数据目录）
- **F-037**: runtime 的 `verify_xmnn.py` 检查 15 个模块版本 + 可选 torch/onnx2pytorch + _libs + libtvm + libLLVM + tvm.build + xmnn API + bootstrap.pth

### 3.6 SDK 工具（sdk/**）

- **F-038**: `sdk/tools/` 含 6 个 CLI：compile/accuracy/infer/performance/bandwidth/excelreport
- **F-039**: 6 个 CLI 均为薄封装，仅转发 `-n <model_name>` 到对应的 `xmnn.*_api` 函数
- **F-040**: `sdk/models/` 按 `caffe/onnx/pytorch/two_inputs` 分类存放模型配置
- **F-041**: `sdk/test_sdk_tools.py`、`run_e2e_test.py` 为 SDK 测试脚本

### 3.7 仓库状态（git）

- **F-042**: `models/` 子模块与 `.gitmodules` 处于 untracked（`??`）状态
- **F-043**: `sdk/models/`、`sdk/tools/` 下有已修改文件（非本次变更，属历史既有状态）

---

## 四、洞察（I 阶段产出，四元组）

> 质量门 G2：每条洞察包含 陈述/证据/反常识/行动 四元组。

### I-01 构建配置与执行脚本存在双轨不一致

- **陈述**: pyproject.toml 声明 `build-system.requires` 含 cmake/ninja，但 `run-build.sh` 通过 sed 移除两者并改用系统 cmake/ninja。
- **证据**: F-001（requires 含 cmake/ninja）与 F-032（run-build.sh patch 移除）并存。
- **反常识**: 构建声明与执行脚本互相矛盾，同一份 wheel 存在两种"正确"构建路径。
- **行动**: 统一构建策略——以 `--no-isolation` 系统工具为准，清理 pyproject 中 cmake/ninja 的 requires 声明（或保留但明确隔离构建），消除双轨。

### I-02 wheel 体积受 libLLVM 主导但未做裁剪

- **陈述**: wheel 约 177MB，其中 `libLLVM.so.22.1` + `libtvm.so` 为体积主因。
- **证据**: F-012（安装 libLLVM.so.22.1 等 7 个 LLVM 依赖到 _libs）、F-015（wheel 总 177MB）。
- **反常识**: 运行时仅需 LLVM 的 JIT 代码生成能力，却整体打包完整 libLLVM（数百 MB 级）。
- **行动**: 评估裁剪 libLLVM 组件（仅保留 CodeGen/Optimize 所需），或使用 `--strip` 减小符号表；作为 P2 优化项。

### I-03 顶层 `_libs` 目录污染全局 site-packages

- **陈述**: `_libs/` 安装到 site-packages 根目录（非包内），runtime 镜像进一步将其注册到系统 ld.so.conf。
- **证据**: F-011（安装到 `_libs/`）、F-030（runtime 注册到 `/etc/ld.so.conf.d/xmnn.conf`）。
- **反常识**: 全局动态库路径注册可能与其他包的同名 `.so` 冲突，且污染系统链接器搜索路径。
- **行动**: 评估将 `_libs` 收敛到包内（如 `xmnn/_libs`），依赖 `$ORIGIN` RPATH 而非全局 ldconfig；作为 P1 审查项。

### I-04 数据目录曾因 Nuitka 嵌入方案丢失（已修复）

- **陈述**: 历史版本 wheel 缺失 autolibs/tools_cpp/fonts 三目录，现已通过"CMake 安装 + 权限保留"修复。
- **证据**: BUILD_REPORT.md 记录 RC1/RC2/RC3 三根因；F-014（CMake 安装 + USE_SOURCE_PERMISSIONS）、F-017（chmod +x）。
- **反常识**: `--include-data-dir` 嵌入 `.so` 的方案对可执行文件/动态库无效，需真实文件系统路径。
- **行动**: 保留"数据目录由 CMake 安装"的既有方案，并在验证清单中持续覆盖（Test 9）。

### I-05 镜像构建存在重复造轮子风险

- **陈述**: dev-llvm22 与 runtime 各自下载 Miniconda + Python 3.14 + 依赖，无公共基础镜像复用。
- **证据**: F-025（dev 自建环境）、F-029（runtime 自建环境），两者 Dockerfile 大量重复（.condarc/时区/工具链初始化）。
- **反常识**: 可提炼 `jupyter-ssh-base` 式公共基础镜像，避免重复下载与一致性偏差。
- **行动**: 作为 P2 优化项，评估提炼公共 Miniconda 基础镜像。

---

## 五、潜在问题清单（P0/P1/P2 分级）

### P0（阻断性，需修复）

- **P0-1**: **CMakeLists.txt 存在历史遗留死代码块**（L39-55 被注释的 xmnn 源码安装段）。无用配置增加维护负担，可能误导后续维护者认为该路径仍生效。
- **P0-2**: **构建配置双轨不一致**（见 I-01）。pyproject 声明 cmake/ninja 下载，run-build.sh 却依赖系统工具，属隐性依赖，易在非 Docker 环境复现失败。

### P1（重要，建议修复）

- **P1-1**: **顶层 `_libs` + 全局 ldconfig 污染**（见 I-03）。生产镜像中 `_libs` 全局注册存在动态库冲突风险。
- **P1-2**: **dev 镜像无条件安装 torch/torchvision**（F-026），与 wheel 的 `torch` 可选依赖声明不一致，非必要场景下徒增镜像体积（dev 镜像 2.07GB）。
- **P1-3**: **runtime 镜像安装 opencv-python-headless**（F-029），但该包仅 `examples` 可选依赖引用，非核心运行时必需，增加部署体积。

### P2（优化项，择机处理）

- **P2-1**: **wheel 体积裁剪**（见 I-02），libLLVM 组件化/符号裁剪。
- **P2-2**: **公共基础镜像复用**（见 I-05），dev/runtime 提炼公共 Miniconda 层。
- **P2-3**: **版本号 `1.2.1-dev0`** 含 dev 后缀，正式发布建议用规范版本号。
- **P2-4**: **wheel 标签为 `linux_x86_64` 而非 `manylinux`**，auditwheel 仅 show 未 repair，跨发行版可移植性受限。
- **P2-5**: **`nuitka_tvm` 的 `--include-data-dir` 与 CMake 安装 relay/std 存在重复**（F-015/F-021），数据可能被嵌入 .so 又单独安装，需确认无重复或冲突。

---

## 六、性能优化建议

### 6.1 镜像体积优化

| 优化项 | 现状 | 建议 | 预期收益 |
|---|---|---|---|
| dev 镜像移除 torch/torchvision | 2.07GB | 默认不装，按需 `--build-arg` | 减 ~1GB |
| runtime 移除 opencv-python-headless | 运行时依赖 | 移除，由 `xmnn[examples]` 按需安装 | 减 ~50MB |
| 提炼公共基础镜像 | 两套独立构建 | 复用同一 Miniconda 层 | 减少重复下载与层数 |
| conda clean + pip 无缓存 | 已部分配置 | 确认所有镜像 `--no-cache-dir` + `conda clean -ya` | 减少 ~数百 MB |

### 6.2 Wheel 体积优化

| 优化项 | 现状 | 建议 | 预期收益 |
|---|---|---|---|
| libLLVM 裁剪 | 完整打包 | 仅保留 JIT 所需组件（libLLVMCodeGen/Optimal） | 减 50-100MB |
| 符号表裁剪 | 未 strip | `patchelf --strip` 或 strip 非导出符号 | 减 10-30% |
| auditwheel repair | 仅 show | 执行 `auditwheel repair` 生成 manylinux 包 | 提升可移植性 |

### 6.3 构建耗时优化

- **F-028** 已配置 `CCACHE_DIR=/workspace/.ccache`，TVM 重新编译可复用缓存。
- **ninja** 并行构建已启用，`nuitka --remove-output` 减少中间产物。
- 建议：Nuitka 阶段可考虑 `--jobs` 并行，减少单模块编译串行等待。

### 6.4 运行时加载优化

- bootstrap 已预加载 `libtvm.so`（F-020 的 TVM_LIBRARY_PATH + ctypes.CDLL）。
- 建议：将 `_libs` 收敛到包内并依赖 `$ORIGIN` RPATH，减少运行时对全局链接器路径的依赖，提升加载确定性。

---

## 七、质量门通过记录

| 质量门 | 判定 | 说明 |
|---|---|---|
| G1（事实无因果词） | ✅ 通过 | F-001~F-043 均为客观描述 |
| G2（洞察四元组） | ✅ 通过 | I-01~I-05 均含陈述/证据/反常识/行动 |
| G3（模式可迁移） | ✅ 通过 | 见 insight-extraction.md，含触发/步骤/反模式/检验/迁移 |
| G4（行动项原子化） | ✅ 通过 | 见 actionable-items.md，含优先级/Owner/验收标准 |

---

## 八、交付物清单

| 交付物 | 路径 | 状态 |
|---|---|---|
| 综合复盘报告 | `README.md`（本文件） | ✅ |
| 模式萃取 | `insight-extraction.md` | ✅ |
| 行动项清单 | `actionable-items.md` | ✅ |
| whl 打包 | 见阶段 3 章节（另行执行） | 待执行 |
| Docker 镜像导出 | 见阶段 4 章节（另行执行） | 待执行 |

---

## 九、结论

XMNN xmtools 项目已形成一套完整的三层镜像 + Nuitka 打包 + wheel 交付体系，核心功能（import tvm/vta/xmnn、tvm.build、数据目录、SDK CLI）经多轮验证稳定。本复盘识别出 2 个 P0、3 个 P1、5 个 P2 问题，核心矛盾集中在**构建配置双轨不一致**与**动态库/镜像体积的工程化平衡**。后续修复与打包/镜像操作详见 actionable-items.md 与阶段 3/4 执行章节。