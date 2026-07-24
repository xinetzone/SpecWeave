---
id: "dependency-shimming-layer"
source: "../../../knowledge/learning/caffe-architecture-wiki/07-caffe-cpp-slim-tvm-ffi-modernization.md"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/architecture-patterns/dependency-shimming-layer.toml"
---
> **提炼自**：[07-caffe-cpp-slim-tvm-ffi-modernization.md](../../../knowledge/learning/caffe-architecture-wiki/07-caffe-cpp-slim-tvm-ffi-modernization.md) —— daoflows/caffe现代化改造（compat/适配层设计）

# 依赖裁剪适配层模式（Dependency Shimming Layer）

## 决策状态

✅ 已接受（Accepted）—— 在 daoflows/caffe caffe-cpp-slim 中验证通过

## 模式类型

架构模式 / 渐进式重构模式

## 成熟度

L2 已验证（Caffe slim核心验证 + SpecWeave AGENTS.md兼容层思想同源）

## 适用场景

当需要将重度依赖的遗留C++/大型项目改造为无依赖/轻依赖版本，但满足以下任一条件时：
- 不想/不能大规模修改上游源码（保持与上游分支合并能力）
- 改造需要分阶段进行，不能一次性全部完成
- 希望保留完整功能版本和裁剪版本共存的能力
- 第三方依赖被深度使用，直接替换会导致大面积编译错误无法定位

典型场景：
- 大型C++库的嵌入式/移动端裁剪（OpenCV/FFmpeg最小化构建）
- 企业内部 fork 开源项目时的适配层设计
- 微服务拆分时从单体中剥离功能的防腐层
- 跨平台移植时为平台特定API提供兼容层
- 渐进式从旧框架迁移到新框架的过渡层

## 上下文与问题背景

大型遗留C++项目常见困境：

| 问题 | 具体表现 | 改造难点 |
|------|---------|---------|
| **依赖地狱** | 强制依赖8+第三方库，版本冲突频发，部署困难 | 直接删除依赖会导致成百上千个编译错误 |
| **上游同步** | fork后直接修改源码导致与上游永久分叉，无法合并上游bugfix | 每处修改都是"技术债务利息" |
| **全有或全无** | 要么用完整版本（依赖重），要么自己从零重写（工作量大） | 缺少"中间路线" |
| **重构风险** | 大规模替换依赖的PR无法code review，bug难以定位 | 改动越大风险越高，越不敢合并 |

**常见错误做法的问题**：
1. **直接fork修改所有源文件**：永久分叉，无法合并上游更新
2. **#ifdef 条件编译满天飞**：代码可读性严重下降，编译矩阵爆炸
3. **一次性移除所有依赖**：几千个编译错误无从下手，容易半途而废
4. **不保留完整版本作为对照**：裁剪出问题时无法对比定位问题

## 决策

引入 **compat/ 适配层（Shim Layer）** 作为依赖裁剪的核心机制：

### 核心结构

```
project/
├── src/                           # 原始源码（不做修改！）
│   ├── net.cpp
│   ├── layer.cpp
│   └── ...
├── include/
│   └── compat/                    # 🔑 适配层目录（仅新增，不修改原有代码）
│       ├── boost/
│       │   ├── shared_ptr.hpp     # using boost::shared_ptr = std::shared_ptr;
│       │   └── mutex.hpp          # using boost::mutex = std::mutex;
│       ├── glog/
│       │   └── logging.h         # 内联轻量级日志宏
│       └── gflags/
│           └── gflags.h          # 空实现或简单替代
└── CMakeLists.txt                 # include path切换：优先compat/，再找系统库
```

### 决策1：零侵入原则——源文件不做任何修改

所有适配通过 include path 和头文件别名完成，原始源文件的 `#include <boost/shared_ptr.hpp>` 保持不变。构建系统通过 `-I include/compat` 将 compat 目录放在系统 include 路径之前，编译器优先找到我们提供的 shim。

**为什么这很重要**：
- git diff 干净，易于code review
- 上游发布新版本时，直接 merge 即可，适配层自动生效
- 完整版本和裁剪版本共享同一份源码，bug修复双向生效

