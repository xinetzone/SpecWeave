# xmnn-dev 开发与打包叠加层 - Independent Review

> Reviewer 契约：fresh context（不参与设计/实施）；只读审查 + 可在
> WSL2 `podman-machine-default` 内独立复核运行证据（镜像
> `localhost/xmnn-dev:latest` c5fc1967d7b4 与 wheel 产物仍在；栈已 down，
> 可按 spec 自行 up）。对照：
> [spec.md](spec.md) 14 AC、[tasks.md](tasks.md) 13 任务完成证据、
> AI 规则 `apps/containers/client/.agents/rules/xmnn-overlay.md`、
> 范式真源 `overlays/onnx-quantized/` 与 `tasks/quant.py`。
> 重点行使 V（对抗审查）：实施期三处细化是否成立、wheel 与已交付 Docker
> 谱系产物是否真等价、"对 ai 零依赖/源码零修改"声明是否可被反证推翻。

> **R1 复核说明（2026-09-14，fresh-context 独立审查员）**
>
> - 复核方式：通读 spec/tasks/全部交付文件（约 30 个）；在 WSL2
>   `podman-machine-default`（podman 5.7.1 / podman-compose 1.6.0）执行
>   **只读**命令（images/inspect/run --rm 守卫与 ABI 断言/config 渲染/
>   zipfile 清单），未 up/down/build、未写容器；Windows 侧实跑
>   `invoke --list`/`invoke xmnn.ps`/包导入；外部仓做文件级 md5/find。
> - 栈复核约束：委托方要求不重新 up。AC-5/6/10 以 tasks.md 运行日志为
>   主证据，reviewer 用镜像/配置/产物静态事实与 wheel verify 日志做独立
>   交叉佐证，已在各 CP 标注证据等级。

- [x] CP-R1: 对 ai 零依赖与 builder 资产齐全（AC-1）
  - **Type**: `rule`
  - **Covers**: AC-1
  - **Result**: **pass**
  - **Evidence**:
    - 对 overlay 全目录执行禁项 grep
      `external/chaos/ai|chaos/ai|--mount=type=bind|CHAOS_ROOT|xmnn-whl-builder|/builder/`
      → 仅 2 处命中，全部在 README.md（L27「不依赖 external/chaos/ai」事实
      表述、L156 关系表），属 AC-1 明示豁免；功能性文件 0 命中。
    - xmnn.py 同 grep 仅 1 处命中（docstring 内"禁止 import podman"自指
      注释）；`import podman|from podman` 实际代码 0 命中。
    - 追加 grep `/opt/xmnn-dist|/app|docker|privileged`（README 除外）
      → 无移植源旧路径/旧指引残留；唯一 privileged 命中为 compose.yaml
      L16 注释"严禁 privileged"。
    - builder 9 资产齐全（镜像内实测，另含宿主目录核对）：
      pyproject.toml、CMakeLists.txt、_xmnn_bootstrap.py、xmnn_bootstrap.pth、
      scripts/{build-wheel.sh,build-tvm.sh,verify-wheel.sh,
      install-build-deps.py,lib/logging.sh}。守卫清单列 8 项（
      install-build-deps.py 为镜像层自用，不入守卫，合理）。

- [x] CP-R2: compose 配置静态正确（AC-2）
  - **Type**: `rule`
  - **Covers**: AC-2
  - **Result**: **pass**
  - **Evidence**: WSL 内
    `podman-compose -f <abs>/compose.yaml config` → **exit 0**。渲染输出
    独立计数：服务恰好 1 个 `xmnn`；image+build 共存
    （dockerfile=Containerfile.xmnn-dev，context 为 overlay 绝对路径，
    三 build-arg 齐）；network_mode=bridge；端口 `2223:22` 与 `8890:8888`；
    bind 恰好 4 个（target /workspace、/workspace/npu_tvm、
    /workspace/npuusertools、/workspace/models，全部长语法
    create_host_path: true）+ named volume `xmnn-ccache:/root/.ccache`
    且顶层 `volumes: xmnn-ccache: {}`；devices=/dev/fuse:/dev/fuse；
    security_opt=label=disable；cgroupns=host；environment 11 键
    （四凭证 + PYTHONPATH/TVM_LIBRARY_PATH/LD_LIBRARY_PATH/NPU_TOOLS_ROOT/
    XMNN_TOOLS_ROOT/OMP_NUM_THREADS/NUITKA_JOBS）；labels 2 个
    org.specweave.*；restart=unless-stopped；privileged/healthcheck/command
    计数均为 0。

