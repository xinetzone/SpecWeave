# xmnn-whl-builder → .temp/notebook podman-compose 迁移 - Implementation Plan

> 方法论：seven-concepts 场景3（I→F→A→C）。I/F 已在 Specify 完成；本文件为 A（原子化）产物。
> 目标根目录：`apps/containers/client/.temp/notebook/xmnn-whl-builder/`（下称 $STACK）。
> 所有命令在 `podman-machine-default` 内 `/mnt/d/spaces/SpecWeave/apps/containers/client/.temp/notebook/xmnn-whl-builder/` 执行。

## Task 1: 骨架与参数模板（.env.example）
- **Status**: `completed`
- **Priority**: `high`
- **Depends On**: None
- **Completion Evidence**:
  - TR-1.1 ✅ find 输出恰为 6 文件（compose×3/.env.example/build-compose.sh/workspace/smoke.ipynb）；`.env` 不存在。
  - TR-1.2 ✅ 8 个变量 `grep -cE '^(...)=' .env.example` = 8。
  - 自校正：XMNN_WORKSPACE 默认由计划的 `../../workspace` 改为 `./workspace`——FR-3 硬契约是 AC-2 的 `/workspace/notebooks/smoke.ipynb` 可见，工作区实际位于 $STACK/workspace，`./workspace` 才能与 smoke 交付物一致。
- **Description**:
  - 创建 `$STACK/` 与 `$STACK/workspace/` 目录。
  - 创建 `.env.example`：`XMNN_IMAGE_TAG`（默认 localhost/xmnn-whl-builder:latest）、`XMNN_CONTAINER_NAME`（xmnn-notebook）、`XMNN_JUPYTER_PORT`（8888）、`JUPYTER_TOKEN`（空=自动生成）、`XMNN_WORKSPACE`（默认 ../../workspace）、`NPU_TVM_HOST`/`NPUUSERTOOLS_HOST`（默认 /mnt/d/spaces/SpecWeave/external/chaos/{npu_tvm,npuusertools}）、`PIP_MIRROR`（aliyun）；逐项中文注释说明用途与默认。
  - 不创建真实 `.env`（.gitignore 已排除 .temp，仍保持纪律）。
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `rule` TR-1.1: 目录树存在 `$STACK/`、`$STACK/workspace/`、`$STACK/.env.example`；`.env` 不存在。证据：`find` 输出。
  - `rule` TR-1.2: .env.example 覆盖 FR-4/FR-5/FR-1 引用的全部 8 个插值变量，每个均有默认值注释。证据：grep 变量名计数=8。

## Task 2: compose.yaml 主运行栈
- **Status**: `completed`
- **Priority**: `high`
- **Depends On**: Task 1
- **Completion Evidence**:
  - TR-2.1 ✅ `podman-compose config` 退出 0，渲染含 image/8888:8888//dev/fuse/label=disable/cgroupns: host//workspace/notebooks。
  - TR-2.2 ✅ `grep -rnE 'privileged|docker\.sock' $STACK` 零命中。
  - TR-2.3 rubric=5：非平凡写法均标注 concepts 章节（02 端口/network_mode、03 服务模式、06 插值/合并、08 扩展克制）。
  - E2E 驱动两处实现期修复（知识包 02/03 标准字段，非 x-podman）：① `network_mode: bridge`——默认项目网络的 aardvark-dns 依赖 systemd user bus，machine（XDG_RUNTIME_DIR 空）报 "Failed to connect to user scope bus"；手工对照实测 bridge 下 nginx HTTP=200。② `healthcheck: disable: true`——镜像继承的 HEALTHCHECK 定时器同样依赖 systemd（"unable to get systemd connection to add healthchecks"）；实测翻译为 podman `[NONE]`，等价源 build.sh 全程使用的 --no-healthcheck。
  - token 语义证伪修正见 spec.md Assumptions（空串=免认证；journald 无 journal）。
- **Description**:
  - `name: xmnn-whl-builder`；单服务 `xmnn`：image/container_name 插值；`command` 为参数数组显式启动 `/opt/conda/envs/main/bin/jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --notebook-dir=/workspace/notebooks --ServerApp.token=${JUPYTER_TOKEN:-} --ServerApp.password=''`（空 token→自动生成并打印 logs）。
  - ports：`"${XMNN_JUPYTER_PORT:-8888}:8888"`。
  - 工作区长语法 bind（FR-3，create_host_path: true）；rootless 三必需标准字段（devices/security_opt/cgroupns）；labels org.specweave.{component,managed-by,source}；restart: unless-stopped。
  - 头注释引用知识包 concepts/02/03/06 章节与用法（up/down/logs/exec + 两 override 叠加示例）；不写任何 *.md。
  - 不设置 privileged/docker.sock/host 网络/SSH 端口。
