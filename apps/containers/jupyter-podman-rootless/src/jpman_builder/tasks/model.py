"""ML model management tasks via OMLMD (OCI Artifact) and OLOT (KServe ModelCar).

Provides commands for two complementary ML model distribution paradigms:
  - OMLMD: push/pull/config — custom media type ML model artifacts (x-mlmodel)
  - OLOT:  pack/extract    — KServe ModelCar standard OCI images (/models/)

All commands run inside the Jupyter container via three-tier exec backend:
  1. podman-compose exec (declarative, daemon-less)
  2. podman-py SDK exec_run (REST API)
  3. CLI podman exec (fallback)
"""
from pathlib import Path

from invoke import task
from invoke.exceptions import Exit

from .client import PodmanNotFound, compose_available, get_client, sdk_available
from .compose_backend import compose_exec, is_compose_ready
from .utils import container_running as cli_container_running, detect_runtime, run_cmd

_DEFAULT_USER = "devuser"
_DEFAULT_WORKDIR = "/workspace"


def _should_use_compose():
    return compose_available() and is_compose_ready()


def _resolve_target(c, target):
    """Resolve target registry URL from argument or config."""
    if target:
        return target
    return c.model.get("registry_url", "localhost:5000")


def _quote(value):
    """Shell-quote a value for safe use in bash -c."""
    return "'" + str(value).replace("'", "'\\''") + "'"


def _build_push_cmd(target, path, name=None, description=None, author=None,
                    model_format=None, version=None, plain_http=True, metadata=None):
    parts = ["cd", _DEFAULT_WORKDIR, "&&", "omlmd", "push", _quote(target), _quote(path)]
    if plain_http:
        parts.append("--plain-http")
    if name:
        parts.extend(["-m", _quote(f"name={name}")])
    if description:
        parts.extend(["-m", _quote(f"description={description}")])
    if author:
        parts.extend(["-m", _quote(f"author={author}")])
    if model_format:
        parts.extend(["-m", _quote(f"model_format_name={model_format}")])
    if version:
        parts.extend(["-m", _quote(f"customProperties.version={version}")])
    if metadata:
        for m in metadata:
            parts.extend(["-m", _quote(str(m))])
    return " ".join(parts)


def _build_pull_cmd(target, output, plain_http=True):
    parts = ["cd", _DEFAULT_WORKDIR, "&&", "omlmd", "pull", _quote(target), _quote(output)]
    if plain_http:
        parts.append("--plain-http")
    return " ".join(parts)


def _build_config_cmd(target, output_format="yaml", plain_http=True):
    parts = ["cd", _DEFAULT_WORKDIR, "&&", "omlmd", "get", "config", _quote(target), "-o", output_format]
    if plain_http:
        parts.append("--plain-http")
    return " ".join(parts)


def _exec_in_container(c, name, command, user=_DEFAULT_USER):
    """Execute a command in the running container using three-tier backend."""
    # Tier 1: podman-compose exec
    if _should_use_compose():
        project_root = Path(__file__).parent.parent.resolve()
        return compose_exec(project_root=project_root, service="jupyter", command=command, user=user)

    # Tier 2: podman-py SDK
    if sdk_available():
        with get_client() as client:
            if client is not None:
                if _exec_via_sdk(client, name, command, user):
                    return True

    # Tier 3: CLI fallback
    _exec_via_cli(c, name, command, user)
    return True


def _exec_via_sdk(client, name, command, user):
    """Execute command via podman-py SDK. Returns True on success."""
    try:
        container = client.containers.get(name)
        if container.status != "running":
            raise Exit(
                f"Container {name} is not running, please start it first with 'invoke run'"
            )
        exit_code, output = container.exec_run(
            command, user=user, demux=False, workdir=_DEFAULT_WORKDIR
        )
        if output:
            print(output.decode("utf-8", errors="replace"))
        return exit_code == 0
    except PodmanNotFound:
        raise Exit(f"Container {name} does not exist")
    except Exit:
        raise
    except Exception as e:
        print(f"[SDK] Command failed, falling back to CLI: {e}")
        return False


def _exec_via_cli(c, name, command, user):
    """Execute command via podman CLI."""
    runtime = detect_runtime()
    if not cli_container_running(c, runtime, name):
        raise Exit(
            f"Container {name} is not running, please start it first with 'invoke run'"
        )
    cmd = f'{runtime} exec -it -u {user} -w {_DEFAULT_WORKDIR} {name} bash -c {_quote(command)}'
    run_cmd(c, cmd, pty=True)


@task(iterable=["metadata"], help={
    "target": "OCI registry target (e.g., localhost:5000/my-model:v1)",
    "path": "Path to model file/directory inside container (default: current workspace dir)",
    "name": "Model name metadata",
    "description": "Model description metadata",
    "author": "Model author metadata",
    "model-format": "Model format name (e.g., pickle, onnx, pytorch)",
    "version": "Model version tag",
    "plain-http": "Use plain HTTP (no TLS) for registry connection (default: True)",
    "metadata": "Additional metadata key=value pairs (repeatable, -m key=value)",
    "container-name": "Container name override",
})
def push(c, target=None, path=".", name=None, description=None, author=None,
         model_format=None, version=None, plain_http=True, metadata=None,
         container_name=None):
    """Push ML model to OCI registry via omlmd in container.

    Pushes a model file or directory with metadata to an OCI registry.
    Set --no-plain-http for HTTPS registries (GHCR, Docker Hub, etc.).
    """
    if container_name is None:
        container_name = c.container.get("container_name", "jupyter-podman")

    target = _resolve_target(c, target)
    print(f"[Model] Pushing to registry: {target}")
    cmd = _build_push_cmd(
        target=target, path=path, name=name, description=description,
        author=author, model_format=model_format, version=version,
        plain_http=plain_http, metadata=metadata,
    )
    _exec_in_container(c, container_name, cmd)


