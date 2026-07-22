---
id: "python-native-extension-self-contained-wheel"
title: "Python原生扩展Wheel自包含打包模式"
type: code-pattern
date: 2026-07-22
maturity: L2 可复用
maturity_note: "已在XMNN/TVM/VTA项目完整验证（9个捆绑系统库、Nuitka编译、RPATH自包含），打包产物在python:slim干净容器中验证通过"
source: "../../reports/task-reports/retrospective-xmnn-nuitka-docker-deployment-20260722/README.md"
related_patterns:
  - "compiled-wheel-runtime-image-build.md"
  - "python-implicit-dependency-detection.md"
  - "shared-lib-symbol-dual-layer-control.md"
  - "direct-file-write-over-shell-pipe.md"
  - "../methodology-patterns/governance-strategy/implement-review-harden-sop.md"
tags: ["python", "wheel", "nuitka", "cmake", "scikit-build-core", "ninja", "rpath", "patchelf", "ldd", "shared-library", "self-contained", "native-extension", "docker", "quality-gate"]
validation_count: 1
reuse_count: 0
---

# Python原生扩展Wheel自包含打包模式

## 概述

将含 C/C++ 原生扩展（Nuitka/Cython/CFFI/pybind11等编译产物）的 Python 项目打包为**自包含 wheel**：wheel 内部捆绑所有非系统共享库依赖，通过 RPATH=$ORIGIN 实现库的相对路径加载，最终 wheel 可在最小化基础镜像（如 `python:slim`）中直接 `pip install` 后正常运行，无需携带完整构建环境。

**核心成果**：XMNN项目 wheel 体积 101MB（压缩）/ 529MB（解压），含 3 个 Nuitka 编译的核心 `.so` 模块和 9 个捆绑系统库，在 `python:3.14-slim-bookworm` 容器中安装导入全部通过。

## 触发场景

- 使用 **Nuitka**、**Cython**、**CFFI**、**pybind11** 等工具编译 Python 扩展为 `.so`
- 项目链接了 **C/C++ 第三方库**（LLVM、OpenCV、CUDA runtime、protobuf 等）
- 需要将打包产物分发给**没有构建环境**的最终用户（pip install 即用）
- 运行时镜像希望使用**最小化基础镜像**（`python:slim`/`distroless`）而非携带完整 conda 环境
- 需要**保护 Python 源码**（通过编译为机器码 `.so`）
- 构建工具链使用 **scikit-build-core + CMake + Ninja** 组合

**识别信号**：
- 在开发机上 `import` 正常，但在干净环境/Docker中 `ImportError: libxxx.so: cannot open shared object file`
- `ldd` 显示 `.so` 依赖 `/opt/conda/envs/xxx/lib/` 下的非系统库
- 构建环境路径被硬编码进 ELF 的 RPATH/RUNPATH
- wheel 安装后需要手动设置 `LD_LIBRARY_PATH` 才能运行

**不适用场景**：
- 纯 Python 包（无 C 扩展）→ 标准 wheel 打包即可
- CUDA 依赖（需 CUDA runtime/driver 兼容）→ 建议用 CUDA 基础镜像而非捆绑
- 静态链接所有依赖的项目（无动态库依赖）→ 无需此模式
- 依赖 JDK/特定语言 runtime 的项目 → 需在基础镜像层面解决

## 与现有模式的关系

| 模式 | 策略 | 镜像体积 | 适用阶段 |
|------|------|---------|---------|
| **compiled-wheel-runtime-image-build (L1)** | 用构建镜像作为运行时基础镜像 | 大（1GB+，含完整 conda 环境） | 开发期/内部部署 |
| **本模式 (L2 自包含)** | 捆绑非系统依赖 + RPATH=$ORIGIN | 小（仅含 wheel + 捆绑库，~500MB） | 对外分发/生产部署 |

**推荐演进路径**：先用 L1 模式快速跑通，再按本模式升级为自包含 wheel。

## 问题本质

### 动态链接的传递性问题

