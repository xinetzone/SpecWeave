# 洞察萃取

## 根因分析（5-Whys）

### Why 1：palmDet 编译为什么会 Segmentation fault？
→ 因为 adaround 模块加载了 PyTorch，PyTorch 的 libtorch.so 与 TVM 的 libtvm.so 中的 LLVM 符号发生冲突

### Why 2：为什么会发生符号冲突？
→ 因为 TVM 静态链接了 LLVM，且 HIDE_PRIVATE_SYMBOLS=OFF，导致所有 LLVM 符号被导出到 libtvm.so 的动态符号表

### Why 3：为什么不启用 HIDE_PRIVATE_SYMBOLS？
→ 之前的实现使用 -fvisibility=hidden + --gc-sections，会导致 TVM 的静态注册机制失效（TVM_REGISTER_GLOBAL 生成的 static 对象被链接器优化删除）

### Why 4：为什么之前的实现用 -fvisibility=hidden？
→ 这是常见的符号隐藏方案，但不适用于 TVM 这种大量使用静态初始化注册的架构

### Why 5：为什么没有找到更好的方案？
→ 团队对链接器选项的理解不够深入，没有意识到 --exclude-libs,ALL 可以只隐藏静态库符号而不影响主程序符号

## 核心洞察

### 洞察1：符号可见性控制需要精确区分"自身符号"与"依赖符号"

**发现**：-fvisibility=hidden 是粗粒度方案，会影响所有符号；--exclude-libs,ALL 是精确方案，只影响静态链接的第三方库符号

**影响**：
- TVM 的 TVM_REGISTER_GLOBAL 等静态注册机制依赖符号可见性和链接器不删除未引用段
- 直接使用 -fvisibility=hidden 会导致注册失效，必须配合 TVM_DLL 宏显式标记导出符号
- 使用 --exclude-libs,ALL 无需修改源码，自动隐藏第三方静态库符号

**适用场景**：任何静态链接第三方库的共享库项目，尤其是使用静态注册模式的项目

### 洞察2：--gc-sections 是静态注册的杀手

**发现**：--gc-sections 配合 -ffunction-sections -fdata-sections 会删除未被直接引用的代码段和数据段

**影响**：
- TVM 的静态注册对象（TVM_REGISTER_GLOBAL 生成的 static 变量）在编译时没有被直接引用
- 它们的作用是在程序启动时通过构造函数自动注册
- --gc-sections 会把这些注册对象所在的段删除，导致注册失效

**适用场景**：所有使用静态初始化进行注册的项目（如 TVM、LLVM、Qt 插件系统等）

### 洞察3：符号冲突的根本原因是动态链接器的符号介入机制

**发现**：动态链接器在解析符号时，会在所有已加载的共享库中按加载顺序查找符号

**影响**：
- 如果 libtvm.so 先加载，其导出的 LLVM 符号会被后续加载的 libtorch.so 中的代码引用
- 即使 libtorch.so 自带了 LLVM 实现，动态链接器也会优先使用已解析的符号
- 不同版本 LLVM 的符号 ABI 可能不兼容，导致运行时崩溃

**适用场景**：任何多框架共存的环境（ML 框架、编译器框架等）

## 反模式

### 反模式1：禁用功能来绕过问题

**描述**：将 adaround=false 作为解决方案，而不是修复根本原因

**后果**：
- 功能被禁用，影响用户体验
- 问题在其他场景可能再次出现
- 无法复用到其他项目

**规避策略**：遇到问题时先做根因分析，找到真正的原因再修复

### 反模式2：使用 -fvisibility=hidden 而不了解其副作用

**描述**：直接启用 -fvisibility=hidden 解决符号冲突，导致静态注册失效

**后果**：
- 运行时出现"Attribute not registered"错误
- 需要逐个添加 TVM_DLL 标记，维护成本高
- 容易遗漏，导致难以排查的运行时错误

**规避策略**：优先使用 --exclude-libs,ALL；必须使用 -fvisibility=hidden 时，确保所有静态注册对象都有正确的可见性标记

### 反模式3：同时使用 --gc-sections 和静态注册

**描述**：启用链接器垃圾回收优化，同时项目使用静态初始化注册

**后果**：
- 注册对象被删除，功能失效
- 错误信息不明确（"Attribute not registered"）
- 难以定位问题根源

**规避策略**：使用静态注册的项目禁用 --gc-sections；或使用 -Wl,--whole-archive 确保注册段被保留

## 迁移验证

### 验证场景1：TVM 编译验证（docker/local 环境）
- 验证内容：重新编译 TVM，确认 libtvm.so 和 libtvm_runtime.so 生成正常
- 结果：通过，编译耗时 6.3 分钟

### 验证场景2：符号表分析
- 验证内容：使用 readelf 检查 libtvm.so 的符号可见性
- 结果：通过，LLVM 符号隐藏，TVM 符号正常导出

### 验证场景3：TVM+PyTorch 共存测试
- 验证内容：先导入 PyTorch，再导入 TVM，执行 relay.build
- 结果：通过，无段错误

## 行动项

| 优先级 | 行动项 | 负责人 | 验收标准 | 预计时间 |
|--------|--------|--------|---------|---------|
| 高 | 将精确符号控制方案推广到其他 TVM 分支 | 开发团队 | 所有分支默认启用 --exclude-libs,ALL | 1周 |
| 中 | 更新 CI/CD 流程，确保新构建使用正确配置 | DevOps | CI 构建日志显示 HIDE_PRIVATE_SYMBOLS=ON | 3天 |
| 低 | 整理符号可见性控制最佳实践文档 | 技术文档 | 文档包含原理、配置、验证方法 | 1周 |

