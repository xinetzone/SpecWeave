# awesome-okf-xs 文档系统 - 验证清单

## 项目结构与文件

- [ ] `doc/` 目录已创建
- [ ] `doc/conf.py` 存在且是合法的 Python 文件
- [ ] `doc/index.md` 存在且包含 toctree 导航
- [ ] `doc/readme.md` 存在且使用 `{include}` 引用根 README
- [ ] `doc/_static/local.css` 存在且包含响应式样式
- [ ] `pyproject.toml` 存在于项目根目录且是合法 TOML
- [ ] `.gitignore` 已更新，包含 `doc/_build/` 和 `doc/bundles/`

## 依赖与配置

- [ ] `pyproject.toml` 包含 `[project.optional-dependencies].doc` 依赖组
- [ ] doc 依赖组包含 sphinx、myst-parser、sphinx-book-theme
- [ ] doc 依赖组包含 sphinx-design、sphinx-copybutton、sphinx-tippy
- [ ] conf.py 中 language 设置为 `zh_CN`
- [ ] conf.py 使用 probe-fallback 模式检测可选扩展
- [ ] conf.py 配置了 myst_enable_extensions
- [ ] conf.py 配置了 html_theme_options（仓库 URL、导航深度等）
- [ ] conf.py 配置了 suppress_warnings 容错 bundles frontmatter

## bundles 子文档库集成

- [ ] conf.py 的 setup() 函数实现了跨平台链接创建
- [ ] Windows 上创建 junction（`mklink /J`），Unix 上创建 symlink
- [ ] 链接创建逻辑是幂等的（重复执行不报错）
- [ ] 链接创建有安全检查（doc/bundles 为普通目录时报错而非覆盖）
- [ ] `doc/bundles` 链接指向 `../bundles`（解析到项目根 bundles/）
- [ ] toctree 中包含 `bundles/index` 入口
- [ ] **bundles/ 目录内无任何文件被修改、创建或删除**

## 构建验证

- [ ] `pip install -e ".[doc]"` 安装成功
- [ ] `sphinx-build -b html doc doc/_build/html` 退出码为 0
- [ ] `doc/_build/html/index.html` 存在且非空
- [ ] `doc/_build/html/bundles/index.html` 存在
- [ ] 至少 3 个 bundle 分组页面被渲染（如 conda、sphinx、jupyter）
- [ ] `git diff --exit-code bundles/` 确认 bundles 无变更
- [ ] 构建无致命错误（ERROR 级别日志为 0）

## 内容与导航

- [ ] 首页显示项目标题和简介
- [ ] 侧边栏导航包含"知识束库"分组
- [ ] 点击 bundles 入口可导航到知识束总索引页
- [ ] bundles/index.md 中的生态关系图正确渲染
- [ ] bundles 内部相对链接可跳转
- [ ] README 内容通过 include 显示在 readme 页面
- [ ] 搜索功能可检索到 bundles 中的中文内容

## 样式与响应式

- [ ] 代码块有横向滚动，不溢出页面
- [ ] 表格在窄屏下可横向滚动
- [ ] 手机宽度（≤768px）下导航和正文正常显示
- [ ] 代码复制按钮可用
- [ ] admonition（提示框）样式正常

## Git 状态

- [ ] `doc/_build/` 被 .gitignore 排除
- [ ] `doc/bundles/`（链接）被 .gitignore 排除
- [ ] `doc/conf.py`、`doc/index.md` 等源文件被 git 追踪
- [ ] `pyproject.toml` 被 git 追踪
- [ ] 无敏感信息泄露
