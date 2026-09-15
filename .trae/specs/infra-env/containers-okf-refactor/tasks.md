# Tasks：基于 OKF 容器知识包优化 apps/containers

- **Spec**：[spec.md](spec.md)
- **切片原则**：垂直可验证切片（shared 基座 → 连接层 → 编排内核 → 逐栈迁移 → compose → 收尾），每个任务独立完成、独立留证；测试与实现同任务交付。
- **实施环境**：Windows + PowerShell 7.4+ / py314 conda 环境；代码改完需 `pip install -e apps/containers/shared`（组内安装顺序：先 shared 后两应用）。
- **禁止**：本阶段不执行 git commit（C 阶段且用户明确要求时再提交）；不得改 projects/vendor。

## 任务总览与依赖

```
T1 shared 基座包（平台/进程/容器工具）─┬─→ T3 overlay_core 内核 ─→ T4 三栈迁移 ─→ T5 compose extends
                                       │                                          │
                                       └─→ T2 连接层统一 ─────────────────────────┘
                                                                                   ↓
                                                          T6 文档/规则/技能同步 → T7 全量验证收尾
```

---

## T1：新建 jpman-common 共享包（平台/进程/容器只读层）

**描述**

新建 `apps/containers/shared/`：`pyproject.toml`（scikit-build-core 纯 Python 四要素：requires/build-backend/`tool.scikit-build.wheel.packages=["src/jpman_common"]`/`build-dir`/`minimum-version="0.9"`，**无 cmake 段**）、`src/jpman_common/__init__.py`、`tests/` 及包内 `[tool.pytest.ini_options] testpaths=["tests"]`。

迁移以下两端重复实现到 shared，以 client 版（含 Windows 修复）为超集蓝本：

- `platform_paths.py`：`to_posix_path`、`normalize_path_str`（来自两端 utils）。
- `proc.py`：`_ensure_win32_stdout_transcode` 等转码 + `run_cmd`（UTF-8 双端转码版）、`detect_runtime`、`check_runtime_ready`、`generate_random_string`。
- `containers.py`：`container_exists`、`container_running`（podman 为 optional import，保持延迟导入）。

接线：

- client `tasks/utils.py` 删除上述实现，改为从 jpman_common 再导出（保持 client 内部既有 import 路径不断）。
- builder `tasks/utils.py` 同样改为再导出；核对 builder 各调用点行为差异（裸 run_cmd → UTF-8 版须确认无调用依赖旧异常/编码行为，有差异点写入 Completion Evidence）。
- builder `pyproject.toml` 移除 `[tool.scikit-build.cmake]` 段（AC-6）；两端 pyproject `dependencies` 增加 `"jpman-common"`。
- client/builder 安装引导（README、docs/03 安装小节如涉及）补安装顺序：`pip install -e ../shared` 先于应用。

**测试**：`shared/tests/test_proc.py`（run_cmd 成功/非零退出/Unicode 输出，monkeypatch subprocess）、`test_platform_paths.py`（Windows 盘符/反斜杠/空值）、`test_containers.py`（podman 缺失时优雅降级）。覆盖率 ≥80%。

**验收映射**：FR-1（部分）、FR-7、FR-8（部分）；AC-1（部分：两端 `invoke --list` 不回归）、AC-4（部分）、AC-6（cmake 部分）。

**Completion Evidence**（2026-09 实施）：

- `apps/containers/shared/`（jpman-common 0.1.0）落地：platform_paths/proc/containers + tests；`pip install --no-build-isolation -e shared` 成功（build isolation 会在临时环境重装 scikit-build-core 卡死，必须 --no-build-isolation）。
- shared 全量：`pytest --cov=jpman_common` **92 passed，TOTAL 97%**（proc/containers/connection 100%，platform_paths 95%，_win32_transcode 87% 难打桩分支）。
- 两端 utils 改 jpman_common 再导出垫片；builder pyproject 去 cmake 段、两端加 jpman-common 依赖；全 11 个任务子模块 import OK。
- 调用点差异核对：builder 旧裸 run_cmd 全部走 UTF-8 双端转码版，调用点均不依赖旧编码异常行为，无行为回退；MIRROR_CHOICES 保留在 builder utils。

---

## T2：SDK 连接层统一入 jpman_common.connection

**描述**

