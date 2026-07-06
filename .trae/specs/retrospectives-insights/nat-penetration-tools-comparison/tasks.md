# 神卓互联、cpolar、花生壳三款内网穿透工具对比分析 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 补充收集三款产品的完整官方信息
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 访问神卓互联官网（shenzhuohl.com），收集完整的产品矩阵、所有套餐定价、硬件产品、功能特性细节
  - 访问cpolar官网（cpolar.com），收集完整的版本对比、套餐权益、NAS版定价、功能列表
  - 访问花生壳官网（hsk.oray.com），收集个人版/企业版全系列套餐参数、配件价格、硬件产品信息
  - 确认三款产品最新的加密方式、安全机制、SLA承诺等细节
  - 交叉验证代理商页面信息与官方信息的一致性
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-1.1: 三款产品的所有在售套餐（从免费版到最高企业版）的价格、带宽、映射数、并发数均已收集，无遗漏
  - `human-judgement` TR-1.2: 信息为2026年最新有效数据，已标注关键数据的来源页面
- **Notes**: 重点关注花生壳2026年5月带宽升级后的最新参数；神卓互联注意区分"巴比达"品牌与主品牌的套餐差异

## [x] Task 2: 整理产品基本信息与功能特性对比
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 整理三款产品的公司背景、成立时间、产品定位、核心技术路线概述
  - 构建功能特性对比大表：协议支持、带宽限制、流量限制、隧道/映射数量、并发连接数、域名策略（固定/随机/自定义）、P2P直连支持、HTTPS自动证书、DDNS支持、TCP/UDP支持、访问控制粒度、IP白名单/黑名单、密码保护、Web管理界面、API支持等至少15项对比点
  - 整理配套硬件产品列表（穿透盒子、组网盒子）
- **Acceptance Criteria Addressed**: [AC-2, AC-8]
- **Test Requirements**:
  - `human-judgement` TR-2.1: 功能对比表格覆盖至少15项核心功能点，每款产品的支持情况明确标注（支持/部分支持/不支持/需付费版本）
  - `human-judgement` TR-2.2: 功能差异表述准确，无错误描述
- **Notes**: 对于部分支持的功能，需标注哪个版本及以上支持

## [x] Task 3: 整理性能表现与易用性对比
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 构建性能表现对比表：SLA保障等级、服务器节点地域分布、BGP线路情况、带宽上限（单映射/账号总带宽）、重连等待时长、服务器集群规模、容灾链路支持、P2P不限速说明
  - 构建易用性对比表：客户端支持平台（Windows/Mac/Linux/群晖/威联通/飞牛/OpenWrt/Docker/Android/iOS/硬件盒子）、界面类型（Web UI/桌面GUI/CLI/移动端APP）、配置复杂度（零配置/图形化向导/需手动编辑配置文件）、文档质量、新手友好度评分
- **Acceptance Criteria Addressed**: [AC-3, AC-4]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 性能对比包含所有可量化的官方参数
  - `human-judgement` TR-3.2: 易用性评估客观，平台支持列表完整
- **Notes**: 由于不做实际性能测试，性能部分基于官方标称参数和公开用户反馈进行评估

## [x] Task 4: 整理安全性与技术支持对比
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 构建安全性对比表：加密协议（TLS版本/AES加密强度）、客户端-服务端通信加密、访问控制机制（IP黑白名单/访问密码/时间限制/区域限制/浏览器/系统限制）、HTTPS证书部署方式、认证机制、安全配件包、等保合规支持、数据隐私说明
  - 构建技术支持对比表：客服渠道（工单/在线客服/电话/400专线）、支持时间（5×8/7×24）、SLA故障响应时间、专属技术专家（各版本差异）、文档/教程/帮助中心质量、社区支持、1V1顾问服务
- **Acceptance Criteria Addressed**: [AC-5, AC-7]
- **Test Requirements**:
  - `human-judgement` TR-4.1: 安全机制对比清晰，标注哪些功能是付费版专属
  - `human-judgement` TR-4.2: 技术支持等级按套餐区分明确
- **Notes**: 若官方未明确说明加密强度，不做猜测，标注"官方未公开"

## [x] Task 5: 构建价格策略完整对比
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 构建免费版限制对比表：带宽、隧道/映射数、并发数、流量限制、域名类型（固定/随机/轮换周期）、功能限制、SLA情况
  - 构建个人/入门付费套餐对比表
  - 构建中小企业/商业套餐对比表
  - 构建企业/旗舰/臻享套餐对比表
  - 单独列出主要硬件产品（穿透盒子、组网盒子）的价格和年费
  - 总结优惠政策（买赠、升舱活动、续费折扣等）
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `programmatic` TR-5.1: 价格表格完整覆盖三款产品所有在售套餐，价格单位统一为人民币元/年
  - `human-judgement` TR-5.2: 各套餐核心权益列示清晰，活动优惠有标注
