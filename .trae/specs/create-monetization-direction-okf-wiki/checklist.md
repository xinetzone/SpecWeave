# 个人变现方向发现方法论 · OKF Wiki — 验证清单（checklist.md）

> 用途：Spec Mode 第七阶段逐项验证。**全部 22 项已通过**，每项附实测证据（非过程描述）。
> 交付：子模块 `54a94f66` + `3b22f24c`；主仓 `aa7e87261` / `f7004ad20` / `672964f65` / `639498b27`（均未 push）。

## 事实与核验

- [x] CP-1（AC-1）：`facts.md` 存在，F 编号 F-001 起连续无跳号，条数 82（≥60），四类信源关键声明均有条目，观点/主张与事实分层标注
      → 证据：本机正则提取编号集合 = 1..82 连续无跳号；分节覆盖 C1/C2/C3/C4；〔主张〕标注 18 处。
- [x] CP-2（AC-2）：C1/C3/C4 类 P0 声明（提出者/年份/核心主张归属）与全部数字声明 100% 有核验记录
      → 证据：`facts.md` 每条带核验级 + 核验结论 + 证据 URL；分布 ✅58 / ⚠️21 / 单源 3 / ❌0；`verification.md` §2 逐条依据。
- [x] CP-3（AC-2）：勘误四张清单逐项过筛并记录于 `verification.md`
      → 证据：`facts.md` §5（日期年份 / 成效数字 / 口径对照 10 组 / 引文逐字）+ `verification.md` §4 同步。
- [x] CP-4（AC-2）：涉及性格/天赋测评工具的内容均有科学效度争议与「非决定论」边界标注
      → 证据：F-038/F-039/F-040（正反并列）、F-041（边界）、F-043（grit）；`index.md` 已知边界段 + `02` 篇。
- [x] CP-5（AC-6）：`facts.md` 与 `references/article-source.md` 的 F 编号集合正则比对一致
      → 证据：本机 PowerShell 双向 `Compare-Object` 差集为空（各 82）；差异项 0，无需 log 注记。

## 结构与归属

- [x] CP-6（AC-3）：bundle 落于既有分组 `sheke/industry`，未新建顶级分组，归属理由已留痕
      → 证据：`knowledge-map.md` §3 候选对照表（industry / personal-growth / marketing / finance / workplace）；`log.md` 归属理由条。
- [x] CP-7（AC-3）：组 index 导航表行、toctree 条目、束数计数三面同步；域/总索引计数同步
      → 证据：industry 27 行 + toctree 27 条 + 计数 27；`check-bundles-index.py` 五面一致（9 域 / 62 组 / 644 束）。
- [x] CP-8（AC-4）：符合 OKF v0.2——根 `index.md` 带 `okf_version: "0.2"` 且含 toctree；`concepts/`、`references/`（article-source + verification）、`log.md` 齐备；非保留 `.md` 均含非空 `type`
      → 证据：本机遍历 22 个 .md；`type` 缺失 0（仅 `log.md` 无 frontmatter，符合保留文件名规范）。
- [x] CP-9（AC-4）：`examples/` 取舍由操作可复现性两问判定，结论与理由已记录于 `log.md`
      → 证据：`log.md`「操作可复现性两问判定」条（两问皆「是」→ 设 examples/，并与 zhihu-monetization 对照）。
- [x] CP-10（AC-4）：frontmatter 字段齐备，`sources` 含理论/著作来源与核验权威 URL
      → 证据：本机遍历非 index `.md`，`type/generated/verified/status/stale_after/sources` 缺失 0（Task 7 补齐 18 文件）；根 index `sources` 含 spec facts + references 双路径。

## 链接与编码

- [x] CP-11（AC-5）：三级 toctree 完整，条目逐一可达
      → 证据：`check-toctrees.py` 通过（exit 0）；本机逐条 `Test-Path` 82 条 → 缺失 0。
- [x] CP-12（AC-5）：全部新增/修改 `.md` 相对链接可达，零 `file:///`
      → 证据：本机解析全部 `](...)` 内联相对链接 171 条 → 断链 0；`file:///` 命中 0。
