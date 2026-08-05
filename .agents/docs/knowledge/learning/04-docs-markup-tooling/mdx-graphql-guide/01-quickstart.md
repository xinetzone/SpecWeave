---
title: "MDX + GraphQL 5分钟快速上手"
source: "insight:retrospective-sphinx-graphql-okf-combination-insights-20260805"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/04-docs-markup-tooling/mdx-graphql-guide/01-quickstart.toml"
date: "2026-08-05"
tags: [mdx, graphql, quickstart, nextjs, tutorial]
category: "learning"
status: "stable"
summary: "从零开始：创建Next.js项目→配置MDX→定义GraphQL Schema→嵌入查询组件→运行验证，含完整可复制代码"
---
# 01 - 5分钟快速上手

> 本章目标：15 分钟内从零搭建一个可运行的「可查询文档站」。完成后你会得到一个 Next.js 项目，其中的 API 文档既可以作为网页浏览，也可以通过 GraphQL 端点查询。

## 示例场景

我们将为一个假想的字符串工具库 `str-utils` 构建文档站，支持：
- 浏览所有 API 端点的文档页面
- 在文档中嵌入动态的「相关 API」列表（通过 GraphQL 查询）
- 通过 `/api/graphql` 端点查询文档数据

## 前置环境

- Node.js 18+ 
- npm / pnpm / yarn（本指南使用 pnpm，其他包管理器命令类似）

## 步骤 1：创建 Next.js 项目

```bash
pnpm create next-app@latest queryable-docs \
  --typescript \
  --eslint \
  --tailwind \
  --app \
  --src-dir \
  --no-import-alias

cd queryable-docs
```

## 步骤 2：安装依赖

安装 MDX 和 GraphQL 相关依赖：

```bash
# MDX 支持
pnpm add @next/mdx @mdx-js/loader @mdx-js/react @types/mdx

# GraphQL 服务器
pnpm add graphql graphql-yoga @pothos/core

# GraphQL 客户端（urql 轻量方案）
pnpm add urql graphql

# 开发依赖：从 MDX 文件读取 frontmatter
pnpm add -D gray-matter glob
pnpm add -D @types/glob
```

## 步骤 3：配置 Next.js 支持 MDX

创建/修改 `next.config.mjs`：

```js
// next.config.mjs
import createMDX from '@next/mdx'

/** @type {import('next').NextConfig} */
const nextConfig = {
  pageExtensions: ['js', 'jsx', 'md', 'mdx', 'ts', 'tsx'],
}

const withMDX = createMDX({
  options: {
    remarkPlugins: [],
    rehypePlugins: [],
  },
})

export default withMDX(nextConfig)
```

在 `src/app/` 下创建 `mdx-components.tsx`：

```tsx
// src/app/mdx-components.tsx
import type { MDXComponents } from 'mdx/types'

export function useMDXComponents(components: MDXComponents): MDXComponents {
  return {
    ...components,
  }
}
```

## 步骤 4：定义 GraphQL Schema

创建 `src/lib/graphql/schema.ts`，使用 Pothos 代码优先方式定义文档类型系统：

```ts
// src/lib/graphql/schema.ts
import SchemaBuilder from '@pothos/core'
import { getAllApiEndpoints, getApiEndpointBySlug } from './docs-data'

const builder = new SchemaBuilder({})

// 定义 API 参数类型
const ParamRef = builder.objectRef<{ name: string; type: string; description: string; required?: boolean }>('Param')
ParamRef.implement({
  fields: (t) => ({
    name: t.exposeString('name'),
    type: t.exposeString('type'),
    description: t.exposeString('description'),
    required: t.exposeBoolean('required', { nullable: true }),
  }),
})

// 定义 API 端点类型（这是核心文档模型）
const ApiEndpointRef = builder.objectRef<{
  slug: string
  title: string
  description: string
  category: string
  returnType: string
  params: { name: string; type: string; description: string; required?: boolean }[]
  deprecated?: boolean
  since?: string
}>('ApiEndpoint')

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
  }),
})

// 定义 Query（查询入口）
builder.queryType({
  fields: (t) => ({
    // 查询所有 API 端点
    apiEndpoints: t.field({
      type: [ApiEndpointRef],
      args: {
        category: t.arg.string(),
        includeDeprecated: t.arg.boolean(),
      },
      resolve: (_root, args) => {
        let endpoints = getAllApiEndpoints()
        if (args.category) {
          endpoints = endpoints.filter((e) => e.category === args.category)
        }
        if (args.includeDeprecated !== true) {
          // 默认不展示已废弃的 API，除非显式传 includeDeprecated: true
          endpoints = endpoints.filter((e) => !e.deprecated)
        }
        return endpoints
      },
    }),
    // 按 slug 查询单个端点
    apiEndpoint: t.field({
      type: ApiEndpointRef,
      args: {
        slug: t.arg.string({ required: true }),
      },
      resolve: (_root, args) => getApiEndpointBySlug(args.slug),
    }),
    // 查询所有分类
    categories: t.field({
      type: ['String'],
      resolve: () => {
        const endpoints = getAllApiEndpoints()
        return [...new Set(endpoints.map((e) => e.category))]
      },
    }),
  }),
})

export const schema = builder.toSchema()
```

