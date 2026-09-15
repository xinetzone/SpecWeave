# monetize.* agent-monetize 开发/原生编译打包栈规则

> 单一职责：本文件只约束 `overlays/agent-monetize-dev/` 叠加镜像与
> `src/jpman_client/tasks/monetize.py` 编排任务。同族通用红线继承
> [quant-overlay.md](quant-overlay.md) 与 [client-overlay-scaffold](../../../../../.agents/skills/client-overlay-scaffold/SKILL.md)；
> 形态 B（轻量工具链挂载栈）范式真源为 [xmnn-overlay.md](xmnn-overlay.md)。

## 1. 架构边界（四层不可混）

| 层 | 载体 | 职责 |
|---|---|---|
| 根/`container.*` | podman-py SDK → CLI fallback | 单容器生命周期（零回归对象） |
| `env.*` | podman CLI 子进程 | client SDK 自举镜像 |
| 根/`quant.*` `xmnn.*` | 既有工作负载栈 | 不改动 |
| **`monetize.*`** | **podman-compose 子进程** | **agent-monetize 源码调试 + tvm-ffi 原生 .so 编译 + 纯 Python wheel** |

- `monetize.py` **禁止 `import podman`**；禁回流根 `invoke run`。
- 复用 `[compose]` extra，不新增 Python 依赖。

## 2. 双门禁 / WSL 桥接（同 C11/C12）

Windows 原生 CPython 先过 `_gate_platform()`——**自动桥接优先**
（2026-09-15 起）：经 `utils.run_in_wsl_bridge` 转发到 WSL 发行版（默认
`podman-machine-default`，`COMPOSE_WSL_DISTRO` 覆盖 / `none` 关闭；该
发行版由 jupyter-podman-rootless 改名顶替 flapping machine）内
执行，实时透传、返回码原样上抛、成功即 Exit(0)；桥接不可用才回退
Exit(1)（WSL2/自举容器双路径动态指引）；POSIX 缺 podman-compose
`_gate_compose_binary()` Exit(1)；build/up/smoke/build-native/wheel 过
daemon 预检。

## 3. compose 三必需 / bridge / 标签

三必需只用标准字段（devices `/dev/fuse`、security_opt `label=disable`、
cgroupns `host` 1.6 空操作须注释），严禁 privileged；`network_mode:
bridge`（machine 无 systemd user bus 实证，与 xmnn 同）；探测用
`io.podman.compose.project/service`，业务标签仅 `org.specweave.*`。

## 4. 源码仅运行时挂载（2 个 bind）

- workspace 与 `MONETIZE_SRC_PATH`（默认 apps/agent-monetize）均长语法
  bind + create_host_path；invoke 解析绝对 POSIX 路径，源码路径做
  **存在性硬校验**（`_SOURCE_MOUNTS`，缺失 Exit 1）。
- 镜像构建上下文=overlay 目录；Containerfile 构建期**不读 agent-monetize
  源码**（无 BuildKit bind）；工具链与打包脚本烤入镜像。
- **checkpoint 可写性契约**：与 xmnn/quant 同族（三栈共享 client/workspace）。
  Jupyter 以 devuser(1000) 运行，rootless+9p/drvfs 下 root 预建的
  `$MONETIZE_WORKSPACE/.ipynb_checkpoints` 在容器视角为 0:0 755 时保存
  notebook 必报 Errno 13；invoke 侧 `_prepare_env()` mkdir 工作区后**必须**
  调用 `utils.ensure_workspace_checkpoint_writable()`（幂等 0777、只改权限位
  不改属主、只作用该单一目录不递归、不碰源码 bind）。

## 5. 本栈特有契约（与 xmnn-dev 的轻量化差异）

- **apt clang 而非 conda LLVM 22**：编译单个 `score_opportunity.cc` 对
  LLVM 版本不敏感，apt `clang++` + patchelf + gdb 即可；tvm-ffi 头/库
  全部来自 pip wheel `apache-tvm-ffi==0.1.13.post3`（含
  `tvm_ffi/include` 与 `tvm_ffi/lib/libtvm_ffi.so`）。
- **单一 cp314 GIL ABI**：apache-tvm-ffi wheel 仅发布 cp314-cp314
  （GIL）manylinux；编译/运行/Jupyter 内核解释器全部固定
  `/opt/conda/bin/python`（base）。main cp314t 只跑 Jupyter 服务，
  不装/不跑 tvm_ffi。守卫对 base GIL + tvm_ffi 做硬断言。
- **.so rpath**：build-native.sh 用 `-Wl,-rpath` + patchelf 把
  score_opportunity.so 的 rpath 指到容器内 tvm_ffi/lib（site-packages
  绝对路径，$ORIGIN 不适用——依赖库不在 .so 同目录）；compose
  LD_LIBRARY_PATH 双保险。
- **纯 Python wheel（.so 不入库）**：pyproject 是 setuptools src 布局、
  不含 ext_modules；build-wheel 出 py3-none-any wheel，.so 是挂载源码树
  native/build 的运行时产物（ffi_bridge 按文件路径加载）。不改 pyproject。
- **agent-monetize 源码改动边界=3 处跨平台适配**：仅
  `config.py`（native_lib 按 sys.platform 选 .dll/.so/.dylib + 空值
  回退）、`config.yaml`（去硬编码 .dll）、`tests/test_ffi.py`（测试
  路径平台化）。Windows build.ps1/.dll 路径与打分业务逻辑不得改。

## 6. 冒烟双路径

- `_toolchain_guards.py`（镜像烤入，构建期 root+devuser 双跑，run --rm
  可独立跑）：base GIL、clang++/patchelf/gdb、tvm_ffi import +
  libtvm_ffi.so + tvm_ffi.h、builder 资产。
- `smoke_native.py`（仅栈运行态）：挂载点断言先于原生分支（.so 缺席是
  合法首次态，不得掩盖挂载失败）；.so 在则 FfiBridge backend=native +
  固定输入与纯 Python 参考容差 1e-9。

## 7. 8 任务与选型

| 命令 | 职责 |
|---|---|
| build / up / down / ps / logs | 镜像与声明式栈生命周期 |
| smoke | 守卫（栈未运行 run --rm）+ 挂载/原生（运行时 exec） |
| build-native | exec build-native.sh：clang++ 出 score_opportunity.so |
| wheel | exec build-wheel.sh：setuptools 纯 Python wheel 落 workspace/dist |

## 8. 选型与边界

- 需要重型 Nuitka/编译整个 TVM/打 xmnn whl → [xmnn-overlay.md](xmnn-overlay.md)。
- ONNX 量化分析 → [quant-overlay.md](quant-overlay.md)。
- 改 agent-monetize 业务代码（打分/通道/合规等）走该应用自身规范，
  不在本规则范围。

## 9. Gotchas（本栈实测新增）

- **apache-tvm-ffi ABI 是 cp314 GIL**：在 cp314t main env 装不上/不可用，
  编译解释器选错会出现 `import tvm_ffi` 失败但无明确 ABI 提示。
- **config.yaml 空 native_lib 必须回退默认**：from_dict 对空串/None 的
  native_lib 过滤，否则会覆盖平台默认得到空路径。
- **裸 compose 相对 source 副产物**：与 xmnn 同族（G1）；invoke 绝对
  路径不产生。