- [x] CP-13（AC-5）：UTF-8 strict roundtrip 无乱码
      → 证据：`check-utf8.py` 通过（11751 文件均为有效 UTF-8，exit 0）。

## 质量与边界

- [x] CP-14（AC-8，rubric）：方法链路可操作性 **5 分**（阈值 ≥4）
      → 理由：完整链路（自评盘点表 + 候选方向生成法 + 需求验证实验 + 决策清单）齐备；方法层四步 05~08 每步均有「输入项 / 操作步骤 / 判定标准 / 反模式 / 达标条件」，`examples/` 四篇均为可填写表格与脚本。证据：`07`/`08`/`09` 逐篇复核 + 独立审查「读者可用性 PASS」。
- [x] CP-15（AC-9，rubric）：七概念质量门 **4 分**（阈值 ≥4）
      → 理由：G1 事实层 01~04 因果推断词命中 **0**；G2 9 条〔洞察〕均改写为「现象 / 根因 / 影响 / 建议」四要素（其中 6 条如实标注「本包未给出根因，属待研究方法问题」——不编造以换取形式完整，见 Task 9）；G3 `00-overview` §六「可迁移模式：变现方向发现四步法」四要素齐备（触发场景 / 核心步骤 / 反模式 / 迁移验证，迁移验证以 P1~P4 复用 + 同簇 5 束对接为证据）；G4 行动项原子化（08 §5 单一职责 + 可独立验证）；F 后有 V 对抗审查。**扣分说明**：G2 有 6 条洞察的根因要素因不得编造而显式留空，稳妥计 4 分而非 5 分。证据：本机四要素标记检索 + `adversarial-review.md` 第六节。
- [x] CP-16（AC-10）：无 F 支撑的因果或收益断言为零；无收益承诺；无具体产品/课程推荐
      → 证据：魔鬼代言人 10 条攻击中「相关当因果」成立 2 条已修（00-overview 因果句改「风险升高」+ 标前提假设；09 §6 改显式「本方法假设」）；事实层因果词 0；`index.md` 已知边界含「非承诺」「不做推荐」段。
- [x] CP-17（AC-10）：魔鬼代言人专项审查记录存在，逐条给出「成立/降级/删除」结论
      → 证据：`.trae/specs/create-monetization-direction-okf-wiki/adversarial-review.md`（16 KB，六节）；结论 不成立 6 / 成立 3 / 降级 1，未决 actionable = 0。

## 门禁与提交

- [x] CP-18（AC-7）：`invoke gates.all` 三 gate 全绿
      → 证据：本机重跑底层脚本 `check-utf8.py` / `check-toctrees.py` / `check-bundles-index.py` 三者 **exit 0**（9 域 / 62 组 / 644 束，11751 文件）。说明：`invoke` 入口因 `invocations` 依赖缺失不可用，改跑等价的底层脚本（`tasks/gates.py` 即封装此三者），已在 `log.md` 如实注明。
- [x] CP-19（AC-7）：提交顺序为子模块 → 主仓库 spec → 主仓库子模块指针；Conventional Commits 中文描述；显式文件列表
      → 证据：`54a94f66`（子模块）→ `aa7e87261`（spec）→ `672964f65`（指针）；补救轮 `3b22f24c` → `f7004ad20` → `639498b27`；全部 `git add` 显式列路径。
- [x] CP-20（AC-7）：`git log` 验证未 push；既有 bundle 正文零改动
      → 证据：上述 6 个提交均在 `origin/main..HEAD` 本地未推送区间；子模块/主仓改动仅限新 bundle + 3 个共享索引文件（+ spec 区），既有 bundle 正文 diff 为空。

## 交付物

- [x] CP-21：`projects/awesome-okf-xs/doc/bundles/sheke/industry/monetization-direction/` 新 bundle 落盘完整
      → 证据：本机列举 **22 个 .md**（concepts 12 / examples 5 / references 3 / index + log），与组索引表「22」一致。
- [x] CP-22：`.trae/specs/create-monetization-direction-okf-wiki/` 含 spec.md / tasks.md / checklist.md / facts.md / sources.md / knowledge-map.md
      → 证据：本机列举 7 文件（另含 `adversarial-review.md`）。
