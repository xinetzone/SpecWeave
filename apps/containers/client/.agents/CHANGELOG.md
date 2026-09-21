# jupyter-podman-client 变更日志（原子提交汇总）

> 本文件只记录消费端特有改动；SpecWeave 工作区根级、apps/containers 组级、构建端（jupyter-podman-rootless）的改动
> 不在本文件范围内。按七概念方法论每次 C（原子提交）阶段完成后追加一条；每条必须：
> ①可追溯（对应根工作区 git commit hash）②关联七概念场景（里程碑复盘/问题解决/重构优化/知识沉淀/创新突破）③说明验收点

## [Unreleased]

### 2026-09-21 · `fix:` 打包期源码树全程只读——AST 兼容层由构建期注入改为运行期补丁（C31）

**关联七概念场景**：场景2「问题解决」（I→F→V→C，V 门强制）——修复
`invoke xmnn.wheel` 的**不可自愈停机**，并按用户指定方向（借鉴
`xmnn/vta_compat.py` 的运行期补丁范式）**彻底不再修改 tvm 源码**。

**I 事实**：

① 故障现场：`build-wheel.sh` 以 `exit code: 2, line: 192` 中止，报
`[FATAL] /workspace/npu_tvm/python/tvm/__init__.py 已含 AST PREAMBLE 但备份
/workspace/npu_tvm/python/tvm/__init__.py.bak_tvm 缺失`；② 精确产生点：
`lib/ast_inject.sh` 的「marker 在 + 无 bak」分支 `return 2`——该分支在安全模型上
**不可判定**（既不能确定注入内容是脏的、也不能确定原始内容），只能人工
`git checkout` 才能继续；③ 成因是上一次构建被 SIGKILL/OOM 中断，EXIT trap
（`_restore_all`）未及执行，`tvm/__init__.py` 停在「注入态」而备份已丢；
④ 该注入自始（`67812663d`，2026-09-14）与 `_xmnn_bootstrap.py` 的 `.pth`
启动钩子**双机制冗余**——后者第 66-100 行的 ast 补丁与注入块逐字等价，
且在**解释器启动时**执行，早于任何 tvm import；⑤ tvm/vta/xmnn 源码对已移除
的 ast 遗留节点**零硬依赖**（全部 `getattr(ast,"X",None)` 防御式写法或版本守卫）；
⑥ Nuitka 编译**不执行**被编译模块、builder 的 CMake **不 import tvm**，且
构建期 `/opt/conda` site-packages 内**不存在** `xmnn_bootstrap.pth`——即构建期
本就不需要该补丁。

**F/V 决策**（V 对抗审查：注入是否真是构建期刚需、移除后是否复现原故障、
运行期补丁能否覆盖 wheel 安装态）：

- **路径 A（构建期改写外部源码树）被否决**：只要写外部源码树，就必然产生
  「注入态」这一**非法中间态**，SIGKILL/OOM 下不可恢复；四态自愈矩阵中
  「marker 在 + 无 bak」是不可判定分支，故障是设计使然而非偶然；
- **路径 B（运行期 monkey-patch）被采纳**：源码树只读、幂等、无残留态，
  与 `vta_compat.py` 既有 `apply_*_fix()` 范式同构；
- **范围（用户已确认）**：三包（tvm/vta/xmnn）注入全移除，ast 兼容**收敛到
  运行期补丁**，彻底消除「注入态残留」这一类故障（含 vta/xmnn 并行编译期
  OOM 场景）。

**E/C 落地**：

- `xmnn/vta_compat.py` 新增幂等 `apply_ast_compat()`（补齐 NameConstant/Num/
  Str/Bytes/Index/ExtSlice 为 `ast.Constant` 子类/`ast.expr` 兜底，`_applied`
  增 `"ast"` 位），`apply_all()` 首行调用；`compile_api.from_frontend()`
  （compile 与 accuracy 共用入口）在模型加载前显式 `apply_ast_compat()`。
- `build-wheel.sh`：移除三处 `ast_inject`/`ast_restore`、`AST_PYTHON`、
  `source lib/ast_inject.sh`、`_restore_all` + `trap … EXIT`、帮助第 6 条
  （「已含 AST PREAMBLE 但备份缺失」，原 7/8 条重编号），头注流程改为
  「源码树全程只读」。
- 删除死代码 `lib/ast_inject.sh` 与 `tests/test_ast_inject.py`（10 例全部
  针对已删除的注入状态机）。
- 闭环文档：`.agents/rules/xmnn-overlay.md` §5（「AST 注入/还原纪律」整段
  改写为「源码树只读纪律」，资产清单去掉 `ast_inject.sh`）、`AGENTS.md` C12、
  `docs/11-xmnn-overlay.md`、`overlays/xmnn-dev/README.md` 排障行、
  `.dockerignore`（去 `*.bak_*`/`*.tmp.*`）、`.agents/rules/invoke-tasks.md`
  （测试现状）。

**V 验收**（全部真机实测）：

- **构建跑通**：容器内 `build-wheel.sh` **exit 0**，产出
  `xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`（170M），全日志
  **零 `[FATAL]`、零 `[INJECT]/[RESTORE]`**——证明构建期注入确为冗余；
- **隔离验证**：`verify-wheel.sh` **10 passed / 0 failed**（含 test 8
  `.pth` bootstrap 存在性）；
- **源码树零改动（AC-9）**：构建前后三包 `__init__.py` md5 逐字一致
  （tvm `c3da634afaba00e2132cc5f28b6fee2f`、vta `1ab236cb422783328ef873ba14a2d90f`、
  xmnn `6c958e99f132242be30168d15ba6f154`），`git status` 干净，
  无 `.bak_*` / `*.tmp.*` 残留；
- **运行期补丁覆盖 wheel 安装态**：`--system-site-packages` venv 装 wheel 后，
  新解释器启动即由 `.pth` 完成补丁——六个 ast 遗留节点齐备、
  `_xmnn_bootstrap` 在 `sys.modules`、`import tvm` 成功；
- **补丁自身**：`apply_ast_compat()` 幂等复调无副作用；六节点功能断言
  （`Num(3).value==3` 且 `isinstance(…, ast.Constant)`、`Str/Bytes/NameConstant/
  Index/ExtSlice` 构造正确）通过；
- **单测**：`pytest tests -q` **263 passed / 7 skipped / 1 failed**，唯一失败
  `test_compose_merge.py::test_vs_real_rec_merge_probes`（真实 podman-compose
  1.6.0 `rec_merge` 对 `depends_on` list↔dict 抛 ValueError）为**既有失败**，
  与本次改动无关（未触碰 `overlay_core.py` 与 `test_compose_merge.py`）。

提交 `fix(client)` = `5d1db8f31`；配套 `npuusertools` 仓 `fix(xmnn)` = `f1e53c0`。

### 2026-09-21 · `feat:` 形态感知镜像 tag——`localhost/xmnn-runtime:<形态>` + `:latest` 别名（C28）

**关联七概念场景**：场景3「重构优化」——把 C26（`--torch cpu|cu130`）与 C27
（up 侧形态校验）留下的**身份缺口**从「事后告警」前移到「标签即内容」。
用户已确认设计：**默认 tag 改为形态感知 + 同时保留 `:latest` 别名**（同镜像
双 `-t`，零额外存储）。

**I 事实**：

① C26 原文「一 tag 一形态」的实伤——CPU 与 cu130 镜像**标签相同而内容不同**
（`localhost/xmnn-runtime:latest`），`up --skip-build` 只查 tag 存在性，切形态
全靠人记得重建；② C27 的 up 侧校验是**不阻断告警**，且拦的是「已跑错」的
事后时刻；③ `:latest` 有 **24 处引用**，其中 `relpack._PACK_SCRIPT` 第 163 行
**硬编码** `SRC="localhost/xmnn-runtime:latest"`（客户交付包入口）——这决定了
`latest` 不能删；④ `image_tag()` 与 compose `${XMNNRT_IMAGE_TAG:-默认}` 必须
同键同默认（C16），故 compose 侧要能算出同一串。

**F/V 决策**（V 对抗审查：显式覆盖 vs 形态感知的优先序、`:latest` 是否该保留、
是否自动改挂旧镜像）：

- **保留 `:latest` 别名**（否则 relpack/README 的 24 处引用集体悬空）；
- **显式 `{PREFIX}_IMAGE_TAG` 最高优先**（用户接管命名时形态感知让位，且
  **不追加**别名）；**显式 `--tag`** 同理不追加；
- **不自动改挂**旧镜像：通用标签可能指向另一形态，改挂与否由用户判断——
  内核只打印 LABEL 形态 + `podman tag` 命令（零成本，避免重下数 GB）。

**E/C 落地**：

- 内核 `StackSpec` 新增 `flavor_tag` 声明位（默认 `""`，非声明栈零回归）；
  `image_tag()` 解析序改为「显式覆盖 > 形态感知 > 默认 tag」，形态经新
  `image_flavor()` 复用 `resolve_build_args`——**CLI `--torch` 单次覆盖也改变
  标签**（杜绝「装 cu130、标 cpu」）；新增 `image_tag_alias()` 判定别名下发；
  `build_image()` 双 `-t` + 构建完成横幅打印别名。
- `xmnnrt.py` 声明 `flavor_tag="localhost/xmnn-runtime"`（**唯一**声明栈）；
  `compose.yaml` 的 `image:` 改嵌套插值
  `${XMNNRT_IMAGE_TAG:-localhost/xmnn-runtime:${TORCH_FLAVOR:-cpu}}`。
- `_require_local_image()` 增**迁移提示**：形态 tag 缺失而通用 tag 在本地时
  打印 LABEL 形态 + 零成本改挂命令。
- 单测：`test_compose_merge.py` 的模拟器补**嵌套插值**（原 `[^}]*` 正则会在
  首个 `}` 截断）+ GOLDEN 改 `:cpu` + 四态用例；`test_overlay_core.py` 新增
  5 例（四态 / CLI 覆盖驱动 tag / 非声明栈零回归 / 别名 gating / 迁移提示）。

**V 验收**：全量 `pytest tests -q --ignore=tests/test_ast_inject.py`
**256 passed / 2 skipped**（较基线 +7，零回归）；`xmnnrt.py` 仍 ≤160 行
（模块预算守卫 `test_modules_bounded_and_declarative` 通过）。

**真机核对**（不改镜像/容器状态）：真实 podman-compose 1.6.0 渲染仓库内
`compose.yaml` 四态全部正确；本地既有 cu130 镜像零成本改挂到 `:cu130`
（同镜像 ID、零额外存储）后 LABEL 形态与 `.env` 一致。**未做**：端到端
`invoke xmnnrt.up --skip-build` 重建容器复核（当时栈在运行，避免中断）。

提交 `feat(client)` = `8ffd3a0f1`。

### 2026-09-21 · `fix:` 补上「声明形态 vs 镜像实物」的跨层校验（C27）

**关联七概念场景**：场景2「问题解决」——用户质疑前一轮给出的两个「坑」，
按 F→V→C→R→I→E 链路核验，结果**一个成立、一个被实测推翻**。

**F/I 根因**（9 轮真机探针 + 代码路径复核）：

① 坑①「tag 覆盖」成立，但定性需修正——`.env TORCH_FLAVOR=cu130` 是**刻意
设置**（注释块指向 xmnn-dev 的 nvcc，实测 xmnn-dev 已装 cu130 torch +
`/usr/local/bin/nvcc`），两栈诉求恰好一致，状态自洽；真正的问题是**共享键
使两栈无法独立取值**（C15 明文设计）。

② 坑②「`podman run --rm` 失败影响 standalone 冒烟」**被推翻**：基底镜像
`ManifestType=docker.v2`（带 HEALTHCHECK，`Containerfile:859`），而叠加镜像
全是 **OCI v1——OCI 格式忽略 HEALTHCHECK 指令**，故 xmnn-dev / xmnn-runtime
均无 healthcheck，`podman run --rm` 实测 `rc=0`。四栈 standalone 冒烟路径
**完全不受影响**；`invoke run` 用的 `jupyter-podman-client` 同为 OCI。
该坑的表述在 rules/README 中一并修正，并记下「依赖 OCI 忽略 HEALTHCHECK」
这一**隐式行为**（若 podman 改默认格式，四栈会集体失效）。

③ **核验中发现真实缺口**（比原 #1 更实在）：`--torch` 是**单次** CLI 覆盖
（C15），只作用于 `build`；`up` 形参面没有 `--torch`，且 `_require_local_image`
比的是 **tag 不是内容** → `build --torch cpu` 后 `up --skip-build` 会**静默**跑
cpu 镜像（`.env` 声明 cu130）。构建期守卫第 10 项比的是「镜像内 marker vs
镜像内实物」，两者一致必然 PASS——偏差在**跨层**，镜像内部自洽检测永远
发现不了。

**E/C 落地**（用户决策：加 up 侧校验 + 保持共享键）：

- 内核新增 `image_torch_flavor(c, tag) -> Optional[str]`：**区分「无 LABEL」
  与「LABEL 为空串」**——后者是合法声明（`TORCH_FLAVOR=""` = 不装 torch），
  前者是无法判定（旧镜像）。**不复用** `client_core._image_torch_flavor`
  （把两者都归空串，照搬会把旧 CPU 镜像误报成「声明空、实物 cpu」）。
- 内核新增 `warn_torch_flavor_mismatch(c, spec, env)`，在 `up_stack` 内、
  镜像存在性预检之后调用；仅 `torch_flavor` 栈生效（quant/monetize 零探测）。
  不符则打印「声明 / 镜像实际 / 修复命令」三行中文指引，**警告不阻断**
  （同 C21 超时不判失败、C24 回读失败不阻断）。
- 查询走 `client_core.image_inspect_info`（原始 JSON，规避双 shell `--format`
  引号差异）；镜像不存在/解析失败降级为「不判定」，不抛异常。
- 测试按既有约定在 **`oc` 命名空间**打桩该符号（同 `load_image`）——**不**
  patch `client_core.run_cmd`：内核自己的 I/O 缝是 `oc.run_cmd`，跨模块旁路
  会同时破坏两条约定（首版实现踩到，已改正）。

**V 验收**（真机 + 单测）：

- 真机 `image_torch_flavor` 五例零误报：`xmnn-runtime:latest`→`cu130`、
  `xmnn-dev:latest`→`cu130`、`xmnn-runtime:1.2.1.dev0`（旧 CPU）→`None`、
  基底镜像→`None`、不存在→`None`；
- 新增 5 例单测（不符报警 / 一致静默 / 旧镜像无 LABEL 不误报 / 非 torch 栈
  零探测 / 「空串声明 vs 无 LABEL」分流正反两向）；
- 全量 `pytest tests -q --ignore=tests/test_ast_inject.py` **249 passed /
  2 skipped**（较前基线 +5，零回归）。

**后续（同日已补）**：镜像形态感知 tag 已由 **C28** 落地（`localhost/xmnn-runtime:<形态>`
+ `:latest` 别名，见上方条目 `8ffd3a0f1`）——本条的 up 侧校验自此退为**兜底**，
专管身份被用户接管的场景；共享键 `TORCH_FLAVOR` 仍按本条决策保持 C15 不动
（若未来两栈需分叉，走「栈专属覆盖键优先、回落共享键」的受控扩展，嵌套插值
`${XMNNRT_TORCH_FLAVOR:-${TORCH_FLAVOR:-cpu}}` 已实测可行）。

提交 `fix(client)` = `833828321`。

### 2026-09-20 · `feat:` xmnnrt 支持 GPU——`up --gpu` 设备透传 + `build --torch cpu|cu130`（C26）

**关联七概念场景**：场景5「创新突破」——承接同日 xmnn-dev 的 GPU/torch 能力
（C18/C19/C25），把同一能力面推广到**交付运行时**栈，并按本栈「干净运行时」
定位收窄边界。

**I 事实**：
① 内核（`resolve_gpu_device` 三态探测 + `gpu_override_file` 形态分派 +
C23 文件集判据）**已完整具备** GPU 能力，`xmnnrt` 只是未声明
`gpu_override` 与缺两个覆盖文件、`up` 形参面少一个 `gpu`；
② torch 层此前把 CPU 形态**硬编码**在 Containerfile（`TORCH_INDEX_URL` 固定
CPU 索引 + 守卫写死 `cuda is None`），故 cu130 会同时在**安装索引**与
**构建期守卫**两处卡死；
③ **同一 `TORCH_FLAVOR` 键在两栈语义不同**——xmnn-dev「空=不装」、
xmnn-runtime「空=回落 cpu（内置契约）」，故缺省值不能在内核硬编码。

**E 方案**（三点，均按「声明优先、单一事实源」落）：
① **内核**：`StackSpec` 新增 `torch_default`（缺省形态声明位），
`resolve_build_args` 回落改为 `spec.torch_default`（xmnn 仍 `""`，行为零变化）；
`_build_help` 公开为 `build_help` 并按缺省分派文案，消除 xmnnrt 侧的 help 复制。
② **xmnnrt 声明**：`gpu_override=True` + `gpu_device_env="GPU_DEVICE"` +
`torch_flavor=True` + `torch_default="cpu"`；自定义 `build`/`up` 薄封装各加
一个形参（`torch`/`gpu`）后原样透传内核——**禁止**在栈模块重复实现分派；
新增 `compose.gpu.yaml`（`${GPU_DEVICE:-/dev/dri}` 单 token）与
`compose.gpu.wsl.yaml`（`/dev/dxg` + libcuda/libdxcore/drivers 三条只读 bind），
compose 段补 `${TORCH_FLAVOR:-cpu}`（与 `spec.torch_default` 同键同默认，C15）。
③ **镜像**：Layer 1 抽出 `scripts/install-torch.sh`（**独立成层**、索引由白名单
形态推导，删掉独立 `TORCH_INDEX_URL` ARG）；守卫第 10 项改为**声明 vs 实物**
（读容器内 `/opt/xmnnrt-torch-flavor` marker）；标签拆为
`torch-version` + `torch-flavor`（`relpack.py` 更新读取键并保留旧键回退，
`release.json` 字段与 schema 不变）。

**边界（刻意保留，非缺口）**：
- `cu130` **不提供 nvcc**——本栈 P0 禁编译器工具链（§4「运行时不含编译器/
  调试器」），CUDA 版 torch 足以跑 GPU 张量与 `torch.jit` 推理；需 nvcc 编译
  CUDA 内核 / TVM CUDA codegen 请回 xmnn-dev 栈（C25）；
- **零 env 改动**：本栈 compose 本就无 `environment` 段（交付语义=干净运行时），
  GPU 覆盖只加 `devices`（WSL 形态另加 `volumes`），WSL 库挂载靠目标取
  `/usr/lib`；任何 `LD_LIBRARY_PATH` 注入既污染交付语义又打挂 env 黄金集；
- 覆盖文件**不进 `release/` 客户离线交付包**（独立谱系，GPU 交付属后续提案）；
  本次仅触及 `relpack.py` 的标签读取键，交付物内容与字段未变。

**C 验收**（daemon-free 单测 + 真机渲染）：
- `pytest tests -q --ignore=tests/test_ast_inject.py` **244 passed / 2 skipped**；
- 新增/更新用例：`test_build_args_torch_default_is_per_spec`（两栈缺省分派）、
  `test_xmnnrt_build_task_torch_defaults_to_cpu` / `..._flows_cu130`（argv 实物）、
  `test_compose_torch_flavor_default_matches_spec`（C15 三处同键同默认，读真实
  compose.yaml）、`test_xmnnrt_gpu_override_is_opt_in_and_adds_no_env`、
  `test_up_gpu_wsl_form_for_xmnnrt_same_kernel_path`（薄封装是否吞参数）、
  WSL 渲染断言参数化扩到 xmnnrt；黄金清单同步（build 形参 +`torch`、
  up/smoke 形参 +`gpu`、smoke docstring 去「CPU」、`xmnnrt.py` 159 行 ≤160）；
- 真机 WSL `podman-compose config` 逐一核对：默认 `TORCH_FLAVOR=cpu`、
  `TORCH_FLAVOR=cu130` 正确插值、`-f compose.gpu.yaml` 追加 `/dev/dri`、
  `-f compose.gpu.wsl.yaml` 追加 `/dev/dxg` + 三条 bind，且**均未新增 env**；
- **未做**：cu130 镜像真机构建（需重下 CUDA torch，体积大）、GPU 设备透传真机
  E2E（需 `xmnnrt.build --torch cu130` 完成后执行 `up --gpu` 并在容器内验证
  `torch.cuda.is_available()`）；镜像构建属有网侧动作，留待用户按 README
  「GPU 用法」三步验收。

- 同步文档：[.agents/rules/xmnnrt-overlay.md](rules/xmnnrt-overlay.md)（§4/§6/新增
  §8）、[overlays/xmnn-runtime/README.md](../overlays/xmnn-runtime/README.md)
  （命令表/守卫 10 项/参数表/GPU 用法/torch 升级 SOP/排障四行）、
  [docs/13-xmnn-runtime-overlay.md](../docs/13-xmnn-runtime-overlay.md)、
  [.env.example](../.env.example)（两栈共用键的默认值差异警示）、
  overlay `.env.example`、[AGENTS.md](../AGENTS.md) C26 条款。
  提交 `feat(client)` = `9b6b0610f`。

### 2026-09-20 · `fix:` cu130 形态补齐 CUDA 编译器工具链——容器内 `nvcc` 从 not found 到可编译（C25）

**关联七概念场景**：场景2「问题解决」——现场症状驱动：JupyterLab 内
`!nvcc -V` 报 `nvcc: not found`，而同环境下 `torch.cuda.is_available()`
为 True（「GPU 可用但编不了 CUDA」的半形态）。

**I 事实**（真机 + 五轮一次性容器探针）：
① 容器内 `pip list` 有 `torch 2.14.0+cu130`、`cuda-toolkit 13.0.3.0`
（**元包，`Requires:` 为空**，仅由 torch 拉入）与 nvidia-* 运行期组件；
`site-packages/nvidia/cu13/` 只有 `{include,lib}`、**无 `bin`** → 无 nvcc；
② `nvidia-cuda-nvcc` 在 PyPI 有 13.0.48–13.4.92；**单独 pin 13.0.88** 安装时
`nvidia-nvvm`/`nvidia-cuda-crt` 被解析到 13.4.92 → **ptxas 与 cicc 错轨**，
编译报 `ptxas fatal: Unsupported .version 9.4; current version is '9.0'`；
③ 三包同 pin 13.0.88 后仍在**头文件层**失败：基座 Ubuntu 26.04 / glibc 2.43 的
`mathcalls.h` 与 CUDA 13.0 `crt/math_functions.h` 的 `rsqrt` noexcept 规格冲突
（`-std=c++14/17/20` 三档均复现）；**13.4.92 编译通过**；
④ 布局/调用三连：裸软链 `/usr/local/bin/nvcc → 真身` 报
`cuda_runtime.h: No such file`（nvcc 以 argv[0] 目录定位自身根）；`-lcudart`
报 `cannot find -lcudart`（pip 布局无短名，nvcc 默认只搜 lib64）；农场
`/usr/local/cuda/{bin,include,lib64,nvvm}` + 短名软链 + wrapper exec 全路径后
`nvcc -V`/编译/链接全通过；`CUDA_HOME=/usr/local/cuda` 被
`torch.utils.cpp_extension` 正确识别（`bin/nvcc`、`include/cuda_runtime.h`、
`lib64/libcudart.so` 三查为真）。
⑤ 真机运行期补刀（首轮镜像重建后）：`nvcc` 编译 + `-lcudart` 链接都成功，但
**运行**时 `libcudart.so.13: cannot open shared object file`——链接期有 nvcc
默认 `-L`、运行期 ld.so 不认识 `/usr/local/cuda/lib64`；真实 toolkit 安装器
靠 `/etc/ld.so.conf.d/*.conf` + `ldconfig` 解决（本修复初版遗漏，已补齐）。

**F 根因**：**能力声明粒度不足 + 验收判据错层**——cu130 形态只覆盖「CUDA
运行时（跑）」，编译器层（编）既无声明也无断言：依赖闭包（torch → 运行期
nvidia-* + 空元包）天然不含 `nvidia-cuda-nvcc`，而既有验收
（`cuInit()`/`torch.cuda.is_available()`/`CDLL`）与守卫 §8（torch 形状）
全部锚在运行期层 →「运行时冒充工具链」被静默放行。

**A 行动**：归属裁决——**并入 cu130 形态**（语义 = 「CUDA 13 开发环境」），
不新增独立构建开关（独立开关会引入第三个「同 tag 不同内容」的形态维度，
复刻 C20 归档盲区需改动 save/load 契约，收益不抵复杂度）。新增
`builder/scripts/install-cuda-toolkit.sh`（**Layer 2.6，独立成层**保住 torch
~2GB 层缓存；`""`/`cpu` 跳过 = C18 默认隔离不变；三包同轨 pin `13.4.92`；
`PIP_MIRROR` 三档索引；农场 + 短名 + wrapper + 标记
`/opt/xmnn-cuda-nvcc-version`）；Containerfile 末尾
`ENV CUDA_HOME=/usr/local/cuda`（置末尾以免使既有层缓存失效）。

**V 对抗审查**（四视角命中，采纳 ≥2 条已落盘）：
① 魔鬼代言人「并入 cu130 是形态语义漂移，且旧 cu130 归档与新归档将**同名不同
内容**」→ **采纳**：不新增归档身份维度（复刻 C20 盲区的前提是互斥能力，此处属
同一形态的版本演进），但在 C25/docs 明示「旧 cu130 归档不含 nvcc，需要者重建后
重新 `save`」；② 未来视角「pin 13.4 与 torch 13.0 不同轨会被后人误当笔误改回
13.0」→ **采纳**：脚本头注 + 规则 §11.6 + docs/11 三处写明「编译器线高于运行时
线是基座约束（glibc 2.43 与 CUDA 13.0 crt 头冲突，`-std` 三档无解）」并保留失败
证据摘要；③ 完整性攻击者「`nvcc --version` 能跑 ≠ 能编」→ **采纳**：守卫 §9 以
**真编译 + 真链接**最小 `.cu` 为判据（两个只在编译期暴露的失败模式：头规格冲突、
`ptxas`/`cicc` 错版）；④ 边界攻击者「运行期 pip 升级单包会静默丢短名软链」→
**采纳**：C25 ⑤ 明令禁止，须回有网侧重打镜像；⑤ 新人视角「用户不知道 nvcc 随
cu130 而来、也不知道 13.4 与 13.0 的关系」→ **采纳**：`.env`/`.env.example`/
README/docs 三处对齐；⑥ 老板视角「构建时间与镜像 +约 200MB」→ 接受（相对 10GB
镜像 <2%，且只在 opt-in 的 cu130 形态）；⑦ 未采纳：独立构建开关 + 归档身份扩展
（成本高于收益，见 F 阶段裁决）。

**验收**：`_toolchain_guards.py` 新增 **§9** 四查——① 标记版本 ==
`nvcc --version` 实测；② 农场布局齐备；③ `ldconfig -p` 已登记 `libcudart`
（产物「开箱即跑」的必要条件）；④ **真编译 + 真链接**最小 `.cu`
（`-c` 与 `-lcudart` 双段，**不运行**——构建期无 GPU 属预期边界），非 cu130
形态反向断言 nvcc 与标记双双缺席。**真机复核（2026-09-20 实测）**：镜像重建 →
`invoke xmnn.down && invoke xmnn.up --gpu --skip-build` → 容器内 `nvcc -V`
= 13.4.92、`CUDA_HOME=/usr/local/cuda`；`nvcc probe.cu -o probe -lcudart && ./probe`
→ 缺省 arch 报 `unsupported toolchain`（sm_75 产物 vs 本机 **RTX 5050 Laptop
cc 12.0**），`-arch=native` 后 `result=42` **全链路通过**（编译→链接→GPU 运行）；
devuser 身份 `nvcc -V` 通过（内核用户面同源）；`invoke xmnn.smoke` 全绿
（守卫 §9 + 源码挂载 + `tvm.build('llvm')`）；`torch.cuda.is_available()=True`。
构建期守卫已把「标记==实测 / 农场 / ldconfig / 真编译真链接」四查固化；
Jupyter `!nvcc -V` 与 exec 同 PATH（`/usr/local/bin` 在镜像默认 PATH）。

**C 同步**：[rules/xmnn-overlay.md](rules/xmnn-overlay.md) §11.2·§11.6（新增）、
[AGENTS.md](../AGENTS.md) C18 ② 与新增 **C25**、
[docs/11](../docs/11-xmnn-overlay.md)、[docs/04](../docs/04-troubleshooting-guide.md)
新增 **C-I7**、[overlays/xmnn-dev/README.md](../overlays/xmnn-dev/README.md)、
[.env.example](../.env.example)。提交 `fix(client)` = `1cd53ab48`、
`docs(client)` = `10f633d64`。

### 2026-09-20 · `fix:` SSH 会话补齐源码调试环境——`import xmnn/tvm` 不再 `ModuleNotFoundError`（C30 / 排障 C-I9）

**关联七概念场景**：场景2「问题解决」完整链路 I→F→V→C（强制 V 门）。
起点：用户 `ssh -p 2223 devuser@localhost` 进 xmnn-dev 容器执行
`python tools/accuracy.py -n debug.iranti_caffe` 报
`ModuleNotFoundError: No module named 'xmnn'`；`conda activate base` 后**仍报同样错**；
交互式 `import tvm` 报 `No module named 'tvm'`。

**I 洞察（G2 门，四元组）**：
① 现象——SSH 会话内 import 全失败，而**同一容器**的 Jupyter「Python 3.14 (xmnn dev)」
内核与 `podman exec` 下同样的 import 全部正常；② 根因——compose `environment` 注入的
5 个调试变量（`PYTHONPATH`/`TVM_LIBRARY_PATH`/`LD_LIBRARY_PATH`/`NPU_TOOLS_ROOT`/
`XMNN_TOOLS_ROOT`）只到达容器 PID 1 与 Jupyter 内核（kernel.json 内嵌），
**sshd 派生的会话不继承容器 config env**；③ 影响——tvm/vta/xmnn 经 `PYTHONPATH`
从 `/workspace` 挂载树导入（**不是** site-packages），变量缺失即全链失效，且报错
形态直指「包缺失/镜像损坏」，把排障方向带偏；④ 建议——在**镜像内**补齐环境，
而非要求使用者手工 `export`。
反证/对照实验：`podman exec xmnn-dev printenv` 五键齐全；交互式 `ssh -tt` 与
`ssh host "cmd"` 两形态实测五键**全空**；仅把这 5 个变量注入 SSH 会话后
`/opt/conda/bin/python -c "import tvm, xmnn; from xmnn.accuracy_api import accuracy_xmnn"`
立即通过（tvm ← `/workspace/npu_tvm/python/tvm`、xmnn ← `/workspace/npuusertools/xmnn`）。

**F 第一性原理**：SSH 会话的环境有两条**各自独立**的通路，且都绕开容器 config env——
① login shell 经 `/etc/profile` → `/etc/profile.d/*`；② `ssh host "cmd"` 的最外层
`bash -c` **不读任何 shell 启动文件**（实测：bash 仅在执行**脚本文件**时读 BASH_ENV，
`-c` 命令串不读）。故任何单通道方案必留缺口，只能双通道——基底 entrypoint 早已用
sshd `SetEnv` 注入 `CONTAINER_HOST`（其注释即写明「SetEnv 是唯一不经任何 shell
启动文件的注入点」），本次沿用同一先例；且基底 entrypoint **无 hook 机制**，故落点
必须在本 overlay 镜像侧。

**V 对抗（六条）**：① **first-wins 陷阱**——`SetEnv` 写成 5 行时 `sshd -T` **只回显
第一条**、其余静默丢弃（实测），必须写成**单行空格分隔**，否则「注入成功但只有 1 个
变量生效」比原缺陷更难察觉；② sshd **不按连接重读** sshd_config（实测：只改文件、
不 SIGHUP 时新连接仍拿不到），脚本须补 SIGHUP 分支（构建期无 sshd 自动跳过；已建立
会话不受影响，`sshd-session` 是独立进程）；③ 幂等——标记行若不参与清理会随每次执行
**累积**（实测连跑 3 次留 3 行），已并入 sed 清理；④ 安全——`sshd -t` 失败必须
**整段回滚**，绝不让容器因注入而起不来 sshd；⑤ 漂移——同一组值在 compose
`environment`、kernel.json（`register-kernel.sh`）、本脚本有**三份副本**，任何一处
改漏都复现「内核可用、SSH 不可用」，须由单测逐字锁死；⑥ **第二个独立陷阱**——
SSH 默认落在 **main env**（cp314t，**无 numpy**），补上 `PYTHONPATH` 后若仍用裸
`python` 会改报 `No module named 'numpy'`，故文档必须写明解释器口径
（`/opt/conda/bin/python` 或 `conda activate base`）。
补充：测试替身（临时 sshd_config 路径）不得触发 SIGHUP，故重载分支以「改写的正是
默认 `/etc/ssh/sshd_config`」为前置条件，避免误伤宿主/其它 sshd 进程。

