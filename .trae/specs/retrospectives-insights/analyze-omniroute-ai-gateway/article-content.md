小黑 小黑

在小说阅读器读本章

去阅读

大家好，我是小黑。

最近又挖到一个比较火爆的开源项目，1.2万 Star，标题写着 Never stop coding，它做了一个聚合操作，把237个AI提供商塞进一个端点，其中有90多个有免费额度，11个永久免费。免费token加起来每月大概16亿，这个数字没注水，重复计算已经去掉了。

## 这到底是个什么东西

![](https://mmbiz.qpic.cn/sz_mmbiz_png/38IO1MnhnazMGFJZraQV2skh17TRE6dmaC468K9wpc7h3whqD79z3Aef6SlDLG76PxPicr3Q1XoKdkUJT9LQ25gacuXhWRfGrcB9ZPRzsIU4/640?wx_fmt=png&from=appmsg)

OmniRoute是个本地AI网关，MIT协议，免费。在本地跑一个服务，把237个AI提供商统一到一个OpenAI兼容的端点。我们把Claude Code、Codex、Cursor、Cline、Copilot这些工具的API地址改成 `localhost:20128/v1` ，后面就不用管了。

它不走云端，数据、API key、请求记录都在自己机器上，AES-256-GCM加密，不收集遥测数据。

Dashboard 开在 `localhost:20128` ，237个提供商的卡片排在那里，Anthropic、OpenAI、Google、DeepSeek、Groq、Cerebras、NVIDIA NIM全都有，点开关就连。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/38IO1MnhnaylImWtEWaZx6zbBQsueLjwHAib4UAzHcg1Wib8gibVkyW1X8A4X02e0ibsyiayrypaEsDjlmTibsiaIChuNVFGyTbhib3icR0EMW51fFNQ/640?wx_fmt=png&from=appmsg)

## 核心功能

### 237个提供商，一个开关

OmniRoute连了237个提供商，其中90多个有免费额度，11个永久免费。Kiro每月50 credits，跑Claude Sonnet 4.5、Qoder不限量，kimi-k2-thinking、qwen3-coder-plus随便用。Cerebras每天100万token，等等。

这些免费额度都能用，OmniRoute把它们聚合到一个Combo里，按优先级自动路由。第一层烧完了，毫秒级切到第二层，依次类推，基本不会断。

![](https://mmbiz.qpic.cn/mmbiz_png/38IO1MnhnaxN6m1r1V7kmP7VDpiaFDcX0QKibC3DWdHWLfXpIorZicedJnp4CyVZ2qibYnv1R4icLOic6ObwomhJeKQnZPMGx7eMcogoVN9IFEoeI/640?wx_fmt=png&from=appmsg)

Dashboard里能看到每个提供商的实时剩余额度、重置时间、条款限制。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/38IO1MnhnawYxnVmukTnV6YsoYkU5yFPKoiahkbrSGjNBOjRLQiaBgJF3uo4kyGicvlQf4ictUyGKyEcW9FRALTzFEBgiaOx6KGwdwwrFEcVWKUY/640?wx_fmt=png&from=appmsg)

### Combo自动故障转移

OmniRoute的核心功能是Combo，多个模型串成一条链，配额用完自动滑到下一个。某个服务商挂了，它毫秒级切到下一个。

内置17种路由策略：

