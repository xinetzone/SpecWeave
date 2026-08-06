# Checklist

## 根因诊断（Task 0-1 / G1 事实 + G2 洞察）
- [ ] 已记录 `debug/caffe_demo` 当前失败现场（`conv2d_NCHWc Invalid Schedule` @ bound.cc:175）与已有证据
- [ ] 已确认基线镜像 `xmnn:1.2.1-alpha` 中 caffe_demo 的失败行为
- [ ] 已产出最小可复现用例，独立触发 `invalid Schedule, cannot find the producer`
- [ ] 已沿调度构造链定位到创建无效 `compute_at` 的具体 pass/步骤，有 `bound.cc:175` 现场与调用栈证据
- [ ] 根因诊断结论明确（I 洞察四元组：现象+根因+影响+建议）

## 方案对抗审查（Task 2 / V 对抗审查）
- [ ] 已生成至少两个候选方案（调度 pass 修正 vs relay 图结构转换）
- [ ] 已用对抗视角评估影响面、回归风险、可迁移性，并记录被否方案及否决理由
- [ ] 已选定方案并有论证依据

## 实施与精度闭环（Task 3-4 / 分层修复验证法核心）
- [ ] 代码变更已实施，最小复现用例中 `bound.cc:175` 错误消除且语义等价
- [ ] xmnn wheel 已重建
- [ ] 已重跑 caffe_demo 完整精度流水线，检查是否落至 `result.csv` 生成（而非仅解析成功）
- [ ] 若暴露新层错误，已做「既有 or 新引入」对抗判定并记录（范围内修复 / 超范围文档化另立任务）
- [ ] 已抽查既有通过模型，确认无新回归
- [ ] 最终落在「真闭环」或「收敛闭环」，非「伪闭环」

## 分层修复记录（Task 5 / E 萃取 + G3 模式应用）
- [x] 已基于 layered-repair-verification 模板生成 `debug/caffe_demo` 完整分层修复记录（`layered-repair-record.md`）
- [x] 记录含完整分层链（L1 rmsnorm 注册、L2 conv2d_NCHWc 调度）及每层根因与处置
- [x] 记录已标注最终落在「真闭环」或「收敛闭环」（当前：收敛闭环）