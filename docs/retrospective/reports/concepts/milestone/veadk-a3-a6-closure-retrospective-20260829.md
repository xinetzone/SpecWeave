---
id: "milestone-veadk-a3-a6-closure-20260829"
title: "veadk 信源稳定性里程碑行动项 A-3/A-6 闭环执行复盘报告"
date: "2026-08-29"
completion_date: "2026-08-29"
type: "Report"
description: "父里程碑（veadk-python 信源稳定性修复）行动项 A-3（Wiki 内部导航断链修复，实测 33 链接/4 文件）与 A-6（ai-collaboration 模式文档 source 归宿排查）的 R→I→V→C 闭环执行；V 阶段对抗审查暴露并修复 GATE-SPS 工具锚点假阳性缺陷（568 个存量误报），模式完成第 3 次独立验证"
status: "stable"
source: "./veadk-python-source-stability-fix-milestone-20260829.md"
milestone-name: "veadk 信源稳定性行动项 A-3/A-6 闭环"
time-range: "2026-08-29（同日完成，四次原子提交 13:11-13:15）"
methodology: "七概念方法论（行动项执行精简链路 R→I→V→C，light 深度，V 阶段对抗审查）"
quality-gates:
  G1: "事实无因果词 ✅（26 条事实，均经命令实测或提交记录核验）"
  G2: "洞察四元组完整 ✅（3 条洞察：陈述+证据+反常识+行动）"
  G3: "模式可迁移验证 ✅（信源稳定性门模式第 3 次验证，新增 2 个检验维度）"
  G4: "行动项原子化 ✅（4 项行动项，含验收标准）"
  V: "对抗审查 ✅（GATE-SPS audit 复扫 + 链接复验 67/0 + 32 单元测试全绿）"
tags: ["里程碑复盘", "七概念", "信源稳定性", "GATE-SPS", "断链修复", "工具假阳性", "external-tag引用", "veadk-python", "行动项闭环"]
generated: { by: "process:retrospective-cmd", at: "2026-08-29T00:00:00Z" }
stale_after: "2027-08-29"
---

<!-- meta_type: retrospective -->

# veadk 信源稳定性里程碑行动项 A-3/A-6 闭环执行复盘报告

> **方法论编排**：七概念行动项执行链路 R→I→V→C（light 深度，V 阶段对抗审查）
> **复盘对象**：父里程碑 [veadk-python-source-stability-fix-milestone-20260829.md](veadk-python-source-stability-fix-milestone-20260829.md) 登记的行动项 A-3（Wiki 内部导航断链修复）与 A-6（模式文档 source 归宿排查）的完整闭环执行
> **复盘日期**：2026-08-29

---

## 一、项目概述

### 1.1 背景

父里程碑于 2026-08-29 同日完成信源稳定性门模式第二案例验证与 800 处引用迁移，登记 6 项边界外行动项。其中 A-1（GATE-SPS 工具建设）、A-2（技能预检内置）、A-4（bundle 元数据同步）、A-5（临时克隆清理）已先后闭环；本会话执行剩余两项：

- **A-3**：修复 veadk-python Wiki 内部导航断链（父报告登记 9 处，指向迁移前旧位置的 `file:///` 绝对链接）
- **A-6**：排查 ai-collaboration 目录其余模式文档 `source` 字段是否误指，并纳入 GATE-SPS 全量扫描补充情报（`skill-intent-routing.md` source 指 `.chaos/libs/tests` 临时克隆）

### 1.2 目标

1. A-3：全部断链修复并通过链接存在性复验，Wiki 内部导航恢复
2. A-6：ai-collaboration 目录活动 source 债清零，失效/虚构引用修正
3. V 阶段对抗审查：GATE-SPS audit 复扫目标文件零发现
4. C 阶段：原子提交、父报告行动项回写、非本任务变更零混入

### 1.3 交付物清单

| 交付物 | 形态 | 提交 |
|--------|------|------|
| GATE-SPS 锚点假阳性修复 + 2 个回归测试 | 工具代码（2 文件，+21/-1） | `ba8272c6` |
| veadk Wiki 33 处断链相对路径化 + 1 处分词歧义修正 | 文档（4 文件，+33/-33） | `e2653788` |
| ai-collaboration source 归宿修复（md 3 处 + TOML 镜像 1 处） | 文档（4 文件，+4/-4） | `1f4a3dfc` |
| 父里程碑报告行动项回写（A-3/A-6 ✅、F-025 计数更正、附录补录） | 文档（1 文件，+9/-5） | `cd1f644d` |

