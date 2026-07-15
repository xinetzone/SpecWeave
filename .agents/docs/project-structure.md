# 项目结构

> **来源**：从 `README.md` "项目结构"章节拆分

## 目录树

```
.
├── AGENTS.md                 # 智能体全局契约（最高优先级入口）
├── LICENSE                   # Apache 2.0 许可证
├── README.md                 # 项目说明文档（入口文件）
├── CONTRIBUTING.md           # 贡献指南
├── .gitignore                # Git 忽略规则
├── .agents/                  # 智能体规范容器
│   ├── README.md             # 目录说明与使用指引
│   ├── roles/                # 智能体角色定义（5 个角色 + 索引）
│   ├── prompts/              # 系统提示词与 few-shot 示例（按角色分子目录）
│   ├── tools/                # 工具调用规范（文件/执行/搜索/通信）
│   ├── protocols/            # 协作协议（交接/消息/冲突/依赖）
│   ├── workflows/            # 标准工作流（开发/审查/测试）
│   ├── templates/            # 任务与交接模板
│   └── scripts/              # 验证与自动化脚本
├── .trae/
│   └── specs/                # 规格驱动开发文档（spec/tasks/checklist）
├── docs/                     # 项目文档与知识库
│   ├── knowledge/            # 技术知识库（决策记录、运维手册、故障排查）
│   ├── retrospective/        # 复盘文档体系（报告、模式、模板、框架、概念）
│   ├── templates/            # 文档模板（README 模板）
│   └── task-summaries/       # 任务执行总结
├── apps/                     # 新应用开发工作空间
│   ├── shared/               # 应用间共享模块
│   └── README.md             # 目录使用说明与开发规范
└── vendor/                   # 第三方库依赖（已被 .gitignore 排除）
```

## 目录职责说明

| 目录 | 职责 | 面向对象 |
|------|------|---------|
| `.agents/` | 智能体规范容器，存放角色、提示词、协议、工作流等 | AI 智能体 |
| `.trae/specs/` | 规格驱动开发文档，包含 spec.md、tasks.md、checklist.md | 开发者 + AI 智能体 |
| `docs/` | 项目文档与知识库，包含技术知识库、复盘体系、模板 | 人类读者 |
| `apps/` | 新应用开发专用工作空间，新应用须先在 .temp/ 暂存开发后迁移至此 | 开发者 + AI 智能体 |
| `vendor/` | 第三方库依赖存放位置，已被 `.gitignore` 排除 | 运行时 |

> **说明**：`vendor/` 目录用于存放第三方库依赖，已被 `.gitignore` 排除，不会纳入版本控制。详见 [临时依赖管理](../protocols/dependency-management.md)。

> **关联模块**：
> - `../README.md`
> - `project-overview.md`
> - `../.agents/README.md`