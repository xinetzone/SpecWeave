# Conda 高性能 Dockerfile 模板

三种集成方式的可复制 Dockerfile 模板，配合 [conda-perf-setup.sh](../../scripts/conda-perf-setup.sh) 和 [condarc-performant*.yaml](../../config/condarc/) 使用。

## 模板选择指南

| 模板文件 | 方式 | 复杂度 | 需要复制的文件 | 适用场景 |
|---------|------|--------|--------------|---------|
| `Dockerfile.method-a-static` | A: 静态 YAML | ★☆☆☆☆ | Dockerfile + 1个YAML | 镜像源固定、追求最简配置 |
| `Dockerfile.method-b1-copy` | B1: COPY 脚本 | ★★☆☆☆ | Dockerfile + 1个Shell脚本 | 需要动态切换镜像源、兼容性优先 |
| `Dockerfile.method-b2-bindmount` | B2: BuildKit bind mount | ★★☆☆☆ | Dockerfile + 1个Shell脚本 | **推荐**：零镜像层、需要BuildKit |

## 快速开始（方式 B2，推荐）

```bash
# 1. 创建项目目录
mkdir my-conda-project && cd my-conda-project
mkdir scripts

# 2. 复制模板和脚本
cp /path/to/Dockerfile.method-b2-bindmount Dockerfile
cp /path/to/conda-perf-setup.sh scripts/

# 3. 替换占位符
#    __BASE_IMAGE__     → ubuntu:24.04
#    __MINIFORGE_VER__  → 24.11.3-2
#    __PYTHON_VERSION__ → 3.12
#    __CONDA_PACKAGES__ → numpy pandas jupyterlab
#    __APP_DIR__        → /app

# 4. 构建（国内网络用 tuna 镜像）
DOCKER_BUILDKIT=1 docker build -t my-conda-app \
    --build-arg CONDA_MIRROR=tuna \
    --build-arg CONDA_THREADS=8 .

# 5. 运行
docker run --rm -it my-conda-app python -c "import numpy; print(numpy.__version__)"
```

## 文件来源

需要从 devcontainer-base 项目复制到你的项目中的文件：

| 文件 | 来源路径 | 放置位置（相对 Dockerfile） |
|------|---------|--------------------------|
| YAML 模板（方式A） | `variants/shared/config/condarc/condarc-performant*.yaml` | 与 Dockerfile 同级 |
| 配置脚本（方式B） | `variants/shared/scripts/conda-perf-setup.sh` | `scripts/conda-perf-setup.sh` |

## 核心优化三原则（所有模板内置）

1. **并行 I/O**：`repodata_threads: 8` / `execute_threads: 8`
2. **单次 Solver**：所有包在一次 `mamba create` 中指定
3. **原生 CLI**：使用 `mamba` 而非 `conda --solver=libmamba`

## 详细文档

完整集成指南见 [docs/CONDA-PERF-INTEGRATION-GUIDE.md](../../../docs/CONDA-PERF-INTEGRATION-GUIDE.md)。
