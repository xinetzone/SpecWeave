"""C-2: 根级 spec 批量归类迁移脚本
基于关键词前缀匹配 + 内容语义匹配，将根级平铺 spec 归入 7 大主题目录。
"""
import sys
import shutil
from pathlib import Path
import json

# 动态计算路径，禁止硬编码绝对路径
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Windows GBK 兼容
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

PROJ_ROOT = SCRIPTS_DIR.parent.parent
SPEC_ROOT = PROJ_ROOT / '.trae' / 'specs'

# 7 大主题目录
THEMES = {
    'core-foundation',
    'roles-governance',
    'standards-tools',
    'readme-branding',
    'docs-restructure',
    'retrospectives-insights',
    'migration-archival',
}

# 保留不动的根级目录（主题本身、已归类目录）
KEEP_ROOT = set()


def is_theme_dir(d: str) -> bool:
    return d in THEMES


def classify_by_name(name: str) -> str | None:
    """基于关键词前缀命名规则进行归类。
    返回目标主题名，无匹配则返回 None（需人工确认）。
    """
    n = name.lower()

    # --- core-foundation: 核心基础设施、知识系统、容器配置 ---
    if any(p in n for p in [
        'create-agents', 'knowledge-management', 'prompt-extraction',
        'create-first-principles', 'create-sphinx-docs', 'monetization',
        'devcontainer', 'conda-dev-source', 'conda-dev-github',
        'python314t-conda-env', 'python314-stdlib', 'optimize-mystx',
        'optimize-okf', 'knowledge-catalog', 'knowledge-consolidation',
        'extract-agent-workspace', 'awesome-okf-xs-doc', 'awesome-okf-exploration',
        'xmhub-agents-workspace', 'agent-app-marketplace',
        'variant-framework', 'ai-dev-variant',
        'bundles-self-contained', 'bundles-grouping',
        'agent-architecture-book', 'universal-prd-template',
    ]):
        return 'core-foundation'

    # --- standards-tools: 标准/工具/教程/wiki 创建 ---
    if any(p in n for p in [
        'standardize-file', 'check-spec', 'optimize-trae',
        'refactor-scripts', 'analyze-script', 'establish-vendor',
        'adjust-vendor', 'fix-windows-terminal', 'establish-mermaid',
        'markdown-as-interface', 'add-tuya', 'sensitive-info',
        'check-academic', 'establish-pwsh7', 'generate-first-principles-knowledge-graph',
        # create-*wiki-tutorial 系列（非经典古籍类）
        'create-*-wiki-tutorial',
        'create-mermaid-wiki-tutorial',
        'create-eve-framework-wiki-tutorial',
        'create-python314-stdlib-wiki-tutorial',
        'create-conda-dev-github-wiki-tutorial',
        'create-conda-dev-source-wiki-tutorial',
        'create-hermes-okf-wiki-tutorial',
        'create-cordis-paper-wiki-tutorial',
        'create-tvm-ffi-wiki-tutorial',
        'create-seven-concepts',
        'create-agent-eval-methodology',
        'create-graphql-wiki-tutorial',
        'create-onnx-wiki-tutorial',
        'create-sexylogy-classics-wiki',
        'create-fangzhong-bajia-wiki',
        'create-mawangdui-fangzhong-wiki',
        # -wiki-tutorial 通用后缀
        'wiki-tutorial',
        # -wiki 但非古籍经典类（技术产品 wiki）
        'okf-wiki',
        # 规则/技能类
        'agentskills', 'claude-vision-skill', 'jira-skill',
        'skill-auto-loader', 'wrap-bare-urls-mermaid',
        'tvm-ffi-wiki-tutorial',
    ]):
        return 'standards-tools'

    # --- roles-governance: 角色定义扩展、治理规则 ---
    if any(p in n for p in [
        'add-thesis-advisor-role', 'create-token-optimizer-role',
        'adversarial-review',
    ]):
        return 'roles-governance'

    # --- readme-branding: README/品牌定位优化 ---
    if any(p in n for p in [
        'readme-branding', 'readme-zero-baseline', 'update-specweave-demo',
    ]):
        return 'readme-branding'

    # --- docs-restructure: 文档重组、去重、分离 ---
    if any(p in n for p in [
        'consolidate-agents-spec-docs', 'docs-restructure',
        'docs-seven-concepts-restructure',
        'reclassify-bundles',
    ]):
        return 'docs-restructure'

    # --- retrospectives-insights: 复盘、洞察、学习分析 ---
    if any(p in n for p in [
        'retrospective', 'retrospect-',
        'analysis', '-analysis',
        'analyze-',
        'learning', 'deepseek-v4-free-plan',
        'xiaomai-comprehensive', 'tvm-ffi-200-perspectives',
        'xmtools-700-perspectives', 'xmtools-comprehensive-retrospective',
        'business-trends-analysis', 'web-content-analysis',
        'image-', 'neijing-illustrations',
        'images-first-principles',
    ]):
        return 'retrospectives-insights'

    # --- migration-archival: 迁移、归档、bundle 整理 ---
    if any(p in n for p in [
        'migrate-', 'archive-', 'consolidate-',
        'awesome-okf-vendor-migration', 'agents-docs-migration',
        'move-knowledge-catalog', 'migrate-learning-to-okf',
        'update-invocations-bundle', 'okf-spec-to-bundle',
        'okf-bundles-integrity',
        'docs-to-okf-wiki', 'docs-to-knowledge',
        'jianshu-blogs-to-okf',
        'dingtalk-okr-wiki-migration',
        'nuitka-scripts-migration',
        'caffe-ffi-extraction-migration',
    ]):
        return 'migration-archival'

    # --- 特殊规则：caffe-* / xmnn-* 系列归入 core-foundation ---
    if n.startswith('caffe-') or n.startswith('caffex-') or n.startswith('caffeproto-'):
        return 'core-foundation'
    if n.startswith('xmnn-') or n.startswith('xmtools-'):
        # xmtools 的分析类归 retrospectives-insights，其余归 core-foundation
        if any(p in n for p in ['retrospective', 'perspective', 'analysis', 'customer-distribution']):
            return 'retrospectives-insights'
        return 'core-foundation'
    if n.startswith('chaos-ai-'):
        return 'core-foundation'
    if n.startswith('vta-hw-') or n.startswith('npu-') or n.startswith('conv-gemm-'):
        return 'core-foundation'

    # --- 经典古籍 OKF Wiki 归 standards-tools（知识包创建） ---
    if n.endswith('-okf-wiki') and any(p in n for p in [
        'laozi', 'zhuangzi', 'kongzi', 'mozi', 'guiguzi', 'legalism',
        'confucian', 'buddhism', 'yinyangjia', 'yinfujing', 'yangsheng',
        'yixinfang', 'fangzhong', 'daojia', 'fusheng', 'waijing',
        'boshu', 'yangsheng-classics', 'tcm-classics',
        'chinese-physics', 'chinese-math', 'chemistry', 'math',
        'physics', 'relationships', 'english-grammar',
        'threeui', 'textualize', 'containers', 'sympy', 'rust-lang',
        'scrapli', 'tkinter', 'ssh-python', 'pyinvoke', 'protobuf',
        'sphinx-argparse', 'pocketflow', 'deepseek-ai',
        'anthropic-python-sdk', 'fastapi', 'graphql',
        'executablebooks', 'tiktoken', 'veadk-python',
        'coze-dev', 'tencent', 'datawhalechina',
        'agora-gemini', 'a2a-mcp', 'bytedance',
        'qwen', 'matrix-agent-company', 'wigolo-blog',
        'hongge', 'hr-admin', 'siemens-industrial',
        'tushare', 'doubao', 'tongyi-mai', 'deepseek-harness',
        'zleap-agent', 'volcengine-agentkit',
        '3b1b', 'anything',
    ]):
        return 'standards-tools'

    # --- okf-bundle 系列归 standards-tools ---
    if '-okf-bundle' in n or n.endswith('-okf-bundle'):
        return 'standards-tools'

    # 无匹配
    return None


