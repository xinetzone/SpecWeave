# 任务清单（Spec Mode · tasks.md）

> 对应 [spec.md](spec.md) 的 ADDED Requirements；状态为 2026-11-06 V 阶段终检结果。
> 链路 `/七概念` → 场景 4「知识沉淀」R→I→E→V→C；结论 **通过，status: flagged**。

## 实施清单

- [x] 1. 启动协议回读根/子项目 `AGENTS.md`、`.agents/context-routing.md`、内容敏感度预检规范、frontmatter 规范（三锚点确认）
- [x] 2. 解析 `/七概念` 斜杠别名 → `.agents/commands/seven-concepts.md` + `seven-concepts-cmd`；能力注册表 `02-skills.md` / `03-commands-*.md` 两处登记行核对；加载 `blog-article-to-okf-wiki` 七阶段工作流
- [x] 3. 内容敏感度预检：`mp.weixin.qq.com/s/<id>` 公开短链、无访问控制参数 → **Public** → 标准 Spec Mode（不进 `playground/`）
- [x] 4. 取得博文全文并登记 F 编号事实（源文 F-001~F-061），输出 spec [facts.md](facts.md)；WebFetch 直接成功，未触发反爬回退（已在 log.md 登记流程偏差）
- [x] 5. P0 权威核验：GitHub REST API、README、dev-spec、schedule、验收记录、tree/contents API + 权威第三方转述 → 补充 F-062~F-084；**24 项 P0/P1 = 12✅ / 8⚠️ / 4❌**
- [x] 6. 骨架判定（操作可复现性两问皆「是」→ 技术教程/方法论骨架，设 `examples/`）与归属决策（`jishu/ai/products/wechatbridge-ios-relay/`；避让并行会话占用的 `wechatbridge/`）
- [x] 7. 信源先行生成 bundle：`references/` → `concepts/00~05` → `examples/00~02` → 三个目录 `index.md` → 根 `index.md` → `log.md`，共 **16 个 md**
- [x] 8. 勘误四张清单齐全；4 项 ❌ 与 8 项 ⚠️ 在正文逐项落实；`status: flagged` 四处落地（frontmatter / verification 顶部 / index 边界 / concepts/00 读前须知）
- [x] 9. V 阶段修复：`article-source.md` 11 条 F 行的早期 V 编号对齐到最终 V-01~V-24；3 处引文链接标记去链接（消除 Sphinx 相对链接断链）
- [x] 10. 四级索引接入（以目录树地面真值 718 做 +1 增量）：`products`（41→42，导航行 + toctree `wechatbridge-ios-relay/index`）、`ai`（290→291，products 41→42）、`jishu`（描述 290→291）、`bundles`（717→718、jishu 526→527、ai 290→291；frontmatter / 计数行 / mermaid / 域节标题 / 分组表束数列五面一致）；另同步 `README.md`（7 处）与 `doc/index.md`（2 处）
- [x] 11. 机械门禁终检：`check-bundles-index.py` rc=0（9 域/64 组/718 束）、`check-toctrees.py` rc=0、`check-utf8.py` rc=0（12961 文件）；手动等效 16 文件 / F 双份 84=84 连续 / 全文 F 与 V 引用越界 0 / 70 条相对链接断链 0 / 4 个 index 全含 toctree
- [x] 12. V 阶段四视角对抗审查与 G1~G4 质量门，结论写入 [review.md](review.md)；`[CMD-LOG]` 结构化日志写入 bundle `log.md`
- [ ] 13. C 阶段原子提交：**用户未要求 commit/push，本会话不执行**。后续顺序为 ① 子模块提交 bundle + 四级 index + `README.md` + `doc/index.md` → ② 主仓库提交 spec 目录 → ③ 主仓库更新 gitlink；用 `git-commit-utf8.py` 显式列全文件

## 全局门禁例外登记（非本束引入）

| 门禁 | 结果 | 判定 |
|------|------|------|
| `check-asset-baseline.py` | rc=1「行尾归一失效，残差 +245636」 | 工作树含并行会话未提交 WIP + Windows `core.autocrlf` 环境级假红；脚本要求「提交或 stash 后复跑」。其**规模数字校验已通过**（读取 `total_bundles: 718`），`.spec/ 泄漏守卫`亦通过 |
| `check-section-anchors.py` | rc=1，全库约 6520 处历史断链 / 锚点问题 | 报告中检索 `wechatbridge-ios-relay` **命中 0 次**；全部为存量在途问题，按最小变更不代修 |
| `invoke gates.*` | 不可用（`ModuleNotFoundError: No module named 'invoke'`） | 按 `blog-article-to-okf-wiki` §7，**不声称「gates 通过」**，改以脚本直跑 + 手动等效清单替代 |

复跑命令（工作目录 `projects/awesome-okf-xs`）：

```bash
python scripts/check-bundles-index.py
python scripts/check-toctrees.py
python scripts/check-utf8.py
```

## 复核待办（`stale_after: 2027-01-31`）

- [ ] iOS 上架与路线图状态是否变更；若变更，重判 V-21 并更新 `status`
- [ ] 灵动岛 / Live Activity 是否进入后续版本；若是，重判 V-22
- [ ] 官方验收记录 R3–R6 是否补齐真机结论、R7 长按是否真机通过
- [ ] 模型权重公开后的「开源」措辞（V-24）与星标等动态数字刷新
