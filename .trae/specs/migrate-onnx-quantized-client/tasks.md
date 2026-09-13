# onnx-quantized 迁移至 apps/containers/client - 实施计划

> 任务依赖链：T1 → T2 → T3 → T4 → T5（运行验证）；T6/T7 为治理与文档，可在 T3 后并行，但完成证据须在 T5 后补齐。

## Task 1: 提取三个纯 ONNX 冒烟脚本为独立文件

- **Status**: `completed`
- **Priority**: `high`
- **Depends On**: None
- **Completion Evidence**:
  - TR-1.1 PASS：`python -m py_compile` 三文件全部通过（输出 PY_COMPILE_ALL_OK）
  - TR-1.2 PASS：逐行对照源 Dockerfile L208-331——节点（Gemm/Relu/Mul/Add）、维度（10×5 / 8×4 / 16→32→8）、种子 42、权重缩放（*0.1 与 1/sqrt(fan_in)）、QInt8/QDQ/per_channel/MinMax、raw=True、opset 18、ir_version≤9、阈值 5.0 全部一致；仅做格式化与溯源头注释改造
  - TR-1.3 PASS：smoke/ 目录 grep `torch|onnxoptimizer` 零命中
  - 产物：overlays/onnx-quantized/smoke/{smoke_dynamic_int8,smoke_fp16,smoke_static_qdq}.py
- **Description**:
  - 新建目录 `apps/containers/client/overlays/onnx-quantized/smoke/`
  - 将源 `variants/onnx-quantized/Dockerfile` Stage 3 内嵌的 QSMOKE / FP16SMOKE / STATICSMOKE 三段 heredoc 逐字提取为：
    - `smoke_dynamic_int8.py`（动态 INT8，Gemm 10×5，种子 42，权重 *0.1）
    - `smoke_fp16.py`（FP16，Gemm+Mul+Add 8×4）
    - `smoke_static_qdq.py`（静态 QDQ，两层 MLP 16→32→8 + RandomCalib）
  - 保持断言阈值（`md < 5.0`）、固定种子、`raw=True`、opset 18、`ir_version=min(...,9)`、CPUExecutionProvider 不变；仅做「独立可执行」改造（添加 `print()` 完成行、`sys.exit` 非零即失败语义由断言天然提供；不引入 pytest 依赖）
  - 每个文件头部中文注释注明来源（派生产物溯源：源 Dockerfile Stage 3 段落）
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-1.1: 三文件存在且 `python -m py_compile` 全部通过（语法零错误）；证据：编译命令输出
  - `rule` TR-1.2: 与源 heredoc 逐行语义比对——节点结构/维度/种子/权重缩放/量化 API 参数（QInt8、QDQ、per_channel、MinMax）/阈值一致；证据：人工对照勾选表
  - `rule` TR-1.3: 文件中不出现 torch/onnxoptimizer 导入；证据：grep 零命中
- **Notes**: 脚本运行依赖量化包，本机执行验证在 T5 随镜像进行；本任务只保证语法与语义等价。

## Task 2: 编写 Containerfile.quantized 与 overlay .env.example

- **Status**: `completed`
- **Priority**: `high`
- **Depends On**: T1
- **Completion Evidence**:
  - 版本真源核实：源 onnx-dev/Dockerfile L52-60 为浮动 pip（无 pin），版本固定改以 RELEASE.md v2.0.0 实测矩阵为准（onnx 1.22.0 / onnxruntime 1.28.0 / onnx-simplifier 0.7.3 / onnxscript 0.7.1 / onnxconverter-common 1.16.0），来源已写入 Containerfile 头注释（TR-2.1 PASS）
  - TR-2.2 PASS：grep 确认无 ENTRYPOINT/CMD 指令行（仅注释说明不覆盖）、无 `SHELL [`、无 `--privileged`；三个 RUN 全部 `/bin/bash -lc` 包裹；嵌套引号经 WSL bash 实测 python3 正确接收（输出 quoting OK）
  - TR-2.3 PASS：Py_GIL_DISABLED / _is_gil_enabled / find_spec(torch|onnxoptimizer) 守卫齐备；3 个 smoke 构建期调用 + devuser 访问验证齐备（grep L79-103）
  - TR-2.4 待 T3 完成后做键集合 diff（.env.example 已落 10 键：QUANT_IMAGE_TAG/QUANT_CONTAINER_NAME/QUANT_SSH_PORT/QUANT_JUPYTER_PORT/QUANT_WORKSPACE/USER_PASSWORD/JUPYTER_TOKEN/GRANT_SUDO/OMP_NUM_THREADS/PIP_MIRROR）
  - 产物：Containerfile.quantized（3 层：五包+守卫 / COPY smoke / 构建期冒烟）、.env.example
