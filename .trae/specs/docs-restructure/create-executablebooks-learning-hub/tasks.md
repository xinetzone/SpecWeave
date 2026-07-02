---
version: 1.0
---

# ExecutableBooks 学习资料库建设 - The Implementation Plan

## [x] Task 1: 创建目录结构基础框架
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `docs/knowledge/learning/` 下创建主文件夹 `executablebooks-myst-guide/`
  - 创建子目录：syntax/、examples/、templates/、resources/
  - 在子目录中添加 .gitkeep 文件以确保空目录被 git 追踪
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 验证 `docs/knowledge/learning/executablebooks-myst-guide/` 目录存在
  - `programmatic` TR-1.2: 验证 syntax/、examples/、templates/、resources/ 四个子目录都存在
  - `programmatic` TR-1.3: 验证每个子目录都包含 .gitkeep 文件
- **Notes**: 使用 kebab-case 命名规范，与现有 learning 目录保持一致

## [x] Task 2: 编写生态概览文档（00-overview.md）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 编写 ExecutableBooks 项目介绍、发展历程
  - 说明 MyST Markdown 的定位（CommonMark 超集、灵感来自 Sphinx/RST）
  - 介绍 mystmd 与 Jupyter Book v1 的关系
  - 概述核心特性：directives/roles、多格式导出、可执行文档、科学出版支持
  - 添加 TOML frontmatter（含 source 字段标注来源）
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `human-judgement` TR-2.1: 文档结构清晰，包含项目介绍、核心特性、生态定位
  - `programmatic` TR-2.2: 文档包含有效的 TOML frontmatter，source 字段指向官方文档
  - `programmatic` TR-2.3: 文档命名符合数字前缀 + kebab-case 规范
- **Notes**: 参考资料：https://executablebooks.org/en/latest/、https://mystmd.org/guide/overview

## [x] Task 3: 编写 MyST 核心语法文档（01-myst-syntax.md）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 详细解释 Directives 语法：冒号围栏（:::）vs 反引号围栏（```）
  - Directives 参数和选项配置：:key: value 格式、YAML 块、inline options
  - Roles 语法：{rolename}`content` 行内扩展
  - 嵌套内容块规则：通过增加反引号/冒号数量实现嵌套
  - 提供每种语法的代码示例
  - 添加常用 directives/roles 速查表
  - 添加 TOML frontmatter
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `human-judgement` TR-3.1: 清晰解释 Directives、Roles、Fences、嵌套语法，配有示例
  - `human-judgement` TR-3.2: 说明何时使用冒号围栏、何时使用反引号围栏
  - `human-judgement` TR-3.3: 包含至少 3 种选项配置方式的示例
  - `programmatic` TR-3.4: 文档包含有效的 TOML frontmatter
- **Notes**: 参考资料：https://mystmd.org/guide/syntax-overview、https://mystmd.org/guide/directives

## [x] Task 4: 编写项目结构与配置文档（02-project-structure.md）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 说明标准 MyST 项目目录结构
  - 详细解释 myst.yml 配置文件：version、project、site 三大块
  - 解释 _build 目录的作用和内容（site/exports/templates/temp）
  - 说明 myst init、myst start、myst build、myst clean 等常用命令
  - 提供项目初始化的完整流程示例
  - 添加 TOML frontmatter
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `human-judgement` TR-4.1: 清晰说明 myst.yml 的 project 和 site 配置块
  - `human-judgement` TR-4.2: 说明项目初始化和构建的基本流程
  - `programmatic` TR-4.3: 文档包含有效的 TOML frontmatter
- **Notes**: 参考资料：https://mystmd.org/guide/quickstart

