---
version: "1.0"
---
# 项目全面敏感信息脱敏检查 - Product Requirement Document

## Overview
- **Summary**: 对 SpecWeave 项目主权区代码与文档进行全面的敏感信息识别、分类与脱敏处理，建立自动化敏感信息检测能力，并生成详细的脱敏检查报告。检查范围覆盖源代码文件、配置文件、文档、注释、日志文件等，处理个人身份信息、账号密码、API密钥、数据库连接信息、内部网络地址、商业机密等各类敏感数据。
- **Purpose**: 项目代码库中存在部分个人信息泄露风险（如用户名路径、个人邮箱、手机号引用、会话标识符等），且现有 .gitignore 对环境变量文件的排除不够完善。需要系统性排查并修复这些问题，同时建立常态化检测机制，确保符合《数据安全法》《个人信息保护法》要求。
- **Target Users**: 项目维护者、代码审查者、安全合规人员

## Goals
- 全面扫描并识别项目主权区内所有类型的敏感信息
- 对发现的敏感信息按类型采取适当脱敏措施（替换/屏蔽/删除/占位符）
- 修复 .gitignore 中环境变量文件排除规则的缺口
- 建立自动化敏感信息检测脚本，可集成到 CI 流水线
- 生成详尽的脱敏检查报告，记录发现问题、处理方法与结果
- 确保脱敏处理不影响系统功能与文档可读性

## Non-Goals (Out of Scope)
- 不修改 `vendor/` 子模块内的文件（第三方/自有协作子模块通过 gitlink 管理，问题需反馈上游）
- 不修改 `external/` 和 `playground/` 目录（已被 .gitignore 排除，不纳入版本控制）
- 不处理历史 Git 提交记录中的敏感信息（如需清理需单独执行 git history rewrite）
- 不实现实时数据脱敏（仅处理静态代码/文档中的敏感信息）
- 不处理 `.env` 文件本身（已被 .gitignore 排除，仅完善排除规则）

