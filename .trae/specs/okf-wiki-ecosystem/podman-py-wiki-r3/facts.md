# R3 事实清单：podman-py vendor 全量源码精读（第 3 轮增量）

> 信源：`vendor/podman-py`（stable git submodule）
> Git：`v5.8.0-9-g5dd81b4` / commit `5dd81b49f35733a27b8051c47e23d3b4c85ea716` / 2026-08-19 / remote `git@github.com:containers/podman-py.git`
> 包内版本：`podman/version.py` `__version__="5.8.0"`、`__compatible_version__="1.40"`
> 纪律：只记录"代码里有什么"，零推断；每条含 文件:行 锚点。基线（R1/R2 已验证的 00-05 概念）不重复采集。

## A. 版本与包导出

- F-A1 `podman/version.py` L3-4：`__version__ = "5.8.0"`、`__compatible_version__ = "1.40"`。
- F-A2 `podman/__init__.py` L3-7：仅导出 `PodmanClient`、`from_env`、`__version__`（`__all__` 三元素）。
- F-A3 `podman/api/api_versions.py` L7-17：`_api_version(release, significant=3)` 按 `.`/`-`/`+` 正则切取前 N 段；`VERSION = "5.8.0"`、`COMPATIBLE_VERSION = _api_version("1.40", 2) = "1.4"`。
- F-A4 `podman/api/__init__.py` L17：`DEFAULT_CHUNK_SIZE = 2 * 1024 * 1024`（2 MiB）；L21-39 `__all__` 共 **17 个符号**（APIClient/COMPATIBLE_VERSION/DEFAULT_CHUNK_SIZE/VERSION/create_tar/decode_header/encode_auth_header/frames/parse_repository/prepare_body/prepare_cidr/prepare_containerfile/prepare_containerignore/prepare_filters/prepare_timestamp/stream_frames/stream_helper，V 阶段 Select-String 独立计数=17）。

## B. APIClient 传输层（podman/api/client.py，394 行）

- F-B1 L94-101：`supported_schemes` 为 6 元素元组 `"unix","http+unix","ssh","http+ssh","tcp","http"`。
- F-B2 L52-69：`APIResponse` 包装 `requests.Response`；`__getattr__` 转发所有未定义属性。
- F-B3 L71-85：`raise_for_status(not_found=NotFound)`：status<400 直接 return；尝试 JSON 取 `cause`/`message`，JSONDecodeError/KeyError 时用 `self.text`；404 抛 `not_found` 参数指定的类（调用方可传 `ImageNotFound`），其余状态码抛 `APIError`。
- F-B4 L155-169：适配器挂载三分支——scheme `http+unix` → `UDSAdapter` 同时 mount 到 `http://` 与 `https://` 且 `self.trust_env=False`（忽略环境代理）；`http+ssh` → `SSHAdapter` 双 mount；`http` → 标准 `HTTPAdapter`；其他 → `PodmanError("APIClient.supported_schemes changed...")`。
- F-B5 L171-174：`self.path_prefix = f"/v{self.version}/libpod/"`；`self.compatible_prefix = f"/v{self.compatible_version}/"`。
- F-B6 L180-183：默认 User-Agent 为 `PodmanPy/{__version__} (API v{version}; Compatible v{compatible_version})`，并写入 session headers。
- F-B7 L185-207 `_normalize_url`：scheme 不在 supported_schemes → `ValueError`；规范化 `unix→http+unix`、`ssh→http+ssh`、`tcp→http`；netloc 为空时用 path 补到 netloc 并清空 path；netloc 含 `/` 时 `urllib.parse.quote_plus`。
- F-B8 L395-462 `_request`：`compatible = kwargs.get("compatible", False)` 切换前缀；`path = path.lstrip("/")`（注释：leading / makes urljoin crazy）；`scheme = "https" if kwargs.get("verify") else "http"`；用 urljoin(path_prefix, path) 拼 URL；`requests` 抛出的 `OSError` 包装为 `APIError`。
- F-B9 L42-49：`ParameterDeprecationWarning(DeprecationWarning)` + `warnings.simplefilter('always', ...)`。
- F-B10 L209-393：`delete/get/head/post/put` 五方法均为 keyword-only 参数（params/headers/timeout/stream）；`files` 仅 post/put 有；post 的 kwargs 文档含 `compatible` 与 `verify`。

## C. UDS 适配器（podman/api/uds.py，138 行）

