# 容器系统 - 信源清单

> 本文件从 facts.md 提取与本分类相关的事实，按模块组织，包含源码路径和关键API清单。
> 信源先行是 source-code-to-okf-wiki 方法论的核心纪律。

## 源码根路径

- **tvm-ffi 根目录**: `d:\AI\.chaos\libs\ffi`
- **TVM 根目录**: `d:\AI\.chaos\libs\ffi`（tvm-ffi + tvm 共存）

---

## 1. Array / List

### 源码路径

- `include/tvm/ffi/container/array.h`
- `include/tvm/ffi/container/list.h`
- `src/ffi/container.cc`

### 关键 API/类型清单

- `ArrayNode`
- `Array<T>`
- `ListNode`
- `List`
- `ArrayNode::GetSize`
- `ArrayNode::at`
- `ArrayNode::SetItem`
- `Array<T>::push_back`

### 相关事实编号

`F-153`, `F-154`, `F-155`, `F-156`, `F-157`, `F-158`, `F-159`, `F-160`, `F-161`, `F-162`, `F-163`, `F-164`, `F-165`, `F-288`, `F-289`

---

## 2. Map / Dict

### 源码路径

- `include/tvm/ffi/container/map.h`
- `include/tvm/ffi/container/dict.h`
- `src/ffi/container.cc`

### 关键 API/类型清单

- `MapNode`
- `Map<K,V>`
- `DictNode`
- `Dict`
- `Map<K,V>::operator[]`
- `Map<K,V>::at`
- `Map<K,V>::find`
- `Map<K,V>::Set`

### 相关事实编号

`F-166`, `F-167`, `F-168`, `F-169`, `F-170`, `F-171`, `F-172`, `F-173`, `F-174`, `F-290`, `F-291`, `F-292`

---

## 3. String / Bytes

### 源码路径

- `include/tvm/ffi/string.h`

### 关键 API/类型清单

- `StringObj`
- `String`
- `BytesObj`
- `Bytes`
- `String::operator std::string`
- `String::c_str`

### 相关事实编号

`F-196`, `F-197`, `F-198`, `F-199`, `F-200`, `F-201`

---

## 4. Shape / Scalar

### 源码路径

- `include/tvm/ffi/container/shape.h`
- `include/tvm/ffi/container/scalar.h`

### 关键 API/类型清单

- `ShapeObj`
- `Shape`
- `ScalarObj`
- `Scalar`

### 相关事实编号

`F-186`, `F-187`, `F-188`, `F-189`, `F-190`, `F-191`

---

## 5. Tuple / Variant

### 源码路径

- `include/tvm/ffi/container/tuple.h`
- `include/tvm/ffi/container/variant.h`

### 关键 API/类型清单

- `TupleObj`
- `Tuple`
- `VariantObj`
- `Variant<Types...>`

### 相关事实编号

`F-192`, `F-193`, `F-194`, `F-195`

---

## 6. C ABI 容器接口

### 源码路径

- `include/tvm/ffi/c_api.h`

### 关键 API/类型清单

- `TVMFFISeqableGetItem`
- `TVMFFIMappingGetItem`
- `TVMFFIArraySetItem`
- `TVMFFIListPushBack`
- `TVMFFIDictGetItem`
- `TVMFFITupleGetItem`
- `TVMFFIVariantGetIndex`
- `TVMFFIStructNew`

### 相关事实编号

`F-042`, `F-043`, `F-044`, `F-045`, `F-046`, `F-047`, `F-048`, `F-049`, `F-050`, `F-051`, `F-052`, `F-065`, `F-066`, `F-067`, `F-068`, `F-069`, `F-070`, `F-071`, `F-072`, `F-073`, `F-074`

---

## 事实来源说明

所有事实编号引用自：
`d:\AI\.trae\specs\tvm-ffi-200-perspectives\supporting-analysis\facts.md`

每条事实包含源码文件路径与行号引用，仅陈述代码中可见内容，不含推测。

## 使用规范

1. 撰写概念文档时，必须引用本清单中的源码路径和事实编号
2. 新增 API 引用前，先在本清单中登记
3. 发现事实遗漏时，先补充 facts.md 再更新本清单
