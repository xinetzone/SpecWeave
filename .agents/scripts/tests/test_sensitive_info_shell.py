"""Shell命令语法脱敏误报修复验证测试。"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.checks.sensitive_info import (
    scan_file, PERSONAL_PATH_WIN, PERSONAL_PATH_UNIX,
    _is_shell_command_context, _is_dockerfile_context,
    _is_valid_path_username,
)


def test_shell_command_context_detection():
    """测试Shell命令上下文检测函数。"""
    test_cases = [
        # (line_tail, expected_result, description)
        (" && echo '---' && ls /etc/", True, "&& 连接多条命令"),
        (" || true", True, "|| 操作符"),
        ("; pwd", True, "; 命令分隔符"),
        ("| grep root", True, "| 管道"),
        ("*//*.log", True, "* 通配符glob"),
        (" /etc/passwd", True, "空格后跟另一个路径（多路径参数）"),
        ("/project", False, "正常子路径（/home/user/project）"),
        ("/.ssh/config", False, "正常隐藏文件子路径"),
    ]
    
    print("=== _is_shell_command_context 单元测试 ===")
    passed = 0
    failed = 0
    for after, expected, desc in test_cases:
        line = "ls -la /home/" + after
        result = _is_shell_command_context(line, len("ls -la /home/"), "/")
        if result == expected:
            print(f"  ✅ {desc}")
            passed += 1
        else:
            print(f"  ❌ {desc}: expected={expected}, got={result}")
            failed += 1
    return passed, failed


def test_valid_path_username():
    """测试用户名有效性验证。"""
    test_cases = [
        # (username, expected_valid, description)
        ("xinzo", True, "正常英文用户名"),
        ("John Doe", True, "带空格的用户名(macOS)"),
        ("zhangsan", True, "拼音用户名"),
        ("user.name", True, "带点的用户名"),
        ("user_name", True, "带下划线的用户名"),
        ("user-name", True, "带连字符的用户名"),
        (" && echo '---'", False, "shell命令片段(含&)"),
        (";ls", False, "shell命令片段(含;)"),
        ("|grep", False, "shell命令片段(含|)"),
        ("'test", False, "以单引号开头"),
        ("$HOME", False, "shell变量($)"),
        ("(subshell)", False, "shell子shell括号"),
    ]
    
    print("\n=== _is_valid_path_username 单元测试 ===")
    passed = 0
    failed = 0
    for username, expected, desc in test_cases:
        result = _is_valid_path_username(username)
        if result == expected:
            print(f"  ✅ {desc}: '{username}' -> {result}")
            passed += 1
        else:
            print(f"  ❌ {desc}: '{username}' expected={expected}, got={result}")
            failed += 1
    return passed, failed


def test_dockerfile_context():
    """测试Dockerfile上下文检测。"""
    print("\n=== _is_dockerfile_context 单元测试 ===")
    passed = 0
    failed = 0
    
    # 测试Dockerfile文件名
    df_path = Path("Dockerfile")
    test_lines = [
        ("ENTRYPOINT [\"/bin/bash\", \"/home/ai/entrypoint.sh\"]", True, "ENTRYPOINT指令"),
        ("ENV PATH=\"/home/conda_user/miniconda3/bin:$PATH\"", True, "ENV指令"),
        ("RUN bash install.sh -b -p /home/conda_user/miniconda3", True, "RUN指令"),
        ("COPY . /app", True, "COPY指令"),
        ("# 这是注释", False, "注释行"),
    ]
    for line, expected, desc in test_lines:
        result = _is_dockerfile_context(df_path, line)
        if result == expected:
            print(f"  ✅ {desc}")
            passed += 1
        else:
            print(f"  ❌ {desc}: expected={expected}, got={result}")
            failed += 1
    
    # 测试非Dockerfile文件名
    md_path = Path("test.md")
    result = _is_dockerfile_context(md_path, "ENTRYPOINT [\"/bin/bash\", \"/home/ai/entrypoint.sh\"]")
    if result == False:
        print(f"  ✅ .md文件中的ENTRYPOINT不触发Dockerfile检测")
        passed += 1
    else:
        print(f"  ❌ .md文件不应触发Dockerfile检测")
        failed += 1
    
    return passed, failed


def test_end_to_end_scan():
    """端到端扫描测试：验证Shell命令和占位符不再误报。"""
    # (content, filename_suffix, should_report_path, description)
    test_cases = [
        # Shell命令语法场景 - 不应报警
        ("ls -la /home/ && echo '---' && ls /etc/wsl.conf\n", ".md", False, "shell: ls /home/ && 列举目录"),
        ("wsl -d distro -- bash -c \"ls -la /home/ && echo test\"\n", ".md", False, "shell: wsl bash -c ls /home/"),
        ("cd /Users/; pwd\n", ".md", False, "shell: cd /Users/; 分号分隔"),
        ("for d in /home/*/; do echo $d; done\n", ".md", False, "shell: /home/*/ glob通配符"),
        # Dockerfile容器内路径 - 不应报警
        ("ENTRYPOINT [\"/bin/bash\", \"/home/ai/entrypoint.sh\"]\n", ".dockerfile", False, "docker: ENTRYPOINT容器路径"),
        ("ENV PATH=\"/home/conda_user/miniconda3/bin:$PATH\"\n", ".dockerfile", False, "docker: ENV容器内PATH"),
        ("RUN bash miniconda.sh -b -p /home/conda_user/miniconda3\n", ".dockerfile", False, "docker: RUN安装到容器路径"),
        # 文档占位符用户名 - 不应报警
        ("硬编码 `/home/dev/project` 导致不可移植\n", ".md", False, "placeholder: /home/dev/"),
        ("TVM_SRC = Path(\"/home/zhangsan/projects/npu\")\n", ".md", False, "placeholder: /home/zhangsan/"),
        ("C:\\Users\\John Doe\\ 路径含空格\n", ".md", False, "placeholder: John Doe带空格示例"),
        ("/home/otheruser/ 跨用户目录边界\n", ".md", False, "placeholder: otheruser边界示例"),
        ("C:\\Users\\YourName\\.ssh\n", ".md", False, "placeholder: YourName教程占位符"),
        ("C:\\Users\\用户名\\Documents\n", ".md", False, "placeholder: 中文用户名占位符"),
        ("/Users/you/.config\n", ".md", False, "placeholder: you通用占位符"),
        ("C:\\Users\\you\\AppData\n", ".md", False, "placeholder: you Windows占位符"),
        # 真实个人路径 - 应该报警（测试数据，使用nosec标记跳过自身扫描）
        ("CONFIG_PATH = \"C:\\Users\\xinzo\\anaconda3\"\n", ".md", True, "real: xinzo Windows真实路径"),  # nosec
        ("/home/xinzo/project/libs/tvm\n", ".md", True, "real: xinzo Unix真实路径"),  # nosec
        # 白名单系统路径 - 不应报警
        ("/root/.bashrc\n", ".md", False, "system: /root/系统目录"),
        ("C:\\Users\\Public\\Documents\n", ".md", False, "system: Public公共目录"),
        ("C:\\Users\\Default\\NTUSER.DAT\n", ".md", False, "system: Default默认用户"),
    ]
    
    print("\n=== 端到端扫描测试 (Shell/占位符误报修复) ===")
    passed = 0
    failed = 0
    
    for content, suffix, should_report, desc in test_cases:
        with tempfile.NamedTemporaryFile(
            mode='w', suffix=suffix, delete=False, encoding='utf-8'
        ) as f:
            f.write(content)
            tmp = Path(f.name)
        findings = scan_file(tmp)
        path_findings = [f for f in findings if f.type in (PERSONAL_PATH_WIN, PERSONAL_PATH_UNIX)]
        reported = len(path_findings) > 0
        tmp.unlink()
        
        if reported == should_report:
            print(f"  ✅ {desc}")
            passed += 1
        else:
            print(f"  ❌ {desc}")
            print(f"     内容: {content.strip()[:70]}")
            print(f"     期望: {'报警' if should_report else '不报警'}, 实际: {'报警' if reported else '不报警'}")
            if path_findings:
                for pf in path_findings:
                    print(f"     匹配: {pf.match} (L{pf.line}:{pf.col})")
            failed += 1
    
    return passed, failed


def main():
    total_passed = 0
    total_failed = 0
    
    p, f = test_shell_command_context_detection()
    total_passed += p
    total_failed += f
    
    p, f = test_valid_path_username()
    total_passed += p
    total_failed += f
    
    p, f = test_dockerfile_context()
    total_passed += p
    total_failed += f
    
    p, f = test_end_to_end_scan()
    total_passed += p
    total_failed += f
    
    print(f"\n{'='*60}")
    print(f"总计: {total_passed} passed, {total_failed} failed")
    print(f"{'='*60}")
    
    return 1 if total_failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
