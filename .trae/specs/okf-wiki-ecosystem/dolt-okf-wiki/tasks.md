# Dolt 博文 → OKF 知识包 - 实施计划

> 方法论编排：seven-concepts-cmd 场景 4（知识沉淀），链路 R→I→E→V→C，对齐 blog-article-to-okf-wiki 七阶段工作流。
> 质量门：G1 事实无因果词 → G2 洞察四元组 → G3 结构可迁移/信源先行 → G4 行动项原子化；F 后强制 V（本任务 V 为独立阶段）。

## Task 1: R-1 博文全文提取（browser_use）

- **Status**：`pending`
- **Priority**：high
- **Depends On**：None
- **Description**：
  - 用 browser_use 子代理打开 `https://mp.weixin.qq.com/s/ES_KncqKLiQxIzaEZ-58gg?bar_style_type=2&from=industrynews&color_scheme=light#rd`，JS 取 `#js_content` innerText 全文
  - 核对正文长度（<500 字判定取错节点，重取）；记录标题、公众号、发布时间、原文 URL
  - 全文保存至 spec 工作区 `.trae/specs/okf-wiki-ecosystem/dolt-okf-wiki/article-source-raw.md`（工作文件，不提交 bundle）
- **Acceptance Criteria Addressed**：FR-1
- **Test Requirements**：
  - `rule` TR-1.1：article-source-raw.md 存在且正文 >2000 字，含博文标题与核心章节（功能/安装/限制等）；证据：文件字数与标题行
  - `rule` TR-1.2：发布时间、公众号名、URL 三项元信息齐备；证据：文件头部元信息表
- **Notes**：微信反爬确定性拦截 WebFetch，直接 browser_use，不浪费轮次

## Task 2: R-2 F 编号事实采集（博文事实层）

- **Status**：`pending`
- **Priority**：high
- **Depends On**：Task 1
- **Description**：
  - 通读全文，F-001 起编号登记全部事实性声明至 spec `facts.md`：元信息、产品定位、功能特性（行级历史/分支合并/MySQL 兼容/Workbench/MCP 等）、数字（Stars、性能、阈值、端口）、命令与安装步骤、限制条件、产品矩阵
  - 作者观点/判断显式标注"作者观点"；作者转述的官方数据标注"博文转述官方口径"
  - G1 质量门：事实句纯客观描述，无"因为/导致/所以"因果推断词
  - 信源距离预判：每条标注距离级（博文=③第三方综述；厂商自宣成效数字标 P0）
- **Acceptance Criteria Addressed**：FR-2、FR-3、AC-2、AC-4
- **Test Requirements**：
  - `rule` TR-2.1：facts.md 事实表覆盖博文全部数字/产品名/命令/日期（对照原文逐节勾选）；证据：coverage 勾选记录
  - `rule` TR-2.2：事实句无因果推断词（G1）；证据：Grep `因为|导致|所以|因此` 事实表无命中（观点区除外）
  - `rule` TR-2.3：P0 候选清单（数字/日期/官方表态/成效数字）已显式列出；证据：facts.md P0 清单节

## Task 3: R-3 P0 权威核验与勘误四清单

- **Status**：`pending`
- **Priority**：high
- **Depends On**：Task 2
- **Description**：
  - 对 P0 清单逐项 WebSearch + 官方源核验：github.com/dolthub/dolt（Stars/LICENSE/README）、docs.doltdb.com（MySQL 兼容/端口/CLI/限制）、dolthub.com 官方博客（TPC-C 性能口径、产品矩阵 DoltHub/DoltLab/Hosted Dolt、MCP Server）
  - 过勘误四张清单：①日期/版本表 ②成效数字溯源表 ③口径对照表（Stars 时点、地域/统计限定词）④引文逐字核对表
  - 核验补充事实续编 F 编号（接博文事实编号之后）；每项给出 ✅/⚠️/❌ + 信源 URL + 摘录
  - 无法核验项标"仅博文单源"，禁止硬编 URL；核心声明 ❌ → 预判 flagged
  - 核验可委派 general_purpose_task 子代理（独立上下文，每项给完整声明内容+博文口径+要求官方源）
- **Acceptance Criteria Addressed**：FR-4、FR-5、AC-3、AC-8
- **Test Requirements**：
  - `rule` TR-3.1：P0 项 100% 有核验结论（✅/⚠️/❌）与实际访问过的信源 URL；证据：verification 初稿表（先落 facts.md 核验节，E 阶段转入 bundle）
  - `rule` TR-3.2：勘误四清单各表存在，❌/⚠️ 项有正确值与差异说明；证据：四张清单表
  - `rubric` TR-3.3：核验充分性；scale 1-5；anchors 1=只搜官网首页敷衍/3=核心数字有官方源但边缘项漏检/5=P0 全项多源交叉、口径限定词核对到位；threshold >= 4；证据：核验记录

