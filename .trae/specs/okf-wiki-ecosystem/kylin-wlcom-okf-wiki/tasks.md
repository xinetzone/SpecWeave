# kylin-wayland-compositor 源码 → OKF Wiki - 实施计划（R→I→E→V→C）

> **执行结果（2026-10-14）**：16 个任务全部 completed；独立审查三轮 R1 fail → R2 fail(N1) → **R3 pass**（终裁 CP-1~CP-8 全 pass，AC-7/8 均 4/5）。交付 33 个束内文件（16 concepts + 3 examples + 9 references + 根 index + 3 子 index + log），851 条编号事实。门禁：bundles rc0（地面真值 634 束，systems=3）、utf8 rc0、toctrees 本束 0 命中、束定向 dummy Sphinx 构建 0 error/warning。未执行任何 git commit（用户要求）。详见 review.md。

> 方法论：seven-concepts 场景4（知识沉淀）链路 R→I→E，V 独立成门；source-code-to-okf-wiki v1.5.0 五阶段纪律。
> 束根：`projects/awesome-okf-xs/doc/bundles/jishu/systems/kylin-wayland-compositor/`
> 信源：`external/dao/action/kylin-wayland-compositor` @ `4df656222427f3cd0101e41d828fb64805e66c15`
> 工作底稿目录：`.trae/specs/okf-wiki-ecosystem/kylin-wlcom-okf-wiki/`（facts 工作版、insights 草稿、子代理回传）

## Task 1: G0 信源固定复核与工作底稿骨架

- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 复核源仓库 remote/HEAD/分支/工作树干净度，记录全 hash、提交日期、与 `build/1.3.1-ok21` 标签距离；落盘后 V 前再核一次。
  - 在 spec 工作目录建 `facts/` 工作子目录（r1-build.md ~ r5-clients.md）与 `insights-draft.md`；记录开工规模基线的脚本与口径（465 C/H、138417 行，等待 V 复算）。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-1.1: `git -C <src> rev-parse HEAD` 输出等于 4df656222427f3cd0101e41d828fb64805e66c15，`status --porcelain` 为空；证据写入 source-code-map 草稿。
  - `rule` TR-1.2: 工作底稿目录存在 5 个 facts 占位文件，且不含束内正式文档。

## Task 2: R1 事实簇——构建/启动/配置/打包（委派只读子代理）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 读 `meson.build`、`meson_options.txt`、`src/main.c`、`src/server.*`、`include/server.h`、`src/config/`、`data/`（systemd unit/target/wrapper/desktop/man/udev/embed.c/config.json）、`debian/`、`README.md`、`docs/ENV.md`、`docs/CONTRIBUTING.md`、`docs/KNOWN_ISSUES.md`、顶层 `.clang-format`。
  - 产出 F-xxx 编号事实：依赖及版本约束、meson 选项全表（脚本计数）、HAVE_* 宏生成机制、CLI 参数与 `-D` 调试项、环境变量全表（与 ENV.md 对账）、日志路径与等级、main.c 启动序列（函数级顺序）、server 核心结构字段分组、data 资产安装去向、debian 包拆分。
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-2.1: 事实零推断词（"用于/目的是/设计为"），每条含文件:行号或行号区间。
  - `rule` TR-2.2: meson 选项数、环境变量数、CLI 选项数经脚本（正则/meson 文件解析）计数并附命令；与 README/ENV.md 文档口径差异列出。

## Task 3: R2 事实簇——后端/渲染/场景/输出/painter（委派只读子代理）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 读 `src/backend/`（backend.c、drm/ 全部含 shaders、fbdev、session/logind、libinput 仅后端接口部分、eis）、`src/render/`（renderer/allocator/egl/opengl/pixman/pass/profile/pixel_format/drm_syncobj*）、`src/scene/`（scene/surface/xdg_shell/render/decoration/animation/linear_gradient/stroke_rect/thumbnail）、`src/output/`、`src/painter/`、对应 `include/backend|render|scene/`、`include/output.h`、`include/painter.h`。
  - 事实：后端结构体表与自动选择逻辑、DRM KMS/原子提交/modifiers/lease/monitor/PNP 生成、logind session 接口、EIS 后端用途证据、renderer 选择（gl/gles2/pixman/vulkan 环境变量与代码分支）、allocator 与 GBM、drm_syncobj v1/timeline 条件编译、scene 节点类型与构建顺序、输出热插拔与配置持久化调用链。
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-3.1: 关键结构体/函数（如 backend 入口、renderer 创建、scene 树构造）均有文件:行号事实，Grep 可命中。
  - `rule` TR-3.2: 该簇 C/H 文件数、shader 文件数经脚本计数；事实清单标注计数口径。

