# Tasks

> 执行链路遵循 `source-code-to-okf-wiki` 的 R→I→E→V→C 五阶段 + `seven-concepts-cmd` 质量门编排。所有产出物写入 `projects/awesome-okf-xs/doc/bundles/`（子模块内），规划文档与原始文本存放 `.trae/specs/jianshu-blogs-to-okf-wiki/`。

## 阶段 0/1：信源采集与事实登记（R 阶段）

- [x] Task 1: 信源采集——抓取三个简书连载全部文章正文，保存原始文本快照
  - [x] SubTask 1.1: 抓取 nb/46194813（matplotlib & pillow & networkx，14 篇）全部文章正文 → `raw/notebook1-matplotlib-pillow-networkx/`（14/14，全成功）
  - [x] SubTask 1.2: 抓取 nb/40234132（开源的世界，10 篇）全部文章正文 → `raw/notebook2-opensource/`（10/10，1 篇部分抓取已标注：9e81e3ca89a8）
  - [x] SubTask 1.3: 抓取 nb/47487870（无人驾驶，10 篇）全部文章正文 → `raw/notebook3-autonomous/`（10/10，全成功）
- [x] Task 2: R 阶段事实采集——通读原始文本，登记编号事实（F-xxx）到 `facts.md`，每条标注来源 URL 与内容时点（2020 年前后），零推测
  - [x] SubTask 2.1: Notebook 1 事实（matplotlib/networkx/pillow 的 API、示例、参数）→ F-101~F-200（100 条）
  - [x] SubTask 2.2: Notebook 2 事实（Git/GitHub/开源实践）→ F-201~F-265（65 条）
  - [x] SubTask 2.3: Notebook 3 事实（Autoware/ROS2/DDS/WSL2）→ F-301~F-363（63 条）
  - [x] 质量门 G1：事实清单无推断性表述（"用于/目的是"等推断词为文章原文陈述，非登记员推断），每条指向来源文章

## 阶段 2：洞察与知识地图（I 阶段）

- [x] Task 3: 洞察与束结构设计
  - [x] SubTask 3.1: 提炼各 notebook 的核心洞察（陈述/证据/反常识/行动四元组）→ `insights.md`
  - [x] SubTask 3.2: 确定束结构与放置：pydata 下 networkx/pillow 新增 + matplotlib 扩展；dev 分组（git/github/opensource）；autonomous 分组（autoware/ros2/dds/ecosystem）
  - [x] SubTask 3.3: 确定每束 concepts/examples/references 文档清单与学习路径
  - [x] 质量门 G2：洞察四元组完整、知识地图有学习路径

## 阶段 3：批量生成（E 阶段）

- [x] Task 4: Notebook 1 生成——pydata 组
  - [x] SubTask 4.1: 扩展 `jishu/data/pydata/matplotlib/`（补齐事件处理、patches/path、分形示例概念，更新其 index/log）
  - [x] SubTask 4.2: 新增 `jishu/data/pydata/networkx/`（节点与边、路径绘制、DAG 画神经网络、布局样式）
  - [x] SubTask 4.3: 新增 `jishu/data/pydata/pillow/`（图像基础与处理、缩放合成、ImageDraw 绘制、图像特效）
  - [x] SubTask 4.4: 更新 `jishu/data/pydata/index.md`（表与 toctree）
- [x] Task 5: Notebook 2 生成——dev 分组（新）
  - [x] SubTask 5.1: 新增 `jishu/dev/index.md`（组 index + toctree）
  - [x] SubTask 5.2: 新增 `jishu/dev/git/`（Git 学习笔记、团队协作、下载加速）
  - [x] SubTask 5.3: 新增 `jishu/dev/github/`（创建 Gist、GitHub Actions 手册）
  - [x] SubTask 5.4: 新增 `jishu/dev/opensource/`（开源项目指南、开启开源项目、README 模板、无版权图库、程序员网站）
