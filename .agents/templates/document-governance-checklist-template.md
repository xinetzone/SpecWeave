---
id: "document-governance-checklist-template"
title: "文档治理Checklist模板"
source: "insight-extraction.md#4-可迁移性评估"
x-toml-ref: "../../.meta/toml/.agents/templates/document-governance-checklist-template.toml"
version: "1.2.0"
patterns_applied: ["three-tier-governance", "entry-container-separation", "meta-document-leverage", "spec-triple-sync"]
---
# 文档治理Checklist模板

> 基于frontmatter元数据统一复盘中萃取的**3项核心原则**、**3项架构模式**和**5项实践经验**，用于新建文档、原子化拆分、批量迁移时的质量门禁检查。
>
> **L3标准化模式集成**：本模板已应用以下L3标准化模式——
> - [three-tier-governance](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-tier-governance.md)：三层治理闭环（原子化→自动化→验证）
> - [entry-container-separation](../../docs/retrospective/patterns/methodology-patterns/document-architecture/entry-container-separation.md)：入口-容器二元架构
> - [meta-document-leverage](../../docs/retrospective/patterns/methodology-patterns/document-architecture/meta-document-leverage.md)：元文档杠杆效应

## 使用方法

1. 复制本Checklist到任务说明或PR描述中
2. 按场景选择检查项（新建文档/原子化拆分/批量迁移/规范发布）
3. 所有适用项打勾后方可提交
4. 工具类检查项可通过自动化脚本完成（见工具清单）

---

## 📋 文档治理Checklist

### 一、Frontmatter合规检查

**自动化工具**：`python .agents/scripts/check-frontmatter.py --file <path>`

- [ ] **四字段结构**：frontmatter包含且仅包含 `id`、`title`（可选，TOML优先）、`source`（派生产物必填）、`x-toml-ref` 四个字段
- [ ] **id命名规范**：kebab-case格式（`^[a-z][a-z0-9]*(-[a-z0-9]+)*$`）
- [ ] **扁平结构**：YAML中无多行缩进嵌套（列表/字典），所有值为标量
- [ ] **无禁止字段**：YAML中不包含 `category`/`date`/`tags`/`version`/`changelog`（这些字段应在TOML中）
- [ ] **x-toml-ref路径正确**：指向的TOML文件存在，相对路径层级正确（可用 `fix-x-toml-ref.py` 自动修复）
- [ ] **source溯源完整**：派生产物（拆分章节、报告文件、复盘文档）标注来源

### 二、内容-元数据二分法检查

> **原则**：核心标识字段（人需要看）内联YAML，索引管理字段（机器需要读）外部化TOML。

- [ ] **内联判断**：该字段是否是"文档内容的一部分"？（作者/标题/核心标签 → 内联）
- [ ] **外部化判断**：该字段是否是"关于文档的描述信息"？（搜索索引/关联关系/统计/变更历史 → TOML）
- [ ] **TOML元数据存在**：`.meta/toml/` 镜像路径下有对应的 `.toml` 文件（可用 `fix-x-toml-ref.py --create-toml` 自动创建骨架）
- [ ] **阅读体验**：frontmatter不超过10行，不影响Markdown正文阅读

### 三、路径与引用检查

**自动化工具**：`python .agents/scripts/fix-x-toml-ref.py --file <path> --dry-run`

- [ ] **x-toml-ref自动验证**：运行fix-x-toml-ref.py确认路径无需修改
- [ ] **相对路径无误**：不依赖心算，使用脚本自动计算或查表验证
- [ ] **内部链接有效**：文件间互相引用的Markdown链接可到达（可用 `check-links.py` 验证）
- [ ] **导航完整性**：原子文件间双向链接完整（上一章→下一章+返回索引），无断裂路径

### 四、原子化拆分检查（适用场景：大文档拆分）

- [ ] **单一职责**：每个原子文件聚焦一个主题，文件行数控制在合理范围（建议<200行）
- [ ] **索引页存在**：源文件转为导航索引页，包含章节导航表
- [ ] **章节间导航**：每个原子文件末尾有"上一章/下一章/返回索引"导航链接
- [ ] **frontmatter一致性**：所有原子文件frontmatter结构一致（可用模板生成）
- [ ] **source溯源**：每个原子文件的source标注来源（如 `atomized-from:xxx.md`）

### 五、工具产出物治理检查

- [ ] **临时文件已忽略**：新工具/脚本引入的临时产出物（如 `.coverage`、`htmlcov/`、缓存目录）已添加到 `.gitignore`
- [ ] **共享库复用**：新脚本优先复用 `.agents/scripts/lib/` 中的共享函数（project.py、frontmatter.py等）
- [ ] **幂等性验证**：批量处理脚本重复运行0文件需修改（dry-run模式验证）
- [ ] **零依赖原则**（[four-negatives-external-dependency](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/four-negatives-external-dependency.md)）：新脚本不引入第三方包依赖，仅使用Python标准库，确保跨Windows/macOS/Linux即用

