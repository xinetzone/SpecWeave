---
id: "specweave-skills-index"
date: "2026-06-30"
type: "index"
source: "AGENTS.md#能力索引;.agents/capability-registry.md"
x-toml-ref: "../../.meta/toml/.agents/skills/README.toml"
title: ".agents/skills/ 目录索引"
---
# .agents/skills/ 目录索引

本目录存放 SpecWeave 项目中所有 Skill 定义。Skill 分为七类：

- **完整Skill**：包含完整的自动化操作能力（脚本、MCP工具调用等），可独立完成任务
- **工作流门面**：对 `docs/retrospective/patterns/` 方法论模式的触发封装（L1 门面 + L2 模式文档），提供触发词、阶段流程、质量门与安全清单
- **命令集门面**：对 `.agents/commands/` 命令集的轻量封装，提供触发词、决策树、快速开始和安全检查
- **脚本命令门面**：对 `.agents/scripts/` 高频自动化脚本的封装，提供参数说明、dry-run安全机制和错误处理
- **内置镜像 Skill**：Trae IDE 内置技能的镜像入库（原貌保留，frontmatter source 溯源），用于项目自托管与统一发现
- **设计库镜像 Skill**：Trae IDE 内置设计系统库的完整归档（token CSS/组件 JSON/预览 HTML/UI Kit 全量自包含，frontmatter source 溯源），不依赖外部源目录
- **TeleAgent 平台镜像 Skill**：TeleAgent（星辰超级智能体）平台技能镜像入库（原貌保留，frontmatter source 溯源），用于工作区自托管与统一发现

## Skill 列表

### 命令集门面（11个）

| Skill名称 | 类型 | 对应命令集 | 核心触发词 | SKILL.md路径 |
|-----------|------|-----------|-----------|-------------|
| ⭐ seven-concepts-cmd | 命令门面 | 方法论编排（基于七概念） | 方法论编排、用方法论、系统性分析、完整流程、七概念（别名） | [seven-concepts-cmd/SKILL.md](seven-concepts-cmd/SKILL.md) |
| retrospective-cmd | 命令门面 | 复盘 | 复盘、retrospective、回顾、总结经验、项目总结 | [retrospective-cmd/SKILL.md](retrospective-cmd/SKILL.md) |
| insight-cmd | 命令门面 | 洞察 | 洞察、insight、分析问题、诊断问题、找原因、根因分析 | [insight-cmd/SKILL.md](insight-cmd/SKILL.md) |
| extraction-cmd | 命令门面 | 萃取 | 萃取、extraction、模式沉淀、模式入库、可复用模式、沉淀为模式 | [extraction-cmd/SKILL.md](extraction-cmd/SKILL.md) |
| export-report-cmd | 命令门面 | 导出报告 | 导出、export、生成报告、导出报告、输出报告 | [export-report-cmd/SKILL.md](export-report-cmd/SKILL.md) |
| atomization-cmd | 命令门面 | 原子化 | 原子化、atomization、拆分文件、拆分文档、整理文件 | [atomization-cmd/SKILL.md](atomization-cmd/SKILL.md) |
| atomic-commit-cmd | 命令门面 | 原子提交 | 提交、commit、原子提交、提交代码、保存更改 | [atomic-commit-cmd/SKILL.md](atomic-commit-cmd/SKILL.md) |
| mermaid-cmd | 命令门面 | Mermaid图表管理 | mermaid、流程图、时序图、状态图、画个图、图表、架构图、思维导图 | [mermaid-cmd/SKILL.md](mermaid-cmd/SKILL.md) |
| token-optimize-cmd | 命令门面 | Token优化 | Token优化、降本、成本优化、缓存命中率、上下文压缩、Prompt优化、LLM成本 | [token-optimize-cmd/SKILL.md](token-optimize-cmd/SKILL.md) |
| sovereign-rollout-cmd | 命令门面 | 主权区治理资产落盘 | 提案、批准落盘、主权区变更、治理资产落盘、先提案后批准 | [sovereign-rollout-cmd/SKILL.md](sovereign-rollout-cmd/SKILL.md) |
| github-org-bootstrap-cmd | 命令门面 | GitHub 组织命名与初始化 | 创建GitHub组织、建个org、组织名怎么起、demo组织、huncheng-lab | [github-org-bootstrap-cmd/SKILL.md](github-org-bootstrap-cmd/SKILL.md) |

### 完整Skill（46个）

