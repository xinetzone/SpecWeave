# xmnnrt.* wheel 消费运行时栈规则（podman-compose 编排层）

> 单一职责：本文件只约束 `invoke xmnnrt.*` 命名空间与
> `overlays/xmnn-runtime/` 叠加栈。通用条款（双门禁/WSL 桥接/rootless
> 三必需/extends 基段/内核零栈知识）继承 [xmnn-overlay.md](xmnn-overlay.md)
> §1-2、§6-7 与 [quant-overlay.md](quant-overlay.md)，本文件只定义
> xmnnrt 栈特有契约。

## 1. 架构定位：builder/runtime 分离（2026-09-16）

| 维度 | xmnn-dev（构建器，`xmnn.*`） | xmnn-runtime（本栈，`xmnnrt.*`） |
|---|---|---|
| 角色 | 源码调试 + Nuitka 打 wheel | 安装预构建 wheel 的干净交付运行时 |
| 镜像 | `localhost/xmnn-dev:latest` | `localhost/xmnn-runtime:<形态>`（cpu/cu130；`:latest` 别名，C28 §8.4） |
| 工具链 | LLVM 22/Nuitka 4.2.1/gcc/gdb/ccache | 无（wheel `_libs` 自包含） |
| 源码 | 运行时 bind npu_tvm/npuusertools/models | 零源码挂载、零构建期源码接触 |
| 制品关系 | 产出 `client/workspace/dist/xmnn-*.whl` | 经 `wheels/` 暂存区 COPY 该 whl 安装 |
| ABI | base `/opt/conda` cp314 GIL 打包；main cp314t 服务 | wheel 装 **base** `/opt/conda`；main 继续只跑 Jupyter |
| 端口 | 2223/8890 | 2225/8893 |

- wheel 是两镜像间**唯一制品契约**（169 MB 量级，含 Nuitka 扩展 +
  `_libs` + bootstrap `.pth` + 数据目录 + 19 依赖元数据）。
- 两镜像 **FROM 同一基底** `localhost/jupyter-podman-rootless:latest`
  （build args `BASE_IMAGE` 可覆盖但必须 ABI 同源）；禁止 runtime
  改从 external/chaos 的 `npu-tvm-build:conda` 谱系继承
  （[apps/docker-images/xmnn-runtime](../../../../docker-images/xmnn-runtime/docker/AGENTS.md)
  是独立 Docker 谱系，ai 用户/无 SSH/Jupyter，与本栈互不复用）。
- `inv xmnn.wheel` 行为**不变**：仍只在 xmnn-dev 栈内打 whl 落
  workspace/dist；安装职责整体归属本栈，不回流 xmnn-dev（对应
  xmnn-overlay.md §9 的 scratch 栈裁决，spec 名 xmnn-overlay-rebuild
  以此落地）。

## 2. 声明式栈边界（沿用 C14）

- xmnnrt.py 禁止 `import podman`；六任务中 down/ps/logs/smoke 直接
  消费 `make_stack_tasks(XMNNRT_SPEC)` 工厂产物。
- **唯一形态差异**：build/up 在调内核 `build_image`/`up_stack` 前
  需要 whl 已暂存进 overlay 构建上下文。以与 xmnn.build-tvm/wheel
  同级的"薄封装例外"自定义该两任务：只允许调用
  `gates`/`ensure_runtime_ready`/`prepare_env`/`build_image`/
  `up_stack` 与本模块的暂存 helper，**禁止复制**门禁/argv/构建命令
  拼接逻辑；模块 ≤160 行（黄金测试断言）。
- overlay_core 零栈知识红线不变：whl 暂存是 xmnnrt 私有行为，
  不得下沉内核（其余三栈无构建上下文外制品输入）。

## 3. wheel 暂存契约（wheels/ 目录）

- 暂存区 `overlays/xmnn-runtime/wheels/`：
  - git：`wheels/.gitignore` 忽略全部 whl（产物不入 git，真实来源是
    xmnn-dev 的 workspace/dist）；
  - podman 构建上下文：`.dockerignore` **不得**排除 wheels/（whl 是
    Containerfile COPY 的必需输入，两个忽略机制互不混淆）；
  - 目录内**同一时刻只保留一个** xmnn whl（`_copy_into_stage` 拷贝前
    清空旧文件），保证 `COPY wheels/xmnn-*.whl` 的 glob 确定性。
