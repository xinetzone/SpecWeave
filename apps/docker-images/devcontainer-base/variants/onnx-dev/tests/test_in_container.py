"""
Integration tests for examples/ and tools/ that require ONNX runtime.
These tests are designed to run INSIDE the devcontainer (where onnx/onnxruntime are installed).
Run with: python -m pytest tests/test_in_container.py -v (inside container)
or via: bash scripts/start-dev.sh -c "python -m pytest tests/ -v"
"""
from __future__ import annotations

import sys

import numpy as np
import pytest

# These imports only work inside the container (where onnx is installed)
onnx = pytest.importorskip("onnx")
ort = pytest.importorskip("onnxruntime")


class TestAddModelFromExamples:
    """Tests for the Add model creation from inference_demo.py."""

    def test_create_add_model_validates(self):
        """create_add_model() should produce a valid ONNX model that passes checker."""
        from inference_demo import create_add_model
        model = create_add_model()
        onnx.checker.check_model(model)

    def test_add_model_inference_correct(self):
        """Add model should produce correct inference results."""
        from inference_demo import create_add_model
        model = create_add_model()
        sess = ort.InferenceSession(model.SerializeToString(), providers=['CPUExecutionProvider'])

        a = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
        b = np.array([[5.0, 6.0], [7.0, 8.0]], dtype=np.float32)
        result = sess.run(None, {'a': a, 'b': b})[0]
        expected = a + b
        np.testing.assert_allclose(result, expected, rtol=1e-6)

    def test_add_model_has_correct_opset(self):
        """Add model should use opset 13 for onnxruntime compatibility."""
        from inference_demo import create_add_model
        model = create_add_model()
        opset_imports = {opset.domain: opset.version for opset in model.opset_import}
        assert opset_imports.get("", 0) <= 13, f"opset should be <=13 for ORT compat, got {opset_imports}"

    def test_add_model_io_shapes(self):
        """Add model should have 2 inputs (a,b) and 1 output (c), all FLOAT."""
        from onnx import TensorProto
        from inference_demo import create_add_model
        model = create_add_model()
        assert len(model.graph.input) == 2
        assert len(model.graph.output) == 1
        input_names = {inp.name for inp in model.graph.input}
        assert input_names == {"a", "b"}
        assert model.graph.output[0].name == "c"


class TestMLPModelFromExamples:
    """Tests for the Mini-MLP model creation from inference_demo.py."""

    def test_create_mlp_model_validates(self):
        """create_simple_linear_model() should produce a valid ONNX model."""
        from inference_demo import create_simple_linear_model
        model = create_simple_linear_model()
        onnx.checker.check_model(model)

    def test_mlp_model_inference_runs(self):
        """MLP model should run inference without errors and produce correct output shape."""
        from inference_demo import create_simple_linear_model
        model = create_simple_linear_model()
        sess = ort.InferenceSession(model.SerializeToString(), providers=['CPUExecutionProvider'])

        input_data = np.random.randn(1, 3, 224, 224).astype(np.float32)
        outputs = sess.run(None, {'input': input_data})
        assert outputs[0].shape == (1, 1000), f"Expected (1,1000), got {outputs[0].shape}"

    def test_mlp_model_deterministic(self):
        """Same model + same input should produce same output (deterministic)."""
        from inference_demo import create_simple_linear_model
        # Use fixed seed for reproducibility
        np.random.seed(42)
        model = create_simple_linear_model()
        sess = ort.InferenceSession(model.SerializeToString(), providers=['CPUExecutionProvider'])
        test_input = np.random.randn(1, 3, 224, 224).astype(np.float32)
        out1 = sess.run(None, {'input': test_input})[0]
        out2 = sess.run(None, {'input': test_input})[0]
        np.testing.assert_array_equal(out1, out2)


class TestFTCompatCheckInContainer:
    """Tests for ft_compat_check.py running inside the FT container."""

    def test_is_free_threading_build_true(self):
        """Inside the onnx-dev container, this should be a free-threading build."""
        from ft_compat_check import is_free_threading_build
        is_ft, gil_enabled = is_free_threading_build()
        assert is_ft is True, "onnx-dev container uses Python 3.14t free-threading build"
        assert gil_enabled is False, "GIL should be disabled by default in FT build"

    def test_core_packages_import(self):
        """Core ONNX packages should all import successfully in container."""
        from ft_compat_check import check_packages
        report = check_packages(
            import_packages=["numpy", "onnx", "onnxruntime", "onnxsim", "onnxscript"],
            expect_absent=[],
        )
        assert report.passed(), f"All core packages should import OK: {[r for r in report.results if r.status != 'ok']}"

    def test_torch_not_present(self):
        """Torch should NOT be present (onnx-dev excludes it)."""
        import importlib.util
        spec = importlib.util.find_spec("torch")
        assert spec is None, "torch should not be installed in onnx-dev variant"

    def test_report_passes_with_defaults(self):
        """Default check_packages should pass in the properly built container."""
        from ft_compat_check import check_packages
        report = check_packages()
        assert report.passed(), f"Default check should pass. Results: {[(r.name, r.status) for r in report.results]}"

    def test_json_output_serializable(self):
        """to_dict() should produce JSON-serializable output."""
        import json
        from ft_compat_check import check_packages
        report = check_packages(import_packages=["numpy"], expect_absent=[])
        d = report.to_dict()
        # Should not raise
        json_str = json.dumps(d, ensure_ascii=False)
        assert "numpy" in json_str


class TestSimpleVerifyScript:
    """Tests for simple_verify.py execution path."""

    def test_add_model_inference_math_correctness(self):
        """Verify the ONNX Add model produces mathematically correct results."""
        from onnx import helper, TensorProto, checker
        import onnxruntime as ort

        X = helper.make_tensor_value_info('X', TensorProto.FLOAT, [None, 3])
        Y = helper.make_tensor_value_info('Y', TensorProto.FLOAT, [None, 3])
        Z = helper.make_tensor_value_info('Z', TensorProto.FLOAT, [None, 3])
        node_def = helper.make_node('Add', inputs=['X', 'Y'], outputs=['Z'])
        graph_def = helper.make_graph([node_def], 'add_model', [X, Y], [Z])
        model_def = helper.make_model(
            graph_def,
            producer_name='test',
            opset_imports=[helper.make_opsetid('', 13)]
        )
        checker.check_model(model_def)

        sess = ort.InferenceSession(model_def.SerializeToString())
        x = np.array([[1.0, 2.0, 3.0]], dtype=np.float32)
        y = np.array([[4.0, 5.0, 6.0]], dtype=np.float32)
        z = sess.run(None, {'X': x, 'Y': y})[0]
        expected = np.array([[5.0, 7.0, 9.0]], dtype=np.float32)
        np.testing.assert_allclose(z, expected)
