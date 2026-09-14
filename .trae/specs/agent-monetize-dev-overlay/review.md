# agent-monetize-dev 叠加层 - Independent Review

> Reviewer: fresh context（只读 + WSL2 只读/一次性容器；禁止 build 改动）。
> 规格/计划/证据：同目录 spec.md、tasks.md（文末完成证据汇总）。
> 镜像 `localhost/agent-monetize-dev:latest`=666b60ac2e88（1.67GB）；
> wheel 在 client/workspace/dist/。

> **环境须知（勿误判为栈缺陷）**：machine 当前 runRoot=
> /mnt/wslg/runtime-dir（tmpfs），**detached 容器约 40-60s 后被 WSL
> 会话回收**（inspect FinishedAt 零值、OOMKilled=false、日志为空；
> 前台 `podman run` 与 `run --rm` 稳定常驻）。这是 machine 存储/linger
> 环境退化（基底镜像本会话初曾整体丢失，已从 .image-cache load 恢复）。
> 评审运行态请用：① up 后**单次 exec 串行**（窗口内完成）或
> ② `podman run --rm --entrypoint bash` 一次性容器。勿用需要容器长时间
> 存活的多轮 exec；不要因此判栈失败。

- [x] CP-R1: 对 ai/外部零依赖与 builder 资产（AC-1）— **R1: pass**
- [x] CP-R2: compose 静态（AC-2：1 服务、2 bind、三必需、bridge、2224/8892、无特权/healthcheck/command）— **R1: pass**
- [x] CP-R3: 镜像构建/守卫/inspect（AC-3；666b、入口链、无 Healthcheck、pyc=0）— **R1: pass**
- [x] CP-R4: 单一 GIL ABI（AC-4：base GIL+tvm_ffi / main cp314t）— **R1: pass**
- [x] CP-R5: E2E 挂载/内核/端口（AC-5；run --rm：挂载点、kernelspec argv/env、2224/8892）— **R1: pass**
- [x] CP-R6: build-native 真实编译（AC-6：.so + NEEDED libtvm_ffi + RUNPATH）— **R1: pass**
- [x] CP-R7: native backend 数值一致（AC-7：backend=native + diff≤1e-9；root/devuser）— **R1: pass**
- [x] CP-R8: wheel 闭环（AC-8：py3-none-any、无 .so、隔离 venv import/reference）— **R1: pass**
- [x] CP-R9: 源码 3 处适配与 Windows 不回归（AC-9：git diff 仅 3 文件、.dll 保留、pytest 9/9）— **R1: pass**
- [x] CP-R10: 清理幂等（AC-10：down 容器清零、bind/wheel 保留）— **R1: pass（附 F4 info）**
- [x] CP-R11: invoke 8 任务/门禁/键集合（AC-11）— **R1: pass**
- [x] CP-R12: 零侵入零回归（AC-12：白名单；onnx/quant 零改；xmnn.py 改动属上会话遗留需核实非本栈引入）— **R1: fail（F1）→ R2: pass（F1 登记+回归关闭，见 O1）**
- [x] CP-U1: 范式保真（rubric AC-13：脚手架 dogfood；apt clang 等差异有事实出处）— **R1: 4/5（附 F2）→ R2: 5/5（F2 已修）**
- [x] CP-U2: 文档/参数一致性（rubric AC-14：12 件套、键/任务/端口三处一致、链接）— **R1: 4/5（附 F3）→ R2: 5/5（F3 已修）**

## Review History

### Review R1
- **Result**: **FAIL** — 12 个 rule CP 中 11 pass / 1 fail（CP-R12）；
  rubric 双 4（≥4 达标）。技术链路（编译/native 数值/wheel/挂载/内核/
  端口/门禁）全部独立复现实证通过；阻断项为 1 个**白名单外共享文件
  改动未登记**（manage.py，F1 medium）+ 2 个低危规范字面偏离（F2/F3）。
  按判定规则「任一 actionable → fail」，修复 F1~F3 后走 R2 复审。
- **Date**: 2026-09-14
- **Reviewer 方法与边界**：全程未 build/up -d/down/push；运行态证据全部
  来自 `podman run --rm`（含 bind 挂载的一次性容器）与 WSL 直连
  `wsl -d podman-machine-default`。未重跑 build-wheel.sh（避免覆盖
  workspace/dist 既有产物，wheel 本体已做内容/隔离 venv 全量审计）；
  未独立做两轮 compose up/down（评审约束），CP-R10 以「当前项目资源
  零状态 + bind/wheel 保留 + config 渲染」取证。会话起始 machine 已停，
  评审执行了 `podman machine start`（仅环境唤醒）。

