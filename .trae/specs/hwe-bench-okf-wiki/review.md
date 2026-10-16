---
okf_version: "0.2"
type: review
spec: ./spec.md
reviewer: "process:fresh-context-independent-c"
at: 2026-10-14T20:00:00+08:00
result: pass
---

# HWE Bench OKF v0.2 教程束 — C 阶段 fresh-context 独立对抗评审

## 1. 评审范围、方法与环境自证

### 1.1 范围

- 评审对象：[hwe-bench 束](../../../projects/awesome-okf-xs/doc/bundles/jishu/iot/hwe-bench/index.md)（29 个 Markdown：根 index + log + concepts 17+index + examples 3+index + references 4+index）。
- 评审依据：[spec.md](./spec.md)（AC-1~AC-6）；tasks.md 未改。
- 上游只读镜像：`d:\spaces\SpecWeave\external\dao\auto-arch-tournament`。
- 身份声明：本评审为 C 阶段 fresh-context 子代理，未参与 R/E/V 任何写作；不采信 V 阶段 [verification.md](../../../projects/awesome-okf-xs/doc/bundles/jishu/iot/hwe-bench/references/verification.md) 的结论，全部计数、门禁与主张均独立复算取证。临时脚本全部自写于 `C:\Users\xinzo\AppData\Local\Temp\`（hwe_c_enum.py、hwe_c_fr.py、hwe_c_log.py、hwe_c_struct.py、hwe_c_dump.py~hwe_c_dump8.py），未调用 V 阶段任何脚本。

### 1.2 环境自证（亲跑）

| 项 | 命令/方式 | 结果 |
|---|---|---|
| 镜像 HEAD | `git -C external/dao/auto-arch-tournament rev-parse HEAD` | `4a137bb1378834ca3664a1c971684777eb5f364a` = pin ✓ |
| 镜像工作树 | `git status --short` | clean（评审全程只读，未改上游一字）✓ |
| 束文件集 | 自写枚举器机械枚举 | 恰 29 个 .md ✓ |
| 环境 | Windows 10 + PowerShell 7 + anaconda Python + Sphinx 8.2.3 | 门禁 cwd=`projects/awesome-okf-xs` ✓ |

### 1.3 方法

1. **机械面**：自写枚举器剔除 ``` 代码围栏后解析全束链接与正文纪律（CP-R5）；自写解析器全量解析 log.jsonl / results.jsonl（CP-R2）；facts/insights/source-code-map 编号完整性独立正则核验（CP-R1）。
2. **主张面**：20 篇正文逐篇抽 ≥3 条数字/机制主张（不抽链接、抽句子），约 90 条高风险主张直读镜像 ~30 个源码/数据文件逐行对拍。
3. **口径面**：AC-2 六类矛盾逐类回镜像复核两个出处。
4. **教学面**：通读全部 20 篇正文与 3 个子 index，按 AC-4 四锚点独立打分。

抽核覆盖率：20/20 正文篇篇有直读镜像的主张对拍（100% 篇覆盖），高风险数字组（CRC、遥测、$ 成本、排行榜、RTL 哈希、schema 键集）按组全量核对，非高风险组链接做机械边界全检+人工相关性抽样。

## 2. 六个 AC 逐条裁决

| AC | 类型 | 裁决 | 证据摘要（详见后续小节） |
|---|---|---|---|
| AC-1 事实可溯源 | rule | **pass** | 20 篇逐篇 ≥3 主张回镜像/facts 对拍，约 90 条命中、命中率 100%、P0=0；另发现并修复台账内 2 处 F 错引（P2，非事实虚构） |
| AC-2 口径矛盾显式化 | rule | **pass** | 六类 6/6 留痕，K-1~K-6 台账在 facts.md L209-L214，逐类双出处独立复核成立 |
| AC-3 结构与门禁全绿 | rule | **pass** | check-bundles-index rc=0；check-toctrees 本束 rc=0；dummy rc=0；严格 -W 本束警告/错误 = 0 |
| AC-4 教学质量 | rubric | **pass（5/5/5/5，均值 5.0，≥4）** | 四维独立打分，附文件+小节例证 |
| AC-5 工程纪律 | rule | **pass** | 600 链接与 20 篇正文机械扫描 0 违例 |
| AC-6 双独立评审收口 | rule | **pass** | V 已回填 24 个内容文件 verified.at=2026-10-14T19:30:00+08:00；review.md 仅 C 阶段创建；终态 pass |

### 2.1 AC-1 / CP-R2：事实抽核（逐篇表）

