# Tasks

- [x] Task 1: R 阶段——双目录事实采集（并行）
  - [x] SubTask 1.1: 子代理 A 盘点 `external/dao/xinzo/.trae`：顶层结构、skills 全量清单（名称+子文件概况）、配置文件清单（argv.json、*-config.json、installed-plugins.json、permission/global.json、builtin manifests 版本）、binaries/extensions/memory/.cleanup 记录；只读，不记录 token 值
  - [x] SubTask 1.2: 子代理 B 盘点 `external/dao/xinzo/.trae-cn`：同 1.1 口径，另含 sandbox.json、permission/work/ 双层结构、local-* 系列 skills 的 info.json/meta.json 要点
  - [x] SubTask 1.3: 汇总两份盘点为 `facts.md`（含共有/独有 skills 对照表），执行 G1 检查（无"因为/导致/所以"等因果词），输出 CMD-LOG
- [x] Task 2: I 阶段——双版对比洞察
  - [x] SubTask 2.1: 基于 facts.md 沿四主线（双版漂移、技能冗余、配置安全、治理机会）产出四元组洞察，写入 `insights.md`
  - [x] SubTask 2.2: 执行 G2 检查（每条洞察四元组完整），输出 CMD-LOG
- [x] Task 3: E 阶段——模式萃取
  - [x] SubTask 3.1: 从洞察提炼可复用模式（如"双版本环境漂移治理"），每个模式含触发场景+核心步骤+反模式+迁移验证，写入 `patterns.md`
  - [x] SubTask 3.2: 执行 G3 检查（模式可迁移三要素齐全），输出 CMD-LOG
- [x] Task 4: 报告导出与收尾
  - [x] SubTask 4.1: 汇总 R/I/E 产出，生成 `playground/reports/trae-env-retrospective-20260901/README.md`（frontmatter 含 source 溯源，正文脱敏无凭证值）
  - [x] SubTask 4.2: 验证两个被分析目录零写入（抽查文件未被修改）、报告内无 token 值、checklist 逐项核验

# Task Dependencies

- Task 2 依赖 Task 1（洞察必须基于已登记事实）
- Task 3 依赖 Task 2（模式必须基于洞察）
- Task 4 依赖 Task 1/2/3
- SubTask 1.1 与 1.2 可并行执行
