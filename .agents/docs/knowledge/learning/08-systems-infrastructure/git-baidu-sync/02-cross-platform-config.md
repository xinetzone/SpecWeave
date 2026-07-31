---
id: git-baidu-sync-cross-platform-config
title: Git 跨平台配置最佳实践（网盘同步场景）
source: original
created: 2026-07-31
tags:
  - git
  - cross-platform
  - config
  - baidu-netdisk
  - sync
---

# Git 跨平台配置最佳实践（网盘同步场景）

本文档针对百度网盘等云同步场景，整理 Git 在 Windows/macOS/Linux 三大平台间协作时的配置最佳实践，避免因换行符、文件权限、符号链接、大小写敏感等差异导致同步冲突和文件损坏。

## 问题背景

在网盘同步场景下，多个操作系统的设备可能同时访问同一个 Git 仓库（包括裸仓库和工作区），文件系统行为差异会导致：

1. **换行符混乱**：CRLF/LF 混合导致整个文件被标记为已修改
2. **权限位漂移**：Windows 不支持 Unix 执行位，导致 chmod +x 失效或文件权限意外变更
3. **符号链接失效**：Windows 默认将 symlink 转为普通文件复制
4. **大小写冲突**：README.md 与 readme.md 在 Linux 是两个文件，在 Windows/macOS 是同一个文件
5. **小文件风暴**：松散对象过多导致网盘同步效率低下、索引损坏
6. **GC 策略不当**：pack 文件数量过多增加同步冲突概率

## 核心配置项详解

### 跨平台兼容性矩阵

| 配置项 | Windows | macOS | Linux | 作用域建议 |
|--------|---------|-------|-------|-----------|
| `core.autocrlf` | `true` | `input` | `input` | 全局 |
| `core.filemode` | `false` | `true` | `true` | 仓库本地 |
| `core.symlinks` | `false` | `true` | `true` | 仓库本地 |
| `core.ignorecase` | `true` | `true` | `false` | 仓库本地（初始化时自动检测，勿手动修改） |
| `core.preloadindex` | `true` | `true` | `true` | 全局 |
| `core.fscache` | `true` | - | - | 全局（Windows 专用） |
| `gc.auto` | `6700` | `6700` | `6700` | 全局/仓库本地 |
| `gc.autopacklimit` | `1` | `1` | `1` | 全局/仓库本地 |
| `receive.denyCurrentBranch` | `updateInstead` | `updateInstead` | `updateInstead` | 非裸中央仓库 |
| `push.default` | `simple` | `simple` | `simple` | 全局 |

---

### 1. core.autocrlf —— 换行符处理

**是什么**：控制 Git 如何在工作区和版本库之间转换换行符。

| 值 | 行为 |
|----|------|
| `true` | 检出时将 LF 转为 CRLF；提交时将 CRLF 转为 LF |
| `input` | 提交时将 CRLF 转为 LF；检出时不转换 |
| `false` | 不做任何转换，按原样读写 |

**为什么这样设**：
- **Windows**：原生文本编辑器（记事本等）和大部分工具默认使用 CRLF，设为 `true` 保证检出文件与 Windows 生态兼容，同时提交时统一为 LF 存入版本库
- **macOS/Linux**：Unix 系系统原生使用 LF，设为 `input` 只在提交时做转换（防止意外提交 CRLF 文件），检出时保持 LF 不变

**不这样设会导致什么问题**：
- 全设 `false`：Windows 提交 CRLF 文件，Linux/macOS 拉取后整个文件行尾差异导致全文件标记为 modified，diff 污染
- 全设 `true`：Linux/macOS 检出文件被转为 CRLF，Shell/Python 脚本执行失败（`#!/usr/bin/env bash` 后跟 CRLF 会导致解释器错误）
- Windows 设 `input`：检出的脚本/批处理文件缺少 CRLF，记事本打开显示为一行

**验证方法**：
```bash
# 查看当前配置
git config core.autocrlf

# 测试：创建一个包含 CRLF 的文件，提交后检查版本库内是否为 LF
printf 'line1\r\nline2\r\n' > test-eol.txt
git add test-eol.txt
git commit -m "test eol"
git show HEAD:test-eol.txt | od -c | head -1
# 正确输出应只包含 \n，无 \r
```

---

