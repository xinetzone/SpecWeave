# SPDX-License-Identifier: GPL-2.0-only
"""无 Podman 静态校验 sticker-studio 编排（xuan-compose 库 API 演示）。

在 examples/ 目录下运行：

    python validate_compose.py

仅 import 与纯解析：不读 sys.argv 之外的输入、不起子进程、不调用 podman。
断言失败以退出码 1 结束，可直接放进 CI / 预提交检查。
"""

import sys

from xuan_compose.cli.parser import parse_args
from xuan_compose.engine import ComposeEngine
from xuan_compose.translate.mounts import parse_short_mount


def main() -> int:
    engine = ComposeEngine()  # 纯状态对象：零子进程
    args = parse_args(engine, ["-f", "compose.yaml", "config", "--quiet"])
    assert args.command == "config" and args.file == ["compose.yaml"]

    engine._parse_compose_file()  # 发现/插值/合并/规范化，全程不触达 podman

    errors: list[str] = []

    # 1) 三个服务齐备
    for name in ("generator", "gallery", "keychroma"):
        if name not in engine.all_services:
            errors.append(f"缺少服务 {name}")

    services = engine.services
    gen = services.get("generator", {})

    # 2) generator 必须有健康检查、文件 secret 与关键挂载
    if "healthcheck" not in gen:
        errors.append("generator 缺少 healthcheck（gallery 的 service_healthy 依赖会落空）")
    if "ark_key" not in (gen.get("secrets") or []):
        errors.append("generator 未引用 ark_key secret")
    mounts = " ".join(str(v) for v in gen.get("volumes", []))
    for required in ("/work/photos", "/work/out", "/work/prompts"):
        if required not in mounts:
            errors.append(f"generator 缺少挂载 {required}")

    # 3) gallery 必须在 web profile 下且健康依赖 generator
    gal = services.get("gallery", {})
    if "web" not in (gal.get("profiles") or []):
        errors.append("gallery 应置于 web profile")
    dep = (gal.get("depends_on") or {}).get("generator") or {}
    if dep.get("condition") != "service_healthy":
        errors.append("gallery 应 depends_on.generator.condition=service_healthy")

    # 4) 命名卷已在顶层声明（未声明时 xuan-compose 在运行期会 RuntimeError）
    if "gen-cache" not in getattr(engine, "vols", {}):
        errors.append("命名卷 gen-cache 未在顶层 volumes 声明")

    # 5) 密钥不得硬编码在 compose 正文里（粗检：合并结果不含 ARK_API_KEY= 字面量）
    if "ARK_API_KEY=" in engine.merged_yaml:
        errors.append("疑似把 ARK_API_KEY 字面量写进了 compose，请改用 secret 或 ${...:?}")

    # 6) 纯翻译函数可独立使用：验证一个短挂载被正确识别为 bind
    m = parse_short_mount("./out:/work/out", basedir=".")
    if m["type"] != "bind" or m["target"] != "/work/out":
        errors.append(f"短挂载解析异常: {m}")

    if errors:
        print("编排校验失败：")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"编排校验通过：项目={engine.project_name!r}，服务={sorted(engine.all_services)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
