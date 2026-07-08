import subprocess
import os
import sys
from pathlib import Path

BASE_DIR = Path(r"d:\AI\.trae\specs\retrospectives-insights\minitap-official-docs-wiki\raw-content")

URLS = [
    ("minitest", "meet-mini", "https://www.minitap.ai/docs/minitest/get-started/meet-mini"),
    ("minitest", "quickstart", "https://www.minitap.ai/docs/minitest/get-started/quickstart"),
    ("minitest", "index", "https://www.minitap.ai/docs/minitest"),
    ("minitest", "cursor-and-claude", "https://www.minitap.ai/docs/minitest/integrations/cursor-and-claude"),
    ("minitest", "github", "https://www.minitap.ai/docs/minitest/integrations/github"),
    ("minitest", "mini-in-slack", "https://www.minitap.ai/docs/minitest/integrations/mini-in-slack"),
    ("minitest", "capabilities", "https://www.minitap.ai/docs/minitest/reference/capabilities"),
    ("minitest", "cli-commands", "https://www.minitap.ai/docs/minitest/reference/cli-commands"),
    ("minitest", "glossary", "https://www.minitap.ai/docs/minitest/reference/glossary"),
    ("minitest", "mcp-tools", "https://www.minitap.ai/docs/minitest/reference/mcp-tools"),
    ("minitest", "mini-commands", "https://www.minitap.ai/docs/minitest/reference/mini-commands"),
    ("minitest", "minitest-trigger-action", "https://www.minitap.ai/docs/minitest/reference/minitest-trigger-action"),
    ("minitest", "builds", "https://www.minitap.ai/docs/minitest/runs/builds"),
    ("minitest", "run-report", "https://www.minitap.ai/docs/minitest/runs/run-report"),
    ("minitest", "triggering-a-run", "https://www.minitap.ai/docs/minitest/runs/triggering-a-run"),
    ("minitest", "anatomy", "https://www.minitap.ai/docs/minitest/suite/anatomy"),
    ("minitest", "authoring", "https://www.minitap.ai/docs/minitest/suite/authoring"),
    ("minitest", "mini-maintains-your-suite", "https://www.minitap.ai/docs/minitest/suite/mini-maintains-your-suite"),
    ("minitest", "issues", "https://www.minitap.ai/docs/minitest/triage/issues"),
    ("minitest", "suggestions", "https://www.minitap.ai/docs/minitest/triage/suggestions"),
    ("mobile-use-sdk", "browserstack-quickstart", "https://www.minitap.ai/docs/mobile-use-sdk/browserstack-quickstart"),
    ("mobile-use-sdk", "cloud-quickstart", "https://www.minitap.ai/docs/mobile-use-sdk/cloud-quickstart"),
    ("mobile-use-sdk", "agent", "https://www.minitap.ai/docs/mobile-use-sdk/core-concepts/agent"),
    ("mobile-use-sdk", "builders", "https://www.minitap.ai/docs/mobile-use-sdk/core-concepts/builders"),
    ("mobile-use-sdk", "observability", "https://www.minitap.ai/docs/mobile-use-sdk/core-concepts/observability"),
    ("mobile-use-sdk", "overview", "https://www.minitap.ai/docs/mobile-use-sdk/core-concepts/overview"),
    ("mobile-use-sdk", "profiles", "https://www.minitap.ai/docs/mobile-use-sdk/core-concepts/profiles"),
    ("mobile-use-sdk", "tasks", "https://www.minitap.ai/docs/mobile-use-sdk/core-concepts/tasks"),
    ("mobile-use-sdk", "app-lock-messaging", "https://www.minitap.ai/docs/mobile-use-sdk/examples/app-lock-messaging"),
    ("mobile-use-sdk", "platform-task-example", "https://www.minitap.ai/docs/mobile-use-sdk/examples/platform-task-example"),
    ("mobile-use-sdk", "simple-photo-organizer", "https://www.minitap.ai/docs/mobile-use-sdk/examples/simple-photo-organizer"),
    ("mobile-use-sdk", "smart-notification-assistant", "https://www.minitap.ai/docs/mobile-use-sdk/examples/smart-notification-assistant"),
    ("mobile-use-sdk", "video-transcription", "https://www.minitap.ai/docs/mobile-use-sdk/examples/video-transcription"),
    ("mobile-use-sdk", "feedback", "https://www.minitap.ai/docs/mobile-use-sdk/feedback"),
    ("mobile-use-sdk", "installation", "https://www.minitap.ai/docs/mobile-use-sdk/installation"),
    ("mobile-use-sdk", "introduction", "https://www.minitap.ai/docs/mobile-use-sdk/introduction"),
    ("mobile-use-sdk", "physical-ios-quickstart", "https://www.minitap.ai/docs/mobile-use-sdk/physical-ios-quickstart"),
    ("mobile-use-sdk", "platform-quickstart", "https://www.minitap.ai/docs/mobile-use-sdk/platform-quickstart"),
    ("mobile-use-sdk", "quickstart", "https://www.minitap.ai/docs/mobile-use-sdk/quickstart"),
    ("mobile-use-sdk", "sdk-agent", "https://www.minitap.ai/docs/mobile-use-sdk/sdk-reference/agent"),
    ("mobile-use-sdk", "sdk-agent-config-builder", "https://www.minitap.ai/docs/mobile-use-sdk/sdk-reference/agent-config-builder"),
    ("mobile-use-sdk", "sdk-exceptions", "https://www.minitap.ai/docs/mobile-use-sdk/sdk-reference/exceptions"),
    ("mobile-use-sdk", "sdk-task-request-builder", "https://www.minitap.ai/docs/mobile-use-sdk/sdk-reference/task-request-builder"),
    ("mobile-use-sdk", "sdk-types", "https://www.minitap.ai/docs/mobile-use-sdk/sdk-reference/types"),
    ("mobile-use-sdk", "troubleshooting", "https://www.minitap.ai/docs/mobile-use-sdk/troubleshooting"),
]

