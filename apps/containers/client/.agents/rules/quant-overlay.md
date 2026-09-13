# quant.* 工作负载叠加栈规则（podman-compose 编排层）

> 单一职责：本文件只约束 `invoke quant.*` 命名空间与 `overlays/onnx-quantized/`
> 叠加栈。根命名空间（`load/run/...`，SDK→CLI 两层）的规则见
> [invoke-tasks.md](invoke-tasks.md) 与 [sdk-connection.md](sdk-connection.md)，
> 本文件不覆盖、不重述。

## 1. 架构边界（三层不可混）

| 层 | 载体 | 职责 |
|---|---|---|
| 根/`container.*` 命名空间 | podman-py SDK → CLI fallback | 单容器命令式生命周期（既有，零回归对象） |
| `env.*` 命名空间 | podman CLI 子进程 | client SDK 自举叠加镜像（Containerfile.client） |
| **`quant.*` 命名空间（本文件）** | **podman-compose 子进程（禁止 import podman）** | **量化工作负载声明式栈（overlays/onnx-quantized）** |

- quant.py 内**禁止**出现 `import podman` / `from podman`：compose 层是子进程消费方，
  不允许复用 SDK 连接路径（Windows 原生门禁独立于 SDK 四策略）。
- 禁止把 compose 提升为 `invoke run` 的第三层后端（用户 2026-09-13 裁决）：
  opt-in 独立命名空间即最终形态，不要向根 run 路径回流。

## 2. 平台门禁（硬约束）

1. **Windows 原生 CPython 一律 Exit(1)**：任何 quant 任务入口先过 `_gate_platform()`。
   podman-compose 子进程与其挂载路径处理在 Windows 原生有已知缺陷
   （短语法 `os.makedirs` 误建盘符目录；构建端已实测门禁）。放行路径仅两条：
   WSL2 发行版内运行 / `invoke env.run-cmd` 自举容器内运行（rootless 基底已内嵌
   podman-compose）。
2. **POSIX 缺 podman-compose 二进制 Exit(1)**：`_gate_compose_binary()` 输出
   `pip install -e ".[compose]"`。pyproject 中 compose 为 optional extra，
   核心 dependencies 永不拉入。
3. 门禁顺序固定：先平台后二进制；两道门都必须输出**可执行中文指引**。

## 3. compose.yaml ↔ rootless 三必需映射

知识包 [podman-compose concepts/03](../../../../../projects/awesome-okf-xs/doc/bundles/jishu/containers/podman-compose/concepts/03-compose-patterns.md)
证实三必需全部可用标准 Compose 字段表达，**严禁**特权容器与非必要 x-podman：

| rootless 三必需（utils.ContainerConfig） | compose 字段 |
|---|---|
| `--device /dev/fuse` | `devices: [/dev/fuse:/dev/fuse]` |
| `--security-opt label=disable` | `security_opt: [label=disable]` |
| `--cgroupns=host` | `cgroupns: host` |

- workspace 绑定一律**长语法** + `bind.create_host_path: true`（短语法在
  podman-compose 会无条件 `os.makedirs`，Windows/异常路径宿主残留事故的同源教训）。
- GPU 默认不透传（默认隔离）；仅 `-f compose.gpu.yaml` 时叠加。

## 4. 多文件深合并语义（GPU 覆盖写法依据）

依据知识包 [06-config-pipeline](../../../../../projects/awesome-okf-xs/doc/bundles/jishu/containers/podman-compose/concepts/06-config-pipeline.md)：
多文件 list 字段默认**追加**（volumes 按 target 去重，**devices 不去重**）。

→ `compose.gpu.yaml` 只写新增设备（`/dev/dri:/dev/dri`），**禁止**重复 /dev/fuse；
整体替换才用 `!override`，本栈无此需求。CDI 形态（nvidia.com/gpu=all）与
/dev/dri 互斥，以注释给出，不默认启用。

## 5. 变量优先级与 workspace 规则

优先级链（与知识包配置管线一致，shell 最高）：

```
shell 显式 export > root client .env（load_dotenv override=False）
> overlay .env（仅裸 podman-compose 自读）> compose.yaml ${VAR:-default}
```

- root `.env` 是 invoke 路径的唯一 .env 事实源；`overlays/.../.env.example`
  复制出的 `.env` 只服务「裸 podman-compose」用户，两处键集合必须一致
  （新增插值键时双向同步，T3 键集合 diff 为强制检查）。
- invoke 路径把 `QUANT_WORKSPACE` 解析为**绝对 POSIX 路径**注入子进程
  （`to_posix_path`，Dimension A 复用），相对路径相对 invoke cwd 解析并 mkdir -p；
  禁止让 daemon 侧解析 compose 文件相对路径（B-scheme/远距 daemon 域不同）。

## 6. 叠加镜像构建契约（Containerfile.quantized）

- `FROM localhost/jupyter-podman-rootless:latest`（与 onnx-dev main/cp314t
  环境同构；用户 2026-09-13 裁决不从 client 叠加层再叠加）。
- 五包装入 `/opt/conda/envs/main`，版本固定 + 来源注释；版本以源
  `variants/onnx-dev/Dockerfile`（浮动 pip）+ 其 RELEASE 实测矩阵 + PyPI 索引
  三重实证，禁止臆造。已知版本异构：`onnx-simplifier==0.5.0` 的 wheel
  内 `onnxsim.__version__=="0.7.3"`。
- 构建期守卫不可删：Py_GIL_DISABLED=1、`_is_gil_enabled() is False`、
  torch/torchvision/onnxoptimizer 缺席（固化于 `smoke/_quant_guards.py`）。
- **OCI 引号教训**：buildah 对 shell-form RUN 的 `bash -lc '<body>'` 二次分词
  会切断内联 `python -c "...\"x\"..."`；含引号的验证逻辑一律固化为脚本文件，
  RUN 行不出现内层双引号。
- 不覆盖 ENTRYPOINT/CMD/WORKDIR（沿用 tini→entrypoint.sh→supervisord）。

## 7. 标签接缝（compose 写、CLI/SDK 读）

podman-compose 自动写 `io.podman.compose.project` /
`io.podman.compose.service` 标签（知识包 05「标签即数据库」）；
`quant.smoke` 的运行探测与运维侧筛选统一用这两个标签，不自行发明标签键。
业务标签仅允许 `org.specweave.*` 前缀。

## 8. 冒烟双路径

`quant.smoke`：栈在运行 → `podman-compose exec -T quant <main python> <script>`；
栈未运行 → `podman run --rm --entrypoint <main python> <img> <script>`
（纯 CPU 一次性计算，不需要三必需之外的任何特权参数）。
三脚本与源 Dockerfile Stage 3 heredoc 语义逐行等价（种子 42、阈值 <5.0），
放宽阈值即破坏 AC-2。

## 9. 选型依据（为何不是别的形态）

知识包 [10-compose-vs-podman-py](../../../../../projects/awesome-okf-xs/doc/bundles/jishu/containers/podman-compose/concepts/10-compose-vs-podman-py.md)
决策表：应用栈生命周期（配置复现、up/down 联动、标签化资源）用 compose；
单资源命令式操作保留 SDK。本栈单服务但仍选 compose——为后续多服务工作负载
预留同一编排范式，且 GPU 覆盖/profile/.env 插值的声明式表达优于在
invoke 参数层复刻一套拼接逻辑。