抽核口径：每篇取 3~6 条**数字或机制句子**，回镜像逐行回扫或回 facts 找 F 编号。命中=句子事实与上游一致；miss=方向错或虚构。

| 篇 | 抽核数 | 命中 | miss | 对拍锚点举例（均直读镜像亲验） |
|---|---|---|---|---|
| 00-position-and-loop | 5 | 5 | 0 | README 七门顺序与胜场表列（无 LUT 列，F-004）；IDENTITY.md L9-L26 三色 `#FAF7F2/#1A1A1A/#1F4380`+三字体；STRATEGY.md L34 tagline；review_log.md L3-L10 MLCAD 175/37+14/0,0,-2 |
| 01-hypothesis-schema | 3 | 3 | 0 | schema 35 行/7 必填键/category 5 枚举/integer 约束；hypothesis.py L40 `HYPOTHESIS_TIMEOUT_SEC=1200`；log.jsonl L19 schema "1.5 not integer" |
| 02-round-orchestration | 5 | 5 | 0 | runner.py L71 `DEFAULT_MAX_COST_USD=200.0` vs L1145 help "(default $30)"；L1140-1141 默认 n=15/k=3；Makefile L27-28 `N?=10 K?=1` |
| 03-worktree-sandbox | 4 | 4 | 0 | worktree.py L155-L167 heredoc 泄漏 +28.5% 注释；ff-only 合并；sandbox.py CONTRACT_PATHS L45-66、EVAL_TOOLS 7 项 L71-79 |
| 04-rvfi-nret-contract | 4 | 4 | 0 | core_bench.sv L83/L89 ready 绑 `1'b1`；wrapper.sv vs wrapper_si.sv 通道差异；checks-deep.cfg nret 1 / checks.cfg nret 2 + ALTOPS 注释 |
| 05-formal-altops | 5 | 5 | 0 | formal.py L6 "53 total"、L42 `EXPECTED_MIN_CHECKS=50`；run_all.sh 95+ 与 PREUNSAT rc=16（L165-191）、reaper `kill -0`（L96-115）；README L199 "~105 checks" |
| 06-cosim-iss | 3 | 3 | 0 | 对拍器实为 reference.py（318 行，无 iss.py）；cosim 三件套 F-058；selftest/coremark 双负载 |
| 07-fpga-fitness | 6 | 6 | 0 | fpga.py L30 SEEDS=[1,2,3]；五 CRC 0xe9f5/0xe714/0x1fd7/0x8e3a/0xfcaf 在 L38-44；22% 停顿注释+"2.87 zero-wait vs 2.21 stalls"L45-52；L56 `MIN_SUCCESSFUL_SEEDS=2`；**fitness 公式实际在 L274（束引 :247 漂移已 K-5 留痕）**；ipc round 6 位 L295 |
| 08-coremark-measurement | 4 | 4 | 0 | holdout.py 50M cycle + 同停顿 flags；v0_expected.json geomean=7212.331561429864；哨兵 ipc=2e-06×1e6=2.2264；127.03×2.2264≈282.82 复算成立 |
| 09-accept-rule-outcomes | 3 | 3 | 0 | 无 target 严格 `>`（F-015）；r24s2 formal/cosim 双过而 fitness −73.25% 被基线闸拦（F-104）；三结果类 F-082 |
| 10-baseline-cpu | 5 | 5 | 0 | RTL 集 baseline 13 / bench 13 / v1 16 个 .sv；bench 与 baseline **12 文件 SHA-256 相同仅 core.sv 不同**；v1 新增 div_unit.sv(182 行)/store_slot.sv(54)/00_core_pkg_first.sv(9) 文件头注释与 concept 逐字一致；bench/core.yaml L4 `nret: 1` |
| 11-v1-evolution | 5 | 5 | 0 | log.jsonl 74 行独立解析 9/51/9/4；diary 09-26 L46 522,817,399 tokens/$123.62；Opus 段 9 imp/13 reg/23 broken、983.24/+247.7%、302.21、3128、33800s |
| 12-scribe-lessons | 4 | 4 | 0 | scribe.py L24 `SCRIBE_TIMEOUT_SEC=240`、白名单正则 L40-42、append-only startswith 回滚 L214-231；固定提交 cores/ 下 LESSONS.md = 0 个（concept 已主动声明为运行时产物，无虚构） |
| 13-v1-bench-methodology | 4 | 4 | 0 | 16 个 models*.yaml 花名册机械清点恰 39 个 `- name:`；core.yaml 301.04 哨兵 vs 282.82 retest；BENCH L21-22 N=15 K=3、L218/225 示例 --n 10 |
| 14-v1-leaderboard | 5 | 5 | 0 | LEADERBOARD.md L15 Opus 983.2/3128/302.2/3.25/46 iters/22%；L183 per-rep 46 iters；L159-163 random formal_failed 135；results.jsonl 41 行/34 键，Opus 行 accepted10/rejected13/broken23/983.24/3128/302.21/fixture_commit 132c378… |
| 15-v2-holdout | 6 | 6 | 0 | v2.html L31 36 scored runs；L44 1.32x/CI 1.18-1.47/p=0.0005；主表 L150-217（7024/6418/5320/5014/3595/3538；VexRiscv 6216；textbook 2645/8.6x；V0 309）；L242-247 135 独立抽取 117/12/6；L364-365 3 draws×45；L369-372 "not comparable" |
| 16-harness-reliability | 4 | 4 | 0 | diary 09-25 L72-88 seatbelt EPERM、PID 91122、601.32、d3c9cd7/7a7d593、aborted1 不计分；log.jsonl L9/L45/L48 placement seeds 全 None；L72 `[49.43,None,None]`；L73 fmax 中位 52.99（seeds 52.99/52.58/54.72）fitness 154.53/lut4 6378/−73.25 |
| examples/00-cold-div | 6 | 6 | 0 | L2/L17/L7 逐字段对拍：id、五文件 changes、broken 行无 timestamp（13 键）、L17 25 键、159.92/375.43/+15.7/5888/2227/seeds[159.92,157.98,165.51]/04:24:16.990069、L7 前任冠军 lut4=10192/fit 324.48，**全部逐字命中** |
| examples/01-opus-983-rep | 3 | 3 | 0 | rep1 账目与 diary 09-26 一致；fixture_commit 与 results.jsonl 对拍；46 iters 口径 L183 |
| examples/02-failure-gallery | 4 | 4 | 0 | 分组拦截点与 log 行一致；placement 三行 seeds=None；schema 1.5 拒纳行 L19；−73.25 最差样本 |
| **合计** | **约 90** | **约 90** | **0** | 命中率 100%，P0=0 |

