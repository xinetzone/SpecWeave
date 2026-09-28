# Tasks：WorkBuddy 博文 → OKF 知识包

工作流：blog-article-to-okf-wiki 七阶段（预检→R 事实核验→I 骨架拆分→E 信源先行→V 审查收尾→C 提交）

## R 阶段（事实采集与核验）

- [x] T1 微信反爬处理：WebFetch 成功提取全文（browser_use 因 Chrome 扩展未连接失败，按回退序直接 WebFetch 命中）
- [x] T2 信源距离预判：厂商正面实测软文（第三方产品经理媒体 + 文末导流 CTA + 同日官宣配套）
- [x] T3 F-001~F-022 博文事实登记（作者观点/体验评价/营销 CTA 显式分层）→ facts.md
- [x] T4 P0/P1 核验 8 项：沙利文报告与双榜第一、腾讯身份、应用发布能力、专家团、连接器、市场数据、机构背书、博文元信息
- [x] T5 F-023~F-032 核验补充登记（6✅/2⚠️/0❌，源文零硬错误）

## I 阶段（骨架与归属）

- [x] T6 操作可复现性两问：两问皆否 → 无 examples/，商业/产品资讯骨架
- [x] T7 归属决策：jishu/ai/tencent/（候选对照表见 spec.md §3）
- [x] T8 三层知识地图：事件层/机制体验层/格局判读层（spec.md §4）

## E 阶段（信源先行生成 bundle）

- [x] T9 建目录 `jishu/ai/tencent/workbuddy-one-sentence-mvp/`
- [x] T10 references/：article-source.md（F-001~F-032 双份登记）+ verification.md + index
- [x] T11 concepts/：00 事件与产品背景、01 实测全流程、02 能力判读与软文读法 + index
- [x] T12 根 index.md（软文提示块/已知边界/主题关联/双信源）+ log.md

## V 阶段（对抗审查与索引收尾）

- [x] T13 四视角审查（事实溯源/结构规范/读者可用/时效边界）——F 编号逐篇核对、观点分层、单源双处标注、mermaid 安全
- [x] T14 双份 F 编号正则比对（facts.md ↔ article-source.md：均 32 条、集合相等、无跳号）
- [x] T15 父级 tencent/index.md 接入（导航行 + toctree + 相关链接；束数 7→8、信源 29→31、事实 470→502；顺带校正概念数历史漂移 →45）
- [x] T16 bundles/index.md 计数同步（以提交态 572 为基线 →573、jishu 432→433、ai 212→213；frontmatter/粗体/mermaid/节标题/分组表五处）
- [x] T17 机械门禁：UTF-8 strict（全库 10657 文件 ✅）/ 本束 8 toctree 条目 / 28 相对链接 / 零 file:/// / frontmatter 完整；全库 toctrees+bundles 两门禁唯一失败项为并行会话未接入的 lightvela 束（非本任务产物，已在 log.md 记录，不代接）
- [x] T18 ai/index.md 腾讯行无计数列，无需改动（已核实）

## C 阶段（提交）

- [ ] T19 子模块 awesome-okf-xs 内原子提交（显式文件列表，不 push）
- [ ] T20 主仓库提交 spec + 子模块指针（用户确认后执行）