- **Description**:
  - 先读取 `apps/docker-images/devcontainer-base/variants/onnx-dev/Dockerfile`，提取五包在 cp314t main 环境的真实固定版本（onnx/onnxruntime/onnx-simplifier/onnxscript；onnxconverter-common 以源 onnx-quantized 层 RELEASE 版本矩阵 1.16.0 为辅证），记录到构建注释；禁止臆造版本
  - 新建 `overlays/onnx-quantized/Containerfile.quantized`：
    - `ARG BASE_IMAGE=localhost/jupyter-podman-rootless:latest` + `ARG PIP_MIRROR=official`（镜像源装 pip 时按需使用 index URL，沿用 rootless/Containerfile.client 既有写法而非自创）
    - 所有 RUN 用 `/bin/bash -lc '...'` 显式包裹（OCI 忽略 SHELL 教训）
    - 直接使用 PATH 顶端 `/opt/conda/envs/main/bin/python -m pip`（不 conda activate）
    - 安装 onnx/onnxruntime/onnx-simplifier/onnxscript/onnxconverter-common（版本固定）；`--no-cache-dir`；末尾清理 build 残留与 `~/.cache/pip`
    - ENV 四件套：`OMP_NUM_THREADS=4` `OPENBLAS_NUM_THREADS=1` `OMP_WAIT_POLICY=PASSIVE` `KMP_DUPLICATE_LIB_OK=TRUE`
    - 构建期守卫单 RUN：`sysconfig Py_GIL_DISABLED==1` + `sys._is_gil_enabled() is False` + `find_spec("torch") is None` + `find_spec("onnxoptimizer") is None`
    - `COPY smoke/ /opt/onnx-quantized-smoke/` 后在构建期顺序执行 3 个脚本
    - LABEL：`org.specweave.component=onnx-quantized`、`org.specweave.base-image=${BASE_IMAGE}` 等治理标签
    - 不写 ENTRYPOINT/CMD/USER 切换残留（沿用基底 root 主进程 + supervisord 模型）
  - 新建 `overlays/onnx-quantized/.env.example`：compose 插值变量模板（QUANT_IMAGE_TAG/QUANT_CONTAINER_NAME/QUANT_SSH_PORT/QUANT_JUPYTER_PORT/QUANT_WORKSPACE/USER_PASSWORD/JUPYTER_TOKEN/GRANT_SUDO/OMP_NUM_THREADS/PIP_MIRROR），逐项中文注释与默认值
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-2.1: 五包版本号均可在源 onnx-dev/Dockerfile（或 RELEASE.md）找到出处，Containerfile 注释列明来源；证据：来源行对照
  - `rule` TR-2.2: Containerfile 中无 `ENTRYPOINT`/`CMD`/`--privileged`/`SHELL [` 指令；所有 RUN 为 `/bin/bash -lc` 包裹；证据：grep 勾选
  - `rule` TR-2.3: 守卫与 3 冒烟调用在文件中齐备（Py_GIL_DISABLED、_is_gil_enabled、find_spec×2、3 个 smoke 路径）；证据：grep 输出
  - `rule` TR-2.4: `.env.example` 变量集合与 T3 compose.yaml 的 `${...}` 插值键完全一致（无孤儿键、无未文档化键）；证据：键集合 diff

## Task 3: 编写 compose.yaml 与 GPU 覆盖文件

- **Status**: `completed`
- **Priority**: `high`
- **Depends On**: T2
- **Completion Evidence**:
  - TR-3.1 PASS（备选路径）：宿主无 podman-compose（WSL Ubuntu），以 PyYAML 解析 + 键断言替代——name/单服务 quant/三必需（devices /dev/fuse、security_opt label=disable、cgroupns host）/端口/长语法 bind（create_host_path=true）/build 段/labels/restart 全部断言通过（.temp/validate_compose.py 输出 YAML_MERGE_OK）
  - TR-3.2 PASS：grep 无 privileged/x-podman 实际字段（仅注释引用知识包）、无短语法 bind
  - TR-3.3 PASS：模拟 list 追加合并 → [/dev/fuse:/dev/fuse, /dev/dri:/dev/dri]，无重复映射
  - 附：键集合 diff 首次发现 3 个未文档化插值键（QUANT_WORKSPACE/SSH_PUBLIC_KEY/OPENBLAS_NUM_THREADS），已补入 .env.example，复检零缺失（TR-2.4 同步 PASS）
  - 产物：compose.yaml、compose.gpu.yaml（仅新增设备一行）
