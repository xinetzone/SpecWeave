---
name: docker-cache-cmd
version: 1.0.0
description: "当用户提到'保存镜像'、'缓存Docker镜像'、'docker缓存'、'镜像缓存'、'加载镜像'、'docker镜像备份'、'封存镜像'、'docker save/load'、'镜像本地缓存'、'WSL重置后恢复镜像'、'docker镜像管理'、'docker-cache'时，必须使用此技能。提供Docker镜像本地缓存与快速恢复能力：将Docker镜像归档为tar.gz持久化到Windows文件系统，WSL2重置/Docker损坏后2-5分钟即可恢复（对比重新构建20-40分钟）。支持智能构建（Dockerfile checksum自动判断缓存命中）、并发安全（flock文件锁）、多线程压缩（pigz优先）、原子写入防损坏。不要手动调用docker save/load——本Skill封装了manifest管理、锁机制、原子写入和校验验证。"
argument-hint: "<save|load|build|list|clean|doctor> [镜像名] [选项]"
user-invocable: true
paths:
  - ".agents/scripts/docker-cache"
  - ".agents/docs/tools/docker-cache.md"
title: "Docker Cache 镜像本地缓存管理 Skill"
x-toml-ref: "../../../.meta/toml/.agents/skills/docker-cache-cmd/SKILL.toml"
---
# Docker Cache 镜像本地缓存管理 Skill

> ⚠️ **本Skill是脚本命令门面（L1索引层）**，遵循[渐进式披露三层架构](../../capabilities/ARCHITECTURE.md)：
> - L0：[.agents/ONBOARDING.md](../../ONBOARDING.md)（入口速查）
> - L1：本文件（<300行，触发词+决策树+核心命令+安全清单）
> - L2：脚本源码 [docker-cache](../../scripts/docker-cache) + 使用文档 [docker-cache.md](../../docs/tools/docker-cache.md)（完整实现与架构原理）

## 1. Skill ID
`docker-cache-cmd`

## 2. 功能描述

提供 Docker 镜像本地缓存与快速恢复能力，解决 WSL2 重置或 Docker 数据损坏导致的环境重建耗时问题（20-40分钟 → 2-5分钟）。

| 命令 | 推荐场景 | 优势 |
|------|---------|------|
| **build** | ⭐ 首次构建镜像/构建后自动缓存 | 智能缓存命中检测，未变更直接加载，已变更重新构建并更新缓存 |
| **save** | ⭐ 手动保存当前 Docker 镜像到缓存 | 原子写入防损坏，SHA256校验，自动更新manifest |
| **load** | ⭐ WSL2重置后/Docker损坏后快速恢复 | 从缓存加载镜像，2-5分钟恢复全部6层依赖链 |
| **list** | 查看缓存内容和状态 | 显示镜像大小、缓存时间、Docker中是否存在及ID是否匹配 |
| **doctor** | 环境检查与缓存完整性验证 | 检查Docker运行状态、依赖工具、manifest完整性、文件hash校验 |
| **clean** | 缓存清理（孤立文件/全部/指定镜像） | dry-run预览，SHA256校验，安全确认机制 |

核心功能：镜像归档为tar.gz持久化存储 → manifest元数据管理 → 并发安全文件锁 → 原子写入防损坏 → 多线程压缩加速 → Dockerfile checksum智能缓存命中。

> **为什么用本Skill而非手动 docker save/load？** 手动 save/load 存在四大问题：1) 无并发安全，多进程同时操作可能损坏缓存文件；2) 无原子写入，写入过程中断会留下损坏文件；3) 无元数据管理，不知道哪些镜像已缓存、对应哪个ID、用哪个Dockerfile构建的；4) 无智能缓存命中判断，每次都要手动判断是否需要重新构建。本Skill封装了flock文件锁、原子临时文件写入、manifest JSON管理、SHA256校验和Dockerfile checksum对比。

## 3. 何时使用本技能

当用户提到以下任何内容时触发：
- "保存镜像"、"缓存镜像"、"封存镜像"、"备份镜像"、"镜像缓存"
- "docker缓存"、"docker镜像管理"、"docker save"、"docker load"
- "加载镜像"、"恢复镜像"、"WSL重置后恢复"、"Docker损坏恢复"
- "docker-cache"、"镜像本地缓存"、"构建并缓存镜像"
- 涉及开发环境 Docker 镜像持久化、快速恢复的需求

> **关于触发**：即使没有明确说"用docker-cache"，只要涉及将Docker镜像保存到本地以便后续快速恢复，就应该使用本Skill。不要自己手动拼接docker save/load命令——那会绕过并发锁、原子写入和manifest管理。

