"""trae_edge_case_handler.py 模块功能测试。"""
import sys
sys.path.insert(0, '.agents/scripts')

from trae_edge_case_handler import (
    BoundaryLevel, BoundaryScene, BoundaryAction, Signal,
    BoundaryContext, BoundaryDecision, BoundarySummary,
    check_multi_signal, classify_boundary_level,
    handle_fatal_boundary, handle_warning_boundary, handle_info_boundary,
    handle_boundary, check_boundary, get_boundary,
    adapt_sandbox_limitation, adapt_powershell_encoding,
    adapt_forum_login_expired, adapt_dom_structure_change,
    _BOUNDARY_REGISTRY,
)

ctx = BoundaryContext(operation='forum_edit', platform='windows')

# 测试1: 多信号组合检测
signals = [
    Signal(name='cookie_expired', hit=True, reliability=3),
    Signal(name='redirect_to_login', hit=True, reliability=2),
    Signal(name='api_returns_401', hit=False, reliability=1),
]
confirmed, hits = check_multi_signal(signals, min_positive=2)
assert confirmed and hits == ['cookie_expired', 'redirect_to_login']
print('[PASS] 测试1: 多信号组合检测')

# 测试2: 三级分级
assert classify_boundary_level(False, False, False) == BoundaryLevel.FATAL
assert classify_boundary_level(True, True, False) == BoundaryLevel.WARNING
assert classify_boundary_level(True, False, True) == BoundaryLevel.WARNING
assert classify_boundary_level(True, False, False) == BoundaryLevel.INFO
print('[PASS] 测试2: 三级分级判断')

# 测试3: 致命级处理（无替代方案 → 退出）
dec = handle_fatal_boundary('trae-ide-sandbox-limitation', ctx)
assert dec.action == BoundaryAction.EXIT and not dec.recovered
print('[PASS] 测试3: 致命级处理（无替代 → 退出）')

# 测试4: 致命级处理（替代方案成功 → 继续）
dec = handle_fatal_boundary('test', ctx, alternatives=[lambda: True])
assert dec.action == BoundaryAction.CONTINUE and dec.recovered
print('[PASS] 测试4: 致命级处理（替代成功 → 继续）')

# 测试5: 警告级处理（降级成功 → 继续）
dec = handle_warning_boundary('test', ctx, degrade_fn=lambda: True, verify_fn=lambda: True)
assert dec.action == BoundaryAction.CONTINUE and dec.recovered
print('[PASS] 测试5: 警告级处理（降级成功 → 继续）')

# 测试6: 警告级处理（降级失败超限 → 升级致命）
count = [0]
def fail_degrade():
    count[0] += 1
    return False
dec = handle_warning_boundary('test', ctx, degrade_fn=fail_degrade, max_retries=2)
assert dec.action == BoundaryAction.EXIT and count[0] == 2
print('[PASS] 测试6: 警告级处理（失败2次 → 升级致命）')

# 测试7: 沙箱限制适配（集成浏览器）
dec = adapt_sandbox_limitation(ctx, use_integrated_browser=True)
assert dec.action == BoundaryAction.CONTINUE and dec.fallback_used == 'integrated_browser'
print('[PASS] 测试7: 沙箱限制适配（集成浏览器）')

# 测试8: 沙箱限制适配（无方案 → 退出）
dec = adapt_sandbox_limitation(ctx)
assert dec.action == BoundaryAction.EXIT
print('[PASS] 测试8: 沙箱限制适配（无方案 → 退出）')

# 测试9: PowerShell编码适配（多行 → -F参数）
dec = adapt_powershell_encoding(ctx, is_multiline=True)
assert dec.fallback_used == 'file_parameter'
print('[PASS] 测试9: PowerShell编码适配（多行 → -F参数）')

# 测试10: 论坛登录过期适配（信号不足 → 继续）
dec = adapt_forum_login_expired(ctx, [Signal('s1', True, reliability=1)])
assert dec.action == BoundaryAction.CONTINUE
print('[PASS] 测试10: 论坛登录过期适配（信号不足 → 继续）')

# 测试11: 论坛登录过期适配（重新登录成功）
signals_strong = [
    Signal('cookie_expired', True, reliability=3),
    Signal('redirect_login', True, reliability=2),
]
dec = adapt_forum_login_expired(ctx, signals_strong, relogin_fn=lambda: True, verify_fn=lambda: True)
assert dec.recovered and dec.fallback_used == 'relogin'
print('[PASS] 测试11: 论坛登录过期适配（重新登录成功）')

# 测试12: DOM变化适配（语义定位）
dec = adapt_dom_structure_change(ctx, semantic_locator_available=True)
assert dec.fallback_used == 'semantic_locator'
print('[PASS] 测试12: DOM变化适配（语义定位）')

# 测试13: DOM变化适配（全失效 → 退出）
dec = adapt_dom_structure_change(ctx)
assert dec.action == BoundaryAction.EXIT
print('[PASS] 测试13: DOM变化适配（全失效 → 退出）')

# 测试14: 边界注册表（19个默认条件）
assert len(_BOUNDARY_REGISTRY) == 19, f'应有19个，实际{len(_BOUNDARY_REGISTRY)}'
print(f'[PASS] 测试14: 边界注册表（{len(_BOUNDARY_REGISTRY)}个默认条件）')

# 测试15: check_boundary（无check_fn → INFO）
dec = check_boundary('trae-ide-sandbox-limitation', ctx)
assert dec.level == BoundaryLevel.INFO
print('[PASS] 测试15: check_boundary（无check_fn → INFO）')

# 测试16: 汇总报告
summary = BoundarySummary()
summary.add(BoundaryDecision('b1', BoundaryLevel.FATAL, BoundaryAction.EXIT, 'r1'))
summary.add(BoundaryDecision('b2', BoundaryLevel.WARNING, BoundaryAction.CONTINUE, 'r2'))
summary.add(BoundaryDecision('b3', BoundaryLevel.INFO, BoundaryAction.CONTINUE, 'r3'))
assert summary.total == 3 and summary.fatal_count == 1 and summary.warning_count == 1
assert '共 3 条' in summary.report()
print('[PASS] 测试16: 汇总报告')

print()
print('=' * 50)
print('全部 16 项测试通过！')
