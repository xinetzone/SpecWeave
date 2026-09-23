---
source: .trae/specs/create-zhihu-monetization-okf-wiki/{facts.md,verification.md,decision-log.md}
created_at: 2026-09-23
task: Task 5（I-b · 三层知识拆分设计）
status: designed
---

# Knowledge Map — 知乎变现体系 bundle 三层拆分设计

> 目标 bundle：`projects/awesome-okf-xs/doc/bundles/sheke/industry/zhihu-monetization/`
> 骨架：无 examples/（Task 4 判定）；结构 = `references/` + `concepts/` + `index.md` + `log.md`
> concepts 命名范式对齐同簇 `ai-monetization`：`NN-kebab-case.md` + 内容导航表 + toctree（含 log）

## 1. 篇目规划（三层）

### 事实层（信源自述，全部声明挂 F 编号；单源项标「仅平台活动页单源」）

| 篇目 | 职责 | F 编号映射 |
|---|---|---|
| `concepts/00-overview.md` | bundle 总览：三信源定位（项目广场/打卡挑战赛/科学季）、bundle 地图与阅读路径、时效声明（stale_after ≤ 2026-12-31）与 flagged 状态明示 | F-001, F-028, F-044（结构锚定）；全局时效声明引 verification.md |
| `concepts/01-project-square-facts.md` | S1 事实层：AI Works 项目广场——页面框架、分类/标签体系、最热 18 项目逐条、热门榜与科学季分类项目 | F-001~F-026；F-027 科学季 7 项目 |
| `concepts/02-checkin-campaign-facts.md` | S2 事实层：创作打卡挑战赛第五十三期——四 Tab 规则全量（打卡/回答/想法/彩蛋）、奖池结构、参与门槛、话题领域 | F-028~F-043；版本差异旁证 F-067；复盘佐证 F-066 |
| `concepts/03-science-season-facts.md` | S3 事实层：科学季 2026——三计划（提问/科普/观察）、六圈子、影像漂流、时间表、合作伙伴 | F-044~F-054；官方补充 F-055~F-058 |

### 机制层（Why；因果解释显式标注「洞察/推断」，现象锚 F 编号）

| 篇目 | 职责 | F 编号映射 |
|---|---|---|
| `concepts/04-yuli-incentive-structure.md` | 盐粒激励结构：瓜分机制、奖池分层、兑换口径（100:1）与提现、历史口径分离 | F-029, F-031, F-036, F-039, F-041, F-046, F-047, F-048, F-059, F-060；防混用 F-056/F-058 |
| `concepts/05-participation-gates-and-cost.md` | 参与门槛与时间成本：报名关系、字数门槛、互动五选三结构、每日任务拆解、零门槛表述的证据层级 | F-032, F-033, F-034, F-043, F-063；规则变动 F-067 |
| `concepts/06-mechanism-insights.md` | 机制洞察五元组（现象+根因+影响+建议，全部标注洞察非事实） | 见第 2 节 |

### 路径层（设计产物，非信源复现；收益区间仅挂 F 或标「待验证」）

| 篇目 | 职责 | F 编号映射 |
|---|---|---|
| `concepts/07-monetization-path-matrix.md` | 角色化路径矩阵（≥3 类角色 × 子路径）：AI/技术创作者、专业领域科普者、泛流量日更者；每角色起点/门槛/行动/收益区间/退出条件 | 收益锚 F-029/F-031/F-036/F-039/F-041/F-046/F-047/F-048/F-059 |
| `concepts/08-ai-creator-main-path.md` | AI/技术内容创作者主路径详解（起点条件 → 准入门槛 → 第 1 周/第 1 月/持续期 → 收益区间 → 退出/切换条件）；与 Task 7 设计稿一致，总览级呈现（详细版在 docs/） | 同上 + F-044/F-055 时间窗 + F-001~F-027 项目广场资产轨 |
| `concepts/09-risks-and-boundaries.md` | 风险与边界：单源声明清单、规则按期变动（F-067）、时间窗错失、口径冲突（F-065）、收益不确定性、AI 协作排除条款的合规边界 | F-065, F-067；verification.md 单源清单 |

### references/ 与索引

| 文件 | 职责 |
|---|---|
| `references/article-source.md` | 三信源事实清单 F-001~F-067——与 spec 区 facts.md **双份登记，编号集合逐字一致**（TR-6.3） |
| `references/verification.md` | 核验报告（spec 区 verification.md 的结构化精简版：结论表 + 勘误四清单 + flagged 判定 + 单源清单 + 证据 URL 清单） |
| `index.md` | bundle 根索引：frontmatter（okf_version/type/title/description + status: flagged + stale_after）+ 内容导航 + 主题关联（同簇互链）+ toctree |
| `log.md` | bundle 日志：骨架判定、归属理由、时效声明、双份一致性核对记录、手动等效验证记录（若 Task 9 需要） |

## 2. 洞察四元组（concepts/06 主体，G2）

> 以下均为**洞察/推断**（非事实），现象锚 F 编号，根因/影响/建议为分析性判断。

**洞察 1 · 盐粒激励的时间结构**
- 现象（F-029, F-031）：周打卡满 1 天即可瓜分（100 万盐粒档），全勤 28 天奖励翻倍，周期按周切分
- 根因（洞察）：低门槛进入（1 天）+ 连续性溢价（28 天翻倍）→ 平台以「易启动 + 难坚持」结构换日活留存
- 影响（预期推断）：当期中断则连续性重计、时间投入沉没；逐日任务的实际约束是「连续性」而非「质量」
- 建议：将打卡嵌入固定作息（固定时段完成 1 创作 + 3 互动），连续性优先于单日质量

