---
type: Pattern
id: "cross-migration-link-fix-sop"
title: "跨迁移断链批量修复 SOP（P-Link-Migrate-v2）"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/process-patterns/cross-migration-link-fix-sop.toml"
maturity: "L2 验证中"
validation_count: 2
source: "知识库链接治理里程碑复盘（2026-07-31，处置263条绝对路径+32条相对路径）；知识库迁移闭环复盘（2026-08-30，.agents/docs/knowledge→docs/knowledge 2918文件迁移+1295文件引用面修复）"
---

# 跨迁移断链批量修复 SOP（P-Link-Migrate-v2）

> **v2 增量**（2026-08-30）：新增「分层归因验证」正交维度（S2a），新增 AM5-AM7 反模式（前缀误伤/存量混入/显示层乱码误判），补充 git mv 保历史与双树合并白名单实践；并按模式文档 V2 质量门补齐「失败案例实录」「不适用场景与反目标用户」「早期预警信号」章节。

## 适用前提

- `check-links.py` 纯本地模式可用，断链清单含源文件行号与目标路径；
- 迁移通过 `git mv` 执行，旧树/旧位置可解析（"按旧位置重算"的锚点存在）；
- 修复在同一工作区完成，可对新树做 basename 唯一定位；
- Windows 环境下遵循 P4：终端显示编码（GBK）与 git 对象存储编码（UTF-8）分层验证。

## 触发场景

当发生以下**任意 1 种**情况时，立即调用本模式：

1. 工作区**跨盘符/跨主机拷贝**后首次运行 link-check（如 `d:/spaces/SpecWeave/...` → `d:/AI/...`）；
2. 原子化拆分/目录重构**涉及 3+ 目录层级**移动后；
3. 第三方 vendor 子模块**大版本升级或换源**导致外部归档路径整体失效；
4. 单轮 check-links 报告本地断链 **≥ 20 条且 50%+ 含盘符绝对路径**；
5. **大规模目录迁移**（git mv 数百至数千文件）完成后的引用面修复阶段。

## 核心步骤（五步分法）

| 步骤 | 动作 | 产出物 | 验证指标 |
|------|------|--------|---------|
| **S1 基线扫描** | 运行 `check-links.py` 纯本地模式，不启用外链检查 | 完整断链清单（含源文件行号 + 目标路径） | 清单 100% 命中断链，无假阴性漏检 |
| **S2 桶分分类** | 正则分桶将断链归入 3 类：<br/>• A桶：`file:///[A-Z]:/` 绝对路径<br/>• B桶：`../` 层数明显不对的相对路径<br/>• C桶：目标文件/目录**确实不存在**的历史占位链接 | 三桶统计表 | 三桶互斥且覆盖率 100% |
| **S2a 分层归因（v2新增）** | 将断链按**成因**归入 3 层：<br/>• MIG-INTERNAL：迁移树内部互链（源文件是本次移动的文件）<br/>• MIG-INBOUND：外部文件指向迁移树（源文件未被移动但目标被移走）<br/>• LEGACY：与迁移无关的存量断链（目标从未存在、external/、模板占位符等） | 分层归因报告（如 `check-migration-impact.py` 输出） | 每条断链有唯一归属层；修复范围严格限定为前两层，LEGACY 层只记录不修复 |
| **S3 脚本批处理** | 按桶用专用脚本处理：<br/>• A桶 → `file:///` 绝对路径批处理脚本，按**是否是当前项目存在的源**分：<br/>&nbsp;&nbsp;– 源存在：计算相对路径回写<br/>&nbsp;&nbsp;– 源不存在：内联 `` `label`（源项目归档路径） `` 注记<br/>• B桶 → `--fix` 自动层+人工 spot-check<br/>• C桶 → 转为内联代码文本 + 不存在注记<br/>• MIG-INTERNAL（v2）→ 迁移文件树内链接**按旧位置解析重算**（源文件内容中的相对链接语义仍锚定旧目录）<br/>• MIG-INBOUND（v2）→ 按 basename 在新树内唯一定位真实子路径后重算 | 修改后的 MD 文件集合 | 批处理脚本执行 exit=0，修改文件数 ≤ 预期 |
| **S4 复检归零** | 再次运行 check-links 纯本地模式 + 误伤审计（`audit-*-suffix.py` 扫描 diff 中被误改的相似前缀路径） | 复检报告 + 审计报告 | 本地断链计数 == 0，或剩余**全部归因为 LEGACY 存量**（非本次迁移引入）；误伤行数为 0 |

## 迁移操作配套实践（v2新增）

