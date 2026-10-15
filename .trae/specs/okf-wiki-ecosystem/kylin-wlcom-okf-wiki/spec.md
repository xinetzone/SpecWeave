# kylin-wayland-compositor 源码 → OKF Wiki 教程知识包 - 需求规格（PRD）

## Overview

- **Summary**：以 `source-code-to-okf-wiki` 五阶段工作流（阶段0 信源固定 + R→I→E→V→C，由 seven-concepts 元编排按「场景4 知识沉淀 R→I→E」链路调度，V 对抗审查独立成门，C 原子提交等待用户明确指令）系统学习 openKylin 默认 Wayland 合成器 kylin-wayland-compositor（简称 **kywc / kylin-wlcom**）源码（本地审计副本 `external/dao/action/kylin-wayland-compositor`，固定提交 `4df656222427f3cd0101e41d828fb64805e66c15`，2026-10-12，分支 `openkylin/huanghe`，`git describe` = `build/1.3.1-ok21-761-g4df65622`），在 `projects/awesome-okf-xs/doc/bundles/jishu/systems/kylin-wayland-compositor/` 新建一个源码教程型 OKF bundle（16 篇 concepts + 3 篇 examples + 9 份 references + 各级 index/log）。
- **Purpose**：把一个基于 wlroots 0.17、约 465 个 C/H 文件、约 13.8 万行、15 个 src 子系统的生产级 Wayland 合成器，转化为可溯源到文件:行号的系统中文教程，覆盖「启动→后端→渲染→场景→输出→输入→视图/工作区→特效→插件→协议→XWayland→安全/门户→客户端库」完整架构，并沉淀 C/wayland 大型项目可迁移的架构模式。
- **Target Users**：希望系统读懂 Wayland 合成器内部机制的中文技术读者（Linux 桌面/图形栈工程师、openKylin/UKUI 生态开发者、想为 kywc 写特效插件或调用 libkywc 的应用开发者），以及研究「AI agent 源码精读→知识包」工程方法的实践者。

> ⚠️ **实施后勘误**：本规格写于开工前（2026-10-14 上午），其中若干规模基线数字在 V 阶段独立复算后被修正（行数 138417→165280、协议 XML 27→34、changelog ok21→ok36、src/ 根为 main.c + server.c 两个文件等）；FR-7/AC-6 中按 628→629 预估的全库总数也已因并行会话入库而漂移。完整勘误表见文末「Post-implementation Errata（实施后勘误）」一节。

## Goals

- G1：在 `jishu/systems/kylin-wayland-compositor/` 产出符合 OKF v0.2 的完整 bundle（frontmatter、三层目录、toctree、log）。
- G2：全部技术陈述可溯源：事实编号 F-xxx 按 5 个子系统簇登记于 `references/facts-*.md`，每条给出 `4df6562` blob 中的文件路径与行号区间；关键结构体/函数/宏/XML 接口名经 Grep 级存在性验证。
- G3：知识主线贯穿合成器数据流：main 启动 → wlroots 后端（DRM/fbdev/session/libinput/EIS）→ renderer/allocator/drm-syncobj → scene 图与 surface → 多输出 → 输入事件分发 → view/workspace → 特效与插件 → 协议全局注册 → XWayland 兼容 → security/portal/libkywc 外部接口。
- G4：诚实呈现 kywc 的私有协议族（ukui/kywc 两套 XML）与 wlr/kde 协议矩阵：协议支持情况以仓库 `docs/PROTOCOLS.md` 与 `protocols/*.xml` 双源对账，支持版本数字不照抄单一信源。
- G5：诚实的证据边界——本次为静态源码学习：不在 Linux/DRM 环境构建运行合成器、不运行其测试、不验证图形渲染效果；README/docs 自陈能力按「项目文档口径」引用并标注。
- G6：完成三级索引计数面更新（systems 分组、jishu 域、bundles 总索引）并通过束相关门禁（toctrees / bundles 三角计数 / utf8 / 变更文件 dummy Sphinx 构建）。

