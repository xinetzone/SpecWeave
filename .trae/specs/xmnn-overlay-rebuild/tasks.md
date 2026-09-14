# xmnn scratch 栈按 onnx-quantized 范式重建 - Implementation Plan

> 方法链路：I（旧栈三重外部耦合）→ F（自包含薄叠加的第一性推导）→ A（文件级原子任务）→ C（按任务收尾）；
> V 对抗审查由 Review 阶段 fresh-context 独立审查承担。所有命令在 WSL2 `podman-machine-default`
> 内栈目录 `/mnt/d/spaces/SpecWeave/apps/containers/client/.temp/notebook/xmnn-whl-builder` 执行。

## Task 1: 自包含镜像资产（Containerfile.xmnn + 内核注册脚本 + smoke 脚本）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 新增 `Containerfile.xmnn`：两阶段——`FROM ${XMNN_DIST_IMAGE:-localhost/xmnn-whl-builder:latest} AS xmnn-dist`（仅 COPY 源，不取其文件系统其他内容）与 `FROM ${BASE_IMAGE:-localhost/jupyter-podman-rootless:latest}`；`COPY --from=xmnn-dist /opt/xmnn-dist/*.whl /tmp/xmnn/`；用 `/opt/conda/bin/pip` 装入 **base env**（PIP_MIRROR 三段判断同 onnx 范式），装后清理 wheel 临时副本与 pip cache；base env 安装 ipykernel；COPY `scripts/` 与 `smoke/`，执行内核注册脚本；构建期以 root 跑 `_xmnn_guards.py` + `smoke_tvm.py`，再以 devuser 复跑 smoke_tvm；完成横幅；LABEL org.specweave.*（component/layer/python-version=3.14-cp314-gil/conda-env=base/base-image/dist-image）。
  - 全部 RUN 显式 `/bin/bash -lc`，不使用 SHELL/HEALTHCHECK 指令，不覆盖 ENTRYPOINT/CMD/WORKDIR；任何含引号的 Python 逻辑只能落在被 COPY 的脚本文件中。
  - 新增 `scripts/register-kernel.sh`（set -euo pipefail；动态定位 main env jupyter 数据路径；写 `/opt/conda/envs/main/share/jupyter/kernels/xmnn-whl-builder/kernel.json`，argv[0]=`/opt/conda/bin/python`，env.PATH 以 /opt/conda/bin 为首、不含 CHAOS_ROOT；chmod a+rX；断言 root 与 `su -s /bin/bash devuser` 两身份 `jupyter kernelspec list` 均可见）。
  - 新增 `smoke/_xmnn_guards.py`：打印 tvm/vta/xmnn 版本；断言 base 解释器 `Py_GIL_DISABLED==0` 且 `sys._is_gil_enabled() is True`；断言 xmnn_bootstrap.pth 可在 site-packages 找到；断言 `_libs/libtvm.so` 存在。
  - 新增 `smoke/smoke_tvm.py`：import tvm/vta/xmnn；`tvm.build`（target='llvm'）向量加（n=4，A=[1,2,3,4]，*2 期望 [2,4,6,8] 或与 smoke.ipynb 一致的 +1 语义——实现时与 smoke.ipynb 统一为同一断言并在证据中注明）；固定随机/无外部数据；退出码非 0 即失败。
- **Acceptance Criteria Addressed**: AC-3, AC-7, AC-10
- **Test Requirements**:
  - `rule` TR-1.1: Containerfile 中 grep 不到 `external/chaos|CHAOS_ROOT|\.dockerignore|SHELL \[|HEALTHCHECK`；FROM 行恰好两个 localhost 默认值
  - `rule` TR-1.2: smoke 与 register-kernel 脚本均可被 `/opt/conda/bin/python`/bash 直接执行（文件语法：python -m py_compile、bash -n 通过）
  - `rubric` TR-1.3: onnx Containerfile 纪律对齐度；scale 1-5；anchors 1=出现内联嵌套引号 -c 或依赖 SHELL 指令或覆盖入口；3=基本对齐但有 1-2 处无注释偏离；5=显式 /bin/bash -lc、脚本固化、薄叠加层次、标签完整与 onnx 一一对应；threshold >= 4；evidence=reviewer 逐段对照

## Task 2: 重写 compose.yaml 与 .env.example
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - `compose.yaml` 按 spec FR-4 全量重写（onnx 范式 + machine 实证）：name= xmnn-whl-builder；服务 xmnn；image 与内联 build（context `.`、dockerfile Containerfile.xmnn、args BASE_IMAGE/XMNN_DIST_IMAGE/PIP_MIRROR）；`network_mode: bridge` 带 2026-09-14 onnx 同机复现实证注释；两端口；长语法 bind ./workspace→/workspace（create_host_path: true）；devices/security_opt/cgroupns 三必需（cgroupns 注释声明 1.6.0 空操作）；environment 四凭证键；labels；restart: unless-stopped；**无 command、无 healthcheck**；头注释引用 OKF concepts/02/03/06/08 与 quant-overlay.md。
  - `.env.example` 按 FR-5 重写：10 个生效键 + 2 个注释态构建参数；删除 CHAOS_ROOT/NPU_TVM_HOST/NPUUSERTOOLS_HOST；顶部注释说明优先级链（shell > .env > compose 默认）与 machine 内执行方式。
