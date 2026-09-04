# Checklist

## 规范文档完整性

- [x] trae-edge-case-handler.md 包含模块概述（定位、职责、核心概念）
- [x] 四大边界场景（IDE集成/论坛操作/外部工具链/Trae Work）均有独立的章节定义
- [x] 每个边界场景下列出至少3个具体边界条件
- [x] 每个边界条件有明确的检测信号和判断方法
- [x] 边界条件三级分级（致命/警告/提示）有清晰定义和处理策略
- [x] 异常处理流程覆盖从检测到恢复的完整链路
- [x] 至少4个特殊场景有预定义适配策略
- [x] 模块接口规范定义了输入/输出/日志/验证四个接口

## 规范一致性

- [x] 引用的 multi-signal-detection.md 模式存在且成熟度≥L2
- [x] 引用的 dry-run-first.md 模式存在且成熟度≥L2
- [x] 引用的 check-and-restore.md 模式存在且成熟度≥L2
- [x] trae-edge-case-handler.md 遵循 .agents/teams/ 现有文档的格式风格
- [x] 文档使用 Mermaid 流程图表达处理流程（遵循项目 Mermaid 优先原则）

## 索引更新

- [x] .agents/teams/README.md 目录结构包含 trae-edge-case-handler.md
- [x] .agents/teams/README.md 模块职责矩阵包含新模块条目
- [x] .agents/teams/README.md 核心概念关系图包含新模块节点
- [x] AGENTS.md 团队管理路由包含新模块引用

## 链接与验证

- [x] trae-edge-case-handler.md 中所有相对路径链接有效
- [x] .agents/teams/README.md 中新增链接有效
- [x] check-links.py 校验通过（无断链）
- [x] check-spec-consistency.py 校验通过（teams目录15个本地引用全部有效）
