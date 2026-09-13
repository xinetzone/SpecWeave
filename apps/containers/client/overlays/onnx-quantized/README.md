# ONNX 量化工作负载叠加层（Podman rootless + podman-compose）

> 一句话：在 `localhost/jupyter-podman-rootless:latest` 之上做一层薄叠加，
> 提供 **纯 ONNX（无 PyTorch）的 INT8/FP16/QDQ 量化工具链**，并以
> podman-compose 声明式栈（或 client 的 `invoke quant.*` 命名空间）一键构建/起停/验证。

- **镜像**：`localhost/onnx-quantized:latest`（薄叠加，约 1.4 GB；基底 1.19 GB）
- **Python**：conda **main 环境**，cp314t free-threading（GIL 禁用），解释器 `/opt/conda/envs/main/bin/python`
- **服务**：SSH（容器 22 → 宿主 2222）+ JupyterLab（8888），supervisord 托管，沿用基底 entrypoint
- **编排**：podman-compose（daemon-less、rootless）；AI 硬约束见
  [../../.agents/rules/quant-overlay.md](../../.agents/rules/quant-overlay.md)

## 包含什么

| 组件 | 版本（2026-09-13 构建实测） | 用途 |
|---|---|---|
| onnx | 1.22.0 | 模型格式/纯 ONNX 构建（`onnx.helper`） |
| onnxruntime | 1.28.0（含 quantization 模块） | CPU 推理 + 量化引擎 |
| onnx-simplifier（PyPI 发行版） | 0.5.0 | 模型简化（模块 `onnxsim.__version__` 报 v0.7.3，包/模块版本异构，非错误） |
| onnxscript | 0.7.1 | ONNX Script 工具 |
| onnxconverter-common | 1.16.0 | FP16 转换（`float16.convert_float_to_float16`） |
| ~~torch/torchvision~~ | 缺席（构建期负向守卫） | 纯 ONNX by design；需要时自行 `pip install torch` |
| ~~onnxoptimizer~~ | 缺席（free-threading 不兼容，CPython #111506） | 用途由 onnxsim 覆盖 |
| neural-compressor | 不预装（需 torch，可选） | `pip install neural-compressor torch` 后使用 PyTorch 量化 |

## 前置条件

1. podman machine（Windows 即 WSL2 后端；Linux/macOS 为本机 rootless podman）已运行
2. 本地已有基底镜像，没有则先在 `apps/containers/client` 加载：
   ```bash
   invoke load        # 从 ../jupyter-podman-rootless/.image-cache 加载 localhost/jupyter-podman-rootless:latest
   ```
3. **Windows 原生 CPython 门禁**：`invoke quant.*` 走 podman-compose 子进程，
   Windows 原生不支持。两种放行方式：
   - 在 WSL2 发行版内执行（推荐）：
     ```bash
     wsl -d <发行版>
     cd /mnt/d/spaces/SpecWeave/apps/containers/client
     pip install -e ".[compose]"     # 安装 podman-compose（核心 invoke 命令不需要它）
     ```
   - 或进入 client 自举容器（基底已内嵌 podman-compose）：
     ```powershell
     invoke env.run-cmd --cmd 'inv quant.up'
     ```

## 路径一：invoke quant.*（推荐）

在 `apps/containers/client` 下（WSL2/Linux/macOS）：

```bash
invoke quant.build            # 构建叠加镜像（构建期自动跑守卫 + 3 冒烟；--pip-mirror tuna 可加速）
invoke quant.up               # 渲染并启动栈（默认随带构建；--skip-build 跳过；--gpu 透传 /dev/dri）
invoke quant.ps               # 查看服务状态与端口
invoke quant.smoke            # 3 个量化冒烟（栈在运行→compose exec；未运行→podman run --rm）
invoke quant.logs             # 跟踪日志（Ctrl+C 退出，不影响容器）
invoke quant.down             # 停止并清理（workspace 绑定数据保留；--volumes 连卷一起删）
```

典型会话：

