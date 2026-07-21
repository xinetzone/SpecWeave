---
id: "python-package-version-standard-api"
source: "../../reports/bug-fix/docker-build/retrospective-conda-build-fix-20260721/README.md"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/python-package-version-standard-api.toml"
---
# Python包版本验证：importlib.metadata 标准API

## 模式概述

验证Python包版本时，统一使用标准库 `importlib.metadata.version()` 函数，而非访问模块的 `__version__` 属性。PEP 396（Module Version Attributes）仅为Informational状态，从未成为强制标准；在Python 3.14+及使用PEP 517/518/621新构建后端（setuptools≥61、scikit-build-core、hatchling等）的包中，`__version__` 属性可能不存在，导致AttributeError。`importlib.metadata.version()` 从包的分发元数据中读取版本，不依赖模块是否注入 `__version__`，是跨版本、跨构建后端兼容的标准方式。

## 问题现象

Docker构建中使用 `python -c "import X; print(X.__version__)"` 验证包安装时，新版 `typing_extensions` 报：

```
AttributeError: module 'typing_extensions' has no attribute '__version__'
```

在 `set -eux` 的Docker RUN层中，此AttributeError导致shell退出码1，整个构建层失败。包实际上已成功安装，但验证探针脚本出错导致构建中止。

反模式代码：
```dockerfile
# ❌ 反模式：__version__ 非标准属性，在新构建后端下可能不存在
RUN python -c "import numpy; print('numpy:', numpy.__version__)"
RUN python -c "import ml_dtypes; print('ml_dtypes:', ml_dtypes.__version__)"
RUN python -c "import typing_extensions; print('typing_extensions:', typing_extensions.__version__)"
RUN python -c "import nuitka; print('nuitka:', nuitka.__version__)"  # nuitka CLI包，import名不同
```

## 解决方案：importlib.metadata.version() 标准模板

### Dockerfile 验证命令模板

```dockerfile
# ✅ 正确：使用 importlib.metadata.version() 标准API
RUN set -eux; \
    python -c "from importlib.metadata import version; print('numpy:', version('numpy'))"; \
    python -c "from importlib.metadata import version; print('ml_dtypes:', version('ml_dtypes'))"; \
    python -c "from importlib.metadata import version; print('typing_extensions:', version('typing-extensions'))"; \
    python -c "from importlib.metadata import version; print('nuitka:', version('Nuitka'))"
```

### 关键注意事项：分发包名 vs import名

`importlib.metadata.version()` 的参数是**分发包名（PyPI name）**，而非import名。两者可能不同：

| import名 | 分发包名（PyPI） | 说明 |
|----------|----------------|------|
| `typing_extensions` | `typing-extensions` | 下划线→连字符 |
| `nuitka` | `Nuitka` | 大小写差异 |
| `PIL` | `Pillow` | 完全不同 |
| `cv2` | `opencv-python` | 完全不同 |
| `sklearn` | `scikit-learn` | 缩写差异 |
| `yaml` | `PyYAML` | 前缀差异 |
| `google.protobuf` | `protobuf` | 命名空间包 |

**判断方法**：以 `pip install <name>` 使用的名称为准。

### Python脚本中的版本验证工具函数

```python
# ✅ 安全的版本验证函数
from importlib.metadata import version, PackageNotFoundError

def verify_package(package_name: str, min_version: str | None = None) -> str:
    """验证包已安装并返回版本号。

    Args:
        package_name: 分发包名（PyPI name，非import名）
        min_version: 最低版本要求（可选）

    Returns:
        版本字符串

    Raises:
        RuntimeError: 包未安装或版本不满足要求
    """
    try:
        ver = version(package_name)
    except PackageNotFoundError:
        raise RuntimeError(f"Package '{package_name}' is not installed") from None

    if min_version is not None:
        from packaging.version import Version
        if Version(ver) < Version(min_version):
            raise RuntimeError(
                f"Package '{package_name}' version {ver} < required {min_version}"
            )

    return ver

# 使用示例
numpy_ver = verify_package("numpy", "1.26.0")
typing_ext_ver = verify_package("typing-extensions")
pillow_ver = verify_package("Pillow")
```

