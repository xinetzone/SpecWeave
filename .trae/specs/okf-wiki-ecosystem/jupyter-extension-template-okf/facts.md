# JupyterLab Extension Template - 事实清单（Facts）

> R阶段产出。零推测原则：只记录代码中存在的事实，不包含推断性表述。

## F-001 ~ F-010: 模板基础配置

F-001: copier.yml 中声明 `_min_copier_version: "7.1.0"`，文件路径 `external/libs/jupyter/extension-template/copier.yml:1`
F-002: copier.yml 中声明 `_subdirectory: template`，文件路径 `external/libs/jupyter/extension-template/copier.yml:2`
F-003: copier.yml 中声明 `_jinja_extensions` 包含 `jinja2_time.TimeExtension`，文件路径 `external/libs/jupyter/extension-template/copier.yml:3-4`
F-004: README.md 中声明安装命令 `pip install "copier~=9.2" jinja2-time`，文件路径 `external/libs/jupyter/extension-template/README.md:19`
F-005: README.md 中声明 conda 安装命令 `conda install -c conda-forge "copier>=9.2,<10" jinja2-time`，文件路径 `external/libs/jupyter/extension-template/README.md:25`
F-006: README.md 中声明使用命令 `copier copy --trust https://github.com/jupyterlab/extension-template .`，文件路径 `external/libs/jupyter/extension-template/README.md:38`
F-007: README.md 中声明更新命令 `copier update --trust`，文件路径 `external/libs/jupyter/extension-template/README.md:66`
F-008: README.md 中列出四种扩展类型：frontend、mimerenderer、frontend-and-server、theme，文件路径 `external/libs/jupyter/extension-template/README.md:7-10`
F-009: 模板目录为 `template/`，包含 `.jinja` 后缀文件和非模板文件（如 CHANGELOG.md、babel.config.js、jest.config.js、ui-tests/playwright.config.js、ui-tests/yarn.lock、style/base.css、style/index.js、ui-tests/jupyter_server_test_config.py、ui-tests/README.md、.github/workflows/enforce-label.yml、.github/workflows/prep-release.yml、.github/workflows/publish-release.yml）
F-010: LICENSE.jinja 使用 BSD 3-Clause License，版权年份通过 `{% now 'utc', '%Y' %}` 动态生成，文件路径 `template/LICENSE.jinja:1-3`

## F-011 ~ F-030: Copier 参数定义（copier.yml）

F-011: `kind` 参数类型为 str，默认值 `frontend`，可选值为 `[frontend, mimerenderer, frontend-and-server, theme]`，文件路径 `copier.yml:6-14`
F-012: `author_name` 参数类型为 str，placeholder 为 "My Name"，validator 使用正则 `^[^\s].*$` 禁止空字符串或以空白开头，文件路径 `copier.yml:16-23`
F-013: `author_email` 参数类型为 str，默认值为空字符串，validator 使用 email 正则校验，文件路径 `copier.yml:25-34`
F-014: `labextension_name` 参数类型为 str，默认值 `{% if kind == 'theme' %}mytheme{% else %}myextension{% endif %}`，文件路径 `copier.yml:36-39`
F-015: `python_name` 参数类型为 str，默认值 `"{{ labextension_name | replace('-', '_') | replace('/', '_') | trim('@') }}"`，文件路径 `copier.yml:41-44`
F-016: `project_short_description` 参数类型为 str，默认值 "A JupyterLab extension."，文件路径 `copier.yml:46-49`
F-017: `has_settings` 参数类型为 bool，条件 `when: "{{ kind != 'mimerenderer' }}"`，默认值 no，文件路径 `copier.yml:51-55`
F-018: `has_binder` 参数类型为 bool，默认值 no，文件路径 `copier.yml:57-60`
F-019: `advanced` 参数类型为 bool，默认值 no，文件路径 `copier.yml:62-65`
F-020: `yarn_linker` 参数类型为 str，条件 `when: "{{ advanced }}"`，可选值 `[node-modules, pnpm]`，默认值 node-modules，文件路径 `copier.yml:67-74`
F-021: `test` 参数类型为 bool，默认值 yes，文件路径 `copier.yml:76-79`
F-022: `has_ai_rules` 参数类型为 bool，默认值 no，文件路径 `copier.yml:81-84`
F-023: `create_claude_symlink` 参数类型为 bool，条件 `when: "{{ has_ai_rules }}"`，默认值 yes，文件路径 `copier.yml:86-90`
F-024: `create_gemini_symlink` 参数类型为 bool，条件 `when: "{{ has_ai_rules }}"`，默认值 yes，文件路径 `copier.yml:92-96`
F-025: `repository` 参数类型为 str，placeholder 为 https://github.com/github_username/my-extension，文件路径 `copier.yml:98-101`
F-026: `viewer_name` 参数类型为 str，条件 `when: "{{ kind == 'mimerenderer' }}"`，文件路径 `copier.yml:103-108`
F-027: `mimetype` 参数类型为 str，条件 `when: "{{ kind == 'mimerenderer' }}"`，placeholder 为 "application/vnd.my_organization.my_type"，文件路径 `copier.yml:110-115`
F-028: `mimetype_name` 参数类型为 str，条件 `when: "{{ kind == 'mimerenderer' }}"`，placeholder 为 my_type，文件路径 `copier.yml:117-122`
F-029: `file_extension` 参数类型为 str，条件 `when: "{{ kind == 'mimerenderer' }}"`，placeholder 为 .my_type，文件路径 `copier.yml:124-129`
F-030: `data_format` 参数类型为 str，条件 `when: "{{ kind == 'mimerenderer' }}"`，可选值 `[string, json]`，默认值 string，文件路径 `copier.yml:131-138`