- **Acceptance Criteria Addressed**: AC-1, AC-7, AC-8
- **Test Requirements**:
  - `rule` TR-2.1: `podman-compose config` 退出码 0，且输出可 grep 到 `xmnn-whl-builder:latest`、`8888`、`/dev/fuse`、`label=disable`、`cgroupns: host`、`/workspace/notebooks`。
  - `rule` TR-2.2: 全栈无 privileged 字符串：`grep -ri privileged $STACK/compose*.yaml` 无命中。
  - `rubric` TR-2.3: 知识包保真度；1-5；锚点同 AC-7；阈值 ≥4；证据：每条非平凡写法头注释标注 concepts 章节。

## Task 3: compose.sources.yaml（opt-in 源码挂载）
- **Status**: `completed`
- **Priority**: `medium`
- **Depends On**: Task 2
- **Completion Evidence**:
  - TR-3.1 ✅ 合并 config 恰 3 个 bind，target 集合 {/workspace/notebooks,/workspace/npu_tvm,/workspace/npuusertools}，源路径解析为 /mnt/d/spaces/SpecWeave/external/chaos/{npu_tvm,npuusertools}。
  - TR-3.2 ✅ 文件仅含 services.xmnn.volumes 单键；config 无报错。
- **Description**:
  - 仅含服务 `xmnn` 的 `volumes:` 列表，两条长语法 bind：`${NPU_TVM_HOST:-/mnt/d/spaces/SpecWeave/external/chaos/npu_tvm}:/workspace/npu_tvm`（create_host_path: false）与 npuusertools 同构；target 与主栈工作区不重叠。
  - 头注释说明 list 追加/按 target 去重语义（concepts/06 §深合并），叠加用法 `-f compose.yaml -f compose.sources.yaml`。
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-7
- **Test Requirements**:
  - `rule` TR-3.1: 合并 config 中 volumes 条目数=3，target 集合 = {/workspace/notebooks,/workspace/npu_tvm,/workspace/npuusertools}。证据：`podman-compose -f ... -f ... config` grep。
  - `rule` TR-3.2: 单文件 YAML 合法且不含 image/ports 等冗余键（只做追加）。证据：config 无报错 + YAML 键检查。

## Task 4: compose.build.yaml + build-compose.sh（opt-in 构建路径）
- **Status**: `completed`
- **Priority**: `medium`
- **Depends On**: Task 2
- **Completion Evidence**:
  - TR-4.1 ✅ 合并 config：context=/mnt/d/spaces/SpecWeave/external/chaos，dockerfile=ai/xmnn-whl-builder/Dockerfile，args PIP_MIRROR=aliyun。
  - TR-4.2 ✅ `bash -n` 通过；`bash build-compose.sh --help` 成功打印用法（脚本顶部 REPO_ROOT 6 级 cd 已成功解析）；BUILDAH_FORMAT export 与 trap restore 均在脚本中（静态）。
  - TR-4.3 ✅ sed 三表达式样例验证：`**/bar`→`*/bar`、`foo/**  # inline`→`foo/*`、全行注释→空行、normal 不变；restore 靠 mv 备份还原（trap EXIT/INT/TERM/HUP）。实际 build 未触发（Non-Goal，镜像已预构建）。
- **Description**:
  - `compose.build.yaml`：服务 `xmnn` 追加 `build.context: ../../../../../../external/chaos`（compose 文件向上 6 级到仓库根）、`dockerfile: ai/xmnn-whl-builder/Dockerfile`、`args.PIP_MIRROR: ${PIP_MIRROR:-aliyun}`；头注释注明前置 BUILDAH_FORMAT=docker 与 wrapper 用途。
  - `build-compose.sh`：set -euo pipefail；`export BUILDAH_FORMAT=docker`；定位 external/chaos/.dockerignore，存在则备份→sed（`**/`→`*/`、`**`→`*`、行内注释剥离）→trap restore；执行 `podman-compose -f compose.yaml -f compose.build.yaml build "$@"`；脚本支持 `--cn`（转 PIP_MIRROR=tuna）透传；含 usage 注释。
  - 不执行实际镜像构建。