- **git mv 保历史**：大规模迁移全部使用 `git mv`（重命名检测保留 `follow` 历史），禁止"删旧建新"；
- **双树合并白名单**：目标树已存在同名文件时，预先声明可覆盖白名单（如索引 README），冲突文件改名保留（如 `README.md` → `WIKI-INDEX.md`），禁止静默覆盖；
- **迁移文件内链接按旧位置重算**：移动后的文件内容中相对链接语义仍锚定旧路径，必须按"旧位置解析 → 新位置重写"，不能按新位置直接验证（否则会把正确链接误判为断链、把断链误判为正确）。

## 正反模式

### ✅ 推荐正模式

- **P1 批处理优先**：A桶 ≥ 10 条时，先写 Python 正则批处理脚本再手改；手改 ≤5 条零散项即可；
- **P2 先预览后执行**：所有 `--fix` 或脚本修改，先 `--dry-run` 预览 diff；
- **P3 误报白名单化**：S4 若剩 lambda/代码块误报，给 checker 提交 fenced-code 跳过改进条目（不作为本次必须闭环）；
- **P4 字节级验证（v2）**：Windows 沙箱终端中文显示乱码时，用 `unicode_escape` 输出验证 git 对象真实字节，再决定是否需要修复（显示层 GBK ≠ 存储层 UTF-8）。

### ❌ 反模式（踩坑证明不可行）

- **AM1 回滚目录改回去赌链接自愈**：返工 2x 起步且破坏原子化拆分成果；
- **AM2 对不存在的 C 桶猜新目录名**（如硬编码 `/docs-old-archive/`）：制造永久相对路径垃圾，下轮重构又会断；
- **AM3 全量纯人工点击改**：≥50 条时平均 2 秒/条 × 上下文切换 = 实际 60+ 分钟，批处理脚本只需 15 秒；
- **AM4 跳过复检（S4）直接算完成**：批处理 regex 最容易把 legitimate 的 `[text](not-a-path)` 也替换，必须复检；
- **AM5 前缀子串匹配无路径边界（v2）**：以 `.agents/docs/knowledge` 做子串替换会误伤 `knowledge-transfer`/`knowledge-base` 等"旧前缀+连字符"相似路径（实测 9 处误伤 6 文件需回滚）；必须匹配 `旧前缀 + "/"` 带边界，并用审计脚本扫 diff 复核；
- **AM6 把 LEGACY 存量断链混入迁移修复提交（v2）**：破坏原子性且让 diff 无法归因；分层归因后存量问题单独开任务；
- **AM7 凭终端显示乱码执行 amend（v2）**：存储字节实际正确时 amend 是无效操作且可能引入新风险；先字节级验证再决策。

## 失败案例实录（v2 新增）

> 以下案例均来自 2026-08-30 知识库迁移闭环实战（2918 文件 git mv + 1295 文件引用面修复），是 AM5-AM7 的真实发生记录而非假设。

- **FC-1 前缀子串匹配误伤 9 处（对应 AM5）**：修复脚本以 `.agents/docs/knowledge` 做无边界子串替换，误改 `knowledge-transfer`/`knowledge-base` 等"共同前缀+连字符"路径 9 处、波及 6 文件（含 `apps/ai-agents/zhujian-wudao/AGENTS.md`）；由 `audit-knowledge-suffix.py` 审计扫描 diff 捕获，`git checkout` 还原全部误伤行。若审计缺位，污染会静默进入迁移提交。
- **FC-2 LEGACY 存量断链混入风险（对应 AM6）**：迁移后全仓 link-check 剩余断链中混有目标从未存在的 first-principles 占位链接、`external/` 路径、模板占位符等存量问题；S2a 分层归因后确认剩余断链 100% 归因为 LEGACY（非本次迁移引入），只记录不修复、转 P2 治理任务。若不分层直接修，1295 文件的修复 diff 将无法归因审计，且破坏提交原子性。
- **FC-3 终端乱码诱发无效 amend（对应 AM7）**：迁移修复提交（c0ab4a56d）后 Windows 沙箱终端 `git log` 中文显示乱码；经 `unicode_escape` 字节级验证确认 git 对象存储为正确 UTF-8（`\u77e5\u8bc6\u5e93\u8fc1\u79fb` =「知识库迁移」），未执行 amend；`git-commit-utf8.py --amend` 因暂存区为空报错退出，无副作用。凭显示乱码 amend 属无效操作且可能引入新风险。

## 不适用场景与反目标用户（v2 新增）

