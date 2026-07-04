# 国内 Skill/MCP 生态盘点学习与 Wiki 教程文档 - 实施计划

## [x] Task 1: 创建 Wiki 教程文档基础框架与目录导航
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 docs/knowledge/learning/ 目录下创建 domestic-skill-mcp-ecosystem-wiki.md 文件
  - 添加符合规范的 YAML frontmatter（title/source/date/tags）
  - 创建完整的目录导航系统，包含所有章节的锚点链接
  - 添加原文参考链接和文章基本信息（作者：卡兹克、可达）的开头引用
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-9]
- **Test Requirements**:
  - `programmatic` TR-1.1: 文件存在于正确路径 docs/knowledge/learning/domestic-skill-mcp-ecosystem-wiki.md
  - `programmatic` TR-1.2: frontmatter 包含所有必填字段（title/source/date/tags），使用 YAML 格式（---包裹）
  - `human-judgement` TR-1.3: 目录导航结构完整，所有章节链接可跳转
  - `programmatic` TR-1.4: 包含原文 URL
- **Notes**: 参考 the-agency-project-wiki.md 和 text-to-cad-wiki.md 的文档结构和格式

## [x] Task 2: 编写概念入门章节（Skill/MCP/CLI 三种集成方式）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 解释 Skill 的定义：面向 Agent 使用者的能力封装，类似"插件"，用户一句话即可安装使用
  - 解释 MCP 的定义：Model Context Protocol，面向开发者的标准化上下文协议，能力更强但需技术接入
  - 解释 CLI 的定义：命令行工具，面向开发者，可被 Claude Code 等编程 Agent 调用
  - 提供三者对比表格（面向人群/技术门槛/能力范围/典型场景）
  - 引用原文通俗解释："对于大家来说，其实都是把网址扔过去然后说给我安装其实就行了"
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `human-judgement` TR-2.1: 三个概念定义准确清晰
  - `human-judgement` TR-2.2: 对比表格维度合理，差异突出
  - `human-judgement` TR-2.3: 通俗解释引用得当
  - `human-judgement` TR-2.4: 适用人群说明准确

## [x] Task 3: 编写餐饮行业盘点章节（瑞幸咖啡、麦当劳）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 瑞幸咖啡 Skill（open.lkcoffee.com）：
    - 支持 Skill、MCP、CLI 三种方式
    - 核心能力：点咖啡、推荐饮品、定位门店、扫码支付
    - 使用体验：能根据健康需求（如心脏不舒服不喝咖啡因）推荐饮品
    - 杯型选择特点：大杯、特大杯、超大杯，唯独没有中杯
    - 局限：目前只支持到店自取，不支持外卖
    - 支付方式：扫码支付（不打通最后一公里）
  - 麦当劳 MCP（https://open.mcd.cn/mcp）：
    - 核心能力：查活动日历、领券
    - 支付方式：最后一步需跳 app 完成支付
- **Acceptance Criteria Addressed**: [AC-4, AC-5]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 两个品牌的集成形态和核心能力说明完整
  - `human-judgement` TR-3.2: 瑞幸的使用体验细节（推荐、杯型、自取）说明准确
  - `human-judgement` TR-3.3: 支付跳转方式说明清晰
  - `programmatic` TR-3.4: 包含两个品牌的官方平台链接

