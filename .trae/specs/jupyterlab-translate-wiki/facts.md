# jupyterlab-translate 事实清单（R阶段）

> 采集时间：2026-08-22
> 源码路径：`d:\spaces\SpecWeave\external\libs\jupyter\jupyterlab-translate`
> 版本：1.3.7

## 项目基本信息

F-001: 包名 `jupyterlab-translate`（PyPI），定义于 `pyproject.toml` 第6行 `name = "jupyterlab-translate"`
F-002: Python包模块名为 `jupyterlab_translate`，所有源码位于 `jupyterlab_translate/` 目录
F-003: 版本号 `__version__ = "1.3.7"`，定义于 `jupyterlab_translate/__init__.py` 第6行
F-004: 描述为 "JupyterLab Language Pack Translations Helper"，定义于 `pyproject.toml` 第7行
F-005: NPM包名为 `@jupyterlab/translate`，版本1.0.0，private: true，定义于 `package.json`
F-006: 构建后端使用 `hatchling.build`，定义于 `pyproject.toml` 第3行
F-007: Python版本要求 `>=3.7`，定义于 `pyproject.toml` 第23行
F-008: License为BSD-3-Clause（LICENSE.txt）

## 入口点（Entry Points）

F-009: CLI命令 `jupyterlab-translate` 指向 `jupyterlab_translate.cli:main`，定义于 `pyproject.toml` 第50行
F-010: CLI命令 `gettext-extract` 指向 `jupyterlab_translate.gettext_extract:main`，定义于 `pyproject.toml` 第51行
F-011: Hatch构建钩子入口 `jupyter-translate` 指向 `jupyterlab_translate.hooks`，定义于 `pyproject.toml` 第53-54行
F-012: `hatch_register_build_hook()` 函数在 `jupyterlab_translate/hooks.py` 中，返回 `JupyterLanguageBuildHook` 类（第8-10行）

## 依赖项

F-013: 核心Python依赖：babel, click, copier>=9.2.0, copier-templates-extensions, crowdin-api-client, hatchling>=1.5, jinja2-time, polib, pydantic, requests（`pyproject.toml` 第24-36行）
F-014: 可选test依赖：hatch, pre-commit, pytest, pytest-cov
F-015: NPM devDependencies：@vercel/ncc ^0.30.0, gettext-extract ^2.0.1, rimraf ^3.0.2
F-016: Python 3.7-3.9需要 `importlib-metadata>=4.8.3`（条件依赖）

## 模块结构

### jupyterlab_translate/__init__.py

F-017: 从 `.finder` 导入 `get_installed_language_packs` 和 `get_language_pack`（第3-4行）
F-018: 定义 `__version__ = "1.3.7"`（第6行）

### jupyterlab_translate/constants.py

F-019: `TEMPLATE_URL = "https://github.com/jupyterlab/jupyterlab-language-pack-cookiecutter"`（第11行）
F-020: `TEMPLATE_REF = "master"`（第12行）
F-021: `EXTENSIONS_FOLDER = "extensions"`（第13行）
F-022: `JUPYTERLAB = "jupyterlab"`（第14行）
F-023: `LANG_PACKS_FOLDER = "language-packs"`（第15行）
F-024: `LC_MESSAGES = "LC_MESSAGES"`（第16行）
F-025: `LOCALE_FOLDER = "locale"`（第17行）
F-026: `TRANSLATIONS_FOLDER = "translations"`（第18行）
F-027: `__build_parsers()` 函数返回 `List[dict]`，构建gettext JS解析器配置（第21-43行）
F-028: JS解析器roots集合：`{"trans", "this.trans", "this._trans", "this.props.trans", "props.trans"}`（第23行）
F-029: JS翻译函数列表包含8个函数定义：__, gettext, _n, ngettext, _p, pgettext, _np, npgettext（第24-36行）
F-030: `GETTEXT_CONFIG` 字典包含js/headers/output三个键（第46-59行）
F-031: GETTEXT_CONFIG中js.glob.pattern为 `"**/*.ts*(x)"`，匹配.ts和.tsx文件（第50-51行）
F-032: GETTEXT_CONFIG中js.glob.options.ignore忽略examples/**/*.ts*(x), **/*.spec.ts, node_modules/**/*.ts*(x)（第52行）