## Non-Goals

- N1：不逐行讲解全部 465 个文件与全部内置特效/配置键——教程在架构层讲清机制与契约，代表性实现深入走读，其余给出文件地图与延伸阅读路径。
- N2：不修改 `external/dao/action/kylin-wayland-compositor` 源仓库任何文件，不切换其检出；不将其升级为 vendor/ git submodule（沿用 opentpu/tuya-iot 等源码束先例：references 登记 canonical 远程 + 固定全 hash 的 Gitee URL；本地路径仅出现在 spec 工作底稿中）。
- N3：不重排、不改写 systems 组既有两束（wsl、powershell-hell）的任何已验证文档；新束对既有束只做必要的单向导航引用。
- N4：不执行任何 git commit / push（子模块与主仓均不提交），完成后由用户决定；原子提交（C）阶段只做束内 log 定稿与交付报告。
- N5：不翻译 `docs/` 英文文档（内容本来主要是中文）；教程为基于源码事实的原创中文组织，不大段复制 GPL 源码（仅教学必要的短引用）。
- N6：不做性能/兼容性数字的第三方复现；不评判 openKylin 发行策略。

## Background & Context

- 信源现状（2026-10-14 实测）：
  - 本地审计副本 `external/dao/action/kylin-wayland-compositor`：remote `https://gitee.com/openkylin/kylin-wayland-compositor.git`，HEAD = `4df656222427f3cd0101e41d828fb64805e66c15`（2026-10-12 21:07 +0800，Weblate 翻译提交），分支 `openkylin/huanghe`。
  - 最近标签 `build/1.3.1-ok21` 为 Debian 构建标签，HEAD 在其之后 761 个提交；meson 工程版本 `1.3.0`，debian changelog 版本 1.3.1-ok21。无可覆盖引用集合的正式 release tag，按「引用集合 ∩ 版本变更集合 = ∅」判据固定精确 commit hash（G0 接受的次选），同时记录 hash + 远程 URL + 日期。
  - 规模口径（2026-10-14 PowerShell 实测，待 V 阶段独立复核）：递归 `*.c/*.h` 共 465 个文件、`Measure-Object -Line` 合计 138417 行；`src/` 下 15 个子系统目录（backend/config/effect/input/output/painter/plugin/render/scene/security/theme/util/view/widget/xwayland），另有顶层 `main.c`；外层还有 `libkywc/`（公共客户端库 + `kywc.syms` 符号脚本）、`portal/`（xdg-desktop-portal-wlcom）、`examples/`（C 插件示例 + lib 工具库 + QML GUI）、`protocols/`（27 个 XML，待脚本复核）、`data/`（systemd/udev/桌面入口/man page）、`po/`（多语言）、`debian/`（打包）。
- 目标位置依据：Wayland 合成器属操作系统显示服务器/图形基础设施。systems 组定位为「操作系统与基础设施」（现有 wsl、powershell-hell 两束）；gui 组明确限定为 Python 桌面 GUI 开发（Qt/tkinter/tauri），不收 C 系统软件。故入 `jishu/systems/`，不新建分组。
- 规范来源：子项目 `projects/awesome-okf-xs/AGENTS.md`、`.agents/rules/frontmatter.md`（OKF v0.2）；同型样板束 `jishu/iot/home-assistant/`（19 concepts + examples + references 含 `facts-*.md`/insights.md 的源码束）与最近同型规格 `.trae/specs/opentpu-okf-wiki/spec.md`；主仓技能 source-code-to-okf-wiki v1.5.0（信源先行、每批 ≤7、index 最后写、Grep 验证、计数断言 R 脚本/V 独立双计、toctree 必填）。
- 关键技术背景（待 R 阶段证实/细化）：wlroots >=0.17,<0.18 与 `-DWLR_USE_UNSTABLE`；wayland-server >=1.23、wayland-protocols >=1.36；meson 选项裁剪协议族（`HAVE_KDE_*/HAVE_UKUI_*/HAVE_WLR_*` 宏）；主程序 `kylin-wlcom` 经 `wlcom.syms` version-script 控制导出；插件目录 `<prefix>/lib/kylin-wlcom/plugins`；README 致谢 sway/wayfire/labwc/wlroots。

