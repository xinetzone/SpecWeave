# NPU与加速器建议 - 信源清单

> 本文件从 facts.md 提取与本分类相关的事实，按模块组织，包含源码路径和关键API清单。
> 信源先行是 source-code-to-okf-wiki 方法论的核心纪律。

## 源码根路径

- **tvm-ffi 根目录**: `d:\AI\.chaos\libs\ffi`
- **TVM 根目录**: `d:\AI\.chaos\libs\ffi`（tvm-ffi + tvm 共存）

---

## 1. Tensor 与设备管理基础

### 源码路径

- `include/tvm/ffi/container/tensor.h`
- `include/tvm/ffi/dtype.h`
- `src/ffi/tensor.cc`

### 关键 API/类型清单

- `TensorObj`
- `Tensor`
- `Tensor::Make`
- `Tensor::device`
- `Tensor::data`
- `Device`
- `DLDevice`
- `TVMFFITensorMake`

### 相关事实编号

`F-175`, `F-176`, `F-177`, `F-181`, `F-183`, `F-230`, `F-287`

---

## 2. DLPack 零拷贝互操作

### 源码路径

- `include/tvm/ffi/container/tensor.h`
- `3rdparty/dlpack/dlpack.h`

### 关键 API/类型清单

- `Tensor::ToDLPack`
- `TensorObj::ToDLPack`
- `DLManagedTensor`
- `DLTensor`
- `deleter`

### 相关事实编号

`F-185`, `F-286`

---

## 3. 函数注册与模块加载

### 源码路径

- `include/tvm/ffi/function.h`
- `src/ffi/extra/module.cc`

### 关键 API/类型清单

- `Function::FromPacked`（function.h:341）
- `Function::GetGlobal`（function.h:409）
- `Function::SetGlobal`（function.h:499）
- `Module`
- `ModuleNode`
- `Module::LoadFromFile`
- `GetFunction`

### 相关事实编号

`F-140`, `F-141`, `F-142`, `F-301`, `F-302`, `F-304`

---

## 4. 错误处理与传播

### 源码路径

- `include/tvm/ffi/error.h`
- `include/tvm/ffi/c_api.h`

### 关键 API/类型清单

- `Error::WithContext`
- `Error::Raise`
- `TVMFFIThrowableGetMessage`
- `TVMFFIThrowableAppendContext`
- `TVMFFIThrowableToAny`

### 相关事实编号

`F-204`, `F-209`, `F-210`, `F-028`, `F-031`

---

## 5. 对象与内存管理

### 源码路径

- `include/tvm/ffi/object.h`
- `include/tvm/ffi/c_api.h`

### 关键 API/类型清单

- `Object::IncRef`
- `Object::DecRef`
- `make_object`
- `TVMFFIObjectIncRef`
- `TVMFFIObjectDecRef`
- `TVMFFIRegisterFinalizer`

### 相关事实编号

`F-106`, `F-120`, `F-019`, `F-062`

---

## 6. 反射与自定义类型注册

### 源码路径

- `include/tvm/ffi/reflection/registry.h`
- `include/tvm/ffi/c_api.h`

### 关键 API/类型清单

- `ObjectDef<T>`
- `TVM_FFI_REGISTER_OBJECT`
- `TVMFFIObjectDef`
- `TVMFFIObjectDefRegister`
- `TVMFFISetCustomClassAllocator`

### 相关事实编号

`F-255`, `F-261`, `F-037`, `F-038`, `F-040`

---

## 事实来源说明

所有事实编号引用自：
`d:\AI\.trae\specs\tvm-ffi-200-perspectives\supporting-analysis\facts.md`

每条事实包含源码文件路径与行号引用，仅陈述代码中可见内容，不含推测。

## 使用规范

1. 撰写概念文档时，必须引用本清单中的源码路径和事实编号
2. 新增 API 引用前，先在本清单中登记
3. 发现事实遗漏时，先补充 facts.md 再更新本清单