## 4. 方案选择决策树

```
需要操作Docker镜像缓存？
├─ 首次构建镜像（需要构建+自动缓存）？ → build命令（第5.1节）
├─ 封存/保存当前镜像到缓存？ → save命令（第5.2节）
│   ├─ 保存所有镜像？ → save --all
│   └─ 保存指定镜像？ → save <image_name>
├─ WSL重置/Docker损坏，需要恢复？ → load命令（第5.3节）
│   ├─ 恢复所有镜像？ → load --all（最常用，2-5分钟）
│   └─ 恢复指定镜像？ → load <image_name>
├─ 查看缓存了哪些镜像？ → list命令（第5.4节）
├─ 检查环境依赖和缓存完整性？ → doctor命令（第5.5节）
└─ 清理缓存空间？ → clean命令（第5.6节，先dry-run！）
```

### ⚠️ 强制：触发时记录输入参数日志

决策前输出CMD_START日志（session前缀 `dc-YYYYMMDD-<action>`）：
```
[CMD-LOG] | level=INFO | cmd=docker-cache | step=S0 | event=CMD_START | session=dc-... | msg=开始Docker缓存操作：<简述> | ctx={"action":"save/load/build/...","target":"--all或镜像名","force":false}
```

> **为什么决策前必须记录日志？** 镜像操作（尤其是clean）是不可逆的写操作，CMD_START记录操作类型和目标便于操作失误后回溯排查。

**写操作（save/clean）原则**：clean操作必须先预览，确认无误再正式执行。

> **为什么clean需要预览确认？** 清理操作会删除缓存文件，一旦删除无法恢复（除非重新构建）。脚本内置交互确认机制，但自动化/CI场景下必须通过参数明确意图。

## 5. 核心命令（快速开始）

脚本路径：[docker-cache](../../scripts/docker-cache)

### 5.1 智能构建（build，首次构建/自动缓存）

```bash
cd d:\spaces\SpecWeave

# 构建镜像并自动缓存（推荐，自动检测Dockerfile变更决定缓存命中或重新构建）
bash .agents/scripts/docker-cache build -i devcontainer-base:chaos-ai-npu-latest \
    -f external/chaos/ai/Dockerfile -c external/chaos/ai/ --cn

# 使用国内镜像源加速构建
bash .agents/scripts/docker-cache build -i <image_name> -f <dockerfile> -c <context> --cn

# 强制重新构建（忽略缓存命中）
bash .agents/scripts/docker-cache build -i <image_name> -f <dockerfile> -c <context> --no-cache-load

# 传递构建参数
bash .agents/scripts/docker-cache build -i <image_name> -f <dockerfile> \
    --build-arg HTTP_PROXY=http://proxy:8080
```

> **智能缓存命中逻辑**：构建前计算Dockerfile的SHA256 checksum，与manifest中记录的checksum对比。如果一致且缓存文件存在，直接从缓存加载（2-5分钟）；如果不一致或缓存文件不存在，则重新构建并自动保存到缓存。

### 5.2 保存镜像（save，手动封存）

```bash
cd d:\spaces\SpecWeave

# 保存所有manifest中记录的镜像到缓存（最常用的"封存"命令）
bash .agents/scripts/docker-cache save --all

# 保存指定镜像
bash .agents/scripts/docker-cache save devcontainer-base:chaos-ai-npu-latest

# 强制重新保存（即使ID未变也重新保存）
bash .agents/scripts/docker-cache save --all --force
```

> **典型场景**：修改了Dockerfile并重新构建后，执行 `save --all` 封存当前所有镜像状态，确保WSL2重置后能恢复到最新状态。

### 5.3 加载镜像（load，快速恢复）

```bash
cd d:\spaces\SpecWeave

# WSL2重置后/Docker损坏后：恢复所有缓存镜像（2-5分钟，核心命令）
bash .agents/scripts/docker-cache load --all

# 加载指定镜像
bash .agents/scripts/docker-cache load devcontainer-base:chaos-ai-npu-latest
```

> **为什么load比docker build快80-90%？** load直接从tar.gz解压加载，不需要执行Dockerfile中的每一层构建指令（apt install、pip install、conda install等耗时操作），只需解压+docker load即可。

### 5.4 查看缓存（list）

```bash
cd d:\spaces\SpecWeave

# 列出所有缓存镜像（含大小、缓存时间、Docker中状态）
bash .agents/scripts/docker-cache list

# JSON格式输出（机器可读）
bash .agents/scripts/docker-cache list --json
```

list 输出中 Docker 列含义：
- ✅ 镜像在Docker中且ID一致（已加载）
- ⚠️ 镜像在Docker中但ID不一致（可能是旧版本）
- ❌ 镜像不在Docker中（需要load）

