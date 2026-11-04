---
type: Reference
title: 豆包工作 Remotion 事实基准
source: https://mp.weixin.qq.com/s/P0ImKmk9glQLYipu0iLhZg
status: flagged
---

# 事实基准

36 条事实，F-001 至 F-036。表行与正式包的 article-source.md 逐行比对；来源键定义以正式包 source-manifest.md 为准。`verified-doc` 是文档核验，不是运行验证。

| F | claim | type | source_id | locator | status |
| --- | --- | --- | --- | --- | --- |
| F-001 | 文章标题为《豆包工作+剪辑Skills！人人都是视频大师！》。 | page_fact | article | 页头标题 | page-observed |
| F-002 | 页面公众号名为前端之神，作者为林三心不学挖掘机，标有原创。 | page_fact | article | 页头署名 | page-observed |
| F-003 | 页面发布时间为 2026-10-30 08:35，未显示时区。 | page_fact | article | 页头日期 | page-observed |
| F-004 | 正文三节为一句话装好 Remotion、照片做成短片、写在最后。 | page_fact | article | 章节标题 | page-observed |
| F-005 | 页面首尾各有一个显示 00:30 的视频；本次未播放。 | page_fact | article | 首尾视频控件 | page-observed |
| F-006 | 作者列举导入照片、转场、配乐和字幕等手工剪辑环节。 | author_claim | article | 开篇问题 | single-source |
| F-007 | 作者推荐豆包工作结合 Remotion，把照片文件夹和自然语言需求交给 Agent。 | author_claim | article | 开篇推荐 | single-source |
| F-008 | 作者称 Remotion GitHub Star 约 6.1 万。 | author_claim | article | 开篇框架介绍 | unverified-historical |
| F-009 | 作者要求新建工作任务并选择本地电脑执行环境。 | author_claim | article | 第 1 节正文 | single-source |
| F-010 | 第 1 张安装截图输入为“安装 github 上 remotion-dev 的 remotion 和 remotion-dev 的 skills”。 | page_fact | article | 第 1 张安装截图 | page-observed |
| F-011 | 作者称一条指令配齐依赖与 12 个技能，涵盖渲染、动画、字幕、音频。 | author_claim | article | 第 1 节结果叙述 | unverified-install |
| F-012 | 作者称可以从更多技能选择，也可以在需求中写“用 Remotion”。 | author_claim | article | 第 1 节末尾 | single-source |
| F-013 | 作者使用广州周边摩托跑山照片，并把照片放入桌面文件夹。 | author_claim | article | 第 2 节素材叙述 | single-source |
| F-014 | 作者要求把照片拼成一条 30 秒摩托短片。 | author_claim | article | 第 2 节需求叙述 | single-source |
| F-015 | 作者要求每个镜头先出静帧，确认后再渲染。 | author_claim | article | 第 2 节审核顺序 | single-source |
| F-016 | 作者称左侧工作进度展示任务拆解。 | author_claim | article | 第 2 节进度叙述 | single-source |
| F-017 | 作者称 Agent 自动做画面质检并修改。 | author_claim | article | 第 2 节质检叙述 | unverified-product-contract |
| F-018 | 作者称得到 10 张静帧，内容分为开场、中段、结尾。 | author_claim | article | 第 2 节预览结果 | single-source |
| F-019 | 作者称确认后得到 1080p、30 秒视频。 | author_claim | article | 第 2 节渲染结果 | unverified-media |
| F-020 | 作者称初版无配乐，追加需求后补入音乐。 | author_claim | article | 第 2 节声音迭代 | single-source |
| F-021 | 作者列出年终骑行、赛道日、女骑合集和车友婚礼等应用设想。 | author_claim | article | 第 3 节场景列举 | single-source |
| F-022 | 作者宣传新用户 30 天免费体验及老用户签到额度，未提供额度数值。 | author_claim | article | 第 3 节福利推广 | unverified-terms |
| F-023 | 官方 Agent Skills 页提供 npx skills add remotion-dev/skills 安装入口。 | official_fact | skills | 安装命令 | verified-doc |
| F-024 | 官方页面有 13 个技能标题：一个 remotion-best-practices 聚合入口与 12 个专项技能。 | official_fact | skills | Available skills 全部标题 | verified-doc |
| F-025 | 官方专项技能分别涉及创建、React markup、Studio、渲染、地图、字幕、SaaS、交互、文档、许可、升级和多媒体。 | official_fact | skills | Available skills 职责描述 | verified-doc |
| F-026 | 官方 Coding Agents 页要求编码 Agent 和 Node.js，并提示多数编码 Agent 需要付费订阅。 | official_fact | coding | 前置条件 | verified-doc |
| F-027 | 官方创建流程给出 npx create-video --yes --blank my-video、新项目内 npx remotion skills add 和 npm run dev。 | official_fact | coding | 新建项目及预览 | verified-doc |
| F-028 | 官方 still CLI 语法为 npx remotion still <serve-url或entry-point> [composition-id] [output-location]，支持静帧。 | official_fact | still | 命令首段 | verified-doc |
| F-029 | still 的 --frame 默认 0；文档允许负帧索引，-1 表示最后一帧。 | official_fact | still | --frame | verified-doc |
| F-030 | 官方 render CLI 语法为 npx remotion render <entry-point或serve-url> <composition-id> <output-location>，用于视频或音频渲染。 | official_fact | render | 命令首段 | verified-doc |
| F-031 | render 文档提供 --width、--height、--fps 和 --duration；duration 单位为帧。 | official_fact | render | 对应选项段落 | verified-doc |
| F-032 | still/render 的 --props 文档提醒 Windows 内联 JSON 引号问题并建议使用 JSON 文件。 | official_fact | still,render | --props | verified-doc |
| F-033 | Remotion 免费许可资格包括个人、最多 3 名员工的营利组织、非营利组织及非商业评估；不符合资格者需公司许可。 | official_fact | license | Free License/Company License | verified-doc |
| F-034 | 许可限制以销售、出租或重新许可 Remotion 衍生软件为目的的复制修改；该许可不是无条件免费许可。 | official_fact | license | 许可条件 | verified-doc |
| F-035 | 公司许可页区分 Creators 的低量手工创作与 Automators 的程序化应用，并把 AI agents/Studio 列入 Creators 场景。 | official_fact | company-license | Creators/Automators | verified-doc |
| F-036 | Agent Skills 与 Coding Agents 页面均标注最后更新于 2026-11-01。 | official_fact | skills,coding | 页尾 Last updated | verified-doc |
