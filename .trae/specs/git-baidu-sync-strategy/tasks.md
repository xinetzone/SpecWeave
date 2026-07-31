---
id: "git-baidu-sync-strategy-tasks"
title: "基于git clone --no-local与百度网盘的私有Git跨设备同步策略 - 实施计划"
date: "2026-07-31"
---

# 基于git clone --no-local与百度网盘的私有Git跨设备同步策略 - The Implementation Plan

## [ ] Task 1: 百度网盘同步空间目录结构设计与规范文档
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 设计百度网盘同步空间根目录下的标准目录布局（repos/、locks/、backups/、logs/、meta/）
  - 定义每个目录的用途、命名约定、生命周期管理规则
  - 编写目录结构规范文档（含Mermaid结构图）
  - 提供一键初始化目录结构的脚本
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-1.1: 初始化脚本在Windows PowerShell上可成功创建所有目录
  - `programmatic` TR-1.2: 初始化脚本在Bash（macOS/Linux）上可成功创建所有目录
  - `human-judgement` TR-1.3: 目录结构文档中每个目录的职责清晰、无歧义，路径命名在三大OS上均合法
- **Notes**: 锁文件目录需考虑原子性创建（目录存在性检查+创建需原子化，避免竞态条件）

## [ ] Task 2: 跨平台Git配置规范文档
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 整理针对网盘同步场景的Git配置最佳实践
  - 明确core.autocrlf、core.filemode、core.symlinks、core.ignorecase、core.preloadindex等关键配置项在不同OS上的推荐值
  - 编写.gitattributes模板处理跨平台换行符和二进制文件
  - 提供git config设置命令脚本（区分Windows/macOS/Linux）
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `programmatic` TR-2.1: 按规范配置后，在Windows创建的文本文件同步到Linux执行git status不显示所有文件被修改
  - `programmatic` TR-2.2: 按规范配置后，可执行shell脚本从Windows同步到Linux权限处理符合预期（不自动设置+可手动chmod）
  - `human-judgement` TR-2.3: 配置文档说明每个配置项为什么这样设置，不只是给命令

## [ ] Task 3: 仓库初始化流程文档（首台设备 + 新设备加入）
- **Priority**: high
- **Depends On**: [Task 1, Task 2]
- **Description**: 
  - 编写首台设备初始化中央裸仓库的标准流程（在本地创建工作仓库 → git clone --no-local --bare到网盘目录 → 配置本地仓库remote）
  - 编写新设备首次加入时从网盘克隆的标准流程（克隆裸仓库到本地工作区）
  - 提供remote命名约定（推荐使用"baidu"或"sync"而不是"origin"，避免与GitHub等远程混淆）
  - 包含路径适配说明（各设备上网盘同步目录路径不同时如何配置）
- **Acceptance Criteria Addressed**: [AC-2, AC-3]
- **Test Requirements**:
  - `programmatic` TR-3.1: 在设备A按流程初始化后，网盘目录中裸仓库git config core.bare返回true
  - `programmatic` TR-3.2: 在设备B按流程克隆后，git remote -v正确指向网盘裸仓库路径
  - `programmatic` TR-3.3: 在设备B克隆后git log与设备A完全一致（同一commit hash at HEAD）
  - `human-judgement` TR-3.4: 流程文档每一步有检查点（执行完后应看到什么输出）

## [ ] Task 4: 基于锁文件的并发冲突预防机制实现
- **Priority**: high
- **Depends On**: [Task 1]
- **Description**: 
  - 设计锁文件格式（JSON/YAML，包含设备ID、进程ID、时间戳、操作类型）
  - 实现lock acquire算法（原子性检查+创建，考虑文件系统原子性）
  - 实现lock release逻辑（正常释放+异常退出时的超时释放机制，建议超时时间30分钟）
  - 实现死锁检测与强制解锁流程（需人工确认）
  - 封装为可调用的shell函数（bash）和PowerShell函数
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `programmatic` TR-4.1: 一个进程已获取锁时，另一个进程获取锁立即失败并返回明确错误码
  - `programmatic` TR-4.2: 锁文件超过超时时间后，新进程可获取锁（先清理过期锁）
  - `programmatic` TR-4.3: 锁释放后网盘同步空间中锁文件被删除
  - `human-judgement` TR-4.4: 错误提示明确告知用户哪个设备持有锁、何时获取的、如何处理

