---
title: TRAE 生态特性周报（2026-09-21）
date: 2026-09-21
source: "多源：TRAE 官方更新日志（docs.trae.cn / docs.trae.ai）+ 本地清单盘点（%USERPROFILE%\\.trae-cn）；各条目来源 URL 见正文"
report_type: trae-feature-watch
check_window: "2026-09-07 ~ 2026-09-21"
---

# TRAE 生态特性周报（2026-09-21）

> 本周监测窗口：2026-09-07（上次基线）～ 2026-09-21。
> 本期共提取 **11 条**增量特性/事实：官方版本更新 6 条、文档新特性 2 条、TraeWork 设计库 1 条、本地 skills·插件变化 2 条。
> 另有 3 个 Hotfix 版本仅修复已知问题（无特性内容），列于第一节备查。

## 一、官方版本更新

### 1. 企业版新增内置模型 DeepSeek-V4.1-Flash（本周新增）

- **来源**：[TRAE 企业版更新日志 · 2026-09-15](https://docs.trae.cn/enterprise_release-notes)
- **能力说明**：TraeCode、TraeCode Plugin 和 TraeCode CLI 企业版新增系统内置模型 **DeepSeek-V4.1-Flash**。
- **适用场景与实用价值**：Flash 定位轻量高速模型，适合高频、低延迟的日常编码问答与批量任务；企业管理员无需自行接入即可在模型开放范围内分配给成员使用。

### 2. TraeCode v3.3.99：支持分享对话（本周新增）

- **来源**：[TraeCode 更新日志 · 2026-09-08](https://docs.trae.cn/ide_changelog)（[分享对话文档](https://docs.trae.cn/ide_chat#hYf8wChBZ)）
- **能力说明**：IDE 内对话支持直接分享给他人查看。
- **适用场景与实用价值**：便于团队内传递排查过程、复用提示词与上下文，减少"截图 + 口述"的沟通成本；做技术分享或问题交接时可直接引用会话。

### 3. TraeCode v3.3.99：支持配置网络代理（本周新增）

- **来源**：[TraeCode 更新日志 · 2026-09-08](https://docs.trae.cn/ide_changelog)
- **能力说明**：TraeCode 客户端内可配置网络代理。
- **适用场景与实用价值**：企业内网或受限网络环境下，可通过代理访问模型服务与扩展资源，降低网络环境对 AI 协作的阻断。

### 4. TraeCode v3.3.97：支持插件市场【仅个人版】（基线漏采补提）

- **来源**：[TraeCode 更新日志 · 2026-09-03](https://docs.trae.cn/ide_changelog)（[插件市场](https://docs.trae.cn/ide_marketplace)）
- **能力说明**：个人版 TraeCode 内置插件市场，可浏览、安装官方插件扩展客户端能力。
- **适用场景与实用价值**：与 TraeWork 插件体系呼应，IDE 用户可在统一市场内按需扩展浏览器控制、设计、代码托管等能力。
- **备注**：条目日期（09-03）早于上次运行日（09-07），因子模块监测 URL 失效（详见第二节第 2 条）未入基线，本期补提。

### 5. TraeCode v3.3.93–96：Solo Agent 与 Agent 合并为 Agent【仅企业版】（基线漏采补提）

- **来源**：[TraeCode 更新日志 · 2026-09-01](https://docs.trae.cn/ide_changelog)
- **能力说明**：企业版中 Solo Agent 智能体与 Agent 智能体合并为统一的 **Agent** 智能体，支持在 IDE、SOLO 模式使用；能力集合包括：支持 `/goal`、`/plan`、`/spec` 等内置命令，支持根据模型选择是否开启 Max 模式，支持选择是否使用 Auto Mode 模型，支持调用自定义智能体。
- **适用场景与实用价值**：消除双智能体选择成本，一个入口同时承载目标续跑（Goal）、计划模式（Plan）、规格模式（Spec）与自定义智能体编排；对本项目"统一入口、长事务直接恢复当前阶段"的协作偏好尤其契合。
- **备注**：同第 4 条，属基线漏采补提。

### 6. TraeCode v3.3.92：支持 TRAE 移动端连接 TraeCode（基线漏采补提）

- **来源**：[TraeCode 更新日志 · 2026-08-20](https://docs.trae.cn/ide_changelog)（[连接 TRAE 移动端](https://docs.trae.cn/ide_connect-traecode-to-traework)）
- **能力说明**：TRAE 移动端 App 可连接桌面端 TraeCode。
- **适用场景与实用价值**：离开电脑后可在手机端查看任务进度、下发指令，实现跨设备任务不中断。
- **备注**：同第 4 条，属基线漏采补提。

### Hotfix 版本备查（无特性内容）

- **来源**：[TraeCode 更新日志](https://docs.trae.cn/ide_changelog) / [TRAE 企业版更新日志](https://docs.trae.cn/enterprise_release-notes)
- 2026-09-15 TraeCode v3.3.101、2026-09-11 v3.3.100、2026-09-04 v3.3.98，均仅"修复已知问题"，不计入特性条数。

### 国际版观察

- **来源**：[TraeCode 国际版更新日志](https://docs.trae.ai/ide/changelog)
- 国际版更新日志顶部仍停留在 2026-08-19（v3.5.89 ~ v3.5.91 Hotfix），本周无新增条目；国内现行更新页的版本节奏（v3.3.101）领先国际页，监测时继续两站并查。

## 二、文档新特性

### 1. 自定义设计系统支持全生命周期编辑管理

- **来源**：[TraeWork 设计系统文档](https://docs.trae.cn/solo_design-system)
- **能力说明**：文档明确自定义设计系统可进入独立管理界面，分四个页签编辑：
  - **主题**：颜色（Hex 直改/调色盘）、排版（字号/字重/行高/字体族，支持上传字体）、圆角、尺寸、间距等设计变量，支持"添加到对话"让 AI 调整或在右侧编辑器手动修改；
  - **组件**：查看主题与图形组合形成的可复用界面，可加入对话让 AI 调整；
  - **图形**：图标/SVG 管理，支持上传 .svg（可勾选"去色"）、重命名、删除；
  - **设计规范**：挂载纯 Markdown 的 README，以及包含 `SKILL.md` 的 zip/.skill 技能包或单独 .md 文件；
  - 支持对自定义设计系统重命名、创建副本、导出为 .zip、删除。
- **适用场景与实用价值**：设计系统从"一次性生成"升级为"可维护资产"，可做版本化导出与团队分发；设计规范中挂载 Skill 后，生成产物时可自动遵循该系统的落地规则，设计到实现的链路更收敛。
- **核验状态**：为官方文档现状的全页核验结果，该段内容的具体上线/变更日期官方未标注，**变更时间待核验**。

### 2. 官方文档路由修正：`ide_changelog` 为现行更新日志页

- **来源**：[TraeCode 更新日志（现行）](https://docs.trae.cn/ide_changelog)；对照旧路由 [docs.trae.cn/ide/changelog](https://docs.trae.cn/ide/changelog)
- **能力说明**：现行 TraeCode 更新日志规范页为下划线形式 `https://docs.trae.cn/ide_changelog`（面包屑"TraeCode/入门/更新日志"，更新至 2026-09-15）；斜杠形式旧路由页面标题为"TRAE CN"，条目停滞在 2026-06-09。官网统一更新日志页 [trae.cn/changelog](https://www.trae.cn/changelog) 与现行页内容一致，可作交叉验证。
- **适用场景与实用价值**：修正监测事实源，避免继续误判"国内站停滞"；引用官方更新时统一使用现行 URL。
- **核验状态**：双页直连比对 + 官网 changelog 交叉验证，已核实。

## 三、TraeWork 设计库

### 1. 内置设计系统全量清单核验：共 16 套

- **来源**：[TraeWork 设计系统文档](https://docs.trae.cn/solo_design-system)；TraeWork 更新日志 [work_changelog](https://docs.trae.cn/work_changelog)
- **能力说明**：TraeWork 更新日志本周无新条目（顶部仍为 2026-08-21 桌面版 v0.1.49 ~ v0.1.52）。经全页核验，内置设计系统共 **16 套**：TraeWork、TraeCode、Volcengine、TikTok、Doubao、Apple、Claude、Google、Vercel、Minimalist、21th、Motion Fit、Golden Time、Nerv、Barbie、Vibe Camp，每套均标注适用页面类型与场景。
- **适用场景与实用价值**：Design 模式选系统时有完整选型参照——中后台选 TraeWork/Volcengine、品牌官网选 Apple、阅读型产品选 Claude、数据看板选 Google/Minimalist、移动端内容流选 TikTok 等。
- **核验状态**：基线快照仅以"TRAE Work/豆包/Apple/Claude/Google/Vercel **等**"概括，本期为清单补全；对应同名 design skills（21th-design、barbie-design、motionfit-design、golden-time-design、nerv-design、vibecamp-design、minimal-dashboard-design）在基线时已存在，故判定 16 套均为旧有而非本周新增，**新增与否不可按日期独立核验，标注待核验**。

## 四、本地 skills·插件变化

### 1. Lark 官方插件升级：1.0.4 → 1.0.5

- **来源**：本地清单（`%USERPROFILE%\.trae-cn\plugins\trae-remote-official\lark\1.0.5`）
- **能力说明**：Lark 插件版本由 1.0.4 升级至 **1.0.5**（旧版本目录已替换）；connector 保持不变，飞书 27 个 lark-* skills 随插件提供。
- **适用场景与实用价值**：属于官方增量更新，建议在飞书文档/日历/Base 等高频场景中留意能力变化；具体 changelog 官方未随插件附带，**版本差异内容待核验**。

### 2. 会话新增技能：sovereign-rollout-cmd

- **来源**：本地清单（当前会话可用 skills 列表）
- **能力说明**：新增 **sovereign-rollout-cmd** 技能：面向 `.agents/`、`docs/` 等主权区落盘新资产（模板/规则/检查单/Skill/模式登记）场景，提供四阶段闭环——提案草案（零写入）→ 用户批准门 → 落盘执行 → 执行报告导出 + 验证。
- **适用场景与实用价值**：治理类资产变更获得"先提案、后批准、再落盘"的强制纪律，防止未授权写入主权区；与本项目治理规则下沉、保持主文档精简的偏好一致。
- **盘点旁证**：会话 skills 总数由 188（155 用户级 + 33 插件贡献）变为 **189（156 + 33）**；browser-bridge 0.2.0 独立插件与其余 11 个官方插件版本无变化；活跃 MCP 服务无变化（integrated_code_mode、mcp_plugin_Gitee_gitee，后者 23 个工具）。

---

## 采集与核验记录

- **成功源**：企业版更新日志、TraeCode 现行更新日志（ide_changelog）、国际版更新日志、TraeWork 更新日志、设计系统文档、官网 changelog（交叉验证）、本地 plugins 目录盘点。
- **采集失败**：TraeCode CLI 独立更新日志页——WebSearch 两次返回 system error 10000000；直连猜测地址 `https://docs.trae.cn/cli_changelog` 返回"页面不存在或已移动"。CLI 变更暂以企业版更新日志中覆盖 TraeCode CLI 的条目（如 09-15 DeepSeek-V4.1-Flash）为部分事实源，独立页面 URL 继续列为待核验。
- **基线待核验项销项**：企业级 Hook 与 Fork Chat 条目日期均核实为 **2026-06-29**（企业版更新日志全文）。
