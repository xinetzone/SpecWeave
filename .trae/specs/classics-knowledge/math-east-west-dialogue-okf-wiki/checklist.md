# 中西数学对读 OKF Wiki 教程 — 验收清单

> 逐项核验，通过后勾选。对应 spec.md 的 AC-1~AC-10 与 tasks.md 的 TR 要求。
> 验证时间 2026-09-01；对抗审查报告见 [review.md](review.md)（含 ⑨ 修复复验记录）。

## 结构与位置（AC-1）

- [x] `projects/awesome-okf-xs/doc/bundles/kexue/math/east-west-dialogue/` 目录存在
- [x] bundle 根 `index.md` 存在且含 `okf_version: "0.2"`
- [x] `log.md`、`facts.md`、`insights.md` 存在
- [x] `concepts/`、`examples/`、`references/` 三个子目录各含 `index.md`
- [x] concepts 文档 ≥9 篇（3 方法论 + 6 对读主题）——实际 9 篇
- [x] examples 文档 ≥3 篇——实际 3 篇
- [x] references 文档 ≥3 篇——实际 3 篇

## Frontmatter 合规（AC-2）

- [x] 每个非保留 `.md` 含可解析 YAML frontmatter 且 `type` 非空（yaml.safe_load 扫描 22/22 通过；facts/log 为保留工作文件，与既有束先例一致免 frontmatter）
- [x] bundle 根 `index.md` 含 `okf_version: "0.2"`
- [x] 概念/示例/信源文档含 `title`/`description`/`tags`/`sources`/`generated`/`status`/`stale_after` 字段
- [x] `index.md`/`log.md` 遵循保留文件结构（log 按 `YYYY-MM-DD` 日期分组倒序）
- [x] frontmatter 中文语境引号使用全角""，无 ASCII 双引号嵌套陷阱（审查 R-6 附属项修复：insights 两处 title 改单引号标量）

## 导航与索引（AC-3）

- [x] `kexue/math/index.md` 含 east-west-dialogue 知识包行、束数 1→2、toctree 条目
- [x] `bundles/index.md` math 分组行束数 1→2、描述更新、kexue 域 15 束、mermaid 标签同步（total_bundles 并入本束与并行会话 physics 扩束；yishu/liaoyu 为并行会话在途交付未代注册，残余 6 处计数漂移全部归属该 WIP）
- [x] toctree 检查（check-toctrees.py）：我方 0 断链 0 孤立（47 处拦截 100% 属并行会话 WIP yishu/liaoyu）
- [x] 计数对账（check-bundles-index.py）：kexue 域与我方相关漂移清零

## 构建质量（AC-4）

- [x] sphinx-build（dummy, -E）：build succeeded，**east-west-dialogue 相关警告 0**（全库残余 5 条警告均属并行会话在途文件 meitong/liaoyu）
- [x] UTF-8 检查（check-utf8.py）：7481 文件全部通过
- [ ] `invoke gates.all` 全门一次通过——**环境限制**：invoke 缺 `invocations` 包不可用（既有已知问题，前序 spec 同款），以三个 scripts 直跑 + sphinx-build 等效替代

## 信源与事实（AC-5）

- [x] references 新增外部 URL 100% 经调研访问验证（research-notes.md 12 项留痕；审查 URL 抽查 4/4 新增可达）
- [x] facts.md ≥30 条事实——实际 43 条（F-001~F-043），每条带信源 id 归因
- [x] facts.md 全文无因果推断词（因为/导致/所以/由于/因此）——审查确认
- [x] 优先权争议事实并列诸说（F-018/F-020/F-021/F-022/F-023），无武断取一说——审查"最 consistently 执行的纪律"评价

## 六大对读主题覆盖（AC-6）

