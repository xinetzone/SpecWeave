"""release/ 客户交付骨架的 daemon-free 结构守卫。

验证随包骨架（compose / 控制脚本 / env 模板）满足"完全独立、面向客户、离线、
Podman+Docker 双兼容"契约：
  - 零仓库知识：无 extends / 无 build / 无 ../ 路径、release/ 内零 Python；
  - 离线：pull_policy never，镜像固定 localhost/ 前缀（归档内规范名，双运行时一致）；
  - 凭证最小注入：容器 environment 仅四变量（不使用 env_file）；
  - SSH host key 持久化；
  - 双端控制脚本命令同构，凭证生成加密学安全、字符集仅字母数字；
  - 骨架内 shebang 脚本全 LF（内核先按字节解析 shebang，`bash\\r` 无法启动）。

底座/载荷分离（2026-09-21）后的追加守卫：载荷暂存区由 `products/<产品>/wheels/`
迁至 `release/payload/`（其内 `Dockerfile` 负责客户机派生装入、构建期跑 root +
devuser 双身份载荷守卫与 `pip check`，且不得覆盖底座 `ENTRYPOINT`/`CMD`）；
`release.json` 升 schema v2（`payload` 与 `archive` 两块**都含 `sha256`**），两端
控制脚本一律按块定向取值，旧「全局第一个 sha256」与旧兜底 glob 不得回归。

迁移自 `apps/containers/client/tests/test_release_bundle.py`（该文件随 Task 6 删除），
三类处置逐条对照：
  - **保留**：骨架跟踪文件清单、compose 主契约与零仓库知识、podman override 三必需、
    env 模板 LF 与键集合、双端命令同构与凭证字符集/随机源、CRLF shebang 守卫、
    `localhost/` 规范名引用计数与「禁止按运行时前缀分流」、端口预检静态序。
  - **替换**：原依赖 `jpman_client.relpack` 纯函数的用例（`resolve_wheel` /
    `to_wsl_path` / `find_crlf_shebang_scripts`）→ 等价静态断言，见
    `test_wheel_version_parse_rule_*`、`test_wheel_staging_*`、
    `test_win_to_wsl_path_rule_parity`、`test_release_shebang_scripts_are_lf_only`。
  - **删除**：以 `bash <harness>`（`sed '$d'` 剥入口 + source）驱动客户脚本的行为用例
    （参数矩阵 / 端口预检 / 用户级 compose 回退）——同等判据已由静态断言覆盖
    （`test_runtime_choice_fail_fast_messages`、
    `test_compose_preflight_user_dir_fallback_parity`、
    `test_up_preflights_host_ports_before_compose`）；理由见各用例 docstring。
    pwsh 侧行为用例无需 bash，仍按原样移植。
"""

import re
import shutil
import socket
import subprocess
from pathlib import Path

import pytest

TRACKED = [
    "README.md", "compose.yaml", "compose.podman.yaml", ".env.example",
    "xmnnctl", "xmnnctl.ps1", "artifacts/.gitignore", "workspace/.gitkeep",
    # 底座/载荷分离（2026-09-21）：载荷 whl 随交付包放在 payload/，由其内
    # Dockerfile 在客户机派生装入底座；.keep 保留空目录、.gitignore 忽略 whl。
    "payload/Dockerfile", "payload/.gitignore", "payload/.keep",
]


# ── 极简 YAML 文本解析（避免引入 PyYAML 依赖）───────────────────────────────
#
# 骨架 compose 结构固定且只有两级映射 + 序列，用缩进扫描即可拿到等价结构，
# 无需把 YAML 解析器变成测试依赖。

_MAPPING = re.compile(r"^(\s*)([^\s#][^:]*):\s*(.*)$")


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _significant(line: str) -> bool:
    stripped = line.strip()
    return bool(stripped) and not stripped.startswith("#")


def _find(lines: list, key: str, indent: int = 0) -> int:
    """定位缩进恰为 indent 的 `key:` 行，返回行号。"""
    for i, line in enumerate(lines):
        if not _significant(line) or _indent(line) != indent:
            continue
        m = _MAPPING.match(line)
        if m and m.group(2) == key:
            return i
    raise AssertionError(f"未找到键 {key!r}（缩进 {indent}）")


def _block(lines: list, idx: int) -> list:
    """返回 idx 行的子块（缩进严格更深），遇缩进不深于 idx 的有效行即止。"""
    header_indent = _indent(lines[idx])
    out = []
    for line in lines[idx + 1:]:
        if _significant(line) and _indent(line) <= header_indent:
            break
        out.append(line)
    return out


def _map(block: list) -> dict:
    """块内**直接**子键 → {key: 标量值}（空串表示其下还有子块/序列）。"""
    entries = []
    for line in block:
        if not _significant(line):
            continue
        m = _MAPPING.match(line)
        if m:
            entries.append((len(m.group(1)), m.group(2), m.group(3).strip().strip("\"'")))
    if not entries:
        return {}
    base = min(i for i, _, _ in entries)
    return {k: v for i, k, v in entries if i == base}


