# TVM编译器集成 - 信源清单

> 本文件从 facts.md 提取与本分类相关的事实，按模块组织，包含源码路径和关键API清单。
> 信源先行是 source-code-to-okf-wiki 方法论的核心纪律。

## 源码根路径

- **tvm-ffi 根目录**: `d:\AI\.chaos\libs\ffi`
- **TVM 根目录**: `d:\AI\.chaos\libs\ffi`（tvm-ffi + tvm 共存）

---

## 1. TVM 运行时基础

### 源码路径

- `include/tvm/runtime/base.h`
- `include/tvm/runtime/module.h`

### 关键 API/类型清单

- `tvm/runtime/base.h`
- `TVM runtime fully relies on TVM FFI C API`
- `ModuleNode 继承 ffi::Object`
- `Module 继承 ffi::ObjectRef`
- `TVM_DLL`
- `TVM_RUNTIME_DLL`
- `TVM_VERSION`

### 相关事实编号

`F-354`, `F-374`, `F-376`, `F-377`

---

## 2. IR 基础表达式

### 源码路径

- `include/tvm/ir/base_expr.h`
- `include/tvm/ir/expr.h`

### 关键 API/类型清单

- `TypeNode 继承 ffi::Object`
- `TypeNode::RegisterReflection`
- `PrimTypeNode`
- `PrimType`
- `PrimType::Int`
- `PrimType::UInt`
- `PrimType::Float`
- `PrimType::BFloat`
- `PrimType::Bool`
- `PrimType::Void`

### 相关事实编号

`F-355`, `F-356`, `F-357`, `F-359`, `F-360`, `F-373`

---

## 3. 运行时打包参数

### 源码路径

- `src/runtime/pack_args.h`

### 关键 API/类型清单

- `PackFuncVoidAddr`
- `PackFuncNonBufferArg`
- `PackFuncPackedArgAligned`
- `ArgUnion32`
- `ArgUnion64`
- `ArgConvertCode`
- `GetArgConvertCode`
- `ffi::Function`
- `ffi::PackedArgs`
- `ffi::Any`
- `ffi::Array`

### 相关事实编号

`F-361`, `F-362`, `F-363`, `F-364`, `F-365`, `F-366`, `F-367`, `F-368`

---

## 4. Python TVM 基础

### 源码路径

- `python/tvm/base.py`

### 关键 API/类型清单

- `load_lib_ctypes`
- `RTLD_GLOBAL`
- `RTLD_LOCAL`
- `tvm_runtime`
- `tvm_compiler`
- `_SKIP_UNKNOWN_OBJECTS`

### 相关事实编号

`F-369`, `F-370`, `F-371`, `F-372`

---

## 5. VM 虚拟机

### 源码路径

- `include/tvm/runtime/vm/vm.h`

### 关键 API/类型清单

- `VirtualMachine`
- `ffi::Function`
- `ffi::Array`

### 相关事实编号

`F-375`

---

## 6. FFI 扩展模块

### 源码路径

- `src/ffi/extra/module.cc`

### 关键 API/类型清单

- `ModuleNode 继承 Object`
- `Module 继承 ObjectRef`
- `Module::GetFunction`
- `Module::LoadFromFile`

### 相关事实编号

`F-301`, `F-302`, `F-303`, `F-304`

---

## 事实来源说明

所有事实编号引用自：
`d:\AI\.trae\specs\tvm-ffi-200-perspectives\supporting-analysis\facts.md`

每条事实包含源码文件路径与行号引用，仅陈述代码中可见内容，不含推测。

## 使用规范

1. 撰写概念文档时，必须引用本清单中的源码路径和事实编号
2. 新增 API 引用前，先在本清单中登记
3. 发现事实遗漏时，先补充 facts.md 再更新本清单