### 2. core.filemode —— 文件执行权限位

**是什么**：控制 Git 是否跟踪文件的可执行权限位（Unix 文件模式中的 +x 位）。

| 值 | 行为 |
|----|------|
| `true` | 跟踪文件权限变更，`chmod +x script.sh` 会被记录为一次修改 |
| `false` | 忽略文件权限位差异，不将权限变更视为文件修改 |

**为什么这样设**：
- **Windows**：NTFS 虽然有 ACL，但没有 Unix 风格的用户/组/其他执行位概念，Git for Windows 无法可靠地持久化权限位。设为 `false` 避免权限位漂移导致每次同步都显示大量文件已修改
- **macOS/Linux**：完整支持 POSIX 权限，Shell 脚本等需要可执行权限才能直接运行，设为 `true` 正确跟踪 +x 位

**不这样设会导致什么问题**：
- Windows 设 `true`：从网盘同步仓库后，Windows 无法读取权限位，Git 可能误判所有可执行文件权限丢失，全部标记为 modified
- macOS/Linux 设 `false`：提交的 Shell 脚本失去可执行权限，其他开发者拉取后需要手动 `chmod +x`，CI/CD 流水线执行失败

**验证方法**：
```bash
git config core.filemode

# macOS/Linux 测试
chmod +x some-script.sh
git status
# 应显示 some-script.sh 已修改（模式变更）

# Windows 测试
# 从其他平台同步后，不应有大量权限变更导致的 modified
git status
# 除真实内容变更外，不应有无意义的模式变更
```

---

### 3. core.symlinks —— 符号链接支持

**是什么**：控制 Git 是否检出符号链接（symbolic link）为真实的 symlink，还是转为普通文本文件。

| 值 | 行为 |
|----|------|
| `true` | 检出符号链接为真实的文件系统 symlink |
| `false` | 将符号链接检出为包含目标路径的普通文本文件 |

**为什么这样设**：
- **Windows**：
  - 创建符号链接需要管理员权限或开发者模式开启（Windows 10 1703+）
  - 网盘客户端（如百度网盘）对 symlink 支持不一致，可能上传链接本身或跟随链接上传目标文件，导致重复存储或链接断裂
  - 跨用户/跨机器同步时 symlink 目标路径可能不存在
  - 设为 `false` 最安全，Git 将 symlink 内容作为普通小文件存储，避免网盘同步异常
- **macOS/Linux**：原生完美支持 symlink，设为 `true` 保留链接语义

**不这样设会导致什么问题**：
- Windows 设 `true`：
  - 无管理员权限时检出失败，报错 "unable to create symlink"
  - 网盘同步可能将 symlink 转换为目标文件的完整副本，仓库体积暴增
  - 同步到其他设备后链接变成普通文件，语义丢失
- macOS/Linux 设 `false`：项目中的符号链接（如 `node_modules/.bin/` 下的命令、配置软链接）变成普通文本文件，无法正常使用

**验证方法**：
```bash
git config core.symlinks

# 在支持 symlink 的平台测试
ln -s ../target.txt link.txt
git add link.txt
git commit -m "add symlink"
git show HEAD:link.txt
# 应输出 "target.txt"（符号链接存储的是目标路径）

# Windows 设为 false 时，检出的 link.txt 是包含 "../target.txt" 文本的普通文件
```

---

### 4. core.ignorecase —— 大小写敏感性

**是什么**：控制 Git 是否将文件名视为大小写不敏感。

| 值 | 行为 |
|----|------|
| `true` | `README.md` 和 `readme.md` 视为同一个文件 |
| `false` | `README.md` 和 `readme.md` 视为两个不同文件 |

**为什么这样设**：
- **Windows (NTFS)** 和 **macOS (APFS/HFS+) 默认**：文件系统大小写不敏感（case-insensitive but case-preserving），Git 初始化仓库时自动设为 `true`
- **Linux (ext4/btrfs/xfs)**：文件系统大小写敏感，Git 初始化时自动设为 `false`

**⚠️ 重要提示**：
- 此配置应在 `git init`/`git clone` 时由 Git 自动检测设置，**不要手动修改**
- 手动强制设为错误值会导致严重问题：在大小写敏感的 Linux 上设为 `true` 会让 Git 无法识别同目录下仅大小写不同的两个文件；在大小写不敏感的 Windows 上设为 `false` 会导致 "file already exists" 错误
- **跨平台最佳实践**：项目内**永远不要创建仅大小写不同的同名文件**，即使在 Linux 上也避免

