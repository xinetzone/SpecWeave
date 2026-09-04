#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 ECharts 单文件可视化：跨实现性能对比柱状图 + 精度误差图"""
import json, os, pathlib

BASE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(BASE, "results")

# 读取本地 echarts.min.js，内联进 HTML 实现完全离线可渲染
_echarts_path = pathlib.Path(BASE) / "echarts.min.js"
if _echarts_path.exists():
    ECHARTS_INLINE = _echarts_path.read_text(encoding="utf-8")
    ECHARTS_TAG = "<script>" + ECHARTS_INLINE + "</script>"
else:
    # 兜底：无本地文件时回退 CDN（需联网）
    ECHARTS_TAG = '<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>'
    print("[warn] echarts.min.js 不存在，回退 CDN（需联网）")

with open(os.path.join(RES, "bench_caffe_ffi.json")) as f: bf = json.load(f)
with open(os.path.join(RES, "bench_caffex.json")) as f: bc = json.load(f)
with open(os.path.join(RES, "cross_ops_comparison.json")) as f: cmp = json.load(f)
with open(os.path.join(RES, "cpu_caffe_ffi.json")) as f: cpuffi = json.load(f)
with open(os.path.join(RES, "cpu_caffex.json")) as f: cpucx = json.load(f)

ops = list(bf["ops"].keys())
ffi_ms = [bf["ops"][o]["mean_ms"] for o in ops]
cx_ms = [bc["ops"][o]["mean_ms"] for o in ops]
ffi_fps = [bf["ops"][o]["fps"] for o in ops]
cx_fps = [bc["ops"][o]["fps"] for o in ops]

# 精度误差（仅对比成功的算子）
err_ops = [r["op"] for r in cmp if r.get("max_abs_err") is not None]
err_vals = [r["max_abs_err"] for r in cmp if r.get("max_abs_err") is not None]

ops_json = json.dumps(ops, ensure_ascii=False)
ffi_ms_json = json.dumps(ffi_ms)
cx_ms_json = json.dumps(cx_ms)
ffi_fps_json = json.dumps(ffi_fps)
cx_fps_json = json.dumps(cx_fps)
err_ops_json = json.dumps(err_ops, ensure_ascii=False)
err_vals_json = json.dumps(err_vals)
err_vals_e = json.dumps([float(v) for v in err_vals])

# CPU 占用率
cpu_labels = json.dumps(["caffe-ffi", "caffex"])
cpu_avg = json.dumps([cpuffi["avg_cpu_pct"], cpucx["avg_cpu_pct"]])
cpu_peak = json.dumps([cpuffi["peak_cpu_pct"], cpucx["peak_cpu_pct"]])
cpu_ncpu = json.dumps([cpuffi["ncpu"], cpucx["ncpu"]])

echarts_tag = ECHARTS_TAG