**C 原子提交**：
- 新增 [overlays/xmnn-dev/scripts/setup-ssh-env.sh](../overlays/xmnn-dev/scripts/setup-ssh-env.sh)：
  通道① `/etc/profile.d/50-xmnn-dev-env.sh`（`${VAR:=默认}` 语义，已注入则不覆盖）；
  通道② sshd_config 单行 `SetEnv`（含标记行、幂等清理历史多行形态）；`sshd -t` 校验
  失败整段回滚 + `sshd -T` 计数自检（把 first-wins 从静默失败变成**构建期硬失败**）
  + 运行期 SIGHUP；三个路径可经环境变量改写仅供测试（生产即默认值）。
- [Containerfile.xmnn-dev](../overlays/xmnn-dev/Containerfile.xmnn-dev) Layer 5
  与 `register-kernel.sh` 同批执行该脚本（Layer 4 已 `COPY scripts/`，无需改 COPY）。
- 新增 [tests/test_xmnn_dev_ssh_env.py](../tests/test_xmnn_dev_ssh_env.py) 7 例：
  三份副本逐字防漂移（compose ↔ kernel.json ↔ 脚本）+ 临时目录实跑（profile.d 内容、
  单行 SetEnv、幂等含标记行、陈旧多行清理、`sshd -t` 失败回滚）。
- 文档闭环：[docs/04](../docs/04-troubleshooting-guide.md) 新增 **C-I9**（含判据、
  老镜像一行 `export` 逃生、解释器口径、first-wins 说明）、
  [docs/11](../docs/11-xmnn-overlay.md) 服务表后新增「SSH 会话自带源码调试环境」段
  + 排障表 `import tvm` 行改写、[overlays/xmnn-dev/README.md](../overlays/xmnn-dev/README.md)
  调试工作流两段改写、[AGENTS.md](../AGENTS.md) P0 清单 C26 与变更日志。

**验收**：`pytest tests/test_xmnn_dev_ssh_env.py -q` → **7 passed**；
**变异测试**（把脚本改回「每变量一行 SetEnv」）→ 确定性失败 3 例（脚本自检报
`[ssh-env] ERROR: sshd -T reports 1 setenv entries, expected 5`），还原后 7 passed；
全量 `pytest tests/ -q`（py314）→ **254 passed / 7 skipped / 1 failed**（唯一失败
`test_vs_real_rec_merge_probes` 为既有预存在，与本次无关）。
真机：把脚本即时写入运行中容器（`podman cp` + `podman exec bash`）后，
`ssh host "cmd"` 与 login shell（`bash -lc`）两形态 `import tvm, xmnn` 均通过，
用户原始命令的 `ModuleNotFoundError` 消除——余下
`FileNotFoundError: 文件 temp/debug.iranti_caffe/accuracy/outputs/59.bin 不存在`
属该网络输入数据缺失，与本缺陷无关；容器内自检 `marker=1 / SetEnv=1 / mode=777`
（幂等与文件权限均保持）。

**注意**：镜像侧修复需 `invoke xmnn.build && invoke xmnn.up --skip-build` 重建容器
才持久（重建后 SSH 密码会重新回读、横幅重印；Jupyter 登录态与 host key 已持久化）；
老镜像按 C-I9 在会话内一行 `export` 逃生。本批全部改动**未提交 git**（用户要求先不提交）。

### 2026-09-20 · `fix:` `up` 横幅 SSH 行改印完整命令（C29 / 排障 C-I8）

**关联七概念场景**：场景2「问题解决」完整链路 I→F→V→C（强制 V 门）。
起点：用户在宿主终端执行 `ssh devuser@localhost`，输入 `invoke xmnn.up` 横幅
打印的密码后连续三次 `Permission denied, please try again.`，疑为密码错或
C24 凭证回读失效。

**I 洞察（G2 门，四元组）**：
① 现象——未带 `-p` 的 ssh 在宿主终端被拒；② 根因——宿主 `0.0.0.0:22` 由
**宿主自身 sshd** 监听（`ss -ltnp` 见 `sshd: /usr/sbin/sshd -D [listener]`），
而宿主无 `devuser` 用户（`getent passwd devuser` 为空），密码比对必然失败，
容器 SSH 只在宿主 2223/2222/2224/2225；③ 影响——报错与「密码错」不可区分，
用户按「凭证链路故障」排障，成本高且会误改 C24 链路；④ 建议——横幅给
**零翻译可执行**的完整命令。反证：同密码 `ssh -p 2223 devuser@localhost`
登录成功（`uid=1000(devuser)`）、容器 `/etc/shadow` 有 devuser 条目、
`sshd_config` 为 `PasswordAuthentication yes`、启动日志
`[IMPORTANT] devuser password:` 与横幅逐字一致 → **凭证链路全通**。

**F 第一性原理**：ssh 客户端**不支持** `user@host:port` 语法，而本栈端口
非默认（22 被宿主占用，容器不可能用 22）→ 裸地址形态**结构性丢失端口信息**，
唯一零歧义表达是完整命令行（同仓 `client_core.py` 访问信息横幅早已如此，
overlay 内核是唯一例外）。

**V 对抗（六条）**：① 只改文案不改肌肉记忆 → 必须同步排障表；
② 端口若为 22，`-p 22` 仍合法，无回归；③ 禁止把密码并入命令行（进 shell
history 与 `ps`），密码仍走独立行；④ 列宽与 `Jupyter ` 对齐，版式不变；
⑤ 改动落在共享内核一处，四栈同受益；⑥ **独立发现**——known_hosts 中
`[localhost]:2223` 是 host key 卷引入**之前**的旧指纹，修好 `-p` 后首连
必撞 `REMOTE HOST IDENTIFICATION HAS CHANGED`，须同批给一次性重置指引。

**C 原子提交**：
- [overlay_core.py](../src/jpman_client/tasks/overlay_core.py) `up_stack`
  横幅 SSH 行由 `localhost:{port}` 改为 `ssh -p {port} devuser@localhost`
  （端口取 `_env_port`，随 `.env`/环境漂移，不写死）。
- [tests/test_overlay_core.py](../tests/test_overlay_core.py) 新增 2 例：
  `test_up_banner_prints_copyable_ssh_command`（含 `-p` 与用户名，并断言
  裸地址形态不再出现）、`test_up_banner_ssh_command_follows_port_env`
  （端口随 env 漂移）。
- 文档闭环：[docs/04](../docs/04-troubleshooting-guide.md) 新增 **C-I8**
  （含「宿主 22 ≠ 容器映射」判别式、`ssh-keygen -R "[localhost]:2223"`
  一次性重置）、[docs/11](../docs/11-xmnn-overlay.md) 横幅描述、
  [AGENTS.md](../AGENTS.md) P0 清单 C25 与变更日志。

**验收**：`pytest tests/test_overlay_core.py -q` → **109 passed / 1 skipped**；
全量 `pytest tests/ -q`（py314）→ 首轮 **246 passed / 7 skipped / 2 failed**，
2 例为既有记录在案的预存在失败（`test_vs_real_rec_merge_probes` 的
podman-compose rec_merge 分歧、`test_env_template_lf_only` 的 xmnn-runtime
`release/.env.example` CRLF），与本次无关；后者已在本批归一化行尾后转绿
（见下「同批行尾归一化」）。真机侧：本次未重建容器（横幅文案随
下一次 `up` 生效），但根因链已用 `ssh -p 2223` + 横幅密码端到端证实。
**同批收口（用户追加要求，先不提交）**：`overlays/xmnn-runtime/Containerfile.xmnn-runtime`
Layer 4 的**构建完成横幅**（非容器内 MOTD，此前表述有误，已更正）原印
`# services : SSH localhost:2225, Jupyter localhost:8893 (invoke xmnnrt.up)`
——同一裸地址形态，且把**宿主端口**当作镜像事实印出（镜像构建期根本不知道
宿主端口，2225/8893 只是 `release/.env` 的默认值，可由 `XMNN_SSH_PORT` /
`XMNN_JUPYTER_PORT` 覆盖）。改为命令形态并标注端口来源：
`# services : ssh -p 2225 devuser@localhost（宿主端口，发布栈默认；XMNN_SSH_PORT 可覆盖）`
+ `#            JupyterLab http://localhost:8893（…；启动 invoke xmnnrt.up）`。
口径与 `release/xmnnctl.ps1::Print-Banner`（`SSH : ssh -p $sport devuser@localhost`，
端口取 `.env`）和 [overlays/xmnn-runtime/README.md](../overlays/xmnn-runtime/README.md)
L87（`ssh -p 2225 devuser@localhost`）一致——发布路径本就正确，仅镜像构建
横幅是例外。该文件工作拷贝为 CRLF（git `text: auto` 归一化，`git diff` 仅
2 增 1 删，无噪声），新增两行已对齐为 CRLF 以保持单文件行尾统一。未重建
镜像（横幅随下次 `xmnnrt.build` 生效），无测试断言该横幅文本（全仓仅
`test_compose_merge.py` 引用 Containerfile 文件名）。

**同批行尾归一化（用户追加要求）**：`overlays/xmnn-runtime/release/.env.example`
本地工作拷贝为 CRLF，命中 `test_env_template_lf_only`（该守卫**直接读字节**，
故能检出 git 归一化所掩盖的 CRLF；CRLF 会污染 bash/compose）。已把该文件
29 行 CRLF 全部归一化为 LF——`file` 判为纯 `UTF-8 text`（不再报 CRLF），
29 行 / 1302 字节，**内容逐行不变**（仅行尾）。**无仓库级改动**：
`git hash-object --path` 与索引 blob 均为 `3999d989291e7195be701f5a486fa7115e47c302`、
`git diff --quiet` 退出码 0（该文件带 `text: auto`，git 读入时本就归一化），
刷新 stat 缓存后 `git status` 转干净——即本项是**本地工作拷贝卫生**，不产生
待提交内容。**注意**：CRLF 是 Windows 侧工作拷贝 / 外部进程写入的产物，可能
再次出现，该守卫正是为捕获此回归而存在。效果：`pytest tests/ -q`（py314）→
**247 passed / 7 skipped / 1 failed**，仅剩 `test_vs_real_rec_merge_probes`
（podman-compose rec_merge 分歧）这一既有预存在失败。同目录
`overlays/xmnn-runtime/.env.example`（31 行）与 `Containerfile.xmnn-runtime`
（132 行）仍为 CRLF：前者无守卫覆盖、后者已在本批把新增行对齐为 CRLF 以
保持单文件行尾统一，二者均**未改动**。

### 2026-09-20 · `fix:` xmnn-dev GPU 透传三层断裂修复——NVIDIA CDI 前置 + 宿主驱动健康探针（C19 / 排障 C-I10）

**关联七概念场景**：场景2「问题解决」完整链路 F→R→V→I→E（强制 V 门）。
起点：xmnn-dev 容器（127.0.0.1:8890）内 `!nvcc -V`/`!nvidia-smi` 均
`not found`，`torch 2.14.0+cu130` 已装但 `cuda.is_available()=False`。

**R 事实（G1 门）**：四个独立断点实证——① 宿主**驱动内核模块 595.71.05**
（/proc/driver/nvidia/version）≠ **用户态库 595.91.07**（dpkg
libnvidia-compute-595-server），宿主自身 `nvidia-smi` 报 `Failed to
initialize NVML: Driver/library version mismatch`（7 月升级后模块从未重载）；
② 纯 N 卡（RTX 3090 + 2080 Ti）加载 nvidia_drm 后**也注册 /dev/dri**，
旧自动探测 `/dev/dri → /dev/dxg` 把 N 卡误判 DRM 形态，只挂渲染节点、
不注入 libcuda（容器内无 /dev/nvidia*）；③ CDI 规格在 tmpfs
`/var/run/cdi/nvidia.yaml`，内部 `host-driver-version=550.90.12` 已过期；
④ llama-server 占用两卡，热重载障碍（用户拍板**重启宿主**规避）。

**V 对抗 → I 根因**：断点②是代码层唯一可修根因，且修复必须让 Intel/AMD/WSL
三既有路径零行为变化（双条件门）；断点①只能 fail-fast 把宿主损坏挡在 up
之前。

**A 行动**：
- 编排层 [overlay_core.py](../src/jpman_client/tasks/overlay_core.py)：
  新增 `NVIDIA_CDI_TOKEN`/`NVIDIA_CONTROL_NODE` 常量与
  `check_nvidia_driver_health()`（宿主 nvidia-smi 探针，version mismatch
  中文诊断 + CDI 重建指引）；`resolve_gpu_device` 自动探测改为
  **CDI（规格 + /dev/nvidiactl 双条件）→ /dev/dri → /dev/dxg**，
  显式/自动 CDI 均强制健康探针；--gpu help 同步。
- 文档闭环（C10）：两份 `.env.example`、overlays/xmnn-dev/README.md
  §GPU/torch、[docs/04](../docs/04-troubleshooting-guide.md) 新增 **C-I10**
  （W-I15/W-I16 同步新探测顺序）、[rules/xmnn-overlay.md](rules/xmnn-overlay.md)
  §11.1.1/§11.4。

**验收**：`pytest tests/ -q` → **244 passed / 7 skipped / 2 failed**，
2 个失败经 git stash 验证为**预存在**（podman-compose rec_merge 依赖、
xmnn-runtime .env CRLF），与本次无关；新增 4 个 GPU 用例全绿。
**真机端到端验证待用户重启宿主后执行**：重建 CDI（/etc/cdi 持久路径）→
`invoke xmnn.build --torch cu130` → `xmnn.up --offline --gpu` → 容器内
nvidia-smi 与 `torch.cuda.is_available()=True`（2 卡）。

### 2026-09-20 · `fix:` 三内部栈补齐 SSH host key 命名卷（quant / monetize / xmnnrt）

**关联七概念场景**：场景2「问题解决」的闭环延伸——承接同日 xmnn-dev 栈
`xmnn-ssh-host-keys` 条目（本文件上一条），补齐**其余三个内部栈**的同款缺口。

**I 事实**：`podman inspect` 与三栈 compose 核对确认 quant / monetize / xmnnrt
均**无任何命名卷**（volumes 仅 bind），三者同源于 `jupyter-podman-rootless`
基底 → 其 SSH host key 同样住容器层、`down/up` 重建即轮换指纹（基底
entrypoint 对未挂载卷的 WARN 回退路径）。

**F 第一性原理（命名规则）**：既有命名卷前缀 = **invoke 命名空间前缀**
（`xmnn-ccache` 对应 `xmnn.*`），故三栈按同一规则取
`quant-` / `monetize-` / `xmnnrt-ssh-host-keys`。**xmnnrt 内部栈刻意与客户
交付栈 `release/compose.yaml` 的 `xmnn-ssh-host-keys` 不同名**——两者项目名
同为 `xmnn-runtime`，若同名则会共享同一实际卷（`xmnn-runtime_xmnn-...`），
一方 `down --volumes` 会牵连另一方；内部栈与交付包属不同生命周期，应隔离。

**A 行动**：三栈 compose.yaml 各增服务段命名卷 + 顶层 `volumes:` 声明；
`xmnn.py` 的 `down_volumes_help` 补第三个卷名；`xmnnrt.py` 的
`down_volumes_help` 由「本栈无命名卷，参数为空操作」改为实际语义（**该文案
已随本改动失真**，属必须同步项）。

**验收**：`test_compose_merge.py` 三栈黄金快照 `volume_targets` 增列
`/var/lib/jpman/ssh-host-keys` → WSL 内五个测试文件
（compose_merge/overlay_core/tasks_surface/xmnnrt_stage/release_bundle）
**194 passed / 7 skipped**（1 例 `test_vs_real_rec_merge_probes` 为已知既有
失败）；三栈真实 `podman-compose config` 渲染逐一核对：卷声明与服务挂载
逐字正确（`quant-` / `monetize-` / `xmnnrt-ssh-host-keys` → `/var/lib/jpman/ssh-host-keys`）。
真机重建验证未做（三个栈中两个正在运行，避免中断）；机制与 xmnn-dev 同源
（同一基底 entrypoint + 同款挂载），且 `xmnn-runtime/release` 栈早已用同
机制交付验证。

**C 同步**：[rules/quant-overlay.md](rules/quant-overlay.md) §3、
[rules/monetize-overlay.md](rules/monetize-overlay.md) §3、
[rules/xmnnrt-overlay.md](rules/xmnnrt-overlay.md) §7 三处卷段落；
[docs/10](../docs/10-quant-overlay.md)、[docs/12](../docs/12-monetize-overlay.md)、
[docs/13](../docs/13-xmnn-runtime-overlay.md) 各增「SSH host key 持久化」条目。
提交 `fix(client)` = `d2ff3a8af`、`docs(client)` = `62444134c`。

### 2026-09-20 · `fix:` 补挂 `xmnn-ssh-host-keys` 命名卷（SSH 主机指纹跨重建稳定）

**关联七概念场景**：场景2「问题解决」（I→F→C 轻量链）。起点是用户请求
「验证 SSH 密钥和 Jupyter token 是否已正确挂载」。

**I 洞察（事实采集）**：四项实测——① `ssh -p 2223 devuser@localhost` 密码登录
成功（`whoami`/`pwd`/`SSH_LOGIN_OK`）；② Jupyter `/api/status` 带 token **200**、
不带 token **403**，token 与 up 横幅一致；③ `podman inspect` 挂载表含命名卷
`xmnn-jupyter`（内含 `notebook_secret`，时间戳 12:06 早于本次 13:45 重建 → 跨
重建保留）；④ **启动日志 WARN**：`Host key volume not mounted at
/var/lib/jpman/ssh-host-keys; keys live in the container layer and WILL rotate on
rebuild`，容器内 `/etc/ssh/ssh_host_*_key` 时间戳 13:45 = 本次重建时间。
→ 凭证链路全通，**唯一缺口是 SSH host key 未持久化**（每次重建轮换指纹，
客户端遭 `REMOTE HOST IDENTIFICATION HAS CHANGED`）。

**F 第一性原理**：基底 entrypoint 已把「host key 存哪」抽象为**卷挂载与否**的
二分（`mountpoint -q /var/lib/jpman/ssh-host-keys` 为唯一判据：挂载=持久模式、
key 落卷内、`sshd_config` 的 `HostKey` 指向卷路径；未挂载=容器层生成并打 WARN）。
故修复不必改 entrypoint，只需在 consume 侧把卷挂上——且客户交付栈
`overlays/xmnn-runtime/release/compose.yaml` 早已挂同卷同落点，本次是
**内部开发栈对其对齐**。

**A 行动**：`overlays/xmnn-dev/compose.yaml` 新增第三个命名卷
`xmnn-ssh-host-keys` 挂 `/var/lib/jpman/ssh-host-keys`（服务段 + 顶层声明），
跟随 `xmnn-ccache`/`xmnn-jupyter` 的既有约定（down 默认保留、`--volumes`
三卷同删）。

**验收**：`tests/test_compose_merge.py` 黄金快照 `volume_targets` 增列
`/var/lib/jpman/ssh-host-keys`（漏挂即断言失败）→ WSL 内
`pytest tests/test_compose_merge.py tests/test_overlay_core.py
tests/test_tasks_surface.py -q` **142 passed / 1 skipped**（1 例
`test_vs_real_rec_merge_probes` 为已知既有失败——真实 `rec_merge` 对
`depends_on` list↔dict 归一化与模拟器分歧，非本次回归）。

**C 同步**：[rules/xmnn-overlay.md](rules/xmnn-overlay.md) §5 新增
「SSH host key 命名卷」段（含与交付栈同卷名同落点的强制约定）、§6 命名卷
计数更新；[docs/11-xmnn-overlay.md](../docs/11-xmnn-overlay.md) 新增持久化段、
排障表 `REMOTE HOST IDENTIFICATION` 行改写为「已根治 + 剩余三情形甄别」；
[overlays/xmnn-dev/README.md](../overlays/xmnn-dev/README.md) 命令表/持久化块/
调试工作流三处同步；[AGENTS.md](../AGENTS.md) 变更日志同步。
提交 `fix(client)` = `8ac12f7db`、`docs(client)` = `b0156c310`。

### 2026-09-20 · `fix:` WSL2 GPU 透传补齐两条宿主依赖（`libdxcore.so` + `/usr/lib/wsl/drivers`）

**关联七概念场景**：场景2「问题解决」（I→F→V→A→C，session
`sc-20260920-torch-missing`）。起点是用户截图「notebook 内 `import torch` 报
`ModuleNotFoundError`」，收尾时连带查出 GPU 透传的深层缺陷。

**I 洞察（现象采集）**：`inv xmnn.build --torch cu130` + `inv xmnn.up --gpu`
成功后，容器内 `torch 2.14.0+cu130` 可导入，但 **`torch.cuda.is_available()` 恒
False**；分层探测（`.temp/probe_cuda.py`）定位到 `cuInit()` 返 **100**
(`CUDA_ERROR_NO_DEVICE`)，而宿主 WSL 侧 `nvidia-smi` 完全正常（RTX 5050 Laptop /
驱动 581.57 / CUDA 13.0）。另：`import torch` 报错本身**不是**缺陷——GPU 与
torch 默认全关（C18），当时镜像 LABEL `torch-flavor=""`、marker 0 字节，
证据四处自洽。

**F 第一性原理**：`/dev/dxg` 只是**半虚拟化通道**，CUDA 实现由 WSL 宿主提供；
用例把「库能否加载」当作「设备是否可见」的判据——该假设被实测证伪：只挂
`libcuda.so.1` 时 `CDLL` 成功而 `cuInit()`=100。逐项差分后**最小充分条件是三条
bind 齐备**：① `libcuda.so.1`（缺则 CDLL 失败）、② `libdxcore.so`（DXCore 桥接
库）、③ `/usr/lib/wsl/drivers`（Windows 驱动库目录，libcuda 初始化时扫描）。
**第一轮实测只验到 ① 这一层**，故曾把「单文件挂载」误写成充分条件。

**V 对抗审查**：① 魔鬼代言人——「`--privileged` 或 `--cap-add SYS_ADMIN` / 
`seccomp=unconfined` 就行」：**实测否决**（前两者均 100；`--privileged` 有效但
非必要，本形态坚持零特权）；② 新人——「挂整目录 `/usr/lib/wsl/lib` + 设
`LD_LIBRARY_PATH` 最省事」：**否决**——目录未进容器内 ld 搜索路径（实测
`libdxcore.so: FAIL`），而设 `LD_LIBRARY_PATH` 会整体冲掉栈自带的 TVM 库路径；
③ 老板——「宿主驱动是不是坏了」：**排除**——宿主 `nvidia-smi` 正常，
`/dev/dxg` 存在，故障面锁定在容器侧挂载；④ 未来——「怎么防再犯」：**采纳**——
门禁改三条校验 + 测试锁 target 全集 + 规则写「库能加载≠设备可见」。

**A 原子化实现**：① `overlays/{xmnn-dev,onnx-quantized}/compose.gpu.wsl.yaml`
三条只读 bind（单文件 `libcuda.so.1`、单文件 `libdxcore.so`、目录
`/usr/lib/wsl/drivers`，均 `create_host_path: false`）；② `overlay_core`：
`WSL_CUDA_LIB` 单常量 → `WSL_GPU_PATHS` 三元组，`resolve_gpu_device` 预检改为
遍历缺项并**逐条点名**；③ 测试：`test_compose_merge.py` 断言三条 bind 的
target→source 全集，`test_overlay_core.py` 改为「缺任一路径均 fail-fast」。

**验收点**：① 单测 `pytest tests/test_compose_merge.py tests/test_overlay_core.py
tests/test_tasks_surface.py -q` → **142 passed / 1 skipped**（1 例
`test_vs_real_rec_merge_probes` 为 WSL 侧既有失败：真实 `rec_merge` 与模拟器对
`depends_on` list↔dict 归一化的分歧，与本次改动无关）；② **真机验收
（决定性）**：重建容器后容器内 `torch 2.14.0+cu130`、`cuda available: True`、
`device count: 1`、`device name: NVIDIA GeForce RTX 5050 Laptop GPU`、
`capability (12, 0)`、512³ matmul 结果正确，且 `LD_LIBRARY_PATH` 为空（TVM 路径
未污染）；③ 容器重建判据正反互证（凭证由 `3wSqlBZOahRHkemi` 变为
`6vTTNsVPLoBt9bXv`）。

**C 同步**：[docs/04-troubleshooting-guide.md](../docs/04-troubleshooting-guide.md)
W-I16 补第二轮实测（「库能加载≠设备可见」+ 三条 bind + `cuInit` 判据）、
[docs/11-xmnn-overlay.md](../docs/11-xmnn-overlay.md) 明确**两维度正交**
（GPU=运行期 `up --gpu`／torch=构建期 `build --torch`，故无 `build --gpu`；
`inv xmnn.up --gpu --offline` 实测可用）、
[overlays/xmnn-dev/README.md](../overlays/xmnn-dev/README.md) 同步三条 bind 与
「改 flavor 须重建镜像+重建容器」、
[rules/xmnn-overlay.md](rules/xmnn-overlay.md) §11.1「禁止引入 `build --gpu`」
+ §11.1.2 两轮矩阵 + §11.4 测试锁。
提交 `fix(client)` = `ee49d2857`、`docs(client)` = `f9c99832b`。

### 2026-09-20 · `fix:` 工作区 9p 无主文件致 Jupyter 保存报 Permission denied（排障 W-I19）

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session
`sc-20260920-workspace-perm`）。

**I 洞察（现象采集）**：xmnn-dev 栈 JupyterLab（localhost:8890）打开工作区既有
`main.ipynb` 时工具栏显示 `notebook is read-only`，保存弹
`File Save Error for main.ipynb — Permission denied: main.ipynb`；而**同目录新建**
的 `Untitled.ipynb` 保存正常。决定性判据来自容器内 `ls -lan /workspace`：
`main.ipynb` 属主为 **`65534 65534`**（nobody），正常文件为 `0 0`；宿主侧
对应 **`100999:100999`**。

**F 第一性原理**：写权限 = 属主 uid × 模式 × 写者在其 user namespace 内的能力。
实测 `/proc/1/uid_map` 为 `0→1000`、`1..65536→524288..589823`（`/etc/subuid`
基线 524288），宿主 100999 **不在任何映射区间** → 容器内呈现 nobody；容器 root
仅对**已映射** uid 持有 `CAP_DAC_OVERRIDE`，对未映射 uid 连 `chown` 都报
`Operation not permitted`（实测）。故该文件在容器内**无解**。100999 = 100000+999
与 subuid 基线 100000 的运行时自洽——这批文件由**另一 UID 映射上下文**（Docker /
其他 WSL podman 实例）写入；工作区根 0777 使新建文件取挂载默认属主 1000，故
**只有旧文件卡死**，极易误判为「Jupyter 权限配置错 / entrypoint 有问题」。

**V 对抗审查**：① 魔鬼代言人——「容器内 `chmod 666` 就行」：**否决**，实测
`chown` EPERM，chmod 同理（同需 CAP_FOWNER）；② 新人——「宿主侧 `chown`/`chmod`
最直接」：**否决并实测证伪**——`/mnt/d` 是 9p/drvfs 且挂载项**无 `metadata`**，
`sudo chmod 600 f` 返回 0 而 `ls` 权限位不变、`sudo chown 1000:1000 f` 后属主仍
100999，「改属性」这条路在本机无效；③ 老板——「只修这一个文件够吗」：**采纳**
为验收项，递归扫描工作区（剪除三个源码 bind）得 3 处同类
（`main.ipynb` / `.ipynb_checkpoints/main-checkpoint.ipynb` / `.Trash-1000`），
一并处理；④ 未来——「怎么防再犯」：**采纳**，写入规则条款 + 速查表 W-I19。

**A 原子化实现**：宿主侧**换 inode**——`cp` 备份 → `rm` 原文件（父目录 0777，
删除只看目录写位）→ `cp` 回原路径，新 inode 取挂载默认属主 1000:1000；空垃圾
目录 `.Trash-1000` 直接 `rm -rf`（Jupyter 按需重建）。**无代码改动**：容器内路径
与「改权限位」路径均经实测排除，自愈代码无处落脚。

**验收点**：① 容器内 `test -w /workspace/main.ipynb` 通过；② 真机
`podman exec xmnn-dev cp` 覆盖写回原文件成功；③ notebook 内容完好（JSON 可解析、
3 cells、983 字节与修复前一致）；④ 容器内属主由 `65534 65534` 变为 `0 0`。

**C 同步**：[docs/04-troubleshooting-guide.md](../docs/04-troubleshooting-guide.md)
新增 **W-I19**（含 `65534` 判据、换 inode 三步、chmod/chown 空操作陷阱）、
[rules/xmnn-overlay.md](rules/xmnn-overlay.md) §4 新增「工作区 9p 无主文件契约」。
提交 `docs(client)` = `ada8cf4de`。

### 2026-09-20 · `fix:` 基段声明 `logging: k8s-file`，恢复 `podman logs` 可读（C24 前置）

**关联七概念场景**：场景2「问题解决」（F→V→C，session `sc-20260920-up-credentials`，
C24 的**根因追加**）。C24 落地后用户反馈「还是没有显示」，据此重开第一性原理
诊断。

**F 第一性原理（重开）**：C24 假设「`podman logs` 能读到容器启动日志」。把该
假设当命题实测：容器 `caecf0206361`（xmnn-dev）`podman logs` 输出 **0 字节**；
新建一次性容器（ubuntu:26.04 + `echo`）复现 **0 字节**；`podman inspect` 显示
驱动为 **`journald`**；而 `journalctl CONTAINER_NAME=xmnn-dev` 能读到完整启动
横幅（含 `[IMPORTANT] devuser password:` / `Token:`）。再验 `podman run
--log-driver k8s-file` → `podman logs` **15 字节正常**。结论：**日志数据完好，
但本机 podman 读不到 journald**——`log_driver = journald` 来自发行版
`/usr/share/containers/containers.conf`（podman-machine 默认），在 WSL 嵌套
systemd 命名空间下 podman 的 journal 访问失效（CLI `journalctl` 可读）。
故 C24 的「第二重成因（tail 窗口）」是**表象**，真根因是**日志通道不可读**：
它不仅打挂凭证回读，还让 `invoke <ns>.logs` **一直是空的**。

**V 对抗审查**：① 魔鬼代言人——「内核回退 `journalctl CONTAINER_ID=<id>` 就行，
别动基段」：**否决**——只救回读，`invoke <ns>.logs` 继续静默为空，把根因留在
原地；且内核要引入 journald 专属分支（栈无关内核不该有环境特化）。② 新人——
「直接改发行版 `containers.conf` 不更省事」：**否决**——那是机器级越权改动、
machine 重建即丢失，且影响同机其他项目。③ 老板——「日志驱动变更会不会影响
其他栈」：**采纳**为验收项——基段被四栈 `extends`，故真机重建 xmnn 栈验证驱动
与日志可读性。④ 未来——「有人顺手删掉这行怎么办」：**采纳**——加正向断言锁死。

**A 原子化实现**：`overlays/_shared/base-rootless.yaml` 服务 `rootless-base` 显式
声明 `logging: {driver: k8s-file}`（含文件头决策注释：证据 + 代价），四栈经
`extends` 同构继承；`tests/test_compose_merge.py` 新增
`test_base_declares_podman_readable_log_driver`（基段 + 四栈渲染双向断言）。

**验收点**：① 单测 `pytest tests/test_compose_merge.py tests/test_overlay_core.py
-q` → **137 passed / 1 skipped**；② **真机验收（决定性）**：
`inv xmnn.down && inv xmnn.up --gpu --skip-build` 重建后，`podman inspect` 驱动
= `k8s-file`、`podman logs xmnn-dev` = **9872 字节可读**（此前 0），up 横幅打印
`密码    devuser / <16 位>` 与 `直达    http://localhost:8890/lab?token=<32 位>`；
③ podman-compose 支持该键已核实（其源码把 `logging.driver` 映射为
`--log-driver`）。

> **代价（已知取舍）**：日志改落容器存储文件，不再进宿主 journal（不跨容器
> 删除保留）。换取 `podman logs` / `invoke <ns>.logs` / up 凭证回读三条链路
> 在本机恢复可用。
> **生效条件**：驱动属**创建期**参数，旧容器需 `inv <ns>.down && inv <ns>.up`
> 重建一次（本次已在 xmnn 栈执行）。

**C 同步**：代码+测试提交 `fix(client)` = `c7c50bf1a`
（`overlays/_shared/base-rootless.yaml` / `tests/test_compose_merge.py`）；
文档提交 `docs(client)` = `582cef178`（
[rules/xmnn-overlay.md](rules/xmnn-overlay.md) §6 C24 前置条件、
[rules/quant-overlay.md](rules/quant-overlay.md) §3 基段字段清单、
[docs/11-xmnn-overlay.md](../docs/11-xmnn-overlay.md) 凭证段、
[.agents/README.md](README.md) 基段行、
[AGENTS.md](../AGENTS.md) P0 C24 条款⑤ + 变更日志、本文件）。

### 2026-09-20 · `feat:` up 横幅回读容器内生成的 SSH 密码与 Jupyter token（C24）

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session `sc-20260920-up-credentials`）。

