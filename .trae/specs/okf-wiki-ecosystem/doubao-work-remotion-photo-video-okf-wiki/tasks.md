---
type: plan
title: 豆包工作与 Remotion 照片视频制作任务队列
status: completed
source: spec.md
---

# 豆包工作与 Remotion 照片视频制作任务队列

## 执行边界

用户批准 [spec.md](spec.md) 与本任务队列后执行。正式知识包写入 `projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/doubao-work-remotion-photo-video/`。

建议结构共 13 个 Markdown 文件：根 index/log，concepts 索引及 4 篇正文，references 索引及 5 篇台账。默认无 examples 目录。另在本规格目录保留 facts.md 作为双份事实核对基准；独立 review.md 仅在任务队列清空后创建。

## Task 1: 完成来源登记与事实核验
- **Status**: `completed`
- **Completion Evidence**:
  - 来源清单先于教程落盘；verification.md 覆盖日期版本、成效、口径、引文四表，图片 2–12、视频、福利和客户端复现缺口保留 flagged。
  - PowerShell Compare-Object 比对双份全部表行及 1..36 编号，输出 PASS: 36 identical fact rows, continuous F-001..F-036。
  - 官方 skills 页恢复后重新读取，确认 13 标题为 1 聚合 + 12 专项；未反推历史安装集合。
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 先写 `references/source-manifest.md`，记录公众号身份、原始与规范 URL、采集日期、访问方式和配图缺口。
  - 生成规格 facts.md 与 `references/article-source.md`，连续 F 编号，分离页面事实、作者主张及官方补充。
  - 完成 `references/verification.md`，逐项核验数量、安装方式、许可、自动质检与套餐，保留不确定项。
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-1.1: 至少 20 条实质事实均有来源键和定位；双份 F 集合相等且连续，使用机械集合比较验证。
  - `rule` TR-1.2: 配图及视频采集缺口、官方资料时点和所有 P0 核验状态完整，不从搜索摘要升级到正文已读。
- **Notes**: 不保存公众号全文；不因浏览器超时绕过访问限制。没有可靠历史证据时不将 Star 动态差异判成源文错误。

## Task 2: 编写学习教程与候选模式
- **Status**: `completed`
- **Completion Evidence**:
  - 四篇概念页已落盘，具体来源回指 F-007–F-036，安装和 CLI 均标未运行，原创模板和时间算例与原文分离。
  - knowledge-map.md 有 I-1/I-2/I-3，均含现象、根因假说、影响、建议、反常识与 F 证据；模式含五步、三反模式、检验及印刷迁移推演，validation_count=0。
  - TR-2.3 自验 4/5：读者能写素材、分镜、声音、输出和审批要求，并识别预览局限；缺原项目及运行验证，未给满分。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `concepts/00-tool-roles-and-boundaries.md`：豆包工作、Skill、Remotion、编码 Agent 和渲染器的分工；许可及费用边界。
  - `concepts/01-photo-storyboard-workflow.md`：素材整理、镜头安排、原创需求模板及静帧审核。
  - `concepts/02-render-audio-and-delivery.md`：确认后渲染、配乐与字幕、全片复查和可维护交付。
  - `concepts/03-preview-before-render-pattern.md`：包内“先预览后出片”候选模式、适用边界、反模式和跨域推演。
  - `references/knowledge-map.md`：事实/机制/迁移分层及三条四元组洞察。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-2.1: 所有具体能力、版本、数字及安装命令回指 F 与已读来源；建议模板标明非原文、未实测。
  - `rule` TR-2.2: 三条洞察四元组完整；模式含适用/不适用、3-7 步、至少三项风险反模式、检验标准和标为推演的跨域迁移，不声称多案例验证。
  - `rubric` TR-2.3: 初学者学习质量；scale 1-5；anchors 1 = 宣传摘要，3 = 分层清楚但步骤不足，5 = 能写完整创作需求并识别边界；threshold >= 4；evidence 为正文及自验说明。

