# Discourse论坛自动化方案调研报告

## 一、Discourse REST API核心端点

Discourse API采用"页面URL+.json"的模式设计，没有独立的`/api/v1/`命名空间。所有POST/PUT请求支持`application/json`、`multipart/form-data`或`application/x-www-form-urlencoded`三种Content-Type。

### 1.1 创建帖子/主题

| 项目 | 详情 |
|------|------|
| HTTP方法 | `POST` |
| 路径 | `/posts.json` |
| 认证方式 | 需要认证（Api-Key + Api-Username 或 User-Api-Key） |
| 返回格式 | JSON |

**必要参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `title` | string | 创建新主题/私信时必填 | 主题标题 |
| `raw` | string | 是 | 帖子内容（Markdown格式） |
| `topic_id` | integer | 回复帖子时必填 | 要回复的主题ID |
| `category` | integer | 创建新主题时可选 | 分类ID |
| `reply_to_post_number` | integer | 可选 | 回复指定楼层的帖子编号 |
| `target_recipients` | string | 私信时必填 | 收件人用户名，逗号分隔 |
| `archetype` | string | 私信时必填 | 值为"private_message" |
| `tags` | string[] | 可选 | 标签数组 |

**示例请求：**
```bash
curl -X POST "https://forum.example.com/posts.json" \
  -H "Content-Type: application/json" \
  -H "Api-Key: YOUR_API_KEY" \
  -H "Api-Username: YOUR_USERNAME" \
  -d '{"title": "主题标题", "raw": "帖子内容", "category": 1}'
```

### 1.2 编辑帖子

| 项目 | 详情 |
|------|------|
| HTTP方法 | `PUT` |
| 路径 | `/posts/{id}.json` 或 `/posts/{id}` |
| 认证方式 | 需要认证 |
| 返回格式 | JSON |

**必要参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `post[raw]` | string | 是 | 新的帖子内容（替换整个帖子） |
| `post[edit_reason]` | string | 可选 | 编辑原因 |

**示例请求（参考官方Ruby gem实现）：**
```bash
curl -X PUT "https://forum.example.com/posts/123.json" \
  -H "Content-Type: application/json" \
  -H "Api-Key: YOUR_API_KEY" \
  -H "Api-Username: YOUR_USERNAME" \
  -d '{"post": {"raw": "更新后的帖子内容"}}'
```

### 1.3 回复帖子

回复帖子实际上也是调用`POST /posts.json`，只是参数不同：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `raw` | string | 是 | 回复内容 |
| `topic_id` | integer | 是 | 主题ID |
| `reply_to_post_number` | integer | 可选 | 要回复的具体楼层号，不填则回复主题 |

**示例请求：**
```bash
curl -X POST "https://forum.example.com/posts.json" \
  -H "Content-Type: application/json" \
  -H "Api-Key: YOUR_API_KEY" \
  -H "Api-Username: YOUR_USERNAME" \
  -d '{"raw": "这是回复内容", "topic_id": 456, "reply_to_post_number": 3}'
```

### 1.4 读取帖子/主题

| 项目 | 详情 |
|------|------|
| HTTP方法 | `GET` |
| 路径 | `/t/{id}.json`（读取整个主题）或 `/posts/{id}.json`（读取单个帖子） |
| 认证方式 | 公开内容无需认证，私有内容需要认证 |
| 返回格式 | JSON |

**查询参数（主题）：**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `posts` | integer | 返回的帖子数量 |
| `include_raw` | boolean | 是否包含原始Markdown内容 |

**示例请求：**
```bash
curl "https://forum.example.com/t/123.json"
curl "https://forum.example.com/posts/456.json"
```

### 1.5 上传图片/附件

| 项目 | 详情 |
|------|------|
| HTTP方法 | `POST` |
| 路径 | `/uploads.json` |
| 认证方式 | 需要认证 |
| Content-Type | `multipart/form-data` |
| 返回格式 | JSON |

