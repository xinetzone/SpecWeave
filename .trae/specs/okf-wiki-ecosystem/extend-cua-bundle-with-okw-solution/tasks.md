# Cua 知识束扩展 × cua+okw 最优解 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: R 阶段 - 第二篇文章全文获取与事实采集（F-066+）
- **Completion Evidence**: 事实 F-066~F-154（第二篇 74 条 + 核验补充 15 条 = 89 条，连续无跳号，与 F-001~F-065 不相交）；类型分布 O 60 / V 7 / S 22；产出 `.trae/specs/okf-wiki-ecosystem/extend-cua-bundle-with-okw-solution/facts.md`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 获取第二篇文章全文（URL `https://mp.weixin.qq.com/s/vEGTwWZ8Mws2fwAQyvm0Yg`；本机已用 `Invoke-WebRequest` + 主区提取脚本取得正文，实现阶段需重新确认可复现取文方式并留痕）
  - 从 F-066 起**连续编号**采集第二篇事实；每条标注类型（`O` 客观 / `V` 作者观点 / `S` 厂商自述）与来源
  - 分类：文章元信息 / 六组件 / 权限三档 / Bench 榜单 v1 / `cua sb` 命令族 / 许可分层 / 废弃包与安全警告 / 何时不需要 / 采用者 / Fleets 定价 / 结语判断
  - 产出 1：`.trae/specs/okf-wiki-ecosystem/extend-cua-bundle-with-okw-solution/facts.md`（规划侧事实清单）
  - 产出 2：`projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/cua/references/second-article-facts.md`（束内信源清单，与 facts.md F 编号一致）
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-1.1: 事实编号自 F-066 起连续无跳号；与既有 F-001~F-065 **无冲突无重复**（正则集合比对）
  - `rule` TR-1.2: 厂商自述/榜单数值单独标记（`S`），观点标注作者观点（`V`）
  - `rule` TR-1.3: 事实表不含因果推断词（"因为/导致/所以"），符合 G1
- **Notes**: 第二篇为第三方公众号推介，非官方文档；作者未提供实测结果

## [x] Task 2: R 阶段 - P0 权威核验与跨信源对账
- **Completion Evidence**: P0 核验结论 **✅ 14 / ⚠️ 6 / ❌ 0**（注：R 阶段摘要曾误记 13/7，Task 8 复核发现、Task 10 统一为 14/6，见 review.md 可行动发现 #1）；2026-10-16 GitHub API 实测 stars 29,926、forks 2,142、issues 1,217、language=Rust(42.31%)、MIT、created 2025-01-31；跨信源对账 4 条四元组（模块命名/接口命名/主语言/Stars 四版）；未核验项 3 项（Fleets 单价、权限三档命名、采用者名单）已如实标注
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - P0 核验对象（预计）：GitHub API 当前时点（stars/forks/open_issues/language/contributors/created_at）；官方 README/许可材料（MIT + FSL-1.1-MIT + AGPL 分层、废弃包、`cuabot` 警告）；`cua.ai` 安装命令（`install.sh` / `cua sb` 命令族 / driver install）；Cua Bench 榜单（cuabench.ai/leaderboard）
  - 产出核验补充事实（F-0NN 续号），并识别 `✅ / ⚠️ / ❌`
  - **跨信源对账四元组**（第一篇 ↔ 第二篇）：Fleets vs Spaces 命名；"Sandbox SDK" vs "Cua SDK 与 CLI"；主语言 HTML vs Rust；Stars 三版快照（24,432 / 29,189 / 2.8 万）
- **Acceptance Criteria Addressed**: AC-3, AC-6
- **Test Requirements**:
  - `rule` TR-2.1: 每项 P0 声明有核验结论与来源 URL
  - `rule` TR-2.2: 发现的差异**不静默照搬**，新增 F 编号记录实际值与差异
  - `rubric` TR-2.3: 跨信源对账四元组（现象/差异/影响/处置）覆盖全部差异点，无遗漏
- **Notes**: GitHub API 为第一优先权威源；榜单分数无法独立复现者标注"厂商/文章转述值"

