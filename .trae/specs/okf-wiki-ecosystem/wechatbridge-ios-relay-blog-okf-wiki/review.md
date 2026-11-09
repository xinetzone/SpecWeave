# V 阶段对抗审查记录（Spec Mode · review.md）

> 审查对象：`projects/awesome-okf-xs/doc/bundles/jishu/ai/products/wechatbridge-ios-relay/`
> 审查时间：2026-11-06 · 链路：R→I→E→**V**→（C 仅登记） · 结论：**通过，`status: flagged`**

## 1. 四视角审查与采纳结果

| 视角 | 提出的质疑 | 采纳与修复 |
|------|-----------|-----------|
| 🔴 魔鬼代言人 | 「iOS 已开发完成 / 正在提审」会不会只是 README 没更新，判 ❌ 是否过重？ | 交叉核对四处独立一手件：README「iOS 版正在开发中」+ 路线图 `[ ] iOS 版` 未勾选 + dev-spec §10 交付定义未全打勾 / §11 Q2「上架中国区需要 App 备案」仍待决 + 验收记录 R3–R6「待真机」。四者一致指向开发中，故维持 **❌ V-21**；同时保留博文原话并列呈现，不删除源文口径 |
| 🟠 老板视角 | 产品方自述文里的成效数字（1.7k star、6 小时、55 分）能不能直接引用？ | 全部 P0 化：`verification.md` 建「成效数字溯源表」，6 小时标注「无独立出处、禁止提效倍数」，星标双时点并列，55 分标媒体转述层级；根 index 增设「厂商/作者自述数据提示」块，并设 `status: flagged` + `stale_after: 2027-01-31` |
| 🔵 未来视角 | iOS 上架状态、模型开源措辞两周内就会变，怎么防陈旧？ | `concepts/05 §6` 四项到期复核清单 + `log.md` 复核清单；`stale_after` 缩短；所有动态数字带时点，禁止互相「修正」 |
| 🟣 新人视角 | 读者会不会把 examples 当成安装教程，或把 6 小时 / 18 工作日相除？ | `examples/index.md` 与 `examples/02` 顶部写明「不是安装教程、App 未上架、不含 IPA/签名/TestFlight」；`article-source.md`「事实使用约束」6 条 + `concepts/02` + `concepts/05` + 根 index 四处重复「禁止相除得提效倍数」 |
| ⚪ 证据强度 | 「待真机」有没有被推测填补？截图图注能否当功能验收？ | 全束采用 ✅ / ⚠️ / ❌ 三态；官方 R3–R6 一律保留「待真机」、R7 保留「模拟器通过，待真机」；「客户复盘」六项判 V-17「仅博文单源」；不以图片内文字补写 UI 细节 |
| ⚫ 编号一致性 | 事实清单里的 V 编号和核验报告对不对得上？ | **发现真实缺陷**：`article-source.md` 11 条 F 行仍引用 R 阶段早期编号（F-009→V-05、F-019→V-11、F-037→V-22 等），而核验表最终重排为 V-01~V-24。已逐条对齐，复跑全文 V 引用 24 个编号、越界 0 |
| ⚫ 链接可达性 | 逐字引文里的官方 Markdown 链接会不会被构站器当成本束相对链接？ | **发现真实断链 2 处**：F-072 引文与引文核对表中的「档期文档」链接标记。已在 `facts.md` / `article-source.md` / `verification.md` 三处去链接保留文字并括注目标；终检 70 条相对链接断链 0 |

## 2. G1~G4 质量门

| 门 | 判据 | 结果 |
|----|------|------|
| G1 事实 | F 编号事实无推断词、数字/版本/命令均有出处；双份登记集合一致 | ✅ 84 条（F-001~F-084），`facts.md` ↔ `article-source.md` 集合相等、连续无跳号、双向差集为空；全文引用 84 个编号越界 0 |
| G2 骨架/归属 | 操作可复现性两问；主线实体优先、查先例、单篇博文不新建分组 | ✅ 两问皆「是」→ 设 `examples/`；归 `products/wechatbridge-ios-relay/`，避让并行会话占用的 `wechatbridge/`，有 wigolo / craft-anything / wechat-intelligence-hub 先例 |
| G3 信源先行 | references 先于 concepts，各级 index 最后 | ✅ 生成顺序已在 `log.md` E 段登记；4 个 index 全部含 `{toctree}` |
| G4 对抗审查 + 机械门禁 | 五视角 + 索引/toctree/UTF-8/链接/frontmatter/`flagged` 落地 | ✅ 见下表；`flagged` 四处落地逐项勾对 |

## 3. 机械门禁终检（全部文件落盘并接线后复跑）