## [x] Task 5: 编写 Frontmatter 配置文档（03-frontmatter-config.md）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 解释 frontmatter 的位置和作用范围（page only / project only / page can override）
  - 分类介绍常用字段：标题/描述、作者/单位、许可/版权、日期/关键词
  - 解释 exports、downloads、bibliography 等配置
  - 说明缩略图、横幅图、社交链接配置
  - 提供完整的 frontmatter 示例
  - 添加 TOML frontmatter
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `human-judgement` TR-5.1: 说明 frontmatter 字段的作用范围分类
  - `human-judgement` TR-5.2: 覆盖常用字段（title/authors/license/exports/bibliography等）
  - `human-judgement` TR-5.3: 提供可直接参考的配置示例
  - `programmatic` TR-5.4: 文档包含有效的 TOML frontmatter
- **Notes**: 参考资料：https://mystmd.org/guide/frontmatter

## [x] Task 6: 编写目录结构配置文档（04-table-of-contents.md）
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 解释 TOC 树结构：file、url、pattern、children 节点类型
  - 说明嵌套页面和下拉菜单（title + children）
  - Glob 模式匹配和排序（ascending/descending）
  - 隐藏页面（hidden: true）
  - 页面内 TOC 指令：{toc} 及其 context 参数（section/page/children/project）
  - URL Slug 生成规则和文件夹保留选项
  - 隐式 TOC（从文件系统自动生成）
  - 添加 TOML frontmatter
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `human-judgement` TR-6.1: 说明 TOC 的树结构和节点类型
  - `human-judgement` TR-6.2: 解释 glob 匹配、嵌套、隐藏页面等特性
  - `human-judgement` TR-6.3: 说明页面内 {toc} 指令的用法
  - `programmatic` TR-6.4: 文档包含有效的 TOML frontmatter
- **Notes**: 参考资料：https://mystmd.org/guide/table-of-contents

## [x] Task 7: 创建 myst.yml 配置模板（templates/myst.yml.template）
- **Priority**: medium
- **Depends On**: Task 4, Task 5
- **Description**:
  - 创建包含详细中文注释的 myst.yml 模板文件
  - 包含 project 块常用配置（title/description/authors/license/bibliography等）
  - 包含 site 块常用配置（template/title/nav/actions/domains等）
  - 包含 TOC 配置示例
  - 包含 exports 配置示例（PDF/Word导出）
  - 注释说明哪些字段是可选的
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `human-judgement` TR-7.1: 模板包含 project 和 site 两大配置块
  - `human-judgement` TR-7.2: 配置项配有中文注释说明用途
  - `human-judgement` TR-7.3: 包含 TOC 和 exports 的示例配置
  - `programmatic` TR-7.4: YAML 语法正确，无解析错误
- **Notes**: 模板文件不需要 TOML frontmatter，但需要清晰的注释

## [x] Task 8: 创建基础使用示例（examples/）
- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 创建 examples/basic-syntax.md：常用 directives 演示（note/warning/tip/important等admonitions、figure、code-block）
  - 创建 examples/roles-demo.md：常用 roles 演示（abbr、sub/sup、math、ref、cite等）
  - 创建 examples/admonitions.md：各类提示框样式示例
  - 创建 examples/cross-references.md：交叉引用示例
  - 每个示例文件包含 TOML frontmatter 和清晰的说明
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `human-judgement` TR-8.1: 至少有 4 个示例文件，覆盖不同使用场景
  - `human-judgement` TR-8.2: 展示至少 5 种常用 directives 和 3 种常用 roles
  - `programmatic` TR-8.3: 每个示例文件都包含 TOML frontmatter
  - `programmatic` TR-8.4: 示例文件语法正确
- **Notes**: 示例应简单直观，便于快速理解和复制

