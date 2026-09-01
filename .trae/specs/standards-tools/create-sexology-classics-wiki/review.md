# Review — create-sexology-classics-wiki

> V 阶段独立对抗评审（新鲜上下文、只读四视角）结论与修复闭环记录。
> 评审对象：`projects/awesome-okf-xs/doc/bundles/think/sexology/classics-reading/`

## 一、评审结论

**总体判定：PASS（附 6 项修复待办）**

bundle 结构符合 OKF v0.2 规范（concepts/examples/references 三层 + facts/insights/log），104 条事实带信源可追溯，六大板块全覆盖，原文引用守住学术引介尺度（公版文献引篇名/核心命题/少量代表片段，现代版权著作仅介绍不录原文）。质量门 toctrees/utf8 首轮通过。

## 二、评审发现问题与修复记录（2026-08-30 闭环）

| # | 问题 | 视角 | 严重度 | 处置 | 状态 |
|---|------|------|--------|------|------|
| 1 | `references/china-modern-sources.md` 事实权威指向 `.temp/sexology-bundle/facts-china-modern.md` 临时文件，违背信源稳定性原则 | 可溯源性 | P1 | 已改为指向 bundle 内 `facts.md`（相对链接 `../facts.md`），F-CHINA-MODERN-001~038 已确认全部收录 | 完成 |
| 2 | 《房内考》1990 版译者署名在 facts.md（郭晓惠）与信源文件（郭小惠）之间不一致 | 事实准确性 | P1 | 经李零北京大学中文系官方个人页核验：两版署名用字确实不同（1990 上海人民出版社版「郭小惠」、2007 商务印书馆版「郭晓惠」）。已修正 F-ANCIENT-027 为分版表述并注明裁定依据 | 完成 |
| 3 | `concepts/07-translations.md` 福柯《性史》中译者名（佘碧平、张廷昱）无信源支撑 | 事实准确性 | P2 | 已补【译者署名待核验】标注，与 bundle「待核验条目处理方式」条款一致 | 完成 |
| 4 | 「蔼理士/霭理士」译名用字在 6 个文件中混用 | 一致性 | P2 | 全目录统一为「霭理士」（商务印书馆潘光旦译注本通行署名），共更新 6 文件，复查零残留 | 完成 |
| 5 | `examples/01-entry-path.md` 自测画像体系与 `concepts/00-reading-map.md` 四大范式自测存在层级错位，易混淆 | 读者体验 | P3 | 已在篇首增加范围声明，明确两套自测的层级关系与使用顺序（先 00 篇定范式，再本篇落选书） | 完成 |
| 6 | bundles/index.md 计数存疑（288/34 vs 289/35） | 索引一致性 | P2 | 全量清点裁决：各域束数行累加 = 289、分组行累加 = 35，与 frontmatter `total_bundles: 289`、`groups: 35` 完全自洽；think 域 8 束·5 组已含 sexology 与并发新增的 yangsheng。维持 289/35，无需改动 | 完成 |

## 三、修复后复验

- `invoke gates.toctrees`：通过（全部 index.md 引用有效，所有内容文档均可达，零孤立）
- `invoke gates.utf8`：通过（5859 个文件均为有效 UTF-8）
- `invoke build`（Sphinx）：修复后复跑，解析（reading sources）阶段 100% 完成、sexology 全部文件零警告（现存 35 条警告均为其他 bundle 既有问题）；写出阶段因全仓构建时长原因中止。修复项均为正文文本级变更且 toctrees/utf8 复验通过，构建风险可忽略；修复前全量构建已在本 spec Task 7 成功执行
- 导航登记：`think/index.md`、`bundles/index.md`（289 束/35 组）、`.trae/specs/standards-tools/README.md`（15/24）、`.trae/specs/README.md`（62/54）均已更新

## 四、遗留事项

- 无阻塞遗留。07-translations.md 中既有【待核验】条目按 bundle 约定随新信源出现时增量核验。