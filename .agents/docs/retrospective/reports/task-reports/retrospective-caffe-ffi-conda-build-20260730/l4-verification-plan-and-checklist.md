---
id: "retrospective-caffe-ffi-conda-build-20260730-l4-verification"
title: "模式 L4 升级验证计划与 Checklist"
date: 2026-07-30
version: "1.0"
type: verification-plan
source: "caffe-ffi Conda 包构建验证复盘"
related_patterns:
  - "../../patterns/code-patterns/conda-build-scikit-build-core-native.md"
  - "../../patterns/code-patterns/conda-package-clean-verification.md"
---

# 模式 L4 升级验证计划与 Checklist

> 本文档包含两部分：(1) 两个L3模式升级到L4需要补充的测试场景与验证计划；(2) 两个模式的检验标准Checklist表格，可直接复制到任务追踪系统使用。

---

## Part 1：L4 升级验证计划

当前两个模式均为 **L3 方法论**（双案例验证，完成闭环验证）。升级到 **L4 标准化** 需要满足：≥3个独立项目成功复用、跨平台验证通过、有自动化CI集成示例、有反例防御验证。

### 模式A：conda-build-scikit-build-core-native L4升级计划

**当前状态**：L3（caffe-ffi + tvm-ffi 双案例验证，仅Linux x86_64）

#### 需要补充的测试场景

| 编号 | 测试场景 | 验证目标 | 优先级 | 前置依赖 | 预计工作量 |
|------|---------|---------|--------|---------|-----------|
| A-T1 | **macOS平台构建验证** | `@loader_path`/`@rpath`替代`$ORIGIN`的语法正确性；`install_name_tool`替代`patchelf`设置RPATH；otool -L依赖检查 | 🔴高 | macOS开发机或CI | 1天 |
| A-T2 | **Windows平台构建验证** | 无RPATH机制下，conda包如何正确查找依赖DLL；PATH环境变量配置；Dependencies工具替代ldd | 🔴高 | Windows开发机或CI | 2天 |
| A-T3 | **多架构Linux验证** | aarch64（ARM64）、ppc64le架构下patchelf行为一致性；RPATH相对路径是否跨架构通用 | 🟡中 | QEMU或ARM硬件 | 1天 |
| A-T4 | **nanobind项目复用验证** | 使用nanobind而非pybind11的项目是否适用（不同的构建后端配置） | 🟡中 | 找一个nanobind的conda recipe | 0.5天 |
| A-T5 | **纯C扩展项目复用验证** | 使用Cython/CAPI而非pybind11的项目是否适用 | 🟡中 | 找一个Cython的conda recipe | 0.5天 |
| A-T6 | **conda-build 25.x兼容性测试** | 新版conda-build（≥25.x）对scikit-build-core的原生支持情况；是否可简化某些步骤 | 🟡中 | conda-forge CI | 0.5天 | ✅ 调研完成 |
| A-T7 | **pyproject.toml配置验证** | 通过`[tool.scikit-build]`配置cmake参数，减少build.sh手动操作的可行性 | 🟢低 | 实验分支 | 1天 | ✅ 完成 |
| A-T8 | **多级嵌套依赖验证** | A包依赖B包，B包依赖C包（三级跨包依赖）的RPATH设置 | 🟢低 | 构造测试案例 | 1天 |
| A-T9 | **conda-forge feedstock PR验证** | 将模式应用到conda-forge的真实feedstock，提交PR验证通过CI | 🔴高 | conda-forge账号 | 2天 |
| A-T10 | **反模式防御验证** | 故意违反每个反模式，验证构建确实会失败（证明反模式清单的准确性） | 🟡中 | 构造故障注入测试 | 1天 |