---

## 二、复盘环节

### 2.1 实施过程回顾

```mermaid
flowchart LR
    R["R 侦察<br/>断链枚举/归宿排查/双树核验"] --> I["I 根因<br/>绝对链接锚定旧位置/<br/>临时克隆债/虚构示例"]
    I --> F["修复落盘<br/>A-3 33处 + A-6 四处"]
    F --> V1["V 链接复验<br/>67 OK / 0 BROKEN"]
    V1 --> V2["audit 复扫<br/>暴露工具锚点假阳性"]
    V2 --> V3["修工具+回归测试<br/>30→32 全绿"]
    V3 --> V4["再复扫目标清零<br/>+CJK 分词修正"]
    V4 --> C["C 四次原子提交<br/>+父报告回写"]
```

| 时间 | 节点 | 关键动作 |
|------|------|---------|
| R | 事实采集 | 核验 Wiki 真实位置（8 子目录）、逐链接枚举断链、reports 双树 Test-Path 核验、jira-skill 仓库布局核验、agent-rules-skill 远程 tag 验证 |
| I | 根因分析 | 四类根因定性：迁移前绝对链接、临时克隆 source 债、虚构教学示例、根相对 source 解析失败 |
| 执行 | 修复落盘 | A-3 相对路径替换 33 处；A-6 四处编辑（md/toml 双轨） |
| V | 对抗审查 | 链接复验 67/0 → audit 复扫暴露工具缺陷 → 修复工具并补回归测试 → 再复扫目标清零 |
| C | 闭环提交 | 四次原子提交（13:11-13:15），父报告回写 |

### 2.2 关键节点分析

**节点 1：断链实测规模与登记不符（33 vs 9）**
逐链接复验确认断链为 **33 个链接、32 行、4 个文件**（[14-adversarial-review.md](../../../../knowledge/learning/03-agent-platforms-tools/01-domestic-platforms/veadk-python/supporting-analysis/14-adversarial-review.md) 12 处/11 行，其中 1 行含 2 链接；[best-practices.md](../../../../knowledge/learning/03-agent-platforms-tools/01-domestic-platforms/veadk-python/faq/best-practices.md) 11 处；[cloud-integration.md](../../../../knowledge/learning/03-agent-platforms-tools/01-domestic-platforms/veadk-python/extensions/cloud-integration.md) 6 处；[custom-run-processor.md](../../../../knowledge/learning/03-agent-platforms-tools/01-domestic-platforms/veadk-python/extensions/custom-run-processor.md) 4 处）。父报告 F-024/F-025 登记的"9 处/9 文件"来自发现阶段宽松正则加人工甄别。决策：不补绝对路径段，统一改为相对路径 `../` 形态——与 Wiki 内部既有链接约定一致，且对未来目录迁移免疫。

**节点 2：agent-rules-skill 引用归宿的排除法判定**
A-5 删除临时克隆后，[skill-intent-routing.md](../../../patterns/methodology-patterns/ai-collaboration/skill-intent-routing.md) 的 source 失归宿。逐级排查：`vendor/` 无此库；`bundles/chaos/ai-agent-skills/` 无 `libs/` 目录（含 concepts/examples/references 等，bundle 08 文档不含 agent-rules 内容）；外部仓库 `github.com/netresearch/agent-rules-skill` 经 `git ls-tree` 验证 tag `v3.14.1` 含 `skills/agent-rules/SKILL.md`。结论：采用 `external:github.com/netresearch/agent-rules-skill@v3.14.1/...` 固定 tag 引用，md 与 [.meta/toml 镜像](../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/ai-collaboration/skill-intent-routing.toml) 双轨同步。

**节点 3：V 阶段工具缺陷暴露与 TDD 修复**
audit 复扫中 [source-stability-gate.md](../../../patterns/methodology-patterns/ai-collaboration/source-stability-gate.md) L43 已修正的真实链接仍报 `❌不存在`，手动 Test-Path 为 True。代码通读定位：[check-source-path-stability.py](../../../../../.agents/scripts/check-source-path-stability.py) 的 `normalize_token` 不剥离 URI fragment，`Path("...x.py#L10").exists()` 恒为 False。修复（`split("#",1)[0]`）并新增 2 个回归测试。首版测试断言 `stability=="stable"` 失败——pytest 的 tmp_path 位于 `AppData/Local/Temp/` 下含 `Temp` 段被分类为 temporary（夹具环境特征，非代码缺陷），调试确认 exists=True 后断言改为锚定语义（`form=="link"` 且 `exists is True`）。