## [x] Task 3: I 阶段 - 归属、骨架与合成章节设计
- **Completion Evidence**: 产出 `structure-plan.md`（269 行）：归属去重说明、骨架判定（无 examples 两问理由）、14 文件清单表、06 章节 6 小节大纲、四类场景选型判据表、F 编号/okw 文档→章节映射表、互链计划、12 项 V 门禁清单；未验证项 8 条
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 确认归属：既有束 `jishu/ai/frameworks/ai-agent/cua/`（**不新建束**，去重）
  - 确认骨架：无 `examples/`（操作可复现性两问 Q2 为否）
  - 设计 `concepts/06-cua-okw-solution.md` 大纲：①问题与定位 ②分层架构分工（宿主/Agent 的电脑/工作负载）③模块选型判据表 ④组合路径（设计）⑤前置条件 ⑥风险与未验证项清单
  - 确定 okw 事实来源锚点（`apps/dev-tools/openkylin-wsl-devkit/README.md`、`apps/dev-tools/openkylin-wsl-devkit/doc/{index,02,03,05,08}.md`）
  - 产出：`structure-plan.md`（含 06 章节大纲与 F 编号/okw 文档映射）
- **Acceptance Criteria Addressed**: AC-1, AC-4
- **Test Requirements**:
  - `rule` TR-3.1: 骨架符合 OKF v0.2（index + concepts/ + references/ + log）
  - `rule` TR-3.2: 06 章节每小节有明确事实锚点（F 编号或 okw 文档路径）
  - `rubric` TR-3.3: 选型判据表可迁移（对他类"宿主 + Agent 电脑 + 工作负载"组合亦适用）
- **Notes**: 06 章节为**合成设计**，与源文事实层严格分离

## [x] Task 4: E 阶段 - 信源先行（references/ 增量）
- **Completion Evidence**: 新增 `references/second-article-facts.md`（F-066~F-154，89 条，与 spec facts.md 集合一致，编号连续、差集 0）；`references/verification.md` 追加第二轮核验（20 项，✅14/⚠️6/❌0）与跨信源对账 4 条；`references/index.md` 追加第二信源与编号索引；`references/article-source.md` 仅追加 1 行指向第二信源
- **Priority**: high
- **Depends On**: Task 2, Task 3
- **Description**:
  - 生成 `references/second-article-facts.md`（F-066+，双份登记之一）
  - 追加 `references/verification.md`：第二轮核验结论表 + 跨信源对账段落（`sources` frontmatter 补第二篇）
  - `references/article-source.md`：仅补一行"第二信源见 second-article-facts.md"，**不改既有 F-001~F-065 事实体**
  - 更新 `references/index.md`：信源清单 + 事实编号索引 + `{toctree}` 追加 `second-article-facts`
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-4.1: `second-article-facts.md` 的 F 编号集合与 spec `facts.md` 完全一致（正则比对）
  - `rule` TR-4.2: `verification.md` 含跨信源对账段落，每条差异有处置
  - `rule` TR-4.3: `references/index.md` 含 `{toctree}` 且条目数与实际文件数一致
- **Notes**: 信源先于是 E 阶段第一步，先于 concepts 生成

## [x] Task 5: E 阶段 - 生成 concepts/06-cua-okw-solution.md
- **Completion Evidence**: 新增 `concepts/06-cua-okw-solution.md`（6 小节：问题定位/三层分工/选型判据表 4 行/组合路径 GUI+headless/前置条件/8 项风险与未验证项）；顶部合成边界声明；无 banned 字面串；01 与 05 各追加 1 行互链
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 撰写 cua × okw 最优解章节（OKF frontmatter：`type: Concept` + title/description/tags/generated/status/stale_after/sources）
  - 顶部显式标注**「合成设计（synthesis）· 未在本机实测」**
  - 内容：分层架构分工 / 模块选型判据表 / 组合路径 / 前置条件 / 风险与未验证项
  - 交叉引用：Cua 侧引 F 编号；okw 侧引 `apps/dev-tools/openkylin-wsl-devkit/README.md` 与 `apps/dev-tools/openkylin-wsl-devkit/doc/*`（**相对路径**，禁 `file:///`）
  - 01-five-core-modules / 05-scenarios-and-limitations 各加一行"延伸阅读 → 06"互链
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-5.1: 章节含合成边界声明，且无"已实测/已验证可用"类无证据表述
  - `rule` TR-5.2: 所有 okw 侧引用为相对路径且可达；无 `file:///` 绝对路径
  - `rubric` TR-5.3: 选型判据表对"无 GUI 命令任务 / 需 GUI 且要求隔离 / 可复现开发环境 / 评测与训练"四类场景给出明确建议
- **Notes**: 未验证项须写明验证路线（如：Cua Linux Driver 对 UKUI/xrdp 会话的支持需实测）

