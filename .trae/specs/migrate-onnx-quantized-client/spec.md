# onnx-quantized 迁移至 apps/containers/client（Podman rootless + podman-compose 编排）- 产品需求文档

## Overview

- **Summary**：将 `apps/docker-images/devcontainer-base/variants/onnx-quantized`（Docker DinD 谱系的 ONNX 量化工具链变体）以 **Podman rootless 薄叠加镜像 + podman-compose 声明式栈 + client 侧 opt-in invoke 命名空间** 的形态，完整迁移至 `apps/containers/client`。
- **Purpose**：让 ONNX 量化工作负载脱离 Docker 4 层继承链（base→conda-llvm→onnx-dev→onnx-quantized），在 client 既有的「rootless 基底 + tar 加载 + SDK/CLI 消费」体系内可声明式地构建、起停与验证；编排机制以 OKF podman-compose 知识包为唯一权威设计依据。
- **Target Users**：在 WSL2/Linux/macOS 上使用 client 消费端运行 ONNX 模型量化（动态/静态 INT8、FP16、QDQ）的开发者与 AI 智能体。

## Goals

- 在 client 内新增量化工作负载叠加镜像（FROM `localhost/jupyter-podman-rootless:latest`），在 conda **main 环境（cp314t，GIL 禁用）**中提供 onnx/onnxruntime/onnx-simplifier/onnxscript/onnxconverter-common 五包。
- 以 `compose.yaml` 声明整个量化栈：端口、workspace 绑定、rootless 三必需、环境变量、GPU opt-in 覆盖；通过 `podman-compose` 子进程驱动。
- 在 client 新增 opt-in 的 `quant.*` invoke 命名空间（build/up/down/ps/logs/smoke），与现有 SDK→CLI 两层**并行且零回归**。
- 迁移源变体的三份人类文档（README/高级指南/最佳实践）并改写为 Podman rootless 语境；同步 client AI 治理资产。
- 保留源 Docker 变体目录原样（torch-dev→ai-dev 构建拓扑不断链），两处文档互链。

## Non-Goals

- **不修改、不删除** `apps/docker-images/` 下任何文件（源变体仅只读引用）。
- **不把 podman-compose 引入现有 `invoke run` 路径**：不新增第三层后端，不改动 C3/C4（rootless 三必需硬编码、`get_client()` 零回归）所辖代码路径。
- 不迁移 neural-compressor（源变体即「按需自装，需 torch」策略，保持不变）。
- 不迁移 torch-dev/ai-dev 依赖链，不做 Docker→Podman 全谱系收敛。
- 不引入多服务（model-registry、Redis 等）；本期栈仅 1 个服务。
- 不在宿主侧捆绑 podman-compose 安装（提供可选 extra；rootless 基底镜像内已内嵌）。
- 不迁移 RELEASE.md / .devcontainer / Docker 专属构建脚本（variants/build.sh、test-onnx-quantized.sh 留在源谱系）。

## Background & Context

- **源资产本质（I 阶段事实）**：onnx-quantized 的可迁移内容 = ① main 环境 5 个 pip 包；② 3 段构建期纯 ONNX 冒烟测试（固定种子 42、Xavier 缩放、`max_diff<5.0`）；③ 2 份深度量化文档 + 1 份发布说明。其 Docker 载体（supervisord DinD、variant-framework.sh、build-info、24 项 shell 测试）属于 Docker 谱系机制，不是量化能力本身。
- **环境同构（F 阶段依据）**：rootless 基底与 onnx-dev 目标环境同构——均为 Ubuntu 26.04 + `/opt/conda/envs/main`（Python cp314t free-threading）+ PATH 顶端为 main/bin + SSH/Jupyter/supervisord。五包在 cp314t 的可安装性已由 Docker 链构建验证。
- **client 现状约束**：AGENTS.md 明确「没有构建流程、没有 Compose、没有 ML 模型管理」，架构为 podman-py SDK（优先）→ CLI fallback；Windows 11 WSL2 是差异化场景。
- **知识包裁决（G1 可信源）**：podman-compose 是 daemon-less 声明式编排器（YAML→podman argv 子进程），与 podman-py 互补——「compose 负责栈生命周期写标签、SDK 负责命令式运维读标签」是天然接缝；rootless 三必需可 1:1 映射为标准 compose 字段（`devices`/`security_opt`/`cgroupns`）；构建端已有 Windows 原生门禁经验（short syntax 触发 `os.makedirs` 在宿主建错误目录 → 长语法 + `create_host_path:false`；Windows 原生 compose 子进程不可用 → WSL/容器内执行）。
- **用户裁决（2026-09-13）**：① 完整迁移；② FROM rootless:latest；③ opt-in 独立命名空间；④ 源目录保留原样。
- **既有可复用机制**：`utils.py`（`to_posix_path`/`detect_runtime`/`run_cmd`/`check_runtime_ready`/`build_passthrough_spec`）、`env_in_container.py`（CLI 子进程 + rootless 三必需拼参模式）、构建端 compose.yaml/compose.passthrough.*.yaml 分层模式。

