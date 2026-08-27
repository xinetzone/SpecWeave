"""model_detect.py 单元测试"""
import os
import sys
import pytest
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPT_DIR)

from onnx_quantize_kit.model_detect import (
    detect_model_type, get_recommended_quant_config,
    analyze_model, ModelType,
)


class TestModelTypeEnum:
    """ModelType 枚举测试"""

    def test_enum_values(self):
        """正常：枚举值正确"""
        assert ModelType.MLP.value == "mlp"
        assert ModelType.CNN.value == "cnn"
        assert ModelType.TRANSFORMER.value == "transformer"
        assert ModelType.RNN.value == "rnn"
        assert ModelType.UNKNOWN.value == "unknown"


class TestDetectModelType:
    """detect_model_type 测试"""

    def test_detect_mlp(self, mlp_model_path):
        """正常：MLP模型检测"""
        mtype = detect_model_type(mlp_model_path)
        assert mtype == ModelType.MLP

    def test_detect_cnn(self, cnn_model_path):
        """正常：CNN模型检测"""
        mtype = detect_model_type(cnn_model_path)
        assert mtype == ModelType.CNN

    def test_detect_from_model_proto(self, mlp_model_path):
        """正常：传入ModelProto对象而非路径"""
        import onnx
        model = onnx.load(mlp_model_path, load_external_data=False)
        mtype = detect_model_type(model)
        assert mtype == ModelType.MLP

    def test_verbose_mode(self, mlp_model_path, capsys):
        """正常：verbose=True打印信息"""
        detect_model_type(mlp_model_path, verbose=True)
        captured = capsys.readouterr()
        assert "Op distribution" in captured.out or "Transformer score" in captured.out

    def test_unknown_model_no_matmul_no_conv(self):
        """边界：不含典型算子的模型返回UNKNOWN"""
        import tempfile
        from onnx import helper, TensorProto
        # 创建一个只有Identity的模型
        X = helper.make_tensor_value_info('input', TensorProto.FLOAT, [1, 5])
        Y = helper.make_tensor_value_info('output', TensorProto.FLOAT, [1, 5])
        nodes = [helper.make_node('Identity', ['input'], ['output'])]
        graph = helper.make_graph(nodes, 'g', [X], [Y])
        model = helper.make_model(graph, opset_imports=[helper.make_opsetid('', 13)])
        mtype = detect_model_type(model)
        # Identity alone -> no MatMul/Gemm/Conv -> UNKNOWN
        assert mtype == ModelType.UNKNOWN


class TestGetRecommendedQuantConfig:
    """get_recommended_quant_config 测试"""

    @pytest.mark.parametrize("mtype,expected_strategy", [
        (ModelType.MLP, "static_qoperator"),
        (ModelType.CNN, "static_qdq"),
        (ModelType.TRANSFORMER, "dynamic"),
        (ModelType.RNN, "dynamic"),
        (ModelType.UNKNOWN, "static_qdq"),
    ])
    def test_recommended_strategy_per_type(self, mtype, expected_strategy):
        """参数组合：各模型类型推荐策略正确"""
        cfg = get_recommended_quant_config(mtype)
        assert cfg["strategy"] == expected_strategy

    def test_mlp_has_fallback(self):
        """正常：MLP有fallback策略"""
        cfg = get_recommended_quant_config(ModelType.MLP)
        assert "fallback" in cfg
        assert cfg["fallback"] == "dynamic"

    def test_cnn_config_has_qdq(self):
        """正常：CNN推荐QDQ格式"""
        cfg = get_recommended_quant_config(ModelType.CNN)
        assert cfg["quant_format"] == "QDQ"
        assert cfg["per_channel"] is True

    def test_transformer_config_simple(self):
        """正常：Transformer配置较简单（动态量化）"""
        cfg = get_recommended_quant_config(ModelType.TRANSFORMER)
        assert cfg["strategy"] == "dynamic"
        assert cfg["fallback"] == "fp16"

    def test_unknown_has_default_config(self):
        """边界：UNKNOWN类型有默认配置"""
        cfg = get_recommended_quant_config(ModelType.UNKNOWN)
        assert "strategy" in cfg
        assert "fallback" in cfg

    def test_invalid_type_returns_unknown_config(self):
        """异常防御：非法ModelType值返回UNKNOWN配置（不应崩溃）"""
        # 注意：传入非ModelType对象会KeyError，但函数用get兜底
        cfg = get_recommended_quant_config("not_a_type")
        # get返回默认值（UNKNOWN的config）
        assert cfg["strategy"] == "static_qdq"


class TestAnalyzeModel:
    """analyze_model 测试"""

    def test_normal_returns_dict(self, mlp_model_path):
        """正常：返回包含所有必要字段的dict"""
        result = analyze_model(mlp_model_path, intra_threads=1)
        assert isinstance(result, dict)
        required_fields = [
            "model_path", "model_name", "file_size_kb", "opset_version",
            "model_type", "recommended_strategy", "fallback_chain",
            "strategy_chain", "input_name", "input_shape",
            "num_inputs", "num_outputs", "num_nodes",
        ]
        for f in required_fields:
            assert f in result, f"missing field: {f}"

    def test_normal_model_type_correct(self, mlp_model_path):
        """正常：model_type正确"""
        result = analyze_model(mlp_model_path)
        assert result["model_type"] == "mlp"

    def test_normal_cnn_type_correct(self, cnn_model_path):
        """正常：CNN模型类型正确"""
        result = analyze_model(cnn_model_path)
        assert result["model_type"] == "cnn"

    def test_normal_input_info(self, mlp_model_path):
        """正常：输入信息正确"""
        result = analyze_model(mlp_model_path)
        assert result["input_name"] == "input"
        assert isinstance(result["input_shape"], tuple)
        assert len(result["input_shape"]) == 2

    def test_normal_file_size_positive(self, mlp_model_path):
        """正常：文件大小>0"""
        result = analyze_model(mlp_model_path)
        assert result["file_size_kb"] > 0

    def test_normal_strategy_chain_contains_primary(self, mlp_model_path):
        """正常：策略链包含主策略"""
        result = analyze_model(mlp_model_path)
        assert result["recommended_strategy"] in result["strategy_chain"]

    def test_normal_counts_positive(self, mlp_model_path):
        """正常：节点数>0"""
        result = analyze_model(mlp_model_path)
        assert result["num_nodes"] > 0
        assert result["num_inputs"] == 1
        assert result["num_outputs"] == 1

    def test_exception_file_not_found(self):
        """异常：文件不存在"""
        with pytest.raises(FileNotFoundError):
            analyze_model("/nonexistent/model.onnx")

    def test_boundary_small_model(self, small_mlp_path):
        """边界：极小模型"""
        result = analyze_model(small_mlp_path)
        assert result["model_type"] in ("mlp", "unknown")
        assert result["num_nodes"] > 0
