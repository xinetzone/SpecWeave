# minitest-trigger GitHub Action 深度分析

## 1. 项目概览

**minitest-trigger** 是一个公开的 GitHub Action（`minitap-ai/minitest-trigger`），用于从 CI 工作流触发 Minitest 测试套件。核心特性：
- 通过 GitHub OIDC 认证，无需管理 Secrets
- 上传构建产物（iOS/Android/Web）
- 触发测试执行并通过 GitHub Check Runs 回报结果
- Fire-and-forget 模式，Action 立即退出

### 1.1 核心文件结构

```
minitest-trigger/
├── action.yml                          # GitHub Action 清单
├── src/
│   ├── main.ts                         # 入口文件
│   ├── api.ts                          # HTTP API 客户端
│   ├── validate.ts                     # 构建验证逻辑
│   ├── ci-metadata.ts                  # CI 元数据提取
│   ├── commit-sha.ts                   # PR SHA 解析
│   ├── commit-title.ts                 # Commit Title 解析
│   └── web-targets.ts                  # Web 测试目标解析
├── dist/                               # ncc 打包产物（发布时构建）
├── .github/workflows/
│   ├── ci.yml                          # CI 工作流
│   └── release.yml                     # 发布工作流
└── package.json
```

---

## 2. action.yml 输入输出分析

### 2.1 Inputs 完整列表

