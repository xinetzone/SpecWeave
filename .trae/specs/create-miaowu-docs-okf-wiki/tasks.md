# Tasks：秒悟 Meoo 官方文档 OKF 双束沉淀

> 配套 spec.md ｜ Session：sc-20261018-meoo-docs
> 任务状态只写入 `Status` 字段；实施顺序按依赖排列。证据路径均为绝对路径。

## Task 1: 模板与门禁基线校准

**优先级**：high ｜ **Status**：completed（2026-10-18；锚点：bounty-plaza 束全部文件 + frontmatter 规范 + check-bundles-index.py + check-toctrees.py + amitabha-sutra/examples 范例；okf_version 一律 "0.2"）
**目标**：在写任何束文件前，机械确认 OKF 束文件的确切格式与 gates.bundles 检查项，杜绝凭印象造结构。
**动作**：
1. 完整通读范例束 `miaowu-bounty-plaza/` 全部文件（index.md、concepts/index.md 及每个概念页、references/{index,source-ledger,verification}.md、log.md；若有 insights/ 或 examples/ 同样读取）。
2. 读 `tasks/gates.py` 中 bundles 门禁实现（frontmatter 必填、计数对账、链接检查的实际规则）。
3. 读 miaowu 组 `index.md` 表格列结构与 ecosystems/index.md 条目写法。
4. 产出内联格式基线（概念页标题约定、F 编号格式、status 取值、ledger 表头）。
**Test Requirements**：
- TR-1（rule）：能在后续任务中引用每个结构要素的范例文件路径与行号；无"自创字段"。证据：任务完成证据中列出 ≥10 个格式锚点（路径#L行）。

## Task 2: 束B references 三件套（ledger + verification + index）

**优先级**：high ｜ **Status**：completed（2026-10-18；F-001–F-074 共 74 条，四源分段；verification 13 项含 Node 三口径/5 条 dated/转写噪声/两页非重复六重证据）｜ **依赖**：Task 1
**目标**：先建审计骨架。束B 源 4 个：cli-features、cli-aliyun、open、cli-open-guide。
**动作**：
1. 建目录 `miaowu/miaowu-cli-open-guide/references/`。
2. `source-ledger.md`：4 源登记（URL/标题/抓取日/分区），F 编号事实表（预计 70-90 条），覆盖全部命令、环境变量、端点、版本矩阵、套餐数字、权益边界、阿里云权限点、运维命令表。
3. `verification.md`：P0 核验表（逐条逐字回验暂存原文）；至少包含——
   - status:dated 条目：集成版权益未上线、AK/SK 人工创建、OAuth 不可自行注册、限时免费 1/4/8；
   - status:conflicting/context 条目：Node 20（CLI 安装前置）vs Node 18+（开放集成运行环境）vs Node 24.15.0（全栈云端构建镜像）三者语境不同，并列引用不调和；
   - 转换残片（`_4d3c6c660f48`、punycode 乱码链接、`team.member.read` 占位 href）登记为"转写噪声，禁入正文"。
4. `references/index.md`。
**Test Requirements**：
- TR-2（rule）：4 个源 URL 与暂存文件一一对应；F 编号连续且每条含来源 URL+章节定位。证据：机械比对清单。
- TR-3（rule）：spec AC-03 中归属束B 的 P0 项（CLI 命令族、token 接口、MEOO_TOKEN、Node 三口径、1/4/8、`0.0.0.0:${PORT:-9000}` 等 ≥10 处）逐字回验通过；任何差异立即修正并记录。

## Task 3: 束B 概念页（7 个 + concepts/index）

