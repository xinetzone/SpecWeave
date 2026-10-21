---
type: Research-Facts
id: "vibeknow-video-expert-20261021-facts-product-features"
topic: vibeknow-product-features
report: retrospective-vibeknow-video-expert-20261021
appendix: B
collected_date: 2026-10-21
security_level: public
source: "公开信源（vibeknow.com 中文站首页/定价页/教程站、vibeknow.ai 英文站、github.com/vibeknow/cli 仓库文档、npm vibeknow-cli 包页、第三方实测文章与第三方中文评测）；本文件为 VibeKnow 视频专家全面调研报告（session=sc-20261021-vibeknow-research）R 阶段产品功能维度事实附录，条目编号与正文引用一致"
---

# VibeKnow 产品功能 · 客观事实清单

采集日期：2026-10-21。本清单仅陈述可验证的公开事实，不含因果与判断。来源优先级：官方页面 > 官方 CLI 仓库文档 > 第三方实测。

## A. 输入能力与内容规格

| 编号 | 事实 | 来源URL | 访问日期 |
|---|---|---|---|
| PRO-01 | 中文站上传区标注支持 PDF、DOC、PPT、TXT、MD 文件及网页/公众号链接；教程页另列出 Word(.docx/.doc)、PDF（扫描版自动 OCR）、PPT(.pptx/.ppt)、TXT 与直接粘贴文字；英文站输入类型含 Document、PDF、Word、PPT、URL、Notion、Markdown、Blog、TXT、Ebook。 | https://vibeknow.com/ ; https://vibeknow.com/learn/document-to-video ; https://vibeknow.ai/ | 2026-10-21 |
| PRO-02 | 定价页权益对比表四个档位（免费体验/基础/专业/大师）的「输入能力」一行均为「50M 以内文档 / URL 链接」。 | https://vibeknow.com/pricing | 2026-10-21 |
| PRO-03 | 文档转视频页按文档字数给出成片时长区间：500–1500 字→1–2 分钟，2000–5000 字→3–5 分钟，5000–15000 字→5–10 分钟，15000 字以上需自行按章节拆分（自动拆集标注为未来功能）；同页推荐文档长度为 800–5000 字。 | https://vibeknow.com/learn/document-to-video | 2026-10-21 |
| PRO-04 | 文档转视频页按格式分派解析策略：PDF 判断文字版/扫描版并自动 OCR，Word 按段落结构自动分镜，PPT 优先使用备注讲稿，网页链接抓取正文并忽略广告/评论/导航；同页记载整个制作过程 3–8 分钟、镜头数一般 10–30 个。 | https://vibeknow.com/learn/document-to-video | 2026-10-21 |
| PRO-05 | PPT 转视频页写「建议 10–60 页之间」；第三方中文评测记为「官方建议单次不超过 50 页」；前端 i18n 词典存在 PDF 页数超限（错误码 1208）与 PPT 页数超限（错误码 1209）两条提示。 | https://vibeknow.com/learn/ppt-to-video ; https://www.aihub.cn/tools/vibeknow/ ; https://vibeknow.com/ | 2026-10-21 |

## B. 模式矩阵与生成引擎

| 编号 | 事实 | 来源URL | 访问日期 |
|---|---|---|---|
| PRO-06 | 中文站 /learn 目录列出 7 个功能介绍页：灵活创作（画面可编辑、动态 PPT 效果，出片后可逐页改画面）、PPT 讲解（逐页自动配音讲解，备注可作讲稿）、图解视频（AI 为每一页画画面，页数即画面张数）、手绘动画（图片矢量化后逐笔绘制，不带数字人）、原文讲解（AI 一字不改照原稿讲）、系列视频（项目空间内连续出片、自动编号、整系列分享）。 | https://vibeknow.com/learn/ 及各子页 | 2026-10-21 |
| PRO-07 | 官方 CLI 文档列出 4 种 pipeline 模式：default（不传 `--mode`，由文档生成视频）、replica（PPT/PDF 逐页还原）、image（每页旁白配一张 AI 生成插图，`--pages N` 设置页数）、handdraw（手绘动画，走「插图→矢量化」独立图）。 | https://github.com/vibeknow/cli/blob/HEAD/AGENTS.md | 2026-10-21 |
| PRO-08 | 官方 CLI 存在两套生成引擎：`--engine pipeline`（v=3 图式流水线，默认，支持全部模式）与 `--engine agent`（v=2 agent 驱动，不支持 replica/image/handdraw）；`--script-lock` 用文档原文逐字作旁白，可叠加在任意模式上。 | https://github.com/vibeknow/cli/blob/HEAD/AGENTS.md | 2026-10-21 |
| PRO-09 | 官网 FAQ 将自动完成环节列为脚本拆解、分镜设计、画面生成、配音、背景音乐（首页三步流程另列「精剪」）；官方 CLI 的 SSE 进度流为 4 阶段：outline（大纲）→ tts（配音）→ render（渲染）→ publish（发布）。 | https://vibeknow.com/ ; https://www.npmjs.com/package/vibeknow-cli | 2026-10-21 |
| PRO-10 | 官网首页标注 16:9 与 9:16 两种画幅一键切换；官方 CLI 的 `--aspect` 接受 `horizontal\|vertical` 或 `16:9`/`9:16` 两种写法；PPT 转视频页写母版与配色保留并由 AI 适配视频画面比例。 | https://vibeknow.com/ ; https://github.com/vibeknow/cli/blob/HEAD/AGENTS.md ; https://vibeknow.com/learn/ppt-to-video | 2026-10-21 |