**I 洞察（四元组）**：**现象**——`invoke xmnn.up --gpu` 成功后，用户看不到 SSH
密码，也看不到 Jupyter token（除非 `.env` 预设过），且执行完 `.env` 仍未见更新，
据此怀疑「凭证丢失 / 配置未生效」。**根因**——`.env` 的 `USER_PASSWORD` /
`JUPYTER_TOKEN` 留空是**设计上的常态**：两键经 `_shared/base-rootless.yaml` 以
`${KEY:-}` 空串透传进容器，由基底 entrypoint 在**容器内**用 `pwgen` 生成，并
**只打印到容器启动日志**；`up` 横幅原样转发 `.env` 值，自然只能拿到空串（且
`.env` 在 overlay 路径是**单向只读**：`_load_env_overrides` 只做
`.env → os.environ`，内核全程无写 `.env` 代码）。**第二重成因**——即便用户去查
日志，`invoke xmnn.logs` 恒带 `--tail=100` 只看**尾部**，而凭证横幅位于启动日志
**头部**，容器启动日志较长时横幅早已被挤出窗口，于是「容器里明明打印过」也变成
「哪里都看不到」。**（2026-09-20 追加更正**：本条当时的「第二重成因」判断**不
成立**——后续实测发现本机 `podman logs` 读 journald 日志恒为空，见上一条 `fix:`
条目；tail 窗口只是表象，真根因是日志通道不可读。此处保留原文以存诊断轨迹。）**影响**——用户被迫在「找不到凭证」与「怀疑工具没读 .env」之间
反复试错，实际只是**信息可见性**缺口，非功能缺失。**建议**——把既有信息在正确的
位置（`up` 收尾横幅）以只读回读的方式呈现，同时消除 tail 窗口的误导。

**F 第一性原理（凭证可见性的必要条件链）**：凭证要在 `up` 横幅可见，必须满足
① 值在某处**已存在**（预设或容器内生成）→ ② `up` 能**读到**它 → ③ 读到后**打印**。
留空场景下 ① 在容器启动日志里已成立，断点在 ②：横幅的数据源只接了 `.env`
（空串），未接「容器运行态」。故最小改动是把数据源从「`.env` 单源」扩为
「`.env` 优先、空则回读容器日志」，**不需要**也不应该改写 `.env`——因为凭证
生成责任已显式留在基底 entrypoint，overlay 若回写 .env 就等于制造第二处事实源，
并让「凭证是随机的、只在本机」这一契约被静默改写。

**V 对抗审查（四视角）**：① **魔鬼代言人**——"直接让 `up` 把生成的凭证写回
`.env` 不就好了"：**否决**——会引入第二处凭证事实源并与 entrypoint 的
`-z` 判定打架（写回后下次启动即变「预设」，日志不再打印随机值横幅），且 overlay
路径一直以「单向只读 .env」为契约，写回属越界；② **新人**——"`parse` 时按
`password:` 匹配就够了"：**否决**——`ALLOW_ROOT_SSH=yes` 时日志里先出现
`Root password:` 行，会把 root 密码误报成开发用户密码，故必须用
`SSH login:` 行取到的用户名**反查**；③ **老板**——"既然日志里有，文档写清楚让
用户自己去查就行"：**否决**——`invoke <ns>.logs` 的 `--tail=100` 会让横幅经常
不在窗口内，纯文档方案等于把「找不到」留给用户（V 阶段同时**采纳**其合理内核：
把 tail 窗口陷阱写进文档）；④ **未来**——"回读失败会不会把 up 搞挂"：**采纳**——
回读全程 `warn=True` 且失败静默降级为空三元组，不打印即不阻断，up 主流程零风险。

**A 原子化实现**：① `overlay_core.py` —— 新增 `parse_container_credentials`
（纯函数，主机零接触、可单测）与 `read_container_credentials`（I/O 包装，按
PROJECT/SERVICE 标签定位容器后 `podman logs <cid> 2>&1 | head -n 300`）；正则
`_CRED_SSH_LOGIN_RE` / `_CRED_TOKEN_RE` 与窗口常量 `_CRED_LOG_HEAD_LINES = 300`
就地声明并注明「勿改回 tail」的理由；`up_stack` 横幅改为回读后再打印
`密码    <user> / <password>（容器内自动生成，仅本机开发）`，并把「直达」行的
token 源改为 `回读值 or .env`（预设时二者同源，行为不变）；内核通用、四栈同构。

**验收点**：① `tests/test_overlay_core.py` 新增 8 例：解析四类边界（完整横幅 /
`Root password` 不得误命中 / 空输入与纯空白 / 仅 SSH 行无 token）+ 横幅两分支
（有回读 → 打印密码行与直达 URL；无回读 → 两行皆不打印）；②
`pytest tests/test_overlay_core.py -q`（py314）→ **103 passed / 1 skipped**；
③ 全量 `pytest tests -q`（py314）→ **238 passed / 2 skipped / 8 failed**，8 例
失败全部为 `test_ast_inject.py`（依赖 bash 的既有 Windows 原生环境差异，非本次
回归）；④ `py_compile` 两文件零告警；⑤ `check-links.py --path apps/containers/client`
无断链（7 条既有目录链接警告与本条无关）。

> **范围（已知未覆盖）**：本条只解决**可见性**——`up` 期间容器确在运行时回读并
> 打印。容器未运行（如 `skip_build` 且栈已被 down）或该容器是 C24 之前启动的
> 历史容器时，横幅仍不显示凭证，此时按文档查日志或用 `podman logs <cid> | head
> -n 300`。`.env` 仍**不回写**（既定契约，非缺陷）；`invoke <ns>.logs` 的
> `--tail=100` 未改动（其语义是跟踪新日志，不适合回看启动横幅）。

**C 同步**：代码 + 测试提交 `feat(client)` = `257d694fa`
（`src/jpman_client/tasks/overlay_core.py` / `tests/test_overlay_core.py`）；
文档提交 `docs(client)` = `aefcaf6d9`（
[rules/xmnn-overlay.md](rules/xmnn-overlay.md) §6 C24、
[docs/11-xmnn-overlay.md](../docs/11-xmnn-overlay.md) 凭证段、
[overlays/xmnn-dev/README.md](../overlays/xmnn-dev/README.md)、
[AGENTS.md](../AGENTS.md) P0 C24 + 变更日志、本文件）。

### 2026-09-20 · `fix:` `up --gpu` 每次都被判「另一控制平面创建」而强制重建栈（C23）

> 编号说明：本条初版曾占用 C22，与同日已先入库的 C22（容器重建轮换 Jupyter cookie
> secret——Terminal 被浏览器层静默中止 / C-I6，见下条）撞号；rebase 到 origin/main 后
> 本条顺延为 **C23**。

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session `sc-20260920-up-preflight-gpu`）。

**I 洞察（四元组）**：**现象**——`inv xmnn.up --gpu` **每次**执行都打印「⚠ 检测到栈由
另一控制平面创建（compose 路径标签 `.../compose.yaml,.../compose.gpu.wsl.yaml`），与当前
平面（`.../compose.yaml`）不一致；直接 up 会被强制 recreate 并可能残留孤儿端口，先优雅
down …」，随后真的 `down` 再 `up -d --no-build`，容器内 Jupyter 会话被销毁、白等
~66 秒首启（真机截图复现）。**根因**——`overlay_core.up_preflight` 的跨平面判据（W-I10）
把**期望值写死成单文件** `str(overlay_dir(spec) / "compose.yaml")`，而 `--gpu` 时
`compose_argv` 恒下发**两个** `--file`（`compose.yaml` + `compose.gpu.*.yaml`），podman 把
两文件以**逗号连接**的原文写进 `com.docker.compose.project.config_files` 标签 → 期望串与
实况**恒不相等** → 判据把「同平面、同参数创建」误判为「他平面创建」。**影响**——凡声明
`gpu_override` 的栈（xmnn / quant）在 `--gpu` 路径上**必然**触发假分歧：`up` 丧失幂等性、
用户容器内会话被无谓销毁，且假阳性会淹没判据本意（防 recreate 留孤儿 rootlessport）
——真出问题时反而不再醒目。**建议**——判据的期望值必须与 `compose_argv` **同源推导**，
不再允许第二处手写文件集。

**F 第一性原理**：① **判据的期望值必须由「本次真正下发的 argv」推出**——两处各写各的
就注定漂移，「写死单文件」的本质是把一个**集合**表达成了**标量**；② **不对称性不可去掉**：
`up --gpu` 对同样由 `--gpu` 创建的栈必须**零动作**（幂等），而 `up`（无 `--gpu`）或形态
切换（generic↔wsl）对同一栈**仍须**判分歧——因为 compose 的 config-hash 确实会变并**真的**
recreate；**精确同集**比较是唯一同时满足两侧的判据，前缀/子集匹配会放过第二种情况；
③ **顺序即语义**：判据需要 `gpu_form` 才能推出文件集，故 `resolve_gpu_device` 必须先于
`up_preflight`；且 GPU 不可用应 **fail-fast 于任何 `down` 之前**——先拆掉用户正在用的栈
再报错，是把可恢复的失败放大成破坏性失败。

**V 对抗审查（四视角）**：① **魔鬼代言人**——"recreate 也能跑通，何必改"：**否决**——
每次 `--gpu` 都拆栈，销毁容器内会话/长任务并白等 66 秒，「`up` 是幂等的」这一语义已被
破坏，且预检本意（防 recreate 留孤儿 rootlessport）被假阳性淹没；② **新人**——"把 expected
改成前缀匹配就行了"：**否决**——会让「无 `--gpu` 的 up 复用 `--gpu` 创建的栈」也被放过，
而那正是 compose 会真 recreate 并留孤儿端口的场景，必须精确同集比较；③ **老板**——"干脆
去掉判据，让 compose 自己 recreate"：**否决**——判据存在的理由是 recreate 会强拆 pod infra
留下孤儿 rootlessport 占端口（W-I10 事故根因）；④ **未来**——"以后再加别的覆盖文件又会
重犯"：**采纳**——抽 `compose_files()` 为唯一事实源，argv 与判据同源，新覆盖文件自动进入
判据。

**A 原子化实现**：① `overlay_core.py` —— 新增 `compose_files(spec, *, gpu, gpu_form)`
（本次调用下发的文件集，**唯一事实源**）与 `compose_config_files_label(...)`（逗号连接，
与 podman 标签同格式）；`compose_argv` 改为复用 `compose_files`；`up_preflight` 新增
关键字形参 `gpu` / `gpu_form`，期望值改由 `compose_config_files_label` 推出；`up_stack`
把 `resolve_gpu_device` 提到 `up_preflight` **之前**并把 `(gpu, gpu_form)` 喂给预检
（顺序即语义，见 F③）。

**验收点**：① `tests/test_overlay_core.py` 新增 6 例：`compose_config_files_label` 的逗号
约定、**同源锁**（三组 `(gpu, form)` 下 `compose_argv` 的 `--file` 拼接必须逐字等于 label
输出）、`up_preflight` 的三种平面关系（gpu 平面同集 → 零 down；非 gpu 平面对 gpu 栈 →
必须 down；form 切换 → 必须 down）、端到端 `up_stack(gpu=True)` 在 gpu 栈上幂等；
② `pytest tests/test_overlay_core.py -q` → **90 passed / 1 skipped**；③ 真机**连续两次**
`inv xmnn.up --gpu --skip-build`（均 exit 0）日志逐字同构：**无**「另一控制平面」警告、
**无** down 行，直接 `podman-compose … --file compose.yaml --file compose.gpu.wsl.yaml
up -d --no-build`，随后「Jupyter 已就绪（127.0.0.1 → HTTP 302）」——两次均**立即可达**，
反证容器未被重建；容器 `Id` / `Created` / `StartedAt` 在两次执行前后**完全一致**
（`17fb88c9f317…` / `2026-09-20 10:17:51.771660461 +0800 CST` /
`10:17:52.990802892 +0800 CST`）→ **零重建，幂等坐实**。

> **范围（已知未覆盖）**：修复依据为**静态推演 + 单测 + 真机连续两次幂等实证**；`down`
> 路径仍只下发 `compose.yaml`（podman-compose down 按项目标签工作，实测有效，本次未改）；
> `up` 的 `--gpu` 旗标本身不写入 `.env`，故「平面」判据的比较对象是**文件集原文**而非
> 旗标历史——若某栈**确实**由裸 compose 用不同文件集创建，判分歧行为按设计保留。

**C 同步**：代码 + 测试提交 `fix(client)` = `6b1fb287d`（`src/jpman_client/tasks/overlay_core.py`/
`tests/test_overlay_core.py`）；文档提交 `docs(client)` = `73ede8f84`（
[rules/invoke-tasks.md](rules/invoke-tasks.md) C23、
[rules/xmnn-overlay.md](rules/xmnn-overlay.md) §4/§11.1.1/§11.4、
[docs/04-troubleshooting-guide.md](../docs/04-troubleshooting-guide.md) W-I10、本文件）；
本条 hash 回填为第三条 `docs(client)` 提交。

### 2026-09-20 · `fix:` 容器重建轮换 Jupyter cookie secret——Terminal 被浏览器层静默中止（C22 / C-I6）

> 编号说明：本条初版曾占用 C21，与同日 xinzo 已先入库的 C21（`up` 就绪等待 /
> W-I18，见下条）撞号；rebase 到 origin/main 后本条顺延为 **C22**，改号前的
> 本地三提交保留在备份分支 `backup/c22-login-state-pre-rebase`。

**关联七概念场景**：场景2「问题解决」（F→V→C→R→I→E，V 门强制，session `sc-20260920-jupyter-terminal-login`）。

**I 洞察（四元组）**：**现象**——xmnn-dev 栈当日 09:28-09:30 由 `invoke xmnn.up --offline`
重建后，浏览器旧标签页点击 JupyterLab **Terminal 打开失败**（Console 见
`PUT /lab/api/workspaces/default` `net::ERR_ABORTED`，另有 Trae 预览注入 `/@vite/client`
404 的良性噪声）；**根因**——`jupyter_cookie_secret`/`notebook_secret` 位于容器临时层
（`/home/devuser/.local/share/jupyter`）且无持久化卷，容器重建即重新生成，旧标签页
cookie 失效后其 `POST /api/terminals` 请求**在浏览器层被重定向/中止、从未到达服务端**
（访问日志零记录，09:31:16 有 `Clearing invalid/expired login cookie`，09:33:02 重新登录）；
**影响**——故障表象在 PTY/WebSocket/权限（误导排查方向），实则是纯登录态失效；
**建议**——第一刀先二分「失败请求是否到达服务端日志」，未到达即认证/浏览器层，
不再下查容器权限；预防上把密钥目录持久化，并让重建后免登录直达成本为零。

**F 第一性原理（Terminal 打开必要条件链）**：浏览器持有效登录 cookie → REST
`POST /api/terminals` 过认证并 200 → WS 升级 `/terminals/websocket/<n>`（注意**无**
`/api` 前缀）→ 服务端 terminado 以 devuser `pty.openpty()` + `/bin/bash` 拉起 shell。
四段逐级实测：curl REST 200、容器内 tornado 回环 WS 回显成功、devuser pty+bash 正常、
token 直访与 127.0.0.1 表单登录两路径 Terminal 均成功——唯一断裂点在链首的 cookie。

**V 对抗审查（四视角）**：① **魔鬼代言人**"是 PTY/rootless 权限坏了，应查 usermod/
SELinux/重建镜像"：**证伪**——四连测试全部通过，且服务端对浏览器的失败请求零日志，
权限故障不会让请求消失在到达之前；② **新人**"WS 404 了，是不是 terminado 版本不兼容"：
**证伪**——那条 404 是诊断者自己误打 `/api/terminals/websocket/` 产生（正确路径无
`/api`），与用户故障无关；③ **老板**"让用户硬刷新重登就算修好"：否决——根因是每次
重建必然复发的结构性缺陷，恢复动作≠修复，必须持久化密钥；④ **未来**"为何不用 bind
挂宿主家目录或全局共享一个 secret 文件"：否决——引入宿主路径耦合、跨栈密钥串用与
uid 漂移风险，命名卷 copy-up 保属主（1000:1000/700 实测）是 rootless 下的正确接缝。

**C 原子修复**：① `overlays/xmnn-dev/compose.yaml` 服务 volumes 增加
`- xmnn-jupyter:/home/devuser/.local/share/jupyter`（附实证注释），顶层
`volumes:` 增加 `xmnn-jupyter: {}`；② `tasks/overlay_core.py` 新增纯函数
`jupyter_direct_url(port, token)`（token 空/空白/None → 空串，否则
`http://localhost:{port}/lab?token={token}`），`up_stack()` 横幅在 Jupyter 行后打印
「直达」行（env 经 prepare_env → `_load_env_overrides` 读 .env，python-dotenv 可容忍
该文件的 CRLF）；③ `tasks/xmnn.py` 的 `down_volumes_help` 文案同步为「同时删除
xmnn-ccache 与 xmnn-jupyter 命名卷（默认保留：Nuitka 编译缓存 + Jupyter 登录态）」。

**验收点**：① 真机（2026-09-20 10:21-10:26，用户批准后 `invoke xmnn.down` ×2 +
`xmnn.up --offline` ×2）——curl `POST /api/terminals` 200、容器内 tornado WS 回环成功、
devuser pty 正常、浏览器两登录路径 Terminal 均打开（用户现场确认恢复），诊断终端全部
DELETE 清理（`GET /api/terminals` → `[]`）；新卷真机三连证：挂载
`xmnn-dev_xmnn-jupyter → /home/devuser/.local/share/jupyter`（devuser:devuser 700、
devuser 可写）、密钥实际落 `runtime/jupyter_cookie_secret`（600）、**两次重建前后
md5 逐字一致**（`8c4b86e5…`），重建前 token 换取的登录 cookie 在重建后**不带 token**
`GET /api/terminals` → 200、`POST` 带浏览器同款 `X-XSRFToken` 头 → 200（裸 POST 403
`'_xsrf' argument missing` 属 XSRF 防护预期，非认证失败），测试终端已 DELETE；up 横幅
两次均打印「直达」URL；② 卷接缝——`podman run -v xmnn-jupyter-voltest:...`
实测镜像内 1000:1000/mode 700 目录 copy-up 后属主保持、devuser 可写（测试卷已清理）；
真实 `podman-compose config`（经 `prepare_env(XMNN_SPEC)`+`compose_argv`）渲染含两个命名卷；
③ 单测——`test_compose_merge.py` 黄金快照 volume_targets 增列
`/home/devuser/.local/share/jupyter`（顺序 /workspace、npu_tvm、npuusertools、models、
/root/.ccache、jupyter）；`test_overlay_core.py` 新增 3 测试函数/5 用例锁 `jupyter_direct_url`
（带 token、strip 空白、空/空白/None 三参数化返回空串）；与 C21（就绪等待）合并后
全量 pytest 实测 **215 passed / 7 skipped / 2 failed**（215 = 合并前 208 + C21
就绪等待新增 7）；2 个存量失败
（`test_vs_real_rec_merge_probes`、`test_env_template_lf_only`）为改动前基线存量问题，
与本次无关。

**E 萃取（可复用模式，已固化为 docs C-I6）**：「UI 请求失败但服务端零日志 ⇒ 故障在
认证/浏览器层，不在容器运行时」——先二分到达性再查权限；另：Jupyter WS 路径是
`/terminals/websocket/<n>`，REST 才带 `/api`，排障探测勿混用。

**C 同步**：代码/测试 5 文件（`compose.yaml`、`overlay_core.py`、`xmnn.py`、
`tests/test_compose_merge.py`、`tests/test_overlay_core.py`）随 `fix(client)` =
`bcfe811b4` 落库；文档 6 处（本文件、[AGENTS.md](../AGENTS.md) P0 C22 + 变更日志、
[04-troubleshooting-guide.md](../docs/04-troubleshooting-guide.md) 新增 C-I6、
[rules/xmnn-overlay.md](rules/xmnn-overlay.md) §5/§6、
[docs/11-xmnn-overlay.md](../docs/11-xmnn-overlay.md)、
[overlays/xmnn-dev/README.md](../overlays/xmnn-dev/README.md)）随文档提交
`docs(client)` = `e45cd809c` 落库；本条 hash 由回填提交补记（沿用 C20/C21 三段式）。

### 2026-09-20 · `fix:` `up` 只等容器不等服务——Jupyter 就绪前浏览器必报 `ERR_EMPTY_RESPONSE`（C21）

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session `sc-20260920-port8890`）。

**I 洞察（四元组）**：**现象**——`invoke xmnn.up` 打印「✅ 栈已启动」并给出
`Jupyter localhost:8890`，用户随即用浏览器打开却得到 `ERR_EMPTY_RESPONSE`
「localhost 未发送任何数据」（此刻命令行 curl 该端口已返回 302）；**根因**——
`up -d` 返回只代表**容器**在跑，不代表**服务**可访问：rootless 端口转发器
（rootlessport）在容器起来的**瞬间**就 accept 宿主端口，而容器内
supervisord → entrypoint → jupyter-lab 真正 listen 需要数十秒（实测
`StartedAt 09:47:58.75` vs jupyter 进程 `lstart 09:49:04` = **66 秒**），窗口期内
连接被 accept 后**立即关闭且零字节返回**，浏览器据此报 `ERR_EMPTY_RESPONSE` 而非
更易理解的 `ECONNREFUSED`；**影响**——用户被「✅ 栈已启动」文案与「端口可连」
**双重误导**，疑心镜像损坏/端口冲突而去排查完全无关的方向，且**四个工作负载栈
全部受影响**（就绪等待落在共享内核 `up_stack`）；**建议**——就绪判据必须从
「容器 Up」升为「**应用层 HTTP 应答**」，超时不是失败而是**给指引**。

**F 第一性原理**：① **「已启动」（容器状态）与「可访问」（服务就绪）是两个断言**，
不应共用一个 `✅`——断言必须与所依据的证据同级；② **TCP connect 在本场景不是
就绪证据**：转发器先于后端 accept，故裸 connect 会**假阳性**（"能连上"恰恰是
窗口期的表征），唯一可靠判据是**读到应用层应答**；③ 就绪等待**不能把慢启动
判成失败**——容器确实 Up，一次 66 秒的首启被中断成 `Exit(1)` 会让用户误以为
"起不来"而重复折腾；④ 该能力属**内核职责**：四栈共享 `up_stack`，落在内核
一处才不会再出现「某个栈忘了等」（与 C18「能力并集」同一取向）。

**V 对抗审查（四视角）**：① **魔鬼代言人**——"刚才那次只是瞬时抖动，刷新就好了，
不必改"：**部分成立但不否决**——现象确实自愈，但**固定 66 秒的窗口必然复发**
（不是抖动而是启动路径的固有耗时），每次首启都误导用户；② **新人**——
"照抄 `refresh_host_keys` 的 TCP 探测（20 秒上限）就行"：**否决**——那里探的是
同 netns 内**真实监听者**，connect 成功即等价就绪；本场景探的是**转发器**，
connect 成功**正是未就绪的表征**（语义相反，且 20 秒还短于实测窗口）；
③ **未来**——"四个栈各加一段等待更灵活"：**收敛**——落内核 `up_stack` 一处，
四栈零成本共享，新栈不写就绪逻辑；④ **老板**——"就绪前干脆不打印 URL"：
**采纳其意并等价实现**——不隐藏 URL（用户可能只想先 ssh），而是**就绪才断言
就绪**，未就绪时 URL 仍给出但明说「可能仍在首次启动，稍后刷新」。

**A 原子化实现**：① `utils.py` —— 新增 `import http.client`、常量
`UP_READY_TIMEOUT_S`/`UP_READY_POLL_S`/`UP_READY_PROGRESS_S`/`UP_READY_PATH`
与 `wait_http_ready(port, *, path, timeout, on_progress) -> (bool, str)`
（双栈地址 `127.0.0.1`/`::1` 各试一次，返回 `(是否就绪, 说明)`；**进度回调排在
超时判定之前**，保证窗口期最后一段也有反馈）。② `overlay_core.py` —— `up_stack`
在 `run_compose_up()` 之后按**宿主 Jupyter 端口**等待就绪（`int(jupyter)`，因
`_env_port` 返回 str）；就绪打印「Jupyter 已就绪（addr → HTTP status）」，
超时**零 `Exit` 调用**，仅打印「⚠ 未在 120s 内应答 + 容器已在运行，稍后刷新
浏览器即可 + `invoke <ns>.logs`」；docstring 同步。

**验收点**：① 新增 `tests/test_up_readiness.py`（5 例，daemon-free，纯回环 socket）：
**TCP 假阳性守卫**（对「只 accept 后立即关闭、零字节回应」的监听者不得判就绪）、
HTTP 应答判就绪（并断言请求路径 = `UP_READY_PATH`）、路径可配、端口关闭时
**超时返回而不抛异常**、长等待期间进度回调确实触发；② `tests/test_overlay_core.py`
新增 2 例：就绪探测必须落在**宿主 Jupyter 端口**（8890）且携带 `on_progress`、
超时路径**不抛 Exit** 且给出 `logs` 指引与 URL；harness 打桩 `wait_http_ready`
为「立即就绪」，避免单测真的轮询 120s；③
`pytest tests/test_up_readiness.py tests/test_overlay_core.py -q` → **89 passed / 1 skipped**；
④ 全量 `pytest tests -q`（py314）→ **219 passed / 2 skipped**，另有 8 例
`test_ast_inject.py` 失败属**既有环境差异**（该模块需 WSL2/Linux 的 bash 与
`os.geteuid`，Windows 原生必然失败，非本次回归）。

> **范围（已知未覆盖）**：就绪探测只覆盖 **Jupyter**（SSH 侧无 HTTP 判据，
> 未纳入）；探针语义是「**任意 HTTP 应答**」而非「Jupyter 业务响应」——302
> 登录跳转即判就绪，故 5xx 也算就绪（对"能否打开页面"这一目标足够，不做内容校验）；
> 机制结论由**强时间证据**（66 秒窗口期 + 零字节关闭 + 两侧 curl 时序）支撑，
> 未做破坏性复现（重启容器会打断用户正在使用的 Jupyter 会话）；超时值 120s
> 为常量，暂未做 CLI/`.env` 可配。

**C 同步**：代码 + 测试提交 `fix(client)` = `5c2b56aa0`（`utils.py`/`overlay_core.py`/
`tests/test_up_readiness.py`/`tests/test_overlay_core.py`，4 文件）；文档提交
`docs(client)` = `5fd7549b9`（[docs/04-troubleshooting-guide.md](../docs/04-troubleshooting-guide.md)
W-I18、[rules/invoke-tasks.md](rules/invoke-tasks.md) C21 与测试节、
[docs/11-xmnn-overlay.md](../docs/11-xmnn-overlay.md)、本文件）；本条 hash
回填为第三条 `docs(client)` 提交。

### 2026-09-20 · `feat:` 离线归档携带 torch 形态身份——`xmnn.save`/`load` 不再静默串档（C20）

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session `sc-20260920-xmnn-save-flavor`）。

**I 洞察（四元组）**：**现象**——用户问「`inv xmnn.save` 如何支持 GPU」，核对后发现
GPU 与归档是**两个正交层面**：设备透传是运行期 compose 叠加（与归档无关），而 torch
形态是镜像内容；**根因**——C18 的「flavor 不参与镜像 tag」与既有「`load` 按 mtime 取
最新归档」两条各自正确的规则叠加出盲区：cpu 与 cu130 两份镜像 **tag 完全相同**
（`localhost/xmnn-dev:latest`），归档名也不带形态时，两者同族同名、共用同一个
`-latest` 软链；**影响**——无网侧 `load` 会**静默导入错形态**，直到容器内
`torch.cuda` 为空（甚至 `import torch` 失败）才暴露，而排查时镜像 tag 与归档名
**双双都看不出区别**；**建议**——镜像的形态身份必须在**归档层可辨识**，且
`save`/`load` 两端都要用它（写得出、也读得回）。

**F 第一性原理**：① 归档是「离线机的镜像来源」，其**身份必须自足**——形态是镜像的
一等属性（已烘进 LABEL `org.specweave.torch-flavor` 与 `/opt/xmnn-torch-flavor`），
归档名若丢弃它，等于让传输层丢字段；② 该属性的**单一事实源是镜像 LABEL**，
不是 `.env TORCH_FLAVOR`（后者只是"打算构建成什么"，镜像才回答"实际是什么"）；
③ 命名与解析必须是**严格互逆的一对**，且解析必须**不可歧义**——镜像 tag 自带
`-latest` 段，形态段若不加以区分就会被反向解析抢走；④ 演进不能**追溯性地废掉**
历史产物，旧归档必须仍可用。

**V 对抗审查（四视角）**：① **魔鬼代言人**——"形态直接加进镜像 tag 不就完了"：
**否决**，一举推翻 C18 已冻结的「一 tag 一形态」契约，且会让 `XMNN_IMAGE_TAG`
这个用户可见键分裂成两份配置；改动面远大于收益；② **新人**——"归档名用
`-<形态>-` 就够，不用加 `-torch-` 中缀"：**实测否决**——`...-xmnn-dev-latest-<id>-<ts>.tar.gz`
会被正则**左最早**匹配成 `flavor=latest`（与 tag 的 `-latest` 段互相冒充），
中缀是消除歧义的最小手段；③ **老板**——"改 `load` 报错就行，不必改命名"：否决，
拒绝导入但不告诉用户"该导哪个"等于把问题推回去，形态进命名后才可能按形态**自动选档**；
④ **未来**——"manifest 已经有字段了，用 manifest 判形态更规范"：**否决**——
`validate_manifest_integrity` 按 `## ` 分段，而 `_append_manifest` 写单 `#` 表头，
实际只有一个块、字段会被后一段覆盖，**只有最后一次 save 的产物能通过校验**；
故形态判定必须落在**归档名**（稳定、逐文件独立），manifest 的 `TORCH_FLAVOR=`
仅作冗余记账字段。

**A 原子化实现**：① `client_core.py` —— 新增 `TORCH_FLAVOR_LABEL` 与
`_image_torch_flavor(info)`（无该 LABEL 恒返回空串，非 torch 栈零影响）；
`save_image` **签名不变**，复用已有的 `image_inspect_info()` 调用顺带取 LABEL，
归档名升为 `<safe_name>[-torch-<形态>]-<shortid12>-<ts>.<ext>`（**无形态时不加段**，
与历史产物逐字一致）；`_append_manifest` 增加 `TORCH_FLAVOR=` 记账字段。
② `utils.py` —— 新增 `archive_flavor(filename)` 与模块级 `_ARCHIVE_FLAVOR_RE`
（与 `save_image` 的命名**严格互逆**）；`find_latest_image_tar(dir, flavor=None)`
增加形态过滤（`None`=不过滤，保持历史语义）。③ `overlay_core.py` —— `load` 的
形态感知**仅当 `spec.torch_flavor` 为真**时生效：未给 `--path` 且期望形态非空 →
按形态过滤选档（无档 Exit(1)）；`--path` 形态与期望不符 → **Exit(1) 且校验先于导入**；
旧归档未标注形态 → 打印提示但**不拦截**；期望形态解析序与 `torch_build_args` 一致
（`os.environ` > `.env` > `""`）；`load` 的 help 文案同步。

**验收点**：① 新增 `tests/test_image_archive.py`（14 例，daemon-free）：`archive_flavor`
四态（含"`-latest` 不得冒充形态"）、`find_latest_image_tar` 形态过滤/空串/无匹配/
跳过软链/目录缺失、`save_image` 归档名与 manifest（有形态 / 无形态零回归）、
`_image_torch_flavor` 五路降级；② `tests/test_overlay_core.py` 新增 5 例锁 `load`
语义（按形态选档、无匹配 Exit、显式路径不符 Exit 且未导入、旧归档提示不拦截、
期望为空保持取最新）；③ `pytest tests/test_image_archive.py tests/test_overlay_core.py -q`
→ **95 passed / 2 skipped**；④ 全量 `pytest tests -q`（py314）→ **212 passed /
2 skipped**，另有 8 例 `test_ast_inject.py` 失败属**既有环境差异**（该模块需
WSL2/Linux 的 bash 与 `os.geteuid`，Windows 原生必然失败，非本次回归）。

> **范围（已知未覆盖）**：形态只进**归档名**与 manifest 记账字段，**不进镜像 tag**
> （C18 契约不变）；`load` 不校验归档内镜像实物的 LABEL（形态以归档名为准，
> 不做二次开箱核对）；`xmnnrt` 栈无 `supports_offline`，故无 `save`/`load`
> 形态路径（其 `.env` 中的 `XMNNRT_IMAGE_TAG=localhost/xmnn-runtime:gpu` 亦无
> 构建路径产出，属另一议题）。

**C 同步**：代码 + 测试提交 `feat(client)` = `88e1a9f35`（`client_core.py`/`utils.py`/
`overlay_core.py`/`tests/test_image_archive.py`/`tests/test_overlay_core.py`，5 文件）；
文档提交 `docs(client)` = `2ee7a2dd4`（[rules/xmnn-overlay.md](rules/xmnn-overlay.md)
§10/§11.2/§11.5、[rules/invoke-tasks.md](rules/invoke-tasks.md) C20 与测试节、
`overlays/xmnn-dev/README.md`、`docs/11-xmnn-overlay.md`、本文件）；本条 hash 回填为
第三条 `docs(client)` 提交。

