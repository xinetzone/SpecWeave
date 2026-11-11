# R 阶段事实台账：字节 AI 产品线收口 → OKF 知识包

> 本文件与 bundle 内 `references/article-source.md` 构成**双份 F 登记**，两集合须一致：F-001~F-049，连续无跳号。
> 主信源：微信公众号「运营派 AI Lab」《字节AI大洗牌，扣子和TRAE陨落》，作者欧阳俊杰。
> URL：https://mp.weixin.qq.com/s/ibCX76N6j82B10AEn2SN9g
> 采集时间：2026-11-11 11:42 (+08:00)。页面未显示发布日期，仅显示"修改于"。

## Source Manifest

| source_id | 标题 | 类型 | 访问时点 | 状态 |
|---|---|---|---|---|
| article | 字节AI大洗牌，扣子和TRAE陨落（运营派 AI Lab / 欧阳俊杰） | 主信源·行业评论 | 2026-11-11 11:42 | collected |
| coze-official | 扣子企业版下线公告（docs.coze.cn） | 官方公告 | 2026-11-11 11:55 | collected |
| trae-merge-report | 硅星人《TRAE 合并 Code 与 Work：能力向外扩展，开发继续深入》2026-10-09 | 媒体一手实测 | 2026-11-11 12:00 | collected |
| sina-finance | 新浪财经《独家｜字节AI生产力整合：TRAE、扣子并入豆包》2026-08-24 | 权威媒体 | 2026-11-11 12:05 | resolved-via-search |
| sohu-account | 搜狐《字节TRAE账号将于11月18日升级为豆包飞书账号》2026-11-06 | 媒体转述 | 2026-11-11 12:02 | collected |
| doubao-work-bundle | 库内既有束 `doubao-work`（APPSO 2026-08-25 实测） | 内部交叉参照 | 2026-11-11 11:50 | collected |

## 事实台账

