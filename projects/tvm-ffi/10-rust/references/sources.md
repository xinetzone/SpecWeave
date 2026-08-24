# Rust绑定 - 信源清单

> 本文件从 facts.md 提取与本分类相关的事实，按模块组织，包含源码路径和关键API清单。
> 信源先行是 source-code-to-okf-wiki 方法论的核心纪律。

## 源码根路径

- **tvm-ffi 根目录**: `d:\AI\.chaos\libs\ffi`
- **TVM 根目录**: `d:\AI\.chaos\libs\ffi`（tvm-ffi + tvm 共存）

---

## 1. Crate 入口

### 源码路径

- `rust/tvm-ffi/src/lib.rs`

### 关键 API/类型清单

- `lib.rs 模块声明`
- `Any`
- `Array`
- `Map`
- `Tensor`
- `Device`
- `Function`
- `Error`
- `DataType`
- `String`
- `Bytes`
- `Shape`
- `Scalar`

### 相关事实编号

`F-305`, `F-306`

---

## 2. Any 类型

### 源码路径

- `rust/tvm-ffi/src/any.rs`

### 关键 API/类型清单

- `Any 枚举`
- `Any::type_index`
- `Any::from_tvm_ffi_any`
- `Any::to_tvm_ffi_any`

### 相关事实编号

`F-307`, `F-308`, `F-309`, `F-310`

---

## 3. Object 句柄

### 源码路径

- `rust/tvm-ffi/src/object.rs`

### 关键 API/类型清单

- `ObjectHandle`
- `Drop`
- `TVMFFIObjectDecRef`
- `TVMFFIObjectIncRef`
- `clone`

### 相关事实编号

`F-311`, `F-312`

---

## 4. Function

### 源码路径

- `rust/tvm-ffi/src/function.rs`

### 关键 API/类型清单

- `Function`
- `Function::call`
- `Function::get_global`
- `Function::register_global`

### 相关事实编号

`F-313`, `F-314`, `F-315`, `F-316`

---

## 5. Error / DataType

### 源码路径

- `rust/tvm-ffi/src/error.rs`
- `rust/tvm-ffi/src/dtype.rs`

### 关键 API/类型清单

- `Error`
- `Error::from_handle`
- `DataType`
- `DataType::int`
- `DataType::uint`
- `DataType::float`
- `DataType::bool`
- `DataType::void`

### 相关事实编号

`F-317`, `F-318`, `F-319`, `F-320`

---

## 6. 集合类型

### 源码路径

- `rust/tvm-ffi/src/collections/tensor.rs`
- `rust/tvm-ffi/src/collections/array.rs`
- `rust/tvm-ffi/src/collections/map.rs`
- `rust/tvm-ffi/src/collections/list.rs`
- `rust/tvm-ffi/src/collections/dict.rs`

### 关键 API/类型清单

- `collections::Tensor`
- `collections::Array<T>`
- `collections::Map<K,V>`
- `collections::List`
- `collections::Dict`
- `shape`
- `dtype`
- `device`
- `data`
- `len`
- `get`
- `push`
- `set`
- `contains`

### 相关事实编号

`F-321`, `F-322`, `F-323`, `F-324`, `F-325`

---

## 7. String

### 源码路径

- `rust/tvm-ffi/src/string.rs`

### 关键 API/类型清单

- `String`
- `String::from_str`
- `String::as_bytes`
- `AsRef<str>`
- `Display`
- `TVMFFIStringCreateFromData`
- `TVMFFIStringGetData`

### 相关事实编号

`F-326`, `F-327`, `F-328`

---

## 事实来源说明

所有事实编号引用自：
`d:\AI\.trae\specs\tvm-ffi-200-perspectives\supporting-analysis\facts.md`

每条事实包含源码文件路径与行号引用，仅陈述代码中可见内容，不含推测。

## 使用规范

1. 撰写概念文档时，必须引用本清单中的源码路径和事实编号
2. 新增 API 引用前，先在本清单中登记
3. 发现事实遗漏时，先补充 facts.md 再更新本清单
