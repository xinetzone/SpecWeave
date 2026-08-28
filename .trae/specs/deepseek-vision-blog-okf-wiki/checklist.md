# Checklist

## 归属与结构
- [ ] bundle 位于 `ai/deepseek/vision-model-selection/`，归属分析已在 spec.md 中论证
- [ ] bundle 结构符合 OKF v0.2：index.md + concepts/ + examples/ + references/ + log.md
- [ ] frontmatter 完整：okf_version / type / title / description / tags / generated / verified / status / stale_after / sources
- [ ] sources 指向微信博文 URL 并注明公众号（"湖北"）与发布日期（2026-08-21）

## 内容质量（G1-G3 质量门）
- [ ] R/G1：所有事实以 F-001 起编号登记于 references/article-source.md，文档中事实引用 F 编号，无信源外编造
- [ ] I：知识结构三层拆分（发布事实/选型矩阵/管线模式）完整覆盖博文核心内容
- [ ] E/G3：4 篇 concepts 覆盖：模型详解、选型全景、场景矩阵、双模型管线；3 篇 examples 覆盖：成本演练、输出结构设计、决策树
- [ ] 双模型管线模式（视觉感知 + DeepSeek 推理）及其三大收益（token 少/可缓存/不重复推理）完整呈现
- [ ] 5 类选型场景（GLM 零成本/豆包国内/Gemini 长视频/GPT-5 nano+MiniCPM 本地/OCR 专用）与价格数据齐全
- [ ] 与 `deepseek-ocr2` bundle 的交叉引用使用相对路径且有效

## 信任与时效
- [ ] "已知边界"声明 Exp 实验模型、价格信息的时效性风险
- [ ] 不可核验的声明标注"仅博文单源"，可核验的补充官方信源
- [ ] stale_after 设置合理（视觉模型与价格迭代快，不超过 2027 年内近点）

## 索引与链接
- [ ] `ai/deepseek/index.md` 新增条目且束数 12→13，toctree 追加
- [ ] `bundles/index.md` total_bundles 269、DeepSeek 分组 13
- [ ] 新增文档所有内部链接经检查有效（check-links.py 或等效验证）

## 模式沉淀（博文类文章→OKF 知识包转化模式）
- [ ] 模式文档位于 `.agents/docs/retrospective/patterns/documentation-patterns/blog-article-to-okf-bundle.md`
- [ ] frontmatter 遵循模式库规范（id/title/date/source/maturity/validation_count/reuse_count/tags/pattern_type/category）
- [ ] G3 质量门：模式包含触发场景 + 核心步骤（含归属判定决策树）+ 反模式 + 迁移验证
- [ ] 以 vision-model-selection bundle 为首个演示案例（demo），步骤可对照复现
- [ ] `documentation-patterns/README.md` 已登记新模式条目

## 收尾
- [ ] 源博文无本地文件被修改（external/ 无变更）
- [ ] tasks.md 全部勾选，最终汇总各阶段产出与质量门通过记录
