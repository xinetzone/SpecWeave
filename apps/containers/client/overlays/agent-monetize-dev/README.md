# agent-monetize-dev 开发/原生编译打包叠加层（Podman rootless + compose）

> 一句话：在 rootless `jupyter-podman-rootless:latest` 之上做一层薄叠加，
> 运行时 bind 挂载 `apps/agent-monetize` 源码，容器内用 apt clang++ 编译
> tvm-ffi 原生 `score_opportunity.so`（头/库来自 pip 包 apache-tvm-ffi），
> Python 经 tvm-ffi 走原生 PackedFunc 打分；并能 setuptools 打纯 Python
> wheel。这是 **client-overlay-scaffold 形态 B 的轻量变体**（对比
> [xmnn-dev](../xmnn-dev/README.md)：无 Nuitka、不编 TVM、apt clang）。

- **镜像**：`localhost/agent-monetize-dev:latest`（薄叠加；FROM rootless）
- **Python**：`/opt/conda/bin/python` **cp314 GIL**（apache-tvm-ffi wheel
  0.1.13.post3 仅 cp314-cp314 GIL；main cp314t 只跑 Jupyter 服务）
- **工具链**：apt clang++ / patchelf / gdb + pip apache-tvm-ffi（自带
  `libtvm_ffi.so` 与头文件）
- **服务**：SSH（2224）+ JupyterLab（8892）+ supervisord，沿用基底 entrypoint
- **编排**：podman-compose；AI 硬约束见
  [../../.agents/rules/monetize-overlay.md](../../.agents/rules/monetize-overlay.md)
- **源码**：运行时挂载 `/workspace/agent-monetize`（镜像构建期零接触）

## 前置条件

1. podman machine（WSL2 后端）已运行；本地已有
   `localhost/jupyter-podman-rootless:latest`，没有则 `invoke load`。
2. 本地存在 `apps/agent-monetize`（仓库内置应用）。
3. **Windows 原生门禁**：在 WSL2 发行版内运行；或进入 client 自举容器。

## 路径一：invoke monetize.*（推荐）

```bash
pip install -e ".[compose]"          # 一次性（WSL2/Linux/macOS）

invoke monetize.build --pip-mirror aliyun
invoke monetize.up --skip-build
invoke monetize.ps
invoke monetize.build-native         # clang++ → native/build/score_opportunity.so
invoke monetize.smoke                # 守卫 + backend=native 数值一致性
invoke monetize.wheel                # 纯 Python wheel → workspace/dist
invoke monetize.down
```

## 路径二：裸 podman-compose

```bash
cp .env.example .env
podman-compose up -d
podman-compose exec monetize bash /opt/monetize-builder/scripts/build-native.sh
podman-compose exec monetize bash /opt/monetize-builder/scripts/build-wheel.sh
podman-compose down
```

## 开发调试工作流

- Jupyter 内核选 **Python 3.14 (agent-monetize dev)**（base GIL，
  PYTHONPATH 直连挂载 src，改代码即时生效，LD_LIBRARY_PATH 含 tvm_ffi/lib）。
- **后端切换**：未编译 .so 时 ffi_bridge 自动降级纯 Python reference；
  `invoke monetize.build-native` 后重启内核即走 native（日志 backend=native）。
- **原生/参考一致性**：smoke 对固定输入断言两者结果容差 1e-9。
- **wheel**：纯 Python（`agent_monetize-0.1.0-py3-none-any.whl`），
  .so 不入库（运行时从 native/build 加载）。

## 参数表

| 键 | 默认 | 用途 |
|---|---|---|
| MONETIZE_IMAGE_TAG/CONTAINER_NAME | localhost/agent-monetize-dev:latest / agent-monetize-dev | 镜像/容器 |
| MONETIZE_SSH_PORT / JUPYTER_PORT | 2224 / 8892 | 宿主端口（错开 quant 2222/8888、xmnn 2223/8890） |
| MONETIZE_WORKSPACE | ../../workspace | → /workspace |
| MONETIZE_SRC_PATH | ../../../../agent-monetize | agent-monetize 源码宿主路径（invoke 存在性硬校验） |
| USER_PASSWORD / JUPYTER_TOKEN / SSH_PUBLIC_KEY / GRANT_SUDO | 空/空/空/yes | 凭证 |
| PIP_MIRROR | official | pip 源（独立 build 用 --pip-mirror；.env 经 up 内联 build 生效） |
| BASE_IMAGE（注释态） | rootless latest | 基底覆盖 |

## 与相关栈的关系

| 维度 | 本栈（monetize） | xmnn-dev |
|---|---|---|
| 源码 | apps/agent-monetize（单 .cc tvm-ffi） | external/chaos npu_tvm+npuusertools |
| 工具链 | apt clang + pip apache-tvm-ffi | conda LLVM 22 + Nuitka 4.1.3 |
| 编译产物 | score_opportunity.so（秒级） | libtvm.so（10-30 分钟）+ xmnn whl |
| wheel | setuptools 纯 Python | Nuitka 原生编译 wheel |
| ABI | 单一 cp314 GIL | base GIL + main cp314t 双 ABI |

## 排障

| 现象 | 处理 |
|---|---|
| `import tvm_ffi` 失败 | 确认用 `/opt/conda/bin/python`（cp314 GIL），不是 main cp314t；镜像构建日志应有 apache-tvm-ffi 安装 |
| ctypes 加载 .so 报找不到 libtvm_ffi.so | build-native 已写 rpath；确认 compose LD_LIBRARY_PATH 含 tvm_ffi/lib；重跑 build-native |
| backend 一直是 reference | 先 `invoke monetize.build-native`；再确认 native/build/score_opportunity.so 存在 |
| 裸 compose 后 workspace 出现空 agent-monetize 目录 | podman-compose 相对 source 预创建副产物（不影响真实挂载）；invoke 绝对路径不产生 |
| clang++ 找不到 tvm_ffi.h | 镜像 pip 层异常；守卫会拦截，重跑 monetize.build |
