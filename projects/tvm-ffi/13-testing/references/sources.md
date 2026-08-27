# 测试策略 - 信源清单

> 本文件从 facts.md 提取与本分类相关的事实，按模块组织，包含源码路径和关键API清单。
> 信源先行是 source-code-to-okf-wiki 方法论的核心纪律。

## 源码根路径

- **tvm-ffi 根目录**: `d:\AI\.chaos\libs\ffi`
- **TVM 根目录**: `d:\AI\.chaos\libs\ffi`（tvm-ffi + tvm 共存）

---

## 1. 核心模块测试

### 源码路径

- `tests/cpp/`
- `tests/python/`

### 关键 API/类型清单

- `test_any 测试 Any/AnyView 类型`
- `test_object 测试 Object/ObjectPtr/ObjectRef`
- `test_function 测试 Function 调用`
- `test_container 测试 Array/List/Map/Dict`
- `test_tensor 测试 Tensor/DLPack`
- `test_error 测试 Error/错误处理`
- `test_dtype 测试 DataType/Device`

### 相关事实编号

`F-001`, `F-075`, `F-099`, `F-135`, `F-153`, `F-175`, `F-202`

---

## 2. C++ 测试套件

### 源码路径

- `tests/cpp/`

### 关键 API/类型清单

- `GoogleTest 框架`
- `TEST_F 宏`
- `EXPECT_EQ`
- `ASSERT_TRUE`

---

## 3. Python 测试套件

### 源码路径

- `tests/python/`

### 关键 API/类型清单

- `pytest 框架`
- `pytest.fixture`
- `assert 语句`

### 相关事实编号

`F-329`, `F-330`

---

## 事实来源说明

所有事实编号引用自：
`d:\AI\.trae\specs\tvm-ffi-200-perspectives\supporting-analysis\facts.md`

每条事实包含源码文件路径与行号引用，仅陈述代码中可见内容，不含推测。

## 使用规范

1. 撰写概念文档时，必须引用本清单中的源码路径和事实编号
2. 新增 API 引用前，先在本清单中登记
3. 发现事实遗漏时，先补充 facts.md 再更新本清单
