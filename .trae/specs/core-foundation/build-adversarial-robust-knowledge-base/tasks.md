# 对抗式健壮知识库系统 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 核心工具库基础架构搭建
- **Priority**: high
- **Depends On**: None
- **Status**: completed
- **Description**: 
  - 在`.agents/scripts/lib/`下创建知识库安全模块`knowledge_security.py`
  - 实现基础工具函数：文件读写、YAML frontmatter解析、路径验证
  - 实现输入验证与sanitize框架
  - 遵循现有共享库规范，参考`.agents/scripts/lib/README.md`
- **Acceptance Criteria Addressed**: [AC-5, AC-9]
- **Test Requirements**:
  - `programmatic` TR-1.1: 路径遍历攻击测试——尝试访问`docs/knowledge/`外的文件被正确拒绝 ✅
  - `programmatic` TR-1.2: 特殊字符/超长输入测试——不崩溃、返回正确错误 ✅
  - `programmatic` TR-1.3: 旧格式frontmatter解析测试——无security_level/integrity字段的文件能正常解析 ✅
  - `human-judgement` TR-1.4: 代码风格与现有lib一致，无重复实现已有功能 ✅
- **实现说明**: 同时增强了frontmatter.py，新增split_frontmatter_and_content()函数和parse_frontmatter_unified的content可选参数，避免重复IO读取。

## [x] Task 2: 分级加密存储实现（核心模块）
- **Priority**: high
- **Depends On**: [Task 1]
- **Status**: core-completed（加密模块已完成，CLI接口待Task 9命令集封装时统一提供）
- **Description**: 
  - 实现AES-256-GCM加密/解密函数
  - 实现密钥管理：支持环境变量`KNOWLEDGE_ENCRYPTION_KEY`或本地密钥文件
  - 实现frontmatter的security_level字段处理逻辑
  - 实现三个安全级别的存储策略：
    - public: 明文存储，与现有格式100%兼容
    - internal: 元数据字段加密，正文明文
    - confidential: 全文加密
  - 提供命令行接口：encrypt/decrypt/migrate（CLI部分待Task 9完成）
- **Acceptance Criteria Addressed**: [AC-2, AC-9]
- **Test Requirements**:
  - `programmatic` TR-2.1: public条目加密前后完全一致（兼容Git diff） ✅
  - `programmatic` TR-2.2: internal条目无密钥时无法读取加密元数据，正文明文可读 ✅
  - `programmatic` TR-2.3: confidential条目无密钥时无法读取任何内容，有密钥时正确解密 ✅
  - `programmatic` TR-2.4: 加密→解密往返测试，内容无损 ✅
  - `programmatic` TR-2.5: 旧条目默认作为public处理，无异常 ✅
- **实现说明**: 创建了knowledge_crypto.py模块，使用cryptography库（环境中已可用），PBKDF2-HMAC-SHA256密钥派生（600,000次迭代），支持字段级和全文级两种加密模式，confidential级别使用---ENC---文件头标记。

## [x] Task 3: 完整性自校验与自动修复实现
- **Priority**: high
- **Depends On**: [Task 1]
- **Status**: completed
- **Description**: 
  - 实现SHA-256校验和计算与验证
  - integrity字段嵌入frontmatter，不单独存储
  - 读取时自动校验完整性，校验失败触发修复流程
  - 实现Git集成的自动修复：从最近Git版本恢复损坏文件
  - 实现部分损坏的优雅降级：尽可能提取可读内容
  - 提供命令行接口：verify/repair（CLI部分待Task 9）
- **Acceptance Criteria Addressed**: [AC-3, AC-6]
- **Test Requirements**:
  - `programmatic` TR-3.1: 正常文件校验通过 ✅
  - `programmatic` TR-3.2: 手动篡改文件内容后，校验检测出损坏 ✅
  - `programmatic` TR-3.3: 损坏文件有Git历史版本时，自动从Git恢复 ✅
  - `programmatic` TR-3.4: 部分截断的文件能提取部分内容并标记损坏 ✅
  - `programmatic` TR-3.5: integrity字段自动生成，不破坏现有格式 ✅
- **实现说明**: 创建了knowledge_integrity.py模块（SHA-256校验和计算/验证/Git恢复/优雅降级），集成到knowledge_security.py读写流程。写入时自动计算integrity校验和，读取时自动校验，损坏时自动触发Git修复→优雅降级流程。修复了split_frontmatter_and_content返回content带前导\n导致校验和偏差的问题，在read_knowledge_entry中统一strip前导换行符。冒烟测试40/40全部通过。

