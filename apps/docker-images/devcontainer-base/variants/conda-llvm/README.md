# DevContainer Base - Conda-LLVM 变体 (LLVM/Clang 工具链)

> 直接基于 devcontainer-base 基础镜像的 LLVM/Clang 编译工具链变体，在保留所有基础功能的前提下，通过 conda-forge 在 **conda main 环境**（Python 3.14.6 cp314t free-threading，默认用户环境）预装 LLVM 工具链（llvmdev, clangdev, clang, lld）与构建工具（cmake, ninja, make），开箱即用。
>
> 历史变更：本变体曾基于 conda 变体（base 环境安装），自 2026-08 起直接基于 `devcontainer-base:${BASE_TAG}`，工具链迁移至 main 环境并与默认用户环境（Python 3.14t free-threading）保持一致；conda 变体已从构建注册表移除。

## ✨ 特性

- **基础镜像继承**：完全继承 devcontainer-base 的所有功能
  - Ubuntu 26.04 + 中文环境 zh_CN.UTF-8 + Asia/Shanghai 时区
  - SSH(22) + Docker DinD(2375) + Podman(rootless) + Jupyter(8888)
  - supervisord 进程管理，devuser 非 root 用户 (UID 1000)
  - Miniforge3（conda-forge 官方发行版，libmamba solver）安装于 `/opt/conda`
- **main 环境安装**：LLVM 工具链安装于 conda **main 环境**（Python 3.14.6 cp314t free-threading，默认用户环境），编译工具与默认 Python/Jupyter 共享同一环境
- **LLVM 工具链**：LLVM/Clang 22.1.8，统一版本通过 conda-forge 安装
  - `llvmdev`, `clangdev`, `clang`, `lld`（版本锁定）
  - `lldb` **已排除**（conda-forge 无 cp314t 构建，安装会引发 GIL 回归，见注意事项）
- **构建工具**：`cmake`, `ninja`, `make` 最新版本（conda-forge）
- **GCC 运行时**：`libgcc`, `libstdcxx-ng`（conda-forge clang 链接器必需，缺失会导致 `cannot find -lgcc`）
- **free-threading 防线**：python 显式锁定 `*=*cp314t` 构建 + 安装后断言 `sys._is_gil_enabled() == False`，任何包引发的 GIL 回归会使构建立即失败
- **PATH 设计**：`/opt/conda/envs/main/bin` 在 PATH 最前面，llvm-config/clang/cmake/ninja 与 Python 3.14t/Jupyter 直接可用
- **服务稳定**：Jupyter 等服务由 supervisord 启动，使用 main 环境的绝对路径，不受 PATH 变更影响
- **国内镜像支持**：conda 源支持 bfsu（默认）/tuna/aliyun/official 四种

## 📦 包含组件

| 组件 | 版本 | 说明 |
|------|------|------|
| LLVM | 22.1.8 | llvmdev 核心库 + 头文件 |
| Clang | 22.1.8 | C/C++/Objective-C 编译器 |
| lld | 22.1.8 | LLVM 链接器 |
| lldb | - | **已排除**（见注意事项 3） |
| CMake | latest | 跨平台构建系统 |
| Ninja | latest | 快速构建系统 |
| Make | latest | GNU Make |
| libgcc / libstdcxx-ng | latest | GCC 运行时库（clang 链接器依赖） |

> 注 1：`clang-tools-extra` 包在 conda-forge 通道不存在，已从安装列表移除。
> 注 2：`lldb` 因 python 绑定无 cp314t（free-threading）构建被排除，详见注意事项。
> 注 3：组件实际版本以容器内 `/etc/devcontainer-variant-conda-llvm-build-info` 为准。

## 📁 目录结构

```
variants/conda-llvm/
├── Dockerfile              # Conda-LLVM 变体构建文件（4个追加阶段）
├── .env.example            # 构建参数配置模板
├── README.md               # 本文件
├── RELEASE.md              # 镜像发布清单（版本矩阵/验证结果/变更记录）
├── RELEASE-GUIDE.md        # 发布操作指南（构建/验证/发布/回滚）
├── DEPENDENCIES.md         # 依赖说明（依赖链/系统依赖/工具链包/升级指引）
└── .agents/
    └── rules/
        └── dockerfile.md   # Dockerfile 规范说明
```

## 🚀 构建

### 前置条件

需要先构建基础镜像（conda 变体已下线，无需中间变体）：

```bash
# 在 devcontainer-base 根目录
cd /path/to/devcontainer-base

# 1. 构建基础镜像（V2 内置默认镜像源）
bash scripts/build.sh --cn
```

### 使用构建脚本（推荐）