| Skill名称 | 类型 | 功能描述 | 核心触发词 | SKILL.md路径 |
|-----------|------|---------|-----------|-------------|
| forum-posting | 完整Skill | Discourse论坛自动化操作（发帖、编辑、回复、清理草稿等），支持双方案（MCP+Playwright脚本） | 发帖、编辑帖子、回复帖子、forum.trae.cn、forum-bot | [forum-posting/SKILL.md](forum-posting/SKILL.md) |
| home-assistant | 完整Skill | Home Assistant智能家居系统集成（设备控制、状态查询、服务调用），REST API交互 | 智能家居、控制设备、查询状态、home assistant、ha_api | [home-assistant/SKILL.md](home-assistant/SKILL.md) |
| git-commit-helper | 完整Skill | Git原子化提交规范执行（三查暂存法→预提交验证→构建提交信息→执行提交→验证结果），含validate_commit.py | 提交、commit、原子提交、代码提交、提交变更、git commit、保存更改 | [git-commit-helper/SKILL.md](git-commit-helper/SKILL.md) |
| trae-computer-use-ptc | 完整Skill | Computer Use Windows 桌面应用 UI 自动化指南（本地 MCP）：list_apps/get_app_state/click/scroll/type_text 等操作，Electron/桌面应用场景，高风险操作前须确认；import-builtin-skills 时既有同名保留未覆盖的本地 v1.2.0 | Computer Use、电脑操作、UI自动化、桌面交互、操作应用 | [trae-computer-use-ptc/SKILL.md](trae-computer-use-ptc/SKILL.md) |
| client-overlay-scaffold | 完整Skill | apps/containers/client/overlays/ 工作负载叠加栈脚手架（v1.1）：形态 A/B 决策树 + 声明式 StackSpec（make_stack_tasks 六任务工厂，栈模块零生命周期代码）+ compose extends `_shared/base-rootless.yaml` 基段（三必需/凭证/bridge 单一事实源）；compose/namespace/.env 三套骨架模板 + 12 件套清单 + 7 接线登记点（含 test_tasks_surface/test_compose_merge 两张黄金表）+ G1~G15 实测踩坑 + 四级验证链；源自 quant/native/monetize 三栈与两轮独立审查 | 新增 client 叠加层、工作负载栈、新 compose invoke 命名空间、照 onnx/native/monetize 栈再做一个、overlay 脚手架 | [client-overlay-scaffold/SKILL.md](client-overlay-scaffold/SKILL.md) |
| collect-api-decouple-cmd | 完整Skill | 硬件/设备采集类 API 的"采集-解析分离 + 日志复用"重构执行卡：副作用边界切分（触网/写盘 vs 纯本地计算）、dataclass 阶段契约、`run_<step>=True` 开关逐层贯通、复用分支纯路径推导并规避 rmtree/unlink 清理型工厂、产物缺失同源报错、缩放参数一致性警示；含 I→F→A→V 步骤模板、安全检查清单、Gotchas 与 npuusertools 双案例 | 推理和后处理分开、采集/推理变成可选、已经推理过了复用日志、跳过设备执行、重放日志、只重新算指标 | [collect-api-decouple-cmd/SKILL.md](collect-api-decouple-cmd/SKILL.md) |
| classical-festival-video | 完整Skill | 古典底本节日祝福视频生成（三关键帧→10s竖版视频→随片文案+考据弹药；含情感分寸矩阵、画面禁字约束、预览确认门与物理量验收） | 祝福视频、节日贺卡视频、给 TA 做个视频、用老子/庄子/诗词做底本、中秋/春节/元宵祝福 | [classical-festival-video/SKILL.md](classical-festival-video/SKILL.md) |
| meoo-cli | 完整Skill | 秒悟（Meoo）全栈应用构建与部署（阿里云官方第三方技能，随 CLI 包安装）：static（SPA→CDN）与 server（全栈→容器）双模式，Supabase 数据库/Auth/Storage + Deno 边缘函数 + AI 模型接入；覆盖初始化→云服务→部署全生命周期，含 Mise 发布协议 BLOCKING 门禁与阿里云自托管部署分支 | 秒悟、Meoo、meoo cli、用秒悟建应用、部署到秒悟、部署全栈应用 | [meoo-cli/SKILL.md](meoo-cli/SKILL.md) |
| meoo-skill-publish | 完整Skill（v1.0.0，L1） | 本地 Skill→自包含 ZIP→Meoo 技能市场（meoo.com/skills）发布/版本更新与字节级回验：P1 根级合规打包（YAML 头/name 一致/零包外引用，确定性 ZIP+b64+清单）→ P2 官方 `POST /api/v1/skills/publish`（带 skill_id 即版本更新，tags 取 v2_* key）→ P3 线上版本下载逐文件 SHA256 比对；含 127.0.0.1 中继脚本、浏览器 evaluate 两步法与 7 条 Gotchas；萃取自 104319 v1 耦合版→v2 独立版实战 | 上传技能、发布技能到 Meoo/技能市场、更新技能版本、技能市场上架、meoo.com/skills 发布 | [meoo-skill-publish/SKILL.md](meoo-skill-publish/SKILL.md) |
| skill-mirror-archive | 完整Skill（v1.0.0，L1） | 外部技能镜像归档：把 TeleAgent/Trae IDE 等外部平台技能镜像入库 .agents/skills/（sovereign-rollout 四阶段 + Copy-Item 保真 + frontmatter source 溯源泛化 + 登记面双轨裁剪 + 原子提交）；萃取自 sc-20261021-teleagent-skill-archive 首例 | 归档技能、技能镜像入库、平台技能导入、镜像归档、外部技能入库 | [skill-mirror-archive/SKILL.md](skill-mirror-archive/SKILL.md) |
| aiworks-deploy-cmd | 完整Skill（v1.0.0，L2） | 知乎 AI Works 源码代部署与发布（官方 deploy-helper 五步链：inspect→描述符→validate 先 --plan-only→settle→archive→浏览器上传→构建观察→审核声明→发布→复核）；含错误码 8 修复、React 表单 bug 与 Draft.js 富文本两大 Gotchas 族；萃取自 sc-20261023-zhihu-ai-science-workshop 发布实战 | 上传源码、一键部署、代部署、部署失败、错误码 8、frontend.deploy.json、AI Works、科学季投稿、deploy-helper、静态作品上线 | [aiworks-deploy-cmd/SKILL.md](aiworks-deploy-cmd/SKILL.md) |
| zhihu-article-publish-cmd | 完整Skill（v1.0.0，L2） | 知乎专栏文章发布自动化（Draft.js 唯一持久化输入通道：CDP Input.insertText，bu.type/execCommand/剪贴板均不可用；图片插入四步法：file input id 注入→upload_file→上传状态确认→JS 点击「插入图片」；话题候选四步选择法：JS 文本精确点击+标签行 DOM 验证；发布后文章页回读验证清单）；含 10.1-10.3 Gotchas 族；萃取自 sc-20261023-zhihu-article-publish 发布实战 | 写文章、发布文章、知乎专栏、zhuanlan、填知乎编辑器、插入配图、话题没加上、补话题、创作声明、发布设置、更新文章 | [zhihu-article-publish-cmd/SKILL.md](zhihu-article-publish-cmd/SKILL.md) |
| declared-consistency-fix | 完整Skill（v1.0.0，L1） | 跨文件「声明不一致」修复（许可证/版本号/路径/分类/依赖下限/构建元数据）：git 考古（log --follow/-S）定真源 → 全仓扫描 + 再生产源（模板/生成器/CI 默认/元数据镜像）→ 策略门确认 → 统一修正 → 机械验证 → 两级提交；含只读校验脚本 check_license_consistency.py 与 xuanspace 八文件实战案例 | 统一口径、修正许可证声明、README 与 LICENSE 不一致、版本号对不上、路径引用失效、声明漂移、修完又漂回去 | [declared-consistency-fix/SKILL.md](declared-consistency-fix/SKILL.md) |
| skill-quality-gate-remediation | 完整Skill（v1.0.0，L1） | 技能质量门（check-skill-quality.py）修复闭环：取基线 → 按 error→warn 定位 → 核对 constants.py 判定正则 → 实质性补齐（> **为什么？** 引用块 ≥2、dry-run/预览门、幂等或步骤级验证、`## N. Gotchas` 编号标题、安全检查清单且全文 `- [ ]` ≥5、推荐 frontmatter 四字段）→ 复跑至 34 项全过 → 记录首次失败原因；含 34 项检查映射表与 declared-consistency-fix 65→100 实战案例 | 质量门没过、check-skill-quality 报错、Skill 只有 65 分、评分低于阈值、补 Why 解释、Gotchas 写了不算数、安全检查清单缺失、技能落盘被扣分 | [skill-quality-gate-remediation/SKILL.md](skill-quality-gate-remediation/SKILL.md) |
| native-skill-surface-registration | 完整Skill（v1.0.0，L1） | 原生 Skill 四处全量登记与双门收尾：前置探针（质量基线+幂等重入探测）→ 预览确认门 → README/registry/CHANGELOG/.meta toml 四处登记与计数同轮更新 → 质量门 34 项全过 + 链接门 0 断链双验收 → PowerShell Junction 用户级联接（禁复制、rmdir 清空目录树）→ HEAD 计数漂移顺带修正与记录；含登记面逐字模板与 skill-quality-gate-remediation v1.31 入库案例 | 登记这个 Skill、四处登记、登记面同步、SKILL.toml 镜像、技能入库、双门收尾、联接而非副本、计数漂移修正 | [native-skill-surface-registration/SKILL.md](native-skill-surface-registration/SKILL.md) |
| oversized-tool-output-slicing | 完整Skill（v1.0.0，L2 双场景复发验证） | 超限工具输出切片取证：识别三类信号（MCP `[OUTPUT TRUNCATED ... 25000 token limit]` 落盘、Read `exceeds maximum allowed tokens`、Glob/ripgrep/find 大仓 20s 超时）→ 路径 A 以错误消息给出的落盘绝对路径为唯一事实来源，用捆绑 `extract_tool_result.js`（零依赖，overview/messages/tool/text/grep 五模式）JSON.parse 后定点切片，禁第二次全文 Read（加 limit 仍按全文计量）→ 路径 B `git ls-files \| grep -iE` 走索引替代超时搜索；含参数预算预防、幂等重入表、7 项安全清单与 8 条 Gotchas | 输出被截断、超过 25000 token、落盘文件读不了、tool-results、Read 超限、ripgrep 超时、大仓找不到文件、读长会话记录取证、咋这么慢 | [oversized-tool-output-slicing/SKILL.md](oversized-tool-output-slicing/SKILL.md) |
| skill-recommendation-disk-triage | 完整Skill（v1.0.0，L1） | Skill 推荐指令磁盘取证分诊：收到自动推荐的 Skill 创建/更新/重命名指令时先只读取证再决定真实动作——跨根查重（~/.qoder/skills 与 .agents/skills 两根）→ 登记面 git grep（README/registry/CHANGELOG/toml 四处）→ 双门 --path 实跑（check-skill-quality + check-links --check-frontmatter-paths）→ 捆绑脚本真实落盘产物回归 → create→register+junction/update 改判决策树 + 写盘前确认门 | 这个推荐该新建还是已存在、别覆盖已有同名 Skill、自动推荐 Skill、先核实再动手、create 还是登记、推荐指令分诊、跨根查重 | [skill-recommendation-disk-triage/SKILL.md](skill-recommendation-disk-triage/SKILL.md) |
| registered-skill-frontmatter-completion | 完整Skill（v1.0.0，L1） | 登记后回指补齐：S0 基线取证（镜像 toml、欠账句、全集断链数）→ S1 镜像先行补三级 x-toml-ref（`../../../.meta/...`，禁止 `../../`）→ S2 按链接门 `_extract_paths_from_value` 真实规则改写 source（中文散文禁夹 `/` 与 `.md/.toml/.py` token）→ S3 欠账句改完成记录（四处落点 + CHANGELOG 版本）→ S4 质量门 100/100 + 定点链接门 0 断链 + 全集基线差值 0；含 118 条既有断链归因与 10 条 Gotchas | frontmatter 补齐、补 source、x-toml-ref 写错、链接门报 source 断链、118 条断链、登记后回指、SKILL.toml 镜像指向、登记状态自相矛盾 | [registered-skill-frontmatter-completion/SKILL.md](registered-skill-frontmatter-completion/SKILL.md) |
| skill-registry-count-drift-audit | 完整Skill（v1.0.0，L1） | 登记面分类计数漂移审计：把 .agents/skills/README.md 与 .agents/capability-registry/02-skills.md 每个分类标题声明的（N个）与该节实际表格数据行逐一比对，先自证计数器再下结论，区分表头漂移、多子表求和与跨面缺行三类；含捆绑只读审计脚本 audit_surface_counts.js（自检夹具 + 4 档退出码）与报告模板 | 登记面计数漂移、表头数字和行数不一致、README 与 registry 数量对不上、命令集门面 11/10、审计分类计数、count drift、核对（N个） | [skill-registry-count-drift-audit/SKILL.md](skill-registry-count-drift-audit/SKILL.md) |
| shared-worktree-rebase-write-guard | 完整Skill（v1.0.0，L1） | 共享工作树写入前预检：探测进行中的 rebase/merge/cherry-pick 与冲突信号，区分可安全创建的新目录与必须延后的共享登记面，绝不 abort/continue 他人发起的 rebase；采用「内容+验证+联接先行、登记延后」的部分交付，恢复后重新读取版本号与计数再补登记；含捆绑脚本 check_rebase_guard.js、信号解释矩阵与 10 条 Gotchas | 共享工作区、rebase 进行中、pull --rebase、gitlink 冲突、登记面数字回退、写入前预检、rebase guard、shared worktree、concurrent rebase、defer registration | [shared-worktree-rebase-write-guard/SKILL.md](shared-worktree-rebase-write-guard/SKILL.md) |
| workspace-triplet-scaffold | 完整Skill（v1.0.0，L1） | 工作区三件套补齐与校验：为目录补 README.md + AGENTS.md + .agents/README.md，先判区域（apps/projects/vendor/external/playground/独立仓库）与 gitignore 状态，再对齐既有范本做增补而非覆盖，最后用捆绑 check_triplet.py 校验启动协议关键词、相对链接、嵌套优先声明与提交状态；含不可提交目录判定与 6 条 Gotchas | 加三件套、补 AGENTS 入口、目录治理结构、README+AGENTS、智能体入口、工作区入口、check_triplet | [workspace-triplet-scaffold/SKILL.md](workspace-triplet-scaffold/SKILL.md) |
| session-to-skill | 完整Skill（v1.0.0，L1） | 会话萃取为可复用 Skill 的端到端编排：加载 skill-creator → 以最小预算读取来源会话并用用户原话与工具失败输出取证 → 跨用户级/主权区/仓库三根查重判定 create/update → 提交方案等待确认 → 写入 SKILL.md + references + evals → 机械验证并如实标注未验证项；含超限切片降级路径与三根查重判定表 | 这个会话做成 Skill、按来源会话创建/更新/重命名 Skill、先核实再动手不要臆造未读内容、会话萃取为 Skill | [session-to-skill/SKILL.md](session-to-skill/SKILL.md) |
| shared-branch-merge-push-gate | 完整Skill（v1.0.0，L1） | 共享分支合并与推送门禁：G0 固化授权基线 → G1 现取分歧度 → G2 fetch 取上游真值 → G3 上游改动路径 → G4 本地脏/未跟踪集合 → G5 求交集 → G6 冲突预演与中间态检查；全通过才 merge，按子模块到父仓顺序推送，推送后复验分歧度 0 0；捆绑 merge_gate.py 提供 0/2/3/4/5/6 六档退出码；含索引锁证据保全与 10 条 Gotchas | 合并后推送、同步上游、merge origin/main、落后上游几条怎么办、推送被拒、共享分支合并 | [shared-branch-merge-push-gate/SKILL.md](shared-branch-merge-push-gate/SKILL.md) |
| user-level-skill-junction-delivery | 完整Skill（v1.0.0，L1） | 用户级 Skill 目录联接交付：三条前置（推荐建到用户级 + 主权区已有双门达标副本 + 本轮明确不做四处登记）→ 只读取证四步 → 提案确认门 → PowerShell Junction 交付（禁复制、禁穿透写）→ 经目标路径六项验收（枚举文件、双门复跑、脚本与 evals、git status 哈希前后一致）；含幂等重入表与 12 条 Gotchas | 在用户级新建 Skill、装到 ~/.qoder/skills、建联接不复制、目录联接交付、为什么用户级没有这个技能 | [user-level-skill-junction-delivery/SKILL.md](user-level-skill-junction-delivery/SKILL.md) |
| version-floor-contract-guard | 完整Skill（v1.0.0，L1） | 版本下限契约守卫：把 manifest 声明的最低支持版本变成可执行断言——实测真门槛（隔离安装候选版本、走真实消费路径跑夹具、再验门槛之上一个版本）→ 枚举全部声明面（实例 manifest/模板/脚手架生成器/文档/conda 与环境文件）→ 把断言并入 CI 已调用的校验脚本 → 夹具正负双向验证（精确退出码与报错条数）→ 扫描面审计（按 .gitmodules 判定子模块，源案例 10→12）；含 probe-matrix 与 guard-and-fixtures 两份参考与 12 条 Gotchas；萃取自会话 c9d91a62 | 版本下限失真、声明 0.10 但实测要求 0.11、minimum-version 该写多少、构建后端下限上调、守卫脚本漏扫目录、门槛从没被执行 | [version-floor-contract-guard/SKILL.md](version-floor-contract-guard/SKILL.md) |
| skill-junction-durability-guard | 完整Skill（v1.0.0，L1） | 用户级 Skill 目录联接的持久性守卫：D0/D1/D2/D2i/D3 五级判定（跟踪状态 × 忽略规则 × 联接目标）→ 五步只读取证（`ls-files--error-unmatch` / `status` / `check-ignore` / `grep HEAD` / blob 比对）→ 联接创建与内容提交拆为 A/B/C/D 四项独立授权 → 提交后 blob 与经目标路径双复验；含纯审计模式与 14 条 Gotchas | 联接指向的技能突然没了、目录联接悬空、用户级技能能触发但没入库、建了联接还要不要提交、git clean 会不会删技能、git clean -fdx | [skill-junction-durability-guard/SKILL.md](skill-junction-durability-guard/SKILL.md) |
| user-skill-sovereign-migration | 完整Skill（v1.3.0，L1） | 用户级 Skill 主权区原生迁移：推荐根与项目约定冲突显式确认 → 双根只读预检（实体/联接/半套副本分类，目标存在转 Update）→ 提案批准 → 原生化 frontmatter（`x-toml-ref` 为条件字段）→ 有源保真复制与 SHA256/正文比对、两侧质量门分差归因（源 65/7 warn → 目标 70/6 warn，+5 为新增 `paths`）→ 无源则携带已有设计与本轮批准交接 `skill-creator`；登记、Junction、源清理与各项 Git 操作分别授权；含 20 条 Gotchas 与 20 项安全检查清单 | 迁入 .agents/skills、为什么没放在 .agents/skills、用户级 Skill 入库、原生迁移、移入主权区、把 ~/.qoder/skills 的技能搬进仓库 | [user-skill-sovereign-migration/SKILL.md](user-skill-sovereign-migration/SKILL.md) |
| skill-guidance-correction-propagation | 完整Skill（v1.0.0，L1） | Skill 与文档规则纠错传播：冻结旧断言与新断言 → 用原句与两组同义词扫描正文、引用章节、测试夹具、测试断言与检测逻辑 → 按依赖顺序修补（权威面 → 指针 → 夹具 → 断言 → 检测）→ 覆盖守恒 → 原始退出码复跑门禁 → 既有失败与本次回归分开归因 → 按面汇报；含 3 处 Why、10 条 Gotchas 与 12 项安全检查清单；萃取自会话 a3d000e0 | 这处规则写错了、把相关文档和测试一起改、修完 references 还矛盾、测试数据固化了旧假设、门禁红了但不是本次改的 | [skill-guidance-correction-propagation/SKILL.md](skill-guidance-correction-propagation/SKILL.md) |
| markdown-first-deliverable-drafting | 完整Skill（v1.0.0，L1） | Markdown 优先交付物起草：敏感度预检定落点（私域入 playground/reports/{类型}-{主题}-{日期}/，README 索引 + 每文件 frontmatter type/source 溯源 + 相对互链）→ 低成本 Markdown 草稿 → 草稿确认门（内容与目标格式双确认后才进转换链，禁止预装重型依赖）→ 转换链先探测现成能力再降级（PDF 走仓库脚本 → weasyprint → Playwright msedge 通道免下载）→ 临时依赖隔离在交付目录 support/generated 内并收尾清理；含决策树、7 条 Gotchas 与 9 项安全清单；萃取自会话 af172fa6 | 整理成Word、转成PDF、导出文档、生成报告文件、把方案变成文档、做成文件夹交付 | [markdown-first-deliverable-drafting/SKILL.md](markdown-first-deliverable-drafting/SKILL.md) |
| ci-gate-effectiveness-audit | 完整Skill（v1.1.0，L1） | CI 门禁有效性审计：枚举 continue-on-error、allow_failure 与 shell 短路（or-true / or-exit-0）三类抑制面，先取基线再单点解除抑制，并把失败分为环境伪失败与真实缺陷；含 scan_gate_suppressions.py 与 ACT-001 实测案例 | 门禁形同虚设、步骤存在却不阻断、要删 continue-on-error、linkcheck 超时算不算真断链 | [ci-gate-effectiveness-audit/SKILL.md](ci-gate-effectiveness-audit/SKILL.md) |
| consulting-lead-magnet-discovery | 完整Skill（v1.0.0，L1） | 咨询服务引流品探索：先确认主营咨询服务与目标客群 → 比较引流形态 → 限定人工成本、答疑范围与数据使用边界 → 区分方案细化与商业验证，默认只在对话中输出待验证方案，不自动开发、落盘、发布或提交 | 咨询获客、咨询引流品、低价诊断、轻体检、9.9元产品、企微代运营咨询获客 | [consulting-lead-magnet-discovery/SKILL.md](consulting-lead-magnet-discovery/SKILL.md) |
| git-sandbox-rehearsal | 完整Skill（v1.0.0，L1） | Git 多仓沙箱预演：在真实仓库之外搭一次性沙箱，用嵌套仓、本地裸远端与父仓子模块重放「嵌套仓提交 → 推送 → 父仓 gitlink 前移 → 父仓推送」，再用 rev-list、ls-remote、ls-tree 断言结果；含沙箱手册与实测案例 | 先试跑推送、沙箱预演、git 演练、验证子模块指针、复现远端领先、不要碰真实仓库 | [git-sandbox-rehearsal/SKILL.md](git-sandbox-rehearsal/SKILL.md) |
| repo-native-skill-frontmatter-contract | 完整Skill（v1.0.0，L1） | 仓库原生 Skill frontmatter 键位契约：version、argument-hint、user-invocable、paths 必须写在顶层，缩进到 metadata 下会被质量门行首锚点漏读并静默扣 20 分；quick_validate 对原生键集退出 1 属尺子不同而非技能缺陷 | frontmatter 怎么写、质量门只有 80 分、version 放哪、quick_validate 报 Unexpected key、新建 Skill 头字段 | [repo-native-skill-frontmatter-contract/SKILL.md](repo-native-skill-frontmatter-contract/SKILL.md) |
| skill-migration-quality-delta | 完整Skill（v1.0.0，L1） | Skill 迁移质量差值归因：对源根与目标根各跑一次 check-skill-quality.py --verbose，按检查名求差集并映射到 frontmatter 或正文改动，最后按「本次引入 0 项、已消除 N 项、既有 M 项」三段陈述；含 diff_quality_warnings.py 与 ci-gate 迁移实测案例 | 迁入后掉分、65 变 70、警告是不是迁入引入、要不要回滚、质量门为什么不到 100 | [skill-migration-quality-delta/SKILL.md](skill-migration-quality-delta/SKILL.md) |
| user-level-junction-acceptance | 完整Skill（v1.0.0，L1） | 用户级目录联接三段验收：经联接路径跑 quick_validate 先对既有联接技能取基线，区分仓库原生 frontmatter 既有失败与本次引入 → 共享工作树全局 git status 哈希不等时改路径级 status、mtime 与 diff 逐路径归因 → Windows Python 不接受 Bash 的 /c/ 路径，统一改 C:/ 或 Path.home()；含 A0-A5 步骤与验收报告模板 | 联接建好了怎么验收、quick_validate 报 Unexpected key、git status 哈希变了、evals 解析 FileNotFoundError、经目标路径验证用户级技能 | [user-level-junction-acceptance/SKILL.md](user-level-junction-acceptance/SKILL.md) |
| contest-playbook | 完整Skill（v1.1.0，L1） | 通用参赛作战流程：判型（5 种赛道形态）→ 采集阶梯 L1-L7 → 编号事实六族结构化 → 抽取跨比赛通用机制判定（3 条经双样本检验）→ 资产对位 → 形态决策树 → 双轨倒排与外部依赖阻塞管理 → 合规四层自查；含规则不可得模式、传播三档分支、提交技术风险 12 项与预检门 | 我要参加 XX 比赛、帮我分析这个比赛规则、做个参赛方案、比赛怎么打、参赛材料清单、提交作品有哪些坑 | [contest-playbook/SKILL.md](contest-playbook/SKILL.md) |
| embedded-page-submit-cmd | 完整Skill（v1.1.0，L1） | 内嵌智能页代提交通道：通道权限模型判定（3 条 API 权限通道 + 1 上下文通道 + 1 交互兜底）→ 宿主 HTTP 面逆向（asar 定位/chunk 裁决/baseUrl 穷举/host 跨域）→ PropertyValue oneof 形状契约 → 三道写入闸门（用户明示确认 / 红线字段禁代填 / 幂等查重）→ 写后回读复核；含只读探针与带闸门提交脚本 | 帮我提交、代填并提交、帮我在活动页报名、这个表单替我填、permission denied、12607、写入被拒 | [embedded-page-submit-cmd/SKILL.md](embedded-page-submit-cmd/SKILL.md) |
| wechat-multi-platform-verify-cmd | 完整Skill（v1.0.0，L1） | 公众号文章多平台事实核验与发布证据包：S0 主张抽取 → S1 四级信源分层选源 → S2 逐平台取证（官方页直取/搜索快照/浏览器三通道）→ S3 主张×来源比对台账 → S4 冲突裁决与同源转载检测 → S5 证据包交付；输出 article.md + verify-<平台>.md + verify-ledger.md 三件套，含四态结论、价格口径门、邀测状态门与 10 条 Gotchas；萃取自 2026-10-23 公众号「千问Go! 我的应用」核验实战 | 核验这篇文章、多平台核验、事实核查、发布前核验、verify 台账、核验报告、证据包、这篇文章靠谱吗、投稿前查一遍 | [wechat-multi-platform-verify-cmd/SKILL.md](wechat-multi-platform-verify-cmd/SKILL.md) |
| public-value-audit | 完整Skill（v1.1.0，L1） | 公开值取值域审计：三张清单（公开面 / 标识列 / 值域构造方）交叉定位泄露面 → 收口三件套（服务端拼装目标值 + 列级授权 + 客户端白名单逐列对齐）→ 7 条可回归不变量（I1~I7，可挂 CI）；含扫描器 / 断言器 / 自检三脚本与三态对照夹具（pre-fix / p115-only / post-fix）；v1.1.0 经 4 视角对抗审查（50 条意见）修订——修复表名归一化与列名解析两处「不变量恒不触发」缺陷、新增 p115 夹具、「入参是否承载标识」判定分流、覆盖率守卫（扫不到≠没问题） | 这个字段会不会泄露用户、公开列安全吗、cover_path 会不会暴露创建者、帮我审一下权限面、值域怎么收口 | [public-value-audit/SKILL.md](public-value-audit/SKILL.md) |
| platform-review-precheck | 完整Skill（v1.0.0，L1） | 平台提审合规预检：静态提取代码实际调用的隐私接口 → 映射官方「处理的信息」类型 → 与《用户隐私保护指引》逐项对账（D1 声明覆盖调用 / D2 无死项 / D3 授权兜底 / D4 声明文件存在）；含扫描器 / 对账器 / 自检三脚本与前后对照夹具；萃取自 2026-10-26 提审被拒实战 | 提审被拒、审核不通过、代码发布审核没过、隐私保护指引怎么填、涉及收集照片手机号位置信息、提交审核被拦 | [platform-review-precheck/SKILL.md](platform-review-precheck/SKILL.md) |
| knowledge-bundle-naming-audit | 完整Skill（v1.0.0，L1） | 只读知识包命名审计：盘点并全文读取 bundle → 映射实际主题与读者任务 → 候选名三项检查（范围承诺、中英一致、误导含义）→ 独立反向审查 → 输出中文标题、英文目录名与范围或日期限定；结论标记待确认，不重命名、不改文件、不提交 | 知识包改名、bundle 名字不准、目录名与内容不符、标题范围过宽、中英命名不一致、命名审计 | [knowledge-bundle-naming-audit/SKILL.md](knowledge-bundle-naming-audit/SKILL.md) |
| specweave-slash-alias-resolution | 完整Skill（v1.0.0，L1） | Slash 别名解析：把 `/七概念` 等中文斜杠别名解析为 `.agents/commands` 指令正文、Skill 门面与两处登记行，四步有界检索后按「有门面/仅指令/未找到」三分支动作，避免仅凭运行时技能列表误判不存在；含超时 grep 降级与输出契约 | 斜杠别名、/七概念、别名解析、技能不存在、未在可用列表、指令集入口、slash alias | [specweave-slash-alias-resolution/SKILL.md](specweave-slash-alias-resolution/SKILL.md) |
| bundled-script-exit-code-ambiguity | 完整Skill（v1.0.0，L1） | 自带脚本退出码歧义判别：区分「契约检出的退出 1」与「未捕获异常返回的退出 1」（Python 未捕获异常固定退出 1，恰是校验脚本最常用的检出码），用退出码 + 语义标记 + 预期命中数三断言把「PASS 但其实是崩了」与真检出分开；含契约清单化预检、歧义码对照、修复模式与复跑证据要求 | 退出码对了但行为不对、Traceback 也是退出 1、目录路径报 IsADirectoryError、夹具只看退出码、PASS 但其实是崩了、异常冒充契约码 | [bundled-script-exit-code-ambiguity/SKILL.md](bundled-script-exit-code-ambiguity/SKILL.md) |
| stale-read-edit-reconciliation | 完整Skill（v1.0.0，L1） | 读后写前漂移恢复：既有文件读完后、写入前被并发会话改写时，先重读现盘，按标题级差集把已获批方案裁成只补缺失项，版本号从现盘顺延，写入后复跑门禁并回报并发事实；含漂移探针脚本、恢复六步与停手条件 | 读完后文件被改了、Edit 报 0 occurrences、版本号被前移、用户级路径变成联接、另一会话动了同一文件、按已确认方案写入却写入失败 | [stale-read-edit-reconciliation/SKILL.md](stale-read-edit-reconciliation/SKILL.md) |
| windows-deletion-blast-radius-attribution | 完整Skill（v1.0.0，L1） | Windows 误删影响面定性：根级清单差异、权限与报错证据、服务写入判别、按 SID 查回收站四步交叉印证，输出「已确认删除 / 已确认完好 / 未验证」三段结论与可恢复性判定；含删除前置断言与安全拦截处置 | 到底删了什么、核对某目录是不是真没了、误删范围有多大、回收站能不能恢复、rm -rf 打到盘根了 | [windows-deletion-blast-radius-attribution/SKILL.md](windows-deletion-blast-radius-attribution/SKILL.md) |
| windows-temp-fixture-teardown-safety | 完整Skill（v1.0.0，L1） | Windows 临时夹具建测清安全约束：单个 Python 进程内 `tempfile.mkdtemp` 建、断言、`shutil.rmtree` 清理，禁止把 cygpath/sed/变量替换得到的路径交给 `rm -rf`，删除前打印并断言解析后的绝对路径前缀与层级深度；含五条硬规则、标准模板与坏味道扫描 | 建临时夹具、跑受控删除验证、清理探针目录、清理命令里出现变量拼接路径 | [windows-temp-fixture-teardown-safety/SKILL.md](windows-temp-fixture-teardown-safety/SKILL.md) |

