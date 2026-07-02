---
id: "pattern-extraction-cmd-log-quality"
title: "CMD-LOG执行日志与质量安全清单"
source: "SKILL.md#04-cmd-log-quality"
x-toml-ref: "../../../../.meta/toml/.agents/skills/pattern-extraction-cmd/SKILL/04-cmd-log-quality.toml"
---
# CMD-LOG执行日志与质量安全清单

## 9. 执行日志（CMD-LOG）

遵循项目 [CMD-LOG命令集执行日志规范](../../../rules/cmd-log-specification.md)，使用统一前缀+键值对+JSON上下文格式。

### 9.1 基本标识

| 字段 | 值 |
|------|-----|
| cmd标识 | `pattern-extraction` |
| Session前缀 | `ptrn-` |
| Session格式 | `ptrn-YYYYMMDD-<pattern-name>` |
| 步骤数 | 6步（S0-S5） |

### 9.2 步骤编号

| 步骤 | 名称 | 对应核心步骤 |
|------|------|-------------|
| S0 | 启动与参数记录 | 第4节强制触发日志（决策前） |
| S1 | 模式识别与分类 | 步骤1-2（三标准判断+目录定位） |
| S2 | 方案决策 | 决策树分支选择（create/update/merge） |
| S3 | 文档生成/更新 | 步骤3-4（frontmatter+标准结构） |
| S4 | 质量验证 | 步骤5（check-pattern-quality.py） |
| S5 | 索引更新与归档 | 步骤6（README/CATEGORIES更新+maturity统计） |

### 9.3 特有事件定义

| 时机 | level | event | msg模板 | ctx必填字段 |
|------|-------|-------|---------|------------|
| 触发参数记录（S0，决策前强制） | INFO | `CMD_START` | 开始模式萃取：\<操作简述\> | trigger_phrase, operation_type, source, pattern_name, user_explicit, dry_run, auto_classify |
| 三标准检查不通过 | WARN | `REUSABILITY_FAIL` | 模式可复用性检查未通过：\<原因\> | failed_criteria（命名/复现/迁移）, pattern_name |
| 目录分类自动判断 | DEBUG | `CLASSIFY_AUTO` | 自动分类目录：\<路径\>，置信度：\<high/med/low\> | target_dir, confidence, classification_basis |
| 决策树分支选择 | INFO | `BRANCH_SELECTED` | 决策分支：\<create/update/merge\>，依据：\<判断依据\> | operation_type, decision_basis, similarity_score（merge时） |
| frontmatter生成 | DEBUG | `FRONTMATTER_READY` | frontmatter已生成：id=\<id\>, maturity=\<L1/L2\>, domain=\<domain\> | pattern_id, maturity, domain, layer, has_source |
| 发现重复模式 | WARN | `DUPLICATE_FOUND` | 发现疑似重复模式：\<现有模式id\>，相似度：\<分数\> | existing_id, similarity_score, overlap_analysis |
| 模式质量检查通过 | INFO | `QUALITY_PASS` | 模式质量检查通过：\<模式id\>，得分：\<分数\> | pattern_id, quality_score, checks_passed |
| 模式质量检查失败 | ERROR | `QUALITY_FAIL` | 模式质量检查失败：\<错误数\>个错误 | pattern_id, error_count, error_details |
| 索引更新完成 | INFO | `INDEX_UPDATED` | 模式索引更新完成：\<目录路径\> | index_path, new_patterns_count |
| 成熟度更新 | DEBUG | `MATURITY_UPDATED` | 模式成熟度更新：\<id\> validation=\<N\> reuse=\<M\> → maturity=\<Lx\> | pattern_id, validation_count, reuse_count, maturity |

### 9.4 关键日志示例

