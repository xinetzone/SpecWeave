#!/bin/bash
# First, simulate an editable install to create _editable_*.pth residuals,
# then run the full test-conda-build.sh to verify cleanup works.
set -e

source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi

echo "============================================================"
echo " Pre-test: Simulating editable install to create residuals"
echo "============================================================"
echo ""

# Do a real pip editable install to create _editable_skbc_*.pth residuals
echo "Running: pip install -e /SpecWeave/projects/xuanspace/libs/caffe-ffi (no-deps)"
pip install --no-deps -e /SpecWeave/projects/xuanspace/libs/caffe-ffi 2>&1 | tail -5
echo ""

echo "=== Verifying editable residuals exist ==="
SP_DIR=$(python -c "import site; print(site.getsitepackages()[0])")
ls -la "$SP_DIR"/_editable_skbc_caffe_ffi* 2>&1
echo ""

echo "=== Verifying Python loads from SOURCE (editable active) ==="
python -c "
import caffe_ffi
print('Loading from:', caffe_ffi.__file__)
assert 'site-packages' not in caffe_ffi.__file__, 'Should load from source before cleanup!'
print('PASS: Loading from source (editable is active)')
"
echo ""

echo "============================================================"
echo " Now running test-conda-build.sh (should auto-clean residuals)"
echo "============================================================"
echo ""

# Fix CRLF on the mounted script
sed -i 's/\r$//' /SpecWeave/apps/docker-images/caffe-ffi-jupyter/scripts/test-conda-build.sh

# Run the test script
bash /SpecWeave/apps/docker-images/caffe-ffi-jupyter/scripts/test-conda-build.sh
