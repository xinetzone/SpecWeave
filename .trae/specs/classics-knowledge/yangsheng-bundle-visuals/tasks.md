# 养生经典阅读束配图与 Mermaid 图表增强 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: Seedream 生成 8 张国风配图
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 使用 GenerateImage 工具（Seedream 插件，主会话执行——子代理无此工具）按 spec FR-2 清单生成 8 张图片。
  - 落盘目录：`d:\spaces\SpecWeave\projects\awesome-okf-xs\doc\_static\bundles\yixue\yangsheng\yangsheng-classics-reading\images\`（先建目录）。
  - 路径参数不带扩展名；生成后逐文件确认实际扩展名（.png/.jpg）。
  - 统一风格锚点（每张 prompt 必含）：中国传统国风工笔淡彩插画，宣纸米黄暖色调，赭石/花青/朱砂点染，古朴典雅，宁静氛围，古代人物汉服/古装，**画面中不出现任何文字、书法、印章文字**（规避 AI 文字错乱），无现代物品，4:3 横版构图。
  - 8 张主题 prompt 要点：
    1. `hero-reading-classics`：古代文人书斋，案头摊开竹简与线装古籍，旁置药葫芦、青瓷茶盏、艾草盆栽，窗外竹影透入暖光，寓意养生经典阅读。
    2. `yangsheng-daily-life`：古代庭院日常生活场景，晨起古人舒展导引、家人食饮有节、起居有序的温暖生活意象。
    3. `neijing-huangdi-qibo`：上古明堂之下，帝王形象长者与医者席地问对，远山云气环绕，寓意《黄帝内经》黄帝岐伯问答。
    4. `jikang-bamboo-grove`：魏晋名士宽袍大袖独坐竹林中抚琴，清峻飘逸，竹林七贤意境。
    5. `sun-simiao-herbs`：唐代白发长须老医者背负药篓、手持药锄、腰悬葫芦，山间采药，慈祥清癯（药王孙思邈意象）。
    6. `zunsheng-scholar-studio`：明代文人书斋内景，香炉青烟、茶具、插花、古玩、琴书，文人展卷燕闲，窗明几净。
    7. `elder-congee-care`：庭院中白发老人安坐石桌旁，晚辈双手奉上一碗热粥，旁有炊粥陶罐，温馨孝亲养老场景。
    8. `shanggu-harmony-nature`：上古田园山水，古人顺应四时而居——晨间田间劳作、山间舒展肢体、茅屋炊烟，天人合一意境。
  - 单张失败自动重试，总计不超过 4 次/张；仍失败则记录并在汇总中报告。
- **Acceptance Criteria Addressed**: AC-1, AC-7
- **Test Requirements**:
  - `programmatic` TR-1.1: images 目录下存在 8 个图片文件，文件名 stem 与清单 8 项完全一致。
  - `human-judgement` TR-1.2: 逐张目检——主题与 FR-2 描述吻合；无文字/水印；无现代物品穿越；8 张风格色调统一。
- **Notes**: GenerateImage 的 path 参数不带扩展名；生成后用 LS/Glob 核实实际文件名与扩展名，供 Task 2 引用。

## [x] Task 2: 嵌入 8 处图片引用 + 撰写 6 张 mermaid 图
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 委派 1 个 general_purpose_task 子代理执行全部 Markdown 增量编辑（仅插入，不改正文文字与 frontmatter）。
  - **图片引用**（8 处）：在每篇目标文档首个正文段落之后插入空行 + `![中文alt](/_static/bundles/yixue/yangsheng/yangsheng-classics-reading/images/<stem><实际扩展名>)`；alt 为描述画面的完整中文句。落点：`index.md`（导语段后）、`concepts/00-why-yangsheng.md`、`concepts/01-huangdi-neijing.md`、`concepts/02-ji-kang-yangsheng-lun.md`、`concepts/03-beiji-qianjin-yao-fang-yangxing.md`、`concepts/04-zunsheng-ba-jian.md`、`concepts/05-laolao-hengyan-and-shouqin.md`、`examples/01-suwen-shanggu-tianzhen.md`。
  - **Mermaid**（6 张，语法铁律：节点标签全部双引号；换行仅用 `<br/>`；禁止未加引号的括号/冒号；不用 gantt/复杂语法）：
    - M1 `concepts/06-schools-lineage.md`（"总览"表格之后）：flowchart TD，中心节点"养生文献五脉"；五脉分支——医家脉：《黄帝内经》战国秦汉→《千金要方》唐652→《养老奉亲书》北宋1085前→《老老恒言》清1773；道家脉：《黄庭经》魏晋→《抱朴子内篇》东晋317→《云笈七签》北宋1025-1029；文人脉：嵇康《养生论》三国魏→《遵生八笺》明1591；食养脉：《食疗本草》唐开元→《饮膳正要》元1330；导引脉：马王堆《导引图》前168→五禽戏（华佗/陶弘景描述）→八段锦（南宋得名/清末定型）→《易筋经》明1624。虚线交汇：医家《千金要方》-.->文人脉（引嵇康五难）；《养性延命录》节点横跨道家/导引（虚线双向标注）。
    - M2 `index.md`（"推荐学习路径"节）：用 mermaid flowchart **替换**现有纯文本代码块（三条路径信息无损保留）：起点"开始阅读"→零基础路径（概念00→概念06→示例02→概念01-05→概念07）；版本关注路径（概念07→core-editions→insights）；谱系兴趣路径（概念06→概念01-05→extended-reading）。
    - M3 `concepts/01-huangdi-neijing.md`（"版本常识"节之后）：flowchart LR，素问链："战国秦汉<br/>主体成书"→"唐·王冰762<br/>补运气七篇<br/>编次24卷"→"北宋·林亿1057<br/>校正医书局"→"明·顾从德1550<br/>翻宋刻本（今通行）"→"现代<br/>人卫影印/郭霭春校注"；灵枢旁支："南宋·史崧<br/>整理定本"→"明赵府居敬堂刊本"；注释节点"第72/73篇<br/>刺法论/本病论=遗篇"。
    - M4 `concepts/02-ji-kang-yangsheng-lun.md`（"养生五难与论辩传统"节）：flowchart LR，"嵇康《养生论》"→|"向秀驳难"|"向秀《难养生论》"→|"嵇康回应"|"嵇康《答难养生论》"；虚线："养生五难<br/>（嵇康曰）"-.->|"《千金要方》卷27引录"|"进入医家正统"。
    - M5 `concepts/07-choosing-editions.md`（"四步"导语之后、第一步之前）：flowchart LR，"第一步<br/>辨托名与成书年代"→"第二步<br/>选善本底本现代整理本"→"第三步<br/>查底本说明"→"第四步<br/>对照影印本"。
    - M6 `examples/02-reading-plan.md`（"总体路线"表格之后）：flowchart LR，四周节点："第1周<br/>养生总纲入门<br/>《养生论》+《上古天真论》"→"第2周<br/>医家养性实践<br/>《千金》卷27+《养性延命录》"→"第3周<br/>明代生活百科<br/>《遵生八笺》按笺选读"→"第4周<br/>老年养生专题<br/>《老老恒言》+《寿亲养老新书》"。
  - 编辑前必读目标文件确认最新内容；只做插入/替换 M2 代码块，其余正文一字不动。
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `programmatic` TR-2.1: 8 个文档各含 1 处 `/_static/bundles/yixue/yangsheng/yangsheng-classics-reading/images/` 图片引用，且引用路径（含扩展名）与磁盘文件一一对应（Glob 交叉核对）。
  - `programmatic` TR-2.2: 6 个文档各含 1 个 ```mermaid 栅栏；栅栏内节点标签 100% 双引号包裹；无未加引号的括号节点；换行符仅 `<br/>`。
  - `programmatic` TR-2.3: `git diff --stat` 显示仅 8 个文档被修改（index.md、concepts/00,01,02,03,04,05,06,07 中实际涉及 9 个文件 + examples/01、examples/02——共 11 个 .md；无 frontmatter 改动、无其他文件改动）。
  - `human-judgement` TR-2.4: mermaid 节点文字与 facts.md/正文事实一致（年代、书名、人名）；图与所在章节主题契合。