#### 逐 CP 证据

**CP-R1 — pass（AC-1）**
- 禁项 grep（overlay 全目录，functional 文件）：`external/chaos/ai`、
  `chaos/ai`、`--mount=type=bind`、`CHAOS_ROOT`、`/builder/`、
  `import podman`、`docker.sock`、`network_mode: host` 均 0 命中；
  唯一 `privileged` 命中是 compose.yaml:11 注释「严禁 privileged」
  （规则文本，非配置）。
- `__X__` 占位符仅剩 2 处说明性注释（compose.yaml:4、.env.example:3，
  「替换占位符后使用」），无功能残留。
- 资产齐：builder/scripts/{build-native.sh,build-wheel.sh,lib/logging.sh}、
  smoke/{_toolchain_guards.py,smoke_native.py}、scripts/register-kernel.sh；
  镜像内守卫对资产清单 [OK]（见 CP-R3）。
- 4 个 shell 脚本 `bash -n` 全过；2 个 smoke 脚本 AST 解析通过；
  smoke 无 `shell=True`（subprocess 列表参数）。

**CP-R2 — pass（AC-2）**
- 在镜像内置 podman-compose（/opt/conda/envs/main/bin/podman-compose，
  podman 5.7.0）内只读挂载 overlay 跑 `podman-compose -f compose.yaml
  config`：rc=0、无渲染告警。1 服务 monetize；image+build(dockerfile)
  共存；network_mode: bridge；端口 2224:22 / 8892:8888；volumes 恰好
  2 个 bind，均长语法 `type: bind` + `bind.create_host_path: true`
  （target /workspace、/workspace/agent-monetize）；devices
  [/dev/fuse:/dev/fuse]、security_opt [label=disable]、cgroupns host
  各 1；environment 含 PYTHONPATH=/workspace/agent-monetize/src 与
  LD_LIBRARY_PATH=…/tvm_ffi/lib；无 privileged/healthcheck/command；
  restart unless-stopped。
- 相对路径层级实证：overlay 在
  apps/containers/client/overlays/agent-monetize-dev，
  `../../../../agent-monetize` 上 4 级 = apps/agent-monetize（真实存在，
  bind 容器内可见）；裸 compose 的 `../../workspace` = client/workspace。
- 说明（非缺陷）：容器内渲染时 `GRANT_SUDO: 'no'`，源自**基底镜像
  ENV GRANT_SUDO=no**（podman inspect 证实），xmnn 栈同环境渲染同样
  为 'no'（同族行为）；真实 invoke/WSL 路径该变量未设置，
  `${GRANT_SUDO:-yes}` 正确回退 yes。

**CP-R3 — pass（AC-3）**
- 镜像在位：`localhost/agent-monetize-dev:latest`=666b60ac2e88，
  1.67GB（xmnn-dev 4.43GB 的 38%，轻量变体成立）。
- inspect：Entrypoint=["/usr/bin/tini","--","/usr/local/bin/entrypoint.sh"]，
  Cmd=null，**Healthcheck=null（无健康检查）**，未覆盖 WORKDIR/USER
  （运行时默认 root）；Labels 含 org.specweave.component=agent-monetize-dev、
  layer=tvmffi-native-build、python-versions=cp314-gil、
  toolchain=apt-clang+apache-tvm-ffi-0.1.13、base-image。
- 守卫在全新 `run --rm` 容器内 **root 与 devuser 双身份全 [OK]**：
  base cp314 GIL、clang++ 21.1.8、patchelf 0.18.0、gdb 17.1、
  tvm_ffi 可导入、libtvm_ffi.so、tvm_ffi.h、core.cpython-314-*.so、
  3 项 builder 资产。
- pyc：镜像 /opt/monetize-builder、/opt/agent-monetize-dev-smoke、
  /opt/agent-monetize-scripts 下 `*.pyc`/`__pycache__` 计数=0
  （基底 ENV PYTHONDONTWRITEBYTECODE=1 + Containerfile 末层 find 双保险）。
- 未重新 build（评审约束）；构建期双守卫与本评审运行的是同一烤入脚本，
  运行即复现。

**CP-R4 — pass（AC-4）**
- base `/opt/conda/bin/python`：3.14.7，Py_GIL_DISABLED=0，
  sys._is_gil_enabled()=True，`import tvm_ffi` 成功。
- main `/opt/conda/envs/main/bin/python`：3.14.7，Py_GIL_DISABLED=1
 （cp314t，仅记录，不要求 tvm_ffi）。
