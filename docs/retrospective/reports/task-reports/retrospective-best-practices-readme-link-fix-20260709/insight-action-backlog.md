---
id: "action-backlog-best-practices-readme-link-fix-20260709"
title: "best-practices目录断链修复行动项Backlog"
date: 2026-07-09
source: "README.md#四改进行动项"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/task-reports/retrospective-best-practices-readme-link-fix-20260709/insight-action-backlog.toml"
type: insight-action-backlog
status: completed
tags: ["action-backlog", "link-fix", "tool-enhancement", "knowledge-base"]
parent_retrospective: "retrospective-best-practices-readme-link-fix-20260709"
---
# 行动项Backlog：best-practices目录断链修复与入口文档建设

> 来源：[README.md](README.md) → [execution-retrospective.md](execution-retrospective.md)
> 更新日期：2026-07-10（全部行动项完成：P2#7模板规范→P1#3 CI门禁集成）
> 文档类型：行动项Backlog（insight-action-backlog）

---

## 行动项状态总览

| 优先级 | 总数 | 已完成 | 部分完成 | 待推进 |
|--------|------|--------|---------|--------|
| P0 | 2 | 2 ✅ | 0 | 0 |
| P1 | 3 | 3 ✅ | 0 | 0 |
| P2 | 2 | 2 ✅ | 0 | 0 |
| **合计** | **7** | **7** | **0** | **0** |

---

## P0（立即执行，1周内）

| # | 行动项 | 验收标准 | 优先级 | 状态 | 交付物/备注 |
|---|--------|---------|--------|------|------------|
| 1 | 扩展check-links.py支持frontmatter路径检查 | 运行工具时自动检测TOML frontmatter中所有路径字段的有效性，输出检测报告 | P0 | ✅ **已完成（超额交付）** | 实现通用`check_frontmatter_paths()`函数，新增`--check-frontmatter-paths`参数。支持：source、x-toml-ref、related_*字段；多路径提取（+、\|、,、;分隔）；智能非路径值过滤（跳过URL、session:、占位符、纯中文描述）；锚点处理；docs/前缀格式检测；向后兼容原`--check-x-toml-ref`参数 |
| 2 | 扫描所有知识库目录，识别并补全缺失的README入口文档 | docs/knowledge/下所有子目录都有README.md，链接检查100%通过 | P0 | ✅ **已完成** | generate-readme.py已批量补全P1阶段48个README；本次验证docs/knowledge目录--scan结果确认覆盖完整 |

---

## P1（1个月内）

| # | 行动项 | 验收标准 | 优先级 | 状态 | 交付物/备注 |
|---|--------|---------|--------|------|------------|
| 3 | 建立"新增内容目录必须同步创建README"的门禁检查 | CI检查中新增目录README存在性验证 | P1 | ✅ **已完成** | 在ci-check.ps1/sh中新增第9步README存在性检查；generate-readme.py新增`--check`模式（发现缺失README时退出码1）；已升级为ERROR级（清理3个预缺失README后）；commit e9c825cc + 61600881 |
| 4 | 统一所有文档frontmatter source字段格式为相对路径，消除docs/绝对路径混用 | grep搜索无 `source: "external: 外部项目引用""参数）；commit d2e0d4a7 |
| 7 | 在创建新文档模板中内置正确的相对路径计算示例 | 模板中的source字段示例使用正确相对路径，不使用docs/前缀 | P2 | ✅ **已完成** | 在frontmatter规范中新增source字段"路径格式规范"子章节（02-yaml-fields.md，含含✅正确/❌错误示例）；04-templates-errors.md新增3行错误条目（docs/前缀、跨项目绝对路径、路径层级不完整）；document-governance-checklist.md的source检查项补充路径格式要求与自动修复工具引用；commit 89954185 |

---

## 工具增强详情：check-links.py --check-frontmatter-paths

### 新增能力

在 [check-links.py](../../../../../.agents/scripts/check-links.py) 中新增通用frontmatter路径检查功能：

```bash
# 推荐用法（检查所有路径字段：source, x-toml-ref, related_*）
python .agents/scripts/check-links.py --path <目录> --check-frontmatter-paths