- **Notes**: M2 是唯一"替换"型编辑（纯文本代码块→mermaid），其余均为插入。图片 alt 不要出现"AI生成"等元信息。

## [x] Task 3: V 对抗审查 + 门控与构建验证（黑盒）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 委派 1 个独立 general_purpose_task 子代理（不看实现过程，只验产出）执行：
  1. **事实对抗（human-judgement 项程序化执行）**：逐张图片打开目检（主题/无文字/无穿越/风格统一）；逐张 mermaid 节点与 facts.md 对账（年代、书名、人名、谱系关系），列出任何不一致。
  2. **门控**：在 `projects/awesome-okf-xs` 执行 `invoke gates.all`（优先 WSL：`wsl -d podman-machine-default` 不可用则 WSL 默认发行版或 Windows py314；记录实际环境），三门须全绿。
  3. **构建**：确保构建环境已装 sphinxcontrib-mermaid（`pip install sphinxcontrib-mermaid` 如缺失），执行 `invoke build`；扫描输出确认无 `image not readable`、无 `Unknown directive`、无新增 warning/error。
  4. **引用完整性**：程序化核对 8 处图片引用路径与磁盘文件（含扩展名）完全一致。
  - 输出结构化审查报告：PASS/FAIL 逐项 + 问题清单（文件、位置、问题、建议修复）。
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-3.1: `invoke gates.all` 退出码 0，toctrees/bundles/utf8 三门全绿。
  - `programmatic` TR-3.2: `invoke build` 成功且无图片/指令类警告（与基线相比零新增警告）。
  - `human-judgement` TR-3.3: 8 图目检通过率 100%（主题吻合、无文字、无穿越、风格统一）。
  - `human-judgement` TR-3.4: 6 张 mermaid 事实对账无错误（每个节点可在 facts.md 或正文找到依据）。
- **Notes**: 若构建环境缺 sphinxcontrib-mermaid，安装后重跑；mermaid 为 CDN 运行时渲染，构建期不验证 JS 渲染，语法安全靠 TR-2.2 规则与本任务人工复核。

## [x] Task 4: 修复回归与收尾（Task 3 全 PASS，无修复项）
- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 按 Task 3 审查报告修复问题（图片主题不符则重新生成单张、mermaid 事实/语法错误则改正文）；每轮修复后重跑相关验证。
  - 自动重试上限 4 轮；超出则停下报告用户。
  - 收尾：汇总变更清单（8 图 + 11 文档编辑点 + 门控/构建结果），不执行 git commit。
- **Acceptance Criteria Addressed**: AC-1~AC-7
- **Test Requirements**:
  - `programmatic` TR-4.1: 复审全部检查项 PASS。
  - `human-judgement` TR-4.2: 变更清单与 spec FR 清单逐项对应，无遗漏、无越界改动。
