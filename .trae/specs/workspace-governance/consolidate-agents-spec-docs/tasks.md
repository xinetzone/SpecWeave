# Tasks

> 链路：I→F→A→C（场景3 重构优化）。所有任务仅涉及 `.agents/` 规范文档（.md），不动脚本代码。
> 提交动作不在本清单内，须用户另行授权。

- [x] Task 1: 模板目录审计与归档候选确认：对 `templates/` 41 个根级单文件逐一判定「可复用模板 / 一次性交付物」，产出确认清单（含每个候选的判定依据：是否含项目特定数据、是否可参数化复用）。
  - [x] SubTask 1.1: 逐文件扫描根级模板，标记一次性交付物候选（基线：spec §2.3 的 3 个候选）
  - [x] SubTask 1.2: 对每个候选核验判定依据，输出最终归档清单（可增删候选，须附理由）
- [x] Task 2: 壳文件归一化（M1）：按统一模板（frontmatter + 一句话定位 + 导航表）重写 `rules/` 下 9 个壳文件，移除与分册重复的正文。
  - [x] SubTask 2.1: 逐壳核验导航表链接与分册实际文件一一对应（含 alternatives-guide 的 03/04/06/07 分册存在性）
  - [x] SubTask 2.2: 重写 9 个壳文件；alternatives-guide.md 的映射表若分册已覆盖则移除，否则保留并注明唯一性
- [x] Task 3: 格式缺陷修复（M2）：删除 `rules/stage-guardrails-guide.md` 中重复的 frontmatter+标题块（第 9-15 行区域），保留单一 frontmatter。
- [x] Task 4: 权限主题收敛（M3）：将 `worlds/collaboration/permissions.md` 中与 `teams/permission-system.md` 重复的 RBAC 模型定义段落替换为引用指针，仅保留扩展差异内容。
- [x] Task 5: 模板归档与准入标准（M4+M5）：按 Task 1 确认清单将一次性交付物迁移至 `templates/archive/`；更新 `templates/README.md`（归档清单 + 准入标准）；在 4 处复盘模板入口补充指向对比表的互链指针。
- [x] Task 6: 索引同步与链接验证（M6）：核验并更新 `rules/README.md`、`capability-registry.md` 及分册、根 `AGENTS.md`、`context-routing.md` 中受 Task 2-5 影响的条目；运行 `python .agents/scripts/check-links.py` 全仓验证零断链。
- [x] Task 7: 独立审查：委派无上下文子代理按 checklist.md 逐项复核全部检查点，输出审查结论（pass/需修复项）。

# Task Dependencies

- Task 2、Task 3、Task 4 相互独立，可并行执行
- Task 5 依赖 Task 1（归档清单）
- Task 6 依赖 Task 2、3、4、5 全部完成
- Task 7 依赖 Task 6
