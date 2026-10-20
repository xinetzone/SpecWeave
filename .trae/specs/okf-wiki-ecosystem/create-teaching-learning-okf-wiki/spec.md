---
title: "「教与学」全面调研 → OKF Wiki 教程"
status: "draft"
version: "1.0"
methodology: "seven-concepts（场景4 知识沉淀：R→I→E，叠加 F 本质剖析 + V 对抗审查）"
content-sensitivity: "public"
---

# 「教与学」全面调研 → OKF Wiki 教程 Spec

## Why

"教与学"是教育的第一性问题，也是每个个体终身面对的问题。本项目已有 feynman-ai-learning（费曼学习法+AI，以教促学）束，但缺少对"教与学"主题本身的概念性、本质性系统化梳理。本任务用七概念方法论对"教与学"做全面调研与分析：它们是什么（定义谱系）、怎么做（教学法与学习科学）、本质是什么（第一性原理）、区别与联系（教学相长）、真问题真目标真需求（动机与 AI 时代变革），沉淀为 awesome-okf-xs 文档库中的系统化 OKF Wiki 教程，与 methodology 分组现有「费曼学习法+AI」「第一性原理」构成"学的方法论 → 教与学本质"的知识闭环。

## 内容敏感度预检（阶段 0）

- 调研对象：公开学术文献、公开文章、经典著作原文（《学记》《论语》）、政府/学术机构网站（教育部、中国教科院、北师大）→ **公开内容（Public）**
- 标准工作流：spec 位于 `.trae/specs/okf-wiki-ecosystem/`，产出物位于 `projects/awesome-okf-xs/doc/bundles/`

## 信源距离预判

- 多源综合调研（非单篇转化）：经典原著与学术机构原文为一级信源（《礼记·学记》原文、教育部引例、北师大学习元社区、NTU/Manchester 学习科学页面）；百科与二手解读仅作线索，关键声明回到一级信源
- AI 时代观点（院士/研究院/媒体笔谈）一律标注为"观点/一方称"，不当作已验证事实
- 学习科学循证策略标注证据来源（机构页面/综述），不夸大效应量

## 骨架判定（操作可复现性两问）

| 判据 | 结论 |
|------|------|
| ① 是否有读者可照做的流程？ | 有——教学法选型对照、学习策略实操（检索练习/间隔重复/费曼）、教与学自查清单均可直接复现 |
| ② 是否有步骤顺序/输入输出？ | 有——各教学法/学习策略均有公开的标准步骤与产出物 |

