# 以道入商·竹简悟道视角升级 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 文档骨架与哲学根基重构
- **Priority**: high
- **Depends On**: None
- **Status**: ✅ 已完成
- **Description**:
  - 创建新文件 `playground/reports/daoshang-business-wudao-v2.0.md`
  - 撰写frontmatter（type: private, package_version: 2.0, wudao_integrated: true等）
  - 重构执行摘要：从"工具包"升级为"道商修行手册"定位
  - 建立"道商"概念定义：基于帛书《老子》的商业哲学，区别于世俗商业
  - 将5条商业公理重新锚定到帛书原典，形成"洞察1-5：道商五公理"，每条含【帛书根源】【核心内容】【商业应用】
- **Acceptance Criteria Addressed**: AC-1, AC-8, AC-10, AC-11
- **Test Requirements**:
  - `programmatic` TR-1.1: ✅ 文件存在于 `playground/reports/daoshang-business-wudao-v2.0.md`
  - `programmatic` TR-1.2: ✅ frontmatter包含package_version: "2.0"和wudao_integrated: true
  - `human-judgement` TR-1.3: ✅ 5条公理每条都有帛书章节号和原文引用
  - `human-judgement` TR-1.4: ✅ 无"你必须""一定要"等指令性语言
- **Verified By**: Task9审查确认零违规

---

## [x] Task 2: 体道四法商业路径（道商四阶）
- **Priority**: high
- **Depends On**: Task 1
- **Status**: ✅ 已完成
- **Description**:
  - 用体道四法重构v1.0的四层变现框架为"道商四阶"
  - 第一阶：虚静内观（收）——定位层，对应帛书第16章
  - 第二阶：自然无为（守）——目标层，对应帛书第25章
  - 第三阶：柔弱不争（柔）——呈现层，对应帛书第36章
  - 第四阶：生活实践（行）——机制层，对应帛书第41章
  - 绘制道商四阶流转图（文本框图）
- **Acceptance Criteria Addressed**: AC-2, AC-8
- **Test Requirements**:
  - `human-judgement` TR-2.1: ✅ 四阶顺序正确（收→守→柔→行），每阶有对应帛书章节
  - `human-judgement` TR-2.2: ✅ v1.0四层框架核心内容完整映射
  - `human-judgement` TR-2.3: ✅ 三阶递进隐含在每阶描述中
- **Verified By**: Task9审查确认

---

## [x] Task 3: 商业概念陷阱解缚（七概念）
- **Priority**: high
- **Depends On**: Task 2
- **Status**: ✅ 已完成
- **Description**:
  - 新增"商业中的概念陷阱——七重解缚"章节
  - 解缚7个概念：必须成功/必须卷/流量为王/努力=结果/快速变现/低价无好货/竞争思维
- **Acceptance Criteria Addressed**: AC-3, AC-11
- **Test Requirements**:
  - `human-judgement` TR-3.1: ✅ 覆盖7个概念陷阱，每个都有四步解缚
  - `human-judgement` TR-3.2: ✅ 每个陷阱至少引用一处帛书原文
  - `human-judgement` TR-3.3: ✅ 不提供"应该怎么做"的替代方案
- **Verified By**: Task9审查确认

---

## [x] Task 4: 体道链商业认知标尺
- **Priority**: high
- **Depends On**: Task 2
- **Status**: ✅ 已完成
- **Description**:
  - 新增"体道链——你的商业认知在哪一层？"章节
  - 六层：名→反→有无→正言若反→无为→玄同
- **Acceptance Criteria Addressed**: AC-4, AC-6
- **Test Requirements**:
  - `human-judgement` TR-4.1: ✅ 六层完整
  - `human-judgement` TR-4.2: ✅ 每层有至少一个开放性自测问题
  - `human-judgement` TR-4.3: ✅ 问题不引导特定方向
- **Verified By**: Task9审查确认

---

## [x] Task 5: 道商九问反思工具
- **Priority**: high
- **Depends On**: Task 3, Task 4
- **Status**: ✅ 已完成
- **Description**:
  - 新增"道商九问"工具章节（虚静3+无为2+柔弱2+践行1+玄同1=9问）
  - 全部为开放性问题，不提供标准答案
- **Acceptance Criteria Addressed**: AC-6, AC-11
- **Test Requirements**:
  - `human-judgement` TR-5.1: ✅ 共9个开放性问题
  - `human-judgement` TR-5.2: ✅ 四法+玄同分布合理（3+2+2+1+1）
  - `human-judgement` TR-5.3: ✅ 问题不隐含"应该"的答案
