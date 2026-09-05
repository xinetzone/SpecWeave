---
status: "completed"
title: "Spec：GPT-5.6 大素数空隙突破资讯 → OKF 知识包"
---

# Spec：GPT-5.6 大素数空隙突破资讯 → OKF 知识包

## 目标

按 `blog-article-to-okf-wiki` Skill 七阶段工作流（R→I→E→V），将知乎博文《GPT-5.6仅用一天改写数学史，「双菲」五人团队8年纪录被破！》转化为 OKF v0.2 知识包，归属 `kexue/math/` 分组，采用**资讯速报骨架**。

## 归属

- 域：`kexue/`（科学）
- 分组：`math/`（数学）
- bundle：`gpt56-large-prime-gaps/`

## 骨架（资讯速报）

```
gpt56-large-prime-gaps/
├── concepts/
│   ├── index.md
│   └── 00-gpt56-prime-gap-breakthrough.md   # 唯一概念：GPT-5.6大素数空隙突破
├── references/
│   ├── index.md
│   ├── article-source.md                    # F编号博文事实清单
│   └── verification.md                      # P0核验报告（含勘误）
├── index.md
└── log.md
```

无 `examples/`（资讯速报无可运行代码示例，非操作教程）。

## 内容概述

**文章核心内容**：
- GPT-5.6 在一天内打破陶哲轩五人团队保持8年的大素数空隙（Large Prime Gaps）纪录
- 提出全新方法「倾斜剩余类」（Skewed Residue Classes）
- 同步给出 Lean 4 形式化验证证明
- 新结果比 2018 年五人组结果省去一个 log₃(n) 因子
- 涉及人物：Jared Duker Lichtman（斯坦福）、陶哲轩、James Maynard、Kevin Ford、Ben Green、Sergei Konyagin
- 背景：素数分布问题、张益唐有界素数空隙、Erdős 第四问题

## 关键约束

- **stale_after**：2026-11-04（资讯速报约2个月，数学领域进展相对稳定可稍长）
- frontmatter 标注「资讯速报」性质
- **信源距离**：厂商/媒体报道（新智元转载），核心数字与结论需 P0 核验
- 区分客观事实与作者观点（如「人类的荣光」等抒情表述为作者观点）
- 所有成效数字（提效倍数、改进幅度）默认 P0 必核验
- 索引更新：math 分组 3 → 4 bundles，kexue 域 16 → 17 束，总计 500 → 501 束

## 验收

- [ ] 6 文件生成（index + concepts/index + 00-concept + references/index + article-source + verification + log = 7 文件）
- [ ] UTF-8 编码无乱码
- [ ] toctree 三级完整（根 → 子目录 → 文档）
- [ ] F 编号全部可追溯，无事实外编造
- [ ] P0 核验结果在 verification.md 如实呈现，勘误在正文落实
- [ ] 相对路径无 `file:///` 绝对路径
- [ ] 父分组 index + bundles/index.md 计数同步
- [ ] `status` 正确（stable / flagged / draft）