## C. 交付形态与可编辑性

| 编号 | 事实 | 来源URL | 访问日期 |
|---|---|---|---|
| PRO-11 | 交付形态为两阶段：官方 CLI 定义 Preview（`vk create` 产出 `share_url` 分享页，可直接在浏览器播放成片）与 Export（可选的 `vk video export`，渲染可下载 MP4，需数分钟并额外消耗积分）；导出文件为 `.mp4`；官网首页三步流程写「大约 3 分钟完成。先预览，满意再导出」。 | https://github.com/vibeknow/cli/blob/HEAD/AGENTS.md ; https://vibeknow.com/learn/quick-start ; https://vibeknow.com/ | 2026-10-21 |
| PRO-12 | 脚本编辑：视频编辑页「脚本」面板可改字、删段、调序，支持手动添加分镜与修改段落语气，改完点「重新生成」同步更新画面与配音，次数无限制；多音字支持 1–4 声与轻声的完整拼音标注，标注后整段重新生成配音，常用多音字可存入词典。 | https://vibeknow.com/learn/edit-script ; https://vibeknow.com/learn/polyphone | 2026-10-21 |
| PRO-13 | 素材与字幕编辑：可对单帧「换背景」（上传/素材库/AI 生成，支持 jpg/png 与 mp4，替换后其他元素位置自动适配，可批量应用到多帧）与「换图片」（本地图片/Unsplash/AI 重新生成，替换后自动适配原位置与尺寸）；字幕面板可全片开关并按段落单独控制显隐；字幕样式编辑器含位置（靠上/居中/靠下、距底部 X%）、动画（无/左滑入/上滑回弹/轻旋入/逐字色扫）、字号、字色、底色、描边、描边宽度，并可「存为字幕模版」；应用内文案记录字幕样式编辑仅在灵活创作、图解、手绘等模式支持。 | https://vibeknow.com/learn/change-background.html ; https://vibeknow.com/learn/change-image.html ; https://vibeknow.com/learn/subtitle-toggle ; https://vibeknow.com/ | 2026-10-21 |
| PRO-14 | 官方 CLI 的 `vk video avatar-retry` 仅重新生成失败的数字人页，不重跑整个任务、不额外扣积分；`vk video edit --scene N --script "..."` 只替换一幕讲稿并重生成该幕，加 `--script-only` 只重生配音，该操作不可撤销，重新导出前 `vk video download` 返回旧讲稿版本。 | https://github.com/vibeknow/cli/blob/HEAD/README.zh.md | 2026-10-21 |

## D. 数字人与声音

| 编号 | 事实 | 来源URL | 访问日期 |
|---|---|---|---|
| PRO-15 | 官方 CLI 的 `--avatar` 接受 `sys_<id>`（公共模）与 `ua_<id>`（用户训练的专属数字人）两类 ID，支持 `--avatar-position bottom-right` 与 `--avatar-size 300`；`--mode handdraw` 与 `--engine agent` 下不可用数字人；第三方实测文章记数字人在编辑台为可拖拽图层，位置可拖、大小可拉，默认每页落固定比例方框、形象按比例缩在框内不拉伸变形，一页调好后可一次性应用到全部页。 | https://github.com/vibeknow/cli/blob/HEAD/README.zh.md ; https://cloud.tencent.com/developer/article/2761670 | 2026-10-21 |
| PRO-16 | 定价页权益对比表：专属数字人额度为基础 1 位、专业 3 位、大师 5 位（均为「全风格」）；公共数字人免费体验档部分开放、三档付费全部解锁。 | https://vibeknow.com/pricing | 2026-10-21 |
| PRO-17 | 应用内文案记录数字人克隆流程为「第一步：选择风格」（3D 质感 / 2D 手绘）、「第二步：选择声音生成 demo」，图片支持 PNG、JPG、WEBP，训练完成状态为「待激活」，激活后方可在视频创作中使用；`/preview/digital-avatar` 页面（标注「即将上线」）写 30 秒克隆老师分身、10 分钟生成一讲课程，并写「自然口型」。 | https://vibeknow.com/ ; https://vibeknow.com/preview/digital-avatar | 2026-10-21 |
| PRO-18 | 声音克隆入口在「声音」设置页的「克隆我的声音」，需录制 30 秒清晰朗读样本或上传音频，AI 几分钟内完成克隆，支持中英文混合与不同情绪；应用内声音资产管理区分「我的声音」与「公共声音」。 | https://vibeknow.com/learn/voice-clone.html ; https://vibeknow.com/ | 2026-10-21 |
| PRO-19 | 定价页权益对比表：专属声音克隆为「首次订阅赠 1 次免费克隆 · 90 天内有效 · 价值 857 积分」；用积分克隆声音免费档 857 积分/个、会员 686 积分/个（8 折、不限数量）；每月免费克隆次数为基础 1 次（价值 857 积分）、专业 3 次（2,571 积分）、大师 5 次（4,285 积分），免费次数用完后会员专享 59 积分/次（原价 857 积分）。 | https://vibeknow.com/pricing | 2026-10-21 |

