# 《黄帝内经》束配图与 Mermaid 增强 - The Implementation Plan (Decomposed and Prioritized Task List)

> 执行约定：① T1 由主控会话执行（GenerateImage 仅主控可用）；T2~T5 委托子代理。② 禁止任何 git add/commit。③ 所有 Mermaid 遵循安全编码规则（以 .agents/scripts/lib/checks/mermaid.py 实测为准）：无空行、中文/含空格文本双引号、节点 ID 英文、subgraph 用 `EN_ID ["中文"]`、边标签 `-->|"标签"|`、围栏全小写 ```mermaid；**标签必须保持单行，严禁 `<br/>`（检查器判 error）**；另禁用带圈数字①②③（error）、中文方括号【】（error）、Unicode 箭头符号→（warning，边用 mermaid 语法箭头）；subgraph 内禁嵌套 direction。④ Mermaid 内容必须先读目标文档与 facts.md 再制图，零编造。⑤ 图片引用范式（T1 实际产物为 .jpg，引用必须用 .jpg 扩展名）：`![描述性alt](/_static/bundles/yixue/huangdi-neijing/images/<name>.jpg)`。⑥ 注意：主仓库 check-mermaid 扫描器 EXCLUDED_DIRS 含 projects/，对子模块文件不生效；验证时用内联 Python 直接调用 `lib.checks.mermaid._process_file` 对目标文件原位校验（T2 已实测可行）。

## [x] Task 1: 生成 6 张 Seedream 文化意境配图（主控执行）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 用 GenerateImage 工具生成以下 6 图，目标目录 `D:\spaces\SpecWeave\projects\awesome-okf-xs\doc\_static\bundles\yixue\huangdi-neijing\images\`（目录不存在则创建；path 参数不带扩展名）。
  - **统一风格后缀（每张 prompt 必含）**："Traditional Chinese Song-dynasty academy gongbi painting style, ink-and-wash with light color (qianjiang), warm aged-silk background, muted earth pigments, elegant and serene, no text, no calligraphy, no seals, no readable characters, no letters, no modern objects"
  - 图 1 `hero-qibo`（尺寸 landscape_16_9）：黄帝与岐伯对坐问答于古松下石台，矮木案上置竹简帛书，远山流烟；青碧与暖赭配色；书斋问道氛围。用途：束首页 hero。
  - 图 2 `editions-slips`（landscape_4_3）：汉代竹简以丝绳编联、一卷展开的帛书、青铜油灯、砚台并陈于旧木案，烛光暖照，深棕琥珀色调，博物静物画风。用途：concepts/01 版本流传。
  - 图 3 `yinyang-landscape`（landscape_4_3）：一幅意境山水——一侧日照山坡、雾气升腾，另一侧月夜幽谷、静水沉影，一条曲流连接明暗；圆形平衡构图暗示阴阳对待，**禁止画太极鱼符号**；水墨淡彩。用途：concepts/03 阴阳五行。
  - 图 4 `nine-needles`（landscape_4_3）：九支形制各异的古铜/铁针陈于深色丝垫与漆木匣中，旁置竹简与小葫芦；深靛丝底配暖铜色，侧光；定位为**艺术静物而非技术图谱**，不追求针形精确。用途：concepts/05 经络与九针。
  - 图 5 `four-seasons`（landscape_16_9）：连续山水长卷一景含四季——左起春（柳芽桃花）、夏（荷塘青峰）、秋（红枫收田）、冬（雪松冰溪），每季一小亭；青绿工笔长卷，绢本暖底。用途：concepts/09 养生/四季调神。
  - 图 6 `yunqi-celestial`（landscape_4_3）：环形中国古天文星图浮于云间，风格化星宿、五色微光代表五星、风云纹环绕圆图；汉唐天文艺术风，深靛夜空配暖金朱砂点；装饰性、符号化，**无可读文字**。用途：concepts/10 五运六气。
  - 每张生成后确认文件实际落盘且大小正常（>100KB）；若某张出现文字/现代元素/严重畸形，重生成（同主题最多 2 次，仍失败则记录并降级处理）。
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `programmatic` TR-1.1: 6 个 JPG 文件存在于目标目录（hero-qibo/editions-slips/yinyang-landscape/nine-needles/four-seasons/yunqi-celestial，实际扩展名为 .jpg），文件大小 >100KB（实测 522KB~1.2MB，已核验）。
  - `human-judgement` TR-1.2: 逐张目检无文字/字母/印章/现代元素；六张风格统一；主题与用途匹配；图 3 无太极符号、图 4 为静物意境。
- **Notes**: prompt 开头带用途标签（如 "[Book cover illustration for a classical Chinese medicine reading guide]"）以利模型理解语境。

## [x] Task 2: 概念篇 Mermaid 与配图插入（第一批：01/02/03/05）
- **Priority**: high
- **Depends On**: Task 1（图片需先落盘）
- **Description**: 委托子代理，拥有文件：concepts/01-authorship-and-editions.md、02-structure-and-reading-path.md、03-yinyang-wuxing.md、05-meridians-and-nine-needles.md。
  - **先读后画**：通读 4 篇正文 + facts.md 相关节（版本流传史、八篇定位、十二经/九针事实）。
  - M2.1（02 篇，"二、《素问》的内容板块"或"四、推荐阅读路径"附近）：flowchart 展示《素问》81 篇板块（养生/阴阳藏象/病机诊法/治则/运气七篇+遗篇）与《灵枢》81 篇（经络/九针/针灸）分工，及三级阅读路径（零基础→进阶→研究）的流向。节点文字以 02 篇正文为准。
  - M2.2（03 篇，"四、五行"表格之后）：五行相生相胜环——相生环 木→火→土→金→水→木（边标签"相生"），相胜环 木→土→水→火→金→木（边标签"相胜/所胜"）。参照 `guoxue/yinyangjia/yinyangjia/concepts/03-wude-zhongshi.md` 的环形 flowchart 范式。
  - M2.3（05 篇，"一、经络系统"或"二、十二经脉叙事"附近）：十二经脉气血流注环：手太阴肺→手阳明大肠→足阳明胃→足太阴脾→手少阴心→手太阳小肠→足太阳膀胱→足少阴肾→手厥阴心包→手少阳三焦→足少阳胆→足厥阴肝→（环回肺）。节点 ID 英文，标签中文经名。
  - 图片插入（裸 `![alt](path)`，单独成段，置于首节正文之后；扩展名一律 .jpg）：01 篇 `editions-slips.jpg`；03 篇 `yinyang-landscape.jpg`；05 篇 `nine-needles.jpg`。alt 须描述画面内容；05 篇 alt 含"意境图"定位。
  - 每张图/表前加一句引导语（如"版本流传的关键节点如下图所示："），图表后正文保持不重复。
  - 完成后对 4 文件运行 `python check_mermaid.py`（路径：仓库根 `check_mermaid.py` 或 `.agents/scripts/check-mermaid.py`，先确认脚本位置）确保零 error。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-5, AC-7
- **Test Requirements**:
  - `programmatic` TR-2.1: 3 张 Mermaid 通过 check-mermaid.py 零 error；3 条图片引用路径与 T1 文件名完全一致。
  - `human-judgement` TR-2.2: 五行生克方向正确（相生：木火土金水循环；相胜：木克土、土克水、水克火、火克金、金克木）；十二经流注顺序与《灵枢·经脉》/正文一致；02 篇板块名称与正文一致。
  - `programmatic` TR-2.3: git diff 确认仅新增行，正文与 frontmatter 零改动。

## [x] Task 3: 概念篇 Mermaid 与配图插入（第二批：06/08/09/10/11）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 委托子代理，拥有文件：concepts/06-disease-causes.md、08-treatment-principles.md、09-yangsheng.md、10-five-movements-six-qi.md、11-commentary-guide.md。
  - **先读后画**：通读 5 篇正文 + facts.md 相关事实。
  - M3.1（06 篇）：病因分类 flowchart——总起"生病起于阳/起于阴"二分；阳侧：六淫（风寒暑湿燥火，风为百病之始）；阴侧：饮食居处、房室、七情五志（喜怒忧思悲恐惊）、金刃虫兽；伏邪作为跨季分支单列。标签以正文为准。
  - M3.2（08 篇）：病机十九条归类 + 治则 flowchart——上半：十九条按属五脏（肝/肾/肺/脾/心）、属火、属热、属风/湿/寒、属上/下归类（条数与归属严格按 08 篇正文）；下半：正治（寒者热之/热者寒之）与反治（热因热用/寒因寒用等，**异文双录"热因热用/热因寒用"按正文原样呈现，不擅改**）分流。
  - M3.3（09 篇，"三、女七男八"附近）：双列生命周期 flowchart——女子列：七歲→二七（天癸至）→三七→四七（盛极）→五七→六七→七七（天癸竭）；丈夫列：八歲→二八→三八→四八→五八→六八→七八→八八。**节点标签必须单行（严禁 `<br/>`）**：用短词附关键征象，如 "二七 天癸至"、"四七 筋骨坚盛极"、"七七 天癸竭"；征象文字精简且出自正文，可用 subgraph 分"女子""丈夫"两列。
  - M3.4（10 篇）：五运六气推导 flowchart——五运：甲己→土、乙庚→金、丙辛→水、丁壬→木、戊癸→火；六气：子午→少阴君火、丑未→太阴湿土、寅申→少阳相火、卯酉→阳明燥金、辰戌→太阳寒水、巳亥→厥阴风木。**所有配对以 10 篇正文为准核对**（若正文表述与上列不同，以正文为准并在报告中说明）。
  - M3.5（11 篇，"二、按学习阶段选用"与"三、查注流程"附近）：三级注本选用 flowchart（入门：内经知要类 → 进阶：类经/集注 → 考据：素问识/灵枢识等）+ 查注五步流程（按正文五步骤）。
  - 图片插入（扩展名 .jpg）：09 篇 `four-seasons.jpg`（"四、四季调神"附近）；10 篇 `yunqi-celestial.jpg`（篇首节之后）。
  - 每图/表前加引导句；完成后运行 check-mermaid.py 零 error。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-5, AC-7
- **Test Requirements**:
  - `programmatic` TR-3.1: 5 张 Mermaid 通过 check-mermaid.py 零 error；2 条图片引用正确。
  - `human-judgement` TR-3.2: 十九条归类计数与正文一致（不得错配脏腑/火/热条目）；女七男八年龄节点与征象无错位；天干化运/地支化气六对配属与正文逐对一致；异文双录未被擅改。
  - `programmatic` TR-3.3: git diff 仅新增行。

## [x] Task 4: 首页 hero、examples/09 甘特图、insights 知识地图与 log 记录
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3（避免同批文件交叉；本任务文件为 index.md、examples/09-reading-plan.md、insights.md、log.md，与 T2/T3 文件不重叠）
- **Description**: 委托子代理。
  - index.md：在"## ⚠️ 首要声明"段落之后、"## 📚 快速导航"之前插入 hero 图 `hero-qibo.jpg`（alt 描述岐黄问答场景），单独成段。
  - examples/09-reading-plan.md：通读十二周计划全文，将周程转为 mermaid **gantt**（12 周分阶段：准备/精读推进/概念回查/通收束，按正文实际周次安排）；若 gantt 中文标签在构建中渲染异常，降级为 flowchart 时间线（每周一节，标题含周次）。
  - insights.md：在"## 知识地图"位置，将现有文字/表格地图增补为 mermaid **mindmap**（中心：《黄帝内经》阅读教程；一级分支：文献层[版本链/注本导航]、理论层[阴阳五行/藏象/经络九针/病因/诊法/治则/养生/运气]、实践层[8 篇精读/12 周计划]、边界层[非医疗声明]）。mindmap 节点文本简短，遵循六规则（mindmap 节点中文文本按 mermaid mindmap 语法处理，必要时加引号）。**保留原有文字内容**，mindmap 为增补。
  - log.md：追加一节（如"## 配图与可视化增强（2026-09-02）"），记录：范围（6 张 Seedream 意境图 + 10 张 Mermaid）、分布清单、门禁与 V 审查结论位（待 T5 回填）。
  - 完成后运行 check-mermaid.py 零 error。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-5, AC-8
- **Test Requirements**:
  - `programmatic` TR-4.1: 2 张 Mermaid（gantt/降级 flowchart、mindmap）通过 check-mermaid.py；hero 引用路径正确。
  - `human-judgement` TR-4.2: gantt 周次划分与 examples/09 正文计划一致；mindmap 分支覆盖束结构且无层级错误；insights 原文未被删改。
  - `programmatic` TR-4.3: log.md 新节存在且含 6 图 10 表清单。

## [x] Task 5: V 对抗审查 + 全量门禁 + 修复闭环（独立子代理）
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4
- **Description**: 委托**独立**子代理（未参与制图）执行黑盒审查：
  1. **门禁**：运行 check-mermaid.py 覆盖全部变更文件；在 awesome-okf-xs 子项目运行 sphinx 构建（`sphinx-build -b html doc doc/_build/html`，以该子项目实际 conf.py 位置为准；如缺依赖先 `pip install -r docs/requirements.txt` 或报告环境阻塞），收集 WARNING/ERROR。
  2. **图片核验**：6 个 PNG 存在且引用一一对应；逐张目检（打开图片）无文字/印章/现代元素、风格统一、主题匹配；图 3 确认无太极符号、图 4 为静物意境。
  3. **事实核验**：逐张 Mermaid 对照 facts.md 与所在篇正文，重点：五行生克方向、十二经流注顺序、十九条归类计数、女七男八节点、天干地支化运配属、版本链人物朝代（王冰/林亿/史崧/顾从德）、三级注本人名书名。发现错误直接修复（仅限 Mermaid/引导句范围内）并复验。
  4. **适度性与侵入面**：确认单篇 ≤1 图 1 表、examples/01~08 无 AI 图、frontmatter/正文零删改（git diff --stat 与抽查）、未触碰束外文件、无 git 提交发生。
  5. 回填 log.md 的 V 审查结论；输出审查报告（发现项/修复项/残余风险）。
- **Acceptance Criteria Addressed**: AC-1~AC-8 全部
- **Test Requirements**:
  - `programmatic` TR-5.1: check-mermaid.py 零 error；sphinx-build 对 huangdi-neijing 页面零 WARNING/ERROR（图片与 Mermaid 相关）。
  - `human-judgement` TR-5.2: 事实核验清单逐项 PASS，关键关系零错误；图片目检 6/6 合格。
  - `programmatic` TR-5.3: git 状态确认无 commit；变更文件清单全部位于 huangdi-neijing 束内 + _static 对应目录。
- **Notes**: 若 sphinx 环境不可用，至少完成 check-mermaid + 引用路径存在性程序核验，并将 sphinx 构建列为残余风险报告。
