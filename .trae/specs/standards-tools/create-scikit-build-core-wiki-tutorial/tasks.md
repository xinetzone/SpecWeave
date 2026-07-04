# Tasks

- [ ] Task 1: 克隆 scikit-build-core 源码到 external/tools/scikit-build-core
  - [ ] SubTask 1.1: 确认 external/ 目录状态，创建 external/tools/ 目录层级
  - [ ] SubTask 1.2: 从 https://github.com/scikit-build/scikit-build-core 克隆源码
  - [ ] SubTask 1.3: 验证克隆成功（检查 src/scikit_build_core/ 目录、pyproject.toml、docs/ 目录存在）

- [ ] Task 2: 研究源码目录结构与核心模块
  - [ ] SubTask 2.1: 列出 src/scikit_build_core/ 完整模块树（build/、settings/、_compat/、program_search/、_vendor/ 等）
  - [ ] SubTask 2.2: 识别核心入口文件（_api.py、build/__init__.py、settings/_skbuild_settings.py 等）
  - [ ] SubTask 2.3: 记录每个模块的职责与关键文件路径锚点

- [ ] Task 3: 抓取官方文档与教程资源
  - [ ] SubTask 3.1: 抓取 https://scikit-build-core.readthedocs.io/en/latest/ 首页与目录结构
  - [ ] SubTask 3.2: 抓取官方文档关键页面（getting-started、configuration、usage、cmake-config、troubleshooting）
  - [ ] SubTask 3.3: 抓取 https://daobook.github.io/pygallery/study/fields/scikit-build-core/index.html 教程目录与内容
  - [ ] SubTask 3.4: 整理三方内容差异与互补点（源码细节 vs 官方文档 vs 教程示例）

- [ ] Task 4: 设计 Wiki 章节结构
  - [ ] SubTask 4.1: 基于源码研究与文档抓取，确定 8-10 个原子化章节文件
  - [ ] SubTask 4.2: 设计章节间导航关系（前后向链接、入口枢纽文件）
  - [ ] SubTask 4.3: 制定文件命名规范（NN-slug.md，NN 为两位序号，slug 为英文短横线命名）

- [ ] Task 5: 编写概述与导航枢纽文档（00-overview.md）
  - [ ] SubTask 5.1: 撰写 scikit-build-core 定位、背景、与同类工具对比
  - [ ] SubTask 5.2: 生成完整目录导航表（链接到所有章节）
  - [ ] SubTask 5.3: 提供 3 条阅读路径（快速上手 / 深入理解 / 排错参考）

- [ ] Task 6: 编写概念与架构章节（01-concepts-architecture.md）
  - [ ] SubTask 6.1: 解释 PEP 517/660 构建后端机制
  - [ ] SubTask 6.2: 解释 CMake 集成机制与 wheel 构建流程
  - [ ] SubTask 6.3: 绘制 Mermaid 架构图（构建流程图）

- [ ] Task 7: 编写项目目录结构章节（02-project-structure.md）
  - [ ] SubTask 7.1: 基于 Task 2 研究结果，描述 src/scikit_build_core/ 模块树
  - [ ] SubTask 7.2: 每个模块标注源码文件路径锚点
  - [ ] SubTask 7.3: 说明 _vendor/、_compat/ 等特殊目录的作用

- [ ] Task 8: 编写核心 API 与配置章节（03-core-api-and-config.md）
  - [ ] SubTask 8.1: 覆盖 build/build_editable 钩子签名与调用时机
  - [ ] SubTask 8.2: 覆盖 [tool.scikit-build] 全部配置项（最小示例 + 完整示例）
  - [ ] SubTask 8.3: 提供 CMakeLists.txt 集成示例代码

- [ ] Task 9: 编写入门到进阶操作指南（04-quickstart-to-advanced.md）
  - [ ] SubTask 9.1: 三级递进路径（最小 CMake 项目 → 真实 C++ 扩展 → 高级配置）
  - [ ] SubTask 9.2: 每级提供可验证验收标准
  - [ ] SubTask 9.3: 涵盖 Ninja、缓存复用、abi3、交叉编译等进阶主题

- [ ] Task 10: 编写常见问题与最佳实践章节（05-faq-and-best-practices.md）
  - [ ] SubTask 10.1: 跨平台编译问题诊断流程
  - [ ] SubTask 10.2: 依赖管理、可编辑安装失败排查
  - [ ] SubTask 10.3: CI 集成最佳实践（GitHub Actions 示例）

- [ ] Task 11: 编写参考资料与扩展阅读章节（06-resources.md）
  - [ ] SubTask 11.1: 官方文档链接、源码仓库链接、教程资源链接
  - [ ] SubTask 11.2: 术语表（PEP 517/660、wheel、sdist、abi3、Ninja 等）
  - [ ] SubTask 11.3: 关联本项目知识库条目（interface-api-abi-protocol-wiki 等）

- [ ] Task 12: 索引同步与链接验证
  - [ ] SubTask 12.1: 运行 docgen 工具更新 docs/knowledge/README.md 索引
  - [ ] SubTask 12.2: 运行 check-links.py 验证所有相对路径链接无断链
  - [ ] SubTask 12.3: 验证所有文档 YAML frontmatter 含 source 字段

# Task Dependencies

- Task 2 依赖 Task 1（需源码才能研究目录结构）
- Task 3 可与 Task 2 并行（在线文档抓取不依赖本地源码）
- Task 4 依赖 Task 2 + Task 3（需整合源码研究与文档抓取结果才能设计章节）
- Task 5-11 依赖 Task 4（需章节结构确定后才能逐章编写）
- Task 5-11 之间可部分并行，但建议按序号顺序执行以保证内容连贯
- Task 12 依赖 Task 5-11 全部完成（索引与链接验证需所有文档就位）