- [x] CP-R3: 镜像真实构建、双 ABI 与工具链/SONAME 事实（AC-3、AC-4）
  - **Type**: `rule`
  - **Covers**: AC-3, AC-4
  - **Result**: **pass**
  - **Evidence**（reviewer 独立运行，非转述）:
    - `podman images`：`localhost/xmnn-dev:latest c5fc1967d7b4 4.43 GB`
      在机（与 tasks 镜像 ID 一致）；基底 localhost/jupyter-podman-rootless
      同在。
    - `podman inspect`：Entrypoint=`[/usr/bin/tini --
      /usr/local/bin/entrypoint.sh]`、Cmd=`[]`、Workdir=`/workspace`、
      User 空；Config JSON 用 python 解析确认 **无 Healthcheck 键**；
      org.specweave.* 六标签齐（component/layer/python-abis/llvm=22.1.8/
      nuitka=4.1.3/base-image）。
    - `podman run --rm` 独立复跑 `_toolchain_guards.py`：**全 PASS**——
      base 3.14.7 cpython-314（Py_GIL_DISABLED=0、_is_gil_enabled=True）、
      main 3.14.7 **cpython-314t**（子进程 -S 断言 GIL disabled）、
      llvm-config 22.1.8、clang 22.1.8、cmake 4.4.3、ninja 1.13.2、
      ccache 4.14、patchelf 0.18.0（/usr/bin）、gdb 17.1（/usr/bin）、
      nuitka 4.1.3；7 glob 实测 SONAME：libLLVM.so.22.1、libz.so.1
      （+.1.3.2）、libzstd.so.1（+1.5.7）、libxml2.so.16（+16.1.4）、
      libiconv.so.2（+2.7.0）、libicuuc.so.78（+78.3）、libicudata.so.78
      （+78.3）。
    - 双 ABI 断言另以两个 python 各跑一次 sysconfig 断言：BASE_OK /
      MAIN_OK 均通过；main 未被 conda 求解互换。
    - 两 smoke 脚本 `py_compile` 通过。
    - 构建期 root+devuser 双跑与横幅：来自 tasks T10 构建日志（reviewer
      未 rebuild；devuser 可见性另由 register-kernel.sh 双 grep 断言与
      Containerfile L118 su 复跑静态佐证）。
    - 附注（非缺陷）：裸环境 `nuitka --version` 会打印一行
      `FATAL: failed to detect GCC version ... gcc` 噪声，但实测退出码 0；
      打包路径 CC 绝对指向 main/bin/clang，全流程已成功，不受影响。

- [x] CP-R4: 栈 E2E（端口/挂载/内核双可见）（AC-5）
  - **Type**: `rule`
  - **Covers**: AC-5
  - **Result**: **pass（运行证据来自 tasks T11；reviewer 未重新 up，
    做静态+镜像交叉佐证）**
  - **Evidence**: tasks T11 记录 2223 可达、curl /lab=302、三挂载点可见、
    kernelspec root+devuser 双可见。Reviewer 独立佐证：镜像内
    `/opt/conda/envs/main/share/jupyter/kernels/xmnn-dev/kernel.json`
    实测 argv[0]=/opt/conda/bin/python、display_name 正确、env 携带
    PYTHONPATH 三源码段/TVM_LIBRARY_PATH/LD_LIBRARY_PATH（build+build/vta+
    main/lib）；compose config 端口/bind 渲染正确（CP-R2）。

- [x] CP-R5: 源码调试链路（import 来自挂载树 + tvm.build）（AC-6）
  - **Type**: `rule`
  - **Covers**: AC-6
  - **Result**: **pass（运行证据来自 tasks T11；强交叉佐证）**
  - **Evidence**: tasks T11 记录 root/devuser 双身份 smoke_mounts PASS、
    tvm/vta/xmnn `__file__` 全部位于 /workspace 挂载树、向量加
    [2,4,6,8]。独立佐证：①smoke_mounts.py 静态断言完备——先独立断言 6
    个挂载/包路径（任一失败即 exit 1，libtvm 缺席分支也先检查 failures），
    存在时再断言三模块前缀与 tvm.build('llvm') n=4 向量加；
    ②/tmp/xmnn-verify2.log test 6 在无源码 venv 内 tvm.build('llvm')
    数值断言通过，且 wheel 内 libtvm.so=81,650,176B 与挂载树
    external/chaos/npu_tvm/build/libtvm.so（Aug 11，81,650,176B）逐字节
    同尺寸，证明 libtvm+main LLVM 22.1.8 运行时 ABI 兼容（消解 spec 最大
    Assumption）。

