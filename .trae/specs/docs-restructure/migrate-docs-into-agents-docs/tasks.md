# Tasks

- [x] Task 1: 完成迁移前盘点与第一性分类决策
  - [x] SubTask 1.1: 盘点当前 `docs/` 目录结构、文件数量、主要分类与入口文档
  - [x] SubTask 1.2: 盘点当前 `.agents/docs/` 目录结构，识别需要保留的智能体专属目录边界
  - [x] SubTask 1.3: 形成目标结构决策：原 `docs/` 内容直接迁移到 `.agents/docs/`，不得形成 `.agents/docs/docs/`
  - [x] SubTask 1.4: 识别仓库内所有引用原 `docs/` 根路径的文件与配置
  - [x] SubTask 1.5: 明确迁移后的人类文档边界声明方案与智能体专属文档保留策略
  - [x] SubTask 1.6: 按 spec 中的目录归类决策表，为现有目录建立默认归属清单

- [x] Task 2: 建立备份与迁移基线
  - [x] SubTask 2.1: 为原 `docs/` 生成完整备份副本
  - [x] SubTask 2.2: 记录迁移前文件总数、相对路径清单、文件大小与内容哈希
  - [x] SubTask 2.3: 记录关键入口文件与导航文件的原始引用关系
  - [x] SubTask 2.4: 确认备份与基线完成后再进入迁移阶段

- [x] Task 3: 执行整目录迁移到 `.agents/docs/`
  - [x] SubTask 3.1: 在 `.agents/docs/` 下准备目标承载位置
  - [x] SubTask 3.2: 将根目录 `docs/` 的内容迁移到 `.agents/docs/`，不得额外生成嵌套根目录
  - [x] SubTask 3.3: 校验迁移后的目录树与原始目录树一致
  - [x] SubTask 3.4: 基于基线比对文件数量、相对路径映射与内容哈希
  - [x] SubTask 3.5: 校验迁移结果中不存在 `.agents/docs/docs/` 路径

- [ ] Task 4: 全量修复路径、链接与配置引用
  - [ ] SubTask 4.1: 更新仓库内所有指向原 `docs/` 的 Markdown 相对路径引用
  - [ ] SubTask 4.2: 更新 `AGENTS.md`、`.agents/` 规则/协议/索引文档中的路径说明
  - [ ] SubTask 4.3: 更新 `.trae/specs/` 中引用主仓库文档路径的 spec/checklist/tasks
  - [ ] SubTask 4.4: 修复因目录深度变化而失效的跨文件相对路径
  - [ ] SubTask 4.5: 确认仓库内不再残留失效的旧 `docs/` 根路径引用
  - [ ] SubTask 4.6: 补充 `.agents/docs/` 的边界说明文件或索引声明，明确人类文档与智能体专属文档的语义分层
  - [ ] SubTask 4.7: 按 spec 中定义的最小模板创建或更新 `.agents/docs/README.md`，至少覆盖目录定位、适用对象、维护原则、禁止事项、快速查找入口
  - [ ] SubTask 4.8: 将目录归类决策表或等效归类摘要同步到 `.agents/docs/README.md` 或 AGENTS 路由入口

- [ ] Task 5: 验证人类访问与智能体读取双通路
  - [ ] SubTask 5.1: 抽查 `.agents/docs/` 下的人类文档入口、目录导航与典型交叉链接
  - [ ] SubTask 5.2: 抽查 `.agents/docs/` 下智能体专属目录，确认未被错误覆盖或混入
  - [ ] SubTask 5.3: 验证“人类文档”与“智能体专属目录”在语义上可区分
  - [ ] SubTask 5.4: 验证迁移后的目录说明足以让维护者判断文件归属，不依赖历史记忆
  - [ ] SubTask 5.5: 对照 README 模板检查五个最小章节是否齐全、措辞是否能直接指导后续维护
  - [ ] SubTask 5.6: 对照目录归类决策表抽查至少 5 个目录或文件，确认默认归属与实际用途一致
  - [ ] SubTask 5.7: 抽查样本优先覆盖 spec 预设的 5 类样本类型，并记录每个样本的路径、默认归属、判定依据、是否需要补充边界说明
  - [ ] SubTask 5.8: 至少包含 1 个混合型样本，验证升级判断规则是否触发且可落地
  - [ ] SubTask 5.9: 按 spec 中定义的 Markdown 表格模板输出抽查记录，保证字段完整且可复查

- [ ] Task 6: 运行程序化校验并收尾
  - [ ] SubTask 6.1: 运行链接校验工具，确认迁移后无断链
  - [ ] SubTask 6.2: 运行文件迁移校验工具，确认无遗漏、无重复、无损坏
  - [ ] SubTask 6.3: 修复校验发现的问题并重新验证
  - [ ] SubTask 6.4: 清理迁移过程中不再需要的旧路径残留与临时状态

- [ ] Task 7: 修复 2026-07-15 迁移验收失败项并完成复验
  - [ ] SubTask 7.1: 修复仓库内仍残留的旧 `docs/` 根路径引用，至少覆盖 `AGENTS.md`、`.agents/` 路由/规则文档与相关 `.trae/specs/`
  - [ ] SubTask 7.2: 调整链接校验范围或清理 `.meta/backup/` 等备份残留，确保 `check-links.py` 面向当前有效工作树执行且结果可通过
  - [ ] SubTask 7.3: 修复 `repo-check` 当前暴露的仓库合规问题，消除外部目录与命名规则导致的阻断项
  - [ ] SubTask 7.4: 重新定义并补齐“迁移完整性”校验口径，区分允许的路径修复改动与真正的内容损坏，再复核 `.agents/docs/` 全量文件
  - [ ] SubTask 7.5: 复跑 `ci-check.ps1`、`check-links.py` 与迁移完整性校验，通过后再回填 Task 4-6 与 `checklist.md`

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 depends on Task 2
- Task 4 depends on Task 3
- Task 5 depends on Task 4
- Task 6 depends on Task 4

# 可并行任务组
- Task 4 的 SubTask 4.1、4.2、4.3 可按引用类型并行处理
- Task 5 可与 Task 6 的首轮校验交叉推进，但最终验收必须等待 Task 6 完成
- Task 7 的 SubTask 7.1、7.2、7.3 可并行收敛，但 7.5 必须等待前三项完成

# 验收说明
- 2026-07-15 全量验证未通过，Task 4-6 暂不勾选。
- 失败依据 1：`python .agents/scripts/check-links.py` 失败，报告 `6291` 个本地断链，含大量旧路径与目录链接问题。
- 失败依据 2：`powershell -ExecutionPolicy Bypass -File .agents/scripts/ci-check.ps1` 失败，阻断于仓库合规检查。
- 失败依据 3：对照 `artifacts/docs-baseline-manifest.json` 的当前完整性复核显示：基线 `2683` 个文件虽无缺失，但存在 `2353` 个哈希差异，需区分路径修复引入的预期改动与非预期损坏后方可判定通过。
