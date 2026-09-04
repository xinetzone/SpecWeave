# Jira Skill 架构洞察与知识地图

> I阶段产出：基于 facts.md 提炼的核心洞察和文档结构设计。

## 一、核心架构洞察

### 洞察1：双技能职责分离——API操作与内容语法正交

- **陈述**：jira-skill 将 Jira 集成为两个正交技能：jira-communication 负责"与Jira对话"（API操作），jira-syntax 负责"对Jira说话"（内容格式），两者无运行时依赖。
- **证据**：F-P002, F-D001~D008；jira-communication 有完整的 Python 脚本体系，jira-syntax 仅有模板、参考文档和 shell 验证脚本，无 Python 代码。
- **反常识**：初学者可能以为这是一个单体插件，但实际上 jira-syntax 是纯静态内容技能——它不调用任何 API，只提供语法参考和模板。两者通过工作流约定（先写内容→验证→提交）协作，而非代码依赖。
- **行动**：OKF Wiki 应将两个技能作为独立概念文档处理，但在"工作流集成"章节说明它们如何配合使用。

### 洞察2：脚本化架构——零MCP开销的设计取舍

- **陈述**：v3.x 彻底移除了 Docker MCP 依赖，改为通过 `uv run` 直接执行 PEP 723 自包含 Python 脚本，每个脚本声明内联依赖，无需虚拟环境。
- **证据**：F-P008（所有脚本 shebang 为 `#!/usr/bin/env -S uv run --script`）；F-G004（PYTHONPATH 引导模式）；README.md 明确列出"Zero MCP overhead"特性。
- **反常识**：与当时主流的 MCP Server 模式相反，该项目选择"脚本直连"而非"工具描述注册"。这意味着 AI 智能体不通过 MCP 协议发现工具，而是通过 SKILL.md 中的自然语言描述了解何时调用哪个脚本。这牺牲了自动发现能力，换取了零上下文开销和快速启动。
- **行动**：文档应解释 PEP 723 内联依赖机制和 uv run 执行模型，这是理解整个插件架构的基础。

### 洞察3：三层脚本分类——core/workflow/utility 的职责边界

- **陈述**：21个 Python 脚本按职责分为三层：core（6个原子操作）、workflow（8个业务流程组合）、utility（7个辅助查询），共享 lib/ 中的11个基础库。
- **证据**：F-D001~D004, F-C001~C024, F-W001~W023, F-U001~U007。
- **反常识**：脚本的分类不是按 Jira API 端点划分，而是按"操作粒度"划分——core 提供 get/update/add 等原子操作，workflow 组合多步操作（如 transition path 自动寻路、qa-gather 一次性聚合），utility 提供字段/用户查询等辅助能力。同一 Jira 资源（如 issue）可能在三个层级都有涉及。
- **行动**：概念文档应按三层结构组织 API 参考，但学习路径应从"常见任务"角度引导（如"搜索工单"→core/jira-search，"批量流转"→workflow/jira-transition path）。

### 洞察4：意图动词机制——从工具调用到工作流语义

- **陈述**：jira-issue.py 提供 work/qa/qa-fail/act 四个意图动词，将常见工作流模式（开始处理工单、QA审查、QA打回、执行状态变更）封装为单次调用，自动聚合所需上下文。
- **证据**：F-C004~C007, F-C009（INTENT_FIELDS 定义意图命令获取的字段集）。
- **反常识**：这些不是简单的 API 包装——work 命令会获取工单详情+评论+状态历史+时间统计；qa-gather（utility层）会一次性拉取工单+描述+评论+工时+链接+同级工单。这体现了"AI智能体调用模式"的设计：减少往返次数，一次获取决策所需的全部上下文。
- **行动**：最佳实践章节应强调"优先使用意图动词而非组合原子命令"，这是区别于传统 Jira CLI 的核心使用模式。

### 洞察5：双部署兼容——自动检测与API差异处理