### 决策2：依赖四分类法

在动手之前，先对所有依赖做分类：

| 分类 | 处理策略 | Caffe示例 |
|------|---------|----------|
| **必需依赖** | 保留，不裁剪 | protobuf（模型序列化）、BLAS（矩阵运算） |
| **可替换依赖** | 用标准库/更轻量方案替换 | boost→std、glog→内联宏 |
| **可移除依赖** | 提供空实现或完全移除功能 | gflags（命令行解析在推理时不需要）、HDF5（训练格式） |
| **可选依赖** | 编译选项开关，按需启用 | CUDA/cuDNN、OpenCV（预处理可选） |

### 决策3：构建系统双模式切换

CMake 提供两种构建模式：
- **完整模式（full）**：链接所有真实第三方库，compat/ 不生效
- **裁剪模式（slim）**：优先使用 compat/ shim，只链接必需依赖

```cmake
# 伪代码
option(BUILD_SLIM "Build slim version without heavy deps" OFF)
if(BUILD_SLIM)
    include_directories(BEFORE include/compat)  # compat优先
    set(CAFFE_LINK_LIBRARIES protobuf blas)     # 仅核心依赖
else()
    find_package(Boost REQUIRED)               # 完整依赖
    find_package(Glog REQUIRED)
    set(CAFFE_LINK_LIBRARIES Boost::boost glog gflags ...)
endif()
```

### 决策4：shim分层设计

compat/ 内部的shim分三层：

| 层级 | 复杂度 | 示例 | 适用场景 |
|------|--------|------|---------|
| **L1 别名层** | 最简单，<10行 | `using boost::shared_ptr = std::shared_ptr;` | API兼容，直接映射 |
| **L2 内联实现层** | 中等，<100行 | 轻量级日志宏、简单mutex封装 | API部分兼容，提供最小可用实现 |
| **L3 空桩层** | 简单，空实现 | 移除的功能（如gflags命令行解析） | 功能不需要，但代码中还有调用 |

### 决策5：渐进式裁剪路径

裁剪按依赖逐个进行，每个依赖单独一个PR：

1. 搭建 compat/ 骨架和CMake切换开关（验证构建仍然正常）
2. 选择一个最容易替换的依赖（如boost::shared_ptr→std::shared_ptr）
3. 编写该依赖的shim
4. 切换到slim模式，编译测试
5. 如果编译错误过多，回滚，分析后换更小粒度的依赖
6. 逐步推进，直到达到目标依赖集合

## 后果与权衡

### 正面后果

✅ **上游可合并**：源文件零修改，上游bugfix可以直接git merge
✅ **风险可控**：每个依赖单独一个PR，改动小易review，出问题容易回滚
✅ **双版本共存**：同一份源码可以构建完整版和slim版，方便对比验证
✅ **渐进式实施**：不需要"大爆炸"式重构，可以随时暂停，已完成部分持续可用
✅ **新人友好**：想裁剪哪个依赖看对应shim即可，不需要理解整个项目
✅ **编译错误局部化**：出问题只看一个shim文件，不需要在几万行源码中找

### 负面后果/代价

⚠️ **shim维护成本**：上游升级第三方库时，shim可能需要适配新API
⚠️ **行为不完全等价**：L2/L3层shim可能与原库行为有细微差异（如日志格式），需测试验证
⚠️ **额外的间接层**：增加了一层头文件跳转，对代码阅读有轻微影响（但IDE可以正常跳转）
⚠️ **长期需要清理**：shim是过渡层，如果项目长期维护，最终还是应该逐步将源码中的#include改为直接使用标准库

### 边界条件

此模式**不适用**于：
- ❌ 依赖的API和替代方案差异极大（如用C重写整个C++库）
- ❌ 性能关键路径上的核心算法依赖（shim可能引入性能开销，L1别名层除外）
- ❌ 项目已经和上游分叉太久，完全没有合并需求
- ❌ 重写比重构更简单的极小项目