- **Verified By**: Task9审查确认

---

## [x] Task 6: 营销物料哲学升级（海报+文案）
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Status**: ✅ 已完成
- **Description**:
  - 共修海报8区块完整升级（主标题/解缚区/正言若反对比/四法交付大纲/同行者画像/教练团/同行故事/行动召唤）
  - 8个人群文案全部升级为正言若反式，融入帛书金句
- **Acceptance Criteria Addressed**: AC-5, AC-9, AC-11
- **Test Requirements**:
  - `human-judgement` TR-6.1: ✅ 海报完整结构保留
  - `human-judgement` TR-6.2: ✅ 8个人群文案全部升级，每个有帛书金句
  - `human-judgement` TR-6.3: ✅ 199元定价和前20名福利保留
  - `human-judgement` TR-6.4: ✅ 语气转为"邀请共修"
  - `human-judgement` TR-6.5: ✅ 不做收益承诺
- **Verified By**: Task9审查确认

---

## [x] Task 7: 执行工具升级（体道践行卡+七日体道）
- **Priority**: high
- **Depends On**: Task 5
- **Status**: ✅ 已完成
- **Description**:
  - 体道践行卡（晨间虚静/日间无为/晚间复盘+签字栏）
  - 七日体道（七个觉察主题，不打卡不连续天数）
- **Acceptance Criteria Addressed**: AC-7, AC-9
- **Test Requirements**:
  - `human-judgement` TR-7.1: ✅ 践行卡包含晨间/日间/晚间三段节律
  - `human-judgement` TR-7.2: ✅ 晨间和晚间开放式问题，日间checkbox
  - `human-judgement` TR-7.3: ✅ 保留可打印的checkbox和签字区
  - `human-judgement` TR-7.4: ✅ 无"打卡天数""连续X天"等游戏化元素
- **Verified By**: Task9审查确认（修复了帛书索引中Day编号问题）

---

## [x] Task 8: 洞察模式萃取+元洞察+附录整合
- **Priority**: medium
- **Depends On**: Task 2, Task 3, Task 4
- **Status**: ✅ 已完成
- **Description**:
  - 道商洞察库（洞察6-13共8个方法论模式）
  - 4条元洞察
  - 行动次第（24h/7d/30d）
  - 帛书金句索引（24章）
  - Changelog
- **Acceptance Criteria Addressed**: AC-8, AC-9
- **Test Requirements**:
  - `human-judgement` TR-8.1: ✅ 洞察编号1-13连续
  - `human-judgement` TR-8.2: ✅ 每个洞察有来源标注
  - `human-judgement` TR-8.3: ✅ 金句索引包含所有引用原文
  - `human-judgement` TR-8.4: ✅ 行动项保留时间分层
  - `programmatic` TR-8.5: ✅ Changelog记录v2.0变更
- **Verified By**: Task9审查确认

---

## [x] Task 9: 哲学约束全文审查与最终润色
- **Priority**: high
- **Depends On**: Task 6, Task 7, Task 8
- **Status**: ✅ 已完成
- **Description**:
  - 全文审查竹简悟道哲学约束C-01~C-08
  - 发现并修复10处问题
  - 最终确认硬约束零违规
- **Acceptance Criteria Addressed**: AC-11, AC-9, NFR-3, NFR-6
- **修复清单**:
  1. frontmatter补充scenes/tags/description
  2. "客观规律"→"样子"（C-06实在论修正）
  3. ❌✅符号→文字描述（C-08）
  4. "知行合一"（王阳明心学）→"勤而行之"（帛书第41章）（C-06概念混用）
  5. "接纳"（心理学词汇）→朴素描述（C-06）
  6. "必须出声""必须读出声"→柔化为引导式（C-08）
  7. "学习金字塔留存率90%"→删除（C-04技术禁令）
  8. "必须有变现闭环"→柔化（C-08）
  9. "道是可验证的认知科学"（含神经科学术语）→"道是践行出来的活法"（C-04+C-06）
  10. 帛书索引Day1-Day7→七个觉察主题名（C-07自相矛盾）
- **Test Requirements**:
  - `human-judgement` TR-9.1: ✅ 指令/承诺词使用语境合法
  - `human-judgement` TR-9.2: ✅ v1.0实操内容完整保留
  - `human-judgement` TR-9.3: ✅ 语气统一为"陪你看清"
  - `human-judgement` TR-9.4: ✅ 无生硬的哲学概念堆砌
- **最终统计**: 中文字符约23,230字，硬约束C-01~C-08零违规