在 shared 新建 `connection.py`，以 client 现有超集为蓝本统一：`sdk_available`、策略 env（auto/legacy/wsl/machine 四值白名单校验）、`host_runtime_uid`（多源推导 PODMAN_RUNTIME_UID→XDG_RUNTIME_DIR→os.getuid→Windows 默认 1000）、`podman_sock_path`、`host_runtime_dir`、WSL distro 探测（wsl.exe UTF-16 LE 解码）、base_url 四级候选、machine conn URI、`ensure_host_podman_socket`、bsock 指引、`get_client()`（@contextmanager，全候选失败才 yield None，scheme 仅限 C1 白名单 6 个、Windows 显式 base_url、A/B 维度分离）。

接线：

- client `tasks/utils.py`（连接相关段）与 `tasks/client_core.py` 的 get_client 改为消费 shared；client_core 仅保留 load/list/save/run/stop/status/clean 等业务编排。
- builder `tasks/client.py` 删除 `_podman_runtime_uid` 硬编码路径与简易 from_env 版，改为从 shared 再导出/薄封装；保持其全部调用点（build/manage/interact/model/registry）的 `with get_client() as client:` + None 降级语义不变。
- 确认三栈模块（quant/xmnn/monetize）与 xmnn.py 长任务不直接 import podman（C11/C13）。

**测试**：`shared/tests/test_connection.py`——UID 各来源优先级（monkeypatch env/getuid/XDG）、非法策略拒绝、候选 URL 生成、scheme 白名单（npipe 必须拒）、get_client 全失败 yield None；全程无 daemon、无真实 wsl 调用（wsl 探测打桩）。

**验收映射**：FR-6、FR-1（完成）；AC-4、AC-6（UID 部分）；C1/C2/C4/C5/C6/C7/C8 不回归。

**Completion Evidence**（2026-09 实施）：

- `shared/src/jpman_common/connection.py`（653 行）为连接层唯一实现：多源 UID（C-I5）、bsock 指引、四策略白名单、WSL UTF-16 探测、P0/P1/P2/legacy 候选、get_client 全失败 yield None；`shared/tests/test_connection.py` 全打桩约 90 用例，**connection.py 覆盖率 100%**。
- Grep 证据：apps/containers 下 `def get_client|def host_runtime_uid|def podman_sock_path|def sdk_base_url_candidates|def _podman_runtime_uid|import podman` 仅命中 shared/connection.py（另三处命中为三栈模块 docstring 中"禁止 import podman"的红线声明）；shared 包 `quant|xmnn|monetize` 仅命中 __init__ 零栈知识注释。
- 两端接线：client client_core.py 删本地 try-import/sdk_available/get_client（约 120 行）改从 jpman_common.connection 导入；client utils.py 删约 14.7k 字符连接段；builder client.py 删 _podman_runtime_uid 硬编码 1000（C-I5）、本地 podman_sock_path/sdk_available/简易 from_env get_client/contextmanager，改为再导出；builder build/container/interact/manage/model/registry 六处调用点经 `.client` 再导出消费，`with get_client()` + None 降级语义不变。
- 运行时验证：`cc.get_client is cn.get_client`、`bc.get_client is cn.get_client` 均 True；两端 podman_sock_path() 同为 /run/user/1000/podman/podman.sock；两端 `invoke --list` 快照任务名/命名空间零变化；11 个任务子模块全 import OK。
- builder tests/ 4 个文件为**容器内探测脚本**（模块级 `PodmanClient.from_env(timeout=30)` 真实连 daemon，非宿主单测），宿主 pytest 收集会阻塞于连接，已 Stop；py_compile 全通过，连接相关回归以 11 模块 import + invoke --list 为准（E2E 随定制 WSL 发行版恢复后置）。

---

## T3：client overlay_core 数据驱动编排内核

**描述**

新建 `client/src/jpman_client/tasks/overlay_core.py`，内容：

