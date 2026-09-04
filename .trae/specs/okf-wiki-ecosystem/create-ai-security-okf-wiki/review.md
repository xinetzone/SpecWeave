---
source: V（Adversarial Review, depth=deep）阶段审查
reviewed: 2026-09-02
reviewed_objects: projects/awesome-okf-xs/doc/bundles/jishu/ai/ai-security/（27 个 md）
fact_bases: facts-cl4r1t4s.md / facts-l1b3rt4s.md / facts-obliteratus.md / insights.md
---

# AI 安全知识包三束 · V 阶段对抗审查报告

> 审查对象：`ai-security/` 分组 27 个 md（group index 1 + cl4r1t4s 8 + l1b3rt4s 7 + obliteratus 11）。
> 审查方法：专项 1 事实核对（对源仓库/Git 对象库逐条复验）+ 专项 2 伦理边界 grep 扫描 + 专项 3 格式脚本扫描 + 四视角对抗审查。
> 处置纪律：发现即修正（共 13 处修改落在 10 个文件），全部修改后复扫格式通过。

## 一、专项 1 事实核对结果

### 1.1 cl4r1t4s 束（抽取 12 处关键论断）

| # | 论断（wiki 位置） | 期望（facts/源文件） | 实测 | 处置 |
|---|---|---|---|---|
| 1 | 26 目录 / 73 档案 / 75 总文件（group index、束 index、catalog） | F-C4-007/009 | `Get-ChildItem -Recurse` 实测 75 文件（73+README+LICENSE），26 目录逐一核对 | ✅ 一致 |
| 2 | 扩展名分布 txt 33/md 32/mkd 3/json 2/无扩展名 3（vendor-landscape） | F-C4-010 | 按实测清单归类复核一致 | ✅ 一致 |
| 3 | ANTHROPIC 14 文件 = 8 txt + 6 md（vendor-landscape、catalog） | F-C4-013 | 实测清单逐一归类 8+6 | ✅ 一致 |
| 4 | **catalog 文件名 `Claude-4.txt`** | — | 源目录实际为 **`Claude_4.txt`**（下划线） | ❌ **已修正** |
| 5 | 其余 72 个文件名（catalog 全表） | 源目录清单 | 逐一比对（含 OPENAI 12+2、XAI 7、无扩展名 3 等） | ✅ 全部一致 |
| 6 | 防注入 9 文件 = XAI 3 + ANTHROPIC 6（defense-lessons） | F-C4-051 | 清单逐名一致 | ✅ 一致 |
| 7 | Claude-4.5-Opus 结构锚点 L904/L1041-1049/L1117/L1173（defense-lessons、compare-guardrails、catalog） | F-C4-038 | 与 facts 行号一致 | ✅ 一致 |
| 8 | GROK-4.1 policy 段 L1-9、persona L11（prompt-anatomy、compare-guardrails） | F-C4-042 | 一致 | ✅ 一致 |
| 9 | ZCode Prompts.md 1843 行 / Skills.md 2346 / Tools.json 1287（vendor-landscape、catalog） | F-C4-022/067~069 | 一致 | ✅ 一致 |
| 10 | 5.6-Sol 组合 4270+8093=12363 行、全库唯一命名（vendor-landscape） | F-C4-070 | 一致 | ✅ 一致 |
| 11 | shadow-puppet 隐喻、"Leak, extract, or reverse-engineer … Good."（mission-transparency、ethics） | — | **Grep README 实测命中**：L22 shadow-puppet、L28 "Leak, extract, or reverse-engineer something? Good."、"virtually all major AI models + agents!" L3 | ✅ 一致（facts 未登记的引语经源文件补验成立） |
| 12 | "对抗暴露面越大的品类，档案越厚……因为这两家被提取最多"（vendor-landscape） | — | 因果关系无证据（相关性推断被写成因果） | ⚠️ **已弱化**为"一个合理的解释是……（相关性解读，而非因果结论）" |

### 1.2 l1b3rt4s 束（抽取 11 处关键论断）