## Functional Requirements

- **FR-1 叠加镜像**：client 内提供 `overlays/onnx-quantized/Containerfile.quantized`，FROM `localhost/jupyter-podman-rootless:latest`（可 ARG 覆盖），在 main 环境安装五包并写入 OMP 调优 ENV；构建期执行 cp314t/GIL/torch 缺席守卫与 3 个冒烟测试；不覆盖 ENTRYPOINT/CMD。
- **FR-2 冒烟脚本**：源 Dockerfile 内嵌的 3 段 Python（动态 INT8 / FP16 / 静态 QDQ）提取为 `smoke/` 下 3 个独立可执行脚本，行为与断言阈值保持一致；镜像构建期执行，且可对运行中容器/镜像重复执行。
- **FR-3 声明式栈**：提供 `compose.yaml`（单服务 `quant`），含镜像/构建、SSH+Jupyter 端口、workspace 绑定（长语法）、rootless 三必需、密码/token/OMP 环境变量、`org.specweave.*` 标签；GPU 以 `compose.gpu.yaml` 覆盖文件 opt-in（默认 `/dev/dri`，CDI 写注释），默认全关。
- **FR-4 quant 命名空间**：新增 `invoke quant.build/up/down/ps/logs/smoke`；统一解析 root `.env`（`load_dotenv(override=False)`）与 compose 默认值；`up` 支持 `--gpu` 叠加覆盖文件；compose 二进制缺失/平台不支持时给可执行中文诊断并以非零码退出。
- **FR-5 平台门禁**：Windows 原生 CPython 下 quant 命令直接门禁（不执行 podman-compose 子进程），指引改用 WSL2 发行版或 client 自举容器；WSL2/Linux/macOS 正常。
- **FR-6 依赖姿态**：pyproject.toml 新增可选 `compose = ["podman-compose>=1.0.0"]` extra，核心依赖不新增。
- **FR-7 文档与治理**：overlay README 快速开始；两份深度指南迁入并去除 Docker DinD 专属内容、改写 rootless 段落；新增 client `.agents/rules/quant-overlay.md`；同步 AGENTS.md 路由、README、`.env.example`、`.agents/CHANGELOG.md`；与源变体双向互链。

## Non-Functional Requirements

- **NFR-1 零回归**：现有根命名空间（load/images/save/run/stop/status/clean）、`container.*`、`env.*` 命令签名与行为零改动；现有 10 条 P0 约束（C1-C10）不受影响。
- **NFR-2 知识保真**：量化语义、版本矩阵、负向守卫（torch/onnxoptimizer 缺席）与源变体一致；版本号以 `variants/onnx-dev/Dockerfile` 实际固定值为真源（禁止臆造）。
- **NFR-3 安全姿态延续**：默认隔离（GPU/透传全关）；严禁 `--privileged`；workspace 挂载源路径经 `to_posix_path` 转换；socket 类/不存在的挂载源不得在宿主自动创建错误目录。
- **NFR-4 可发现性**：`invoke --list` 能看到全部 quant 子命令；所有命令 `--help` 中文说明完整。
- **NFR-5 原子化**：新增文件按单一职责组织；任务模块复用 utils 既有助手，不重复实现路径转换/运行时检测。
- **NFR-6 公开内容合规**：全部产物落 apps/containers/client/ 内（公开开源代码）；不写入 `.agents/docs/`；Markdown 路径引用相对化。

## Constraints

