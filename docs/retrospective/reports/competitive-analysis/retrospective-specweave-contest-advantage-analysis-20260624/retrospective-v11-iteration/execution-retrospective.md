+++
id = "retrospective-specweave-contest-advantage-analysis-20260624-v11-iteration-execution"
date = "2026-06-25"
type = "execution-retrospective"
scope = "iteration"
source = "retrospective-specweave-contest-advantage-analysis-20260624/retrospective-v11-iteration.md#过程事实"
+++

# 过程事实（按时间线）：v11 双作品策略迭代

> 来源：[README.md](README.md) — 迭代复盘索引

## 1. 承前：v10 已完成，用户揭示真实参赛身份

此前 11 轮对话已将竞品分析迭代至 v10——13 项优势 + 13 条洞察 + Community Live #13 TRAE Rules 产品根基。用户随后揭示实际报名作品是 [竹简悟道](https://forum.trae.cn/t/topic/28207)，SpecWeave 退为方法论基础设施。上轮对话末尾，用户要求"两者分别制定策略"，export-suggestions.md 重写启动但中途断裂。

## 2. 断裂修复（首个关键事件）

**问题**：export-suggestions.md 第一次 SearchReplace（写入 §4.0-4.2）成功后，第二次 SearchReplace（清理旧内容）因文件已被修改而失败——错误信息为 "search content not found in original content"。文件处于混合状态：新 §4.0-4.3 头部 + 旧 v10 内容尾部。

**修复路径**：
```
① Read 388 行确认断裂边界（行 169 起为旧内容）
② RunCommand 截取前 168 行为 head 文件
③ Write 新 tail 内容（§4.3.1 全人工评审策略 → §4.6 赛后延续）
④ PowerShell $head + $tail 拼接写入目标文件
⑤ 验证 312 行，尾部内容完整
```

**根因**：SearchReplace 工具在文件已被修改后无法识别旧的 search content——这是工具本身的并发感知缺陷。预防措施：涉及多个 SearchReplace 对同一文件操作时，后续 SearchReplace 的 old_str 必须是**第一轮替换后的实际内容**，而非原始文件内容。

> **教训**：大块内容替换优于局部搜索替换。当替换量超过 100 行时，优先用"截取头部 + 拼接新尾部"的 Write 策略，而非多轮 SearchReplace。

## 3. 策略重写（核心产出）

export-suggestions.md 从 SpecWeave 单作品策略完整重写为双作品结构：

| 章节 | 内容 | 关键决策 |
|------|------|---------|
| §4.0 | 双作品关系定位 + 80/20 资源分配 + 交叉叙事线 | SpecWeave 的参赛价值不是"多一个作品多一次机会"，而是"让竹简悟道 TRAE 应用深度打满分" |
| §4.1 | 竹简悟道主策略：赛道/四维评审得分预估 4.7/5 / 三层差异化叙事 / Demo 帖模板 | 逆周期定位——"所有 AI 追求更快，我刻意追求更慢" |
| §4.2 | SpecWeave 辅策略：轻量级 1 小时投入 / 四目标 / 交叉引用设计 | 不追求独立晋级——追求在关键维度上的证据溢出 |
| §4.3 | 共享策略：全人工评审叙事 + HTML 差异化 + 抖音传播 | "一个人工评审看的不只是产品，而是你做了什么别人没做过的事" |
| §4.4-4.6 | 两作品并行行动清单（6/25 → 决赛）+ 官网资源 + 赛后延续 | 竹简悟道 28.5h / SpecWeave 8h，严格 80/20 |

## 2.4 报名帖撰写

在 export-suggestions §4.2.2 轻量级 Demo 帖策略指导下，撰写 SpecWeave 报名帖草稿：

**错误路径**：初稿直接写入 `d:\AI\specweave-registration-post.md`（根目录）——违反项目约定。用户指出后立即移至临时目录，再复制到竞品分析报告目录。

**正确路径**：`d:\AI\docs\retrospective\reports\competitive-analysis\retrospective-specweave-contest-advantage-analysis-20260624\specweave-registration-post.md`

> **教训**：文件新建时先确认目标目录是否符合项目约定——临时文件 → 临时目录，最终产物 → 项目规范目录。

## 5. 全局定位修正（第二个关键事件）

用户指出"Vibe Coding 是否太局限了"。分析确认三个问题：

| 问题 | 影响 |
|------|------|
| 范畴过窄 | Vibe Coding 暗示只是"写代码"——但 SpecWeave 覆盖文档撰写、架构设计、研究分析等一切深度 AI 协作 |
| 时效性风险 | 热潮词——评审可能认为是蹭标签 |
| 降维效应 | 把完整方法论框在"写代码"格子里，削弱实际价值 |

**修正策略**：Vibe Coding 降级为行业背景切面（仅 4 处保留为"问题引入的切口"），核心定位升级为"**AI 智能体协作的工程化方法**"。

**修正范围**：
- `insight-extraction.md`：3 处（优势 11 标题+内容、洞察 4 标题+内容、洞察 8 叙事表述）
- `execution-retrospective.md`：2 处（策略影响矩阵 + 评审机制）
- `export-suggestions.md`：2 处（答辩预判 + 赛后规划）
- `specweave-registration-post.md`：5 处（标题、问题引入、一句话定位、目标用户、社会价值）

共 14 处修正，剩余 4 处 Vibe Coding 引用均为正确的"背景切面"用法。
