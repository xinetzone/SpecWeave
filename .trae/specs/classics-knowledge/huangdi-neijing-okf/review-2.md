# 《黄帝内经》OKF 知识包（neijing-reading）C 阶段整改后复审报告

## 〇、元信息

| 项 | 内容 |
|---|---|
| 审查对象 | `projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/`（32 个 .md）及分组落地页 `huangdi-neijing/index.md`（1 个），合计 33 个 .md |
| 复审性质 | C 阶段整改后独立复审（fresh context，未参与生成与初审），针对初审 `review.md`（结论 FAIL：1 Blocker + 10 Major + 5 Minor，共 16 项）逐条核验 |
| 审查员 | 独立对抗性内容审查子代理 |
| 审查日期 | 2026-08-31 |
| 审查语言 | 中文 |
| 审查方法 | 通读 bundle 全部 33 文件（facts/insights/log/index 全读、concepts 12 篇全读或抽读、examples 9 篇全读或抽读、references 4 篇全读或抽读）→ 16 项修复逐条文件:行号取证 → 全包反向关键字归零搜索 → frontmatter/结构/占位符扫描 → S7/S12 信源编号一致性核查 → ctext 在线补核（2 次请求：1 次成功取至本篇第 5 段、1 次触发限流页）→ 门检复跑 |
| 门检命令 | `python scripts\check-toctrees.py "doc\bundles\think\huangdi-neijing"`（cwd=`projects/awesome-okf-xs`） |

> **审查纪律声明**：复审员未修改 bundle 内任何文件；本报告所有判定均基于复审员亲自读取的文件内容与亲自执行的搜索/门检/网络请求，证据给出文件与行号；无法直核者如实标注"未能直核"，不猜测结论。

---

## 一、结论

### ✅ **PASS（复审通过）**

- 初审 16 项缺陷（B-1、M-1~M-10、m-1~m-5）**全部真实落盘修复**，逐条核验见表 §二；
- 反向归零搜索：全部错误写法 0 命中（"1135"仅存于 log.md 整改叙述"1135→1155"中，属应保留内容）；
- 未发现修复引入的新问题：占位符 0 命中、水平线/frontmatter/toctree 结构完好、门检 **EXIT=0**；
- 信源编号 S7/S12 全包一致（F-110 仅 S7；F-112 保留 S7/S12 与初审"勿报"说明一致；examples/06 底本行与 log.md legend 均已纠正）；
- 非医疗声明覆盖完整（bundle 根 index、分组 index、concepts/00 专节、examples 全 9 篇篇头警示、concepts/06 新增篇末边界段）；
- 唯一未竟事项：病机十九条整段 ctext 四部丛刊页**本次复审仍未能直核**（首次请求成功但仅取至本篇第 5 段，十九条在后半篇；第二次请求即触发 ctext 限流页）——bundle 校记已如实标注"未直核"，且复审员从成功获取的 ctext 同篇第 4 段独立验证"氣上衝胸/病衝頭痛/上衝心痛"均作"衝"，与校记自称的旁证一致。列为 Minor 观察项，不阻断发布。

---

## 二、16 项修复逐条核验表

