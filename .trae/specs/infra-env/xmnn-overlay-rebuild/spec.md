# xmnn scratch 栈按 onnx-quantized 范式重建 - Product Requirements Document

## Overview
- **Summary**: 将 `apps/containers/client/.temp/notebook/xmnn-whl-builder/` 的 podman-compose scratch 栈**推倒重建**：不再以 `external/chaos/ai/xmnn-whl-builder`（Docker/BuildKit 谱系）的构建上下文/源码树为依赖，而是完全对齐同族正式叠加层 `apps/containers/client/overlays/onnx-quantized/` 的范式——栈目录内自包含 Containerfile（多阶段从**预构建镜像**的 wheel 分发目录取 wheel，FROM Podman rootless 基底薄叠加）、compose 内联 build 段、smoke 脚本烤入镜像并在构建期执行、长语法 bind、rootless 三必需、双端口与 entrypoint 凭证环境变量。
- **Purpose**: 旧栈对 `external/chaos/` 存在三重**目录级耦合**（compose.build.yaml 的 context 指向 chaos 根、build-compose.sh 临时 patch chaos 的 .dockerignore、compose.sources.yaml bind chaos 源码树），导致栈目录不可移动、跨机器不可复现、构建需 wrapper 且触碰外部只读源树。重建后栈目录自包含，`external/chaos/` 仅作为事实参考（版本/验证项出处），构建与运行均不读取该目录。
- **Target Users**: 在 WSL2 `podman-machine-default` 内以 podman-compose 驱动 notebook 工作负载的单机开发者（与上一期相同用户画像）。

## Goals
- **G1（脱钩）**: 栈的构建与运行路径中不存在任何对 `external/chaos/` 目录或宿主源码树的引用：无 `CHAOS_ROOT`、无 `.dockerignore` patch/wrapper、无 `npu_tvm/npuusertools` bind；构建上下文 = 栈目录自身（`context: .`）。
- **G2（谱系对齐）**: 新增栈内 `Containerfile.xmnn`：多阶段构建，dist 阶段仅为 wheel 来源（`FROM ${XMNN_DIST_IMAGE}`，默认 `localhost/xmnn-whl-builder:latest`，COPY `/opt/xmnn-dist/*.whl`），final 阶段 `FROM localhost/jupyter-podman-rootless:latest`，把 wheel 装入 **base env（/opt/conda，cp314 GIL）**并注册 `xmnn-whl-builder` 内核，产出 `localhost/xmnn-notebook:latest`。
- **G3（compose 范式）**: `compose.yaml` 对齐 onnx 叠加层——image+build 共存内联、长语法 bind→`/workspace`、三必需标准字段、entrypoint 四凭证变量（USER_PASSWORD/JUPYTER_TOKEN/SSH_PUBLIC_KEY/GRANT_SUDO）、22/8888 双端口、org.specweave labels、restart 策略；不覆盖 ENTRYPOINT/CMD（沿用 tini→entrypoint.sh→supervisord）。
- **G4（环境实证保留）**: 保留 `network_mode: bridge`（S1：2026-09-14 同机实测 onnx 栈默认项目网络同样 aardvark-dns 失败，与镜像谱系无关）；移除 `healthcheck: disable`（S2 根因消除：rootless 基底镜像 Config 无 Healthcheck，实证）。
- **G5（冒烟双路径）**: `smoke/` 纯 Python 脚本 COPY 入镜像并在构建期执行（守卫 + tvm.build LLVM 向量加 + devuser 可执行）；运行期可 `podman-compose exec` 复跑；`workspace/smoke.ipynb` 继续承担内核 UX 验证（nbconvert 指定 xmnn-whl-builder 内核）。
- **G6（自包含文档）**: README/AGENTS/.agents 规则随结构重写，所有相对链接可达；删除旧三文件（compose.sources.yaml、compose.build.yaml、build-compose.sh）。

