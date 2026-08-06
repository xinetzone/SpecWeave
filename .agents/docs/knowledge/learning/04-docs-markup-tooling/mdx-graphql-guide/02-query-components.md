---
title: "MDX + GraphQL 查询组件开发"
source: "insight:retrospective-sphinx-graphql-okf-combination-insights-20260805"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/04-docs-markup-tooling/mdx-graphql-guide/02-query-components.toml"
date: "2026-08-05"
tags: [mdx, graphql, components, schema, patterns]
category: "learning"
status: "stable"
summary: "深入文档元数据Schema设计、Query组件模式、Fragment复用、静态生成vs运行时查询、服务端组件中的GraphQL"
---
# 02 - GraphQL 查询组件开发

> 本章目标：掌握可查询文档中 GraphQL Schema 设计和查询组件编写模式。学完本章你能够设计自己的文档类型系统，编写可复用的查询组件，并选择合适的数据获取策略。

## Schema 设计进阶

[01 章](01-quickstart.md) 中我们定义了一个简单的 `ApiEndpoint` 类型。真实项目中，文档的类型系统通常更丰富。以下是一些常见扩展方向。

### 扩展文档模型

```ts
// src/lib/graphql/schema.ts
import SchemaBuilder from '@pothos/core'

const builder = new SchemaBuilder({})

// 参数类型（已有）
const ParamRef = builder.objectRef<ParamMeta>('Param')

// 代码示例类型（新增）
const CodeExampleRef = builder.objectRef<{
  language: string
  code: string
  title?: string
}>('CodeExample')
CodeExampleRef.implement({
  fields: (t) => ({
    language: t.exposeString('language'),
    code: t.exposeString('code'),
    title: t.exposeString('title', { nullable: true }),
  }),
})

// 版本变更记录类型（新增）
const VersionNoteRef = builder.objectRef<{
  version: string
  type: 'added' | 'changed' | 'deprecated' | 'removed'
  description: string
}>('VersionNote')
VersionNoteRef.implement({
  fields: (t) => ({
    version: t.exposeString('version'),
    type: t.exposeString('type'),
    description: t.exposeString('description'),
  }),
})

// API 端点类型（扩展版）
const ApiEndpointRef = builder.objectRef<ApiEndpointMeta>('ApiEndpoint')
ApiEndpointRef.implement({
  fields: (t) => ({
    slug: t.exposeString('slug'),
    title: t.exposeString('title'),
    description: t.exposeString('description'),
    category: t.exposeString('category'),
    returnType: t.exposeString('returnType'),
    params: t.expose('params', { type: [ParamRef] }),
    deprecated: t.exposeBoolean('deprecated', { nullable: true }),
    since: t.exposeString('since', { nullable: true }),
    // 新增字段
    examples: t.expose('examples', { type: [CodeExampleRef], nullable: true }),
    versionNotes: t.expose('versionNotes', { type: [VersionNoteRef], nullable: true }),
    seeAlso: t.field({
      type: [ApiEndpointRef],
      resolve: (endpoint) => {
        // 查找同分类的其他端点
        const all = getAllApiEndpoints()
        return all
          .filter((e) => e.category === endpoint.category && e.slug !== endpoint.slug)
          .slice(0, 5)
      },
    }),
    // 关联字段：反向查找引用此 API 的其他端点
    referencedBy: t.field({
      type: [ApiEndpointRef],
      resolve: (endpoint) => {
        const all = getAllApiEndpoints()
        return all.filter((e) =>
          e.description?.includes(endpoint.title) ||
          e.params?.some((p) => p.type.includes(endpoint.title))
        )
      },
    }),
  }),
})
```

对应的 MDX frontmatter 扩展：

```mdx
---
title: "formatDate"
category: "date"
returnType: "string"
since: "1.0.0"
params:
  - name: "date"
    type: "Date"
    description: "日期对象"
    required: true
  - name: "format"
    type: "string"
    description: "格式化模式"
    required: false
examples:
  - language: "ts"
    title: "基础用法"
    code: |
      formatDate(new Date(), 'YYYY-MM-DD')  // '2026-08-05'
  - language: "ts"
    title: "中文格式"
    code: |
      formatDate(new Date(), 'YYYY年MM月DD日')
versionNotes:
  - version: "2.0.0"
    type: "changed"
    description: "默认格式从 'MM/DD/YYYY' 改为 ISO 8601"
---

# formatDate
...正文...
```

### 分类类型

如果分类本身也有元数据（图标、描述、排序等），可以独立建模：

