---
title: "MDX + GraphQL 最佳实践与FAQ"
source: "insight:retrospective-sphinx-graphql-okf-combination-insights-20260805"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/04-docs-markup-tooling/mdx-graphql-guide/03-best-practices.toml"
date: "2026-08-05"
tags: [mdx, graphql, best-practices, deployment, okf, faq]
category: "learning"
status: "stable"
summary: "性能优化、缓存策略、生产部署、安全考虑、与OKF开放知识协议集成方向、常见问题解答"
---
# 03 - 最佳实践与FAQ

> 本章目标：掌握生产环境部署可查询文档站的关键注意事项，理解性能优化策略，了解如何与 OKF 开放知识协议集成，并解答常见问题。

## 性能优化

### 1. 数据缓存策略

文档数据变更频率低，缓存收益极高：

```ts
// src/lib/graphql/docs-data.ts
import fs from 'node:fs'
import path from 'node:path'
import matter from 'gray-matter'
import { glob } from 'glob'

const DOCS_DIR = path.join(process.cwd(), 'src/content/docs')

// 内存缓存 + 文件修改时间检测（比简单缓存更智能）
let cache: {
  data: ApiEndpointMeta[]
  mtimes: Map<string, number>
} | null = null

function loadAllEndpoints(): ApiEndpointMeta[] {
  const files = glob.sync('**/*.mdx', { cwd: DOCS_DIR })
  const mtimes = new Map<string, number>()
  let needRebuild = !cache

  const endpoints: ApiEndpointMeta[] = []

  for (const file of files) {
    const filePath = path.join(DOCS_DIR, file)
    const stat = fs.statSync(filePath)
    mtimes.set(file, stat.mtimeMs)

    // 检查文件是否修改过
    if (cache && cache.mtimes.get(file) !== stat.mtimeMs) {
      needRebuild = true
    }

    if (!needRebuild && cache) {
      // 使用缓存数据
      continue
    }

    const content = fs.readFileSync(filePath, 'utf-8')
    const { data } = matter(content)
    endpoints.push({
      slug: file.replace(/\.mdx$/, ''),
      title: data.title ?? file,
      description: data.description ?? '',
      category: data.category ?? 'misc',
      returnType: data.returnType ?? 'void',
      params: data.params ?? [],
      deprecated: data.deprecated ?? false,
      since: data.since,
    })
  }

  if (needRebuild) {
    cache = { data: endpoints, mtimes }
    return endpoints
  }

  return cache!.data
}
```

**生产环境优化**：构建时预先生成 JSON 数据文件，运行时直接 import，完全跳过文件系统读取：

```ts
// scripts/build-docs-index.ts (构建脚本)
import fs from 'node:fs'
import path from 'node:path'
import matter from 'gray-matter'
import { glob } from 'glob'

// 构建时运行，生成 docs-index.json
const files = glob.sync('src/content/docs/**/*.mdx')
const endpoints = files.map((file) => {
  const { data } = matter(fs.readFileSync(file, 'utf-8'))
  return {
    slug: file.replace('src/content/docs/', '').replace(/\.mdx$/, ''),
    ...data,
  }
})

fs.writeFileSync(
  'src/lib/graphql/docs-index.json',
  JSON.stringify(endpoints, null, 2)
)
```

```ts
// src/lib/graphql/docs-data.ts (生产环境版本)
// 直接 import 构建时生成的 JSON
import docsIndex from './docs-index.json'

export function getAllApiEndpoints(): ApiEndpointMeta[] {
  return docsIndex as ApiEndpointMeta[]
}
```

在 `package.json` 中添加构建脚本：

```json
{
  "scripts": {
    "prebuild": "tsx scripts/build-docs-index.ts",
    "predev": "tsx scripts/build-docs-index.ts",
    "build": "next build",
    "dev": "next dev"
  }
}
```

### 2. GraphQL 查询缓存

urql 默认启用了 `cacheExchange`，文档场景建议使用默认缓存即可。如果需要更精细控制：