## Non-Goals
- **不编译 wheel**：不运行 Nuitka/scikit-build 构建（10-30 分钟），不接触 npu_tvm/npuusertools 源码；wheel 唯一来源是预构建镜像内 `/opt/xmnn-dist/`（其 Dockerfile 明确保留该目录「供下游 runtime 镜像 COPY 使用」）。
- 不迁入 `overlays/`、不新增 invoke 命名空间、不修改 client `src/jpman_client/`（scratch 纪律不变，正式化仍须另立 spec）。
- 不修改 `external/chaos/` 与 `overlays/onnx-quantized/` 任何文件（只读参考）。
- 不提供 GPU/CDI 覆盖文件（本机 nvidia CDI 不可用、VTA 走 sim；需要时按 onnx 的 compose.gpu.yaml list 追加范式另立 opt-in 文件）。
- 不发布 SSH 之外的额外服务；不做镜像推送/远程 registry。
- 不创建 git commit（`.temp/` 被 .gitignore 排除；如用户要求仅提交 `.trae/specs/` 规划文档，另行原子提交）。

## Background & Context
- **旧栈现状（2026-09-13 交付）**：compose.yaml（消费预构建镜像，显式 command 拉 jupyter lab，bridge+healthcheck disable）+ compose.sources.yaml（bind chaos 源码）+ compose.build.yaml（context=${CHAOS_ROOT}，dockerfile=ai/xmnn-whl-builder/Dockerfile）+ build-compose.sh（BUILDAH_FORMAT=docker + .dockerignore globstar/行内注释 sed patch/restore）+ .env.example（9 变量含 CHAOS_ROOT/NPU_TVM_HOST/NPUUSERTOOLS_HOST）+ workspace/smoke.ipynb + 自治文档。
- **2026-09-14 重建前实证（本 spec 事实基础）**：
  1. `podman images`：`localhost/xmnn-whl-builder:latest`（5.2GB）、`localhost/jupyter-podman-rootless:latest`（1.19GB）、`localhost/onnx-quantized:latest`（1.4GB）均在机内。
  2. `podman run --rm --no-healthcheck xmnn-whl-builder ls /opt/xmnn-dist` → `xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`（187,896,958 字节，2026-09-08）。
  3. rootless 基底 `/opt/conda/bin/python` = 3.14.7 **cp314 GIL enabled**（`Py_GIL_DISABLED=0`、`sys._is_gil_enabled()=True`）；main env = 3.14.7 cp314t；两 env 均在。wheel 为 cp314-cp314 ABI（requires-python>=3.14.6），**直接匹配 base env，无需 conda 升级**（chaos Dockerfile 的 py314-base 阶段针对的是 Docker 谱系 devcontainer-base 的旧 base env，对 rootless 基底不适用）。
  4. rootless 基底：Entrypoint=tini→entrypoint.sh，Config **无 Healthcheck 字段**；ExposedPorts 22/8888；supervisord 托管 jupyter（user=devuser、directory=/workspace、config=/home/devuser/.jupyter/jupyter_notebook_config.py）与 sshd；故 notebook 根目录即 `/workspace`，bind target 由旧栈 `/workspace/notebooks` 改为 `/workspace`（与 onnx 一致）。
  5. 在 machine 内对**未改动的 onnx 栈**执行 `podman-compose up -d`：复现 `aardvark-dns failed to start: Failed to connect to user scope bus`（容器停 Created）——证明 S1 是 machine 无 systemd user bus 的环境事实，非 chaos 镜像特有；down 后零残留。
  6. 旧 chaos 镜像直接 `podman run` 不挂 `--no-healthcheck` 即报 `unable to get systemd connection to add healthchecks`；rootless 基底无 HEALTHCHECK，新镜像无需该字段（构建后 inspect 复核）。