```ts
const CategoryRef = builder.objectRef<{
  slug: string
  name: string
  description: string
  icon?: string
}>('Category')
CategoryRef.implement({
  fields: (t) => ({
    slug: t.exposeString('slug'),
    name: t.exposeString('name'),
    description: t.exposeString('description'),
    icon: t.exposeString('icon', { nullable: true }),
    endpoints: t.field({
      type: [ApiEndpointRef],
      resolve: (cat) => getAllApiEndpoints().filter((e) => e.category === cat.slug),
    }),
    endpointCount: t.field({
      type: 'Int',
      resolve: (cat) => getAllApiEndpoints().filter((e) => e.category === cat.slug).length,
    }),
  }),
})

// 在 Query 中添加
builder.queryType({
  fields: (t) => ({
    categories: t.field({
      type: [CategoryRef],
      resolve: () => {
        // 从配置文件或 MDX 目录的 _category.mdx 读取
        return getCategories()
      },
    }),
    // ... 其他字段
  }),
})
```

## Query 组件模式

### 模式 1：简单列表组件（客户端渲染）

这是 [01 章](01-quickstart.md) 中 `ApiEndpointsList` 使用的模式，适合"增强型"交互内容：

```tsx
'use client'

import { useQuery, gql } from 'urql'

const QUERY = gql`
  query RelatedEndpoints($slug: String!, $category: String!) {
    apiEndpoints(category: $category) {
      slug
      title
      description
      returnType
    }
  }
`

export function RelatedEndpoints({ slug, category }: { slug: string; category: string }) {
  const [{ data, fetching }] = useQuery({
    query: QUERY,
    variables: { slug, category },
  })

  if (fetching) return <Skeleton /> // 骨架屏

  const endpoints = (data?.apiEndpoints ?? [])
    .filter((e: { slug: string }) => e.slug !== slug)

  return (
    <div className="space-y-2">
      {endpoints.map((e: any) => (
        <EndpointCard key={e.slug} endpoint={e} />
      ))}
    </div>
  )
}
```

**使用场景**：页面内的"相关推荐"、"更多内容"等非核心、可延迟加载的列表。

### 模式 2：带搜索/筛选的组件

```tsx
'use client'

import { useQuery, gql } from 'urql'
import { useState, useMemo } from 'react'

const SEARCH_QUERY = gql`
  query SearchEndpoints($query: String, $category: String) {
    apiEndpoints(category: $category) {
      slug
      title
      description
      returnType
      category
      deprecated
    }
  }
`

export function EndpointSearch() {
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState<string | null>(null)
  const [{ data }] = useQuery({ query: SEARCH_QUERY, variables: { category } })

  const filtered = useMemo(() => {
    const endpoints = data?.apiEndpoints ?? []
    if (!search) return endpoints
    const q = search.toLowerCase()
    return endpoints.filter((e: any) =>
      e.title.toLowerCase().includes(q) ||
      e.description.toLowerCase().includes(q)
    )
  }, [data, search])

  return (
    <div>
      <input
        type="search"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="搜索 API..."
        className="w-full px-4 py-2 border rounded-lg"
      />
      {/* 分类筛选按钮 */}
      {/* 结果列表 */}
    </div>
  )
}
```

### 模式 3：SSR/SSG 中的 GraphQL（服务端查询）

如果你希望查询结果在服务端渲染时就填充（有利于 SEO 和首屏速度），可以在 Server Component 中直接执行 GraphQL 查询：

```tsx
// src/components/ServerEndpointList.tsx
// 注意：这是 Server Component，不需要 'use client'
import Link from 'next/link'
import { schema } from '@/lib/graphql/schema'
import { graphql } from 'graphql'

// 在服务端直接执行查询，不需要 HTTP 往返
async function getEndpoints(category?: string) {
  const result = await graphql({
    schema,
    source: `
      query ($category: String) {
        apiEndpoints(category: $category) {
          slug
          title
          description
          returnType
        }
      }
    `,
    variableValues: { category },
  })
  return result.data?.apiEndpoints as any[]
}

export async function ServerEndpointList({ category }: { category?: string }) {
  const endpoints = await getEndpoints(category)

  return (
    <div className="space-y-2">
      {endpoints.map((e) => (
        <Link key={e.slug} href={`/docs/${e.slug}`} className="block p-3 border rounded">
          <code className="font-semibold text-blue-600">{e.title}</code>
          <span className="text-gray-400 ml-2">→ {e.returnType}</span>
          <p className="text-sm text-gray-600 mt-1">{e.description}</p>
        </Link>
      ))}
    </div>
  )
}
```

**优势**：数据在构建时/请求时就已获取，首屏无 loading，SEO 友好。
**劣势**：失去客户端交互性（搜索、筛选需要客户端组件）。

**最佳实践**：首屏核心内容用 Server Component 查询，交互增强部分用 Client Component 查询。

### 模式 4：Fragment 复用

当多个组件需要查询相同字段时，使用 Fragment 避免重复：

```tsx
// src/lib/graphql/fragments.ts
import { gql } from 'urql'

export const ENDPOINT_SUMMARY = gql`
  fragment EndpointSummary on ApiEndpoint {
    slug
    title
    description
    returnType
    deprecated
  }
`
```

```tsx
// 在组件中使用
import { useQuery, gql } from 'urql'
import { ENDPOINT_SUMMARY } from '@/lib/graphql/fragments'

const CATEGORY_QUERY = gql`
  query CategoryEndpoints($category: String!) {
    apiEndpoints(category: $category) {
      ...EndpointSummary
      since
    }
  }
  ${ENDPOINT_SUMMARY}
