# sphinx-argparse 源码事实清单

> R阶段产出：所有事实零推测，只记录"代码里有什么"，每个事实指向具体文件路径。

## 基本信息

F-001: 包名 `sphinx-argparse`，版本 `0.6.1`，定义于 `sphinxarg/__init__.py` 第1行（`__version__ = '0.6.1'`）
F-002: `version_info = (0, 6, 1)`，定义于 `sphinxarg/__init__.py` 第2行
F-003: 构建系统使用 flit_core（`requires = ["flit_core >= 3.10, <4"]`），定义于 `pyproject.toml` 第2行
F-004: 项目描述为 "A sphinx extension that automatically documents argparse commands and options"，定义于 `pyproject.toml` 第8行
F-005: Python 版本要求 `>=3.10`，定义于 `pyproject.toml` 第17行
F-006: 核心依赖为 `sphinx>=5.1.0` 和 `docutils>=0.19`，定义于 `pyproject.toml` 第38-41行
F-007: 可选依赖 `markdown` 需要 `CommonMark>=0.5.6`，定义于 `pyproject.toml` 第45-47行
F-008: 作者为 Ash Berlin-Taylor，邮箱 ash_github@firemirror.com，定义于 `pyproject.toml` 第66-68行
F-009: 许可证为 MIT，定义于 `pyproject.toml` 第15行
F-010: 模块名为 `sphinxarg`（flit module配置），定义于 `pyproject.toml` 第70-71行

## 包结构

F-011: 包 `sphinxarg/` 包含4个Python模块：`__init__.py`、`ext.py`、`markdown.py`、`parser.py`、`utils.py`
F-012: `sphinxarg/ext.py` 是主要扩展模块，从 `sphinxarg.parser` 导入 `parse_parser` 和 `parser_navigate`（ext.py 第29行）
F-013: `sphinxarg/ext.py` 从 `sphinxarg.utils` 导入 `command_pos_args` 和 `target_to_anchor_id`（ext.py 第30行）

## parser.py 模块

