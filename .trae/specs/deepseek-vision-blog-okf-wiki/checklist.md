# Checklist

## 归属与结构
- [x] bundle 位于 `ai/deepseek/vision-model-selection/`，归属分析已在 spec.md 中论证
- [x] bundle 结构符合 OKF v0.2：index.md + concepts/ + examples/ + references/ + log.md
- [x] frontmatter 完整：okf_version / type / title / description / tags / generated / verified / status / stale_after / sources
- [x] sources 指向微信博文 URL 并注明公众号（"湖北"）与发布日期（2026-08-21）

## 内容质量（G1-G3 质量门）
- [x] R/G1：所有事实以 F-001 起编号登记于 references/article-source.md，文档中事实引用 F 编号，无信源外编造（对抗审查逐条比对 F-001~F-036 全部一致）
- [x] I：知识结构三层拆分（发布事实/选型矩阵/管线模式）完整覆盖博文核心内容
- [x] E/G3：4 篇 concepts 覆盖：模型详解、选型全景、场景矩阵、双模型管线；3 篇 examples 覆盖：成本演练、输出结构设计、决策树
- [x] 双模型管线模式（视觉感知 + DeepSeek 推理）及其三大收益（token 少/可缓存/不重复推理）完整呈现
- [x] 5 类选型场景（GLM 零成本/豆包国内/Gemini 长视频/GPT-5 nano+MiniCPM 本地/OCR 专用）与价格数据齐全
- [x] 与 `deepseek-ocr2` bundle 的交叉引用使用相对路径且有效（审查代理 Glob/Read 验证目标存在）

## 信任与时效
- [x] "已知边界"声明 Exp 实验模型、价格信息的时效性风险
- [x] 不可核验的声明标注"仅博文单源"（Gemini/GPT-5 nano/MiniCPM/OCR 相关），可核验的补充官方信源（三项核验全部通过，含 DeepSeek 官方新闻/智谱文档/z.ai 定价/火山引擎价格文档）
- [x] stale_after 设置合理（2026-12-31，约 4 个月，匹配视觉模型与价格迭代速度）

## 索引与链接
- [x] `ai/deepseek/index.md` 新增条目且束数 12→13，toctree 追加
- [x] `bundles/index.md` total_bundles 269、DeepSeek 分组 13、ai 域 96
- [x] 新增文档所有内部链接经检查有效（invoke gates.toctrees 通过：全部 index.md 引用有效、所有内容文档可达；gates.utf8 通过）

## 模式沉淀（博文类文章→OKF 知识包转化模式）
- [x] 模式文档位于 `.agents/docs/retrospective/patterns/documentation-patterns/blog-article-to-okf-bundle.md`
- [x] frontmatter 遵循模式库规范（id/title/date/source/maturity/validation_count/reuse_count/tags/pattern_type/category）
- [x] G3 质量门：模式包含触发场景 + 核心步骤（含归属判定决策树）+ 反模式 + 迁移验证
- [x] 以 vision-model-selection bundle 为首个演示案例（demo），步骤可对照复现（含候选位置对照表/36 事实核验表/三层映射表/4 项修复记录）
- [x] `documentation-patterns/README.md` 已登记新模式条目（目录原无 README，首建索引并补录既有条目）

## 收尾
- [x] 源博文无本地文件被修改（git status 确认 external/ 无任何变更）
- [x] tasks.md 全部勾选，最终汇总各阶段产出与质量门通过记录（见下方汇总）

---

## 最终汇总

**方法论链路**：R→I→E→V→索引收尾→模式沉淀，全链路闭环。

| 阶段 | 产出 | 质量门 |
|------|------|--------|
| R | facts.md（F-001~F-036，36 条事实 + 3 项官方核验） | G1 通过：事实无因果推断，纯客观登记 |
| I | 三层知识结构（发布事实/选型矩阵/管线模式） | 拆分完整覆盖博文核心 |
| E | vision-model-selection bundle（14 文件：4 concepts + 3 examples + 3 references + 3 index + log） | G3 通过：模式含触发/步骤/反模式/迁移 |
| V | 四视角对抗审查（事实/结构/读者/时效），修复 P1-P4 | 全视角 PASS；gates.toctrees/utf8 复核通过 |
| 索引收尾 | deepseek 分组 12→13、ai 域 95→96、全库 268→269 | 导航可达，计数同步 |
| 模式沉淀 | blog-article-to-okf-bundle.md 模式 + README 登记 | 首个演示案例可对照复现 |
