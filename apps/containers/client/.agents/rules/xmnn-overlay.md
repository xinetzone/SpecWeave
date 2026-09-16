# xmnn.* 开发/打包叠加栈规则（podman-compose 编排层）

> 单一职责：本文件只约束 `invoke xmnn.*` 命名空间与
> `overlays/xmnn-dev/` 叠加栈。根命名空间（SDK→CLI 两层）规则见
> [invoke-tasks.md](invoke-tasks.md) 与 [sdk-connection.md](sdk-connection.md)；
> 同族 quant 栈规则见 [quant-overlay.md](quant-overlay.md)，本文件不重述其
> 通用条款，只定义 xmnn 栈特有契约。

## 1. 架构边界（四层不可混）

| 层 | 载体 | 职责 |
|---|---|---|
| 根/`container.*` | podman-py SDK → CLI fallback | 单容器命令式生命周期（零回归对象） |
| `env.*` | podman CLI 子进程 | client SDK 自举叠加镜像 |
| `quant.*` | podman-compose 子进程 | ONNX 量化工作负载栈 |
| **`xmnn.*`（本文件）** | **podman-compose 子进程（禁止 import podman）** | **npu_tvm/xmnn 源码调试 + Nuitka wheel 打包栈（overlays/xmnn-dev）** |

- xmnn.py 内**禁止** `import podman` / `from podman`；禁止把本层提升为
  `invoke run` 的后端或向根路径回流（同 C11 裁决）。
- xmnn.py 现为 **StackSpec 声明 + 长任务薄封装**：唯一事实源 `XMNN_SPEC`，
  六任务（build/up/down/ps/logs/smoke）由
  `overlay_core.make_stack_tasks(XMNN_SPEC)` 工厂生成；`build-tvm` /
  `wheel` 两个栈内 exec 长任务保留在 xmnn.py，调内核 helper（gates /
  ensure_runtime_ready / require_running / run_compose）。同构编排函数
  （门禁/prepare_env/compose_argv/残留自愈等）唯一定义在 overlay_core。
  红线：overlay_core 与 jpman_common 零栈知识（不得 import 具体栈模块、
  不出现栈名/路径），栈模块零 podman。
- 8 个任务：`build / up / down / ps / logs / smoke / build-tvm / wheel`。
  `build-tvm` 与 `wheel` 是对运行中容器的 `podman-compose exec` 长任务。

## 2. 平台门禁 / WSL 桥接（硬约束）

与 quant 栈完全同族：
1. Windows 原生 CPython 一律先过 `overlay_core.gate_platform(XMNN_SPEC)`
   ——**自动桥接优先**（2026-09-15 起）：经
   `utils.run_in_wsl_bridge(extra_env_keys=XMNN_SPEC.bridge_env_keys)`
   把本任务原样转发到 WSL 发行版（默认 `podman-machine-default`（client
   专用 rootless 发行版，与 flapping 的默认 machine 相互独立、镜像存储
   不互通；`COMPOSE_WSL_DISTRO` 可覆盖，`none` 显式关闭））内执行，
   实时透传，返回码原样上抛；桥接成功即 `Exit(0)` 收尾，不再走
   Windows 侧后续逻辑。栈专属透传键（5 个 XMNN_* 键 + NPU_TVM_PATH /
   NPUUSERTOOLS_PATH / MODELS_PATH）由 `XMNN_SPEC.bridge_env_keys`
   声明，utils 只内置 `_BRIDGE_COMMON_ENV_KEYS` 通用键集；
2. 桥接不可用（无 wsl.exe / 发行版缺失 / none 哨兵）才回退门禁
   `Exit(1)`（动态推导的 /mnt 路径 + 发行版检查 + WSL2 发行版 /
   `invoke env.run-cmd` 双路径中文指引）；
3. POSIX 缺 podman-compose 二进制
   `overlay_core.gate_compose_binary(XMNN_SPEC)` Exit(1)，
   提示 `pip install -e ".[compose]"`（复用既有 optional extra，不新增依赖）；