```bash
# 在 devcontainer-base 根目录执行
bash variants/build.sh --variant conda-llvm

# 国内镜像源构建（推荐中国网络环境）
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
  --build-arg CONDA_MIRROR=bfsu \
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

**conda-llvm 变体中，`/opt/conda/envs/main/bin` 在 PATH 最前面**，因此：
- `llvm-config`, `clang`, `clang++`, `cmake`, `ninja`, `make` 直接可用
- `python` 和 `pip` 默认指向 conda main 环境的 **Python 3.14.6（cp314t free-threading，GIL 默认禁用）**
- `jupyter` 同样来自 main 环境
- **Jupyter 服务不受影响**：supervisord 使用 main 环境绝对路径启动

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

# 验证 free-threading Python（默认环境）
python --version                       # Python 3.14.6
python -c "import sys; print(sys._is_gil_enabled())"   # False（GIL 已禁用）
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

### Conda 环境说明

- 工具链与默认 Python 均位于 **main 环境**（`/opt/conda/envs/main`），登录 shell 自动激活（`/etc/profile.d/conda-init.sh`）
- 备选激活脚本：`/etc/profile.d/conda-llvm-init.sh`（同样激活 main 环境，向后兼容保留）
- base 环境仅保留 conda 自身运行时（无 cp314t 构建），不建议在其上安装工具链
- 如需隔离环境，可自行 `conda create -n myenv`

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

# 验证默认 Python 为 free-threading 构建（main 环境）
docker run --rm devcontainer-base:conda-llvm-latest \
  bash -c 'python --version && python -c "import sys; print(sys._is_gil_enabled())"'
# 期望输出: Python 3.14.6 / False

# 验证 Jupyter 服务仍可用（main 环境绝对路径）
docker run --rm devcontainer-base:conda-llvm-latest /opt/conda/envs/main/bin/jupyter --version

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
| `BASE_TAG` | `latest` | 基础镜像标签（直接基于 devcontainer-base，无中间变体） |
| `APT_MIRROR` | `official` | APT 源：official/aliyun/tuna |
| `CONDA_MIRROR` | `bfsu` | Conda 源：bfsu（北外，默认）/tuna（清华）/aliyun（阿里云）/official（官方） |
| `PIP_MIRROR` | `aliyun` | PyPI 源：aliyun（阿里云）/tuna（清华）/official |
| `LLVM_VERSION` | `22.1.8` | LLVM/Clang 统一版本号 |

## 📋 关键路径

| 路径 | 说明 |
|------|------|
| `/opt/conda/envs/main/bin` | main 环境 bin 目录（PATH 最前：LLVM 工具 + Python 3.14t + Jupyter） |
| `/opt/conda` | Miniforge3 安装根目录 |
| `/opt/conda/envs/main` | main 环境（默认用户环境，Python 3.14.6 cp314t） |
| `/etc/profile.d/conda-init.sh` | 基础镜像默认激活脚本（激活 main 环境） |
| `/etc/profile.d/conda-llvm-init.sh` | Conda-LLVM 备选激活脚本（激活 main 环境） |
| `/etc/devcontainer-variant-conda-llvm-build-info` | 构建元数据 |

## ⚠️ 注意事项

1. **PATH 优先级**：conda-llvm 变体中 `/opt/conda/envs/main/bin` 在 PATH 最前面。默认 `python` 是 main 环境的 Python 3.14.6（cp314t free-threading）。

2. **free-threading 运行时**：main 环境 Python 为 cp314t 构建，GIL 默认禁用（`sys._is_gil_enabled()` 返回 `False`）。构建期有两道防线：python 显式锁定 `*=*cp314t` 构建 + 安装后 GIL 状态断言，任何包试图引入 GIL 构建的 python 都会使构建失败。

3. **lldb 不可用**：`lldb` 的 python 绑定在 conda-forge 上没有 cp314t（free-threading）构建，安装 lldb 会使求解器静默将 python 从 `cp314t` 切换为 `cp314 + python-gil`（GIL 回归）。因此 lldb 被排除在安装列表之外；如需调试器，建议在独立环境（非 main）中安装，避免污染 free-threading 运行时。

4. **服务不受影响**：Jupyter、SSH、Docker 等服务由 supervisord 使用 main 环境绝对路径启动，不受 PATH 顺序变更影响。

5. **版本一致性**：所有 LLVM 相关包（llvmdev, clangdev, clang, lld）统一锁定到 `${LLVM_VERSION}`，避免版本不匹配问题。

6. **GCC 运行时依赖**：conda-forge 的 clang 链接器（`x86_64-conda-linux-gnu-ld`）需要 `-lgcc`/`-lstdc++`，故必须安装 `libgcc`/`libstdcxx-ng`；镜像清理时静态库删除对 `libgcc*`/`libstdc++*` 豁免，否则用户编译会报 `cannot find -lgcc`。

7. **编译缓存**：Dockerfile 使用 BuildKit cache 挂载 `/opt/conda/pkgs`，重复构建时可大幅加速 conda 包下载和安装。

## 🔗 相关镜像

- [devcontainer-base](../../README.md) - 基础镜像（SSH + Docker + Podman + Jupyter + Miniforge3）

## 📄 相关文档

- [镜像发布清单](./RELEASE.md) - 版本矩阵、验证结果、变更记录
- [发布操作指南](./RELEASE-GUIDE.md) - 构建/验证/发布/回滚全流程
- [依赖说明](./DEPENDENCIES.md) - 依赖链、系统/工具链依赖、升级指引
