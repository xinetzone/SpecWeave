---
id: "subagent-wiki-delivery-checklist"
title: "Wiki子代理委派与产出验收检查清单"
source: "retrospective-mopmonk-wiki-20260704, retrospective-sunlogin-camera-su1-wiki-20260704"
x-toml-ref: "../../.meta/toml/.agents/templates/subagent-wiki-delivery-checklist.toml"
---
# Wiki子代理委派与产出验收检查清单

> 基于MopMonk、text-to-cad和向日葵SU1摄像头等多次wiki教程任务复盘萃取，用于防止frontmatter格式错误、TOML路径错误、三级标题编号不规范、参数遗漏等重复问题。
> 使用方法：委派wiki创作子代理时，将本清单的【强制前置步骤】和【交付前自检】嵌入任务描述末尾；子代理交付后，主代理按【主代理验收7点检查】逐项验证。

---

## 📋 强制前置步骤（子代理任务开始前必须执行）

> **在生成任何文件之前，必须先完成以下步骤，不得跳过。**

### 步骤0：确认wiki类型

根据任务描述中的原子化决策，确定本次wiki类型：
- **单文件wiki**：所有内容在一个.md文件中，不创建子目录
- **原子化wiki**：拆分为索引页+子目录+数字前缀原子文件

```
【强制前置步骤 - 开始任务前必须执行】

0. 确认wiki类型（根据spec.md中的原子化决策）：
   - 单文件wiki：frontmatter仅含4个字段：title、source、date、tags（禁止添加author/version/category等额外字段）
   - 原子化wiki：frontmatter仅含4个字段：id、title、source、x-toml-ref（禁止添加date/tags/category等应在TOML中的字段）

1. 读取参考文件确认格式（禁止凭记忆决定格式）：
   - 单文件wiki参考：docs/knowledge/learning/sunlogin-security-wiki.md
   - 原子化wiki参考：docs/knowledge/learning/mopmonk-security-agent-wiki/00-overview.md
   - 确认以下格式细节（必须以实际文件为准，不是模板/记忆为准）：
     * frontmatter分隔符：使用 --- （YAML格式），不是 +++ （TOML格式）
     * frontmatter字段：严格按照步骤0的类型对应4个字段，不多不少
     * 三级标题编号：单文件wiki中格式为"x.y"（如1.1、2.3），从x.1开始连续编号，禁止使用x.0
     * x-toml-ref路径（仅原子化wiki）：原子文件用 ../../../../.meta/toml/...（4层上级），索引页用 ../../../.meta/toml/...（3层上级）
     * 文件命名：kebab-case、纯英文、原子文件使用两位数字前缀（00-、01-...）

2. 确认目录结构：
   - 单文件wiki索引页：docs/knowledge/learning/{{wiki-name}}.md（无子目录，无TOML文件）
   - 原子化wiki索引页：docs/knowledge/learning/{{wiki-name}}.md
   - 原子化wiki原子目录：docs/knowledge/learning/{{wiki-name}}/
   - TOML位置（仅原子化wiki）：.meta/toml/docs/knowledge/learning/{{wiki-name}}/NN-xxx.toml

3. 确认frontmatter格式（严格按类型）：

单文件wiki标准模板（4字段，禁止添加额外字段）：
---
title: "{{中文完整标题}}"
source: "{{原始URL或来源描述}}"
date: "{{YYYY-MM-DD}}"
tags: ["tag1", "tag2", "..."]
---

原子化wiki标准模板（4字段）：
---
id: "{{wiki-name}}-xxx"
title: "{{章节标题}}"
source: "{{来源URL或父文件路径}}"
x-toml-ref: "{{正确计算的相对路径}}"
---
```

---

## ✅ 交付前自检清单（子代理交付前必须逐项检查）

子代理完成内容创作后，在标记任务完成之前，必须逐项自检：

- [ ] **分隔符检查**：所有.md文件frontmatter使用`---`（YAML），没有使用`+++`（TOML）
- [ ] **frontmatter字段检查**：严格按照wiki类型使用4个字段，无多余字段（单文件：title/source/date/tags；原子化：id/title/source/x-toml-ref）
- [ ] **x-toml-ref路径验证**（仅原子化wiki）：每个文件的x-toml-ref指向的TOML文件路径层级正确（数清楚`../`层数）
- [ ] **文件命名检查**：文件名纯英文、kebab-case、无中文、原子文件两位数字前缀
- [ ] **source字段存在**：派生产物有source溯源字段指向原始URL或父文件
- [ ] **标题层级检查**：每个文件第一行是`# 标题`（h1），没有跳级（h1→h3）
- [ ] **三级标题编号检查**（单文件wiki）：三级标题从x.1开始连续编号（如1.1、2.1），无x.0编号
- [ ] **参数完整性检查**（硬件/产品类wiki）：对照原始数据源逐一核对参数表，确保无遗漏参数
- [ ] **TOML文件已创建**（仅原子化wiki）：.meta/toml/镜像路径下有对应的.toml文件
- [ ] **无多余字段**：YAML frontmatter中没有author/version/category等不应出现的字段

