# TVM FFI 200 视角深度解读 - 实施计划

## 任务总览

- **总视角数**: 200
- **分类数**: 15
- **源码路径**: `d:\AI\.chaos\libs\ffi`（tvm-ffi + tvm）
- **产出路径**: `d:\AI\projects\docs`
- **方法论**: seven-concepts 知识沉淀链路（R→I→E）+ source-code-to-okf-wiki 五阶段（R→I→E→V→C）

## 产出目录结构

```
d:\AI\projects\docs\
├── index.md                          # 总索引
├── 01-architecture/                  # 架构与设计哲学（15篇）
├── 02-core-types/                    # 核心类型系统（20篇）
├── 03-functions/                     # 函数与调用系统（15篇）
├── 04-containers/                    # 容器系统（15篇）
├── 05-tensor-dlpack/                 # Tensor与DLPack（10篇）
├── 06-error-handling/                # 错误处理系统（10篇）
├── 07-reflection/                    # 反射系统（15篇）
├── 08-cpp-impl/                      # C++实现细节（15篇）
├── 09-python/                        # Python绑定（15篇）
├── 10-rust/                          # Rust绑定（10篇）
├── 11-c-abi-platform/                # C ABI与平台（10篇）
├── 12-build-package/                 # 构建与打包（10篇）
├── 13-testing/                       # 测试策略（10篇）
├── 14-tvm-integration/               # TVM编译器集成（15篇）
└── 15-npu-accelerator/               # NPU与加速器建议（15篇）
```

每个分类目录为一个 OKF bundle，包含 `index.md`、`log.md`、`concepts/`、`references/`。

---

