# XMNN wheel 消费运行时叠加层（Podman rootless + podman-compose）

> 一句话：与 [xmnn-dev](../xmnn-dev/README.md) **构建器/运行时分离**——
> `inv xmnn.wheel` 只负责在重型开发栈打出 whl；本叠加层把预构建 whl
> **安装进一个干净的交付镜像**（无 LLVM/Nuitka 工具链、不挂载源码），
> 自带 SSH + JupyterLab，Jupyter 内核 `Python 3.14 (xmnn runtime)`
> 直接从 site-packages 运行自包含 wheel。

- **镜像**：`localhost/xmnn-runtime:latest`（薄叠加
  FROM `localhost/jupyter-podman-rootless:latest`，与 xmnn-dev 同基底保证 ABI 一致）
- **ABI**：wheel 为 `cp314-cp314`（GIL enabled），装入 base env
  `/opt/conda`；main env（cp314t）继续跑 Jupyter 服务，不动
- **制品契约**：`xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`
  自包含 `_libs/`（libtvm.so + libLLVM 22，RPATH `$ORIGIN`）、
  `xmnn_bootstrap.pth`、autolibs/tools_cpp/fonts 数据目录与 19 个依赖声明
- **服务**：SSH（宿主 **2225**→22）+ JupyterLab（**8893**→8888），
  supervisord 托管，沿用基底 entrypoint
- **不包含**：LLVM/Clang、Nuitka、gcc/g++、gdb、ccache；npu_tvm/
  npuusertools 源码树（与 xmnn-dev 的关键差异）
- **内置**：torch 2.14.0+cpu（pytorch 前端编译/精度；typer/xmflow CLI；
  构建期 10 项硬验证）
- **编排**：podman-compose（rootless、无 privileged）；AI 硬约束见
  [../../.agents/rules/xmnnrt-overlay.md](../../.agents/rules/xmnnrt-overlay.md)

## builder/runtime 分工

| 维度 | xmnn-dev（构建器，`xmnn.*`） | xmnn-runtime（本栈，`xmnnrt.*`） |
|---|---|---|
| 镜像 | `localhost/xmnn-dev:latest` | `localhost/xmnn-runtime:latest` |
| 工具链 | LLVM/Clang 22、Nuitka 4.1.3、gcc/g++、gdb、ccache | 仅 wheel 运行依赖 |
| 源码 | 运行时 bind npu_tvm/npuusertools/models | **不挂载**（site-packages 运行） |
| 产物/输入 | 产出 `workspace/dist/xmnn-*.whl` | 消费该 whl（构建前暂存进 `wheels/`） |
| Jupyter 内核 | Python 3.14 (xmnn dev)，env 带源码 PYTHONPATH | Python 3.14 (xmnn runtime)，无源码路径 |
| 端口 | 2223 / 8890 | 2225 / 8893 |
| 变化频率 | 工具链稳定、源码天天变 | 只随 wheel 版本变化，适合交付 |

## 客户独立交付包（release/）

面向客户的**完全独立离线交付物**：`invoke xmnnrt.pack` 把镜像导出为
`release/artifacts/xmnn-runtime-<版本>.tar.gz` + `release.json`（sha256
清单），配合自包含 compose（无 extends、无仓库路径）、bash/pwsh7 双端
`xmnnctl`（init/load/up/down/ps/logs/smoke）与客户向文档；客户侧无需
Python、无需联网，Podman 与 Docker 双兼容。客户侧使用说明见
[release/README.md](release/README.md)。

> 在**开发仓库内演练**随包脚本时须进入 `release/`（叠加层根目录不含
> `xmnnctl`）：`cd release; .\xmnnctl.ps1 init`，或直接
> `.\release\xmnnctl.ps1 init`；日常开发态仍使用下文的 `invoke xmnnrt.*`。

## 前置条件

1. podman machine（Windows 即 WSL2 后端）已运行；
2. 本地有基底镜像（与 xmnn-dev 同一镜像）：`invoke load`；
3. 已有 whl 产物：先在 xmnn-dev 栈执行
   ```bash
   invoke xmnn.up --skip-build          # 若构建器栈未运行
   invoke xmnn.build-tvm                # 首次需要（build/libtvm.so）
   invoke xmnn.wheel                    # 产物落 client/workspace/dist/
   ```
