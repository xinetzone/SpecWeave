# DevContainer Base - Conda-LLVM 变体 (LLVM/Clang 工具链)

> 基于 devcontainer-base:conda 变体的 LLVM/Clang 编译工具链镜像，在保留所有基础功能的前提下，通过 conda-forge 预装完整的 LLVM 工具链（llvmdev, clang, clangdev, lld, lldb）以及构建工具（cmake, ninja, make），直接在 conda base 环境安装，开箱即用。

## ✨ 特性

- **基础镜像继承**：完全继承 conda 变体和 devcontainer-base 的所有功能
  - Ubuntu 26.04 + 中文环境 zh_CN.UTF-8 + Asia/Shanghai 时区
  - SSH(22) + Docker DinD(2375) + Podman(rootless) + Jupyter(8888)
  - supervisord 进程管理，devuser 非 root 用户 (UID 1000)
  - Miniconda3 安装在 `/opt/conda`
- **LLVM 工具链**：LLVM/Clang 22.1.8，统一版本通过 conda-forge 安装
  - `llvmdev`, `clangdev`, `clang`, `lld`, `lldb`
- **构建工具**：`cmake`, `ninja`, `make` 最新版本（conda-forge）
- **PATH 设计**：`/opt/conda/bin` 在 PATH 最前面，llvm-config/clang/cmake/ninja 直接可用
- **开箱即用**：无需手动激活 conda，所有编译工具直接在 PATH 中
- **服务稳定**：Jupyter 等服务由 supervisord 用绝对路径启动，不受 PATH 变更影响
- **国内镜像支持**：支持清华 TUNA conda 镜像、阿里云/清华 pip 镜像

## 📦 包含组件

| 组件 | 版本 | 说明 |
|------|------|------|
| LLVM | 22.1.8 | llvmdev 核心库 + 头文件 |
| Clang | 22.1.8 | C/C++/Objective-C 编译器 |
| Clang Tools Extra | 22.1.8 | clang-tidy, clang-format 等 |
| lld | 22.1.8 | LLVM 链接器 |
| lldb | 22.1.8 | LLVM 调试器 |
| CMake | latest | 跨平台构建系统 |
| Ninja | latest | 快速构建系统 |
| Make | latest | GNU Make |

## 📁 目录结构

```
variants/conda-llvm/
├── Dockerfile              # Conda-LLVM 变体构建文件（4个追加阶段）
├── .env.example            # 构建参数配置模板
├── README.md               # 本文件
└── .agents/
    └── rules/
        └── dockerfile.md   # Dockerfile 规范说明
```

## 🚀 构建

### 前置条件

需要先构建基础镜像和 conda 变体：

```bash
# 在 devcontainer-base 根目录
cd /path/to/devcontainer-base

# 1. 构建基础镜像
bash scripts/build.sh --cn

# 2. 构建 conda 变体
bash variants/build.sh --variant conda --cn
```

### 使用构建脚本（推荐）

```bash
# 在 devcontainer-base 根目录执行
bash variants/build.sh --variant conda-llvm

# 使用国内镜像源构建（推荐中国网络环境）
bash variants/build.sh --variant conda-llvm --cn

# 构建后验证
bash variants/build.sh --variant conda-llvm --cn --verify
```

### 手动 docker build

```bash
# 在 devcontainer-base 根目录执行
# 标准构建
docker build -f variants/conda-llvm/Dockerfile \
  -t devcontainer-base:conda-llvm-latest .

# 国内镜像源构建
docker build -f variants/conda-llvm/Dockerfile \
  --build-arg APT_MIRROR=aliyun \
  --build-arg CONDA_MIRROR=tuna \
  --build-arg PIP_MIRROR=aliyun \
  -t devcontainer-base:conda-llvm-latest .

# 指定 LLVM 版本
docker build -f variants/conda-llvm/Dockerfile \
  --build-arg LLVM_VERSION=22.1.8 \
  -t devcontainer-base:conda-llvm-22.1.8 .
```

## 🐳 运行

### DinD 模式（推荐开发环境）

```bash
docker run -d \
  --name devcontainer-conda-llvm \
  --privileged \
  -p 2222:22 \
  -p 2375:2375 \
  -p 8888:8888 \
  -v $(pwd)/workspace:/workspace \
  -v docker-storage:/var/lib/docker \
  -e USER_PASSWORD=devpass \
  -e JUPYTER_TOKEN=mysecret \
  -e GRANT_SUDO=yes \
  devcontainer-base:conda-llvm-latest
```

### 命令模式（调试/一次性编译任务）

```bash
# 进入容器交互模式
docker run -it --rm --privileged devcontainer-base:conda-llvm-latest bash

# 直接在容器内编译测试
docker run --rm -v $(pwd):/workspace -w /workspace \
  devcontainer-base:conda-llvm-latest \
  bash -c "clang++ --std=c++17 hello.cpp -o hello && ./hello"
```

## 🔧 工具使用说明

### PATH 优先级说明

**conda-llvm 变体中，`/opt/conda/bin` 在 PATH 最前面**，因此：
- `llvm-config`, `clang`, `clang++`, `cmake`, `ninja`, `make` 直接可用
- `python` 和 `pip` 默认指向 conda base 环境的 Python
- 系统 venv `/opt/venv/bin` 的 Python 仍可通过绝对路径 `/opt/venv/bin/python` 访问
- **Jupyter 服务不受影响**：supervisord 使用 `/opt/venv/bin/jupyter` 绝对路径启动

### 快速验证工具链

```bash
# 检查所有工具版本
llvm-config --version
clang --version
clang++ --version
cmake --version
ninja --version
make --version
lld --version
```

### 编译 C++ 项目