## Task 4: R3 事实簇——输入/视图/工作区/widget/xwayland/theme/util（委派只读子代理）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 读 `src/input/`（action/binding/config/cursor/data_device/event/keyboard/pointer/touch/tablet/gesture/seat/keyboard_group/primary_selection/function 等以实际文件为准）、`src/view/`、`src/widget/`、`src/xwayland/`、`src/theme/`、`src/util/`（聚焦与输入/视图协作的部分：event/queue/spsc_chain/anim/dialog/dbus/spawn 等）、对应 include 目录。
  - 事实：seat/keyboard group/xkb 处理链、IME（input-method v2、text-input v1/v2/v3、virtual-keyboard）接入点、指针/触摸/数位板/手势事件流、快捷键 binding 解析与 action 分发、光标与软件光标 quirks、view/toplevel 状态机字段、workspace 切换与虚拟桌面协议消费、widget（menu/scaled_buffer）机制、xwm 窗口管理与 DND/选择、theme 加载。
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-4.1: 事件从 backend libinput 回调到 view/effect 的分发链有连续事实（函数名+行号）。
  - `rule` TR-4.2: input 源文件数、xwayland 源文件数脚本计数；协议-实现对应（如 zwp_text_input* 注册点）给出 Grep 证据。

## Task 5: R4 事实簇——特效/插件/安全（委派只读子代理）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 读 `src/effect/` 全部（effect 框架 + 各内置特效 .c + shaders/）、`src/plugin/`（含 `security/`）、`include/effect/`、`include/kywc/plugin.h`、`include/kywc/` 其余公共头、`include/security/`、`src/security/`（若存在）。
  - 事实：插件 API 契约（注册宏/生命周期/接口表）、effect 基类与 animator/transform 节点体系、内置特效清单（脚本计数并按功能分类：动效/模糊/截图录屏/辅助功能/输入可视化/水印壁纸等）、shader 资源加载、PLUGIN_DIR 扫描与加载顺序、security 插件（gui.cpp）做什么、`kywc_*` 公共头导出面。
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-5.1: 内置特效 .c 文件数脚本计数并逐个给出一句话事实（来自代码证据，非文件名猜测）。
  - `rule` TR-5.2: 插件接口每个导出符号在 `include/kywc/plugin.h` 与 src/plugin 实现中双向 Grep 命中。

## Task 6: R5 事实簇——协议/libkywc/portal/examples/i18n（委派只读子代理）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 读 `protocols/`（XML + meson.build，全部 27 个待脚本复核）、`libkywc/`（含 kywc.syms、meson.build、provider.h、各 kywc_*.c）、`portal/`（main/access/screencast/screenshot/remote_desktop/input_capture/ei_sender/session/request/stream/wayland + data 单元）、`examples/`（lib/ wlu、gui/ QML、各独立示例 .c）、`po/`（LINGUAS/POTFILES）、`tools/`（若存在）、`docs/PROTOCOLS.md`。
  - 事实：XML 协议清单与按族分类（wayland core/wlr/kde/ukui/kywc/external）、代码生成与全局注册函数（Grep global_bind*）、PROTOCOLS.md 支持矩阵与 XML/代码的双源对账（抽样）、libkywc 公开 API 面（kywc.syms 行级事实）、portal 各接口实现状态、PipeWire 串流链路、wlu 四文件职责、QML 示例结构、po 语言数（LINGUAS 计数）。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-7
- **Test Requirements**:
  - `rule` TR-6.1: protocols/ XML 文件数脚本计数（去重名），PROTODOLS.md 表中协议行数独立计数，差异（如重复 xwayland_shell_v1 行）记录。
  - `rule` TR-6.2: libkywc 导出符号数按 kywc.syms 脚本计数；portal D-Bus/portal 接口名与 .service/.portal data 文件对账。
  - `rule` TR-6.3: LINGUAS 语言数、examples C/C++ 文件数脚本计数。

