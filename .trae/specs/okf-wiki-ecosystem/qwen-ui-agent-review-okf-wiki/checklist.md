# Checklist：Qwen-UI-Agent 技术评测

## R 阶段
- [x] C1 敏感度预检（公开内容，标准工作流）
- [x] C2 内容性质判定（技术评测/选型骨架，含examples）
- [x] C3 归属判定（ai/ai-agent/，GUI Agent属Agent框架）
- [x] C4 事实采集 F-001~F-044（44条：博文31条+核验补充13条）
- [x] C5 P0核验8项（5✅ + 2⚠️ + 1❌）
- [x] C6 3项勘误识别并记录（MAI-UI权重混淆/58%以偏概全/硬件要求有误）

## E 阶段
- [x] C7 index.md 根索引（frontmatter+性质声明+信源说明+结构总览+导航+信任声明+已知边界+toctree）
- [x] C8 concepts/ 3篇概念文档（项目概述/技术能力/实测踩坑）
- [x] C9 concepts/index.md 目录索引
- [x] C10 examples/ 1篇示例（3个内部流程实测）
- [x] C11 examples/index.md 目录索引
- [x] C12 references/ 2篇信源文档（article-source.md 44事实清单 + verification.md 8项核验）
- [x] C13 references/index.md 目录索引（含F编号索引表+可信度说明）
- [x] C14 log.md 生成日志（R→I→E→V链路+文件清单+G1-G4质量门+勘误处理说明）

## V 阶段
- [x] C15 UTF-8严格解码（11文件全部PASS）
- [x] C16 toctree三级完整（根→3子目录→6内容文档）
- [x] C17 相对链接全部可达（PASS，0断链）
- [x] C18 无file:///绝对路径（PASS）
- [x] C19 external/无变更（PASS）
- [x] C20 父分组index更新（ai-agent total_bundles 22→23，📰产品资讯板块追加，toctree追加）
- [x] C21 bundles/index.md更新（total 271→272，ai域98→99束，ai-agent 21→22）
- [x] C22 3项勘误在bundle中如实呈现（未静默照搬博文错误）
- [x] C23 作者实测体验标注为团队自述（F-038，非官方benchmark）
- [x] C24 分数自报可信度边界标注（F-027）
- [x] C25 stale_after设为2026-12-31（约4个月，技术项目迭代中）