- **onnx-quantized 范式要点（quant-overlay.md 规则 + overlay 实测）**：Containerfile 薄叠加、RUN 全部显式 `/bin/bash -lc`（OCI 格式构建器兼容，不依赖 SHELL 指令）、含引号验证逻辑固化为脚本文件（OCI 二次分词教训）、不覆盖 ENTRYPOINT/CMD/WORKDIR、构建期守卫固化于 `smoke/_quant_guards.py`、compose build 段内联（context: .）、裸 `podman-compose build` 无需 wrapper。
- **wheel 依赖**（pyproject.toml，参考）：numpy/scipy/pandas/matplotlib/Pillow/onnx/protobuf/openpyxl/tabulate/rich/tqdm/tomlkit/decorator/attrs/psutil/cloudpickle/typing_extensions/pytest/telnetlib3；torch 系为 optional extra，核心依赖不含。chaos 构建链已于 2026-09 在 cp314 GIL 上 pip 解析成功。
- **内核 ABI 不可变**：Jupyter 服务在 main env（cp314t）；内核 argv 必须是 `/opt/conda/bin/python`（base env cp314 GIL），内核规格目录名 `xmnn-whl-builder`；对 devuser 可见的系统级位置为 `/opt/conda/envs/main/share/jupyter/kernels/xmnn-whl-builder/`。
- **方法论**：seven-concepts 场景 3（重构优化 I→F→A→C）；F 推导的 V 对抗审查由 Spec Mode 独立审查承担；配置冲突裁决依据 OKF G1 知识包 podman-compose bundle（concepts/02/03/06/08/10）与 client `.agents/rules/quant-overlay.md`。

## Functional Requirements
- **FR-1（自包含 Containerfile）**: 栈目录新增 `Containerfile.xmnn`：
  - `ARG XMNN_DIST_IMAGE=localhost/xmnn-whl-builder:latest` + `FROM ${XMNN_DIST_IMAGE} AS xmnn-dist`（仅取 `/opt/xmnn-dist/*.whl`）；
  - `ARG BASE_IMAGE=localhost/jupyter-podman-rootless:latest` + `FROM ${BASE_IMAGE} AS runtime`；
  - 以 `/opt/conda/bin/pip`（base env，cp314 GIL）安装 COPY 来的 wheel 及其依赖（不装可选 torch extra）；PIP_MIRROR build-arg（official/aliyun/tuna）与 onnx Containerfile 同构；
  - COPY 内核注册脚本与 smoke/，注册内核到 main env 系统级 kernelspec 目录，构建期运行守卫+冒烟（root 与 devuser 两种身份）；
  - 不写 SHELL/HEALTHCHECK 指令，不覆盖 ENTRYPOINT/CMD/WORKDIR；携带 org.specweave.* LABEL。
- **FR-2（内核注册资产）**: 内核注册逻辑固化为脚本文件（如 `scripts/register-kernel.sh`），无内联嵌套双引号 python -c；生成 kernel.json：argv=`/opt/conda/bin/python -m ipykernel_launcher -f {connection_file}`，display_name 沿用 `Python 3.14 (xmnn whl-builder)`，env.PATH 以 `/opt/conda/bin` 为首；构建期断言 main env `jupyter kernelspec list` 可见且 devuser 身份同样可见。
- **FR-3（smoke 资产）**: `smoke/_xmnn_guards.py`（守卫：base 解释器为 cp314 **GIL enabled**、xmnn 版本串、wheel bootstrap .pth 生效、_libs 含 libtvm.so）与 `smoke/smoke_tvm.py`（import tvm/vta/xmnn + tvm.build('llvm') 固定向量加法断言，参考 verify-wheel.sh 第 1/5 项语义），均可用 `/opt/conda/bin/python <script>` 直接运行，不依赖工作区挂载。
- **FR-4（compose 主栈）**: `compose.yaml` 服务名 `xmnn`，`name: xmnn-whl-builder`；image `${XMNN_IMAGE_TAG:-localhost/xmnn-notebook:latest}` 与内联 build（context `.`、dockerfile `Containerfile.xmnn`、args 透传 BASE_IMAGE/XMNN_DIST_IMAGE/PIP_MIRROR）共存；container_name 插值；`network_mode: bridge`；端口 `${XMNN_SSH_PORT:-2222}:22` 与 `${XMNN_JUPYTER_PORT:-8888}:8888`；workspace 长语法 bind（source `${XMNN_WORKSPACE:-./workspace}` → target `/workspace`，create_host_path: true）；devices /dev/fuse、security_opt label=disable、cgroupns host；environment 仅 USER_PASSWORD/JUPYTER_TOKEN/SSH_PUBLIC_KEY/GRANT_SUDO 四键（${VAR:-} 插值）；labels org.specweave.component/managed-by/base；restart: unless-stopped；无 command、无 healthcheck 段。
- **FR-5（参数模板）**: `.env.example` 只保留新栈实际插值键：XMNN_IMAGE_TAG、XMNN_CONTAINER_NAME、XMNN_SSH_PORT、XMNN_JUPYTER_PORT、XMNN_WORKSPACE、USER_PASSWORD、JUPYTER_TOKEN、SSH_PUBLIC_KEY、GRANT_SUDO、PIP_MIRROR，以及注释形式的构建参数 XMNN_DIST_IMAGE/BASE_IMAGE；删除 CHAOS_ROOT/NPU_TVM_HOST/NPUUSERTOOLS_HOST。
- **FR-6（旧文件删除）**: 删除 `compose.sources.yaml`、`compose.build.yaml`、`build-compose.sh`（含其全部 wrapper 逻辑）；删除后栈目录无任何可执行构建包装器，构建命令就是 `podman-compose build`。
- **FR-7（文档重写）**: README.md 改为 onnx 风格（前置条件含两本地镜像、裸 compose 路径、参数表、构建说明、双冒烟、已知 machine 行为、与 onnx 叠加层/external chaos 的关系表）；AGENTS.md 与 `.agents/rules/compose-stack.md` 更新定位（S1 保留、S2 移除、S5 改为「自包含构建、禁止 wrapper 回归」、内核 ABI 节保留、新增 wheel 来源说明）；`.agents/README.md` 资产索引同步。
- **FR-8（notebook 冒烟）**: `workspace/smoke.ipynb` 保持 nbformat 4.x、kernelspec name=`xmnn-whl-builder`；内容为 tvm/vta/xmnn 导入与 tvm.build LLVM 向量加（期望 [2.0,3.0,4.0,5.0]）；容器内路径随 bind 变为 `/workspace/smoke.ipynb`。