- **Technical**：Python ≥ 3.14（宿主 py314）；OCI 镜像格式忽略 SHELL 指令（RUN 须 `/bin/bash -lc` 包裹，沿用 Containerfile.client 教训）；构建上下文必须小（overlay 目录自包含，不 COPY client 全树）；podman-compose v1.x（知识包基线 1.6.0）。
- **Business**：遵循 Conventional Commits 中文提交（本期不代为提交，除非用户要求）；scikit-build-core 构建后端不变。
- **Dependencies**：运行时需要 daemon 侧已存在 rootless 基底镜像与运行中的 podman machine（Windows 即 WSL2）；五包 wheel 可达性依赖 pip 镜像源（支持 PIP_MIRROR build-arg）。

## Assumptions

- 实施环境可访问 WSL2 podman machine 做构建/E2E 验证；若 machine 不可用，运行型验证（镜像构建/up/smoke）按 Spec Mode 记 `blocked` 并请用户解除，静态型验证（compose config/YAML/import）不受影响。
- 源 `variants/onnx-dev/Dockerfile` 中五包版本可直接提取并用于固定；若个别 wheel 在 rootless 基底（同为 cp314t）安装失败，优先复现源链版本，不擅自换包。
- rootless 基底已内嵌 podman-compose/podman-py（容器内路径可用）；宿主侧 POSIX 通过 `[compose]` extra 获得。

## Acceptance Criteria

### AC-1: 量化叠加镜像可构建且守卫完备

- **Type**: `rule`
- **Given**: daemon 侧存在 `localhost/jupyter-podman-rootless:latest`
- **When**: 在 `apps/containers/client` 执行 `invoke quant.build`（或等价 `podman build -f overlays/onnx-quantized/Containerfile.quantized`）
- **Then**: 产出 `localhost/onnx-quantized:latest`；构建日志含 cp314t/GIL 禁用/torch 缺席三项断言通过；五包均可在 `/opt/conda/envs/main/bin/python` 下导入；ENTRYPOINT/CMD 未被覆盖
- **Pass Condition**: 构建退出码 0 且镜像 inspect 存在；守卫输出 PASS
- **Evidence**: 构建日志摘录 + `podman image inspect` 标签输出

### AC-2: 三个纯 ONNX 冒烟脚本行为等价且可重复执行

- **Type**: `rule`
- **Given**: 量化镜像已构建
- **When**: 构建期执行 3 脚本，且宿主执行 `invoke quant.smoke`
- **Then**: 动态 INT8 / FP16 / 静态 QDQ 三个脚本均退出码 0，打印各自 `[OK]` 行与 max_diff（阈值 <5.0）；脚本文件与源 Dockerfile 内嵌逻辑（种子 42、raw=True、opset 18、ir_version≤9）逐行语义一致
- **Pass Condition**: 6 次执行（3 构建期 + 3 inv）全通过；代码评审确认等价
- **Evidence**: smoke/ 三个文件 + 执行输出

### AC-3: compose.yaml 是合法且 rootless 安全的声明式栈

- **Type**: `rule`
- **Given**: overlays/onnx-quantized 下 compose.yaml 与 compose.gpu.yaml
- **When**: 执行 `podman-compose -f compose.yaml config` 校验，并 `up -d` 后验证
- **Then**: config 渲染成功且包含 `devices:/dev/fuse`、`security_opt:label=disable`、`cgroupns:host`，全文件无 `privileged`；workspace 为长语法 bind；栈启动后 SSH 端口（默认 2222）与 Jupyter（8888）可连通；默认不启用 GPU；`--gpu` 时设备节点出现在渲染配置
- **Pass Condition**: config 退出码 0；up 后端口探测成功；down 可清理
- **Evidence**: config 输出、up/ps/down 日志、端口探测结果

### AC-4: quant.* 命名空间完整且现有命令零回归

- **Type**: `rule`
- **Given**: client 以 editable 安装
- **When**: 执行 `invoke --list`
- **Then**: 列出 quant.build/up/down/ps/logs/smoke 共 6 个任务，且原有 load/images/save/run/stop/status/clean、container.* 7 个别名、env.* 3 个任务数量与签名不变；quant 模块不 import podman SDK（走子进程）
- **Pass Condition**: 命令计数前后一致（新增仅 quant 6 个）；静态检查 quant.py 无 `from podman` / `import podman`
- **Evidence**: `invoke --list` 前后对比、grep 结果

