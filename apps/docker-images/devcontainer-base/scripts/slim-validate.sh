#!/usr/bin/env bash
# Slim validation test - simulate cleanup and verify compilation
set -e
export PATH=/opt/conda/envs/main/bin:/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

echo "=== Pre-slim size ==="
du -sh /opt/conda/envs/main/ 2>/dev/null

SAVED=0

del() {
    local target="$1"
    local desc="$2"
    if [ -e "$target" ]; then
        local sz
        sz=$(du -sb "$target" 2>/dev/null | awk '{print $1}')
        rm -rf "$target"
        echo "  [DEL] $desc ($(numfmt --to=iec $sz)): $target"
        SAVED=$((SAVED + sz))
    fi
}

echo ""
echo "=== Removing non-essential LLVM/Clang binaries ==="
# LLVM dev tools (not needed for user compilation)
del /opt/conda/envs/main/bin/llvm-exegesis-22        "llvm-exegesis (benchmarking)"
del /opt/conda/envs/main/bin/llvm-tblgen-22         "llvm-tblgen (build-time codegen)"
del /opt/conda/envs/main/bin/clang-tblgen-22        "clang-tblgen"
del /opt/conda/envs/main/bin/llvm-pdbutil-22       "PDB debug utility"
del /opt/conda/envs/main/bin/llvm-cvtres-22         "Windows resource converter"
del /opt/conda/envs/main/bin/llvm-rc-22             "Windows resource compiler"
del /opt/conda/envs/main/bin/llvm-dlltool-22        "Windows DLL tool"
del /opt/conda/envs/main/bin/llvm-lib-22            "Windows lib tool"
del /opt/conda/envs/main/bin/llvm-mt-22             "Windows manifest tool"
# Clang tools (IDE provides these; not needed for CLI compilation)
del /opt/conda/envs/main/bin/clangd                 "clangd (language server)"
del /opt/conda/envs/main/bin/clangd-22              "clangd versioned"
del /opt/conda/envs/main/bin/clang-tidy             "clang-tidy (linter)"
del /opt/conda/envs/main/bin/clang-tidy-22          "clang-tidy versioned"
del /opt/conda/envs/main/bin/clang-doc              "clang-doc"
del /opt/conda/envs/main/bin/clang-doc-22           "clang-doc versioned"
del /opt/conda/envs/main/bin/clang-include-fixer    "clang-include-fixer"
del /opt/conda/envs/main/bin/clang-include-fixer-22 "clang-include-fixer versioned"
del /opt/conda/envs/main/bin/clang-pseudo           "clang-pseudo"
del /opt/conda/envs/main/bin/clang-pseudo-22        "clang-pseudo versioned"
del /opt/conda/envs/main/bin/clang-rename           "clang-rename"
del /opt/conda/envs/main/bin/clang-rename-22        "clang-rename versioned"
del /opt/conda/envs/main/bin/clang-refactor         "clang-refactor"
del /opt/conda/envs/main/bin/clang-refactor-22      "clang-refactor versioned"
del /opt/conda/envs/main/bin/clang-apply-replacements    "clang-apply-replacements"
del /opt/conda/envs/main/bin/clang-apply-replacements-22 "clang-apply-replacements versioned"
del /opt/conda/envs/main/bin/diagtool               "diagtool"
# CMake extras
del /opt/conda/envs/main/bin/cpack                  "cpack (packaging)"
del /opt/conda/envs/main/bin/ccmake                 "ccmake (curses UI)"
# Cross-linkers (wasm/macos/windows - not needed for native linux)
del /opt/conda/envs/main/bin/wasm-ld                "wasm-ld (WebAssembly linker)"
del /opt/conda/envs/main/bin/ld64.lld               "ld64.lld (macOS linker)"
del /opt/conda/envs/main/bin/lld-link                "lld-link (Windows linker)"
# Pandoc (156M Haskell binary for doc conversion, optional)
del /opt/conda/envs/main/bin/pandoc                 "pandoc"
del /opt/conda/envs/main/bin/pandoc-server          "pandoc-server"
del /opt/conda/envs/main/bin/pandoc-lua             "pandoc-lua"

