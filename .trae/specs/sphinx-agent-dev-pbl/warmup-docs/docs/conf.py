# Sphinx 配置文件 —— 热身项目专用
#
# ⚠️ 学生请注意：这个文件你【不需要】看懂，也【不要】修改。
#    它已经为你配置好了。你的任务只是编辑 index.md。
#
# 如果构建报错，先检查你是不是不小心改动了这个文件。

project = "我的文档站"
author = "热身项目"
copyright = "2026"

# --- 扩展 ---------------------------------------------------------------
# 只启用热身任务必需的三个，降低出错概率
extensions = [
    "myst_parser",          # 让学生能用 Markdown 写文档
    "sphinx_copybutton",    # 代码块右上角加复制按钮
    "sphinx_design",        # 提供卡片等排版组件（本任务用不到，留着给后续任务）
]

# --- 源文件设置 ----------------------------------------------------------
# 允许 .md（Markdown）和 .rst 两种格式
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# 首页文件名
root_doc = "index"

# MyST 额外语法（热身任务用不到，但无害）
myst_enable_extensions = ["colon_fence", "deflist"]

# --- 语言与编码 ----------------------------------------------------------
language = "zh_CN"

# --- HTML 输出 -----------------------------------------------------------
# ⚠️ 使用 Sphinx 内置主题（无需额外安装任何主题包）
#    这样保证「零安装」——不会因为缺一个主题包就构建失败
html_theme = "alabaster"

html_theme_options = {
    "description": "我的第一个文档站",
    "fixed_sidebar": True,
}

# 静态文件目录（热身任务不需要自定义静态资源，留空即可）
html_static_path = []

# 不让 Sphinx 对每个文件都打印版权信息，减少干扰输出
html_show_copyright = False
html_show_sphinx = False

# --- 放宽警告 ------------------------------------------------------------
# 热身任务允许出现"文档没被 toctree 引用"之类的警告，不视为失败
suppress_warnings = ["toc.not_included"]

# --- 排除构建产物 --------------------------------------------------------
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