### 工作流门面（7个）

| Skill名称 | 类型 | 功能描述 | 核心触发词 | SKILL.md路径 |
|-----------|------|---------|-----------|-------------|
| source-code-to-okf-wiki | 工作流门面 | 源码阅读→OKF Wiki 生成（R→I→E→V→C 五阶段，信源先行、分批生成、Grep级API验证，杜绝虚构API） | 源码学习、读源码、源码阅读、生成Wiki、OKF Wiki、源码转文档、深度学一个库 | [source-code-to-okf-wiki/SKILL.md](source-code-to-okf-wiki/SKILL.md) |
| blog-article-to-okf-wiki | 工作流门面 | 博文/资讯文章→OKF 知识包转化（七阶段：敏感度预检→骨架两问→归属决策树→F编号事实+P0核验勘误四清单→三层拆分→信源先生成→对抗审查），13篇实战验证 | 博文转化、公众号文章、微信文章、转知识包、OKF bundle、OKF wiki、文章转文档、资讯转知识库 | [blog-article-to-okf-wiki/SKILL.md](blog-article-to-okf-wiki/SKILL.md) |
| scanned-book-to-okf-wiki | 工作流门面（v2.0.0，L2 双案例验证） | 扫描版版权书籍→OKF Wiki 教程转化（六工序：route决策前置→文本层可信度判定（覆盖纯图像与扫描图+噪声OCR混合型）+逐章通读页码映射→深度摘要→原创改写（含主张分层）→合规声明契约化（含计数口径）→V审查实证对账（含中间摘要回图核验））；案例1财商寓言、案例2《魔力》练习册 | 扫描版书籍转教程、书转Wiki、摘要替代转录、扫描版版权材料、书转知识包、混合型PDF | [scanned-book-to-okf-wiki/SKILL.md](scanned-book-to-okf-wiki/SKILL.md) |
| ⭐ role-model-methodology | 工作流门面（v1.1.0） | 榜样人物方法论萃取与正面解读（四级事实分层 A权威/B百科/C转述/D推断 → 三框架诊断 → 证据桥接审查（时间线核对 + ★~★★★★★五档强度）→ 六步解读法 → 23条交付门禁）；含伦理四条约束（创伤不是教材/他人不是论据/隐私不评判/幸存者偏差前置）；案例：2026-10-03 三人榜样知识包（陶行知/游本昌/胡歌，61文档/254条四级事实/3框架） | 榜样学习、人物解读、正面解读师、名人方法论、人物关联洞察、榜样学习路径、终身学习者、怎么学名人、人物知识包、向谁学习、以某人为榜样 | [role-model-methodology/SKILL.md](role-model-methodology/SKILL.md) |
| mindfulness-positivity | 工作流门面（v1.0.0） | 正念 vs 正面（积极心态）概念辨析与整合：四场景决策树（概念问答/内容产出/自我调节方案/知识包沉淀）+ 七维度辨析框架 + 「先接纳后重构」四步整合法 + 心理健康安全边界（不诊断/不替代治疗/危机转介/证据分级）；L2 知识底座 sc-20261003-mindfulness-positivity（22事实/3洞察/1模式） | 正念、正面、积极心态、正能量、mindfulness、positive thinking、习得性乐观、有毒正能量、toxic positivity、先接纳后重构、正念和积极有什么区别 | [mindfulness-positivity/SKILL.md](mindfulness-positivity/SKILL.md) |
| dao-san-triads | 工作流门面（v1.0.0） | 「三」之本体论与三元组诊断：六类「三」解释谱系（和气/天地人/一+天地/模式/三合生物/本体显现）+ **第五义「三=关系位」统一模型** + 奥古斯丁三分法与最强反驳 + 时态检验诊断法 + 两组行动三元组四元关联 + **七条可当场判定的生存指南**（≤1200字）+ 「三之位」可迁移模式（5反模式/3问检验/L1-draft）+ 《老子》版本纪律（甲乙本/今本/楚简本不得混称）；L2 知识底座 sc-20261003-dao-san-yuan（50事实/4洞察/1模式/9条审查） | 三生万物、道生一、二生三、三之位、三元组、过去现在未来、时间三分、奥古斯丁三分法、一分为三、真问题真需求真目标、品质技能身份、生存指南、行动准则、极简原则、二选一怎么办、自我诊断、古典哲学概念 | [dao-san-triads/SKILL.md](dao-san-triads/SKILL.md) |
| persona-brand-positioning | 工作流门面（v1.0.0） | 人格化品牌定位诊断：画层级图（品牌→子模块→子频道，避免子模块被当成品类招牌）→ 理解命名哲学三层（哲学/美学/人格）→ 补桥不改名（靠简介与页面内容承接搜索权重）→ 三环闭环按人→学→钱顺序建；含 6 条反模式、9 项安全检查清单、6 条无报错码隐性陷阱（Gotchas）、预览确认与幂等复用机制；L2 知识底座 sc-20261026-daode-masterxiong（26事实/3洞察/1模式/9行动项） | 品牌定位诊断、优化小程序简介、品牌名怎么取、人格化IP、搜索权重、简介怎么写、品牌名要不要加品类词、子站命名 | [persona-brand-positioning/SKILL.md](persona-brand-positioning/SKILL.md) |