1. `@dataclass(frozen=True) SmokeSpec`：mode（multi-script guard+mounts / 显式脚本表）、interpreter、smoke_dir、scripts、mounts_script、exec_args 等字段，覆盖三栈现状差异（quant 的 01-04 脚本、xmnn/monetize 的 01-03 + jax 探测）。
2. `@dataclass(frozen=True) StackSpec`：project 名、namespace、service 名、overlay 子目录、Containerfile 名、默认 image tag/base、env 前缀、端口 env 与默认值（banner 用）、workspace env、`source_mounts`（env→默认锚点/标签/必须存在标志，锚点区分仓库根与 client 根）、build_args 名表（BASE/PIP_MIRROR/CONDA_MIRROR 等）、`bridge_env_keys` 元组、smoke: SmokeSpec、长任务钩子（可选，如 wheel 构建器引用）。
3. 内核操作（全部以 spec 为首参，纯函数/显式 c 参数）：`gate_platform/gate_compose_binary/gates/ensure_runtime_ready/overlay_dir/image_tag/compose_argv/run_compose/container_running/reconcile_stale_containers/prepare_env/build_image/up/down/ps/logs/smoke`。
4. `make_stack_tasks(spec) -> dict[str, invoke.Task]`：工厂内部 @task 装饰闭包生成六任务骨架，help/错误前缀/横幅全部由 spec 派生；xmnn/monetize 的 build-tvm/build-native/wheel 长任务通过 spec 钩子或在各自模块内用内核 helper 单独构造后并入命名空间。
5. **统一 `shlex.quote`**（AC-2 目标值）：argv 日志与拼接全部 quote（quant 漂移在本任务内核层自然修复）。

先不切换三栈；在 client 新建 `tests/test_overlay_core.py`：argv 黄金快照（三栈各自 spec 实例 × 代表性参数组合，含 --gpu/--mirror/--cleanup/tag/workspace）、门控失败消息含 project 名、prepare_env 的 workspace/checkpoint 解析与空占位不注入（C9）、reconcile 标签筛选（构造假 labels 字典，不触 daemon）、桥接键表由 spec 传入。

**测试**：见上；overlay_core 覆盖率 ≥80%。

**验收映射**：FR-2、FR-3、FR-8；AC-2、AC-4。

**Completion Evidence**（2026-09 实施）：

- `client/src/jpman_client/tasks/overlay_core.py`（约 710 行）：SourceMount/ SmokeSpec/TaskDocs/StackSpec（frozen dataclass，含衍生 env 键属性）+ gates/prepare_env/compose_argv/run_compose/container_running/reconcile/require_running/build_image/up_stack/down_stack/ps_stack/logs_stack/smoke_stack 内核 + make_stack_tasks 六任务工厂（conda_mirror/gpu_override/auto_shortflags 条件签名，docstring 经 Task 实例透传）。
- client pyproject 加 `[tool.pytest.ini_options] testpaths=["tests"]`；`client/tests/test_overlay_core.py` 三栈 spec 镜像夹具（T4 迁入模块）：**33 passed, 1 skipped（quant 无源码挂载分支）**；`--cov=jpman_client.tasks.overlay_core` **90%**（≥80% 达标）。
- 黄金快照：compose_argv 三栈 5 类 tail + quant GPU 双文件 + 非 GPU 栈 gpu=True RuntimeError；任务签名（build conda 变体/up/smoke gpu 参数）、auto_shortflags（quant True，其余 False）、docstring 逐字；prepare_env workspace/checkpoint/锚点/空占位（C9）；reconcile 标签筛选与 stale→down；门控三类文案含 namespace；build/up/down/smoke 端到端离线执行。
- 旧 quant 无 quote 反例断言：`test_run_compose_quotes_every_token`（含空格路径正则断言被单引号整体包裹）。
- 桥接键隔离断言：`test_bridge_keys_isolated_per_stack`（各栈 spec.bridge_env_keys 不含他栈前缀；F-10 于 T4 接线）。

---

## T4：quant/xmnn/monetize 三栈迁移为声明

**描述**

逐栈迁移（建议顺序 quant → monetize → xmnn，复杂度递增）：

- 每模块只保留：`<NAME>_SPEC = StackSpec(...)` 常量 + 调用 `make_stack_tasks`（+ xmnn/monetize 长任务函数与任务注册）。
- 删除各模块同构函数与六任务骨架（AC-5 Grep 证据）。
- `tasks/__init__.py` 三命名空间注册改为消费工厂产物；保持 `quant./xmnn./monetize.` 命名空间名、任务名、参数名、短选项不变。
- **F-10 修复**：`utils.py` 删除 `_BRIDGE_ENV_KEYS` 三栈枚举；WSL 桥接函数改为 `run_in_wsl_bridge(argv, extra_env_keys=...)`，由内核从 `spec.bridge_env_keys` 传入；通用键保留在桥接函数默认值。
- 各模块 docstring 中过期"改名顶替"发行版叙述更正（FR-10）。
- xmnn.py 保留 build-tvm/wheel 双 cp314 ABI 长任务（C13 不互换契约：base=/opt/conda cp314 GIL / main cp314t），monetize.py 保留 build-native/wheel（单 cp314，agent-monetize 源码 3 处适配不动），长任务内的 compose/argv/门禁调用全部改为内核 helper + 本栈 spec。
- 迁移每完成一栈即跑该栈测试与 --list 快照，不等三栈全改完。

