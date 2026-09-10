# 网易有道开源生态 OKF Wiki 教程 - 验收检查清单

## G0 信源稳定性门

- [x] 6 个仓库已迁移为 `vendor/netease-youdao/<repo>` git 子模块（gitlink mode 160000）
- [x] 子模块固定到 release tag 或 commit hash（非 main/master 浮动分支），EmotiVoice/QAnything pin 勘察 HEAD commit（分别超前 v0.3/v2.0.0 共 17/69 commits，决策见 migration-baseline.md），LobsterAI 恰为 tag 2026.9.4，其余固定 commit hash
- [x] `git submodule status` 6 个子模块无前缀 `-`/`+`，检出与迁移基线一致
- [x] vendor/AGENTS.md 路由表、vendor/README.md 依赖清单、vendor/VERSION.md 版本记录已更新（含 tag/hash/许可证/日期）
- [x] `check-vendor.py --deep` 合规检测通过（netease-youdao 6 子模块全部 PASS；整体 rc=1 仅因迁移前已存在的 podman-compose/py/toolbox 未初始化）
- [x] 旧临时克隆目录已删除，且删除前 GATE-SPS 扫描 rc=0（零引用）
- [x] 既有 vendor 子模块（flexloop、ark-cli、awesome-okf、knowledge-catalog 等）未受影响（11 个既有子模块 hash 逐一比对与基线一致）
- [x] 迁移基线（HEAD commit 对照表）已记录在 spec 目录备查

## R 阶段（G1）

- [x] 6 个仓库事实清单完整，每条事实编号 F-xxx 且指向 vendor 稳定路径
- [x] 事实表述无"用于/目的是/设计为"等推断词
- [x] 各仓库核心模块全覆盖（对照其 README/AGENTS.md/目录结构）

## I 阶段（G2）

- [x] 每仓库 3-5 个洞察四元组完整（陈述+证据 F-xxx+反常识+行动）
- [x] 知识地图含 concepts/ 文档编号清单与入门→高级学习路径

## E 阶段（G3）

- [x] `doc/bundles/jishu/ai/netease-youdao/` 分组 index.md 含 okf_version frontmatter 与 6 束导航
- [x] 6 个 bundle 目录结构合规（index.md/log.md/concepts/references，有示例的含 examples）
- [x] references/ 信源文件先于 concepts/examples 生成
- [x] 每批生成 ≤7 文件；各级 index.md 最后书写
- [x] 非保留 .md 文件 frontmatter 九字段完整（type/title/description/tags/generated/verified/status/stale_after/sources），sources 指向存在文件
- [x] 子目录 index.md 无 frontmatter；交叉链接全部 `/` 开头 bundle-relative 路径

## V 阶段（G4）

- [x] 文档引用的每个类名/方法名/函数签名经 Grep 在 vendor 源码中验证存在，零虚构 API
- [x] 所有"X个/Y份/Z处"数量陈述经 Glob/Grep 独立计数比对一致
- [x] 交叉链接无断裂；`check-toctrees.py` 导航链完整无"未收录(不可达)"
- [x] 验证报告输出且全部问题已修复

## C 阶段（G5）

- [x] 工作流回顾完成，新反模式/改进点已回写 source-code-to-okf-wiki 模式文档（如有）
- [x] 全部变更按 Conventional Commits 原子提交（中文主体、单一职责）