## F-031 ~ F-040: Copier 后处理任务

F-031: `_tasks` 列表包含两个后处理命令，文件路径 `copier.yml:140-146`
F-032: 第一个任务执行 Python 命令创建 CLAUDE.md 符号链接到 AGENTS.md，条件 `when: "{{ has_ai_rules and create_claude_symlink }}"`，文件路径 `copier.yml:142-143`
F-033: 第二个任务执行 Python 命令创建 GEMINI.md 符号链接到 AGENTS.md，条件 `when: "{{ has_ai_rules and create_gemini_symlink }}"`，文件路径 `copier.yml:145-146`

## F-041 ~ F-060: package.json.jinja（NPM 包配置）

F-041: package.json.jinja 中 name 字段值为 `"{{ labextension_name }}"`，版本 "0.1.0"，文件路径 `template/package.json.jinja:2-3`
F-042: package.json.jinja 中 license 字段为 "BSD-3-Clause"，文件路径 `template/package.json.jinja:14`
F-043: package.json.jinja 中 files 字段包含 `lib/**/*.{d.ts,eot,gif,html,jpg,js,js.map,json,png,svg,woff2,ttf}`、`style/**/*.{css,js,eot,gif,html,jpg,json,png,svg,woff2,ttf}`、`src/**/*.{ts,tsx}`，条件包含 `schema/*.json` 当 has_settings 为 true，文件路径 `template/package.json.jinja:19-24`
F-044: package.json.jinja 中 main 字段为 "lib/index.js"，types 为 "lib/index.d.ts"，文件路径 `template/package.json.jinja:25-26`
F-045: package.json.jinja 中 style 字段条件存在：kind != 'theme' 时为 "style/index.css"，文件路径 `template/package.json.jinja:27`
F-046: package.json.jinja scripts.build 值为 "jlpm build:lib && jlpm build:labextension:dev"，文件路径 `template/package.json.jinja:33`
F-047: package.json.jinja scripts.build:prod 值为 "jlpm clean && jlpm build:lib:prod && jlpm build:labextension"，文件路径 `template/package.json.jinja:34`
F-048: package.json.jinja scripts.build:labextension 值为 "jupyter-builder build ."，文件路径 `template/package.json.jinja:35`
F-049: package.json.jinja scripts.build:labextension:dev 值为 "jupyter-builder build --development True ."，文件路径 `template/package.json.jinja:36`
F-050: package.json.jinja scripts.build:lib 值为 "tsc --sourceMap"，build:lib:prod 值为 "tsc"，文件路径 `template/package.json.jinja:37-38`
F-051: package.json.jinja scripts.watch 值为 "run-p watch:src watch:labextension"，watch:src 值为 "tsc -w --sourceMap"，watch:labextension 值为 "jupyter-builder watch ."，文件路径 `template/package.json.jinja:55-57`
F-052: package.json.jinja scripts.test 条件存在：test 为 true 时值为 "jest --coverage"，文件路径 `template/package.json.jinja:54`
F-053: package.json.jinja dependencies 条件分支：非 mimerenderer 时依赖 `@jupyterlab/application: ^4.0.0`；theme 额外依赖 `@jupyterlab/apputils: ^4.0.0`；frontend-and-server 额外依赖 `@jupyterlab/coreutils: ^6.0.0` 和 `@jupyterlab/services: ^7.0.0`；has_settings 时额外依赖 `@jupyterlab/settingregistry: ^4.0.0`；mimerenderer 时依赖 `@jupyterlab/rendermime-interfaces: ^3.8.0` 和 `@lumino/widgets: ^2.1.0`，文件路径 `template/package.json.jinja:59-66`
F-054: package.json.jinja devDependencies 包含 `@eslint/js: ^9.0.0`、`@jupyter/builder: ^1.2.0`、`@jupyter/eslint-plugin: ^1.1.0`、typescript: "~5.5.4" 等，文件路径 `template/package.json.jinja:67-98`
F-055: package.json.jinja resolutions 固定 lib0 为 "0.2.111"、webpack 为 "5.106.0"，文件路径 `template/package.json.jinja:99-102`
F-056: package.json.jinja jupyterlab 字段条件分支：frontend-and-server 时包含 discovery.server.managers=["pip"] 和 base.name="{{ python_name }}"；mimerenderer 时 mimeExtension: true，其他类型 extension: true；outputDir 为 "{{python_name}}/labextension"；has_settings 时 schemaDir 为 "schema"；theme 时 themePath 为 "style/index.css"，文件路径 `template/package.json.jinja:112-128`
F-057: package.json.jinja publishConfig.access 为 "public"，文件路径 `template/package.json.jinja:109-111`
F-058: package.json.jinja sideEffects 条件分支：非 theme 时包含 "style/*.css" 和 "style/index.js"；theme 时仅包含 "style/*.css"，文件路径 `template/package.json.jinja:103-108`
F-059: package.json.jinja styleModule 仅在非 theme 时存在，值为 "style/index.js"，文件路径 `template/package.json.jinja:107`
F-060: package.json.jinja 包含 prettier 和 stylelint 配置节，文件路径 `template/package.json.jinja:129-161`

