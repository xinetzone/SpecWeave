# 《知识魔法少女OK炭》100集OKF动漫 - 实施计划

## [x] 任务0：项目初始化与基础设定
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建输出目录结构：`playground/books/okf-100ep-anime/` 下的 `videos/`、`scripts/`、`assets/` 子目录
  - 生成角色设定集：4个核心角色的详细立绘（seedream）
  - 生成世界观设定集：知识混沌界地图、七圣器视觉设计（seedream）
  - 生成OP动画片段：固定15秒OP，OK炭变身+标题logo展示（seedance）
  - 生成过场动画（eye catch）：OKF logo闪现5秒片段（seedance）
  - 编写总览README.md，包含番剧介绍、角色列表、集数列表、观看指南
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-7
- **Test Requirements**:
  - `programmatic` TR-0.1: 目录结构创建完整，子目录存在
  - `programmatic` TR-0.2: 角色设定集.md、世界观设定集.md、README.md存在
  - `human-judgement` TR-0.3: 角色立绘形象统一、符合设定描述
  - `programmatic` TR-0.4: OP片段(op.mp4)和过场片段(eyecatch.mp4)生成成功

## [/] 任务1：第1章·序章（第1-10集）制作
- **Priority**: high
- **Depends On**: 任务0
- **Description**:
  - 编写第1-10集分镜脚本，每集单独一个Markdown文件
  - 为每集生成关键帧插画（每集3-5张关键帧，seedream）
  - 按分镜用关键帧生成视频片段（每段15秒，seedance）
  - 拼接每集：OP + 前情 + 正片片段 + ED/预告
  - 第10集结尾生成第二章预告片段
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-1.1: 分镜脚本ep001-ep010.md共10个文件存在
  - `programmatic` TR-1.2: 视频文件ep001.mp4-ep010.mp4共10个存在
  - `programmatic` TR-1.3: 每集时长在180-300秒(3-5分钟)之间
  - `human-judgement` TR-1.4: 第1-10集知识点覆盖：动机/四大原则/五大问题/type字段/Frontmatter基础，与规范一致
  - `human-judgement` TR-1.5: 四个核心角色全部出场，形象一致，性格符合设定
  - `human-judgement` TR-1.6: 世界观建立清晰，剧情有吸引力，留下悬念进入下一章

## [ ] 任务2：第2章·知识宝箱（第11-25集）制作
- **Priority**: high
- **Depends On**: 任务1
- **Description**:
  - 编写第11-25集分镜脚本
  - 生成关键帧插画（知识宝箱圣器视觉设计、图书馆遗迹场景等）
  - 生成并拼接15集完整视频
  - 知识点覆盖：Bundle结构/三种分发方式/保留文件名/index.md渐进披露/log.md更新日志/概念文档结构/type必填/title/description/resource/tags/扩展字段/脚注归因
  - 第25集结尾生成第三章预告片段
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-2.1: ep011-ep025共15个分镜和视频存在
  - `programmatic` TR-2.2: 每集时长符合3-5分钟要求
  - `human-judgement` TR-2.3: 第11-25集知识点覆盖bundle-structure/concept-documents/index-files/log-files全部内容
  - `human-judgement` TR-2.4: 第一圣器「知识宝箱」获得剧情完整，混沌博士首次作为反派登场并被击退
  - `human-judgement` TR-2.5: 反模式演示准确：误用保留文件名、缺失type字段等错误有明确展示

## [ ] 任务3：V阶段·第1-2章对抗审查与修正
- **Priority**: high
- **Depends On**: 任务2
- **Description**:
  - 对照 `projects/awesome-okf-xs/bundles/okf-spec/` 原文逐集核对技术准确性
  - 检查角色一致性、剧情连贯性
  - 发现错误/不一致的地方修正对应分镜和视频
  - 记录审查报告
- **Acceptance Criteria Addressed**: AC-5, AC-3, AC-6
- **Test Requirements**:
  - `human-judgement` TR-3.1: 前25集无技术事实错误
  - `human-judgement` TR-3.2: 角色无OOC，剧情连贯无矛盾
  - `programmatic` TR-3.3: 审查报告review-ch1-2.md存在