- **Acceptance Criteria Addressed**: AC-2, AC-10
- **Test Requirements**:
  - `rule` TR-2.1: `podman-compose config` 退出码 0，且输出满足 AC-2 全部逐项断言（服务数、端口、bridge、三必需、bind target=/workspace、四 env、无 healthcheck/command、build.context 绝对化、dockerfile 文件名）
  - `rule` TR-2.2: .env.example 键集合与 compose 插值键 diff 为空（注释态构建参数除外），grep 不到 CHAOS_ROOT/NPU_TVM/NPUUSERTOOLS
  - `rubric` TR-2.3: 与 onnx compose.yaml 的范式对齐度；scale 1-5；anchors 1=出现特权/短语法 bind/自定义 x-podman；3=可运行但偏差 ≥2 处；5=除 bridge（带实证注释）外逐行同构；threshold >= 4；evidence=逐行对照

## Task 3: 删除旧耦合文件并核对 smoke.ipynb
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 删除 `compose.sources.yaml`、`compose.build.yaml`、`build-compose.sh`（用 DeleteFile，不留 .bak）。
  - 核对 `workspace/smoke.ipynb`：kernelspec name 必须为 `xmnn-whl-builder`；确认其代码单元语义与新 `smoke/smoke_tvm.py` 断言一致；容器内新路径 `/workspace/smoke.ipynb`；如需修改仅改 notebook 内容，不改内核名。
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `rule` TR-3.1: 三文件在文件系统不存在（LS/Test-Path 实证）
  - `rule` TR-3.2: smoke.ipynb JSON 解析成功，metadata.kernelspec.name=="xmnn-whl-builder"，代码含 tvm.build 与期望向量断言

## Task 4: 静态门禁汇总（grep 脱钩 + config 断言）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3
- **Description**:
  - 对功能性文件全集执行 AC-1 grep 门禁；固化 `podman-compose config` 的 AC-2 断言输出；记录为验收证据。
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-4.1: AC-1 grep 0 命中（功能性文件范围），旧三文件不存在
  - `rule` TR-4.2: AC-2 断言清单逐项有命令输出佐证，全部通过后方可进入构建任务

## Task 5: 真实自包含构建与「外部零接触」证据
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 构建前快照：external/chaos 的 `git status` 与 `.dockerignore`/关键文件 mtime。
  - 在栈目录执行裸 `podman-compose build`（不 wrapper、不 export BUILDAH_FORMAT；PIP_MIRROR 默认按 compose 设定）。
  - 构建后：确认 `localhost/xmnn-notebook:latest` 存在、大小；inspect 无 Healthcheck、Entrypoint=tini→entrypoint.sh；复拍 external/chaos 快照证明零接触；确认无 `.podman-compose-bak-*`。
  - 若 pip 个别依赖在默认源解析失败：仅允许切换 PIP_MIRROR（aliyun/tuna）重试，不得改栈结构或引入 sdist 编译 hack；过程与结论入证据。
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-5.1: 构建退出码 0；日志含 root 身份 guards OK、smoke_tvm PASS、devuser 复跑 PASS、完成横幅
  - `rule` TR-5.2: podman images 含 localhost/xmnn-notebook:latest；inspect Healthcheck=<nil>、入口链正确
  - `rule` TR-5.3: external/chaos 构建前后 git status 与 mtime 快照逐项一致；无备份残留文件

## Task 6: 栈 E2E（up / 内核 / lab / nbconvert / 运行期 smoke / down / 幂等）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - `podman-compose up -d` → ps Up；curl `/lab`；2222/tcp 探测；exec 列 kernelspec（含 argv 核验与 devuser 可见性）；base python 导入 tvm/vta/xmnn；ls /workspace/smoke.ipynb。
  - nbconvert 执行 smoke.ipynb（kernel_name=xmnn-whl-builder）核验输出。
  - exec 运行镜像内 `/opt/xmnn-smoke/_xmnn_guards.py` 与 `smoke_tvm.py`。
  - down → 项目容器/网络零残留；再做一轮 up→nbconvert→down 证幂等。
  - 若遇 aardvark/healthcheck 类错误：属环境字段缺失/多余，回 Task 2 修 compose 后重验（禁止 x-podman 偏方）。
- **Acceptance Criteria Addressed**: AC-5, AC-6, AC-7, AC-8
- **Test Requirements**:
  - `rule` TR-6.1: AC-5 五项全过（200/302、2222 可连、kernelspec argv=/opt/conda/bin/python、三包导入、ipynb 可见）
  - `rule` TR-6.2: AC-6 nbconvert 退出码 0 且结果向量与期望一致
  - `rule` TR-6.3: AC-7 镜像内两脚本 exec 退出码 0
  - `rule` TR-6.4: AC-8 两轮 up/down 后标签容器与项目网络计数为零，workspace 宿主文件保留