- [x] 几何与度量对读专文（四层完整——审查 6.1 表判定合格）
- [x] 数论与代数对读专文（四层完整）
- [x] 极限与无穷小对读专文（四层完整）
- [x] 符号化与抽象对读专文（四层完整）
- [x] 公理化与算法化对读专文（四层完整）
- [x] 接触与互鉴对读专文（四层完整）
- [x] 每篇西方节点链向 classics-reading 对应文档（审查链接抽查 8/8 可达 + 复验脚本 0 断链）
- [x] 每篇中国平行链向 suanjing-reading 对应文档（同上）

## 不重复既有内容（AC-7）

- [x] 无整段复制 classics-reading 或 suanjing-reading 正文（审查 6.3：未发现；反证 F-028 纠正源文笔误）
- [x] 每篇内容文档 ≥2 条指向既有两束的相对链接
- [x] 比较分析以"链接+概括+差异聚焦"呈现

## 对读示范质量（AC-8, rubric ≥4）

- [x] 3 篇示例各含四部分：原文对照（公共领域选段+底本标注）/ 解法逐步对照 / 现代统一解读 / 差异分析
- [x] 勾股对读：欧几里得 I.47 vs 赵爽弦图——审查验算全对（4×6+1=25 等）
- [x] 线性方程组对读：审查验算全对（x=37/4, y=17/4, z=11/4、det A=12、Cramer 全链路零误差）
- [x] 圆周率对读：审查发现两处硬伤（密率"落在盈朒二限之内"、S₂ₙ 分解理由句）→ **R-3/R-4 已修复**，复验数值自洽
- [x] 评分：审查初评 3.5（扣分集中在 R-3/R-4/R-7），修复后复验 PASS——扣分项全部消除，达标 ≥4

## 比较分析洞察力（AC-9, rubric ≥4）

- [x] 六主题比较分析讲清路径差异、优先权辨析、思想特征，非简单并置（审查 4/5：镜像概括、媒介即知识存亡、底本意识获好评）
- [x] 无时代错置、单线进化史观、文化优越论偏见（审查中立性判定 PASS，含双向防范与报警判据）
- [x] 评分 4/5 ≥4（扣分点"240 年"算术错误已修 R-5；Sarton 评语"之一"限定保留）

## 方法论闭环（AC-10, rubric ≥4）

- [x] insights.md ≥4 条四元组洞察（现象+根因+影响+建议）——实际 4 条
- [x] insights.md 附六主题 × 双方对应著作覆盖矩阵，无缺项（矩阵结论：三层覆盖无缺项）
- [x] ≥2 个可迁移比较阅读模式，各含触发条件/核心步骤/反模式/迁移示例四要素（同题双源对读法、思想路径分岔图法）
- [x] 评分 4/5 ≥4（扣分点死链验证标记与溯源声明过强已修 R-6/R-10）

## 命名与规范（NFR-4）

- [x] 新增文件名全部 kebab-case 纯英文——0 违规（正则扫描）
- [x] 全库 grep 无 `file:///` 绝对路径链接——0 命中
- [x] 正文为规范现代汉语

## 对抗审查（Task 9）

- [x] ≥12 个关键事实经独立 Web 复核——实际 26 项，0 硬错误 + 1 WARN（F-008 页码已标"转引待复核"）；发现 FAIL 项 6 类已全部修复闭环（review.md ⑨）
- [x] 抽样新增 URL 复验可达率 100%（4/4 新增 + 7 复用）
- [x] review.md 存在且含全部 AC 核验证据与 rubric 评分表 + 修复复验记录（结论 FAIL → 修复 → PASS）

## 提交闭环（Task 10）

- [x] git status 变更范围已核对：我方交付 = `east-west-dialogue/` 整目录（未跟踪）+ 3 个索引文件的对应行；暂存区当前含并行会话在途文件（physics 扩束、classics-reading 修改等），**本轮不执行 add/commit 以避免带走他方在途工作**
- [x] 原子提交建议已给出（Conventional Commits 格式），待用户确认
- [x] 未自动执行 git commit（用户确认前置）