```ts
// src/lib/graphql/client.ts
import { Client, cacheExchange, fetchExchange, dedupExchange } from 'urql'

export const urqlClient = new Client({
  url: '/api/graphql',
  exchanges: [
    dedupExchange,   // 去重重复请求
    cacheExchange,   // 缓存
    fetchExchange,   // 网络请求
  ],
  // 文档数据很少变化，可以设置较长的缓存时间
  requestPolicy: 'cache-first',
})
```

### 3. 组件懒加载

页面上的查询组件可以使用 `next/dynamic` 延迟加载，减少首屏 JS：

```tsx
import dynamic from 'next/dynamic'

// 相关 API 列表不需要首屏立即显示，懒加载
const ApiEndpointsList = dynamic(
  () => import('@/components/ApiEndpointsList'),
  {
    loading: () => <div className="h-20 bg-gray-100 animate-pulse rounded" />,
    ssr: false, // 客户端组件不需要 SSR
  }
)
```

### 4. Persisted Queries（可选）

对于固定查询（非动态拼接的查询），可以使用 Persisted Queries 减少网络传输，但这对文档站来说通常是过度优化。

## 安全考虑

### 1. 生产环境禁用 GraphiQL

```ts
// src/app/api/graphql/route.ts
const { handleRequest } = createYoga({
  schema,
  graphqlEndpoint: '/api/graphql',
  fetchAPI: { Response },
  // 只在开发环境启用 GraphiQL
  graphiql: process.env.NODE_ENV === 'development',
  // 生产环境考虑禁用 introspection（但会影响外部工具发现能力）
  // introspection: process.env.NODE_ENV !== 'production',
})
```

**注意**：如果你希望外部工具（IDE 插件、CLI 工具、AI agents）能自动发现文档结构，**必须**保留 introspection。文档数据通常不是敏感数据，开启 introspection 通常是可接受的。

### 2. 查询深度/复杂度限制

防止恶意复杂查询拖垮服务器：

```ts
import { createYoga } from 'graphql-yoga'
import { createGraphQLError } from 'graphql-yoga'

const MAX_DEPTH = 5
const MAX_COMPLEXITY = 100

function calculateDepth(info: any): number {
  // 简单实现：遍历 fieldNodes 计算深度
  // 生产环境建议使用 graphql-query-complexity 等库
  return 3 // 简化示例
}

const { handleRequest } = createYoga({
  schema,
  graphqlEndpoint: '/api/graphql',
  fetchAPI: { Response },
  graphiql: process.env.NODE_ENV === 'development',
  plugins: [
    {
      onValidate({ context, setResult }) {
        // 深度限制逻辑
      },
    },
  ],
})
```

对于文档站，由于 resolver 只是从内存缓存中读取数据，性能风险很低，深度限制可以放宽。

### 3. CORS 配置

如果 GraphQL 端点需要被外部域名访问（如 IDE 插件从不同域名查询），配置 CORS：

```ts
const { handleRequest } = createYoga({
  schema,
  graphqlEndpoint: '/api/graphql',
  fetchAPI: { Response },
  cors: {
    origin: ['https://your-ide-plugin.com', 'tauri://localhost'], // 允许的来源
    credentials: true,
    methods: ['POST', 'GET'], // GET 方便 GraphiQL
  },
})
```

## 生产部署

### Vercel（推荐）

Vercel 是 Next.js 的官方托管平台，零配置部署：

```bash
# 安装 Vercel CLI
pnpm add -g vercel

# 部署
vercel --prod
```

在 Vercel 项目设置中确保：
- **Node.js Version**：18.x 或更高
- **Build Command**：`pnpm build`（会自动执行 prebuild 脚本）
- **Output Directory**：`.next`（默认）

### Docker 部署

```dockerfile
FROM node:18-alpine AS base
FROM base AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml* ./
RUN corepack enable pnpm && pnpm fetch --frozen-lockfile

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN corepack enable pnpm && pnpm build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
ENV PORT=3000
CMD ["node", "server.js"]
```

