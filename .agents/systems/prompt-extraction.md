---
id: "systems-prompt-extraction"
title: "提示词萃取系统（prompt_extraction）"
source: "AGENTS.md#核心规范入口"
x-toml-ref: "../../.meta/toml/.agents/systems/prompt-extraction.toml"
---
# 提示词萃取系统（prompt_extraction）

独立的 Python 子项目，实现从对话记录中自动萃取可复用提示词模式的完整流水线。

## 系统架构

| 模块 | 组件 | 功能 |
|------|------|------|
| 输入层 | `input/` | 对话记录解析与结构化 |
| 预处理层 | `preprocessing/` | 数据清洗与标准化 |
| 萃取层 | `extraction/` | 提示词模式提取 |
| 优化层 | `optimization/` | 模式调优与去重 |
| 评估层 | `assessment/` | 质量评估与评分 |
| 界面层 | `ui/` | Streamlit Web 界面（含雷达图、差异查看器） |
| 测试层 | `tests/` | 7 个测试模块的完整测试套件 |