- **Description**:
  - 新建 `overlays/onnx-quantized/compose.yaml`（知识包 concepts/03/08 模式）：
    - `name: onnx-quantized`；单服务 `quant`
    - `image: ${QUANT_IMAGE_TAG:-localhost/onnx-quantized:latest}` + `build.context=.` / `dockerfile: Containerfile.quantized` / `args.PIP_MIRROR`
    - 端口 `${QUANT_SSH_PORT:-2222}:22`、`${QUANT_JUPYTER_PORT:-8888}:8888`
    - workspace 一律**长语法 bind**（source `${QUANT_WORKSPACE:-../../workspace}`、target `/workspace`），显式 `bind.create_host_path: true`（workspace 与 socket 不同，允许创建；路径由任务侧默认解析为绝对 POSIX）
    - rootless 三必需标准字段：`devices: [/dev/fuse]`、`security_opt: [label=disable]`、`cgroupns: host`
    - environment：USER_PASSWORD/JUPYTER_TOKEN/GRANT_SUDO/OMP_NUM_THREADS 等全部走 `${VAR:-default}` 插值
    - labels：`org.specweave.component: onnx-quantized`（compose 自动补 io.podman.compose.* 标签，供 SDK 接缝）
    - `restart: unless-stopped`
  - 新建 `compose.gpu.yaml`：仅覆盖 devices（合并 /dev/dri；注释 CDI 形态 `--device nvidia.com/gpu=all` 的用法与限制），不含其他差异；由 `-f compose.yaml -f compose.gpu.yaml` 叠加
  - 不使用非必要 x-podman 字段；不写 bind 短语法；不写 privileged
- **Acceptance Criteria Addressed**: AC-3, AC-U1
- **Test Requirements**:
  - `rule` TR-3.1: 若本机有 podman-compose，`podman-compose -f compose.yaml config` 与叠加 `-f compose.gpu.yaml config` 均退出码 0，渲染含三必需键；无工具时以 PyYAML 解析 + 键断言替代并记录；证据：config/解析输出
  - `rule` TR-3.2: 两个 YAML 全文无 `privileged`、无 `- ./xxx:/xxx` 短语法挂载、无 `x-podman`（除非在评审中给出不可替代理由）；证据：grep
  - `rule` TR-3.3: 默认渲染 GPU 设备缺席，叠加 gpu 覆盖后出现；证据：两次 config 的 devices 段对比

## Task 4: 新增 quant 任务模块、命名空间注册与可选依赖

- **Status**: `completed`
- **Priority**: `high`
- **Depends On**: T3
- **Completion Evidence**:
  - TR-4.1 PASS：py314 下 `import jpman_client.tasks.quant` 成功；`invoke --list` 共 23 任务 = 7 根 + 7 container + 3 env + 6 quant，原 17 个一个不少
  - TR-4.2 PASS：grep 仅命中文档字符串中的「禁止 import podman」说明，无真实导入；pyproject 核心 dependencies 零 diff，新增 `[project.optional-dependencies] compose = ["podman-compose>=1.0.0"]`
  - TR-4.3 PASS：Windows 平台门禁实测输出中文双路径指引并 Exit（PLATFORM_GATE_OK）；缺二进制分支经 monkeypatch shutil.which→None 实测输出 pip 安装指引并 Exit（BINARY_GATE_OK；注：py314 已装 podman-compose.EXE）
  - TR-4.4 PASS：quant.up/quant.build --help 中文渲染正常，长选项齐备
  - 产物：src/jpman_client/tasks/quant.py（6 任务，纯子进程，复用 _project_root/_load_env_overrides/to_posix_path/detect_runtime/run_cmd/check_runtime_ready）、__init__.py 注册、pyproject.toml compose extra
