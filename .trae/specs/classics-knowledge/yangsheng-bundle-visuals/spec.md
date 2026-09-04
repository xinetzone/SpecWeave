# 养生经典阅读束配图与 Mermaid 图表增强 - Product Requirement Document

## Overview

- **Summary**：为 OKF 知识包 `doc/bundles/yixue/yangsheng/yangsheng-classics-reading/`（养生经典阅读教程，8 概念 + 2 示例 + 3 信源 + facts/insights，共 19 个文档）补齐视觉资产：使用 Seedream 生成 8 张中国风配图嵌入对应文档，并撰写 6 张 mermaid 图表承载谱系、流程、版本流传等结构化信息。

- **Purpose**：该束为纯文本知识包，无一张图片/图表。养生经典阅读的核心障碍是"只见树木不见森林"（insights 洞察一）与"人物/时代缺乏具象感"；配图建立时代与人物的感性入口，mermaid 把五脉谱系、阅读路径、版本层累、论辩往复、选书流程、阅读计划等结构性知识可视化，降低初读门槛。

- **Target Users**：零基础养生经典读者（普通中文读者）、OKF 文档站（Sphinx/Read the Docs）访问者。

## Goals

- 为束首页与 7 篇核心文档各配 1 张风格统一的中国风插图（共 8 张），图片与该文档主题严格对应。

- 为 6 处结构化知识节点配置 mermaid 图：五脉谱系总图、三条阅读路径、《素问》版本层累流传、嵇康论辩往复、四步选书法、四周阅读计划。

- 全部视觉资产通过子模块质量门（`invoke gates.all`）与 Sphinx 构建（`invoke build` 零新增警告）。

- 图片与 mermaid 内容不得与 facts.md 登记事实冲突（V 对抗审查）。

## Non-Goals (Out of Scope)

- 不新增/删除/重排任何 Markdown 文档，不改动 toctree 结构与 frontmatter（正文内容仅做"插入图片引用/图表块"的增量编辑）。

- 不修改 `doc/bundles/index.md` 总索引与计数（束数量不变，gates.bundles 仅回归验证）。

- 不撰写新的事实/洞察内容，不做正文文字扩写（图片 alt 文本与 mermaid 节点文字除外）。

- 不处理 references/ 3 篇信源文档与 facts.md、insights.md（纯登记/分析类文档不配图）。

- 不执行 git commit / push（用户未要求；子模块共享索引竞态风险下仅交付工作树变更）。

## Background & Context

- **子模块规范**：目标在 `projects/awesome-awesome-okf-xs`（第一方 git submodule），遵循其 AGENTS.md：正文中文、文件名 kebab-case、相对路径引用、改动后跑 `invoke gates.all` + 构建验证。

- **图片先例**：`doc/_static/bundles/yishu/vocal/meitong-yanyin-pedagogy/images/` 已有 3 张配图，正文以 `![alt](/_static/bundles/<域>/<组>/<束>/images/<file>.<ext>)` 根绝对路径引用。本束照此约定，图片存放于 `doc/_static/bundles/yixue/yangsheng/yangsheng-classics-reading/images/`。

- **Mermaid 先例**：`doc/conf.py` 已配置 `myst_fence_as_directive = ["mermaid"]` + sphinxcontrib-mermaid（CDN 渲染，v11.4.1），束内多处在用（如 four-books、east-west-dialogue）。历史教训（yangming 束 log）：节点标签必须全部加引号，特殊字符仅用 `<br/>`，禁止未加引号的括号节点。

- **内容底册**：facts.md 登记 F-001\~F-145 客观事实（成书、版本、人物年代），所有视觉内容以此为事实边界。

- **方法论**：seven-concepts-cmd 轻量链路 R（事实已采集）→ F（配图第一性原理）→ V（对抗审查）→ C（原子交付）。第一性原理推导：插图承载"氛围/人物/场景"（感性认知），mermaid 承载"关系/流程/谱系"（理性结构），二者不互替；人物场景图对应 01-05 经典专论（每篇一位主角/一部书），结构图对应 06/07/index/examples。

## Functional Requirements

- **FR-1**：使用 Seedream（GenerateImage 工具）生成 8 张配图，统一风格为中国传统国风工笔淡彩/水墨淡彩、宣纸暖色调、无任何文字（规避 AI 文字错乱）、人物古装、场景宁静典雅；统一 4:3 横版。

