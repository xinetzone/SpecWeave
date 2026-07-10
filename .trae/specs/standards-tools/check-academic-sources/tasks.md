# Tasks

- [ ] Task 1: 创建脚本基础框架
  - [ ] SubTask 1.1: 创建 `check-academic-sources.py` 文件头部（shebang、docstring、sys.path设置）
  - [ ] SubTask 1.2: 导入依赖模块（argparse/json/re/sys/urllib/concurrent.futures/pathlib），复用 lib 中的 cli/markdown/project 模块
  - [ ] SubTask 1.3: 定义常量（DOI正则、arXiv正则、API端点、缓存配置、并发参数）
  - [ ] SubTask 1.4: 实现 CLI 参数解析（--path/--json 通用参数 + --no-cache/--timeout/--workers 特有参数）

- [ ] Task 2: 实现 L0 — DOI/arXiv ID 提取
  - [ ] SubTask 2.1: 编写 DOI 正则表达式，支持裸DOI、doi.org URL、dx.doi.org URL 三种格式
  - [ ] SubTask 2.2: 编写 arXiv ID 正则表达式，支持 arXiv:YYMM.NNNNN 和 arxiv.org/abs/ 两种格式
  - [ ] SubTask 2.3: 实现 `extract_identifiers_from_file(file_path)` 函数，返回文件中所有提取到的 DOI/arXiv ID 及其位置（行号）
  - [ ] SubTask 2.4: 实现 DOI 规范化函数（统一为 `10.xxxx/xxxx` 格式，去重）

- [ ] Task 3: 实现缓存机制
  - [ ] SubTask 3.1: 参照 check-links.py 缓存模式，实现 `load_cache()`/`save_cache()` 函数
  - [ ] SubTask 3.2: 缓存存储在 `.agents/cache/academic-sources-cache.json`，TTL 为 7 天
  - [ ] SubTask 3.3: 支持 `--no-cache` 参数强制跳过缓存

- [ ] Task 4: 实现 L1 — CrossRef API 客户端
  - [ ] SubTask 4.1: 实现 `query_crossref(doi)` 函数，使用 urllib.request 调用 `https://api.crossref.org/works/{doi}`
  - [ ] SubTask 4.2: 设置 User-Agent（参照 check-links.py 的 LINK_CHECK_USER_AGENT 模式）
  - [ ] SubTask 4.3: 处理 HTTP 200（有效DOI）、404（无效DOI）、超时、网络异常
  - [ ] SubTask 4.4: 实现并发请求（ThreadPoolExecutor，默认 3 个 worker）
  - [ ] SubTask 4.5: 从 CrossRef 响应中提取标题、作者（姓氏列表）、出版年份、期刊名

- [ ] Task 5: 实现 L2 — 元数据一致性比对
  - [ ] SubTask 5.1: 实现标题模糊匹配（归一化大小写/标点/空格后计算相似度，阈值 85%）
  - [ ] SubTask 5.2: 实现年份精确比对
  - [ ] SubTask 5.3: 实现第一作者姓氏比对（大小写不敏感）
  - [ ] SubTask 5.4: 从 Markdown 中提取当前文件记录的元数据（识别"作者"、"发表"、"年份"等字段模式）
  - [ ] SubTask 5.5: 当文档中无显式元数据时，标记为"info"级别而非错误

- [ ] Task 6: 实现报告输出
  - [ ] SubTask 6.1: 实现文本模式输出（按文件分组，使用 print_pass/print_warn/print_error）
  - [ ] SubTask 6.2: 实现 JSON 模式输出（结构化数据，含位置、状态、元数据快照、差异详情）
  - [ ] SubTask 6.3: 实现末尾汇总统计（pass/warn/error/skipped 计数）

- [ ] Task 7: 编写单元测试
  - [ ] SubTask 7.1: 创建 `tests/test_check_academic_sources.py`
  - [ ] SubTask 7.2: 测试 DOI/arXiv ID 正则提取（各种格式的测试用例）
  - [ ] SubTask 7.3: 测试 DOI 规范化函数
  - [ ] SubTask 7.4: 测试标题模糊匹配（完全一致/近似/不匹配三种情况）
  - [ ] SubTask 7.5: 使用 mock 数据测试 CrossRef API 响应解析（不发起真实网络请求）
  - [ ] SubTask 7.6: 测试缓存读写逻辑

- [ ] Task 8: 集成验证与收尾
  - [ ] SubTask 8.1: 运行 `python check-duplication.py` 确认无重复代码
  - [ ] SubTask 8.2: 在 first-principles 知识库目录上试运行脚本，验证结果合理性
  - [ ] SubTask 8.3: 运行单元测试确认全部通过
  - [ ] SubTask 8.4: 检查脚本头部 docstring 完整性和注释规范

# Task Dependencies

- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 1]
- [Task 4] depends on [Task 1, Task 3]
- [Task 5] depends on [Task 2, Task 4]
- [Task 6] depends on [Task 5]
- [Task 7] depends on [Task 2, Task 4, Task 5]（可并行编写测试用例）
- [Task 8] depends on [Task 6, Task 7]
