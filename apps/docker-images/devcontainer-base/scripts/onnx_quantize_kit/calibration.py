"""校准数据Reader实现"""
import os
from pathlib import Path
from typing import Callable, Iterable, Optional

import numpy as np
from onnxruntime.quantization import CalibrationDataReader


class RandomCalibrationReader(CalibrationDataReader):
    """随机数据校准Reader（用于流程验证，生产环境请用真实数据）"""

    def __init__(self, input_name: str, input_shape: tuple, num_samples: int = 100):
        self.input_name = input_name
        self.input_shape = input_shape
        self.num_samples = num_samples
        self.idx = 0
        self._generate()

    def _generate(self):
        self.data = [
            {self.input_name: np.random.randn(*self.input_shape).astype(np.float32)}
            for _ in range(self.num_samples)
        ]

    def get_next(self) -> Optional[dict]:
        if self.idx >= len(self.data):
            return None
        d = self.data[self.idx]
        self.idx += 1
        return d

    def rewind(self):
        self.idx = 0


class FileCalibrationReader(CalibrationDataReader):
    """从.npy文件目录加载校准数据"""

    def __init__(self, input_name: str, input_shape: tuple,
                 calib_dir: str, num_samples: int = 100,
                 preprocess_fn: Optional[Callable] = None):
        self.input_name = input_name
        self.input_shape = input_shape
        self.num_samples = num_samples
        self.preprocess_fn = preprocess_fn
        self.idx = 0
        self.data = []
        self._load(calib_dir)

    def _load(self, calib_dir: str):
        npy_files = sorted(Path(calib_dir).glob("*.npy"))[:self.num_samples]
        for f in npy_files:
            arr = np.load(str(f)).astype(np.float32)
            if self.preprocess_fn:
                arr = self.preprocess_fn(arr)
            self.data.append({self.input_name: arr})
        if not self.data:
            raise FileNotFoundError(
                f"No .npy files found in {calib_dir}. "
                f"Place calibration data as .npy files in this directory."
            )

    def get_next(self) -> Optional[dict]:
        if self.idx >= len(self.data):
            return None
        d = self.data[self.idx]
        self.idx += 1
        return d

    def rewind(self):
        self.idx = 0


class NumpyCalibrationReader(CalibrationDataReader):
    """从numpy数组列表或迭代器加载校准数据"""

    def __init__(self, input_name: str, data_iter: Iterable[np.ndarray]):
        self.input_name = input_name
        self.data = [{input_name: arr.astype(np.float32)} for arr in data_iter]
        self.idx = 0

    def get_next(self) -> Optional[dict]:
        if self.idx >= len(self.data):
            return None
        d = self.data[self.idx]
        self.idx += 1
        return d

    def rewind(self):
        self.idx = 0


CalibrationReader = CalibrationDataReader  # 别名，方便导入