### Trae 内置工作流 Skill（2个，来自 external/doutops）

| Skill名称 | 类型 | 功能描述 | 核心触发词 | SKILL.md路径 |
|-----------|------|---------|-----------|-------------|
| TRAE-plan-mode | 内置工作流 | 有界仓库变更的规划-批准-执行工作流（单一实施计划+一次批准门，批准前禁写），计划落盘 `.trae/documents/` | 规划、实施计划、plan mode、计划批准、先规划后执行、有界变更 | [TRAE-plan-mode/SKILL.md](TRAE-plan-mode/SKILL.md) |
| TRAE-spec-mode | 内置工作流 | 复杂变更端到端规范工作流（Specify→Plan→Approve→Implement→Review 五阶段，spec/tasks/review 三产物落盘 `.trae/specs/`，rule/rubric 验收词汇+独立 Review 门，支持中断恢复） | 规范模式、spec mode、需求澄清、验收标准、任务队列、独立审查、恢复中断工作流 | [TRAE-spec-mode/SKILL.md](TRAE-spec-mode/SKILL.md) |

> 两者互为选型路由：有界变更→plan，复杂/高影响/跨会话→spec。派生自 Trae 内置 doutops skill（`external/` 非 git 目录），已适配为中文五要素版，source 字段记录原始路径；Trae 同步覆盖后以本仓库版本为准。

