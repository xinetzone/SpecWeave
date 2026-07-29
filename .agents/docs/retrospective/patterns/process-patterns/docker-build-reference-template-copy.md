---
id: "docker-build-reference-template-copy"
title: "Docker 构建系统参考模板复制法"
type: "process"
date: "2026-07-22"
maturity: "L1"
source: "retrospective-caffe-docker-runtime-20260722"
tags: ["docker", "build-system", "template", "reference-copy", "directory-structure"]
validation_count: 1
reuse_count: 0
documentation_level: "basic"
---
# Docker 构建系统参考模板复制法

## 触发场景

- 需要为新项目创建 Docker 构建系统
- 存在同类项目的成熟 Docker 构建系统可作为参考
- 适用于：任何需要 Docker 化的软件项目
- 不适用于：参考项目结构与目标项目差异过大（如 Go 项目参考 Python 项目）

## 核心做法

1. **识别参考项目**：找到与目标项目技术栈相近、Docker 构建系统成熟的参考项目
2. **提取目录骨架**：复制目录结构（`lib/`、`build/`、`config/`、`scripts/`），保留核心文件（`log.sh`、`check_env.sh`、Dockerfile 模板）
3. **适配替换**：将参考项目特定的内容替换为目标项目的内容（镜像名、依赖列表、编译命令）
4. **逐层构建验证**：从 `base-system` 开始逐层构建，每层验证通过后再进入下一层
5. **补充文档**：编写 `RUNTIME_IMAGE_USAGE.md` 使用指南

## 反模式（不要这么做）

- ❌ **从零设计目录结构**：浪费时间在不必要的设计决策上，且容易遗漏关键文件（如 `check_env.sh` 的容器工具检测、`log.sh` 的彩色日志）
- ❌ **复制全部文件不修改**：参考项目的特定配置（如 TVM 的编译选项）不适用于目标项目，盲目复制会导致构建失败
- ❌ **跳过逐层验证，直接构建全量镜像**：一旦失败，排查范围是全部层，定位困难。多阶段构建应逐层验证

## 检验标准

- 目录结构与参考项目对齐（`lib/`、`build/`、`config/`、`scripts/` 均存在）
- 首次构建可从 `base-system` 开始逐层成功
- 二次构建缓存命中率 > 90%

## 迁移示例

- 场景 1（非当前领域）：为 TensorFlow 项目创建 Docker 构建系统，参考 Caffe 项目结构
- 场景 2（跨领域）：为 Node.js Web 应用创建 Docker 构建系统，参考 Python 项目的脚本组织方式

## 实际案例

- **Caffe Docker 运行时镜像构建**（2026-07-22）：参考 `npu_tvm/docker/local/` 目录结构，1 小时内完成 13 个产出物。目录结构对齐后，后续维护和脚本复用成本显著降低。