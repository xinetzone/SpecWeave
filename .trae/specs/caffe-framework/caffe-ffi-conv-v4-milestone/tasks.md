# caffe-ffi Conv v4 优化里程碑收官 - 实现计划

## [ ] Task 1: InceptionV1 batch=16 抖动诊断脚本开发
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 开发 `bench_jitter_diagnose.py`，系统测试 OMP_SCHEDULE（static/dynamic/guided）× OMP_WAIT_POLICY（PASSIVE/ACTIVE）× 预热轮次（5/20/50）的组合
  - 测试"内存预分配"策略：预热阶段先跑多次forward使OpenBLAS内存池、OS page cache、caffe-ffi blob内存全部touch后再计时
  - 每个组合运行30次迭代，记录Avg/P50/P95/P99/CV%/Tail ratio
  - 定位抖动根因（线程调度开销/缓存抖动/BLAS内存分配/GEMM粒度太小）
  - 输出抖动诊断结论：推荐配置组合 + CV%改善幅度
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-1.1: 脚本可独立运行，至少测试12种配置组合（3 schedule × 2 wait policy × 2 warmup策略）
  - `programmatic` TR-1.2: 输出每种配置的完整稳定性指标表（Avg/P50/P95/P99/CV%/Tail）
  - `programmatic` TR-1.3: 给出明确的最优配置推荐，附带CV%对比数据
  - `human-judgement` TR-1.4: 诊断结论有逻辑支撑，不只是罗列数据
- **Notes**: 重点关注 OMP_SCHEDULE=dynamic,1 是否比 static 更好（小GEMM场景）；内存预分配策略通过加大warmup迭代次数+warmup阶段打乱输入数据实现

## [ ] Task 2: sdk_full_test 模型适配与全量回归测试脚本
- **Priority**: high
- **Depends On**: None（可与Task 1并行，但最终整合需等Task 1完成）
- **Description**:
  - 将 fgvsirfeature（人脸嵌入，120×120）和 fgvsirfeature_ssd（人脸检测）模型加入测试套件
  - 开发 `bench_sdk_full.py`，支持5个模型（ResNet-50、InceptionV1、ResNet-101、fgvsirfeature、fgvsirfeature_ssd）
  - 自动检测输入尺寸（从prototxt解析或使用默认值），适配不同mean values（人脸模型可能不需要ImageNet mean）
  - 模型路径适配：SDK模型从 sdk_full_test 目录加载，标准模型从 ~/.caffe_test_data/models/ 加载
  - 对fgvsirfeature_ssd小模型进行特殊处理：通道数可能<32，此时min_chunk=32策略应自动降级
  - 运行batch=1和batch=4（人脸模型batch=16可能过大）的稳定性测试
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-2.1: 5个模型全部加载成功，forward不报错
  - `programmatic` TR-2.2: OMP=1 vs OMP=4正确性检查max_abs_diff < 1e-4（排除随机权重模型ResNet-101）
  - `programmatic` TR-2.3: 每个模型输出完整性能表（线程数1/2/4/8 × batch=1/4）
  - `programmatic` TR-2.4: fgvsirfeature_ssd等小模型在OMP>1时不崩溃（自适应线程数正确降级）
- **Notes**: fgvsirfeature使用caffe-ffi格式caffemodel（已在playground/caffemodel-conversion/sdk_full_test/下转换好），需确认容器内路径

## [ ] Task 3: 一键脚本 build_and_bench_v6.sh 开发
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**:
  - 基于 build_and_bench_v5.sh 升级为v6版本，整合以下步骤：
    1. 编译（cmake --build）
    2. 模型准备（下载ResNet-101 prototxt、复制/链接SDK模型到容器内）
    3. 全局环境变量导出（OMP_NUM_THREADS=4、OPENBLAS_NUM_THREADS=1、OMP_WAIT_POLICY=PASSIVE）
    4. 正确性验证（OMP=1 vs OMP=4，所有模型）
    5. InceptionV1抖动诊断（运行Task 1的脚本）
    6. sdk_full_test全量回归（运行Task 2的脚本，使用Task 1推荐的最优配置）
    7. 自动生成最终Markdown报告
  - 报告自动生成：将所有测试输出汇总为一份 final_report.md
  - 错误处理：任一步骤失败输出明确错误信息并停止
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-3.1: 脚本从头执行到尾exit code 0
  - `programmatic` TR-3.2: 所有步骤有明确的进度输出（[1/7]、[2/7]...）
  - `programmatic` TR-3.3: 最终报告 final_report.md 存在且包含所有章节
  - `programmatic` TR-3.4: 全局环境变量在脚本开头导出，子进程正确继承
- **Notes**: 报告生成可以用Python脚本将benchmark输出解析为Markdown表格