## F-061 ~ F-080: pyproject.toml.jinja（Python 包配置）

F-061: pyproject.toml.jinja build-system.requires 包含 `hatchling>=1.5.0`、`hatch-nodejs-version>=0.3.2`、`jupyter-builder>=1.2.0,<2`，build-backend 为 "hatchling.build"，文件路径 `template/pyproject.toml.jinja:1-3`
F-062: pyproject.toml.jinja project.name 为 "{{ python_name }}"，requires-python 为 ">=3.10"，文件路径 `template/pyproject.toml.jinja:5-10`
F-063: pyproject.toml.jinja project.license 为 "BSD-3-Clause"，文件路径 `template/pyproject.toml.jinja:8`
F-064: pyproject.toml.jinja project.classifiers 包含 "Framework :: Jupyter :: JupyterLab :: 4" 和 Python 3.10-3.14 分类器，文件路径 `template/pyproject.toml.jinja:11-26`
F-065: pyproject.toml.jinja project.dependencies 条件分支：frontend-and-server 时包含 "jupyter_server>=2.13.0,<3"，其他类型为空列表，文件路径 `template/pyproject.toml.jinja:27-29`
F-066: pyproject.toml.jinja project.dynamic 为 ["version", "description", "authors", "urls", "keywords"]，文件路径 `template/pyproject.toml.jinja:30`
F-067: pyproject.toml.jinja project.optional-dependencies.dev 包含 "jupyterlab>=4"、"jupyter-builder>=1.2.0"，文件路径 `template/pyproject.toml.jinja:33-36`
F-068: pyproject.toml.jinja project.optional-dependencies.test 条件存在：test 且 kind=='frontend-and-server' 时包含 coverage、pytest、pytest-asyncio、pytest-cov、pytest-jupyter[server]>=0.6.0，文件路径 `template/pyproject.toml.jinja:37-43`
F-069: pyproject.toml.jinja tool.hatch.version.source 为 "nodejs"，文件路径 `template/pyproject.toml.jinja:45-46`
F-070: pyproject.toml.jinja tool.hatch.metadata.hooks.nodejs.fields 为 ["description", "authors", "urls", "keywords"]，文件路径 `template/pyproject.toml.jinja:48-49`
F-071: pyproject.toml.jinja tool.hatch.build.targets.sdist.artifacts 包含 "{{ python_name }}/labextension"，exclude 为 [".github", "binder"]，文件路径 `template/pyproject.toml.jinja:51-53`
F-072: pyproject.toml.jinja tool.hatch.build.targets.wheel.shared-data 映射："{{ python_name }}/labextension" → "share/jupyter/labextensions/{{ labextension_name }}"，"install.json" → "share/jupyter/labextensions/{{ labextension_name }}/install.json"；frontend-and-server 时额外映射 "jupyter-config/server-config" → "etc/jupyter/jupyter_server_config.d"，文件路径 `template/pyproject.toml.jinja:55-58`
F-073: pyproject.toml.jinja tool.hatch.build.hooks.version.path 为 "{{ python_name }}/_version.py"，文件路径 `template/pyproject.toml.jinja:60-61`
F-074: pyproject.toml.jinja tool.hatch.build.hooks.jupyter-builder.dependencies 为 ["hatch-jupyter-builder>=0.5"]，build-function 为 "hatch_jupyter_builder.npm_builder"，文件路径 `template/pyproject.toml.jinja:63-65`
F-075: pyproject.toml.jinja tool.hatch.build.hooks.jupyter-builder.ensured-targets 包含 "{{ python_name }}/labextension/package.json"，非 theme 时额外包含 "{{ python_name }}/labextension/static/style.js"，文件路径 `template/pyproject.toml.jinja:66-69`
F-076: pyproject.toml.jinja tool.hatch.build.hooks.jupyter-builder.skip-if-exists 为 ["{{ python_name }}/labextension/static/style.js"]，文件路径 `template/pyproject.toml.jinja:70`
F-077: pyproject.toml.jinja tool.hatch.build.hooks.jupyter-builder.build-kwargs.build_cmd 为 "build:prod"，npm 为 ["jlpm"]，文件路径 `template/pyproject.toml.jinja:72-74`
F-078: pyproject.toml.jinja tool.hatch.build.hooks.jupyter-builder.editable-build-kwargs.build_cmd 为 "install:extension"，npm 为 ["jlpm"]，source_dir 为 "src"，build_dir 为 "{{python_name}}/labextension"，文件路径 `template/pyproject.toml.jinja:76-80`
F-079: pyproject.toml.jinja tool.jupyter-releaser.options.version_cmd 为 "hatch version"，文件路径 `template/pyproject.toml.jinja:82-83`
F-080: pyproject.toml.jinja tool.check-wheel-contents.ignore 为 ["W002"]，文件路径 `template/pyproject.toml.jinja:93-94`

