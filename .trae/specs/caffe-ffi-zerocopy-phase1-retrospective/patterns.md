# E阶段 - 可复用模式萃取

> G3质量门：每个模式包含触发场景、核心步骤（3-7步）、反模式（≥3个）、检验标准、迁移示例（≥1个非当前场景）
>
> **归档状态**：✅ 已归档至模式库 (2026-07-31)
> - PAT-001 → [code-patterns/ffi-intrusive-refcount-zerocopy.md](../../.agents/docs/retrospective/patterns/code-patterns/ffi-intrusive-refcount-zerocopy.md)（L2-validated, validation_count: 2）
> - PAT-002 → [architecture-patterns/raw-pointer-ffi-smart-pointer-bridge.md](../../.agents/docs/retrospective/patterns/architecture-patterns/raw-pointer-ffi-smart-pointer-bridge.md)（L1-draft, validation_count: 1）

---

## PAT-001: FFI侵入式引用计数零拷贝张量共享模式

```yaml
---
id: PAT-001
title: FFI侵入式引用计数零拷贝张量共享
type: code
date: 2026-07-31
maturity: L1-draft
source: I1, I4 (Split层零拷贝Phase 1复盘)
related_patterns: [PAT-002]
tags: [zero-copy, tvm-ffi, refcount, tensor-sharing, performance]
---
```

### 触发场景
- 当基于引用计数对象系统（如TVM FFI Object）实现张量/数据容器时
- 当需要在多个对象之间共享大块数据缓冲区以消除memcpy开销时
- 当存在N=1 fan-out（identity passthrough）这种写冲突风险为零的场景时
- 适用于：深度学习框架的层间数据传递、DLPack跨框架零拷贝、多视图数据共享
- 不适用于：N≥2 fan-out且存在就地修改(in-place write)风险的场景（需COW）、需要独占所有权的场景

### 核心做法
1. **选择最小充分机制**：使用对象系统已有的侵入式引用计数（如TVM FFI Tensor的ObjectPtr）作为共享机制，不自行实现引用计数或共享指针
2. **API分对设计**：提供Share()/SharesWith()方法对——Share()执行引用计数赋值（零拷贝），SharesWith()验证两个对象是否指向同一内存（用于测试和断言）
3. **显式打断语义**：明确规定哪些操作会打断共享关系（如Reshape()分配新内存时必须断开共享），并在打断时输出日志
4. **N=1捷径先行**：先实现最安全的N=1 identity场景，充分验证引用计数机制正确性后，再考虑N≥2的COW扩展
5. **性能埋点**：在共享路径添加结构化性能日志，包含share_time(μs)、shared_bytes、memcpy_saved、ptr_equal等字段
6. **单元测试三件套**：编写指针相等测试(Share→ptr_equal)、引用计数测试(use_count变化)、共享打断测试(Reshape→ptr_not_equal)

### 反模式（不要这么做）
- ❌ **反模式1：自行实现引用计数**：不使用对象系统已有的refcount，而是自己写shared_ptr或手动引用计数——容易与vendor的TypeTraits、对象生命周期机制冲突（对应I1 TypeTraits重复定义问题）
- ❌ **反模式2：不加区分地全场景共享**：在N≥2场景直接共享而不做COW保护——导致一个top的就地修改污染其他top的数据
- ❌ **反模式3：不定义共享打断语义**：Share()之后不说明Reshape()/mutable_data()等操作是否会断开共享——其他开发者可能依赖共享状态做假设，在共享被意外打断后出现悬空指针或数据不一致
- ❌ **反模式4：跳过N=1验证直接做COW**：在引用计数共享机制本身未经验证时就实现复杂的COW触发逻辑——出问题时无法定位是共享机制本身的bug还是COW逻辑的bug

### 检验标准
做完之后怎么知道做对了？
- 标准1：Share()后两个对象的data_ptr()返回相同地址
- 标准2：共享Tensor的引用计数(use_count)正确增加和减少
- 标准3：Reshape()或其他分配新内存的操作后，SharesWith()返回false
- 标准4：N=1场景的性能日志中memcpy_saved等于单次memcpy数据量，share_time在微秒级
- 标准5：C++单元测试覆盖指针相等、引用计数、共享打断三个场景
- 标准6：Python端回归测试通过，功能等价（共享不影响计算结果正确性）