F-014: `parser.py` 定义异常类 `NavigationException(Exception)`，第8-9行
F-015: 函数 `parser_navigate(parser_result, path, current_path=None)` 定义于 parser.py 第12-34行
F-016: `parser_navigate` 接受 `parser_result`（dict）、`path`（str或list）、`current_path`（list或None）参数
F-017: `parser_navigate` 中 path 为字符串时按空白符分割为列表（第16行 `re.split(r'\s+', path)`）
F-018: `parser_navigate` 递归导航到子解析器，子命令通过 `child['identifier']`（别名）或 `child['name']` 匹配（第26行）
F-019: `parser_navigate` 在找不到子元素时抛出 `NavigationException`（第21-22行、第30-34行）
F-020: 函数 `_try_add_parser_attribute(data, parser, attribname)` 定义于 parser.py 第37-44行
F-021: `_try_add_parser_attribute` 从 parser 对象获取属性值，当属性为非空字符串时添加到 data 字典
F-022: 函数 `_format_usage_without_prefix(parser)` 定义于 parser.py 第47-54行
F-023: `_format_usage_without_prefix` 使用 argparse 私有API `parser._get_formatter()` 获取不带 'usage: ' 前缀的 usage 字符串
F-024: 函数 `parse_parser(parser, data=None, **kwargs)` 定义于 parser.py 第57-204行
F-025: `parse_parser` 接受关键字参数：`skip_default_values`、`skip_default_const_values`、`color`（第60-63行注释）
F-026: `parse_parser` 检查 parser 是否有 `color` 属性（Python 3.14+ argparse支持ANSI颜色），默认设为 False（第66-68行）
F-027: `parse_parser` 当 data 为 None 时初始化字典，包含键：`name`（空字符串）、`usage`、`bare_usage`、`prog`（第70-76行）
F-028: `parse_parser` 通过 `_try_add_parser_attribute` 添加 `description` 和 `epilog` 字段（第77-78行）
F-029: `parse_parser` 遍历 `parser._get_positional_actions()` 查找 `_SubParsersAction` 类型的动作（第79-81行）
F-030: `parse_parser` 处理子解析器别名：共享同一parser的多个名称只保留第一个，其余标记为别名（第86-99行）
F-031: 子解析器的 `prog` 属性被设置为 `f'{parser.prog} {name}'`（第106行）
F-032: 子解析器数据字典包含键：`name`、`help`、`usage`、`bare_usage`、`parent`（第107-116行）
F-033: 有别名的子解析器数据包含 `identifier` 键（第119-120行）
F-034: `parse_parser` 递归调用自身处理子解析器（第121行），子数据追加到 `data['children']` 列表（第122行）
F-035: `parse_parser` 遍历 `parser._action_groups` 提取选项组（第136行）
F-036: 每个 action group 内遍历 `action_group._group_actions`，跳过 `_HelpAction` 类型（第138-140行）
F-037: 字符串/None 类型的默认值被加引号（第143-150行）
F-038: help 字符串通过 `%` 格式化，使用 `vars(action)` 作为字典，包含 `prog` 和 `default` 键（第152-157行）
F-039: 位置参数（option_strings 为空列表）使用 `action.dest` 或 `action.metavar` 作为名称（第160-162行）
F-040: 名称为 `['==SUPPRESS==']` 的选项被跳过（第164-165行）
F-041: `_StoreConstAction` 类型的选项使用 `show_defaults_const` 控制默认值显示（第167-172行）
F-042: 其他类型选项使用 `show_defaults` 控制默认值显示（第173-178行）
F-043: 有 `choices` 属性的选项添加 `choices` 键到 option 字典（第179-180行）
F-044: help 中包含 `==SUPPRESS==` 的选项被跳过（第181-182行）
F-045: action_group 的 title 为 'options' 时重命名为 'Named Arguments'（第188-189行）
F-046: action_group 的 title 为 'positional arguments' 时重命名为 'Positional Arguments'（第190-191行）
F-047: 每个 group 字典包含键：`title`、`description`、`options`（第193-197行）
F-048: 非空的 action_groups 存入 `data['action_groups']`（第201-202行）

## utils.py 模块

F-049: 函数 `command_pos_args(result: dict) -> str` 定义于 utils.py 第1-33行
F-050: `command_pos_args` 递归构建完整命令名字符串：优先使用 `result['name']`，其次 `result['prog']`，有 `parent` 键时递归前缀父命令
F-051: `command_pos_args` 对非dict输入返回空字符串（doctest 第20-21行验证）
F-052: 函数 `target_to_anchor_id(target: str) -> str` 定义于 utils.py 第36-49行
F-053: `target_to_anchor_id` 将空格替换为连字符（`target.replace(' ', '-')`，第49行）
F-054: `target_to_anchor_id` 对空字符串输入抛出 ValueError（第45-47行）
F-055: utils.py 包含 `if __name__ == '__main__': doctest.testmod()`（第52-55行）

## markdown.py 模块

