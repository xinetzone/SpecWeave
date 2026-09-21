"""offline-delivery 测试夹具（daemon-free，不触 podman / 容器守护进程）。

本目录**不建 Python 包**（无 `__init__.py`、无 `pyproject.toml`），pytest 以 rootdir
方式直接收集；夹具只做路径定位与 product.env 解析，供
`test_release_skeleton.py`（客户交付骨架静态守卫）与
`test_relpack_cli.py`（`bin/relpack*` 静态守卫）共用。
"""

from pathlib import Path

import pytest

# 应用根：tests/ 的上一级（apps/containers/offline-delivery/）
APP_ROOT = Path(__file__).resolve().parents[1]

# 首个产品；CLI 的产品差异（镜像名/Containerfile/wheel glob/骨架目录名）全部来自
# products/<产品>/product.env，测试据此定位而非复制常量。
PRODUCT_NAME = "xmnn-runtime"


@pytest.fixture(scope="session")
def app_root() -> Path:
    """应用根目录（`bin/` 与 `products/` 的父目录）。"""
    return APP_ROOT


@pytest.fixture(scope="session")
def bin_dir(app_root: Path) -> Path:
    """厂商侧 CLI 目录（`bin/relpack` + `bin/lib/*.sh` + `bin/relpack.ps1`）。"""
    return app_root / "bin"


@pytest.fixture(scope="session")
def product_dir(app_root: Path) -> Path:
    """产品目录（`products/xmnn-runtime/`）。"""
    return app_root / "products" / PRODUCT_NAME


@pytest.fixture(scope="session")
def release_dir(product_dir: Path) -> Path:
    """客户交付骨架目录（`products/<产品>/release/`，客户可见契约）。"""
    return product_dir / "release"


@pytest.fixture(scope="session")
def product_env(product_dir: Path) -> dict:
    """解析 `product.env`（`KEY=VALUE` 逐行，值不加引号、不写空格）→ dict。"""
    env = {}
    for line in (product_dir / "product.env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env