![](https://mmbiz.qpic.cn/mmbiz_png/38IO1MnhnawURiaYl7q6QU4vfZbDU2niaXn8qQg1ZOKrFibicfK4eyPRuCSXKkqELfMicFJsVzcx1P5ClvkVjeK9NMcvE9ErjamrRnzjGXoNibNUc/640?wx_fmt=png&from=appmsg)

auto策略最省事，模型参数填auto，OmniRoute会根据实时健康度、额度、成本、延迟、成功率打分，挑最好的。

还有auto/coding、auto/fast、auto/cheap、auto/offline、auto/smart这些变体。auto/coding优化代码质量，auto/fast优化速度，auto/cheap省钱，auto/smart还能探索新模型。

最新版本加了Quota-Share，同一个订阅账号下面有多把key，它按权重分额度。如果小团队共用一张Codex Pro或者Kimi Coding Plan，这个功能就很有用，一个人把5小时额度全烧光，Quota-Share会拦住，其他人不会被锁死。而且一个模型挂了，不会拖累整个连接。

![](https://mmbiz.qpic.cn/mmbiz_png/38IO1MnhnaypzicUBiaIUkaH8NH2JzeoFb2YbLvQWFvQKXTyjWLauSZn68qbm4icOBXzmOzJ3tsTHNLzO2ZduuGlTfX50IGHjVVYdyzvZ8rWibA/640?wx_fmt=png&from=appmsg)

### RTK + Caveman压缩

这是个省钱功能（说实话，这个没啥用，我都混免费额度了，还替我省什么，但是既然有这个功能，我们也来说说），RTK过滤工具输出里的重复内容，Caveman做规则压缩，两者叠加能省15%到95%的token。

官方给的例子：

> 一段69个token的React解释，压缩后剩19个token，意思没变。代码块、URL、JSON结构它不动，只压缩冗余内容。

经常跑git diff、grep、日志的人，这个压缩率能省不少钱。压缩的是输入，输出不会变，质量也不会掉。

![](https://mmbiz.qpic.cn/mmbiz_png/38IO1MnhnaxyiawFgbPu9Kcia9U0d9Aqa9xUMyiaoArPSl70RibO6LiaOic44qK5ZsllfePnw366YxV1bicUlVafeJjGZ4J8w9MeJVCV9RqDhYzdW8/640?wx_fmt=png&from=appmsg)

### 24+工具一键接入

OmniRoute给Claude Code、Codex、Cursor等这些工具准备了setup命令，不用手动改JSON、配环境变量，一行命令，配置文件就生成了。

![](https://mmbiz.qpic.cn/mmbiz_png/38IO1MnhnaxWk12nFXI0q4H1SmZn8BrRgwwqex0TGZy9rmUEia98w8rlGId9mIujWHQ5KKT8cyjs7Io5mQsT4hoZakuKwa2dYbhaY5wlfIpU/640?wx_fmt=png&from=appmsg)

Remote模式也支持，OmniRoute跑在VPS上，本地CLI用omniroute connect远程控制。带权限范围的token分read、write、admin三级。我在家里笔记本上连公司的OmniRoute实例，模型列表、额度、路由策略都能同步。

### MCP和A2A协议

OmniRoute内置了MCP服务器，95个工具，30个scope，stdio、HTTP、SSE三种传输。

![](https://mmbiz.qpic.cn/mmbiz_png/38IO1MnhnawhibX6HKdCd2BMib2XsoPp5W3dP4jusFOicMu0dhQqMv4fXaFZSsvnUq9cymzocFYfNjNNM3xnQGJ2R6WzCN2TDlbxJBkeicpUxGs/640?wx_fmt=png&from=appmsg)

Claude Desktop、Cursor这些支持MCP的客户端可以直接调用OmniRoute的管理功能。

A2A协议也有，AI代理可以自己管理路由、切换提供商、查额度、调压缩策略。

Claude Code可以通过 `mcp add-server` 把OmniRoute全套工具集接进去。

## 快速开始

装起来挺简单：

```
npm install -g omniroute
omniroute
```

Dashboard开在 `localhost:20128` ，API端点是 `localhost:20128/v1` 。进去点Providers，连一个免费的Kiro或者Pollinations，然后复制 `API key` 。

打开Claude Code，base URL改成 `http://localhost:20128/v1` ，模型参数填auto，完事。

验证一下：

```
curl http://localhost:20128/v1/models -H "Authorization: Bearer YOUR_KEY"
```

模型列表弹出来，说明通了。客户端没法发自定义header，OmniRoute准备了带token的兼容地址，比如 `http://localhost:20128/vscode/YOUR_KEY/chat/completions` ，填进配置里。

Docker也能装：

```
docker run -d --name omniroute --restart unless-stopped --stop-timeout 40   -p 20128:20128 -v omniroute-data:/app/data diegosouzapw/omniroute:latest
```

作者还做了PWA和Electron桌面版，Windows、macOS、Linux都能跑。

Node版本要求 `>=22.0.0 <23` 。

本地编译慢的话，用pnpm安装或者 `OMNIROUTE_SKIP_POSTINSTALL=1` 跳过本地构建。

## 最后聊聊

我跑了一周OmniRoute，最大的变化是不用到处找免费token了。之前为了省Claude Code的额度，我注册了一堆平台。每个平台的额度、重置时间、API格式都不一样，记都记不住，密码也记不住。

OmniRoute把这些全接进了一个Dashboard，路由、切换、压缩都是自动的。我只管写代码，额度的事不用管。

免费额度聚合和自动故障转移是OmniRoute的核心，其他功能是添头，不过项目功能太多，文档分散，新手第一次打开Dashboard会有点懵，装完之后跑起来，不用再看文档，可以试一下。

GitHub地址：

> https://github.com/diegosouzapw/OmniRoute

*****点击下方卡片，关注极客之家*****

这个公众号曾分享过许多有趣的开源项目。如果你不想逐篇翻阅历史文章，也可以直接关注微信公众号“极客之家”，通过后台留言与我们互动交流

![图片](https://mmbiz.qpic.cn/mmbiz_jpg/38IO1Mnhnax4MD9xl7CYqek6NiaxCnHzPDwliafvic8zhPsIWicLBQpABmtXZREgzRt2CwGzDfXwZHYxmYTSxuwbiamQVeBFgPDYxPbCBkxbANCM/640?wx_fmt=jpeg&from=appmsg&watermark=1&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=6)

微信扫一扫  
使用小程序

： ， ， ， ， ， ， ， ， ， ， ， ， 。 视频 小程序 赞 ，轻点两下取消赞 在看 ，轻点两下取消在看 分享 留言 收藏 听过