# 《知识魔法少女OK炭》100集OKF动漫 - 验证检查清单

## 项目规划阶段检查
- [x] spec.md PRD文档完整编写
- [x] tasks.md 12个任务单元分解完成，依赖关系形成有效DAG
- [x] checklist.md 本验证清单编写完成
- [ ] 用户审核并批准规划文档

## 任务0：项目初始化验证
- [ ] 输出目录结构完整创建（videos/scripts/assets子目录）
- [ ] 4个核心角色立绘生成（OK炭/小信/混沌博士/金链精灵）
- [ ] 角色设定集.md 完整包含形象/性格/口头禅/能力设定
- [ ] 世界观设定集.md 包含知识混沌界地图+七圣器视觉
- [ ] OP动画片段op.mp4 15秒生成成功
- [ ] 过场动画eyecatch.mp4 5秒生成成功
- [ ] 总览README.md包含番剧介绍/角色/集数表/观看指南

## 第1章（1-10集）验证
- [ ] ep001-ep010共10个分镜脚本存在
- [ ] ep001-ep010共10个视频文件存在
- [ ] 每集时长3-5分钟
- [ ] 第1集世界观和主角出场完整
- [ ] 第4集OKF五大问题（溯源/信任/新鲜度/生命周期/认证）全部提出
- [ ] 第5集OKF四大原则（可读/可解析/可diff/可移植）准确讲解
- [ ] 第7集"type是唯一必填字段"最小合规概念讲清
- [ ] 第10集结尾有第二章预告
- [ ] 角色性格符合设定：OK炭认真天然呆、小信好奇闯祸
- [ ] 美术风格统一为吉卜力+萌系科幻风

## 第2章（11-25集）验证
- [ ] ep011-ep025共15个分镜和视频存在
- [ ] Bundle结构三种分发方式（Git/tarball/子目录）准确
- [ ] index.md和log.md保留文件名规则讲清
- [ ] 渐进披露概念（先看清单再深入）有剧情演示
- [ ] Frontmatter必填/推荐/扩展字段层次讲清
- [ ] type不集中注册、容忍未知类型的设计讲透
- [ ] 脚注id键控vs位置索引的区别有反模式演示
- [ ] 第一圣器「知识宝箱」获得仪式完整
- [ ] 混沌博士在25集登场并被容错机制击退
- [ ] 结尾有第三章预告

## V阶段1-2章审查
- [ ] 对照okf-spec原文逐集核对前25集技术点
- [ ] 角色无OOC（Out of Character）
- [ ] 剧情无前后矛盾
- [ ] 发现的错误已修正
- [ ] review-ch1-2.md审查报告存在

## 第3章（26-40集）验证
- [ ] ep026-ep040共15个分镜和视频存在
- [ ] sources字段结构讲解准确
- [ ] "记录信号不记录评分"的设计哲学讲透
- [ ] 三个可信度信号author/usage_count/last_modified各自含义准确
- [ ] usage_count粗粒度性（不能精确排名、只能看数量级/活性）有明确演示
- [ ] usage_window时间窗口概念准确
- [ ] 谱系通过普通链接表达、无需专用字段讲清
- [ ] 逐断言脚注归因、重排不失效有反模式演示（位置索引陷阱）
- [ ] 第二圣器「溯源金锁」获得
- [ ] 结尾有第四章预告

## 第4章（41-55集）验证
- [ ] ep041-ep055共15个分镜和视频存在
- [ ] generated（谁写的）和verified（谁核验的）分立原因讲透（编写者≠核验者）
- [ ] verified支持多核验者、裸映射=单元素列表准确
- [ ] 三级信任层级判定准确：
  - [ ] 无verified → unverified铜徽章
  - [ ] 仅非human: → machine-confirmed银徽章
  - [ ] 有human: → human-reviewed金徽章
- [ ] 信任是咨询信号不是访问控制讲透（没verified也不能拒绝）
- [ ] 三种actor格式：<producer>/<version>、human:<id>、process:<id>准确
- [ ] human:前缀对信任层级判定的关键性强调
- [ ] 第三圣器「三级信任徽章」获得
- [ ] 混沌博士伪造人工核验被识破的剧情合理
- [ ] 结尾有第五章预告

## V阶段3-4章审查
- [ ] 对照原文核对26-55集技术点
- [ ] 信任层级判定无错误
- [ ] actor约定使用准确
- [ ] review-ch3-4.md审查报告存在

## 第5章（56-70集）验证
- [ ] ep056-ep070共15个分镜和视频存在
- [ ] status三种状态draft/stable/deprecated含义准确
- [ ] status缺省默认是stable讲清
- [ ] stale_after绝对日期vs相对TTL的设计理由讲透（零依赖日期比较）
- [ ] today >= stale_after即过期判定准确
- [ ] generated和verified独立（可重新生成不核验、可重新核验不生成）准确
- [ ] 过期≠删除，deprecated+stale_after组合使用讲清
- [ ] 生命周期状态和信任层级互相独立准确（过期的金徽章还是金徽章）
- [ ] 第四圣器「时间沙漏」获得
- [ ] 混沌博士把知识设成永不过期被惩罚的反模式演示
- [ ] 结尾有第六章预告

