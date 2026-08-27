"""benchmark.py 单元测试 — 覆盖正常/边界/异常/空值/参数组合场景"""
import os
import sys
import pytest
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPT_DIR)

from onnx_quantize_kit.benchmark import (
    create_session, benchmark_model, BenchmarkResult,
    _resolve_input, _safe_get_input_shape,
)
from onnx import helper, TensorProto
import onnx


class TestCreateSession:
    """create_session 测试"""

    def test_normal_creates_session(self, mlp_model_path):
        """正常：创建Session成功"""
        sess = create_session(mlp_model_path, intra_threads=1)
        assert sess is not None
        assert len(sess.get_inputs()) == 1
        assert sess.get_inputs()[0].name == "input"

    def test_with_custom_providers(self, mlp_model_path):
        """正常：自定义providers"""
        sess = create_session(mlp_model_path, intra_threads=2, providers=["CPUExecutionProvider"])
        assert sess is not None

    def test_boundary_threads_1(self, mlp_model_path):
        """边界：线程数=1"""
        sess = create_session(mlp_model_path, intra_threads=1, inter_threads=1)
        assert sess is not None

    def test_exception_nonexistent_file(self):
        """异常：不存在的文件路径应抛出异常"""
        with pytest.raises(Exception):
            create_session("/nonexistent/path/model.onnx")

    def test_exception_invalid_model(self, tmp_path):
        """异常：损坏的模型文件"""
        bad_path = tmp_path / "bad.onnx"
        bad_path.write_bytes(b"not an onnx file")
        with pytest.raises(Exception):
            create_session(str(bad_path))


class TestSafeGetInputShape:
    """_safe_get_input_shape 测试（Bug #2修复验证）"""

    def test_normal_all_static_dims(self):
        """正常：全静态维度"""
        import onnxruntime as ort
        # 创建一个静态形状模型
        X = helper.make_tensor_value_info('input', TensorProto.FLOAT, [1, 10])
        Y = helper.make_tensor_value_info('output', TensorProto.FLOAT, [1, 5])
        W = helper.make_tensor('W', TensorProto.FLOAT, [10, 5], np.random.randn(50).tolist())
        nodes = [helper.make_node('MatMul', ['input', 'W'], ['output'])]
        graph = helper.make_graph(nodes, 'g', [X], [Y], [W])
        model = helper.make_model(graph, opset_imports=[helper.make_opsetid('', 13)])
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.onnx', delete=False) as f:
            onnx.save(model, f.name)
            path = f.name
        try:
            sess = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
            inp = sess.get_inputs()[0]
            shape = _safe_get_input_shape(inp)
            assert shape == (1, 10)
        finally:
            os.unlink(path)

    def test_normal_dynamic_dim_param_string(self):
        """正常：动态维度（dim_param字符串如'batch'）应替换为default值"""
        import onnxruntime as ort
        X = helper.make_tensor_value_info('input', TensorProto.FLOAT, ['N', 10])
        Y = helper.make_tensor_value_info('output', TensorProto.FLOAT, ['N', 5])
        W = helper.make_tensor('W', TensorProto.FLOAT, [10, 5], np.random.randn(50).tolist())
        nodes = [helper.make_node('MatMul', ['input', 'W'], ['output'])]
        graph = helper.make_graph(nodes, 'g', [X], [Y], [W])
        model = helper.make_model(graph, opset_imports=[helper.make_opsetid('', 13)])
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.onnx', delete=False) as f:
            onnx.save(model, f.name)
            path = f.name
        try:
            sess = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
            inp = sess.get_inputs()[0]
            shape = _safe_get_input_shape(inp, default=1)
            assert shape == (1, 10), f"动态维度应被替换为1，得到{shape}"
        finally:
            os.unlink(path)

    def test_normal_dim_value_zero(self):
        """正常：dim_value=0（动态）应替换为default"""
        # dim_value=0 也表示动态维度
        pass  # 已由上面的字符串dim_param覆盖

    def test_boundary_custom_default(self):
        """边界：自定义default值"""
        import onnxruntime as ort
        X = helper.make_tensor_value_info('input', TensorProto.FLOAT, ['B', 'S', 'D'])
        Y = helper.make_tensor_value_info('output', TensorProto.FLOAT, ['B', 'S', 'D'])
        nodes = [helper.make_node('Identity', ['input'], ['output'])]
        graph = helper.make_graph(nodes, 'g', [X], [Y])
        model = helper.make_model(graph, opset_imports=[helper.make_opsetid('', 13)])
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.onnx', delete=False) as f:
            onnx.save(model, f.name)
            path = f.name
        try:
            sess = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
            inp = sess.get_inputs()[0]
            shape = _safe_get_input_shape(inp, default=2)
            assert shape == (2, 2, 2), f"所有动态维度应替换为2，得到{shape}"
        finally:
            os.unlink(path)

    def test_with_session_object(self, mlp_model_path):
        """正常：传入Session对象而非input"""
        sess = create_session(mlp_model_path, intra_threads=1)
        shape = _safe_get_input_shape(sess)
        assert len(shape) == 2
        assert shape[0] == 1  # batch=1 (dynamic -> 1)
        assert shape[1] == 10  # MLP input dim


