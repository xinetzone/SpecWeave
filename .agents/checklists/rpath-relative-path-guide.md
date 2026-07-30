---
title: "RPATH 相对路径计算辅助指南"
date: 2026-07-30
source:
  - .agents/checklists/conda-build-best-practices.md#3-rpath-与共享库处理检查
  - projects/xuanspace/libs/caffe-ffi/conda.recipe/build.sh
tags: [conda-build, RPATH, $ORIGIN, patchelf, shared-library]
status: "✅ 基于caffe-ffi build 5实践验证"
---

# RPATH 相对路径计算辅助指南

> 为什么必须使用相对路径？Conda-build 默认扫描二进制文件中的构建路径，替换为80字符占位符。绝对RPATH路径过长会导致 "Placeholder of length '80' too short" 错误。使用 `$ORIGIN` 相对路径 + `detect_binary_files_with_prefix: false` 是根本解决方案。

---

## 📐 RPATH 层级计算参考图

### Python site-packages 标准布局

理解RPATH计算的前提是清楚conda环境中Python包的标准目录结构：

```
$PREFIX/                              ← Conda 环境根目录
├── lib/                              ← Conda 标准库路径（protobuf, openblas 等系统库）
│   ├── libprotobuf.so
│   ├── libopenblas.so.0
│   └── ...
└── lib/python3.14/
    └── site-packages/                ← Python 包安装目录（$SP_DIR）
        ├── caffe_ffi/                ← 主包目录
        │   ├── __init__.py
        │   ├── _caffe_ffi.so         ← 主扩展 SO（深度 = site-packages + 1）
        │   └── lib/                  ← 主包私有库（预留）
        │       └── ...
        └── tvm_ffi/                  ← 依赖包目录
            ├── __init__.py
            └── lib/
                └── libtvm_ffi.so     ← 依赖 SO（深度 = site-packages + 2）
```

### 相对路径上溯级数速查表

| SO 文件位置 | 相对于 $PREFIX 的深度 | 到 $PREFIX/lib 的上溯级数 | $ORIGIN 相对路径 |
|------------|---------------------|-------------------------|------------------|
| `site-packages/pkg/_ext.so` | 3 (site-packages → python3.14 → lib → PREFIX) | **3级** | `$ORIGIN/../../..` |
| `site-packages/pkg/lib/libpkg.so` | 4 (lib → pkg → site-packages → ...) | **4级** | `$ORIGIN/../../../..` |
| `site-packages/dep/lib/libdep.so` | 4 (lib → dep → site-packages → ...) | **4级** | `$ORIGIN/../../../../` |

**通用计算方法**：从SO所在目录数到PREFIX有多少级`..`，就是上溯级数。

---

## 🗺️ 完整路径解析示意图

### 主扩展 SO 的 RPATH 解析（_caffe_ffi.so）

`_caffe_ffi.so` 位于 `$PREFIX/lib/python3.14/site-packages/caffe_ffi/`，需要能找到：
1. **同目录**的其他SO → `$ORIGIN`
2. **同目录lib子目录**的私有库 → `$ORIGIN/lib`
3. **同级依赖包**的lib目录 → `$ORIGIN/../tvm_ffi/lib`
4. **PREFIX/lib**的系统库 → 上溯3级

```
$ORIGIN = site-packages/caffe_ffi/
    │
    ├── $ORIGIN               → site-packages/caffe_ffi/              (同目录)
    ├── $ORIGIN/lib           → site-packages/caffe_ffi/lib/          (私有库预留)
    │
    ├── $ORIGIN/..            → site-packages/
    │   └── tvm_ffi/lib/      → site-packages/tvm_ffi/lib/            (依赖库)✅
    │
    └── $ORIGIN/../../..      → 逐级上溯：
        │                       1. caffe_ffi/ → site-packages/  (..)
        │                       2. site-packages/ → python3.14/ (../..)
        │                       3. python3.14/ → lib/          (../../..)
        └── lib/              → PREFIX/lib/                         (系统库)✅
```

### 依赖 SO 的 RPATH 解析（libtvm_ffi.so）

`libtvm_ffi.so` 位于 `$PREFIX/lib/python3.14/site-packages/tvm_ffi/lib/`，深度比主SO多一级：

```
$ORIGIN = site-packages/tvm_ffi/lib/
    │
    ├── $ORIGIN               → site-packages/tvm_ffi/lib/           (同目录)
    ├── $ORIGIN/..            → site-packages/tvm_ffi/               (包根目录)
    │
    └── $ORIGIN/../../../../  → 逐级上溯4级：
        │                       1. lib/ → tvm_ffi/          (..)
        │                       2. tvm_ffi/ → site-packages/ (../..)
        │                       3. site-packages/ → python3.14/ (../../..)
        │                       4. python3.14/ → lib/       (../../../..)
        └── lib/              → PREFIX/lib/                         (系统库)✅
```

---

## 💻 标准代码模板

### 模板1：主扩展SO的RPATH修复