## Functional Requirements

- **FR-1（束结构）**：创建 `jishu/systems/kylin-wayland-compositor/`，含根 `index.md`（带 `okf_version: "0.2"`）、`log.md`、`concepts/`（00-15 共 16 篇 + index）、`examples/`（3 篇 + index）、`references/`（source-code-map / project-docs / facts-×5 / insights / verification 共 9 份 + index）。
- **FR-2（信源先行）**：E 阶段第一批落盘文件为 references 信源登记；所有 concept/example 的 frontmatter `sources` 指向 references 内已存在文件；正文外部源码链接使用固定到 `4df6562` 的 Gitee blob URL，禁止 file:///、禁止出现 `external/dao` 本地路径。
- **FR-3（内容覆盖）**：16 篇 concepts 按学习路径编号——
  00 项目全景与学习路径；01 依赖/构建/运行/CLI/环境变量/日志/启动单元/打包；02 Wayland 与 wlroots 基础概念；03 main.c 启动序列与 server 总体架构；04 后端层（drm/fbdev/session-logind/libinput/EIS 与自动选择）；05 渲染体系（renderer/allocator/pass/profile/drm-syncobj/像素格式/直接扫描输出）；06 场景图与 surface（scene/xdg_shell/decoration/gradient/stroke/thumbnail）；07 输出与多显示器管理（output/kde-output v2/ukui-output/wlr-output-management）；08 输入系统（seat/keyboard group/IME/text-input/pointer/touch/tablet/gesture/cursor/binding/选区）；09 视图、工作区与窗口管理（view/workspace/toplevel/action）；10 特效框架与内置特效；11 插件系统（kywc plugin API/PLUGIN_DIR/security 插件）；12 协议全景与私有协议族（XML 代码生成、全局注册、PROTOCOLS 矩阵对账）；13 XWayland 兼容层（xwm/xwayland_shell/noxwayland）；14 安全模型与 xdg-desktop-portal-wlcom（screenshot/screencast/remote-desktop/input-capture/EI/PipeWire）；15 libkywc 客户端库与示例生态（syms 符号控制/缩略图与串流 API/wlu 工具库/QML GUI 示例/tools）。
- **FR-4（examples）**：3 篇实战走读——①跟 `examples/simple_plugin.c`（+ `alpha_modifier.c`/`kde_keystate.c`）走一遍特效插件结构与 meson 注册；②`examples/lib`（wlu：buffer/display/input/window）与 `monitor.c`/`output_doctor.c`/`virtual_desktop.c` 工具走读；③libkywc 稳定 API + `examples/gui` QML 缩略图客户端（ThumMain/context/thumbnail/security）走读。所有命令注明「本次未执行」与前置 openKylin/wlroots 环境条件。
- **FR-5（facts 与计数）**：5 份 `references/facts-<cluster>.md` 承载 R 阶段全部 F-xxx 事实（按模块分组、文件:行号、零推断词）；数量类事实（C/H 文件数与行数、XML 协议数、内置特效源文件数、po 语言数、环境变量数、meson 选项数、portal 接口面等）一律脚本计数并记录命令与口径，禁止人工枚举当事实。
- **FR-6（洞察与模式）**：`references/insights.md` 给出 3-5 个四元组洞察（陈述/证据/反常识/行动）与知识地图；concept 11/12/15 等处沉淀可迁移模式（wlroots 不稳定 API 与版本钉死、编译宏裁剪协议族、version-script 控制 ABI、特效-插件双扩展机制、私有协议族与上游协议的并行策略、C11+meson 大型项目组织），并给适用边界。
- **FR-7（导航与计数）**：束内每个 index.md 含隐藏 `{toctree}` 块且收录本目录全部内容文档；更新 `jishu/systems/index.md`（表格行 + toctree，2→3）、`jishu/index.md`（systems 束数与简介行）、`bundles/index.md`（frontmatter total_bundles 628→629、正文计数行、jishu 节标题 465→466、jishu 分组表 systems 行 2→3、mermaid 节点文案）使官方计数门禁三角一致；groups 61、domains 9 不变。
- **FR-8（验证产物）**：`references/verification.md` 记录 G4 全项：结构/frontmatter、Grep 符号核验结果、计数断言（R/V 两口径、原始匹配数/去重名数分列）、链接检查、三道门禁与 dummy 构建输出、遗留问题与归属过滤说明。