**必要参数：**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `type` | string | 是 | 上传类型：`composer`（帖子编辑器）、`avatar`（头像）、`profile_background`、`card_background` |
| `synchronous` | boolean | 推荐设为true | 同步上传，立即返回结果 |
| `files[]` | file | 是 | 文件字段（注意是`files[]`不是`file`） |

**响应包含：**
- `id`: 上传ID
- `url`: 完整URL
- `short_url`: 短URL格式（`upload://abcDEF123.png`），用于在帖子中引用

**在帖子中引用上传文件的Markdown格式：**
- 图片：`![alt text](upload://abcDEF123.png)`
- 附件：`[filename.pdf|attachment](upload://abcDEF123.pdf)`

**示例请求：**
```bash
curl -X POST "https://forum.example.com/uploads.json" \
  -H "Api-Key: YOUR_API_KEY" \
  -H "Api-Username: YOUR_USERNAME" \
  -F "type=composer" \
  -F "synchronous=true" \
  -F "files[]=@/path/to/image.png"
```

---

## 二、Discourse API认证方式

Discourse有两套独立的API认证体系，分别适用于不同场景。

### 2.1 两种API Key对比

| 属性 | 全局API Key (Admin API Key) | 用户API Key (User API Key) |
|------|----------------------------|----------------------------|
| 创建者 | 管理员在后台创建 | 普通用户通过OAuth授权流程创建 |
| 创建位置 | Admin → API → New API Key | `/user-api-key/new` 授权页面 |
| HTTP Header | `Api-Key` + `Api-Username` | `User-Api-Key` + `User-Api-Client-Id`（可选） |
| 身份模拟 | 可以指定任意用户（包括system用户） | 只能代表授权用户本人 |
| 权限范围 | 全局权限或细粒度权限（按操作分类） | 预定义scope：`read`、`write`、`message_bus`、`push`、`notifications`、`session_info`、`one_time_password` |
| 访问Admin接口 | 可以（如果对应用户是管理员） | 不可以，即使用户是管理员 |
| 撤销方式 | 管理员在API页面撤销 | 用户在个人资料页面的"应用"标签页撤销 |
| 适用场景 | 后端自动化、ETL、机器人、批量操作 | 移动App、浏览器扩展、端用户小工具 |

### 2.2 HTTP Header格式

**使用Admin API Key：**
```
Api-Key: your-api-key-here
Api-Username: username-to-impersonate
```

**使用User API Key：**
```
User-Api-Key: user-api-key-here
User-Api-Client-Id: your-client-id
```

⚠️ **重要陷阱**：使用`Api-Key`时必须同时提供`Api-Username`，否则会静默返回403错误，没有明确提示缺少用户名。

### 2.3 User API Key生成流程

User API Key采用类似OAuth的授权流程，需要用户在浏览器中显式授权：

1. **客户端生成密钥对**：应用（桌面App、浏览器插件、移动App）生成RSA公钥/私钥对
2. **构造授权URL**：重定向用户到：
   ```
   https://forum.example.com/user-api-key/new
   ```
   参数包括：
   - `auth_redirect`: 授权后回调URL
   - `application_name`: 应用名称（显示在授权页面）
   - `client_id`: 客户端唯一标识
   - `scopes`: 逗号分隔的权限范围列表
   - `public_key`: 客户端公钥
   - `push_url`: 推送通知URL（如果需要push/notifications scope）

3. **用户登录并授权**：如果用户未登录会先跳转到登录页，登录后显示授权确认页面，明确列出请求的权限
4. **生成Key并回调**：用户点击"授权"后，Discourse生成User API Key，用客户端公钥加密后重定向回`auth_redirect`
5. **客户端解密**：客户端用私钥解密payload获得API Key

**用户设置页面入口**：授权后，用户的个人页面会出现"**应用**"(Apps)标签页，列出所有已授权的应用，包括：
- 应用名称
- 最后使用日期
- 授权日期
- 授予的权限范围列表
- **撤销访问**按钮

### 2.4 速率限制（默认值，Discourse 3.4）