| 检查 | 命令 / 方法 | 结果 |
|------|------------|------|
| 总索引三角对账 | `python scripts/check-bundles-index.py` | ✅ rc=0：**9 域 / 64 组 / 718 束**，frontmatter、计数行、节标题、分组表、toctree 五面一致 |
| toctree 完整与可达 | `python scripts/check-toctrees.py` | ✅ rc=0：全部 `index.md` 引用有效、所有内容文档可达（接线前本束唯一红灯为 `log` 未落盘，写入后消除） |
| UTF-8 严格编码 | `python scripts/check-utf8.py` | ✅ rc=0：12961 个文件均为有效 UTF-8 |
| 双份 F 编号 | 正则 `^\|\s*F-(\d{3})\s*\|` 比对两文件 | ✅ 各 84，F-001~F-084 连续，集合相等 |
| F / V 引用越界 | 全束 16 篇正则扫描 | ✅ F 引用 84 个编号越界 0；V 引用 24 个编号（V-01~V-24）越界 0 |
| 本束相对链接 | 一次性解析扫描（16 文件 / 70 链接） | ✅ 断链 0、`file:///` 0、绝对路径 0、跨仓库越界链接 0 |
| frontmatter | 解析每个文件的 YAML 头 | ✅ `okf_version` **仅**在根 `index.md` 声明；12 篇内容文档均带 `type`；三个目录 index 沿用同组惯例不带 frontmatter |
| 章节体量 | 行数扫描 | ✅ 最长 `index.md` 156 行，无超 600 行文档 |
| 全局断链报告归属 | `check-section-anchors.py` 输出检索本束名 | ✅ 命中 **0** 处，未引入新断链 |
| 敏感信息 | 人工核对 | ✅ 无家目录绝对路径、无密钥、无真实聊天数据；示例路径均为占位符 |

### 三项全局门禁例外（明确非本束引入，不扩大变更范围）

1. **`check-asset-baseline.py` rc=1**：报「行尾归一失效，工作区归一后字节与 HEAD 残差 +245636」。核查：子模块工作树含多个并行会话 WIP（`wechatbridge/`、`workbuddy-wechat-chat-forward-skills/` 等未跟踪目录），属 Windows `core.autocrlf=true` 下字节归一的环境级假红；脚本自身要求「提交或 stash 后复跑」。其**规模数字校验部分已通过**（读取 `total_bundles: 718` 与 README / doc-index 一致），`.spec/ 泄漏守卫`通过。
2. **`check-section-anchors.py` rc=1**：全库约 6520 处既有断链 / MyST 锚点问题，报告 70 行；本束在报告中命中 0 次。
3. **`invoke gates.*` 不可用**：`ModuleNotFoundError: No module named 'invoke'`。按 `blog-article-to-okf-wiki` §7 不声称「gates 通过」，改以上述脚本直跑 + 手动等效验证替代。

## 4. 状态判定说明

按 `blog-article-to-okf-wiki` §6 步骤 6.4：`flagged` 只在「P0 出现 ❌ **且**失败项为核心声明」时启用。本次 4 项 ❌ 中
**V-21（iOS 完成态/提审）与 V-22（灵动岛入口）** 属博文主推功能，命中核心声明 → **`status: flagged`**。
对照同组 `wechatbridge`（18 项 14✅/4⚠️/0❌ → `stable`）与 `wechat-intelligence-hub`（22 项 14✅/8⚠️/0❌ → `stable`），
既**未滥用 flagged**，也**未把核心 ❌ 藏进 stable**。四处落地：根 index frontmatter、verification 顶部、根 index「阅读前必知」、concepts/00 读前须知。

## 5. 遗留与移交

- **计数来源**：会话早期读到总索引 714，随后并行会话推进至 717；本束落盘后以 `scan_tree` 地面真值确认为 **718**，故按 +1 增量接线，未沿用摘要快照、未重复累加。
- **C 阶段**：用户未要求 commit/push。当前主仓库 `M projects/awesome-okf-xs` + 未跟踪 spec 目录；子模块工作树含本束与并行会话 WIP。移交时按「① 子模块提交 bundle + 四级 index + README + doc/index → ② 主仓库提交 spec → ③ 更新 gitlink」，用 `git-commit-utf8.py` 显式列全文件，不 push。
- **并行会话隔离**：本束未修改 `wechatbridge/`、`workbuddy-wechat-chat-forward-skills/`，未代其接线；两束已在各自 index 做主题分工互链。
- **复核日期**：`stale_after: 2027-01-31`。若届时出现官方上架证据或灵动岛入版，应重判 V-21/V-22、调整 `status` 并在 `log.md` 追加记录。