**优先级**：high ｜ **Status**：completed（2026-10-18，7 页含 3 张决策表 + 4 条跨页洞察）｜ **依赖**：Task 2
**概念清单**：
1. `00-open-platform-overview.md` 开放平台总览：能力域（生成/云/发布）、三身份模式（团队集成/用户 API Key/OAuth）、三功能流程、接入前须知红线；
2. `01-cli-positioning.md` CLI 定位：本地 Agent 接管云端工作、支持工具、场景/人群、与网页端关系；
3. `02-cli-install-login.md` 安装（自动 skill-setup / npm 两种）、浏览器授权、`meoo login` 兜底、前置条件；
4. `03-deploy-static-vs-fullstack.md` 静态 vs 全栈部署决策（CDN / `--runtime image`、后端逻辑、适用框架、全栈云端构建环境规格与运行约束）；
5. `04-local-agent-workflow.md` 本地 Agent 协作工作流（意图话术、localhost:3015 预览、同步云端、网页/本地冲突规避、云服务开通延迟 2-3 分钟等 FAQ 坑点）；
6. `05-aliyun-byoc-deploy.md` 自有阿里云 BYOC（ROS 编排、RAM 专用 AK 与权限点、先询价后创建、deploy/update/status/delete/rollback 运维表、与默认部署对比、仅 RDS MySQL 限制）；
7. `06-team-skill-cli-integration.md` 团队 Skill+CLI 集成（AK/SK→member token HMAC 签发、`meoo skill install [--target]`、MEOO_TOKEN/MEOO_API_URL 注入、CI `--skip-build --skip-push --force`、token 生命周期四阶段、两接入方式对比）。
**Test Requirements**：
- TR-4（rule）：每个事实性断言挂 F 编号；命令块与 ledger 逐字一致；无 F 编号的"事实"不允许出现（教程性引导语除外）。
- TR-5（rubric，AC-12 局部）：概念页含「定位/何时用/怎么做/坑点边界/延伸」结构，7 页整体评分 ≥2.5/3，含 ≥2 张选型/决策表。

## Task 4: 束B examples（3 个命令流 + index）

**优先级**：medium ｜ **Status**：completed（2026-10-18，3 页均带文档级复现声明与 F 编号）｜ **依赖**：Task 3
**动作**：建 `examples/`：
1. `01-static-and-fullstack-deploy.md`（安装→登录→本地预览→`meoo deploy`→全栈首次 `--runtime image`）；
2. `02-aliyun-byoc.md`（装 aliyun CLI→`aliyun configure`→环境检查→询价→部署→运维与 DELETE 确认）；
3. `03-team-token-ci-publish.md`（签 token HTTP 报文→npm 安装 tgz→skill install→export 变量→whoami/projects list→projects use/cloud status/sandbox push/deploy→CI 直发）。
每个示例顶部声明"文档级复现，未做运行验证（2026-10-18）"。
**Test Requirements**：
- TR-6（rule）：示例命令 100% 来自源页（逐字），不拼接源页不存在的参数；每段命令标注来源 F 编号。

## Task 5: 束B 束根 index.md 与 log.md

**优先级**：high ｜ **Status**：completed（2026-10-18，读者地图 + 三口径提示 + toctree 四支）｜ **依赖**：Task 3、Task 4
**动作**：`index.md`（frontmatter 合规、读者地图、概念/示例/references toctree 与卡片、源站分区说明、stale_after 2027-01-18）；`log.md`（R→I→E 过程、CMD-LOG G1/G2 门、缺口：open 区未抓取页清单）。
**Test Requirements**：
- TR-7（rule）：frontmatter 通过 gates 字段校验；index 中全部相对链接可解析。

## Task 6: 束A references 三件套（14 源）