> **📌 A-T6 调研结论（2026-07-30）**：基于 conda-build 25.x/26.x 官方 CHANGELOG 调研（25.1.x-26.5.0），核心发现如下：
>
> **1. scikit-build-core 原生支持：不存在**
> conda-build 25.x-26.x **没有**对 scikit-build-core 的特殊原生支持。构建仍然通过标准 PEP 517 build backend 机制（`pip install --no-build-isolation` 或 `python -m build`）调用 scikit-build-core。conda-build 26.x 的主要新增是 **rattler-build v1 recipe**（`recipe.yaml` 格式）支持，而非对特定 build backend 的集成。
>
> **2. 影响当前模式的关键变更（需要适配）**
>
> | conda-build版本 | 变更类型 | 影响 | 适配建议 |
> |---|---|---|---|
> | 25.3.0 | ⚠️ 限制 | `Limit patchelf to <0.18`（patchelf≥0.18有兼容性问题） | meta.yaml 中 `patchelf # [linux]` 无需 pin 版本，conda-build 自动约束 |
> | 25.4.0 | ✅ 简化 | conda-build 自动强制 pip install 选项（`--no-deps`/`--no-build-isolation`/`--ignore-installed`），不需手动设置 | build.sh 中 pip install 可简化；但为向后兼容建议保留显式参数 |
> | 25.11.0 | ⚠️ 变更 | 移除 Python 3.9 支持（最低 3.10）；CMake 4 generator 兼容性更新 | caffe-ffi 使用 Python 3.14 不受影响；CMake 参数需兼容 CMake 4 |
> | 26.1.0 | ✅ macOS修复 | macOS 上 `Delete rpath before adding rpath` 避免 RPATH 空间不足错误 | ACT-004 macOS 适配在 26.1.0+ 更可靠；旧版本需先删后加 |
> | 26.3.0 | ⚠️ 变更 | Python 3.14 tarfile 兼容；要求 `conda >=25.11.0` | Python 3.14 环境需 conda ≥25.11 |
> | 26.5.0 | ⚠️ 重命名 | `missing_dso_whitelist`→`missing_dso_allowlist`（deprecation，27.3 移除） | meta.yaml 中建议同时保留两个 key 做向前兼容 |
>
> **3. build.sh 可简化点**
> - conda-build 25.4.0+ 自动管理 pip install 选项，`pip install --no-deps --no-build-isolation --ignore-installed .` 可简化为 `pip install .`
> - 但为兼容 conda-build <25.4 用户，建议保留显式参数或加版本条件判断
>
> **4. v1 recipe 格式（recipe.yaml）**
> - conda-build 26.3+ 支持 rattler-build 的 v1 recipe 格式（YAML 替代 meta.yaml），但语法完全不同，需要 `py-rattler-build` 包，不建议当前迁移
>
> **5. 验证状态**
> - ✅ 文档调研完成（25.1.x-26.5.0 CHANGELOG 全量审查）
> - ❌ 实机构建验证待执行（需 Docker/CI 环境安装 conda-build 25.x/26.x 运行构建）
> - ❌ 建议在 conda-forge feedstock PR 中自动测试多版本兼容性

