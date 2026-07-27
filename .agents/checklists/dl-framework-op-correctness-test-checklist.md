---
id: "dl-framework-op-correctness-test-checklist"
title: "深度学习框架算子正确性测试检查清单"
source: "docs/retrospective/reports/bug-fix/docker-build/retrospective-caffe-ops-correctness-test-20260727/"
related_patterns:
  - "C1: dockerignore-exclude-whitelist.md"
  - "C2: dl-framework-op-test-assert-unpack.md"
  - "C3: pytest-marker-positive-selection.md"
  - "C4: parametrized-test-filename-dict-serialize.md"
  - "C5: framework-param-broadcast-verification.md"
tags: ["dl-framework", "testing", "correctness", "pytest", "caffe", "checklist", "operator"]
---

# 深度学习框架算子正确性测试检查清单

> 基于 Caffe 算子正确性测试开发复盘萃取，覆盖 Docker 构建环境、测试断言、Marker 管理、参数化文件名、参数广播验证共 5 大维度。
>
> **适用场景**：为 Caffe/PyTorch/TensorFlow/ONNX 等深度学习框架编写算子正确性单元测试。

---

## 使用方法

在编写算子正确性测试前，按以下 5 个阶段逐项检查。测试提交前必须通过所有检查项。

```
阶段1：构建环境验证 → 阶段2：算子参数调研 → 阶段3：测试编写 → 阶段4：测试执行 → 阶段5：提交前检查
```

---

## 阶段1：构建环境验证（Build Environment）

### 1.1 Docker Build Context 完整性

| # | 检查项 | 反模式 | 萃取来源 |
|---|--------|--------|---------|
| 1 | ✅ **检查 `.dockerignore` 是否排除了测试脚本目录**，若排除则使用白名单回补需要的子目录 | ❌ `docker/**` 整目录排除导致 Dockerfile COPY 所需 scripts 不在 build context 中 | C1 |
| 2 | ✅ **白名单回补模式**：先排除目录，再 `!dir/subdir/` 回补需要的子目录，最后排除子目录中不需要的部分 | ❌ 简单整目录排除或全部不排除导致 build context 过大 | C1 |
| 3 | ✅ **修改 `.dockerignore` 后必须运行一次 `docker build` 验证**，确认 COPY 指令所需文件在 build context 中 | ❌ 修改 dockerignore 后不验证，CI 时才发现文件缺失 | C1 |

---

## 阶段2：算子参数调研（Parameter Semantics）

### 2.1 参数语义与广播行为验证（Pattern C5 — 最关键）

| # | 检查项 | 反模式 | 萃取来源 |
|---|--------|--------|---------|
| 4 | ✅ **查阅 proto/头文件确认算子是否存在**：搜索 proto 文件中的参数定义（如 `permute_param`、`argmax_param`），确认层已注册 | ❌ 凭直觉假设算子存在，运行时才发现 `AttributeError: no attribute 'Permute'` | C5 |
| 5 | ✅ **查阅文档/源码确认每个参数的默认值和广播行为**：标量参数是否会广播到多维度？axis 是0-based还是1-based？ | ❌ 凭 PyTorch/NumPy 经验假设参数语义，标量 offset 被广播到所有维度导致越界（Crop层教训） | C5 |
| 6 | ✅ **对于含 axis 参数的算子**：明确测试 axis=0/1/2/3 各维度的行为，确认 axis 是选择单一维度而非广播到所有后续维度 | ❌ 只测默认 axis，遗漏其他 axis 的正确性验证 | C5 |
| 7 | ✅ **对于含多维度参数的算子（如 offset/stride/pad）**：显式指定每个维度的值，不依赖标量广播默认行为 | ❌ 传单个标量 offset 给 Crop，被隐式广播到 yx 两个维度导致坐标偏移错误 | C5 |
| 8 | ✅ **不可用算子标记 `@pytest.mark.skip` 并说明原因**，保留 numpy 参考实现供未来启用时参考 | ❌ 直接删除不可用算子的测试文件，丢失参考实现 | C5 |

