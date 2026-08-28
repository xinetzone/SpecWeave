"""Invoke 任务命名空间入口——组装 docs 和 gates 两个子模块。

CLI 用法：
    invoke build / invoke html / invoke clean / invoke linkcheck / invoke doctest
    invoke gates.utf8 / invoke gates.toctrees / invoke gates.frontmatter / invoke gates.all
"""
from __future__ import annotations

from invoke import Collection

from . import docs, gates

ns = Collection()

# 文档构建任务提升到根命名空间
ns.add_task(docs.help, default=True)
ns.add_task(docs.build)
ns.add_task(docs.html)
ns.add_task(docs.clean)
ns.add_task(docs.linkcheck)
ns.add_task(docs.doctest)

# 质量门任务作为子集合：invoke gates.utf8 等
ns.add_collection(Collection.from_module(gates))

ns.configure(
    {
        "sphinx": {
            "source": ".",
            "target": "_build/html",
            "target_file": "index.html",
        }
    }
)