@task(help={
    "target": "OCI registry target (e.g., localhost:5000/my-model:v1)",
    "output": "Output directory inside container (default: current workspace dir)",
    "plain-http": "Use plain HTTP (no TLS) for registry connection (default: True)",
    "container-name": "Container name override",
})
def pull(c, target=None, output=".", plain_http=True, container_name=None):
    """Pull ML model from OCI registry via omlmd in container."""
    if container_name is None:
        container_name = c.container.get("container_name", "jupyter-podman")

    target = _resolve_target(c, target)
    print(f"[Model] Pulling from registry: {target} -> {output}")
    cmd = _build_pull_cmd(target=target, output=output, plain_http=plain_http)
    _exec_in_container(c, container_name, cmd)


@task(name="config", help={
    "target": "OCI registry target (e.g., localhost:5000/my-model:v1)",
    "output-format": "Output format: yaml or json (default: yaml)",
    "plain-http": "Use plain HTTP (no TLS) for registry connection (default: True)",
    "container-name": "Container name override",
})
def model_config(c, target=None, output_format="yaml", plain_http=True, container_name=None):
    """Get ML model metadata config from OCI registry via omlmd."""
    if container_name is None:
        container_name = c.container.get("container_name", "jupyter-podman")

    target = _resolve_target(c, target)

    if output_format not in ("json", "yaml"):
        raise Exit(f"output_format must be 'json' or 'yaml', got: {output_format}")

    print(f"[Model] Metadata config for: {target}")
    cmd = _build_config_cmd(target=target, output_format=output_format, plain_http=plain_http)
    _exec_in_container(c, container_name, cmd)


def _build_pack_cmd(base, target, files, modelcard=None, root_dir=None,
                    labels=None, annotations=None, plain_http=True):
    parts = ["cd", _DEFAULT_WORKDIR, "&&", "olot_car.py", "pack",
             "--base", _quote(base), "--target", _quote(target)]
    if modelcard:
        parts.extend(["--modelcard", _quote(modelcard)])
    if root_dir:
        parts.extend(["--root-dir", _quote(root_dir)])
    if labels:
        for lbl in labels:
            parts.extend(["-l", _quote(str(lbl))])
    if annotations:
        for ann in annotations:
            parts.extend(["-a", _quote(str(ann))])
    if not plain_http:
        parts.append("--no-plain-http")
    for f in files:
        parts.append(_quote(str(f)))
    return " ".join(parts)


def _build_extract_cmd(source, output, tar_filter_dir="/models", plain_http=True):
    parts = ["cd", _DEFAULT_WORKDIR, "&&", "olot_car.py", "extract",
             "--source", _quote(source), "--output", _quote(output)]
    if tar_filter_dir != "/models":
        parts.extend(["--tar-filter-dir", _quote(tar_filter_dir)])
    if not plain_http:
        parts.append("--no-plain-http")
    return " ".join(parts)


@task(iterable=["file", "label", "annotation"], help={
    "base": "Base image reference (required, e.g., quay.io/mmortari/hello-world-wait:latest)",
    "target": "Target ModelCar image reference (e.g., localhost:5000/my-model:v1)",
    "file": "Model file path inside container (repeatable, -f path)",
    "modelcard": "Path to ModelCarD README.md inside container",
    "root-dir": "Root directory for preserving subdirectory structure",
    "label": "OCI image labels key=value (repeatable, -l key=value)",
    "annotation": "OCI manifest annotations key=value (repeatable, -a key=value)",
    "plain-http": "Use plain HTTP (no TLS) for registry connection (default: True)",
    "container-name": "Container name override",
})
def pack(c, base, target=None, file=None, modelcard=None, root_dir=None,
         label=None, annotation=None, plain_http=True, container_name=None):
    """Pack model files into KServe ModelCar image and push to registry via olot.

    Creates a standard OCI image with model files at /models/ (KServe ModelCar),
    using the pure-Python oras-py backend (no Docker daemon required).
    Specify --no-plain-http for HTTPS registries (GHCR, Docker Hub, etc.).
    """
    if not file:
        raise Exit("At least one --file/-f is required (model file to pack)")
    if container_name is None:
        container_name = c.container.get("container_name", "jupyter-podman")

    target = _resolve_target(c, target)
    print(f"[ModelCar] Packing {len(file)} file(s) into: {target}")
    print(f"[ModelCar] Base image: {base}")
    cmd = _build_pack_cmd(
        base=base, target=target, files=file, modelcard=modelcard,
        root_dir=root_dir, labels=label, annotations=annotation,
        plain_http=plain_http,
    )
    _exec_in_container(c, container_name, cmd)


@task(help={
    "source": "Source ModelCar image reference to extract from",
    "output": "Output directory inside container (default: ./extracted-models/)",
    "tar-filter-dir": "Directory prefix to extract (default: /models)",
    "plain-http": "Use plain HTTP (no TLS) for registry connection (default: True)",
    "container-name": "Container name override",
})
def extract(c, source, output="./extracted-models", tar_filter_dir="/models",
            plain_http=True, container_name=None):
    """Extract /models directory from KServe ModelCar image to local path.

    Reverse of pack: pulls a ModelCar image and extracts its /models content
    to the specified output directory inside the container.
    """
    if container_name is None:
        container_name = c.container.get("container_name", "jupyter-podman")

    print(f"[ModelCar] Extracting /models from: {source} -> {output}")
    cmd = _build_extract_cmd(
        source=source, output=output, tar_filter_dir=tar_filter_dir,
        plain_http=plain_http,
    )
    _exec_in_container(c, container_name, cmd)