### 迁移示例
这个模式还能用在什么其他场景？
- **场景1（其他CNN层）**：Eltwise层在N=1且操作是identity时也可以零拷贝传递；Dropout层在inference模式下可以直接共享输入输出
- **场景2（跨领域，DLPack）**：NumPy ndarray与PyTorch Tensor通过DLPack协议零拷贝共享底层数据，DLPack胶囊(capsule)的引用计数机制与TVM FFI ObjectPtr原理相同
- **场景3（非深度学习，字符串池）**：编译器/解释器中的字符串驻留(string interning)，多个AST节点共享同一字符串常量，使用引用计数管理生命周期

---

## PAT-002: 内部原始指针+FFI智能指针桥接模式

```yaml
---
id: PAT-002
title: 内部原始指针+FFI智能指针桥接
type: architecture
date: 2026-07-31
maturity: L1-draft
source: I2 (Blob API设计复盘)
related_patterns: [PAT-001]
tags: [api-design, ffi, raw-pointer, smart-pointer, bridge-pattern]
---
```

### 触发场景
- 当C++类库同时被内部C++代码（使用原始指针遍历/访问）和外部FFI绑定（使用智能指针/ObjectPtr管理生命周期）调用时
- 当框架层容器存储原始指针（如std::vector<T*>），但公共API需要考虑跨语言调用的生命周期安全时
- 适用于：带Python/JS/Rust等语言绑定的C++库、游戏引擎的ECS系统（组件用原始指针访问但用智能指针管理）、插件架构（内部高性能访问+外部安全API）
- 不适用于：纯C++内部库（无FFI需求）、完全由智能指针管理的应用层代码

### 核心做法
1. **内部API接收原始指针**：类的公共方法（如ShareData、SharesDataWith）使用`T*`或`const T*`作为参数类型，而非`const ObjectPtr<T>&`或`shared_ptr<T>`
2. **入口处做null检查**：在方法入口统一用`ptr != nullptr`做null校验，不依赖智能指针特有的`defined()`或`operator bool()`方法
3. **FFI层lambda桥接**：在FFI注册代码中，使用lambda捕获参数类型转换：`[](T* self, const ObjectPtr<T>& other) { self->method(other.get()); }`
4. **参数校验前置**：在内部方法中做参数校验（如CHECK_NOTNULL、CHECK_TYPE），不在FFI lambda中重复校验
5. **返回值策略一致**：返回内部对象数据时，返回原始指针或值类型（非智能指针），FFI层根据需要包装

### 反模式（不要这么做）
- ❌ **反模式1：公共API只使用智能指针**：内部C++代码用原始指针遍历容器，每次调用方法都要从原始指针构造ObjectPtr（额外引用计数开销）或遇到编译错误（对应F22参数类型不匹配）
- ❌ **反模式2：依赖智能指针特有的null检查方法**：使用`obj.defined()`或`if (obj)`检查null，在原始指针调用场景下语义不一致——原始指针应统一用`!= nullptr`
- ❌ **反模式3：在FFI层重复业务逻辑**：lambda桥接层做参数校验或业务逻辑——桥接层应只做类型转换，所有逻辑在内部方法中实现，否则测试需要同时覆盖两条路径
- ❌ **反模式4：API设计只考虑单一入口**：设计公共方法时只考虑FFI调用场景，忽略内部C++层的使用需求（对应Why4/Why5）——导致后续内部调用时需要修改方法签名

### 检验标准
做完之后怎么知道做对了？
- 标准1：内部C++代码（如Layer实现）可以直接将容器中的T*传入方法，无需类型转换
- 标准2：FFI层所有需要传递对象的方法都有lambda桥接，不存在ObjectPtr→T*转换遗漏
- 标准3：null检查统一使用`!= nullptr`，代码中不存在`obj.defined()`调用（除非是ObjectPtr局部变量）
- 标准4：参数校验逻辑只出现在类方法实现中，不出现在FFI注册lambda中
- 标准5：新增公共方法时，代码审查checklist中"是否同时支持原始指针和FFI调用"项能快速判断

### 迁移示例
这个模式还能用在什么其他场景？
- **场景1（游戏引擎ECS）**：ECS系统内部用Entity*或Component*原始指针遍历进行高性能查询，脚本绑定层（Lua/Python）用ObjectPtr<Entity>管理生命周期，API层统一接收原始指针，绑定层做桥接
- **场景2（编译器AST）**：编译器优化pass内部通过ASTNode*原始指针遍历树，IDE插件的语言服务器协议(LSP)通过智能指针管理AST节点生命周期
- **场景3（数据库连接池）**：内部查询执行路径使用Connection*原始指针（高性能、零开销），外部用户API返回shared_ptr<Connection>或RAII包装，连接池内部统一用原始指针操作
