---
title: "Spec：千问创作平台多Agent协同资讯速报 → OKF 知识包"
status: "draft"
---

# Spec：千问创作平台多Agent协同资讯速报 → OKF 知识包

## 目标

按 L2 版 `blog-article-to-okf-bundle` 模式，将微信博文《阿里做了个AI短剧团队，不是工具》转化为 OKF 知识包，**首次验证"资讯速报"骨架**（index+references+log，concepts仅1篇，stale_after 1-2月）。

## 归属

- 域：ai/
- 分组：ai-agent/（用户确认，核心为多Agent协同）
- bundle：`qwen-creative-platform-news/`

## 骨架（资讯速报）

```
qwen-creative-platform-news/
├── concepts/
│   ├── index.md
│   └── 00-multi-agent-creative-team.md   # 唯一概念：多Agent剧组协同
├── references/
│   ├── index.md
│   ├── article-source.md                  # F-001~F-034 博文事实
│   └── verification.md                    # 8项P0核验（5通过3勘误）
├── index.md
└── log.md
```

无 examples/（资讯速报无可运行代码示例）。

## 关键约束

- stale_after: 2026-10-31（资讯速报约2个月）
- frontmatter 标注资讯速报性质
- 3项勘误如实记录：Wan上一代版本号（2.5→2.7）、Arena排名时效性、小云雀表述简化
- ManClaw搭载字节Seedance 2.0（非阿里Wan 3.0）需标注
- 区分客观事实与导演观点（F-031~F-034）
- 索引更新：ai-agent 21→22 bundles，bundles/index.md total 270→271, ai域 97→98

## 验收

- [ ] 7文件生成，UTF-8编码
- [ ] toctree三级完整（根→子目录→文档）
- [ ] F编号全部可追溯
- [ ] 3项勘误在verification.md和index.md已知边界中如实呈现
- [ ] 相对路径无file:///
- [ ] 父分组index + bundles/index.md计数同步
- [ ] external/无变更
