# 《黄帝内经》束配图与 Mermaid 增强 - Verification Checklist

> 状态说明：T5 独立 V 对抗审查已完成（2026-09-02），全部核验项通过；nine-needles 工笔风格替换已闭环（重生成就位，文件头字节与目检双验）。

## 配图（Seedream AI 图）
- [x] 6 个 JPG 文件存在于 `doc/_static/bundles/yixue/huangdi-neijing/images/`（hero-qibo、editions-slips、yinyang-landscape、nine-needles、four-seasons、yunqi-celestial，均为 .jpg，522KB~1.2MB，已核验非空）
- [x] 6 条 `/_static/bundles/yixue/huangdi-neijing/images/...` 引用与文件一一对应，分布于 index.md、concepts/01、03、05、09、10（V 审查逐一解析命中）
- [x] 逐张目检：无文字/字母/印章/可辨识字符，无现代元素（V 子代理逐张 Read 打开核验）
- [x] 六张风格统一（宋代院体工笔/水墨浅绛、绢本暖调）——nine-needles 写实初版已由工笔重生成版替换就位（漆匣靛垫九针+葫芦竹简卷），JPEG 文件头 FF D8 FF E0 有效、729KB、目检与其余 5 张统一
- [x] 图 3（阴阳）为意境山水、不含太极鱼符号；图 4（九针）为古器静物意境、非技术图谱
- [x] alt 文本准确描述画面，05 篇九针图含"意境图"定位；V 修复 1 项：01 篇 alt「青铜油灯」→「青铜灯台」
- [x] hero 图位于 index.md 首要声明之后、快速导航之前

## Mermaid 图表（实际 11 张：08 篇 2 张）
- [x] 齐全：concepts/02 结构路径、03 五行环、05 十二经流注、06 病因树、08 十九条归类+正治反治（2 张）、09 女七男八、10 五运六气、11 注本导航、examples/09 gantt、insights mindmap
- [x] 围栏全小写 ```mermaid；13 个变更文件 `_process_file` 原位校验 errors=0、warnings=0
- [x] 安全规则：块内无空行；中文文本双引号（flowchart）；节点 ID 全英文；subgraph 英文 ID；边标签 `-->|"..."|`；标签单行、无 `<br/>`；无带圈数字、无【】；mindmap 节点无引号无冒号
- [x] 五行环：相生 木→火→土→金→水→木；相胜 木→土→水→火→金→木，方向正确
- [x] 十二经流注：肺→大肠→胃→脾→心→小肠→膀胱→肾→心包→三焦→胆→肝→环回，经名与正文一致
- [x] 病机十九条归类计数与 08 篇正文一致（火5/热4/五脏5/上下2/风寒湿3=19，无属燥；燥条为刘完素补）；"热因热用/热因寒用"异文双录原样保留
- [x] 女七男八年龄节点（七/二七…七七；八/二八…八八）与正文征象对应无错位
- [x] 天干化运（甲己土、乙庚金、丙辛水、丁壬木、戊癸火）与地支化气六对配属逐对与 10 篇正文一致
- [x] 每张 Mermaid 前有引导句，内容可溯源至 facts.md/正文，无编造（V 逐项对照 F-001~F-137 零事实错误）
- [x] gantt 一次通过未降级；周次主题逐行出 examples/09 正文表格

## 构建与门禁
- [x] Sphinx 全树解析构建（py314，`python -m sphinx -b dummy -E doc`，7516 文档）build succeeded；本包 28 文档 0 warning，13 变更文件逐一 READ_OK；仅 2 条 warning 位于 yishu/vocal 他方束（与本次无关）
- [x] 无断链：6 条图片引用逐一解析命中；文档内既有链接未受影响
- [x] 配置确认：子项目 conf.py 已配 `myst_fence_as_directive=['mermaid']` + sphinxcontrib.mermaid（mermaid 11.4.1 CDN 渲染），```mermaid 围栏为正确范式

## 侵入面与规范
- [x] 单篇文档至多 1 图 +（08 篇批准例外 2 表）；examples/01~08 八篇精读无 AI 图
- [x] git diff 仅新增行：正文文字、引文、表格、frontmatter、toctree 零删改（V 抽查 03/08/insights 等）
- [x] 变更全部位于 huangdi-neijing 束内及 _static 对应目录，束外文件零改动
- [x] 未执行任何 git add / git commit（V 核验 git log 无本次提交；6 张图片仍为 untracked，提交时需显式 add）
- [x] log.md 已追加配图增强记录（含 6 图 11 表清单、V 审查结论、Sphinx 构建结论回填）
- [x] V 审查由未参与制图的独立子代理完成，审查报告已产出

## 未决项
- 无。nine-needles.jpg 风格替换已闭环：工笔重生成版直接落盘 nine-needles.jpg（初次替换发现文本模式搬运工具损坏二进制——高位字节被 UTF-8 替换符 EF BF BD 取代，已删除损坏件后以同 prompt 重新生成；终态 JPEG 文件头 FF D8 FF E0 有效、目检通过），目录仅存 6 图，文档引用无需改动。
