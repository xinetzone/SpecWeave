# C ABI与平台 - 信源清单

> 本文件从 facts.md 提取与本分类相关的事实，按模块组织，包含源码路径和关键API清单。
> 信源先行是 source-code-to-okf-wiki 方法论的核心纪律。

## 源码根路径

- **tvm-ffi 根目录**: `d:\AI\.chaos\libs\ffi`
- **TVM 根目录**: `d:\AI\.chaos\libs\ffi`（tvm-ffi + tvm 共存）

---

## 1. C ABI 核心类型

### 源码路径

- `include/tvm/ffi/c_api.h`

### 关键 API/类型清单

- `TVMFFITypeIndex`
- `TVMFFIObject`
- `TVMFFIAny`
- `TVMFFISafeCallType`
- `TVMFFIFunction`

### 相关事实编号

`F-001`, `F-013`, `F-014`, `F-015`, `F-016`, `F-017`

---

## 2. 版本与运行时特性

### 源码路径

- `include/tvm/ffi/c_api.h`

### 关键 API/类型清单

- `TVMFFIGetVersion`（c_api.h:546）
- `TVMFFIVersion`（c_api.h:90）

### 相关事实编号

`F-018`, `F-025`, `F-379`

---

## 3. 对象生命周期管理

### 源码路径

- `include/tvm/ffi/c_api.h`

### 关键 API/类型清单

- `TVMFFIObjectIncRef`
- `TVMFFIObjectDecRef`
- `TVMFFISetCustomClassAllocator`
- `TVMFFIObjectNew`
- `TVMFFIPointerIsAlive`
- `TVMFFIPointerDecWeakRef`
- `TVMFFIPointerLock`
- `TVMFFIRegisterFinalizer`

### 相关事实编号

`F-019`, `F-040`, `F-041`, `F-060`, `F-062`

---

## 4. 容器 C ABI

### 源码路径

- `include/tvm/ffi/c_api.h`

### 关键 API/类型清单

- `TVMFFIArrayAllocate`
- `TVMFFIArrayGetCapacity`
- `TVMFFIArrayGetSize`
- `TVMFFIArraySetSize`
- `TVMFFIArrayGetData`
- `TVMFFIListGetCapacity`
- `TVMFFIListGetSize`
- `TVMFFIListSetSize`
- `TVMFFIListGetData`
- `TVMFFIDictAllocate`
- `TVMFFIDictReHash`
- `TVMFFIDictGetSize`
- `TVMFFIDictGetCapacity`
- `TVMFFIDictGetIndex`
- `TVMFFIDictGetKeyAt`
- `TVMFFIDictGetValueAt`
- `TVMFFIDictSetValueAt`
- `TVMFFIDictEraseAt`
- `TVMFFIMapAllocate`
- `TVMFFIMapGetSize`
- `TVMFFIMapIndex`
- `TVMFFIMapGetKeyAt`
- `TVMFFIMapGetValueAt`
- `TVMFFIMapEraseAt`
- `TVMFFI_CONTAINER_ALIGNED_BYTES`

### 相关事实编号

`F-047`, `F-048`, `F-049`, `F-050`, `F-064`, `F-065`, `F-066`, `F-067`, `F-068`, `F-069`, `F-070`, `F-071`, `F-072`, `F-073`, `F-074`

---

## 5. 字符串/字节 C ABI

### 源码路径

- `include/tvm/ffi/c_api.h`

### 关键 API/类型清单

- `TVMFFIBytesCreateFromData`
- `TVMFFIBytesGetData`
- `TVMFFIStringCreateFromData`
- `TVMFFIStringGetData`

### 相关事实编号

`F-055`, `F-056`, `F-057`, `F-058`

---

## 事实来源说明

所有事实编号引用自：
`d:\AI\.trae\specs\tvm-ffi-200-perspectives\supporting-analysis\facts.md`

每条事实包含源码文件路径与行号引用，仅陈述代码中可见内容，不含推测。

## 使用规范

1. 撰写概念文档时，必须引用本清单中的源码路径和事实编号
2. 新增 API 引用前，先在本清单中登记
3. 发现事实遗漏时，先补充 facts.md 再更新本清单
