---
title: "Spec：Qwen-UI-Agent 技术评测 → OKF 知识包"
status: "draft"
---

# Spec：Qwen-UI-Agent 技术评测 → OKF 知识包

## 目标

按 L2 版 `blog-article-to-okf-bundle` 模式，将微信博文《阿里刚开源的 Qwen-UI-Agent》转化为 OKF 知识包。内容性质为**技术评测/选型类**（含3个实测流程），使用技术教程/选型骨架（含examples）。

## 归属

- 域：ai/
- 分组：ai-agent/（GUI Agent 属 Agent 框架范畴）
- bundle：`qwen-ui-agent/`

## 骨架（技术评测/选型）

```
qwen-ui-agent/
├── concepts/
│   ├── index.md
│   ├── 00-project-overview.md        # 项目概述与定位
│   ├── 01-capabilities-benchmarks.md # 技术能力与基准成绩
│   └── 02-practice-and-pitfalls.md   # 实测踩坑与部署
├── examples/
│   ├── index.md
│   └── 01-three-internal-workflows.md # 3个内部流程实测
├── references/
│   ├── index.md
│   ├── article-source.md
│   └── verification.md
├── index.md
└── log.md
```

共11文件。

## 关键约束

- 3项核验勘误如实记录：
  1. F-032/F-042：混淆MAI-UI 1.0与Qwen-UI-Agent，Qwen-UI-Agent权重尚未发布
  2. F-033：58%步数节省仅限OSWorld-v2对比MiniMax M3，非"整体"
  3. F-034：8B为旧版模型，Python 3.10+/PyTorch 2.0+无官方依据
- 博文3个流程为团队自述实测（F-038），非官方benchmark，需标注
- 分数为阿里自报（F-027），第三方未复现
- stale_after: 2026-12-31（技术项目，约4个月）
- 索引更新：ai-agent 22→23 bundles，bundles/index.md total 271→272, ai域98→99

## 验收

- [ ] 11文件生成，UTF-8编码
- [ ] toctree三级完整
- [ ] F编号全部可追溯
- [ ] 3项勘误如实呈现
- [ ] 相对路径无file:///
- [ ] 父分组index + bundles/index.md计数同步
- [ ] external/无变更