def _seq(block: list) -> list:
    """块内**直接**序列项（`- 值`）→ [值]（去掉两端引号）。"""
    items = []
    for line in block:
        if not _significant(line):
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append((_indent(line), stripped[2:].strip().strip("\"'")))
    if not items:
        return []
    base = min(i for i, _ in items)
    return [v for i, v in items if i == base]


def _load(path: Path) -> list:
    """读文件（UTF-8）并返回按行切分结果。"""
    return path.read_text(encoding="utf-8").splitlines()


# ── 骨架文件清单与零 Python 契约 ────────────────────────────────────────────


@pytest.mark.parametrize("rel", TRACKED)
def test_tracked_skeleton_present(release_dir, rel):
    assert (release_dir / rel).is_file(), rel


def test_release_has_no_python_files(release_dir):
    # workspace/ 是客户运行时可写的用户数据区（交付时仅含 .gitkeep，客户的
    # notebook/模型脚本会在使用中落入），artifacts/ 是镜像归档；两者都不属于
    # "零 Python 控制面"契约的扫描范围。
    pys = [
        p for p in release_dir.rglob("*.py")
        if p.relative_to(release_dir).parts[0] not in ("artifacts", "workspace")
    ]
    assert pys == [], f"客户目录不应包含 Python 文件：{pys}"


def test_payload_dir_replaces_wheels_dir(product_dir, release_dir):
    """载荷暂存区迁移：`products/<产品>/wheels/` 删除 → `release/payload/` 新增。

    重构前 CLI 把产品 wheel 暂存到产品目录下的 `wheels/` 并让底座构建上下文
    消费它；重构后底座镜像**不含载荷**，载荷改为随交付包放在 `release/payload/`，
    由客户机 `xmnnctl load` 经派生构建装入。
    """
    assert not (product_dir / "wheels").exists(), "wheels/ 已随底座/载荷分离删除"
    payload = release_dir / "payload"
    assert payload.is_dir()
    gi = (payload / ".gitignore").read_text(encoding="utf-8")
    assert "*.whl" in gi and "!.gitignore" in gi
    assert (payload / ".keep").is_file()


# ── payload/Dockerfile：客户机派生构建契约 ──────────────────────────────────
#
# 底座镜像 `localhost/xmnn-runtime:base-<形态>` 只含依赖面 + torch + 守卫脚本，
# 载荷（xmnn wheel）由 `xmnnctl load` 以本文件为入口在客户机派生装入，产出
# `localhost/xmnn-runtime:<交付版本>`（与 compose 的 ${XMNN_VERSION} 逐字一致）。


def test_payload_dockerfile_derivation_contract(release_dir):
    text = (release_dir / "payload" / "Dockerfile").read_text(encoding="utf-8")
    assert "FROM ${BASE_IMAGE}" in text, "派生镜像必须基于随交付包下发的底座 ref"
    assert "COPY xmnn-*.whl /tmp/payload/" in text
    # ① 完全离线：禁网 + 跳过依赖解析（依赖面已由底座铺满，缺失即底座漏项）
    assert "--no-index" in text and "--no-deps" in text
    # ② 载荷守卫 root + devuser 双身份各跑一次（任一失败即构建失败）
    assert "/opt/xmnnrt-smoke/_runtime_smoke.py" in text
    assert text.count("_runtime_smoke.py") == 2, "守卫须 root 与 devuser 各跑一次"
    assert "su -s /bin/bash devuser" in text
    # ③ 依赖区间校验：pip check 全量打印，仅 xmnn 相关冲突判交付失败
    assert "-m pip check" in text
    assert 'grep -Eq "^xmnn[[:space:]]"' in text
    # ④ LABEL 载荷版本（派生镜像可溯源）
    assert 'org.specweave.payload-version="${PAYLOAD_VERSION}"' in text


def test_payload_dockerfile_keeps_base_entrypoint(release_dir):
    """派生只是「加一层载荷」：不得出现 ENTRYPOINT/CMD 指令行（服务契约沿用底座）。"""
    text = (release_dir / "payload" / "Dockerfile").read_text(encoding="utf-8")
    assert not re.search(r"(?m)^\s*(ENTRYPOINT|CMD)\s", text), \
        "派生构建不得覆盖 ENTRYPOINT/CMD（tini -> entrypoint.sh -> supervisord）"


# ── xmnnctl / xmnnctl.ps1：schema v2 清单按块取值 + 底座导入 + 载荷派生 ──────
#
# ⚠️ schema v2 的 `payload` 与 `archive` 两块**都含 `"sha256"`**：抓「全局第一个
# sha256」的旧写法会把载荷摘要当成 1.1 GB 底座归档的摘要去校验，必然误报
# 「完整性校验失败」。故两端一律按块定向取值，且旧兜底 glob 不得回归。