- **反目标场景 A：小规模移动/少量断链**——单目录重命名、移动文件 ≤5 个、断链 <20 条且无盘符绝对路径时，直接 `git mv` + `check-links.py --fix` + 人工 spot-check 即可；套五步法与分层归因属过度工程（归因报告成本高于修复本身）。
- **反目标场景 B：纯外部 URL 死链**——HTTP 404、域名失效、外链搬迁等走 `external-url-dead-bucket-fix-sop`（死链桶分）；本 SOP 闭环针对本地文件引用，外链可达性不在 S1-S4 范围内。
- **反目标场景 C：非 Markdown 链接域**——代码 import（Python/TS）、`.classpath`、tsconfig paths、Dockerfile 路径等需语言专属工具（eslint-import-resolver、Maven/Gradle 声明化、编译闭环验证）；本 SOP 的正则桶分针对 Markdown 链接语法与 frontmatter 路径字段，代码域仅在"类比映射"意义上可参考（见迁移验证表），不可直接套用脚本。
- **反目标场景 D：LEGACY 存量断链治理**——目标从未存在的占位链接、`external/` 引用、模板示例链接等不是迁移引入的，本 SOP 只在 S2a 记录归属、不修复；存量治理须单独开任务（复盘行动项 A1），混入迁移提交即触发 AM6。
- **反目标场景 E：无迁移前基线（前提缺失）**——迁移未用 git mv、旧提交已不可达时，"按旧位置解析重算"失去锚点，MIG-INTERNAL 桶无法处理；只能退化为 basename 模糊匹配 + 全量人工核对，不满足本 SOP 的自动化前提，应回退重做迁移而非强行套用。

## 早期预警信号（v2 新增）

| # | 预警信号 | 含义 | 即时动作 |
|---|---------|------|---------|
| W1 | S1 基线断链数 > 迁移文件数的 50% | 引用面远超移动面预期，移动范围统计不全或存在未登记入站引用 | 暂停 S3，回查迁移清单与入站扫描范围 |
| W2 | dry-run diff 出现"旧前缀+连字符"相似路径被改（如 knowledge → knowledge-transfer） | AM5 前缀误伤正在发生 | 立即停止，正则改为 `旧前缀+"/"` 带边界匹配 |
| W3 | S4 复检剩余断链无法全部归入 MIG-INTERNAL/INBOUND/LEGACY | 归因不完备，修复范围可能失控 | 逐条人工归因后再决定修复或转治理任务 |
| W4 | 批处理 dry-run 修改文件数 > 预估上限 | 正则命中范围外溢 | 收窄匹配模式，逐文件抽查 diff |
| W5 | Windows 终端中文显示乱码 | 可能仅是显示层 GBK 问题 | `unicode_escape` 字节级验证，禁止凭显示 amend（AM7） |
| W6 | MIG-INBOUND basename 定位出现多命中 | 同名文件多个，自动选择错误率高 | 人工消歧，禁止取第一个命中（复盘行动项 A3） |
| W7 | 迁移用了"删旧建新"而非 git mv | follow 历史丢失、旧位置不可解析 | 回退重做迁移，S2a/S3 前提不成立 |
| W8 | 预提交钩子拦截模式文档质量章节 | 触碰的存量文档存在质量债 | 被拦截文件移出暂存区保主体原子性，质量债单独提交补齐（洞察 4） |

## 迁移验证（跨领域复用证明）

本模式已在以下**非 Markdown 链接**场景验证等价可复用：

| 非目标域 | 原问题映射 | 调整方法 | 结果 |
|---------|-----------|---------|------|
| Python 代码库 `import D:\old-path\module` 绝对引用 | 类比 A桶 `file:///D:/...` | 正则替换 `import [A-Z]:\\` → `from project_relative import` | 编译闭环成功 |
| TypeScript monorepo 子包被拆后 `../../` 跨层错误 | 类比 B桶相对路径错深度 | `check-imports` + eslint-import-resolver 自动修 90% | 剩余 10% TSConfig paths 别名修 |
| Java Eclipse 旧工程 `.classpath` 绝对 jar 路径 | 类比 A桶 | Maven/Gradle 依赖声明化 | 构建闭环 |
| 大规模目录迁移引用面（v2，Markdown 域内二次验证） | 2918 文件 git mv + 双树合并 | 分层归因 + 树内链接旧位置重算 + 入站 basename 定位 | 1295 文件修复，剩余断链 100% 归因 LEGACY，误伤 9 处被审计捕获并回滚 |

## 参考资源

- 触发本模式的源头复盘：`retrospective/reports/project-governance/retrospective-document-link-health-milestone-20260731/README.md`
- v2 增量来源复盘：`retrospective/reports/project-governance/archiving-and-migration/retrospective-knowledge-migration-closedloop-20260830.md`
- 工具脚本约定：`.agents/scripts/check-links.py` §5.2 修复模式 + `lib/link_fixer/` 算法说明；一次性脚本样本见 `.temp/active/`（check-migration-impact.py / audit-knowledge-suffix.py）
