#!/usr/bin/env python3
import re
import os

BASE_DIR = r"d:\spaces\SpecWeave\.agents\docs\knowledge\learning\08-systems-infrastructure\wsl-wiki"
FILES = [
    "04-architecture.md",
    "05-filesystem-interop.md",
    "06-wslc-api.md",
    "07-network-config-systemd.md",
]

FORBIDDEN_PATTERNS = [
    (r'<br\s*/?>', "<br/> HTML标签"),
    (r'[①②③④⑤]', "带圈数字 ①②③④⑤"),
    (r'[【】]', "中文方括号 【】"),
    (r'subgraph[^}]*direction', "嵌套 direction 语句"),
]

def extract_mermaid_blocks(content):
    pattern = r'```mermaid\s*\n(.*?)```'
    blocks = []
    for match in re.finditer(pattern, content, re.DOTALL):
        blocks.append({
            'start_line': content[:match.start()].count('\n') + 1,
            'end_line': content[:match.end()].count('\n') + 1,
            'content': match.group(1)
        })
    return blocks

def check_cross_subgraph_note(block_content):
    subgraphs = []
    subgraph_pattern = r'subgraph\s+(\w+)'
    for m in re.finditer(subgraph_pattern, block_content):
        subgraphs.append(m.group(1))
    
    if len(subgraphs) < 2:
        return False
    
    note_pattern = r'note\s+(?:right|left|over)\s+of\s+(\w+)'
    notes = []
    for m in re.finditer(note_pattern, block_content):
        notes.append(m.group(1))
    
    end_pattern = r'end\b'
    subgraph_stack = []
    node_to_subgraph = {}
    
    lines = block_content.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('subgraph '):
            sg_match = re.match(r'subgraph\s+(\w+)', line)
            if sg_match:
                subgraph_stack.append(sg_match.group(1))
        elif line == 'end':
            if subgraph_stack:
                subgraph_stack.pop()
        else:
            node_def = re.match(r'\s*(\w+)\s*(?:\[|\(|\{|\>|\")', line)
            if node_def and subgraph_stack:
                node_to_subgraph[node_def.group(1)] = subgraph_stack[-1]
    
    for note in notes:
        note_target_subgraph = node_to_subgraph.get(note)
        if note_target_subgraph and len(subgraph_stack) > 0:
            pass
    
    if 'note ' in block_content.lower() and 'over' in block_content.lower():
        note_over_match = re.search(r'note\s+over\s+([^:\n]+):', block_content)
        if note_over_match:
            targets = note_over_match.group(1).split(',')
            target_sgs = set()
            for t in targets:
                t = t.strip()
                if t in node_to_subgraph:
                    target_sgs.add(node_to_subgraph[t])
                elif t in subgraphs:
                    target_sgs.add(t)
            if len(target_sgs) > 1:
                return True
    
    return False

def check_block(filepath, block_idx, block):
    issues = []
    content = block['content']
    
    for pattern, desc in FORBIDDEN_PATTERNS:
        if re.search(pattern, content):
            matches = re.findall(pattern, content)
            issues.append(f"  - 发现{desc}: {matches}")
    
    if check_cross_subgraph_note(content):
        issues.append("  - 发现跨subgraph的note语句")
    
    return issues

def main():
    all_results = {}
    
    for filename in FILES:
        filepath = os.path.join(BASE_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        blocks = extract_mermaid_blocks(content)
        results = []
        
        for idx, block in enumerate(blocks, 1):
            issues = check_block(filepath, idx, block)
            results.append({
                'index': idx,
                'start_line': block['start_line'],
                'end_line': block['end_line'],
                'issues': issues,
                'passed': len(issues) == 0
            })
        
        all_results[filename] = results
    
    print("=" * 80)
    print("Mermaid 代码块禁止项检查报告")
    print("=" * 80)
    
    total_blocks = 0
    total_passed = 0
    total_failed = 0
    
    for filename, results in all_results.items():
        print(f"\n📄 {filename}")
        print("-" * 60)
        for r in results:
            total_blocks += 1
            if r['passed']:
                total_passed += 1
                print(f"  ✅ 代码块 #{r['index']} (行 {r['start_line']}-{r['end_line']}): 通过")
            else:
                total_failed += 1
                print(f"  ❌ 代码块 #{r['index']} (行 {r['start_line']}-{r['end_line']}): 发现问题")
                for issue in r['issues']:
                    print(issue)
    
    print("\n" + "=" * 80)
    print(f"统计: 共 {total_blocks} 个Mermaid代码块, 通过 {total_passed} 个, 有问题 {total_failed} 个")
    print("=" * 80)

if __name__ == '__main__':
    main()
