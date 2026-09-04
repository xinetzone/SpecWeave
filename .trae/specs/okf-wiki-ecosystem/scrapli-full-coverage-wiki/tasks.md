# Tasks

- [x] Task 1: R 阶段——未覆盖子文件夹事实采集（写入 scrapli-facts-2.md）
  - [x] SubTask 1.1: 阅读 `examples/cli/` 全部 12 个示例目录的 README.md + main.py，提取每示例的主题、所用 API、关键参数事实（F-001 起）
  - [x] SubTask 1.2: 阅读 `examples/netconf/` 4 个示例目录，提取 Netconf 操作用法事实
  - [x] SubTask 1.3: 阅读 `tests/`（functional/conftest.py + test_cli.py 结构、golden 文件组织规律、unit/dummy_ssh_server/main.go、unit/fixtures/），提取测试体系事实
  - [x] SubTask 1.4: 采样阅读 `scrapli/definitions/` 中 5-8 个代表性平台 YAML（cisco_nxos、juniper_junos、arista_eos、nokia_srlinux、huawei_vrp、mikrotik_routeros、fortinet_fortios、vyos_vyos），并统计 44 个 YAML 的共性字段，提取分类事实
  - [x] SubTask 1.5: 阅读 `docs/`（index.md、details.md、installation.md、migration.md、examples/python.md）与 `scrapli/lib/README.md`，提取安装矩阵、迁移映射、libscrapli 加载机制事实
  - [x] SubTask 1.6: 阅读 `.github/workflows/` 7 个工作流，提取 CI 检查矩阵事实（lint/test/docs/publish 等）
  - [x] SubTask 1.7: G1 质量门自检：全部事实无"用于/目的是/设计为"推断词，每条含源码路径

- [x] Task 2: I 阶段——新洞察提炼（写入 scrapli-insights-2.md）
  - [x] SubTask 2.1: 提炼 2-3 条洞察四元组（陈述+证据+反常识+行动），候选：golden 文件测试法与 TEST Transport 闭环、官方示例的渐进式主题矩阵、44 平台 YAML 分类学与钩子边界
  - [x] SubTask 2.2: G2 质量门自检：四元组完整，洞察基于 F-xxx 事实

- [x] Task 3: E 阶段——批量生成新文档（扩展现有 bundle，信源先行、每批 ≤7、index 最后写）
  - [x] SubTask 3.1: 更新 `references/scrapli-source.md`：追加子文件夹覆盖清单、新增事实数统计、示例/测试/CI 描述
  - [x] SubTask 3.2: 批次 1（2 篇）：生成 `concepts/09-testing-system.md`、`concepts/10-platform-catalog.md`
  - [x] SubTask 3.3: 批次 2（2 篇）：生成 `concepts/11-migration.md`、`concepts/12-repository-examples.md`
  - [x] SubTask 3.4: 批次 3（3 篇）：生成 `examples/proxy-jump.md`、`examples/output-parsing.md`、`examples/session-recorder.md`
  - [x] SubTask 3.5: 最后更新索引：`concepts/index.md`、`examples/index.md`、根 `index.md`（计数 14→21、更新信任说明）、`log.md`（追加 2026-08-28 扩展记录）

- [x] Task 4: V 阶段——独立验证与修复
  - [x] SubTask 4.1: Grep 验证：新文档中引用的每个类名/方法名/参数（Cli、Netconf、send_prompted_input、read_with_callbacks、TransportTestOptions、set_recording_path、forward_jump、preference 等）在 `external/libs/scrapli/scrapli/` 源码中存在；golden 文件名与测试文件名在 tests/ 中存在
  - [x] SubTask 4.2: 结构检查：7 篇新文档 frontmatter 完整（type/title/description/tags/generated/verified/status/stale_after/sources）、子目录 index.md 无 frontmatter、交叉链接 `/` 开头
  - [x] SubTask 4.3: 在 awesome-okf-xs 子项目运行 `invoke gates.toctrees` 验证 toctree 完整性（或等效人工检查：根 index.md toctree 覆盖新文档、无孤立文档）
  - [x] SubTask 4.4: 输出验证报告，逐一修复发现的问题，G4 质量门通过

- [x] Task 5: C 阶段——收尾沉淀
  - [x] SubTask 5.1: 确认 `log.md` 完整记录 R/I/E/V 各阶段数据（事实数、洞察数、文档数）
  - [x] SubTask 5.2: 勾选 tasks.md 与 checklist.md 全部条目，输出最终汇总

# Task Dependencies
- Task 1 → Task 2 → Task 3（顺序依赖：事实→洞察→生成）
- Task 3.1 必须先于 3.2-3.4 执行（信源先行）
- Task 3.5 必须最后执行（Index 最后写）
- Task 3 → Task 4 → Task 5（顺序依赖）
- SubTask 1.1-1.6 之间可并行委派（独立子文件夹）
