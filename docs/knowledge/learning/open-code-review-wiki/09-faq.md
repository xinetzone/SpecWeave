---
id: "open-code-review-wiki-09"
title: "常见问题（FAQ）"
source: "../open-code-review-wiki.md#常见问题faq"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/open-code-review-wiki/09-faq.toml"
---

# 常见问题（FAQ）

> 本章节汇总使用 Open Code Review 过程中的常见疑问，基于原文内容提供清晰准确的解答。

---

### Q1: Open Code Review 适合什么场景使用？

**A**: Open Code Review 适合以下场景：

1. **工程级稳定代码评审**：追求高准确率（25-38%）、低噪声的团队代码评审，F1 综合指标最优达 25.10%
2. **CI/CD 流水线集成**：Token 消耗可控（352K-743K），适合大规模自动化评审
3. **大型仓库评审**：分治策略 + 上下文隔离，变更规模翻倍时 Token 仅线性增长
4. **多语言混合项目**：内置 13 套语言/文件类型专属规则，开箱即用
5. **审计陌生代码库**：使用 `ocr scan` 全量扫描模式，无需 diff 即可审查整份源码

**不适合的场景**：安全审计等"宁可错杀不可放过"的场景，建议配合 Claude Code 使用以最大化召回率（CC 最优 28.90% vs OCR 最优 20.00%）。

---

### Q2: ocr review 和 ocr scan 有什么区别？

**A**: 两者核心区别在于评审对象：

| 维度 | `ocr review` | `ocr scan` |
|------|--------------|------------|
| 评审对象 | 变更（diff） | 完整文件 |
| 依赖 Git | 是，需要 diff | 否，非 Git 目录也可（自动回退到文件系统遍历） |
| 典型场景 | PR/MR 评审、commit 评审 | 审计陌生代码库、迁移前体检、存量代码扫描 |
| 多阶段流程 | 标准评审循环 | Plan 阶段 + 批次评审 + Dedup 去重 + Project Summary |
| 成本控制 | 分治策略，Token 线性可控 | 内置 `--max-tokens-budget` 预算上限 |

简单来说：`review` 看"改了什么"，`scan` 看"整个文件/仓库有什么问题"。

---

### Q3: 必须配置自己的 LLM 端点吗？支持哪些模型？

**A**: **是的，必须配置**。Open Code Review 本身不内置大模型，需要外部 LLM 端点驱动。

配置方式：
```bash
ocr config provider          # 选择内置供应商或添加自定义供应商
ocr config model             # 为当前供应商选择模型
```

支持的模型覆盖主流厂商，评测中测试过的模型包括：
- **Anthropic**：Claude-4.6-Opus、Claude-4.8-Opus
- **OpenAI**：GPT-5.5
- **阿里**：Qwen3.7-Max
- **DeepSeek**：Deepseek-V4-Pro
- **智谱**：GLM-5.1

对于纯本地化部署场景，可使用 Ollama 等本地推理框架提供兼容 OpenAI API 的端点。CI/CD 集成时通过 Secrets 注入 `OCR_LLM_URL`、`OCR_LLM_AUTH_TOKEN`、`OCR_LLM_MODEL`。

---

### Q4: 与 Claude Code 的 /code-review 相比有什么优势？

**A**: 基于 AACR-Bench 评测集的客观对比，Open Code Review 的核心优势在于：

1. **准确率显著领先**：OCR 25-38% vs CC 7-16%。以 Claude-4.6-Opus 为例，OCR 产出 889 条评论命中 301 个真实问题（33.90%），CC 产出 5980 条评论命中 435 个（7.23%）。更低的噪声意味着工程师处理效率更高。

2. **F1 综合指标更优**：OCR 最优 F1 25.10% vs CC 最优 F1 14.13%，在准确率和召回率间更均衡。

3. **资源开销大幅降低**：OCR Token 消耗 352K-743K / 1-6 分钟，CC 为 2,062K-5,664K / 5-14 分钟。OCR 仅为 CC 的 1/6 到 1/8。