**不这样设会导致什么问题**：
- Linux 设为 `true`：两个仅大小写不同的文件会互相覆盖，Git 工作区混乱
- Windows/macOS 设为 `false`：`git checkout` 时报错 "cannot create file 'Readme.md': File exists"
- 网盘同步场景：从 Linux 同步 `README.md` 和 `readme.md` 到 Windows，网盘客户端可能反复覆盖、产生冲突文件

**验证方法**：
```bash
git config core.ignorecase
# Git 初始化时自动设置，一般不需要手动验证

# 检查项目中是否存在仅大小写不同的文件（危险信号）
git ls-files | sort -f | uniq -di
# 如果输出非空，说明存在仅大小写不同的文件，需要重命名
```

---

### 5. core.preloadindex —— 索引预加载

**是什么**：启用并行预加载索引，加速 `git status`、`git diff` 等命令在大仓库上的执行速度。

| 值 | 行为 |
|----|------|
| `true` | 启动时并行扫描文件系统，提前填充 lstat 缓存 |
| `false` | 串行扫描，默认兼容模式 |

**为什么这样设**：
- **所有平台都设为 `true`**：这是一个纯粹的性能优化选项，无功能副作用
- 对包含上万文件的大仓库，`git status` 速度可提升 2-5 倍
- Git 2.1+ 默认已开启，但显式设置确保所有版本、所有平台一致生效
- 网盘同步场景下，文件系统操作是性能瓶颈，此优化尤为明显

**不这样设会导致什么问题**：
- 仅影响性能，不导致功能错误
- 大仓库中每次执行 `git status` 需要等待很长时间，降低开发效率
- 频繁的 status 检查增加网盘文件扫描压力，可能触发同步客户端的文件锁冲突

**验证方法**：
```bash
git config core.preloadindex
# 应输出 true

# 性能对比测试
time git status
# 与关闭时对比：git -c core.preloadindex=false status
```

---

### 6. core.fscache —— Windows 文件系统缓存

**是什么**：Windows 专用的文件系统元数据缓存优化，将目录扫描结果缓存到内存，减少重复的系统调用。

| 值 | 行为 |
|----|------|
| `true` | 启用 Windows 文件系统缓存（Git for Windows 2.8+ 支持） |
| `false` | 不缓存，每次都重新扫描 |

**为什么这样设**：
- **仅 Windows 设为 `true`**：Windows 的文件系统 API（FindFirstFile/FindNextFile）相对较慢，fscache 可显著提升大仓库的 status/diff 性能
- macOS/Linux 上此配置项不存在或被忽略，不需要设置
- 对包含大量文件的仓库（如 node_modules 未被正确忽略），性能提升尤为明显
- 在网盘映射盘/网络驱动器场景下，缓存效果更加显著

**不这样设会导致什么问题**：
- 仅性能问题，Windows 上 `git status` 等命令响应慢
- 无数据一致性风险——缓存会在文件操作时自动失效

**验证方法**：
```powershell
# Windows 验证
git config core.fscache
# 应输出 true

# macOS/Linux 验证
git config core.fscache
# 无输出或报错，属于正常
```

---

### 7. gc.auto —— 自动 GC 松散对象阈值

**是什么**：当版本库中松散对象（loose object，即单个存储的对象文件）数量超过此值时，Git 自动执行 `git gc --auto` 将其打包。

| 值 | 行为 |
|----|------|
| `6700` | 松散对象超过约 6700 个时自动打包（推荐值） |
| `0` | 禁用自动 GC |
| 默认值 `6700` 是 Git 出厂默认，但显式设置确保一致性 |

**为什么这样设**：
- **网盘同步场景的关键配置**：松散对象存储在 `.git/objects/xx/xxxxxx...` 路径下，每个对象一个文件
- 如果松散对象积累到几万甚至几十万个，`.git/objects/` 目录下会有海量小文件
- 网盘同步客户端处理大量小文件效率极低：
  - 每个小文件都需要单独上传/下载，产生大量网络请求
  - 大量小文件增加网盘索引和冲突检测的负担
  - 同步过程中文件被逐个更新，此时执行 Git 操作可能读到半同步状态，导致对象损坏