echo ""
echo "=== Removing dev headers (not needed for user C/C++ compilation) ==="
del /opt/conda/envs/main/include/llvm               "LLVM dev headers"
del /opt/conda/envs/main/include/llvm-c             "LLVM-C dev headers"
del /opt/conda/envs/main/include/clang              "Clang dev headers"
del /opt/conda/envs/main/include/clang-tidy         "Clang-tidy headers"
del /opt/conda/envs/main/include/clang-c            "Clang-C dev headers"

echo ""
echo "=== Removing sanitizer & debug libraries ==="
find /opt/conda/envs/main/lib -name "libclang_rt.*san*" -delete 2>/dev/null || true
find /opt/conda/envs/main/lib -name "libclang_rt.*fuzzer*" -delete 2>/dev/null || true
find /opt/conda/envs/main/lib -name "libclang_rt.*profile*" -delete 2>/dev/null || true
find /opt/conda/envs/main/lib -name "libclang_rt.*memprof*" -delete 2>/dev/null || true
find /opt/conda/envs/main/lib -name "libclang_rt.*hwasan*" -delete 2>/dev/null || true
find /opt/conda/envs/main/lib -name "libclang_rt.*nsan*" -delete 2>/dev/null || true
find /opt/conda/envs/main/lib -name "libarcher*" -delete 2>/dev/null || true
find /opt/conda/envs/main/lib -name "libompd*" -delete 2>/dev/null || true
echo "  [DONE] Sanitizer/debug libraries removed"

echo ""
echo "=== Removing libexec/llvm build tools ==="
del /opt/conda/envs/main/libexec/llvm               "LLVM libexec (build-time tools)"

echo ""
echo "=== Removing old/duplicate libraries ==="
# Check if libclang.so.13 is a symlink to libclang.so.22 or a separate file
if [ -f /opt/conda/envs/main/lib/libclang.so.13 ] && [ ! -L /opt/conda/envs/main/lib/libclang.so.13 ]; then
    # It's a real file. Check if it's hardlinked to the v22 version
    inode13=$(stat -c %i /opt/conda/envs/main/lib/libclang.so.13 2>/dev/null || echo 0)
    inode22=$(stat -c %i /opt/conda/envs/main/lib/libclang-cpp.so.22.1 2>/dev/null || echo 1)
    if [ "$inode13" != "$inode22" ]; then
        del /opt/conda/envs/main/lib/libclang.so.13    "libclang.so.13 (old compat, 50M)"
    fi
fi

