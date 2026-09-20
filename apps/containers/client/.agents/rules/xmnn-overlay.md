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
  `overlay_core.make_stack_tasks(XMNN_SPEC)` 工厂生成（`supports_offline=True`
  时工厂额外生成 `save` / `load` 两个离线条目）；`build-tvm` /
  `wheel` 两个栈内 exec 长任务保留在 xmnn.py，调内核 helper（gates /
  ensure_runtime_ready / require_running / run_compose）。同构编排函数
  （门禁/prepare_env/compose_argv/残留自愈等）唯一定义在 overlay_core。
  红线：overlay_core 与 jpman_common 零栈知识（不得 import 具体栈模块、
  不出现栈名/路径），栈模块零 podman。
- 10 个任务：`build / up / down / ps / logs / smoke / build-tvm / wheel /
  save / load`。`build-tvm` 与 `wheel` 是对运行中容器的
  `podman-compose exec` 长任务；`save` / `load` 是镜像归档出口/入口
  （离线通道，契约见 §10）。

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
| 编译/打包/内核 | `/opt/conda`（base） | 3.14.x **cp314 GIL enabled** | nuitka==4.2.1、scikit-build-core、build、invoke、ipykernel、wheel 19 依赖 |
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
- **工作区 9p 无主文件契约（2026-09-20 实证，排障 W-I19）**：宿主工作区若被
  **另一 UID 映射上下文**写过（subuid 基线 ≠ 本机 524288 的运行时，如 Docker /
  其他 WSL podman 实例），旧文件在宿主侧落成 **100999** 之类**未映射 UID**，
  容器内呈现 `65534:65534`（nobody）——当前容器 root 对其读写皆 EPERM、
  `chown` 报 `Operation not permitted`，Jupyter 保存 notebook 即
  `Permission denied` 且工具栏显示 `notebook is read-only`（**新建**文件不受
  影响：工作区根 0777，新文件取挂载默认属主 1000:1000）。**容器内无解，必须
  宿主侧换 inode**：`cp` 备份 → `rm` 原文件（父目录 0777，删除只看目录写位）
  → `cp` 回原路径；`.Trash-<uid>` 等旧垃圾目录直接 `rm -rf`。**红线：`chmod`/
  `chown` 在 9p/drvfs 无 `metadata` 挂载项下是空操作**（rc=0 但属性不变，本机
  实测），禁止把「宿主侧 chmod/chown 修权限」写进任何排障指引或自愈代码；
  判别唯一入口是容器内 `ls -lan /workspace` 出现 `65534`。**纪律**：同一宿主
  工作区固定单一运行时，勿在 Docker / 其他 WSL podman 实例 / 本栈之间交替写入。
- **up 三道 preflight 自愈契约（2026-09-15 实证，三栈共用
  `overlay_core.up_preflight`，顺序不可调换）**：
  ① **残留容器**——`podman ps -a -q --filter label=<project> --filter
  status=created --filter status=exited`（多 status 为 OR 语义）探测本项目
  非 running 容器，命中即先 `compose down`（**不**加 --volumes，保留
  ccache 卷/镜像/workspace/源码 bind）；
  ② **跨控制平面分歧**——读活体容器标签
  `com.docker.compose.project.config_files` 原文，与本平面将下发的
  `--file` 原文比较（**含 GPU 覆盖文件**：期望集与 `compose_argv` 同源，
  见 §11.1.1 C23）：Windows 裸 compose 写 `D:\...`、WSL 桥接 invoke 写
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
  为 `.bak_<tag>`（**字节级**临时文件+mv 原子备份）；备份与组装复制一律
  **禁止 `cp -p`/`cp -a`/`--preserve`**——rootless userns 只映射启动用户
  单个宿主 UID，外部同步树文件的 POSIX ACL 含未映射 UID（如多机 pc=1000/
  ai=1006）时，cp 复制 ACL 的内核 setxattr 返回 EINVAL（与目标 FS 无关，
  容器 overlayfs 同样失败）；还原必须 `cat 备份 > 原文件` 回写**原 inode**
  （不得 mv 替换，否则源码文件属主/模式/ACL 漂移），cp 失败即清 tmp、
  ast_inject 入口幂等清扫同 tag 陈旧 `.tmp.*`；CMake 组装侧对应禁令：
  autolibs 用 `cp -R` 不用 `cp -a`（wheel 不携带 ACL/属主）。父 shell
  注册**全程统一**的 `_restore_all` EXIT trap（三对确定性 .bak 路径，子
  shell 被 SIGKILL 时由父退出兜底），正常路径编译后立即还原；`ast_inject`
  自带四态自愈矩阵（marker/bak 组合：注入态+bak 在→自愈、注入态无 bak→
  Exit 2 要求 git checkout 不覆盖、截断残留+bak 在→用干净 bak 自愈、
  正常态→备份注入）；ast_restore 信息走 stderr（stdout 只输出 backup
  路径）。外部源码工作树零修改是硬验收（AC-9：内容、属主、模式、ACL
  四不变）。
- Nuitka 语义不可裁剪：tvm 串行先行 → vta/xmnn 后台并行；三次调用差异
  （交叉 nofollow、dill-compat、vta include-data-dir、jobs、`--mode=module`、
  --quiet、--no-pyi-file）保持；退出码经 `.vta_exit/.xmnn_exit` 回传。
