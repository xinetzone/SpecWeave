# Tasks

- [x] Task 1: R 阶段——信源采集与事实登记（facts 基础，G1）
  - [x] 1.1 国际脉络调研：用 WebSearch/WebFetch 调研艺术疗愈六大分支的历史与理论主干（Adrian Hill 术语首创与战时实践、Margaret Naumburg 动力取向、Edith Kramer 艺术即治疗、Juliette Alvin、Mary Priestley、Helen Bonny GIM、Nordoff-Robbins、Marian Chace、Mary Whitehouse、Moreno 心理剧、Renee Emunah、Paolo Knill、Shaun McNiff、Levine 夫妇），以及职业组织（AATA/AMTA/ADTA/NADTA/IEATA）官网定义与成立时间；每个关键事实 ≥2 独立信源交叉核对（组织官网/学术文献/WHO/Cochrane 为主信源，维基百科仅作线索）
  - [x] 1.2 循证与中国脉络调研：WHO 2019 scoping review（Fancourt & Finn）与 Cochrane 音乐治疗相关系统综述结论登记；中医五音疗疾/情志相胜古籍原文（对照 ctext.org、维基文库，并核对 `yixue/tcm` 既有束的核对记录）；近现代西方艺术治疗引入中国的关键事实（高校专业建设、职业发展）
  - [x] 1.3 登记各束 facts.md：≥60 条编号事实（前缀按束：OV=总览、AT=美术、MT=音乐、DD=舞动戏剧、EA=表达性、CN=中国），每条带信源 URL，无因果推断词（G1）——实际登记 77 条（OV 11/AT 18/MT 16/DD 11/EA 10/CN 11）
- [x] Task 2: I 阶段——跨束洞察提炼（G2）
  - [x] 2.1 基于 facts 编号提炼总览束 insights.md 6 条四元组洞察（≥3 达标）：先驱卒年系统性后移、术语三层外延、证据规模≠强度、中西话语不可互译、职业定义版本化、五步职业化路径（48 个事实编号经核真实存在）
- [x] Task 3: 生成总览束 `yishu/liaoyu/liaoyu-overview/`（13 文件：5 concepts + 2 examples + references + index/log/facts/insights）
  - [x] 3.1 concepts 5 篇（定义辨析与术语分层、历史脉络与分支谱系、循证证据概貌、职业体系与资源地图、阅读路径）
  - [x] 3.2 examples 2 篇（分支选择决策指南、资料可信度五步评估法）
  - [x] 3.3 references 信源登记 + index.md（toctree）+ log.md + facts.md/insights.md 收编
- [x] Task 4: 生成美术治疗束 `yishu/liaoyu/art-therapy/`（14 文件，5 concepts + 2 examples）
- [x] Task 5: 生成音乐治疗束 `yishu/liaoyu/music-therapy/`（14 文件，5 concepts + 2 examples）
- [x] Task 6: 生成舞动与戏剧治疗束 `yishu/liaoyu/dance-drama-therapy/`（14 文件，5 concepts + 2 examples）
- [x] Task 7: 生成表达性艺术治疗束 `yishu/liaoyu/expressive-arts/`（11 文件，4 concepts + 1 example）
- [x] Task 8: 生成中国艺术疗愈束 `yishu/liaoyu/china-art-therapy/`（12 文件，5 concepts + 1 example）
- [x] Task 9: E 阶段——萃取 3 个可复用模式并入总览束 insights.md（G3：双源核年法/引文分层法/五步职业化判读框架，各含触发场景+核心步骤+反模式+检验标准+跨领域迁移示例）
- [x] Task 10: 索引更新（三方联动）
  - [x] 10.1 新增 `yishu/liaoyu/index.md`（type: group，六束导航表 + toctree）
  - [x] 10.2 更新 `yishu/index.md`（域描述、分组导航表新增 liaoyu 行、toctree 追加）
  - [x] 10.3 更新 `bundles/index.md` 五面（frontmatter 计数 389/44、正文计数行、yishu 域行 7 束·2 组、mermaid 节点描述；toctree 域级无需变更）；并行会话 kexue +5 束合并计数后以目录树地面真值对齐
- [x] Task 11: V 阶段——对抗审查
  - [x] 11.1 事实抽查 13 条回访信源 URL（11 条一致；2 条 WHO 官方 URL 不可达已在 sources.md 登记可达性审查记录）
  - [x] 11.2 中医古籍引文逐字核对（东方段/九气段/五法/按语与 facts 逐字一致）+ 现代著作引用版权边界检查（无整段转录，P0=0）
  - [x] 11.3 合规审查：7 处免责声明可见、证据表述无夸大、G1 因果词 0 命中、YAML safe_load 83 文件全过；5 处快修已落地（CN-08 细节单源标注、DD-08 弱信源披露、WHO 可达性记录、全角引号统一、ATCB 首现展开）
- [x] Task 12: C 阶段——质量门与原子提交
  - [x] 12.1 三门全绿：`check-utf8.py`（7518 文件）/ `check-toctrees.py` / `check-bundles-index.py`（9 域/44 组/389 束五面一致）+ 两门自检探针通过（因 `invocations` 模块缺失改为直接运行底层脚本，等效 `invoke gates.all`）
  - [x] 12.2 按束原子提交 7 个（010b98fd 总览 / b0b6e84f 美术 / c1a867e8 音乐 / 883e3db5 舞动戏剧 / bdd724ee 表达性 / eee4551a 中国 / 2f9bccc5 索引），UTF-8 -F 提交信息无乱码；pathspec 限定提交实现暂存隔离，并行会话已暂存的 kexue 文件原样保留未被带走；仅本地提交未推送（推送闸门维持用户指令）

# Task Dependencies

- Task 2 依赖 Task 1（洞察必须引用事实编号）✓ 已满足
- Task 3、4、5、6、7、8 均依赖 Task 1 与 Task 2（内容以 facts/insights 为纲）；Task 4-8 之间无依赖已并行 ✓
- Task 9 依赖 Task 3-8（模式萃取基于束内容）；Task 10 依赖 Task 3-8（索引登记全部新文件）✓
- Task 11 依赖 Task 9 与 Task 10；Task 12 依赖 Task 11 ✓