4. **工程级稳定性**：确定性工程 × Agent 混合驱动，相比纯语言驱动的 Skills 方案，行为更可预测、结果更可复现。

**Claude Code 的优势**：召回率更高（28.90% vs 20.00%），适合安全审计等"宁可多查、不可遗漏"的场景。两者配合使用效果最佳。

---

### Q5: 如何自定义评审规则？四层规则如何生效？

**A**: Open Code Review 通过四层规则穿透机制解析评审规则，每层采用 first-match-wins 策略：

| 优先级 | 来源 | 路径 | 适用场景 |
|--------|------|------|---------|
| 1（最高） | CLI 参数 | `--rule <path>` | 临时专项评审，如安全审计、上线前 Checklist |
| 2 | 项目配置 | `<repoDir>/.opencodereview/rule.json` | 团队级规则，随 git 版本控制共享 |
| 3 | 全局配置 | `~/.opencodereview/rule.json` | 个人偏好规则，跨所有项目生效 |
| 4（最低） | 系统默认 | 内嵌 | 13 套语言/文件类型专属规则，开箱即用 |

**生效逻辑**：文件路径命中某个 glob pattern 后立即生效，不再向下穿透；若该层无匹配，则自动降级到下一层。

**规则文件格式示例**：
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

- `path` 支持 `**` 递归匹配和 `{java,kt}` 大括号展开
- 规则文件支持 `include` / `exclude` 字段精确控制评审范围
- 使用 `ocr rules check <file>` 命令预览任意文件路径将匹配到哪条规则

---

### Q6: 可以集成到现有的 CI/CD 流水线吗？

**A**: **可以，且开箱即用**。Open Code Review 天然适配 CI/CD 场景：

1. **结构化输出**：`--format json` 输出包含文件路径、行号、问题描述、修复建议的结构化结果
2. **静默模式**：`--audience agent` 静默所有进度输出，获得纯净的机器可读输出
3. **官方示例**：`examples/` 目录提供 GitHub Actions 和 GitLab CI 完整集成示例

**核心命令**：
```bash
ocr review --from "origin/$BASE_BRANCH" --to "origin/$HEAD_BRANCH" \
    --format json --audience agent
```

**配置方式**：只需通过 CI Secrets/Variables 注入三个环境变量：
- `OCR_LLM_URL`：LLM 端点地址
- `OCR_LLM_AUTH_TOKEN`：API Key
- `OCR_LLM_MODEL`：模型名称

**GitLab CI 特性**：在 Merge Request 创建时自动触发，评审结果通过 GitLab Discussions API 以行级讨论形式回写到 MR，支持自托管 GitLab 实例。

---

### Q7: 内部版的反思模型和定位模型是否开源？

**A**: **目前未开源**。Open Code Review 内部版依赖的两个专用模型尚未对外开源：

| 模型 | 用途 | 内部版性能 | 对外版本方案 |
|------|------|-----------|-------------|
| Qwen3-30B-A3B 反思模型 | 误报拦截过滤器 | 误报拦截率 30.09% → 52.63%，耗时 5s → 500ms | 依赖基模能力 |
| Qwen3-8B 定位模型 | 评论位置重定位 | 成功率 37.35% → 85.65%，耗时 3s → 1s | 三层递进式定位策略工程兜底 |

**对外版本的应对**：
- 位置准确性：工程层面的 Hunk-based 匹配 + 全文件扫描 + LLM 重定位三层策略，仍能保证 97%+ 的位置准确率
- 误报拦截：依赖精细化规则模板和上下文隔离设计降低误报

**未来计划**：官方正在逐步将内部版特性开源到社区，专用模型训练方法可参考反思模型论文（arxiv.org/pdf/2602.20166v1）。

---

### Q8: 评审结果的位置准确率如何？

**A**: **内部数据：评论位置准确率超过 97%**（基于 CR 被合并到目标分支的前提）。

