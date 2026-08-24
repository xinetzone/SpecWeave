# 构建与打包 - 信源清单

> 本文件从 facts.md 提取与本分类相关的事实，按模块组织，包含源码路径和关键API清单。
> 信源先行是 source-code-to-okf-wiki 方法论的核心纪律。

## 源码根路径

- **tvm-ffi 根目录**: `d:\AI\.chaos\libs\ffi`
- **TVM 根目录**: `d:\AI\.chaos\libs\ffi`（tvm-ffi + tvm 共存）

---

## 1. 源码结构

### 源码路径

- `CMakeLists.txt`
- `include/tvm/ffi/`
- `src/ffi/`
- `python/tvm_ffi/`
- `rust/tvm-ffi/`

### 关键 API/类型清单

- `头文件目录 include/tvm/ffi/`
- `源文件目录 src/ffi/`
- `Python 包目录 python/tvm_ffi/`
- `Rust crate 目录 rust/tvm-ffi/`

### 相关事实编号

`F-378`

---

## 2. 总括头文件

### 源码路径

- `include/tvm/ffi/tvm_ffi.h`

### 关键 API/类型清单

- `tvm_ffi.h 包含所有公共头文件`
- `any.h`
- `c_api.h`
- `cast.h`
- `container/array.h`
- `container/list.h`
- `container/map.h`
- `container/dict.h`
- `container/tuple.h`
- `container/variant.h`
- `container/tensor.h`
- `container/shape.h`
- `container/scalar.h`
- `string.h`
- `dtype.h`
- `enum.h`
- `error.h`
- `function.h`
- `object.h`
- `optional.h`
- `result.h`

### 相关事实编号

`F-378`

---

## 事实来源说明

所有事实编号引用自：
`d:\AI\.trae\specs\tvm-ffi-200-perspectives\supporting-analysis\facts.md`

每条事实包含源码文件路径与行号引用，仅陈述代码中可见内容，不含推测。

## 使用规范

1. 撰写概念文档时，必须引用本清单中的源码路径和事实编号
2. 新增 API 引用前，先在本清单中登记
3. 发现事实遗漏时，先补充 facts.md 再更新本清单
