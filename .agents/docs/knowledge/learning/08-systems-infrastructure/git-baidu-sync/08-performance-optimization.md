# 08 - 性能优化

## 1. 为什么网盘同步场景需要特别关注 Git GC

在网盘同步环境中，Git 仓库的松散对象（loose objects）会导致严重的同步性能问题：

- **文件数量爆炸**：每次提交产生的 commit、blob、tree 对象都以独立文件形式存储在 `.git/objects/xx/` 目录下（40位十六进制文件名），一个中型仓库可能产生数千甚至数万个小文件
- **云同步客户端压力**：
  - 文件数过多导致同步扫描索引耗时呈线性增长
  - 大量小文件传输时网络连接频繁建立/断开，同步速度显著下降
  - 冲突概率随文件数增加而升高（两个设备同时操作不同对象可能触发文件锁冲突）
  - 部分网盘客户端对单目录文件数有隐性限制，超过阈值可能触发限流或索引失败
- **Pack 打包收益**：执行 `git gc` 后，数千个松散对象被打包为 1-2 个文件（`.pack` + `.idx`），文件数量减少 99% 以上，同步稳定性大幅提升

## 2. 松散对象 vs 打包对象对比表

| 维度 | 松散对象（Loose Objects） | 打包对象（Packed Objects） |
|------|--------------------------|----------------------------|
| **文件数量** | 每个 commit/blob/tree 对应一个独立文件（通常数千~数万个） | 通常仅 1-2 个文件（`.pack` 数据包 + `.idx` 索引文件） |
| **同步效率** | 大量小文件同步慢、易中断、断点续传效率低、易产生文件冲突 | 单一大文件连续传输稳定、支持断点续传、冲突概率极低 |
| **空间占用** | 每个对象独立 zlib 压缩，无 delta 复用 | 使用 delta 压缩（对象间差异存储），通常节省 30%-70% 磁盘空间 |
| **网盘客户端处理** | 文件数过多可能触发客户端限流、索引超时、内存占用过高 | 客户端处理高效，无文件数量压力 |
| **Git 访问性能** | 查找对象需遍历多个目录，稍慢 | 基于 idx 索引二分查找，访问更快 |

## 3. GC 策略建议

### 3.1 自动 GC 配置（推荐设置）

```bash
# 松散对象超过 6700 个时自动触发 GC（Git 默认值，不建议调低）
git config gc.auto 6700

# 保持最少的 pack 文件数（默认 50，设为 1 时自动合并多余 pack）
git config gc.autopacklimit 1

# 自动修剪多久前的不可达对象（默认 2.weeks.ago，可按需调整）
git config gc.pruneexpire "2.weeks.ago"
```

### 3.2 手动 GC 时机

| 场景 | 建议命令 | 频率 |
|------|----------|------|
| 大量提交/分支操作后（如 rebase、filter-repo） | `git gc --aggressive --prune=now` | 事件触发 |
| 新仓库注册到网盘同步前 | `git gc --aggressive --prune=now` | 注册前必做 |
| 执行 `git repack` 或大合并后 | `git gc --aggressive --prune=now` | 事件触发 |
| 日常定期维护 | `git gc` | 每周 1 次或同步明显变慢时 |
| 推送到远程前 | `git gc` | 可选，减少推送后同步压力 |

### 3.3 命令说明

- **`git gc --aggressive --prune=now`**：
  - `--aggressive`：使用更彻底的 delta 压缩算法，优化效果更好但耗时更长（大型仓库可能需要数分钟）
  - `--prune=now`：立即修剪所有不可达对象（不等待 2 周冷却期）
  - **注意**：日常维护不要频繁使用 `--aggressive`，会增加 CPU 消耗且收益递减

- **`git gc`（日常维护）**：
  - 执行标准打包和修剪，速度快
  - 适合常规优化，不会过度消耗资源

### 3.4 查看 GC 配置

```bash
# 查看当前 GC 相关配置
git config --get-regexp gc\.
```

## 4. .gitignore 最佳实践模板（网盘同步场景）

创建适用于网盘同步的 `.gitignore` 文件，减少不必要的同步文件：

