# docs/knowledge/learning 目录主题分类系统性划分 - The Implementation Plan

## [x] Task 0: 现状调研与引用索引构建
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 盘点 learning 目录下所有文件和子目录，确认完整清单（24个原子化目录 + 35+单文件）
  - 运行 `python .agents/scripts/build-ref-index.py --path docs/knowledge/learning` 构建反向引用索引，识别所有受影响的引用方
  - 对 dspark-paper-wiki.md 和 ian-xiaohei-illustrations.md 进行内容确认，确定最终归属主题
  - 输出完整的「源路径 → 目标路径」映射表，每个 Wiki 明确目标主题目录
  - 确认已原子化 Wiki 的同名根目录 .md 文件是入口文件，与对应目录一同迁移
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-0.1: 构建引用索引成功，无报错
  - `programmatic` TR-0.2: 完整映射表覆盖所有 Wiki（24个原子化目录 + 所有单文件），无遗漏
  - `human-judgement` TR-0.3: dspark 和 ian-xiaohei 两个 Wiki 的主题归属经内容确认后合理
- **Notes**: 映射表是后续所有迁移操作的基础，必须 100% 准确

## [x] Task 1: 创建主题目录结构
- **Priority**: high
- **Depends On**: Task 0
- **Description**:
  - 在 learning 目录下创建 8 个一级主题子目录（01-08）
  - 在 07-vendor-product-learning/ 下创建二级子目录 sunlogin/ 和 tuya/
  - 确认目录创建成功，命名符合 `{两位数编号}-{kebab-case}` 规范
- **Acceptance Criteria Addressed**: AC-1, AC-4
- **Test Requirements**:
  - `programmatic` TR-1.1: 8个一级主题目录全部存在，命名正确
  - `programmatic` TR-1.2: 07目录下 sunlogin/ 和 tuya/ 二级子目录存在
- **Notes**: 仅创建空目录，不移动任何文件

## [x] Task 2: 分批迁移文件（按主题逐个迁移）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 按主题编号顺序（01→08）逐个主题迁移：
    - SubTask 2.0: 迁移 01-agent-protocols-interfaces（约10个Wiki）
    - SubTask 2.1: 迁移 02-agent-engineering-methodology（约6个Wiki）
    - SubTask 2.2: 迁移 03-agent-platforms-tools（约12个Wiki）
    - SubTask 2.3: 迁移 04-docs-markup-tooling（约4个Wiki）
    - SubTask 2.4: 迁移 05-ai-multimodal-content（约5个Wiki）
    - SubTask 2.5: 迁移 06-business-trends-analysis（约5个Wiki）
    - SubTask 2.6: 迁移 07-vendor-product-learning（向日葵到sunlogin/，涂鸦到tuya/）
    - SubTask 2.7: 迁移 08-systems-infrastructure（约2个Wiki）
  - 每个 Wiki 迁移时：原子化目录整体移动（保持内部结构），单文件直接移动
  - 每迁移完一个主题，立即运行链接检查和修复
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-5
- **Test Requirements**:
  - `programmatic` TR-2.1: 每个主题迁移后，文件/目录位于正确的目标路径
  - `programmatic` TR-2.2: 原子化 Wiki 目录迁移后内部文件结构完整，无丢失
  - `programmatic` TR-2.3: 每个主题迁移后源位置无残留文件/目录
- **Notes**: 严格按主题逐个迁移，不要一次性全部移动。每个主题迁移后立即验证，发现问题及时修正

## [x] Task 3: 修复内部链接引用
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 运行 `python .agents/scripts/check-links.py --path docs/knowledge/learning --fix` 自动修复相对路径
  - 手动检查原子化 Wiki 内的章节导航链接（prev/next/directory），确保路径正确
  - 检查并修复 Wiki 之间的交叉引用路径
  - 检查并修复已原子化 Wiki 根目录入口文件中的内部导航链接