## F-081 ~ F-100: TypeScript 前端入口（src/index.ts.jinja）

F-081: src/index.ts.jinja 非 mimerenderer 分支从 '@jupyterlab/application' 导入 JupyterFrontEnd、JupyterFrontEndPlugin，文件路径 `template/src/index.ts.jinja:1-4`
F-082: src/index.ts.jinja theme 分支从 '@jupyterlab/apputils' 导入 IThemeManager，文件路径 `template/src/index.ts.jinja:5-6`
F-083: src/index.ts.jinja has_settings 分支从 '@jupyterlab/settingregistry' 导入 ISettingRegistry，文件路径 `template/src/index.ts.jinja:7-8`
F-084: src/index.ts.jinja frontend-and-server 分支从 './request' 导入 requestAPI，文件路径 `template/src/index.ts.jinja:9-10`
F-085: src/index.ts.jinja 非 mimerenderer 分支定义 `const plugin: JupyterFrontEndPlugin<void>`，id 为 '{{ labextension_name }}:plugin'，autoStart: true，文件路径 `template/src/index.ts.jinja:15-21`
F-086: src/index.ts.jinja theme 分支 plugin.requires 为 [IThemeManager]，activate 函数中调用 manager.register() 注册主题，name 为 '{{ labextension_name }}'，isLight: true，load 回调为 `() => manager.loadCSS(style)`，unload 回调为 `() => Promise.resolve(undefined)`，style 路径为 '{{ labextension_name }}/index.css'，文件路径 `template/src/index.ts.jinja:18-30`
F-087: src/index.ts.jinja has_settings 分支在 activate 中调用 settingRegistry.load(plugin.id)，成功时打印 settings.composite，失败时 console.error，文件路径 `template/src/index.ts.jinja:31-41`
F-088: src/index.ts.jinja frontend-and-server 分支在 activate 中调用 requestAPI<any>('hello', app.serviceManager.serverSettings)，成功时 console.log(data)，失败时 console.error 提示 server extension 缺失，文件路径 `template/src/index.ts.jinja:42-51`
F-089: src/index.ts.jinja mimerenderer 分支从 '@jupyterlab/rendermime-interfaces' 导入 IRenderMime，data_format=='json' 时从 '@lumino/coreutils' 导入 JSONObject，从 '@lumino/widgets' 导入 Widget，文件路径 `template/src/index.ts.jinja:56-60`
F-090: src/index.ts.jinja mimerenderer 分支定义 MIME_TYPE 常量为 '{{ mimetype }}'，CLASS_NAME 为 'mimerenderer-{{ mimetype_name }}'，文件路径 `template/src/index.ts.jinja:65-70`
F-091: src/index.ts.jinja mimerenderer 分支定义 OutputWidget 类，继承 Widget 并实现 IRenderMime.IRenderer，文件路径 `template/src/index.ts.jinja:75-97`
F-092: OutputWidget 构造函数接受 IRenderMime.IRendererOptions 参数，调用 super()，设置 this._mimeType = options.mimeType，调用 this.addClass(CLASS_NAME)，文件路径 `template/src/index.ts.jinja:79-83`
F-093: OutputWidget.renderModel 方法接受 IRenderMime.IMimeModel 参数，返回 Promise<void>；data_format=='json' 时将 model.data[this._mimeType] 转为 JSONObject 并 JSON.stringify 显示；data_format=='string' 时将数据作为 string 截取前 16384 字符显示，文件路径 `template/src/index.ts.jinja:88-94`
F-094: src/index.ts.jinja mimerenderer 分支定义 rendererFactory: IRenderMime.IRendererFactory，safe: true，mimeTypes: [MIME_TYPE]，createRenderer 返回 new OutputWidget(options)，文件路径 `template/src/index.ts.jinja:102-106`
F-095: src/index.ts.jinja mimerenderer 分支定义 extension: IRenderMime.IExtension，id: '{{labextension_name}}:plugin'，rendererFactory，rank: 100，dataType: '{{ data_format }}'，文件路径 `template/src/index.ts.jinja:111-130`
F-096: extension.fileTypes 包含一个对象：name: '{{ mimetype_name }}'，mimeTypes: [MIME_TYPE]，extensions: ['{{ file_extension }}']，文件路径 `template/src/index.ts.jinja:117-123`
F-097: extension.documentWidgetFactoryOptions 包含 name: '{{ viewer_name }}'，primaryFileType: '{{ mimetype_name }}'，fileTypes: ['{{ mimetype_name }}']，defaultFor: ['{{ mimetype_name }}']，文件路径 `template/src/index.ts.jinja:124-129`

