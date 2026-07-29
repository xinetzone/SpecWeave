# Caffe Normalize→RMSNorm 代码优化 - Verification Checklist

## 代码优化检查
- [x] 消除了 `_normalize_rmsnorm_params` 和 `_normalize_rmsnorm_plan` 的重复调用
- [x] 原有辅助函数 `_normalize_rmsnorm_params`、`_normalize_rmsnorm_plan`、`_should_convert_normalize_to_rmsnorm` 保持向后兼容
- [x] 长三元表达式被拆分为命名中间变量（needs_transpose, rms_input_expr, needs_inverse），可读性提升
- [x] 关键转换步骤有清晰注释，解释重参数化数学原理与 axis 转置策略
- [x] 增加了防御性校验（`if rms_weight is not None`），参数无效时安全回退到 L2 normalize 路径
- [x] 代码风格与 caffe.py 现有风格一致（英文 docstring、4空格缩进、空行规范）

## 单元测试检查
- [x] 新增端到端数值等价性测试，覆盖多种 shape（1D/2D/3D/4D/5D）— test_rms_norm_numerical.py 共 970 个测试用例
- [x] 测试覆盖不同 axis 配置（正索引、负索引）
- [x] 测试覆盖不同 eps 值范围（1e-10 到 1e-2）
- [x] 测试覆盖 across_spatial=True/False 两种模式（多轴返回 None）
- [x] 测试覆盖 channel_shared=True/False 两种缩放模式
- [x] across_spatial=True（多轴归一化）场景验证不使用 RMSNorm（返回 None）
- [x] 所有测试用例 max_abs_diff ≈ 4.8e-7，远低于 1e-5 阈值（float32 精度）
- [x] 测试无需 NPU 硬件即可运行（纯 NumPy + monkeypatch stub）

## 回归测试检查
- [x] test_caffe_normalize_rmsnorm.py 中所有现有测试全部通过
- [x] 原有 `_should_convert_normalize_to_rmsnorm` 行为不变（op 在 model_outputs 中返回 False）
- [x] 单轴归一化场景仍能正确转换为 RMSNorm
- [x] 多轴归一化场景仍走原有 L2 normalize 路径
- [x] scale 参数处理逻辑（channel_shared、单值广播、多值校验）行为不变

## 功能等价性检查
- [x] 相同输入下，RMSNorm 转换路径与 L2 normalize 路径输出数值一致（max_abs_diff ≤ 4.8e-7）
- [x] axis 转置后结果正确恢复到原始维度顺序（transpose_roundtrip 测试通过）
- [x] 边界情况（dim=1、负 axis 索引、空 axis）处理正确
- [x] 新增 5 个 CI 单元测试覆盖 _try_prepare_rmsnorm_conversion 的各种场景

## 修改文件清单
1. **caffe.py** (d:\spaces\SpecWeave\external\xmhub\npu_tvm\python\tvm\relay\frontend\caffe.py):
   - 新增 `_try_prepare_rmsnorm_conversion` 函数（第90-104行）
   - 优化 `convert_normalize` 中 RMSNorm 转换分支（第566-580行）
2. **test_caffe_normalize_rmsnorm.py** (d:\spaces\SpecWeave\external\xmhub\npu_tvm\tests\python\ci\test_caffe_normalize_rmsnorm.py):
   - 新增 5 个测试函数（第157-255行）
3. **test_rms_norm_numerical.py** (d:\spaces\SpecWeave\apps\tests\test_rms_norm_numerical.py):
   - 新增纯 NumPy 数值等价性验证测试
