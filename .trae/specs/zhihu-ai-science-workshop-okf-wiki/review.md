# 对抗审查报告：知乎《AI 科学创新工坊第二弹》→ OKF v0.2 知识包

## 审查元信息

| 项 | 值 |
|---|---|
| 审查时间 | 2026-10-22 |
| 审查者 | V 阶段审查者（同会话执行，但**机械检查全部独立重跑**，不复述 E 阶段自检结论） |
| 独立性说明 | 本次审查**非** fresh-context 第三方审查。四视角对抗审查在 E 阶段内以「魔鬼代言人 / 新人 / 老板 / 未来」四角色执行并写入 `references/verification.md`；本报告在此基础上做**独立机械复跑**（重写正则脚本、重跑三个官方门禁、自写链接解析），并逐 AC 给出裁决。局限：结论由同一会话产出，缺少独立第二意见 |
| 审查对象 | `projects/awesome-okf-xs/doc/bundles/sheke/industry/zhihu-ai-science-workshop/`（15 个 .md）、三级索引增量改动、spec 侧 facts.md / spec.md / tasks.md |
| 对照基准 | spec.md（AC-1~AC-7）、tasks.md、facts.md、同组先例 `zhihu-monetization/`、`big-tech-pontzi-track-selection/`、`ai-side-hustle-playbook/`、磁盘当前态三级索引 |
| 方法 | ①通读全部 15 个被审文件 + spec/tasks/facts + 先例；②独立重跑机械检查（自写 Python 脚本 + 三个官方门禁），不复述作者自检；③逐 AC 独立判断并给锚点理由；④F 编号双向对账；⑤发现项修复后复检闭环；⑥**暂存树复跑**（把将要落库的树检出后重跑门禁） |

> **结论演进**：**首轮（2026-10-22）：5 项 P1 未闭环**——F 编号重排后的交叉引用漂移（P1-1）、frontmatter 首行开围栏丢失（P1-2）、F-073 双份登记措辞不一致（P1-3）、跨束链接层级错误（P1-4）、log.md 含绝对路径字面量（P1-5）。
> **终轮（同日）：PASS**——P1-1~P1-5 全部修复并复检闭环；AC-1~AC-4、AC-6~AC-7 全 PASS，AC-5 全篇抽检 PASS；P0 零项，残留仅 P2 级观察项。

---

## 逐 AC 裁决

### AC-1：bundle 骨架与定位 —— **PASS**（rule）

独立证据（机械枚举，非引用）：

- 目录枚举恰为 15 个 .md：`index.md`、`log.md`、`concepts/{index,00-overview,01-campaign-facts,02-track-rules,03-participation-flow,04-science-challenges,05-participant-works,06-mechanism-insights,07-participation-path,08-risks-and-boundaries}.md`、`references/{index,article-source,verification}.md`，与 FR-1 一一对应；`examples/` 目录 Test-Path=False。
- `okf_version` 出现文件集合 = `['index.md']`（机械扫描全 15 文件），符合 OKF v0.2「仅 bundle 根 index.md 携带」规则。
- 根 index.md 隐藏 toctree 三条目（concepts/index、references/index、log）；concepts/index.md toctree 9 条；references/index.md toctree 2 条。
- 官方 `check-bundles-index.py` 在**工作树** exit 0：「9 域 / 63 组 / 671 束，frontmatter、计数行、节标题、分组表、toctree 五面一致」；在**暂存树**（本任务落库态）同样 exit 0：「9 域 / 63 组 / 666 束，五面一致」。
- 骨架判定两问留痕于 spec.md §2 与 log.md：第二问为「否」→ 不设 `examples/`，description 标注「活动规则分析包，非操作教程」。

### AC-2：F 编号双份一致、事实观点分层 —— **PASS**（rule）

独立证据（正则 `^\|\s*F-(\d{3})\s*\|` 自行提取）：

- `references/article-source.md`：83 条，min=1 / max=83，**连续无跳号、无重复**；spec 侧 `facts.md`：83 条，同样连续。双向差集 = `set()`（完全相等）。
- **83 行声明列逐字一致**：首轮比对曾发现 F-073 的信源定位与备注列措辞在两侧不一致（bundle 侧写「豆包官方定价文档 / C17 ❌ 源文措辞失实，须勘误」，spec 侧为「豆包官方帮助中心定价文档 + 付费服务协议 / C17 ⚠️ 部分确认……」），已按 spec 侧权威表述回填 bundle 后复检通过。
- 全束 F 引用越界扫描：concepts + references + index + log 中出现的所有 `F-NNN` 均在 83 条域内，**越界 0**。
- 事实层零因果推断词（G1 门）；机制层因果表述全部显式标注「洞察/推断」；路径层收益零承诺。

