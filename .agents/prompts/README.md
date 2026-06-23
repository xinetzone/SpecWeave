# 提示词使用说明

本目录包含多智能体协作系统中各角色的系统提示词与 Few-shot 示例，用于指导角色在执行任务时的行为规范与输出格式。

## 目录结构

```
.agents/prompts/
├── README.md                    # 本文件，使用说明
├── orchestrator/
│   ├── system-prompt.md         # 编排协调者系统提示词
│   └── few-shot.md              # 编排协调者 Few-shot 示例
├── architect/
│   ├── system-prompt.md         # 架构师系统提示词
│   └── few-shot.md              # 架构师 Few-shot 示例
├── developer/
│   ├── system-prompt.md         # 开发者系统提示词
│   └── few-shot.md              # 开发者 Few-shot 示例
├── reviewer/
│   ├── system-prompt.md         # 代码审查者系统提示词
│   └── few-shot.md              # 代码审查者 Few-shot 示例
└── tester/
    ├── system-prompt.md         # 测试工程师系统提示词
    └── few-shot.md              # 测试工程师 Few-shot 示例
```

## 文件说明

### system-prompt.md
每个角色的系统提示词，包含四个部分：
- **角色定位**：描述角色在多智能体协作中的定位与职责边界。
- **能力描述**：列出该角色的核心能力，3-5 条。
- **行为约束**：列出该角色必须遵守的约束，3-5 条。
- **输出格式要求**：描述该角色的输出格式规范。

### few-shot.md
每个角色的 Few-shot 示例，包含 2 个示例：
- 每个示例包含场景描述、输入内容与输出内容。
- 示例用于指导角色在类似场景下的输出风格与结构。

## 使用方法

1. **角色初始化**：在角色实例化时，加载对应的 `system-prompt.md` 作为系统提示词。
2. **Few-shot 注入**：在角色首次执行任务前，将 `few-shot.md` 中的示例作为上下文注入。
3. **角色绑定**：角色定义文件位于 `.agents/roles/`，通过 `id` 字段与提示词目录关联。
4. **输出校验**：根据 `system-prompt.md` 中的输出格式要求校验角色输出是否符合规范。
5. **协作流程**：orchestrator 负责调用各角色并按照交接协议传递上下文。

## 角色与提示词映射

| 角色 | 角色定义文件 | 系统提示词 | Few-shot 示例 |
|---|---|---|---|
| 编排协调者 | roles/orchestrator.md | prompts/orchestrator/system-prompt.md | prompts/orchestrator/few-shot.md |
| 架构师 | roles/architect.md | prompts/architect/system-prompt.md | prompts/architect/few-shot.md |
| 开发者 | roles/developer.md | prompts/developer/system-prompt.md | prompts/developer/few-shot.md |
| 代码审查者 | roles/reviewer.md | prompts/reviewer/system-prompt.md | prompts/reviewer/few-shot.md |
| 测试工程师 | roles/tester.md | prompts/tester/system-prompt.md | prompts/tester/few-shot.md |