def test_ctl_manifest_read_is_block_scoped(release_dir):
    bash = (release_dir / "xmnnctl").read_text(encoding="utf-8")
    pwsh = (release_dir / "xmnnctl.ps1").read_text(encoding="utf-8")
    # bash：awk 按块定向取值；顶层字段复用同一 helper（不另立抓取逻辑）
    assert "manifest_block_field() {" in bash
    assert 'manifest_version_field() { manifest_block_field "-" version; }' in bash
    for call in ('manifest_block_field payload sha256', 'manifest_block_field archive sha256',
                 'manifest_block_field image id', 'manifest_block_field "-" schema_version'):
        assert call in bash, call
    # pwsh：结构化 JSON 解析（ConvertFrom-Json）+ 同名块键
    assert "ConvertFrom-Json" in pwsh
    assert 'Get-ManifestVersion { return (Get-ManifestField "" "version") }' in pwsh
    for call in ('Get-ManifestField "payload" "sha256"', 'Get-ManifestField "archive" "sha256"',
                 'Get-ManifestField "image" "id"', 'Get-ManifestField "" "schema_version"'):
        assert call in pwsh, call


@pytest.mark.parametrize("script", ["xmnnctl", "xmnnctl.ps1"])
def test_ctl_scripts_have_no_legacy_archive_lookup(release_dir, script):
    """旧「全局第一个 sha256」与旧兜底 glob 已废除，不得回归。"""
    text = (release_dir / script).read_text(encoding="utf-8")
    assert """grep -o '"sha256"'""" not in text, "全局第一个 sha256 写法已废除"
    assert "xmnn-runtime-*.tar.gz" not in text, "旧兜底 glob 已废除（归档按清单文件名取）"
    assert "xmnn-runtime-$ver.tar.gz" not in text, "旧按交付版本猜归档名已废除"


def test_ctl_load_imports_base_and_derives_payload(release_dir):
    bash = (release_dir / "xmnnctl").read_text(encoding="utf-8")
    # 清单必须成套：缺 release.json 即 fail-fast
    assert "交付包不完整：缺 artifacts/release.json" in bash
    # 版本自检：.env 的 XMNN_VERSION 必须与清单 version 一致
    assert "版本不一致：.env 的 XMNN_VERSION=" in bash
    # 底座导入幂等：先比镜像 Id，命中即跳过 1.1 GB 归档导入
    assert "image_id_matches() {" in bash
    assert 'if image_id_matches "$base_ref" "$base_id"; then' in bash
    # 底座归档与载荷 wheel 各按**自己那块**的 sha256 校验
    assert 'verify_sha256 "artifacts/$archive_file" "$archive_sha" "底座归档"' in bash
    assert 'verify_sha256 "payload/$payload_file" "$payload_sha" "载荷 wheel"' in bash
    # 派生构建：上下文 payload/、-f payload/Dockerfile、底座与版本经 --build-arg 下发
    assert '"$RT" build -f payload/Dockerfile' in bash
    assert '--build-arg "BASE_IMAGE=$base_ref"' in bash
    assert '--build-arg "PAYLOAD_VERSION=$ver"' in bash
    assert '-t "$img_ref" payload' in bash
    assert 'img_ref="localhost/xmnn-runtime:$ver"' in bash


def test_ctl_scripts_load_branch_parity(release_dir):
    """两端关键分支对等（命名风格各异，语义同一组）。"""
    bash = (release_dir / "xmnnctl").read_text(encoding="utf-8")
    pwsh = (release_dir / "xmnnctl.ps1").read_text(encoding="utf-8")
    assert "manifest_block_field" in bash and "Get-ManifestField" in pwsh
    assert "verify_sha256" in bash and "Verify-Sha256" in pwsh
    assert "image_id_matches" in bash and "Test-ImageIdMatches" in pwsh
    for text in (bash, pwsh):
        assert "版本不一致：.env 的 XMNN_VERSION=" in text
        assert "payload/Dockerfile" in text
        assert "artifacts/release.json" in text
        assert "BASE_IMAGE=" in text and "PAYLOAD_VERSION=" in text
        assert "payload/" in text


# ── compose.yaml：零仓库知识 + 主契约 ───────────────────────────────────────


def test_no_repo_knowledge_in_compose(release_dir):
    text = (release_dir / "compose.yaml").read_text(encoding="utf-8")
    lines = _load(release_dir / "compose.yaml")
    svc = _map(_block(lines, _find(lines, "xmnnrt", 2)))
    # 无 YAML extends 键（结构级断言，不靠注释文本）；无父目录相对路径；无 build
    assert "extends" not in svc
    assert "../" not in text
    assert not re.search(r"(?m)^\s*(extends|build)\s*:", text), \
        "交付骨架不得 extends / build（镜像一律来自本地归档）"


