# 中西数学对读知识包 — 内容规格契约（子代理写作依据）

> 本文件是 `east-west-dialogue` 知识包内容文档（concepts 9 篇 + examples 3 篇）的统一写作契约。所有文档必须严格遵守。

## 一、输出位置

- 概念文档写入：`d:\spaces\SpecWeave\projects\awesome-okf-xs\doc\bundles\kexue\math\east-west-dialogue\concepts\`
- 示例文档写入：`d:\spaces\SpecWeave\projects\awesome-okf-xs\doc\bundles\kexue\math\east-west-dialogue\examples\`

## 二、Frontmatter 模板（强制）

概念文档（type: Concept）：

```yaml
---
type: Concept
title: <中文标题>
description: <一句中文概括，60-120字>
tags: [中西比较, <主题词>, ...]
generated: { by: "agent:seven-concepts-cmd", at: "2026-09-01T12:00:00+08:00" }
status: draft
stale_after: 2027-09-01
sources:
  - id: <信源id，如 r-mactutor-ninechapters>
    resource: <URL 或库内相对路径>
    title: <信源名>
    author: <org:xxx 或 person:xxx>
---
```

示例文档（type: Example）同模板，仅 `type: Example`。

**硬规则**：
- YAML 中含中文的引号一律全角“”；禁止 ASCII 双引号嵌套在双引号标量内（MyST 会报 Malformed YAML）
- 每篇 sources 至少 2 条（一西方侧一中国侧或一研究信源一库内链接）
- 正文规范现代汉语；文件名 kebab-case 纯英文
- 禁止 `file:///` 绝对路径；交叉引用一律相对路径
- 数学公式用 `$...$`；可用 mermaid 围栏图（```mermaid）

## 三、相对路径速查（从 concepts/ 或 examples/ 出发，两处相同）

| 目标 | 相对路径 |
|------|---------|
| 本束 bundle 根 | `../index.md` |
| 本束 facts | `../facts.md` |
| 本束其他 concepts | `0X-slug.md` |
| 本束 examples | `../examples/XX-slug.md` |
| 本束 references | `../references/xxx.md` |
| classics-reading 束根 | `../../classics-reading/index.md` |
| classics-reading concepts（如 05） | `../../classics-reading/concepts/05-greek-geometry.md` |
| classics-reading examples（如 01） | `../../classics-reading/examples/01-euclid-close-reading.md` |
| classics-reading references | `../../classics-reading/references/original-sources.md` |
| suanjing-reading 束根 | `../../../../guoxue/suanxue/suanjing-reading/index.md` |
| suanjing-reading concepts（如 06） | `../../../../guoxue/suanxue/suanjing-reading/concepts/06-zhoubi-suanjing.md` |
| suanjing-reading examples（如 07） | `../../../../guoxue/suanxue/suanjing-reading/examples/07-geyuan-pi.md` |
| 3b1b | `../../../../jishu/viz/3b1b/index.md` |
| psi-math | `../../../../zhexue/psi/psi-math/index.md` |
| katex | `../../../../jishu/document/katex/index.md` |
| sympy | `../../../../jishu/data/pydata/sympy/index.md` |
| kexue/chemistry | `../../../chemistry/index.md` |
| kexue/physics | `../../../physics/index.md` |

**注意**：concepts/ 与 examples/ 都在 bundle 根下一级，上述路径对两个目录均适用。

## 四、既有束可链接目标（真实存在的文件，链接必须用这些文件名）

classics-reading/concepts/：00-why-read-originals、01-accessing-originals、02-editions-translations、03-using-commentaries、04-reading-across-languages、05-greek-geometry、06-hellenistic-number-theory、07-islamic-algebra、08-early-modern-17c、09-euler-18c、10-gauss-turn、11-nineteenth-revolution、12-rigor-and-foundations、13-twentieth-foundations

classics-reading/examples/：01-euclid-close-reading、02-first-originals-starter、03-reading-roadmap

suanjing-reading/concepts/：00-why-read-suanjing、01-history-overview、02-chousuan-numeration、03-jiuzhang-structure、04-jiuzhang-key-methods、05-liuhui-commentary、06-zhoubi-suanjing、07-suanjing-shishu、08-zu-chongzhi、09-song-yuan-peak、10-dayan-tianyuan-siyuan、11-ming-qing-transition、12-chinese-math-characteristics、13-reading-path

suanjing-reading/examples/：01-fangtian-fractions、02-yingbuzu-double-false、03-fangcheng-negative、04-gougu-pythagoras、05-wuwuzhishu-crt、06-baiji-weng、07-geyuan-pi、08-reading-plan

## 五、事实一致性要求

facts.md 已存在（本束 `../facts.md`，可读取），含 F-001~F-043。正文中涉及年代、人物、优先权、交流事件的事实必须与 facts.md 一致；关键事实可在行内标注 `（F-0XX）` 形式引用。核心事实摘要：

- 《原本》约前 300 年，13 卷，卷一 23 定义 5 公设 5 公理 48 命题（F-001）
- 《九章》246 题，九章名目（F-002）；方程章"遍乘直除"= 高斯消元等价（F-013）；最早负数记载（F-014）
- 刘徽约 220–280，263 年注九章（F-004）；割圆术 192 边形、徽率 157/50（F-010）；"割之弥细"引文（见 suanjing-reading）
- 祖冲之 π 界 3.1415926–3.1415927、密率 355/113（F-019）
- 阿基米德 96 边形、3+10/71 < π < 3+1/7（F-009）
- 李冶 1248《测圆海镜》天元术（F-006）；朱世杰 1303《四元玉鉴》（F-007）
- 花剌子米约 820《代数学》修辞代数（F-015）
- 1607 利玛窦+徐光启前六卷、克拉维乌斯底本（F-024）；界说/求作/公论/题（F-025）；1857 伟烈亚力+李善兰后九卷、Billingsley 底本（F-027）；1865 金陵书局十五卷本（F-028）
- 争议并列：周髀勾股证明归属（Cullen 质疑，F-020）；负数/优先权无传播证据（F-018/F-021/F-022/F-023）
- Chemla 证明观（F-035）；MacTutor "not exactly proofs"（F-034）；中国数学无公理化发展、问题导向（F-032）

**反偏见要求**：比较分析避免单线进化史观、文化优越论、时代错置；优先权表述为"平行独立发展"或"文献先后比较，不构成传承证据"。

## 六、篇幅与结构

- 概念文档每篇 130–220 行；示例文档每篇 150–250 行
- 六大主题概念（03–08）必须含四个二级标题节（名称可微调但四层齐备）：`## 西方节点`、`## 中国平行`、`## 比较分析`、`## 对读示范指引`，开头另有引言节
- 每篇至少 2 条指向既有两束的相对链接（04 方法论篇指向两束导论/示例）
- 示例文档必须含四个固定部分：`## 原文对照`、`## 解法逐步对照`、`## 现代统一解读`、`## 差异分析`，另有引言与延伸

## 七、写作完成后自查

- [ ] frontmatter YAML 可解析（注意全角引号规则）
- [ ] 所有相对链接目标存在（对照第三节路径表）
- [ ] 事实与第五节摘要一致，争议处并列
- [ ] 无 file:///、无 ASCII 引号嵌套、文件名 kebab-case