**测试**：扩展 `tests/`：`test_tasks_surface.py`——三命名空间任务集合/参数签名与黄金清单一致；迁移前后 `invoke --list` 文本快照 diff 为空。

**验收映射**：FR-2/3/4 完成；AC-1、AC-2（三栈实例）、AC-5、AC-8。

**Completion Evidence**（2026-09 实施完成）：

- 三模块声明化（行数均 ≤160 目标）：[quant.py](apps/containers/client/src/jpman_client/tasks/quant.py) 88 行（QUANT_SPEC + TASKS + 6 别名）、[monetize.py](apps/containers/client/src/jpman_client/tasks/monetize.py) 121 行（MONETIZE_SPEC + 6 任务 + build_native/wheel 长任务）、[xmnn.py](apps/containers/client/src/jpman_client/tasks/xmnn.py) 158 行（XMNN_SPEC + 6 任务 + build_tvm/wheel 长任务，docstring 含双 cp314 ABI 契约 C13）。
- F-10 桥接键下沉：`utils.py` 的 `_BRIDGE_ENV_KEYS`（含三栈枚举）改名 `_BRIDGE_COMMON_ENV_KEYS`（仅 11 个通用键），`run_in_wsl_bridge(argv=None, extra_env_keys=())` 内 `keys = set(_BRIDGE_COMMON_ENV_KEYS) | set(extra_env_keys)`；overlay_core.gate_platform 传 `extra_env_keys=spec.bridge_env_keys`。Grep 证据：utils.py 中 QUANT/XMNN/MONETIZE/NPU_TVM 零命中。
- 注册：`tasks/__init__.py` 三命名空间改为 `for _name,_task in <mod>.TASKS.items()` 循环注册，xmnn/monetize 长任务单独 add_task；configure() 块未动。
- 等价性验证（py314）：三栈迁移后 `invoke --list` 与迁移前快照**逐行一致**——根 7 任务 + container.*/env.* 别名 + quant 6 + xmnn 8（含 build-tvm/wheel）+ monetize 8（含 build-native/wheel），描述文本、换行折叠、中文文案零变化；短选项差异（quant auto_shortflags=True，其余 False）保持。
- 测试：`tests/test_overlay_core.py` 三栈 SPEC 改为从 quant.QUANT_SPEC/xmnn.XMNN_SPEC/monetize.MONETIZE_SPEC 导入（模块成为唯一事实源）；新增 `tests/test_tasks_surface.py` 对生产 Collection `ns` 做黄金清单（任务集合/参数签名/auto_shortflags/docstring/根与别名命名空间/模块 ≤160 行且无内嵌同构函数 6 用例）。client `pytest tests -q`：**39 passed, 1 skipped**；overlay_core 覆盖率 **90%**。
- AC-5 Grep 证据：client/src 下 `def _gate_platform|def _compose_argv|def _run_compose|def _reconcile|def _prepare_env|def _overlay_dir|def _image_tag|def _gate_all|_BRIDGE_ENV_KEYS` **零命中**（唯一定义均在 overlay_core.py）。

---

## T5：compose 公共段 extends 抽取

**描述**

1. 新建 `client/overlays/_shared/base-rootless.yaml`：定义基服务（建议服务名 `rootless-base`），仅含无路径字段——rootless 三必需（`/dev/fuse` 设备、`security_opt: ["label=disable"]`、`cgroupns: host`）、`network_mode: bridge`、凭证四变量（USER_PASSWORD/JUPYTER_TOKEN/SSH_PUBLIC_KEY/GRANT_SUDO，保持现有 env 插值语法与空值语义）、公共 labels、restart 策略。**严禁** volumes/build/env_file/ports 外任何路径字段（ports 也留在栈文件以保直观）。
2. 三栈 `compose.yaml`：本服务改为
   ```yaml
   services:
     <service>:
       extends:
         file: ../_shared/base-rootless.yaml
         service: rootless-base
       # 以下保留各自：image/container_name/build/ports/volumes/栈专属 env
   ```
   删除已上移的重复字段；容器名/服务名/项目名不变。
