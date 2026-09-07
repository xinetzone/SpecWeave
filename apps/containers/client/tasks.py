try:
    from jpman_client.tasks import *  # noqa: F401,F403
    from jpman_client.tasks import ns as namespace, ns  # noqa: F401
except ModuleNotFoundError as e:
    if "jpman_client" in str(e):
        raise RuntimeError(
            "请先在 apps/containers/client/ 下执行："
            "  pip install -e . --no-build-isolation\n"
            "然后再使用 invoke（不要手动把 src/ 加入 PYTHONPATH 或 sys.path）"
        ) from e
    raise