- 单一 GIL 选型的 ABI 事实依据：apache-tvm-ffi 0.1.13.post3 wheel
  dist-info/WHEEL 仅 `Tag: cp314-cp314-manylinux_2_24/28_x86_64`
  （GIL，非 cp314t），Root-Is-Purelib=false。形态差异非拍脑袋。

**CP-R5 — pass（AC-5）**
- 挂载：bind 一次性容器内
  /workspace/agent-monetize/{pyproject.toml,src/agent_monetize/__init__.py,
  core/ffi_bridge.py,native/score_opportunity.cc} 均可见。
- 内核：/opt/conda/envs/main/share/jupyter/kernels/agent-monetize-dev/
  kernel.json argv[0]=/opt/conda/bin/python，env.PYTHONPATH=
  /workspace/agent-monetize/src，env.LD_LIBRARY_PATH 含 tvm_ffi/lib；
  `jupyter kernelspec list` root 与 devuser 均见 agent-monetize-dev。
- 端口（无参数前台 supervisord 的 `run --rm` 一次性容器，等效栈服务链；
  未用 compose up）：容器内 22/8888 均 listening；宿主
  127.0.0.1:2224 返回 `SSH-2.0-OpenSSH_10.2p1` banner；
  http://127.0.0.1:8892/lab 返回 **302**。服务由基底 supervisord 拉起，
  与 overlay 无关的容器内嵌套 rootless podman 启动失败（未给 /dev/fuse
  + newuidmap 无权）不影响 sshd/jupyter。

**CP-R6 — pass（AC-6，核心）**
- 在容器内把挂载源码复制到 /tmp/am 并**先删除既有 .so**（宿主产物零
  触碰），`SRC_ROOT=/tmp/am build-native.sh`：rc=0，clang++ 21.1.8
  一次编译成功，产物 88K。
- 动态定位（不写死）：site-packages 由
  `sysconfig.get_paths()['purelib']` 取自 base python；日志打印
  tvm_ffi include/lib 均为 /opt/conda/lib/python3.14/site-packages/tvm_ffi/…。
- `readelf -d`：**NEEDED libtvm_ffi.so**（另有 libstdc++/libm/libgcc_s/
  libc），**RUNPATH=/opt/conda/lib/python3.14/site-packages/tvm_ffi/lib**
  （-Wl,-rpath + patchelf --set-rpath 双保险，幂等再写一次）。
- 失败不静默：`SRC_ROOT=/nonexistent/am` → 中文错误「未找到 C++ 源码」
  **exit 2**。clang 缺失/tvm_ffi 头或库缺失 exit 2 分支静态核实
  （build-native.sh L33-49；头/库缺失分支未做运行时注入故障，无法在
  不篡改镜像的前提下模拟，代码路径直接）。

**CP-R7 — pass（AC-7，核心）**
- 全新编译的 /tmp .so：root 与 devuser 均 backend=**native**、
  tvm_ffi_available=True、load_error=None、native_lib_path 指向所加载
  .so；4 组固定输入 (100,.8,1.5,20)/(10,.8,1.5,2)/(3,.5,.2,.3)/
  (50,1,3,5) native vs `_reference_score_opportunity` **diff=0.000e+00**
  （≤1e-9），值在 [0,100]。
- 挂载树既有宿主 .so（87704B）：smoke_native.py root 与 devuser 均
  rc=0，含挂载点 5 项前置断言、reference 段、native 段全 [OK]。
- `pytest tests/test_ffi.py`（挂载树）：**9 passed**（rc=0）。

**CP-R8 — pass（AC-8）**
- 产物 `agent_monetize-0.1.0-py3-none-any.whl`（38540B）；zip 清单
  **0 个 .so/.pyd/native 文件**；dist-info/WHEEL：
  Root-Is-Purelib=**true**、Tag=**py3-none-any**、Generator=setuptools
  84.0.0；Name=agent-monetize Version=0.1.0。
- 隔离验证（G9：剥 PYTHONPATH）：base python 建
  `venv --system-site-packages /tmp/v`，`env -u PYTHONPATH` 装 wheel
  （--no-index --find-links workspace/dist；PyYAML 由 system-site 满足）
  → `import agent_monetize` 解析到 **/tmp/v/.../site-packages**（非挂载
  src，路径断言通过）；reference score=6.068041757、无 .so 时 FfiBridge
  优雅 backend=reference；console script `agent-monetize --help` rc=0。
  venv 随 --rm 容器销毁。
- 边界说明：未重跑 build-wheel.sh（避免覆盖宿主既有 wheel）；脚本
  bash -n 过、base env `import build,wheel` 可用、产物内容全审计。

