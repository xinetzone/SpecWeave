---
id: "update-yct-onionhead-wiki"
title: "洋葱头（YCT）官网深度学习与Wiki系统性更新"
source: "https://yct.oray.com/"
date: "2026-07-06"
---

# 洋葱头（YCT）官网深度学习与Wiki系统性更新 - Product Requirement Document

## Overview
- **Summary**: 系统性学习贝锐洋葱头（yct.oray.com）官网内容，提取产品定位、核心功能、技术架构、最新动态等关键信息，对现有贝锐综合分析Wiki中的洋葱头章节进行全面更新与补充，消除原文档中标注的"信息有限"问题，确保内容准确、完整、时效性强。
- **Purpose**: 原贝锐综合分析Wiki中洋葱头章节标注了"官网公开信息相对有限"，通过本次深度学习补充完整信息，包括：4A管理架构细节、部署模式（SaaS/私有化）详细说明、版本信息、RPA集成最新动态、内网访问能力、AD域支持、短信助手App等新发现的功能特性。
- **Target Users**: 产品研究人员、SaaS产品经理、企业IT管理者、AI Agent生态研究者、对贝锐产品矩阵感兴趣的学习者。

## Goals
- 全面提取yct.oray.com官网（首页、下载页、新闻页、产品详情文章）的完整信息
- 更新[oray-comprehensive-analysis-wiki.md](file:///d:/AI/docs/knowledge/learning/07-vendor-product-learning/oray/oray-comprehensive-analysis-wiki.md)中3.5节洋葱头章节的内容
- 补充4A管理架构的详细说明、两大应用场景（电商运营/企业办公）的深度描述
- 添加版本信息（Windows/macOS/统信麒麟）、部署模式详细对比（SaaS/私有化）
- 加入最新动态：影刀RPA集成（2026-06-16）实现验证码自动化
- 补充新增功能：AD域对接、内网访问网关、短信助手App、API接口、开发者工具限制等
- 更新支持平台列表（美团/饿了么/抖店/小红书/巨量引擎/知乎知+/快手磁力等）
- 移除原文档中"信息充足度声明"的警告标注，替换为信息来源说明
- 校对所有新增/修改内容，确保与yct.oray.com官网信息一致
- 更新文档frontmatter中的date字段，确保时效性标注准确

## Non-Goals (Out of Scope)
- 不对向日葵、蒲公英、花生壳等其他产品线章节进行修改（除非与洋葱头协同相关的必要补充）
- 不创建新的独立洋葱头单产品Wiki（本次仅更新现有综合Wiki中的对应章节）
- 不进行价格信息的猜测或推断，仅使用官网明确公开的信息
- 不更新OrayOS章节（本次任务聚焦洋葱头）
- 不修改复盘报告目录下的文件

## Background & Context
- 贝锐（Oray）五大产品线综合分析Wiki创建于2026-07-06，原文档中洋葱头（3.5节）标注了"信息充足度声明"，说明官网公开信息有限
- 通过对yct.oray.com的深度抓取（包括首页、下载页、新闻列表页、2026-05-18产品详解文章、2026-06-16 RPA集成新闻），发现了大量原文档未覆盖的详细信息
- 原文档对洋葱头的描述停留在框架层面，缺少版本信息、部署模式细节、内网访问能力、AD域支持、RPA生态集成、短信助手App等关键内容
- 洋葱头作为贝锐产品矩阵中"身份应用层"的关键产品，其完整信息对于理解贝锐"连接→管理→AI执行"战略闭环至关重要
- 现有Wiki文档路径：[oray-comprehensive-analysis-wiki.md](file:///d:/AI/docs/knowledge/learning/07-vendor-product-learning/oray/oray-comprehensive-analysis-wiki.md)

## Functional Requirements
- **FR-1**: 完整提取并整理洋葱头官网所有公开信息，包括产品定位、4A架构、功能矩阵、部署模式、版本信息、支持平台、最新动态
- **FR-2**: 更新3.5.1产品定位章节，明确两大场景（电商运营+企业办公），补充产品概述的完整描述
- **FR-3**: 重写3.5.2核心功能矩阵，补充AD域支持、内网访问网关、短信助手App、API接口、开发者工具限制、Cookie授权登录等新发现功能
- **FR-4**: 新增3.5.3部署模式章节，详细对比SaaS版本与私有化部署的差异（含30分钟极速安装等细节）
- **FR-5**: 新增3.5.4版本信息章节，列出Windows/macOS/统信麒麟的当前版本号、支持系统版本
- **FR-6**: 扩充3.5.5典型应用场景，按电商运营和企业办公两大场景分别详细描述，补充支持的具体平台列表
- **FR-7**: 更新3.5.6量化价值章节，保留原有数据，补充RPA集成带来的24小时无人值守价值
- **FR-8**: 新增3.5.7最新动态章节，记录2026-06-16影刀RPA集成的功能细节和价值
- **FR-9**: 更新3.5.7（原3.5.6）与其他产品协同章节，补充内网访问与蒲公英/花生壳的协同逻辑
- **FR-10**: 更新文档frontmatter，确保source字段包含yct.oray.com，date字段更新为2026-07-06
- **FR-11**: 移除原3.5节开头的"⚠️ 信息充足度声明"警告，替换为信息来源说明
- **FR-12**: 确保所有更新内容与现有文档的格式风格（标题层级、表格样式、emoji使用、引用格式）保持一致

## Non-Functional Requirements
- **NFR-1**: 内容准确性：所有事实性信息必须与yct.oray.com官网内容完全一致，不得添加主观臆断内容（推断内容需明确标注）
- **NFR-2**: 格式一致性：严格遵循现有Wiki文档的格式规范，包括标题层级、表格样式、加粗规则、列表格式、emoji使用习惯
- **NFR-3**: 引用可追溯：关键信息点需能够对应到官网来源页面（可在更新说明中记录来源对应关系）
- **NFR-4**: 结构完整性：更新后的3.5节应包含产品概述、核心架构、功能矩阵、部署模式、版本信息、应用场景、量化价值、最新动态、产品协同等完整子章节
- **NFR-5**: 时效性标注：文档应明确标注信息更新时间为2026-07-06，基于官网2026-05-18至2026-06-16期间的公开内容
- **NFR-6**: 无破坏性变更：不得删除或修改其他产品线（向日葵/蒲公英/花生壳/OrayOS）的现有内容，除非是与洋葱头协同相关的必要补充

## Constraints
- **Technical**: 仅能修改[d:/AI/docs/knowledge/learning/07-vendor-product-learning/oray/oray-comprehensive-analysis-wiki.md](file:///d:/AI/docs/knowledge/learning/07-vendor-product-learning/oray/oray-comprehensive-analysis-wiki.md)这一个文件
- **Business**: 必须基于yct.oray.com官网公开信息，不得编造未公开的功能或价格
- **Dependencies**: 现有Wiki文档的结构和格式、已收集的官网内容（首页/下载页/新闻页/2篇关键文章）

## Assumptions
- yct.oray.com是洋葱头的唯一官方网站，公开信息具有权威性
- 2026-05-18的产品详解文章是官方发布的权威产品介绍，信息准确
- 2026-06-16的RPA集成新闻代表最新功能动态
- 现有Wiki文档中除洋葱头章节外的其他内容无需更新
- 文件名使用kebab-case规范，本次仅更新现有文件不创建新文件

## Acceptance Criteria

### AC-1: 产品定位与架构描述完整准确
- **Given**: 现有Wiki的3.5.1节仅有简短定位描述
- **When**: 完成更新后
- **Then**: 3.5.1节应包含：明确定位为"企业账号管理浏览器"、两大核心场景（电商运营+企业办公）、4A管理架构的完整解释（Account/Authentication/Authorization/Audit各维度详细说明）
- **Verification**: `programmatic` + `human-judgment`
- **Notes**: 内容应与2026-05-18官方文章一致

### AC-2: 核心功能矩阵全面覆盖所有已发现功能
- **Given**: 原功能矩阵仅列出5大类功能
- **When**: 完成更新后
- **Then**: 功能矩阵应至少包含：账号多开与隔离、自动代填与转发（含短信助手App/API）、第三方身份源（飞书/钉钉/企微+AD域）、4A审计（事前/事中/事后三层，含禁止开发者工具）、权限管理、内网访问网关、Cookie授权登录、加密存储等功能点
- **Verification**: `programmatic` + `human-judgment`

### AC-3: 部署模式章节清晰对比SaaS与私有化
- **Given**: 原文档仅简单提及企业版/私有化
- **When**: 完成更新后
- **Then**: 应有专门的部署模式子章节，清晰说明：SaaS版本（开箱即用、按账号订阅、适合快速上手）、私有化部署（30分钟极速安装、数据私有、支持定制开发、适合合规要求高的企业）
- **Verification**: `human-judgment`

### AC-4: 版本信息准确完整
- **Given**: 原文档无版本信息
- **When**: 完成更新后
- **Then**: 应包含版本信息子章节，列出：Windows版3.2.5.0（支持Win10/Win11/Server2019+）、macOS版3.2.5.0、统信麒麟版2.2.6.17、预览版渠道说明
- **Verification**: `programmatic`
- **Notes**: 数据来源为yct.oray.com/download页面

### AC-5: 应用场景描述详细且平台列表完整
- **Given**: 原场景描述较简略
- **When**: 完成更新后
- **Then**: 应按电商运营和企业办公两大场景分别展开，电商场景应明确列出支持平台：美团外卖、饿了么、抖店、小红书、巨量引擎、知乎知+、快手磁力、微信视频号等；企业办公场景应包含内网访问、远程办公、PLC运维等
- **Verification**: `programmatic` + `human-judgment`

### AC-6: 最新动态章节记录RPA集成
- **Given**: 原文档无2026年6月最新动态
- **When**: 完成更新后
- **Then**: 应有最新动态或产品更新子章节，说明2026-06-16影刀RPA集成：验证码API接口、自动调取填充、24小时无人值守、跨平台自动化流程不中断、验证码多端同步+短信助手App配合
- **Verification**: `programmatic` + `human-judgment`

### AC-7: 原信息不足警告移除
- **Given**: 原3.5节开头有"⚠️ 信息充足度声明"警告
- **When**: 完成更新后
- **Then**: 该警告应被移除，替换为合适的信息来源说明（如"本节信息基于yct.oray.com官网2026年5-6月公开内容整理"）
- **Verification**: `programmatic`

### AC-8: 格式与现有文档保持一致
- **Given**: 现有Wiki有统一的格式风格
- **When**: 完成更新后
- **Then**: 更新内容应在标题层级（####/#####）、表格样式、emoji使用、加粗规则、列表格式、引用块等方面与文档其他部分保持一致
- **Verification**: `human-judgment`

### AC-9: 其他产品线内容未被意外修改
- **Given**: 本次任务仅限洋葱头章节
- **When**: 完成更新后
- **Then**: 文档中第1-3.4节、3.6-12节的内容应与更新前完全一致，无意外修改
- **Verification**: `programmatic`（通过git diff验证）

### AC-10: 内容校对完成且与官网一致
- **Given**: 所有更新完成
- **When**: 进行最终校对时
- **Then**: 所有新增事实性信息（版本号、功能描述、量化数据、平台名称、部署时间等）应能在yct.oray.com官网找到对应来源，无编造内容
- **Verification**: `human-judgment`

## Open Questions
- [ ] 是否需要在oray目录的README.md中更新洋葱头相关说明？（本次任务默认不修改，仅更新主Wiki文件）
- [ ] 是否需要同步更新产品系列索引文件sunlogin-product-series-index.md？（该文件是向日葵系列索引，不包含洋葱头，默认不修改）