```
[CMD-LOG] | level=INFO | cmd=pattern-extraction | step=S0 | event=CMD_START | session=ptrn-20260701-markdown-as-interface | msg=开始模式萃取：从insight-b-markdown-as-interface创建新模式 | ctx={"trigger_phrase":"把这个洞察沉淀成模式","operation_type":"create","source":"insight-b-markdown-as-interface.md","pattern_name":"markdown-as-interface","user_explicit":false,"dry_run":false,"auto_classify":true}
[CMD-LOG] | level=DEBUG | cmd=pattern-extraction | step=S1 | event=CLASSIFY_AUTO | session=ptrn-20260701-markdown-as-interface | msg=自动分类目录：methodology-patterns/ai-collaboration，置信度：high | ctx={"target_dir":"methodology-patterns/ai-collaboration","confidence":"high","classification_basis":"涉及Agent接口/五要素模型，属AI协作方法论"}
[CMD-LOG] | level=INFO | cmd=pattern-extraction | step=S2 | event=BRANCH_SELECTED | session=ptrn-20260701-markdown-as-interface | msg=决策分支：create，依据：无同名/相似模式，满足三标准 | ctx={"operation_type":"create","decision_basis":"三标准通过，无重复","similarity_score":null}
[CMD-LOG] | level=INFO | cmd=pattern-extraction | step=S5 | event=CMD_COMPLETE | session=ptrn-20260701-markdown-as-interface | msg=模式萃取完成：markdown-as-interface（L1），总耗时：约15分钟 | ctx={"duration":"~15m","pattern_id":"markdown-as-interface","maturity":"L1","quality_score":100}
```

### 9.5 决策分支排查示例

当发现分类错误或分支选错时，可通过以下命令快速定位问题：

```powershell
# 查看某次模式萃取的完整决策路径
Select-String -Path ".agents/logs/cmd-*.log" -Pattern "ptrn-20260701-<pattern-name>" | Select-Object -Property Line

# 查看所有模式分类决策（排查目录归类问题）
Select-String -Path ".agents/logs/cmd-*.log" -Pattern "CLASSIFY_AUTO|BRANCH_SELECTED" | Select-Object -Property Line
```


## 10. 安全检查清单（模式质量门）

模式入库前必须逐项确认：

- [ ] **可复用三标准已满足**：可命名+可复现+可迁移，不是一次性特定方案
- [ ] **分类目录正确**：已判断是架构/代码/方法论层，子主题归属准确
- [ ] **frontmatter字段完整**：id/domain/layer/maturity/validation_count/reuse_count/documentation_level/source均已填写
- [ ] **source字段已标注**：指向来源洞察/复盘文件的相对路径（溯源要求）
- [ ] **标准结构完整**：包含问题/解决方案/案例/反模式/边界章节
- [ ] **至少1个实际案例**：不是纯理论，有本项目真实应用场景
- [ ] **文件路径使用相对路径**：禁止file:///绝对路径
- [ ] **索引已更新**：对应目录README.md和CATEGORIES.md（如适用）已添加条目
- [ ] **质量检查已通过**：check-pattern-quality.py 无错误
- [ ] **成熟度统计已更新**：pattern-maturity.py check-index --fix 已运行
- [ ] **模式文档控制在合理长度**：单模式文档建议<300行，复杂内容拆分L2引用
- [ ] **命名符合kebab-case**：文件名和frontmatter id使用kebab-case格式


---

## 相关模式

- - [insight-cmd Skill](../../insight-cmd/SKILL.md)
- - [retrospective-cmd Skill](../../retrospective-cmd/SKILL.md)
- - [CMD-LOG日志规范](../../../rules/cmd-log-specification.md)
- - [模式成熟度管理](../../../scripts/pattern-maturity.py)
- - [模式萃取方法论](../../../../docs/retrospective/patterns/README.md)
- - [模式合并边界判断](../../../../docs/retrospective/patterns/methodology-patterns/document-architecture/pattern-merge-boundary.md)

← 上一章: [现有模式更新与模式合并重构方案](03-update-merge.md) | **[返回索引](../SKILL.md)** | 下一章 → [错误处理、Gotchas陷阱与参考速查表](05-errors-gotchas-reference.md)