## [ ] Task 9: 编写最佳实践文档（05-best-practices.md）
- **Priority**: medium
- **Depends On**: Task 3, Task 4, Task 5
- **Description**:
  - 围栏选择指南：何时用 ::: 何时用 ```
  - Frontmatter 组织建议：project 级 vs page 级
  - 项目结构建议：文件命名、文件夹组织
  - 常见陷阱和注意事项
  - 与现有 CommonMark Markdown 的兼容性建议
  - 性能和可访问性建议
  - 添加 TOML frontmatter
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `human-judgement` TR-9.1: 包含围栏选择、frontmatter 组织等实用建议
  - `human-judgement` TR-9.2: 列出至少 5 个常见陷阱或注意事项
  - `programmatic` TR-9.3: 文档包含有效的 TOML frontmatter
- **Notes**: 结合官方文档和实际使用经验总结

## [ ] Task 10: 编写参考资源文档（06-resources.md）
- **Priority**: low
- **Depends On**: Task 2
- **Description**:
  - 官方文档链接汇总（mystmd.org、executablebooks.org、jupyterbook.org）
  - GitHub 仓库链接
  - 社区资源：论坛、博客、示例项目
  - 相关规范：MyST Spec、CommonMark 规范
  - 模板资源：myst-templates（400+ 期刊模板）
  - 推荐学习路径（从入门到进阶）
  - 添加 TOML frontmatter
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `human-judgement` TR-10.1: 包含官方文档、GitHub、社区等资源链接
  - `human-judgement` TR-10.2: 提供清晰的进阶学习路径建议
  - `programmatic` TR-10.3: 文档包含有效的 TOML frontmatter
  - `programmatic` TR-10.4: 外部链接格式正确
- **Notes**: 链接应指向官方和权威来源

## [ ] Task 11: 编写主入口 README.md
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9, Task 10
- **Description**:
  - 编写学习资料库的入口文档
  - 包含 ExecutableBooks/MyST 一句话简介
  - 提供学习路径建议（新手→进阶→高级）
  - 文档导航：列出所有子文档并提供一句话说明
  - 包含一分钟快速参考表（最常用的语法/配置）
  - 与项目其他学习资料的关联说明
  - 添加 TOML frontmatter
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `human-judgement` TR-11.1: 包含学习路径指引
  - `human-judgement` TR-11.2: 提供所有子文档的导航链接
  - `human-judgement` TR-11.3: 包含快速参考表
  - `programmatic` TR-11.4: 文档包含有效的 TOML frontmatter
  - `programmatic` TR-11.5: 所有内部链接使用相对路径且有效
- **Notes**: 参考 karpathy-llm-coding-guidelines-tutorial.md 的入口文档风格

## [ ] Task 12: 更新知识库索引（docs/knowledge/README.md）
- **Priority**: high
- **Depends On**: Task 11
- **Description**:
  - 读取现有的 docs/knowledge/README.md
  - 在 learning 相关部分添加 executablebooks-myst-guide 的条目
  - 添加简短描述和链接
  - 保持与现有索引格式一致
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-12.1: README.md 中包含 executablebooks-myst-guide 的条目
  - `programmatic` TR-12.2: 链接指向正确的相对路径
  - `human-judgement` TR-12.3: 条目的描述清晰准确
- **Notes**: 参考现有 learning 目录下其他资料的索引格式

## [ ] Task 13: 链接有效性检查和规范验证
- **Priority**: high
- **Depends On**: Task 12
- **Description**:
  - 运行链接检查脚本：`python .agents/scripts/check-links.py --path docs/knowledge/learning/executablebooks-myst-guide`
  - 验证所有文档的 TOML frontmatter 格式正确
  - 验证无 file:/// 绝对路径
  - 验证文件命名规范
  - 修复发现的问题
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `programmatic` TR-13.1: 链接检查通过，无断链
  - `programmatic` TR-13.2: 无 file:/// 绝对路径引用
  - `programmatic` TR-13.3: 所有 .md 文件都有有效的 TOML frontmatter（含 source 字段）
  - `programmatic` TR-13.4: 文件命名符合数字前缀 + kebab-case 规范
- **Notes**: 使用项目现有的 check-links.py 脚本进行验证