- **Acceptance Criteria Addressed**: AC-8, AC-9
- **Test Requirements**:
  - `programmatic` TR-3.1: check-links.py 运行结果显示 0 个断链
  - `human-judgement` TR-3.2: 抽查3-5个原子化 Wiki 的 prev/next 导航链接正确
  - `programmatic` TR-3.3: 跨 Wiki 交叉引用路径正确指向新位置
- **Notes**: 特别注意目录深度变化（多了一层主题目录），`../` 层级需要增加

## [x] Task 4: 创建CATEGORIES.md主题划分说明
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 创建 docs/knowledge/learning/CATEGORIES.md
  - 内容包含：分类设计原则（6条）、8个主题详细定义（名称、核心主题词、边界说明、认知定位）、每个主题下的完整 Wiki 清单（带链接和一句话说明）、主题间关联关系图、推荐学习路径
  - 文档遵循项目 Markdown 规范，使用 YAML frontmatter
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `human-judgement` TR-4.1: 文档结构完整，包含所有要求的章节
  - `human-judgement` TR-4.2: 每个主题下列出的 Wiki 清单与实际目录内容一致
  - `programmatic` TR-4.3: 文档内链接指向正确的 Wiki 路径

## [x] Task 5: 创建/更新learning/README.md主题导航
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 创建或更新 docs/knowledge/learning/README.md
  - 内容包含：learning 知识库简介、统计数字（Wiki总数、主题数、原子化Wiki数）、8个主题导航表格（编号、名称、描述、Wiki数）、每个主题下的 Wiki 快速链接列表、推荐学习路径建议、指向 CATEGORIES.md 的链接
  - 作为 learning 目录的入口文档
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `human-judgement` TR-5.1: README 内容完整，导航清晰
  - `programmatic` TR-5.2: 所有 Wiki 链接指向正确路径
  - `human-judgement` TR-5.3: 学习路径建议逻辑合理

## [x] Task 6: 更新上层文档索引
- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 更新 docs/knowledge/README.md 中的 learning 相关部分
  - 将原来的平铺列表改为按主题分类展示，链接路径更新为新的主题目录结构
  - 检查 docs/knowledge/README.md 中其他可能引用 learning 下文件的地方（如统计数字、分类表格）
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `programmatic` TR-6.1: docs/knowledge/README.md 中所有 learning 相关链接路径正确
  - `human-judgement` TR-6.2: learning 部分展示方式清晰，反映新的分类结构
- **Notes**: 注意 docs/knowledge/README.md 中的统计数字可能需要更新

## [x] Task 7: 全量验证与收尾
- **Priority**: high
- **Depends On**: Task 3, Task 4, Task 5, Task 6
- **Description**:
  - 运行全量链接检查：`python .agents/scripts/check-links.py --path docs/knowledge`
  - 运行迁移完整性验证：`python .agents/scripts/check-move.py`（如有对应功能）
  - 检查文件总数是否一致（迁移前后对比）
  - 清理迁移过程中产生的空目录
  - 抽查若干 Wiki 的 YAML frontmatter 完整性
  - 运行 `python .agents/scripts/finalize-atomization.py --path docs/knowledge/learning` 完成收尾
- **Acceptance Criteria Addressed**: AC-8, AC-11, AC-12, AC-13
- **Test Requirements**:
  - `programmatic` TR-7.1: docs/knowledge 全目录 0 断链
  - `programmatic` TR-7.2: 迁移前后文件总数一致（允许新增 README.md 和 CATEGORIES.md）
  - `programmatic` TR-7.3: learning 目录下无空目录残留
  - `programmatic` TR-7.4: 抽查的 frontmatter 字段完整无损坏
- **Notes**: finalize-atomization.py 会自动处理断链修复和导航更新

## [x] Task 8: 主题看板更新
- **Priority**: low
- **Depends On**: Task 7
- **Description**:
  - 更新 .trae/specs/docs-restructure/README.md 主题看板，登记本 spec 完成状态
  - 补充核心交付物说明
- **Acceptance Criteria Addressed**: (项目管理要求)
- **Test Requirements**:
  - `human-judgement` TR-8.1: 主题看板中本 spec 标记为完成，交付物链接正确