### 2026-09-20 · `fix:` WSL 桥接探测吞掉 stderr——门禁给出「看似健康」的死胡同指引（W-I17）

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session `sc-20260920-wsl-probe-stderr`）。

**I 洞察（四元组）**：**现象**——Windows 原生 `inv xmnn.build --torch cu130` 打印
「Windows 原生 CPython 不支持 podman-compose 编排路径……且**未能自动桥接至 WSL
发行版**」门禁块，但 `wsl -l -v` 明示 `podman-machine-default` **Running**，发行版内
**任何**命令都不可执行；**根因**——WSL2 虚拟机处于 VM 层不可用态（实测
`wsl.exe -d podman-machine-default -- true` 返回 **11**，stderr
`<3>WSL (...) ERROR: CreateProcessCommon:813: execvpe(/bin/true) failed: I/O error`），
而 `_wsl_distro_available()` 只用 `returncode` 判真伪、**把这条 stderr 丢掉了**；
**影响**——门禁只能提示「WSL 发行版可启动（`wsl --list --verbose`）/ 设置
`COMPOSE_WSL_DISTRO` / 重装 client 依赖」三件**都与本因无关**的事，用户照着核对得到
"Running"，反而更难定位；**建议**——诊断类探测**不得吞掉被探测进程的错误输出**，
「存在但不可用」必须与「不存在」在提示层可区分。

**F 第一性原理**：① 探测的目的是**给出可行动的下一步**，不是"返回 True/False"——
布尔投影在失败路径上丢弃了唯一有用的信息（失败原因），是**信息降级**而非抽象；
② "发行版存在"与"发行版可执行"是两个独立事实，`wsl -l -v` 只回答前者，把
后者交由它回答必然误导；③ 失败处置有**唯一正确解**——VM 层不可用态只能靠
`wsl --shutdown` 重置虚拟机，这条非显然的补救必须能被**非专家的用户**看到，
否则等于把排障成本外包给搜索引擎。

**V 对抗审查（四视角）**：① **魔鬼代言人**——"探测失败就自动 `wsl --shutdown`
不更省事"：**否决**，该命令关闭**全部**发行版进程，编排器擅自重置用户的 WSL
虚拟机属越权破坏性动作，只能作为**提示**给出；② **新人**——"直接打印全部 stderr
更清楚"：否决，wsl.exe 诊断含多行 relay/时间戳噪声，取**末条非空行**才是可读摘要；
③ **老板**——"补个文档就行，代码不改"：否决，用户**已经在**终端看到了误导性
提示，问题恰恰出在提示本身，文档不能替代运行时诊断；④ **未来**——"把失败原因
缓存进模块级变量最省事"：否决，`_wsl_probe` 已 `lru_cache`，重算即缓存命中，
无需引入全局可变状态（并发下更安全）。

**A 原子化实现**：`utils.py` 把探测从 `_wsl_distro_available() -> bool` 升级为
`_wsl_probe() -> tuple[bool, str]`（返回 `(可用, 失败原因)`，失败原因取 wsl.exe
stderr 末行），新增 `_wsl_stderr_last_line()`（**UTF-16LE+BOM 与 UTF-8 自动判编码**：
wsl.exe 自身诊断走 UTF-16LE，被捕获命令输出走 UTF-8，按前 64 字节是否含 NUL 区分）
与 `wsl_bridge_diagnosis()`（非 Windows 或桥接可用返回空串，`COMPOSE_WSL_DISTRO=none`
单独说明为「显式关闭」而非故障）；`_wsl_distro_available()` 保留为布尔投影
（既有接线与打桩点零改动）。`overlay_core.gate_platform()` 门禁块首行打印实测原因
并附 `wsl --shutdown` 逃生指引（无原因时不打印，避免噪音）。

**验收点**：① 新用例 10 例——UTF-16LE 诊断原文透出、UTF-8 兜底、无 stderr 回退
退出码、无 wsl.exe 不抛、布尔投影 + 缓存只探测一次、`none` 哨兵、非 Windows 空串、
桥接可用空串、原因透出；门禁提示 2 例（带诊断时见原因 + `wsl --shutdown`，无诊断
时两块均不出现）；② `pytest tests/test_wsl_bridge.py tests/test_overlay_core.py -q`
→ **95 passed / 1 skipped**；③ 全量 `pytest tests -q --ignore=tests/test_ast_inject.py`
→ **185 passed / 7 skipped / 1 failed**（唯一 failed 为 `test_vs_real_rec_merge_probes`
的既有环境差异：WSL 内 PyPI `podman-compose 1.6.0` 与仓库 vendored 快照在
`depends_on` list↔dict 归一化上不一致，本次改动前已存在，非回归）；④ **真机验证**：
`wsl.exe -d podman-machine-default -- true` 修复前返回 11、`wsl --shutdown` 后返回 0，
`inv xmnn.ps` 经 Windows 原生桥接执行成功（`✅ 已经 WSL 发行版 podman-machine-default
桥接执行`），随后 `inv xmnn.build --torch cu130` 正常进入镜像构建并拉取
`torch-2.14.0+cu130-cp314` wheel。

> **范围（已知未覆盖）**：本修复只让**诊断可见**，不改动桥接目标选择与重试策略——
> 探测失败仍一律门禁 Exit(1)，不做自动重置、不做多发行版轮询（`COMPOSE_WSL_DISTRO`
> 仍是唯一覆盖入口）。VM 层不可用态的成因（本次为长会话后 WSL 虚拟机进入异常态）
> 未做深挖，属宿主侧问题。

**C 同步**：代码 + 测试提交 `fix(client)` = `8b2ac964e`（`utils.py`/`overlay_core.py`/
`tests/test_wsl_bridge.py`/`tests/test_overlay_core.py`，4 文件，预防措施
`[prevent: wsl-probe-stderr-diagnosis]`）；文档提交 `docs(client)` = `586e44807`
（[rules/windows-wsl.md](rules/windows-wsl.md) §8 第 3 条、`docs/04-troubleshooting-guide.md`
W-I17、`docs/03`/`docs/README.md` 速查表范围、本文件）；本条 hash 回填为第三条
`docs(client)` 提交。

### 2026-09-20 · `fix:` `inv xmnn.up --gpu` 在 WSL2 失败——设备运行期门禁 + 自动探测 + 驱动库挂载（C19）

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session `sc-20260920-xmnn-up-gpu-fix`）。

**I 洞察（四元组）**：**现象**——`inv xmnn.up --gpu --skip-build` 在 WSL2 宿主
（`podman-machine-default`）exit 125，报 `Error: stat /dev/dri: no such file or directory`
（`podman-compose up 失败 (exit=125)`）；**根因**——C18 的 `--gpu` 只做「追加覆盖文件」
这一件事，对设备**是否存在毫无预检**，而 `compose.gpu.yaml` 的缺省值
`${GPU_DEVICE:-/dev/dri}` 是 **PCI 形态**假设；WSL2 发行版**没有 `/dev/dri`**，
只有 `/dev/dxg`（`crw-rw-rw- 10,258`）——缺省值直接把非法路径丢给 podman；
**影响**——`--gpu` 这一 opt-in 能力在本仓库最主要的落地场景（Windows 11 × WSL2）
100% 不可用，且报错是 podman 原生 stat 文本，用户无从判断该改设备还是改配置；
**建议**——opt-in 设备能力必须自带**运行期可用性门禁**，并按宿主实况自动选择形态。

**F 第一性原理**：① 设备能力是**运行期事实**而非**声明期事实**——能不能透传 GPU
取决于当下宿主有没有该设备，故判据必须在 `up` 执行时从 **podman 宿主侧**取得，
不能在编排期（Windows 原生本机）猜测；② 与 C15/C16 同构：**单一事实源**——
设备形态的解析只能有一个入口（`resolve_gpu_device`），compose argv 层不得再
分派；③ WSL2 的 GPU 栈是**两件东西**而非一件——`/dev/dxg`（设备）**加**
`libcuda.so.1`（驱动库，WSL 侧由宿主注入在 `/usr/lib/wsl/lib`），只给设备不给库，
`ctypes.CDLL("libcuda.so.1")` 依然失败（实测矩阵见下）；④ 库必须挂到**标准搜索路径**
（`/usr/lib/`）而非靠 `LD_LIBRARY_PATH`——compose 的 `environment` 是 **mapping 替换**
语义，一旦覆盖就冲掉栈原有的 TVM 库路径（`npu_tvm/build:build/vta:main/lib`）。

**V 对抗审查（四视角，均有实测支撑）**：① **魔鬼代言人**——"硬编码 `/dev/dxg`
不是更简单"：否决，本仓库同时面向 Intel/AMD（`/dev/dri`）与 NVIDIA CDI 用户，
硬编码会把 WSL2 的修复变成**其他所有平台的回归**；② **新人**——"挂整目录
`/usr/lib/wsl/lib` 更省事"：**实测失败**（该目录下库的依赖链解析不出来），
只有单文件挂载 `/usr/lib/wsl/lib/libcuda.so.1:/usr/lib/libcuda.so.1:ro` 成功；
③ **老板**——"加个 env 让用户自己设就行"：否决，缺省即失败等于把配置负担转嫁给
用户，而"缺什么"是可以自动探测的；④ **未来**——"设 `LD_LIBRARY_PATH` 会不会更稳"：
**实测失败且有害**——库路径能被冲掉，容器内 `printenv LD_LIBRARY_PATH` 会从
TVM 路径变成 `/usr/lib/wsl/lib`，故明确写入规则**禁止**。

**实测矩阵（`podman-machine-default` 内，`CDLL("libcuda.so.1")`）**：

| 配置 | 结果 |
|---|---|
| 无设备/库 | 失败 |
| 仅 `--device /dev/dxg` | 失败（缺库） |
| **`--device /dev/dxg` + 单文件挂载 `libcuda.so.1` → `/usr/lib/`** | **成功** |
| 挂整目录 或 仅设 `LD_LIBRARY_PATH` | 失败 |

**A 原子化实现**：内核 `overlay_core.py` 新增 `GPU_DEVICE_FORMS`（`/dev/dri` →
`/dev/dxg`，**顺序即探测优先级**）、`WSL_CUDA_LIB`、`gpu_override_file(spec, form)`、
`_runtime_path_exists` / `_runtime_cdi_available` / `_form_of_device`、
`resolve_gpu_device(c, spec, env) -> (token, form)`；`compose_argv`/`run_compose`/
`run_compose_up` 增加 `gpu_form` 参数（默认 `generic`，保持既有调用零改动）；
`up_stack()`/`smoke_stack()` 在 `gpu=True` 时调用解析并把 `form` 传入；
`up_help` 的 `--gpu` 文案改为按 `gpu_device_env` 生成双形态 + 探测顺序说明。
compose 侧新增 `overlays/xmnn-dev/compose.gpu.wsl.yaml` 与
`overlays/onnx-quantized/compose.gpu.wsl.yaml`（同构，service 名各异），
quant 的 `compose.gpu.yaml` 由硬编码 `- /dev/dri:/dev/dri` 改为单条
`- ${GPU_DEVICE:-/dev/dri}`（与 xmnn 同构）；`quant.py` 补
`gpu_device_env="GPU_DEVICE"` 与 `bridge_env_keys += GPU_DEVICE`（WSL 桥接只透传
环境变量、不转发 CLI 参数）。

**验收点**：① `pytest tests -q --ignore=tests/test_ast_inject.py` **182 passed /
1 skipped**（`-k "gpu or wsl"` 26 passed）——新增 C19 用例 9 例（form 分派与回退、
`/dev/dri` 自动探测、`/dev/dxg` 自动探测 + libcuda 缺失、无设备 fail-fast、
显式路径缺失 fail-fast、CDI 未生成 fail-fast、wsl form 贯通 compose argv、
quant 同内核路径、**不开 `--gpu` 绝不探测设备**）与渲染断言 2 例；② **真机验证**
（经 WSL 桥接）：`inv xmnn.up --gpu --skip-build` 日志显示自动选中
`compose.gpu.wsl.yaml`、`GPU /dev/dxg 已透传`、`EXIT=0`；容器内
`ctypes.CDLL("libcuda.so.1")` → `CUDA_LIB_OK`；`podman exec xmnn-dev ls /dev/dxg`
存在；`printenv LD_LIBRARY_PATH` 仍为 TVM 路径（未被污染）；③ quant 侧以
`podman-compose -f compose.yaml -f compose.gpu.wsl.yaml config`（EXIT=0）验证新文件
可解析（devices + libcuda 单文件 bind + `read_only` 均正确渲染）；④ 验证后
`inv xmnn.down` 清理，EXIT=0。

> **范围（已知未覆盖）**：真机验证在**无 CUDA 运行时**的镜像上进行（`CDLL` 成功
> 证明设备 + 驱动库通路可用，未跑实际 CUDA 算例——该镜像 `TORCH_FLAVOR` 为空）；
> `/dev/dxg` 之外的 WSL 变体（如自定义发行版）未逐一实测，按 `GPU_DEVICE_FORMS`
> 顺序探测即可覆盖常见形态。

**C 同步**：代码 + 测试提交 `fix(client)` = `34c2bbf83`（`overlay_core.py`/`quant.py`/
两个 `compose.gpu.wsl.yaml`/quant `compose.gpu.yaml`/两个测试文件，7 文件，
预防措施 `[prevent: opt-in-device-runtime-preflight]`）；文档提交 `docs(client)`
= `a946496c1`（13 文件：[rules/xmnn-overlay.md](rules/xmnn-overlay.md) §11.1.1·§11.1.2·§11.4、
[rules/quant-overlay.md](rules/quant-overlay.md) §3·§4、`docs/04-troubleshooting-guide.md`
W-I16、`docs/03`/`docs/README.md`/`docs/11` 速查表与说明、两个 overlay README 与
`.env.example`、`AGENTS.md` P0 清单 C19 与变更日志、本文件）。

### 2026-09-20 · `feat:` xmnn-dev 支持 GPU 可选透传与 torch 可选安装（C18）

**关联七概念场景**：场景5「创新突破」（R→F→V→I→C，session sc-20260920-xmnn-dev-gpu-torch）。

**R 事实**：改造前 `overlays/xmnn-dev` 无 `compose.gpu.yaml`、`XMNN_SPEC` 无 `gpu_override`，
镜像内既无 torch 也无 CUDA 运行时；`overlay_core.make_stack_tasks()` 的 `up`/`smoke`
是 `if spec.gpu_override / elif spec.supports_offline / else` **互斥分支**。
用户诉求（原话）：「支持 gpu 作为可选，且支持 torch-gpu」。

**F 第一性原理**：① 用户要的是**两种可选能力**而非两个默认行为——"可选"的判据是
**不开时与改造前逐字等价**（零设备透传、零 torch、离线契约不变），故开关必须是
opt-in 且默认关；② GPU 与 torch 是**正交维度**（前者是运行期设备透传，后者是构建期
依赖形态），不得互相耦合（如"装了 cu130 就自动开 GPU"）；③ podman-compose 的
`devices` 是**原样透传**的字符串列表（vendor `podman_compose.py` L1382-L1383 不做冒号
拆分），故"同时支持设备路径与 CDI 引用"只能靠**单条插值**承载两种形态，写成并列两条
必有一条非法；④ 构建期网络请求的目标（`download.pytorch.org/whl/<flavor>`）**不得由
用户输入任意拼接**，故 flavor 必须是白名单而非自由文本。

**V 对抗审查（四视角）**：① **魔鬼代言人**——"最优突破方向应否是独立 GPU 栈而非
xmnn 加开关"：否决，理由是新增栈需复制 12 件套且违背「默认隔离」承诺，而 GPU 与
torch 都是**既有栈的能力扩展**（对齐 quant 已实证的 `compose.gpu.yaml` 模式）；
② **新人**——"为什么 `devices` 不写成两条（`/dev/dri` + CDI）"：vendor 源码实证
devices 列表项原样下传为 `--device <item>`，两条并列时 CDI 形态必然 `stat` 失败；
③ **老板**——torch 装 base env（cp314 GIL）而非 main env：依 C13 双 ABI 不可互换 +
xmnn-runtime 既有先例，main env 是 free-threading，装 CUDA torch 会破坏 ABI 契约；
④ **未来**——"kernel 的互斥分支会怎样"：**已实证为真风险**——xmnn 同时声明
`gpu_override` 与 `supports_offline` 后，互斥分支让 `--offline`/`--no-offline`
被 gpu 分支吃掉，静默破坏 §10 离线契约。**采纳的修正**：① 内核重构为
**能力并集四路正交** + 公共 `_up_impl`（离线旗标固化必须先于 `gates()` 保留在
`_up_impl` 内）；② torch 层插在 mamba 工具链层之后、`COPY builder` 之前，
使 ~2GB wheel 层不被 builder 变更失效；③ 用单一脚本 + 早期单文件 COPY 承载安装逻辑，
规避「RUN 行不写内层引号 `python -c`」的既有约定。

**I 洞察落地（设计裁决，均已用户确认）**：① torch 形态 = 构建期可选默认不装
（`TORCH_FLAVOR` / `--torch`，白名单 `""|cpu|cu130`）；② GPU 形态 = 复用 `GPU_DEVICE`
双形态（`/` 开头=设备路径，否则=CDI 引用），与根 `invoke run --gpu` 同键同语义；
③ flavor **不参与镜像 tag**（沿用 `XMNN_IMAGE_TAG`，一 tag 一形态）。

**A 原子化实现**：内核 `overlay_core.py`（`TORCH_FLAVORS` 白名单 + `StackSpec` 三新字段
`gpu_device_env`/`torch_flavor` + `resolve_build_args(torch=)` + `build_image` 透传 +
`up_stack` 双形态提示 + `make_stack_tasks` 能力并集四路正交）、栈声明 `tasks/xmnn.py`
（`gpu_override`/`gpu_device_env`/`torch_flavor` + bridge_env_keys 加 `TORCH_FLAVOR`/`GPU_DEVICE`）、
`overlays/xmnn-dev/compose.gpu.yaml`（新建，单条 `${GPU_DEVICE:-/dev/dri}`）、
`compose.yaml`（`TORCH_FLAVOR` build-arg）、`Containerfile.xmnn-dev`（Layer 2.5 + LABEL +
横幅）、`builder/scripts/install-torch.sh`（新建）、`smoke/_toolchain_guards.py`（§8 声明 vs 实物）。

**验收点**：① `pytest tests -q --ignore=tests/test_ast_inject.py` **170 passed / 1 skipped**
（较 C17 基线净增 4 例：`test_build_args_torch_flavor_whitelist`、
`test_build_task_argv_xmnn_torch_flavor_flows`、`test_xmnn_gpu_override_is_opt_in_and_single_device`、
`test_xmnn_gpu_device_double_form_interpolation`；另有 4 例黄金清单/签名同步改写）；
② 渲染断言锁定「默认零透传 + `--gpu` 追加单条设备 + `GPU_DEVICE` 三种取值」；
③ 白名单非法值（`cu129`）解析期 `Exit(1)`。

> **范围（已知未覆盖）**：镜像未重建，torch 安装与 CUDA 可用性未做容器内端到端实测
> （`install-torch.sh` 的索引可达性与 wheel 体积需在有网侧 `inv xmnn.build --torch cu130`
> 时验证；构建期守卫 §8 会在那时给出「声明 vs 实物」结论）。GPU 路径未做真机透传实测
> （需宿主具备 `/dev/dri` 或 CDI 配置）。

**C 同步**：已提交（代码侧 `feat(client)` = `086d3a998`，11 文件；文档侧 `docs(client)` = `11c926f62`，8 文件；本条 hash 回填为第三条 `docs(client)` 提交）。

### 2026-09-18 · `fix:` `up` 输出收敛——过滤 podman 原生回显噪声（C17）

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session sc-20260918-terminal-echo）。

**R 事实**：用户实测 `invoke xmnn.up --offline`（Windows 原生 → WSL 桥接）一屏被 4 行 podman 原生行冲散：① `2096d7b4…`、② `d3f33bf7…`（两行裸 64 位对象 ID）、③ `xmnn-dev`（裸容器名）、④ `ERROR[0001] failed to move the rootless netns pasta process to the systemd user.slice: dbus: couldn't determine address of session bus`。scratch 项目真机复现：`up` stdout = N×64-hex + 容器名，stderr = podman 原生错误；`down` stdout = 容器名×2 + pod ID + `_default` 网络名。

**I 洞察（四元组）**：**现象**——编排层中文提示被 podman 原生回显切碎，`ERROR` 一行尤其像真故障；**根因**——vendor `podman_compose.py` L1907 在无 `log_formatter` 时以 `close_fds=False` 执行 `asyncio.create_subprocess_exec`，podman 子进程**继承 stdio** 直通终端，而仓库侧 `run_compose()` 是裸转发、无过滤层；且 podman-compose **无全局静默旗标**（`-q/--quiet` 语义恰为「只显示容器 ID」，反而更多 ID）；**影响**——用户无法区分「良性回显」与「真实错误」（第 ④ 行是宿主无 systemd 用户会话总线时的良性提示，容器照常创建）；**建议**——在 `podman-compose` 进程边界捕获输出并按白名单过滤。

**F 第一性原理**：① 噪声的**生产者**是 podman，`podman-compose` 只是透明管道——要收敛只能在**唯一可控边界**（子进程 fd）拦，靠 podman-compose 自身开关无解；② 过滤必须是**白名单**而非黑名单：终端可信度优先，无法确证良性的行一律保留（黑名单漏掉一种噪声只是难看，白名单误杀一条真错误则是信任事故）；③ 失败路径的信息完整性**高于**美观——非零退出码时必须零过滤。

**V 对抗审查（四视角）**：① **魔鬼代言人**——"过滤会不会吞掉真错误"：白名单三式均为**整行全等/全匹配**，且失败路径零过滤 + 退出码透传（`Exit(code=rc)`），单测含 4 条反例（netavark 真错误、含项目名的上下文行、非 64 位 hex、dbus 换理由）；② **新人**——"`-q` 不是更省事"：`-q` 语义相反，已实证否决；③ **老板**——零命令面变化、零 compose 变化，仅 `up_stack()` 一行调用改道 + 内核新增纯函数；④ **未来**——"podman 升级后新增良性回显怎么办"：判据集中在 `is_benign_compose_noise()` 单点，新增一类只需加一行正则 + 一例反例断言。

**实现（A 原子化）**：`overlay_core.py` 新增 `_COMPOSE_ECHO_ID_RE`、`_PASTA_DBUS_NOISE_RE`、`compose_echo_names()`、`is_benign_compose_noise()`、`run_compose_up()`；`up_stack()` 起容器由 `run_compose()` 改走 `run_compose_up()`。白名单三式：① 整行恰为 64 位十六进制；② 整行与 `compose_echo_names(spec)`（容器名 / `pod_<project>` / `<project>_default`）全等；③ pasta-user.slice-dbus 行。命中时打印 `ℹ 已过滤 N 行 podman 原生回显噪声`。

**验收点**：① `pytest tests -q --ignore=tests/test_ast_inject.py` **166 passed / 1 skipped**（较 C16 基线净增 4 例：`test_is_benign_compose_noise_whitelist_only`（含 4 反例）、`test_run_compose_up_filters_echo_noise`、`test_run_compose_up_failure_prints_raw_and_exits`（零过滤 + `Exit.code == 125`）、`test_up_stack_captures_compose_up_output`（断言 `hide=True, echo=False, pty=False`））；② 真机经 WSL 桥接实测：`invoke xmnn.up --offline`（幂等路径）过滤 **1 行**、`invoke quant.up --skip-build`（真实新建路径）过滤 **3 行**，栈可用，随后 `invoke quant.down` 清理完毕。

> **范围（已知未覆盖）**：仅 `up` 应用过滤；`down`/`ps`/`logs`/`exec` 保持原生输出——实测 `invoke quant.down` 仍有同类 3 行噪声（`onnx-quantized`×2 + 1 行裸 hex），如需收敛另行提案。用户截图顶部 `WSL 桥接命令失败（exit=1），详见上方输出` 位于提示符**之上**，判定为**上一命令遗留**，本轮未改。

**C 同步**：代码 + 测试提交 `fix(client)`（`overlay_core.py` + `test_overlay_core.py`，预防措施 `[prevent: podman-raw-echo-noise]`）；文档提交 `docs(client)`（[rules/invoke-tasks.md](rules/invoke-tasks.md) §5 C17 + §6 测试现状、`docs/02-invoke-reference.md` C17 契约段、`AGENTS.md` P0 清单与变更日志、本文件）。

### 2026-09-18 · `fix:` 终端三项噪声 + Nuitka 升 4.2.1（I→F→V→C，session sc-20260918-terminal）

**关联七概念场景**：场景2「问题解决」（I→F→V→C）。

**R 事实**：`invoke xmnn.wheel` 终端有四类噪声：① `Exception ignored while flushing sys.stdout: BrokenPipeError: [Errno 32] Broken pipe`；② `4.1.3` / `Commercial: None` 两行裸输出（未走 `log_kv` 排版）；③ `Nuitka-Options:WARNING: Using module mode specific option '--no-pyi-file' has no effect...`；④ `Nuitka:WARNING: The Python version '3.14' is only experimentally supported by Nuitka '4.1.3'`。

**I 洞察（四元组）**：**现象**——打包日志被四类非错误信息污染；**根因**——① `build-wheel.sh` 版本行以 `"$BASE_PYTHON" -m nuitka --version | head -2` 截断 **Python 生产者**的管道，消费者提前退出后 Python 侧 flush 触发 EPIPE；② 同一行原样透传 stdout，未走 `log_kv` 的 `%-22s` 排版；③ Nuitka 4.x 里 `--module` 是遗留别名，只置 `options.module_mode`，而 `_warningModuleModeOnlyOption()` 的判据是 `options.compilation_mode`（仅 `--mode=module` 赋值）；④ 4.1.3 的 `getSupportedPythonVersions()` 止于 `3.13`；**影响**——真实告警被噪声淹没、日志不可扫读、每次打包都刷屏；**建议**——管道改 `awk` 读尽后再格式化、旗标改 `--mode=module`、Nuitka 升 4.2.1。

**F 第一性原理**：① 终端的「版本行」本质是**一条已经是单行的 KV 记录**，其生产者是 Python 进程——任何在中间掐断生产者管道的消费者（`head`）都会让写端 EPIPE，故应让消费者**读尽全流**再决定输出什么（`awk` END 块天然如此）；② 旗标有效性的判定权在**选项解析层**，不在调用者意图——调用者以为 `--module` 就是 module 模式，但解析层用另一个字段做判据，故必须以解析层字段为准。

**V 对抗审查（四视角）**：① **魔鬼代言人**——"升 Nuitka 是不是为了一条 WARNING 冒重建镜像的风险"：本地容器（`podman run --rm localhost/xmnn-dev:latest`）实测 4.2.1 可装、`--version` 首行 `4.2.1`、`getSupportedPythonVersions()` 含 `3.14`，且升级同时消除实验性警告；代价是需在**有网侧**重跑 `inv xmnn.build`（镜像内 `/opt/xmnn-builder` 与 base env 均为烤入层，非 bind）；② **新人**——"为何不直接删 `--no-pyi-file`"：删了会重新产出 `.pyi` 文件，是语义倒退，改旗标是唯一正解；③ **老板**——零命令面变化、零 compose 变化，三处旗标替换 + 一行 pin；④ **未来**——"`--mode=module` 会不会改变产物"：同机对拍 `--module` vs `--mode=module` 编译同一模块，产物文件名与可导入性完全一致（均为 `pkgprobe.cpython-314-x86_64-linux-gnu.so`，`import pkgprobe` 均得 `value=1`），且新增守卫断言 `sys.version_info[:2] in getSupportedPythonVersions()`，未来升解释器时构建期即失败而非运行时刷警告。

**实现（A 原子化）**：① `builder/scripts/build-wheel.sh`：版本行改 `awk 'NR==1{v=$0} /^Commercial:/{c=$0} END{...}'` 走 `log_kv`（同时消解 BrokenPipeError 与排版；只取版本与 `Commercial:` 行，避开 4.2+ 第 2 行的非确定性 `Update status: ... (cached, N seconds old).`）；三处 `--module` → `--mode=module`；文件头注改 4.2.1；② `builder/scripts/install-build-deps.py`：`nuitka==4.2.1`（pin 单一事实源）；③ `Containerfile.xmnn-dev`：LABEL `org.specweave.nuitka="4.2.1"`、Layer 3 末尾去掉 `| head -2`、完成横幅改 4.2.1；④ `smoke/_toolchain_guards.py`：断言改 4.2.1 + **新增**「运行解释器在 `getSupportedPythonVersions()` 内」守卫（§3）+ docstring/结尾消息同步；⑤ 文档同步：client `AGENTS.md` C12、rules/xmnn-overlay.md（ABI 表 + `--mode=module` 新条款）、rules/xmnnrt-overlay.md、docs/11、.env.example、三处 overlay README、`tasks/xmnn.py`、`tasks/__init__.py`、根 `.agents/skills/compose-overlay-ops/SKILL.md`。

**验收点（容器内实测，`localhost/xmnn-dev:latest` + `--entrypoint /bin/bash` 隔离跑）**：① 升级后 `--version` 首行 `4.2.1`，`getSupportedPythonVersions()` = `('2.6'...'3.13','3.14')`，运行解释器 `3.14` 在列 → 实验性警告消除；② 旗标探针：`--module --no-pyi-file` WARNING 2 条（含 `'--no-pyi-file' has no effect`），`--mode=module --no-pyi-file` 1 条（该条消失，剩下的是裸探针未 `--include-package` 的固有提示）；③ 版本行：旧写法 `| head -2` 实测 1 次 `BrokenPipeError`，新写法 0 次，且经 `log_kv` 输出稳定单行 `nuitka                 4.2.1 (Commercial: None)`（连跑三次一致）；④ 补丁后 `_toolchain_guards.py` 全量跑 `exit=0`，新增断言 `[OK] 运行解释器 3.14 在 Nuitka 支持列表内`；⑤ `bash -n build-wheel.sh` 通过。

> **未做**：`build-wheel.sh` 全流程跑（需先 `build-tvm` 产出 libtvm.so，本次宿主 `workspace/npu_tvm/build/` 无该产物，全流程约需 20-40 分钟），故本轮未复现真实端到端打包；改旗标对产物的等价性以「同机同模块对拍产物文件名 + 可导入性一致」佐证。**镜像未重建，改动尚未在 `invoke xmnn.wheel` 路径生效。**

**C 同步**：代码侧提交 `375189b68`（`fix(client)`，4 文件：build-wheel.sh / install-build-deps.py / Containerfile.xmnn-dev / _toolchain_guards.py）——预防措施 `[prevent: pipe-producer-truncation]`（版本行禁 `head` 掐断 Python 生产者）+ `[prevent: nuitka-supported-python]`（构建期守卫拦截解释器不在支持列表）。规则固化于 [rules/xmnn-overlay.md](rules/xmnn-overlay.md) §打包契约新增「模式旗标必须写 `--mode=module`」条款。**待用户在有网侧重跑 `inv xmnn.build` 重建 xmnn-dev 镜像使修复生效**（`/opt/xmnn-builder` 与 base env 均为烤入层）。

### 2026-09-18 · `fix:` 构建执行者唯一——`up` 恒 `--no-build`，消除双构建（C16，方案 B 治本）

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session sc-20260918-client-build-up，commit aa47257b2 + fc2df0e27；F/V 承 C15 同一会话，本条为残留项收口）。

**R 事实**：① `compose_up_tail(offline)` 原为 `["up","-d","--no-build"] if offline else ["up","-d"]`——非离线路径无 `--no-build`；② vendor `podman_compose.py` L4098 为 `if not args.no_build:`，即 `up` 默认对含 `build:` 段的服务执行构建；③ 故一次非 `--skip-build` 的 `invoke x.up` 会构建两次（内核 `build_image()` + compose 段）；④ `--skip-build` 只跳过内核那次，compose 段仍构建，语义名不副实；⑤ `up_stack()` 的镜像存在性预检原以 `if offline:` 为条件，非离线路径完全无预检。

**I 洞察（四元组）**：**现象**——`up` 存在不可见的第二次构建，`--skip-build` 不"跳过构建"；**根因**——`up` 的本质职责是「保证镜像存在」+「启动容器」，而「构建」这一职责被分给了**两个执行者**；C15 只对齐了两者的**参数**（消除白重建），未消除**执行者本身**；**影响**——多一次构建调用与潜在整层缓存失效、compose 那一半看不到 CLI 旗标、时点在内核之后、离线场景破网风险；**建议**——执行者唯一化：镜像存在性只由内核负责，compose 恒 `--no-build`。

**F 第一性原理**：职责正交分解下「谁负责使镜像存在」只能有**一个**答案。两个执行者必然带来三重不可见性——参数不可见（compose 读不到旗标）、时点不可见（compose 在内核之后）、失败不可见（两边都可能构建失败且报错形态不同）。选定 B2 而非 B1（`no_build` 仅在离线为真）：既然要唯一化，就不该保留一条"看情况由 compose 兜底"的隐式分支。