## F-101 ~ F-115: request.ts（前端-后端通信）

F-101: request.ts.jinja 从 '@jupyterlab/coreutils' 导入 URLExt，从 '@jupyterlab/services' 导入 ServerConnection，文件路径 `template/src/request.ts.jinja:1-3`
F-102: request.ts.jinja 导出异步函数 requestAPI<T>，参数为 endPoint: string、serverSettings: ServerConnection.ISettings、init: RequestInit = {}，返回 Promise<T>，文件路径 `template/src/request.ts.jinja:13-17`
F-103: requestAPI 函数内使用 URLExt.join 拼接 URL：serverSettings.baseUrl + '/{{ python_name | replace("_", "-") }}' + endPoint，文件路径 `template/src/request.ts.jinja:19-23`
F-104: requestAPI 函数内调用 ServerConnection.makeRequest(requestUrl, init, serverSettings)，捕获异常抛出 ServerConnection.NetworkError，文件路径 `template/src/request.ts.jinja:25-34`
F-105: requestAPI 函数获取 response.text()，尝试 JSON.parse，非 JSON 时 console.log，文件路径 `template/src/request.ts.jinja:36-44`
F-106: requestAPI 函数在 response.ok 为 false 时抛出 ServerConnection.ResponseError，文件路径 `template/src/request.ts.jinja:46-48`

## F-107 ~ F-120: Python 后端

F-107: __init__.py.jinja 尝试从 ._version 导入 __version__，ImportError 时 warnings.warn 并设置 __version__ = "dev"，文件路径 `template/{{python_name}}/__init__.py.jinja:1-9`
F-108: __init__.py.jinja frontend-and-server 分支从 .routes 导入 setup_route_handlers，文件路径 `template/{{python_name}}/__init__.py.jinja:10`
F-109: __init__.py.jinja 定义 _jupyter_labextension_paths() 函数，返回 [{"src": "labextension", "dest": "{{ labextension_name }}"}]，文件路径 `template/{{python_name}}/__init__.py.jinja:13-17`
F-110: __init__.py.jinja frontend-and-server 分支定义 _jupyter_server_extension_points() 返回 [{"module": "{{ python_name }}"}]，文件路径 `template/{{python_name}}/__init__.py.jinja:20-23`
F-111: __init__.py.jinja frontend-and-server 分支定义 _load_jupyter_server_extension(server_app) 函数，调用 setup_route_handlers(server_app.web_app) 并记录日志，文件路径 `template/{{python_name}}/__init__.py.jinja:26-36`
F-112: routes.py.jinja 导入 json、tornado，从 jupyter_server.base.handlers 导入 APIHandler，从 jupyter_server.utils 导入 url_path_join，文件路径 `template/{{python_name}}/routes.py.jinja:1-5`
F-113: routes.py.jinja 定义 HelloRouteHandler 类，继承 APIHandler，文件路径 `template/{{python_name}}/routes.py.jinja:7`
F-114: HelloRouteHandler.get 方法使用 @tornado.web.authenticated 装饰器，调用 self.finish(json.dumps({"data": "..."})) 返回包含 "Hello, world!" 和端点路径信息的 JSON，文件路径 `template/{{python_name}}/routes.py.jinja:11-19`
F-115: routes.py.jinja 定义 setup_route_handlers(web_app) 函数，host_pattern 为 ".*$"，base_url 从 web_app.settings["base_url"] 获取，路由模式为 url_path_join(base_url, "{{ python_name | replace('_', '-') }}", "hello")，handlers 列表为 [(hello_route_pattern, HelloRouteHandler)]，调用 web_app.add_handlers(host_pattern, handlers)，文件路径 `template/{{python_name}}/routes.py.jinja:22-29`