`
```

## 静态生成 vs 运行时查询：如何选择？

| 策略 | 实现方式 | SEO | 首屏速度 | 交互性 | 适用场景 |
|------|---------|:---:|:-------:|:-----:|---------|
| **SSG + 服务端查询** | `generateStaticParams` + Server Component 执行 graphql() | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | 文档正文、索引页、核心列表 |
| **SSR + 服务端查询** | Server Component 中 graphql() | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | 个性化内容、实时数据 |
| **CSR + 客户端查询** | `'use client'` + urql useQuery | ⭐ | ⭐ | ⭐⭐⭐ | 搜索、筛选、动态推荐、"相关内容"等增强区域 |
| **混合策略** | Server Component 渲染骨架 + Client Component 填充 | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | 大部分文档站推荐 |

**推荐架构**：
1. 文档正文、API 列表索引 → SSG 静态生成（Server Component）
2. 文档中的"相关推荐"、"最近更新" → CSR 客户端查询（增强体验）
3. 全站搜索框 → CSR 客户端查询（强交互）

## 给 MDX 传递 Props

在 Next.js App Router 中，MDX 组件默认不接收来自页面的 props。如果你想将当前页面的 slug/category 等信息传递给 MDX 内的查询组件，有两种方式：

### 方式 1：通过 URL 参数（简单）

在动态路由页面中，查询组件可以用 `usePathname()` 获取当前路径：

```tsx
'use client'

import { usePathname } from 'next/navigation'
import { useQuery, gql } from 'urql'

const RELATED_QUERY = gql`
  query ($slug: String!, $category: String!) {
    apiEndpoint(slug: $slug) {
      category
      seeAlso {
        slug
        title
        description
        returnType
      }
    }
  }
`

export function SmartRelatedList() {
  const pathname = usePathname()
  // 从 /docs/string/capitalize 提取 slug
  const slug = pathname.replace('/docs/', '')

  const [{ data, fetching }] = useQuery({
    query: RELATED_QUERY,
    variables: { slug, category: slug.split('/')[0] },
    pause: !slug, // slug 未就绪时暂停查询
  })

  // ...
}
```

### 方式 2：通过 MDX 组件传参（推荐）

在渲染 MDX 时通过 `useMDXComponents` 传递上下文：

```tsx
// src/app/docs/[...slug]/page.tsx
import { getAllApiEndpoints } from '@/lib/graphql/docs-data'

interface DocPageProps {
  params: { slug: string[] }
}

export default async function DocPage({ params }: DocPageProps) {
  const slug = params.slug.join('/')
  const endpoint = getApiEndpointBySlug(slug)
  const { default: MDXContent } = await import(`../../../content/docs/${slug}.mdx`)

  return (
    <article className="prose prose-lg max-w-none">
      <MDXComponentsProvider currentSlug={slug} currentCategory={endpoint?.category}>
        <MDXContent />
      </MDXComponentsProvider>
    </article>
  )
}
```

```tsx
// src/components/MDXComponentsProvider.tsx
'use client'

import { createContext, useContext } from 'react'

const MDXContext = createContext<{ currentSlug?: string; currentCategory?: string }>({})

export function MDXComponentsProvider({
  children,
  currentSlug,
  currentCategory,
}: {
  children: React.ReactNode
  currentSlug?: string
  currentCategory?: string
}) {
  return (
    <MDXContext.Provider value={{ currentSlug, currentCategory }}>
      {children}
    </MDXContext.Provider>
  )
}

export function useMDXContext() {
  return useContext(MDXContext)
}
```

然后在查询组件中使用：

```tsx
export function RelatedList() {
  const { currentSlug, currentCategory } = useMDXContext()
  // 直接使用，不需要解析 URL
  const [{ data }] = useQuery({
    query: RELATED_QUERY,
    variables: { slug: currentSlug, category: currentCategory },
    pause: !currentSlug,
  })
  // ...
}
```

## Mutation（可选）

文档站通常只需要 Query。如果你需要"在文档中提交反馈"或"标记为有用"等功能，可以添加 Mutation：

```ts
builder.mutationType({
  fields: (t) => ({
    submitFeedback: t.field({
      type: 'Boolean',
      args: {
        endpointSlug: t.arg.string({ required: true }),
        helpful: t.arg.boolean({ required: true }),
        comment: t.arg.string(),
      },
      resolve: (_root, args) => {
        // 保存到数据库/文件/分析服务
        console.log(`Feedback for ${args.endpointSlug}: ${args.helpful}`)
        return true
      },
    }),
  }),
})
```

## 下一章

→ [03 - 最佳实践与FAQ](03-best-practices.md)：性能优化、缓存策略、生产部署、与 OKF 开放知识协议的集成方向。

---

← 上一章：[5分钟快速上手](01-quickstart.md) | [目录](README.md) | 下一章：[最佳实践与FAQ](03-best-practices.md) →
