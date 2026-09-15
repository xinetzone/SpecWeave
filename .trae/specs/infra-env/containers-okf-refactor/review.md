---
title: "独立对抗审查报告：基于 OKF 容器知识包优化 apps/containers（T1-T7）"
source: 本次重构独立审查
date: 2026-09-15
---

# 独立对抗审查报告（R1/R2）

- **审查对象**：`apps/containers/`（shared 0.1.0 / client / jupyter-podman-rootless）T1-T7 全部交付物
- **审查方法**：fresh 只读子代理，四视角对抗（魔鬼代言人 / 新人 / 老板 / 未来）；所有 extends/rec_merge 指控以仓库内 vendor 权威源码直接核对并运行实证，不接受二手转述
- **权威事实源**：[podman_compose.py](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py)（vendor 只读 submodule，[L54](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L54) `__version__ = "1.6.0"`，与 T5 实证版本一致；审查期间零改动，`git status` 干净）
- **审查日期**：2026-09-15；除本 review.md 外未修改任何文件

---

## 0. 结论

**评级：CONDITIONAL PASS（有条件通过）**

- **blocker 0 条 / major 2 条 / minor 2 条 / nit 5 条。**
- 三栈当前产物在真实 podman-compose 1.6.0 管线下行为正确：审查者独立驱动真实 1.6.0 解析管线渲染四组配置（quant、quant+GPU、xmnn、monetize），AC-3 断言字段（devices 含 GPU 顺序、environment 键并集、labels、ports、volumes targets、network_mode、cgroupns、security_opt、privileged 缺失）与模拟器渲染**逐字段一致**；T5 Evidence 的关键声称全部复现。
- 但 AC-3 的**兜底模拟器本身有两处与真实 `rec_merge` 语义相反的实现**（volumes 去重方向、长语法 volumes 去重），并用自证用例把错误语义锁成了"契约"；同一错误表述已扩散到 scaffold 技能、规则、基文件注释。当前三栈数据恰好不触发（基文件无 volumes、GPU 文件无 volumes），所以零运行时影响；但该测试的全部存在意义就是兜底等价性，且 scaffold 规定第四栈必须在此登记——它会在真正出事的场景给出假 PASS。**关闭 R2 前必须修复 M1/M2。**

### Pass 前必修项（CONDITIONAL PASS 的条件）

