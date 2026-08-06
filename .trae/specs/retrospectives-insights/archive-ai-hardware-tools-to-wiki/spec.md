# AI硬件设计工具分析报告归档到Wiki - Product Requirement Document

## Overview
- **Summary**: 将已完成的微信公众号文章《一定要收藏！10个AI硬件设计的常用网站！》深度分析报告从 `.trae/specs/retrospectives-insights/analyze-ai-hardware-design-tools/` 归档到项目知识库wiki教程目录 `.agents/docs/knowledge/learning/06-business-trends-analysis/ai-hardware-design-tools-wiki/`，按照wiki规范格式化，添加YAML frontmatter，创建README索引入口，并更新目录索引。
- **Purpose**: 将临时分析产出物沉淀为可长期查阅、可检索、可被其他智能体和人类开发者发现的知识库条目，完善"商业趋势分析"分类下的AI工具生态内容。
- **Target Users**: 硬件工程师、电子爱好者/创客、嵌入式开发者、硬件创业者、EDA行业从业者、AI应用落地研究者、知识库使用者

## Goals
- 创建wiki目录 `ai-hardware-design-tools-wiki/` 到 `06-business-trends-analysis/` 下
- 将analysis-report.md转换为符合wiki规范的格式（添加YAML frontmatter、调整链接路径）
- 创建cleaned-article.md保存微信公众号原文清洗版
- 创建README.md作为wiki入口索引页
- 在README.md中包含文档索引、核心观点、相关资源链接
- 确保文件命名符合kebab-case规范
- 确保YAML frontmatter包含必要字段（id、title、category、date、source、tags）
- 验证归档后文档链接的正确性

## Non-Goals (Out of Scope)
- 不对分析报告内容进行实质性修改或重写
- 不重新分析文章或补充新的工具信息
- 不创建额外的教程章节（如FAQ、速查表等），除非已有内容可直接拆分
- 不运行generate-readme.py自动生成目录索引（可手动添加条目，或交由后续自动化处理）
- 不修改源报告文件（.trae/specs/下的原始文件保留不动）

## Background & Context
- **源文件位置**: `d:\AI\.trae\specs\retrospectives-insights\analyze-ai-hardware-design-tools\analysis-report.md`（约12000字，14个章节）
- **源文章信息**: 
  - 标题：《一定要收藏！10个AI硬件设计的常用网站！》
  - 作者：硬件狗哥
  - URL：https://mp.weixin.qq.com/s/YAm3b7kKkAPbFKgPpsTRVA
  - 发布时间：2026-07-08
- **归档目标目录**: `d:\AI\.agents\docs\knowledge\learning\06-business-trends-analysis\`
- **参考范例**: `copilot-cost-multimodel-era-wiki/`（同类型微信文章分析归档）
- **wiki格式规范**:
  - 目录命名：kebab-case + `-wiki`后缀
  - README.md作为入口，包含YAML frontmatter（id、title、category、date、source）
  - analysis-report.md为核心报告
  - cleaned-article.md为原文清洗版
  - 内部链接使用相对路径
  - 相关资源链接需指向spec文档和上级目录

## Functional Requirements
- **FR-1**: 在 `06-business-trends-analysis/` 下创建 `ai-hardware-design-tools-wiki/` 子目录
- **FR-2**: 将analysis-report.md内容复制到wiki目录，添加符合规范的YAML frontmatter
- **FR-3**: 创建cleaned-article.md，保存微信公众号原文的清洗版本（包含文章标题、作者、发布时间、10个工具完整信息）
- **FR-4**: 创建README.md作为wiki入口页，包含：
  - YAML frontmatter（id、title、category、date、source）
  - 一句话摘要
  - 文档索引表（链接到analysis-report.md和cleaned-article.md）
  - 核心观点列表（3-5条）
  - 相关资源链接（上级目录、首页、spec文档）
- **FR-5**: 确保所有Markdown链接路径正确（相对路径）
- **FR-6**: 文件名符合kebab-case英文命名规范

## Non-Functional Requirements
- **NFR-1**: frontmatter字段与现有wiki文档保持一致的风格
- **NFR-2**: 文档编码为UTF-8，无BOM
- **NFR-3**: 中文内容完整保留，无乱码
- **NFR-4**: 文件结构清晰，与参考范例（copilot-cost-multimodel-era-wiki）风格一致

## Constraints
- **Technical**: 仅在 `.agents/docs/knowledge/learning/06-business-trends-analysis/` 下创建文件，不修改其他位置文件
- **Business**: 保留源spec文件不动，归档为复制而非移动
- **Dependencies**: 源analysis-report.md已存在且内容完整
- **Naming**: 必须使用纯英文kebab-case命名

## Assumptions
- 源analysis-report.md内容完整、质量已通过验证
- wiki目录06-business-trends-analysis已存在
- 不需要运行generate-readme.py自动更新索引
- 不需要在上级README.md中手动添加索引条目（可后续自动化处理）

## Acceptance Criteria

### AC-1: Wiki目录创建成功
- **Given**: 源报告已完成
- **When**: 执行归档
- **Then**: 在 `d:\AI\.agents\docs\knowledge\learning\06-business-trends-analysis\` 下存在 `ai-hardware-design-tools-wiki/` 目录
- **Verification**: `programmatic`

### AC-2: analysis-report.md格式合规
- **Given**: wiki目录已创建
- **When**: 转换分析报告
- **Then**: analysis-report.md包含正确的YAML frontmatter（id、title、category、date、source、tags），内容完整无缺失
- **Verification**: `human-judgment`

### AC-3: cleaned-article.md内容完整
- **Given**: wiki目录已创建
- **When**: 创建原文清洗版
- **Then**: cleaned-article.md包含文章标题、作者信息、发布时间、原文URL、10个工具的完整原始介绍
- **Verification**: `human-judgment`

### AC-4: README.md入口页完整
- **Given**: analysis-report.md和cleaned-article.md已创建
- **When**: 创建README.md
- **Then**: README.md包含frontmatter、一句话摘要、文档索引表、核心观点、相关资源链接，格式与参考范例一致
- **Verification**: `human-judgment`

### AC-5: 文件命名符合规范
- **Given**: 所有文件已创建
- **When**: 检查文件名
- **Then**: 所有文件名使用kebab-case纯英文命名，无中文文件名
- **Verification**: `programmatic`

### AC-6: 内部链接路径正确
- **Given**: 所有文件已创建
- **When**: 检查README中的链接
- **Then**: 所有相对路径链接指向正确的文件，相关资源链接路径有效
- **Verification**: `human-judgment`

### AC-7: 源文件未被修改
- **Given**: 归档完成
- **When**: 检查源文件
- **Then**: `.trae/specs/retrospectives-insights/analyze-ai-hardware-design-tools/` 下的原始文件保持不变
- **Verification**: `programmatic`

## Open Questions
- 无（归档路径和格式已明确，参考范例已找到）
