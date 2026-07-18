---
id: "document-governance-checklist"
title: "文档治理Checklist"
source: "insight-extraction.md#4-可迁移性评估"
x-toml-ref: "../../../.meta/toml/.agents/docs/templates/document-governance-checklist.toml"
---
# 文档治理Checklist

> 基于frontmatter元数据统一复盘中萃取的**3项核心原则**、**3项架构模式**和**5项实践经验**，用于新建文档、原子化拆分、批量迁移时的质量门禁检查。
>
> 📌 本模板面向人类读者（`docs/`目录），AI智能体使用版本请参见 [.agents/templates/](../../templates/document-governance-checklist-template.md)。

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
- [ ] **source溯源完整**：派生产物（拆分章节、报告文件、复盘文档）标注来源，且路径为相对路径（禁止 `docs/` 前缀与跨项目绝对路径，可用 `check-links.py --fix --check-frontmatter-paths` 自动修复）

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
- [ ] **共享库复用**：新脚本优先复用 `.agents/scripts/lib/` 中的共享函数（project.py、frontmatter.py、files.py等）
- [ ] **幂等性验证**：批量处理脚本重复运行0文件需修改（dry-run模式验证）

### 六、提交前最终验证

- [ ] **frontmatter校验通过**：`python .agents/scripts/check-frontmatter.py --dir <target-dir>` 0错误
- [ ] **链接检查通过**：`python .agents/scripts/check-links.py --path <target-dir>` 无断链
- [ ] **原子提交**：提交范围单一，commit message遵循Conventional Commits格式
- [ ] **中文编码**：含中文的commit message通过 `git commit -F <utf8-file>` 提交，避免GBK乱码

---

## 🛠 自动化工具清单

所有工具位于项目根目录的 [.agents/scripts/](../../scripts/README.md) 目录下。

| 工具 | 用途 | 命令示例 |
|------|------|---------|
| **[docgov.py](../../scripts/docgov.py)** | **统一CLI入口（推荐）** | `python .agents/scripts/docgov.py doctor --dir docs/` |
| [check-frontmatter.py](../../scripts/check-frontmatter.py) | frontmatter完整性校验 | `python .agents/scripts/docgov.py check --dir docs/` |
| [fix-x-toml-ref.py](../../scripts/fix-x-toml-ref.py) | x-toml-ref路径自动修复+TOML创建 | `python .agents/scripts/docgov.py fix --dir docs/ --write --create-toml` |
| [add-frontmatter-title.py](../../scripts/add-frontmatter-title.py) | 批量添加title字段 | `python .agents/scripts/docgov.py add-title --dir docs/ --write` |
| [add-frontmatter-id.py](../../scripts/add-frontmatter-id.py) | 批量添加id字段 | `python .agents/scripts/docgov.py add-id --dir docs/ --write` |
| [audit-metadata-ecosystem.py](../../scripts/audit-metadata-ecosystem.py) | 元数据生态双向审计+自动修复 | `python .agents/scripts/docgov.py audit --dir docs/ --fix` |
| [check-links.py](../../scripts/check-links.py) | Markdown链接有效性检查 | `python .agents/scripts/docgov.py links --path docs/` |

**快速开始**：`python .agents/scripts/docgov.py doctor --dir docs/ --dry-run` 预览，确认后去掉 `--dry-run` 执行全量治理。

工具复用共享库（[.agents/scripts/lib/](../../scripts/lib/README.md)）：
- [project.py](../../scripts/lib/project.py) — `resolve_project_root()` 项目根目录解析
- [frontmatter.py](../../scripts/lib/frontmatter.py) — YAML frontmatter解析与字段提取

---

## 📐 核心原则速查

| 原则 | 一句话总结 | 违反信号 |
|------|----------|---------|
| 内容-元数据二分法 | 人看的内联YAML，机器读的外部化TOML | frontmatter超过15行、包含统计/索引字段 |
| 机械心算必错 | 重复心算超3层必错，必须工具化/查表化 | 手动数`../`层数、手动拼路径 |
| 规范三同步 | 发现→导航→示范缺一项规范必悬空 | 规范写完但总览/路由/示范任一缺失 |

---

## 相关资源

| 资源 | 路径 | 说明 |
|------|------|------|
| 规范发布Checklist | [.agents/templates/spec-release-checklist-template.md](../../templates/spec-release-checklist-template.md) | 新规范发布专用（三同步原则） |
| 洞察萃取报告模板 | [.agents/templates/insight-extraction-template.md](../../templates/insight-extraction-template.md) | 洞察萃取报告模板 |
| 任务定义模板 | [.agents/templates/task-template.md](../../templates/task-template.md) | 通用任务定义模板 |
| 复盘报告 | [insight-extraction.md](../retrospective/reports/insight-extraction/meta-methodology/retrospective-frontmatter-metadata-unification-20260702/insight-extraction.md) | 本Checklist的来源复盘报告 |
| 元数据规范 | [frontmatter-metadata-standard.md](../../rules/frontmatter-metadata-standard.md) | Frontmatter元数据分层规范原文 |
