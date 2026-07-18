---
id: "release-gate-automated-verification"
title: "发布门禁自动化验证模式"
type: "process-pattern"
date: 2026-07-18
maturity: "L1 实验性"
maturity_note: "单案例验证（XMNN Runtime 镜像导出 10 项门禁），待第二个独立案例验证后升级 L2"
source: "../../reports/task-reports/retrospective-xmnn-export-entrypoint-fix-20260718/README.md"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/process-patterns/release-gate-automated-verification.toml"
related_patterns:
  - "docker-entrypoint-two-step-reset.md"
tags: ["release", "gate", "verify", "docker", "export", "automation", "checklist", "ci"]
validation_count: 1
reuse_count: 0
---

# 发布门禁自动化验证模式

## 触发场景

- 软件发布流程的最后一步——导出产物（镜像/包/二进制）后需验证完整性
- 发布流程中有多个手动检查项，容易遗漏
- 发布缺陷（如 ENTRYPOINT 错误）在之前版本中已存在但未被发现
- 需要确保每次发布的产物质量一致

**识别信号**：
- 发布后用户反馈"不能用"且原因是可自动检测的配置问题
- 每次发布需要手动执行多个检查步骤
- 发布 Checklist 存在但无人执行或执行不完整
- 不同人执行发布，结果不一致

**不适用场景**：
- 发布流程极简单（单文件拷贝），无需自动化验证
- 所有验证已集成到 CI/CD 流水线中
- 产物是中间产物，不直接交付给用户

## 问题背景

### 为什么手动验证不可靠

1. **依赖记忆**：每次发布需要记住所有检查项，容易遗漏
2. **不可重复**：不同人/不同时间执行结果可能不同
3. **隐性缺陷积累**：配置错误（如 ENTRYPOINT）在多次发布中持续存在，但用户用 workaround 绕过
4. **验证滞后**：缺陷在发布后数小时甚至数天才被发现

### 核心原则

```
门禁必须从最终产物验证（docker load tar.gz），而非本地缓存
原因：本地 Docker 缓存可能与导出产物不一致
```

## 核心步骤

### 步骤1：设计门禁检查项

按以下维度分类：

| 维度 | 检查内容 | 示例 |
|------|---------|------|
| 配置完整性 | ENTRYPOINT、CMD、环境变量 | `docker inspect` |
| 回归测试 | 之前失败的用例 | `docker run <img> bash -c '...'` |
| 内容完整性 | 关键文件版本/哈希 | `sha256sum libtvm.so` |
| 功能冒烟 | 核心 API 可调用 | `python -c "import xmnn"` |
| 符号可见性 | 动态库符号表 | `readelf -sW libtvm.so` |

### 步骤2：编写门禁脚本

```bash
#!/bin/bash
set -uo pipefail

TAR="$1"
PASS=0; FAIL=0
ok()  { echo "PASS: $1"; PASS=$((PASS+1)); }
bad() { echo "FAIL: $1"; FAIL=$((FAIL+1)); }

# 1. 从最终产物加载
docker load -i "$TAR"
docker tag <loaded-image> verify:latest

# 2. 配置检查
EP=$(docker inspect verify:latest --format '{{json .Config.Entrypoint}}')
[ "$EP" = "null" ] && ok "ENTRYPOINT" || bad "ENTRYPOINT: $EP"

# 3. 回归测试
docker run --rm verify:latest bash -c 'echo OK' | grep -q OK \
  && ok "regression" || bad "regression"

# 4. 内容完整性
docker run --rm verify:latest bash -c 'sha256sum /path/to/key/file'

# 5. 功能冒烟
docker run --rm verify:latest bash -c 'python -c "import core; print(\"OK\")"'

# 6. 输出报告
echo "RESULT: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ]
```

### 步骤3：集成到导出流程

```bash
# 导出脚本末尾
./do_export.sh
./verify_final_image.sh  # 门禁验证
if [ $? -ne 0 ]; then
    echo "ERROR: 门禁未通过，产物不可发布"
    exit 1
fi
```

### 步骤4：维护门禁项

- 每次发现新缺陷类型 → 增加对应检查项
- 每次修复 → 增加回归测试用例
- 定期审查检查项是否仍然有效

## 反模式（不要这么做）

### ❌ 反模式1：只验证本地 Docker 缓存中的镜像

- **错误**：`docker inspect xmnn-runtime:latest`（本地缓存）
- **后果**：本地缓存可能与 `docker save` 导出的 tar.gz 不一致
- **正确做法**：先 `docker load -i tar.gz`，再验证加载后的镜像

### ❌ 反模式2：手动逐项检查

- **错误**：每次发布手动执行 `docker run`、`docker inspect` 等
- **后果**：遗漏检查项，不同人执行结果不一致
- **正确做法**：编写脚本自动化执行，输出 PASS/FAIL 报告

### ❌ 反模式3：门禁脚本放在不同仓库

- **错误**：验证脚本与导出脚本不在同一目录
- **后果**：新维护者找不到门禁脚本，门禁形同虚设
- **正确做法**：门禁脚本与导出脚本放在同一目录，导出完成后自动调用

### ❌ 反模式4：门禁失败时继续发布

- **错误**：门禁脚本输出 FAIL 但流程继续
- **后果**：有缺陷的产物被发布给用户
- **正确做法**：门禁失败时脚本返回非零退出码，阻断发布流程

## 检验标准

- [ ] 门禁脚本从最终产物（tar.gz/安装包）加载验证
- [ ] 门禁脚本可独立运行，不依赖特定环境变量
- [ ] 检查项覆盖配置、回归、内容、功能、符号五个维度
- [ ] 门禁失败时返回非零退出码
- [ ] 门禁脚本与导出脚本在同一目录

## 迁移示例

### 场景1：XMNN Runtime 镜像导出（本项目，源案例）

- **问题**：ENTRYPOINT 错误在之前版本中已存在但未被发现
- **实现**：`verify_final_image.sh`（88 行），10 项检查，从 tar.gz 加载验证
- **结果**：10/10 通过，每次导出后自动运行

### 场景2：npm 包发布门禁（推断，待验证）

- **类似问题**：发布 npm 包后 `package.json` 的 `main` 字段指向不存在的文件
- **对应策略**：`npm pack` → 解压 → 验证 `package.json` 字段 → 验证入口文件存在
- **差异**：npm 生态有 `npm publish --dry-run`，但不会验证产物内容

### 场景3：二进制发布门禁（推断，待验证）

- **类似问题**：编译产物缺少动态库依赖，在开发机可运行但在用户机器上失败
- **对应策略**：`ldd` 检查动态库依赖 → 在干净 Docker 镜像中验证可执行

## Changelog

- **2026-07-18** (v1.0.0): 初始版本，从 XMNN Runtime 镜像导出修复复盘萃取，单案例验证，标记 L1 实验性