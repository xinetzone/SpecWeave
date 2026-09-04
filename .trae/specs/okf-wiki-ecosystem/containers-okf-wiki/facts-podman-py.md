# podman-py 项目事实

1. 项目名称为 podman（PyPI 包名），版本为 5.8.0，兼容 API 版本为 1.40，描述为 "Bindings for Podman RESTful API"，是 Podman RESTful API 的 Python 绑定库
2. 项目要求 Python 版本 >=3.9，支持 3.9、3.10、3.11、3.12、3.13，构建系统使用 setuptools>=46.4，setup.py 中自定义 build_py 类排除 podman/tests/* 包
3. 核心依赖为 requests>=2.24、tomli>=1.2.3（Python<3.11 时）、urllib3；可选依赖分为三组：progress_bar（rich>=12.5.1）、docs（sphinx）、test（coverage、fixtures、pytest、requests-mock、tox）
4. 项目主要入口在 podman/__init__.py，导出：PodmanClient、from_env、__version__；同时提供别名 DockerClient = PodmanClient 以兼容 Docker SDK 代码
5. 版本号定义在 podman/version.py：__version__ = "5.8.0"，__compatible_version__ = "1.40"
6. podman/client.py 中定义核心类 PodmanClient，继承自 AbstractContextManager，支持上下文管理器协议（with 语句）
7. PodmanClient.__init__() 接受关键字参数：base_url（Podman 服务 URL，支持 unix、http+unix、ssh、http+ssh、tcp、http scheme）、version（API 版本，默认 auto）、timeout（超时秒数）、tls、user_agent、credstore_env、use_ssh_client、max_pool_size、connection（从 containers.conf 读取连接配置）、identity（SSH 密钥路径）
8. PodmanClient 提供类方法 from_env(cls, *, version: str = "auto", timeout: Optional[int] = None, max_pool_size: Optional[int] = None, ssl_version: Optional[int] = None, assert_hostname: bool = False, environment: Optional[dict[str, str]] = None, credstore_env: Optional[dict[str, str]] = None, use_ssh_client: bool = True) -> "PodmanClient"，从环境变量（CONTAINER_HOST、DOCKER_HOST、CONTAINER_TLS_VERIFY、DOCKER_TLS_VERIFY、CONTAINER_CERT_PATH、DOCKER_CERT_PATH）读取连接配置
9. PodmanClient 使用 @cached_property 提供以下管理器属性：containers（ContainersManager）、images（ImagesManager）、manifests（ManifestsManager）、networks（NetworksManager）、volumes（VolumesManager）、quadlets（QuadletsManager）、pods（PodsManager）、secrets（SecretsManager）、system（SystemManager）
10. PodmanClient 提供直接方法：df() -> dict[str, Any]、events(*args, **kwargs)、info(*args, **kwargs)、login(*args, **kwargs)、ping() -> bool、version(*args, **kwargs)、close()；swarm/services/configs/nodes 属性抛出 NotImplementedError（不支持 Swarm 操作）
11. podman/api/ 目录包含 HTTP 传输层实现：api/client.py（APIClient 类，继承自 requests.Session）、ssh.py（SSHAdapter）、uds.py（UDSAdapter）、adapter_utils.py、api_versions.py、http_utils.py、output_utils.py、parse_utils.py、path_utils.py、tar_utils.py
12. podman/api/__init__.py 导出：APIClient、VERSION、COMPATIBLE_VERSION、DEFAULT_CHUNK_SIZE（2*1024*1024=2MB）、create_tar、decode_header、encode_auth_header、frames、parse_repository、prepare_body、prepare_cidr、prepare_containerfile、prepare_containerignore、prepare_filters、prepare_timestamp、stream_frames、stream_helper
13. podman/api/client.py 中定义 APIResponse 类（代理 requests.Response，重写 raise_for_status() 实现 Podman API 错误映射：404 映射到 NotFound，其他错误映射到 APIError）和 APIClient 类
14. APIClient.supported_schemes 类变量列出支持的 URL scheme：["unix", "http+unix", "ssh", "http+ssh", "tcp", "http"]
15. podman/domain/ 目录包含高层领域管理器：config.py（PodmanConfig）、containers.py、containers_create.py、containers_manager.py、containers_run.py、events.py（EventsManager）、images.py、images_build.py、images_manager.py、ipam.py、json_stream.py、manager.py、manifests.py（ManifestsManager）、networks.py、networks_manager.py、pods.py、pods_manager.py、quadlets.py（QuadletsManager）、registry_data.py、secrets.py（SecretsManager）、system.py（SystemManager）、volumes.py（VolumesManager）
16. podman/errors/ 目录包含异常定义：exceptions.py 中定义 APIError、NotFound、PodmanError 等异常类
17. podman/tests/ 目录分为 unit/（单元测试）和 integration/（集成测试）两个子目录，测试配置在 pyproject.toml 中 testpaths = ["podman/tests"]
18. 默认连接：当未指定 base_url 或 connection 时，PodmanClient 会检查 PodmanConfig 的 active_service，如果是 machine 则使用其 URL，否则回退到本地 Unix socket：http+unix://<runtime_dir>/podman/podman.sock（runtime_dir 通过 podman.api.path_utils.get_runtime_dir() 获取）
19. 传输适配器：Unix socket 使用 UDSAdapter，SSH 连接使用 SSHAdapter，普通 HTTP 使用 requests.adapters.HTTPAdapter