**V 对抗审查（四视角）**：① **魔鬼代言人**——"`--skip-build` 首次使用会 fail-fast 是否过于激进"：是，但 fail-fast 文案给出两条可执行出口（`x.up` 随带构建 / `x.build && x.up --skip-build`），且全仓 grep 证据表明 `--skip-build` 用法**一律与「已有镜像」共现**（`docs/10:15` 两步路径、`docs/04` W-I8/W-I10/W-I12 恢复路径、`overlays/onnx-quantized/README.md:65`「已有镜像 + GPU 推理」），无任何路径依赖 compose 兜底；② **新人**——"compose 的 `build:` 段成了死代码"：确实在 invoke 路径不再被消费，故在 `docs/02` 与 `docs/10`-`13` 明确其「仅服务裸 `podman-compose` 路径」；③ **老板**——收益是每次 `up` 少一次构建调用与潜在的层缓存失效风险，成本仅一处语义变更 + 一处 `not_running_hint` 文案；④ **未来**——四栈全部经 `make_stack_tasks` 工厂或 `up_stack` 收敛，新栈自动继承，无遗漏点。

**实现（A 原子化）**：① `compose_up_tail()` 去 `offline` 形参、无分支恒返 `["up","-d","--no-build"]`；② `up_stack()` 预检条件 `if offline:` → `if skip_build:`（覆盖 `--skip-build` 与离线两条路径）；③ `_require_local_image()` 增必填关键字 `offline` + 双分支文案（离线指 `save`/`load`，非离线指 `up`/`build && up --skip-build`）；④ `monetize.py` 的 `not_running_hint` 改指默认路径（`--skip-build` 现要求镜像已存在，长任务前置提示不保证）；⑤ 四个栈的 `skip-build` help 文案同步；⑥ 测试：新增 `test_up_inline_build_runs_exactly_once`（断言 `build` 恰一次）与 `test_up_skip_build_without_local_image_exits_with_guidance`（断言 Exit 1 + 指引 + 未起容器），`test_compose_up_tail_adds_no_build_offline` 改写为 `test_compose_up_tail_always_no_build`，`test_up_offline_missing_image_exits` 补 capsys 文案断言。

**验收点**：`python -m pytest tests -q --ignore=tests/test_ast_inject.py` → **162 passed / 1 skipped**（较 C15 基线 160 净增 2 例）；安全性依据 `image_tag(spec, env)` 与 compose 的 `${PREFIX}_IMAGE_TAG:-默认}` 同键同默认，tag 不漂移。

**C 同步**：预防措施 `[prevent: single-build-executor]`——`invoke x.up` 恒 `up -d --no-build`，镜像存在性只由内核 `build_image()` 负责；`--skip-build`/`--offline` 必须先过本地镜像存在性预检。规则固化于 [rules/invoke-tasks.md](rules/invoke-tasks.md) §5 新增 **C16**、`AGENTS.md` P0 清单 C16 与 C12 离线条款修订、[docs/02-invoke-reference.md](../docs/02-invoke-reference.md) §参数契约 C16 段、`docs/10`-`13`、[rules/xmnn-overlay.md](rules/xmnn-overlay.md) §10（纠正已失效的 `compose_up_tail(offline=True)` 签名引用）、[rules/xmnnrt-overlay.md](rules/xmnnrt-overlay.md) §3、`.env.example` 与四 overlay README。

### 2026-09-18 · `fix:` 构建参数单一事实源——`up` 内联构建与 compose 段同键（C15），消除换源后白重建

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session sc-20260918-client-build-up，commit aa47257b2 + fc2df0e27）。

**R 事实**：① `up_stack` 内联构建硬编码 `pip_mirror="official"` / `conda_mirror="official"` / `base_image=spec.default_base_image`，而 `overlays/*/compose.yaml` 的 `build.args` 读**无前缀** `${PIP_MIRROR:-official}` / `${CONDA_MIRROR:-official}` / `${BASE_IMAGE:-...}`（即 root `.env` 同一批键）——两条路径参数源不同；② podman-compose 的 `up` 默认对含 build 段的服务执行构建，故 `up`（非 `--skip-build`）会构建两次；③ `docs/10`、`docs/11` 用裸 `up`，`docs/12`、`docs/13` 用 `up --skip-build`，同一契约两种写法；④ `overlays/xmnn-dev/README.md:234` 与 `agent-monetize-dev/README.md:73` 明写"独立 build 只认 CLI 旗标、.env 只对 compose 生效"——与事实相反。

**I 洞察（四元组）**：**现象**——按文档 `invoke x.build --pip-mirror tuna && invoke x.up` 会全量白重建；**根因**——build-arg 有**三个来源**（CLI 旗标 / 内核硬编码 / compose 插值）而**无单一事实源**，任一来源变化即改变 build-arg、使构建层缓存整体失效；**影响**——apt/mamba/pip 重新下载，虚拟机上是分钟到十分钟级空耗，且症状（"改了源反而更慢"）不指向根因；**建议**——把三个 build-arg 收敛到与 compose 段天然同键的无前缀 `.env` 键，内核单点解析。

**F 第一性原理**：构建参数的正交分解只有「**值从哪来**」与「谁消费」两问；消费方有三个（invoke build / invoke up 内联 / compose），故值来源必须唯一且对三方可见——CLI 旗标天然只对第一个可见，**只有 `.env` 同时对三方可见**。

**V 对抗审查（四视角）**：① **魔鬼**——"删掉 `up` 内联构建岂不更彻底"：否，内联构建承担"改了 Containerfile 即时生效"，且 `--skip-build` 只是跳过内核那次、compose 段仍会构建，删除会让语义更混乱；② **新人**——"为何不改 compose 段去读 CLI"：compose 是子进程、看不到旗标，方向不可行；③ **老板**——零命令面变化、零 compose 改动（黄金快照不动），仅内核 + 一个长任务签名；④ **未来**——"CLI 旗标会不会变成陷阱"：会，故在帮助文本、`docs/02`、四个 overlay 文档、两处 `.env` 模板中统一标注「跨三处一致必须写 `.env`，旗标只覆盖单次」。

**实现（A 原子化）**：① 内核新增 `resolve_build_args()`（单点解析，优先级 `CLI 旗标 > shell export > .env > 默认值`）；② `build_image()` 三个 build-arg 参数改 `Optional[str] = None` 并内联解析；③ `up_stack()` 内联构建不再传死值；④ `make_stack_tasks()` 的 `build` 默认值改 `None`、`xmnnrt.build` 长任务同步（去掉 `spec.default_base_image` 硬默认）；⑤ 帮助文本与 `skip-build` 说明改述为"读 .env 同键"；⑥ 测试：harness 增加 `PIP_MIRROR`/`CONDA_MIRROR`/`BASE_IMAGE` 清空（防宿主环境污染黄金断言）+ 4 例新断言（up 内联构建读 env、build 默认跟随 env、无 env 回退默认、CLI 旗标优先）。

**验收点**：`python -m pytest tests -q` → **160 passed / 1 skipped**（非 bash 模块；`test_ast_inject.py` 8 例需 WSL2/Linux 的 bash，Windows 原生失败不构成本次回归）；未设 `.env` 键时 build argv 与旧行为逐字一致（黄金快照零变化）；`docs/10`、`docs/11` 的示例改为 `.env` + `build` + `up --skip-build` 两步路径。

**C 同步**：预防措施 `[prevent: single-source-build-args]`——build-arg 只允许经 `overlay_core.resolve_build_args()` 解析，禁止任何调用点硬编码 `"official"` / `spec.default_base_image`；规则固化于 [rules/invoke-tasks.md](rules/invoke-tasks.md) §5 新增 **C15**、`AGENTS.md` P0 清单 C15、[docs/02-invoke-reference.md](../docs/02-invoke-reference.md) §参数契约，四个 overlay 文档与 `.env` 模板同步（含撤销"独立 build 只认 CLI 旗标"的错误陈述）。

### 2026-09-18 · `fix:` `inv xmnn.wheel` 在 rootless + 同步树 POSIX ACL 下 EINVAL（字节级备份 / 原 inode 回写 / autolibs `cp -R`）

**关联七概念场景**：场景2「问题解决」（F→V→C→R→I→E，强制 V 门）。

**R 事实（G1 摘录）**：`inv xmnn.wheel` 稳定 exit 1，止于 `cp: preserving permissions for '/workspace/npu_tvm/python/tvm/__init__.py.bak_tvm.tmp.<pid>': Invalid argument`（3 次复现，3 个泄漏 tmp）；宿主 `/media/pc/data` 为 XFS 直接 bind（非 SMB/FUSE）；uid_map 仅 `0→1006`+subuid 段；源码文件属主 codesrc(1001) 容器视角 65534，宿主 ACL 含 `user:1000(pc)`/`user:1006(ai)` 具名条目；容器内 raw `system.posix_acl_access` 出现 id=-1（未映射）条目；**普通 cp 成功、`cp -p` 在 bind 树与容器 overlayfs `/tmp` 双双 EINVAL**，而手工 chown/chmod/utime 全成功；`cat 备份 > 原文件` 保持 inode/属主/777/ACL 不变。

**I 洞察（四元组）**：① **陈述**——失败本质不是「挂载 FS 不支持保留权限」，而是 GNU cp 把源文件含未映射 UID 的 ACL 原样写到任意目标，内核 setxattr 拒 EINVAL；**证据**——同错在容器原生 /tmp 复现、手工元数据系统调用全成功；**反常识**——锅不随目标 FS 走而随源文件元数据走；**行动**——备份去 `-p`。② **陈述**——`mv` 还原用新 inode 替换源码文件，属主 1001→1006、mode 777→775、ACL 全漂移，违背「零修改」；注入本身却是保 inode 的截断写；**反常识**——「原子 mv 更安全」只防半写内容却破坏元数据身份，非原子内容回写反而更忠实且四态矩阵本就覆盖截断残留。③ 自愈状态机漏「tmp 泄漏态」（set -e 下 cp 失败永不清理）。④ 故障随宿主 uid 拓扑偶联（主机用户恰为 uid 1000 的机器上 `-p` 反而成功），构建机难发现。

**F 第一性原理**：备份的唯一本质是「持有原始字节供回写」，位置/属主/ACL 皆无关；注入-还原周期必须保持外部 inode 身份不变；容器内构建对宿主 uid/ACL 拓扑零假设。

**V 对抗审查（四视角）**：① **魔鬼**——攻击「cp -a 只有一处吗」：全 overlay 排查坐实第二故障点 `CMakeLists.txt` autolibs `cp -a`（同源 EINVAL，不修则 Nuitka 编译十余分钟后必在 wheel 组装阶段失败，实测 `cp -R` 内容等价 exit 0）；`install(DIRECTORY USE_SOURCE_PERMISSIONS)` 只 chmod 模式位不复制具名 ACL，保留；② 内容回写非原子→保留「cat 成功才 rm 备份」，失败留 bak 交四态矩阵收敛（与既有 Python in-place 截断写风险同级）；③ stale tmp 清扫 glob 带完整绝对路径+tag 前缀，跨包不误伤；④ **新人**——禁令写进脚本头注/规则/C12，防后人改回 `-p`；⑤ **老板**——零命令面、零 compose 变化，1 shell 库 + 1 CMake 注释级改动 + 10 例 daemon-free 单测；⑥ **未来**——模式固化为「bind 树元数据复制禁令」。

**实现（A 原子化）**：① `builder/scripts/lib/ast_inject.sh`：备份改普通 `cp`（失败即清 tmp 并 return 2）、入口幂等清扫同 tag 陈旧 `.tmp.*`、`ast_restore` 改 `cat backup > init` 原 inode 内容回写（回写失败保留备份）；② `builder/CMakeLists.txt`：autolibs `cp -a`→`cp -R`（注释说明 wheel 不携带 ACL/属主）；③ 新增 `tests/test_ast_inject.py` 10 例（往返字节/inode/mode 一致、四态矩阵、tmp 清扫、失败无残留、tag 隔离、双周期幂等、静态守卫禁 `cp -p/-a`）；④ 闭环文档：规则 xmnn-overlay.md §5（AC-9 扩为内容/属主/模式/ACL 四不变 + CMake 禁令）、AGENTS C12、overlay README 排障双行（旧镜像报 EINVAL 的重建指引 + tmp 自动清扫）。

**验收点**：`pytest tests -q` → 158 passed / 7 skipped（新增 10 例全绿；2 个存量失败与本次无关：`.env.example` CRLF、podman-compose depends_on list/dict 合并，已另行报告）；真机 `inv xmnn.build` 重建镜像后 `inv xmnn.wheel` 端到端产出 whl（含 CMake 组装阶段）；外部源码树 `git status` 干净、无 `.bak*`/`.tmp.*` 残留。

**C 同步**：预防措施 `[prevent: no-metadata-copy-on-bind-tree]`——容器内对宿主 bind 树一律「备份只复制字节、还原写回原 inode、组装用 cp -R」，规则固化于 [rules/xmnn-overlay.md](rules/xmnn-overlay.md) §5 与 P0 清单 C12，daemon-free 静态守卫防回退。

### 2026-09-17 · `fix:` 清扫运行时依赖计数的陈旧文案（19 → 动态表述）

**背景**：真机构建期 §7 守卫实测 `[project].dependencies` 为 **20 条**，而仓库内 8 处文案仍写「19 个」；`install-build-deps.py` 实为动态读取该清单、并无 19 的硬编码逻辑，故该数字纯属陈旧漂移（清单增补依赖时无人同步散文）。8 处统一改为「pyproject 声明的全部运行时依赖」，Containerfile Layer 3 注释显式注明"数量随清单变化，勿在此硬编码"。

**C 同步**：预防措施 `[prevent: no-hardcoded-dep-counts]`——易漂移的计数不进散文，改由单一事实源表达（`builder/pyproject.toml` 为唯一清单 + §7 守卫构建期实测并打印实际条数）。

### 2026-09-17 · `refactor:` xmnn-dev 固化为两个过程——镜像构建（有网）/ 离线开发（无网）+ 构建期离线完备性守卫

**关联七概念场景**：场景3「重构优化」（I→F→V→A→C，session sc-20260917-xmnn-dev-two-phase，commit 26eaa00ca）。

**I 洞察（四元组）**：**现象**——离线能力散落在 CLI 开关上，镜像是否真的自足没有任何构建期证据（`build-wheel.sh` 已读 `XMNN_OFFLINE`，`build-tvm.sh` 却完全无离线语义）；**根因**——镜像构建期（有网）与容器内开发期（本该无网）从未被显式建模为两个过程，于是「过程二需要的东西是否已在过程一固化」这一问题从未被追问、也未落到任何断言，离线是按脚本零散补的而非契约驱动的；**影响**——缺口只在无网机器上暴露，而那里**没有补救手段**（apt/pip 均需网），故障点与修复点跨机器分离，是排障成本最高的一类；**建议**——把两阶段写成契约，并把「镜像自足」变成构建期可执行的断言。

**F 第一性原理（三条公理）**：**A1** 离线承诺的等价物是**镜像自足性**——过程二一切"首次运行才补齐"的路径都使承诺失效；**A2** 断言必须能在无网侧执行（守卫自身不联网、不装包），否则守卫成为新的离线缺口；**A3** 两个过程之间只有单向传递（镜像归档 + 使用者自备源码树）→ **所有校验必须前移到有网侧**。

**V 对抗审查（四视角）**：① **魔鬼**（攻击核心断言"镜像真的自足吗"）——逐行核查过程二三个脚本后确认 `build-tvm.sh`（invoke config/cmake/ninja/gcc）、`build-wheel.sh`（`python -m build --no-isolation` + Nuitka 旗标置空）、`verify-wheel.sh`（bundled ensurepip + 本地 whl `--no-deps` + 不升级 pip）均无对外请求，故自足性缺口**不在脚本层而在"无断言"层**，守卫即为该断言；② **新人**——"缺依赖该在哪补"答案唯一化为"回过程一"，消除无网侧手工 pip 的歧义（W-I14 同步说明依赖缺失是过程一缺陷）；③ **老板**——改动零命令面变化（仍 10 任务），仅脚本 + 守卫 + 文档；④ **未来**——把「两阶段 + 单向传递」写成不变量而非一次性排查经验，新增过程二脚本时按 §10 检查联网点。

**实现（A 原子化）**：① 守卫扩展 `smoke/_toolchain_guards.py` **§7「离线完备性」**——断言 gcc/g++/ccache/cmake/ninja/make/patchelf/readelf 在**显式构造**的 `/opt/conda/bin:/opt/conda/envs/main/bin:$PATH` 上可解析、`pyproject [project].dependencies` 声明的全部运行时依赖已装（**单一事实源**，用发行版元数据判定以避开 dist→import 名映射）、打包工具链已装；随构建期 root/devuser 双身份执行自动获得双覆盖，**不新增第二个守卫入口**。② `build-tvm.sh` 补离线语义：脚本头声明"全本地、无对外请求"，3rdparty 子模块缺失时按 `XMNN_OFFLINE` 给出"须在联网侧检出后随源码携带"的指引。③ `verify-wheel.sh` 头注声明无联网点。④ Containerfile Layer 5 注释与 BUILD COMPLETE 横幅标示 `offline: phase-2 全离线`。⑤ 文档：overlay README 新增「两个过程」章节（原「离线模式」更名并改写为过程一/过程二）+ 路径一命令块按过程分组 + 排障行标注子模块属过程一预备；`docs/11` 与 W-I14 同步；规则 §10 新增三条契约（两阶段 / 守卫实测 / 阶段二无联网点证据）、§8 说明守卫不另设入口；AGENTS C12 与路由表、P0 清单同步。

**验收点**：`pytest tests -q` 无回归（本次为容器内脚本 + 守卫 + 文档改动，Python 编排侧零变化）；守卫 `py_compile` 通过；check-links 无新增断链；镜像重建后 Layer 5 应打印 §7 全 `[OK]`（离线自足即过程一的验收条件，真机 `xmnn.build` 待跑）。

**C 同步**：预防措施 `[prevent: phase1-self-sufficiency-guard]`——把"离线能不能用"从运行期问题转为构建期断言，缺口结构性前移到有网侧；规则固化于 [rules/xmnn-overlay.md](rules/xmnn-overlay.md) §10 三条与 P0 清单 C12。

### 2026-09-17 · `feat:` xmnn.\* 离线模式——镜像归档 save/load + `XMNN_OFFLINE` 全链路禁网

**关联七概念场景**：场景5「创新突破」（F→V→I→C，session sc-20260917-xmnn-dev-offline，commit 8dfd99578）。

**背景与缺口四层**：① 栈侧无任何离线语义——无网机器上 `xmnn.up` 会静默尝试联网并留下难懂的构建报错；② 无 xmnn 自己的镜像归档出口/入口（离线机器拿不到镜像）；③ 容器内打包存在隐藏联网假设——numpy/scipy 走 pip 兜底、Nuitka 三处 `--assume-yes-for-downloads`、`build-wheel.sh` 无条件改写 pip 镜像；④ 从零构建镜像需 apt/mamba/pip 三段联网，**明确不在范围内**（越界承诺会误导使用者）。

**F 第一性原理（四条公理）**：A1 离线 = 栈侧动作不发起对外网络请求；A2 制品必须可由外部载体携带并校验；A3 离线判定须单一事实源且必须透传进容器；A4 离线失败必须 fail-fast + 中文可执行指引，不做静默降级。

**V 对抗审查（两处关键修正）**：**V-1**——WSL 桥接只透传 `bridge_env_keys` 中的环境变量、**不转发 CLI 参数**，若 `--offline` 不先固化为 `os.environ[XMNN_OFFLINE]`，桥接后即丢失（故 `resolve_offline()` 必须在 `gates()` 之前调用并回写，且 `bridge_env_keys` 必须含该键）；**V-2**——podman-compose 源码（`podman_compose.py` L4098 `if not args.no_build:`）表明 **`up` 默认对含 build 段的服务执行构建**，仅 `--skip-build` 不足以禁网，离线必须同时追加 `--no-build`。

**实现（I 落地）**：① 内核 `overlay_core.py` 新增 `StackSpec.supports_offline` / `offline_env_key` 声明、`resolve_offline()`（三态复用 `_resolve_bool`，显式开 > 显式关 > `.env` > 默认）、`offline_exec_env()`、`compose_up_tail()`、`_require_local_image()`；`build_image` 首行 fail-fast；`make_stack_tasks` 对 `supports_offline` 栈条件注入 `save`/`load`（仅该栈表面变化，其余栈黄金快照零改动）。② `xmnn.py` 声明升级为 10 任务（+`save`/`load`，`bridge_env_keys` 加 `XMNN_OFFLINE`），`wheel`/`build-tvm` 经 `offline_exec_env()` 单点注入。③ `build-wheel.sh` 读同一开关：numpy/scipy 缺失 `exit 2` 不再 pip 兜底、`$NUITKA_DL_FLAG`（空值 unquoted 展开整体消失）替换三处 Nuitka 下载旗标、pip 镜像 `case` 整体跳过、缺系统 gcc 前置断言 `exit 2`。④ `save_image` 的 client 专属文案参数化为 `not_found_hint`/`restore_hint` 供栈侧复用。⑤ 不触碰 compose `environment` 段与 `stack spec` 其余字段，保住 `test_compose_merge.py` 黄金快照。

**验收点（测试锁行为）**：`tests/test_overlay_core.py` 新增 10 例（声明范围仅 xmnn / 环境回写 V-1 / `.env` 回退与同开同关冲突 / `--no-build` V-2 / `exec -e` 门控 / `build` 首行 fail-fast 且 `runner.commands == []` / 缺镜像 Exit / `up` 任务体参数存活至 argv / `save`·`load` 仅离线栈生成），`test_tasks_surface.py` 黄金清单同步；`apps/containers/client` 下 `pytest tests -q` → **147 passed, 1 skipped**；`bash -n build-wheel.sh` exit 0。

**C 同步**：预防措施 `[prevent: offline-hard-fail]`——离线路径一律"硬失败 + 中文指引"，禁止静默降级为联网重试（无网环境下静默联网只会把真实原因埋在超时里）；规则固化于 [rules/xmnn-overlay.md](rules/xmnn-overlay.md) §10 与 P0 清单 C12，人类文档见 [../overlays/xmnn-dev/README.md](../overlays/xmnn-dev/README.md) §两个过程（该章节 2026-09-17 由「离线模式」更名而来），`.env.example`（client 与 overlay 两处键集合）同步登记。

### 2026-09-17 · `fix:` load 时 Podman 未启动被误报"镜像版本不符"——双脚本新增守护可达性预检与 load 退出码检查

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session sc-20260917-load-daemon-down，未提交，commit hash 待补）。

**现象与根因**：真机执行 `./xmnnctl.ps1 load`，sha256 校验通过后报 `Cannot connect to Podman... dial tcp 127.0.0.1:60432 actively refused`，随即脚本以 `[ERR] 导入的镜像中没有 localhost/xmnn-runtime:...；请核对 XMNN_VERSION` 收场——把客户引向错误的排障方向（改版本号）。取证：`podman machine list` 显示默认机器 LAST UP 为 Never，CLI 已安装但后台虚拟机从未启动。5-Why 系统性根因——脚本把"CLI 在 PATH 中"（Detect-Runtime 只做 Get-Command/command -v）等同于"守护进程可达"，且 `load` 退出码从未检查：load 对 1.2GB 包失败后继续走镜像 inspect 重试（5×2s），最终用"版本不符"这一唯一被预设的失败模式兜底，掩盖 socket 连不上的真实原因。

**修复（双脚本对等 + 测试锁行为）**：① bash 新增 `assert_runtime_alive()`、ps1 新增 `Assert-RuntimeAlive`：以 `podman/docker info` 探测守护，失败即 fail-fast 并按运行时给出可操作指引（podman→`podman machine start`/Podman Desktop；docker→启动 Docker Desktop 等托盘就绪）；② 在 `load`（sha256 之前，避免对 1.2GB 包做无用哈希）、`up`、`smoke` 三处调用，`init` 保持免守护特性（生成凭证不依赖后台）；③ `load` 调用后立即检查退出码，失败时 die"镜像导入失败，请查看上方原始报错（常见磁盘空间不足），导入幂等可重试"，不再落入误导性版本排查；④ README §7 排障表新增连接失败行与"次生误报版本不符"说明行，§9.2 FAQ 新增 `Cannot connect to Podman` 条目；⑤ test_release_bundle.py 新增 2 例：bash 真实行为测试（stub podman 的 info 恒失败，断言 exit 1、输出含 `podman machine start`、不进入后续流程）与双脚本静态对等断言（预检函数定义+三处调用、load 失败文案）。

**V 对抗审查（四视角）**：① 魔鬼——机器处于 starting 中间态时 `info` 也失败，报错同样指向 start，语义正确；预检误杀风险仅限 load/up/smoke，init/down/ps/logs 行为不变；② 新人——错误信息直接给出可复制命令，无需知道"虚拟机/daemon"概念；③ 老板——改动局限 xmnnctl 双脚本/README/测试，无契约面变更；④ 未来——"安装探测 ≠ 可达性探测"作为预检分层原则固化在注释中，新增运行时命令时按此模板加预检。

**C 同步**：预防措施 `[prevent: daemon-preflight]`——可达性预检前置到重操作之前，同类"未启动机器"故障被结构性拦截，且不再产生误导性次生报错；眼前解困：已执行 `podman machine start`（started successfully），用户重跑 `./xmnnctl.ps1 load` 即可。

### 2026-09-17 · `docs:` release/README 小白化——零基线读者的环境准备、第 0 步、预期输出与词典 FAQ

**关联七概念场景**：场景5「知识沉淀」（E→C，session sc-20260917-readme-newbie，未提交，commit hash 待补）。

**背景**：客户交付文档的真实读者是完全不懂技术的终端用户（只会复制粘贴），旧版 README 默认读者已知"终端/PowerShell/容器/localhost/Token"等概念，且从不描述"成功时长什么样"，用户见到红字即恐慌、不知道播放器后台需先启动。

**修复（纯文档，零行为变更）**：① 开头新增"30 秒建立印象"块（软件电脑 + 播放器类比、红字不等于失败的语义）；② §1 增"开始前三样东西"（Podman Desktop/Docker Desktop 官方链接、PowerShell 7 自检命令 `$PSVersionTable.PSVersion`、解压双层同名目录避坑）；③ §2 新增"第 0 步：在正确文件夹打开终端"（Shift+右键/地址栏 pwsh、`dir` 核对、托盘启动检查、终端粘贴常识）；④ init/load/up 预期输出与耗时表（16 位密码/32 位 Token、1.2 GB 约 1-5 分钟、`====` 方框为成功标志、蓝绿黄红四色语义）；⑤ 首次登录 JupyterLab 指引（Token 从 .env 获取、URL 直登法、内核必须选 Python 3.14 (xmnn runtime)）；⑥ 新增 §9 小白词典（9 条）与高频问题（8 条，含重启后只需 up、可关终端、执行策略 Bypass、Linux chmod）；⑦ 顺带修正事实矛盾：`workspace/` 首次 `up` 才创建，不能作为刚解压时的位置判别标志。

**V 对抗审查**：所有耗时/位数/颜色/命令事实逐行对照 xmnnctl 双脚本源码核实；check-links 通过；纯文档无契约面变更。

**C 同步**：预防措施 `[prevent: zero-baseline-docs]`——五件套（类比开场→环境自检→动作级第 0 步→预期输出表→词典/FAQ）作为客户交付文档基线模板。

### 2026-09-17 · `fix:` 根目录新增 xmnnctl 薄转发壳，`./xmnnctl` 在叠加层根直接可用

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session sc-20260917-readme-block-unrunnable，未提交，commit hash 待补）。

**现象与根因**：文档接缝条目（同日稍早）发布后，同一用户在叠加层根目录执行 `./xmnnctl init` 仍报"术语不会被识别"——文档提醒被实证无效。5-Why 重估的不可削减事实：①IDE 终端 cwd 固定为叠加层根，是用户不可改变的工作习惯；②用户连续三次均在根目录直接敲命令，真实意图是"当前位置直接可用"而非"读文档换目录"；③根目录与 `release/` 同名文件并列，位置语义只能靠主动阅读文档获得。系统性根因：跨布局执行缺一个**在错误位置可见的可执行入口**，文档是被动信息，无法拦截直觉行为。

**修复（薄转发壳，结构性预防）**：①叠加层根新增 `xmnnctl.ps1`（pwsh）与无扩展名 `xmnnctl`（bash）两个零逻辑壳：ps1 壳 `& release\xmnnctl.ps1 @args; exit $LASTEXITCODE`，bash 壳 `exec .../release/xmnnctl "$@"`（退出码透传）；②真实脚本启动即 `Set-Location`/`cd` 自身目录，`.env`、`workspace`、compose project 操作全部落在 `release/` 侧，根目录零写入；③.gitattributes 规则由 `**/release/xmnnctl` 泛化为 `**/xmnnctl`，覆盖新 bash 壳的 LF 行尾；④两 README 执行位置指引改为"根目录直接 `./xmnnctl`"，排障行同步。

**V 对抗审查（推翻同日早先的否决）**：早先魔鬼视角否决"根目录加壳"的三条理由经重新取证均不成立——①"双脚本漂移"：壳零业务逻辑（4 行转发），真实脚本仍是唯一事实源，无漂移面；②"根目录被 .env/workspace 污染、与同名 compose project 冲突"：真实脚本自定位 `release/`，写入全在客户侧；两套 compose 的 project 名/容器名/端口（2225/8893）本就相同，开发栈与交付栈天然互斥，壳不引入任何新冲突；③"壳误入客户包"：relpack 只取 `release/`，壳永远不到达客户。实测 PowerShell 对无扩展名调用自动补 `.ps1`（`./xmnnctl` 可命中 `xmnnctl.ps1`），与用户截图中的敲法完全吻合。

**C 同步**：预防措施 `[prevent: convenience-shim]`——以可见的可执行入口替代被动文档，同类"位置直觉"故障被结构性消除；眼前解困 `./xmnnctl init` 从叠加层根直接执行。

### 2026-09-17 · `fix:` 叠加层根目录执行 `.\xmnnctl.ps1` 报"不会被识别"——双布局位置接缝补引导

**关联七概念场景**：场景2「问题解决」（F→V→C，session sc-20260917-xmnnctl-ps1-missing，未提交，commit hash 待补）。

**现象与根因**：在 `overlays/xmnn-runtime` 根目录执行 `.\xmnnctl.ps1 init`，PowerShell 报"术语不会被识别为 cmdlet"。取证：脚本物理路径为 `release/xmnnctl.ps1`（客户交付包根），根目录只有开发栈同名文件 `compose.yaml`/`.env.example`。5-Why 系统性根因——开发态栈（根目录，`invoke xmnnrt.*`，extends 仓库 `_shared`）与客户交付态栈（`release/`，自包含、零仓库知识、xmnnctl）两套布局同构、同名文件并列且仅隔一层目录；客户文档 §2 的命令文本隐含"cwd=交付包根"却不携带位置信息，"厂商 pack 后在开发仓库内演练交付脚本"这一高频场景无任一文档覆盖，跨布局执行时错误点零引导。

**修复（文档接缝，零行为变更）**：① release/README.md §2 开头加「执行位置」块（交付包根判别标志：同目录含 `xmnnctl.ps1`+`artifacts/`+`workspace/`；仓库演练给 `cd release` 与 `.\release\xmnnctl.ps1` 两条可复制路径）；② §7 排障表新增行覆盖原始报错关键词"不会被识别"；③ 叠加层根 README §客户独立交付包补厂商演练指引（经 release/，开发态仍走 invoke）。

**V 对抗审查（四视角）**：① 魔鬼——评估"根目录加转发/提示脚本"后否决：双脚本漂移违背单一事实源，且会在 staging 写入 `.env`/`workspace` 并与同名 compose project 的容器/卷互相干扰；② 新人——"交付包根"首次接触不可懂，已给判别标志与可复制命令；③ 老板——改动 2 README + 本条 CHANGELOG，无代码/测试面变更，不破坏 release 契约（零 Python/零仓库知识测试不受影响）；④ 未来——排障行按原始报错词书写，搜索即命中。实测从叠加层根 `.\release\xmnnctl.ps1 version/init` 均成功（脚本 `Set-Location $PSScriptRoot` 自定位，artifacts tar 1.2 GB 与 release.json 完整、git 忽略有效）。

**C 同步**：预防措施 `[prevent: doc-seam]`——双布局边界在客户文档与开发文档两侧显式表达；眼前解困命令 `.\release\xmnnctl.ps1 init` 已实测通过。

### 2026-09-17 · `fix:` xmnnctl 预检在 WSL 非登录 shell 误报"缺少 compose"——PATH 外用户级 companion 回退探测

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session sc-20260917-preflight-companion，未提交，commit hash 待补）。

**现象与根因**：重打包后真机跑 `./xmnnctl load` 交付链路时，预检 2 秒即死：`[ERR] Podman 已安装但缺少 compose 支持`。取证：`podman compose` 插件在本机确实不可用（5.7.1 未装 provider），但 `podman-compose` 实际已由 pip `--user` 安装在 `~/.local/bin`；登录 shell 经 `~/.profile` 自动包含该目录故一切正常，而 WSL 非登录调用（`wsl -- bash -c`、自动化/最小 PATH 环境）不读 profile，`command -v podman-compose` 失败——"已安装"被误判为"未安装"。原 die 信息只给一句笼统指引，客户无法区分"没装"与"装了但 PATH 没有"。