- F-C1 L22-43 `UDSSocket(socket.socket)`：`AF_UNIX/SOCK_STREAM`；`connect()` 中 `unquote(urlparse(self.uds).netloc)` 得路径；任何异常包装为 `APIError("Unable to make connection to UDS ...")`。
- F-C2 L46-93：`UDSConnection(urllib3.connection.HTTPConnection)` 从 kwargs pop 出 `uds`；`UDSConnectionPool(HTTPConnectionPool)` 的 `ConnectionCls = UDSConnection`。
- F-C3 L96-126 `UDSPoolManager`：`_PoolKey` namedtuple 在 urllib3 PoolKey 上扩展 `key_uds` 字段；`_pool_classes_by_scheme` 把 `"http"` 与 `"http+ssh"` 都映射到 `UDSConnectionPool`（SSH 本地转发 socket 复用 UDS 池）；`_key_fn_by_scheme` 两 scheme 均用 `_key_normalizer` 偏函数。
- F-C4 L129-179 `UDSAdapter(HTTPAdapter)`：`_pool_kwargs={"uds": uds}`，有 timeout 时加入；`init_poolmanager` 把 uds/timeout 注入 pool kwargs。
- F-C5 `podman/api/adapter_utils.py` L7-51：`_key_normalizer` 注释明示复制自 `urllib3.poolmanager._default_key_normalizer`：scheme/host 转小写、headers/_proxy_headers/_socks_options 转 frozenset、socket_options 转 tuple、上下文键加 `key_` 前缀、缺字段补 None。

## D. api 工具层

- F-D1 `http_utils.py` L10-29 `prepare_filters`：接受 str（`"k=v"`）/list（多项 `"k=v"`）/Mapping 三态，统一为 `dict[str,list]` 后 `json.dumps(sort_keys=True)`；空输入返 None。
- F-D2 L61-109 `prepare_body`：递归剔除值为 None/空 Sized 的键，**False 与 0 保留**；键 `"networks"` 特殊放行（允许 `networks={name: {}}` 空字典值）；非递归层 `""` 也剔除。
- F-D3 L112-113 `encode_auth_header`：`base64.urlsafe_b64encode(json.dumps(auth_config).encode())`。
- F-D4 `parse_utils.py` L15-29 `parse_repository`：`rsplit(":",1)`，仅当右段不含 `/` 才视为 tag（规避 host:port 误切）。
- F-D5 L42-56 `prepare_timestamp`：None→None；int 原样；naive datetime 补 UTC 后算 epoch；其他类型 `ValueError`。
- F-D6 L59-64 `prepare_cidr`：返回 `(str(network_address), base64(netmask.packed).decode())` 二元组（注释：Go JSON decoder 要求）。
- F-D7 L67-80 `frames(response)`：缓冲式，8 字节帧头 `struct.unpack_from(">BxxxL")`（1 字节类型+3 pad+4 字节大端长度），从 `response.content` 逐帧 yield。
- F-D8 L83-107 `stream_frames(response, demux=False)`：循环 `response.raw.read(8)` 读头、`read(frame_length)` 读体；demux=True 时对 `header+data` 调 `demux_output`，yield bytes 或 (stdout,stderr) 元组。
- F-D9 L110-117 `stream_helper(response, decode_to_json=False)`：`response.iter_lines()` 逐行，可选 `json.loads`。
- F-D10 `output_utils.py` L3-49：`HEADER_SIZE=8`、`STDOUT=1`、`STDERR=2`；`demux_output` 按帧循环，数据不足一帧时 `break`（等更多数据），未知 stream_type 忽略；返回 `(stdout or None, stderr or None)`。
- F-D11 `path_utils.py` L9-46 `get_runtime_dir`：优先 `XDG_RUNTIME_DIR`；否则 `/run/user/{uid}`（`os.path.isdir` 验证）；再否则 `/tmp/podmanpy-runtime-dir-fallback-{user}`——用 `lstat`（防 symlink 替换攻击），不存在则 `mkdir(0o700)`；存在但非目录/属主不符/组或其他用户有权限则删除重建 0700。
- F-D12 L49-54 `get_xdg_config_home`：`XDG_CONFIG_HOME` → `~/.config`。
- F-D13 `tlsconfig.py` L4-27：`TLSConfig` docstring 明示 "Provided for compatibility, currently ignored."；`__init__(*args, **kwargs)` 空实现；`configure_client` 静态方法 no-op，注释 TODO 接入 SSHAdapter。
- F-D14 `tar_utils.py` L14-31 `prepare_containerignore`：按序查 `.containerignore`、`.dockerignore`（前者优先），去空行与 `#` 注释行；都不存在返 `[]`。
- F-D15 L34-52 `prepare_containerfile`：dockerfile 与 anchor 同目录（`samefile`）→仅返回文件名；否则 `shutil.copy2(..., follow_symlinks=False)` 复制为 anchor 下 `.containerfile.{random.getrandbits(160):x}`。
- F-D16 L55-119 `create_tar(anchor, name=None, exclude=None, gzip=False)`：filter 仅放行 file/dir/symlink；mtime `<0` 或 `>8**11-1` 钳制（Py issue32713 workaround）；强制 `info.uid=0`、`uname=gname="root"`（注释 do not leak client information）；win32 下 `mode & 0o755 | 0o111`；默认临时文件 `prefix="podman_context", suffix=".tar"`；exclude 追加 tar 自身文件名；`_exclude_matcher` 仅 `fnmatch`，源码注释 FIXME 不支持 `!`、`**`。