## Non-Functional Requirements
- **NFR-1（范式保真）**: 每条非平凡写法可指认 OKF 知识包章节（02 rootless、03 patterns、06 插值/深合并、08 标准字段优先、10 选型）或 quant-overlay.md 条款；唯一环境偏差 `network_mode: bridge` 必须有 2026-09-14 实测注释。
- **NFR-2（零外部接触）**: 构建在断网 external 目录的意义上自包含——除两个 `localhost/` 基底镜像与 PyPI（经 PIP_MIRROR）外不读取宿主任何路径；构建前后 external/chaos 工作树 mtime/内容零变化。
- **NFR-3（rootless 安全）**: 无 privileged、无 docker.sock、无 host 网络；宿主端口 ≥1024；三必需与 C11 同源（cgroupns 在 podman-compose 1.6.0 空操作的事实须在注释中声明，不宣称运行时生效）。
- **NFR-4（可清理/幂等）**: down 后项目容器与网络为零、bind 宿主文件保留；重复 build/up/down 幂等；构建不产生命名卷。
- **NFR-5（scratch 最小侵入）**: 全部产物限本目录 + `.trae/specs/xmnn-overlay-rebuild/`；client 产品代码、external/、overlays/onnx-quantized/ git 状态零变化；.temp/ 仍不入库。
- **NFR-6（可复跑构建）**: 构建仅数分钟量级（wheel COPY + pip 依赖，无编译），可作为日常验证手段真实执行，而非只做静态检查。

## Constraints
- **Technical**:
  - 仅在 WSL2 `podman-machine-default`（rootless UID 1000、无 systemd user bus、journald 无 journal）内运行；podman 5.7.1、podman-compose 1.6.0；Windows 原生不运行（同 quant 门禁认知）。
  - 构建期两个本地镜像必须存在：`localhost/jupyter-podman-rootless:latest`（1.19GB）与 wheel 源镜像（默认 `localhost/xmnn-whl-builder:latest`，可经 build arg 替换）；二者均不得触发远程 pull。
  - wheel ABI 约束：只能装入 base env（cp314 GIL）；内核 argv 固定 `/opt/conda/bin/python`；服务进程仍在 main env。
  - 9p 路径：栈目录经 `/mnt/d/spaces/SpecWeave/...` 在 machine 内访问；构建上下文为 9p 上的小目录（仅脚本/元数据，无海量文件）。
  - OCI 构建纪律：所有 RUN 显式 `/bin/bash -lc`；含引号验证一律脚本文件；不依赖 SHELL 指令（因此裸 `podman-compose build` 可直接产出可运行镜像，无需 BUILDAH_FORMAT hack）。
