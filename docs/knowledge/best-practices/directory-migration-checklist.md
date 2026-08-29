---
id: directory-migration-checklist
title: 目录迁移五步法检查清单
x-toml-ref: .meta/toml/.agents/docs/knowledge/best-practices/directory-migration-checklist.toml
category: best-practices
tags:
  - migration
  - directory-restructure
  - checklist
  - five-step-method
  - atomic-commit
date: 2026-07-18
status: active
version: 1.0.0
author: SpecWeave Team
---

# 目录迁移五步法检查清单

## 概述

基于**五步法**（常量先行→元数据迁移→引用批量修复→ID同步→分层验证）的标准化迁移流程。

---

## 一、迁移前预检（四层依赖扫描）

### 1.1 第一层：脚本路径扫描

| 检查项 | 预期结果 | 状态 |
|--------|----------|------|
| Python脚本硬编码路径 | 0处硬编码 | [ ] |
| PowerShell/Shell脚本路径 | 0处硬编码 | [ ] |
| constants.py常量定义 | 所有路径使用常量 | [ ] |
| 导入语句路径依赖 | 0处直接导入旧路径 | [ ] |

### 1.2 第二层：TOML元数据扫描

| 检查项 | 预期结果 | 状态 |
|--------|----------|------|
| TOML mirror文件存在性 | mirror文件存在 | [ ] |
| frontmatter x-toml-ref字段 | 引用正确 | [ ] |
| TOML中路径字段 | 0处旧路径 | [ ] |
| TOML ID映射完整性 | 一一对应 | [ ] |

### 1.3 第三层：Markdown引用扫描

| 检查项 | 预期结果 | 状态 |
|--------|----------|------|
| 内部wikilink引用 | 0处旧链接 | [ ] |
| 相对路径引用 | 0处旧链接 | [ ] |
| x-toml-ref交叉引用 | 指向新路径 | [ ] |
| README导航链接 | 链接更新 | [ ] |

### 1.4 第四层：测试路径扫描

| 检查项 | 预期结果 | 状态 |
|--------|----------|------|
| 测试文件fixture路径 | 路径使用常量 | [ ] |
| conftest.py配置 | 路径正确 | [ ] |
| CI脚本路径引用 | 路径正确 | [ ] |
| 预提交钩子路径 | 路径正确 | [ ] |

### 预检确认

- [ ] 四层扫描全部通过
- [ ] 创建备份分支
- [ ] 记录当前提交哈希
- [ ] dry-run测试通过
- [ ] 团队通知到位

---

## 二、五步法详细执行步骤
### Step 1: 常量先行

**目标**：更新路径常量，不移动文件

| 检查项 | 验证标准 | 状态 |
|--------|----------|------|
| 更新constants.py | 新路径常量定义正确 | [ ] |
| 更新配置文件 | spec-loader.toml等路径更新 | [ ] |
| 运行相关测试 | 测试通过 | [ ] |
| 原子提交S1 | refactor(path): step1 - update constants | [ ] |

### Step 2: 元数据迁移

**目标**：移动TOML mirror文件

| 检查项 | 验证标准 | 状态 |
|--------|----------|------|
| 创建新目录结构 | 目录存在 | [ ] |
| 移动TOML mirror文件 | mirror文件移动完成 | [ ] |
| 更新TOML内部路径字段 | 所有TOML路径更新 | [ ] |
| 验证TOML语法 | 无语法错误 | [ ] |
| 原子提交S2 | refactor(metadata): step2 - migrate TOML | [ ] |

### Step 3: 引用批量修复

**目标**：修复所有交叉引用和链接

| 检查项 | 验证标准 | 状态 |
|--------|----------|------|
| 修复wikilink引用 | [[OLD]] → [[NEW]] | [ ] |
| 修复Markdown链接 | 所有链接指向新位置 | [ ] |
| 修复x-toml-ref字段 | 指向新TOML路径 | [ ] |
| 运行链接检查 | 0个断链 | [ ] |
| 原子提交S3 | fix(xref): step3 - fix cross-references | [ ] |

### Step 4: ID同步

**目标**：移动实际文件，同步ID