```bash
# Hello World 示例
cat > hello.cpp << 'EOF'
#include <iostream>
int main() {
    std::cout << "Hello from LLVM/Clang!\n";
    return 0;
}
EOF

# 使用 clang++ 编译
clang++ --std=c++17 hello.cpp -o hello
./hello
```

### 使用 CMake + Ninja 构建

```bash
# 典型 CMake 项目构建流程
mkdir build && cd build
cmake -G Ninja -DCMAKE_BUILD_TYPE=Release ..
ninja -j$(nproc)
```

### 使用 llvm-config 获取编译参数

```bash
# 获取 LLVM 包含路径
llvm-config --includedir

# 获取 LLVM 库路径
llvm-config --libdir

# 获取链接 LLVM 所需的库
llvm-config --libs core orcjit native

# 获取编译标志
llvm-config --cxxflags
```

### 切换回系统 venv Python（如需要）

```bash
# 临时使用系统 venv 的 Python
/opt/venv/bin/python --version
/opt/venv/bin/pip --version

# 或修改 PATH 临时切换
export PATH=/opt/venv/bin:$PATH
which python  # 现在指向 /opt/venv/bin/python

# 永久切换：编辑 ~/.bashrc 将 /opt/venv/bin 放在前面
echo 'export PATH=/opt/venv/bin:$PATH' >> ~/.bashrc
```

### 使用原始 conda-init.sh（不激活 base）

如果需要原始 conda 变体的行为（不自动激活），仍可使用：

```bash
# 重置 PATH 到 conda 变体默认状态（venv 优先）
source /etc/profile.d/conda-init.sh
# 注意：这不会自动 conda activate base
```

## ✅ 验证命令

```bash
# 验证 LLVM 版本
docker run --rm devcontainer-base:conda-llvm-latest llvm-config --version
# 期望输出: 22.1.8

# 验证 Clang 版本
docker run --rm devcontainer-base:conda-llvm-latest clang --version
# 期望输出: clang version 22.1.8

# 验证 CMake 可用
docker run --rm devcontainer-base:conda-llvm-latest cmake --version

# 验证 Ninja 可用
docker run --rm devcontainer-base:conda-llvm-latest ninja --version

# 验证 Jupyter 服务仍可用（绝对路径）
docker run --rm devcontainer-base:conda-llvm-latest /opt/venv/bin/jupyter --version

# 验证 Docker 可用
docker run --rm --privileged devcontainer-base:conda-llvm-latest docker --version

# 验证 C++ 编译
docker run --rm devcontainer-base:conda-llvm-latest bash -c 'echo "#include <iostream>" > /tmp/test.cpp && echo "int main(){std::cout<<\"OK\"<<std::endl;return 0;}" >> /tmp/test.cpp && clang++ --std=c++17 /tmp/test.cpp -o /tmp/test && /tmp/test'
# 期望输出: OK

# 查看构建信息
docker run --rm devcontainer-base:conda-llvm-latest cat /etc/devcontainer-variant-conda-llvm-build-info
```

## ⚙️ 构建参数说明

| 参数 | 默认值 | 说明 |
|------|-------|------|
| `BASE_TAG` | `latest` | conda 基础镜像标签 |
| `APT_MIRROR` | `official` | APT 源：official/aliyun/tuna |
| `CONDA_MIRROR` | `tuna` | Conda 源：tuna（清华）/official（官方） |
| `PIP_MIRROR` | `aliyun` | PyPI 源：aliyun（阿里云）/tuna（清华）/official |
| `LLVM_VERSION` | `22.1.8` | LLVM/Clang 统一版本号 |

## 📋 关键路径

| 路径 | 说明 |
|------|------|
| `/opt/conda/bin` | Conda base 环境 bin 目录（在 PATH 最前） |
| `/opt/conda` | Miniconda3 安装根目录 |
| `/opt/venv` | 系统 Python venv（服务使用，绝对路径访问） |
| `/etc/profile.d/conda-init.sh` | 原始 conda 激活脚本（不自动激活） |
| `/etc/profile.d/conda-llvm-init.sh` | Conda-LLVM 备选激活脚本 |
| `/etc/devcontainer-variant-conda-llvm-build-info` | 构建元数据 |

## ⚠️ 注意事项

1. **PATH 优先级**：conda-llvm 变体中 `/opt/conda/bin` 在 PATH 最前面，这与 conda 变体不同。这是为了让 LLVM/Clang 工具链开箱即用。默认 `python` 是 conda base 环境的 Python。

2. **服务不受影响**：Jupyter、SSH、Docker 等服务由 supervisord 使用绝对路径启动，因此不受 PATH 顺序变更影响，始终使用系统 venv 的 Python 运行。

3. **base 环境安装**：所有 LLVM 工具直接安装在 conda base 环境中，没有创建新环境，简化使用。如需隔离环境，可以自行 `conda create -n myenv`。

4. **版本一致性**：所有 LLVM 相关包（llvmdev, clangdev, clang, lld, lldb）统一锁定到 `${LLVM_VERSION}`，避免版本不匹配问题。

5. **编译缓存**：Dockerfile 使用 BuildKit cache 挂载 `/opt/conda/pkgs`，重复构建时可大幅加速 conda 包下载和安装。

6. **如需使用系统 venv Python**：请使用绝对路径 `/opt/venv/bin/python` 或 `/opt/venv/bin/pip`，或在 `~/.bashrc` 中调整 PATH 顺序。

## 🔗 相关镜像

- [devcontainer-base](../../README.md) - 基础镜像（SSH + Docker + Podman + Jupyter）
- [conda variant](../conda/README.md) - Conda 基础变体（Miniconda3，venv 优先）