- **Acceptance Criteria Addressed**: AC-1, AC-5, AC-7, AC-8
- **Test Requirements**:
  - `rule` TR-4.1: 合并 config 中 build.context 为 `/mnt/d/spaces/SpecWeave/external/chaos`（machine 视角绝对路径），dockerfile 字段正确。
  - `rule` TR-4.2: `bash -n build-compose.sh` 退出码 0；`bash -x` 干跑（带参数 `--cn` 到打印 podman-compose 行即止，可通过临时 `PODMAN_COMPOSE_DRY` 或 grep 函数体验证）可见 `BUILDAH_FORMAT=docker` 与 sed patch/trap 注册；脚本不真跑 build（以 `--help` 分支或函数级检查完成）。
  - `rule` TR-4.3: .dockerignore patch 函数幂等：对一份含 `**/foo  # c` 的临时样例执行 sed 函数后符合 buildah 兼容形态（无 `**`、无行内注释），restore 后原文复原。

## Task 5: workspace/smoke.ipynb 冒烟资产
- **Status**: `completed`
- **Priority**: `high`
- **Depends On**: Task 2
- **Completion Evidence**:
  - TR-5.1 ✅ ConvertFrom-Json：nbformat=4.5，cells[0]=code，metadata.kernelspec.name=xmnn-whl-builder。
  - TR-5.2 ✅ 源文件 outputs=0、execution_count 为空（执行仅写容器内 /tmp/smoke-out.ipynb，宿主源文件未回填结果）。
- **Description**:
  - 合法 nbformat 4.x 最小 notebook，1 code cell：import tvm/vta/xmnn 打印版本；用 tvm.relay/tir 最小 LLVM target `tvm.build` 完成 c=a+b（n=4，期望 [1,3,5,7] 或等价断言）并 numpy 断言输出。
  - 无输出单元预填（由执行生成）；metadata 声明 language/python，kernelspec name `xmnn-whl-builder`、display `Python 3.14 (xmnn whl-builder)`（对齐源 kernel.json）。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-8
- **Test Requirements**:
  - `rule` TR-5.1: JSON 可被 python `json.load`、nbformat 最小字段（cells/cells[0].cell_type=code/metadata.kernelspec.name=xmnn-whl-builder）齐全。
  - `rule` TR-5.2: notebook 源文件内不嵌入任何执行结果（由 nbconvert 首次执行产出）。

## Task 6: 静态配置验证
- **Status**: `completed`
- **Priority**: `high`
- **Depends On**: Task 2, Task 3, Task 4, Task 5
- **Completion Evidence**:
  - TR-6.1 ✅ 三条 config 全退出 0（默认 1 服务 1 bind；sources 3 bind targets 去重；build context 绝对路径+dockerfile）；CRLF=0。
  - TR-6.2 ✅ privileged/docker.sock/x-podman 三项 grep 零命中。
  - 历史残留 `notebook_test_1` 经 inspect 确认属项目 `notebook`（service=test，cuda 样本）后 `podman rm -f` 清除。
- **Description**:
  - machine 内依次执行 AC-1 三条 config 并落实证；同时验证 YAML 中无短语法 bind、无旧式顶层 `x-podman:` 字典（概念 08 硬校验项）。
  - 清理 machine 内历史残留 `notebook_test_1` Created 容器（属于既有 cuda 测试样本，记录后 `podman rm -f`，避免与本项目标签混淆；仅删该非本项目残留需先在证据中确认标签非本项目）。
- **Acceptance Criteria Addressed**: AC-1, AC-7
- **Test Requirements**:
  - `rule` TR-6.1: 三条 config 断言（AC-1 五断言）全部成立，输出摘要入证据。
  - `rule` TR-6.2: `grep -rnE 'privileged|/var/run/docker.sock' $STACK` 零命中；`grep -rn 'x-podman:' $STACK` 零命中（如需 x-podman 须为点号扁平字段且有概念 08 依据，本任务不需要）。

