# I 阶段洞察：podman-py R3（vendor 全量源码）

> 输入：facts.md（A-P 组事实）。每个洞察四元组：陈述 / 证据(F 锚点) / 反常识 / 行动（落到新文档）。

## 洞察 #1：统一 Manager 骨架下，资源契约是"历史端点映射"而非重新设计——跨资源没有可类推的一致性

- **陈述**：9 个 Manager 共享同一套 prepare_model/CRUD 骨架，但身份键、端点后缀、错误键名、prune 语义四处系统性分叉。
- **证据**：id 键三种取法（Container `Id` / Pod `ID` 优先 / Network 缺 Id 时 sha256(name) 推导 / Volume.id==name / Secret 名在 `Spec.Name`）F-F2/G1/H1/I1/J1；端点后缀：Network get `/networks/{key}` 无 json、Secret exists 借 `/json`、其他资源多为 `/json`+`/exists` F-H11/J3/H12；prune 错误键 pods/volumes 用 `Err`、networks 用 `Error` F-G7/I4/H10；SpaceReclaimed 三态（pods/networks 恒 0、volumes 累加 Size、images 累加 Size）F-G7/H10/I4；Manifest.list 直接 NotImplementedError F-K9。
- **反常识**：docker-py 用户最容易"看着一个资源的写法类推另一个"，但这些差异不是疏忽，而是对 libpod 各历史端点的忠实映射（各端点由不同时期/不同作者加入）。
- **行动**：06/07 概念文档以"差异矩阵"为主结构而非重复通用 CRUD；每个资源给"端点/身份/特殊语义"三列，明确标注"禁止类推"。

## 洞察 #2：流（streaming）在 SDK 内有三套互不兼容的线协议，"stream=True"在不同方法里含义不同

- **陈述**：消费流式响应前必须先判定协议：NDJSON 行流（events/pull 进度/build 日志）、Docker 多路复用 8 字节帧（logs/exec attach）、HTTP Upgrade 裸 socket（exec_run socket=True）。
- **证据**：events.iter_lines + json.loads F-N2；pull `_stream_helper` 按 `raw._fp.chunked` 逐块 JSON F-L15；frames/stream_frames 用 `struct ">BxxxL"` 解帧 + demux_output 分 stdout/stderr F-D7/D8/D10/N8/N9；exec socket 走 101 Upgrade 且 SSH scheme 显式拒绝 F-N7。
- **反常识**：`stream=True` 是多义词——logs 的 stream 返回帧生成器（且不暴露 demux），exec_run 的 stream 返回帧但支持 demux，stats 默认 stream=True（容器）而 pods.stats 默认 False，pull 的 stream 返回 JSON 进度，build 的 stream 是参数层的固定行为。另外 Container.attach/attach_socket 两个方法是无条件 NotImplementedError F-N5。
- **行动**：08 概念以"三协议 × 消费方法"矩阵组织；给每种协议一个最小可读消费片段；显式列出默认值差异表与 attach 不可用事实。

## 洞察 #3：push() 的进度消息是客户端合成的；多个"看起来在调服务端"的方法其实是本地行为

- **陈述**：ImagesManager.push 不迭代服务端响应体，返回的两条 Pushing 状态由客户端代码构造；prune_builds 完全不发请求；images.load 的返回是生成器函数（含 yield，调用即得生成器）。
- **证据**：F-L10（body 两条本地 dict，非 stream 时 json.dumps 拼成字符串）；F-L9（prune_builds 本地返空）；F-L7（load 内 `_generator`）。
- **反常识**：文档/类型签名暗示推送进度来自 registry；实际 push(stream=True) 永远只产出固定两条合成消息。要真实推送进度/错误，不能依赖该方法的返回内容，只能靠 raise_for_status 成败。
- **行动**：07 概念（镜像分发面：manifest/registry/load/push 语义）明确标注"合成进度"陷阱；示例 04 对推送结果只断言不抛异常。