**优先级**：high ｜ **Status**：completed（2026-10-18；F-001–F-150 共 150 条十四源分段；verification 13 项，conflicting 双源并存/5MB vs 50MB 语境并列/13 项放弃核验）｜ **依赖**：Task 1（可与 Task 2-5 并行起步，ledger 独立）
**目标**：源 = 主页 + 13 features 页（web-apps/wechat-miniprogram/agent-modes/models/cloud-services/ai/asset-center/visual-editing/project-config/file-storage/skills/skill-marketplace/connectors）。
**动作**：
1. `source-ledger.md`：14 源、F 编号预计 120-160 条；模型页 13 模型的参数级宣传语（2.4T/552B/1M TPS 等）按"厂商自述"登记。
2. `verification.md`：
   - **conflicting 核心条目**：构建器模型页 13 模型（Qwen3.8 系列等）vs AI 服务页 9 个 API 传参值（`qwen3.6-plus`/`qwen3-max`/`kimi-k2.5`/`deepseek-v3.2`/`glm-5`/`MiniMax-M2.5`/`qwen3-vl-plus`/`qwen-image-2.0`/`wan2.7-image`），双源并存、注明页面定位差异与时效风险；
   - dated：套餐相关（代码下载限 LITE/PRO/MAX）、模型版本、技能页"后续支持 MCP"、连接器"后续将支持 MCP"；
   - 数字核验：5MB/10 个、50MB、回收站 30 天、TPS 80~100、1M≈1500 页 A4 等；
   - 截图依赖声明：visual-editing/file-storage/wechat-miniprogram 等页关键操作以截图承载，可转写文字层边界明确。
3. `references/index.md`。
**Test Requirements**：
- TR-8（rule）：14 个 URL 全登记；主页营销表述有"厂商自述"标记；冲突条目双方证据完整。
- TR-9（rule）：spec AC-03 中归属束A 的 ≥5 处 P0（两个 api.meoo.host 端点、MEOO_PROJECT_API_KEY、5MB、50MB）逐字回验通过。

## Task 7: 束A 概念页·区 1-2（平台总览 + 应用构建主线，6 页）

**优先级**：high ｜ **Status**：completed（2026-10-18，6 页，含 13 模型选型图谱与权责 10 行表，厂商自述逐条标注）｜ **依赖**：Task 6
**概念清单**：
1. `00-platform-overview.md`（主页：定位与产品形态、套餐/积分入口，营销话术标注）；
2. `01-agent-modes.md`（Agent/Swarms/Plan/Design 四模式选型表）；
3. `02-model-selection.md`（13 模型按厂商/定位/上下文/多模态图谱 + 与 AI 服务 API 模型的口径区别指引）；
4. `03-web-app-build.md`（四阶段流程、提示词五要素正反例、澄清、链接数据库、预览自测、版本回滚/对比、发布与自定义域名）；
5. `04-wechat-miniprogram.md`（七步上线、第三方服务商授权、H5/真机双预览、备案、审核、三方权责表、审核前清单、6 FAQ）；
6. `05-visual-editing.md`（点击编辑/双模/圈选标注/对话修改；截图信息边界）。
**Test Requirements**：
- TR-10（rule）：F 挂接规则同 TR-4；微信权责表逐行有源；无截图脑补。
- TR-11（rubric，AC-13 局部）：至少 2 条跨页四元组洞察（如"对话即控制台"、双轨预览）以独立小节呈现并标注洞察类型。

## Task 8: 束A 概念页·区 3-5（平台服务 + 文件配置 + 扩展生态，8 页）与 concepts/index

