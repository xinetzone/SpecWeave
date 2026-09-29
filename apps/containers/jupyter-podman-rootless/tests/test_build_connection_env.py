"""CLI build connection environment regression tests."""
from importlib import import_module
import os
from pathlib import Path

import pytest
from invoke import Context


build_module = import_module("jpman_builder.tasks.build")


@pytest.mark.parametrize(
    ("runtime", "host", "expected_unset"),
    [
        ("podman", "npipe:////./pipe/podman-machine-default", ("CONTAINER_HOST",)),
        ("podman", "npipe://[", ("CONTAINER_HOST",)),
        ("podman", "ssh://user@machine/run/podman.sock", ()),
        ("docker", "npipe:////./pipe/docker_engine", ()),
    ],
)
def test_build_cli_unsets_only_unsupported_podman_npipe(
    monkeypatch, capsys, runtime, host, expected_unset
):
    calls = []
    monkeypatch.setattr(build_module, "detect_runtime", lambda: runtime)
    monkeypatch.setattr(build_module.platform, "system", lambda: "Windows")
    monkeypatch.setattr(build_module, "run_cmd", lambda *args, **kwargs: calls.append(kwargs))
    monkeypatch.setenv("CONTAINER_HOST", host)

    build_module._build_via_cli(
        Context(),
        Path.cwd(),
        "jupyter-podman-rootless:latest",
        "tuna",
        "tuna",
        "tuna",
        False,
    )

    assert calls[0].get("unset_env", ()) == expected_unset
    assert os.environ["CONTAINER_HOST"] == host
    output = capsys.readouterr().out
    assert ("忽略 Podman CLI 不支持的 CONTAINER_HOST=npipe" in output) == bool(
        expected_unset
    )
