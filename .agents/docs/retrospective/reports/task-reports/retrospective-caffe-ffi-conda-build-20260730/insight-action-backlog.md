---
id: "retrospective-caffe-ffi-conda-build-20260730-backlog"
title: "洞察行动项 Backlog：caffe-ffi Conda 包构建验证"
date: 2026-07-30
version: "1.4"
type: insight-action-backlog
status: active
source: "caffe-ffi Conda 包构建验证复盘"
ssot:
  retrospective_source: README.md
  insight_source: README.md#s3-洞察与模式萃取
  verification_plan: l4-verification-plan-and-checklist.md
---
# 洞察行动项 Backlog

> 本文件记录从 caffe-ffi Conda 包构建验证复盘中转化的可执行行动项。核心包含：**6项已完成改进**（editable三重保护、跨包RPATH、符号验证、参数隔离、单元测试、模式沉淀）+ 1项取消（绝对路径RPATH不可行）+ 1项搁置（meta.yaml注释）+ 1项🔄进行中（macOS/Windows跨平台L1+L2 Docker交叉编译完成，L3待CI/真机/Wine）。
>
> 📋 **相关文档**：[L4升级验证计划与Checklist表格](l4-verification-plan-and-checklist.md) — 包含模式升级到L4所需的20个补充测试场景和可复制到任务追踪系统的Checklist表格。

## 行动项总览

| ID | 行动项 | 优先级 | 类型 | 状态 | 预期收益 |
|----|--------|--------|------|------|---------|
| ACT-001 | build.sh增加`_editable_*`自动清理，实现三重保护策略 | 🔴高 | 质量门禁 | ✅ 已完成 | 彻底消除editable残留干扰，确保验证环境干净 |
| ACT-002 | meta.yaml增加`missing_dso_whitelist`详细注释 | 🟡中 | 文档 | ⏸️ 搁置 | 其他开发者理解DSO白名单用途，降低维护成本 |
| ACT-003 | ~~RPATH改用`$PREFIX/lib`绝对路径~~ | 🟡中 | 健壮性 | ❌ 已取消 | 绝对路径触发conda-build prefix replacement "Placeholder too short"错误，方案不可行 |
| ACT-003b | 为每个依赖.so单独计算RPATH深度，添加`$ORIGIN/../tvm_ffi/lib`跨包路径 | 🟡中 | 健壮性 | ✅ 已完成 | 不同深度的.so都能正确解析依赖，无需LD_LIBRARY_PATH |
| ACT-004 | macOS/Windows conda包支持（`@rpath`/`@loader_path`+install_name_tool+Docker交叉编译） | 🔴高 | 跨平台 | 🔄 L1+L2已通过Docker交叉编译解决（L3待CI/真机/Wine） | macOS/Windows用户可直接使用conda包，开发阶段无需macOS/Windows开发机 |
| ACT-005 | 将洞察/模式萃取为正式模式文档存入patterns/ | 🟡中 | 知识沉淀 | ✅ 已完成 | 模式可复用，其他scikit-build-core项目受益 |
| ACT-006 | build.sh增加关键符号nm验证步骤（TVMFFIGetCustomAllocator） | 🟡中 | 健壮性 | ✅ 已完成 | 防止pip wheel符号缺失导致运行时崩溃 |
| ACT-007 | 嵌套构建时CMAKE_ARGS/SKBUILD_CMAKE_ARGS参数隔离 | 🟡中 | 健壮性 | ✅ 已完成 | conda参数不污染子项目独立构建 |
| ACT-008 | 验证脚本集成Python单元测试（CAFFE_FFI_DISABLE_BACKTRACE=1） | 🟡中 | 质量门禁 | ✅ 已完成 | 一键验证包含单元测试，防止C++ backtrace在pytest中崩溃 |

---

## 🔴 高优先级行动项

### ACT-001：build.sh增加`_editable_*`自动清理步骤，实现三重保护策略 ✅ 已完成