def test_main_compose_contract(release_dir):
    lines = _load(release_dir / "compose.yaml")
    assert _map(lines)["name"] == "xmnn-runtime"
    svc = _map(_block(lines, _find(lines, "xmnnrt", 2)))
    # localhost/ 规范名：podman 打包时裸名归一化进入归档，docker load 原样保留；
    # 裸名在 docker 下会被解析为 docker.io/xmnn-runtime 触发远程拉取。离线禁止拉取。
    assert svc["image"] == "localhost/xmnn-runtime:${XMNN_VERSION}"
    assert svc["pull_policy"] == "never"
    assert svc["network_mode"] == "bridge"
    assert _seq(_block(lines, _find(lines, "ports", 4))) == [
        "${XMNN_SSH_PORT:-2225}:22",
        "${XMNN_JUPYTER_PORT:-8893}:8888",
    ]
    # 仅凭证四变量注入容器（无 env_file）
    assert "env_file" not in svc
    assert set(_map(_block(lines, _find(lines, "environment", 4)))) == {
        "USER_PASSWORD", "JUPYTER_TOKEN", "SSH_PUBLIC_KEY", "GRANT_SUDO",
    }
    # workspace bind + SSH host key named volume
    targets = [v.split(":")[1] for v in _seq(_block(lines, _find(lines, "volumes", 4)))]
    assert targets == ["/workspace", "/var/lib/jpman/ssh-host-keys"]
    assert svc["restart"] == "unless-stopped"
    named = _map(_block(lines, _find(lines, "volumes", 0)))
    assert set(named) == {"xmnn-ssh-host-keys"}
    assert named["xmnn-ssh-host-keys"] == "{}"


def test_podman_override_rootless_essentials(release_dir):
    text = (release_dir / "compose.podman.yaml").read_text(encoding="utf-8")
    lines = _load(release_dir / "compose.podman.yaml")
    svc = _map(_block(lines, _find(lines, "xmnnrt", 2)))
    assert _seq(_block(lines, _find(lines, "devices", 4))) == ["/dev/fuse:/dev/fuse"]
    assert _seq(_block(lines, _find(lines, "security_opt", 4))) == ["label=disable"]
    assert svc["cgroupns"] == "host"
    assert "privileged" not in svc
    # 「严禁 privileged」在文件注释里出现，故按 YAML 键判据而非子串判据
    assert not re.search(r"(?m)^\s*privileged\s*:", text)


# ── .env.example 与 artifacts/.gitignore ────────────────────────────────────


def test_env_template_lf_only(release_dir):
    data = (release_dir / ".env.example").read_bytes()
    assert b"\r" not in data, ".env.example 必须 LF 换行（CRLF 会污染 bash/compose）"


def test_env_example_keys(release_dir):
    keys = set()
    for line in (release_dir / ".env.example").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#") and "=" in line:
            keys.add(line.split("=", 1)[0])
    assert keys == {
        "XMNN_VERSION", "XMNN_CONTAINER_NAME", "XMNN_SSH_PORT",
        "XMNN_JUPYTER_PORT", "USER_PASSWORD", "JUPYTER_TOKEN",
        "SSH_PUBLIC_KEY", "GRANT_SUDO",
    }


def test_artifacts_gitignore_keeps_itself(release_dir):
    text = (release_dir / "artifacts" / ".gitignore").read_text(encoding="utf-8")
    assert "*" in text and "!.gitignore" in text


# ── 双端控制脚本：命令同构 / 凭证字符集 / CRLF 免疫 ─────────────────────────


@pytest.mark.parametrize("script", ["xmnnctl", "xmnnctl.ps1"])
def test_ctl_scripts_command_parity_and_security(release_dir, script):
    text = (release_dir / script).read_text(encoding="utf-8")
    for cmd in ("init", "load", "up", "down", "ps", "logs", "smoke"):
        assert cmd in text, (script, cmd)
    # smoke 一次性容器必须显式 --entrypoint（否则默认 entrypoint 命令模式失败）
    assert "--entrypoint /opt/conda/bin/python" in text
    # 凭证字符集仅字母数字（bash 区间 / pwsh 显式字符集）
    if script == "xmnnctl":
        assert "A-Za-z0-9" in text
    else:
        assert "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789" in text


def test_ctl_command_surface_parity(release_dir):
    """两端子命令集合同构（bash `case` 分发 ↔ pwsh `switch` 分发）。"""
    bash = (release_dir / "xmnnctl").read_text(encoding="utf-8")
    pwsh = (release_dir / "xmnnctl.ps1").read_text(encoding="utf-8")
    bash_body = bash.split('case "$cmd" in', 1)[1].split("esac", 1)[0]
    bash_cmds = set(re.findall(r"(?m)^\s*([a-z]+)\)", bash_body))
    pwsh_body = pwsh.split("# ── 入口分发", 1)[1]
    pwsh_cmds = set(re.findall(r'(?m)^\s*"([a-z]+)"\s*\{', pwsh_body))
    expected = {"init", "load", "up", "down", "ps", "logs", "smoke", "version"}
    assert bash_cmds == expected, bash_cmds
    assert pwsh_cmds == expected, pwsh_cmds


def test_scripts_defend_against_crlf_env(release_dir):
    bash = (release_dir / "xmnnctl").read_text(encoding="utf-8")
    pwsh = (release_dir / "xmnnctl.ps1").read_text(encoding="utf-8")
    # bash 读 .env 去 CR；pwsh 写 .env 强制 LF（WriteAllText + LF join）
    assert "tr -d '\\r'" in bash
    assert 'TrimEnd("`r")' in pwsh
    assert "WriteAllText" in pwsh and '"`n"' in pwsh