- 设为 `6700`（或更小，如 `1000`）让 Git 频繁打包，将松散对象合并为少数几个 `.pack` 文件
- `.pack` 文件是大的连续文件（通常几 MB 到几百 MB），网盘同步效率高、冲突概率低

**不这样设会导致什么问题**：
- 设太大（如 `50000`）或禁用 GC：`.git/objects/` 下堆积几万~几十万小文件
- 网盘同步极慢，CPU/磁盘/网络资源被小文件同步占满
- 同步过程中如果遇到断电/网盘客户端崩溃，可能导致对象文件损坏，仓库无法恢复
- 跨设备同步后，不同设备上的松散对象集不一致，容易产生冲突

**验证方法**：
```bash
git config gc.auto
# 应输出 6700

# 统计当前松散对象数量
find .git/objects -type f -name "[0-9a-f]*" | wc -l
# 不应长期超过 6700，执行 git gc 后应显著减少

# 手动触发 GC 验证
git gc --auto
# 执行后再次统计松散对象，应减少
```

---

### 8. gc.autopacklimit —— 自动打包保留包数量上限

**是什么**：执行 `git gc` 时，当 `.git/objects/pack/` 下的 pack 文件数量超过此值时，自动将多个 pack 合并为一个。

| 值 | 行为 |
|----|------|
| `1` | 始终保持只有 1 个 pack 文件（推荐用于网盘同步） |
| 默认值 `50` | 超过 50 个 pack 时才合并 |

**为什么这样设**：
- **网盘同步场景的关键配置**：默认值 `50` 意味着 Git 允许保留最多 50 个 pack 文件后才合并
- 每个 pack 文件都是一个独立的大文件，pack 数量越多：
  - 网盘需要同步的独立文件数越多，冲突概率越高
  - 如果多个设备同时 push，各自产生新的 pack 文件，同步后 pack 文件数量快速增长
  - 多个 pack 文件增加了网盘同步时的版本合并复杂度
- 设为 `1` 强制每次 GC 都将所有 pack 合并为单个 pack 文件，pack 目录中始终只有 1~2 个 pack 文件（1 个主 pack + 临时的 keep 文件）
- 单个 pack 文件虽然体积大，但网盘同步单个大文件的效率远高于多个中等文件，且冲突时恢复简单

**不这样设会导致什么问题**：
- 保持默认 `50`：经过一段时间多设备同步后，`.git/objects/pack/` 下累积几十个 pack 文件
- 每次 push/fetch 可能新增 pack 文件，不同设备新增不同的 pack，同步时文件数爆炸
- pack 文件之间有冗余对象，重复存储浪费网盘空间
- 极端情况下，pack 文件数量膨胀到数百个，`git gc` 耗时剧增

**验证方法**：
```bash
git config gc.autopacklimit
# 应输出 1

# 统计当前 pack 文件数量
ls .git/objects/pack/*.pack 2>/dev/null | wc -l
# 正常情况下应 ≤ 2（gc 运行过程中可能临时有多个）

# 执行 gc 验证合并
git gc
ls .git/objects/pack/*.pack 2>/dev/null | wc -l
# gc 完成后应只有 1 个 .pack 文件和对应的 .idx 文件
```

---

### 9. receive.denyCurrentBranch —— 非裸仓库推送行为

**是什么**：控制当向一个正在被检出（有工作区）的非裸仓库 push 时，Git 是否拒绝操作以及如何处理。

| 值 | 行为 |
|----|------|
| `refuse`（默认） | 拒绝向当前分支推送，报错 "refusing to update checked out branch" |
| `updateInstead` | 接收推送并自动更新工作区（如果工作区干净） |
| `warn` | 接收推送但打印警告，不更新工作区（危险） |
| `ignore` | 静默接收，不更新工作区（非常危险） |

**为什么这样设**：
- **裸仓库（bare repo）不需要设置**：裸仓库没有工作区，push 直接更新分支引用，无问题
- **网盘同步的非裸中央仓库**：某些场景下我们可能用非裸仓库作为中转（不推荐，但如果使用需要设为此值）
- 设为 `updateInstead`：当其他设备 push 到当前分支，如果工作区是干净的，自动将工作区更新到新提交；如果工作区有未提交修改则拒绝推送（保护机制）
- **裸仓库才是网盘同步的推荐方案**，如果确实需要使用非裸仓库作为同步点，此项必须配置