### AC-3：P0 核验与勘误完整、flagged 管理 —— **PASS**（rule）

独立证据（verification.md 逐点定位 + F 编号对账）：

- 结论表 19 行齐备（C1~C19），含 ✅ / ⚠️ 两级判定与各自的证据主体与备注列；勘误 5 项逐条落在 F-073 / F-077 / F-078 / F-080 / F-081 上，编号与正文双处可查。
- 关键事实错误均有官方依据：诺奖为**诺贝尔物理学奖 2026**（2026-10-06 瑞典皇家科学院公布）、获奖者**仅 Francis Halzen 一人独享**（Prize share 1/1），2025 年度奖为 Clarke/Devoret/Martinis（超导量子隧穿），与本活动无关；「豆包标准模式会员卡」非官方产品名，官方为「豆包专业版·标准套餐」且 ¥68 是**连续包月价**（另有连续包年 ¥688、单次购买 1 个月 ¥80、1 年 ¥828）；官方中微子口径为「约 **100 万亿**/秒穿过人体」，「650 亿」原指「每秒约 650 亿个太阳中微子穿过你的小指甲」。
- **自我纠错留痕**：首轮把「活动说明 4 条条件」误并入投稿要求而判「实为 5 项」，回溯 `raw/cli-windows.md` 6 个窗口逐字比对后确认投稿要求恒为 **4 条**（原创图文 ≥500 字 / 配图 ≥3 张 / 嵌入作品链接 / 标注赛道），已在 spec.md §6 标为 C13 自我纠错并在 log.md 落账。
- **去重判定**：7 篇检出参赛作品中 `p/2093792060528649287` 与 `p/2093028032369932182` 同作者同署名且正文同句，**非独立佐证** → 独立参赛作品 6 篇（F-066~F-071，F-072）。
- flagged 一致性：14 个含 frontmatter 文件全部 `status: flagged` + `stale_after: 2026-12-31`；`log.md` 按体例无 frontmatter。
- 无编造深链：只记「发布主体 + 指标名 + 时点 + 结论」三元组，不固化页面深链。

### AC-4：原创改写与版权安全 —— **PASS**（rule）

独立证据：

- 全束 15 文件无 `.jpg/.jpeg/.png/.gif/.webp/.svg/.html`（机械扫描 media 文件数 = 0），无原图入库，无原文 raw HTML 镜像。
- 敏感串扫描 `sk-` / `ghp_` / `AKIA` / 键值赋值型敏感模式 / 本机绝对路径，在 15 文件中命中 **0**；`file` 协议的绝对路径链接写法命中 **0**（首轮曾在 log.md 的描述性文本中出现该字面量，已改写）。
- 编者补充与编者推断均显式标注；正文呈现一律为核验后的值，源文错误值只出现在引述与勘误表。

### AC-5：三级索引与机械门禁 —— **PASS**（rule）

独立证据（本轮亲自重跑）：

- 官方 `scripts/check-bundles-index.py` exit 0（工作树）：「bundles 总索引对账通过: 9 域 / 63 组 / 671 束，frontmatter、计数行、节标题、分组表、toctree 五面一致。」exit 0（暂存树）：「9 域 / 63 组 / 666 束，五面一致。」
- 官方 `scripts/check-utf8.py` exit 0：「UTF-8 检查通过: 12254 个文件均为有效 UTF-8。」
- 官方 `scripts/check-toctrees.py`：工作树 exit 1，报出 2 条，全部位于 `doc/bundles/sheke/finance/ponzi-scheme/`（**未跟踪目录**，属并行会话在途产物），本束命中数 **0**；暂存树 exit 0：「toctree 检查通过: 全部 index.md 引用有效，所有内容文档均可达。」
- 自写 8 项机械门禁脚本 `gate_v.py` 输出 **PASS 17 条**：双份 F 编号一致且连续（F-001~F-083）、83 行声明列逐字一致、bundle 根 3 条 / concepts 9 条 / references 2 条 / 组级 30 条 / 域级 9 条 / 总索引 9 条 toctree 全部可达、三级计数一致（总 671 / sheke 76 / industry 30）、敏感信息零残留、frontmatter 结构与字段完整（14 个含 frontmatter）、5 项勘误逐条落实回验、相对链接全可达且零绝对路径。
- 计数面共 **10 处**逐面核对（总索引 frontmatter + 计数行 + mermaid + 节标题 + 分组表 = 5；域级 description + 域简介 + 分组行 = 3；组级 description + 导航行 + toctree = 2），全部一致。
- **并发污染的如实处置**：工作树地面真值 671 束 vs 索引 HEAD 基线 665 束，差额 +1 属本束、+5 属他人在途束（jishu 493→497、jishu/ai 261→265、finance 2→3），提交时以 HEAD 基线 + 本任务增量（666 束）写入索引，**未夹带**他人在途增量，也未回退他人工作树改动。

