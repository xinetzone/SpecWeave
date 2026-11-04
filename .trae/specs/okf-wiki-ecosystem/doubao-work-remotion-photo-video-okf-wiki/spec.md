---
type: spec
title: 豆包工作与 Remotion 照片视频制作 OKF Wiki
status: completed
date: 2026-11-04
methodology: seven-concepts-cmd
content-sensitivity: public
source: https://mp.weixin.qq.com/s/P0ImKmk9glQLYipu0iLhZg
---

# 豆包工作与 Remotion 照片视频制作 OKF Wiki

## 概述

将公众号“前端之神”的《豆包工作+剪辑Skills！人人都是视频大师！》转成中文原创教程。读者是希望把照片做成视频、并理解 Agent 与程序化渲染分工的初学者。教程区分文章实测、官方能力、执行者建议及尚未核验的信息，不照搬推广结论。

目标目录为 `projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/doubao-work-remotion-photo-video/`。子项目自治规范允许公开知识包写入 `doc/bundles/`；已读取根、projects 与子项目三级 AGENTS。

## 目标与非目标

- 目标：覆盖工具分工、安装前置条件、照片整理、分镜与静帧审核、渲染与配乐、迭代及交付边界。
- 目标：保留连续编号事实、来源与核验台账、三条四元组洞察、包内单案例候选模式及独立审查证据。
- 非目标：安装豆包、Node.js 或 Remotion，修改客户端、运行素材渲染、领取权益、购买服务或发布视频。
- 非目标：复制公众号全文、镜像原始 HTML、公开个人照片、登记独立模式或 Skill。
- 非目标：未经另行授权执行 Git 提交、推送或改变子模块指针。

## 已采集背景

采集日期为 2026-11-04。微信正文可匿名读取；公众号为“前端之神”，作者为“林三心不学挖掘机”，页面标注原创及发布时间 2026-10-30 08:35，未显示时区。

正文三个章节为“一句话装好 Remotion”“照片做成短片”“写在最后”。作者记录本地执行环境、安装技能、桌面照片文件夹、30 秒摩托短片、先看静帧再确认渲染、10 张静帧、1080p 视频和后续补配乐。

安装截图中的提示词已读到：“安装 github 上 remotion-dev 的 remotion 和 remotion-dev 的 skills”。这是源文输入，不能当成官方安装命令。其余配图因浏览器连续超时未完成核对，视频未播放；正文只有“用 Remotion”等片段，不具备完整视频提示词逐字记录。

官方资料已获得：

