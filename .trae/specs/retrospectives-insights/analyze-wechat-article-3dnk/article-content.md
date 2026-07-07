小黑 小黑

在小说阅读器读本章

去阅读

大家好，我是小黑。

GitHub上有个项目叫 Project N.O.M.A.D，33k Star，3k Fork。作者 Chris Sherwood 是个搞网络设备的 YouTuber，Crosstalk Solutions 频道有 38 万多订阅。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/38IO1MnhnawRQePq5ZL6M3tj5fIMgPzYyovhWOLicPHOI28fgf9aAZdPYgftIw3GlTElC9fp8fVx7mABUJkmZu1AoGhpG9jvr7Q6fSO3w1dE/640?wx_fmt=png&from=appmsg)

这项目说白了就是把维基百科、本地 AI、离线地图、离线教育平台全塞进 Docker 里，断网也能用。

我第一眼看到的时候，心想这不就是个大号离线 U 盘吗？点进去看了看，明白了，这是妥妥的末世生存宝库，而且是断网状态用的！

## 它到底是个什么东西

![](https://mmbiz.qpic.cn/sz_mmbiz_png/38IO1MnhnayiaBoLeFAxgkmMzNCqLJIl0Alnldm5zkdgbFx9ET3zzBnm24tqsc9DKXxJ8DbPWQmFXUO2mCLCwAMQzUcIlGiaEH7zEdafHXEVc/640?wx_fmt=png&from=appmsg)

N.O.M.A.D 全称是 Node for Offline Media, Archives, and Data。Chris Sherwood 搞了超过一年，主要代码贡献者是 jakeaturner。项目用 TypeScript 写的，Apache 2.0 协议，完全免费。

思路很直接： **用 Docker Compose 把一堆开源工具串起来，通过一个 Command Center 的 Web 界面统一管理，装完之后拔掉网线，所有功能照样跑。**

![](https://mmbiz.qpic.cn/mmbiz_png/38IO1Mnhnay9jCd7RT4UHbPez69aqYoodTzB6CTDvic8cMYz1qOLdOfFHlgc3XUUrknajPcp13zelKAMl3lZIyohTicTTtN55aOb6lNhl1piaM/640?wx_fmt=png&from=appmsg)

市面上有类似的，比如 PrepperDisk（199 到 279 美元）、Doom Box（699 美元）。但这些玩意要么锁死在树莓派上，要么不带 GPU 加速，AI 功能基本等于没有。

N.O.M.A.D 不一样，它跑在任何 x86 Linux 机器上，支持 NVIDIA GPU 加速，Ollama 本地大模型能正常跑，而且一分钱不收。

Chris Sherwood 自己说过一句话： *"When that internet connection goes away, it all goes away. I wanted to find a way to save a copy of that information locally."*

翻译过来就是：

> 当网络连接中断时，所有数据都会随之消失，我想找到一种方法，将这部分信息本地保存一份副本。

## 里面装了些什么

Command Center 的界面把功能分成了几个大块，我挨个说。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/38IO1Mnhnaw4kWeGR6yUm03iccybCBER6nZhy4gnw7l6msl887was86E4cTQDAIgSjMemejswDEKtbLVrhLq3CKTzzJSkSY0pDZGFomZJMXY/640?wx_fmt=png&from=appmsg)

### 本地 AI 助手，RAG 也带上了

AI 这块用的是 Ollama 跑本地大模型，向量数据库用 Qdrant，RAG 语义搜索直接内置。我们可以上传自己的文档，AI 能基于这些文档回答问题。不想用 Ollama 也行，设置里填个 OpenAI 兼容的 API 地址，比如 LM Studio 的本地服务，照样能跑。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/38IO1MnhnazngpSqlQCyZib56kic8Aia2dYTRGlCqSeSqoS6F45QB1NMZCf59D72Rm8ybSoEnCG3wuSpE035pzZ3lLmPV8FWGZb6IcAPmroNJk/640?wx_fmt=png&from=appmsg)

