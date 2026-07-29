---
title: 导出建议
source: caffe.py RMSNorm transpose removal
---
# 导出建议

## 萃取模式

本次复盘萃取2个L2（已验证）代码级模式，已入库：

### 模式1：API参考验证模式
- **文件**：[api-reference-verification.md](../../../patterns/code-patterns/api-reference-verification.md)
- **成熟度**：L2 已验证（基于本次caffe.py优化实践+TVM rms_norm参考实现验证+1250个数值测试）
- **核心要点**：使用算子/API前执行"参考实现验证三步法"——查参考实现→查API签名→查调用示例，消除基于经验假设引入的冗余操作
- **反模式信号**：transpose+op+transpose三段式结构、注释声称API"只能/总是"做某事、20+行的适配规划函数

### 模式2：TryPrepare判定准备合并模式
- **文件**：[try-prepare-merge.md](../../../patterns/code-patterns/try-prepare-merge.md)
- **成熟度**：L2 已验证（基于本次_try_prepare_rmsnorm_conversion重构实践）
- **核心要点**：将"判定是否适用(should_X)"和"准备参数(prepare_X)"合并为`_try_prepare_X()`函数，成功返回参数元组，失败返回(None,...)，消除重复计算和调用方记忆负担
- **适用边界**：判定过程需要计算（非简单标志检查），且准备过程代价不高（非IO/网络级操作）

## 代码模式索引更新

已更新 [code-patterns/README.md](../../../patterns/code-patterns/README.md) 模式清单表，新增2个条目：
- `api-reference-verification.md` — API参考验证三步法
- `try-prepare-merge.md` — TryPrepare判定准备合并模式

代码模式总数：64个。

## 行动项

| 行动项 | 优先级 | 说明 |
|--------|--------|------|
| 审查caffe.py中其他前端转换逻辑中是否存在类似的"基于错误假设的transpose"模式 | 中 | 重点关注有transpose成对出现的算子转换代码 |
| 审查npu_tvm中其他前端(onnx/tensorflow/pytorch)的转换代码是否存在同样问题 | 低 | 跨框架推广API参考验证模式 |
| 在TVM算子使用规范中加入"使用前查阅topi/testing/参考实现"的检查项 | 低 | 长期措施：建立团队编码纪律 |

## 经验教训总结

1. **经验是双刃剑**：领域经验（"RMSNorm归一化最后一维"）在特定上下文中正确（LLaMA实现），但在通用框架上下文中可能不成立（TVM通用rms_norm算子）。对经验性假设保持怀疑，用源码事实验证。

2. **"简化"优于"优化"**：第一轮优化虽然改进了代码结构（合并函数、提取变量），但没有触及最根本的问题（错误假设导致的冗余transpose）。真正的性能提升来自于消除不必要的操作，而不是优化包含不必要操作的代码。

3. **参考实现是全维度权威**：参考实现不仅提供数学正确性基准，更是API使用方式的最直接范例。对照参考实现时要同时关注"怎么算"和"怎么调用"两个维度。

4. **用户是最好的代码审查者**：用户通过提供参考文件路径直接指出了优化方向，这比AI自主探索更高效。当用户提供参考文件时，应逐行对照而非仅提取数学公式。
