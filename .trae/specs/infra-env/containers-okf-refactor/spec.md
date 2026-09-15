# Spec：基于 OKF 容器知识包优化 apps/containers

- **Spec ID**：infra-env/containers-okf-refactor
- **创建日期**：2026-09-15
- **方法论**：七概念场景 3（重构优化），链路 I→F→A→V→C（V 强制）；TRAE-spec-mode 五阶段
- **内容敏感度**：公开（开源代码 + 公开 OKF 知识包）→ 标准工作流
- **知识源**：`projects/awesome-okf-xs/doc/bundles/jishu/containers/`（G1 最高可信源，只读引用，13 知识包）
- **改造对象**：`apps/containers/`（builder + client 两个独立可安装应用，主仓库主权区，可直接修改）

## 1. 背景与事实底座（R/I 阶段）

### 1.1 OKF 知识包给出的结构性原则

- **F-1 声明式生命周期 vs 编程式接缝分工**（`podman-compose/concepts/10-compose-vs-podman-py.md`）：podman-compose 负责声明式 YAML→CLI 子进程（标签即数据库：`io.podman.compose.project/service`、config-hash、依赖图）；podman-py 负责编程化读取/验证/运维。组合模式是"compose 写标签部署、SDK 读标签验证"。
- **F-2 argv 翻译层必须逐参数忠实**（`podman-compose/concepts/05-cli-translation-layer.md`）：所有路径/值经 shell argv 传递时必须 quote，等价于 shell 安全；`toolbox/concepts/04` 佐证"薄 argv 外层 + 透传优先"。
- **F-3 compose 深合并语义**（`podman-compose/concepts/06-config-pipeline.md` L83-103）：dict 按键递归合并；list 默认追加（`command/entrypoint` 例外为替换）；volumes 按 target 去重；`extends` 支持外部文件的服务级继承（`extends.file`，基服务先归一化后 `rec_merge`，当前服务覆盖）；`include` 为顶层组合且被引文件的 `volumes/env_file/build.context` 相对路径按**被引文件目录**重写。
- **F-4 rootless 三必需**（`podman/concepts/` 多篇 + client 实测沉淀）：`/dev/fuse` 设备、`security_opt label=disable`、`cgroupns=host`（podman-compose 1.6 下 cgroupns 为空操作但保留）；严禁 `--privileged`。
- **F-5 无 daemon 可测试性**（`podman-py/examples/03-testing-governance`）：连接策略、argv 构造、env 合并等纯逻辑应可离线单测。

### 1.2 代码现状（apps/containers，行数据为实测）

- **F-6 三栈 ~80% 同构复制**：client `tasks/quant.py`(335)、`xmnn.py`(393)、`monetize.py`(304) 各自重复实现 `_gate_platform`/`_gate_compose_binary`/`_gate_all`/`_ensure_runtime_ready`/`_overlay_dir`/`_compose_argv`/`_run_compose`/`_image_tag`/`_reconcile_stale_containers`/`_<stack>_container_running`/`_prepare_env` 及 build/up/down/ps/logs/smoke 六任务骨架。
- **F-7 复制已发生漂移**：`quant.py` 的 argv 日志拼接为 `" ".join(argv)` 无 quote（约 L181），xmnn/monetize 已修为 `shlex.quote`；错误前缀与文案靠拷贝后手工改。
- **F-8 跨应用 8 函数复制分叉**：builder `tasks/utils.py`(118) 与 client `tasks/utils.py`(1355) 重复 detect_runtime、to_posix_path、normalize_path_str、check_runtime_ready、run_cmd、generate_random_string、container_exists、container_running；client 版含 Windows UTF-8 双端转码，builder 版仍是裸 subprocess。
- **F-9 builder 侧陈旧 bug 类回归**：builder `client.py` 的 `_podman_runtime_uid()` 仍无条件默认 `"1000"`（约 L51-52），client 侧已演进为 `host_runtime_uid()` 多源推导（env→XDG→getuid→Windows 1000，C-I5 教训）；SDK 连接 client 侧已是四级候选，builder 侧仍为简单 from_env。
- **F-10 依赖方向倒挂**：client `utils.py` 的 `_BRIDGE_ENV_KEYS`（约 L1063-1076）在共享桥接层硬编码枚举了三个栈的全部 env 键——每新增一栈必须改核心 utils，违反开闭原则与"栈配置栈内自包含"。
- **F-11 utils.py 上帝文件**：1355 行/43 个 def，混合 Windows 转码、SDK 连接、透传 spec、WSL 桥接、镜像 tar 校验、host key、路径工具七类职责。
- **F-12 client 零单测**：仅有镜像内 smoke shell；builder 有 3 个测试。与 F-5 原则及全局规则（单测覆盖率 ≥80%）不符。
- **F-13 构建系统小违规**：builder `pyproject.toml` 为纯 Python 包却保留 `[tool.scikit-build.cmake]` 段（`wheel.cmake=false`），违反根 AGENTS.md "纯 Python 包不写 cmake 段"。
- **F-14 compose YAML 公共段三份重复**：三栈 compose.yaml 重复 rootless 三必需、`network_mode: bridge`、凭证四变量（USER_PASSWORD/JUPYTER_TOKEN/SSH_PUBLIC_KEY/GRANT_SUDO）、labels/restart。既有 `compose.gpu.yaml` 已实证 list 追加合并语义（按 F-3）。
- **F-15 文档腐烂**：三栈 `_gate_platform` docstring 仍叙述"定制发行版由 jupyter-podman-rootless 改名顶替"，而该 17.4GB 实体 2026-09-15 傍晚已灭失，当前同名 machine 为官方精简版。
- **F-16 预留位**：`apps/shared/` 仅有 .gitkeep（根级跨组共享预留）；本重构共享包服务于 containers 组内两应用，落在 `apps/containers/shared/`（组内聚更合适）。