## [x] Task 4: 第一性原理知识分类体系增强
- **Priority**: medium
- **Depends On**: [Task 1]
- **Status**: completed
- **Description**: 
  - 从第一性原理出发定义知识本质类型标签：factual（事实性）、procedural（程序性）、conditional（条件性）、metacognitive（元认知）
  - 扩展YAML frontmatter，增加knowledge_type、validation_status、reuse_count字段
  - 更新知识条目模板
  - 增强索引生成脚本，支持按知识本质维度检索
  - 保留原有分类目录，实现多维标签体系
- **Acceptance Criteria Addressed**: [AC-1, AC-7]
- **Test Requirements**:
  - `human-judgement` TR-4.1: 分类体系从知识本质出发（而非类比现有目录），逻辑自洽 ✅
  - `programmatic` TR-4.2: 新旧标签体系共存，索引生成正常 ✅
  - `programmatic` TR-4.3: 按knowledge_type检索返回正确结果 ✅
  - `human-judgement` TR-4.4: 现有知识条目无需强制迁移，可逐步补全新标签 ✅
- **实现说明**: 创建了`knowledge_classification.py`模块定义四类知识本质类型（factual/procedural/conditional/metacognitive），支持启发式自动推断、多维组合筛选和分类统计；扩展`_apply_default_metadata`补全新增字段；创建知识条目模板和增强索引生成脚本`generate-knowledge-index.py`支持多维筛选。所有冒烟测试通过，保持向后兼容。

## [x] Task 5: 异常输入防御与边界检查
- **Priority**: high
- **Depends On**: [Task 1, Task 2, Task 3]
- **Status**: completed
- **Description**: 
  - 实现文件大小限制（单条目默认<5MB）
  - 实现所有入口点的输入验证：frontmatter格式、标签格式、路径格式
  - 实现资源消耗防护：防止OOM、死循环
  - 实现错误处理框架：所有异常都有清晰错误信息，不裸露栈追踪给用户
  - 模糊测试基础框架：生成随机畸形输入测试鲁棒性
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `programmatic` TR-5.1: 10MB超大文件被拒绝，不OOM ✅
  - `programmatic` TR-5.2: 畸形YAML frontmatter不导致崩溃，返回解析错误 ✅
  - `programmatic` TR-5.3: 路径遍历尝试（如`../../etc/passwd`）被正确拦截 ✅
  - `programmatic` TR-5.4: 空文件、全特殊字符文件不导致崩溃 ✅
  - `programmatic` TR-5.5: 嵌套引用/循环引用不导致死循环 ✅
- **实现说明**: 创建了`knowledge_defense.py`防御模块（统一错误框架KnowledgeError+InputValidator+ResourceGuard+defensive_read+validate_all_entry_points），创建了`knowledge_fuzzer.py`模糊测试框架（32个场景覆盖字符串/文件名/标签/元数据/frontmatter/边界/资源/路径），集成到`knowledge_security.py`的read/write入口点。32/32模糊测试+10/10集成测试全部通过。

## [x] Task 6: Git集成与冗余备份
- **Priority**: medium
- **Depends On**: [Task 1, Task 3]
- **Status**: completed
- **Description**: 
  - 实现Git状态检查：变更前自动校验完整性
  - 实现本地冗余备份：支持备份到指定目录
  - 实现"知识时光机"：查询任意Git版本的知识状态
  - 实现大规模损坏检测与批量恢复
  - 提供命令行接口：backup/restore/history
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `programmatic` TR-6.1: 备份命令创建完整副本，可用于恢复 ✅
  - `programmatic` TR-6.2: 能正确列出Git历史中的版本 ✅
  - `programmatic` TR-6.3: 指定版本能正确检出 ✅
  - `programmatic` TR-6.4: 批量损坏时，自动检测并从Git恢复 ✅
- **实现说明**: 创建了`knowledge_backup.py`模块（备份/恢复/时光机/批量检测修复/变更前检查），创建了`backup-knowledge.py` CLI工具（9个子命令：backup/restore/list/history/show/diff/detect/repair/precheck），创建了`test_task6_smoke.py`冒烟测试。12/12冒烟测试通过，585条目完整性检测全部通过。

## [ ] Task 7: 检索增强与查询验证
- **Priority**: medium
- **Depends On**: [Task 1, Task 3, Task 4]
- **Description**: 
  - 增强索引生成：包含knowledge_type、security_level、validation_status索引
  - 实现检索结果完整性过滤：自动排除损坏条目
  - 实现按多维标签组合查询
  - 实现查询输入验证与注入防护
  - 返回结果包含完整性状态标记
- **Acceptance Criteria Addressed**: [AC-7]
- **Test Requirements**:
  - `programmatic` TR-7.1: 检索结果只包含校验通过的条目
  - `programmatic` TR-7.2: 按knowledge_type+security_level组合查询返回正确结果
  - `programmatic` TR-7.3: 恶意查询注入（如特殊字符、路径遍历）被正确处理
  - `programmatic` TR-7.4: 索引生成在1000条目内<30秒完成

