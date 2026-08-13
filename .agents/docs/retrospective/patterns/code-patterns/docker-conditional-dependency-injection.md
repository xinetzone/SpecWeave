---
id: "docker-conditional-dependency-injection"
title: "Docker 声明式依赖条件注入模式"
type: "code-pattern"
date: "2026-08-07"
maturity: "L1-draft"
source: "chaos/docker/hub/conda.Containerfile (2026-08-07)"
related_patterns:
  - "configurable-by-default-principle"
  - "dockerfile-runtime-logical-layering"
tags: ["docker", "dockerfile", "environment.yml", "conda", "conditional-injection", "configurable"]
validation_count: 1
reuse_count: 0
---

# Docker 声明式依赖条件注入模式

## 触发场景

- 需要构建一个通用容器镜像，但不同项目/场景的依赖各不相同
- 希望用一份 Dockerfile 服务多个项目，避免为每个项目复制一份 Dockerfile
- 依赖变更时希望只改声明文件（如 environment.yml），不触碰 Dockerfile
- 镜像构建时按需注入外部声明的依赖

**不适用于**：
- 依赖完全固定、单用途的镜像（直接写死在 Dockerfile 更清晰）
- 需要在构建时注入机密/密钥的场景（应走 secret mount 而非环境文件）

## 核心做法

### 1. 约定外部声明文件位置

```dockerfile
# 约定项目根目录放置 environment.yml，构建时挂载到 /workspace
COPY . /workspace
```

### 2. 条件判断 + 声明式注入

```dockerfile
RUN if [ -f /workspace/environment.yml ]; then \
        conda env update -n base -f /workspace/environment.yml; \
    fi
```

- 用 `if [ -f ... ]` 判断声明文件是否存在，不存在则静默跳过
- 声明文件存在时，按声明内容更新环境，实现"有配置则注入，无配置则用默认"

### 3. 保持构建幂等

```dockerfile
conda env update -n base -f /workspace/environment.yml
# 用 update 而非 create，重复执行结果一致，天然幂等
```

## 反模式（不要这么做）

### ❌ 反模式1：在 Dockerfile 内硬编码依赖

```dockerfile
RUN conda install -y numpy scipy pandas
# 每个项目都要改 Dockerfile，Dockerfile 无法复用
```

### ❌ 反模式2：条件判断导致构建失败

```dockerfile
RUN conda env update -n base -f /workspace/environment.yml
# 若文件不存在直接失败；应先用 if [ -f ] 判断，缺失时优雅跳过
```

### ❌ 反模式3：用 create 而非 update

```dockerfile
RUN conda env create -n base -f /workspace/environment.yml
# create 在环境已存在时报错，不可重复构建；update 天然幂等
```

## 检验标准

做完之后怎么知道做对了？

1. **有声明文件**：依赖按 environment.yml 正确注入
2. **无声明文件**：构建不因文件缺失而失败，使用默认环境
3. **可复用**：同一 Dockerfile 服务多个项目，只换声明文件
4. **幂等**：同一声明文件重复构建结果一致

## 迁移示例

| 语言/工具 | 声明文件 | 注入命令 |
|----------|---------|---------|
| conda | environment.yml | `conda env update -n base -f environment.yml` |
| pip | requirements.txt | `pip install -r requirements.txt` |
| npm | package.json | `npm install` |
| apt | packages.txt | `apt-get install -y $(cat packages.txt)` |

### 跨领域迁移
- **CI 配置**：按环境变量条件选择安装分支，声明式配置驱动
- **脚手架生成**：根据模板配置文件条件生成不同结构
- **HashiCorp 配置**：按 `ENV` 变量选择不同配置块，实现单配置多环境

## 与其他模式的关系

| 关联模式 | 关系类型 | 关系说明 |
|---------|---------|---------|
| [configurable-by-default-principle.md](configurable-by-default-principle.md) | 同源 | "可配置性默认原则"在 Docker 依赖注入侧的具体化 |
| [dockerfile-runtime-logical-layering.md](dockerfile-runtime-logical-layering.md) | 互补 | 依赖注入层应放在层序中合适位置以优化缓存 |

## 待验证场景

本模式目前为 L1-draft（单项目验证），建议在以下场景验证：
1. pip/requirements.txt 的条件注入变体
2. 多环境文件（dev/prod）切换策略
3. 构建参数（--build-arg）与声明文件优先级冲突处理