### 1.3 G2 四元组洞察

1. **三栈三重拷贝是"脚手架生成后未回收"的结构性重复**。反常识：client-overlay-scaffold 把"复制 12 件套"当交付终态，但脚手架只解决 0→1；1→N 的边际成本与漂移（F-7）证明终态应是数据驱动栈注册表。行动：StackSpec + 任务工厂，三栈退化为声明。
2. **"刻意独立"已腐化为"复制+分叉"**。反常识：复制时"避免跨应用 import"的初衷合理，但无同步机制，独立退化为分叉，可移植性收益被 F-9 类已知回归抵消。行动：组内共享包（用户已裁决选最彻底方案）。
3. **横切关注点被栈私有常量反向侵入共享层**（F-10）。反常识：桥接修复图快把栈键表塞进共享 utils，依赖方向倒挂。行动：env 键表回归 StackSpec；compose 公共段按 F-3 用 extends 抽取。
4. **知识包被"裁决引用"但未转化为"结构约束"**（F-12/F-15/F-13）。反常识：文档引用知识包不等于代码遵循知识包——没有可执行测试把接缝契约（标签筛选、argv quote、scheme 白名单）固化，引用只是修辞。行动：daemon-free 单测 + 过期事实清理 + 构建合规修复。

## 2. 目标（F 阶段第一性原理推导）

- **公理 1**：栈的本质 = 一份声明数据（project/service/overlay 目录/镜像/端口/环境键表/源码挂载/smoke 规格/构建参数）+ 一组同构无状态生命周期操作。同构操作只应有一份实现（F-1）。
- **公理 2**：invoke 任务层是 podman-compose CLI 的薄翻译器（F-2），翻译器数据驱动，argv 构造必须 quote。
- **公理 3**：依赖方向只能 栈 → 编排内核 → 共享包；共享包零栈知识（修复 F-10）。
- **公理 4**：跨应用边界是打包边界而非复制借口；共享包以组内 editable 安装消费，两端仍各自产出独立 wheel（wheel 构建时声明共享包依赖）。
- **公理 5**：无 daemon 纯函数必须可离线测试（F-5）。

### 2.1 目标结构

```
apps/containers/
  shared/                          # 【新增】组内共享包 jpman-common
    pyproject.toml                 # scikit-build-core 纯 Python（无 cmake 段）
    src/jpman_common/
      __init__.py
      platform_paths.py            # host_runtime_uid/podman_sock_path/host_runtime_dir/to_posix_path/normalize_path_str
      proc.py                      # win32 UTF-8 转码 + run_cmd + detect_runtime/check_runtime_ready/generate_random_string
      containers.py                # container_exists/container_running（SDK 只读）
      connection.py                # sdk_available/策略/env/四级候选/get_client() 超集上下文管理器/diagnose
    tests/                         # pytest（无 daemon）
  client/src/jpman_client/tasks/
    overlay_core.py                # 【新增】StackSpec/SmokeSpec + 门控/prepare/argv/reconcile/build/up/down/ps/logs/smoke + 任务工厂
    quant.py / xmnn.py / monetize.py  # 瘦身为 SPEC 声明（+ xmnn/monetize 保留长任务）
    utils.py                       # 仅保留 client 专属：透传 spec/镜像 tar/WSL 桥接（键表来自 SPEC）/hostkey/checkpoint
    client_core.py                 # 消费 jpman_common.connection
  builder/src/jpman_builder/tasks/
    utils.py / client.py           # 瘦身为 jpman_common 再导出 + builder 专属
  client/overlays/
    _shared/base-rootless.yaml     # 【新增】extends 基服务（仅无路径字段，规避 F-3 路径重写）
    */compose.yaml                 # 改为 extends ../_shared/base-rootless.yaml
```