## 步骤 5：实现文档数据加载器

创建 `src/lib/graphql/docs-data.ts`，从 MDX 文件中提取 frontmatter 作为数据源：

```ts
// src/lib/graphql/docs-data.ts
import fs from 'node:fs'
import path from 'node:path'
import matter from 'gray-matter'
import { glob } from 'glob'

export interface ApiEndpointMeta {
  slug: string
  title: string
  description: string
  category: string
  returnType: string
  params: { name: string; type: string; description: string; required?: boolean }[]
  deprecated?: boolean
  since?: string
}

const DOCS_DIR = path.join(process.cwd(), 'src/content/docs')

// 缓存，避免每次请求都读文件
let cache: ApiEndpointMeta[] | null = null

function loadAllEndpoints(): ApiEndpointMeta[] {
  if (cache) return cache

  const files = glob.sync('**/*.mdx', { cwd: DOCS_DIR })
  const endpoints: ApiEndpointMeta[] = []

  for (const file of files) {
    const filePath = path.join(DOCS_DIR, file)
    const content = fs.readFileSync(filePath, 'utf-8')
    const { data } = matter(content)

    // slug 从文件路径推导：category/endpoint.mdx → category/endpoint
    const slug = file.replace(/\.mdx$/, '')

    endpoints.push({
      slug,
      title: data.title ?? slug,
      description: data.description ?? '',
      category: data.category ?? 'misc',
      returnType: data.returnType ?? 'void',
      params: data.params ?? [],
      deprecated: data.deprecated ?? false,
      since: data.since,
    })
  }

  cache = endpoints
  return endpoints
}

export function getAllApiEndpoints(): ApiEndpointMeta[] {
  return loadAllEndpoints()
}

export function getApiEndpointBySlug(slug: string): ApiEndpointMeta | null {
  const endpoints = loadAllEndpoints()
  return endpoints.find((e) => e.slug === slug) ?? null
}

// 开发环境下清除缓存（方便热更新）
if (process.env.NODE_ENV === 'development') {
  // 文件变更时清缓存（Next.js dev 模式下每次请求会重新执行模块，无需手动处理）
}
```

## 步骤 6：创建 GraphQL API 端点

创建 `src/app/api/graphql/route.ts`：

```ts
// src/app/api/graphql/route.ts
import { createYoga } from 'graphql-yoga'
import { schema } from '@/lib/graphql/schema'

const { handleRequest } = createYoga({
  schema,
  graphqlEndpoint: '/api/graphql',
  fetchAPI: { Response },
  // 开发环境启用 GraphiQL
  graphiql: process.env.NODE_ENV === 'development',
})

export { handleRequest as GET, handleRequest as POST }
```

## 步骤 7：配置 urql 客户端

创建 `src/lib/graphql/client.ts`：

```ts
// src/lib/graphql/client.ts
import { Client, cacheExchange, fetchExchange } from 'urql'

export const urqlClient = new Client({
  url: '/api/graphql',
  exchanges: [cacheExchange, fetchExchange],
})
```

创建客户端 Provider（Client Component，因为 urql 需要在浏览器端运行）：

```tsx
// src/components/GraphQLProvider.tsx
'use client'

import { Provider } from 'urql'
import { urqlClient } from '@/lib/graphql/client'

export function GraphQLProvider({ children }: { children: React.ReactNode }) {
  return <Provider value={urqlClient}>{children}</Provider>
}
```

修改 `src/app/layout.tsx`，包裹 Provider：

```tsx
// src/app/layout.tsx
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { GraphQLProvider } from '@/components/GraphQLProvider'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'str-utils 文档',
  description: '可查询的 API 文档站',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body className={inter.className}>
        <GraphQLProvider>{children}</GraphQLProvider>
      </body>
    </html>
  )
}
```

## 步骤 8：创建 MDX 文档内容

创建文档目录和内容文件：