| F | claim | type | source_id | locator | status |
|---|---|---|---|---|---|
| F-001 | 文章标题为《字节AI大洗牌，扣子和TRAE陨落》，署名欧阳俊杰，发布号"运营派 AI Lab" | page_fact | article | 页头 | verified |
| F-002 | 文章主题为一个月内字节调整三条 AI 产品线，并给出整合到豆包体系的判断 | page_fact | article | 导语 | verified |
| F-003 | 2026年10月29日，扣子发布企业版下线公告 | page_fact | article | 第1节 | verified |
| F-004 | 2026年11月30日起，扣子企业标准版、企业旗舰版停止接受新客户购买 | page_fact | article | 第1节 | verified |
| F-005 | 2026年12月31日，在火山引擎购买的旧版套餐全面下线 | page_fact | article | 第1节 | verified |
| F-006 | 2027年12月31日，新版企业标准版、企业旗舰版全面下线 | page_fact | article | 第1节 | verified |
| F-007 | 已购客户可在对应套餐全面下线前按合同约定继续使用 | page_fact | article | 第1节 | verified |
| F-008 | 文章称本次调整针对企业版套餐，扣子个人版未宣布全面停服 | page_fact | article | 第1节 | verified |
| F-009 | 2026年10月9日，字节宣布将 TraeWork 与 TraeCode 合并为全新的 TRAE | page_fact | article | 第1节 | verified |
| F-010 | 合并前，TraeWork 偏向办公、任务和内容生成 | page_fact | article | 第1节 | verified |
| F-011 | 合并前，TraeCode 专注专业编程 | page_fact | article | 第1节 | verified |
| F-012 | 合并后两款产品变为一个统一入口，支持 Agent 与 IDE 两种模式 | page_fact | article | 第1节 | verified |
| F-013 | Agent 模式负责任务拆解、工具调用和多项目协作 | page_fact | article | 第1节 | verified |
| F-014 | IDE 模式保留专业代码编辑、调试和开发能力 | page_fact | article | 第1节 | verified |
| F-015 | 2026年10月23日，旧版 TraeWork 独立客户端结束服务，相关能力转入新版 TRAE | page_fact | article | 第1节 | single-source/flagged |
| F-016 | 2026年11月6日，TRAE 发布账号升级公告 | page_fact | article | 第1节 | verified |
| F-017 | 自2026年11月18日起，TRAE 中国版个人用户账号自动升级为豆包飞书账号 | page_fact | article | 第1节 | verified |
| F-018 | 企业客户不在本次账号升级范围内 | page_fact | article | 第1节 | single-source |
| F-019 | 升级后原有代码、项目、历史记录、会员权益和积分均予以保留 | page_fact | article | 第1节 | verified |
| F-020 | 升级后同一账号可登录豆包 App、飞书、PICO、火山引擎、豆包输入法等产品 | page_fact | article | 第1节 | single-source |
| F-021 | 2026年8月，字节对 AI 办公产品线进行团队整合，TRAE、扣子团队整体并入豆包体系 | page_fact | article | 第2节 | verified |
| F-022 | 整合方案中，TRAE Work、扣子与豆包在工作场景的产品能力进行整合 | page_fact | article | 第2节 | verified |
| F-023 | 整合方案中，TRAE IDE 与 CLI 作为豆包品牌下的编程产品线继续发展 | page_fact | article | 第2节 | verified |
| F-024 | 2026年8月下旬，豆包工作正式亮相 | page_fact | article | 第2节 | verified |
| F-025 | 豆包工作可围绕用户目标拆解任务、调用工具、推进复杂工作流程 | page_fact | article | 第2节 | verified |
| F-026 | 豆包工作可与飞书打通，在用户权限范围内调用文档、表格、知识库等工作资料 | page_fact | article | 第2节 | verified |
| F-027 | 作者判断：字节正在把分散的 AI 产品和能力逐步整合到豆包体系中 | author_claim | article | 导语/第2节 | n/a |
| F-028 | 作者判断：产品入口在减少，背后的能力在重新组合 | author_claim | article | 第1节末 | n/a |
| F-029 | 作者判断：大厂争夺的第一层价值是用户入口，即用户打开电脑后首先使用的 AI 产品 | author_claim | article | 第3节 | n/a |
| F-030 | 作者判断：第二层价值是连接工作上下文（聊天记录、文档、会议纪要、项目资料） | author_claim | article | 第3节 | n/a |
| F-031 | 作者判断：第三层价值是掌握任务执行与结果交付 | author_claim | article | 第3节 | n/a |
| F-032 | 作者判断：入口、上下文与执行连接后，产品价值从"模型回答多好"转为"能否把事做完" | author_claim | article | 第3节 | n/a |
| F-033 | 作者判断：只给通用模型套一层界面并提供几个常见功能的 AI 产品，在大厂集成同类能力后容易失去优势 | author_claim | article | 第4节 | n/a |
| F-034 | 作者判断：独立 AI 产品的竞争力来自独有行业数据、深入专业工作流、稳定业务系统集成与长期用户信任 | author_claim | article | 第4节 | n/a |
| F-035 | 作者判断：竞争重点将从"推出更多 AI 工具"转为"连接模型、Agent、工具与用户工作流" | author_claim | article | 第4节 | n/a |
| F-036 | 作者判断：成为用户完成任务的第一入口，更有机会掌握下一阶段 AI 生态 | author_claim | article | 第4节 | n/a |
| F-037 | 文章标题用"陨落"描述扣子与 TRAE 两条产品线 | page_fact | article | 标题 | verified |
| F-038 | 文章未给出任何量化数据（市场份额、时长、收入、用户数） | page_fact | article | 全文 | verified |
| F-039 | 文章未给出官方公告链接，也未标注第三方数据来源 | page_fact | article | 全文 | verified |
| F-040 | 文章把三件事概括为"短短一个月"内发生 | page_fact | article | 导语 | verified |
| F-041 | 文章未提及扣子个人版于同期发布的套餐价格调整公告 | page_fact | article | 全文 | verified |
| F-042 | 文章未区分 TRAE 中国版与海外版、个人版与企业版的账号策略差异 | page_fact | article | 全文 | verified |
| F-043 | 文章未给"团队并入豆包"一事的报道出处或公告编号 | page_fact | article | 第2节 | verified |
| F-044 | 文章结论将竞争定义为"超级入口之争" | page_fact | article | 第4节末 | verified |
| F-045 | 页面未显示发布日期，仅显示"修改于" | page_fact | article | 页尾 | verified |
| F-046 | 官方 FAQ：企业版套餐到期后 14 天内仍可续费，超过 14 天按新购处理 | page_fact | coze-official | 公告·常见问题 | verified |
| F-047 | 官方公告：旧版套餐超出 2026-12-31 的未使用部分自动退款至火山引擎账户 | page_fact | coze-official | 公告·客户服务与退款安排 | verified |
| F-048 | 官方公告：对话、记忆、文件、编程项目、低代码工作流的导出与备份安排将在后续公告明确 | page_fact | coze-official | 公告·常见问题 | verified |
| F-049 | 扣子官网公告列表存在《扣子个人版套餐价格调整公告》（路径 subscription-plan-adjustment-20261112），个人版仍在运营并调价 | page_fact | coze-official | 文档站·定价/活动与公告/公告 | verified |

## G1 自检

- 事实 49 条（≥20）。
- 事实区无"因为/所以/导致/失误"等因果或判断词；作者判断统一标 `author_claim` 并写明"作者判断"。
- 关键日期、阶段、范围均可回查官方公告或权威媒体。