- [x] CP-R6: Nuitka wheel 真实闭环与内容等价性（AC-7）
  - **Type**: `rule`
  - **Covers**: AC-7
  - **Result**: **pass（产物 reviewer 独立解包核验）；附 1 条 advisory
    证据表述偏差（F-2）**
  - **Evidence**: host python3 zipfile 只读核对
    `client/workspace/dist/xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`
    （193,456,300B，158 项）：顶层 3 个 .so
    （tvm/vta/xmnn.cpython-314-x86_64-linux-gnu.so）；`_libs/` 14 项
    （libtvm.so + libLLVM.so.22.1 + 6 依赖各 SONAME 名与全名版本）；
    _xmnn_bootstrap.py / xmnn_bootstrap.pth 在；xmnn/autolibs 17 项、
    tools_cpp 89 项、fonts 1 项；vta_hw/config 25 项；tvm/relay/std
    4 个 .rly 含 prelude.rly；METADATA Requires-Python>=3.14.6、
    dist-info 三件齐。构建闭环退出 0 见 tasks T12（build-wheel.sh
    三次 Nuitka 参数静态核对齐全：dill-compat、--module、交叉 nofollow、
    vta include-data-dir、jobs、.vta_exit/.xmnn_exit 回传、六
    cmake.define、libtvm 前置 exit 2、DIST_DIR 默认 /workspace/dist）。
  - **偏差记录（F-2，advisory）**：wheel 内 14 个 _libs 条目经 zip
    external_attr 与 verify 日志（无 [symlink] 标记）确认**全部为常规
    文件、0 个 zip 软链**（6 对 SONAME/全名文件逐对同尺寸），与 tasks
    T12「libLLVM.so.22.1 软链 + 6 依赖 SONAME 软链」表述不符——CMake
    install(CODE) 阶段确在 staging 建了软链，但 wheel 打包链解引用为
    常规文件。加载器语义完全满足（SONAME 名存在），代价是约 40MB
    未压缩重复（压缩后 wheel 与旧谱系 187.9MB 同量级，193.5MB）。

- [x] CP-R7: wheel 隔离验证 10 项与 base 零污染（AC-8）
  - **Type**: `rule`
  - **Covers**: AC-8
  - **Result**: **pass（10/10 有日志原件；脚本隔离逻辑审查通过）；
    附 2 条 advisory（F-3、F-4）**
  - **Evidence**: WSL `/tmp/xmnn-verify2.log`（3,098B，2026-09-14）仍在，
    实测内容：venv 路径 /tmp/xmnn-verify-venv、`--no-deps
    --force-reinstall` 安装、Tests 1-9 全 PASS、SUMMARY `10 passed,
    0 failed`（含 test 4b「13 libs with $ORIGIN, 0 without」、test 5
    unset LD_LIBRARY_PATH ctypes 加载 libtvm、test 6 tvm.build 数值断言、
    prelude.rly、.pth、数据三目录）。脚本逻辑审查：venv 用
    `--system-site-packages` 且 wheel --no-deps，等价"有 19 依赖、无
    tvm/xmnn 源码"的客户机；脚本开头与 venv 安装后**两次** unset
    LD_LIBRARY_PATH/PYTHONPATH/TVM_LIBRARY_PATH（修补 compose 注入遮蔽，
    实施期细化③成立）；`trap cleanup_venv EXIT` 覆盖注册后所有退出路径；
    base 零污染见 tasks T12④（pip list 无 xmnn/tvm/vta，import tvm 仍
    指向源码树）。
  - 弱点（不改变本次 PASS 裁决，理由见 F-3/F-4）：tests 4-9 的
    `cmd; if [ $? -eq 0 ]` 写法在 `set -e` 下失败会提前中止（退出码仍
    非零，故不会假绿，但 FAIL 计数/SUMMARY 失效）；test 4b 只统计告警
    不做断言（实际回归由 test 5 干净环境 ctypes 加载兜底）。