- 选择顺序（`_ensure_wheel_staged`）：
  1. `--wheel <path>` 显式指定：校验是 `xmnn-*.whl` 普通文件后强制
     替换暂存（无效路径 Exit 1，不静默回退）；
  2. `client/workspace/dist/` 存在 whl：取 mtime 最新；与暂存区同名
     则跳过拷贝，否则替换（up 默认跟随 dist 最新，避免装旧 wheel）；
  3. dist 无 whl 但暂存区有：复用并打印提示；
  4. 两处都无：Exit 1 + 中文指引（先 `invoke xmnn.wheel`）。
- `xmnnrt.up` 默认随带构建，构建前自动跑第 2-4 步；`--skip-build`
  既不暂存也不构建，直接消费本地已有镜像——缺失立即 Exit 1 并给中文
  指引（C16：compose 的 `build:` 段不再兜底构建，`up` 恒 `--no-build`）。
- 禁止用 BuildKit `--mount=type=bind` 直接挂 dist/ 或宿主 whl
  （构建必须可脱离 9p 源码树复现，与 xmnn-dev §4 同纪律）。

## 4. Containerfile 契约

- 薄叠加，不覆盖 ENTRYPOINT/CMD/WORKDIR；全部 RUN 显式
  `/bin/bash -lc`；含引号验证逻辑只能进 smoke/scripts 脚本文件
  （OCI 二次分词教训）。
- 安装解释器固定 `/opt/conda/bin/python`（cp314 GIL）；wheel tag 为
  cp314-cp314，**禁止装入 main env**（cp314t 不接受该 wheel tag）。
- 同层显式安装 `ipykernel`（基底 base env 默认无；Jupyter 内核
  launch 需要）；wheel 的运行时依赖由 pip 按元数据自动解析，
  不在 Containerfile 重复维护清单。
- **依赖版本漂移边界**：元数据为开放区间（`numpy>=1.26` 等），运行时
  解析的小版本集合可能异于构建器当次环境；可复现交付的版本锁定是
  wheel 打包端（xmnn-dev pyproject/constraints）职责，本栈不 pin、
  不以 `==` 重写依赖（避免双事实源）。
- **whl COPY 层冗余已知**：单阶段保留约 170 MB 的 COPY 层（rm 不回收
  层体积）；优化需改双阶段，属未来增强而非缺陷（2026-09-16 实测镜像
  3.18 GB，含内置 torch CPU；xmnn-dev 4.69 GB）。
- 禁止安装 LLVM/Clang/Nuitka/gcc/gdb/patchelf 等构建器工具；运行时
  对 libLLVM 的需求由 wheel `_libs`（RPATH `$ORIGIN`）满足。
- **torch 内置层形态可选（Layer 1；2026-09-16 起内置，2026-09-20 起形态可选，C26）**：
  `ARG TORCH_VERSION=2.14.0` 精确 pin；形态 `ARG TORCH_FLAVOR`（白名单
  `""|cpu|cu130`，**缺省 cpu**——与 xmnn-dev 的「空=不装」语义相反，缺省由
  `StackSpec.torch_default` 声明，compose 段 `${TORCH_FLAVOR:-cpu}` 同默认，
  详见 §8 与 C15）。安装逻辑在 `scripts/install-torch.sh`（**独立成层**且位于
  whl 层之前，重打 whl 增量构建复用该层）；**索引由形态推导**
  （`download.pytorch.org/whl/<flavor>`）而**不是**独立 ARG——默认 PyPI/tuna/
  aliyun 的 torch 是 CUDA 变体，会拉 nvidia 大包，严禁换源，且独立的
  `TORCH_INDEX_URL` 会制造「形态 vs 索引」两处事实源。形态落盘
  `/opt/xmnnrt-torch-flavor` 供守卫第 10 项断言「声明 vs 实物」（守卫在镜像内
  读不到 LABEL）。只装 torch，不装 torchvision（compile_api 仅 torch.jit.load +
  relay 前端，实测不需要）；`cu130` **不随带 nvcc**（本栈 P0 禁编译器工具链，
  需 nvcc 编译 CUDA 内核请回 xmnn-dev 栈，其 cu130 经 C25 提供）。升级 torch：
  同时改 Containerfile ARG 与 smoke `_EXPECTED_TORCH_MAJOR`。