```gitignore
# ===== 操作系统文件 =====
.DS_Store
Thumbs.db
Desktop.ini
$RECYCLE.BIN/
*.lnk

# ===== 编辑器和 IDE =====
.vscode/
.idea/
*.swp
*.swo
*~
*.sublime-workspace
*.sublime-project
.atom/
*.code-workspace

# ===== 构建产物 =====
build/
dist/
out/
target/
bin/
obj/
*.o
*.obj
*.exe
*.dll
*.so
*.dylib
*.class
*.pyc
*.pyo

# ===== 依赖目录 =====
node_modules/
vendor/
venv/
.venv/
env/
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
packages/

# ===== 日志文件 =====
*.log
logs/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*

# ===== 大文件（根据项目类型调整） =====
*.iso
*.zip
*.tar.gz
*.tgz
*.rar
*.7z
*.mp4
*.mov
*.avi
*.mkv
*.psd
*.ai
*.sketch
*.pdf（如不需要版本控制可取消注释）
*.dmg
*.pkg
*.msi

# ===== 临时文件 =====
*.tmp
*.temp
*.bak
*.cache
*.pid
*.seed
*.pid.lock

# ===== 敏感信息（必须忽略！）=====
*.key
*.pem
*.p12
*.pfx
.env
.env.local
.env.*.local
*.secret
secrets.json
credentials.json
config.local.json

# ===== 测试和覆盖率 =====
coverage/
.nyc_output/
*.lcov
.coverage
htmlcov/

# ===== 其他 =====
*.orig
*.rej
```

**重要提醒**：
- `.env` 等敏感配置文件绝对不能提交，应在 README 中说明如何创建本地配置
- 大文件规则需根据项目实际情况调整，二进制资产建议使用专门策略（见第 5 节）

## 5. 大文件处理策略（不使用 Git LFS）

网盘同步环境通常没有 LFS 服务器支持，因此采用以下替代方案：

### 5.1 方案 A：仓库外独立同步（推荐）

将大文件放在 Git 仓库外部的独立目录，通过网盘直接同步：

```
git-baidu-sync/
├── repos/           # Git 仓库（版本控制）
├── assets/          # 大文件资源（网盘直接同步，不纳入 Git）
│   ├── videos/
│   ├── datasets/
│   └── archives/
└── backups/         # 备份文件
```

在项目 README.md 中说明依赖关系：

```markdown
## 大文件依赖
本项目的数据集和视频资源位于同步目录的 `assets/` 下，
不在 Git 仓库内。克隆仓库后请确保 assets 目录已同步完成。
```

### 5.2 方案 B：.gitattributes 标记二进制文件

对于必须纳入版本控制的二进制文件，禁用 delta 压缩以避免 pack 文件膨胀：

```gitattributes
# 二进制文件不做 delta 压缩
*.png -delta
*.jpg -delta
*.jpeg -delta
*.gif -delta
*.ico -delta
*.pdf -delta
*.zip -delta
*.gz -delta
*.tar -delta
*.exe -delta
*.dll -delta
*.so -delta
*.dylib -delta
*.psd -delta
*.mp4 -delta
*.mov -delta
*.avi -delta

# 文本文件显式标记（可选）
*.md text
*.txt text
*.py text
*.js text
```

**原理**：二进制文件压缩后差异极小，delta 压缩会消耗大量 CPU 时间且无法显著减小体积，禁用后 pack 过程更快。

### 5.3 方案 C：定期清理大文件历史

如果大文件已被误提交到历史中，使用工具清理：

**使用 git filter-repo（推荐）：**

```bash
# 安装 git-filter-repo（Python 脚本，跨平台）
pip install git-filter-repo

# 删除所有 .mp4 文件的历史记录
git filter-repo --path-glob '*.mp4' --invert-paths

# 清理后强制执行 GC
git gc --aggressive --prune=now
```

**使用 BFG Repo-Cleaner（Java，适合大型仓库）：**

```bash
# 删除大于 100MB 的文件
java -jar bfg.jar --strip-blobs-bigger-than 100M my-repo.git
```

**注意**：历史重写后需要强制推送（`git push --force`），且所有协作者需要重新克隆。

### 5.4 方案 D：git bundle 分卷备份

对于大型仓库，使用 `git bundle` 分卷打包备份：

```bash
# 创建完整 bundle
git bundle create repo.bundle --all

# 分卷压缩（适合大仓库）
git bundle create - --all | 7z a -si repo.bundle.7z -v100m
# 或使用 split（Linux/macOS/Git Bash）
git bundle create - --all | split -b 100m - repo.bundle.part.
```

### 5.5 明确不推荐

❌ **不要将 >100MB 的大文件直接提交到 Git 仓库**：
- 会导致仓库体积快速膨胀
- 每次克隆都需要下载完整历史
- GC 和 delta 压缩耗时剧增
- 网盘同步压力大

## 6. 百度网盘选择性同步配置建议

在百度网盘客户端中配置选择性同步，只同步必要目录：

### 6.1 必须同步的目录

| 目录 | 必要性 | 说明 |
|------|--------|------|
| `repos/` | ✅ 必须 | Git 仓库主目录，所有版本控制数据都在这里 |
| `meta/` | ✅ 必须 | 仓库元数据、注册信息，缺失会导致仓库无法识别 |
| `locks/` | ✅ 必须 | 分布式锁文件目录（注意：`.lock` 临时锁文件可忽略，但目录本身要存在） |

### 6.2 可选同步目录（按需开启）

