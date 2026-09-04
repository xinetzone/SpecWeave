---
id: create-codewhale-wiki-tutorial-checklist
title: CodeWhale Wiki 教程生成 - 验证清单
source: spec.md
---

# CodeWhale Wiki 教程生成 - 验证清单

## R阶段：事实采集

- [x] G1-1: 官网事实清单≥20条，无因果词（"因为""导致""所以"）
- [x] G1-2: 源码事实清单≥15条，无因果词
- [x] G1-3: 官网覆盖产品定位、功能、安装、运行时四个维度
- [x] G1-4: 源码覆盖 crates/ 模块划分、核心模块功能、关键配置文件
- [x] G1-5: 事实数据准确（版本号 v0.9.3、36 个提供商、MIT 协议、39k Star）
- [x] G1-6: 所有事实可追溯到官网页面或源码文件

## I阶段：洞察提炼

- [x] G2-1: 核心洞察≥3条
- [x] G2-2: 每条洞察包含完整四元组（陈述/证据/反常识/行动）
- [x] G2-3: 证据引用事实编号（F-xxx），可追溯
- [x] G2-4: 洞察之间有独立性，维度不重叠
- [x] G2-5: 有反常识性，不是正确的废话
- [x] G2-6: 行动建议具体可执行
- [x] G2-7: 覆盖模型路由、嵌套宪法、终端优先、Fleet 编排等核心主题

## E阶段：Wiki 教程萃取

- [x] G3-1: Wiki 教程目录结构符合知识库模板规范
- [x] G3-2: index.md 包含架构总览 Mermaid 图
- [x] G3-3: tech/intro.md 包含项目定位、核心价值、技术栈、架构概览
- [x] G3-4: tech/quickstart.md 包含完整安装步骤和首次使用指引
- [x] G3-5: tech/features.md 覆盖 Route Resolver、Nested Constitution、Plan/Act/Operate、Fleet
- [x] G3-6: tech/deploy.md 覆盖安装渠道和提供商配置
- [x] G3-7: tech/changelog.md 覆盖版本演进（deepseek-tui → CodeWhale）
- [x] G3-8: general/domain/index.md 覆盖终端优先哲学与模型无关理念
- [x] G3-9: topics/index.md 覆盖设计哲学与行业洞察
- [x] G3-10: 所有页面使用 YAML frontmatter，遵循 MDI v1.0 规范
- [x] G3-11: 文件名遵循 kebab-case 规范
- [x] G3-12: 专业术语首次出现时附中英文对照
- [x] G3-13: 代码示例可直接复制执行
- [x] G3-14: 教程覆盖"安装→配置→使用→进阶"完整学习路径

## V阶段：对抗审查

- [x] V-1: 四视角全部覆盖（魔鬼代言人/新人/老板/未来）
- [x] V-2: 审查意见≥5条，每条有具体攻击点
- [x] V-3: 新人视角：零基础用户可按教程完成安装和首次使用
- [x] V-4: 魔鬼代言人：数据准确性已验证，逻辑漏洞已修复
- [x] V-5: 老板视角：教程实用价值评估通过
- [x] V-6: 未来视角：教程时效性评估通过
- [x] V-7: 至少采纳2条意见修正产出

## C阶段：质量验证与原子提交

- [x] C-1: check-links.py 全部通过
- [x] C-2: check-filename-convention.py 全部通过
- [x] C-3: 每个提交符合单一职责原则
- [x] C-4: 提交信息遵循 Conventional Commits 规范
- [x] C-5: 提交信息用中文描述"为什么"
- [x] C-6: 知识库索引文件已更新