**节点 4：历史快照原则的边界判定**
三处"命中但不改写"：14-adversarial-review.md L155 引用 veadk 源码常量默认值 `"/tmp/veadk_local_database.db"`（审查证据，过去时态）；skill-knowledge-operation-separation.md L97/L136 引用 2026-08-25 mermaid 实验测量脚本；source-stability-gate.md 正文 `.chaos/libs`、`/tmp` 等教学反例（文档讲授对象）。

### 2.3 执行情况与结果数据

| 指标 | 数值 | 验证方式 |
|------|------|---------|
| A-3 断链修复 | 33 链接 / 32 行 / 4 文件 | 逐链接枚举；提交 e2653788 stat 33/33 |
| 修复后链接复验 | 67 OK / 0 BROKEN | 链接存在性复验脚本 |
| GATE-SPS 单元测试 | 30 → 32 全绿 | `pytest -q` 实测 |
| 全仓带锚 `file:///` 链接 | 1167 个：文件存在 568（旧逻辑假阳性）、真缺失 599 | GATE-SPS 模块全仓扫描实测 |
| 全仓不带锚链接对照 | 1913 个中 1356 个不存在 | 同上 |
| audit「不存在」基线 | 4850 → 4283（净降 567，与实测假阳性 568 互证，差 1 为剪枝口径） | 修复前后两次全量 audit |
| 原子提交 | 4 次，11 文件，+67/-43 | `git show --stat` 逐次核验 |
| 非本任务混入 | 0（工作树余并行会话 docx/子模块指针） | 提交后 `git status` 核验 |

### 2.4 成功经验

1. **相对路径方案一次到位**：33 处替换后 67/0 复验通过，相对链接对未来迁移免疫，与 Wiki 既有约定一致
2. **历史快照原则一致适用**：源码常量引用、实验测量脚本、教学反例三类"命中但不改写"判定标准统一，未过度修复
3. **TDD 自纠错迅速**：夹具环境特征导致的首次失败经一个调试脚本即定位，断言改锚语义后全绿
4. **并行会话 git 竞态纪律有效**：显式 `git add` 指定文件、index.lock 轮询不删锁、逐次 `show --stat` 核验；期间并行会话提交 `5e9c0df9` 穿插，本任务四次提交零混入

### 2.5 存在问题

| # | 问题 | 根因 | 影响 |
|---|------|------|------|
| P1 | 行动项登记规模（9 处）与实测规模（33 链接）偏差 3.7 倍 | 发现阶段宽松正则+人工甄别，验收阶段逐链接复验，跨阶段测量口径不同源 | 按登记清单点验将漏掉 3/4 真实缺陷 |
| P2 | GATE-SPS 对带锚链接系统性误报 | `normalize_token` 未覆盖 URI fragment 形态；30 个合成测试未构造锚点样本 | 568 个真实链接被恒判不存在，占修复前「不存在」基线约 12%，基线数字无法直接用于分诊 |
| P3 | TOML 镜像中 `libs/` 死路径自创建起不可达 | 元数据双轨（md/toml）影子轨无复验机制 | 镜像与源文档长期漂移而无告警 |
| P4 | 全仓存量 audit 债务数字此前不可信 | 工具假阳性未修时基线含 568 个误报 | 存量分诊（1356 不带锚缺失 + 599 带锚真缺失，大宗为 projects/xuanspace 旧机器路径）在工具修复后才首次具备可信基线 |

---

## 三、洞察环节

### 3.1 关键发现（G2 四元组）

**I-1　行动项规模登记的测量口径必须与验收口径同源**
- **陈述**：跨阶段（登记→验收）更换测量工具会产生规模漂移；行动项"已登记"不构成"规模已知"
- **证据**：父报告 F-025 登记 9 处/9 文件，逐链接复验实测 33 链接/32 行/4 文件（3.7 倍）；两阶段分别使用宽松正则人工甄别与逐链接复验
- **反常识**：行动项表给人"范围已圈定"的错觉，但发现阶段的工具精度决定登记规模的可信度；按清单点验而非全量复扫，会静默放过大部分同类缺陷
- **行动**：行动项登记必须附注测量方法与口径；验收必须用同等精度工具全量复扫（本案例 GATE-SPS audit 即为标准复扫工具），复扫结果反过来更正登记计数（父报告 F-025 已更正）