4. Windows 原生自动桥接 `podman-machine-default`（与三栈同族，
   `COMPOSE_WSL_DISTRO` 可指定、`none` 关闭）。

## 路径一：invoke xmnnrt.*（推荐）

在 `apps/containers/client` 下：

```bash
invoke xmnnrt.build                       # 自动暂存 workspace/dist 最新 whl 后构建镜像
                                         #   --wheel <path> 显式指定 whl
                                         #   --pip-mirror tuna|aliyun 加速依赖安装
                                         #   构建期自动执行 9 项硬验证（root+devuser）
invoke xmnnrt.up                          # 启动栈（默认随带构建；自动暂存最新 whl）
invoke xmnnrt.ps
invoke xmnnrt.smoke                       # 已装 wheel 的干净环境 9 项守卫
invoke xmnnrt.logs
invoke xmnnrt.down                        # 停止清理（workspace 保留）
```

启动后：

| 服务 | 地址 | 凭证 / 入口 |
|---|---|---|
| JupyterLab | http://localhost:8893 | `JUPYTER_TOKEN`；内核选 **Python 3.14 (xmnn runtime)** |
| SSH | `ssh -p 2225 devuser@localhost` | `USER_PASSWORD` |

## 路径二：裸 podman-compose

```bash
# 1) 手工暂存 whl（裸 compose 不会自动暂存）
cp ../../workspace/dist/xmnn-*.whl wheels/
# 2) 起栈
cp .env.example .env
podman-compose up -d
podman-compose down
```

## 构建期硬验证（9 项，失败即镜像构建失败）

`smoke/_runtime_smoke.py` 烤入 `/opt/xmnnrt-smoke/`，构建期以 root 与
devuser 双身份执行，`xmnnrt.smoke` / `podman run --rm` 可重复运行：

1. 解释器 ABI：`/opt/conda/bin/python` + cp314 **GIL enabled**
2. import tvm/vta/xmnn 且 `__file__` 落在 site-packages（命中
   `/workspace/`、`/opt/xmnn-builder` 即失败）
3. `_libs/` 含 libtvm.so 与 libLLVM*
4. 干净环境 ctypes RTLD_GLOBAL 加载 libtvm.so（无 LD_LIBRARY_PATH）
5. `tvm.build('llvm')` 向量乘 2 数值断言
6. relay/std/prelude.rly 数据
7. `xmnn_bootstrap.pth` 在 site-packages
8. xmnn 数据三目录（autolibs/tools_cpp/fonts）
9. `xmnn-runtime` Jupyter 内核已注册且 argv 指向 base python、env 无源码路径

## 参数表

| 键 | 默认值 | 用途 |
|---|---|---|
| `XMNNRT_IMAGE_TAG` | `localhost/xmnn-runtime:latest` | 镜像标签 |
| `XMNNRT_CONTAINER_NAME` | `xmnn-runtime` | 容器名（project name 固定 xmnn-runtime） |
| `XMNNRT_SSH_PORT` / `XMNNRT_JUPYTER_PORT` | `2225` / `8893` | 宿主端口 |
| `XMNNRT_WORKSPACE` | `../../workspace` | notebook 工作区 → /workspace |
| `BASE_IMAGE`（build args） | `localhost/jupyter-podman-rootless:latest` | 基底（须与构建器一致） |
| `PIP_MIRROR`（build args） | `official` | wheel 依赖安装源（official/aliyun/tuna） |
| `USER_PASSWORD` / `JUPYTER_TOKEN` / `SSH_PUBLIC_KEY` / `GRANT_SUDO` | 空/`yes` | 凭证四变量（基段继承） |

## 模型精度验证（SIM_VTA2.0 仿真，真机实测 2026-09-16）

`xmflow`/API 的 accuracy 任务对比 TVM 浮点参考（LLVM）与量化仿真输出的
逐层余弦/MSE/MAE，编译目标 `SIM_VTA2.0` 纯 CPU（wheel 已含
libvta_fsim 与 tools_cpp ELF，干净镜像实测可执行）。模型目录按
`src_model_group_dir/<name 的点号转斜杠>/config.toml` 寻址。

