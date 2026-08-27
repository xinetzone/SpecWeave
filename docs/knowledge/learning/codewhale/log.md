# 变更日志

## 2026-08-22

- 初始转换为 OKF v0.2 Bundle
- 将 9 个 Markdown 文件重组为 OKF 标准目录结构：
  - `index.md` → 根 `index.md`（frontmatter 精简为仅 `okf_version: "0.2"`）
  - `comparison.md` → `concepts/comparison.md`（Reference）
  - `tech/changelog.md` → `concepts/tech/changelog.md`（Reference）
  - `tech/deploy.md` → `concepts/tech/deploy.md`（Tutorial）
  - `tech/features.md` → `concepts/tech/features.md`（Tutorial）
  - `tech/intro.md` → `concepts/tech/intro.md`（Tutorial）
  - `tech/quickstart.md` → `concepts/tech/quickstart.md`（Tutorial）
  - `general/domain/index.md` → `concepts/general/domain/index.md`（子目录索引，移除 frontmatter）
  - `topics/index.md` → `concepts/topics/index.md`（子目录索引，移除 frontmatter）
- 为 6 个内容文件补全 OKF frontmatter：
  - `type`（Reference/Tutorial）
  - `generated`（by: process:docs-to-okf-conversion, at: 2026-08-22T00:00:00Z，嵌套 YAML 格式）
  - `verified`（by: process:seven-concepts-v, at: 2026-08-22T00:00:00Z，嵌套 YAML 格式）
  - `status: "stable"`
  - `stale_after: "2027-08-22"`
  - 保留原有 frontmatter 字段（id、title、description、last_updated、source、category、tags）
- 链接转换：同 Bundle 内 Markdown 链接统一改为 `/` 开头的 bundle-absolute 路径
  - 根 `index.md` 中指向 `tech/`、`general/`、`topics/` 的链接改为 `/concepts/...`
  - `concepts/` 下内容文件的同级链接改为 `/concepts/tech/...`
  - 返回根首页的链接改为 `/index.md`
  - 锚点链接（如 `#3-中国用户镜像加速`）与外部 URL 保持原样
- 创建 `concepts/index.md`（无 frontmatter，导航索引）
- 正文内容不改写，仅调整 frontmatter 与内部链接路径
