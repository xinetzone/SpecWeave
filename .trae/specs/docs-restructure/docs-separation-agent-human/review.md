# .agents/docs 与 docs 分离方案 — 验证清单

## 规划阶段验证
- [ ] Checklist 1: 分类矩阵完整覆盖所有文件，无遗漏
- [ ] Checklist 2: Agent必留文件确实被路由表或规则引用
- [ ] Checklist 3: 迁移路线图包含批次划分、文件数量统计、依赖关系说明
- [ ] Checklist 4: 每批迁移文件数 ≤ 100 个
- [ ] Checklist 5: 路由表引用的文件放在最后批次迁移

## 迁移执行验证（每批次）
- [ ] Checklist 6: 文件成功移动到目标位置（源文件数 = 新位置文件数）
- [ ] Checklist 7: 路径引用已更新（无 `file:///` 绝对路径）
- [ ] Checklist 8: `check-links.py` 验证无死链
- [ ] Checklist 9: `check-move.py` 验证文件迁移完整性
- [ ] Checklist 10: 原子提交完成（遵循 Conventional Commits 规范）

## 规则更新验证
- [ ] Checklist 11: `global-core-rules.md` 路径解析规则更新正确
- [ ] Checklist 12: `global-core-rules.md` 内容敏感度分流产出物路径更新正确
- [ ] Checklist 13: `AGENTS.md` 文档边界声明与物理现实一致
- [ ] Checklist 14: `docs/DEPRECATED.md` 已替换为正常入口文档

## 收尾验证
- [ ] Checklist 15: `check-links.py` 全项目验证无死链
- [ ] Checklist 16: `.agents/docs/` 仅保留 6 个 agent 必读文件（agent-roles.md, collaboration.md, development-standards.md, knowledge-base.md, knowledge/README.md, retrospective/README.md）
- [ ] Checklist 17: `docs/` 包含所有人类文档，结构清晰
- [ ] Checklist 18: 空目录已清理
- [ ] Checklist 19: 主题 README 已登记完成状态
- [ ] Checklist 20: `context-routing.md` 中的路由引用路径更新正确

## Agent 路由验证
- [ ] Checklist 21: agent 启动时能正确加载 `.agents/docs/` 中的必读文件
- [ ] Checklist 22: agent 不会误读 `docs/` 中的人类文档（除非任务明确需要）
- [ ] Checklist 23: 路径解析规则无歧义，agent 不需要推理"该读哪个"