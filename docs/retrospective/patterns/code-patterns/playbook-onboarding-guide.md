---
id: "playbook-onboarding-guide"
source: "../../reports/competitive-analysis/retrospective-minitest-ecosystem-learning-20260707/insight-extraction.md#模式8"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/code-patterns/playbook-onboarding-guide.toml"
maturity: "L1"
validation_count: 1
reuse_count: 0
documentation_level: "standard"
related_patterns:
  -   - "cli-skill-pair-sync"
---
> **来源**：从Minitest AI QA测试平台生态系统复盘萃取，经Minitest CLI验证

# Playbook引导Onboarding模式（Playbook Guided Onboarding Pattern）

## 模式类型

代码模式（CLI工具首次使用引导）

## 成熟度

L1 首次萃取（Minitest CLI验证）

## 适用场景

功能丰富、工作流复杂的CLI工具首次使用引导。

## 问题背景

新用户/AI Agent首次使用复杂CLI工具时，不知道从何开始，需要阅读大量文档才能完成首次端到端流程。

## 核心规则

### 方案

- `minitest init`命令输出结构化的onboarding playbook
- 自动检测执行环境（TTY/非TTY/Agent环境变量）
- Agent模式（非交互/--json/--agent）：直接输出原始markdown到stdout，无装饰
- 人类交互模式：Rich渲染markdown，输出介绍和提示到stderr
- Playbook按顺序引导完成7个步骤：认证→查找/创建应用→定义Personas→映射用户旅程→创建带依赖的场景→上传构建→运行测试

### 环境检测与输出策略

| 执行环境 | 输出策略 | 实现方式 | 目的 |
|---------|---------|---------|------|
| TTY（人类交互） | Rich渲染markdown | 使用Rich库渲染表格、spinner、彩色状态消息 | 提升交互体验 |
| 非TTY（脚本/CI） | 原始markdown到stdout | 直接输出无装饰的markdown | 便于脚本处理 |
| Agent模式 | 原始markdown到stdout | `--agent`参数触发 | Agent可直接按步骤执行 |

### Playbook步骤结构

| 步骤序号 | 步骤名称 | 核心任务 |
|---------|---------|---------|
| 1 | 认证 | 完成CLI认证配置 |
| 2 | 查找/创建应用 | 定位或创建测试应用 |
| 3 | 定义Personas | 定义测试角色和用户画像 |
| 4 | 映射用户旅程 | 定义用户旅程和场景路径 |
| 5 | 创建带依赖的场景 | 创建测试场景及其依赖关系 |
| 6 | 上传构建 | 上传应用构建文件 |
| 7 | 运行测试 | 执行测试并查看结果 |

## 验证清单

- [ ] `minitest init`命令输出结构化的onboarding playbook
- [ ] 自动检测TTY/非TTY环境
- [ ] Agent模式（`--agent`）输出原始markdown到stdout
- [ ] 人类交互模式使用Rich渲染markdown
- [ ] Playbook包含完整的7步引导流程

## 最佳实践

- **一行安装**：`curl -fsSL https://.../install.sh \| bash`（install.sh/install.ps1）
- **init引导**：`minitest init`自动检测环境，输出7步onboarding playbook
- **依赖图Mermaid可视化**：`minitest apps dependencies <id>`输出flowchart TD
- **--watch实时流式输出**：`minitest run start --watch`每2秒轮询，Rich spinner显示状态
- **Rich精美输出**：使用Rich库渲染表格、spinner、彩色状态消息
- **非阻塞更新检查**：24小时缓存，在main callback中异步检查，不阻塞命令执行

## 与cli-skill-pair-sync的关系

本模式是cli-skill-pair-sync在用户引导场景的延伸，确保新用户和AI Agent都能通过结构化的playbook快速完成首次端到端流程，降低使用门槛。