## [ ] Task 5: 日常Push-Pull同步流程封装脚本
- **Priority**: high
- **Depends On**: [Task 3, Task 4]
- **Description**: 
  - 封装git-sync-push脚本：预检查（锁文件、冲突副本、工作区干净）→ 获取锁 → 执行git push到网盘裸仓库 → 等待网盘同步完成（基于文件大小/修改时间稳定检测）→ 释放锁
  - 封装git-sync-pull脚本：预检查（锁文件检查、冲突副本检测、裸仓库健康快速检查）→ 获取锁（pull是否需要锁？设计为pull只读可不加锁，但需检测半同步状态）→ 执行git pull → 释放锁
  - 封装git-sync（一体化）脚本：先pull → 如有本地commit则push → 输出同步状态摘要
  - 实现网盘同步完成检测机制（循环检查裸仓库大小/最新文件修改时间，连续N秒无变化则认为同步完成）
  - 提供bash版本（macOS/Linux）和PowerShell版本（Windows）
- **Acceptance Criteria Addressed**: [AC-3, AC-4]
- **Test Requirements**:
  - `programmatic` TR-5.1: 设备A执行git-sync-push后，设备B执行git-sync-pull能获取新commit，两边HEAD一致
  - `programmatic` TR-5.2: 工作区有未提交更改时，push脚本报错退出不执行push
  - `programmatic` TR-5.3: 网盘目录存在冲突副本文件时，脚本检测到并停止执行
  - `human-judgement` TR-5.4: 同步完成后输出清晰的状态信息（新增commit数、同步耗时、是否有异常）
- **Notes**: 同步等待时间需可配置（默认轮询间隔2秒，稳定阈值10秒）

## [ ] Task 6: 百度网盘冲突副本检测与清理工具
- **Priority**: high
- **Depends On**: [Task 1]
- **Description**: 
  - 研究百度网盘冲突文件命名模式（不同客户端版本可能有不同格式：`(1)`, `(冲突版本)`, `(来自XXX)`等）
  - 编写扫描脚本检测网盘裸仓库目录下的所有冲突副本文件
  - 提供冲突文件列表报告（路径、文件大小、修改时间）
  - 提供安全清理建议（先报告、备份、再清理；不能盲目删除）
- **Acceptance Criteria Addressed**: [AC-7]
- **Test Requirements**:
  - `programmatic` TR-6.1: 在objects目录下创建名为`abc123 (1).tmp`的文件，扫描脚本能检测到
  - `programmatic` TR-6.2: 正常的Git对象文件不被误报为冲突副本
  - `human-judgement` TR-6.3: 清理建议明确说明哪些文件可以安全删除、哪些需要人工判断

## [ ] Task 7: 仓库健康检查与完整性校验脚本
- **Priority**: high
- **Depends On**: [Task 3]
- **Description**: 
  - 封装git fsck检查脚本（针对网盘裸仓库执行git fsck --full --strict）
  - 实现refs一致性快速检查（对比本地仓库HEAD和网盘裸仓库HEAD）
  - 实现半同步状态检测（检查是否有.tmp、.lock、.pack-tmp等临时文件存在）
  - 实现对象计数对比（本地对象数与裸仓库对象数对比，快速发现异常）
  - 输出健康检查报告（通过/警告/错误三级状态）
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `programmatic` TR-7.1: 健康的裸仓库执行检查返回"通过"状态，退出码0
  - `programmatic` TR-7.2: 手动删除一个对象文件后，检查返回"错误"状态，退出码非0
  - `programmatic` TR-7.3: 裸仓库中存在.tmp临时文件时，检查返回"警告"状态
  - `programmatic` TR-7.4: 本地HEAD领先于网盘HEAD时，提示"有未push的提交"

## [ ] Task 8: Git GC优化与性能配置指南
- **Priority**: medium
- **Depends On**: [Task 2]
- **Description**: 
  - 编写针对网盘同步场景的git gc策略（建议频率、gc参数优化、打包后对象数量对比）
  - 分析松散对象vs打包对象的同步效率差异（大量小文件对网盘同步的影响）
  - 提供.gitignore最佳实践（避免大文件、构建产物、依赖目录进入仓库）
  - 提供大文件处理建议方案（Git LFS替代方案：分离大文件存储、bundle分卷、或其他策略）
  - 给出百度网盘选择性同步配置建议（哪些目录不应同步）
- **Acceptance Criteria Addressed**: [NFR-2]
- **Test Requirements**:
  - `programmatic` TR-8.1: 执行gc后，松散对象数量显著减少（建议<100个）
  - `human-judgement` TR-8.2: 文档解释为什么gc对网盘同步重要（小文件数量减少→同步更快更可靠）
  - `human-judgement` TR-8.3: .gitignore模板覆盖常见的构建产物、依赖目录、日志文件