补充：ex00 摘引 JSON 中 fmax/fitness/delta/lut4/ff/seeds/timestamp/键数 9 项一次性全中，属全束抽核中最强的单点证据。

### 2.2 AC-2：六类口径矛盾留痕（6/6）

| # | 矛盾 | 留痕位置 | C 独立复核 |
|---|---|---|---|
| ① | V1/V2 数字不可互比 | K-1（facts.md L209）；concept 15 正文；v2.html L351-366 vs L369-372 "not comparable" | 两出处均亲读，1.32x 对比的对象与 V1 排行榜口径确实不同，束内未做任何互比计算 ✓ |
| ② | 博客「10 胜/50 回归」vs 日志 9/51 | K-2（L210）；concept 00/11；F-004 | README 表 10 行含 0.0h 基线哨兵；独立解析 log.jsonl = 9 improvement/51 regression（不含哨兵）✓ |
| ③ | IPC/ff 量纲 | F-083；concept 08「量纲勘误」节（L44-54）；concept 13 L57 | L1 哨兵 ipc_coremark=2e-06 为 iter/cycle 绝对值，×1e6=2.2264 CoreMark/MHz；127.03×2.2264≈282.82 复算成立 ✓ |
| ④ | formal 检查数 53 / 95+ / ~105 | K-4（L212）；C15（source-code-map.md L159）；concept 05 | formal.py L6/L42、run_all.sh L165-191、README L199 三口径原文齐在，束内并列呈现不调和 ✓ |
| ⑤ | N=10 vs 预注册 N=15/K=3 vs 示例 --n 10 | K-3（L211）；concept 02/13 | Makefile L27-28 `N?=10 K?=1`、BENCH L21-22 15/3、L218/225 示例 --n 10 三处亲读 ✓ |
| ⑥ | fpga.py:247 等行号/字符串漂移 | K-5（L213）；concept 07；F-029 | 四处漂移全部独立实证：fitness 公式实居 **L274**（非 :247）；runner.py L1145 help "$30" vs L71 默认 200；implement.py L11 代码 `600*3`（30min）旁注 "10 min"（上游笔误，束内如实转录留痕）；--n 10 示例漂移 ✓ |

结论：六类齐备、每类双出处可点开、采用口径有声明，**6/6 pass**，无静默调和。