**不这样设会导致什么问题**：
- 保持默认 `refuse`：从设备 A 推送到设备 B 的非裸仓库时报错，同步失败
- 设为 `ignore`/`warn`：推送更新了 HEAD 引用但没更新工作区，导致工作区与索引不一致，Git 认为大量文件被修改或删除，非常混乱

**验证方法**：
```bash
git config receive.denyCurrentBranch
# 非裸中央仓库应输出 updateInstead
# 裸仓库无需设置（或为默认 refuse，但裸仓库 push 时不触发此检查）

# 检查仓库是否为裸仓库
git rev-parse --is-bare-repository
# true = 裸仓库，false = 非裸仓库
```

---

### 10. push.default —— 默认推送策略

**是什么**：控制 `git push` 不指定目标分支时的默认行为。

| 值 | 行为 |
|----|------|
| `simple`（Git 2.0+ 默认） | 只推送当前分支到其上游跟踪分支，且要求上游分支同名 |
| `current` | 推送当前分支到同名远程分支 |
| `upstream`/`tracking` | 推送当前分支到其上游分支（允许不同名） |
| `matching`（Git 1.x 默认） | 推送所有本地和远程都存在的同名分支 |

**为什么这样设**：
- **所有平台都显式设为 `simple`**：这是 Git 2.0 之后的默认值，也是最安全、最符合直觉的策略
- `simple` 的安全特性：
  - 只推送当前分支，不会意外推送其他分支
  - 要求本地分支与上游分支同名，避免推错分支
  - 如果当前分支没有上游，拒绝推送，提醒你先 `git push -u`
- 显式设置的原因：避免在老版本 Git（1.x）环境下默认使用 `matching` 策略导致意外推送所有分支

**不这样设会导致什么问题**：
- 使用 `matching`：执行 `git push` 会把所有本地有对应远程分支的分支全部推送，可能将未准备好的 feature/wip 分支意外推送到中央仓库
- 使用 `current`：第一次 push 到新仓库时自动在远程创建同名分支，如果没有权限创建远程分支会失败
- 不设置在老 Git 上行为不确定

**验证方法**：
```bash
git config push.default
# 应输出 simple

# 测试：在一个有多个分支的仓库执行
git checkout feature/test
git push --dry-run
# 应显示只推送 feature/test 分支，且提示设置上游（如果未设置）
```

## .gitattributes 模板

除了 Git 配置，仓库根目录的 `.gitattributes` 文件是跨平台换行符控制的**强制手段**（优先级高于 `core.autocrlf`），确保无论用户本地配置如何，文件都以正确的换行符入库。

在仓库根目录创建 `.gitattributes`：

