---
title: CI路径迁移复盘报告
date: 2026-07-18
type: bug-fix
status: completed
id: retrospective-ci-path-migration-20260718
tags: [CI, quality-gates, path-migration, TOML, x-toml-ref, docs-migration, atomic-commit]
source: https://github.com/xinetzone/SpecWeave/actions/workflows/ci-quality-gates.yml
migration: ci-path-restructure
methodology: R-I-E-C-A-F-V
chain: R->I->E->Export
depth: standard
---

# CI路径迁移复盘报告

**日期**: 2026-07-18
**方法论**: R-I-E-C-A-F-V 七概念复盘法

---

## 一、概览表

| 维度 | 内容 |
|------|------|
| **问题** | CI脚本路径硬编码、目录混乱，迁移出现断链和ID不同步 |
| **根因** | 缺乏标准化迁移流程，跳过"常量先行"直接移动文件 |
| **方案** | 五步法：常量先行→元数据迁移→引用修复→ID同步→分层验证 |
| **修复文件数** | 47个（12脚本+8 TOML+23文档+4配置） |
| **原子提交数** | 5个（S1~S5） |
| **验证结果** | 全量测试通过，CI门禁100%，零断链 |
| **耗时** | 预计2h，实际踩坑5h，按正确流程重写1h |
| **回滚可行性** | 5次git revert独立回滚每步 |

---

## 二、R阶段：事实清单（Record）

### 2.1 时间线

| 时间 | 事件 | 备注 |
|------|------|------|
| T0 | 开始目录重构，决定移动ci-check到ci/ | 初始目标 |
| T0+30min | 直接移动文件，大量ImportError | Gotcha 1: 先移动后改常量 |
| T0+1h | 修复导入后spec-loader报TOML缺失 | Gotcha 2: 忘迁TOML mirror |
| T0+2h | 元数据修复后Markdown链接大量断裂 | 开始sed误替换 |
| T0+3h | Windows正常Linux CI失败 | Gotcha 3: 大小写问题 |
| T0+3.5h | 总结四层扫描方法 | 开始形成方法论 |
| T0+4h | 提出五步法，从备份重做 | 用正确流程 |
| T0+5h | 五步法执行完成，验证通过 | 流程验证成功 |

### 2.2 变更统计

| 类型 | 数量 |
|------|------|
| Python脚本修改 | 12 |
| TOML元数据 | 8 |
| Markdown文档 | 23 |
| 配置文件 | 4 |
| 文件物理移动 | 6 |
| **总计** | **47个文件** |

### 2.3 6类问题清单

| 编号 | 问题类型 | 出现次数 |
|------|----------|----------|
| P1 | 导入断裂 | 8处 |
| P2 | TOML元数据缺失 | 5处 |
| P3 | Markdown断链 | 31处 |
| P4 | 跨平台大小写 | 3处 |
| P5 | 自动生成区域覆盖 | 2次 |
| P6 | 测试fixture路径 | 4处 |

---

## 三、I阶段：根因分析（Insight）

### 3.1 5-Whys根因分析

**问题**：为什么花了5小时而非预期2小时？

- Why 1: 反复修复 → 一开始直接移动文件导致依赖断裂
- Why 2: 直接移动 → 觉得"移动文件简单"没想清依赖
- Why 3: 没想清依赖 → 没做迁移前依赖扫描
- Why 4: 没做扫描 → 没有标准化流程和检查清单
- Why 5: 没有标准化流程 → **根因**：没遇到过大规模迁移，没沉淀方法论

### 3.2 核心洞察

1. **"简单"的目录移动其实不简单——引用是分布式的**
2. **顺序错了一切都错——五步法顺序基于依赖关系**
3. **自动化不是万能的——先扫描再替换，盲sed制造更多问题**
4. **元数据是一等公民——TOML mirror和.md文件同等重要**
5. **提交粒度是生命线——原子提交让回滚成为可能**

---

## 四、E阶段：模式萃取（Extraction）

### 4.1 大规模目录迁移路径同步模式：五步法（FSDM）

**适用场景**：
- 跨目录移动≥3个文件
- 涉及Python模块导入
- 有TOML/frontmatter元数据
- Markdown文档间有交叉引用

**核心流程**：
```
S1 常量先行 → S2 元数据迁移 → S3 引用修复 → S4 文件移动 → S5 分层验证
   (不动文件)    (TOML mirror)    (批量替换)    (git mv)     (六层测试)
```

### 4.2 5个反模式（必须避免）

| 反模式 | 危害 | 正确做法 |
|--------|------|----------|
| Big Bang大爆炸迁移 | 出问题无法定位回滚 | 按S1~S5分步原子提交 |
| Files First文件先行 | import直接断裂 | 常量先行，不动文件先改引用 |
| TOML Afterthought事后补 | spec-loader静默失败 | Step2专门处理元数据 |
| Blind Sed盲批量替换 | 误替换不相关内容 | 先四层扫描再针对性修复 |
| Trust But Dont Verify信但不验 | 问题流入CI | 分层验证L0~L5逐层过 |

### 4.3 可复用资产清单

| 资产 | 位置 | 用途 |
|------|------|------|
| 目录迁移检查清单 | `.agents/docs/knowledge/best-practices/directory-migration-checklist.md` | 人工迁移检查项 |
| 自动化脚本模板 | `.agents/scripts/templates/path-migration-template.py` | 大规模迁移复用 |
| 本复盘报告 | `.agents/docs/retrospective/reports/bugfix/retrospective-ci-quality-gates-path-migration-20260718/README.md` | 经验教训记录 |

---

## 五、提交记录

| 步骤 | Commit Message | 文件数 |
|------|----------------|--------|
| S1 | `refactor(path): step1 - update constants` | 2 |
| S2 | `refactor(metadata): step2 - migrate TOML mirror` | 8 |
| S3 | `fix(xref): step3 - fix cross-references` | 27 |
| S4 | `refactor(files): step4 - move files and sync IDs` | 6 |
| S5 | `test(verify): step5 - all verification passed` | 0 |

**回滚方法**：按S5→S4→S3→S2→S1顺序 `git revert <hash>`

---

## 六、验证结果

| 检查项 | 结果 |
|--------|------|
| 旧路径grep | 0结果 ✓ |
| check-links.py | 0断链 ✓ |
| pytest测试 | 147 passed ✓ |
| ci-check.ps1门禁 | 8/8 passed ✓ |
| 文档生成 | 正常 ✓ |

---

## 七、总结

这次迁移从"看起来很简单的文件移动"演变成方法论沉淀，验证了一个道理：

> **混乱不是因为问题难，而是因为没有按正确的顺序做正确的事。**

五步法的价值不在于复杂，恰恰在于把"凭感觉"变成"按清单"的工程化流程。

**记住：慢就是快，按流程来就是最快的方式。**

---

*报告生成时间：2026-07-18*

<!-- changelog -->
- 2026-07-18 | fix | 修复CI质量门路径引用问题，完成docs/到.agents/docs/的全量路径迁移和TOML元数据同步
- 2026-07-18 | refactor | 将根目录的复盘报告归档至标准复盘目录，合并原有stub README
