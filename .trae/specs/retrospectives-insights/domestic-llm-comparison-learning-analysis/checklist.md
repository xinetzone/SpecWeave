# Checklist

## 文档存在与命名

- [x] 学习笔记文件 `docs/knowledge/learning/domestic-llm-comparison-notes.md` 已创建
- [x] 文件名 `domestic-llm-comparison-notes.md` 通过 `python .agents/scripts/check-filename-convention.py` 验证（kebab-case 纯英文）

## 内容完整性（11 个章节）

- [x] 章节一：文章元信息（标题、作者"丸美小沐"、来源URL、阅读日期 2026-07-04）
- [x] 章节二：核心观点摘要（3-5 条要点，含"能力是入场券，信任才是留下来的理由"）
- [x] 章节三：文章结构框架（章节目录）
- [x] 章节四：按人群分类的模型推荐矩阵（表格形式）
- [x] 章节五：四款模型详细评价（DeepSeek / Kimi K2.7 Code / MiniMax M3 / GLM 5.2）
- [x] 章节六：价格与成本对比数据（表格形式）
- [x] 章节七：专业术语表（Token plan、Coding plan、多模态、长上下文、幻觉率、高并发、API 等）
- [x] 章节八：信任问题洞察
- [x] 章节九：信息价值评估（实用性/时效性/主观性/局限性）
- [x] 章节十：与项目实践的关联建议
- [x] 章节十一：参考资料链接

## 推荐矩阵准确性

- [x] 不写代码-文案类 → DeepSeek V4 Pro（免费网页版）
- [x] 不写代码-多模态资料 → MiniMax M3（token plan + 桌面端 minimax Agent，或 Trae/Workbuddy）
- [x] 写代码 → GLM 5.2 主力 / Kimi K2.7 Code 替补
- [x] 高并发批量任务 → DeepSeek V4 Flash + MiniMax M3 API（不能用 token plan，并发不够）

## 模型评价准确性（忠实原文）

- [x] DeepSeek：开源、便宜、脑子活；适合批量任务；长任务信心不足；便宜耐用最让人放心
- [x] Kimi K2.7 Code：相对稳定；编程替补；曾接 OpenClaw 小瑶机器人 2.6 版本；社区风评褒贬不一（小号 Gemini）
- [x] MiniMax M3：被低估的多面手；原生多模态强；1M 长上下文；永久半价；速度曾慢现已改善；适合复杂前端任务
- [x] GLM 5.2：编程能力最强；长上下文扎实；幻觉率不低；无多模态；Coding plan 难买（每天早十点抢购）；适合平替主 Agent 主模型；API 价格不适合批量任务

## 价格数据准确性

- [x] 价格从低到高排序：DeepSeek → MiniMax M3 → Kimi K2.7 → GLM 5.2
- [x] Coding plan 中档套餐约 400+ 元/月（用于三五个小项目日常维护）
- [x] DeepSeek API：处理 500 份长文档约 1 元
- [x] MiniMax M3 API：处理约 200 份大文件约 1 元（根据用量波动）

## 信任问题洞察完整性

- [x] 包含核心金句"能力是入场券，信任才是留下来的理由"
- [x] 包含 Claude/OpenAI 自动找补 vs 国产模型下意识归类不靠谱的心理对比
- [x] 包含"信任余额"概念（隐形信任积累）
- [x] 包含测试场景偏见问题（直接塞进复杂长任务，出错就归类不靠谱）
- [x] 包含作者结论：能力差距在补，信任需要更多时间与场景

## 索引登记

- [x] `docs/knowledge/README.md` 的 learning 类目下已新增本笔记条目
- [x] 索引条目格式与现有学习类条目一致（标题、相对路径链接、一句话简介）
- [x] 索引中的相对路径链接有效（点击可跳转到笔记文件）

## 链接有效性

- [x] 原文链接 https://mp.weixin.qq.com/s/WM3bIS42FPoiQgDw_SVrTA 已添加
- [x] 所有内部相对路径链接有效（无断链）
- [x] 引用的项目内文档路径正确（遵循 ../../../ 项目根、.agents/ 前缀、../ 同目录规则）

## 内容质量

- [x] 笔记忠实反映原文观点，无主观歪曲或夸大
- [x] 推荐矩阵表格清晰，可快速查询
- [x] 价格数据表格清晰，可核对
- [x] 专业术语释义准确，结合文章语境
- [x] 信息价值评估客观，涵盖实用性/时效性/主观性/局限性四个维度
- [x] 与项目实践的关联建议具体可执行（不空泛）
