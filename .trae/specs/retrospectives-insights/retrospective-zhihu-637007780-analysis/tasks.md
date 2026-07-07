# Tasks

- [x] Task 1: S1 事实收集
  - [x] SubTask 1.1: 读取 `analyze-zhihu-question-637007780/` 下的全部 5 个文件（spec.md, tasks.md, checklist.md, learning-notes.md, raw-content.md）
  - [x] SubTask 1.2: 梳理任务执行时间线（spec 创建 → 内容获取尝试 → 分析执行 → 报告生成）
  - [x] SubTask 1.3: 记录 6 种内容获取策略的尝试结果（策略名称、结果、错误码、原因）
  - [x] SubTask 1.4: 记录产出物清单（文件名、大小、用途）
  - [x] SubTask 1.5: 记录样本覆盖率数据（3/23 回答，13%，赞同数分布）

- [x] Task 2: S2 过程分析
  - [x] SubTask 2.1: 识别成功因素（agent-browser + 反自动化 flag + 桌面 UA 组合成功的原因）
  - [x] SubTask 2.2: 识别失败原因（5 种失败策略各自的失败原因分析）
  - [x] SubTask 2.3: 识别瓶颈（登录态限制、反爬技术对抗、沙箱网络限制）
  - [x] SubTask 2.4: 评估三层分析框架在样本受限时的表现（哪些维度有效、哪些维度失效）
  - [x] SubTask 2.5: 识别"分析精度 vs 原始内容信度"矛盾的具体表现
  - [x] SubTask 2.6: 识别执行过程中的其他问题（如子智能体委派策略、spec 规划耗时等）

- [x] Task 3: S3 洞察提炼
  - [x] SubTask 3.1: 萃取"反爬策略决策树"模式（针对知乎类反爬站点的获取策略优先级与 fallback 链）
  - [x] SubTask 3.2: 萃取"小样本分析方法论"（样本量 < 5 时的分析策略调整：降级、标注、补充获取）
  - [x] SubTask 3.3: 萃取"三层分析框架适用性边界"（系统性学习/深度洞察/知识萃取三层的适用条件与降级规则）
  - [x] SubTask 3.4: 萃取"子智能体委派策略"洞察（何时委派、如何传递上下文、如何验证产出）
  - [x] SubTask 3.5: 提出具体改进建议（每个建议含优先级高/中/低 + 验收标准）

- [x] Task 4: S4 报告生成
  - [x] SubTask 4.1: 读取复盘报告模板 `docs/retrospective/templates/retrospective-report-template.md`（如存在）
  - [x] SubTask 4.2: 撰写复盘报告，包含「事实→分析→洞察→建议」四部分
  - [x] SubTask 4.3: 添加执行摘要与关键发现
  - [x] SubTask 4.4: 列出改进行动项（优先级 + 验收标准）
  - [x] SubTask 4.5: 添加 frontmatter（含 source 字段）

- [x] Task 5: S5 归档沉淀
  - [x] SubTask 5.1: 确定报告归档目录（`docs/retrospective/reports/` 下的分类子目录）
  - [x] SubTask 5.2: 评估可复用模式成熟度（L1-L4），决定是否入库
  - [x] SubTask 5.3: 如达到入库标准，创建模式文件至 `docs/retrospective/patterns/`
  - [x] SubTask 5.4: 更新相关索引（docs/retrospective/README.md 或 patterns/README.md）

- [x] Task 6: 导出正式报告
  - [x] SubTask 6.1: 调用 export-report-cmd 验证报告格式
  - [x] SubTask 6.2: 确保 frontmatter 完整
  - [x] SubTask 6.3: 确认报告已保存到正确目录

# Task Dependencies

- Task 1 → Task 2（事实收集是过程分析的基础）
- Task 2 → Task 3（过程分析是洞察提炼的基础）
- Task 3 → Task 4（洞察提炼是报告生成的核心内容）
- Task 4 → Task 5（报告生成后才能归档沉淀）
- Task 5 → Task 6（归档后导出正式报告）