**I-2　质量门工具的假阳性与漏报同罪，且只能由真实案例校准**
- **陈述**：工具在合成测试集上全绿不等于在真实语料上判得准；未进入构造者想象空间的输入形态会形成系统性误报类
- **证据**：GATE-SPS 上线时 30 个测试全绿，但全仓 1167 个带锚链接中 568 个真实文件被恒判"不存在"；缺陷由 V 阶段一个真实修复链接（L43）触发暴露，而非由测试发现；测试夹具自身的环境特征（tmp_path 含 `Temp` 段）也是一类误报源
- **反常识**：假阳性不阻断流程（rc=1 反正拦截），却稀释信号——4850 个「不存在」中真假混杂时，真实缺陷被噪音淹没，基线数字无法支撑分诊决策；"工具能跑通"与"工具判得对"是两件独立的事
- **行动**：质量门每次在真实案例上误报/漏报，"修工具+回归测试"与"修对象"同优先级闭环（本次 `ba8272c6` 先于文档提交）；基线数字用于决策前必须经已知正负样本校准；测试断言锚定语义（exists）而非环境敏感标签（stability 分类）

**I-3　临时信源"删除前放行、引用侧失归宿"是清理流程的固有缺口；external 固定 tag 是第四级稳定归宿**
- **陈述**：存在性复验对"未来删除"零防护——引用指向磁盘上仍存在的临时克隆时全部通过，克隆一旦删除，frontmatter source 立即变死引用；归宿决策须按 bundles → vendor → external → .chaos 的排除链执行
- **证据**：A-5 删除克隆后 skill-intent-routing 的 source 失归宿，三级稳定归宿（bundles/vendor）逐一排除后 external tag v3.14.1 成为唯一可固定方案；TOML 镜像中 `libs/` 路径自创建起就不可达，影子轨从未被复验
- **反常识**：清理 SOP 的"删除前扫描零活动引用即放行"只保证删除瞬间不断链，不保证引用有稳定归宿——临时克隆承担过"唯一信源副本"角色时，删除动作把引用逼成死链或逼向 external；双轨元数据中无人复验的一轨是隐性债务
- **行动**：临时克隆清理 SOP 增补"引用归宿判定"步骤（零活动引用之外，曾被引用的克隆须在删除前完成归宿迁移或 external 固定）；GATE-SPS 扫描覆盖 `.meta/toml` 镜像轨；`external:` 固定 tag 引用形态写入信源归宿分级（bundles/ git 追踪 > vendor/ 子模块 > external: 固定 tag > .chaos/ 临时克隆）

### 3.2 规律认知

本次闭环复现并强化了一条已入库模式的运行规律：**质量门体系的有效性 = 门禁规则 × 工具判真率 × 跨阶段口径一致性**。信源稳定性门模式在三个案例（jira 案例1、veadk 主里程碑案例2、本次行动项收尾案例3）中依次暴露：引用载体多样性（链接/frontmatter/散文）→ 扫描锚点选择（特征段而非语法）→ 工具判真率（URI 形态覆盖）与口径一致性（登记/验收同源、双轨镜像复验）。缺陷逐案例向工具链下游移动，模式成熟度随验证次数累积。

### 3.3 模式成熟度更新

| 模式 ID | 成熟度 | 本次触发 | validation_count |
|---------|--------|---------|------------------|
| 信源稳定性门（source-stability-gate） | L2（维持） | 第 3 次独立验证：新增「URI fragment 锚点剥离」（工具层已实现）与「元数据双轨复验」两个检验维度 | 3（jira / veadk 主里程碑 / 本次收尾） |

### 3.4 潜在机会

- GATE-SPS 可进一步复验锚点**行号有效性**（当前只验文件存在，`#L999` 越界不告警）
- 全仓存量债务在工具修复后首次有了可信基线，具备分诊专项条件
- `external:` 固定 tag 引用形态可推广为所有"外部仓库信源"的标准归宿写法

---

## 四、导出环节

### 4.1 改进建议与行动计划