## Background & Context
- 项目已建立数据安全治理规则体系（见 `.agents/rules/data-security/`），包含数据分类分级、脱敏技术规范等
- vendor 区域 flexloop 子模块已有信息脱敏规范（`vendor/flexloop/apps/chaos/.agents/rules/information-sanitization.md`）
- 现有 `.agents/rules/detection-and-reporting/` 包含硬编码检测规则，但缺少专门的敏感信息扫描脚本
- 初步扫描已发现：个人用户目录路径 `C:\Users\xinzo\` 多处泄露、真实手机号引用、会话标识符长字符串、.gitignore 环境变量排除缺口等问题

## Functional Requirements
- **FR-1**: 敏感信息扫描识别
  - 支持识别以下敏感信息类型：个人身份信息（姓名、身份证号、手机号、邮箱）、认证凭据（密码、API密钥、Token、Secret Key）、数据库连接信息、内部IP地址、个人文件路径、会话/设备标识符、支付信息
  - 覆盖文件类型：Python源代码(.py)、Markdown文档(.md)、JSON/YAML/TOML配置文件(.json/.yaml/.yml/.toml)、环境变量文件(.env*)、Shell脚本(.sh/.ps1/.bat)
  - 支持排除 vendor/、external/、playground/、__pycache__/、.git/ 等目录
  - 区分真实敏感值与占位符/示例值（如 `your-api-key-here`、`localhost`、`192.168.x.x` 示例IP等）

- **FR-2**: 敏感信息分类与风险分级
  - 按照项目数据分类分级标准（L1-L4）对发现的敏感信息分级
  - 高风险（L3/L4）：真实密钥、真实密码、完整身份证号、真实支付信息
  - 中风险（L2）：真实手机号、真实个人邮箱、个人文件路径、内部IP地址
  - 低风险（L1）：示例占位符、测试数据、公开联系方式

- **FR-3**: 脱敏处理
  - 个人文件路径：将 `C:\Users\xinzo\` 替换为通用占位符 `<USER_HOME>\` 或 `~`
  - 真实手机号：中间四位替换为 `****`（如 `132****8023`）
  - 个人邮箱：用户名部分脱敏或替换为通用占位符（如 `developer@example.com`）
  - 会话/设备标识符：评估后决定脱敏或删除
  - 示例IP/localhost：保留但标记为示例（如非真实内部地址）
  - 所有脱敏处理需确保文档上下文可理解、代码功能不受影响

- **FR-4**: .gitignore 规则完善
  - 补充 `.env.staging`、`.env.production`、`.env.development` 等环境文件的排除规则
  - 补充其他可能包含敏感信息的常见文件名模式

- **FR-5**: 自动化检测脚本
  - 创建 `.agents/scripts/check-sensitive-info.py` 脚本
  - 支持命令行参数：`--path` 指定扫描路径、`--fix` 自动修复可修复项、`--json` JSON格式输出、`--verbose` 详细输出
  - 输出包含：文件路径、行号、敏感信息类型、匹配内容、风险等级、建议处理方式

- **FR-6**: 脱敏检查报告生成
  - 生成 Markdown 格式的详细报告
  - 报告包含：扫描范围、扫描统计、发现问题清单（位置/类型/风险等级/处理状态）、处理方法说明、残留风险说明、预防措施建议
  - 报告保存至 `.agents/reports/sensitive-info-audit-YYYYMMDD.md`

## Non-Functional Requirements
- **NFR-1**: 性能：单次全量扫描（主权区）应在 30 秒内完成
- **NFR-2**: 准确性：误报率应低于 15%，通过占位符识别规则减少假阳性
- **NFR-3**: 幂等性：脱敏脚本可重复执行，已脱敏内容不会重复处理
- **NFR-4**: 可维护性：正则规则集中管理，便于新增敏感信息类型
- **NFR-5**: 合规性：脱敏处理符合《个人信息保护法》要求，不保留可还原的真实个人信息

## Constraints
- **Technical**: Python 3.10+，使用标准库（re、pathlib、argparse、json），不引入新的第三方依赖
- **Business**: vendor/ 子模块不得修改；external/playground 已忽略不处理；不修改历史 Git 记录
- **Dependencies**: 复用 `.agents/scripts/lib/` 中现有的工具函数（如文件遍历、报告生成）

## Assumptions
- 用户同意对发现的个人信息进行脱敏处理
- vendor 子模块中的敏感信息问题将通过上游反馈渠道处理，不在本次任务范围内
- 脱敏处理使用通用占位符不会影响文档的技术参考价值
- 示例代码中的 `your-api-key`、`example.com`、`localhost` 等占位符值不需要脱敏

## Acceptance Criteria

### AC-1: 敏感信息全面识别
- **Given**: 项目主权区完整代码库
- **When**: 运行敏感信息扫描脚本
- **Then**: 能够识别出所有已发现问题类型（个人路径、手机号、邮箱、会话标识符、.gitignore缺口），且输出结构化结果
- **Verification**: `programmatic`
- **Notes**: 对比初步扫描结果，覆盖率达到 100%

### AC-2: 个人文件路径脱敏
- **Given**: 文档中存在 `C:\Users\xinzo\` 形式的个人路径
- **When**: 执行自动脱敏修复
- **Then**: 所有个人用户名路径被替换为 `<USER_HOME>\` 或 `~` 等通用占位符，且文档上下文语义保持通顺
- **Verification**: `programmatic` + `human-judgment`

### AC-3: 真实手机号脱敏
- **Given**: 文档中存在引用的真实手机号
- **When**: 执行脱敏处理
- **Then**: 手机号中间四位替换为 `****`，保留号段和后四位供识别
- **Verification**: `programmatic`

### AC-4: .gitignore 规则完善
- **Given**: 当前 .gitignore 只排除部分 .env 文件
- **When**: 更新 .gitignore
- **Then**: 所有环境变量文件模式（.env、.env.*、!.env.example）均被正确排除，示例文件 .env.example 允许提交
- **Verification**: `programmatic`

### AC-5: 自动化检测脚本可用
- **Given**: 新建 check-sensitive-info.py 脚本
- **When**: 运行脚本并执行测试
- **Then**: 脚本支持 CLI 参数、输出格式正确、误报率可控、有单元测试覆盖
- **Verification**: `programmatic`

### AC-6: 脱敏检查报告完整
- **Given**: 扫描和处理完成
- **When**: 生成报告
- **Then**: 报告包含扫描统计、问题清单、处理方法、残留风险、预防建议，格式规范易读
- **Verification**: `human-judgment`

### AC-7: 系统功能不受影响
- **Given**: 脱敏处理完成
- **When**: 运行现有单元测试和脚本
- **Then**: 所有现有测试通过，代码可正常运行，文档链接不失效
- **Verification**: `programmatic`

### AC-8: vendor 区域不被修改
- **Given**: 执行脱敏处理
- **When**: 检查 git status
- **Then**: vendor/ 目录下无文件变更
- **Verification**: `programmatic`

## Open Questions
- [ ] 会话标识符/设备ID 类长字符串（如 `121377507783968:5e488b...`）是否属于需要脱敏的敏感信息？
- [ ] 复盘文档中的个人路径是否作为"操作记录"可保留，还是统一脱敏？
- [ ] 文章引用中的公开联系方式（如火山引擎 service@volcengine.com）是否需要脱敏？