## E. 模板、风格与资产

| 编号 | 事实 | 来源URL | 访问日期 |
|---|---|---|---|
| PRO-20 | 官网首页标注「100+ 模板」；英文站标注 100+ templates、Speak 8+ languages natively，并引用第三方评测称 40+ 音色；定价页「创作风格 / 图解视频风格」免费体验档为「基础模板」、三档付费均为「全套风格 + 自定义」。 | https://vibeknow.com/ ; https://vibeknow.ai/ ; https://vibeknow.com/pricing | 2026-10-21 |
| PRO-21 | 应用内「创作资产」模块含数字人、系列封面、灵活创作风格、图解视频风格、声音、Logo 标识、连接器；自定义主题可配置配色（背景色/卡片底色/主文字/次要文字/强调色/卡片填充/描边色）、字体（标题字体/正文字体）、面板样式（圆角/透明度/描边粗细）与背景（抽象色场/背景效果）；图解视频风格分「IP 形象」与「视觉主题」两个子标签，训练图片需短边≥128px、宽高比在 1:3~3:1 之间、仅支持 PNG/JPG/WEBP。 | https://vibeknow.com/ | 2026-10-21 |
| PRO-22 | 定价页权益对比表「视频水印」一行：免费体验档为「带水印」，基础/专业/大师三档均为「无水印」；应用内「水印设置」为会员功能，支持文字与图片两种水印模式，可设颜色、大小、排版（居中/铺满）、密集度、倾斜角度，并可对新生成视频自动加水印。 | https://vibeknow.com/pricing ; https://vibeknow.com/ | 2026-10-21 |
| PRO-23 | 第三方中文评测记导出为 1080p MP4，基础会员画质区间标注为 1080p–4K；官网中文定价页权益表未列出分辨率项，英文定价页对 Plus 档仅写「Higher export quality」。 | https://www.aihub.cn/tools/vibeknow/ ; https://vibeknow.com/pricing ; https://vibeknow.ai/pricing | 2026-10-21 |

## F. 批量、团队与 API

| 编号 | 事实 | 来源URL | 访问日期 |
|---|---|---|---|
| PRO-24 | 定价页「视频并行任务数」为免费 1、基础 5、专业 50、大师不限制（批量生产）；定价页设「团队版」入口，应用内文案为「团队版敬请期待」与「扫码联系产品负责人，获取专属方案」；自媒体批量页记载会员可在多个浏览器标签页并行开工、建议开 3–5 个标签页、5 分钟启动 5 条视频，同页写「还没开放批量 API」（页面标注 2026-04-18）；系列项目制作台标注「一讲做完再开始下一讲，积分逐讲扣」。 | https://vibeknow.com/pricing ; https://vibeknow.com/learn/batch-video-for-creators ; https://vibeknow.com/ | 2026-10-21 |
| PRO-25 | 官网中英文 FAQ 均写提供 API 接入，联系邮箱 sales@vibeknow.com；应用设置含「API 密钥」标签页，密钥表字段为名称、密钥前缀、状态（生效中/已停用）、最近使用、创建时间，团队空间下密钥属团队、调用消耗团队积分、团队管理员均可管理；官方 CLI 提供 `vibeknow api call --service <service> --method GET\|POST --path /v1/<resource>` 原始接口调用；定价页「服务」一栏三档付费均为电子发票，支持服务为社区教程/在线客服/在线客服/优先客服。 | https://vibeknow.com/ ; https://vibeknow.com/pricing ; https://github.com/vibeknow/cli/blob/HEAD/README.zh.md | 2026-10-21 |