## Non-Functional Requirements

- **NFR-1（零虚构）**：文中出现的每个文件名、结构体/函数/宏名、环境变量、CLI 选项、XML 协议与接口名、meson 选项名，必须能在 `4df6562` blob 中 Grep 命中；V 阶段全量复核并留证据。
- **NFR-2（数量断言）**：凡「X 个/Y 份/Z 处/N 篇」陈述，R 阶段对固定 blob 脚本计数，V 阶段换独立手段复核；每个数字附统计口径，勘误在 facts 文件留痕并三处同步（facts/insights/正文）。
- **NFR-3（风格一致）**：中文正文、kebab-case 英文文件名；二级标题分节；代码块标注语言；每篇结尾含「相关概念」；束内交叉链接一律 `/` 开头 bundle-relative；子目录 index 无 frontmatter；frontmatter 字段风格对齐 home-assistant 束（type/title/description/tags/generated/verified/status/stale_after/sources 齐备）。
- **NFR-4（证据边界显式）**：项目自陈能力/支持矩阵标注信源层级（仓库 README/docs/PROTOCOLS / 本次静态读码），教程不宣称运行验证；新束文档 `status: draft`、`stale_after: 2027-04-30`（上游活跃开发、wg API 不稳定，半年复核节奏）。
- **NFR-5（教学连贯）**：概念按学习路径编号，符号约定跨篇一致；每篇开头给「本篇在数据流中的位置」，16 篇串成从开机到客户端 API 的完整路径；跨篇引用用束内绝对链接。
- **NFR-6（门禁）**：束相关 toctree 检查零失败；计数门禁对本束三角一致；UTF-8 无 BOM；变更文件 dummy Sphinx 构建 0 error（全量门禁中若非本束归属的红项，过滤说明、不代为修复共享索引）。
- **NFR-7（合规）**：源仓库主许可 GPL-1.0-or-later（另有 LGPL/MIT-CMU/MulanPSL 单文件许可，见 LICENSES/）；教程为原创中文阐述，代码引用控制在教学必要的短片段并标注文件出处，不整文件搬运。

## Constraints

- **Technical**：产出在 git submodule `projects/awesome-okf-xs` 工作树内（子项目流程：本次只写不提交）；Windows + PowerShell 7 环境；门禁脚本位于子项目 `scripts/`（check-toctrees.py / check-bundles-index.py / check-utf8.py，纯 stdlib），可直接 `python scripts/...` 或经 `invoke gates.*`；Sphinx dummy 构建若缺依赖按 blocked 取证而非静默放行；R 阶段读码可并行委派 5 个只读子代理（按信息边界切簇、禁止写同一文件、事实以 markdown 回传主会话落盘）。
- **Business**：用户指定信源（本地 kywc 源码）与指定产出根（bundles）；公开内容（Gitee 官方开源仓库，GPL/LGPL/MIT/MulanPSL）。
- **Dependencies**：`external/dao/action/kylin-wayland-compositor` 工作树保持 `4df6562` 检出且不得切换/修改；仓库自带 `docs/`（PROTOCOLS/ENV/KNOWN_ISSUES/CONTRIBUTING）作为二级事实源。

## Assumptions