# 改名自 `relpack.find_crlf_shebang_scripts`（该纯函数随 client 删除）：等价实现
# 镜像 `bin/lib/pipeline.sh` 的 `guard_crlf_shebang` 判定（扫描面与排除项一致）。
_SHEBANG_SKIP_SUFFIXES = {".ps1", ".psm1", ".bat", ".cmd"}
_CRLF_SCAN_EXCLUDE = {"artifacts"}


def _find_crlf_shebang_scripts(root: Path) -> list:
    bad = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix.lower() in _SHEBANG_SKIP_SUFFIXES:
            continue
        rel = p.relative_to(root)
        if rel.parts[0] in _CRLF_SCAN_EXCLUDE:
            continue
        if p.read_bytes()[:2] != b"#!":
            continue
        if b"\r" in p.read_bytes():
            bad.append(p)
    return bad


def test_release_shebang_scripts_are_lf_only(release_dir):
    # shebang 在解释器启动前由内核按字节解析（'bash\r' 无法启动），
    # 脚本内 tr -d '\r' 救不了自己的 shebang——随包 POSIX 脚本必须全 LF。
    assert _find_crlf_shebang_scripts(release_dir) == []


def test_crlf_shebang_scanner_detects_bad_and_skips(tmp_path):
    """镜像实现的判据自检：坏文件必被识别，.ps1 与 artifacts/ 必被跳过。"""
    (tmp_path / "ctl").write_bytes(b"#!/usr/bin/env bash\r\necho hi\r\n")
    (tmp_path / "ok.sh").write_bytes(b"#!/bin/sh\ntrue\n")
    # .ps1 首行虽有 shebang，但规范行尾就是 CRLF，必须跳过
    (tmp_path / "ctl.ps1").write_bytes(b"#!/usr/bin/env pwsh\r\nWrite-Host 1\r\n")
    # artifacts/ 内为镜像归档（大二进制），即使字节偶然命中也不扫描
    art = tmp_path / "artifacts"
    art.mkdir()
    (art / "image.tar.gz").write_bytes(b"#!/bin/sh\r\njunk\r\n")

    assert [p.name for p in _find_crlf_shebang_scripts(tmp_path)] == ["ctl"]


# ── 运行时选择与守护可达性（静态）───────────────────────────────────────────


def test_loaded_image_uses_localhost_canonical_name(release_dir):
    # 归档由 podman save 产出：打包机 tag 时裸名已归一化，tar 内 RepoTag 固定
    # localhost/xmnn-runtime:<ver>；docker load 原样保留（podman 会在解析裸名时
    # 隐式补 localhost/，docker 不会）。双端脚本的 load 后 inspect 与一次性
    # smoke run 必须统一使用 localhost/ 全称，且不得再按运行时做条件前缀分流。
    bash = (release_dir / "xmnnctl").read_text(encoding="utf-8")
    pwsh = (release_dir / "xmnnctl.ps1").read_text(encoding="utf-8")
    canonical = "localhost/xmnn-runtime:$ver"
    # 每端恰好两处：load 后 inspect 引用 + smoke 一次性容器镜像引用
    assert bash.count(canonical) == 2
    assert pwsh.count(canonical) == 2
    assert f'img_ref="{canonical}"' in bash
    assert f'$imgRef = "{canonical}"' in pwsh
    # 禁止回退为按运行时条件加前缀的分流写法
    assert '[ "$RT" = "podman" ] && img_ref=' not in bash
    assert 'if ($Script:Rt -eq "podman") { $imgRef' not in pwsh


def test_bash_uses_urandom_pwsh_uses_crypto_rng(release_dir):
    bash = (release_dir / "xmnnctl").read_text(encoding="utf-8")
    pwsh = (release_dir / "xmnnctl.ps1").read_text(encoding="utf-8")
    assert "/dev/urandom" in bash
    assert "RandomNumberGenerator" in pwsh
    assert "Get-Random" not in pwsh


def test_compose_preflight_user_dir_fallback_parity(release_dir):
    # pipx/pip --user 安装的 compose 不在 PATH 时（WSL 非登录 shell / 最小化环境），
    # 两侧预检都必须回退用户级目录并给出可操作提示，而非直接判"缺少 compose"。
    bash = (release_dir / "xmnnctl").read_text(encoding="utf-8")
    pwsh = (release_dir / "xmnnctl.ps1").read_text(encoding="utf-8")
    assert "find_companion" in bash and "$HOME/.local/bin" in bash
    assert "Find-UserCompanion" in pwsh and ".local\\bin" in pwsh
    assert "pip install --user podman-compose" in bash
    assert "pip install --user podman-compose" in pwsh
    assert "export PATH=" in bash
    # 回退命中须显式告知用户（自动启用），失败信息须可操作（安装命令 + PATH 自救）
    assert "已自动启用" in bash and "已自动启用" in pwsh


@pytest.mark.parametrize("script", ["xmnnctl", "xmnnctl.ps1"])
def test_daemon_preflight_and_load_exit_guard(release_dir, script):
    # CLI 已安装 ≠ 守护可达：load/up/smoke 前必须预检；load 退出码必须检查，
    # 否则 daemon 中断会被误报为"镜像中没有/版本不符"（2026-09-17 实测踩坑）。
    text = (release_dir / script).read_text(encoding="utf-8")
    assert "podman machine start" in text
    assert "Docker Desktop" in text
    assert "镜像导入失败" in text
    name = "assert_runtime_alive" if script == "xmnnctl" else "Assert-RuntimeAlive"
    # 1 处定义 + load/up/smoke 三处调用
    assert text.count(name) >= 4


