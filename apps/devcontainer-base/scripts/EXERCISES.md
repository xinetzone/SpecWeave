# ONNX 量化实操演练任务清单

> **面向读者**：刚加入团队的新成员  
> **目标**：通过 7 个渐进式练习，掌握 ONNX 量化工具包的核心使用方法  
> **预计时间**：60-90 分钟  
> **前置条件**：已阅读 [QUICKSTART.md](QUICKSTART.md)，环境已配置（onnxruntime ≥ 1.20）

---

## ✅ 练习 0：环境验证（5 分钟）

**目标**：确认环境就绪，工具包可正常导入和运行。

**任务**：
- [ ] 进入 `apps/devcontainer-base/scripts/` 目录
- [ ] 运行 `python -c "from onnx_quantize_kit import auto_quantize; print('OK')"`，输出 `OK`
- [ ] 运行 `python test_quantize_kit.py`，确认所有测试通过（期望 `37 passed, 0 failed`）
- [ ] 运行 `python onnx-quantize.py --help`，确认 CLI 工具可用

**验收标准**：
- 导入无报错，测试全绿，CLI help 正常输出

**遇到问题？** 检查 `PYTHONPATH` 是否包含 scripts 目录，参考 QUICKSTART.md §1.1。

---

## ✅ 练习 1：你的第一次量化（10 分钟）

**目标**：使用 Python API 和 CLI 两种方式完成一个模型的自动量化。

**任务**：
- [ ] 用 PyTorch 创建一个简单 MLP 模型（Linear→ReLU→Linear），导出为 ONNX（opset ≥ 17）
- [ ] 用 `auto_quantize()` 自动量化，打印 `strategy_used`、`speedup`、`max_diff`
- [ ] 用 CLI 工具 `python onnx-quantize.py model.onnx` 完成同样的量化
- [ ] 对比两次量化结果（策略是否一致、加速比是否接近）
- [ ] 用 `--info` 参数查看模型信息，确认类型检测正确

**参考代码**：
```python
import torch, torch.nn as nn
class SimpleMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(128, 256), nn.ReLU(), nn.Linear(256, 10))
    def forward(self, x): return self.net(x)

m = SimpleMLP().eval()
torch.onnx.export(m, torch.randn(1, 128), "mlp.onnx",
                  input_names=["input"], output_names=["output"], opset_version=18)
```

**验收标准**：
- 输出模型文件存在且可被 onnxruntime 加载推理
- CLI 彩色输出正常显示 Strategy Chain 和 Comparison 表格

---

## ✅ 练习 2：理解回滚机制（15 分钟）

**目标**：亲眼观察自动回滚机制如何工作，理解策略选择链。

**任务**：
- [ ] 阅读 `onnx_quantize_kit/quantize.py` 中 `_build_fallback_chain()` 函数，画出策略回退链
- [ ] 设置一个极端严格的精度阈值（`max_diff=0.0001`），对练习 1 的 MLP 模型运行量化，观察回滚过程
- [ ] 用 `--strict` 模式运行 CLI 量化，对比默认阈值的区别
- [ ] 阅读 `test_quantize_kit.py` 中的 **Test 4**（回滚机制测试），理解测试如何构造"不可能通过"的阈值
- [ ] （选做）运行 Test 4b 相关代码片段，观察 Transformer 模型的"精度灾难"现象

**关键观察点**：
- 回滚链中每个策略的 max_diff 和 speedup 变化
- 哪个策略在你的模型上最终成功？为什么？
- 为什么小模型可能所有策略都被拒绝（speedup < 1.0x）？

**验收标准**：
- 能解释 4 种策略（static_qdq / static_qoperator / dynamic / fp16）的区别和适用场景
- 能解释为什么回滚链中 dynamic 在 fp16 之前

---

## ✅ 练习 3：模型类型检测与策略推荐（10 分钟）

**目标**：理解自动检测逻辑，学会为不同类型模型选择合适策略。

