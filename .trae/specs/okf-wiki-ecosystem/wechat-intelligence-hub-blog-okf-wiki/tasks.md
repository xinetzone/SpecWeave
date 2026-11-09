# 任务清单（Spec Mode · tasks.md）

> 对应 [spec.md](spec.md) 的 ADDED Requirements；状态为 2026-11-06 V 阶段终检结果。

## 实施清单

- [x] 1. 启动协议回读根/子项目 `AGENTS.md`、`context-routing.md`、内容敏感度预检规范（三锚点确认）
- [x] 2. 解析 `/七概念` 斜杠别名 → `seven-concepts.md` + `seven-concepts-cmd`；加载 `blog-article-to-okf-wiki` 七阶段工作流
- [x] 3. 内容敏感度预检：Public，走标准 Spec Mode（不进 `playground/`）
- [x] 4. 取得博文全文并登记 F 编号事实（F-001~F-040），输出 spec `facts.md`
- [x] 5. P0 权威核验：GitHub REST API + 官方 README，补充 F-041~F-057；22 项 P0/P1 = 14✅/8⚠️/0❌
- [x] 6. 骨架判定（操作可复现性两问皆否 → 概念骨架，无 `examples/`）与归属决策（`jishu/ai/products/`）
- [x] 7. 信源先行生成 bundle：`references/` → `concepts/00~05` → 三级 `index.md` → 根 `index.md` → `log.md`
- [x] 8. 勘误四张清单齐全，8 项 ⚠️ 在正文逐项落实；标题 hook 标「未独立核验」
- [x] 9. 四级索引接入：`products`（38→39，导航行 + toctree）、`ai`（287→288）、`jishu`（描述 287→288）、`bundles`（714→715、jishu 523→524、ai 287→288、mermaid/节标题/计数行/frontmatter）；另同步 `README.md` 与 `doc/index.md`
- [x] 10. 机械门禁：`check-bundles-index.py` / `check-toctrees.py` / `check-utf8.py` 通过；双份 F 编号集合相等且连续；本束 42 条相对链接零断链
- [x] 11. V 阶段四视角对抗审查，结论写入 [review.md](review.md)
- [x] 12. C 阶段原子提交（用户「提交」指令后执行）：子模块单独提交本束 `log.md` 的 V/C 记录修正 → 主仓库提交 spec 四件并更新 gitlink；并行在途改动未纳入，未 push

## 全局门禁例外登记（非本束引入）

| 门禁 | 结果 | 判定 |
|------|------|------|
| `check-asset-baseline.py` | rc=1「行尾归一失效，残差 +299202」 | 工作树已干净、无 WIP 可 stash；属 Windows `core.autocrlf=true` 下字节归一的环境级假红；其**数字口径校验（total_bundles=715）已通过** |
| `check-section-anchors.py` | rc=1，全库 6557 处既有断链 / 413 处锚点警告 | 本束出现在报告中的次数为 **0**；全部为历史在途问题，按最小变更不代修 |
| `check-toctrees.py`（终检复跑） | rc=1，4 处导航问题 | 本束入库当次 rc=0；终检时并行会话新建 `products/wechatbridge/`（缺 index.md）与 `products/workbuddy-wechat-chat-forward-skills/`（缺 index.md + 2 篇 references 未收录）。4 处均非本束，按「谁添加谁接线」不代修 |

复跑命令（工作目录 `projects/awesome-okf-xs`）：

```bash
python scripts/check-bundles-index.py
python scripts/check-toctrees.py
python scripts/check-utf8.py
```
