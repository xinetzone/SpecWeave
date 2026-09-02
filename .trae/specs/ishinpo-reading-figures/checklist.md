# 《医心方》研读束配图与 Mermaid 视觉增强 — 验证清单

- [x] C1: `doc/_static/bundles/yixue/medicine/ishinpo-reading/images/` 下存在 9 个图片文件，文件名与 visual-design.md 清单一致（Get-ChildItem 实测 9 个 PNG，逐名核对通过）
- [x] C2: index.md、concepts/00-05（6 篇）、examples/01-02（2 篇）共 9 个文档各含 1 行图片引用，路径为 `/_static/bundles/yixue/medicine/ishinpo-reading/images/<file>` 且与实际文件同名（grep 实测 14 行匹配中 9 行为 `![` 引用，分布于 9 文档）
- [x] C3: references/ 3 篇、facts.md、insights.md、log.md 无 AI 配图引用（grep `!\[` 仅命中 9 个目标文档；log.md 仅文字登记文件名）
- [x] C4: 9 张图人工目检通过：暖纸底水墨淡彩风格统一、图内无文字/水印/印章、无露骨内容、无现代穿帮、与文档主题及 alt 语义相关（3 张首轮问题图经强化 blank/no-text 约束重生成，edo 图第 3 次重构场景消除墙上伪书法挂轴后定稿）
- [x] C5: concepts/01、02、03、04 与 examples/02 共 5 个文档各含 1 个新 ```mermaid 围栏块（小写围栏），块前有引导语
- [x] C6: Mermaid 安全六规则合规：块内无空行、中文文本双引号、节点 ID 全英文、换行用 `<br/>`、subgraph 为 `EN_ID ["中文"]` 格式、边标签为 `-->|"标签"|` 无空格（T2 子代理逐字比对 ALL_OK）
- [x] C7: ~~`python check_mermaid.py`~~ 该脚本为 wsl-wiki 硬编码旧脚本（BASE_DIR 指向已迁移的 .agents/docs 路径），启动即 FileNotFoundError，不可用；等效验证三重通过：①R 阶段 mermaid 11.4.1 真实解析器 41 节点全通过；②Sphinx 最小化构建 5 页面零 mermaid 告警且 mermaid 容器齐全；③边标签语法错误（`-->| "x" |`）已在 T2 修正
- [x] C8: Mermaid 事实核验表逐条通过——所有年代/人名/书名/版本名/统计数字可回溯 facts.md F-编号或所在文档正文，无臆造事实；分歧数据（撰成 982/984、引书 204/280、写本 52/53）图中未裁断；修复图文不一致 1 处（"六个功能板块"→"五个"）
- [x] C9: 图型恰当：三十卷=TD 分组 flowchart（5 subgraph）、辑佚=LR 链路 flowchart、版本=TD 谱系树（3 subgraph）、研究史=LR 时间线、阅读计划=LR 阶段路线（Sphinx HTML 抽查 5/5 图首行一致）
- [x] C10: 构建验证通过（等价证据链，沙箱内 `invoke` 缺 invocations 包、子模块 _build 写入被拦截）：最小化 Sphinx 8.2.3 构建 10 源文件 exit 0；9 图全部 copying images 成功、HTML `<img>` alt/src 正确（子页 `../_images/`）；零 image not readable / mermaid / YAML 告警；40 条剩余 warning 均为故意省略的兄弟页交叉引用（全量树中存在）
- [x] C11: 三门质量门全绿——check-utf8.py / check-toctrees.py / check-bundles-index.py 直接运行均 exit 0（含各自自检探针），等价 `invoke gates.all`
- [x] C12: 最小侵入——`git diff --stat` 本束 10 个文件全部纯新增（index +4、00 +4、01 +41、02 +23、03 +40、04 +23、05 +4、examples/01 +4、examples/02 +17、log +7，0 删除）；facts.md/insights.md/references 正文零变更；无文档新增/删除/重命名（工作区其余改动属并行会话他方束，与本任务无关）
- [x] C13: log.md 含 `## 2026-09-02 视觉增强（事实内容零变更）` 条目，列出 9 图 5 图清单、存放/引用路径、统一图注与验证结论
- [x] C14: 未执行任何 git add/commit/push（git index.lock 沙箱拦截亦为佐证）；交付报告含完整变更文件清单与验证证据
