# Review：中国古代物理典籍阅读教程 OKF 知识包

> 验收时间：2026-08-30
> 验收对象：`d:\AI\projects\awesome-okf-xs\doc\bundles\science\physics\chinese-physics-classics/`
> 验收方式：独立只读审查（V 阶段发现性审查 → 修复 → Review 阶段最终验收审查），未修改源码文件。

## 一、验收标准对照（AC-1 ~ AC-9）

| AC | 验收项 | 结论 | 依据 |
|----|--------|------|------|
| AC-1 | 结构完整性 | ✅ | 28 个 .md：根 4 + concepts 9 + examples 10 + references 5 |
| AC-2 | toctree/链接 | ✅ | 束内 0 断链；三处跨束链接均可达；无 file:///；`invoke gates.toctrees` 全局通过 |
| AC-3 | Sphinx 构建 | ✅（环境受限） | 28 个 .md markdown-it 解析 0 失败；gates.utf8 通过；全站 6044 文件 `-E` 强制构建在本环境反复被系统中断（未到 science 域），已在 log.md 记录 |
| AC-4 | 引文可溯源 | ✅ | 9 篇 examples ≥20 条原文抽查逐字一致；所有引文在 online-sources（W-1~14）/ core-classics（C-1~9）登记；辑佚转引标注"某书引某书"层级 |
| AC-5 | frontmatter/编码 | ✅ | 根 index 含 type/okf_version/status/generated/stale_after；工作文档无 frontmatter；28 文件 UTF-8 无 BOM |
| AC-6 | 索引联动 | ✅ | bundles→science→physics→两束 toctree 完整；`gates.toctrees` 0 断链 |
| AC-7 | 解读学术质量 | ✅（rubric≥4） | 原文/解读分层；顺收限≈f、距显限=f1+f2、司南四说、磁偏角等核对准确；争议显式标注；无过度拔高 |
| AC-8 | 教程可用性 | ✅（rubric≥4） | 三类读者各有独立快速开始路径；跨文档引用顺畅 |
| AC-9 | 七概念过程 | ✅ | facts.md 无因果词（正则 0 命中）；insights.md 6 条四元组（现象/根因/影响/建议）；3 个 Conventional Commits 单一职责 |

## 二、七概念链路（R→I→E→V→C）质量门

| 门 | 检查项 | 结论 |
|----|--------|------|
| G1 | 事实无因果词 | ✅ facts.md（F-001~F-061）纯客观，因果词 0 命中 |
| G2 | 洞察四元组 | ✅ insights.md 6 条均含现象/根因/影响/建议 |
| G3 | 模式可迁移 | ✅ concepts/07 解读方法论含触发场景+检查清单+术语对照+反模式（辉格五问） |
| G4 | 提交原子化 | ✅ 三提交职责分离，单一可验证 |

## 三、原子提交记录（子模块内，C 阶段）

| commit | 消息 | 职责 |
|--------|------|------|
| 09c596fa | `feat(physics): 新增中国古代物理典籍阅读教程知识包骨架与信源文档` | 骨架 + 根 index/facts/insights/log + references 4 篇 |
| 64a0fa51 | `docs(physics): 补充八篇概念文档与九篇典籍原文解读` | concepts 8 + examples 9 + 两子目录 index |
| 5bf811d7 | `docs(bundles): 自然科学域物理分组索引与信源索引联动` | references/index + science/index + physics/index |

边界验证：三提交共 30 文件 1944 行新增，未纳入任何并行会话的 chemistry/physics-classics-reading/relationships 文件；`git status` 无本束遗留未提交变更。

## 四、V 阶段发现与修复闭环

独立审查发现 6 项问题，全部修复：
1. [高] examples/07 跨束链接缺一层（`../../chemistry` → `../../../chemistry`）✅
2. [高] references/extended-bibliography 跨束链接缺一层 ✅
3. [低] concepts/02、03、06；examples/03 偏辉格措辞（"世界上最早/最高/受控实验高峰"）→ 改为标注评价者或中性表述 ✅
4. [低] examples/04（磁石拒棋、雷者火也）、examples/09（作照景镜）引用块夹带批注 → 移出引用块 ✅

## 五、外部信源遗留项（非本束缺陷）

- 维基文库（W-14）调研环境抓取失败，已如实标注"未在线核对"，建议日后人工浏览器复核；
- online-sources 深处链（典藏网/识典等站内编号）随站点改版可能变动，属正常运维范畴；
- 全站 sphinx 强制构建受环境限制无法在会话内完成（AC-3），以语法+结构+编码三层验证替代，已在束 log.md 记录。