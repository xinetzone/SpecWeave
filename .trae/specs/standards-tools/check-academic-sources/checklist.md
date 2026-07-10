# Checklist

## 文件创建
- [x] `.agents/scripts/check-academic-sources.py` 文件已创建
- [x] 文件头部包含 shebang（`#!/usr/bin/env python3`）和 docstring 说明
- [x] 文件头部包含标准 sys.path 设置（参照 lib/README.md 规范）
- [x] 缓存目录 `.agents/cache/` 存在或可自动创建（mkdir(parents=True, exist_ok=True)）

## L0: DOI/arXiv ID 提取
- [x] DOI 正则支持裸 DOI 格式（`10.xxxx/xxxx`）
- [x] DOI 正则支持 `https://doi.org/10.xxxx/xxxx` URL 格式
- [x] DOI 正则支持 `https://dx.doi.org/10.xxxx/xxxx` 旧版 URL 格式
- [x] arXiv 正则支持 `arXiv:YYMM.NNNNN` 新版 ID 格式
- [x] arXiv 正则支持 `arxiv.org/abs/YYMM.NNNNN` URL 格式
- [x] arXiv 正则支持旧版 `arXiv:hep-th/XXXXXXX` 格式
- [x] DOI 规范化函数正确输出统一格式并去重（去除尾部 `)`, `;`, `,`, `.`）
- [x] 提取结果包含位置信息（文件名、行号）

## L1: CrossRef API 验证
- [x] 使用 `urllib.request`（标准库），未引入 `requests` 依赖
- [x] 有效 DOI 返回 200 时标记为 pass
- [x] 无效 DOI 返回 404 时标记为 error
- [x] 网络异常/超时时标记为 skipped（不中断整个扫描）
- [x] 并发请求使用 ThreadPoolExecutor，默认 worker 数 3（≤5）
- [x] 设置合理的 User-Agent（AcademicSourceChecker/1.0）
- [x] HTTP 请求超时时间可配置（默认 10 秒）

## 缓存机制
- [x] 缓存文件位于 `.agents/cache/academic-sources-cache.json`
- [x] 缓存 TTL 为 7 天
- [x] `--no-cache` 参数可强制跳过缓存
- [x] 缓存命中时不发起网络请求

## L2: 元数据一致性比对
- [x] 标题比对使用模糊匹配（SequenceMatcher归一化+相似度），阈值 85%
- [x] 完全一致→pass
- [x] 近似匹配（≥85%）→warn，输出文档标题 vs API 标题
- [x] 不匹配（<85%）→error
- [x] 年份精确匹配（数字比较）
- [x] 第一作者姓氏比对（大小写不敏感）
- [x] 文档中无显式元数据时标记为 info（不判定为错误）
- [x] 同句多篇论文引用时年份不匹配标记为warn（非error）
- [x] 年份提取优先使用DOI前括号内模式 `(YYYY)...DOI:`

## 输出报告
- [x] 文本模式使用 print_pass/print_warn/print_error/print_summary 输出（与现有脚本风格一致）
- [x] 结果按文件分组展示
- [x] 末尾有汇总统计（pass/warn/error/skipped 计数）
- [x] JSON 模式（--json）输出结构化数据
- [x] JSON 输出包含：来源位置、DOI/arXiv ID、验证状态、API元数据、差异详情

## 只读原则
- [x] 脚本不修改任何被扫描的 Markdown 文件
- [x] 仅写入缓存文件（.agents/cache/ 目录）
- [x] 不自动修复发现的问题
- [x] 不实现引用计数功能（代理指标，违反第一性原理）
- [x] 不输出可信度评级（A/B/C级）

## CLI 参数
- [x] 支持 --path 参数指定扫描目录
- [x] 支持 --json 参数启用 JSON 输出
- [x] 支持 --no-cache 参数强制刷新
- [x] 支持 --timeout 参数配置超时
- [x] 支持 --workers 参数配置并发数
- [x] 使用 add_common_args() 注册通用参数

## 共享库复用
- [x] 使用 lib.cli 的 add_common_args 和输出函数
- [x] 使用 lib.markdown.find_markdown_files 扫描文件
- [x] 使用 lib.project.resolve_project_root 解析项目根目录
- [x] 缓存读写模式参照 check-links.py 既有模式

## 单元测试
- [x] 测试文件位于 `.agents/scripts/tests/test_check_academic_sources.py`
- [x] DOI/arXiv 提取正则测试覆盖各种格式（11个ID提取测试）
- [x] DOI 规范化函数测试（7个测试：裸DOI、URL、旧URL、尾部标点、大小写）
- [x] 标题模糊匹配测试（完全一致/近似/不匹配，6个测试）
- [x] CrossRef API 解析测试使用 mock 数据（无真实网络请求，3个测试）
- [x] 缓存读写逻辑测试（5个测试：不存在、存/取、新鲜/过期、缺日期）
- [x] 元数据比对测试（年份匹配/不匹配/缺失、作者匹配、标题匹配，6个测试）
- [x] arXiv验证测试（3个测试：新格式、旧格式、版本号）
- [x] 文档元数据提取测试（3个测试）
- [x] 所有测试通过（41/41 passed in 0.46s）

## 试运行验证
- [x] 在 docs/knowledge/learning/first-principles/ 目录上试运行成功
- [x] 能正确识别档案中已有的 DOI（15个DOI + 1个arXiv = 16个学术ID）
- [x] 输出结果合理（12通过、3警告、1错误，错误为1980年老DOI未在CrossRef注册）
