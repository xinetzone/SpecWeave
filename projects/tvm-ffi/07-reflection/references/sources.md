# 反射系统 - 信源清单

> 本文件从 facts.md 提取与本分类相关的事实，按模块组织，包含源码路径和关键API清单。
> 信源先行是 source-code-to-okf-wiki 方法论的核心纪律。

## 源码根路径

- **tvm-ffi 根目录**: `d:\AI\.chaos\libs\ffi`
- **TVM 根目录**: `d:\AI\.chaos\libs\ffi`（tvm-ffi + tvm 共存）

---

## 1. 对象反射注册

### 源码路径

- `include/tvm/ffi/reflection/registry.h`
- `include/tvm/ffi/c_api.h`

### 关键 API/类型清单

- `refl::GlobalDef`（reflection/registry.h）
- `refl::ObjectDef`（reflection/registry.h:726）
- `TVMFFIGetTypeInfo`（c_api.h:1498）
- `TVMFFITypeKeyToIndex`（c_api.h:705）

### 相关事实编号

`F-249`, `F-250`, `F-251`, `F-252`, `F-253`

---

## 2. ObjectDef / FieldDef

### 源码路径

- `include/tvm/ffi/reflection/registry.h`

### 关键 API/类型清单

- `reflection::FieldDef`
- `reflection::ObjectDef<T>`
- `ObjectDef<T>::def`
- `ObjectDef<T>::def_ro`
- `ObjectDef<T>::def_rw`
- `AttachFieldFlag`
- `DefaultValue`
- `TVM_FFI_REGISTER_OBJECT`
- `TVM_FFI_REGISTER_OBJECT_REF`

### 相关事实编号

`F-254`, `F-255`, `F-256`, `F-257`, `F-258`, `F-259`, `F-260`, `F-261`, `F-262`

---

## 3. C ABI 反射接口

### 源码路径

- `include/tvm/ffi/c_api.h`

### 关键 API/类型清单

- `TVMFFIReflectionVTableGet`
- `TVMFFIReflectionVTable`
- `TVMFFIFieldKind`
- `TVMFFIFieldInfo`
- `TVMFFIObjectDef`
- `TVMFFIObjectDefRegister`
- `TVMFFIObjectDefRegisterWithInit`
- `TVMFFISetCustomClassAllocator`
- `TVMFFIObjectNew`

### 相关事实编号

`F-033`, `F-034`, `F-035`, `F-036`, `F-037`, `F-038`, `F-039`, `F-040`, `F-041`

---

## 4. 结构化相等与哈希

### 源码路径

- `include/tvm/ffi/extra/structural_equal.h`
- `include/tvm/ffi/extra/structural_hash.h`
- `src/ffi/extra/structural_equal.cc`
- `src/ffi/extra/structural_hash.cc`
- `include/tvm/ffi/c_api.h`

### 关键 API/类型清单

- `StructuralEqual`
- `StructuralHash`
- `SEqualReducer`
- `SHashReducer`
- `TVMFFIStructuralEqual`
- `TVMFFIStructuralHash`
- `kTVMFFISEqHashKindTreeNode`
- `kTVMFFISEqHashKindDAGNode`

### 相关事实编号

`F-024`, `F-263`, `F-264`, `F-265`, `F-266`, `F-267`, `F-268`, `F-269`, `F-270`, `F-271`, `F-272`, `F-273`

---

## 5. 基础类型反射注册

### 源码路径

- `src/ffi/extra/reflection_extra.cc`

### 关键 API/类型清单

- `reflection_extra.cc 基础类型注册（int/float/bool/string）`

### 相关事实编号

`F-300`

---

## 事实来源说明

所有事实编号引用自：
`d:\AI\.trae\specs\tvm-ffi-200-perspectives\supporting-analysis\facts.md`

每条事实包含源码文件路径与行号引用，仅陈述代码中可见内容，不含推测。

## 使用规范

1. 撰写概念文档时，必须引用本清单中的源码路径和事实编号
2. 新增 API 引用前，先在本清单中登记
3. 发现事实遗漏时，先补充 facts.md 再更新本清单
