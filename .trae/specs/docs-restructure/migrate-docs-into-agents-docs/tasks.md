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

- [x] Task 4: 全量修复路径、链接与配置引用
  - [x] SubTask 4.1: 更新仓库内所有指向原 `docs/` 的 Markdown 相对路径引用
  - [x] SubTask 4.2: 更新 `AGENTS.md`、`.agents/` 规则/协议/索引文档中的路径说明
  - [x] SubTask 4.3: 更新 `.trae/specs/` 中引用主仓库文档路径的 spec/checklist/tasks
  - [x] SubTask 4.4: 修复因目录深度变化而失效的跨文件相对路径
  - [x] SubTask 4.5: 确认迁移范围内不再残留失效的旧 `docs/` 根路径引用
  - [x] SubTask 4.6: 补充 `.agents/docs/` 的边界说明文件或索引声明，明确人类文档与智能体专属文档的语义分层
  - [x] SubTask 4.7: 按 spec 中定义的最小模板创建或更新 `.agents/docs/README.md`，至少覆盖目录定位、适用对象、维护原则、禁止事项、快速查找入口
  - [x] SubTask 4.8: 将目录归类决策表或等效归类摘要同步到 `.agents/docs/README.md` 或 AGENTS 路由入口

- [x] Task 5: 验证人类访问与智能体读取双通路
  - [x] SubTask 5.1: 抽查 `.agents/docs/` 下的人类文档入口、目录导航与典型交叉链接
  - [x] SubTask 5.2: 抽查 `.agents/` 下智能体专属目录与 `.agents/docs/` 边界，确认未被错误覆盖或混入
  - [x] SubTask 5.3: 验证“人类文档”与“智能体专属目录”在语义上可区分
  - [x] SubTask 5.4: 验证迁移后的目录说明足以让维护者判断文件归属，不依赖历史记忆
  - [x] SubTask 5.5: 对照 README 模板检查五个最小章节是否齐全、措辞是否能直接指导后续维护
  - [x] SubTask 5.6: 对照目录归类决策表抽查至少 5 个目录或文件，确认默认归属与实际用途一致
  - [x] SubTask 5.7: 抽查样本优先覆盖 spec 预设的 5 类样本类型，并记录每个样本的路径、默认归属、判定依据、是否需要补充边界说明
  - [x] SubTask 5.8: 至少包含 1 个混合型样本，验证升级判断规则是否触发且可落地
  - [x] SubTask 5.9: 按 spec 中定义的 Markdown 表格模板输出抽查记录，保证字段完整且可复查

- [x] Task 6: 运行程序化校验并收尾
  - [x] SubTask 6.1: 运行链接校验工具，确认迁移后无断链
  - [x] SubTask 6.2: 运行文件迁移校验工具，确认无遗漏、无重复，并形成完整性复核报告
  - [x] SubTask 6.3: 修复校验发现的问题并重新验证
  - [x] SubTask 6.4: 清理迁移过程中不再需要的旧路径残留与临时状态

- [x] Task 7: 修复 2026-07-15 迁移验收失败项并完成复验
  - [x] SubTask 7.1: 修复仓库内仍残留的旧 `docs/` 根路径引用，至少覆盖 `AGENTS.md`、`.agents/` 路由/规则文档与相关 `.trae/specs/`
  - [x] SubTask 7.2: 调整链接校验范围或清理 `.meta/backup/` 等备份残留，确保 `check-links.py` 面向当前有效工作树执行且结果可通过
  - [x] SubTask 7.3: 修复 `repo-check` 当前暴露的仓库合规问题，消除外部目录与命名规则导致的阻断项
  - [x] SubTask 7.4: 重新定义并补齐“迁移完整性”校验口径，区分允许的路径修复改动与真正的内容损坏，再复核 `.agents/docs/` 全量文件
  - [x] SubTask 7.5: 复跑迁移专项校验并回填 Task 4-6 与 `checklist.md`；全仓 `repo-check all` 剩余 Mermaid 存量问题转入后续治理，不再阻塞本次迁移收尾

