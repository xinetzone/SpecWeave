# 规范落地度量批量对比报告

- **扫描时间**: 2026-07-02 20:32:47
- **项目根**: `D:\spaces\SpecWeave`
- **全局加权评分**: **83.7/100** (B (良好))
- **扫描目录数**: 3
- **总文件数**: 1137

## 目录对比总览

| 目录 | Profile | 文件数 | 综合评分 | 评级 | FM合规率 | 链接有效率 | 溯源覆盖率 | 模式引用率 | 断链数 | 大文件数 |
|------|---------|--------|---------|------|---------|-----------|-----------|-----------|--------|---------|
| `.agents` | specs | 140 | **91.3** | A | 100.0% | 100.0% | 100.0% | 25.7% | 0 | 26 |
| `.agents/scripts` | code | 8 | **61.9** | D | 37.5% | 100.0% | 37.5% | 37.5% | 0 | 4 |
| `docs` | docs | 989 | **82.8** | B | 95.0% | 98.8% | 89.8% | 18.1% | 42 | 60 |

## 权重配置

| Profile | 适用场景 | 权重配置 |
|---------|---------|---------|
| `docs` | 文档区（默认）- 适用于docs/等内容文档目录 | frontmatter_compliance=0.25, link_validity=0.25, source_traceability=0.2, pattern_reference_rate=0.15, nav_link_compliance=0.15 |
| `specs` | 规范区 - 适用于.agents/等规范定义目录（模式引用/导航降权，排除专用schema文件） | frontmatter_compliance=0.35, link_validity=0.3, source_traceability=0.25, pattern_reference_rate=0.05, nav_link_compliance=0.05 |
| `code` | 代码区 - 适用于scripts/等工具脚本目录（frontmatter降权，链接升权） | frontmatter_compliance=0.1, link_validity=0.4, source_traceability=0.1, pattern_reference_rate=0.25, nav_link_compliance=0.05, large_file_ratio_inverted=0.1 |

## 各目录问题明细

### .agents (specs) — 91.3分/A (优秀)

- ✅ Frontmatter无问题

- ✅ 链接全部有效
- 📄 待原子化大文件(>300行): 26个

### .agents/scripts (code) — 61.9分/D (较差)

**Frontmatter问题**:
- 缺少id字段: 5个文件
- 缺少x-toml-ref: 5个文件
- 包含应外部化字段: 5个文件
- 存在嵌套结构: 1个文件

- ✅ 链接全部有效
- 📄 待原子化大文件(>300行): 4个

### docs (docs) — 82.8分/B (良好)

**Frontmatter问题**:
- 缺少id字段: 104个文件
- 缺少x-toml-ref: 104个文件
- 包含应外部化字段: 43个文件
- frontmatter膨胀(>15行): 1个文件

- 🔗 断链: 42个（建议运行 `check-links.py --fix`）
- 📄 待原子化大文件(>300行): 60个
