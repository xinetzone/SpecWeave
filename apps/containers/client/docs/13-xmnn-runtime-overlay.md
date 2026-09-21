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
# 2) 暂存最新 whl + 构建运行时镜像（构建期 10 项硬验证 root+devuser 双跑）
invoke xmnnrt.build                   # pip 源/基底默认读 .env（C15）
invoke xmnnrt.build --torch cu130     # 可选：CUDA 13.0 版 torch（缺省 cpu）
# 3) 起交付环境：SSH 2225 / JupyterLab 8893
invoke xmnnrt.up --skip-build
invoke xmnnrt.up --gpu --skip-build   # 可选：透传 GPU 设备（默认隔离不透传）
invoke xmnnrt.smoke
invoke xmnnrt.down
```

- **构建参数单一事实源（C15）**：pip 源与基底走 `.env` 的 `PIP_MIRROR` /
  `BASE_IMAGE`，与 `up` 内联构建、compose 段同键；CLI 旗标只覆盖单次 `build`
  （见 [02-invoke-reference.md](02-invoke-reference.md#参数契约)）。
- **构建执行者唯一（C16）**：`xmnnrt.up` 恒 `up -d --no-build`，镜像只由内核构建。
  默认 `xmnnrt.up` 内联构建一次即起容器；`--skip-build` 不做任何构建，故要求本地
  已有镜像（缺失立即 Exit 1，指引 `xmnnrt.up` / `xmnnrt.build`）。compose 的
  `build:` 段仅服务裸 `podman-compose` 路径。
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
- **pytorch 前端开箱即用**：torch **2.14.0 已内置**于镜像（缺省 CPU 构建；
  `build --torch cu130` 可换 CUDA 13.0 版，索引由白名单形态推导），守卫第
  10 项按容器内 marker 硬断言「声明形态 == 实物」；镜像 tag **随形态走**
  （C28，2026-09-21）：`localhost/xmnn-runtime:cpu` / `:cu130`，另标记
  `:latest` 通用别名——`up --skip-build` 找的就是当前声明形态的那份镜像，
  两形态可共存互不覆盖（旧镜像只挂 `:latest`，按 `up` 提示 `podman tag`
  改挂即可）。resnet18/two_inputs 等
  .pt 模型无需手装任何依赖；需要 torchvision 时按 overlay README 自建薄镜像层。
  torch 升级（版本 pin/守卫双点、真机重建、精度回归、回滚与禁项）见
  overlay README 「torch 升级指南（SOP）」。
- **GPU 可选（C26，2026-09-20）**：`invoke xmnnrt.up --gpu` 透传设备（复用
  C19/C23 内核：三态探测 + 形态分派，WSL2 自动改用 `compose.gpu.wsl.yaml`
  挂 libcuda/libdxcore/drivers）；配合 `build --torch cu130` 才能在容器内
  真正用上 GPU。两能力默认全关 = 与改造前逐字等价；设备是**运行期**
  维度、torch 形态是**构建期**维度。本栈 **cu130 不提供 nvcc**（交付运行时
  P0 禁编译器工具链，需 nvcc 请回 xmnn-dev 栈 C25）。覆盖文件不进
  `release/` 客户交付包（独立谱系，GPU 交付属后续提案）。
- compose 公共段同样 extends
  [../_shared/base-rootless.yaml](../overlays/_shared/base-rootless.yaml)；
  Windows 原生自动桥接同三栈。
- **SSH host key 持久化（2026-09-20）**：命名卷 `xmnnrt-ssh-host-keys` 挂
  `/var/lib/jpman/ssh-host-keys`，`down/up` 重建容器**不再轮换主机指纹**；
  仅 `down --volumes` 清除。卷名与客户交付栈（`release/compose.yaml` 的
  `xmnn-ssh-host-keys`）刻意不同——内部栈与交付包属不同生命周期，避免
  同机共享卷导致清理互相牵连。
- 完整说明：[overlays/xmnn-runtime/README.md](../overlays/xmnn-runtime/README.md)；
  AI 硬约束 [.agents/rules/xmnnrt-overlay.md](../.agents/rules/xmnnrt-overlay.md)。
