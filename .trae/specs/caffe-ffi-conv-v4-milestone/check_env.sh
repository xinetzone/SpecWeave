#!/bin/bash
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
echo "which python: $(which python)"
echo "exec:"
python -c "import sys; print(sys.executable)"
echo "numpy check:"
python -c "import numpy; print('numpy', numpy.__version__)" 2>&1 | head -3
echo "caffe_ffi check:"
python -c "import caffe_ffi; print('caffe_ffi', caffe_ffi.__version__)" 2>&1 | head -3
echo "conda numpy:"
conda list 2>/dev/null | grep -i numpy | head -5