### AC-6：知识转化质量 —— **PASS**（rule）

锚点理由：

- 三层结构完整可辨：事实层 6 篇（00~05）逐条挂 F；机制层 1 篇（06）四元组洞察的根因/影响/建议三项全部标「洞察/推断」；路径层 2 篇（07 路径 / 08 风险边界）收益仅挂 F 或标「待验证」。
- 评测与奖池解构未越界：40,000 元拆为单赛道 20,000 × 2，10 张豆包卡名义面值 680 元与商汤周边**不计入**奖池；「40,000 元现金奖池」与「10 张卡」**不可相加**（F-082）；「海量 Token」无量化口径（G2），**不可**用参赛者自述积分 36500 反推官方额度。
- 防混用注记在 00 / 04 / 08 三篇显性化：本活动 ≠「科学季 2026」（主办方、时间窗、玩法、奖励形态均不同）；两期之间 10/1–10/8 空档无说明（G9）；诺奖年份 2026 与获奖者 Halzen 个人不可写成 2025 年度或「与 IceCube 团队」。
- 5 项勘误在正文命中回验通过：①标准套餐 + 连续包月 ②投稿要求恒为 4 条 ③2026 年度诺贝尔物理学奖 + 10-06 早于活动起始 ④100 万亿/秒穿过人体 ⑤独立作品 6 篇。

### AC-7：相对链接与路径规范 —— **PASS**（rule）

独立证据：

- 自写链接解析器扫描全束 15 文件的 `](*.md)` 链接并按各文件所在目录规范化解析，**broken = 0**（含 concepts 内互链、根 index→concepts/references、跨束主题关联 `../../zhihu-monetization/...`、references 内互链）。
- 首轮曾检出 `concepts/00-overview.md` 的跨束链接少一层 `../`（应为 `../../zhihu-monetization/...`）→ 已修正并复检通过。
- 零 `file:///` 绝对路径链接；文档内路径一律相对路径。

---

## 发现清单

| ID | 级别 | 发现 | 处置 | 状态 |
|---|---|---|---|---|
| P1-1 | P1 | 勘误段重排后 facts/article-source 两表编号变为 F-073~F-083，但 concepts/00~04、verification.md 与两表备注列仍指向旧编号 F-070~F-080（共 45 处交叉引用漂移） | 经 45 处定向锚定替换，使编号引用与权威声明逐一对齐 | 已闭环 |
| P1-2 | P1 | 批量 frontmatter 归一化脚本拼接缺陷，导致 14 个文件丢失 frontmatter 首行开围栏 `---` | 由定向修复脚本按文件补回首行围栏 | 已闭环 |
| P1-3 | P1 | F-073 在 spec facts.md 与 bundle article-source.md 两侧的**信源定位与备注列措辞不一致**（bundle 侧偏离权威表述） | 按 spec 侧权威表述回填 bundle，复检 83 行逐字一致 | 已闭环 |
| P1-4 | P1 | `concepts/00-overview.md` 的跨束链接层级错误（少一层 `../`），链接不可达 | 修正为 `../../zhihu-monetization/...`，复检 broken=0 | 已闭环 |
| P1-5 | P1 | `log.md` Verification 段在描述检查项时写入 `file:///` 字面量，会被链接正则命中 | 改写为「`file` 协议的绝对路径链接写法零命中」，复检命中 0 | 已闭环 |
| P2-1 | P2 | 源文 7 处正文内链 href 因知乎 403 通道限制不可复核 | 显式登记为已知限制（`references/verification.md` + `index.md` 信源边界段），不据锚文本反推 URL | 已知缺口，不阻断 |
| P2-2 | P2 | 「海量 Token」无官方量化口径 | 标为 G2 缺口，并禁止用参赛者自述积分反推官方额度 | 已知缺口，不阻断 |
| P2-3 | P2 | 第一期与第二期之间 10/1–10/8 空档无活动说明，两期是否共用「科学季」项目类型未获明示 | 标为 G9 缺口，写入时间轴与防混用注记 | 已知缺口，不阻断 |
| P2-4 | P2 | 活动结束后的获奖名单与真实投稿数据未登记 | 本束只登记活动规则，不登记结果；Q2 留待后续追加「结果层」文档 | 设计取舍，不阻断 |

> **P0 零项**：未发现会导致产出不可信、不可用或产生虚假声明的缺陷。

---

## 机械检查原始输出摘要