```gitattributes
# 默认：所有文本文件自动检测换行符，入库时统一为 LF
* text=auto

# ===== 明确指定需要 LF 换行符的文件（跨平台脚本/源码）=====
# Shell 脚本（必须 LF，否则 shebang 行失败）
*.sh text eol=lf
*.bash text eol=lf
*.zsh text eol=lf
*.fish text eol=lf

# Python/Ruby/Perl/PHP 等脚本语言
*.py text eol=lf
*.rb text eol=lf
*.pl text eol=lf
*.pm text eol=lf
*.php text eol=lf

# 编程语言源码（统一 LF）
*.c text eol=lf
*.h text eol=lf
*.cpp text eol=lf
*.hpp text eol=lf
*.cc text eol=lf
*.hh text eol=lf
*.java text eol=lf
*.go text eol=lf
*.rs text eol=lf
*.js text eol=lf
*.jsx text eol=lf
*.ts text eol=lf
*.tsx text eol=lf
*.mjs text eol=lf
*.cjs text eol=lf
*.css text eol=lf
*.scss text eol=lf
*.less text eol=lf
*.html text eol=lf
*.htm text eol=lf
*.xml text eol=lf
*.json text eol=lf
*.yaml text eol=lf
*.yml text eol=lf
*.toml text eol=lf
*.ini text eol=lf
*.cfg text eol=lf
*.conf text eol=lf
*.env text eol=lf
*.sql text eol=lf

# 文档类（Markdown/reStructuredText）
*.md text eol=lf
*.markdown text eol=lf
*.rst text eol=lf
*.txt text eol=lf
*.textile text eol=lf

# Makefile 和构建文件
Makefile text eol=lf
makefile text eol=lf
*.mk text eol=lf
CMakeLists.txt text eol=lf
*.cmake text eol=lf
Dockerfile text eol=lf
docker-compose.yml text eol=lf
*.service text eol=lf
*.timer text eol=lf

# Git 相关文件
.gitignore text eol=lf
.gitattributes text eol=lf
.gitmodules text eol=lf
.mailmap text eol=lf

# ===== 明确指定需要 CRLF 换行符的文件（Windows 专用）=====
# Windows 批处理脚本（必须 CRLF，否则 cmd.exe 解析失败）
*.bat text eol=crlf
*.cmd text eol=crlf
*.ps1 text eol=crlf
*.psm1 text eol=crlf
*.psd1 text eol=crlf

# Windows 特定配置
*.reg text eol=crlf
*.inf text eol=crlf
AutoHotkey.ahk text eol=crlf
*.ahk text eol=crlf

# ===== 二进制文件（禁止换行符转换，禁止 diff）=====
# 图片
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.bmp binary
*.ico binary
*.svg binary
*.webp binary
*.tiff binary
*.tif binary

# 字体
*.ttf binary
*.otf binary
*.woff binary
*.woff2 binary
*.eot binary

# 文档二进制
*.pdf binary
*.doc binary
*.docx binary
*.xls binary
*.xlsx binary
*.ppt binary
*.pptx binary
*.odt binary
*.ods binary
*.odp binary

# 压缩包/归档
*.zip binary
*.tar binary
*.gz binary
*.bz2 binary
*.xz binary
*.7z binary
*.rar binary
*.zst binary
*.lz binary
*.lzma binary
*.tgz binary
*.tbz2 binary

# Git 内部包文件（重要！防止 pack 被当作文本处理）
*.pack binary
*.idx binary
*.bundle binary

# 可执行文件/库
*.exe binary
*.dll binary
*.so binary
*.dylib binary
*.a binary
*.lib binary
*.o binary
*.obj binary
*.bin binary
*.msi binary

# 音视频
*.mp3 binary
*.mp4 binary
*.wav binary
*.flac binary
*.ogg binary
*.avi binary
*.mkv binary
*.mov binary
*.webm binary

# 其他二进制格式
*.sqlite binary
*.db binary
*.swf binary
*.class binary
*.jar binary
*.war binary
*.pyc binary
*.pyo binary
*.pyd binary
*.so binary
*.egg binary
*.whl binary
```

**为什么用 `.gitattributes` 而不只是依赖 `core.autocrlf`**：
1. `.gitattributes` 随仓库提交，所有协作者自动生效，不依赖每个人的本地 Git 配置
2. 可以按文件类型/路径精细控制，而 `core.autocrlf` 是全局一刀切
3. 新开发者克隆仓库即获得正确的换行符配置，无需手动配置 Git
4. 二进制文件明确标记 `binary` 可防止 Git 尝试 diff 或转换，减少误判

## 全局配置 vs 仓库本地配置

Git 配置有三个作用域，优先级从高到低：
1. `--local`：仓库级，写入 `<repo>/.git/config`，仅对当前仓库生效，优先级最高
2. `--global`：用户级，写入 `~/.gitconfig`（Windows：`%USERPROFILE%\.gitconfig`），对当前用户所有仓库生效
3. `--system`：系统级，写入 `/etc/gitconfig`（Windows：Git 安装目录），对系统所有用户生效

### 配置作用域推荐表