**修复（双脚本对等 + 测试锁行为）**：① bash `xmnnctl` 新增 `find_companion()`：compose 插件与 PATH 均未命中后，依次回退探测 `$HOME/.local/bin`、`$HOME/bin`（pipx 链接 / pip --user / 旧发行版落点），命中即以绝对路径自动启用并打 WARN 指引加 PATH；彻底缺失时 `compose_missing_die` 输出多行可操作信息（pipx/pip --user 两条安装命令 + WSL 非登录 shell 的 `export PATH` 自救）；docker 分支对 docker-compose 做对等回退。② `xmnnctl.ps1` 对等新增 `Find-UserCompanion`：`%USERPROFILE%\.local\bin`（pipx）+ `%APPDATA%\Python\Python3xx\Scripts`（pip --user，递归深度 2 不穿 site-packages），命中自动启用并 WARN，失败时同样多行可操作报错。③ test_release_bundle.py 新增 3 例：双脚本回退/提示静态对等断言；bash 真实行为测试（隔离 HOME/PATH + stub podman，stdin 喂入脚本源码剥掉末行 main 后 source 调用 detect_runtime），正例断言选中 `~/.local/bin/podman-compose` 并告警、负例断言 exit 1 且报错含安装命令与 PATH 自救；无 bash 环境自动 skip。④ README 排障表同步。

**V 对抗审查（踩坑实证）**：① 行为测试经 WSL 互操作执行连踩三坑并固化为注释：`bash -c` 内联多行/`$()` 被互操作 argv 重组吞掉（须落盘 `bash <file>`）、Windows 路径反斜杠被吞（须传 `/mnt/<drive>` 原生路径）、Windows 文本管道把 `\n` 翻成 `\r\n`（bash 报 `pipefail\r: invalid option`——须以字节喂 stdin，恰与本交付包 CRLF 天敌同源）；② `set -u` 下 `${HOME:-}` 兜底；③ 回退只认 `-x` 可执行文件，不用 PATH 改写全局污染（COMPOSE 数组持绝对路径，作用域仅限本进程）；④ ps1 递归限定 Depth 2，避免每次预检遍历 site-packages；⑤ 行为测试 stub 全部在 WSL 原生 /tmp（exec 位真实），不依赖 9p 元数据。

**C 同步**：预防措施 `[prevent: test-case]`——正/负行为测试使"PATH 外已安装 companion"回归永久锁定；客户侧报错信息从一句话升级为"安装命令 + PATH 自救"自描述。

### 2026-09-16 · `fix:` 客户首跑 `./xmnnctl` 报 `/usr/bin/env: 'bash\r'`——无扩展名 POSIX CLI 漏出 gitattributes LF 保护

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session sc-20260916-xmnnctl-crlf，未提交，commit hash 待补）。

**现象与根因**：客户控制台执行随包 `xmnnctl` 即报 `/usr/bin/env: 'bash\r': No such file or directory`。取证：仓库 index/工作区该文件均为 LF（本机 core.autocrlf=false），但 `git ls-files --eol` 显示其属性仅为 `text=auto`——脚本无 `.sh` 扩展名，不匹配根 .gitattributes 的 `*.sh text eol=lf`；在 core.autocrlf=true 的 Windows 检出/打包机上工作区被写成 CRLF，拷贝/压缩通道只搬运字节，交付副本首跑即死。shebang 由内核在解释器启动前按字节解析（`bash\r` ≠ `bash`），脚本内既有的 `tr -d '\r'`（防 .env CRLF）无法自救。同类事故 2026-08 已在 `**/bin/jpman` 发生并加过单点规则，但未泛化——`release/xmnnctl` 作为新无扩展名 CLI 漏网；既有测试锁了 `.env.example` 的 LF 与脚本对 .env 的去 CR，唯独没锁脚本文件自身字节。

**修复（三层防御 + 客户自救）**：① 根 .gitattributes 把 jpman 单点升级为「无扩展名 POSIX CLI 清单」，新增 `**/release/xmnnctl text eol=lf`（任何 autocrlf 配置下 checkout 强制 LF）；② relpack 新增纯函数 `find_crlf_shebang_scripts()`（跳过 .ps1/.bat/.cmd 等规范即 CRLF 的 Windows 原生脚本与 artifacts/ GB 级归档），`pack_release()` 打包前 fail-fast 并提示 `git add --renormalize`；③ test_release_bundle.py 新增两例：交付骨架 shebang 脚本零 CR、纯函数命中 CRLF bash/放过 CRLF ps1 与 artifacts；④ release/README 排障表加客户自助行（Linux/WSL `sed -i 's/\r$//'`、macOS BSD sed 变体）。

**V 对抗审查（四视角）**：① 魔鬼——仓库文件已是 LF 为何仍改：故障副本来自 autocrlf=true 的其他检出/交付通道，jpman 前科实证该路径真实存在，规则不可省；② 边界——xmnnctl.ps1 首行同为 shebang 但规范行尾即 CRLF，扫描必须按后缀排除（测试锁定）；③ 边界——artifacts/ 含 GB 级镜像 tar.gz，全量 read_bytes 会爆，按目录跳过；④ 新人——未来新增无扩展 CLI 漏配规则时骨架测试自动红，不依赖人记住 gitattributes；⑤ 未来——pack 是厂商交付唯一 choke point，守卫挂此使坏字节不出门。自有 overlays/bin 全量扫描确认无第二条漏网 POSIX 脚本。

**C 同步**：预防措施 `[prevent: test-case, build-gate]`——gitattributes 源头强制 LF、relpack 打包 fail-fast、shebang-LF 双测试回归锁；客户侧 README 排障行提供存量坏副本自救。

### 2026-09-16 · `feat:` xmnn-runtime 内置 torch 2.14.0+cpu——pytorch 前端工具链固化（稳定版）

**关联七概念场景**：场景3「重构优化」（I→F→V→C，session sc-20260916-runtime-torch-builtin，未提交，commit hash 待补）。

**背景**：torch CPU 此前为容器内手工 `podman exec pip install`（down/重建即丢、默认 PyPI 易拉 CUDA 变体、版本浮动），与"工具链稳定"诉求冲突。

**方案（三层稳定性）**：Containerfile 新增独立 Layer 1（无 COPY 输入、置于 whl 层之前，重打 whl 增量构建复用）：`ARG TORCH_VERSION=2.14.0` 精确 pin + `ARG TORCH_INDEX_URL=https://download.pytorch.org/whl/cpu` 固定官方 CPU 索引（构建日志实证依赖仅 sympy/networkx/fsspec/mpmath/filelock，零 nvidia 包）；只装 torch 不装 torchvision（compile_api 仅 torch.jit.load+relay 前端，四 demo 实测不需要）；builder 镜像与 wheel pyproject 不动（torch 为函数内 lazy import，Nuitka 不 follow）。守卫新增第 10 项硬断言 `torch.version.cuda is None` + jit 可用 + CUDA 不可用 + CPU 张量算子，root/devuser 双身份构建期执行。

**V 验证**：`inv xmnnrt.build --no-cache` 真机构建成功（torch 196 MB 下载层），构建期 10/10 PASS；**全新容器零手装** `xmflow pipeline -n demo.pytorch.resnet18 -t compile,accuracy` 与 `demo.two_inputs` 均 2/2 成功，输出余弦 0.9989583 / 0.9998791，与手装 torch 时逐位一致；独立 `podman run` 守卫复跑 10/10。镜像体积 2.29→3.18 GB（torch CPU 解压约 0.9 GB，仍小于 xmnn-dev 4.69 GB）。daemon-free 95 passed/1 skipped（smoke docstring 黄金断言 9→10 项同步）。

**C 同步**：xmnnrt-overlay.md §4 新增 torch 内置层契约（版本 pin/索引禁令/层序/升级双点）；runtime README「PyTorch 前端说明（torch 已内置）」+ 体积取舍 + torchvision 薄层层叠范式 + 排障（旧镜像/CUDA 变体）；docs/13 改为开箱即用说明；预防措施 `[prevent: build-gate]`——第 10 项守卫使 CUDA 变体/缺失 torch 在构建期即失败。

### 2026-09-16 · `feat:` xmnnrt.\* wheel 消费运行时栈——builder/runtime 镜像分离（第四声明式栈）

**关联七概念场景**：场景3「重构优化」（I→F→A→V→C，session sc-20260916-xmnn-wheel-split，未提交，commit hash 待补）。

**洞察与方案**：`inv xmnn.wheel` 原在重型开发镜像内完成构建后，verify-wheel.sh 仅以同镜像 `--system-site-packages` venv + `--no-deps` 验证（证明"开发镜像里能 import"，从未证明干净客户机从零安装）；且 [xmnn-overlay.md §9](../.agents/rules/xmnn-overlay.md) 早已裁决 wheel 消费型 scratch 栈"不回流 xmnn-dev"但从未落地。第一性原理：wheel 是构建器→运行时唯一制品契约（cp314 GIL、`_libs` RPATH `$ORIGIN` 自包含、内置 `.pth`、19 依赖元数据），两镜像 FROM 同一 rootless 基底即 ABI 同源。新增第四栈 `overlays/xmnn-runtime`（namespace `xmnnrt`，形态 A，2225/8893）：whl 装 base env `/opt/conda` + 补 ipykernel + 注册 `Python 3.14 (xmnn runtime)` 交付内核（env 仅 PATH 白名单）；零 LLVM/Nuitka 工具链、零源码挂载。

**whl 暂存契约**：`xmnnrt.build/up` 调内核构建前把 whl 暂存进 overlay `wheels/`（显式 `--wheel` > workspace/dist 最新 mtime > 已暂存复用 > Exit 1 指引；暂存区同时只留一个 whl；whl 不入 git、.dockerignore 反放行）。build/up 为 ≤160 行声明模块中的薄封装（与 build-tvm/wheel 长任务同性质豁免），不复制任何编排函数（C14）。

**V 验证**：daemon-free 79 passed/1 skipped（surface 黄金清单新增 xmnnrt 任务集/docstring/签名/短选项/模块边界，compose-merge GOLDEN 新增 xmnnrt 渲染断言）；真机 podman-machine-default：`invoke xmnnrt.build --pip-mirror tuna` 桥接构建 COMMIT 成功（169.6 MB whl），构建期 9 项守卫 root+devuser 双身份 9/9 PASS（cp314 GIL ABI、site-packages 路径黑名单 /workspace|/opt/xmnn-builder、_libs/libtvm+libLLVM、干净环境 ctypes 加载、tvm.build llvm 向量乘 2、relay 数据、bootstrap .pth、数据三目录、内核可见）；`podman run --rm --entrypoint /opt/conda/bin/python localhost/xmnn-runtime:latest /opt/xmnnrt-smoke/_runtime_smoke.py` 独立容器复跑 9/9 PASS；真机 E2E：裸 `podman-compose up -d` 起栈（2225/8893 Up，标签 project=xmnn-runtime/service=xmnnrt 正确），HostConfig 与 xmnn-dev 同族一致（SEC label=disable、privileged=false；devices/cgroupns 为 podman-compose 1.6 既有空操作，容器内 /dev/fuse 节点由 crun 默认提供），Jupyter HTTP 302、`xmnn-runtime` kernelspec 对 main env 可见、compose exec 守卫 9/9，`podman-compose down` 后残留计数 0。镜像体积实测 rootless 1.19 GB → runtime 2.29 GB（xmnn-dev 4.69 GB，省 51%；约 170 MB whl COPY 层为单阶段已知冗余）。

**V 对抗审查（四视角）**：① P0 同名 whl 陈旧——dev0 wheel 文件名恒定，旧逻辑只比文件名会在重打包后复用旧暂存 whl，修正为 name+size+mtime_ns 三全等才跳过（copy2 保 mtime 保证二次运行正确复用），新增 tests/test_xmnnrt_stage.py 7 例锁定选择顺序；② 依赖开放区间版本漂移、③ whl COPY 层体积两项记录为已知设计边界（README「已知边界」+ 规则 §4），版本锁定归属 wheel 打包端。

**C 同步**：新增规则 [xmnnrt-overlay.md](../.agents/rules/xmnnrt-overlay.md)（7 节特有契约）；docs/13 + docs 索引、client AGENTS/.agents README/apps AGENTS 路由登记；根 .env.example 加 XMNNRT 段；预防措施 `[prevent: test-case, build-gate]`——黄金两表锁定栈表面与 compose 渲染，9 项守卫构建期硬失败，暂存选择顺序 7 例单测锁定；全量 95 passed/1 skipped。

### 2026-09-16 · `fix:` `inv xmnn.wheel` 构建成功却 exit 1——invoke 3.0.3 × Python 3.14 stdin 线程 FIONREAD 缓冲溢出（假失败）

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session sc-20260916-xmnn-wheel-stdin，未提交，commit hash 待补）。

**现象与根因**：Windows 原生 `inv xmnn.wheel > error.log` 经透明桥接执行，容器内 build-wheel.sh 全流程成功（🎉 WHEEL BUILD COMPLETE，170M whl 已产出），WSL 内 invoke 收尾却抛 `ThreadException(SystemError: buffer overflow)`，桥接层 Exit(1) 报「WSL 桥接命令失败」。取证链：① 崩溃点 `invoke/runners.py::handle_stdin → read_our_stdin → terminals.bytes_to_read → fcntl.ioctl(input_, termios.FIONREAD, b"  ")`；② invoke 3.0.3 对 TTY stdin 用 **2 字节**缓冲做 FIONREAD（按 signed short 解析），而 Linux 内核固定写回 `sizeof(int)`=4 字节；③ Python 3.14 加固 fcntl 后越界写直接 `SystemError: buffer overflow`——pty 真机探针证明**与队列字节数无关（queued=0 也必崩，py3.14.2）**；④ 桥接 stdin 是 console 中继 pty（isatty=真），`pty=True` 默认启动 stdin 转发线程，长任务收尾时中继 fd 半关闭/可读，线程必崩。影响面覆盖全部 `run_cmd(pty=True)` 路径（build/up/down/logs/wheel/build-tvm）及 py3.14 下的真交互命令（首次按键即崩）。

**修复（共享包 `apps/containers/shared/src/jpman_common/proc.py`，builder/client 同族生效）**：① `run_cmd` 新增 `forward_stdin: bool = False`，默认向 `c.run` 注入 invoke 钦定的 `in_stream=False`——invoke 因此根本不创建 stdin 转发线程（`runners.py::create_io_threads` 对 falsy in_stream 直接跳过），编排命令全部非交互、零行为损失，Ctrl+C 仍经 KeyboardInterrupt→send_interrupt 信号路径传播；② 新增 `apply_invoke_stdin_compat()`，用 4 字节缓冲重做 FIONREAD 的兼容函数幂等替换 **两处绑定**（`invoke.terminals.bytes_to_read` 定义点 + `invoke.runners` 顶部 `from .terminals import bytes_to_read` 的名字绑定——三态 pty 探针实证只改定义点无效），进程导入 proc 时自动应用（仅 POSIX，Windows 静默跳过）；③ 仅真交互式入口 `env.shell` 与 builder `interact.shell`/`_exec_via_cli`（`podman run/exec -it … bash`）显式 `forward_stdin=True` opt-in，其 py3.14 键盘输入由兼容补丁兜底。

**V 验证（三态 pty 真机探针 + 双平台单测）**：在 podman-machine-default（invoke 3.0.3 / py3.14.2）以 pty.fork 注入 stdin 事件——原生 invoke 必现 ThreadException（crash 复现）、`in_stream=False` 干净退出、兼容补丁保留转发也干净退出；先证明 2 字节 `fcntl.ioctl(FIONREAD, b"  ")` 在该环境 queued=0 即抛 SystemError，再断言 4 字节实现返回正整数。新增 5 例单测（默认注入断言、opt-in 不注入、非 fileno/非 tty 回退 1、POSIX tty 不溢出、双绑定幂等）：Windows py314 185 passed/2 skipped（POSIX 用例跳过），WSL 全量 205 中 proc/桥接/内核 80 passed/1 skipped（另 6 个失败经 stash 基线对比为改动前既有的 Windows 专属测试 Linux 平台错配，与本修复无关）。真机重跑 `invoke xmnn.wheel` 退出码 0、日志无 ThreadException。

**C 同步**：docs/04 新增 W-I13（成功却 exit 1 的判别要点 + 勿重跑长任务）；docs/03 新增「透明桥接 stdin 契约」节；预防措施 `[prevent: test-case]`——默认 `in_stream=False`、opt-in 边界与 FIONREAD 兼容路径全部由 daemon-free/pty 单测锁定。

### 2026-09-16 · `fix:` `inv <ns>.build` 桥接被 enterns 劫持进交互 shell + VM 回收后 `/run/user/<uid>` 丢失 podman exit 125

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session sc-20260916-xmnn-build-shell，未提交，commit hash 待补）。

**现象与根因（双根因同日实证）**：① 用户在 Windows 原生执行 `inv xmnn.build`，任务未运行却进入一个交互 shell（伴随 wslmotd *nested process namespace... exit twice* 文案）。取证：桥接器 `utils.run_in_wsl_bridge` 用 `wsl.exe -d podman-machine-default -- bash -lc <任务>` 启动**登录** shell；Fedora-WSL 系发行版 `/etc/profile.d/enterns.sh` 检测到嵌套 systemd（`/lib/systemd/systemd` 非 PID 1）即无参执行 `/usr/local/bin/enterns`，其对普通用户走 `sudo nsenter -m -p -t <pid> su -l $USER`——一个全新交互登录 shell，原任务命令串在命名空间切换中被丢弃；同目录 `docker-host.sh` 登录时执行 `podman info`，podman 未就绪还会污染 `DOCKER_HOST=unix://`。② VM 被 WSL 回收重启后（容器呈 `Exited (0) 292 years ago`），tmpfs 上的 `/run/user/1000`（正常由 systemd-logind/pam 会话创建）未重建，rootless podman 任意命令报 `creating events dirs: mkdir /run/user/1000: permission denied`（exit 125）；实测仅 `export XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir` 不能替代该目录（events dir 硬编码回退 /run/user/<uid>）。

**修复（编排层，`src/jpman_client/tasks/utils.py` + `overlay_core.py`，三栈同族生效）**：① 桥接由登录 `bash -lc` 改为非登录 `bash -c`（与实证可靠的 `.temp/xmnn-launch/run-inv.sh` 同构），PATH 显式前置 `~/.local/bin`、LANG 兜底 `C.UTF-8`，profile 的 enterns/docker-host 两个副作用均不触发；② 新增 `ensure_wsl_rootless_runtime()`（仅 `/proc/version` 含 microsoft 时动作：XDG 空且 `/mnt/wslg/runtime-dir` 可写则兜底；`/run/user/<uid>` 缺失则 `sudo -n` 幂等 mkdir/chown/chmod 700，免密不可用仅警告不阻断），在 `gate_platform` 的 Linux 放行路径调用——Windows 桥接重入与 WSL 内原生 invoke 两个入口同时覆盖；③ 顺带修正桥接失败 `Exit(rc, msg)` 参数反序（invoke 签名 `Exit(message, code=None)`，旧写法退出码恒为 1、rc 被当消息），改为 `Exit(message, code=rc)`。

**V 验证**：daemon-free 新增 `tests/test_wsl_bridge.py` 9 例（非登录 argv 断言、空 argv 不裸开 shell、rc 原样上抛、运行时自愈的平台判定/幂等/sudo 失败不阻断/XDG 兜底），client 全套 84 passed/1 skipped。真机（podman-machine-default）：模拟回收 `sudo rm -rf /run/user/1000` 后 Windows `inv xmnn.ps` 自动自愈且无登录污染 warning；`inv xmnn.build --pip-mirror tuna --conda-mirror tuna` 直接进入 podman build 流并 COMMIT 成功（90s，不再进 shell）；`inv xmnn.up --skip-build` 恢复被回收栈（up_preflight 再次收敛 Exited 残留与孤儿 rootlessport），单会话浸泡 80s 后 exec OK、Jupyter 302、`xmnn.smoke` 全过（双 ABI/LLVM 22.1.8/Nuitka 4.1.3/挂载源码/tvm.build 向量加）。

**独立事件记录（非本项目缺陷）**：验证期间 08:53:04 一个外部 Go-http-client 经 `podman.sock` 发起 `POST /v5.7.0/libpod/system/prune`（all=false），删除了两个 Exited 容器（含跨项目的 jupyter-podman 单容器）、空 pod 与 6 个悬空镜像（journald user journal 取证；Windows 侧无 Podman Desktop/gvproxy 进程，bash/root history 无 prune 记录）。有 tag 镜像与命名卷无损，`inv up` 秒级恢复；预防措施是避免在共享该 socket 的 UI/自动化中执行 system prune。

**C 同步**：docs/04 新增 W-I11/W-I12；windows-wsl.md 新增 §8「透明桥接硬契约：非登录 shell + rootless 运行时自愈」；预防措施 `[prevent: test-case]`（非登录 argv 与自愈分支全部 daemon-free 单测锁定）。

### 2026-09-16 · `fix:` WSL 回收循环假 Up 自动识别：`up_preflight` 新增 init PID 活体判据与 stale conmon 定点回收

**关联七概念场景**：场景2「问题解决」（I→F→A→V→C，session sc-20260915-fake-up-auto-heal，未提交，commit hash 待补）。

**背景与根因**：W-I8 记录的假 Up（WSL 发行版回收循环后 daemon libpod sqlite 仍记 running，但容器 init 进程在宿主已死——`ps`/端口/HTTP 302 均为孤儿 conmon/rootlessport 制造的假象，exec 报 `crun ... status: No such file`）首版只有手工五步定向清理；跨平面反复交替还会累积已删容器的 stale conmon（不持端口、不阻断 up 但是进程垃圾）。daemon 单视角探测必然被假象欺骗。

**修复（编排层 `src/jpman_client/tasks/overlay_core.py`，三栈同族生效）**：① 新增 `_container_init_pid`（`inspect --format {{.State.Pid}}`）+ `_host_process_alive`（宿主 `ps -p <pid> -o pid=`，零双引号探针）+ `_container_truly_alive` 双重活体判据；`up_preflight` 在 reconcile 之后、config_files 标签比对之前检测假 Up，命中先 `compose down` 清除失实记录再进入孤儿回收；② 新增 `parse_conmon_process`/`_list_stale_conmons`/`reap_stale_conmons`——双门判定（进程名 conmon + `-n` 为本栈容器名 + 64 位 ID 不在 `podman ps -aq` 运行集合），TERM→0.5s→复检→KILL，活 conmon 与他栈 conmon 绝不触碰，与 rootlessport 回收同一前置条件；③ `require_running`（build-tvm/wheel/build-native 长任务前置）从 daemon 视角收紧为真活体，假 Up 直接 Exit(1) 并提示重新 up，不自动重建以免破坏长任务现场。

**V 验证**：daemon-free 单测新增 6 例——真实 conmon 命令行解析、双门只收本栈 stale（活/他栈不动）、rootlessport 与 stale conmon 同轮分别精确点名 kill、假 Up 强制 down 后再回收、真活体 no-op、`require_running` 拒绝假 Up；FakeRunner 的 TERM 模拟改为按点名 PID 从各自数据源移除（对齐真机语义）。

**C 同步**：本条为 W-I8（症状矩阵/手工五步清理）与 compose-overlay-ops v1.0.2「exec 是唯一活体判据」的自动化代码落地；预防措施 `[prevent: test-case]`——活体判据、双门回收与拦截路径全部由 daemon-free 单测锁定。

### 2026-09-15 · `fix:` 跨控制平面标签分歧致 `up -d` 强制 recreate + 孤儿 rootlessport 占 2223：`up_preflight` 三道自愈

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session sc-20260915-xmnn-2223-bind，未提交，commit hash 待补）。

**现象与根因（三次确定性复现）**：在 overlay 目录裸跑 Windows 原生 `podman-compose up -d` 报 `conmon exited prematurely: conmon process killed` 后接 `rootlessport listen tcp4 0.0.0.0:2223: bind: address already in use`（exit 125）。取证链：`podman inspect` 活体容器标签——裸 compose 写 `com.docker.compose.project.config_files=D:\spaces\...\compose.yaml`，WSL 桥接 invoke 固定下发 `--file /mnt/d/.../compose.yaml`；podman-compose 把该标签**原文**纳入 config-hash，两平面交替操作即判配置漂移强制 recreate；podman-compose 1.6「每项目一 pod」模式强拆 infra conmon 时，rootlessport 已被 WSL `/init` 收养成为孤儿继续监听 2223/8890，新 pod bind 必败（**真机实证：先优雅 down 同样可能留下该孤儿**，②③两道都必须存在）。反证：同一平面连续两次 `podman-compose up -d` 幂等无重建。