## E. 配置解析（podman/domain/config.py，147 行）

- F-E1 L12-21：TOML 解析器四级回退：3.11+ `tomllib` → `tomli` → `toml` → `pytomlpp`。
- F-E2 L75-79：默认配置路径为 `$XDG_CONFIG_HOME/containers/podman-connections.json`（新 JSON），同时记录旧文件 `containers.conf`（TOML），`is_default=True`。
- F-E3 L81-85：路径含 `@@is_test@@` 为测试专用钩子（替换前缀后定位测试目录）。
- F-E4 L90-106：显式 path 先按 JSON 读，异常后尝试 TOML，都失败抛 `AttributeError("...neither a JSON nor a TOML connections file")`。
- F-E5 L109-113：默认路径下若旧 TOML `containers.conf` 存在，读取后 `attrs.update()`（TOML 内容补充进 attrs）。
- F-E6 L128-158 `services`：先装旧 TOML `engine.service_destinations`，再装新 JSON `Connection.Connections`，**同名连接 JSON 覆盖 TOML**（注释明示）。
- F-E7 L160-177 `active_service`：先取新 JSON `Connection.Default` + `Connection.Connections[Default]`；否则旧 TOML `engine.active_service`；都无返 None。
- F-E8 L48-65 `ServiceConnection`：`url` 兼容 `uri`/`URI`（小写优先）；`identity` 兼容 `identity`/`Identity`；`is_machine` 读 `attrs.get("IsMachine", False)`。

## F. 基类（podman/domain/manager.py，137 行）

- F-F1 L24-55：`PodmanResource(ABC)` 构造接收 attrs/client/collection/podman_client，collection 存为 `self.manager`；`.api` 属性在 client 为 None 时抛 `AttributeError`。
- F-F2 L66-80：`id = attrs.get("Id")`；`short_id`：id 以 `sha256:` 开头取前 17 字符，否则前 10 字符。
- F-F3 L82-93：`collection` 是 `manager` 的 property 别名（含 setter），docstring 明示为 Docker SDK 兼容双命名。
- F-F4 L95-102：`reload(**kwargs)` 调 `self.manager.get(self.id, **kwargs)` 并整体替换 attrs（kwargs 可传 compatible）。
- F-F5 L105-149：`Manager(ABC)` 抽象成员：`resource` 属性、`exists/get/list`；同样有 None 守卫的 `.api`。
- F-F6 L151-174 `prepare_model`：传入 PodmanResource 实例→回填 client/podman_client/collection/manager 后原物返回；Mapping→`self.resource(attrs=..., client=..., podman_client=..., collection=self)` 实例化；其他类型 `raise Exception(f"Can't create ...")`。

## G. Pod 资源（pods.py 95 行 / pods_manager.py 134 行）

