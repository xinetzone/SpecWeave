# Caffe 两实现（caffe-ffi / caffex）在 hub 真实模型库上的网络级综合对比测试 - Verification Checklist

## 模型清单与 harness（FR-0 / FR-1）
- [x] 检查点1: hub/caffe/ 全部含 `.caffemodel` 的模型已枚举（模型清单条目数 ≥ 25，实际 30）
- [x] 检查点2: 每个模型归一化出「标准 deploy prototxt + caffemodel + 输入形状」三元组，prototxt variant 选择规则明确
- [x] 检查点3: 网络级对比 harness 可在 caffe-ffi 与 caffex 两环境对同一模型分别产出输出文件

## 环境预检
- [x] 检查点4: caffe-ffi py314 环境可用（`import caffe_ffi`、`read_net` 可用，Python 3.14.6 / caffe_ffi 0.1.0）
- [x] 检查点5: caffex origin 镜像可用（`caffe.Net` 可加载模型，BVLC Caffe 1.0 / Python 3.10）
- [x] 检查点6: 两环境版本（Python/numpy/caffe_ffi/caffex）已记录

## caffe-ffi 全模型网络级测试（FR-2）
- [x] 检查点7: 在 py314 环境对全部清单模型执行 `read_net` + `net.forward()`（25/30 通过）
- [x] 检查点8: 记录每个模型的权重加载状态、输出 NaN/Inf、输出形状、加载失败原因

## caffex 全模型网络级测试（FR-3）
- [x] 检查点9: 在 origin 镜像环境对全部清单模型执行 `caffe.Net` + `net.forward()`（25/30 通过，子进程隔离防崩溃连锁）
- [x] 检查点10: 记录每个模型的通过/失败、输出形状、有限值、加载失败原因（含 SIGABRT 崩溃）

## 跨实现精度对比与 A-001 验证（FR-4 / FR-5）
- [x] 检查点11: 逐模型精度指标（max/mean abs error、max rel error、形状一致性、Top-K）产出
- [x] 检查点12: A-001 权重加载缺陷在真实模型上已判定（**已修复**：resnet50 conv1 std=0.1111，输出无 NaN/Inf）

## 性能与资源占用（FR-6）
- [x] 检查点13: 逐模型延迟 mean/std/min/max（ms）与 FPS 产出（net_bench_*.json）
- [x] 检查点14: CPU 累计时间（rusage）已采集；环境差异（OpenBLAS 线程过订阅）已注明

## 可视化与报告（FR-7）
- [x] 检查点15: 结果以结构化 Markdown 表格呈现（性能/精度/通过率/A-001 证据），离线可渲染
- [x] 检查点16: 综合报告 6 章节覆盖（总览/性能/逐模型明细/失败原因/关键结论/产出物清单），涵盖 FR-7 要求的 8 个主题
- [x] 检查点17: 报告数据与原始结果 JSON 文件一致（可追溯）
- [x] 检查点18: 异常记录含问题定位建议（fd_rebecca 系列 InsertSplits、fa_rebecca 参数数不匹配、person Eltwise 形状不匹配、pd_abigail 输出形状差异）
- [x] 检查点19: 报告归档至 `.agents/docs/retrospective/reports/insight-extraction/external-learning/`

## 质量门（七概念）
- [x] G1: 事实部分无因果推断词，纯客观描述
- [x] G2: 差异分析含现象+证据+建议四元组
- [x] V: 报告数据经对抗审查视角自检（异常加载场景/A-001 状态/环境差异/数据可信性）