```bash
# 定位主扩展SO（优先SP_DIR，回退PREFIX全局查找）
_MAIN_SO=""
if [ -n "${SP_DIR:-}" ] && [ -d "${SP_DIR}/<pkg_name>" ]; then
    _MAIN_SO=$(find "${SP_DIR}/<pkg_name>" -name "_<ext_name>*.so" -type f 2>/dev/null | head -1 || true)
fi
if [ -z "$_MAIN_SO" ]; then
    _MAIN_SO=$(find "${PREFIX}" -name "_<ext_name>*.so" -type f 2>/dev/null | head -1 || true)
fi

if [ -z "$_MAIN_SO" ]; then
    echo "ERROR: Cannot find main extension .so"
    exit 1
fi

echo "Main SO: $_MAIN_SO"

# 设置RPATH（全相对路径！）
# 注意：在bash中$ORIGIN需要转义为\$ORIGIN
if command -v patchelf &>/dev/null; then
    echo "Current RPATH: $(patchelf --print-rpath "$_MAIN_SO" 2>/dev/null || echo '(none)')"

    # 根据实际目录结构调整：
    _MAIN_RPATH="\$ORIGIN"
    _MAIN_RPATH="$_MAIN_RPATH:\$ORIGIN/lib"                                    # 私有库
    _MAIN_RPATH="$_MAIN_RPATH:\$ORIGIN/../<dep_pkg>/lib"                       # 同级依赖包
    _MAIN_RPATH="$_MAIN_RPATH:\$ORIGIN/../../.."                               # PREFIX/lib（上溯3级）

    patchelf --set-rpath "$_MAIN_RPATH" "$_MAIN_SO"
    echo "New RPATH:     $(patchelf --print-rpath "$_MAIN_SO")"
fi
```

### 模板2：依赖SO的RPATH修复（子目录中）

```bash
# 定位依赖SO
_DEP_SO="$SP_DIR/<dep_pkg>/lib/lib<dep_name>.so"

if [ -f "$_DEP_SO" ] && command -v patchelf &>/dev/null; then
    echo "Dep SO: $_DEP_SO"
    echo "Current RPATH: $(patchelf --print-rpath "$_DEP_SO" 2>/dev/null || echo '(none)')"

    # 依赖SO在<pkg>/lib/下，深度多一级：上溯4级
    _DEP_RPATH="\$ORIGIN"
    _DEP_RPATH="$_DEP_RPATH:\$ORIGIN/.."                                        # 包根目录
    _DEP_RPATH="$_DEP_RPATH:\$ORIGIN/../../../../"                              # PREFIX/lib（上溯4级）

    patchelf --set-rpath "$_DEP_RPATH" "$_DEP_SO"
    echo "New RPATH:     $(patchelf --print-rpath "$_DEP_SO")"
fi
```

### 模板3：RPATH和依赖验证

```bash
echo ""
echo "=== RPATH Verification ==="
echo "_caffe_ffi.so RPATH: $(patchelf --print-rpath "$_MAIN_SO")"
echo "libtvm_ffi.so RPATH: $(patchelf --print-rpath "$_DEP_SO")"

# 检查：RPATH中不应包含绝对路径
if patchelf --print-rpath "$_MAIN_SO" | grep -q '/opt/conda\|/usr/'; then
    echo "ERROR: RPATH contains absolute paths!"
    exit 1
fi
echo "✓ No absolute paths in RPATH"

echo ""
echo "=== ldd Verification ==="
ldd "$_MAIN_SO" || true

# 检查：无 "not found" 依赖
if ldd "$_MAIN_SO" 2>&1 | grep -q "not found"; then
    echo "ERROR: Unresolved dependencies!"
    ldd "$_MAIN_SO" | grep "not found"
    exit 1
fi
echo "✓ All dependencies resolved"

# 检查：关键依赖路径正确（从包内lib/解析，而非PREFIX/lib）
_DEP_RESOLVED=$(ldd "$_MAIN_SO" 2>/dev/null | grep lib<dep_name> | awk '{print $3}')
if echo "$_DEP_RESOLVED" | grep -q "<dep_pkg>/lib"; then
    echo "✓ lib<dep_name> correctly resolved to <dep_pkg>/lib/"
else
    echo "WARNING: lib<dep_name> resolved to: $_DEP_RESOLVED (expected <dep_pkg>/lib/)"
fi
```

---

## 🔧 CMake SKBUILD_CMAKE_ARGS 配置

**重要**：`SKBUILD_CMAKE_ARGS` 中也不能使用 `${PREFIX}/lib` 绝对路径作为 `CMAKE_INSTALL_RPATH`。CMake构建时注入的绝对RPATH同样会导致prefix replacement问题。

### 错误配置（含绝对路径）

```bash
# ❌ 错误：${PREFIX}/lib 是绝对路径
export SKBUILD_CMAKE_ARGS="\
-DCMAKE_INSTALL_RPATH=\$ORIGIN:\$ORIGIN/lib:\$ORIGIN/../tvm_ffi/lib:${PREFIX}/lib \
..."
```

