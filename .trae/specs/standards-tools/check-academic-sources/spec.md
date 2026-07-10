# 学术来源自动化验证脚本 Spec

## Why

当前第一性原理知识档案（[docs/knowledge/learning/first-principles/](file:///d:/AI/docs/knowledge/learning/first-principles/)）包含 92 个引用来源，其中约 12 个是有 DOI 或 arXiv ID 的学术论文/预印本。学术来源的元数据（DOI 是否存在、作者/年份/标题是否准确、论文是否被撤稿）是来源可信度评级的"地基"。

当前这些元数据依赖人工逐个点击 DOI 链接肉眼比对，存在三个问题：
1. **效率低**：新增一篇论文需人工验证 3-5 分钟
2. **易遗漏**：撤稿/修正信息无法通过简单链接检查发现
3. **不可重复**：人工验证结果没有机器可读的记录，无法集成到 CI 流水线

需要开发一个自动化验证脚本，通过 CrossRef 和 arXiv API 自动验证学术来源的元数据一致性，但**严格限定自动化边界**——只验证可客观判定的事实性元数据，不做引用计数（代理指标陷阱），不做可信度评级（需领域判断），不自动修改文件内容（避免意外写入）。

## What Changes

- 新增 `check-academic-sources.py` 脚本，位于 `.agents/scripts/` 目录
- 核心功能分四层（L0-L3），MVP 实现 L0+L1+L2：
  - **L0：DOI/arXiv ID 提取与格式校验**（无网络，100% 自动）
  - **L1：DOI 存在性验证**（CrossRef API，带缓存，验证 DOI 是否有效）
  - **L2：元数据一致性比对**（比对标题/作者/年份，模糊匹配，标记差异供人工确认）
  - **L3：撤稿/修正检测**（CrossRef Crossmark，P2 优先级，MVP 后迭代）
- 不实现：引用计数抓取（违反第一性原理，引用量≠质量）、arXiv 期刊发表版本追踪、自动修复
- 复用现有基础设施：`lib/cli.py` CLI 框架、`lib/markdown.py` Markdown 扫描、`check-links.py` 的缓存/并发/超时模式
- 遵循 [lib/README.md](file:///d:/AI/.agents/scripts/lib/README.md) 新增脚本开发流程

## Impact

- Affected specs: 无既有 spec 受影响，属新增工具
- Affected code:
  - 新增文件：`.agents/scripts/check-academic-sources.py`
  - 可能新增：`.agents/scripts/lib/academic_sources/` 模块目录（如逻辑超过 200 行，按共享库引力定律提取）
  - 新增缓存：`.agents/cache/academic-sources-cache.json`（参照外部链接缓存模式）
  - 新增测试：`.agents/scripts/tests/test_check_academic_sources.py`
  - 可选集成：`.agents/scripts/ci-check.sh/ps1` 中加入学术来源检查步骤
- 不修改任何知识档案文件（只读检查工具）

## ADDED Requirements

### Requirement: DOI 与 arXiv ID 提取

脚本 SHALL 能够从 Markdown 文件中自动提取 DOI 和 arXiv ID，支持多种格式。

#### Scenario: 提取多种 DOI 格式

- **WHEN** 扫描 Markdown 文件中的 DOI 引用
- **THEN** 能识别以下格式：
  - 裸 DOI：`10.1207/s15516709cog0702_3`
  - DOI 链接：`https://doi.org/10.1207/s15516709cog0702_3`
  - 旧版 DOI 链接：`https://dx.doi.org/10.1207/...`
  - 标记为 DOI 字段后的链接
- **AND** 提取结果规范化为标准 DOI 格式（`10.xxxx/xxxx`），去重

#### Scenario: 提取 arXiv ID

- **WHEN** 扫描 Markdown 文件中的 arXiv 引用
- **THEN** 能识别 `arXiv:YYYY.NNNNN`（新版）和 `arXiv:XXXX.YYYY`（旧版）格式
- **AND** 支持从 `arxiv.org/abs/YYYY.NNNNN` URL 中提取 ID

### Requirement: DOI 存在性验证（L1）

脚本 SHALL 通过 CrossRef API 验证 DOI 是否存在。

#### Scenario: 有效 DOI 返回元数据

- **WHEN** 查询一个有效的 DOI（如 `10.1207/s15516709cog0702_3`）
- **THEN** CrossRef API 返回 HTTP 200 及论文元数据（标题、作者、期刊、年份）
- **AND** 脚本标记该 DOI 为"✅ 存在"

#### Scenario: 无效 DOI 返回 404

- **WHEN** 查询一个不存在的 DOI
- **THEN** CrossRef API 返回 HTTP 404
- **AND** 脚本标记该 DOI 为"❌ 不存在"，输出到错误报告

#### Scenario: 网络异常优雅降级

- **WHEN** 网络不可用或 API 请求超时
- **THEN** 脚本标记该 DOI 为"⚠️ 验证跳过（网络异常）"
- **AND** 使用缓存结果（如有），缓存 TTL 7 天
- **AND** 不因单个请求失败而中断整个扫描过程

#### Scenario: 请求缓存避免重复调用

- **WHEN** 同一 DOI 在 7 天内被多次验证
- **THEN** 使用本地缓存结果，不重复发起 API 请求
- **AND** 缓存存储在 `.agents/cache/academic-sources-cache.json`
- **AND** 支持 `--no-cache` 参数强制刷新

### Requirement: 元数据一致性比对（L2）

脚本 SHALL 将 CrossRef/arXiv 返回的元数据与文档中记录的信息进行比对，标记不一致项。

#### Scenario: 标题模糊匹配

- **WHEN** CrossRef 返回的标题与文档中记录的标题进行比对
- **THEN** 使用模糊匹配（归一化大小写、标点、空格后比较）
- **AND** 完全一致→"✅ 标题匹配"
- **AND** 模糊匹配（相似度≥85%）→"⚠️ 标题近似，建议人工确认"（输出文档标题 vs API 返回标题）
- **AND** 不匹配（相似度<85%）→"❌ 标题不一致"

#### Scenario: 作者与年份比对

- **WHEN** 比对作者和出版年份
- **THEN** 年份精确匹配（数字比较）
- **AND** 作者比对第一作者姓氏（大小写不敏感）
- **AND** 期刊/出版物名称模糊匹配

#### Scenario: 元数据缺失时的处理

- **WHEN** 文档中没有显式记录作者/年份/标题（仅有 DOI 链接）
- **THEN** 标记为"ℹ️ 元数据缺失，可从 API 补充"
- **AND** 不判定为错误（不强制要求文档显式记录所有元数据）

### Requirement: 输出报告

脚本 SHALL 输出结构化验证报告，不自动修改任何文件。

#### Scenario: 文本模式输出

- **WHEN** 以默认文本模式运行
- **THEN** 输出格式与现有检查脚本一致：
  - 使用 `print_pass`/`print_warn`/`print_error`/`print_summary` 输出
  - 按文件分组显示结果
  - 末尾汇总统计（通过/警告/错误/跳过数量）

#### Scenario: JSON 模式输出

- **WHEN** 使用 `--json` 参数运行
- **THEN** 输出机器可读的 JSON，包含每个来源的：
  - 来源位置（文件、行号）
  - 提取的 DOI/arXiv ID
  - 验证状态（pass/warn/error/skipped）
  - API 返回的元数据快照
  - 差异详情（如有）

#### Scenario: 只读原则

- **WHEN** 脚本执行任何操作
- **THEN** 不修改任何被扫描的 Markdown 文件
- **AND** 仅写入缓存文件（`.agents/cache/` 目录）
- **AND** 输出报告到 stdout（不写入结果文件，除非指定 `--output` 参数）

### Requirement: 技术实现规范

脚本 SHALL 遵循项目现有脚本开发规范。

#### Scenario: 标准库优先，不引入新依赖

- **WHEN** 实现 HTTP 请求
- **THEN** 使用 `urllib.request`（与 check-links.py 一致），不引入 `requests` 第三方库
- **AND** 使用 `concurrent.futures.ThreadPoolExecutor` 实现并发请求
- **AND** 并发数限制为 ≤5（避免触发 API 速率限制）

#### Scenario: CLI 参数规范

- **WHEN** 脚本启动
- **THEN** 支持以下通用参数（通过 `add_common_args`）：
  - `--path`：指定扫描目录（默认项目根目录）
  - `--json`：JSON 输出模式
- **AND** 支持脚本特有参数：
  - `--no-cache`：跳过缓存，强制刷新
  - `--timeout`：HTTP 请求超时（默认 10 秒）
  - `--workers`：并发线程数（默认 3）

#### Scenario: 共享库复用

- **WHEN** 编写脚本
- **THEN** 复用以下共享模块：
  - `lib.cli.add_common_args` / `print_pass` / `print_warn` / `print_error` / `print_summary`
  - `lib.markdown.find_markdown_files`
  - `lib.project.resolve_project_root`
- **AND** 脚本头部添加标准 sys.path 设置
- **AND** 完成后运行 `python check-duplication.py` 检查重复代码

### Requirement: 排除项（明确不做）

脚本 SHALL NOT 实现以下功能，避免范围蔓延和第一性原理违背。

#### Scenario: 不做引用计数

- **WHEN** 设计脚本功能
- **THEN** 不抓取或展示引用次数
- **BECAUSE** 引用计数是代理指标（proxy metric），高引用≠高质量，违反第一性原理"从基本事实出发"原则
- **AND** 不同数据库引用数差异大（Google Scholar > Scopus > CrossRef），制造伪精确

#### Scenario: 不自动修复文件

- **WHEN** 发现元数据不一致
- **THEN** 只输出报告标记问题，不自动修改 Markdown 文件
- **BECAUSE** 元数据修复需要人工判断（如：API 返回的作者名缩写与文档中的全名是否等价）

#### Scenario: 不做可信度评级

- **WHEN** 验证完成
- **THEN** 不输出 A/B/C 级评级
- **BECAUSE** 可信度评级需要领域知识、语境判断、利益冲突识别，超出自动化边界

### Requirement: MVP 范围限定

MVP 版本 SHALL 严格限定实现范围。

#### Scenario: MVP 包含的功能

- **WHEN** 交付 MVP
- **THEN** 包含：
  - L0：DOI/arXiv ID 提取（支持多种格式）
  - L1：DOI 存在性验证（CrossRef API + 缓存 + 并发 + 优雅降级）
  - L2：元数据一致性比对（标题模糊匹配 + 年份精确匹配 + 第一作者姓氏匹配）
  - 文本报告 + JSON 报告
  - 单元测试（使用 mock 数据，不依赖真实 API）

#### Scenario: MVP 不包含的功能（后续迭代）

- **WHEN** 规划 MVP 范围
- **THEN** 不包含：
  - arXiv API 集成（L1 中 arXiv ID 仅做格式校验，不查 API）
  - L3 撤稿检测（需 Crossmark 或 Retraction Watch API）
  - ISBN/Open Library 书籍验证
  - CI 集成
  - 自动修复建议