## Task 7: I 阶段——架构洞察四元组 + 知识地图

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5, Task 6
- **Description**:
  - 汇总 5 簇事实，全局连续编号 F-xxx；产出 `insights-draft.md`：3-5 个洞察四元组（陈述/证据 F 编号/反常识/行动）、Mermaid 知识地图、16 篇 concept 的 F 编号覆盖矩阵；裁决 spec Q3（篇数是否微调，14-17 区间内）。
  - 复核所有数量类事实口径，闭合 R 簇间矛盾（G1/G2 门）。
- **Acceptance Criteria Addressed**: AC-7, AC-8
- **Test Requirements**:
  - `rule` TR-7.1: 每篇 concept 的覆盖矩阵至少映射 5 条 F 事实，F 编号无重复分配冲突。
  - `rubric` TR-7.2: 洞察质量；1-5；1=事实复述，3=有洞察但四元组残缺，5=四元组完整且反常识点有硬证据；阈值 >=4；证据：insights-draft.md 评审记录。

## Task 8: E1——references 信源先行（9 份 + index 占位最后补）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 先写 `references/source-code-map.md`（信源固定四要素、目录地图、规模口径、Gitee 固定 hash 链接规则）与 `references/project-docs.md`（README/docs/PROTOCOLS/ENV/KNOWN_ISSUES/CONTRIBUTING 登记）。
  - 再把 5 份 facts 工作版整理发布为 `references/facts-<cluster>.md`（带 OKF frontmatter、sources 指向 source-code-map/project-docs）。
  - 发布 `references/insights.md`（四元组+知识地图）。
- **Acceptance Criteria Addressed**: AC-1, AC-4, AC-8
- **Test Requirements**:
  - `rule` TR-8.1: 本任务完成时 references/ 下 8 份内容 .md 存在（verification.md 除外），每份 frontmatter type 非空、sources 不指向不存在文件。
  - `rule` TR-8.2: 全文无 file:///、无 `external/dao`、无本地绝对路径（Grep 0 命中）。

## Task 9: E2——concepts 批次 A（00-04，5 篇）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 8
- **Description**: 00-overview、01-build-run、02-wayland-wlroots-basics、03-startup-architecture、04-backends；每篇附本篇数据流位置、F 编号事实引用、短代码片段（标文件出处）、「相关概念」。
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-7
- **Test Requirements**:
  - `rule` TR-9.1: 5 篇 frontmatter 齐备且 sources 指向已存在 references；`/concepts/`、`/references/` 链接全部可解析。
  - `rubric` TR-9.2: 教学连贯性；1-5；锚点 1/3/5 同 AC-7；阈值 >=4；证据：主会话自评+V 阶段复核引用具体段落。

## Task 10: E3——concepts 批次 B（05-10，6 篇）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 9
- **Description**: 05-rendering、06-scene-graph、07-output-management、08-input、09-view-workspace、10-effects-framework。
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-7
- **Test Requirements**:
  - `rule` TR-10.1: 本篇出现的结构体/函数/环境变量/宏 Grep 命中（批内自检表），未命中项改写后复验。
  - `rubric` TR-10.2: 输入→场景→特效数据流跨 06/08/10 可追踪；1-5；阈值 >=4。

## Task 11: E4——concepts 批次 C（11-15，5 篇）

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 10
- **Description**: 11-plugin-system、12-protocols、13-xwayland、14-security-portal、15-libkywc-clients。
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-7, AC-8
- **Test Requirements**:
  - `rule` TR-11.1: 12-protocols 的协议矩阵数字与 facts-r5/ PROTOCOLS.md 双源一致；15-libkywc API 名与 kywc.syms 一致。
  - `rubric` TR-11.2: 可迁移模式（协议裁剪/ABI 控制/扩展分层）阐述含触发条件与反模式；1-5；阈值 >=4。

## Task 12: E5——examples（3 篇）

- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 11
- **Description**: 01-effect-plugin（simple_plugin/alpha_modifier/kde_keystate + meson 注册走读）、02-wlu-utilities（examples/lib + monitor/output_doctor/virtual_desktop）、03-libkywc-qml-client（libkywc API + examples/gui）。
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-7
- **Test Requirements**:
  - `rule` TR-12.1: 示例中引用的代码片段均标注源文件路径（固定 hash Gitee 链接），函数名 Grep 命中；所有构建/运行命令标注「本次未执行」。
  - `rubric` TR-12.2: 可跟做性；1-5；1=片段跳跃无法跟做，3=主路径可跟但缺前置，5=前置/步骤/预期/排障完整；阈值 >=4。

## Task 13: E6——束内 index/log 与三级导航注册

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 12
- **Description**:
  - 最后写 `concepts/index.md`、`examples/index.md`、`references/index.md`（无 frontmatter，含隐藏 toctree，stem 与文件一一对应）、束根 `index.md`（okf_version + 内容概览 + toctree 收三组+log）、`log.md`（2026-10-14 首版条目：新增/事实来源两段）。
  - 更新 `jishu/systems/index.md`（表格新增行 + toctree 增 kylin-wayland-compositor/index，简介文字补一句）；`jishu/index.md`（systems 束数 2→3 与简介行）；`bundles/index.md`（frontmatter 628→629、计数行 628→629、mermaid jishu 465→466、节标题 465→466、systems 表行 2→3；groups 61/domains 9 不动）。
- **Acceptance Criteria Addressed**: AC-1, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-13.1: 四个 index 的 toctree stem 集合与目录文件集合严格相等（人工比对表 + 门禁）。
  - `rule` TR-13.2: 三处共享索引只改 systems 相关与总计数行，diff 中无其他束内容改动。

## Task 14: V 阶段——独立手段自检 + verification.md

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 13
- **Description**:
  - 运行 `python scripts/check-utf8.py`、`check-toctrees.py`、`check-bundles-index.py`（cwd=子项目根；invoke 不可用时直接 python）；变更文件 dummy Sphinx 构建；符号 Grep 全量复核（AC-2 清单）；数量断言独立复算（AC-3，换命令口径）；链接扫描；路径纪律扫描；外部 Gitee 链接抽样可达。
  - 写 `references/verification.md`（type: Reference，含命令、输出摘录、符号核验表、计数对账表、遗留项与非本束红项归属说明）；修复发现的问题并复验。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-14.1: 三道门禁束相关 0 失败（或红项归属证明完整）；dummy 构建 0 error，输出粘贴入 verification.md。
  - `rule` TR-14.2: 符号核验表未命中数=0（或修复复验记录齐）；计数对账表无未解释差异。

## Task 15: Review——fresh-context 只读独立审查

- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 14
- **Description**: 委派一个全新 general_purpose_task 只读审查（不携带实现上下文）：按 review 契约核验 AC-1~AC-8，重点攻击虚构 API、计数失真、链接/路径、教学连贯性与洞察质量；产出结构化结论 pass/fail/blocked。
- **Acceptance Criteria Addressed**: AC-1~AC-8
- **Test Requirements**:
  - `rule` TR-15.1: review.md 在本任务创建（此前不存在），每个 AC 有独立证据列与 pass/fail 裁决。
  - `rubric` TR-15.2: 审查独立性与覆盖度；1-5；1=自审换皮，3=覆盖部分 AC，5=逐 AC 独立取证含 Grep/门禁复跑；阈值 >=4。

## Task 16: 修复闭环 + C 收尾（不提交 git）

- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 15
- **Description**:
  - fail 则把全部 actionable 发现建成 Issue 任务（I-1…）回到 Implement，修复后重跑 Task 14/15 直至 pass；pass 后定稿 log.md，输出交付报告（束路径、篇数、F 事实数、门禁证据、未提交声明、后续可执行的子模块原子提交建议）。
  - 不执行 git add/commit/push；等待用户明确指令。
- **Acceptance Criteria Addressed**: AC-7, AC-8
- **Test Requirements**:
  - `rule` TR-16.1: `git -C projects/awesome-okf-xs status` 变更仅限本束 + systems/jishu/bundles 三索引，无 commit 产生。
  - `rule` TR-16.2: tasks 队列所有项 ∈ {completed, user-approved cancelled}，review 终裁 pass。
