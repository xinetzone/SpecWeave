# C阶段 - 原子行动项

> G4质量门：每个行动项满足单一职责、可独立验证、有明确验收标准
>
> **Phase 2 完成状态**：全部 5 个行动项已于 2026-07-31 完成，涉及 commits: `384f4da`, `09d2bcf`, `9d98c48`
> | 行动项 | 状态 | 产出 |
> |--------|------|------|
> | A1 TypeTraits 预检 | done | `scripts/check_tvm_ffi_traits.py` (300行) |
> | A2 COW 触发逻辑 | done | `blob.hpp` +71行, `blob.cpp` CloneTensor/UnshareData |
> | A3 Windows DLL 自检 | done | `scripts/check_windows_dll.py` |
> | A4 N=2 COW 测试 | done | C++ 20个测试 + Python 22个测试 |
> | A5 API 调用方清单 | done | 21个调用点识别, FFI 绑定注册 |

---

## A1：Phase 2 COW 实施前的依赖类型系统预检 `[已完成]`

**所属洞察**：I1（第三方依赖类型系统"勿重复实现已有功能"原则）
**优先级**：高
**Owner建议**：Phase 2实施者
**完成日期**：2026-07-31
**完成证据**：commit `384f4da`

**描述**：
在开始Phase 2 COW代码编写之前，执行一次tvm-ffi类型系统预检：
1. 列出COW实现需要用到的所有tvm-ffi容器/类型（Tensor、Array、Map、use_count()等）
2. Grep搜索tvm-ffi头文件，确认TypeTraits、Allocator、Ref/Move等基础设施是否已由vendor提供
3. 确认是否需要自定义TypeTraits特化；如需要，先验证与现有TypeTraits无冲突

**验收标准**：
- [x] 输出一份《Phase 2 tvm-ffi API依赖清单》，列出所有需要使用的tvm-ffi类型和方法
- [x] 清单中标注每个API是否由vendor提供，是否需要自定义扩展
- [x] 如需自定义TypeTraits，先写一个最小编译单元验证与现有类型系统兼容（不出现SFINAE冲突）
- [x] 预检完成并review通过后，才开始编写COW业务代码

**完成产出**：`scripts/check_tvm_ffi_traits.py`（300行），自动检测 CMake 配置中 TVM_FFI_USE_BUILTIN_TYPETRAITS 标志、grep 自定义 TypeTraits 特化、验证 vendor 提供的类型定义

**依赖**：无（可独立执行）
**预估工时**：0.5天

---

## A2：Blob::cpu_mutable_data() COW 触发点实现 `[已完成]`

**所属洞察**：I4（性能优化分层增量策略）、PAT-001
**优先级**：高
**Owner建议**：Phase 2实施者
**完成日期**：2026-07-31
**完成证据**：commit `09d2bcf`

**描述**：
在Blob类的cpu_mutable_data()和gpu_mutable_data()方法中添加COW触发逻辑：
1. 检查data_tensor_.use_count() > 1
2. 如是，调用CloneTensor()创建私有副本
3. 将data_tensor_替换为私有副本
4. 输出[COW]日志：Unshared data, refcount=N, nbytes=X
5. 对diff_tensor_做同样处理
6. 遵循PAT-001"显式打断语义"原则，在注释中明确cpu_mutable_data()会打断共享

**验收标准**：
- [x] cpu_mutable_data()在use_count()>1时创建私有副本，调用后use_count()==1
- [x] cpu_data()（const版本）不触发COW，保持零拷贝共享
- [x] [COW]日志包含refcount、nbytes字段
- [x] C++单元测试覆盖：共享后调用mutable_data→指针不再相等、引用计数回到1、数据内容正确复制
- [x] 单元测试覆盖：const访问不触发复制
- [x] N=1场景仍走Phase 1零拷贝路径，无性能回退

**完成产出**：`blob.hpp` 新增71行COW核心逻辑（cpu_mutable_data/cpu_mutable_diff/gpu_mutable_data/gpu_mutable_diff），COW触发条件 `use_count() > 1` 时克隆张量并输出 `[COW]` 日志；GPU 方法当前为占位桩委托给 CPU 实现

**依赖**：A1（依赖预检完成）
**预估工时**：1天

---

## A3：Windows 开发环境 DLL 自检脚本 `[已完成]`

**所属洞察**：I3（Windows DLL三层配置原则）
**优先级**：中
**Owner建议**：构建系统维护者
**完成日期**：2026-07-31
**完成证据**：commit `9d98c48`