## [x] Task 4: 编写出行行业盘点章节（飞猪、滴滴、高德、腾讯地图）
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 飞猪 Skill（https://flyai.open.fliggy.com/）：
    - 底层接自己的 MCP 服务，无需 API Key 即可试用
    - 核心能力：机票、酒店、门票、用车咨询规划预订
    - 使用体验：规划杭州周末游，列出航班表（航司/时间/时长/价格/首选备选性价比）和酒店
    - 体验版数据有缺失，完整能力需申请 API Key
  - 滴滴 Skill（https://mcp.didichuxing.com/）：
    - 2024 年 9 月上线 MCP，2025 年 4 月上线 Skill
    - 核心能力：实时叫车、预约出行、订单查询、查看司机位置
    - 特色设计：能直接提醒司机状态，可组合 hook 触发飞书电话
  - 高德地图 Skill（https://lbs.amap.com/）：
    - 2024 年 7 月推出 MCP，2025 年 4 月上线 Skill 市场
    - 涵盖：位置服务、地图开发、Android Agent、iOS Agent、RTOS 地图
    - 使用体验：搜索杭州余杭区酒店，生成 5 公里范围搜索链接，列出名称/评分/地址/图片
  - 腾讯地图 Skill（https://lbs.qq.com）：
    - 提供 Skill 和 MCP
    - 核心能力：搜索、规划、天气查询、模型展示
    - 差异点：多一个前端地图开发 Skill，支持 3D 地图、Three.js 集成、GLTF 模型
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-4.1: 四个品牌的集成形态和核心能力说明完整
  - `human-judgement` TR-4.2: 上线时间线准确（滴滴、高德）
  - `human-judgement` TR-4.3: 高德与腾讯地图的差异点说明清晰
  - `programmatic` TR-4.4: 包含四个品牌的官方平台链接

## [x] Task 5: 编写跑腿与办公协作章节（美团跑腿、飞书、钉钉、企业微信、腾讯文档）
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 美团跑腿 Skill（github.com/meituan/MT-Paotui-For-Client）：
    - 2025 年 6 月发布
    - 特色设计：地址簿优先匹配（不用每次重输）、订单预览卡片确认后提交
    - 支付方式：需打开 app 操作
  - 飞书 Skill/CLI/MCP（https://open.feishu.cn/?lang=zh-CN）：
    - 三种形态都有，办公协作主战场
    - CLI 在三月份开源
  - 钉钉 Skill/CLI/MCP（https://open.dingtalk.com/）：
    - 三种形态都有
    - 覆盖：消息、待办、日程、审批流
    - 与飞书功能高度重叠，选哪个看公司用哪家
  - 企业微信 CLI/Skill/MCP（github.com/WecomTeam/wecom-cli）：
    - 核心能力：消息收发、通讯录管理
  - 腾讯文档 Skill/MCP（https://docs.qq.com/open/document/）：
    - 核心能力：创建编辑在线文档、知识库管理、AI PPT 生成
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-5.1: 五个品牌的集成形态和核心能力说明完整
  - `human-judgement` TR-5.2: 美团跑腿的地址簿和订单预览设计亮点说明清晰
  - `human-judgement` TR-5.3: 飞书与钉钉的功能对比客观准确
  - `programmatic` TR-5.4: 包含五个品牌的官方平台/GitHub 链接

## [x] Task 6: 编写支付能力章节（支付宝、微信支付）与"最后一公里"信任难题分析
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 支付宝 Skill/MCP（https://open.alipay.com/）：
    - 2024 年 4 月推出国内首个支付 MCP
    - 覆盖：手机支付、网页支付、订单查询、退款、退款查询五项能力
    - 后续推出支付集成 Skill，面向开发者（收钱的人用）
    - 可让 AI 快速接入支付能力：生成收款链接、创建订单、查状态、退款
    - 完整收款闭环，个人开发者也可用
  - 微信支付 Skill/MCP（https://github.com/wechatpay-apiv3/wechatpay-skills）：
    - 2024 年开放 MCP（仅腾讯元器可用），2025 年 4 月上线 Skill
    - 面向开发者：判断支付产品类型、给示例代码、检查代码安全
    - 支持商品券：发券、核销、查询、退券
  - "支付最后一公里"信任难题深度分析：
    - 现象：几乎所有付钱环节都让用户跳出去自己完成（瑞幸扫码、麦当劳跳 app、美团跑腿打开 app）
    - 技术维度：技术上轻轻松松就能做到 Agent 直接付款
    - 社会维度：整个社会的信任上还没到那一步
    - 生态维度：信任不是靠一两个产品能建起来，需要整个生态慢慢磨
