# xmnn scratch 栈按 onnx-quantized 范式重建 - Independent Review

- [x] CP-R1: 外部目录耦合清除（静态门禁）
  - **Type**: `rule`
  - **Covers**: AC-1, FR-5, FR-6, TR-4.1
  - **Evidence**:
    - 独立 LS/Glob 当前栈目录（11 个文件）：`compose.sources.yaml`、`compose.build.yaml`、`build-compose.sh` 均不存在；无 `.dockerignore`、无 `.podman-compose-bak-*`。
    - 用 Grep 对功能性文件集（compose*.yaml、Containerfile*、.env.example、scripts/*、smoke/*）重跑 `CHAOS_ROOT|external/chaos|NPU_TVM_HOST|NPUUSERTOOLS_HOST|\.dockerignore|docker-wrapper`：**0 命中**。
    - 文档（README/AGENTS/rules）中出现的 `external/chaos`、`BUILDAH_FORMAT`、`/workspace/notebooks`、`healthcheck: disable`、`--ServerApp.token=` 全部处于「旧栈/已废止/禁止回潮/事实只读参考」语境，无一条作为现行指令（Grep 逐条人工判读）。
  - **Result**: `pass`

- [x] CP-R2: compose 配置静态正确性
  - **Type**: `rule`
  - **Covers**: AC-2, FR-4, FR-5, TR-2.1, TR-2.2
  - **Evidence**: WSL `podman-machine-default` 内栈目录执行 `podman-compose config`，退出码 0，输出逐项核对：
    - 恰好 1 服务 `xmnn`；name=`xmnn-whl-builder`；image=`localhost/xmnn-notebook:latest`；
    - build.context 归一化为栈目录绝对路径 `/mnt/d/spaces/SpecWeave/apps/containers/client/.temp/notebook/xmnn-whl-builder`，dockerfile=`Containerfile.xmnn`，args 恰好 BASE_IMAGE/XMNN_DIST_IMAGE/PIP_MIRROR 三键；
    - 端口 `2222:22`、`8888:8888`；`network_mode: bridge`；
    - devices 1（/dev/fuse:/dev/fuse）、security_opt 1（label=disable）、cgroupns=host；
    - volumes 恰好 1 个长语法 bind：source=./workspace → target=/workspace，create_host_path=true；
    - environment 恰好四凭证键（USER_PASSWORD/JUPYTER_TOKEN/SSH_PUBLIC_KEY 空串、GRANT_SUDO=yes）；
    - labels 恰好 org.specweave.component/managed-by/base 三键；restart=unless-stopped；
    - 无 healthcheck 段、无 command 段；container_name=xmnn-notebook。
    - `.env.example` 生效键 10 个（XMNN_IMAGE_TAG/XMNN_CONTAINER_NAME/XMNN_SSH_PORT/XMNN_JUPYTER_PORT/XMNN_WORKSPACE/USER_PASSWORD/JUPYTER_TOKEN/SSH_PUBLIC_KEY/GRANT_SUDO/PIP_MIRROR）+ 注释态 BASE_IMAGE/XMNN_DIST_IMAGE，与 compose 插值键集合 diff 为空；CHAOS/NPU 键不存在。
  - **Result**: `pass`

- [x] CP-R3: 自包含镜像真实构建
  - **Type**: `rule`
  - **Covers**: AC-3, FR-1, FR-2, FR-3, TR-1.1, TR-1.2
  - **Evidence**:
    - `podman images`：`localhost/xmnn-notebook:latest`（3e3bdb5e5abf，2.32 GB，2026-09-14 09:34 构建）在机；两个基底镜像在机、构建未触发 pull（机内日志 `/tmp/xmnn-build.log`，18.5KB，独立读取非重建）。
    - 机内构建日志关键行独立复核：`[OK] xmnn-whl-builder kernel visible to both root and devuser`、`[OK] guards: cp314 GIL enabled + xmnn bootstrap + libtvm.so present`、`[OK] tvm.build LLVM vector add passed: [2.0, 3.0, 4.0, 5.0]`、`[OK] devuser xmnn runtime access verified`、`XMNN-NOTEBOOK OVERLAY BUILD COMPLETE`；Stage 1 SHELL/HEALTHCHECK OCI 忽略 warning 与文档描述一致（来自 wheel 源镜像）。
    - `podman image inspect localhost/xmnn-notebook:latest`：Entrypoint=`["/usr/bin/tini","--","/usr/local/bin/entrypoint.sh"]`、Cmd=`null`、Healthcheck=`null`、WorkingDir=`/workspace`（继承未覆盖）、ExposedPorts=22/8888；org.specweave.* 标签 7 个（component/managed-by/layer/python-version=3.14-cp314-gil/conda-env=base/base-image/wheel-source）。
    - 静态指令审计：Containerfile 仅含 ARG/FROM/LABEL/COPY/RUN；无 SHELL/HEALTHCHECK/ENTRYPOINT/CMD/WORKDIR/USER/ENV 指令（相关词仅出现在注释）；无内联嵌套引号 `python -c`；RUN 全部显式 `/bin/bash -lc`。
    - 脚本语法：`bash -n register-kernel.sh` 通过；两个 smoke 脚本 py_compile（doraise）通过。
    - 一次性容器独立复跑（无服务、--rm）：`smoke_tvm.py` 输出 tvm 0.19.0 / xmnn 1.2.1.dev0 / `[OK] ... [2.0, 3.0, 4.0, 5.0]`，退出 0；`_xmnn_guards.py` 输出 python 3.14.7 cpython-314、守卫 `[OK]`，退出 0。
    - 镜像内 kernel.json 独立读取：argv[0]=`/opt/conda/bin/python`、argv=`-m ipykernel_launcher -f {connection_file}`、display_name=`Python 3.14 (xmnn whl-builder)`、env.PATH 以 /opt/conda/bin 为首；root 与 `su devuser` 两身份 `jupyter kernelspec list` 均见 xmnn-whl-builder（位置 /opt/conda/envs/main/share/jupyter/kernels/）。
    - 最终镜像 `/tmp/xmnn` 已清理（计数 0）、`/opt/xmnn-dist` 不存在——只取 wheel、未继承 dist 镜像文件系统；base env `import tvm,vta,xmnn` 独立验证成功（0.19.0 / 1.2.1.dev0）；ipykernel 7.3.0（与 README 一致）。
  - **Result**: `pass`

- [x] CP-R4: 构建不触碰 external/chaos
  - **Type**: `rule`
  - **Covers**: AC-4, NFR-2, TR-5.3
  - **Evidence**:
    - 构建上下文静态可证 = 栈目录（config 绝对路径）；Containerfile 的 COPY 源仅 `--from=xmnn-dist`（镜像内 /opt/xmnn-dist）与栈内 `scripts/`、`smoke/`，结构上无任何宿主外部路径可读。
    - 抽查 chaos 关键文件 mtime：Dockerfile 2026-09-08、build.sh 2026-09-08、pyproject.toml 2026-09-08、docker-wrapper.sh 2026-08-26、_xmnn_bootstrap.py 2026-08-10，均早于 2026-09-14 09:34 构建时刻。
    - `find external/chaos -name .podman-compose-bak-*` 0 命中（WSL 与 Windows 双侧）；external/chaos 工作树 `git status --porcelain` clean。
  - **Result**: `pass`

- [x] CP-R5: Notebook 栈 E2E 可用
  - **Type**: `rule`
  - **Covers**: AC-5, FR-8
  - **Evidence**:
    - 独立核验（一次性容器 + 静态配置）：kernelspec 含 xmnn-whl-builder 且 argv[0]=/opt/conda/bin/python、devuser 可见（见 CP-R3）；base python `import tvm,vta,xmnn` 退出 0（tvm 0.19.0 / xmnn 1.2.1.dev0）；bind 配置 target=/workspace 且宿主 `workspace/smoke.ipynb` 存在；端口 22/8888 发布于 config 且镜像 ExposedPorts 22/8888；ENTRYPOINT 未被覆盖（tini→entrypoint.sh→supervisord）。
    - 实现方证据（本审查受「不得 up 常驻容器」授权约束未直接复现）：up 后 /lab=302、2222 返回 SSH banner。该两项行为完全由未改动的 rootless 基底提供（与正式 onnx 叠加层同基底同入口），且与上述独立证据无矛盾。
  - **Result**: `pass`（活服务 HTTP/SSH 二子项采信实现方证据，审查覆盖边界见 Review Notes）

- [x] CP-R6: notebook 内核冒烟
  - **Type**: `rule`
  - **Covers**: AC-6, FR-8, TR-3.2, TR-6.2
  - **Evidence**:
    - smoke.ipynb 原始字节 + JSON 解析：合法 nbformat 4.5，metadata.kernelspec.name=`xmnn-whl-builder`、display_name 一致，1 个 code 单元，含 `tvm.build` 与 `[2,3,4,5]` 断言。
    - **独立复现（非服务路径）**：一次性容器把宿主 smoke.ipynb 只读挂入 /workspace，`/opt/conda/envs/main/bin/jupyter nbconvert --to notebook --execute --ExecutePreprocessor.kernel_name=xmnn-whl-builder --output /tmp/o.ipynb /workspace/smoke.ipynb` 退出 0，输出 notebook 中 grep 到 `2.0, 3.0, 4.0, 5.0`（内核走真实 ipykernel 进程，与 AC-6 同一条内核路径）。
    - smoke_tvm.py 与 smoke.ipynb 断言语义逐行一致（[1,2,3,4]+[1,1,1,1]=[2,3,4,5]），tasks.md Task 1 的 +1/*2 统一要求满足。
  - **Result**: `pass`

- [x] CP-R7: 运行期 smoke 脚本复跑
  - **Type**: `rule`
  - **Covers**: AC-7, FR-3, TR-6.3
  - **Evidence**: 一次性容器 `--entrypoint /opt/conda/bin/python` 分别运行 `/opt/xmnn-smoke/smoke_tvm.py` 与 `/opt/xmnn-smoke/_xmnn_guards.py`（即 compose exec 等价命令，未挂工作区，验证 FR-3 不依赖 cwd/挂载）：均退出 0，输出含 tvm.build 成功行与守卫 `[OK]` 行。
  - **Result**: `pass`

- [x] CP-R8: 清理与幂等
  - **Type**: `rule`
  - **Covers**: AC-8, NFR-4, TR-6.4
  - **Evidence**:
    - 独立时点核验（在实现方两轮 up/down 及本审查 4 次一次性容器之后）：`podman ps -a --filter label=io.podman.compose.project=xmnn-whl-builder` 0 行；`podman network ls | grep xmnn` 0 行；`podman ps` 全机 0 运行容器。
    - 宿主 workspace 文件保留：smoke.ipynb 仍在（mtime 2026-09-13，审查过程未改动）；bridge 模式不建项目网络与零网络残留互证。
    - 第二轮重复 up→nbconvert→down 本身未由本审查复现（授权禁止 up 常驻）；幂等机制静态成立（无命名卷、无状态写入、image+bind 声明式），与实现方两轮证据及当前零残留状态一致。
  - **Result**: `pass`

- [x] CP-R9: 零侵入
  - **Type**: `rule`
  - **Covers**: AC-9, NFR-5, TR-7.2
  - **Evidence**:
    - 主仓库 Windows 侧 `git status --porcelain`：仅 `?? .trae/specs/xmnn-overlay-rebuild/`；
    - `git check-ignore -v` 实证 .temp 命中 `apps/containers/client/.gitignore:35:.temp/`；
    - `git status --porcelain -- external/chaos` 与 `-- apps/containers/client/overlays/onnx-quantized` 均空；
    - 未发现任何 commit（Open Question 2「默认不提交」被遵守）。
    - 备注：WSL 内对主仓库跑 git status 会遇 `vendor/netease-youdao/BCEmbedding` 子模块 gitdir 指针 fatal（路径内嵌 `D:/spaces/...` 的 WSL 翻译问题），属该子模块既有环境问题，Windows git 正常且与本次重构无关。
  - **Result**: `pass`

- [x] CP-U1: onnx 范式保真度
  - **Type**: `rubric`
  - **Covers**: AC-10, NFR-1, NFR-3, TR-1.3, TR-2.3
  - **Scale**: 1-5
  - **Anchors**: 1 = 仍依赖外部构建上下文或 wrapper/x-podman/特权；3 = 结构对齐但 ≥2 处偏离无注释依据；5 = 文件集与写法与 onnx 范式一一对应，每条偏差（仅 bridge 一条）有实证与知识包/规则注释
  - **Pass Threshold**: >= 4
  - **Evidence / 锚点理由**（逐项对照 onnx 样板与 quant-overlay.md）：
    - Containerfile：薄叠加单 FROM rootless 基底（多出的 dist 阶段是 spec G2 明确的 wheel 来源适配，非偏离）、mirror 三段判断逐行同构、`chmod -R a+rX`、root 守卫 + devuser `su -s /bin/bash` 复跑、完成横幅、不覆盖 ENTRYPOINT/CMD/WORKDIR、无 SHELL/HEALTHCHECK——与 Containerfile.quantized 一一对应；LABEL 比 onnx 更全且为 FR-1 明确要求。
    - compose：image+build 内联、长语法 bind+create_host_path、双端口、四凭证 env、三必需、org.specweave labels、restart、无 command/healthcheck 与 onnx 同构。**唯一环境偏差 `network_mode: bridge`** 在 compose.yaml 行内、compose-stack.md S1、README 三处均有 2026-09-14 未改动 onnx 栈同机复现 aardvark-dns user-bus 失败的实证注释，并引 OKF concepts/02 标准字段依据。
    - 三必需诚实性：cgroupns 在 podman-compose 1.6.0 空操作在 compose 注释与 S3 表格中明确声明，未宣称运行时生效；无 privileged、无 docker.sock、无 host 网络（全栈 grep 仅命中禁止性注释）。
    - 所引 OKF 概念文件 02/03/06/08/10 与 index 全部 Test-Path 存在。
    - 其余差异均为 spec 授权且非偏方：PIP_MIRROR 默认 aliyun（允许三段内取值，.env/README 同步）、managed-by=specweave-scratch（scratch 定位正确）、多两个 build args（FR-4 要求）。
  - **Score**: **5**
  - **Result**: `pass`

- [x] CP-U2: 产物原子性与文档一致性
  - **Type**: `rubric`
  - **Covers**: AC-11, G6, FR-7, TR-7.1, TR-7.3
  - **Scale**: 1-5
  - **Anchors**: 1 = 残留失效文件/文档矛盾/坏链；3 = 1-2 处冗余或过时描述；5 = 每文件职责单一、文档与实现逐条一致、链接全通
  - **Pass Threshold**: >= 4
  - **Evidence / 锚点理由**：
    - 文件集 11 个，职责单一无冗余无占位（.agents 明确不建空目录）；旧三文件已净删。
    - 文档-实现逐条抽查一致：镜像 2.32GB、tvm 0.19.0、xmnn 1.2.1.dev0、ipykernel 7.3.0、python 3.14.7 cp314 GIL、端口、env 四键、bind /workspace、内核名/路径/argv、nbconvert 命令、镜像标签全部与实际相符；旧文件/旧 /workspace/notebooks/旧免认证语义仅以「已废止/差异说明」存在，无现行性误导。
    - 相对链接：README（8 条）、AGENTS（11 条）、.agents/README（8 条，含父级回退链 3 条）、compose-stack.md（spec 深链）共 15+ 目标 Test-Path 全通（含旧 spec spec.md/review.md、OKF bundle、chaos 只读目录、client .gitignore/AGENTS、根 AGENTS）。
    - 扣分项无（仅 2 条 advisory nit，见 Findings，均不在本维度定义内或不影响逐条一致性）。
  - **Score**: **5**
  - **Result**: `pass`

## Findings

- **F-1**: `advisory`; severity **nit**; 位置 [tasks.md](file_path/d:/spaces/SpecWeave/.trae/specs/xmnn-overlay-rebuild/tasks.md)；7 个任务 Status 仍为 `pending`、无 Completion Evidence 段（spec-mode 工件卫生问题，不影响栈产物与本审查的独立 AC 核验）。建议（非阻塞）：收尾时把 7 任务标 completed 并补关键证据指针。
- **F-2**: `advisory`; severity **nit**; 位置 [README.md](file:///d:/spaces/SpecWeave/apps/containers/client/.temp/notebook/xmnn-whl-builder/README.md) §wheel 从哪来 第 2 步；文档述「以 `/opt/conda/bin/pip` 把 wheel 装入 base env」，实现（及 S5 规则）实际为 `/opt/conda/bin/python -m pip`。二者功能等价（同 shebang），spec FR-1 也沿用了 `/opt/conda/bin/pip` 措辞，仅为文档精度问题。建议改为 `/opt/conda/bin/python -m pip`。
- blocker: 0；major: 0；minor: 0；nit: 2（均 advisory，不阻塞）。

## Review Notes（证据链与覆盖边界）

- 实现方提交的 AC-1~AC-9 证据与本审查独立复核结果**无自相矛盾、无夸大**：镜像 ID/size、inspect 四字段、构建日志关键行、版本串、向量结果、git 状态全部当场复现一致；构建日志（09:34:58）与镜像年龄在审查时点相互吻合。
- 审查授权明确「不得 up 常驻容器、不得触发重建」，故 AC-5 的活服务 HTTP/SSH 探测与 AC-8 的第二轮 up/down 未由本审查直接重放；这两项的依赖面（未改动的基底 entrypoint/supervisord/sshd、声明式 bridge+bind、无命名卷）经静态与镜像级证据覆盖，且当前残留为零、workspace 文件保留。复跑路径建议（如需）：按 README 在 machine 内执行一轮 up→curl /lab→2222 探测→nbconvert→down。
- spec Open Questions 未被擅自更改：产出标签仍为默认 `localhost/xmnn-notebook:latest`（compose 默认与实际镜像一致）；规划文档未提交（git 无 commit）。

## Review History

### Review R1
- **Date**: 2026-09-14
- **Reviewer**: Spec Mode fresh-context 独立审查员（未参与实现）
- **Result**: `pass`
- **Checks Performed**:
  - 逐文件阅读 11 个栈产物 + onnx 样板 3 文件 + quant-overlay.md 规则 + spec/tasks/模板；
  - Grep 独立重跑 AC-1 门禁（功能性文件 0 命中）+ 特权/x-podman/SHELL/HEALTHCHECK/ENTRYPOINT/CMD/WORKDIR/python -c 附加门禁（仅注释命中）；
  - WSL `podman-compose config` 全断言核对；
  - `podman images` + `podman image inspect`（Entrypoint/Cmd/Healthcheck/Workdir/Labels/ExposedPorts）；
  - 一次性容器复跑 smoke_tvm.py、_xmnn_guards.py（均退出 0）；
  - 一次性容器读取 kernel.json + root/devuser 双身份 kernelspec list + base 三包导入 + ipykernel 版本；
  - 一次性容器只读挂载 smoke.ipynb 跑 nbconvert --ExecutePreprocessor.kernel_name=xmnn-whl-builder（退出 0，输出含 [2.0, 3.0, 4.0, 5.0]）；
  - 项目标签容器/网络计数、.podman-compose-bak 扫描、workspace 宿主文件保留核查；
  - 三处 git status + check-ignore；chaos 关键文件 mtime；
  - 15+ 文档相对链接 Test-Path；OKF 概念文件存在性；smoke.ipynb JSON/nbformat 解析；脚本 bash -n / py_compile；构建日志只读复核。
- **Checkpoint Results**: CP-R1 `pass`；CP-R2 `pass`；CP-R3 `pass`；CP-R4 `pass`；CP-R5 `pass`（活服务二子项采信实现方证据，边界见 Review Notes）；CP-R6 `pass`；CP-R7 `pass`；CP-R8 `pass`；CP-R9 `pass`；CP-U1 `pass` score **5**；CP-U2 `pass` score **5**。
- **Blocked By**: 无