## [ ] Task 4: 里程碑复盘报告（七概念方法论 R→I→E→C）
- **Priority**: high
- **Depends On**: Task 3（需要最终测试数据作为事实来源）
- **Description**:
  - 按照七概念方法论场景1（里程碑复盘）+场景2（问题解决，针对InceptionV1抖动）混合链路执行：
  - **R（复盘）**：采集≥20条客观事实（时间线、关键决策、性能数据、环境配置、遇到的问题与解决方案）
  - **I（洞察）**：提炼3条核心洞察，每条包含四元组（陈述/证据/反常识/行动）
    - 洞察1：并行策略的扩展性与模型结构的关系（小卷积核/小batch的Amdahl瓶颈）
    - 洞察2：环境变量配置的系统性风险（局部设置vs全局导出）
    - 洞察3：OpenMP调度策略对尾延迟的影响
  - **E（萃取）**：萃取1-2个可迁移模式（如"CPU推理OpenMP环境变量配置模式"）
  - **C（原子行动项）**：产出3-5个原子化后续行动项
  - 报告保存为 `milestone_retrospective.md`
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-4.1: 事实清单≥20条，无"因为/所以/导致"等因果推断词（G1门检查）
  - `programmatic` TR-4.2: 3条洞察每条都包含陈述/证据(F-xxx引用)/反常识/行动四要素（G2门检查）
  - `human-judgement` TR-4.3: 模式文档包含触发场景、核心步骤、≥3个反模式、迁移验证（G3门检查）
  - `programmatic` TR-4.4: 行动项原子化（单一职责、可独立验证、有验收标准）（G4门检查）
- **Notes**: 事实编号F-001起，洞察引用事实编号

## [ ] Task 5: 生产部署配置建议文档
- **Priority**: high
- **Depends On**: Task 1, Task 2（需要抖动诊断结果和SDK模型数据）
- **Description**:
  - 基于所有测试数据，生成 `deployment_config_guide.md`，包含三种部署Profile：
    - **Profile A: 延迟敏感型**（batch=1，实时推理场景如人脸识别）：OMP线程数推荐、预期延迟/P99/CV%、配置命令块
    - **Profile B: 吞吐优先型**（batch=N，批量处理场景如离线特征提取）：OMP线程数推荐、预期FPS、配置命令块
    - **Profile C: 通用均衡型**（默认推荐，兼顾延迟和吞吐）：OMP=4配置、适用场景说明
  - 包含决策树：根据输入尺寸(batch大小/分辨率)和SLA要求选择Profile
  - 包含禁用项清单：不要设置OMP_PROC_BIND、不要用多线程BLAS、不要设置OMP_WAIT_POLICY=ACTIVE
  - 包含InceptionV1等Inception系列模型的特殊注意事项
  - 包含SDK模型（fgvsirfeature等小输入模型）的专门建议
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `human-judgement` TR-5.1: 三种Profile配置命令可复制即用，无需修改
  - `programmatic` TR-5.2: 配置参数与benchmark数据一致（推荐线程数对应实际最优值）
  - `human-judgement` TR-5.3: 决策树逻辑清晰，覆盖常见场景
  - `human-judgement` TR-5.4: 禁用项有数据支撑（说明为什么不要这么做）
- **Notes**: 小模型（如fgvsirfeature_ssd，251KB）的并行收益可能极低，需要专门说明OMP=1可能更优

## [ ] Task 6: 最终交付报告整合
- **Priority**: high
- **Depends On**: Task 3, Task 4, Task 5
- **Description**:
  - 在 `final_report.md` 中整合所有产出：
    1. 执行摘要（核心结论、最优配置、性能提升数据）
    2. 模型性能对比总表（5个模型 × 推荐配置 × 延迟/FPS/CV%/稳定性评级）
    3. 部署配置建议摘要（指向 deployment_config_guide.md）
    4. InceptionV1抖动分析结论（指向诊断结果）
    5. SDK模型专项结论（fgvsirfeature/fgvsirfeature_ssd性能表现）
    6. 已知问题与限制
    7. 后续优化方向
  - 将里程碑复盘摘要（关键洞察和行动项）作为附录
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `human-judgement` TR-6.1: 报告结构清晰，非技术人员也能理解执行摘要
  - `programmatic` TR-6.2: 性能数据表数字与原始benchmark输出一致
  - `human-judgement` TR-6.3: 结论都有数据支撑，没有无依据的断言
  - `programmatic` TR-6.4: 所有内部文档引用使用相对路径链接
- **Notes**: 最终报告是唯一需要交付给用户的文档入口，其他文档作为附件引用

## [ ] Task 7: 原子提交交付
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 使用 atomic-commit-cmd 进行原子提交，遵循 Conventional Commits 规范
  - 提交信息格式：`feat(caffe-ffi): conv v4 milestone - retrospective, deployment guide, sdk regression`
  - 确保所有新文件在正确路径下（spec目录或playground目录）
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `programmatic` TR-7.1: git status 确认只有预期文件变更
  - `programmatic` TR-7.2: 提交信息符合规范，中文描述
  - `programmatic` TR-7.3: 提交后验证文件完整性
- **Notes**: 如果在Windows环境下git commit中文乱码，使用UTF-8文件方式提交