## [ ] Task 8: 多Agent对抗式审查工作流
- **Priority**: high
- **Depends On**: [Task 1, Task 2, Task 3, Task 5]
- **Description**: 
  - 设计对抗式审查Prompt模板（基于卡兹克方法论）
  - 实现审查用例生成框架：构造异常输入、边界条件、攻击场景
  - 实现多Agent并发审查调度
  - 实现审查结果收集与结构化报告生成
  - 审查报告存入`docs/retrospective/`体系
  - 提供命令行接口：`/knowledge review`触发审查
  - 定义审查场景清单：
    - 超大/畸形文件
    - 加密边界（错误密钥、篡改密文）
    - 完整性校验绕过尝试
    - 检索注入
    - 路径遍历
    - Git历史重写攻击
    - 元数据污染
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `programmatic` TR-8.1: 审查框架能构造至少10种不同攻击场景
  - `programmatic` TR-8.2: 每个攻击场景执行后不导致系统永久损坏
  - `human-judgement` TR-8.3: 审查报告包含复现步骤、风险等级、修复建议
  - `human-judgement` TR-8.4: 审查Prompt体现第一性原理+对抗式审查闭环思想
  - `programmatic` TR-8.5: 审查发现的漏洞能被准确定位到文件/函数

## [ ] Task 9: Agent体系集成与命令集封装
- **Priority**: medium
- **Depends On**: [Task 2, Task 3, Task 6, Task 8]
- **Description**: 
  - 更新AGENTS.md增加对抗式健壮知识库引用
  - 更新各角色定义：Reviewer增加审查职责、Architect增加第一性原理分类职责
  - 在`.agents/commands/`下封装knowledge命令集：
    - `/knowledge verify`: 校验完整性
    - `/knowledge encrypt`: 加密指定条目
    - `/knowledge review`: 触发对抗式审查
    - `/knowledge backup`: 创建冗余备份
    - `/knowledge migrate`: 迁移旧条目到新格式
  - 提供标准CLI入口，符合项目命令集规范
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `human-judgement` TR-9.1: AGENTS.md中引用清晰，角色职责更新正确
  - `programmatic` TR-9.2: 所有命令能正常调用，参数解析正确
  - `human-judgement` TR-9.3: 命令帮助信息清晰易懂
  - `human-judgement` TR-9.4: 与现有.agents体系无冲突

## [ ] Task 10: 迁移脚本与向后兼容验证
- **Priority**: high
- **Depends On**: [Task 1, Task 2, Task 3, Task 4]
- **Description**: 
  - 编写旧条目迁移脚本：批量补全security_level=public、计算integrity
  - 提供dry-run模式，预览迁移变更
  - 全量向后兼容测试：使用现有知识库所有条目验证
  - 编写迁移指南文档
- **Acceptance Criteria Addressed**: [AC-9]
- **Test Requirements**:
  - `programmatic` TR-10.1: 迁移dry-run不修改任何文件
  - `programmatic` TR-10.2: 迁移后所有现有条目能正常读取
  - `programmatic` TR-10.3: 迁移后索引生成正常
  - `human-judgement` TR-10.4: 迁移过程可逆（有Git回滚能力）

## [ ] Task 11: 测试套件与自验证
- **Priority**: high
- **Depends On**: [Task 1-10]
- **Description**: 
  - 为所有核心模块编写单元测试，覆盖率不低于80%
  - 编写集成测试：端到端流程验证
  - 编写对抗式测试用例：从攻击者视角验证防御有效性
  - 测试脚本放入`.agents/scripts/tests/`目录
  - 确保所有测试通过
- **Acceptance Criteria Addressed**: [AC-2, AC-3, AC-5, AC-6, AC-7, AC-9]
- **Test Requirements**:
  - `programmatic` TR-11.1: 单元测试覆盖率≥80%
  - `programmatic` TR-11.2: 所有单元测试通过
  - `programmatic` TR-11.3: 集成测试覆盖完整CRUD+加密+校验流程
  - `programmatic` TR-11.4: 对抗测试用例验证所有防御机制有效

## [ ] Task 12: 文档更新与主题README登记
- **Priority**: medium
- **Depends On**: [Task 11]
- **Description**: 
  - 更新`docs/knowledge/README.md`，增加安全功能说明
  - 更新core-foundation主题README，登记本spec
  - 编写使用指南：如何使用加密、校验、审查、备份功能
  - 更新AGENTS.md中知识库相关引用
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `human-judgement` TR-12.1: 文档清晰完整，人类读者能理解如何使用
  - `human-judgement` TR-12.2: 主题README正确登记本spec状态
  - `programmatic` TR-12.3: 所有内部链接有效（可通过link-check验证）
