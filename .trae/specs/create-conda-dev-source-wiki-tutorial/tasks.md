# Tasks

## 任务总览

本 spec 采用七概念方法论「知识沉淀链路（R→I→E）」编排，分三阶段：
- **阶段 R（事实采集）**：Task 1 —— 系统学习两个文件夹，产出事实记录（内部，不单独成文档，直接驱动后续章节）
- **阶段 I（架构洞察）**：Task 2 —— 提炼分层架构与模块职责，形成 00/01 章节框架
- **阶段 E（萃取 wiki）**：Task 3 ~ Task 11 —— 原子化输出各章节 + 质量验证

- [x] Task 1: 事实采集——系统性学习 `conda` 与 `conda-docs` 两个文件夹结构、模块与文档
- [x] Task 2: 架构洞察——梳理 conda 分层架构与 conda-docs 文档架构
- [x] Task 3: 创建 `00-overview.md` 教程总览与导航索引
- [x] Task 4: 创建 `01-architecture.md` 整体架构
- [x] Task 5: 创建 `02-core-modules.md` 核心模块
- [x] Task 6: 创建 `03-cli-commands.md` CLI 命令层
- [x] Task 7: 创建 `04-gateways-plugins-env.md` 网关与扩展
- [x] Task 8: 创建 `05-key-apis.md` 关键 API
- [x] Task 9: 创建 `06-scenarios.md` 典型应用场景
- [x] Task 10: 创建 `07-faq.md` 常见问题
- [x] Task 11: 创建 `08-best-practices.md` 最佳实践
- [x] Task 12: 创建 `09-resources.md` 术语表与参考资料
- [x] Task 13: 创建 `README.md` 并统一质量验证

---

## 任务详细分解

### Task 1: 事实采集——系统性学习两个文件夹
- [x] Step 1.1: 枚举 `external/libs/conda-dev/conda` 的包目录（base/common/models/core/cli/gateways/plugins/env/notices/auxlib/shell/testing/_private）与根级模块
- [x] Step 1.2: 枚举 `external/libs/conda-dev/conda-docs` 的 `docs/source` 结构与关键文件（conf.py/index.rst/扩展）
- [x] Step 1.3: 逐包阅读 `__init__.py` 与关键模块头部 docstring，记录职责
- [x] Step 1.4: 阅读 `conda/api.py`/`resolve.py`/`exports.py`/`activate.py` 等根级入口
- [x] Step 1.5: 阅读 `conda-docs/docs/source/conf.py` 与 `_extensions/` 扩展
- **验证**: 已建立完整目录清单与模块职责映射（作为后续章节事实来源）

### Task 2: 架构洞察——梳理分层架构
- [x] Step 2.1: 归纳 conda 源码分层（base→common→models→core→gateways→cli→plugins）与依赖方向
- [x] Step 2.2: 归纳 conda-docs 文档站点架构（source/_static/_templates/扩展/用户指南/开发指南）
- [x] Step 2.3: 对比 `conda` 内嵌 `docs/` 与独立 `conda-docs` 的关系与差异
- [x] Step 2.4: 提炼关键设计意图（求解器抽象、虚拟包、插件 hookspec、cadapter 下载抽象）
- **验证**: 形成 00/01 章节的架构框架与 Mermaid 图草稿

### Task 3: 创建 `00-overview.md` 教程总览与导航索引
- [x] Step 3.1: 在 `.agents/docs/knowledge/learning/08-systems-infrastructure/conda-dev-source-wiki/` 下创建 `00-overview.md`
- [x] Step 3.2: 编写 YAML frontmatter（id/title/source/category/tags/date/status/author/summary）
- [x] Step 3.3: 编写教程引言（conda 源码学习价值 + 分层架构概览）
- [x] Step 3.4: 绘制 Mermaid 分层架构定位图
- [x] Step 3.5: 编写章节导航表（章节号 + 标题 + 内容摘要 + 文件链接）
- [x] Step 3.6: 编写目标读者说明（初学者/进阶/源码研究者三级）与阅读路径建议
- [x] Step 3.7: 关联 conda-dev-github-wiki
- **验证**: 文件 < 350 行；frontmatter 完整；含 Mermaid；链接相对路径

