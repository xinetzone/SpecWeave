"""CI 质量门任务——封装 scripts/ 下的检查脚本为 invoke 任务。

用法::

    invoke gates.utf8          # UTF-8 有效性检查
    invoke gates.toctrees      # toctree 导航完整性检查
    invoke gates.frontmatter   # frontmatter 合规性检查
    invoke gates.all           # 运行全部质量门
"""
from pathlib import Path

from invoke import task

ROOT = Path(__file__).resolve().parent.parent  # tasks/gates.py → tasks/ → docs/
SCRIPTS = ROOT / "scripts"


@task
def utf8(c, self_test: bool = False):
    """检查 docs/ 下所有 Markdown 文件的 UTF-8 有效性。"""
    flag = " --self-test" if self_test else ""
    c.run(f"python {SCRIPTS / 'check-utf8.py'}{flag}")


@task
def toctrees(c, self_test: bool = False):
    """检查 docs/ 的 index.md/toctree 导航完整性。"""
    flag = " --self-test" if self_test else ""
    c.run(f"python {SCRIPTS / 'check-toctrees.py'}{flag}")


@task
def frontmatter(c, self_test: bool = False):
    """检查 docs/ 下 Markdown 文件的 frontmatter 合规性。"""
    flag = " --self-test" if self_test else ""
    c.run(f"python {SCRIPTS / 'check-frontmatter.py'}{flag}")


@task(default=True)
def all(c):
    """运行全部 CI 质量门（utf8 + toctrees + frontmatter）。"""
    c.run(f"python {SCRIPTS / 'check-utf8.py'}")
    c.run(f"python {SCRIPTS / 'check-toctrees.py'}")
    c.run(f"python {SCRIPTS / 'check-frontmatter.py'}")
