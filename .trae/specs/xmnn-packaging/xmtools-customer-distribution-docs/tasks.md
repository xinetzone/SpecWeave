# Tasks

创建 `xmtools/distribution/` 客户分发文档集。

## Task 1: 创建分发目录与 README 索引
- [x] 1.1 创建 `distribution/` 目录
- [x] 1.2 创建 `README.md` 索引：概述 + 文档导航表 + 版本信息

## Task 2: 编写产品介绍文档
- [x] 2.1 创建 `intro.md`：XMNN 是什么、典型应用场景、核心价值
- [x] 2.2 内容面向非技术背景，通俗说明

## Task 3: 编写功能说明文档
- [x] 3.1 创建 `features.md`：功能总览 + 各功能详解（模型编译、精度验证、推理、性能分析、REST API 服务）
- [x] 3.2 功能矩阵表（含状态）

## Task 4: 编写快速开始文档
- [x] 4.1 创建 `quickstart.md`：前置条件 + 安装（wheel/Docker 镜像）+ 首次使用示例 + 预期输出
- [x] 4.2 命令与项目实际一致

## Task 5: 编写使用指南文档
- [x] 5.1 创建 `usage-guide.md`：详细使用流程（Docker 运行、模型加载、REST API 调用、常见运维操作）
- [x] 5.2 客户端友好，步骤清晰

## Task 6: 编写常见问题（FAQ）文档
- [x] 6.1 创建 `faq.md`：基于 README 与 DEPLOYMENT 常见问题，转为客户友好表述
- [x] 6.2 覆盖：安装、运行、模型、性能、端口冲突等

## Task 7: 编写版本说明文档
- [x] 7.1 创建 `changelog.md`：当前版本 1.2.1-dev0 说明 + 版本历史
- [x] 7.2 标注发布日期与状态

## Task 8: 校验文档质量
- [x] 8.1 核对所有文档 frontmatter 合法（title/description/last_updated）
- [x] 8.2 核对版本号、命令、功能描述与项目实际一致
- [x] 8.3 核对 README 索引正确链接全部文档

# Task Dependencies

- [Task 1] 无依赖（目录与索引先行）
- [Task 2-7] 依赖 [Task 1]（需目录存在），可并行
- [Task 8] 依赖 [Task 2-7]（全部文档完成后校验）

# 并行化说明

- Task 2-7（各文档编写）相互独立，可并行执行
- Task 1 需先完成以建立目录结构
- Task 8 为收尾校验，依赖全部文档完成