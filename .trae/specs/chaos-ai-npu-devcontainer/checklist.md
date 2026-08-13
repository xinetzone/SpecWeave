# Chaos AI NPU DevContainer - Verification Checklist

## 目录结构与基础文件
- [ ] Checkpoint 1: `external/chaos/ai/` 目录已创建
- [ ] Checkpoint 2: `external/chaos/ai/scripts/` 子目录已创建
- [ ] Checkpoint 3: `.env.example` 存在且包含 BASE_TAG/APT_MIRROR/CONDA_MIRROR/PIP_MIRROR 配置
- [ ] Checkpoint 4: `build.sh` 存在且可执行（chmod +x）
- [ ] Checkpoint 5: `build.bat` 存在（Windows便捷脚本）
- [ ] Checkpoint 6: `Dockerfile` 存在
- [ ] Checkpoint 7: `README.md` 存在且包含完整使用说明
- [ ] Checkpoint 8: `scripts/verify-deployment.py` 存在
- [ ] Checkpoint 9: `scripts/chaos-ai-init.sh` 存在

## Dockerfile 规范
- [ ] Checkpoint 10: Dockerfile syntax 指令为 `# syntax=docker/dockerfile:1.7-labs`
- [ ] Checkpoint 11: FROM 正确引用 `devcontainer-base:onnx-quantized-${BASE_TAG}`
- [ ] Checkpoint 12: SHELL 设置为 `["/bin/bash", "-e", "-o", "pipefail", "-c"]`
- [ ] Checkpoint 13: LABEL 包含 variant="chaos-ai-npu"、maintainer、description
- [ ] Checkpoint 14: ENV CONDA_DIR=/opt/conda，PATH 以 /opt/conda/bin 开头
- [ ] Checkpoint 15: OpenMP 环境变量已设置（OMP_NUM_THREADS/OPENBLAS_NUM_THREADS/KMP_DUPLICATE_LIB_OK）
- [ ] Checkpoint 16: 3层追加架构完整（Stage1基础验证/Stage2安装依赖/Stage3配置+冒烟测试）
- [ ] Checkpoint 17: 每层都有 [TIMER] 计时输出和阶段标记
- [ ] Checkpoint 18: Stage2 使用 BuildKit cache 挂载（/opt/conda/pkgs、/root/.cache/pip）
- [ ] Checkpoint 19: 创建挂载点目录 /workspace/npu_tvm、/workspace/npuusertools、/workspace/models
- [ ] Checkpoint 20: COPY 入口脚本到 /etc/profile.d/chaos-ai-init.sh
- [ ] Checkpoint 21: 写入 /etc/devcontainer-variant-chaos-ai-npu-build-info 元数据
- [ ] Checkpoint 22: 每层结束有清理（conda clean/pip cache purge/apt-get clean/rm -rf /tmp/*）
- [ ] Checkpoint 23: ENTRYPOINT 为空（继承base的空ENTRYPOINT）
- [ ] Checkpoint 24: 保留所有基础服务（sshd/dockerd/jupyter/supervisord），不破坏supervisord配置

## XMNN 依赖安装
- [ ] Checkpoint 25: apt 安装 patchelf（如果base没有的话）
- [ ] Checkpoint 26: pip 安装 scikit-build-core
- [ ] Checkpoint 27: pip 安装 nuitka
- [ ] Checkpoint 28: pip 安装 invoke
- [ ] Checkpoint 29: pip 安装 build（PEP 517构建前端）
- [ ] Checkpoint 30: pip 安装 decorator、attrs、cloudpickle、typing_extensions（TVM依赖）
- [ ] Checkpoint 31: pip 安装使用 --no-cache-dir
- [ ] Checkpoint 32: bin目录权限正确（find /opt/conda/bin -executable -exec chmod a+x）

## profile.d 入口脚本
- [ ] Checkpoint 33: chaos-ai-init.sh 使用 bash 语法，开头有 shebang
- [ ] Checkpoint 34: bash -n 语法检查通过
- [ ] Checkpoint 35: 检测 /workspace/npuusertools 存在则添加到 PYTHONPATH
- [ ] Checkpoint 36: 检测 /workspace/npu_tvm/python 存在则添加到 PYTHONPATH
- [ ] Checkpoint 37: 检测 /workspace/npu_tvm/vta/python 存在则添加到 PYTHONPATH
- [ ] Checkpoint 38: 设置 XMNN_TOOLS_ROOT 环境变量
- [ ] Checkpoint 39: 未挂载目录时不报错，仅输出 INFO 提示
- [ ] Checkpoint 40: 脚本被 COPY 到 /etc/profile.d/ 并设置可执行权限

## Stage 3 冒烟测试
- [ ] Checkpoint 41: 验证 Python 版本为 3.14.x
- [ ] Checkpoint 42: 验证 cmake >= 4.4
- [ ] Checkpoint 43: 验证 ninja >= 1.13
- [ ] Checkpoint 44: 验证 llvm-config --version == 22.1.8
- [ ] Checkpoint 45: 验证 import torch、onnx、onnxruntime
- [ ] Checkpoint 46: 验证 import onnxruntime.quantization（quantize_dynamic等）
- [ ] Checkpoint 47: 验证 import scikit_build_core、nuitka、invoke
- [ ] Checkpoint 48: 验证 import decorator、attrs、cloudpickle、typing_extensions
- [ ] Checkpoint 49: 验证 which patchelf 或 patchelf --version
- [ ] Checkpoint 50: 验证 /opt/venv Jupyter 保留
- [ ] Checkpoint 51: 验证 docker/supervisord 服务可用
- [ ] Checkpoint 52: 验证 devuser 可访问所有工具（su - devuser -c "..."）
- [ ] Checkpoint 53: 最终输出构建计时汇总表格（Stage1/2/3 + 总计）

## 构建脚本
- [ ] Checkpoint 54: build.sh 开头有 set -euo pipefail
- [ ] Checkpoint 55: build.sh 支持 --help/-h 参数输出帮助
- [ ] Checkpoint 56: build.sh 支持 --tag 参数自定义镜像标签
- [ ] Checkpoint 57: build.sh 支持 --cn 参数启用国内镜像
- [ ] Checkpoint 58: build.sh 支持 --no-cache 参数
- [ ] Checkpoint 59: build.sh 自动检测基础镜像是否存在，不存在给出提示
- [ ] Checkpoint 60: build.sh 设置 DOCKER_BUILDKIT=1
- [ ] Checkpoint 61: build.sh 构建完成后输出镜像大小
- [ ] Checkpoint 62: build.sh 构建完成后输出快速运行命令
- [ ] Checkpoint 63: build.bat 正确调用 WSL 执行 build.sh（Windows环境）

## 验证脚本 verify-deployment.py
- [ ] Checkpoint 64: Python 语法正确，可直接运行
- [ ] Checkpoint 65: 验证 SSH 服务运行
- [ ] Checkpoint 66: 验证 Docker daemon 可用
- [ ] Checkpoint 67: 验证 Supervisord 运行
- [ ] Checkpoint 68: 验证 Jupyter 可用
- [ ] Checkpoint 69: 验证 Python 版本
- [ ] Checkpoint 70: 验证所有核心包导入（torch/onnx/onnxruntime/quantization）
- [ ] Checkpoint 71: 验证 XMNN 构建包导入（scikit_build_core/nuitka/invoke等）
- [ ] Checkpoint 72: 验证系统工具（cmake/ninja/llvm-config/patchelf）
- [ ] Checkpoint 73: 验证挂载点目录存在
- [ ] Checkpoint 74: 验证 devuser 权限
- [ ] Checkpoint 75: 输出彩色 PASS/FAIL/SKIP 和汇总统计
- [ ] Checkpoint 76: 有失败项时返回非零退出码

## README 文档
- [ ] Checkpoint 77: 包含镜像概述和依赖链
- [ ] Checkpoint 78: 包含版本信息表格
- [ ] Checkpoint 79: 包含构建命令（普通/国内镜像）
- [ ] Checkpoint 80: 包含完整运行命令（含 -v 挂载 npuusertools/npu_tvm）
- [ ] Checkpoint 81: 包含验证方法（运行verify-deployment.py）
- [ ] Checkpoint 82: 包含服务访问说明（SSH/Jupyter/Docker端口和凭证）
- [ ] Checkpoint 83: 包含环境变量说明
- [ ] Checkpoint 84: 包含在容器内构建npuusertools的快速示例
- [ ] Checkpoint 85: 所有Markdown链接有效（无断链）

## 代码质量
- [ ] Checkpoint 86: 所有 shell 脚本通过 bash -n 语法检查
- [ ] Checkpoint 87: 所有 Python 脚本通过 python -m py_compile
- [ ] Checkpoint 88: Dockerfile 中没有硬编码的绝对路径（宿主机路径）
- [ ] Checkpoint 89: 敏感信息（密码/token）通过ENV传入，不硬编码
- [ ] Checkpoint 90: 文件权限正确（shell脚本可执行，配置文件可读）
- [ ] Checkpoint 91: 代码风格与 onnx-quantized 变体保持一致（注释/格式/输出风格）
