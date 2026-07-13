# Harness Engineering 七概念分析 — Verification Checklist

## 核心产出物检查
- [ ] Checklist 1: 事实清单 `facts.md` 存在且≥20条客观事实
- [ ] Checklist 2: 事实清单中无"因为/所以/导致/错误/失误"因果词（G1质量门）
- [ ] Checklist 3: 洞察文件 `insights.md` 存在且≥3条洞察
- [ ] Checklist 4: 每条洞察包含完整四元组（陈述/证据/反常识/行动）（G2质量门）
- [ ] Checklist 5: 模式文件已存入 `docs/retrospective/patterns/methodology-patterns/governance-strategy/`
- [ ] Checklist 6: 模式包含触发场景/步骤/反模式/迁移验证（G3质量门）
- [ ] Checklist 7: 对抗审查文件 `adversarial-review.md` 存在且≥5条审查意见
- [ ] Checklist 8: 至少2条审查意见已被采纳并修正（V门质量标准）
- [ ] Checklist 9: 索引文件已更新，包含新模式条目
- [ ] Checklist 10: 所有本地链接验证通过（无断链）

## 七概念流程合规性检查
- [ ] Checklist 11: 遵循 R→I→E→V→C 顺序（顺序不可颠倒原则）
- [ ] Checklist 12: 上下文传递完整（I引用R事实编号，E引用I洞察）
- [ ] Checklist 13: 所有质量门（G1-G3+V门）均已通过

## 文档规范检查
- [ ] Checklist 14: 所有产出文件遵循项目命名规范（kebab-case）
- [ ] Checklist 15: 所有产出文件包含正确的 frontmatter（id/title/source/x-toml-ref）
- [ ] Checklist 16: 复盘报告结构完整，包含所有阶段产出
