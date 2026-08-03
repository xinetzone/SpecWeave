---
id: "bp-tech-article-to-wiki-batch"
title: "技术文章Wiki化批量生成模式"
type: "process"
date: "2026-08-03"
maturity: "L2-validated"
source: "七概念方法论编排·里程碑复盘(sc-20260803-harness-wiki)"
related_patterns: ["bp-subagent-std"]
tags: ["wiki", "knowledge-management", "subagent", "batch-generation", "quality-gates", "defuddle", "docgen", "link-checking", "harness-engineering"]
validation_count: 5
reuse_count: 5
documentation_level: "complete"
abstract_level: "L3-process"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/tech-article-to-wiki-batch-generation.toml"
---

# 技术文章Wiki化批量生成模式（Technical Article to Wiki Batch Generation）

## 模式概述

将一篇长技术文章/教程/深度分析（预计800行以上、包含多个独立可引用章节）高效转化为原子化Wiki结构的标准化8步流程模式。核心思想是：**充分Spec约束下子代理可批量高质量生成原子文件，自动化工具链负责元数据/索引/格式修复，链接检查是不可跳过的最后质量门禁**。

## 触发场景

- 当需要将一篇长技术文章/微信公众号文章/技术博客/行业报告转化为团队内部可复用的原子化Wiki结构时
- 适用于：技术概念学习、方法论沉淀、工具教程、行业趋势分析、产品哲学解读等需要章节独立引用的知识沉淀场景
- 不适用于：短篇文章（<500行，无需原子化拆分）、创意写作（标准化流程会限制创造力）、实时性强的新闻资讯（无需沉淀为结构化Wiki）

## 核心做法（8步标准化流程）

### 步骤1：Spec先行
- 撰写完整的spec.md（PRD格式），包含Overview/Goals/章节划分表/原子化决策/DoD标准
- 章节划分表明确每个原子文件的三要素：**文件名**（kebab-case，数字前缀）、**标题**、**核心内容**
- 参考已有Wiki的frontmatter格式和章节结构
- 验收标准使用Given/When/Then格式，区分programmatic和human-judgment验证类型

### 步骤2：任务拆解
- 撰写tasks.md，按线性依赖顺序拆分为10-16个Task
- 每个Task包含：Description、Acceptance Criteria Addressed、Test Requirements
- **最后3个Task固定为**：元数据自动化修复 → 格式验证（文件名/链接/frontmatter）→ 原子提交
- 索引页创建合并到Task 1，不单独作为后期完善Task

### 步骤3：验收清单
- 撰写checklist.md，包含7大类检查项：
  1. 格式规范（frontmatter/YAML/x-toml-ref/h1标题/文件名）
  2. 内容完整性（章节覆盖/数据准确性/来源标注）
  3. 结构完整性（导航表/术语表/阅读路径）
  4. 子代理5点强制验收（YAML分隔符/x-toml-ref路径/h1标题/文件名kebab-case/source字段）
  5. 自动化验证（TOML创建/文件名规范/链接检查）
  6. 索引更新
  7. 提交验证

### 步骤4：内容提取
- 使用**defuddle**工具提取原始网页内容（`defuddle parse <url> --md`）
- WebFetch失败时defuddle是可靠备选方案
- PowerShell下注意URL含`&`参数时需引号包裹，或截断到`?`前的主URL
- 检查输出内容而非仅看exit code（非零退出码不等于内容提取失败）

### 步骤5：批量生成
- 调用general_purpose_task子代理**一次性**生成所有原子文件（10个左右）
- 子代理prompt中必须传入：
  - 完整spec文档内容
  - 章节划分表（文件名+标题+核心内容三要素）
  - **5点强制验收标准**（显式列出，反模式警告）
  - **现有wiki文件名清单**（避免引用不存在的文件）
  - frontmatter格式示例（YAML ---，严禁+++ TOML）
  - 内部wiki链接必须指向*-wiki.md索引页而非原子文件的明确说明
- **不要逐文件生成验证**——批量生成在完整spec约束下质量更高，逐文件生成丢失全局上下文一致性

### 步骤6：自动化修复
- 运行 `python .agents/scripts/fix-x-toml-ref.py --dir <wiki-dir>/ --write --create-toml`：
  - 自动创建TOML元数据骨架文件
  - 自动修复x-toml-ref路径层级
- 运行 `python .agents/scripts/docgen.py nav`：
  - 自动更新docs/knowledge/README.md索引
  - 不需要手动编辑README或手动计算../层级

### 步骤7：质量门禁（三道关卡）
1. **文件名规范**：`python .agents/scripts/check-filename-convention.py --directory <wiki-dir>/`
2. **链接检查**（最关键！）：`python .agents/scripts/check-links.py --path <wiki-dir>/`
   - **修复断链后必须重跑确认零断链**
   - 重点检查内部wiki链接是否指向*-wiki.md索引页而非子目录原子文件
3. **frontmatter格式**：`python .agents/scripts/check-frontmatter.py --dir <wiki-dir>/`
   - 0错误即可通过，category/date迁移到TOML的警告不影响验收

### 步骤8：原子提交
- 显式 `git add` 每个相关文件（**禁止git add .**）
- 使用 `python .agents/scripts/git-commit-utf8.py -m "type(scope): 中文描述"` 处理Windows中文编码
- Commit message遵循Conventional Commits：`docs(learning): ...`
- scope以实际目录分类为准（learning/knowledge/patterns等），计划时留有余地

## 反模式（不要这么做）