**CP-R9 — pass（AC-9）**
- `git diff 0a408a0fb -- apps/agent-monetize --name-only`：**恰好 3
  文件**（config.py、config.yaml、tests/test_ffi.py）；ffi_bridge.py、
  native/build.ps1 相对基线 **0 改动**（name-only 为空）。
- config.py：新增 `_default_native_lib_name()` 按 sys.platform 三分支
  （win→.dll 字面保留 / darwin→.dylib / 其他→.so），目录前缀固定；
  FfiConfig.native_lib 改 field(default_factory=…)；from_dict 仅过滤
  「k=='native_lib' 且 falsy」。容器内实测：YAML 加载→.so；显式
  'custom/x.so' + fallback False → 用户值生效（**不吞显式配置**）；
  空串 → 回退平台默认 .so。
- config.yaml：硬编码 .dll 行改为注释说明 + 注释示例，不留激活键。
- test_ffi.py：NATIVE_LIB 扩展按平台变量；reference/降级用例平台无关；
  pytest 9/9。
- build.ps1 仍是 MSVC/.dll/tvm_ffi.lib 原脚本（未触碰）；打分业务
  逻辑零改动。

**CP-R10 — pass（附 F4 info，AC-10）**
- 当前机内：label io.podman.compose.project=agent-monetize-dev 容器
  计数 0、name=agent-monetize-dev 计数 0；network 无 agent-monetize
  项目网络；评审产生的一次性容器均 --rm/已清理。
- bind 保留：apps/agent-monetize/native/build/{.dll,.so} 在位
  （gitignored 运行时产物）；workspace/dist wheel 保留（38540B）。
- 未独立执行两轮 up/down（评审禁令）；down 行为为 podman-compose
  标准 label 过滤删除 + tasks.md 两轮证据，config 渲染正常，判 pass。

**CP-R11 — pass（AC-11）**
- Windows py314（editable 安装 jpman_client）`invoke --list`：
  monetize.* **恰好 8 任务**（build/up/down/ps/logs/smoke/build-native/
  wheel），quant/xmnn 命名空间同列正常（导入级无回归）。
- Windows 原生 `invoke monetize.ps`：打印双路径中文指引（WSL2 /
  env.run-cmd 自举）后 **Exit 1**。
- monetize.py 全文无 podman import（仅 docstring 禁项文字）；
  _SOURCE_MOUNTS 对 MONETIZE_SRC_PATH 做绝对 POSIX 解析 + 不存在
  Exit(1) 硬校验（代码 L106-115）；含路径参数 shlex.quote、
  auto_shortflags=False（G10）；smoke 双路径（运行→双 exec；未运行→
  run --rm 仅守卫）；build 基底存在预检。
- 键集合三方一致（12 键）：compose ${…} ≡ overlay .env.example ≡
  client/.env.example 注释段（MONETIZE_IMAGE_TAG/CONTAINER_NAME/
  SSH_PORT/JUPYTER_PORT/WORKSPACE/SRC_PATH + 四凭证 + PIP_MIRROR +
  注释态 BASE_IMAGE）。

**CP-R12 — FAIL（F1，AC-12）**
- 白名单外改动：`apps/containers/client/src/jpman_client/tasks/manage.py`
  处于工作区 M，且文件 mtime 18:52 落在 monetize 实施窗口
  （monetize.py 18:16、__init__ 18:28），**归属本栈实施**，非上会话
  遗留。改动重写 `_load_env_overrides`：把 `load_dotenv(override=False)`
  换为逐键写入并跳过空值（空 CONTAINER_HOST 不再注入 os.environ，规避
  podman CLI 5.7 空串误入 REST 模式）。实测新行为正确（空值不注入、
  非空保留、shell 优先语义不变；quant/xmnn/monetize --list 均正常），
  但它是**影响 root/quant/xmnn 全命名空间的共享模块**，spec FR/AC-12
  白名单与 tasks.md 均未申报，违反 NFR-2/AC-12 零侵入边界纪律。
  处置见 F1（补登记 + 回归记录，或还原）。
- xmnn.py 的 M 已核实**非本栈引入**：diff 为 external/chaos 默认路径
  锚定仓库根（root.parents[2]）的修正；monetize.py 仅 `from .manage
  import …` 与 `from .utils import …`，不 import/不依赖 xmnn.py 任何
  改动（xmnn.py mtime 20:09 为评审期间外部进程触碰，内容仍为路径
  锚定修正，非 monetize 接线）。
- onnx-quantized overlay、quant.py 在 git status 中零出现（未改）。
- 另一白名单外 `.vscode/settings.json`（cmake.sourceDirectory 指向
  projects/xuanspace）与本栈无关，记 F5 info。