| 限制类型 | 默认值 |
|----------|--------|
| 匿名请求 | 60 req / 60s / IP |
| 已认证请求 | 200 req / 60s / 用户 |
| 创建操作 | 5-20次/分钟/用户（按信任级别缩放） |
| User API Key | 20 req / 分钟，2880 req / 天 |

⚠️ 遇到429错误时，响应包含`Retry-After: N`头，表示需要等待N秒后重试。

---

## 三、forum.trae.cn User API Key可行性分析

### 3.1 forum.trae.cn基本信息

通过访问`https://forum.trae.cn/about.json`获取到：
- 站点名称：TRAE官方中文社区
- 版本：2026.3.0-latest
- 创建时间：2026-01-27
- 用户数：100,099+
- 帖子数：140,461+
- 语言：zh_CN

### 3.2 普通用户能否生成User API Key？

**结论：理论上支持，但需要通过OAuth流程，用户设置页面没有直接入口。**

分析依据：

1. **User API Key是Discourse核心功能**：从Discourse 2.x版本开始内置，除非管理员通过站点设置显式禁用（`min_trust_level_for_user_api_key`设置为过高值或完全禁用），否则普通用户都可以通过`/user-api-key/new`端点生成。

2. **用户设置页面没有"API密钥"入口**：与Admin API Key不同，User API Key**不是**在用户设置页面（`/my/preferences/security`）手动生成的。用户设置页面只有在已经授权过应用后才会显示"应用"标签页来管理已授权的Key，没有主动创建Key的UI入口。

3. **正确生成方式**：普通用户必须通过应用发起的OAuth授权流程来生成User API Key，即：
   - 使用`@discourse/mcp`提供的`generate-user-api-key`命令，它会自动处理密钥对生成、浏览器授权流程
   - 或自己实现OAuth流程访问`/user-api-key/new`

4. **使用@discourse/mcp的便捷方式**：
   ```bash
   npx @discourse/mcp@latest generate-user-api-key \
     --site https://forum.trae.cn \
     --save-to ./trae-forum-profile.json
   ```
   这个命令会自动打开浏览器，用户登录后点击授权，Key会自动保存到配置文件中。

5. **权限边界**：生成的User API Key拥有与该用户账号完全相同的权限，不能超出用户本身的权限范围（比如普通用户无法用这个Key访问管理员功能）。

---

## 四、@discourse/mcp npm包详解

`@discourse/mcp`是Discourse官方发布的Model Context Protocol服务器，将Discourse REST API封装为AI Agent可直接调用的工具。

### 4.1 基本信息

| 项目 | 详情 |
|------|------|
| npm包名 | `@discourse/mcp` |
| 仓库 | https://github.com/discourse/discourse-mcp |
| 运行时 | Node.js >= 24（推荐24 LTS） |
| 最新版本 | 0.2.4 |
| 传输方式 | stdio（默认）或HTTP |
| 开源协议 | MIT |

### 4.2 安装与运行

**只读模式（无需认证，推荐初始试用）：**
```bash
npx -y @discourse/mcp@latest
```

**启用写入功能（需要API Key）：**
```bash
npx -y @discourse/mcp@latest \
  --allow_writes \
  --read_only=false \
  --auth_pairs '[{"site":"https://forum.trae.cn","user_api_key":"YOUR_KEY","user_api_client_id":"discourse-mcp"}]'
```

**Claude Desktop配置示例：**
```json
{
  "mcpServers": {
    "discourse": {
      "command": "npx",
      "args": ["-y", "@discourse/mcp@latest"]
    }
  }
}
```

