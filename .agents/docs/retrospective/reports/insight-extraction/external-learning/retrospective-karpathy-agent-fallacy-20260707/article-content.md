---
id: "retrospective-karpathy-agent-fallacy-20260707-article"
title: "Karpathy：逼Agent干活是AI最大错误（新智元原文）"
source: "https://mp.weixin.qq.com/s/NTwunYHLz8naycDBhFYYKA?from=industrynews&color_scheme=light#rd"
x-toml-ref: "../../../../../../../.meta/toml/.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-karpathy-agent-fallacy-20260707/article-content.toml"
publisher: "新智元"
extracted: "2026-07-07"
extraction_method: "defuddle --md"
---
### 新智元报道

![](https://mmbiz.qpic.cn/sz_mmbiz_png/Rvq8Ow69CYWGxcbmnyYvqrSqhntcbPdelKBG0JLug4pEX8icjBSe5eib6PekswOSvrq8ybatQJRDr9Vib5WOKaUuibKfLb5qH3J4kEIYmC4NQJU/640?wx_fmt=png&from=appmsg)

##### 【新智元导读】Karpathy内部炸场：逼Agent干活是AI最大错误！最前沿不在OpenAI，在你手里。

一句话，把整个Agent圈子浇了个透心凉。

Andrej Karpathy——现Anthropic预训练团队核心研究员，最近在一场面向Agent开发者的现场分享里，甩出一句让全场安静的暴论：

**当前AI领域最大的错误，就是人们急着逼Agent干活，却根本没先把底层的大模型搞明白。**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/Rvq8Ow69CYVDCUSBcc57ibibjHhzzI5BWJ0sDIlDdiaeQFPuLAxZ9paPMCRQBb0DdmTXlUiaffeia3ztR20WZ29rarkoMK7zyicmaR7gNXYcUfMbk/640?wx_fmt=png&from=appmsg)

这段视频被剪出来扔到X上，几天就传疯了。

因为它戳中的，恰恰是眼下最热、最挤、所有人都往里冲的那条赛道。

而说这话的人，不是外行泼冷水，是踩过坑的人在复盘自己的血泪。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/UicQ7HgWiaUb3uEdSPKrwGNmZEOaaGyzVvZ8dTtE9jU1rFsda3llYbCZpmWfiazUYjWBLTGvlPpXucH8Q0lEUJN3Q/640?wx_fmt=png&from=appmsg)

**真金白银烧出来的教训**

把时间拨回到2016年。

那时Karpathy在OpenAI搞一个项目，叫World of Bits，目标听起来特别「2026」：让Agent学会用键盘鼠标操作电脑，去订机票、点外卖，帮你把活干了。

熟不熟悉？这几乎就是今天所有Agent创业公司PPT第一页的画面。

结果呢？没做成。

Karpathy说得很直白：当时他和Tianlin Shi、Jim Fan几个人一起干，对着几个简陋网页疯狂点鼠标、试图订张机票、点份吃的，最后还真在ICML 2017发了篇论文。

论文标题就叫《World of Bits: An Open-Domain Platform for Web-Based Agents》——一个关于「比特世界」的宏大构想，最终困死在了几个简陋网页上。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/Rvq8Ow69CYUibTLF5e115ZIGYeEQypLoQpGQkVRrEtz6hbichS0KT5xdsH6AzsyfrITdxiaUhLIW9LMQBunuKicjEs7vpXqAZWQkyfpQTkX9NDU/640?wx_fmt=png&from=appmsg)

技术没准备好。手里唯一的锤子是强化学习，怎么使劲都砸不出来。

回头看，那时候真正正确的做法，是彻底忘掉Agent，转头去做语言模型。

五年后，工具箱彻底换了——你们现在做Agent，几乎没人再用强化学习了。这在当年，根本无法想象。

有意思的是，当年和他一起写论文的Jim Fan，如今已是NVIDIA的高级研究科学家，搞出了Voyager、MineDojo等一系列炸裂项目，在NeurIPS拿了杰出论文奖。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/Rvq8Ow69CYW3LgERW68fsFeWYbuJQBZiadugvu8o2I4AsmWalR6B4lorp7YGHoPGy5McqRWKiafYqGUuFfAwiblyFTkP9byz9cC5QdPgF2KyBU/640?wx_fmt=png&from=appmsg)

一个2016年的「失败项目」里的年轻实习生，十年后成了AI Agent领域的顶级玩家。

但走的路，不是2016年那条。

**Demo很容易，产品要花十年**

顺着这个教训，Karpathy给了三步忠告，句句反着当下的热潮来。

**第一步，别再逼你的Agent什么都干，先把底层模型做对。**

今年5月他加入Anthropic预训练团队时，在X上写的第一句话就是：我认为接下来几年LLM前沿的工作将尤为关键。

