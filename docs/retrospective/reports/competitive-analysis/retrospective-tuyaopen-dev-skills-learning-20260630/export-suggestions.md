---
id: "retrospective-tuyaopen-dev-skills-learning-20260630-export"
source: "docs/knowledge/learning/tuyaopen-dev-skills-learning.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/competitive-analysis/retrospective-tuyaopen-dev-skills-learning-20260630/export-suggestions.toml"
---
# 导出建议

## 一、导出包内容（本次已生成）

| 文件 | 用途 |
|------|------|
| [exports/tuyaopen-dev-skills-report.md](exports/tuyaopen-dev-skills-report.md) | 可直接转发的精简版报告（适合分享给团队或沉淀到知识库） |
| [exports/tuyaopen-dev-skills-report.json](exports/tuyaopen-dev-skills-report.json) | 结构化摘要，适合后续自动化索引/检索/对比 |
| [exports/manifest.txt](exports/manifest.txt) | 导出清单（便于归档与校验） |

## 二、落地建议（如果要把方法论迁移到你们自己的 Skill 体系）

| ID | 建议 | 优先级 | 验收标准 |
|---|---|---|---|
| IMP-001 | 为“脚本型能力”统一提供 `--json` 输出契约（ok/error/关键字段） | 高 | 任意脚本可被上层流程稳定解析；失败时 exit code 非 0 |
| IMP-002 | 对接受路径参数的脚本默认加“路径越界防护” | 高 | 传入 repo_root 外路径时能被阻断并提示错误 |
| IMP-003 | 对需要跨命令共享状态的脚本引入“session file 外部化” | 中 | start/tail/stop 可在不同进程/不同终端安全协同 |
| IMP-004 | 对 kill/stop 类操作增加“停止前身份校验” | 中 | kill 只作用于目标进程，避免误杀 |
| IMP-005 | pytest 优先覆盖“环境不确定性”（目录查找、env 优先级、session dir） | 中 | 在不同 OS/路径结构下行为一致 |

## 三、导出命名与归档建议

- 建议统一命名：`tuyaopen-dev-skills-report-YYYYMMDD.{md,json}`
- 对外分享：只需要 `*.md`
- 做自动化入库：同时保留 `*.json` 方便机器消费