- **Acceptance Criteria Addressed**: [AC-4, AC-5]
- **Test Requirements**:
  - `human-judgement` TR-6.1: 两个支付品牌的集成形态和核心能力说明完整
  - `human-judgement` TR-6.2: 三个维度的信任难题分析深入（技术/社会/生态）
  - `human-judgement` TR-6.3: 三种支付跳转方式（瑞幸/麦当劳/美团）列举准确
  - `human-judgement` TR-6.4: 引用原文"技术上轻轻松松就能做到，但整个社会的信任上，还没到那一步"
  - `programmatic` TR-6.5: 包含两个支付品牌的官方平台/GitHub 链接

## [x] Task 7: 编写内容创作章节（微信读书、网易云音乐、美图）
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 微信读书 Skill（weread.qq.com/r/weread-skills）：
    - 2025 年 5 月推出
    - 核心能力：查书架、看阅读进度、统计阅读时长/天数、检索笔记划线、搜索书籍、查看详情、根据偏好推荐相似书
  - 网易云音乐 Skill/CLI（github.com/NetEase/skills）：
    - 2025 年 3 月推出
    - 核心能力：搜索、播放音乐、歌单管理、红心歌单偏好画像分析
  - 美图 CLI/Skill（https://www.miraclevision.com/open-claw）：
    - 同步上线 CLI 和 Skill
    - 核心能力：图片编辑、文生图、文生视频、AI 写真、换脸、虚拟换装、背景替换
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-7.1: 三个品牌的集成形态和核心能力说明完整
  - `human-judgement` TR-7.2: 上线时间准确（微信读书 5 月、网易云 3 月）
  - `human-judgement` TR-7.3: 美图的 AI 能力列表完整
  - `programmatic` TR-7.4: 包含三个品牌的官方平台/GitHub 链接

## [x] Task 8: 编写第三方集成章节（千问、豆包、WorkBuddy）
- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - 区分两种模式：独立发布 Skill vs 在 AI 产品中集成第三方服务
  - 千问（通义千问）：
    - 2025 年 1 月接入淘宝、支付宝、淘宝闪购、飞猪、高德等阿里生态
    - 2025 年 6 月开放第三方 Skill，肯德基、蜜雪冰城、东方航空首批接入
  - 豆包：
    - 2025 年 6 月 22 日上线打车服务，接曹操出行，灰测中
  - WorkBuddy（腾讯产品）：
    - 内置大量 Skill 和 MCP
    - 集成微信支付 AI 专属卡、QQ 邮箱、腾讯文档、腾讯 ima、腾讯问卷、微云等腾讯系能力
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `human-judgement` TR-8.1: 两种模式（独立发布 vs 集成第三方）区分清晰
  - `human-judgement` TR-8.2: 三个 AI 产品的集成策略和生态布局说明准确
  - `human-judgement` TR-8.3: 时间线准确（千问 1 月/6 月、豆包 6 月 22 日）
  - `human-judgement` TR-8.4: 千问的两阶段策略（接入阿里生态+开放第三方）说明清晰

## [x] Task 9: 编写趋势洞察章节（Agent 化窗口期与贾维斯愿景）
- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - 核心论点 1：Agent 化时代正在到来
    - 我们正在向一个逐渐全面 Agent 化的时代过渡
    - 当 Agent 能点咖啡、叫出租车、查航班、发飞书消息、发邮件、管理文档、搜酒店，最后自循环完成支付
  - 核心论点 2：2017 年小程序类比
    - 当前阶段类似 2017 年小程序刚出来时
    - 当时大家觉得没啥用，三年后很多品牌都在做，特别是与现实交互多的
    - Skill 和 MCP 现在处于窗口期，先做的人在探路，大量品牌在观望
    - 趋势已不可逆
  - 核心论点 3：贾维斯愿景
    - Agent 不再只是工具，慢慢变成数字世界里的另一个自己
    - 或者说，是我们每个人心中的那个贾维斯
    - 名单还会越来越长
