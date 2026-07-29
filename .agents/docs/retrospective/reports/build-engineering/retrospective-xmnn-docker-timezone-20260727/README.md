---
id: "retrospective-xmnn-docker-timezone-20260727"
title: "XMNN Docker 镜像时区缺失修复复盘"
type: "task"
date: "2026-07-27"
source: "external/chaos/xmtools Docker timezone fix"
status: "completed"
maturity: "L1"
---

# XMNN Docker 镜像时区缺失修复复盘

## 执行摘要

用户报告 `xmnn:1.2.1-alpha` 运行时镜像时区不正确（默认为 UTC，中国用户期望 CST/UTC+8）。问题根因为 Dockerfile 模板中遗漏了时区配置。修复采用三层保障方案（tzdata 安装 + /etc/localtime 符号链接 + TZ 环境变量），同步修复了 dev-llvm22 构建镜像的相同时区问题，并萃取了 [docker-timezone-configuration](../../../patterns/code-patterns/docker-timezone-configuration.md) 可复用模式。

**关键数据**：
- 修改文件：2 个 Dockerfile（[runtime/Dockerfile](../../../../../../external/chaos/xmtools/docker/runtime/Dockerfile)、[dev-llvm22/Dockerfile](../../../../../../external/chaos/xmtools/docker/dev-llvm22/Dockerfile)）
- 新建模式：1 个（docker-timezone-configuration，L1）
- 影响范围：3 个镜像（runtime ✅、dev ✅、serve 自动继承 runtime 无需修复）
- 构建验证：runtime 镜像重建成功，ALL CHECKS PASSED

---

## 一、事实还原（S1）

### 1.1 问题发现

用户在使用 `xmnn:1.2.1-alpha` 镜像时发现容器内时间为 UTC（差 8 小时），报告"时区不对"。

### 1.2 根因确认

检查三个 Dockerfile：
- `runtime/Dockerfile`：基于 `ubuntu:26.04`，安装了系统依赖但未安装 `tzdata`，未设置 `/etc/localtime` 和 `TZ` 环境变量 → 默认 UTC
- `dev-llvm22/Dockerfile`：同样基于 `ubuntu:26.04`，存在相同问题
- `serve/Dockerfile`：基于 `xmnn:1.2.1-alpha`，修复 runtime 后自动继承时区

### 1.3 修复过程

| 步骤 | 操作 | 结果 |
|------|------|------|
| F1 | runtime/Dockerfile Step 1 添加 tzdata + ln -sf localtime + echo timezone | 系统时区配置 |
| F2 | runtime/Dockerfile Step 6 添加 ENV TZ=Asia/Shanghai | 环境变量配置 |
| F3 | 重新构建 runtime 镜像 | 构建成功，所有验证通过 |
| F4 | dev-llvm22/Dockerfile 同步修复 | 构建镜像时区一致 |
| F5 | 创建 docker-timezone-configuration 模式 | 可复用知识沉淀 |

### 1.4 变更内容

**runtime/Dockerfile**：
- Step 1 apt 依赖列表新增 `tzdata`
- Step 1 安装后追加 `ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo "Asia/Shanghai" > /etc/timezone`
- Step 6 环境变量新增 `ENV TZ=Asia/Shanghai`

**dev-llvm22/Dockerfile**：
- 同样的三处修复，保持与 runtime 一致

---

## 二、过程分析（S2）

### 2.1 为什么时区配置被遗漏？

**5-Whys 分析**：

1. **Why 时区不对？** Dockerfile 中没有安装 tzdata 和配置时区
2. **Why 没配置？** Dockerfile 模板创建时关注焦点在构建工具链（LLVM/Clang/Conda/Python）和 XMNN 运行时依赖，系统级本地化配置（时区/语言/编码）未纳入检查清单
3. **Why 检查清单没覆盖？** Docker 模板验证关注功能正确性（import tvm、tvm.build、ldconfig），未包含系统环境检查（时区、locale、编码）
4. **Why 系统环境检查缺失？** 之前所有 Docker 构建经验中时区问题从未成为阻塞项——开发环境多为 UTC 友好（CI/CD、日志聚合通常用 UTC），未遇到用户直接报告时间问题
5. **根本原因**：Dockerfile 基础配置清单不完整，缺少"系统本地化配置"检查项；验证脚本只验证 XMNN 功能，不验证系统环境

### 2.2 问题扩散范围

三个 Dockerfile 中两个需要修复（runtime 和 dev），serve 基于 runtime 自动继承。这说明：
- 基础镜像（ubuntu:26.04）直接使用的 Dockerfile 都需要显式配置时区
- 基于已配置镜像的子镜像自动继承，无需重复配置
- 这符合 Docker 层叠继承的设计原则