### 2.2 numpy 参考实现编写

| # | 检查项 | 反模式 | 萃取来源 |
|---|--------|--------|---------|
| 9 | ✅ **为每个算子编写独立的 numpy 参考实现函数**（如 `_relu_ref`、`_argmax_ref`），函数签名与算子参数对应 | ❌ 在测试函数中内联参考计算，无法复用 | C2 |
| 10 | ✅ **参考实现显式处理边界值**：负数、零值、极大值、极小值、NaN/Inf（若适用） | ❌ 参考实现只处理正数正态分布输入 | C5 |

---

## 阶段3：测试编写（Test Implementation）

### 3.1 断言函数输出解包（Pattern C2）

| # | 检查项 | 反模式 | 萃取来源 |
|---|--------|--------|---------|
| 11 | ✅ **断言函数必须处理框架返回的 list/tuple/dict 封装类型**：`net.forward()` 可能返回单元素 list `[array]` 而非直接 array | ❌ 假设 forward() 返回 numpy array，导致 shape mismatch 误报：`(1, N, C, H, W) != (N, C, H, W)` | C2 |
| 12 | ✅ **断言函数统一处理输出类型**：list→取第一个元素，dict→提取对应 blob，numpy array→直接比较 | ❌ 每个测试自行写解包逻辑，代码重复且容易遗漏 | C2 |
| 13 | ✅ **数值比较设置合理容差**：`atol=1e-5, rtol=1e-4`，整数输出（ArgMax/TopK）使用 `atol=0` | ❌ 所有算子用同一容差，整数索引比较误报浮点误差 | C2 |

### 3.2 pytest Marker 正向选择（Pattern C3）

| # | 检查项 | 反模式 | 萃取来源 |
|---|--------|--------|---------|
| 14 | ✅ **使用正向 marker 选择测试**：`pytest -m "correctness"` 只跑正确性测试 | ❌ 反向排除 `pytest -m "not slow"` 意外包含未就绪的 forward 测试 | C3 |
| 15 | ✅ **在 pytest.ini 中注册所有自定义 marker**，启用 `--strict-markers` 防止拼写错误导致测试被静默跳过 | ❌ 不注册 marker，typo（如 `@pytest.mark.correctnesss`）导致测试被静默排除 | C3 |
| 16 | ✅ **正确性测试统一使用 `@pytest.mark.correctness` 标记**，与 `@pytest.mark.edge`（边界）、`@pytest.mark.slow`（性能）区分 | ❌ 所有测试无标记，无法按类型选择性执行 | C3 |

### 3.3 参数化测试文件名唯一化（Pattern C4）

