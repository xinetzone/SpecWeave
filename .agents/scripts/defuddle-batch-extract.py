#!/usr/bin/env python3
"""使用defuddle批量提取网页内容，支持llms.txt格式和普通URL列表。
功能：
- 支持读取llms.txt格式（URL 标题）或纯URL列表
- 批量调用defuddle CLI提取Markdown内容
- 自动按URL路径生成文件名，保存到指定目录
- 提供进度报告、错误统计和失败重试
- Windows PowerShell兼容（单引号包裹URL处理）
遵循defuddle-web-extraction-preferred模式：
1. 索引优先发现（llms.txt/sitemap.xml）
2. 批量提取
3. 完整性检查"""

import argparse
import re
import sys
import time
import subprocess
from pathlib import Path
from urllib.parse import urlparse, unquote
from concurrent.futures import ThreadPoolExecutor, as_completed

from lib.cli import add_common_args, print_pass, print_warn, print_error, print_summary
from lib.project import resolve_project_root

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

DEFAULT_TIMEOUT = 30
DEFAULT_WORKERS = 3
DEFAULT_RETRY = 2
SLEEP_BETWEEN_REQUESTS = 1

LLMS_LINE_RE = re.compile(r"^-\s*(https?://\S+)(?:\s*:\s*(.+))?$", re.MULTILINE)
URL_RE = re.compile(r"^https?://\S+$", re.MULTILINE)


def sanitize_filename(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        path = "index"
    if path.endswith("/"):
        path = path[:-1]
    name = path.replace("/", "-")
    name = unquote(name)
    name = re.sub(r"[^a-zA-Z0-9\-_\u4e00-\u9fff]", "-", name)
    name = re.sub(r"-+", "-", name)
    name = name.strip("-")
    if parsed.query:
        query_hash = str(abs(hash(parsed.query)))[:8]
        name = f"{name}-{query_hash}"
    return f"{name}.md"


def parse_url_list(file_path: Path) -> list:
    urls = []
    content = file_path.read_text(encoding="utf-8", errors="ignore")

    llms_matches = LLMS_LINE_RE.findall(content)
    if llms_matches:
        for url, title in llms_matches:
            urls.append({"url": url.strip(), "title": title.strip() if title else ""})
        return urls

    plain_urls = URL_RE.findall(content)
    if plain_urls:
        for url in plain_urls:
            urls.append({"url": url.strip(), "title": ""})
        return urls

    for line in content.splitlines():
        line = line.strip()
        if line.startswith("http://") or line.startswith("https://"):
            line = line.split("#")[0].strip()
            if line:
                parts = line.split(None, 1)
                url = parts[0]
                title = parts[1] if len(parts) > 1 else ""
                urls.append({"url": url, "title": title})

    return urls


def extract_single_url(url_info: dict, output_dir: Path, timeout: int, retry_count: int) -> dict:
    url = url_info["url"]
    title = url_info.get("title", "")
    filename = sanitize_filename(url)
    output_path = output_dir / filename

    if output_path.exists() and output_path.stat().st_size > 100:
        return {"url": url, "title": title, "status": "skipped", "file": str(output_path), "size": output_path.stat().st_size}

    last_error = None
    for attempt in range(retry_count + 1):
        try:
            cmd = ["defuddle", "parse", url, "--md", "-o", str(output_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="ignore")
            if result.returncode == 0 and output_path.exists():
                size = output_path.stat().st_size
                if size > 50:
                    return {"url": url, "title": title, "status": "success", "file": str(output_path), "size": size}
                else:
                    last_error = f"Output too small ({size} bytes)"
            else:
                stderr = result.stderr.strip() if result.stderr else "Unknown error"
                last_error = f"defuddle exit code {result.returncode}: {stderr[:200]}"
        except subprocess.TimeoutExpired:
            last_error = f"Timeout after {timeout}s"
        except Exception as e:
            last_error = str(e)[:200]

        if attempt < retry_count:
            time.sleep(SLEEP_BETWEEN_REQUESTS * (attempt + 1))

    return {"url": url, "title": title, "status": "failed", "error": last_error}


def main():
    parser = argparse.ArgumentParser(description="使用defuddle批量提取网页内容（支持llms.txt格式）")
    parser.add_argument("url_file", help="包含URL列表的文件（llms.txt格式或纯URL列表，每行一个URL）")
    parser.add_argument("-o", "--output-dir", required=True, help="输出目录路径")
    parser.add_argument("-w", "--workers", type=int, default=DEFAULT_WORKERS, help=f"并发数（默认：{DEFAULT_WORKERS}）")
    parser.add_argument("-t", "--timeout", type=int, default=DEFAULT_TIMEOUT, help=f"单个URL超时时间（秒，默认：{DEFAULT_TIMEOUT}）")
    parser.add_argument("-r", "--retry", type=int, default=DEFAULT_RETRY, help=f"失败重试次数（默认：{DEFAULT_RETRY}）")
    parser.add_argument("--dry-run", action="store_true", help="仅显示待提取URL列表，不执行提取")
    add_common_args(parser)

    args = parser.parse_args()
    project_root = resolve_project_root()

    url_file = Path(args.url_file)
    if not url_file.exists():
        print_error(f"URL列表文件不存在: {url_file}")
        return 1

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    urls = parse_url_list(url_file)
    if not urls:
        print_error(f"未在 {url_file} 中找到有效URL")
        return 1

    print(f"📋 待提取URL数量: {len(urls)}")
    print(f"📂 输出目录: {output_dir}")
    print(f"⚙️  并发数: {args.workers}, 超时: {args.timeout}s, 重试: {args.retry}次")
    print()

    if args.dry_run:
        print("Dry-run模式，待提取URL列表：")
        for i, item in enumerate(urls, 1):
            title = f" ({item['title']})" if item['title'] else ""
            print(f"  {i:3d}. {item['url']}{title}")
        print(f"\n共 {len(urls)} 个URL")
        return 0

    success_count = 0
    skipped_count = 0
    failed_count = 0
    results = []
    total_size = 0

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(extract_single_url, url_info, output_dir, args.timeout, args.retry): url_info for url_info in urls}
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            results.append(result)
            status = result["status"]
            url = result["url"]
            short_url = url[:80] + "..." if len(url) > 80 else url

            if status == "success":
                success_count += 1
                size_kb = result["size"] / 1024
                total_size += result["size"]
                print_pass(f"[{i}/{len(urls)}] 成功: {short_url} ({size_kb:.1f}KB)")
            elif status == "skipped":
                skipped_count += 1
                size_kb = result["size"] / 1024
                print(f"⏭️  [{i}/{len(urls)}] 跳过: {short_url} (已存在, {size_kb:.1f}KB)")
            else:
                failed_count += 1
                print_error(f"[{i}/{len(urls)}] 失败: {short_url}")
                print_warn(f"    原因: {result['error']}")

    elapsed = time.time() - start_time
    total_size_kb = total_size / 1024

    print()
    print("=" * 60)
    print_summary("批量提取完成")
    print(f"  总URL数: {len(urls)}")
    print(f"  ✅ 成功: {success_count}")
    print(f"  ⏭️  跳过: {skipped_count}")
    print(f"  ❌ 失败: {failed_count}")
    print(f"  📊 总大小: {total_size_kb:.1f}KB")
    print(f"  ⏱️  耗时: {elapsed:.1f}秒")
    print(f"  📂 输出目录: {output_dir}")

    if failed_count > 0:
        print()
        print_warn("失败URL列表：")
        for result in results:
            if result["status"] == "failed":
                print(f"  - {result['url']}")
                print(f"    原因: {result['error']}")

    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