---

## 🔍 主代理验收7点检查（接收子代理产出时必须执行）

> 主代理收到子代理产出后，**不要直接信任**，必须在30秒内完成以下7点检查：

| # | 检查项 | 检查方法 | 失败处理 |
|---|--------|---------|---------|
| 1 | **frontmatter分隔符正确** | 打开第一个文件，看前3行：必须是`---`开头，不能是`+++` | 立即修正，通知子代理错误 |
| 2 | **frontmatter字段类型正确且无多余** | 单文件wiki：仅title/source/date/tags；原子化wiki：含id/title/source/x-toml-ref | 删除多余字段或补全缺失字段 |
| 3 | **x-toml-ref路径合理**（仅原子化） | 检查frontmatter中是否有x-toml-ref字段，`../`层数是否正确 | 修正路径，必要时用fix-x-toml-ref.py |
| 4 | **标题层级从h1开始** | 文件第一行标题是`# `开头，不是`## ` | 修正标题层级 |
| 5 | **文件名合规** | 检查文件名：kebab-case、纯英文、数字前缀正确 | 重命名文件 |
| 6 | **source溯源字段存在** | frontmatter中有source字段指向原始来源 | 添加source字段 |
| 7 | **三级标题编号规范**（单文件wiki） | 三级标题从x.1开始，无x.0编号 | 修正编号 |

**验收通过标准**：7项全部通过，才能继续后续工作（原子化/提交/收尾）。
**验收耗时**：每个文件10秒，全套检查不超过1分钟。
**拦截率**：可拦截80%以上的低级格式错误（基于三次复盘数据）。

---

## 📝 子代理任务描述模板（可直接复制使用）

委派wiki创作任务时，在任务描述末尾附加以下内容：

```
【重要 - 格式要求 - 必须遵守】

0. 确认wiki类型：{{单文件wiki / 原子化wiki}}（根据spec.md决策）

1. 开始写文件之前，必须先读取以下文件确认实际格式（禁止凭记忆写frontmatter）：
   - 单文件wiki参考：docs/knowledge/learning/sunlogin-security-wiki.md
   - 原子化wiki参考：docs/knowledge/learning/mopmonk-security-agent-wiki/00-overview.md

2. frontmatter必须使用YAML格式（---分隔），禁止使用TOML格式（+++分隔）

3. frontmatter字段严格按照wiki类型使用，禁止添加额外字段：
   - 单文件wiki：title、source、date、tags（4个，禁止author/version等）
   - 原子化wiki：id、title、source、x-toml-ref（4个）

4. 三级标题编号规范（单文件wiki）：使用"x.y"格式（如1.1、2.3），从x.1开始连续编号，禁止使用x.0

5. 文件命名：kebab-case、纯英文无中文，原子文件使用两位数字前缀（00-、01-...）

6. 交付前请按"子代理交付前自检清单"逐项检查：
   - 分隔符是否为---
   - frontmatter字段是否为类型对应的4个且无多余
   - x-toml-ref路径是否正确（仅原子化）
   - 文件名是否合规
   - source字段是否存在
   - 标题是否从h1开始
   - 三级标题编号是否从x.1开始（单文件wiki）
```

---

## 🔗 关联参考

- [wiki-spec-template.md](wiki-spec-template.md) - Wiki教程制作完整工作流模板（含四层漏斗模型、8章节结构、DoD完成定义）
- [document-governance-checklist-template.md](document-governance-checklist-template.md) - 文档治理通用Checklist
- [retrospective-mopmonk-wiki-20260704](../../../docs/retrospective/reports/competitive-analysis/retrospective-mopmonk-wiki-20260704/) - 本清单的来源复盘报告（MopMonk）
- [retrospective-sunlogin-camera-su1-wiki-20260704](../../../docs/retrospective/reports/competitive-analysis/retrospective-sunlogin-camera-su1-wiki-20260704/) - 编号规范/参数检查改进来源（SU1摄像头）