### Task 4: 创建 `01-architecture.md` 整体架构
- [x] Step 4.1: 创建文件并编写 frontmatter
- [x] Step 4.2: 编写 `conda` 源码完整目录树（11 包 + 根级模块），基于 Task 1 事实
- [x] Step 4.3: 编写分层依赖关系与 Mermaid 分层图
- [x] Step 4.4: 编写 `conda-docs` 目录树与构建架构
- [x] Step 4.5: 说明 `conda` 内嵌 `docs/` 与独立 `conda-docs` 关系/差异
- [x] Step 4.6: 添加底部双向导航
- **验证**: 文件 < 350 行；目录树与本地仓库一致；含 Mermaid

### Task 5: 创建 `02-core-modules.md` 核心模块
- [x] Step 5.1: 创建文件并编写 frontmatter
- [x] Step 5.2: 编写 `base`（constants/context）
- [x] Step 5.3: 编写 `common`（path/serialize/configuration/signals/toposort/url/compat）
- [x] Step 5.4: 编写 `models`（channel/match_spec/records/version/prefix_graph/package_info/dist/enums/environment）
- [x] Step 5.5: 编写 `core`（solve/index/link/prefix_data/subdir_data/package_cache_data/envs_manager/portability/path_actions）
- [x] Step 5.6: 编写根级模块（api/resolve/exports/activate/deprecations/exceptions/history/misc/utils/reporters）
- [x] Step 5.7: 添加底部双向导航
- **验证**: 文件 < 350 行；模块与本地仓库一致；关键符号准确

