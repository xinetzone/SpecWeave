from __future__ import annotations

import numpy as np
import onnx
import onnxruntime as ort

from onnx_adaround.export import (
    build_arg_parser,
    fuse_quant_to_onnx,
    run_adaround,
)
from onnx_adaround.onnx_utils import QuantModel


def _write_image(tmp_path, name, size=(8, 8)):
    from PIL import Image
    img = Image.fromarray(np.random.randint(0, 255, (*size, 3), dtype=np.uint8), "RGB")
    img.save(tmp_path / name)


def test_fuse_quant_to_onnx(tmp_path, make_conv_model):
    model = make_conv_model
    qnn = QuantModel(model)
    layer = qnn.layers[0]
    # simulate an alpha from reconstruction
    layer.alpha = np.random.default_rng(0).standard_normal(layer.weight.shape)
    fuse_quant_to_onnx(model, qnn)
    # model still loadable and runnable
    sess = ort.InferenceSession(model.SerializeToString(), providers=["CPUExecutionProvider"])
    x = np.random.default_rng(1).standard_normal((1, 3, 8, 8)).astype(np.float32)
    out = sess.run(None, {"input": x})
    assert out[0].shape == (1, 4, 8, 8)


def test_run_adaround_end_to_end(tmp_path, make_conv_model):
    model = make_conv_model
    onnx_path = str(tmp_path / "in.onnx")
    onnx.save(model, onnx_path)
    # create calibration data dir with a few images
    cali = tmp_path / "cali"
    cali.mkdir()
    for i in range(4):
        _write_image(cali, f"img{i}.png")

    final = str(tmp_path / "out.onnx")
    out = run_adaround(
        onnx_path=onnx_path,
        final_onnx_path=final,
        data_path=str(cali),
        num_samples=4,
        iters_w=10,
        batch_size=2,
        input_size=8,  # model input is 8x8
    )
    assert out == final
    assert (tmp_path / "out.onnx").exists()
    # loaded model runs
    loaded = onnx.load(final)
    sess = ort.InferenceSession(loaded.SerializeToString(), providers=["CPUExecutionProvider"])
    x = np.random.default_rng(2).standard_normal((1, 3, 8, 8)).astype(np.float32)
    res = sess.run(None, {"input": x})
    assert res[0].shape == (1, 4, 8, 8)


def test_build_arg_parser():
    parser = build_arg_parser()
    args = parser.parse_args([
        "--onnx_path", "a.onnx", "--final_onnx_path", "b.onnx", "--data_path", "c",
    ])
    assert args.onnx_path == "a.onnx"
    assert args.n_bits_w == 4
