# Checklist

- [x] 已收集 6 个失败模型的 accuracy_logs / 0-accuracy.log / 0-compile.log 证据
- [x] 每个模型记录了退出码（cpp_deploy_static exit 134）或异常堆栈（ValueError / AssertionError）
- [x] `debug/caffe_demo` 根因定位：VTA_TOPI_rmsnorm 未知算子（op_registry 缺失）
- [x] `debug/yolov5ns` / `debug/yolov5ns2` 根因定位：静态推理崩溃 exit 134
- [x] `tests/whisper` 根因定位：watch_ops 映射不匹配 ops=32/32/32/34
- [x] `tests/whisper2` / `tests/whisper2_sim` 根因定位：推理超时挂起
- [x] 已交叉核对基线镜像，判定 6 个模型均非 caffe_pb2 更新回归
- [x] 报告含每个模型的失败现象、证据、根因、影响、处置建议
- [x] 报告已生成于 `external/chaos/xmtools/build/xmnn-failure-models-analysis-report.md`