- **模式旗标必须写 `--mode=module`**：4.x 里遗留别名 `--module` 只置
  `module_mode`，而「module 模式专属选项」告警的判据是 `compilation_mode`
  （仅 `--mode=` 赋值），故 `--module` 配 `--no-pyi-file` 会误报
  `has no effect`；改旗标是唯一正解（删 `--no-pyi-file` 会重新产出 .pyi）。
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
- **Jupyter 登录态命名卷（2026-09-20 起，C22）**：第二个命名卷
  `xmnn-jupyter` 挂 `/home/devuser/.local/share/jupyter`，持久化
  `jupyter_cookie_secret`/`notebook_secret`——否则密钥随容器临时层轮换，
  `down/up` 重建后浏览器旧标签页的 Terminal/notebook REST 全被踢回登录
  （请求在浏览器侧中止，服务端零日志，极易误判为 PTY/权限故障，详见
  docs/04 C-I6）。该目录镜像内属主 1000:1000/mode 700，新命名卷首次
  copy-up 属主与可写性必须保持（真机实测）；down 默认保留，--volumes
  与 ccache 一并删除，删除后重新登录属预期。禁止用 bind 指宿主家目录。
- **SSH host key 命名卷（2026-09-20 起）**：第三个命名卷
  `xmnn-ssh-host-keys` 挂 `/var/lib/jpman/ssh-host-keys`。基底 entrypoint
  以 `mountpoint -q` 为唯一分流判据——挂载即持久模式（key 落卷内、
  `sshd_config` 的 `HostKey` 指向卷路径、清空 `/etc/ssh` 默认位置），
  未挂载则回退容器层生成并打 WARN（重建即轮换，客户端遭
  `REMOTE HOST IDENTIFICATION HAS CHANGED`）。**卷名与落点必须与客户交付栈
  [overlays/xmnn-runtime/release/compose.yaml](../../overlays/xmnn-runtime/release/compose.yaml)
  一致**（同 `xmnn-ssh-host-keys` / 同 `/var/lib/jpman/ssh-host-keys`），
  属主/权限（700 目录 + 600 key）由 entrypoint 自管；down 默认保留，
  `--volumes` 与上述两卷一并删除（删后指纹轮换属预期）。
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
  environment、`labels.component`；`xmnn-ccache`/`xmnn-jupyter`/
  `xmnn-ssh-host-keys` 三个命名卷等栈专属卷保持栈内声明（基文件无
  volumes/build/env_file/ports）。extends
  合并语义（rec_merge / L2844-L2849 路径解析）见 [quant-overlay.md](quant-overlay.md) §4.1。
- up 成功横幅**回读容器内实际凭证并打印**（C24，2026-09-20）：`.env` 凭证键
  留空为常态，密码/token 此时由容器内 entrypoint 用 `pwgen` 生成、**只进容器
  启动日志**，故 `up` 收尾从容器日志**头部**回读（`podman logs <cid> | head
  -n 300`，勿用 `--tail`——横幅在启动日志头部，`invoke <ns>.logs` 默认
  `--tail=100` 只看尾部，手动查日志时会被挤出窗口）解析出密码行与 token，打印
  `密码    <user> / <password>` 并用回读 token 构造「直达」行。**`.env` 全程
  只读、不回写**（凭证生成责任留在基底 entrypoint，overlay 内核不得写 .env）。
  内核通用实现 `overlay_core.read_container_credentials` /
  `parse_container_credentials`（四栈同构，解析纯函数可单测）；密码必须用
  `SSH login:` 行取到的用户名反查对应 password 行——只按 `password:` 匹配会先
  命中 `Root password:`（`ALLOW_ROOT_SSH=yes` 时存在）而误报 root 密码。
  回读失败（容器未跑/日志无横幅）静默降级为不打印，绝不阻断 up。
  **前置条件——日志必须可被 podman 读取**：2026-09-20 实证本机发行版默认
  `log_driver = journald`（`/usr/share/containers/containers.conf`），在 WSL
  嵌套 systemd 命名空间下 `podman logs <cid>` 返回 **0 字节**（日志进了宿主
  journal，只有 `journalctl CONTAINER_NAME=<name>` 能读），于是凭证回读与
  `invoke <ns>.logs` **同时**失效——这才是「看不到凭证」的最初根因。修复：
  基段 `_shared/base-rootless.yaml` 显式声明 `logging: {driver: k8s-file}`
  （四栈同构继承，`test_compose_merge.py` 有正向断言锁死），日志落盘文件后
  `podman logs` 恢复可读。**禁止**依赖宿主默认日志驱动。
- up 成功横幅在配置了 `JUPYTER_TOKEN` 时额外打印「直达」行
  （`http://localhost:<jupyter 端口>/lab?token=...`，内核通用 helper
  `overlay_core.jupyter_direct_url`，四栈同构；token 为空不打印），
  使容器重建后免登录直达，与 C22 共同消除重建即重登体验；token 亦优先取
  C24 回读值（预设时二者同源）。
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
  §7「离线完备性」同在该脚本内（契约见 §10），随构建期双身份执行自动获得
  两个身份的覆盖，**不单独增设第二个守卫入口**。
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