### 批量验证Shell函数

```bash
# ✅ Shell中批量验证包版本
verify_packages() {
    python - "$@" <<'PYEOF'
import sys
from importlib.metadata import version, PackageNotFoundError

failed = False
for pkg in sys.argv[1:]:
    try:
        print(f"  {pkg}: {version(pkg)}")
    except PackageNotFoundError:
        print(f"  {pkg}: NOT INSTALLED", file=sys.stderr)
        failed = True

sys.exit(1 if failed else 0)
PYEOF
}

# 使用
verify_packages numpy ml_dtypes typing-extensions Nuitka
```

## 适用场景

### 必须使用本模式的场景

1. **Dockerfile包验证**：在 `set -e` 环境下验证conda/pip包安装
2. **CI/CD安装验证**：GitHub Actions/GitLab CI中验证依赖安装
3. **安装脚本/healthcheck**：部署脚本和健康检查中的依赖验证
4. **跨Python版本项目**：需支持Python 3.8-3.14多个版本
5. **使用新构建后端的包**：typing_extensions、pydantic、rich等使用hatchling/scikit-build-core的包

### Python版本兼容性

| Python版本 | importlib.metadata | importlib_metadata 回填 |
|:---------:|:-----------------:|:----------------------:|
| 3.8+ | 标准库内置 | 不需要 |
| 3.7及以下 | 不可用 | `pip install importlib_metadata`，`from importlib_metadata import version` |

> 本项目目标Python 3.14，可直接使用标准库。

## 反模式

### 反模式1：假设所有包都有 __version__

```python
# ❌ PEP 396不是强制标准，新构建后端不再自动注入__version__
import typing_extensions
print(typing_extensions.__version__)  # AttributeError
```

### 反模式2：用 import 名查 metadata

```python
# ❌ import名≠分发名，typing_extensions是import名，分发包名是typing-extensions
version("typing_extensions")  # PackageNotFoundError
version("nuitka")             # PackageNotFoundError（应为Nuitka）
version("PIL")                # PackageNotFoundError（应为Pillow）
```

### 反模式3：pkg_resources（已废弃）

```python
# ❌ pkg_resources已废弃，启动慢且在setuptools新版本中逐步移除
import pkg_resources
ver = pkg_resources.get_distribution("numpy").version
```

### 反模式4：pip show 解析输出

```dockerfile
# ❌ 解析CLI输出脆弱，pip版本变化可能改变输出格式
RUN pip show numpy | grep Version | awk '{print $2}'
```

## 迁移验证（G3）

本模式可迁移到以下非当前领域场景：

- **Node.js**：`require('pkg').version` 读取package.json的version字段，但也有包不暴露version属性；标准方式是 `require('pkginfo')` 或读取package.json
- **Rust**：`env!("CARGO_PKG_VERSION")` 编译期注入，比Python可靠，但build.rs生成的包需用其他方式
- **Go**：`runtime/debug.ReadBuildInfo()` 读取模块版本，类似importlib.metadata
- **Java**：`Package.getPackage("x").getImplementationVersion()` 读取MANIFEST.MF，类似metadata但常被打包工具遗漏；标准方式是Maven/Gradle生成version类
- **npm CLI验证**：`node -e "console.log(require('pkg/package.json').version)"` 是Node.js生态的等价"标准API"

跨领域共性原则：**从分发元数据读取版本，不要从运行时对象读取**。

## 与其他模式的关系

- **被 compiled-wheel-runtime-image-build 使用**：wheel运行时镜像的包验证步骤依赖本模式
- **被 python-implicit-dependency-detection 使用**：依赖检测中的版本验证需使用标准API
- **与 defensive-attribute-access 互补**：如果必须使用 `__version__`（如某些特殊场景），应配合防御性属性访问
- **与 exception-precision-guards 相关**：捕获PackageNotFoundError而非裸except

## 成熟度

L2 已验证（2次成功案例：typing_extensions.__version__修复 + nuitka/Nuitka大小写问题修复）
