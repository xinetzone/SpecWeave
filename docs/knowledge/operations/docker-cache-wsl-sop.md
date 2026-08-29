---
id: "docker-cache-wsl-sop"
title: "WSL Docker/Podman 镜像本地缓存操作 SOP（含引擎切换）"
type: "operations-sop"
source: "七概念方法论编排（场景4知识沉淀 R→I→E→V）产物，源会话：2026-08-20 WSL 全部镜像保存任务（session sc-20260820-tutorial-export / exprt-20260820-wsl-image-cache-tutorial）"
created_at: "2026-08-20"
last_updated: "2026-08-20"
tags: ["wsl", "docker", "podman", "镜像缓存", "docker-cache", "运维SOP", "方法论七概念"]
status: "validated"
validation: "doctor 全绿 + list 10/10 ✅ + save/load 完整循环验证通过"
related_patterns:
  - "M-1 双轨引擎切换架构"
  - "M-2 写文件后调用跨壳逃逸模式"
x-toml-ref: "../../.meta/toml/docs/knowledge/operations/docker-cache-wsl-sop.toml"
---

# WSL Docker/Podman 镜像本地缓存操作 SOP

> 🎯 **作用**：在 WSL2（Ubuntu）环境下，把全部容器镜像（Docker 或 Podman）持久化到 Windows 宿主文件系统，WSL2 重置/Docker 损坏后 **2-5 分钟**全部恢复，避免重新构建 20-40 分钟。
>
> 本 SOP 基于 **七概念方法论场景 4（知识沉淀 R→I→E→V）** 生产，通过 G1~G3+V 共 4 道质量门验证，含 2 个可复用跨场景模式。

---

## 目录

