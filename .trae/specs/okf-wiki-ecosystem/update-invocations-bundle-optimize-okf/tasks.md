# Tasks

## 阶段 1：源头复基线（source-code-to-okf-wiki R 阶段）
- [ ] Task 1: 读取 vendor 源码事实采集
  - [ ] SubTask 1.1: 确认版本（pyproject.toml = 4.1.0）与真实顶层模块清单
  - [ ] SubTask 1.2: 逐模块记录真实文件（`__init__/autodoc/checks/ci/console/docs/environment/pytest/testing/util/watch` + `packaging/(release|semantic_version_monkey|vendorize)`），确认**无** `packaging/version.py`
  - [ ] SubTask 1.3: 记录各模块主要 task 函数签名/默认参数与工具函数、`ns` Collection 结构、`ns.configure()` 配置键
  - [ ] SubTask 1.4: 将事实写入 spec 目录 `facts.md`（零推测，标注源码路径）

## 阶段 2：对抗性审查既有 bundle（I + V 阶段）
- [ ] Task 2: 逐文件对账 bundle 内容与真实源码
  - [ ] SubTask 2.1: 遍历全部 22 文件，收集所有引用的模块名/任务名/参数/配置键
  - [ ] SubTask 2.2: Grep 验证每个引用在 vendor 源码中的存在性
  - [ ] SubTask 2.3: 定位漂移项（`packaging/version.py`、模块清单 16→实际、`tasks.py` 归属等）
  - [ ] SubTask 2.4: 产出对抗性审查报告（写入 spec 目录 `review-report.md`），含「确定性漂移/疑似漂移/无问题」分类

## 阶段 3：更新 bundle（E 阶段）
- [ ] Task 3: 修正 references/invocations-source.md
  - [ ] SubTask 3.1: 按真实模块清单修正「模块清单」表
  - [ ] SubTask 3.2: 新增指向本地 vendor 源码路径的信源条目
  - [ ] SubTask 3.3: 更新版本/核心约定描述（如需要）
- [ ] Task 4: 修正受影响 concepts/examples
  - [ ] SubTask 4.1: 定位并修正引用 `packaging/version.py` 的文档
  - [ ] SubTask 4.2: 修正确认有误的任务名/参数/配置键
  - [ ] SubTask 4.3: 更新受影响文档的 `verified` 字段（`process:source-code-to-okf-wiki-v`，当前日期）
- [ ] Task 5: 更新 log.md
  - [ ] SubTask 5.1: 追加对抗性审查与更新记录（日期、漂移项、修复摘要）

## 阶段 4：项目优化（invocations 封装，为 awesome-okf-xs）
- [ ] Task 6: 引入 invoke/invocations 任务化
  - [ ] SubTask 6.1: 新增 `tasks.py`，用 `invocations` Collection 封装 `build`/`clean`（复用 Sphinx 构建命令）
  - [ ] SubTask 6.2: 在 `pyproject.toml` `[project.optional-dependencies].doc` 增加 `invoke`（按需 `invocations`）
  - [ ] SubTask 6.3: CI `pages.yml` 改用任务化命令入口（如 `invoke build`）
- [ ] Task 7: 本地验证
  - [ ] SubTask 7.1: 安装依赖后运行 `invoke build` 产出 `_build/html`
  - [ ] SubTask 7.2: 运行 `invoke clean` 验证清理生效

## 阶段 5：验证与模式沉淀（checklist 系统性验证 + C 阶段）
- [ ] Task 8: 按 checklist.md 逐条验证全部检查点
- [ ] Task 9: C 阶段模式沉淀——将「源码→OKF 对抗性更新」「invocations Collection 封装 Sphinx 构建」两组模式写入 patterns 目录，含触发场景/核心步骤/反模式/迁移验证

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3][Task 4][Task 5] depend on [Task 2]
- [Task 6] 独立于 [Task 1-5]，可与 [阶段2-3] 并行
- [Task 8] depends on [Task 3-7]
- [Task 9] depends on [Task 8]