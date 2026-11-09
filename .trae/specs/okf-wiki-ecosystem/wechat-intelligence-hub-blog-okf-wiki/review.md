# V 阶段对抗审查记录（Spec Mode · review.md）

> 审查对象：`projects/awesome-okf-xs/doc/bundles/jishu/ai/products/wechat-intelligence-hub/`
> 审查时间：2026-11-06 · 链路：R→I→E→**V**→入库 · 结论：**通过，status: stable**

## 1. 四视角审查与采纳结果

| 视角 | 提出的质疑 | 采纳与修复 |
|------|-----------|-----------|
| 🔴 魔鬼代言人 | 「只读、AGPL」会不会被读成可以随便闭源集成？博文「不重签名」是否覆盖全项目？ | 新增 `concepts/05 §3.1` 许可证边界（AGPL-3.0-only、闭源/OEM/白标需商业授权、SaaS 触发网络开源义务）；`concepts/01 §4` 把「不重签名」收窄到 **Reader 核心**，并列出 macOS 候选接入助手的重启/重签名副作用（F-056）。根 index 与采用提示同步。 |
| 🟠 老板视角 | 博文一个版本号都没给，命令会不会过期？有没有实机验证？ | 补登记 `v0.9.2-preview.2`（F-045）；`concepts/04` 通篇标注「官方 README 逐字命令、本束未实机验证」，并写入复核提示（锁版本、命令漂移风险）。 |
| 🔵 未来视角 | 星标热度数字会不会很快失真？UI 名称会不会漂移？ | `stale_after: 2027-03-06`；三星标口径（1976 / 2000 / 2764）全部带时点；复核清单含 Star、preview→GA、macOS/Windows 首次接入进展。 |
| 🟣 证据强度 | 截图漂亮不等于功能验收；「5 天攒 2000 星」是不是硬伤？ | 建立四层信源距离地图（`concepts/00 §4`）与三种证据强度表（`concepts/02 §4`）；标题 hook 标「未独立核验」，并明确 **不得写成「仓库创建后 5 天」**（created_at 早于发文约 20 天）；全虚构 Demo 只证明链路、不证明真实数据可用。 |

## 2. G1~G4 质量门

| 门 | 判据 | 结果 |
|----|------|------|
| G1 事实 | F 编号事实无推断词、数字/版本/命令均有出处；双份登记集合一致 | ✅ 57 条（F-001~F-057），facts.md ↔ article-source.md 集合相等、连续无跳号 |
| G2 骨架/归属 | 操作可复现性两问；主线实体优先、查先例、单篇博文不新建分组 | ✅ 概念骨架无 examples/；归 `products/`，有 wigolo/agent-reach/creatorhub 先例 |
| G3 信源先行 | references 先于 concepts，各级 index 最后 | ✅ 生成顺序已在 log.md E 段登记 |
| G4 对抗审查 + 机械门禁 | 四视角 + 索引/toctree/UTF-8/链接/frontmatter | ✅ 见下表 |

## 3. 机械门禁终检

| 检查 | 命令 / 方法 | 结果 |
|------|------------|------|
| 总索引三角对账 | `python scripts/check-bundles-index.py` | ✅ rc=0：**9 域 / 64 组 / 715 束**，frontmatter、计数行、节标题、分组表、toctree 五面一致 |
| toctree 完整 | `python scripts/check-toctrees.py` | ✅ 本束入库当次 rc=0（4 个 index 指令块齐备、内容文档可达）；终检复跑 rc=1，4 处报错均为并行在途束，本束 0 处（见 §3.1） |
| UTF-8 严格编码 | `python scripts/check-utf8.py` | ✅ rc=0：12919 个文件均为有效 UTF-8 |
| 双份 F 编号 | 正则 `^\|\s*F-(\d{3})\s*\|` 比对两文件 | ✅ 各 57，F-001~F-057 连续，集合相等，差集双向为空 |
| 本束相对链接 | 自研一次性扫描（12 文件 / 42 链接） | ✅ 断链 0、`file:///` 0、绝对路径 0、锚点引用 0 |
| 全局断链报告归属 | `check-section-anchors.py` 输出中检索本束名 | ✅ 命中 **0** 处，未引入新断链 |
| frontmatter | 人工核对 | ✅ 根 `okf_version` 唯一，`type`/`title`/`description`/`tags`/`generated`/`verified`/`status`/`stale_after`/`sources`(3) 齐备；子文档仅用 `type` 等字段 |
| 敏感信息 | 人工核对 | ✅ 无家目录绝对路径、无密钥、无真实聊天数据；示例路径均为占位符 |

### 两项全局门禁例外（明确非本束引入，不扩大变更范围）

1. **`check-asset-baseline.py` rc=1**：报「行尾归一失效，工作区归一后字节与 HEAD 残差 +299202」。核查：子模块 `git status` 干净、无可 stash 的 WIP；属 Windows `core.autocrlf=true` 环境下字节归一的环境级假红。其**规模数字校验部分已通过**（读取 `total_bundles: 715` 与 README/doc-index 一致）。
2. **`check-section-anchors.py` rc=1**：全库 6557 处既有断链、413 处 MyST 跨文档锚点警告，全部为历史在途问题；本束在报告中命中 0 次。
3. **`check-toctrees.py` 终检复跑 rc=1**：本束入库当次为 rc=0；随后并行会话新建 `products/wechatbridge/`（缺 index.md）与 `products/workbuddy-wechat-chat-forward-skills/`（缺 index.md + 2 篇 references 未收录），共 4 处报错。均非本束，按「谁添加谁接线」不代修；`check-bundles-index.py` 仍通过（715 束，新目录因无 index.md 尚未计入树）。

## 4. 遗留与移交

- **计数来源**：开工时总索引为 714（并行会话已从 713 更新），本束入库后由地面真值脚本确认为 715；子模块 HEAD 提交 `12efe455` 的标题为「新增三束…（712→715）」，说明同期另有两束并行入库，绝对值以脚本为准，未重复累加。
- **C 阶段**：用户下达「提交」指令后按单一职责收尾——子模块单独提交本束 `log.md` 的 V/C 记录修正；主仓库提交 spec 四件并更新子模块 gitlink。并行在途改动（`wechatbridge/`、`wechatbridge-ios-relay/`、`ai-comic-drama-opc-transition/`、716→718 计数、3 个并行 spec 目录）均**未纳入**本次提交；未执行 push。
- **复核日期**：`stale_after: 2027-03-06`，若届时出现 ❌ 级反证或官方逐字证据，应调整 `status` 并在 `log.md` 登记。
