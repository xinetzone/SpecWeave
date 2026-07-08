# 文章内容归档

## 文章基本信息

| 项目 | 内容 |
|---|---|
| 文章标题 | 《「同样的token,换个分法」:Anthropic产品团队据称放话,准确率从15%干到90%!》 |
| 发布方 | 微信公众号"海哥说事儿" |
| 发布时间 | 2026-07-05 18:50:33 |
| 文章URL | https://mp.weixin.qq.com/s/RUATqoajM5ZtbKZyNBW9hw |
| 文章类型 | 事实核查型 + 技术深度分析型复合报道 |
| 字符数 | 4860 字符 |

---

## 文章正文（按章节组织，保留原文结构）

### 第一部分：病毒式说法引入（@0xCodila 推文与四角色框架）

当地时间7月2日晚上10点09分,一条署名"Anthropic产品团队"的说法,被X用户@0xCodila摆上了台面。

没有长篇大论,只有几行字,信息量却大得吓人:多数人给AI喂更多token,指望换来更好的结果,Anthropic反过来测试了另一条路，同样数量的token,换一种分配方式,准确率从15%跳到90%。用他们自己的话讲,这叫"同样成本,效果翻5倍"。

15和90之间,隔着整整75个百分点。没换模型,没加预算,只是把干活的方式换了一下。这条消息像极了一张"作弊码":同样的钱,同样的算力,结果却是天壤之别。

同样的token,分给四个"打工人"@0xCodila把这套说法总结成一张清单,四个角色,四个动作:

- execute（执行者），do the work,负责把活干完
- advise（顾问），check the direction,负责把关方向对不对
- grade（评分官），pass or fail against a rubric,按一份评分标准判断通过还是失败
- dream（复盘者），inspect, learn, write to memory, sharpen next round,负责检查、学习、写进记忆、给下一轮做准备

"instead of one AI doing everything - split it into four: one works, one checks, one scores, one learns - same cost, but 5x better"

「把一个AI要干的所有事拆成四份:一个执行、一个检查、一个打分、一个学习，成本没变,效果翻了5倍。」

> ▲ @0xCodila的推文原文与中文翻译,232赞、458收藏、3.8万次查看

放到人话里理解也不难。一个模型如果既要写方案、又要自己审、还要自己打分、自己总结教训,四件事全挤在一个脑子里,难免顾此失彼。拆开之后,干活的专心干活,把关的专心挑毛病,打分的照标准来,复盘的负责把经验存下来，就像一个正常的团队分工,谁都不用一心多用。

### 第二部分：说法溯源与查证（逐字核对官方材料，判定"查无实据"）

这句话,Anthropic真的说过吗?问题是,这段话被反复截图、反复引用,却没人回答一个基本问题:Anthropic产品团队,真的说过这句话吗?

把"15% to 90%""execute advise grade dream"这几个关键词,放进Anthropic官网、开发者文档、工程博客里逐字核对,一个字都对不上。Anthropic从未在任何公开材料里,把token工作拆成execute、advise、grade、dream这套说法,更没有留下15%到90%这组数字的原始出处。

### 第三部分：衍生版本识别（主语/数字/预算变化，识别"可套用模板"特征）

更值得玩味的是,同一个创作者圈子里,还流传着另一个版本。有账号把同样的故事换了个主语,说成是"Anthropic平台工程负责人"讲的,数字也变了:起点从15%换成42%,还多了一个600000 token的具体预算。角色框架没变,人设变了,数字也变了。这不太像一次转述出了偏差,更像一套可以反复套用的模板，换个头衔,换一组数字,同一个故事可以讲很多遍。

这段说法本身查无实据。把干活、把关、打分、复盘拆给不同角色这件事,却能在Anthropic自己的产品页面和工程博客里,找到几乎一模一样的技术实现。

### 第四部分：官方证据链挖掘（Agent Teams/Subagents//goal/多智能体博客）

#### Claude Code 官方定位与真实案例

Claude Code的官方定位是"an agentic coding system that reads your codebase, makes changes across files, runs tests, and delivers committed code"(一套能读懂代码库、跨文件修改代码、跑测试、交付已提交代码的智能编码系统)。官方给出的几个真实案例已经足够说明分量:

- Stripe用它把一万行Scala代码迁移到Java,压缩到4天完成
- Ramp的故障排查时间减少80%
- Rakuten新功能的交付周期,从24个工作日缩短到5天

真正对应"四个角色"的,是三个具体功能。

#### Agent Teams（智能体团队）

一个lead session(主线程)负责协调,底下带着几个teammate(队友),每个队友都有自己独立的context window(上下文窗口),彼此之间还能互相发消息、共享任务清单。官方给出的推荐用法,几乎把"四个角色"翻译了一遍:一个盯用户体验,一个啃技术架构,还专门留一个唱反调的,当devil's advocate(魔鬼代言人)。

> ▲ Claude Code文档:Orchestrate teams of Claude Code sessions,强调"each in its own context window"

#### Subagents（子智能体）

如果说Agent Teams解决的是分工,Subagents解决的就是专精。文档写得很明白:当一个任务会把主对话灌满搜索结果、日志、大段文件内容,而这些内容之后又用不上时,就该交给子智能体单独处理,只把结论带回来。用户可以自己写一份带YAML frontmatter的配置文件,定义名字、描述、允许用的工具、模型、权限。内置示例里就有code-reviewer(代码评审员)、security-reviewer(安全评审员)、debugger(调试员)，本质上正是"grade"和"advise"两个角色的落地方式。

> ▲ Create custom subagents文档:独立上下文加可复用角色配置,对应"打分"与"把关"的官方实现

#### /goal循环