### AC-5: Windows 原生门禁与缺失依赖诊断

- **Type**: `rule`
- **Given**: Windows 原生 CPython（非 WSL）或未安装 podman-compose 的 POSIX
- **When**: 执行任一 `invoke quant.*`
- **Then**: Windows 原生直接输出中文原因 + 两条可执行路径（WSL2 内运行 / `invoke env.run-cmd` 自举容器内运行）并 Exit(1)；POSIX 缺二进制时输出 `pip install -e ".[compose]"` 提示并 Exit(1)；不产生任何 podman-compose 子进程或宿主残留目录
- **Pass Condition**: 两路径各手工验证一次退出码=1 且文案含指引；检查无多余目录创建
- **Evidence**: 命令输出截图/文本

### AC-6: 可选依赖与配置优先级

- **Type**: `rule`
- **Given**: pyproject.toml 与 quant 任务实现
- **When**: 审查依赖声明与变量解析
- **Then**: `dependencies` 无新增；存在 `[project.optional-dependencies] compose`；变量优先级为 shell 显式 export > root `.env`（override=False）> compose.yaml `${VAR:-default}`；`.env.example` 新增 QUANT_* 段且与代码键名一一对应
- **Pass Condition**: 四项逐一核对通过
- **Evidence**: pyproject.toml diff、.env.example、代码走读

### AC-7: 文档迁移与 AI 治理同步、源目录零改动

- **Type**: `rule`
- **Given**: 迁移完成后的工作树
- **When**: 核对文档/治理资产与源目录 git 状态
- **Then**: overlay README + 两份深度指南就位且为 rootless 语境（无 `docker run --privileged` 等 DinD 指令作为主路径）；`.agents/rules/quant-overlay.md` 新增；client AGENTS.md/README/CHANGELOG 已同步；源目录 `git status` 干净；新旧文档双向链接存在
- **Pass Condition**: 每个就位项可点击打开；源目录零 diff；链接无 file:/// 与断链
- **Evidence**: 文件树、git status、链接检查输出

### AC-U1: 与 podman-compose 知识包的架构对齐度

- **Type**: `rubric`
- **Dimension**: 编排设计与 OKF podman-compose 知识包（concepts/02、03、06、07、08、10）的一致性
- **Scale**: 1-5
- **Anchors**: 1 = 照搬 Docker compose 习惯、出现短语法挂载/Windows 不兼容/特权容器；3 = 能跑通但 x-podman 滥用或 .env 双源混乱；5 = 标准字段优先、x-podman 零不必要使用、override 分层与变量插值清晰、compose 标签可被 SDK 侧按标签发现（接缝成立）、门禁策略与构建端一致
- **Pass Threshold**: >= 4
- **Evidence**: compose 文件、任务代码、与知识包条目对照走读

### AC-U2: 量化能力迁移保真度

- **Type**: `rubric`
- **Dimension**: 相对源变体的量化语义与工程约束保真
- **Scale**: 1-5
- **Anchors**: 1 = 丢包/丢守卫/冒烟阈值被放宽；3 = 包齐但版本漂移无据或文档残留 Docker 专属步骤；5 = 五包版本取自源 Dockerfile 真源、三守卫与 3 冒烟全保留、OMP 调优一致、文档完成 DinD→rootless 语境改写且能力边界（neural-compressor 可选）说明清楚
- **Pass Threshold**: >= 4
- **Evidence**: 版本提取对照、冒烟代码 diff 走读、文档走读

### AC-U3: client 工程整洁度

- **Type**: `rubric`
- **Dimension**: 单一职责 / DRY / 可发现性 / 中文文案质量
- **Scale**: 1-5
- **Anchors**: 1 = 逻辑堆砌、重复实现路径转换/运行时检测；3 = 功能完整但模块边界模糊；5 = quant.py 单一编排职责、复用 utils 助手与 env_in_container 模式、目录自描述、中文诊断可执行
- **Pass Threshold**: >= 4
- **Evidence**: 代码走读

## Open Questions

- 无（四项架构歧义已于 2026-09-13 由用户裁决；实施中若发现 cp314t wheel 不可用等技术性阻塞，按 blocked 升级而非自行换方案）。
