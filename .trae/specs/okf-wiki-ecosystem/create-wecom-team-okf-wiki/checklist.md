# Checklist

## G0 信源稳定性

- [x] 三个子模块 `git status --porcelain` 均为空，工作树已恢复（非 `git show` 兜底模式）
- [x] HEAD 分别为 `1d48b6c9ecd1b4897c4bf728d564bfda1d62fbde`、`cae8a5befac67d96bfe573b1675c5faab474758e`、`6bcb59a9a636c566f4c6ea5268b228e3def1611a`
- [x] `git ls-tree -r HEAD --name-only` 计数为 600 / 197 / 19
- [x] 三束 `references/sources.md` 均登记完整 commit、远程 URL、MIT 许可证与取证命令
- [x] vendor 源码零改动（`git -C <sub> status --porcelain` 无内容改动）；`vendor/VERSION.md` 与 `vendor/WecomTeam/README.md` 未修改

## R 阶段（G1 事实门）

- [x] wecom-cli 事实 ≥80 条，编号 `F-0xx` 连续无跳号
- [x] wecom-unified 事实 ≥50 条，编号连续
- [x] wecom-aibot-python-sdk 事实 ≥45 条，编号连续
- [x] 每条事实含「陈述 + 路径:行号 + 取证命令」三要素
- [x] 事实清单中不存在「为了/目的是/设计为/用于解决」等因果推断表述
- [x] `wecom-cli` 15 个 skills 目录与「14 个业务 Skill」口径差异已并置登记
- [x] `aibot` 的 `__version__ = "1.0.0"` 与 pyproject `1.0.1` 差异已并置登记

## I 阶段（G2 洞察门）

- [x] 每束 ≥4 条四元组洞察（陈述 + 证据 F 编号 + 反常识 + 行动）
- [x] 每条洞察至少引用 2 条事实编号
- [x] 每束 `concepts/index.md` 给出 `00 → NN` 学习路径与前置依赖

## E 阶段（G3 模式门 / 结构合规）

- [x] 3 束目录齐全：`concepts/`、`examples/`、`references/`、`index.md`、`log.md`
- [x] 生成顺序为 references → concepts/examples → 各级 index；单批写入 ≤7 文件
- [x] 子目录 `index.md` 无 frontmatter，且含 `{toctree}` 块
- [x] 每个非保留 `.md` 具备 `type/title/description/tags/generated/verified/status/stale_after/sources` 九字段
- [x] 所有 `sources` 指向本束已存在的 `references/` 文件
- [x] 束规模达标：wecom-cli 8+3、wecom-unified 6+3、aibot 5+3（概念+示例）
- [x] 所有示例统一标注「未在本机实跑」，不伪装为可复现实验

## 索引与计数

- [x] `tencent/index.md` 导航新增 3 行、toctree 新增 3 项，束数 19 → 22
- [x] `tencent/index.md` 的概念/示例/信源/事实计数等于实际文件与 F 编号总数
- [x] `ecosystems/index.md`、`jishu/ai/index.md`、`jishu/index.md` 计数同步
- [x] `doc/bundles/index.md` 的 `total_bundles` 等于门禁实测值（本批新增 3 束后为 727，其中 2 束来自并行会话新增），jishu 行 = 533 束，分组仍 64
- [x] `README.md` 徽章、总览表、合计行与 `doc/index.md` 规模段落与门禁实测值一致（727 束）
- [x] 与 3 个既有企业微信束建立双向互链

## V 阶段（G4 行动门 / 独立验证）

- [x] 文档中出现的每个类名/方法名/常量/命令名在 vendor 源码 Grep 命中，零虚构 API
- [x] 所有「N 个 / N 篇 / N 行 / N 个 crate」数量陈述经独立计数一致
- [x] 束内链接零断裂（相对路径或 `/` 开头 bundle-relative 路径）
- [x] `python scripts/check-toctrees.py` rc=0
- [x] `python scripts/check-bundles-index.py` rc=0
- [x] `python scripts/check-asset-baseline.py` rc=0
- [x] `check-section-anchors.py`：全库既有 6596+ 处锚点失败（样例均非本批三束），本批三束零新增；其余四项门禁 rc=0
- [x] 未修改既有 `wecom-5-0-10-release` / `wecom-5-0-12-release` / `wecom-topic-scenarios` 正文（仅新增链接行）

## C 阶段（G5 沉淀与交付）

- [x] 三束 `log.md` 记录 V 阶段缺陷与修复过程
- [x] 沉淀「运行时 → 路由层 → 协议层」三层读法模式（3-7 步）
- [x] 沉淀 ≥3 条反模式（如：把 Skill 文档当 API 权威、凭 README 版本号推断行为、混淆 CLI 与 SDK 的认证模型）
- [x] 未执行 `git add` / `commit` / `push`
- [x] 交付清单给出文件数、事实数、洞察数、门禁结果