## Task 4: I-1 骨架判定与三层知识拆分

- **Status**：`pending`
- **Priority**：high
- **Depends On**：Task 3
- **Description**：
  - 操作可复现性两问：①博文有读者可照做的安装/配置/代码/调用流程？②经作者实测、有版本/输入输出/步骤顺序？两问皆"是"才设 examples/；结论与理由写入 facts.md
  - 归属判定复核：主线实体 Dolt → `jishu/data/dolt/`（候选位置对照表论证：data vs dev）
  - 三层知识拆分定稿：
    - concepts/00 发布事实层：Dolt 定位、公司/开源协议、Stars 时点、产品矩阵（Dolt/DoltHub/DoltLab/Hosted Dolt）、博文信息结构分析
    - concepts/01 机制原理层：行级版本控制、分支/合并/冲突、Git 概念映射、MySQL 协议兼容、存储引擎（仅官方源口径）
    - concepts/02 工作流与 AI 时代用法：CLI/SQL 工作流、Workbench、MCP Server、AI Agent 安全操作沙箱
    - concepts/03 边界与趋势：性能限制与适用边界、适用/不适用场景、数据库版本控制行业趋势、选型启示（洞察四元组：现象+根因+影响+建议，G2）
  - G2 质量门：洞察层含四元组；观点与事实分层
- **Acceptance Criteria Addressed**：FR-6、FR-7、AC-7、AC-10
- **Test Requirements**：
  - `rule` TR-4.1：两问答案有明确"是/否"+证据（博文段落/命令有无版本输出），examples/ 取舍与答案一致；证据：facts.md 骨架判定节
  - `rule` TR-4.2：concepts 篇目清单（≥3 篇）与三层映射表确定；证据：spec/facts 中篇目规划
  - `rubric` TR-4.3：洞察四元组完整性（现象/根因/影响/建议）与观点-事实分层；scale 1-5；anchors 1=观点当事实/3=有分层但洞察浅/5=四元组完整且趋势分析有增量；threshold >= 4；证据：03 篇提纲

## Task 5: E-1 信源先行生成 references/

- **Status**：`pending`
- **Priority**：high
- **Depends On**：Task 4
- **Description**：
  - 创建 `projects/awesome-okf-xs/doc/bundles/jishu/data/dolt/` 目录
  - 写 `references/article-source.md`：博文信息表、信源距离分级、F 编号事实双份登记（与 facts.md 集合一致，博文事实+核验补充分组呈现）
  - 写 `references/verification.md`：P0 核验报告、勘误四张清单、信源 URL 清单、flagged/stable 建议
  - 写 `references/index.md`：无 frontmatter，含 toctree 块收录 article-source、verification
- **Acceptance Criteria Addressed**：FR-8、FR-9、AC-1、AC-2、AC-3
- **Test Requirements**：
  - `rule` TR-5.1：article-source.md 的 F 编号集合与 spec facts.md 正则比对相等、连续；证据：双份比对输出
  - `rule` TR-5.2：references/index.md 含 toctree 且条目文件存在；证据：文件清单
  - `rule` TR-5.3：两文件 frontmatter 合规（type: Reference 等）；证据：frontmatter 摘录

## Task 6: E-2 生成 concepts/ 与根 index/log

- **Status**：`pending`
- **Priority**：high
- **Depends On**：Task 5
- **Description**：
  - 写 concepts/00~03（按 Task 4 拆分）：所有数字/版本/产品名引用 F 编号；作者观点标"作者观点"、编辑者洞察标"编者分析"；伪代码/推导标"非官方"；Mermaid 图（如 Git-Dolt 概念映射、产品矩阵）遵循安全编码
  - 写 `concepts/index.md`：toctree 收录全部概念文档
  - 写根 `index.md`：okf_version frontmatter + 完整 sources（博文 URL + 核验权威 URL）+ status/stale_after(2026-12-31)/generated/verified + 内容导航表 + toctree（concepts/index、references/index、log）；若非操作教程，description 含"非操作教程"标注
  - 写 `log.md`：2026-09-08 创建条目（来源、F 编号范围、核验结论、结构、归属、工作流、gates 状态占位）
  - 如两问皆"是"则补 examples/（本任务预期不触发，触发时按 wigolo 先例追加）
- **Acceptance Criteria Addressed**：FR-8、FR-9、AC-1、AC-4、AC-7、AC-10、AC-11
- **Test Requirements**：
  - `rule` TR-6.1：正文每个数字/版本/产品名可回溯 F 编号或 sources；证据：逐篇 F 引用核对
  - `rule` TR-6.2：根 index frontmatter 十字段齐备（okf_version/type/title/description/tags/generated/verified/status/stale_after/sources），sources 含博文+权威双信源；证据：frontmatter
  - `rule` TR-6.3：全部 toctree 条目对应文件存在；证据：条目-文件对照
  - `rubric` TR-6.4：内容质量（中文流畅、三层清晰、表格得当、观点分层）；scale 1-5；anchors 1=复述堆砌/3=完整但平淡/5=有洞察增量且可读性强；threshold >= 4；证据：通读记录