设定一个完成条件,Claude会持续干活,直到条件满足为止。每一轮结束,都有一个更小更快的模型检查条件是否成立,不成立就继续下一轮,不用人一直盯着。官方特意强调:少了这道检查,循环就没有意义。一个模型自己给自己打勾,几乎永远都是通过。

> ▲ Keep Claude working toward a goal文档:核心在于"a small fast model checks whether the condition holds"

#### 工程博客《How we built our multi-agent research system》

最有分量的证据,藏在Anthropic 2025年6月13日发布的工程博客《How we built our multi-agent research system》(我们如何构建多智能体研究系统)里。文中这样写道,几乎把整条viral说法的逻辑原样复述了一遍:

"multi-agent systems work mainly because they help spend enough tokens to solve the problem."

「多智能体系统之所以有效,主要原因是它们能帮你把足够多的token,花在解决问题的关键处。」

博客披露了一组内部评测:用Claude Opus 4当Lead(主控),Sonnet 4当Subagents(子智能体)并行工作,这套多智能体系统在研究类评测上,比单独一个Opus 4模型,效果高出90.2%。

15%到90%这组数字查无实据,但90.2%这个数字,白纸黑字写在Anthropic自己的博客里。两者未必是同一件事,方向却完全一致，分工比堆料更管用。

> ▲ 《How we built our multi-agent research system》,2025年6月13日发布,披露多智能体架构比单智能体高90.2%

### 第五部分：拆分角色有效的五个原因

为什么拆开角色,效果能差这么多普通人的直觉是:模型越强、token越多、上下文越长,效果就该越好。这套直觉,漏掉了几个很容易被忽视的坑。

**上下文会被自己的错误弄脏。** 一个模型如果同时要想点子、写代码、自我审查、还要复盘,它会把自己的草稿、假设、甚至错误全部留在同一个上下文里,后面的输出很容易被前面踩过的坑锚住。拆开角色之后,每个模型只看见跟自己任务相关的那部分,干净得多。

**自己给自己打分,几乎永远合格。** 官方反复提到,没有独立的verifier(验证器),循环就只是自我重复。grade这个角色,逼着系统按一份明确的标准判断通过或失败,幻觉和低质量输出因此被大幅拦下来。

**专业化,是人类团队早就验证过的常识。** 前端、后端、测试、产品,分工本身就是效率来源。放到模型身上,execute专注把活干完,advise专注方向对不对,grade专注质量够不够格,dream专注沉淀经验，每个角色的任务窄了,反而做得更精。

**并行加独立记忆,才是真正的杠杆。** 官方多智能体系统里,子智能体各自带着独立上下文和记忆目录,可以同时探索不同的假设,再把提炼后的结果交回给主控。dream角色做的,正是"检查、学习、写入记忆"这件事。

**token花在哪,比花了多少更能决定效果。** 工程博客里提到,很多时候性能差异其实来自有没有把足够的token用在正确的地方。多智能体表面上烧更多token,但换算到每一次成功产出的成本上,反而更低。

### 第六部分：历史脉络梳理（ReAct/Reflexion/Self-Refine/Karpathy Loop/工业界实践）

拆分角色这件事,早就有人先趟过路这套打法,在Anthropic之前就已经有人摸索过。

2023年前后,ReAct讨论让模型"思考"和"行动"交替进行;Reflexion和Self-Refine,让模型自己写检讨、自己重写答案,这是dream角色最早的雏形。@0xCodila本人几天前刚发过一篇关于"Karpathy Loop"的长文,提到卡帕西(Andrej Karpathy)式的自动研究框架:train.py负责干活(execute),不能被agent改动的prepare.py负责评分(grade),program.md负责给方向(advise)。agent自己做实验、自己回滚、自己记录状态。

工业界也不新鲜。不少公司内部早就把coding agent拆成Planner(规划者)、Coder(写代码的)、Tester(测试者)、Security Auditor(安全审计员)几个固定角色,分头干活。

Anthropic做的,是把这套散落在社区、论文、内部实践里的方法,一步步产品化，从Computer Use、Extended Thinking,到现在的Agent Teams、Subagents、/goal、多智能体研究系统,全部装进了Claude Code里。

### 第七部分：代价与边界分析

5倍效果背后,代价也不轻这套打法,代价一点也不便宜。

官方数据摆在那儿:多智能体系统消耗的token,大约是普通对话的15倍。协调开销也是实打实的，agent之间要互相通信,要处理任务依赖,还要解决冲突。

并非所有活儿都适合拆。强依赖顺序、需要共享大量状态的编码任务,单一会话可能反而更快。而且这套系统的地基,是一个可靠的verifier，测试用例、评分标准、人工审核,少了这一环,整个系统就退化成一场更贵的自言自语。调试难度也会跟着上升,一个子agent的小失误,可能带着整个团队一起走偏。

### 第八部分：核心论断升华

更大的模型,不如更懂事的团队回到最初那条推文。15%到90%这组数字或许经过了加工,或许只是一次营销式的再包装,但它抓住了2026年AI工程界一个真实的转向:token该往哪个角色身上砸,比token喂了多少更重要。

Anthropic用Agent Teams、Subagents、/goal、多智能体研究系统这些产品,把"拆队伍"从一个提示词技巧,变成了基础设施。谁执行、谁把关、谁打分、谁复盘记忆，同样的预算下,团队怎么搭,比模型堆多大更能决定效果。

这大概也是为什么,从Karpathy到Anthropic的工程师们,都在反复强调同一件事:验证环节是循环的灵魂,记忆是进化的燃料,角色分工,才是放大智能真正的杠杆。

---

> 预览时标签不可点