## 替代方案对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| **依赖裁剪适配层（本模式）** | 零侵入、渐进式、上游可合并 | 需要写shim，有维护成本 | 大型遗留项目、需要持续同步上游 |
| **直接fork修改源码** | 简单直接，不需要shim | 永久分叉、无法合并上游、diff难review | 一次性fork不需要同步上游 |
| **#ifdef 条件编译** | 灵活，可以细粒度控制 | 代码可读性差、编译矩阵爆炸 | 平台特定代码的少量差异 |
| **完全重写** | 架构最干净 | 工作量大、风险高、周期长 | 旧代码完全无法维护时 |
| **vcpkg/conan 依赖管理** | 解决版本问题，不减少依赖 | 依赖依然存在，镜像体积大 | 依赖版本冲突问题（不是依赖数量问题） |

## 实施检查清单

裁剪每个依赖前：

- [ ] **分类**：该依赖属于必需/可替换/可移除/可选中的哪一类？
- [ ] **API调研**：列出该依赖在项目中被使用的所有API（不要漏）
- [ ] **shim分层**：确定用L1别名/L2内联/L3空桩哪一层
- [ ] **测试准备**：完整模式下测试全部通过作为基线
- [ ] **小步提交**：一个依赖一个PR，不要把多个依赖的shim混在一起
- [ ] **对比验证**：slim模式下的输出与完整模式做数值/功能对比
- [ ] **记录差异**：如果shim与原库有行为差异，在shim文件顶部注释说明
- [ ] **完整模式仍可构建**：裁剪后完整版不能被破坏

## 反模式与陷阱

| 陷阱 | 表现 | 规避方法 |
|------|------|---------|
| **shim中写业务逻辑** | compat/目录中出现大量实现代码 | compat/只做适配，不做业务；业务逻辑应在重构完成后迁移到源码中 |
| **一开始就裁剪所有依赖** | 一次提交10+个shim，上千个编译错误 | 按依赖逐个推进，每个shim单独验证 |
| **shim隐式修改行为** | 把glog的FATAL改为不退出程序，导致隐藏bug | 行为差异必须显式记录，必要时提供开关 |
| **不保留完整构建模式** | 删了完整构建的CMake逻辑，无法对比验证 | 始终保留full模式作为"标准答案" |
| **在shim中用#ifdef** | shim本身又引入条件编译，复杂度不减反增 | shim应该简单直白，复杂逻辑说明不该用shim |
| **上游API变化不跟进** | 上游boost升级了API，shim不更新导致merge冲突 | 定期同步上游，shim随上游API演进 |

## Caffe 实际验证案例

**caffex→caffe-cpp-slim 裁剪结果**：
- 裁剪前依赖：boost、glog、gflags、OpenCV、HDF5、LMDB、LevelDB、boost::python、CUDA、BLAS（10个）
- 裁剪后依赖：protobuf、DLPack、TVM FFI（header-only）、可选CUDA/BLAS（3-4个）
- 源码改动：新增compat/目录（约5个shim头文件），caffex/原始代码零修改
- 构建产物：libcaffe_core.a（无依赖静态推理核心）+ _caffe.so（FFI绑定）
- 净代码变化：+867/-7913行（净减7046行）

## 与现有模式的关系

| 关联模式 | 关系 |
|---------|------|
| [thin-entry-shim.md](thin-entry-shim.md) | 同属shim思想：thin-entry-shim解决API路径兼容，本模式解决依赖兼容 |
| [cascade-update-topology.md](cascade-update-topology.md) | 渐进式裁剪可以按依赖拓扑排序，先裁剪被依赖最少的 |
| [incremental-regression-verification.md](incremental-regression-verification.md) | 每个shim添加后立即做增量验证，不破坏已有功能 |
| [c-abi-dynamic-binding.md](c-abi-dynamic-binding.md) | 裁剪完成后，C ABI绑定是slim核心对外暴露的标准方式 |
| [staged-startup-integration-loading.md](staged-startup-integration-loading.md) | 都体现渐进式、可回滚的架构思想 |

## 相关决策

- [c-abi-dynamic-binding.md](c-abi-dynamic-binding.md)：slim核心对外的绑定方式选择
- [four-step-extension-recipe.md](four-step-extension-recipe.md)：框架扩展时如何保持依赖最小化