### 2.3 AC-3 / CP-R4：三门禁原始输出

| 门禁（cwd=projects/awesome-okf-xs） | rc | 关键输出（亲跑摘录） |
|---|---|---|
| `python scripts/check-bundles-index.py` | **0** | 最终复跑：「9 域 / 61 组 / 632 束，frontmatter、计数行、节标题、分组表、toctree 五面一致」（评审窗口内并行会话注册，束数 631→632；中间曾瞬时五面漂移 rc=1，非本束改动所致，收敛后复跑 rc=0） |
| `python scripts/check-toctrees.py doc/bundles/jishu/iot/hwe-bench` | **0** | 「全部 index.md 引用有效，所有内容文档均可达」 |
| `python -m sphinx -b dummy doc <tmp>`（非严格） | **0** | 最终复跑「build succeeded, 279 warnings.」，含 hwe-bench 的 WARNING/ERROR=0（前一轮构建为 280 条，差异来自并行会话对他束的增改；抽样均为 myst-tutorial、english-grammar、first-principles 等他束既有警告） |
| `python -m sphinx -W --keep-going -b dummy doc <tmp>`（严格） | **1（预期）** | 末行原文：「build finished with problems, 281 warnings (with warnings treated as errors).」；全日志 230 个 WARNING 行/106 个 ERROR 行（ERROR 为 zhexue/first-principles 等他束的 docutils 硬错误与被 -W 升级的警告）；**含 `hwe-bench` 的 WARNING/ERROR = 0**（29 处 hwe-bench 提及全部为 reading/writing 进度行） |

说明：评审窗口内有并行会话注册其他束，总束数 629→630→631→632 漂移；按简报纪律「五面一致即接受」，未改动任何与本束无关的计数（iot 组=9 束含 hwe-bench，表格行+toctree+组计数三面已核）。严格构建 rc=1 系他束历史问题所致，AC-3 的通过条件是「dummy rc=0 且本束 0 警告」，两条均满足。

### 2.4 AC-5 / CP-R5：工程纪律机械扫描

自写枚举器（剔除围栏）复跑结果（修复后）：

- 链接 600 条：pinned blob 353、pinned tree 9、束内 236、仓库根 URL 2。
- `HASH_BAD=0`（所有 pin hash 恰 40 字符且=4a137bb…）、`BLOB_MISSING=0`、`TREE_MISSING=0`、`ANCHOR_BAD=0`（#Lxx-Lyy 对镜像文件逐一对行号，0 越界）、`INTERNAL_MISSING=0`、裸文本错 hash `BARE_HASH_ISSUES=0`、`PENDING-V=0`。
- 20 篇正文：0 file:///、0 `external/dao`、0 `.tmp/.spec`、0 `](../`、无重复 H1、frontmatter 后无 H1、每篇均以「## 相关概念」或「## 相关概念与示例」收尾。
- 29 文件 frontmatter 形态：20 正文 + log + references 4 内容文件 + 根 index（type: bundle、sources 两条、无 verified 段）合规；3 个子 index 无 frontmatter；24 个内容文件 nested verified.at 统一 `2026-10-14T19:30:00+08:00`（直接 Read 核实；注意 generated.at 为各批时间 14:30~18:00，二者不混淆）。

## 3. P0-P3 发现与修复清单

| 级别 | 数 | 处置 |
|---|---|---|
| P0（虚构/门禁红/结构缺件） | **0** | — |
| P1（口径错/锚点越界/纪律违例） | **0** | — |
| P2（措辞/错引，建议修） | 发现 2，**已修 2** | 见下 |
| P3（观察项） | 2 | 只记录，见第 7 节 |

P2 修复明细（均在束内 references/source-code-map.md，C 阶段修复，修后枚举器复跑 0 违例）：

1. **C15 F 编号错引（L159）**：原文「三处行号见 F-058」，但 F-058 是 cosim 三件套；formal 三口径事实编号是 **F-057**（已回 facts 表核对两条定义）。已改为 F-057。
2. **C17 事实指向错误（L161）**：原文「实现提交 hash 全表见 F-121」，而 F-121 实为 V2 random 135 独立抽取；且亲验 log.jsonl 的 improvement 行 25 键中**没有任何 commit/hash 字段**。已改为「九胜场逐条明细（槽位/标题/fitness/增幅/日志行）见 F-100；log.jsonl 不记录实现提交 hash，hash 仅能经 git log --all 与日志时间戳/标题对拍复原」。