## 第6章（71-85集）验证
- [ ] ep071-ep085共15个分镜和视频存在
- [ ] 计算独立成概念的三个理由（runtime定义参数语义/一套计算多消费者/信任隔离）讲透
- [ ] 契约五字段runtime/parameters/computation/executor/attester各自含义准确
- [ ] executor.receipt返回证据字段的概念准确
- [ ] attester必须是确定性无LLM代码强调
- [ ] 两种计算承载方式：内联围栏vs外部文件准确
- [ ] 智能体只能填参数绝对不能改写计算的核心安全规则反复强调
- [ ] 认证检查两要素：溯源校验+保真度校验讲清
- [ ] 消费者六步流程（发现→加载→参数化→执行→认证→门禁）完整演示
- [ ] verification（文档级慢速核验）vs attestation（运行时逐次认证）区别讲透
- [ ] 损益表收入计算完整示例准确
- [ ] 第五圣器「契约红印」获得
- [ ] 混沌博士改写SQL被attester抓获的剧情合理
- [ ] 结尾有第七章预告

## V阶段5-6章审查
- [ ] 对照原文核对56-85集技术点
- [ ] Attested Computation安全设计无错误
- [ ] verification vs attestation区别无混淆
- [ ] review-ch5-6.md审查报告存在

## 第7章（86-95集）验证
- [ ] ep086-ep095共10个分镜和视频存在
- [ ] 两种链接：bundle-relative绝对路径（/开头，推荐）vs 相对路径准确
- [ ] 为什么推荐绝对路径（文档移动不失效）讲清
- [ ] 链接不表达类型，关系由行文表达讲透
- [ ] 断链允许=未来知识的宽容设计有剧情演示
- [ ] 路径值字段清单（resource/sources[]/computation/executor/attester）准确
- [ ] references/子目录约定讲清
- [ ] actor约定完整复习
- [ ] 合规三要件（每个非保留.md有frontmatter/有type/保留文件守规范）准确
- [ ] "不得拒绝"5项清单完整演示：缺可选字段/未知type/未知扩展键/断链/缺index都不能拒绝
- [ ] 第六圣器「航路罗盘」获得
- [ ] 结尾有终章预告

## 第8章（96-100集）验证
- [ ] ep096-ep100共5个分镜和视频存在
- [ ] 每集加长到5-6分钟作为大结局
- [ ] versioning规则：major/minor版本、向后兼容vs破坏性变更准确
- [ ] okf_version在根index.md声明准确
- [ ] v0.1→v0.2两处破坏性变更+增量变更准确：
  - [ ] timestamp → generated.at
  - [ ] 正文# Citations → frontmatter sources
  - [ ] 新增字段族/Attested Computation/actor约定等增量
- [ ] 损益表完整迁移v0.1→v0.2示例准确（对应examples/income-statement.md）
- [ ] 合规大演练：混沌博士所有刁钻攻击都被化解
- [ ] 混沌博士洗白，理解OKF的宽容哲学
- [ ] 七圣器集齐，加冕建立可信知识王国
- [ ] 加长版ED所有角色出场谢幕
- [ ] v0.3未来展望留下余韵

## 最终全片审查
- [ ] ep001-ep100.mp4共100个视频文件全部存在，连续编号无缺失
- [ ] ep001-ep100.md共100个分镜脚本全部存在
- [ ] 所有19个okf-spec概念文档知识点覆盖率100%
  - [ ] concepts/motivation.md 覆盖
  - [ ] concepts/terminology.md 覆盖
  - [ ] concepts/bundle-structure.md 覆盖
  - [ ] concepts/concept-documents.md 覆盖
  - [ ] concepts/provenance-sources.md 覆盖
  - [ ] concepts/trust-generated-verified.md 覆盖
  - [ ] concepts/lifecycle-status-stale.md 覆盖
  - [ ] concepts/cross-linking-paths.md 覆盖
  - [ ] concepts/actor-convention.md 覆盖
  - [ ] concepts/index-files.md 覆盖
  - [ ] concepts/log-files.md 覆盖
  - [ ] concepts/attested-computations.md 覆盖
  - [ ] concepts/conformance.md 覆盖
  - [ ] concepts/versioning.md 覆盖
  - [ ] concepts/changes-from-v0.1.md 覆盖
  - [ ] examples/ 三个示例都有演示
- [ ] 每集结构统一：OP+前情+正片+ED预告
- [ ] 角色形象100集保持一致，无OOC
- [ ] 美术风格统一
- [ ] 关键术语中英双语标注
- [ ] 伏笔全部回收
- [ ] 最终审查报告final-review.md存在
- [ ] README.md最终版完整，包含100集完整列表

## 观看体验检查
- [ ] 即使完全不懂OKF的初学者也能看懂
- [ ] 剧情有趣，有笑点有萌点有燃点，能让人想追下去
- [ ] 技术点通过剧情自然引出，没有生硬念PPT的感觉
- [ ] 反模式演示清晰，看完知道什么是错的为什么错
- [ ] 看完100集能够实际使用OKF编写合规的知识包