## [ ] Task 9: Bundle备份与损坏恢复流程
- **Priority**: medium
- **Depends On**: [Task 7]
- **Description**: 
  - 设计bundle快照备份策略（定期自动创建git bundle文件存放到backups/目录）
  - 编写自动备份脚本（可手动触发或配置定时任务）
  - 编写从bundle恢复仓库的完整流程
  - 编写从半损坏状态恢复的流程（哪些对象可恢复、哪些情况需使用备份）
  - 提供紧急恢复checklist
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `programmatic` TR-9.1: 备份脚本生成的bundle文件可通过git bundle verify验证通过
  - `programmatic` TR-9.2: 从bundle文件可成功克隆出完整仓库，git log与原仓库一致
  - `human-judgement` TR-9.3: 恢复流程每一步有验证命令，用户可确认恢复进度

## [ ] Task 10: 故障排查手册与常见问题FAQ
- **Priority**: high
- **Depends On**: [Task 5, Task 6, Task 7]
- **Description**: 
  - 分类整理常见故障场景：
    - 同步卡住（网盘客户端无响应、上传/下载队列阻塞）
    - Push被拒绝（锁被占用、非快进推送、工作区不干净）
    - Pull失败（裸仓库损坏、半同步状态、网络中断）
    - 冲突副本文件大量出现
    - 跨平台异常（文件名大小写、换行符、权限问题）
    - 仓库报错（对象损坏、refs不一致、dangling对象）
  - 每个场景提供：现象描述 → 可能原因 → 诊断步骤 → 解决方案 → 预防措施
  - 编写分步诊断流程图（Mermaid）
  - 提供一键诊断脚本（自动收集信息：git status、锁文件状态、冲突文件列表、fsck结果、网盘客户端状态提示）
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `human-judgement` TR-10.1: 覆盖至少10种常见问题场景
  - `human-judgement` TR-10.2: 每个问题的诊断步骤具体到执行什么命令、预期看到什么输出
  - `human-judgement` TR-10.3: 诊断脚本输出格式清晰，问题与建议一目了然
  - `human-judgement` TR-10.4: 文档包含紧急联系/求助建议（什么时候应认为问题超出自救范围）

## [ ] Task 11: 完整操作指南主文档与Quick Start
- **Priority**: medium
- **Depends On**: [Task 1, Task 2, Task 3, Task 5, Task 10]
- **Description**: 
  - 编写完整的操作指南主文档（README），整合所有子文档链接
  - 编写Quick Start快速上手章节（5步快速开始：配置网盘→初始化目录→首台设备→新设备加入→第一次同步）
  - 编写日常使用速查表（常用命令、正常/异常状态判断）
  - 编写操作原则（单写者原则、push后等待、定期备份等核心原则强调）
  - 提供文档索引与导航
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-8]
- **Test Requirements**:
  - `human-judgement` TR-11.1: 一个Git使用经验中等的用户按照Quick Start可在30分钟内完成首次配置
  - `human-judgement` TR-11.2: 主文档结构清晰，可快速跳转到需要的章节
  - `human-judgement` TR-11.3: 核心原则（单写者、等待同步、定期备份）在文档中醒目强调

## [ ] Task 12: 对抗审查（V阶段）与方案加固
- **Priority**: high
- **Depends On**: [Task 1, Task 2, Task 3, Task 4, Task 5, Task 6, Task 7, Task 10]
- **Description**: 
  - 执行对抗审查（V阶段），从四个视角攻击方案：
    - 魔鬼代言人：寻找方案中最薄弱的环节、最坏情况
    - 新用户视角：刚接触Git的用户可能在哪里犯错
    - 老板视角：这个方案可能导致什么数据灾难
    - 未来用户视角：半年后使用时会遇到什么维护问题
  - 根据审查结果修正方案缺陷
  - 将发现的问题转化为反模式和坑点警告
- **Acceptance Criteria Addressed**: [All ACs]
- **Test Requirements**:
  - `human-judgement` TR-12.1: 至少发现并记录8个潜在问题/边界情况
  - `human-judgement` TR-12.2: 每个发现的问题有对应的缓解措施或文档警告
  - `human-judgement` TR-12.3: 形成独立的"坑点与反模式"章节文档

## [ ] Task 13: 知识沉淀入库与Wiki归档
- **Priority**: medium
- **Depends On**: [Task 12]
- **Description**: 
  - 将完整策略沉淀为可复用模式（SDCP类似的方法论沉淀）
  - 归档到.git-advanced-wiki或新建专门的wiki目录
  - 更新知识库索引
  - 修复所有文档间的交叉引用
- **Acceptance Criteria Addressed**: [G3质量门]
- **Test Requirements**:
  - `programmatic` TR-13.1: 所有文档内的相对链接有效（无断链）
  - `human-judgement` TR-13.2: 模式文档包含触发条件、核心步骤、反模式、迁移验证
  - `human-judgement` TR-13.3: 可迁移到其他云同步盘（OneDrive、Dropbox、坚果云等）使用
