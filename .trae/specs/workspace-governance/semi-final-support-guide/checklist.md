---
title: SpecWeave复赛作品技术支持资源指南 - 验证清单
date: 2026-07-22
---

# SpecWeave复赛作品技术支持资源指南 - Verification Checklist

## 文档结构与规范

- [ ] 文档目录 `playground/semi-final-support/` 已创建
- [ ] 主文档README.md包含正确的frontmatter（title/date/content_sensitivity: private）
- [ ] 文档开头有"如何使用本指南"简明说明
- [ ] 目录结构清晰，支持快速定位到任意章节
- [ ] 所有章节标题层级正确（H1→H2→H3），无跳级

## 资源覆盖完整性

- [ ] 8大资源类别全部覆盖：代码模块、API接口、开发工具、模板脚手架、技术文档、测试质量、容器部署、案例参考
- [ ] 可复用代码模块章节包含至少9个核心库模块（frontmatter/markdown/cli/patterns/atomic_write/io_safety/rules/spec_loader/process）
- [ ] 多智能体冲突解决模块和测试场景生成器单独说明
- [ ] MDI Mermaid生成器和MCP服务器有独立说明
- [ ] API章节覆盖Flask API（3个端点）、提示词萃取Pipeline、MCP端点、HA API、论坛Bot
- [ ] 开发工具覆盖至少10个常用Skill和15个核心脚本
- [ ] 容器化模板覆盖PyTorch/Docker-DIND/XMNN三套
- [ ] 文档模板至少包含handoff-template和task-template
- [ ] 测试质量章节包含10项CI检查完整说明
- [ ] 优秀作品库（563件）作为案例参考入口被引用

## 代码示例质量

- [ ] 每个核心库模块至少1个可运行的Python代码片段
- [ ] 代码示例语法正确（通过python -m py_compile检查）
- [ ] 代码示例包含import语句和核心调用，可复制使用
- [ ] API调用示例包含完整的请求/响应格式
- [ ] 有第三方依赖的模块明确标注依赖名称和安装方式
- [ ] Shell命令可直接复制执行（抽样5个验证--help输出一致）
- [ ] 容器构建命令包含完整的docker build指令

## 开发阶段工作流

- [ ] 6个开发阶段全部覆盖：项目初始化、核心开发、质量保障、性能优化、部署交付、文档撰写
- [ ] 每个阶段至少3项推荐资源
- [ ] 每个阶段的快速操作步骤≤5步
- [ ] 阶段之间逻辑递进关系清晰
- [ ] 质量保障阶段包含完整的CI 10项检查执行顺序

## 作品类型资源包

- [ ] AI Agent类作品推荐清单完整（必选≥3项+推荐≥2项）
- [ ] 工具CLI类作品推荐清单完整
- [ ] Web应用类作品推荐清单完整
- [ ] 文档/知识库类作品推荐清单完整
- [ ] 每类作品有≤5步的快速启动步骤
- [ ] 必选资源与推荐资源有明确视觉区分
- [ ] 参考案例链接指向真实存在的文件/目录

## 链接与路径

- [ ] 所有相对路径链接可正确跳转（通过check-links.py验证0死链）
- [ ] 代码引用使用可点击的文件链接格式
- [ ] 源文件路径使用相对于项目根目录的写法
- [ ] 外部链接（如有）标注为外部参考

## Mermaid图表

- [ ] 资源全景图Mermaid代码块通过check-mermaid.py检查（0错误0警告）
- [ ] 如有其他Mermaid图表（开发阶段流程图等），同样通过检查
- [ ] Mermaid图表在VS Code预览中正确渲染
- [ ] 遵循Mermaid安全编码六规则（无空行、文本加引号、无<br/>等）

## 快速参考卡片

- [ ] 快速参考卡片包含≥10个常用命令
- [ ] 快速参考卡片包含≥5个关键路径
- [ ] 快速参考卡片包含≥3个常见问题解答
- [ ] 卡片内容可在一屏内显示（≤80行）
- [ ] 所有命令可直接复制执行

## 兼容性与平台说明

- [ ] Mermaid跨环境渲染方案有说明（安全编码规则+check-mermaid.py）
- [ ] Python跨平台兼容性有说明（标准库优先、编码处理）
- [ ] Git跨平台配置有说明（.gitattributes/.editorconfig/UTF-8设置）
- [ ] Windows/Linux/Mac的命令差异有标注（如ci-check.sh vs ci-check.ps1）

## 产出物合规性

- [ ] 所有产出文件位于 `playground/semi-final-support/` 目录下
- [ ] 未修改任何原始项目文件（git diff仅显示新增文件）
- [ ] frontmatter标记content_sensitivity为private
- [ ] 文档语言为中文，术语使用与项目保持一致
- [ ] 不包含虚构的API或不存在的资源（所有引用均验证存在）