| 检查项 | 验证标准 | 状态 |
|--------|----------|------|
| 移动实际文件 | 文件物理移动完成 | [ ] |
| 验证frontmatter ID一致性 | ID规范符合要求 | [ ] |
| 同步TOML主键 | 主键与文件ID一致 | [ ] |
| 删除旧空目录 | 旧目录清理 | [ ] |
| 原子提交S4 | refactor(files): step4 - move files and sync IDs | [ ] |

### Step 5: 分层验证

**目标**：六层验证

| 检查项 | 验证标准 | 状态 |
|--------|----------|------|
| L0: 文件系统验证 | 文件存在、权限正确 | [ ] |
| L1: 语法验证 | 无语法错误 | [ ] |
| L2: 引用验证 | 0断链 | [ ] |
| L3: 功能测试 | 全部测试通过 | [ ] |
| L4: CI全量检查 | 8项检查全过 | [ ] |
| L5: 文档生成验证 | 导航生成正确 | [ ] |
| 原子提交S5 | test(verify): step5 - verification passed | [ ] |

---

## 三、原子提交策略表

| 阶段 | 提交类型 | Commit Message规范 | 回滚命令 |
|------|----------|-------------------|----------|
| S1 常量先行 | refactor | `refactor(path): step1 - update path constants for {OLD}->{NEW}` | `git revert HEAD` |
| S2 元数据迁移 | refactor | `refactor(metadata): step2 - migrate TOML mirror` | `git revert HEAD` |
| S3 引用修复 | fix | `fix(xref): step3 - batch fix {N} cross-references` | `git revert HEAD` |
| S4 文件移动 | refactor | `refactor(files): step4 - move {N} files` | `git revert HEAD` |
| S5 验证通过 | test | `test(verify): step5 - layered verification passed` | `git reset --hard HEAD~1` |

---

## 四、6个常见陷阱（Gotchas）

### Gotcha 1: 先移动文件，后改常量

- **症状**：import路径全部断裂
- **根因**：违反常量先行原则
- **规避**：Step1只改常量不动文件

### Gotcha 2: TOML mirror与文件不同步

- **症状**：spec-loader加载失败
- **根因**：只移动.md忘记.meta/toml
- **规避**：Step2专门处理元数据

### Gotcha 3: 大小写不敏感文件系统陷阱

- **症状**：Windows过Linux失败
- **根因**：NTFS大小写不敏感
- **规避**：用git mv -f，跨平台验证

### Gotcha 4: 自动生成区域被手动修改

- **症状**：docgen后手动修改被覆盖
- **根因**：修改了NAV_START区域
- **规避**：不要编辑自动生成区域

### Gotcha 5: 硬编码藏在注释/字符串中

- **症状**：grep没发现但运行时出现
- **根因**：路径硬编码在日志/错误消息
- **规避**：四层扫描含字符串注释

### Gotcha 6: 测试fixture用相对路径

- **症状**：不同目录运行pytest失败
- **根因**：依赖cwd的相对路径
- **规避**：用__file__或constants.py

---

## 五、验收标准

### 5.1 静态检查
- [ ] 零旧路径残留：全仓库grep旧路径返回0结果
- [ ] 零断链：check-links.py 0 broken link
- [ ] frontmatter合规：check-frontmatter.py通过
- [ ] TOML完整性：所有TOML可正常解析

### 5.2 测试验证
- [ ] 单元测试全过：pytest 100%通过
- [ ] CI质量门禁：ci-check.ps1 8项全过
- [ ] 文档可生成：generate-nav.py正常运行

### 5.3 功能验证
- [ ] spec-loader正常：warmup无错误
- [ ] 命令行工具可用：CLI脚本可正常调用
- [ ] Git状态干净：工作区无未预期变更

### 5.4 回滚验证
- [ ] 回滚预案就绪：记录5个原子提交哈希
- [ ] 备份分支存在：backup/pre-migration已推送
- [ ] 回滚命令验证：可顺序revert 5个提交

---

**变更记录**：

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| 1.0.0 | 2026-07-18 | 初始版本 | SpecWeave Team |