- **FR-2**：8 张图片主题与落点：

  1. `hero-reading-classics` → 束 `index.md` 顶部：古代书斋，案头竹简与线装医书、药葫芦、青瓷茶盏、窗外竹影暖光。
  2. `yangsheng-daily-life` → `concepts/00-why-yangsheng.md`：古代民间日常养生场景（晨起导引、食饮有节、起居有常的庭院生活意象）。
  3. `neijing-huangdi-qibo` → `concepts/01-huangdi-neijing.md`：黄帝与岐伯明堂问对，远山云气阴阳意象（问答体源头）。
  4. `jikang-bamboo-grove` → `concepts/02-ji-kang-yangsheng-lun.md`：魏晋名士竹林中席地抚琴（嵇康/竹林七贤意境）。
  5. `sun-simiao-herbs` → `concepts/03-beiji-qianjin-yao-fang-yangxing.md`：唐代白发老医者背药篓采药、腰悬药葫芦（孙思邈/药王意象）。
  6. `zunsheng-scholar-studio` → `concepts/04-zunsheng-ba-jian.md`：明代文人书斋，香炉、茶具、插花、古玩、展卷（燕闲清赏/遵生八笺意境）。
  7. `elder-congee-care` → `concepts/05-laolao-hengyan-and-shouqin.md`：庭院中白发老人安坐、晚辈奉粥（自养+孝亲双主题，粥谱意象）。
  8. `shanggu-harmony-nature` → `examples/01-suwen-shanggu-tianzhen.md`：上古田园四时生活（春耕/晨练/山水，天人合一、法于阴阳意象）。

- **FR-3**：每张图片在对应文档中以 Markdown 图片语法引用（`/_static/` 根绝对路径），alt 文本为中文完整句、描述画面内容；位置为该文档首个正文段落之后（frontmatter 与 H1/H2 标题之后）。

- **FR-4**：撰写 6 张 mermaid 图并嵌入：

  1. **M1 五脉谱系总图**（`concepts/06-schools-lineage.md`"总览"表格之后）：flowchart，医家/道家/文人/食养/导引五脉各为一支，节点为代表著作+年代（`<br/>` 换行），含两处交汇虚线（《千金》引嵇康五难、《养性延命录》横跨道家/导引）。
  2. **M2 三条阅读路径**（`index.md`"推荐学习路径"节，替换现有纯文本代码块，信息无损）：flowchart，零基础/版本关注/谱系兴趣三分支。
  3. **M3 《素问》版本层累流传**（`concepts/01`"版本常识"节之后）：flowchart LR，战国秦汉成书→王冰762补七篇编24卷→林亿1057校正→顾从德1550翻宋本→现代影印/校注；旁支灵枢：史崧南宋定本→赵府居敬堂本；遗篇以注释节点标注。
  4. **M4 养生论辩往复**（`concepts/02`"养生五难与论辩传统"节）：flowchart，嵇康《养生论》→向秀《难养生论》→嵇康《答难养生论》；虚线节点"养生五难"→《千金要方》卷27引录。
  5. **M5 四步选书法**（`concepts/07`"四步"导语之后）：flowchart LR，辨托名与成书年代→选善本底本整理本→查底本说明→对照影印本。
  6. **M6 四周阅读计划**（`examples/02-reading-plan.md`"总体路线"表格之后）：flowchart LR，第1-4周节点各含主题与目标文本（`<br/>` 换行）。

- **FR-5**：所有 mermaid 节点标签一律双引号包裹；标签内特殊字符仅用 `<br/>`；不使用未加引号的括号/冒号/书名号外特殊符号；gantt 等易失败语法不用。

## Non-Functional Requirements

- **NFR-1（构建零回归）**：`invoke build`（sphinx-build）不得出现任何新增 warning/error；图片路径全部可解析（无 image not readable）；mermaid 栅栏全部被识别为 directive。

- **NFR-2（门控全绿）**：`invoke gates.toctrees`、`invoke gates.bundles`、`invoke gates.utf8` 全部通过。

- **NFR-3（事实一致性）**：图片画面与 mermaid 节点不得出现与 facts.md 冲突的信息（如人物朝代、著作年代、书名）；图片不出现可辨识文字以免错乱或杜撰。

- **NFR-4（风格一致）**：8 张图片画风、色调、构图语言统一（同一系列感），暖纸基调契合 OKF 文档站阅读气质。

