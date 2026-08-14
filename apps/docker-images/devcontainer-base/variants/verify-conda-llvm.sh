#!/bin/bash
set -e
echo "=== Conda-LLVM Variant Runtime Verification ==="
echo ""

echo "1. Default environment check:"
echo "   CONDA_DEFAULT_ENV=$CONDA_DEFAULT_ENV"
echo "   PATH=$PATH"
echo ""

echo "2. Python version and path:"
python --version 2>&1
which python
echo ""

echo "3. LLVM tool paths (should be in /opt/conda/envs/main/bin):"
echo "   llvm-config: $(which llvm-config 2>&1)"
echo "   clang:       $(which clang 2>&1)"
echo "   clang++:     $(which clang++ 2>&1)"
echo "   cmake:       $(which cmake 2>&1)"
echo "   ninja:       $(which ninja 2>&1)"
echo "   make:        $(which make 2>&1)"
echo ""

echo "4. Tool version verification:"
echo "   LLVM:    $(llvm-config --version 2>&1)"
echo "   Clang:   $(clang --version 2>&1 | head -1)"
echo "   CMake:   $(cmake --version 2>&1 | head -1)"
echo "   Ninja:   $(ninja --version 2>&1)"
echo "   Make:    $(make --version 2>&1 | head -1)"
echo ""

echo "5. Conda environments:"
conda env list 2>&1
echo ""

echo "6. Installation location verification:"
if [ -x /opt/conda/envs/main/bin/llvm-config ]; then
    echo "   ✅ llvm-config is in main environment (/opt/conda/envs/main/bin/)"
else
    echo "   ❌ llvm-config NOT in main environment"
fi
if [ -x /opt/conda/envs/main/bin/clang ]; then
    echo "   ✅ clang is in main environment"
else
    echo "   ❌ clang NOT in main environment"
fi
echo ""

echo "7. Jupyter availability (from main env):"
which jupyter 2>&1
jupyter --version 2>&1 | head -3
echo ""

echo "8. Build metadata:"
cat /etc/devcontainer-variant-conda-llvm-build-info 2>&1
echo ""

echo "=== All verification checks complete ==="
