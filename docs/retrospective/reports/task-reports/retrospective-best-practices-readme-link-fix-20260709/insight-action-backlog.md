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
> 更新日期：2026-07-09（第一性原理推进后状态更新）
> 文档类型：行动项Backlog（insight-action-backlog）

---

## 行动项状态总览

| 优先级 | 总数 | 已完成 | 部分完成 | 待推进 |
|--------|------|--------|---------|--------|
| P0 | 2 | 2 ✅ | 0 | 0 |
| P1 | 3 | 1 ✅ | 1 🔄 | 1 ⏳ |
| P2 | 2 | 0 | 0 | 2 ⏳ |
| **合计** | **7** | **3** | **1** | **3** |

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
| 3 | 建立"新增内容目录必须同步创建README"的门禁检查 | CI检查中新增目录README存在性验证 | P1 | ⏳ 待推进 | 需要在CI流水线中集成generate-readme.py --scan检查，属于CI集成阶段任务 |
| 4 | 统一所有文档frontmatter source字段格式为相对路径，消除docs/绝对路径混用 | grep搜索无 `source: "docs/` 格式的路径 | P1 | 🔄 **部分完成** | 本次修复docs/knowledge/operations/下4个问题（3个docs/前缀+1个不完整路径）；全库仍有历史遗留问题待批量修复，建议后续使用增强后的check-links.py --check-frontmatter-paths扫描全库批量修复 |
| 5 | 全面切换索引维护为自动生成，废弃手动编辑索引文件 | knowledge/README.md标记为自动生成区域，禁止手动编辑 | P1 | ✅ **已完成** | generate-readme.py + docgen.py已实现自动化索引生成，标记区域幂等覆盖 |

---

## P2（持续优化）

| # | 行动项 | 验收标准 | 优先级 | 状态 | 交付物/备注 |
|---|--------|---------|--------|------|------------|
| 6 | 增强check-links.py的--fix能力，支持frontmatter路径字段自动修复 | 自动修复frontmatter路径字段的深度错误和格式问题（docs/前缀→相对路径、不完整路径补全） | P2 | ⏳ 待推进 | 依赖check_frontmatter_paths()的检测结果，扩展--fix模式支持frontmatter修复 |
| 7 | 在创建新文档模板中内置正确的相对路径计算示例 | 模板中的source字段示例使用正确相对路径，不使用docs/前缀 | P2 | ⏳ 待推进 | 需要更新docs/templates/下的文档模板 |

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

## 后续推进建议

1. **批量修复P1 #4**：使用增强后的 `check-links.py --check-frontmatter-paths --fix`（待实现P2 #6后）扫描全库，批量修复docs/前缀问题
2. **CI集成P1 #3**：在ci-check.ps1/sh中添加generate-readme.py --scan检查
3. **模板更新P2 #7**：更新文档模板中的source字段示例为正确相对路径格式
4. **frontmatter自动修复P2 #6**：基于已实现的检测逻辑，扩展--fix模式支持frontmatter路径自动修复

---

## 关联文档

- **执行复盘**：[execution-retrospective.md](execution-retrospective.md)
- **洞察萃取**：[insight-extraction.md](insight-extraction.md)
- **主索引**：[README.md](README.md)