**优先级**：high ｜ **Status**：completed（2026-10-18，8 页 + concepts/index；07 页三段 fetch 按 F-087 还原换行，星号保留；Task 13 对 06/09 的 F 标签完成重映射）｜ **依赖**：Task 6（可与 Task 7 并行，文件不重叠）
**概念清单**：
7. `06-cloud-services.md`（后台工具箱：数据/文件50MB/Secret/GoTrue/独立数据库/实时消息、按需启用）；
8. `07-ai-service.md`（自动集成四步、Edge Functions、9 传参值表、两端点三类调用代码、计费、Cloud→AI 用量）；
9. `08-asset-center.md`（素材制作入口、Agent/直连双模、图/视频（全能参考/首尾帧）/音频三子类、积分预估、资产中心筛选/收藏夹/30 天回收站/批量）；
10. `09-file-storage.md`（10 格式/5MB/10 个、下载与套餐、>5MB 沙箱临存易失、CDN 四步法）；
11. `10-root-file-seo-geo.md`（验证文件默认开放 vs robots/sitemap/llms 开放双条件、独立域名判定、4 FAQ）；
12. `11-skills-authoring.md`（Skill 与 Prompt 区别、三步构建、提示词四原则与天气示例、两种应用方式、上线后五步迭代法）；
13. `12-skill-marketplace.md`（语义搜索、标签七类、详情权限矩阵、zip 上传）；
14. `13-connectors.md`（连接器本质、安装/连接/凭证、构建期与注入应用两场景、积分与明细、解绑范围、注册自有连接器、MCP 展望）；
另完成 `concepts/index.md` 全 14 概念导航。
**Test Requirements**：
- TR-12（rule）：14 个概念页齐备（含 Task 7 的 6 个）且编号连续；AI 调用代码两端点与参数表逐字一致。
- TR-13（rubric，AC-12 局部）：扩展生态 3 页含"何时用 Skill vs 连接器 vs AI 服务"辨析，评分 ≥2.5。

## Task 9: 束A index.md 与 log.md

**优先级**：high ｜ **Status**：completed（2026-10-18；Task 13 修复两处姊妹束死链前缀；log.md 含整改闭环条目）｜ **依赖**：Task 7、Task 8
**动作**：束根 `index.md`（五区读者地图、与束B 的分工互链、"对话即控制台"主线、stale_after）；`log.md`（R/I/E/V 记录、CMD-LOG G1-G3、采集局限、缺口清单）。
**Test Requirements**：
- TR-14（rule）：frontmatter 与全部内链通过校验；互链束B 使用相对路径。

## Task 10: 四层索引注册与计数五面对账

**优先级**：high ｜ **Status**：completed（2026-10-18；645→647 / 247→249 / 95→97 / 3→5，五面一致，check-bundles-index exit 0）｜ **依赖**：Task 5、Task 9
**动作**：
1. `miaowu/index.md` 表格新增 2 行（实施前重读确认当前 3 行写法与列结构）；
2. `ecosystems/index.md`：95→97（目录 16 不变，同步正文表述）；
3. `jishu/ai/index.md`：正文"247 个"→249、description 中 247→249、六大类表 ecosystems 行束数 95→97；
4. `jishu/index.md`：ai 一句话简介中"247 束"→249 束；
5. `bundles/index.md`：frontmatter `total_bundles: 647` + 正文 645→647；
6. 若实施前磁盘基线已变化，以磁盘实际值为基准 +2，并在两束 log.md 记录调整。
**Test Requirements**：
- TR-15（rule）：五面计数机械一致（grep 计数），无遗漏的旧数字残留（247/95/645/3 行束表等该改处全改、不该改处不动）。

## Task 11: 门禁、构建与污染扫描

**优先级**：high ｜ **Status**：completed（2026-10-18；门禁三件套 exit 0；首轮 -E 全量构建发现 I-07 一条 Malformed YAML，Task 13 修复后复跑归零，详见 Task 13）｜ **依赖**：Task 10
**动作**：
1. cwd=`projects/awesome-okf-xs/tasks` 执行 `python gates.py bundles`，再 `python gates.py all`；
2. 按子模块 README 跑 Sphinx 构建（dummy/linkcheck 或 html），确认两束 toctree 解析、零新增告警；
3. 污染扫描：新文件中无 `.temp/`、`file:///`、`_4d3c6c660f48`、`xn--`、`http://skill.md/`、`http://team.member.read/`；
4. `git -C projects/awesome-okf-xs status --short` 确认改动范围只在 doc/bundles 四层索引 + 两个新束目录；
5. AC 覆盖矩阵自查（AC-01..14 × 证据）。
**Test Requirements**：
- TR-16（rule）：两门禁退出码均为 0；Sphinx 零新增 warning；污染扫描 0 命中；改动范围符合 FR 边界。证据：命令输出摘录。

