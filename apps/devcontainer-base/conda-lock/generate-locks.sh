#!/usr/bin/env bash
# =============================================================================
# generate-locks.sh — conda-lock 锁文件生成 + cmake+ninja C扩展编译命令集 (B2)
# =============================================================================
# 功能：
#   1. 生成跨平台 conda-lock 锁文件（linux-64, osx-64, osx-arm64, win-64）
#   2. 提供 cmake+ninja 编译 C 扩展的标准命令（适配 cp314t free-threading ABI）
#   3. 验证锁文件中所有包的 ABI 标签与 free-threading 兼容性
#
# 用法：
#   bash conda-lock/generate-locks.sh              # 生成 linux-64 锁文件
#   bash conda-lock/generate-locks.sh --all        # 生成所有平台锁文件
#   bash conda-lock/generate-locks.sh --verify     # 验证现有锁文件
#   bash conda-lock/generate-locks.sh --cmake      # 打印 cmake+ninja 编译命令模板
#   bash conda-lock/generate-locks.sh --install    # 从锁文件安装环境
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${SCRIPT_DIR}/environment.yml"
LOCK_DIR="${SCRIPT_DIR}/locks"
mkdir -p "$LOCK_DIR"

# ── 默认目标平台 ──
PLATFORMS="${PLATFORMS:-linux-64}"

# ── 参数解析 ──
ACTION="generate"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --all) PLATFORMS="linux-64 osx-64 osx-arm64 win-64"; shift ;;
        --verify) ACTION="verify"; shift ;;
        --cmake) ACTION="cmake-help"; shift ;;
        --install) ACTION="install"; shift ;;
        --platform) PLATFORMS="$2"; shift 2 ;;
        -h|--help)
            grep '^#' "$0" | grep -v '#!/' | sed 's/^# \?//'
            exit 0 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# ── cmake+ninja C扩展编译命令模板 ──
print_cmake_commands() {
    cat <<'CMAKEHELP'
╔══════════════════════════════════════════════════════════════════╗
║  cmake + ninja C 扩展编译命令集（cp314t free-threading ABI）   ║
╚══════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 环境变量配置（必须在编译前设置）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 激活 main 环境（free-threading Python）
conda activate main

# 验证当前 Python 是 free-threading 构建
python -c "import sysconfig; assert sysconfig.get_config_var('Py_GIL_DISABLED')==1; print('Free-threading Python OK')"

# 获取 SOABI 标签（应为 cpython-314t-x86_64-linux-gnu）
export PYTHON_SOABI=$(python -c "import sysconfig; print(sysconfig.get_config_var('SOABI'))")
echo "SOABI: $PYTHON_SOABI"

# 获取 Python 路径和 include 目录
export PYTHON_EXECUTABLE=$(which python)
export PYTHON_INCLUDE_DIR=$(python -c "import sysconfig; print(sysconfig.get_path('include'))")
export PYTHON_LIBRARY=$(python -c "import sysconfig; print(sysconfig.get_config_var('LIBDIR'))")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. cmake 配置命令（标准 C 扩展项目）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

cd <your-project>
mkdir -p build && cd build

cmake .. \
    -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DPython3_EXECUTABLE="$PYTHON_EXECUTABLE" \
    -DPython3_INCLUDE_DIR="$PYTHON_INCLUDE_DIR" \
    -DPython3_FIND_STRATEGY=LOCATION \
    -DPython3_FIND_IMPLEMENTATIONS="CPython" \
    -DCMAKE_C_FLAGS="-O3 -DNDEBUG -fno-semantic-interposition" \
    -DCMAKE_CXX_FLAGS="-O3 -DNDEBUG -fno-semantic-interposition" \
    -DPYTHON_SOABI="$PYTHON_SOABI" \
    -DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. ninja 编译命令
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 编译（使用所有CPU核心）
ninja -j$(nproc)

# 安装到当前环境
ninja install

# 或手动复制 .so 文件到包目录
cp *.so /path/to/your/python/package/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. pybind11 / nanobind 项目专用 cmake 配置
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# pybind11 项目（CMakeLists.txt 中 find_package(pybind11 REQUIRED)）
cmake .. \
    -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DPython3_EXECUTABLE="$PYTHON_EXECUTABLE" \
    -Dpybind11_DIR=$(python -c "import pybind11; print(pybind11.get_cmake_dir())")

# nanobind 项目（CMakeLists.txt 中 find_package(nanobind REQUIRED)）
# 注意：nanobind 对 free-threading 有更好的原生支持
cmake .. \
    -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DPython3_EXECUTABLE="$PYTHON_EXECUTABLE" \
    -Dnanobind_DIR=$(python -c "import nanobind; print(nanobind.cmake_dir())")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. Cython 扩展编译（setuptools + pip 方式，非cmake）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 使用 pip 编译安装（自动适配 free-threading ABI）
pip install --no-build-isolation -v .

# 或使用 setup.py 手动编译
python setup.py build_ext --inplace

# 验证编译产物的 SOABI
find . -name "*.so" -exec python -c "
import sysconfig
expected = sysconfig.get_config_var('SOABI')
import sys
so = sys.argv[1]
if expected in so:
    print(f'OK: {so} -> {expected}')
else:
    print(f'WARN: {so} does not match {expected}')
" {} \;

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6. 验证编译后 C 扩展的 free-threading 兼容性
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# 使用 verify-cext.sh 验证扩展
/usr/local/bin/verify-cext.sh --python "$PYTHON_EXECUTABLE" --expect-soabi "$PYTHON_SOABI" --deep

# 手动验证：扩展可以在 free-threading 模式下导入和运行
python -c "
import your_extension_module
import sysconfig
assert sysconfig.get_config_var('Py_GIL_DISABLED') == 1
print(f'Extension loaded OK on free-threading Python, SOABI={sysconfig.get_config_var(\"SOABI\")}')
"

# 多线程压力测试（验证GIL禁用下不崩溃）
python -c "
import threading, your_extension_module
def worker():
    for _ in range(10000):
        your_extension_module.some_function()
threads = [threading.Thread(target=worker) for _ in range(8)]
[t.start() for t in threads]
[t.join() for t in threads]
print('Multi-thread stress test PASSED')
"

CMAKEHELP
}

