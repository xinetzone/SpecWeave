丛林 丛林

在小说阅读器读本章

去阅读

> 字数 2010，阅读大约需 11 分钟

看到QuantDinger这个项目，我第一反应是：又一个量化交易框架？

但看完README，我发现它有点不一样。这东西不是那种给你个API包装就完事的库，也不是那种必须把API密钥交给第三方SaaS的黑箱平台，QuantDinger把自己叫做“开源的AI量化交易基础设施层”。

## 项目简介

QuantDinger是一个自托管的AI量化交易平台，把AI研究、策略编写、回测、模拟盘、实盘执行、监控全塞进一个Docker Compose栈里，你的代码、数据、密钥，全跑在你自己的机器上。

![](https://mmbiz.qpic.cn/mmbiz_png/38IO1MnhnazBZPqiaBPQ7tShNEqqZ0rXEABwKROeI6p6VLM0JCyoEibAyX5Bb5RiabMtnOK9gf1hhBoCBesV6ibfdszp3dicLVAuLUMNy65N6JN4/640?wx_fmt=png&from=appmsg)

它支持加密货币（Binance、OKX、Bybit这些）、美股（IBKR、Alpaca）、外汇（MT5），还能让AI助手（比如Cursor、Claude Code）通过MCP协议直接调用它的Agent Gateway，读市场数据、跑回测、下模拟单。

项目是Apache 2.0协议，后端源码全开放，前端源码需要单独授权。作者brokermr810明显是个老手，文档写得极其详细，从一键安装到生产部署都给了步骤。

## 快速上手

先说说怎么把它跑起来，QuantDinger给了两种安装方式：一条命令快速体验，或者手动克隆配置。

**快速安装** （适合快速体验）：

```
curl -fsSL https://raw.githubusercontent.com/brokermr810/QuantDinger/main/install.sh | bash
```

Windows下用PowerShell：

```
irm https://raw.githubusercontent.com/brokermr810/QuantDinger/main/install.ps1 | iex
```

这脚本会问你管理员账号密码，然后拉取Docker镜像，启动整个栈。默认端口8888，打开浏览器就能登录。

**手动安装** （适合生产环境）：

```
git clone https://github.com/brokermr810/QuantDinger.git
cd QuantDinger
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥等配置
docker compose up -d
```

国内加个 `IMAGE_PREFIX=docker.m.daocloud.io/library/` 就能解决拉取慢的问题。

启动后，打开 `http://localhost:8888` 就能看到登录界面。默认账号密码是 `admin` / `admin` ，记得第一时间改掉。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/38IO1MnhnayyAoYN56bZiaIbtwEcynZhDUeiaqegXickg2YB7IJb2mfhYp1WrVeRsZic589FwnrFOg6bdV6JSD3MrQMC0Y3P86ibKk6RJhIf4QsI/640?wx_fmt=png&from=appmsg)

架构图挺清楚，数据从交易所和经纪商进来，经过指标、信号、策略层，再到回测或实盘执行。整个闭环都在你自己的服务器上跑，不依赖任何外部SaaS。

如果你只是想试试AI研究功能，可以先不配置交易所API，直接用模拟数据跑回测。QuantDinger自带了一个示例策略库，里面有几个简单的策略代码，可以直接加载运行。

## 功能详情

### 1\. AI研究集成：内置多LLM支持，用自然语言生成策略代码

