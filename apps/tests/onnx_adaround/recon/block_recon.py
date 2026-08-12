"""Block reconstruction for onnx-adaround.

Reconstructs a block by iterating per-layer reconstruction. Mirrors the role of
``xmnn.adaround.quant.block_recon``.
"""

from .layer_recon import layer_reconstruction


def block_reconstruction(model, block_layers, inp_cache, out_cache, **kwargs):
    """Reconstruct a block's layers.

    ``block_layers`` is a list of QuantLayer; ``inp_cache`` / ``out_cache`` are
    lists of per-layer reference activations aligned with ``block_layers``.
    """
    for i, layer in enumerate(block_layers):
        layer_reconstruction(model, layer, inp_cache[i], out_cache[i], **kwargs)
    return block_layers


__all__ = ["block_reconstruction", "layer_reconstruction"]