## [x] Task 6: E 阶段 - 更新束内导航与文件计数
- **Completion Evidence**: `concepts/index.md` 路径表/路径建议/toctree 追加 06（7 条）；束根 `index.md` 更新 frontmatter（description/tags/sources/generated/verified）、性质声明、目录树、信源表、分层导航、信任与生命周期（事实 65→154、两轮核验）、已知边界（+2 条）、文件计数（9 内容文档/12 文件 → 11 内容文档/14 文件）；根 toctree 保持 3 条；父级索引零改动（`git status --porcelain` 佐证）
- **Priority**: high
- **Depends On**: Task 4, Task 5
- **Description**:
  - `concepts/index.md`：学习路径表 + `{toctree}` 追加 `06-cua-okw-solution`
  - 根 `index.md`：frontmatter（description/tags/sources/generated/verified 更新）、目录树、"知识结构总览"、分层导航、信源说明、文件计数（12 → 14）、"已知边界"补第二信源与合成章节声明、`{toctree}` 不变（仍 concepts/index + references/index + log）
  - **确认无计数变更**：不改 `ai-agent/index.md` / `ai/index.md` / `jishu/index.md` / `bundles/index.md` 的任何计数
- **Acceptance Criteria Addressed**: AC-5, AC-7
- **Test Requirements**:
  - `rule` TR-6.1: 根 `index.md` 声明的文件计数 = 实际文件数（14）
  - `rule` TR-6.2: 导航表链接与 `{toctree}` 条目一致
  - `rule` TR-6.3: 父级/域/总索引计数**零改动**（`git diff` 证明这些文件未被修改）

## [x] Task 7: E 阶段 - 更新 log.md
- **Completion Evidence**: `log.md` 追加第二轮章节（175 行）：R→I→E→V 链路表、14 项文件清单（新增 2 / 修改 5 / 沿用 7）、G1–G4 表、跨信源对账 4 条、已知限制 3 条；第一轮内容零改写（git diff 仅 4 个 hunk）
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 追加第二轮 R→I→E→V 记录：动作/产出表、第二信源表、文件清单（14 项）、G1–G4 结论、跨信源对账说明、已知限制（含"合成章节未实测"）
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-7.1: log.md 含第二轮记录且与最终文件清单一致
  - `rule` TR-7.2: 第二轮 G1–G4 逐项有结论

## [x] Task 8: V 阶段 - 机械门禁与对抗审查
- **Completion Evidence**: 独立验证报告：门禁 9 PASS / 1 FAIL（FAIL 项为父级 `doc/bundles/index.md`、`jishu/ai/index.md` 被**并行会话**改动，非本束；`git diff` 无 cua 字样）；四视角审查发现 **P0=0、P1=1（核验分级计数 13✅/7⚠️ 与表 14✅/6⚠️ 不一致）、P2=3**；链接实测 168 条 BROKEN=0；F 号双份 89/89 集合相等；banned 三串 0
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - 在 `projects/awesome-okf-xs/` 运行：`invoke gates.toctrees`、`invoke gates.bundles`、`invoke gates.utf8`
  - 相对链接可达性检查（`check-links` 或等价工具，针对束目录）
  - 四视角对抗审查：事实视角（F 编号/双份一致）、结构视角（OKF v0.2 / toctree）、可用视角（分层导航/合成边界）、时效视角（时点标注/stale_after）
  - 双份 F 编号一致性：spec `facts.md` ↔ 束 `references/second-article-facts.md`
- **Acceptance Criteria Addressed**: AC-6, AC-7, AC-8
- **Test Requirements**:
  - `rule` TR-8.1: `gates.toctrees` 通过（无断链、无孤立、bundle 根 index 完整）
  - `rule` TR-8.2: `gates.bundles` 通过且计数与改动前一致
  - `rule` TR-8.3: `gates.utf8` 通过（无 BOM、UTF-8 严格解码）
  - `rule` TR-8.4: 无 `file:///` 绝对路径；相对链接全部可达
  - `rubric` TR-8.5: 四视角审查各有结论记录
- **Notes**: 门禁失败须回修后重跑，不得仅凭过程描述宣称通过