success_list = []
failed_list = []

total = len(URLS)
print(f"开始提取 {total} 个页面...\n")

for idx, (category, filename, url) in enumerate(URLS, 1):
    output_dir = BASE_DIR / category
    output_file = output_dir / f"{filename}.md"
    
    print(f"[{idx}/{total}] 正在提取: {url}")
    print(f"  -> 保存到: {output_file}")
    
    try:
        cmd = f'defuddle parse "{url}" --md'
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
            shell=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result.stdout)
            file_size = os.path.getsize(output_file)
            print(f"  ✓ 成功 ({file_size} bytes)")
            success_list.append((category, filename, url, file_size))
        else:
            error_msg = result.stderr.strip() if result.stderr else "无输出内容"
            print(f"  ✗ 失败: {error_msg}")
            failed_list.append((category, filename, url, error_msg))
    except subprocess.TimeoutExpired:
        print(f"  ✗ 失败: 超时")
        failed_list.append((category, filename, url, "超时"))
    except Exception as e:
        print(f"  ✗ 失败: {str(e)}")
        failed_list.append((category, filename, url, str(e)))
    
    print()

print("=" * 60)
print("提取完成！统计结果：")
print(f"总计: {total} 个页面")
print(f"成功: {len(success_list)} 个")
print(f"失败: {len(failed_list)} 个")
print()

if success_list:
    print("成功提取的文件：")
    for cat, fname, url, size in success_list:
        print(f"  ✓ {cat}/{fname}.md ({size} bytes)")
    print()

if failed_list:
    print("失败列表：")
    for cat, fname, url, err in failed_list:
        print(f"  ✗ {cat}/{fname}: {err}")
    print()

minitest_success = sum(1 for s in success_list if s[0] == "minitest")
mobile_success = sum(1 for s in success_list if s[0] == "mobile-use-sdk")
print(f"minitest 部分: {minitest_success}/20 成功")
print(f"mobile-use-sdk 部分: {mobile_success}/25 成功")
