# Tasks

> 工作流：`source-code-to-okf-wiki`（阶段0 G0 + R→I→E→V→C）。所有事实基线为三仓库固定 commit：`1d48b6c`（wecom-cli）、`cae8a5b`（wecom-unified）、`6bcb59a`（wecom-aibot-python-sdk）。

- [x] Task 1: G0 信源稳定性门——恢复三个子模块工作树并固化基线
  - [x] SubTask 1.1: 对 `vendor/WecomTeam/{wecom-cli,wecom-unified,wecom-aibot-python-sdk}` 分别执行 `git reset --hard HEAD`（不 fetch、不切分支）
  - [x] SubTask 1.2: 核验 `git rev-parse HEAD` 为完整 hash `1d48b6c9…` / `cae8a5be…` / `6bcb59a9…`，`git status --porcelain` 为空
  - [x] SubTask 1.3: 核验受控文件数为 600 / 197 / 19，并实测 `wecom-cli/README.md`、`wecom-unified/skills/wecom-unified/SKILL.md`、`wecom-aibot-python-sdk/aibot/ws.py` 可读
  - [x] SubTask 1.4: 若出现权限位/行尾噪声，仅在子模块内做三分法归因记录；恢复失败则切换 `git show HEAD:<path>` 取证模式并在 sources 中声明

- [x] Task 2: R 阶段（一）——wecom-cli 事实采集（≥80 条 F 编号）
  - [x] SubTask 2.1: 采信 Cargo workspace 5 crate 与 npm 包装（`bin/wecom.js`、5 个平台包）结构与版本
  - [x] SubTask 2.2: 采信命令语法与 13 个 service 域、`+helper`、`auth` / `cache` / `schema` 管理命令、registry TTL 与 schema→clap 装配
  - [x] SubTask 2.3: 采信认证链路（`auth init|show` 参数、`credentials.enc` 加密、环境变量优先级、853004 会话刷新）
  - [x] SubTask 2.4: 采信传输与韧性（reqwest 后端、信封、轮询、断点续传、trace 链）与双域文件沙箱及 deny 策略
  - [x] SubTask 2.5: 统计并采信 `skills/` 15 个目录（含 `shared`）与「14 个业务 Skill」口径差异、每个 SKILL.md 的 `metadata.requires.bins`
  - [x] SubTask 2.6: 产出 `references/facts.md`（含路径:行号与取证命令）

- [x] Task 3: R 阶段（二）——wecom-unified 事实采集（≥50 条 F 编号）
  - [x] SubTask 3.1: 采信 `skills/wecom-unified/SKILL.md` 章节结构、frontmatter、`allowed-tools`
  - [x] SubTask 3.2: 采信前置检查三步（`--version` ≥1.2.1、`auth show --status`、`auth init --noninteractive`）与 `identity whoami`
  - [x] SubTask 3.3: 统计 133 篇 references 的域分布（contact/disk/media/message/doc/calendar/meeting/todo/sheet/smartsheet/smartpage/pptx/email 等）与命名规范
  - [x] SubTask 3.4: 采信 6 个脚本的入参/产物/依赖（`build_docx.py`、`build_page.py`、`collect.py`、`doc_image_extractor.py`、`pptx2image.py`、`recalc.py`）
  - [x] SubTask 3.5: 采信 PPT 模板系统（`assets/templates/index.json`、`DESIGN.preset.md`、`shell/content.jsx`、`slides/*.slide`、政务 gate）
  - [x] SubTask 3.6: 产出 `references/facts.md`

- [x] Task 4: R 阶段（三）——wecom-aibot-python-sdk 事实采集（≥45 条 F 编号）
  - [x] SubTask 4.1: 采信 9 个模块与公开 API 清单（`WSClient`、`WSClientOptions`、`WsFrame*`、`MessageType`、`EventType`、`TemplateCardType`、`decrypt_file` 等）
  - [x] SubTask 4.2: 采信 WS 生命周期（订阅帧 `aibot_subscribe`、30s 心跳、2 次缺失判死、指数退避 1s→30s）
  - [x] SubTask 4.3: 采信回复管线（串行队列上限 100、ack 超时 5.0s、`reply_stream`、`reply_template_card`、`reply_stream_with_card`、`update_template_card`）
  - [x] SubTask 4.4: 采信事件分发（`aibot_event_callback` → `event.<eventtype>`）与文件下载解密（Content-Disposition 解析、AES-256-CBC、PKCS#7）
  - [x] SubTask 4.5: 采信安装与配置（包名、Python ≥3.8、依赖下限、`.env.example`）与 `examples/` 两个示例文件；登记版本号不一致口径
  - [x] SubTask 4.6: 产出 `references/facts.md`