**修复（编排层，`src/jpman_client/tasks/overlay_core.py`，三栈同族生效）**：`up_stack` 在 `up -d` 前改调新增 `up_preflight`，顺序三道——① Created/Exited 项目残留（旧 `reconcile_stale_containers` 保留）先 `compose down`（不带 --volumes）；② 活体容器 config_files 标签原文与本平面 `--file` 不一致先优雅 down（对抗审查曾误写成 `/mnt/d`↔`D:\` 路径等价归一，被 V 阶段真机探针证伪：compose hash 按原文算，等价归一无效，已改回原文比较 `config_paths_diverge`）；③ 无活体项目容器时 `ss -ltnp` 解析本栈端口持有者，仅对进程名 **rootlessport** 的 PID 定点 TERM→复检→KILL（他栈 pasta/conmon 绝不触碰；ss 缺失静默跳过不阻断）。纯逻辑（`parse_ss_port_holders`/`config_paths_diverge`）抽出做 daemon-free 单测。

**V 真机验收（podman-machine-default，jupyter-podman 2222/8888 全程零影响）**：V-1 破损现场（Created 残留+孤儿 pid=111397）`invoke xmnn.up --skip-build` 自动 down→定点 kill→up 成功；V-2 干净状态 Windows 裸 compose up 成功；V-3 裸 compose 同平面二次执行无重建（幂等）；V-4 Windows py314 `invoke xmnn.up` 桥接触发跨平面分支（打印分歧标签→优雅 down，down 过程如期出现 conmon 竞态→分支③回收孤儿 126644→up 成功）；V-5 invoke 同平面二次执行无警告无重建。终验：浸泡 80s 后 exec OK、Jupyter 302、SSH banner 正常；离线单测 69 passed/1 skipped，ruff 全过。

**C 同步**：docs/04 新增 W-I10；xmnn-overlay.md「up 残留自愈契约」升级为「up 三道 preflight 自愈契约」（含量化根因链与单一控制平面纪律）；compose-overlay-ops 技能错误表新增跨平面根因行与 v1.0.3 changelog；overlays/xmnn-dev/README.md 排障段同步。

### 2026-09-15 · `feat:` xmnn wheel 首次在重建栈内全流程打包成功（170M，10/10 隔离验证）；`fix:` 排除假 Up 容器与桥接发行版缺工具两个阻断

**关联七概念场景**：场景2「问题解决」（I→F→A→V→C，session sc-20260915-xmnn-wheel-build，未提交，commit hash 待补）。

**任务**：`invoke xmnn.wheel`——容器内 Nuitka 串行编译 tvm → 并行 vta/xmnn → scikit-build/CMake 组装 wheel，产物落宿主 `workspace/dist/`。

**阻断①（W-I9）桥接发行版未备 client 环境**：Windows 原生 invoke 透明桥接 podman-machine-default 后报 `bash: line 1: invoke: command not found`（exit 127）。该发行版为 Fedora 43 Container Image，自带 python3 3.14 但**无 pip**（`No module named pip`）；直接装 client 又报 `No matching distribution found for jpman-common`（jpman-common 是 `apps/containers/shared` 纯本地兄弟包，PyPI 无发布）。修复（发行版内，均 `--user`）：`python3 -m ensurepip --user` → `pip install -e ../shared` → `pip install -e '.[compose]'`（tuna 源），invoke/podman-compose 1.6.0 落 `~/.local/bin`（桥接器已自动 PATH 前置）。

**阻断②（W-I8）容器假 Up**：重装环境后 exec 报 `crun: container <id> does not exist: open /mnt/wslg/runtime-dir/crun/<id>/status: No such file`（127），但 `podman ps` 显示 Up、`inspect .State=running`、Jupyter 8890 仍 302。取证：inspect 的 PID 在宿主已不存在、`crun/` 下仅剩 `.cache`/`.empty-directory`，stale conmon(67549) 与孤儿 rootlessport(67532, 持有 2223/8890 LISTEN) 仍存活——libpod sqlite 与内核进程在发行版回收循环后脱节，ps/HTTP 均为假象。修复（**免 `wsl --shutdown` 的定向清理**，不影响同发行版健康的 jupyter-podman 栈）：`invoke xmnn.down`（容忍 conmon prematurely/netavark netns ENOENT 告警）→ `ss -ltnp` 定位并 kill 孤儿 rootlessport → `ps -ef | grep <容器ID>` kill stale conmon → 复查端口 free → `invoke xmnn.up --skip-build`，浸泡 75s 后 exec/Jupyter 302/libtvm.so 三验证通过。

**V 真机验收**：V-1 wheel 全流程 exit 0，tvm 串行 + vta/xmnn 并行 Nuitka 编译（编译期 7 clang 满载 + ccache 活跃实证）→ wheel 组装成功；V-2 产物 `workspace/dist/xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`（169.6MB，宿主 bind 目录可见）；V-3 `verify-wheel.sh` 隔离 venv **10 passed, 0 failed**（含真实 `tvm.build(llvm)` 向量加、relay/std 数据、bootstrap .pth、autolibs/tools_cpp/fonts 打包，base env 零污染）。

**C 同步**：docs/04 新增 W-I8（假 Up 症状矩阵/五步定向清理/活体探针预防）、W-I9（桥接发行版三步安装序）；compose-overlay-ops 技能升 v1.0.2（错误表新增"假 Up"行、端口占用行两因扩三因——新增 `ss -ltnp` 可见显式 rootlessport 持有者的可定向 kill 变体并置于 wslrelay 粘滞/wsl --shutdown 裁决之前、步骤 1 安装序修正、Gotchas 第 9 条"exec 是唯一活体判据"）。

### 2026-09-15 · `fix:` `build-tvm.sh` 配置阶段 rmtree(build/CMakeFiles) EACCES：9p 跨上下文无主旧产物 + 清理函数零容错

**关联七概念场景**：场景2「问题解决」（I→F→A→V→C，session sc-20260915-tvm-build-rmtree-eacces，未提交）。

**根因（双叠加）**：`podman-compose exec xmnn bash /opt/xmnn-builder/scripts/build-tvm.sh` 在 `inv config -f` 清空 build/ 时 `shutil.rmtree` → `os.unlink` 报 `PermissionError [Errno 13] CMakeFiles`。实证：挂载为 9p drvfs（`D:\ → /workspace/npu_tvm,uid=1000`），build/ 内 10:42 旧产物属主 `65534:65534`、目录 755（其他映射上下文生成），而 build/ 本身 0:0 777；容器内 root 对无主文件 chmod 直接 EPERM（9p 服务端在 Windows 侧判权、root 无 DAC 绕过），devuser(1000) 写 CMakeFiles 同样 denied；root/1000 新建文件恒为 0:0 777 且可互删——只有这批旧文件卡死。npu_tvm `tasks.py::_clear_directory_contents` 旧实现为裸 `shutil.rmtree(child)`，无 onexc 容错与指引。

**修复（F 裁决）**：①一次性解封走宿主 NTFS（ACL 允许、9p 即时同步）：PowerShell `Remove-Item -Recurse -Force <NPU_TVM_PATH>\build`，容器内随即可见目录消失；②`external/chaos/npu_tvm/tasks.py`（**属用户自有 pu_tvm.git 仓，非 SpecWeave 文件，需另行提交到该仓**）`_clear_directory_contents` 加 `onexc`：PermissionError 先 chmod 0777 重试（覆盖只读位场景，含文件 unlink 同构处理），再失败抛带宿主清理命令的中文 PermissionError。否决：容器内 chmod/chown/换 uid1000 执行（实测均被 9p 拒绝/仍非属主）、改 build 目录到 named volume（破坏 build/ 在源码树复用 libtvm.so 的调试设计，属大改）。

**V 真机验收（xmnn-dev，podman 5.7.0-rc3）**：V-1 清理后容器内确认 build/ 消失；V-2 `py_compile tasks.py` OK；V-3 真机重跑 build-tvm.sh：config -f 通过原失败点、ninja -j16 全量成功（ccache 热），产出 `libtvm.so`(78MB)/`libtvm_runtime.so`/VTA 双库，符号隐藏+18462 导出守卫全过，exit 0；V-4 **二次执行**验证重复强制清理闭环：887 目标重建 101.7s 成功、末次 `ninja: no work to do`（证明新建 0:0 777 文件的清空-重建幂等）。

**C 同步**：docs/04 新增 W-I7；.agents/rules/xmnn-overlay.md 新增「9p 无主旧产物清理契约」（容器内无解、必须宿主侧清理、tasks.py 外部仓归属说明）；builder/scripts/build-tvm.sh 头注更正——原「容器内 rm -rf build 强制全量」在该场景会失败，改为宿主 PowerShell 删除指引。

### 2026-09-15 · `fix:` 裸 `podman-compose up -d` 双根因修复：僵尸 editable 安装 + 1.6.0 Windows 盘符误判 git URL 丢失 `-f`

**关联七概念场景**：场景2「问题解决」（I→F→A→V→C，session sc-20260915-podman-compose-broken，本次按用户要求未提交，commit hash 待补）。

**根因（双叠加，均在宿主 Windows 原生 py314）**：① **僵尸 editable**——`pip show podman-compose` 1.6.0 的 `Editable project location` 指向已删除的 `D:\spaces\SpecWeave\external\dao\action\Containers\podman-compose`，finder MAPPING 死路径 → 入口垫片 `podman-compose.exe` 存在但 `import podman_compose` 必失败（`ModuleNotFoundError`），另有 pip 中断残留 `~odman_compose-1.6.0.dist-info`；② **上游盘符误判 bug**——重装后 `up -d` 稳定报 `no Containerfile or Dockerfile specified or found in context directory`，进程内 monkeypatch 抓真实 build argv 证实**缺失 `-f`**：1.6.0 `podman_compose.py::is_context_git_url()` 对 Windows 绝对路径 `D:\...` 经 `urllib.parse.urlparse` 得到 `scheme='d'`，L3245 `r.scheme != "" and r.netloc == "" and r.path != ""` 误判 git URL → L3297 分支跳过自定义 dockerfile 的 `-f` 注入；自定义 `Containerfile.xmnn-dev` 必现，默认名 Containerfile 的栈不受影响。同形态手工 `podman build -f <abs> <abs ctx>` 正常（对照实证排除 podman 本体问题）。

**修复（第一性原理裁决：宿主编排器按宿主约定安装；上游 bug 最小语义补丁）**：①卸载僵尸 editable + 清理 `~odman_compose` 残骸，PyPI 常规安装 `podman-compose>=1.0.0`（1.6.0；**不**用 `jupyter-podman-rootless/upstream/podman-compose` 镜像专用固定 commit 快照）；②站点包一行补丁：`is_context_git_url` 条件改 `len(r.scheme) > 1 and r.netloc == "" and r.path != ""`（盘符单字母 vs 真实 scheme 多字母）。vendored 快照不同步修改——镜像内 Linux 构建无盘符不触发。TRAE 沙箱硬保护 conda `Scripts\`，卸载/重装入口 exe 由用户在自有终端完成，site-packages 补丁由 agent 执行。

**V 真机验收（podman 5.7.0-rc3 Windows 远程客户端，xmnn-dev 栈）**：V-1 `podman-compose version`=1.6.0 且 `pip show` 无 Editable；V-2 `podman-compose config` extends 合并正常；V-3 补丁后抓 argv 含 `-f D:\...\Containerfile.xmnn-dev`，补丁语义 8 用例（D:/C: 盘符、相对路径、https/git/ssh/scp）全过；V-4 真机 `podman-compose up -d` 构建（全缓存）+ 起容器成功，`xmnn-dev` Up、`0.0.0.0:2223->22`/`8890->8888` 监听，应用层 HTTP 8890 `/api`=200、SSH 2223 banner `SSH-2.0-OpenSSH_10.2p1`，supervisord sshd/jupyter 双 RUNNING。诊断探针/临时日志/`:probe` 镜像 tag 用后即清。

**C 同步**：docs/04-troubleshooting-guide.md 新增 W-I5（僵尸 editable 症状/清理/PyPI 重装/预防：禁止从临时目录 editable 装编排器）与 W-I6（盘符误判根因/一行补丁/重装后须重打/argv `-f` 验证法）。

### 2026-09-15 · `fix:` `invoke env.build-layer` 叠加镜像构建失败：镜像内缺 jpman-common（No matching distribution found）

**关联七概念场景**：场景2「问题解决」（I→F→V→C，session sc-20260915-env-buildlayer-common）。

**根因**：同日 jpman-common 重构（见下方 refactor 条）把 client 的平台/连接层依赖上移到兄弟包 `apps/containers/shared`（纯本地包，PyPI 无发布），client `pyproject.toml` 已声明 `dependencies=["jpman-common"]`，但镜像构建链路未同步——`Containerfile.client` 的 build context 只有 client 根目录，STEP 8 `pip install -e /opt/apps/containers/client/` 在镜像内解析依赖时无本地源码可装，必报 `ERROR: No matching distribution found for jpman-common`（重构验收当时只覆盖宿主 editable + daemon-free 单测，未重跑镜像构建）。连锁影响：env.shell / env.run-cmd / `invoke run --rebuild-layer` 全断（重建失败后仅回退旧镜像）。

**修复（第一性原理裁决：构建期本质需求 = 两个本地源码树 + 安装顺序）**：采用 podman **命名构建上下文**——① `Containerfile.client` 新增 `COPY --chown=devuser:devuser --from=shared . /opt/apps/containers/shared/`，RUN 内安装顺序改为先 shared 后 client 两个 `pip install -e --no-build-isolation`，构建期自检改为同时 `import jpman_common, jpman_client`，清理段追加 `shared/build`；② `env_in_container.py::rebuild_client_layer()` 自动注入 `--build-context shared=<root.parent>/shared`（main context 仍为 client 根），构建前对 `shared/pyproject.toml` 做存在性中文预检（缺失 return False 不裸跑）。否决方案：父目录 `apps/containers` 作 context（含 builder `.image-cache/` 等 GB 级内容，ignore 脆弱）、task 临时复制源码树（临时目录生命周期）、宿主预构建 wheel（多余构建步骤）。

**V 真机验收（podman 5.7.0-rc3 Windows 远程客户端）**：V-1 `invoke env.build-layer` 全 16 步构建成功并打 tag（命名上下文的宿主绝对路径在客户端侧正确解析打包）；V-2 运行容器内 `pip show jpman-common`=0.1.0、`import jpman_common` 命中 editable 真实目录 `/opt/apps/containers/shared/src/jpman_common/`，jpman_client 同验；V-3 二次构建幂等成功、基底指纹 LABEL 保留；V-4 shared+client 单测 **160 passed / 1 skipped** 零回归。同步：docs/08-env-bootstrap.md（双上下文说明 + 手动 build 必须追加参数）、.agents/rules/invoke-tasks.md §4.3（双构建上下文契约与「新增兄弟包依赖先问构建上下文」预防条款）、Containerfile.client 头注与层注（预防措施：重构移动依赖归属时，必须穷举该依赖的所有安装现场——宿主 editable、镜像构建、CI；只验宿主会漏掉容器链路）。

### 2026-09-15 · `docs:` 固化 Windows shell 引用契约（cmd.exe 通道双引号为正确写法，推翻「3 处双引号遗留」误判）

**关联七概念场景**：场景2「问题解决」（builder `inv run` 修复的 V/C 延伸实证，session sc-20260915-inv-run-stale-container）。

builder 侧 `inv run` 修复后初稿把 client 的 4 处 `--format "..."`（`env_in_container.py` images/digest 2 处、`client_core.py` images/ps 2 处）登记为同款遗留。补验推翻：client 的 invoke **不覆盖** `run.shell`，Windows runner 实测为 `C:\WINDOWS\system32\cmd.exe`（COMSPEC），与 builder 显式锁定的 pwsh 7 是两条相反规则的通道——双引号命令在 cmd.exe 下全部 rc=0 且模板正确展开（含 `|` 分隔模板，Python 解析出 5 行镜像）；单引号会被当字面量传入（实证输出 `'sha256:...'`），将污染 tag 成员判定/digest 指纹比对。故**零代码改动**，仅在 `.agents/rules/invoke-tasks.md` 新增 §3.4「Windows shell 引用契约」固化正反两面规则与现状清单，并同步修正 builder CHANGELOG/规则中的错误遗留描述。验收：诊断脚本 5 用例（images 双/单引号对照、ps table、inspect digest 双/单引号对照）+ 复合模板解析实证，脚本用后即删。

### 2026-09-15 · `refactor:` 学习 OKF 容器知识包重构 apps/containers（jpman-common 共享包 + overlay_core 声明式内核 + compose extends）

**关联七概念场景**：场景3「重构优化」（I→F→A→V→C，V 强制）；用户输入「学习 projects/awesome-okf-xs/doc/bundles/jishu/containers 优化 apps/containers」。规格 `.trae/specs/infra-env/containers-okf-refactor/`（用户已批准）。三项架构裁决：①两端共享包 `apps/containers/shared`，包名 **jpman-common**；②compose 公共段用 **extends 服务级继承**抽 `overlays/_shared/base-rootless.yaml`；③静态等价 + daemon-free 单测验收，真机 E2E 用户环境恢复后后补。

**A 阶段原子交付**：
1. **jpman-common 共享只读层 + 连接层**：新建 `apps/containers/shared/`（scikit-build-core 纯 Python 包）：`proc.py`/`platform_paths.py`/`containers.py` 承载平台/进程/容器只读工具，`connection.py`（653 行，17 导出）承载 SDK 连接层唯一事实源（四级候选/base_url 显式/UTF-16 LE/host_runtime_uid 不硬编码 1000）；client 的 `utils.py`/`client_core.py` 与 builder 的 `tasks/utils.py`/`tasks/client.py` 瘦身为再导出垫片（builder 保留 compose 探测与 sdk_*_kwargs）；两端 pyproject 声明依赖 `jpman-common`，安装顺序先 shared 后两端（`pip install -e shared -e client` / `-e jupyter-podman-rootless`，editable 必须 `--no-build-isolation`）。
2. **overlay_core 数据驱动内核**：`src/jpman_client/tasks/overlay_core.py`（~715 行）：`SourceMount`/`SmokeSpec`/`TaskDocs`/`StackSpec` frozen dataclass + gates/prepare_env/compose_argv/run_compose/reconcile/build/up/down/ps/logs/smoke 内核函数 + `make_stack_tasks()` 六任务工厂；内核零栈知识，只 import 标准库/`.manage`/`.utils`/`jpman_common`。
3. **三栈声明化**：`quant.py` 88 行 / `xmnn.py` 158 行 / `monetize.py` 121 行（均 ≤160），仅 `<NAME>_SPEC` + `TASKS` + 六别名（xmnn/monetize 长任务 build-tvm/wheel、build-native/wheel 例外）；桥接键下沉 `utils._BRIDGE_COMMON_ENV_KEYS`；Grep 三查：同构编排函数与栈名硬编码零命中。
4. **compose extends 公共段**：新建 `overlays/_shared/base-rootless.yaml`（服务 `rootless-base`：network_mode bridge + /dev/fuse + label=disable + cgroupns host + 凭证四变量 + org.specweave.managed-by label + restart unless-stopped；无 volumes/build/env_file/ports/image/container_name）；三栈 compose.yaml 改 `extends: {file: ../_shared/base-rootless.yaml, service: rootless-base}` 只保留差异段。
5. **文档/规则/技能同步**：client `.agents/rules/` 6 文件（quant/xmnn/monetize/invoke-tasks/sdk-connection/windows-wsl）+ docs/10-12 extends 条目 + docs/01 两步安装 + AGENTS.md（9 模块/C14/第四栈路径/文件地图）；builder AGENTS/README/docs 08/09/rules 同步 shared 接线；client-overlay-scaffold 技能升 v1.1.0（SKILL §12/§13、namespace.py.skeleton 声明式重写、compose skeleton extends 形态、delivery-checklist 黄金表门）。

**F 阶段关键实证（知识包 ↔ 本机源码双证）**：
- podman-compose 1.6.0 `_parse_compose_file`（vendor 源码 L2844-L2849）先把 extends.file 按引用文件目录 join 重写绝对路径，`resolve_extends`（L2364）执行 `rec_merge({}, base, current)`——故 run_compose **无需 cd 前缀**；合并语义 dict 递归/普通 list 追加/command、entrypoint 无条件替换；volumes 特例（L2289-L2297）：仅短语法字符串按 target 去重且覆盖方获胜，**长语法 dict bind 不去重**；另有 `!override`/`!reset` 标签（三栈未使用）。
- `podman-compose config` 打印的是 resolve_extends **之前**的 merged_yaml（不含继承字段，勿据此误判失败）；真实继承结果须驱动 `_parse_args(['-f',...,'up','--no-start'])` 后读 `self.containers`。
- 真实渲染黄金结果：quant devices=[/dev/fuse] env 6 键；quant GPU devices=[/dev/fuse,/dev/dri]；xmnn env 11 键 volumes 5 target；monetize env 6 键 volumes 2 target ports 2224/8892；三栈 network_mode=bridge、labels 并集、privileged 缺省。

**⚠️ 已知行为变更（用户可见）**：quant 栈迁移前 compose.yaml **无 network_mode**，现随基文件获得 `network_mode: bridge`。依据：xmnn 旧文件头 2026-09-14 aardvark-dns user scope bus 实证（rootless 下 bridge 是可用配置）；回归风险低，但属语义变化，真机 up 时须确认 quant 服务名解析/出网正常。

**V 等价门（静态，已过）**：shared 92 passed（覆盖 97%）；client 全量 62 passed 1 skipped（含 test_overlay_core 内核黄金快照、test_tasks_surface 命名空间黄金清单、test_compose_merge 23 用例：rec_merge 模拟器 + 真实文件渲染 + **与真实 podman-compose 1.6.0 rec_merge 的对照探针**）；`invoke --list` 与迁移前逐行一致（根 7 + container/env 别名 + quant 6 + xmnn 8 + monetize 8）；红线 Grep（内核 import 栈、栈 import podman、同构函数、_BRIDGE_ENV_KEYS 旧名）零命中。

**R 独立对抗审查（CONDITIONAL PASS → 修复后 PASS，见规格 review.md）**：fresh 子代理以 vendor/podman-compose 1.6.0 源码（只读 submodule）+ 运行探针核对，0 blocker；修复 2 major + 2 minor：① **M1** 合并模拟器 volumes 两处反向语义更正——短语法实为「覆盖方按 target 获胜并移尾部」（vendor L2289-L2297）、长语法 dict bind 真实**不去重**；反转错误自证用例，新增长语法/匿名卷/类型冲突用例与 2 条真实 rec_merge 对照测试（环境无 podman-compose 时 skip）；② **M2** 5+ 处「volumes 按 target 去重」失实表述更正（基文件头/quant 规则 §4 §4.1/xmnn/monetize 规则/SKILL §7.6+G15/compose 骨架/本条 F 阶段实证）；③ M3 模拟器 docstring 声明保真边界（标签/归一化/插值子集/类型冲突 ValueError）；④ M4 删除 tasks/__init__.py 三栈零消费 ns.configure 死配置块（唯一事实源已是 StackSpec）。另处置 N1（行号 L2845-2847→L2844-L2849、resolve_extends L2329→L2364，共 6 处）、N2（模拟器渲染括号改为真实管线「先 -f 合并后 extends」顺序）、N4（standalone 裸 run 加三必需未来守卫注释）；N3/N5 登记。

**V 真机 E2E 后置清单（环境恢复后由用户/值班代理执行，daemon 可用时逐项打勾）**：
前置：恢复定制 WSL 发行版 + rootless podman（`systemctl --user enable --now podman.socket`、`loginctl enable-linger`）；在 apps/containers 下 `pip install --no-build-isolation -e shared -e client -e jupyter-podman-rootless`。
1. [ ] **xmnn 栈**：`inv xmnn.build`（构建成功，AST PREAMBLE trap 还原无残留）→ `inv xmnn.up`（2223/8890 端口可达）→ `inv xmnn.smoke`（双 ABI/SONAME 守卫 PASS）→ `inv xmnn.down`（零残留：容器/网络/匿名卷）。
2. [ ] **quant 栈**：`inv quant.build` → `inv quant.up`（2222/8888 可达；**重点确认 bridge 行为变更后服务名解析与出网正常**）→ `inv quant.smoke`（INT8/FP16/QDQ 三守卫 PASS）→ `inv quant.down`。
3. [ ] **quant GPU 覆盖**：`inv quant.up --gpu`（真实渲染 devices=[/dev/fuse,/dev/dri]；NPU/GPU 透传视硬件）→ smoke → down。
4. [ ] **monetize 栈**：`inv monetize.build`（apt clang + apache-tvm-ffi 0.1.13）→ `inv monetize.up`（2224/8892）→ `inv monetize.smoke` → `inv monetize.build-native`（单 .so，3 处源码适配生效）→ `inv monetize.wheel`（纯 Python wheel 不含 .so）→ down。
5. [ ] **builder 端垫片**：`invoke --list` 正常（已在静态门验证，真机复跑确认环境一致）+ `python -c "from jpman_builder.tasks import client as c, utils as u; print(c.get_client.__module__, u.run_cmd.__module__)"` 应打印 `jpman_common.connection jpman_common.proc`（证明连接/工具符号确实来自共享包，垫片无断链）。
6. [ ] 任一项失败：按「修复即闭环」三阶段处理，更新本清单与对应规则文件。
成功判据：以上全部 PASS 且 `podman ps -a`/`podman network ls` 无栈残留；通过后将本段勾选结果回链至本条与规格 tasks.md T6。

### 2026-09-15 · `docs:` README.md 原子化为 docs/（00-12 文档集 + 索引 + 根入口精简）

**关联七概念场景**：场景3「重构优化」单独 A 子类（A→V→C，等价性验证强制）；用户输入「README.md 原子化为 doc」。

**A 阶段拆分方案**：对齐构建端 jupyter-podman-rootless/docs/ 先例（两位数字序号 + docs/README.md 索引 + 根 README 精简为入口）。642 行 README 的 14 章节按 topic 策略拆为 13 个原子文件：
- `docs/00-overview.md`（定位/构建端关系/jpman 分工/核心能力）
- `docs/01-getting-started.md`（安装/快速开始/镜像备份恢复）
- `docs/02-invoke-reference.md`（命令速查/布尔三态/known_hosts 维护）
- `docs/03-windows-wsl.md`（三路径/连接优先级/逃生舱/A-B 维度分离）
- `docs/04-troubleshooting-guide.md`（W-I1~W-I4 + C-I1~C-I5 速查表，源 §5.4）
- `docs/05-sdk-usage.md`（Python import）/ `docs/06-run-discipline.md`（rootless 三必需）
- `docs/07-environment-variables.md`（容器级/SDK级/透传三表）
- `docs/08-env-bootstrap.md`（env.* 自举/base-digest 防陈旧）
- `docs/09-passthrough.md`（5+1 透传开关/端口语义/宿主前置）
- `docs/10~12-*-overlay.md`（quant/xmnn/monetize 三工作负载栈）

**外部引用同步**：AGENTS.md 三处锚点（§7→docs/06、README→docs/README、5.4→docs/04）；.agents/README.md 人类文档↔AI 规则对应表 5 行锚点全覆盖；构建端 entrypoint.md C-I2 交叉引用；docs/retrospective/patterns/win32-tty-pipe-charset-strategy.md 活模式引用。

**V 等价门**：check-links（30 文件 179 内联链接 0 断链）；check-atomization-duplication（源↔13 模式文件 0 重复）；finalize-atomization.py（断链/导航/看板 PASS）；12 原子文档全部满足单一职责，04/08 因表格与流程语义完整性略超 5000 字符（6182/5467）判定不拆。

**验收点**：根 README 精简为 4 章入口（定位/快速开始/文档导航/AI 规范）；docs/README.md 索引按入门/使用参考/架构高级三组导航；全部原子文件 frontmatter 携带 source 溯源；2026-09-15 未提交的「Windows 原生自动桥接」改动（git diff 9 insertions）已完整保留至 docs/10-12。

### 2026-09-13 · `feat/refactor:` onnx-quantized 迁移至 client（Podman rootless 薄叠加 + podman-compose 声明式栈 + quant.* 命名空间）

**关联七概念场景**：场景3「重构优化」（I→F→A→V→C，Spec Mode 全流程）；用户输入「迁移 apps/docker-images/devcontainer-base/variants/onnx-quantized 到 apps/containers/client，使用 podman-compose 知识包」。四项架构歧义经用户裁决：完整迁移 / FROM rootless:latest / opt-in 独立命名空间 / 源目录保留原样。

**I 阶段洞察（迁移本质）**：源变体的可迁移内容是 ① conda main 环境五包（onnx/onnxruntime/onnx-simplifier/onnxscript/onnxconverter-common）② 3 段纯 ONNX 构建期冒烟 ③ 2 份深度量化文档；Docker 4 层继承链与 variant-framework 是载体不是能力。rootless 基底与 onnx-dev 目标环境**同构**（Ubuntu 26.04 + /opt/conda/envs/main cp314t free-threading + PATH 优先 + SSH/Jupyter/supervisord），薄叠加可行。

**F 阶段设计（知识包裁决）**：以 OKF podman-compose 束（concepts/02/03/06/08/10）为 G1 依据——三必需 1:1 映射标准字段；多文件 list **追加**合并（devices 不去重）决定 GPU 覆盖只写新增设备；compose 写标签/SDK CLI 读标签为接缝；选型「栈生命周期用 compose、单资源命令式留 SDK」，compose 层 opt-in 不回流根 run。

**A 原子交付**：
- `overlays/onnx-quantized/`：Containerfile.quantized（3 层：五包安装 / COPY 守卫与冒烟 / 构建期执行）、compose.yaml（单服务 quant、长语法 bind、三必需、org.specweave 标签）、compose.gpu.yaml（仅追加 /dev/dri，CDI 注释）、.env.example（12 键）、smoke/（_quant_guards.py + 3 逐行等价脚本）
- `src/jpman_client/tasks/quant.py`：build/up/down/ps/logs/smoke 六任务，纯子进程（禁 import podman），复用 _project_root/_load_env_overrides/to_posix_path/detect_runtime/run_cmd/check_runtime_ready；双门禁（Windows 原生 / 缺 podman-compose）
- `__init__.py` 注册 quant 命名空间；pyproject `[compose]` extra；新规则 `.agents/rules/quant-overlay.md`（C11）；AGENTS/README/.agents 索引/.env.example/CHANGELOG 同步

**V 对抗门（实测暴露并修复）**：① RELEASE 写 onnx-simplifier「v0.7.3」但 PyPI 最高发行版 0.5.0——构建实证 0.5.0 sdist 拉取 onnxsim-0.7.3 wheel（包版本≠模块版本串），按索引实证改 pin 并留注释；② buildah 对 shell-form RUN `bash -lc '<body>'` 二次分词切断内联 `python -c "…\"…\""` 嵌套引号（宿主 bash 同写法通过、构建器内失败）——守卫固化为 smoke/_quant_guards.py，RUN 不写内层双引号。

**验收点（podman machine Fedora43 / podman 5.7.1 实测）**：① 构建 exit=0，五包版本打印 + 三守卫 PASS + 构建期 3 冒烟 PASS（INT8 max_diff=0.001914 / FP16 0.000211 / QDQ 节点=10 diff=0.014510）+ devuser 访问 PASS；② 真实 podman-compose config 双文件渲染：默认含 cgroupns/label=disable//dev/fuse，叠加后 devices=[/dev/fuse,/dev/dri] 无重复；③ `inv quant.up` 后 2222 SSH banner / 8888 HTTP 302 可达；④ compose exec 路径冒烟 3/3；down 后容器与网络零残留；栈未运行时 `podman run --rm` 兜底路径 3/3；⑤ 标签接缝 `podman ps --filter label=io.podman.compose.project=onnx-quantized` 命中；⑥ 原 17 任务零回归（总数 23）；Windows 门禁/缺二进制门禁均 Exit(1) 且文案可执行；⑦ 源 variants/onnx-quantized/ 目录零改动。

### 2026-09-12 · `fix:` inv run 在 UID≠1000 的原生 Linux 必现 exit=125（B-scheme UID 动态推导 + socket 预检自愈 + C-I5）

**关联七概念场景**：场景2「问题解决」（F→V→C→R→I→E，强制 V 门）；原生 Linux（宿主 uid=1006，podman 3.4.4）执行 `python -m invoke run`，CLI 拼出 `-v /run/user/1000/podman/podman.sock:...`，podman 报 `Error: statfs /run/user/1000/podman/podman.sock: no such file or directory` exit=125；随后被 C-I3 透传诊断误分类，提示用户"去掉 --wayland/--gpu 开关"（本次未启用任何透传，指引完全无关）。

**F 阶段根因（三层，逐层实测）**：
1. **UID 硬编码**：`podman_sock_path()`/`host_runtime_dir()` 默认 `PODMAN_RUNTIME_UID=1000`（WSL2 惯例），但本机 `id -u=1006`、`XDG_RUNTIME_DIR=/run/user/1006`；挂载源路径直接不存在。
2. **socket 服务未运行**：即便路径改为 1006，`podman.socket` 用户单元状态为 enabled-but-inactive，socket 文件不存在（本机 podman CLI 直连 daemon 不需要它，但 B-scheme 容器经 REST socket 复用宿主 daemon，必需）。实测 `systemctl --user start podman.socket` 后文件生成（0660）、`_ping` HTTP 200。
3. **诊断误分类**：B-scheme socket 是**必选核心挂载**，却与 wayland/gpu 等 opt-in 透传共用 C-I3 匹配（关键字仅为 statfs+ENOENT），输出无关修复动作。

**V 对抗门（4 视角）关键裁决**：① Windows 原生默认必须保留 1000（本机 UID 无意义，daemon 在 WSL2/Machine 远端），POSIX 才取运行时事实；② 自愈仅限用户级 systemd 单元（免提权、可逆、10s 超时），容器内（`HOST_PODMAN_SOCK` 已注入）、非 Linux、非 podman runtime 一律放行不动作；③ 容器内 entrypoint B-scheme 分支经核实**路径无关**（消费 HOST_PODMAN_SOCK 变量 + userns 属组映射 + devuser 读写自检），UID 1006 实测通过，无需重建镜像；④ C-I3 对 `podman.sock` 路径必须静默，SDK/CLI 两处异常分流先判 C-I5。

**修复点（C 原子交付）**：
- `utils.py`：新增 `host_runtime_uid()`（优先级：显式 `PODMAN_RUNTIME_UID` → POSIX `$XDG_RUNTIME_DIR` 末段 → `os.getuid()` → Windows 1000）作为唯一事实源，`podman_sock_path()`/`host_runtime_dir()` 改为消费它；新增 `ensure_host_podman_socket()`（缺失时自动 `systemctl --user start podman.socket`，返回 `(就绪, 明细, 是否自愈)`）与 `bsock_missing_guidance()`（C-I5 三步指引）；`passthrough_diagnose_hint()` 对 podman.sock 返回空串。
- `client_core.py`：`run_container()` 在 runtime 就绪检查后接入预检（失败 fail-fast，自愈成功打印 `[Run][B-scheme]` 日志）；`_run_via_sdk` 与 CLI except 两处先 C-I5 后 C-I3。

**预防**：规则 `invoke-tasks.md` 新增 S6 硬约束与 §6 第 5 条 B-scheme 回归门（UID 四优先级断言 + 自愈第三元为 True + C-I3 对 podman.sock 必须静默）；`.env.example` 补 `PODMAN_RUNTIME_UID` 文档；README §5.4 新增 C-I5 行。

**验收点**：① 制造 socket 缺失后 `ensure_host_podman_socket()` 返回 `(True, '', True)`；② `invoke run` 端到端 exit=0，挂载 `-v /run/user/1006/podman/podman.sock:...`；③ 容器 entrypoint 日志 `[B-scheme] [OK] devuser can read/write host podman socket`；④ 容器内 devuser 经 socket `_ping` HTTP 200、REST `GET /images/json` 列出宿主 8 个镜像；⑤ C-I3 对 podman.sock 报错返回空串、C-I5 正常输出；⑥ py_compile 与 GetDiagnostics 零告警。

**遗留观察（不在本次范围）**：宿主 podman 3.4.4 的 REST 服务仅响应 Docker 兼容端点（`/images/json` 200），`/libpod/*` 返回 404——这是宿主端 podman-py SDK 恒降级 CLI 的根因；容器内 v5 podman 经 B-scheme 调 libpod 端点可能同样受限，升级宿主 podman ≥4 可解，属环境升级决策（L2）。

### 2026-09-12 · `fix:` inv load 在 POSIX 平台必现 exit=125（CLI 喂入方式平台分流 + C-I4 诊断）

**关联七概念场景**：场景2「问题解决」（F→V→C→R→I→E，强制 V 门）；Linux 原生（podman 3.4.4）执行 `python -m invoke load`，SDK 按设计降级 CLI 后，CLI 报 `Error: payload does not match any of the supported image formats (oci, oci-archive, dir, docker-archive)`，exit=125。

**F 阶段根因（两层独立故障，G1 事实门 24 条）**：
1. **跨平台命令漂移（主因）**：`_load_via_cli` 无条件拼接 `type "<tar>" | podman load`。`type` 是 Windows cmd.exe 的读文件命令；在 POSIX shell 中是"显示命令类型"内建——zsh 向 stdout 回显路径文本（实测 243B）、bash 向 stderr 报 not found，送给 podman 的根本不是 tar 字节流。该写法违反 `invoke-tasks.md §3.2` 自身契约（规定 `load -i`）。
2. **podman 3.4.x stdin 路径缺陷（次因，排除"把 type 换成 cat 即可"的想当然修复）**：实测同机同归档 `cat <tar> | podman load` 仍在 Copying 4 个 blob 后报同样错误，而 `podman load -i <tar>` 成功（`Loaded image(s)`，1.96GB 归档完好：23 层 + manifest.json docker-archive，外层 tar 遍历无错）。
3. 诊断盲区：失败兜底只输出 `[CLI] load 命令执行失败（exit=125）`，丢弃 podman 原生 stderr，排查者零信息增量。

**V 对抗门（4 视角）关键裁决**：① Windows 原生**不得**跟随改 `-i`——有 Windows→WSL2 远距 daemon 大文件 EOF 历史实测，保留 `type |` 管道；② WSL2 **内部** platform=Linux 走 `-i` 正确（EOF 问题仅限 Windows 原生 CPython）；③ 成功判定子串 "Loaded image" 同时兼容 podman 3.x（"Loaded image(s):"）与 4/5.x（"Loaded image:"）；④ 不触碰 SDK 候选链（C8 A/B 维度分离），SDK 在本机不可用（podman 3.4.4 无 active socket）属设计内降级，CLI 是 C4 承诺的保底路径。

**修复点（C 原子交付）**：
- `utils.py`：新增 `image_load_cli_command(runtime, tar_path)` 作为跨平台 load 命令唯一事实源（Windows=`type |`，POSIX=`load -i`），docstring 固化双向硬约束。
- `client_core.py::_load_via_cli`：改调 helper（消除硬编码 `type`）；新增 **C-I4** "payload does not match" 中文诊断分支（tar tf 自检 → 手动 `-i` 复核 → 升级/重存 三步指引）；最终失败消息携带 podman 原生 stderr 末行，消除诊断盲区。

**预防（为什么下次不会再出现）**：① 平台分流收敛到单一 helper，规则 `invoke-tasks.md §3.2 调用链表 / §3.3 load 专项契约（6 条）/ §5-S5 / §6 第 4 条平台分流回归门` 同步为强制契约并记录"严禁 POSIX 用 type/cat 管道"的实测依据，review 时可直接对照；② 同类错误（归档/喂入/版本三因素同表象）已有 C-I4 自动翻译，不再退回裸 exit=125。

**闭环**：README §5.4 速查表新增 C-I4 行（标题更新为 C-I1~C-I4）；AGENTS.md 变更日志追加摘要。

**验收点**：① `python -m invoke load` 在 Linux + podman 3.4.4 端到端成功（`Loaded image(s): localhost/jupyter-podman-client:latest`）；② `invoke images` CLI 降级表格正常；③ `python -m py_compile` 零告警；④ Windows 路径命令字符串保持 `type ... | podman.exe load` 不变（静态核对）。

### 2026-09-11 · `fix:` inv load 支持 .tar 未压缩产物（save 降级契约同步）

**关联七概念场景**：场景2「问题解决」（I→F→V→C）；`inv load` 报「缓存目录中未找到 tar.gz」，但上轮 `invoke save` 在 Windows 原生（无 gzip）已降级产出 `.tar`——**save 三档降级新增但 load 搜索未同步**，构成 save/load 扩展名契约断裂。

**F 阶段根因**：`find_latest_image_tar()` 仅 glob `*.tar.gz`（构建端 jpman save 时代的单一产物形态）；save 增加 `.tar` 降级后搜索模式未随之扩展 → 缓存中存在有效备份但 load 找不到。

**修复点**：`utils.py::find_latest_image_tar` 改为双扩展名 `("*.tar.gz", "*.tar")` 搜索（跳过 symlink 逻辑保留）；`_load_via_cli` 的 `type <file> | podman load` 管道天然兼容未压缩 tar，无需改动。

**预防**：save 新增产物形态时必须同步 load 搜索契约（save/load 扩展名白名单一致）；README §4.1 已声明双扩展名产物。

**验收点**：① `inv load` 在仅含 `.tar` 缓存时成功加载（实测 `Loaded image: localhost/jupyter-podman-client:latest`）；② py_compile 零告警；③ 双扩展名产物并存时按 mtime 取最新。

> **2026-09-12 更正**：本条「`type <file> | podman load` 管道天然兼容未压缩 tar，无需改动」的判断仅在 Windows 原生成立，在 POSIX 被证伪（`type` 非读文件命令 + podman 3.4.x stdin 缺陷），详见 2026-09-12 C-I4 条目。

### 2026-09-11 · `feat:` 新增 invoke save 导出镜像到缓存（备份/恢复闭环）

**关联七概念场景**：场景3「重构优化」（F→A→V→C）；client 已有 load/run/stop/status/clean 但缺 save（只消费不产出），镜像备份需绕道构建端 jpman。

**F 阶段设计（对齐构建端 `bin/jpman cmd_save` 规范）**：
- 产物命名 `<镜像名>-<short_id>-<YYYYMMDD-HHMMSS>.tar.gz`；无 gzip/pigz 时降级 `.tar` 未压缩（Windows 原生 cmd/PowerShell 无 gzip 命令，`| gzip` 管道 exit 255）
- 写 `manifest.txt` 段（IMAGE_FILE/SIZE/SHA256/SAVED），与 `validate_manifest_integrity` 解析格式互操作
- `gzip -t` 完整性校验 + SHA256 摘要 + `*-latest` 软链接

**修复点**（A 阶段原子拆分）：
- `client_core.py`：`save_image()` + `_save_via_cli()`（pigz>gzip>未压缩三档降级）+ `_image_exists_fast()` + `_check_gzip_integrity()` + `_append_manifest()`
- `manage.py`：`save` 任务（`--tag`/`--cache-dir`，默认 .env IMAGE_TAG）
- `__init__.py`：根命名空间与 `container.*` 别名注册（7 命令）
- README §4 命令表 + §4.1 备份/恢复小节

**V 对抗审查发现的陷阱（均已修复）**：① digest 形如 `sha256:xxx` 含冒号 → 进入文件名/命令在 Windows shell 破坏 → 去前缀取前 12 位；② `Path.with_suffix` 在 `.tar.gz` 上产生 `.tar.tar` 双后缀 → 统一由 save_image 决定扩展名；③ `run_cmd` 文本捕获会损坏二进制 → 压缩走 shell 管道落文件、未压缩走 `podman save -o` 直接落盘。

**验收点**：① `invoke --list` 出现 `save` 与 `container.save`；② `invoke save` 成功落盘 1872MB tar + manifest + SHA256；③ 无 gzip 环境降级 `.tar` 成功；④ 与 `invoke load`/`bin/jpman load` 格式互兼容。

### 2026-09-11 · `feat:` run 新增 --rebuild-layer 自动重建叠加层（基底陈旧一键恢复）

**关联七概念场景**：场景4「知识沉淀」（R→I→E→V→C）+ 场景3「重构优化」混合；上一轮修复了「叠加层基底陈旧」警告的根因（重建镜像消除），本次沉淀机制文档并落地 B 档预防方案。

**F 阶段机制：基底先固定后更新**——镜像 tag 是移动指针，叠加层固化的是 digest（不可变指纹）：`env.build-layer` 构建时经 `--build-arg BASE_DIGEST` 把基底 digest 烤进 LABEL；run 前 `_warn_if_layer_stale` 比对 LABEL 固化值 vs 基底当前值，不一致即中文警告。只警告不阻断（旧基底可能是有意选择）。

**修复点**（B 档半自动）：
- `env_in_container.py`：把 `build_layer` 核心逻辑提取为 `rebuild_client_layer()`（返回 bool，不吞异常）；`build_layer` 任务改为其薄包装（失败仍 Exit）
- `manage.py::_warn_if_layer_stale`：返回值从 None 改为 bool（True=陈旧/无指纹），供调用方决策
- `manage.py::run`：新增 `--rebuild-layer` 标志——检测到陈旧时自动重建叠加层，**重建失败回退旧基底启动**（不因构建失败阻断容器）
- README §10.5：新增「叠加层基底指纹防陈旧机制」文档（三环节闭环 + 一键恢复命令 + JPUMAN_SKIP_BASE_CHECK 静默）
- rules/invoke-tasks.md：run 参数契约表补 `--rebuild-layer`

**V 对抗审查要点**：拒绝 C 档（构建端 post-build 自动重链叠加层）——破坏构建端/消费端解耦、引入构建风暴；B 档保留「检测不阻断、修复可执行」哲学；`run_cmd warn=True` 使重建失败返回 Result 可判，确保回退分支可达。

**验收点**：① `invoke run --help` 出现 `--rebuild-layer`；② `_warn_if_layer_stale` 5 分支单测全过（SKIP=1/陈旧/非叠加/无指纹/新鲜）；③ py_compile 两文件零告警；④ README §10.5 与 rules 参数表同步。

### 2026-09-11 · `fix:` SDK 在 Windows 原生结构性不可用诊断为 W-I4 + P2 显式 Machine SSH URI

**关联七概念场景**：场景2「问题解决」（F→V→C→R→I→E）；`inv run`/`inv images` 在 Windows 11 原生 CPython（py314t）持续打印「SDK路径不可用（首候选=P1-wsl-9p AttributeError）」且降级原因不明。

**F 阶段根因链（5-Why）**：
1. 现象：首候选 P1-wsl-9p AttributeError → 但实际 `os` 无 `getuid`（`AttributeError: module 'os' has no attribute 'getuid'`）
2. 为什么 from_env 被调用？→ P1/P2 候选 `base_url=None` 时 `get_client` 走 `_podman_sdk.from_env()`
3. 为什么 from_env 崩？→ podman-py `podman/api/path_utils.py::get_runtime_dir()` L20 调 `os.getuid()`（POSIX 专属，Windows 无此属性）
4. 为什么即使显式 ssh:// 仍崩？→ podman-py `podman/api/uds.py::UDSSocket.__init__` L34 调 `socket.socket(socket.AF_UNIX, ...)`（py314t 实测无 `AF_UNIX`）——Windows 原生下 unix/ssh 适配**皆不可用**（结构性，非配置问题）
5. 为什么 P2-machine 也没救？→ 原实现 base_url=None → from_env，撞同一 AttributeError；日志仅笼统显示「首候选=P1-wsl-9p AttributeError」未归因

**修复点**（C 阶段原子拆分）：
- `utils.py`：新增 `machine_connection_uri()`（`podman system connection list --format json` → Default=true 连接 URI，lru_cache）；`sdk_base_url_candidates` 的 P2-machine 候选在 Windows 原生改用显式 ssh://（实测返回 `ssh://user@127.0.0.1:63851/run/user/1000/podman/podman.sock`），规避 from_env 崩溃
- `utils.py::windows_diagnose_hint`：新增 **W-I4** 分支（`AttributeError` + `getuid`/`AF_UNIX`）——明确「结构性不可用、与配置无关、已自动降级 CLI fallback」
- `.env` / `.env.example`：`WSL_DISTRO_NAME=Ubuntu` → `podman-machine-default`（本机 `wsl.exe --list --quiet` 实测发行版名；原值不存在导致 P1 探测失败前置误导）
- README §5.4 / rules/windows-wsl.md §5：W-I1~W-I3 → W-I1~W-I4（三处同步）

**V 对抗审查要点**：改 vendor/podman-py（third_party 只读子模块）被否——即使修复 `os.getuid()`，`AF_UNIX` 依旧缺失，SDK 在任何 scheme 下都不可用，治标不治本；正确闭环是「识别 + 显式提示 + 自动 CLI fallback」。

**验收点**：① `inv images` 在 py314t 正常输出镜像表（降级一行提示，非错误）；② `PODMAN_CLIENT_LOG_LEVEL=DEBUG inv images` 打印 W-I4 全量根因与 30 秒修复；③ `machine_connection_uri()` 返回非空 ssh://；④ README §5.4 / windows-wsl.md §5 / utils.py 三处 W-I4 描述一致；⑤ `py_compile` 两文件零告警。

### 2026-09-11 · `feat:` 新增 --video 透传（UVC 摄像头字符设备）

**关联七概念场景**：场景3「重构优化」（I→F→A→C）；USB 透传仅总线级（容器内 lsusb 可见但无 /dev/video*），摄像头采集（v4l2/OpenCV）需字符设备。

**I 阶段根因**：`--usb` 透传 `/dev/bus/usb`（总线级），UVC 摄像头需 `/dev/video<n>` 字符设备。

**修复点**（A 阶段原子拆分）：
- `utils.py`：`passthrough_paths()` 增 `video_devices`（`VIDEO_DEVICES` env，逗号分隔，默认 `/dev/video0-3`）；`build_passthrough_spec` 增 video 分支（每设备 `--device <d>:<d>` 同名映射）；`ContainerConfig` 增 `video=False`
- `manage.py`：run 增 `--video/--no-video` 三态 + `.env` 键 `PASSTHROUGH_VIDEO` + help
- `client_core.py`：透传摘要打印补 video
- 文档：`.env`/`.env.example` 增 PASSTHROUGH_VIDEO 与 VIDEO_DEVICES 说明；README §11 表格补 ⑥ 行 + §11.3 增 Video 段落（回写原"已知边界"为已支持）

**验收点**：① `inv run --help` 出现 `--video/--no-video`；② 重启后 run 命令含 `--device /dev/video0-3` 四项；③ 容器内 `/dev/video0-3` 字符设备存在，`head -c1` 打开成功（EINVAL 为非协商格式预期行为）；④ 容器内 `fcntl.ioctl(QUERYCAP)` 返回 `driver=uvcvideo card=Integrated RGB Camera`（uvcvideo 驱动探活成功）；⑤ 透传摘要显示 `video`。

### 2026-09-11 · `docs:` 透传部署文档固化（WSLg Wayland / CDI GPU / usbipd USB 前置）

**关联七概念场景**：场景4「知识沉淀」（R→I→E）；三项透传（Wayland/GPU/USB）在 NVIDIA WSL2 podman machine 实测跑通后，把宿主侧前置固化为文档，避免操作者凭记忆重试。

**沉淀内容**：
- README 新增 §11.3「三大透传的宿主侧前置」：WSLg Wayland（`HOST_XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir` 关键路径）、NVIDIA GPU（CDI `nvidia-ctk cdi generate` + `GPU_DEVICE=nvidia.com/gpu=all`）、USB（usbipd-win bind/attach + VM 内确认/排障）
- `.env.example` 同步：WSLg Wayland 注释、GPU 双形态、USB 前提步骤

**验收点**：文档命令与实测路径一致（`/mnt/wslg/runtime-dir/wayland-0`、`/etc/cdi/nvidia.yaml`、`usbipd attach --wsl podman-machine-default`）；container 内验证命令可用（printenv/nvidia-smi/lsusb）。

### 2026-09-11 · `feat:` GPU 透传支持 CDI 设备引用（NVIDIA）

**关联七概念场景**：场景2「问题解决」（I→F→V→C）；`inv run --gpu` 在 NVIDIA WSL2 podman machine 上失败 `stat /dev/dri: no such file or directory`（VM 无 `/dev/dri`，GPU 走 `/dev/dxg` DXCore）。

**I 阶段根因**：client 侧 GPU 透传固定拼 `GPU_DEVICE:/dev/dri`（设备节点路径）。NVIDIA WSL2 下不存在 `/dev/dri`，需走 **CDI**（`nvidia-ctk cdi generate` → `/etc/cdi/nvidia.yaml` → `--device nvidia.com/gpu=all`，自动挂载 `/dev/dxg` + `/usr/lib/wsl/lib/libcuda*`）。

**修复点**：`utils.py::build_passthrough_spec` GPU 分支按形态分派——`GPU_DEVICE` 以 `/` 开头（设备路径，默认 `/dev/dri`）→ 映射容器内 `/dev/dri`；否则视为 CDI 引用（如 `nvidia.com/gpu=all`）→ 原样透传。

**验收点**：① `GPU_DEVICE=nvidia.com/gpu=all inv run --gpu` 启动成功（`--device nvidia.com/gpu=all` 出现在 run 命令）；② 容器内 `nvidia-smi` 输出 `NVIDIA-SMI 580.102.01 / Driver 581.57 / CUDA 13.0`；③ 端口映射模式 jupyter/sshd RUNNING、HTTP 200；④ `/dev/dri` 路径形态分支保持兼容（startswith("/") 判据）。

### 2026-09-11 · `chore:` 基底联动重建（devuser UID 固定 1000 + B-scheme socket 修复 + :toolbx 变体）

**关联七概念场景**：场景2 后置联动（构建端 spec：`.trae/specs/infra-env/toolbx-host-image/`）。

构建端当日交付三项变更（devuser 固定 UID 1000、entrypoint socket 属主穿透修复、`:toolbx` 变体），client 侧经**基底指纹机制**（同日早些时候上线）自然驱动联动：`inv env.build-layer` 重建叠加层，烤入新基底 digest `sha256:2826166e…`（与 rootless:latest 逐字符一致）；`inv stop && inv run` 重启 jupyter-podman（沿用既有 JUPYTER_TOKEN/USER_PASSWORD，浏览器/SSH 零感知）。

**本侧代码改动**：仅文档/注释——`README.md` §10.4「默认用户」改为"固定 UID/GID 1000"；`Containerfile.client` V 阶段注释中"UID 自动分配（如 1001）"改写。无任务代码改动（指纹检测首次实战即正确触发，无陈旧误报/漏报）。

**验收点**：容器内 `id -u devuser`=1000；supervisorctl jupyter/sshd RUNNING；Jupyter HTTP 200；容器内 `toolbox create` 仍为 wrapper 中文指引；`invoke run` 无陈旧告警；base-digest label == 基底 Digest（DIGEST_MATCH）。

### 2026-09-11 · `fix:` 叠加层基底指纹与陈旧检测（toolbox wrapper 缺席事故闭环）

**关联七概念场景**：场景2「问题解决」（F→V→C→R→I→E 链路）；用户在 client 容器（8eddb24390eb）内执行 `toolbox create` 仍裸报 `Error: TOOLBOX_PATH not set`，而构建端前一日已交付 wrapper 优雅降级。

**F 阶段根因（5-Why 终局）**：client 叠加镜像在构建时刻固化基底（`FROM localhost/jupyter-podman-rootless:latest`）；rootless 基底重建（含 toolbox-wrapper.sh 与 flatpak-spawn 补装）后 tag 移动**不传导**给已存在的 overlay——当日 client:latest（CST 11:29 构建）比新基底（CST 16:22）早 5 小时，容器内 `/usr/local/bin/toolbox` 仍是 11.2 MB 裸 ELF、`/usr/local/libexec/toolbox` 不存在。系统性根因：base→overlay 镜像谱系无基底指纹，「重建基底后必须重建叠加层」只存在于操作者脑中，`run` 只验镜像「存在」不验「新鲜」。

**上游事实（vendor/toolbox/src/cmd/root.go:160-173）**：容器内（`/run/.containerenv` 存在）`TOOLBOX_PATH` 为空即硬错误；该变量由宿主 Toolbx 启动器注入，用于把宿主二进制挂入新容器并经 `flatpak-spawn --host` 回调宿主。**普通 podman 会话内 `toolbox create` 架构上不可用**，wrapper 退出码 1 + 中文指引是正确行为而非失败。

**修复点**：基于新 rootless:latest 重建 client 叠加层并 stop/run 替换容器（保留原 JUPYTER_TOKEN/USER_PASSWORD，浏览器访问与 SSH 凭据不变）；验证 `toolbox --version` 透传输出 `toolbox version 0.3`、`toolbox create` 输出中文指引。

**预防（C10 闭环）**：

1. `Containerfile.client` 末尾新增薄层 `LABEL org.specweave.base-image/base-digest`（置于末尾不使前置 COPY/RUN 缓存失效）
2. `env_in_container.py::build_layer` 构建前自动采集基底 digest 经 `--build-arg BASE_DIGEST` 烤入标签
3. `client_core.py` 新增 `image_inspect_info()`（走原始 JSON 而非 --format 模板，规避 Windows cmd / Linux bash 双 shell 引号与 `$` 展开差异）
4. `manage.py::run` 启动前新增 `_warn_if_layer_stale()`：仅对 `org.specweave.component=jupyter-podman-client` 镜像比对烤入 digest 与基底当前 digest，陈旧/无指纹时中文告警并给出 `invoke env.build-layer && invoke stop && invoke run` 完整命令，**只警告不阻断**；`JPUMAN_SKIP_BASE_CHECK=1` 逃生（`.env.example` 已登记）；`load` 成功后同步一次性提示
5. 任何 inspect 异常静默降级，不影响 run 主流程

**验收点**：① 新镜像 label 中 base-digest 与 rootless 当前 digest 逐字符一致；② 四分支实测：指纹一致静默 / monkeypatch 陈旧正确告警 / skip 静默 / 非 client 镜像静默；③ 重建容器内 wrapper + flatpak-spawn 齐备；④ `py_compile` 三文件全过。

### 2026-09-10 · `fix:` 布尔参数三态化 + `run` 任务关闭自动短选项（含对上一提交声明的更正）

**关联七概念场景**：场景2「问题解决」（I→F→V→C 链路）；I 阶段读 invoke 3.0.3 源码定位根因，F 阶段确立可行解，V 阶段以「单元级 6 场景 + CLI 实跑」逐条证伪

**I 阶段根因（源码 + 实测）**：

1. `invoke/tasks.py:223-231`：`Argument.kind` **仅由 `type(default)` 推断** → 默认写 `None` 会让 kind 退化为 `str`，旗标变成「需取值」而非开关 → **三态哨兵不可行**
2. `invoke/parser/argument.py:127`：`value` 在未赋值时回落 `default` → **「未指定」与「显式 False」不可区分**
3. `invoke/parser/context.py:150`：反向旗标 `--no-<flag>` **仅在 `default is True`** 时自动生成
4. `invoke/tasks.py:215-220`：短名生成 = 「逐字符取首个未被占用字符」，**与参数顺序耦合** → 实测 `-h` 被 `ssh_public_key` 抢走（`invoke run -h` 报 `needed value`）、`host_network` 退化到短名 `-`、`--gpu` 无可用字符

**更正声明**：上一提交（同步运行时透传）中「修复 `GRANT_SUDO=no` 因 `bool("no")` 判真而失效」**实际未生效**——`_env_bool()` 只修正了文本解析，但 `grant_sudo` 的 invoke 默认值为 `True`，未指定时 `Argument.value` 直接回落 `True`，`.env` 根本不被读取。本次才真正闭环。

**验收点**（原子提交单一职责，可独立验证）：

A. **三态解析**：新增 `manage.py::_resolve_bool(on_val, off_val, env, env_key, default, flag)`；每个布尔项配对 `--x` / `--no-x`（`grant-sudo` 的 CLI 面保持 `--grant-sudo` / `--no-grant-sudo` 不变）；同开同关报「参数冲突」
B. **短选项契约**：`run` 任务 `@task(..., auto_shortflags=False)` → `invoke run -h` 恢复输出帮助，自动短名全部取消，长选项成为唯一公开契约
C. **规则固化**：`.agents/rules/invoke-tasks.md` 新增「布尔项三态规则」与「短选项规则」两条**违反打回**约束

**验证证据**：

- 单元级 6 场景全对：未指定取 `.env`（`grant_sudo=False` / `gpu=True`）、`--gpu` 开、**`--no-gpu` 覆盖 `.env` 的 yes**、`--grant-sudo` 覆盖 `.env` 的 no、`--no-grant-sudo` 关、`--gpu --no-gpu` 被拦截
- CLI 实测：`invoke run -h` 输出 Usage（不再报错）；`^\s{2}-[a-z],` 无匹配 = 自动短名已全部消除；`--no-{dbus,gpu,grant-sudo,host-network,usb,wayland}` 六个配对旗标均已注册

### 2026-09-10 · `feat:` 同步构建端运行时透传（5 个开关 + C-I3 诊断）

**关联七概念场景**：场景5「创新突破」（F→V→I→C 链路）；F 阶段确认执行模型不同（构建端 compose 分层覆盖 → 消费端 SDK/CLI 编程式），V 阶段对抗审查产出下述关键约束

**F 阶段公理（V 已逐条验证）**：

1. 透传均为运行期参数 → 只能落在 SDK kwargs / CLI 参数，无法进镜像
2. **挂载源与设备节点由 daemon 宿主（WSL2 / Podman Machine）解析** → 客户端本机 `Path.exists()` 必然为假，**禁止本机预检**（否则误判拒绝正确请求）
3. podman 对缺失源**硬失败**（退出码 125、不自动创建）→ 只能事后把原生报错翻译为 C-I3 指引
4. `--network host` 与端口发布互斥 → 不传 `-p`；rootless 无法绑特权 22 → 自动设 `SSHD_PORT=--ssh-port`
5. 既有 P0 不可破坏：C3 rootless 三必需保留、C8 A/B 维度分离、S1~S5

**验收点**（原子提交单一职责，可独立验证）：

A. **参数构造层（新增单一事实源）**
   - `utils.py`：新增 `PassthroughSpec` + `build_passthrough_spec(cfg)` + `passthrough_paths()`（路径变量与构建端 `compose.passthrough*.yaml` 同名）+ `CONTAINER_RUNTIME_DIR`
   - `ContainerConfig` 新增 5 个布尔字段（默认全关 = 默认隔离）

B. **两条路径等价消费**：`client_core.py::_sdk_run_kwargs`（`network_mode` / `volumes` / `devices` 追加）与 `_run_via_cli`（`--network host` / `-v` / `--device`）均由同一份 spec 驱动，禁止各自拼接

C. **C-I3 诊断**：`utils.py::passthrough_diagnose_hint()` 匹配 `statfs` / `stat ... no such file or directory`，给出缺失路径 + 可覆盖变量 + daemon 侧自检命令；在 `_run_via_sdk` 与 `run_container`（CLI 异常捕获）两处挂载

D. **CLI 面**：`manage.py::run` 新增 `--host-network` / `--wayland` / `--gpu` / `--usb` / `--dbus`；新增 `_env_bool()` 修复 `bool("no")` 判真导致 `GRANT_SUDO=no` 失效的既有缺陷

E. **文档同步**：`README.md` §4 / §5.4 / §8.3 / §11、`.agents/rules/invoke-tasks.md`（§3.2 统一 spec 约束 + §4.4 命令面）、`.agents/rules/windows-wsl.md` §5（C-I3 行）

**验证证据**：单元级 5 组组合参数全部正确（默认组与旧版本零差异）；实跑 `--dbus` 容器内落到 `srw-rw-rw- /tmp/runtime-user/bus` 且两个环境变量就位；实跑 `--gpu` 触发 `Error: stat /dev/dri`（退出码 125）并打印 C-I3 指引

### 2026-09-10 · `fix:` 容器内 Podman socket EACCES（C-I2）根因修复与诊断闭环

**关联七概念场景**：场景2「问题解决」（F→V→C→R→I→E 链路）；F 根因分析后经**强制 V 对抗审查**（采纳 5 条意见：自验证 / `%G` 空回退 `%g` / 代价与红线声明 / `stat` 失败必 warn / C-I2 分支先于平台守卫）

**验收点**（原子提交单一职责，可独立验证）：

A. **消费端代码改动（SDK 侧诊断能力）**
   - `src/jpman_client/tasks/utils.py`：`podman_sock_path()` 默认 `PODMAN_RUNTIME_UID=1000` 且支持环境变量覆盖（**严禁硬编码容器内 UID**）；`windows_diagnose_hint()` 新增 **C-I2 匹配**（`permission denied` 且 socket 路径存在 → 属组修复引导），与 C-I1（`ENOENT`，socket/目录不存在）语义分离
   - `src/jpman_client/tasks/client_core.py`：异常汇总表叠加 C-I2 诊断文案，`get_client()` 失败路径不回归

B. **消费端文档对齐（三处同步）**
   - `README.md` §5.4：新增 **C-I2**「socket 存在但无权限（EACCES）」条目，与 W-I1/W-I2/W-I3/C-I1 并列（共 5 条口径）
   - `.agents/rules/windows-wsl.md` §5：C-I2 速查表（30 秒修复须为一行命令）
   - `AGENTS.md` + `.agents/README.md`：坑位索引与双向锚点同步

C. **联动修复（构建端 `jupyter-podman-rootless`，跨端引用登记以保证可追溯）**
   - `entrypoint.sh`：B-scheme 分支新增 **socket 属组自适应**——`stat` 宿主 socket 取属组名 → `usermod -aG` 加入非 root 用户 → 复验可读写；`stat` 失败必 `log_warn`（不静默）；UID 动态推导，不硬编码 1000/1001
   - `config/supervisor/conf.d/jupyter.conf`：移除硬编码 UID 1001 漂移，改 `%(ENV_CONTAINER_HOST)s` / `%(ENV_XDG_RUNTIME_DIR)s` 继承 entrypoint 动态导出值
   - `.agents/rules/entrypoint.md`：规则同步

D. **验收证据（verify 全部通过）**
   - `bash -n entrypoint.sh` ✅
   - base 镜像重建 → `701c2e509fd8`（`socket group` 关键字命中 5，旧镜像基线 0）✅
   - client 层重建 → `5ed156783148`（`User=root`；`jpman_client` editable 安装 OK）✅
   - 容器重建 → `41d46c351352` ✅
   - entrypoint 日志：`[B-scheme] Added devuser to socket group 'root' (gid 0)` + `[B-scheme] [OK] devuser can read/write host podman socket` ✅
   - 容器内 `/proc/<jupyter>/status`：`Groups: 0 27 997 1001`（gid 0 已注入）✅
   - `PodmanClient.from_env()` 成功：`podman 5.7.1`、3 容器、**无 PermissionError** ✅
   - devuser 侧 `podman images`（11 镜像）/ `podman info`（`rootless=true`、`RemoteSocket=unix:///run/user/1000/podman/podman.sock`）在显式 `CONTAINER_HOST` 下成功 ✅
   - 反证：无 `CONTAINER_HOST` 时触发 `newuidmap: write to uid_map failed`（WSL 三层 userns 限制），证明 `su -` 登录 shell 丢环境变量是历史误判来源、非 C-I2 修复失败 ✅

**根仓库 git commit**：`[52084da68](#)`

### 2026-09-09 · `fix:` 宿主 socket 直通连通 + 镜像缓存完整性 + known_hosts 维护

**关联七概念场景**：场景2「问题解决」

**验收点**：

A. **宿主 socket 直通（B-scheme）端到端连通**：容器内 devuser 经 userns 映射后可读写宿主直通 socket，`podman images` / `from_env()` 均成功
B. **镜像缓存完整性**：`validation_manifest_integrity` 修正首块误匹配，`inv load` 在缓存损坏时给出明确错误而非静默失败
C. **SSH host key 维护**：`ensure_known_hosts` 修复 Windows 路径失效；`refresh_host_keys` 改为 TCP 探测等待 sshd 就绪，并兼容 OpenSSH 10 KEX 与 host 段规范化

**根仓库 git commit**：（见对应 `fix(containers)` 系列提交）

### 2026-09-08 · `feat:` 默认镜像泛化为 client 管理枢纽 + 容器内 SDK socket ENOENT（C-I1）修复

**关联七概念场景**：场景2「问题解决」（容器内 C-I1）+ 场景3「重构优化」（镜像泛化）

**验收点**：

A. **镜像泛化与瘦身**：默认目标镜像由构建端镜像改为 `localhost/jupyter-podman-client:latest` 通用管理枢纽；叠加镜像体积 2.82 GB → 1.80 GB
B. **非 root entrypoint 修复**：修复 client 镜像以非 root 运行 `entrypoint.sh` 致 `chpasswd` 失败、容器以 `Exited (1)` 退出的问题
C. **容器内 SDK socket ENOENT（C-I1）修复**：bootstrap 路径（`env.run-cmd` / `env.shell`）由 `env_in_container.py::PODMAN_SERVICE_BOOT` 自举 `podman system service --time=0` 并预建 `${XDG_RUNTIME_DIR}/libpod/tmp`；常驻容器由 `entrypoint.sh::setup_podman()` 保证

**根仓库 git commit**：（见对应 `feat/fix(containers)` 系列提交）

### 2026-09-07 · `feat:` Windows 11 WSL2 SDK 全链路支持 + AI 自治规范容器初始化

**关联七概念场景**：场景3「重构优化」（I→F→A→C 链路）+ 场景4「知识沉淀」（从 podman-py OKF v0.2 bundles 萃取跨平台模式）

**验收点**（原子提交 C4 单一职责，可独立验证）：

A. **src/jpman_client/tasks/ 层代码改动（podman-py SDK Windows 兼容）**
   - `utils.py`：新增 SDK 逃生舱常量、`sdk_strategy_from_env()` 归一化、`_has_wsl_host_support()` 双门卫、`wsl_distro_name()` 3 级回退 UTF-16 LE 解析、`_wsl_user_uid()` 探测缓存、`BaseUrlCandidate` 数据类、`sdk_base_url_candidates()` P0→P3 序列生成、`windows_diagnose_hint()` W-I1~W-I3 速查匹配
   - `client_core.py`：重写 `get_client()` 上下文管理器接入多候选 ping 循环、失败汇总表、诊断文案叠加；CLI fallback 行为零回归（全部失败仍 `yield None`）
   - `manage.py`：`_load_env_overrides()` 修复核心 Bug——新增 `load_dotenv(override=False, encoding="utf-8")` 把 .env 同步到 os.environ，保证 SDK 级逃生舱读到 .env 变量；import 清理未使用的常量
   - `tasks/` → `src/jpman_client/tasks/` 布局迁移（消除与构建端 `jpman_builder.tasks` 的命名冲突），根 `tasks.py` 降级为纯转发层，新增 `env_in_container.py`（`env.*` 自举命名空间）
   - 静态验证：`python -m py_compile src/jpman_client/tasks/*.py` exit_code=0；VS Code `GetDiagnostics` 五文件零告警

B. **人类文档层改动（README.md + .env.example）**
   - `README.md` 新增 §5「Windows 11 × WSL2 支持」：§5.1 三路径矩阵、§5.2 四级连接优先级、§5.3 四策略逃生舱、§5.4 W-I1~W-I3 速查表、§5.5 A/B 维度分离表；原 §5→§6 / §6→§7 / §7→§8 / §8→§9 编号顺延
   - `README.md` §8「.env 配置完整清单」拆 8.1 容器级（9 项） + 8.2 SDK 级（4 项）两张表，明确优先级链：命令行 > shell export > .env > 默认
   - `.env.example` 追加 Windows WSL 专属 4 个 SDK 级变量：`PODMAN_CLIENT_SDK_STRATEGY`（含四策略注释）/ `WSL_DISTRO_NAME` / `CONTAINER_HOST` / `DOCKER_HOST`（兜底注释）
   - 双向锚点：README§5.4 ⇄ `utils.py::windows_diagnose_hint` ⇄ `.agents/rules/windows-wsl.md §5` 三处 W-I1~W-I3 条目 1:1 对应

C. **AI 协作者自治规范容器初始化（AGENTS.md + .agents/）**
   - `AGENTS.md`：消费端专属启动协议（嵌套路由 + 文档边界 + 内容敏感度预检）；项目概述；嵌套路由关系树；上下文路由表（10+ 条目）；10 条 P0 硬约束 C1~C10 违反打回清单；快速开始最小验证路径；父级引用声明；变更日志倒排
   - `.agents/README.md`：AI 资产容器索引；6 目录结构 + 3 规则文件；源代码真源表；人类文档↔AI 规则双向对应表；父级继承 7 层；新增规则 4 步流程；变更日志倒排
   - `.agents/rules/invoke-tasks.md`：消费端 invoke 开发规范；模块职责边界 5×5 禁止跨层表；两层后端架构 8 条不可变行为契约；CLI fallback 7 函数等价实现表；三命名空间（根 + `container.*` 别名 + `env.*` 自举）；6 条 P0 安全约束；3 条修改后必跑冒烟
   - `.agents/rules/sdk-connection.md`：6 合法 scheme 白名单 + npipe 严禁；Windows base_url 必显式约束；四策略逃生舱矩阵；多候选优先级序列（strategy × platform）；P1 WSL9P 生成契约（distro 3 级/UID 探测）；P3 tcp 兜底；8 条错误输出格式不可变；ImportError 降级安全
   - `.agents/rules/windows-wsl.md`：A/B 两维度分离表（核心差异）；两种用户画像；WSL 发行版名 3 级回退；UTF-16 LE 编码硬规定；_has_wsl_host_support 双门卫；UID 严禁硬编码 1000；W-I1~W-I3 三处同步对齐；.env 加载语义 override=False 红线；4 条必跑验证脚本
   - `.agents/{CHANGELOG.md,README.md,rules/*}` 其余子目录（roles/skills/scripts/workflows/templates/docs）预留 .gitkeep 占位（父级回退路径）

D. **治理承诺（七概念 G1~G4 质量门）**
   - G1（事实无因果）：所有 podman-py 行为陈述均有 OKF v0.2 bundles 原文锚定，无"应该/可能"类推断
   - G2（洞察四元组）：上一轮 WSL SDK 改造的根因分析四元组见 AGENTS.md 项目约束速览 C1~C10 后附的根因段
   - G3（模式可迁移）：从 bundles 萃取 2 个模式已落地——「Windows Podman 连接多候选自动降级」+「WSL2 发行版名 3 级回退」
   - G4（行动项原子化）：本次变更拆 A/B/C 三大原子块，可单独 revert 任意一块不影响其他块

**根仓库 git commit**：`[91c29c240](#)`
