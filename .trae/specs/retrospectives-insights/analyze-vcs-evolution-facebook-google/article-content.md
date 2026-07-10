---
title: "为什么Facebook和Google都\"抛弃\"了Git？"
source_url: "https://mp.weixin.qq.com/s/dULZehqx6-dU1mAgYW9RJA"
type: "技术史科普"
topic: "版本控制系统演进、Monorepo、Git、Mercurial、Sapling、Piper"
extracted_at: "2026-07-09"
---

liuxin liuxin

在小说阅读器读本章

去阅读

**0** **1**

**两个软件同时诞生**

2005 年 4 月，一场意外让整个 Linux 社区措手不及。

BitKeeper的作者Larry发现有人违反协议，对他的宝贝软件 BitKeeper 进行逆向工程，一怒之下撤销了 Linux 社区的免费使用许可。

Linux 瞬间陷入了没有源码管理系统可用的困境！

这件事彻底改变了版本控制系统的发展历史。一方面，Linus Torvalds不得不暂停内核管理工作，亲自开发 Git。

另一方面，几周后，Olivia Mackall 发布了自己开发的 Mercurial 0.1。

![图片](https://mmbiz.qpic.cn/mmbiz_png/KyXfCrME6UJyiaZ08rtdvrjFrX7JWMvZcbBd5MiaKicbTj3hxIHGMMIpD4PVCGW0MtnriaiaTOxMkXqN29nHEH7d4jQ/640?wx_fmt=png&amp;from=appmsg&amp;tp=webp&amp;wxfrom=5&amp;wx_lazy=1#imgIndex=0)

这是一款与 Git 一样采用分布式架构、强调可扩展性的版本控制系统。

Git 和 Mercurial 几乎是在同一时间起跑。

不过，凭借 Linux 的巨大影响力，再加上 Git 本身出色的设计，它很快成为主流选择，越来越多的互联网公司开始采用 Git，其中就包括 Facebook。

随着业务高速扩张，Facebook 的代码规模也迎来了爆炸式增长。仅 2013 年一年，代码仓库就新增了 4.4 万个文件、1700 万行代码，规模甚至超过了当时的 Linux 内核。

要命的是， Facebook 和 Google 一样，采用了 Monorepo（单一代码库）策略：公司几乎所有项目都放在同一个代码仓库中！

这听起来有点疯狂，但 Monorepo 的好处非常明显：

(1) 所有代码统一进行版本管理，不用为跨仓库同步代码、合并共享库而头疼。

(2) 不同团队可以方便地共享和复用代码，避免重复造轮子。

(3) 依赖关系集中管理，升级和维护更加简单。

(4) 跨团队协作成本大幅降低

**0** **2**

**Facebook决定抛弃Git**

Monorepo 带来便利的同时，Git 的性能开始成为 Facebook 工程师最头疼的问题。

Facebook工程师们根据业务增长速度，模拟了未来几年的代码库规模，做了一些测试。

结果令人震惊：一些最基本的 Git 命令，执行一次竟然需要 45 分钟。

如果继续这样发展，整个研发体系都会被拖垮。

Facebook 立即成立了专门的团队，开始寻找解决方案。

第一站，他们找到了 Git 社区。

Facebook 希望和 Git 维护者一起优化 Git，让它能够支撑这种超大型 Monorepo。

然而得到的回复却很直接：不是 Git 有问题，而是你们的代码库太大了，应该拆分。

站在 Git 社区的角度，这并不难理解。

当时几乎没有公司会把数千个项目全部放进一个仓库，Facebook的场景过于特殊，社区自然没有动力为了极少数用户重构 Git 的底层架构。

Git 这条路走不通，Facebook 又把目光投向了商业软件 Perforce。

Perforce 是版本控制领域的老牌玩家，成立于 1995 年，Google、Salesforce、Netflix、SAP、迪士尼等众多大型企业都曾是它的客户，在游戏行业更是事实上的标准。

可深入评估后，Facebook 发现 Perforce 在本地一致性方面存在缺陷，而 Perforce 官方并不认为这是需要优先解决的问题。

于是，这条路也被放弃了。

就在大家一筹莫展时，一位长期使用 Mercurial 的工程师提出了一个建议：

为什么不试试 Mercurial？

相比 Git，Mercurial 的代码结构更加清晰，采用 Python 编写，拥有良好的面向对象设计，也更容易扩展。

对于 Facebook 这样拥有数百万文件的仓库来说，一个最大的性能瓶颈，就是判断哪些文件发生了变化。

Git 的做法是遍历整个工作区，文件越多，速度越慢。

而 Facebook 内部恰好有一个工具 Watchman，能够实时监听文件变化。

由于 Mercurial 的架构足够灵活，工程师很快就把 Watchman 集成进去，查看文件状态的速度一下子提升了 5 倍以上。

Mercurial 还提供了一个名为 filelog 的抽象，Facebook 又基于它开发了 remotefilelog 扩展，把大量历史数据放到服务器端，需要时再按需下载。

结果，超大仓库的 clone 和 pull 速度提升了 10 倍以上，原本需要几分钟的操作，被缩短到了几秒钟！

如果说 remotefilelog 是在版本控制软件级别实现了文件的按需下载，那么 EdenFS 就是Facebook更进一步，在操作系统级别实现的终极黑科技。

它是个虚拟文件系统，让你的代码仓库看起来像在本地，其实文件是用到才生成/下载。

Mercurial 社区为了支持 Facebook，也愿意修改底层架构，接受大量新的设计。

而 Facebook 也没有只是"提需求"，在一年半时间里，他们向 Mercurial 提交了 500 多个补丁，包括新的图算法、用 C 重写性能关键路径、优化存储结构等。

这与当时 Git 社区"建议拆库"的态度，形成了鲜明对比。

最终，Facebook从Mercurial 分叉，把remotefilelog，EdenFS,Stacked Commits等技术整合起来，又重新设计了开发者交互层（UI/CLI体验），从而创建了新的版本控制系统：Sapling。

![Sapling Meta](https://mmbiz.qpic.cn/mmbiz_png/Armv0pa9c8heCR5Pz4ibr1ibj3q4cOhFgic4skBSkR9yml8EnAUQXicash2FHg3uCnORQnN60Ecmias4B8xBFBxqGMObfo8G9GnbfOQwHArWjBBE/640?wx_fmt=png&amp;from=appmsg)

**0** **3**

**Google 发明新轮子**

如果说 Facebook 把 Git 推到了极限，那么 Google 从一开始，就走上了另一条路。

Google 的代码库，比 Facebook 还要夸张，截至 2015 年，它已经拥有 20 亿行代码，占用 86TB 存储空间。除了 Chrome 和 Android，Google 几乎所有产品的源码都放在同一个代码库中。

数字没有直观感觉，看个图吧：Windows，Office等常见软件在中间，Google代码库是最下方的绿色方块。

![图片](https://mmbiz.qpic.cn/mmbiz_png/KyXfCrME6UJyiaZ08rtdvrjFrX7JWMvZclu5Crer9poxH6JDJdc11s6Gk45z4YVUlnGMR0lOJvY4LRgYVgsW8nw/640?wx_fmt=png&amp;from=appmsg&amp;tp=webp&amp;wxfrom=5&amp;wx_lazy=1#imgIndex=5)

如此庞大的代码库，已经远远超出了当时主流版本控制系统的设计范围。

创业初期，Google 和很多公司一样，直接选择了商业版本控制系统 Perforce。

但随着业务不断增长，Perforce 也逐渐到了极限。Google 的工程师不断对它进行扩展和优化，可最终还是挡不住代码库的膨胀：服务器 CPU 长期满负荷运行，TCP 连接频繁失败，整个系统越来越难以维护。

他们当然也研究过 Git，同样，Git认为应该拆成多个小仓库。

于是，Google 做出了一个和 Linus 十分相似的决定：既然现有工具解决不了问题，那就自己造一个。

这就是后来著名的 Piper。

开发一套新的版本控制系统，并不是最困难的事情，真正困难的是迁移。

当时，Perforce 已经在 Google 内部运行了 11 年，围绕它构建了 300 多种开发工具。如果简单照搬 Perforce 的接口，不仅技术债巨大，还可能带来法律风险。

2010 年，Google 因 Android 中使用 Java API 而遭到 Oracle 起诉，这件事让工程团队格外警惕。

为了避免重蹈覆辙，他们没有复制 Perforce 的 API，而是采用了经典的"洁净室（Clean Room）"开发方式：由完全不了解 Perforce 接口实现的工程师，从零设计 Piper 的接口和架构。

整个迁移过程持续了 4 年，Google 才最终完成从 Perforce 到 Piper 的切换。

这场迁移的代价巨大，但也让 Google 获得了一套真正能够支撑数十亿行代码、数万名工程师同时协作的版本控制系统。

**0** **4**

**总结**

Facebook 和 Google 这两家互联网巨头，在代码库演进过程中，都坚持了单一代码库（Monorepo）策略，也因此在不同阶段"抛弃"了 Git。

Facebook 选择在开源 Mercurial 的基础上进行深度改造，让它适配超大规模代码库。

Google 则更彻底，直接发明新轮子 Piper，并投入多年完成全公司迁移。

这两条路线都代价巨大，也都不是普通公司可以复制的工程选择。

对大多数团队来说，Git 依然是最合适、最稳妥的答案。

微信扫一扫
使用小程序

## 结构分析

### 章节划分

- **01 两个软件同时诞生**：BitKeeper事件 → Git/Mercurial诞生 → Facebook采用Git → Monorepo四大优势
- **02 Facebook决定抛弃Git**：Git性能瓶颈 → 三站选型（Git社区→Perforce→Mercurial）→ Mercurial三层创新（Watchman集成→remotefilelog→EdenFS）→ 社区协作（500+补丁）→ Sapling诞生
- **03 Google发明新轮子**：规模惊人（20亿行/86TB）→ Perforce极限（11年运行/300+工具）→ 自研Piper → 洁净室开发（规避Oracle诉讼风险）→ 4年迁移
- **04 总结**：核心结论——普通公司Git仍是最佳选择

### 关键时间节点

| 时间 | 事件 |
|---|---|
| 2005年4月 | BitKeeper事件，Git和Mercurial诞生 |
| 2010年 | Oracle起诉Google Android使用Java API（洁净室开发背景） |
| 2013年 | Facebook代码爆炸，新增4.4万文件/1700万行 |
| 2015年 | Google代码库规模达20亿行/86TB |

### 配图说明

- **图1（imgIndex=0）**：Git/Mercurial作者图（Linus Torvalds与Olivia Mackall）
- **图2**：Sapling Meta图（Sapling项目标识）
- **图3（imgIndex=5）**：代码规模对比图（Windows/Office在中间，Google绿色方块在最下方）

### 关键数据点

| 数据 | 说明 |
|---|---|
| 45分钟 | Facebook测试中Git基础命令执行时间 |
| 5倍 | Watchman集成后文件状态查看速度提升 |
| 10倍+ | remotefilelog带来的clone/pull速度提升 |
| 4.4万文件/1700万行 | 2013年Facebook代码仓库年新增量 |
| 20亿行/86TB | 2015年Google代码库规模 |
| 500+ | Facebook一年半内向Mercurial提交的补丁数 |
| 4年 | Google Piper迁移持续时间 |
| 11年 | Perforce在Google内部运行时间 |
| 300+ | 围绕Perforce构建的开发工具数量 |