### 内置镜像 Skill（21个，来自 Trae IDE builtin 镜像）

Trae IDE 内置通用技能镜像入库（扁平去重取最全版，2026-09-03 导入）。来源目录 external/dao/xinzo/.trae-cn/builtin/{work,global,design,code}，每个 SKILL.md 的 frontmatter `source` 字段标注原始路径；镜像保留技能包原貌（含 LICENSE/scripts/assets），不随 Trae 同步改写。导入清单见 .trae/specs/workspace-governance/import-builtin-skills/migration-manifest.md。

skill-creator 为 2026-10-24 刷新整合版（正文取 builtin scope 默认版，eval 工具链与 bundled 资源取用户级全量技能包）；其余内置镜像技能保持原貌。

**work 家族：办公文档（8个）**

| 技能名 | 来源家族 | 功能描述 | SKILL.md路径 |
|--------|---------|---------|-------------|
| doc-writing-guide | work（办公文档） | 文档/内容写作主技能（PRD、技术提案、研究报告、竞品分析、手册等），管理意图解读、体裁格式选择、写作风格校准、内容结构编排与子场景路由 | [SKILL.md](doc-writing-guide/SKILL.md) |
| docx | work（办公文档） | .docx 专业文档创建/编辑/分析：修订追踪（tracked changes）、批注、格式保留与文本提取 | [SKILL.md](docx/SKILL.md) |
| html-deck | work（办公文档） | 从零创建动画丰富的 HTML 演示文稿（自包含单 HTML 文件、多端像素级一致）；用户说 PPT/ppt 时路由至 pptx，交付物恒为 HTML | [SKILL.md](html-deck/SKILL.md) |
| html-report | work（办公文档） | 创建除幻灯片外的任意自包含 HTML 交付物：研究报告、白皮书、PRD、仪表盘、作品集、简历、邮件模板、数据可视化等，零外部依赖 | [SKILL.md](html-report/SKILL.md) |
| pdf | work（办公文档） | PDF 综合处理工具包：提取文本与表格、创建新 PDF、合并/拆分文档、表单处理，支撑规模化程序化处理与分析 | [SKILL.md](pdf/SKILL.md) |
| pptx | work（办公文档） | .pptx 演示文稿创建、编辑与分析：新建、内容修改、版式调整、批注与演讲者备注等 | [SKILL.md](pptx/SKILL.md) |
| research-guide | work（办公文档） | 研究/分析场景主技能：检索查证、技术/产品对比、竞品分析、研究报告撰写，提供信源分级、交叉验证方法论、搜索范式与子场景路由 | [SKILL.md](research-guide/SKILL.md) |
| xlsx | work（办公文档） | 电子表格为主输入/输出时的技能：读写/编辑/修复 .xlsx/.xlsm/.csv/.tsv、新建表格、格式转换、清洗杂乱数据；交付物必须为表格文件 | [SKILL.md](xlsx/SKILL.md) |