```bash
mkdir -p src/content/docs/string src/content/docs/array
```

创建 `src/content/docs/string/capitalize.mdx`：

```mdx
---
title: "capitalize"
description: "将字符串首字母大写"
category: "string"
returnType: "string"
params:
  - name: "str"
    type: "string"
    description: "输入字符串"
    required: true
since: "1.0.0"
---

import { ApiEndpointsList } from '@/components/ApiEndpointsList'

# capitalize

将字符串的首字母转换为大写，其余字母保持不变。

## 用法

\`\`\`ts
import { capitalize } from 'str-utils'

capitalize('hello') // 'Hello'
capitalize('world') // 'World'
\`\`\`

## 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| str | string | ✅ | 要处理的输入字符串 |

## 返回值

返回首字母大写后的新字符串。

## 相关 API（动态查询）

下面的列表通过 GraphQL 实时查询获取，展示同分类下的其他 API：

<ApiEndpointsList category="string" excludeSlug="string/capitalize" />
```

创建 `src/content/docs/string/truncate.mdx`：

```mdx
---
title: "truncate"
description: "截断字符串到指定长度"
category: "string"
returnType: "string"
params:
  - name: "str"
    type: "string"
    description: "输入字符串"
    required: true
  - name: "length"
    type: "number"
    description: "最大长度"
    required: true
  - name: "suffix"
    type: "string"
    description: "截断后追加的后缀，默认为 '...'"
    required: false
since: "1.0.0"
---

# truncate

将字符串截断到指定长度，超出部分用省略号（或自定义后缀）代替。

## 用法

\`\`\`ts
import { truncate } from 'str-utils'

truncate('hello world', 5)        // 'hello...'
truncate('hello world', 8, '…')   // 'hello wo…'
\`\`\`
```

创建 `src/content/docs/string/kebab-case.mdx`：

```mdx
---
title: "kebabCase"
description: "将字符串转换为 kebab-case 格式"
category: "string"
returnType: "string"
params:
  - name: "str"
    type: "string"
    description: "输入字符串"
    required: true
since: "1.2.0"
deprecated: false
---

# kebabCase

将驼峰命名或空格分隔的字符串转换为 kebab-case（短横线分隔）格式。

## 用法

\`\`\`ts
import { kebabCase } from 'str-utils'

kebabCase('helloWorld')  // 'hello-world'
kebabCase('Hello World') // 'hello-world'
\`\`\`
```

创建 `src/content/docs/array/chunk.mdx`：

```mdx
---
title: "chunk"
description: "将数组按指定大小分块"
category: "array"
returnType: "T[][]"
params:
  - name: "arr"
    type: "T[]"
    description: "输入数组"
    required: true
  - name: "size"
    type: "number"
    description: "每块的大小"
    required: true
since: "2.0.0"
---

# chunk

将数组按指定大小分割成多个子数组。

## 用法

\`\`\`ts
import { chunk } from 'str-utils'

chunk([1, 2, 3, 4, 5], 2) // [[1, 2], [3, 4], [5]]
\`\`\`
```

## 步骤 9：创建 GraphQL 查询组件

创建核心的 `<ApiEndpointsList>` 组件，这是 MDX 中嵌入的动态查询组件：

```tsx
// src/components/ApiEndpointsList.tsx
'use client'

import { useQuery, gql } from 'urql'
import Link from 'next/link'

const API_ENDPOINTS_QUERY = gql`
  query GetApiEndpoints($category: String, $excludeSlug: String) {
    apiEndpoints(category: $category) {
      slug
      title
      description
      returnType
      deprecated
    }
  }
`

interface ApiEndpointsListProps {
  category?: string
  excludeSlug?: string
}

export function ApiEndpointsList({ category, excludeSlug }: ApiEndpointsListProps) {
  const [{ data, fetching, error }] = useQuery({
    query: API_ENDPOINTS_QUERY,
    variables: { category },
  })

  if (fetching) return <div className="text-sm text-gray-500">加载中...</div>
  if (error) return <div className="text-sm text-red-500">加载失败: {error.message}</div>

  let endpoints = data?.apiEndpoints ?? []
  if (excludeSlug) {
    endpoints = endpoints.filter((e: { slug: string }) => e.slug !== excludeSlug)
  }

  if (endpoints.length === 0) {
    return <div className="text-sm text-gray-400">暂无相关 API</div>
  }

  return (
    <div className="not-prose my-4 rounded-lg border border-gray-200 divide-y">
      {endpoints.map((endpoint: {
        slug: string
        title: string
        description: string
        returnType: string
        deprecated?: boolean
      }) => (
        <Link
          key={endpoint.slug}
          href={`/docs/${endpoint.slug}`}
          className="block px-4 py-3 hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center gap-2">
            <code className="text-sm font-mono font-semibold text-blue-600">
              {endpoint.title}
            </code>
            <span className="text-xs text-gray-400">→ {endpoint.returnType}</span>
            {endpoint.deprecated && (
              <span className="text-xs px-1.5 py-0.5 bg-yellow-100 text-yellow-700 rounded">
                已废弃
              </span>
            )}
          </div>
          <p className="text-sm text-gray-600 mt-1">{endpoint.description}</p>
        </Link>
      ))}
    </div>
  )
}
```