4. 顺序固定：先平台后二进制；build/up/smoke/build-tvm/wheel 另过 daemon 预检
   （`overlay_core.ensure_runtime_ready`）。
   WSL 桥接目标**禁止复用 `WSL_DISTRO_NAME`**（SDK 连接专用，默认
   podman-machine-default flapping 且镜像存储不互通）。

## 3. 双 ABI 工具链契约（不可互换）

| 角色 | env | Python | 内容 |
|---|---|---|---|
| Jupyter 服务 | `/opt/conda/envs/main` | 3.14.x **cp314t**（GIL off） | 基底 jupyterlab（supervisord，devuser） |
| 编译/打包/内核 | `/opt/conda`（base） | 3.14.x **cp314 GIL enabled** | nuitka==4.1.3、scikit-build-core、build、invoke、ipykernel、wheel 19 依赖 |
| 原生工具链 | main env | — | llvmdev/clangdev/clang/lld **22.1.8**、cmake、ninja、make、ccache、libgcc、libstdcxx-ng |
| **编译前端（npu_tvm）** | 系统层（apt） | — | **gcc/g++**（系统包；2026-09-15 起作默认 CC/CXX） |

- **编译前端裁决（2026-09-15）**：npu_tvm 构建默认用系统 `gcc/g++`
  （build-tvm.sh `CC=${CC:-gcc}`/`CXX=${CXX:-g++}`，env 可覆盖回退 clang）。
  原因：VTA FSIM 仿真驱动（`vta/vta_hw/src/sim_*`）的「VLA+初始化器」是
  Clang 22 hard error（`variable-sized object may not be initialized`）、
  GCC 允许的扩展。LLVM/Clang 22 工具链**仍必须安装**（llvm-config 供 CMake
  `USE_LLVM`、lld 供链接、构建期守卫断言 SONAME）；只把编译前端切 gcc，
  不改变工具链契约。Nuitka 4.x 打包后端同样默认找 gcc（更标准）。

- **Nuitka 4.1.3 在 cp314t 编译失败、cp314 GIL 成功**（allocator.h:606
  Spike 结论）：所有打包/验证脚本的解释器固定 `/opt/conda/bin/python`；
  工具链 bin 用绝对路径（CC/CXX/LLVM_CONFIG 指向 main env），跨 env
  PATH/LD_LIBRARY_PATH 导出只在脚本进程内生效，不反转全局 PATH。
- conda 装工具链必须 pin `python=*=*cp314t`，构建期
  `_toolchain_guards.py` 对双 ABI 做双向断言（main 被求解互换即构建失败）。
- 系统层仅 apt 装 patchelf（CMake RPATH 阶段）、gdb（调试诉求）、gcc/g++（npu_tvm 编译前端，见上）。

## 4. 源码仅运行时挂载（构建期零接触）

- 四个 bind（一律长语法 + `bind.create_host_path: true`）：
  `XMNN_WORKSPACE→/workspace`、`NPU_TVM_PATH→/workspace/npu_tvm`、
  `NPUUSERTOOLS_PATH→/workspace/npuusertools`、`MODELS_PATH→/workspace/models`。
- invoke 路径把四个宿主路径解析为**绝对 POSIX 路径**注入（Dimension A
  复用 `to_posix_path`），相对路径相对 invoke cwd；三个源码路径做
  **存在性硬校验**（缺失 Exit 1 + 中文指引），workspace 自动 mkdir。
- **已知副产物（2026-09-14 裸 podman-compose 1.6.0 实测）**：裸
  `podman-compose up`（不经 invoke 绝对路径注入）时，长语法 bind 的相对
  source + `create_host_path: true` 会在 `client/workspace/` 下预创建
  `npu_tvm/npuusertools/models` 三个**空目录**（不影响真实挂载——容器内
  绑定的仍是 external/chaos 真源码，由 smoke_mounts 路径前缀断言保证）；
  down 后可安全 `rmdir`（均为空）。invoke 路径注入绝对路径不产生该副产物。
