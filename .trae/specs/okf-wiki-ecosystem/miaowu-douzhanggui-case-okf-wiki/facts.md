# 事实登记（F-001–F-060）

> 本表为 Spec 的事实基础，**镜像**自 bundle 内 [source-ledger.md](../../../../projects/awesome-okf-xs/doc/bundles/jishu/ai/ecosystems/miaowu/miaowu-douzhanggui-case/references/source-ledger.md)（唯一权威出处）。
> 事实分层：`page_fact`（文章写了什么）/ `author_claim`（文章对做法的判断与建议）。执行者洞察与模式不进入本表。
> **全部 60 条来自单一信源 S1**（微信公众号「秒悟Meoo」2026-10-29 01:00《纳尼?！真有人靠 Meoo 做副业月入过万！》），无第三方独立凭证。

## S1 信源身份

| 项 | 值 |
|---|---|
| URL | `https://mp.weixin.qq.com/s/LCow44TOI0J-HjINToYWtQ` |
| 账号/归属 | 微信公众号「秒悟Meoo」（`#js_name`） |
| 发布时间 | 2026-10-29 01:00（`#publish_time`） |
| 可访问性 | 公开、无需登录/验证码/邀请码；WebFetch 单通道取到完整正文 |
| 利益相关 | 发布账号即案例中工具（Meoo）的提供方 |

## 1. 文章身份与人物背景（F-001–F-009）

| F | claim | type | status |
|---|---|---|---|
| F-001 | 文章标题为《纳尼?！真有人靠 Meoo 做副业月入过万！》 | page_fact | verified |
| F-002 | 发布账号为微信公众号「秒悟Meoo」 | page_fact | verified |
| F-003 | 页面显示的发布时间为「2026年10月29日 01:00」 | page_fact | verified |
| F-004 | 文章公开地址为 `https://mp.weixin.qq.com/s/LCow44TOI0J-HjINToYWtQ` | page_fact | verified |
| F-005 | 主角为王玉丹，02 年出生 | page_fact | single-source |
| F-006 | 2026 年 5 月，王玉丹从北京一家公司辞职 | page_fact | single-source |
| F-007 | 辞职前她做的是面向央企客户的数字化转型业务 | page_fact | single-source |
| F-008 | 受数据安全要求限制，工作中能实践 AI 的机会不多 | page_fact | single-source |
| F-009 | 辞职后她花了两个月自学 AI，想找个实际问题练练手 | page_fact | single-source |

## 2. 需求发现（F-010–F-019）

| F | claim | type | status |
|---|---|---|---|
| F-010 | 她走进上海一家拼豆店 | page_fact | single-source |
| F-011 | 店里有三四十张桌子 | page_fact | single-source |
| F-012 | 老板忙着烫豆 | page_fact | single-source |
| F-013 | 两名店员来回穿梭，还得隔空喊话，确认哪桌要核销、哪桌快到时间、哪桌准备结账 | page_fact | single-source |
| F-014 | 核销要分别打开美团、抖音 | page_fact | single-source |
| F-015 | 计时靠手机 | page_fact | single-source |
| F-016 | 结账还要核对套餐和额外消费 | page_fact | single-source |
| F-017 | 店员要同时照顾几十张桌子，信息反复确认；坐在顾客的位置上这些事也很容易发现 | page_fact | single-source |
| F-018 | 她想到：能不能做个应用，把桌位、计时和订单放到一起，让店员少一些来回切换 | author_claim | single-source |
| F-019 | 「豆掌柜」的想法由此而来 | page_fact | single-source |

## 3. 工具层与开发起点（F-020–F-027）

| F | claim | type | status |
|---|---|---|---|
| F-020 | 2026 年 7 月中旬，玉丹开始开发「豆掌柜」 | page_fact | single-source |
| F-021 | 动手之后才发现，功能能跑起来还只是开头 | author_claim | single-source |
| F-022 | 在外滩黑客松 AI Coding 比赛上，她接触到了 Meoo，尝试用它重新做了一版 | page_fact | single-source |
| F-023 | 重做后生成的界面更简洁，也更符合她的审美 | author_claim | single-source |
| F-024 | 过去需要折腾的服务器、数据库和部署，处理起来也方便了 | author_claim | single-source |
| F-025 | 可以生成访问链接，让别人直接打开 | author_claim | single-source |
| F-026 | 她终于有了一个能带进门店的应用 | page_fact | single-source |
| F-027 | 「豆掌柜」是拼豆店门店管理应用，聚合桌位、计时、订单、核销、在线预约、数据仪表盘与套餐设置 | page_fact | derived |

## 4. 客户开发与三类失败（F-028–F-035）