3. `compose.gpu.yaml` 等 override 文件不动（其追加语义基于 F-3，已实证）。
4. 渲染等价验证：在 podman-machine-default（官方精简版）内 `python3 -m pip install --user podman-compose`（无 daemon 亦可跑 config），对三栈分别执行 `podman-compose -f compose.yaml config`（gpu 栈加 -f compose.gpu.yaml 再渲一次），与抽取前渲染结果逐项 diff（设备不重不漏、env 键并集一致、labels 一致）；若 WSL 内无网络无法 pip，则用按 F-3 语义（rec_merge dict 递归/list 追加/volumes 按 target 去重）实现的离线合并模拟单测兜底，并在 Evidence 注明。
5. 内核 `compose_argv` 不需要改（extends 对 argv 透明）；确认三栈 `_compose_argv` 调用路径与渲染验证一致。

**测试**：`client/tests/test_compose_merge.py`——离线合并模拟断言 AC-3 全部条款（privileged 缺失为正向断言）。

**验收映射**：FR-5；AC-3。

**Completion Evidence**（2026-09 实施完成）：

- 新建 [base-rootless.yaml](apps/containers/client/overlays/_shared/base-rootless.yaml)：服务名 `rootless-base`，仅含 network_mode bridge、rootless 三必需（devices /dev/fuse、security_opt label=disable、cgroupns host）、凭证四变量（保持 `${VAR:-}`/`${GRANT_SUDO:-yes}` 插值空值语义）、label org.specweave.managed-by、restart unless-stopped；**无** volumes/build/env_file/ports/image/container_name（test_base_file_contains_only_pathless_fields 正向锁定）。
- 三栈 compose.yaml 改 `extends: {file: ../_shared/base-rootless.yaml, service: rootless-base}`，删除已上移字段；image/container_name/build/ports/volumes/栈专属 env/组件 label 全保留；compose.gpu.yaml 未动。
- **真实 1.6.0 解析管线验证**（本机 py314 环境装有 podman-compose 1.6.0，无 daemon 亦可跑解析）：直接驱动 `PodmanCompose._parse_args + _parse_compose_file` 取 resolve_extends 后的 `self.containers`（注意 `config` 子命令打印的是 L2895 resolve 前的 merged_yaml 快照，不含 extends 合并，不能用作 diff 依据）。四组渲染全部符合黄金清单：quant devices=[/dev/fuse] 且 env 6 键；quant GPU devices=[/dev/fuse,/dev/dri]（list 追加、fuse 不重）；xmnn env 11 键/volumes 5 target；monetize env 6 键/volumes 2 target/ports 2224、8892；三栈 network_mode=bridge、cgroupns=host、security_opt=[label=disable]、labels 并集（managed-by+component）、restart=unless-stopped、privileged=None。
- **路径解析实证（修正规格假设）**：1.6.0 并非按裸 CWD 解析 extends.file——`_parse_compose_file` L2845-2847 先把 extends.file 按引用 compose 文件目录 join 重写，再由 resolve_extends（L2329）`rec_merge({}, base, current)` 合并；故内核 run_compose **无需 cd**（绝对 --file 任意 cwd 可跑，插桩 open() 实证打开的是 `overlays/onnx-quantized/../_shared/base-rootless.yaml`），已在 base 与三栈文件头、overlay_core.run_compose docstring 注明 L2845 行为。
- **行为变更（已知、经批准规格要求）**：quant 栈此前无 network_mode 声明，现随基文件统一获得 `bridge`。依据 xmnn-dev 旧 compose.yaml 文件头 2026-09-14 实证（machine 无 systemd user bus，默认项目网络 aardvark-dns 必现 Failed to connect to user scope bus，未改动 onnx 栈同机复现）；T6 CHANGELOG 须用户可见地记录此项。
- 兜底离线测试 [test_compose_merge.py](apps/containers/client/tests/test_compose_merge.py)（18 用例）：按 F-3 语义实现 rec_merge 模拟器（dict 递归/list 追加/command、entrypoint 替换/volumes 按 target 去重先到先得），对仓库真实 YAML 渲染并断言 AC-3 全部条款（privileged/cap_add 缺失为正向断言、env 键并集、插值覆盖、三必需不重不漏），另含 3 个模拟器自证用例防假阳性。
- client 全量：**57 passed, 1 skipped**；`invoke --list` 栈任务数 22（6+8+8）不回归。

