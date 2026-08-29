# Checklist

## R 阶段（G1 事实门）
- [ ] facts-mobile-world.md / facts-mai-ui.md / facts-mobilepa-bench.md / facts-websites.md 全部存在且事实编号 F-xxx 连续唯一
- [ ] 每条事实标注源码文件路径，无"用于/目的是/设计为"等推断词
- [ ] 核心模块全覆盖：MobileWorld（agents/core/runtime/tasks/cli/eval_server）、MAI-UI（6 个 src 文件 + evaluation/cookbook）、MobilePA-Bench（README/网站）、Qwen-UI-Agent 网站、MAI-UI-blog

## I 阶段（G2 洞察门）
- [ ] insights.md 含 3 个 bundle 各 3-5 个洞察四元组（陈述/证据/反常识/行动）
- [ ] 知识地图明确各概念文档覆盖的 F-xxx 编号与学习路径依赖

## E 阶段（G3 生成门）
- [ ] 3 个 bundle（mai-ui/mobile-world/mobilepa-bench）均已生成，目录结构含 index.md、log.md、concepts/、references/（examples/ 视源码示例而定）
- [ ] references/ 信源文件先于 concepts/ 生成，frontmatter sources 字段全部指向存在的信源文件
- [ ] 每批生成文件 ≤7
- [ ] 根 index.md 含 okf_version frontmatter；子目录 index.md 无 frontmatter 且均含 `{toctree}` 块收录本目录全部内容文档
- [ ] 交叉链接使用 `/` 开头 bundle-relative 路径，无 `../`
- [ ] 文档为中文，代码块标注语言，API 调用与 facts 一致

## V 阶段（G4 验证门）
- [ ] 文档中每个类名/方法名经 Grep 源码验证存在（重点防虚构 API），签名一致
- [ ] MobilePA-Bench/Qwen-UI-Agent 网站文档明示"非实现代码仓"性质，无虚构实现细节
- [ ] `invoke gates.all`（UTF-8 + toctrees）在 projects/awesome-okf-xs 零失败
- [ ] verification.md 验证报告已产出，问题全部修复复检

## 索引同步
- [ ] bundles/ai/ai-agent/index.md 新增 3 束条目（31→34）
- [ ] bundles/ai/index.md 与 bundles/index.md 计数更新（total_bundles 283→286），Mermaid/说明文字同步
- [ ] qwen-ui-agent 束与 3 个新束互链已建立

## C 阶段（G5 提交门）
- [ ] awesome-okf-xs 子模块原子提交完成，预提交钩子全过，提交信息 Conventional Commits 中文主体
- [ ] SpecWeave 主仓库子模块指针提交完成
- [ ] 两仓库工作区干净（push 听用户指令）