**任务**：
- [ ] 阅读 `onnx_quantize_kit/model_detect.py` 中的检测逻辑
- [ ] 分别创建三类模型并导出 ONNX：
  - MLP（全连接网络，≥3 层 Linear）
  - CNN（包含 Conv2d 层）
  - Transformer（使用 nn.TransformerEncoder 或自定义 Attention）
- [ ] 对每个模型运行 `python onnx-quantize.py model.onnx --dry-run`，记录推荐的策略和回退链
- [ ] 用 `detect_model_type()` API 验证检测结果是否正确
- [ ] 强制对 Transformer 模型使用 `--strategy static_qdq`，观察精度灾难和自动回滚

**思考题**：
- 为什么 CNN 推荐 static_qdq 而 MLP 推荐 static_qoperator？
- Transformer 为什么默认不推荐静态量化？

**验收标准**：
- 三类模型均能被正确检测类型
- Transformer 静态量化确实触发回滚并最终选择 dynamic 或 fp16

---

## ✅ 练习 4：校准数据实践（10 分钟）

**目标**：理解校准数据的重要性，学会提供真实校准数据。

**任务**：
- [ ] 创建一个 CNN 模型（如 3 层 Conv2d），导出 ONNX
- [ ] 使用默认随机校准数据运行静态量化，记录 max_diff
- [ ] 准备校准数据目录：用 numpy 生成 100 个与真实输入分布相同的 `.npy` 文件
  ```python
  import numpy as np, os
  os.makedirs("calib_data", exist_ok=True)
  for i in range(100):
      # 模拟真实数据分布（非随机噪声）
      sample = np.random.randn(1, 3, 32, 32).astype(np.float32) * 0.5 + 0.3
      np.save(f"calib_data/calib_{i:04d}.npy", sample)
  ```
- [ ] 用 `-d calib_data/` 参数使用真实校准数据重新量化，对比 max_diff 差异
- [ ] 故意使用分布不匹配的校准数据（如全零或范围异常的数据），观察精度下降

**关键观察点**：
- 校准数据分布对静态量化精度的影响
- 为什么 RandomCalibrationReader 只作为"兜底"而非推荐用法？

**验收标准**：
- 能解释校准数据的作用
- 能独立创建 FileCalibrationReader 可用的校准数据目录

---

## ✅ 练习 5：CLI 工具高级用法（10 分钟）

**目标**：熟练使用 CLI 工具的各种模式，适配本地开发场景。

**任务**：
- [ ] **预览模式**：对模型使用 `--dry-run`，确认不生成输出文件
- [ ] **信息模式**：使用 `--info` 快速查看模型结构、类型、输入输出
- [ ] **JSON 模式**：使用 `--json` 获取结构化输出，用 `jq` 或 Python 解析关键字段
  ```bash
  python onnx-quantize.py model.onnx --json | python -c "import sys,json; d=json.load(sys.stdin); print(d['strategy_used'], d['speedup'])"
  ```
- [ ] **自定义阈值**：用 `--max-diff 0.01` 设置精度阈值，观察何时触发回滚
- [ ] **排除节点**：创建一个含 LayerNorm 的模型，使用 `--exclude-nodes` 排除敏感节点后静态量化
- [ ] **指定策略**：用 `--strategy fp16` 强制 FP16，对比 INT8 量化的精度和速度差异

**验收标准**：
- 能独立使用 CLI 完成"查看模型→预览策略→执行量化→查看结果"完整流程
- 理解 `--strict` / `--relaxed` / `--max-diff` 三种精度控制方式的区别

---

## ✅ 练习 6：Python API 精细控制（15 分钟）

**目标**：掌握 Python API 的高级用法，能编写自定义量化脚本。