- [ ] CP-R8: 外部源码零修改与 AST 还原（AC-9）
  - **Type**: `rule`
  - **Covers**: AC-9
  - **Result**: **fail → 见 F-1（actionable，severity medium）**
  - **Evidence（现状干净，reviewer 独立复核）**:
    - 三 `__init__.py` md5 与 tasks T12 基线前缀逐字一致：
      tvm `c3da634afaba00e2132cc5f28b6fee2f`、
      vta `e8210b694e388c769630892402dd18a5`、
      xmnn `6c958e99f132242be30168d15ba6f154`；三文件均无
      `XMNN BOOTSTRAP` 标记；两仓 `find -name '*.bak_*'` 为空；
      git status 计数 npu_tvm=14820、npuusertools=99，与基线一致
      （vta `__init__.py` 的 M 属既存 14820 之列，打包前后 md5 不变即
      证明 build-wheel 未改写）。
    - trap 静态审查：tvm 段父 shell EXIT trap（注入前注册、编译后
      显式还原并 `trap - EXIT`）、vta/xmnn 两个并行子 shell 各自
      `trap ... EXIT ERR`（注册先于注入）——正常路径与 SIGINT/普通错误
      路径还原成立。
  - **对抗缺口（F-1）**：①OOM/SIGKILL 杀的是**子 shell 运行的 Nuitka
    进程组**时，子 shell 自身的 EXIT/ERR trap 对 SIGKILL 不触发，而父
    shell 的 tvm EXIT trap 已在 L233 清除、**没有覆盖 vta/xmnn 的统一
    还原兜底**；jobs=8 ~15GB 峰值恰是 README 自己标注的 OOM 场景。
    ②`inject_ast_preamble()` 无条件先 `cp init backup`（L179）再检查
    标记——一旦上次 SIGKILL/写入中断留下「init 已注入 + .bak 原件」，
    重跑会用**含注入的 init 覆盖掉唯一干净备份**，随后 marker 已存在
    跳过写入，restore 回来的仍是注入版，静默持续污染（只能靠外部仓
    `git checkout` 恢复）。spec Background 增强点②明示「异常 kill 不留
    `.bak_*`」，当前实现未达该承诺（README 排障表虽提示手工 mv，
    但未防上述重跑覆盖）。

- [x] CP-R9: 清理幂等与 ccache 卷语义（AC-10）
  - **Type**: `rule`
  - **Covers**: AC-10
  - **Result**: **pass（终态 reviewer 实测；两轮幂等以 tasks T13 为准）**
  - **Evidence**: 当前机上
    `podman ps -a --filter label=io.podman.compose.project=xmnn-dev`
    无容器、`podman volume ls | grep xmnn` 无卷、`podman network ls |
    grep xmnn` 无网络——与 tasks T13「最后一轮 down --volumes」终态
    一致；wheel 仍在 bind 的 workspace/dist（宿主文件保留实测）。
    plain down 保留卷 / --volumes 删卷的两轮记录见 tasks T13①②
    （reviewer 受不重新 up 约束未重放；命名卷语义为 podman-compose
    标准行为，compose 顶层 volumes 声现已实测）。

- [x] CP-R10: invoke xmnn.* 集成、门禁与键集合（AC-11）
  - **Type**: `rule`
  - **Covers**: AC-11
  - **Result**: **pass（Windows 侧 reviewer 实跑）；附 2 条 advisory
    （F-5、F-6）**
  - **Evidence**: Windows 原生 `PYTHONPATH=src python -m invoke --list`
    exit 0 且含 xmnn.build/up/down/ps/logs/smoke/build-tvm/wheel 8 任务；
    `python -m invoke xmnn.ps` → **Exit 1** + 双路径中文指引（WSL/
    env.run-cmd）；xmnn.py 无 `import podman`；三源码路径
    `_resolve_path(must_exist=True)` 缺失即 Exit 1，workspace 自动 mkdir；
    wheel 的 `-e NUITKA_JOBS=<int>/CLEAN_REBUILD/TVM_COMPILE_FLAGS` 经
    `shlex.quote` 逐元素拼接后交 podman-compose，本地 shell 无注入面，
    容器内 env 值不经 shell 求值（build-wheel.sh 仅按空白分词为 flag，
    无 eval，无命令注入）；build 含基底镜像存在性预检。
    键集合：compose 插值 17 键（含 BASE_IMAGE）= overlay .env.example
    16 生效键 + 注释态 BASE_IMAGE = client 根 .env.example xmnn 段 17
    注释键，三方一致。