## Task 3: 完成知识包导航及最小索引接入
- **Status**: `completed`
- **Completion Evidence**:
  - 13 页严格 UTF-8 解码且无 BOM，英文 kebab-case 文件名；9 个非保留文档 YAML 必需字段及 sources.resource 全部机械通过，仅新包根声明 okf_version。
  - runpy 调用 check-toctrees.py 的 run_scan(bundle_root) 为 0 错误；从 doc/index.md 的 BFS 覆盖本包全部 13 页。check-links.py --paths 全部13文件 --check-frontmatter-paths 实扫43本地引用有效，外链未做HTTP复测。
  - 已接入本包表行与 toctree，并与三个既有豆包包互链。用户在计数差异预览后批准“同步数字（推荐）”，四索引仅补数字；目录真值 ai-agent61/frameworks94/AI285/技术520，总索引710束对账0错误。
  - 路径限定 git diff 保留他方 ecosystems/practice/products、技术通信与总索引在途增量；未暂存、提交、推送或改他方新包。log 已追加包级通过及他方14项导航失败，未宣称全库导航通过。
- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - 各级 index 最后生成；根入口提供按读者问题的导航、已知边界、质量门与状态。
  - 写 log.md，仅记录实际采集、修订与验证事件。
  - 接入 ai-agent 分组，并与已有三个豆包工作主题包互链。
  - 重读共享索引现值，只追加本包与必要计数；不改其他会话的新包或事实。
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-3.1: 所有非保留 Markdown 具可解析 OKF frontmatter、type、sources.resource、status、stale_after、generated；仅 bundle 根声明 okf_version。
  - `rule` TR-3.2: 从父索引沿 toctree 可达全部新页；相对链接有效，文件名 kebab-case，UTF-8 无 BOM。
  - `rule` TR-3.3: 组/分区/总索引必要计数与当前目录一致，路径限定 diff 只包含本次增量且保留已知并行修改。
- **Notes**: 共享文件写前重读；动态重算计数，不照搬规格中的历史数字。

## Task 4: 执行门禁并回填验证证据
- **Status**: `completed`
- **Completion Evidence**:
  - 修订后复跑包级完整 toctree、站点父链 BFS、YAML/UTF-8/文件名、双份36表行与连续编号均通过；主仓链接器实际扫描13页、43本地引用及frontmatter路径通过。外部7链接未HTTP复测，已注明。
  - check-bundles-index.py 的 run_scan(doc/bundles) 输出空错误；目录真值61/94/285/520与共享计数一致。全库 check-toctrees.py exit1，14项全属 learn-from-materials（13页不可达、父toctree缺条目），本包0错误。
  - 现有环境 invoke gates.utf8 已检查12842文件通过；本轮13页又严格解码及无BOM回验。git diff --check 的本次路径无空白错误。
  - Sphinx 9.1.0 限定包级HTML构建exit0，使用原doc/conf.py、root_doc=bundles/jishu/ai/frameworks/ai-agent/doubao-work-remotion-photo-video/index及include_patterns=<本包>/**，临时独立输出。机械确认13HTML及“本地读取批准不是外传批准”“已验证可重建”最终修订文字存在；仅jieba/pkg_resources弃用提示。原全库后台构建仍运行，不重启、不宣称全站通过。
  - 四独立视角返回13条意见均已落实，P1上传授权风险已修；事实表不变。TR-4.2自验4/5，新人独立视角4/5：需求模板集中素材、帧率、格式、声音、交付及审批，CLI术语就地解释；原作媒体与客户端实测仍不足，因此不评5分。
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 使用子项目已有 UTF-8、toctree、bundles 门禁及适用链接/文件名检查，按路径保存精简结果。
  - 对双份 F、正文来源、关键计数做机械核对。
  - 可用时运行 Sphinx 构建；依赖缺失时不擅自安装，记录失败与等效检查边界。
  - 将自验结果回填每个任务的 Completion Evidence；不执行 Git 提交。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5
- **Test Requirements**:
  - `rule` TR-4.1: 运行过的检查均有命令和结果，存量错误与本次错误分类；新包不存在未修复断链或孤立页。
  - `rubric` TR-4.2: 初学者学习质量复验；scale 1-5；anchors 1/3/5 与 AC-3 相同；threshold >= 4；evidence 为自验评分、理由及修订定位。
- **Notes**: 队列清空后进入独立 Review，届时创建 review.md。新上下文只读审查全部 AC/TR，四视角记录到 references/adversarial-review.md；审查失败按规范追加修复 issue，不提前宣布完成。

## 最终验收

Review R3独立核验全部AC/TR并返回pass，新人4/5，无可行动修复issue。自身限定构建exit0且13HTML齐全；双份36事实、编码/YAML、导航/父链、43本地引用及现盘61/94/286/521/711计数通过。原全库后台构建另已exit0，仍有他方告警，不升级为全库门禁通过。R1/R2历史阻塞保留；本次文档交付完成，运行复现与Git操作不在完成范围。