Open Code Review 设计了三层递进式定位策略来保证位置准确性，从根本上回避了"让 LLM 数行号"的固有缺陷：

1. **第一层：Hunk-based 文本匹配**。模型通过 `code_comment` 工具提供 `existing_code`（评论的代码片段）而非行号，系统解析 diff hunks 通过归一化连续行匹配找到精确位置。
2. **第二层：全文件内容扫描**。如果 hunk 匹配失败，回退到对文件新版本内容逐行扫描。
3. **第三层：LLM 重定位**。如果前两层都失败（通常是模型复述代码时发生篡改），调用 LLM 重新从 diff 中提取精确的逐字代码片段，然后重试前两层。

**对比业界方案**：
- 复述代码定位：约 30% 偏差率（模型可能篡改原始代码）
- 行号定位：LLM 对数字不敏感，位置偏移常见
- AST 定位：准确性高但粒度太粗（如 20 行 if 语句只能定位到语句级别）

OCR 的 Hunk-based 方案在粒度和准确性之间取得了更好平衡。

---

### Q9: Token 消耗如何控制？大仓库扫描会不会很贵？

**A**: Open Code Review 在 Token 优化上设计了 7 项工程措施，大仓库扫描成本可控：

**核心优化措施**：
1. **分治策略**：变更拆分为独立子任务并发评审，Token 消耗线性可控（变更规模翻倍，Token 仅线性增长）
2. **双阈值内存压缩**：对话历史达 MaxTokens 60% 触发异步压缩，80% 触发同步压缩（三区模型：冻结区/压缩区/活跃区）
3. **大文件预过滤**：Diff 超过 MaxTokens 80% 的文件直接跳过
4. **工具输出设上限**：`file_read` 单次最多 500 行，`code_search` 最多 100 条匹配，`file_find` 最多 100 个结果
5. **Plan 阶段智能跳过**：变更不足 50 行的小文件跳过 Plan 阶段
6. **精确 Token 预算控制**：使用 tiktoken 预估，超限前主动拦截
7. **确定性逻辑接管**：文件筛选、规则匹配、行号定位等零 Token 消耗

**`ocr scan` 的成本控制**：
- 运行前打印粗略 Token 成本预估
- `--preview` / `-p` 预览文件清单不调用 LLM
- `--max-tokens-budget` 设置总 Token 上限，超出停止调度新批次
- `--no-plan` / `--no-dedup` / `--no-summary` 跳过可选阶段

**实测数据参考**：OCR 平均 Token 消耗 352K-743K，耗时 1-6 分钟，是同类工具中效率最高的（Claude Code 为 2,062K-5,664K）。对比 Anthropic Code Review 产品每次 PR 平均 15-25 美元的成本，OCR 的规模化部署经济性显著更优。

---

### Q10: 项目还在积极维护吗？

**A**: **是的，项目正在积极维护并持续开源更多特性**。

**维护活跃度证据**：
1. **官方 Roadmap 明确**：官方公布了未来规划，包括 Ultra 评审模式、IDE 插件、MCP 集成、专用模型训练、特定领域长期记忆等方向
2. **逐步开源策略**：官方明确表示"正在逐步将内部版的更多特性开源到社区中"
3. **社区共建邀请**：官方诚挚邀请开发者参与共建，无论是优化语言规则、Agent 策略、工具集，还是集成到更多平台
4. **反馈渠道畅通**：通过 [GitHub Issues](https://github.com/alibaba/open-code-review/issues) 接收使用体验问题和建议

**内部验证基础**：Open Code Review 的前身在阿里集团内部已服务 2 万月活用户、累计执行 370 万次真实评审任务、用户采纳率超过 30%、有效 AI 评论占比近 80%，经过大规模生产环境充分验证后才开源，项目具备持续迭代的工程基础和数据积累。

**参与方式**：
- 在 [GitHub Issues](https://github.com/alibaba/open-code-review/issues) 反馈问题或想法
- 贡献语言规则、Agent 策略优化、工具集改进
- 集成到更多平台（MCP、IDE 等）