**任务**：
- [ ] 阅读 `onnx_quantize_kit/__init__.py`，列出所有公开 API
- [ ] 编写一个 Python 脚本，完成以下流程：
  1. 加载 ONNX 模型
  2. 检测模型类型并获取推荐配置
  3. 使用自定义 `CalibrationDataReader`（继承基类）提供校准数据
  4. 调用 `auto_quantize()` 执行量化
  5. 遍历 `result.all_attempts`，打印每个策略的尝试结果
  6. 将结果保存为 JSON 报告
- [ ] 使用 `benchmark_model()` 单独对量化前后的模型做性能基准测试
- [ ] 使用 `quantize_model()` 单独执行量化（不自动回滚），对比与 `auto_quantize()` 的区别

**参考骨架**：
```python
from onnx_quantize_kit import (
    auto_quantize, QuantizationConfig, AccuracyThresholds,
    detect_model_type, benchmark_model, CalibrationDataReader,
)
import numpy as np, json

class MyCalibReader(CalibrationDataReader):
    # 实现 __init__, get_next, rewind
    pass

model_type = detect_model_type("model.onnx")
print(f"Detected: {model_type}")

config = QuantizationConfig(strategy="auto", ...)
result = auto_quantize("model.onnx", "out.onnx", calib_reader=..., config=config)
print(f"Success: {result.success}, Strategy: {result.strategy_used}")
```

**验收标准**：
- 脚本能独立运行并输出完整量化报告
- 自定义 CalibrationDataReader 能正常工作
- 能区分 `auto_quantize()`（自动回滚）和 `quantize_model()`（单策略）的使用场景

---

## ✅ 练习 7：CI 门禁集成模拟（10 分钟）

**目标**：理解量化工具如何在 CI 流水线中工作，能配置自动化门禁。

**任务**：
- [ ] 阅读 `ci_quantization_gate.py` 的源码，理解退出码含义（0/1/2/3）
- [ ] 使用 `ci_quantization_gate.py` 对你的模型运行量化并生成 JSON 报告
  ```bash
  python ci_quantization_gate.py -m model.onnx -o model_q.onnx --report report.json --ci
  ```
- [ ] 检查报告 JSON 中的字段，理解 CI 如何根据报告判断是否通过
- [ ] 故意制造一个会导致量化失败的场景（如损坏的模型文件），观察退出码
- [ ] 对比 `ci_quantization_gate.py`（CI 场景）和 `onnx-quantize.py`（本地开发场景）的设计差异

**思考题**：
- CI 工具为什么用 `--ci` 模式禁用彩色输出？
- CI 工具和本地 CLI 工具在参数设计上有什么不同？为什么？

**验收标准**：
- 能解释 4 个退出码各自的含义
- 能独立运行 ci_gate 并解读 JSON 报告

---

## 🎯 完成自检清单

完成以上 7 个练习后，确认你能够：

- [ ] 解释 ONNX 量化的 4 种策略及其适用场景
- [ ] 描述自动回滚机制的完整策略链
- [ ] 解释为什么 Transformer 模型静态量化容易精度灾难
- [ ] 使用 CLI 工具一键量化模型，读懂彩色输出
- [ ] 使用 Python API 进行精细控制和自定义
- [ ] 准备校准数据并理解其对静态量化精度的影响
- [ ] 理解 CI 门禁工具和本地 CLI 工具的区别
- [ ] 阅读并运行测试套件，定位量化失败的原因

---

## 📚 进阶学习路径

完成基础练习后，可以深入：

1. **阅读源码**：`quantize.py` 中的 `_try_strategy()` 函数是核心逻辑
2. **ONNX Runtime 官方文档**：https://onnxruntime.ai/docs/performance/quantization.html
3. **量化算法原理**：QDQ vs QOperator 格式、对称/非对称量化、per-channel/per-tensor
4. **性能调优**：线程数、opset 版本、图优化级别对量化效果的影响
5. **敏感层处理**：学习如何使用 `exclude_nodes` 跳过 LayerNorm/Softmax 等敏感层