- A1：本地克隆在任务期间保持 `4df6562`、工作树干净（开工前与落盘前各核一次 hash）。
- A2：`4df6562`（用户指定路径时的实际 HEAD，openkylin/huanghe 分支顶端）即为用户意图对应的「当前源码」；固定全 hash 而非回退到构建标签。
- A3：子项目 Python 环境可直接运行 `scripts/` 下纯 stdlib 门禁；invoke/dummy 构建若缺依赖按 blocked 处理并取证。
- A4：systems 组是新束登记位置，不新建分组；Gitee blob URL 形如 `https://gitee.com/openkylin/kylin-wayland-compositor/blob/4df6562.../<path>`（V 阶段抽样核验可达性，不可达则退回树地址并记录）。
- A5：R 阶段子代理回传的事实由主会话统一编号入册（F-xxx 全局连续），子代理不直接写束内文件，避免并发写与编号竞态。

## Acceptance Criteria

### AC-1：束结构与 OKF frontmatter 合规（rule）

- **Given**：`jishu/systems/kylin-wayland-compositor/` 落盘完成
- **When**：运行 toctree 门禁（cwd=子项目根，`python scripts/check-toctrees.py`）并人工核对 frontmatter
- **Then**：rc=0 且本束零命中失败项；每个非保留 .md 有可解析 YAML 与非空 type；仅根 index.md 含 okf_version；子目录 index 无 frontmatter；log.md 存在且日期倒序
- **Pass Condition**：门禁输出中本束相关项 0 失败 + 逐文件 frontmatter 检查清单全部勾选
- **Evidence**：门禁 stdout（粘贴进 verification.md）、Glob 文件清单

### AC-2：零虚构 API/符号（rule）

- **Given**：全部 concept/example/facts 正文
- **When**：V 阶段把每篇出现的结构体、函数、宏、环境变量、CLI 选项、meson 选项、XML 协议/接口名整理为符号清单，在 `4df6562` blob 中逐一 Grep
- **Then**：每个符号有命中路径:行号（或明确标注为 wlroots/wayland 外部符号并给出来源）；任何无命中的 kywc 自有符号必须删除或改写为有证据表述
- **Pass Condition**：符号核验表零「未命中」（未命中项全部修复并复验）
- **Evidence**：verification.md 符号核验表（含 Grep 命令/命中数/抽样命中行）

### AC-3：数量断言经脚本双重计数（rule）

- **Given**：facts 与正文中全部数量陈述（C/H 文件数与行数、XML 数、特效文件数、po 语言数、环境变量数、meson 选项数、src 子系统数等）
- **When**：R 阶段脚本计数结果与 V 阶段独立复核结果（不同命令/不同口径）比对
- **Then**：两口径一致或差异已解释；每个数字带统计口径（含/不含什么、原始匹配数 vs 去重名数）；人工枚举零采信
- **Pass Condition**：计数对账表无数值冲突；465 文件 / 138417 行等开工基线数字经独立复算或被修正并留勘误痕
- **Evidence**：facts 文件计数记录（含命令）、verification.md 对账表

### AC-4：信源固定与路径纪律（rule）

- **Given**：references/source-code-map.md 与全部发布文档
- **When**：检查信源登记内容与束内链接
- **Then**：source-code-map 记录 remote URL、`4df656222427f3cd0101e41d828fb64805e66c15` 全 hash、提交日期、分支、与 `build/1.3.1-ok21` 标签关系、meson/debian 双版本；发布文档无 file:///、无 `external/dao`、无 .tmp/.chaos 路径；外部源码链接为固定 hash 的 Gitee URL
- **Pass Condition**：束内路径扫描 0 命中本地/临时路径；信源字段要素齐全
- **Evidence**：verification.md 路径扫描结果 + source-code-map 内容

### AC-5：链接完整可达（rule）

- **Given**：束内全部 Markdown 链接与三级注册链接
- **When**：检查束内 `/`-开头链接、相对链接、跨束链接（wsl 等）与外部 Gitee 链接抽样
- **Then**：内部链接目标全部存在；toctree 条目 stem 与文件一一对应；外部链接抽样 HTTP 可达
- **Pass Condition**：断链检查 0 失败（本束范围）
- **Evidence**：链接检查输出/手工清单写入 verification.md

