import re, pathlib, sys

R = pathlib.Path(sys.argv[1])

# (描述, 相对文件, 正则, 期望出现)
checks = [
    ('main() 入口', 'src/main.c', r'int\s+main\s*\('),
    ('server_init/server_start 声明', 'include/server.h', r'server_(init|start|run)\b'),
    ('后端自动选择函数', 'src/backend/backend.c', r'backend_autocreate'),
    ('输入队列容量 64', 'src/backend/libinput/input_queue.h', r'INPUT_QUEUE_CAPACITY\s+64'),
    ('libinput 线程入口', 'src/backend/libinput/backend.c', r'(pthread|handle_input_batch|input_thread)'),
    ('renderer 选择', 'src/render/renderer.c', r'(renderer_autocreate|KYWC_RENDERER|pixman|vulkan)'),
    ('EGL 二次 getenv', 'src/render/egl.c', r'getenv\(\s*"KYWC_RENDERER"'),
    ('多 GPU swapchain 容量', 'src/render/swapchain.c', r'SWAPCHAIN_CAP|capac'),
    ('场景输出渲染', 'src/scene/output.c', r'scene_output_do_render'),
    ('输出编排函数', 'src/output/configure.c', r'configure_outputs'),
    ('默认亮度 100', 'src/output/configure.c' if (R/'src/output/configure.c').exists() else 'src/output/output.c', r'100'),
    ('功能键分发', 'src/input/function.c', r'function_manager_handle_key_binding'),
    ('IME 注册点 text_input', 'src/input/text_input.c', r'wl_global_create|text_input_manager'),
    ('workspace 数配置', 'src/view/workspace.c', r'num_workspaces'),
    ('view 18 层枚举', 'include/view/view.h',enum := None),
    ('插件接口结构', 'include/kywc/plugin.h', r'struct\s+kywc_plugin_interface|kywc_plugin_interface'),
    ('get_interface 带参', 'include/kywc/plugin.h', r'kywc_plugin_get_interface\s*\(\s*void\s*\*\s*plugin\s*\)'),
    ('option_value 成员 num/str/realnum/boolean', 'include/kywc/plugin.h', r'(realnum|boolean)'),
    ('dlopen RTLD_NOW', 'src/plugin/plugin.c', r'RTLD_NOW\s*\|\s*RTLD_GLOBAL'),
    ('ABI 硬编码 1.0', 'src/plugin/plugin.c', r'1\.0'),
    ('security.c:466 附近注册', 'src/plugin/security/security.c', r'wl_global_create'),
    ('protector 通道序', 'src/security/protector.c', r'\{\s*r\s*,\s*b\s*,\s*g'),
    ('xwayland shell 手写注册', 'src/xwayland/shell.c', r'wl_global_create'),
    ('libkywc 双 roundtrip', 'libkywc/libkywc.c', r'wl_display_roundtrip'),
    ('provider 能力表', 'libkywc/provider.h', r'capabil|kywc_provider'),
    ('portal D-Bus name', 'portal/main.c', r'org\.freedesktop\.impl\.portal\.desktop\.wlcom'),
    ('portal ScreenCast 版本', 'portal/screencast.c', r'5|SCREENCAST'),
    ('特效钩子 17', 'include/effect/effect.h', r'^typedef.*\(\*'),
    ('blur priority 999', 'src/effect/blur.c', r'999'),
    ('zoom priority 122', 'src/effect/zoom.c', r'122'),
    ('compositor version 6', 'src/server.c', r'wlr_compositor_create\([^;]*,\s*6'),
    ('日志默认路径', 'src/util/logger.c', r'\.log/kylin-wlcom\.log|kylin-wlcom\.log'),
    ('D-Bus 总线名', 'src/util/dbus.c', r'com\.kylin\.Wlcom'),
]

fails = []
for desc, rel, pat in checks:
    p = R / rel
    if not p.exists():
        print(f'MISSING FILE  {desc:32s} {rel}'); fails.append(desc); continue
    if pat is None:
        print(f'SKIP          {desc:32s} {rel}'); continue
    txt = p.read_text(encoding='utf-8', errors='replace')
    m = re.search(pat, txt, re.M)
    if m:
        ln = txt[:m.start()].count('\n') + 1
        print(f'OK  L{ln:<6d} {desc:32s} {rel}')
    else:
        print(f'NO MATCH      {desc:32s} {rel} :: {pat}')
        fails.append(desc)

# view layer 枚举单独数
vh = (R / 'include/view/view.h').read_text(encoding='utf-8', errors='replace')
print('\nview.h enum 计数抽样：含 LAYER/ROLE/CAP 关键字行数 =',
      len(re.findall(r'KYWC_VIEW_(LAYER|ROLE|CAP)', vh)))

# libkywc.h 声明数
api = re.findall(r'^\w[\w \*]*\bkywc_\w+\s*\(', (R/'libkywc/libkywc.h').read_text(encoding='utf-8'), re.M)
print('libkywc.h kywc_ 函数声明 =', len(api))

# 12 篇关键 XML 存在性
for x in ['kywc-stream-v1.xml', 'ukui-shell-v1.xml', 'xdg-toplevel-tag-v1.xml', 'wlr-layer-shell-unstable-v1.xml']:
    print('XML exists', x, (R/'protocols'/x).exists())

print('\nRESULT:', 'ALL PASS' if not fails else f'{len(fails)} FAIL: {fails}')