### 5.5 环境检查（doctor）

```bash
cd d:\spaces\SpecWeave

# 检查Docker运行状态、依赖工具、缓存完整性
bash .agents/scripts/docker-cache doctor
```

doctor 检查项：Docker安装/运行状态、缓存目录可写性、manifest合法性、压缩工具（pigz/gzip）、文件锁（flock）、python3、SHA256工具、缓存文件hash校验、孤立文件检测。

### 5.6 清理缓存（clean）

```bash
cd d:\spaces\SpecWeave

# 查看当前缓存统计（不加参数）
bash .agents/scripts/docker-cache clean

# 清理孤立文件（images/中存在但manifest未记录的文件）
bash .agents/scripts/docker-cache clean --orphans

# 清理指定镜像缓存
bash .agents/scripts/docker-cache clean devcontainer-base:chaos-ai-npu-latest

# 清理所有镜像缓存（会提示确认）
bash .agents/scripts/docker-cache clean --all

# 跳过确认直接清理（CI/自动化场景）
bash .agents/scripts/docker-cache clean --all -y
```

> 完整参数表和更多用法见L2文档 [docker-cache.md](../../docs/tools/docker-cache.md)。

## 6. 安全机制与并发保护

脚本内置多层安全防护：

- **原子写入**：保存镜像时先写入临时文件 `<name>.tar.gz.tmp.$$`，校验完成后通过 `mv` 原子重命名为最终文件名，写入中断不会损坏已有缓存
- **文件锁**：使用 `flock`（优先）或目录锁（降级方案），每个镜像独立锁文件，确保同一镜像的操作互斥、不同镜像可并行
- **SHA256校验**：保存时计算tar.gz文件的SHA256存入manifest，doctor检查时验证文件完整性
- **幂等加载**：load时检查Docker中镜像ID是否与缓存一致，一致则跳过不重复加载
- **临时文件清理**：脚本退出时通过trap清理残留的 `.tmp.$$` 临时文件
- **Python JSON校验**：manifest更新采用"临时文件→JSON解析校验→mv覆盖"三步法，确保写入合法JSON

## 7. 安全检查清单（执行写操作前逐项确认）

- [ ] Docker daemon 正在运行（执行 `docker info` 确认）
- [ ] 项目根目录正确（当前目录应为 SpecWeave 根目录或子目录）
- [ ] **clean 操作已预览确认**（不加 `-y` 参数时脚本会交互式确认；脚本场景确认意图正确）
- [ ] save 操作前确认镜像已正确构建且功能正常（避免缓存有问题的镜像）
- [ ] 有足够磁盘空间（缓存目录 `.docker-cache/images/` 需要存放所有镜像的tar.gz）
- [ ] 并发操作时脚本内置flock保护，无需手动加锁
- [ ] 操作完成后用 `list` 或 `doctor` 验证结果

> **为什么不要手动删除 .docker-cache/ 下的文件？** 手动删除tar.gz文件后manifest.json中仍有记录，会导致load时报"缓存文件不存在"错误。应使用 `clean` 命令，它会同步更新manifest。

## 8. 常见错误处理

| 错误场景 | 原因 | 处理方式 |
|---------|------|---------|
| "Docker 未运行或无法访问" | Docker daemon未启动 | 启动Docker Desktop/WSL2中的Docker服务 |
| "镜像不存在于 Docker 中" | save指定的镜像名在本地Docker中不存在 | 先docker build/pull，或检查镜像名拼写 |
| "manifest 中未找到镜像记录" | load指定的镜像未被缓存过 | 先用save或build缓存该镜像 |
| "缓存文件不存在" | tar.gz文件被手动删除，manifest中仍有记录 | 执行 `clean --orphans` 清理孤儿记录 |
| flock不可用 | 系统未安装flock | 脚本自动降级为目录锁，无需手动处理；可安装util-linux获取flock |
| pigz不可用 | 系统未安装pigz | 脚本自动降级为gzip；安装pigz可加速压缩/解压 |
| 缓存加载后ID不匹配 | docker load生成的镜像ID与保存时不同 | 通常是正常的（docker load对某些镜像会重新计算ID），功能不受影响 |
| 临时文件残留（.tmp.$$文件） | 脚本被强制kill（kill -9）导致trap未执行 | 执行 `find .docker-cache/images/ -name "*.tmp.*" -delete` 清理 |

> 加详细环境诊断请执行 `bash .agents/scripts/docker-cache doctor`。

## 9. Gotchas（陷阱与反直觉行为）

