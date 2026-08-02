---
id: separate-nets-independent-ops
title: 独立操作分离Net
type: code
date: 2026-08-01
maturity: L2-validated
source:
  - retrospective-caffe-ffi-p3b-test-milestone-20260731 (Eltwise SUM/PROD/MAX对比)
  - test_p3a_conv_pool_bn.py参数组合测试
related_patterns:
  - explicit-split-multi-consumer
tags: [testing, deep-learning, test-isolation, graph-topology, caffe]
validation_count: 2
reuse_count: 0
---

# 独立操作分离Net

## 触发场景

- 当需要对比同一层/同一算子的不同参数变体时（如Eltwise的SUM/PROD/MAX、Concat的不同axis）
- 当多个独立测试操作会导致Blob消费冲突时
- 当担心一个操作的副作用影响另一个操作的测试结果时
- 适用于：DL框架算子对比测试、参数组合遍历测试、有单消费/状态副作用的框架测试
- 不适用于：同一网络内的多节点组合测试（这时候应该用explicit-split-for-multi-consumer模式）、需要共享权重初始化的关联测试

## 核心做法

1. **识别独立性边界**：如果多个操作之间不需要共享中间blob、不需要在同一网络内形成数据流，它们就是独立的
2. **每个变体一个独立Net**：对于不同参数组合/不同操作类型，每个都创建一个独立的Net实例，而不是塞进同一个Net里
3. **提取公共构造函数**：写一个辅助函数（如`_make_eltwise_net(op, coeffs=None)`）接收参数，返回构建好的Net
4. **测试参数化**：使用`@pytest.mark.parametrize`遍历参数组合，每个参数组合在独立Net中运行
5. **Net生命周期隔离**：每个测试函数/参数用例自己创建Net，测试结束后Net自然销毁，不跨测试复用
6. **输入共享但不污染**：输入numpy数组可以共享（按值传入Forward），但Net本身和Blob不共享

## 反模式（不要这么做）

- ❌ **反模式1：一个Net塞所有变体**：在同一个prototxt里定义多个平行分支（如a→eltwise_sum→out_sum, a→eltwise_prod→out_prod）。后果：需要大量Split处理blob消费冲突，prototxt复杂难维护，一个分支出错影响其他分支
- ❌ **反模式2：跨测试复用Net实例**：在setup_class/模块级创建一次Net，所有测试方法复用。后果：一个测试修改了权重/状态，后续测试受污染；COW/引用计数问题跨测试传播；测试顺序依赖
- ❌ **反模式3：不提取辅助函数**：每个参数变体都复制粘贴整个prototxt构建代码，只有一行差异。后果：代码重复率高，修改prototxt模板时需要改N处，容易遗漏
- ❌ **反模式4：强行组合不相关操作**：为了"少建Net"把逻辑上不相关的层硬塞到同一个Net里。后果：引入不必要的拓扑依赖，一个blob形状错误导致整个Net无法构建，测试隔离性丧失
- ❌ **反模式5：忘记in-place副作用**：Net复用时假设forward是纯函数，但有些层可能有in-place修改或状态变化。后果：前一个测试遗留的状态导致后一个测试失败，且难以复现

## 检验标准

做完之后怎么知道做对了？
- 标准1：同一操作类型的不同参数变体都在独立Net中运行
- 标准2：有一个统一的`_make_xxx_net()`辅助函数接收参数，prototxt模板只有一份
- 标准3：使用`@pytest.mark.parametrize`或循环遍历参数，而非复制粘贴测试代码
- 标准4：每个测试函数独立创建Net，没有跨测试/跨用例的Net复用
- 标准5：单个参数变体的测试失败不会影响其他变体的执行和结果
- 标准6：prototxt简洁，每个Net只做一件事，没有大量平行分支和Split

## 迁移示例

这个模式还能用在什么其他场景？
- 场景1（API参数测试）：测试一个API的不同flag/参数组合时，每个参数组合使用独立的测试客户端/独立请求上下文，而不是复用同一个连接做所有测试
- 场景2（编译器选项测试）：测试不同编译优化级别（O0/O1/O2/O3）时，每个级别单独构建独立的构建目录和编译产物，不共用build目录避免增量编译污染
- 场景3（数据库隔离测试）：每个DAO/Repository测试使用独立的数据库事务或独立的in-memory DB，测试结束回滚/销毁，不共享数据库状态
- 场景4（配置组合测试）：测试不同配置组合（如cache=on/off、auth=none/jwt）时，每个配置组合启动独立的应用实例，不在同一实例内热切换配置
- 场景5（图像处理filter测试）：测试不同滤镜/参数时，每个滤镜应用到原始图片副本上，而非串联应用（避免前一个滤镜的结果影响后一个）