- **Business**: `.temp/` gitignored 实验区，不入库、不登记父级路由；external/chaos 只读参考。
- **Dependencies**: 构建需要 PyPI（或镜像源）网络以下发 wheel 的 19 个核心依赖；运行期无网络依赖。

## Assumptions
- PyPI/镜像源可提供 cp314 GIL 所需全部依赖 wheel（chaos 构建链 2026-09 已实证同一解析；若个别包仅有 sdist，构建期以实际 pip 输出为证据，必要时换源不换栈结构）。
- rootless 基底 main env 的 JupyterLab 版本满足 notebook 7/jupyter_server 用法（基底 2026-09-12 构建；E2E 以 /lab=200 与 nbconvert 实际结果裁决，不臆测版本）。
- 空 USER_PASSWORD/JUPYTER_TOKEN 时沿用基底 entrypoint「自动生成并打印」契约；machine 日志不可得时以 `jupyter server list` 与显式 .env 凭证为操作路径（S4 教训保留）。
- 镜像标签 `localhost/xmnn-notebook:latest` 作为新栈产出标识（区分于 Docker 谱系 xmnn-whl-builder:latest）；如用户在审批时要求改名，仅改默认值不改结构。
- 8888/2222 端口空闲（旧栈与 onnx 测试栈均已 down，当前 machine 零容器）。

## Acceptance Criteria