> **📌 A-T7 实践结论（2026-07-30）**：通过 `[tool.scikit-build.cmake.define]` + `[[tool.scikit-build.overrides]]` 将项目通用CMake参数迁移到pyproject.toml，build.sh的SKBUILD_CMAKE_ARGS从12个参数精简为5个（仅保留conda运行时相关参数）。
>
> **1. 迁移原则：三层分离**
>
> | 层 | 位置 | 包含参数 | 原因 |
> |---|---|---|---|
> | 项目默认值 | `pyproject.toml [tool.scikit-build.cmake.define]` | BUILD_TYPE、CPU_ONLY、USE_BLAS、BUILD_TESTS、SKIP_BUILD_RPATH、BUILD_WITH_INSTALL_RPATH、POSITION_INDEPENDENT_CODE、INSTALL_RPATH_USE_LINK_PATH | 适用于所有构建环境（pip/conda/editable） |
> | 平台条件 | `pyproject.toml [[tool.scikit-build.overrides]]` | Linux: BUILD_RPATH_USE_ORIGIN；macOS: MACOSX_RPATH、INSTALL_NAME_DIR | 平台差异通过`if.platform-system`条件匹配 |
> | Conda运行时 | `build.sh SKBUILD_CMAKE_ARGS` | CMAKE_PREFIX_PATH、INSTALL_RPATH、PREFER_SYSTEM_TVM_FFI、TVM_FFI_USE_LIBBACKTRACE、TVM_FFI_BACKTRACE_ON_SEGFAULT | 依赖运行时变量`$PREFIX`或需要post-build patchelf/install_name_tool处理 |
>
> **2. 关键发现**
> - scikit-build-core的`[[tool.scikit-build.overrides]]`支持`if.platform-system`（正则匹配`sys.platform`），Linux用`"linux"`，macOS用`"^darwin"`
> - **不能迁移**到pyproject.toml的参数：`CMAKE_PREFIX_PATH=${PREFIX}`（运行时变量）、`CMAKE_INSTALL_RPATH`（构建后被patchelf覆盖）、`CAFFE_FFI_PREFER_SYSTEM_TVM_FFI=ON`（conda特有逻辑）
> - **原pyproject.toml的问题**：`CMAKE_BUILD_RPATH_USE_ORIGIN=ON`全局设置对macOS无意义（macOS用`@loader_path`而非`$ORIGIN`），已修正为Linux-only override
> - build.sh SKBUILD_CMAKE_ARGS从12个-D参数（含平台分支）精简为5个conda专属参数
>
> **3. 修改文件**
> - `pyproject.toml`：新增`CAFFE_USE_BLAS`/`CAFFE_FFI_BUILD_TESTS`/`CMAKE_POSITION_INDEPENDENT_CODE`到cmake.define；将`CMAKE_BUILD_RPATH_USE_ORIGIN`移到Linux override；新增macOS override（`CMAKE_MACOSX_RPATH`/`CMAKE_INSTALL_NAME_DIR`）
> - `build.sh`：移除`_EXTRA_CMAKE_ARGS`分支和10个重复的-D参数，仅保留5个conda专属参数
>
> **4. 待验证**
> - ❌ 需在Docker/macOS实机构建验证参数精简后构建是否仍然成功
> - ❌ 非conda环境（直接`pip install .`）是否使用正确的默认CMake参数

#### 验收标准（L4升级DoD）

- [ ] macOS + Linux + Windows 三平台至少各有1个成功案例
- [ ] 至少3个不同项目（caffe-ffi外）成功复用该模式
- [ ] 至少1个conda-forge feedstock PR使用该模式并通过CI
- [ ] 所有10项检验标准在跨平台场景下仍然成立
- [ ] 反模式清单经过故障注入验证（每个反模式都有对应的失败案例）
- [ ] build.sh模板有平台自适应分支（Linux/macOS/Windows）
- [ ] 有自动化CI脚本可在三平台运行验证

---

### 模式B：conda-package-clean-verification L4升级计划

**当前状态**：L3（caffe-ffi项目6次迭代验证，仅Linux x86_64）

#### 需要补充的测试场景

| 编号 | 测试场景 | 验证目标 | 优先级 | 前置依赖 | 预计工作量 |
|------|---------|---------|--------|---------|-----------|
| B-T1 | **macOS干净环境验证** | otool -L替代ldd；otool -Iv替代nm；editable四件套在macOS的文件路径是否一致 | 🔴高 | macOS开发机或CI | 0.5天 |
| B-T2 | **Windows干净环境验证** | Dependencies工具（dumpbin /dependents）替代ldd；dumpbin /exports替代nm；Windows下editable安装机制差异 | 🔴高 | Windows开发机或CI | 1天 |
| B-T3 | **setuptools项目验证** | 使用setuptools而非scikit-build-core的项目，editable残留文件是否相同（.pth命名差异） | 🟡中 | 找一个setuptools项目 | 0.5天 |
| B-T4 | **hatchling项目验证** | 使用hatchling构建后端的项目，editable安装机制是否一致 | 🟡中 | 找一个hatchling项目 | 0.5天 |
| B-T5 | **maturin(Rust)项目验证** | Rust/maturin构建的原生扩展，验证五维验证法是否适用 | 🟡中 | 找一个maturin项目 | 0.5天 |
| B-T6 | **conda-forge CI集成** | 将验证脚本集成到conda-forge feedstock的CI中（Linux/macOS/Windows三平台） | 🔴高 | conda-forge feedstock | 1天 |
| B-T7 | **性能基准维度扩展** | 增加导入耗时、函数调用延迟等性能基准检查，防止构建版本性能退化 | 🟢低 | 确定基准阈值 | 1天 |
| B-T8 | **多Python版本验证** | Python 3.10/3.11/3.12/3.13/3.14多版本矩阵测试 | 🟡中 | conda多版本环境 | 1天 |
| B-T9 | **stale包目录深度污染测试** | 故意制造多层stale目录（手动复制旧版本到site-packages），验证清理函数能彻底清理 | 🟡中 | 构造测试场景 | 0.5天 |
| B-T10 | **pip install vs conda install冲突测试** | 先pip install同一个包，再conda install，验证清理和路径正确性 | 🟡中 | 构造测试场景 | 0.5天 |

