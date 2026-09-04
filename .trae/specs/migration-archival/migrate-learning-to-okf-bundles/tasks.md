# Tasks

> 场景识别：知识沉淀+重构优化混合场景，链路 R（台账）→ A（分批迁移）→ I（洞察）→ V（对抗审查）→ C（原子提交）。
> 目标库：`projects/awesome-okf-xs/doc/bundles/`（git submodule，注意并行会话竞态：add 与 commit 分离）。

- [x] Task 1: 文件级迁移台账（R 阶段）
  - [x] 1.1 递归扫描 `docs/knowledge/learning/` 全部文件，生成台账（spec 目录 `facts-ledger.md`）：路径、主题、目标束、处置类型（新建/合并/直迁/重复删除/低价值舍弃-隐私元数据）
  - [x] 1.2 逐分类核对主题清单与映射表（spec.md 分类映射表），标注 10 对重复、5 项部分重叠的处置决定
  - [x] 1.3 登记非 md 资源（.html/.png 等）处置方式
  - [x] 1.4 隐私脱敏标记：按已完成的隐私扫描结果，在台账中标记 12 个 retrospective、17 个 seven-concepts-report、37 个 log.md 的处置（元数据文件不迁入；正文残留的 session ID/token 消耗/执行时间线/个人环境细节在迁移时剔除）
- [x] Task 2: okf-bundles/chaos 10 个已成型 OKF 包直接重定位
  - [x] 2.1 迁移 ai-agent-skills、apache-tvm、mobile-use、tiktoken、veadk-python → `jishu/ai/`（或 `jishu/ml/` 视内容）
  - [x] 2.2 迁移 english-grammar → `wenxue/english/`（新建组）；home-assistant、tuya-iot → `jishu/iot/`（新建组）；laozi-lineage → `guoxue/laozi/`；okf-ecosystem → `meta/`
  - [x] 2.3 chaos 根级 4 个元文件（index/CROSS_BUNDLE_REVIEW/PATTERNS_LESSONS/retrospective）归入对应束 references 或 `meta/`
  - [x] 2.4 各级 index.md toctree 接线 + `bundles/index.md` 登记 + `invoke gates.toctrees` 验证
- [x] Task 3: 重复对收敛（10 对合并回填）
  - [x] 3.1 逐对比对 learning 侧与 bundles 侧内容差异，识别 learning 独有实质内容
  - [x] 3.2 独有内容回填既有束（增量章节 + log.md 登记），无独有内容则标记重复删除
  - [x] 3.3 涉及：boshu-laozi、agent-skills、graphql、okf-wiki、protobuf、agency-agents、deepseek-harness、codewhale、pyinvoke、scikit-build-core
- [x] Task 4: 00/01/02 分类迁移（哲学·协议·工程方法论）（磁盘验证：first-principles、ffi/idl/tvm-ffi、jira-skill、agent-interface、ai-engineering-methodology、context-optimization 均已落盘）
  - [x] 4.1 first-principles → `zhexue/methodology/`（新建组）；01 分类新建束：ffi、idl、tvm-ffi、jira-skill、okf-desktop、agent-interface、agent-runtime-protocol、knowledge-catalog（合并 meta/okf-spec）
  - [x] 4.2 02 分类 AI 工程方法论六板块整合为 1-2 束入 `jishu/ai/`（实拆 ai-engineering-methodology + context-optimization 两束）
  - [x] 4.3 toctree 接线 + 索引登记 + gates.toctrees（热区登记由集中落盘代理统一完成）
- [x] Task 5: 03/04 分类迁移（平台工具·文档标记）
  - [x] 5.1 03 分类新建束：eve、orca、okf-kit、open-code-review、quantdinger 及散文件主题（anthropic 系、areal、browseract、minitap 等）→ `jishu/ai/`
  - [x] 5.2 04 分类：myst 系两主题合并入 `jishu/document/myst/` 相关束；新建 mermaid、weasyprint、python314-stdlib；python314-cpython-wiki 合并 `jishu/python/cpython/`；executablebooks-myst-guide、mdx-graphql-guide、declarative-partial-updates 散文件处置（后者按内容实质改判 jishu/web）
  - [x] 5.3 toctree 接线 + 索引登记 + gates.toctrees
- [x] Task 6: 05/06 分类迁移（多模态内容·商业趋势）
  - [x] 6.1 05 分类新建束：animejs-threejs-adapter、atomic-emergence、causal-ai、mainecoon、minit2i 及散文件主题 → `jishu/ai/` 或 `jishu/viz/`
  - [x] 6.2 06 分类新建组 `sheke/industry/`，迁入 ai-monetization、ai-switch-governance、douyin-vibecoding、ems-energy、rqndd、three-ai-tools、volcengine-ecosystem 等（14 束）
  - [x] 6.3 toctree 接线 + 索引登记 + gates.toctrees
