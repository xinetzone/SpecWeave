> **来源**：从 `docs/retrospective/knowledge-extraction.md` 四、可复用模板 拆分

# spec.md 模板

```markdown
# {项目名称} Spec

## Why
{1-3 段描述：为什么需要这个变更？解决什么问题？}

## What Changes
- {变更项 1}
- {变更项 2}

## Impact
- Affected specs: {受影响的 spec 目录或无}
- Affected code: {受影响的代码文件或无}

## ADDED Requirements

### Requirement: {需求名称}
{一句话描述需求}

#### Scenario: {场景名称}
- **WHEN** {触发条件}
- **THEN** {预期结果}

## MODIFIED Requirements

### Requirement: {需求名称}
{修改后的描述}

## REMOVED Requirements

### Requirement: {需求名称}
{删除原因}
```

> **关联模块**：
> - `patterns/methodology-patterns/spec-driven-development.md`
> - `templates/tasks-template.md`
> - `templates/checklist-template.md`