C/C++ 编译的 `.so` 文件通过动态链接器（`ld.so`）解析依赖时，存在**传递性依赖链**：

```
libtvm.so
├── libLLVM-19.so.1      ← conda 环境中的非系统库
│   ├── libffi.so.8      ← libLLVM 的依赖
│   ├── libxml2.so.2     ← libLLVM 的依赖
│   │   └── libicuuc.so.74
│   └── libzstd.so.1
├── libstdc++.so.6       ← 系统库（基础镜像自带）
└── libc.so.6            ← 系统库（glibc）
```

仅仅把 `libtvm.so` 放进 wheel 是不够的——它的所有**非系统间接依赖**都必须存在，且能在运行时被找到。

### RPATH 硬编码陷阱

编译时链接器通常将**构建环境的库路径**写入 ELF 的 RUNPATH：

```bash
$ readelf -d libtvm.so | grep RUNPATH
0x0000001d (RUNPATH) Library runpath: [/opt/conda/envs/tvm-build/lib]
```

当 wheel 安装到 `/usr/local/lib/python3.14/site-packages/tvm/` 时，这个路径不存在 → `ImportError`。

## 解决方案架构

### 整体流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    构建阶段（有完整 conda 环境）                   │
├─────────────────────────────────────────────────────────────────┤
│  1. Nuitka 编译 Python → C → .so                                │
│  2. CMake + Ninja 编译 C++ 原生库（libtvm.so 等）                 │
│  3. scikit-build-core 组装 wheel                                │
│  4. ★ 依赖捆绑（核心步骤）：                                     │
│     a. ldd 递归扫描所有 .so 的非系统依赖                          │
│     b. 复制依赖库到 wheel 内 tvm/_libs/ 目录                      │
│     c. patchelf 设置 RPATH=$ORIGIN                               │
│  5. 更新 wheel RECORD 文件（哈希校验）                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    运行阶段（最小化镜像）                          │
├─────────────────────────────────────────────────────────────────┤
│  pip install xmnn-*.whl                                         │
│    ↓                                                           │
│  1. 安装 Python 依赖（numpy/scipy等，通过 pip 声明）             │
│  2. .so 文件就位，RPATH=$ORIGIN 指向 _libs/ 目录                 │
│  3. ld.so 通过 $ORIGIN 找到捆绑的依赖库                          │
│  4. import tvm / vta / xmnn 正常工作                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    质量门禁（流水线末尾）                         │
├─────────────────────────────────────────────────────────────────┤
│  verify_wheel.py 在 python:slim 容器中自动验证：                │
│  ✅ pip install 无错误                                          │
│  ✅ 核心模块导入（tvm/vta/xmnn）                                 │
│  ✅ 所有公开 API 可访问                                         │
│  ✅ Nuitka 编译产物为 .so（无源码泄露）                          │
│  ✅ 捆绑库存在（tvm/_libs/*.so）                                 │
│  ✅ RPATH=$ORIGIN（自包含验证）                                  │
│  ✅ 基本功能可运行（relay 计算图构建）                           │
└─────────────────────────────────────────────────────────────────┘
```

## 核心实现步骤

### 步骤1：项目构建配置

使用 scikit-build-core 作为 build backend，配合 CMake + Ninja：

```toml
# pyproject.toml
[build-system]
requires = ["scikit-build-core>=0.9", "cmake>=3.28", "ninja>=1.11"]
build-backend = "scikit_build_core.build"

[project]
name = "your-package"
version = "1.0.0"
requires-python = ">=3.13"
dependencies = [
    "numpy>=2.0",
    # 声明所有 Python 级别的依赖
]

[tool.scikit-build]
cmake.build-type = "Release"
cmake.generator = "Ninja"
wheel.packages = ["your_package"]
```

### 步骤2：Nuitka 编译配置

```python
# nuitka 编译命令（在打包脚本中）
nuitka_cmd = [
    sys.executable, "-m", "nuitka",
    "--module",
    "--include-package=your_package",
    "--include-module=required_dynamic_module",  # 动态导入的模块
    "--output-dir=nuitka_build",
    "--lto",  # 链接时优化
    "--remove-output",
    "your_package/__init__.py",
]
```

**关键注意**：Nuitka 无法自动发现**动态导入**的模块（如 `importlib.import_module()` 调用），必须通过 `--include-module`/`--include-package` 显式声明。

### 步骤3：依赖捆绑脚本（核心）

这是整个模式的关键步骤。在 CMake install 后、wheel 打包前执行：

```python
import subprocess
import re
import os
import shutil
import hashlib
import csv
import zipfile
from pathlib import Path

def get_system_library_prefixes():
    """返回系统库路径前缀（这些库不需要捆绑）"""
    return (
        '/lib/', '/usr/lib/', '/lib64/', '/usr/lib64/',
        '/lib/x86_64-linux-gnu/', '/usr/lib/x86_64-linux-gnu/',
    )

def get_deps(so_path: str) -> dict[str, str]:
    """递归获取 .so 文件的所有非系统依赖
    
    使用 ldd 分析直接依赖，过滤掉系统库（glibc, libm, libpthread 等），
    返回 {库名: 绝对路径} 的字典。
    """
    try:
        result = subprocess.run(
            ['ldd', so_path], capture_output=True, text=True, timeout=30
        )
        deps = {}
        for line in result.stdout.splitlines():
            # 匹配格式: libfoo.so.1 => /path/to/libfoo.so.1 (0x...)
            m = re.match(r'\s*(\S+)\s*=>\s*(\S+)\s*\(0x[0-9a-f]+\)', line)
            if m:
                lib_name, lib_path = m.groups()
                if lib_path.startswith(get_system_library_prefixes()):
                    continue
                if os.path.exists(lib_path):
                    real_path = os.path.realpath(lib_path)
                    deps[lib_name] = real_path
        return deps
    except Exception as e:
        print(f'  Warning: ldd failed for {so_path}: {e}')
        return {}

def recursive_deps(so_paths: list[str]) -> dict[str, str]:
    """递归收集所有依赖（包括间接依赖）
    
    BFS 遍历依赖图，避免重复和循环引用。
    """
    all_deps = {}
    queue = list(so_paths)
    visited = set()

    while queue:
        so_path = queue.pop(0)
        if so_path in visited:
            continue
        visited.add(so_path)
        
        if not os.path.isabs(so_path):
            continue
            
        direct_deps = get_deps(so_path)
        for name, path in direct_deps.items():
            if name not in all_deps:
                all_deps[name] = path
                queue.append(path)
    
    return all_deps

def bundle_and_patch(wheel_unpacked: Path):
    """捆绑依赖库并设置 RPATH
    
    1. 找到 wheel 中所有 .so 文件
    2. 递归收集非系统依赖
    3. 复制到 tvm/_libs/ 目录
    4. 用 patchelf 设置 RPATH=$ORIGIN
    5. 更新 RECORD 文件
    """
    libs_dir = wheel_unpacked / "tvm" / "_libs"
    libs_dir.mkdir(parents=True, exist_ok=True)

    # 1. 找到所有 .so 文件
    so_files = list(wheel_unpacked.rglob("*.so"))
    
    # 2. 递归收集依赖
    all_deps = recursive_deps([str(f) for f in so_files])
    
    # 3. 复制依赖库到 _libs
    for lib_name, lib_path in all_deps.items():
        dest = libs_dir / lib_name
        if not dest.exists():
            shutil.copy2(lib_path, dest)
            # 复制符号链接目标（处理 .so -> .so.1 -> .so.1.0 链）
            real_path = Path(lib_path).resolve()
            real_dest = libs_dir / real_path.name
            if real_path != Path(lib_path) and not real_dest.exists():
                shutil.copy2(real_path, real_dest)
    
    # 4. patchelf 设置 RPATH
    all_sos = so_files + list(libs_dir.glob("*.so*"))
    for so in all_sos:
        subprocess.run(
            ['patchelf', '--set-rpath', '$ORIGIN', str(so)],
            check=True, capture_output=True, timeout=10
        )
        # 对于 _libs 目录下的库，$ORIGIN 指向自身目录
        if str(so).startswith(str(libs_dir)):
            subprocess.run(
                ['patchelf', '--set-rpath', '$ORIGIN', str(so)],
                check=True, capture_output=True, timeout=10
            )
    
    # 5. 更新 RECORD 文件
    update_record(wheel_unpacked)

def update_record(wheel_unpacked: Path):
    """更新 wheel 的 RECORD 文件
    
    patchelf 修改 .so 后，文件哈希和大小变化，必须更新 RECORD。
    RECORD 是 CSV 格式，每行: 路径,sha256=hash,size
    """
    dist_info = list(wheel_unpacked.glob("*.dist-info"))[0]
    record_path = dist_info / "RECORD"
    
    rows = []
    if record_path.exists():
        with open(record_path, 'r', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and len(row) >= 1:
                    file_path = row[0]
                    # 跳过捆绑目录和被修改的 .so（稍后重新计算）
                    full_path = wheel_unpacked / file_path
                    if full_path.exists():
                        rows.append(row)
    
    # 重新计算所有捆绑库的哈希
    for so_file in wheel_unpacked.rglob("*.so*"):
        rel_path = so_file.relative_to(wheel_unpacked).as_posix()
        h = hashlib.sha256(so_file.read_bytes()).digest()
        import base64
        hash_str = "sha256=" + base64.urlsafe_b64encode(h).rstrip(b'=').decode()
        size = so_file.stat().st_size
        
        # 替换已有记录或添加新记录
        found = False
        for i, row in enumerate(rows):
            if row[0] == rel_path:
                rows[i] = [rel_path, hash_str, str(size)]
                found = True
                break
        if not found:
            rows.append([rel_path, hash_str, str(size)])
    
    with open(record_path, 'w', newline='') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerows(rows)
```

**Python-in-Shell-Heredoc 注意**：如果将上述脚本嵌入 shell 的 heredoc 中，需要注意字符串转义：
- Python 源码中的 `\n` 需要写为 `\\n`（shell 转义）
- 使用独立的 `.py` 文件而非内联可以避免此问题
- 参考 `direct-file-write-over-shell-pipe.md` 模式：优先写文件而非 shell 内联

### 步骤4：.pth 文件设置环境变量

对于需要环境变量的组件（如 VTA 的硬件配置路径），使用 `.pth` 文件做包级自初始化：

```python
# site-packages/_xmnn_init.py
import os

# 设置 TVM 库路径（指向 wheel 内的 _libs）
_pkg_dir = os.path.dirname(__file__)
_libs_dir = os.path.join(_pkg_dir, 'tvm', '_libs')

# 设置 VTA 硬件路径
os.environ.setdefault("VTA_HW_PATH", os.path.join(_pkg_dir, 'vta'))

# 将 _libs 加入 LD_LIBRARY_PATH
if os.path.isdir(_libs_dir):
    current = os.environ.get("LD_LIBRARY_PATH", "")
    if _libs_dir not in current:
        os.environ["LD_LIBRARY_PATH"] = (
            f"{_libs_dir}:{current}" if current else _libs_dir
        )
```

```python
# site-packages/xmnn_init.pth（每行一条 Python 语句，import 时执行）
import _xmnn_init
```

**为什么用 .pth 而不是 ENV**：
- `.pth` 在 Python 解释器启动时自动执行，无需用户设置环境变量
- 路径是相对于包安装位置的，跨机器/环境通用
- 不依赖 Dockerfile 的 ENV 指令或 shell profile

### 步骤5：声明 Python 依赖

在 pyproject.toml 中完整声明运行时依赖，**不要遗漏隐式导入**：

```toml
dependencies = [
    "numpy>=2.0",
    "scipy>=1.11",       # tvm.relay.quantize.kl_divergence 隐式依赖 scipy.stats
    "ml_dtypes>=0.4",
    "typing_extensions>=4.5",
    "Pillow>=10.0",
    "psutil>=5.9",
    "cloudpickle>=2.2",
    "attrs>=23.1",
]

[project.optional-dependencies]
onnx = ["onnx>=1.14", "onnxruntime>=1.16"]
pytorch = ["torch>=2.0", "torchvision", "packaging"]
tensorflow = ["tensorflow"]
infer = ["pandas", "tqdm", "tomlkit"]
report = ["matplotlib", "openpyxl"]
rpc = ["tornado"]
deploy = ["telnetlib3", "protobuf"]
all = ["xmnn[onnx,pytorch,tensorflow,infer,report,rpc,deploy]"]
```

**隐式依赖发现方法**：
1. 用 `grep -r "^import\|^from" --include="*.py" | grep -v __pycache__` 扫描所有顶层 import
2. 注意 `try/except ImportError` 保护的可选导入
3. 特别留意顶层导入链中出现的第三方库（如 `tvm.relay.quantize` 模块顶层 `from scipy.stats import entropy`）

## 质量门禁：干净环境自动验证

打包完成后必须在干净环境中验证，不能假设"在构建环境能 import 就行"。

### 验证脚本架构

```
verify_wheel.py（流水线脚本）
├── 自动查找 packaging/dist/ 下最新 wheel
├── docker run python:3.14-slim（完全干净）
│   ├── pip install <wheel>（安装 wheel 本身）
│   └── python verify_import.py（运行验证检查）
│       ├── 核心模块导入（tvm/vta/xmnn）
│       ├── XMNN APIs 可用性
│       ├── Nuitka 编译产物检查（.so 存在、无 .py 源码泄露）
│       ├── 捆绑库检查（tvm/_libs/ 目录）
│       ├── RPATH=$ORIGIN 验证（readelf 检查）
│       ├── 核心依赖导入（numpy/scipy等）
│       └── 基本功能测试（relay 计算图构建）
└── 输出 PASS/FAIL + JSON 报告
```

### 使用方式

```bash
# 开发验证
python verify_wheel.py

# CI/CD 流水线（严格模式 + JSON 输出）
python verify_wheel.py --strict --json --output verify-report.json

# 指定 wheel 和 Python 版本
python verify_wheel.py --wheel packaging/dist/xmnn-1.2.2-*.whl --python 3.13

# 失败时保留容器调试
python verify_wheel.py --keep-container --verbose
```

### Invoke 集成

```python
# tasks.py
from invoke import task

@task
def verify(c):
    """干净环境验证 wheel（质量门禁）"""
    c.run("python verify_wheel.py --strict", pty=True)

@task(post=[verify])
def nuitka(c):
    """Nuitka 编译打包并验证"""
    c.run("python src/xmpack/wheel.py", pty=True)
```

## 检验清单（Checklist）

自包含 wheel 打包完成后，逐项确认：

### 依赖完整性
- [ ] `ldd` 所有 `.so` 文件，输出中**没有** "not found"
- [ ] 非系统依赖库**全部**在 wheel 内的 `tvm/_libs/` 目录中
- [ ] 系统库（libc, libm, libpthread, libstdc++, libgomp, libdl, ld-linux）**未**被捆绑（它们属于基础镜像）
- [ ] Python 依赖**全部**在 pyproject.toml 的 dependencies 中声明

### RPATH 正确性
- [ ] `readelf -d <wheel内.so> | grep RUNPATH` 显示 `[$ORIGIN]`
- [ ] `_libs/` 目录内的共享库也设置了 `$ORIGIN`（它们互相依赖）
- [ ] 运行时**不需要**设置 `LD_LIBRARY_PATH`（由 .pth 文件兜底设置即可）

### 功能验证
- [ ] 在 `python:slim` 容器中 `pip install` 无错误
- [ ] `import tvm; import vta; import xmnn` 成功
- [ ] `from xmnn import compile_api, infer_api, ...` 所有 API 可导入
- [ ] Nuitka 编译的模块确实是 `.so` 文件（非 `.py` 源码）
- [ ] 基本功能测试通过（如构建简单 relay 计算图）

### RECORD 文件
- [ ] RECORD 文件中包含所有捆绑库的条目（路径+sha256+大小）
- [ ] `pip install` 时无 RECORD hash mismatch 警告
- [ ] `pip check` 无依赖冲突

## 反模式（不要这么做）

### ❌ 反模式1：只捆绑直接依赖，遗漏间接依赖

- **错误**：只把 `ldd libtvm.so` 直接列出的库复制进去
- **后果**：运行时报 `libicuuc.so not found`——libLLVM 的依赖没被捆绑
- **正确做法**：递归 BFS 遍历依赖图，收集所有非系统依赖

### ❌ 反模式2：先复制再 patchelf，但忘记更新 RECORD

- **错误**：patchelf 修改 .so 后直接 zip 打包
- **后果**：`pip install` 时 `hash mismatch` 警告或安装失败
- **正确做法**：patchelf 之后必须重新计算所有修改文件的 sha256 并更新 RECORD

### ❌ 反模式3：RPATH 设置为绝对路径

- **错误**：`patchelf --set-rpath /opt/xmnn/libs libtvm.so`
- **后果**：wheel 安装到不同路径时库找不到
- **正确做法**：永远使用 `$ORIGIN`（相对于 .so 文件自身位置）

### ❌ 反模式4：在构建环境中验证通过就认为 OK

- **错误**：打包后在开发机/conda 环境中 `import` 成功就发布
- **后果**：用户安装后缺依赖——因为开发环境有完整的 conda 库路径
- **正确做法**：必须在**全新的最小化容器**中验证（`python:slim`）

### ❌ 反模式5：捆绑系统库（libc, libstdc++ 等）

- **错误**：把 `/lib/x86_64-linux-gnu/libc.so.6` 也复制进 wheel
- **后果**：版本冲突、符号未定义、段错误
- **正确做法**：只捆绑 conda/pip 安装的非系统第三方库（libLLVM, libxml2, libicu 等）

### ❌ 反模式6：Python 脚本内联到 shell heredoc 中

- **错误**：`RUN python -c "..."` 中写复杂的依赖分析逻辑
- **后果**：`\n` 转义错误、字符串展开问题、调试困难
- **正确做法**：将 Python 逻辑写入独立 `.py` 文件，在 Dockerfile/shell 中调用

## 迁移示例

### 场景1：XMNN/TVM/VTA Nuitka 编译（本项目，源案例）✅

- **编译工具**：Nuitka + CMake + Ninja + scikit-build-core
- **捆绑库**：9个（libLLVM-19, libxml2, libicuuc, libicui18n, libicudata, libzstd, liblzma, libtinfo, libffi）
- **验证**：`python:3.14-slim-bookworm` 容器中全量验证通过
- **产物**：101MB wheel → `pip install` 即装即用

### 场景2：OpenCV Python 自包含 wheel（推断，待验证）

- **编译工具**：scikit-build-core + OpenCV C++ 编译
- **预期捆绑库**：libpng, libjpeg, libtiff, libwebp, libopenjp2 等
- **系统库例外**：libGL, libglib2.0（可能需要安装系统包或捆绑）
- **验证方法**：相同流程，在 python:slim 中验证 `import cv2`

### 场景3：pybind11 C++ 扩展项目（推断，待验证）

- **编译工具**：pybind11 + CMake + scikit-build-core
- **典型依赖**：项目自有 C++ 库、可能依赖 Eigen/Boost 等 header-only 库（无需捆绑）
- **特殊考虑**：如果依赖 Boost 等 header-only 库，静态链接即可，无动态依赖问题
- **验证方法**：检查 ldd 输出，确认无非系统动态依赖

### 场景4：Cython 编译的科学计算库（推断，待验证）

- **编译工具**：Cython + setuptools/scikit-build
- **典型依赖**：可能依赖 OpenBLAS/LAPACK 等数学库
- **特殊考虑**：OpenBLAS 体积大（~30MB），且可能有系统级优化；可选择捆绑或让用户自行安装
- **验证方法**：在 numpy+scipy 基础的 slim 镜像中验证

## 常见问题排查

### Q: 验证时报 `version 'GLIBCXX_3.4.32' not found`

**原因**：捆绑的库（如 libLLVM）编译时链接了新版本 libstdc++，但基础镜像的 libstdc++ 过旧。

**解决**：
1. 升级基础镜像（如 `bookworm` → `trixie/sid`），或
2. 不要捆绑需要新版 libstdc++ 的库，改用较旧版本的依赖编译，或
3. 在运行时镜像中安装新版 libstdc++（`apt install libstdc++6`）

### Q: 验证时报 `undefined symbol`

**原因**：RPATH 设置正确，但库版本不匹配（如 libxml2 的符号在捆绑的版本中不存在）。

**解决**：确保捆绑的库与编译时链接的是**完全相同**的文件（使用 `os.path.realpath()` 解析符号链接）。

### Q: wheel 安装后 `ModuleNotFoundError`（Python 模块）

**原因**：Python 依赖未在 pyproject.toml 中声明，或 Nuitka 未包含动态导入模块。

**解决**：
1. 检查缺失的模块，添加到 pyproject.toml dependencies
2. 如果是动态导入，在 Nuitka 命令中添加 `--include-module=xxx`

### Q: `pip install` 时报 RECORD hash mismatch

**原因**：patchelf 修改 .so 文件后未更新 RECORD 文件的哈希值。

**解决**：确保在 patchelf 之后重新计算所有受影响文件的 sha256 并写入 RECORD。注意：
- csv.writer 使用 `lineterminator='\n'`（Unix 行尾）
- sha256 使用 base64 URL-safe 编码，去掉末尾 `=`
- 包含 _libs 目录下的所有新文件

### Q: macOS/Windows 兼容性如何？

**当前状态**：本模式在 Linux x86_64 验证通过。其他平台差异：
- **macOS**：使用 `otool -L` 替代 `ldd`，使用 `install_name_tool` 替代 `patchelf`，`@loader_path` 替代 `$ORIGIN`
- **Windows**：使用 `dumpbin /DEPENDENTS` 或 `Dependencies` 工具，DLL 搜索路径机制不同（PATH 或同级目录）
- **待验证**：需要额外适配工作，欢迎贡献

## 工具链版本参考

XMNN 项目验证使用的工具版本：

| 工具 | 版本 | 说明 |
|------|------|------|
| Python | 3.14 | 目标运行时版本 |
| Nuitka | 2.4+ | Python→C 编译 |
| CMake | 3.28+ | C/C++ 构建系统 |
| Ninja | 1.11+ | 快速构建后端 |
| scikit-build-core | 0.9+ | Python build backend |
| patchelf | 0.18+ | RPATH 修改工具 |
| Docker | 24+ | 干净环境验证 |
| base image | python:3.14-slim-bookworm | 验证基础镜像 |

## 参考文件

本模式的参考实现位于 XMNN 项目中：

- 打包脚本核心逻辑：`src/xmpack/wheel.py`（依赖捆绑、patchelf、RECORD 更新）
- 项目配置：`packaging/pyproject.toml`
- 验证脚本：`verify_wheel.py`（流水线质量门禁）
- 容器内验证：`packaging/verify_import.py`
- Dockerfile：`docker/Dockerfile.runtime`（多阶段构建）
- 部署脚本：`docker/deploy.sh`（一键构建+验证+部署）

## Changelog

- **2026-07-22** (v2.0.0): 从 XMNN Nuitka 打包+Docker 部署完整复盘萃取，成熟度从 L1 升级到 L2。新增自包含 wheel 策略（RPATH=$ORIGIN + 依赖捆绑）、质量门禁验证脚本、隐式依赖发现方法、反模式清单，更新与 compiled-wheel-runtime-image-build 的关系说明。
