"""ONNX model loading, graph-level BatchNorm folding, and QuantModel.

Operates directly on the ONNX graph (torch-free). Mirrors the role of
``xmnn.adaround.quant.quant_model`` + ``fold_bn`` + the onnx2pytorch conversion
step, but keeps everything as an ONNX model and numpy arrays.
"""

from __future__ import annotations

import numpy as np
import onnx
from onnx import numpy_helper

from .quant import UniformAffineQuantizer

# Ops that carry a learnable weight (quantizable layers).
QUANTIZABLE_OPS = ("Conv", "ConvTranspose", "MatMul", "Gemm")


class QuantLayer:
    """A quantizable layer extracted from the ONNX graph (numpy-backed)."""

    __slots__ = (
        "name",
        "op_type",
        "weight_name",
        "weight",
        "bias_name",
        "bias",
        "attrs",
        "ignore_reconstruction",
        "weight_quantizer",
        "act_quantizer",
        "use_weight_quant",
        "use_act_quant",
        "alpha",
        "delta",
        "zero_point",
        "n_bits",
        "soft_targets",
    )

    def __init__(self, name, op_type, weight_name, weight, bias_name, bias, attrs):
        self.name = name
        self.op_type = op_type
        self.weight_name = weight_name
        self.weight = weight
        self.bias_name = bias_name
        self.bias = bias
        self.attrs = attrs
        self.ignore_reconstruction = False
        self.weight_quantizer = None
        self.act_quantizer = None
        self.use_weight_quant = False
        self.use_act_quant = False
        self.alpha = None
        self.delta = None
        self.zero_point = None
        self.n_bits = 8
        self.soft_targets = False


class QuantModel:
    """Wraps an ONNX model and exposes its quantizable layers in order."""

    def __init__(self, onnx_model, weight_quant_params=None, act_quant_params=None,
                 auto_quant_blocks=True):
        self.model = onnx_model
        self.layers = _extract_layers(onnx_model)
        self.weight_quant_params = weight_quant_params or {}
        self.act_quant_params = act_quant_params or {}
        self._init_quantizers()

    def _init_quantizers(self):
        for layer in self.layers:
            wq_params = dict(self.weight_quant_params)
            groups = layer.attrs.get("group", 1)
            if layer.op_type in ("Conv", "ConvTranspose"):
                if layer.weight.shape[0] / groups > 16:
                    wq_params["n_bits"] = 4
                else:
                    wq_params["n_bits"] = 8
            else:
                wq_params["n_bits"] = 8
            layer.n_bits = wq_params["n_bits"]
            layer.weight_quantizer = UniformAffineQuantizer(**wq_params)
            layer.act_quantizer = UniformAffineQuantizer(**self.act_quant_params)

    def named_layers(self):
        return [(layer.name, layer) for layer in self.layers]

    def set_first_last_layer_to_8bit(self):
        if len(self.layers) == 0:
            return
        self.layers[0].weight_quantizer.bitwidth_refactor(8)
        self.layers[0].act_quantizer.bitwidth_refactor(8)
        self.layers[0].ignore_reconstruction = True
        self.layers[0].n_bits = 8

    def disable_network_output_quantization(self):
        if len(self.layers):
            self.layers[-1].use_act_quant = False

    def forward_weight_quant(self, layer, weight):
        """Apply the layer's uniform affine quantizer to a weight array."""
        return layer.weight_quantizer(weight)


def _attrs_of(node):
    a = {}
    for attr in node.attribute:
        if attr.type == onnx.AttributeProto.INTS:
            a[attr.name] = list(attr.ints)
        elif attr.type == onnx.AttributeProto.INT:
            a[attr.name] = attr.i
        elif attr.type == onnx.AttributeProto.FLOAT:
            a[attr.name] = attr.f
        elif attr.type == onnx.AttributeProto.STRING:
            a[attr.name] = attr.s.decode()
        elif attr.type == onnx.AttributeProto.FLOATS:
            a[attr.name] = list(attr.floats)
        elif attr.type == onnx.AttributeProto.TENSOR:
            a[attr.name] = numpy_helper.to_array(attr.t)
    return a


def _initializer_map(model):
    return {init.name: numpy_helper.to_array(init) for init in model.graph.initializer}


