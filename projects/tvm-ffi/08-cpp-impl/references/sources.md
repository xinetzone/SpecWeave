# C++实现细节 - 信源清单

> 本文件从 facts.md 提取与本分类相关的事实，按模块组织，包含源码路径和关键API清单。
> 信源先行是 source-code-to-okf-wiki 方法论的核心纪律。

## 源码根路径

- **tvm-ffi 根目录**: `d:\AI\.chaos\libs\ffi`
- **TVM 根目录**: `d:\AI\.chaos\libs\ffi`（tvm-ffi + tvm 共存）

---

## 1. TypeTable 类型表

### 源码路径

- `src/ffi/object.cc`

### 关键 API/类型清单

- `TypeTable`
- `TypeTable::RegisterType`
- `TypeTable::TypeKey2Index`
- `TypeTable::TypeIndex2Key`

### 相关事实编号

`F-274`, `F-275`, `F-276`, `F-277`, `F-278`, `F-279`

---

## 2. 容器实现

### 源码路径

- `src/ffi/container.cc`

### 关键 API/类型清单

- `ArrayNode::ArrayNode`
- `ArrayNode::SetItem`
- `MapNode::MapNode`
- `MapNode::Find`
- `MapNode::Set`

### 相关事实编号

`F-288`, `F-289`, `F-290`, `F-291`, `F-292`

---

## 3. Tensor 实现

### 源码路径

- `src/ffi/tensor.cc`

### 关键 API/类型清单

- `TensorObj::TensorObj`
- `TensorObj::~TensorObj`
- `TensorObj::ToDLPack`
- `Tensor::Make`

### 相关事实编号

`F-284`, `F-285`, `F-286`, `F-287`

---

## 4. InitOnce 线程安全初始化

### 源码路径

- `src/ffi/init_once.cc`

### 关键 API/类型清单

- `InitOnce`
- `std::call_once`

### 相关事实编号

`F-297`

---

## 5. Custom Allocator 自定义分配器

### 源码路径

- `src/ffi/custom_allocator.cc`

### 关键 API/类型清单

- `custom_allocator::Alloc`
- `custom_allocator::Free`
- `aligned_alloc`

### 相关事实编号

`F-298`, `F-299`

---

## 6. 对象终结器与弱引用

### 源码路径

- `include/tvm/ffi/c_api.h`
- `include/tvm/ffi/object.h`

### 关键 API/类型清单

- `TVMFFIPointerIsAlive`
- `TVMFFIPointerDecWeakRef`
- `TVMFFIPointerLock`
- `TVMFFIRegisterFinalizer`
- `WeakObjectPtr<T>`
- `WeakObjectPtr<T>::lock`

### 相关事实编号

`F-060`, `F-062`, `F-122`, `F-123`

---

## 事实来源说明

所有事实编号引用自：
`d:\AI\.trae\specs\tvm-ffi-200-perspectives\supporting-analysis\facts.md`

每条事实包含源码文件路径与行号引用，仅陈述代码中可见内容，不含推测。

## 使用规范

1. 撰写概念文档时，必须引用本清单中的源码路径和事实编号
2. 新增 API 引用前，先在本清单中登记
3. 发现事实遗漏时，先补充 facts.md 再更新本清单
