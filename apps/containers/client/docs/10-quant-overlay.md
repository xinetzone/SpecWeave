---
id: "jupyter-podman-client-quant-overlay"
title: "工作负载叠加层：onnx-quantized（quant.*）"
source: "README.md#12-工作负载叠加层onnx-quantizedquant-命令opt-in"
---
# 工作负载叠加层：onnx-quantized（quant.* 命令，opt-in）

除了用 `invoke run --tag` 跑任意镜像，client 还内置一个**声明式工作负载栈**：
ONNX 量化工具链叠加层（INT8/FP16/QDQ，纯 ONNX 无 PyTorch，cp314t free-threading）。
它由 podman-compose 子进程驱动，与 SDK→CLI 两层平行、互不影响。

```bash
pip install -e ".[compose]"          # 一次性安装可选依赖 podman-compose（WSL2/Linux/macOS）
invoke quant.build --pip-mirror tuna # 构建 localhost/onnx-quantized:latest（构建期含守卫+冒烟）
invoke quant.up                      # 启动栈：SSH 2222 / Jupyter 8888
invoke quant.smoke                   # 动态 INT8 / FP16 / 静态 QDQ 三个固定种子冒烟
invoke quant.up --gpu                # 需要 GPU 推理时（叠加 compose.gpu.yaml，透传 /dev/dri）
invoke quant.down                    # 停止并清理
```

- **Windows 原生自动桥接**：`quant.*`/`xmnn.*`/`monetize.*` 在 Windows 原生
  CPython 默认**自动桥接**到 WSL 发行版 `podman-machine-default`（或
  `COMPOSE_WSL_DISTRO` 指定目标；该发行版由 jupyter-podman-rootless 改名顶替）内执行（2026-09-15 起替代硬门禁，见
  [utils.py::run_in_wsl_bridge](../src/jpman_client/tasks/utils.py)）；发行版
  不可用或设为 `COMPOSE_WSL_DISTRO=none` 时才回退门禁提示（WSL2 内运行或
  `invoke env.run-cmd` 进入自举容器，基底已内嵌 podman-compose）。
- **配置**：`QUANT_IMAGE_TAG` / `QUANT_SSH_PORT` / `QUANT_JUPYTER_PORT` /
  `QUANT_WORKSPACE` / `USER_PASSWORD` / `JUPYTER_TOKEN` 等写入本目录 `.env`
  即可（模板见 `.env.example` 与 [overlays/onnx-quantized/.env.example](../overlays/onnx-quantized/.env.example)）。
- **裸 compose**：不加装任何 Python 包也可在 `overlays/onnx-quantized/`
  直接 `podman-compose up -d`。

完整说明（版本矩阵、冒烟含义、与 Docker 谱系源变体的差异、深度量化指南）：
[overlays/onnx-quantized/README.md](../overlays/onnx-quantized/README.md)。
对应 AI 硬约束：[.agents/rules/quant-overlay.md](../.agents/rules/quant-overlay.md)（C11）。