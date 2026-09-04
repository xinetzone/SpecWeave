# Checklist — create-ai-security-okf-wiki（交付核验版 2026-09-02）

> 核验证据：gates 三门运行记录 + 定向 sphinx dummy 构建 + V 阶段审查报告 review.md + 提交 72467fe3。
> 注：树真值经 3 轮并行会话漂移收敛，最终 413 束/52 组/ai 128（非 spec 预估的 401/47）。

## R 阶段（G1）
- [x] `facts-cl4r1t4s.md`（70 条）/ `facts-l1b3rt4s.md`（55 条）/ `facts-obliteratus.md`（66 条）齐备，每条带 F 编号与来源，无因果推断词
- [x] L1B3RT4S 全部事实注明经 `git show HEAD:`（64960b7）读取，未触碰其工作树（子代理结束后复验 git status：44 文件仍全 D）
- [x] 计数与实际一致：CL4R1T4S 26 目录/73 文件、L1B3RT4S 34 厂商 .mkd（44 文件总数）、OBLITERATUS 模块清单（15 核心模块全部核验）

## I 阶段（G2）
- [x] `insights.md` 7 条洞察（≥3），每条含陈述+证据（F 编号）+反常识+行动四元组

## E 阶段（G3 详实性与可靠性）
- [x] `jishu/ai/ai-security/index.md` 分组索引含导航表与 toctree（三束）
- [x] cl4r1t4s 束：index + 5 concepts + 1 example + 1 references（篇均 4032~7329 字符）
- [x] l1b3rt4s 束：index + 4 concepts + 1 example + 1 references（concepts 4026~6166 字符）
- [x] obliteratus 束：index + 7 concepts + 2 examples + 1 references（concepts 4959~7487 字符）
- [x] 每篇 concepts 含表格或 Mermaid 图；OBLITERATUS 束 CLI 命令/Python API经 cli.py/abliterate.py 等源码 Grep 核验
- [x] 每束根 index.md 含 `okf_version: "0.2"`、toctree 全量引用、信任声明与源码位置
- [x] 所有新文档 frontmatter 含非空 `type`，派生文档带 `sources` 溯源字段
- [x] 文件名全部 kebab-case 纯英文，正文中文

## 内容伦理边界（V 专项）
- [x] 全文无逐字可操作越狱载荷、无完整系统提示词正文复制（l1b3rt4s 两轮 grep 载荷标记零命中；cl4r1t4s 仅 ≤2 行脱敏结构引用）
- [x] 无绕过安全机制的 step-by-step 指南（OBLITERATUS 用法均为上游公开研究工具文档内容）
- [x] 用途限定声明齐备（分组 index 显著位置 + 各束 index + ethics/responsible-disclosure 专篇），上游伦理/免责要点保留
- [x] 学术术语带出处引用（Arditi arXiv:2406.11717、JailbreakBench、HarmBench、COSMIC arXiv:2506.00085、RDO ICML 2025 等）

## 索引与计数
- [x] `jishu/ai/index.md` 分组导航 + toctree 已注册 ai-security（含首轮 toctree 编辑被并行会话覆盖后补登）
- [x] `jishu/index.md` ai 行 128（树真值）、关键词含 ai-security、正文 16 组、gui 组注册
- [x] `bundles/index.md` 五面更新且数字全部由 gates 重算（413 束/52 组/9 域；jishu 313 束·16 组；ai 128）
- [x] toctree 写法统一（目录条目 `/index`、束内条目显式 `.md`）

## V 阶段
- [x] 37 处关键论断逐条对照事实清单/源文件核验（超出每束 ≥10 要求），11 处问题已修正
- [x] `yaml.safe_load` 27/27 解析通过（零英文双引号嵌套）
- [x] 4 视角对抗审查 11 条实质意见全部采纳修正（10 文件 13 处），报告见 review.md

## C 阶段
- [x] `gates.utf8` 全绿（8081 文件）；`gates.bundles`/`gates.toctrees` 己方面零问题——残留项仅为他会话在建目录（sheke/finance、sheke/marketing 0 束无组索引，无法代注册；依 bd47eebb/push-gate 先例留待其补齐）；构建验证采用项目规范 §14.2 定向 `sphinx-build -b dummy`（30 文件成功 0 error 0 己方 warning；全量 build 因并行 WIP 污染与时长改用此规范途径）
- [x] add 与 commit 分离执行，暂存集精确 30 文件，暂存 blob 关键行核验通过
- [x] Conventional Commits 中文提交信息（72467fe3），未推送（待用户指令/全树门绿）