GPU 现在只支持 NVIDIA，AMD 和 Apple Silicon 用户暂时没戏。 **VRAM 越大，能跑的模型越大，RTX 3060 12GB 是起步配置。**

### 离线维基百科，快 100GB

信息图书馆用的是 Kiwix，离线维基百科、医疗参考、生存指南、电子书该有的都有。完整版带图片的维基百科接近 100GB，所以存储得留够。

![](https://mmbiz.qpic.cn/mmbiz_png/38IO1MnhnaxVB4v4cZIIHM7QCElZ910VicoDw0moMbjWDHjWyPDdJxiac2J4mKYrklic26caoRolCDZkrgttvH6ulWiaQ04JNjzXnxZFw2ias6mg/640?wx_fmt=png&from=appmsg)

Kiwix 这工具本身不算新，但 N.O.M.A.D 把它和整个系统捆在一起，不用我们自己配 ZIM 文件、调端口。

### Khan Academy 课程，进度能跟踪

教育平台用的是 Kolibri，Khan Academy 的课程全搬进来了，还能跟踪学习进度，支持多用户。有完整的k12课程体系，有小孩的话，这功能比刷短视频强。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/38IO1Mnhnax214laPj7j9NbacNYNsOAeCBsxfURIiasMB5l2ibnXrFFngeCDu1G4JPlyicJibc1nvxSy8bENricy2XQ9E2R0xTgNlZicnH4PAq8bA/640?wx_fmt=png&from=appmsg)

### 离线地图，不用流量

地图用的是 ProtoMaps，区域地图可以下载到本地，搜索和导航都能用。出国旅游或者去信号差的地方，这玩意比 Google Maps 离线模式靠谱。

![](https://mmbiz.qpic.cn/mmbiz_png/38IO1MnhnawlBbNZJEqesIicVYrnsOMecrEoz5eDYm3dP4bmNoGZCs5QibyE7n6FKDmjWKKuZAicUqOB7uics9Pe4gia8XbvkIVVkdjHtYd3LJxM/640?wx_fmt=png&from=appmsg)

### 数据工具、笔记、跑分排行榜

CyberChef 负责加密、编码、哈希和数据分析。FlatNotes 是个本地 Markdown 笔记工具。系统基准测试能给你的硬件打分，分数还能上传到社区排行榜，看看别人的配置有多猛。

![](https://mmbiz.qpic.cn/mmbiz_png/38IO1MnhnaxYeAZ1uGiaDsR6yC1rYmfa4onEumMzjsSGD3hxf9XQotCMvF3H3mGXxPhQnfs7UDdq1ADG3ib62ovzMCkngAEoMFkwo0KKEDOBQ/640?wx_fmt=png&from=appmsg)

## 怎么把它跑起来

N.O.M.A.D 只支持 Debian 系的 Linux，Ubuntu 是官方推荐的。Windows 用户可以通过 WSL2 跑，macOS 现在没原生支持。

硬件分两档：

**最低配置：** 2GHz 双核处理器、4GB 内存、5GB 硬盘，这只能跑 Command Center 本身，AI 功能别想了。

**想完整体验：** AMD Ryzen 7 或 Intel i7 以上、32GB 内存、NVIDIA RTX 3060 或更高、250GB 以上 SSD，完整维基百科加 AI 模型，硬盘空间往 1TB 准备差不多够。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/38IO1MnhnayyMtO1ibpxEQx7sOvrEGibe0zUjqkWEIbrF3gTSo6q0nQxCAy9rMvnUggOdlktgXmGJQ26VqDFkwqKthuAgT0PCIHKia5DOOnbhU/640?wx_fmt=png&from=appmsg)

安装就一条命令：

```
sudo apt-get update && \
sudo apt-get install -y curl && \
curl -fsSL https://raw.githubusercontent.com/Crosstalk-Solutions/project-nomad/refs/heads/main/install/install_nomad.sh \
  -o install_nomad.sh && \
sudo bash install_nomad.sh
```

装完打开浏览器，访问 `http://localhost:8080` 或者 `http://你的IP:8080` ，就能看到 Command Center。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/38IO1MnhnawfmKu4DLMjTTd41OE7HagiabHf8UoasLUWib5fMTH8opW0436LqjO7iaaNG3CCz3uiaK7WH94iaL1tKNo2IbqXTNMk5bdz6x2ng1BU/640?wx_fmt=png&from=appmsg)

