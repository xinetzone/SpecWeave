# 道医束配图与 Mermaid 增强 - 验证清单

> 由独立 V 阶段子代理逐项黑盒验证；全部勾选后方可进入提交。

## Mermaid 图表（9 张）
- [x] C1：concepts/00 含三圆模型 × 道-理-术三层对应图，三圆内容（中心=汤液本草针灸／中间=导引调息内丹辟谷内视房中／外周=符占签咒斋禁祭祀）与正文表格一致
- [x] C2：concepts/01 含历史时间线，盖建民三期、六期表述、祝由科节点（唐咒禁科→元明祝由科→1571裁撤）与正文一致
- [x] C3：concepts/03 含葛洪/陶弘景/孙思邈著述关系图，生卒 283-363/456-536/581-682 与著作归属正确（肘后/抱朴子；本草经集注/名医别录/养性延命录；千金要方/翼方、道藏93卷本注记）
- [x] C4：concepts/04 含道藏体系图，涵芬楼1120册/三家本36册/中华道藏49册、云笈七签卷次（32-36/56-62/63-73/74起）、道枢42卷、修真十书60卷与正文一致
- [x] C5：concepts/05 含丹经脉络时间线，参同契（东汉）/黄庭经/悟真篇（1075）/性命圭旨（1615）/伍柳仙宗（1794/1896）/静功疗养法（1957）节点正确，外丹→内丹更替标注存在
- [x] C6：concepts/06 含汉志四家↔出土↔传世对应图，马王堆前168/张家山前186/天回920余简/敦煌南北朝-五代与四家（医经/经方/房中/神仙）连线正确
- [x] C7：concepts/07 含会通五家时间线，年份按序（扁鹊心书1146/医贯1617/景岳全书1624/四圣心源1753/郑钦安1869·1874·1894），人物与著作归属正确
- [x] C8：concepts/08 含辨伪决策流程图，三类文本→断代三法→两说并陈链路完整；平台四级（识典/维基/ctext/diancang）与 zysj 禁用节点与正文一致
- [x] C9：examples/02 含三档阅读路径图（零基础8周/中医基础6周/研究型）与"识典→点校本→道藏/出土"阶梯
- [x] C10：全部 Mermaid 节点标签加双引号、无半角括号/半角冒号等违规字符；语法经校验流程通过
- [x] C11：每图有自然引导语，插入未破坏既有表格、引用块、非医疗声明与交叉链接

## 配图（8 张）
- [x] C12：images 目录存在 8 个图片文件（hero-daoyi、history-yidao、classics-roots、daoist-physicians、daozang-canon、neidan-cultivation、excavated-texts、yidao-schools）
- [x] C13：8 处 Markdown 引用路径与实际文件名（含扩展名）完全一致；引用前缀为 /_static/bundles/yixue/daoyi/daoyi-reading/images/
- [x] C14：8 张图均为水墨淡彩中国风、横向构图、风格统一；无现代元素、无水印、无可辨读文字
- [x] C15：无人物真容/穴位解剖/功法动作/符箓图像（人物仅远景/背影/剪影）
- [x] C16：每图下方有含"AI 生成"与"非历史图像"语义的斜体图注；alt 文本为画面描述且无事实断言
- [x] C17：图位正确——首页图在开篇段后/快速导航前；概念页图在 H1 后首个小节前

## 范围与门禁
- [x] C18：变更集仅含 8 个新图片 + concepts 9 文件 + examples/02 + daoyi-reading/index.md + log.md；无新增 .md、无 toctree 改动、doc/bundles/index.md 未被触碰
- [x] C19：frontmatter 未被破坏（无 Malformed YAML 风险写法）；facts.md 编号与正文事实数据零改动
- [x] C20：log.md 追加 2026-09-02 视觉增强条目，格式与既有条目一致
- [x] C21：质量门（utf8/toctrees/bundles 三脚本含自检探针）全绿（invoke 环境缺失，已等价直跑 scripts/ 下三脚本）
- [x] C22：sphinx-build（dummy builder）退出码 0，daoyi 束零 WARNING/ERROR、无 image not readable（唯一 ERROR/WARNING 在并行会话 meitong 束，与本任务无关）
- [x] C23：非医疗声明在全部既有页面原样保留

## 提交
- [x] C24：提交前 `.git/MERGE_HEAD` 不存在；add 与 commit 分步执行
- [x] C25：`git diff --cached --name-only` 暂存集全部为本任务文件，无他方文件混入
- [x] C26：提交信息为 Conventional Commits 中文主体；未执行 push（提交 13c07f9f，main ahead 1）
