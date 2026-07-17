---
title: "npu_tvm docker/ 目录中度重构设计"
date: "2026-07-17"
status: "draft-for-review"
scope: "design"
project: "SpecWeave / external/xmhub/npu_tvm"
authors:
  - "TRAE"
tags:
  - docker
  - refactor
  - repository-structure
  - compatibility
---

# npu_tvm docker/ 目录中度重构设计

## 1. 背景

`external/xmhub/npu_tvm/docker/` 当前同时承载两套不同性质的内容：

- upstream 历史 TVM Docker/CI 基础设施
- 本轮新增的本地开发与 Conda/Compose 工作流

两套内容平铺在同一层，导致以下问题：

- 新人难以快速区分“CI 基础设施”和“本地开发入口”
- 新增文档、脚本、compose 配置缺少统一入口
- `README-old.md`、`README.conda.md`、`QUICKSTART.md`、`validated-matrix.md` 并列存在，但没有清晰导航
- 后续继续扩展本地开发能力时，根目录会继续膨胀

同时，该目录又被历史 CI/Jenkins 逻辑直接引用，无法进行激进重排。

因此，本设计目标不是重写整个 `docker/` 体系，而是在不破坏 upstream 兼容性的前提下，对“本地开发体系”做边界清晰的中度重构。

## 2. 设计目标

本次重构需要同时满足以下目标：

1. 明确区分 upstream CI 体系与本地开发体系
2. 降低 `docker/` 根目录的认知负担
3. 保持现有常用命令入口兼容
4. 控制改动范围，避免误伤历史 Jenkins/CI 路径
5. 为后续新增本地开发脚本和文档预留清晰落点

## 3. 非目标

本次重构不包含以下事项：

- 不系统性重排所有 `Dockerfile.ci_*` 和 `Dockerfile.demo_*`
- 不修改历史 Jenkins 生成逻辑
- 不改造 upstream `build.sh`、`bash.sh`、`dev_common.sh` 的设计
- 不在本次顺手完成板端文档或 CI 流水线重写
- 不对 `install/`、`python/`、`utils/` 做结构调整

## 4. 现状判断

### 4.1 应保留原位的内容

以下内容属于 upstream 历史基础设施，应保持原位：

- `Dockerfile.ci_*`
- `Dockerfile.demo_*`
- `build.sh`
- `bash.sh`
- `dev_common.sh`
- `install/`
- `python/`
- `utils/`
- `with_the_same_user`

保留原因：

- 已存在外部直接引用
- 与 Jenkins/CI 生成模板强耦合
- 本轮问题不在这部分内容本身，而在新增本地开发内容的平铺

### 4.2 应重构的内容

以下内容属于本轮新增的本地开发体系，适合一起收束：

- `Dockerfile.conda`
- `build_conda.sh`
- `run_conda.sh`
- `verify-tvm.sh`
- `test_build.sh`
- `condarc`
- `pip.conf`
- `compose.sh`
- `docker-compose.yml`
- `start-jupyter.sh`
- `start-rpc-server.sh`
- `start-rpc-tracker.sh`
- `.env.example`
- `README.conda.md`
- `QUICKSTART.md`
- `validated-matrix.md`
- `local-cache-proxy-config.md`
- `README-old.md`

## 5. 方案对比

### 方案 A：保守整理

做法：

- 不移动文件
- 只补总入口 README 和文档索引
- 将旧文档标记为 legacy

优点：

- 风险最低
- 基本不需要修引用

缺点：

- 目录物理结构不改善
- 根层仍然混杂
- 难以长期承接更多本地开发内容

### 方案 B：中度重构

做法：

- 仅迁移本地开发体系
- 保留 upstream CI 体系在根目录
- 在根目录保留兼容脚本与兼容文档入口

优点：

- 结构清晰
- 风险可控
- 旧命令可兼容
- 长期可维护性更好

缺点：

- 需要同步修正相对路径与文档引用
- 需要保留少量兼容壳

### 方案 C：激进重排

做法：

- 对整个 `docker/` 目录重新分区
- 大量移动 CI/demo/install 相关文件

优点：

- 最终结构最整洁

缺点：

- 影响面过大
- 高概率破坏历史引用
- 超出本轮可控范围

## 6. 选型结论

选择 **方案 B：中度重构**。

理由：

- 它精准解决了当前“本地开发体系与历史基础设施混层”的问题
- 它不要求触碰高风险 upstream 路径
- 它允许保留根目录兼容入口，避免已有工作流立即失效
- 它能为后续扩展本地开发体系提供长期稳定的目录落点

## 7. 目标结构

目标结构如下：

```text
docker/
  Dockerfile.ci_*
  Dockerfile.demo_*
  build.sh
  bash.sh
  dev_common.sh
  install/
  python/
  utils/
  with_the_same_user

  legacy/
    README-old.md

  local/
    conda/
      Dockerfile
      build.sh
      run.sh
      verify-tvm.sh
      test_build.sh
      condarc
      pip.conf
    compose/
      compose.sh
      docker-compose.yml
      start-jupyter.sh
      start-rpc-server.sh
      start-rpc-tracker.sh
      .env.example
    docs/
      README.md
      QUICKSTART.md
      validated-matrix.md
      local-cache-proxy-config.md

  build_conda.sh
  run_conda.sh
  compose.sh
  README.conda.md
  QUICKSTART.md
```

说明：

- `legacy/` 用于显式隔离历史说明文档
- `local/conda/` 用于单容器与镜像构建入口
- `local/compose/` 用于本地开发编排与运行脚本
- `local/docs/` 用于本地开发文档集合
- 根目录保留兼容入口，避免已有使用方式断裂