- **陈述**：通过 is_cloud_url() 自动检测 Cloud vs Server/DC，在客户端层面处理 API 差异（如 Cloud 使用 search/jql 端点、用户标识用 accountId vs username）。
- **证据**：F-L004~L005, F-L019, F-L038；LazyJiraClient._jql_cloud() 专门处理 Cloud JQL 分页。
- **反常识**：依赖 atlassian-python-api 被故意锁定在 v3（>=3.41,<4），因为 v4 虽然修复了 Cloud 问题但引入了 DC 回归。项目主要目标是 Jira Server/DC 9.12，Cloud 支持是次要的。这与"总是升级到最新版"的直觉相反。
- **行动**：安装配置章节应明确两种部署的认证差异，故障排查章节应记录 v4 锁定的原因。

## 二、知识地图

### 文档分组与学习路径

```
入门篇（Foundational）
├── 00-overview        教程总览、核心特性、版本演进
├── 01-architecture    双技能架构、三层脚本、数据流
└── 02-installation    安装方式、凭证配置、环境校验

核心篇（Core）
├── 03-quickstart          快速上手指南
├── 04-jira-communication  API操作技能详解
├── 05-jira-syntax         语法规范技能详解
└── 06-jql                 JQL查询语言参考

高级篇（Advanced）
├── 07-best-practices  意图动词、dry-run、安全实践
├── 08-troubleshooting 故障排查指南
└── 09-glossary        术语表与资源
```

### OKF Bundle 目录结构设计

```
jira-skill-wiki/                    # Bundle 根目录
├── index.md                        # 根索引（含 okf_version frontmatter）
├── log.md                          # 变更日志
├── concepts/                       # 概念文档（从现有wiki转换）
│   ├── index.md                    # 概念索引（无frontmatter）
│   ├── 00-overview.md
│   ├── 01-architecture.md
│   ├── 02-installation.md
│   ├── 03-quickstart.md
│   ├── 04-jira-communication.md
│   ├── 05-jira-syntax.md
│   ├── 06-jql.md
│   ├── 07-best-practices.md
│   ├── 08-troubleshooting.md
│   └── 09-glossary.md
├── examples/                       # 示例文档（新增）
│   ├── index.md
│   ├── basic-cli-usage.md          # 基础CLI使用示例
│   ├── workflow-automation.md      # 工作流自动化示例
│   └── syntax-templates.md         # 语法模板使用示例
└── references/                     # 信源登记
    ├── index.md
    ├── source-code.md              # 源码结构信源
    ├── api-reference.md            # API参考信源
    └── official-docs.md            # 官方文档信源
```

### 文档-事实覆盖矩阵

| 文档 | 覆盖事实ID范围 |
|------|---------------|
| 00-overview | F-P001~P010, 版本演进 |
| 01-architecture | F-D001~D008, F-L001~L051, 洞察1-3 |
| 02-installation | F-P005~P006, F-L014~L020, F-C020~C024 |
| 03-quickstart | F-G001~G005, 核心命令示例 |
| 04-jira-communication | F-C001~C024, F-W001~W023, F-U001~U007, 洞察3-4 |
| 05-jira-syntax | F-S001~S015 |
| 06-jql | JQL参考文档内容, F-L050, F-C010~C012 |
| 07-best-practices | 洞察4-5, references/最佳实践 |
| 08-troubleshooting | references/troubleshooting, 常见错误 |
| 09-glossary | 术语汇总 |

## 三、转换策略

现有wiki已有10个结构良好的文档（00-09），转换策略为：

1. **重组目录结构**：将现有10个文档移入 concepts/ 子目录
2. **升级 frontmatter**：将现有YAML头转换为OKF v0.2规范格式（添加 type/description/generated/verified/status/stale_after/sources）
3. **补充信源溯源**：在 references/ 下创建信源登记文件，每个概念文档的 sources 字段指向对应信源
4. **新增示例文档**：在 examples/ 下创建3个实操示例文档
5. **生成索引文件**：根 index.md（含 okf_version）、concepts/index.md、examples/index.md、references/index.md
6. **创建变更日志**：log.md 记录本次转换
7. **交叉链接规范化**：将现有相对链接改为 OKF bundle-relative `/` 开头路径