- [x] Task 6: Notebook 3 生成——autonomous 分组（新）
  - [x] SubTask 6.1: 新增 `jishu/autonomous/index.md`（组 index + toctree）
  - [x] SubTask 6.2: 新增 `jishu/autonomous/autoware/`（Autoware.Auto 安装与基础：WSL2/Ubuntu）
  - [x] SubTask 6.3: 新增 `jishu/autonomous/ros2/`（ROS2 概念）
  - [x] SubTask 6.4: 新增 `jishu/autonomous/dds/`（数据分发服务 DDS）
  - [x] SubTask 6.5: 新增 `jishu/autonomous/ecosystem/`（无人驾驶数据集、汽车术语、Autonomous 资源、WSL2 GPU 深度学习环境）
  - [x] 质量门 G3：信源先行（references/ 先于 concepts/）、每批 ≤7 文件、index 最后写

## 阶段 4：索引对账与独立验证（V 阶段）

- [x] Task 7: 索引同步与计数对账
  - [x] SubTask 7.1: 更新 `jishu/index.md`（新增 dev、autonomous 分组行 + toctree）
  - [x] SubTask 7.2: 更新 `doc/bundles/index.md` 总索引（分组表/域节/计数行/toctree 五面）
  - [x] 质量门：`check-bundles-index.py` 通过——9 域 / 52 组 / 416 束 frontmatter、计数行、节标题、分组表、toctree 五面一致（并行会话已推进计数，己方 dev/autonomous/data 行与 toctree 条目均保留）
- [x] Task 8: 独立验证（V 阶段）
  - [x] SubTask 8.1: `invoke gates.all`——utf8 通过（8144 文件全有效）；bundles 计数通过；toctrees 己方文件零错误（68 处错误全部为并行会话 WIP：ai-agent-skills/ai-app-survival/wigolo、sheke/marketing，非本方欠债）
  - [x] SubTask 8.2: `sphinx-build` 定向 dummy 构建成功（213 文件 pydata/dev/autonomous 全量解析），己方路径零警告零错误（25 条警告全部为并行会话文件）；frontmatter YAML 解析无错误
  - [x] SubTask 8.3: 计数断言验证——dev=33、autonomous=36、networkx=13、pillow=16 .md 文件经 Glob 独立复核一致
  - [x] SubTask 8.4: 过时内容现状校正抽查——autonomous 四束（autoware/ros2/dds/ecosystem）与 dev 三束、networkx（2.x 时代）、pillow（7.x 时代）均带 `stale_after: 2026-12-31` + 「历史教程类/基于 2020 年前后」声明 + 「现状」小节标注过时 API
  - [x] 质量门 G4：无虚构 API（全部溯源编号事实 F-xxx）、链接无断裂（sphinx 零警告）、frontmatter 完整、计数一致

## 阶段 5：原子提交（C 阶段）

- [x] Task 9: 原子提交与交付
  - [x] SubTask 9.1: 检查 `.git/MERGE_HEAD` 与并行会话暂存区——无 MERGE_HEAD；`doc/bundles/index.md` 剩余未提交差异为并行会话 marketing 描述改动，己方索引行已由并行会话提交（39b5465a）含入，故不暂存
  - [x] SubTask 9.2: 显式 add 本任务文件（add 与 commit 分两次）；add 后 `git diff --cached --name-only` 核对暂存集 109 文件全部为本方路径（autonomous 36 + pydata 1 + matplotlib 10 + networkx 13 + pillow 16 + dev 33），零混入并行会话文件
  - [x] SubTask 9.3: Conventional Commits 中文主体提交——`34af4a62`（docs(bundles): 简书三连载转 OKF Wiki 教程，+6778/-9）
  - [x] 质量门 G5：提交单一职责、暂存集纯净（109 文件全部为本任务束文件）

# Task Dependencies

- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 2]
- [Task 4] depends on [Task 3]；[Task 5] depends on [Task 3]；[Task 6] depends on [Task 3]
- [Task 4]/[Task 5]/[Task 6] 相互独立，可并行
- [Task 7] depends on [Task 4]/[Task 5]/[Task 6]
- [Task 8] depends on [Task 7]
- [Task 9] depends on [Task 8]