### AC-6：三级导航与计数门禁（rule）

- **Given**：束文件落盘且 systems/index.md、jishu/index.md、bundles/index.md 已更新
- **When**：运行 `python scripts/check-bundles-index.py` 与 `python scripts/check-toctrees.py`、`check-utf8.py`
- **Then**：总索引 frontmatter（629/61/9）、计数行、jishu 节标题（466 束 · 18 组）、systems 表行（3）五面对账一致；本束相关项零失败；非本束红项过滤列明归属
- **Pass Condition**：门禁 rc=0（或红项全部证明与本次变更无关并记录）
- **Evidence**：门禁 stdout + git diff 统计的变更文件列表

### AC-7：教程质量与数据流贯穿（rubric）

- **Type**： `rubric`
- **Dimension**：教学有效性
- **Scale**：1-5
- **Anchors**：1 = 文件级事实堆砌、子系统间无关联、读者无法形成端到端路径；3 = 分层清楚但启动→渲染→输入→插件→客户端的数据流只局部打通、证据边界偶有模糊；5 = 学习路径平滑、每篇定位明确、同一请求（如「一次键盘输入到窗口特效上屏」）可跨 03/05/06/08/10 追踪、证据/边界/延伸阅读清晰，读者可按图完成静态走读
- **Pass Threshold**：>= 4
- **Evidence**：独立 Review 按维度评分并引用具体篇章证据

### AC-8：洞察与可迁移模式质量（rubric）

- **Type**： `rubric`
- **Dimension**：知识沉淀深度
- **Scale**：1-5
- **Anchors**：1 = 只有事实复述；3 = 有洞察但四元组不完整或迁移建议空泛；5 = 3-5 个四元组洞察证据扎实（如「编译宏裁剪协议族」「version-script 双库 ABI」「特效插件与场景节点的扩展分层」「私有协议族跟随上游节奏」），每个模式含触发条件、核心步骤、反模式与不适用边界
- **Pass Threshold**：>= 4
- **Evidence**：insights.md + concept 11/12/15，独立 Review 评分

## Open Questions

- [ ] Q1：R/I 工作底稿（facts 工作版、洞察草稿、子代理原始回传）放在 `.trae/specs/okf-wiki-ecosystem/kylin-wlcom-okf-wiki/` 下随 spec 留存，定稿后再「发布」入束 references/——默认按此执行（底稿可引用本地审计路径，发布版只保留固定 hash URL）。
- [ ] Q2：若子项目环境无法运行 dummy Sphinx 构建（缺 sphinx/myst），AC-1 的构建证据是否接受「门禁脚本 + 人工 frontmatter 核对」降级？默认：记 blocked 并尝试 `python -m sphinx` 一次取证，不静默降级。
- [x] Q3：concept 篇数（16）是否合适？默认按 FR-3 的 16 篇执行；R 阶段若发现 14-security-portal 或 15-libkywc 信息密度失衡，允许在 I 阶段知识地图评审时微调拆分（总数控制在 14-17 篇），调整记录进 tasks.md 并在审批门知会。——I 阶段裁决维持 16 篇（14 由 R4 安全三节 + R5 portal 整节共同支撑，不拆），已落实。

## Post-implementation Errata（实施后勘误）

> 本节由实施方于 2026-10-15 补注；勘误事实于 2026-10-14 经 V 阶段独立复算与 R1-R3 fresh-context 审查闭合。原文保留不动（规格是开工前快照），仅在此统一标注；每条均已在束内留痕（[verification.md](../../../../projects/awesome-okf-xs/doc/bundles/jishu/systems/kylin-wayland-compositor/references/verification.md)、各 facts 文件「V/R1 勘误」小节、spec 工作目录 review.md）。

