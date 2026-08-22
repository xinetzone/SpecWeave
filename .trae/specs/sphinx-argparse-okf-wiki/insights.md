# sphinx-argparse 架构洞察与知识地图

## I-01：三层管道架构——数据提取/渲染/集成分离

**陈述**：sphinx-argparse 采用严格的三层分离架构：`parser.py`（纯数据提取层，无Sphinx依赖）→ `ext.py`指令渲染层（argparse字典→docutils节点）→ Sphinx域/索引集成层（交叉引用+索引生成）。

**证据**：
- F-024~F-048：`parse_parser()` 函数只依赖argparse私有API（`_get_positional_actions`、`_action_groups`、`_group_actions`、`_get_formatter`等），输入ArgumentParser对象，输出纯字典结构（含name/usage/bare_usage/action_groups/children等键），完全不导入sphinx或docutils
- F-012~F-013：ext.py从parser.py导入`parse_parser`和`parser_navigate`，从utils.py导入工具函数
- F-095~F-130：`ArgParseDirective`类负责Sphinx指令生命周期（run()方法），调用parse_parser获取数据后转换为docutils节点
- F-137~F-151：`ArgParseDomain`类独立管理命令注册和交叉引用解析
- F-131~F-136：`CommandsIndex`和`CommandsByGroupIndex`独立处理索引生成

**反常识**：初学者可能认为这是个简单的"argparse→HTML"扩展，但实际上parser.py完全可以脱离Sphinx独立使用——它输出的是一个通用的字典树结构，可以被任何文档生成器消费。

**行动**：概念文档应按三层架构组织，先讲parser数据模型（概念4-5），再讲指令渲染（概念6-8），最后讲域和索引（概念9-10）。

## I-02：嵌套内容增强系统——definition_list注入机制

**陈述**：指令体内嵌内容通过definition_list语法实现四种注入模式（@before/@after/@replace/@skip），允许用户精确控制特定参数、子命令、选项组的文档内容，而无需修改Python源码。

**证据**：
- F-083~F-086：`map_nested_definitions()`从nested_content的definition_list中提取定义，classifier仅支持四个值
- F-152~F-163：`_print_action_groups()`和`_print_subcommands()`根据classifier决定是插入、追加、替换还是跳过特定项的描述
- F-160~F-164：子命令可以嵌套definition_list，实现无限层级的内容增强

**反常识**：用户可能以为指令体内容只是简单的"前言"文本，但实际上definition_list语法提供了类似AOP（面向切面编程）的精确注入能力——可以针对单个`--upgrade`选项追加文档，或替换整个子命令组的描述。

**行动**：概念文档需要专门一章讲解嵌套内容增强（概念7），四种classifier都要有示例。

## I-03：双Markdown支持路径——嵌套内容Markdown与帮助文本Markdown

**陈述**：扩展提供两种独立的Markdown渲染路径：`:markdown:`标志用于指令体嵌套内容的Markdown解析，`:markdownhelp:`标志用于argparse程序描述和选项帮助字符串的Markdown解析，两者通过独立的函数入口实现。

**证据**：
- F-404~F-415：`parse_markdown_block()`是Markdown解析入口，CommonMark解析→nest_sections手动嵌套→markdown()分发转换
- F-087~F-089：`render_list()`根据`markdown_help`参数决定走Markdown还是RST解析路径
- F-122~F-123：`run()`方法中，嵌套内容的Markdown通过`:markdown:`标志控制（第794行），帮助文本的Markdown通过`:markdownhelp:`标志控制（第807-808行）
- F-325~F-401：`nest_sections()`手动实现section嵌套，因为CommonMark本身不支持层级section

**反常识**：`:markdown:`和`:markdownhelp:`是两个独立开关——开启嵌套内容Markdown不影响帮助文本的解析方式。此外markdown.py没有使用myst-parser或recommonmark，而是自己实现了一个精简的CommonMark→docutils转换器（仅18种节点类型）。