在 `next.config.mjs` 中启用 standalone 输出：

```js
const nextConfig = {
  output: 'standalone',
  // ...
}
```

### 静态导出（无服务器）

如果你的文档不需要运行时 GraphQL 服务器（所有查询都在构建时执行），可以静态导出：

```js
// next.config.mjs
const nextConfig = {
  output: 'export',
  // ...
}
```

但这意味着 `/api/graphql` 端点不会被部署——你需要将 GraphQL 服务器托管到其他地方（如 Cloudflare Workers、Supabase Edge Functions），或者所有查询都在构建时通过 Server Component 执行。

## 与 OKF 开放知识协议集成

基于 [Sphinx × GraphQL × OKF 组合洞察](../../../../retrospective/reports/insight-extraction/external-learning/retrospective-sphinx-graphql-okf-combination-insights-20260805/insight-extraction.md)，MDX + GraphQL 可以很自然地扩展 OKF 的三个核心层：

### 许可层嵌入（OKF 协议层 → 生产层）

在构建时自动注入开放许可元数据：

```ts
// src/lib/okf/license-metadata.ts
export interface LicenseInfo {
  type: 'CC0-1.0' | 'CC-BY-4.0' | 'CC-BY-SA-4.0' | 'MIT'
  url: string
  holder: string
}

// 在 GraphQL Schema 中添加许可字段
// ApiEndpoint 类型增加：
//   license: LicenseInfo
//   contributors: [Contributor]
//   sourceUrl: String
```

在 MDX frontmatter 中声明：

```mdx
---
title: "capitalize"
license: "MIT"
contributors:
  - name: "张三"
    url: "https://github.com/zhangsan"
sourceRepository: "https://github.com/your-org/str-utils"
---
```

### 知识互联（OKF 协议层 → 接口层）

GraphQL 天然支持跨源联邦。可以扩展 Schema 链接到外部开放知识库：

```ts
// src/lib/graphql/schema.ts
const ExternalKnowledgeRef = builder.objectRef<{
  source: 'wikidata' | 'dbpedia' | 'schemaorg'
  id: string
  label: string
  url: string
}>('ExternalKnowledge')

// ApiEndpoint 增加字段：
//   sameAs: [ExternalKnowledge]  // 链接到开放知识图谱
```

```ts
// resolver 中可以链接到 Wikidata 等开放知识库
sameAs: t.field({
  type: [ExternalKnowledgeRef],
  resolve: (endpoint) => {
    // 示例：如果函数名对应 Wikidata 上的概念，返回关联
    const mappings: Record<string, any[]> = {
      capitalize: [{ source: 'wikidata', id: 'Q116884066', label: 'Capitalization', url: 'https://www.wikidata.org/wiki/Q116884066' }],
    }
    return mappings[endpoint.title] ?? []
  },
}),
```

### JSON-LD 输出

为每个文档页面生成 JSON-LD 结构化数据，供搜索引擎和知识图谱消费：

```tsx
// src/app/docs/[...slug]/page.tsx
export async function generateMetadata({ params }: DocPageProps) {
  const endpoint = getApiEndpointBySlug(params.slug.join('/'))
  if (!endpoint) return {}

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'APIReference',
    name: endpoint.title,
    description: endpoint.description,
    license: 'https://opensource.org/licenses/MIT',
    // ...
  }

  return {
    title: `${endpoint.title} - API 文档`,
    description: endpoint.description,
    other: {
      'script:ld+json': JSON.stringify(jsonLd),
    },
  }
}
```

### 联邦查询网关（OKF 愿景级）

