---
id: "export-suggestions"
title: "改进建议与行动计划"
parent: "retrospective-large-file-atomization-batch-20260703"
date: "2026-07-03"
action_items_count: 5
high_priority: 2
medium_priority: 2
low_priority: 1
---

# 改进建议与行动计划

## 高优先级行动项（立即执行）

### 行动项1：在atomic-commit-cmd中增加"三查暂存"检查

**问题**：git add后容易遗漏删除文件的暂存，或误加入__pycache__等构建产物
**改进措施**：
- 在原子提交流程中增加强制检查步骤：git status --short
- 自动检查是否有D状态（deleted）未暂存
- 自动检测并警告*.pyc、__pycache__等文件是否被加入暂存区
**预期效果**：消除漏提交和误提交问题，amend率降低80%以上
**验收标准**：连续10次原子提交不需要amend修复暂存问题
**建议完成时间**：2026-07-04

### 行动项2：文档化Windows环境git中文提交最佳实践

**问题**：Windows PowerShell直接传递中文commit message容易乱码
**改进措施**：
- 在开发规范中明确：Windows环境下使用临时文件法（commit-msg.txt）提交中文信息
- 提供标准命令模板
- 在atomic-commit-cmd中自动使用此方法
**预期效果**：彻底解决Windows中文提交乱码问题
**验收标准**：连续20次中文提交无乱码
**建议完成时间**：2026-07-04

## 中优先级行动项（近期规划）

### 行动项3：固化"三段式"拆分架构模板

**问题**：每次拆分都要重复编写类似的__init__.py、cli.py垫片模板
**改进措施**：
- 将三段式拆分架构沉淀为标准模板
- 创建模板文件：__init__.py.tpl、cli_shim.py.tpl、constants.py.tpl、models.py.tpl
- 编写拆分checklist
**预期效果**：新文件拆分准备时间减少50%
**验收标准**：使用模板拆分一个新文件比不使用模板节省至少5分钟
**建议完成时间**：2026-07-05

### 行动项4：在CI中增加大文件门禁检查

**问题**：目前大文件是事后拆分，无法阻止新的大文件引入
**改进措施**：
- 在ci-check-cmd中增加文件大小检查
- >300行：警告
- >500行：阻断提交/合并
**预期效果**：从"事后拆分"转向"事前预防"，从源头控制大文件产生
**验收标准**：新增代码中不允许出现>500行文件，>300行文件有明确说明
**建议完成时间**：2026-07-05

## 低优先级行动项（长期优化）

### 行动项5：开发半自动化拆分辅助脚本

**问题**：手动创建目录和模板文件仍有重复劳动
**改进措施**：
- 编写atomization-assist.py脚本
- 功能1：自动创建包目录结构
- 功能2：自动生成标准模板文件
- 功能3：自动生成薄垫片代码框架
- 功能4：给出拆分建议（按什么维度拆分）
**预期效果**：拆分准备工作自动化率达60%以上
**验收标准**：使用辅助脚本完成一个文件拆分比纯手动节省10分钟以上
**建议完成时间**：2026-07-10

## 模式沉淀计划

| 模式名称 | 目标路径 | 成熟度 | 沉淀时间 |
|---------|---------|--------|---------|
| 三段式原子化拆分架构 | docs/retrospective/patterns/technical-patterns/atomization-three-layer-arch.md | L3 | 2026-07-05 |
| Windows git中文提交方案 | docs/retrospective/patterns/tooling-patterns/git-windows-utf8-commit.md | L2 | 2026-07-04 |
| 原子提交三查验证法 | docs/retrospective/patterns/methodology-patterns/atomic-commit-three-check.md | L2 | 2026-07-04 |
