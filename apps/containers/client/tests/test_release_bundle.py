"""release/ 客户独立交付包的 daemon-free 结构守卫。

验证随包骨架（compose / 控制脚本 / env 模板）满足"完全独立、面向客户、
离线、Podman+Docker 双兼容"契约：
  - 零仓库知识：无 extends、无 ../ 路径、release/ 内零 Python；
  - 离线：pull_policy never，镜像无 registry 前缀；
  - 凭证最小注入：容器 environment 仅四变量（不使用 env_file）；
  - SSH host key 持久化；
  - 双端控制脚本命令同构，凭证生成加密学安全、字符集仅字母数字；
  - 厂商打包器 relpack 的纯函数（版本解析 / WSL 路径转换）正确。
"""

from pathlib import Path

import pytest
import yaml

from jpman_client import relpack

CLIENT_ROOT = Path(__file__).resolve().parents[1]
RELEASE = CLIENT_ROOT / "overlays" / "xmnn-runtime" / "release"

TRACKED = [
    "README.md", "compose.yaml", "compose.podman.yaml", ".env.example",
    "xmnnctl", "xmnnctl.ps1", "artifacts/.gitignore", "workspace/.gitkeep",
]


@pytest.fixture(scope="module")
def main_compose() -> dict:
    with (RELEASE / "compose.yaml").open(encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.mark.parametrize("rel", TRACKED)
def test_tracked_skeleton_present(rel):
    assert (RELEASE / rel).is_file(), rel


def test_release_has_no_python_files():
    pys = [p for p in RELEASE.rglob("*.py")]
    assert pys == [], f"客户目录不应包含 Python 文件：{pys}"


def test_no_repo_knowledge_in_compose(main_compose):
    text = (RELEASE / "compose.yaml").read_text(encoding="utf-8")
    # 无 YAML extends 键（结构级断言，不靠注释文本）；无父目录相对路径
    assert "extends" not in main_compose["services"]["xmnnrt"]
    assert "../" not in text


def test_main_compose_contract(main_compose):
    assert main_compose["name"] == "xmnn-runtime"
    svc = main_compose["services"]["xmnnrt"]
    # 无 registry 前缀 + 版本插值；离线禁止拉取
    assert svc["image"] == "xmnn-runtime:${XMNN_VERSION}"
    assert svc["pull_policy"] == "never"
    assert svc["network_mode"] == "bridge"
    assert svc["ports"] == [
        "${XMNN_SSH_PORT:-2225}:22",
        "${XMNN_JUPYTER_PORT:-8893}:8888",
    ]
    # 仅凭证四变量注入容器（无 env_file）
    assert "env_file" not in svc
    assert set(svc["environment"]) == {
        "USER_PASSWORD", "JUPYTER_TOKEN", "SSH_PUBLIC_KEY", "GRANT_SUDO",
    }
    # workspace bind + SSH host key named volume
    targets = [v.split(":")[1] for v in svc["volumes"]]
    assert targets == ["/workspace", "/var/lib/jpman/ssh-host-keys"]
    assert svc["restart"] == "unless-stopped"
    assert main_compose["volumes"] == {"xmnn-ssh-host-keys": {}}


def test_podman_override_rootless_essentials():
    doc = yaml.safe_load((RELEASE / "compose.podman.yaml").read_text(encoding="utf-8"))
    svc = doc["services"]["xmnnrt"]
    assert svc["devices"] == ["/dev/fuse:/dev/fuse"]
    assert svc["security_opt"] == ["label=disable"]
    assert svc["cgroupns"] == "host"
    assert "privileged" not in svc


def test_env_template_lf_only():
    data = (RELEASE / ".env.example").read_bytes()
    assert b"\r" not in data, ".env.example 必须 LF 换行（CRLF 会污染 bash/compose）"


def test_env_example_keys():
    keys = set()
    for line in (RELEASE / ".env.example").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#") and "=" in line:
            keys.add(line.split("=", 1)[0])
    assert keys == {
        "XMNN_VERSION", "XMNN_CONTAINER_NAME", "XMNN_SSH_PORT",
        "XMNN_JUPYTER_PORT", "USER_PASSWORD", "JUPYTER_TOKEN",
        "SSH_PUBLIC_KEY", "GRANT_SUDO",
    }


@pytest.mark.parametrize("script", ["xmnnctl", "xmnnctl.ps1"])
def test_ctl_scripts_command_parity_and_security(script):
    text = (RELEASE / script).read_text(encoding="utf-8")
    for cmd in ("init", "load", "up", "down", "ps", "logs", "smoke"):
        assert cmd in text, (script, cmd)
    # smoke 一次性容器必须显式 --entrypoint（否则默认 entrypoint 命令模式失败）
    assert "--entrypoint /opt/conda/bin/python" in text
    # 凭证字符集仅字母数字（bash 区间 / pwsh 显式字符集）
    if script == "xmnnctl":
        assert "A-Za-z0-9" in text
    else:
        assert "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789" in text


def test_scripts_defend_against_crlf_env():
    bash = (RELEASE / "xmnnctl").read_text(encoding="utf-8")
    pwsh = (RELEASE / "xmnnctl.ps1").read_text(encoding="utf-8")
    # bash 读 .env 去 CR；pwsh 写 .env 强制 LF（WriteAllText + LF join）
    assert "tr -d '\\r'" in bash
    assert 'TrimEnd("`r")' in pwsh
    assert 'WriteAllText' in pwsh and '"`n"' in pwsh


def test_release_shebang_scripts_are_lf_only():
    # shebang 在解释器启动前由内核按字节解析（'bash\r' 无法启动），
    # 脚本内 tr -d '\r' 救不了自己的 shebang——随包 POSIX 脚本必须全 LF。
    assert relpack.find_crlf_shebang_scripts(RELEASE) == []


def test_find_crlf_shebang_scripts_detects_bad_and_skips(tmp_path):
    (tmp_path / "ctl").write_bytes(b"#!/usr/bin/env bash\r\necho hi\r\n")
    (tmp_path / "ok.sh").write_bytes(b"#!/bin/sh\ntrue\n")
    # .ps1 首行虽有 shebang，但规范行尾就是 CRLF，必须跳过
    (tmp_path / "ctl.ps1").write_bytes(
        b"#!/usr/bin/env pwsh\r\nWrite-Host 1\r\n"
    )
    # artifacts/ 内为镜像归档（大二进制），即使字节偶然命中也不扫描
    art = tmp_path / "artifacts"
    art.mkdir()
    (art / "image.tar.gz").write_bytes(b"#!/bin/sh\r\njunk\r\n")

    bad = relpack.find_crlf_shebang_scripts(tmp_path)

    assert [p.name for p in bad] == ["ctl"]


def test_post_load_inspect_is_runtime_aware():
    # podman load 裸名归一化 localhost/：inspect 引用必须按运行时分流
    bash = (RELEASE / "xmnnctl").read_text(encoding="utf-8")
    pwsh = (RELEASE / "xmnnctl.ps1").read_text(encoding="utf-8")
    assert 'img_ref="localhost/$img_ref"' in bash
    assert '$imgRef = "localhost/$imgRef"' in pwsh


def test_bash_uses_urandom_pwsh_uses_crypto_rng():
    bash = (RELEASE / "xmnnctl").read_text(encoding="utf-8")
    pwsh = (RELEASE / "xmnnctl.ps1").read_text(encoding="utf-8")
    assert "/dev/urandom" in bash
    assert "RandomNumberGenerator" in pwsh
    assert "Get-Random" not in pwsh


def test_artifacts_gitignore_keeps_itself():
    text = (RELEASE / "artifacts" / ".gitignore").read_text(encoding="utf-8")
    assert "*" in text and "!.gitignore" in text


# ── relpack 纯函数 ──────────────────────────────────────────────────────────


def test_resolve_wheel_from_fake_dir(tmp_path):
    whl = tmp_path / "xmnn-9.9.9-cp314-cp314-linux_x86_64.whl"
    whl.write_bytes(b"x")
    info = relpack.resolve_wheel(tmp_path)
    assert info.version == "9.9.9"
    assert info.file == whl.name
    assert info.size_bytes == 1


def test_resolve_wheel_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        relpack.resolve_wheel(tmp_path)


def test_to_wsl_path():
    assert relpack.to_wsl_path(Path("D:/a/b")) == "/mnt/d/a/b"