| # | 检查项 | 反模式 | 萃取来源 |
|---|--------|--------|---------|
| 17 | ✅ **动态生成 prototxt/模型文件名时，递归序列化所有参数类型**：dict→`k1-v1_k2-v2`，list→`a-b-c`，bool→`T`/`F` | ❌ 只处理 int/float/str，dict 参数被忽略，不同参数组合写入同一文件导致测试污染 | C4 |
| 18 | ✅ **验证不同参数组合生成不同文件名**：同一算子不同参数（如 alpha=0.1 vs alpha=1.0）不得写入同一 prototxt | ❌ Reshape层不同shape参数写入同一文件，后写覆盖前写导致测试结果错误 | C4 |
| 19 | ✅ **文件名中禁止使用路径分隔符 `/` `\`**，dict/list 序列化时使用 `-` 和 `_` 分隔 | ❌ dict 序列化为 `{k:v}` 含非法文件名字符导致文件创建失败 | C4 |

### 3.4 测试用例覆盖要求

| # | 检查项 | 反模式 | 萃取来源 |
|---|--------|--------|---------|
| 20 | ✅ **至少覆盖 2-3 种输入 shape**：标准 4D NCHW、2D 矩阵、可能有 1D 向量 | ❌ 只测一种 shape，维度广播问题未暴露 | C5 |
| 21 | ✅ **覆盖默认参数和非默认参数**：测试 alpha=1.0（默认）和 alpha=0.1/2.0（非默认） | ❌ 只测默认参数，自定义参数路径未验证 | C5 |
| 22 | ✅ **显式验证输出 shape**：不仅比数值，还要断言 `caffe_out[0].shape == expected_shape` | ❌ 只比数值，shape 错误但数值巧合通过 | C5 |

---

## 阶段4：测试执行（Test Execution）

### 4.1 测试运行验证

| # | 检查项 | 反模式 | 萃取来源 |
|---|--------|--------|---------|
| 23 | ✅ **运行 `pytest -m "correctness" -v` 验证所有正确性测试通过**，注意 skipped 数量是否符合预期（如不可用算子） | ❌ 只跑单个测试文件，遗漏其他文件的失败 | C3 |
| 24 | ✅ **检查 pytest 收集的测试数量**：确认没有 marker 拼写错误导致测试被意外排除 | ❌ 不检查收集数，测试被 typo marker 静默跳过却以为通过 | C3 |
| 25 | ✅ **对于输出整数索引的算子（ArgMax/TopK）**，使用 `atol=0, rtol=0` 精确比较，不允许浮点误差 | ❌ 使用默认浮点容差比较整数索引，错误索引被容差掩盖 | C2 |

---

## 阶段5：提交前检查（Pre-commit）

| # | 检查项 | 反模式 | 萃取来源 |
|---|--------|--------|---------|
| 26 | ✅ **新增算子测试文件遵循命名规范**：`test_<opname>.py`，如 `test_argmax.py`、`test_tile.py` | ❌ 文件命名不统一，难以按算子名查找 | C3 |
| 27 | ✅ **不可用算子的 skip 原因写明**：缺什么参数定义/什么层类，附参考实现 | ❌ `@pytest.mark.skip` 不写 reason，后人不知道为什么跳过 | C5 |
| 28 | ✅ **测试文件开头注释引用本 Checklist 或相关模式**，方便后人理解测试设计遵循的规范 | ❌ 无文档说明测试遵循的规范，新人踩同样的坑 | C1-C5 |
| 29 | ✅ **不提交临时调试数据/模型文件**：`tmp_path` fixture 自动清理，不手动写固定路径 | ❌ 将 caffemodel/prototxt 写入 tests/ 目录并提交 | C4 |
| 30 | ✅ **运行已有的其他算子测试确保无回归**：新测试不破坏旧测试的文件名/目录 | ❌ 新测试文件名与旧测试冲突覆盖文件 | C4 |

---

## 附录：算子测试模板

```python
import logging
import numpy as np
import pytest
from utils import L, _test_op, assert_op_correct

logger = logging.getLogger(__name__)


def _test_opname(data, test_dir, **kwargs):
    """Test helper for <OpName>."""
    logger.debug(f"<OpName> params: {kwargs}")
    return _test_op(data, L.<OpName>, "<OpName>", test_dir, **kwargs)


def _opname_ref(x, param1=default1, param2=default2):
    """Numpy reference implementation for <OpName>.
    描述算子数学公式和参数语义。
    """
    # numpy reference implementation
    return result.astype(np.float32)


@pytest.mark.correctness
def test_opname_correctness(caffe_test_dir):
    """<OpName> correctness test with numpy reference."""
    logger.info("Running test_opname_correctness")
    np.random.seed(42)
    # Test cases covering multiple shapes and parameter combinations
    ...
    ref = _opname_ref(x, param1=val1, param2=val2)
    caffe_out = _test_opname(x, caffe_test_dir, opname_param={"param1": val1, "param2": val2})
    assert_op_correct(caffe_out, ref, op_name=f"<OpName>(p1={val1},p2={val2})")
    assert caffe_out[0].shape == expected_shape
```

---

## 历史

- **2026-07-27**：初版，基于 Caffe 算子正确性测试复盘萃取 5 个候选模式
