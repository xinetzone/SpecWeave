# kylin-wayland-compositor 源码 → OKF Wiki - Independent Review

- 审查方式：fresh-context 只读子代理，三轮（R1 全面审查 → 修复 → R2 复审 → 修复 → R3 窄口径终审）。
- 审查对象：`projects/awesome-okf-xs/doc/bundles/jishu/systems/kylin-wayland-compositor/`（33 md）；信源码固定提交 `4df6562`。
- 规格：同目录 spec.md（AC-1~AC-8）。

## Checkpoints（终裁，R3 后）

- [x] CP-1：AC-6 三级导航与计数门禁 — `rule` — **pass**
  - `check-bundles-index.py` rc=0（终验地面真值 634 束/61 组/9 域，本任务开工基线 628；增量含并行会话束，systems=3 注册正确，五面一致）；`check-utf8.py` rc=0（11556 文件）；`check-toctrees.py` 全局红项 82 处全部归属他束 WIP（tauri/deepseek-harness/wifit3/telecom-*/ling-3-1/wecom 等），过滤本束 0 命中。
- [x] CP-2：AC-1 束结构与 OKF frontmatter — `rule` — **pass**
  - concepts 16 / examples 3 / references 9 与三个子 index 的 toctree 严格相等；仅束根 index.md 含 okf_version；子 index 与 log 无 frontmatter；28 个内容文档 type 非空；全部无 BOM；C0 控制字符字节扫描 NONE。
- [x] CP-3：AC-2 零虚构符号 — `rule` — **pass**
  - R1 审查员独立 Grep/Read 约 48 个符号/行号/接口版本（IME 5 注册点、21 个特效 priority、10 个 XML interface version、portal 5 接口版本、9 个 libkywc API、启动链等）全部命中；发现的非符号断言问题（shared_module、MulanPSL）已转 finding 修复。R2 另抽 6 处全部命中。
- [x] CP-4：AC-3 数量断言双口径 — `rule` — **pass**（R1 fail → 修复后 pass）
  - python 独立复算：465 C/H、165280 物理行（勘 PowerShell 138417 少计）、src 283、34 XML/77 interface、40 特效 .c、14 shader、44 meson 选项、16 LINGUAS/27 .po、17/14/34 libkywc/portal/examples、67 API、18 layer、12 能力、21 action、851 facts。R1 三个冲突（绑定类型 19/20、scene 角色 22/23、KYWC 名 16/17）已全部闭合。
- [x] CP-5：AC-4/AC-5 信源路径与链接 — `rule` — **pass**
  - 全束 0 本地/临时路径；393 个束内链接 0 断链；33 个 Gitee 外链全部固定全 hash（抽样 HTTP 200/阴性 404）；1 处断链与 1 处伪链接已修。
- [x] CP-6：AC-7 教学有效性 — `rubric` — **pass，4/5**
  - 16 篇篇首数据流位置块 16/16、篇尾相关概念 16/16；键盘链与指针链逐跳行号可跨 04→08→09→10 追踪；14 篇端到端走读 portal→wldialog→libkywc→kywc-stream→PipeWire→EIS；证据边界高密度。扣分项（正文数字易被证伪）已随 F-1/F-3 修复消除。
- [x] CP-7：AC-8 洞察与可迁移模式 — `rubric` — **pass，4/5**
  - 五个四元组洞察四段齐全且被审查员独立印证（协议三态裁剪/SPSC 输入线程/三层 ABI/六级回退）；11/12/15 篇模式含触发条件、步骤、反模式与边界；I-4 携带的 shared_module 失实已修。
- [x] CP-8：NFR-6/7 构建与合规 — `rule` — **pass**
  - 束定向 `sphinx -b dummy` 三轮均 build succeeded，本束 ERROR/WARNING = 0（全局 ERROR 均他束 transition WIP）；代码引用均为 ≤14 行教学短片段（42/67 行块为 Mermaid）；28 文档 sources 齐备；中文原创。

## Findings 处置台账

| ID | 级别 | 问题 | 处置 | 验证轮 |
|---|---|---|---|---|
| F-1 | actionable/medium | key_binding_type 19→20（CUSTOM_DEF 为真实类型，NUM 才是哨兵） | 08 篇+facts 三处同步 | R2 fixed |
| F-2 | actionable/medium | shared_module 实为 2 处（security + examples/simple），非全树唯一 | 10/11/examples01/insights/facts 七处同步 | R2 fixed |
| F-3 | actionable/low-med | scene 真实角色 23（22 为有调试名数） | 00/06/insights/facts 四处同步+角色表含 SNAPSHOT | R2 fixed |
| F-4 | advisory | INPUT_PANEL 标注枚举值 11 | 09 篇已修 | R2 fixed |
| F-5 | advisory | 特效 23/26 两口径未分清 | 10 篇已注明 | R2 fixed |
| F-6 | advisory | KYWC 唯一名 16→17 | facts 勘误（后再精确化归因，第 17 名为 EIS_SOCKET） | R2/R3 fixed |
| F-7 | advisory | `(L197)` 伪链接 | 改全角括号 | R2 fixed |
| F-8 | advisory | insights 引用 R 底稿文件名 | 改发布名 | R2 fixed |
| F-9 | advisory | 17 角色枚举器未注 UNDEF | 10 篇补注 | R2 fixed |
| 额外 | actionable（实施方自查） | 「security.xml 唯一 MulanPSL」错误：实为 14 个 MulanPSL 协议 XML（6 kywc+7 ukui+security） | 12 篇+facts-r5 勘误 | R2 confirmed |
| N1 | actionable（R2 新发现） | 3 个 C0 控制字符（U+0008/U+001B）损坏勘误文本（PowerShell here-string 反引号转义引入） | python 字节级修复，全束扫描 NONE | R3 pass |
| N2/N4/N5 | advisory | 旧标题加内联勘误标记、EIS_SOCKET 归因、log 补审查记录 | 已处理（标记最终采用渲染可见普通文本） | R3 pass |

## Review History

### Review R1
- **Result**：`fail`
- **Evidence**：2 个 rubric 均 4/5 通过；rule 类 AC-3 因 3 处计数冲突失败，另 F-1/F-2 为 actionable；约 48 项符号核验全部命中、门禁与构建证据由审查员独立复现。
- **Findings**：F-1~F-9（3 actionable + 6 advisory）。

### Review R2
- **Result**：`fail`（窄口径）
- **Evidence**：F-1~F-9 全部 fixed（逐条源码/计数独立证实），MulanPSL 额外修复 confirmed（35 协议 XML 中 14 个 MulanPSL）；门禁 rc0、dummy 本束 0 error/warning；新发现 N1（3 个控制字符）阻塞，N2~N5 advisory。

### Review R3
- **Result**：`pass`
- **Evidence**：N1 修复后束内 C0 字符 NONE、损坏段还原为完整正确列表项；N2/N4/N5 完成；393 链接 0 断链、frontmatter 完整；utf8 rc0（11556）、bundles rc0（634）。
- **终裁**：CP-1~CP-8 全部 pass；无未处理 actionable finding。

## 范围与归属说明

- 子模块工作树无新增 commit（HEAD 未变）；变更仅限：束目录 33 文件（未跟踪）、bundles/index.md、jishu/index.md、jishu/systems/index.md。
- `jishu/ai/ecosystems/index.md` 的修改为并行会话在途变更，非本任务产物，未触碰。
- 全局 toctrees/dummy 他束红项（transition 语法、缺 index 等）归属并行会话 WIP，已过滤列明，未代为修复。