## 10. 离线契约

- **两阶段契约（2026-09-17 固化，不新增命令名）**：本栈开发流程显式拆为
  **阶段一「镜像环境构建」（有网侧，一次性）** = `xmnn.build` + `xmnn.save`，
  与 **阶段二「启动开发环境并开发」（无网侧）** = `xmnn.load` +
  `xmnn.up --offline` + `build-tvm` / `wheel` / `verify-wheel.sh`。两阶段是
  既有任务的**用法契约**而非新入口，命令表面保持 10 个不变。契约要求：
  ① 阶段二可能触达的每一项外部依赖，都必须在阶段一固化进镜像；
  ② 阶段间只有单向传递（镜像归档 + 使用者自备源码树），阶段二**没有回补
  手段**——缺任何一项的正确处置是回阶段一重建，禁止在无网侧 pip/apt 补救；
  ③ 因此所有完整性校验必须前移到阶段一（见下条守卫）。
- **离线自足性由构建期守卫实测（阶段一的验收条件）**：
  `smoke/_toolchain_guards.py` §7「离线完备性」在镜像构建期断言
  ① `builder/pyproject.toml` `[project].dependencies` 声明的运行时依赖
  全部已在 base env 安装（**单一事实源**，不在守卫里另立清单；用发行版
  元数据判定而非 dist→import 名映射）；② 打包工具链
  （nuitka/scikit-build-core/build/wheel/invoke/ipykernel）已装；
  ③ gcc/g++/ccache/cmake/ninja/make/patchelf/readelf 在脚本实际建立的
  PATH 上可解析。PATH 探测必须**显式构造**
  `/opt/conda/bin:/opt/conda/envs/main/bin:$PATH`，不得依赖调用者继承的
  PATH（该脚本在 root 与 devuser 两身份各跑一次，须给出一致结论）。
  守卫自身**禁止联网、禁止装包**——否则守卫成为新的离线缺口。
- **阶段二无联网点的证据（2026-09-17 逐行核查）**：`build-tvm.sh`
  （`invoke config` + cmake + ninja + gcc，全本地；唯一外部前提是源码树
  自带的 3rdparty 子模块，须在联网侧检出）、`build-wheel.sh`
  （`python -m build --no-isolation`，Nuitka 下载旗标置空）、
  `verify-wheel.sh`（`venv --system-site-packages` 用 bundled ensurepip +
  本地 whl `--no-deps` 安装 + 不升级 pip）三者均无对外请求。新增或修改任一
  阶段二脚本时若引入联网点（`pip download` / `--find-links` / `uv` /
  `FetchContent` / `--assume-yes-for-downloads` / 依赖解析），必须同步本节
  并说明阶段一如何覆盖该依赖。
- **能力边界（不可越界承诺）**：离线只覆盖「运行 + 容器内编译/打包」，
  **不覆盖从零构建镜像**（构建期 apt / mamba / pip 三段均需联网）。无网
  机器必须通过镜像归档获得镜像，任何试图让 `xmnn.build` 在离线可用的
  改动都属于越界，应走独立规格。
- **单一事实源 `XMNN_OFFLINE`**（`0`/`1`，默认 `0`）：栈侧经
  `StackSpec.supports_offline=True` 声明后由内核 `resolve_offline()` 解析
  （显式开 > 显式关 > `.env` > 默认，复用 `_resolve_bool` 三态语义）。
  ⚠️ **必须解析后立即回写 `os.environ[XMNN_OFFLINE]`，且必须发生在
  `gates()` 之前**：WSL 桥接只透传 `bridge_env_keys` 中列出的环境变量、
  **不转发 CLI 参数**，`--offline` 若不固化进环境就会在桥接后丢失。
  `.env` 键不写入 compose `environment` 段（保住 `test_compose_merge.py`
  黄金快照），容器内由 `offline_exec_env()` 以 `exec -e` 单点注入。
- **`up` 恒 `--no-build`（C16，2026-09-18 修订）**：podman-compose 的 `up`
  默认对含 build 段的服务执行构建，故 `compose_up_tail()` **无参无分支**恒返回
  `["up","-d","--no-build"]`——离线与在线同构（此前 `offline=True` 才追加，属
  C15 阶段的临时分叉，已随 C16 消除）。镜像存在性只由内核 `build_image()` 负责，
  compose 的 `build:` 段仅服务裸 `podman-compose` 路径。因此离线**只需**强制
  `skip_build=True`（`resolve_offline()` 结果）即可禁网，不再依赖额外的 `--no-build`
  开关；镜像缺失时 `_require_local_image(offline=True)` fail-fast Exit(1)，指引
  `xmnn.save` / `xmnn.load`。
- **`save`/`load` 沿用既有镜像缓存约定**：tar.gz + 时间戳命名 + `latest`
  软链 + manifest/SHA256 校验（`default_build_cache_dir` /
  `find_latest_image_tar` / `validate_manifest_integrity`），不新造归档
  格式；`load` 必须先校验 manifest 再导入（拷贝损坏在 load 步暴露）。
  归档名另携带 **torch 形态**中缀（`-torch-<形态>-`），见 §11.5（C20）。