```bash
invoke quant.up --skip-build --gpu     # 已有镜像 + 要做 GPU 推理时
invoke quant.smoke
invoke quant.down
```

启动后访问（默认凭证可通过环境变量覆盖，见 `.env.example`）：

| 服务 | 地址 | 凭证 |
|---|---|---|
| JupyterLab | http://localhost:8888 | `JUPYTER_TOKEN`（留空则启动日志自动生成） |
| SSH | `ssh -p 2222 devuser@localhost` | `USER_PASSWORD`（留空自动生成） |

## 路径二：裸 podman-compose

在本目录（`overlays/onnx-quantized/`）下，无需 invoke：

```bash
cp .env.example .env           # 按需修改（端口/workspace/凭证/pip 源）
podman-compose up -d           # 首次自动构建
podman-compose -f compose.yaml -f compose.gpu.yaml up -d   # 启用 GPU（/dev/dri）
podman-compose ps
podman-compose logs -f
podman-compose down
```

`compose.yaml` 已内置 rootless 三必需（`/dev/fuse` 设备、`security_opt: label=disable`、
`cgroupns: host`），workspace 使用长语法绑定，**无特权容器**。
变量优先级：shell export > `.env` > compose 文件内默认值。

## 冒烟测试（3 个，纯 ONNX）

镜像内 `/opt/onnx-quantized-smoke/` 提供与源 Docker 变体逐行等价的固定种子（42）冒烟：

| 脚本 | 内容 | 断言 |
|---|---|---|
| `smoke_dynamic_int8.py` | Gemm 动态 QInt8 权重量化 | max_diff < 5.0（实测 0.001914） |
| `smoke_fp16.py` | Gemm+Mul+Add 的 FP16 转换 | max_diff < 5.0（实测 0.000211） |
| `smoke_static_qdq.py` | 两层 MLP 静态 QDQ + MinMax 校准 | QDQ 节点 > 0（实测 10 个），max_diff < 5.0（实测 0.014510） |
| `_quant_guards.py` | 构建期守卫：cp314t、GIL 禁用、torch/torchvision/onnxoptimizer 缺席 | 任一不满足构建失败 |

构建期自动执行一次；任何时候可用 `invoke quant.smoke` 重复验证。

## 与 Docker 谱系源变体的关系

本目录是同一量化能力在 **Podman rootless 谱系**的载体；Docker 谱系原目录
[../../../../docker-images/devcontainer-base/variants/onnx-quantized/](../../../../docker-images/devcontainer-base/variants/onnx-quantized/README.md)
**保留原样**（它仍是 torch-dev→ai-dev 构建链的一环）。两处文档互链，量化语义同源。

| 维度 | Docker 谱系（源） | 本叠加层（Podman rootless） |
|---|---|---|
| 继承链 | base→conda-llvm→onnx-dev→onnx-quantized（4 次构建，DinD） | rootless 基底 + 1 个薄叠加层 |
| 构建/编排 | docker build + variants/build.sh + supervisord DinD | podman build + podman-compose（rootless 三必需） |
| 消费方式 | docker run --privileged -p 2375（DinD 端口） | `invoke quant.*` / podman-compose；无 privileged、无 2375 |
| 任务入口 | shell 测试套件（24 项） | invoke 6 任务 + 3 冒烟（构建期 + 可重复） |
| Python 环境 | conda main，cp314t，GIL 禁用 | **同左**（同构基底） |
| neural-compressor | 可选（需 torch） | 同左 |

## 深入阅读

- [静态量化与 FP16/BF16 高级指南](docs/ADVANCED-QUANTIZATION-GUIDE.md)（校准 Reader/QDQ/QOperator/精度验证）
- [QDQ vs QOperator 最佳实践](docs/QUANTIZATION-BEST-PRACTICES.md)（选型决策、基准、自动化）
- [OKF podman-compose 知识包](../../../../../projects/awesome-okf-xs/doc/bundles/jishu/containers/podman-compose/index.md)（编排行为权威依据）
- [client AI 硬约束：quant-overlay.md](../../.agents/rules/quant-overlay.md)