| # | 位置 | 开工时记录 | 实施后核实值 | 依据与处置 |
|---|---|---|---|---|
| E1 | Purpose、Background L32 | 约 13.8 万行；`Measure-Object -Line` 合计 138417 行 | **165280 物理行**（465 个 C/H 文件不变） | PowerShell `Measure-Object -Line` 对字符串数组系统性少计（如 src/view/view.c 物理 3022 行被计 2578）；python 字节 LF 口径 165276 + 4 个末尾无换行文件补 1。束内 4 处文档已改并双口径并列 |
| E2 | Background L31 | debian changelog 版本 1.3.1-ok21 | 顶端 **1.3.1-ok36**（huanghe，2026-09-04；共 75 个版本条目） | 原文以最近构建标签 `build/1.3.1-ok21` 描述 `git describe` 无误（该标签确实存在），但同句把 changelog 顶端也写成 ok21；source-code-map 已分列 meson 1.3.0 / changelog ok36 / 标签 ok21 三个版本 |
| E3 | Background L32 | `protocols/`（27 个 XML，待脚本复核） | **34 个 XML / 77 个 interface**；另有第 35 个协议 XML 在 src/plugin/security/security.xml（不经 protocols/meson.build） | R5 簇脚本逐个解析 XML 计数；concepts/12 已用 34+1 口径并列出第 35 个的例外路径 |
| E4 | Background L32 | 15 个子系统目录，另有顶层 `main.c` | 15 个子系统目录 **281** 个 C/H + 根目录 **main.c 与 server.c 两个**，`src/` 合计 **283** | spec 漏列 server.c（432 行，server 装配主体）；concepts/03 已按两个根文件走读 |
| E5 | FR-7、AC-6（L46/L119） | 预期 total_bundles 628→629、jishu 465→466、systems 2→3 | systems **2→3 与本束净增 1 符合预期**；但全库总数因多个并行会话同期入库持续漂移：R3 终审时（10-14）目录树 634 束/jishu 469；10-15 目录树 634/jishu 470 | 全库/jishu 总数为易变共享计数，**以 `python scripts/check-bundles-index.py` 实时输出为准**，不以本规格数字为准；本束只对 systems 行与本束 toctree 负责。groups 61、domains 9 全程未变 |
| E6 | Background L32 | `src/` 子系统名单含 view 目录 | view 目录基线 42（R3 采集一度报 41） | 递归实测 42 个 C/H（根 38 含 view_p.h + tile/ 4 含 tile_manager_p.h），已在 facts-input-view 的 D-R3-01 就地裁决 |
| E7 | FR-6/关键技术背景 | 未给具体数量 | 实施中另核实：meson 选项 **44** 个（37 boolean + 3 feature + 4 string）、内置特效 **40** 个 `.c`、libkywc 公开 API **67** 个、LINGUAS 16 语言/27 个 `.po`、特效 shader 14 个 | 这些在开工时标为「待 R 阶段证实」，R/V 阶段全部脚本计数闭合，详见束内 00-overview 规模表 |

**勘误方法学注记（供后续源码束复用）**：① 行数类计数禁止使用 PowerShell `Get-Content | Measure-Object -Line`（少计），统一用物理行口径（python 逐字节计 LF，末尾无换行文件补 1）并在发布文档标注口径；② 向 Markdown 文件追加含行内反引号的中文文本时，PowerShell 双引号 here-string 会把反引号后的 `n`/`r`/`t`/`b`/`e` 解释为转义符（换行/CR/Tab/退格/ESC）而吞字或注入 C0 控制字符——本次 R2 审查即据此抓出 3 个 U+0008/U+001B；应使用文件工具、单引号 here-string 或独立脚本写入，并在 V 阶段做字节级 C0 扫描；③ glob/宏模式（如 `*.c/*.h`、`HAVE_KDE_*/HAVE_UKUI_*/HAVE_WLR_*`）必须整体包反引号，否则 `*` 会被 Markdown 当作强调定界符（本规格 L32/L35 即有此问题，2026-10-15 已修）。