**CP-U1 — 4/5（AC-13，附 F2）**
- 形态差异全部有事实/规格出处：apt clang（实测 apt clang 21.1.8 编单
  .cc 成功）vs conda LLVM 22；单一 cp314 GIL（wheel tag 实证
  cp314-cp314）vs 双 ABI；无 Nuitka/不编 TVM（tvm_ffi 头/库来自
  pip wheel 实证）；纯 Python wheel（pyproject 无 ext_modules 实证）；
  3 处源码适配最小化。三骨架 dogfood、无占位符功能残留。
- G1 长语法 bind ✓；G2 bridge+实证注释 ✓；G3 无 SHELL/HEALTHCHECK ✓；
  G4 exec 环境显式注入 PYTHONPATH/LD_LIBRARY_PATH ✓；G5 GIL 双断言
  （Py_GIL_DISABLED + _is_gil_enabled）✓；G7 .dockerignore `**/` 嵌套
  模式 + 末层 find ✓；G8 clang/patchelf/gdb 走 PATH/shutil.which 不
  写死目录 ✓；G9 隔离 venv 剥 PYTHONPATH ✓；G10 shlex.quote +
  auto_shortflags ✓；G6/G11 不适用（无 CMake/无 9p 重编）。
- 扣分：Containerfile L55 RUN 内联 `python -c "…\"…\""` 字面触碰
  SKILL §8「RUN 行禁止内层双引号 python -c」红线（外层 bash -lc
  单引号使 buildah 无二次分词、镜像已成功构建，功能无影响）→ F2。
  裸 `RUN chmod`（L60）与 xmnn-dev L108 同族先例，不扣分。

**CP-U2 — 4/5（AC-14，附 F3）**
- 脚手架 12 件套齐；8 任务名在 compose/.env/README/AGENTS/rules/
  __init__ 全部一致；端口 2224/8892 三处一致（2223/8890/2222/8888
  仅出现在对比注释）；overlay README 相对链接（../xmnn-dev/README.md、
  ../../.agents/rules/monetize-overlay.md）、rules 内链接
  （quant/xmnn-overlay.md、技能 SKILL.md 五级相对）目标均存在；
  client AGENTS/.agents README/README §13.5/apps AGENTS 七处登记 +
  C13 + changelog 齐；每文件单一职责。
- 扣分：vendor logging.sh 默认 on_error 帮助文本仍是 xmnn 专属内容
  （Nuitka/LLVM、libtvm.so、inv xmnn.build-tvm），与本栈不符 → F3。

#### Findings（actionable）

| # | sev | CP | 问题 | 复现 | 期望 |
|---|---|---|---|---|---|
| F1 | medium | R12 | manage.py（共享模块）白名单外被本栈修改且未在 spec/tasks 申报；影响 root/quant/xmnn 全路径 | `git status` 见 M apps/containers/client/src/jpman_client/tasks/manage.py；`git diff` 见 `_load_env_overrides` 空值注入语义变更；mtime 18:52 在 monetize 实施窗口 | 二选一：① 在 spec FR-9/AC-12 白名单与 tasks.md 补登该前置修复（含「空 CONTAINER_HOST 致 podman CLI 误入 REST」实证）并记录 quant/xmnn 回归结论（建议补跑一次两命名空间 Windows 门禁/--list，本评审已做导入级）；② 若 monetize 不实际依赖则还原。代码本身可保留（行为已验证正确），但必须显式登记 |
| F2 | low | U1 | Containerfile L55 RUN 内联 `python -c "import tvm_ffi; print(\"…\")"` 字面违反 SKILL §8 / xmnn Containerfile 头注释「RUN 行禁止内层双引号」 | 见 Containerfile.agent-monetize L55；镜像已成功构建（外层 bash -lc 单引号隔离，无实际分词风险） | 改为单引号 `python -c '…'`，或直接删除该内联检查（tvM_ffi 导入已由 _toolchain_guards.py 硬断言覆盖） |
| F3 | low | U2 | vendor logging.sh 默认 ERR 帮助仍是 xmnn/Nuitka/libtvm/build-tvm.sh 文案，误导本栈失败排查 | builder/scripts/lib/logging.sh L77-84（HELP heredoc） | 替换为 clang/tvm-ffi 排障文本，或在 build-native/build-wheel 调 log_set_error_help 固化本栈帮助 |
| F4 | info | R10 | machine 内残留实施会话手工容器 `monetize-debug`（Exited，无 compose 标签，非项目资源） | `podman ps -a` 见 monetize-debug localhost/agent-monetize-dev Exited | `podman rm monetize-debug`（清理即可，不影响 AC-10 判定） |
| F5 | info | R12 | `.vscode/settings.json` 新增 cmake.sourceDirectory=projects/xuanspace，与本栈无关 | `git diff -- .vscode/settings.json` | 非本栈引入，建议勿入本栈提交；白名单卫生确认 |

