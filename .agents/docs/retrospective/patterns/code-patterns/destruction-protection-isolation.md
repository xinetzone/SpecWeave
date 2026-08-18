---
id: "destruction-protection-isolation"
title: "清理-保护域隔离原则"
type: "code-pattern"
date: 2026-08-15
maturity: "L2-validated"
maturity_note: "≥2个案例跨场景验证：cleanup.sh备份自毁(bug修复)+wsl-docker-storage快照正例对比+跨领域Docker prune类比"
source:
  - "session: conda-llvm-docker-build-cleanup-fix"
  - "pattern: shell-cleanup-non-blocking.md"
  - "pattern: wsl-docker-storage-cleanup-five-step-method.md"
related_patterns:
  - "shell-cleanup-non-blocking.md"
  - "wsl-docker-storage-cleanup-five-step-method.md"
  - "wsl-docker-command-safety.md"
tags: ["shell", "bash", "cleanup", "rm", "backup", "isolation", "scope", "invariant", "filesystem", "docker", "defensive-programming"]
validation_count: 2
reuse_count: 0
---

# 清理-保护域隔离原则

## 触发场景

- Shell 脚本中需要执行批量删除操作（`rm -rf`、`find -delete`、`prune`等）
- 删除前需要保留/备份部分数据（计时器、快照、配置文件、活跃资源）
- 使用通配符删除（`*`、`.*`）或递归删除（`-rf`）时，作用域覆盖整个目录树
- 备份/临时保存位置与删除目标在同一目录树内
- 存在"移开→清理→恢复"（move-aside → cleanup → restore）模式

**识别信号**：
- 备份路径变量与删除目标路径有共同父目录前缀
- 删除命令使用 `*` 或 `.*` 通配符覆盖整个目录
- 代码注释中出现"排除"(exclude/preserve)关键词但路径验证缺失
- "mv aside" 后紧跟 `rm -rf` 同一父目录

## 反目标用户与边界场景（不适用场景）

本模式并非银弹，以下场景不需要或不适用本模式：

| 场景类型 | 具体描述 | 为什么不适用 | 推荐做法 |
|---------|---------|-------------|---------|
| **1. 空目录/全新目录清理** | 删除目标是刚创建的空目录、或明确无任何需要保留的内容 | T∩D=∅问题根本不存在——保护集P是空集 | 直接 `rm -rf` 即可，无需额外防护 |
| **2. 文件描述符(FD)持有备份** | 已通过 `exec 3<>file` 打开文件持有FD，然后unlink路径 | Linux下已打开文件即使unlink，FD仍可读写直到close，数据不会丢失 | 不需要文件系统级备份，直接清理路径即可 |
| **3. 数据库事务级备份** | PostgreSQL/MySQL等支持事务的数据库，通过BEGIN/COMMIT保护 | 数据库有WAL/redo log，回滚机制不同于文件系统备份，本模式的文件系统隔离假设不成立 | 使用数据库原生事务/备份工具（pg_dump、mysqldump等） |
| **4. 内存文件系统(tmpfs)** | `/dev/shm`、`/run`等tmpfs挂载点，重启自动清空 | tmpfs是临时存储，本身就是"删除域"，备份到同一tmpfs无意义 | 重要数据不要放在tmpfs，或备份到持久化存储 |
| **5. 单次原子rename替换** | 用 `mv newfile oldfile` 原子覆盖单个文件（非目录） | rename是原子操作，不存在"先删备份再恢复"的时间窗口，不会出现备份自毁 | 直接rename即可，本模式针对的是批量递归删除场景 |
| **6. 只读目录清理** | 清理的目录是只读挂载或无写入权限 | 备份无法创建，mv操作会失败，问题在更早阶段暴露 | 先检查权限，处理完权限问题再考虑隔离；只读目录本身也不会误删备份 |

## 早期预警信号（5+个）

以下信号出现时，T∩D=∅违反风险极高，应立即应用本模式检查：