### 4.3 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--site <url>` | 无 | 绑定到单个站点，隐藏site选择工具 |
| `--read_only` | `true` | 只读模式，禁用所有写入工具 |
| `--allow_writes` | `false` | 允许写入操作（需同时关闭read_only） |
| `--auth_pairs` | 无 | JSON数组，配置站点认证信息 |
| `--profile <path.json>` | 无 | 从配置文件加载所有参数（避免密钥暴露在命令行） |
| `--timeout_ms` | 15000 | 请求超时（毫秒） |
| `--concurrency` | 4 | 并发请求数 |
| `--log_level` | `info` | 日志级别：silent/error/info/debug |
| `--max-read-length` | 50000 | 帖子内容最大返回字符数 |
| `--allowed_upload_paths` | 无 | 允许上传的本地目录列表（逗号分隔） |
| `--transport` | `stdio` | 传输方式：stdio或http |
| `--port` | 3000 | HTTP模式端口 |

**auth_pairs支持的认证方式：**
- Admin API Key：`{"site":"...","api_key":"...","api_username":"..."}`
- User API Key：`{"site":"...","user_api_key":"...","user_api_client_id":"..."}`
- HTTP Basic Auth：额外添加`http_basic_user`和`http_basic_pass`

### 4.4 MCP Resources（资源，只读列表）

Resources通过URI寻址，提供静态/半静态数据：

| Resource URI | 说明 |
|--------------|------|
| `discourse://site/categories` | 列出所有分类（含层级结构、权限） |
| `discourse://site/tags` | 列出所有标签（含使用次数） |
| `discourse://site/groups` | 列出所有用户组（含可见性设置） |
| `discourse://chat/channels` | 列出所有公开聊天频道 |
| `discourse://user/chat-channels` | 列出用户的聊天频道（含私信、未读数） |
| `discourse://user/drafts` | 列出用户的草稿 |

### 4.5 MCP Tools（工具列表）

#### 只读工具（始终可用）

| 工具名 | 功能说明 |
|--------|----------|
| `discourse_select_site` | 选择要操作的Discourse站点（验证`/about.json`） |
| `discourse_search` | 全站搜索，返回匹配主题列表 |
| `discourse_read_topic` | 读取主题详情，包含帖子内容（支持分页） |
| `discourse_read_post` | 读取单个帖子的完整内容 |
| `discourse_get_user` | 获取用户基本信息（信任级别、注册时间、简介等） |
| `discourse_list_user_posts` | 列出用户的所有帖子/回复 |
| `discourse_filter_topics` | 高级主题过滤（支持分类、标签、状态、日期、点赞数、排序等复杂查询） |
| `discourse_get_chat_messages` | 获取聊天频道消息 |
| `discourse_get_draft` | 获取指定草稿 |
| `discourse_list_users` | 列出用户（需要Admin API Key，支持筛选、排序、分页） |

#### 写入工具（需同时满足：`--allow_writes` + `--read_only=false` + 配置了auth）

| 工具名 | 功能说明 |
|--------|----------|
| `discourse_create_topic` | 创建新主题（支持标题、内容、分类、标签） |
| `discourse_create_post` | 在现有主题下回复帖子 |
| `discourse_update_topic` | 更新主题（标题、分类、标签、特色链接） |
| `discourse_save_draft` | 保存草稿（支持创建主题、回复、编辑等类型） |
| `discourse_delete_draft` | 删除草稿 |
| `discourse_upload_file` | 上传文件/图片（支持base64、URL、本地文件） |
| `discourse_create_user` | 创建用户（需要Admin权限） |
| `discourse_update_user` | 更新用户信息（个人资料、头像、简介等） |

### 4.6 与直接REST API调用的区别和优势