| 配置项 | 推荐作用域 | 理由 |
|--------|-----------|------|
| `core.autocrlf` | **global** | 属于用户工作环境偏好，跟随用户而不是仓库；Windows 用户设 true，macOS/Linux 用户设 input |
| `core.filemode` | **local** | 取决于文件系统，网盘同步的裸仓库/共享仓库必须显式设置；随仓库走避免跨设备混乱 |
| `core.symlinks` | **local** | 取决于操作系统和使用场景，共享仓库设为 false 最安全 |
| `core.ignorecase` | **local**（Git 自动设置） | 初始化时 Git 自动检测文件系统设置，**不要手动修改** |
| `core.preloadindex` | **global** | 纯性能优化，用户级偏好，所有仓库受益 |
| `core.fscache` | **global**（仅 Windows） | Windows 系统级性能优化，用户所有仓库受益 |
| `gc.auto` | **global** 或 local | GC 策略对所有仓库都适用，可全局设置；特殊仓库可单独覆盖 |
| `gc.autopacklimit` | **global** 或 local | 同上，网盘同步相关仓库建议显式设置 |
| `receive.denyCurrentBranch` | **local** | 仅非裸中央仓库需要设置，是仓库属性而非用户属性 |
| `push.default` | **global** | 用户的推送偏好，适合全局设置 |
| `user.name` | **global** | 用户身份，跟随用户 |
| `user.email` | **global** | 用户身份，跟随用户 |
| `core.quotepath` | **global** | 建议设为 false，让中文文件名正常显示 |
| `core.longpaths` | **global**（Windows） | Windows 建议设 true，解除 260 字符路径限制 |

### 全局配置建议

执行以下命令设置用户全局配置（每个设备设置一次）：

**Windows**：
```powershell
git config --global core.autocrlf true
git config --global core.preloadindex true
git config --global core.fscache true
git config --global gc.auto 6700
git config --global gc.autopacklimit 1
git config --global push.default simple
git config --global core.longpaths true
git config --global core.quotepath false
```

**macOS/Linux**：
```bash
git config --global core.autocrlf input
git config --global core.preloadindex true
git config --global gc.auto 6700
git config --global gc.autopacklimit 1
git config --global push.default simple
git config --global core.quotepath false
```

### 网盘同步仓库的本地配置建议

对于百度网盘同步目录下的**每个仓库**（裸仓库尤其重要），在仓库内执行：

**Windows**（进入仓库目录后）：
```powershell
git config --local core.filemode false
git config --local core.symlinks false
git config --local core.ignorecase true
# gc 配置如果全局已设，此处可省略
git config --local gc.auto 6700
git config --local gc.autopacklimit 1
# 仅非裸中央仓库需要：
# git config --local receive.denyCurrentBranch updateInstead
```

**macOS/Linux**（进入仓库目录后）：
```bash
git config --local core.filemode true
git config --local core.symlinks true
git config --local core.ignorecase false
git config --local gc.auto 6700
git config --local gc.autopacklimit 1
```

**⚠️ 注意**：如果裸仓库会被多个平台设备访问（网盘同步场景就是如此），保守的跨平台统一设置是：
- `core.filemode false`（Windows 无法处理权限位，统一关闭避免冲突）
- `core.symlinks false`（避免 Windows 无法创建 symlink 导致的问题）
- 所有平台都使用这套保守设置，兼容性最好

## 自动配置脚本

项目提供两个自动化配置脚本（PowerShell 和 Bash），自动检测操作系统并应用推荐配置：

| 脚本 | 路径 | 适用平台 |
|------|------|---------|
| PowerShell | `.agents/scripts/git-baidu-sync/setup-git-config.ps1` | Windows |
| Bash | `.agents/scripts/git-baidu-sync/setup-git-config.sh` | macOS/Linux/Git Bash |

### 脚本功能

1. 自动检测当前操作系统
2. 根据 OS 应用对应的推荐配置
3. 支持 `--global` / `--local` 参数（默认 `--global`）
4. 输出每个配置项的变更情况（旧值 → 新值）
5. 检测 Git 版本是否 ≥ 2.30，过低给出警告
6. 可生成 `.gitattributes` 模板到指定目录
7. 设置完成后自动运行 `git config --list` 验证

### 使用方法

**设置全局配置（推荐首次使用时执行一次）**：
```powershell
# Windows PowerShell
.\setup-git-config.ps1
# 或显式指定 --global
.\setup-git-config.ps1 --global
```

```bash
# macOS/Linux
chmod +x setup-git-config.sh
./setup-git-config.sh
```

**为网盘同步仓库设置本地配置（在仓库目录内执行）**：
```powershell
# 在裸仓库目录下执行
cd D:\BaiduSync\git-sync\repos\my-project.git
.\setup-git-config.ps1 --local
```

```bash
# 在裸仓库目录下执行
cd ~/BaiduSync/git-sync/repos/my-project.git
./setup-git-config.sh --local
```

