---
type: specification
title: "public-apis 博文转 OKF Wiki"
source: "https://mp.weixin.qq.com/s/rCCa5Y_UpWB_HKL4VCORvA"
status: completed
---

# public-apis 博文转 OKF Wiki

## 内容敏感度预检

微信公众号文章为公开页面，无 `share?code=`、`token` 或企业内部访问控制参数，按公开工作流处理。Spec 位于 `.trae/specs/`，最终 bundle 位于 `projects/awesome-okf-xs/doc/bundles/`。

## 场景与链路

本任务是知识沉淀场景，按七概念方法论编排 `R → I → E → V`：提取文章事实，识别目录的工作机制，生成可迁移的知识包，再进行独立核验和机械审查。文章转化流程补充 P0 数字核验、信源距离标注、双份 F 编号对拍和索引收尾。

## 骨架判定

文章是公共 API 资源盘点与使用边界综述。正文没有固定版本、完整输入输出、可复现安装顺序或作者实测日志，操作可复现性两问中至少一问为“否”，因此不创建 `examples/`，bundle 定位为“资源目录综述，非操作教程”。

## 归属位置分析

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `jishu/dev/opensource/` | ✅ | 主线是 GitHub 开源目录与开发者资源，现有束已容纳“程序员常用网站”类资源盘点 |
| `jishu/web/` | ❌ | 文章不是 Web 框架或 API 查询语言教程，目录本身也不是调用运行时 |
| `jishu/ai/` | ❌ | 文中仅把机器学习列为一个分类，没有 AI 主线 |
| 新建顶级分组 | ❌ | 单篇博文不新建分组，避免目录碎片化 |

## 知识地图

1. `00-public-apis-catalog.md`：项目定位、目录结构、五列元数据与免费边界。
2. `01-discovery-and-selection.md`：从分类、认证、HTTPS、CORS 到官方文档复核的筛选流程。
3. `02-companion-api-and-governance.md`：配套 API、贡献规则、许可证与生产使用风险。

## 验收标准

- 所有数字、项目名、协议、接口和能力声明均可回溯到 `F-xxx`。
- 文章的 51 分类、1700 多条、4.7 万 Star 与当前官方快照的差异在核验报告中显式记录。
- bundle 根索引与两个子目录索引均含 `{toctree}`。
- 不生成伪造的安装教程、调用示例或统一商用许可结论。
- `facts.md` 与 `references/article-source.md` 的 F 编号集合连续且一致。