如果需要连接多个开放文档站，可以使用 [GraphQL Federation](https://www.apollographql.com/docs/federation/) 构建统一网关：

```ts
// gateway.ts（独立服务）
import { createYoga } from 'graphql-yoga'
import { buildSubgraphSchema } from '@apollo/subgraph'

// 各文档站作为 subgraph 暴露部分 Schema
// 网关将多个 subgraph 拼接成统一知识图
```

这是愿景级功能，适合大型开放知识平台，大多数项目不需要一开始就做。

## 使用其他框架

### 不使用 Next.js？

如果你使用其他框架，核心思路相同：

| 框架 | MDX 集成 | GraphQL 服务器 |
|------|---------|---------------|
| **Astro** | `@astrojs/mdx` 官方集成 | 用 `astro:api` 端点或独立服务器 |
| **Remix** | `@mdx-js/rollup` 等插件 | Remix route 作为 GraphQL 端点 |
| **Docusaurus** | 原生支持 MDX | 需要 plugin 或独立服务 |
| **Vite + React** | `@mdx-js/rollup` | `graphql-yoga` 配合 vite 插件 |

### 不使用 Pothos？

如果你更熟悉 SDL 方式定义 Schema，使用 `graphql-tools`：

```ts
// src/lib/graphql/schema.ts
import { makeExecutableSchema } from '@graphql-tools/schema'
import { getAllApiEndpoints, getApiEndpointBySlug } from './docs-data'

const typeDefs = `
  type Param {
    name: String!
    type: String!
    description: String!
    required: Boolean
  }

  type ApiEndpoint {
    slug: String!
    title: String!
    description: String!
    category: String!
    returnType: String!
    params: [Param!]!
    deprecated: Boolean
    since: String
  }

  type Query {
    apiEndpoints(category: String, includeDeprecated: Boolean): [ApiEndpoint!]!
    apiEndpoint(slug: String!): ApiEndpoint
    categories: [String!]!
  }
`

const resolvers = {
  Query: {
    apiEndpoints: (_: any, args: { category?: string; includeDeprecated?: boolean }) => {
      let endpoints = getAllApiEndpoints()
      if (args.category) endpoints = endpoints.filter(e => e.category === args.category)
      if (!args.includeDeprecated) endpoints = endpoints.filter(e => !e.deprecated)
      return endpoints
    },
    apiEndpoint: (_: any, args: { slug: string }) => getApiEndpointBySlug(args.slug),
    categories: () => [...new Set(getAllApiEndpoints().map(e => e.category))],
  },
}

export const schema = makeExecutableSchema({ typeDefs, resolvers })
```

### 不使用 urql？

**Apollo Client**：

```bash
pnpm add @apollo/client
```

```tsx
'use client'
import { ApolloClient, InMemoryCache, ApolloProvider } from '@apollo/client'

const client = new ApolloClient({
  uri: '/api/graphql',
  cache: new InMemoryCache(),
})

export function GraphQLProvider({ children }: { children: React.ReactNode }) {
  return <ApolloProvider client={client}>{children}</ApolloProvider>
}
```

**React Query + graphql-request**（最精简方案）：

```bash
pnpm add @tanstack/react-query graphql-request graphql
```

```tsx
'use client'
import { request } from 'graphql-request'
import { useQuery } from '@tanstack/react-query'

const query = gql`
  query GetEndpoints($category: String) {
    apiEndpoints(category: $category) { slug title description returnType }
  }
`

function EndpointList({ category }: { category: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ['endpoints', category],
    queryFn: () => request('/api/graphql', query, { category }),
  })
  // ...
}
```

## 常见问题 FAQ

### Q: 为什么不用 Docusaurus？

Docusaurus 是优秀的文档框架，如果你只需要传统文档站，它是很好的选择。MDX + GraphQL 的方案适合你有以下需求时：
- 需要在文档中嵌入动态数据驱动的组件
- 需要为 IDE/CLI/AI agents 提供文档查询 API
- 需要跨文档站的知识联邦查询
- 团队熟悉 Next.js 且希望统一技术栈

Docusaurus 也可以通过插件添加 GraphQL 端点，但灵活性不如 Next.js 的 Route Handlers。

### Q: 为什么不用 OpenAPI/Swagger？

OpenAPI 是 REST API 描述规范，GraphQL 是查询语言——它们解决不同问题：
- OpenAPI 适合描述 REST API 的请求/响应格式
- GraphQL 适合作为**文档内容本身**的查询接口

对于文档场景，你可能两者都需要：用 OpenAPI 描述你的 REST API，用 MDX+GraphQL 让文档可被查询。

### Q: 文档内容量很大（1000+ 页面）时性能如何？

内存缓存方案加载 1000+ MDX 文件的 frontmatter 通常在 50-200ms 之间（首次），后续请求 <1ms（缓存命中）。如果更大，可以：
1. 构建时预生成 JSON 索引（推荐）
2. 使用 SQLite/LevelDB 存储索引
3. 分页查询（GraphQL Connection 模式）

### Q: 如何支持全文搜索？

GraphQL 适合结构化查询（按分类、按返回类型、按版本筛选），全文搜索建议搭配专门的搜索方案：
- **轻量级**：[MiniSearch](https://lucaong.github.io/minisearch/) 在客户端构建索引
- **中量级**：构建时生成 Lunr.js/Elasticlunr 索引
- **生产级**：Algolia DocSearch / Meilisearch / Typesense

可以在 GraphQL Schema 中添加 search 字段，后端对接搜索引擎：

```ts
search: t.field({
  type: [SearchResultRef],
  args: { query: t.arg.string({ required: true }) },
  resolve: (_, args) => searchIndex.search(args.query),
}),
```

### Q: 如何将文档 Schema 与代码中的 TypeScript 类型自动同步？

如果文档描述的是 TypeScript 库，可以使用 [TypeDoc](https://typedoc.org/) 或 [API Extractor](https://api-extractor.com/) 从源码提取类型信息，在构建时生成 GraphQL Schema 和 MDX 模板文件，避免手动维护 frontmatter 与代码类型不一致。

### Q: 可以在 MDX 中直接写 GraphQL 查询吗（类似 MDX + gql 标签）？

可以！以下是一个更"Declarative"的模式（需要自定义 MDX 插件）：

```mdx
---
title: "capitalize"
---

import { Query } from '@/components/Query'

# capitalize

<Query query={`
  query RelatedTo($slug: String = "string/capitalize") {
    apiEndpoint(slug: $slug) {
      seeAlso {
        slug
        title
        description
      }
    }
  }
`}>
  {({ data, fetching }) => fetching ? <Loading /> : (
    <RelatedList items={data?.apiEndpoint?.seeAlso ?? []} />
  )}
</Query>
```

这种"内联查询"模式非常灵活，但在文档中混入过多查询逻辑会影响可读性。推荐对常用查询模式封装成命名组件（如 `<ApiEndpointsList>`），MDX 作者不需要写 GraphQL。

### Q: 和 GitBook/Notion/Confluence 等文档工具有什么区别？

这些工具是 SaaS 文档产品，MDX+GraphQL 是**你自己可控的技术方案**：
- GitBook/Notion：开箱即用，但定制性有限，数据在他人平台，无法提供 GraphQL API
- MDX+GraphQL：需要开发，但完全可控，可以深度集成到你的开发工具链

## 学习资源

- [GraphQL Yoga 官方文档](https://the-guild.dev/graphql/yoga-server)
- [Pothos GraphQL 官方文档](https://pothos-graphql.dev/)
- [urql 官方文档](https://formidable.com/open-source/urql/)
- [Next.js MDX 文档](https://nextjs.org/docs/app/building-your-application/configuring/mdx)
- [MDX 官方文档](https://mdxjs.com/)
- [Sphinx × GraphQL × OKF 组合洞察报告](../../../../retrospective/reports/insight-extraction/external-learning/retrospective-sphinx-graphql-okf-combination-insights-20260805/insight-extraction.md)

---

本指南到此结束。恭喜你完成了 MDX + GraphQL 可查询文档的完整学习路径！🚀

← 上一章：[查询组件开发](02-query-components.md) | [返回目录](README.md) | 下一章：无