| # | 改进项 | 具体措施 | 优先级 | 验收标准 | 状态 |
|---|--------|---------|--------|---------|------|
| ACT-1 | 模式文档增补检验维度 | source-stability-gate 模式文档补「URI fragment 剥离」「TOML 镜像双轨复验」两条检验标准，validation_count 更新为 3 | 中 | 模式文档含新条目且与 GATE-SPS 实际行为一致 | ✅ 已完成 `51c8d823`（检验标准 6→8 条、反模式 5→6 条、validation_count=3） |
| ACT-2 | 锚点行号有效性复验 | GATE-SPS 对 `#Lxx` 锚点复验目标行是否越界，audit 汇总增加越界计数 | 低 | 回归测试覆盖越界锚点；audit 输出含行号越界分类 | ✅ 已完成 `a2e37b25`（工具+4 测试，32→36 全绿）+ `5207d558`（10 处真实越界修复，anchor_oob 10→0） |
| ACT-3 | 全仓存量债务分诊 | 对 1356 个不带锚缺失 + 599 个带锚真缺失（大宗为 projects/xuanspace `d:/spaces` 旧机器路径）按历史快照原则批量甄别 | 低 | 分诊结论登记；活动文档真缺失清零或转行动项 | ✅ 已完成 `b8d4d2a0`（[分诊报告](source-path-debt-triage-audit-20260829.md)：A 类约 2,750/B 类约 1,050 不改写、C 类约 200 登记 backlog、D-1~D-5 活动债务登记分批修复） |
| ACT-4 | ai-multimodal TOML 镜像死引用 | 补建 ai-multimodal-fullstack-dev-loop.toml 镜像或登记 x-toml-ref 死引用 | 低 | x-toml-ref 解析有效或死引用在册 | ✅ 已完成 `96758a4c`（镜像补建，x-toml-ref 解析有效，fix-x-toml-ref dry-run 确认） |

### 4.2 关键提交索引

| Commit | 类型 | 内容 |
|--------|------|------|
| `ba8272c6` | fix(scripts) | GATE-SPS normalize_token 剥离片段锚点 + 2 回归测试（30→32） |
| `e2653788` | docs(wiki) | A-3：veadk Wiki 33 处断链相对路径化 + CJK 分词歧义修正 |
| `1f4a3dfc` | docs(patterns) | A-6：external tag 引用、教学示例真实路径、source 相对路径修正（md/toml 双轨） |
| `cd1f644d` | docs(retrospective) | 父里程碑报告 A-3/A-6 闭环回写、F-025 计数更正 |
| `41a6a291` | docs(retrospective) | 本复盘报告归档与里程碑索引登记 |
| `51c8d823` | docs(patterns) | ACT-1：信源稳定性门模式第 3 次验证回灌（检验标准 6→8、反模式 5→6、案例 3） |
| `a2e37b25` | feat(scripts) | ACT-2：GATE-SPS 行号锚点越界复验 + 4 回归测试（32→36） |
| `5207d558` | fix(wiki) | ACT-2：vendor tag 1.0.10 固定后 10 处行号锚点越界修正（anchor_oob 10→0） |
| `b8d4d2a0` | docs(retrospective) | ACT-3：全仓信源路径存量债务分诊审计报告与索引登记 |
| `96758a4c` | fix(patterns) | ACT-4：补建 ai-multimodal-fullstack-dev-loop TOML 镜像，x-toml-ref 死引用闭环 |

### 4.3 后续优化方向

本次为父里程碑的收尾闭环，6 项行动项（A-1 至 A-6）与本报告登记的 4 项行动项（ACT-1 至 ACT-4）均已全部完成（提交哈希见 4.2）。模式资产侧，信源稳定性门模式完成第 3 次独立验证沉淀（检验标准 8 条、反模式 6 条、validation_count=3）；工具侧，GATE-SPS 具备锚点剥离与行号越界复验双重能力，单元测试 36 全绿、全仓 anchor_oob=0。后续工作以 [ACT-3 分诊报告](source-path-debt-triage-audit-20260829.md) 登记的 D-1~D-5 活动信源债为队列（knowledge d:/spaces 265 条、tuya-iot 临时克隆 269 条、.chaos 139 条、C:/Users 129 条、xuanspace 子模块 76 条），按优先级分批修复；其中 **D-1 已于 2026-08-29 闭环**（提交 `685506db`，45 个活动教程文档逐文档语义核验修复，复扫活动文档 spaces 令牌清零、anchor_oob=0、36 测试全绿；根 `docs/` 空壳旧树 116 条登记 deprecated 不改写，详见分诊报告第六章），队列剩余 D-2~D-5；C 类约 200 条工具误报进入 GATE-SPS backlog（CJK 伪 token 识别、prose 行号后缀甄别）。

---

> **报告编制**：本文档基于会话执行记录、git 提交历史与 GATE-SPS 实测数据编制，全部数字均经命令复核（提交统计、pytest、全仓锚点扫描、修复前后双次 audit）。报告遵循"事实 → 分析 → 洞察 → 建议"结构，事实阶段不含因果判断。
