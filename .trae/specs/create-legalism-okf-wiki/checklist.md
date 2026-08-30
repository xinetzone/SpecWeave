# Checklist

## 原文忠实性

- [x] 核心篇目（《韩非子》8 篇、《商君书》7 篇、《管子》6 篇、申慎辑佚）原文均经至少两个独立权威信源逐字核对
- [x] 关键异文显式标注"某本作某"并给出校本出处，在 facts 文件登记编号事实与信源 URL（如 F-HF-051 辟/避、F-SJS-033 刑者/利者、F-SJS-067/068 等）
- [x] 《申子》《慎子》佚文逐条标注辑佚来源（严可均辑本、《意林》、守山阁本等），不将辑佚文本伪装成传世完本

## 文本真伪与归属诚实分层

- [x] 《管子》明确标注"托名管仲、稷下学派混合文集"性质，不将其全部内容等同于管仲思想
- [x] 《商君书》明确标注"非商鞅手著、后学与官文书结集"属性
- [x] 《韩非子·初见秦》《存韩》等争议篇并列呈现主要归属学说及依据，无单方面裁决
- [x] 全部四个 bundle 不将传统托名当史实陈述

## 解读多元性

- [x] 核心命题（法不阿贵、刑无等级、性本利、仓廪实知礼节等）解读至少呈现 2 种立场并标注出处（如法不阿贵的江荣海人治/法治定性之争 F-HF-040）
- [x] 解读覆盖古注/校勘、现代学术（冯友兰、萧公权、郭沫若等）、西方汉学（Watson、Pines、Creel 等）多元传统

## OKF 格式与导航

- [x] 所有新增内容文档含可解析 YAML frontmatter 且 `type` 非空，遵循 OKF v0.2（含 `sources` 溯源字段）
- [x] 四个 bundle 根 `index.md` 均以 `{toctree}` 引用全部内容文档；分组 `index.md` 引用全部 4 个 bundle
- [x] 文件名均为 kebab-case 纯英文，正文中文；Markdown 交叉引用为相对路径且无断链
- [x] `think/index.md` 分组表新增 legalism 行，toctree 含 `legalism/index`
- [x] `bundles/index.md` 统计更新：实际为 total_bundles 293、groups 36（spec 预估 290/33 因并行会话基数推进而调整，think 域 13 束 7 组），生态关系图与推荐路径的 think 标签补 legalism
- [x] `projects/awesome-okf-xs` 下 `invoke gates.all`：UTF-8 全量通过；legalism 相关 toctree 问题清零（修复 shang-jun-shu 根索引补 log、6 个子索引补 hidden toctree 后复查无 legalism 报错；剩余报错均属其他并行会话未完成 bundle）

## 方法论闭环（seven-concepts 场景4）

- [x] G1：facts 文件合计 ≥50 条编号事实（《韩非子》≥20、其余各 ≥10）——实际合计 193 条（50+66+46+31），事实陈述无因果推断词
- [x] G2：insights.md ≥4 条洞察，每条含现象/根因/影响/建议四元组
- [x] G3：≥2 个可复用阅读模式，每个含触发场景/核心步骤/反模式/迁移示例——实际 3 个
- [x] V：随机抽查 10 条 facts 事实与信源一致，原文抽查逐字一致，无虚构引证（审查发现 5 项中低危问题已全部修复）
- [x] C：子模块仓库原子提交（Conventional Commits、中文主体）——347430d7/def28de4/f62b998a/ccc1aa53/b188ef96；主仓提交 fc91c9b40

## 边界与安全

- [x] 未修改任何既有 bundle 内容与 SpecWeave 主仓既有文件
- [x] 新增文件仅位于 `projects/awesome-okf-xs/doc/bundles/think/`（及两处索引更新）与 `.trae/specs/create-legalism-okf-wiki/`
- [x] 内容敏感度判定为 Public，产出物路径与级别匹配（公开知识 → `doc/bundles/`）