## [ ] 任务4：第3章·溯源金锁（第26-40集）制作
- **Priority**: high
- **Depends On**: 任务3
- **Description**:
  - 编写第26-40集分镜脚本
  - 生成关键帧（金链精灵、溯源锁链视觉、信源水晶等）
  - 生成并拼接15集完整视频
  - 知识点覆盖：sources字段/为什么不用评分/三个可信度信号(author/usage_count/last_modified)/usage_window/谱系通过链接表达/逐断言脚注归因/位置索引陷阱
  - 第40集结尾生成第四章预告片段
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-4.1: ep026-ep040共15个分镜和视频存在
  - `human-judgement` TR-4.2: provenance-sources.md全部知识点覆盖
  - `human-judgement` TR-4.3: usage_count粗粒度信号、id键控vs位置索引等细节准确
  - `human-judgement` TR-4.4: 金链精灵作为新守护精灵登场并保持后续一致性

## [ ] 任务5：第4章·信任徽章（第41-55集）制作
- **Priority**: high
- **Depends On**: 任务4
- **Description**:
  - 编写第41-55集分镜脚本
  - 生成关键帧（铜/银/金三级徽章、演员身份标识等）
  - 生成并拼接15集完整视频
  - 知识点覆盖：generated/verified分立/generated.by/at/verified多核验者/裸映射简写/三级信任层级(unverified/machine-confirmed/human-reviewed)/信任是咨询信号非访问控制/actor约定三种格式/human:前缀重要性
  - 第55集结尾生成第五章预告片段
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-5.1: ep041-ep055共15个分镜和视频存在
  - `human-judgement` TR-5.2: trust-generated-verified.md全部知识点覆盖，actor-convention.md完整讲解
  - `human-judgement` TR-5.3: 三级信任层级判定规则演示准确（特别是human:前缀判定）
  - `human-judgement` TR-5.4: "没有verified也不能拒绝知识"的宽容原则明确传达

## [ ] 任务6：V阶段·第3-4章对抗审查与修正
- **Priority**: high
- **Depends On**: 任务5
- **Description**:
  - 对照规范逐集核对第3-4集技术准确性
  - 角色一致性、剧情连贯性检查
  - 修正错误，记录审查报告
- **Acceptance Criteria Addressed**: AC-5, AC-3, AC-6
- **Test Requirements**:
  - `human-judgement` TR-6.1: 第26-55集无技术事实错误
  - `programmatic` TR-6.2: 审查报告review-ch3-4.md存在

## [ ] 任务7：第5章·时间沙漏（第56-70集）制作
- **Priority**: high
- **Depends On**: 任务6
- **Description**:
  - 编写第56-70集分镜脚本
  - 生成关键帧（时间沙漏、四种状态水晶、日历场景等）
  - 生成并拼接15集完整视频
  - 知识点覆盖：status三种状态(draft/stable/deprecated)/status默认stable/stale_after绝对日期/为什么不用相对TTL/过期判定/today>=stale_after/generated与verified独立/过期≠删除
  - 第70集结尾生成第六章预告片段
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-7.1: ep056-ep070共15个分镜和视频存在
  - `human-judgement` TR-7.2: lifecycle-status-stale.md全部知识点覆盖
  - `human-judgement` TR-7.3: "绝对日期vs相对TTL"的设计理由讲清楚
  - `human-judgement` TR-7.4: 四种状态水晶视觉一致，状态变化逻辑准确

## [ ] 任务8：第6章·契约红印（第71-85集）制作
- **Priority**: high
- **Depends On**: 任务7
- **Description**:
  - 编写第71-85集分镜脚本
  - 生成关键帧（魔法契约、红蜡印、executor/attester视觉等）
  - 生成并拼接15集完整视频
  - 知识点覆盖：为什么计算独立成概念/runtime决定参数语义/一套计算多消费者/信任隔离/契约五字段/executor.receipt/attester无LLM/内联vs文件计算/智能体不能改计算/认证检查(溯源+保真度)/消费者六步流程/verification vs attestation区别
  - 第85集结尾生成第七章预告片段
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-8.1: ep071-ep085共15个分镜和视频存在
  - `human-judgement` TR-8.2: attested-computations.md全部知识点覆盖
  - `human-judgement` TR-8.3: 智能体不能改写计算只能填参数这个核心安全设计讲透
  - `human-judgement` TR-8.4: verification vs attestation的区别演示清晰（文档级vs运行时）
  - `human-judgement` TR-8.5: 损益表计算示例完整准确