```bash
# 推荐：console script xmflow（wheel [project.scripts] 入口，2026-09-16 起随 whl 提供）
podman run --rm --device /dev/fuse --security-opt label=disable --cgroupns=host \
  -v <repo>/external/chaos/models:/models:ro \
  -v <client>/workspace:/workspace \
  --entrypoint xmflow localhost/xmnn-runtime:latest \
  pipeline -n demo.caffe.resnet50 -t compile,accuracy \
    --src-model-group-dir /models --temp-dir /workspace/xmnn-temp
# 单步：xmflow accuracy -n <name> --src-model-group-dir /models --temp-dir ...
# 产物 result.csv 在 workspace/xmnn-temp/<name>/accuracy/result.csv
```

> Python API 等价路径：`xmnn.compile_api.compile_xmnn(...)` /
> `xmnn.accuracy_api.accuracy_xmnn(...)`（见 workspace/xmnn-demo/
> run_demo.py；注意 Nuitka 包**不支持** `python -m xmnn.cli.xmflow`，
> runpy `get_code` 限制；compile_api 默认吞异常，脚本编排需开
> `xmnn.logger_config.logging_config.set_debug_mode(True)`，CLI 自身
> 已处理日志）。

demo 实测（a8w8 / percentile 0.99999，SIM_VTA2.0，单图）：

| demo | 前端 | 输出余弦相似度 | 全局最差层 cos | compile 耗时 |
|---|---|---|---|---|
| caffe/resnet50 | caffe（TVM 前端，无需 pycaffe） | 0.9984（fc1000） | 0.9938 | 149 s |
| onnx/yolov5s | onnx（无需 onnxruntime） | 0.9986–0.9994（三检测头） | 0.9947 | 489 s |
| pytorch/resnet18 | pytorch | 0.9990（linear） | 0.9967 | 85 s |
| two_inputs | pytorch（双输入 32/64） | 0.9999（add） | 0.9999 | 7 s |

前端依赖（全部内置，开箱即用）：

- **torch 2.14.0+cpu 已烤入镜像**（2026-09-16 起，Containerfile Layer 1
  版本 pin + PyTorch 官方 CPU 索引；守卫第 10 项构建期硬验证
  `torch.version.cuda is None`）。pytorch 前端模型（.pt）无需任何手工
  安装，直接 `xmflow pipeline -t compile,accuracy` 即可。
- caffe/onnx 前端由 TVM relay 前端 + vendored caffe_pb2 支持，无额外框架。
- **typer 随 wheel 安装**（pyproject 声明 `typer>=0.12` + `xmflow`
  console script）。

## PyTorch 前端说明（torch 已内置）

pytorch 模型经 `torch.jit.load` 加载再转 TVM relay（compile_api
`_load_pytorch_model`）。镜像内置的是 **CPU 构建** torch（SIM_VTA*
仿真纯 CPU，rootless 环境无 nvidia 运行时）：

```bash
# 直接运行，无需先装 torch
podman run --rm --device /dev/fuse --security-opt label=disable --cgroupns=host \
  -v <repo>/external/chaos/models:/models:ro \
  -v <client>/workspace:/workspace \
  --entrypoint xmflow localhost/xmnn-runtime:latest \
  pipeline -n demo.pytorch.resnet18 -t compile,accuracy \
    --src-model-group-dir /models --temp-dir /workspace/xmnn-temp
```

稳定性约束（Containerfile ARG，修改需重建镜像）：

- `TORCH_VERSION=2.14.0`：精确 pin，升级步骤见下文「torch-cpu 升级指南」；
- `TORCH_INDEX_URL=https://download.pytorch.org/whl/cpu`：**不可**换成
  默认 PyPI 或 tuna/aliyun 镜像——那些渠道的 torch 是 CUDA 变体，会拉入
  nvidia-cuda-*/cudnn/nccl 十余个共数 GB 的包。

torch 层无 COPY 输入且位于 whl 层之前：重打 xmnn whl 触发的增量构建会
复用 torch 层（不重复下载 196 MB）。

## torch-cpu 升级指南（SOP）

torch 版本由**两个点**锁定，升级必须同步修改并真机重建验证。

### 升级前检查（30 秒）