- wheel 自带 `_xmnn_bootstrap.py` + `xmnn_bootstrap.pth`（builder
  CMakeLists 已 install 进 wheel），**不得**在 runtime 额外 COPY
  任何 bootstrap/init 文件（与 docker-images/xmnn-runtime 的
  `_xmnn_init.py` 谱系区分，勿跨谱系搬运）。

## 5. Jupyter 内核契约

- 内核名 `xmnn-runtime`，display `Python 3.14 (xmnn runtime)`，
  注册位置 `/opt/conda/envs/main/share/jupyter/kernels/xmnn-runtime/`
  （main env jupyter 可见，root/devuser 双可见）。
- argv[0] 固定 `/opt/conda/bin/python`；kernel.json 的 env **只允许
  PATH**：不得注入 PYTHONPATH/TVM_LIBRARY_PATH/LD_LIBRARY_PATH
  （交付语义=无源码、无 conda lib 路径的干净运行时）；守卫脚本
  对这两项做反向断言。

## 6. 守卫契约（10 项硬验证）

- `smoke/_runtime_smoke.py` 烤入 `/opt/xmnnrt-smoke/`，构建期 root +
  devuser 双身份执行（任一失败镜像构建失败，不允许 WARNING 放行）；
  栈运行路径经 compose exec 复跑，未运行时 `podman run --rm
  --entrypoint /opt/conda/bin/python` 独立执行（SmokeSpec 双路径）。
- 与 xmnn-dev verify-wheel.sh 的本质区别：本守卫**直接在 base env
  导入已安装 wheel**（非临时 venv、非 --no-deps），等价真实客户机
  首次启动；并断言模块路径不含 `/workspace/`、`/opt/xmnn-builder`。
- tvm.build('llvm') 算例是自包含性的最终证明（镜像无系统 LLVM）。
- 第 10 项是**形态一致性**判据（C26）：读 `/opt/xmnnrt-torch-flavor`
  marker → `""` 断言不可 import torch；`cpu` 断言 `torch.version.cuda
  is None` 且 `cuda.is_available() is False`；`cu130` 断言
  `torch.version.cuda is not None`。**禁止**把判据写死为 CPU-only——
  `build --torch cu130` 会在守卫处误报失败；反过来只断言「能 import」
  又会放过「声明 cpu 却装了 CUDA 包」的错版（错版只在运行期浮现）。
  CUDA 形态**刻意不断言** `cuda.is_available()`：设备是运行期维度
  （C19），构建期无 GPU 属正常，该值仅作 INFO 打印。
- **standalone 路径可用性依赖一个隐式行为**（2026-09-21 实测澄清）：本栈
  `podman run --rm --entrypoint ...` 之所以可用，是因为叠加镜像是 **OCI 格式**
  而 **OCI 忽略 `HEALTHCHECK` 指令**——基底 `Containerfile:859` 定义了
  HEALTHCHECK（`/usr/local/bin/healthcheck.sh`），但基底自身的 ManifestType 是
  `docker.v2`、叠加镜像全是 `oci.v1`，故 xmnn-dev/xmnn-runtime 实际都**不带**
  healthcheck（`podman image inspect` 顶层 Healthcheck = null）。
  **反面**：直接对**基底镜像**跑 `podman run --rm` 会失败
  （`Error: create healthcheck: unable to get systemd connection ...`，
  WSL 下 systemd 会话总线不可达），需 `--no-healthcheck` 绕开
  （构建端 `Containerfile.toolbx` 早已用 `HEALTHCHECK NONE` 处理同类问题）。
  故**禁止**把「podman build 默认输出 OCI」当作理所当然——若上游改为默认
  docker 格式，四栈 standalone 冒烟会集体失效，须同步补 `--no-healthcheck`
  或显式 `HEALTHCHECK NONE`。

## 7. compose / 端口 / 卷

- extends `../_shared/base-rootless.yaml` 继承三必需/凭证四变量/
  bridge/labels/restart；栈文件**无 environment 段**（凭证全继承，
  无栈专属变量），黄金测试 test_compose_merge.py GOLDEN["xmnnrt"]
  锁定 env 集 = 凭证四变量。
