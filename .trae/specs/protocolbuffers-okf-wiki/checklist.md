# Checklist

## 覆盖完整性
- [ ] `external/libs/protocolbuffers/` 下全部 2 个子仓库（protobuf、protobuf-ci）均有对应知识束
- [ ] protobuf 主仓全部顶层子目录（src、python、java、csharp、objectivec、php、ruby、rust、hpb、hpb_generator、editions、conformance、benchmarks、examples、docs、lua、bazel、cmake）在 references/ 信源登记且被 concepts/ 覆盖
- [ ] protobuf 束概念文档 ≥15 篇，protobuf-ci 束概念文档 4-5 篇

## G1-R 阶段：事实零推测
- [ ] 事实文件（facts-*.md）每条编号 F-xxx 并指向具体源码路径
- [ ] 事实中无"用于/目的是/设计为/因为/导致"等推断性表述

## G2-I 阶段：洞察四元组
- [ ] insights.md 含 3-5 条洞察，每条含陈述/证据（引用 F-xxx）/反常识/行动
- [ ] 含知识地图：概念分组、依赖关系、学习路径、概念-事实映射

## G3-E 阶段：生成纪律
- [ ] references/ 信源文件先于 concepts/ 生成
- [ ] concepts/ 分批生成，每批 ≤7 篇
- [ ] 各级 index.md 在所有内容文档定稿后最后生成
- [ ] 交叉链接全部使用 `/` 开头 bundle-relative 路径（无 `../`）

## G4-V 阶段：独立验证
- [ ] Grep 验证：文档中引用的类名/方法名在 `external/libs/protocolbuffers/` 源码中全部存在，零虚构 API
- [ ] 链接检查：所有交叉链接目标文件存在，无断链
- [ ] Frontmatter 检查：所有内容文档含 type/title/description/tags/generated/verified/status/stale_after/sources 完整字段，sources 指向存在的文件
- [ ] 束根 index.md 含 `okf_version: "0.2"` 与 `{toctree}`（覆盖全部内容文档）；子目录 index.md 无 frontmatter
- [ ] 代码示例中的 API 调用与 facts 中事实一致

## 索引与构建质量门
- [ ] `comm/serialization/index.md` 分组索引已创建（含生态关系图与学习路径）
- [ ] `comm/index.md` 已注册 serialization 分组
- [ ] `doc/bundles/index.md` 总索引计数已更新（束 263→265、分组 30→31）
- [ ] `invoke gates.toctrees` 通过（无断链、无孤立文档、bundle 根 index 完整）
- [ ] `invoke gates.utf8` 通过
- [ ] 源码目录 `external/libs/protocolbuffers/` 无任何修改（git status 干净）

## G5-C 阶段：模式沉淀
- [ ] 模式/经验文档已入库或 skill 模板已更新（含本次新发现的反模式，如有）
- [ ] 两束 log.md 记录生成信息（日期、生成者、源码版本 protobuf v37.0）
- [ ] tasks.md 全部勾选
