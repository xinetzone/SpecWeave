# caffe-ffi Conv v4 优化里程碑收官 - 验证清单

## Task 1: InceptionV1 batch=16 抖动诊断
- [ ] Checkpoint 1.1: `bench_jitter_diagnose.py` 脚本存在且可执行
- [ ] Checkpoint 1.2: 脚本至少测试 3 种 OMP_SCHEDULE（static/dynamic/guided）× 2 种 OMP_WAIT_POLICY（PASSIVE/ACTIVE）
- [ ] Checkpoint 1.3: 每种配置输出 Avg/P50/P95/P99/CV%/Tail ratio 完整指标
- [ ] Checkpoint 1.4: 测试了内存预分配/加大预热轮次的策略
- [ ] Checkpoint 1.5: 给出明确的最优配置推荐，附带CV%改善百分比
- [ ] Checkpoint 1.6: 如果无法将CV%降到15%以下，明确说明根因和是否使用多线程的建议

## Task 2: sdk_full_test 全量回归测试
- [ ] Checkpoint 2.1: `bench_sdk_full.py` 支持5个模型（ResNet-50/InceptionV1/ResNet-101/fgvsirfeature/fgvsirfeature_ssd）
- [ ] Checkpoint 2.2: fgvsirfeature 模型（120×120输入）加载成功，forward无报错
- [ ] Checkpoint 2.3: fgvsirfeature_ssd 小模型加载成功，forward无报错（自适应线程数降级正确）
- [ ] Checkpoint 2.4: OMP=1 vs OMP=4 正确性验证 max_abs_diff < 1e-4（有权重模型）
- [ ] Checkpoint 2.5: 每个模型输出完整性能表（线程1/2/4/8 × batch=1/4）
- [ ] Checkpoint 2.6: SDK模型的输入尺寸和mean values自动适配正确

## Task 3: 一键脚本 v6
- [ ] Checkpoint 3.1: `build_and_bench_v6.sh` 存在，shebang正确（#!/bin/bash）
- [ ] Checkpoint 3.2: 脚本开头全局导出 OMP_NUM_THREADS=4、OPENBLAS_NUM_THREADS=1、OMP_WAIT_POLICY=PASSIVE
- [ ] Checkpoint 3.3: 包含7个步骤（编译→模型准备→正确性→抖动诊断→全量回归→报告生成→完成提示）
- [ ] Checkpoint 3.4: 每步有进度标记 [1/7]...[7/7]
- [ ] Checkpoint 3.5: set -e 确保任一步失败即停止
- [ ] Checkpoint 3.6: 脚本执行exit code 0，输出final_report.md路径
- [ ] Checkpoint 3.7: final_report.md 包含所有必要章节

## Task 4: 里程碑复盘报告
- [ ] Checkpoint 4.1: `milestone_retrospective.md` 存在
- [ ] Checkpoint 4.2: 事实清单≥20条，每条编号F-001起，无因果推断词（G1门）
- [ ] Checkpoint 4.3: 3条核心洞察，每条包含陈述/证据(引用F-xxx)/反常识/行动四元组（G2门）
- [ ] Checkpoint 4.4: 萃取1-2个可迁移模式，包含触发场景、核心步骤、≥3个反模式（G3门）
- [ ] Checkpoint 4.5: 3-5个原子行动项，满足单一职责、可独立验证（G4门）
- [ ] Checkpoint 4.6: 报告结构化（R/I/E/A/C各章节清晰分隔）

## Task 5: 生产部署配置建议
- [ ] Checkpoint 5.1: `deployment_config_guide.md` 存在
- [ ] Checkpoint 5.2: 包含三种Profile（延迟敏感/吞吐优先/通用均衡），每种有完整export命令块
- [ ] Checkpoint 5.3: 每种Profile标注预期CV%和尾延迟比
- [ ] Checkpoint 5.4: 包含配置决策树（根据场景选择Profile）
- [ ] Checkpoint 5.5: 包含禁用项清单（不要设置的环境变量及原因）
- [ ] Checkpoint 5.6: 包含InceptionV1和小模型（fgvsirfeature_ssd）的特殊注意事项
- [ ] Checkpoint 5.7: 配置参数与实际benchmark数据一致（推荐线程数=实测最优值）

## Task 6: 最终交付报告
- [ ] Checkpoint 6.1: `final_report.md` 存在且为报告入口
- [ ] Checkpoint 6.2: 包含执行摘要（核心结论一页可读）
- [ ] Checkpoint 6.3: 包含5个模型性能对比总表
- [ ] Checkpoint 6.4: 包含部署配置建议摘要（链接到deployment_config_guide.md）
- [ ] Checkpoint 6.5: 包含InceptionV1抖动分析结论
- [ ] Checkpoint 6.6: 包含SDK模型专项结论
- [ ] Checkpoint 6.7: 包含已知问题与限制
- [ ] Checkpoint 6.8: 包含后续优化方向
- [ ] Checkpoint 6.9: 内部文档引用使用相对路径

## Task 7: 原子提交
- [ ] Checkpoint 7.1: git status 确认只有预期的新文件/修改文件
- [ ] Checkpoint 7.2: 提交信息遵循 Conventional Commits 规范，中文描述
- [ ] Checkpoint 7.3: 提交后验证文件完整性（无乱码、无遗漏）

## 全局验证
- [ ] Checkpoint G.1: 所有Python脚本可在容器内独立运行，无路径硬编码错误
- [ ] Checkpoint G.2: 所有测试使用固定随机种子(42)，结果可复现
- [ ] Checkpoint G.3: 所有benchmark使用子进程隔离环境变量，避免互相干扰
- [ ] Checkpoint G.4: 不修改vendor/目录和caffe-ffi C++源码（仅新增脚本和文档）