## Task 12: fresh-context 独立对抗评审（V）

**优先级**：high ｜ **Status**：completed（2026-10-18；fresh-context 只读子代理产出 review.md，结论 **fail**：AC-05/08/09 fail、AC-14=2.0；7 个 issue——I-01..I-07，P1×5、P2×2、无 P0；AC-03 抽核 20/20、AC-12/13 满分 3）｜ **依赖**：Task 11
**动作**：派发一个全新上下文的只读评审子代理，给其 spec.md/tasks.md/两束目录/暂存原文路径，执行四视角审查（事实核对者/新人读者/运维集成者/知识库维护者），结果写入 `.trae/specs/create-miaowu-docs-okf-wiki/review.md`。
**Test Requirements**：
- TR-17（rule）：评审由未参与写作的 fresh context 执行；每个 AC 均有独立复核证据；结论为 pass/fail/blocked 三选一且符合 Review Result Contract。

## Task 13: 整改闭环与复审

**优先级**：high ｜ **Status**：completed（2026-10-18；I-01..I-07 全部 fixed-verified，第二轮 fresh-context 复审最终结论 **pass**，无 I-08；AC-05/08/09 转 pass、AC-14 升至 3；详见 review.md 第 6 章）｜ **依赖**：Task 12
**动作**：将 fail 发现物化为 tasks.md pending issue（编号 I-xx），逐项修复、重跑相关门禁；复审由 fresh context 再执行一轮直至 pass；pass 后更新两束 log.md 评审记录与本文件全部任务状态。

**Issue 登记（源自 review.md 第 4 节）**：

| Issue | Sev | 位置 | 整改 | 自验证据 | 状态 |
|---|---|---|---|---|---|
| I-01 | P1 | 束B concepts/05:138 残片串 `_4d3c6c660f48` | 删除字面哈希，改无残片表述 | 污染正则复扫 concepts/+examples/ 0 命中 | fixed-verified（复审 pass） |
| I-02 | P1 | 束A index:86/124、束B index:91 死链（`../../`） | 三处前缀改 `../` | Test-Path=True；全束链接复扫 | fixed-verified（复审 pass） |
| I-03 | P1 | 束A 06/09/index/log 23 处 F 硬错配（11 编号） | 按台账权威映射重挂（F-069/070/071/072/078/111-115） | 逐号回台账对账无错配 | fixed-verified（复审 pass） |
| I-04 | P2 | 束B verification:35/157 自检「0 命中」失实 | 改两轮扫描据实记录（漏扫→命中→整改→0 命中） | 与 I-01 同次复扫证据一致 | fixed-verified（复审 pass） |
| I-05 | P2 | 束A 09:63/73 F-113 宽挂 | 改区间 F-112–F-114 | 同 I-03 对账 | fixed-verified（复审 pass） |
| I-06 | P1 | 束A 06:83 zip/json 下载→上传语义反转 | 按源稿 F-111 订正为下载通道口径 | 与暂存稿 file-storage.md:53 逐字复核；09:57 一致 | fixed-verified（复审 pass） |
| I-07 | P1 | 束A verification.md:33 frontmatter `- S7` | 补为 `- id: S7` | PyYAML 34/34 解析通过；-E 全量构建新束 0 告警 | fixed-verified（复审 pass） |

**整改后自验（2026-10-18）**：check-bundles-index/check-toctrees/check-utf8 均 exit 0；PyYAML 两束 34 个 frontmatter `parsed: 34 bad: 0`；污染扫描两束正文 0 命中；git status 仍恰为 5 M + 2 ??；`sphinx-build -b html -E -W --keep-going` 复跑（结果以复审确认值为准）。

**Test Requirements**：
- TR-18（rule）：所有 actionable finding 有对应 completed issue 与证据；复审结论 pass；队列满足 drained 条件。