## 3. 需求（FR）

| 编号 | 需求 | 依据 |
|---|---|---|
| FR-1 | 新建组内共享包 `jpman-common`（scikit-build-core 纯 Python 包，零新增三方依赖，podman 保持 optional import）；两端 pyproject 声明 `jpman-common` 依赖并支持 editable 组内安装（先 shared 后应用） | 公理 4、F-8/F-9 |
| FR-2 | client 新建 `overlay_core.py`：`StackSpec`/`SmokeSpec` dataclass + 全部同构生命周期操作 + invoke 任务工厂；三栈模块瘦身为纯声明（xmnn/monetize 长任务保留并改用内核 helper） | 公理 1/2、F-6 |
| FR-3 | 修复复制漂移：quant 的 argv 日志/参数拼接统一 `shlex.quote`；消除手工错误前缀（由 SPEC 派生） | F-7、F-2 |
| FR-4 | 依赖方向归位：WSL 桥接 env 键表由 `StackSpec.bridge_env_keys` 自声明，共享桥接函数只接收键表参数；`utils.py` 中 `_BRIDGE_ENV_KEYS` 删除栈枚举 | F-10、公理 3 |
| FR-5 | compose 公共段以 **extends 服务级继承**抽到 `overlays/_shared/base-rootless.yaml`，仅放无路径字段（rootless 三必需/network_mode/凭证四变量/labels/restart）；三栈 yaml `extends.file` 引用并保留各自服务名与全部差异化字段 | F-3/F-4/F-14 |
| FR-6 | builder 经共享包自然获得：host_runtime_uid 多源推导（消除硬编码 1000）、UTF-8 run_cmd、统一 SDK 连接超集；其调用点签名与"全候选失败 yield None"语义保持兼容 | F-8/F-9 |
| FR-7 | builder `pyproject.toml` 移除违规 `[tool.scikit-build.cmake]` 段（纯 Python 包） | F-13 |
| FR-8 | shared 与 client 各建独立 pytest 配置（包目录内 `pyproject.toml [tool.pytest.ini_options] testpaths`，不污染根 pytest.ini 的 .agents/scripts 锁定）；新增 daemon-free 单测，shared 与 overlay_core 行覆盖率 ≥80% | F-5/F-12、全局规则 |
| FR-9 | 同步更新：client/builder AGENTS.md 与 `.agents/rules/`（containers 六规则）中的文件结构/import 路径描述、docs/03-架构/10-生产环境/12-环境变量速查等受影响文档、CHANGELOG；`client-overlay-scaffold` 技能骨架改为"新栈=SPEC+目录"的数据驱动形态 | F-15、公理 1 |
| FR-10 | 更正三栈 `_gate_platform` 等处过期发行版叙述为 2026-09-15 状态翻转后的事实（定制实体已灭失、同名为官方精简 machine、三栈 E2E 需重建环境） | F-15 |

## 4. 非目标（明确排除）

1. 不改镜像层：任何 Containerfile/entrypoint/supervisord/sshd_config/jupyter_server_config 内容。
2. 不改 overlay 业务脚本：三栈 smoke 内容、builder/scripts/、register-kernel.sh、jupyter kernel.json。
3. 不做功能增强：omlmd/olot Python API 升级、Quadlet、ai-lab-recipes、ModelCar、CDI 新接入等（另立 spec）。
4. 不重建定制 WSL 发行版、不跑真机 E2E（up/build/smoke 由用户环境恢复后按后置清单执行）。
5. 不发布 wheel 到 PyPI；共享包仅组内 editable/本地路径消费。
6. 不改 `projects/`、`vendor/` 任何文件（知识包只读引用）。
7. 不重命名既有 invoke 命名空间（quant./xmnn./monetize./build./kernel./mirror./model.）与任务名、不破坏 CLI 参数。
8. 不引入 entry_points 式插件机制（三个半实例下 YAGNI）；新增第四栈以"加一个 StackSpec 实例"为上限。

## 5. 约束（必须遵守的行为契约）

- client `AGENTS.md` C1-C13 全部继续生效：podman-py 仅 6 个合法 scheme（禁 npipe）、Windows 显式 base_url、rootless 三必需硬编码、get_client 为 @contextmanager 且全候选失败才 yield None、UID 运行时探测禁硬编码、wsl.exe 输出 UTF-16 LE、策略四值白名单 auto/legacy/wsl/machine、A/B 维度分离、`load_dotenv(override=False)` 空占位不注入、双 ABI 不互换（xmnn base=/opt/conda cp314 GIL / main cp314t；monetize 单 cp314）、三栈模块禁 import podman（podman 只允许存在于 jpman_common 连接/容器层）。
- 共享包不得反向 import client/builder；overlay_core 不得 import 具体栈模块。
- extends 基服务文件严禁出现 volumes/build/env_file 等路径字段（F-3 路径重写陷阱）。
- 根规范：Conventional Commits 中文主体；Python 3.14+；scikit-build-core（requires/build-backend/wheel.packages/build-dir/minimum-version 四要素）。