**global 家族：通用（6个）**

| 技能名 | 来源家族 | 功能描述 | SKILL.md路径 |
|--------|---------|---------|-------------|
| digital-avatar-creator | global（通用） | 创建数字分身（Avatar）技能的强制工具：生成以自主 SubAgent 运行、按专长独立处理用户请求的虚拟角色/助手 | [SKILL.md](digital-avatar-creator/SKILL.md) |
| dynamic-ui | global（通用） | 在文字回答旁内联展示可视化内容（图表、架构图、交互 demo、对比分析），仅当紧凑可视化使回答更清晰时使用；不用于网站/应用/报告/看板/幻灯片 | [SKILL.md](dynamic-ui/SKILL.md) |
| TRAE-browseruse | global（通用） | 浏览器自动化指南：浏览网站、访问 URL、抓取网页内容、测试前端 UI 及多步交互（点击、验证元素、填写表单） | [SKILL.md](TRAE-browseruse/SKILL.md) |
| TRAE-browseruse-external | global（通用） | 在用户本机 Chrome（外部浏览器）中自动化任务（经 TRAE Chrome 扩展路由 native 模式），响应「用我的浏览器打开」类请求 | [SKILL.md](TRAE-browseruse-external/SKILL.md) |
| TRAE-code-mode-orchestrator | global（通用） | Code Mode（Exec）使用模式：并行扇出、JS 变换流水线、条件分支、循环直到条件、多源聚合等单脚本多工具编排场景 | [SKILL.md](TRAE-code-mode-orchestrator/SKILL.md) |
| TRAE-computer-use | global（通用） | 通过 Computer Use 控制本地应用 UI：读取屏幕并点击、输入、滚动、拖拽、按键、设置值，高风险操作前需用户确认 | [SKILL.md](TRAE-computer-use/SKILL.md) |

**design 家族：设计（4个）**