| Input | Required | Default | 说明 | 文件引用 |
|---|---|---|---|---|
| `app-slug` | ✅ Yes | — | Minitest 应用 slug | [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/action.yml:9-11](../../../../external/anthropics/claude-code-security-review/action.yml#L9-L11) |
| `user-story-types` | No | — | 逗号分隔的用户故事类型（如 `login,checkout`），与 `user-stories` 互斥 | [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/action.yml:12-14](../../../../external/anthropics/claude-code-security-review/action.yml#L12-L14) |
| `user-stories` | No | — | 用户故事 UUID（换行/逗号分隔），与 `user-story-types` 互斥 | [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/action.yml:15-17](../../../../external/anthropics/claude-code-security-review/action.yml#L15-L17) |
| `run-ios` | No | `'true'` | 是否运行 iOS 测试 | [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/action.yml:18-21](../../../../external/anthropics/claude-code-security-review/action.yml#L18-L21) |
| `run-android` | No | `'true'` | 是否运行 Android 测试 | [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/action.yml:22-25](../../../../external/anthropics/claude-code-security-review/action.yml#L22-L25) |
| `ios-build-path` | No | — | 预构建 iOS 产物路径（`.app` 目录或 `.ipa` 文件） | [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/action.yml:26-28](../../../../external/anthropics/claude-code-security-review/action.yml#L26-L28) |
| `android-build-path` | No | — | 预构建 Android `.apk` 路径（必须 x86-64） | [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/action.yml:29-31](../../../../external/anthropics/claude-code-security-review/action.yml#L29-L31) |
| `run-web` | No | `'false'` | 是否运行 Web 测试 | [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/action.yml:32-35](../../../../external/anthropics/claude-code-security-review/action.yml#L32-L35) |
| `web-targets` | No | — | 显式 Web 目标，逗号分隔 `<browser>:<viewport>` | [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/action.yml:36-38](../../../../external/anthropics/claude-code-security-review/action.yml#L36-L38) |
| `web-url` | No | — | Web URL 覆盖（如 PR 预览部署） | [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/action.yml:39-41](../../../../external/anthropics/claude-code-security-review/action.yml#L39-L41) |
| `commit-title` | No | — | Commit 标题（自动从事件 payload 检测） | [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/action.yml:42-44](../../../../external/anthropics/claude-code-security-review/action.yml#L42-L44) |
| `tenant-id` | No | — | 租户 ID（多租户场景必需） | [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/action.yml:45-47](../../../../external/anthropics/claude-code-security-review/action.yml#L45-L47) |
| `api-url` | No | `'https://testing-service.app.minitap.ai'` | API 基础 URL 覆盖 | [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/action.yml:48-51](../../../../external/anthropics/claude-code-security-review/action.yml#L48-L51) |
| `cancel-previous-runs` | No | `'true'` | 取消同一源分支上匹配发布分支模式的正在进行的批次 | [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/action.yml:52-55](../../../../external/anthropics/claude-code-security-review/action.yml#L52-L55) |

### 2.2 Outputs

| Output | 说明 | 文件引用 |
|---|---|---|
| `batch-id` | 触发的测试批次 ID | [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/action.yml:58-59](../../../../external/anthropics/claude-code-security-review/action.yml#L58-L59) |
| `status` | 触发批次的初始状态 | [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/action.yml:60-61](../../../../external/anthropics/claude-code-security-review/action.yml#L60-L61) |

### 2.3 运行时配置

```yaml
runs:
  using: 'node20'
  main: 'dist/index.js'
```
*引用：[file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/action.yml:63-65](../../../../external/anthropics/claude-code-security-review/action.yml#L63-L65)*

---

## 3. 主流程分析（src/main.ts）

### 3.1 执行流程概览

入口函数 `run()` 在 [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/main.ts:17-219](../../../../external/anthropics/claude-cookbooks/managed_agents/slack/src/main.ts#L17-L219) 中定义，流程如下：

1. **读取输入**（行 19-58）：解析所有 inputs，处理互斥校验
2. **解析 Commit Title**（行 71）：调用 `getCommitTitle()`
3. **提取 CI 元数据**（行 74）：调用 `getCiMetadata()`
4. **验证运行标志**（行 77-83）：校验平台标志与构建路径组合
5. **验证构建产物**（行 85-106）：iOS/Android 构建验证
6. **获取 OIDC Token**（行 109-111）：通过 `core.getIDToken(apiUrl)` 获取
7. **解析 OIDC Claims**（行 114-129）：提取 `sha` claim
8. **PR SHA 覆盖**（行 131-142）：PR 事件时用真实 head SHA 覆盖 merge commit SHA
9. **上传构建**（行 144-180）：iOS/Android 构建上传
10. **触发测试运行**（行 183-200）：调用 `triggerRun()` API
11. **设置输出**（行 202-211）：输出 batch-id 和 status

### 3.2 输入解析与互斥校验

```typescript
if (userStoryTypes?.length && userStoryIds?.length) {
  throw new Error(
    '`user-story-types` and `user-stories` are mutually exclusive — provide only one.',
  )
}
```
*引用：[file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/main.ts:48-52](../../../../external/anthropics/claude-cookbooks/managed_agents/slack/src/main.ts#L48-L52)*

### 3.3 平台数组构建逻辑

平台数组仅在非默认配置时发送给服务器（默认：iOS+Android+无 Web）：

```typescript
const platforms: Platform[] | undefined =
  runIos && runAndroid && !wantWeb
    ? undefined
    : ([runIos && 'ios', runAndroid && 'android', wantWeb && 'web'].filter(
        Boolean,
      ) as Platform[])
```
*引用：[file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/main.ts:63-68](../../../../external/anthropics/claude-cookbooks/managed_agents/slack/src/main.ts#L63-L68)*

---

## 4. OIDC 认证流程详解

### 4.1 获取 ID Token

```typescript
core.info(`Requesting GitHub OIDC token with audience: ${apiUrl}`)
const token = await core.getIDToken(apiUrl)
core.info('OIDC token obtained successfully')
```
*引用：[file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/main.ts:109-111](../../../../external/anthropics/claude-cookbooks/managed_agents/slack/src/main.ts#L109-L111)*

**关键要点：**
- **Audience**：使用 `apiUrl` 作为 audience（默认 `https://testing-service.app.minitap.ai`）
- **权限要求**：工作流必须配置 `id-token: write` 权限

### 4.2 Claims 解析

```typescript
const payload = token.split('.')[1]
const claims = JSON.parse(Buffer.from(payload, 'base64url').toString())
if (apiUrl !== DEFAULT_API_URL) {
  core.info('OIDC token claims:')
  core.info(JSON.stringify(claims, null, 2))
}
const oidcSha = claims.sha as string | undefined
```
*引用：[file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/main.ts:114-129](../../../../external/anthropics/claude-cookbooks/managed_agents/slack/src/main.ts#L114-L129)*

**安全设计**：仅当使用非默认 API URL（调试自定义部署）时才打印 claims，避免在常规客户工作流日志中泄露仓库、ref、run ID 等元数据。

### 4.3 PR SHA 覆盖逻辑

**问题背景**：对于 `pull_request` / `pull_request_target` 事件，OIDC token 中的 `sha` claim（以及 `GITHUB_SHA`）指向的是 `refs/pull/{n}/merge` 上的临时合并提交，而非 PR 的真实 head commit。这个合并提交不属于 PR 的提交历史，导致 Checks 标签页无法解析锚定到它的 Check Run，点击时显示"No check run found with ID <id> for this pull request"。

**解决方案**：从事件 payload 读取 `pull_request.head.sha`：

```typescript
const eventName = process.env.GITHUB_EVENT_NAME
const prHeadSha = resolvePrHeadSha(eventName)
const commitSha = prHeadSha ?? oidcSha
if (prHeadSha && prHeadSha !== oidcSha) {
  core.info(
    `Using PR head SHA ${prHeadSha} from event payload instead of OIDC merge SHA ${oidcSha}`,
  )
}
```
*引用：[file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/main.ts:135-142](../../../../external/anthropics/claude-cookbooks/managed_agents/slack/src/main.ts#L135-L142)*

### 4.4 resolvePrHeadSha 实现

在 `file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/commit-sha.ts:21-52` 中：

- **非 PR 事件**：返回 `undefined`，使用 OIDC sha
- **PR 事件**：读取 `GITHUB_EVENT_PATH`，解析 `event.pull_request.head.sha`
- **容错设计**：失败时返回 `undefined`（不抛出），回退到 OIDC sha——丢失覆盖比 crash 更好
- **SHA 格式校验**：使用正则 `/^[0-9a-f]{40}$/` 验证 SHA 格式

**服务器端行为**：服务器仅对 `pull_request` / `pull_request_target` 事件接受 `commit_sha` 覆盖，其他事件忽略该字段。

---

## 5. 构建验证机制

### 5.1 validateRunFlags - 运行标志校验

在 [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/validate.ts:15-44](../../../../playground/chaos/src/utils/validate.ts#L15-L44) 中实现：

**校验规则：**
1. 至少启用一个 lane（iOS/Android/Web）
2. 构建路径只能为已启用的平台提供（否则会上传但从不测试）

### 5.2 iOS 构建验证与自动打包

在 [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/validate.ts:137-230](../../../../playground/chaos/src/utils/validate.ts#L137-L230) 中实现：

**支持两种格式：**

1. **`.ipa` 文件**：直接上传，校验文件存在且是文件
2. **`.app` 目录（模拟器 bundle）**：自动打包为 `.ipa`

**.app → .ipa 自动打包流程（行 183-220）：**

```
1. 创建临时目录：os.tmpdir()/minitap-ipa-XXXXXX/
2. 创建 Payload/ 子目录
3. cp -R <AppName>.app Payload/
4. zip -r -q <temp>.ipa Payload/
5. 返回临时 .ipa 路径
6. 上传完成后在 finally 块清理临时文件
```

IPA 结构要求：`Payload/<AppName>.app/`

**临时文件清理**在 [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/main.ts:160-166](../../../../external/anthropics/claude-cookbooks/managed_agents/slack/src/main.ts#L160-L166)：
- 比较 `iosUploadPath !== resolvedIosBuildPath` 判断是否是临时生成的 .ipa
- 使用 `fs.rmSync(iosUploadPath, { force: true })` 清理

### 5.3 Android 构建验证（x86_64 ABI 检查）

在 [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/validate.ts:55-126](../../../../playground/chaos/src/utils/validate.ts#L55-L126) 中实现：

**验证步骤：**
1. 文件存在且以 `.apk` 结尾
2. 是文件而非目录
3. 使用 `unzip -l` 列出 APK 内容
4. 通过正则 `/\blib\/([\w-]+)\//` 扫描架构目录
5. **三种结果：**
   - 无 native 库（纯 Java/Kotlin）：兼容所有架构 ✓
   - 包含 `x86_64`：通过验证 ✓
   - 有 native 库但无 `x86_64`：报错，列出找到的架构

**错误示例：**
```
Android build must target x86-64 emulators.
  Found architectures: arm64-v8a, armeabi-v7a
  Hint: Build your app for x86_64...
```

---

## 6. Web 测试支持（browser:viewport 组合）

### 6.1 web-targets 解析

在 `file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/web-targets.ts:4-44` 中实现。

**有效组合映射表：**

| Token | platform | browser | viewport | 说明 |
|---|---|---|---|---|
| `safari:mobile` | `ios` | `safari` | _(无)_ | iOS Safari（真机） |
| `chrome:mobile` | `android` | `chrome` | _(无)_ | Android Chrome（真机） |
| `chrome:tablet` | `web` | `chrome` | `tablet` | 平板 Chrome |
| `firefox:tablet` | `web` | `firefox` | `tablet` | 平板 Firefox |
| `chrome:desktop` | `web` | `chrome` | `pc` | 桌面 Chrome |
| `firefox:desktop` | `web` | `firefox` | `pc` | 桌面 Firefox |

**关键设计：**
- Mobile web 目标运行在真机上，**无 viewport**（iOS 用 Safari，Android 用 Chrome）
- Browser web 目标运行在浏览器中，viewport 为 `tablet` 或 `pc`
- 无效组合（如 `firefox:mobile`、`safari:desktop`）会被拒绝并给出清晰错误

### 6.2 Web lane 启用逻辑

```typescript
const wantWeb = runWeb || webTargets !== undefined
```
*引用：[file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/main.ts:58](../../../../external/anthropics/claude-cookbooks/managed_agents/slack/src/main.ts#L58-L58)*

- `run-web: true`：使用应用配置的默认 Web 目标
- `web-targets`：显式指定目标列表，自动启用 Web lane（无需同时设置 `run-web`）
- 两者是叠加关系，可以混合运行 native + web

### 6.3 Web URL 处理

```typescript
webUrl: wantWeb ? webUrl.trim() || undefined : undefined,
```
*引用：[file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/main.ts:193](../../../../external/anthropics/claude-cookbooks/managed_agents/slack/src/main.ts#L193-L193)*

- 对于链接到 GitHub 仓库的 Web 应用：Minitest 构建并服务当前 commit，无需 `web-url`
- `web-url` 用于测试独立部署的 URL（如 PR 预览部署）

---

## 7. CI 元数据提取

在 `file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/ci-metadata.ts:41-106` 中实现。

### 7.1 CiMetadata 接口

```typescript
interface CiMetadata {
  prNumber?: number
  prTitle?: string
  baseRef?: string   // PR base 分支（PR 事件）
  headRef?: string   // 源分支
}
```
*引用：`file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/ci-metadata.ts:4-17`*

### 7.2 事件类型处理

| 事件类型 | 提取字段 | 来源 |
|---|---|---|
| `pull_request` / `pull_request_target` | `prNumber`, `prTitle`, `baseRef`, `headRef` | `event.pull_request.{number,title,base.ref,head.ref}` |
| `push`（分支） | `headRef` | `GITHUB_REF` 去掉 `refs/heads/` 前缀 |
| `workflow_dispatch` | `headRef` | 同上 |
| `schedule` | `headRef` | 同上 |
| `merge_group` | `headRef` | 同上 |
| tag 推送/其他 | 无分支元数据 | — |

**BRANCH_REF_EVENTS 集合**在 `file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/ci-metadata.ts:22-27` 定义。

**容错设计**：永不抛出——元数据是尽力而为的可选字段。缺少 `baseRef`/`headRef` 时仅输出警告，分支相关功能（如 cancel-previous-runs）在服务器端跳过。

---

## 8. Commit Title 提取策略

在 `file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/commit-title.ts:17-76` 中实现，采用三级 fallback 策略：

### 优先级顺序（从高到低）

1. **显式输入**：`commit-title` action input（行 19-23）
2. **事件 Payload**：
   - Push 事件：`event.head_commit.message`（行 32-37）
   - PR 事件：`event.pull_request.title`（行 40-47）
3. **Git Log Fallback**：使用 `GITHUB_SHA` 执行 `git log -1 --format='%s' <sha>`（行 54-69）

### firstLine 处理

```typescript
function firstLine(text: string): string {
  return (
    text
      .split(/\r?\n/)
      .map((line) => line.trim())
      .find(Boolean) ?? ''
  )
}
```
*引用：`file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/commit-title.ts:79-86`*

只返回第一行（commit message 的标题部分），去掉换行后的所有内容。

---

## 9. cancel-previous-runs 机制（Release Branch 模式）

### 9.1 输入配置

默认值：`true`（启用）
*引用：[file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/action.yml:52-55](../../../../external/anthropics/claude-code-security-review/action.yml#L52-L55)*

### 9.2 传递给 API

```typescript
cancelPreviousRuns,
```
*引用：[file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/main.ts:199](../../../../external/anthropics/claude-cookbooks/managed_agents/slack/src/main.ts#L199-L199)*

在 [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/api.ts:171-176](../../../../external/multica-ai/multica/packages/core/types/api.ts#L171-L176) 中定义的 `TriggerRunRequest` 接口：

```typescript
/**
 * When true, the server cancels previous in-flight CI batches on the same
 * `headRef` if it matches the app's `release_branch_patterns`. No-op on
 * tag events, on non-release branches, or when `headRef` is missing.
 */
cancelPreviousRuns?: boolean
```

### 9.3 取消作用域（服务器端逻辑）

根据 `file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/README.md:212-228`：

- **同一源分支**：匹配 PR head 分支（PR 事件）或 push/workflow_dispatch/schedule/merge_group 的分支 ref
- **仅发布分支**：分支必须匹配应用配置的 `release_branch_patterns`（gitignore 风格）
- **仅 CI 触发的批次**：Webapp、Slack 或 API 触发的运行不受影响

**No-op 场景：**
- Tag 推送（`refs/tags/*`）
- 不匹配发布分支模式的分支
- 无法确定分支的事件（如 PR 事件 payload 缺失）

---

## 10. API 客户端与字段命名约定

### 10.1 两个 API 端点

在 [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/api.ts](../../../../external/multica-ai/multica/packages/core/types/api.ts) 中实现：

**1. Build Upload**：`POST /api/v1/ci/builds/upload`（multipart form）

**2. Trigger Run**：`POST /api/v1/ci/run`（JSON）

### 10.2 Form snake_case vs JSON camelCase 约定

**关键区分：**

| 场景 | 命名风格 | 示例 |
|---|---|---|
| Multipart 表单字段（构建上传） | **snake_case** | `app_slug`, `commit_title`, `commit_sha`, `tenant_id` |
| JSON 请求体（触发运行） | **camelCase** | `appSlug`, `commitTitle`, `commitSha`, `userStoryTypes`, `iosBuildId`, `tenantId` |

**表单字段实现**（[file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/api.ts:228-259](../../../../external/multica-ai/multica/packages/core/types/api.ts#L228-L259)）：
```typescript
parts.push(Buffer.from(`--${boundary}\r\nContent-Disposition: form-data; name="app_slug"\r\n\r\n${appSlug}\r\n`, 'utf-8'))
parts.push(Buffer.from(`--${boundary}\r\nContent-Disposition: form-data; name="commit_title"\r\n\r\n${commitTitle}\r\n`, 'utf-8'))
parts.push(Buffer.from(`--${boundary}\r\nContent-Disposition: form-data; name="commit_sha"\r\n\r\n${commitSha}\r\n`, 'utf-8'))
if (tenantId) {
  parts.push(Buffer.from(`--${boundary}\r\nContent-Disposition: form-data; name="tenant_id"\r\n\r\n${tenantId}\r\n`, 'utf-8'))
}
```

**原因**：根据 [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/AGENTS.md:58](../../../../external/multica-ai/multica/AGENTS.md#L58-L58)，服务器端（testing-service）使用 Pydantic alias generation，表单参数用 snake_case 是因为它们是 multipart form params 而非 JSON。

### 10.3 认证头

所有 API 请求使用 Bearer token：
```typescript
Authorization: `Bearer ${token}`
```
*引用：[file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/api.ts:280](../../../../external/multica-ai/multica/packages/core/types/api.ts#L280-L280) 和 [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/api.ts:328](../../../../external/multica-ai/multica/packages/core/types/api.ts#L328-L328)*

### 10.4 错误处理

三种错误信封格式：
1. **标准错误**：`{ error, message, details?: { errors?: [...] } }`
2. **Build Invalid**：`{ error_code: "build_invalid", issues: [...] }`——每个 issue 作为 GitHub Annotation 输出
3. **未知格式**：保留原始 JSON 不丢失真实错误

*引用：[file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/src/api.ts:49-88](../../../../external/multica-ai/multica/packages/core/types/api.ts#L49-L88)*

---

## 11. 发布流程详解

### 11.1 发布工作流

在 [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/.github/workflows/release.yml](../../../../external/multica-ai/multica/.github/workflows/release.yml) 中定义：

**触发条件**：GitHub Release published 事件

**步骤：**

1. **Checkout**：`actions/checkout@v6`，ref 设置为 release tag（行 15-17）
2. **Setup Node.js**：`actions/setup-node@v6`，Node 20，启用 npm cache（行 19-23）
3. **Install dependencies**：`npm ci`（行 25-26）
4. **Build and bundle**：`npm run all`（行 28-29）
   - 执行 `tsc` 编译
   - ESLint 检查
   - Prettier 格式检查
   - **ncc 打包**到 `dist/`
5. **Commit dist/**：强制添加 `dist/` 目录并提交（行 31-36）
   ```bash
   git config user.name "github-actions[bot]"
   git config user.email "github-actions[bot]@users.noreply.github.com"
   git add -f dist/
   git commit -m "chore: build dist for ${{ github.event.release.tag_name }}"
   ```
6. **Update major version tag**：提取主版本号并强制更新 v1 标签（行 38-44）
   ```bash
   MAJOR=$(echo "$TAG" | grep -oE '^v[0-9]+')
   git tag -fa "$MAJOR" -m "Update $MAJOR tag to $TAG"
   git push origin "$MAJOR" --force
   ```

### 11.2 npm scripts

在 [file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/package.json:6-13](../../../../external/multica-ai/multica/package.json#L6-L13)：

| Script | 命令 | 说明 |
|---|---|---|
| `build` | `tsc` | TypeScript 编译 |
| `bundle` | `ncc build src/main.ts --source-map --license licenses.txt` | ncc 打包为单文件 |
| `lint` | `eslint src/` | ESLint 检查 |
| `format` | `prettier --write 'src/**/*.ts'` | Prettier 格式化（写入） |
| `format:check` | `prettier --check 'src/**/*.ts'` | Prettier 格式检查 |
| `all` | `build && lint && format:check && bundle` | 全量检查+打包 |

### 11.3 版本分发机制

1. 用户创建 semver tag 的 GitHub Release（如 `v1.0.0`）
2. Release workflow 自动构建 `dist/` 并提交到该 tag
3. 更新 `v1` 主版本标签指向新 release
4. 用户引用 `@v1` 自动获得最新版本

**dist/ 目录策略**：在 `.gitignore` 中忽略（永不手动提交），仅由 release workflow 在发布时构建提交。

---

## 12. 技术栈与依赖

### 12.1 Runtime Dependencies

| 包 | 版本 | 用途 |
|---|---|---|
| `@actions/core` | ^1.11.1 | GitHub Actions runtime（inputs, outputs, OIDC, logging） |
| `@actions/http-client` | ^2.2.3 | HTTP 请求 |

*引用：[file:///d:/AI/.chaos/libs/minitap-ai/minitest-trigger/package.json:24-27](../../../../external/multica-ai/multica/package.json#L24-L27)*

### 12.2 Dev Dependencies

| 包 | 用途 |
|---|---|
| `typescript` | TypeScript 编译器（strict 模式，ES2022，CommonJS） |
| `@vercel/ncc` | 打包为单文件 `dist/index.js` |
| `eslint` + `typescript-eslint` | 代码检查（flat config） |
| `prettier` | 代码格式化（无分号，单引号） |
| `@types/node` | Node.js 类型定义 |

---

## 13. 关键设计决策总结

| 决策 | 设计 | 原因 |
|---|---|---|
| OIDC audience | 使用 `apiUrl` | 支持自定义部署，token 绑定到特定 API |
| Claims 日志 | 仅非默认 API 时打印 | 避免泄露客户仓库元数据 |
| PR SHA 覆盖 | 用 head.sha 替代 merge commit sha | Check Runs 在 PR Checks 标签页可解析 |
| iOS .app → .ipa | 自动临时打包 | 用户体验友好，无需手动打包 |
| Android ABI 检查 | unzip -l 扫描 lib/ 目录 | 早期失败，避免模拟器运行时才发现架构不兼容 |
| Web 目标映射 | mobile 无 viewport，desktop/tablet 有 viewport | mobile 跑真机，桌面跑浏览器 |
| cancel-previous-runs | 仅发布分支生效 | 避免功能分支重复推送取消测试，发布分支需要避免队列堆积 |
| 字段命名 | Form snake_case / JSON camelCase | multipart 表单传统与 JSON 惯例的平衡 |
| dist/ | gitignored，release workflow 构建 | 源码树干净，发布时自动打包 |
| 错误处理 | best-effort fallback | 非关键路径失败不 crash，如 commit title/git log 失败才报错 |