### Task 6: 创建 `03-cli-commands.md` CLI 命令层
- [x] Step 6.1: 创建文件并编写 frontmatter
- [x] Step 6.2: 编写 `cli/main.py` 入口、`conda_argparse.py`/`common.py`/`find_commands.py`/`condarc.py`
- [x] Step 6.3: 编写 `main_*.py` 命令分类（install/create/remove/list/search/update/env/*/config/info/clean/run/export/notices/package/compare/rename）
- [x] Step 6.4: 说明命令注册与分发流程（如何从 `conda <cmd>` 到对应 `main_<cmd>.py`）
- [x] Step 6.5: 说明 CLI 层与 `core`/`gateways` 的调用关系
- [x] Step 6.6: 添加底部双向导航
- **验证**: 文件 < 350 行；命令覆盖完整；分发流程准确

### Task 7: 创建 `04-gateways-plugins-env.md` 网关与扩展
- [x] Step 7.1: 创建文件并编写 frontmatter
- [x] Step 7.2: 编写 `gateways`（connection/adapters（http/ftp/s3/localfs）、download/session、disk、subprocess、repodata、shards、logging/streams）
- [x] Step 7.3: 编写 `plugins`（hookspec + manager + virtual_packages/subcommands/solvers/reporter_backends/package_extractors/prefix_data_loaders/post_solves）
- [x] Step 7.4: 编写 `env`（specs/installers/env.py/pip_util）
- [x] Step 7.5: 编写 `notices`、`auxlib`、`shell`
- [x] Step 7.6: 添加底部双向导航
- **验证**: 文件 < 350 行；覆盖全面；hookspec 说明准确

### Task 8: 创建 `05-key-apis.md` 关键 API
- [x] Step 8.1: 创建文件并编写 frontmatter
- [x] Step 8.2: 编写 `conda.api`（create/install/remove/update/Solver，含签名与示例）
- [x] Step 8.3: 编写 `MatchSpec`/`Channel`/`Version` 构造与匹配示例
- [x] Step 8.4: 编写 `PrefixData`/`SubdirData`/`PackageCacheData` 查询示例
- [x] Step 8.5: 编写 `Context` 配置读取、`History` 历史记录、`conda.exports` 重导出
- [x] Step 8.6: 编写 conda-docs Sphinx 扩展（`conda_umls.py`/`nav_glossary.py`）与 `conf.py` 要点
- [x] Step 8.7: 添加底部双向导航
- **验证**: 文件 < 350 行；签名与本地仓库一致；示例语言标注正确

### Task 9: 创建 `06-scenarios.md` 典型应用场景
- [x] Step 9.1: 创建文件并编写 frontmatter
- [x] Step 9.2: 编写场景①程序化环境创建与包安装
- [x] Step 9.3: 编写场景②MatchSpec 匹配与依赖解析
- [x] Step 9.4: 编写场景③SubdirData 与 solv 索引
- [x] Step 9.5: 编写场景④虚拟包与 CUDA/archspec 检测
- [x] Step 9.6: 编写场景⑤插件子命令开发（hookspec）
- [x] Step 9.7: 编写场景⑥conda-docs 本地构建与文档贡献
- [x] Step 9.8: 编写场景⑦channel/adapter 自定义下载
- [x] Step 9.9: 添加底部双向导航
- **验证**: 文件 < 350 行；每场景含背景/步骤/示例/预期结果

### Task 10: 创建 `07-faq.md` 常见问题
- [x] Step 10.1: 创建文件并编写 frontmatter
- [x] Step 10.2: 编写求解器冲突（Solver/unsatisfiable）
- [x] Step 10.3: 编写通道优先级与 channel_priority
- [x] Step 10.4: 编写 conda 与 pip 混用环境污染
- [x] Step 10.5: 编写代理与网络（ssl_verify/proxy_servers）
- [x] Step 10.6: 编写权限与文件锁
- [x] Step 10.7: 编写激活脚本失效、插件兼容、文档构建报错
- [x] Step 10.8: 添加底部双向导航
- **验证**: 文件 < 350 行；≥8 条问答；每条含现象/原因/解决

### Task 11: 创建 `08-best-practices.md` 最佳实践
- [x] Step 11.1: 创建文件并编写 frontmatter
- [x] Step 11.2: 编写环境管理最佳实践（命名/隔离/复现）
- [x] Step 11.3: 编写通道与求解器配置建议
- [x] Step 11.4: 编写程序化调用 conda API 的健壮性建议
- [x] Step 11.5: 编写插件开发规范
- [x] Step 11.6: 编写 conda 源码贡献规范（测试/类型/`news/` 片段）
- [x] Step 11.7: 编写 conda-docs 写作规范
- [x] Step 11.8: 编写 ≥3 个反模式与规避方式
- [x] Step 11.9: 添加底部双向导航
- **验证**: 文件 < 350 行；含 ≥3 反模式

### Task 12: 创建 `09-resources.md` 术语表与参考资料
- [x] Step 12.1: 创建文件并编写 frontmatter
- [x] Step 12.2: 编写术语表（≥15 条）
- [x] Step 12.3: 编写权威参考资料链接清单
- [x] Step 12.4: 编写按难度分级的扩展阅读建议
- [x] Step 12.5: 添加底部双向导航
- **验证**: 文件 < 350 行；术语 ≥15 条；含权威链接

### Task 13: 创建 `README.md` 并统一质量验证
- [x] Step 13.1: 创建 `README.md`（教程入口、章节列表、一句话说明）
- [x] Step 13.2: 所有原子文档 < 350 行（max/min 统计）
- [x] Step 13.3: 链接检查全部通过（无断链、无 file:/// 绝对路径）
- [x] Step 13.4: 所有文件 frontmatter 含 `source: "spec:create-conda-dev-source-wiki-tutorial"` 与 `category: "learning"`
- [x] Step 13.5: 01-08 文件底部三向导航完整且正确
- [x] Step 13.6: 模块/API 引用抽样核对（与本地仓库一致）
- [x] Step 13.7: 修复验证中发现的所有问题
- **验证**: 全部检查项通过

---

# Task Dependencies

- 执行顺序：阶段 R（Task 1）→ 阶段 I（Task 2）→ 阶段 E（Task 3-12 并行 + Task 13 质量验证）
- Task 1 是 Task 2 的事实基础；Task 2 是 Task 3/4 的框架基础
- Task 5-12 相互独立，可在 Task 2 完成后并行执行
- Task 13 依赖 Task 3-12 全部完成
- 所有章节内容必须以本地仓库 `external/libs/conda-dev/conda` 与 `conda-docs` 文件为事实来源，禁止臆造