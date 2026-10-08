"""openKylin 开发脚手架：deb 打包骨架与 OKBS dput 上传配置生成。

设计依据（知识库）：
- F-015：系列代号 yangtze(1.0) / nile(2.0) / huanghe(3.0)，changelog 系列代号须与软件源代号一致。
- D-F-027：OKBS 编译平台，dput.cf 口径 fqdn=upload.build.openkylin.top:2121 / method=sftp / incoming=%(okbs)s。
"""

from pathlib import Path

SERIES_ALIASES: dict[str, str] = {
    "1.0": "yangtze",
    "yangtze": "yangtze",
    "2.0": "nile",
    "nile": "nile",
    "3.0": "huanghe",
    "huanghe": "huanghe",
}

OKBS_FQDN = "upload.build.openkylin.top:2121"

class ScaffoldError(Exception):
    """受控脚手架错误。"""

def scaffold_deb(project: str, series: str, version: str, target_dir: str | Path) -> list[Path]:
    """生成 debian/ 打包骨架，返回生成的文件清单。"""
    series_name = SERIES_ALIASES.get(series)
    if series_name is None:
        raise ScaffoldError(
            f"未知系列代号：{series}。可选：yangtze(1.0) / nile(2.0) / huanghe(3.0)"
        )
    if not project or not version:
        raise ScaffoldError("project 与 version 不能为空")

    root = Path(target_dir)
    debian = root / "debian"
    debian.mkdir(parents=True, exist_ok=True)

    control = debian / "control"
    control.write_text(
        f"Source: {project}\n"
        f"Section: utils\n"
        f"Priority: optional\n"
        f"Maintainer: Your Name <you@example.com>\n"
        f"Build-Depends: debhelper (>= 12), cmake\n"
        f"Standards-Version: 4.6.0\n"
        f"Homepage: https://gitee.com/openkylin/{project}\n\n"
        f"Package: {project}\n"
        f"Architecture: amd64\n"
        f"Depends: ${{shlibs:Depends}}, ${{misc:Depends}}\n"
        f"Description: {project} - openKylin package\n"
        f"  Short description here.\n"
        f"  Longer description follows after a leading space.\n",
        encoding="utf-8",
        newline="\n",
    )

    changelog = debian / "changelog"
    changelog.write_text(
        f"{project} ({version}) {series_name}; urgency=medium\n\n"
        f"  * Initial release.\n\n"
        f" -- Your Name <you@example.com>  {_changelog_date()}\n",
        encoding="utf-8",
        newline="\n",
    )

    rules = debian / "rules"
    rules.write_text(
        "#!/usr/bin/make -f\n"
        "%:\n"
        "\tdh $@\n",
        encoding="utf-8",
        newline="\n",
    )

    compat = debian / "compat"
    compat.write_text("12\n", encoding="utf-8", newline="\n")

    source_dir = debian / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    fmt = source_dir / "format"
    fmt.write_text("3.0 (quilt)\n", encoding="utf-8", newline="\n")

    return [control, changelog, rules, compat, fmt]

def _changelog_date() -> str:
    """RFC 2822 日期（Debian changelog 格式）。"""
    from email.utils import formatdate

    return formatdate(localtime=True)

DPUT_TEMPLATE = """# openKylin OKBS 上传配置（scaffold dput 生成）
# 用法：
#   1) 在 https://build.openkylin.top 注册 openKylin ID 并配置 SSH/PGP 公钥（先签 CLA：https://cla.openkylin.top）
#   2) 生成源码包后执行： dput okbs:~{login}/ppa <source.changes>
#   3) 到 https://archive.build.openkylin.top/dput-logs/ 查询构建结果
# 前置依赖：sftp 方式需安装 paramiko（pip install paramiko 或 apt install dput-ng）
[okbs]
fqdn = {fqdn}
method = sftp
incoming = %(okbs)s
login = {login}
"""

def scaffold_dput(openkylin_id: str, output: str | Path | None = None) -> tuple[str, Path | None]:
    """生成 OKBS dput.cf 配置片段；默认打印到 stdout，--output 时写文件。

    返回 (配置文本, 写入路径或 None)。
    """
    if not openkylin_id.strip():
        raise ScaffoldError("openkylin ID 不能为空")
    text = DPUT_TEMPLATE.format(fqdn=OKBS_FQDN, login=openkylin_id.strip())
    written: Path | None = None
    if output:
        out = Path(output).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8", newline="\n")
        written = out
    return text, written