> **注意**：上面代码中的 `not-prose` 类需要 Tailwind Typography 插件。如果没装，可以去掉 `not-prose` 和 `className` 中的 Tailwind 类，用普通样式替代。

安装 Tailwind Typography（推荐，用于 MDX 内容排版）：

```bash
pnpm add -D @tailwindcss/typography
```

更新 `tailwind.config.ts`：

```ts
// tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/content/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [require('@tailwindcss/typography')],
}
export default config
```

## 步骤 10：创建动态路由渲染 MDX 文档

创建 `src/app/docs/[...slug]/page.tsx`，动态加载 MDX 文件：

```tsx
// src/app/docs/[...slug]/page.tsx
import fs from 'node:fs'
import path from 'node:path'
import { notFound } from 'next/navigation'
import { getAllApiEndpoints } from '@/lib/graphql/docs-data'

interface DocPageProps {
  params: { slug: string[] }
}

// 静态生成所有文档页面
export async function generateStaticParams() {
  const endpoints = getAllApiEndpoints()
  return endpoints.map((e) => ({
    slug: e.slug.split('/'),
  }))
}

export default async function DocPage({ params }: DocPageProps) {
  const slug = params.slug.join('/')
  const filePath = path.join(process.cwd(), 'src/content/docs', `${slug}.mdx`)

  if (!fs.existsSync(filePath)) {
    notFound()
  }

  // 动态导入 MDX 文件
  const { default: MDXContent } = await import(`../../../content/docs/${slug}.mdx`)

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <nav className="mb-6 text-sm text-gray-500">
        <a href="/" className="hover:text-blue-600">首页</a>
        <span className="mx-2">/</span>
        <a href="/docs" className="hover:text-blue-600">文档</a>
        <span className="mx-2">/</span>
        <span className="text-gray-900">{slug}</span>
      </nav>
      <article className="prose prose-lg max-w-none">
        <MDXContent />
      </article>
    </div>
  )
}
```

创建文档首页 `src/app/docs/page.tsx`：

```tsx
// src/app/docs/page.tsx
import { ApiEndpointsIndex } from '@/components/ApiEndpointsIndex'

export default function DocsIndex() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-2">API 文档</h1>
      <p className="text-gray-600 mb-8">str-utils 库的完整 API 参考</p>
      <ApiEndpointsIndex />
    </div>
  )
}
```

创建 `src/components/ApiEndpointsIndex.tsx`（服务端组件，直接调用数据函数，不需要 GraphQL 客户端开销）：

```tsx
// src/components/ApiEndpointsIndex.tsx
import Link from 'next/link'
import { getAllApiEndpoints } from '@/lib/graphql/docs-data'

export function ApiEndpointsIndex() {
  const endpoints = getAllApiEndpoints()
  const categories = [...new Set(endpoints.map((e) => e.category))]

  return (
    <div className="space-y-8">
      {categories.map((category) => (
        <div key={category}>
          <h2 className="text-xl font-semibold mb-3 capitalize">{category}</h2>
          <div className="grid gap-2">
            {endpoints
              .filter((e) => e.category === category)
              .map((endpoint) => (
                <Link
                  key={endpoint.slug}
                  href={`/docs/${endpoint.slug}`}
                  className="block p-4 rounded-lg border hover:border-blue-300 hover:bg-blue-50/30 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <code className="font-mono font-semibold text-blue-600">
                      {endpoint.title}
                    </code>
                    <span className="text-sm text-gray-400">→ {endpoint.returnType}</span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{endpoint.description}</p>
                </Link>
              ))}
          </div>
        </div>
      ))}
    </div>
  )
}
```

创建首页 `src/app/page.tsx`：

