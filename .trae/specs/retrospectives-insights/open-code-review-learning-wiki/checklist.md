# Open Code Review 项目学习与 Wiki 教程文档 - 验证清单

## 格式规范
- [x] Checkpoint 1: 索引页文件已创建在正确路径（docs/knowledge/learning/open-code-review-wiki.md）
- [x] Checkpoint 2: 原子文件目录已创建（docs/knowledge/learning/open-code-review-wiki/）
- [x] Checkpoint 3: 所有原子文件使用 YAML frontmatter（---分隔），不是 TOML（+++分隔）
- [x] Checkpoint 4: 每个原子文件 frontmatter 包含 id/title/source/x-toml-ref 四个字段
- [x] Checkpoint 5: x-toml-ref 路径指向 .meta/toml/docs/knowledge/learning/open-code-review-wiki/ 镜像路径，层级计算正确
- [x] Checkpoint 6: 文件名使用 kebab-case 规范，纯英文无中文，两位数字前缀（00-10）
- [x] Checkpoint 7: 所有内部链接使用相对路径，无死链

## 内容质量
- [x] Checkpoint 8: 核心观点完整保留，无重大遗漏
- [x] Checkpoint 9: 关键概念解释清晰（确定性工程×Agent混合驱动、四层规则穿透、三层递进式定位等）
- [x] Checkpoint 10: 章节逻辑连贯，无跳脱
- [x] Checkpoint 11: 代码/命令示例可验证（npm install、ocr review、ocr scan 等命令完整）
- [x] Checkpoint 12: 有明确的学习路径

## 结构完整性
- [x] Checkpoint 13: 索引页包含完整的目录导航表，链接到所有11个章节
- [x] Checkpoint 14: 00-overview.md 包含背景介绍、核心主题、学习目标、前置知识、文档导航
- [x] Checkpoint 15: 01-core-concepts.md 清晰阐述通用 Agent 方案的3个问题（覆盖不全/位置漂移/效果不稳定）
- [x] Checkpoint 16: 01-core-concepts.md 准确解析"确定性工程×Agent混合驱动"理念，包含4大强约束环节和2大动态决策环节
- [x] Checkpoint 17: 02-installation.md 包含 npm 安装、ocr version 验证、LLM 配置（provider/model）完整步骤
- [x] Checkpoint 18: 03-usage.md 详细说明 ocr review 的4种使用方式（工作区/分支对比/单次提交/附带背景）
- [x] Checkpoint 19: 03-usage.md 详细说明 ocr scan 的适用场景、4阶段流程（Plan/Batching/Dedup/Summary）和成本控制
- [x] Checkpoint 20: 03-usage.md 包含 ocr review 和 ocr scan 的常用参数表
- [x] Checkpoint 21: 04-optimizations.md 完整说明假阴性4个优化策略（文件打包/Plan阶段/Agent动态召回/场景化工具集）
- [x] Checkpoint 22: 04-optimizations.md 完整说明假阳性3个优化策略（反思模型/规则模板/上下文隔离），含反思模型数据（30.09%→52.63%）
- [x] Checkpoint 23: 04-optimizations.md 清晰说明四层规则穿透机制（CLI参数/项目维度/用户维度/系统默认）
- [x] Checkpoint 24: 04-optimizations.md 完整说明三层递进式定位策略（Hunk-based/全文件扫描/LLM重定位）
- [x] Checkpoint 25: 04-optimizations.md 完整说明 Token 7个优化策略（分治/双阈值压缩/大文件预过滤/工具输出上限/Plan跳过/精确预算/确定性逻辑接管）
- [x] Checkpoint 26: 05-integrations.md 清晰对比 Claude Code 的 Command 与 Skills 两种集成方式
- [x] Checkpoint 27: 05-integrations.md 完整说明 Claude Code 集成的4大工作机制（上下文隔离/需求感知/置信度分级/自动修复）
- [x] Checkpoint 28: 05-integrations.md 完整说明 GitHub Actions 和 GitLab CI 集成方式，含环境变量（OCR_LLM_URL/OCR_LLM_AUTH_TOKEN/OCR_LLM_MODEL）
- [x] Checkpoint 29: 05-integrations.md 说明自定义评审规则四层链路解析和规则配置文件格式
- [x] Checkpoint 30: 05-integrations.md 说明 OpenTelemetry 可观测性配置和 Web 视图
- [x] Checkpoint 31: 06-effectiveness.md 完整列出内部数据5项指标（2万月活/370万任务/30%采纳率/近80% AI评论占比/97%+位置准确率）
- [x] Checkpoint 32: 06-effectiveness.md 清晰说明3个评测结论（准确率vs召回率/资源开销差异/新一代模型非全面优于上一代），含具体数据
- [x] Checkpoint 33: 06-effectiveness.md 完整说明实践案例（Claude Code 用 Go 重写开源版本，106次变更发现145个有效问题）
- [x] Checkpoint 34: 06-effectiveness.md 完整说明 AACR-Bench 3大核心优势（人机结合/多维度评估/深刻行业洞察）
- [x] Checkpoint 35: 07-limitations.md 列出至少6项局限性，表述客观中立
- [x] Checkpoint 36: 07-limitations.md 包含与 Claude Code/Codex 的对比表（准确率/召回率/F1/资源开销/适用场景）
- [x] Checkpoint 37: 08-summary.md 包含6条核心要点回顾
- [x] Checkpoint 38: 08-summary.md 说明未来规划（Ultra模式/IDE插件/MCP集成/专用模型/长期记忆）
- [x] Checkpoint 39: 09-faq.md 包含至少9个常见问题及解答
- [x] Checkpoint 40: 10-resources.md 包含 GitHub 项目地址、原文链接、论文链接、数据集链接

## 子代理产出验收5点检查（强制！）
- [x] Checkpoint 41: ✅ **frontmatter 分隔符正确**：使用 `---`（YAML），不是 `+++`（TOML）
- [x] Checkpoint 42: ✅ **x-toml-ref 存在且路径正确**：指向 .meta/toml/ 镜像路径，相对层级计算正确
- [x] Checkpoint 43: ✅ **标题层级从 h1 开始**：文件第一行是 `# 标题`，无跳级
- [x] Checkpoint 44: ✅ **文件名合规**：kebab-case、纯英文、两位数字前缀（00-10）
- [x] Checkpoint 45: ✅ **source 溯源字段存在**：派生产物标注原始来源 URL 或父文件

## 元数据与索引
- [x] Checkpoint 46: tags 分类准确（open-code-review、ai-code-review、alibaba、cli、agent、aacr-bench、code-quality、devops）
- [x] Checkpoint 47: date 字段正确（2026-07-04）
- [x] Checkpoint 48: .meta/toml/docs/knowledge/learning/open-code-review-wiki/ 目录下有对应 TOML 文件
- [x] Checkpoint 49: docs/knowledge/README.md 已更新，learning 分类新增 Open Code Review 教程条目
- [x] Checkpoint 50: 知识库索引条目格式与现有条目一致，包含标题/摘要/日期/标签

## 工具验证
- [x] Checkpoint 51: 运行 `python .agents/scripts/fix-x-toml-ref.py --dir docs/knowledge/learning/open-code-review-wiki/ --write --create-toml` 成功
- [x] Checkpoint 52: 运行 `python .agents/scripts/check-filename-convention.py` 无违规文件
- [x] Checkpoint 53: 运行 `python .agents/scripts/check-links.py` 无断链
