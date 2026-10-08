# 杭州求姻缘地点调研知识包 OKF wiki - 验收检查清单

## R 阶段（G1）

- [x] facts.md 存在且事实 ≥60 条，编号 F-001 起连续，七轨覆盖（民俗源流/法喜寺/灵隐景区/其他寺院/黄龙洞/万松书院/实用信息）
- [x] 每条事实含至少 1 个 http(s) URL、信源层级标注；时效性事实标注采集日期
- [x] 抽查 10 条 URL 可访问；无因果推断词；无"灵验/最灵"主观断言作事实陈述
- [x] P0 双源核验表 ≥15 行，门票/开放时间/地址三类关键实用事实全覆盖

## 配图

- [x] `minsu-group-hero.jpg` 与 `hangzhou-qiuyinyuan-guide-cover.jpg` 落位 `doc/_static/bundles/sheke/minsu/images/`
- [x] 图片无文字乱码、无真实人物肖像、风格含蓄不庸俗、不渲染迷信

## I 阶段（G2）

- [x] insights.md 存在，≥5 条四元组洞察（现象/根因/影响/建议），每条回指 ≥1 个 F 编号
- [x] 洞察非常识复述，对行程决策或内容维护有直接指导意义

## A 阶段（G3）

- [x] concepts/ 8 篇 + index 共 9 文件存在，frontmatter 合规（可解析、含 type），每篇含"学完能做什么"并回指 F 编号
- [x] examples/ 3 篇 + index 共 4 文件存在；一日路线含时间轴/交通衔接/费用小计；避坑指南含官方复核入口
- [x] references/ 3 篇 + index 共 4 文件存在；每条信源含 URL 与层级标注；无营销号/付费占卜导流站点
- [x] 束根 index.md（type: OKF、okf_version 0.2、快速导航、读者路径 mermaid、toctree 全覆盖）与分组 index.md（type: group、hero 图引用、知识地图）齐备
- [x] okf_version 仅出现在束根；文件名 kebab-case 英文；正文中文；相对路径引用、零 file:///；UTF-8 无 BOM

## 内容红线

- [x] 无灵验度承诺/排名背书；无算命占卜/婚介付费服务引导
- [x] 万松书院相亲角内容无可识别个人信息；全束无个人隐私数据
- [x] 宗教场所表述尊重客观（民俗文化与旅游视角）

## V 阶段（G4）

- [x] 四视角审查记录存在（魔鬼代言人/新人/老板/未来），意见 ≥5 条且每条有文件/段落定位
- [x] ≥2 条采纳修正已落盘并复验；修正未引入断链

## C 阶段（交付）

- [x] `sheke/index.md` 分组表新增 minsu 行、toctree 含 `minsu/index`，计数以门控重算为准
- [x] `bundles/index.md` 五面对账一致（frontmatter 计数 == 计数行 == 域节标题 == 分组表 == toctree）
- [x] `invoke gates.utf8` / `invoke gates.toctrees` / `invoke gates.bundles` 三门全绿
- [x] 定向 `sphinx -b dummy` 构建退出码 0，无与新增文件相关 warning/error
- [x] 未执行 git commit/push（交付物为工作树文件 + 门控全绿）

---

## 验收记录（2026-10-01）

| 检查区 | 关键证据 |
|---|---|
| R 阶段 | facts.md 78 条事实（F-001~F-078 连续）、七轨分布 8/12/17/13/9/7/12；P0 表 22 行；10 条 URL 抽查全通 |
| 配图 | hero 2752×1536 (16:9) + cover 2400×1792 (4:3)，Read 目检无文字/无人物，MD5 非占位图 |
| I 阶段 | insights.md 7 条洞察、四要素齐全、53 个去重 F 回指机检无悬空 |
| A 阶段 | concepts 9 文件 77 个 F 回指全量机检无悬空、P0 口径抽查 10 项全对；examples 49 个 F 回指无悬空、费用小计与 P0 表逐项一致、时间轴闭环；references 55 条信源、8 条 URL 抽查全通；束根/分组 index toctree 目标全存在、okf_version 仅束根 |
| 内容红线 | V 审查专项确认：灵验表述均归因信源客观记录、相亲角无可识别个人信息、无营销号混入一级信源 |
| V 阶段 | review.md：10 条意见（4×P1/5×P2/1×P3）均有定位，8 条采纳落盘，toctrees 复跑退出码 0 |
| C 阶段 | 三门门控两轮全绿（UTF-8 10717 文件 / toctree 全可达 / bundles 五面对账 577 束·60 组·9 域，sheke 48 束·8 组）；sphinx dummy 退出码 0、与新增文件相关 warning 为 0；git 零写操作 |

遗留开放问题（见束内 review.md 第五节）：OQ-1 stale_after 一刀切与除夕内容保鲜期矛盾（P2）；OQ-2 票价多点重复缺机器校验（P3）；OQ-3 F-020「九寺一观」名单实为 8 寺 1 观待下轮事实维护补注（P3）。
