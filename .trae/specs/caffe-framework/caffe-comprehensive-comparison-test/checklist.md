# Caffe 两实现（caffe-ffi / caffex）综合对比测试 - Verification Checklist

## 环境与测试矩阵
- [x] 检查点1: 两套运行环境已验证可用（caffe-ffi py314 / caffex 的 origin 镜像）
- [x] 检查点2: caffe-ffi C++ 扩展可加载（`import caffe_ffi` 通过，`_caffe_ffi.so` 正常）
- [x] 检查点3: 测试矩阵确定（≥10 算子 + ≥3 网络 + 输入形状 + 固定随机种子）

## caffe-ffi 功能测试（FR-1）
- [x] 检查点4: 在 py314 环境运行 caffe-ffi 测试套件并记录通过/失败/跳过统计
- [x] 检查点5: 核心接口验证通过（`import caffe_ffi` / `read_net` / `net.forward()`）
- [x] 检查点6: 测试结果导出为 JUnit XML / 日志，退出码记录

## caffex 功能测试（FR-2）
- [x] 检查点7: 在 origin 镜像环境运行 caffex `tests/ops/` 测试
- [x] 检查点8: 算子级通过率与 numpy 参考偏差记录
- [x] 检查点9: 实现特性清单（COW 恒等 / dtype / 形状语义 / Backward）产出，作为 vs caffe-ffi 差异分析依据

## 跨实现精度对比（FR-3）
- [x] 检查点10: 逐算子精度指标（max/mean abs error、max rel error、Top-1/Top-5）产出
- [x] 检查点11: 精度数据以 CSV/JSON 保存，数值合理

## 性能与资源占用（FR-4）
- [x] 检查点12: 延迟 mean/std/min/max（ms）与 FPS 产出
- [x] 检查点13: CPU/GPU 资源占用记录，环境差异在上文注明

## 可视化（FR-5）
- [x] 检查点14: 性能对比柱状图 / 精度误差图生成且可离线渲染

## 综合报告（FR-5）
- [x] 检查点15: 报告 8 章节完整（环境/摘要/精度/性能/差异分析/图表/异常/复现附录）
- [x] 检查点16: 报告数据与原始测试结果一致（可追溯）
- [x] 检查点17: 异常记录含问题定位建议
- [x] 检查点18: 报告归档至 `.agents/docs/retrospective/reports/insight-extraction/external-learning/`

## 质量门（七概念）
- [x] G1: 事实部分无因果推断词，纯客观描述
- [x] G2: 差异分析含现象+证据+建议四元组
- [x] V: 报告数据经对抗审查视角自检（异常场景/环境差异/数据可信性）