## [x] Task 9: C 阶段 - 子模块内原子提交
- **Completion Evidence**: 子模块 `projects/awesome-okf-xs` 内提交 `137483e7`（`docs(bundle): Cua 知识束补录第二信源并新增 cua x okw 最优解章节`），10 files changed, 643 insertions(+), 29 deletions(-)，**仅含本次 cua 束内 10 个文件**；未推送；工作区剩余改动经 `git diff` 核验无 cua 字样，属并行会话 `wecom-topic-scenarios` 束，按不回滚原则保持不动
- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - 在 `projects/awesome-okf-xs` 子模块内执行原子提交（Conventional Commits，中文主体；`docs(bundle): ...`）
  - 提交范围**仅限**本次束内改动文件；不夹带其他变更；不推送（除非用户明确要求）
  - 提交后 `git status` 核对，确认无遗留
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `rule` TR-9.1: 单次提交单一职责，仅含本次束改动
  - `rule` TR-9.2: 提交信息符合 Conventional Commits 且主体为中文
  - `rule` TR-9.3: 提交后工作区干净（`git status` 无本次相关未跟踪/未暂存项）

## [x] Task 10: V 阶段 - 修复 Task 8 审查发现（P1 计数不一致 / 文件状态 / status）
- **Completion Evidence**: 归一化核验计数为 **14✅/6⚠️/0❌**（verification.md L194/L219、index.md L28/L48/L102、references/index.md L10、log.md G3、spec facts.md）；`log.md` 文件状态改为 修改 8 / 沿用 4 并同步清单 #4/#8/#11；回填 V 门四视角结论与并行会话隔离备注；`second-article-facts.md` status → stable；`concepts/06` 声明块与后文去除易误判字面串。复验：check-utf8 exit 0、check-toctrees exit 0、`13✅|7⚠️` 残留 0 命中
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 修正核验分级计数：§6 结论表实测 **✅14 / ⚠️6 / ❌0**，但正文与索引多处写作"13✅ / 7⚠️"，全部归一化为 14/6
  - 修正 `log.md` 第二轮文件状态汇总（实际 修改 8 / 沿用 4，非 修改 5 / 沿用 7），并同步文件清单表中 #4、#8、#11 的状态列
  - `references/second-article-facts.md` 的 `status: draft` → `stable`（与束内一致）
  - `concepts/06-cua-okw-solution.md` 声明块末尾改写，去除可能被门禁误判的字面串
  - `log.md` 回填 Task 8 的 V 门（四视角）结论，替换"待 Task 8 复核确认"占位
  - spec 侧 `facts.md` 若存在"13✅/7⚠️"表述，一并对齐为 14/6
- **Acceptance Criteria Addressed**: AC-3, AC-6, AC-7
- **Test Requirements**:
  - `rule` TR-10.1: 全仓（束内 + spec facts.md）无"13✅""7⚠️"残留，与 §6 表逐行计数一致
  - `rule` TR-10.2: `log.md` 文件状态汇总与 `git status` 实际改动一致
  - `rule` TR-10.3: 修复后重跑 UTF-8 与 toctree 门禁仍 PASS

---

# Task Dependencies

- Task 2 depends on Task 1
- Task 3 depends on Task 1
- Task 4 depends on Task 2, Task 3
- Task 5 depends on Task 3
- Task 6 depends on Task 4, Task 5
- Task 7 depends on Task 6
- Task 8 depends on Task 7
- Task 10 depends on Task 8
- Task 9 depends on Task 10

# Parallelizable Work

- Task 2（核验）与 Task 3（设计）可并行（同依赖 Task 1）
- Task 4（references）与 Task 5（concepts/06）可在 Task 3 完成后并行启动

# Acceptance Criteria

- **AC-1**: 第二篇文章已作为第二主信源登记，事实编号自 F-066 起连续，与 F-001~F-065 无冲突
- **AC-2**: 双份 F 编号一致（spec facts.md ↔ 束 references/second-article-facts.md）
- **AC-3**: P0 核验完成，`✅/⚠️/❌` 分级齐备，差异不静默照搬
- **AC-4**: `concepts/06-cua-okw-solution.md` 存在，覆盖架构分工/选型判据/组合路径/前置条件/风险
- **AC-5**: 合成边界声明显式，无未经证据支持的"可用/已验证"表述
- **AC-6**: 跨信源对账四元组完整（现象/差异/影响/处置）
- **AC-7**: 束内导航（concepts/index、references/index、根 index、log）收录新增内容；文件计数正确（14）
- **AC-8**: 机械门禁（toctrees/bundles/utf8/链接）全通过，且父级计数零改动
- **AC-9**: 子模块内原子提交完成且工作区干净