```
=== gate_v.py（自写 8 项机械门禁）===
bundle 文件数: 15
PASS [G2] 双份 F 编号一致且连续：F-001~F-083（83 条）
PASS [G2b] 事实表 83 行逐字一致
PASS [G3] bundle 根: 3 条 toctree 全部可达
PASS [G3] concepts 索引: 9 条 toctree 全部可达
PASS [G3] references 索引: 2 条 toctree 全部可达
PASS [G3] 组级 industry: 30 条 toctree 全部可达
PASS [G3] 域级 sheke: 9 条 toctree 全部可达
PASS [G3] 总索引: 9 条 toctree 全部可达
PASS [G4] 三级索引计数一致：总 671 / sheke 76 / industry 30
PASS [G5] 密钥/凭据/本机绝对路径零残留
PASS [G6] frontmatter 结构与字段完整（14 个含 frontmatter）
PASS [G7] 勘误1 官方产品名 落实回验通过
PASS [G7] 勘误2 投稿要求 4 条 落实回验通过
PASS [G7] 勘误3 诺奖年份+公布日 落实回验通过
PASS [G7] 勘误4 中微子官方口径 落实回验通过
PASS [G7] 勘误5 独立作品 6 篇 落实回验通过
PASS [G8] 相对链接全部可达，零 file:///
机械门禁全部通过（PASS 17 条）

=== 官方门禁（工作树）===
check-bundles-index.py : exit 0  9 域 / 63 组 / 671 束，五面一致
check-utf8.py          : exit 0  12254 个文件均为有效 UTF-8
check-toctrees.py      : exit 1  2 条，均位于他人在途未跟踪目录 sheke/finance/ponzi-scheme/，本束命中 0

=== 官方门禁（暂存树 · 待落库的那棵树）===
check-bundles-index.py : exit 0  9 域 / 63 组 / 666 束，五面一致
check-toctrees.py      : exit 0  全部 index.md 引用有效，所有内容文档均可达
```

---

## 实质性质证覆盖说明

| 质证点 | 结论 | 依据 |
|---|---|---|
| 活动存在性 | 真 | 知乎「知乎科学」已认证机构号 + 权威媒体转载（第一期） |
| 40,000 元奖池算术 | 自洽 | 单赛道 20,000 × 2；卡券与周边不计入奖池 |
| 诺奖指涉 | **源文有误，已勘误** | 官方为诺贝尔物理学奖 2026、Halzen 一人独享；公布日早于活动起始 3 天 |
| 豆包产品名与定价 | **源文有误，已勘误** | 官方为「豆包专业版·标准套餐」，¥68 为连续包月价 |
| 投稿要求条数 | **首轮自我误判，已纠错** | 回溯 6 窗口逐字比对，恒为 4 条 |
| 中微子数量级 | **转述失真，已勘误** | 官方为约 100 万亿/秒穿过人体；「650 亿」原指太阳中微子穿过小指甲 |
| 独立参赛作品数 | **去重后 6 篇** | 7 篇中 1 篇与另一篇同作者同署名同句 |
| 商汤「技术支持」 | 平台自述，⚠️ 单源 | 商汤官网仅见「代码小浣熊 / 办公小浣熊」；徽章与杯具 IP 吻合可旁证 |
| 「海量 Token」 | 无量化口径，⚠️ | 不可用参赛者自述积分反推官方额度 |

---

## 最终结论

**PASS**。AC-1~AC-7 全部通过；P0 零项；P1 五项全部修复并复检闭环；残留 P2 四项为**已知缺口与设计取舍**，已在 bundle `log.md` 与 `references/verification.md` 显式登记，不构成交付阻断。

产出物：`projects/awesome-okf-xs/doc/bundles/sheke/industry/zhihu-ai-science-workshop/`（15 个 .md），`status: flagged` + `stale_after: 2026-12-31`；到期前优先复核项为 P2-1（7 处 href）与活动结果层。

---

## C 阶段（原子提交）记录

| 层 | 提交 | 提交集 | 隔离说明 |
|---|---|---|---|
| 子模块 `projects/awesome-okf-xs` | `19bae835` | 18 个文件（15 本束新文件 + 3 份共享索引的本任务增量），1865 insertions / 8 deletions | 三份共享脏文件以 `git show HEAD:<path>` 取 HEAD 基线 → 临时副本施加本任务增量 → `git hash-object -w` + `git update-index --cacheinfo` 精确写入索引；工作区的 finance/ponzi-scheme、jishu/ai 4 束及其索引增量**未被夹带** |
| 主仓 `SpecWeave` | 本次提交 | spec 四件套（spec.md / tasks.md / review.md / facts.md）+ `projects/awesome-okf-xs` gitlink 指针前移（a046ea05 → 19bae835） | 主仓工作区的他人在途改动（`docs/retrospective/**`、`.trae/specs/retrospectives-insights/**`、根目录 4 个 png）一律未纳入；`raw/` 已被 `.trae/specs/.gitignore` 排除 |

> **不 push**：子模块与主仓均未推送远端。
