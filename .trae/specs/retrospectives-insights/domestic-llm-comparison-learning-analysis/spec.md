# 国产大模型对比文章学习分析 Spec

## Why

微信公众号文章《丸美小沐：国产AI模型对比与使用场景推荐》（URL: https://mp.weixin.qq.com/s/WM3bIS42FPoiQgDw_SVrTA）系统对比了 GLM 5.2、Kimi K2.7 Code、DeepSeek V4、MiniMax M3 四款国产大模型在不同使用场景下的表现与推荐策略。文章基于作者真实使用体感，提供了按人群/任务分类的模型选择建议、价格对比和信任问题洞察，对项目成员选择 AI 工具、配置智能体后端模型具有直接参考价值。需要将文章内容系统学习并整理成结构化学习笔记，纳入项目知识库 `docs/knowledge/learning/`，便于后续查阅与引用。

## What Changes

- 新增学习笔记文档 `docs/knowledge/learning/domestic-llm-comparison-notes.md`，系统整理文章核心内容
- 在 `docs/knowledge/README.md` 学习类索引中登记新笔记
- 笔记内容包含：文章元信息、核心观点、按人群/任务分类的模型推荐矩阵、四款模型详细评价、价格与成本数据、专业术语表、信任问题洞察、信息价值评估、与项目实践的关联建议

## Impact

- Affected specs: 无（纯学习笔记新增，不修改现有规范）
- Affected code: 无（不涉及代码改动）
- Affected docs:
  - 新增 `docs/knowledge/learning/domestic-llm-comparison-notes.md`
  - 更新 `docs/knowledge/README.md`（在 learning 类目下追加索引条目）

## ADDED Requirements

### Requirement: 学习笔记文档结构

学习笔记文档 SHALL 包含以下章节，顺序为：
1. 文章元信息（标题、作者、来源URL、阅读日期）
2. 核心观点摘要（3-5条要点）
3. 文章结构框架（章节目录）
4. 按人群分类的模型推荐矩阵
5. 四款模型详细评价（DeepSeek / Kimi K2.7 Code / MiniMax M3 / GLM 5.2）
6. 价格与成本对比数据
7. 专业术语表
8. 信任问题洞察（"能力是入场券，信任才是留下来的理由"）
9. 信息价值评估（实用性/时效性/主观性/局限性）
10. 与项目实践的关联建议
11. 参考资料链接

#### Scenario: 笔记内容完整覆盖文章要点

- **WHEN** 读者阅读学习笔记
- **THEN** 能够在不打开原文的情况下，掌握文章的核心观点、模型推荐逻辑、价格数据和信任洞察

#### Scenario: 推荐矩阵清晰可查

- **WHEN** 读者需要选择国产大模型
- **THEN** 能够通过推荐矩阵快速定位适合自己的模型（按是否写代码、是否处理多模态资料、是否高并发批量任务分类）

### Requirement: 模型评价信息准确性

学习笔记中的四款模型评价 SHALL 忠实反映文章原文观点，包括：
- DeepSeek：开源、便宜、脑子活；适合批量任务；长任务信心不足
- Kimi K2.7 Code：相对稳定；编程替补；社区风评褒贬不一；曾用于 OpenClaw 小瑶机器人
- MiniMax M3：被低估的多面手；原生多模态强；1M 长上下文；永久半价；曾因速度慢被诟病，现已改善
- GLM 5.2：编程能力最强；长上下文扎实；幻觉率不低；无多模态；Coding plan 难买（每天早十点抢购）

#### Scenario: 评价信息不歪曲原文

- **WHEN** 对比笔记评价与原文评价
- **THEN** 核心结论一致，不引入笔记作者的主观改写或夸大

### Requirement: 价格数据可追溯

学习笔记中的价格数据 SHALL 与原文一致，包括：
- 价格从低到高排序：DeepSeek → MiniMax M3 → Kimi K2.7 → GLM 5.2
- Coding plan 中档套餐约 400+ 元/月（用于三五个小项目日常维护）
- DeepSeek API：处理 500 份长文档约 1 元
- MiniMax M3 API：处理约 200 份大文件约 1 元

#### Scenario: 价格数据可核对

- **WHEN** 读者核对笔记价格数据与原文
- **THEN** 数值与排序均一致，无误差

### Requirement: 知识库索引登记

`docs/knowledge/README.md` 的 learning 类目下 SHALL 新增条目登记本笔记，格式与现有学习类条目保持一致（包含标题、相对路径链接、一句话简介）。

#### Scenario: 索引可访问

- **WHEN** 读者浏览 `docs/knowledge/README.md`
- **THEN** 能够看到并点击进入国产大模型对比学习笔记

### Requirement: 文件命名与路径合规

学习笔记文件 SHALL 命名为 `domestic-llm-comparison-notes.md`，放置于 `docs/knowledge/learning/` 目录下，文件名使用 kebab-case 纯英文，符合项目命名规范（通过 `python .agents/scripts/check-filename-convention.py` 验证）。

#### Scenario: 命名规范验证通过

- **WHEN** 运行文件命名规范检查脚本
- **THEN** 新增文件名通过检查，无警告或错误