| 维度 | 直接REST API | @discourse/mcp |
|------|-------------|----------------|
| 协议适配 | 需要手动处理HTTP请求、认证、错误处理 | 实现MCP标准协议，AI Agent可直接调用 |
| 工具抽象 | 需要自己理解每个端点的参数和返回格式 | 封装为语义化工具，输入输出都是结构化JSON |
| 认证管理 | 需要自己管理Key的存储和刷新 | 支持profile文件管理，自动处理Header注入 |
| 写入安全 | 没有防护，可能误操作 | 默认只读，写入需显式开启，~1 req/sec速率限制 |
| 错误重试 | 需要自己实现429重试、退避逻辑 | 自动重试429/5xx错误（3次，带退避） |
| 结果简化 | 返回原始完整JSON，可能包含大量冗余字段 | 返回精简的结构化数据，适合LLM处理 |
| 高级查询 | 需要自己构造复杂的查询参数 | `discourse_filter_topics`提供强大的查询语言 |
| 多站点支持 | 需要自己切换base_url | 支持多站点配置，运行时选择或启动时绑定 |
| 本地文件上传 | 需要自己读取文件、构造multipart请求 | 配置`--allowed_upload_paths`后可直接上传本地文件 |
| 缓存 | 需要自己实现 | 内置轻量级GET请求内存缓存 |

---

## 五、三方案对比结论

### 5.1 方案概述

| 方案 | 当前方案（integrated_browser MCP + agent-browser CLI） | REST API直接调用 | @discourse/mcp |
|------|-------------------------------------------------------|------------------|----------------|
| 核心原理 | 通过浏览器自动化模拟用户操作 | 直接调用Discourse后端HTTP API | 官方MCP服务器封装REST API |
| 认证要求 | 需要用户登录（Cookie/Session） | 需要Admin API Key或User API Key | 需要User API Key（普通用户可获取） |

### 5.2 详细对比表

| 对比维度 | integrated_browser + agent-browser | REST API直接调用 | @discourse/mcp |
|----------|------------------------------------|------------------|----------------|
| **适用场景** | - 没有API访问权限时<br>- 需要模拟复杂UI交互<br>- 快速原型、一次性任务<br>- 调试、探索页面功能 | - 高性能后端服务<br>- 批量数据处理、ETL<br>- 已有Admin权限的机器人<br>- 需要精细控制每个请求 | - AI Agent集成<br>- 普通用户自动化<br>- 快速开发MCP客户端工具<br>- 多站点管理 |
| **前提条件** | - 浏览器环境可用<br>- 用户能正常登录forum.trae.cn<br>- 页面结构没有大变化 | - 需要API Key（Admin或User）<br>- 理解API端点和参数<br>- HTTP客户端开发能力 | - Node.js >= 24环境<br>- 能通过浏览器完成一次OAuth授权<br>- MCP客户端（Claude Desktop、Trae等） |
| **开发成本** | - 中等：需要写选择器、处理页面等待<br>- 维护成本高：UI变化易失效 | - 低中等：REST调用标准化<br>- 但需要自己处理认证、重试、错误 | - 极低：工具已封装好<br>- 直接调用语义化工具，零HTTP代码 |
| **性能** | - 低：启动浏览器慢、页面渲染开销大<br>- 单步操作延迟高（秒级） | - 极高：直接HTTP请求，毫秒级<br>- 可并发、可批量 | - 高：HTTP请求+轻量封装<br>- 内置缓存和重试 |
| **稳定性** | - 低：强依赖页面DOM结构<br>- 前端更新容易导致脚本失效 | - 极高：API是稳定契约<br>- 遵循Discourse版本兼容性 | - 高：官方维护，跟随API更新<br>- 但作为新项目，可能有小bug |
| **权限要求** | - 只要用户能在浏览器做的，都能做<br>- 不需要额外申请Key | - Admin Key：需要管理员配合创建<br>- User Key：普通用户可自助获取 | - User Key：普通用户可自助获取<br>- 权限与用户账号完全一致 |
| **功能完整性** | - 理论上100%覆盖（用户能看到的都能操作）<br>- 包括复杂的UI交互流程 | - 几乎覆盖所有功能<br>- 但部分边缘操作可能需要逆向工程 | - 覆盖核心功能：读帖、发帖、回复、搜索、上传、用户信息<br>- 目前不支持帖子编辑（但支持主题编辑）、点赞等操作 |
| **反爬/风控风险** | - 中高：浏览器自动化特征可能被检测<br>- 操作频率受前端限制 | - 低：合法API调用，遵循速率限制即可 | - 低：合法User API Key调用<br>- 内置速率限制保护 |
| **文本输出质量** | - 需要自己从HTML提取内容<br>- 可能有广告、导航等噪音 | - 原生JSON，raw字段是干净的Markdown | - 原生JSON，返回raw Markdown<br>- 自动截断过长内容 |
| **文件上传** | - 复杂：需要处理文件选择对话框<br>- 模拟输入、等待上传完成 | - 需要自己构造multipart/form-data<br>- 处理files[]字段正确格式 | - 简单：提供base64/URL/本地路径即可<br>- 自动处理multipart构造 |
| **LLM集成度** | - 低：浏览器是通用工具<br>- 需要自己设计提示词和工具调用 | - 低：需要自己封装为函数/工具<br>- 自己设计参数Schema | - 极高：原生MCP协议<br>- AI客户端自动发现和调用工具 |
| **维护成本** | - 高：页面改版就要改选择器<br>- 依赖浏览器版本 | - 低：API向下兼容性好<br>- Discourse版本升级通常不破坏API | - 低：官方维护更新<br>- 通过npx自动使用最新版本 |
| **部署复杂度** | - 需要浏览器/Playwright环境<br>- 依赖较多较重 | - 轻量：任何HTTP客户端即可<br>- 无特殊依赖 | - 轻量：Node.js环境即可<br>- npx一键运行，无需安装 |