```tsx
// src/app/page.tsx
import Link from 'next/link'

export default function Home() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-16">
      <h1 className="text-4xl font-bold mb-4">str-utils</h1>
      <p className="text-xl text-gray-600 mb-8">
        一个实用的字符串处理工具库。文档采用 MDX + GraphQL 构建，支持程序化查询。
      </p>
      <div className="flex gap-4">
        <Link
          href="/docs"
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          查看文档
        </Link>
        <a
          href="/api/graphql"
          target="_blank"
          className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          打开 GraphQL Playground
        </a>
      </div>
    </div>
  )
}
```

## 步骤 11：运行验证

```bash
pnpm dev
```

打开浏览器验证以下功能：

1. **http://localhost:3000** — 首页，点击"查看文档"或"GraphQL Playground"
2. **http://localhost:3000/docs** — 文档索引页，按分类展示所有 API
3. **http://localhost:3000/docs/string/capitalize** — 单个 API 文档页，底部有通过 GraphQL 动态加载的"相关 API"列表
4. **http://localhost:3000/api/graphql** — GraphiQL 交互式查询界面

### 在 GraphiQL 中尝试查询

打开 GraphiQL（步骤4中开发环境自动启用），尝试以下查询：

**查询所有 string 类别的 API**：
```graphql
query {
  apiEndpoints(category: "string") {
    title
    description
    returnType
    params {
      name
      type
      required
    }
  }
}
```

**查询特定 API 的详情**：
```graphql
query {
  apiEndpoint(slug: "string/truncate") {
    title
    description
    returnType
    params {
      name
      type
      description
    }
  }
}
```

**查询所有分类**：
```graphql
query {
  categories
}
```

## 验收标准

完成以上步骤后，你应该能确认：

- [ ] `pnpm dev` 无报错启动
- [ ] 可以浏览 `/docs` 页面看到所有 API 列表
- [ ] 点击进入单个 API 页面，正文正常渲染
- [ ] 页面底部的"相关 API"列表通过 GraphQL 动态加载显示
- [ ] 访问 `/api/graphql` 可以打开 GraphiQL
- [ ] 在 GraphiQL 中执行上述查询返回正确数据

## 项目结构概览

完成后的项目核心文件结构：

```
queryable-docs/
├── src/
│   ├── app/
│   │   ├── api/graphql/route.ts    # GraphQL API 端点
│   │   ├── docs/
│   │   │   ├── [...slug]/page.tsx  # 动态文档页面
│   │   │   └── page.tsx            # 文档索引
│   │   ├── page.tsx                # 首页
│   │   ├── layout.tsx              # 根布局（含 GraphQLProvider）
│   │   └── mdx-components.tsx      # MDX 组件配置
│   ├── components/
│   │   ├── ApiEndpointsList.tsx    # GraphQL 查询组件（动态列表）
│   │   ├── ApiEndpointsIndex.tsx   # 服务端索引组件
│   │   └── GraphQLProvider.tsx     # urql Provider
│   ├── content/docs/               # MDX 文档内容
│   │   ├── string/
│   │   │   ├── capitalize.mdx
│   │   │   ├── truncate.mdx
│   │   │   └── kebab-case.mdx
│   │   └── array/
│   │       └── chunk.mdx
│   └── lib/graphql/
│       ├── schema.ts               # GraphQL Schema（Pothos 定义）
│       ├── docs-data.ts            # MDX frontmatter 数据加载器
│       └── client.ts               # urql 客户端配置
├── next.config.mjs                 # Next.js + MDX 配置
└── tailwind.config.ts
```

## 常见问题

**Q: MDX 文件中的 `<ApiEndpointsList>` 组件是客户端渲染的，影响 SEO 吗？**
A: 文档正文是 SSG 静态生成的，查询组件是页面加载后动态获取的"增强功能"，不影响正文的 SEO。如果需要 SEO 友好的动态列表，可以在 [02 章](02-query-components.md) 中学习静态生成时的 GraphQL 查询模式。

**Q: 如何添加更多文档元数据字段（如示例代码、版本历史）？**
A: 在 MDX frontmatter 中添加字段，然后在 Schema 中扩展 `ApiEndpoint` 类型的字段定义。详见 [02 章](02-query-components.md)。

**Q: 生产环境部署有什么注意事项？**
A: 确保部署平台支持 Next.js Route Handlers（Vercel/Netlify 开箱即用，其他平台可能需要配置）。详见 [03 章](03-best-practices.md)。

## 下一章

→ [02 - GraphQL 查询组件开发](02-query-components.md)：深入理解文档元数据 Schema 设计、Query 组件模式、静态生成 vs 运行时查询。

---

← 上一章：[概述与核心概念](00-overview.md) | [目录](README.md) | 下一章：[查询组件开发](02-query-components.md) →