F-056: `markdown.py` 从 `commonmark` 或 `CommonMark` 包导入 `Parser`（兼容两种导入方式，第8-11行）
F-057: `markdown.py` 从 `commonmark.node` 或 `CommonMark.node` 导入 `Node`（第12-15行）
F-058: 函数 `custom_walker(node, space='')` 定义于 markdown.py 第18-48行，docstring描述为"A convenience function to ease debugging"，打印CommonMark节点树结构
F-059: 函数 `paragraph(node)` 定义于 markdown.py 第51-63行，处理Markdown段落节点
F-060: 函数 `text(node)` 定义于 markdown.py 第66-70行，返回 `nodes.Text(node.literal)`
F-061: 函数 `hardbreak(node)` 定义于 markdown.py 第73-77行，返回换行符文本节点
F-062: 函数 `softbreak(node)` 定义于 markdown.py 第80-84行，返回换行符文本节点
F-063: 函数 `reference(node)` 定义于 markdown.py 第87-98行，处理链接节点，设置 `refuri` 和可选 `name`
F-064: 函数 `emphasis(node)` 定义于 markdown.py 第101-108行，返回 `nodes.emphasis()` 斜体节点
F-065: 函数 `strong(node)` 定义于 markdown.py 第111-118行，返回 `nodes.strong()` 粗体节点
F-066: 函数 `literal(node)` 定义于 markdown.py 第121-147行，处理行内代码，支持语法高亮（通过Lexer）
F-067: 函数 `literal_block(node)` 定义于 markdown.py 第150-178行，处理代码块，支持语法高亮
F-068: 函数 `raw(node)` 定义于 markdown.py 第181-190行，处理原始HTML（`nodes.raw(..., format='html')`）
F-069: 函数 `transition(node)` 定义于 markdown.py 第193-197行，返回 `nodes.transition()`（水平线）
F-070: 函数 `title(node)` 定义于 markdown.py 第200-204行，返回 `nodes.title(node.first_child.literal, ...)`
F-071: 函数 `section(node)` 定义于 markdown.py 第207-218行，创建docutils section节点，使用首个heading子节点文本作为ID
F-072: 函数 `block_quote(node)` 定义于 markdown.py 第221-229行，返回 `nodes.block_quote()`
F-073: 函数 `image(node)` 定义于 markdown.py 第232-241行，创建 `nodes.image(uri=node.destination)`，alt文本取自第一个子节点
F-074: 函数 `list_item(node)` 定义于 markdown.py 第244-251行，返回 `nodes.list_item()`
F-075: 函数 `list_node(node)` 定义于 markdown.py 第254-269行，处理bullet list（`nodes.bullet_list`）和ordered list（`nodes.enumerated_list`）
F-076: 函数 `markdown(node)` 定义于 markdown.py 第272-322行，是核心分发函数，按节点类型 `t` 分派到对应处理函数
F-077: `markdown()` 函数支持的节点类型：paragraph, text, softbreak, linebreak, link, heading, emph, strong, code, code_block, html_inline, html_block, block_quote, thematic_break, image, list, item, MDsection（第282-315行）
F-078: 未处理的节点类型会打印警告并调用 `cur.pretty()`（第316-318行）
F-079: 函数 `finalize_section(section)` 定义于 markdown.py 第325-336行，修正节点的 nxt 和 parent 指针
F-080: 函数 `nest_sections(block, level=1)` 定义于 markdown.py 第339-401行，手动将CommonMark平铺节点嵌套为层级section结构
F-081: `nest_sections` 按heading级别递归嵌套section，创建自定义 `MDsection` 类型节点（第359行）
F-082: 函数 `parse_markdown_block(text)` 定义于 markdown.py 第404-415行，解析Markdown文本块：先用CommonMark Parser解析，再调用 `nest_sections` 嵌套section，最后调用 `markdown()` 转换

## ext.py 模块 - 辅助函数

F-083: 函数 `map_nested_definitions(nested_content)` 定义于 ext.py 第48-88行
F-084: `map_nested_definitions` 从嵌套内容的 definition_list 中提取定义字典，键为term文本，值为 `(classifier, definition_node, subcontent)` 元组
F-085: `map_nested_definitions` 支持的classifier值：`@replace`、`@before`、`@after`、`@skip`（第68-73行）
F-086: `map_nested_definitions` 遇到未知classifier抛出Exception（第74-75行）
F-087: 函数 `render_list(l, markdown_help, settings=None)` 定义于 ext.py 第91-113行
F-088: `render_list` 在 `markdown_help=True` 时调用 `parse_markdown_block` 解析Markdown（第97-100行）
F-089: `render_list` 在 `markdown_help=False` 时使用docutils RST Parser解析每个字符串元素（第101-112行）
F-090: `render_list` 对 `nodes.definition` 类型元素直接追加（第110-111行）
F-091: 函数 `_is_suppressed(item)` 定义为模块级函数（第116-121行）和 `ArgParseDirective` 的静态方法（第720-726行），逻辑相同：判断值是否为None或 `==SUPPRESS==`（去除引号后比较）
F-092: 函数 `print_action_groups(data, nested_content, markdown_help=False, settings=None, id_prefix='')` 定义于 ext.py 第124-221行（模块级旧版函数）
F-093: 函数 `print_subcommands(data, nested_content, markdown_help=False, settings=None)` 定义于 ext.py 第224-282行（模块级旧版函数）
F-094: 函数 `ensure_unique_ids(items)` 定义于 ext.py 第285-307行，递归遍历节点树中section节点，对重复ID添加 `_repeat{i}` 后缀保证唯一性