| 技能名 | 来源家族 | 功能描述 | SKILL.md路径 |
|--------|---------|---------|-------------|
| design-library-creator | design（设计） | 创建/扩展/精炼专业设计库与设计系统（结构化 token 架构、主题创建）；仅显式提及设计系统术语或提供 design-spec bundle 时触发，素材/页面类意图路由至 solo-design | [SKILL.md](design-library-creator/SKILL.md) |
| solo-design | design（设计） | 设计网站页面、UI 界面、原型、页面级视觉系统及既有 .design 项目改版；位图编辑/海报生成/设计库分别路由至三姊妹技能 | [SKILL.md](solo-design/SKILL.md) |
| solo-graphic-generation | design（设计） | 位图优先静态视觉资产生成（海报、横幅、KV、封面、插画、产品图、图片批次，无需 HTML）；生成前须确认输出尺寸 | [SKILL.md](solo-graphic-generation/SKILL.md) |
| solo-image-edit | design（设计） | 以图生图（image-to-image）编辑既有位图，所有保留结果写回所属 .design 画布 | [SKILL.md](solo-image-edit/SKILL.md) |

**code 家族：基建（2个）**

| 技能名 | 来源家族 | 功能描述 | SKILL.md路径 |
|--------|---------|---------|-------------|
| feedback | code（基建） | 仅用于显式 TRAE 反馈提交意图（/feedback 或宿主注入 Use Skill: feedback），将反馈转化为最小 feedback JSON；仅提及 feedback/bug 不触发 | [SKILL.md](feedback/SKILL.md) |
| TRAE-product-knowledge | code（基建） | TRAE 品牌与官方产品知识问答：产品差异、TraeCode/TraeWork/CLI/Plugin 入口、能力、MCP、Skills、官方文档链接；不用于普通编码问题 | [SKILL.md](TRAE-product-knowledge/SKILL.md) |

**trae 家族：默认（1个）**

| 技能名 | 来源家族 | 功能描述 | SKILL.md路径 |
|--------|---------|---------|-------------|
| skill-creator | trae（默认） | 技能创建/更新/安装向导：Trae 项目级与全局技能目录落位、frontmatter 与正文结构规范、校验与反模式清单；附 eval 工具链与基准测试（评估循环、描述触发词优化、报告生成） | [SKILL.md](skill-creator/SKILL.md) |

### 设计库镜像 Skill（16个，来自 Trae IDE design_libraries 镜像）

Trae IDE 内置设计系统库完整归档（2026-09-03 导入），来源目录 external/dao/xinzo/.trae-cn/design_libraries（只读）。每个库整目录自包含（token CSS/组件 JSON/预览 HTML/UI Kit 全量内嵌），SKILL.md frontmatter `source` 字段标注原始路径；`__MACOSX/` 元数据与 `.DS_Store` 已排除。归档清单见 .trae/specs/workspace-governance/design-library-archive/migration-manifest.md。

| 技能名 | 品牌/系统 | 功能描述 | SKILL.md路径 |
|--------|---------|---------|-------------|
| 21th-design | 21th | 21th 分析仪表盘设计系统（明/暗双主题、mono 排版、方形几何、偏移阴影、电光蓝点缀）：生成仪表盘界面与资产的品牌化 UI | [SKILL.md](21th-design/SKILL.md) |
| barbie-design | Barbie | Barbie 俏皮光泽仪表盘设计系统：品牌化界面生成（色彩/字体/阴影/间距/组件规格） | [SKILL.md](barbie-design/SKILL.md) |
| claude-design-system-design | Claude | Claude 设计系统（Anthropic 美学，暖调编辑风、对话优先 UI）：完整主题 token、组件规格、预览与 UIKit 引用 | [SKILL.md](claude-design-system-design/SKILL.md) |
| doubao-design | Doubao | 豆包极简冷调 AI 仪表盘设计系统：token/组件规格/预览/UI kit 引用 | [SKILL.md](doubao-design/SKILL.md) |
| golden-time-design | Golden Time | Golden Time 暖调编辑风高端仪表盘设计系统：完整 token/组件/预览/UI kit，已修复为自包含相对路径 | [SKILL.md](golden-time-design/SKILL.md) |
| google-design | Google | Google 简洁分析型仪表盘设计系统：设计准则/色彩/字体/组件参考 | [SKILL.md](google-design/SKILL.md) |
| minimal-dashboard-design | Minimal Dashboard | 极简仪表盘设计系统：色彩/字体/token/组件参考/预览/dashboard UI kit | [SKILL.md](minimal-dashboard-design/SKILL.md) |
| motionfit-design | MotionFit | MotionFit 设计系统：色彩/字体/字体族/组件参考/UI kit（dashboard 原型） | [SKILL.md](motionfit-design/SKILL.md) |
| nerv-design | Nerv | Nerv 未来感高对比运维仪表盘品牌：设计准则/色彩/字体/组件参考/UI kit | [SKILL.md](nerv-design/SKILL.md) |
| nimbus-core-design | Nimbus Core（TraeCode） | TraeCode/Nimbus Core 暗色优先产品设计系统（23 组件/2 UI Kit/115 SVG 图标）：token、组件契约、预览与架构文档 | [SKILL.md](nimbus-core-design/SKILL.md) |
| pinguo-apple-design | Pinguo（苹果） | Pinguo 消费影像产品生态（Apple 启发克制美学）：设计准则/色彩/字体/组件参考/UI kit 模式 | [SKILL.md](pinguo-apple-design/SKILL.md) |
| tiktok-design | TikTok | 抖音社交视频平台设计：按场景（移动 feed/网页/编辑）或复用内置 UI kit/组件，token-first & icon-first | [SKILL.md](tiktok-design/SKILL.md) |
| trae-work-design | TraeWork | TraeWork 专业工作台设计系统：完整 token/组件/UI kit（scaffold/组件 CSS/图标渲染器） | [SKILL.md](trae-work-design/SKILL.md) |
| vercel-design-library-design | Vercel | Vercel 设计系统：色彩/字体/资产/UI kit（dashboard 原型） | [SKILL.md](vercel-design-library-design/SKILL.md) |
| yuanli-design-system | Yuanli（源力） | 源力设计系统（Volcengine，PRD 驱动中文生成）：PRD→页面生成规则 + 完整 token/组件/UI kit | [SKILL.md](yuanli-design-system/SKILL.md) |
| vibecamp-design | Vibecamp | Vibecamp 大胆编辑风 dashboard 产品：设计准则/色彩/字体/组件参考/UI kit | [SKILL.md](vibecamp-design/SKILL.md) |

### TeleAgent 平台镜像 Skill（1个）

TeleAgent（星辰超级智能体）平台技能镜像入库（2026-10-21 首次导入）。来源为 TeleAgent 用户级技能目录，SKILL.md frontmatter `source` 字段标注来源与归档日期；镜像保留技能包原貌，不随平台版本演进改写。

| 技能名 | 来源家族 | 功能描述 | SKILL.md路径 |
|--------|---------|---------|-------------|
| ui-screenshot-review | TeleAgent 平台 | Web 页面/本地应用 UI 视觉验证工作流：多级降级截图（交互浏览 → headless Chromium → 静态渲染等价）+ 六维度结构化评审（1–5 分）+「打磨→复截图→复评审」迭代闭环 | [SKILL.md](ui-screenshot-review/SKILL.md) |

### 脚本命令门面（16个）

