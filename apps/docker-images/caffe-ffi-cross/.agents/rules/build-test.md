---
id: "caffe-ffi-cross-build-test-rules"
title: "构建与测试流程"
source: "build.sh + run.sh + docker-compose.yml"
---
# 构建与测试流程（caffe-ffi-cross）

## 重要说明

本项目是**纯交叉编译构建镜像**，无运行时服务（SSH/Jupyter等）。镜像用于在Linux环境中交叉编译macOS( osx-64 )和Windows( win-64 )的conda包。

## 构建命令速查

### macOS交叉编译镜像

```bash
# 默认构建（official源）
bash build.sh

# 使用国内镜像源
bash build.sh --mirror tuna

# 跳过macOS SDK下载（运行时挂载）
bash build.sh --skip-sdk

# 自定义镜像名
bash build.sh --mirror aliyun
```

### Windows交叉编译镜像

```bash
# 构建Windows交叉编译镜像
docker build -f Dockerfile.win-cross -t caffe-ffi-cross-win:latest .

# 跳过Wine安装
docker build --build-arg SKIP_WINE=1 -f Dockerfile.win-cross -t caffe-ffi-cross-win:latest .

# 使用国内镜像源
docker build --build-arg APT_MIRROR=tuna --build-arg CONDA_MIRROR=tuna \
  -f Dockerfile.win-cross -t caffe-ffi-cross-win:latest .
```

### macOS交叉编译脚本参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--mirror` | official | 镜像源：tuna/aliyun/official |
| `--skip-sdk` | 关 | 跳过SDK下载，运行时挂载 |
| `--help/-h` | - | 显示帮助 |

## 运行交叉编译

```bash
# macOS交叉编译（挂载源码和输出目录）
docker run --rm \
  -v /path/to/caffe-ffi:/workspace/caffe-ffi \
  -v $(pwd)/output:/output \
  caffe-ffi-cross-macos:latest

# 如果构建时跳过了SDK，运行时挂载
docker run --rm \
  -v /path/to/MacOSX11.3.sdk:/opt/MacOSX11.3.sdk \
  -v /path/to/caffe-ffi:/workspace/caffe-ffi \
  -v $(pwd)/output:/output \
  caffe-ffi-cross-macos:latest

# Windows交叉编译
docker run --rm \
  -v /path/to/caffe-ffi:/workspace/caffe-ffi \
  -v $(pwd)/output:/output \
  caffe-ffi-cross-win:latest
```

## Docker Compose

```bash
# 使用docker-compose启动
docker compose up -d

# 查看日志
docker compose logs -f
```

## 验证

```bash
# 验证macOS交叉编译器
docker run --rm caffe-ffi-cross-macos:latest \
  x86_64-apple-darwin13.4.0-clang --version

# 验证conda-build
docker run --rm caffe-ffi-cross-macos:latest \
  conda build --version

# 验证输出产物格式（Mach-O for macOS）
file output/*/osx-64/*.conda 2>/dev/null || file output/*/osx-64/*.tar.bz2

# 验证Windows输出（PE32+ for Windows）
file output/*/win-64/*.conda 2>/dev/null || file output/*/win-64/*.tar.bz2
```

## 常见问题排查

| 问题 | 排查命令 | 常见原因 |
|------|---------|---------|
| SDK下载超时 | 查看构建日志 | 网络不稳定，使用--skip-sdk构建后运行时挂载 |
| conda-forge包安装慢 | 查看conda安装日志 | 使用--mirror tuna使用清华源 |
| 交叉编译器找不到 | `which x86_64-apple-darwin13.4.0-clang` | conda环境未激活，检查ENV PATH设置 |
| Wine安装失败 | 查看Stage 2日志 | 使用SKIP_WINE=1跳过，L3测试非必须 |
| conda build报错 | 查看conda build输出 | 检查meta.yaml或conda_build_config.yaml配置 |