## ext.py 模块 - ArgParseDirective 类

F-095: 类 `ArgParseDirective(SphinxDirective)` 定义于 ext.py 第310行
F-096: `ArgParseDirective.has_content = True`（第311行）
F-097: `ArgParseDirective.required_arguments = 0`（第312行）
F-098: `ArgParseDirective.option_spec` 定义了18个选项（第313-331行）：`module`、`func`、`ref`、`prog`、`path`、`nodefault`(flag)、`nodefaultconst`(flag)、`filename`、`manpage`、`nosubcommands`、`passparser`(flag)、`noepilog`、`nodescription`、`markdown`(flag)、`markdownhelp`(flag)、`color`(flag)、`index-groups`
F-099: `ArgParseDirective.index_groups` 类属性默认为空元组（第332行）
F-100: 方法 `_construct_manpage_specific_structure(self, parser_info)` 定义于第334-421行，生成man page格式节点
F-101: `_construct_manpage_specific_structure` 生成SYNOPSIS section（包含bare_usage）、DESCRIPTION section、OPTIONS section、SUB-COMMANDS section
F-102: `_construct_manpage_specific_structure` 在环境变量 `INCLUDE_DEBUG_SECTION` 存在时输出JSON调试信息（第410-420行）
F-103: 方法 `_format_positional_arguments(self, parser_info)` 定义于第423-445行，将位置参数格式化为option_list
F-104: 方法 `_format_optional_arguments(self, parser_info)` 定义于第447-475行，将可选参数格式化为option_list，非suppress的默认值显示为 `=default`
F-105: 方法 `_format_subcommands(self, parser_info)` 定义于第477-493行，将子命令格式化为definition_list
F-106: 方法 `_nested_parse_paragraph(self, text)` 定义于第495-498行，使用 `self.state.nested_parse` 解析RST文本为paragraph节点
F-107: 属性 `_srcdir` 定义于第500-506行，返回 `self.env.srcdir`
F-108: 方法 `_open_filename(self)` 定义于第508-526行，打开 `:filename:` 指定的文件，相对路径相对于 `_srcdir` 解析
F-109: 方法 `_print_subcommands(self, data, nested_content, markdown_help=False, settings=None)` 定义于第528-609行，是新版子命令渲染方法（使用Sphinx域系统注册命令）
F-110: `_print_subcommands` 使用 `command_pos_args` 生成完整命令名作为anchor ID（第544-547行、第556-557行）
F-111: `_print_subcommands` 通过 `domain.add_argparse_command` 注册命令到域（第569行）
F-112: `_print_subcommands` 根据配置 `sphinxarg_full_subcommand_name` 决定子命令标题显示完整命令名还是短名（第563-566行）
F-113: 方法 `_print_action_groups(...)` 定义于第611-718行，是新版action group渲染方法，使用 `make_id` 生成唯一ID
F-114: 静态方法 `_is_suppressed` 定义于第720-726行
F-115: 方法 `run(self)` 定义于第728-855行，是指令执行入口
F-116: `run()` 支持三种指定parser的方式：`:module:+:func:`、`:ref:`、`:filename:+:func:`（第729-746行）
F-117: `run()` 在非filename模式下使用 `mock(self.config.autodoc_mock_imports)` 上下文导入模块（第750-766行）
F-118: `run()` 支持三种获取parser的方式：直接使用ArgumentParser实例、`:passparser:` 标志传递parser给函数、调用函数返回parser（第768-774行）
F-119: `run()` 调用 `parse_parser(parser, ...)` 解析parser，参数包括 `skip_default_values`（:nodefault:）、`skip_default_const_values`（:nodefaultconst:）、`color`（:color:）（第781-786行）
F-120: `run()` 调用 `parser_navigate(result, path)` 导航到指定子命令路径（第787行）
F-121: `run()` 在指定 `:manpage:` 时返回man page结构（第788-789行）
F-122: `run()` 在指定 `:markdown:` 时使用 `parse_markdown_block` 解析嵌套内容，否则用RST nested_parse（第793-800行）
F-123: `run()` 在指定 `:markdownhelp:` 时启用Markdown渲染帮助文本（第807-808行）
F-124: `run()` 解析 `:index-groups:` 为逗号分隔的组列表（第815-818行）
F-125: `run()` 为主命令创建target节点并注册到域（第820-828行）
F-126: `run()` 输出usage代码块（第830行）
F-127: `run()` 调用 `_print_action_groups` 渲染选项组（第831-839行）
F-128: `run()` 在无 `:nosubcommands:` 时调用 `_print_subcommands` 渲染子命令（第840-848行）
F-129: `run()` 在有epilog且无 `:noepilog:` 时解析并输出epilog（第849-850行）
F-130: `run()` 最后调用 `ensure_unique_ids(items)` 确保ID唯一（第853行）