| Skill名称 | 类型 | 对应脚本 | 核心触发词 | SKILL.md路径 |
|-----------|------|---------|-----------|-------------|
| compose-overlay-ops | 应用CLI门面 | invoke quant.*/native.*/monetize.*（apps/containers/client，podman-compose 子进程层） | 启动/重建 native-dev、onnx-quantized、agent-monetize 叠加栈、native.up/build/smoke、容器 Exited(0)、netavark nft、Jupyter 保存 Errno 13、WSL 发行版回收、tuna 构建叠加镜像 | [compose-overlay-ops/SKILL.md](compose-overlay-ops/SKILL.md) |
| jpman-podman-ops | 应用CLI门面 | jpman（apps/containers/jupyter-podman-rootless/bin，bash/cmd/ps1 三版本） | jpman、启动jupyter容器、podman machine、工作区挂载、容器WARN分诊、fuse device、rootless排障、WSL保活、rebuild、crun pids not available、non-systemd cgroup、WSL3 systemd=true+argv0 shim 修复 | [jpman-podman-ops/SKILL.md](jpman-podman-ops/SKILL.md) |
| openkylin-wsl-devkit | 应用CLI门面 | okw（apps/dev-tools/openkylin-wsl-devkit，Python 零运行时依赖 CLI，七组命令） | okw、openKylin WSL 导入/验收、openKylin 发行版内装 podman、okw podman/compose/image 排错、xuan-compose/xc 引导、openKylin 开发容器镜像、deb/dput 脚手架、okw ref、修改 openkylin-wsl-devkit 源码 | [openkylin-wsl-devkit/SKILL.md](openkylin-wsl-devkit/SKILL.md) |
| docker-cache-cmd | 脚本门面 | docker-cache（bash） | 保存镜像、缓存Docker镜像、docker缓存、镜像缓存、加载镜像、WSL重置恢复、docker save/load、镜像本地缓存 | [docker-cache-cmd/SKILL.md](docker-cache-cmd/SKILL.md) |
| docker-wsl-bridge-cmd | 跨Shell编排 | wsl+podman命令编排 | 镜像转WSL、docker镜像导入WSL、镜像转rootfs、podman export转wsl、WSL重置后恢复开发环境、docker-wsl-bridge | [docker-wsl-bridge-cmd/SKILL.md](docker-wsl-bridge-cmd/SKILL.md) |
| wsl-ops-cmd | 脚本门面 | compress-wsl-vhdx.ps1、Restart-WslDockerGpu.ps1、setup-wsl-docker-gpu.sh、cleanup-trae-cache.ps1 | WSL磁盘清理、vhdx压缩、盘爆红、Docker GPU不可用、--gpus报错、nvidia-container-toolkit、wsl --shutdown后Docker不自启、wsl.conf boot、setsid dockerd、Trae缓存清理、fstrim、孤儿卷/build cache清理 | [wsl-ops-cmd/SKILL.md](wsl-ops-cmd/SKILL.md) |
| link-check-cmd | 脚本门面 | check-links.py | 链接检查、断链修复、验证链接、提交前检查 | [link-check-cmd/SKILL.md](link-check-cmd/SKILL.md) |
| atomization-finalize-cmd | 脚本门面 | finalize-atomization.py | 原子化收尾、一键收尾、文件移动后处理、断链修复导航更新 | [atomization-finalize-cmd/SKILL.md](atomization-finalize-cmd/SKILL.md) |
| submodule-atomization-finalize-cmd | 脚本门面（子模块补位） | 自带 scripts/check_doc_links.py（GitHub slug 门禁）+ 六步收尾 SOP | 子模块文档原子化收尾、projects 下文档拆分收尾、子模块断链/中文锚点检查、子模块文件移动引用核对、事实守恒 diff | [submodule-atomization-finalize-cmd/SKILL.md](submodule-atomization-finalize-cmd/SKILL.md) |
| docgen-cmd | 脚本门面 | docgen.py | 更新导航、刷新看板、生成文档索引、docgen、更新README | [docgen-cmd/SKILL.md](docgen-cmd/SKILL.md) |
| ci-check-cmd | 脚本门面 | ci-check.ps1/ci-check.sh | CI检查、提交前检查、综合检查、流水线检查、全量检查、pre-commit | [ci-check-cmd/SKILL.md](ci-check-cmd/SKILL.md) |
| check-duplication-cmd | 脚本门面 | check-duplication.py | 重复代码、重复检查、代码重复、提取共享库、DRY检查、脚本重复 | [check-duplication-cmd/SKILL.md](check-duplication-cmd/SKILL.md) |
| knowledge-graph-generator | 脚本门面 | generate-graph.py | 知识图谱、knowledge graph、概念关系可视化、交互式知识图谱、节点关系网络 | [knowledge-graph-generator/SKILL.md](knowledge-graph-generator/SKILL.md) |
| artifact-consistency-audit | 脚本门面 | 复用 check-links.py + check-source-traceability.py（无新建脚本） | 核验一致性、复验、体检、覆盖率核对、引用是否忠实、有无遗漏、修补后复验 | [artifact-consistency-audit/SKILL.md](artifact-consistency-audit/SKILL.md) |
| docs-as-product-cmd | 脚本门面 | docs-as-product.py | 文档即产品、docs-as-product、Diátaxis四型分区、文档质量门G1-G4/V门、sphinx-build -W、元数据漂移F-021、读者契约、文档指标M1-M5 | [docs-as-product-cmd/SKILL.md](docs-as-product-cmd/SKILL.md) |
| wsl-vhdx-compact-cmd | 脚本门面 | compact-vhdx-with-baseline.ps1；失败自动降级 compress-wsl-vhdx.ps1（双方案自动降级 + BaselineOnly dry-run 只读基线 + RestorePodman/RestoreOriginalState 原态恢复 + Win32 FreeGiB 数值闭环） | 压缩WSL磁盘、vhdx回收、ext4.vhdx太大、wsl --manage --compact、宿主机FreeGiB核对、VHDX前后基线、podman-machine-default vhdx压缩、openKylin WSL磁盘回收、C/D盘爆红 清WSL、wsl vhdx瘦身、Win32_LogicalDisk 对账 | [wsl-vhdx-compact-cmd/SKILL.md](wsl-vhdx-compact-cmd/SKILL.md) |

## 模板

| 文件 | 用途 | 路径 |
|------|------|------|
| SKILL-TEMPLATE.md | Skill创建模板，包含五要素模型骨架 | [SKILL-TEMPLATE.md](SKILL-TEMPLATE.md) |

## Skill 结构规范

每个Skill遵循以下目录结构（遵循 vendor skill-creator 规范）：

```
.agents/skills/<skill-name>/
├── SKILL.md          # 必需：技能定义（YAML frontmatter + Markdown）
├── scripts/          # 可选：可执行脚本
├── references/       # 可选：参考文档（按需加载）
└── assets/           # 可选：模板、图标等资源
```

SKILL.md 必须包含五要素：
1. **Trigger-Ready Description**：触发就绪描述（YAML frontmatter 中的 description）
2. **Decision Tree**：方案决策树（多方案时必须提供）
3. **Progressive Disclosure**：渐进式披露（正文≤500行，低频内容引用外部文档）
4. **Why-Explanation**：设计意图解释（关键规则后用 `> **为什么？**` 说明）
5. **Safety Checklist**：安全检查清单（写操作必须包含dry-run/幂等/验证）

## 发现机制（L0-L3）

Skill通过四层发现机制被Agent发现：

```mermaid
flowchart LR
    L0["L0: ONBOARDING.md<br/>入门快速路由"] --> L1["L1: capability-registry.md<br/>全量能力索引"]
    L1 --> L2["L2: 语义匹配<br/>关键词/触发词匹配"]
    L2 --> L3["L3: 本目录 SKILL.md<br/>详细操作指南"]
```

- **L0 入口**：[ONBOARDING.md](../ONBOARDING.md) — 新会话快速开始
- **L1 索引**：[capability-registry.md](../capability-registry.md) — 全量能力静态索引
- **L3 详情**：各SKILL.md — 具体操作步骤与安全检查

## 创建新 Skill

1. 复制 [SKILL-TEMPLATE.md](SKILL-TEMPLATE.md) 到 `<skill-name>/SKILL.md`
2. 阅读 [skill-development.md](../rules/skill-development.md) 了解SpecWeave补充规范
3. 阅读 vendor [skill-creator/SKILL.md](../../vendor/flexloop/apps/chaos/.agents/skills/skill-creator/SKILL.md) 了解权威方法论
4. 完成后运行 `python .agents/scripts/check-skill-quality.py <skill-name>` 验证质量
5. 更新本索引和 [capability-registry.md](../capability-registry.md)

## Changelog

完整变更记录见 [CHANGELOG.md](CHANGELOG.md)。
