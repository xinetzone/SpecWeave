# 新增 onnx-pytorch 镜像变体 - Verification Checklist

## 目录结构检查
- [ ] `variants/onnx-pytorch/` 目录存在，含 Dockerfile/.env.example/README.md/.agents/rules/dockerfile.md
- [ ] Dockerfile 首行含 `# syntax=docker/dockerfile:1.7-labs`

## Dockerfile 正确性检查
- [ ] FROM 使用 `devcontainer-base:conda-llvm-${BASE_TAG}`（基于 conda-llvm）
- [ ] FROM 后重新声明 `ARG BASE_TAG` 等（避免 build-info 中 BASE_IMAGE 退化为空标签）
- [ ] 使用 `SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]`
- [ ] 未覆盖 ENTRYPOINT/CMD/WORKDIR/USER
- [ ] 安装阶段有 `[TIMER]` 计时标记
- [ ] 使用 `--mount=type=cache` 缓存挂载
- [ ] 末尾有 `[VALIDATION CHECKPOINT]` 且包含基础服务继承验证
- [ ] build-info 写入 `/etc/devcontainer-variant-onnx-pytorch-build-info`

## PyTorch CPU 安装
- [ ] 构建后 `import torch` 成功，`torch.__version__` 可输出
- [ ] CPU 版验证：`torch.cuda.is_available()` 为 False
- [ ] `import torchvision` 成功
- [ ] build-info 记录了 torch 实际版本

## ONNX 生态安装
- [ ] 构建后 `import onnx` 成功，`onnx.__version__` 可输出
- [ ] 构建后 `import onnxruntime` 成功，`onnxruntime.__version__` 可输出
- [ ] onnx-simplifier / onnxoptimizer 已安装
- [ ] build-info 记录了 onnx/onnxruntime 实际版本

## build.sh 注册
- [ ] `bash variants/build.sh --list` 显示 `onnx-pytorch` 变体
- [ ] VARIANTS 条目依赖 `conda-llvm`，字段分隔符为 `|`，验证命令用 `;` 分隔

## 测试脚本
- [ ] `variants/scripts/test-onnx-pytorch.sh` 存在且 `bash -n` 通过
- [ ] 覆盖 L1-L6 六层测试（工具链版本 / Hello World / 深度组件 / 服务继承 / PATH 优先级 / 配置文件）

## 文档与注册
- [ ] `variants/README.md` 变体表格已新增 `onnx-pytorch` 条目
- [ ] `variants/onnx-pytorch/README.md` 含镜像说明/构建命令/运行命令/验证命令
- [ ] `variants/onnx-pytorch/.agents/rules/dockerfile.md` 已创建

## 服务继承与环境共存
- [ ] 新镜像可 `docker run` 正常启动
- [ ] ssh/supervisord/docker/jupyter/devuser 基础服务未破坏
- [ ] `/opt/venv/bin/python`（Jupyter 依赖）仍可用，PATH 优先级正确

## 构建验证
- [ ] `bash variants/build.sh --variant onnx-pytorch --cn` 构建成功，无错误
- [ ] `[TIMER]` 阶段计时在构建日志中正确显示
- [ ] build.sh 快速验证全部 PASS
- [ ] `bash variants/scripts/test-onnx-pytorch.sh` 全部测试 PASS
