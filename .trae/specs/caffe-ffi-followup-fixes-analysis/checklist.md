# caffe-ffi 后续修复与分析 - Verification Checklist

## RQ-1: 标准 norm_param 协议支持
- [x] 检查点1: 已核查 caffe-ffi proto 与 BVLC/caffex 的字段差异（l2_norm_param=158 vs norm_param=149）
- [x] 检查点2: `caffe.proto` 已更新，标准 `norm_param` 可被解析
- [x] 检查点3: 含 `norm_param { ... }` 的 prototxt 解析成功、参数可读、无报错
- [x] 检查点4: 既有 `l2_norm_param`（158）向后兼容，行为不变
- [x] 检查点5: `caffe_pb2.py` 已基于更新后的 proto 重新生成

## RQ-2: A-001 read_net 权重加载修复
- [x] 检查点6: 已定位 `read_net` → `_merge_weights` → `NewNetFromProtoString` 链路根因
- [x] 检查点7: 修复方案文档化（含权重写入与形状校验）
- [ ] 检查点8: 用预训练 caffemodel 推理，conv1 权重为真实值（非全 1.0/std=0）— ⚠️ 需容器重编译 native 后运行验证
- [ ] 检查点9: 网络级输出无 Inf/NaN，与 caffex 结果对齐（精度容差内）— ⚠️ 需容器重编译 native 后运行验证

## RQ-3: 性能瓶颈分析
- [x] 检查点10: 已基于 bench JSON 计算每算子比值/绝对延迟/FPS 差距/std
- [x] 检查点11: 瓶颈按严重程度（比值 × 绝对延迟）排序，标注最严重瓶颈
- [x] 检查点12: 高方差算子（长尾）已识别并分析
- [x] 检查点13: 瓶颈分析报告产出，含优化建议

## RQ-4: Top-K CSV 导出
- [x] 检查点14: `topk_comparison.csv` 已生成，字段完整（impl/model/output_shape/top1/top5/probs_top5/has_nan/has_inf/score_max/ok）
- [x] 检查点15: CSV 数据与 topk JSON 一致，可被 pandas/Excel 打开

## 质量门（七概念）
- [x] G2: 性能瓶颈分析含现象 + 数据证据 + 优化建议（四元组）
- [x] V: A-001 修复方案经对抗审查视角自检（边界/形状校验/向后兼容）

## RQ-2b: 容器内 A-001 编译+验证脚本
- [x] 检查点16: 脚本已生成，位于 spec 目录，可在 `caffe-ffi-jupyter` 容器内一键执行
- [x] 检查点17: 脚本覆盖 env 装载 + 本地 tvm-ffi 定位 + `pip install -e . --no-build-isolation` 重编译
- [x] 检查点18: 脚本运行 `a001_verify_fix.py` 完成 conv1 权重/无 NaN/caffex 对齐验证
- [x] 检查点19: 脚本幂等可重入、失败有明确退出码

## RQ-3b: eltwise_sum / pooling OpenMP 优化示例
- [x] 检查点20: 已给出 eltwise_sum 的 OpenMP 并行代码示例（输出块切分，无数据竞争）
- [x] 检查点21: 已给出 pooling 的 OpenMP 并行代码示例（batch×通道 collapse 并行）
- [x] 检查点22: 示例含预分配缓冲复用、`CAFFE_FFI_ENABLE_OPENMP` 构建配置与线程数控制说明

## RQ-1b: norm_param 字段编号差异解释
- [x] 检查点23: 解释含 caffe-ffi 用 190 / BVLC 用 149 的编号设计逻辑
- [x] 检查点24: 分析文本 prototxt 与二进制 caffemodel 的兼容性差异
- [x] 检查点25: 给出二进制兼容性结论与规避建议

## 质量门（续）
- [x] V2: OpenMP 优化示例经对抗审查（并行维度/数据竞争/向下兼容 OpenMP 选项）
- [x] G4: 三项产出物行动项原子化、可独立验证