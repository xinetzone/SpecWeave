---
id: "harness-engineering-facts"
title: "Harness Engineering 文章事实清单"
source: "微信公众号文章《新ClaudeCode和Codex变得越来越强的5个Harness设计》"
x-toml-ref: "../../../../../.meta/toml/.trae/specs/retrospectives-insights/harness-engineering-seven-concepts-analysis/facts.toml"
---

# Harness Engineering 文章事实清单

> **质量门G1**: 事实清单中无因果词（因为/所以/导致/错误/失误），所有条目均为客观陈述

---

## 一、文章基本信息

F001. 文章标题为《新 ClaudeCode 和 Codex 变得越来越强的 5 个 Harness 设计》
F002. 文章来源为微信公众号"皇子谈技术"
F003. 文章发布于2026年7月13日
F004. 文章引用了Lilian Weng的论文《Harness Engineering for Self-Improvement》
F005. 文章引用了OpenAI的论文《Unrolling the Codex agent loop》
F006. 文章引用了Zhang et al. 2025的论文《Agentic Context Engineering》
F007. 文章引用了Ye et al. 2026的论文《Meta Context Engineering via Agentic Skill Evolution》
F008. 文章引用了Lee et al. 2026的论文《Meta-Harness》

---

## 二、Harness 概念与定义

F009. Harness被定义为模型接入真实世界之前的运行骨架
F010. Harness需要解决5件事：Workflow、Tools、Permissions、Memory、Evaluation/Recovery
F011. 模型像引擎，Harness像整辆车的比喻被用于解释两者关系
F012. Prompt只是Harness的一个输入面
F013. 真正决定上限的是runtime如何组织整个工作过程
F014. Coding agent harness结构图展示了完整的运行架构
F015. 最小harness loop包含chooseTool、runTool、updateContext、saveArtifacts、shouldStop五个环节

---

## 三、五个Harness设计要点

### 设计1：Workflow设计

F016. Workflow设计不是问一句答一句的单轮问答
F017. 真正的Harness是持续推进任务的loop
F018. loop流程为：目标进来→规划→调用工具→观察结果→再决策→再执行
F019. 这层被称为workflow orchestration
F020. 模型只负责think，外部loop负责执行

### 设计2：文件系统做记忆

F021. 长任务系统不能把所有东西都硬塞进prompt
F022. 文件系统作为持久记忆是长任务Agent的关键模式
F023. 文件具有分层、归档、搜索、跨轮次重用、中断后恢复的特性
F024. 类比后端系统的冷热分层：热数据放内存，冷数据放持久层
F025. 成熟Harness的目录结构被描述为一套工作现场

### 设计3：子代理分工

F026. 主代理的核心价值是做判断、做归纳、做收敛
F027. 高噪音、强搜索、弱决策的工作应下放给子代理
F028. 子代理可专门负责翻日志、找文件、找测试缺口、做代码审查
F029. 主代理只接收子代理的摘要结果
F030. 这被称为上下文污染隔离
F031. Subagent本质上是给Agent runtime做职责分层

### 设计4：权限与恢复机制

F032. 模型本身不知道操作风险高低
F033. 编辑本地文件与删除目录的风险等级不同
F034. 跑测试与force push到主分支的风险等级不同
F035. 成熟Harness需要有权限分层和失败恢复机制
F036. 权限分为：可直接做、需提醒、必须停下来问人三个级别
F037. 失败后系统需要具备继续执行的能力，而非直接终止
F038. 类比后端系统的熔断+回滚+人工确认机制

### 设计5：Context Engineering

F039. ACE（Agentic Context Engineering）将上下文视为不断演化的playbook
F040. MCE（Meta Context Engineering）优化的是管理上下文的方法本身
F041. Meta-Harness是端到端优化模型Harness的方向
F042. AI工程下一阶段的竞争对象从prompt内容转向上下文构造方法
F043. 优化方向包括：从成功轨迹和失败轨迹中持续沉淀可复用的结构化经验

---

## 四、技术对比与工程类比

F044. 同样是MySQL，有的系统跑起来像丝滑的交易引擎，有的系统一到大促就抖
F045. MySQL性能差异源于连接池、事务边界、缓存策略、限流、重试、索引设计、故障恢复
F046. Agent runtime被类比为带状态的workflow engine
F047. 子代理分工被类比为网关或异步任务编排
F048. 文件系统记忆被类比为后端系统的冷热分层

---

## 五、能力要求与学习路径

F049. 后端/架构/技术负责人接下来最值得补充4个能力：任务拆解、上下文治理、权限与恢复设计、评估与反馈闭环
F050. 学习路径第1步：读Lilian Weng原文建立完整地图
F051. 学习路径第2步：读OpenAI的Codex loop文章理解基础执行循环
F052. 学习路径第3步：用Claude Code的subagent和docs功能实践上下文隔离
F053. 学习路径第4步：自己写一个最小harness demo，从文件系统持久记忆开始
F054. 学习路径第5步：回头看ACE/MCE/Meta-Harness理解context engineering的优化目标

---

## 六、趋势判断

F055. 模型之间的纯能力差距还在，但正在变得没那么决定性
F056. 长任务、真项目、真实仓库越来越考验运行时设计
F057. AI编程工具的进化方向已从Prompt工程转向workflow、memory、subagent、permission、context engineering
F058. AI编程工具的竞争正在从"谁更会答题"走向"谁更像一个靠谱的工程同事"
F059. Harness正在变成AI时代的软件工程基本功

---

**事实总数**: 59条

**质量门G1验证**: 本清单中未出现"因为/所以/导致/错误/失误"等因果判断词，符合七概念方法论质量门G1要求。