- **Description**:
  - 新建 `src/jpman_client/tasks/quant.py`，6 个 invoke 任务：
    - `build`：`detect_runtime()` + `podman build -f .../Containerfile.quantized -t <tag> <overlay-dir>`（透传 `--no-cache`、`--pip-mirror`、`--base-image`）
    - `up`：解析配置后 `podman-compose -f compose.yaml [--project-name onnx-quantized] up -d --build`；`--gpu` 追加 `-f compose.gpu.yaml`
    - `down`：`podman-compose ... down`（可选 `--volumes`）
    - `ps`：`podman-compose ... ps`
    - `logs`：`podman-compose ... logs -f --tail=<n>`（默认 100）
    - `smoke`：优先对运行栈 `exec quant /opt/conda/envs/main/bin/python /opt/onnx-quantized-smoke/<script>`；栈未运行时降级为 `podman run --rm <img> <python> <script>`（冒烟纯 CPU，无须三必需之外的特权；仍经 run_cmd）
  - 实现要点（NFR-5 复用）：
    - 复用 `manage._project_root` / `_load_env_overrides`（root .env → os.environ，override=False）
    - 复用 `utils.to_posix_path` / `detect_runtime` / `run_cmd` / `check_runtime_ready`
    - overlay 根目录常量 `_quant_overlay_dir() = _project_root()/"overlays"/"onnx-quantized"`
    - 默认 QUANT_WORKSPACE 解析为 client/workspace 绝对路径并 `to_posix_path`，注入子进程环境
  - 平台门禁（AC-5）：
    - Windows 原生（`platform.system()=="Windows"` 且非 WSL 内）：任何 quant 任务开头输出中文原因 + 路径一（WSL2 发行版执行）路径二（`invoke env.run-cmd` 进自举容器后执行）并 `raise Exit(1)`
    - POSIX 下 `shutil.which("podman-compose")` 缺失：输出 `pip install -e ".[compose]"`（或容器内已内置说明）并 Exit(1)
  - `__init__.py` 注册 `Collection("quant")` 6 任务；ns.configure 增加 quant 默认段（image/container/ports/workspace）
  - `pyproject.toml` 增加 `[project.optional-dependencies] compose = ["podman-compose>=1.0.0"]`；核心 dependencies 不动
  - 模块**禁止 import podman**（纯子进程层）
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-4.1: `python -c "import jpman_client.tasks.quant"` 在 py314 环境无异常；`invoke --list` 输出含 6 个 quant. 任务且原有 17 个任务（7 根+7 别名+3 env）一个不少；证据：命令输出
  - `rule` TR-4.2: `grep -R "import podman" quant.py` 零命中；pyproject dependencies 数组 diff 为空、新增 compose extra；证据：grep + diff
  - `rule` TR-4.3: Windows 门禁与缺二进制门禁各有单元级验证（可用 monkeypatch/直接函数级调用断言 Exit；若无既有测试目录则以最小内联 python -c 调用来留证）；证据：执行记录
  - `rule` TR-4.4: 各任务 `--help` 渲染成功且 help 文本为中文；证据：invoke <task> --help 输出

## Task 5: 构建与端到端验证（runtime 门）

- **Status**: `completed`
- **Priority**: `high`
- **Depends On**: T2, T3, T4
- **Completion Evidence**（podman machine Fedora 43 / podman 5.7.1 / 真 podman-compose，经 `podman machine ssh` 在 WSL 内执行）：
  - TR-5.1 PASS：`invoke quant.build --pip-mirror tuna` exit=0；守卫打印 cp314t+GIL off+torch/torchvision/onnxoptimizer absent；构建期 3 冒烟 PASS；镜像 COMMIT localhost/onnx-quantized:latest（1.40 GB）；inspect 标签含 org.specweave.component/base-image，Entrypoint 沿用 [tini -- entrypoint.sh]、CMD 空、workdir /workspace
  - TR-5.2 PASS：真实 `podman-compose config` 默认渲染含 cgroupns/label=disable//dev/fuse，叠加 gpu 后 devices=[/dev/fuse,/dev/dri] 无重复；`inv quant.up` 后 2222 收 SSH banner（OpenSSH_10.2）、8888 HTTP 302；exec 路径冒烟 3/3（0.001914/0.000211/QDQ 10 节点 0.014510）；`inv quant.down` 后 ps -a 与 network ls 零残留；栈未运行时 `podman run --rm` 兜底冒烟 3/3
  - TR-5.3 PASS：`podman ps --filter label=io.podman.compose.project=onnx-quantized --filter label=...service=quant` 命中运行容器（标签接缝）；`invoke --list` 23 任务、`invoke images` 等既有命令正常
  - TR-5.4 rubric 自评 5/5：最终链路一次通过，中文指引连贯（含构建前置基底检查），双冒烟路径与清理闭环完整；过程中 2 个真实缺陷（onnx-simplifier pin、OCI 嵌套引号）已在 T2 修复并固化注释/规则，无残留资源
