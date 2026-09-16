---
id: "jupyter-podman-client-xmnn-runtime-overlay"
title: "工作负载叠加层：xmnn-runtime（xmnnrt.*）"
source: "overlays/xmnn-runtime/README.md"
---
# 工作负载叠加层：xmnn-runtime（xmnnrt.* 命令）

第四个声明式栈 **`xmnnrt.*`** 是 xmnn-dev 的 **wheel 消费型运行时**
（builder/runtime 分离）：`xmnn.wheel` 只在重型构建器栈产 whl，本栈把
预构建 whl 装进干净交付镜像——无 LLVM/Nuitka 工具链、不挂载源码，
wheel 的 `_libs`（libtvm.so + libLLVM 22，RPATH `$ORIGIN`）自包含。

```bash
# apps/containers/client
# 1) 构建器栈产 whl（产物落 workspace/dist）
invoke xmnn.wheel
# 2) 暂存最新 whl + 构建运行时镜像（构建期 9 项硬验证 root+devuser 双跑）
invoke xmnnrt.build --pip-mirror tuna
# 3) 起交付环境：SSH 2225 / JupyterLab 8893
invoke xmnnrt.up --skip-build
invoke xmnnrt.smoke
invoke xmnnrt.down
```

- 端口默认 **2225/8893**（quant 2222/8888、xmnn 2223/8890、monetize
  2224/8892 之后的下一组）。
- ABI：wheel 为 cp314-cp314 **GIL**，装入 base env `/opt/conda`；
  main env（cp314t）继续只跑 Jupyter。两镜像 FROM 同一 rootless 基底
  保证 ABI 一致；交付内核 `Python 3.14 (xmnn runtime)` 的 argv 指向
  `/opt/conda/bin/python`，kernel env 不含任何源码路径。
- whl 暂存：build/up 自动从 `workspace/dist` 取最新 whl 拷入
  `overlays/xmnn-runtime/wheels/`（不入 git；`--wheel` 可显式指定）；
  裸 `podman-compose up` 需手工拷入。
- 与 [apps/docker-images/xmnn-runtime](../../../docker-images/xmnn-runtime/docker/AGENTS.md)
  互不相关：后者基于外部 `npu-tvm-build:conda`（ai 用户、无 SSH/Jupyter），
  是独立 Docker 谱系。
- **pytorch 前端开箱即用**：torch **2.14.0+cpu 已内置**于镜像
  （Containerfile 版本 pin + PyTorch 官方 CPU 索引，守卫第 10 项构建期
  硬验证 `torch.version.cuda is None`），resnet18/two_inputs 等 .pt 模型
  无需手装任何依赖；需要 torchvision 时按 overlay README 自建薄镜像层。
  torch 升级（版本 pin/守卫双点、真机重建、精度回归、回滚与禁项）见
  overlay README 「torch-cpu 升级指南（SOP）」。
- compose 公共段同样 extends
  [../_shared/base-rootless.yaml](../overlays/_shared/base-rootless.yaml)；
  Windows 原生自动桥接同三栈。
- 完整说明：[overlays/xmnn-runtime/README.md](../overlays/xmnn-runtime/README.md)；
  AI 硬约束 [.agents/rules/xmnnrt-overlay.md](../.agents/rules/xmnnrt-overlay.md)。