| 预警信号 | 危险等级 | 说明 |
|---------|---------|------|
| 备份路径变量包含删除目标路径前缀（如backup="/tmp/..."，删除目标含/tmp） | 🔴 高危 | 最直接的T⊂D信号，几乎必然触发自毁 |
| 使用 `*` 和 `.*` 双重通配符覆盖目录（如 `rm -rf /dir/* /dir/.*`） | 🔴 高危 | `.`开头的隐藏文件/备份不会被`*`匹配，但会被`.*`匹配 |
| "mv aside"和"rm -rf"在同一函数内，操作同一父目录 | 🟠 中危 | 时序上备份→删除→恢复在同一代码块，容易遗漏位置检查 |
| mktemp使用默认目录（未显式-p指定），后续清理$TMPDIR或/tmp | 🟠 中危 | mktemp默认在$TMPDIR（通常是/tmp），后续清理会销毁临时文件 |
| docker system prune/docker volume prune不加任何filter | 🟡 低危 | 删除域是"所有未使用资源"，其他项目的停止容器/卷属于P⊂D |
| 代码注释出现"排除/exclude/preserve"但无对应路径验证代码 | 🟡 低危 | 开发者意识到要保护数据，但只停留在注释层面，无实际断言 |
| bind mount/symlink路径传递给清理函数 | 🟠 中危 | 符号链接可能使T和D表面路径不同但实际指向同一inode |

## 失败案例

### 案例1：cleanup.sh计时器备份自毁（本项目源案例）

#### 事故经过

**时间**：2026-08-15，构建conda-llvm变体镜像时
**场景**：`cleanup_tmp()` 函数在Docker构建Stage 4执行激进清理，减少镜像体积

**原始代码（有bug）**：
```bash
cleanup_tmp() {
    # 计时器目录需要保留（Stage 5需要用计时数据生成报告）
    local tmp_timer_backup="/tmp/.variant-timers-backup-$$"  # ⚠️ T在D内！
    mv "${_VARIANT_TIMER_DIR}" "${tmp_timer_backup}"

    rm -rf /tmp/* /tmp/.* /var/tmp/* /var/tmp/.* 2>/dev/null || true  # 💥 双通配符删除所有内容

    mkdir -p "$(dirname "${_VARIANT_TIMER_DIR}")"
    mv "${tmp_timer_backup}" "${_VARIANT_TIMER_DIR}" 2>/dev/null || true  # 备份已删，mv失败
}
```

**事故时间线**：
```
t0: 计时器目录 /root/.variant-timers/ 存在（P集合）
t1: mv 到 /tmp/.variant-timers-backup-12345（T集合，在/tmp内）
t2: rm -rf /tmp/* /tmp/.* 执行
    - /tmp/* 不匹配.开头文件 → 备份暂时幸存
    - /tmp/.* 匹配所有.开头文件 → 💥 备份被删除！
t3: mv /tmp/.variant-timers-backup-12345 → 路径不存在
    - mv失败（但有||true，不报错）
t4: /root/.variant-timers/ 永久丢失
t5: Stage 5 [VALIDATION CHECKPOINT] 找不到计时数据，构建失败
```

**影响**：
- 构建失败率：3次连续构建均失败（看似"随机失败"，实际必现）
- 排查耗时：~20分钟，由于有`2>/dev/null || true`抑制错误，无明显错误日志
- 根因隐蔽性：双重陷阱——`*`不匹配隐藏文件的常识+`|| true`静默失败

**修复方案**：
1. 备份路径改为 `/root/.variant-timers-backup-$$`（T在/root，与/tmp隔离）
2. 后续进一步重构为safe_cleanup_dir()白名单方案（原则3），完全不需要mv-aside

### 成功偏误警示

此bug在测试阶段未被发现的原因：
- 单元测试使用空/tmp目录，没有计时器备份
- 手动测试时备份文件名用可见字符（如`tmp-backup`），不被`.*`匹配（被`*`匹配但此时备份已移出）
- 只有完整构建流程、且备份以`.`开头隐藏时才触发——属于"路径依赖+时序依赖"双重耦合

## 问题背景

### 核心不变量：T ∩ D = ∅

任何"移开→清理→恢复"模式都涉及三个集合：