- F-G1 `pods.py` L21-28：`Pod.id` 读 `attrs["ID"]` 回退 `attrs["Id"]`（大写 ID 优先，与 Container 的 Id 不同）；`name=attrs["Name"]`。
- F-G2 L30-94：Pod 动作方法 `kill(signal=None)`、`pause()`、`restart()`、`start()`、`unpause()` 均 POST `/pods/{id}/<action>`；`stop(timeout=None)` 的 query 参数名为 `"t"`；`remove(force=None)` 委托 `self.manager.remove`。
- F-G3 L96-115：`top(ps_args=None, **)` GET `/pods/{id}/top?ps_args=&stream=False`；响应体为空字符串时返回 `{"Processes": [], "Titles": []}`。
- F-G4 `pods_manager.py` L25-40：`create(name, **kwargs)` POST `/pods/create`，body 复制 kwargs 并强制 `data["name"]=name`，响应取 `body["Id"]` 再 `self.get()` 返回。
- F-G5 L42-60：`exists(key)` GET `/pods/{key}/exists` 返 `response.ok`；`get(pod_id)` GET `/pods/{pod_id}/json`。
- F-G6 L62-87：`list` GET `/pods/json`，docstring 列 9 类 filters：ctr-ids/ctr-names/ctr-number/ctr-status/id/name/status/label/network。
- F-G7 L89-112：`prune(filters=None)` POST `/pods/prune`；逐项检查 `item["Err"]`，非空抛 APIError（explanation `Failed to prune pod '{Id}'`）；返回 `{"PodsDeleted": [...], "SpaceReclaimed": 0}`。
- F-G8 L114-132：`remove(pod_id, force=None)` 接受 Pod 实例（取 .id）或字符串，DELETE `/pods/{id}?force=`。
- F-G9 L134-168：`stats`：`all` 与 `name` 同传 → `ValueError("...mutually exclusive")`；`stream` 默认 **False**（注释：保持旧行为，major 版本再对齐 container.stats）；参数名映射 `name→namesOrIDs`；stream → `api.stream_helper(response, decode_to_json=decode)`；非 stream 且 decode=False 返回原始 `response.content`。

## H. Network 资源（networks.py 116 / networks_manager.py 165 / ipam.py 52）

- F-H1 `networks.py` L36-45：`Network.id` 先取 `attrs["Id"]`（suppress KeyError），否则 `hashlib.sha256(attrs["name"].encode("ascii")).hexdigest()` 推导。
- F-H2 L56-65：`name` 兼容 `Name`/`name`，都无则 `raise KeyError`。
- F-H3 L48-53：`containers` 属性每次新建 `ContainersManager(client=self.client)`，对 `attrs["containers"]` 的键逐个 `get()`；KeyError → `[]`。
- F-H4 L67-70：`reload()` 用 **name**（不是 id）调 `manager.get`。
- F-H5 L72-121 `connect(container, aliases/driver_opt/ipv4_address/ipv6_address/link_local_ips/links=None)`：Container 实例取 id；组装嵌套 PascalCase 结构（IPAMConfig 含 IPv4Address/IPv6Address/Links；外层 EndpointConfig 含 Aliases/DriverOpts/IPAddress/IPAMConfig/Links/NetworkID）；逐层剔除 None/空值；POST `/networks/{name}/connect`，`**kwargs` 透传给请求。
- F-H6 L123-140 `disconnect(container, force=None)`：POST `/networks/{name}/disconnect`，body `{"Container": id, "Force": force}`。
- F-H7 `networks_manager.py` L33-80 `create(name, **kwargs)`：body 键名为 `name/driver/dns_enabled/network_dns_servers/subnets/ipv6_enabled/internal/labels/options`（`enable_ipv6` 映射为 `ipv6_enabled`）；ipam 通过 `_prepare_ipam` 注入；POST `/networks/create` 用 `http_utils.prepare_body`。
- F-H8 L82-103 `_prepare_ipam`：`Driver` → `data["ipam_options"]={"driver": ...}`；遍历 `Config` 生成 `subnets=[{"gateway","subnet","lease_range":{"start_ip","end_ip"}}]`；IPRange 用 `ipaddress.ip_network` 计算 `net[1]` 与 `net[-2]`。
- F-H9 L124-165 `list`：GET `/networks/json`；调用方 names/ids 被并入 filters 字典（`filters["name"]`、`filters["id"]`）。
- F-H10 L167-194 `prune`：逐元素错误键是 **`item["Error"]`**（对比 pods/volumes 的 `"Err"`），Name 进删除列表；SpaceReclaimed 恒 0。
- F-H11 L105-122：`exists` GET `/networks/{key}/exists`；`get(key)` GET `/networks/{key}`（**无 /json 后缀**，与其他资源不同）。
- F-H12 L196-210 `remove`：Network 实例取 `.name`，DELETE `/networks/{name}?force=`。
- F-H13 `ipam.py` L10-36 `IPAMPool(dict)`：键 `AuxiliaryAddresses/Gateway/IPRange/Subnet`（aux_addresses docstring 标注 Ignored）。L39-62 `IPAMConfig(dict)`：`driver` 默认 `"host-local"`，键 `Config/Driver/Options`；docstring 明示 **Podman only supports one pool**。