- [x] CP-R11: 零侵入与 quant 零回归（AC-12）
  - **Type**: `rule`
  - **Covers**: AC-12
  - **Result**: **pass**
  - **Evidence**: 主仓 `git status --porcelain` 改动恰为 NFR-6 白名单：
    6 改（apps/AGENTS.md、client AGENTS.md、client .agents/README.md、
    client .env.example、client README.md、tasks/__init__.py）+
    4 新（xmnn-overlay.md、overlays/xmnn-dev/、xmnn.py、
    .trae/specs/xmnn-dev-overlay/）；onnx-quantized/ 与 quant.py 0 改动；
    `__init__.py` diff 纯追加（import/Collection/config/docstring 仅
    xmnn 段）；quant 零回归实测：`invoke quant.ps` 同样 Exit 1 且输出其
    原有双路径指引（无导入错误）；`python -c "import
    jpman_client.tasks"` exit 0。另：工作树另有
    `.trae/specs/podman-py-wiki-r3/`、`.trae/specs/xmnn-overlay-rebuild/`
    两个未跟踪 spec 目录，均非本期产出（后者为 spec 引用的既有前序
    规格），不计入白名单违规。

- [x] CP-U1: 范式保真度（AC-13）
  - **Type**: `rubric`
  - **Covers**: AC-13
  - **Scale**: 1-5
  - **Score**: **4**
  - **Anchors**: 1 = wrapper/特权/短语法/回流根 run/双 ABI 无依据；3 = ≥2 处无注释偏离；5 = 仅 bridge/端口两偏差且有实证注释，双 ABI 跨 env 设计有 chaos 实证出处
  - **Evidence**: 与 quant 范式逐项同构（Collection 注册/双门禁/daemon
    预检/load_dotenv override=False/标签探测/固定 project+绝对 -f/长语法
    bind/三必需/裸 RUN chmod 亦与 Containerfile.quantized L85 同族）；
    shlex 处理比 quant 更严；xmnn.py 不回流根 run、不 import podman；
    仅 network_mode=bridge（带 2026-09-14 aardvark-dns 实证注释，onnx
    同机复现）与 2223/8890 端口两处偏差，均有注释；双 ABI/pin cp314t/
    LLVM 22.1.8 有 chaos 移植源与机内守卫双重出处。扣 1 分原因：交付
    镜像烤入宿主 cp313 pyc（F-7）、build 对 .env 构建参数不敏感未在
    xmnn.py 留 quant 那样的说明注释（F-5）。

- [x] CP-U2: 产物原子性与文档一致性（AC-14）
  - **Type**: `rubric`
  - **Covers**: AC-14
  - **Scale**: 1-5
  - **Score**: **4**
  - **Anchors**: 1 = 文档与实现矛盾/坏链/参数不一致；3 = 1-2 处过时；5 = .env/compose/任务参数三处逐字一致、链接全通
  - **Evidence**: check-links.py 对 overlay 目录、rules 目录、client
    AGENTS.md/README.md、apps/AGENTS.md 全部通过（无 file:///）；README
    八任务名/参数（--jobs/--clean/--tvm-flags/--pip-mirror/--conda-mirror/
    --skip-build/--volumes/--no-cache）、端口、路径与 xmnn.py/compose.yaml
    逐字一致；参数表 17 键齐。扣 1 分：①tasks T12 把 wheel _libs 常规
    文件称作"软链"（F-2）；②两处文档把 xmnn .env 键数写作"16 项"
    （client AGENTS.md L74、.agents/README.md L60），与三方 17 键口径
    （含注释态 BASE_IMAGE）不统一（F-6）；③镜像内 pyc 卫生（F-7）。

## Review History