### 六、L3标准化模式合规检查

- [ ] **入口-容器分离**（[entry-container-separation](../../docs/retrospective/patterns/methodology-patterns/document-architecture/entry-container-separation.md)）：
  - 入口文档（README/AGENTS/00-overview）控制在<100行，仅作导航用途
  - 深度内容放在容器文件中，入口仅提供链接
  - 新增模块时先创建/更新入口索引，再写深度内容
- [ ] **元文档杠杆**（[meta-document-leverage](../../docs/retrospective/patterns/methodology-patterns/document-architecture/meta-document-leverage.md)）：
  - 资源有限时优先优化索引/导航/入口，而非深化L2内容
  - 新增文档后立即更新上级目录的README索引
  - Skill L1门面文档超过500行时必须拆分
- [ ] **三层治理闭环**（[three-tier-governance](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-tier-governance.md)）：
  - L1原子化：规则/流程已拆分为单一职责的原子单元
  - L2自动化：机械重复操作（路径计算/格式校验/链接检查）已脚本化
  - L3验证：提交前有自动化门禁（check-links/check-frontmatter等）
- [ ] **Spec驱动**（[spec-driven-development](../../docs/retrospective/patterns/methodology-patterns/creative-design/spec-driven-development.md)）：
  - 非平凡任务（>3个文件变更）先写spec再执行
  - spec包含明确的DoD完成定义

### 七、提交前最终验证

- [ ] **frontmatter校验通过**：`python .agents/scripts/check-frontmatter.py --dir <target-dir>` 0错误
- [ ] **链接检查通过**：`python .agents/scripts/check-links.py --path <target-dir>` 无断链
- [ ] **原子提交**：提交范围单一，commit message遵循Conventional Commits格式
- [ ] **中文编码**：含中文的commit message通过 `git commit -F <utf8-file>` 提交，避免GBK乱码

---

## 🛠 自动化工具清单

| 工具 | 用途 | 命令示例 |
|------|------|---------|
| **[docgov.py](../../.agents/scripts/docgov.py)** | **统一CLI入口（推荐）** | `python .agents/scripts/docgov.py doctor --dir docs/` |
| [check-frontmatter.py](../../.agents/scripts/check-frontmatter.py) | frontmatter完整性校验 | `python .agents/scripts/docgov.py check --dir docs/` |
| [fix-x-toml-ref.py](../../.agents/scripts/fix-x-toml-ref.py) | x-toml-ref路径自动修复+TOML创建 | `python .agents/scripts/docgov.py fix --dir docs/ --write --create-toml` |
| [add-frontmatter-title.py](../../.agents/scripts/add-frontmatter-title.py) | 批量添加title字段 | `python .agents/scripts/docgov.py add-title --dir docs/ --write` |
| [add-frontmatter-id.py](../../.agents/scripts/add-frontmatter-id.py) | 批量添加id字段 | `python .agents/scripts/docgov.py add-id --dir docs/ --write` |
| [audit-metadata-ecosystem.py](../../.agents/scripts/audit-metadata-ecosystem.py) | 元数据生态双向审计+自动修复 | `python .agents/scripts/docgov.py audit --dir docs/ --fix` |
| [check-links.py](../../.agents/scripts/check-links.py) | Markdown链接有效性检查 | `python .agents/scripts/docgov.py links --path docs/` |

**快速开始**：`python .agents/scripts/docgov.py doctor --dir docs/ --dry-run` 预览，确认后去掉 `--dry-run` 执行全量治理。

工具复用共享库：
- [lib/project.py](../../.agents/scripts/lib/project.py) — `resolve_project_root()` 项目根目录解析
- [lib/frontmatter.py](../../.agents/scripts/lib/frontmatter.py) — YAML frontmatter解析与字段提取

---

## 📐 核心原则速查

| 原则 | 一句话总结 | 违反信号 |
|------|----------|---------|
| 内容-元数据二分法 | 人看的内联YAML，机器读的外部化TOML | frontmatter超过15行、包含统计/索引字段 |
| 机械心算必错 | 重复心算超3层必错，必须工具化/查表化 | 手动数`../`层数、手动拼路径 |
| 规范三同步 | 发现→导航→示范缺一项规范必悬空 | 规范写完但总览/路由/示范任一缺失 |

---

## 相关模板

- [spec-release-checklist-template.md](spec-release-checklist-template.md) — 新规范发布专用Checklist（三同步原则）
- [insight-extraction-template.md](insight-extraction-template.md) — 洞察萃取报告模板
- [task-template.md](task-template.md) — 通用任务定义模板