## ext.py 模块 - 索引类

F-131: 类 `CommandsIndex(Index)` 定义于 ext.py 第858-871行
F-132: `CommandsIndex.name = 'index'`，`localname = 'Commands Index'`（第859-860行）
F-133: `CommandsIndex.generate(docnames=None)` 返回按命令首字母分组的 `IndexEntry` 列表（第862-871行）
F-134: 类 `CommandsByGroupIndex(Index)` 定义于 ext.py 第874-890行
F-135: `CommandsByGroupIndex.name = 'by-group'`，`localname = 'Commands by Group'`（第876-877行）
F-136: `CommandsByGroupIndex.generate(docnames=None)` 按 `commands-by-group` 数据分组返回 IndexEntry 列表（第879-890行）

## ext.py 模块 - ArgParseDomain 类

F-137: 类 `ArgParseDomain(Domain)` 定义于 ext.py 第893行
F-138: `ArgParseDomain.name = 'commands'`（第894行）
F-139: `ArgParseDomain.label = 'commands-label'`（第895行）
F-140: `ArgParseDomain.roles = {'command': XRefRole()}`（第897-899行），定义 `:command:` 交叉引用角色
F-141: `ArgParseDomain.indices = []`（第900行，初始为空，在configure_ext中动态添加）
F-142: `ArgParseDomain.initial_data = {'commands': [], 'commands-by-group': {}}`（第901-904行）
F-143: `ArgParseDomain.temporary_index_files: list[Path] = []`（第909行，类属性，跟踪临时索引文件）
F-144: 方法 `get_objects(self)` 定义于第911-912行，yield from `self.data['commands']`
F-145: 方法 `clear_doc(self, docname)` 定义于第914-932行，清除指定文档的命令数据（支持并行构建）
F-146: 方法 `merge_domaindata(self, docnames, otherdata)` 定义于第934-949行，合并并行构建的子进程数据
F-147: 方法 `resolve_xref(self, env, fromdocname, builder, typ, target, node, contnode)` 定义于第951-976行，解析 `:command:` 交叉引用
F-148: `resolve_xref` 使用 `target_to_anchor_id` 将目标转换为anchor ID进行匹配（第961行）
F-149: 方法 `add_argparse_command(self, result, anchor, groups=())` 定义于第978-991行，添加命令到域数据
F-150: `add_argparse_command` 创建条目元组 `(full_command, desc, 'command', docname, anchor, 0)`（第982行）
F-151: `add_argparse_command` 将条目添加到 `commands` 列表，并按groups添加到 `commands-by-group` 字典（第983-991行）

