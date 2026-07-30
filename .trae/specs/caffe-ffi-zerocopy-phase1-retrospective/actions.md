# C阶段 - 原子行动项

> G4质量门：每个行动项满足单一职责、可独立验证、有明确验收标准

---

## A1：Phase 2 COW 实施前的依赖类型系统预检

**所属洞察**：I1（第三方依赖类型系统"勿重复实现已有功能"原则）
**优先级**：高
**Owner建议**：Phase 2实施者

**描述**：
在开始Phase 2 COW代码编写之前，执行一次tvm-ffi类型系统预检：
1. 列出COW实现需要用到的所有tvm-ffi容器/类型（Tensor、Array、Map、use_count()等）
2. Grep搜索tvm-ffi头文件，确认TypeTraits、Allocator、Ref/Move等基础设施是否已由vendor提供
3. 确认是否需要自定义TypeTraits特化；如需要，先验证与现有TypeTraits无冲突

**验收标准**：
- [ ] 输出一份《Phase 2 tvm-ffi API依赖清单》，列出所有需要使用的tvm-ffi类型和方法
- [ ] 清单中标注每个API是否由vendor提供，是否需要自定义扩展
- [ ] 如需自定义TypeTraits，先写一个最小编译单元验证与现有类型系统兼容（不出现SFINAE冲突）
- [ ] 预检完成并review通过后，才开始编写COW业务代码

**依赖**：无（可独立执行）
**预估工时**：0.5天

---

## A2：Blob::cpu_mutable_data() COW 触发点实现

**所属洞察**：I4（性能优化分层增量策略）、PAT-001
**优先级**：高
**Owner建议**：Phase 2实施者

**描述**：
在Blob类的cpu_mutable_data()和gpu_mutable_data()方法中添加COW触发逻辑：
1. 检查data_tensor_.use_count() > 1
2. 如是，调用CloneTensor()创建私有副本
3. 将data_tensor_替换为私有副本
4. 输出[COW]日志：Unshared data, refcount=N, nbytes=X
5. 对diff_tensor_做同样处理
6. 遵循PAT-001"显式打断语义"原则，在注释中明确cpu_mutable_data()会打断共享

**验收标准**：
- [ ] cpu_mutable_data()在use_count()>1时创建私有副本，调用后use_count()==1
- [ ] cpu_data()（const版本）不触发COW，保持零拷贝共享
- [ ] [COW]日志包含refcount、nbytes字段
- [ ] C++单元测试覆盖：共享后调用mutable_data→指针不再相等、引用计数回到1、数据内容正确复制
- [ ] 单元测试覆盖：const访问不触发复制
- [ ] N=1场景仍走Phase 1零拷贝路径，无性能回退

**依赖**：A1（依赖预检完成）
**预估工时**：1天

---

## A3：Windows 开发环境 DLL 自检脚本

**所属洞察**：I3（Windows DLL三层配置原则）
**优先级**：中
**Owner建议**：构建系统维护者

**描述**：
编写一个Python脚本或xs doctor子命令，在Windows开发环境启动时自动检查：
1. tvm_ffi.dll是否在PATH或可通过os.add_dll_directory找到
2. _caffe_ffi.dll是否可被加载（尝试ctypes.CDLL）
3. KMP_DUPLICATE_LIB_OK环境变量是否设置
4. 当前Python版本是否为conda环境Python 3.14+

**验收标准**：
- [ ] 脚本输出PASS/FAIL状态，FAIL时给出具体修复指引
- [ ] 脚本集成到clean_build_test.cmd或dev.ps1开头，环境异常时提前终止并提示
- [ ] README或开发文档中引用此脚本作为Windows环境验证步骤
- [ ] 检查覆盖三层配置点（PATH环境变量、Python dll目录、CMake安装路径提示）

**依赖**：无（可独立执行）
**预估工时**：0.5天

---

## A4：N=2 COW 场景单元测试先行

**所属洞察**：I4（分层增量策略）、PAT-001
**优先级**：高
**Owner建议**：Phase 2实施者

**描述**：
在实现N≥2 COW逻辑之前/同时，按照"测试三件套+扩展"原则编写单元测试：
1. 两个top共享bottom后，调用top[0]->mutable_cpu_data()触发COW
2. 验证top[0]数据指针与bottom不再相等，top[1]仍与bottom共享（或根据实现策略验证）
3. 修改top[0]数据后，bottom和top[1]数据不受污染（COW正确性）
4. 验证COW日志[COW] Unshared正确输出
5. Python端添加Split N=2测试用例，验证in-place修改不会交叉污染

**验收标准**：
- [ ] test_blob_zerocopy.cpp新增COW测试用例≥3个（mutable_data触发、const不触发、数据隔离）
- [ ] Python tests新增Split N=2 in-place修改测试用例≥1个
- [ ] 所有COW测试在实现前应失败（红），实现后通过（绿）
- [ ] [COW]日志的copy_triggered字段在CSV性能日志中可被捕获

**依赖**：A2（COW触发点实现）
**预估工时**：1天

---

## A5：API 设计调用方清单检查项

**所属洞察**：I2（API边界分层设计）、PAT-002
**优先级**：中
**Owner建议**：代码审查者

**描述**：
在代码审查checklist中新增一项API设计检查：每个新增的Blob/Layer公共方法必须在MR/PR描述中列出调用方清单（内部C++层、Python FFI层、其他绑定）。
1. 确认方法参数类型对内部调用方友好（原始指针而非智能指针）
2. 确认FFI注册层有对应的lambda桥接
3. 确认null检查使用统一的!= nullptr风格

**验收标准**：
- [ ] 项目代码审查checklist文档新增"API调用方清单"检查项
- [ ] Phase 2 COW相关的所有新方法（如UnshareData()、CloneTensor()等）在CR时通过此检查
- [ ] FFI注册文件_caffe_ffi.cc中所有新方法都有lambda桥接（无直接透传ObjectPtr到内部方法的情况）

**依赖**：无（可独立执行，与A2/A4并行）
**预估工时**：0.2天