- **Notes**: 注意区分"单映射带宽"和"账号总带宽"，避免混淆

## [x] Task 6: 总结优劣势与场景选型建议
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5
- **Description**: 
  - 分别总结三款产品的核心优势（每款至少3点）和主要不足（每款至少2点）
  - 按场景给出明确选型建议：
    1. 个人开发者临时调试/Demo演示
    2. 家庭NAS外网访问/私有云
    3. 微信公众号/小程序开发调试
    4. 小微企业/个体户OA/财务软件远程访问
    5. 中型企业ERP/CRM跨地域办公
    6. 连锁门店/工地视频监控集中传输
    7. 大型企业/政企单位核心业务系统发布
    8. 游戏联机/P2P直连场景
  - 每个场景推荐具体产品和版本，并简要说明理由
- **Acceptance Criteria Addressed**: [AC-8, AC-9]
- **Test Requirements**:
  - `human-judgement` TR-6.1: 优劣势总结客观，基于前面的对比数据，不凭空评价
  - `human-judgement` TR-6.2: 场景建议覆盖至少8种典型场景，推荐明确无歧义
- **Notes**: 可适当提及开源方案（frp等）作为特定场景的补充选项

## [x] Task 7: 生成完整Wiki文档
- **Priority**: high
- **Depends On**: Task 6
- **Description**: 
  - 先读取同目录1-2个现有Wiki文件，确认实际格式（frontmatter风格、章节结构、表格样式）
  - 确定最终文件存放位置：建议在docs/knowledge/learning/07-vendor-product-learning/下新建comparison/子目录（参考sunlogin系列已有comparison目录）
  - 按标准结构撰写Wiki文档：
    1. 概述与背景
    2. 三款产品基本介绍
    3. 功能特性对比（含大表）
    4. 性能表现对比（含大表）
    5. 易用性对比（含大表）
    6. 安全性对比（含大表）
    7. 价格策略对比（含多表格）
    8. 技术支持与服务对比（含大表）
    9. 产品生态与配套硬件
    10. 各产品优劣势总结
    11. 场景化选型建议
    12. 总结
  - 添加正确的YAML frontmatter（id、title、date、tags、source等）
  - 文件命名：nat-penetration-tools-comparison-wiki.md（kebab-case纯英文）
- **Acceptance Criteria Addressed**: [AC-10]
- **Test Requirements**:
  - `programmatic` TR-7.1: 文件命名符合kebab-case纯英文规范，通过文件名检查脚本
  - `programmatic` TR-7.2: YAML frontmatter格式正确，字段完整
  - `human-judgement` TR-7.3: 文档章节结构清晰，表格格式规范，语言专业通顺
- **Notes**: 遵循"格式一致性优先原则"，先看现有同类文档的实际格式，再写文件

## [x] Task 8: 更新知识库索引
- **Priority**: medium
- **Depends On**: Task 7
- **Description**: 
  - 在docs/knowledge/learning/07-vendor-product-learning/下创建comparison/子目录（如不存在）
  - 创建或更新comparison/README.md作为该目录索引
  - 更新docs/knowledge/learning/CATEGORIES.md（如需要）
  - 检查是否有其他相关索引文件需要更新
- **Acceptance Criteria Addressed**: [AC-11]
- **Test Requirements**:
  - `programmatic` TR-8.1: 新Wiki在索引中可被找到，链接路径正确
  - `human-judgement` TR-8.2: 索引条目描述准确，与文档内容一致
- **Notes**: 参考现有sunlogin/comparison目录的索引结构

## [x] Task 9: 整体质量验证与格式检查
- **Priority**: high
- **Depends On**: Task 8
- **Description**: 
  - 运行文件名规范检查脚本，确认文件名合规
  - 检查内部链接有效性
  - 通读全文，核对数据一致性（如价格、带宽数字在各表格中一致）
  - 检查Markdown表格格式完整性（无缺列、无语法错误）
  - 检查专业术语一致性
- **Acceptance Criteria Addressed**: [AC-12]
- **Test Requirements**:
  - `programmatic` TR-9.1: 文件名检查通过
  - `human-judgement` TR-9.2: 通读检查无数据矛盾、无格式错误、无错别字
  - `human-judgement` TR-9.3: 报告整体达到专业IT选型参考水准
- **Notes**: 数据一致性是重点，同一套餐的带宽/价格在不同表格中必须完全一致