def _extract_layers(model):
    inits = _initializer_map(model)
    layers = []
    for node in model.graph.node:
        if node.op_type not in QUANTIZABLE_OPS:
            continue
        if len(node.input) < 1 or node.input[0] not in inits:
            # Weight is usually input[1]; handle MatMul/Gemm weight locations.
            pass
        name = node.output[0] if node.output else f"{node.op_type}_{len(layers)}"
        attrs = _attrs_of(node)

        if node.op_type in ("MatMul", "Gemm"):
            weight_name = node.input[1]
            bias_name = node.input[2] if len(node.input) > 2 else None
        else:  # Conv / ConvTranspose
            weight_name = node.input[1]
            bias_name = node.input[2] if len(node.input) > 2 else None

        if weight_name not in inits:
            continue
        weight = inits[weight_name]
        bias = inits[bias_name] if bias_name and bias_name in inits else None

        # Normalize conv attrs (ints may be a single scalar).
        if node.op_type in ("Conv", "ConvTranspose"):
            for key in ("strides", "pads", "dilations"):
                if key in attrs and len(attrs[key]) == 1:
                    attrs[key] = attrs[key] * 2
            if "group" not in attrs:
                attrs["group"] = 1
            if "strides" not in attrs:
                attrs["strides"] = [1, 1]
            if "pads" not in attrs:
                attrs["pads"] = [0, 0, 0, 0]
            if "dilations" not in attrs:
                attrs["dilations"] = [1, 1]

        layers.append(QuantLayer(name, node.op_type, weight_name, weight,
                                 bias_name, bias, attrs))
    return layers


def fold_bn_into_onnx(model):
    """Graph-level BatchNorm folding into preceding Conv/MatMul/Gemm.

    Folds BatchNormalization parameters into the previous quantizable op's
    weight and bias, then removes the BN node. Returns the (mutated) model.
    """
    inits = {init.name: init for init in model.graph.initializer}
    graphs = list(model.graph.node)

    # Map node output -> node for quick lookup.
    out_to_node = {}
    for node in graphs:
        for o in node.output:
            out_to_node[o] = node

    remove_nodes = set()
    for node in graphs:
        if node.op_type != "BatchNormalization":
            continue
        if len(node.input) < 5:
            continue
        prev_out = node.input[0]
        prev_node = out_to_node.get(prev_out)
        if prev_node is None or prev_node.op_type not in QUANTIZABLE_OPS:
            continue

        scale_name = node.input[1]
        b_name = node.input[2]
        mean_name = node.input[3]
        var_name = node.input[4]
        eps = _bn_epsilon(node)

        if not all(n in inits for n in (scale_name, b_name, mean_name, var_name)):
            continue

        scale = numpy_helper.to_array(inits[scale_name])
        bias = numpy_helper.to_array(inits[b_name])
        mean = numpy_helper.to_array(inits[mean_name])
        var = numpy_helper.to_array(inits[var_name])

        # Determine weight initializer and any existing conv bias.
        if prev_node.op_type in ("MatMul", "Gemm"):
            w_name = prev_node.input[1]
            conv_bias_name = prev_node.input[2] if len(prev_node.input) > 2 else None
        else:
            w_name = prev_node.input[1]
            conv_bias_name = prev_node.input[2] if len(prev_node.input) > 2 else None

        w_arr = numpy_helper.to_array(inits[w_name])
        safe_std = np.sqrt(var + eps)
        if w_arr.ndim == 4:  # Conv
            w_new = w_arr * (scale / safe_std).reshape(-1, 1, 1, 1)
        else:  # MatMul/Gemm/Linear
            w_new = w_arr * (scale / safe_std).reshape(-1, 1)

        if conv_bias_name and conv_bias_name in inits:
            cbias = numpy_helper.to_array(inits[conv_bias_name])
            beta = bias - scale * mean / safe_std
            b_new = scale * cbias / safe_std + beta
        else:
            beta = bias - scale * mean / safe_std
            b_new = beta

        # Write folded weight back.
        inits[w_name].CopyFrom(numpy_helper.from_array(w_new, name=w_name))

        # Add/update a bias initializer.
        if conv_bias_name and conv_bias_name in inits:
            inits[conv_bias_name].CopyFrom(numpy_helper.from_array(b_new, name=conv_bias_name))
        else:
            new_bias_name = f"{w_name}_folded_bias"
            inits[new_bias_name] = numpy_helper.from_array(b_new, name=new_bias_name)
            # append bias input to prev_node
            prev_node.input.append(new_bias_name)

        # Replace downstream references of the BN output with conv output.
        bn_out = node.output[0]
        for other in graphs:
            for i, inp in enumerate(other.input):
                if inp == bn_out:
                    other.input[i] = prev_out
        if bn_out in model.graph.output:
            for o in model.graph.output:
                if o.name == bn_out:
                    o.CopyFrom(onnx.ValueInfoProto())
        remove_nodes.add(node.name if node.name else id(node))

    # Remove BN nodes.
    new_nodes = []
    removed = set()
    for node in graphs:
        key = node.name if node.name else id(node)
        if key in remove_nodes:
            removed.add(node.name)
            continue
        new_nodes.append(node)
    del model.graph.node[:]
    model.graph.node.extend(new_nodes)
    return model


def _bn_epsilon(node):
    for attr in node.attribute:
        if attr.name == "epsilon":
            return attr.f
    return 1e-5


def build_weight_mapping(model):
    """Map layer output name -> weight initializer name for Conv/ConvTranspose."""
    mapping = {}
    for node in model.graph.node:
        if node.op_type in ("Conv", "ConvTranspose") and len(node.input) >= 2:
            mapping[node.output[0]] = node.input[1]
    return mapping