性质说明：两处都是**台账内部的编号错指**（读者点过去会看到相邻主题的事实），不是正文虚构或方向性错误；所陈述事实本身（三口径并存、九胜场）在镜像中成立。按 P2 顺手修复并留痕。

## 4. 独立复算结果

### 4.1 log.jsonl（cores/v1/experiments，独立 Python 全量解析）

- 74 行、603,222 字节 = 73 真假设 + L1 基线哨兵；结局分布 **improvement 9 / regression 51 / broken 9 / placement_failed 4**（不含哨兵）；类别 structural 25 / micro_opt 24 / predictor 24；键并集 26；最差 r24s2 **−73.25%**（formal/cosim 双过）；9 个真胜首尾行与 F-100 表对拍一致。与束内数字 0 差异。
- 旁证：broken/sandbox 行 13 键无 timestamp；improvement 行 25 键无 hash 字段；L11/L26/L71 sandbox 拒 test/_helpers.py 留痕。

### 4.2 results.jsonl（bench 遥测，独立解析）

- 41 行、34 键并集；榜首 Opus 行：accepted 10 / rejected 13 / broken 23、best=983.24、lut4=3128、fmax=302.21、ipc=3e-06、fixture_commit=132c378287350708f5ce26cb67a8b4ef838a0f5c，与 LEADERBOARD.md/concept 14 转录一致。

### 4.3 references 编号完整性（独立正则）

- facts.md：**F-001~F-126 共 126 条，0 缺号 0 重号**；十组计数 10/12/12/10/13/9/13/12/15/20 与表头一致；K-1~K-6 台账在 L209-L214；全束 F 引用 **0 指向未定义、0 定义未被引用**。
- source-code-map.md：**C01-C20 齐**（C10/C11/C12 承载 log 三复算、C13 RTL 计数、C15 formal 三口径、C18/C19 V2）。
- insights.md：**I-1~I-6 齐**，四元组（陈述/证据/反常识/行动）四段无缺；按「证据」行边界独立重数 F 出现次数为 **5/5/7/5/8/5 次**（去重后 5/5/7/5/7/5），每条 ≥3，满足简报要求。与 V 报告自报的 5/5/8/5/7/5 存在计数边界差异（V 疑似把块内非证据行或重复 F 计入），**不影响任何结论**，此处留独立计数备查。

### 4.4 其他独立清点

- 花名册：tools/bench 下 16 个 models*.yaml，`- name:` 条目恰 **39**。
- RTL：baseline 13 / bench 13 / v1 个 .sv；bench 与 baseline 12 文件 SHA-256 相同、仅 core.sv 不同；v1 新增 3 文件行数与文件头注释逐字对拍。
- 链接统计与门禁/Sphinx 输出：见 2.3/2.4。
- holdout：v0_expected.json geomean 7212.331561429864、5 内核；holdout.py 50M cycle。
- LESSONS.md 在固定提交 cores/ 下 = 0（concept 12 无虚构）。

## 5. CP-U1 教学质量打分明细（AC-4，独立）

| 维度 | 分 | 例证（文件 + 小节，均本次通读亲见） |
|---|---|---|
| 可读性 | **5** | concept 00「一句话机制」用 ASCII 流程图把七门顺序/短路/ff-only 一图说清，且头条数字先标「作者报告」口径；concept 07 把 fitness=Fmax 中位数×iter/cycle×1e6 与反常量折叠夹具（ready 绑 1'b1）分「公式→夹具→22% 停顿→量纲」递进；术语首次出现均有解释（如 NRET、ALTOPS、rNsM ID 在 concept 01/04/05 首现处给定义）；逐字英文引文均入围栏配中文解读 |
| 知识地图连贯性 | **5** | 17 concept 严格按 spec 七大主题排开（00 定位→01-03 假设/编排/沙箱→04-08 验证链→09 接受规则→10-11 baseline/v1→13-14 V1 bench→15-16 V2/harness，12 横切 scribe）；跨篇数字靠 F 编号单一事实源（F-001~F-126 无重号无悬空调用，本次机检 0 dangling）；六类易混口径全部在正文现场挂 K-x，而不是堆到附录让读者自己拼 |
| 概念间导航 | **5** | 20 篇篇尾均有「相关概念/相关概念与示例」导航节（机检 0 例外）；3 个子 index 不堆标题而带阅读问题与路径（concepts index 按主题分组、examples index 给阅读顺序）；ex00 一篇内向 concept 02/03/05/06/07/11 与 ex01/ex02 的 8 条导航全部与正文论点对应，无死链式引用（236 条束内链接机检 0 missing） |
| 示例可独立走读 | **5** | ex00 自身就是完整教学闭环：同一除法器想法 r1s0 死亡→r6s0 +15.7% 复活，给两段精简 JSON（13 键/25 键）、四个「为什么编排允许复活」的结构性原因、div_unit.sv 文件头物证、三条可迁移教训；不依赖先读其他篇即可看懂（本次逐字段对拍 9 项数字全中，证明示例自洽）；ex01 走通一个 rep 的收支账、ex02 按拦截点陈列失败样本，三篇合起来覆盖「单假设生死→单 rep 冠军→失败全集」三个尺度 |
| **均值** | **5.0** | ≥4 通过线；扣分项观察：计数台账曾有 2 处 F 错引（已修，见第 3 节），属 references 层瑕疵，不影响正文叙事体验，故不扣分但留痕 |