- **容器内打包禁网 = 硬失败而非降级**：`build-wheel.sh` 读同一
  `XMNN_OFFLINE`，三处行为——① numpy/scipy 导入失败时不再 pip 兜底而是
  `exit 2`；② Nuitka 的 `--assume-yes-for-downloads` 改由 `$NUITKA_DL_FLAG`
  承载（离线为空值，unquoted 展开整体消失）；③ pip 镜像 `case` 整体跳过，
  且缺系统 gcc（VTA FSIM 的 VLA 依赖）前置断言 `exit 2`。
- **测试锁行为**：离线语义在 `tests/test_overlay_core.py` 有 10 个用例
  （声明范围 / 环境回写 / `--no-build` / `exec -e` / `build` 首行 fail-fast
  且 `runner.commands == []` / 缺镜像 Exit / `up` 任务体参数存活 /
  `save`·`load` 仅离线栈生成），改动离线路径必须同步这组断言。

## 11. 可选能力 opt-in（GPU / torch，2026-09-20 / C18·C19·C20）

**总原则**：两项能力**默认全关**，不开时镜像体积、设备面与离线契约与改造前
逐字等价（`up` 不加载 GPU 覆盖文件、`TORCH_FLAVOR` 为空不装 torch）。

### 11.1 GPU 透传（`up --gpu`）

- 形态与 quant 栈一致：仅当 `--gpu` 时追加 `-f <覆盖文件>`（list 追加
  语义只写**新增**设备，不重复 `/dev/fuse`，见 [quant-overlay.md](quant-overlay.md) §4.1）。
- **设备项只写一条** `${GPU_DEVICE:-/dev/dri}` 单 token 插值，**禁止**写成
  `a:b` 并列两条：podman-compose 1.6.0 把 devices 列表项**原样**下传为
  `--device <item>`（vendor `podman_compose.py` L1382-L1383，不做冒号拆分），
  两条并列时 CDI 形态必有一条非法。
- `GPU_DEVICE` 双形态（与根 `invoke run --gpu` 同键同语义）：
  ① `/` 开头 → 宿主机设备路径；② 其他 → CDI 引用（如 `nvidia.com/gpu=all`，
  宿主先 `nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml`）；
  ③ **未设/空 → 自动探测**（不再是「默认 `/dev/dri`」，见下条）。
- `GPU_DEVICE` 已列入 `bridge_env_keys`——WSL 桥接只透传环境变量、不转发
  CLI 参数，遗漏会导致桥接后回退自动探测。
- **GPU 是运行期维度，禁止引入 `build --gpu`**（2026-09-20 定调）：透传只改
  compose 文件集（`--device` + 只读库 bind），**不改镜像内容**，构建期没有
  GPU 相关对象可操作；镜像内唯一与 GPU 相关的差异是 torch 形态，已由
  §11.2 `build --torch` 承担。两维度正交，故 `up --gpu` 与 `--offline`
  可自由组合——**`invoke xmnn.up --gpu --offline` 必须可用**（离线只禁构建：
  `offline → skip_build` + 本地镜像存在性预检，与设备探测零耦合；2026-09-20
  真机实测通过，容器零重建）。任何把 GPU 判定挪进构建期、或让离线分支拒绝
  `--gpu` 的改动都属回归。

#### 11.1.1 运行期可用性门禁与自动探测（C19，2026-09-20）

**背景**（W-I16 实测）：缺省 `GPU_DEVICE=/dev/dri` 在 WSL2 宿主**不存在**
（`podman-machine-default` 只有 `/dev/dxg`），改造前的 `--gpu` 无任何预检，
直接透传给 podman → `Error: stat /dev/dri: no such file or directory`，
`podman-compose up` exit 125。故 **opt-in 能力必须自带运行期可用性门禁**。

- 内核 `resolve_gpu_device(c, spec, env) -> (token, form)` 是唯一解析入口，
  在 `up_stack()`/`smoke_stack()` 中 `gpu=True` 时才调用，返回的 `form`
  决定覆盖文件（`gpu_override_file(spec, form)`）：
  | `form` | 覆盖文件 | 触发条件 |
  |---|---|---|
  | `generic` | `compose.gpu.yaml` | `/dev/dri` 等 PCI 设备或 CDI 引用 |
  | `wsl` | `compose.gpu.wsl.yaml`（存在时；否则回退 generic） | `/dev/dxg` |
- **三态语义**：① 显式设备路径（`/` 开头）→ 经 `test -e` 校验存在性，缺失
  fail-fast；② 显式 CDI 引用 → 校验 `/etc/cdi/*.yaml` 或 `/var/run/cdi/*.yaml`
  已生成；③ 未设/空 → 按 `GPU_DEVICE_FORMS`（`/dev/dri` → `/dev/dxg`）
  **顺序探测**，取首个存在者并**回写 `os.environ`**（`GPU_DEVICE`），
  使 compose 插值与提示文案同源。
