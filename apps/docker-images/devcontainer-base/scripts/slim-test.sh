#!/bin/bash
set -e
export PATH=/opt/conda/envs/main/bin:/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

echo "=== Strip savings test ==="
echo "libLLVM.so.22.1 before: $(du -sh /opt/conda/envs/main/lib/libLLVM.so.22.1 | cut -f1)"
cp /opt/conda/envs/main/lib/libLLVM.so.22.1 /tmp/libLLVM-test.so
strip --strip-unneeded /tmp/libLLVM-test.so 2>&1 || echo "strip may have warnings"
echo "libLLVM.so.22.1 after:  $(du -sh /tmp/libLLVM-test.so | cut -f1)"

echo "libclang-cpp.so.22.1 before: $(du -sh /opt/conda/envs/main/lib/libclang-cpp.so.22.1 | cut -f1)"
cp /opt/conda/envs/main/lib/libclang-cpp.so.22.1 /tmp/libclang-cpp-test.so
strip --strip-unneeded /tmp/libclang-cpp-test.so 2>&1 || true
echo "libclang-cpp.so.22.1 after:  $(du -sh /tmp/libclang-cpp-test.so | cut -f1)"

echo ""
echo "=== Total potential strip savings for all .so ==="
BEFORE=$(du -sb /opt/conda/envs/main/lib/*.so* 2>/dev/null | awk '{sum+=$1} END{print sum}')
mkdir -p /tmp/so-test
cp /opt/conda/envs/main/lib/*.so* /tmp/so-test/ 2>/dev/null || true
for f in /tmp/so-test/*.so*; do
    strip --strip-unneeded "$f" 2>/dev/null || true
done
AFTER=$(du -sb /tmp/so-test 2>/dev/null | awk '{print $1}')
rm -rf /tmp/so-test /tmp/libLLVM-test.so /tmp/libclang-cpp-test.so
echo "Before strip: $(numfmt --to=iec $BEFORE)"
echo "After strip:  $(numfmt --to=iec $AFTER)"
echo "Saved:        $(numfmt --to=iec $((BEFORE - AFTER)))"

echo ""
echo "=== Check clang++ header search path ==="
echo '#include <iostream>' > /tmp/test-stl.cpp
echo 'int main() { std::cout << "hi\n"; return 0; }' >> /tmp/test-stl.cpp
echo "Include search paths:"
clang++ -v /tmp/test-stl.cpp -o /tmp/test-stl -stdlib=libstdc++ 2>&1 | grep -E "^\s/" | head -20
/tmp/test-stl
echo "C++ STL compile works!"
rm -f /tmp/test-stl.cpp /tmp/test-stl

echo ""
echo "=== Check which tools are truly needed for compilation ==="
echo "clang binary: $(which clang)"
echo "clang++ binary: $(which clang++)"
echo "lld binary: $(which ld.lld)"
echo "llvm-config: $(which llvm-config)"
echo "Headers in lib/clang:"
ls /opt/conda/envs/main/lib/clang/*/include/ 2>/dev/null | head -5