![](https://mmbiz.qpic.cn/mmbiz_png/Rvq8Ow69CYUAN62nMDea6CN5icoU0vwCUfpr6yNjDOibhvgKH33smH89FVTfFRxQukdgWcwtz7JX0srmkNUPJ2vrt9Yh2YQZotJvmaAvt4daw/640?wx_fmt=png&from=appmsg)

一个「发明」了vibe coding、让Collins辞典把它评为年度词汇的人，此刻选择回到最底层的预训练研究——这本身就是对Agent热潮的一记「行为投票」。

**第二步，Demo很容易，把它做成产品要花十年。**

他搬出两个所有人都熟的例子：自动驾驶，让一辆车绕着街区跑一圈的Demo谁都能做，可真做成产品，用了整整十年，他自己在Tesla就亲历了这场马拉松。

VR也一样，惊艳的Demo满天飞，落地成产品同样是十年起步。

Agent，就是这一类。

极容易想象、极容易做Demo，却极难做成真正的产品。

你要真入这行，就得准备好干十年，而不是做完一个炫酷Demo就以为上岸了。

**第三步，Agent不是产品，基础能力才是产品。** 把地基打牢，Agent会自然涌现出来。

这三句话，几乎把当下「套个壳、堆个Agent、赶紧发布」的玩法，做了彻头彻尾的否定。

Karpathy的意思很清楚，地基不牢，楼盖得越快，塌得越狠。

自动驾驶已经用十年替所有人验证过一遍了，Agent没有理由能跳过这一课。

![](https://mmbiz.qpic.cn/mmbiz_png/Rvq8Ow69CYViayicLuJUeSibia1Ssf4fuicvOBXibSGJt99Sr2SicVBCiaSTM6odfbWGvWI4e2mA8JhLtj9worlibsia8tTQUWmjm3NWwOy6c3dqIksko/640?wx_fmt=png&from=appmsg)

**向大脑偷师**

说完教训，Karpathy话锋一转，一头扎进神经科学找灵感。

他在台上抛出一连串问题：Agent里什么东西相当于海马体，负责记忆、索引和检索？

什么相当于基底神经节，控制行为选择和动作执行？什么相当于丘脑，那个「多个念头抢麦克风」、像意识之座一样的地方？

一个顶级AI研究者在说：我们造数字生命，眼下最缺的不是更花哨的功能，而是对「智能到底是什么」这个根问题的敬畏。

他甚至专门带了一本David Eagleman的神经科学著作《Brain and Behavior: A Cognitive Neuroscience Perspective》推荐给在场所有人。

![](https://mmbiz.qpic.cn/mmbiz_png/Rvq8Ow69CYVh8Ip9a4qvNyEmwRyMp0y4qs4ZtZ0yYuT3PWia1q1TxdbgeajhrPMr51L28hX5EeCyFDyibtnH6QbRiat1VDKQwfurdGPrAINc6w/640?wx_fmt=png&from=appmsg)

在他看来，今天造Agent，值得像深度学习早期那样——当年我们从单个神经元的结构里偷来了人工神经网络的灵感，如今完全可以再去大脑里偷一次。

**真正炸场的，是最后这句**

如果说前面是泼冷水，Karpathy的结尾，又给台下点了一把火。

他对着满屋子独立开发者和创业者说：

**真正站在Agent能力最前沿的，是你们。不是OpenAI，不是DeepMind，是你们。**

这不是场面上的客套。他给了一个特别扎心的解释：

像OpenAI这样的大厂，训练大规模Transformer语言模型的确无人能及——一篇新的Transformer训练论文出来，内部Slack里的反应往往是「哦，这个两年半前有人试过了，为什么没成，我们门儿清」。

可一旦一篇新的Agent论文冒出来，所有人的反应却是：「哦，这真酷，真新颖。」

为什么？ **因为在Agent这件事上，没有任何一家大厂积累了五年。**

大厂并不站在能力的边缘，而你们——创业者、黑客——才站在那条边缘上。

道理其实不难懂。

大厂在语言模型这条路上跑了这么多年，早把每一个坑都踩遍、每一条弯路都标好；可Agent是一片刚被开垦的新大陆，谁都没有五年的先发家底，大家几乎站在同一条起跑线上。

这时候，灵活、敢试、能快速调头的独立开发者，反而比船大难掉头的巨头更有机会撞出新东西。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/UicQ7HgWiaUb3uEdSPKrwGNmZEOaaGyzVvZ8dTtE9jU1rFsda3llYbCZpmWfiazUYjWBLTGvlPpXucH8Q0lEUJN3Q/640?wx_fmt=png&from=appmsg)

**回到那句最初的暴论**

Karpathy要泼的冷水，不是「别做Agent」，而是「别跳过基础去做Agent」。

他自己就是最好的注脚——这位发明了vibe coding、把Agent用到飞起的人，在2026年最重要的职业选择却是：回到预训练，回到大模型最底层的那间实验室。

他要点的火，也不是让人焦虑，而是告诉每一个正在一线折腾的人：这场仗，你并不落后，你就在最前面。

热潮总会退去，Demo也终会褪色。

但把底层模型吃透、愿意为一件事扎进去十年的人，才配站到十年之后的岸上。

参考资料：https://x.com/0xCodila/status/2073544407643496771

编辑：所罗门
