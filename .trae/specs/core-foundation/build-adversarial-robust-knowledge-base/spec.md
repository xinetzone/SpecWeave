# 对抗式健壮知识库系统 - Product Requirement Document

## Overview
- **Summary**: 基于卡兹克《Vibe Coding 两大神级 Prompt》方法论（第一性原理+对抗式审查），对现有项目知识管理系统进行增强升级，构建一个具备自我对抗测试能力、分级加密存储、完整性自校验、异常防御机制的健壮知识库系统。系统采用本地文件系统+Git部署形态，Python脚本+现有多Agent体系实现，确保知识资产的安全存储、智能检索与抗损毁能力。
- **Purpose**: 解决现有知识库缺乏健壮性保障的问题——防止文件损坏/篡改、检索逻辑漏洞、异常输入崩溃、Git误操作丢失、未授权访问、数据泄露等风险，通过"第一性原理管生成（知识分类与关联）+对抗式审查管验证（多Agent攻防测试）"的闭环机制，建立可自我验证、自我修复的高可靠性知识管理体系。
- **Target Users**: 项目AI智能体（Architect/Developer/Reviewer等角色）、项目维护者、知识贡献者

## Goals
- 基于第一性原理重构知识分类体系，从知识本质属性出发而非类比推理建立分类与关联
- 实现分级加密存储机制（public/internal/confidential三级安全级别）
- 建立完整性自校验与自动修复机制（动态伪装=校验和+冗余+自愈）
- 实现多Agent对抗式审查工作流，定期从攻击者视角测试知识库健壮性
- 建立异常输入防御体系，防止恶意/畸形数据导致系统崩溃
- 实现Git分布式版本控制与本地冗余备份，确保知识可追溯、可恢复
- 与现有.agents体系无缝集成，不破坏现有工作流

## Non-Goals (Out of Scope)
- 不构建客户端-服务器架构或Web UI（保持纯本地文件系统+Git形态）
- 不引入重量级数据库或外部服务依赖
- 不实现P2P分布式传播（Git本身已提供分布式能力）
- 不做复杂的访问控制UI（基于文件系统权限和加密密钥管理）
- 不重写现有知识库的基础功能（目录结构、YAML frontmatter、索引生成均复用现有实现）
- 不实现实时的网络爬取防护（本地系统无对外网络接口）

## Background & Context
- 现有基础：项目已有`docs/knowledge/`目录结构、YAML frontmatter标准格式、`generate_index.py`索引生成脚本，基础知识管理系统已完成
- 方法论依据：卡兹克《Vibe Coding 两大神级 Prompt》提出"第一性原理管生成+对抗式审查管验证"的闭环方法论，已在本项目通过AIHOT案例和2026-07-09类比错误反面案例验证
- 第一性原理应用：知识分类不从现有目录结构类比，而是从"知识本质上是什么、如何被使用、如何失效"重新推导
- 对抗式审查应用：模拟恶意用户/异常场景对知识库进行攻击测试，包括：
  - 超大文件/畸形输入
  - 文件损坏/篡改
  - 检索逻辑边界条件
  - Git误操作场景
  - 加密/解密边界
  - 索引生成异常

## Functional Requirements
- **FR-1**: 基于第一性原理的知识分类体系增强
- **FR-2**: 分级加密存储（public/internal/confidential三级）
- **FR-3**: 完整性自校验与自动修复机制（动态伪装）
- **FR-4**: 多Agent对抗式审查工作流
- **FR-5**: 异常输入防御与边界检查
- **FR-6**: Git版本控制集成与冗余备份
- **FR-7**: 智能检索增强与查询验证
- **FR-8**: 现有Agent体系集成

## Non-Functional Requirements
- **NFR-1**: 性能：索引生成与完整性校验在1000个知识条目内完成时间<30秒
- **NFR-2**: 可靠性：单文件损坏不影响整体系统运行，自动检测并修复可修复的损坏
- **NFR-3**: 安全性：confidential级别知识加密存储，无密钥无法读取明文
- **NFR-4**: 兼容性：完全向后兼容现有知识库格式，不破坏现有条目
- **NFR-5**: 可审计性：所有审查、修复、加密操作均有结构化日志记录
- **NFR-6**: 可维护性：新增代码遵循项目现有风格，脚本放入`.agents/scripts/`共享库

## Constraints
- **Technical**: 
  - Python 3.x作为脚本语言（与现有项目一致）
  - 加密使用Python标准库（cryptography可选作为增强）
  - 复用现有`.agents/scripts/lib/`共享工具库
  - 遵循项目现有开发规范（kebab-case文件名、YAML frontmatter、Conventional Commits）
- **Business**: 
  - 纯本地运行，不依赖外部网络服务
  - 不增加新的重量级第三方依赖
- **Dependencies**:
  - 现有`docs/knowledge/`目录结构
  - 现有`.agents/`多Agent工作流体系
  - Git版本控制系统
  - Python标准库（hashlib、json、os、sys等）

## Assumptions
- 用户/智能体在访问confidential级知识时能提供正确的加密密钥
- Git已正确初始化并可正常使用
- 运行环境为Windows/macOS/Linux，Python 3.8+可用
- 现有知识条目将逐步迁移到新的分级安全体系，不要求一次性全量迁移
- 对抗式审查定期执行（每2-3周一次，与卡兹克推荐节奏一致）

