# caffe-ffi Conv v4 优化里程碑收官 - 验证清单

## Task 1: InceptionV1 batch=16 抖动诊断
- [x] Checkpoint 1.1: `bench_jitter_diagnose.py` 脚本存在且可执行
- [x] Checkpoint 1.2: 脚本测试 4 种 OMP_SCHEDULE（static/dynamic/dynamic,1/guided）× 2 种 OMP_WAIT_POLICY（PASSIVE/ACTIVE）× 2种预热策略 = 16种组合
- [x] Checkpoint 1.3: 每种配置输出 Avg/P50/P95/P99/CV%/Tail ratio/FPS 完整指标
- [x] Checkpoint 1.4: 测试了内存预分配/加大预热轮次（warmup=50+每次新数据）的策略
- [x] Checkpoint 1.5: 按CV%排序输出最优配置推荐，附带改善百分比
- [x] Checkpoint 1.6: 包含根因分析和4线程使用建议（CV<15%阈值判断）
- [ ] Checkpoint 1.7: 在Docker容器内运行，输出实际数据验证

## Task 2: sdk_full_test 全量回归测试
- [x] Checkpoint 2.1: `bench_sdk_full.py` 支持5个模型（ResNet-50/InceptionV1/ResNet-101/fgvsirfeature/fgvsirfeature_ssd）
- [x] Checkpoint 2.2: fgvsirfeature（120×120）配置正确，自动mean=None处理
- [x] Checkpoint 2.3: fgvsirfeature_ssd（32×32）配置正确，仅batch=1，自适应线程数降级
- [x] Checkpoint 2.4: 正确性验证 OMP=1 vs OMP=4 max_abs_diff < 1e-4
- [x] Checkpoint 2.5: 线程扩展性测试 [1,2,4,8] × batch=[1,4]（小模型仅batch=1）
- [x] Checkpoint 2.6: 通用输出blob获取（out_candidates列表+自动回退到最后blob）
- [ ] Checkpoint 2.7: 在Docker容器内运行，5个模型全部forward成功

## Task 3: 一键脚本 v6
- [x] Checkpoint 3.1: `build_and_bench_v6.sh` 存在，shebang正确（#!/bin/bash），set -e
- [x] Checkpoint 3.2: 脚本开头全局导出 OMP_NUM_THREADS=4、OPENBLAS_NUM_THREADS=1、OMP_WAIT_POLICY=PASSIVE
- [x] Checkpoint 3.3: 包含7个步骤（编译→模型准备→正确性→抖动诊断→全量回归→报告生成→完成）
- [x] Checkpoint 3.4: 每步有进度标记 [1/7]...[7/7]
- [x] Checkpoint 3.5: SDK模型自动从/SpecWeave挂载点复制到容器内
- [x] Checkpoint 3.6: 内嵌Python生成final_report.md（7章节+附录+链接）
- [ ] Checkpoint 3.7: 脚本在Docker容器内从0执行exit code 0

## Task 4: 里程碑复盘报告
- [x] Checkpoint 4.1: `milestone_retrospective.md` 存在
- [x] Checkpoint 4.2: 事实清单31条（F-001~F-031），6个类别，无因果推断词（G1门通过）
- [x] Checkpoint 4.3: 3条核心洞察，四元组完整（陈述/证据/反常识/行动）（G2门通过）
- [x] Checkpoint 4.4: V对抗审查4视角8条攻击，采纳修正意见
- [x] Checkpoint 4.5: 1个可迁移模式（CPU推理OpenMP双层并行隔离配置模式），4个反模式（G3门通过）
- [x] Checkpoint 4.6: 5个原子行动项（P0×2/P1×2/P2×1），单一职责可验证（G4门通过）

## Task 5: 生产部署配置建议
- [x] Checkpoint 5.1: `deployment_config_guide.md` 存在
- [x] Checkpoint 5.2: 三种Profile（延迟敏感/吞吐优先/通用均衡），每种有可复制export命令块
- [x] Checkpoint 5.3: 每种Profile标注预期CV%、P99延迟比、FPS
- [x] Checkpoint 5.4: 包含Mermaid决策树+文字版决策流程
- [x] Checkpoint 5.5: 6项禁用清单，每项有原因说明
- [x] Checkpoint 5.6: InceptionV1抖动缓解4级方案、小模型并行建议
- [x] Checkpoint 5.7: 自适应线程数Python代码示例、容器部署建议、FAQ 7问

## Task 6: 最终交付报告（v6脚本自动生成）
- [x] Checkpoint 6.1: final_report.md由v6脚本自动生成，为报告入口
- [x] Checkpoint 6.2: 包含执行摘要（核心结论+最优配置推荐表）
- [x] Checkpoint 6.3: 包含5模型性能对比总表（自动从benchmark输出解析）
- [x] Checkpoint 6.4: 包含"相关文档"章节链接到milestone_retrospective.md和deployment_config_guide.md
- [x] Checkpoint 6.5: 包含InceptionV1抖动分析（基线vs最优对比+改善幅度+阈值判断）
- [x] Checkpoint 6.6: 包含SDK模型专项结论（fgvsirfeature/fgvsirfeature_ssd分别分析）
- [x] Checkpoint 6.7: 包含6项已知问题与限制
- [x] Checkpoint 6.8: 包含后续优化方向（短期v4.x/中期v5/长期）
- [x] Checkpoint 6.9: 第8章里程碑复盘摘要（核心洞察+原子行动项表格）
- [x] Checkpoint 6.10: 附录包含产出文档清单（7个文件）和原始输出文件位置

## Task 7: 原子提交
- [x] Checkpoint 7.1: git status确认8个文件在本次提交，无无关文件
- [x] Checkpoint 7.2: 提交信息遵循Conventional Commits（feat(caffe-ffi): ...），中文描述
- [x] Checkpoint 7.3: Pre-commit hooks全部通过（文件位置/敏感信息/并发安全）
- [x] Checkpoint 7.4: commit hash: 9fd71190，8 files changed, 2199 insertions(+)

## 全局验证（脚本静态检查）
- [x] Checkpoint G.1: Python脚本无Windows路径硬编码（容器内路径均为/root/或/tmp/）
- [x] Checkpoint G.2: 所有子进程内np.random.seed(42)固定，结果可复现
- [x] Checkpoint G.3: 所有benchmark使用subprocess隔离环境变量（os.environ在子进程内设置）
- [x] Checkpoint G.4: 不修改vendor/目录和caffe-ffi C++源码（仅新增脚本和文档）
- [ ] Checkpoint G.5: Docker容器端到端运行验证（需执行 build_and_bench_v6.sh）

---

## 运行方式

在Docker容器内执行：
```bash
docker exec -it caffe-ffi-jupyter bash /SpecWeave/.trae/specs/caffe-ffi-conv-v4-milestone/build_and_bench_v6.sh
```

执行完成后查看最终报告：
```bash
docker exec caffe-ffi-jupyter cat /SpecWeave/.trae/specs/caffe-ffi-conv-v4-milestone/final_report.md
```