| 项次 | 缺陷与修复声称 | 复审证据（文件:行号） | 判定 |
|---|---|---|---|
| **B-1** | 史崧献《灵枢》年份 1135→1155，共 5 处；1135 仅应存于 log.md 整改叙述 | ① [facts.md:65](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/facts.md#L65) F-028："南宋绍兴乙亥年（**1155**）"；② [insights.md:20](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/insights.md#L20)："史崧 **1155** 年献本定型"；③ [concepts/00-why-read-neijing.md:23](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/concepts/00-why-read-neijing.md#L23)："南宋史崧 **1155** 年献家藏本"；④ [concepts/01-authorship-and-editions.md:65](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/concepts/01-authorship-and-editions.md#L65)："南宋绍兴乙亥（**1155**），史崧献出家藏《灵枢》"；⑤ [references/editions.md:38](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/references/editions.md#L38)："**1155**（南宋绍兴乙亥）｜史崧献《灵枢》"；"1135"全包仅 [log.md:34](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/log.md#L34) 整改叙述"1135→1155"一处 | ✅ 已修复 |
| **M-1** | F-110 信源 S7/S12→S7；F-112 保留 S7/S12 勿报 | [facts.md:174](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/facts.md#L174) F-110 信源列仅"**S7**"（"熱因熱用，寒因寒用"读法归王洪图系统）；[facts.md:176](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/facts.md#L176) F-112 信源列"S7/S12"（求属句两源皆载，保留正确）；异文双录 F-111 为"S3/S12/S7"（[facts.md:175](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/facts.md#L175)），与异文内容对应 | ✅ 已修复 |
| **M-2** | examples/06 底本行信源改 S12；log.md R 阶段叙述与末行 legend 的 S7/S12 互换 | ① [examples/06-zhizhen-yao.md:24](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/06-zhizhen-yao.md#L24)："黄元御《素问悬解》（**S12**，cloudtcm）"；② [log.md:9](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/log.md#L9) R 阶段信源网络："cloudtcm《素问悬解》（**S12**）"；③ [log.md:47](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/log.md#L47) legend："**S7=王洪图《内经选读》教材/讲课；S12=cloudtcm《素问悬解》**"，与 [facts.md:19](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/facts.md#L19)、[facts.md:24](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/facts.md#L24) 信源表一致；全包搜索"（S7，cloudtcm）"类错误组合 0 命中 | ✅ 已修复 |
| **M-3** | "恬惔虛无"（非"恬惔虛無"） | [concepts/09-yangsheng.md:41](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/concepts/09-yangsheng.md#L41) blockquote："恬惔虛**无**，真氣從之"；另 [facts.md:144](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/facts.md#L144) F-080、[examples/01-shanggu-tianzhen.md:46](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/01-shanggu-tianzhen.md#L46) 同句均作"无"，examples/01:48 另有专条异文注记 | ✅ 已修复 |
| **M-4** | "鬭而鑄錐"（非"鬥而鑄錐"） | [concepts/09-yangsheng.md:71](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/concepts/09-yangsheng.md#L71)："譬猶渴而穿井，**鬭**而鑄錐"；同字另见 [facts.md:150](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/facts.md#L150) F-086、[examples/02-siqi-tiaoshen.md:52](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/02-siqi-tiaoshen.md#L52)、[concepts/07-diagnostics.md:76](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/concepts/07-diagnostics.md#L76)；examples/02:54 出"鬭/鬥"异体校记 | ✅ 已修复 |
| **M-5** | "精氣溢寫"（非"精氣溢瀉"） | [concepts/09-yangsheng.md:52](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/concepts/09-yangsheng.md#L52) 丈夫条："二八腎氣盛、天癸至、精氣溢**寫**"；另 [facts.md:146](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/facts.md#L146) F-082、[examples/01-shanggu-tianzhen.md:58](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/01-shanggu-tianzhen.md#L58) 同句均作"寫"，examples/01:60 出"寫/瀉"古今字注记 | ✅ 已修复 |
| **M-6** | 治皮毛段作"其次治六府，其次治五藏。治五藏者，半死半生也"（非"五臟"） | [concepts/07-diagnostics.md:66](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/concepts/07-diagnostics.md#L66) blockquote："故善治者治皮毛，其次治肌膚，其次治筋脈，其次治六府，其次治五**藏**。治五**藏**者，半死半生也"（同段"筋脈""六府"未动，正确）；另 [facts.md:164](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/facts.md#L164) F-100、[examples/04-yinyang-yingxiang.md:72](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/04-yinyang-yingxiang.md#L72) 同段均作"五藏"；全包"五臟"0 命中 | ✅ 已修复 |
| **M-7** | examples/02 冬三月引文补"使志若伏若匿，若有私意，若已有得"14 字 | [examples/02-siqi-tiaoshen.md:44](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/02-siqi-tiaoshen.md#L44) 冬三月 blockquote："早臥晚起，必待日光，**使志若伏若匿，若有私意，若已有得**，去寒就溫，無泄皮膚，使氣亟奪"——14 字已在段中，衔接自然，全文无省略号残留 | ✅ 已修复 |
| **M-8** | "天運當以日光明"（有"日"字） | [facts.md:152](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/facts.md#L152) F-088："故天運當以**日**光明，是故陽因而上"；[examples/03-shengqi-tongtian.md:36](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/03-shengqi-tongtian.md#L36) 同句一致 | ✅ 已修复 |
| **M-9** | 十九条作"諸氣膹鬱""諸逆衝上"（鬱非郁、衝非冲），与 concepts/08 统一，并出字形校记如实标注未直核 | 字形统一三处：[facts.md:170](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/facts.md#L170) F-106、[examples/06-zhizhen-yao.md:35](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/06-zhizhen-yao.md#L35)、[concepts/08-treatment-principles.md:30](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/concepts/08-treatment-principles.md#L30) 均作"諸氣膹**鬱**……諸逆**衝**上"；用字注记 [examples/06:39](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/06-zhizhen-yao.md#L39)；字形校记 [examples/06:40](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/06-zhizhen-yao.md#L40) 如实写明"十九条整段所在页当次抓取遇限流未直核"，并记载同篇"氣上衝胸、病衝頭痛、上衝心痛"已逐字核作"衝"；[log.md:40](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/log.md#L40) 同步叙述 | ✅ 已修复（ctext 整段直核仍为遗留观察项，见 §五、§七） |
| **M-10** | insights.md 事实计数 128→137 | [insights.md:3](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/insights.md#L3)："基于事实清单（facts.md，**137 条**）"；与 facts.md 实点 F-001~F-137（末行 [facts.md:205](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/facts.md#L205) 自称 137 条）及 bundle 根 [index.md:61](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/index.md#L61) 一致；全包"128 条/128條"0 命中 | ✅ 已修复 |
| **m-1** | concepts/06 篇末新增"阅读边界"非医疗声明段（--- 分隔） | [concepts/06-disease-causes.md:79-81](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/concepts/06-disease-causes.md#L79-L81)：第 79 行为"---"（前后均空行，结构完好），第 81 行"**阅读边界**：……不是现代病原学结论，也不构成养生或诊疗建议；不得据本 bundle 内容自我诊断、自我调治，健康问题请咨询具备资质的执业医师。" | ✅ 已修复 |
| **m-2** | F-125 与 examples/08 肺经引文作"膨脹而喘咳"（非"膨膨"） | [facts.md:189](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/facts.md#L189) F-125："是動則病肺脹滿，**膨脹**而喘咳"；[examples/08-jingmai.md:47](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/08-jingmai.md#L47) 同句一致；全包"膨膨"0 命中；同段"喘渴"（翻案 R-1 确认的底本原字）保留未动 | ✅ 已修复 |
| **m-3** | facts.md 凡例新增"简体信源引文繁体化"说明行 | [facts.md:7](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/facts.md#L7) 用字凡例："简体信源（S3/S4/S5/S6 等）引文经繁体化转录；凡 S1/S2 四部丛刊底本可核的段落，用字一从底本（如鍼、麤、寫、藏、鬭、无、痒、栗、衝、鬱、脹、飱）；仅见于简体信源的段落照录原字并随条标注。" | ✅ 已修复 |
| **m-4** | F-137 与 examples/02 秋三月作"冬為飱泄"并附异体注记 | [facts.md:201](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/facts.md#L201) F-137："逆之則傷肺，冬為**飱**泄，奉藏者少"，条末附注："'飱'为'飧'的四部丛刊本异体；《阴阳应象大论》'夏生飧泄'从'飧'，二字为异体"；[examples/02-siqi-tiaoshen.md:40](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/02-siqi-tiaoshen.md#L40) 引文作"飱"，[examples/02:56](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/02-siqi-tiaoshen.md#L56) 出专条字形注记；《阴阳应象大论》侧"夏生飧泄"仍从"飧"（[concepts/06:53](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/concepts/06-disease-causes.md#L53)、[facts.md:195](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/facts.md#L195) F-131），异体双形各随底本且互注，符合规则 | ✅ 已修复 |
| **m-5** | log.md 用字规则限定"太衝脈"，穴名"太沖"不得误改 | [log.md:21](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/log.md#L21)："太**衝脈**（脈名作'衝'；肝经原穴'太**沖**'底本即作'沖'，勿改）"；穴名"太沖"完好保留于 [facts.md:185](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/facts.md#L185) F-121 与 [examples/07-jiuzhen-shier-yuan.md:62](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/07-jiuzhen-shier-yuan.md#L62)（"肝……出於太沖"）；脉名"太衝脈"见于 [facts.md:145](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/facts.md#L145) F-081、[examples/01:54](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/01-shanggu-tianzhen.md#L54)——"脉名衝、穴名沖"双规则均未被破坏 | ✅ 已修复 |

**小结**：16/16 项全部判定"已修复"，无虚假整改、无半改漏改。

---

## 三、反向归零搜索结果

对全 bundle 目录（`huangdi-neijing/`，含分组 index 与 neijing-reading 全部子目录）执行关键字搜索，结果如下：

| 搜索关键字 | 命中数 | 命中位置与判定 |
|---|---|---|
| `1135` | 1 | 仅 [log.md:34](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/log.md#L34) 整改叙述"年份 1135→1155（……1135 为乙卯年）"——系整改说明应保留内容，**归零判定通过** |
| `恬惔虛無` | 0 | ✅ 归零 |
| `溢瀉` | 0 | ✅ 归零 |
| `膨膨` | 0 | ✅ 归零 |
| `天運當以光明`（脱"日"形） | 0 | ✅ 归零（"天運當以日光明"正向命中 facts.md:152、examples/03:36） |
| `五臟` | 0 | ✅ 全包 0 命中（治皮毛段及各引文均作"五藏"） |
| `膹郁` | 0 | ✅ 归零 |
| `諸逆沖`／`逆沖上`／`沖上` | 0 | ✅ 归零 |
| `鬥而鑄錐` | 0 | ✅ 归零（"鬥"单字仅出现于 log.md:21、examples/02:54、examples/index.md:26 的规则说明/校记语境，均为"鬭（鬥）"对照表述，非引文） |
| `128 条`／`128條` | 0 | ✅ 归零（F-128 为事实编号，不含"条"字，不误伤） |
| `S7，cloudtcm`／`S7,cloudtcm` | 0 | ✅ 错误信源组合归零 |
| `@NL`／`@ @`（占位符） | 0 | ✅ 归零 |
| `TODO`／`FIXME`／`XXX`／`待补`／`占位` | 0 | ✅ 归零 |
| `針`（灵枢引文应作"鍼"） | 0 处引文 | "針"仅出现于 log.md:21、examples/07:22、examples/index.md:26 的"鍼（非針）"规则说明；全部灵枢引文（concepts/05:69、examples/07:33/37/43/47、facts F-114~F-118）均作"鍼"。另"《针经》"为书名专称（F-003、concepts/01 等），属现代叙述语境，不违规 |
| `雲`（"吹云"应作"云"） | 0 处引文 | 仅出现于规则说明"云（非雲）"；引文中"若風之吹云"（facts.md:182 F-118、examples/07:53）作"云" |

---

## 四、新问题扫描结果（修复是否引入新缺陷）

| 扫描项 | 方法 | 结果 |
|---|---|---|
| 占位符/模板残留 | 全包搜索 `@NL`、`@ @`、`TODO`、`FIXME`、`待补`、`占位` | **0 命中** ✅ |
| Markdown 水平线结构 | 全包枚举 `^---$` 并检查前后行 | 所有 frontmatter 开闭（26 个内容文件 + bundle 根 index）与正文水平线（facts.md:27/203、insights.md:5/52、concepts/06:79 新增段等）前后均有空行；concepts/06 新增"阅读边界"段为"空行 + --- + 空行 + 正文"，结构完好 ✅ |
| 列表/表格缩进 | 通读改动文件（concepts/06、examples/02、06、08、facts.md、log.md） | 表格列数一致、bullet 缩进正常，未发现破损 ✅ |
| bundle 根 frontmatter | [index.md:1-13](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/index.md#L1-L13) | `type: OKF` + `okf_version: "0.2"`（全包唯一一处），generated/verified/status/stale_after 齐全 ✅ |
| 内容文件 frontmatter | 全包搜索 `^type: ` | 26 个文件：1 OKF + 12 Concept + 9 Example + 4 Reference，类型与目录归属一致；Concept/Example 均含 verified 字段；Reference 无 verified（与初审确认的房屋惯例一致）✅ |
| 目录 index | concepts/index.md、examples/index.md、references/index.md、分组 index.md | 四者均**无 frontmatter**、以 `#` 标题开头，且均含 ````{toctree}` 块（concepts/index:31-47 列 12 篇、examples/index:30-43 列 9 篇、references/index:19-27 列 4 篇、分组 index:15-20 列 neijing-reading/index）✅ |
| toctree 门检 | 复跑 `python scripts\check-toctrees.py "doc\bundles\think\huangdi-neijing"` | 输出"toctree 检查通过： 全部 index.md 引用有效，所有内容文档均可达。"**EXIT=0** ✅ |
| 修复连带改动核对 | 比对改动点上下文 | examples/02 新增 14 字后冬三月段完整；concepts/06 新增边界段未破坏原有六节结构；log.md C 阶段叙述（L33-43）与实际落盘内容逐项相符，未发现"声称已改实际未改"项 ✅ |

**未发现修复引入的新问题。**

---

## 五、ctext 十九条补核结果

**结论：十九条整段 ctext 四部丛刊正字本次复审仍"未能直核"；但取得同篇旁证，且 bundle 校记的诚实性经独立验证为真。**

复审员于 2026-08-31 发起 3 次 ctext 请求：

1. **第 1 次请求成功**：`https://ctext.org/huangdi-neijing/zhi-zhen-yao-da-lun/zh`（《素问·至真要大论》繁体页）正常返回，页首明确标注底本为"**《四部叢刊初編》本《重廣補註黃帝內經素問》：至真要大論**"——与 bundle S1 底本声称一致。但该页转存内容仅含本篇第 1~5 段（页面体量超限截断），**病机十九条所在的后半篇段落（"帝曰：願聞病機何如"段）不在已获取内容中**，故"諸氣膹鬱"之"鬱"、"諸逆衝上"之"衝"在十九条语境下的底本正字**未能直核**。
2. **第 2 次请求**（ctext 站内检索 `膹鬱`）与**第 3 次请求**（单段节点接口 `text.pl?node=82906`）均返回 ctext 限流页："Access to ctext.org is unavailable from your current location……嚴禁使用自動下載軟体"——与 bundle F-069 记录的限流机制（连续抓取约 6 页后限流）相符。
3. **同篇旁证（直核成功）**：在第 1 次请求获取的本篇第 4 段中，复审员逐字读到 ctext 底本作"**氣上衝胸**"（少陰在泉热淫条）、"**病衝頭痛**"（太陰在泉湿淫条）、"**上衝心痛**"（太陽在泉寒淫条）——三处表"气上逆"义的字**均作"衝"**。这与 [examples/06:40](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/06-zhizhen-yao.md#L40) 校记自称"同篇表'气上逆'诸句（氣上衝胸、病衝頭痛、上衝心痛）均作'衝'，已逐字核"**完全一致**，证明该校记所述旁证真实可信。同段另见"以鹹**寫**之"，亦与"寫"字规则一致。
4. "鬱"字：复审员本次未取得 ctext 直核证据，**不作字形结论**；bundle 以"鬱"为繁体正字、"郁"为简体网络本字形的处理与凡例（facts.md:7）及传统文献通行繁体形态一致，且已在校记中如实标注未直核状态，处置诚实。

按审查纪律，本项不猜测、不替 bundle 下"ctext 正字即如此"的定论；建议后续 ctext 冷却后由维护者择期直核十九条整段页并更新校记（列为 Minor 观察项，不阻断本次 PASS）。

---

## 六、抽查引文结果（底本用字一致性，≥5 段）

除 16 项修复点外，复审员另抽查以下底本引文与 ctext 四部丛刊繁体用字规则的一致性（多数经初审在线比对或本次 ctext 同篇直核）：

| # | 用字规则 | bundle 证据（文件:行号） | 判定 |
|---|---|---|---|
| 1 | 《灵枢》作"鍼"不作"針" | [examples/07:33](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/07-jiuzhen-shier-yuan.md#L33)（"欲以微鍼通其經脈……先立鍼經"）、:37、:43、:47（九针全段"鑱鍼/員鍼/鍉鍼/鋒鍼/鈹鍼/員利鍼/毫鍼/長鍼/大鍼"）、[concepts/05:69](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/concepts/05-meridians-and-nine-needles.md#L69)、facts F-114~F-118 | ✅ 全作"鍼" |
| 2 | "麤守形"作"麤" | [examples/07:37](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/07-jiuzhen-shier-yuan.md#L37)（"麤守形，上守神"）、[facts.md:179](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/facts.md#L179) F-115，examples/07:39 出"麤/粗"异体注记 | ✅ |
| 3 | "若風之吹云"作"云" | [examples/07:53](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/07-jiuzhen-shier-yuan.md#L53)、[facts.md:182](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/facts.md#L182) F-118 | ✅ |
| 4 | "寫"（瀉）字规则 | "濕勝則濡**寫**"（[facts.md:161](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/facts.md#L161) F-097、[examples/04:46](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/04-yinyang-yingxiang.md#L46)）；"盛則**寫**之"（[examples/08:53](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/08-jingmai.md#L53)、F-126）；ctext 至真要大论第 4 段本次直核作"以鹹**寫**之" | ✅ 三处一致 |
| 5 | "藏/府"规则 | "受五**藏**六**府**之精而**藏**之，故五**藏**盛乃能**寫**"（[facts.md:146](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/facts.md#L146) F-082、[examples/01:58](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/01-shanggu-tianzhen.md#L58)）；"五藏五俞……六府六俞"（[examples/07:57](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/07-jiuzhen-shier-yuan.md#L57)）；全包"五臟/六腑"0 命中（"六腑"仅见现代叙述表格，如 concepts/07:73 表格层，非引文） | ✅ |
| 6 | "鬭"字规则 | "鬭而鑄錐"4 处（facts F-086、examples/02:52、concepts/09:71、concepts/07:76） | ✅ |
| 7 | "恬惔虛无"作"无" | facts F-080、examples/01:46、concepts/09:41 三处 | ✅ |
| 8 | 十九条"痒/栗" | "**諸痛痒瘡**……**諸禁鼓栗**，如喪神守"（[examples/06:35](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/06-zhizhen-yao.md#L35)、[facts.md:170](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/facts.md#L170) F-106、[concepts/08:30](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/concepts/08-treatment-principles.md#L30)），"痒"非"癢"、"栗"非"慄" | ✅ |
| 9 | "飱/飧"异体各随底本 | 秋三月"冬為**飱**泄"（F-137、examples/02:40）与《阴阳应象大论》"夏生**飧**泄"（F-131、concepts/06:53）双形并存且互注 | ✅ |
| 10 | "脉名衝、穴名沖"双规则 | "太**衝**脈盛/衰少"（F-081、examples/01:54）与"其原出於太**沖**"（F-121、examples/07:62）各守其字 | ✅ |

抽查 10 组（要求 ≥5 段，实际覆盖 20 余处引文）**全部合规**。

---

## 七、遗留问题清单

### Blocker
无。

### Major
无。

### Minor（观察项，不阻断发布）

1. **【观察项，非缺陷】十九条整段 ctext 直核未竟**：病机十九条整段所在 ctext 页面，初审与本次复审均因限流/截断未直核（本次复审成功取至该篇第 5 段，十九条在后半篇）。bundle 已在 [examples/06:40](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/examples/06-zhizhen-yao.md#L40) 如实标注"未直核"，且其声称的同篇"衝"字旁证经复审员独立直核为真（ctext 至真要大论第 4 段"氣上衝胸/病衝頭痛/上衝心痛"三例）。建议维护者在 ctext 冷却后择期直核该页，确认"鬱"字后可将校记中的"未直核"标注升级为"已核"。
2. **【体例观察，初审基线即如此】** concepts/02、03、04、11 四篇无篇内医疗边界段（02 为结构路径、03/04 为理论框架、11 为注本导航，临床操作性弱）；安全声明由 bundle 根 index"首要声明"（[index.md:23-25](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/index.md#L23-L25)）、分组 index 阅读边界声明、concepts/00 专节（L55-62）及 examples 全 9 篇篇头"⚠️ 文献精读，非医疗建议"承担；concepts/06 边界段补齐后，临床相关概念篇（05/06/07/08/09/10）边界覆盖已齐。此为初审接受的覆盖形态，记录在案。
3. **【极次要，转述截断】** [concepts/09-yangsheng.md:65](file:///d:/spaces/SpecWeave/projects/awesome-okf-xs/doc/bundles/think/huangdi-neijing/neijing-reading/concepts/09-yangsheng.md#L65) 四季作息情志表"冬三月·情志要领"单元格引作"使志若伏若匿，若有私意"，未含末四字"若已有得"。该格为摘要表转述（非 blockquote、无逐字全文声称），且完整 14 字已在 examples/02:44 引文与同表"冬三月"作息语境中正确呈现，不构成伪全文；若追求体例极致，可在该格补全为 14 字。

### 其他复核确认事项（无问题）

- 非医疗声明覆盖：bundle 根 index（首要声明 + "不是医书，不构成任何医疗建议" L21/25）、分组 index（L11-13 阅读边界声明）、concepts/00（⚠️ 非医疗用途声明专节）、concepts/05/06/07/08/09/10（各有边界段/读法边界节）、examples 全 9 篇（篇头 ⚠️ 警示 + 篇尾"可以/不可以怎么用"栏 + 执业医师提示，examples/07 另有"严禁据以自行施针"、examples/08 有"针灸操作请寻求执业针灸医师"）——覆盖完整。
- 信源编号一致性：facts.md 信源表 S1~S13 与 log.md legend、electronic-sources.md 分级、各条事实/各篇底本行互相一致；全包 S7 均指王洪图教材/讲课系统、S12 均指 cloudtcm《素问悬解》，未发现残留颠倒。
- 门检：check-toctrees.py **EXIT=0**（"全部 index.md 引用有效，所有内容文档均可达"）。
- AC-10 原子提交属 C 阶段流程事项（log.md:43 已记录提交意图），不属本内容复审判定范围。

---

## 八、复审总评

初审 16 项缺陷（1 Blocker + 10 Major + 5 Minor）经逐条独立取证，**16/16 真实修复落盘**；反向错误写法全部归零；未发现修复引入的新结构/编号/占位符问题；门检通过；非医疗声明与信源体系一致性完好。唯一未竟事项（十九条 ctext 整段直核）已在 bundle 内诚实标注且其旁证经复审员在线验证为真，列为 Minor 观察项。

**复审结论：✅ PASS——同意进入发布/提交流程。**