- **NFR-5（适度原则）**：mermaid 总量控制在 6 张，仅用于结构/谱系/流程；references/facts/insights 不插图不绘图。

## Constraints

- **Technical**：Windows 主机；构建优先 WSL（用户偏好），依赖缺失时回退 Windows py314 conda 环境；构建环境需装 sphinxcontrib-mermaid（否则 \`\`\`mermaid 栅栏无法识别）。图片由 Seedream GenerateImage 生成（主会话工具，子代理不可用），落盘于子模块 `doc/_static/...`。

- **Business**：不提交 git（用户未授权）；子模块为共享工作区，存在并行会话可能，仅触碰本束目录与本束图片目录，不碰共享索引。

- **Dependencies**：Seedream 图像生成服务、Sphinx + myst-parser + sphinxcontrib-mermaid、子模块 invoke 任务（tasks/gates.py、tasks/docs.py）。

## Assumptions

- 图片风格默认采用"国风工笔淡彩 + 宣纸暖色调 + 无文字"方案（与用户暖灰纸感视觉偏好一致）；如需写实摄影风或其他风格，在审批门提出。

- 图片数量 8 张、mermaid 6 张为"适度"基线；审批时可增减。

- GenerateImage 落盘扩展名由工具决定（.png/.jpg），正文引用以实际扩展名为准（先例中 .png/.jpg 均有）。

- mermaid 在 HTML 为运行时 CDN 渲染，构建期不校验 JS 渲染结果，故语法安全性靠"全引号标签 + 仅 `<br/>`"规则与人工审查保证。

## Acceptance Criteria

### AC-1: 8 张配图全部生成落盘

- **Given**：图片目录 `doc/_static/bundles/yixue/yangsheng/yangsheng-classics-reading/images/`

- **When**：图像生成任务完成

- **Then**：目录下存在 8 个图片文件，文件名与 FR-2 清单一一对应（hero-reading-classics、yangsheng-daily-life、neijing-huangdi-qibo、jikang-bamboo-grove、sun-simiao-herbs、zunsheng-scholar-studio、elder-congee-care、shanggu-harmony-nature），均可正常打开

- **Verification**: `programmatic`

### AC-2: 图片引用全部有效且位置正确

- **Given**：8 篇目标文档

- **When**：检查正文

- **Then**：每篇恰有 1 处 `![...](/_static/bundles/yixue/yangsheng/yangsheng-classics-reading/images/...)` 引用，路径与实际文件（含扩展名）完全一致，alt 为中文描述句，位于首个正文段之后

- **Verification**: `programmatic`

### AC-3: 6 张 mermaid 图嵌入且语法安全

- **Given**：index.md、concepts/01、02、06、07、examples/02 共 6 个文档

- **When**：检查正文

- **Then**：每篇恰含 1 个 \`\`\`mermaid 代码块，内容符合 FR-4 的 M1-M6 结构；所有节点标签双引号包裹、换行仅用 `<br/>`、无未加引号的括号节点

- **Verification**: `programmatic`

### AC-4: Sphinx 构建零新增警告

- **Given**：子模块构建环境（含 sphinxcontrib-mermaid）

- **When**：在 `projects/awesome-okf-xs` 执行 `invoke build`

- **Then**：构建成功，无 image not readable、无 unknown directive、无新增 warning/error

- **Verification**: `programmatic`

### AC-5: 子模块质量门全绿

- **When**：执行 `invoke gates.all`（toctrees + bundles + utf8）

- **Then**：三道门全部通过

- **Verification**: `programmatic`

### AC-6: 视觉内容事实一致（V 对抗审查）

- **Given**：facts.md 事实底册与 8 图 6 图

- **When**：对抗审查员逐图/逐节点核对

- **Then**：人物、朝代、著作、年代、谱系关系无事实错误；图片不含可辨识文字；mermaid 节点信息可在 facts.md 或正文找到依据

- **Verification**: `human-judgment`

### AC-7: 风格统一性

- **Given**：8 张配图

- **When**：并排审阅

- **Then**：画风、色调（暖纸基调）、人物造型语言一致，呈同一系列感；无现代物品穿越、无文字水印

- **Verification**: `human-judgment`

## Open Questions

- [ ] 图片风格是否认可"国风工笔淡彩/宣纸暖色调/无文字"默认方案？（备选：水墨写意、绢本重彩）

- [ ] 8 图 6 图的数量基线是否认可？