| 符号 | 含义 | 示例 |
|------|------|------|
| **D**（Destruction scope） | 删除操作的作用域——所有将被删除的路径集合 | `/tmp/*` + `/tmp/.*` → 整个/tmp目录树 |
| **P**（Preservation set） | 必须存活的保护数据集合 | `/root/.variant-timers/`（计时器状态） |
| **T**（Temporary location） | P被临时移至的备份位置 | `/tmp/.variant-timers-backup-$$`（错误）/ `/root/.variant-timers-backup-$$`（正确） |

**安全不变量**：备份位置 T 必须在删除作用域 D **之外**，即 T ∩ D = ∅。

### 触发条件与隐蔽性

此 bug 具有高度隐蔽性，三个条件同时存在才触发：

1. **隐式假设**：开发者假设"`.`"开头的隐藏文件不会被 `*` 匹配
2. **通配符覆盖**：但代码使用 `/tmp/* /tmp/.*` 双重通配符，`.`开头文件也被覆盖
3. **时序依赖**：备份→删除→恢复的顺序执行中，删除操作无差别销毁备份

```
时间线视图：
t0: /tmp/.variant-timers-backup-$$ 存在（T在D内）
t1: rm -rf /tmp/* /tmp/.* 执行
t2: T 被删除！（违反T∩D=∅不变量）
t3: mv T P → T不存在，恢复失败，P丢失
```

## 核心步骤（隔离验证三原则）

### 原则1：备份位置必须在删除作用域之外（核心规则）

```bash
# ❌ 反模式：备份放在删除目标内
local tmp_timer_backup="/tmp/.variant-timers-backup-$$"  # T在/tmp内
mv "${_VARIANT_TIMER_DIR}" "${tmp_timer_backup}"
rm -rf /tmp/* /tmp/.*  # 删除整个/tmp，备份被自毁！

# ✅ 正确模式：备份放在删除作用域之外
local tmp_timer_backup="/root/.variant-timers-backup-$$"  # T在/root，与/tmp同级
mv "${_VARIANT_TIMER_DIR}" "${tmp_timer_backup}"
rm -rf /tmp/* /tmp/.*  # 安全，/root不受影响
mv "${tmp_timer_backup}" "${_VARIANT_TIMER_DIR}"
```

**判断方法**：备份路径 T 和删除目标 D 不能有"被删除的目录"作为共同祖先。

### 原则2：删除前断言备份完整性

在执行删除操作前，验证备份确实存在且不在删除范围内：

```bash
# 防御性断言
local tmp_timer_backup="/root/.variant-timers-backup-$$"
mv "${_VARIANT_TIMER_DIR}" "${tmp_timer_backup}"

# 断言1：备份存在
[[ -d "${tmp_timer_backup}" ]] || { echo "ERROR: Backup failed"; return 1; }

# 断言2：备份不在删除范围内（关键！）
case "${tmp_timer_backup}" in
    /tmp/*|/var/tmp/*) echo "ERROR: Backup inside cleanup scope!"; return 1 ;;
esac

# 现在可以安全删除
rm -rf /tmp/* /tmp/.* /var/tmp/* /var/tmp/.* 2>/dev/null || true
```

### 原则3：优先使用白名单排除而非移开-恢复

如果保护数据就在删除目标目录内，优先考虑用 `find` 排除而非 mv-aside：

```bash
# 方案A（不推荐）：移开-恢复模式（需要验证T∩D=∅）
mv /tmp/preserve-dir /root/backup/
rm -rf /tmp/*
mv /root/backup/preserve-dir /tmp/

# 方案B（推荐）：find白名单删除——原地排除
find /tmp -mindepth 1 -maxdepth 1 ! -name "preserve-dir" -exec rm -rf {} + 2>/dev/null || true
```

方案B优势：不需要备份位置，不存在"备份被删"风险；原子性更好（不存在备份→删除→恢复之间的时间窗口）。

### 通用函数库：直接调用 safe_cleanup.sh

为避免每次手动实现隔离检查，项目已提供通用 Shell 库 [safe_cleanup.sh](../../../../scripts/shell/safe_cleanup.sh)，封装了所有安全检查：

