# Checklist — XMNN SDK 使用指南 docx→Sphinx 项目转换与双向导出

## 骨架与依赖
- [x] `d:\AI\.chaos\xmtools\xmnn-sdk-docs\` 目录结构完整（source/scripts/requirements.txt/build.ps1/README.md）
- [x] `pip install docxbuilder==1.2.0 rst2pdf==0.105` 安装成功（已通过 requirements.txt 统一安装）
- [x] 占位 HTML 构建成功（无 ERROR）

## 转换完整性
- [x] `scripts/docx2rst.py` 运行成功，源 docx 未被修改
- [x] 生成 6 个章节 RST 文件（changelog/environment/npuusertools/cpp-sdk/quantization/examples）
- [x] `source/_static/images/` 含 11 张提取图片，且 RST 中以 figure 引用
- [x] 26 个表格全部转为 RST 表格（list-table）
- [x] code 样式段落转为 code-block，数量 ≥ 200（实测 209 个）
- [x] `index.rst` toctree 按原文档顺序包含 6 个章节

## 风格保持
- [x] `custom.css` 声明三类字体栈：标题黑体系、正文仿宋系、代码楷体系
- [x] HTML 页面引用 custom.css，中文渲染正常

## docx 导出
- [x] `sphinx-build -b docx` 成功生成 `.docx`
- [x] 导出 docx 可被 python-docx 打开，含 6 个一级标题
- [x] docx 样式字体配置生效（标题黑体/正文仿宋/代码楷体）

## pdf 导出
- [x] PDF 构建成功，产物大小 > 0（实测 1.92 MB）
- [x] rst2pdf 字体配置注册了中文字体（simhei/simfang/simkai），字体缺失时有明确报错路径

## 一键构建
- [x] `build.ps1 all` 依次完成 html/docx/pdf 三格式构建
- [x] 三种产物均存在于 `build/` 下，构建日志无 ERROR
- [x] README.md 含构建说明与源文档溯源信息

## 边界合规
- [x] 未修改 `npu_tvm/`、`npuusertools/` 子仓库任何文件
- [x] `build/` 产物目录未纳入版本管理（.gitignore 覆盖）
