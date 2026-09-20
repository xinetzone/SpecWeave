---
status: "draft"
version: "1.0"
---

# 执行任务清单（tasks.md）

> 链路：`R（事实采集+核验）→ I（骨架/归属/拆分）→ E（信源先行生成）→ V（对抗审查+门禁）→ C（原子提交）`

## Task 1：R 阶段——信源获取与事实采集 ✅

- [x] 用浏览器子代理抓取微信公众号全文（`#js_content` innerText），规避 WebFetch 反爬
- [x] 记录标题/公众号/发布时间/字数（极客之家，2026-09-14 14:05，约 2635 字）
- [x] F-001~F-060 博文事实登记，逐条标注信源距离层级与 P 级
- [x] 作者观点（F-006/F-019/F-028/F-051/F-055~F-057）显式标注，不作为事实引用

## Task 2：R 阶段——P0 权威核验 ✅

- [x] 信源距离预判：本文为**第三方媒体产品介绍**，涉产品自宣数据（星标、Agent 数量、免费/账号口径）一律按 P0 处理
- [x] 三路并行核验：GitHub 仓库事实 / 官网与功能口径 / 移动端与第三方交叉核验
- [x] F-061~F-103 核验补充事实登记
- [x] 勘误七项（E-1~E-7）落表，其中 **E-1 域名拼写为博文硬错误**
- [x] 结论：核心声明（产品存在、功能、开源免费、安装命令）全部证实 → `status: stable`；E-2 属部分失真，须在正文以双口径呈现

## Task 3：I 阶段——骨架判定与归属 ✅

- [x] 操作可复现性两问 → 设 `examples/`（2 篇），并附加"官方文档逐字核验"限定
- [x] 归属判定 → `jishu/ai/orca-ade`（落既有分组，不新建分组）
- [x] 命名消歧 → `-ade` 后缀（规避 Homebrew plotly/orca 同名混淆，F-071）
- [x] 三层知识拆分 → concepts/ 三篇（事实层 / 机制层 / 生态适用层）

## Task 4：E 阶段——bundle 生成 ✅

- [x] Task 4.1 `references/article-source.md`（F 编号双份登记，信源先行）
- [x] Task 4.2 `references/verification.md`（P0 核验记录 + 勘误表）
- [x] Task 4.3 `references/index.md`
- [x] Task 4.4 `concepts/00-orca-overview.md`
- [x] Task 4.5 `concepts/01-fleet-worktree-mechanism.md`
- [x] Task 4.6 `concepts/02-ecosystem-and-fit.md`
- [x] Task 4.7 `concepts/index.md`
- [x] Task 4.8 `examples/00-install-and-first-session.md`
- [x] Task 4.9 `examples/01-parallel-worktrees-and-cli.md`
- [x] Task 4.10 `examples/index.md`
- [x] Task 4.11 `log.md`
- [x] Task 4.12 `index.md`（最后写，含主题关联与已知边界）

## Task 5：V 阶段——对抗审查与机械门禁 ✅

- [x] Task 5.1 四视角审查（事实溯源 / 结构规范 / 读者可用性 / 时效边界）
- [x] Task 5.2 双份 F 编号一致性正则比对：facts.md ↔ article-source.md 均 F-001~F-103 连续 103 条，集合相等
- [x] Task 5.3 三级 toctree 完整性（12 个文档逐一可达，指令行不计入条目数）；check-toctrees.py 本束零问题
- [x] Task 5.4 相对链接全可达（39 条）、`file:///` 零出现；**修复 concepts/02 三条跨束链接少一层的层级错误**
- [x] Task 5.5 UTF-8 严格 roundtrip 校验（check-utf8.py：10434 文件通过）
- [x] Task 5.6 敏感信息零残留（家目录绝对路径）
- [x] Task 5.7 frontmatter 齐备（含 sources 双信源）；**补齐 verification.md 缺失的 `verified` 字段**
- [x] Task 5.8 勘误落实核对（E-1~E-7 在正文呈现正确值；`onnorca.dev` 仅存于勘误语境）

## Task 6：V 阶段——索引接入 ✅

- [x] Task 6.1 `jishu/ai/index.md`：导航表加行 + toctree 追加
- [x] Task 6.2 `bundles/index.md`：total_bundles 556→557、jishu 节标题与 mermaid 节点 423→424、ai 分组束数 204→205（脚本对账通过：9 域/59 组/557 束五面一致）
- [x] Task 6.3 质量门：**直接运行仓库 stdlib 脚本**（check-bundles-index.py / check-utf8.py / check-toctrees.py），未经 invoke 通道，故不声称"`invoke gates` 通过"；结果与"他会话 WIP 未代为修改"的说明已记入 log.md

## Task 7：C 阶段——原子提交

- [x] Task 7.1 子模块 `projects/awesome-okf-xs` 内提交 bundle 12 文件 —— `7af4add5 feat(bundles): 新增 Orca ADE 多 Agent 桌面工作台知识包（极客之家博文核验转化）`
- [x] Task 7.2 分组/总索引同步更新（`jishu/ai/index.md` 导航行 + toctree；`bundles/index.md` 计数四面）——**注：该两个文件被并发会话提交 `9a53c2c5` 一并纳入**（非本会话提交，内容与预期一致，已在 bundle log.md 登记）
- [x] Task 7.3 主仓库提交 spec 四文件（spec.md + facts.md + tasks.md + review.md）并携带子模块指针更新
- [x] 显式列出全部文件路径传 `git-commit-utf8.py`（未传目录参数）；用户未要求，**未 push**