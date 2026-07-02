---
id: "templates-theme-templates-migration-archival-task-template"
title: "Tasks"
source: "AGENTS.md#模板"
x-toml-ref: "../../../.meta/toml/.agents/templates/theme-templates/migration-archival-task-template.toml"
---
# Tasks

> 主题：migration-archival（迁移与归档）
> 适用场景：外部内容引入、沙箱治理、项目迁移、归档清理、备份恢复

- [ ] Task 0: 迁移前调研与准备
  - [ ] SubTask 0.1: 盘点源目录/源项目的完整文件清单（含文件数、大小、类型统计）
  - [ ] SubTask 0.2: 对源目录进行内容分类：有价值内容（迁移）、归档内容（留存）、临时内容（删除）
  - [ ] SubTask 0.3: 安全审查：检查是否包含敏感信息（密钥、API Token、凭证、个人数据、内部地址等）
  - [ ] SubTask 0.4: 创建完整备份（迁移前必须可回滚，备份存放在独立位置）
  - [ ] SubTask 0.5: 识别所有受影响的引用路径（grep 搜索源文件被引用的位置）
  - [ ] SubTask 0.6: 确定目标目录位置和结构（参照项目现有目录组织方式）
  - [ ] SubTask 0.7: 制定详细迁移计划（顺序、批次划分、每步验证点、回滚方案）
  - [ ] SubTask 0.8: 确认遵循临时依赖管理协议（.agents/protocols/dependency-management.md）

- [ ] Task 1: 内容萃取与预处理
  - [ ] SubTask 1.1: 从源内容中萃取有价值的部分（去除 node_modules/、.venv/、__pycache__/、.temp/ 等噪声目录）
  - [ ] SubTask 1.2: 处理敏感信息（脱敏、移除密钥、替换内部地址等）
  - [ ] SubTask 1.3: 按目标主题/目录组织萃取后的内容
  - [ ] SubTask 1.4: 对归档内容添加元数据标记（来源项目/目录、归档日期、归档原因、内容摘要）
  - [ ] SubTask 1.5: 统一文件命名为 kebab-case（源文件命名不规范时进行重命名）
  - [ ] SubTask 1.6: 处理编码问题（如从其他系统迁移时的编码转换）

- [ ] Task 2: 执行迁移
  - [ ] SubTask 2.1: 按计划逐批次移动/复制文件到目标位置
  - [ ] SubTask 2.2: 每批次迁移后立即更新相关引用路径
  - [ ] SubTask 2.3: 每批次迁移后验证内容完整性（文件数核对、大小校验、抽检文件内容）
  - [ ] SubTask 2.4: 跨平台路径兼容性处理（从 Linux/macOS 迁移到 Windows 时注意路径分隔符）
  - [ ] SubTask 2.5: 处理文件名冲突（如目标位置已存在同名文件，制定合并或重命名策略）
  - [ ] SubTask 2.6: 大文件或二进制文件特殊处理（确认是否需要 LFS 或排除）

- [ ] Task 3: 迁移后验证与收尾
  - [ ] SubTask 3.1: 运行 check-links.py 验证无死链
  - [ ] SubTask 3.2: 运行 check-move.py 验证迁移完整性
  - [ ] SubTask 3.3: 文件数量核对（源文件数 = 迁移文件数 + 归档文件数 + 删除文件数）
  - [ ] SubTask 3.4: 更新目标目录的 README/索引文件，登记迁移来源
  - [ ] SubTask 3.5: 验证源目录中确定删除的内容已清理（确认不提交到 Git）
  - [ ] SubTask 3.6: 更新 .gitignore（如迁移内容包含需要忽略的文件类型）
  - [ ] SubTask 3.7: 确认备份保留策略（备份保留多久、何时清理备份）
  - [ ] SubTask 3.8: 在对应主题 README.md 的执行看板中登记完成状态

# Task Dependencies

- Task 0 必须最先且最谨慎地执行（迁移操作不可逆风险高，备份和安全审查是底线）
- Task 1 依赖 Task 0 完成（萃取和预处理在备份后进行）
- Task 2 依赖 Task 1 完成，且必须按批次执行、每批验证
- Task 3 依赖 Task 2 全部完成后进行最终验证
- **重要红线**：
- 1. 未备份不迁移
- 2. 安全审查未通过不迁移
- 3. 临时依赖（vendor/、node_modules/、.temp/ 等）绝不提交到 Git
- 4. 迁移过程中发现问题立即停止，回滚到备份状态后重新规划