html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<title>Caffe 两实现（caffe-ffi / caffex）综合对比测试可视化</title>
{echarts_tag}
<style>
  body {{ font-family: "Microsoft YaHei", Arial, sans-serif; margin: 20px; background:#f7f8fa; }}
  h2 {{ color: #1f2d3d; }}
  .chart {{ width: 100%; height: 520px; background:#fff; border-radius:8px; margin-bottom:30px; box-shadow:0 2px 8px rgba(0,0,0,.06); }}
  .note {{ color:#666; font-size:13px; margin-bottom:6px; }}
</style>
</head>
<body>
<h2>Caffe 两实现对比测试可视化</h2>
<p class="note">环境：caffe-ffi (py3.14, caffe-ffi-jupyter 容器) vs caffex (py3.10, caffe-cpu:origin-runtime 容器)。均为 CPU 容器，绝对延迟受容器资源影响，仅作相对参考。</p>

<h3>1. 算子平均延迟对比（ms，30 次迭代均值）</h3>
<div class="chart" id="c1"></div>

<h3>2. 算子吞吐量对比（FPS）</h3>
<div class="chart" id="c2"></div>

<h3>3. 算子精度对比（caffe-ffi vs caffex 最大绝对误差）</h3>
<p class="note">误差为 0 表示精确一致；非零为浮点实现差异（数量级 1e-7 属正常，由不同累加顺序/实现导致）。</p>
<div class="chart" id="c3"></div>

<h3>4. CPU 占用率对比（推理过程平均/峰值，% 相对整机多核）</h3>
<p class="note">通过 /proc 采样推理进程 CPU 占用。caffex 峰值 870% 表明其使用 OpenMP 多核并行（最高 16 核）；caffe-ffi 峰值 70.89% 主要为单/低线程。平均值反映稳态占用。</p>
<div class="chart" id="c4"></div>

<h3>5. 网络级 Top-K 分类一致性（InceptionV1，同一固定输入）</h3>
<p class="note">caffex 输出有限概率、Top-1=#904；caffe-ffi 因权重加载缺陷（A-001）Top-5 概率全为 NaN，Top-K 结果无效、与 caffex 不一致。</p>
<div class="chart" id="c5"></div>

<h3>6. 关键异常提示</h3>
<div style="background:#fff5f5;border-left:4px solid #e02424;padding:14px 16px;border-radius:6px;box-shadow:0 2px 6px rgba(0,0,0,.05)">
<b>异常 A-001</b>：caffe-ffi 的 <code>read_net(proto, caffemodel)</code> 未加载 caffemodel 真实权重（conv1 权重全 1.0/std=0），导致 InceptionV1/MobileNetV2 网络推理输出指数放大至 Inf/NaN。算子级测试（net_from_param 无 caffemodel）不受影响，故算子精度对比仍有效。
</div>

<script>
var ops = {ops_json};
var ffi_ms = {ffi_ms_json};
var cx_ms = {cx_ms_json};
var ffi_fps = {ffi_fps_json};
var cx_fps = {cx_fps_json};
var err_ops = {err_ops_json};
var err_vals = {err_vals_e};

var cpu_labels = {cpu_labels};
var cpu_avg = {cpu_avg};
var cpu_peak = {cpu_peak};
var cpu_ncpu = {cpu_ncpu};

var colors = {{ ffi: '#409EFF', cx: '#67C23A' }};

function mkBar(id, series) {{
  var c = echarts.init(document.getElementById(id));
  c.setOption({{
    tooltip: {{ trigger: 'axis' }},
    legend: {{ data: ['caffe-ffi', 'caffex'] }},
    grid: {{ left: 60, right: 30, bottom: 60, top: 40 }},
    xAxis: {{ type: 'category', data: ops, axisLabel: {{ rotate: 30 }} }},
    yAxis: {{ type: 'value' }},
    series: series
  }});
  return c;
}}

mkBar('c1', [
  {{ name: 'caffe-ffi', type: 'bar', data: ffi_ms, itemStyle: {{ color: colors.ffi }} }},
  {{ name: 'caffex', type: 'bar', data: cx_ms, itemStyle: {{ color: colors.cx }} }}
]);

mkBar('c2', [
  {{ name: 'caffe-ffi', type: 'bar', data: ffi_fps, itemStyle: {{ color: colors.ffi }} }},
  {{ name: 'caffex', type: 'bar', data: cx_fps, itemStyle: {{ color: colors.cx }} }}
]);

var c3 = echarts.init(document.getElementById('c3'));
c3.setOption({{
  tooltip: {{ trigger: 'axis' }},
  grid: {{ left: 80, right: 30, bottom: 60, top: 40 }},
  xAxis: {{ type: 'category', data: err_ops, axisLabel: {{ rotate: 30 }} }},
  yAxis: {{ type: 'log', name: 'log(最大绝对误差)' }},
  series: [{{ name: 'max_abs_err', type: 'bar', data: err_vals, itemStyle: {{ color: '#F56C6C' }} }}]
}});

var c4 = echarts.init(document.getElementById('c4'));
c4.setOption({{
  tooltip: {{ trigger: 'axis' }},
  legend: {{ data: ['平均占用', '峰值占用'] }},
  grid: {{ left: 60, right: 30, bottom: 40, top: 40 }},
  xAxis: {{ type: 'category', data: cpu_labels }},
  yAxis: {{ type: 'value', name: 'CPU 占用率(%)' }},
  series: [
    {{ name: '平均占用', type: 'bar', data: cpu_avg, itemStyle: {{ color: '#409EFF' }} }},
    {{ name: '峰值占用', type: 'bar', data: cpu_peak, itemStyle: {{ color: '#F56C6C' }} }}
  ]
}});

var c5 = echarts.init(document.getElementById('c5'));
c5.setOption({{
  tooltip: {{ trigger: 'item' }},
  grid: {{ left: 60, right: 30, bottom: 40, top: 40 }},
  xAxis: {{ type: 'category', data: ['caffex(有效)', 'caffe-ffi(无效)'] }},
  yAxis: {{ type: 'value', name: 'Top-1 概率' }},
  series: [{{
    name: 'Top-1 概率',
    type: 'bar',
    data: [0.0012, null],
    itemStyle: {{ color: ['#67C23A', '#F56C6C'] }},
    label: {{ show: true, position: 'top', formatter: function(p){{ return p.value == null ? 'NaN' : p.value; }} }}
  }}]
}});

window.addEventListener('resize', function() {{
  var arr = ['c1','c2','c3','c4','c5'];
  arr.forEach(function(id){{ var c = echarts.getInstanceByDom(document.getElementById(id)); if(c) c.resize(); }});
}});
</script>
</body>
</html>"""

out = os.path.join(BASE, "visualization.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print("可视化已生成:", out)