## Task 7: 自治文档重写 + 链接与零侵入核查
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - README.md：onnx 风格重写（一句话定位、镜像/内核/服务表、前置双镜像、快速开始、参数表、构建说明强调无 wrapper、双冒烟、machine 已知行为仅保留 bridge 一条与日志不可得、与 onnx 叠加层及 external chaos 关系表）。
  - AGENTS.md：定位表改为「Podman rootless 谱系薄叠加 scratch 栈」；目录结构、路由表、P0 速览更新（S1 保留、S2 移除并注明根因消除、S5 改为自包含构建禁 wrapper、S6 scratch 纪律保留、内核 ABI 保留）；变更日志追加 2026-09-14 重建条目。
  - `.agents/README.md` 索引同步；`.agents/rules/compose-stack.md` 重写：S1（附 2026-09-14 onnx 同机复现证据）、S3 生效边界表保留、S4 更新为 entrypoint 凭证契约 + machine 取 token 路径、S5 全改为「自包含构建纪律」、新增 wheel 来源节（/opt/xmnn-dist 多阶段 COPY，非目录依赖）、内核 ABI 节保留、排障表更新。
  - 全栈 Markdown 相对链接批量校验（深 6-8 级相对路径，PowerShell Test-Path）；git 三处状态核查（AC-9）。
- **Acceptance Criteria Addressed**: AC-9, AC-11
- **Test Requirements**:
  - `rule` TR-7.1: 栈内所有 md 相对链接 Test-Path 全通过；无失效 external/chaos 路径链接（事实性引用须以「只读参考」措辞且路径真实存在）
  - `rule` TR-7.2: AC-9 git 状态三处断言成立（主仓库仅 .trae/specs/xmnn-overlay-rebuild/ 新增；.temp 不可见；external/chaos 与 overlays/onnx-quantized clean）
  - `rubric` TR-7.3: 文档与实现一致性；scale 1-5；anchors 1=文档仍描述旧三文件/旧 S2/旧路径；3=主要结构已更但有过时片段；5=README/AGENTS/rules 与新文件集、字段、命令逐条一致；threshold >= 4；evidence=reviewer 文档-实现交叉核对

## 完成证据汇总（2026-09-14，Implement+Verify 收尾）

| Task | 关键证据 |
|---|---|
| Task 1 | 四资产落盘：Containerfile.xmnn（两阶段、全局 ARG 置顶修正一次 `no FROM statement found`）、scripts/register-kernel.sh、smoke/_xmnn_guards.py、smoke/smoke_tvm.py；`bash -n` + `py_compile` 通过；TR-1.1 grep 0 命中 |
| Task 2 | compose.yaml/.env.example 重写；`podman-compose config` 退出 0 且 AC-2 全断言逐项成立；插值键 12 = .env 10 生效 + 2 注释态 |
| Task 3 | 旧三文件 DeleteFile 删除（LS 实证不存在）；smoke.ipynb JSON 合法、kernelspec.name=xmnn-whl-builder、断言 [2,3,4,5] |
| Task 4 | AC-1 脱钩 grep（Grep 工具）功能性文件 0 命中；AC-2 config 断言输出归档于本汇总 |
| Task 5 | 裸 `podman-compose build` 退出 0（aliyun，约 2 分钟，依赖全部 cp314 wheel 无编译）；日志含 root guards/smoke [OK] + devuser 复跑通过 + 完成横幅；产出 localhost/xmnn-notebook:latest（2.32GB）；inspect：tini→entrypoint.sh、Cmd=null、Healthcheck=<nil>、Workdir=/workspace；external/chaos 15 项 mtime 前后逐项一致、NO-BAK |
| Task 6 | 两轮 up→smoke→down：/lab=302、2222 SSH banner、devuser kernelspec 可见且 argv[0]=/opt/conda/bin/python、三包导入 OK、nbconvert 退出 0 含 [2.0,3.0,4.0,5.0]、镜像内两脚本 exec 退出 0；down 后项目容器/网络计数为零，宿主 workspace 保留 |
| Task 7 | README/AGENTS/.agents README/rules 四文档重写；PowerShell 链接校验 4 md 全通；主仓库 git status 仅 `?? .trae/specs/xmnn-overlay-rebuild/`，.temp 不可见，external/chaos 与 overlays/onnx-quantized clean |

**Review 结论**：fresh-context 独立审查 PASS（见 [review.md](review.md)）——AC-1~AC-9 全 pass，AC-10=5、AC-11=5；0 blocker/major/minor，2 nit 已在收尾处理（任务状态与证据补登；README pip 表述对齐实现为 `/opt/conda/bin/python -m pip`）。