> **为什么需要Gotchas？** 错误处理记录"已知错误码及修复方式"，Gotchas记录"容易踩的坑、反直觉行为、容易被忽略的约束条件"——不会产生明确错误码但会导致结果不符合预期的隐性陷阱。

- **build命令需要从项目根目录或子目录执行**：脚本通过向上查找 `.git` 目录定位项目根，如果在项目外执行会找不到正确的缓存目录。建议始终 `cd d:\spaces\SpecWeave` 后再执行。
- **缓存目录默认在项目根的 `.docker-cache/`**：不是Docker数据目录，而是项目根目录下的隐藏目录，便于备份和版本控制排除。该目录应加入 `.gitignore`（已自动处理）。
- **save不会自动保存所有本地镜像**：`save --all` 只保存manifest中已记录的镜像（即曾经通过build/save缓存过的镜像），不会扫描Docker中所有镜像。新镜像首次需要手动 `save <image_name>` 或通过 `build` 命令自动缓存。
- **原子写入留下的.tmp文件**：正常退出时trap会清理临时文件，但如果脚本被 `kill -9` 强制终止，临时文件可能残留。这些 `.tmp.$$` 文件不会影响正常缓存（不会被manifest识别），但会占用磁盘空间，可用clean命令或手动find删除。
- **SHA256用于完整性校验而非写入前验证**：SHA256在文件写入完成后计算并存入manifest，用于后续doctor检查和load时校验；不是写入前计算再比对的"防篡改"机制。
- **Dockerfile checksum只检测Dockerfile本身变更**：build命令的智能缓存命中只看Dockerfile文件的SHA256，如果Dockerfile中COPY的文件变了但Dockerfile本身没变，checksum相同会误判为缓存命中。这种情况下需要使用 `--no-cache-load` 强制重新构建。
- **WSL2中执行 vs PowerShell中执行**：脚本是bash脚本，必须在WSL2或Git Bash中执行。PowerShell中需要通过 `wsl bash .agents/scripts/docker-cache ...` 调用。
- **压缩格式是tar.gz不是tar**：缓存文件使用gzip压缩（pigz多线程优先），不是未压缩的tar。不要手动用 `docker save > file.tar` 然后期望被load命令识别——load命令只识别manifest中记录的tar.gz文件。

## 10. 关键参考

| 参考 | 层级 | 路径 | 何时查阅 |
|------|------|------|---------|
| 使用文档（架构原理/工作流） | L2 | [docker-cache.md](../../docs/tools/docker-cache.md) | 理解架构、典型工作流、原子写入机制 |
| 脚本源码（完整实现） | L2 | [docker-cache](../../scripts/docker-cache) | 调试问题、查看完整参数、理解锁机制 |
| 产品需求规格 | Spec | [spec.md](../../../.trae/specs/docker-image-local-cache-management/spec.md) | 需求背景、验收标准 |
| 任务分解 | Spec | [tasks.md](../../../.trae/specs/docker-image-local-cache-management/tasks.md) | 实现任务清单 |
| 验证检查清单 | Spec | [checklist.md](../../../.trae/specs/docker-image-local-cache-management/checklist.md) | 38项验证点 |

## 11. 典型工作流

### 11.1 首次环境搭建

```bash
cd d:\spaces\SpecWeave
# 逐层构建（从基础镜像到上层镜像，每层build自动缓存）
bash .agents/scripts/docker-cache build -i devcontainer-base:conda-latest -f apps/docker-images/devcontainer-base/Dockerfile.conda -c apps/docker-images/devcontainer-base/ --cn
bash .agents/scripts/docker-cache build -i devcontainer-base:onnx-pytorch-latest -f apps/docker-images/devcontainer-base/Dockerfile.onnx-pytorch -c apps/docker-images/devcontainer-base/ --cn
# ... 其他层
bash .agents/scripts/docker-cache list  # 验证缓存
```

### 11.2 日常开发封存

```bash
# 修改Dockerfile并重新构建后，封存当前状态
bash .agents/scripts/docker-cache save --all
bash .agents/scripts/docker-cache doctor  # 验证完整性
```

### 11.3 WSL2重置后恢复

```bash
# WSL2重置后，Docker数据清空，只需：
cd d:\spaces\SpecWeave
bash .agents/scripts/docker-cache load --all
# 2-5分钟后所有镜像恢复，无需重新构建
```

## 12. Changelog

- **v1.0.0** (2026-08-10): 初始版本，封装docker-cache脚本为命令门面Skill，支持save/load/build/list/clean/doctor六个子命令，包含智能缓存命中、并发安全、原子写入、SHA256校验等核心功能。遵循五要素模型和渐进式披露三层架构。
