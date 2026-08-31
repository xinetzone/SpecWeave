---
type: Wiki Tutorial

id: knowledge-catalog-wiki-metadata-as-code
title: 03 - 元数据即代码（mdcode/kcmd工具链）
date: 2026-08-15
tags:
  - metadata-as-code
  - kcmd
  - typescript
  - mcp
  - cli
  - git-workflow
source:
  - vendor/knowledge-catalog/toolbox/mdcode/README.md
  - vendor/knowledge-catalog/toolbox/README.md
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/07-vendor-product-learning/google-cloud/knowledge-catalog-wiki/03-metadata-as-code.toml"
maturity: L1-draft
---
# 03 - 元数据即代码（mdcode/kcmd工具链）

> Metadata as Code (mdcode) 是Knowledge Catalog面向生产的工具链，为数据管理员、数据生产者和AI Agent提供基于源码制品的元数据管理和上下文工程UX。用户和Agent可以使用开发者友好的工作流（版本控制、CI/CD）创作、管理和丰富元数据制品。

---

## 一、mdcode 概述

### 1.1 核心理念

mdcode将元数据表示为源码制品（YAML+Markdown文件），可以与Knowledge Catalog服务中的元数据双向同步。这是"基础设施即代码(IaC)"理念在元数据管理领域的延伸：

| 传统元数据管理 | Metadata as Code |
|--------------|-----------------|
| Web UI点击操作 | 文本文件编辑+Git工作流 |
| 集中式存储 | 本地工作区+目录服务双向同步 |
| 无版本历史或版本历史在DB中 | Git天然提供完整版本历史、diff、blame、PR审查 |
| 手动变更管理 | CI/CD自动化验证和发布 |
| 专有API访问 | 文件系统+标准工具链 |

### 1.2 关键特性

1. **人类和Agent友好的元数据表示**：以YAML和Markdown文件作为源码，制品按层次结构组织，镜像数据和元数据资产的资源层次
2. **本地工作区与目录服务双向同步**：pull/push工作流，类似Git
3. **支持第一方和第三方元数据构造**：aspect类型可扩展
4. **多分发形态**：TypeScript库、Python库、CLI工具（kcmd）、MCP服务器

### 1.3 技术栈

| 组件 | 技术 |
|------|------|
| 核心库 | TypeScript |
| CLI | Node.js |
| 认证 | gcloud CLI（application-default login） |
| GCP API | Dataplex/Knowledge Catalog API |
| 测试 | 内置测试框架（含语义SQL golden测试） |

---

## 二、元数据制品结构

### 2.1 目录布局

元数据在表示资源（如BigQuery Dataset、Dataplex EntryGroup等）的目录中组织。

```
path/to/root/
├── catalog.yaml                       # 清单和配置指令
└── catalog/                           # 包含元数据快照
    └── <dir1>/
        └── <entry-id1>.yaml           # Entry
        └── <dir2>/
            ├── <entry-id2>.yaml       # Entry（带sidecar markdown）
            └── <entry-id2>.aspect.md  # aspect文件
```

### 2.2 Manifest文件（catalog.yaml）

**catalog/catalog.yaml**是清单文件，定义同步范围和配置：

```yaml
scope: bq-dataset.prod-data.ecommerce

aliases:
  ca-guidelines:
    aspect: data-agents-project.global.ca-guidelines
  ecommerce:
    aspect: data-agents-project.global.ecommerce

snapshot:
  entries:
    - bigquery-table
    - bigquery-view
    - entry-group
  aspects:
    - overview
    - descriptions

publishing:
  aspects:
    - overview
    - descriptions
```

关键字段：
- `scope`：同步的资源范围（格式：`<type>.<project>.<dataset>`等）
- `aliases`：aspect类型别名，简化引用
- `snapshot.entries`：快照包含的entry类型
- `snapshot.aspects`：快照包含的aspect类型
- `publishing.aspects`：发布时推送的aspect类型

### 2.3 Entry YAML文件

**catalog/<dir>/<entry-id>.yaml**表示单个元数据entry：

```yaml
id: products
type: bigquery-table

resource:
  name: projects/prod-data/datasets/ecommerce/tables/products
  displayName: Products Table
  description: All products in the catalog
  labels:
    env: prod
  createTime: 2026-04-23T00:44:03Z
  updateTime: 2026-04-23T00:44:03Z

schema:
  ...

contacts:
  ...
```

### 2.4 Entry Sidecar Markdown文件

**catalog/<dir>/<entry-id>.<aspect>.md**是aspect的sidecar Markdown文件，用于富文本aspect内容（如overview、descriptions）：

```markdown
---
userManaged: true
links:
  ...
---
[overview.content]
```

frontmatter中`userManaged: true`表示这是用户管理的内容（区别于服务端自动生成）。

---

## 三、使用方式

mdcode提供三种使用方式：TypeScript库、kcmd CLI、MCP服务器。

### 3.1 TypeScript库

安装：
```bash
npm install kcmd
```

编程方式使用：

