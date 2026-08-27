# 核心类型系统 - 信源清单

> 本文件从 facts.md 提取与本分类相关的事实，按模块组织，包含源码路径和关键API清单。
> 信源先行是 source-code-to-okf-wiki 方法论的核心纪律。

## 源码根路径

- **tvm-ffi 根目录**: `d:\AI\.chaos\libs\ffi`
- **TVM 根目录**: `d:\AI\.chaos\libs\ffi`（tvm-ffi + tvm 共存）

---

## 1. Any / AnyView

### 源码路径

- `include/tvm/ffi/any.h`

### 关键 API/类型清单

- `AnyView`
- `Any`
- `AnyView::type_index()`
- `AnyView::IsNone()`
- `AnyView::Cast<T>()`
- `Any::TryCast<T>()`
- `Any::operator==`

### 相关事实编号

`F-075`, `F-076`, `F-077`, `F-078`, `F-079`, `F-080`, `F-081`, `F-082`, `F-083`, `F-084`, `F-085`, `F-086`, `F-087`, `F-088`, `F-089`, `F-090`, `F-091`, `F-092`, `F-093`, `F-094`, `F-095`, `F-096`, `F-097`, `F-098`

---

## 2. Object / ObjectPtr / ObjectRef

### 源码路径

- `include/tvm/ffi/object.h`
- `src/ffi/object.cc`

### 关键 API/类型清单

- `Object`
- `ObjectPtr<T>`
- `WeakObjectPtr<T>`
- `ObjectRef`
- `make_object<T>`
- `Downcast<T>`
- `TypeTable`

### 相关事实编号

`F-099`, `F-100`, `F-101`, `F-102`, `F-103`, `F-104`, `F-105`, `F-106`, `F-107`, `F-108`, `F-109`, `F-110`, `F-111`, `F-112`, `F-113`, `F-114`, `F-115`, `F-116`, `F-117`, `F-118`, `F-119`, `F-120`, `F-121`, `F-122`, `F-123`, `F-124`, `F-125`, `F-126`, `F-127`, `F-128`, `F-129`, `F-130`, `F-131`, `F-132`, `F-133`, `F-134`, `F-274`, `F-275`, `F-276`, `F-277`, `F-278`, `F-279`

---

## 3. TypeIndex 类型索引

### 源码路径

- `include/tvm/ffi/c_api.h`

### 关键 API/类型清单

- `TVMFFITypeIndex`
- `kTVMFFITypeIndexDynamicBegin`
- `TVMFFITypeKeyToIndex`（c_api.h:705）
- `TypeIndex2Key`（C++ 侧，include/tvm/ffi/object.h:176）

### 相关事实编号

`F-001`, `F-002`, `F-003`, `F-004`, `F-005`, `F-006`, `F-007`, `F-008`, `F-009`, `F-010`, `F-011`, `F-012`, `F-023`

---

## 4. DataType / Device

### 源码路径

- `include/tvm/ffi/dtype.h`
- `src/ffi/dtype.cc`

### 关键 API/类型清单

- `DataType`
- `Device`
- `DataType::Int`
- `DataType::UInt`
- `DataType::Float`
- `DataType::BFloat`
- `DataType::Bool`

### 相关事实编号

`F-214`, `F-215`, `F-216`, `F-217`, `F-218`, `F-219`, `F-220`, `F-221`, `F-222`, `F-223`, `F-224`, `F-225`, `F-226`, `F-227`, `F-228`, `F-229`, `F-230`, `F-231`, `F-293`, `F-294`

---

## 5. 类型转换 Cast

### 源码路径

- `include/tvm/ffi/cast.h`

### 关键 API/类型清单

- `Cast<T>`
- `TryCast<T>`
- `AnyView::Cast<T>()`
- `AnyView::TryCast<T>()`

### 相关事实编号

`F-239`, `F-240`, `F-241`, `F-242`, `F-243`, `F-244`, `F-245`, `F-246`, `F-247`, `F-248`

---

## 事实来源说明

所有事实编号引用自：
`d:\AI\.trae\specs\tvm-ffi-200-perspectives\supporting-analysis\facts.md`

每条事实包含源码文件路径与行号引用，仅陈述代码中可见内容，不含推测。

## 使用规范

1. 撰写概念文档时，必须引用本清单中的源码路径和事实编号
2. 新增 API 引用前，先在本清单中登记
3. 发现事实遗漏时，先补充 facts.md 再更新本清单
