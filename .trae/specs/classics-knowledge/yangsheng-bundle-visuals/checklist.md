# 养生经典阅读束配图与 Mermaid 图表增强 - Verification Checklist

- [x] CP-1: `doc/_static/bundles/yixue/yangsheng/yangsheng-classics-reading/images/` 下存在 8 个图片文件，stem 分别为 hero-reading-classics、yangsheng-daily-life、neijing-huangdi-qibo、jikang-bamboo-grove、sun-simiao-herbs、zunsheng-scholar-studio、elder-congee-care、shanggu-harmony-nature（均为 .jpg，2240×1680）
- [x] CP-2: 8 张图片目检——主题与 spec FR-2 一一吻合；画面无任何文字/水印/署名（印章形印记与书页纹理不可辨识，已放大复核）；无现代物品穿越；均为 4:3 横版
- [x] CP-3: 8 张图片并排审阅——画风统一（国风工笔淡彩/水墨淡彩）、色调统一（宣纸暖色调）、呈同一系列感
- [x] CP-4: index.md、concepts/00、01、02、03、04、05、examples/01 共 8 个文档各含 1 处图片引用，路径为 `/_static/bundles/yixue/yangsheng/yangsheng-classics-reading/images/<stem>.jpg`，且与磁盘实际文件名完全一致
- [x] CP-5: 图片引用均位于各文档首个正文段落之后，alt 为中文完整描述句，无"AI生成"类元信息
- [x] CP-6: index.md（M2 三路径）、concepts/06（M1 五脉谱系）、concepts/01（M3 版本层累）、concepts/02（M4 论辩往复）、concepts/07（M5 四步选书）、examples/02（M6 四周计划）共 6 个文档各含 1 个 ```mermaid 代码块
- [x] CP-7: 全部 mermaid 节点标签双引号包裹；换行仅使用 `<br/>`；无未加引号的括号/冒号节点；未使用 gantt 等易失败语法
- [x] CP-8: M1 五脉谱系含医家/道家/文人/食养/导引五支全部代表著作与年代，且含两处交汇关系（《千金》引嵇康五难、《养性延命录》横跨道/导引）
- [x] CP-9: M2 替换原纯文本路径代码块后，零基础/版本关注/谱系兴趣三条路径信息无损
- [x] CP-10: 6 张 mermaid 全部节点文字与 facts.md/正文对账一致（人名、朝代、成书年代、书名、卷次无事实错误）
- [x] CP-11: 变更范围仅限本束——8 个图片新文件 + 11 个 .md 文档编辑（index、concepts/00-07、examples/01、02）；frontmatter 未改动；共享索引 doc/bundles/index.md 未触碰；无文件删除
- [x] CP-12: 在 projects/awesome-okf-xs 执行 `invoke gates.all`（Windows conda py314），toctrees/bundles/utf8 三门全绿，退出码 0
- [x] CP-13: 构建验证——最小等价工程构建（真实 conf.py + 本束 19 文档 + 8 图）退出码 0、warnings.log 0 字节；8 图全部成功复制无 image not readable；6 个 `<pre class="mermaid">` 节点正确产出；无 Unknown directive。注：沙箱内 `invoke build` 默认产物目录被 TRAE 沙箱拦截（环境问题非交付物问题），RTD CI 不受影响
- [x] CP-14: 未执行任何 git add/commit/push 操作（工作树交付，待用户决定提交）