```bash
# 1) 确认目标版本有 cp314 CPU wheel（只列容器实际平台 linux x86_64）
wsl -d podman-machine-default -- bash -c \
  'curl -s https://download.pytorch.org/whl/cpu/torch/ | grep -o "torch-[0-9.]*%2Bcpu-cp314-cp314-manylinux[^\" ]*x86_64\.whl" | sort -uV | tail -5'

# 2) 确认当前镜像版本（镜像 LABEL）
podman image inspect localhost/xmnn-runtime:latest \
  --format '{{index .Config.Labels "org.specweave.torch-cpu"}}'
```

> 硬约束：目标版本必须有 **cp314**（非 cp314t）+ **+cpu** wheel；
> torch 大版本跨越（如未来 3.x）时守卫 `_EXPECTED_TORCH_MAJOR` 与
> `compile_api._load_pytorch_model` 的 TorchScript 行为需一并评估。

### 升级步骤（补丁/小版本，如 2.14.0 → 2.14.1）

1. **改版本 pin**（仅一处）：
   - [Containerfile.xmnn-runtime](Containerfile.xmnn-runtime) 的
     `ARG TORCH_VERSION=2.14.0` → 目标版本；
   - 同主版本（2.x）时守卫 `_EXPECTED_TORCH_MAJOR = "2."` 无需改。

2. **真机构建**（必加 `--no-cache`，强制重下 torch 层）：
   ```bash
   cd apps/containers/client
   invoke xmnnrt.build --no-cache
   ```
   构建期第 10 项守卫会验证 `torch.version.cuda is None` + jit + CPU
   张量算子；版本 pin 写错（无此 wheel）或误拉 CUDA 变体会在本步失败。

3. **回归精度**（至少一个 pytorch demo，确认 TorchScript 加载未变）：
   ```bash
   podman run --rm --device /dev/fuse --security-opt label=disable \
     --cgroupns=host \
     -v <repo>/external/chaos/models:/models:ro \
     -v <client>/workspace:/workspace \
     --entrypoint xmflow localhost/xmnn-runtime:latest \
     pipeline -n demo.two_inputs -t compile,accuracy \
       --src-model-group-dir /models --temp-dir /workspace/xmnn-temp
   ```
   期望 `output-aten::add_0_0` 余弦仍 ≈0.9999（量化精度不应随 torch
   补丁版本显著漂移；明显下降即回滚）。

4. **更新文档版本号**：本 README 中出现的 `2.14.0` 实测记录、
   [.agents/rules/xmnnrt-overlay.md](../../.agents/rules/xmnnrt-overlay.md)
   §4、CHANGELOG 追加一条升级记录（旧→新版本号 + 精度回归结果）。

### 升级步骤（大版本，如 2.x → 3.x）

在小版本 4 步之外，额外：

1. [smoke/_runtime_smoke.py](smoke/_runtime_smoke.py) 的
   `_EXPECTED_TORCH_MAJOR = "2."` 改为新主版本前缀（如 `"3."`）；
2. 评估 `xmnn.compile_api._load_pytorch_model` 使用的
   `torch.jit.load` + `relay.frontend.from_pytorch` 在新版本是否有
   API 变更（该文件在外部子模块 npuusertools，改动走子模块流程）；
3. **全量四个 demo 回归**（caffe/onnx 不受 torch 影响，但构建期
   同镜像，确认无连带）；
4. 先在开发镜像 `xmnn-dev` 用同版本 torch 验证一次编译链路，再升
   runtime（builder 默认不带 torch，需 `podman exec` 临时装）。

### 回滚

torch 与镜像 tag 无强绑定（无 lock 文件层），回滚即把
`TORCH_VERSION` 改回旧值并 `invoke xmnnrt.build --no-cache`；若旧
镜像仍在本地，可直接 `podman tag <旧 image id> localhost/xmnn-runtime:latest`
应急（`podman images` 查历史 id）。

### 不要做的事

- ❌ 不要去掉 `==` 版本 pin（`torch` 浮动会让同一 Dockerfile 不同时间
  构建出不同工具链，违背稳定性目标）；
- ❌ 不要把 `TORCH_INDEX_URL` 改为 PyPI/tuna/aliyun（拉入 CUDA 大包，
  第 10 项守卫会因 `cuda is not None` 直接失败）；
- ❌ 不要把 torch 加进 wheel pyproject 的默认 dependencies（会同时
  污染 builder 镜像与纯 caffe/onnx 用户；runtime 层是正确归属）；
- ❌ 不要在运行中容器里 `pip install -U torch`（只对该容器生效，
  down/重建即丢，且绕过守卫；正确做法是改 ARG 重建镜像）。