### 2.3 修复方案评估

采用了**三层保障**方案而非单一方式：

| 层次 | 方法 | 覆盖场景 |
|------|------|---------|
| 系统层 | tzdata + /etc/localtime 符号链接 + /etc/timezone | C 标准库 time()、系统命令 date、不读取 TZ 变量的程序 |
| 环境变量层 | ENV TZ=Asia/Shanghai | Python datetime、Java user.timezone、大多数现代应用 |
| 验证层 | （建议）验证脚本检查时区 | 防止未来修改意外破坏 |

---

## 三、洞察提炼（S3）

### 3.1 核心洞察

**洞察 1：Docker 基础镜像的"隐式默认"是常见遗漏源**

Ubuntu 基础镜像默认为 UTC 时区、C locale、POSIX 编码——这些是"能工作但不正确"的隐式默认。当用户在中国环境使用时，UTC 时区会导致日志时间差 8 小时、定时任务在错误时间触发、业务时间逻辑出错。这类"不报错但结果不对"的配置问题比编译错误更难发现。

**洞察 2：验证脚本的覆盖范围决定了问题的发现时机**

当前 [verify_xmnn.py](../../../../../../external/chaos/xmtools/docker/runtime/verify_xmnn.py) 只验证 XMNN 功能（import、tvm.build、API 检查），不验证系统环境（时区、locale、文件编码）。如果验证脚本包含时区检查，问题在构建时就能发现，而非等到用户使用时报错。

**洞察 3：镜像继承关系可以简化配置但需要显式认知**

serve/Dockerfile 基于 `xmnn:1.2.1-alpha`，修复 runtime 后自动继承时区——这是正确的。但如果未来有人重新创建一个不基于 xmnn:1.2.1-alpha 的新 Dockerfile（比如新的微服务镜像），时区问题会再次出现。模式的价值在于将隐性知识（"需要配时区"）变为显性检查项。

### 3.2 可复用模式

| 模式 | 类型 | 状态 |
|------|------|------|
| [docker-timezone-configuration](../../../patterns/code-patterns/docker-timezone-configuration.md) | 代码模式 | ✅ 新建（L1, validation_count=1） |

### 3.3 反模式汇总

1. **只设 TZ 环境变量不装 tzdata**——缺少时区数据库文件
2. **装 tzdata 不设 /etc/localtime**——noninteractive 模式下默认 UTC
3. **用 dpkg-reconfigure 设置时区**——noninteractive 下不可靠
4. **依赖 docker run -e TZ 传递**——运行时设置不持久化
5. **挂载宿主机 /etc/localtime**——不可移植

---

## 四、改进行动项（S4）

### 高优先级（P0）

| 行动项 | 验收标准 | 责任方 |
|--------|---------|--------|
| 在 verify_xmnn.py 中添加时区检查（验证 TZ 环境变量和 localtime） | 构建时如果时区不正确则验证失败 | developer |

### 中优先级（P1）

| 行动项 | 验收标准 | 责任方 |
|--------|---------|--------|
| Dockerfile 创建/审查清单中增加"系统本地化配置"项（时区、locale、编码） | 新建 Dockerfile 时检查清单包含 tzdata + TZ + localtime | reviewer |
| 检查是否需要配置 locale（如 zh_CN.UTF-8） | 确认中文文件名/输出是否正常 | developer |

### 低优先级（P2）

| 行动项 | 验收标准 | 责任方 |
|--------|---------|--------|
| 重新构建 dev-llvm22 镜像使时区配置生效 | dev 容器中 date 显示 CST | developer |

---

## 五、经验沉淀

### 与已有模式的关联

本次萃取的 [docker-timezone-configuration](../../../patterns/code-patterns/docker-timezone-configuration.md) 模式与以下模式形成 Docker 配置模式族：
- [dockerfile-python-code-safe-embedding](../../../patterns/code-patterns/dockerfile-python-code-safe-embedding.md)：Dockerfile 中嵌入代码的安全实践
- [conda-custom-channels-mirror](../../../patterns/code-patterns/conda-custom-channels-mirror.md)：Conda 国内镜像配置
- [docker-buildtime-vs-runtime-config](../../../patterns/code-patterns/docker-buildtime-vs-runtime-config.md)：构建时与运行时配置分离

### 项目记忆更新

已向 project_memory.md 添加硬约束：Docker 镜像必须在 Step 1 配置 Asia/Shanghai 时区（三层保障）。
