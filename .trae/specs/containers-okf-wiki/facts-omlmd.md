# omlmd 项目事实

1. 项目名称为 omlmd，版本 0.1.6，描述为 "OCI Artifact for ML model & metadata"，是一个利用 OCI Artifact 和容器来处理 ML 模型和元数据的蓝图、模式和工具链集合（Python SDK 和 CLI 形式）
2. 项目在 PyPI 发布，包名为 omlmd，作者为 Matteo Mortari (matteo.mortari@gmail.com)，许可证为 Apache-2.0
3. 项目要求 Python 版本 ^3.9（支持 3.9、3.10、3.11、3.12），构建系统使用 poetry-core
4. 核心依赖为 oras>=0.2.23,<0.3.0、pyyaml^6.0.1、click^8.1.7、cloup^3.0.5；开发依赖包括 pytest、jq、scikit-learn、model-registry、ruff、mypy 等
5. CLI 入口点为 omlmd = "omlmd.cli:cli"，使用 Click + Cloup 框架构建，支持子命令
6. 项目目录结构：omlmd/ 包含 __init__.py（空）、cli.py、constants.py、helpers.py、listener.py、model_metadata.py、provider.py；另有 docs/、e2e/、tests/ 目录
7. cli.py 中定义了 cli 命令组（使用 @cloup.group() 装饰器），包含以下子命令：pull（拉取 OCI Artifact）、get（子命令组，包含 config 子命令）、crawl（爬取元数据）、push（推送 OCI Artifact）
8. cli.py 中 pull 命令参数：--plain-http（标志，允许非 SSL 连接）、target（位置参数，目标镜像引用）、-o/--output（输出目录，默认为当前工作目录）、--media-types/-m（多个值，过滤媒体类型）
9. cli.py 中 push 命令参数：--plain-http（标志）、target（位置参数）、path（位置参数，模型文件路径）、-m/--metadata（元数据文件路径，JSON 或 YAML 格式）、--empty-metadata（标志，推送空元数据）；元数据选项使用 cloup.option_group 并要求互斥（require_one 约束）
10. model_metadata.py 中定义 @dataclass 类 ModelMetadata，字段包括：name: str | None、description: str | None、author: str | None、customProperties: dict[str, Any] | None（默认空 dict）、uri: str | None、model_format_name: str | None、model_format_version: str | None
11. ModelMetadata 类方法：to_json() -> str、to_dict() -> dict[str, Any]、to_annotations_dict() -> dict[str, str]、is_empty() -> bool、静态方法 from_json(json_str: str) -> "ModelMetadata"、to_yaml() -> str、静态方法 from_yaml(yaml_str: str) -> "ModelMetadata"、静态方法 from_dict(data: dict[str, Any]) -> "ModelMetadata"
12. model_metadata.py 中定义函数 deserialize_mdfile(file)，从文件反序列化元数据，自动尝试 JSON 解析，失败则尝试 YAML 解析，都失败则抛出 ValueError
13. provider.py 中定义类 OMLMDRegistry，继承自 oras.provider.Registry，使用 @ensure_container 装饰器
14. OMLMDRegistry 类方法：download_layers(self, package, download_dir, media_types)（根据 media_types 过滤下载层）、get_config(self, package) -> str（获取配置层内容，使用临时目录处理）
15. helpers.py 中定义 @dataclass 类 Helper，字段：_registry: OMLMDRegistry（默认使用 insecure=True 初始化）、_listeners: list[Listener]（默认空列表）
16. Helper 类方法：类方法 from_default_registry(cls, insecure: bool)、push(self, target: str, path: Path | str, name: str | None = None, description: str | None = None, author: str | None = None, model_format_name: str | None = None, model_format_version: str | None = None, **kwargs)、pull(self, target: str, outdir: Path | str, media_types: Sequence[str] | None = None)、get_config(self, target: str) -> str、crawl(self, targets: Sequence[str]) -> str、add_listener(self, listener: Listener) -> None、remove_listener(self, listener: Listener) -> None、notify_listeners(self, event: Event) -> None
17. constants.py 中定义常量：FILENAME_METADATA_JSON="model_metadata.omlmd.json"、FILENAME_METADATA_YAML="model_metadata.omlmd.yaml"、MIME_APPLICATION_CONFIG="application/x-config"、MIME_APPLICATION_MLMODEL="application/x-mlmodel"
18. Helper.push() 方法会自动生成 model_metadata.omlmd.json 和 model_metadata.omlmd.yaml 临时元数据文件，推送时包含三个文件：模型文件（application/x-mlmodel）、JSON 元数据（application/x-config）、YAML 元数据（application/x-config），完成后清理临时文件
19. Helper.crawl() 方法接受多个目标引用，调用 get_config() 获取每个目标的配置，返回 JSON 数组格式的结果
