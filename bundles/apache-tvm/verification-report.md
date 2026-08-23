---
type: VerificationReport
title: Apache TVM Bundle V 阶段验证报告
verified_at: 2026-08-23
verifier: blackbox-validator/V
bundle_path: d:\AI\bundles\apache-tvm\
source_paths:
  - d:\AI\.chaos\libs\ffi\tvm\
  - d:\AI\.chaos\libs\ffi\tvm-ffi\
---

# Apache TVM Bundle V 阶段验证报告

**验证日期**：2026-08-23
**验证员**：独立黑盒验证员（未参与生成）
**验证对象**：`d:\AI\bundles\apache-tvm\`
**源码基线**：TVM 主仓库 + TVM-FFI 0.1.13

---

## 一、验证结果总览

| 检查项 | 状态 | 发现问题数 | 已修复 |
|--------|------|-----------|--------|
| 1. 文件结构完整性 | ✅ 通过 | 0 | — |
| 2. Frontmatter 验证 | ⚠️ 修复后通过 | 13 | 13 |
| 3. 内部链接验证 | ✅ 通过 | 0 | — |
| 4. Grep API 验证 | ⚠️ 修复后通过 | 8 类虚构 API | 全部修复 |
| 5. 代码示例验证 | ⚠️ 修复后通过 | 2 | 2 |
| 6. Index 完整性 | ✅ 通过 | 0 | — |
| 7. 事实编号引用验证 | ⚠️ 格式不一致（可接受） | 1 | 记录在案 |
| 8. 内容质量检查 | ✅ 通过 | 0 | — |

**最终结论**：✅ **验证通过**（所有阻断性问题已修复）

---

## 二、逐项检查详情

### 1. 文件结构完整性 — ✅ 通过

使用 Glob 确认全部 37 个必需文件存在：

- `index.md`、`log.md`
- `concepts/00-overview.md` 至 `21-llm-inference.md`（22 篇）+ `concepts/index.md`
- `examples/tvm-quickstart.md` + `examples/index.md`
- `references/facts-ir-tir.md`、`facts-relax-te-topi.md`、`facts-runtime-target-arith.md`、`facts-tvm-ffi.md`
- `references/insights.md`
- `references/ir-tir-source.md`、`relax-te-topi-source.md`、`runtime-target-arith-source.md`、`tvm-ffi-source.md`
- `references/index.md`

### 2. Frontmatter 验证 — ⚠️ 修复后通过

**发现问题**：

| 编号 | 严重程度 | 文件 | 问题描述 |
|------|---------|------|---------|
| FM-01 | 中 | `log.md` | 缺少 YAML frontmatter |
| FM-02 | 中 | `concepts/index.md` | 缺少 YAML frontmatter |
| FM-03 | 中 | `examples/index.md` | 缺少 YAML frontmatter |
| FM-04 | 中 | `references/index.md` | 缺少 YAML frontmatter |
| FM-05 | 中 | `references/insights.md` | 缺少 YAML frontmatter |
| FM-06 | 中 | `references/facts-ir-tir.md` | 缺少 YAML frontmatter |
| FM-07 | 中 | `references/facts-relax-te-topi.md` | 缺少 YAML frontmatter |
| FM-08 | 中 | `references/facts-runtime-target-arith.md` | 缺少 YAML frontmatter |
| FM-09 | 中 | `references/facts-tvm-ffi.md` | 缺少 YAML frontmatter |
| FM-10 | 中 | `references/ir-tir-source.md` | type 为 Reference 而非 source-code，缺少 source_id 字段 |
| FM-11 | 中 | `references/relax-te-topi-source.md` | 同上 |
| FM-12 | 中 | `references/runtime-target-arith-source.md` | 同上 |
| FM-13 | 中 | `references/tvm-ffi-source.md` | 同上 |

**修复措施**：为全部 13 个文件补全合规的 YAML frontmatter，包含 type、title、description、tags、generated、verified、status、stale_after 等必需字段。source 文件的 type 更正为 `source-code` 并添加 `source_id` 字段。

### 3. 内部链接验证 — ✅ 通过

使用 Grep 搜索 bundle 内所有 `/references/`、`/concepts/`、`/examples/` 链接，逐一验证目标文件存在。未发现断链。

### 4. Grep API 验证 — ⚠️ 修复后通过

在 TVM 主仓库和 TVM-FFI 源码中逐一验证文档提到的关键类名/函数名。

**已确认真实存在的 API**（部分清单）：

| API 名称 | 源码位置 |
|----------|---------|
| `IRModule` | `include/tvm/ir/module.h` |
| `PrimFunc` | `include/tvm/tirx/function.h` |
| `BlockBuilder` | `include/tvm/relax/block_builder.h` |
| `Schedule` | `include/tvm/s_tir/schedule/schedule.h` |
| `SBlock` | `include/tvm/tirx/stmt.h` |
| `PassContext` | `include/tvm/ir/transform.h` |
| `IterVar` | `include/tvm/tirx/var.h` |
| `Buffer` | `include/tvm/tirx/buffer.h` |
| `VirtualMachine` | `include/tvm/runtime/vm/vm.h` |
| `Target` | `include/tvm/target/target.h` |
| `CodeGenLLVM` | `src/target/llvm/codegen_llvm.h` |
| `Analyzer` | `include/tvm/arith/analyzer.h` |
| `Tensor`、`ComputeOp` | `include/tvm/te/` |
| `DataflowVar` | `include/tvm/relax/expr.h` |
| `ExecBuilder` | `include/tvm/relax/exec_builder.h` |
| `MetaSchedule`/`TuneContext` | `include/tvm/s_tir/meta_schedule/` |
| `PagedKVCache` | `src/runtime/vm/paged_kv_cache.cc` |
| `DeviceAPI` | `include/tvm/runtime/device_api.h` |
| `ffi::Object`、`ffi::Function`、`ffi::Any` | TVM-FFI 头文件 |
| `TVMFFIAny`、`GlobalFunctionTable` | TVM-FFI 源码 |
| `sblock`（TVMScript） | `python/tvm/tirx/script/builder/ir.py:562` |

**发现并修复的虚构/过时 API**：

| 编号 | 严重程度 | 虚构 API | 正确 API | 影响文件 |
|------|---------|---------|---------|---------|
| API-01 | **高** | `TVM_FFI_REGISTER_GLOBAL` 宏 | `refl::GlobalDef().def(...)` | `concepts/03-pass-infrastructure.md` |
| API-02 | **高** | `TVM_REGISTER_GLOBAL("device_api.xxx")` | `refl::GlobalDef().def_packed("device_api.xxx", ...)` | `concepts/17-runtime-module.md`、`references/facts-runtime-target-arith.md` |
| API-03 | **高** | `PackedFunc`（运行时函数类型） | `ffi::Function` | `concepts/00-overview.md`、`17-runtime-module.md`、`18-vm-bytecode.md`、`19-rpc-distributed.md`、`examples/tvm-quickstart.md`、`examples/index.md`、`concepts/index.md`、`index.md`、`log.md` |
| API-04 | **高** | `TVMArgs`/`TVMRetValue` | `ffi::PackedArgs`/`ffi::Any` | `concepts/17-runtime-module.md`、`examples/tvm-quickstart.md` |
| API-05 | **高** | `runtime::TypedPackedFunc<...>` | `ffi::Optional<ffi::Function>` | `concepts/13-relax-ops.md`（FusionPatternNode 定义） |
| API-06 | **高** | `TVMFuncCall`/`TVMArrayAlloc`/`TVMArrayFree`/`TVM_RUNTIME_ALLOC_ALIGNMENT` | `TVMFFIFunctionCall`/`TVMFFIAny`/`TVMFFIEnvModLookupFromImports`/`tvm_ffi_main` | `concepts/04-target-codegen.md` |
| API-07 | 中 | `@tvm.script.tir` 装饰器 | `@tvm.script.tirx.prim_func` | `concepts/20-tvmscript.md`、`examples/tvm-quickstart.md`、`examples/index.md` |
| API-08 | 中 | `tirx.block("C")` | `tirx.sblock("C")` | `examples/tvm-quickstart.md` |

**保留的合法引用**：`PackedFuncTypeNode`/`PackedFuncType` 是 Relax 类型系统中的真实类名（`include/tvm/relax/type.h:52`），`FCallPacked` 是 Relax 算子属性的真实类型别名（`include/tvm/relax/op_attr_types.h:61`），这些引用正确无误，予以保留。

### 5. 代码示例验证 — ⚠️ 修复后通过

检查 `examples/tvm-quickstart.md` 中的 Python API 引用：

- `te.placeholder`、`te.compute`、`te.reduce_axis`、`te.create_prim_func` — 均在 `python/tvm/te/__init__.py` 中导出 ✅
- `tvm.compile`、`tvm.tirx.build` — 在 Driver 层存在 ✅
- `tvm.cpu()`、`tvm.nd.array`、`tvm.nd.empty` — Runtime API 存在 ✅
- TVMScript 装饰器和 `sblock` — 修复后正确 ✅

**修复的问题**：
1. `@tvm.script.tir` → `@tvm.script.tirx.prim_func`
2. `tirx.block("C")` → `tirx.sblock("C")`

### 6. Index 完整性 — ✅ 通过

`index.md` 列出了全部 22 篇概念文档（00-21），包含 examples 和 references 链接。根 index 包含 `okf_version: "0.2"` 字段。

### 7. 事实编号引用验证 — ⚠️ 格式不一致（非阻断）

抽查 5 篇概念文档（00-overview、11-relax-ir、15-te-tensor-expression、17-runtime-module、20-tvmscript）的事实编号引用。

**发现**：
- `facts-ir-tir.md` 使用 `F-XXX:` 格式（如 `F-060:`）
- 其余三个事实文件（`facts-relax-te-topi.md`、`facts-runtime-target-arith.md`、`facts-tvm-ffi.md`）使用纯数字列表（`1.`、`2.`...）
- 概念文档统一使用 `[F-XXX]` 格式引用

**评估**：编号本身在对应事实文件中可追溯（数字编号一一对应），仅前缀格式不一致。这不影响事实的可验证性，属于生成阶段的风格不统一。考虑到全面重编号风险较大且收益有限，本次验证记录此问题但不做强制修改。

### 8. 内容质量检查 — ✅ 通过

- 所有 22 篇概念文档主题清晰、结构完整
- 未发现 "TODO"、"待补充"、"FIXME"、"TBD" 等占位内容
- 中文表达通顺专业，术语使用一致
- 代码示例与概念说明配合恰当

---

## 三、修复文件清单

本次验证共修改以下 **18 个文件**：

### 虚构 API 修复（10 个文件）
1. `concepts/03-pass-infrastructure.md` — TVM_FFI_REGISTER_GLOBAL → refl::GlobalDef
2. `concepts/04-target-codegen.md` — 旧版 C API → TVM-FFI C API
3. `concepts/13-relax-ops.md` — TypedPackedFunc → ffi::Optional<ffi::Function>，FusionPatternNode 修正
4. `concepts/17-runtime-module.md` — PackedFunc/TVMArgs → ffi::Function/ffi::PackedArgs
5. `concepts/18-vm-bytecode.md` — PackedFunc → ffi::Function
6. `concepts/19-rpc-distributed.md` — PackedFunc stub → ffi::Function stub
7. `concepts/20-tvmscript.md` — @tvm.script.tir → @tvm.script.tirx.prim_func
8. `concepts/00-overview.md` — PackedFunc → ffi::Function
9. `concepts/11-relax-ir.md` — 外部 PackedFunc 引用 → ffi::Function
10. `examples/tvm-quickstart.md` — TVMScript 装饰器、sblock、PackedFunc

### 描述性文字同步更新（4 个文件）
11. `index.md` — PackedFunc → ffi::Function
12. `log.md` — PackedFunc → ffi::Function
13. `concepts/index.md` — PackedFunc → ffi::Function
14. `examples/index.md` — @tvm.script.tir、PackedFunc

### Frontmatter 补全（13 个文件，部分与上述重叠）
15. `references/facts-ir-tir.md`
16. `references/facts-relax-te-topi.md`
17. `references/facts-runtime-target-arith.md`
18. `references/facts-tvm-ffi.md`
19. `references/insights.md`
20. `references/index.md`
21. `references/ir-tir-source.md`（type + source_id 修正）
22. `references/relax-te-topi-source.md`
23. `references/runtime-target-arith-source.md`
24. `references/tvm-ffi-source.md`

---

## 四、统计

| 指标 | 数值 |
|------|------|
| 验证文件总数 | 37 |
| 发现问题总数 | 23（13 frontmatter + 8 类虚构 API + 2 示例错误） |
| 已修复问题数 | 23 |
| 修复率 | 100% |
| 虚构 API 类数 | 8 |
| 受影响文件数 | 18 |
| 断链数 | 0 |
| 占位内容数 | 0 |

---

## 五、验证结论

Apache TVM bundle 在文件结构、内部链接、内容完整性和整体质量方面基础扎实。发现的主要问题是部分文档使用了 TVM 旧版 API 名称（PackedFunc/TVMArgs/TVM_REGISTER_GLOBAL 等），这些 API 在当前基于 TVM-FFI 的版本中已被 `ffi::Function`、`ffi::PackedArgs`、`refl::GlobalDef()` 等替代。所有虚构/过时 API 已逐一通过源码 Grep 验证并更正为真实存在的等价物。Frontmatter 缺失问题已全部补全。

**验证结果：✅ 通过**