- ❌ **逐文件生成验证**：生成一个文件检查一个再生成下一个——子代理在有完整spec约束时批量生成质量更高，逐文件生成丢失全局上下文一致性，且效率极低
- ❌ **手动编辑索引和README**：手动更新docs/knowledge/README.md或手动计算x-toml-ref的../层级——自动化工具更可靠，手动操作容易引入路径错误，且docgen能自动完成
- ❌ **跳过链接检查**：认为"内容正确链接就不会错"——原子化拆分后跨文件引用是最高发问题点，子代理缺乏完整目录存在性信息，链接问题在逐文件内容审核中极易被忽略
- ❌ **不提供frontmatter格式示例**：仅靠文字描述"使用YAML"不足以保证子代理格式正确——必须在prompt中提供具体格式示例+"严禁使用TOML(+++)"的反模式警告
- ❌ **不提供现有wiki文件清单**：子代理可能引用不存在的wiki文件（如本次zleap-agent-harness-learning-analysis.md问题）——必须在prompt中提供现有wiki文件名列表
- ❌ **git add .提交**：会把临时文件、无关修改一并提交——必须显式指定每个文件

## 检验标准

做完之后怎么知道做对了？

- **标准1（批量生成质量）**：子代理一次性生成的原子文件5点验收首次通过率≥90%，仅链接层面可能存在问题
- **标准2（零断链）**：check-links.py最终检查结果为0个本地断链，内部wiki链接均指向*-wiki.md索引页
- **标准3（文件名合规）**：check-filename-convention.py检查通过，所有文件kebab-case+数字前缀
- **标准4（索引自动更新）**：docs/knowledge/README.md通过docgen自动更新，无手动编辑痕迹
- **标准5（提交单一职责）**：git commit只包含本次wiki相关文件，无无关文件混入
- **标准6（TOML完整）**：fix-x-toml-ref.py为每个md文件创建了对应的TOML骨架文件

## 迁移示例

这个模式还能用在什么其他场景？

- **场景1（技术博客→API文档）**：defuddle提取开源项目博客 → Spec定义API文档章节 → 子代理批量生成API参考 → 自动化工具链接检查 → 提交
- **场景2（行业报告→分析Wiki）**：defuddle提取行业分析报告 → Spec定义分析维度章节 → 子代理批量生成分析章节 → 数据准确性校验 → 提交
- **场景3（开源README→中文教程）**：defuddle提取GitHub README → Spec定义教程章节（快速开始/安装/配置/示例/FAQ）→ 子代理批量生成教程 → 链接检查 → 提交
- **场景4（会议演讲→学习笔记Wiki）**：defuddle提取演讲文字稿/幻灯片 → Spec定义笔记章节 → 子代理批量生成笔记 → 格式验证 → 提交

## 验证案例

| 案例编号 | 任务 | 验证日期 | 结果 |
|---------|------|---------|------|
| harness-wiki | Harness Engineering系统性学习Wiki（10原子文件，1111行） | 2026-07-04 | ✅ 5点验收首次通过，1个断链修复后零问题 |
| four-engineering | 四大工程概念Wiki教程 | 2026-07-04 | ✅ 流程验证通过，子代理首次即正确使用YAML |
| longcat-agent | LongCat Agent/Loop Engineering学习Wiki | 2026-07 | ✅ 模式复用成功 |
| mopmonk-security | MopMonk多Agent安全护栏Wiki | 2026-07 | ✅ 模式复用成功 |
| rainman-book | RainMan翻译书籍Wiki | 2026-07 | ✅ 模式复用成功 |

## 配套工具清单

| 工具 | 路径 | 用途 |
|------|------|------|
| defuddle | `npx defuddle parse <url> --md` | 网页内容提取 |
| fix-x-toml-ref | `.agents/scripts/fix-x-toml-ref.py` | TOML创建+x-toml-ref路径修复 |
| docgen | `.agents/scripts/docgen.py nav` | 文档导航表自动生成 |
| check-filename-convention | `.agents/scripts/check-filename-convention.py` | 文件名规范检查 |
| check-links | `.agents/scripts/check-links.py` | Markdown链接有效性检查 |
| check-frontmatter | `.agents/scripts/check-frontmatter.py` | frontmatter格式验证 |
| git-commit-utf8 | `.agents/scripts/git-commit-utf8.py` | Windows中文安全提交 |

## 与现有模式的关系

- **本模式是[子代理标准化指令模式](subagent-standardized-instruction.md)（bp-subagent-std）在"网页→Wiki"垂直场景的具体化**
- bp-subagent-std提供子代理指令的通用结构原则，本模式提供Wiki创建场景的具体8步流程和工具链
- 本模式的"5点强制验收+格式示例+反模式警告"做法是对bp-subagent-std"内嵌验收标准"原则的最佳实践补充

## 演进历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-07-04 | 四大工程概念Wiki复盘首次萃取5步流程 |
| v2.0 | 2026-08-03 | Harness Engineering Wiki复盘升级为8步流程，增加验收清单、三道质量门禁、链接检查修复后重跑、现有wiki文件清单等关键步骤 |

## 关联资源

- [Harness Engineering Wiki里程碑复盘报告](../../reports/milestone/harness-engineering-wiki-retrospective-20260803.md)
- [四大工程概念Wiki里程碑复盘](../../reports/milestone/four-engineering-concepts-wiki-retrospective-20260704.md)
- [子代理分析任务标准化指令模式](subagent-standardized-instruction.md)
- 子代理Wiki交付检查清单：[`.agents/templates/subagent-wiki-delivery-checklist.md`](../../../../.agents/templates/subagent-wiki-delivery-checklist.md)