#### Rubric
- AC-13 范式保真：**4/5**（形态差异全部有 wheel ABI/实测事实；G1~G11
  逐条对齐；F2 一处字面红线偏离）。
- AC-14 产物原子性/文档一致性：**4/5**（12 件套齐、键/任务/端口/链接
  一致；F3 vendor 帮助文本残留 xmnn 内容）。

#### 一句话结论
技术交付质量高且核心链全部独立实证（clang++ 全新编译、NEEDED/RUNPATH
正确、root/devuser native 与纯 Python diff=0、纯 Python wheel 隔离
venv 可用、3 处适配 Windows 不回归），但存在 1 个白名单外共享文件
改动未登记（F1）+ 2 个低危规范字面项（F2/F3），按规则判定 **FAIL**，
修复后可快速复审转 pass。

---

### Review R2（fresh-context 复审，只读）
- **Result**: **PASS** — R1 的 F1~F5 全部 **close**（F1~F3 阻断/规范项
  实证修复，F4/F5 info 项清零/确认无涉）；14 个 CP 无回归（12 rule
  全 pass，rubric AC-13/AC-14 均升至 **5/5**）；核心链在**重建镜像
  6ad7e4b68502** 上由 R2 单次 `run --rm` 独立复跑全绿。无 actionable。
- **Date**: 2026-09-14
- **复审镜像**：`localhost/agent-monetize-dev:latest`=**6ad7e4b68502**
  （1.67GB，created 2026-09-14 12:30 UTC，晚于 Containerfile mtime
  20:24 CST，属 F2 修复后重建）。
- **Reviewer 方法与边界**：全程未 build/up -d/down/push；运行态证据
  全部来自 `podman run --rm -i --entrypoint bash`（经 stdin 喂 LF
  脚本的一次性容器，挂载 apps/agent-monetize）与 Windows py314
  （D:\…\envs\py314，editable jpman_client）静态门禁。未重跑
  build-wheel.sh 隔离 venv 安装（wheel 与 R1 同物：38540B/mtime
  19:27，仅做内容审计）、未重跑实时 2224/8892 端口（F2/F3 修复不涉
  入口/服务链，R1 supervisord 证据继续有效）。

#### Findings 处置（逐条独立核实）