@pytest.mark.parametrize("script", ["xmnnctl", "xmnnctl.ps1"])
def test_runtime_selection_exposed_with_auto(release_dir, script):
    # 运行时必须可经命令行选择：podman|docker|auto 三值、默认 auto 探测，
    # 旧的"仅二值"错误文案不得残留（防止回退为 env-only 设计）。
    text = (release_dir / script).read_text(encoding="utf-8")
    assert "podman|docker|auto" in text
    assert "只允许 podman|docker（当前" not in text
    assert "auto" in text
    # 强制指定未安装的运行时时须 fail-fast，不得静默回退到另一个运行时
    assert "未安装或不在 PATH" in text
    if script == "xmnnctl":
        assert "parse_global_args" in text
        assert "--runtime" in text
        # 优先级链：CLI --runtime > 环境变量 XMNN_RUNTIME > auto
        assert '${CLI_RUNTIME:-${XMNN_RUNTIME:-auto}}' in text
    else:
        assert "Parse-GlobalArgs" in text
        assert "--runtime" in text and "$Script:CliRuntime" in text
        assert "$env:XMNN_RUNTIME" in text and '"auto"' in text


def test_runtime_choice_fail_fast_messages(release_dir):
    """取代原 `bash` 行为用例（`_BASH_PARSE_*` / `_BASH_RUNTIME_BAD_CHOICE`）：
    以静态断言锁定同批判据——非法值/缺值与两种"未找到运行时"分支的 fail-fast
    文案，以及参数扫描形态（`--runtime=`/`-rX`/`--` 分隔）。
    理由：本应用守卫测试须 daemon-free 且不依赖仓库内 POSIX bash（Windows 原生
    无 bash；经 wsl.exe 驱动 `sed '$d'` + 多行 harness 存在参数重组风险，原文件
    注释已实测踩坑），而上述判据可等价静态表达。
    """
    bash = (release_dir / "xmnnctl").read_text(encoding="utf-8")
    pwsh = (release_dir / "xmnnctl.ps1").read_text(encoding="utf-8")
    for text in (bash, pwsh):
        assert "只允许 podman|docker|auto" in text
        assert "未安装或不在 PATH" in text
        assert "未找到 podman 或 docker" in text
        assert "需要参数" in text
    # bash：优先级链 + 三种 token 形态 + `--` 之后原样下发
    assert 'choice="${CLI_RUNTIME:-${XMNN_RUNTIME:-auto}}"' in bash
    assert "--runtime=*)" in bash and "-r?*)" in bash and "--runtime|-r)" in bash
    assert 'shift; REMAIN+=("$@"); break' in bash
    # pwsh：同名形态（`-Runtime=` / `-rX` / `--`）+ 优先级链
    assert re.search(r"(?m)^\s*\'\^--\?runtime=\(\.\+\)\$\'", pwsh)
    assert re.search(r"(?m)^\s*\'\^-r\(\.\+\)\$\'", pwsh)
    assert '$env:XMNN_RUNTIME' in pwsh


# ── up 前宿主端口预检（跨 podman/docker 引擎冲突 fail-fast）─────────────────
#
# 背景：两引擎共享宿主网络命名空间却互不可见对方的端口占用；rootless 的转发
# 表现为宿主用户进程（rootlessport）。不预检时 compose up 在绑定阶段才报
# "bind: address already in use"，且不指认占用者。预检必须：
#   1) 直接探测宿主网络栈（不能只查当前引擎 ps）；
#   2) 本引擎同名容器自持有端口时豁免（幂等 up / 改配置重建）；
#   3) 被占时给出对侧 down 指引与"并存需端口+容器名+workspace 三隔离"指引。


@pytest.mark.parametrize("script", ["xmnnctl", "xmnnctl.ps1"])
def test_up_preflights_host_ports_before_compose(release_dir, script):
    text = (release_dir / script).read_text(encoding="utf-8")
    if script == "xmnnctl":
        body = text.split("do_up() {", 1)[1].split("\n}", 1)[0]
        assert body.index("preflight_ports") < body.index("compose up -d")
        assert "port_holder" in text and "self_publishes_port" in text
    else:
        body = text.split("function Do-Up {", 1)[1].split("\n}", 1)[0]
        assert body.index("Assert-HostPorts") < body.index('Invoke-Compose "up -d"')
        assert "Test-HostPortListening" in text and "Test-SelfPublishesPort" in text
    # 可操作指引三件套：对侧运行时 down、并存改容器名、workspace 不可共享
    assert "另一运行时" in text
    assert "XMNN_CONTAINER_NAME" in text
    assert "workspace" in text


# ── pwsh 侧参数解析与端口预检行为（daemon-free；无 pwsh 时跳过）──────────────
#
# 原 bash 行为用例的等价移植面：pwsh 无需仓库内 POSIX bash，直接以 pwsh 驱动。