- `wsl` 形态额外校验 :data:`WSL_GPU_PATHS` **三条**路径
  （`/usr/lib/wsl/lib/libcuda.so.1` + `/usr/lib/wsl/lib/libdxcore.so` +
  `/usr/lib/wsl/drivers`）是否齐备，缺**任一**条即 fail-fast 并**逐条点名**缺失
  路径（驱动库在 `podman-machine-default` 内可见，实测见 11.1.2）；探测全失败时
  **fail-fast + 中文指引**，不再把非法路径丢给 podman 报 exit 125。
  **禁止退化为只校验 libcuda**：缺 `libdxcore.so` / `drivers` 时容器内
  `CDLL` 成功但 `cuInit()` 返 100，属于「门禁放行 + 运行时不可用」的假通过。
- **设备探测必须经 run_cmd 在 podman 宿主侧执行**（`test -e`），禁止在本机
  做 `Path.exists()`——Windows 原生编排时本机文件系统与 WSL 发行版不是同一
  视图（与 C-I3 的「不做本机存在性判断」同源）。
- **解析必须先于 `up_preflight`，且形态要喂给预检（C23，2026-09-20）**：
  `up_stack` 的调用顺序是 `resolve_gpu_device` → `up_preflight(gpu=…,
  gpu_form=…)` → `run_compose_up`。两条理由：① 预检的跨平面判据要把
  「本平面将下发的 `--file` 原文串」与运行容器标签比，而 `--gpu` 会多下发
  一个覆盖文件，故期望串必须由 `compose_config_files_label()`（与
  `compose_argv` 共用 `compose_files()`，唯一事实源）推出——写死单文件会让
  **每次** `--gpu` 都被判「另一控制平面创建」而强制优雅 down + recreate
  （实测复现，容器 Created 每次刷新）；② GPU 不可用时应当 fail-fast 于任何
  `down` **之前**，而不是先把用户正在用的栈拆掉再报错。不变量：`up --gpu`
  对**同样由 `--gpu` 创建**的栈必须零动作（幂等）；而 `up`（无 `--gpu`）或
  形态切换（generic↔wsl）对 `--gpu` 创建的栈**仍须**判分歧（compose 确会
  recreate），不得退化成前缀/子集匹配。

#### 11.1.2 WSL2 形态的驱动库挂载（两轮实测矩阵，2026-09-20）

`podman-machine-default`（WSL2 后端）内一次性容器实测，**分两轮**——第一轮判据
是「库能否加载」（`CDLL("libcuda.so.1")`），第二轮装 cu130 torch 复核时改用
「设备是否可见」（`cuInit()` / `torch.cuda.is_available()`）：

| 轮次 | 配置 | 结果 |
|---|---|---|
| 1 | 无任何设备/库 | 失败（库不存在） |
| 1 | 仅 `--device /dev/dxg` | 失败（缺 `libcuda.so.1`） |
| 1 | 仅设 `LD_LIBRARY_PATH=/usr/lib/wsl/lib` | 失败（容器内无该文件） |
| 1 | 挂整目录 `/usr/lib/wsl/lib:ro`（不设 `LD_LIBRARY_PATH`） | 失败（该目录未进容器内 ld 搜索路径） |
| 1 | `--device /dev/dxg` + **单文件挂载 libcuda** `/usr/lib/wsl/lib/libcuda.so.1:/usr/lib/libcuda.so.1:ro` | CDLL 成功 |
| 2 | 同上（仍缺 ②③） | **`cuInit()`=100 `CUDA_ERROR_NO_DEVICE`**、`torch.cuda.is_available()`=False |
| 2 | 上 + `--cap-add SYS_ADMIN` / `seccomp=unconfined` | 100（无效） |
| 2 | 上 + 单文件 `libdxcore.so`（仍缺 drivers 目录） | 100（仍 NO_DEVICE） |
| 2 | **`--device /dev/dxg` + 三条只读 bind（单文件 `libcuda.so.1` + 单文件 `libdxcore.so` + 目录 `/usr/lib/wsl/drivers`）** | **`cuInit()`=0、`cuDeviceGetCount()`=1、`torch.cuda.is_available()`=True** |
| 2 | `--privileged` + 挂整个 `/usr/lib/wsl` | 0 成功（**有效但非必要**） |

- 结论：`compose.gpu.wsl.yaml` = `devices: [/dev/dxg]` + **三条** bind
  `read_only: true`（`bind.create_host_path: false`）——三条**同为最小充分条件**，
  缺任一即 CUDA 不可用（缺 ① 是 CDLL 层失败，缺 ②③ 是 NO_DEVICE 层失败）。
  内核 :data:`WSL_GPU_PATHS` 与测试断言必须与三条一致，**不得只留 libcuda**。
- **`/dev/dxg` 只是半虚拟化通道**：设备节点本身不提供 CUDA 实现，libcuda 由
  WSL 宿主提供；「CDLL 成功」只证明库被找到，**不证明设备被枚举**——两轮判据
  的差异正是本形态最容易踩的假阳性（第一轮结论曾据此把单文件挂载写成充分条件）。
- **刻意不设 `LD_LIBRARY_PATH`**：该 compose 字段是 **mapping 替换**语义，
  一旦设 `/usr/lib/wsl/lib` 会冲掉栈原有的 TVM 库路径
  （`.../npu_tvm/build:.../vta:.../main/lib`）——三条 bind 的挂载点均落在
  基底默认搜索路径（`/usr/lib`、`/usr/lib/wsl/drivers`）上，无需改环境变量
  （实测容器内 `printenv LD_LIBRARY_PATH` 未被污染）。