- **Description**:
  - 预检 podman machine（WSL2）：不可用则按 Spec Mode 置 blocked，Blocked By 写明，不伪造运行证据
  - 确保 `localhost/jupyter-podman-rootless:latest` 存在（缺失则提示 `invoke load`，不代为构建基底）
  - 执行：`invoke quant.build` → `podman-compose -f compose.yaml config` → `invoke quant.up` → 端口/进程验证（SSH 2222、Jupyter 8888）→ `invoke quant.ps` → `invoke quant.smoke` → `invoke quant.logs`（短暂）→ GPU 覆盖 config 渲染验证（不要求真 GPU）→ `invoke quant.down`
  - 验证 SDK 接缝：up 后用现有 SDK/CLI 路径能按 `io.podman.compose.project=onnx-quantized` 标签发现容器（`podman ps --filter label=...`）
  - 零回归回归：`invoke --list` 比对、`invoke run --help` 签名未变
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-U1
- **Test Requirements**:
  - `rule` TR-5.1: 量化镜像构建退出码 0，守卫 3 项 + 构建期冒烟 3 项在日志中可见 PASS；证据：日志关键行
  - `rule` TR-5.2: up 后两端口可连通（nc/tcp 探测或 podman port 输出），smoke 6/6 通过，down 后容器与网络被清理（podman ps -a / network ls 无残留）；证据：命令输出
  - `rule` TR-5.3: 按标签过滤能发现 compose 栈容器（接缝证据）；现有命令零回归（任务数/签名）；证据：filter 输出与 --list 对比
  - `rubric` TR-5.4: E2E 顺畅度（中文提示可理解、失败可诊断）；scale 1-5；anchors 1=中途裸错无指引/残留资源，3=成功但需手工排障，5=一次通过且中文指引连贯、清理干净；threshold >= 4；证据：完整执行流水

## Task 6: AI 治理资产同步（规则/路由/配置/变更记录）

- **Status**: `completed`
- **Priority**: `medium`
- **Depends On**: T4
- **Completion Evidence**:
  - TR-6.1 PASS：新增 `.agents/rules/quant-overlay.md`（9 节：边界/双门禁/三必需映射表/深合并/变量优先级/镜像契约/标签接缝/冒烟双路径/选型依据，知识包相对链接 5 处）；client AGENTS.md 路由表+核心入口+嵌套树+P0 C11+源码真源 6 模块全部同步；.agents/README.md 资产表/对应关系表/新增规则流程（3→4 文件）同步
  - TR-6.2 PASS：根 `.env.example` 新增 quant 栈段（12 键，与 overlay .env.example 一致，注明门禁与两处 .env 关系）；`.agents/CHANGELOG.md` 新增 2026-09-13 完整七概念条目；apps/AGENTS.md 三处 client 描述（路由表/嵌套树/边界表，3→4 rules）同步
  - TR-6.3 PASS：check-links.py 对 apps/containers/client「通过：所有本地引用均存在」（4 个目录警告为 skills/commands 既有条目，非本次引入）；无 file:///
- **Notes**: 4 个指向 overlay README 的断链在 T7 文档就位后复检归零。
- **Description**:
  - 新增 `.agents/rules/quant-overlay.md`：quant 命名空间契约（子进程边界、平台门禁、compose 字段↔rootless 三必需映射表、.env 优先级、GPU opt-in、知识包引用路径相对化）
  - 更新 `AGENTS.md`：项目概述中「没有 Compose」表述修正为「根运行路径无 Compose；quant.* opt-in 工作负载走 podman-compose」；上下文路由表新增 quant 行；嵌套路由树补 overlays/ 与 quant.py；P0 约束新增 1 条（quant 层禁止 import podman/禁止 privileged/Windows 门禁）或在新 rule 文件承载并在速览表登记
  - 更新根 `.env.example`：新增 `# quant.* 叠加栈` 段（与 overlay .env.example 键名一致，注明两处的关系：root .env 为任务侧事实源）
  - 更新 `.agents/CHANGELOG.md`：新增本次迁移条目（refactor/feat 性质与决策四连）
  - 更新 `.agents/README.md` 若其中列有 rules 索引
  - 同步 `apps/AGENTS.md` client 行描述（compose opt-in 能力）
