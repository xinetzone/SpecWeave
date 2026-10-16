# 开工基线计数（主会话，2026-10-14，PowerShell 7）

> 信源：external/dao/action/kylin-wayland-compositor @ 4df656222427f3cd0101e41d828fb64805e66c15（openkylin/huanghe，干净工作树，距 build/1.3.1-ok21 761 提交）。
> 口径：Get-ChildItem -Recurse -Include；全部排除 build/（仓库无 build 目录检出）。V 阶段须换独立手段复算。

| 指标 | 值 | 命令口径 |
|---|---|---|
| 全仓 *.c/*.h | 465 | 递归 -Include *.c,*.h |
| 全仓行数 | 138417 | Get-Content \| Measure-Object -Line 求和（行数=换行符数，末行无换行则少计 1） |
| src/ 15 子目录合计 | 281 | backend34 config9 effect41 input35 output13 painter4 plugin5 render26 scene17 security6 theme5 util24 view42 widget4 xwayland16 |
| src/ 根文件 | 2 | main.c, server.c |
| libkywc/ C/H | 17 | 递归 |
| portal/ C/H | 14 | 递归 |
| examples/ C/CPP/H | 34 | 递归 -Include *.c,*.cpp,*.h |
| protocols/*.xml | 34 | 目录直挂 *.xml（visual LS 曾误数 27，以脚本为准） |
| src/effect/*.c | 40 | 目录直挂 .c；加 effect_p.h 共 41 C/H |
| effect shaders | 14 | shaders/ 下 *.frag+*.vert（7 对） |
| drm shaders | 5 文件 | tex.frag/tex.vert/tex_oes.frag/tex_yuv.frag + meson.build |
| po/LINGUAS 条目 | 16 | 非空行数 |
| po/*.po 文件 | 27 | 目录直挂 |
| meson_options option() | 44 | Select-String 'option\(' meson_options.txt |
| data/ 文件 | 9（+udev-rules/） | 目录直挂 |
| src/plugin/ | 9 文件 | config.c/interface.c/plugin.c/plugin_p.h/meson.build + security/{gui.cpp,security.c,security.xml,meson.build} |
| tools/ | 存在 | 待 R1 列清单 |