| # | 必修 | 位置 |
|---|---|---|
| M1 | 修正 `merge_one` volumes 语义并反转自证用例期望：真实 1.6.0 为「仅短语法字符串参与、覆盖方（source/current）按 target 获胜且条目移至列表尾部」，非「先到先得、基服务保留」；补一条长语法 dict volumes **不去重**的真实行为用例 | [test_compose_merge.py#L106-L131](file:///d:/spaces/SpecWeave/apps/containers/client/tests/test_compose_merge.py#L106-L131)、[#L273-L280](file:///d:/spaces/SpecWeave/apps/containers/client/tests/test_compose_merge.py#L273-L280) |
| M2 | 更正已扩散的「volumes 按 target 去重」表述为「短语法按 target 去重、覆盖方获胜；**长语法 bind（scaffold 强制形态）在 1.6.0 不去重**；基文件无 volumes 故三栈当前无碰撞」 | [base-rootless.yaml#L16-L26](file:///d:/spaces/SpecWeave/apps/containers/client/overlays/_shared/base-rootless.yaml#L16-L26)、[quant-overlay.md#L85-L97](file:///d:/spaces/SpecWeave/apps/containers/client/.agents/rules/quant-overlay.md#L85-L97)、[SKILL.md#L188-L191](file:///d:/spaces/SpecWeave/.agents/skills/client-overlay-scaffold/SKILL.md#L188-L191)、[SKILL.md#L317](file:///d:/spaces/SpecWeave/.agents/skills/client-overlay-scaffold/SKILL.md#L317)、[compose.yaml.skeleton#L18-L20](file:///d:/spaces/SpecWeave/.agents/skills/client-overlay-scaffold/templates/compose.yaml.skeleton#L18-L20) |

建议同 PR 处理：M3（模拟器边界声明/实现）、M4（删除死配置块）；nit 可登记后处理。

---

## 1. 五项权威事实核对（按补充事实源逐条裁定）

实证方式：`sys.path` 指向 vendor 后 `import podman_compose as pc`（打印 1.6.0），直接调用真实函数/真实类驱动管线；对照物为 client 仓库内模拟器与 YAML。

### 1.1 extends.file 按引用文件目录 join 重写 —— 属实，行号有漂移

- 真实代码在 [podman_compose.py#L2844-L2849](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2844-L2849)：判断在 L2844-2846（`'extends' in service and (service_file := ...)`），重写动作在 L2847-2849（`service['extends']['file'] = os.path.join(os.path.dirname(filename), service_file)`）。
- tasks.md/基文件/模拟器/内核 docstring 统一引用的「L2845-2847」**不精确**（真实区间 L2844-2849），但行为描述正确。
- 下游消费在 [resolve_extends L2342-L2345](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2342-L2345)：先剥 `./` 前缀再 `open(filename)`。绝对 `--file`（invoke 路径）与栈目录内裸跑（`-f compose.yaml` 时 dirname 为空，join 结果仍相对栈 cwd）均可解析；审查者从任意 cwd 以绝对路径驱动，四组渲染全部成功打开 `overlays/<stack>/../_shared/base-rootless.yaml`。**「内核无需 cd」的结论成立。**

### 1.2 resolve_extends 的 rec_merge({}, base, current) —— 属实，行号精确

- [podman_compose.py#L2364](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2364)：`new_service = rec_merge({}, from_service, service)`；基服务先经 L2349 `rec_subs`、L2351 `normalize_service(from_service, subdirectory)`。
- 注意 resolve_extends **不删除** `extends` 键（合并结果保留重写后的绝对路径），对后续 container args 无影响；模拟器同样保留（相对值），属无伤害差异。

### 1.3 rec_merge 真实语义 vs 模拟器逐条对照 —— 发现 2 处反向、4 处缺边

真实实现 [rec_merge_one L2225-L2308](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2225-L2308)，模拟器 [test_compose_merge.py#L106-L138](file:///d:/spaces/SpecWeave/apps/containers/client/tests/test_compose_merge.py#L106-L138)。运行真实函数探测结果：

| 语义点 | 真实 1.6.0（vendor 行号） | 模拟器 | 裁定 |
|---|---|---|---|
| dict 递归 | [L2300-L2301](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2300-L2301) | L111-115 深合并 | 一致 |
| 普通 list 追加 | [L2298-L2299](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2298-L2299) | L129 追加 | 一致 |
| devices 追加不去重（fuse 重复会双份） | 同上；实测 `[fuse,fuse,dri]` | L129 追加 | 一致；[compose.gpu.yaml#L17-L21](file:///d:/spaces/SpecWeave/apps/containers/client/overlays/onnx-quantized/compose.gpu.yaml#L17-L21) **确实只写 /dev/dri、未重复 /dev/fuse**，断言 [test_compose_merge.py#L237-L245](file:///d:/spaces/SpecWeave/apps/containers/client/tests/test_compose_merge.py#L237-L245) 与真实管线一致（实测渲染 `['/dev/fuse:/dev/fuse','/dev/dri:/dev/dri']`） |
| command/entrypoint 替换 | [L2263-L2265](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2263-L2265)（不看类型直接替换） | L117-118 仅 list 对 list 替换 | 当前数据无此字段，结果等价；边界不等价（见 M3） |
| **volumes 短语法去重方向** | [L2289-L2297](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2289-L2297)：pts 取 **source（覆盖方）** 的 target，从 **target（基方）** 删除碰撞项后 `extend(value2)` —— **覆盖方获胜并移到尾部**。实测 `['/h1:/w']+['/h2:/w','/h3:/d']` → `['/h2:/w','/h3:/d']` | L119-128 遍历 `[*a,*b]` **先到先得、基方获胜**；自证 L273-280 断言 `source=='s1'` | **反向（M1）** |
| **volumes 长语法（dict）** | `if ":" in v` 对 dict 是键成员判断 → dict 项**永不参与去重**，直接 extend；实测 1 基 + 2 覆盖（含 /workspace 碰撞）→ **3 条、/workspace 重复** | L97-103 `_volume_target` 识别 dict 并按 target 去重 | **反向（M1）**。scaffold 恰恰强制「bind 一律长语法」，见 M2 |
| None / 类型冲突 | [L2272-L2273](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2272-L2273) 仅 `None + dict` 特殊合并；[L2283-L2286](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2283-L2286) 其余一律 `ValueError`。实测 dict↔None、None↔list、str↔None、int↔str、dict env↔list env **全部抛 ValueError** | L130-131 静默保留/替换 | 不等价（M3）；当前 YAML 无 null 覆盖、无跨类型冲突，未触发 |
| `!reset` / `!override` | [L2253-L2261](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2253-L2261)，标签定义 [L1764-L1808](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L1764-L1808) | 不支持（普通 `yaml.safe_load` 遇到标签会直接构造失败） | 缺边（M3）；当前文件未使用 |
| depends_on list/dict 归一化 | [L2276-L2281](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2276-L2281) + [normalize_service L2129-L2145](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2129-L2145) | 无 | 缺边；当前文件未使用 |
| 归一化层（merge 之前） | [normalize_service L2107-L2123](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2107-L2123)：`build.args` dict→list、environment/labels list/dict 双方→`norm_as_dict`（[L517-L535](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L517-L535)）、security_opt str→list | 完全不模拟 | 实测差异仅体现在 `build.args`（dict vs list）与 `build.context`（绝对化，[normalize_final L2201-L2211](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2201-L2211)）；AC-3 不断言这两字段，无假断言 |
| env 两种形态 | 真实管线在 merge **前**把 list 形态（`["K=V"]`）转 dict，故官方文件里两种形态可合并；merge 函数本身遇 dict+list 会 ValueError（实测） | 仅支持 dict；三栈 + 基文件**全部为 dict 映射形态**（[base L47-L52](file:///d:/spaces/SpecWeave/apps/containers/client/overlays/_shared/base-rootless.yaml#L47-L52)、[quant L49-L54](file:///d:/spaces/SpecWeave/apps/containers/client/overlays/onnx-quantized/compose.yaml#L49-L54)、[xmnn L71-L84](file:///d:/spaces/SpecWeave/apps/containers/client/overlays/xmnn-dev/compose.yaml#L71-L84)、[monetize L50-L57](file:///d:/spaces/SpecWeave/apps/containers/client/overlays/agent-monetize-dev/compose.yaml#L50-L57)） | 当前一致；第四栈若写 list 形态，模拟器静默产出 list（靠 GOLDEN 断言可侥幸捕获），不会模拟真实的归一化路径 |
| 插值 | 真实为 tokenizer（`$VAR`/`$$`/`:-`/`:?` 等，[L388-L462](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L388-L462)），且 [rec_subs L477-L491](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L477-L491) 支持服务 env 互引 | 模拟器正则仅 `${NAME:-default}`（[L27](file:///d:/spaces/SpecWeave/apps/containers/client/tests/test_compose_merge.py#L27)、[L82-L94](file:///d:/spaces/SpecWeave/apps/containers/client/tests/test_compose_merge.py#L82-L94)） | 当前文件只用 `:-`，四组渲染 env 零差异 |

**结论**：AC-3 关心的所有字段，模拟器与真实 1.6.0 输出一致（审查者逐字段比对，仅 `build`/`extends`/`_config_hash` 三类非 AC-3 字段有差异）；模拟器的问题集中在 volumes 两条反向语义与未声明的边界缺口。

### 1.4 `config` 打印 resolve 前 merged_yaml —— 属实

- [L2895](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2895) `self.merged_yaml = yaml.safe_dump(compose)` 在文件循环结束后、resolve_extends（[L2919](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2919)）**之前**；[compose_config L4795-L4803](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L4795-L4803) 直接 print 它。
- 实测 quant：merged_yaml 中 `network_mode`、`/dev/fuse` 均**不存在**，`extends:` 存在；resolve 后 service 才有 bridge/fuse。tasks.md「config 不能用作 diff 依据」的警示正确且重要——这是实施方高质量发现，避免了一次必然错误的等价验证。

### 1.5 多文件 -f 与 extends 的叠加顺序 —— 裁定 GPU 断言与真实管线一致

真实顺序（代码 + 实测双重确认）：

1. 文件循环内逐文件 `rec_merge(compose, content)`（[L2851](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2851)）：compose.yaml 先入、compose.gpu.yaml 后入（gpu 的 devices `['/dev/dri:/dev/dri']` 在此追加到尚未 resolve 的 service）；
2. 循环后 [L2919](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2919) 统一 resolve_extends：`rec_merge({}, base, merged)`，优先级 **base-rootless < compose.yaml < compose.gpu.yaml**。
3. devices 是普通 list 追加（不去重），实测结果 `['/dev/fuse:/dev/fuse', '/dev/dri:/dev/dri']`，顺序与 [test_compose_merge.py#L242](file:///d:/spaces/SpecWeave/apps/containers/client/tests/test_compose_merge.py#L242) 黄金断言一致。
4. **若 GPU 文件也写 /dev/fuse**：真实结果为 `['/dev/fuse','/dev/fuse','/dev/dri']`（同一设备映射两次下发 podman）；[compose.gpu.yaml#L6](file:///d:/spaces/SpecWeave/apps/containers/client/overlays/onnx-quantized/compose.gpu.yaml#L6) 注释明确知道这一点且实际文件**没有**重复写，行为与文档自洽。
5. 模拟器的合并括号顺序相反（[L159-L162](file:///d:/spaces/SpecWeave/apps/containers/client/tests/test_compose_merge.py#L159-L162)：先 extends 后叠 gpu），优先级序在当前数据下等价（实测四组无差异），但遇到 volumes 碰撞等非结合场景可能分叉——随 M1 一并修正括号顺序更稳妥（nit）。

---

## 2. 四视角发现

### 2.1 魔鬼代言人（专挑致命反例）

- **【M1，major，confidence 高】兜底测试在唯一危险点上撒谎**：volumes 是 F-3 全部合并语义里唯一做去重的字段，模拟器恰好在这个字段上两处反向（短语法胜负方向反、长语法根本不去重却被模拟成去重），且 `test_simulator_volumes_dedup_by_target` 把错误语义命名为「先到先得（基服务值保留）」固化。真实行为经 vendor 源码 [L2289-L2297](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2289-L2297) 与运行探测双重证实是**覆盖方获胜**。当前三栈：基文件被正向锁定无 volumes（[test_compose_merge.py#L169-L183](file:///d:/spaces/SpecWeave/apps/containers/client/tests/test_compose_merge.py#L169-L183)）、GPU 无 volumes，故无现实碰撞；但「测试通过」不能为 volumes 去重场景背书。
- **【M2，major，confidence 高】错误保证已扩散到第四栈生产线**：scaffold 一边强制「bind 一律长语法 + create_host_path」（[monetize compose.yaml#L9-L10](file:///d:/spaces/SpecWeave/apps/containers/client/overlays/agent-monetize-dev/compose.yaml#L9-L10) 同款纪律），一边在 [SKILL.md#L188-L191](file:///d:/spaces/SpecWeave/.agents/skills/client-overlay-scaffold/SKILL.md#L188-L191) 承诺「volumes 按 target 去重」——而长语法正是 1.6.0 **唯一不去重**的形态。第四栈若在 override 文件重声明同一 target（典型如换 workspace 源路径做调试），真实管线会下发重复挂载点给 podman，模拟器却渲染出干净列表，GOLDEN 测试照过。
- **【M3，minor，confidence 高】静默宽容 vs 真实抛错**：真实 rec_merge 对类型/null 冲突是硬 `ValueError`（podman-compose 直接失败），模拟器 [L130-131](file:///d:/spaces/SpecWeave/apps/containers/client/tests/test_compose_merge.py#L130-L131) 静默取值。第四栈 YAML 写出 `environment:` 两形态混用、或某处 `key:` 空值覆盖时，真机报错、测试全绿。模拟器 docstring [L8-L10](file:///d:/spaces/SpecWeave/apps/containers/client/tests/test_compose_merge.py#L8-L10) 自称语义对齐但未列排除项。
- 反方试图攻击「extends 相对路径在任意 cwd 不可解析」——**被实证驳倒**：真实重写逻辑 L2844-2849 + 实测绝对 `--file` 任意 cwd 四组渲染成功；内核 [overlay_core.py#L326-L334](file:///d:/spaces/SpecWeave/apps/containers/client/src/jpman_client/tasks/overlay_core.py#L326-L334) 无需 cd 的设计成立。
- 反方试图攻击「GPU fuse 双份」——**被真实文件驳倒**：GPU 文件只声明 /dev/dri（[L19-L20](file:///d:/spaces/SpecWeave/apps/containers/client/overlays/onnx-quantized/compose.gpu.yaml#L19-L20)），实测顺序正确。
- 反方试图攻击「config 渲染验证无效」——实施方没有踩坑，改走 `_parse_compose_file` 后 `self.services`，路径正确（[tasks.md T5 Evidence](tasks.md)）；审查者复现其方法可行。
- 反方试图攻击「quant 新增 network_mode=bridge 是未授权行为变更」——spec FR-5 明确把 network_mode 列入基文件字段（[spec.md#L82](spec.md#L82)），基文件头 [L32-L35](file:///d:/spaces/SpecWeave/apps/containers/client/overlays/_shared/base-rootless.yaml#L32-L35) 与 CHANGELOG 均用户可见记录，合规；其依据的 2026-09-14 aardvark-dns 实证无法在本环境复验（machine 已灭失），属 AC-10 已接受的 E2E 后置项，非本次审查缺陷。

### 2.2 新人（今天入职，只能照文档/测试建立心智模型）

- 测试组织优秀：真实 SPEC 即夹具（[test_overlay_core.py#L17-L25](file:///d:/spaces/SpecWeave/apps/containers/client/tests/test_overlay_core.py#L17-L25)）、黄金表面清单逐参数锁定（[test_tasks_surface.py#L55-L88](file:///d:/spaces/SpecWeave/apps/containers/client/tests/test_tasks_surface.py#L55-L88)）、基文件字段正向锁定，新人很难误删三必需。
- 但新人读 [test_compose_merge.py#L273-L280](file:///d:/spaces/SpecWeave/apps/containers/client/tests/test_compose_merge.py#L273-L280) 会学到**错误的** podman-compose volumes 胜负规则，并把它当成上游行为（M1）；这是错误心智模型的注入点。
- 行号引用「L2845-2847」在 tasks.md、基文件头、内核 docstring、规则中四处一致但均有 1-2 行漂移（真实 L2844-2849）。新人对照源码会短暂困惑（nit）。
- [__init__.py#L99-L119](file:///d:/spaces/SpecWeave/apps/containers/client/src/jpman_client/tasks/__init__.py#L99-L119) 仍保留 quant/xmnn/monetize 三段 `ns.configure`，全仓 grep 零消费方——新人会误以为改端口镜像要改这里（实际唯一事实源已是各 SPEC）。**【M4，minor，confidence 高】**

### 2.3 老板（投入产出、交付风险、承诺兑现）

- 结构性目标全部兑现：三模块 88/158/120 行（≤160，[quant.py](file:///d:/spaces/SpecWeave/apps/containers/client/src/jpman_client/tasks/quant.py)、[xmnn.py](file:///d:/spaces/SpecWeave/apps/containers/client/src/jpman_client/tasks/xmnn.py)、[monetize.py](file:///d:/spaces/SpecWeave/apps/containers/client/src/jpman_client/tasks/monetize.py)）、同构函数唯一定义在内核、builder UID 硬编码消除（实测 `hasattr(client,'_podman_runtime_uid')=False`、`get_client.__module__=jpman_common.connection`）、client 57 passed/1 skipped、shared 92 passed（审查者 py314 复跑全绿）、栈任务 22 个、vendor 零改动。
- AC-1/AC-2/AC-3/AC-4/AC-5/AC-6/AC-8/AC-9 静态证据成立；AC-7 文档量大，本次抽查的 rec_merge 表述恰是其中唯一失实簇（M2），check-links 结论未复验但与本次评级无关。
- 剩余风险敞口诚实登记：真机 E2E 六项后置（用户已裁决不阻塞），quant bridge 行为变更已用户可见记录。**本次没有发现任何夸大或静默关闭的痕迹。**
- 修复成本评估：M1 是 1 个测试文件内 ~20 行改动，M2 是 5 处注释/文档措辞；均无产品代码风险，应在收尾前完成，不值得带着已知错误测试进入维护期。

### 2.4 未来（三个月后加第四栈、升 podman-compose、换维护者）

- 第四栈路径设计成立：声明 SPEC + extends + 两处黄金登记（[AGENTS.md C14](file:///d:/spaces/SpecWeave/apps/containers/client/AGENTS.md)），内核零栈知识经 import grep 实证（仅 stdlib/invoke/`.manage`/`.utils`，三栈模块与内核均无真实 `import podman`，仅 docstring 负向声明）。
- **未来最大的坑就是 M1+M2**：长语法 bind 不去重 + 假去重测试 + scaffold 强制长语法，三者叠加是定时炸弹；未来 override 卷碰撞时症状是 podman 侧重复挂载点报错，而仓库测试全绿，排查会绕远路。
- 版本耦合：规则/注释把 1.6.0 行号写死（L2329/L2845/L2895）。升级 podman-compose 时这些注释会腐烂；vendor submodule 已固定 1.6.0，且模拟器与真实渲染的端到端比对方法（本次审查脚本同款）值得固化成一条测试或 scaffold 检查清单项——建议 M1 修复时直接在测试里 `pytest.importorskip` 条件允许时用 vendor/已安装包做一次真实 rec_merge 对照（如环境无 podman-compose 则 skip），让模拟器永远不能悄悄偏离上游。
- [overlay_core.py#L541-L555](file:///d:/spaces/SpecWeave/apps/containers/client/src/jpman_client/tasks/overlay_core.py#L541-L555) standalone 冒烟的裸 `podman run --rm` 不带 rootless 三必需——这是迁移前既有行为（AC-2 要求逐字节等价，未被允许改），当前仅用于纯 CPU ONNX/守卫脚本，无风险；未来若给 standalone 路径加设备依赖需重新评估（nit，登记即可）。
- spec T1「无 cmake 段」措辞与交付物中 `wheel.cmake = false` 标量键（[shared pyproject#L21](file:///d:/spaces/SpecWeave/apps/containers/shared/pyproject.toml#L21)、[client#L26](file:///d:/spaces/SpecWeave/apps/containers/client/pyproject.toml#L26)、[builder#L26](file:///d:/spaces/SpecWeave/apps/containers/jupyter-podman-rootless/pyproject.toml#L26)）表面冲突，实质被 builder AGENTS 的表述消歧（禁的是 `[tool.scikit-build.cmake]` 表，标量键是 scikit-build-core 纯 Python 的正确开关），AC-6 满足（nit）。

---

## 3. 发现清单（按严重度）

| ID | 级别/置信度 | 发现 | 证据 | 建议 |
|---|---|---|---|---|
| M1 | **major / 高** | 模拟器 volumes 语义两处反向（短语法覆盖方应获胜却模拟成基方先到先得；长语法 dict 真实不去重却被去重），自证用例锁定错误语义 | 真实 [L2289-L2297](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2289-L2297)；探测：短语法→`['/h2:/w','/h3:/d']`，长语法→3 条含重复 /workspace；模拟器 [L97-L131](file:///d:/spaces/SpecWeave/apps/containers/client/tests/test_compose_merge.py#L97-L131)、自证 [L273-L280](file:///d:/spaces/SpecWeave/apps/containers/client/tests/test_compose_merge.py#L273-L280) | pass 前修：按真实实现重写 volumes 分支（仅字符串、source target 删 target 碰撞后尾部 extend），反转自证期望并新增长语法不去重用例；最好加一条「安装了 podman-compose 则与真实 rec_merge 对照」的条件测试 |
| M2 | **major / 高** | 「volumes 按 target 去重」失实表述扩散 5 处，且与 scaffold 强制长语法 bind 矛盾（长语法恰恰不去重） | [base-rootless.yaml#L16-L21](file:///d:/spaces/SpecWeave/apps/containers/client/overlays/_shared/base-rootless.yaml#L16-L21)、[quant-overlay.md#L85-L95](file:///d:/spaces/SpecWeave/apps/containers/client/.agents/rules/quant-overlay.md#L85-L95)、[SKILL.md#L188-L191](file:///d:/spaces/SpecWeave/.agents/skills/client-overlay-scaffold/SKILL.md#L188-L191)、[#L317](file:///d:/spaces/SpecWeave/.agents/skills/client-overlay-scaffold/SKILL.md#L317)、[skeleton#L18-L20](file:///d:/spaces/SpecWeave/.agents/skills/client-overlay-scaffold/templates/compose.yaml.skeleton#L18-L20) | pass 前修：统一改为「短语法按 target 去重且覆盖方获胜；长语法不去重；override 卷场景需人工避免 target 碰撞」 |
| M3 | minor / 高 | 模拟器对类型/null 冲突静默宽容（真实 ValueError）、不支持 `!reset/!override`、depends_on、build.args/env 归一化；docstring 未声明排除范围 | 真实 [L2253-L2286](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2253-L2286)、[L2107-L2145](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2107-L2145)；模拟器 [L8-L10](file:///d:/spaces/SpecWeave/apps/containers/client/tests/test_compose_merge.py#L8-L10)、[L130-L131](file:///d:/spaces/SpecWeave/apps/containers/client/tests/test_compose_merge.py#L130-L131) | 在测试 docstring 明确「仅模拟三栈所用 YAML 子集，类型冲突/标签/归一化不在模拟器保真范围」，或补 ValueError 行为 |
| M4 | minor / 高 | 三栈 ns.configure 死配置块（零消费），误导新人 | [__init__.py#L99-L119](file:///d:/spaces/SpecWeave/apps/containers/client/src/jpman_client/tasks/__init__.py#L99-L119)；全 src grep 无消费 | 删除或加注释标明仅历史兼容 |
| N1 | nit / 高 | 「L2845-2847」行号漂移（真实 L2844-2849）四处 | tasks.md、[base-rootless.yaml#L24](file:///d:/spaces/SpecWeave/apps/containers/client/overlays/_shared/base-rootless.yaml#L24)、[test L152](file:///d:/spaces/SpecWeave/apps/containers/client/tests/test_compose_merge.py#L152)、[overlay_core.py#L329-L331](file:///d:/spaces/SpecWeave/apps/containers/client/src/jpman_client/tasks/overlay_core.py#L329-L331)、quant-overlay.md | 改为 L2844-2849 或去掉行号只留函数名 |
| N2 | nit / 中 | 模拟器合并括号与真实管线相反（extends 先 vs 真实 -f 先、extends 最后） | 模拟器 [L159-L162](file:///d:/spaces/SpecWeave/apps/containers/client/tests/test_compose_merge.py#L159-L162)；真实 [L2851](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2851)+[L2919](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L2919) | 随 M1 调整为「先 -f 合并、后 extends」 |
| N3 | nit / 高 | 插值模拟器为简化正则，不支持 `$VAR`/`$$`/`:?`/服务 env 互引 | [test L27](file:///d:/spaces/SpecWeave/apps/containers/client/tests/test_compose_merge.py#L27)；真实 [L388-L497](file:///d:/spaces/SpecWeave/vendor/podman-compose/podman_compose.py#L388-L497) | docstring 注明即可（当前文件只用 `:-`） |
| N4 | nit / 中 | standalone 冒烟裸 `podman run` 不带 rootless 三必需（既有等价行为，非回归） | [overlay_core.py#L541-L555](file:///d:/spaces/SpecWeave/apps/containers/client/src/jpman_client/tasks/overlay_core.py#L541-L555) | 登记；未来加设备依赖前先改这里 |
| N5 | nit / 中 | spec「无 cmake 段」措辞与 `wheel.cmake=false` 标量键字面冲突（实质合规） | [spec.md T1](spec.md)；三端 pyproject | 下次修订 spec 时措辞改为「无 `[tool.scikit-build.cmake]` 表」 |

无 blocker。未发现：特权路径回潮（三栈+基文件 privileged/cap_add 缺失为正向断言且实测 `privileged=None`）、依赖倒挂（内核/共享零栈知识实证）、双 ABI 漂移（quant 冒烟解释器 main env `/opt/conda/envs/main/bin/python`、xmnn/monetize base `/opt/conda/bin/python`，与 C12/C13 及 compose/镜像契约一致）、隐藏 commit 或 vendor 改动。

---

## 4. 审查复现记录（可审计）

| 验证 | 命令/方法 | 结果 |
|---|---|---|
| vendor 版本 | 导入 vendor `podman_compose.__version__` | `1.6.0` |
| 真实 rec_merge 边界 | 直接调用 vendor `rec_merge` 6 组探针 | volumes 短语法覆盖方胜、长语法不去重、4 类类型冲突 ValueError、devices 重复追加、env dict/list 冲突 ValueError |
| 端到端等价 | vendor 单例 `_parse_args` + 新实例 `_parse_compose_file()`，取 `self.services`，与 `render_stack()` 逐字段 diff，4 组（quant/quant-gpu/xmnn/monetize） | AC-3 字段零差异；仅 build.context 绝对化、build.args dict→list、extends 保留、`_config_hash` 内部键差异 |
| config 快照陷阱 | 检查 quant `merged_yaml` | 无 network_mode/无 fuse/有 extends；resolve 后才有 bridge/fuse |
| client 测试 | py314 `pytest tests -q`（client 目录） | **57 passed, 1 skipped**（复现 T7 数据） |
| shared 测试 | py314 `pytest tests -q`（shared 目录） | **92 passed**（复现 T7 数据） |
| 表面等价 | `invoke --list` 三栈任务计数 | 22（6+8+8） |
| builder 垫片 | 导入 builder client/utils 查符号来源 | `get_client`→`jpman_common.connection`、`run_cmd`→`jpman_common.proc`、`_podman_runtime_uid` 已不存在 |
| vendor 只读 | 根仓与 submodule `git status --porcelain` | 均 0 改动 |
| cgroupns 声明 | vendor 全文 grep `cgroupns` | 仅 device_cgroup_rules 两处，无 cgroupns 翻译器——基文件「空操作」注释属实 |

## 5. AC 收口意见

- **AC-1/2/4/5/6/8/9**：审查者独立复验通过（测试绿、表面清单、grep 红线、模块体量、builder 同源）。
- **AC-3**：**当前三栈渲染等价成立（含真实 1.6.0 端到端证据）**，但兜底设施存在 M1/M2 两处失实，修复前 AC-3 的「模拟兜底」条款只能算有条件满足。
- **AC-7**：主体落地；M2 所列 rec_merge 表述簇为本审查发现的唯一文档失实，修完即闭环。
- **AC-10**：E2E 后置清单已登记且用户预裁决不阻塞；quant bridge 变更记录合规。
- 完成 M1-M4（M3/M4 强烈建议同 PR）后可将本结论升级为 **PASS**；nit 登记跟踪不阻塞。
