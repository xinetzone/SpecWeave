# 火山引擎 AgentKit Wiki 教程 - Verification Checklist

## G1 质量门：事实阶段（R阶段）验证
- [ ] Checkpoint G1.1: facts.md 存在于 spec 目录，包含 ≥35 条编号事实
- [ ] Checkpoint G1.2: 事实条目不包含"因为/所以/导致/由于/因此/使得"等因果推断词（正则检查）
- [ ] Checkpoint G1.3: 事实均匀覆盖 6 大类别（产品定位/功能模块/VeADK/SDKCLI/场景/生态），每类 ≥5 条
- [ ] Checkpoint G1.4: 每条事实标注来源编号（S1-S5），可溯源至 5 个官方来源

## G2 质量门：洞察阶段（I阶段）验证
- [ ] Checkpoint G2.1: insights.md 存在于 spec 目录，包含 ≥5 条核心洞察
- [ ] Checkpoint G2.2: 每条洞察四元组完整：现象陈述 + 证据引用（Fxx编号）+ 反常识发现 + 落地建议
- [ ] Checkpoint G2.3: 洞察有层次感：≥1 条战略层 + ≥2 条架构层 + ≥2 条实践层
- [ ] Checkpoint G2.4: 反常识发现确实挑战常见认知（不是"常识复述"），至少 1 条有观点冲击力
- [ ] Checkpoint G2.5: 所有证据引用编号均在 facts.md 中存在对应条目，无悬垂引用

## G3 质量门：萃取阶段（E阶段）验证
- [ ] Checkpoint G3.1: patterns.md 存在于 spec 目录，包含 ≥3 个结构化模式
- [ ] Checkpoint G3.2: 模式 1（选型框架）：≥8 个评估维度，每维度有权重和 1-5 分量化标准
- [ ] Checkpoint G3.3: 模式 2（改造 SOP）：5 步流程，每步有输入/输出/工具，≥3 个反模式
- [ ] Checkpoint G3.4: 模式 3（Demo→生产清单）：≥12 项检查，覆盖 6 大维度，每项有 pass/fail 标准
- [ ] Checkpoint G3.5: 每个模式可迁移（G3标准）：模式 1 可用于评估 Dify/LangGraph 等，模式 2 可用于任何 API 改造
- [ ] Checkpoint G3.6: 每个模式明确标注 ≥2 条反模式（"不要做什么"）

## V 门：对抗审查阶段（V阶段）验证
- [ ] Checkpoint V.1: adversarial-review.md 存在，四视角齐全（魔鬼代言人/新手/CTO/未来用户）
- [ ] Checkpoint V.2: 每视角 ≥4 条具体攻击，总计 ≥16 条攻击意见
- [ ] Checkpoint V.3: 攻击意见具体可操作，不是客套话（每条有质疑点+修正建议）
- [ ] Checkpoint V.4: 采纳率 ≥30%（≥5 条标注"已采纳"）
- [ ] Checkpoint V.5: 至少修正 1 个 facts 事实性问题 + 1 个 insights 逻辑漏洞 + 1 个 patterns 可迁移性问题
- [ ] Checkpoint V.6: 修正记录可追踪（每条采纳意见写明：修正了哪个文件哪个部分）

## AC-1 目录结构完整
- [ ] Checkpoint AC1.1: 目标目录包含 README.md + 00-overview.md ~ 10-resources-glossary.md 共 12 个文件
- [ ] Checkpoint AC1.2: 12 个文件每个 < 300 行（NFR-1）
- [ ] Checkpoint AC1.3: 目录位置正确：`.agents/docs/knowledge/learning/03-agent-platforms-tools/volcengine-agentkit-wiki/`