- **Acceptance Criteria Addressed**: [AC-7]
- **Test Requirements**:
  - `human-judgement` TR-9.1: 三个核心论点阐述完整
  - `human-judgement` TR-9.2: 2017 年小程序类比贴切，时间对比清晰
  - `human-judgement` TR-9.3: 贾维斯愿景引用原文"它在慢慢变成你在数字世界里的另一个自己"
  - `human-judgement` TR-9.4: 语言有洞察力，与开篇形成呼应

## [x] Task 10: 编写 FAQ 常见问题解答章节
- **Priority**: medium
- **Depends On**: Task 9
- **Description**:
  - 整理常见问题并提供解答，如：
    - Q: Skill、MCP、CLI 有什么区别？我该用哪个？
    - Q: 普通用户可以使用这些 Skill 吗？需要技术背景吗？
    - Q: 为什么所有支付环节都要跳出去自己完成？
    - Q: 飞书和钉钉的 Skill 功能差不多，该怎么选？
    - Q: 高德地图和腾讯地图的 Skill 有什么差异？
    - Q: 千问接入的第三方 Skill 和品牌独立发布的 Skill 有什么不同？
    - Q: Agent 化浪潮现在处于什么阶段？
    - Q: 这些 Skill 都是免费的吗？
    - Q: 如何让自己的产品也支持 Skill/MCP？
    - Q: 国内 Skill/MCP 生态未来会如何发展？
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `human-judgement` TR-10.1: 至少包含 8 个 FAQ 问题
  - `human-judgement` TR-10.2: 问题覆盖概念/安装/支付/选型/趋势等维度
  - `human-judgement` TR-10.3: 解答清晰准确，引用前文章节内容

## [x] Task 11: 编写相关资源链接章节
- **Priority**: medium
- **Depends On**: Task 10
- **Description**:
  - 原文链接：微信公众号文章 URL
  - 餐饮类：瑞幸（open.lkcoffee.com）、麦当劳（https://open.mcd.cn/mcp）
  - 出行类：飞猪（https://flyai.open.fliggy.com/）、滴滴（https://mcp.didichuxing.com/）、高德（https://lbs.amap.com/）、腾讯地图（https://lbs.qq.com）
  - 跑腿类：美团跑腿（github.com/meituan/MT-Paotui-For-Client）
  - 办公协作类：飞书（https://open.feishu.cn/?lang=zh-CN）、钉钉（https://open.dingtalk.com/）、企业微信（github.com/WecomTeam/wecom-cli）、腾讯文档（https://docs.qq.com/open/document/）
  - 支付类：支付宝（https://open.alipay.com/）、微信支付（https://github.com/wechatpay-apiv3/wechatpay-skills）
  - 内容创作类：微信读书（weread.qq.com/r/weread-skills）、网易云音乐（github.com/NetEase/skills）、美图（https://www.miraclevision.com/open-claw）
- **Acceptance Criteria Addressed**: [AC-9]
- **Test Requirements**:
  - `programmatic` TR-11.1: 原文链接正确
  - `programmatic` TR-11.2: 16 个品牌的官方平台/GitHub 链接完整
  - `human-judgement` TR-11.3: 资源按行业分类清晰

## [x] Task 12: 更新知识库索引 README.md
- **Priority**: high
- **Depends On**: Task 11
- **Description**:
  - 在 docs/knowledge/README.md 的 learning 分类表格中新增本教程条目
  - 条目包含：标题、摘要、日期（2026-07-04）、标签（skill、mcp、cli、ai-agent、ecosystem、domestic、wechat、feishu、dingtalk、payment）
  - 遵循现有索引格式，保持表格结构一致
- **Acceptance Criteria Addressed**: [AC-10]
- **Test Requirements**:
  - `programmatic` TR-12.1: README.md 中 learning 分类新增了条目
  - `human-judgement` TR-12.2: 摘要准确概括教程内容
  - `human-judgement` TR-12.3: 标签设置合理
  - `programmatic` TR-12.4: 表格格式保持一致
