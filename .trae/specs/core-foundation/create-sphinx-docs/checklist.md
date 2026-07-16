# SpecWeave Sphinx 文档站点创建 - Verification Checklist

## 目录结构检查
- [x] `docs/` 目录已创建
- [x] `docs/_static/` 目录已创建
- [x] `docs/_static/images/` 目录已创建
- [x] `docs/_templates/` 目录已创建
- [x] `docs/tech/` 目录已创建
- [x] `docs/general/` 目录已创建
- [x] `docs/topics/` 目录已创建

## 配置文件检查
- [x] `docs/conf.py` 文件存在
- [x] `docs/conf.py` 通过 Python 语法检查（`py_compile` 无错误）
- [x] `docs/conf.py` 中 `project` 配置为 "SpecWeave"
- [x] `docs/conf.py` 中 `language` 配置为 "zh_CN"
- [x] `docs/conf.py` 中 `author` 包含 "SpecWeave"
- [x] `docs/conf.py` 中无 `autoapi` 相关配置（已移除）
- [x] `docs/conf.py` 中无 `bibtex_bibfiles` 配置（已移除）
- [x] `docs/conf.py` 包含 Windows 事件循环兼容代码（hasattr 检查）
- [x] `docs/conf.py` 中 MyST 扩展已配置（myst_enable_extensions）
- [x] `docs/conf.py` 中 mermaid 围栏代码指令配置存在（myst_fence_as_directive）
- [x] `docs/conf.py` 包含 suppress_warnings 配置抑制 myst.xref_missing
- [x] `docs/conf.py` exclude_patterns 包含 `.venv`（额外修复）
- [x] `docs/_config.toml` 文件存在
- [x] `docs/_config.toml` 为有效的 TOML 格式（可被 tomllib 加载）
- [x] `docs/_config.toml` 中 repository_url 指向 SpecWeave 仓库
- [x] `docs/_config.toml` 中无 launch_buttons 配置段（已移除 binder/colab）
- [x] `docs/_config.toml` 包含 repository_provider = "gitlab"（额外修复，支持 GitCode）
- [x] `docs/tasks.py` 文件存在
- [x] `docs/tasks.py` 通过 Python 语法检查
- [x] `docs/tasks.py` 包含 help、build、html、clean、linkcheck 任务函数

## 静态资源检查
- [x] `docs/_static/local.css` 文件存在
- [x] `docs/_static/variables.css` 文件存在
- [x] `docs/_static/mermaid.css` 文件存在
- [x] `docs/_static/images/` 目录下有 logo 文件
- [x] `docs/_static/images/` 目录下有 favicon 文件

## 入口文档检查
- [x] `docs/index.md` 文件存在
- [x] `docs/index.md` 包含 toctree 指令
- [x] `docs/index.md` 的 toctree 引用 tech/index、general/index、topics/index
- [x] `docs/tech/index.md` 文件存在
- [x] `docs/tech/index.md` 包含 toctree 指令
- [x] `docs/tech/index.md` 的 toctree 引用 intro、quickstart、features、contributing、changelog
- [x] `docs/general/index.md` 文件存在
- [x] `docs/topics/index.md` 文件存在

## tech/ 初始文档检查
- [x] `docs/tech/intro.md` 文件存在且有一级标题
- [x] `docs/tech/quickstart.md` 文件存在且有一级标题
- [x] `docs/tech/features.md` 文件存在且有一级标题
- [x] `docs/tech/contributing.md` 文件存在且有一级标题
- [x] `docs/tech/changelog.md` 文件存在且有一级标题

## README 截断标记检查
- [x] 根目录 `README.md` 中存在 `<!-- end-doc-include -->` 标记
- [x] `<!-- end-doc-include -->` 标记位置合理（在"文档导航"章节前）

## 内容质量检查
- [x] 所有 Markdown 文件使用 UTF-8 编码
- [x] 文档中路径引用使用相对路径
- [x] 配置文件有合理的注释说明
- [x] vendor/flexloop/ 目录下无意外修改（git status 干净）

## 构建验证检查
- [x] conf.py 可被 Python 导入或执行，无致命错误
- [x] `sphinx-build -b html docs docs/_build/html` 构建成功（返回码 0）
- [x] 构建输出目录 `docs/_build/html/index.html` 存在
- [x] `docs/_build/html/index.html` 文件大小 56KB > 1KB（非空）
- [x] HTML 页面标题包含 "SpecWeave"
- [x] 构建错误输出中无 "Configuration error" 类致命错误
- [x] tech/ 目录下 6 个 HTML 文件正常生成
- [x] general/ 和 topics/ 入口 HTML 文件正常生成

## 边界与一致性检查
- [x] 目录结构与参考模板 vendor/flexloop/docs/ 的核心组织方式一致（三轨分类）
- [x] 没有引入不必要的依赖扩展
- [x] 文档骨架具有可扩展性（新增文档只需追加到 toctree）
- [x] CSS 样式文件完整保留响应式设计和暗色模式支持
- [x] .gitignore 已添加 docs/_build/ 和 .venv/ 忽略规则