### 需要 torchvision / onnx2pytorch 时

| 包 | 何时需要 | 处理 |
|---|---|---|
| `torchvision` | 你的模型定义/预处理引用它（xmnn 前端本身不导入，四个 demo 均不需要） | 自建薄镜像层追加（见下） |
| `onnx2pytorch` | ONNX 模型需转 pytorch 链路（常规 onnx 直接走 onnx 前端，无需） | 自建薄镜像层追加 |

```dockerfile
# Dockerfile.torch-extra（放项目目录，勿提交进 overlay）
ARG BASE_IMAGE=localhost/xmnn-runtime:latest
FROM ${BASE_IMAGE}
RUN /opt/conda/bin/python -m pip install --no-cache-dir torchvision \
    --index-url https://download.pytorch.org/whl/cpu
```

> 不推荐 `pip install "xmnn[torch]"`：该 extra 含 torchvision/
> onnx2pytorch 且 torch 走默认源（CUDA 变体大包）。

## 已知边界（设计取舍）

1. **依赖版本按开放区间解析**：wheel 元数据为 `numpy>=1.26` 类区间约束，
   运行时镜像构建时拉取的依赖小版本可能与 xmnn-dev 当次构建集合不同
   （首次构建实测 numpy 2.5.3 / pandas 3.0.5）。可复现交付需要在 wheel
   打包端锁定版本（pyproject pin 或 constraints），属打包端职责；本栈
   `--pip-mirror` 只换源不锁版本。
2. **whl COPY 层体积冗余**：单阶段构建中 `COPY wheels/xmnn-*.whl`
   （约 170 MB）作为独立镜像层保留（末尾 rm 不回收层体积）。实测镜像
   体积：rootless 基底 1.19 GB → xmnn-runtime **3.18 GB**（含内置
   torch CPU 解压后约 0.9 GB；xmnn-dev 4.69 GB）；若需 tar 分发极致
   瘦身，后续可改双阶段（installer stage 安装、runtime stage 只拷
   site-packages 产物）。
3. **torch 内置的体积取舍**：torch CPU 层约 +0.9 GB，对纯 caffe/onnx
   用户是冗余；换取的是 pytorch 前端零手装、版本可复现的稳定工具链
   （2026-09-16 决策）。需要更小镜像可回退到无 torch 基栈+自建薄层层叠。
4. **运行时不含编译器/调试器**：镜像内无 gcc/gdb/patchelf，设计如此；
   源码级调试请用 xmnn-dev 栈。

## 排障

| 现象 | 处理 |
|---|---|
| `xmnnrt.build` 报"未找到 xmnn wheel" | 先在 xmnn-dev 栈 `invoke xmnn.wheel`；或 `--wheel <path>` 指定 |
| 裸 `podman-compose up` 报 `wheels/xmnn-*.whl not found` | 裸路径不自动暂存：手工 `cp ../../workspace/dist/xmnn-*.whl wheels/` 或先跑一次 `invoke xmnnrt.build` |
| 构建期守卫 FAIL：模块来自 /workspace | wheel 自包含性被破坏（正常镜像无源码树），检查 whl 是否被旧挂载污染后重新 `xmnn.wheel` |
| 精度/编译报 `No module named 'torch'` | 镜像过旧：torch CPU 自 2026-09-16 起内置，重新 `invoke xmnnrt.build`；自建变体须从最新 xmnn-runtime 继承 |
| torch 报错带 CUDA/nvidia 字样 | torch 被换成了默认源的 CUDA 变体；内置层固定走 download.pytorch.org/whl/cpu，勿覆盖 |
| Jupyter 里选不到 xmnn runtime 内核 | 构建日志检查 register-kernel 段；守卫第 9 项会拦截此情况，镜像不会构建成功 |
| 换了 whl 版本但镜像内容没变 | 重新 `invoke xmnnrt.build`（任务自动按 dist 最新 mtime 暂存）；`--no-cache` 全量重建 |
| pip 装依赖慢/失败 | `--pip-mirror tuna`（或 aliyun） |
| `invoke xmnnrt.*` Windows 门禁 Exit(1) | 自动桥接不可用的兜底；在 WSL2 发行版内 `pip install -e ".[compose]"` 后执行 |