- [ ] Task 8: 后续治理迁移收尾后的存量问题
  - [x] SubTask 8.1: 先清点并归类完整性报告中的 18 个新增文件，形成“纳入新基线 / 移位 / 删除”三分清单
  - [x] SubTask 8.2: 先处理低争议新增文件：补入新基线或归位到更合适目录，并更新相应说明或索引
  - [x] SubTask 8.3: 将 38 个疑似内容/结构性改动按类型分组，至少拆分为“README 结构性改写 / frontmatter 溯源退化 / 正文链接或文案变更 / 复盘报告派生改动”
  - [x] SubTask 8.4: 先复核高确定性样本，优先处理 `source` 退化和 `x-toml-ref` 异常，形成“应保留 / 应修复 / 待人工判断”清单
  - [x] SubTask 8.5: 单独复核 `.agents/docs/README.md`、`standards/README.md`、`reuse-and-generalization.md` 等入口级结构改写，确认哪些属于迁移后应保留的语义重构
  - [x] SubTask 8.6: 对剩余需回滚或修复的疑似样本执行最小修复，并复跑完整性复核，压缩待人工判断样本数
  - [x] SubTask 8.7: 为 Mermaid 存量问题建立分批治理清单，按“核心规范文档 / `.agents/docs` 人类文档 / 历史 spec 产物 / 生成型输出”四类拆分
  - [x] SubTask 8.8: 先处理核心规范文档中的 Mermaid 真问题，范围优先限定 `README.md`、`.agents/commands/`、`.agents/checklists/`
  - [x] SubTask 8.9: 再处理 `.agents/docs` 内高价值人类文档的 Mermaid 问题，排除纯归档或历史产出目录
  - [x] SubTask 8.10: 最后决定历史 spec 与生成型输出中的 Mermaid 问题是修复、豁免还是排除出校验范围，并沉淀统一口径
  - [ ] SubTask 8.11: 复跑 `repo-check all`、完整性复核与必要抽样检查，更新本 spec 的后续治理结论（2026-07-15 已完成首轮复验与结论文档化，但验证未通过，详见 `artifacts/task8-11-final-verification.md`）

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 depends on Task 2
- Task 4 depends on Task 3
- Task 5 depends on Task 4
- Task 6 depends on Task 4
- Task 7 depends on Task 6
- Task 8 depends on Task 7
- SubTask 8.2 depends on SubTask 8.1
- SubTask 8.4 depends on SubTask 8.3
- SubTask 8.5 depends on SubTask 8.3
- SubTask 8.6 depends on SubTask 8.4 and SubTask 8.5
- SubTask 8.8 depends on SubTask 8.7
- SubTask 8.9 depends on SubTask 8.7
- SubTask 8.10 depends on SubTask 8.7
- SubTask 8.11 depends on SubTask 8.2 and SubTask 8.6 and SubTask 8.8 and SubTask 8.9 and SubTask 8.10

# 可并行任务组
- Task 4 的 SubTask 4.1、4.2、4.3 可按引用类型并行处理
- Task 5 可与 Task 6 的首轮校验交叉推进，但最终验收必须等待 Task 6 完成
- Task 7 的 SubTask 7.1、7.2、7.3 可并行收敛，但 7.5 必须等待前三项完成
- Task 8 的 SubTask 8.1 与 8.7 可并行启动：前者治理完整性新增文件，后者建立 Mermaid 分批清单
- Task 8 的 SubTask 8.4 与 8.5 可并行推进：一个处理元数据/溯源问题，一个处理入口级结构改写
- Task 8 的 SubTask 8.8、8.9、8.10 可按文档类型分批执行，但 8.11 必须等待前三类治理结果稳定后再统一复验

# 验收说明
- 2026-07-15 首轮全量验证未通过，随后由 Task 7 收敛失败项并完成迁移专项复验。
- 迁移专项验证已通过：`.agents/docs` 链接校验与 frontmatter 校验通过，旧 `docs/` 根路径残留已收敛，迁移完整性已形成复核报告。
- 全仓 `repo-check all` 仍有与本次迁移解耦的 Mermaid 存量问题，不再阻塞本次迁移闭环，转入 Task 8 后续治理。
- 完整性报告仍保留 `38` 个需人工复核样本与 `18` 个新增文件确认项，作为迁移后治理工作继续跟踪，不影响本次路径迁移收尾状态。
- 2026-07-15 执行 `SubTask 8.11` 首轮复验后，确认基线覆盖仍为 `0 missing`，但当前工作树上的 `.agents/docs` 链接/frontmatter 校验重新失败，新增文件集合也从预期的 `15` 扩张到 `25`。
- 同轮复验显示，全仓 Mermaid 失败面除历史 spec / 生成型输出外，仍残留 `core` 规范层与 `.agents/docs` 的非 `8.10` 口径 `error` 文件，因此 `SubTask 8.11` 暂不回填完成；详见 `artifacts/task8-11-final-verification.md`。