```bash
# 在脚本开头 source
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/safe_cleanup.sh"  # 根据实际路径调整

# ── API 1（优先）：find 白名单原地删除，零备份风险 ──
safe_cleanup_dir /tmp                    # 清理/tmp所有内容
safe_cleanup_dir /tmp /tmp/preserve-me   # 清理/tmp但保留preserve-me

# ── API 2（兜底）：移开→清理→恢复，自动验证T∩D=∅ ──
safe_cleanup_move_aside /tmp /root /tmp/preserve-me
                          │    │      │
                          │    │      └─ 要保留的路径
                          │    └─ 备份父目录（必须在删除域外！）
                          └─ 清理目标
# 如果 backup_parent 在 target 内，函数直接报错返回（拒绝执行）

# ── API 3：独立断言，自定义流程时使用 ──
safe_assert_isolated "/root/my-backup" "/tmp" || exit 1

# ── API 4：安全临时文件（自动在目标域外创建） ──
tmpf=$(safe_mktemp_outside "/tmp" "myapp-")   # 文件
tmpd=$(safe_mktemp_outside "/tmp" "myapp-" -d) # 目录
```

**安全护栏**：
- 自动拒绝清理根目录 `/`（防误删）
- 自动解析 symlink/realpath，防止符号链接绕过检查
- 备份在删除域内时**直接拒绝执行**并输出错误，不抱侥幸心理
- 清理失败输出 WARN 但不 fatal exit（兼容 `set -e`）

完整测试：[test_safe_cleanup.sh](../../../../scripts/shell/test_safe_cleanup.sh)（15 项测试覆盖所有场景）

### 决策树

```
需要批量删除且有保护数据？
├─ 保护数据在删除目录内？
│   ├─ 能用find -exclude原地排除？ ──是──→ find白名单（原则3）
│   └─ 必须移开再恢复？ ──是──→ 移到父级/同级目录（原则1）+ 断言验证（原则2）
└─ 保护数据已在删除目录外？ ──是──→ 直接删除，但仍建议加断言（原则2）
```

## 反模式（不要这么做）

### ❌ 反模式1：隐藏文件备份在同目录

```bash
# ❌ 错误：/tmp/.* 会匹配 /tmp/.variant-timers-backup-$$
local backup="/tmp/.my-backup-$$"
mv /data/to-save "$backup"
rm -rf /tmp/* /tmp/.*   # .开头文件被.*匹配，备份被删
```

- **后果**：`*` 不匹配`.`开头文件，但 `.*` 匹配——双通配符是常见陷阱
- **正确做法**：备份到 `/root/`、`/var/backups/` 或其他不在删除域内的位置

### ❌ 反模式2：依赖文件系统语义而非显式验证

```bash
# ❌ 错误：假设mv原子性会保护文件，但rm -rf在mv完成后执行
mv /important /tmp/safe/
rm -rf /important/*      # 看似只删/important下的内容，但如果/tmp/safe是symlink到/important/safe...
```

- **后果**：符号链接、bind mount、硬链接可能使T和D实际指向同一inode
- **正确做法**：用 `realpath` 或 `readlink -f` 验证T的真实路径不在D内

### ❌ 反模式3：使用mktemp在待清理目录内创建临时文件

```bash
# ❌ 错误：mktemp默认在/tmp下创建
TMPFILE=$(mktemp)           # /tmp/tmp.XXXXXX，在/tmp内！
echo "important data" > "$TMPFILE"
rm -rf /tmp/* /tmp/.*       # TMPFILE被删除，数据丢失
cat "$TMPFILE"              # 失败！
```

- **后果**：`mktemp` 默认使用 `$TMPDIR` 或 `/tmp`，当后续清理/tmp时临时文件被销毁
- **正确做法**：`mktemp -p /root/` 或显式指定不在删除域内的目录

### ❌ 反模式4：docker prune不加标签过滤（跨领域同构）

```bash
# ❌ 错误：删除所有未使用资源，包括其他项目的容器/卷
docker system prune -a -f

# ✅ 正确：用label过滤，确保只有当前项目的资源被清理
docker system prune -a -f --filter "label=project=my-project"
```