## I. Volume 资源（volumes.py，175 行，Model 与 Manager 同文件）

- F-I1 L21-28：`Volume.id` 直接返回 `self.name`；`name=attrs.get("Name")`。
- F-I2 L67-93 `create(name=None, driver/driver_opts/labels)`：body 为 PascalCase `{Driver, Labels, Name, Options}`，POST `/volumes/create`。
- F-I3 L114-131 `list`：响应 `status_code == requests.codes.not_found` 时返回 `[]`（不抛错）。
- F-I4 L133-161 `prune`：错误键 `"Err"`，explanation 用 `item.get("Id")`；**累加 `item["Size"]`**，SpaceReclaimed 为真实值（对比 pods/networks 恒 0）。
- F-I5 L41-56：`Volume.inspect(tls_verify=True)` GET `/volumes/{id}/json?tlsVerify=`。
- F-I6 L180-225：`export_archive(name)` GET `/volumes/{name}/export` 返回 `response._content`；`import_archive(name, data=None, path=None)` POST `/volumes/{name}/import`，data 与 path 必须恰好给一个（都不给/都给均 `RuntimeError`），path 不存在也 RuntimeError。

## J. Secret 资源（secrets.py，111 行）

- F-J1 L11-28：`Secret.id = attrs.get("ID")`；`name` 取 `attrs['Spec']['Name']`（suppress KeyError → `""`）；`__repr__` 用 name。
- F-J2 L54-60：`SecretsManager.__init__(self, client)` 显式签名（不经基类 podman_client）。
- F-J3 L62-64：`exists(key)` 用 GET `/secrets/{key}/json` 的 `response.ok`（无独立 /exists 端点）。
- F-J4 L94-120 `create(name, data: bytes, labels=None, driver=None)`：`labels` 参数 docstring 标注 Ignored；name/driver 走 query params，**data 原始字节直接作请求体**，POST `/secrets/create`，再 `self.get(body["ID"])`。
- F-J5 L122-143 `remove(secret_id, all=None)`：DELETE `/secrets/{id}?all=`。

## K. Manifest 资源（manifests.py，205 行）

- F-K1 L19-27：`Manifest.id` 取 `attrs["manifests"][0]["digest"]`，`sha256:` 前缀剥离（suppress KeyError/TypeError/IndexError），失败回退 `self.name`。
- F-K2 L29-52：`name = attrs.get("names")`；`quoted_name = urllib.parse.quote_plus(self.name)`；`names` 为 name 别名；`media_type=attrs["mediaType"]`；`version=attrs["schemaVersion"]`。
- F-K3 L54-94 `add(images, all/annotation/arch/features/os/os_version/variant)`：Image 实例取 `attrs["RepoTags"][0]`；body 固定 `"operation": "update"` 与 images 列表，经 `api.prepare_body`；PUT `/manifests/{quoted_name}`；`raise_for_status(not_found=ImageNotFound)`；末尾 `return self.reload()`。
- F-K4 L96-134 `push(destination, all=None, auth_config=None)`：头 `X-Registry-Auth`（有 auth_config 时 encode_auth_header，否则空串）；POST `/manifests/{quoted_name}/registry/{quote_plus(destination)}?all=&destination=`。
- F-K5 L136-155 `remove(digest)`：含 `@` 时切出 digest 段；PUT body `{"operation":"remove","images":[digest]}`；not_found 映射 ImageNotFound；reload。
- F-K6 L157-160：`reload()` 用 `self.name` 调 manager.get 换 attrs。
- F-K7 L171-211 `ManifestsManager.create(name, images=None, all=None)`：POST `/manifests/{quote_plus(name)}`，images 走 query params（Image 同样取 RepoTags[0]）；get 回 manifest 后**手动补 `attrs["names"]=name`**，`attrs["manifests"] is None` 时置 `[]`。
- F-K8 L213-238：`exists(key)` quote_plus 后 GET `/manifests/{key}/exists`；`get(key)` GET `/manifests/{key}/json`，body 无 `names` 键时补入查询 key。
- F-K9 L240-243：`list(**kwargs)` 直接 `raise NotImplementedError("Podman service currently does not support listing manifests.")`。
- F-K10 L245-255：manager.`remove(name)` DELETE `/manifests/{name}`（name 可能为列表，直接拼路径）；返回 body 并写入 `ExitCode=response.status_code`。

## L. Registry/Image 补充事实