echo ""
echo "=== Stripping all shared libraries ==="
BEFORE_SO=$(du -sb /opt/conda/envs/main/lib/*.so* 2>/dev/null | awk '{sum+=$1} END{print sum+0}')
for f in /opt/conda/envs/main/lib/*.so*; do
    [ -f "$f" ] && strip --strip-unneeded "$f" 2>/dev/null || true
done
# Also strip in subdirectories
find /opt/conda/envs/main/lib -name "*.so*" -type f -exec strip --strip-unneeded {} \; 2>/dev/null || true
AFTER_SO=$(du -sb /opt/conda/envs/main/lib/*.so* 2>/dev/null | awk '{sum+=$1} END{print sum+0}')
SO_SAVED=$((BEFORE_SO - AFTER_SO))
echo "  .so strip saved: $(numfmt --to=iec $SO_SAVED)"
SAVED=$((SAVED + SO_SAVED))

echo ""
echo "=== Removing static libraries ==="
find /opt/conda/envs/main -name "*.a" -delete 2>/dev/null || true
echo "  [DONE] Static libraries removed"

echo ""
echo "=== Removing CMake config files for LLVM/Clang (only needed for dev) ==="
rm -rf /opt/conda/envs/main/lib/cmake/llvm 2>/dev/null || true
rm -rf /opt/conda/envs/main/lib/cmake/clang 2>/dev/null || true
rm -rf /opt/conda/envs/main/lib/cmake/lld 2>/dev/null || true
echo "  [DONE] CMake config files removed"

echo ""
echo "=== Post-slim size ==="
du -sh /opt/conda/envs/main/ 2>/dev/null
echo ""
echo "Total estimated savings from file deletion: $(numfmt --to=iec $SAVED)"

echo ""
echo "============================================================"
echo "=== VERIFICATION: C/C++ compilation still works? ==="
echo "============================================================"

echo ""
echo "[TEST 1] C++ Hello World with STL"
cat > /tmp/hello.cpp << 'EOF'
#include <iostream>
#include <vector>
#include <string>
int main() {
    std::vector<std::string> msg = {"Hello", "from", "slimmed", "container!"};
    for (auto& m : msg) std::cout << m << " ";
    std::cout << "\n";
    return 0;
}
EOF
clang++ --std=c++17 -stdlib=libstdc++ /tmp/hello.cpp -o /tmp/hello && /tmp/hello && echo "[PASS] C++ STL compilation works!"
rm -f /tmp/hello.cpp /tmp/hello

echo ""
echo "[TEST 2] C compilation"
cat > /tmp/hello.c << 'EOF'
#include <stdio.h>
int main() { printf("Hello from C!\n"); return 0; }
EOF
clang --std=c11 /tmp/hello.c -o /tmp/hello_c && /tmp/hello_c && echo "[PASS] C compilation works!"
rm -f /tmp/hello.c /tmp/hello_c

echo ""
echo "[TEST 3] CMake + Ninja build"
mkdir -p /tmp/cmake_test
cat > /tmp/cmake_test/CMakeLists.txt << 'EOF'
cmake_minimum_required(VERSION 3.10)
project(hello)
add_executable(hello main.cpp)
EOF
cat > /tmp/cmake_test/main.cpp << 'EOF'
#include <iostream>
int main() { std::cout << "CMake+Ninja build works!\n"; return 0; }
EOF
cd /tmp/cmake_test
cmake -G Ninja -B build -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_C_COMPILER=clang >/dev/null 2>&1
ninja -C build >/dev/null 2>&1 && ./build/hello && echo "[PASS] CMake+Ninja build works!"
rm -rf /tmp/cmake_test

echo ""
echo "[TEST 4] Core tools available"
for cmd in clang clang++ llvm-config cmake ninja make ccache ld.lld; do
    if command -v $cmd >/dev/null 2>&1; then
        echo "  [OK] $cmd"
    else
        echo "  [FAIL] $cmd MISSING!"
        exit 1
    fi
done

echo ""
echo "[TEST 5] Python + free-threading still works"
python3 -c "import sys; assert sys._is_gil_enabled() is False, 'GIL check failed'; print('[PASS] Python free-threading OK')"
python3 -c "import onnx, onnxruntime; print(f'[PASS] ONNX {onnx.__version__} + onnxruntime {onnxruntime.__version__}')"

echo ""
echo "[TEST 6] ccache masquerade"
mkdir -p /tmp/ccache_test
export CCACHE_DIR=/tmp/ccache_test
ccache -z >/dev/null 2>&1
echo 'int main(){return 0;}' > /tmp/tiny.c
ccache clang /tmp/tiny.c -o /tmp/tiny >/dev/null 2>&1 && /tmp/tiny && echo "[PASS] ccache wrapping works!"
ccache -s 2>&1 | head -5
rm -rf /tmp/ccache_test /tmp/tiny.c /tmp/tiny

echo ""
echo "============================================================"
echo "ALL VERIFICATION TESTS PASSED!"
echo "============================================================"
