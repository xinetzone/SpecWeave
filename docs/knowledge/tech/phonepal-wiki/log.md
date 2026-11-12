# 变更日志

## v1.0.0 — 2026-11-12

**新增**

- 知识包首版：11 篇概念、3 个示例、3 份信源/核验文档，根索引与本日志。
- 事实基础：82 条编号事实（F-001 ~ F-082），全部绑定 commit `580fdf750f946a6e411c3f54a86443c66aa46652`，含脚本计数与源码行号。
- 架构洞察：4 条四元组（双模型分工、模型外闸门、纯 JVM 内核、宽容解析 + 显式反馈），另有「文件即契约」作为第四条洞察的展开。

**事实来源**

- 源码：`git@github.com:aduoge/xiaoman.git`（目录名 `xiaoman`，产品名 PhonePal），MIT。
- 随仓库文档：`README.md`、`docs/ARCHITECTURE.md`、`docs/skills.md`、`cli/README.md`，仅作交叉印证。
- 计数：`.temp/xiaoman-count/count_facts.py`（一次性脚本，不随包分发）。

**验证**

- V 阶段：Grep 级 API 核验、计数断言复核、链接与 frontmatter 检查；记录见 [references/02-adversarial-review.md](references/02-adversarial-review.md)。
- 未执行：真机运行、Gradle 构建、模型 API 调用（无设备/无 Key）；正文中涉及运行行为的描述均来自源码与仓库文档，已在对抗审查中标注边界。

**已知边界**

- 信源无 release tag，只有两个提交；上游更新后需重新固定 commit。
- `external/` 不随主仓分发；正文引用一律为仓库相对路径 + commit hash。
- 无障碍与截图行为随 Android 版本变化，`07-hands-accessibility.md` 中「Android 11–13 黑帧」为源码注释记载的口径。
