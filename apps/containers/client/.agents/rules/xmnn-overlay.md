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
- 8 个任务：`build / up / down / ps / logs / smoke / build-tvm / wheel`。
  `build-tvm` 与 `wheel` 是对运行中容器的 `podman-compose exec` 长任务。

## 2. 平台门禁（硬约束）

与 quant 栈完全同族：
1. Windows 原生 CPython 一律 `_gate_platform()` Exit(1)（双路径中文指引：
   WSL2 发行版 / `invoke env.run-cmd`）；
2. POSIX 缺 podman-compose 二进制 `_gate_compose_binary()` Exit(1)，
   提示 `pip install -e ".[compose]"`（复用既有 optional extra，不新增依赖）；
3. 顺序固定：先平台后二进制；build/up/smoke/build-tvm/wheel 另过 daemon 预检。

## 3. 双 ABI 工具链契约（不可互换）

| 角色 | env | Python | 内容 |
|---|---|---|---|
| Jupyter 服务 | `/opt/conda/envs/main` | 3.14.x **cp314t**（GIL off） | 基底 jupyterlab（supervisord，devuser） |
| 编译/打包/内核 | `/opt/conda`（base） | 3.14.x **cp314 GIL enabled** | nuitka==4.1.3、scikit-build-core、build、invoke、ipykernel、wheel 19 依赖 |
| 原生工具链 | main env | — | llvmdev/clangdev/clang/lld **22.1.8**、cmake、ninja、make、ccache、libgcc、libstdcxx-ng |

- **Nuitka 4.1.3 在 cp314t 编译失败、cp314 GIL 成功**（allocator.h:606
  Spike 结论）：所有打包/验证脚本的解释器固定 `/opt/conda/bin/python`；
  工具链 bin 用绝对路径（CC/CXX/LLVM_CONFIG 指向 main env），跨 env
  PATH/LD_LIBRARY_PATH 导出只在脚本进程内生效，不反转全局 PATH。
- conda 装工具链必须 pin `python=*=*cp314t`，构建期
  `_toolchain_guards.py` 对双 ABI 做双向断言（main 被求解互换即构建失败）。
- 系统层仅 apt 装 patchelf（CMake RPATH 阶段）与 gdb（调试诉求）。

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
- verify-wheel.sh 在 `--system-site-packages` 临时 venv 内装 wheel 跑
  10 项检查，结束删除 venv——base env 的源码调试链路零污染。

## 6. compose ↔ rootless 三必需 / bridge / 环境注入

- 三必需只用标准字段：`devices: [/dev/fuse:/dev/fuse]`、
  `security_opt: [label=disable]`、`cgroupns: host`（1.6.0 空操作须注释
  声明）；严禁 privileged、docker.sock、host 网络。
- `network_mode: bridge` 是**带证据的偏差**：2026-09-14 同机实证 machine
  无 systemd user bus 时默认项目网络 aardvark-dns 必失败；注释必须保留
  该实证，不得擅自删改。
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