## F-121 ~ F-140: 配置文件

F-121: install.json.jinja 内容为 {"packageManager": "python", "packageName": "{{ python_name }}", "uninstallInstructions": "Use your Python package manager (pip, conda, etc.) to uninstall the package {{ python_name }}"}，文件路径 `template/install.json.jinja:1-5`
F-122: tsconfig.json.jinja compilerOptions 包含 strict: true、strictNullChecks: true、noImplicitAny: true、target: "ES2018"、module: "esnext"、moduleResolution: "node"、jsx: "react"、outDir: "lib"、rootDir: "src"，文件路径 `template/tsconfig.json.jinja:2-23`
F-123: tsconfig.json.jinja test 条件下 types 包含 "jest"，文件路径 `template/tsconfig.json.jinja:21-22`
F-124: tsconfig.json.jinja include 为 ["src/*"]，文件路径 `template/tsconfig.json.jinja:24`
F-125: jupyter-config/server-config/{{python_name}}.json.jinja 内容为 {"ServerApp": {"jpserver_extensions": {"{{ python_name }}": true}}}，文件路径 `template/jupyter-config/server-config/{{python_name}}.json.jinja:1-7`
F-126: schema/plugin.json.jinja 内容为 {"jupyter.lab.shortcuts": [], "title": "{{ labextension_name }}", "description": "{{ labextension_name }} settings.", "type": "object", "properties": {}, "additionalProperties": false}，文件路径 `template/schema/plugin.json.jinja:1-8`
F-127: .yarnrc.yml.jinja 中 nodeLinker 条件：yarn_linker=='pnpm' 时为 pnpm，否则为 node-modules；enableScripts: false；pnpm 模式下 packageExtensions 为 @module-federation/sdk 添加 process 依赖，文件路径 `template/.yarnrc.yml.jinja:1-8`
F-128: eslint.config.mjs.jinja 使用 @eslint/js、typescript-eslint、eslint-plugin-prettier/recommended、globals、@jupyter/eslint-plugin，文件路径 `template/eslint.config.mjs.jinja:1-7`
F-129: eslint.config.mjs.jinja ignores 包含 node_modules、dist、coverage、**/*.js、**/*.d.ts、.venv；test 时额外忽略 tests、**/__tests__、ui-tests，文件路径 `template/eslint.config.mjs.jinja:10-20`
F-130: style/index.css.jinja theme 分支 @import url('./variables.css')；非 theme 分支 @import url('base.css')，文件路径 `template/style/index.css.jinja:1`
F-131: style/base.css 包含注释指向 JupyterLab Developer Guide CSS Patterns 文档，文件路径 `template/style/base.css:1-5`
F-132: style/index.js 内容为 `import './base.css';`，文件路径 `template/style/index.js:1`
F-133: style/variables.css 定义 :root 下大量 CSS 变量（--jp-* 系列），涵盖 elevation shadows、borders、UI fonts、content fonts、code fonts、layout colors、brand/accent colors、state colors、cell styles、notebook styles、rendermime styles 等，文件路径 `template/style/variables.css:27-398`
F-134: .gitignore.jinja 包含 *.bundle.*、lib/、node_modules/、*.log、.eslintcache、.stylelintcache、*.egg-info、.ipynb_checkpoints、*.tsbuildinfo、{{python_name}}/labextension、{{python_name}}/_version.py、Python 标准 gitignore 条目、.DS_Store、.yarn/，test 时额外包含 ui-tests/test-results/、ui-tests/playwright-report/，文件路径 `template/.gitignore.jinja:1-128`
F-135: .prettierignore.jinja 包含 node_modules、**/node_modules、**/lib、**/package.json（但 !/package.json 排除根 package.json）、{{python_name}}、eslint.config.mjs、.venv，文件路径 `template/.prettierignore.jinja:1-8`

