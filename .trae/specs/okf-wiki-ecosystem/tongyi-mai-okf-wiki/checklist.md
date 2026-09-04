# Checklist

> 验证时间：2026-08-29；验证方式：source-code-to-okf-wiki 五阶段 + `invoke gates.all` + 独立 Sub-Agent Grep 验证（详见 verification.md）

## R 阶段（G1 事实门）
- [x] facts-mobile-world.md / facts-mai-ui.md / facts-mobilepa-bench.md / facts-websites.md 全部存在且事实编号 F-xxx 连续唯一（80/54/32/40 条）
- [x] 每条事实标注源码文件路径，无"用于/目的是/设计为"等推断词
- [x] 核心模块全覆盖：MobileWorld（agents/core/runtime/tasks/cli/eval_server）、MAI-UI（6 个 src 文件 + evaluation/cookbook）、MobilePA-Bench（README/网站）、Qwen-UI-Agent 网站、MAI-UI-blog

## I 阶段（G2 洞察门）
- [x] insights.md 含 3 个 bundle 各 3-5 个洞察四元组（陈述/证据/反常识/行动）——共 15 个
- [x] 知识地图明确各概念文档覆盖的 F-xxx 编号与学习路径依赖

## E 阶段（G3 生成门）
- [x] 3 个 bundle（mai-ui 16 文件 / mobile-world 18 文件 / mobilepa-bench 11 文件）均已生成，目录结构含 index.md、log.md、concepts/、references/（examples/ 视源码示例而定：mai-ui 2 篇、mobile-world 3 篇、mobilepa-bench 无并记录理由）
- [x] references/ 信源文件先于 concepts/ 生成，frontmatter sources 字段全部指向存在的信源文件
- [x] 每批生成文件 ≤7
- [x] 根 index.md 含 okf_version frontmatter；子目录 index.md 无 frontmatter 且均含 `{toctree}` 块收录本目录全部内容文档
- [x] 交叉链接使用 `/` 开头 bundle-relative 路径，无 `../`（跨束互链 `../<bundle>/index.md` 为既有约定）
- [x] 文档为中文，代码块标注语言，API 调用与 facts 一致

## V 阶段（G4 验证门）
- [x] 文档中类名/方法名经 Grep 源码验证存在（33 项符号矩阵全部对齐），签名一致
- [x] MobilePA-Bench/Qwen-UI-Agent 网站文档明示"非实现代码仓"性质，无虚构实现细节
- [x] `invoke gates.all`（UTF-8 + toctrees）在 projects/awesome-okf-xs 零失败（5806 文件 UTF-8 有效、toctree 全部可达）
- [x] verification.md 验证报告已产出，17 处计数偏差等问题全部修复复检

## 索引同步
- [x] bundles/ai/ai-agent/index.md 新增 3 束条目（31→34）+ toctree 3 行 + 统计行更新
- [x] bundles/ai/index.md 与 bundles/index.md 计数更新（total_bundles 283→286、ai 域 110→113），说明文字同步
- [x] qwen-ui-agent 束与 3 个新束互链已建立

## C 阶段（G5 提交门）
- [x] awesome-okf-xs 子模块原子提交完成（d67de37b，49 文件 +4754/-7），提交信息 Conventional Commits 中文主体
- [x] SpecWeave 主仓库子模块指针提交完成（ba6bbaab9，10 文件，预提交钩子全过）
- [x] 两仓库工作区干净（push 听用户指令）
