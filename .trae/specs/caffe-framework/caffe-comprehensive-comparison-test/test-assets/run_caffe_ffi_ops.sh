#!/bin/bash
# caffe-ffi 算子测试（显式指定 ops 文件，绕过 testpaths=.. 递归）
set -e
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
export PATH="$CONDA_PREFIX/bin:$PATH"
export KMP_DUPLICATE_LIB_OK=TRUE

OPS_ROOT="/SpecWeave/projects/xuanspace/libs/caffe-ffi/tests/python/ops"
cd "$OPS_ROOT"

echo "=== 算子测试 (ops) ==="
python -m pytest -p no:cacheprovider \
  -o testpaths= \
  test_convolution.py test_pooling.py test_relu.py test_sigmoid.py test_tanh.py \
  test_softmax.py test_eltwise.py test_concat.py test_slice.py test_scale.py \
  test_batchnorm.py test_inner_product.py test_dropout.py test_reshape.py \
  test_flatten.py test_lrn.py test_prelu.py test_elu.py test_swish.py \
  test_argmax.py test_clip.py test_crop.py test_deconvolution.py test_embed.py \
  test_exp.py test_log.py test_power.py test_reduction.py test_threshold.py \
  test_tile.py test_permute.py \
  -q --tb=short --no-header 2>&1 | tail -60
echo "OPS_EXIT=${PIPESTATUS[0]}"