## Task 7: V-1 对抗审查与机械门禁

- **Status**：`pending`
- **Priority**：high
- **Depends On**：Task 6
- **Description**：
  - 四视角审查：①事实溯源（无 F 外数字/模型名，勘误在正文落实）②结构规范（OKF v0.2 + toctree）③读者可用性（相对链接逐一可达、导航完整）④时效边界（单源/时点/观点分层标注）
  - 8 项机械门禁逐项执行：UTF-8 strict roundtrip、双份 F 编号一致、三级 toctree 完整、相对链接全可达+无 file:///、三级计数同步、敏感信息零残留、frontmatter 完整、勘误落实
  - 尝试在子模块跑 `invoke gates.utf8`/`gates.toctrees`/`gates.bundles`；依赖缺失则执行手动等效清单并在 log.md 注明（禁止谎报 gates 通过）
  - 问题直接修复并记录
- **Acceptance Criteria Addressed**：FR-10、AC-2、AC-5、AC-6、AC-8
- **Test Requirements**：
  - `rule` TR-7.1：8 项机械门禁逐项有执行记录与结论；证据：检查命令输出
  - `rule` TR-7.2：gates 有实际输出或手动等效清单全勾 + log.md 注明；证据：gates 输出或 log 注记
  - `rule` TR-7.3：四视角审查发现的问题全部修复；证据：问题-修复对照

## Task 8: V-2 三级索引接入与计数同步

- **Status**：`pending`
- **Priority**：high
- **Depends On**：Task 7
- **Description**：
  - 更新 `jishu/data/index.md`：分组导航表加 dolt 行（或直挂束表）、toctree 追加 `dolt/index`、束数先读现值再 +1
  - 更新 `jishu/index.md`：data 行束数（一级束口径）现值 +1
  - 更新 `bundles/index.md`：frontmatter total_bundles +1、jishu 束数 +1、data 组束数 +1、正文/mermaid 计数同步（以 gates.bundles 三角校验为准）
  - 重跑 gates.bundles 或手动三角校验确认五面一致
- **Acceptance Criteria Addressed**：FR-11、AC-5
- **Test Requirements**：
  - `rule` TR-8.1：三处索引 diff 仅含 dolt 相关新增与计数 +1；证据：git diff
  - `rule` TR-8.2：gates.bundles 通过或手动计数（目录树 vs frontmatter vs 计数行 vs 域节 vs toctree）五面一致；证据：校验输出

## Task 9: C-1 原子提交（子模块→主仓库→指针）

- **Status**：`pending`
- **Priority**：medium
- **Depends On**：Task 8
- **Description**：
  - ①子模块 `projects/awesome-okf-xs` 内用 `python .agents/scripts/git-commit-utf8.py -m "docs(data): 新增 Dolt 版本化 SQL 数据库知识包（博文转化+P0核验）" <显式文件列表>` 提交（bundle 全部文件 + data/index.md + jishu/index.md + bundles/index.md）
  - ②主仓库提交 spec（`.trae/specs/okf-wiki-ecosystem/dolt-okf-wiki/`）
  - ③主仓库更新子模块指针并提交
  - 三查暂存（工作区状态/暂存区差异/最近提交）；Conventional Commits；不 push
- **Acceptance Criteria Addressed**：FR-12、AC-9
- **Test Requirements**：
  - `rule` TR-9.1：子模块提交含全部 bundle 与索引文件且无遗漏/无多余；证据：`git show --stat`
  - `rule` TR-9.2：主仓库两条提交（spec、子模块指针）存在，两仓库 `git status` 干净；证据：两仓库 git log/status
  - `rule` TR-9.3：未执行 push；证据：无 push 命令记录

## Task 10: 独立审查（Review 阶段）

- **Status**：`pending`
- **Priority**：high
- **Depends On**：Task 9
- **Description**：
  - 队列清空后进入 Review：fresh context 独立审查（委派 general_purpose_task 只读审查），给审查者完整契约（用户目标、仓库根、spec/tasks/review 绝对路径、bundle 路径、验收标准）
  - 审查者独立复核全部 rule AC 与 rubric AC，产出结构化结果（pass/fail/blocked）
  - fail → review.md 记录 findings，回 Implement 将每条 actionable finding  materialize 为 pending issue 后修复，再启新一轮审查
- **Acceptance Criteria Addressed**：全部 AC
- **Test Requirements**：
  - `rule` TR-10.1：review.md 存在且每个 AC 有独立证据；证据：review.md
  - `rule` TR-10.2：最终 Review result == pass，无遗留 actionable finding；证据：Review History