### 11.2 torch 形态（`build --torch` / `TORCH_FLAVOR`）

- 取值是**白名单** `("", "cpu", "cu130")`（`overlay_core.TORCH_FLAVORS`），
  解析期非法值 `Exit(1)`：该值直接拼进 `download.pytorch.org/whl/<flavor>`
  索引 URL，构建期网络请求目标**不得由用户输入任意拼接**。
- 键遵循 C15：**无前缀** `.env` 键 `TORCH_FLAVOR`，与 `compose.yaml`
  `build.args` 的 `${TORCH_FLAVOR:-}` 同键；CLI `--torch` 只覆盖单次
  `build`（`up` 内联构建与 compose 段看不到旗标，跨三处一致必须写 `.env`）。
- 安装脚本 `builder/scripts/install-torch.sh`（Layer 2.5，位于 mamba 工具链
  层之后、`COPY builder` 之前）装 **base env `/opt/conda`**（cp314 GIL），
  依据 C13 双 ABI 不可互换；pin `torch==2.14.0`（`TORCH_VERSION`）。
  **cu130 是 2026-09-20 实测唯一与 CPU 侧同 pin 的 CUDA 索引**
  （cu129→2.13.0、cu128→2.11.0 会引入版本漂移，勿改用）。
- 形态落 `/opt/xmnn-torch-flavor`（空/cpu/cu130），由构建期守卫
  `_toolchain_guards.py` §8 断言「声明 vs 实物」：空→torch 必须缺席、
  cpu→已装且 `torch.version.cuda is None`、cu130→已装且非空。脚本缺失标记
  文件即判失败（Layer 2.5 未执行）。
- **flavor 不参与镜像 tag**（沿用 `XMNN_IMAGE_TAG`，一 tag 一形态）；
  换 flavor 后必须 `invoke xmnn.build` 重建，不能靠 `up` 增量刷新。
  由此产生的「同 tag 双形态归档不可辨识」盲区由 §11.5（C20）在归档层补齐。
- torch 属**可选依赖**，不写入 `builder/pyproject.toml`，故 §7 离线完备性
  守卫不受影响（空形态下镜像仍离线自足）；但 **cu130 形态的 CUDA 运行时
  依赖由 wheel 自带**，离线侧不额外补装。
- **cu130 形态同时提供 CUDA 编译器工具链（nvcc）**——「cu130 = CUDA 13 开发
  环境」的完整语义；安装脚本、三包同轨 pin、农场/wrapper 纪律与实测依据见
  §11.6（C25）。

### 11.3 内核形参面 = 能力并集

`make_stack_tasks()` 的 `up`/`smoke` 形参按**能力并集**生成（`gpu_override`、
`supports_offline` 四路正交 + 公共 `_up_impl`），**禁止 if/elif 互斥分支**：
xmnn 同时声明两能力后，互斥写法会让 `--offline`/`--no-offline` 被 gpu 分支
吃掉，静默破坏 §10 离线契约。`up_help` 的 GPU 提示文本按 `gpu_device_env`
动态生成（有该字段时提示双形态与自动探测顺序，无则提示硬编码 `/dev/dri`）。

### 11.4 测试锁行为（C19 / C23）

CUDA 设备解析在 `tests/test_overlay_core.py` 有 9 个用例（覆盖文件 form 分派
与回退、`/dev/dri` 自动探测、`/dev/dxg` 自动探测 + **三条宿主路径缺任一均
fail-fast**、无设备 fail-fast、显式路径缺失 fail-fast、CDI 未生成 fail-fast、
wsl form 贯通到 compose argv、quant 同路径、**不开 `--gpu` 绝不探测设备**）；
渲染侧在 `tests/test_compose_merge.py` 断言 `compose.gpu.wsl.yaml` 的
`devices: [/dev/dxg]` 与 **三条 bind（target 全集 + source 映射 + 逐条
`read_only`/`create_host_path: false`）**，以及 quant 的
`${GPU_DEVICE}` 双形态插值。改动 GPU 解析路径必须同步这两组断言；
`WSL_GPU_PATHS` 增删条目时，`compose.gpu.wsl.yaml`（两栈）、这两组断言与
本规则 §11.1.1/§11.1.2 必须同批更新，**禁止只改常量不改覆盖层**
（缺项会让门禁放行一个 `cuInit()=100` 的形态）。

C23 另加 6 例锁住「文件集同源 + 判据不对称性」：`compose_config_files_label`
的逗号约定（单文件 / `--gpu` 双文件）、**同源锁**（三组 `(gpu, form)` 下
`compose_argv` 的 `--file` 值拼接必须逐字等于 label 输出）、`up_preflight`
的三种平面关系（gpu 平面同集 → 零 down；非 gpu 平面对 gpu 栈 → 必须 down；
form 切换 → 必须 down），以及端到端 `up_stack(gpu=True)` 在 gpu 栈上幂等
（无 `down`、无「另一控制平面」提示）。改判据或改 `compose_files()` 必须
同步这组断言——**禁止**放宽为前缀/子集匹配来让用例变绿。