### Review R2
- **Scope**: 复审 I-1~I-7 是否真实闭环（重点 I-1 自愈四场景实测、I-2 _libs 8 项与 cp 硬失败、I-3 pyc=0、I-4 check 式不中止）+ 修复回归抽查（AC-1 脱钩 grep、AC-7 wheel 内容、AC-8 零污染、AC-9 hash、AC-11 8 任务/键集合、AC-12 白名单）。
- **Result**: **pass**
- **Date**: 2026-09-14
- **Reviewer**: fresh-context 独立审查员（全程只读；证据全部来自 podman run --rm 一次性验证，未 build/up/down/push、未改任何文件）
- **逐项裁决**：I-1 闭环（TR-I-1.4 评 4/5；A/B/C/D 27/27 + 子 shell 不执行 EXIT trap 的竞态排除 + kill -9 子进程 rc=137 后父 EXIT trap 还原实证）；I-2 闭环（wheel _libs 恰 8 项 NEEDED 短名、cmake -P 故障注入实证 cp RESULT_VARIABLE→FATAL、REMOVE_DUPLICATES 全复数、独立 verify 10/10）；I-3 闭环（.dockerignore、镜像 pyc=0）；I-4 闭环（check 式强制失败探针证明不中止、4b 硬 assert）；I-5/6/7 闭环（help 口径、17 键三方一致、-f shlex）；全量回归抽查 PASS（AC-1/2/3/7/8/9/11/12 + 镜像无构建中间产物 + 镜像-宿主文件 md5 一致）。
- **Findings（无 actionable）**：F-R2-1（advisory low，AST 注入器毫秒截断窗口：marker 缺席+bak 在会被无条件 cp 覆盖）、F-R2-2（advisory trivial，规则/README 三处修复前措辞）。实施方已在 R2 后顺手闭环：F-R2-1 由 ast_inject 四态自愈矩阵吸收（marker 缺席+bak 在→用干净 bak 自愈，场景 E 实测 PASS）；F-R2-2 四处文档同步。收尾构建另实证一条构建卫生教训并修复：.dockerignore 裸 `__pycache__/` 不匹配嵌套目录，改 `**/__pycache__/` 并在 Layer 5 末尾兜底清理。
- **最终交付物**: 镜像 `localhost/xmnn-dev:latest` = **4b31eebdc525**（4.43GB；root/devuser 双跑守卫 PASS；pyc/bak 计数 0）；wheel `xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl` 177,764,212B（_libs 8 项；verify 10/10）。
- **一句话结论**：R1 唯一 actionable 的 OOM/SIGKILL 污染与重跑毁备份路径已被实测证明闭环，I-2~I-7 全部独立复核成立，无回归、无遗留 actionable，rubric 维持 ≥4，R2 = pass，Spec Mode 结束条件满足。

### Review R1
- **Result**: **fail**
- **Date**: 2026-09-14
- **Reviewer**: fresh-context 独立审查员（只读；WSL2 只读命令 + Windows
  实跑门禁；未 up/down/build、未修改任何文件）
- **一句话结论**：13 个 CP 中 12 个 pass（含两个 rubric 各 4 分，达
  >=4 阈值），AC-1..8、AC-10..14 的事实主张全部经得起独立复核；
  **CP-R8（AC-9）因 AST 注入/还原在 SIGKILL/OOM 路径存在真实缺口且
  重跑会摧毁干净备份而 fail**，按裁决规则（任一 actionable → fail）
  R1 = fail。该缺口为脚本逻辑层修复，不影响已交付 wheel 的正确性与
  现有产物/镜像的可用性。

### Findings（按严重度排序）

#### F-1（actionable，severity medium）AST 注入在 SIGKILL/OOM 路径
#### 无父级还原兜底，且重跑会用污染版覆盖干净 .bak（违反 AC-9 硬承诺
#### 与 spec 增强点②）
- **位置**：
  [build-wheel.sh](../../../apps/containers/client/overlays/xmnn-dev/builder/scripts/build-wheel.sh)
  L175-202（inject/restore）、L211/L233（父 trap 注册与清除）、
  L249-296（两个并行子 shell）。
- **复现（静态可证，无需真 OOM）**：
  1. vta 或 xmnn 并行 Nuitka 期间容器 OOM（README 标注 jobs=8 约 15GB
     峰值，OOM 是被显式文档化的失败模式），子 shell 被 SIGKILL：
     子 shell 的 `trap _vta_restore EXIT ERR` 不触发；父 shell 的
     tvm EXIT trap 已在 L233 `trap - EXIT` 清除，父进程随后仅按缺失的
     `.vta_exit/.xmnn_exit` 判失败退出，**不会还原 vta/xmnn 的
     __init__.py 与 .bak_*，也不删 .bak**。
  2. 用户直接重跑 build-wheel.sh：`inject_ast_preamble()` L179
     `cp "$init_file" "$backup"` **无条件执行**——此时 init 已含注入
     标记，干净 .bak 被含注入的副本覆盖；随后 marker 检查跳过写入；
     编译结束 `mv backup init` 还原回来的仍是注入版。外部工作树被
     静默持续污染，AC-9"工作树零修改"承诺被反证推翻（只能 git
     checkout 恢复）。写入窗口内被 kill（init 被截断）同理。
