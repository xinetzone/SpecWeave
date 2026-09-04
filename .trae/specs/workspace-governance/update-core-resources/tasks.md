# Tasks

- [x] Task 1: 运行 `docgen.py stats` 自动更新 README.md 和 AGENTS.md 核心数据
  - 执行 `python .agents/scripts/docgen.py stats`
  - 验证 README.md 徽章区域数据已更新
  - 验证 AGENTS.md changelog 最新条目数据已更新
  - 验证两个文件中的核心指标（Skill 数量、指令集数量）一致

- [x] Task 2: 更新 .agents/README.md 目录结构
  - 在目录树中补充 `brand/` 目录条目
  - 更新目录树中所有子目录的统计数据注释（脚本数、Skill 数、规则数、指令集数）
  - 验证目录树与实际文件系统结构一致

- [x] Task 3: 更新 .agents/README.md 子目录职责表
  - 更新 commands/ 行的指令集数量（从 10 个更新为实际值）
  - 更新 skills/ 行的 Skill 数量（从 16 个更新为实际值）
  - 更新 scripts/ 行的脚本数量（从 320+ 更新为实际值）
  - 更新 rules/ 行的规则文件数量
  - 更新 "与 AGENTS.md 的关系" 章节中的统计数据
  - 验证所有计数与文件系统实际一致

- [x] Task 4: 全局一致性验证
  - 对比 README.md、AGENTS.md、.agents/README.md 三份文件中的核心数据指标
  - 确认同一指标在三处文档中数值一致
  - 运行 `python .agents/scripts/check-links.py --path .agents/README.md` 确保链接有效

# Task Dependencies

- Task 1 无依赖，可独立执行
- Task 2、Task 3 依赖 Task 1 完成后的实际数据作为参考，但可并行执行
- Task 4 依赖 Task 1、2、3 全部完成