- volumes = workspace 一个长语法 bind（+create_host_path）+ 命名卷
  `xmnnrt-ssh-host-keys` 挂 `/var/lib/jpman/ssh-host-keys`（2026-09-20 起：
  host key 持久化，`down/up` 重建容器不轮换主机指纹；entrypoint 以
  `mountpoint -q` 分流持久/容器层两模式）。**卷名前缀 `xmnnrt-` 与客户交付栈
  `release/compose.yaml` 的 `xmnn-ssh-host-keys` 刻意不同**——内部栈与交付包
  属不同生命周期，避免同机共享卷导致一方 `down --volumes` 牵连另一方。
  无源码 bind；端口固定 2225/8893（与三栈错开）。

## 8. 可选能力：GPU 透传与 torch 形态（C26，2026-09-20）

两能力**默认全关 = 与改造前逐字等价**（不开时镜像层、设备面、compose 文件集
零变化），且互为正交：GPU 是**运行期**维度（只改 compose 文件集），torch 形态
是**构建期**维度（只改镜像内容）。二者组合才有意义——只透传设备而镜像内是
CPU 版 torch，容器里仍然用不上 GPU。

### 8.1 GPU：`up --gpu`

- 设备解析/预检/形态分派**完全复用内核**（C19/C23，与 quant/xmnn 同源）：
  `up --gpu` → `resolve_gpu_device` 三态探测（显式设备路径 → 显式 CDI 引用 →
  按 `GPU_DEVICE_FORMS` 自动探测 `/dev/dri` → `/dev/dxg`）→ 追加
  `compose.gpu.yaml` 或 `compose.gpu.wsl.yaml`（**互斥，只加载一个**）。
  `xmnnrt.py` 只负责把 `gpu` 形参透传给 `up_stack`，**禁止**在栈模块里
  重复实现形态分派。
- 两个覆盖文件都是**薄层**：`compose.gpu.yaml` 只写一条设备
  `${GPU_DEVICE:-/dev/dri}` 单 token 插值（`/` 开头=设备路径，否则=CDI 引用；
  podman-compose 1.6.0 把 devices 列表项**原样**下传为 `--device <item>`，
  写成 `a:b` 两条并列必有一条非法）；`compose.gpu.wsl.yaml` 写 `/dev/dxg` +
  三条只读 bind（libcuda.so.1 / libdxcore.so / `/usr/lib/wsl/drivers`，
  同为最小充分条件，2026-09-20 实测）。
- **本栈零 env 改动是硬约束**：compose.yaml **本就没有 `environment` 段**
  （凭证四变量由基段继承），故覆盖文件只允许加 `devices`（WSL 形态另加
  `volumes`）。任何 `LD_LIBRARY_PATH` 注入都会凭空新增栈专属 env——既污染
  「干净交付运行时」语义，又打挂 `test_compose_merge.py` 的 env 黄金集。
  WSL 库挂载靠**目标取 `/usr/lib`（基底 glibc 默认搜索目录）**实现，不需要
  也不允许环境变量配合。
- 覆盖文件**不进客户交付包**：`release/` 是独立谱系（自包含 compose +
  `xmnnctl`），本次改造不涉及；GPU 交付属后续独立提案。

### 8.2 torch 形态：`build --torch cpu|cu130`

- 缺省 **cpu**（`StackSpec.torch_default="cpu"`，保持 2026-09-16 起的「内置
  CPU 层」语义）；`cu130` 经 `download.pytorch.org/whl/cu130` 装 CUDA 版
  torch 2.14.0。取值是**白名单**（`resolve_build_args` 解析期拦截），索引由
  形态推导，杜绝用户输入拼接网络请求目标。
- **与 xmnn-dev 的语义差异必须显式理解**：同一个 `.env TORCH_FLAVOR` 键，
  在 xmnn-dev 是「空=不装 torch」，在 xmnnrt 是「空/未设=回落 **cpu**」。
  故缺省值**不可**硬编码在内核里（内核只认 `spec.torch_default`），
  compose 段也必须写 `${TORCH_FLAVOR:-cpu}` 与之同键同默认（C15）。