## 8. 文件迁移映射

### 8.1 Conda 相关

- `docker/Dockerfile.conda` -> `docker/local/conda/Dockerfile`
- `docker/build_conda.sh` -> `docker/local/conda/build.sh`
- `docker/run_conda.sh` -> `docker/local/conda/run.sh`
- `docker/verify-tvm.sh` -> `docker/local/conda/verify-tvm.sh`
- `docker/test_build.sh` -> `docker/local/conda/test_build.sh`
- `docker/condarc` -> `docker/local/conda/condarc`
- `docker/pip.conf` -> `docker/local/conda/pip.conf`

### 8.2 Compose 相关

- `docker/compose.sh` -> `docker/local/compose/compose.sh`
- `docker/docker-compose.yml` -> `docker/local/compose/docker-compose.yml`
- `docker/start-jupyter.sh` -> `docker/local/compose/start-jupyter.sh`
- `docker/start-rpc-server.sh` -> `docker/local/compose/start-rpc-server.sh`
- `docker/start-rpc-tracker.sh` -> `docker/local/compose/start-rpc-tracker.sh`
- `docker/.env.example` -> `docker/local/compose/.env.example`

### 8.3 文档相关

- `docker/README.conda.md` -> `docker/local/docs/README.md`
- `docker/QUICKSTART.md` -> `docker/local/docs/QUICKSTART.md`
- `docker/validated-matrix.md` -> `docker/local/docs/validated-matrix.md`
- `docker/local-cache-proxy-config.md` -> `docker/local/docs/local-cache-proxy-config.md`
- `docker/README-old.md` -> `docker/legacy/README-old.md`

## 9. 兼容策略

### 9.1 根层兼容脚本

以下旧路径仍保留，但仅作为薄封装：

- `docker/build_conda.sh`
- `docker/run_conda.sh`
- `docker/compose.sh`

行为：

- 根脚本只负责将参数透传到新路径脚本
- 对外命令保持不变
- 内部实现以 `local/` 目录为准

### 9.2 根层兼容文档

以下文档继续保留，但只承担“入口跳转”职责：

- `docker/README.conda.md`
- `docker/QUICKSTART.md`

行为：

- 提供一句说明
- 指向 `docker/local/docs/` 下的新正式文档

### 9.3 引用修复范围

需要修复的主要是新增本地开发体系内部的相对路径，包括：

- `docker-compose.yml` 中的 `dockerfile` 路径
- 启动脚本路径
- 文档中的命令示例与链接
- `.dockerignore` 中针对本地开发体系的白名单规则

不应修改的引用包括：

- Jenkins 相关对 `docker/build.sh`、`docker/bash.sh` 的引用
- 历史 CI 逻辑中对 `Dockerfile.ci_*` 的约定

## 10. 实施步骤

建议按以下顺序实施：

1. 创建 `legacy/`、`local/conda/`、`local/compose/`、`local/docs/`
2. 移动本地开发体系文件到新位置
3. 在根目录创建兼容脚本
4. 在根目录创建兼容文档入口
5. 修复 `docker-compose.yml` 与脚本中的相对路径
6. 修复 `.dockerignore`
7. 回归检查旧入口命令是否仍可用
8. 回归检查文档链接是否仍可用

## 11. 测试策略

本次重构以“结构不变更行为”为原则，验证重点如下：

### 11.1 路径兼容验证

- `bash docker/build_conda.sh --help` 正常
- `bash docker/run_conda.sh --help` 正常
- `bash docker/compose.sh help` 正常

### 11.2 文档入口验证

- 根目录文档能正确跳转到新文档
- 新文档内所有相对链接有效

### 11.3 Compose 验证

- compose 配置能正确找到 `Dockerfile`
- compose 启动脚本路径有效
- `.env.example` 能被正确复制与读取

### 11.4 非回归验证

- `docker/build.sh`、`docker/bash.sh` 仍在原路径
- `Dockerfile.ci_*` 与 `Dockerfile.demo_*` 未被移动

## 12. 风险与缓解

### 风险一：相对路径失效

风险描述：

- 文件迁移后，脚本与文档中的相对路径可能断裂

缓解：

- 优先使用脚本自身目录推导路径
- 迁移后逐个检查根入口与新入口

### 风险二：旧命令使用者无感知失败

风险描述：

- 如果旧路径直接删除，已有命令会立即失效

缓解：

- 根层保留兼容壳
- 文档先跳转后逐步迁移认知

### 风险三：误伤 Jenkins/CI 路径

风险描述：

- 历史 CI 对 `docker/` 根目录存在强依赖

缓解：

- 严格限制重构范围
- upstream CI 路径全部原位保留

## 13. 产出物

本设计落地后，预期新增或调整的产出包括：

- 更清晰的 `docker/local/` 本地开发体系
- 更明确的 `docker/legacy/` 历史文档隔离
- 可兼容旧用法的根入口脚本
- 更统一的本地开发文档导航

## 14. 验收标准

满足以下条件即可视为本次重构完成：

1. 新人浏览 `docker/` 根目录时，可以快速区分：
   - upstream CI 基础设施
   - 本地开发体系
   - 历史文档
2. 旧命令入口保持可用
3. 本地开发文档集中在单一位置
4. `docker-compose.yml` 与相关脚本可以在新结构下运行
5. upstream 历史 CI 路径未被破坏

## 15. 结论

本次 `docker/` 重构不追求一次性“彻底整理”，而是通过中度重构，把当前最混乱的“本地开发体系平铺”问题解决掉。

该方案兼顾了三件事：

- 结构清晰
- 风险可控
- 兼容现有使用方式

因此，它是当前阶段最合适的目录治理方案。
