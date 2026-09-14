# V 阶段验证报告：podman-py R3（2026-09-14）

验证对象：bundle `doc/bundles/jishu/containers/podman-py/` 第 3 轮新增 7 内容文件 + 更新的 4 个 index + log。

## G4 检查项与结果

### 1. API 真实性 Grep（防虚构）

- **26 个类**逐一 Grep `^class` 命中：UDSSocket/UDSConnection/UDSConnectionPool/UDSPoolManager/UDSAdapter、IPAMPool/IPAMConfig、Pod/PodsManager、Network/NetworksManager、Volume/VolumesManager、Secret/SecretsManager、Manifest/ManifestsManager、RegistryData、EventsManager、BuildMixin、SystemManager、PodmanConfig/ServiceConnection、TLSConfig、APIResponse/APIClient。
- **21 个函数** Grep `^def` 命中：prepare_filters/prepare_body/encode_auth_header/parse_repository/prepare_timestamp/prepare_cidr/frames/stream_frames/stream_helper/demux_output/get_runtime_dir/get_xdg_config_home/create_tar/prepare_containerfile/prepare_containerignore/_key_normalizer/stream_as_text/json_splitter/json_stream/line_splitter/split_buffer。
- **50 处端点字符串** Grep 比对：/pods/{create,json,prune,stats,{id}/json|exists|kill|pause|...}、/networks/{create,json,prune,{key}（无 /json 证实）,{name}/connect|disconnect}、/volumes/{create,json,prune,{name}/export|import}、/secrets/{create,json}、/manifests/{name,registry/{dest}}、/events、/build、/system/df、/info、/auth、/_ping、/version 全部与文档一致。
- **关键行为字符串**：`NotImplementedError("Podman service currently does not support listing manifests.")`、`"exec_run(socket=True) is not supported over SSH"`、attach/attach_socket 两处裸 `NotImplementedError()`、HEADER_SIZE=8、DEFAULT_CHUNK_SIZE 2MiB 全部命中。
- **签名抽查**：`CreateMixin.create(image, command=None, **kwargs)`（containers_create.py L26-31）、`PodsManager.stats(stream=False)`、`Container.stats(stream=True)`、`SecretsManager.__init__(client)`、`SystemManager.__init__(client)` 与文档/示例一致。
- `compatible=True` 全 domain 层仅 system.py L83（login /auth）一处真实调用（另一处为 docstring）——"唯一显式兼容端点"陈述成立。

### 2. 计数断言（独立工具复核，非目测）

| 文档陈述 | 复核方式 | 结果 |
|---|---|---|
| 库代码 39 文件 / 6078 行 | Get-ChildItem + Measure-Object 全量 | ✅ 一致（api 11/1209、domain 22/4455、errors 2/197、顶层 4/217，求和一致） |
| 测试 unit 26 / integration 11 | Glob test_*.py | ✅ 一致 |
| api `__all__` 17 符号 | Select-String 独立计数 | ❌→✅ 初稿误写 14，已改 facts.md + source-code-map.md |
| SecretsManager 唯一自定义 `__init__` | Grep `def __init__` | ❌→✅ SystemManager 同样自定义，07 文档已改为二者并列+区别说明 |
| R 阶段精读"18 个模块" | 按 facts 清单复盘 | ❌→✅ 实为 25 文件（8 api+14 domain 全文+2 分段+tlsconfig），log/root index 已修 |
| Pod list filters 9 类 | 对照 docstring 枚举 | ✅ 9 |
| 门槛表 9 行 | 表格行数 | ✅ 9 |
| 端点差异表 8 资源 | 表格行数 | ✅ 8 |
| 新增内容文档 7、总计 19（11+4+4） | 文件系统 + index | ✅ 一致 |

### 3. 结构/导航/编码门禁

- `python scripts/check-toctrees.py`：唯一失败为并行 WIP 束 `jishu/ai/free-llm-api-roundup-2026` 缺 index（与本束无关，按归属原则不修）；Select-String `podman-py` 命中数 **0**——本束 toctree 4 级闭环（根→3 子 index→19 内容文档）无断头。
- `python scripts/check-utf8.py`：**10170 文件全部有效 UTF-8，exit 0**。
- `python scripts/check-bundles-index.py`：534/535 漂移来自同一未注册 WIP 束；本轮未新增 bundle 目录，漂移前已存在，零本束命中。
- Sphinx：`sphinx -b dummy -E -q` 定向构建 8 个 R3 文件（根 index + 5 概念 + 示例 04 + 信源），后台任务 **exit code 0**，日志零 warning/error。

### 4. Frontmatter / 链接 / 规范

- 7 个新文件 frontmatter 九字段齐全（type/title/description/tags/generated/verified/status/stale_after/sources）；子目录 index 无 frontmatter；仅根 index 带 okf_version。
- 交叉链接全部为 bundle-relative（`/` 开头或同目录相对），目标文件均存在（00-05 概念、01-03 示例、3 份旧信源、新信源）。
- 信源先行：source-code-map 先于概念生成；concepts 两批（3+2+1 ≤7）；index 最后写。
- §6.5 增量纪律：编号 06-10/04 续接；未重写 12 篇旧文档结论；index 表格+toctree 与 log 均为追加/计数更新。

## G4 结论：通过（3 处事实/计数偏差已在交付前修复）
