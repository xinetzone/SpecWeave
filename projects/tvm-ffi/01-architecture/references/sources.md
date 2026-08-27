# 架构与设计哲学 - 信源清单

> 本文件从 facts.md 提取与本分类相关的事实，按模块组织，包含源码路径和关键API清单。
> 信源先行是 source-code-to-okf-wiki 方法论的核心纪律。

## 源码根路径

- **tvm-ffi 根目录**: `d:\AI\.chaos\libs\ffi`
- **TVM 根目录**: `d:\AI\.chaos\libs\ffi`（tvm-ffi + tvm 共存）

---

## 1. C ABI 层

### 源码路径

- `include/tvm/ffi/c_api.h`

### 关键 API/类型清单

- `TVMFFITypeIndex`
- `TVMFFISafeCallType`
- `TVMFFIFunction`
- `TVMFFIGetVersion`
- `TVMFFI_CONTAINER_ALIGNED_BYTES`

### 相关事实编号

`F-001`, `F-012`, `F-016`, `F-017`, `F-018`, `F-064`

---

## 2. 核心类型层

### 源码路径

- `include/tvm/ffi/any.h`
- `include/tvm/ffi/object.h`
- `include/tvm/ffi/function.h`

### 关键 API/类型清单

- `AnyView`
- `Any`
- `Object`
- `ObjectPtr<T>`
- `ObjectRef`
- `Function`

### 相关事实编号

`F-075`, `F-085`, `F-099`, `F-111`, `F-124`, `F-135`

---

## 3. 全局函数注册

### 源码路径

- `include/tvm/ffi/function.h`
- `src/ffi/function.cc`

### 关键 API/类型清单

- `Function::GetGlobal`（function.h:409）
- `Function::SetGlobal`（function.h:499）
- `Function::ListGlobalNames`
- `refl::GlobalDef`（include/tvm/ffi/reflection/registry.h）

### 相关事实编号

`F-141`, `F-142`, `F-143`, `F-151`, `F-280`, `F-281`, `F-282`

---

## 4. 模块系统

### 源码路径

- `src/ffi/extra/module.cc`
- `include/tvm/runtime/module.h`

### 关键 API/类型清单

- `ModuleNode`
- `Module`
- `Module::GetFunction`
- `Module::LoadFromFile`

### 相关事实编号

`F-301`, `F-302`, `F-303`, `F-304`, `F-374`

---

## 5. 总括头文件

### 源码路径

- `include/tvm/ffi/tvm_ffi.h`

### 关键 API/类型清单

- `tvm_ffi.h 总括包含所有公共头文件`

### 相关事实编号

`F-378`, `F-379`

---

## 事实来源说明

所有事实编号引用自：
`d:\AI\.trae\specs\tvm-ffi-200-perspectives\supporting-analysis\facts.md`

每条事实包含源码文件路径与行号引用，仅陈述代码中可见内容，不含推测。

## 使用规范

1. 撰写概念文档时，必须引用本清单中的源码路径和事实编号
2. 新增 API 引用前，先在本清单中登记
3. 发现事实遗漏时，先补充 facts.md 再更新本清单
