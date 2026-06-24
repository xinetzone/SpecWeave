> **来源**：从 `docs/retrospective/knowledge-extraction.md` 四、可复用模板 拆分

# checklist.md 模板

```markdown
# Checklist

## {检查类别 1}
- [ ] {检查点 1}
- [ ] {检查点 2}

## {检查类别 2}
- [ ] {检查点 3}
- [ ] {检查点 4}

## 关联系统影响
- [ ] 检查是否需要同步更新 AGENTS.md（上下文路由表、角色索引、协作协议概要）
- [ ] 检查是否需要同步更新 .agents/ 下的相关规范文件
- [ ] 检查是否需要同步更新 docs/project-structure.md（目录树、职责说明表）

## 验证
- [ ] 对 {N} 个目标执行检查，结果符合预期
```

> **关联模块**：
> - `patterns/methodology-patterns/spec-driven-development.md`
> - `templates/spec-template.md`
> - `templates/tasks-template.md`