### 正确配置（全相对路径）

```bash
# ✅ 正确：使用 $ORIGIN/../../.. 替代 ${PREFIX}/lib
export SKBUILD_CMAKE_ARGS="\
-DCMAKE_INSTALL_RPATH=\$ORIGIN:\$ORIGIN/lib:\$ORIGIN/../tvm_ffi/lib:\$ORIGIN/../../.. \
-DCMAKE_BUILD_RPATH_USE_ORIGIN=ON \
-DCMAKE_SKIP_BUILD_RPATH=OFF \
-DCMAKE_BUILD_WITH_INSTALL_RPATH=ON \
..."
```

### 额外的CMake RPATH选项说明

| 选项 | 值 | 说明 |
|------|-----|------|
| `CMAKE_INSTALL_RPATH` | `$ORIGIN:...` | 安装时的RPATH，必须全相对 |
| `CMAKE_BUILD_RPATH_USE_ORIGIN` | `ON` | 构建阶段也使用`$ORIGIN`相对路径 |
| `CMAKE_SKIP_BUILD_RPATH` | `OFF` | 不跳过构建RPATH（构建时需要能找到依赖） |
| `CMAKE_BUILD_WITH_INSTALL_RPATH` | `ON` | 构建时就使用install RPATH（避免patchelf前的构建产物有绝对路径） |

---

## 📋 meta.yaml 配套配置

仅有RPATH相对路径还不够，meta.yaml中必须同步配置：

```yaml
build:
  number: <N>
  detect_binary_files_with_prefix: false   # 🔴 关键：禁用二进制prefix扫描
  missing_dso_whitelist:
    - "*/lib<dep_name>*.so*"               # 包内自带的库加入白名单
```

**为什么需要 `detect_binary_files_with_prefix: false`？**

- conda-build默认会扫描所有二进制文件中的构建路径
- 它会将构建时的绝对路径替换为占位符（默认80字符）
- 安装时再替换为真实PREFIX路径
- 即使RPATH用了相对路径，如果有其他嵌入路径（debug info等）仍可能触发扫描
- 设置为false明确告诉conda-build：本包不需要路径替换，RPATH全是相对的

---

## ⚠️ 常见陷阱

| 陷阱 | 现象 | 解决方案 |
|------|------|----------|
| RPATH上溯级数算错 | 系统库"not found"，或依赖库从PREFIX/lib解析而非包内lib | 数清楚：SO在site-packages下N级，就需要N个`..` |
| 忘记给依赖SO设置RPATH | 依赖SO自己找不到系统库（虽然主SO能找到依赖SO，但依赖SO的依赖找不到） | **所有**包内SO都需要独立设置RPATH，不只是主扩展 |
| bash中`$ORIGIN`未转义 | RPATH变成空字符串或当前目录（bash变量展开） | 必须用`\$ORIGIN`转义 |
| CMAKE_INSTALL_RPATH含绝对路径 | CMake构建产物自带绝对RPATH，patchelf修复前已触发prefix replacement | SKBUILD_CMAKE_ARGS中也用相对路径 |
| 只patchelf不设meta.yaml | 仍报"Placeholder too short"（其他二进制段含路径） | 同时设置`detect_binary_files_with_prefix: false` |
| 混淆`$ORIGIN`和`${ORIGIN}` | RPATH语法错误 | `$ORIGIN`是动态链接器特殊变量，不是cmake变量，不加`{}` |

---

## 🧪 RPATH调试技巧

### 查看当前RPATH
```bash
patchelf --print-rpath /path/to/lib.so
```

### 查看动态链接器实际搜索过程
```bash
LD_DEBUG=libs python -c "import your_pkg" 2>&1 | grep -E "rpath|searching|found"
```

### 检查RPATH中是否有绝对路径
```bash
patchelf --print-rpath /path/to/lib.so | tr ':' '\n' | grep '^/'
# 无输出 = 全相对路径 ✅
```

### 手动验证RPATH解析
```bash
# 用readelf查看更详细的动态段信息
readelf -d /path/to/lib.so | grep -i rpath
readelf -d /path/to/lib.so | grep -i runpath
```

**注意**：RPATH和RUNPATH的区别：
- **RPATH**：在LD_LIBRARY_PATH之前搜索（优先级高）
- **RUNPATH**：在LD_LIBRARY_PATH之后搜索（优先级低）
- patchelf默认设置的是RUNPATH；如需RPATH用 `--force-rpath` 选项
- Conda环境中一般不需要强制RPATH，RUNPATH即可正常工作

---

## 📁 相关文件

- 最佳实践清单：[conda-build-best-practices.md](file:///d:/spaces/SpecWeave/.agents/checklists/conda-build-best-practices.md#3-rpath-与共享库处理检查)
- caffe-ffi实现参考：[build.sh](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/conda.recipe/build.sh#L273-L303)