## Acceptance Criteria

### AC-1: 第一性原理知识分类体系
- **Given**: 现有知识库目录结构
- **When**: 从知识本质属性（事实性知识/程序性知识/条件性知识/元认知知识）出发重新设计分类增强
- **Then**: 分类体系支持多维标签（知识类型、安全级别、验证状态、复用次数），不破坏原有目录结构，提供从本质属性检索的能力
- **Verification**: `human-judgment`
- **Notes**: 原有operations/platform/troubleshooting/decisions/best-practices分类保留，增加知识本质维度的元数据标签

### AC-2: 分级加密存储
- **Given**: 知识条目frontmatter包含security_level字段
- **When**: security_level=public时明文存储；security_level=internal时元数据加密、正文明文；security_level=confidential时全文加密
- **Then**: 
  - public条目与现有格式完全兼容，Git diff正常工作
  - internal条目元数据字段（如author、source）不可直接读取，需解密
  - confidential条目无密钥无法读取任何内容
  - 加密/解密通过命令行脚本调用，提供统一接口
- **Verification**: `programmatic`
- **Notes**: 使用AES-256-GCM对称加密，密钥从环境变量或本地密钥文件读取

### AC-3: 完整性自校验与自动修复
- **Given**: 每个知识条目存储时生成校验和（SHA-256）
- **When**: 系统读取知识条目时
- **Then**: 
  - 自动校验文件完整性，校验失败立即报告
  - 若存在Git历史版本，自动从最近正确版本恢复（自愈）
  - 若文件部分损坏，尽可能提取可读内容并标记
  - 校验和嵌入frontmatter的integrity字段，不单独存储
- **Verification**: `programmatic`
- **Notes**: 这就是"动态伪装机制"的核心——通过校验和+版本控制实现"看起来正常但能自发现自修复"

### AC-4: 多Agent对抗式审查工作流
- **Given**: 触发对抗式审查命令（手动或定期）
- **When**: 启动N个Agent并发执行
- **Then**: 
  - Agent从攻击者视角构造测试用例：超大文件、畸形frontmatter、未来时间戳、空值/超长值、特殊字符、路径遍历攻击等
  - 覆盖所有入口点：索引生成、检索查询、加密解密、完整性校验
  - 发现漏洞生成结构化审查报告，包含复现步骤、风险等级、修复建议
  - 审查报告存入`docs/retrospective/`体系
- **Verification**: `programmatic` + `human-judgment`
- **Notes**: 审查频率建议每2-3周一次，对应卡兹克实践节奏

### AC-5: 异常输入防御
- **Given**: 畸形/恶意输入（超大文件、特殊字符、路径遍历等）
- **When**: 知识库脚本处理输入时
- **Then**: 
  - 不崩溃、不挂死、不执行危险操作
  - 输入验证失败返回清晰错误信息
  - 文件大小限制（单条目<5MB）
  - 路径遍历防护（禁止访问`docs/knowledge/`外的文件）
  - 所有外部输入都经过sanitize处理
- **Verification**: `programmatic`

### AC-6: Git集成与冗余备份
- **Given**: 知识库变更提交到Git
- **When**: 执行备份命令或Git提交时
- **Then**: 
  - 自动校验变更前后完整性
  - 支持本地冗余备份到指定目录
  - 提供"知识时光机"：可查询任意Git版本的知识状态
  - 检测到大规模文件损坏时，自动从Git恢复
- **Verification**: `programmatic`

### AC-7: 检索增强与查询验证
- **Given**: 用户/Agent查询知识库
- **When**: 执行检索时
- **Then**: 
  - 检索结果自动验证完整性，排除损坏条目
  - 支持按知识本质类型、安全级别、验证状态过滤
  - 查询输入经过边界检查，防止注入
  - 返回结果包含完整性状态标记
- **Verification**: `programmatic`

### AC-8: Agent体系集成
- **Given**: 现有.agents角色定义
- **When**: 各角色执行任务时
- **Then**: 
  - AGENTS.md增加对抗式健壮知识库的引用
  - Reviewer角色增加对抗式审查职责
  - Architect角色在沉淀知识时使用第一性原理分类
  - 所有角色在读取知识时自动验证完整性
  - 提供标准命令集：`/knowledge encrypt`、`/knowledge verify`、`/knowledge review`、`/knowledge backup`
- **Verification**: `human-judgment`

### AC-9: 向后兼容性
- **Given**: 现有知识条目（无security_level、无integrity字段）
- **When**: 新系统读取旧条目时
- **Then**: 
  - 正常读取，默认security_level=public
  - 自动补全缺失的元数据字段（不修改原文件直到显式迁移）
  - 索引生成正常工作
  - 提供迁移脚本帮助用户逐步升级旧条目
- **Verification**: `programmatic`

## Open Questions
- [ ] 加密密钥的存储位置与管理方式（环境变量vs本地密钥文件vs用户输入）
- [ ] 对抗式审查的Agent数量默认配置（参考卡兹克40个Agent的实践，但本地环境可能需要调整）
- [ ] 是否需要实现知识条目之间的语义关联图谱（第一性原理的关联vs简单标签）
- [ ] 冗余备份的默认存储位置与保留策略