| F | claim | type | status |
|---|---|---|---|
| F-028 | 王玉丹前后跑了 5 家拼豆店 | page_fact | single-source |
| F-029 | 有的老板已经有类似系统，用不着换 | page_fact | single-source |
| F-030 | 有的店里太忙，没空和她聊 | page_fact | single-source |
| F-031 | 还有的加了联系方式，之后就没有下文 | page_fact | single-source |
| F-032 | 玉丹自称「i 人」，主动走进店里介绍自己做的东西对她来说并不轻松 | page_fact | single-source |
| F-033 | 她为自己做了一个进店沟通的话术导图 | page_fact | single-source |
| F-034 | 跑过几家之后，终于有一家愿意试一试 | page_fact | single-source |
| F-035 | 文章指出「应用做好、展示一下就会有人买单」这一印象容易被各种赚钱故事省略 | author_claim | single-source |

## 5. 试用与迭代（F-036–F-042）

| F | claim | type | status |
|---|---|---|---|
| F-036 | 玉丹提出先免费用一个月 | page_fact | single-source |
| F-037 | 免费使用的前提是老板需要告诉她哪里不好用、还缺什么 | page_fact | single-source |
| F-038 | 为了弄清楚店里的真实需求，她干脆在店里待了整整一周 | page_fact | single-source |
| F-039 | 顾客预约容易遗漏，需要加上在线预约 | page_fact | single-source |
| F-040 | 老板想随时看经营情况，数据仪表盘就得继续完善 | page_fact | single-source |
| F-041 | 套餐设置用着不方便，也要改；需求很琐碎，但店员每天要用的东西往往就卡在这些小地方 | page_fact | single-source |
| F-042 | 整个开发过程中，「豆掌柜」累计迭代了数百次 | page_fact | single-source |

## 6. 成交与后续（F-043–F-050）

| F | claim | type | status |
|---|---|---|---|
| F-043 | 到 2026 年 8 月底，这家店的老板决定购买「豆掌柜」 | page_fact | single-source |
| F-044 | 玉丹的第一个完整的 AI 项目有了付费客户 | page_fact | single-source |
| F-045 | 成交金额为 1 万元 | page_fact | single-source |
| F-046 | 双方约定了一年内免费维护及需求修改 | page_fact | single-source |
| F-047 | 「豆掌柜」能不能继续卖给第二家、第三家，现有的故事还没有给出答案 | page_fact | single-source |
| F-048 | 王玉丹现在仍处于创业初期，主要探索 AI 硬件方向 | page_fact | single-source |
| F-049 | 「豆掌柜」是她学习过程中意外做成的一单 | page_fact | single-source |
| F-050 | 她此前有数字化业务经历，也投入了学习、跑店和驻店时间；不能只留下「年轻人用 AI 赚钱」的结果 | author_claim | single-source |

## 7. 文章的通用建议（F-051–F-057）

| F | claim | type | status |
|---|---|---|---|
| F-051 | 建议从身边一家店开始，注意店员每天在哪些事情上花时间 | author_claim | single-source |
| F-052 | 建议注意：哪些信息总要反复问？哪些步骤一忙起来就容易出错？ | author_claim | single-source |
| F-053 | 文章承认这些问题未必都能做成生意 | author_claim | single-source |
| F-054 | 建议先找一个你接触得到的人，听他工作中具体的麻烦 | author_claim | single-source |
| F-055 | 建议最好看看他实际怎么操作，再决定要不要做一个版本给他试 | author_claim | single-source |
| F-056 | 建议不用急着把功能做全，先看对方愿不愿意用、用完会提出什么问题 | author_claim | single-source |
| F-057 | 建议报价包含什么、哪些修改需另外沟通、后续维护要花多少时间，都该在接单时谈清楚 | author_claim | single-source |

## 8. 结尾互动（F-058–F-060）

| F | claim | type | status |
|---|---|---|---|
| F-058 | 文章结尾邀请读者在评论区聊「想帮谁、解决什么问题」 | page_fact | verified |
| F-059 | 从分享想法的评论中随机抽取 1 位，送出一件 Meoo 定制 Polo 衫 | page_fact | verified |
| F-060 | 开奖时间为 2026 年 10 月 30 日（周五）15:00（北京时间） | page_fact | verified |

## 放弃核验清单（7 项）

| # | 本可核验项 | 未核验原因 |
|---|---|---|
| 1 | 「豆掌柜」应用真实存在与功能范围 | 无公开可访问的应用地址（仅截图） |
| 2 | 是否真的成交、金额是否 1 万元 | 无合同、凭证或第三方报道 |
| 3 | 跑 5 家店的过程细节 | 文章仅给三类失败概括 |
| 4 | 「累计迭代数百次」的精确计数 | 文章为定性表述 |
| 5 | Meoo 是否真能「免服务器/数据库/部署」「生成访问链接」 | 未与官方文档逐条交叉 |
| 6 | 王玉丹后续进展与第二、三家客户 | 文章自述尚无答案（F-047） |
| 7 | 文章配图与截图内容 | 原始配图不落库 |

## 口径提醒

- 「月入过万」为**标题表述**；正文可核的成交事实是**一笔 1 万元**（F-045），不读作持续收入。
- 「豆掌柜」为产品名（F-019），「拼豆店」为场景（F-010）；均为文章用词，未做外部核实。
- 时间口径：文章发布于 2026-10-29（F-003）；案例事件集中于 2026-05 至 2026-08 底（F-006、F-043）。
