# Spec：豆包工作连上飞书 → OKF 知识包

## 基本信息

- **博文URL**：https://mp.weixin.qq.com/s/dqvRKQoH45cXL2F8z0ZHYw
- **博文标题**：《实测豆包工作：连上飞书后，Agent终于像个同事了》
- **作者/账号**：APPSO（爱范儿旗下）
- **发布日期**：2026-08-25 11:29
- **内容敏感度**：公开（微信公开文章，无访问控制参数）→ 标准工作流
- **内容性质**：产品实测评测（hands-on体验），含战略分析
- **骨架选择**：商业分析/战略资讯骨架（index + concepts + references + log，**无examples**）
- **归属**：`ai/ai-agent/`
- **Bundle路径**：`projects/awesome-okf-xs/doc/bundles/ai/ai-agent/doubao-work/`
- **Bundle名**：doubao-work

## 骨架（10文件，无examples）

| # | 文件 | 内容 |
|---|------|------|
| 1 | index.md | 根索引：frontmatter + 性质声明 + 信源 + 结构总览 + 导航 + 信任声明 + toctree |
| 2 | concepts/index.md | 概念目录索引：4篇学习路径 + toctree |
| 3 | concepts/00-product-overview.md | 产品发布、定位、核心能力（文档/PPT/网页/AI编辑）、额度模型 |
| 4 | concepts/01-multimodal-and-computer.md | 多模态生成（Seedance/Seedream/GitHub Skill）、电脑操作、远程控制 |
| 5 | concepts/02-feishu-integration.md | 飞书深度集成（组织/文档/消息/任务/多维表格/会议纪要/权限/由豆包发送） |
| 6 | concepts/03-work-context-thesis.md | 战略分析（工作现场/Sam Altman引语/模型vs组织上下文/金句） |
| 7 | references/index.md | 信源清单 + F编号索引 + 可信度说明 + toctree |
| 8 | references/article-source.md | F-001~F-042完整事实登记 |
| 9 | references/verification.md | 8项P0核验报告（全部通过）+ 权威来源URL汇总 |
| 10 | log.md | R→I→E→V链路 + 文件清单 + G1-G4质量门 |

## 事实编号

F-001~F-042（42条），P0核验8项全部通过，无勘误。

## 索引更新计划

- `ai/ai-agent/index.md`：total_bundles 24→25，📰产品资讯板块追加doubao-work行，toctree追加
- `bundles/index.md`：total_bundles 273→274，ai域100→101束，ai-agent行23→24

## 验收标准

- UTF-8严格解码（10文件）
- toctree三级完整
- 相对链接可达，无file:///绝对路径
- external/无变更
- stale_after: 2026-12-31（产品快速迭代中）
- 区分客观事实与作者观点（📝标注）
