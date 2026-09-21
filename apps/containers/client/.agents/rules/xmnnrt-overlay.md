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
| 镜像 | `localhost/xmnn-dev:latest` | `localhost/xmnn-runtime:latest` |
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
- 形态不改镜像 tag（沿用 `XMNNRT_IMAGE_TAG`，一 tag 一形态）：CPU 与 cu130
  镜像 tag 相同但内容不同，切换形态必须重建镜像；**不做**形态感知的 tag 命名
  （与 xmnn-dev 一致——它的 arch/torch 区分经 `save` 归档名承担，本栈无
  `save`/`load`）。
- **不提供 nvcc**：本栈 P0 禁编译器工具链（§4），CUDA 版 torch 足以跑 GPU
  张量与 torch.jit 推理；需要编译 CUDA 内核 / TVM CUDA codegen 请回 xmnn-dev
  栈（其 cu130 经 C25 提供 nvcc 13.4.92）。这是**刻意保留的边界**，不是缺口。
- 客户交付包（`release/`）的 torch 版本标签读取口径随本次改造改为
  `org.specweave.torch-version`（旧 `torch-cpu` 键名在 cu130 下失真），
  `relpack.py` 保留旧键回退以兼容本地残留镜像；`release.json` 字段与
  schema **无变化**。
