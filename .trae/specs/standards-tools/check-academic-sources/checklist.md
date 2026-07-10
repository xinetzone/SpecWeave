# Checklist

## 文件创建
- [ ] `.agents/scripts/check-academic-sources.py` 文件已创建
- [ ] 文件头部包含 shebang（`#!/usr/bin/env python3`）和 docstring 说明
- [ ] 文件头部包含标准 sys.path 设置（参照 lib/README.md 规范）
- [ ] 缓存目录 `.agents/cache/` 存在或可自动创建

## L0: DOI/arXiv ID 提取
- [ ] DOI 正则支持裸 DOI 格式（`10.xxxx/xxxx`）
- [ ] DOI 正则支持 `https://doi.org/10.xxxx/xxxx` URL 格式
- [ ] DOI 正则支持 `https://dx.doi.org/10.xxxx/xxxx` 旧版 URL 格式
- [ ] arXiv 正则支持 `arXiv:YYMM.NNNNN` 新版 ID 格式
- [ ] arXiv 正则支持 `arxiv.org/abs/YYMM.NNNNN` URL 格式
- [ ] DOI 规范化函数正确输出统一格式并去重
- [ ] 提取结果包含位置信息（文件名、行号）

## L1: CrossRef API 验证
- [ ] 使用 `urllib.request`（标准库），未引入 `requests` 依赖
- [ ] 有效 DOI 返回 200 时标记为 pass
- [ ] 无效 DOI 返回 404 时标记为 error
- [ ] 网络异常/超时时标记为 skipped（不中断整个扫描）
- [ ] 并发请求使用 ThreadPoolExecutor，默认 worker 数 ≤5
- [ ] 设置合理的 User-Agent
- [ ] HTTP 请求超时时间可配置（默认 10 秒）

## 缓存机制
- [ ] 缓存文件位于 `.agents/cache/academic-sources-cache.json`
- [ ] 缓存 TTL 为 7 天
- [ ] `--no-cache` 参数可强制跳过缓存
- [ ] 缓存命中时不发起网络请求

## L2: 元数据一致性比对
- [ ] 标题比对使用模糊匹配（归一化+相似度），阈值 85%
- [ ] 完全一致→pass
- [ ] 近似匹配（≥85%）→warn，输出文档标题 vs API 标题
- [ ] 不匹配（<85%）→error
- [ ] 年份精确匹配（数字比较）
- [ ] 第一作者姓氏比对（大小写不敏感）
- [ ] 文档中无显式元数据时标记为 info（不判定为错误）

## 输出报告
- [ ] 文本模式使用 print_pass/print_warn/print_error/print_summary 输出（与现有脚本风格一致）
- [ ] 结果按文件分组展示
- [ ] 末尾有汇总统计（pass/warn/error/skipped 计数）
- [ ] JSON 模式（--json）输出结构化数据
- [ ] JSON 输出包含：来源位置、DOI/arXiv ID、验证状态、API元数据、差异详情

## 只读原则
- [ ] 脚本不修改任何被扫描的 Markdown 文件
- [ ] 仅写入缓存文件（.agents/cache/ 目录）
- [ ] 不自动修复发现的问题
- [ ] 不实现引用计数功能（代理指标，违反第一性原理）
- [ ] 不输出可信度评级（A/B/C级）

## CLI 参数
- [ ] 支持 --path 参数指定扫描目录
- [ ] 支持 --json 参数启用 JSON 输出
- [ ] 支持 --no-cache 参数强制刷新
- [ ] 支持 --timeout 参数配置超时
- [ ] 支持 --workers 参数配置并发数
- [ ] 使用 add_common_args() 注册通用参数

## 共享库复用
- [ ] 使用 lib.cli 的 add_common_args 和输出函数
- [ ] 使用 lib.markdown.find_markdown_files 扫描文件
- [ ] 使用 lib.project.resolve_project_root 解析项目根目录
- [ ] 完成后通过 check-duplication.py 检查，无重复代码

## 单元测试
- [ ] 测试文件位于 `.agents/scripts/tests/test_check_academic_sources.py`
- [ ] DOI/arXiv 提取正则测试覆盖各种格式
- [ ] DOI 规范化函数测试
- [ ] 标题模糊匹配测试（完全一致/近似/不匹配）
- [ ] CrossRef API 解析测试使用 mock 数据（无真实网络请求）
- [ ] 缓存读写逻辑测试
- [ ] 所有测试通过

## 试运行验证
- [ ] 在 docs/knowledge/learning/first-principles/ 目录上试运行成功
- [ ] 能正确识别档案中已有的 DOI（如 Gentner 1983、Nickerson 1998 等）
- [ ] 输出结果合理（无大量误报）