### 11.5 归档的 torch 形态身份（C20，2026-09-20）

**问题**：§11.2「flavor 不参与镜像 tag」+ §10「`load` 按 mtime 取最新归档」
两条正确规则叠加出一个盲区——cpu 与 cu130 两份镜像 **tag 相同**
（`localhost/xmnn-dev:latest`），若归档名也不带形态，则两者同族同名、共用
同一个 `-latest` 软链，离线机 `load` 会**静默导入错形态**，直到容器内
`torch.cuda` 为空才暴露。

- 形态的唯一事实源是镜像内 **LABEL `org.specweave.torch-flavor`**
  （构建期 build-arg 烘入，与 `/opt/xmnn-torch-flavor` 标记文件并列）。
  `save_image` 复用已有的 `image_inspect_info` 调用顺带取 LABEL，
  **签名不变**（不新增参数）。
- 归档名：`<safe_name>[-torch-<形态>]-<short_id12>-<YYYYMMDD-HHMMSS>.<ext>`，
  `-latest` 软链同 stem。**无形态时不加段**，命名与历史产物逐字一致。
- **形态段必须带 `-torch-` 标记中缀**：镜像 tag 自带 `-latest` 段，无标记的
  `-<形态>-` 会被反向正则左最早匹配成 `flavor=latest`（`...-xmnn-dev-latest-<shortid>-<ts>.tar.gz`）。
  `client_core.save_image` 的命名与 `utils.archive_flavor` 的解析**严格互逆**，
  改动其一必须同步另一处。
- `find_latest_image_tar(search_dir, flavor=None)`：`None` 不过滤（历史语义、
  零回归）、空串只取未标注形态、`"cu130"` 只取该形态；无匹配返回 `None`。
- `load` 的形态感知**仅当 `spec.torch_flavor` 为真**时生效（其余栈零影响）：
  ① 未给 `--path` + 期望形态非空 → 按形态过滤选档；② 过滤后无档 → `Exit(1)`
  （提示当前 `TORCH_FLAVOR`）；③ `--path` 点名的归档形态与期望不符 → `Exit(1)`
  （**校验先于导入**）；④ 归档未标注形态（C20 之前的旧产物）→ 打印提示但
  **不拦截**（不能因命名演进拒绝历史归档）。
- 期望形态解析序与 `torch_build_args` 一致：`os.environ["TORCH_FLAVOR"]` >
  `.env TORCH_FLAVOR` > `""`。
- manifest 段的 `TORCH_FLAVOR=<形态>` 是**冗余记账字段**（供人工核对），
  **不是 load 的判定依据**——`validate_manifest_integrity` 按 `## ` 分段解析，
  而 `_append_manifest` 写单 `#` 表头，实际只有一个块、字段会被后一段覆盖，
  只有最后一次 save 的产物能通过校验；故形态判定必须以**归档名**为准。
- **测试锁行为**：`tests/test_image_archive.py`（新增，13 例）覆盖
  `archive_flavor` 四态（含 `-latest` 不得冒充形态）、
  `find_latest_image_tar` 形态过滤/无匹配/跳过软链、`save_image` 命名与
  manifest（有形态 / 无形态零回归）、`_image_torch_flavor` 降级；
  `tests/test_overlay_core.py` 另有 5 例锁 `load` 选档与拦截语义。

### 11.6 CUDA 编译器工具链随 cu130 形态提供（C25，2026-09-20）

**背景（现场）**：`TORCH_FLAVOR=cu130` 真机上 `torch.cuda.is_available()` 为
True，但容器内 `nvcc -V` 报 `not found`。根因两层：① torch cu130 的依赖闭包
只含 CUDA **运行时/库**（`nvidia-cuda-runtime`/`nvrtc`/`cublas`… 以及
`Requires:` 为空的 `cuda-toolkit` **元包**），**不含编译器** `nvidia-cuda-nvcc`；
② 既有验收全在运行期层（`cuInit()` / `torch.cuda.is_available()` / `CDLL`），
§8 守卫只断言 torch 形状，**没有任何断言覆盖编译器层**——「运行时冒充工具链」
被静默放行。

- **归属裁决**：nvcc **并入 `TORCH_FLAVOR=cu130` 形态**（语义 = 「CUDA 13 开发
  环境」），**不新增独立构建开关**——独立开关会引入第三个「同 tag 不同内容」的
  形态维度，而复用 C20 归档身份需改动 save/load 命名契约，收益不抵复杂度。
  默认形态（`""`/`cpu`）**零 CUDA 编译器**，C18「默认全关 = 默认隔离」不变。
  旧 cu130 归档不含 nvcc（同一形态的版本演进，非 C20 类别的「互斥能力串档」），
  需要者须回有网侧重建并重新 `save`。
- **安装脚本** `builder/scripts/install-cuda-toolkit.sh`（**Layer 2.6，独立成层**
  ——改本层不触碰 Layer 2.5 的 ~2GB torch 层缓存），由 `TORCH_FLAVOR` 白名单
  路由（`""`/`cpu` 跳过、`cu130` 安装、非法值 Exit 1）；pip 索引走 `PIP_MIRROR`
  三档映射（C15 同键）。