#### 验收标准（L4升级DoD）

- [ ] macOS + Linux + Windows 三平台验证脚本均可用
- [ ] 至少3个不同构建后端（scikit-build-core、setuptools、maturin/hatchling）验证通过
- [ ] 至少1个conda-forge feedstock集成了该验证流程
- [ ] 所有10项检验标准在跨平台场景下仍然成立
- [ ] 清理函数经过stale/pip/conda冲突场景验证
- [ ] 有可复用的CI workflow模板（GitHub Actions/GitLab CI）
- [ ] 快速验证命令清单适配三大平台

---

### L4升级路线图

```
Phase 1（本周）：A-T1/B-T1 macOS验证 → 两模式支持Linux+macOS
Phase 2（下周）：A-T2/B-T2 Windows验证 → 三平台支持
Phase 3（2周内）：A-T4/A-T5/B-T3/B-T4/B-T5 多构建后端复用验证 → ≥3个独立案例
Phase 4（1月内）：A-T9/B-T6 conda-forge feedstock集成 → L4标准化
Phase 5（持续）：A-T3/A-T6/A-T7/A-T8/A-T10/B-T7/B-T8/B-T9/B-T10 补充测试
```

---

## Part 2：检验标准 Checklist 表格

> 以下表格可直接复制到任务追踪系统（Jira/Notion/飞书项目等）使用。

### Checklist A：conda-build-scikit-build-core-native（打包模式）

| 序号 | 检验项 | 验证方法 | 通过标准 | 阶段 | 责任人 | 状态 |
|-----|--------|---------|---------|------|--------|------|
| A1 | scikit-build-core在host段 | 检查meta.yaml requirements | scikit-build-core、setuptools-scm出现在host.requirements中，不是build.requirements | 构建前 | 打包者 | ⬜ |
| A2 | detect_binary_files_with_prefix=false | 检查meta.yaml build段 | build段显式设置detect_binary_files_with_prefix: false | 构建前 | 打包者 | ⬜ |
| A3 | 嵌套构建参数隔离 | 检查build.sh | 子项目构建前保存CMAKE_ARGS/SKBUILD_CMAKE_ARGS，unset后构建，完成后恢复 | 构建中 | 打包者 | ⬜ |
| A4 | 全$ORIGIN相对RPATH | grep build.sh | RPATH中无${PREFIX}绝对路径，全部使用$ORIGIN开头 | 构建后 | 打包者 | ⬜ |
| A5 | 每个.so单独RPATH深度 | 检查patchelf命令 | 不同目录深度的.so使用不同深度的../（如3级vs4级） | 构建后 | 打包者 | ⬜ |
| A6 | patchelf前后nm符号双重验证 | 检查build.sh | patchelf执行前后各有一次nm -D检查关键符号为T类型 | 构建后 | 打包者 | ⬜ |
| A7 | ldd依赖无not found | 执行ldd *.so | 所有.so的ldd输出中无"not found"行 | 构建后 | 打包者/CI | ⬜ |
| A8 | 三重editable清理 | 检查build.sh | 构建前、依赖安装后、主包安装后共三次clean_editable调用 | 构建中 | 打包者 | ⬜ |
| A9 | __file__路径验证门禁 | 检查build.sh末尾 | 构建末尾有python -c断言import路径包含site-packages | 构建后 | 打包者 | ⬜ |
| A10 | 无Placeholder/missing DSO错误 | 查看conda-build日志 | 构建日志无"Placeholder too short"、"missing DSO"错误 | 构建后 | CI | ⬜ |
| A11 | 全新环境离线安装可import | conda create + conda install --offline + import | 全新环境中import成功，不报错 | 验证 | QA | ⬜ |
| A12 | 全新环境单元测试全过 | CAFFE_FFI_DISABLE_BACKTRACE=1 pytest | 100%测试通过，无crash无fail | 验证 | QA | ⬜ |

