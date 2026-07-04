---
id: "harness-engineering-wiki-04"
title: "实战案例：悟空AI招聘"
source: "https://mp.weixin.qq.com/s/0w_xMwto4sLx6J_85OhWQw?from=industrynews&color_scheme=light#rd"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/harness-engineering-wiki/04-wukong-case-study.toml"
date: "2026-07-04"
category: "learning"
---

# 实战案例：悟空AI招聘

## 案例背景

悟空是钉钉的企业级Agent，本案例是其中的**AI招聘系统**。

- 每天处理上千份简历
- 已稳定运行数月
- 数据声明：本文数字来自内部实测，仅代表本场景，不构成通用基准

## 第一版："全能招聘Agent"的失败

### 架构
- 1个"万能Agent"
- 13个工具
- 600+行Prompt

### 五大病灶

| 问题 | 表现 |
|------|------|
| **上下文炸** | 600行Prompt+13个工具描述+对话历史，上下文经常超限，模型读到后面忘了前面 |
| **工具选错率高** | 13个工具摆在面前，Agent经常选错，比如该调用score_match时调用了chat_reply |
| **Prompt遗忘** | Prompt太长，模型读到200行后开始幻觉，前面写的规则后面忘了 |
| **状态全在上下文里** | 会话一断，所有进度丢失；想断点续传？做梦；想debug？不知道之前发生了什么 |
| **错误难复现** | 状态全在Context里，同样的输入，不同的对话历史可能导致不同结果，bug无法稳定复现 |

## 第二版："2 Agent + N Skill"架构

### 角色分工

1. **悟空（Orchestrator，主Agent）**
   - 职责：拆任务、分发给Sub-Agent、维护Workspace、跨会话记忆
   - 工具：仅最基础的任务分发和状态管理工具
   - Prompt：精简的编排逻辑

2. **人岗匹配Agent（Sub-Agent 1）**
   - 职责：RPA操作、JD简历解析、批量打分
   - 工具：4个（RPA操作、简历解析、匹配度计算、结果写入）
   - Prompt：约80行

3. **招聘沟通Agent（Sub-Agent 2）**
   - 职责：监听聊天、自动对话、协商面试时间
   - 工具：5个（消息监听、消息发送、日历查询、会议室预订、状态更新）
   - Prompt：约90行

4. **N个Skill（技能）**
   - 每个Skill是一个原子函数，有明确签名
   - 示例：`parse_resume`、`score_match`、`query_calendar`、`book_room`、`send_message`
   - 无独立Context，哪个Agent需要就调用哪个

### Workspace文件结构

```
workspace/
├── candidates/
│   └── {candidate_id}/
│       └── state.json       # 候选人状态：new/parsed/matched/contacted/interviewed
├── jobs/
│   └── {job_id}/
│       └── jd.md            # 职位描述
├── chat_history.log         # 沟通日志（追加写入）
└── rpa_lock/
    └── {batch_id}.json      # RPA事务锁：running/done/failed
```

## 五条铁律落点

| 铁律 | 在悟空招聘里的落点 |
|------|-------------------|
| 上下文越少越好 | 每个Agent的Prompt控制在100行以内，Sub-Agent只看到自己需要的4-5个工具，Context不膨胀 |
| 专才Agent赢通才 | 2个专才Sub-Agent（人岗匹配+招聘沟通），而非1个万能Agent；Agent总数严格控制在3个以内（悟空+2个Sub-Agent） |
| 状态写文件不塞上下文 | 所有状态写入Workspace：candidates/{id}/state.json、chat_history.log、rpa_lock；Context只加载当前步骤需要的状态 |
| 能写成Linter不写文档 | 合规规则写成Linter/检查函数：比如"发送给候选人的消息必须经过合规检查"，用代码强制拦截，不是靠Prompt里写"请遵守合规要求" |
| Agent昂贵Skill廉价 | 只有3个Agent，Skill可以无限加；能用Skill解决的绝不加Agent |

## 改造前后对比

| 维度 | 全能Agent（第一版） | 专才架构（第二版） |
|------|-------------------|-------------------|
| 工具选择错率 | 高（经常选错工具） | 显著下降（每个Agent只有4-5个工具） |
| 准确率 | 不稳定，无法生产 | 达标，已上线生产运行 |
| 可调试性 | 小时级定位（要翻长对话历史） | 分钟级定位（看Workspace状态文件即可） |
| 可复用性 | 低（代码逻辑耦合在Prompt里） | 高（人岗匹配Agent已复用到两个场景） |
| 上下文消耗 | 高（经常超限） | 显著下降（每个Agent Context精简） |
| 新增需求成本 | 数天（改600行Prompt，牵一发动全身） | 半天（加Skill或调整对应Sub-Agent） |

## 三条血泪经验

### 经验1：Agent数量不要超过3个，Skill可以无限加

- 实测：Agent堆到6个时，编排层（Orchestrator）开始选错Agent——"该派给谁"本身成了新问题
- 建议：先想清楚能不能用Skill解决，确实需要独立Context/独立工具集/独立Prompt时再加Agent
- 经验值：**3个Agent是甜蜜点**，超过就要反思是不是拆太细了

### 经验2：RPA+Agent接缝处要做"事务边界"

RPA（浏览器/桌面自动化）是Agent最容易出问题的地方，因为外部世界不可控：
- RPA点了按钮，页面没加载出来
- 操作到一半网络断了
- 页面结构变了，选择器失效

**解法：lock文件机制**
1. 开始RPA操作前：写入`rpa_lock/{batch_id}.json`，状态标为`running`，记录开始时间、操作参数
2. 操作完成后：状态标为`done`，记录结果
3. 异常中断时：下次启动先检查lock文件，如果有`running`状态的任务，从断点续传，而不是从头开始

这就是数据库里的事务概念——用文件锁实现RPA操作的原子性和可恢复性。

### 经验3：对外说话的Agent必须接三层硬护栏

凡是Agent要**对外发消息**（给候选人发消息、发邮件、操作用户数据），必须有三层硬护栏，缺一不可：

| 层级 | 护栏机制 | 作用 |
|------|---------|------|
| 第一层 | 白名单工具 | Agent只能调用白名单内的"发送"工具，不能自己写代码直接发请求 |
| 第二层 | Linter拦截 | 消息内容经过代码检查：敏感词、合规规则、语气检查，不通过直接打回 |
| 第三层 | 第二个Agent审稿 | 换一个全新Context的Reviewer Agent，以"怀疑的HR"身份审核消息内容，确认没问题才放行 |

**为什么要三层？**
- 第一层：从入口限制能力，从根源上防止Agent乱调用
- 第二层：机器快速过滤80%的低级错误，成本低速度快
- 第三层：最后一道防线，处理那些Linter难以覆盖的语义问题

三层护栏会增加延迟和成本，但**对外说话和动用户数据的地方，这个钱不能省**。一次事故的代价远大于护栏成本。
