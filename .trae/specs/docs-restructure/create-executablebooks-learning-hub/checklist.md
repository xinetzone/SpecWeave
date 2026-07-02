---
version: 1.0
---

# ExecutableBooks 学习资料库建设 - Verification Checklist

## 目录结构验证
- [x] 主文件夹 `docs/knowledge/learning/executablebooks-myst-guide/` 已创建
- [x] 子目录 syntax/ 已创建（可含 .gitkeep）
- [x] 子目录 examples/ 已创建（可含 .gitkeep）
- [x] 子目录 templates/ 已创建（可含 .gitkeep）
- [x] 子目录 resources/ 已创建（可含 .gitkeep）
- [x] 目录命名符合 kebab-case 规范

## 核心文档验证
- [x] 00-overview.md 存在且包含生态概览、核心特性介绍
- [x] 01-myst-syntax.md 存在且详细解释 Directives/Roles/Fences/嵌套语法
- [x] 02-project-structure.md 存在且说明 myst.yml 配置和项目结构
- [x] 03-frontmatter-config.md 存在且说明 frontmatter 字段和配置
- [x] 04-table-of-contents.md 存在且说明 TOC 配置
- [x] 05-best-practices.md 存在且包含实用建议和常见陷阱
- [x] 06-resources.md 存在且包含官方链接和学习路径
- [x] README.md 存在且作为主入口文档

## 模板和示例验证
- [x] templates/myst.yml.template 存在且包含注释的配置模板
- [x] examples/ 目录下至少有 4 个示例文件
- [x] 示例文件覆盖至少 5 种常用 directives 和 3 种 roles
- [x] 配置模板 YAML 语法正确

## 文档内容质量验证
- [x] 00-overview.md 清晰说明 ExecutableBooks 生态和 MyST 定位
- [x] 01-myst-syntax.md 包含代码示例说明冒号围栏 vs 反引号围栏的使用场景
- [x] 01-myst-syntax.md 说明三种选项配置方式（:key:value/YAML/inline）
- [x] 02-project-structure.md 说明 myst init/start/build/clean 命令
- [x] 03-frontmatter-config.md 说明字段作用范围分类（page/project/override）
- [x] 04-table-of-contents.md 说明 file/url/pattern/children 节点类型
- [x] 04-table-of-contents.md 说明 {toc} 指令及 context 参数
- [x] 05-best-practices.md 包含至少 5 条实用建议或注意事项
- [x] 06-resources.md 包含官方文档链接和进阶学习路径
- [x] README.md 包含学习路径指引
- [x] README.md 包含所有子文档的导航链接
- [x] README.md 包含一分钟快速参考表/快速开始指南

## 规范合规验证
- [x] 所有 Markdown 文档（除模板文件外）包含 TOML frontmatter
- [x] TOML frontmatter 包含 source 字段标注信息来源
- [x] 所有内部链接使用相对路径（无 file:/// 绝对路径）
- [x] 文件命名采用数字前缀 + kebab-case 风格
- [x] 文档内容基于官方文档整理，无编造信息
- [x] 配置模板包含中文注释说明

## 索引同步验证
- [x] docs/knowledge/README.md 已更新，包含 executablebooks-myst-guide 条目
- [x] 索引条目包含清晰的描述和正确的相对链接
- [x] 新条目与现有学习资料格式保持一致

## 链接有效性验证
- [x] 运行链接检查脚本无断链错误
- [x] 内部文档间的交叉引用有效
- [x] 外部链接格式正确