## 洞察 #4：构建上下文在客户端完成全部标准化，服务端只接收一个去身份化的 x-tar 包

- **陈述**：path/fileobj/custom_context 三种入口最终都归约为 tar 字节流；ignore 解析、Containerfile 代理拷贝、tar 成员过滤/uid 归零/Windows 位修正全在客户端。
- **证据**：BuildMixin 三分支 F-M2；prepare_containerignore 双文件优先级 F-D14；prepare_containerfile samefile 判定+随机代理名 copy2(follow_symlinks=False) F-D15；create_tar filter（uid=0/root、mtime 钳制、仅 file/dir/symlink、win32 mode）F-D16；_render_params 的参数映射与"不支持 kwargs 静默忽略" F-M6；响应侧 tee 分叉+正则取 image_id F-M5。
- **反常识**：① dockerignore 高级语法（`!`、`**`）在源码里明确 FIXME 不支持，只有 fnmatch；② gzip 与 encoding 不能同给；③ build 返回的 Image 是用正则从流文本里抠出 16 进制 id 再 get 回来的，错误信息藏在逐行 JSON 的 error 键里。
- **行动**：09 概念画"从目录到 /build 请求"的管线图，列三入口归约表、tar 脱敏规则、BuildError 诊断三部曲；明确 ignore 语法限制。

## 洞察 #5：连接与配置层充满"兼容优先于实现"的折中——TLS 空壳、双前缀、双配置格式、合成 scheme

- **陈述**：TLSConfig 是被忽略的兼容类；URL scheme 在 normalize 阶段被改写（unix/ssh/tcp → http+*/http）；containers.conf 新旧两格式同名连接 JSON 赢；verify 参数同时切换 URL scheme 与 requests 的 TLS 校验；非 libpod 端点只有 /auth 等极少数。
- **证据**：F-D13（TLSConfig ignored）；F-B7（scheme 改写、netloc quote_plus）；F-E6/E7（JSON 覆盖 TOML、Default/active_service）；F-B8（verify→https）；F-O3（login compatible=True）；B5 双前缀。
- **反常识**：传 `tcp://` 最终请求的 URL scheme 是 `http`；UDS 连接同时 mount http:// 与 https://；ping 不抛异常只返 bool；HTTP 层 timeout 与 stop 的 grace timeout 是两个量纲（后者再 ×1.5）。
- **行动**：10 概念做"URL 一生"轨迹图（用户输入 → normalize → mount → 前缀 → 实际请求行），配安全注意（TLS 不生效的边界、UDS trust_env=False、fallback runtime dir 0700 防 symlink）。

## G2 自检

5 个洞察均含 陈述/证据(F 锚点)/反常识/行动 四元组；全部可由 facts.md 复核，无新增未采事实。

## 知识地图（R3 增量）

学习路径续接既有 00-05（入门/连接/管理器/容器/镜像/高级资源+治理）：

| 新文档 | 编号 | 覆盖 F 组 | 前置 |
|---|---|---|---|
| Pod/Network/Volume 组编排原语 | concepts/06 | F-G/H/I + F-F | 02 |
| Secret/Manifest/Registry 分发面 | concepts/07 | F-J/K/L | 04 |
| 事件与三套流协议 | concepts/08 | F-N + F-D7~D10 | 03 |
| 构建上下文管线 | concepts/09 | F-M + F-D14~D16 | 04 |
| 传输/配置/系统端点深化 | concepts/10 | F-B/C/E/O + D11~D13 | 01 |
| 多容器 Pod 网络拓扑实战（含 events 监听） | examples/04 | F-G/H/I/J + N2 + P3 | 06/08 |
| vendor 全量源码信源登记 | references/source-code-map | 全部（结构地图） | — |

新信源 1 份 + 新概念 5 篇 + 新示例 1 篇 = 7 个内容文件；既有 12 篇结论不重写，index/log 追加。