**洞察 2 · 多层奖池的叠加结构**
- 现象（F-029, F-036, F-039, F-041）：基础瓜分 + 回答任务 300 万 + 想法任务 100 万 + 彩蛋无上限，「多发多得」
- 根因（洞察）：分层覆盖不同创作意愿与边际成本——想法（≥20 字 + ≥1 图）与回答（≥100 字）单位时间成本差约 5 倍，同池瓜分下单位时间收益倾向想法层
- 影响（预期推断）：纯盐粒导向参与者向低门槛层聚集；回答层竞争密度更低、深度内容机会相对更大
- 建议：想法任务作日常底盘、回答任务做增量，避免在单一层级内卷

**洞察 3 · AI 协作排除条款的信号意义**
- 现象（F-037, F-040）：四类排除内容均含「涉及 AI 协作」；官方积分条件为「非纯 AIGC 生成」（F-057）
- 根因（洞察）：盐粒激励指向「人类原创信号」甄别——纯 AI 内容会稀释瓜分池价值与社区内容质量
- 影响（预期推断）：纯 AI 生成内容无法参与瓜分；AI 辅助须到「人类判断显性化」程度（观点、案例、结构由人主导）
- 建议：AI 工具仅用于资料检索与编辑辅助；成品中的判断、经验、数据引用须人工把关并留痕

**洞察 4 · 流量激励与作品资产的双轨结构**
- 现象（F-001~F-027 项目广场长期榜单；F-044~F-048 科学季短期激励）：同一平台并行「流量型」激励（即时盐粒）与「资产型」沉淀（可运行项目/科普内容）
- 根因（洞察）：两类机制服务不同平台目标——日活（流量型）与内容资产库（资产型）
- 影响（预期推断）：打卡收益短期可复制但单位价值低且随奖池摊薄波动；项目资产冷启动慢、热度不确定，但具备复利与展示价值
- 建议：双轨并行——日常打卡保底，同时以项目广场作品或开源计划科普内容建长期资产

**洞察 5 · 专业内容的时间窗红利**
- 现象（F-044, F-047, F-052, F-061）：万元现金（总榜前三，F-056）挂钩科学知识开源计划；活动窗 09.30–10.30 与 2026 国庆（10.1–10.7）及诺奖公布窗（10.5–10.12）重叠；报名窗 9.3–9.30（F-055）
- 根因（洞察）：平台以现金奖励拉升专业内容供给，供给缺口的时间窗内单位收益高于日常瓜分
- 影响（预期推断）：具备专业领域知识背景者，在该时间窗内单位时间收益高于日常打卡；错过报名窗则当届不可参与
- 建议：专业背景创作者优先跟踪开源计划报名窗（9.3–9.30），日常打卡作保底；无专业背景者走通用打卡 + 项目广场轨

## 3. 同主题簇互链清单

| bundle | 互链方向 |
|---|---|
| [ai-monetization](../../../projects/awesome-okf-xs/doc/bundles/sheke/industry/ai-monetization/index.md) | 总论：变现模式全景 → 本 bundle 是其「平台内创作激励」场景的具体化 |
| [monetization-essence](../../../projects/awesome-okf-xs/doc/bundles/sheke/industry/monetization-essence/index.md) | 方法论：变现本质公理 → 本 bundle 提供知乎平台的机制实例 |
| [overseas-freelance-night-work](../../../projects/awesome-okf-xs/doc/bundles/sheke/industry/overseas-freelance-night-work/index.md) | 对照：数字自由职业副业族 → 知乎打卡是「低门槛零成本」一极，海外远程是「技能变现」一极 |
| [ai-one-person-micro-product](../../../projects/awesome-okf-xs/doc/bundles/sheke/industry/ai-one-person-micro-product/index.md) | 延伸：一人公司/微型产品 → 本 bundle 路径层的「资产型」轨道可接入其验证循环 |

## 4. Task 6 生成顺序（G3：信源先行）

1. `references/article-source.md`（F-001~F-067 与 facts.md 逐字一致）→ `references/verification.md`；
2. `concepts/00-overview.md` → `01`~`03`（事实层）→ `04`~`06`（机制层）→ `07`~`09`（路径层）；
3. `index.md`（含主题关联互链 + toctree + status: flagged + stale_after）→ `log.md` 最后写；
4. 更新 `industry/index.md`（导航表+1 行、toctree+1 条、description 18→19 束）→ `sheke/index.md`（16→17 束方向列表、18→19 束分组表）→ 总 `index.md`（total_bundles 564→565、sheke 41→42 束两处、图与表同步）；
5. frontmatter 十字段对齐 `ai-monetization` 范式（okf_version/type/title/description/tags/sources/generated）。

## 5. 自检

- [x] 三层无缺层（事实→机制→路径）、无混层（事实层不含因果、机制层每条显式标「洞察/推断」）
- [x] 每篇 concepts 均有 F 编号映射来源
- [x] 洞察四元组 5 条（现象挂 F、根因/影响/建议标注推断性质）
- [x] 单源标注机制落到 01/02/03 与 09（verification.md 第 6 节清单）
- [x] 防混用三对照（F-056 vs F-048 纪念卡/徽章；F-058 vs F-048 100,000 盐粒；F-059 vs F-060 兑换比）在 04 篇显性化