- **期望**：
  1. 父 shell 持有**三个文件的统一还原兜底**：注入开始即注册一个覆盖
     tvm/vta/xmnn 的 EXIT trap（用关联数组/固定变量记录 backup 路径），
     脚本最末成功路径才解除——子 shell 被 SIGKILL 而父进程存活走失败
     退出时，由父 trap 完成全部还原与 .bak 清理；
  2. `inject_ast_preamble()` 增加前置条件：发现 init 已含
     `XMNN BOOTSTRAP` 标记或同名 .bak 已存在时，不得覆盖 backup——
     应先尝试用现存干净 .bak 还原并报错退出（或要求显式确认），并
     校验 backup 自身不含 marker；写入 init 用临时文件+原子 rename，
     避免 kill 在截断窗口；
  3. 在 xmnn-overlay.md §5 与 README 排障表把"手工 mv"升级为脚本
     自愈语义说明。
- **建议的 Issue 要点**（不在本次审查中改代码）：
  - 标题：xmnn-dev build-wheel.sh AST PREAMBLE 还原在 OOM/SIGKILL
    路径失效且重跑覆盖干净备份（AC-9）
  - 复现：并行 Nuitka 子进程被 SIGKILL（OOM）→ init 留注入+.bak；
    重跑 → 干净备份被污染版覆盖
  - 验收：①模拟 kill -9 编译子进程后，三 __init__.py 自动还原、
    0 .bak；②预置"init 已注入+.bak"状态重跑，脚本报错并自愈，
    git status 与基线一致；③正常路径/SIGINT 路径行为不回归；
    ④规则与 README 同步更新。

#### F-2（advisory，severity low-medium）wheel _libs 实际为常规文件
#### 副本而非软链，tasks 证据与"软链兜底"表述失真
- **位置**：[CMakeLists.txt](../../../apps/containers/client/overlays/xmnn-dev/builder/CMakeLists.txt)
  L95-109（install(CODE) ln -sf）；tasks.md T12②；spec FR-2/G6。
- **复现**：`python3 -c zipfile` 读 wheel：14 个 _libs 条目的
  external_attr 无 S_IFLNK，6 对 SONAME/全名文件逐对同尺寸；
  verify 日志 test 4 无 `[symlink]` 标记。CMake staging 软链被 wheel
  打包链解引用。
- **影响**：加载器语义正确（10/10 PASS、ctypes 干净环境加载成功），
  仅约 40MB 未压缩/数 MB 压缩级冗余；若未来 conda 同时提供
  libLLVM.so.22.1 与 .22.1.8，glob 双命中会再多一份 ~197MB 副本。
- **期望**：二选一并回写证据——①接受常规文件事实，把 tasks/规则中
  "软链"改为"SONAME 同名文件兜底"，并在 CMake 注释说明 wheel 解引用；
  或②让打包链保留软链（scikit-build/wheel 软链支持）后重新核验
  zip 条目类型。

#### F-3（advisory，severity low）verify-wheel.sh 在 set -e 下 tests
#### 4-9 失败即中止，FAIL 计数与 SUMMARY 失效
- **位置**：[verify-wheel.sh](../../../apps/containers/client/overlays/xmnn-dev/builder/scripts/verify-wheel.sh)
  L109-125 等七处 `"$VENV_PY" -c ...; if [ $? -eq 0 ]`。
- **复现**：任一检查 python 退出非零 → `set -e`（L24）在 if 之前
  直接终止脚本；PASS/FAIL 汇总不打印。
- **影响**：退出码仍非零（trap 也会清 venv），**不会产生假绿**，
  仅排障信息退化；tests 1-3 的 check() 函数无此问题。
- **期望**：七处改为 `if output=$("$VENV_PY" -c "..." 2>&1); then`
  形式（或该段 `set +e`），保证 10 项计数完整。

#### F-4（advisory，severity low）verify test 4b 只告警不判定
- **位置**：verify-wheel.sh L157-169（rpath_warn 计数后无 assert）。
- **复现**：脚本静态可见 rpath_warn>0 不导致失败。
- **影响**：RPATH 回归的实际兜底是 test 5（unset LD_LIBRARY_PATH 的
  ctypes 加载）与 CMake patchelf 段；4b 形同信息项，与 FR-5
  "RPATH $ORIGIN 检查"措辞不符。