- 镜像构建上下文 = overlay 目录自身；Containerfile 不得 COPY/引用宿主
  源码树，不得出现 BuildKit `--mount=type=bind`、`chaos/ai`、`CHAOS_ROOT`。
- TVM 构建产物默认就在挂载源码树 `npu_tvm/build/`（复用宿主既有
  libtvm.so，调试直观）；9p 全量编译慢时把 NPU_TVM_PATH 指向 WSL 原生
  克隆（README 必须给出该性能提示）。
- **9p 无主旧产物清理契约（2026-09-15 实证，排障 W-I7）**：跨环境（WSL
  发行版/其他容器/本栈）混用同一宿主 build/ 时，旧产物在 9p 视角属主为
  `65534:65534`、目录 755；当前容器 root 无 DAC 绕过且 chmod EPERM、
  devuser(1000) 同样不可写 → `inv config -f` 的 `_clear_directory_contents`
  必在 rmtree 阶段 EACCES。**容器内无解，必须宿主侧清理**
  （`Remove-Item -Recurse -Force <宿主 NPU_TVM_PATH>\build`，NTFS ACL 允许、
  9p 即时同步）。已在 npu_tvm `tasks.py` 加 onexc（只读位 chmod 重试 +
  9p 场景中文指引）；该文件属 external/chaos/npu_tvm 自有 git 仓（origin
  本地 pu_tvm.git），不入 SpecWeave 提交。脚本头注禁止再写「容器内
  rm -rf build 可强制全量」——9p 无主文件场景该命令会失败。
- **checkpoint 可写性契约**：Jupyter 以 devuser(1000) 运行，而
  rootless+9p/drvfs 下容器内 root 预建的
  `$XMNN_WORKSPACE/.ipynb_checkpoints`
  在容器视角为 0:0 755，devuser 保存 notebook 必报 Errno 13。invoke 侧
  `overlay_core.prepare_env(XMNN_SPEC)` 在 mkdir 工作区后**必须**调用
  `utils.ensure_workspace_checkpoint_writable()`（quant 栈同族接线；
  幂等 0777、只改权限位不改属主、只作用该单一目录不递归、不触碰三个源码
  bind）；禁止把该职责退回镜像/entrypoint 层（薄叠加不覆盖基底）。
- **up 三道 preflight 自愈契约（2026-09-15 实证，三栈共用
  `overlay_core.up_preflight`，顺序不可调换）**：
  ① **残留容器**——`podman ps -a -q --filter label=<project> --filter
  status=created --filter status=exited`（多 status 为 OR 语义）探测本项目
  非 running 容器，命中即先 `compose down`（**不**加 --volumes，保留
  ccache 卷/镜像/workspace/源码 bind）；
  ② **跨控制平面分歧**——读活体容器标签
  `com.docker.compose.project.config_files` 原文，与本平面将下发的
  `--file` 原文比较：Windows 裸 compose 写 `D:\...`、WSL 桥接 invoke 写
  `/mnt/d/...`，compose config-hash 按原文计算（**禁止路径等价归一**），
  不一致即判为他平面创建的栈，先优雅 `compose down` 再 up，避免
  podman-compose 强制 recreate 时强拆 pod infra 留下孤儿 rootlessport；
  ③ **孤儿 rootlessport 回收**——无活体项目容器时用 `ss -ltnp` 检查本栈
  端口，只对进程名为 rootlessport 的持有者定点 TERM/KILL（他栈 pasta/
  conmon 一律不动；ss 缺失则跳过不阻断）。
  根因链：跨平面交替操作（或异常中断）致 podman-compose 1.6 pod 模式
  强拆 infra conmon，rootlessport 在 WSL 被 `/init` 收养成为孤儿继续监听，
  新 pod bind 2223/8890 报 `address already in use`（exit 125，优雅 down
  同样可能触发，故②后必须接③）；裸 compose 翻车现场直接重跑
  `invoke xmnn.up --skip-build` 即可恢复。**纪律：同一栈固定单一控制平面**
  （长期裸 Windows compose 就不切 invoke，反之亦然）。quant/monetize
  同族接线；排障条目 W-I10。