- F-L1 `registry_data.py` L15-45 `RegistryData`：必传 `image_name`；attrs 缺省时 `self.manager.get(image_name).attrs`；`pull(platform=None)` 解析 repository 后调 `manager.pull(repository, tag=self.id, platform=platform)`。
- F-L2 L46-88 `has_platform(platform)`：None→`{}`；dict 须含 os/architecture 否则用 `client.version()` 的 `Os`/`Arch` 补；str 按 `/` 切 os/architecture/variant（边界条件 `1 < len(elements) > 3` 抛 InvalidArgument）；比较 `attrs["Os"]` 与 `attrs["Architecture"]`；注释明示 variant 不被 libpod attrs 承载。
- F-L3 `images_manager.py` L98-121 `get_registry_data(name, auth_config=...)`：auth_config 未使用（`# FIXME populate attrs using auth_config`），以 image.attrs 构造 RegistryData。
- F-L4 `images.py` L27-43：`Image.tags` 过滤掉 `"<none>:<none>"`；`labels` 为空返 `{}`。
- F-L5 L76-112 `Image.save(chunk_size=DEFAULT_CHUNK_SIZE, named=False)`：GET `/images/{img}/get?format=docker-archive`，stream 返 iter_content；`named=True` 用 `tags[0]`（quote）；`named=str` 时该名不在 tags 中 → `InvalidArgument`。
- F-L6 L114-143 `tag(repository, tag, force=False)`：POST `/images/{id}/tag?repo=&tag=`；ok 返 True；`force=True` 且 status_code<=500 返 False；否则 raise_for_status。
- F-L7 `images_manager.py` L123-159 `load(data=None, file_path=None)`：两者皆无/皆有 → PodmanError；POST `/images/load`（application/x-tar）；内部生成器对 `body["Names"]` 逐个 `self.get(item)` yield Image。
- F-L8 L161-222 `prune(all=False, external=False, filters=None)`：API 可能返回 JSON null，代码显式 `if response.json() is not None` 防护；错误聚合成分号分隔字符串一次性抛 APIError；成功返 `{ImagesDeleted:[{Deleted,Untagged:""}], SpaceReclaimed}`。
- F-L9 L224-230 `prune_builds()`：纯本地返回 `{"CachesDeleted": [], "SpaceReclaimed": 0}`，不发请求。
- F-L10 L232-295 `push(repository, tag=None, ...)`：POST `/images/{quote_plus(name)}/push`，`raise_for_status(not_found=ImageNotFound)`；**进度 body 为客户端本地合成的 2 条 dict**（`Pushing repository {repository} ({tag_count} tags)` 与 `Pushing`），不迭代服务端响应体；stream=True 经 `_push_helper` 生成器产出（decode 控制 dict/json 字符串），非 stream 拼接为一个字符串返回。
- F-L11 L309-382 `pull`：tag 空 → parse_repository 解析或 `"latest"`；params 含 `policy`（默认 always）、`reference`、`tlsVerify`（默认 True）、`compatMode`（默认 True）；all_tags 置 allTags 否则 reference=`repo:tag`；platform 切 `OS/Arch/Variant`（`1 < len(tokens) > 3` → ValueError）。
- F-L12 L384-414：`progress_bar=True` 时若 rich `Progress is None` → `ModuleNotFoundError('progress_bar requires rich.progress module')`；强制 `compatMode=True`、`stream=True`；Rich 四列控件（TextColumn/BarColumn/TaskProgressColumn/TimeRemainingColumn）消费 iter_lines，**返回 None**（Image 对象被消费掉）。
- F-L13 L416-429：stream → `_stream_helper`；非 stream **反向遍历** `reversed(list(response.iter_lines()))` 找最后一条含 `id`（或 all_tags 下含 `images`）的 JSON 转 Image；找不到返回 `self.resource()`（空 Image 实例）。
- F-L14 L431-460 `__show_progress_bar`：仅处理 status 为 `Download complete`/`Downloading` 的行（其他跳过）；层 id 维度任务表；小层秒下场景直接补 completed=100。
- F-L15 L555-585 `_stream_helper`：检查 `response.raw._fp.chunked`——chunked 则 `read(1)` 阻塞拿首字节+`chunk_left` 读整块，逐块 json.loads；JSONDecodeError/UnicodeDecodeError/`error` 键三种情况调 `_stream_error_helper`；非 chunked（通常立即出错）调 `self._result(response, json=decode)`。
- F-L16 L23-33：rich.progress 五个符号 try import，失败 `Progress = None`。

## M. 构建管线（images_build.py，188 行）