## F-141 ~ F-155: 测试配置

F-141: babel.config.js（非模板）内容为 `module.exports = require('@jupyterlab/testutils/lib/babel.config');`，文件路径 `template/babel.config.js:1`
F-142: jest.config.js（非模板）从 '@jupyterlab/testutils/lib/jest-config' 导入 jestJupyterLab，esModules 列表包含 @codemirror、@jupyter/ydoc、@jupyterlab/、lib0、nanoid、vscode-ws-jsonrpc、y-protocols、y-websocket、yjs，文件路径 `template/jest.config.js:1-13`
F-143: jest.config.js 配置 automock: false，collectCoverageFrom 为 ['src/**/*.{ts,tsx}', '!src/**/*.d.ts', '!src/**/.ipynb_checkpoints/*']，testRegex 为 'src/.*/.*.spec.ts[x]?$'，文件路径 `template/jest.config.js:17-27`
F-144: __tests__/{{python_name}}.spec.ts.jinja 包含一个简单测试：describe('{{ labextension_name }}', () => { it('should be tested', () => { expect(1 + 1).toEqual(2); }); })，文件路径 `template/src/__tests__/{{python_name}}.spec.ts.jinja:1-9`
F-145: ui-tests/ 目录（非模板子目录）包含 README.md、jupyter_server_test_config.py、playwright.config.js、yarn.lock；package.json.jinja 和 tests/{{python_name}}.spec.ts.jinja 为条件模板，文件路径 `template/ui-tests/`
F-146: ui-tests/playwright.config.js（非模板）从 '@jupyterlab/galata/lib/playwright-config' 导入 baseConfig，webServer.command 为 'jlpm start'，url 为 'http://localhost:8888/lab'，timeout 120000ms，文件路径 `template/ui-tests/playwright.config.js:1-14`
F-147: ui-tests/jupyter_server_test_config.py（非模板）从 jupyterlab.galata 导入 configure_jupyter_server，调用 configure_jupyter_server(c)，文件路径 `template/ui-tests/jupyter_server_test_config.py:1-10`
F-148: ui-tests/package.json.jinja name 为 "{{ labextension_name }}-ui-tests"，scripts.start 为 "jupyter lab --config jupyter_server_test_config.py"，scripts.test 为 "jlpm playwright test"，devDependencies 包含 @jupyterlab/galata: ^5.0.5 和 @playwright/test: ^1.60.0，文件路径 `template/ui-tests/package.json.jinja:1-15`
F-149: ui-tests/tests/{{python_name}}.spec.ts.jinja 非 mimerenderer 分支：test.use({ autoGoto: false })，测试用例验证 console 中包含 'JupyterLab extension {{ labextension_name }} is activated!' 消息，文件路径 `template/ui-tests/tests/{{python_name}}.spec.ts.jinja:1-21`
F-150: ui-tests/tests/{{python_name}}.spec.ts.jinja mimerenderer 分支：包含两个测试用例——验证文件打开显示和 notebook 输出显示，使用 screenshot 快照对比，文件路径 `template/ui-tests/tests/{{python_name}}.spec.ts.jinja:22-70`
F-151: conftest.py.jinja 声明 pytest_plugins = ("pytest_jupyter.jupyter_server",)，jp_server_config fixture 返回 {"ServerApp": {"jpserver_extensions": {"{{ python_name }}": True}, "allow_unauthenticated_access": False}}，文件路径 `template/conftest.py.jinja:1-14`

## F-156 ~ F-170: CI/CD 工作流