## 5. 打包内核契约（/opt/xmnn-builder 自包含）

- 资产：pyproject.toml（wheel 元数据单一事实源，19 依赖）、CMakeLists.txt、
  _xmnn_bootstrap.py、xmnn_bootstrap.pth、scripts/{build-wheel.sh,
  build-tvm.sh,verify-wheel.sh,install-build-deps.py,lib/logging.sh,
  lib/ast_inject.sh}。
  **禁止**从 external/chaos/ai 跨目录 COPY 或 source（两个 lib 必须 vendor）。
- **AST 注入/还原纪律**：注入/还原逻辑在可 source 的
  `builder/scripts/lib/ast_inject.sh`，build-wheel.sh 临时向 tvm/vta/xmnn
  的 `__init__.py` 注入 6 个 Python 3.14 已删 AST 类的兼容 PREAMBLE，备份
  为 `.bak_<tag>`（临时文件+mv 原子备份）；父 shell 注册**全程统一**的
  `_restore_all` EXIT trap（三对确定性 .bak 路径，子 shell 被 SIGKILL 时
  由父退出兜底），正常路径编译后立即还原；`ast_inject` 自带四态自愈矩阵
  （marker/bak 组合：注入态+bak 在→自愈、注入态无 bak→Exit 2 要求
  git checkout 不覆盖、截断残留+bak 在→用干净 bak 自愈、正常态→备份注入）；
  ast_restore 信息走 stderr（stdout 只输出 backup 路径）。外部源码工作树
  零修改是硬验收（AC-9）。
- Nuitka 语义不可裁剪：tvm 串行先行 → vta/xmnn 后台并行；三次调用差异
  （交叉 nofollow、dill-compat、vta include-data-dir、jobs、--module、
  --quiet、--no-pyi-file）保持；退出码经 `.vta_exit/.xmnn_exit` 回传。
- **SONAME 漂移防护**：CMake 对 7 个 LLVM 依赖库（libLLVM.so.22*、
  libz/libzstd/libxml2/libiconv/libicuuc/libicudata）按 glob 收集，并按
  「NEEDED 只认 SONAME 短名」单副本安装（软链去引用 `cp -L` 为短名常规
  文件——wheel ZIP 经 scikit-build 打包会解引用软链；被指向的长名真实文件
  跳过；无链真实文件原名装），glob 空或 cp 返回码非 0 均 FATAL_ERROR；
  CMake 4.x 只用复数 `REMOVE_DUPLICATES`（3.x 接受的单数拼写在 4.4 FATAL）。
  构建期守卫对 llvm-config --libdir 做同款 glob 硬检查并打印实际 SONAME。
  patchelf 缺失/数据目录缺失同为 FATAL（不允许 WARNING 静默出残 wheel）。
- wheel 产物落 `$DIST_DIR`（默认 /workspace/dist，宿主可见）；Nuitka
  中间产物在容器内 /opt/xmnn-builder/build；ccache 走命名卷
  `xmnn-ccache`（挂 /root/.ccache，down 默认保留，--volumes 删除）。
- **wheel 元数据（pyproject.toml 单一事实源，2026-09-16 起）**：
  `[project.scripts] xmflow = xmnn.cli.xmflow:app` 随 whl 生成 console
  script `/opt/conda/bin/xmflow`——Nuitka 包不支持 `python -m`
  （runpy get_code），console script 是交付镜像内 CLI 的唯一入口；
  `typer>=0.12` 必须在 dependencies（CLI 运行时依赖，不能只放 dev
  extra）。改 pyproject 后须重打 whl；运行中旧栈容器的
  /opt/xmnn-builder 是镜像 COPY 副本（非挂载），需 `podman cp` 进容器
  或重建镜像，打包才读得到新文件。