### jupyterlab_translate/cli.py

F-033: CLI使用click框架，`main()` 函数用 `@click.group()` 装饰（第39-48行）
F-034: `extract` 子命令接受 `package_repo_dir`（Path类型，必须存在）和 `project` 参数（第53-61行）
F-035: `update` 子命令接受 `package_repo_dir`, `project`, `--locales/-l`（multiple=True）参数（第63-71行）
F-036: `update_contributors` 子命令接受 `package_repo_dir` 参数，需要 `CROWDIN_API_KEY` 环境变量（第74-102行）
F-037: `compile` 子命令接受 `package_repo_dir`, `project`, `--locales/-l` 参数（第105-111行）
F-038: `extract_pack` 子命令接受 `package_repo_dir`, `language_packs_repo_dir`, `project` 参数（第116-126行）
F-039: `update_pack` 子命令接受 `package_repo_dir`, `language_packs_repo_dir`, `project`, `--locales/-l` 参数（第129-140行）
F-040: `compile_pack` 子命令接受 `language_packs_repo_dir`, `project`, `--locales/-l` 参数（第143-150行）
F-041: `package_repo_dir_arg` 定义为 `click.argument("package_repo_dir", type=click.Path(exists=True, path_type=Path))`（第26-28行）
F-042: `lang_packs_repo_dir_arg` 定义为 `click.argument("language_packs_repo_dir", type=click.Path(exists=True))`（第23-25行）

### jupyterlab_translate/api.py

F-043: `check_locales(locales: List[str])` 函数遍历locales列表，对每个locale调用 `check_locale()`，无效则抛出ValueError（第25-38行）
F-044: `normalize_project(project: str) -> str` 将project名转小写、`-`替换为`_`（第41-50行）
F-045: `extract_package(package_repo_dir, project, merge: bool = True)` 规范化project名，调用 `extract_translations()`（第53-66行）
F-046: `update_package(package_repo_dir, project, locales)` 校验locales，规范化project名，调用 `update_translations()`（第69-84行）
F-047: `compile_package(package_repo_dir, project, locales)` 校验locales，调用 `compile_translations()`，然后对每个po文件调用 `convert_catalog_to_json()` 和 `compile_to_mo()`（第87-100行）
F-048: `extract_language_pack(package_repo_dir, language_packs_repo_dir, project, merge: bool = True)` 当project=="jupyterlab"时output_dir在language_packs_repo_dir/jupyterlab，否则在extensions/子目录（第103-121行）
F-049: `update_language_pack(...)` 当project=="jupyterlab"时output_dir在language_packs_repo_dir/jupyterlab，否则在jupyterlab_extensions/子目录（第124-141行）
F-050: `compile_po_file(po_path: Path)` 删除旧的.json和.mo文件，调用 `convert_catalog_to_json()` 和 `compile_to_mo()`（第144-156行）
F-051: `compile_language_pack(...)` 编译翻译后，将.mo和.json文件移动到language-packs目录结构中（第159-209行）
F-052: language pack包名格式为 `jupyterlab-language-pack-{locale}`，locale中`_`替换为`-`（第185行）
F-053: language pack内部Python包名将`-`替换为`_`（第187行）

### jupyterlab_translate/utils.py

