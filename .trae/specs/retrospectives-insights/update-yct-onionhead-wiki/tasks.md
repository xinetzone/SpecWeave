# 洋葱头（YCT）官网深度学习与Wiki系统性更新 - The Implementation Plan (Decomposed and Prioritized Task List)

## [ ] Task 1: 信息整理与更新准备
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 整理已收集的洋葱头官网所有内容（首页、下载页、新闻列表、2026-05-18产品详解、2026-06-16 RPA集成新闻）
  - 阅读现有[oray-comprehensive-analysis-wiki.md](../../../../docs/knowledge/learning/07-vendor-product-learning/oray/oray-comprehensive-analysis-wiki.md)的3.5节完整内容，确认需要更新的具体位置
  - 对照现有文档格式风格（标题层级、表格样式、emoji使用等），确保更新时风格统一
  - 备份原文件或确认git状态，便于验证无意外修改
- **Acceptance Criteria Addressed**: [AC-8, AC-9]
- **Test Requirements**:
  - `programmatic` TR-1.1: 能够清晰列出需要更新的子章节（3.5.1-3.5.7）
  - `human-judgement` TR-1.2: 整理的信息素材完整，覆盖所有已发现的新功能点
- **Notes**: 重点关注原3.5节从第357行开始的内容边界

## [ ] Task 2: 更新文档frontmatter和3.5节开头
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 更新文档frontmatter中的date字段为2026-07-06
  - 确认source字段已包含https://yct.oray.com/
  - 移除3.5节开头的"⚠️ 信息充足度声明"警告块
  - 替换为信息来源说明："本节信息基于yct.oray.com官网2026年5-6月公开内容整理（含2026-05-18产品详解、2026-06-16 RPA集成更新）"
- **Acceptance Criteria Addressed**: [AC-7, AC-10]
- **Test Requirements**:
  - `programmatic` TR-2.1: frontmatter中date字段值为"2026-07-06"
  - `programmatic` TR-2.2: 原"信息充足度声明"文本不再出现在文档中
  - `human-judgement` TR-2.3: 新的来源说明表述自然、符合文档风格
- **Notes**: 使用Edit工具精确替换，避免影响其他内容

## [ ] Task 3: 更新3.5.1产品定位与核心价值
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 明确产品定位为"企业账号管理浏览器"
  - 补充两大核心场景：国内电商运营 + 企业办公与IT管理
  - 添加4A管理架构（Account/Authentication/Authorization/Audit）的详细解释
  - 保留原有的核心价值主张并进行扩充
  - 补充：账号从录入到登录均加密存储、业务数据独立存储于企业私有空间
- **Acceptance Criteria Addressed**: [AC-1, AC-10]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 4A四个维度都有清晰解释
  - `programmatic` TR-3.2: 包含"企业账号管理浏览器"、"电商运营"、"企业办公"等关键词
  - `human-judgement` TR-3.3: 描述与2026-05-18官方文章一致
- **Notes**: 参考现有其他产品章节（如3.2、3.3、3.4）的写作风格

## [ ] Task 4: 重写3.5.2核心功能矩阵
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 扩充核心功能矩阵表格，新增以下功能模块：
    - 账号统一管理：补充Cookie授权无感知登录、账号加密存储
    - 自动代填与转发：补充短信助手App（手机端实时接收）、API接口支持、验证码智能过滤定向转发
    - 第三方身份源：补充AD域对接支持（原有飞书/钉钉/企微保留）
    - 内网访问能力：新增模块，说明通过访问网关访问内网系统，无需单独部署VPN
    - 行为审计与安全：补充禁止打开开发者工具、屏幕快照记录
    - 权限与组织管理：补充外包/供应商协作管理、内网业务授权访问
  - 确保表格格式与现有功能矩阵表格一致
- **Acceptance Criteria Addressed**: [AC-2, AC-8, AC-10]
- **Test Requirements**:
  - `programmatic` TR-4.1: 功能矩阵包含AD域、内网访问、短信助手App、API、开发者工具限制等关键词
  - `human-judgement` TR-4.2: 表格列数、样式与3.2.2/3.3.2/3.4.2的功能矩阵一致
  - `human-judgement` TR-4.3: 功能分类逻辑清晰，无遗漏重要功能
- **Notes**: 表格两列结构：功能模块 | 具体功能

## [ ] Task 5: 新增3.5.3部署模式章节
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 插入新的"#### 3.5.3 部署模式"子章节（在核心功能矩阵之后）
  - 说明两种部署模式：
    - **SaaS版本**：开箱即用，按账号灵活订阅，适合快速上手及轻量化协作管理
    - **私有化部署**：通用脚本极速安装（平均30分钟完成部署），所有数据存储在企业私有网络，支持定制化开发，适合有严格合规与保密要求的企业
  - 调整后续子章节编号（原3.5.3版本价格→3.5.4，以此类推）
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `programmatic` TR-5.1: 包含"SaaS"、"私有化"、"30分钟"等关键词
  - `human-judgement` TR-5.2: 两种模式的适用场景描述清晰
  - `programmatic` TR-5.3: 后续子章节编号正确顺延（3.5.3→新版本价格→3.5.4，等等）
- **Notes**: 参考其他产品的版本/部署章节结构

## [ ] Task 6: 调整并扩充版本与价格章节（原3.5.3→新3.5.4）
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 将原3.5.3版本价格体系调整为3.5.4
  - 保留原有价格信息（月付低至3元/账号、企业版/私有化面议）
  - 新增版本号和支持系统信息：
    - Windows版本：3.2.5.0，支持Win10、Win11、Server2019及以上版本
    - macOS版本：3.2.5.0
    - 统信/麒麟版本：2.2.6.17
    - 预览版渠道：可抢先体验新功能
