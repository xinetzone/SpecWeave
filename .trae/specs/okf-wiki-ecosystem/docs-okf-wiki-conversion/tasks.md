# docs 目录 OKF Wiki 教程规范化改造 - 实施计划

## Task 1: 移植 conf.py frontmatter 日期兼容性钩子

- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 从 `projects/awesome-okf-xs/doc/conf.py` 移植 `_quote_frontmatter_dates` source-read 钩子到 `docs/conf.py`
  - 该钩子自动为 frontmatter 中的裸日期/时间戳补上双引号，防止 myst_parser 解析为 datetime 对象导致 JSON 序列化失败
  - 同时移植 `_has()` 函数的 ModuleNotFoundError 容错（已有则跳过）
- **Acceptance Criteria Addressed**: AC-3, AC-7
- **Test Requirements**:
  - `rule` TR-1.1: `docs/conf.py` 中存在 `_quote_frontmatter_dates` 函数且连接到 `source-read` 事件；证据：Grep 搜索函数定义和 `connect` 调用
  - `rule` TR-1.2: Sphinx 构建不因裸日期格式崩溃；证据：`sphinx-build -b dummy docs _build/dummy` 退出码 0
- **Notes**: 参考 awesome-okf-xs/doc/conf.py 的实现

## Task 2: 创建质量门检查脚本

- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 从 `projects/awesome-okf-xs/scripts/` 适配以下脚本到 `docs/scripts/`：
    - `check-toctrees.py`: 检查 toctree 完整性（无断链、无孤立文档、bundle 根 index 完整）
    - `check-utf8.py`: 检查所有 Markdown 文件 UTF-8 编码无 BOM
  - 根据 docs 目录结构调整脚本中的路径逻辑（awesome-okf-xs 的脚本可能假设了特定的 bundle 结构）
  - 新增 `check-frontmatter.py`: 检查所有非保留 .md 文件的 frontmatter 合规性（type 字段存在性、index.md 层级权限）
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, NFR-2
- **Test Requirements**:
  - `rule` TR-2.1: `docs/scripts/check-utf8.py` 可独立运行并正确报告编码问题；证据：命令执行输出
  - `rule` TR-2.2: `docs/scripts/check-toctrees.py` 可独立运行并正确报告 toctree 问题；证据：命令执行输出
  - `rule` TR-2.3: `docs/scripts/check-frontmatter.py` 可检测到缺失 type 字段和 index.md 越权 okf_version；证据：命令执行输出

## Task 3: 重构 tasks.py 为 tasks/ 包

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 将 `docs/tasks.py` 重构为 `docs/tasks/` 包
  - `tasks/__init__.py`: 命名空间入口，导入所有任务命名空间
  - `tasks/docs.py`: 文档构建任务（build/clean/html/linkcheck/doctest/browse）
  - `tasks/gates.py`: 质量门任务（utf8/toctrees/frontmatter/all）
  - 保持现有构建任务功能不变，新增质量门任务
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-3.1: `invoke docs.html` 可正常构建 HTML 文档；证据：命令退出码 0
  - `rule` TR-3.2: `invoke gates.all` 可运行所有质量门检查；证据：命令执行输出
  - `rule` TR-3.3: `invoke gates.utf8`、`invoke gates.toctrees`、`invoke gates.frontmatter` 可独立运行；证据：各命令退出码

## Task 4: 修复各级 index.md frontmatter 层级权限

- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 移除以下子目录 index.md 的 frontmatter（整个 `---...---` 块）：
    - `docs/knowledge/index.md`
    - `docs/tech/index.md`
    - `docs/retrospective/index.md`
    - `docs/general/index.md`
    - `docs/topics/index.md`
    - `docs/refactor/index.md`
    - 所有 `concepts/index.md`
    - 所有 `examples/index.md`
    - 所有 `references/index.md`
    - 其他非根目录的 index.md
  - 保留 `docs/index.md` 的 `okf_version: "0.2"` frontmatter
  - 注意：`docs/README.md` 有完整 frontmatter，但该文件将在 Task 6 中处理
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-4.1: 除 `docs/index.md` 外，0 个 index.md 文件包含 frontmatter；证据：`check-frontmatter.py` 输出
  - `rubric` TR-4.2: 移除 frontmatter 后 index.md 正文内容完整保留；scale 1-5；anchors 1=内容丢失/3=内容完整但格式有小问题/5=完全保留；threshold >= 4；证据：git diff 抽样审查