- verify-wheel.sh 在 `--system-site-packages` 临时 venv 内装 wheel 跑
  10 项检查，结束删除 venv——base env 的源码调试链路零污染。

## 6. compose ↔ rootless 三必需 / bridge / 环境注入

- 三必需（`devices: [/dev/fuse:/dev/fuse]`、`security_opt: [label=disable]`、
  `cgroupns: host`，1.6.0 空操作须注释声明）、凭证四变量与
  `network_mode: bridge` 已**上移 `../_shared/base-rootless.yaml`**
  （extends 单一事实源），xmnn 栈 compose.yaml 以
  `extends: {file: ../_shared/base-rootless.yaml, service: rootless-base}`
  继承，**禁止在栈文件重复声明**；严禁 privileged、docker.sock、host 网络。
- `network_mode: bridge` 是**带证据的偏差**：2026-09-14 同机实证 machine
  无 systemd user bus 时默认项目网络 aardvark-dns 必失败；实证注释保留在
  基文件与 xmnn compose.yaml 文件头，不得擅自删改。
- 栈文件只保留栈专属字段：image/build/ports/四个 bind volumes、调试
  environment、`labels.component`；`xmnn-ccache` 命名卷等栈专属卷保持
  栈内声明（基文件无 volumes/build/env_file/ports）。extends 合并语义
  （rec_merge / L2844-L2849 路径解析）见 [quant-overlay.md](quant-overlay.md) §4.1。
- 调试环境变量（PYTHONPATH/TVM_LIBRARY_PATH/LD_LIBRARY_PATH/NPU_TOOLS_ROOT/
  XMNN_TOOLS_ROOT）经 compose environment 注入；LD_LIBRARY_PATH 必须含
  npu_tvm/build、build/vta 与 /opt/conda/envs/main/lib（非登录 exec 不读
  profile.d，libtvm 的 NEEDED 解析依赖此注入；spec FR-6 有留痕）。
- 端口默认 2223/8890（与 onnx 的 2222/8888 错开，支持并行）。

## 7. 标签接缝

沿用 podman-compose 自动写的 `io.podman.compose.project` /
`io.podman.compose.service` 标签做运行探测（xmnn.smoke/wheel/build-tvm
的容器筛选），不自行发明标签键；业务标签仅允许 `org.specweave.*`。

## 8. 冒烟双路径

- `_toolchain_guards.py`（镜像烤入 /opt/xmnn-dev-smoke）：构建期 root +
  devuser 双身份执行；栈未运行时 `podman run --rm --entrypoint
  /opt/conda/bin/python <img> <script>` 也可独立执行（不依赖挂载）。
- `smoke_mounts.py`：仅栈运行路径（compose exec）；三挂载点断言始终执行；
  libtvm.so 缺席时跳过 import/算例段并 exit 0（首次未编译合法），存在时
  断言 tvm/vta/xmnn 来自 /workspace 源码并跑 tvm.build('llvm') 向量加。
- 内核 `xmnn-dev`（argv=/opt/conda/bin/python，env 携带源码路径）注册到
  main env share/jupyter/kernels，root/devuser 双可见，构建期断言。

## 9. 选型依据与边界

- 选型同 OKF 知识包 concept 10：可复现工作负载（多文件路径/环境/构建产物
  联动）用 compose 声明式栈；单资源操作留 SDK。
- 本栈是**开发/打包端**；wheel 消费型 notebook 形态（从预构建镜像 COPY
  wheel 直装）属 scratch 栈 spec `xmnn-overlay-rebuild`，不回流本目录。
- external/chaos/ai 仅为事实参考；npu_tvm/npuusertools/models 是外部
  git 仓库，只读/只挂载，任何任务不得改写其工作树（AST 临时注入除外，
  且必须还原）。
