# 残留frontmatter路径问题修复计划（✅ 全部完成）

> **完成状态**：8阶段全部完成，frontmatter 357→0 + 内联断链 63→0 = 残留问题全部清零
> **完成日期**：2026-07-10

## Context

批量修复（commit `9bb1ce5c`）将803个frontmatter路径问题降至357个（降幅73.5%），但剩余357个问题因工具能力限制和目标文件缺失无法自动修复。本计划通过扩展工具能力 + 手动修复，将残留问题降至最低。

### 问题分类（357个）

| 类别 | 数量 | 根因 | 可修复性 |
|------|------|------|---------|
| docs/前缀(source在TOML中) | ~121 | `fix_frontmatter_paths()`只修改md文件，不修改TOML | **工具扩展后自动修复** |
| docs/前缀(source在YAML中) | ~15 | 边缘情况或新增文件 | **自动修复** |
| docs/前缀(目标缺失) | ~16 | 原子化拆分后删除原始报告 | 手动修复 |
| 缺失TOML文件 | 54 | x-toml-ref指向不存在的.toml | **fix-x-toml-ref.py --create-toml** |
| 跨项目路径(d:/AI/) | 28 | source指向其他项目 | 手动修复 |
| 缺失source目标(.md) | 96 | 原子化拆分后删除原始报告 | 手动修复 |
| temp路径(.temp/) | 11 | source指向临时文件 | 手动修复 |
| 其他缺失 | 43 | 待调查 | 待定 |
| 内联断链 | 63 | 正文链接指向已删除文件 | 手动修复 |

## 修复方案

### Phase 1: 扩展 `fix_frontmatter_paths()` 支持TOML文件修复

**目标**：修复根因——工具检测到TOML中的source字段但无法写入TOML文件

**修改文件**：
- `d:\spaces\SpecWeave\.agents\scripts\check-links.py` — `fix_frontmatter_paths()` 函数（~L516-642）
  - 检测字段来源：YAML还是TOML（利用 `parse_frontmatter_unified()` 已加载的metadata分离信息）
  - 若来自TOML：读取 `x-toml-ref` 指向的TOML文件内容，执行路径替换，写回TOML文件
  - 写回时使用 `newline=""` 保留LF行尾
- `d:\spaces\SpecWeave\.agents\scripts\tests\test_check_links_frontmatter_fix.py` — 新增测试用例
  - 测试source字段在TOML中时的修复
  - 测试TOML文件写入保留LF行尾
  - 测试修复报告准确性（不误报已修复）

**关键设计**：
- 复用现有 `_compute_frontmatter_fix()` 计算修复路径
- 复用现有 `_replace_path_in_text()` 在TOML文本中替换路径
- 新增 `_fix_path_in_toml()` 辅助函数：读取TOML → 替换 → 写回
- 通过 `parse_frontmatter_unified()` 返回的元数据中区分字段来源

### Phase 2: 创建缺失TOML文件

**命令**：`python .agents/scripts/fix-x-toml-ref.py --dir docs --create-toml --write`

**效果**：自动创建54个缺失的TOML骨架文件

### Phase 3: 重新运行批量修复

**命令**：`python .agents/scripts/check-links.py --path docs --fix --check-frontmatter-paths`

**预期效果**：
- 修复121个TOML中的docs/前缀问题（Phase 1扩展后）
- 修复15个YAML中的docs/前缀问题
- 预计修复后残留：~357 - 121 - 15 - 54 = ~167个

### Phase 4: 手动修复跨项目路径（28个）

**策略**：
- 检查 `d:/AI/...` 路径的文件是否在当前项目中存在（路径映射）
- 若存在：转换为相对路径
- 若不存在：移除source字段或标注为外部引用

