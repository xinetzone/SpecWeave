---
source: ".trae/specs/design-library-archive/spec.md；实测命令 d:/spaces/SpecWeave/external/dao/xinzo/.trae-cn/design_libraries/（2026-09-03）"
date: "2026-09-03"
type: "manifest"
title: "design-library-archive 迁移清单（冻结）"
---

# design-library-archive 迁移清单

## 盘点结论

- 十六源目录全部唯一设计库：**16**
- 跳过 `__MACOSX/` 目录（macOS 资源分支元数据）
- **本次新增归档 = 16 个技能目录**，合计约 **2,419 文件 / 9.45MB**（文件数/字节数一列均为归档后目标树实测）
- 源目录 `external/dao/xinzo/.trae-cn/design_libraries/` **只读**，本次仅复制不搬移
- `dl_builtin_trae` 顶层无 SKILL.md，取 `TRAE(1)/` 子目录内完整版本
- `dl_builtin_doubao`、`dl_builtin_golden_time`、`dl_builtin_trae`、`dl_builtin_trae_work` 的 SKILL.md 无 YAML frontmatter，归档时前置最小 frontmatter

## 冻结映射（16）

| 源目录 | metadata.name | SKILL.md name | 目标目录名 | 文件数 | 字节数 |
|---|---|---|---|---|---|
| external/dao/xinzo/.trae-cn/design_libraries/dl_builtin_21th | 21th | 21th-design | 21th-design | 60 | 100,541 |
| external/dao/xinzo/.trae-cn/design_libraries/dl_builtin_apple | 苹果 | pinguo-apple-design | pinguo-apple-design | 63 | 122,718 |
| external/dao/xinzo/.trae-cn/design_libraries/dl_builtin_barbie | Barbie | barbie-design | barbie-design | 60 | 100,127 |
| external/dao/xinzo/.trae-cn/design_libraries/dl_builtin_claude | Claude | claude-design-system-design | claude-design-system-design | 58 | 149,870 |
| external/dao/xinzo/.trae-cn/design_libraries/dl_builtin_doubao | 豆包 | （无 frontmatter） | doubao-design | 63 | 148,007 |
| external/dao/xinzo/.trae-cn/design_libraries/dl_builtin_golden_time | Golden Time | （无 frontmatter） | golden-time-design | 60 | 220,658 |
| external/dao/xinzo/.trae-cn/design_libraries/dl_builtin_google | 谷歌 | google-design | google-design | 60 | 103,573 |
| external/dao/xinzo/.trae-cn/design_libraries/dl_builtin_minimalist | 极简 | minimal-dashboard-design | minimal-dashboard-design | 63 | 154,130 |
| external/dao/xinzo/.trae-cn/design_libraries/dl_builtin_motion_fit | Motion Fit | motionfit-design | motionfit-design | 60 | 103,165 |
| external/dao/xinzo/.trae-cn/design_libraries/dl_builtin_nerv | Nerv | nerv-design | nerv-design | 60 | 100,773 |
| external/dao/xinzo/.trae-cn/design_libraries/dl_builtin_tik_tok | 抖音 | tiktok-design | tiktok-design | 31 | 142,598 |
| external/dao/xinzo/.trae-cn/design_libraries/dl_builtin_trae | TraeCode | Nimbus Core（无 frontmatter） | nimbus-core-design | 181 | 450,380 |
| external/dao/xinzo/.trae-cn/design_libraries/dl_builtin_trae_work | TraeWork | TraeWork Design System（无 frontmatter） | trae-work-design | 730 | 2,211,535 |
| external/dao/xinzo/.trae-cn/design_libraries/dl_builtin_vercel | Vercel | vercel-design-library-design | vercel-design-library-design | 63 | 144,632 |
| external/dao/xinzo/.trae-cn/design_libraries/dl_builtin_volcengine | 源力 | 源力设计系统 (Yuanli Design System)（无 frontmatter） | yuanli-design-system | 744 | 5,473,693 |
| external/dao/xinzo/.trae-cn/design_libraries/dl_builtin_vibe_camp | Vibe Camp | vibecamp-design | vibecamp-design | 63 | 179,067 |

## 合计核对

- 文件数（目标树实测）：60+63+60+58+63+60+60+63+60+60+31+181+730+63+744+63 = **2,419**
- 字节数（目标树实测）：100,541+122,718+100,127+149,870+148,007+220,658+103,573+154,130+103,165+100,773+142,598+450,380+2,211,535+144,632+5,473,693+179,067 = **9,905,467 bytes ≈ 9.45 MB**
- 与源树差异：①SKILL.md 前置 frontmatter/source 字段使多数库字节微增；②归档时删除 `.DS_Store`（tiktok -1、trae-work -3、nimbus 顶层化去冗余 -2）；③nimbus-core-design 取 `TRAE(1)/` 顶层化（原统计按 `dl_builtin_trae` 全树含冗余顶层 css/ 计，偏高）