_PWSH_PARSE_HARNESS = r"""
. "__LIB__"
function Check($cond, $msg) { if (-not $cond) { Write-Host "FAIL: $msg"; exit 1 } }
Parse-GlobalArgs @("--runtime", "docker", "up")
Check ($Script:CliRuntime -eq "docker") "a1"
Check (($Script:Remain -join ",") -eq "up") "a2"
Parse-GlobalArgs @("up", "-r", "podman")
Check ($Script:CliRuntime -eq "podman") "b1"
Check (($Script:Remain -join ",") -eq "up") "b2"
Parse-GlobalArgs @("init", "--force")
Check ($Script:CliRuntime -eq "") "c1"
Check (($Script:Remain -join "|") -eq "init|--force") "c2"
Parse-GlobalArgs @("-Runtime=auto", "-rdocker", "up")
Check ($Script:CliRuntime -eq "docker") "d1"
Check (($Script:Remain -join ",") -eq "up") "d2"
Parse-GlobalArgs @("--", "--runtime", "docker")
Check ($Script:CliRuntime -eq "") "e1"
Check (($Script:Remain -join "|") -eq "--runtime|docker") "e2"
Write-Host "PS_PARSE_OK"
"""

_PWSH_PARSE_MISSING_VALUE = r"""
. "__LIB__"
Parse-GlobalArgs @("up", "--runtime")
"""


def _run_pwsh_lib_harness(release_dir: Path, body: str, tmp_path: Path) -> subprocess.CompletedProcess:
    # 剥掉入口分发段后 dot-source：仅装载函数与 $Script: 状态，不触发命令分发。
    # `Set-Location -Path $PSScriptRoot` 在 dot-source 时把 cwd 切到脚本所在目录
    # （即 tmp_path），故宿主侧 .env 也写在 tmp_path。
    src = (release_dir / "xmnnctl.ps1").read_text(encoding="utf-8")
    head = src.split("# ── 入口分发", 1)[0]
    lib = tmp_path / "xmnnctl-lib.ps1"
    lib.write_text(head, encoding="utf-8", newline="\n")
    harness = tmp_path / "harness.ps1"
    harness.write_text(body.replace("__LIB__", str(lib)), encoding="utf-8", newline="\n")
    proc = subprocess.run(
        ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(harness)],
        capture_output=True, timeout=120,
    )
    proc.stdout = proc.stdout.decode("utf-8", errors="replace")
    proc.stderr = proc.stderr.decode("utf-8", errors="replace")
    return proc


_no_pwsh = pytest.mark.skipif(shutil.which("pwsh") is None, reason="环境无 pwsh，跳过 ps1 参数解析行为测试")


@_no_pwsh
def test_pwsh_parse_global_args_matrix(release_dir, tmp_path):
    proc = _run_pwsh_lib_harness(release_dir, _PWSH_PARSE_HARNESS, tmp_path)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "PS_PARSE_OK" in proc.stdout, proc.stdout + proc.stderr


@_no_pwsh
def test_pwsh_runtime_flag_without_value_fails_fast(release_dir, tmp_path):
    proc = _run_pwsh_lib_harness(release_dir, _PWSH_PARSE_MISSING_VALUE, tmp_path)
    assert proc.returncode == 1
    assert "需要参数" in proc.stdout + proc.stderr


def _closed_local_port() -> int:
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.bind(("127.0.0.1", 0))
    port = probe.getsockname()[1]
    probe.close()
    return port


def _listening_local_port() -> tuple:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.listen(1)
    return sock, port


def _pwsh_port_harness(release_dir: Path, tmp_path: Path, ssh_port: str,
                       self_holds: bool, jupyter_port: str = "8893"):
    (tmp_path / ".env").write_text(
        f"XMNN_SSH_PORT={ssh_port}\nXMNN_JUPYTER_PORT={jupyter_port}\n"
        "XMNN_CONTAINER_NAME=xmnn-runtime\n",
        encoding="utf-8", newline="\n")
    override = "$true" if self_holds else "$false"
    body = f"""
. "__LIB__"
$Script:Rt = "docker"
function Test-SelfPublishesPort([string]$c, [int]$p) {{ {override} }}
Assert-HostPorts
Write-Host "PORT_PREFLIGHT_DONE"
"""
    return _run_pwsh_lib_harness(release_dir, body, tmp_path)


@_no_pwsh
def test_pwsh_port_preflight_free_passes(release_dir, tmp_path):
    # 关闭后的临时端口：本机连接立即被拒（避免依赖固定端口空闲）
    proc = _pwsh_port_harness(
        release_dir, tmp_path, str(_closed_local_port()), self_holds=False,
        jupyter_port=str(_closed_local_port()))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "PORT_PREFLIGHT_DONE" in proc.stdout