| 来源 | 已读内容 | 使用边界 |
| --- | --- | --- |
| [Agent Skills](https://www.remotion.dev/docs/ai/skills) | 官方技能目录与安装入口，页面标注 2026-11-01 更新；13 个标题包括一个聚合入口和 12 个专项技能 | 恢复后回读纠正初次计数；不反推作者安装时的精确版本 |
| [Coding Agents](https://www.remotion.dev/docs/ai/coding-agents) | 编码 Agent、Node.js 前置条件、新建项目、技能安装和预览 | 官方通用路径，不代表豆包客户端已实测 |
| [静帧 CLI](https://www.remotion.dev/docs/cli/still) | 静帧渲染及 `--frame`；Windows 的 props 推荐文件输入 | 关键段落已读取，按需补核具体命令参数 |
| [渲染 CLI](https://www.remotion.dev/docs/cli/render) | 视频/音频渲染、宽高、fps、duration 参数 | 关键段落已读取；禁止填入未经核对的示例参数 |
| [许可入口](https://www.remotion.dev/license) | 返回 Remotion 仓库 LICENSE：个人、最多 3 名员工的营利组织等免费许可资格，其他主体可能需公司许可 | 许可条款需与最新版官网复核；不称 MIT 或无条件免费 |
| [豆包下载页](https://www.doubao.com/download/desktop) | 搜索命中官方页面“新用户领30天免费体验套餐”；直接抓取仅得标题 | 仅搜索摘要支持，未核对完整领取规则，不写永久福利 |

仍待核验：作者称约 6.1 万 Star 的历史时点、自动画面质检的官方产品契约、老用户签到额度规则、完整图片内提示词。不同采集时点的 Star 数不用于证伪历史数字。

## 归属与骨架

| 候选 | 判定 | 理由 |
| --- | --- | --- |
| `jishu/ai/frameworks/ai-agent/` | 选定 | 已有豆包工作三篇主题包与 Agent 视频制作专题，可形成互链 |
| `jishu/ai/products/` | 不选 | 可容纳产品，但拆散已有豆包主题簇 |
| `jishu/viz/` | 不选 | 本次主线是 Agent 制作流程，不是渲染框架源码精读 |
| 新分组 | 不选 | 单篇文章不新增分组 |

原文有操作顺序和案例输出，但缺客户端、项目及依赖版本，部分关键步骤藏在未读配图内。因此当前两问判定为“有操作流程；精确复现证据不足”。默认不建 `examples/`，把原创需求提示模板放在概念教程中，并明确“建议模板、非原文逐字记录、未在豆包实测”。若补采后能满足两问，再经范围对齐决定是否增加 examples。

## 功能需求

- FR-1：先登记 source-manifest 与事实，事实编号 F-001 起连续；区分 page_fact、author_claim、official_fact。
- FR-2：P0 核验涵盖日期、数量、许可、套餐、官方能力；四张清单记录日期版本、成效溯源、口径对照、引文核对，不适用项说明理由。
- FR-3：教程按读者任务组织，不按原文段落或官网目录照搬；每项具体能力引用 F 编号及来源。
- FR-4：知识地图包含事实、机制、迁移三层；机制推断与单案例模式不能标成产品保证或普遍结论。
- FR-5：正文说明素材授权、照片隐私、本地执行与云端模型处理的区别、音乐授权、静帧不能检验全片时序与声音，以及代码渲染不保证审美。
- FR-6：按 OKF v0.2 编写根索引、子索引、概念页、信源页与 log，更新分组及上层必要计数和导航，保留其他会话变更。
- FR-7：与既有豆包工作主题包说明分工并互链；不修改其历史事实、核验与执行日志。

## 约束与假设

- 内容级别：公开；不绕过登录、验证码或访问控制。
- 正文中文、文件名 kebab-case、相对链接；非保留 Markdown 文件含可解析 frontmatter 和非空 type。
- sources 使用 resource 键；记录 status、stale_after、generated，核验事件只写实际执行的验证。
- 当前状态先为 draft；核心产品主张无法核验时使用 flagged 并限定影响范围，不因检索无结果断言产品没有该能力。
- 已有并行变更涉及总索引、AI/技术域索引及其他新包。写共享文件前重新读取并做最小增量，不回滚已有变更。
- 未获得三独立信源的核心断言保持单源或官方口径，不为了凑数量收录互相转载的文章。
- 本次不新增自制图片、视频或运行脚本资产。

## 验收标准

### AC-1 来源与事实
- **Type**: `rule`
- **Given**: 公开文章、官方资料和已知采集缺口。
- **When**: 编写事实与来源台账。
- **Then**: 至少 20 条实质可溯源事实；F 编号连续且双份集合相等；作者观点与官方事实分离；图片未读取项和视频未播放项有记录。
- **Pass Condition**: 来源键、定位、状态齐备，无猜测配图内容或全文镜像。
- **Evidence**: facts.md、references/article-source.md、source-manifest.md 与集合比对结果。

### AC-2 核验与边界
- **Type**: `rule`
- **Given**: 文章包含数量、福利、自动质检及开源免费描述。
- **When**: 核验并编写教程。
- **Then**: 每项 P0 有证据或明确未核验标记；官方许可、时点、隐私及音乐边界落入正文；未实测不标为实测通过。
- **Pass Condition**: 核验台账与正文没有互相矛盾的结论；核心失败项有 flagged 提示。
- **Evidence**: verification.md、概念正文与来源回验。

### AC-3 教程学习质量
- **Type**: `rubric`
- **Dimension**: 初学者理解工具分工、学习顺序和验收方式。
- **Scale**: 1-5
- **Anchors**: 1 = 改写宣传且无学习路径；3 = 分层清楚但步骤或边界不足；5 = 读者能写出有素材、分镜、静帧审核、声音及交付要求的创作需求，并辨认未验证项。
- **Pass Threshold**: >= 4
- **Evidence**: 概念页、知识地图及独立审查评分。

### AC-4 方法论与独立审查
- **Type**: `rule`
- **Given**: 七概念知识沉淀场景。
- **When**: R→I→E→V 完成。
- **Then**: 三条洞察含现象、根因假说、影响、建议及事实证据；包内模式含边界、步骤、反模式、检验标准与标为推演的跨域迁移；四视角至少五条具体意见有裁定和回验。
- **Pass Condition**: 不将单案例推演标为跨案例实测；独立审查无遗留可行动发现。
- **Evidence**: knowledge-map.md、模式页、adversarial-review.md、review.md 和 CMD-LOG。

### AC-5 格式导航与变更隔离
- **Type**: `rule`
- **Given**: 存在并行在途知识包。
- **When**: 接入导航并验证。
- **Then**: 新包 UTF-8、frontmatter、文件名、链接、toctree 完整；必要计数与现盘实际目录一致；既有无关变更保留。
- **Pass Condition**: 项目门禁实际执行并记录结果；存量失败与本次回归分开，不宣称未运行门禁通过。
- **Evidence**: 命令输出、路径限定 diff/status、索引计数核对。

## 批准状态

规格与任务预览已由 NotifyUser 获得用户批准。进入实施；未安装或渲染，未提交或推送。初次技能总数陈述已在恢复时按官方原文纠正，验收范围不变。

## 完成记录

四项实施任务已完成。最终独立Review R3为pass，全部AC/TR通过，新人评分4/5，无遗留可行动发现。R1/R2阻塞及解除证据保留于review.md；教程包继续flagged、候选模式继续L1-draft，未实测安装或媒体，不提交或推送。

```text
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START | session=sc-20261104-doubao-remotion-photo-video | msg=公开文章知识沉淀启动 | ctx={"scenario":"knowledge","depth":"deep"}
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S2 | event=CHAIN_SELECTED | session=sc-20261104-doubao-remotion-photo-video | msg=选择R-I-E-V，C等待另行提交授权 | ctx={"commit":false,"approval":"pending"}
```
