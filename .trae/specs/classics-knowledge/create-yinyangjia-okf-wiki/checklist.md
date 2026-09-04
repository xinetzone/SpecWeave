# Checklist

## 内容权威性与真实性
- [x] 《汉书·艺文志》阴阳家著录全目逐家登记（二十一家三百六十九篇），与点校本/ctext.org 核对一致
- [x] 邹衍佚文经 ctext.org + 维基文库（或辑佚书电子版）双源逐字核对，异文在 facts.md 登记且正文显式标注"某本作某"（Y-01～Y-23）
- [x] 所有文本材料按三层标注：A 确证佚文（注明辑本与原始引书）/ B 争议归属（列出分歧依据）/ C 受影响传世文献，无混用
- [x] 阴阳家著作"全部亡佚"事实清晰呈现，无构拟补全文本，无将 B/C 层材料陈述为"阴阳家原文"
- [x] 邹衍事迹逐条标注史料出处（《史记》直接史料与后世追述区分）
- [x] 五德终始说解读含《吕氏春秋·应同》原文 + ≥1 古代评述 + ≥2 现代研究观点，均标注出处

## OKF 格式与导航
- [x] 所有新增文档带 OKF v0.2 YAML frontmatter（type: OKF、source、generated/verified、status、stale_after）
- [x] bundle 根 index.md 以 `{toctree}` 引用全部内容文档，无孤立文档、无断链
- [x] 文件名 kebab-case 纯英文，正文中文，Markdown 相对路径交叉引用（无 file:/// 绝对路径）
- [x] 派生产物 frontmatter 标注 `sources` 溯源字段
- [x] `think/index.md` 新增 yinyangjia 分组行 + toctree 条目
- [x] `bundles/index.md` 统计数字与 think 域描述更新（以仓库实际状态为基准 +1）
- [x] 在 `projects/awesome-okf-xs` 运行 `invoke gates.all` 通过（UTF-8 + toctree 完整性）——阴阳家知识包零告警；整体失败项均来自并行会话在途目录（confucian/、buddhism/heart-sutra），不属本 spec 范围

## 方法论闭环（seven-concepts 场景4）
- [x] facts.md ≥30 条编号事实，无因果推断词（"因为/导致/所以"等），每条含信源 URL（G1）（实际 64 条）
- [x] insights.md ≥3 条洞察，每条含完整四元组（陈述/证据 F-xxx/反常识/行动）（G2）（实际 4 条）
- [x] ≥2 个可复用阅读模式：触发场景 + 核心步骤 + ≥3 反模式 + 检验标准 + 跨领域迁移示例（G3）
- [x] 对抗审查（V）完成：4 视角覆盖、意见 ≥5 条且具体、抽查 10 条事实全部与信源一致、至少采纳 2 条修正（review.md Q-01～Q-07）
- [x] 子模块内原子提交：单一职责、Conventional Commits 中文描述"为什么"、提交信息无乱码（G4）（子模块 cf70f93b + 主仓 gitlink 同步 a1b23c6a8，消息经字节级校验为干净 UTF-8）
- [x] log.md 记录 R→I→E→V→C 各阶段产出与质量门通过记录
