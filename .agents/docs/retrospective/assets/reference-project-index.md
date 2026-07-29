---
id: "reference-project-index"
title: "可参考项目索引"
source: "retrospective-caffe-docker-runtime-20260722#洞察1"
date: 2026-07-22
tags: [reference, index, docker, template]
---
# 可参考项目索引

> 创建新项目的 Docker 构建系统时，优先查阅本索引寻找可参考的同类项目模板，避免从零设计。

## 已有参考项目

### Docker 构建系统

| 项目 | 路径 | 参考价值 | 关键特征 |
|------|------|---------|---------|
| NPU TVM | `external/xmhub/npu_tvm/docker/local/` | Docker 构建系统模板 | 多阶段构建、conda 环境、lib/ 公共库、build/ 构建脚本、conda+config/ 环境配置、.gitignore 日志管理 |
| Caffe | `external/chaos/caffe/docker/local/` | 老旧 C++ 框架 Docker 化 | 参考 npu_tvm 结构、Makefile 动态生成、conda 环境兼容性处理、验证脚本体系 |

### 目录结构规范

所有 Docker 构建系统应遵循以下目录结构（参考 npu_tvm）：

```
docker/local/
├── conda/                  # conda 环境入口
│   ├── Dockerfile          # 多阶段 Dockerfile
│   ├── build.sh            # 开发构建脚本
│   ├── run.sh              # 开发容器启动脚本
│   ├── RUNTIME_IMAGE_USAGE.md  # 运行时镜像使用指南
│   ├── build/              # 构建相关脚本
│   │   ├── build-multistage.sh  # 多阶段构建（含日志）
│   │   └── export-image.sh      # 镜像导出
│   ├── config/             # 环境配置
│   │   ├── condarc         # conda 镜像源配置
│   │   └── pip.conf        # pip 镜像源配置
│   └── scripts/            # 辅助脚本
│       ├── generate-makefile-config.sh  # Makefile 动态生成
│       ├── verify-caffe.sh              # 编译验证
│       └── verify-runtime.sh            # 运行时验证
├── lib/                    # 公共函数库
│   ├── log.sh              # 彩色日志
│   └── check_env.sh        # 环境检查
└── logs/                   # 构建日志
```

## 如何使用

1. **第一步**：在本索引中找到与当前任务最相似的项目
2. **第二步**：复制参考项目的目录结构作为骨架
3. **第三步**：根据当前项目需求调整 Dockerfile、脚本、配置
4. **第四步**：将新项目添加回本索引，供后续复用

## 反模式

- 不要跳过索引直接从零设计——至少参考一个已有项目
- 不要复制后不调整——每个项目的依赖、编译方式、环境需求不同
- 不要只参考结构不参考公共库——lib/log.sh 和 lib/check_env.sh 是核心复用资产