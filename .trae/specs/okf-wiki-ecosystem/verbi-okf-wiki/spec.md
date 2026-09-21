# Verbi 出海案例 → OKF Wiki 转化 Spec

## 任务来源

- 用户指令：`Use Skill: seven-concepts-cmd 全面学习 https://mp.weixin.qq.com/s/ysCuzByxUUb7S27mTwuKIw，生成 okf wiki 教程`
- 方法论：seven-concepts-cmd（场景 4：知识沉淀 R→I→E→V→C）+ blog-article-to-okf-wiki 七阶段工作流
- 内容敏感度：**公开内容**（公开发布的微信公众号文章，无访问控制）→ 标准工作流

## 信源概况

| 项 | 值 |
|---|---|
| 标题 | 《一个人 5 个半月，月入 11 万美元》 |
| 公众号 | 冬枯木（栏目：出海案例） |
| 发布时间 | 2026-09-17 10:15（IP 属地：广东；年份页面未标注，按上下文为 2026 年） |
| 形态 | 微信图片消息（share image）：正文一段摘要 + 5 张 1080×1440 轮播长图 |
| 获取方式 | browser_use 提取 `#js_content` + 逐张原图转录 |

## 骨架判定（操作可复现性两问）

1. 博文中有无读者可照做的安装/配置/代码/调用/实测流程？→ **无**（技术栈仅以文本列举，无代码块、无步骤顺序）
2. 作者是否实测可复现？→ 不适用

**结论：不设 `examples/`**。骨架：index + concepts/（4 篇）+ references/（article-source + verification）+ log；description 标注「产品案例资讯，非操作教程」。

## 归属判定

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `jishu/ai/verbi/` | ✅ 采用 | 主线实体为 AI 应用 Verbi；同分组已有 aitokenbus/uumit-a2a-marketplace 等「产品/案例资讯」类直挂束先例；单篇博文不新建分组 |
| `sheke/industry/` | ❌ | 文章围绕具体 AI 产品展开，非行业趋势分析 |
| 新建分组 | ❌ | 违反「单篇博文禁止新建分组」与最小变更 |

## 三层知识拆分（商业案例资讯类）

| 层级 | 篇目 | 内容 |
|---|---|---|
| 事件事实层（What/When/Who） | concepts/00-product.md | 产品形态、9 语言、四技能、双端/Web、上线日期、创始人、技术栈 |
| 账本核验层（How much） | concepts/01-revenue-ledger.md | RevenueCat 六项数字、X 一手 RevenueCat 截图时间线、数字勾稽 |
| 定位增长层（Why/How） | concepts/02-positioning-growth.md | 「敢开口」错位定位、ASO/TikTok/UGC 渠道勘误、付费转化 |
| 模式趋势层（So what） | concepts/03-business-pattern.md | 单人窄赛道现金流模式、可迁移性、风险边界 |

## 质量门记录

- G1（事实无因果词）：facts.md 按 F 编号客观登记，作者观点显式标注（F-018/F-020）✅
- P0 核验：15 项声明逐项过勘误四张清单，详见 bundle `references/verification.md`
- G3（信源先行）：生成顺序 references → concepts → 各级 index ✅
- G4（V 阶段机械门禁）：双份 F 编号核对、toctree、相对链接、计数同步，见 review.md