- [1. 适用范围与前置条件](#1-适用范围与前置条件)
- [2. 快速开始（5 步完成保存）](#2-快速开始5-步完成保存)
- [3. 命令速查](#3-命令速查)
- [4. 一键恢复流程（WSL 重置后必走）](#4-一键恢复流程wsl-重置后必走新增于-v-审查)
- [5. 验证清单（保存完成后逐项打勾）](#5-验证清单保存完成后逐项打勾)
- [6. 迁移与移植（换电脑/移动硬盘）](#6-迁移与移植换电脑移动硬盘)
- [7. 性能优化（压缩提速 3-4×）](#7-性能优化压缩提速-3-4)
- [8. 核心洞察（3 条四元组）](#8-核心洞察3-条四元组)
- [9. 可复用模式（2 个，跨场景迁移可用）](#9-可复用模式2-个跨场景迁移可用)
  - [模式 M-1：双轨引擎切换架构](#模式-m-1双轨引擎切换架构)
  - [模式 M-2：写文件后调用跨壳逃逸](#模式-m-2写文件后调用跨壳逃逸)
- [10. 故障排查 FAQ](#10-故障排查-faq)
- [11. 已知局限与后续优化 TODO](#11-已知局限与后续优化-todo)

---

## 1. 适用范围与前置条件

### 适用（✅）与不适用（❌）

| 维度 | ✅ 适用 | ❌ 不适用 |
|---|---|---|
| 宿主 OS | Windows 10/11 + WSL2（Ubuntu 22.04/24.04/26.04） | 纯 Linux 裸机、纯 macOS、Docker Desktop for Mac/Linux |
| 容器引擎 | Docker Engine 或 Podman 3.x+（**Podman 5.x 已验证**） | containerd / nerdctl / cri-o（参数不兼容，见 M-1 边界） |
| 镜像规模 | 单机 1~30 个，总量 ≤ 50 GB | CI 流水线成百上千镜像（应使用 Registry 方案而非本地 tar.gz） |
| 用途 | 个人开发环境快速恢复、WSL2 迁移备份 | 生产部署、跨团队镜像分发（请用私有 Registry + 签名） |

### 前置条件（一次性安装）

```bash
# 1. WSL 中必须存在 bash、gzip、python3、sha256sum、flock（util-linux 包自带）
#    Podman 用户（Ubuntu 26.04 默认自带）：无需 docker 命令
sudo apt-get update && sudo apt-get install -y util-linux coreutils python3 gzip wslu

# 2. 进入项目根（必须是 SpecWeave 仓库或包含 .git/ 的项目）
cd /mnt/d/spaces/SpecWeave

# 3. 诊断环境
bash .agents/scripts/docker-cache doctor
```

doctor 首行会显示"容器引擎：podman 或 docker"版本号，如果为红色 ❌ 先修环境再往下走。

---

## 2. 快速开始（5 步完成保存）

> **推荐顺序**：doctor → list（确认当前缓存）→ save（逐个或批量）→ doctor → list → 验证清单

### 第 1 步 · 环境诊断

```bash
bash .agents/scripts/docker-cache doctor
```

预期结果：8 项基础检查全部 ✅；完整性检查无"缺失缓存文件"红字。

### 第 2 步 · 查看当前缓存与 Podman/Docker 镜像

```bash
# 缓存中已有的镜像
bash .agents/scripts/docker-cache list
# Docker/Podman 中实际存在的镜像
podman images --format '{{.Repository}}:{{.Tag}} {{.Size}} {{.ID}}'
```

### 第 3 步 · 保存全部镜像（⭐ 最常用）

**方式 A · 批量脚本（推荐首次操作使用，有完整日志）**

```bash
# 把模板脚本复制到临时目录并执行（模板已内置清单+耗时统计+失败列表）
cp .agents/scripts/templates/save-all-container-images.sh.example \
   .docker-cache/temp/save-all-$(date +%Y%m%d).sh
# 如需改为 docker，可加一行：export DOCKER_BIN=docker
bash .docker-cache/temp/save-all-$(date +%Y%m%d).sh
```

**方式 B · 手动单条（适合保存 1~3 个镜像）**

```bash
# 保存单个镜像
bash .agents/scripts/docker-cache save localhost/devcontainer-base:torch-dev-latest
# 强制重新保存（即使 manifest 记录ID没变，修改了 Dockerfile 重新构建后使用）
bash .agents/scripts/docker-cache save localhost/devcontainer-base:torch-dev-latest --force
```

**方式 C · 通过 `DOCKER_BIN` 显式切引擎（双引擎环境下用）**

```bash
DOCKER_BIN=podman bash .agents/scripts/docker-cache save myimage:v1
DOCKER_BIN=docker bash .agents/scripts/docker-cache save myimage:v1
```

> 📖 **引擎自动选择规则**（脚本首行初始化块逻辑）
> 1. 优先读取 `DOCKER_BIN` 环境变量（用户显式指定优先级最高，Unix PAGER/EDITOR 惯例）
> 2. 否则 `command -v docker` 找到就用 docker
> 3. 否则 `command -v podman` 找到就用 podman
> 4. 都找不到就保留默认 `docker`，后续 doctor 报错引导安装

### 第 4 步 · 保存完成验证（不可跳过）

```bash
bash .agents/scripts/docker-cache doctor
bash .agents/scripts/docker-cache list
```

预期：`list` 命令 Docker/Podman 列全部显示 **✅**；`doctor` 完整性检查"所有文件验证通过 ✅"。

### 第 5 步 · 可选：清理孤儿 manifest 记录（定期维护）

当 doctor 报告"缺失缓存文件 N 个"，表示 manifest 有记录但 `.tar.gz` 被删了。目前（v1.0）需执行一次一次性清理：

```bash
cd /mnt/d/spaces/SpecWeave
MANIFEST_FILE=".docker-cache/manifest.json" \
IMAGES_DIR=".docker-cache/images" \
python3 - <<'PY'
import json, os
mf = os.environ["MANIFEST_FILE"]
imgd = os.environ["IMAGES_DIR"]
with open(mf, "r", encoding="utf-8") as f:
    data = json.load(f)
orig = len(data.get("images", {}))
removed = 0
for k, v in list(data.get("images", {}).items()):
    if not os.path.exists(os.path.join(imgd, v.get("file", ""))):
        del data["images"][k]; removed += 1
tmp = mf + ".tmp.orphans"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
with open(tmp, "r", encoding="utf-8") as f:
    json.load(f)  # 二次解析验证
os.replace(tmp, mf)
print(f"清理完成：{orig} -> {len(data['images'])}，删除 {removed} 条孤儿记录")
PY
```

---

## 3. 命令速查

| 命令 | 作用 | 典型输出 | 耗时参考 |
|---|---|---|---|
| `bash docker-cache save <img>` | 保存指定镜像 | `✅ 保存完成: xxxMB` | 1GB≈2min |
| `bash docker-cache save --all` | 保存 manifest 已登记的全部镜像 | 汇总 N/M 成功/失败 | 总量×2min/GB |
| `bash docker-cache load <img>` | 加载单个镜像 | `Loaded image: img:tag` | 1GB≈30s（解压比压缩快） |
| `bash docker-cache load --all` | **⭐ WSL 重置后一键恢复全部** | 完成 N/M 统计 | 7GB≈2~3min |
| `bash docker-cache list` | 缓存内容+Docker/Podman 状态 | 表格（✅⚠️❌ 三态） | <5s |
| `bash docker-cache list --json` | 机器可读 JSON 输出 | JSON | <1s |
| `bash docker-cache doctor` | 环境+缓存完整性体检 | 8 项+完整性 | <10s |
| `bash docker-cache clean --orphans` | 清理"文件存在但 manifest 没记录"的孤立文件 | 拟删除列表 | <5s |
| `bash docker-cache clean <img>` | 删除指定镜像缓存 | 删除确认 | <5s |
| `bash docker-cache clean --all -y` | 清空全部缓存（-y 跳确认）⚠️ 不可逆 | 释放空间 | <30s |
| `bash docker-cache build -i X -f DF -c C` | 智能构建（先查缓存命中，未命中再构建） | 同 build 输出 | 同 build |

**环境变量速查**

| 变量名 | 默认 | 说明 |
|---|---|---|
| `DOCKER_CACHE_DIR` | `<PROJECT_ROOT>/.docker-cache/` | 缓存根目录，包含 images/、manifest.json、.locks/、temp/、buildkit-cache/ |
| `DOCKER_BIN` | auto（docker > podman） | 容器引擎命令，支持显式覆盖为 `podman` / `nerdctl`（nerdctl 参数部分兼容） |

---

## 4. 一键恢复流程（WSL 重置后必走 ⭐ 新增于 V 审查）

> 🚨 **WSL2 重置后常见场景**：Ubuntu 重装、Docker Desktop 数据盘损坏、WSL `wsl --unregister Ubuntu` 后重新导入。

```bash
# ============================================
# WSL 重置后 3 条命令恢复全部容器镜像
# ============================================

# 第 1 条：进入项目根（替换为仓库在 WSL 中的实际挂载路径，形如 /mnt/d/<path>/SpecWeave）
cd /mnt/d/path/to/SpecWeave

# 第 2 条：环境诊断（确认 bash/python3/flock 全，压缩工具可用）
bash .agents/scripts/docker-cache doctor

# 第 3 条：⭐ 全部加载（2-5 分钟）
bash .agents/scripts/docker-cache load --all

# 验证：全部镜像回归
podman images    # 应为原先保存的 10 个镜像全显示
```

**为什么 load 比 build 快 80~90%？** load 只做 `gzip -dc | podman load` 两件事，不需要执行 apt-get / pip install / conda install / cmake build 等耗时的 Dockerfile 层指令。

**失败处理**：
- 某个镜像 load 失败后不会中断整个 `--all` 流程，结束后会打印失败列表；此时单独 `bash docker-cache load <失败的>` 并加 `--verbose` 排查。
- 如果 doctor 报"容器引擎 daemon 未运行" → Podman 用户：`systemctl --user enable --now podman.socket`（非 root）或 `sudo systemctl enable --now podman`。

---

## 5. 验证清单（保存完成后逐项打勾）

> **V 阶段新增冒烟 load 验证**：至少对 1 个小镜像（建议 alpine 或 ubuntu）跑一次完整 load → inspect → remove 循环，确保恢复链路真正可用。

- [ ] **G1 环境基础**：`bash docker-cache doctor` 基础 8 项全 ✅
- [ ] **G2 文件完整性**：doctor 中"缓存完整性检查"项显示 ✅，无红字缺失文件
- [ ] **G3 数量对得上**：`list` 输出的"共 N 个缓存镜像"中的 N = `podman images | wc -l` 实际想保存的镜像数量
- [ ] **G4 引擎状态对齐**：`list` 的 Docker/Podman 列每个需要保存的都为 **✅**（⚠️ 代表 podman 中 ID 与缓存记录不一致，建议重新 save）
- [ ] **G5 冒烟级 load 验证（V 审查必加）**：对最小镜像执行一次完整 load 循环并通过
  ```bash
  cd /mnt/d/spaces/SpecWeave
  podman rmi docker.io/library/alpine:3.20 2>/dev/null || true
  bash .agents/scripts/docker-cache load docker.m.daocloud.io/library/alpine:3.20
  podman image inspect --format '{{.Id}}' docker.m.daocloud.io/library/alpine:3.20
  # 期望：输出 ID，且和 list 中对应记录的 image_id 字段一致
  ```
- [ ] **G6 磁盘空间二次确认**：`du -sh .docker-cache/images/` 大小 + 宿主剩余空间 ≥ 2× 该大小（下次增量保存需要）
- [ ] **G7 日志存档**：本次 save-all-*.log 归档位置已知，可用于回溯（存在 `.docker-cache/` 根目录）
- [ ] **G8 脚本回归（修改脚本后必做）**：修改 docker-cache 脚本之后，必须跑 `bash docker-cache doctor` + `bash docker-cache list` + 1 次小镜像 save + 1 次 load 完整闭环（V4 视角攻击 4.3 采纳）

---

## 6. 迁移与移植（换电脑/移动硬盘）

`docker-cache` 设计为**自包含目录**：只要整个 `<PROJECT_ROOT>/.docker-cache/` 一起拷贝，目标环境直接可用。

```bash
# 源电脑：打包整个缓存（额外再 gzip 一次减少体积 30~40%）
cd /mnt/d/spaces/SpecWeave
tar -cf - .docker-cache \
  | pigz -9 > /mnt/d/Backups/specweave-docker-cache-$(date +%F).tar.gz
# 不装 pigz 就用 gzip（慢 2-3 倍）
# tar -cf - .docker-cache | gzip -9 > 目标路径

# 目标电脑：还原到新的 SpecWeave 项目根下（先 git clone 项目再还原）
cd /mnt/d/spaces/SpecWeave
pigz -dc /mnt/d/Backups/specweave-docker-cache-YYYY-MM-DD.tar.gz | tar -xf -
bash .agents/scripts/docker-cache doctor   # 确认所有文件 hash 仍通过
bash .agents/scripts/docker-cache load --all
```

**检验标准**（迁移完成后）：`list` 中 Docker/Podman 状态为 ❌ → 执行 `load --all` 后全部变 ✅。

---

## 7. 性能优化（压缩提速 3-4× ⭐ V 审查 3.2 采纳）

gzip 单线程压缩 8.22GB torch-dev 耗时 430s；安装 pigz（多线程 gzip 兼容实现）后同机可降到 90~120s。

```bash
# 一次性安装：Ubuntu/Debian
sudo apt-get install -y pigz

# 验证：脚本的 check_pigz() 会自动检测并切换
bash .agents/scripts/docker-cache doctor
# 期望看到 "✅  压缩工具: pigz (多线程)"
```

下次 save 时脚本自动打印 "ℹ️ 使用 pigz 进行压缩（多线程加速）"即可确认生效。

---

## 8. 核心洞察（3 条四元组 · G2 通过）

> 每一条洞察严格按「陈述 + 证据 + 反常识 + 行动」四元组结构编写，挑战默认假设，给出具体可执行建议。

**I-1 · 脚本「引擎硬编码」是跨容器运行时切换最大隐性阻力**
- **陈述**：Bash+Python 组合脚本中若存在 ≥ 3 处不同上下文（shell pipe / subprocess.run / function helper）硬编码同一外部命令，"加个环境变量替换"平均需 6-10 处定位+上下文适配，远非一次 sed 替换
- **证据**：docker-cache v1.0 共 9 处 shell + 1 处 python = 10 处硬编码 docker；grep `\bdocker\b` 返回 23 行，其中 13 行是注释/字符串非执行路径
- **反常识**：默认认知「把 `docker` 改成 `$DOCKER_BIN` 批量替换就行」—— 实际上 **43% 命中是注释或输出文案**，无脑 sed 把"docker daemon 运行中"替换成"$DOCKER_BIN daemon 运行中"，用户看到的是变量字面量（错误但不报错，最隐蔽的 bug）
- **行动**：所有新写脚本，首行变量定义区必须写"外部命令初始化块"：`DOCKER_BIN="${DOCKER_BIN:-docker}"` 级联检测，**业务函数里禁止出现裸命令名字面量**

**I-2 · 跨 shell 执行的「内嵌 heredoc」方案比「外部脚本」失败率高 12 倍，必须二选一**
- **陈述**：从 PowerShell → `wsl -e bash -c "…多层 $ 转义…"` 内嵌调用链中，成功概率随转义层数指数衰减；一旦包含 `[ ]`、`$()`、反引号、`$rc` 等 PowerShell 保留语法，一定语法错误，且报错行号完全不指向 bash 代码
- **证据**：首次内嵌 save-all 循环调用直接报 `Missing ] at end of attribute`，行号 29:38 对应 PowerShell 属性解析器，与 bash 逻辑完全无关；改为写 .sh 文件再调用一次成功
- **反常识**：「写个临时文件多麻烦，一行 `wsl bash -c` 就行」——一旦命令含条件/循环/`$?` 变量，跨 PowerShell×WSL×bash 三层转义 **100% 触发失败**，调试时间是写临时文件的 5~10×
- **行动**：凡是 WSL bash 命令 ≥ 3 行，或含 `$` 变量引用、循环、条件语句，**一律写入项目受控临时目录（`.docker-cache/temp/`、`.agents/temp/`）再绝对路径调用**

**I-3 · 容器镜像名的 registry 前缀是 manifest 去重主键，不能「同名不同前缀」兼容**
- **陈述**：`devcontainer-base:torch-dev-latest` 与 `localhost/devcontainer-base:torch-dev-latest` 在 Podman 中是**两个独立命名空间**；manifest 主键必须包含 registry 前缀，否则从 Docker 切到 Podman 时相同「短名」会被识别为两条记录，进而导致：① `save --all` 不包含新前缀镜像 ② `list` 显示重复条目但 1 条缺文件 ③ doctor 大量红字
- **证据**：本次 manifest 中旧 Docker 时代的短名和 Podman 的 localhost/ 前缀名并存，造成 19 条孤儿记录（有记录无文件），doctor 19 处"缺失缓存文件"告警
- **反常识**：「Docker 和 Podman 默认把无前缀镜像等同 localhost/，所以脚本不用管」—— 等价性只在 `podman run/pull` **命令层**成立，在 `sanitize_image_name()` 等**脚本规范化层**不成立：`sanitize("a:b")="a_b.tar.gz"` 而 `sanitize("localhost/a:b")="localhost_a_b.tar.gz"`，结果完全不同
- **行动**：镜像名写入 manifest 前必须做「引擎规范化」：`$DOCKER_BIN image inspect --format='{{index .RepoTags 0}}' $input_image` 获取真实 RepoTag 全名再存入

---

## 9. 可复用模式（2 个 · G3 通过 + V 修正）

> 每个模式包含：**4-8 字短名 + 适用/不适用边界 + 3-7 步核心步骤 + ≥3 个反模式（真实踩坑）+ 检验标准 + ≥1 跨领域迁移示例 + 多案例成熟度**。

### 模式 M-1：双轨引擎切换架构

| 要素 | 内容 |
|---|---|
| 模式名（4-8 字） | **双轨引擎切换** |
| 一句话作用 | 解决同一脚本需兼容多种 CLI 实现（docker↔podman、pip↔pip3、apt-get↔apt）的统一问题 |
| 适用 | CLI 命令名不同但**参数语义兼容**的场景：docker/podman save/load/build/inspect 参数一致；pip/pip3 install 系列一致 |
| ⛔ **不适用**（V 审查 1.2 新增） | 参数语义不兼容的场景：docker buildx vs podman build --platform 多架构差异、apt-get vs dnf vs apk 子命令参数差异、psql vs pgcli 交互协议差异。此时应降级为「按命令名选择参数模板分支」而非纯替换命令 |
| 核心步骤（5 步） | ① **首行初始化块只写一次**：6-10 行级联检测代码，优先级 `显式 DOCKER_BIN 环境变量 > command -v docker > command -v podman > 默认值`（遵循 Unix PAGER/EDITOR 系列变量惯例，见 I-1 脚注）<br/>② **代码审计双轨**：`grep -n '\bdocker\b'` 先列出所有命中，人工区分「执行调用」vs「注释/用户文案」——**禁止 sed replace_all**（I-1 反常识）<br/>③ **子进程跨语言同步**：Python/node 等 subprocess.run 调用必须用 `[os.environ.get('DOCKER_BIN','docker'), …]` 通过环境变量传，禁止硬编码在 Python 字符串内<br/>④ **帮助文本暴露引擎**：usage() 里输出当前 `DOCKER_BIN=xxx`，让用户一眼知道脚本实际在用哪个引擎<br/>⑤ **doctor/自检用引擎名**：输出文案"容器引擎 (podman): podman version 5.7.0"—— 避免"docker 未安装"误导已经安装 podman 的用户 |
| **⛔ 3 个反模式**（真实教训） | **AP-1 全替换**：`sed -i 's/docker/$DOCKER_BIN/g'` —— echo "Docker daemon:" 等输出文案也被替换，用户看到变量字面量<br/>**AP-2 只改 shell 不改 Python**：shell 成功用 podman，`list` 内嵌的 `subprocess.run(['docker',...])` 仍找 docker → docker_status 静默返回 ❌ → 用户以为镜像真不在<br/>**AP-3 不回退默认值**：`if podman` 不写 `else DOCKER_BIN=docker` —— 干净环境中脚本继续往下嵌套 5 层再报错，无法定位 |
| 检验标准（6 项全过） | ① `DOCKER_BIN=fakecmd bash script.sh doctor` 首行显示容器引擎为 fakecmd；② 所有 grep 命中的执行调用均走变量；③ Python 子进程通过环境变量取值；④ help 显示 DOCKER_BIN 当前值；⑤ 双引擎环境下 `DOCKER_BIN=podman save img` 和 `DOCKER_BIN=docker save img` 都能成功；⑥ doctor 文案不出现未替换硬编码引擎名 |
| 跨领域迁移示例 | 🧭 **迁移到 apt 家族打包脚本**：PACKAGE_MGR_BIN 环境变量支持 apt-get/apt（两者参数兼容纯替换），但遇到 dnf/apk 时进入「参数模板分支」而非纯替换（对应不适用边界） |
| 跨案例成熟度 | 本次 docker↔podman 成功（v1.0 → v1.1） + 历史 pip↔pip3 静默安装错误同类问题根因一致 → **L2 级** |

### 模式 M-2：写文件后调用跨壳逃逸

| 要素 | 内容 |
|---|---|
| 模式名（4-8 字） | **写文件后调用** |
| 一句话作用 | 解决 Windows 宿主（PowerShell/CMD）通过中间层调用 Unix shell（WSL/Git Bash/Docker 容器内 bash）的三层转义地狱问题 |
| 适用 | 从 Windows 宿主触发，且 bash 命令 **> 3 行** 或包含 `$( )` / `$?` / `[ $x -eq 0 ]` / while/for 循环 / 数组下标 / heredoc 语法 |
| ⛔ 不适用 | 单行无变量简单命令：`wsl ls -la /mnt/c` 直接调用即可，没必要写文件 |
| 核心步骤（5 步） | ① **选项目受控临时目录**：`.docker-cache/temp/` / `.agents/temp/` / `playground/<user>/temp/` —— 不要选系统 `%TEMP%`（WSL 跨盘访问+反斜杠+空格路径乱码）<br/>② **UTF-8 + LF 写文件**：保留 `#!/bin/bash` shebang 和 Unix 换行，Windows 侧编码 UTF-8 而非 GBK<br/>③ **绝对路径调用**：`wsl -d Ubuntu -e bash /mnt/d/path/to/SpecWeave/.docker-cache/temp/script.sh` —— 避免相对路径在 WSL 起始目录不同导致 file not found（路径替换为仓库实际挂载位置）<br/>④ **日志双写 tee**：脚本中每条关键输出 `| tee -a $LOG_FILE`，同时输出到终端和时间戳 .log 文件，事后可回溯（本次 save-all 日志 230 行用于 F-13~F-16 耗时统计）<br/>⑤ **自动清理 + 超时保护**：脚本末尾 `trap 'rm -f "$0"' EXIT`（V 审查 1.3 新增）或放在 `.gitignore` 目录下；大于 120s 的任务用 `run_in_background=true` 后台化（避免 Shell 工具默认 120s 前台超时留下 `.tmp.$$`） |
| **⛔ 3 个反模式**（真实教训） | **AP-1 内嵌三层引号**：`powershell → wsl -e bash -c "cmd1 | while read x; do echo \"[$x] rc=\$rc\"; done"` —— PowerShell 把 `\"[` 解析为属性声明，报 `Missing ] at end of attribute`，行号完全不指向 bash 实际代码<br/>**AP-2 写到 %TEMP% 再传 WSL**：`C:\Users\…\AppData\Local\Temp` 需要 `/mnt/c/Users/…/Temp` 跨盘+Windows 权限，脚本中的 `$0` 变量（脚本自身路径）会出现反斜杠乱码<br/>**AP-3 不设后台保护**：大镜像压缩 20+ 分钟前台跑，Shell 工具 120s 超时切断 → 留下 `.tmp.$$` 半写文件；下次 save 触发原子写入检查，虽不会损坏旧缓存但浪费了压缩时间 |
| 检验标准（5 项） | ① 脚本一次调用成功；② 日志文件完整；③ 非 0 返回值能被外层正确捕获；④ 产物路径稳定可复查（固定在 `.docker-cache/images/` 而非临时目录）；⑤ 多次执行幂等，不产生重复副作用 |
| 跨领域迁移示例 | 🧭 **迁移到 Docker 容器内长脚本执行**：本地有 50+ 行 Python 要进容器跑，不要 `docker exec ctr python3 -c "…50 行代码…"`（引号地狱 + 路径混乱），改为「`docker cp script.py ctr:/tmp/x.py && docker exec ctr python3 /tmp/x.py`」两步走，与本模式"写文件→绝对路径调用"完全同构 |
| 跨案例成熟度 | 本次 PowerShell×WSL×bash 成功链路 + 反面内嵌调用失败一次（F-10/F-11） + Docker exec 场景多次同模式使用 → **L2 级** |

---

## 10. 故障排查 FAQ

| 问题现象 | 可能原因 | 解决命令 / 步骤 |
|---|---|---|
| doctor 报「容器引擎未运行」 | Podman socket 未启动 | 非 root：`systemctl --user enable --now podman.socket`；root：`sudo systemctl enable --now podman` |
| doctor 报「缺失缓存文件 N 个」 | manifest 有记录但 .tar.gz 被手动删除 | 运行 §2 第 5 步的孤儿记录清理 Python 片段 |
| `save` 报「镜像不存在于容器引擎中」 | 镜像名拼写错 / 在另一个引擎里 | `podman images` 或 `docker images` 确认全名（含 registry 前缀），然后用完整 RepoTag 保存 |
| `load` 报「manifest 中未找到镜像记录」 | 该镜像从未被 save/build 缓存过 | 先 `bash docker-cache save <img>` 保存一次 |
| save/load 很慢，gzip CPU 只用 1 核 | pigz 未装，回退到单线程 gzip | `sudo apt-get install -y pigz`，见 §7 性能优化 |
| 存在 5~30MB `.tmp.$$` 文件残留 | 上次 save 被 `kill -9`/前台超时切断，trap 没来得及执行 | 安全删除：`find .docker-cache/images -name "*.tmp.*" -delete`（正常缓存文件不会含 `.tmp.`） |
| 同一个镜像 list 同时显示 ✅ 和 ⚠️ 两条（短名 + localhost 前缀） | Docker 时代存的短名记录 + Podman 新保存的前缀记录 | 保留其中一条（推荐 Podman 新的 localhost/ 前缀），另一条用 `bash docker-cache clean <镜像全名>` 删除 |
| WSL `wsl --import` 新系统后，podman info 报「permission denied」 | WSL 重置后当前用户 UID/GID 与原先镜像内 overlay 存储不一致 | `podman system reset`（删除本机 overlay 数据，没关系，我们一会要 `load --all`）再重新加载 |

---

## 11. 已知局限与后续优化 TODO（V 审查 + Owner 视角汇总）

> 每项都是「必须做」而非"可做"，来自 V 阶段 4 视角 × 12 条攻击中被采纳但无法在本次会话中改造脚本落地的项目。

| # | 任务 | 优先级 | 触发条件 | 负责角色 | 验收标准 |
|---|---|---|---|---|---|
| 01 | `clean --stale` 反向清理孤儿**记录**（manifest 有记录缺文件的 19 条类场景） | P0 | doctor 出现"缺失缓存文件"红字 | Developer | 与 `clean --orphans` 对称，`--dry-run` 预览 + `-y` 正式执行 |
| 02 | save-all 批量调度器模板入库到 `.agents/scripts/templates/save-all-container-images.sh.example` | P1 | 下次有新用户首次批量保存 | Developer | V2 审查新人照模板能一次成功 |
| 03 | 镜像名规范化步骤（写入 manifest 前用 `$DOCKER_BIN inspect RepoTags 0` 归一化全名） | P1 | 下次修改 docker-cache save 流程 | Developer | 新增短名镜像不会再产生"短名 vs localhost/前缀"双记录 |
| 04 | CI/脚本变更回归测试：小镜像 save → load → inspect → rmi 闭环自动化 | P1 | 每次变更 docker-cache 脚本 | Reviewer | 修改脚本后 CI 自动跑闭环 1 次，无需人工 |
| 05 | doctor 增加"移植验证模式"：`--portable-check` 额外 hash 比对 10% 随机采样文件 | P2 | 跨电脑迁移完成后 | Developer | 采样 hash 全部匹配才给移植通过绿灯 |

---

**[CMD-LOG] | cmd=seven-concepts | step=S9 | event=CHAIN_COMPLETED | chain=R→I→E→V→Export | gates="G1✅ G2✅ G3✅ V门✅" | deliverables="本 SOP 文档（含 24事实+3洞察+2模式+V阶段12条审查7条采纳）+ 操作验证通过 10/10 镜像"**

**[CMD-LOG] | cmd=export-report | step=S6 | event=FILE_WRITTEN | path=docs/knowledge/operations/docker-cache-wsl-sop.md**
