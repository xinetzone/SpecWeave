# Tasks — XMNN SDK 使用指南 docx→Sphinx 项目转换与双向导出

> 子项目位置：`d:\AI\.chaos\xmtools\xmnn-sdk-docs\`
> 源文档（只读）：`d:\AI\.chaos\tests\old\work\doc\XMNN_SDK_使用指南v1.1.0.docx`

## [x] Task 1: 创建 Sphinx 子项目骨架
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建目录 `d:\AI\.chaos\xmtools\xmnn-sdk-docs\`，结构：`source/`（conf.py、index.rst、_static/、各章节 rst）、`scripts/`、`build/`（产物，不入库）、`requirements.txt`、`build.ps1`、`README.md`
  - `conf.py` 配置：project="芯劢微XMNPU工具链使用指南"、release="1.1.0"、extensions 含 `docxbuilder`（或 `sphinxcontrib.docxbuilder`，以实际安装名为准）、语言 `zh_CN`
  - `requirements.txt` 声明：sphinx、docxbuilder==1.2.0、rst2pdf==0.105、python-docx
  - 安装依赖：`pip install docxbuilder==1.2.0 rst2pdf==0.105`
- **Verification**: `sphinx-build -b html source build/html` 以占位 index.rst 构建成功

## [x] Task 2: 编写 docx2rst.py 转换脚本
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 使用 python-docx 遍历源文档段落，按样式映射：Heading 1~4 → RST 标题（=`-`~`^` 层级）；code → 归并连续 code 段为 `.. code-block:: text`；List Paragraph → 列表项；Normal → 正文段落
  - 表格转换：遍历 `document.tables`，按文档顺序插入，转为 `.. list-table::`（兼容合并单元格降级）
  - 图片提取：从 docx 包内 `word/media/` 提取 11 张图片至 `source/_static/images/`，在对应段落位置插入 `.. figure::`
  - 按 6 个 Heading 1 切分输出 6 个 RST 文件：`changelog.rst`、`environment.rst`、`npuusertools.rst`、`cpp-sdk.rst`、`quantization.rst`、`examples.rst`
  - 生成 `index.rst` toctree 按原文档顺序引用 6 个章节
- **Verification**: 运行脚本后检查：6 个 RST 文件存在；图片目录含 11 个文件；代码块数量 ≥ 200；表格数量 = 26

## [x] Task 3: 配置风格保持（HTML CSS）
- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - 创建 `source/_static/custom.css`：标题字体栈 `"SimHei", "黑体", sans-serif`；正文字体栈 `"FangSong", "仿宋", "STFangsong", "华文仿宋", serif`；代码字体栈 `"KaiTi", "楷体", "STKaiti", "华文楷体", monospace`；正文字号 10.5pt 观感
  - `conf.py` 注册 `html_css_files = ['custom.css']`，选择内置主题（alabaster 或 classic）作为基础
- **Verification**: HTML 构建后 custom.css 被引用，页面中文字体栈声明完整

## [x] Task 4: 配置 Sphinx→docx 导出
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - `conf.py` 配置 docxbuilder 选项（标题样式、作者"浙江芯劢微电子股份有限公司"、版本号 1.1.0）
  - 通过 docxbuilder 的样式钩子或后处理，将 Word 标题字体设为黑体、正文设为仿宋、代码设为楷体
- **Verification**: `sphinx-build -b docx source build/docx` 生成 docx；用 python-docx 打开验证含 6 个一级标题

## [x] Task 5: 配置 Sphinx→pdf 导出（rst2pdf）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 探测 `C:\Windows\Fonts` 中文字体文件（黑体/仿宋/楷体），编写 `pdf.style`（rst2pdf styles 配置）注册字体与字体族（含中文回退）
  - `conf.py` 添加 `rst2pdf` 相关配置（或独立构建命令 `sphinx-build -b pdf`，以 rst2pdf 实际集成为准）
  - 字体文件缺失时输出明确错误提示
- **Verification**: 生成 PDF 文件且大小 > 0，构建无致命错误

## [x] Task 6: 一键构建脚本与验证
- **Priority**: high
- **Depends On**: Task 3, Task 4, Task 5
- **Description**:
  - 编写 `build.ps1`（pwsh 7.4+ 兼容）：参数 `-Target html|docx|pdf|all`，输出产物路径
  - 编写 `README.md`：项目说明、构建命令、目录结构、源文档溯源（source 字段）
  - 端到端验证：`.\build.ps1 all` 三格式全部产出
- **Verification**: 三格式产物均存在于 `build/` 下，构建日志无 ERROR

## Task Dependencies

- Task 2 依赖 Task 1（骨架就绪后才能放置脚本与 RST）
- Task 3/4/5 依赖 Task 2（RST 内容就绪后才能验证各格式渲染）；三者可并行
- Task 6 依赖 Task 3/4/5（汇总三格式构建入口）
