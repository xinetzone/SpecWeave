# Tasks

- [x] Task 1: 准备学习笔记文档骨架
  - [x] SubTask 1.1: 在 `docs/knowledge/learning/` 目录下创建 `domestic-llm-comparison-notes.md`
  - [x] SubTask 1.2: 写入文档元信息（标题、作者"丸美小沐"、来源URL、阅读日期 2026-07-04）
  - [x] SubTask 1.3: 按 spec.md 中要求的 11 个章节顺序建立文档骨架（章节标题与占位）

- [x] Task 2: 整理文章核心观点与结构框架
  - [x] SubTask 2.1: 撰写"核心观点摘要"章节，提炼 3-5 条要点（含"能力是入场券，信任才是留下来的理由"）
  - [x] SubTask 2.2: 撰写"文章结构框架"章节，列出原文的章节目录（开篇背景→按人群分类推荐→价格对比→各模型详细评价→心里话）

- [x] Task 3: 编写按人群分类的模型推荐矩阵
  - [x] SubTask 3.1: 整理"不写代码-文案类"推荐：DeepSeek V4 Pro（免费网页版）
  - [x] SubTask 3.2: 整理"不写代码-多模态资料"推荐：MiniMax M3（token plan + 桌面端 minimax Agent，或 Trae/Workbuddy）
  - [x] SubTask 3.3: 整理"写代码"推荐：GLM 5.2 主力 / Kimi K2.7 Code 替补
  - [x] SubTask 3.4: 整理"高并发批量任务"推荐：DeepSeek V4 Flash + MiniMax M3 API（不能用 token plan，并发不够）
  - [x] SubTask 3.5: 以表格形式呈现推荐矩阵，便于快速查询

- [x] Task 4: 编写四款模型详细评价
  - [x] SubTask 4.1: DeepSeek 评价（开源、便宜、脑子活；批量任务；长任务信心不足；便宜耐用最让人放心）
  - [x] SubTask 4.2: Kimi K2.7 Code 评价（相对稳定；编程替补；曾接 OpenClaw 小瑶机器人 2.6 版本；社区风评褒贬不一，有人称小号 Gemini）
  - [x] SubTask 4.3: MiniMax M3 评价（被低估的多面手；原生多模态强；1M 长上下文；永久半价；曾因速度慢被诟病，现已改善；适合复杂前端任务）
  - [x] SubTask 4.4: GLM 5.2 评价（编程能力最强；长上下文扎实；幻觉率不低；无多模态；Coding plan 难买，每天早十点抢购；适合平替主 Agent 主模型；API 价格不适合批量任务）

- [x] Task 5: 整理价格与成本对比数据
  - [x] SubTask 5.1: 列出价格从低到高排序：DeepSeek → MiniMax M3 → Kimi K2.7 → GLM 5.2
  - [x] SubTask 5.2: 记录 Coding plan 中档套餐约 400+ 元/月（用于三五个小项目日常维护，完全够用）
  - [x] SubTask 5.3: 记录 DeepSeek API 成本：处理 500 份长文档约 1 元
  - [x] SubTask 5.4: 记录 MiniMax M3 API 成本：处理约 200 份大文件约 1 元（根据用量波动）
  - [x] SubTask 5.5: 以表格形式呈现价格对比

- [x] Task 6: 整理专业术语表
  - [x] SubTask 6.1: 整理术语：Token plan（令牌套餐）、Coding plan（编程套餐）、多模态、长上下文、幻觉率、高并发、API 等
  - [x] SubTask 6.2: 每个术语提供简要中文释义，结合文章语境

- [x] Task 7: 编写信任问题洞察章节
  - [x] SubTask 7.1: 记录核心金句"能力是入场券，信任才是留下来的理由"
  - [x] SubTask 7.2: 整理作者对 Claude/OpenAI 自动找补 vs 对国产模型下意识归类为不靠谱的心理对比
  - [x] SubTask 7.3: 整理"信任余额"概念（隐形信任积累）
  - [x] SubTask 7.4: 整理测试场景偏见问题（直接塞进 Claude/OpenAI 已推进的复杂长任务中，一旦出错就归类不靠谱）
  - [x] SubTask 7.5: 整理作者结论：能力差距在补，但信任需要更多时间与场景

- [x] Task 8: 编写信息价值评估章节
  - [x] SubTask 8.1: 实用性评估（高：提供具体使用场景推荐和价格对比，可直接指导模型选择）
  - [x] SubTask 8.2: 时效性评估（强：针对最新发布的 GLM 5.2 和 Kimi 2.7，但模型迭代快，时效性会衰减）
  - [x] SubTask 8.3: 主观性评估（中：基于个人使用体感，非严格基准测试，但具有参考价值）
  - [x] SubTask 8.4: 局限性评估（缺乏严格基准测试数据；样本量为单人经验；未覆盖更多国产模型如通义千问、文心一言等）

- [x] Task 9: 编写与项目实践的关联建议
  - [x] SubTask 9.1: 结合项目 AGENTS.md 智能体配置，建议 GLM 5.2 作为主 Agent 编程模型（如可购买）
  - [x] SubTask 9.2: 建议 Kimi K2.7 Code 作为编程替补（稳定性优势）
  - [x] SubTask 9.3: 建议批量内容处理（如脚本批量执行、文档批量转换）使用 DeepSeek API
  - [x] SubTask 9.4: 建议多模态资料处理（截图、PDF、扫描件）使用 MiniMax M3
  - [x] SubTask 9.5: 提醒模型选择应考虑信任建立过程，避免一次出错就完全弃用

- [x] Task 10: 添加参考资料链接
  - [x] SubTask 10.1: 添加原文链接 https://mp.weixin.qq.com/s/WM3bIS42FPoiQgDw_SVrTA
  - [x] SubTask 10.2: 添加四款模型官方/介绍链接（如有）
  - [x] SubTask 10.3: 添加项目内相关文档链接（如 docs/knowledge/ 下其他 AI 模型相关笔记）

- [x] Task 11: 更新知识库索引
  - [x] SubTask 11.1: 在 `docs/knowledge/README.md` 的 learning 类目下追加国产大模型对比学习笔记条目
  - [x] SubTask 11.2: 索引条目格式与现有学习类条目保持一致（标题、相对路径链接、一句话简介）

- [x] Task 12: 验证与归档
  - [x] SubTask 12.1: 运行 `python .agents/scripts/check-filename-convention.py` 验证文件命名合规
  - [x] SubTask 12.2: 检查所有 Markdown 链接有效性（相对路径正确）
  - [x] SubTask 12.3: 通读笔记内容，确认忠实反映原文观点，无主观歪曲

# Task Dependencies

- Task 1 须先完成（建立文档骨架），Task 2-10 可在此基础上并行/顺序编写
- Task 11 依赖 Task 1-10 完成（笔记内容定稿后再登记索引）
- Task 12 依赖 Task 11 完成（最终验证）