## [x] Task 1: R阶段 - 源码事实采集

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 系统性阅读 tvm-ffi 的所有头文件（include/tvm/ffi/*.h）和源文件（src/ffi/*.cc）
  - 阅读 Rust 绑定（rust/tvm-ffi/src/*.rs）和 Python 绑定（python/tvm_ffi/*.py, *.pyi）
  - 阅读 TVM 中与 FFI 交互的关键文件（python/tvm/ir/_ffi_api.py, runtime/module.cc 等）
  - 提取编号事实清单 F-001 ~ F-NNN，写入 facts.md
  - 事实零推测：只记录"代码里有什么"，不记录"用于什么"
  - 核心模块全覆盖：any, c_api, cast, dtype, enum, error, function, object, container, tensor, backtrace, init_once, module
- **Acceptance Criteria Addressed**: AC-3, AC-7
- **Test Requirements**:
  - `programmatic` TR-1.1: 事实清单中每个事实包含源码文件路径和行号引用
  - `programmatic` TR-1.2: 事实中不出现"用于"/"目的是"/"设计为"等推断词（G1质量门）
  - `human-judgement` TR-1.3: 核心模块（any/c_api/function/object/container/tensor/error）全部覆盖
- **Notes**: 这是整个任务的基础。facts.md 存放在 spec 目录下的 supporting-analysis/ 中。

## [x] Task 2: I阶段 - 架构洞察与知识地图设计

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于事实清单提炼 5-8 个核心洞察四元组（陈述+证据+反常识+行动）
  - 设计 200 视角的完整分类映射表（视角编号→分类→标题→覆盖的事实编号）
  - 确定每个视角的源码依据和分析角度
  - 设计学习路径：入门→核心→高级→NPU实践
  - 输出 insights.md 和 knowledge-map.md
- **Acceptance Criteria Addressed**: AC-2, AC-7
- **Test Requirements**:
  - `programmatic` TR-2.1: 200 个视角全部有标题和分类映射
  - `programmatic` TR-2.2: 每个视角至少关联一个 F-xxx 事实编号
  - `human-judgement` TR-2.3: 洞察四元组完整（G2质量门），分类逻辑合理无重叠
- **Notes**: 视角清单见下方附录 A。

## [x] Task 3: 基础设施搭建

- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 创建 `d:\AI\projects\docs` 目录及 15 个分类子目录
  - 每个分类下创建 `concepts/` 和 `references/` 子目录
  - 为每个分类生成 references/ 信源文件（基于 facts.md）
  - 创建总 index.md 骨架（不含最终链接列表，后续填充）
  - 创建 log.md 变更日志模板
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `programmatic` TR-3.1: 15 个分类目录全部存在
  - `programmatic` TR-3.2: 每个分类的 references/ 目录包含至少 1 个信源文件
  - `programmatic` TR-3.3: references 文件先于 concepts 创建（G3信源先行）
- **Notes**: 信源先行是 source-code-to-okf-wiki 的核心纪律。

## [x] Task 4: 分类01 - 架构与设计哲学（15篇，视角001-015）

- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 分批生成 15 份概念文档（每批≤7份，共3批）
  - 视角列表：
    - 001: TVM FFI 整体架构总览
    - 002: 分层设计（C ABI → C++ API → 语言绑定）
    - 003: 类型擦除模式
    - 004: 值语义与引用语义
    - 005: ABI 稳定性策略
    - 006: 最小核心设计哲学
    - 007: 框架无关设计方法
    - 008: 插件与扩展架构
    - 009: 全局函数注册模式
    - 010: 动态模块加载系统
    - 011: 跨语言边界设计
    - 012: 错误传播边界设计
    - 013: 内存所有权模型
    - 014: 零拷贝设计原则
    - 015: 版本演进与兼容性策略
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-4, AC-5, AC-7, AC-10
- **Test Requirements**:
  - `programmatic` TR-4.1: 15 份文档全部存在且 frontmatter 完整
  - `programmatic` TR-4.2: 文档中引用的类名/函数名经 Grep 验证存在
  - `human-judgement` TR-4.3: 每份文档有源码引用、设计分析、相关概念链接
- **Notes**: 通过 general_purpose_task 分批委派，每批 5 份。

## [x] Task 5: 分类02 - 核心类型系统（20篇，视角016-035）

- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 分批生成 20 份概念文档（每批≤7份，共3批）
  - 视角列表：
    - 016: TVMFFIAny 16字节布局深度解析
    - 017: AnyView 非拥有语义
    - 018: Any 拥有语义
    - 019: TypeIndex 类型索引系统
    - 020: 静态类型索引与动态类型索引
    - 021: 小字符串优化（SmallStr）
    - 022: 小字节数组优化（SmallBytes）
    - 023: TypeTraits 类型特征机制
    - 024: cast/try_cast/as 三态转换
    - 025: FFI 中的移动语义
    - 026: 跨边界复制语义
    - 027: TVMFFIObject 对象头布局
    - 028: 组合引用计数设计
    - 029: 对象继承模型
    - 030: ObjectRef 引用包装器模式
    - 031: Deleter 析构机制
    - 032: 不透明对象（OpaqueObject）
    - 033: Python 不透明对象
    - 034: FFI 中的右值引用
    - 035: 类型转换流水线
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-4, AC-5, AC-7
- **Test Requirements**:
  - `programmatic` TR-5.1: 20 份文档全部存在
  - `programmatic` TR-5.2: TVMFFIAny/AnyView/Any/TypeTraits 等关键符号 Grep 验证通过
  - `human-judgement` TR-5.3: 内存布局分析准确，偏移量与源码一致
- **Notes**: 这是技术深度最高的分类，需要逐行精读 any.h 和 c_api.h。

## [x] Task 6: 分类03 - 函数与调用系统（15篇，视角036-050）

- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 分批生成 15 份概念文档（每批≤7份，共3批）
  - 视角列表：
    - 036: Packed Function 打包调用约定
    - 037: TVMFFIFunctionCell 函数单元
    - 038: safe_call 与 cpp_call 双路径
    - 039: C 回调函数创建
    - 040: 全局函数注册表
    - 041: 函数作为一等公民
    - 042: Lambda 与回调支持
    - 043: 参数传递约定
    - 044: 返回值约定
    - 045: 异常跨越 FFI 边界
    - 046: TLS 错误传播机制
    - 047: 函数快速路径（cpp_call 直通）
    - 048: 模块入口点约定
    - 049: __tvm_ffi_ 符号前缀
    - 050: 函数重载解析
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-4, AC-7
- **Test Requirements**:
  - `programmatic` TR-6.1: 15 份文档全部存在
  - `programmatic` TR-6.2: TVMFFIFunctionCell/safe_call/TVMFFIFunctionCreate 等符号验证通过
  - `human-judgement` TR-6.3: 调用约定分析准确，错误传播流程清晰
- **Notes**: 重点分析 function.cc 和 c_api.h 中的函数相关 API。

## [x] Task 7: 分类04 - 容器系统（15篇，视角051-065）

- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 分批生成 15 份概念文档（每批≤7份，共3批）
  - 视角列表：
    - 051: Array 不可变数组
    - 052: List 可变列表
    - 053: Map 不可变映射
    - 054: Dict 可变字典
    - 055: String 字符串对象
    - 056: Bytes 字节数组对象
    - 057: Shape 形状对象
    - 058: Tuple 元组
    - 059: Variant 变体类型
    - 060: TVMFFISeqCell 序列单元
    - 061: 原地数组存储（inplace storage）
    - 062: 容器迭代机制
    - 063: 容器类型擦除
    - 064: 自定义哈希与相等性
    - 065: 容器内存布局
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-4, AC-7
- **Test Requirements**:
  - `programmatic` TR-7.1: 15 份文档全部存在
  - `programmatic` TR-7.2: Array/List/Map/Dict/String/Bytes/Shape 等类名 Grep 验证通过
  - `human-judgement` TR-7.3: 不可变/可变容器的语义差异分析准确
- **Notes**: 参考 container.cc 源码和 test_array.cc/test_map.cc/test_list.cc/test_dict.cc 测试。

## [x] Task 8: 分类05 - Tensor与DLPack（10篇，视角066-075）

- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 分批生成 10 份概念文档（每批≤7份，共2批）
  - 视角列表：
    - 066: Tensor 对象设计（含NPU建议）
    - 067: DLPack 零拷贝互操作（含NPU建议）
    - 068: DLManagedTensor 生命周期（含NPU建议）
    - 069: DLTensor 元数据结构（含NPU建议）
    - 070: 张量对齐检查（含NPU建议）
    - 071: 连续性检查（含NPU建议）
    - 072: 不安全张量视图（含NPU建议）
    - 073: DLPack 版本化支持（含NPU建议）
    - 074: 跨框架张量交换（含NPU建议）
    - 075: 张量中的设备管理（含NPU建议）
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-4, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-8.1: 10 份文档全部存在
  - `programmatic` TR-8.2: DLPack/DLTensor/DLManagedTensor/TVMFFITensorFromDLPack 等符号验证通过
  - `human-judgement` TR-8.3: 每份文档包含"NPU 建议"章节，建议具体可操作
- **Notes**: 本分类全部文档包含 NPU 建议。参考 tensor.cc 和 3rdparty/dlpack/dlpack.h。

## [x] Task 9: 分类06 - 错误处理系统（10篇，视角076-085）

- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 分批生成 10 份概念文档（每批≤7份，共2批）
  - 视角列表：
    - 076: Error 对象设计
    - 077: ErrorCell 结构
    - 078: 错误类型分类
    - 079: 栈回溯捕获
    - 080: 跨 FFI 边界回溯
    - 081: 错误因果链
    - 082: 额外错误上下文
    - 083: TLS 错误状态
    - 084: 错误创建 API
    - 085: 异常类型层次
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-4, AC-7
- **Test Requirements**:
  - `programmatic` TR-9.1: 10 份文档全部存在
  - `programmatic` TR-9.2: TVMFFIErrorCell/TVMFFIErrorMoveFromRaised/TVMFFIErrorSetRaised 等符号验证通过
  - `human-judgement` TR-9.3: 跨边界错误传播流程分析准确
- **Notes**: 参考 error.cc, backtrace.cc, error.h 和 test_error.cc。

## [x] Task 10: 分类07 - 反射系统（15篇，视角086-100）

- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 分批生成 15 份概念文档（每批≤7份，共3批）
  - 视角列表：
    - 086: FieldInfo 字段信息设计
    - 087: MethodInfo 方法信息设计
    - 088: TypeMetadata 类型元数据
    - 089: TypeInfo 运行时类型信息
    - 090: ObjectDef 构建器
    - 091: def_field/def_method 注册
    - 092: c_class Python 集成
    - 093: 字段标志位系统
    - 094: 结构化相等性与哈希
    - 095: SEqHash 种类
    - 096: Def Region 语义
    - 097: TypeAttr 类型属性列
    - 098: 自定义哈希/相等注册
    - 099: Creator 创建函数
    - 100: 存根生成（stubgen）
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-4, AC-7
- **Test Requirements**:
  - `programmatic` TR-10.1: 15 份文档全部存在
  - `programmatic` TR-10.2: TVMFFIFieldInfo/TVMFFIMethodInfo/TVMFFITypeInfo/ObjectDef 等符号验证通过
  - `human-judgement` TR-10.3: 反射字段标志位语义分析准确
- **Notes**: 反射系统是 c_api.h 中最复杂的部分，需要仔细阅读字段标志枚举。

## [x] Task 11: 分类08 - C++实现细节（15篇，视角101-115）

- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 分批生成 15 份概念文档（每批≤7份，共3批）
  - 视角列表：
    - 101: 命名空间约定
    - 102: 头文件-only vs 编译分离
    - 103: 模板元编程
    - 104: SFINAE/enable_if 模式
    - 105: 内联优化
    - 106: TVM_FFI_INLINE 宏
    - 107: 分支预测提示
    - 108: 静态断言
    - 109: 友元类模式
    - 110: Unsafe 操作
    - 111: 原子内存序
    - 112: Arena 分配器
    - 113: OrderedMap/OrderedSet
    - 114: RingBuffer 环形缓冲
    - 115: Base64 编码
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-4, AC-7
- **Test Requirements**:
  - `programmatic` TR-11.1: 15 份文档全部存在
  - `programmatic` TR-11.2: TVM_FFI_INLINE/TVM_FFI_PREDICT_TRUE/TVM_FFI_THROW 等宏验证通过
  - `human-judgement` TR-11.3: C++ 技术分析准确，代码风格与源码一致
- **Notes**: 112-115 来自 tvm/src/support/ 目录，是 TVM 的支撑库而非 tvm-ffi 核心。

## [/] Task 12: 分类09 - Python绑定（15篇，视角116-130）

- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 分批生成 15 份概念文档（每批≤7份，共3批）
  - 视角列表：
    - 116: Cython 绑定架构
    - 117: _ffi_api 模块模式
    - 118: Python 对象注册
    - 119: register_object 装饰器
    - 120: register_global_func
    - 121: Python 错误转换
    - 122: Python GIL 处理
    - 123: 自由线程 Python 支持
    - 124: 存根生成流水线
    - 125: core.pyi 类型存根
    - 126: Python dataclass 集成
    - 127: PyObject 不透明处理
    - 128: Python 打包（wheel）
    - 129: pyproject.toml 配置
    - 130: Python C API 交互
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-4, AC-7
- **Test Requirements**:
  - `programmatic` TR-12.1: 15 份文档全部存在
  - `programmatic` TR-12.2: register_object/register_global_func/_ffi_api 等符号在 Python 源码中验证通过
  - `human-judgement` TR-12.3: Python 绑定机制分析准确，GIL/自由线程讨论有据
- **Notes**: 注意 tvm-ffi/python/ 目录文件较少（core.pyi, error.py, py.typed），Cython 生成的 .cpp 不在源码树中。需要结合 tvm/python/tvm/ 中的使用模式分析。

## [ ] Task 13: 分类10 - Rust绑定（10篇，视角131-140）

- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 分批生成 10 份概念文档（每批≤7份，共2批）
  - 视角列表：
    - 131: Rust crate 结构
    - 132: tvm-ffi-sys 原始绑定
    - 133: tvm-ffi 安全包装器
    - 134: Rust 类型转换
    - 135: Rust 所有权与 FFI
    - 136: Rust 中的 Any
    - 137: Rust 错误处理
    - 138: build.rs 构建脚本
    - 139: Cargo workspace
    - 140: Rust 安全不变量
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-4, AC-7
- **Test Requirements**:
  - `programmatic` TR-13.1: 10 份文档全部存在
  - `programmatic` TR-13.2: rust/tvm-ffi/src/ 中的模块和函数名验证通过
  - `human-judgement` TR-13.3: Rust 安全分析准确，unsafe 边界讨论有据
- **Notes**: Rust 代码量较少（any.rs + lib.rs），需要结合 Cargo.toml 和 build.rs 分析整体设计。

## [ ] Task 14: 分类11 - C ABI与平台（10篇，视角141-150）

- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 分批生成 10 份概念文档（每批≤7份，共2批）
  - 视角列表：
    - 141: C ABI 稳定性保证
    - 142: 结构体打包与对齐
    - 143: 32/64位兼容性
    - 144: 字节序考量
    - 145: DLL 导出/导入
    - 146: 弱链接
    - 147: Emscripten/WASM 支持（含NPU建议）
    - 148: MSVC vs GCC/Clang
    - 149: 平台相关栈回溯
    - 150: 版本查询 API
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-4, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-14.1: 10 份文档全部存在
  - `programmatic` TR-14.2: TVM_FFI_DLL/TVM_FFI_WEAK/TVMFFIGetVersion 等符号验证通过
  - `human-judgement` TR-14.3: 平台兼容性分析全面，147包含NPU建议
- **Notes**: 147 WASM 支持对 NPU Web 部署场景有意义，包含 NPU 建议。

## [ ] Task 15: 分类12 - 构建与打包（10篇，视角151-160）

- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 分批生成 10 份概念文档（每批≤7份，共2批）
  - 视角列表：
    - 151: CMake 构建系统
    - 152: pyproject.toml 构建配置
    - 153: Cython 编译流程
    - 154: 共享库目标
    - 155: Wheel 分发包
    - 156: "One Wheel" 策略
    - 157: 多 Python 版本支持
    - 158: 依赖管理
    - 159: DLPack 供应商依赖
    - 160: 构建配置选项
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-4, AC-7
- **Test Requirements**:
  - `programmatic` TR-15.1: 10 份文档全部存在
  - `programmatic` TR-15.2: CMakeLists.txt/pyproject.toml 中的构建目标和配置验证通过
  - `human-judgement` TR-15.3: 构建流程分析准确
- **Notes**: 参考 CMakeLists.txt, pyproject.toml, build.rs。

## [ ] Task 16: 分类13 - 测试策略（10篇，视角161-170）

- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 分批生成 10 份概念文档（每批≤7份，共2批）
  - 视角列表：
    - 161: C++ GoogleTest 套件
    - 162: Python pytest 套件
    - 163: test_any 覆盖分析
    - 164: test_container 覆盖分析
    - 165: test_dtype 覆盖分析
    - 166: test_error 覆盖分析
    - 167: test_shape/tuple 覆盖分析
    - 168: CI/CD 流水线
    - 169: 跨平台测试
    - 170: 代码检查与格式化
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-4, AC-7
- **Test Requirements**:
  - `programmatic` TR-16.1: 10 份文档全部存在
  - `programmatic` TR-16.2: 测试文件中的测试用例名称验证通过
  - `human-judgement` TR-16.3: 测试覆盖分析有数据支撑
- **Notes**: 参考 tests/cpp/ 目录下的 10 个测试文件和 .github/workflows/。

## [ ] Task 17: 分类14 - TVM编译器集成（15篇，视角171-185）

- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 分批生成 15 份概念文档（每批≤7份，共3批）
  - 视角列表：
    - 171: TVM FFI 在 TVM 运行时中的应用（含NPU建议）
    - 172: TIR 表达式系统与 FFI
    - 173: Relax IR 与 FFI
    - 174: Pass 基础设施
    - 175: Module 系统集成
    - 176: RPC 服务端/客户端（含NPU建议）
    - 177: 虚拟机（VM）（含NPU建议）
    - 178: 字节码执行（含NPU建议）
    - 179: KV State 管理（含NPU建议）
    - 180: 目标代码生成注册（含NPU建议）
    - 181: TOPI 算子库
    - 182: TE 张量表达式
    - 183: Arith 简化器
    - 184: Source Map
    - 185: Instrument 与性能分析（含NPU建议）
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-4, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-17.1: 15 份文档全部存在
  - `programmatic` TR-17.2: tvm/src/ 和 tvm/include/tvm/ 中的关键类名验证通过
  - `human-judgement` TR-17.3: FFI 集成分析准确，标注的文档包含NPU建议
- **Notes**: 本分类分析 tvm/ 目录（非 tvm-ffi/），展示 FFI 在真实编译器中的应用。171/176/177/178/179/180/185 包含 NPU 建议。

## [ ] Task 18: 分类15 - NPU与加速器建议（15篇，视角186-200）

- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 分批生成 15 份概念文档（每批≤7份，共3批）
  - 视角列表：
    - 186: NPU FFI 集成总览
    - 187: VTA 类加速器设计
    - 188: NPU 内核库发布
    - 189: NPU 设备 API 设计
    - 190: NPU 张量交换
    - 191: NPU 命令队列 via FFI
    - 192: NPU 内存管理
    - 193: NPU 自定义算子注册
    - 194: NPU 运行时模块加载
    - 195: NPU 错误处理策略
    - 196: NPU 多设备支持
    - 197: NPU 性能分析与追踪
    - 198: NPU ABI 稳定性建议
    - 199: NPU 框架互操作（PyTorch/JAX）
    - 200: NPU 内核 DSL 集成
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-4, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-18.1: 15 份文档全部存在
  - `programmatic` TR-18.2: 引用的 TVM FFI API 符号验证通过；引用的 npu-ffi/VTA 代码符号验证通过
  - `human-judgement` TR-18.3: NPU 建议具体、合理、可操作，结合 TVM FFI 机制给出实现路径
- **Notes**: 参考 projects/xuanspace/libs/npu-ffi/ 和 tvm/src/target/ 中的后端注册模式。所有文档均含 NPU 建议。

## [ ] Task 19: V阶段 - 独立验证与修复

- **Priority**: high
- **Depends On**: Task 4-18
- **Description**:
  - 结构检查：所有文档 frontmatter 字段完整性
  - 链接检查：所有交叉链接目标存在
  - **Grep 级 API 验证**：对每份文档中引用的类名/方法名/结构体字段，在源码中 Grep 验证存在性
  - 代码示例检查：API 调用与 facts.md 事实一致
  - Index 完整性检查：总索引和分类索引无遗漏
  - NPU 建议检查：标注为含 NPU 建议的文档确实包含该章节
  - 输出验证报告，逐一修复发现的问题
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5, AC-6, AC-8
- **Test Requirements**:
  - `programmatic` TR-19.1: 0 个虚构 API（所有引用符号 Grep 验证通过）
  - `programmatic` TR-19.2: 0 个断裂链接
  - `programmatic` TR-19.3: 所有 frontmatter 字段完整
  - `human-judgement` TR-19.4: NPU 建议质量审查通过
- **Notes**: Grep 验证是 G4 质量门的核心，不可跳过。发现虚构 API 必须修复文档而非删除检查。

## [ ] Task 20: 索引生成与收尾

- **Priority**: high
- **Depends On**: Task 19
- **Description**:
  - 所有内容文档定稿后，生成各级 index.md（Index 最后写原则）
  - 总索引包含 15 个分类链接和 200 份文档清单
  - 每个分类 index 列出其下所有概念文档
  - 生成 log.md 记录生成过程
  - 更新交叉链接确保完整
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-20.1: 总索引链接 200 份文档，无遗漏
  - `programmatic` TR-20.2: 15 个分类索引各列出其下全部文档
  - `programmatic` TR-20.3: 所有索引链接可点击到达
- **Notes**: Index 必须最后写，避免新增文档后遗漏更新。

---

## 附录 A：200 视角分类映射表

| 编号 | 分类 | 标题 | NPU建议 |
|------|------|------|:------:|
| 001 | 01-architecture | 整体架构总览 | |
| 002 | 01-architecture | 分层设计 | |
| 003 | 01-architecture | 类型擦除模式 | |
| 004 | 01-architecture | 值语义与引用语义 | |
| 005 | 01-architecture | ABI稳定性策略 | ✓ |
| 006 | 01-architecture | 最小核心设计哲学 | |
| 007 | 01-architecture | 框架无关设计 | |
| 008 | 01-architecture | 插件与扩展架构 | ✓ |
| 009 | 01-architecture | 全局函数注册模式 | |
| 010 | 01-architecture | 动态模块加载系统 | ✓ |
| 011 | 01-architecture | 跨语言边界设计 | |
| 012 | 01-architecture | 错误传播边界设计 | ✓ |
| 013 | 01-architecture | 内存所有权模型 | ✓ |
| 014 | 01-architecture | 零拷贝设计原则 | ✓ |
| 015 | 01-architecture | 版本演进与兼容性 | |
| 016 | 02-core-types | TVMFFIAny 16字节布局 | |
| 017 | 02-core-types | AnyView非拥有语义 | |
| 018 | 02-core-types | Any拥有语义 | |
| 019 | 02-core-types | TypeIndex类型索引 | |
| 020 | 02-core-types | 静态与动态类型索引 | |
| 021 | 02-core-types | 小字符串优化 | |
| 022 | 02-core-types | 小字节数组优化 | |
| 023 | 02-core-types | TypeTraits机制 | |
| 024 | 02-core-types | cast/try_cast/as | |
| 025 | 02-core-types | FFI移动语义 | |
| 026 | 02-core-types | 跨边界复制语义 | |
| 027 | 02-core-types | TVMFFIObject对象头 | |
| 028 | 02-core-types | 组合引用计数 | ✓ |
| 029 | 02-core-types | 对象继承模型 | |
| 030 | 02-core-types | ObjectRef包装器 | |
| 031 | 02-core-types | Deleter析构机制 | ✓ |
| 032 | 02-core-types | 不透明对象 | |
| 033 | 02-core-types | Python不透明对象 | |
| 034 | 02-core-types | FFI右值引用 | |
| 035 | 02-core-types | 类型转换流水线 | |
| 036 | 03-functions | Packed Function约定 | |
| 037 | 03-functions | FunctionCell函数单元 | |
| 038 | 03-functions | safe_call与cpp_call | |
| 039 | 03-functions | C回调函数创建 | |
| 040 | 03-functions | 全局函数注册表 | |
| 041 | 03-functions | 函数一等公民 | |
| 042 | 03-functions | Lambda与回调 | ✓ |
| 043 | 03-functions | 参数传递约定 | |
| 044 | 03-functions | 返回值约定 | |
| 045 | 03-functions | 异常跨越FFI边界 | ✓ |
| 046 | 03-functions | TLS错误传播 | |
| 047 | 03-functions | cpp_call快速路径 | |
| 048 | 03-functions | 模块入口点约定 | ✓ |
| 049 | 03-functions | __tvm_ffi_符号前缀 | |
| 050 | 03-functions | 函数重载解析 | |
| 051 | 04-containers | Array不可变数组 | |
| 052 | 04-containers | List可变列表 | |
| 053 | 04-containers | Map不可变映射 | |
| 054 | 04-containers | Dict可变字典 | |
| 055 | 04-containers | String字符串对象 | |
| 056 | 04-containers | Bytes字节数组 | |
| 057 | 04-containers | Shape形状对象 | ✓ |
| 058 | 04-containers | Tuple元组 | |
| 059 | 04-containers | Variant变体类型 | |
| 060 | 04-containers | SeqCell序列单元 | |
| 061 | 04-containers | 原地数组存储 | ✓ |
| 062 | 04-containers | 容器迭代机制 | |
| 063 | 04-containers | 容器类型擦除 | |
| 064 | 04-containers | 自定义哈希与相等 | |
| 065 | 04-containers | 容器内存布局 | |
| 066 | 05-tensor-dlpack | Tensor对象设计 | ✓ |
| 067 | 05-tensor-dlpack | DLPack零拷贝互操作 | ✓ |
| 068 | 05-tensor-dlpack | DLManagedTensor生命周期 | ✓ |
| 069 | 05-tensor-dlpack | DLTensor元数据 | ✓ |
| 070 | 05-tensor-dlpack | 张量对齐检查 | ✓ |
| 071 | 05-tensor-dlpack | 连续性检查 | ✓ |
| 072 | 05-tensor-dlpack | 不安全张量视图 | ✓ |
| 073 | 05-tensor-dlpack | DLPack版本化支持 | ✓ |
| 074 | 05-tensor-dlpack | 跨框架张量交换 | ✓ |
| 075 | 05-tensor-dlpack | 张量设备管理 | ✓ |
| 076 | 06-error-handling | Error对象设计 | |
| 077 | 06-error-handling | ErrorCell结构 | |
| 078 | 06-error-handling | 错误类型分类 | |
| 079 | 06-error-handling | 栈回溯捕获 | |
| 080 | 06-error-handling | 跨FFI边界回溯 | ✓ |
| 081 | 06-error-handling | 错误因果链 | |
| 082 | 06-error-handling | 额外错误上下文 | |
| 083 | 06-error-handling | TLS错误状态 | |
| 084 | 06-error-handling | 错误创建API | |
| 085 | 06-error-handling | 异常类型层次 | |
| 086 | 07-reflection | FieldInfo设计 | |
| 087 | 07-reflection | MethodInfo设计 | |
| 088 | 07-reflection | TypeMetadata | |
| 089 | 07-reflection | TypeInfo运行时类型 | |
| 090 | 07-reflection | ObjectDef构建器 | |
| 091 | 07-reflection | def_field/def_method | |
| 092 | 07-reflection | c_class Python集成 | |
| 093 | 07-reflection | 字段标志位系统 | |
| 094 | 07-reflection | 结构化相等与哈希 | |
| 095 | 07-reflection | SEqHash种类 | |
| 096 | 07-reflection | Def Region语义 | |
| 097 | 07-reflection | TypeAttr类型属性 | |
| 098 | 07-reflection | 自定义哈希/相等注册 | |
| 099 | 07-reflection | Creator创建函数 | ✓ |
| 100 | 07-reflection | 存根生成stubgen | |
| 101 | 08-cpp-impl | 命名空间约定 | |
| 102 | 08-cpp-impl | 头文件-only vs编译 | |
| 103 | 08-cpp-impl | 模板元编程 | |
| 104 | 08-cpp-impl | SFINAE/enable_if | |
| 105 | 08-cpp-impl | 内联优化 | |
| 106 | 08-cpp-impl | TVM_FFI_INLINE宏 | |
| 107 | 08-cpp-impl | 分支预测提示 | |
| 108 | 08-cpp-impl | 静态断言 | |
| 109 | 08-cpp-impl | 友元类模式 | |
| 110 | 08-cpp-impl | Unsafe操作 | |
| 111 | 08-cpp-impl | 原子内存序 | ✓ |
| 112 | 08-cpp-impl | Arena分配器 | ✓ |
| 113 | 08-cpp-impl | OrderedMap/Set | |
| 114 | 08-cpp-impl | RingBuffer | ✓ |
| 115 | 08-cpp-impl | Base64编码 | |
| 116 | 09-python | Cython绑定架构 | |
| 117 | 09-python | _ffi_api模块模式 | |
| 118 | 09-python | Python对象注册 | |
| 119 | 09-python | register_object装饰器 | |
| 120 | 09-python | register_global_func | |
| 121 | 09-python | Python错误转换 | |
| 122 | 09-python | Python GIL处理 | |
| 123 | 09-python | 自由线程Python | |
| 124 | 09-python | 存根生成流水线 | |
| 125 | 09-python | core.pyi类型存根 | |
| 126 | 09-python | dataclass集成 | |
| 127 | 09-python | PyObject不透明处理 | |
| 128 | 09-python | Python打包wheel | ✓ |
| 129 | 09-python | pyproject.toml配置 | |
| 130 | 09-python | Python C API交互 | |
| 131 | 10-rust | Rust crate结构 | |
| 132 | 10-rust | tvm-ffi-sys原始绑定 | |
| 133 | 10-rust | tvm-ffi安全包装 | |
| 134 | 10-rust | Rust类型转换 | |
| 135 | 10-rust | Rust所有权与FFI | ✓ |
| 136 | 10-rust | Rust中的Any | |
| 137 | 10-rust | Rust错误处理 | |
| 138 | 10-rust | build.rs构建脚本 | |
| 139 | 10-rust | Cargo workspace | |
| 140 | 10-rust | Rust安全不变量 | |
| 141 | 11-c-abi-platform | C ABI稳定性保证 | ✓ |
| 142 | 11-c-abi-platform | 结构体打包与对齐 | ✓ |
| 143 | 11-c-abi-platform | 32/64位兼容性 | |
| 144 | 11-c-abi-platform | 字节序考量 | |
| 145 | 11-c-abi-platform | DLL导出/导入 | |
| 146 | 11-c-abi-platform | 弱链接 | |
| 147 | 11-c-abi-platform | Emscripten/WASM | ✓ |
| 148 | 11-c-abi-platform | MSVC vs GCC/Clang | |
| 149 | 11-c-abi-platform | 平台栈回溯 | |
| 150 | 11-c-abi-platform | 版本查询API | |
| 151 | 12-build-package | CMake构建系统 | |
| 152 | 12-build-package | pyproject.toml构建 | |
| 153 | 12-build-package | Cython编译流程 | |
| 154 | 12-build-package | 共享库目标 | ✓ |
| 155 | 12-build-package | Wheel分发包 | ✓ |
| 156 | 12-build-package | One Wheel策略 | ✓ |
| 157 | 12-build-package | 多Python版本支持 | |
| 158 | 12-build-package | 依赖管理 | |
| 159 | 12-build-package | DLPack供应商依赖 | |
| 160 | 12-build-package | 构建配置选项 | |
| 161 | 13-testing | C++ GoogleTest套件 | |
| 162 | 13-testing | Python pytest套件 | |
| 163 | 13-testing | test_any覆盖分析 | |
| 164 | 13-testing | test_container覆盖 | |
| 165 | 13-testing | test_dtype覆盖 | |
| 166 | 13-testing | test_error覆盖 | |
| 167 | 13-testing | test_shape/tuple覆盖 | |
| 168 | 13-testing | CI/CD流水线 | |
| 169 | 13-testing | 跨平台测试 | |
| 170 | 13-testing | 代码检查与格式化 | |
| 171 | 14-tvm-integration | TVM运行时FFI应用 | ✓ |
| 172 | 14-tvm-integration | TIR表达式与FFI | |
| 173 | 14-tvm-integration | Relax IR与FFI | |
| 174 | 14-tvm-integration | Pass基础设施 | |
| 175 | 14-tvm-integration | Module系统集成 | |
| 176 | 14-tvm-integration | RPC服务端/客户端 | ✓ |
| 177 | 14-tvm-integration | 虚拟机VM | ✓ |
| 178 | 14-tvm-integration | 字节码执行 | ✓ |
| 179 | 14-tvm-integration | KV State管理 | ✓ |
| 180 | 14-tvm-integration | 目标代码生成注册 | ✓ |
| 181 | 14-tvm-integration | TOPI算子库 | |
| 182 | 14-tvm-integration | TE张量表达式 | |
| 183 | 14-tvm-integration | Arith简化器 | |
| 184 | 14-tvm-integration | Source Map | |
| 185 | 14-tvm-integration | Instrument性能分析 | ✓ |
| 186 | 15-npu-accelerator | NPU FFI集成总览 | ✓ |
| 187 | 15-npu-accelerator | VTA类加速器设计 | ✓ |
| 188 | 15-npu-accelerator | NPU内核库发布 | ✓ |
| 189 | 15-npu-accelerator | NPU设备API设计 | ✓ |
| 190 | 15-npu-accelerator | NPU张量交换 | ✓ |
| 191 | 15-npu-accelerator | NPU命令队列 | ✓ |
| 192 | 15-npu-accelerator | NPU内存管理 | ✓ |
| 193 | 15-npu-accelerator | NPU自定义算子注册 | ✓ |
| 194 | 15-npu-accelerator | NPU运行时模块加载 | ✓ |
| 195 | 15-npu-accelerator | NPU错误处理策略 | ✓ |
| 196 | 15-npu-accelerator | NPU多设备支持 | ✓ |
| 197 | 15-npu-accelerator | NPU性能分析追踪 | ✓ |
| 198 | 15-npu-accelerator | NPU ABI稳定性建议 | ✓ |
| 199 | 15-npu-accelerator | NPU框架互操作 | ✓ |
| 200 | 15-npu-accelerator | NPU内核DSL集成 | ✓ |

**NPU 建议文档统计**: 共约 55 篇文档包含 NPU 建议章节。
