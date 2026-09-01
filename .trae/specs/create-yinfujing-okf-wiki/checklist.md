# Checklist — 《黄帝阴符经》OKF 知识包

## 内容正确性
- [x] 原文全录（四百余字三章本）与至少 2 个独立权威信源逐字一致（V 阶段实抓 R7 底本 + R6/R1/R8/R9 对校，17 处抽查零偏差）
- [x] 三百字本差异已登记并说明（F1–F7 字数谱系、01-text-versions 谱系表、03 结构注记：疏本经文止于"我以时物文理哲"，尾附段自"自然之道静"起）
- [x] 托名传说（黄帝著）与学术成书年代学说明确区分，未混淆（02 按 P2 三层框架，托名层显式标注"不作史实"）
- [x] 成书年代各学说均标注依据文献（F21–F29：邵雍/程颐/梁启超/寇谦之说/余嘉锡/黄庭坚/朱熹/王明定年 531–580/李筌伪撰反证）
- [x] 核心句解读均呈现 ≥2 注家立场且出处可溯（V 8.3 八条逐一比对 R 原话；01 篇句组六/七因 facts 无登记引文诚实留白为练习场）

## 方法论质量门
- [x] G1：facts.md ≥30 条编号事实，纯客观描述（无"因为/导致/所以"），每条带信源 URL（57 条 F1–F57 + 28 条 R1–R28）
- [x] G2：insights.md ≥3 条四元组洞察（现象+根因+影响+建议）（I1–I4 共 4 条）
- [x] G3：≥2 个可复用阅读模式，各含触发场景/核心步骤/反模式/迁移示例（P1 双源逐字核读法、P2 托名文本三层判读框架、P3 名句立场表阅读法）
- [x] V：原文抽查 10 处 + 事实抽查 10 条全部通过（实际抽查原文 17 处、事实 12 条；发现 2 处转述层缺陷——F46 史例混挂、V8 漏 R8 witness——均已修正闭环）

## OKF 格式与结构
- [x] 全部新增文档 frontmatter 符合 OKF v0.2（type/source/generated/verified/status/stale_after）（V 8.4 Grep 全量验证）
- [x] bundle 根 index.md 及各子目录 index.md 均含 toctree 且引用全部文档（范围化 check-toctrees exit 0：全部引用有效、所有内容文档可达）
- [x] 文件名 kebab-case 纯英文；正文中文；交叉引用为相对路径无断链、无 file:///（Grep "file://" 0 命中）
- [x] `bundles/think/huangdi/` 分组 index 与 toctree 完整
- [x] `bundles/think/index.md` 与 `bundles/index.md` 统计数字、分组表行、toctree 已同步更新（两文件 huangdi 行已在 HEAD 入库——由并行会话随其提交带入；工作区残余统计数字变更属其他会话，未纳入本任务提交）

## 交付验证
- [x] `invoke gates.all`（在 projects/awesome-okf-xs）全部通过（toctrees + utf8）——UTF-8 全库 6098 文件通过；本 bundle 范围化 toctree 检查通过且在全库 BFS 中无未可达条目；全局 gate 余留 117 处问题经逐条核对全部位于其他并行会话未完成 bundle（amitabha-sutra/diamond-sutra/platform-sutra/four-books/guan-tzu/shang-jun-shu/yinyangjia 等），按"不得回滚他人改动"纪律不处理
- [x] 原子提交完成且符合 Conventional Commits；主仓 gitlink 同步处理妥当（子模块提交 `195fc2b5`：docs(bundles) 19 文件/1592 行，git-commit-utf8 UTF-8 bytes 通道 PASS；主仓 gitlink 同步提交经用户确认跳过，指针变更保留在工作区待后续统一同步）