## Task 5: 统一知识包 log.md 格式

- **Status**: `pending`
- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 审查所有 log.md 文件，确保符合 OKF 规范：
    - 使用 `YYYY-MM-DD` 日期标题
    - 日期分组倒序排列（最新在前）
    - 每个日期条目使用 `-` 列表项
    - 前导粗体词约定（如 `- **Bundle 名称**：...`）
  - 对格式不规范的 log.md 进行修正
  - 为缺失 log.md 的 bundle 补充最小 log.md
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-5.1: 所有 bundle 目录有 log.md 文件；证据：目录扫描
  - `rubric` TR-5.2: log.md 格式一致性；scale 1-5；anchors 1=格式混乱/3=基本一致有少量偏差/5=完全一致；threshold >= 4；证据：抽样审查

## Task 6: 清理 docs/README.md 重复文件

- **Status**: `pending`
- **Priority**: medium
- **Depends On**: None
- **Description**:
  - `docs/README.md` 与 `docs/index.md` 内容高度重复
  - 删除 `docs/README.md`（index.md 已是 Sphinx 主文档入口）
  - 检查是否有其他文件引用了 README.md，如有则更新为 index.md
- **Acceptance Criteria Addressed**: FR-8
- **Test Requirements**:
  - `rule` TR-6.1: `docs/README.md` 不存在；证据：文件系统检查
  - `rule` TR-6.2: 无断链指向已删除的 README.md；证据：Grep 搜索 `README.md` 引用

## Task 7: 统一 tech/ 目录文档 frontmatter

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 审查 `docs/tech/` 下所有非 index.md/log.md 文件的 frontmatter
  - 确保每个文件有 `type` 字段
  - 统一字段顺序：type → title → description → tags → generated → verified → status → stale_after → sources → 扩展字段
  - 保留已有扩展字段（id/date/category/source 等）
  - tech/ 已在 2026-08-22 完成过转换，主要做验证和微调
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-7.1: tech/ 下所有内容文档 frontmatter 含非空 type；证据：check-frontmatter.py
  - `rule` TR-7.2: 无虚构字段引用；证据：frontmatter 字段审查

## Task 8: 统一 knowledge/ 目录文档 frontmatter

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 审查 `docs/knowledge/` 下所有非 index.md/log.md 文件的 frontmatter
  - 这是最大的目录，包含 15+ 个 wiki bundle
  - 确保每个文件有 `type` 字段
  - 统一字段顺序
  - 处理特殊情况：
    - 部分文件有 `id`、`date`、`category` 等非标准字段（保留为扩展字段）
    - 部分文件可能缺少 `generated`/`verified`/`status`/`stale_after`（补充默认值）
    - `references/seven-concepts-report.md` 等过程文档应有正确 type
  - 分批处理，每批 5-7 个文件
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-8.1: knowledge/ 下所有内容文档 frontmatter 含非空 type；证据：check-frontmatter.py
  - `rubric` TR-8.2: frontmatter 字段顺序和格式一致性；scale 1-5；anchors 1=混乱/3=基本一致/5=完全统一；threshold >= 4；证据：抽样审查

