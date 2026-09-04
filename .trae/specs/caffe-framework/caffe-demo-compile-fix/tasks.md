# Caffe Demo 模型编译修复 - Implementation Plan

## [x] Task 1: 根因分析：确认 shape 不匹配导致 VTA split error
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 对比 config.toml 的 shape [1,3,120,120] 与 prototxt 的 input_dim: 32
  - 分析 120×120 输入经 conv1+pool 后产生 29×29 特征图，超出 VTA tile 约束
  - 验证 32×32 输入产生 7×7 特征图，在约束范围内
- **Acceptance Criteria Addressed**: AC-1, AC-4
- **Test Requirements**:
  - `programmatic` TR-1.1: 120×120 输入复现 split error，vta_config.bin 不生成
  - `programmatic` TR-1.2: 32×32 输入编译通过，vta_config.bin 生成
- **Notes**: caffe_demo_old 的 prototxt 是 120×120，config 复制时未更新

## [x] Task 2: 修复 config.toml 的输入 shape
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 将 `external/chaos/models/debug/caffe_demo/config.toml` 第 8 行
  - 从 `shape = [ 1, 3, 120, 120,]` 改为 `shape = [ 1, 3, 32, 32,]`
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-2.1: config.toml 中 shape 值为 [1,3,32,32]
  - `programmatic` TR-2.2: prototxt 中 input_dim 为 32，两者一致
- **Notes**: 仅修改 1 行，不触碰其他配置

## [x] Task 3: 干净编译验证
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 清除 temp/debug/caffe_demo 目录
  - 执行 compile.py -n debug/caffe_demo
  - 确认 6 步全部通过
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-3.1: compile.py 退出码为 0
  - `programmatic` TR-3.2: 日志包含"模型编译全部完成"
  - `programmatic` TR-3.3: vta_config.bin 存在且非空（8480 bytes）
  - `programmatic` TR-3.4: runtime_bandwidth_first.log 无 error/fail/split
  - `programmatic` TR-3.5: 所有产物文件存在（network.xmnn, param.bin, vta_data.bin, caffe_demo.bin）
- **Notes**: 实际编译耗时约 7.92 秒
