---
id: "caffe-ffi-dockerfile-rules"
title: "Dockerfile 增量构建规范"
source: "AGENTS.md#项目特有约束"
---
# Dockerfile 增量构建规范（caffe-ffi-jupyter）

<a id="基础约定"></a>
## 基础约定

- 文件名为 `Dockerfile`，首行声明 BuildKit 语法：`# syntax=docker/dockerfile:1.7-labs`
- **基础镜像依赖**：`FROM jupyter-ssh-base:1.1`（必须预先构建，build.sh自动检查）
- 构建注释/日志使用**英文**（避免编码问题）
- 启用 `SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]`
- 结构化日志前缀：`[INFO]`/`[OK]`/`[BUILD]`/`[WARN]`/`[ERROR]`
- 关键步骤输出版本验证

## 重要：继承关系

本镜像**继承**jupyter-ssh-base，以下规范**直接复用父镜像**，无需在本Dockerfile中重复定义：
- ✅ supervisord双服务管理（sshd + jupyter）
- ✅ entrypoint.sh（tini init + 密码初始化 + 信号处理 + 命令模式）
- ✅ jupyteruser用户（UID 1000）
- ✅ 中文环境（zh_CN.UTF-8 / Asia/Shanghai）
- ✅ Python虚拟环境 `/opt/venv` 中的Jupyter
- ✅ SSH配置（ED25519、禁用root、host keys启动时生成）
- ✅ 健康检查
- ❌ **不覆盖ENTRYPOINT**：继承父镜像的tini + entrypoint.sh

父镜像规范参考：[../jupyter-ssh-base/.agents/rules/](../jupyter-ssh-base/.agents/rules/)

## 构建上下文

构建上下文**必须为SpecWeave根目录**（`../../`），因为需要COPY caffe-ffi源码：
```
projects/xuanspace/libs/caffe-ffi/
```
build.sh自动从正确的上下文目录执行docker build。

## 构建阶段结构

增量构建在jupyter-ssh-base基础上添加：

1. **Stage 1（系统包）**：安装编译依赖（build-essential, cmake, ninja-build, libopenblas-dev, libprotobuf-dev, protobuf-compiler）
2. **Stage 2（Miniconda）**：安装Miniconda3到 `/opt/conda`，创建caffe-ffi conda环境（Python 3.14）
3. **Stage 3（caffe-ffi编译安装）**：
   - COPY caffe-ffi源码
   - 使用 `pip install --no-build-isolation` 编译安装（必须使用--no-build-isolation！）
   - scikit-build-core自动调用CMake+Ninja
   - SKBUILD_CMAKE_ARGS启用RPATH（CMAKE_INSTALL_RPATH_USE_LINK_PATH=ON）
4. **Stage 4（运行时配置）**：
   - 通过三层机制确保C++扩展动态库可找到：
     1. ENV LD_LIBRARY_PATH包含conda环境lib目录
     2. `/etc/ld.so.conf.d/caffe-ffi.conf`注册site-packages路径 + ldconfig
     3. 编译时RPATH嵌入链接库路径
   - 安装libprotobuf-dev（runtime，版本与builder阶段一致）
   - 注册Jupyter内核（conda环境的ipykernel）到 `/usr/local/share/jupyter/kernels/`
5. **Stage 5（清理）**：卸载编译工具链、清理apt/pip/conda缓存、验证

<a id="安全规范"></a>
## 安全规范

- 继承父镜像：禁止在Dockerfile中硬编码密码/token
- 敏感信息通过环境变量注入
- 构建阶段USER root，最终USER切换回jupyteruser

<a id="非-root-用户规范"></a>
## Conda环境规范

- 环境名：`caffe-ffi`
- 路径：`/opt/conda/envs/caffe-ffi/`
- Python版本：3.14
- 自动激活：通过 `/etc/profile.d/conda.sh` 和 `.bashrc`（仅对jupyteruser的SSH会话）
- 注意：Jupyter运行在/opt/venv中，通过kernel注册发现conda环境

## Jupyter内核注册

在runtime阶段通过以下命令注册conda环境内核到系统级kernel目录：
```bash
source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi && \
python -m ipykernel install --prefix=/usr/local --name "caffe-ffi" --display-name "Python 3.14 (caffe-ffi)"
```
- `--prefix=/usr/local`确保内核安装到 `/usr/local/share/jupyter/kernels/`
- /opt/venv中的Jupyter能自动发现系统级kernel
- 保留父镜像的默认venv内核

## 运行时库路径（三层机制）

caffe-ffi的C++扩展依赖tvm_ffi等动态库，必须通过三层机制确保运行时可找到：

1. **LD_LIBRARY_PATH**：ENV设置包含conda环境lib目录
2. **ld.so.conf.d**：写入tvm_ffi和caffe_ffi的site-packages路径到 `/etc/ld.so.conf.d/caffe-ffi.conf`，执行ldconfig
3. **编译时RPATH**：通过SKBUILD_CMAKE_ARGS设置 `CMAKE_INSTALL_RPATH_USE_LINK_PATH=ON`

## Protobuf版本兼容

runtime阶段安装 `libprotobuf-dev`（不硬编码版本包名），确保apt自动解析与builder阶段一致的protobuf运行时库版本，适配Ubuntu 26.04。

<a id="镜像优化"></a>
## 镜像优化

- 编译完成后卸载编译工具链（build-essential等）
- 清理apt缓存（`rm -rf /var/lib/apt/lists/*`）
- pip安装使用 `--no-cache-dir`
- conda清理（`conda clean -afy`）
- 最终镜像包含：jupyter-ssh-base + Miniconda + caffe-ffi（不含编译工具链）

## 网络容错

- wget配置5次重试/120秒超时
- apt配置5次重试
- 支持国内镜像源（通过 `--cn` 参数）

## WSL构建

所有构建操作必须在WSL2/Linux环境中执行，build.sh包含环境检测警告。

## 验证清单

- [ ] bash scripts/build.sh无错误，构建日志有清晰的Stage标记
- [ ] 基础镜像jupyter-ssh-base:1.1存在时构建成功
- [ ] caffe-ffi可在conda环境中导入：`python -c "import caffe_ffi; print(caffe_ffi.__version__)"`
- [ ] Jupyter内核列表包含"Python 3.14 (caffe-ffi)"
- [ ] SSH和Jupyter双服务正常运行（继承自父镜像）
- [ ] ldconfig验证无错误：`ldconfig -p | grep -E 'tvm|caffe'`
- [ ] C++扩展动态库可解析：`ldd <caffe_ffi_so_path>`无"not found"
- [ ] 容器以jupyteruser用户运行
- [ ] 镜像中不含build-essential/cmake/ninja-build（已卸载）