## 6. 验收标准（AC）

| 编号 | 类型 | 标准 |
|---|---|---|
| AC-1 | rule | 两端 py314 环境按"shared 先、应用后"editable 安装成功；`invoke --list`（builder 与 client）任务/命名空间集合与重构前快照完全一致。 |
| AC-2 | rule | argv 黄金快照测试：三栈 build/up/down/ps/logs/smoke 及 xmnn build-tvm/wheel、monetize build-native/wheel 在代表性参数组合（含 --gpu/--mirror/--cleanup/自定义 tag/workspace）下生成的 argv 与重构前目标值逐字节一致；quant 无 quote 旧值作为反例断言存在。 |
| AC-3 | rule | compose 合并结果验证（WSL 内 `pip install --user podman-compose` 后 `podman-compose -f <stack>/compose.yaml config`，离线时以按 F-3 语义实现的合并模拟为 fallback）：三栈均含 /dev/fuse、label=disable、cgroupns host、无 privileged、凭证四变量、network_mode bridge；各自 ports/volumes/build args/栈专属 env 无丢失无重复（devices 无 /dev/fuse 双份）。 |
| AC-4 | rule | `pytest`（shared/ 与 client/ 包目录内）全绿且无需 daemon/无网络；jpman_common 与 overlay_core 行覆盖率 ≥80%（pytest-cov 输出存档）。 |
| AC-5 | rule | Grep 证据：quant/xmnn/monetize 内不再定义 `_gate_platform`/`_compose_argv`/`_reconcile_stale_containers`/`_<stack>_container_running` 等同构函数（唯一定义在 overlay_core）；`_BRIDGE_ENV_KEYS` 栈枚举已删除；jpman_common 内无 quant/xmnn/monetize 字样。 |
| AC-6 | rule | builder 不再自有 `_podman_runtime_uid` 硬编码 1000 路径，UID 推导与 client 同源（PODMAN_RUNTIME_UID→XDG→getuid→Windows 默认）；builder pyproject 无 `[tool.scikit-build.cmake]`。 |
| AC-7 | rule | FR-9/FR-10 文档更新全部落地且 check-links 无断链（变更目录跑 `.agents/scripts/check-links.py`）；client-overlay-scaffold 技能产出的新栈骨架不再含生命周期复制代码。 |
| AC-8 | rubric | 去重与可维护性（1-5）：三栈模块各自 ≤160 行、第四栈新增成本=1 个 StackSpec + 1 个 overlay 目录 + compose；threshold ≥4。 |
| AC-9 | rubric | 架构方向合规（1-5）：依赖方向无倒挂、共享包零栈知识、extends 基文件零路径字段；threshold ≥4。 |
| AC-10 | rule | E2E 后置清单登记到 tasks.md（三栈 up/build/smoke 命令、预期、环境前置），用户已裁决不以 E2E 缺失阻塞本次合并。 |

## 7. 验证策略（用户已裁决：静态等价 + 单测，E2E 后补）

1. 行为等价：argv 黄金快照 + `invoke --list` 快照 + py_compile/import 冒烟。
2. 配置等价：podman-compose config 渲染（WSL 官方 machine 内 user 级 pip 安装，无需 daemon）；merge 模拟单测兜底。
3. 单元测试：monkeypatch subprocess/invoke.context/os.environ，零 daemon。
4. 真机 E2E：环境恢复后用户执行后置清单（`inv xmnn.up && inv xmnn.smoke` 等），结果回填本 spec。

## 8. 风险登记

| 风险 | 缓解 |
|---|---|
| invoke 任务工厂动态生成的 @task help/shortflags 行为漂移 | 工厂内统一 @task 装饰闭包；AC-1 快照对比 --list 与 --help |
| extends 外部文件在 podman-compose 1.6 的归一化边界（env_file/build 路径） | 基文件零路径字段（FR-5 硬约束）；AC-3 渲染验证 |
| 共享包 editable 安装改变开发引导顺序 | FR-1：pyproject 声明 + README/CHANGELOG 明示安装顺序；CI/脚本入口先校验 jpman_common 可 import |
| 大爆炸式迁移难回滚 | 任务按垂直切片（先 shared、再 core、再逐栈迁移），每切片独立可验证 |
| 定制 WSL 环境灭失导致无法运行态验证 | 用户已裁决静态验收；AC-10 后置清单 |
