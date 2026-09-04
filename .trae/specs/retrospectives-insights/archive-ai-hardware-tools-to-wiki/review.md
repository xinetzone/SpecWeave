# AI硬件设计工具分析报告归档到Wiki - Verification Checklist

## 目录结构检查
- [ ] wiki目录 `ai-hardware-design-tools-wiki/` 已创建在正确路径下
- [ ] 目录下包含且仅包含3个文件：README.md、analysis-report.md、cleaned-article.md
- [ ] 无多余临时文件或中间产出文件

## YAML Frontmatter检查
- [ ] README.md包含正确的frontmatter（id、title、category、date、source）
- [ ] analysis-report.md包含正确的frontmatter（id、title、category、date、source、tags）
- [ ] cleaned-article.md包含正确的frontmatter（id、title、source、date、category、tags）
- [ ] frontmatter使用YAML格式（---包裹），字段值正确
- [ ] date字段为归档日期（2026-08-01）
- [ ] source字段为微信公众号原文URL

## cleaned-article.md内容检查
- [ ] 包含文章标题《一定要收藏！10个AI硬件设计的常用网站！》
- [ ] 包含作者信息（硬件狗哥）
- [ ] 包含发布时间信息
- [ ] 包含原文URL
- [ ] 10个工具的名称完整准确
- [ ] 10个工具的URL完整准确
- [ ] 10个工具的简介与原文一致

## analysis-report.md内容检查
- [ ] 报告内容完整，与源文件一致无截断
- [ ] 中文内容无乱码
- [ ] 重要声明/局限性说明保留
- [ ] Mermaid流程图保留且格式正确
- [ ] 表格格式正确
- [ ] 章节结构完整（14个章节）
- [ ] 源spec文件未被修改

## README.md内容检查
- [ ] 一句话摘要准确概括报告内容
- [ ] 文档索引表包含analysis-report.md和cleaned-article.md的链接
- [ ] 索引表中文档说明清晰
- [ ] 核心观点列表（4-5条）准确反映报告主要发现
- [ ] 相关资源链接包含：返回上级目录、文档首页、spec文档链接
- [ ] 链接使用正确的相对路径
- [ ] 整体风格与copilot-cost-multimodel-era-wiki/README.md一致

## 文件命名规范检查
- [ ] 所有文件名为kebab-case纯英文
- [ ] 目录名为kebab-case + -wiki后缀
- [ ] 无中文文件名

## 提交检查
- [ ] 仅提交wiki目录下的3个新文件
- [ ] 提交信息符合Conventional Commits规范：docs(knowledge): 归档AI硬件设计工具生态深度洞察报告到商业趋势分析wiki
- [ ] 未包含其他无关文件变更
- [ ] 源文件目录下文件未被修改或移动
