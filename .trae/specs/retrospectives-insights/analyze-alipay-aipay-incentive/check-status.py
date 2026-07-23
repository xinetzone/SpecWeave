#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
支付宝AI支付激励计划 - 域名&ICP备案状态监控脚本

功能：
  1. 查询阿里云域名实名认证状态（通过阿里云OpenAPI）
  2. 查询ICP备案状态（通过工信部公开查询接口）
  3. 检查域名DNS解析和HTTPS可访问性
  4. 显示活动关键节点倒计时
  5. 彩色终端输出 + JSON状态输出

依赖安装：
  pip install alibabacloud-tea-openapi alibabacloud-domain20180129 alibabacloud-tea-util

使用方式：
  1. 复制 config.example.json 为 config.json，填入你的信息
  2. python check-status.py              # 单次检查
  3. python check-status.py --watch 300  # 每5分钟自动检查
  4. python check-status.py --json       # 输出JSON格式（便于脚本集成）
"""

import json
import sys
import os
import socket
import ssl
import time
import argparse
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path

try:
    from alibabacloud_tea_openapi import models as open_api_models
    from alibabacloud_domain20180129 import models as domain_models
    from alibabacloud_domain20180129.client import Client as DomainClient
    from alibabacloud_tea_util import models as util_models
    ALIYUN_SDK_AVAILABLE = True
except ImportError:
    ALIYUN_SDK_AVAILABLE = False

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config.json"

ACTIVITY_DEADLINE_ONLINE = datetime(2026, 8, 7, 23, 59, 59)
ACTIVITY_DEADLINE_USERS = datetime(2026, 8, 14, 23, 59, 59)
ACTIVITY_END = datetime(2026, 8, 21, 23, 59, 59)

BEIAN_KEYWORDS = ("ICP", "备案", "beian")

REALNAME_STATUS_MAP = {
    "NONAUDIT": ("未实名认证", "FAIL"),
    "SUCCEED": ("实名认证成功", "PASS"),
    "FAILED": ("实名认证失败", "FAIL"),
    "AUDITING": ("审核中", "WARN"),
}

DOMAIN_VERIFY_STATUS_MAP = {
    "NONAUDIT": ("命名审核未通过/未审核", "FAIL"),
    "SUCCEED": ("命名审核成功", "PASS"),
    "FAILED": ("命名审核失败", "FAIL"),
    "AUDITING": ("命名审核中", "WARN"),
}


class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"

    @staticmethod
    def supports_color():
        if os.name == "nt":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                return True
            except Exception:
                return False
        return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


USE_COLOR = Color.supports_color()


def cprint(text, color=None, bold=False, file=None):
    if file is None:
        file = sys.stdout
    if USE_COLOR and file is sys.stdout:
        prefix = ""
        if bold:
            prefix += Color.BOLD
        if color:
            prefix += color
        print(f"{prefix}{text}{Color.RESET}", file=file)
    else:
        print(text, file=file)


def status_icon(status):
    if not USE_COLOR:
        return {"PASS": "[PASS]", "FAIL": "[FAIL]", "WARN": "[WARN]", "INFO": "[INFO]"}.get(status, "[?]")
    return {
        "PASS": f"{Color.GREEN}✓{Color.RESET}",
        "FAIL": f"{Color.RED}✗{Color.RESET}",
        "WARN": f"{Color.YELLOW}⚠{Color.RESET}",
        "INFO": f"{Color.BLUE}ℹ{Color.RESET}",
    }.get(status, "?")


def load_config(json_mode=False):
    if not CONFIG_PATH.exists():
        warn_file = sys.stderr if json_mode else sys.stdout
        cprint(f"\n⚠ 配置文件不存在: {CONFIG_PATH}", Color.YELLOW, file=warn_file)
        cprint("  请先复制 config.example.json 为 config.json 并填入你的信息", Color.YELLOW, file=warn_file)
        cprint("  或使用 --domain 参数直接指定域名（部分功能将不可用）\n", Color.YELLOW, file=warn_file)
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def create_aliyun_client(access_key_id, access_key_secret):
    if not ALIYUN_SDK_AVAILABLE:
        return None
    config = open_api_models.Config(
        access_key_id=access_key_id,
        access_key_secret=access_key_secret,
    )
    config.endpoint = "domain.aliyuncs.com"
    return DomainClient(config)


def check_domain_realname(client, domain_name):
    result = {
        "check": "domain_realname",
        "domain": domain_name,
        "status": "UNKNOWN",
        "status_text": "未知",
        "details": {},
        "error": None,
    }

    if client is None:
        result["status"] = "SKIP"
        result["status_text"] = "SDK未安装，跳过"
        result["error"] = "alibabacloud SDK not installed"
        return result

    try:
        req = domain_models.QueryDomainByDomainNameRequest(
            domain_name=domain_name,
            lang="zh",
        )
        runtime = util_models.RuntimeOptions()
        resp = client.query_domain_by_domain_name_with_options(req, runtime)
        body = resp.body

        realname = body.real_name_status or "NONAUDIT"
        verify = body.domain_name_verification_status or "NONAUDIT"

        rn_text, rn_status = REALNAME_STATUS_MAP.get(realname, (f"未知状态({realname})", "WARN"))
        dy_text, dy_status = DOMAIN_VERIFY_STATUS_MAP.get(verify, (f"未知状态({verify})", "WARN"))

        result["details"] = {
            "real_name_status": realname,
            "real_name_text": rn_text,
            "domain_verification_status": verify,
            "domain_verification_text": dy_text,
            "registration_date": body.registration_date,
            "expiration_date": body.expiration_date,
            "registrant_type": "个人" if body.registrant_type == "1" else "企业" if body.registrant_type == "2" else "未知",
            "email_verified": bool(body.email_verification_status),
            "dns_servers": body.dns_list.dns if body.dns_list else [],
        }

        if rn_status == "PASS" and dy_status == "PASS":
            result["status"] = "PASS"
            result["status_text"] = rn_text
        elif rn_status == "FAIL" or dy_status == "FAIL":
            result["status"] = "FAIL"
            result["status_text"] = f"{rn_text} / {dy_text}"
        elif rn_status == "AUDITING" or dy_status == "AUDITING":
            result["status"] = "WARN"
            result["status_text"] = f"{rn_text} / {dy_text}"
        else:
            result["status"] = rn_status
            result["status_text"] = rn_text

    except Exception as e:
        result["status"] = "ERROR"
        result["status_text"] = f"查询失败: {e}"
        result["error"] = str(e)

    return result


def check_dns_resolution(domain_name):
    result = {
        "check": "dns_resolution",
        "domain": domain_name,
        "status": "UNKNOWN",
        "status_text": "",
        "ip": None,
        "error": None,
    }
    try:
        ip = socket.gethostbyname(domain_name)
        result["ip"] = ip
        result["status"] = "PASS"
        result["status_text"] = f"解析到 {ip}"
    except socket.gaierror as e:
        result["status"] = "FAIL"
        result["status_text"] = f"DNS解析失败"
        result["error"] = str(e)
    return result


def check_https(domain_name, timeout=10):
    result = {
        "check": "https",
        "domain": domain_name,
        "status": "UNKNOWN",
        "status_text": "",
        "status_code": None,
        "has_beian": False,
        "beian_found": False,
        "error": None,
    }
    try:
        ctx = ssl.create_default_context()
        url = f"https://{domain_name}"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        result["status_code"] = resp.getcode()
        result["status"] = "PASS"
        result["status_text"] = f"HTTPS正常 (HTTP {resp.getcode()})"

        body = resp.read(8192).decode("utf-8", errors="ignore")
        body_lower = body.lower()
        if any((kw.lower() in body_lower) for kw in BEIAN_KEYWORDS):
            result["has_beian"] = True
            result["beian_found"] = True
        resp.close()
    except urllib.error.HTTPError as e:
        result["status_code"] = e.code
        result["status"] = "WARN"
        result["status_text"] = f"HTTPS可访问但返回HTTP {e.code}"
    except Exception as e:
        result["status"] = "FAIL"
        result["status_text"] = f"HTTPS不可访问: {type(e).__name__}"
        result["error"] = str(e)
    return result


def check_icp_beian_miit(domain_name):
    result = {
        "check": "icp_beian",
        "domain": domain_name,
        "status": "UNKNOWN",
        "status_text": "",
        "beian_no": None,
        "company_name": None,
        "website_name": None,
        "error": None,
        "source": None,
    }

    try:
        url = f"https://api.vvhan.com/api/icp?url={urllib.parse.quote(domain_name)}"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode("utf-8"))
        resp.close()

        if data.get("success") and data.get("data"):
            info = data["data"]
            result["status"] = "PASS"
            result["beian_no"] = info.get("icp", "")
            result["company_name"] = info.get("name", "")
            result["website_name"] = info.get("title", "")
            result["status_text"] = f"已备案: {result['beian_no']}"
            result["source"] = "vvhan API"
        else:
            result["status"] = "FAIL"
            result["status_text"] = "未查询到ICP备案记录（可能尚未备案或审核中）"
            result["source"] = "vvhan API"
    except Exception as e:
        result["status"] = "WARN"
        result["status_text"] = f"第三方查询失败，请手动查询"
        result["error"] = str(e)

    return result


def check_icp_beian_manual(domain_name):
    return {
        "check": "icp_beian_manual",
        "domain": domain_name,
        "status": "INFO",
        "status_text": f"手动查询: https://beian.miit.gov.cn (输入域名'{domain_name}'查询)",
        "url": "https://beian.miit.gov.cn",
    }


def get_countdown(deadline):
    now = datetime.now()
    delta = deadline - now
    total_seconds = delta.total_seconds()
    if total_seconds <= 0:
        return 0, "已过期"
    days = delta.days
    hours = delta.seconds // 3600
    if days > 0:
        return days, f"还剩 {days} 天 {hours} 小时"
    elif hours > 0:
        return 0, f"还剩 {hours} 小时"
    else:
        minutes = delta.seconds // 60
        return 0, f"还剩 {minutes} 分钟"


def print_countdown():
    cprint("\n┌─────────────────────────────────────────────────────┐", Color.CYAN)
    cprint("│          📅 活动关键节点倒计时                       │", Color.CYAN)
    cprint("├─────────────────────────────────────────────────────┤", Color.CYAN)

    now = datetime.now()

    deadlines = [
        ("🔴 安全上线日（必须完成部署上线）", ACTIVITY_DEADLINE_ONLINE, "建议此日前上线，留足运营时间"),
        ("🟠 用户达标截止日（T+7起算点）", ACTIVITY_DEADLINE_USERS, "必须在此日前达标，否则T+7超期"),
        ("⚫ 活动结束日（T+7期满解锁）", ACTIVITY_END, "所有奖励最终解锁日"),
    ]

    for label, deadline, hint in deadlines:
        days_left, text = get_countdown(deadline)
        if days_left <= 0:
            color = Color.RED
        elif days_left <= 3:
            color = Color.YELLOW
        else:
            color = Color.GREEN
        date_str = deadline.strftime("%m月%d日")
        cprint(f"│ {label}  {date_str}", Color.CYAN)
        cprint(f"│   → {text}  ({hint})", color)

    cprint("└─────────────────────────────────────────────────────┘", Color.CYAN)


def print_report(results, domain_name):
    print()
    cprint("=" * 58, Color.BOLD + Color.CYAN if USE_COLOR else None)
    cprint(f"  支付宝AI支付激励计划 - 状态监控报告", Color.BOLD + Color.CYAN if USE_COLOR else None)
    cprint(f"  检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Color.GRAY if USE_COLOR else None)
    cprint(f"  监控域名: {domain_name}", Color.GRAY if USE_COLOR else None)
    cprint("=" * 58, Color.BOLD + Color.CYAN if USE_COLOR else None)

    for r in results:
        icon = status_icon(r["status"])
        check_name = r["check"].replace("_", " ").title()
        cprint(f"\n  {icon} {check_name}", Color.BOLD)
        cprint(f"    {r['status_text']}")
        if r.get("details"):
            for k, v in r["details"].items():
                if isinstance(v, list):
                    v = ", ".join(v) if v else "无"
                cprint(f"    · {k}: {v}", Color.GRAY if USE_COLOR else None)
        if r.get("beian_no"):
            cprint(f"    · 备案号: {r['beian_no']}", Color.GRAY if USE_COLOR else None)
        if r.get("company_name"):
            cprint(f"    · 主体: {r['company_name']}", Color.GRAY if USE_COLOR else None)
        if r.get("ip"):
            cprint(f"    · IP: {r['ip']}", Color.GRAY if USE_COLOR else None)
        if r.get("status_code"):
            cprint(f"    · HTTP状态: {r['status_code']}", Color.GRAY if USE_COLOR else None)

    print()
    print_countdown()

    pass_all = all(r["status"] in ("PASS", "INFO", "SKIP") for r in results)
    has_fail = any(r["status"] == "FAIL" for r in results)
    has_warn = any(r["status"] == "WARN" for r in results)

    cprint("\n" + "─" * 58, Color.CYAN)
    if has_fail:
        cprint("  🚨 存在未通过项！请立即处理上述失败项。", Color.RED + Color.BOLD if USE_COLOR else None)
        cprint("     如ICP备案尚未通过，请访问备案控制台查看进度。", Color.YELLOW if USE_COLOR else None)
    elif has_warn:
        cprint("  ⚠ 有审核中/警告项，请持续关注进度。", Color.YELLOW + Color.BOLD if USE_COLOR else None)
    elif pass_all:
        cprint("  🎉 所有检查项已通过！可以开始接入和部署。", Color.GREEN + Color.BOLD if USE_COLOR else None)
    cprint("─" * 58, Color.CYAN)
    print()


def generate_json(results):
    data = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "countdowns": {
            "deadline_online": ACTIVITY_DEADLINE_ONLINE.isoformat(),
            "deadline_users": ACTIVITY_DEADLINE_USERS.isoformat(),
            "activity_end": ACTIVITY_END.isoformat(),
            "days_to_online": get_countdown(ACTIVITY_DEADLINE_ONLINE)[0],
            "days_to_users": get_countdown(ACTIVITY_DEADLINE_USERS)[0],
            "days_to_end": get_countdown(ACTIVITY_END)[0],
        },
    }
    return data


def main():
    parser = argparse.ArgumentParser(
        description="支付宝AI支付激励计划 - 域名&ICP备案状态监控",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python check-status.py                    # 使用config.json配置单次检查
  python check-status.py --domain example.cn  # 直接指定域名（跳过阿里云API查询）
  python check-status.py --watch 300        # 每300秒(5分钟)自动刷新
  python check-status.py --json             # JSON格式输出
  python check-status.py --no-aliyun        # 跳过阿里云API（不需要AK/SK）
        """
    )
    parser.add_argument("--domain", help="要监控的域名（优先使用config.json中的配置）")
    parser.add_argument("--watch", type=int, metavar="SECONDS", help="持续监控，每SECONDS秒刷新一次")
    parser.add_argument("--json", action="store_true", help="以JSON格式输出结果")
    parser.add_argument("--no-aliyun", action="store_true", help="跳过阿里云API查询（不需要AccessKey）")
    parser.add_argument("--no-miit", action="store_true", help="跳过ICP备案查询")
    args = parser.parse_args()
    json_mode = args.json

    config = load_config(json_mode=json_mode)

    domain_name = args.domain or config.get("domain")
    if not domain_name:
        err_file = sys.stderr if json_mode else sys.stdout
        cprint("错误: 请在config.json中配置domain或使用--domain参数指定域名", Color.RED, file=err_file)
        sys.exit(1)

    ak_id = config.get("aliyun_access_key_id", "")
    ak_secret = config.get("aliyun_access_key_secret", "")

    use_aliyun = not args.no_aliyun and bool(ak_id and ak_secret) and ALIYUN_SDK_AVAILABLE

    warn_file = sys.stderr if json_mode else sys.stdout

    if not ALIYUN_SDK_AVAILABLE and not args.no_aliyun:
        cprint("提示: 阿里云SDK未安装，域名实名认证状态将跳过", Color.YELLOW, file=warn_file)
        cprint("  安装命令: pip install alibabacloud-tea-openapi alibabacloud-domain20180129 alibabacloud-tea-util", Color.GRAY, file=warn_file)
        cprint("  或使用 --no-aliyun 参数跳过此项检查\n", Color.GRAY, file=warn_file)

    if not use_aliyun and not args.no_aliyun and ALIYUN_SDK_AVAILABLE:
        if not (ak_id and ak_secret):
            cprint("提示: 未配置阿里云AccessKey，将跳过域名实名认证API查询", Color.YELLOW, file=warn_file)
            cprint("  在config.json中填入aliyun_access_key_id和aliyun_access_key_secret即可启用\n", Color.GRAY, file=warn_file)

    def run_checks():
        results = []

        if use_aliyun:
            client = create_aliyun_client(ak_id, ak_secret)
            results.append(check_domain_realname(client, domain_name))
        else:
            results.append({
                "check": "domain_realname",
                "domain": domain_name,
                "status": "SKIP",
                "status_text": "已跳过（未配置AK/SK或SDK未安装）",
            })

        dns_result = check_dns_resolution(domain_name)
        results.append(dns_result)

        https_result = check_https(domain_name)
        results.append(https_result)

        if not args.no_miit:
            icp_result = check_icp_beian_miit(domain_name)
            results.append(icp_result)
        else:
            results.append(check_icp_beian_manual(domain_name))

        if not args.no_miit:
            results.append(check_icp_beian_manual(domain_name))

        return results

    if args.watch:
        interval = args.watch
        cprint(f"开始持续监控，每 {interval} 秒刷新一次（按 Ctrl+C 停止）", Color.CYAN)
        while True:
            try:
                if os.name == "nt":
                    os.system("cls")
                else:
                    os.system("clear")
                results = run_checks()
                if args.json:
                    print(json.dumps(generate_json(results), ensure_ascii=False, indent=2))
                else:
                    print_report(results, domain_name)
                cprint(f"下次刷新: {interval}秒后 (Ctrl+C 停止)", Color.GRAY if USE_COLOR else None)
                time.sleep(interval)
            except KeyboardInterrupt:
                cprint("\n监控已停止", Color.CYAN)
                break
    else:
        results = run_checks()
        if args.json:
            print(json.dumps(generate_json(results), ensure_ascii=False, indent=2))
        else:
            print_report(results, domain_name)


if __name__ == "__main__":
    main()