- **形态参与镜像 tag 命名**（C28，2026-09-21 起；取代 C26 原文「一 tag
  一形态」）：`localhost/xmnn-runtime:<形态>`（cpu / cu130）+ 保留 `:latest`
  通用别名。改造前 CPU 与 cu130 **标签相同而内容不同**，`up --skip-build`
  只查 tag 存在性，切形态全靠人记得重建——详见 §8.4。
- **不提供 nvcc**：本栈 P0 禁编译器工具链（§4），CUDA 版 torch 足以跑 GPU
  张量与 torch.jit 推理；需要编译 CUDA 内核 / TVM CUDA codegen 请回 xmnn-dev
  栈（其 cu130 经 C25 提供 nvcc 13.4.92）。这是**刻意保留的边界**，不是缺口。
- 客户交付包（`release/`）的 torch 版本标签读取口径随本次改造改为
  `org.specweave.torch-version`（旧 `torch-cpu` 键名在 cu130 下失真），
  `relpack.py` 保留旧键回退以兼容本地残留镜像；`release.json` 字段与
  schema **无变化**。

### 8.3 起容器前的形态一致性校验（C27，2026-09-21）

**缺口**（C15 × C16 的交叉盲区）：`--torch` 是**单次** CLI 覆盖，只作用于
`build`；而 `up` 的形参面没有 `--torch`（拿到也无效——它不做构建），只查镜像
**存在性**（`_require_local_image` 比的是 tag，不是内容）。于是：

```bash
# 形态感知 tag 生效时（C28）：build --torch cpu 产出 :cpu（并把 :latest 别名
# 一并指向它），up 仍按 .env 找 :cu130 —— 命中的是那份真 cu130 镜像，缺口已由
# **标签身份**堵住。残留场景是身份被接管的模式：
# .env TORCH_FLAVOR=cu130 且 XMNNRT_IMAGE_TAG=myrepo/xmnn:latest（显式覆盖）
invoke xmnnrt.build --torch cpu     # 镜像内容变 cpu，标签仍是那个显式名
invoke xmnnrt.up --skip-build       # 存在性通过 → 静默跑 cpu 镜像（本校验拦）
```

构建期守卫第 10 项**发现不了**：它比的是「镜像内 marker vs 镜像内实物」，
两者一致必然 PASS——偏差在**跨层**（`.env` 声明 vs 镜像内容），不在镜像内部。

**规则**：`up` 起容器前必须过 `overlay_core.warn_torch_flavor_mismatch()`，
把 `resolve_build_args` 解析出的**期望形态**与镜像 LABEL
（`client_core.TORCH_FLAVOR_LABEL`）比对，不符则打印中文指引（含修复命令）。

- **警告不阻断**（同 C21 超时不判失败、C24 回读失败不阻断）：镜像可用，形态
  不符只影响能力面（如无 CUDA）；用户也可能刻意临时用另一形态，fail-fast 会
  把「能用」的场景一并挡掉。
- **判据在 `up_stack` 内、仅 `torch_flavor` 栈生效**（quant/monetize 零探测
  零噪音）。非 `--skip-build` 路径刚由 `build_image` 按同一 `resolve_build_args`
  重建，形态必然一致（零噪音通过），该卡点真正拦的是 `--skip-build`/`--offline`。
- **「无 LABEL」与「LABEL 为空串」必须分流**：空串是**合法声明**
  （`TORCH_FLAVOR=""` = 不装 torch），无 LABEL 是**无法判定**（改造前旧镜像 /
  非 torch 栈镜像）。故本校验另立 `overlay_core.image_torch_flavor()` 返回
  `Optional[str]`（None=无标签），**不得**复用 `client_core._image_torch_flavor`
  （那个把两者都归空串，供 save 命名用——照搬会把旧镜像误报成「声明空、实物
  cpu」）。真机实测：`xmnn-runtime:latest`→`cu130`、`1.2.1.dev0`（旧 CPU）→
  `None`、基底镜像→`None`，零误报。
- **查询走 `client_core.image_inspect_info`**（原始 JSON，规避 Windows cmd 与
  Linux bash 双 shell 的 `--format` 模板引号差异），镜像不存在/解析失败降级为
  None，不抛异常阻断主流程。测试按既有约定在 **`oc` 命名空间**打桩该符号
  （同 `load_image`），**不**去 patch `client_core.run_cmd`——内核自己的 I/O 缝
  是 `oc.run_cmd`，跨模块旁路会同时破坏两条约定。