两问均为"是" → 设 **examples/**（实操层）。骨架：index + concepts/（9 篇）+ examples/（3 篇）+ references/（4 篇）+ log.md。

## 归属判定

**结论：`zhexue/methodology/teaching-and-learning/`**

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `zhexue/methodology/`（选定） | ✅ | 分组描述为"思维模型、学习方法论及相关实践指南"；同组 feynman-ai-learning 正是"以教促学"的直接案例，first-principles 提供本质剖析方法；教与学的概念与本质探索属方法论范畴 |
| `sheke/personal-growth/` | ❌ | 该组偏个人成长实操应用（15 束已饱和），本束是概念—本质层的综合主题，非技巧清单 |
| `sheke/` 新建 education 分组 | ❌ | 单束新建分组属过度工程；且学记/孔子思想已有 guoxue 域，本束是跨中西的现代主题综合，归国学亦不适 |
| `guoxue/` | ❌ | 学记/论语精读属国学经典层，本束是教与学的现代系统化综述，仅引用其原文，不承载经典精读功能 |

## What Changes

- 新增 spec：`.trae/specs/okf-wiki-ecosystem/create-teaching-learning-okf-wiki/`（spec.md + tasks.md）
- 新增 OKF bundle：`projects/awesome-okf-xs/doc/bundles/zhexue/methodology/teaching-and-learning/`（约 19 文件）
- 更新 `zhexue/methodology/index.md`：total_bundles 3→4、toctree 追加、知识包列表表加行
- 更新 `zhexue/index.md`：methodology 行束数与域说明同步（需读取现状后精确修订）
- 更新 `bundles/index.md`：total_bundles 650→651、mermaid zhexue 7→8、哲学域节 7→8、methodology 行束数 3→4
- **BREAKING**：无破坏性变更（纯新增）

## Impact

- Affected specs：无（独立新增）
- Affected code：`projects/awesome-okf-xs/doc/bundles/` 下新增 1 束 + 三级索引 3 处修改（awesome-okf-xs 为第一方 git submodule，在子模块内开发与提交）

## ADDED Requirements

### Requirement: 概念文档层（concepts/，9 篇）

| 内容层 | 映射篇目 |
|--------|---------|
| 教是什么：定义谱系（共同活动论/教学即教学生学/学重于教）+ 第一性原理 | `00-what-is-teaching.md` |
| 学是什么：定义谱系（行为改变/认知建构/关系中的自我改变）+ 学习三要素 | `01-what-is-learning.md` |
| 学习理论谱系：行为主义→认知主义→建构主义→社会文化理论→深度学习 | `02-learning-theory-spectrum.md` |
| 教学法流派与实践：讲授/苏格拉底/建构主义三法/项目式/探究式/翻转课堂，各法适用边界 | `03-teaching-methods.md` |
| 学习科学循证策略：检索练习/间隔/交错/样例/主动学习/认知负荷管理 | `04-evidence-based-learning.md` |
| 教与学的关系：区别（无教可学/有教未必学）、联系（教以学为归宿）、教学相长（学记+费曼） | `05-teaching-learning-relationship.md` |
| 第一性原理：教与学的本质——学的不可代理性、教的条件创设性、输出驱动输入的合流 | `06-first-principles-essence.md` |
| 真问题真目标真需求：动机（SDT 自主/胜任/归属）、教与学脱节、评估错位、学会学习 | `07-real-needs-and-goals.md` |
| AI 时代的教与学：知识通胀/认知外包/流畅陷阱/能力转向/提问与反思 | `08-ai-era-transformation.md` |

### Requirement: 实操层（examples/，3 篇）

- `01-teaching-method-selection.md`：教学法选型对照表（目标×学习者×场景→方法，含各法失效条件）
- `02-learning-strategy-playbook.md`：学习策略实操手册（检索练习/间隔重复/费曼讲解/主动回忆的具体执行步骤）
- `03-teaching-and-learning-self-check.md`：教与学自查清单（教者自问"是否促成学"，学者自问"学是否真实发生"）

### Requirement: 信源层（references/，4 篇）

- `01-chinese-pedagogy-sources.md`：中国教学论信源谱系（《学记》原文引例/孔子/叶圣陶/谢维和，含 URL）
- `02-western-philosophy-sources.md`：西方教育哲学信源（杜威教育本质论/卢梭自然教育/教育定义）
- `03-learning-science-sources.md`：学习科学信源（NTU/Manchester/北师大认知神经/认知负荷/浙大讲座）
- `04-ai-era-sources.md`：AI 时代信源（郭毅可/张雨东/中国教科院/教育部行动计划，标注观点属性）

### Requirement: 研究产物（bundle 根）

- `index.md`：bundle 根索引（frontmatter 含 `okf_version: "0.2"`，toctree 覆盖全部内容文档，含概念表与关键洞察）
- `log.md`：更新历史（YYYY-MM-DD 倒序）

### Requirement: 状态与时效

- `status: stable`——核心概念与经典理论跨周期有效，多源互证
- `stale_after: 2027-10-01`——概念层跨周期；AI 时代观点与政策标注时点

## 约束

- 所有具体声明引用 sources 脚注或 references 信源；《学记》《论语》原文标注篇目出处
- 不替任何教学法/学习理论宣称普适有效性；每法标注适用边界与失效条件
- AI 时代"观点类"内容明确标注"一方称/观点"属性，不当作已验证事实
- 交叉引用使用相对路径，禁止 `file:///`；正文中文，文件名 kebab-case 纯英文
- 遵循 awesome-okf-xs AGENTS.md：新增 bundle 后必跑 `invoke gates.toctrees` 与 `invoke gates.bundles`（计数五面对账），构建验证 `invoke build`

## Acceptance Criteria

### AC-1: bundle 结构与 toctree 完整
- **Type**: `rule`
- **Given**: bundle 已落盘 `zhexue/methodology/teaching-and-learning/`
- **When**: 运行 `invoke gates.toctrees`
- **Then**: 全部内容文档被 toctree 覆盖，无断链告警
- **Pass Condition**: 命令退出码 0 且无本束相关告警
- **Evidence**: 质量门输出

### AC-2: frontmatter 合规与计数对账
- **Type**: `rule`
- **Given**: bundle 与三级索引已更新
- **When**: 运行 `invoke gates.bundles`
- **Then**: 每个非保留 .md 含可解析 frontmatter 且有非空 `type`；bundles 总计数 650→651 五面对账一致
- **Pass Condition**: 命令退出码 0
- **Evidence**: 质量门输出

### AC-3: Sphinx 构建通过
- **Type**: `rule`
- **Given**: bundle 落盘完成
- **When**: 运行 `invoke build`（或 `sphinx-build -b dummy`）
- **Then**: 构建成功且无本束引入的 ERROR
- **Pass Condition**: 构建退出码 0，日志无本束文件相关 ERROR
- **Evidence**: 构建日志

### AC-4: 概念覆盖度
- **Type**: `rubric`
- **Dimension**: 主题覆盖完整性（教/学/理论谱系/教学法/循证策略/关系/本质/真需求/AI 时代 9 大主题）
- **Scale**: 1-5
- **Anchors**: 1 = 覆盖 ≤4 主题；3 = 覆盖 7 主题且至少 5 篇有信源；5 = 9 主题全覆盖、每篇有信源且跨中西双谱系
- **Pass Threshold**: >= 4
- **Evidence**: concepts/ 文件清单与信源引用核对

### AC-5: 事实溯源
- **Type**: `rule`
- **Given**: 读者抽查具体声明（《学记》原文、经典引语、关键事实）
- **When**: 核对原文与来源
- **Then**: 均带 sources 脚注或 references 信源，可在 references/ 查到出处
- **Pass Condition**: 抽查 5 处声明全部可溯源
- **Evidence**: 抽查记录

### AC-6: 本质洞察深度
- **Type**: `rubric`
- **Dimension**: 第一性原理论证质量（学的不可代理性、教的条件创设性、教学相长/输出驱动合流三论）
- **Scale**: 1-5
- **Anchors**: 1 = 仅罗列定义；3 = 提出单一本质命题；5 = 三重命题互相咬合、含对抗审查视角（含"教学相长非自动发生"的反例边界）
- **Pass Threshold**: >= 4
- **Evidence**: `06-first-principles-essence.md` 与 `05-teaching-learning-relationship.md` 内容

### AC-7: 可操作性
- **Type**: `rule`
- **Given**: 读者带着真实教/学场景
- **When**: 使用 examples/ 三篇
- **Then**: 可直接照做教学法选型、学习策略与自查清单，无需额外补全步骤
- **Pass Condition**: 三篇均含步骤或清单式可执行内容
- **Evidence**: examples/ 文件检查

### AC-8: 三级索引计数一致
- **Type**: `rule`
- **Given**: 索引更新完成
- **When**: 核对 bundles/index.md、zhexue/index.md、zhexue/methodology/index.md
- **Then**: 计数一致（651 / zhexue 8 / methodology 4），导航表含新束条目
- **Pass Condition**: 三处计数与目录树实际一致
- **Evidence**: 文件核对

### AC-9: 命名与语言规范
- **Type**: `rule`
- **Given**: bundle 落盘完成
- **When**: 检查文件名与正文
- **Then**: 文件名 kebab-case 纯英文，正文中文，保留文件名（index/log）用途正确
- **Pass Condition**: 检查通过
- **Evidence**: 文件清单检查

## Open Questions

- [ ] 是否单独设"学习动机"独立篇？（倾向：并入 07 真需求篇，避免概念重复）
- [ ] 是否纳入脑神经机制细节？（倾向：references 信源提及，concepts 不做 deep dive，避免与 kexue 域重复）

<!-- changelog -->
<!--
- 2026-10-20 | initial | 七概念（I→F→V→E）全面调研「教与学」→ OKF Wiki 教程
-->