- [x] Task 5: I 阶段——三束洞察、知识地图与学习路径
  - [x] SubTask 5.1: 每束提炼 ≥4 条四元组洞察（陈述+证据 F 编号+反常识+行动），写入 `references/insights.md`
  - [x] SubTask 5.2: 每束给出 `00 → NN` 编号学习路径与前置依赖，写入 `concepts/index.md` 骨架
  - [x] SubTask 5.3: 提炼跨仓库「运行时 → 路由层 → 协议层」三层读法模式草案（供 C 阶段定稿）

- [x] Task 6: E 阶段（一）——三束 `references/` 层落盘
  - [x] SubTask 6.1: `tencent/wecom-cli/references/{index,sources,facts,insights}.md`
  - [x] SubTask 6.2: `tencent/wecom-unified/references/{index,sources,facts,insights}.md`
  - [x] SubTask 6.3: `tencent/wecom-aibot-python-sdk/references/{index,sources,facts,insights}.md`
  - [x] SubTask 6.4: 每束 `sources.md` 登记完整 commit、远程 URL、许可证、文件数、取证命令与「工作树基线」声明

- [x] Task 7: E 阶段（二）——`wecom-cli` 束 concepts + examples + index + log
  - [x] SubTask 7.1: 8 篇 concepts（定位与安装、命令模型、crate 架构、认证与会话、传输与韧性、沙箱与安全、Skills 层、开发与发布）
  - [x] SubTask 7.2: 3 篇 examples（安装与授权自检、通讯录检索与发消息、文档/表格读写链路；统一标注「未在本机实跑」）
  - [x] SubTask 7.3: `concepts/index.md`、`examples/index.md`、束根 `index.md`、`log.md`

- [x] Task 8: E 阶段（三）——`wecom-unified` 束 concepts + examples + index + log
  - [x] SubTask 8.1: 6 篇 concepts（套件定位与依赖、前置检查与身份、意图路由、references 分类学、脚本工具链、PPT 模板系统）
  - [x] SubTask 8.2: 3 篇 examples（安装与自检、消息/日程域操作、文档与表格产出链路；标注未实跑）
  - [x] SubTask 8.3: 各级 index 与 `log.md`

- [x] Task 9: E 阶段（四）——`wecom-aibot-python-sdk` 束 concepts + examples + index + log
  - [x] SubTask 9.1: 5 篇 concepts（概览与快速开始、WS 生命周期、帧协议与事件分发、流式回复与模板卡片、文件下载解密）
  - [x] SubTask 9.2: 3 篇 examples（回声机器人、流式+卡片、文件下载解密；基于 `examples/basic.py` 改写并标注未实跑）
  - [x] SubTask 9.3: 各级 index 与 `log.md`

- [x] Task 10: E 阶段（五）——索引与计数同步
  - [x] SubTask 10.1: `tencent/index.md`：新增 3 行导航、toctree 3 项、计数按实际复算（19→22 束）
  - [x] SubTask 10.2: `ecosystems/index.md`、`jishu/ai/index.md`、`jishu/index.md` 计数与导航同步
  - [x] SubTask 10.3: `doc/bundles/index.md`（`total_bundles` 722→725、jishu 行 528→531）、`README.md`（徽章 + 表格 jishu 行 + 合计）、`doc/index.md`（规模段落）
  - [x] SubTask 10.4: 与 `wecom-5-0-10-release`、`wecom-5-0-12-release`、`wecom-topic-scenarios` 建立双向互链（仅在其 index.md「主题关联/已知边界」补链，不改正文）

- [x] Task 11: V + C 阶段——独立验证、模式沉淀与交付记录
  - [x] SubTask 11.1: 对全部类名/方法名/常量/命令执行 Grep 真实性验证，零虚构 API
  - [x] SubTask 11.2: 机械复算全部数量陈述；检查链接、frontmatter 九字段、子目录 index 无 frontmatter
  - [x] SubTask 11.3: 运行 `check-toctrees.py`、`check-bundles-index.py`、`check-asset-baseline.py`（及 `check-section-anchors.py` 如存在），全部 rc=0
  - [x] SubTask 11.4: 三束 `log.md` 补齐 V 缺陷与修复记录；沉淀「三层读法」模式 + ≥3 条反模式
  - [x] SubTask 11.5: 输出交付清单（文件数、事实数、洞察数、门禁结果）；不执行 git 提交

# Task Dependencies

- Task 1 是全部任务的前置（G0 未通过不得进入 R 阶段）
- Task 2、Task 3、Task 4 相互独立，可并行
- Task 5 依赖 Task 2/3/4
- Task 6 依赖 Task 5（信源与洞察定稿后方可落盘 references）
- Task 7、Task 8、Task 9 依赖 Task 6，三者相互独立，可并行
- Task 10 依赖 Task 7/8/9（计数须以实际文件为真值）
- Task 11 依赖 Task 10