## AC-2 ~ AC-11 内容完整度
- [ ] Checkpoint AC2: 01-product-intro.md 包含：产品定义 + 4大痛点 + 8大功能模块详解 + 4大优势（每优势2-3证据）+ Mermaid 发展时间线
- [ ] Checkpoint AC3: 02-core-architecture.md 包含：≥6层 Mermaid 分层架构图 + Harness 3特性 + Serverless 3能力 + 安全3层模型（每层≥2能力）+ 评测闭环 Mermaid 图
- [ ] Checkpoint AC4: 03-veadk-framework.md 包含：三语言安装命令（每语言≥2方式）+ ≥20行产品融合矩阵表（8大类）+ DeepResearch 6特性 + 3×GitHub 链接 + 3×镜像地址
- [ ] Checkpoint AC5: 04-agentkit-sdk-cli.md 包含：≥20行装饰器完整代码示例 + CLI 5命令清单（功能/参数/示例）+ 3模式×5维度对比表 + 3项Platform服务接入说明
- [ ] Checkpoint AC6: 05-quickstart.md 包含：4项前置条件 + 5步上手流程（每步：命令+预期输出+注意事项）+ ≥5条FAQ（错误信息/原因/方案）
- [ ] Checkpoint AC7: 06-application-scenarios.md 包含：4场景（描述+Mermaid架构+能力映射+5步实施）+ 3行业落地框架 + 标准化vs定制化Mermaid决策树
- [ ] Checkpoint AC8: 07-core-features-detailed.md 包含：5大模块详解（Identity/Gateway/A2A/Session-Memory/Knowledge），每模块≥3子模块+集成代码片段，明确交叉引用MCP和A2A协议wiki
- [ ] Checkpoint AC9: 08-comparison-ecosystem.md 包含：6平台×10维度对比表（每格有内容）+ 8维度选型框架（量化标准）+ 火山AI产品矩阵Mermaid图 + 自研vs采购决策树
- [ ] Checkpoint AC10: 09-faq-best-practices.md 包含：≥15条FAQ（6大分类齐全，每条问题+原因+方案）+ 8条最佳实践（每条可操作）+ ≥5条常见陷阱（触发+规避）
- [ ] Checkpoint AC11: 10-resources-glossary.md 包含：≥20条术语（英/中/定义）+ 官方资源≥10项链接 + 知识库交叉引用≥10个（每项：关联wiki/推荐章节/学习价值）+ 版本兼容矩阵≥3行

## AC-12 ~ AC-15 规范性与一致性
- [ ] Checkpoint AC12.1: 12 个文件 YAML frontmatter 字段齐全：id/title/source/category/tags/date/status/author/summary
- [ ] Checkpoint AC12.2: source 字段值统一为 `seven-concepts: volcengine-agentkit-wiki`，category 统一为 `learning`
- [ ] Checkpoint AC13: 运行链接检查无错误：内部相对路径全部有效，无 `file:///` 绝对路径，无断链
- [ ] Checkpoint AC14: 分章文档（01~10）底部双向导航齐全：上一章 / 返回目录 / 下一章
- [ ] Checkpoint AC15: 交叉引用充分：全教程共引用 ≥6 个已有 wiki（至少包含 MCP协议/A2A协议/七大组件/对抗审查/接口deep-dive/Skill开发）

## 产出物完整性（spec 目录中间产物 + 最终产出）
- [ ] Checkpoint Final.1: spec 目录包含 5 份中间产物：facts.md / insights.md / patterns.md / adversarial-review.md / verification-report.md
- [ ] Checkpoint Final.2: verification-report.md 包含 AC-1 ~ AC-15 逐项验证结果（✓/✗ + 备注），全部通过
- [ ] Checkpoint Final.3: facts/insights/patterns 三份均通过 G1~G3 质量门，有明确通过记录
- [ ] Checkpoint Final.4: 教程内容不包含产品定价、商务条款、SLA等时效性商业信息（符合Non-Goals）
- [ ] Checkpoint Final.5: 教程标注内容快照时间（2026年7月），提示读者后续以官方文档为准（符合 Assumptions）
