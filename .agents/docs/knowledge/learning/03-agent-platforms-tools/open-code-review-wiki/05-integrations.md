---
id: "open-code-review-wiki-05"
title: "集成与高级用法"
source: "../open-code-review-wiki.md#集成与高级用法"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/open-code-review-wiki/05-integrations.toml"
---
# 集成与高级用法

Open Code Review 不仅可作为独立 CLI 工具使用，还提供了与 Claude Code、CI/CD 流水线的原生集成能力，并支持自定义评审规则、可观测性与 Web 视图等高级用法。本章介绍如何将 Open Code Review 嵌入到现有的开发工作流中。

## 一、Claude Code 集成

Open Code Review 提供了对 Claude Code 的原生集成，支持 **Command** 和 **Skills** 两种接入方式，执行对应命令即可完成安装（在此之前请先参考基础使用章节配置你的模型端点）。

### 1.1 两种接入方式对比

| 特性 | Command | Skills（CLAUDE.md） |
| --- | --- | --- |
| 触发方式 | 用户主动调用 /open-code-review | 每次对话自动加载 |
| 本质 | 可复用的任务提示词模板 | 持久的行为规范、常驻上下文 |
| 灵活性 | 支持参数传入 | 静态内容，全局生效 |
| 适用场景 | 特定任务的快捷入口 | 项目级约束与背景知识 |

### 1.2 Command 安装

```bash
mkdir -p ~/.claude/commands && curl -fsSL "https://code.alibaba-inc.com/open-code-review/cc-integrated/raw/master/.claude/commands/open-code-review.md" -o ~/.claude/commands/open-code-review.md
```

### 1.3 Skills 安装

```bash
mkdir -p ~/.claude/skills/open-code-review && curl -fsSL "https://code.alibaba-inc.com/open-code-review/cc-integrated/raw/master/.claude/skills/open-code-review/SKILL.md" -o ~/.claude/skills/open-code-review/SKILL.md
```

### 1.4 Claude Code 集成的四大工作机制

安装完成后，你可以在 Claude Code 的任意工作流中随时触发 Open Code Review。其核心工作机制如下：

- **上下文隔离**：评审任务在独立线程中执行，全程不污染当前主任务的上下文。
- **需求感知**：Agent 会自动判断是否需要提取当前需求背景，并将其注入评审上下文，从而对需求完成度与实现一致性进行深度评审。
- **置信度分级**：评审结果按 High / Medium / Low 三级过滤，自动丢弃低置信度意见，只呈现真正有价值的问题。
- **自动修复**：对于值得采纳的建议，Agent 可直接发起自动修复，减少人工介入成本。

这种集成方式让专业的代码评审无缝嵌入编码过程，**真正将评审左移至编码阶段**，在问题产生的第一现场将其拦截。与此同时，借助上游 Agent 已有的需求上下文，能够更准确地区分哪些问题值得修复、哪些是 by design 的合理决策，从而避免误报干扰，整个过程无需人工介入。

## 二、GitHub/GitLab CI 流水线集成

Open Code Review 天然适配 CI/CD 场景——`--format json` 输出结构化的评审结果（包含文件路径、行号、问题描述、修复建议），`--audience agent` 静默所有进度输出，两者组合即可获得纯净的机器可读输出，方便下游脚本解析并回写到代码平台。

### 2.1 核心命令

```bash
ocr review --from "origin/$BASE_BRANCH" --to "origin/$HEAD_BRANCH" \
    --format json --audience agent
```

### 2.2 GitHub Actions 集成

在 `examples/` 目录下提供了 GitHub Actions 的完整集成示例，开箱可用，只需配置模型端点即可在 PR 创建时自动触发评审。

### 2.3 GitLab CI 集成

`examples/gitlab_ci/` 目录下提供了 GitLab CI 的完整集成示例：

- 在 Merge Request 创建时自动触发评审
- 评审结果通过 GitLab Discussions API 以**行级讨论**的形式回写到 MR
- 支持自托管 GitLab 实例

### 2.4 CI 集成所需环境变量

两套方案只需配置一个模型端点（通过 CI Secrets/Variables 注入），无需额外改造现有流水线：

- `OCR_LLM_URL`：LLM 服务端点
- `OCR_LLM_AUTH_TOKEN`：LLM 认证令牌
- `OCR_LLM_MODEL`：使用的模型名称

## 三、自定义评审规则

Open Code Review 通过四层链路解析评审规则。每层采用首次匹配原则（first-match-wins）：如果文件路径匹配到某个模式，则使用该规则；否则穿透到下一层。

### 3.1 四层链路解析（优先级从高到低）

| 优先级 | 来源 | 路径 | 描述 |
| --- | --- | --- | --- |
| 1 | --rule 参数 | 用户指定路径 | CLI 显式覆盖 |
| 2 | 项目配置 | `<repoDir>/.opencodereview/rule.json` | 项目级规则，可用 git 管理 |
| 3 | 全局配置 | `~/.opencodereview/rule.json` | 用户级规则 |
| 4 | 系统默认 | 内嵌 | 覆盖常见语言和文件类型的内置规则 |

### 3.2 规则配置文件格式

```json
{
  "rules": [
    {
      "path": "force-api/**/*.java",
      "rule": "所有对外接口必须使用 AuthType 注解进行鉴权"
    },
    {
      "path": "**/*mapper*.xml",
      "rule": "检查 SQL 注入风险、参数错误和缺少闭合标签"
    }
  ]
}
```

### 3.3 规则匹配说明

- `path` 支持 `**` 递归匹配和 `{java,kt}` 大括号展开。
- 在每一层内，规则按声明顺序评估——首次匹配生效。
- 如果规则文件不存在，将被静默跳过。

## 四、OpenTelemetry 可观测性

Open Code Review 内置 OpenTelemetry 支持，可上报评审过程的 spans 和 metrics，便于监控和调优：

```bash
ocr config set telemetry.enabled true
ocr config set telemetry.exporter otlp
ocr config set telemetry.otlp_endpoint localhost:4317
ocr config set telemetry.content_logging true  # 可选：包含 LLM prompt 内容
```

其中 `telemetry.content_logging` 设置为 `true` 时会在遥测数据中包含 LLM prompt 内容，便于调试。

## 五、Web 视图

启动内置 WebUI 查看器，可视化浏览历史评审会话：

```bash
ocr viewer
ocr viewer --addr :3000
```

通过 Web 视图可以更直观地查看每次评审的详细结果、问题分布与历史趋势，便于团队回顾与质量跟踪。
