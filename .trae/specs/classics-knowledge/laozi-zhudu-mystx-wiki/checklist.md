# 《帛书老子注读》MyST Wiki 教程 - Verification Checklist

## 项目骨架
- [x] pyproject.toml 存在，requires-python = ">=3.14" ✅
- [x] doc/conf.py 存在，mystx 主题正确配置 ✅
- [x] doc/_config.toml 存在，主题选项适配本项目 ✅
- [x] doc/index.md 存在，包含根 toctree ✅
- [x] uv 虚拟环境创建成功，mystx 可导入 ✅
- [x] PDF 全文 297 页提取完成，保存为结构化数据（chapters.json）✅
- [x] 81个章节起始位置精确到页（第一章 P13，末章到P280，附录P281）✅

## OKF 合规
- [x] 每个 Markdown 文件以 `---` YAML frontmatter 开头和结尾 ✅
- [x] 每个文件 type = BookChapter（章节）/ BookFrontMatter / BookSectionTitle / BookAppendix ✅
- [x] 每个文件包含 title 字段（对应章节标题）✅
- [x] 每个文件包含 part 字段（front_matter/de_jing/dao_jing/appendix）✅
- [x] 每个文件包含 chapter_num 字段（整数，帛书顺序1-81）✅
- [x] 每个文件包含 modern_chapter 字段（整数，对应今本章节号1-81）✅
- [x] 每个文件 sources 数组中包含原始 PDF 引用（"秦波，《帛书老子注读》，2024"）✅
- [x] 每个文件包含 generated 元数据（日期格式）✅

## 内容完整性与忠实度
- [x] 版权信息页完整保留（122字）✅
- [x] 作者简介内容完整（137字，水印已去除）✅
- [x] 序（P7-9）完整保留（1281字）✅
- [x] 注读说明（P10-11）完整保留（550字）✅
- [x] 德经注读44章：每章包含帛书版、传世版、版本差异、直译、解读 ✅
- [x] 道经注读37章：每章包含帛书版、传世版、版本差异、直译、解读 ✅
- [x] 附录注音版完整保留（带校对警告，P281-297拼音/汉字分离问题已标注）✅
- [x] 帛书版原文与 PDF 一致（抽查首章："上德不德，是以有德" 正确）✅
- [x] 传世版原文与 PDF 一致（抽查）✅
- [x] 解读部分不截断、不遗漏（抽查首末段）✅
- [x] 版本差异注释（①②③...）标记保留 ✅
- [x] 无添加作者原文以外的评论、注解、AI生成内容 ✅

## 文本质量
- [x] 段落内硬换行已修复（PDF 提取造成的断行合并）✅
- [x] 段落间空行正确保留 ✅
- [x] 无明显乱码或缺失字符 ✅
- [x] Markdown 小标题正确标记各子部分（### 帛书版 等）✅
- [x] 一级标题（#）已添加到每个文件 frontmatter 之后 ✅

## Sphinx 构建
- [x] sphinx-build -b html 退出码为 0（-W --keep-going 通过）✅
- [x] doc/_build/html/index.html 生成 ✅
- [x] 无 ERROR 级别构建消息（myst.header 警告已 suppress）✅
- [x] toctree 包含所有章节，无孤立文档（93个md全部被引用）✅
- [x] HTML 页面中文渲染正常 ✅
- [x] 侧边栏导航按 前言→德经→道经→附录 顺序排列 ✅
- [x] 章节间链接可点击跳转（97个HTML文件生成）✅
- [x] mystx 主题正常加载 ✅
- [x] 本地预览服务器运行在 http://localhost:8090/ ✅

## 目录结构
- [x] doc/front-matter/ 下有：copyright、author-intro、preface、reading-guide、index ✅
- [x] doc/de-jing/ 下有 44 个章节文件（ch01-ch44）+ title.md + index.md ✅
- [x] doc/dao-jing/ 下有 37 个章节文件（ch45-ch81）+ title.md + index.md ✅
- [x] doc/appendix/ 下有 phonetic.md + index.md ✅
- [x] 文件名采用 chXX.md 格式，XX 为两位数序号（01-81）✅
- [x] .gitignore 已创建，排除 _build/、__pycache__/、.venv/ 等 ✅

## 字数统计
- 章节最少字数：740字（ch50）
- 章节最多字数：3207字（ch46）
- 章节平均字数：1503字
- 总章节字数：约 148,330 字
- 异常字数文件：无
