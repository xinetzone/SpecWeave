---
id: "add-sunlogin-cli-wiki-tasks"
title: "向日葵企业CLI Wiki创建与更新 - 任务分解"
source: "spec.md"
date: "2026-07-06"
---

# 向日葵企业CLI帮助指南Wiki文档创建与更新 - The Implementation Plan

## [x] Task 1: 创建向日葵CLI完整Wiki文档（sunlogin-cli-wiki.md）
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 创建新文件 `d:\AI\docs\knowledge\learning\07-vendor-product-learning\sunlogin\sunlogin-cli-wiki.md`
  - 按照现有Wiki的10章结构编写：
    1. 概述与学习目标（产品定位、CLI价值、学习目标、整体架构）
    2. 核心概念（MCP API、会话ID、归一化坐标、7种连接类型）
    3. 安装与环境配置（环境要求、npm安装、AI Agent安装、验证方法）
    4. 快速上手（登录、设备列表、建立会话、会话ID保存）
    5. 全局选项与账号管理（output/verbose/help、login/logout）
    6. 设备管理命令（ls/search/info/restart/shutdown/wakeup）
    7. 会话控制命令（ls/connect/status/disconnect/screenshot）
    8. 桌面/文件/端口转发/SSH命令（mouse/type/paste/keycombo、文件管理、端口转发配置、SSH地址获取）
    9. AI Agent集成与实战场景（集成优势、工作原理、自动巡检、技术支持、批量部署三大场景）
    10. 专业洞察、常见问题与资源链接（产品设计哲学、AI Agent启示、环境变量、错误码、帮助获取、相关链接）
  - 添加专业深度洞察章节，分析CLI与MCP的关系、"命令行即API"设计理念、AI原生工具特征
  - 所有命令示例使用bash代码块
  - 添加内部链接到其他相关Wiki
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-6
- **Test Requirements**:
  - `programmatic` TR-1.1: 文件名符合kebab-case规范（sunlogin-cli-wiki.md）
  - `programmatic` TR-1.2: YAML frontmatter包含title、source、date、tags字段
  - `programmatic` TR-1.3: 所有代码块标注为bash语言
  - `human-judgement` TR-1.4: 覆盖官方文档所有7大类命令，包含用途、语法、选项、示例
  - `human-judgement` TR-1.5: 包含3个实战场景的完整代码示例
  - `human-judgement` TR-1.6: 包含错误码表、环境变量配置说明
  - `human-judgement` TR-1.7: 包含专业洞察章节，分析产品设计哲学
- **Notes**: 参考sunlogin-security-wiki.md的章节结构和写作风格

## [x] Task 2: 更新向日葵综合分析Wiki（sunlogin-comprehensive-analysis-wiki.md）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 读取现有sunlogin-comprehensive-analysis-wiki.md
  - 在第八章"AI战略深度解析"中补充CLI工具的介绍
  - 在8.2节向日葵AI产品矩阵部分添加CLI作为MCP的命令行入口
  - 说明CLI与MCP服务器的关系：MCP是面向AI Agent的协议接口，CLI是面向命令行/脚本的工具，二者互补
  - 补充CLI的核心价值：适合批量运维、脚本集成、自动化场景
  - 保持原有文档结构，不破坏现有内容
  - 添加到新CLI Wiki的内部链接
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `human-judgement` TR-2.1: 第八章AI战略部分有CLI工具的介绍
  - `human-judgement` TR-2.2: 清晰说明CLI与MCP的关系和定位差异
  - `human-judgement` TR-2.3: 包含指向新CLI Wiki的内部链接
  - `human-judgement` TR-2.4: 原有文档内容保持完整，无意外修改

## [x] Task 3: 更新向日葵产品系列索引（sunlogin-product-series-index.md）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 读取现有sunlogin-product-series-index.md
  - 在"五、跨产品综合分析与AI战略"分类下添加CLI Wiki条目
  - 更新"系列概览"表格中的Wiki总数（从11篇更新为12篇）
  - 在"跨产品共性洞察"或"AI Agent跨领域映射"部分考虑是否需要补充CLI相关内容
  - 在"相关资源"部分添加CLI Wiki链接
  - 更新文档最后更新日期
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `human-judgement` TR-3.1: 系列概览统计数字正确更新
  - `human-judgement` TR-3.2: 产品分类表格中有CLI Wiki的条目和链接
  - `human-judgement` TR-3.3: 链接使用相对路径，格式正确
  - `human-judgement` TR-3.4: 最后更新日期更新为当前日期

## [x] Task 4: 格式验证与链接检查
- **Priority**: medium
- **Depends On**: Task 1, Task 2, Task 3
- **Description**: 
  - 运行文件名规范检查脚本验证所有文件名
  - 验证所有内部链接的正确性（相对路径是否正确）
  - 验证YAML frontmatter格式
  - 验证代码块语言标注
  - 验证表格格式整齐
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-4.1: 运行python .agents/scripts/check-filename-convention.py验证文件名
  - `programmatic` TR-4.2: 验证所有内部链接路径格式正确
  - `human-judgement` TR-4.3: 人工检查YAML frontmatter格式正确
  - `human-judgement` TR-4.4: 检查代码块语言标注一致性

## [x] Task 5: 内容准确性最终验证
- **Priority**: medium
- **Depends On**: Task 1, Task 2, Task 3
- **Description**: 
  - 对比官方文档验证关键信息：
    - 安装命令：npm install -g @aweray/awesun-cli
    - 版本验证：awesun-cli --version
    - 7种连接类型：desktop/file/cmd2/ssh/desktop_view/newcamera/forward
    - 6种错误码：0成功/1通用错误/2参数错误/3认证失败/4网络错误/5会话不存在/6设备离线
    - 3个实战场景：批量巡检、技术支持、批量部署
  - 检查是否有遗漏的重要命令或说明
  - 确保没有添加官方文档中不存在的信息
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `human-judgement` TR-5.1: 关键命令和参数与官方文档一致
  - `human-judgement` TR-5.2: 7种连接类型完整准确
  - `human-judgement` TR-5.3: 错误码表完整准确（共7种：0成功/1通用错误/2参数错误/3认证失败/4网络错误/5会话不存在/6设备离线）
  - `human-judgement` TR-5.4: 没有添加未经证实的内容
