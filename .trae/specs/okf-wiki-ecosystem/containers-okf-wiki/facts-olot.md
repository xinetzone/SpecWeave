# olot 项目事实

1. 项目名称为 olot，版本 1.2.2，描述为 "oci layers on top"，是一个基于 Python 的工具，用于向 OCI 兼容镜像追加层（文件）
2. 项目在 PyPI 发布，包名为 olot，作者为 tarilabs (matteo.mortari@gmail.com)
3. 项目要求 Python 版本 >=3.10，构建系统使用 setuptools>=61.0 和 wheel
4. 核心依赖为 click>=8.1.7,<9 和 pydantic>=2.10.3,<3；可选依赖包括 modelcar-base-image 和 oras-py
5. CLI 入口点为 olot = "olot.cli:cli"，使用 Click 框架构建
6. 项目目录结构包含：backend/（skopeo.py、oras_py.py、oras_cp.py）、oci/（oci_common.py、oci_config.py、oci_defs.py、oci_image_index.py、oci_image_layout.py、oci_image_manifest.py、oci_utils.py 等）、modelpack/（const.py、model_config.py、__init__.py）、utils/、dockerdist/ 子模块
7. cli.py 中定义的 cli() 函数是 Click 命令，参数包括：-m/--modelcard（ModelCarD 文件路径）、--add-modelpack（标志）、-v/--verbose（标志）、--root-dir（模型文件根目录）、ocilayout（OCI layout 目录路径，位置参数）、model_files（模型文件，可变位置参数）、-r/--remove-originals（可选参数）
8. basics.py 中定义核心函数 oci_layers_on_top()，函数签名为：oci_layers_on_top(ocilayout: str | os.PathLike, model_files: Sequence[os.PathLike], modelcard: os.PathLike | None = None, *, labels: dict[str, str] | None = None, annotations: dict[str, str] | None = None, root_dir: str | os.PathLike | None = None, remove_originals: RemoveOriginals | None = None, add_modelpack: bool | None = None)
9. basics.py 中还定义了以下函数：add_modelpack_manifest()、check_and_sanitize_flag_add_modelpack()、check_manifest()、crawl_ocilayout_manifests()、crawl_ocilayout_indexes()、crawl_ocilayout_blobs_to_extract()、write_empty_config_in_ocilayoyt()
10. enums.py 中定义了三个枚举类：CustomStrEnum（基类，提供 values() 类方法）、RemoveOriginals（值为 DEFAULT="default"、ALL="all"）、LayerInputType（值为 FILE="file"、DIRECTORY="directory"）
11. constants.py 中定义了四个层注解键常量：ANNOTATION_LAYER_CONTENT_DIGEST、ANNOTATION_LAYER_CONTENT_TYPE、ANNOTATION_LAYER_CONTENT_INLAYERPATH、ANNOTATION_LAYER_CONTENT_NAME
12. backend/skopeo.py 中提供 skopeo 后端函数：is_skopeo()、skopeo_pull(base_image: str, dest: str | os.PathLike, params: typing.Sequence[str]=())、skopeo_push(src: str | os.PathLike, oci_ref: str, params: typing.Sequence[str]=())、skopeo_inspect(skopeo_ref: str, params: typing.Sequence[str]=()) -> str
13. backend/oras_py.py 中提供纯 Python oras 后端函数：is_oras_py()、oras_py_pull(base_image: str, dest: str | os.PathLike, *, insecure: bool = False, tls_verify: bool = True) -> None、oras_py_push(src: str | os.PathLike, oci_ref: str, *, insecure: bool = False, tls_verify: bool = True) -> None
14. oci/oci_common.py 中定义 MediaTypes 类，包含常量：manifest="application/vnd.oci.image.manifest.v1+json"、index="application/vnd.oci.image.index.v1+json"、layer="application/vnd.oci.image.layer.v1.tar"、layer_gzip="application/vnd.oci.image.layer.v1.tar+gzip"、empty="application/vnd.oci.empty.v1+json"、config="application/vnd.oci.image.config.v1+json"
15. modelpack/const.py 中定义了 ModelPack 相关的 MediaType 常量，包括 ARTIFACTTYPEMODELMANIFEST="application/vnd.cncf.model.manifest.v1+json"、MEDIATYPEMODELCONFIG、MEDIATYPEMODELWEIGHT、MEDIATYPEMODELDOCGZIP 等多种类型
16. 项目支持三种后端：skopeo CLI 工具、oras cp CLI 工具、oras-py Python 库（纯 Python 后端，无需外部工具）
17. 支持 ModelCar 模式，可将 ML 模型文件和 ModelCarD（README.md 元数据）添加到 OCI 镜像层中，文件默认放置在 /models/ 目录下