## Task 9: 统一 retrospective/ 目录文档 frontmatter

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 审查 `docs/retrospective/` 下所有非 index.md/log.md 文件的 frontmatter
  - 包含 patterns/ 和 reports/ 两个子目录
  - 模式文档（concepts/*.md）应有 `type: Pattern`
  - 复盘报告应有 `type: Retrospective` 或类似描述性类型
  - 确保字段完整
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-9.1: retrospective/ 下所有内容文档 frontmatter 含非空 type；证据：check-frontmatter.py

## Task 10: 统一 general/、topics/、refactor/ 目录文档 frontmatter

- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 审查 `docs/general/`、`docs/topics/`、`docs/refactor/` 下所有非 index.md/log.md 文件
  - general/ 和 topics/ 文件较少，主要是 references/readme.md
  - refactor/ 有一个概念文档
  - 确保 frontmatter 合规
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-10.1: 三个目录下所有内容文档 frontmatter 含非空 type；证据：check-frontmatter.py

## Task 11: 修复各级 toctree 完整性

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 4, Task 7, Task 8, Task 9, Task 10
- **Description**:
  - 运行 `check-toctrees.py` 识别所有 toctree 问题
  - 为每个含内容文档的目录确保 toctree 覆盖全部文档：
    - `docs/knowledge/index.md`: 当前 toctree 只列了 2 个条目，需补充所有子分类入口
    - `docs/knowledge/learning/03-agent-platforms-tools/README.md`: 确认是否在 toctree 中
    - 各 wiki bundle 的 index.md 确保 toctree 覆盖 concepts/examples/references
    - `docs/retrospective/index.md`: 确保 patterns 和 reports 入口完整
    - `docs/tech/index.md`: 已有较完整 toctree，验证即可
  - 确保 toctree 中引用的路径都存在（无断链）
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-11.1: `check-toctrees.py` 通过，0 个孤立文档，0 个断链；证据：脚本输出
  - `rubric` TR-11.2: toctree 组织逻辑清晰，学习路径合理；scale 1-5；threshold >= 4；证据：人工审查

## Task 12: 修复交叉引用断链

- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 11
- **Description**:
  - 扫描所有 Markdown 文件中的内部链接
  - 修复因目录结构变更导致的断链
  - 确保使用相对路径，无 `file:///` 绝对路径
  - 特别检查：
    - wiki 内部使用 `/concepts/xx.md` 等 bundle-relative 路径是否正确
    - 跨 bundle 链接路径是否正确
    - 指向 `.agents/`、`AGENTS.md` 等项目根目录的链接层级是否正确
- **Acceptance Criteria Addressed**: FR-10
- **Test Requirements**:
  - `rule` TR-12.1: Sphinx 构建无 unresolved reference 警告（suppress_warnings 中已排除的除外）；证据：构建日志
  - `rule` TR-12.2: 无 `file:///` 绝对路径；证据：Grep 搜索

## Task 13: 根 index.md 优化

- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 11
- **Description**:
  - 更新 `docs/index.md` 确保 toctree 覆盖五大板块入口
  - 确认徽章链接、文档导览表格等内容准确
  - 保持 `okf_version: "0.2"` frontmatter
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-13.1: 根 index.md toctree 包含 tech/knowledge/retrospective/general/topics 五个入口；证据：文件内容检查

## Task 14: Sphinx 构建验证

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1, Task 11, Task 12, Task 13
- **Description**:
  - 运行完整 Sphinx HTML 构建
  - 修复所有构建错误
  - 确认无新增警告
- **Acceptance Criteria Addressed**: AC-3, NFR-1
- **Test Requirements**:
  - `rule` TR-14.1: `sphinx-build -b html docs _build/html` 退出码 0；证据：命令输出
  - `rule` TR-14.2: 构建输出无 ERROR 级别消息；证据：构建日志审查

## Task 15: 质量门全量检查与最终验证

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 14
- **Description**:
  - 运行 `invoke gates.all` 执行全部质量门
  - UTF-8 编码检查
  - toctree 完整性检查
  - frontmatter 合规性检查
  - 修复所有发现的问题
  - 进行最终内容完整性抽样审查
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-15.1: `invoke gates.all` 全部通过；证据：命令输出
  - `rubric` TR-15.2: 内容完整性抽样审查；scale 1-5；anchors 1=发现正文丢失/3=正文完整/5=正文完整且格式规范；threshold >= 4；证据：抽样对比报告
