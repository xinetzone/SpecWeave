import socket
import sys

# 无外网环境：让 intersphinx inventory 拉取快速失败（参考既有 dummy 构建经验）
_orig = socket.create_connection


def _boom(*a, **k):
    raise OSError("network disabled in dummy targeted build")


def main():
    socket.create_connection = _boom

    from sphinx.cmd.build import build_main

    srcdir = sys.argv[1]
    outdir = sys.argv[2]
    files = sys.argv[3:]
    args = ["-b", "dummy", "-E", srcdir, outdir] + files
    rc = build_main(args)
    print("sphinx dummy rc =", rc)
    sys.exit(rc)


if __name__ == "__main__":
    main()