![](https://mmbiz.qpic.cn/sz_mmbiz_png/38IO1MnhnayrXAFK7KXRrhEX491hwzs9ibrRCHBpNoF5jFVqyXcBfyrrL56mRc0EDxcP03ZvfmRGwVSic8ewWmZTOYjSQxAVAFIoTnllnGrLw/640?wx_fmt=png&from=appmsg)

QuantDinger把AI研究当作一等公民，它内置了多LLM集成，支持OpenAI、OpenRouter、AtlasCloud这些提供商。你配置好API密钥，就能在界面里让AI分析市场、生成指标代码、甚至给出交易建议。

更牛的是它的“机会雷达”和NL→代码转换。你可以用自然语言描述一个策略想法，比如“当RSI低于30且成交量放大时买入”，AI会尝试生成对应的Python指标代码。这当然不是百分百准确，但能帮你快速把想法变成代码，省去不少手动敲键盘的功夫。

![](https://mmbiz.qpic.cn/mmbiz_gif/38IO1Mnhnaygf2lLmbwL82YQWwqdaxmJbKiaunwvQFlAj6uBfxXss02JANzCblibrbKWzicm0nfgtUuT563EfCiaM4ws8aM1FDAZLyrcSnBVkPw/640?wx_fmt=gif&from=appmsg)

演示GIF展示了从安装到AI分析的完整流程。界面是Vue写的，图表用了KLineCharts和ECharts，看起来挺专业，至少比那些花里胡哨的Dashboard实在。

### 2\. 策略开发模式：IndicatorStrategy与ScriptStrategy双轨并行

![](https://mmbiz.qpic.cn/sz_mmbiz_png/38IO1MnhnawiaicxI3oPHsVQKNbRweqOcM5IEXrMBDRhoRthZtMRWATBDO3M9IxjR3TWxwlEWtvYx6Lrb1BFyLicLSyNiaUyiaF9DPlCOL3JLriaw/640?wx_fmt=png&from=appmsg)

QuantDinger支持两种策略编写方式： `IndicatorStrategy` 和 `ScriptStrategy` 。

`IndicatorStrategy` 是基于数据框的向量化信号。你写一个Python函数，输入是OHLC数据框，输出是买卖信号和图表叠加，这种方式适合快速研究和可视化。

`ScriptStrategy` 是事件驱动的，有 `on_init` 和 `on_bar` 回调，你可以用 `ctx.buy()` 、 `ctx.sell()` 直接控制订单，这种方式更接近实盘交易的状态管理。

两种模式共享同一个回测引擎和实盘执行层。你可以在研究阶段用 `IndicatorStrategy` 快速验证想法，然后迁移到 `ScriptStrategy` 做更精细的控制。

我个人更喜欢ScriptStrategy，因为它更接近实盘交易的状态管理，但IndicatorStrategy对于快速验证想法确实方便。

### 3\. 回测与实盘执行：从历史验证到真实交易的无缝衔接

![](https://mmbiz.qpic.cn/mmbiz_png/38IO1MnhnazjddcDv3Ol14YvS5NteVZ2LT6l2fBUsvG243vpMZbngBK0S9YRrSnTMzs601NBic0Sica3mWI7gWJicHlMgmoV6ZFR08VG4vpCtQ/640?wx_fmt=png&from=appmsg)

回测在服务端跑，不是那种前端糊弄人的把戏，它会生成资金曲线、最大回撤、交易日志这些指标，回测完你可以直接把策略部署成实盘机器人。

实盘执行自带的支持很多交易所，但都不是国内的，这里不做介绍，意义不大。所有经纪商账户在一个页面统一管理，每个用户的会话是隔离的，不会互相踢掉。

订单通过后台Worker处理，有健康检查和重试机制。你可以设置Telegram、邮件、短信、Discord通知，策略开平仓都能收到提醒。

### 4\. 多市场支持：覆盖加密货币、美股、外汇主流交易所

加密货币方面，CCXT支持的交易所基本都涵盖了。传统市场方面，IBKR和Alpaca对接股票和ETF，MT5对接外汇，数据源可以接Yahoo Finance、Finnhub、Tiingo这些。

经济日历数据默认用AkShare和WallstreetCN的免费源，也支持Trading Economics（需要配置密钥）。

### 5\. Agent Gateway：通过MCP协议连接AI编程助手

![](https://mmbiz.qpic.cn/mmbiz_png/38IO1Mnhnazydicb01dAlHCZbTPkmf1G0iaPhK8cQnPiaW3gYZfkk3exHbCevQ6a4NNc2eY0swNObg7uRe2ibECtPE4euzM6bPRzXmkKeYDdfR4/640?wx_fmt=png&from=appmsg)

这是QuantDinger最让我眼前一亮的地方，它提供了一个Agent Gateway（ `/api/agent/v1` ），还发布了PyPI包 `quantdinger-mcp` ，让Cursor、Claude Code、Codex这些AI编程助手能直接跟你的QuantDinger实例对话。

你生成一个Agent Token，配置到MCP里，AI就能读取市场数据、管理策略、跑回测、下模拟单（默认是模拟盘，实盘需要显式开启）。所有调用都有审计日志，谁在什么时候干了什么一清二楚。

这意味着你可以用自然语言让AI助手帮你调整策略参数，或者让它定期检查持仓。对于习惯用AI编程的人来说，这个集成大大降低了操作门槛。

### 6\. 安全模型：自托管架构与密钥本地存储

QuantDinger的安全设计挺实在，Agent Token默认只能下模拟单，想开实盘得同时满足两个条件：Token的 `paper_only=false` ，并且服务器环境变量 `AGENT_LIVE_TRADING_ENABLED=true` 。

交易所API密钥永远留在你自己的部署里，不会发给QuantDinger的SaaS运营商（如果你用自托管），审计日志记下每一个Agent调用，方便事后复盘。

这种“默认模拟盘、显式开启实盘”的设定，比那些一上来就要你API密钥的平台谨慎多了。

## 界面UI精细

我们来看看这个开源产品的前端UI，这部分是需要授权的，所以做的也相当精美，简单过一下，如果玩这个涉及二开，不如用AI重新搭前端，这个前端并没有做国际化，全英文页面。

所以简单浏览一遍即可

- • 指标集成开发、图表绘制、回测和快速交易
![](https://mmbiz.qpic.cn/sz_mmbiz_png/38IO1MnhnaxtRU5Ye5Zia8ZaJq9vqSZdqzj0Om0v7oVLXkSbOfKjSficfLZKBerrIaxBm0wyMp4ljib7jkziaDGDMS6DyXnY2FWqlmNbKfYAa1M/640?wx_fmt=png&from=appmsg)

- • 人工智能资产分析与机会雷达
![](https://mmbiz.qpic.cn/sz_mmbiz_png/38IO1MnhnaxNdficE5GM8NBWrOq28v1LMiaP2ONicYic0B55FPebia0Av8OvzK6icXv1kJkPWWdltUkicT6u8JibGG3ATKgl9HibvmDK2xclrXSySpII/640?wx_fmt=png&from=appmsg)

- • 交易机器人工作区和自动化模板
![](https://mmbiz.qpic.cn/sz_mmbiz_png/38IO1MnhnawVFZ9CY3uXIGxQnoOHlmOcd1mjbpRl0ibxs4rLASfhicddMiaDvV1vFbLBlGKVcEW3B151XGyylGygreWN6EYuFBzpWeweImdSwU/640?wx_fmt=png&from=appmsg)

- • 战略实时运营、性能与监控
![](https://mmbiz.qpic.cn/sz_mmbiz_png/38IO1MnhnawfEpAAibhmH030zCWDN0Sfg0EhkT9T0tbhvxeZmOMC84QIOEP4iacGSKer1zYse4fWQrkibfyHyRichKJrSwH5MicNxceWJIzoCVFk/640?wx_fmt=png&from=appmsg)

## 最后聊聊

QuantDinger不是一个完美的产品，它的前端源码不是完全开源，商用需要单独授权。它的学习曲线不低，你得懂点Docker、Python和量化交易的基本概念。但它做了件很重要的事：把AI研究、策略开发、回测、实盘执行这些碎片化的工具链，打包成一个自托管的完整栈。

这个项目对想要打造一个量化交易系统的人来说，非常有参考价值，但必须懂一些编程知识，重新配置对接国内一些交易商账户，还涉及部分二次开发。总的来说不是一款开箱即用的开源产品，需要有一定的相关知识储备才行。

GitHub仓库：

> https://github.com/brokermr810/quantdinger

*****点击下方卡片，关注极客之家*****

这个公众号曾分享过许多有趣的开源项目。如果你不想逐篇翻阅历史文章，也可以直接关注微信公众号“极客之家”，通过后台留言与我们互动交流

![图片](https://mmbiz.qpic.cn/sz_mmbiz_jpg/38IO1MnhnazkbVhlN1qImZrP9eKa7xxO5tJFwFIh7EeZsfeicF2YCnnlEJ8W7ib1NImowDbwedJxjGnx2CMmrViaHWu4wEvConX38zibibYGvbHc/640?wx_fmt=jpeg&from=appmsg&watermark=1&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=6)

知道了

微信扫一扫  
使用小程序

： ， ， ， ， ， ， ， ， ， ， ， ， 。 视频 小程序 赞 ，轻点两下取消赞 在看 ，轻点两下取消在看 分享 留言 收藏 听过