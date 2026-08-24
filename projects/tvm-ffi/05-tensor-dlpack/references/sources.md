# Tensor与DLPack - 信源清单

> 本文件从 facts.md 提取与本分类相关的事实，按模块组织，包含源码路径和关键API清单。
> 信源先行是 source-code-to-okf-wiki 方法论的核心纪律。

## 源码根路径

- **tvm-ffi 根目录**: `d:\AI\.chaos\libs\ffi`
- **TVM 根目录**: `d:\AI\.chaos\libs\ffi`（tvm-ffi + tvm 共存）

---

## 1. Tensor 核心

### 源码路径

- `include/tvm/ffi/container/tensor.h`
- `src/ffi/tensor.cc`

### 关键 API/类型清单

- `TensorObj`
- `Tensor`
- `Tensor::data`
- `Tensor::device`
- `Tensor::dtype`
- `Tensor::ndim`
- `Tensor::shape`
- `Tensor::strides`
- `Tensor::ToDLPack`
- `Tensor::Make`

### 相关事实编号

`F-175`, `F-176`, `F-177`, `F-178`, `F-179`, `F-180`, `F-181`, `F-182`, `F-183`, `F-184`, `F-185`, `F-284`, `F-285`, `F-286`, `F-287`

---

## 2. C ABI Tensor 接口

### 源码路径

- `include/tvm/ffi/c_api.h`

### 关键 API/类型清单

- `TVMFFITensorMake`
- `TVMFFITensorGetView`
- `TVMFFI_CONTAINER_ALIGNED_SHAPE_DIMS`

### 相关事实编号

`F-053`, `F-054`, `F-380`

---

## 3. DLPack 相关结构

### 源码路径

- `3rdparty/dlpack/dlpack.h`
- `include/tvm/ffi/container/tensor.h`

### 关键 API/类型清单

- `DLTensor`
- `DLManagedTensor`
- `DLDevice`
- `DLDataType`
- `DLManagedTensorContext`

### 相关事实编号

`F-175`, `F-177`, `F-185`

---

## 事实来源说明

所有事实编号引用自：
`d:\AI\.trae\specs\tvm-ffi-200-perspectives\supporting-analysis\facts.md`

每条事实包含源码文件路径与行号引用，仅陈述代码中可见内容，不含推测。

## 使用规范

1. 撰写概念文档时，必须引用本清单中的源码路径和事实编号
2. 新增 API 引用前，先在本清单中登记
3. 发现事实遗漏时，先补充 facts.md 再更新本清单