## ext.py 模块 - 扩展配置与setup

F-152: 函数 `_delete_temporary_files(app, _err)` 定义于第994-998行，在build-finished事件中删除临时索引文件
F-153: 函数 `_create_temporary_dummy_file(app, domain, docname, title)` 定义于第1001-1022行，创建临时RST文件以支持索引加入toctree
F-154: `_create_temporary_dummy_file` 在目标文件已存在时抛出 `ExtensionError`（第1006-1010行）
F-155: 函数 `configure_ext(app)` 定义于第1025-1050行，在builder-inited事件中配置索引
F-156: `configure_ext` 根据配置决定是否将 `CommandsIndex` 和 `CommandsByGroupIndex` 添加到domain.indices（第1043-1047行）
F-157: 函数 `setup(app)` 定义于第1053-1079行，是Sphinx扩展入口点
F-158: `setup()` 调用 `app.setup_extension('sphinx.ext.autodoc')` 加载autodoc扩展（第1054行）
F-159: `setup()` 调用 `app.add_domain(ArgParseDomain)` 注册commands域（第1055行）
F-160: `setup()` 调用 `app.add_directive('argparse', ArgParseDirective)` 注册argparse指令（第1056行）
F-161: `setup()` 注册7个配置值（第1060-1071行）：
  - `sphinxarg_full_subcommand_name`（bool，默认False）
  - `sphinxarg_build_commands_index`（bool，默认False）
  - `sphinxarg_commands_index_in_toctree`（bool，默认False）
  - `sphinxarg_build_commands_by_group_index`（bool，默认False）
  - `sphinxarg_commands_by_group_index_in_toctree`（bool，默认False）
  - `sphinxarg_commands_by_group_index_file_suffix`（str，默认'by-group'）
  - `sphinxarg_commands_by_group_index_title`（str，默认'Commands by Group'）
F-162: `setup()` 连接 `builder-inited` 事件到 `configure_ext`（第1073行）
F-163: `setup()` 连接 `build-finished` 事件到 `_delete_temporary_files`（第1074行）
F-164: `setup()` 返回字典包含 `version`、`parallel_read_safe: True`、`parallel_write_safe: True`（第1075-1079行）

## 指令选项汇总（来自ext.py option_spec和usage.rst文档）

F-165: `:module:` - 模块名（字符串，unchanged）
F-166: `:func:` - 函数名（字符串，unchanged），函数返回ArgumentParser实例或接受parser参数（配合:passparser:）
F-167: `:ref:` - 组合形式的module.func引用（字符串，unchanged）
F-168: `:prog:` - 工具显示名称（字符串，unchanged），覆盖parser.prog
F-169: `:path:` - 子命令路径（字符串，unchanged），空格分隔导航到嵌套子命令
F-170: `:nodefault:` - 标志选项（flag），不显示默认值
F-171: `:nodefaultconst:` - 标志选项（flag），仅对store_const/store_true/store_false类型不显示默认值
F-172: `:filename:` - 文件名（字符串，unchanged），直接exec文件而非import模块
F-173: `:manpage:` - 字符串选项，生成man page格式输出
F-174: `:nosubcommands:` - 字符串选项，不渲染子命令部分
F-175: `:passparser:` - 标志选项（flag），函数接受parser参数而非返回parser
F-176: `:noepilog:` - 字符串选项，不解析epilog
F-177: `:nodescription:` - 字符串选项，不解析description
F-178: `:markdown:` - 标志选项（flag），嵌套内容使用Markdown语法
F-179: `:markdownhelp:` - 标志选项（flag），程序描述和选项帮助使用Markdown解析
F-180: `:color:` - 标志选项（flag），启用ANSI颜色输出（Python 3.14+ argparse）
F-181: `:index-groups:` - 字符串选项，逗号分隔的分组名，值传入 `domain.add_argparse_command` 的groups参数