- **共享键语义（本次决策：保持 C15 不动）**：`TORCH_FLAVOR` 是两栈共用的无前缀
  键（C15），xmnn-dev 与 xmnnrt **无法各自独立取值**。当前两栈诉求恰好一致
  （dev 要 nvcc 编译、runtime 要 GPU 张量），故接受该耦合；若未来需要分叉，
  走「栈专属覆盖键优先、回落共享键」的受控扩展（已实测 podman-compose 支持
  嵌套插值 `${XMNNRT_TORCH_FLAVOR:-${TORCH_FLAVOR:-cpu}}`），届时需同步修订 C15。

### 8.4 形态感知镜像 tag（C28，2026-09-21）

**动机**：C26 原文「一 tag 一形态」的实伤——CPU 与 cu130 镜像**标签相同而内容
不同**，`up --skip-build` 只查 tag 存在性，切形态全靠人记得重建；C27 只是**事后
不阻断告警**，标签本身仍可能指向「上一次构建的形态」。

**规则**（`StackSpec.flavor_tag` 声明位，**仅 xmnnrt** 声明
`"localhost/xmnn-runtime"`；非声明栈零回归）：

1. **解析序**：显式 `{PREFIX}_IMAGE_TAG` > 形态感知 tag > `default_image_tag`。
   形态感知取 `<flavor_tag>:<形态>`，形态由 `overlay_core.image_flavor()` 复用
   `resolve_build_args` 的**同一解析序**（CLI `--torch` > shell export > `.env`
   > `spec.torch_default`）——**CLI 单次覆盖也改变标签**，杜绝「装的是 cu130、
   标签写 cpu」的骗人镜像。空串形态按「未设」处理（回落缺省），**不产生**
   `xmnn-runtime:` 这类空 tag。
2. **通用别名必须保留**：`build_image` 对同一镜像双 `-t`（形态 tag +
   `default_image_tag`）。`:latest` 是**被外部消费**的稳定入口——客户交付打包
   脚本 `relpack._PACK_SCRIPT` 硬编码 `SRC="localhost/xmnn-runtime:latest"`，
   README 的 `podman run ... latest` 示例同理；删之则引用集体悬空。显式
   `--tag` 视为用户自管命名，**不**追加别名。
3. **compose 侧同键同默认嵌套插值**：`image: ${XMNNRT_IMAGE_TAG:-localhost/
   xmnn-runtime:${TORCH_FLAVOR:-cpu}}`，与 `image_tag()` **逐字同串**（C16：
   存在性预检与起容器共用同一判据）。podman-compose 1.6.0 四态实测：无变量
   →`:cpu`；`TORCH_FLAVOR=cu130`→`:cu130`；显式 `XMNNRT_IMAGE_TAG=custom:v9`
   胜出；`TORCH_FLAVOR=` 空串→回落 `:cpu`（**不产生空 tag**）。
4. **迁移**：改造前镜像只挂 `:latest`，改后 `up` 找形态 tag → `up --skip-build`
   会 Exit(1)。`_require_local_image` 检出「形态 tag 缺失 + 通用 tag 在本地」时
   打印**零成本改挂**命令 `podman tag localhost/xmnn-runtime:latest
   localhost/xmnn-runtime:<形态>`（并打印通用标签的 LABEL 形态供判断）；
   **只提示不自动改挂**——通用标签可能指向另一形态，改挂与否由用户按形态判断。
5. **C27 校验保留为兜底**：形态 tag 让「声明 ≠ 实物」在**默认路径**上消失，
   `warn_torch_flavor_mismatch` 自此专管身份被接管的场景（显式
   `{PREFIX}_IMAGE_TAG` / 手工 `podman tag` / 改造前旧镜像被人工改挂）。
6. **零回归**：`flavor_tag=""` 的三栈恒 `default_image_tag`
   （`test_image_tag_unchanged_for_stacks_without_flavor_tag` 锁死）；xmnn-dev
   的形态区分仍由 `save` 归档名承担（C20），两者机制不混用。