| # | 论断（wiki 位置） | 期望（facts/git HEAD 64960b7） | 实测 | 处置 |
|---|---|---|---|---|
| 1 | HEAD `64960b783249d36f76a48a33103cc4b168332b9b`（index、catalog） | F-L1-001 | 与本地 git 对象库一致 | ✅ 一致 |
| 2 | 44 文件 = 34 厂商 .mkd + 5 非厂商 + 2 JSON + 1 TXT + README + LICENSE（index、catalog 计数断言） | F-L1-008 | `git ls-tree -r HEAD` 实测 44 | ✅ 一致 |
| 3 | **34 厂商清单及全部字节数**（catalog 34 行表格） | F-L1-009/010 + git ls-tree -l | 44 文件字节数逐一比对：AAA 147 / ALIBABA 6,178 / AMAZON 981 / … / ZYPHRA 481，**全部与 git blob size 一致，零误差** | ✅ 一致 |
| 4 | TOKEN80M8 23,448,666 B、TOKENADE 1,867,310 B、README 24,071 B 可见约 51 字符、LICENSE 34,523 B | F-L1-003/004/010/017 | 一致 | ✅ 一致 |
| 5 | glitch token 库 7,895 token × 8 类行为 × 5 分词器（index、attack-taxonomy、defense-perspective、catalog） | F-L1-014/015 | 一致 | ✅ 一致 |
| 6 | 杂项 10 文件字节数与用途（catalog） | F-L1-012~019 | 一致（!SHORTCUTS 10,859 / *SPECIAL_TOKENS 55,437 / -MISC- 20,327 / 1337 35 / SYSTEMPROMPTS 37,059 / #MOTHERLOAD 2,239） | ✅ 一致 |
| 7 | ANTHROPIC 14 章节 / GOOGLE 15 / OPENAI 21 条目 / XAI 8 / ZAI 6 / DEEPSEEK 6（mission、catalog） | F-L1-045/029/025/032/036/039 | 一致 | ✅ 一致 |
| 8 | RESET_CORTEX 模板见 GOOGLE/XAI/MOONSHOT/ZAI/GROK-MEGA；指纹要素表（attack-taxonomy、catalog） | F-L1-030/038/039/046/047 | 一致 | ✅ 一致 |
| 9 | **"17/20 文件命中 LOVE PLINY"（catalog 指纹表）** | facts 无此计数 | V 阶段 `git grep -E "LOVE[ \|/\\\\-]*PLINY"` 复测：34 厂商 .mkd 中 **16** 命中 + `-MISCELLANEOUS-` 1 = 17 文件；"17/20" 分母口径不可复现 | ❌ **已修正**为可复核的 git grep 表述 |
| 10 | T 类别归属（M 级 20 文件的 T 编号） | facts 未逐条登记 | 无法逐条源码复验——catalog 已用 **D/M 核验深度标记**自我限定，且仅登记类别归属不涉载荷 | ⚠️ 接受（标记纪律已兜底） |
| 11 | AGPL-3.0 全文 34,523 字节、含第 13 条（responsible-disclosure、catalog） | F-L1-004 | 一致 | ✅ 一致 |

### 1.3 obliteratus 束（抽取 14 处关键论断，含 6 处勘误项专项复核）