- F-M1 L26 `BuildMixin.build(**kwargs)` 声明返回 `tuple[Image, Iterator[bytes]]`。
- F-M2 L87-120 三种上下文输入：(a) `custom_context=True` 必须同时有 fileobj 与 dockerfile，否则两条不同文案的 PodmanError，body 直接用 fileobj；(b) 仅有 fileobj → 建 `tempfile.TemporaryDirectory()`，把 dockerfile 写入后 `api.create_tar(anchor=tmp, gzip=...)`；(c) path → `prepare_containerfile` 决定是否代理拷贝、`prepare_containerignore` 取排除模式、`create_tar(anchor, exclude, gzip)`。
- F-M3 L122-141：POST `/build`，头 `Content-type: application/x-tar`，`stream=True`，timeout 单独 float 化；请求后 `body.close()`（若有）与临时目录 `path.cleanup()`。
- F-M4 L143：`raise_for_status(not_found=ImageNotFound)`。
- F-M5 L145-161：`marker = re.compile(r"(^[0-9a-f]+)\n$")`；`itertools.tee(response.iter_lines())` 分叉报告流与消费流；逐行 json.loads，`error` 键 → `BuildError(result["error"], report_stream)`；`stream` 键匹配 marker 得 image_id；最终 `self.get(image_id)` 返回，未取到 id → `BuildError(unknown or "Unknown", report_stream)`。
- F-M6 L163-220 `_render_params`：path/fileobj 均无 → TypeError；gzip 与 encoding 同给 → PodmanError；dockerfile 缺省随机 `.containerfile.{getrandbits(160):x}`；`layers` 默认 True；`outputformat` 默认 `application/vnd.oci.image.manifest.v1+json`；未支持 kwargs 静默丢弃；buildargs/cache_from/container_limits（cpuperiod/cpuquota/cpusetcpus/cpushares/memory/memswap）/extra_hosts/labels/secrets 分别 json.dumps。

## N. 事件与流式（events.py / json_stream.py / containers.py 流式方法）

- F-N1 `events.py` L15-24：`EventsManager` 仅一个 list 方法（`too-few-public-methods`）；`client.py` L195-196 门面 `events()` **每次调用现 new 一个 EventsManager**（非 cached_property）。
- F-N2 L26-59 `list(since=None, until=None, filters=None, decode=False)`：params `filters/since/stream=True/until`（时间走 prepare_timestamp），GET `/events` stream=True，逐行 `response.iter_lines()`，decode 时 json.loads。
- F-N3 `json_stream.py` L6-41：模块级 `json_decoder = json.JSONDecoder()`；`json_splitter` 用 `raw_decode` 从缓冲切出一个对象 + 剩余串（WHITESPACE 正则跳空白），ValueError→None；`json_stream(stream) = split_buffer(stream, json_splitter, json_decoder.decode)`——兼容"部分条目有换行、部分没有"的不一致缓冲。
- F-N4 L44-75：`line_splitter` 按 `\n` 切（块保留尾分隔符）；`split_buffer` 持续拼接 buffered 循环切分；流结束后残块 decode 异常包装为 `StreamParseError(e) from e`；`stream_as_text` 对 bytes 用 utf-8 replace 解码。
- F-N5 `containers.py` L71-91：`attach(**kwargs)` 与 `attach_socket(**kwargs)` 均直接 `raise NotImplementedError()`。
- F-N6 L136-206 `exec_run`：environment 为 dict 时转 `["K=V"]` 列表；`Cmd` 为字符串时 `shlex.split`；创建体含 AttachStderr/Stdin/Stdout/Cmd/Env/Privileged/Tty/WorkingDir/User；`stream = stream and not detach`。
- F-N7 L213-245：先 POST `/containers/{self.name}/exec` 取 `Id`；`socket=True` 时：scheme 为 `http+ssh` → `NotImplementedError("exec_run(socket=True) is not supported over SSH")`；否则 POST `/exec/{id}/start` 带头 `Connection: Upgrade`、`Upgrade: tcp`、stream=True；从 `start_resp.raw.connection.sock` 取裸 socket，取不到抛 APIError；`sock._hijacked_response = start_resp` 锚定响应防 urllib3 回收连接；返回 `(None, sock)`，调用方自管读写关闭。
- F-N8 L248-262：常规 start POST `/exec/{id}/start`；stream → `(None, api.stream_frames(start_resp, demux=demux))`；非 stream 再 GET `/exec/{id}/json` 取 `ExitCode`；demux 时对 `start_resp.content` 调 demux_output，返回 `(ExitCode, (stdout, stderr))`。
- F-N9 L326-359 `logs`：`follow` 缺省取 `stream` 的值；params follow/since/stderr/stdout/tail/timestamps/until；stream 返 `api.stream_frames(response)`（**logs 路径不暴露 demux**），非 stream 返 `api.frames(response)`。
- F-N10 L454-482 `stats`：`stream` 默认 **True**（与 PodsManager.stats 默认 False 相反）；GET `/containers/stats?containers={id}&stream=`；stream→stream_helper(decode)；非 stream decode 返 json.loads(content) 否则原始 content。
- F-N11 L511-534 `top`：stream 默认 False；stream 时 stream_helper 固定 decode_to_json=True。
- F-N12 L764-801 `wait`：condition 为 str 时包成 list；POST `/containers/{id}/wait?condition=&interval=`（`if condition != []`/`if interval != ""` 守卫），timeout 透传；返回 response.json()（退出码整数）；condition 合法值 docstring：configured/created/running/stopped/paused/exited/removing/stopping。
- F-N13 L264-300：`export(chunk_size=2MiB)` GET `/containers/{id}/export` stream iter_content；`get_archive(path)` GET `/containers/{id}/archive?path=[path]`，stat 从头 `x-docker-container-path-stat` 经 `api.decode_header` 解码，返回 (iter_content, stat dict)。
- F-N14 L484-509 `stop`：params all/timeout；给 timeout 时 HTTP 层 timeout = 参数 ×1.5；204 no_content 成功返回；304 not_modified 且 ignore=True 静默；其余响应读 body cause/message 抛 APIError。

