---
id: progressive-interface-extension
title: 框架接口渐进式扩展
type: code
date: 2026-07-31
maturity: L1-draft
source: 2026-07-31-caffe-ffi-backward-logging-milestone-retro.md
related_patterns:
  - four-step-extension-recipe
  - configurable-by-default-principle
tags:
  - c++
  - api-design
  - framework
  - backward-compatibility
  - refactoring
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/progressive-interface-extension.toml"
---

# 框架接口渐进式扩展

## 触发场景

- 当在基类/框架接口中添加新虚方法，影响N≥3个子类时
- 当部分子类暂不需要或尚未实现该功能时
- 当调用路径尚未完全打通（如训练模式Backward路径在推理框架中不存在）时
- 适用于：抽象基类演进、插件系统新API添加、SDK版本升级、框架功能分期上线
- 不适用于：
  - ❌ 影响<3个子类的小改动（直接实现即可，不需要渐进）
  - ❌ 调用路径已完全打通且所有子类必须立即实现（可用纯虚强制）
  - ❌ 接口已废弃移除（用deprecated标记而非渐进扩展）

## 核心做法

1. **第一步：默认存根阶段**
   - 在基类添加虚方法，**不要设为纯虚**
   - 提供默认实现：要么输出WARN日志提示"未实现"，要么在调用路径激活时THROW明确异常
   - 保证现有代码能编译通过，不会出现N个子类同时编译失败的"大爆炸"

2. **第二步：分批按优先级实现**
   - 按P0/P1/P2优先级分批实现子类：P0是核心路径必须立即实现，P1是常用层近期实现，P2是边缘层按需实现
   - 每批次实现后跑测试，避免一次性改太多难以审查
   - 每批次提交独立原子commit，便于回滚

3. **第三步：调用路径激活时切换为强制**
   - 当上层调用路径（如Net::Backward编排方法）真正实现并启用时
   - 将基类默认实现从WARN切换为THROW异常（未实现即报错）
   - 最终当所有子类都实现后，可考虑切换为纯虚方法（但这一步可选，THROW已经足够安全）

## 反模式（不要这么做）

- ❌ **反模式1：一开始就纯虚**
  - 表现：添加新方法直接设为`=0`纯虚
  - 后果：所有现有子类同时编译失败，阻断整个开发流程；尤其是在调用路径还没打通时，纯虚强制实现的方法永远不会被调用，是无效代码

- ❌ **反模式2：默认空函数静默**
  - 表现：默认实现是`{}`空函数，什么也不做
  - 后果：子类忘记实现时静默失败，没有任何错误提示，调试极难；梯度消失等问题根源可能就在空实现的Backward中

- ❌ **反模式3：大爆炸式全部实现**
  - 表现：一次性修改所有21个子类，在一个PR/ commit中提交
  - 后果：Code Review困难（几百行diff无法细看）；引入bug难以定位是哪个子类改坏了；回滚成本极高

## 检验标准

做完之后怎么知道做对了？
- 标准1：添加新虚方法后，现有代码（未实现该方法的子类）能正常编译通过
- 标准2：调用未实现的方法时，有明确的WARN日志或THROW异常，不是静默失败
- 标准3：子类实现分批次提交，每个commit < 200行，审查负担可控
- 标准4：调用路径激活时，默认实现升级为THROW，未实现的子类会被立即发现
- 标准5：没有出现"为了通过编译而写的空实现/桩代码"残留到生产环境

## 迁移示例

这个模式还能用在什么其他场景？

- **场景1：插件系统新API**：IDE/编辑器插件架构添加新生命周期方法（如onWorkspaceDidSave），老插件不需要立即实现，用WARN默认实现；IDE版本大升级时再切换为THROW
- **场景2：SDK版本升级**：支付SDK添加新支付渠道接口，旧版本商户代码不需要立即适配；在下一个major版本中标记为必须实现
- **场景3：Web框架新中间件钩子**：Web框架添加新的请求后处理钩子，现有中间件不需要全部重写；等框架3.0版本发布时切换为强制
- **场景4：游戏引擎新组件接口**：游戏引擎添加新的物理碰撞回调，现有游戏对象不需要立即实现；物理系统正式启用时升级为THROW

## 实施检查清单

- [ ] 计算影响的子类数量：≥3个才用渐进式，<3个直接实现
- [ ] 确认调用路径状态：未打通则WARN默认实现，已打通则考虑THROW
- [ ] 基类添加虚方法，带明确日志/异常消息（包含类名/方法名/提示信息）
- [ ] 列出子类优先级清单：P0立即实现，P1近期实现，P2按需实现
- [ ] P0批次实现并提交，验证核心路径工作正常
- [ ] 在Backlog/任务系统中登记P1/P2实现任务
- [ ] 登记"切换为THROW"的触发条件（即调用路径何时激活）
- [ ] 调用路径激活时，执行切换：默认实现从WARN→THROW
- [ ] 跑全量测试，确认所有应该实现的子类都已实现

## 代码审查速查

快速审查接口扩展代码时，使用 [框架扩展与性能日志CR清单](../../../../checklists/framework-extension-and-perf-logging-review.md#二框架接口渐进式扩展检查) 逐项对照。

## 实际案例（Caffe-ffi Backward扩展）

本模式提炼自caffe-ffi Backward_cpu接口扩展：

- **背景**：layer.hpp基类只有Forward_cpu纯虚方法，需要添加Backward_cpu虚方法支持训练；共21个层子类；当前框架是推理模式，Net::Backward编排方法尚未实现
- **错误做法（规避）**：一开始就设Backward_cpu为纯虚，导致21个层全部编译失败
- **正确实施**：
  1. Backward_cpu提供默认WARN实现：`LOG(WARNING) << "Backward_cpu not implemented for " << type();`
  2. P0批次：先实现Sigmoid+ReLU两个核心激活层的Backward_cpu
  3. 登记任务：剩余19个层分批实现
  4. 未来：Net::Backward实现时，将默认实现切换为THROW异常
- **结果**：核心层Backward可用，其他层编译正常，调用路径未打通时不会出现静默错误

## 与现有模式的关系

| 关联模式 | 关系 |
|---------|------|
| [four-step-extension-recipe.md](../architecture-patterns/four-step-extension-recipe.md) | 四步法是新算子扩展流程，本模式是基类接口演进策略，互补使用 |
| [configurable-by-default-principle.md](configurable-by-default-principle.md) | 默认配置原则与本模式思想一致：提供安全默认，按需覆盖 |
| [legacy-integration-dual-track.md](../architecture-patterns/legacy-integration-dual-track.md) | 遗留系统双轨集成也体现了渐进式演进思想 |
