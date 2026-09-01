---
id: three-layer-test-validation
title: 三层测试验证法
type: code
date: 2026-08-01
maturity: L2-validated
source:
  - retrospective-caffe-ffi-p3a (Conv/Pool/BN测试)
  - retrospective-caffe-ffi-p3b-test-milestone-20260731
related_patterns:
  - numpy-reference-first
  - zero-copy-tensor-verification
tags: [testing, test-strategy, numerical-correctness, determinism, deep-learning]
validation_count: 2
reuse_count: 0
---

# 三层测试验证法

## 触发场景

- 当需要全面验证一个算子/层的forward计算正确性时
- 当担心边界情况、数值精度、非确定性问题时
- 当编写P2/P3级别的组合测试/集成测试时
- 适用于：深度学习算子测试、数值计算函数测试、数学库验证
- 不适用于：纯结构测试、错误路径测试、仅需smoke test的原型代码

## 核心做法

对每个被测层/算子，必须包含三类测试用例，形成从点到面的覆盖：

1. **第一层：已知值精确验证（Known Values）**
   - 使用手工构造的极小输入（如1x1x2x2、全1输入、identity矩阵）
   - 手算或通过numpy参考计算精确期望值
   - 验证在最简情况下实现完全正确
   - 作用：捕获最基础的逻辑错误（如axis搞反、系数用错、符号错误）

2. **第二层：随机数据Numpy匹配**
   - 使用固定seed（如42）生成中等规模随机输入
   - 与numpy参考实现输出对比，使用合理的rtol/atol
   - 覆盖各种参数组合（如不同axis、不同operation、不同shape）
   - 作用：在广泛输入空间验证数值正确性，覆盖边界情况和参数组合

3. **第三层：重复前向确定性验证（Repeated Determinism）**
   - 使用相同输入连续forward两次/多次
   - 验证两次输出完全相等（或在浮点误差内一致）
   - 验证权重不被意外修改（weights不变性）
   - 作用：捕获非确定性问题、内存泄漏、in-place错误、状态污染

4. **（可选）第四层：边界与极端输入**
   - 全零输入、全一输入、极大值/极小值、NaN/Inf防护
   - 作用：验证饱和行为、数值稳定性、异常处理

## 反模式（不要这么做）

- ❌ **反模式1：只测随机数据**：没有known values测试，用np.allclose对比随机输入。后果：整体形状/scale正确但系数错0.5倍、axis搞反这类错误可能被容差掩盖
- ❌ **反模式2：只测known values**：只测1-2个手工用例就认为正确。后果：过拟合简单用例，复杂shape/参数组合下的bug无法发现
- ❌ **反模式3：不测确定性**：每个测试只forward一次，不验证重复运行一致性。后果：内存覆盖、未初始化变量、COW错误等非确定性bug溜到生产
- ❌ **反模式4：容差设置过宽**：rtol=1e-2甚至更大来"让测试通过"。后果：失去数值测试的意义，相当于没有测试
- ❌ **反模式5：不验证权重不变性**：只看输出对不对，不检查forward后weights是否被修改。后果：推理时悄悄修改权重的bug无法发现

## 检验标准

做完之后怎么知道做对了？
- 标准1：每个测试类都有明确的三类用例划分（test_known_*、test_random_*、test_repeated_*）
- 标准2：known values测试用的输入极小（≤4个元素），期望值可手算验证
- 标准3：随机测试固定np.random.seed，避免偶发失败
- 标准4：repeated forward测试连续运行≥2次，使用np.array_equal或极严容差验证完全一致
- 标准5：有weights不变性检查（forward前后blobs[0]数据完全相同）
- 标准6：rtol/atol根据算子类型合理选择（激活层1e-6、乘加1e-5、BN1e-4）

## 迁移示例

这个模式还能用在什么其他场景？
- 场景1（API测试）：第一层：简单请求验证（已知输入→已知输出）；第二层：fuzz随机请求对比参考实现；第三层：重复请求验证幂等性
- 场景2（编译器测试）：第一层：小代码片段（如1+1）验证；第二层：随机生成程序对比解释器输出；第三层：多次编译+运行验证二进制确定性
- 场景3（序列化测试）：第一层：已知对象序列化/反序列化精确匹配；第二层：随机对象往返对比；第三层：多次序列化输出字节级一致
- 场景4（加密函数测试）：第一层：标准测试向量（如AES test vectors）；第二层：随机明文/密钥对比参考实现；第三层：相同输入多次加密输出一致（或IV正确变化）