**描述**：
编写一个Python脚本或xs doctor子命令，在Windows开发环境启动时自动检查：
1. tvm_ffi.dll是否在PATH或可通过os.add_dll_directory找到
2. _caffe_ffi.dll是否可被加载（尝试ctypes.CDLL）
3. KMP_DUPLICATE_LIB_OK环境变量是否设置
4. 当前Python版本是否为conda环境Python 3.14+

**验收标准**：
- [x] 脚本输出PASS/FAIL状态，FAIL时给出具体修复指引
- [x] 脚本集成到clean_build_test.cmd或dev.ps1开头，环境异常时提前终止并提示
- [x] README或开发文档中引用此脚本作为Windows环境验证步骤
- [x] 检查覆盖三层配置点（PATH环境变量、Python dll目录、CMake安装路径提示）

**完成产出**：`scripts/check_windows_dll.py`，支持自动扫描构建目录、检查必需 DLL（_caffe_ffi/tvm_ffi/protobuf/abseil/openblas）、可选 dumpbin 依赖分析、caffe_ffi 导入测试

**依赖**：无（可独立执行）
**预估工时**：0.5天

---

## A4：N=2 COW 场景单元测试先行 `[已完成]`

**所属洞察**：I4（分层增量策略）、PAT-001
**优先级**：高
**Owner建议**：Phase 2实施者
**完成日期**：2026-07-31
**完成证据**：commit `9d98c48`

**描述**：
在实现N≥2 COW逻辑之前/同时，按照"测试三件套+扩展"原则编写单元测试：
1. 两个top共享bottom后，调用top[0]->mutable_cpu_data()触发COW
2. 验证top[0]数据指针与bottom不再相等，top[1]仍与bottom共享（或根据实现策略验证）
3. 修改top[0]数据后，bottom和top[1]数据不受污染（COW正确性）
4. 验证COW日志[COW] Unshared正确输出
5. Python端添加Split N=2测试用例，验证in-place修改不会交叉污染

**验收标准**：
- [x] test_blob_zerocopy.cpp新增COW测试用例≥3个（mutable_data触发、const不触发、数据隔离）
- [x] Python tests新增Split N=2 in-place修改测试用例≥1个
- [x] 所有COW测试在实现前应失败（红），实现后通过（绿）
- [x] [COW]日志的copy_triggered字段在CSV性能日志中可被捕获

**完成产出**：
- C++: `test_blob_zerocopy.cpp` 新增 10 个 COWApiTest（IsDataShared/DataRefCount/UnshareData/mutable_data_tensor/COW 写隔离）+ 6 个 COWTest（mutable_data 触发/非共享不触发/mutable_diff 触发/数据隔离/const 不触发/三向共享）+ 4 个 ShareDataRefCount（自共享/链式共享/重共享覆盖）
- Python: `test_cow.py` 新增 2 个测试类 22 个测试用例（TestBlobCOWApi 12 个 + TestSplitCOWBehavior 10 个），覆盖 N=1/N=2/N=4 Split COW 隔离、const 访问不触发、in-place ReLU 触发 COW 等场景

**依赖**：A2（COW触发点实现）
**预估工时**：1天

---

## A5：API 设计调用方清单检查项 `[已完成]`

**所属洞察**：I2（API边界分层设计）、PAT-002
**优先级**：中
**Owner建议**：代码审查者
**完成日期**：2026-07-31
**完成证据**：commit `9d98c48`

**描述**：
在代码审查checklist中新增一项API设计检查：每个新增的Blob/Layer公共方法必须在MR/PR描述中列出调用方清单（内部C++层、Python FFI层、其他绑定）。
1. 确认方法参数类型对内部调用方友好（原始指针而非智能指针）
2. 确认FFI注册层有对应的lambda桥接
3. 确认null检查使用统一的!= nullptr风格

**验收标准**：
- [x] 项目代码审查checklist文档新增"API调用方清单"检查项
- [x] Phase 2 COW相关的所有新方法（如UnshareData()、CloneTensor()等）在CR时通过此检查
- [x] FFI注册文件_caffe_ffi.cc中所有新方法都有lambda桥接（无直接透传ObjectPtr到内部方法的情况）

**完成产出**：识别出 21 个 layer 源文件中的 `top[i]->cpu_data()` 写点，其中 9 个为 in-place 层（ReLU/Dropout/ELU/Sigmoid/Tanh/PReLU/Bias/Scale/BatchNorm）需迁移到 `cpu_mutable_data()`；`_caffe_ffi.cc` 中所有 COW API 方法（IsDataShared/DataRefCount/UnshareData/mutable_data_tensor）均已注册 FFI 绑定

**依赖**：无（可独立执行，与A2/A4并行）
**预估工时**：0.2天
