---
id: "jupyter-podman-client-monetize-overlay"
title: "工作负载叠加层：agent-monetize-dev（monetize.*）"
source: "README.md#135-工作负载叠加层agent-monetize-devmonetize-命令"
---
# 工作负载叠加层：agent-monetize-dev（monetize.* 命令）

第三个声明式栈 **`monetize.*`** 是 client-overlay-scaffold **形态 B 的
轻量变体**，为 `apps/agent-monetize` 提供 tvm-ffi 原生 C++ 编译/调试与
纯 Python wheel：apt clang++ 编译单个 `score_opportunity.cc`（头/库来自
pip 包 apache-tvm-ffi，无需 LLVM 22/Nuitka/编译 TVM），单一 cp314 GIL。

```bash
# apps/containers/client
pip install -e ".[compose]"           # 与 quant/xmnn 同一个可选依赖
invoke monetize.build                 # 构建参数（pip 源、基底）默认读 .env（C15）
invoke monetize.up --skip-build
invoke monetize.build-native          # clang++ → score_opportunity.so
invoke monetize.smoke                 # backend=native 与参考实现一致性
invoke monetize.wheel                 # 纯 Python wheel → workspace/dist
invoke monetize.down
```

- **构建参数单一事实源（C15）**：pip 源与基底走 `.env` 的 `PIP_MIRROR` /
  `BASE_IMAGE`，与 `up` 内联构建、compose 段同键；CLI 旗标只覆盖单次 `build`
  （见 [02-invoke-reference.md](02-invoke-reference.md#参数契约)）。
- **构建执行者唯一（C16）**：`monetize.up` 恒 `up -d --no-build`，镜像只由内核构建。
  默认 `monetize.up` 内联构建一次即起容器；`--skip-build` 不做任何构建，故要求本地
  已有镜像（缺失立即 Exit 1，指引 `monetize.up` / `monetize.build`）。compose 的
  `build:` 段仅服务裸 `podman-compose` 路径。
- 端口默认 **2224/8892**（与 quant 2222/8888、xmnn 2223/8890 错开）。
- compose 公共段（rootless 三必需、凭证四变量、公共 labels/restart、
  `network_mode: bridge`）由三栈共享的
  [../_shared/base-rootless.yaml](../overlays/_shared/base-rootless.yaml)
  经 extends 单一提供，栈 compose.yaml 只写 agent-monetize 专属字段
  （image/build/ports/两个 bind/PYTHONPATH 与 LD_LIBRARY_PATH/组件 label）。
- 对 agent-monetize 仅 3 处跨平台适配（.dll→按平台选 .so/.dylib），
  Windows build.ps1 不回归；.so 不打入 wheel。
- Windows 原生自动桥接同 quant/xmnn（`COMPOSE_WSL_DISTRO` 可指定发行版 / `none` 关闭回退门禁）。
- 完整说明：[overlays/agent-monetize-dev/README.md](../overlays/agent-monetize-dev/README.md)；
  AI 硬约束 [.agents/rules/monetize-overlay.md](../.agents/rules/monetize-overlay.md)（C13）。