| # | R1 sev/判定 | R2 处置 | R2 独立证据 |
|---|---|---|---|
| F1 | medium，阻断（manage.py 白名单外改动未登记） | **close** | ①来源：`git log` manage.py 最新提交为 1dbc22920；`git show 67812663d:…/manage.py` 与 `git show dcbf03fbb:…/manage.py`（xmnn 提交、monetize 提交）均仍是旧 `load_dotenv(override=False)` 版本——空值过滤仅存于未提交工作树；monetize 提交 dcbf03fbb 仅 10 文件（spec/tasks/compose/.env/builder 3 件/smoke 2 件/monetize.py），不含 manage.py/quant/xmnn/utils/.vscode。②无耦合：monetize.py L24-25 仅 `from .manage import _load_env_overrides, _project_root`（与 quant.py:37、xmnn.py:36 同型），_prepare_env L94 仅调一次、以 `env.get()` 读；MONETIZE_SRC_PATH L106-115 显式 resolve+`exists()` Exit(1) 硬校验、workspace L97-104 显式默认，均不读空值过滤；AST 实证无 `import podman` 语句（仅 docstring 禁项文字），亦不 import utils 新增 `ensure_workspace_checkpoint_writable`。③登记充分：spec.md NFR-2 末段（L96-101）显式闭合白名单——属性（SDK/quant 通用改进）、67812663d 未含、monetize 不依赖、决定不还原、三命名空间回归承诺五要素齐。④回归：py314 `invoke --list` quant/xmnn/monetize 三命名空间全列；直接调用实证空键（CONTAINER_HOST=、QUANT_WORKSPACE=）不注入 os.environ、非空键保留、shell 已 export 优先（override=False 语义不变）；`invoke monetize.ps` 仍 Exit 1 并打印 WSL2/自举双路径指引 |
| F2 | low（Containerfile RUN 内联 `python -c "…\"…\""` 违反引号纪律） | **close** | ①Containerfile.agent-monetize Layer 2（L36-56）已无任何内联 python -c：全文 grep `python -c` 仅 L56 一条说明性注释（"不在 RUN 行内联 python -c——OCI 引号纪律"）；tvm_ffi import/lib/header 断言移交 smoke/_toolchain_guards.py。②新镜像构建期守卫：Layer 4 RUN 在 `set -euo pipefail` 下 root 跑守卫 + `su devuser` 复跑（失败即 build fail），镜像 20:30 CST 后重建成功；R2 `run --rm` 复烤入脚本 root **rc=0**、devuser **rc=0**，tvm_ffi 可导入 / libtvm_ffi.so / tvm_ffi.h / core.cpython-314-*.so 四断言俱在。③镜像内 6 个 builder/smoke/scripts 文件 md5 与宿主 overlay **逐一相同**（build-native 042a76da…、build-wheel a3a5bf9f…、logging.sh 7347208c…、_toolchain_guards 901f0553…、smoke_native b69c251f…、register-kernel 8e203a1f…），即最新 COPY；镜像 pyc=0。**info 笔误（非 actionable）**：L55 注释称"Layer 5"而守卫 RUN 标号为 Layer 4，纯层号注释笔误 |
| F3 | low（logging.sh on_error 默认帮助残留 xmnn/Nuitka 文案） | **close** | builder/scripts/lib/logging.sh L77-85 heredoc 已全本栈化：pip 镜像源（--pip-mirror tuna\|aliyun）、clang++ -I/-L 与 apache-tvm-ffi、`python -m build`、MONETIZE_SRC_PATH 挂载、`.so 不入 wheel`、`inv monetize.build-native`；帮助体内 grep `Nuitka/LLVM/libtvm.so/build-tvm/xmnn` **0 命中**；`bash -n` OK（4 个 shell 脚本全过）；镜像内同文件 md5 一致。**info（非 actionable）**：L3 文件头自述"xmnn-dev 共享构建日志函数库（vendor…）"为 vendor 出处注释，与 FR-2"vendor（复用 xmnn-dev 的精简日志库）"表述一致，非失败排查文案；如需可润色为"vendor 自 xmnn-dev" |
| F4 | info（残留手工容器 monetize-debug） | **close** | `podman ps -a` 当前全机 **0 容器**；名称 grep `monetize-debug\|md2\|ldt\|base-debug` → NO_STRAY_CONTAINERS；评审自身容器均 --rm |
| F5 | info（.vscode/settings.json 无关改动） | **close** | dcbf03fbb 文件清单无 .vscode；工作树 diff 仅新增 `cmake.sourceDirectory=…/projects/xuanspace`，本栈代码/文档零引用，未纳入本栈提交；维持"勿入本栈提交"即可 |

**O1（R2 新增 info，非本栈 actionable）**：工作树另有 quant.py / utils.py
未提交改动（`ensure_workspace_checkpoint_writable`：rootless+9p 下
Jupyter devuser checkpoint 目录预建不可写的修复，quant.py 注释
"同 xmnn 栈"、utils docstring 标注"2026-09-14 xmnn-dev 栈实测"），
与 R1 已豁免的 xmnn.py M 同族。manage/quant/xmnn/utils 四文件 mtime
均为 20:24 前的 20:14:29（外部会话整批触碰，晚于 monetize 实施窗口
18:16/18:28）；monetize.py 对新符号零引用、--list 三命名空间无回归。
按 R1 对 xmnn.py 的同例处置（非本栈引入即不阻断 AC-12），建议由
xmnn/SDK 属主工作流自行登记/提交。

#### 14 CP 回归状态（R2 独立复核）