- **优先级**：🔴 高
- **来源**：复盘 §S3 洞察3 — Editable Install 残留的三重保护清理策略
- **责任人**：caffe-ffi conda recipe 维护者
- **预期收益**：在有 editable install 残留的开发容器中，验证脚本也能正确加载 conda 包，避免误判；系统性解决PEP 660 editable残留问题
- **状态**：✅ **已完成**（2026-07-30，v1.1）
- **验收标准（DoD）**：
  1. ✅ build.sh内置`clean_editable_files()`函数，tvm-ffi安装后、caffe-ffi安装后各执行一次（双重保险）
  2. ✅ test-conda-build.sh实现`clean_editable_residuals(pkg_name)`函数，Step 1b预清理 + Step 7a安装前彻底清理
  3. ✅ 清理函数同时处理：`_editable_skbc_*.pth/.py`、`__editable__.*.pth`、`__pycache__`缓存、指向源码路径的.pth、pip的`direct_url.json`、stale包目录
  4. ✅ Step 8a0 路径验证门禁：`__file__`必须包含`site-packages/caffe_ffi`，否则直接fail
  5. ✅ 在有editable残留的环境中运行脚本，验证能正确通过（首次运行清理所有残留，二次运行环境已干净）
- **涉及文件**：
  - [conda.recipe/build.sh](../../../../../../projects/xuanspace/libs/caffe-ffi/conda.recipe/build.sh#L20-L34)（clean_editable_files函数，两次调用）
  - [scripts/test-conda-build.sh](../../../../../../apps/caffe-ffi-jupyter/scripts/test-conda-build.sh#L29-L70)（clean_editable_residuals函数，Step 1b+7a）
  - [scripts/test-conda-build.sh](../../../../../../apps/caffe-ffi-jupyter/scripts/test-conda-build.sh#L294-L302)（Step 8a0 路径验证门禁）

---

## 🟡 中优先级行动项

### ACT-002：meta.yaml增加`missing_dso_whitelist`详细注释 ⏸️ 搁置

- **优先级**：🟡 中
- **来源**：复盘 §S1 修改文件清单 — meta.yaml missing_dso_whitelist 已有简单注释但不够详细
- **责任人**：caffe-ffi conda recipe 维护者
- **预期收益**：其他维护者能快速理解哪些库是 vendored/bundled、为什么需要白名单，避免误删白名单导致构建失败
- **状态**：⏸️ **搁置**（2026-07-30，用户指示暂时搁置）
- **搁置原因**：用户指示暂时搁置，优先执行ACT-005模式沉淀
- **验收标准（DoD）**：
  1. `missing_dso_whitelist` 段上方有块注释说明用途（全相对RPATH不需要prefix replacement、vendored库由patchelf处理）
  2. 为每个白名单条目添加行内注释说明原因（libtvm_ffi是本地编译bundled、libopenblas/libprotobuf是conda依赖由RPATH解析）
- **涉及文件**：
  - [conda.recipe/meta.yaml](../../../../../../projects/xuanspace/libs/caffe-ffi/conda.recipe/meta.yaml#L14-L18)
- **实施步骤**：
  1. 在 `missing_dso_whitelist:` 上方添加块注释：
     ```yaml
     # DSO whitelist: these libraries are resolved via $ORIGIN-relative RPATH at runtime.
     # detect_binary_files_with_prefix is false because all RPATHs use $ORIGIN (no absolute prefix paths),
     # so conda-build's binary prefix replacement is not needed and would cause "Placeholder too short" errors.
     ```
  2. 为每个白名单条目添加行内注释

### ACT-003：~~将RPATH `$ORIGIN/../../..`改为`$PREFIX/lib`绝对路径~~ ❌ 已取消

- **优先级**：~~🟡 中~~ → ❌ 取消
- **来源**：复盘 v1.0 最初建议
- **取消原因**：
  - 实测使用`${PREFIX}/lib`绝对路径会触发conda-build的prefix replacement机制
  - conda-build会尝试将构建时的PREFIX路径（如`/opt/conda/envs/caffe-ffi`）替换为安装时的PREFIX路径
  - RPATH字符串长度超过placeholder长度限制（默认256字符），导致"Placeholder too short"构建错误
  - **正确方案**：使用全`$ORIGIN`相对路径，精确计算每个.so的上溯级数（见ACT-003b）
- **替代方案**：ACT-003b

### ACT-003b：为每个依赖的.so单独计算并设置RPATH（考虑目录嵌套深度），添加`$ORIGIN/../tvm_ffi/lib`跨包路径 ✅ 已完成

- **优先级**：🟡 中
- **来源**：复盘 §S3 洞察4 — 跨包RPATH依赖的层级计算模型
- **责任人**：caffe-ffi 构建系统维护者
- **预期收益**：不同深度的共享库都能通过相对RPATH正确找到依赖；无需依赖LD_LIBRARY_PATH；跨包依赖（如同级tvm_ffi/lib/）也能正确解析
- **状态**：✅ **已完成**（2026-07-30，v1.1）
- **验收标准（DoD）**：
  1. ✅ _caffe_ffi.so RPATH: `$ORIGIN:$ORIGIN/lib:$ORIGIN/../tvm_ffi/lib:$ORIGIN/../../..`（深度3，跨包路径指向tvm_ffi/lib）
  2. ✅ libtvm_ffi.so RPATH: `$ORIGIN:$ORIGIN/..:$ORIGIN/../../../../`（深度4，因在tvm_ffi/lib/下深一级）
  3. ✅ 构建后patchelf --print-rpath验证RPATH正确
  4. ✅ ldd检查所有依赖解析，无not found
  5. ✅ 注释明确说明禁止使用绝对路径的原因
- **涉及文件**：
  - [conda.recipe/build.sh](../../../../../../projects/xuanspace/libs/caffe-ffi/conda.recipe/build.sh#L169-L190)（RPATH配置，含禁止绝对路径注释）
  - [conda.recipe/build.sh](../../../../../../projects/xuanspace/libs/caffe-ffi/conda.recipe/build.sh#L285-L315)（patchelf设置两个.so的RPATH）
- **关键发现**：
  - RPATH层级计算：从.so所在目录到PREFIX/lib需要的`..`个数
  - _caffe_ffi.so在`caffe_ffi/`：caffe_ffi/ → site-packages/ → python3.14/ → lib/ = 3级`..`
  - libtvm_ffi.so在`tvm_ffi/lib/`：lib/ → tvm_ffi/ → site-packages/ → python3.14/ → lib/ = 4级`..`

### ACT-006：build.sh中增加关键符号nm验证步骤 ✅ 已完成

- **优先级**：🟡 中
- **来源**：复盘 §S3 洞察6 — 预编译Wheel的符号完整性验证
- **责任人**：caffe-ffi 构建系统维护者
- **预期收益**：避免PyPI wheel缺少关键符号（如TVMFFIGetCustomAllocator）导致运行时custom allocator功能失效；链接时不报错但运行时才崩溃的问题提前在构建阶段发现
- **状态**：✅ **已完成**（2026-07-30，v1.1）
- **验收标准（DoD）**：
  1. ✅ tvm-ffi安装后立即用`nm -D`验证TVMFFIGetCustomAllocator为T符号（全局文本段）
  2. ✅ patchelf设置RPATH后再次验证符号存在
  3. ✅ 本地源码编译tvm-ffi优先，SETUPTOOLS_SCM_PRETEND_VERSION=0.1.13绕过git describe问题
  4. ✅ 构建前清理tvm-ffi in-tree构建残留，确保全新编译
- **涉及文件**：
  - [conda.recipe/build.sh](../../../../../../projects/xuanspace/libs/caffe-ffi/conda.recipe/build.sh#L136-L145)（tvm-ffi安装后符号验证）
  - [conda.recipe/build.sh](../../../../../../projects/xuanspace/libs/caffe-ffi/conda.recipe/build.sh#L277-L283)（RPATH设置后再次符号验证）
- **关键教训**：pip安装的apache-tvm-ffi 0.1.12 wheel缺少TVMFFIGetCustomAllocator符号，导致运行时失败；必须本地源码编译+符号验证

### ACT-007：嵌套构建时CMAKE_ARGS/SKBUILD_CMAKE_ARGS参数隔离 ✅ 已完成

- **优先级**：🟡 中
- **来源**：复盘 §S3 洞察5 — 嵌套构建时的CMAKE_ARGS隔离机制
- **责任人**：caffe-ffi 构建系统维护者
- **预期收益**：conda-build注入的CMAKE_ARGS（含CMAKE_INSTALL_PREFIX等）不会污染tvm-ffi等依赖的独立构建；子项目使用自己的CMake配置
- **状态**：✅ **已完成**（2026-07-30，v1.1）
- **验收标准（DoD）**：
  1. ✅ tvm-ffi构建前保存`_OLD_CMAKE_ARGS`和`_OLD_SKBUILD_CMAKE_ARGS`
  2. ✅ 清空CMAKE_ARGS，仅追加tvm-ffi需要的特定参数（-DTVM_FFI_USE_LIBBACKTRACE=OFF）
  3. ✅ tvm-ffi构建完成后恢复原始CMAKE_ARGS和SKBUILD_CMAKE_ARGS
  4. ✅ caffe-ffi构建前同样隔离CMAKE_ARGS，设置独立的SKBUILD_CMAKE_ARGS
- **涉及文件**：
  - [conda.recipe/build.sh](../../../../../../projects/xuanspace/libs/caffe-ffi/conda.recipe/build.sh#L87-L119)（tvm-ffi构建参数隔离+恢复）
  - [conda.recipe/build.sh](../../../../../../projects/xuanspace/libs/caffe-ffi/conda.recipe/build.sh#L175-L235)（caffe-ffi构建参数隔离+恢复）

### ACT-008：验证脚本集成Python单元测试步骤 ✅ 已完成

- **优先级**：🟡 中
- **来源**：复盘 §S3 洞察7 — C++栈回溯在pytest环境中的崩溃问题
- **责任人**：caffe-ffi 验证脚本维护者
- **预期收益**：一键构建验证包含单元测试，功能验证更完整；默认禁用C++ backtrace防止pytest环境崩溃
- **状态**：✅ **已完成**（2026-07-30，v1.1）
- **验收标准（DoD）**：
  1. ✅ test-conda-build.sh Step 8d集成Python单元测试运行
  2. ✅ 测试前设置`CAFFE_FFI_DISABLE_BACKTRACE=1`环境变量
  3. ✅ 测试失败时直接fail，不继续
  4. ✅ 测试文件路径：tests/python/test_python_api.py
- **涉及文件**：
  - [scripts/test-conda-build.sh](../../../../../../apps/caffe-ffi-jupyter/scripts/test-conda-build.sh#L398-L418)（Step 8d 单元测试）
- **关键发现**：C++层`backtrace_symbols()`在pytest环境处理Python栈帧会崩溃，必须默认禁用

### ACT-005：将洞察/模式萃取为正式模式文档存入patterns/ ✅ 已完成

- **优先级**：🟡 中
- **来源**：复盘 §S3 模式1和模式2（升级版L3成熟度）+ 新增洞察3-7
- **责任人**：方法论维护者
- **预期收益**：其他使用 conda-build + scikit-build-core 的项目可直接参考模式，避免重复踩坑
- **状态**：✅ **已完成**（2026-07-30，v1.1）
- **验收标准（DoD）**：
  1. ✅ 创建模式文档 [conda-build-scikit-build-core-native.md](../../../patterns/code-patterns/conda-build-scikit-build-core-native.md)（升级版L3）
     - 位置：`.agents/docs/retrospective/patterns/code-patterns/`（归类为code-patterns，因包含大量具体代码模板）
     - 包含：触发场景、五层陷阱分析、conda-build三段式依赖表、六步法完整流程、build.sh/meta.yaml代码模板、RPATH深度计算公式、符号验证标准、6个反模式、12项检验标准、完整test脚本模板、迁移示例
  2. ✅ 创建模式文档 [conda-package-clean-verification.md](../../../patterns/code-patterns/conda-package-clean-verification.md)（升级版L3）
     - 位置：`.agents/docs/retrospective/patterns/code-patterns/`
     - 包含：触发场景、四类假成功陷阱、PEP 660 editable四件套残留分析、五维验证法、editable清理函数、路径验证门禁、ldd+nm双重依赖检查、backtrace环境配置、全量单元测试规范、6个反模式、10项检验标准、快速验证命令清单、迁移示例
  3. ✅ 更新 patterns/code-patterns/README.md 索引，添加两个新L3模式条目
  4. ✅ 两个模式均标注成熟度 L3 方法论，包含完整反模式清单和检验标准
- **涉及文件**：
  - [conda-build-scikit-build-core-native.md](../../../patterns/code-patterns/conda-build-scikit-build-core-native.md)（新建，L3，501行）
  - [conda-package-clean-verification.md](../../../patterns/code-patterns/conda-package-clean-verification.md)（新建，L3，507行）
  - [code-patterns/README.md](../../../patterns/code-patterns/README.md#L86-L87)（更新索引，新增2行）

---

## 🟢 低优先级行动项

### ACT-004：macOS/Windows conda 包支持 🔄 L1+L2 Docker交叉编译已解决（L3待CI/真机/Wine）

- **优先级**：🔴 高（从🟢低升级，因Docker方案大幅降低跨平台验证门槛）
- **来源**：复盘 §S2 瓶颈与约束
- **责任人**：caffe-ffi 跨平台维护者
- **预期收益**：macOS/Windows 用户可通过 conda 直接安装 caffe-ffi；**开发阶段无需macOS/Windows开发机或CI**，L1编译+L2静态验证可在Linux Docker中完成
- **状态**：🔄 **L1+L2已通过Docker交叉编译解决（L3待CI/真机/Wine）**（2026-07-30 v1.4）
- **已完成工作（代码层+Docker交叉编译）**：
  1. ✅ build.sh 添加平台检测（`uname -s`），自动识别 Linux/macOS
  2. ✅ 跨平台工具函数封装：`get_rpath()`/`set_rpath()`/`check_symbol()`/`check_deps()`/`fix_dep_ref()`
     - Linux: `patchelf` + `$ORIGIN` + `ldd` + `nm -D`
     - macOS: `install_name_tool` + `@loader_path` + `otool -L` + `nm -gU`
     - Windows: 无RPATH机制，使用DLL搜索路径+`llvm-objdump`/`llvm-nm`
  3. ✅ RPATH前缀按平台选择（`$ORIGIN` vs `@loader_path` vs Windows无RPATH），深度计算逻辑复用
  4. ✅ macOS额外处理：`install_name_tool -change`修复libtvm_ffi引用、设置install name id
  5. ✅ Windows适配：meta.yaml条件依赖、.pyd/.dll DSO白名单、DLL导入表验证
  6. ✅ **Docker跨平台交叉编译方案实现**（apps/caffe-ffi-cross/）：
     - 利用conda-forge交叉编译工具链（clang_osx-64、clang_win-64等）在Linux容器中编译macOS/Windows包
     - L1编译验证：conda-build成功生成目标平台包文件 ✅
     - L2静态验证：使用cctools(file/otool/nm)/llvm-objdump验证二进制格式、架构、符号、依赖 ✅
     - L3运行时验证：Windows可用Wine+Windows Miniconda做smoke test；macOS需CI/真机
  7. ✅ meta.yaml 更新支持交叉编译（cross-python_{{ target_platform }}、build_platform条件判断）
  8. ✅ test-conda-build.sh 添加平台检测（osx-64/osx-arm64/win-64）、跨平台工具函数封装、Bootstrap自适应
- **待执行（验证层 - L3运行时）**：
  1. ⏳ macOS L3：在CI或macOS真机（Intel/Apple Silicon）上运行smoke test
  2. ⚠️ Windows L3：Wine smoke test可选（验证基本import和函数调用），最终仍需Windows实机/CI
  3. ❓ 验证RPATH `@loader_path` 在macOS实机的实际效果（是否能正确解析跨包依赖）
  4. ❓ 验证Windows DLL搜索路径配置（是否需要额外PATH设置或conda activation脚本）
- **验收标准（DoD）**：
  1. ✅ L1编译：Docker交叉编译成功生成macOS/Windows conda包
  2. ✅ L2静态：Mach-O/PE格式验证通过、依赖检查无not found、关键符号存在
  3. ⏳ L3运行：macOS CI/真机验证通过；Windows Wine/实机验证通过
  4. ✅ RPATH使用平台适配方案（Linux: `$ORIGIN`、macOS: `@loader_path`、Windows: 无RPATH）
  5. ✅ 跨包依赖：`@loader_path/../tvm_ffi/lib`等相对路径在macOS正确；Windows DLL搜索路径正确
- **Docker方案位置**：apps/caffe-ffi-cross/
  - 使用方式：`cd apps/caffe-ffi-cross && ./run.sh`（一键测试所有平台）
  - 支持单独平台：`./run.sh macos` / `./run.sh windows --no-wine`
  - docker compose profile：`docker compose --profile macos run --rm macos-cross`
- **前置依赖**：ACT-003b RPATH设计已稳定
- **涉及文件**：
  - [build.sh](../../../../../../projects/xuanspace/libs/caffe-ffi/conda.recipe/build.sh)：跨平台适配（平台检测+工具函数+RPATH前缀+依赖修复）
  - [meta.yaml](../../../../../../projects/xuanspace/libs/caffe-ffi/conda.recipe/meta.yaml)：macOS/Windows条件依赖、交叉编译配置、DSO白名单
  - [test-conda-build.sh](../../../../../../apps/caffe-ffi-jupyter/scripts/test-conda-build.sh)：跨平台适配（平台检测+Bootstrap自适应+otool/nm/llvm-objdump封装+符号验证）
  - apps/caffe-ffi-cross/：Docker交叉编译方案（Dockerfile、docker-compose.yml、run.sh、交叉编译recipe）

---

## 行动项依赖关系

```
ACT-001（editable三重保护）── 独立可执行，无需前置依赖 ✅
    │
    └── 为 ACT-003b 的RPATH验证提供干净环境基础 ✅

ACT-002（meta.yaml注释）── 独立可执行，文档改进无代码依赖 ⏳

ACT-003（绝对路径RPATH）── ❌ 已取消（方案不可行）
    │
    └── 替代为 ACT-003b（相对路径RPATH深度计算）✅

ACT-003b（跨包RPATH）── 依赖ACT-001干净环境 ✅
    │
    └── 为 ACT-004 macOS支持提供RPATH设计基础

ACT-006（符号验证）── 独立可执行 ✅
ACT-007（参数隔离）── 独立可执行 ✅
ACT-008（单元测试）── 独立可执行，依赖backtrace禁用发现 ✅

ACT-004（macOS/Windows支持）── 依赖 ACT-003b 的RPATH设计基础 🔄（L1+L2 Docker交叉编译完成，L3待CI/真机/Wine）

ACT-005（模式沉淀）── 建议在所有代码改进完成后沉淀
    （包含最终版本的最佳实践L3模式，而非中间状态）⏳
```

---

## 完成追踪

| ID | 状态 | 完成日期 | 验证结果 |
|----|------|---------|---------|
| ACT-001 | ✅ 已完成 | 2026-07-30 | 三重保护策略实现：build.sh内置clean_editable_files()两次调用 + test脚本Step1b预清理+Step7a彻底清理；Step8a0路径验证门禁；清理覆盖.pth+.py+pyc+direct_url.json+stale目录 |
| ACT-002 | ⏳ 待执行 | - | - |
| ACT-003 | ❌ 已取消 | 2026-07-30 | 绝对路径触发"Placeholder too short"错误，不可行；替代方案ACT-003b已完成 |
| ACT-003b | ✅ 已完成 | 2026-07-30 | _caffe_ffi.so（深度3）和libtvm_ffi.so（深度4）RPATH独立设置；新增$ORIGIN/../tvm_ffi/lib跨包路径；ldd全部解析无not found |
| ACT-004 | 🔄 进行中（L1+L2完成） | 2026-07-30 | Docker跨平台交叉编译方案实现（apps/caffe-ffi-cross/）：L1编译+L2静态验证在Linux Docker中完成；macOS L3需CI/真机，Windows L3可用Wine做smoke test；前置依赖"macOS/Windows开发机或CI"已解决 |
| ACT-005 | ⏳ 待执行 | - | - |
| ACT-006 | ✅ 已完成 | 2026-07-30 | nm -D验证TVMFFIGetCustomAllocator为T符号（安装后+RPATH设置后两次验证）；本地源码优先编译；SETUPTOOLS_SCM_PRETEND_VERSION处理版本问题 |
| ACT-007 | ✅ 已完成 | 2026-07-30 | tvm-ffi构建和caffe-ffi构建均实现CMAKE_ARGS/SKBUILD_CMAKE_ARGS保存/清空/恢复隔离；子项目参数不被conda污染 |
| ACT-008 | ✅ 已完成 | 2026-07-30 | test-conda-build.sh Step 8d集成单元测试；CAFFE_FFI_DISABLE_BACKTRACE=1防止pytest崩溃；测试失败直接fail |

**完成率**：5/8 已完成，1/8 已取消，1/8 进行中（L1+L2 Docker交叉编译完成，L3待验证），1/8 搁置（文档注释）

---

## 快速执行参考

```bash
# ACT-001/003b/006/007/008: 一键验证所有已完成改进
cd /path/to/caffe-ffi-jupyter
docker exec caffe-ffi-jupyter bash /SpecWeave/apps/caffe-ffi-jupyter/scripts/test-conda-build.sh
# 观察输出：
#   - Step 1b: Pre-cleaned N editable residual file(s)
#   - Step 7a: Cleaned N editable residual file(s)
#   - Step 8a0: PASS Loading from conda site-packages
#   - Step 8c: PASS All shared library dependencies resolved
#   - Step 8c: PASS libtvm_ffi.so correctly linked
#   - Step 8d: PASS Python unit tests PASSED

# ACT-003b: 验证RPATH在安装后的实际值（深度计算）
docker exec caffe-ffi-jupyter bash -c "
  source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi &&
  CAFFE_SO=\$(python -c 'import caffe_ffi, glob, os; print(glob.glob(os.path.join(os.path.dirname(caffe_ffi.__file__), \"_caffe_ffi*.so\"))[0]') &&
  TVM_SO=\$(python -c 'import tvm_ffi, os; print(os.path.join(os.path.dirname(tvm_ffi.__file__), \"lib\", \"libtvm_ffi.so\"))') &&
  echo '_caffe_ffi.so RPATH:' && patchelf --print-rpath \$CAFFE_SO &&
  echo 'libtvm_ffi.so RPATH:' && patchelf --print-rpath \$TVM_SO &&
  echo 'ldd check:' && ldd \$CAFFE_SO | grep 'not found' && echo FAIL || echo PASS
"

# ACT-006: 验证TVMFFIGetCustomAllocator符号
docker exec caffe-ffi-jupyter bash -c "
  source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi &&
  TVM_SO=\$(python -c 'import tvm_ffi, os; print(os.path.join(os.path.dirname(tvm_ffi.__file__), \"lib\", \"libtvm_ffi.so\"))') &&
  echo 'Symbol check:' && nm -D \$TVM_SO | grep TVMFFIGetCustomAllocator && echo 'PASS: symbol found' || echo 'FAIL: symbol missing'
"

# ACT-002: 查看当前 meta.yaml missing_dso_whitelist
cat projects/xuanspace/libs/caffe-ffi/conda.recipe/meta.yaml | grep -A10 "missing_dso"

# ACT-004: Docker跨平台交叉编译（L1+L2验证）
cd apps/caffe-ffi-cross

# 一键测试所有平台（macOS+Windows）
./run.sh

# 仅macOS交叉编译+静态验证
./run.sh macos

# 仅Windows（跳过Wine smoke test）
./run.sh windows --no-wine

# 或使用docker compose
docker compose --profile macos run --rm macos-cross
docker compose --profile windows run --rm win-cross

# 验证产物格式（在容器内或提取后）
# macOS: file检查Mach-O格式
file $CONDA_PREFIX/caffe-ffi/_caffe_ffi*.so
# 预期: Mach-O 64-bit x86_64 bundle

# Windows: file检查PE格式
file $CONDA_PREFIX/caffe-ffi/_caffe_ffi*.pyd
# 预期: PE32+ executable (DLL) x86-64, for MS Windows
```

**行动项总结**：v1.4版本共8项行动项，其中🔴高优先级ACT-001已完成（三重保护editable清理），ACT-004（macOS/Windows跨平台支持）L1+L2层已通过Docker交叉编译方案解决（apps/caffe-ffi-cross/），开发阶段无需macOS/Windows开发机或CI；🟡中优先级6项中，ACT-003b/005/006/007/008已完成（跨包RPATH、模式沉淀、符号验证、参数隔离、单元测试），ACT-003已取消（绝对路径不可行），ACT-002（meta.yaml注释）搁置；核心构建验证闭环已完成，跨平台L1+L2验证已解决，剩余为L3运行时验证（macOS需CI/真机，Windows可用Wine做smoke test）和文档完善。