---

## T6：文档、规则与脚手架技能同步

**描述**

1. `client/AGENTS.md`：更新文件地图（shared 包、overlay_core、瘦身模块）、新增第四栈指引改为"声明 StackSpec + 建 overlay 目录"；保留 C1-C13 全部 P0 约束原文并核对引用行号/文件名。
2. `client/.agents/rules/` 六规则中涉及文件结构/import 路径/env 键登记处同步（特别是 WSL 桥接、compose 规则中对三必需重复声明的描述改为"extends 基文件单一事实源"）；builder 侧规则/README 同步 shared 安装与连接层变化。
3. `apps/containers/client/CHANGELOG.md` 与 docs（`docs/` 下若有 containers 架构/生产部署/环境变量速查章节，先查 toctree 定位再改，路径用相对路径）记录重构、安装顺序、extends 基文件、E2E 后置清单。
4. 更新 `client-overlay-scaffold` 技能（`.agents/skills/` 或技能登记位置，先 Grep 定位）：栈骨架模板改为引用 overlay_core.StackSpec + extends base-rootless.yaml，12 件套清单与 7 个接线登记点相应修订；模板里的生命周期复制代码删除。
5 FR-10 发行版叙述：除 T4 三模块外，Grep "改名顶替/jupyter-podman-rootless 改名" 等表述逐处更正。
6. 产出 **E2E 后置清单**（写入 client CHANGELOG 或 docs 对应章节并在本 tasks 回链）：环境恢复前置 → `inv xmnn.build/up/smoke`、`inv quant.up/smoke`、`inv monetize.up/smoke`、builder 侧 `invoke build.info/mirror.list` 等命令、预期成功判据。
7. 变更目录跑 `python .agents/scripts/check-links.py --path <变更目录>`；Windows .ps1 合规脚本（如有新增 ps1）。

**验收映射**：FR-9、FR-10；AC-7、AC-10。

**Completion Evidence（2026-09-15 完成）**：