F-054: `HERE = Path(__file__).parent`（第34行）
F-055: `get_version(repo_root_path: Path, project: str) -> str` 按优先级获取版本：1)setup.py --version 或 hatch version，2)package.json中的version，3)git describe --tags（第38-89行）
F-056: `create_new_language_pack(output_dir, locale, template_url=TEMPLATE_URL, template_ref=TEMPLATE_REF, version="0.1.post0")` 使用copier从模板创建新的语言包（第92-125行）
F-057: `check_locale(locale: str) -> bool` 使用 `babel.Locale.parse()` 验证locale，特例白名单：`ach_UG`, `no_NO`（第128-141行）
F-058: `find_locales(output_dir: Path) -> Tuple[str]` 在output_dir/locale/下查找有效locale目录（第144-162行）
F-059: `find_packages_source_files(packages_path) -> Dict[str, List[Path]]` 遍历packages_path下的每个包，调用 `find_source_files()`（第167-185行）
F-060: `find_source_files(path, extensions={".ts",".tsx",".py"}, skip_folders={"tests","test","node_modules","lib",".git",".ipynb_checkpoints"})` 递归查找源文件，跳过指定目录（第188-220行）
F-061: `extract_tsx_strings(input_path) -> List[Dict]` 使用gettext-extract命令行工具从TS/TSX文件提取字符串，返回条目列表（第225-278行）
F-062: `extract_tsx_strings()` 通过临时文件写入GETTEXT_CONFIG JSON配置，调用 `gettext-extract --config <config>`（第237-247行）
F-063: `extract_tsx_strings()` 使用polib.pofile读取生成的.pot文件（第254行）
F-064: `get_line(lines: List[str], value: str) -> str` 在lines列表中查找value最后一次出现的行号（第281-299行）
F-065: `DEFAULT_SCHEMA_SELECTORS` 字典定义了JSON schema中需要翻译的字段路径模式到翻译上下文的映射（第306-319行）
F-066: 默认schema上下文：title→"schema"，description→"schema"，properties/*/title→"settings"，properties/*/description→"settings"（第307-312行）
F-067: JupyterLab特定schema选择器包含：jupyter.lab.setting-icon-label→"settings"，jupyter.lab.menus/*/label→"menu"等（第314-318行）
F-068: `_prepare_schema_patterns(schema: dict) -> Dict[Pattern, str]` 合并DEFAULT_SCHEMA_SELECTORS和schema中jupyter.lab.internationalization.selectors定义的自定义选择器，编译为正则表达式（第322-335行）
F-069: `_extract_schema_strings(schema, ref_path, prefix="", to_translate=None)` 递归遍历JSON schema字典，对匹配to_translate正则模式的字符串值生成翻译条目（第338-384行）
F-070: `extract_schema_strings(input_path) -> List[Dict]` 查找package.json中的jupyterlab.schemaDir指定的schema目录，提取其中所有.json文件的可翻译字符串（第387-417行）
F-071: `extract_strings(input_paths, output_path, project, version) -> Path` 调用 `pybabel extract` 命令从Python文件提取字符串（第420-450行）
F-072: `extract_strings()` 使用 `pybabel_config.cfg` 作为mapping文件（第435行）
F-073: `fix_location(path_to_remove, pot_path, append_entries=None) -> Dict[str, str]` 使用polib读取.pot文件，将绝对路径转换为相对路径，规范化路径分隔符为`/`，可选追加条目，返回metadata（第453-500行）
F-074: `remove_duplicates(pot_path: Path, metadata: Dict[str, str])` 去重POT文件中的条目，合并重复条目的occurrences（第503-571行）
F-075: `remove_duplicates()` 去重key为 `(msgctxt, msgid, msgid_plural)` 三元组（第525行）
F-076: `create_catalog(repo_root_dir, locale_dir, project, version, merge=True) -> Tuple[Path, Dict[str, str]]` 创建POT目录：提取Python字符串→提取TS/TSX字符串→提取schema字符串→合并→去重（第574-621行）
F-077: `create_catalog()` 在临时目录中操作，最后复制到最终pot_path（第594-619行）
F-078: `create_catalog()` merge=True时使用 `xgettext` 命令合并新旧POT文件（第606-615行）
F-079: `update_catalogs(pot_path, output_dir, locale) -> Path` 调用pybabel init或update创建/更新PO文件（第624-656行）
F-080: `update_catalogs()` PO文件路径为 `{output_dir}/{locale}/LC_MESSAGES/{domain}.po`（第642行）
F-081: `compile_catalog(locale_dir, domain, locale) -> Path` 调用 `pybabel compile` 编译PO文件，返回PO文件路径（第659-681行）
F-082: `compile_to_mo(po_path: Path) -> Path` 使用polib的 `save_as_mofile()` 将.po编译为.mo（第684-695行）
F-083: `extract_translations(repo_root_dir, output_dir, project, merge=True) -> Path` 高层API：获取版本→创建locale目录→创建catalog→去重（第700-728行）
F-084: `update_translations(repo_root_dir, output_dir, project, locales=None)` 高层API：查找locales→获取版本→创建catalog→去重→对每个locale更新PO文件→更新版本信息（第731-762行）
F-085: `compile_translations(output_dir, project, locales=None) -> Dict[str, Path]` 高层API：查找locales→对每个locale调用compile_catalog，返回locale→po_path映射（第765-786行）
F-086: `update_version(po_path, project, version) -> Path` 更新PO文件metadata中的Project-Id-Version字段（第789-798行）

### jupyterlab_translate/converters.py

F-087: `convert_catalog_to_json(po_path: Path, output_dir: Path, project: str) -> Path` 将PO文件转换为Jed JSON格式（第9-68行）
F-088: Jed JSON格式顶层key `""` 包含metadata：domain, version, language, plural_forms（第28-35行）
F-089: version从PO metadata的Project-Id-Version中取最后一个空格后的部分（第32行）
F-090: language从PO metadata的Language字段获取，`_`替换为`-`（第33行）
F-091: 有msgctxt的条目key格式为 `{msgctxt}\x04{msgid}`（第49行，\x04为EOT控制字符）
F-092: 无msgctxt的条目key为msgid本身（第51行）
F-093: 有翻译的条目值为 `[msgstr]`（单元素列表）（第54行）
F-094: 复数形式条目值为所有msgstr_plural值的列表（第55-64行）
F-095: 单复数形式语言（如韩语nplurals=1）的复数列表追加一个空字符串以满足JupyterLab前端校验（第60-64行）
F-096: 转换时会合并已有的JSON文件（保留旧翻译字符串）（第38-42行）
F-097: obsolete条目不写入JSON（第45-46行）

### jupyterlab_translate/finder.py

F-098: `JUPYTERLAB_LANGUAGEPACK_ENTRY = "jupyterlab.languagepack"`（第16行）
F-099: `JUPYTERLAB_LOCALE_ENTRY = "jupyterlab.locale"`（第17行）
F-100: `merge_data()` 函数体为空（pass），未实现（第20-23行）
F-101: `get_installed_packages_locale(locale: str) -> dict` 通过 `jupyterlab.locale` entry point查找所有包含locale数据的已安装包，返回{package_name: {locale: json_data}}（第26-66行）
F-102: `get_installed_language_packs() -> list` 通过 `jupyterlab.languagepack` entry point返回所有已安装语言包名称列表（第69-81行）
F-103: `get_language_pack(locale: str) -> dict` 通过 `jupyterlab.languagepack` entry point查找指定locale的语言包数据，返回Jed格式dict（第84-101行）
F-104: finder.py在Python<3.10时使用 `importlib_metadata.entry_points`，>=3.10时使用标准库 `importlib.metadata.entry_points`（第8-11行）

### jupyterlab_translate/plugin.py

F-105: `JupyterLanguageBuildHook` 继承自 `hatchling.builders.hooks.plugin.interface.BuildHookInterface`（第21行）
F-106: `PLUGIN_NAME = "jupyter-translate"`（第24行）
F-107: `COMPILATION_THRESHOLD = 0`（第17行）—编译阈值百分比
F-108: `PACKAGE_PREFIX = "jupyterlab_language_pack_"`（第18行）
F-109: `_get_locale_name()` 方法通过glob查找 `jupyterlab_language_pack_??_??` 或 `jupyterlab_language_pack_???_??` 格式的目录，返回messages_folder路径和locale_name（第26-41行）
F-110: `clean(versions)` 方法删除messages_folder中所有.json和.mo文件（第43-55行）
F-111: `initialize(version, build_data)` 方法在wheel构建时编译PO文件为.json和.mo；非wheel构建时更新贡献者列表（第57-98行）
F-112: initialize()在wheel构建时，遍历所有.po文件，检查翻译百分比是否>=COMPILATION_THRESHOLD，满足则调用 `compile_po_file()`（第67-81行）
F-113: initialize()非wheel构建时，如果有CROWDIN_API_KEY环境变量则更新CONTRIBUTORS.md（第85-96行）

### jupyterlab_translate/gettext_extract.py

F-114: `INDEX_JS = HERE / "index.js"` 指向同目录下打包的ncc产物（第9行）
F-115: `main()` 将命令行参数转发给 `node <index.js>` 执行（第12-14行）

### jupyterlab_translate/contributors.py

F-116: `CONTRIBUTORS = "CONTRIBUTORS.md"`（第17行）
F-117: `FirstCrowdinClient` 继承自 `crowdin_api.CrowdinClient`，设置TOKEN从 `CROWDIN_API_KEY` 环境变量，PAGE_SIZE=100000（第20-22行）
F-118: 模块级 `client = FirstCrowdinClient()` 实例（第25行）
F-119: `get_project_data(project_id=409874)` 调用 `client.projects.get_project(project_id)` 返回data字段（第28-43行）
F-120: `get_languages(project_data)` 从project_data的targetLanguages提取locale→{id,name}映射（第46-64行）
F-121: `download_data(project_id=409874, language_id=None)` 生成Crowdin顶级成员报告（CSV格式），等待后下载（第67-107行）
F-122: `format_data(data, language=None)` 解析Crowdin CSV报告，格式化为Markdown贡献者列表（第110-167行）
F-123: `get_contributors_report(project_id=409874, locale=None, crowdin_key=None) -> str` 整合流程：获取项目→获取语言ID→下载数据→格式化（第170-210行）
F-124: 默认Crowdin项目ID为409874（JupyterLab官方项目）（第28行）
F-125: 报告时间起始点为2019-04-01（第83行）

### jupyterlab_translate/pybabel_config.cfg

F-126: Python提取配置：`[python: **.py]`，提取函数为 `trans.gettext, trans.pgettext, trans.ngettext, trans.npgettext, trans.__, trans._p, trans._n, trans._np`（第1-2行）

### jupyterlab_translate/index.js

F-127: index.js是通过 `ncc build node_modules/gettext-extract/bin/gettext-extract -o jupyterlab_translate --minify` 生成的monolithic JS文件

## 数据格式

F-128: POT/PO文件使用polib库操作
F-129: PO文件路径约定：`{output_dir}/{locale}/LC_MESSAGES/{domain}.po`
F-130: MO文件与PO文件同目录，扩展名为.mo
F-131: JSON文件（Jed格式）与PO文件同目录，扩展名为.json
F-132: 独立扩展包的locale目录在 `{package_dir}/{project}/locale/` 下
F-133: 语言包的locale目录在 `jupyterlab_language_pack_{locale}/locale/{locale_with_underscore}/LC_MESSAGES/` 下
F-134: 语言包Python包名格式：`jupyterlab_language_pack_{locale_with_underscore}`（如jupyterlab_language_pack_ko_KR）
F-135: 语言包pip包名格式：`jupyterlab-language-pack-{locale_with_dash}`（如jupyterlab-language-pack-ko-KR）

## CLI命令汇总

F-136: 独立扩展包流程：extract → update → compile
F-137: 语言包流程：extract_pack → update_pack → compile_pack
F-138: extract命令签名：`jupyterlab-translate extract <JLAB-EXTENSION-DIR> <JLAB-EXTENSION-NAME>`
F-139: update命令签名：`jupyterlab-translate update <JLAB-EXTENSION-DIR> <JLAB-EXTENSION-NAME> [-l <locale> ...]`
F-140: compile命令签名：`jupyterlab-translate compile <JLAB-EXTENSION-DIR> <JLAB-EXTENSION-NAME> [-l <locale> ...]`

## 测试

F-141: test_utils.py包含：test_create_catalog_with_merge, test_create_catalog_without_merge, test_extract_from_settings（第33-95行）
F-142: test_hatch_hook.py测试hatch构建钩子，验证wheel中包含.json和.mo文件、sdist中包含.po文件（第145-217行）
F-143: dummy_pkg测试包包含：locale/dummy_pkg.pot, src/documentwidget.ts