### 5.3 方案选择建议

#### 🏆 **优先推荐：@discourse/mcp方案**
**适用条件**：
- 你的目标是让AI Agent（Trae、Claude等）与论坛交互
- 你是普通用户，没有管理员权限
- 需要核心功能：发帖、回复、搜索、读取、上传图片
- 希望快速开发，不想处理HTTP细节

**优点**：普通用户可自助获取User API Key、官方维护、MCP标准协议、默认安全只读、写入有速率限制保护。

**操作步骤**：
1. 运行`npx @discourse/mcp@latest generate-user-api-key --site https://forum.trae.cn --save-to ./trae-profile.json`
2. 浏览器打开后登录forum.trae.cn并点击授权
3. 编辑profile.json添加`"read_only": false, "allow_writes": true`开启写入
4. 在MCP客户端配置中使用`--profile ./trae-profile.json`启动

---

#### 🥈 **备选方案：直接REST API调用**
**适用条件**：
- 你有Admin API Key（管理员权限）
- 需要构建高性能后端服务/批处理脚本
- 需要@discourse/mcp目前不支持的功能（如编辑帖子、点赞、管理分类等）
- 你熟悉HTTP开发，愿意自己处理认证和重试

**优点**：最灵活、性能最高、可访问所有API端点。

**缺点**：需要管理员配合提供Key（如果用Admin Key），自己处理所有底层细节。

---

#### 🥉 **当前方案（浏览器自动化）**
**适用条件**：
- 完全无法获取API Key（比如站点禁用了User API Key）
- 需要操作API无法覆盖的特殊UI功能
- 一次性临时任务，不值得配置API
- 探索和调试阶段

**优点**：不需要任何API权限，只要能登录浏览器就能用。

**缺点**：慢、脆弱、维护成本高，不适合长期稳定运行的自动化。

### 5.4 关于forum.trae.cn的具体建议

基于调研结果，对于forum.trae.cn：

1. **首选@discourse/mcp + User API Key**：
   - forum.trae.cn版本是2026.3.0-latest，支持User API Key功能
   - 普通用户可以通过`generate-user-api-key`命令自助授权，不需要联系管理员
   - 获得的Key拥有与你账号相同的权限，可以满足大多数自动化需求

2. **如果遇到功能缺口**：
   - 比如@discourse/mcp目前不支持编辑帖子，可以结合少量REST API调用补充
   - 或者给discourse-mcp项目提Issue/PR添加缺失工具

3. **浏览器自动化作为兜底**：
   - 如果某些极端操作API确实无法完成，再用agent-browser补充
   - 不建议作为主方案长期使用