## O. SystemManager 与门面直方法（system.py 89 行）

- F-O1 L23-31 `df()`：GET `/system/df` → json。
- F-O2 L33-37 `info(*_, **__)`：GET `/info`，所有参数忽略。
- F-O3 L39-87 `login`：POST `/auth`，**compatible=True**（走 Docker 兼容前缀 `/v1.4/`），`verify=tls_verify`；body 键 `username/password/email/serveraddress/auth/identitytoken/registrytoken`（经 prepare_body）。
- F-O4 L89-92 `ping()`：HEAD `/_ping`，返回 `response.ok` 布尔（不 raise）。
- F-O5 L94-106 `version(**kwargs)`：GET `/version`；`api_version=False` 时删除 body 的 `APIVersion` 键（默认 True 保留）。
- F-O6 `client.py` L190-223：门面 7 直方法 df/events/info/login/ping/version/close，均转发 system（events 例外转发现建 EventsManager）；方法定义后用 `fn.__doc__ = Manager 方法.__doc__` 复制 docstring。
- F-O7 L225-237：`swarm` property 抛 NotImplementedError；`services = configs = nodes = swarm` 别名。

## P. 测试基建与官方示例

- F-P1 `tests/integration/base.py` L28-66：`IntegrationTest(fixtures.TestWithFixtures)`；setUpClass 读 `PODMAN_BINARY`（默认 "podman"），`shutil.which` 找不到 → AssertionError；`PODMAN_LOG_LEVEL` 默认 INFO；setUp 用 fixtures.TempDir + uuid 生成临时 socket_file（`unix://{path}`），由 `utils.PodmanLauncher` 启动并 addCleanup 停止。
- F-P2 `tests/utils.py` L7-43：`OS_RELEASE = freedesktop_os_release()`（3.10 以下手解析 /etc/os-release）；`PODMAN_VERSION = podman_version()` 调 `podman info --format "{{.Version.Version}}"` 子进程，正则取首组 x.y.z 转 int 元组；`is_root()` 用 `os.geteuid()==0`。
- F-P3 `contrib/examples/demo.py` L1-36：with PodmanClient() → ping → version 报告取 `Version`、`Components[0].Details.APIVersion`、`MinAPIVersion` → pull `quay.io/libpod/alpine:latest`（两种调用形式）→ `pods.create("demo_pod")` → `containers.create(image, pod=pod)`（容器 attrs 有 `Pod` 键）→ `pod.remove(force=True)` → images.remove(force=True) → list。
- F-P4 测试文件计数（待 V 阶段 Glob 独立复核）：unit/ 与 integration/ 两个 test 包，conftest.py 15 行、tests/errors.py 17 行、tests/utils.py 34 行。

## G1 自检

全部条目为源码中可 grep/可 Read 复核的客观事实（类名、签名、端点、常量、控制流），无"用于/目的是/设计为"类推断词；推断性结论统一留到 I 阶段 insights.md。
