---
name: inflight-deliverable-commit-verify
description: 对非本会话生产的在途产物（并行会话/其他窗口遗留在工作区的知识包、模式、技能）做提交前完整性核验并原子提交。当用户要求提交"工作区残留/别人改的/并行会话的/未跟踪的新目录"时使用。本会话自产变更直接用 atomic-commit-cmd，勿用本技能。
---

# 在途产物提交前核验与原子提交

## 1. 定位

本技能是 [atomic-commit-cmd](../../../.agents/skills/atomic-commit-cmd/SKILL.md) 的前置补强：后者保证"一次提交只做一件事"，本技能额外解决**提交者不是产物作者**带来的信息差——没参与构建就不知道产物是否完整、配套件是否齐全、生成文件是否夹带了其他会话的条目。

核心纪律：**只核验与提交，不改他人在途产物的内容**。发现缺件或质量门失败，停下报告，不替作者补写。

## 2. 触发场景

- "工作区还有改动，一起提交吧""把残留的也提交了"，而残留文件并非本会话创建；
- 多会话/多窗口并行（本仓库高频）：`git status` 出现未知的未跟踪目录或修改；
- 用户点名提交某个并行会话的产物（知识包、模式、技能、报告）。

**不适用**：本会话自产变更（直接走 atomic-commit-cmd）；纯查询工作区状态；产物作者明确表示仍在编辑（只核验不提交，结论报给用户）。

## 3. 五步流程

### 步骤 1：盘点与归属判定

```bash
git status --short
git log --oneline -5
git show --stat --format="%h %an %ad %s" <可疑提交>
```

- 逐个变更标注归属：本会话 / 并行会话在途 / 历史遗留；
- **提交前与重试前都要查 `git log`**：并行会话可能在你操作期间自行提交。若目标文件已不在 `git status` 中，用 `git show --stat` 核对其提交是否完整覆盖本应提交的文件——已覆盖则不重复提交，直接汇报。

### 步骤 2：产物完整性核验（按类型对照清单）

| 产物类型 | 位置特征 | 必查项 |
|---|---|---|
| 知识包 | `docs/knowledge/<域>/<bundle>/` | index.md frontmatter（id/title/date/status/source session）；`concepts/` 概念页齐全；`references/source-inventory.md` 与 `adversarial-review.md`；上级域 `index.md` toctree 已登记 |
| 方法论模式 | `docs/retrospective/patterns/.../<category>/` | 模式 md 与 `.meta/toml/...` 双星（id/category/maturity 一致）；三处登记——分类 `index.md` toctree、模式库总表、`CATEGORIES.md`（生成文件）；与上游知识包双向加链 |
| 技能 | `.trae/skills/<name>/` | `SKILL.md` frontmatter 的 name 等于目录名、description 含触发词 |
| 复盘报告 | `docs/retrospective/reports/` | 引用目标以 `concepts/` 下权威拷贝路径为准（见步骤 3 经验） |

配套件惯例用抽查确认而非假设：如知识包 TOML 非强制（抽查同类包多数无 TOML 即非遗漏），模式 TOML 则为强制双星。

### 步骤 3：质量门（限定目录，避免全仓扫描）

```powershell
# Python 不在 PATH 时用全路径
python .agents/scripts/check-links.py --path <产物目录>
python .agents/scripts/check-filename-convention.py --directory <产物目录>
```

- **必须加 `--path`/`--directory`**：全仓扫描含 git submodule，极慢；`--fix` 模式还会全仓建文件索引（实测累计 CPU 上千秒不返回），疑似路径层数错误时改为人工定点修复，每条新路径用 Glob 定位实际文件并与同目录权威文件中的先例核对；
- 链接修复的路径层数先例：知识包 index 在 `docs/knowledge/tech/<bundle>/`，引 retrospective 用 `../../../retrospective/`；`concepts/` 子页用 `../../../../retrospective/`；`patterns/code-patterns/` 与 `patterns/architecture-patterns/` 在 `patterns/` 下，从分类子目录引用是 `../../code-patterns/`（两层，不是三层）；
- 报告目录历史迁移：旧链 `reports/knowledge|milestone/...` 的现位置为 `reports/concepts/knowledge|milestone/...`。