- **Acceptance Criteria Addressed**: AC-6, AC-7, AC-U3
- **Test Requirements**:
  - `rule` TR-6.1: 新规则文件存在且被 AGENTS.md 路由表引用；路由树包含 overlays/onnx-quantized 与 quant.py；证据：文件与链接
  - `rule` TR-6.2: 根 .env.example QUANT_* 段键集合与 overlay .env.example 一致；CHANGELOG 有 2026-09-13 条目；证据：diff
  - `rule` TR-6.3: 全仓新增引用无 file:/// 绝对路径、无断链（运行仓库链接检查脚本针对变更目录）；证据：check-links 输出

## Task 7: 人类文档迁移与互链

- **Status**: `completed`
- **Priority**: `medium`
- **Depends On**: T3, T6
- **Completion Evidence**:
  - TR-7.1 PASS：overlay README.md 新建（能力/版本实测矩阵/前置/inv 与裸 compose 两路径/端口凭证/3 冒烟/Docker 差异表/深度阅读）；两份深度指南迁入 docs/ 并加迁移溯源 banner；grep 仅剩 1 处 `--privileged -p 2375` 且明确位于「Docker 谱系（源）」对比列（旧路径标注，非推荐路径）；基准脚本 4 个失效链接改指源树（../../../../../docker-images/...）并加「Docker 谱系共享资产」说明
  - TR-7.2 PASS：链接检查全通过（含 overlay README↔源 README、知识包、C11 规则、client README §12）；`git status -- apps/docker-images/devcontainer-base/variants/onnx-quantized` 空（源零改动，单向互链）
  - TR-7.3 rubric 自评 5/5：新人可按 README 从 machine 就绪→load 基底→quant.build→up（含 WSL 门禁与 --gpu）→smoke→down 走完整闭环，含故障指引（基底缺失/缺二进制/Windows 门禁）与实测版本矩阵；最终 rubric 由独立审查复核
  - 产物：overlays/onnx-quantized/{README.md, docs/ADVANCED-QUANTIZATION-GUIDE.md, docs/QUANTIZATION-BEST-PRACTICES.md}、client README.md §12 + §4 命令表 3 行
- **Description**:
  - 新建 `overlays/onnx-quantized/README.md`：能力简介（五包+三模式）、前置（rootless 基底 + podman machine）、两条使用路径（`invoke quant.*` 与裸 `podman-compose`）、端口/凭证/workspace 说明、GPU opt-in、与源 Docker 变体的关系与差异表（DinD→rootless、docker→podman-compose、构建链→薄叠加）
  - 迁移并改写两份深度指南到 `overlays/onnx-quantized/docs/`：
    - `ADVANCED-QUANTIZATION-GUIDE.md`：量化技术内容保留；所有 `/opt/conda/envs/main/bin/python` 路径保持有效；部署/构建章节替换为 compose 语境
    - `QUANTIZATION-BEST-PRACTICES.md`：去除 `docker run --privileged` 等 DinD 主路径指令，替换为 rootless/compose 等价写法；frontmatter/来源注记（源文档相对路径）
  - 在 client 根 `README.md` 增加「工作负载叠加层：onnx-quantized」小节（快速入口 + 链接）
  - 互链：overlay README ↔ 源变体 README（相对路径，跨 apps 分组 `../../../docker-images/devcontainer-base/variants/onnx-quantized/README.md`）；源文件零改动（单向链接即可，或仅在本次评审明确后反向加链——默认不反向以遵守「源零改动」）
  - T5 完成后把实测版本矩阵/验证结果补入 overlay README
- **Acceptance Criteria Addressed**: AC-7, AC-U2
- **Test Requirements**:
  - `rule` TR-7.1: 三份文档就位，迁移文档中 Docker 专属主路径指令（`--privileged`、`docker build -f variants/...`、2375 DinD 端口作为推荐路径）已清除或明确标注为「旧 Docker 谱系」；证据：grep + 走读
  - `rule` TR-7.2: 互链相对路径全部可达；源目录 `git status -- apps/docker-images/devcontainer-base/variants/onnx-quantized` 为空；证据：链接检查 + git status
  - `rubric` TR-7.3: 文档可操作性（新人按 README 能独立完成 build→up→量化→down）；scale 1-5；anchors 1=断步骤/路径失效，3=能走通但需猜测，5=步骤闭环含故障指引与 WSL 说明；threshold >= 4；证据：文档走读

## 实施顺序备注

- T1-T4 为静态可交付，互不阻塞地串行实施；T5 是唯一 runtime 门，阻塞时其余任务继续。
- 所有提交点由用户显式要求后再执行（atomic-commit-cmd）；实施过程中不自动 commit。