**行动**：Markdown支持单独作为一章（概念8），讲清两个标志的区别和各自的使用场景。

## I-04：索引临时文件桥接机制

**陈述**：为解决Sphinx扩展生成的索引无法直接加入toctree的限制，扩展通过创建临时RST虚拟文件（builder-inited时创建，build-finished时删除）桥接这一gap。

**证据**：
- F-152~F-154：`_create_temporary_dummy_file()`在srcdir创建临时RST文件，包含标题和说明文本
- F-153：目标文件已存在时抛出ExtensionError
- F-1033~F-1041：`configure_ext()`在配置启用时创建对应临时文件
- F-094~F-098：`_delete_temporary_files()`在build-finished事件中清理所有临时文件
- F-143：`ArgParseDomain.temporary_index_files`列表跟踪所有临时文件路径

**反常识**：这不是"内存中动态生成文档"的优雅方案，而是利用Sphinx文件发现机制的务实hack——临时文件让Sphinx以为源目录中有一个真实的RST文件，从而允许它出现在toctree中。构建完成后立即删除，不留下痕迹。

**行动**：索引机制（概念10）需要解释这个临时文件机制，让用户理解为什么需要`*_in_toctree`配置选项。

---

## 知识地图

### 文档分组设计

**入门篇（concepts/ 00-03）**：了解扩展是什么、怎么安装、最基础的用法
- 00-introduction：sphinx-argparse简介、设计理念、安装
- 01-getting-started：5分钟快速上手、第一个argparse指令
- 02-directive-basics：argparse指令基础、三种parser指定方式（module+func/ref/filename+func）
- 03-directive-options：指令选项全解（18个选项分类讲解）

**核心篇（concepts/ 04-08）**：理解数据模型和渲染机制
- 04-parser-data-model：parser数据提取模型——parse_parser输出的字典结构
- 05-nested-subcommands：子命令与路径导航——parser_navigate、:path:选项、多级子命令
- 06-nested-content-enhancement：嵌套内容增强系统——@before/@after/@replace/@skip
- 07-markdown-support：Markdown支持——:markdown:与:markdownhelp:的区别
- 08-manpage-output：Man page输出格式——:manpage:选项

**高级篇（concepts/ 09-11）**：域系统、索引和扩展开发
- 09-domain-crossref：commands域与交叉引用——:command:角色、ArgParseDomain
- 10-command-indices：命令索引生成——两种索引、临时文件机制、分组索引
- 11-configuration：conf.py配置选项详解——7个配置值

**实战篇（examples/）**：
- basic-usage：基础用法——module+func方式的完整示例
- filename-pattern：外部脚本文档化——:filename:方式
- subcommand-docs：子命令文档化——:path:选项与多页面组织
- content-enhancement：内容增强——嵌套definition_list注入自定义文档
- markdown-integration：Markdown集成——:markdown:和:markdownhelp:的使用

**信源（references/）**：
- sphinx-argparse-source：源码信源登记

### 概念文档与事实覆盖映射

| 文档 | 覆盖事实 |
|------|---------|
| 00-introduction | F-001~F-010, F-011 |
| 01-getting-started | F-095~F-098, F-116~F-121, F-165~F-169 |
| 02-directive-basics | F-116~F-118, F-165~F-168, F-172 |
| 03-directive-options | F-165~F-181（全部18个选项） |
| 04-parser-data-model | F-024~F-048（parse_parser完整输出结构） |
| 05-nested-subcommands | F-014~F-019, F-029~F-034, F-169 |
| 06-nested-content-enhancement | F-083~F-089, F-152~F-164 |
| 07-markdown-support | F-056~F-082, F-087~F-089, F-178~F-179 |
| 08-manpage-output | F-100~F-105, F-173 |
| 09-domain-crossref | F-137~F-151, F-052~F-054 |
| 10-command-indices | F-131~F-136, F-152~F-156, F-143 |
| 11-configuration | F-157~F-164（全部7个配置值） |
