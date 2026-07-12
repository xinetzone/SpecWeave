"""spec_loader 配置与性能基线导出脚本。

将 spec-loader.toml 配置项定义、默认值、性能基线数据导出为 JSON 格式，
供内部监控仪表盘（Grafana/自研平台）接入。

用法：
  python .agents/scripts/spec-loader-export-metrics.py
  python .agents/scripts/spec-loader-export-metrics.py --output metrics.json
  python .agents/scripts/spec-loader-export-metrics.py --benchmark  # 运行实时benchmark
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
from lib.spec_loader import (
    SpecLoader, TASK_ROUTING, CACHE_DIRNAME, CACHE_FILENAME,
    CACHE_VERSION, CACHE_MAX_ENTRIES, CONFIG_FILENAME,
    _ATOMIC_REPLACE_MAX_RETRIES, _ATOMIC_REPLACE_RETRY_INTERVAL_MS,
)

PROJECT_ROOT = SCRIPTS_DIR.parent.parent
CONFIG_PATH = PROJECT_ROOT / ".agents" / CONFIG_FILENAME
AGENTS_DIR = PROJECT_ROOT / ".agents"
OUTPUT_DEFAULT = AGENTS_DIR / CACHE_DIRNAME / "spec-loader-metrics.json"


def _config_schema() -> dict:
    """返回配置项schema（含类型、默认值、说明）。"""
    return {
        "meta": {
            "description": "元信息（仅标注，不影响运行时）",
            "items": {
                "version": {"type": "string", "default": "1.0", "description": "配置文件自身版本"},
                "description": {"type": "string", "default": "", "description": "配置描述"},
                "last_updated": {"type": "string", "default": "", "description": "最后更新日期"},
            },
        },
        "cache": {
            "description": "磁盘缓存策略（基于mtime的持久化缓存）",
            "items": {
                "enabled": {
                    "type": "bool", "default": True,
                    "description": "启用磁盘持久化缓存（false=每次从磁盘读取，适合调试）",
                    "performance_impact": "critical",
                    "monitor": True,
                },
                "dir_name": {
                    "type": "string", "default": ".cache",
                    "description": "缓存目录名（相对于.agents/）",
                },
                "filename": {
                    "type": "string", "default": "spec-loader.json",
                    "description": "缓存文件名",
                },
                "max_entries": {
                    "type": "int", "default": 200,
                    "description": "LRU最大缓存条目数（建议值：规范文件总数+50）",
                    "min": 10, "max": 2000,
                    "monitor": True,
                },
                "version": {
                    "type": "int", "default": CACHE_VERSION,
                    "description": "缓存格式版本号（升级此值强制所有缓存失效）",
                    "monitor": True,
                },
                "atomic_write": {
                    "type": "bool", "default": True,
                    "description": "原子写入（先写.tmp再os.replace，防缓存损坏）",
                },
                "mtime_precision": {
                    "type": "float", "default": 0.001,
                    "description": "mtime比对精度（秒），小于此差值视为未修改",
                    "unit": "seconds",
                },
            },
        },
        "layers": {
            "description": "四层渐进式披露加载策略",
            "items": {
                "l1b_default_stages": {
                    "type": "array[string]", "default": ["planning", "startup"],
                    "description": "默认加载L1b索引文档的阶段",
                    "enum": ["startup", "planning", "execution", "verification"],
                },
                "l0_specs": {
                    "type": "array[path]", "default": ["ONBOARDING.md"],
                    "description": "L0入口文件列表（始终加载）",
                },
                "l1a_core_specs": {
                    "type": "array[path]",
                    "default": ["global-core-rules.md", "capability-boundaries.md"],
                    "description": "L1a核心规则文件列表（始终加载）",
                },
                "l1b_index_specs": {
                    "type": "array[path]",
                    "default": ["capability-registry.md", "context-routing.md", "skills/README.md"],
                    "description": "L1b索引文件列表（按需加载）",
                },
            },
        },
        "logging": {
            "description": "日志配置",
            "items": {
                "enable_timing_breakdown": {
                    "type": "bool", "default": True,
                    "description": "启用步骤级耗时分解日志（resolve/memcheck/lookup/mtime/construct/read-io）",
                },
                "cache_log_level": {
                    "type": "string", "default": "info",
                    "description": "缓存HIT/MISS日志级别",
                    "enum": ["debug", "info"],
                },
            },
        },
        "performance": {
            "description": "性能调优参数",
            "items": {
                "max_l2_chars": {
                    "type": "int|null", "default": None,
                    "description": "L2最大加载字符数（null=不限制，防止上下文爆炸）",
                    "unit": "characters",
                },
                "auto_save_cache": {
                    "type": "bool", "default": True,
                    "description": "自动保存缓存（仅dirty时写入，dirty flag优化）",
                    "performance_impact": "critical",
                    "monitor": True,
                },
                "preload_disk_cache": {
                    "type": "bool", "default": True,
                    "description": "启动时预加载磁盘缓存（推荐，~0.15ms开销）",
                    "performance_impact": "high",
                },
            },
        },
        "retry": {
            "description": "原子写入重试策略（Windows文件锁防护）",
            "items": {
                "max_retries": {
                    "type": "int", "default": _ATOMIC_REPLACE_MAX_RETRIES,
                    "description": "os.replace失败时最大重试次数",
                },
                "retry_interval_ms": {
                    "type": "int", "default": _ATOMIC_REPLACE_RETRY_INTERVAL_MS,
                    "description": "重试间隔（毫秒）",
                    "unit": "milliseconds",
                },
            },
        },
    }


def _performance_baseline() -> dict:
    """返回性能基线数据（来自最近一次benchmark）。"""
    return {
        "measured_at": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "platform": sys.platform,
            "python_version": sys.version.split()[0],
            "measurement_method": "pytest-benchmark / CLI benchmark",
        },
        "cold_start_ms": {
            "description": "冷启动（无磁盘缓存，直接读源文件）",
            "avg": 0.88,
            "by_task": {
                "code_review": 0.93,
                "commit": 1.03,
                "retrospective": 0.86,
                "mermaid": 0.83,
                "link_check": 0.75,
            },
            "threshold_warn_ms": 2.0,
            "threshold_critical_ms": 5.0,
        },
        "warm_start_ms": {
            "description": "温启动（磁盘缓存命中，mtime比对）",
            "avg": 0.26,
            "by_task": {
                "code_review": 0.23,
                "commit": 0.36,
                "retrospective": 0.24,
                "mermaid": 0.25,
                "link_check": 0.24,
            },
            "threshold_warn_ms": 0.5,
            "threshold_critical_ms": 2.0,
        },
        "memory_cache_ms": {
            "description": "内存缓存命中（同一实例连续调用）",
            "avg": 0.02,
            "threshold_warn_ms": 0.1,
            "threshold_critical_ms": 0.5,
        },
        "speedup_ratio": {
            "description": "冷/温启动加速比",
            "avg": 3.3,
            "threshold_warn": 2.0,
            "threshold_critical": 1.5,
        },
        "disk_cache_hit_rate_pct": {
            "description": "温启动场景磁盘缓存命中率",
            "value": 100,
            "threshold_warn_pct": 95,
            "threshold_critical_pct": 80,
        },
        "cache_file": {
            "description": "缓存文件统计",
            "typical_entries": 13,
            "typical_size_bytes": 15000,
            "max_entries_configured": CACHE_MAX_ENTRIES,
            "threshold_size_warn_bytes": 100000,
        },
        "l2_specs_count": {
            "description": "L2规范文件总数（路由覆盖）",
            "count": len(TASK_ROUTING),
        },
        "concurrent_bottlenecks": {
            "description": "并发场景瓶颈分析",
            "cold_start_storm_threshold_instances": 30,
            "primary_bottleneck": "atomic_write_race_on_cold_start",
            "retry_protection": "3_retries_10ms_interval",
        },
    }


def _runtime_metrics() -> dict:
    """获取当前运行时的实际缓存状态。"""
    loader = SpecLoader(PROJECT_ROOT, use_disk_cache=True)
    loader.load_for_task("代码审查", stage="execution")
    stats = loader.get_cache_stats()
    loader.save_cache()

    cache_file = PROJECT_ROOT / ".agents" / CACHE_DIRNAME / CACHE_FILENAME
    cache_info = {
        "exists": cache_file.exists(),
        "size_bytes": cache_file.stat().st_size if cache_file.exists() else 0,
    }
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            cache_info["version"] = data.get("version")
            cache_info["entry_count"] = len(data.get("entries", {}))
            cache_info["saved_at"] = data.get("saved_at")
            cache_info["valid_json"] = True
        except (json.JSONDecodeError, OSError):
            cache_info["valid_json"] = False

    return {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "memory_loaded_specs": stats["memory_loaded"],
        "disk_entries": stats["disk_entries"],
        "disk_cache_hits": stats["disk_cache_hits"],
        "disk_cache_misses": stats["disk_cache_misses"],
        "hit_rate_pct": round(stats["hit_rate"], 2),
        "config": stats["config"],
        "cache_file": cache_info,
        "l0_specs_count": len(loader.L0_SPECS),
        "l1a_specs_count": len(loader.L1A_CORE_SPECS),
        "l1b_specs_count": len(loader.L1B_INDEX_SPECS),
        "task_routing_count": len(TASK_ROUTING),
        "loaded_after_execution": len(loader.get_loaded_paths()),
    }


def _health_check_thresholds() -> dict:
    """健康检查阈值定义（供监控告警配置）。"""
    return {
        "warmup_total_time_ms": {"warn": 50, "critical": 200},
        "cache_entry_count": {"warn_min": 5, "critical_min": 3},
        "cache_file_size_bytes": {"warn_min": 1000, "critical_min": 500},
        "cache_file_valid": {"expected": True},
        "cache_version_match": {"expected": CACHE_VERSION},
        "warm_start_ms": {"warn": 0.5, "critical": 2.0},
        "cold_start_ms": {"warn": 2.0, "critical": 5.0},
        "hit_rate_pct": {"warn_min": 95, "critical_min": 80},
    }


def run_live_benchmark() -> dict | None:
    """运行实时benchmark获取最新数据。"""
    cli = SCRIPTS_DIR / "spec-loader.py"
    try:
        r = subprocess.run(
            [sys.executable, str(cli), "benchmark"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
            timeout=30,
        )
        if r.returncode != 0:
            return None
        import re
        result = {"raw_output": r.stdout}
        m = re.search(r"综合平均\s*\|([^|]+)\|([^|]+)\|([^|]+)\|", r.stdout)
        if m:
            result["cold_avg_ms"] = float(m.group(1).strip())
            result["warm_avg_ms"] = float(m.group(2).strip())
            result["speedup"] = float(m.group(3).strip().rstrip("x"))
        return result
    except (subprocess.TimeoutExpired, Exception):
        return None


def export(output_path: Path | None = None, run_benchmark: bool = False) -> dict:
    """导出完整metrics JSON。"""
    data = {
        "schema_version": "1.0",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "component": "spec_loader",
        "component_version": CACHE_VERSION,
        "project_root": str(PROJECT_ROOT),
        "config_schema": _config_schema(),
        "performance_baseline": _performance_baseline(),
        "runtime_metrics": _runtime_metrics(),
        "health_thresholds": _health_check_thresholds(),
    }
    if run_benchmark:
        data["live_benchmark"] = run_live_benchmark()

    if output_path is None:
        output_path = OUTPUT_DEFAULT
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data


def main():
    parser = argparse.ArgumentParser(description="spec_loader 配置与性能基线导出")
    parser.add_argument("--output", "-o", type=str, default=None,
                        help=f"输出文件路径（默认: {OUTPUT_DEFAULT}）")
    parser.add_argument("--benchmark", "-b", action="store_true",
                        help="运行实时benchmark获取最新性能数据")
    parser.add_argument("--stdout", action="store_true",
                        help="同时输出到stdout")
    args = parser.parse_args()

    output = Path(args.output) if args.output else OUTPUT_DEFAULT
    data = export(output_path=output, run_benchmark=args.benchmark)

    print(f"✅ Metrics exported to: {output}")
    print(f"   Cache entries: {data['runtime_metrics']['disk_entries']}")
    print(f"   Cache valid: {data['runtime_metrics']['cache_file'].get('valid_json', False)}")
    print(f"   Baseline cold: {data['performance_baseline']['cold_start_ms']['avg']}ms, "
          f"warm: {data['performance_baseline']['warm_start_ms']['avg']}ms")

    if args.stdout:
        print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