**主要文件**：
- `docs/retrospective/patterns/methodology-patterns/research-knowledge/vendor-doc-info-compensation-search.md`
- `docs/retrospective/patterns/methodology-patterns/research-knowledge/vendor-product-learning-twelve-step-template.md`
- `docs/retrospective/patterns/methodology-patterns/retrospective-knowledge/pre-check-duplication-layered-sedimentation.md`
- `docs/knowledge/learning/07-vendor-product-learning/sunlogin/sunlogin-ai-developer-ecosystem-wiki.md`

### Phase 5: 手动修复temp路径（11个）

**策略**：移除指向 `.temp/` 的source字段

**主要文件**：
- `docs/knowledge/learning/06-business-trends-analysis/2026-07-08-ai-anthropomorphic-interim-measures-analysis.md`

### Phase 6: 手动修复缺失source目标（96个+43个其他缺失）

**策略**：
1. 检查目标文件是否被原子化拆分（原文件删除，拆分为目录）
2. 若已拆分：更新source指向拆分后的目录或最相关的子文件
3. 若无替代：移除source字段或标注"来源已归档"

**批量处理方式**：编写一次性脚本扫描所有缺失目标的source字段，自动查找替代文件（按文件名匹配）

### Phase 7: 修复内联断链（63个）

**策略**：逐个检查断链，更新或移除无效链接

### Phase 8: 验证与提交

1. 运行 `check-links.py --path docs --check-frontmatter-paths` 验证残留数量
2. 运行 `fix-x-toml-ref.py --dir docs --dry-run` 验证TOML文件完整
3. 更新 `insight-action-backlog.md` 后续建议第5项标记完成
4. 创建原子提交（按Phase分别提交）

## 提交计划

| # | 范围 | 提交消息 | 状态 |
|---|------|---------|------|
| 1 | Phase 1: 工具扩展+测试 | `fix(check-links): 扩展fix_frontmatter_paths支持TOML文件路径修复` (ef40f834) | ✅ |
| 2 | Phase 2: TOML创建 | `docs(toml): 批量创建208个缺失TOML元数据文件并修复197个x-toml-ref路径` (34582cfc) | ✅ |
| 3 | Phase 3: 批量修复 | `docs(links): 重新批量修复frontmatter路径问题` (84d0b2fa) | ✅ |
| 4 | Phase 4-5: 跨项目+temp | `docs(frontmatter): 修复跨项目路径和temp引用替换为描述性字符串` (a0dd3222) | ✅ |
| 5a | Phase 6a: 模板引用+绝对路径 | `docs(frontmatter): 批量修复模板引用和绝对路径为external标记或相对路径` (f072f55a) | ✅ |
| 5b | Phase 6b: docs/前缀路径 | `docs(frontmatter): 批量修复docs/前缀source路径为相对路径或README.md引用` (6fb0a5bd) | ✅ |
| 5c | Phase 6c: 目录链接+TOML同步 | `docs(frontmatter): 修复目录链接和缺失文件路径及TOML source同步` (88674912) | ✅ |
| 6 | Phase 7: 内联断链 | `docs(links): 修复63个内联断链并更新Backlog后续建议第5项为已完成` (ee1d6949) | ✅ |
| 7 | Phase 8: TOML验证 | 1个x-toml-ref修复（本提交） | ✅ |

## 验证方式

```bash
# 验证frontmatter路径
python .agents/scripts/check-links.py --path docs --check-frontmatter-paths 2>&1 | tail -5

# 验证TOML完整性
python .agents/scripts/fix-x-toml-ref.py --dir docs --dry-run

# 运行单元测试
python -m pytest .agents/scripts/tests/test_check_links_frontmatter_fix.py -v
```

## 预期成果（实际完成）

- ~~357个残留问题 → 预计降至 <50个~~ → **实际降至 0个**（超额完成）
- ~~63个内联断链 → 手动修复~~ → **实际降至 0个**（100%消除）
- ✅ 工具能力提升：`fix_frontmatter_paths()` 现可修复TOML文件中的source字段
- ✅ Backlog后续建议第5项标记完成
- ✅ TOML完整性验证通过（0错误）
- ✅ 所有8阶段原子提交完成
