"""精度验证模块"""
from dataclasses import dataclass
from typing import Optional

import numpy as np
import onnxruntime as ort

from .benchmark import create_session, _resolve_input


@dataclass
class AccuracyThresholds:
    """精度验证阈值配置

    基于4类模型实测数据设定的分级阈值：
    - max_diff < excellent_max_diff: 🟢 优秀
    - max_diff < acceptable_max_diff: 🟡 可接受
    - max_diff >= acceptable_max_diff: 🔴 不可接受，需回滚
    """
    excellent_max_diff: float = 0.01
    acceptable_max_diff: float = 0.05
    min_cosine_sim: float = 0.99
    min_speedup: float = 1.0  # speedup低于此值认为量化无性能收益

    @classmethod
    def strict(cls):
        """严格阈值（精度敏感任务：分类top-1、回归）"""
        return cls(excellent_max_diff=0.005, acceptable_max_diff=0.02,
                   min_cosine_sim=0.999, min_speedup=1.0)

    @classmethod
    def relaxed(cls):
        """宽松阈值（生成任务、特征提取）"""
        return cls(excellent_max_diff=0.05, acceptable_max_diff=0.1,
                   min_cosine_sim=0.95, min_speedup=0.9)


@dataclass
class AccuracyResult:
    """精度验证结果"""
    max_diff: float = 0.0
    mean_diff: float = 0.0
    p95_diff: float = 0.0
    p99_diff: float = 0.0
    cosine_sim_mean: float = 1.0
    cosine_sim_min: float = 1.0
    num_samples: int = 0
    passed: bool = True
    level: str = "excellent"  # excellent / acceptable / unacceptable
    fail_reason: Optional[str] = None

    def to_danger_dict(self) -> dict:
        """返回问题诊断摘要"""
        return {
            "level": self.level,
            "passed": self.passed,
            "max_diff": self.max_diff,
            "cosine_sim_min": self.cosine_sim_min,
            "fail_reason": self.fail_reason,
        }


def validate_accuracy(fp32_path: str, quant_path: str,
                      input_shape: Optional[tuple] = None,
                      input_name: Optional[str] = None,
                      num_samples: int = 50,
                      thresholds: Optional[AccuracyThresholds] = None,
                      intra_threads: int = 4,
                      speedup: Optional[float] = None) -> AccuracyResult:
    """验证量化模型精度

    Args:
        fp32_path: FP32基准模型路径
        quant_path: 量化模型路径
        input_shape: 输入形状，None则自动检测
        input_name: 输入节点名，None则自动检测
        num_samples: 测试样本数
        thresholds: 精度阈值，None使用默认值
        intra_threads: 推理线程数
        speedup: 已测得的加速比（用于判断性能收益）

    Returns:
        AccuracyResult包含详细精度指标和通过/失败判定
    """
    if thresholds is None:
        thresholds = AccuracyThresholds()

    result = AccuracyResult(num_samples=num_samples)

    try:
        sess_fp32 = create_session(fp32_path, intra_threads)
        sess_quant = create_session(quant_path, intra_threads)

        name32, shape32, _ = _resolve_input(sess_fp32, input_shape, input_name)
        nameq, shapeq, dtype_q = _resolve_input(sess_quant, input_shape, input_name)
        shape = shape32

        max_diffs = []
        mean_diffs = []
        cos_sims = []

        for _ in range(num_samples):
            x32 = np.random.randn(*shape).astype(np.float32)
            o32 = sess_fp32.run(None, {name32: x32})[0].astype(np.float32)

            xq = x32.astype(dtype_q) if np.issubdtype(dtype_q, np.floating) else x32
            oq = sess_quant.run(None, {nameq: xq})[0].astype(np.float32)

            diff = np.abs(o32 - oq)
            max_diffs.append(float(np.max(diff)))
            mean_diffs.append(float(np.mean(diff)))

            fp32_flat = o32.flatten()
            q_flat = oq.flatten()
            cos_sim = float(np.dot(fp32_flat, q_flat) /
                            (np.linalg.norm(fp32_flat) * np.linalg.norm(q_flat) + 1e-10))
            cos_sims.append(cos_sim)

        result.max_diff = float(np.max(max_diffs))
        result.mean_diff = float(np.mean(mean_diffs))
        result.p95_diff = float(np.percentile(max_diffs, 95))
        result.p99_diff = float(np.percentile(max_diffs, 99))
        result.cosine_sim_mean = float(np.mean(cos_sims))
        result.cosine_sim_min = float(np.min(cos_sims))

        # 判定精度等级
        reasons = []
        if result.max_diff >= thresholds.acceptable_max_diff:
            result.level = "unacceptable"
            result.passed = False
            reasons.append(f"max_diff={result.max_diff:.4f} >= {thresholds.acceptable_max_diff}")
        elif result.max_diff >= thresholds.excellent_max_diff:
            result.level = "acceptable"
        else:
            result.level = "excellent"

        if result.cosine_sim_min < thresholds.min_cosine_sim:
            result.passed = False
            reasons.append(f"cosine_sim_min={result.cosine_sim_min:.4f} < {thresholds.min_cosine_sim}")
            if result.level != "unacceptable":
                result.level = "unacceptable"

        if speedup is not None and speedup < thresholds.min_speedup:
            result.passed = False
            reasons.append(f"speedup={speedup:.2f}x < {thresholds.min_speedup}x (no performance gain)")

        if reasons:
            result.fail_reason = "; ".join(reasons)

    except Exception as e:
        result.passed = False
        result.level = "unacceptable"
        result.fail_reason = f"validation error: {str(e)}"

    return result