# 旧参数--check-x-toml-ref自动升级为全面检查，输出兼容性提示
```

### 核心能力清单

| 能力 | 说明 |
|------|------|
| 支持字段 | source、x-toml-ref、所有related_前缀字段 |
| 值类型 | 字符串、列表、多路径分隔（+、\|、,、;） |
| 智能过滤 | 自动跳过URL、session:引用、占位符、纯中文描述、枚举ID值 |
| 锚点支持 | 正确处理带#锚点的路径（只验证文件存在，不验证锚点） |
| 格式检测 | 报告`docs/`前缀不规范写法 |
| 向后兼容 | 原`--check-x-toml-ref`仍可用，自动升级为全面检查 |

### 实现的关键函数

- `check_frontmatter_paths()`: 主检查函数，遍历文件解析frontmatter并验证路径
- `_extract_paths_from_value()`: 从复杂值中提取路径列表，支持多分隔符和混合格式
- `_is_path_value()`: 判断字符串是否为路径值（过滤非路径内容）
- `_check_single_path()`: 检查单个路径是否存在，处理锚点分割

---

## 本次推进修复清单（第一性原理推进阶段）

| # | 文件 | 问题 | 修复 |
|---|------|------|------|
| 1 | [html-body-extraction.md](../../../../knowledge/operations/html-body-extraction.md) | source使用docs/前缀 | 修正为相对路径 `../../retrospective/...` |
| 2 | [tool-failure-degradation-matrix.md](../../../../knowledge/operations/tool-failure-degradation-matrix.md) | source使用docs/前缀 | 修正为相对路径 `../../retrospective/...` |
| 3 | [wechat-mp-content-extraction.md](../../../../knowledge/operations/wechat-mp-content-extraction.md) | source使用docs/前缀 | 修正为相对路径 `../../retrospective/...` |
| 4 | [windows-platform-compatibility-guide.md](../../../../knowledge/operations/windows-platform-compatibility-guide.md) | source路径不完整（缺少../../前缀） | 补全正确相对路径 |

---

## 第一性原理推进记录

### 推进思路

用第一性原理审视行动项Backlog：P1 #4要求"统一全库frontmatter source字段格式"，全库有803个frontmatter路径问题，手动修复不现实。本质问题是**缺少自动化修复工具**，而非路径问题本身。因此优先实现P2 #6（工具自动化），再用工具批量执行P1 #4（手动修复变自动修复），形成"工具→批量执行"的闭环。

### 推进顺序

1. **P2 #6 工具实现**（commit d2e0d4a7）：新增 `fix_frontmatter_paths()` 函数，支持docs_prefix直接修复和missing_file候选搜索修复；32个单元测试覆盖所有边界场景；同时修复Windows下write_text的LF行尾保留问题
2. **P1 #4 全库批量修复**：运行 `python .agents/scripts/check-links.py --path docs --fix --check-frontmatter-paths`，扫描2243个.md文件，耗时约56分钟

### 批量修复结果

| 指标 | 修复前 | 修复后 | 修复数 | 降幅 |
|------|--------|--------|--------|------|
| frontmatter路径问题 | 803 | 294 | 509 | 63.5% |
| 内联断链（本地） | 542 | 63 | 479 | 88.4% |
| **合计** | **1345** | **357** | **988** | **73.5%** |
| 变更文件数 | - | 512 | - | - |
| 路径替换数 | - | 923 | - | - |

### 残留问题分析（357个，均为无法自动修复类型）

| 类型 | 数量 | 说明 | 建议处理方式 |
|------|------|------|------------|
| 缺失TOML元数据文件 | ~20 | x-toml-ref指向不存在的.toml文件 | 创建对应TOML文件或更新引用 |
| 跨项目路径（d:/AI/） | ~10 | source指向d:/AI/目录（其他项目） | 改为相对路径或标注为外部引用 |
| 目标文件不存在 | ~60 | source指向的.md文件已被删除或重命名 | 手动确认并更新引用 |
| docs/前缀但目标不存在 | ~15 | source使用docs/前缀且目标文件不存在 | 手动确认目标文件路径后修复 |
| 内联断链（文件不存在） | 63 | 链接指向的文件已被删除或重命名 | 手动确认并更新链接 |
| 外部链接 | 0 | 无 | - |

### 8阶段修复记录（2026-07-10）

| Phase | 范围 | 提交 | 结果 |
|-------|------|------|------|
| Phase 1 | 扩展fix_frontmatter_paths支持TOML修复 | ef40f834 | 工具增强 |
| Phase 2 | 批量创建208个缺失TOML文件 | 34582cfc | 197个x-toml-ref路径修复 |
| Phase 3 | 重新批量修复 | 84d0b2fa | 357→303（降幅15%） |
| Phase 4-5 | 跨项目路径+temp引用 | a0dd3222 | 50个source替换为描述性字符串 |
| Phase 6a | 模板引用+绝对路径 | f072f55a | 303→205（降幅32%） |
| Phase 6b | docs/前缀路径 | 6fb0a5bd | 205→76（降幅63%） |
| Phase 6c | 目录链接+缺失文件+TOML同步 | 88674912 | 76→0（100%消除） |
| Phase 7 | 内联断链 | （本提交） | 63→0（100%消除） |

**最终结果**：frontmatter路径问题 357→0，内联断链 63→0，残留问题全部清零。

### LF行尾验证

- 采样20个修改文件：LF-only=20，CRLF=0，Mixed=0
- `newline=""`参数正确保留原始LF行尾，符合.gitattributes规范（`*.md text eol=lf`）

---

## 后续推进建议

1. ~~**批量修复P1 #4**~~ ✅ 已完成（P2#6工具实现后全库批量修复）
2. ~~**frontmatter自动修复P2 #6**~~ ✅ 已完成（commit d2e0d4a7）
3. ~~**CI集成P1 #3**~~ ✅ 已完成（commit e9c825cc，generate-readme.py --check门禁）
4. ~~**模板更新P2 #7**~~ ✅ 已完成（commit 89954185，frontmatter路径格式规范）
5. ~~**残留问题处理**~~ ✅ 已完成（8阶段修复：frontmatter 357→0 + 内联断链 63→0，详见下方修复记录）
6. ~~**README门禁升级**~~ ✅ 已完成（清理3个预缺失README后，ci-check第9步已从WARN级升级为ERROR级）

---

## 关联文档

- **执行复盘**：[execution-retrospective.md](execution-retrospective.md)
- **洞察萃取**：[insight-extraction.md](insight-extraction.md)
- **主索引**：[README.md](README.md)