def main():
    # 收集根级 spec 目录
    root_specs = []
    for d in sorted(SPEC_ROOT.iterdir()):
        if not d.is_dir():
            continue
        if is_theme_dir(d.name):
            KEEP_ROOT.add(d.name)
            continue
        if (d / 'spec.md').exists():
            root_specs.append(d)

    print(f"根级 spec 目录总数: {len(root_specs)}")

    # 执行归类
    mapping = {}  # dir_name -> theme
    no_match = []

    for spec_dir in root_specs:
        name = spec_dir.name
        theme = classify_by_name(name)
        if theme:
            mapping[name] = theme
        else:
            no_match.append(name)

    print(f"自动归类: {len(mapping)} 个")
    print(f"需人工确认: {len(no_match)} 个")
    print()

    # 输出归类摘要
    theme_counts = {}
    for name, theme in mapping.items():
        theme_counts[theme] = theme_counts.get(theme, 0) + 1

    print("归类分布:")
    for theme, count in sorted(theme_counts.items(), key=lambda x: -x[1]):
        print(f"  {theme}: {count} 个")
    print()

    if no_match:
        print("需人工确认的目录:")
        for name in no_match:
            print(f"  - {name}")
        print()

    # 执行迁移（dry-run 模式：先输出计划，不实际移动）
    dry_run = True  # 设为 False 执行实际迁移

    moves = []
    for src_name, theme in mapping.items():
        src = SPEC_ROOT / src_name
        dst = SPEC_ROOT / theme / src_name
        if src.exists():
            moves.append((src, dst, src_name, theme))

    print(f"迁移计划: {len(moves)} 个 spec 目录")
    if dry_run:
        print("(DRY-RUN 模式：仅输出计划，未实际移动)")
    else:
        for src, dst, src_name, theme in moves:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            print(f"  [{theme}] {src_name} -> {dst}")

    # 保存归类映射表
    out_path = PROJ_ROOT / '.temp' / 'spec-classification-map.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({
            'mapping': mapping,
            'no_match': no_match,
            'total': len(root_specs),
            'mapped': len(mapping),
            'dry_run': dry_run,
        }, f, ensure_ascii=False, indent=2)
    print(f"\n归类映射表已写入: {out_path}")

    # 统计迁移后根级剩余数量
    remaining = [d.name for d in SPEC_ROOT.iterdir()
                 if d.is_dir() and d.name not in THEMES and (d / 'spec.md').exists()]
    print(f"迁移后根级平铺 spec 数量: {len(remaining)}")
    if remaining:
        print("剩余根级 spec:")
        for r in remaining:
            print(f"  - {r}")


if __name__ == '__main__':
    main()