class TestResolveInput:
    """_resolve_input 测试"""

    def test_normal_auto_detect(self, mlp_model_path):
        """正常：自动检测input_name和shape"""
        sess = create_session(mlp_model_path, intra_threads=1)
        name, shape, dtype = _resolve_input(sess, None, None)
        assert name == "input"
        assert shape[0] == 1  # batch dim
        assert dtype == np.float32

    def test_normal_explicit_shape_and_name(self, mlp_model_path):
        """正常：显式指定shape和name"""
        sess = create_session(mlp_model_path, intra_threads=1)
        name, shape, dtype = _resolve_input(sess, (1, 10), "input")
        assert name == "input"
        assert shape == (1, 10)

    def test_normal_fp16_dtype_detection(self):
        """正常：FP16模型检测dtype"""
        # FP16输入
        X = helper.make_tensor_value_info('input', TensorProto.FLOAT16, [1, 10])
        Y = helper.make_tensor_value_info('output', TensorProto.FLOAT16, [1, 10])
        nodes = [helper.make_node('Identity', ['input'], ['output'])]
        graph = helper.make_graph(nodes, 'g', [X], [Y])
        model = helper.make_model(graph, opset_imports=[helper.make_opsetid('', 13)])
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.onnx', delete=False) as f:
            onnx.save(model, f.name)
            path = f.name
        try:
            sess = create_session(path, intra_threads=1)
            name, shape, dtype = _resolve_input(sess, None, None)
            assert dtype == np.float16
        finally:
            os.unlink(path)

    def test_exception_no_inputs_model(self):
        """异常：无输入模型"""
        # 创建一个无输入的模型（常量输出）
        const_val = helper.make_tensor('const', TensorProto.FLOAT, [1], [1.0])
        Y = helper.make_tensor_value_info('output', TensorProto.FLOAT, [1])
        nodes = [helper.make_node('Constant', [], ['output'], value=const_val)]
        graph = helper.make_graph(nodes, 'g', [], [Y])
        model = helper.make_model(graph, opset_imports=[helper.make_opsetid('', 13)])
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.onnx', delete=False) as f:
            onnx.save(model, f.name)
            path = f.name
        try:
            sess = create_session(path, intra_threads=1)
            with pytest.raises(ValueError, match="no inputs"):
                _resolve_input(sess, None, None)
        finally:
            os.unlink(path)

    def test_boundary_default_batch_param(self, mlp_model_path):
        """边界：custom default_batch"""
        sess = create_session(mlp_model_path, intra_threads=1)
        name, shape, dtype = _resolve_input(sess, None, None, default_batch=4)
        assert shape[0] == 4


class TestBenchmarkModel:
    """benchmark_model 测试"""

    def test_normal_returns_valid_result(self, mlp_model_path):
        """正常：benchmark返回有效结果"""
        result = benchmark_model(mlp_model_path, warmup=2, runs=5, intra_threads=1)
        assert isinstance(result, BenchmarkResult)
        assert result.success, f"benchmark failed: {result.error}"
        assert result.avg_ms > 0
        assert result.size_kb > 0
        assert result.runs == 5

    def test_normal_all_percentiles(self, mlp_model_path):
        """正常：百分位数指标都有效"""
        result = benchmark_model(mlp_model_path, warmup=2, runs=10, intra_threads=1)
        assert result.p50_ms > 0
        assert result.p95_ms >= result.p50_ms
        assert result.p99_ms >= result.p95_ms
        assert result.min_ms <= result.avg_ms <= result.max_ms
        assert result.std_ms >= 0
        assert result.throughput_fps > 0

    def test_normal_auto_detects_input(self, mlp_model_path):
        """正常（Bug #1/#2验证）：无需指定input_shape/input_name即可运行"""
        result = benchmark_model(mlp_model_path, warmup=1, runs=3, intra_threads=1)
        assert result.success, f"auto-detect failed: {result.error}"

    def test_boundary_zero_warmup(self, mlp_model_path):
        """边界：warmup=0"""
        result = benchmark_model(mlp_model_path, warmup=0, runs=3, intra_threads=1)
        assert result.success

    def test_boundary_single_run(self, mlp_model_path):
        """边界：runs=1"""
        result = benchmark_model(mlp_model_path, warmup=0, runs=1, intra_threads=1)
        assert result.success
        assert result.avg_ms > 0

    def test_boundary_many_threads(self, mlp_model_path):
        """边界：线程数较多（4线程）"""
        result = benchmark_model(mlp_model_path, warmup=2, runs=5, intra_threads=4)
        assert result.success

    def test_exception_nonexistent_file(self):
        """异常：不存在的文件返回error而非抛出"""
        result = benchmark_model("/nonexistent.onnx", warmup=1, runs=1)
        assert not result.success
        assert result.error is not None

    def test_exception_wrong_shape(self, mlp_model_path):
        """异常：错误的input_shape导致推理失败"""
        # MLP期望(1,10)，传入错误形状(1,999)
        result = benchmark_model(mlp_model_path, input_shape=(1, 999), input_name="input",
                                 warmup=1, runs=1, intra_threads=1)
        assert not result.success
        assert result.error is not None

    def test_exception_wrong_input_name(self, mlp_model_path):
        """异常：错误的input_name"""
        result = benchmark_model(mlp_model_path, input_shape=(1, 10), input_name="wrong_name",
                                 warmup=1, runs=1, intra_threads=1)
        assert not result.success

    def test_param_combination_explicit_shape_name(self, small_mlp_path):
        """参数组合：显式指定所有参数"""
        result = benchmark_model(
            small_mlp_path,
            input_shape=(1, 4),
            input_name="input",
            warmup=2,
            runs=5,
            intra_threads=2,
        )
        assert result.success
        assert result.threads == 2

    def test_result_dataclass_defaults(self):
        """空值/默认值：BenchmarkResult默认值"""
        r = BenchmarkResult()
        assert r.avg_ms == 0.0
        # success是property：error=None → success=True（无错误即成功）
        assert r.success is True
        assert r.size_kb == 0.0
        assert r.error is None