## [ ] 任务9：V阶段·第5-6章对抗审查与修正
- **Priority**: high
- **Depends On**: 任务8
- **Description**:
  - 对照规范逐集核对第5-6章技术准确性
  - 重点审查Attested Computation的安全设计和使用流程
  - 修正错误，记录审查报告
- **Acceptance Criteria Addressed**: AC-5, AC-3, AC-6
- **Test Requirements**:
  - `human-judgement` TR-9.1: 第56-85集无技术事实错误，特别是认证相关内容
  - `programmatic` TR-9.2: 审查报告review-ch5-6.md存在

## [ ] 任务10：第7章·航路罗盘（第86-95集）制作
- **Priority**: high
- **Depends On**: 任务9
- **Description**:
  - 编写第86-95集分镜脚本
  - 生成关键帧（知识网络、航路罗盘、references传送门等）
  - 生成并拼接10集完整视频
  - 知识点覆盖：两种链接(bundle-relative绝对/相对路径)/为什么推荐绝对路径/链接不表达类型/断链允许/路径值字段清单/references约定/actor约定完整复习/合规三要件/"不得拒绝"宽容清单
  - 第95集结尾生成终章预告片段
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-10.1: ep086-ep095共10个分镜和视频存在
  - `human-judgement` TR-10.2: cross-linking-paths.md + conformance.md全部知识点覆盖
  - `human-judgement` TR-10.3: "不得拒绝"5项清单演示完整，宽容哲学传达清晰
  - `human-judgement` TR-10.4: 断链=未来知识这个理念有明确剧情演示

## [ ] 任务11：第8章·终章·王国建成（第96-100集）制作
- **Priority**: high
- **Depends On**: 任务10
- **Description**:
  - 编写第96-100集分镜脚本
  - 生成关键帧（版本王冠、加冕典礼、可信知识王国全景等）
  - 生成并拼接5集完整视频（加长到每集5-6分钟作为大结局）
  - 知识点覆盖：versioning(major/minor规则)/v0.1→v0.2变更/完整实战损益表v0.1迁移v0.2/合规大演练/混沌博士洗白/七圣器集齐加冕/ED完结撒花/未来v0.3展望
  - 生成加长版ED（30秒），所有角色出场谢幕
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-11.1: ep096-ep100共5个分镜和视频存在
  - `human-judgement` TR-11.2: versioning.md + changes-from-v0.1.md全部知识点覆盖
  - `human-judgement` TR-11.3: 损益表迁移示例完整准确（对应income-statement.md示例）
  - `human-judgement` TR-11.4: 七圣器集齐，混沌博士洗白，剧情收束完整，有感动点
  - `human-judgement` TR-11.5: 大结局有仪式感，ED谢幕完整，留下对v0.3的期待

## [ ] 任务12：最终V阶段·全100集终审
- **Priority**: high
- **Depends On**: 任务11
- **Description**:
  - 全100集抽审：每章抽2集（共16集）做详细技术审核
  - 角色一致性从头到尾检查
  - 剧情线从头到尾连贯检查，伏笔全部回收
  - 总目录README更新完成，100集列表完整
  - 生成最终审查报告
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-12.1: ep001-ep100.mp4全部100个文件存在，无缺失
  - `programmatic` TR-12.2: 所有100个分镜脚本存在
  - `human-judgement` TR-12.3: 抽审的16集无技术错误
  - `human-judgement` TR-12.4: 从头到尾角色无OOC，美术风格统一
  - `human-judgement` TR-12.5: 所有伏笔回收，结局完整，看完能学会OKF
  - `programmatic` TR-12.6: 最终审查报告final-review.md存在
  - `human-judgement` TR-12.7: README.md完整，观看指南清晰

## 任务依赖关系图

```
任务0 → 任务1 → 任务2 → 任务3 → 任务4 → 任务5 → 任务6 → 任务7 → 任务8 → 任务9 → 任务10 → 任务11 → 任务12
         第1章    第2章    V1-2    第3章    第4章    V3-4    第5章    第6章    V5-6    第7章     第8章    终审
```

## 分批交付说明

100集体量较大，按8章+3次V审查+最终审评分12个任务单元推进
每完成一个V审查任务，可先审阅当前章内容，确认后再继续下一章
