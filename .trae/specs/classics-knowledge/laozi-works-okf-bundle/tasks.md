# Tasks

- [x] Task 1: 建立 bundle 骨架与索引
  - [x] SubTask 1.1: 创建 `think/laozi/laozi-works/` 目录及子目录 `concepts/`、`text/`、`commentaries/`、`references/`
  - [x] SubTask 1.2: 生成根 `index.md`（含 `okf_version: "0.2"`、toctree 引用全部子目录 index 与 facts/insights/patterns/log）
  - [x] SubTask 1.3: 生成 `log.md`（Creation 条目，ISO 8601 倒序）

- [x] Task 2: 采集权威信源与事实（R 阶段）
  - [x] SubTask 2.1: 检索并核实出土文献整理本信源（高明《帛书老子校注》、荆门市博物馆《郭店楚墓竹简》、北京大学《北京大学藏西汉竹书（贰）》等）
  - [x] SubTask 2.2: 检索并核实历代注本信源（王弼、河上公、严遵、苏辙）
  - [x] SubTask 2.3: 检索并核实现代学者注本信源（陈鼓应、楼宇烈、李零）
  - [x] SubTask 2.4: 生成 `references/index.md` 及各分类信源登记文档，每条含可核查 `resource`（ISBN/机构 URL）
  - [x] SubTask 2.5: 生成 `facts.md`（零推测事实清单，通过 G1 质量门）

- [x] Task 3: 编写核心概念文档（concepts/）
  - [x] SubTask 3.1: 生成 `concepts/index.md`
  - [x] SubTask 3.2: 《道德经》名实与全书概览（书名沿革、篇章结构、德经/道经篇序）
  - [x] SubTask 3.3: 出土文献三大系统（郭店楚简、马王堆帛书、北大汉简）成书与价值
  - [x] SubTask 3.4: 核心哲学概念（道、德、无为、自然）——出土文献视角
  - [x] SubTask 3.5: 相关道家著作概览（《文子》《关尹子》《阴符经》成书、真伪、与老子思想关系）

- [x] Task 4: 编写出土文献原文（text/）
  - [x] SubTask 4.1: 生成 `text/index.md`
  - [x] SubTask 4.2: 帛书甲本原文（释文溯源至高明《帛书老子校注》，标注残毁处）
  - [x] SubTask 4.3: 帛书乙本原文（较完整底本，标注与甲本差异）
  - [x] SubTask 4.4: 郭店楚简本现存部分原文（显式说明残简范围）
  - [x] SubTask 4.5: 北大汉简本原文（溯源至北大整理本）
  - [x] SubTask 4.6: 关键异文对照（如「大器晚成/免成」等，链接至解读）

- [x] Task 5: 编写权威解读（commentaries/）
  - [x] SubTask 5.1: 生成 `commentaries/index.md`
  - [x] SubTask 5.2: 出土文献校注解读（高明等立场）
  - [x] SubTask 5.3: 历代注本解读（王弼、河上公、严遵、苏辙立场对照）
  - [x] SubTask 5.4: 现代学者注本解读（陈鼓应、楼宇烈、李零立场对照）
  - [x] SubTask 5.5: 争议与不确定性显式化（如「无」与「道」的哲学诠释分歧）

- [x] Task 6: 洞察与模式萃取（I/E 阶段）
  - [x] SubTask 6.1: 生成 `insights.md`（至少 3 条含四元组：现象+根因+影响+建议，通过 G2）
  - [x] SubTask 6.2: 生成 `patterns.md`（至少 2 个可复用模式：触发场景+核心步骤+反模式+迁移验证，通过 G3）

- [x] Task 7: 更新父级导航（think/laozi/index.md）
  - [x] SubTask 7.1: 在知识包列表表追加 laozi-works 行
  - [x] SubTask 7.2: 在 toctree 追加 `laozi-works/index`

- [x] Task 8: 对抗审查（V 阶段）与质量门验证
  - [x] SubTask 8.1: 对有争议断代/释文/诠释执行对抗审查，记录于「争议与不确定性」小节
  - [x] SubTask 8.2: 运行 `invoke gates.toctrees` 验证（laozi 相关零报错；其余报错来自并行任务的 bundle）
  - [x] SubTask 8.3: frontmatter YAML 可解析性与 UTF-8 编码验证（内容文件 20/20 通过）
  - [x] SubTask 8.4: 文件完整性验证（25 文件全部落盘，零空文件）

- [x] Task 9: 原子提交（C 阶段）
  - [x] SubTask 9.1: 核对 `git status`/`git diff` 实际变更
  - [x] SubTask 9.2: 按 Conventional Commits 规范原子提交（单一职责）

# Task Dependencies

- Task 2 依赖 Task 1（先建骨架再采集信源）
- Task 3/4/5 依赖 Task 2（事实与信源先于正文编写）
- Task 6 依赖 Task 3/4/5（洞察与模式来自概念/原文/解读）
- Task 7 依赖 Task 1（索引存在后方可引用于父级导航）
- Task 8 依赖 Task 3/4/5/6/7（内容齐全后验证）
- Task 9 依赖 Task 8（质量门通过后提交）
- Task 3、Task 4、Task 5 相互独立，可并行执行