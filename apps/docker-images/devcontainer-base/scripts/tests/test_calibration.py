"""calibration.py 单元测试"""
import os
import sys
import tempfile
import pytest
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SCRIPT_DIR)

from onnx_quantize_kit.calibration import (
    RandomCalibrationReader, FileCalibrationReader,
    NumpyCalibrationReader,
)


class TestRandomCalibrationReader:
    """RandomCalibrationReader 测试"""

    def test_normal_generates_correct_count(self):
        """正常：生成指定数量的样本"""
        reader = RandomCalibrationReader("input", (1, 32), num_samples=10)
        count = 0
        while reader.get_next() is not None:
            count += 1
        assert count == 10

    def test_normal_data_has_correct_shape_dtype_name(self):
        """正常：数据形状、类型、名称正确"""
        reader = RandomCalibrationReader("my_input", (2, 4, 8), num_samples=3)
        sample = reader.get_next()
        assert sample is not None
        assert "my_input" in sample
        arr = sample["my_input"]
        assert arr.shape == (2, 4, 8)
        assert arr.dtype == np.float32

    def test_normal_rewind_resets_index(self):
        """正常：rewind重置迭代器"""
        reader = RandomCalibrationReader("input", (1, 5), num_samples=3)
        # 消费完所有数据
        for _ in range(3):
            reader.get_next()
        assert reader.get_next() is None
        # rewind后重新开始
        reader.rewind()
        assert reader.get_next() is not None

    def test_normal_rewind_multiple_times(self):
        """正常：多次rewind幂等"""
        reader = RandomCalibrationReader("input", (1, 5), num_samples=2)
        reader.get_next()
        reader.rewind()
        reader.get_next()
        reader.get_next()
        assert reader.get_next() is None
        reader.rewind()
        assert reader.get_next() is not None

    def test_boundary_zero_samples(self):
        """边界：num_samples=0"""
        reader = RandomCalibrationReader("input", (1, 5), num_samples=0)
        assert reader.get_next() is None

    def test_boundary_single_sample(self):
        """边界：num_samples=1"""
        reader = RandomCalibrationReader("input", (1, 5), num_samples=1)
        assert reader.get_next() is not None
        assert reader.get_next() is None

    def test_boundary_large_shape(self):
        """边界：大形状"""
        reader = RandomCalibrationReader("input", (1, 1000), num_samples=2)
        s = reader.get_next()
        assert s["input"].shape == (1, 1000)

    def test_empty_name_allowed(self):
        """空值：空字符串input_name（虽然不推荐但不应崩溃）"""
        reader = RandomCalibrationReader("", (1, 5), num_samples=1)
        s = reader.get_next()
        assert "" in s


class TestFileCalibrationReader:
    """FileCalibrationReader 测试"""

    def test_normal_loads_npy_files(self, tmp_path):
        """正常：从目录加载.npy文件"""
        # 创建npy文件
        for i in range(3):
            arr = np.random.randn(1, 10).astype(np.float32)
            np.save(tmp_path / f"sample_{i:03d}.npy", arr)
        reader = FileCalibrationReader("input", (1, 10), str(tmp_path), num_samples=10)
        count = 0
        while reader.get_next() is not None:
            count += 1
        assert count == 3

    def test_normal_data_correct_shape_name(self, tmp_path):
        """正常：加载的数据名称和形状正确"""
        arr = np.random.randn(2, 5).astype(np.float32)
        np.save(tmp_path / "s.npy", arr)
        reader = FileCalibrationReader("x", (2, 5), str(tmp_path))
        s = reader.get_next()
        assert "x" in s
        assert s["x"].dtype == np.float32

    def test_normal_respects_num_samples_limit(self, tmp_path):
        """正常：num_samples限制加载数量"""
        for i in range(10):
            np.save(tmp_path / f"s{i}.npy", np.random.randn(1, 5).astype(np.float32))
        reader = FileCalibrationReader("input", (1, 5), str(tmp_path), num_samples=3)
        count = 0
        while reader.get_next() is not None:
            count += 1
        assert count == 3

    def test_normal_preprocess_fn(self, tmp_path):
        """正常：preprocess_fn被调用"""
        arr = np.ones((1, 5), dtype=np.float32)
        np.save(tmp_path / "s.npy", arr)
        reader = FileCalibrationReader(
            "input", (1, 5), str(tmp_path),
            preprocess_fn=lambda x: x * 2.0
        )
        s = reader.get_next()
        assert np.allclose(s["input"], 2.0)

    def test_normal_rewind(self, tmp_path):
        """正常：rewind"""
        np.save(tmp_path / "s.npy", np.random.randn(1, 5).astype(np.float32))
        reader = FileCalibrationReader("input", (1, 5), str(tmp_path))
        reader.get_next()
        assert reader.get_next() is None
        reader.rewind()
        assert reader.get_next() is not None

    def test_exception_empty_directory(self, tmp_path):
        """异常：空目录抛出FileNotFoundError"""
        with pytest.raises(FileNotFoundError, match="No .npy files"):
            FileCalibrationReader("input", (1, 5), str(tmp_path))

    def test_exception_nonexistent_directory(self):
        """异常：不存在的目录"""
        with pytest.raises(Exception):
            FileCalibrationReader("input", (1, 5), "/nonexistent/dir")

    def test_boundary_sorted_alphabetically(self, tmp_path):
        """正常：文件按字母序加载"""
        np.save(tmp_path / "b.npy", np.array([[1.0]], dtype=np.float32))
        np.save(tmp_path / "a.npy", np.array([[2.0]], dtype=np.float32))
        reader = FileCalibrationReader("input", (1, 1), str(tmp_path))
        first = reader.get_next()["input"]
        second = reader.get_next()["input"]
        # a.npy字母序在前
        assert first[0, 0] == 2.0
        assert second[0, 0] == 1.0


class TestNumpyCalibrationReader:
    """NumpyCalibrationReader 测试（Bug #10验证：公共API可导入）"""

    def test_normal_from_list(self):
        """正常：从numpy数组列表创建"""
        arrays = [np.random.randn(1, 5).astype(np.float32) for _ in range(4)]
        reader = NumpyCalibrationReader("input", arrays)
        count = 0
        while reader.get_next() is not None:
            count += 1
        assert count == 4

    def test_normal_data_correct(self):
        """正常：数据正确转换为float32"""
        arr = np.array([[1.0, 2.0]], dtype=np.float64)  # float64输入
        reader = NumpyCalibrationReader("x", [arr])
        s = reader.get_next()
        assert s["x"].dtype == np.float32

    def test_normal_rewind(self):
        """正常：rewind"""
        reader = NumpyCalibrationReader("input", [np.zeros((1, 3), dtype=np.float32)])
        reader.get_next()
        assert reader.get_next() is None
        reader.rewind()
        assert reader.get_next() is not None

    def test_boundary_empty_iterable(self):
        """边界：空列表"""
        reader = NumpyCalibrationReader("input", [])
        assert reader.get_next() is None

    def test_from_generator(self):
        """正常：从生成器创建"""
        def gen():
            for i in range(3):
                yield np.ones((1, 2), dtype=np.float32) * i
        reader = NumpyCalibrationReader("input", gen())
        s0 = reader.get_next()
        assert np.allclose(s0["input"], 0.0)