```typescript
import * as kcmd from 'kcmd';

// 从头创建catalog manifest
const manifest = new kcmd.CatalogManifest(...);
manifest.save('/path/to/root');

// 从文件系统加载catalog快照
const snapshot = kcmd.CatalogSnapshot.fromPath('/path/to/root');

// 从Catalog服务拉取最新元数据
const pullResult = await snapshot.pull();
if (pullResult.success) {
  console.log('Metadata pulled successfully');
} else {
  console.error('Metadata pull failed:', pullResult.error);
}

// 推送修改后的元数据到Catalog服务
const pushResult = await snapshot.push();
if (pushResult.success) {
  console.log('Metadata pushed successfully');
} else {
  console.error('Metadata push failed:', pushResult.error);
}
```

### 3.2 kcmd CLI工具

kcmd是独立分发的CLI二进制文件，提供git风格的工作流。

> 注意：CLI使用`gcloud`获取认证token，确保已通过`gcloud auth application-default login`认证。

#### 初始化

```bash
# 为BigQuery dataset初始化新的catalog快照
kcmd init --bigquery-dataset <projectId>.<datasetId>

# 为多个BigQuery datasets初始化
kcmd init --bigquery-dataset <projectId>.<datasetId1> --bigquery-dataset <projectId>.<datasetId2>

# 为BigQuery dataset初始化，指定entry和aspect类型
kcmd init --bigquery-dataset <projectId>.<dataset> \
  --entry bigquery-table --entry bigquery-view \
  --aspect overview --aspect description

# 为自定义EntryGroup初始化
kcmd init --entry-group <projectId>.<locationId>.<entryGroupId>
```

#### 拉取与同步

```bash
# 从Knowledge Catalog服务拉取最新catalog快照
# 如果存在尚未推送到catalog的pending变更，会报告冲突
# 支持--dry-run标志
kcmd pull
```

#### 状态查看

```bash
# 检查本地修改
kcmd status
```

#### 推送发布

```bash
# 将本地更改推送到Knowledge Catalog服务
# 仅推送自上次pull以来的更改，且前提是元数据在此期间未在catalog中被修改
# 支持--dry-run标志
kcmd push
```

### 3.3 MCP服务器

要将Metadata as Code工具作为MCP工具在Agent系统（如Gemini CLI）中使用，将以下内容添加到MCP设置文件：

```json
{
  "mcpServers": {
    "kc-mac": {
      "command": "kcmd",
      "args": ["mcp", "--path", "/path/to/root"]
    }
  }
}
```

MCP服务器提供以下工具：

| 工具 | 说明 |
|------|------|
| `pull` | 从Catalog服务拉取最新元数据 |
| `push` | 将修改后的元数据推送到Catalog服务 |
| `list-entries` | 列出catalog快照中的entries |
| `lookup-entry` | 从快照中查找entry及其元数据 |
| `modify-entry` | 修改快照中的entry及其元数据 |

> 注意：MCP服务器使用`gcloud`获取认证token。

---

## 四、开发者工作流

如果你要在本地开发mdcode：

### 4.1 环境搭建

```bash
git clone https://github.com/googlecloudplatform/knowledge-catalog
cd toolbox/mdcode
npm install
```

### 4.2 构建

```bash
npm run build
```

### 4.3 测试

```bash
npm run test
```

测试包含：
- 单元测试
- 语义加载器测试
- BigQuery SQL生成golden测试（`tests/libts/semantic/fixtures/`）
- 场景测试（`tests/scenarios/`）：包含init/pull/push各种场景的YAML规格

---

## 五、mdcode与OKF的关系

这是一个容易混淆的点，需要澄清：

| 维度 | OKF（开放知识格式） | mdcode（Metadata as Code） |
|------|-------------------|--------------------------|
| **定位** | 厂商中立的知识交换格式 | Knowledge Catalog(GCP)专用的元数据管理工具 |
| **文件格式** | Markdown + YAML frontmatter | YAML条目文件 + Markdown sidecar |
| **目录结构** | 灵活，约定index.md/log.md | 固定的catalog/目录层次+catalog.yaml |
| **信任/来源** | 一等公民（sources/generated/verified/stale_after） | 通过Knowledge Catalog API同步 |
| **认证计算** | 原生支持Attested Computation类型 | 面向GCP Entry/Aspect模型 |
| **可视化** | 内置Cytoscape.js可视化器(viz.html) | CLI+MCP工具 |
| **生态** | 通用，任意工具可读写 | GCP生态，与Dataplex API深度集成 |
| **关系** | mdcode可以导出/导入OKF吗？ | mdcode是GCP原生元数据的代码表示；OKF是更通用的知识交换格式；两者可以互相转换 |

简单来说：
- OKF是一种**开放格式规范**，类似"Markdown for knowledge"
- mdcode/kcmd是**GCP专用工具链**，类似"git for Dataplex metadata"
- 参考智能体(reference_agent)生成OKF bundles
- kcmd管理GCP Knowledge Catalog原生Entry/Aspect元数据

---

继续阅读：[04-samples.md - 示例智能体实战（Discovery/Enrichment）](04-samples.md)