- **Acceptance Criteria Addressed**: [AC-4, AC-10]
- **Test Requirements**:
  - `programmatic` TR-6.1: 包含版本号"3.2.5.0"、"2.2.6.17"
  - `programmatic` TR-6.2: 包含支持系统"Win10"、"Win11"、"Server2019"、"macOS"、"统信"、"麒麟"
  - `human-judgement` TR-6.3: 版本信息展示方式清晰易读
- **Notes**: 数据来源为yct.oray.com/download页面

## [ ] Task 7: 扩充3.5.5典型应用场景（原3.5.4→新3.5.5）
- **Priority**: medium
- **Depends On**: Task 6
- **Description**: 
  - 将原3.5.4量化价值调整到后面，本章节专注场景
  - 按两大场景分别详细描述：
    - **国内电商运营场景**：面向代运营及电商客服团队，明确列出支持平台：美团外卖、饿了么商家后台、抖店、小红书、巨量引擎、知乎知+、抖音巨量、小红书聚光、微信视频号、快手磁力等
    - **企业办公与IT管理场景**：面向中大型企业的数据保护及远程办公需求，包含内网NAS/系统访问、PLC设备远控运维、业务数据私有存储等
  - 保留原有的三个场景要点并整合到新结构中
- **Acceptance Criteria Addressed**: [AC-5, AC-10]
- **Test Requirements**:
  - `programmatic` TR-7.1: 包含"美团外卖"、"饿了么"、"抖店"、"小红书"、"巨量引擎"、"知乎知+"、"快手"等平台名称
  - `human-judgement` TR-7.2: 两大场景区分清晰，描述符合官网内容
  - `programmatic` TR-7.3: 包含"PLC"关键词（特殊运维场景）
- **Notes**: 注意平台名称准确，不要写错

## [ ] Task 8: 更新量化价值章节（原3.5.5→新3.5.6）并新增最新动态（新3.5.7）
- **Priority**: medium
- **Depends On**: Task 7
- **Description**: 
  - 保留原有四个量化数据（1分钟授权、1.5小时/天、80%投诉下降、120倍效率提升）
  - 新增"#### 3.5.7 最新动态：影刀RPA集成（2026-06-16）"子章节：
    - 洋葱头验证码接口与影刀RPA结合
    - 自动化脚本可直接调取短信验证码并自动填入
    - 无需人工填码，实现24小时无人值守全自动化运营
    - 支持多平台自动登录、批量发布、跨平台数据采集
    - 验证码多端同步接收+短信助手App方案，支持智能过滤和定向转发
- **Acceptance Criteria Addressed**: [AC-6, AC-10]
- **Test Requirements**:
  - `programmatic` TR-8.1: 保留四个原有量化数据（1分钟、1.5小时、80%、120倍）
  - `programmatic` TR-8.2: 包含"影刀RPA"、"24小时无人值守"、"API"、"2026-06-16"等关键词
  - `human-judgement` TR-8.3: RPA集成价值描述清晰准确
- **Notes**: 新闻链接可标注为来源：https://yct.oray.com/news/53766

## [ ] Task 9: 更新产品协同章节（原3.5.6→新3.5.8）
- **Priority**: medium
- **Depends On**: Task 8
- **Description**: 
  - 将原3.5.6协同章节调整为3.5.8
  - 保留原有的协同逻辑推断
  - 补充内网访问能力与蒲公英/花生壳的协同说明：
    - 洋葱头访问网关+蒲公英组网：实现远程安全访问内网，无需额外VPN
    - 洋葱头+向日葵：身份认证→远程控制的闭环，操作审计联动
  - 保留"基于集团逻辑推断"的标注
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `human-judgement` TR-9.1: 协同逻辑描述合理，与新增的内网访问功能一致
  - `programmatic` TR-9.2: 仍保留推断内容的明确标注
- **Notes**: 推断内容需明确标注，不要作为确定性功能描述

## [ ] Task 10: 全文格式统一与编号检查
- **Priority**: high
- **Depends On**: Task 9
- **Description**: 
  - 检查3.5节所有子章节编号（3.5.1-3.5.8）正确连续
  - 检查标题层级（####）与其他产品章节一致
  - 检查表格样式、列表格式、emoji使用与全文风格统一
  - 检查加粗规则是否一致（关键术语加粗）
  - 更新目录导航（如需要）——注意目录是手动维护的，检查第二章到第三章等其他部分是否需要更新（本次仅洋葱头，目录无需大改）
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `programmatic` TR-10.1: 子章节编号从3.5.1到3.5.8连续无跳号
  - `human-judgement` TR-10.2: 视觉上格式与3.2/3.3/3.4节一致
- **Notes**: 使用Read工具通读更新后的完整3.5节

## [ ] Task 11: 验证无意外修改+内容校对
- **Priority**: high
- **Depends On**: Task 10
- **Description**: 
  - 使用git diff验证：只有3.5节和frontmatter被修改，其他章节（1-3.4、3.6-12）无变化
  - 逐项核对所有新增事实信息：
    - 版本号与下载页一致
    - 功能描述与2026-05-18文章一致
    - RPA集成描述与2026-06-16新闻一致
    - 平台列表准确无误
    - 部署时间（30分钟）准确
  - 通读3.5节全文，确保语句通顺、逻辑连贯
- **Acceptance Criteria Addressed**: [AC-9, AC-10]
- **Test Requirements**:
  - `programmatic` TR-11.1: git diff显示修改范围仅限frontmatter和3.5节区域
  - `human-judgement` TR-11.2: 所有事实性信息都能在官网内容中找到对应来源
  - `human-judgement` TR-11.3: 全文通读无明显错别字、语句不通顺问题
- **Notes**: 这是最终质量把关，必须认真完成