- **期望**：末尾 `assert rpath_warn == 0`（libtvm 已单独强校验），
  或把 4b 明确标注为信息项不计入 10 项。

#### F-5（advisory，severity low）inv xmnn.build/up 不读 .env 中的
#### PIP_MIRROR/CONDA_MIRROR/BASE_IMAGE，与 .env 模板措辞略有出入
- **位置**：[xmnn.py](../../../apps/containers/client/src/jpman_client/tasks/xmnn.py)
  L189-229（build 仅取 CLI 参数）；overlay .env.example L49、
  client .env.example L193-197。
- **复现**：在 client .env 置 PIP_MIRROR=tuna 后 `inv xmnn.build`
  仍以 official 构建（裸 `podman-compose build` 才读插值）。
- **影响**：行为与 quant 同族（quant.py L227-229 有显式注释说明，
  xmnn.py 未留同款注释）；README 主路径给了 --pip-mirror/
  --conda-mirror flag，不构成功能阻断。
- **期望**：在 xmnn.py build 处补同款注释（"up 内联构建不透传 .env
  镜像源，需走两步"），或让 build 回退读 os.environ 的同名变量；
  .env 模板注明"仅裸 compose build 生效"。

#### F-6（advisory，severity trivial）xmnn .env 键数文档口径 16/17 不一
- **位置**：client AGENTS.md L74、client/.agents/README.md L60
  （"xmnn 栈 16 项"）vs tasks T7"17 键（含注释态 BASE_IMAGE）"、
  compose 插值实为 17 键。
- **期望**：统一表述为"16 业务键 + 1 注释态构建参数 BASE_IMAGE"。

#### F-7（advisory，severity low）交付镜像烤入 4 个宿主侧 cpython-313
#### 字节码（且 COPY 资产权限为 777）
- **位置**：镜像内 /opt/xmnn-builder/__pycache__/、
  /opt/xmnn-builder/scripts/__pycache__/、/opt/xmnn-dev-smoke/
  __pycache__/（各含 cp313 pyc，共 4 个）；宿主源
  overlays/xmnn-dev/**/__pycache__（被 client/.gitignore L8 忽略，
  故不入库，但被 `COPY builder/`、`COPY smoke/` 带入镜像）。
- **复现**：`podman run --rm --entrypoint find <img> /opt/xmnn-builder
  /opt/xmnn-dev-smoke -name '*.pyc'` → 4 个 cpython-313 pyc，
  权限 777；宿主 Get-ChildItem 可见同源 4 文件。
- **影响**：cp314 解释器 magic 不匹配不会加载，功能零影响；属构建
  上下文卫生问题（错误 Python 版本字节码进入交付镜像），全部 COPY
  文件 777 亦偏宽（与 9p 上下文默认模式有关，quant 同族）。
- **期望**：overlay 增加 `.dockerignore`（`__pycache__/`、`*.pyc`、
  `.env`）或在 COPY 后清 xmnn 目录 pyc；重建镜像复核 0 pyc。

#### F-8（advisory，severity trivial）xmnn.py build 的 `-f <containerfile>`
#### 未走 shlex（同族遗留）
- **位置**：xmnn.py L220（quant.py L209 同款）。
- **影响**：Windows 已门禁；POSIX 下仅当仓库路径含空格时分词出错，
  默认路径不受影响；其余 build-arg 均已 quote。
- **期望**：改为 `f"-f {shlex.quote(str(containerfile))}"`。

### 独立复核命令索引（均可只读重放）
- 禁项 grep：overlay 目录 + xmnn.py（禁项正则见 CP-R1）
- WSL：`podman images`、`podman inspect localhost/xmnn-dev:latest
  --format '{{json .Config}}'`、`podman run --rm` 复跑
  _toolchain_guards.py 与双 ABI 断言、`podman-compose -f <abs>/
  compose.yaml config`、find 镜像内 /opt/xmnn-builder 与 pyc、
  host python3 zipfile 列 wheel、md5sum/find/git status 外部三仓、
  /tmp/xmnn-verify2.log 原件
- Windows：`PYTHONPATH=src python -m invoke --list`、
  `python -m invoke xmnn.ps`、`python -m invoke quant.ps`、
  `python -c "import jpman_client.tasks"`、check-links.py