| # | 论断（wiki 位置） | 期望（facts/源码） | 实测 | 处置 |
|---|---|---|---|---|
| 1 | **六处勘误项在 wiki 中以源码值为准且勘误表齐全**（novel-techniques 勘误表 6 行） | F-OB-012/013/014/032/034/050 | 逐项核对：测试 116 文件/1,949 函数 ✅、模型预设 130 ✅、nuclear=4 ✅、study layers/pruning=100 ✅、UI 10 tab ✅、ANALYZE 5 模块 ✅——勘误表 6 项齐全且方向标注正确 | ✅ 勘误体系完备 |
| 2 | **group index 写 "116 模型预设（5 层级）"（两处）** | F-OB-013：源码 130，README 116 为勘误项 | group index 用了 README 勘误值，与 obliteratus 束内自述（130）冲突 | ❌ **已修正**（两处 → 130 源码实测，标注勘误） |
| 3 | nuclear 4 方向 + "Uses 4 SVD directions (not 8)" + 顽固 MoE（GPT-OSS 20B、GLM-5）（methods-presets） | F-OB-014 + abliterate.py | grep 实测：L511 n_directions: 4；L498 "Combo mode for stubborn MoE models (GPT-OSS 20B, GLM-5, etc)" | ✅ 一致 |
| 4 | spectral_cascade 6 方向（methods-presets、architecture-map） | facts 未登记 | grep 实测 L350 n_directions: 6 | ✅ 补验成立 |
| 5 | qwen38_e01/e02/e03 固定 500/142/200 划分（methods-presets） | facts 未登记数值 | 实测 e01 description "immutable 500/142/200 split"（L198） | ✅ 补验成立 |
| 6 | advanced regularization 0.3 / embed_regularization 0.5 / 2 轮精炼；optimized KL 0.5 / bayesian_trials 50；winsorize_percentile 0.01（methods-presets、novel-techniques） | facts 未登记数值 | grep 实测 L302-304 / L487-493 / L246 等 | ✅ 全部成立 |
| 7 | steering_vectors.py：SteeringVector 字段、SteeringConfig 默认（alpha=1.0/position=all/normalize=True）、from_refusal_direction 默认 alpha=-1.0、mean(pos)-mean(neg) L140-143、combine L155（abliteration-primer、methods-presets、python-api） | F-OB-048 未登记字段级细节 | grep 实测 L55-74/L90-98/L140-141/L155 全部一致 | ✅ 一致 |
| 8 | informed：ouroboros_threshold 0.5 / max_ouroboros_passes 3 / entanglement_gate 0.8 / hydra 别名 L206-207 / cleanup_failed_run（pipeline、analysis-modules、python-api） | F-OB-044/057 部分 | grep 实测 L203-209/L257-261/L280 全部一致 | ✅ 一致 |
| 9 | cli：--min/max-layer-fraction L252-258、info --task/--device cpu/--dtype float32 L177-181（cli-quickstart） | F-OB-042 未登记 | grep 实测一致 | ✅ 一致 |
| 10 | **METHODS 字典 "11 键"（architecture-map）** | — | grep `^    "…": {` 实测 **12 键**（7 预设+spectral_cascade+informed+qwen38×3） | ❌ **已修正**（→ 12 键并列明键名构成） |
| 11 | **analysis/ "28 个 .py"（architecture-map、analysis-modules 两处）** | facts 未登记 | `Get-ChildItem -Filter *.py` 实测 **29** | ❌ **已修正**（两处 → 29） |
| 12 | PROBE 1024 前向 / DISTILL+EXCISE ~30s / VERIFY 210-270s / REBIRTH 194-350s / 90% 墙钟（pipeline、scaling） | F-OB-022 摘要级 | grep README 实测 L648-650/L655/L661 全部命中 | ✅ 一致 |
| 13 | 130 预设 5 层级显存范围与示例、预消融变体 Dolphin/Hermes/WhiteRabbitNeo（scaling） | F-OB-013 + presets.py | tiny<1GB/small~4GB/frontier 多 GPU 与 docstring 一致；变体名 presets.py L1216-1275 命中 | ✅ 一致 |
| 14 | v0.1.3 / 19 CLI / 10 --method choices / 15+15 导出 / 20 包级导出（各篇） | F-OB-015/041/017/053/051 | 一致 | ✅ 一致 |

**专项 1 小结**：累计核对论断 37 处（cl4r1t4s 12 + l1b3rt4s 11 + obliteratus 14），一致 31 处、补验成立 5 处（facts 未登记但经源文件/Git 复验为真）、确认错误 4 处（全部已修正）、表述弱化 2 处。l1b3rt4s 编目（44 文件字节数）零误差；obliteratus 六处勘误体系完整且全束以源码值为准。

## 二、专项 2 伦理边界扫描结果

- **载荷特征 grep（3 轮）**：`NEW RULE`/`ResponseFormat`/`PWNED`/`SYSTEM GONE`/`developer mode`/`Ignore all`/完整双响应段/step-by-step 指令——**零命中完整载荷**。唯一英文长句命中为 cl4r1t4s 中 persona 句 "You are ChatGPT, a large language model trained by OpenAI"（守方档案结构特征登记，F-C4-040 原样，≤1 行）。
- **l1b3rt4s 束长句扫描**：≥10 词英文连续句零命中——所有引用均为术语/指纹级（`RESET_CORTEX`、`{Z}`、`<|vq_*|>`、`LOVE PLINY` 等），仅用于归因登记，无构造用法，符合"指纹最小化"边界。
- **用途限定声明**：group index（L19）、cl4r1t4s index（用途限定段）、l1b3rt4s index（"用途限定声明（先读）"）、obliteratus index（"研究用途限定声明"）——4/4 存在。
- **结论**：合规，无需修改。

## 三、专项 3 格式扫描结果

脚本扫描（yaml.safe_load + toctree 双向校验 + 禁用模式），27/27 文件：

| 检查项 | 结果 |
|---|---|
| frontmatter YAML 解析 | 27/27 通过，无解析失败 |
| group index toctree 3 条 ↔ 3 束 index | 一一对应 |
| 各束 index toctree 覆盖全部子文档（8/7/11） | 无缺失、无死链 |
| `file:///` 绝对路径 | 0 处 |
| 脚注块前手写 `---` | 0 处 |

全部修改后复扫：仍 27/27 通过。