# ── 生成锁文件 ──
generate_locks() {
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  conda-lock: 生成精确版本锁文件                            ║"
    echo "╠══════════════════════════════════════════════════════════════╣"
    printf "║  Environment: %-45s║\n" "$ENV_FILE"
    printf "║  Platforms:   %-45s║\n" "$PLATFORMS"
    printf "║  Output dir:  %-45s║\n" "$LOCK_DIR"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""

    # 检查 conda-lock 是否安装
    if ! command -v conda-lock &>/dev/null; then
        echo "[INFO] conda-lock not found, installing via pip..."
        pip install conda-lock --quiet
    fi

    echo "[INFO] conda-lock version: $(conda-lock --version 2>&1 | head -1)"
    echo ""

    # 为每个平台生成锁文件
    for platform in $PLATFORMS; do
        echo ">>> Generating lock for platform: $platform"
        lock_file="${LOCK_DIR}/conda-${platform}.lock"
        conda-lock lock \
            --file "$ENV_FILE" \
            --platform "$platform" \
            --lockfile "$lock_file" \
            2>&1 | tail -5

        if [ -f "$lock_file" ]; then
            line_count=$(wc -l < "$lock_file")
            echo "[OK] Generated: $lock_file ($line_count lines)"
        else
            echo "[FAIL] Failed to generate lock for $platform"
        fi
        echo ""
    done

    echo "[OK] Lock file generation complete!"
    echo ""
    echo "To install from lock file:"
    echo "  conda-lock install --name main ${LOCK_DIR}/conda-linux-64.lock"
    echo "  # or with micromamba:"
    echo "  micromamba create -n main -f ${LOCK_DIR}/conda-linux-64.lock"
}

# ── 验证锁文件 ──
verify_locks() {
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  conda-lock: 验证锁文件 ABI 兼容性                         ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""

    local lock_file="${LOCK_DIR}/conda-linux-64.lock"
    if [ ! -f "$lock_file" ]; then
        echo "[ERROR] Lock file not found: $lock_file"
        echo "Run generate first: bash conda-lock/generate-locks.sh"
        exit 1
    fi

    echo ">>> Checking $lock_file..."
    echo ""

    # 1. 验证 Python 版本和 build string
    echo "[1] Python free-threading (cp314t) check:"
    if grep -q "python-.*cp314t" "$lock_file"; then
        py_line=$(grep "python-3.14" "$lock_file" | head -3)
        echo "  [OK] Found free-threading Python in lock:"
        echo "$py_line" | sed 's/^/       /'
    else
        echo "  [FAIL] No free-threading Python (cp314t) found in lock file!"
        echo "  Make sure environment.yml specifies python=3.14.6=*_cp314t"
    fi
    echo ""

    # 2. 验证 cmake 和 ninja 存在
    echo "[2] Build toolchain check:"
    for tool in cmake ninja; do
        if grep -q "^- ${tool}-" "$lock_file" 2>/dev/null || grep -q "/${tool}-" "$lock_file" 2>/dev/null; then
            echo "  [OK] $tool found in lock"
        else
            echo "  [WARN] $tool not found in lock (may be system package)"
        fi
    done
    echo ""

    # 3. 验证 numpy/pandas 版本（free-threading 兼容要求 numpy≥2.0）
    echo "[3] Free-threading compatible package versions:"
    if grep -q "numpy-2\." "$lock_file" 2>/dev/null; then
        np_ver=$(grep "numpy-2" "$lock_file" | head -1 | grep -oP 'numpy-\K[0-9.]+')
        echo "  [OK] numpy $np_ver (>=2.0 required for free-threading)"
    else
        np_ver=$(grep "numpy-" "$lock_file" | head -1 | grep -oP 'numpy-\K[0-9.]+' || echo "not found")
        echo "  [WARN] numpy $np_ver (>=2.0 required for free-threading support)"
    fi
    echo ""

    # 4. 统计包数量和总大小
    echo "[4] Lock summary:"
    pkg_count=$(grep -c "^#" "$lock_file" 2>/dev/null || echo "?")
    echo "  - Package entries: $(wc -l < "$lock_file") lines"
    echo "  - Lock file size: $(du -h "$lock_file" | cut -f1)"
    echo ""

    echo "[VERIFY COMPLETE]"
}

# ── 从锁文件安装 ──
install_from_lock() {
    local lock_file="${LOCK_DIR}/conda-linux-64.lock"
    if [ ! -f "$lock_file" ]; then
        echo "[ERROR] Lock file not found: $lock_file"
        echo "Run generate first: bash conda-lock/generate-locks.sh"
        exit 1
    fi

    echo "Installing environment from lock file..."

    if command -v micromamba &>/dev/null; then
        echo "Using micromamba..."
        micromamba create -y -n main -f "$lock_file"
    else
        echo "Using conda/mamba..."
        conda-lock install --name main "$lock_file"
    fi

    echo "[OK] Environment installed from lock file!"
}

# ── 主逻辑 ──
case "$ACTION" in
    generate) generate_locks ;;
    verify) verify_locks ;;
    cmake-help) print_cmake_commands ;;
    install) install_from_lock ;;
esac