- **client/AGENTS.md**：L48-51 任务管理/编排内核/共享包/叠加层四段重写（9 模块、_shared 基文件、extends）；文件地图加 `../shared/`、`overlays/_shared/base-rootless.yaml`、overlay_core、3 个新测试文件、pyproject 依赖；路由表新增「容器配置真源改指 jpman_common.containers」「新增第四栈」两行；源代码真源行改指内核+声明栈+shared；快速开始改两步安装（`pip install -e shared -e client`）；**新增 P0 约束 C14**（声明式栈分层红线四款：内核零栈知识/栈模块只写声明 ≤160 行/base-rootless 唯一事实源/podman 只在 connection）；新增「新增第四栈唯一正确路径」小节（scaffold 技能→StackSpec→extends→黄金清单登记→静态验收）；变更日志加 2026-09-15 重构条目（含 quant bridge 行为变更指针）。
- **client/.agents/rules/**（子代理 A）：quant-overlay.md（§1 声明红线/§2 gate+bridge_env_keys/§3 extends 单一事实源/§4.1 rec_merge L2845/§8 smoke_stack）、xmnn-overlay.md、monetize-overlay.md、invoke-tasks.md（按磁盘实际写 9 模块 + §声明式栈）、sdk-connection.md（实现位置块指 jpman_common.connection）、windows-wsl.md（符号定位改 jpman_common）。
- **client docs**：10/11/12-quant/xmnn/monetize-overlay.md 加 extends 条目（10 含 quant bridge 行为变更）；01-getting-started.md 改先装 shared 再装 client；根 README.md L13-21 两步安装。
- **client/.agents/README.md**：加 jpman_common/overlay_core/_shared/pyproject 4 行资产。
- **FR-10**：utils.py 三处注释、.env.example L61-63、三 overlay README 桥接句全部中性化；Grep "改名顶替" client 全域 **0 命中**。
- **builder 侧**（子代理 B，已逐项核验落地）：AGENTS.md L36/L61-64 共享包条与文件地图；.agents/README.md L41-42；.agents/rules/invoke-tasks.md（垫片/连接层/依赖段 8 处）、entrypoint.md L50；docs/08-directory-structure.md L10-11/L24/L41-42/L117/L121-122 共享包章节；docs/09-three-tier-backend.md L80/L125 实现位置与伪代码说明（主线复核补改）；README 项目结构移除断引 CMakeLists.txt 行、加 ../shared/（主线复核补改）；docs/07 修复 1 处历史断链（vendor 相对层级少一级 → ../../../../vendor/toolbox/...）。
- **builder CHANGELOG**：`.agents/CHANGELOG.md` 加 2026-09-15 refactor 行（垫片/保留面/安装顺序/真机 E2E 回链 client 第 5 项）。
- **client CHANGELOG**：[.agents/CHANGELOG.md](apps/containers/client/.agents/CHANGELOG.md) Unreleased 顶部加重构完整条目（5 项原子交付/F 双证实证/quant bridge 行为变更/静态等价门/**真机 E2E 后置清单 6 项含勾选框与成功判据**）。
- **scaffold 技能**（子代理 B）：[client-overlay-scaffold](.agents/skills/client-overlay-scaffold/) 升 **v1.1.0**——SKILL.md §12 安全清单 + §13 Changelog；templates/namespace.py.skeleton 重写为 StackSpec+TASKS+六别名+形态B长任务；compose.yaml.skeleton 改 extends 形态；env.example.skeleton 改桥接/非桥接两区；references/delivery-checklist.md 三张黄金表门 + 7 接线点；技能 README L45、CHANGELOG L10（v1.20 技能包）、capability-registry/02-skills.md L17、SKILL.toml date/version 同步。
- **docs/ 根文档**：查 toctree 后无根级 containers 架构章节（apps 内文档自成体系），重构记录落在两端 CHANGELOG/AGENTS，无需根 docs 新增（符合任务书「先查 toctree 定位再改」）。
- **check-links**：`check-links.py --path apps/containers` → **校验通过（0 断链，12 个目录链接警告均为历史既有的指向目录模式）**；`--path .agents/skills/client-overlay-scaffold` → 6/6 通过。无新增 .ps1，跳过 pwsh7 合规。
- **E2E 后置清单回链**：[apps/containers/client/.agents/CHANGELOG.md](apps/containers/client/.agents/CHANGELOG.md) 2026-09-15 条目「V 真机 E2E 后置清单」（前置→xmnn/quant/quant-gpu/monetize/builder 五组六项 + 成功判据 + 失败闭环要求）。

---

## T7：全量验证收尾与证据归档

**描述**

1. shared/ 与 client/ 包目录分别 `pytest --cov`，覆盖率达标（AC-4）；builder 既有 3 测试不回归（在 builder 包目录跑 pytest，必要时补其包内 pytest 配置）。
2. 两端 `invoke --list` 快照最终对比（AC-1）；三栈 argv 黄金快照全量跑（AC-2）；compose 合并断言（AC-3）。
3. AC-5 Grep 证据集中采集（同构函数、桥接枚举、common 零栈知识三查）。
4. 全量 `py_compile`/import 冒烟两端；根 `pytest`（.agents/scripts 套件）确认无仓库级回归。
5. Completion Evidence 汇总回本文件各任务；不满足项登记为 pending issue（不得静默关闭）。
6. 不做 git commit；向用户报告并等待 C 阶段指令。

**验收映射**：AC-1 至 AC-9 全部复核；AC-10 清单已在 T6 登记。

**Completion Evidence（2026-09-15 完成）**：

| 验证项（AC） | 命令 | 结果 |
|---|---|---|
| AC-4 覆盖率 | shared：`pytest --cov=jpman_common` | **92 passed，TOTAL 97%**（connection.py 100% 255 stmts、proc 100%、containers 100%、platform_paths 95%、_win32_transcode 87%、__init__ 100%） |
| AC-4 覆盖率 | client：`pytest --cov=jpman_client` | **57 passed, 1 skipped**；重构目标 **overlay_core 90%**（322 stmts，门槛 ≥90%）、quant 声明模块 100%、tasks/__init__ 100%；client_core/env_in_container/manage/utils 为既有 daemon 连接代码（8%-21%，本次未触碰行为，不在 AC-4 新增覆盖范围） |
| AC-1 表面等价 | client `invoke --list` | 39 任务与迁移前逐行一致：根 7 + container 别名 7 + env 3 + quant 6 + xmnn 8（含 build-tvm/wheel）+ monetize 8（含 build-native/wheel）；docstring 完整透传 |
| AC-1 表面等价 | builder `invoke --list` | 22 任务（9 根+container 别名 9 + model 5 + registry 2 + build-toolbx/container.build-toolbx 计入）与重构前一致，默认任务 build |
| AC-2 argv 黄金快照 | client pytest 内 test_overlay_core.py | 全过（夹具从 QUANT_SPEC/XMNN_SPEC/MONETIZE_SPEC 唯一事实源导入） |
| AC-3 extends 合并 | client pytest 内 test_compose_merge.py | 18 用例全过（rec_merge 模拟器 + 真实 YAML 渲染 + 3 模拟器自证） |
| AC-5 红线 Grep | overlay_core import 清单 | 仅 stdlib（os/platform/shlex/shutil/dataclasses/pathlib/typing）+ invoke + `.manage` + `.utils`，**无 podman、无任一栈模块** |
| AC-5 红线 Grep | quant/xmnn/monetize 三模块 | `import podman` 仅出现在「禁止 import podman」docstring 负向声明；`_BRIDGE_ENV_KEYS` 旧名 0 命中；`def compose_/run_compose/prepare_env/reconcile` 同构函数 0 命中 |
| AC-5 模块体量 | 行数统计 | quant.py **88** / xmnn.py **158** / monetize.py **120**，均 ≤160 |
| 编译冒烟 | `compileall -q` 三端 src | **compileall OK**（shared/client/builder 全部 src） |
| builder 垫片 | `python -c "from jpman_builder.tasks import client as c, utils as u; print(c.get_client.__module__, u.run_cmd.__module__)"` | 输出 `jpman_common.connection jpman_common.proc True`（连接/工具符号确实来自共享包，MIRROR_CHOICES 保留） |
| 文档门禁 | check-links apps/containers + scaffold 技能 | **0 断链**（12 目录警告均为历史模式）；顺带修复 builder docs/07 一处历史 vendor 层级断链 |
| 仓库级回归 | 根 `pytest`（.agents/scripts 套件，py314） | 2696 passed / 16 skipped；22 failed + 28 errors + 1 收集错误**经逐条甄别全部为与本次改动无关的既存基线问题**（见下） |

**根套件失败甄别（全部 pre-existing，与 apps/containers 重构及 scaffold 编辑无因果）**：
- `test_analyze_xlsx_test_report.py` 收集错误：py314 环境缺 openpyxl（环境问题）。
- `test_mdi_validator` 105 错误 / `test_mdi_parser` 2 失败：失败主体为全部既存 vendor 镜像技能（E003 触发措辞）与 `algorithmic-art` 镜像技能空 title；输出中 **client-overlay-scaffold 零命中**（本次编辑未引入新违规）。
- `test_python314_new_apis` 8 失败：CPython 3.14.3 与测试预期的更新版本 API 差异（环境版本基线）。
- `test_check_sensitive_info` 4、`test_doc_navbar_options` 2、`test_docgen_strict_anomaly` 3、`test_quality_utils` 1、`test_check_academic_sources` 1（WinError 5 沙箱临时目录权限）、`test_benchmarks` 28 errors（沙箱文件限制）：均与本次变更路径无交集。

**pending issue 清单**：
1. **P1（环境恢复后）**：client CHANGELOG 2026-09-15 条目登记的真机 E2E 后置清单 6 项（定制 WSL 发行版灭失，daemon 不可用，无法在本环境关闭）。
2. **P2（非本次范围）**：根套件上述基线失败（openpyxl 缺失、vendor 技能 MDI 违规、py314 版本 API 差异等）建议另开规格处理，本次不修复、不静默关闭。

**Git**：未执行任何 commit（遵守用户约束）；等待 C 阶段指令。

---

## 后续（Review 阶段，不在实施任务内）

- R1：委托 fresh 独立只读子代理按 4 视角（魔鬼代言人/新人/老板/未来）对抗审查，重点攻击：任务工厂 invoke 行为、extends 合并边界、共享包打包依赖、双 ABI 契约、等价性测试充分性。
- R2：审查结果物化为 `review.md`；fail/pending 项必须可追踪；pass 后方可收尾。