@_no_pwsh
def test_pwsh_port_preflight_foreign_holder_fails_fast(release_dir, tmp_path):
    sock, port = _listening_local_port()
    try:
        proc = _pwsh_port_harness(
            release_dir, tmp_path, str(port), self_holds=False,
            jupyter_port=str(_closed_local_port()))
    finally:
        sock.close()
    assert proc.returncode == 1
    merged = proc.stdout + proc.stderr
    assert f"宿主端口 {port} 已被占用" in merged
    assert "另一运行时（podman）" in merged
    assert "PORT_PREFLIGHT_DONE" not in merged


@_no_pwsh
def test_pwsh_port_preflight_self_holder_warns_and_passes(release_dir, tmp_path):
    sock, port = _listening_local_port()
    try:
        proc = _pwsh_port_harness(
            release_dir, tmp_path, str(port), self_holds=True,
            jupyter_port=str(_closed_local_port()))
    finally:
        sock.close()
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "原地更新" in proc.stdout
    assert "PORT_PREFLIGHT_DONE" in proc.stdout


# ── 原 relpack 纯函数用例的等价静态替代 ─────────────────────────────────────
#
# 原文件末尾三个用例（`test_resolve_wheel_from_fake_dir` /
# `test_resolve_wheel_missing_raises` / `test_to_wsl_path`）依赖
# `jpman_client.relpack`——该模块随 client 侧移除（Task 6）不复存在；其语义
# 现由 `bin/lib/pipeline.sh`（`wheel_version` / `stage_wheel`）与
# `bin/lib/common.sh`（`win_to_wsl_path`）/ `bin/relpack.ps1`（`ConvertTo-WslPath`）
# 承载，故改为「实现静态核对 + 规则镜像」的等价断言。


def _wheel_version(name: str, prefix: str) -> str:
    """与 `pipeline.sh::wheel_version` 同语义：去前缀 → 去 .whl → `-cp` 前截断。"""
    v = name.split("/")[-1]
    if v.startswith(prefix):
        v = v[len(prefix):]
    if v.endswith(".whl"):
        v = v[:-4]
    return v.split("-cp", 1)[0]


def test_wheel_version_parse_rule_matches_wheel_filename(app_root, product_env):
    pipeline = (app_root / "bin" / "lib" / "pipeline.sh").read_text(encoding="utf-8")
    prefix = product_env["WHEEL_PREFIX"]
    # 实现侧三步规则
    assert 'v="${v#"$WHEEL_PREFIX"}"' in pipeline       # 去产品前缀
    assert 'v="${v%.whl}"' in pipeline                  # 去扩展名
    assert "${v%%-cp*}" in pipeline                     # 在 -cp 之前截断
    # 规则镜像：与 pipeline.sh 同语义（原 resolve_wheel 的 version 判据）
    assert _wheel_version(f"{prefix}9.9.9-cp314-cp314-linux_x86_64.whl", prefix) == "9.9.9"
    assert _wheel_version(f"{prefix}1.2.1.dev0-cp314-cp314-linux_x86_64.whl", prefix) == "1.2.1.dev0"


def test_wheel_staging_rejects_missing_and_foreign_wheels(app_root, product_env):
    pipeline = (app_root / "bin" / "lib" / "pipeline.sh").read_text(encoding="utf-8")
    prefix = product_env["WHEEL_PREFIX"]
    glob = product_env["WHEEL_GLOB"]
    # 显式 --wheel 不存在 → fail-fast（原 resolve_wheel 的 FileNotFoundError 判据）
    assert 'die "--wheel 指定的文件不存在：$src"' in pipeline
    # 非本产品 wheel → fail-fast（按 WHEEL_PREFIX 校验文件名）
    assert '"$WHEEL_PREFIX"*.whl)' in pipeline
    # 暂存区与来源目录皆空 → fail-fast 并给出上游指引
    assert "未找到 $PRODUCT wheel" in pipeline
    # 暂存区只留一个 whl（COPY glob 才确定）：先清空旧 whl 再拷贝
    assert 'for old in "$WHEEL_STAGE"/$WHEEL_GLOB; do' in pipeline
    assert 'rm -f "$old"' in pipeline
    assert prefix and glob == f"{prefix}*.whl"


def test_win_to_wsl_path_rule_parity(app_root):
    # 原 `to_wsl_path(Path("D:/a/b")) == "/mnt/d/a/b"` 判据：Windows 盘符路径 →
    # WSL drvfs 形式。bash 与 pwsh 两侧各有一份实现，语义必须一致。
    common = (app_root / "bin" / "lib" / "common.sh").read_text(encoding="utf-8")
    ps1 = (app_root / "bin" / "relpack.ps1").read_text(encoding="utf-8")
    assert "win_to_wsl_path" in common
    assert r"[A-Za-z]:[\\/]*" in common            # 盘符路径识别
    assert "tr '[:upper:]' '[:lower:]'" in common  # 盘符转小写
    assert "/mnt/%s%s" in common                   # drvfs 挂载点形式
    assert "ConvertTo-WslPath" in ps1
    assert "^[A-Za-z]:" in ps1                     # 盘符路径识别
    assert '"/mnt/$drive"' in ps1                  # drvfs 挂载点形式
    # 已经是 POSIX 路径时原样返回（两侧同判定）
    assert "*) printf '%s' \"$p\" ;;" in common
    assert "return $full" in ps1