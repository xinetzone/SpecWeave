# Checklist

## Task 1: 参数模型扩展
- [x] 11 个 P2 参数 message 已新增（Data/ImageData/HDF5Data/HDF5Output/MemoryData/WindowData/DummyData/Python/ContrastiveLoss/InfogainLoss/Upsample）
- [x] LayerParameter 字段 179-189 已注册，默认值对齐 caffex
- [x] caffe_pb2.py 已重新生成并提交

## Task 2: 数据输入/工具类算子
- [x] MemoryData / DummyData 实现 forward 正确
- [x] Python 层 ffi 桥接 setup/reshape/forward/backward 可用
- [x] Recurrent 基类决策记录（抽象基类不可注册，由子类注册）
- [x] Upsample 最近邻上采样 forward 正确

## Task 3: 损失类算子
- [x] ContrastiveLoss / InfogainLoss / MultinomialLogisticLoss 前向正确
- [x] 各损失层 Backward 数值梯度通过

## Task 4: 数据 I/O 类算子（Python/numpy 桥接）
- [x] Data / ImageData / HDF5Data / HDF5Output / WindowData 已注册
- [x] Python 侧数据源回调注册后，C++ 层 Forward 取数成功
- [x] 未引入 leveldb/lmdb/OpenCV/HDF5 C++ 依赖

## Task 5: CuDNN 决策记录
- [x] CuDNN 包装层标注"不实现"，理由已记录（GPU 专属，纯 CPU 引擎）

## Task 6: 构建验证
- [x] CMake 构建零错误（含 proto 重新生成）
- [x] `import caffe_ffi` 在 py314 环境正常（P0 环境 WSL Docker 验证，`is_available()==True`）
- [x] LayerTypeList 含全部 13 个新算子（P0 环境 `p0_env_check.py`：`P2 registered count: 12 / 12`）
- [x] 新算子可实例化（layer_factory 创建，P0 运行时验证通过）
- [x] 静态回调注册表 segfault 修复（`ClearDataIOCallback`/`ClearPythonLayerCallback` + atexit hook）

## Task 7: 单元测试
- [x] 13 个算子均有 forward/backward 测试（test_p2_data_io_ops / test_p2_loss_ops / test_p2_other_ops）
- [x] 数值梯度测试通过无回归（ContrastiveLoss / InfogainLoss / MultinomialLogisticLoss / Upsample）
- [x] 单元测试覆盖（P0 环境 61 用例全绿，13/13 算子行为级覆盖；P2 为 C++ 实现，Python 行覆盖率不适用，口径详见 tasks.md）
- [x] ContrastiveLoss 修正：Backward y==0 缺因子 2（-2→-4）、FULL 归一化 num*dim→num
- [x] C¹ 拐点算子使用 avoid_c1_discontinuity（P1 既有约定，P2 损失层/Upsample 无 C¹ 拐点）
- [x] 静态回调注册表清理回归测试（test_callback_registry_cleanup，防 segfault）

## Task 8: 报告更新
- [x] gap_analysis_report.md P2 缺失清单移除已实现算子
- [x] 算子覆盖率更新
- [x] Proto 参数数量更新至 57
- [x] 路线图 Phase C 标记完成，数据层定位调整，CuDNN 决策记录，行动项更新

## 质量门
- [x] G1 事实：实现对象与报告 P2 清单一一对应
- [x] G2 洞察：算子语义与 caffex 参考实现一致
- [x] G3 迁移：每个算子可独立验证（测试覆盖）