"""Sphinx 文档构建任务——自包含实现，不依赖 invocations。

提供 help(default)/build/html/clean/linkcheck/doctest 任务，
使用 sphinx-build -M make-mode 语义。
"""
import os
import shlex
import subprocess

from invoke import Exit, task


def _split_cli_args(value: str) -> list[str]:
    """Split a shell-style option string into argv tokens."""
    if not value.strip():
        return []
    return shlex.split(value, posix=os.name != "nt")


def _collect_sphinx_opts(opts: str = "") -> list[str]:
    """Preserve the established Sphinx option merge order."""
    args: list[str] = []
    for part in (os.environ.get("SPHINXOPTS", ""), os.environ.get("O", ""), opts):
        args.extend(_split_cli_args(part))
    return args


def _run_sphinx_make_mode(
    target: str,
    sourcedir: str,
    builddir: str,
    opts: str = "",
) -> None:
    sphinx_build = os.environ.get("SPHINXBUILD", "sphinx-build")
    command = [
        sphinx_build,
        "-M",
        target,
        sourcedir,
        builddir,
        *_collect_sphinx_opts(opts),
    ]

    try:
        completed = subprocess.run(command, check=False)
    except FileNotFoundError as exc:
        raise Exit(
            "The 'sphinx-build' command was not found. Set SPHINXBUILD to the "
            "full path of the executable or add it to PATH."
        ) from exc

    if completed.returncode != 0:
        raise Exit(code=completed.returncode)


@task(default=True)
def help(
    _ctx,
    sourcedir: str = ".",
    builddir: str = "_build",
    opts: str = "",
) -> None:
    """Show Sphinx make-mode help."""
    _run_sphinx_make_mode(
        target="help",
        sourcedir=sourcedir,
        builddir=builddir,
        opts=opts,
    )


@task
def build(
    _ctx,
    target: str = "html",
    sourcedir: str = ".",
    builddir: str = "_build",
    opts: str = "",
) -> None:
    """Build docs via ``sphinx-build -M`` (default target: html)."""
    _run_sphinx_make_mode(
        target=target,
        sourcedir=sourcedir,
        builddir=builddir,
        opts=opts,
    )


@task
def html(
    _ctx,
    sourcedir: str = ".",
    builddir: str = "_build",
    opts: str = "",
) -> None:
    """Build HTML documentation."""
    build(_ctx, target="html", sourcedir=sourcedir, builddir=builddir, opts=opts)


@task
def clean(
    _ctx,
    sourcedir: str = ".",
    builddir: str = "_build",
    opts: str = "",
) -> None:
    """Clean built documentation."""
    build(_ctx, target="clean", sourcedir=sourcedir, builddir=builddir, opts=opts)


@task
def linkcheck(
    _ctx,
    sourcedir: str = ".",
    builddir: str = "_build",
    opts: str = "",
) -> None:
    """Check all external links for integrity."""
    build(_ctx, target="linkcheck", sourcedir=sourcedir, builddir=builddir, opts=opts)


@task
def doctest(
    _ctx,
    sourcedir: str = ".",
    builddir: str = "_build",
    opts: str = "",
) -> None:
    """Run doctests in the documentation."""
    build(_ctx, target="doctest", sourcedir=sourcedir, builddir=builddir, opts=opts)