想自己折腾的可以用 Docker Compose 手动部署，项目仓库里有模板，改改配置再 `docker compose up -d` 就行。

## 几个要注意的点

项目默认不带认证，局域网内任何人都能访问。Chris Sherwood 说未来可能会加可选的认证层，但现在得靠我们自己用防火墙或者端口控制来管。

N.O.M.A.D 本身不收集任何遥测数据，连上网检测都只是请求一下 Cloudflare 的 `1.1.1.1/cdn-cgi/trace` ，装完之后完全可以断网运行，这点比大多数国产软件强。

社区还挺活跃，有人 fork 出了 Homelab Edition，专门适配 Unraid 和 TrueNAS SCALE。GitHub Discussions 里欧洲地图、存储路径管理这些功能都有人提，开发者也在跟进。

## 我怎么看这玩意

说实话，我一开始觉得这就是个 prepper 的玩具，末日生存狂才会感兴趣，但看了架构图之后，觉得自己之前想岔了。

我越想越觉得这事离谱：现在人对互联网的依赖已经到病态了。medical dosage、基础电路接线、孩子正在学的课程，这些东西本来应该在我们脑子里或者本地能查到，但现在全变成了"打开浏览器搜一下"，网一断，全瞎。

N.O.M.A.D 最值钱的地方不是酷，是把本地 AI、知识库、教育内容、地图这些原本要分别装的东西，打包成了一条脚本就能跑的产品。Ollama、Kiwix、Kolibri、Qdrant、CyberChef，这些工具我们自己都能装，但配起来得花点时间，现在 N.O.M.A.D 用一条脚本加一套 UI 把这事搞定了。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/38IO1MnhnayMToehxl6Area8cWQsLj8RQiaMOYDY4863c73SDOFFB0roY3BW3R5fMhBUUD2AibTrcwKLgHnR2Ima0rgutbZp4iaWpHF36Ao1UQ/640?wx_fmt=png&from=appmsg)

当然它也有硬伤：GPU 只支持 NVIDIA，平台锁死 Debian，没有默认认证，这些我估计在后续迭代中都能修正，社区现在挺活跃，已经衍生出不少社区版新功能了，就算开发者不去填这些坑，后面肯定也有人填。

这玩意最狠的一点是它的思路： **离线优先，别等网断了再想办法，先把所有东西准备好。** 这个思路放在今天这个云厂商三天两头出故障、API 随时可能限流、某公司时不时封号的环境里，我觉得拿一份永久的离线资料库也蛮重要的，这存储量，大概相当于一座图书馆了吧，而且你还能继续往里填东西，只要你的硬盘足够大！

**GitHub地址：**

> https://github.com/Crosstalk-Solutions/project-nomad

Discord 社区和硬件排行榜的链接在仓库 README 里，感兴趣的可以直接过去看。

*****点击下方卡片，关注极客之家*****

这个公众号曾分享过许多有趣的开源项目。如果你不想逐篇翻阅历史文章，也可以直接关注微信公众号“极客之家”，通过后台留言与我们互动交流

![图片](https://mmbiz.qpic.cn/sz_mmbiz_jpg/38IO1MnhnawRribwNAbEAysoTwkdTe31DjSPupmHEF8vxcdYicbYUoE2ibVzXRp4zPQ7jOX4t6jckvxp0BXX6hC9ickymTicggN4Vic6DVtznaugU/640?wx_fmt=jpeg&from=appmsg&watermark=1&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=6)

微信扫一扫  
使用小程序

： ， ， ， ， ， ， ， ， ， ， ， ， 。 视频 小程序 赞 ，轻点两下取消赞 在看 ，轻点两下取消在看 分享 留言 收藏 听过