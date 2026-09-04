# Checklist

## 源码准备

- [x] `external/tools/scikit-build-core` 目录已创建并克隆源码
- [x] `external/tools/scikit-build-core/src/scikit_build_core/` 核心模块目录存在
- [x] `external/tools/scikit-build-core/pyproject.toml` 项目配置文件存在
- [x] `external/tools/scikit-build-core/docs/` 官方文档源码存在（用于交叉验证）

## Wiki 目录结构

- [x] `docs/knowledge/learning/scikit-build-core-wiki/` 目录已创建
- [x] 包含 `00-overview.md` 入口枢纽文件
- [x] 包含 01-06 共 6 个核心章节文件（或按实际拆分不少于 6 个）
- [x] 所有文件命名遵循 `NN-slug.md` 规范（NN 两位序号，slug 英文短横线）

## 内容完整性

- [x] 概述章节说明 scikit-build-core 定位、与 setuptools/distutils/scikit-build(旧版) 关系
- [x] 概述章节含完整目录导航表，链接到所有章节
- [x] 概念架构章节解释 PEP 517/660、CMake 集成、wheel 构建
- [x] 概念架构章节含至少一张 Mermaid 架构图
- [x] 目录结构章节基于实际源码，模块说明标注文件路径锚点
- [x] API 章节覆盖 build/build_editable 钩子与 [tool.scikit-build] 配置项
- [x] API 章节每示例含可复制最小代码块
- [x] 入门到进阶指南含三级递进路径与验收标准
- [x] 常见问题章节含跨平台编译、依赖管理、CI 集成实践
- [x] 参考资料章节含术语表与官方链接

## 文档规范一致性

- [x] 每个文档含 YAML frontmatter
- [x] frontmatter 含 `source` 字段（值为 `"spec:create-scikit-build-core-wiki-tutorial"`）
- [x] 文档间引用使用相对路径（无 `file:///` 绝对路径）
- [x] 源码引用标注文件路径（必要时含 `#L行号` 锚点）
- [x] Mermaid 图表符合安全编码六规则（无非法字符、正确转义）

## 索引与链接验证

- [x] `docs/knowledge/README.md` 索引已通过 docgen 工具更新
- [x] scikit-build-core-wiki 条目出现在 learning 分类列表中
- [x] 运行 `python .agents/scripts/check-links.py --path docs/knowledge/learning/scikit-build-core-wiki/` 无断链
- [x] 所有章节间导航链接（前一篇/后一篇）可达

## 交叉引用与关联

- [x] 参考资料章节链接到本项目 `interface-api-abi-protocol-wiki`（构建工具链 ABI 相关）
- [x] 参考资料章节链接到官方文档与教程资源
- [x] 入口文档（00-overview.md）在 docs/knowledge/README.md 索引中可点击到达
