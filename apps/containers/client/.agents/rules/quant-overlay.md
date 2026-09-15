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
- quant.py 现为**纯声明模块**：唯一事实源是 `QUANT_SPEC`（StackSpec），
  `TASKS = make_stack_tasks(QUANT_SPEC)` 加六个任务别名（build/up/down/ps/
  logs/smoke）即模块全部内容；门禁/环境准备/argv/执行/残留自愈/冒烟双路径
  等同构编排逻辑**唯一定义在 overlay_core**，quant.py 不再含任何编排函数。
- **红线：内核零栈知识 / 栈模块零 podman**——overlay_core 与共享包 jpman_common
  不得 import quant/xmnn/monetize，也不得出现具体栈名/栈路径（栈知识一律由
  StackSpec 实例从外部注入）；`import podman` 只允许出现在
  `apps/containers/shared` 的 jpman_common 内。
- 禁止把 compose 提升为 `invoke run` 的第三层后端（用户 2026-09-13 裁决）：
  opt-in 独立命名空间即最终形态，不要向根 run 路径回流。

## 2. 平台门禁 / WSL 桥接（硬约束）

1. **Windows 原生 CPython 自动桥接优先**（2026-09-15 起）：任何 quant 任务
   入口先过 `overlay_core.gate_platform(QUANT_SPEC)`，经
   `utils.run_in_wsl_bridge(extra_env_keys=QUANT_SPEC.bridge_env_keys)`
   把任务原样转发到 WSL 发行版（默认 `podman-machine-default`（client 专用
   rootless 发行版，与 flapping 的默认 machine 相互独立、镜像存储不互通；
   `COMPOSE_WSL_DISTRO` 可覆盖，`none` 显式关闭））内执行，实时透传、
   返回码原样上抛、成功即 `Exit(0)`。桥接透传的栈专属环境键由
   `QUANT_SPEC.bridge_env_keys` 声明（5 个 QUANT_* 键）；utils 只内置三栈
   无关的 `_BRIDGE_COMMON_ENV_KEYS`（11 个通用键），不再枚举任何栈专属键。
   podman-compose 子进程与其挂载路径处理在 Windows 原生有已知
   缺陷（短语法 `os.makedirs` 误建盘符目录），桥接放行到 POSIX 环境规避。
2. **桥接不可用才回退 Exit(1) 门禁**：无 wsl.exe / 发行版缺失 /
   `COMPOSE_WSL_DISTRO=none` → 动态门禁（推导 /mnt 路径 + 发行版检查 +
   双放行路径：WSL2 发行版内运行 / `invoke env.run-cmd` 自举容器内运行
   （rootless 基底已内嵌 podman-compose）。
3. **POSIX 缺 podman-compose 二进制 Exit(1)**：
   `overlay_core.gate_compose_binary(QUANT_SPEC)` 输出
   `pip install -e ".[compose]"`。pyproject 中 compose 为 optional extra，
   核心 dependencies 永不拉入。
4. 门禁顺序固定：先平台后二进制；两头都输出**可执行中文指引**；桥接
   目标禁止复用 `WSL_DISTRO_NAME`（SDK 连接专用，默认 machine 发行版
   flapping 且镜像存储不互通）。

## 3. rootless 三必需单一事实源（overlays/_shared/base-rootless.yaml，extends 继承）

知识包 [podman-compose concepts/03](../../../../../projects/awesome-okf-xs/doc/bundles/jishu/containers/podman-compose/concepts/03-compose-patterns.md)
证实三必需全部可用标准 Compose 字段表达，**严禁**特权容器与非必要 x-podman。
三必需连同凭证四变量（`USER_PASSWORD`/`JUPYTER_TOKEN`/`SSH_PUBLIC_KEY`/
`GRANT_SUDO`）、公共 label（`org.specweave.managed-by=jupyter-podman-client`）、
`restart: unless-stopped` 与 `network_mode: bridge` 的**单一事实源**是
`overlays/_shared/base-rootless.yaml`（服务名 `rootless-base`）；三栈
compose.yaml 只以 `extends: {file: ../_shared/base-rootless.yaml, service:
rootless-base}` 继承，**栈文件禁止重复声明**这些字段，只保留栈专属的
image/build/ports/volumes/栈 env/`labels.component`。字段映射保留备查
（现位于基文件）：

| rootless 三必需（utils.ContainerConfig 默认值同源） | 基文件 compose 字段 |
|---|---|
| `--device /dev/fuse` | `devices: [/dev/fuse:/dev/fuse]` |
| `--security-opt label=disable` | `security_opt: [label=disable]` |
| `--cgroupns=host` | `cgroupns: host` |

- `network_mode: bridge` 同样在基文件统一提供（2026-09-14 同机实证：
  podman-machine-default 无 systemd user bus，默认项目网络启 aardvark-dns
  必现「Failed to connect to user scope bus」）。**行为变更**：quant 栈
  compose.yaml 此前未声明 network_mode，自 2026-09-15 继承基文件起获得
  bridge。
- workspace 绑定一律**长语法** + `bind.create_host_path: true`（短语法在
  podman-compose 会无条件 `os.makedirs`，Windows/异常路径宿主残留事故的同源教训）。
- GPU 默认不透传（默认隔离）；仅 `-f compose.gpu.yaml` 时叠加。

## 4. 多文件深合并语义（GPU 覆盖写法依据）

依据知识包 [06-config-pipeline](../../../../../projects/awesome-okf-xs/doc/bundles/jishu/containers/podman-compose/concepts/06-config-pipeline.md)
与 vendor 1.6.0 源码（L2289-L2297）：多文件 list 字段默认**追加**（**devices
不去重**）；volumes 仅**短语法字符串**按 target 去重且覆盖方获胜，**长语法
dict bind 不去重**——workspace 绑定全部用长语法（见 §3），故 override 中
重声明同 target 会产生重复挂载，需人工避免，不能依赖合并器去重。

> `compose.gpu.yaml` 只写新增设备（`/dev/dri:/dev/dri`），**禁止**重复 /dev/fuse；
整体替换才用 `!override`，本栈无此需求。CDI 形态（nvidia.com/gpu=all）与
/dev/dri 互斥，以注释给出，不默认启用。

### 4.1 extends 服务级继承（base-rootless.yaml 合并语义）

- podman-compose 1.6.0 `resolve_extends`（L2364）对服务级 extends 执行
  `rec_merge({}, base, current)`：dict 深合并（environment/labels 取键并集）、
  普通 list 追加、`command`/`entrypoint` 无条件整体替换；volumes 特殊：
  仅短语法字符串按 target 去重（覆盖方获胜并移至尾部），长语法 dict 不去重。
- `extends.file` 的相对路径在**解析阶段**（`_parse_compose_file`
  L2844-L2849）按引用它的 compose 文件目录重写为绝对路径——故 invoke 的
  绝对 `--file` + 任意 cwd 与栈目录内裸 podman-compose 两种方式都能解析
  `../_shared/base-rootless.yaml`（`overlay_core.run_compose` docstring 同源说明）。
- GPU 覆盖（`-f compose.gpu.yaml`）走的是**多文件 list 追加**链路，与
  extends 服务级继承互不影响，仍按本节上段只写新增设备。

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

双路径语义由 `overlay_core.smoke_stack(c, QUANT_SPEC)` 统一实现（quant.py
不再私有副本），分支行为不变：栈在运行 → `podman-compose exec -T quant
<main python> <script>`；
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
