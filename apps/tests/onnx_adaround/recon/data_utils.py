"""Intermediate activation caching for layer reconstruction.

Uses onnxruntime to run the FP32 model once with all quantizable layers'
inputs and outputs registered as extra graph outputs, so we can cache the
per-layer reference in/out needed by AdaRound reconstruction.
"""

from __future__ import annotations

import numpy as np
import onnx
import onnxruntime as ort


def _with_extra_outputs(model, tensor_names):
    """Return a deep copy of the model with extra tensors as graph outputs.

    Extra outputs (e.g. intermediate layer tensors) are registered with their
    actual element type, resolved via ONNX shape inference. onnxruntime rejects
    models whose graph outputs carry an UNDEFINED elem_type, which would
    otherwise break multi-layer (multi-quantizable-op) models where a layer's
    input/output is an intermediate tensor rather than the graph input/output.
    """
    m = onnx.ModelProto()
    m.CopyFrom(model)
    existing = {o.name for o in m.graph.output}

    # Populate ``value_info`` for intermediate tensors so we can resolve types.
    try:
        inferred = onnx.shape_inference.infer_shapes(m, strict_mode=False, data_prop=False)
    except Exception:  # shape inference failure is a fallback to the raw model
        inferred = m
    type_map = {}
    for vi in list(inferred.graph.input) + list(inferred.graph.value_info):
        tt = vi.type.tensor_type
        if vi.name and tt.HasField("elem_type"):
            type_map[vi.name] = tt.elem_type

    for name in tensor_names:
        if name in existing:
            continue
        info = onnx.helper.make_tensor_value_info(name, onnx.TensorProto.UNDEFINED, None)
        elem = type_map.get(name)
        if elem is not None:
            info.type.tensor_type.elem_type = elem
        m.graph.output.append(info)
    return m


def build_ort_session(model, providers=None):
    if providers is None:
        providers = ["CPUExecutionProvider"]
    return ort.InferenceSession(model.SerializeToString(), providers=providers)


def _make_batch_dynamic(model):
    """Make every graph input's leading (batch) dimension dynamic.

    ONNX models often carry a fixed batch size (e.g. ``[1, 3, 8, 8]``), which
    would make onnxruntime reject batched calibration feeds. We relax only the
    leading dimension so arbitrary batch sizes can be cached. Mutates the model
    copy in place.
    """
    for inp in model.graph.input:
        tt = inp.type.tensor_type
        if not tt.HasField("shape"):
            continue
        dims = tt.shape.dim
        if len(dims) > 0 and not dims[0].HasField("dim_value"):
            continue
        if len(dims) > 0:
            dims[0].dim_param = "batch"
    return model


def cache_layer_inp_out(model, layers, cali_data, batch_size=32):
    """Run the FP32 model once and cache (input, output) for each layer.

    ``cali_data`` is an NCHW numpy array. Returns two lists aligned with
    ``layers``: ``inp_batches[i]`` and ``out_batches[i]`` are numpy arrays of
    shape (num_samples, ...) captured at that layer's input / output.
    """
    # Collect unique tensors we need.
    inp_names = []
    out_names = []
    for layer in layers:
        # For layer input we use the first graph input feeding into it; the
        # simplest robust proxy is the node's first input tensor name that is
        # not an initializer. We cache the layer output and the node input.
        node = _find_node(model, layer)
        if node is None:
            continue
        node_inp = _first_non_init_input(model, node)
        node_out = node.output[0]
        if node_inp not in inp_names:
            inp_names.append(node_inp)
        if node_out not in out_names:
            out_names.append(node_out)

    m = _with_extra_outputs(model, inp_names + out_names)
    _make_batch_dynamic(m)
    sess = build_ort_session(m)

    input_name = model.graph.input[0].name
    n = cali_data.shape[0]
    inp_store = {k: [] for k in inp_names}
    out_store = {k: [] for k in out_names}
    fetch = inp_names + out_names

    for i in range(0, n, batch_size):
        batch = cali_data[i:i + batch_size]
        feeds = {input_name: batch.astype(np.float32)}
        # Request outputs by explicit name so ordering matches ``fetch``,
        # independent of the model's graph-output order.
        res = sess.run(fetch, feeds)
        for name, arr in zip(fetch, res):
            if name in inp_store:
                inp_store[name].append(arr)
            else:
                out_store[name].append(arr)

    # Rebuild per-layer aligned lists.
    inp_batches = []
    out_batches = []
    for layer in layers:
        node = _find_node(model, layer)
        if node is None:
            inp_batches.append(None)
            out_batches.append(None)
            continue
        node_inp = _first_non_init_input(model, node)
        node_out = node.output[0]
        inp = _concat(inp_store.get(node_inp))
        out = _concat(out_store.get(node_out))
        inp_batches.append(inp)
        out_batches.append(out)
    return inp_batches, out_batches


def _find_node(model, layer):
    for node in model.graph.node:
        if node.op_type == layer.op_type and node.output and node.output[0] == layer.name:
            return node
    return None


def _first_non_init_input(model, node):
    inits = {i.name for i in model.graph.initializer}
    graph_inputs = {i.name for i in model.graph.input}
    for inp in node.input:
        if inp in inits:
            continue
        if inp == "":
            continue
        if inp in graph_inputs or inp in _intermediate_names(model):
            return inp
    return node.input[0]


def _intermediate_names(model):
    names = set()
    for node in model.graph.node:
        names.update(node.output)
    return names


def _concat(batches):
    if not batches:
        return None
    return np.concatenate([b for b in batches if b is not None], axis=0)
