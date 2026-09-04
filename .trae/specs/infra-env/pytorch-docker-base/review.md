# PyTorch Docker 基础镜像（Conda 版）- Verification Checklist

## 目录结构与规范
- [ ] apps/pytorch-base/ 目录已创建
- [ ] AGENTS.md 存在且包含"启动协议"关键词
- [ ] .dockerignore 文件存在
- [ ] environment.yml 存在（conda 环境定义）
- [ ] Dockerfile 文件存在
- [ ] entrypoint.sh 文件存在且可执行
- [ ] build.sh 文件存在且可执行
- [ ] wheels/ 目录存在（用于离线 wheel 包）
- [ ] conda-cache/ 目录存在（用于离线 conda 包缓存）
- [ ] README.md 文件存在

## Dockerfile 质量检查
- [ ] Dockerfile 语法正确
- [ ] CPU版本基础镜像明确指定为 ubuntu:26.04（不使用 latest）
- [ ] 每个 RUN 指令末尾有清理 apt 缓存（rm -rf /var/lib/apt/lists/*）
- [ ] apt-get install 使用了 --no-install-recommends
- [ ] pip install 使用了 --no-cache-dir
- [ ] conda 安装后执行 conda clean -ya 清理缓存
- [ ] apt 配置了 Acquire::Retries "5" 重试
- [ ] pip 配置了 --retries 10 --timeout 120
- [ ] wget 配置了 --tries=5 --timeout=60 重试参数
- [ ] 使用了 BuildKit cache mount 缓存 conda pkgs（/opt/conda/pkgs）
- [ ] 使用了 BuildKit cache mount 缓存 pip 下载（/root/.cache/pip）
- [ ] 每个关键阶段有 `=== Stage X/7 ===` 标题输出
- [ ] 关键步骤有 `[BUILD]` 日志输出
- [ ] LABEL 包含 maintainer、description、version 元信息
- [ ] ENV 设置了 DEBIAN_FRONTEND=noninteractive、TZ=Asia/Shanghai、LANG=zh_CN.UTF-8
- [ ] ENV 设置了 CONDA_ENVS_DIRS、CONDA_PKGS_DIRS、PATH 包含 conda
- [ ] Miniconda3 安装到 /opt/conda
- [ ] .condarc 配置了清华 TUNA 镜像源
- [ ] pip.conf 配置了阿里云镜像源和可信主机
- [ ] 创建了名为 pytorch 的 conda 环境，Python 版本为 3.14
- [ ] conda 默认激活 pytorch 环境（/etc/profile.d/、root .bashrc、ai .bashrc）
- [ ] 非 root 用户 ai 被创建（UID 1000），加入 sudo 组，配置 NOPASSWD
- [ ] ai 用户的 .bashrc 正确激活 conda pytorch 环境
- [ ] ENTRYPOINT 使用 tini 作为 init 进程
- [ ] WORKDIR 设置为 /workspace
- [ ] 默认 USER 为 ai（或通过 entrypoint 正确切换）
- [ ] 最后阶段有完整的验证步骤：conda 环境检查、torch 导入、版本打印、张量运算
- [ ] 构建元信息写入 /etc/pytorch-base-build-info 文件
- [ ] 支持 USE_GPU build-arg 切换 GPU 版本
- [ ] 支持 MINICONDA_INSTALLER build-arg 离线安装 Miniconda
- [ ] 支持 CONDA_PKGS_CACHE build-arg 离线 conda 包缓存
- [ ] 支持 WHEEL_DIR build-arg 离线 wheel 安装
- [ ] 支持 PYTORCH_VERSION、TORCHVISION_VERSION、PYTHON_VERSION build-arg 版本配置

## 网络不稳定应对检查
- [ ] apt sources.list 已替换为阿里云镜像（mirrors.aliyun.com/ubuntu）
- [ ] .condarc 已配置清华 TUNA 镜像（mirrors.tuna.tsinghua.edu.cn/anaconda）
- [ ] pip.conf 已配置阿里云镜像（mirrors.aliyun.com/pypi/simple）
- [ ] PyTorch 安装优先使用 conda（通过清华镜像加速）
- [ ] conda 配置了离线模式支持（本地 pkgs 缓存优先）
- [ ] 所有下载命令（wget/curl/pip/conda）都配置了重试参数
- [ ] 单个 RUN 指令中的命令使用 set -eux 和 && 串联，失败立即终止
- [ ] BuildKit cache mount 生效，二次构建时不重新下载已缓存的包

## Conda 环境验证（构建后）
- [ ] `docker run --rm pytorch-base:2.5.1-py314-cpu which conda` 输出 /opt/conda/bin/conda
- [ ] `docker run --rm pytorch-base:2.5.1-py314-cpu conda info --envs` 显示 pytorch 环境且有 * 标记
- [ ] `docker run --rm pytorch-base:2.5.1-py314-cpu python --version` 输出 Python 3.14.x
- [ ] `docker run --rm pytorch-base:2.5.1-py314-cpu which python` 输出 /opt/conda/envs/pytorch/bin/python
- [ ] `docker run --rm pytorch-base:2.5.1-py314-cpu bash -lc "python -c 'import sys; print(sys.executable)'"` 同样指向 pytorch 环境的 python

## 功能验证（构建后）
- [ ] docker build 成功完成，无错误退出
- [ ] `docker run --rm pytorch-base:2.5.1-py314-cpu python -c "import torch; print('PyTorch:', torch.__version__)"` 输出正确的 PyTorch 版本
- [ ] `docker run --rm pytorch-base:2.5.1-py314-cpu python -c "import torchvision; print('torchvision:', torchvision.__version__)"` torchvision 可导入
- [ ] `docker run --rm pytorch-base:2.5.1-py314-cpu python -c "import torchaudio; print('torchaudio:', torchaudio.__version__)"` torchaudio 可导入
- [ ] `docker run --rm pytorch-base:2.5.1-py314-cpu python -c "import torch; x = torch.randn(3,3); print(x @ x.T)"` 张量运算成功
- [ ] `docker run --rm pytorch-base:2.5.1-py314-cpu python -c "import numpy; print('numpy:', numpy.__version__)"` numpy 可用（PyTorch依赖）
- [ ] `docker run --rm pytorch-base:2.5.1-py314-cpu whoami` 默认用户是 ai
- [ ] `docker run --rm pytorch-base:2.5.1-py314-cpu sudo -n whoami` sudo 免密正常工作（输出 root）
- [ ] `docker run --rm pytorch-base:2.5.1-py314-cpu bash -lc "which python && python --version"` ai 用户 login shell 也使用 pytorch 环境
- [ ] `docker run --rm pytorch-base:2.5.1-py314-cpu locale` 显示 LANG=zh_CN.UTF-8
- [ ] `docker run --rm pytorch-base:2.5.1-py314-cpu date` 显示 Asia/Shanghai 时区时间
- [ ] `docker run --rm pytorch-base:2.5.1-py314-cpu pip config get global.index-url` 输出阿里云镜像地址
- [ ] `docker run --rm pytorch-base:2.5.1-py314-cpu conda config --show channels` 显示清华 TUNA 镜像

## 可复用性验证
- [ ] 测试 Dockerfile（FROM pytorch-base:2.5.1-py314-cpu + RUN python -c "import torch; import conda"）构建成功
- [ ] 上层镜像构建时，自动继承 apt 源、conda 源、pip 源配置
- [ ] 上层镜像构建时，conda pytorch 环境已默认激活
- [ ] 上层镜像可以直接使用 ai 用户或切换到 root 运行
- [ ] 上层镜像可以通过 conda install 安装新包，使用清华镜像
- [ ] 镜像 tag 规范：pytorch-base:<version>-py<python-version>-cpu（如 pytorch-base:2.5.1-py314-cpu）

## 构建脚本验证
- [ ] ./build.sh（无参数）构建 CPU 版本，tag 为 pytorch-base:2.5.1-py314-cpu
- [ ] ./build.sh --help 输出清晰的帮助信息
- [ ] ./build.sh --torch-version 2.4.1 可指定 PyTorch 版本构建
- [ ] ./build.sh --python-version 3.12 可指定 Python 版本构建
- [ ] 构建脚本自动启用 DOCKER_BUILDKIT=1
- [ ] 构建脚本完成后自动运行基础验证命令
- [ ] 构建脚本输出最终的运行示例命令

## 离线构建验证（可选）
- [ ] wheels/ 目录下有提前下载的 torch 和 torchvision wheel 文件
- [ ] conda-cache/ 目录下有提前缓存的 conda 包
- [ ] 本地有 Miniconda3 安装包文件
- [ ] ./build.sh --offline 构建成功
- [ ] 离线构建过程中无外部网络访问（可通过断开网络验证）

## GPU 版本验证（需要 nvidia-docker 环境，可选）
- [ ] ./build.sh --gpu 构建成功，tag 为 pytorch-base:2.5.1-py314-gpu-cu124
- [ ] GPU 镜像基于 nvidia/cuda 基础镜像
- [ ] GPU 镜像在支持 nvidia-docker 的环境下运行时 `torch.cuda.is_available()` 返回 True
- [ ] GPU 镜像大小在可接受范围内（解压后≤10GB）

## 镜像体积检查
- [ ] CPU 版本镜像通过 `docker images` 查看，压缩体积≤3GB
- [ ] CPU 版本解压后（容器内 du -sh /）≤5GB
- [ ] conda clean -ya 已执行，无冗余包缓存
- [ ] 无明显的冗余层（如重复的 apt update、未清理的 /tmp 文件）

## 文档检查
- [ ] README.md 包含快速开始命令，可直接复制执行
- [ ] README.md 列出了所有 build-arg 参数及其默认值
- [ ] README.md 列出了 build.sh 所有命令行参数
- [ ] README.md 提供了其他 Dockerfile FROM 引用的示例
- [ ] README.md 包含离线构建步骤说明（如何预下载Miniconda、conda包、wheel）
- [ ] README.md 包含 conda 环境使用说明（如何安装新包、如何切换环境）
- [ ] README.md 包含 GPU 版本说明和 nvidia-docker 要求
- [ ] README.md 中所有示例命令均可执行（无拼写错误）