**生成 .gitattributes 模板到当前目录**：
```powershell
.\setup-git-config.ps1 --attributes
```

```bash
./setup-git-config.sh --attributes
```

**生成 .gitattributes 到指定目录**：
```powershell
.\setup-git-config.ps1 --attributes --target-dir D:\projects\my-repo
```

```bash
./setup-git-config.sh --attributes --target-dir ~/projects/my-repo
```

## 配置验证清单

配置完成后，按以下清单验证：

- [ ] `git config core.autocrlf` —— Windows 为 `true`，macOS/Linux 为 `input`
- [ ] `git config core.filemode` —— 网盘共享仓库统一为 `false`，纯 macOS/Linux 仓库为 `true`
- [ ] `git config core.symlinks` —— 网盘共享仓库统一为 `false`，纯 macOS/Linux 仓库为 `true`
- [ ] `git config core.preloadindex` —— 所有平台为 `true`
- [ ] Windows 上 `git config core.fscache` 为 `true`
- [ ] `git config gc.auto` 为 `6700`
- [ ] `git config gc.autopacklimit` 为 `1`
- [ ] `git config push.default` 为 `simple`
- [ ] 仓库根目录存在 `.gitattributes` 且内容正确
- [ ] `git status` 执行干净，无意外的 modified 文件
- [ ] 执行 `git gc` 后 pack 文件数 ≤ 2
- [ ] 创建 Shell 脚本提交后，版本库内换行符为 LF
- [ ] Windows 上创建 `.bat` 脚本提交后，版本库内换行符为 CRLF

## 常见问题排查

### Q: Windows 克隆仓库后所有文件都显示 modified？

**排查**：
1. 检查 `core.autocrlf` 是否为 `true`：`git config core.autocrlf`
2. 检查仓库是否有 `.gitattributes`，其中是否对相关文件设置了 `eol=lf`
3. 如果 `.gitattributes` 设了 `*.sh eol=lf` 但你在 Windows，这是正常的——脚本文件检出就是 LF，这样跨平台才正确
4. 如果是所有文本文件都显示 modified，可能是 `.gitattributes` 设置后没有重新归一化：
   ```bash
   git add --renormalize .
   git commit -m "renormalize line endings"
   ```

### Q: macOS/Linux 上 Shell 脚本无法执行，提示 bad interpreter？

**排查**：
1. 检查脚本换行符：`head -1 your-script.sh | od -c`
2. 如果看到 `\r\n`，说明文件被存为 CRLF
3. 检查 `.gitattributes` 是否有 `*.sh text eol=lf`
4. 检查本地 `core.autocrlf` 是否为 `input`（macOS/Linux），不能是 `true`
5. 修复：重新归一化并提交
   ```bash
   git add --renormalize *.sh
   git commit -m "fix shell script line endings to LF"
   ```

### Q: Windows 提示 unable to create symlink？

**排查**：
1. 这是 `core.symlinks=true` 但你没有权限创建符号链接
2. 网盘同步仓库应设 `core.symlinks=false`
3. 临时解决：以管理员身份运行，或开启 Windows 开发者模式
4. 永久解决：`git config core.symlinks false`，然后重新克隆或 checkout

### Q: .git/objects/ 下文件特别多，网盘同步很慢？

**排查**：
1. 统计松散对象数量：`find .git/objects -type f | wc -l`（Linux/macOS）或 PowerShell: `(Get-ChildItem -Recurse -File .git/objects).Count`
2. 检查 `gc.auto` 配置：`git config gc.auto`
3. 如果松散对象超过 6700，手动执行 GC：`git gc --aggressive --prune=now`
4. 检查 `gc.autopacklimit` 是否为 1：`git config gc.autopacklimit`
5. 设置 `git config gc.auto 6700` 和 `git config gc.autopacklimit 1`，让 Git 自动维护

### Q: 两个文件仅大小写不同，同步到 Windows 后丢失？

**排查**：
1. 这是跨平台协作的根本性问题，Windows/macOS 默认文件系统大小写不敏感
2. **预防**：永远不要在项目中创建仅大小写不同的文件/目录
3. 检查是否存在：`git ls-files | sort -f | uniq -di`
4. 如果已存在，在 Linux 环境下重命名其中一个文件，提交后同步到所有平台
