#!/bin/bash
# 测试 conda 编译器是否能正常链接
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
cat > /tmp/t.cpp <<'EOF'
int main(){return 0;}
EOF
echo "=== 编译+链接 ==="
/opt/conda/envs/caffe-ffi/bin/x86_64-conda-linux-gnu-c++ /tmp/t.cpp -o /tmp/t 2>&1
echo "COMPILE_EXIT=$?"
echo "=== 运行 ==="
/tmp/t
echo "RUN_EXIT=$?"
echo "=== CXX 版本 ==="
/opt/conda/envs/caffe-ffi/bin/x86_64-conda-linux-gnu-c++ --version 2>&1 | head -1
echo "=== ldd 检查 ==="
ldd /tmp/t 2>&1 | head -5