| CP | R2 | 关键新证据 |
|---|---|---|
| CP-R1（AC-1） | pass | overlay 全目录禁项 grep（external/chaos/ai、--mount=type=bind、CHAOS_ROOT、/builder/、import podman、docker.sock、host 网络、privileged: true）0 命中；"privileged" 唯一命中为 compose.yaml:11「严禁 privileged」规则注释；`__X__` 仅 2 处说明性注释；6 个资产在镜像且 md5 与宿主一致 |
| CP-R2（AC-2） | pass | 镜像内 `podman-compose -f compose.yaml config` **rc=0、无 stderr 告警**：1 服务 monetize；network_mode bridge；2224:22/8892:8888；恰好 2 bind（长语法 type: bind + create_host_path: true，target /workspace 与 /workspace/agent-monetize）；/dev/fuse、label=disable、cgroupns host 各 1；env 含 PYTHONPATH/LD_LIBRARY_PATH；无 privileged/healthcheck/command；restart unless-stopped |
| CP-R3（AC-3） | pass | 6ad7e4b：Entrypoint tini→entrypoint.sh、Cmd=null、**无 Healthcheck 键**、未覆 WORKDIR/USER；5 个 org.specweave labels 正确；root+devuser 守卫 rc=0；pyc=0 |
| CP-R4（AC-4） | pass | 守卫实测输出：base 3.14.7 `Py_GIL_DISABLED=0`/`_is_gil_enabled=True` + tvm_ffi 可导入；main 3.14.7 cp314t（Py_GIL_DISABLED=1）仅记录 |
| CP-R5（AC-5） | pass | 一次性容器挂载点 5 项断言 root+devuser 全 OK；kernel.json argv[0]=/opt/conda/bin/python、env.PYTHONPATH=/workspace/agent-monetize/src、env.LD_LIBRARY_PATH 含 tvm_ffi/lib；`jupyter kernelspec list` root 与 devuser 均见 agent-monetize-dev。实时端口未重跑（修复不涉服务链，R1 的 2224 banner/8892 302 证据有效） |
| CP-R6（AC-6，核心） | pass | 挂载源码复制 /tmp/am **先删 .so**（宿主零触碰）后 `SRC_ROOT=/tmp/am build-native.sh` rc=0，clang++ 21.1.8；`readelf -d`：**NEEDED libtvm_ffi.so**（+libstdc++/libm/libgcc_s/libc）、**RUNPATH=/opt/conda/lib/python3.14/site-packages/tvm_ffi/lib** |
| CP-R7（AC-7，核心） | pass | 挂载树 .so（87704B）smoke_native root+devuser：backend=**native**、load_error=None、native_lib_path 指向挂载 .so、固定输入 diff=**0.000e+00**；全新编译 /tmp .so 4 组输入 (100,.8,1.5,20)/(10,.8,1.5,2)/(3,.5,.2,.3)/(50,1,3,5) root 与 devuser diff **全 0.000e+00**，值均在 [0,100] |
| CP-R8（AC-8） | pass | workspace/dist/agent_monetize-0.1.0-py3-none-any.whl（38540B，与 R1 同物未重造）：zip 30 条目、**.so/.pyd/.dll = 0**、Root-Is-Purelib=true、Tag=py3-none-any、Generator setuptools 84.0.0。隔离 venv 行为沿用 R1 实证 |
| CP-R9（AC-9） | pass | `git diff --name-only 0a408a0fb -- apps/agent-monetize` 恰 config.py/config.yaml/test_ffi.py 3 文件；build.ps1 零改；挂载树 score_opportunity.dll（55808B，Windows 产物）保留 |
| CP-R10（AC-10） | pass | 机内 ps -a 零容器、无项目网络残留；bind 产物（.dll/.so）与 wheel 在位；R2 产生容器全部 --rm |
| CP-R11（AC-11） | pass | Windows py314 `invoke --list`：monetize.\* **恰好 8 任务**（build/build-native/down/logs/ps/smoke/up/wheel），quant 5 与 xmnn 8 同列正常；monetize.ps 门禁 Exit 1 双路径中文指引；AST 无 podman import |
| CP-R12（AC-12） | pass | F1 已 close（登记+回归）；monetize 提交 10 文件白名单内；agent-monetize 仅 3 文件；onnx overlay/quant 提交零涉；quant/xmnn/utils 工作树改动见 O1（外部 xmnn 域、monetize 零耦合，不阻断） |
| CP-U1（AC-13） | **5/5** | F2 字面红线项已消除，引号逻辑固化守卫脚本文件；G1~G11 对齐不变，形态差异（apt clang/单 GIL/纯 Python wheel/3 处适配）均有 wheel ABI 与实测出处；唯一残留为 L55 层号注释笔误（info） |
| CP-U2（AC-14） | **5/5** | F3 帮助文本已本栈化；12 件套齐、任务/键/端口三处一致、vendor 仅存准确出处注释（与 FR-2 一致）；其余 xmnn/LLVM/Nuitka 命中均为 README 对比表、Containerfile/.env 差异说明等事实表述 |

#### Rubric（R2）
- AC-13 范式保真：**5/5**（R1 扣分项 F2 已实证修复并重建镜像；
  无新增无依据偏离）。
- AC-14 产物原子性/文档一致性：**5/5**（R1 扣分项 F3 已修复；
  仅 2 条纯注释级 info：Containerfile L55 层号笔误、logging.sh L3
  vendor 出处措辞，均不影响功能/排障/一致性判定）。

#### 一句话结论
F1~F5 全部 close，核心链在重建镜像 6ad7e4b68502 上由 R2 单次
run --rm 独立复现全绿（clang++ 全新编译 NEEDED/RUNPATH 正确、
root/devuser 原生与参考 4 组输入 diff 全 0、纯 Python wheel 无原生件、
compose/门禁/白名单无回归），12 rule 全 pass、双 rubric 5/5、
无 actionable → **PASS**。