叙事问题专项检查：术语首次出现无解释=未发现；跨篇矛盾口径=未发现（六类矛盾均为有意留痕且双口径并列）；导航死链式引用=0（机检）；示例与 concept 事实冲突=0（ex00/ex01/ex02 的数字全部能回到 concept 与镜像）。

## 6. 七大主题覆盖映射（CP-R1）

| spec 主题 | 覆盖文件 |
|---|---|
| ①定位与自主研究循环 | concepts/00 |
| ②假设 schema 与隔离/沙箱 | concepts/01、02、03 |
| ③RVFI/formal/cosim/FPGA/CoreMark 验证链 | concepts/04、05、06、07、08 |
| ④接受规则与三结果类 | concepts/09 |
| ⑤baseline/v1 RTL 与进化史 | concepts/10、11、12（scribe 横切） |
| ⑥V1 排行榜方法学 | concepts/13、14 |
| ⑦V2 口径演进、holdout、harness 可靠性 | concepts/15、16 |
| 三示例 | examples/00（一假设两度尝试生命周期）、01（Opus 983 rep 拆解）、02（失败/拒纳样本集） |

log.md 含 G0/R/I/E/V 五段实际记录；C 段已由本评审于 2026-10-14 20:00 +08 回填实际过程与结论。

## 7. blocked / 观察项

### blocked（任务边界，非缺陷）

1. **EDA/仿真/FPGA 未执行**：Windows 无工具链且 spec Non-Goals 明确静态走读；所有性能/频率/费用数字本评审只做转录一致性核对，未做独立物理复现（束内已全篇标「作者报告」）。
2. **V2 原始运行数据不可得**：v2 分支外链，本评审仅对 v2.html 静态文本转录核对（36 scored runs、1.32x、p=0.0005、135 抽取等），且 K-1 已强制 V1/V2 不互比。
3. **锚点相关性**：353 blob 链接全部机检行号不越界；相关性语义判断集中在高风险组全做，其余为抽样。

### P3 观察项（只记录，不改）

1. **C05「39+1」措辞**：source-code-map C05 行写「39+1 个模型条目」，其中 +1 在镜像内无出处；C 独立清点 16 个 models*.yaml 恰 39 个 `- name:`。verification.md §6 已显式指引读者引用以 39 为准。按 P3 纪律本次不改，仅登记：后续若动该文件，建议把「+1」删除或补出处。
2. **implement.py L11 上游笔误**：代码 `600*3`（=1800s/30min）同行注释写 "10 min"。属上游文档错误，镜像只读不代改；束内 F-029/K-5 已如实转录并列入口径漂移，读者不会被误导。
3. **insights 证据 F 计数边界差异**：见 4.3，独立计数 5/5/7/5/8/5（次），与 V 自报略有出入，全部 ≥3，无实质影响。

## 8. 终态

- P0 未决：**0**；P1 未决：**0**；P2 发现 2 已修复并复跑验证；P3 观察 3 项（含计数边界差异）均不阻断。
- AC-1~AC-6 裁决：**pass / pass / pass / pass（5.0）/ pass / pass**。
- 改动面：仅束内 2 个文件被修改——[source-code-map.md](../../../projects/awesome-okf-xs/doc/bundles/jishu/iot/hwe-bench/references/source-code-map.md)（L159/L161 P2×2）与 [log.md](../../../projects/awesome-okf-xs/doc/bundles/jishu/iot/hwe-bench/log.md)（C 段回填）；本文件为 spec 目录唯一新增文件；无 *-draft.md 残留；未执行任何 git commit/push；未改上游镜像、其他束、spec.md、tasks.md。

# Result: **pass**