### AC-1: 外部目录耦合清除（静态门禁）
- **Type**: `rule`
- - **Given**: 重建后的栈目录
- **When**: 检查文件清单并对功能性文件（compose*.yaml、Containerfile*、.env.example、scripts/*、smoke/*）grep `CHAOS_ROOT|external/chaos|NPU_TVM_HOST|NPUUSERTOOLS_HOST|\.dockerignore|docker-wrapper`
- **Then**: compose.sources.yaml/compose.build.yaml/build-compose.sh 三文件不存在；grep 在功能性文件中 0 命中（文档/变更日志中「不依赖」的事实性说明除外）
- **Pass Condition**: 文件不存在且 grep 0 命中
- **Evidence**: 目录树 + grep 命令输出

### AC-2: compose 配置静态正确性
- **Type**: `rule`
- **Given**: machine 内栈目录
- **When**: `podman-compose config` 退出码与输出
- **Then**: 退出码 0；输出含恰好 1 服务 xmnn；build.context 归一化为栈目录绝对路径、dockerfile=Containerfile.xmnn；两端口 2222/8888；network_mode=bridge；三必需字段各 1；恰好 1 个 bind（target=/workspace）；四凭证 env 键；无 healthcheck 段；无 command 段
- **Pass Condition**: 上述断言逐项成立（grep 计数实证）
- **Evidence**: config 输出摘要入 tasks.md

### AC-3: 自包含镜像真实构建
- **Type**: `rule`
- **Given**: 两个 localhost 基底镜像在机内
- **When**: 在栈目录执行裸 `podman-compose build`（不 source 任何 wrapper、不 export BUILDAH_FORMAT）
- **Then**: 构建退出码 0；构建日志含守卫 `[OK]` 与 smoke_tvm 通过及 devuser 执行通过；`localhost/xmnn-notebook:latest` 出现在 podman images；镜像 inspect 无 Healthcheck、Entrypoint 为 tini/entrypoint
- **Pass Condition**: 4 项全成立
- **Evidence**: 构建日志关键行、images 行、inspect 输出

### AC-4: 构建不触碰 external/chaos
- **Type**: `rule`
- **When**: 构建前后比对 `external/chaos` 工作树（git status / 关键文件 mtime）并复核构建全程命令 cwd 与上下文
- **Then**: external/chaos 无任何修改/mtime 变化、无 `.podman-compose-bak-*` 类残留；构建上下文路径位于栈目录
- **Pass Condition**: 前后快照一致
- **Evidence**: 构建前后 git status 与 mtime 快照

### AC-5: Notebook 栈 E2E 可用
- **Type**: `rule`
- **When**: `podman-compose up -d` 后等待服务；curl `http://127.0.0.1:8888/lab`；探测 2222/tcp；exec 以 main env jupyter 列 kernelspec 并以 base python 导入三包
- **Then**: /lab HTTP 200（或 302 跳登录）；2222 端口可连；kernelspec 含 `xmnn-whl-builder`，其 argv[0]=/opt/conda/bin/python 且 devuser 身份可见；`/opt/conda/bin/python -c "import tvm,vta,xmnn"` 退出码 0；容器内 `/workspace/smoke.ipynb` 可见
- **Pass Condition**: 5 项全过
- **Evidence**: curl 状态码、端口探测、kernelspec JSON、exec 输出、ls

### AC-6: notebook 内核冒烟
- **Type**: `rule`
- **When**: exec 执行 `jupyter nbconvert --to notebook --execute --ExecutePreprocessor.kernel_name=xmnn-whl-builder --output /tmp/smoke-out.ipynb /workspace/smoke.ipynb`
- **Then**: 退出码 0；输出无 error；含 tvm.build 向量加结果 [2.0, 3.0, 4.0, 5.0]
- **Pass Condition**: 退出码 0 且结果断言成立
- **Evidence**: nbconvert 输出摘要

### AC-7: 运行期 smoke 脚本复跑
- **Type**: `rule`
- **When**: `podman-compose exec -T xmnn /opt/conda/bin/python /opt/xmnn-smoke/smoke_tvm.py` 与 `... _xmnn_guards.py`
- **Then**: 两者退出码 0，输出含 tvm.build 成功行与守卫 OK 行
- **Pass Condition**: 两脚本退出码 0
- **Evidence**: exec 输出

### AC-8: 清理与幂等
- **Type**: `rule`
- **When**: `podman-compose down` 后列举项目标签容器/网络；再次 up→smoke→down 一轮
- **Then**: down 后 `io.podman.compose.project=xmnn-whl-builder` 容器与项目网络均为零；./workspace 宿主文件保留；第二轮 up/down 同样成功
- **Pass Condition**: 残留为零且第二轮幂等通过
- **Evidence**: podman ps/network 输出、两轮记录

### AC-9: 零侵入
- **Type**: `rule`
- **When**: 主仓库 `git status --porcelain`（.temp 应不可见）、external/chaos 与 overlays/onnx-quantized 各自工作树状态
- **Then**: 主仓库仅出现 `.trae/specs/xmnn-overlay-rebuild/` 新增（如阶段已落盘）；.temp 无追踪项；两个只读参考区 clean
- **Pass Condition**: 三项断言成立
- **Evidence**: 三处 git status 摘要

### AC-10: onnx 范式保真度
- **Type**: `rubric`
- **Dimension**: 栈结构/compose 写法/Containerfile 纪律与 onnx-quantized 叠加层及 quant-overlay.md、OKF 知识包的对齐度
- **Scale**: 1-5
- **Anchors**: 1 = 仍依赖外部构建上下文或引入 wrapper/x-podman 偏方/特权；3 = 结构对齐但 ≥2 处偏离无注释依据；5 = 文件集与写法与 onnx 范式一一对应，每条偏差（仅 bridge 一条）有实证与知识包/规则注释
- **Pass Threshold**: >= 4
- **Evidence**: reviewer 逐文件对照表

### AC-11: 产物原子性与文档一致性
- **Type**: `rubric`
- **Dimension**: 最少必要文件集、单一职责、README/AGENTS/rules 与实际结构一致、相对链接全可达
- **Scale**: 1-5
- **Anchors**: 1 = 残留失效文件/文档描述与实现矛盾/坏链；3 = 存在 1-2 处冗余或过时描述；5 = 每文件职责单一、文档与实现逐条一致、链接全通
- **Pass Threshold**: >= 4
- **Evidence**: 目录树 + 链接校验 + reviewer 逐文件说明

## Open Questions
- 新镜像产出标签默认 `localhost/xmnn-notebook:latest`（结构无关，审批时可改名）。
- 是否在收尾时原子提交 `.trae/specs/xmnn-overlay-rebuild/` 规划文档（默认不提交，待用户明示）。
