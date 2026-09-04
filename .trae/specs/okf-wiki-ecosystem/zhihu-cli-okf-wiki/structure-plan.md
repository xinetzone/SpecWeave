# Zhihu CLI OKF Wiki 结构规划

> 知识包主题：知乎数据开放平台 Zhihu CLI
> 事实总数：105 条（F-001 ~ F-105）
> 规划日期：2026-09-04
> 操作可复现性：是（注册安装、命令使用、Agent 接入均可复现）

---

## 一、目录骨架

```
zhihu-cli/
├── index.md              # 知识包首页
├── concepts/             # 概念层（5-6 篇）
│   ├── 00-platform-overview.md
│   ├── 01-access-architecture.md
│   ├── 02-security-credentials.md
│   ├── 03-core-capabilities.md
│   ├── 04-practical-playbooks.md
│   └── 05-ecosystem-integration.md
├── examples/             # 操作层（3 篇）
│   ├── 01-setup-installation.md
│   ├── 02-core-commands.md
│   └── 03-agent-integration.md
└── references/           # 参考层（3 篇）
    ├── article-source.md
    ├── verification.md
    └── index.md
```

---

## 二、concepts/ 概念层规划

### 00-platform-overview.md

- **知识层级**：事实层
- **核心定位**：解答"这是什么、能做什么、质量如何"
- **主要 F 编号**：F-001 ~ F-010、F-024 ~ F-027、F-030
- **内容大纲**：
  1. 平台定位与价值主张
     - Zhihu CLI 是什么：知乎数据开放平台官方命令行工具
     - 核心价值：公共内容 + 个人数据同时交到 AI 手中
     - 产品阶段：邀测阶段与免费额度（注意时点标注）
  2. 产品矩阵概览
     - 六大核心产品：全网搜索、知乎搜索、直答 Agent、工具、社区数据、知识库
     - 官方 Skills：热榜、站内搜索、全网搜索、直答（4 套）
     - Zhihu CLI 与 Skills 的关系：统一入口 CLI 工具 + Skill
  3. 内容质量保障体系
     - L1-L5 内容分级体系
     - 专业创作者生态
     - 百亿索引规模（厂商自述标注）

### 01-access-architecture.md

- **知识层级**：机制层
- **核心定位**：解答"有哪些接入方式、调用链路是怎样的"
- **主要 F 编号**：F-037、F-046、F-051 ~ F-060、F-099 ~ F-102
- **内容大纲**：
  1. 三种接入方式对比
     - API 直接调用（底层基础）
     - Skill + CLI 组合（Agent 常用）
     - 托管式 MCP 服务（Agent 常用）
     - 三种方式的关系与选择建议
  2. 调用链路详解
     - Skill + CLI 调用链路：自然语言 → AI 按 Skill 指令调用 CLI → CLI 带 Access Secret 请求开放平台 → 返回 JSON → AI 整理
     - MCP 调用链路特点
     - 输出约定：stdout JSON / stderr 诊断 / 稳定 JSON 错误码
  3. 技术架构要点
     - 后端接口共用：三种接入方式共用同一套接口和 Access Secret
     - 全网搜索技术架构：双源融合、分钟级索引、600ms 延迟（厂商自述标注）
     - 流式输出：answer 命令的 SSE/流式响应机制

### 02-security-credentials.md

- **知识层级**：机制层
- **核心定位**：解答"为什么安全、凭证怎么管"
- **主要 F 编号**：F-035、F-036、F-043、F-045、F-061 ~ F-070
- **内容大纲**：
  1. 供应链安全校验
     - 四道校验机制：官方域名、文件大小、SHA-256、二进制自报版本
     - 官方 first-party 技能，HTTPS-only 下载
     - Skill 与 CLI 的安全定位
  2. 凭证管理设计
     - Access Secret 的作用与获取
     - 系统级凭证存储：macOS Keychain / Windows Credential Manager
     - 无明文存储机制
  3. 鉴权与传输安全
     - Bearer Token 鉴权机制
     - X-Request-Timestamp 秒级时间戳校验（⚠️ 待官方确认）
     - HTTPS 通信安全

### 03-core-capabilities.md

- **知识层级**：事实层 + 机制层
- **核心定位**：解答"具体有哪些能力、每个命令怎么用"
- **主要 F 编号**：F-011 ~ F-023、F-028 ~ F-030
- **内容大纲**：
  1. 搜索能力
     - 知乎站内搜索（search zhihu）
     - 全网搜索（search global）：百亿索引、双源融合、分钟级更新、600ms 延迟（厂商自述标注）
     - 两种搜索范围的适用场景
  2. 热榜能力
     - hot / trending 命令
     - 数据来源与更新频率
  3. 直答能力
     - ask / answer 命令
     - 流式输出特性
     - 知识库对接能力
  4. 个人数据能力
     - me contents：我的创作
     - me followees：我的关注
     - me favorites：我的收藏
  5. 辅助命令
     - quota：额度查询
     - 输出格式约定

### 04-practical-playbooks.md