### 步骤 4：提交边界隔离（并行工作区特有）

1. **筛查生成文件夹带**：`CATEGORIES.md` 等自动生成文件可能同时含多个并行会话的新条目。提交前 `git diff` 逐行核对，只保留本产物相关条目；属于他人的条目与计数临时回退，提交后由对应会话重新生成恢复（告知用户这一影响）。
2. **显式文件清单，禁止目录参数与 `git add .`**：`git-commit-utf8.py` 传目录路径会因"add 后暂存区与指定列表不一致"失败，必须逐文件列出（知识包通常 8-10 个文件，可接受）。
3. **暂存区预检**：提交工具检测到列表外已暂存文件会 FAIL。先 `git reset HEAD -- <无关文件>` 清空再提交（reset 不丢工作区内容）。

### 步骤 5：执行、编码验证与重扫描

```powershell
python .agents/scripts/git-commit-utf8.py -m "type(scope): 中文描述（为什么）" <显式文件1> <显式文件2> ...
git log -1 --format="%s"   # 验证中文无乱码
git status --short         # 批量场景必须重扫描，残留变更回到步骤 1 重新判定
```

- 提交类型：知识包/模式/技能入库均为 `docs` 或 `chore(skills)`；断链修复用 `fix(links)` 并按"修复即闭环"标注 `[prevent: ci-gate]`；
- **不推送**，除非用户明确要求；
- 提交后汇报：提交哈希、文件数、质量门结果、剩余在途变更及其归属、需要其他会话补做的收尾（如重建 CATEGORIES.md）。

## 4. 安全清单

- [ ] 每个变更的归属已判定，他人在途且未完成的产物只核验不提交
- [ ] 产物结构、配套件、索引登记按类型清单核对完毕
- [ ] 链接与文件名质量门在限定目录通过
- [ ] 生成文件（CATEGORIES.md 等）已 diff 筛查，无他人条目夹带
- [ ] 显式文件清单提交，未用目录参数与 `git add .`
- [ ] 提交失败后先查 `git log` 确认未被并行会话抢先收录，再决定重试
- [ ] 提交后 `git status` 重扫描，残留逐项报告归属
- [ ] 核验中发现的内容缺陷只报告、不代改

## 5. Gotchas

- **并行会话抢跑**：你重试提交的间隙，另一会话可能已提交同一批文件。症状：`git status` 中文件消失、出现陌生提交。处理：`git show --stat` 核对覆盖度与有无夹带，覆盖完整即停止，勿重复提交。
- **CATEGORIES.md 计数是机械值**：判定对错不靠肉眼——重跑 `generate-categories.py` 后 `git diff` 零差异即权威一致；总模式数增量应恰等于新增模式数。
- **历史断链的目标选择**：`docs/retrospective/reports/` 下新旧分类目录可能并存双份拷贝，修复目标以 OKF 转换后的 `concepts/` 权威拷贝中已验证的链接为准。
- **检查器误报**：行内反引号包裹的 `[文字](路径)` 示例、`**<占位符>**` 会被误判为断链；文档中示例一律改为纯文字描述（如"方括号文字紧跟圆括号路径"）。
- **失效文件名引用**：`.trae/specs/` 下旧 `analysis-report.md` 已按 Spec Mode 更名为 `spec.md`，遇此断链改引现存的规范三件套文件。

## 6. 来源

萃取自 2026-09-30 多会话并行工作日（场景区间选型法入库、25 处历史断链修复、量子密信知识包、knowledge-pack-builder 技能更新连续四次提交实战），会话中两次遇到并行会话抢跑提交、一次生成文件夹带、一次目录参数导致提交工具失败。