| 目录 | 建议 | 说明 |
|------|------|------|
| `backups/` | ⚠️ 按需 | 仓库备份，占用空间大但恢复必需；建议主设备同步，移动设备不同步 |
| `logs/` | ❌ 可不同步 | 运行日志，仅用于排查问题，不同步不影响功能 |
| `archive/` | ❌ 按需 | 归档仓库，仅在需要查阅历史时同步，新设备默认不同步 |
| `assets/` | ⚠️ 按需 | 大文件资源（见 5.1 节），根据项目需要同步 |

### 6.3 应排除同步的文件

在网盘客户端中添加以下排除规则：

```
# Git 临时锁文件
*.lock
.lock

# 操作系统临时文件
.DS_Store
Thumbs.db

# 网盘同步临时文件（百度网盘）
.baidunetdisk*
~*.tmp
```

## 7. 性能监控指标

定期检查以下指标，评估仓库健康状态：

### 7.1 松散对象数

```bash
# 查看松散对象数量（关注 loose 字段）
git count-objects -v

# 人类可读格式
git count-objects -vH
```

**健康指标**：
- `loose` < 1000：优秀
- 1000 < `loose` < 6700：正常
- `loose` > 6700：建议执行 `git gc`

### 7.2 Pack 文件数

```bash
# Windows PowerShell
(Get-ChildItem .git/objects/pack/*.pack -ErrorAction SilentlyContinue).Count

# Git Bash / Linux / macOS
ls .git/objects/pack/*.pack 2>/dev/null | wc -l
```

**健康指标**：
- pack 文件数 ≤ 2：优秀
- 2 < pack 文件数 < 10：正常
- pack 文件数 > 10：建议执行 `git gc --aggressive`

### 7.3 仓库总大小

```bash
# 查看 pack 文件大小（关注 size-pack 字段）
git count-objects -vH

# 查看 .git 目录总大小（Windows PowerShell）
"{0:N2} MB" -f ((Get-ChildItem .git -Recurse | Measure-Object Length -Sum).Sum / 1MB)
```

### 7.4 同步耗时记录

启用 git-doctor 日志记录同步耗时：

```bash
# 同步耗时日志默认位于 logs/ 目录
# 可通过以下命令查看最近同步记录
git doctor --log-tail 20
```

## 8. 常见性能问题与优化

| 现象 | 可能原因 | 解决方案 |
|------|----------|----------|
| **同步越来越慢** | 松散对象积累过多 | 执行 `git gc`，日常用 `git gc`，首次/大变更后用 `git gc --aggressive --prune=now` |
| **网盘客户端显示"同步中"很久不结束** | 1. 大量松散对象正在同步；2. 存在冲突文件；3. 大文件 delta 压缩导致临时文件多 | 1. 执行 `git gc` 减少文件数；2. 运行 `git doctor --check-conflicts` 检查冲突；3. 检查 `.git/objects/` 下是否有异常大量文件 |
| **推送后等待同步时间过长** | 1. 产生大量新松散对象；2. 网络带宽不足 | 1. 推送后执行 `git gc`；2. 检查网络连接，避免在网络高峰期执行大量推送 |
| **克隆/拉取后仓库体积异常大** | 历史中包含大文件 | 参考第 5.3 节清理大文件历史 |
| **GC 执行时间过长** | 仓库过大或使用了 `--aggressive` | 耐心等待；日常维护不加 `--aggressive` 参数；考虑分拆大仓库 |
| **同步时 CPU 占用高** | 网盘客户端索引大量小文件 | 执行 `git gc` 打包减少文件数；关闭不必要的实时扫描 |

### 8.1 快速诊断流程

当遇到同步性能问题时，按以下顺序排查：

```bash
# 1. 检查松散对象数
git count-objects -v | findstr loose

# 2. 检查 pack 文件数
# Windows
(Get-ChildItem .git/objects/pack/*.pack -ErrorAction SilentlyContinue).Count
# Git Bash
ls .git/objects/pack/*.pack 2>/dev/null | wc -l

# 3. 检查是否有冲突
git doctor --check-conflicts

# 4. 执行 GC
git gc

# 5. 如仍有问题，执行深度 GC
git gc --aggressive --prune=now
```

## 9. 一键优化脚本

性能优化检查和修复已集成到 `git-doctor` 工具的 `-Fix` 参数中：

```bash
# 执行健康检查并自动修复（包括 GC、冲突解决、锁清理等）
git doctor -Fix
```

该命令会自动执行以下操作：
- 检测松散对象数量，超过阈值时自动执行 GC
- 检查并清理无效锁文件
- 检测文件冲突并给出解决方案
- 验证仓库完整性
- 报告性能指标

**无需手动创建额外脚本**，直接使用 `git doctor -Fix` 即可完成常规性能优化。