- **知识层级**：应用层
- **核心定位**：解答"可以用来做什么、有哪些创意玩法"
- **主要 F 编号**：F-071 ~ F-095
- **内容大纲**：
  1. 创作生涯全身体检
     - 全量拉取个人创作数据
     - 数据分析维度：年产量、赞同数、收藏数、创作方向分布
     - 可视化：赞同×收藏散点图识别高价值内容
  2. 写作风格蒸馏
     - 全量正文作为专属语料
     - 风格提炼维度：论证结构、段落长度、术语密度、惯用类比、开头结尾方式
     - 输出：个人专属写作 Skill
  3. 选题雷达
     - 定时热榜监控
     - 个人创作领域标签匹配
     - 选题灵感发现
  4. 其他创意应用
     - 智能硬件看板
     - 飞书定时推送热榜
     - AI loop engineering 思路

### 05-ecosystem-integration.md

- **知识层级**：应用层
- **核心定位**：解答"支持哪些平台、怎么和其他工具集成"
- **主要 F 编号**：F-041、F-042、F-096 ~ F-105
- **内容大纲**：
  1. Agent 平台支持
     - Codex Agent 集成
     - Claude Code Agent 集成
     - Cursor Agent 集成
     - 各平台 Skill / MCP 两种接入方式
  2. 平台兼容性
     - Linux 平台支持
     - Windows 平台注意事项（PowerShell 5.1 UTF-8 BOM 坑）
     - macOS 凭证存储特性
  3. 第三方生态
     - 社区封装工具：zhihu-search（作者 klarkxy）
     - 飞书等办公工具集成
     - 智能硬件场景
     - 社区生态发展现状

---

## 三、examples/ 操作层规划

### 01-setup-installation.md

- **知识层级**：操作层
- **核心定位**：从零到一完成注册、安装、验证
- **主要 F 编号**：F-031 ~ F-040、F-044、F-048 ~ F-050
- **内容大纲**：
  1. 前置准备
     - 知乎账号准备
     - 实名认证流程
  2. 获取 Access Secret
     - 访问 developer.zhihu.com
     - 登录与实名认证
     - 获取并保存 Access Secret
  3. CLI 安装
     - 方式一：通过 Skill 自动安装（推荐 Agent 场景）
     - 方式二：uv 手动安装（社区推荐）
     - 安装验证
  4. Windows 安装避坑
     - PowerShell 版本要求
     - UTF-8 BOM 问题处理

### 02-core-commands.md

- **知识层级**：操作层
- **核心定位**：常用命令的实操指南与示例
- **主要 F 编号**：F-011 ~ F-023、F-089 ~ F-094
- **内容大纲**：
  1. 搜索命令实战
     - 知乎站内搜索示例
     - 全网搜索示例
     - 输出结果解读
  2. 热榜命令实战
     - 获取热榜
     - 结果字段说明
  3. 直答命令实战
     - 基础提问
     - 流式输出体验
  4. 个人数据命令实战
     - 拉取我的创作
     - 查看我的关注/收藏
  5. 额度查询
     - quota 命令使用
     - 额度限制说明

### 03-agent-integration.md

- **知识层级**：操作层
- **核心定位**：在主流 Agent 中配置 Zhihu CLI / MCP
- **主要 F 编号**：F-031、F-037、F-041、F-042、F-096 ~ F-102
- **内容大纲**：
  1. Skill + CLI 方式接入
     - Claude Code 配置步骤
     - Cursor 配置步骤
     - Codex 配置步骤
  2. MCP 方式接入
     - 托管式 MCP 服务介绍
     - 配置步骤
     - 适用场景对比
  3. 验证与调试
     - 验证接入成功
     - 常见问题排查
     - stderr 诊断信息使用

---

## 四、references/ 参考层规划

### article-source.md
- 全部 105 条事实登记（F-001 ~ F-105）
- 与 facts.md 保持双份一致
- 带 frontmatter 和来源说明

### verification.md
- P0 核验报告（14 项）
- 勘误汇总（3 条）
- 厂商自述数据清单（8 项）
- 时效边界说明

### index.md
- toctree 导航
- 参考层说明
- 快速跳转表

---

## 五、知识层级分布统计

| 层级 | 篇数 | 文档 | 主要 F 编号范围 |
|------|------|------|----------------|
| 事实层 | 2 篇 | 00-platform-overview、03-core-capabilities（部分） | F-001~F-010, F-011~F-023, F-024~F-030 |
| 机制层 | 2.5 篇 | 01-access-architecture、02-security-credentials、03-core-capabilities（部分） | F-037, F-043, F-046, F-051~F-070 |
| 应用层 | 2 篇 | 04-practical-playbooks、05-ecosystem-integration | F-071~F-105 |
| 操作层 | 3 篇 | examples/ 下 3 篇 | F-031~F-050, F-089~F-102 |
| 参考层 | 3 篇 | references/ 下 3 篇 | 全部 F 编号 |

---

## 六、作者观点与厂商自述标注策略

- 📝 作者观点：在对应文档中以"社区观点"或"作者经验"形式标注，不视为客观事实
- [厂商自述] 数据：统一以"官方宣称"或"厂商公开数据"表述，并在 verification.md 集中声明无法独立核验
- 口径差异：如老狼创作数据等，在涉及的文档中同时列出两种口径并说明差异原因