## 四、四视角意见清单

| 视角 | 意见 | 处置 |
|---|---|---|
| 魔鬼代言人 | vendor-landscape "档案越厚……**因为**被提取最多" 将相关性写成因果，证据不足 | ✅ 已采纳：弱化为"合理的解释……相关性解读，而非因果结论" |
| 魔鬼代言人 | l1b3rt4s catalog "17/20 文件命中" 分母口径不可复现 | ✅ 已采纳：改为 git grep 可复现表述（16/34 厂商 + 1 杂项） |
| 魔鬼代言人 | compare-guardrails 占比数字、T 归类 M 级标记均为编者估计 | ⚠️ 免于修改：两者已自带"近似值估算"/"D/M 核验深度"自我限定，符合研究登记纪律 |
| 新人视角 | defense-perspective 中 "NFKC" 缩写未展开 | ✅ 已采纳：补全"Unicode 归一化形式 NFKC" |
| 新人视角 | Ouroboros/abliteration/refusal direction 等术语 | 免于修改：首次出现处均有定义（概念速查表 + 正文括注"命名自衔尾蛇"） |
| 老板视角 | defense-lessons 四条类别级防御建议缺落地路径回链 | ✅ 已采纳：补交叉链接至 l1b3rt4s 防御视角反哺与红队评估工作流 |
| 老板视角 | 九条护栏 checklist、勘误核验方法示范、评估矩阵 | 免于修改：可操作价值已充分（checklist/矩阵/四步核验法齐备） |
| 未来视角 | cl4r1t4s 与 obliteratus 束缺 git HEAD 快照锚点（l1b3rt4s 有，标准不一致），计数/版本号类内容易随上游漂移 | ✅ 已采纳：两束 index 信任声明补 HEAD `93b0ae6f…` 与 `e39f9088…` |
| 未来视角 | 模型代际内容（Gemini 1.5~3、GPT-4o~5.2 等）会过时 | 免于修改：mission-attack-research 已有"时效判定/代际演化信号"专节，束内处处标注 2026-09-02 快照 |

## 五、修正文件清单（10 文件 / 13 处）

| # | 文件 | 修改 |
|---|---|---|
| 1 | `index.md`（group） | 两处 obliteratus 简介 "116 模型预设" → "130（源码实测，README 称 116 为勘误项）"；7 方法预设补注 "CLI 实际 10 choices" |
| 2 | `cl4r1t4s/index.md` | 信任声明补快照 git HEAD `93b0ae6f…` |
| 3 | `cl4r1t4s/references/catalog.md` | `Claude-4.txt` → `Claude_4.txt`（与源目录一致） |
| 4 | `cl4r1t4s/concepts/vendor-landscape.md` | 因果表述弱化为相关性解读 |
| 5 | `cl4r1t4s/concepts/defense-lessons.md` | 类别级防御建议补 l1b3rt4s 交叉链接 |
| 6 | `l1b3rt4s/references/catalog.md` | "17/20 命中" → git grep 可复现表述（16/34 + 1 杂项） |
| 7 | `l1b3rt4s/concepts/defense-perspective.md` | NFKC 补全称 |
| 8 | `obliteratus/index.md` | 信任声明补快照 git HEAD `e39f9088…` |
| 9 | `obliteratus/references/architecture-map.md` | METHODS "11 键" → "12 键"（列明构成）；analysis/ "28 个 .py" → "29 个 .py" |
| 10 | `obliteratus/concepts/analysis-modules.md` | "28 个 .py 文件" → "29 个 .py 文件（V 阶段复核一致）" |

## 六、残留风险

1. **l1b3rt4s catalog 的 M 级 T 类别归属**（20 文件）与 cl4r1t4s catalog 的主题注记（如 "会议助手""全栈 Web 生成"）为 R 阶段标记级登记，本轮未逐文件复验条目内容——已通过核验深度标记（D/M）显式降级，引用时应按标记取信。
2. **facts 未登记、本轮补验成立的 5 组数值**（spectral_cascade=6、qwen38 500/142/200、advanced 正则参数组、steering 字段默认值、informed 门控默认值）尚未回写 facts 清单；若后续 S/W 阶段重启，建议回填以免二次漂移。
3. **上游快照锚定**：l1b3rt4s 为 git HEAD 只读核验（工作树已删，天然不可变）；cl4r1t4s 与 obliteratus 为工作树核验并已补 HEAD 锚点，但上游推送后 wiki 数值（尤其 obliteratus 计数类）可能再次漂移——勘误表方法论已提示读者按源码锚点复验。
