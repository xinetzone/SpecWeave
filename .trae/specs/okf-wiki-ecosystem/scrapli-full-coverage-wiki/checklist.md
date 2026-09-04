# scrapli 全子文件夹覆盖 OKF Wiki 扩展 - 验证清单

## G1: R 阶段事实质量
- [x] `scrapli-facts-2.md` 存在且新增事实 ≥60 条（实际 109 条，F-001~F-109）
- [x] 全部事实无"用于"/"目的是"/"设计为"等因果推断词
- [x] 每条事实含源码文件路径（及行号或模块名）
- [x] 覆盖全部实质子文件夹：examples/cli（12 目录）、examples/netconf（4 目录）、tests/（functional+unit）、scrapli/definitions（采样 8 个 YAML + 44 个全集统计）、docs/、scrapli/lib/、.github/workflows/
- [x] examples/ 事实覆盖每个示例的主题与核心 API 调用
- [x] tests/ 事实覆盖 golden 文件组织规律与 dummy_ssh_server 角色

## G2: I 阶段洞察质量
- [x] `scrapli-insights-2.md` 含 2-3 条新洞察（实际 3 条）
- [x] 每条洞察四元组完整：陈述+证据+反常识+行动
- [x] 洞察引用具体 F-xxx 事实编号作为证据

## G3: E 阶段生成纪律
- [x] `references/scrapli-source.md` 先于新概念/示例文档更新（信源先行）
- [x] 每批生成 ≤7 个文档（分 3 批并行委派：2+2+3）
- [x] 新文档 frontmatter 完整：type（Concept/Example）、title、description、tags、generated（by/at）、verified（process:seven-concepts-v）、status: stable、stale_after: 2027-06-30、sources 指向 /references/scrapli-source.md
- [x] 新概念文档编号衔接现有序列（09/10/11/12）
- [x] 新示例文档命名 kebab-case 纯英文，正文中文
- [x] 各级 index.md 在所有内容文档定稿后最后更新

## G4: V 阶段 API 真实性（Grep 验证）
- [x] 新文档中每个类名在 `external/libs/scrapli/scrapli/` 中 Grep 命中（Cli、Netconf、AuthOptions、SessionOptions、TransportTestOptions、ReadCallback、LoadedDefinition 等 14 个全部命中）
- [x] 新文档中每个方法名 Grep 命中（send_input、send_inputs、send_prompted_input、read_with_callbacks、get_prompt、enter_mode、raw_rpc、get_config、edit_config、commit、lock 等 29 个全部命中，含行号）
- [x] 示例文档中的会话录制/proxy jump 相关 API 经源码验证（recorder_path ✅ session.py:44；proxy_jump_* 7 参数 ✅ transport.py:242-248；textfsm_parse 签名 ✅ cli_result.py:318-323；官方示例文件真实存在）
- [x] `concepts/10-platform-catalog.md` 中平台 YAML 数量 = 44（逐文件核对，43 平台 + default = 44）
- [x] `concepts/11-migration.md` 中旧版类名（Scrapli/AsyncScrapli/NetworkDriver）明确标注为旧版 API，新版映射（Cli/Netconf）Grep 验证存在
- [x] golden 文件名/测试文件名（test_cli.py、dummy_ssh_server/main.go 等）真实存在于 tests/（V 阶段发现 1 处事实错误已修复：get-next-notification 等目录位于 fixtures/ 而非 golden/）

## 结构与链接
- [x] 子目录 index.md（concepts/examples/references）无 frontmatter
- [x] 根 index.md 保留 `okf_version: "0.2"`，文档计数更新为 21（13 概念 + 7 示例 + 1 信源）
- [x] 新文档交叉链接使用 `/` 开头 bundle-relative 路径（无 `../`）
- [x] 新文档结尾含"相关概念"章节
- [x] 代码块标注语言（python/bash/yaml；09 的目录树补标 text）
- [x] toctree 完整：根 index.md 的 toctree 覆盖全部新文档，concepts/examples index.md toctree 全覆盖、无断链、无孤立文档（等效检查通过）

## log.md 与收尾
- [x] log.md 追加 2026-08-28 扩展记录：R/I/E/V 各阶段完成情况、新增事实数/洞察数/文档数
- [x] 现有 14 篇文档未被修改（git status 确认：仅新增 7 篇 + 更新 5 个索引/信源/日志文件）
- [x] 无残留占位符或 TODO

## 内容质量（V 阶段对抗审查）
- [x] 09-testing-system：准确描述 golden 文件测试法与 TEST Transport 关系（fixtures/golden 对应机制经事实修正后与源码一致）
- [x] 10-platform-catalog：44 平台分类逻辑清晰，YAML 共性结构说明与采样事实一致
- [x] 11-migration：迁移映射与 docs/migration.md 源码一致，未虚构旧版 API 逐条映射表
- [x] 12-repository-examples：16 个示例目录全部提及且主题归纳准确
- [x] 3 篇新示例文档代码基于官方示例改写，与 facts 一致（行号级核验通过）
- [x] 中文表达流畅，与现有 14 篇文档风格一致