F-156: .github/workflows/build.yml.jinja 定义 Build 工作流，on: push(branches: main) 和 pull_request(branches: '*')，文件路径 `template/.github/workflows/build.yml.jinja:1-7`
F-157: build.yml.jinja build job runs-on: ubuntu-latest，步骤包含 Checkout、Base Setup（jupyterlab/maintainer-tools）、Install dependencies（pip install -U "jupyterlab>=4.0.0,<5"）、Lint（jlpm + jlpm run lint:check）、Test（jlpm run test，条件 test）、Build（pip install .[test]，frontend-and-server 时额外运行 pytest 和检查 server extension），文件路径 `template/.github/workflows/build.yml.jinja:14-55`
F-158: build.yml.jinja build job 中 Build 步骤执行 `python -m jupyterlab.browser_check`，frontend-and-server 时执行 `python .github/scripts/check_auth.py` 验证端点认证，文件路径 `template/.github/workflows/build.yml.jinja:47-55`
F-159: build.yml.jinja build job 执行 `python -m build` 打包，上传 extension-artifacts，文件路径 `template/.github/workflows/build.yml.jinja:56-69`
F-160: build.yml.jinja test_isolated job needs: build，在 Python 3.10 环境中安装 wheel 包（先删除 NodeJS），验证 labextension list 和 browser_check，文件路径 `template/.github/workflows/build.yml.jinja:71-99`
F-161: build.yml.jinja integration-tests job（条件 test）needs: build，使用 Playwright + Galata 运行 ui-tests，文件路径 `template/.github/workflows/build.yml.jinja:101-158`
F-162: build.yml.jinja check_links job 使用 jupyterlab/maintainer-tools 的 check-links action，文件路径 `template/.github/workflows/build.yml.jinja:160-167`
F-163: .github/workflows/check-release.yml.jinja 定义 Check Release 工作流，使用 jupyter-server/jupyter_releaser 的 check-release action，文件路径 `template/.github/workflows/check-release.yml.jinja:1-30`
F-164: .github/workflows/enforce-label.yml（非模板）检查 PR 标签，文件路径 `template/.github/workflows/enforce-label.yml`
F-165: .github/workflows/prep-release.yml（非模板）为 Jupyter Releaser 准备发布，文件路径 `template/.github/workflows/prep-release.yml`
F-166: .github/workflows/publish-release.yml（非模板）执行发布，文件路径 `template/.github/workflows/publish-release.yml`
F-167: .github/scripts/check_auth.py.jinja 从 jupyter_server.serverapp 导入 ServerApp，从 jupyter_server.utils 导入 JupyterServerAuthWarning，创建 ServerApp 实例（allow_unauthenticated_access=False, jpserver_extensions={"{{ python_name }}": True}, reraise_server_extension_failures=True），捕获 JupyterServerAuthWarning 并在有问题时 sys.exit，文件路径 `template/.github/scripts/check_auth.py.jinja:1-47`

## F-171 ~ F-185: 文档与辅助文件

F-171: README.md.jinja 包含项目标题、CI badge、Binder badge（条件 has_binder）、项目描述、Requirements（JupyterLab >= 4.0.0）、Install/Uninstall 命令、Troubleshoot 部分（frontend-and-server 条件）、Contributing 链接、AI Coding Assistant Support 部分（条件 has_ai_rules），文件路径 `template/README.md.jinja:1-101`
F-172: CHANGELOG.md（非模板）包含 `<!-- <START NEW CHANGELOG ENTRY> -->` 和 `<!-- <END NEW CHANGELOG ENTRY> -->` 标记，文件路径 `template/CHANGELOG.md:1-5`
F-173: CONTRIBUTING.md.jinja 包含 Development install（venv + pip install -e + jupyter-builder develop）、watch 模式说明、Development uninstall、Endpoint authentication（frontend-and-server 条件）、Testing（Jest/pytest/Playwright）、Packaging 链接，文件路径 `template/CONTRIBUTING.md.jinja:1-117`
F-174: RELEASE.md.jinja 包含 Manual release（Python 用 build+twine+hatch，NPM 用 npm publish）和 Automated releases with Jupyter Releaser 的说明，以及 conda-forge 发布说明，文件路径 `template/RELEASE.md.jinja:1-88`
F-175: binder/environment.yml.jinja 定义 conda 环境名为 `{{ python_name | replace('_', '-') }}-demo`，channels: [conda-forge]，dependencies 包含 python >=3.14,<3.15、jupyterlab >=4.0.0,<5、nodejs >=22,<23、pip、wheel，文件路径 `template/binder/environment.yml.jinja:1-21`
F-176: binder/postBuild.jinja（非模板文件，路径在条件目录中）文件路径 `template/binder/postBuild.jinja`
F-177: AGENTS.md.jinja（条件 has_ai_rules）包含 JupyterLab Extension Development 编码规范：PRIORITY RESOURCE USAGE（外部文档优先）、Code Quality Rules（Logging/Type Safety/File-Scoped Validation）、Coding Standards（Naming/Documentation/Code Organization）、Theme Extensions 指南、MIME Renderer Extensions 指南、Backend-Frontend Integration 工作流、Development Workflow、Best Practices、Common Pitfalls、Quick Reference，文件路径 `template/AGENTS.md.jinja:1-925`
