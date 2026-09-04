# Tasks

- [x] Task 1: 收集 6 个失败模型的证据链
  - [x] SubTask 1.1: 从 `xmnn:1.2.1-new` 容器提取 `build/accuracy_logs/*.log` 中 6 个模型的运行日志
  - [x] SubTask 1.2: 提取各模型 `temp/<model>/accuracy/0-accuracy.log` 与 `compile/0-compile.log`
  - [x] SubTask 1.3: 记录每个模型的退出码（如 cpp_deploy_static exit 134）与堆栈（如 ValueError / AssertionError）
- [x] Task 2: 按失败模式分类并定位根因
  - [x] SubTask 2.1: `debug/caffe_demo` — 定位 `VTA_TOPI_rmsnorm` 未知算子错误（op_registry 缺失）
  - [x] SubTask 2.2: `debug/yolov5ns` / `debug/yolov5ns2` — 确认 `cpp_deploy_static` exit 134 (SIGABRT) 静态推理崩溃
  - [x] SubTask 2.3: `tests/whisper` — 确认 watch_ops 映射 `AssertionError: ops=32/32/32/34`
  - [x] SubTask 2.4: `tests/whisper2` / `tests/whisper2_sim` — 确认推理长时间无响应（>75min 挂起）
- [x] Task 3: 判定是否为 caffe_pb2 更新回归
  - [x] SubTask 3.1: 交叉核对基线镜像 `xmnn:1.2.1-alpha` 中相同模型的失败行为
  - [x] SubTask 3.2: 输出每个模型"是否新 wheel 引入回归"的明确判定
- [x] Task 4: 生成结构化失败原因分析报告
  - [x] SubTask 4.1: 撰写 `xmnn-failure-models-analysis-report.md`
  - [x] SubTask 4.2: 含每个模型的失败现象、证据、根因、影响、处置建议
  - [x] SubTask 4.3: 汇总各类失败模式清单与后续行动计划

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 1]
- [Task 4] depends on [Task 1],[Task 2],[Task 3]