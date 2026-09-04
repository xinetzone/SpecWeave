# Zhihu CLI 知乎数据开放平台 OKF Wiki - Review Checklist

> 本文档仅在 Review 阶段填写。Specify 和 Plan 阶段不得修改此文件。

## Review History

| 轮次 | 日期 | 审查者 | 结果 | 备注 |
|------|------|--------|------|------|
| R1 | - | - | pending | 首次审查 |

---

## 审查检查点

### 事实与溯源
- [ ] **CP-1**: 所有关键事实（数字、日期、产品名、官方表态）均有 F 编号引用
- [ ] **CP-2**: 双份 F 编号一致（spec facts.md 与 bundle references/article-source.md 编号集合相等且连续）
- [ ] **CP-3**: P0 项均有核验结论与核验来源，厂商自述数据明确标注
- [ ] **CP-4**: 勘误已落实（verification.md 中 ❌/⚠️ 项在正文呈现正确值）

### OKF 规范合规
- [ ] **CP-5**: 目录结构符合 OKF v0.2（index + concepts/ + examples/ + references/ + log）
- [ ] **CP-6**: 每个 index.md 含 toctree 块（排除指令行后条目数与实际文件数一致）
- [ ] **CP-7**: frontmatter 必填字段完整（okf_version/type/title/description/tags/generated/verified/status/stale_after/sources）
- [ ] **CP-8**: 相对链接全部可达，无 file:/// 绝对路径

### 内容质量
- [ ] **CP-9**: 事实与观点分层，作者观点不显式标注为"官方结论"
- [ ] **CP-10**: 时效性内容标注时点与 stale_after 日期
- [ ] **CP-11**: examples/ 内容符合"操作可复现性两问"判据
- [ ] **CP-12**: 同主题 bundle 互链（如有相邻主题）

### 索引与计数
- [ ] **CP-13**: 父级分组 index 接入正确（导航表 + toctree + 计数）
- [ ] **CP-14**: 全库计数同步（bundles/index.md 三处一致）
- [ ] **CP-15**: 新 bundle 可从根 index 通过 toctree BFS 到达

---

## 可行动发现（Actionable Findings）

> Review 结果为 fail 时，每条发现对应一条修复 issue，写入 tasks.md 作为 pending issue。

| # | 严重程度 | 发现描述 | 对应 AC | 修复建议 |
|---|---------|---------|---------|---------|
| - | - | - | - | - |