- **同构本质**：D（所有未使用Docker资源）⊃ P（其他项目的停止容器），保护集P在删除域D内

## 检验标准

- [ ] 备份路径 T 的父目录不在删除目标 D 的目录树内
- [ ] 双重通配符 `* /.*` 使用时，已确认无 `.` 开头的保护文件
- [ ] 执行 `rm -rf` 前有防御性断言（备份存在性 + 位置验证）
- [ ] 保护数据优先使用 `find -exclude` 原地排除，而非 mv-aside
- [ ] `mktemp` 创建的临时文件不在待清理目录内
- [ ] Docker prune/cleanup 命令使用了label或name过滤
- [ ] 跨设备/符号链接场景下使用 `realpath` 验证真实路径

## 迁移示例

### 场景1：devcontainer-base cleanup.sh（本项目，源案例）

- **问题**：`cleanup_tmp()` 将计时器目录备份到 `/tmp/.variant-timers-backup-$$`，`rm -rf /tmp/* /tmp/.*` 删除备份，导致后续 Stage 5 验证失败
- **修复**：备份路径改为 `/root/.variant-timers-backup-$$`（在/tmp之外）
- **关键代码**：
  ```bash
  local tmp_timer_backup="/root/.variant-timers-backup-$$"
  mv "${_VARIANT_TIMER_DIR}" "${tmp_timer_backup}" 2>/dev/null || true
  rm -rf /tmp/* /tmp/.* /var/tmp/* /var/tmp/.* 2>/dev/null || true
  mkdir -p "$(dirname "${_VARIANT_TIMER_DIR}")"
  mv "${tmp_timer_backup}" "${_VARIANT_TIMER_DIR}" 2>/dev/null || true
  ```

### 场景2：WSL Docker存储清理五步法（正例对比）

- **来源**：`wsl-docker-storage-cleanup-five-step-method.md`
- **正确应用**：清理前快照保存到 `/tmp/cleanup_snapshot_${TS}.txt`，Docker prune 的删除域 D = `/var/lib/docker/*`（镜像/容器/卷），T = `/tmp/` 与 D 无交集
- **验证**：快照天然在删除域外，不需要额外隔离检查

### 场景3：跨领域——Docker prune保护其他项目容器（概念迁移）

- **类比**：`docker system prune -a -f` 的删除域 D 是"所有未使用资源"，其他项目的停止容器 P 在 D 内
- **迁移要点**：使用 `--filter label=project=xxx` 缩小D的范围，将P显式排除到D外
- **待验证**：不同编排系统（docker-compose/k8s）的label最佳实践

### 场景4：跨领域——数据库备份在数据目录内（概念迁移）

- **类比**：`pg_dump` 输出到 `/var/lib/postgresql/backup.sql` 然后清理旧数据目录，备份被清理销毁
- **迁移要点**：备份必须输出到数据目录之外（如 `/var/backups/`），与"备份放在/tmp外"同构
- **待验证**：具体数据库系统的备份路径最佳实践

## 与相关模式的关系

- **[shell-cleanup-non-blocking.md](shell-cleanup-non-blocking.md)**：兄弟模式——本模式解决"清理什么/不清理什么"的作用域问题，shell-cleanup-non-blocking解决"清理失败是否中断流程"的容错问题；两者常组合使用
- **[wsl-docker-storage-cleanup-five-step-method.md](wsl-docker-storage-cleanup-five-step-method.md)**：正例来源——快照到/tmp的设计天然满足隔离原则，可作为参考实现
- **[wsl-docker-command-safety.md](wsl-docker-command-safety.md)**：三层Shell模型中PowerShell/WSL/bash跨层解析也存在"作用域溢出"风险，与本模式的域隔离思想同构
- **[check-and-restore.md](check-and-restore.md)**：状态保存-检测-恢复模式与本模式的move-aside/cleanup/restore结构同构，但本模式聚焦文件系统删除场景的安全不变量

## Changelog

- **2026-08-15** (v1.0.0): 初始版本，从 cleanup.sh 备份自毁 bug 修复萃取，跨 wsl-docker-storage 正例对比验证，标记 L2-validated
