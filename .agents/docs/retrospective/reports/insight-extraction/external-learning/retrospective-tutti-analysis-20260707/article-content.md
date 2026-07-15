# Tutti 原始文章内容

> 来源：https://mp.weixin.qq.com/s/32_9_2AjjC4GscIVhf73BA?from=industrynews&color_scheme=light#rd
> 作者：小 G 小 G
> 提取时间：2026-07-07

---

前几天用 Claude Code 做一个项目，开发到一半额度就没了，想让 Codex 接着干。

结果光跟 Codex 交代项目背景、确认 Claude 改到哪一步，就花费了十几分钟，还有漏掉的。

明明手上可用的 Agent 工具一大堆，可是每次切换的时候，都得把前因后果重新讲一遍。

于是我到 GitHub 上寻找，想看看有没有比较好的多 Agent 协作开源工具。

偶然发现一款名为 **Tutti** 的工具，刚开源不久，提供了一个很有意思的解决方案。

GitHub：https://github.com/tutti-os/tutti

![image-20260703182200930](https://mmbiz.qpic.cn/mmbiz_png/snxIHWuwQokMWIpLrb8bT2Gibkt5r9pmj8fea13xVKtBSZfyd51YtJXRjzXSicrSEmibpDoeFp4dIk3j4xWanAWFOBCPdJcSDHwicKGYE5hfqW4/640?wx_fmt=png&from=appmsg)

image-20260703182200930

### Tutti 是什么

安装后打开界面，第一眼看起来就像个 OS 系统，底部是可以快速打开的应用。

可以接入 Claude Code、Codex，在启动台，还看到 Hermes、Gemini、OpenClaw 是置灰状态，后续应该也会支持接入。

另外里面还内置了一些自己的应用，比如有产品原型设计、AI 文档、PPT、生图等等。

![image-20260703200157374](https://mmbiz.qpic.cn/sz_mmbiz_png/snxIHWuwQonjjtLYyZO5YS3lu4hpUeRcQibDyGv45TjA1iafNwCTfKZs19B1zkseFQ2JThntRaoAJDMib2FzWXFQnsdpweucGLQiax060vlrMYk/640?wx_fmt=png&from=appmsg)

image-20260703200157374

README 里说 **Tutti 是一个多 Agent 实时共享的工作空间，打通了上下文、应用、任务、文件** 。

周末测了一下发现，上面这几个东西，Agent 之间确实能共享，甚至还能共享应用的产出。

比如我先在 Claude Code 里做一个项目，然后要切到 Codex，只需在输入框 @ 一下。

![image-20260704175412892](https://mmbiz.qpic.cn/sz_mmbiz_png/snxIHWuwQom0F2oEIMichOtmvG7cicVaO5aThpf8icea1jeicpTVwia04138MMgeszTv6078DyqMYkYKFZE5MUUdcZJ0NEw9Utl8gcEia7I4Mib1rk/640?wx_fmt=png&from=appmsg)

image-20260704175412892

就可以直接引用刚才 Claude Code 里的历史会话，里面完整的上下文。

包括我的需求、它的回复、过程文件的 diff、所有改动等等信息。

让 Codex 接手的时候，不再需要我自己总结，或者重新进入到项目交代任务。

它自己就能看到我在 Claude Code 里到底做了什么，做到了哪一步。

另外还发现 Tutti 里的应用，只要涉及 AI 能力的，都可以选择我已连接的 Agent。

![image-20260704175708101](https://mmbiz.qpic.cn/sz_mmbiz_png/snxIHWuwQolEayks7xJzsaz5l076BjMIIOcS2AagktN2Y1OIxZZXNYfHBQ4ycsicqgtkrny8nibnwvj873plPbFRnDRaRgA7Qa0zvKr1YzJQY/640?wx_fmt=png&from=appmsg)

image-20260704175708101

也就是说，能用我已有的 AI 订阅，让我的 Agent 拥有在垂类场景解决问题的能力。

在应用里生成的东西，再回到 Codex 里，同样可以通过 @ 引用它，用到项目里。

到这里初步了解完 Tutti 后，说真的，内心还是挺激动和震撼的。

他们用一种很不一样、且合理的方式，解决了跨 Agent 交接、复杂工作流的连续性问题。

将人从反复搬运上下文的重复劳力里释放出来。

而对 Agent 来说，这就像是从只给他一张纸，到给他一本有目录的书。

要用什么上下文，照着目录翻就能拿到，比人转述的那几句充足多了。

### 上手体验

为了看它是不是真的有用，我拿它从零开始做了一个小项目。

一个「2026 世界杯赛事实时追踪」应用，里面有赛程、比分、球队信息、积分榜。

这样的项目其实不算复杂，但我觉得带大家从零开始做，很适合测试一下 Tutti。

因为过程会涉及到需求梳理、原型设计、页面开发、功能迭代等环节。

平时都是需要用到多个 AI 工具协作才能完成的，经常会来回切换，很麻烦。

首先在 Tutti 里打开 Claude Code，让它帮我梳理需求，提示词大概就如下图这样：

![image-20260627103726435](https://mmbiz.qpic.cn/mmbiz_png/snxIHWuwQol4e7u07JHdKGfQpw2KBjD7SVJSThLuLEVqWQn0RKCR1eXdlsMHNFXHHonMVDw3vmlhpmAPGHYocZpUroUxVv1QXiaGYesfSbrU/640?wx_fmt=png&from=appmsg)

image-20260627103726435

可以看到 Tutti 里 Claude Code，交互比在终端清晰许多。

很快 Claude Code 就把需求整理出来了，以往我会把需求文档粘贴给 Claude Design。

让它输出设计稿之后，再回到 Claude Code 开发，这样来回挺折腾的。

我在 Tutti 里看到一个类似 Claude Design 的应用「产品原型设计应用」。

这次直接在原来的 Claude Code 对话里，@ 了 Tutti 里的「产品原型设计」应用。

再简单说一句话，让它基于刚才的 PRD，先生成一版产品原型。

![image-20260627111401242](https://mmbiz.qpic.cn/sz_mmbiz_png/snxIHWuwQonm1WwCMARbFbvvjaLB8DF8TZETzcWvib3NN5vPMKHolkyAkFSgnd2SrLUmdA6J6KWUGOHPhFoQejCj57WqEO3w2dY5VJFAHSSM/640?wx_fmt=png&from=appmsg)

image-20260627111401242

这里体验比较顺，原型生成后，可以直接在 Tutti 内置的浏览器里预览。

想要修改调整，在对话里继续发送信息即可。

如果想抠细节又不好描述，也可以打开「产品原型设计」应用找到当前任务，直接在设计稿上标注修改。

![image-20260627114149639](https://mmbiz.qpic.cn/sz_mmbiz_png/snxIHWuwQon2BOZQsBu6PcA0nbR6IiaIqfQh7cXiaEXA4iaDzpsz4g8dxslRDib0k3Y7ia2fsnJCFA90HTbZ4FiatWtHNgVKwibzyTTS43X8zJQRHM/640?wx_fmt=png&from=appmsg)

image-20260627114149639

原型确认之后，就开始让 Claude Code 根据设计稿开发了。

因为设计稿已经是这个空间里的产物，Claude Code 可以直接读取它，然后继续搭项目。

这一步省掉了以前很烦的一段流程，下载设计稿或截图、发给 Claude Code，再补一句要按这张图来做，参考风格、参考文字，等等等等。

![image-20260627132653833](https://mmbiz.qpic.cn/sz_mmbiz_png/snxIHWuwQomQPhDdVIwIof9aPGMhXRAf1yxicI4I8FgNeicVjaU9oIkz2mCffcN3QzDHFIwiadgqsRvAPQmKVdzyDdMNVq74tBmGibg9zAq9Mcs/640?wx_fmt=png&from=appmsg)

image-20260627132653833

没多久项目就开发完成了，但有个页面缺少配图，由于 Claude Code 不支持生图，以前解决这问题其实挺麻烦的。

一般需要到网上逐一搜索寻找相关配图，或者用其他 AI 应用，比如 Lovart、Canvas。

费时间不说，还得再来一遍，重新描述一下我的需求。

![image-20260627151940119](https://mmbiz.qpic.cn/sz_mmbiz_png/snxIHWuwQomgPxtuEZ6UGA15Jxa1oSuOwpk9MD1o7BO4aB39xGnbDReyJxGliafLIFrzibIMasQdibuhXc1iaFqVWGKg6iaPSLzSHE7vib4AJ7KJ4/640?wx_fmt=png&from=appmsg)

image-20260627151940119

在 Tutti 里就不用这么麻烦，直接在 Claude Code 的对话框里 @Codex，或者 @AI Canvas 应用就能解决。

这里我直接让它调了 Codex，用 GPT-Image 2 帮我们生成场馆配图，然后顺手把图片加进去，把项目代码给改了。

![image-20260627153309150](https://mmbiz.qpic.cn/mmbiz_png/snxIHWuwQokDNqUTQlrRSntJGEhQl6Uic3Opv5oQ5Fh0oqL5XRIaRuWIzP8O2JUZvxedkcBPeic0QDCUSv23wpHmHPh9Ocmo3EEnAica2gr008/640?wx_fmt=png&from=appmsg)

image-20260627153309150

全程没有重复交代背景，Codex 通过 Claude Code 的调度，直接 Review 了当前项目代码，以及前面我与 Claude 的对话上下文。

就这么简单，只需 @ 一下，就能指挥不同 Agent 完成任务。

![image-20260704175913032](https://mmbiz.qpic.cn/mmbiz_png/snxIHWuwQonCicbmZ0mdXXudb8X4CBeL6U8wmbAZO9ql7pqJ6S8uPMPm7FbQmQgwuYNetnueIXNwZGVzSHfnPxgSlnNFZo5Kg45A944kbO5k/640?wx_fmt=png&from=appmsg)

image-20260704175913032

最后应用跑起来，大概就是这样，能以非常低的时间成本支配不同的 Agent 干活，共同完成一个任务。

### 写在最后

用 Claude Code 梳理需求、写代码，产品原型设计应用输出设计稿，Codex 接手作图改项目。

整条开发链路，各个工具之间调用，没有一次需要重复交代背景，全在一个空间里通过 @ 调度完成。

这也是我觉得最值得关注 Tutti 的地方。

它不是单纯多接了几个 Agent，也不是简单做了一个能把所有 AI 都接进来的桌面。

而是在补充 AI 工具链里容易被忽略的一层，环境层。让 Agent 们能在同一个项目状态、同一个上下文继续工作。

最重要的是，用我们自己订阅的 Claude 或 Codex，没有多花一分钱，这就很爽了。

也许往后，比的不再是谁手里的工具有多强，而是谁能高效协调一堆 Agent 完成任务。

感兴趣的同学，可以到项目的 GitHub 上下载 Tutti 安装包体验看看。

GitHub 项目地址：https://github.com/tutti-os/tutti

今天的分享到此结束，感谢大家抽空阅读，我们下期再见，Respect！

---

## 文章结构分段

1. **问题引入**（开头至"提供了一个很有意思的解决方案"）：多Agent切换时上下文丢失的痛点
2. **产品介绍**（"Tutti 是什么"至"比人转述的那几句充足多了"）：Tutti定位、OS级界面、四打通、@引用机制
3. **上手体验/Demo**（"上手体验"至"共同完成一个任务"）：2026世界杯应用开发全流程演示
4. **总结思考**（"写在最后"至结尾）：环境层价值、订阅复用、趋势判断

## 提取的关键术语/产品名称（10个）

1. **Tutti** - 多Agent实时共享工作空间（核心分析对象）
2. **Claude Code** - Anthropic的AI编程工具
3. **Codex** - OpenAI的AI编程工具
4. **Hermes** - 待支持的Agent（置灰状态）
5. **Gemini** - Google的AI模型（置灰状态）
6. **OpenClaw** - 开源Agent框架（置灰状态）
7. **@引用机制** - Tutti的核心交互方式，用于引用上下文和应用产物
8. **四打通** - 上下文、应用、任务、文件的共享能力
9. **环境层** - Tutti的核心定位，AI工具链中缺失的一层
10. **GPT-Image 2** - OpenAI的图像生成模型
11. **产品原型设计应用** - Tutti内置的垂直应用
12. **AI Canvas** - Tutti内置的生图应用