- [x] Task 7: 07/08/09/10 分类迁移（厂商产品·系统设施·ML部署·基础知识）
  - [x] 7.1 07 分类：baidu-ocr、deepseek 定价、volcengine 系、miaowu、sunlogin 系、oray 系、tuya 系 → `jishu/iot/` 与 `jishu/ai/`；chatgpt-codex 与既有 openai-codex 束比对合并；okr-wiki → `sheke/workplace/`；google-cloud → 合并 meta/okf-spec
  - [x] 7.2 08 分类：新建组 `jishu/systems/` 收 wsl、powershell-hell；git 系并入 `jishu/dev/`（A7）；conda-dev 两 wiki 合并 `jishu/build/conda/`；caffe-architecture → `jishu/ml/`；cpython-devguide 合并 `jishu/python/cpython/`
  - [x] 7.3 09 分类 onnx-wiki 与 `jishu/ml/onnx/` 比对合并回填
  - [x] 7.4 10 分类：勾股定理 → `kexue/math/`；thesis-writing → `sheke/workplace/`；python314-cpython-wiki 合并 `jishu/python/cpython/`
  - [x] 7.5 toctree 接线 + 索引登记 + gates.toctrees（热区集中落盘后 check-toctrees 1161→11，剩余为并行会话 agent-platform-notes；check-bundles-index 通过 9域/56组/497束）
- [x] Task 8: 时效性核验（实时性保障）
  - [x] 8.1 筛选时效敏感束（版本/定价/产品状态/Release Notes 类），WebSearch 核验 2026-09 现状（onnx 版本线、deepseek 定价两项定向核验完成）
  - [x] 8.2 过时数据更新或标注 `status: deprecated`/`stale_after`，核验记录写入各束 log.md（deepseek-pricing：官方平价制与束内峰谷表述冲突已留痕待复核；onnx：官方 Latest v1.22.0/Opset 27，束内 1.23.0/opset 28 未能确认已留痕）
- [x] Task 9: 洞察报告（I 阶段）
  - [x] 9.1 基于台账与迁移过程产出 `insights.md`：重复率统计、时效衰减发现、知识资产分布、双体系治理建议
- [x] Task 10: 对抗审查（V 阶段）
  - [x] 10.1 独立子代理对账：台账每条目归宿核实（2124 md 全对账，28 目录文件数守恒 28/28）、内容保真抽查、索引计数与目录树三角校验（check-bundles-index exit 0：9域/56组/497束）
  - [x] 10.2 隐私复扫：对迁入内容复扫隐私模式（个人标识/凭据格式/私人叙事/工作流元数据），59 元数据文件零误迁；发现 2 处 major 个人路径残留（orca/open-code-review）已修复复扫 CLEAN
  - [x] 10.3 真实凭据格式扫描：60+ 命中逐一核实全部为占位符/官方示例/公开默认凭据，真实凭据零命中
  - [x] 10.4 审查发现问题登记并修复，复验通过（review.md 总判定 PASS 可删源）
- [x] Task 11: 源目录删除与上游修复
  - [x] 11.1 删除 `docs/knowledge/learning/` 整目录（含 .meta/toml/docs/knowledge/learning 孤儿元数据与 categories/learning 孤儿分片）
  - [x] 11.2 修复主仓库全部指向 learning/ 的引用：docs/ 193 文件 6360 处（6260 改链 bundles、100 纯文本化）+ .agents/ 13 文件 37 处 + knowledge/index.md、README.md、categories/knowledge.md、archive-wiki-linkage-guide.md、mermaid-manual-fix-guide.md、fix-frontmatter.py 手动修复
  - [x] 11.3 主仓库 `check-links.py --path docs/`（learning 断链清零，剩 119 处均为存量历史断链）+ `sphinx-build -b dummy -E` 零新增错误
- [x] Task 12: 全量门控与原子提交（C 阶段）
  - [x] 12.1 子模块门控：utf8 exit 0（9596 文件）、bundles exit 0（9域/56组/498束，含并行 WIP 1 束）、toctrees 仅剩并行会话遗留 12 处（本迁移零新增）、sphinx reading 100% 且 236 条警告与本迁移 1758 文件交集为 0
  - [x] 12.2 子模块原子提交 c57848410（1758 文件 +411166/−55；add 与 commit 分离、暂存集逐文件前缀核对 VIOLATIONS=0、禁止项零混入）
  - [x] 12.3 主仓库两笔提交：4a3a04e48 `docs(knowledge): 下线 learning 板块并修复全部上游引用`（3887 文件）+ 0f93fb4c2 `chore(submodules): awesome-okf-xs 指针更新`（gitlink 2b716df7c→c57848410）；未 push

# Task Dependencies

- Task 1 是全部任务的前置（台账为对账依据）
- Task 2-7 依赖 Task 1；Task 2 与 Task 3 可并行；Task 4-7 按分类可并行（注意同一子模块内 index.md 共享文件的写入串行化）
- Task 8 依赖 Task 2-7（束就位后核验）
- Task 9 依赖 Task 1-8
- Task 10 依赖 Task 2-8（审查对象就位）
- Task 11 依赖 Task 10（对账通过后才可删除）
- Task 12 依赖 Task 11（全部验证通过后提交）
