# Containers 生态 OKF Wiki 生成 - Verification Checklist

## 目录结构
- [ ] `doc/bundles/containers/` 目录已创建
- [ ] `doc/bundles/containers/index.md` 存在且包含 `okf_version: "0.2"` frontmatter
- [ ] 11 个子项目 bundle 目录均存在：conmon, conmon-rs, fuse-overlayfs, libocispec, olot, omlmd, podman-py, podman-compose, qm, toolbox, ai-lab-recipes

## Bundle 结构（每个项目）
- [ ] 每个 bundle 根目录有 `index.md`（无 frontmatter，含 toctree）
- [ ] 每个 bundle 根目录有 `log.md`
- [ ] 每个 bundle 有 `concepts/` 子目录
- [ ] 每个 bundle 有 `examples/` 子目录
- [ ] 每个 bundle 有 `references/` 子目录
- [ ] `concepts/` 目录下有 `index.md`
- [ ] `examples/` 目录下有 `index.md`
- [ ] `references/` 目录下有 `index.md`

## 文档数量
- [ ] 每个 bundle 的 `concepts/` 下 ≥3 个概念文档
- [ ] 每个 bundle 的 `examples/` 下 ≥2 个示例文档
- [ ] 每个 bundle 的 `references/` 下 ≥1 个信源文档

## Frontmatter 合规性
- [ ] 每个概念文档（concepts/*.md）frontmatter 包含 `type: Concept`
- [ ] 每个示例文档（examples/*.md）frontmatter 包含 `type: Example`
- [ ] 每个信源文档（references/*.md）frontmatter 包含 `type: Reference`
- [ ] 所有文档包含 `title` 字段
- [ ] 所有文档包含 `description` 字段（30-80字）
- [ ] 所有文档包含 `tags` 字段（列表形式）
- [ ] 所有文档包含 `sources` 字段（指向 references/ 下的信源）
- [ ] 所有文档包含 `generated` 字段（含 by 和 at）
- [ ] 所有文档包含 `verified` 字段
- [ ] 所有文档包含 `status` 字段（draft/stable/deprecated）
- [ ] 所有文档包含 `stale_after` 字段（YYYY-MM-DD格式）

## 内容质量
- [ ] 文档正文使用中文撰写
- [ ] 技术术语首次出现时附英文括号注释
- [ ] 代码块标注语言（c/rust/python/go/bash）
- [ ] 每个概念文档结尾有「## 相关概念」章节
- [ ] 交叉引用使用 `/` 开头的 bundle-relative 绝对路径
- [ ] 无 `../` 相对路径交叉引用

## API 真实性验证（Grep）
- [ ] conmon 文档中引用的 C 函数/结构体在源码中存在
- [ ] fuse-overlayfs 文档中引用的 Rust 模块/函数在源码中存在
- [ ] podman-py 文档中引用的 Python 类/方法在源码中存在
- [ ] olot/omlmd 文档中引用的 Python API 在源码中存在
- [ ] toolbox 文档中引用的 Go 函数/包在源码中存在
- [ ] 无虚构的类名/方法名/函数名

## 链接完整性
- [ ] 所有交叉引用链接指向存在的文件
- [ ] 各级 index.md 的 toctree 中引用的文件均存在
- [ ] toctree 中无遗漏的新增文档
- [ ] 无指向不存在文件的死链

## 总索引更新
- [ ] `doc/bundles/index.md` 生态关系图中加入 containers 域节点
- [ ] `doc/bundles/index.md` 推荐入门路径中加入 containers 域（可选位置）
- [ ] `doc/bundles/index.md` 十域导航中加入 containers 域章节
- [ ] `doc/bundles/index.md` hidden toctree 中加入 `containers/index`
- [ ] `total_bundles` 计数更新为 259
- [ ] `groups` 和 `domains` 计数正确更新

## 质量门
- [ ] `invoke gates.utf8` 通过（UTF-8 编码无 BOM）
- [ ] `invoke gates.toctrees` 通过（无断链、无孤立文档、bundle 根 index 完整）
- [ ] `invoke gates.all` 全部通过

## 日志与溯源
- [ ] 每个 bundle 的 log.md 有初始条目（记录创建日期和生成方式）
- [ ] sources 字段中的 resource 路径正确指向 references/ 下文件
- [ ] generated.by 使用 actor 约定格式（如 `reference_agent/trae-cn`）
