冷逸 冷逸

在小说阅读器读本章

去阅读

大家好，我是冷逸。

昨天，看到腾讯混元发布了Hy3正式版。295B参数规模（激活21B），Moe架构，开源。

官方说，相比Preview版本，Hy3正式版在Agent与Coding能力上有大幅提升。并且针对WorkBuddy做了专门的适配与优化，在WorkBuddy上使用效果最佳。

目前，模型已在WorkBuddy上线，最近两周使用都是免费的。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/H9yPeQXaIQgCv20cgfYlMYNLtAqvKIxz4OrfyKj9S4YyOSlU1az6M2qIr76iaxTia3CSibLaegK8EicVQl1M5oD6T6ASoBiciaXMU27xdW4aMb9WA/640?wx_fmt=png&from=appmsg)

为了摸清它的真实能力与边界，我拉来了DeepSeek-v4-pro和glm5.2，三个模型一起做了期横评：统一任务类型、统一提示词、统一评分标准，全部走API在Claude Code / WorkBuddy里实跑一遍。

一共 6 个任务，覆盖3D编程、前端设计、网站开发、游戏开发、Agent长程任务和内容写作等场景。

![](https://mmbiz.qpic.cn/mmbiz_jpg/NX4HOlP6ibCicV1QppcudDqHNibe1FiaSiaXvic8DcjbZP6CtUD7nHjdLA0fB0eibP1sbkJBqTVafECcdFc416I0ia2VHw/640?wx_fmt=jpeg&from=appmsg)

一手横评

测评原则依旧是：变量归一，对比才有意义。

三个模型用同一份素材、同一条提示词，分别接各家API在Claude Code / WorkBuddy里测，最终从「任务完成度」和「输出质量」两个维度来评价。

1）3D任务

3D任务依旧是我们的3D魔方，主要考验模型的逻辑推理和建模细节。

> 提示词：Create a single HTML file containing a fully functional 3D Rubik's Cube simulation using Three.js (via CDN). The cube must be able to automatically solve itself.
> 
> 中文：创建一个HTML文件，其中使用Three.js（通过CDN方式引入）来实现一个功能完备的3D魔方模拟程序。该魔方必须能够自动完成自己的“解谜”过程。

DeepSeek-v4-pro：

![](https://mmbiz.qpic.cn/sz_mmbiz_gif/H9yPeQXaIQj2ZZM8t0ahYCrI5TVyUoEjjKb1VS4jNAHvI1O8FAe0oLOnV48Vibd2vxn1LN09aqq1vClHpMoU6G0b3ibcIO4ibGXXd3LS381WZ4/640?wx_fmt=gif&from=appmsg)

Hy3：

![](https://mmbiz.qpic.cn/mmbiz_gif/H9yPeQXaIQjoh3fNVmp6NcvXyBN9Z0Zhh6JKtIy5x6UlOIQNxZ3X805zrM0bMIK6gIqklwNJdDXqzTRFN9vGAK2k9bbwNAQ1zRib6OJggxSU/640?wx_fmt=gif&from=appmsg)

GLM-5.2：

![](https://mmbiz.qpic.cn/mmbiz_gif/H9yPeQXaIQgxLcGexncib1bPwWiab0dxDbUia1CkNwlgQSP2icAibviaW5cfP9qYicHeuuYtH3zrBEdU0USQYnMdTdyibf6S6Abh6pUD8LM94Fmicz34/640?wx_fmt=gif&from=appmsg)

三个模型都能把运算逻辑算对，能打乱、也能还原（逆向计算），推理能力都过关。

但在建模的阴影细节、色彩搭配和功能丰富度上，GLM-5.2更胜一筹，整体更有高级感。DeepSeek-v4-pro和Hy3要糙一些，尤其是DeepSeek-v4-pro，建模质量垫底，空间表现上甚至还有一些bug。

本轮实测：GLM-5.2 > Hy3 > DeepSeek-v4-pro。

2）小游戏开发

这轮任务的提示词极其简单，就一句话。刚好Claude Code和WorkBuddy都是带loop的Agent，我只给一个goal，看各个模型的自我规划与执行能力。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/H9yPeQXaIQiaLNskGqibln9VP4mkPnTJicNEx1NE1wlrwrkbvCPfva643e8ibnUgWbd6oBAyK0baeHGl472smR9DZ2n875ic1bbc9SPlX2wMosDo/640?wx_fmt=png&from=appmsg)

DeepSeek-v4-pro：

![](https://mmbiz.qpic.cn/mmbiz_gif/H9yPeQXaIQiaR1mB6AdgTia8xaGvWNWGkolrb9e410t8XRSuxwjnIsZFXRLFybJnjraQFeRrUc4YUFzGQcCHXtWc36vF8Z8LxJgazGWFaiaseM/640?wx_fmt=gif&from=appmsg)

Hy3：

![](https://mmbiz.qpic.cn/sz_mmbiz_gif/H9yPeQXaIQgJ7zFW4ECZlNtfWR6SKXrmNow4fhSNvEuZPHQcAlZEicWvQFCD8RtLusSZVpjE6SvdG0VDAMPIclh5uGjXIAdBUKD4eHMbCL20/640?wx_fmt=gif&from=appmsg)

GLM-5.2：

![](https://mmbiz.qpic.cn/mmbiz_gif/H9yPeQXaIQhBOjJ9PX0q95KTlJ1KSrEDXic3QMU6wveKhYIPgqViak4W9lC0BV46Ze9gsfoKpMv0x47MW3viahy46TJibbmjskQ1ibUeL4icclXDs/640?wx_fmt=gif&from=appmsg)

这一轮one-shot情况下，我认为表现最好的是Hy3。

另外两个模型生成的小游戏，不二次修改基本都玩不了：DeepSeek的水果弹跳高度设计不合理，用鼠标几乎切不到水果；GLM则是水果太小、出现速度太快，同样很难划到。

真正能玩的，只有Hy3生成的版本。它的抛物线物理设计，能保证水果飞到屏幕62%~90%的高度，轻松就能被划到。

本轮实测：Hy3 > GLM-5.2 > DeepSeek-v4-pro。

3）前端任务

让各模型用HTML写一台电子鼓机模拟器。

> 提示词：使用Web Audio API创建一个16步的鼓机模拟器，提供前卫、时尚的电子音乐体验，只输出一个单HTML文件，集成合成鼓声、实时Glitch音效等，中文界面。

DeepSeek-v4-pro：

Hy3：

GLM-5.2：

整体来看，这轮无疑是GLM-5.2表现最佳。另外两个模型做的电子鼓机都不太对，很难调出好听的音乐；GLM-5.2 生成的鼓机，随便调都能出片。

Hy3的界面设计得不错，能看出有前端审美在里头，只是鼓机的声音设计还需提升。DeepSeek的鼓机，前端不好看，配乐也不对。

本轮实测：GLM-5.2 > Hy3 > DeepSeek-v4-pro。

4）网站开发

网站开发，还是我们的老case，给「冷同学的院子」设计一个官网。

和之前的横评一样，提示词一字未改。

```
给这家民宿设计一个官方网站。

民宿的基本信息：
- 民宿名称：冷同学的院子
- Slogan：云朵上的院子，冷同学的家
- 地理位置：四川汶川（羌族文化核心区、高山峡谷地带）
- 品牌调性关键词：温暖治愈 · 在地羌韵 · 自然松弛 · 外冷内热 · 有故事感
- 目标客群：追求慢生活的年轻人、亲子家庭、文化旅行者、成都周末度假客、川西旅游爱好者

文件夹【民宿资料包】放着很多民宿的素材，有logo、门店、房间、周边和宣传视频，你自己决定用哪些素材（不是所有素材都用上）。我只需要最终交付的网站顶级审美，让人看了就想马上去玩。
```

DeepSeek-v4-pro：

![](https://mmbiz.qpic.cn/mmbiz_png/H9yPeQXaIQhZK4EMvmtjDQjCQ2UBWoEb0dHh6AGUwVWWkcgjMqVKd5lMsjYsfPGyyEsqDH2icq80GTDlsgRwIjEs7HjdfPB8ib3N79xFuI8cI/640?wx_fmt=png&from=appmsg)

**（可上下滑动，查看全图）**

Hy3：

GLM-5.2：

这个任务带了一堆图片和视频素材，如果是具备VLM能力的模型来测会占优。但恰好这三个模型都没有VLM能力，所以算是公平竞争。

最终效果上，这轮表现最好的是GLM-5.2，做的网站确实更好看、更有品味。Hy3设计得也不错，只是首屏Hero区和页面丰富度上差GLM-5.2一点，房型卡片展示上也有排版错乱的问题。

u1s1，腾讯混元的前端能力确实好起来了，比之前的版本强很多。

![](https://mmbiz.qpic.cn/mmbiz_png/H9yPeQXaIQg9QoKMjNHXuQyXXKsmEHrqUaYGwO31LdhDkzbJ9OHumJdHl2m9C3G16uibmlTCa0ELZVVx37ea7UZlR3NkMGL3icahSvyWj8A1M/640?wx_fmt=png&from=appmsg)

DeepSeek在这轮里中规中矩，垫底。

本轮实测：GLM-5.2 > Hy3 > DeepSeek-v4-pro。

5）Agent长程任务

这个case的链路非常复杂，特别考验模型的工具调用和在长链路下的上下文管理问题，需要模型借助Agent完成「联网搜索 + Word生成 + Excel 生成 + Skill 调用 + 网站开发」的一连串复杂任务。

提示词是：

> 联网检索腾讯2025年的关键财报信息，构建腾讯的营收模型，读取权威研报内容，合理假设，基于最新的信息对腾讯营收建模，分别出一份Word研究报告和Excel图表，然后调用guizang-ppt-skill生成10页PPT。

先看各模型交付的产物，都是3份：Excel建模、Word研报、HTML式PPT。

DeepSeek-v4-pro：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/H9yPeQXaIQjdCXPAicjDjYaib2GrxZictdBw2taHhFcaJ71C6fAHVA5a4aLCgW9hrr1Xj5ykLuHw8qSNJq9njtQKmv7c6oyFepDfOR8T7MeDFo/640?wx_fmt=png&from=appmsg) ![](https://mmbiz.qpic.cn/mmbiz_png/H9yPeQXaIQiaFDGh4ccoDarnR2P29Niclb9TbK1xcQ1zYjtgia1JLP2FolT9hCbdKbCDpfUzM3RxAEMy52VqMFJ6sgZUpQM0ib7WcDVRelIR85A/640?wx_fmt=png&from=appmsg)

**（可上下滑动，查看全图）**

![](https://mmbiz.qpic.cn/mmbiz_gif/H9yPeQXaIQjYf4g6zJqxqnfHy1Mh9rHOfX6ecxIpcj3o3BnItvt2krzTBr9X3SAWufI6cLf7L7HtMEMvWpKuic4iaSz1S1cQJmqg6jGWnwYy4/640?wx_fmt=gif&from=appmsg)

Hy3：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/H9yPeQXaIQhmvboxKK0l95JQ7mup5OiavfmkEFXOsdc8yoiavQBQgFkCxMxLwgrBRGfFLc9hfxmQM23qnshx2PqBsYH9Iw7Sia5MbLon91VQys/640?wx_fmt=png&from=appmsg) ![](https://mmbiz.qpic.cn/sz_mmbiz_png/H9yPeQXaIQiabIwk6kvwDS0K2jbmeBkGnGKD9RzMeqBSQHiaWfhKXs0sKd45EN13HSA4NKFAscEnQExwIZBpfvUIthV2NQGElKNPib9w69GPL8/640?wx_fmt=png&from=appmsg)

**（可上下滑动，查看全图）**

![](https://mmbiz.qpic.cn/mmbiz_gif/H9yPeQXaIQgNr5gFGBobkDQU5000z28vnC79BlARoqeLgarBqJNoSicKUR0Mlib1RNuvlM25mU6Fcicce13bjPyht1OWjjIKOIRvS5CUr2iaJ7U/640?wx_fmt=gif&from=appmsg)

GLM-5.2：

![](https://mmbiz.qpic.cn/mmbiz_png/H9yPeQXaIQiaZBuElY6zY6M8iaO5ZJKYYWeed3ByEL6SJzc9AO9hBcFIXz85umuAm2e4hjz1y6pt26HzOEkYeAGnpd0QKnjneAsCTLRfhNSPI/640?wx_fmt=png&from=appmsg) ![](https://mmbiz.qpic.cn/sz_mmbiz_png/H9yPeQXaIQj6K9PkVO0qGBduAGLVJD1Q29MA4PZvEL4ua4OJqfsQPo40zichsLRuWAHXiaxCJWaQIsiap04LrOdskQe9XibMpj4AG6VcFf4ib9TE/640?wx_fmt=png&from=appmsg)

**（可上下滑动，查看全图）**

![](https://mmbiz.qpic.cn/sz_mmbiz_gif/H9yPeQXaIQhfPmPvhO7zK7VM6pYpE3PAQXgFQXCgib4mELIRibROqumz8yP1GrHUDK20ZHr8PGwtmicFRSH2BN3A6frUg6Gv9zdpEMiaYPkKV48/640?wx_fmt=gif&from=appmsg)

这个任务的难点在「长链路」，要求模型在多次工具调用下，始终保持上下文连贯、指令不漂移，对模型的长程稳定性和工具协调能力要求很高。

而且，它不是让模型联网收集信息再做个总结，而是要求它有自己的预测、推理和判断。

先说 Excel 估值建模：无论数据丰富性、准确性、逻辑性还是图表质量，DeepSeek的表现都更好一些；Hy3次之，但分析偏少；GLM看起来只是做了检索，没有自己的分析。

![](https://mmbiz.qpic.cn/mmbiz_gif/H9yPeQXaIQiaUheLMevOfl4kiaIvYHsvT1gSjboeCYx4lBdYMoXksPHYev7EbPpLVTo3PeVRNpscTx3ibtnXpB6ZPYfOeNv3Oia4bcLfNzNNrrw/640?wx_fmt=gif&from=appmsg)

DeepSeek-v4-pro的Excel建模

再说Word研报：评价基本和Excel一致，DeepSeek质量最好，有完整的分析过程；Hy3和GLM更像是汇总了分析师观点，缺少自己的分析。

最后看 PPT 完成度：三个模型都交付了质量不错的 PPT。DeepSeek加入了真实图表数据；Hy3和GLM-5.2每页都有微动画，都用的是瑞士国际主义风格。

不过有个独立问题值得单独说：GLM-5.2生成的PPT，第一次打开竟然是空白，让Claude Code重新修复后才正常打开。大概率是上下文又被干爆了。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/H9yPeQXaIQglgpeSgLwwdoobavyppPjIhhaPhiadTzSQPL2gu01bXNhtKBau4bJL6kqoY1qPsW32mAajntQCKrH6js52QSmtCQu9yWmjoSgk/640?wx_fmt=png&from=appmsg)

我去查了下日志，果然如此，它交付的时候，上下文已经用到了99%。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/H9yPeQXaIQiah6IAVoiaQIpuWs4XuKOj9fQrSdfMM8X6scic47o7ibEMqf1WrKAgFcEzicOicDpBSibhK9k2go46icaXzNHxlb9CYEmw1vxSaqWeZPo/640?wx_fmt=png&from=appmsg)

本轮实测：DeepSeek-v4-pro > Hy3 > GLM-5.2。

6）写作任务

昨晚偶然翻到一篇我十二年前写的文章，没想到那时还挺文绉绉的。我觉得适合拉来做横评，让模型基于我的文风续写。

![](https://mmbiz.qpic.cn/mmbiz_png/H9yPeQXaIQjwjjGXh3gD66WVABgicuDTeP7yAplfAEJAIhViaEicbYKN7ibiaswgrliaIk8cGClIA0LtvQHfsf2JR7lF1ia2UbvrZXcyia5pSL6NAVE/640?wx_fmt=png&from=appmsg)

初始文章：

十点下班，和康君打车到北门，下车后我便准备坐公交回家。康说“你去学校坐校车吧，快一点”。我便转头向北门走去，进了校门，很显目的八字题石碑进入眼前，“海纳百川，大道致远”。向前走去，准备在十字路口处等车。等了七八分钟还是不见校车，心生疑虑“莫非现在的时间点校车已经停运了？”先不等车了，让我好好感受下大学的气质吧。

路上来往学子不多，想来现在已经十一点了，差不多应该都就寝了吧，况且明早儿还得早起上课呢。不禁想到我大学时，楼管还停我们电，竟是这般可恶。在没电的情况下什么事都干不成，只能躺在床上期望窗外一丝轻风袭来，让我们的汗流不至于浃背，就这样一趟就是一整晚，人是睡着了，风却没有来。

借着淡淡的柔光，走在清新的小道上，和煦的夏风吹来，夹杂着春天泥土的芬芳，这味实在是美妙极了。不远处，望去，有情侣在调侃，有学子在看书。来到了这里，给你的直觉就是——这里是校园，不是外面的社会。我很喜欢这样的小社会，喜欢这个校园社会，不喜欢那个人烟繁杂的大社会。难怪老子先生那么追求小国寡民的封闭型社会，人人心目中都有一个乌托邦，都在努力寻找那个桃花源。

来看下各个模型写的内容。

DeepSeek-v4-pro：

我继续向前走去，脚步不自觉地放轻了，生怕惊扰了这片刻的安宁。路灯将树影拉得细长，斑驳地洒在水泥路面上，像是谁随手写下的 草书，潦草却有意境。远处教学楼的灯火稀疏着，几扇亮着的窗户里，大概还有人在为论文或考试熬着夜。我忽然有些羡慕他们，羡慕 他们仍处在一个人可以说"我在读书"的年纪，仿佛这四个字本身就自带一种豁免权——不必立刻去面对那些复杂的人际关系、权衡的利益、说不出口的妥协。

走到湖边，水面静得几乎没有波纹，倒映着岸边的路灯和树影，像一面被时间遗忘的镜子。我在长椅上坐下，夏夜的蝉鸣已不似盛夏时 那般聒噪，反倒成了背景里一层温柔的底色。我想起刚毕业那会儿，也是这般坐在校园的长椅上，满心以为只要走出校门，便是广阔天地、大有所为。可真正走进那个"大社会"之后才发现，广阔有时候也意味着空旷，自由有时候不过是另一种形式的漂泊。

校园真好。它用围墙把一些东西隔在了外面，又用青春把一些东西留在了里面。这里的人说话可以慢半拍，走路可以不看手机，谈恋爱 可以在路灯下站很久。这种"慢"在外面是奢侈的，在这里却是日常。我终于有些理解，为什么人在经历了社会的打磨之后，总会怀念校 园——怀念的其实不是某栋楼某条路，而是那种还能相信"努力就有回报""真心能换真心"的单纯氛围。

手机忽然震动，是康君发来的消息："到家了吗？"我这才回过神来，起身拍了拍裤子上的灰。校车大概是等不到了，也好，这一趟夜行便算是我偷偷借来的时光。走出北门的时候，我忍不住又回头看了一眼。八字题石碑在夜色里沉默着，像一位不善言辞的老者。我转身汇入街灯下的车流与人潮，心里知道，那个桃花源还在那里，只是我不能再久留了。

Hy3：

我顺着小道继续往里走，不觉已到了水池边。水面静得出奇，月色铺了一层薄银，偶有鱼儿翻了身，涟漪便把那轮月揉碎了又慢慢拼好。池畔几盏老路灯昏黄着，像是舍不得睡去，固执地守着这一方安静。

忽又想起白日里城市的模样——地铁里挤作一团的人、写字楼彻夜不熄的灯、手机里永远回不完的消息。那样的世界总逼着人往前跑，跑得喘不上气，却不知要跑到哪里去。而此处，连时间都仿佛慢了半拍。原来所谓桃花源，未必在远山深谷，也可在这几步之遥的围墙之内，只要你肯停下脚步。

不远处自习室还亮着几扇窗，影影绰绰有人伏案。他们大约也在为明日的事忧心，却至少忧心得这样体面、这样干净。我竟有些羡慕了。我们总说长大是失去，失去的或许正是这份"只需操心一纸试卷"的纯粹——彼时烦恼很小，天地却很大。

风又起，吹得池边柳条轻摆，像谁在低声絮语。我站了许久，忽然听见远处一声引擎响——是校车，竟晚了一班。它缓缓停在我面前，车门打开，暖黄的灯泻出来。

我上了车，回头望了一眼那八字石碑：海纳百川，大道致远。车开出校门，城市的灯火便扑面而来。我知道那方桃花源还在身后，而我，总要回到人烟繁杂里去。只是今夜，心里多了半分清凉，够我撑过许多个闷热的白日了。

GLM-5.2：

过了十字路口，路灯便稀疏起来，只有远处的教学楼还亮着几扇窗。我放慢脚步，不忍惊扰这夜的静谧。树影在地上晃着，像是谁随手 泼下的淡墨，风一吹，又晕开几分。草地里虫声唧唧，细听竟也有章法，仿佛在合奏一曲无人喝彩的夏夜小调。

我循着石板路往深处走，路过图书馆时，看见顶层还有一盏灯孤零零地亮着。那光白得清冷，却让人心头一暖——想必又是哪个孩子在赶论文吧。曾几何时，我也在这样的深夜里抱着电脑，对着空白的文档发呆，把咖啡一杯杯灌进肚里，把青春一段段写进脚注。那时总觉 得未来遥远得像窗外的星空，如今站在星空下，才发觉那些熬过的夜、发过的呆，早已成了生命里最柔软的衬底。

操场边的看台沉默地卧着，白日里的喧闹此刻全收了声。我拾级而上，找了处干净的地方坐下。远处的海面隐没在夜色中，只听得见潮水一波波推上岸，又退下去，像某种亘古不变的叹息。海风比刚才又凉了一些，带着咸涩，把额前的汗意慢慢吹干。

我忽然觉得，人这一辈子，不过是在门之间穿梭。从家门到校门，从校门到社会的门，每一扇门都开着，每一扇门也都关着。校园里的人想出去，外面的人偶尔又想回来。 可真正让人眷恋的，或许不是某一道门，而是门与门之间那段可以慢慢走、慢慢想的路。

又一辆校车从远处驶来，车灯切开了夜色。我起身拍了拍裤子上的灰，朝站台走去。车停稳，门开，我跨上去，把这一夜的校园轻轻关在身后。车窗外的路灯连成一条细线，像谁写下的未完待续。

我原本以为DeepSeek会在这轮测试中占优，没想到一轮横测下来，表现最好的居然是Hy3。这个文字读起来是真的舒服，有人味儿，终于不是“稳稳接住你”的那个味儿了。

而且，它是有灵魂的，不只是浮躁词汇的堆砌。我决定，把后续所有写作工作流都换成Hy3。

这轮实测：Hy3 ＞ DeepSeek-v4-pro ＞ GLM-5.2。

![](https://mmbiz.qpic.cn/mmbiz_jpg/NX4HOlP6ibCicV1QppcudDqHNibe1FiaSiaXvchrPAK3S9ibJjY6ibrzfXP6eUeh1IhG5DzGiaatTn9k3XGl1vebRJm43Q/640?wx_fmt=jpeg&from=appmsg)

写在最后

整体测下来，我觉得Hy3的综合能力不差。

Coding方面，glm-5.2依然是国产标杆。Hy3大概是智谱上代模型glm5.1的水准，部分场景甚至超过DeepSeek-v4-pro，而且它的前端表现还挺不错。如果混元能够在VLM上补齐短板，它的Coding能力还能再上一个台阶。

Agentic方面，三家都挺能打。有点意外的是DeepSeek——上次横测时它对Claude Code的适应还非常差，能明显看出DeepSeek团队最近在Agent上做了大量优化。GLM则是「想得太深」，虽然有1M上下文窗口，长任务却很容易把上下文撑爆，耗时基本是Hy3和DeepSeek的两倍以上。

Hy3我本以为会在Agent上有所不足，没想到一轮测下来表现还挺稳。虽然只有256k上下文窗口，但配合WorkBuddy还是能「稳稳接住」我的实测；第五个任务它只花了10分钟，是三个模型里效率最高的。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/H9yPeQXaIQjlFyDAyV8x79rEof5fXo64CiaYpJJ58lfogsn6DwpPL0ZzGVSEyPkOLbkBgvGZb0BibmOibhjZr8AicHKg3lA2cjYKjHUKH5kdxlY/640?wx_fmt=png&from=appmsg)

最后是价格。国产模型在这方面都挺有性价比的，而且也都开源。基本上，现在全球的开源模型就看中国了。

非要挑最便宜的话，目前Hy3输入1元（命中缓存0.25元）、输出4元，是最便宜的，比DeepSeek还便宜。

![](https://mmbiz.qpic.cn/mmbiz_png/H9yPeQXaIQjy4NoLGCAyd8YahBQy3OG7miaXmPXIt2nBcOwpZsOm4El9lCn61Cxc0gTpuCiaiaaia2pSSN1pykG3thP8q0Ok2C2d7hZozO1wbHs/640?wx_fmt=png&from=appmsg)

对了，如果你在WorkBuddy上用的话，最近这两周是免费的。

欢迎大家去体验。用完后，回来评论区告诉我效果如何。

微信扫一扫  
使用小程序

： ， ， ， ， ， ， ， ， ， ， ， ， 。 视频 小程序 赞 ，轻点两下取消赞 在看 ，轻点两下取消在看 分享 留言 收藏 听过