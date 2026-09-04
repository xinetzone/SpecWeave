# XMNN 客户运行时镜像 - Verification Checklist

## 目录结构与文件
- [x] xmnn-runtime/ 目录已创建，位置正确（external/chaos/ai/xmnn-runtime/）
- [x] Dockerfile 存在，首行为 `# syntax=docker/dockerfile:1.7-labs`
- [x] build.sh 存在（bash -n语法通过，需chmod +x在使用时执行）
- [x] build.bat 存在，Windows对等版本
- [x] .env.example 存在，包含 APT_MIRROR、CONDA_MIRROR、PIP_MIRROR、BASE_TAG 变量
- [x] .agents/rules/dockerfile.md 存在，记录本变体 Dockerfile 特有规则
- [x] README.md 存在，包含构建、运行、升级说明
- [x] verify-runtime.sh 存在，将被 COPY 到镜像内 /opt/verify-runtime.sh（bash -n语法通过）

## Dockerfile 构建规范（三阶段）
- [x] 正确定义 ARG BASE_TAG=latest、APT_MIRROR、CONDA_MIRROR、PIP_MIRROR
- [x] Stage 1 (runtime-base): FROM devcontainer-base:conda-${BASE_TAG}
- [x] runtime-base FROM 后重新声明所有 ARG
- [x] runtime-base 设置正确 SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]
- [x] runtime-base 设置 LABEL maintainer/description/variant=xmnn-runtime/runtime/excluded
- [x] runtime-base 设置 ENV PATH=/opt/conda/bin:${PATH}
- [x] runtime-base 设置 OpenMP 环境变量（OMP_NUM_THREADS=4、OPENBLAS_NUM_THREADS=1、OMP_WAIT_POLICY=PASSIVE、KMP_DUPLICATE_LIB_OK=TRUE）
- [x] 追加层 1/3（系统层）：安装 tzdata + libgomp1 并配置时区（三层保证）
  - [x] apt-get install -y --no-install-recommends tzdata libgomp1（DEBIAN_FRONTEND=noninteractive）
  - [x] ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
  - [x] echo Asia/Shanghai > /etc/timezone
  - [x] dpkg-reconfigure -f noninteractive tzdata
  - [x] ENV TZ=Asia/Shanghai（final阶段设置，第三层保证）
- [x] 追加层 1/3：初始化计时器文件 /tmp/.xmnn-runtime-build-timer
- [x] 追加层 1/3：输出 [TIMER] 阶段耗时
- [x] 追加层 2/3（pip层）：根据 PIP_MIRROR 参数配置 pip 镜像源（支持aliyun/tuna/bfsu/official）
- [x] 追加层 2/3：输出 [TIMER] 阶段耗时
- [x] Stage 2 (whl-artifacts): FROM xmnn-whl-builder:latest，无 RUN 命令
- [x] Stage 3 (final): FROM runtime-base
- [x] final 阶段 COPY --from=whl-artifacts /opt/xmnn-dist/xmnn-*.whl /tmp/whl/（注意：路径从/builder/dist/修正为/opt/xmnn-dist/）
- [x] final 阶段激活 conda base（source /opt/conda/etc/profile.d/conda.sh && conda activate base）
- [x] final 阶段执行 pip install /tmp/whl/xmnn-*.whl（无 --no-deps，安装所有依赖）
- [x] final 阶段 COPY verify-runtime.sh /opt/verify-runtime.sh 并 chmod +x
- [x] final 阶段内置精简验证（6项Python检查：版本/tvm-vta-xmnn/_libs/ctypes加载/tvm.build计算/.pth）
- [x] final 阶段删除 /tmp/whl/*.whl 减小镜像体积
- [x] final 阶段写入 build-info 到 /etc/devcontainer-variant-xmnn-runtime-build-info
- [x] final 阶段清理：conda clean -ya、pip cache purge、apt clean、rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
- [x] final 阶段设置 ENTRYPOINT []（空数组）
- [x] final 阶段设置 CMD 为打印版本信息的 python 命令
- [x] final 阶段输出 [VALIDATION CHECKPOINT]（12项最终验证）
- [x] final 阶段输出 BUILD TIMING SUMMARY 表
- [x] 每个追加层均输出 [TIMER] 标记

## 运行时功能验证（核心）— 待实际构建验证
- [ ] docker run --rm 镜像 python --version 显示 Python 3.14.x
- [ ] docker run --rm 镜像 python -c "import sys; assert sys.version_info >= (3,14)" 通过
- [ ] docker run --rm 镜像 python -c "import tvm" 无报错
- [ ] docker run --rm 镜像 python -c "import vta" 无报错
- [ ] docker run --rm 镜像 python -c "import xmnn" 无报错
- [ ] _libs 目录存在且包含 libtvm.so 和 libLLVM
- [ ] ctypes.CDLL 加载 libtvm.so（RTLD_GLOBAL）成功
- [ ] tvm.build('llvm') 成功编译向量加倍计算图
- [ ] tvm.build 产物执行计算结果正确
- [ ] /opt/verify-runtime.sh 10项全部PASS

## 排除项验证（不包含构建工具链）— 待实际构建验证
- [ ] which llvm-config 返回空
- [ ] which cmake 返回空
- [ ] which ninja 返回空
- [ ] python -c "import torch" 返回 ModuleNotFoundError

## 基础服务与环境保留 — 待实际构建验证
- [ ] docker --version 正常输出
- [ ] supervisord --version 正常输出
- [ ] 容器内运行 date 显示 CST 时区
- [ ] cat /etc/timezone 输出 Asia/Shanghai
- [ ] echo $TZ 输出 Asia/Shanghai
- [ ] su - devuser -c "python -c 'import xmnn'" 成功

## 升级路径验证 — 待实际构建验证
- [ ] 容器内 pip install whl --force-reinstall 成功
- [ ] pip install 后 import 和 tvm.build 仍正常
- [ ] /opt/verify-runtime.sh 可执行

## 镜像质量与构建脚本 — 静态审查通过，待实际验证
- [x] 构建脚本检查依赖镜像：conda-latest 不存在时给出友好提示
- [x] 构建脚本检查依赖镜像：xmnn-whl-builder:latest 不存在时给出友好提示
- [x] build.bat 包含chcp 65001和对等参数解析
- [ ] 镜像构建过程 exit code 为 0
- [ ] 镜像大小 < 3GB
- [ ] build-info 字段完整
- [ ] bash build.sh 构建成功
- [ ] bash build.sh --cn 构建成功

## README 文档
- [x] 说明镜像用途（客户运行时 vs 开发环境）
- [x] 提供 docker run 完整可复制命令
- [x] 提供升级步骤
- [x] 说明构建前提条件

## 额外修复
- [x] xmnn-whl-builder/Dockerfile 已修复：FINAL阶段保留whl到 /opt/xmnn-dist/ 供下游COPY