---

### Checklist B：conda-package-clean-verification（验证模式）

| 序号 | 检验项 | 验证方法 | 通过标准 | 阶段 | 责任人 | 状态 |
|-----|--------|---------|---------|------|--------|------|
| B1 | 创建全新conda环境 | 检查脚本 | 测试前执行conda env remove + conda create，不复用现有环境 | 验证准备 | QA | ⬜ |
| B2 | conda build使用--no-test | 检查构建命令 | conda build带--no-test参数，测试在独立环境执行 | 构建阶段 | QA | ⬜ |
| B3 | Editable四件套预清理 | 检查清理函数 | .pth+.py+__pycache__+direct_url.json四类文件都被清理 | 构建前+安装前 | QA | ⬜ |
| B4 | __file__路径含site-packages | python -c "import pkg; assert 'site-packages' in pkg.__file__" | 断言通过，不触发AssertionError | 验证 | QA | ⬜ |
| B5 | __file__不在项目源码目录 | python -c "assert PROJECT_ROOT not in pkg.__file__" | 断言通过，不触发AssertionError | 验证 | QA | ⬜ |
| B6 | ldd检查无not found | for so in *.so; do ldd $so; done | 所有.so无"not found"依赖 | 验证 | QA/CI | ⬜ |
| B7 | nm关键符号为T类型 | nm -D libxxx.so \| grep "T SymbolName" | 关键导出符号标记为T（全局文本段） | 验证 | QA | ⬜ |
| B8 | 必要环境变量已设置 | echo $CAFFE_FFI_DISABLE_BACKTRACE | 测试环境中CAFFE_FFI_DISABLE_BACKTRACE=1 | 测试前 | QA | ⬜ |
| B9 | --pyargs非源码目录运行pytest | cd /tmp && pytest --pyargs pkg | 从site-packages运行测试，不从tests/目录 | 测试 | QA | ⬜ |
| B10 | 干净环境单元测试100%通过 | pytest返回码 | exit code=0，所有测试passed | 测试 | QA/CI | ⬜ |
| B11 | 脚本可重复运行 | 连续执行两次脚本 | 第二次执行无错误（环境销毁→重建幂等） | 验证 | QA | ⬜ |

---

### 快速参考：关键命令（复制即用）

```bash
# A4/A5: 检查RPATH是否为全$ORIGIN相对路径
for so in $(find $SP_DIR -name "*.so"); do
  echo "=== $so ==="
  readelf -d $so | grep -E "RPATH|RUNPATH"
done

# A6/B7: 检查关键符号
nm -D $SP_DIR/tvm_ffi/lib/libtvm_ffi.so | grep "T TVMFFIGetCustomAllocator"
# 预期输出：00000000000xxxxx T TVMFFIGetCustomAllocator

# A7/B6: 检查ldd依赖
for so in $(find $SP_DIR/caffe_ffi -name "*.so"); do
  echo "=== $so ==="
  ldd $so | grep -E "not found|libtvm|libopenblas" && echo "FAIL" || echo "OK"
done

# B4/B5: 路径验证
python -c "
import caffe_ffi, os
assert 'site-packages' in caffe_ffi.__file__, f'Wrong path: {caffe_ffi.__file__}'
print(f'OK: {caffe_ffi.__file__}')
"

# B9/B10: 非源码目录运行pytest
cd /tmp
CAFFE_FFI_DISABLE_BACKTRACE=1 python -m pytest --pyargs caffe_ffi -v
```

---

## 参考链接

- 打包模式文档：[conda-build-scikit-build-core-native.md](../../patterns/code-patterns/conda-build-scikit-build-core-native.md)
- 验证模式文档：[conda-package-clean-verification.md](../../patterns/code-patterns/conda-package-clean-verification.md)
- 复盘主报告：[README.md](README.md)
- 行动项Backlog：[insight-action-backlog.md](insight-action-backlog.md)