## Task 7: E2E 运行验证（up→服务→内核→nbconvert→sources→down）
- **Status**: `completed`
- **Priority**: `high`
- **Depends On**: Task 6
- **Completion Evidence**:
  - TR-7.1 ✅（AC-2 四项）容器 Up、`0.0.0.0:8888->8888`；curl /lab=200、/api=200、/api/contents=200；kernelspec 含 xmnn-whl-builder（/root/.local/share/jupyter/kernels/）；`/opt/conda/bin/python -c "import tvm,vta,xmnn"` 输出 `imports OK; xmnn= 1.2.1.dev0`；/workspace/notebooks/smoke.ipynb 可见（rwx 9p bind）。PID 1 = jupyter-lab，argv 与设计逐字一致。
  - TR-7.2 ✅（AC-3）nbconvert 以 xmnn-whl-builder kernel 执行退出 0，写入 /tmp/smoke-out.ipynb；输出 `[OK] tvm.build LLVM vector add passed: [2.0, 3.0, 4.0, 5.0]`；`grep -c ename`=0（无 error 单元）。
  - TR-7.3 ✅（AC-4）sources 栈 exec ls：/workspace/npu_tvm/version.py、/workspace/npuusertools/AGENTS.md、/workspace/notebooks/smoke.ipynb 均在。
  - TR-7.4 ✅ sources 栈 down 后：项目 label 容器查询为空、`network ls | grep xmnn` 为空（network_mode: bridge 不建项目网络）；宿主 workspace/smoke.ipynb 完好。
- **Description**:
  - `podman-compose up -d`；轮询日志等待 JupyterLab URL 出现（≤90s）；curl 127.0.0.1:8888/lab 状态码；exec kernelspec list、cp314 导入、/workspace/notebooks 可见性（AC-2）。
  - 容器内 nbconvert 以 xmnn-whl-builder kernel 执行 smoke.ipynb（AC-3），校验期望输出。
  - down 后以 sources 覆盖 up，验证两个源码挂载（AC-4），随后 down。
  - 默认栈最终 down，验证容器/网络零残留（AC-3 对应 NFR-3，并入 AC-6 检查）。
  - 全过程日志摘录入 Completion Evidence。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, NFR-3
- **Test Requirements**:
  - `rule` TR-7.1: AC-2 四项断言全过；JupyterLab 日志含 token/URL 行。
  - `rule` TR-7.2: nbconvert 退出码 0 且执行结果含向量加法期望值。
  - `rule` TR-7.3: sources 栈 ls 两个标志文件成功（AC-4）。
  - `rule` TR-7.4: down 后 `podman ps -a --filter label=io.podman.compose.project=xmnn-whl-builder -q` 与项目 network 均为空。

## Task 8: 零侵入核验与证据归档
- **Status**: `completed`
- **Priority**: `medium`
- **Depends On**: Task 7
- **Completion Evidence**:
  - TR-8.1 ✅ `git check-ignore -v`：$STACK/compose.yaml 命中 `apps/containers/client/.gitignore:35:.temp/`；`git status --porcelain -- apps/containers/client` 零输出（src/overlays 零改动）。external/chaos/ai 仓库仅有**先存**变更（.agents/skills/...benchmark.md、review.html 为会话前修改；xmnn-whl-builder/logs/ 为历史未跟踪构建日志），本任务工具调用未触该树；external/chaos/.dockerignore 时间戳 Aug 28 且无 `.podman-compose-bak-*` 残留（wrapper 未触发真实 build）。
  - TR-8.2 ✅ 最终文件集恰 6 个：.env.example / build-compose.sh / compose.build.yaml / compose.sources.yaml / compose.yaml / workspace/smoke.ipynb。
  - 说明：`.trae/specs/xmnn-notebook-compose/` 为主仓库未跟踪的 Spec 工件（标准 Spec 位置），用户未要求提交。
- **Description**:
  - Windows 侧主仓库 `git status --porcelain` 确认 .temp 不出现追踪变更；`external/chaos/ai` 独立 git 仓库 `git status` 确认零修改；client src/ 无改动。
  - 汇总任务证据，更新 tasks.md Completion Evidence；产出最终目录树。
- **Acceptance Criteria Addressed**: AC-6, AC-8
- **Test Requirements**:
  - `rule` TR-8.1: 三处 git 工作树检查无来自本任务的修改（.temp 在 client/.gitignore 内不可见即通过）。
  - `rule` TR-8.2: 最终文件集恰为 compose.yaml/compose.sources.yaml/compose.build.yaml/.env.example/build-compose.sh/workspace/smoke.ipynb（+目录），无多余文件。