- **三包必须同轨**：`nvidia-cuda-nvcc` + `nvidia-cuda-crt` + `nvidia-nvvm` 同一
  pin（当前 `13.4.92`）。混版实测症状：cicc（nvvm 13.4）产 PTX `.version 9.4`、
  ptxas（nvcc 13.0）只认 9.0 → `ptxas fatal: Unsupported .version 9.4`。
- **为何 pin 13.4.92 而非与 torch 运行时同轨的 13.0.x**：基座 Ubuntu 26.04 /
  glibc 2.43 下 CUDA 13.0 的 `crt/math_functions.h` 与 glibc `mathcalls.h` 的
  `rsqrt` noexcept 规格冲突（`-std=c++14/17/20` 三档均复现），13.4.92 实测通过
  ——编译器线高于运行时线是**基座约束**；torch 的 CUDA 运行时仍由 cu130 wheel
  自带，不受影响。
- **`/usr/local/cuda` 农场 + wrapper 纪律（禁裸软链）**：pip 布局在
  `site-packages/nvidia/cu13/{bin,nvvm}`，**无 lib64、无 `libcudart.so` 短名**，
  且 nvcc **以 argv[0] 所在目录定位自身根**（`bin/..//include`）：
  ① 裸软链 `/usr/local/bin/nvcc → 真身` 是**假通过**——`_HERE_` 落
  `/usr/local/bin`，报 `cuda_runtime.h: No such file`（实测），**禁止**；
  ② 农场 `/usr/local/cuda/{bin,include,lib64,nvvm}` 软链 pip 实体，并为
  `cu13/lib/lib*.so.<ver>` 补短名（缺短名时 `-lcudart` 报
  `cannot find -lcudart`，实测）；
  ③ PATH 上的 `/usr/local/bin/nvcc` 是**唯一入口**（包装器 exec 农场全路径）。
  运行期 pip 升级单个 CUDA 组件会丢短名软链 → **禁止**，须回有网侧重打镜像
  （与 §10 无网侧不得补装同源）。
- **CUDA_HOME**：Containerfile 末尾 `ENV CUDA_HOME=/usr/local/cuda`（置文件末尾
  以免使既有层缓存失效）；无它则 `which nvcc` 推出 `/usr/local`（wrapper 所在
  目录）而非农场根，torch 扩展编译头文件解析错误。
- **动态链接器登记（`/etc/ld.so.conf.d/10-xmnn-cuda.conf` + `ldconfig`）**：
  真实 toolkit 安装器同款做法。缺这一步时**编译/链接都过、运行期才炸**——
  `libcudart.so.13: cannot open shared object file`（链接期有 nvcc 默认 `-L`，
  运行期 ld.so 不认识 `/usr/local/cuda/lib64`；2026-09-20 真机实测）。替代
  方案是让用户设 `LD_LIBRARY_PATH`，与本栈 C19 纪律（禁以 env 覆盖库路径）
  冲突，故必须在镜像层解决。
- **构建期守卫**：`smoke/_toolchain_guards.py` §9 四查——① 标记
  `/opt/xmnn-cuda-nvcc-version` 与 `nvcc --version` 实测版本一致；② 农场布局
  齐备（`bin/nvcc`、`include/cuda_runtime.h`、`lib64/libcudart.so`、
  `nvvm/libdevice`）；③ `ldconfig -p` 已登记 `libcudart`（产物可运行）；
  ④ **真编译 + 真链接**最小 `.cu`（`-c` 与 `-lcudart` 双段，**不运行**——构建
  期无 GPU 设备属预期边界）。非 cu130 形态反向断言 nvcc 与标记双双缺席。
  「nvcc 存在」不是充分条件——头文件冲突、三包错版与链接器登记缺失都只在
  编译/运行期暴露。
- **默认 `-arch` 边界（2026-09-20 实测）**：nvcc 缺省 arch（sm_75）产物在新架构
  GPU（本机 RTX 5050 Laptop = cc 12.0/sm_120）上**能编能链、启动期报**
  `the provided PTX was compiled with an unsupported toolchain`——根因是 nvcc 13.4
  产出的 PTX 版本高于宿主驱动线（本机 WSL 驱动 580.102 ≈ CUDA 13.0 代）所支持的
  版本，属**工具链/驱动版本差**而非镜像缺陷；`-arch=native` 与 `-arch=sm_120`
  两条路径均真机实测通过（`result=42`；device 枚举/拷贝/同步本已正常，失败只在
  JIT 发射一跳）。**镜像刻意不预设 arch**：`-arch=native` 需编译期可见设备
  （构建期无 GPU），预设还会把产物绑死构建机。文档层（README/排障）必须给
  `-arch=native` 指引，镜像层不得注入默认值；torch 扩展编译走 torch 自身 arch
  检测（`TORCH_CUDA_ARCH_LIST`）不受影响。
- **边界**：`nvidia-smi` 属运行期 WSL 形态（宿主 `/usr/lib/wsl/lib/nvidia-smi`
  还需 `libnvidia-ml` 等依赖），**不在本条款范围**；容器内编译产物能否运行仍
  取决于 `up --gpu` 的设备透传（C19）。

