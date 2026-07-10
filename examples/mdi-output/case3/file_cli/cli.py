"""CLI module for 文件操作 CLI 工具."""

import sys
from typing import Optional

import click


@click.group()
@click.version_option()
def main():
    """一个轻量级的跨平台文件操作命令行工具，支持文件列出、复制、删除等常用文件管理功能。"""
    pass


@click.argument('path', type=click.STRING)
@click.option('--recursive', is_flag=True, help='是否递归列出子目录')
@click.option('--pattern', type=click.STRING, help='文件名通配符过滤模式（如 *.py）')
@click.option('--sort-by', type=click.STRING, default='name', help='排序方式：name/size/modified')
@click.option('--show-hidden', is_flag=True, help='是否显示隐藏文件')
@main.command()
def list(path: str, recursive: bool | None = False, pattern: str | None = None, sort_by: str | None = 'name', show_hidden: bool | None = False):
    """列出目录内容"""
    click.echo('TODO: Implement list')


@click.argument('source', type=click.STRING)
@click.argument('destination', type=click.STRING)
@click.option('--recursive', is_flag=True, help='是否递归复制目录')
@click.option('--force', is_flag=True, help='强制覆盖已存在的目标文件')
@click.option('--preserve-metadata', is_flag=True, default=True, help='保留文件元数据（时间戳、权限）')
@main.command()
def copy(source: str, destination: str, recursive: bool | None = False, force: bool | None = False, preserve_metadata: bool | None = True):
    """复制文件或目录"""
    click.echo('TODO: Implement copy')


@click.argument('target', type=click.STRING)
@click.option('--recursive', is_flag=True, help='是否递归删除非空目录')
@click.option('--force', is_flag=True, help='强制删除（不提示确认）')
@click.option('--dry-run', is_flag=True, help='预览模式，仅显示将被删除的文件')
@main.command()
def delete(target: str, recursive: bool | None = False, force: bool | None = False, dry_run: bool | None = False):
    """删除文件或目录"""
    click.echo('TODO: Implement delete')


if __name__ == "__main__":
    main()
