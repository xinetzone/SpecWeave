"""统一性能基准测试模块"""
import time
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import onnxruntime as ort


@dataclass
class BenchmarkResult:
    """基准测试结果"""
    avg_ms: float = 0.0
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    min_ms: float = 0.0
    max_ms: float = 0.0
    std_ms: float = 0.0
    throughput_fps: float = 0.0
    size_kb: float = 0.0
    runs: int = 0
    warmup: int = 0
    threads: int = 0
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.error is None


def create_session(model_path: str, intra_threads: int = 4,
                   inter_threads: int = 1,
                   providers: Optional[list] = None) -> ort.InferenceSession:
    """创建统一配置的ONNX Runtime InferenceSession

    所有模型使用相同SessionOptions确保公平对比：
    - ORT_ENABLE_ALL: 最高图优化级别
    - ORT_SEQUENTIAL: 顺序执行（避免并行开销干扰测量）
    - 固定线程数: 保证可复现性
    """
    if providers is None:
        providers = ["CPUExecutionProvider"]
    so = ort.SessionOptions()
    so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    so.intra_op_num_threads = intra_threads
    so.inter_op_num_threads = inter_threads
    so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    return ort.InferenceSession(model_path, sess_options=so, providers=providers)


def _safe_get_input_shape(inp, default: int = 1) -> tuple:
    """从ONNX Runtime input安全提取形状，兼容DimensionProto/纯int/Session对象

    动态维度（dim_value=0 或 dim_param字符串存在）会被替换为default值。
    与 quantize._safe_get_input_shape 保持一致的逻辑。
    """
    # 支持传入InferenceSession对象
    if isinstance(inp, ort.InferenceSession):
        if len(inp.get_inputs()) == 0:
            raise ValueError("Session has no inputs")
        inp = inp.get_inputs()[0]
    shape = inp.shape
    result = []
    for d in shape:
        if isinstance(d, int):
            result.append(d if d > 0 else default)
        elif hasattr(d, 'dim_value'):
            if hasattr(d, 'dim_param') and d.dim_param:
                result.append(default)
            else:
                result.append(d.dim_value if d.dim_value > 0 else default)
        else:
            result.append(default)
    return tuple(result)


def _resolve_input(sess: ort.InferenceSession, input_shape: Optional[tuple],
                   input_name: Optional[str], default_batch: int = 1) -> tuple:
    """解析输入名称和形状

    安全处理：
    - 动态维度（字符串dim_param，如"batch"/"seq_len"）替换为default_batch
    - dim_value=0或负数替换为default_batch
    - 非int/非DimensionProto类型安全降级为default_batch
    """
    if len(sess.get_inputs()) == 0:
        raise ValueError("Model has no inputs")
    inp = sess.get_inputs()[0]
    name = input_name or inp.name
    is_fp16 = "float16" in str(inp.type)
    dtype = np.float16 if is_fp16 else np.float32
    if input_shape is None:
        shape = _safe_get_input_shape(inp, default=default_batch)
    else:
        shape = tuple(input_shape)
    return name, shape, dtype


def benchmark_model(model_path: str, input_shape: Optional[tuple] = None,
                    input_name: Optional[str] = None,
                    warmup: int = 50, runs: int = 300,
                    intra_threads: int = 4,
                    providers: Optional[list] = None) -> BenchmarkResult:
    """基准测试模型推理性能

    Args:
        model_path: ONNX模型路径
        input_shape: 输入形状，None则自动从模型推断
        input_name: 输入节点名，None则自动检测
        warmup: 预热次数（消除JIT/缓存影响）
        runs: 正式测量次数
        intra_threads: intra_op线程数
        providers: EP列表，默认CPUExecutionProvider

    Returns:
        BenchmarkResult包含avg/p50/p95/p99延迟(ms)、吞吐量(FPS)、模型大小
    """
    result = BenchmarkResult(runs=runs, warmup=warmup, threads=intra_threads)

    try:
        import os
        result.size_kb = os.path.getsize(model_path) / 1024
        sess = create_session(model_path, intra_threads, providers=providers)
        name, shape, dtype = _resolve_input(sess, input_shape, input_name)
    except Exception as e:
        result.error = str(e)
        return result

    def make_input():
        return np.random.randn(*shape).astype(dtype)

    try:
        for _ in range(warmup):
            sess.run(None, {name: make_input()})

        times = []
        for _ in range(runs):
            x = make_input()
            t0 = time.perf_counter()
            sess.run(None, {name: x})
            times.append(time.perf_counter() - t0)

        t = np.array(times) * 1000  # ms
        result.avg_ms = float(np.mean(t))
        result.p50_ms = float(np.median(t))
        result.p95_ms = float(np.percentile(t, 95))
        result.p99_ms = float(np.percentile(t, 99))
        result.min_ms = float(np.min(t))
        result.max_ms = float(np.max(t))
        result.std_ms = float(np.std(t))
        result.throughput_fps = float(1000.0 / np.mean(t) * shape[0])
    except Exception as e:
        result.error = str(e)

    return result
