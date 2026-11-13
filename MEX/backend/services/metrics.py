import threading
import time
from collections import deque

STAGES = ("capture", "upload", "inference", "total")
WINDOW_SIZE = 500

_lock = threading.Lock()
_samples: dict[str, deque] = {stage: deque(maxlen=WINDOW_SIZE) for stage in STAGES}
_status_counts: dict[str, int] = {"GREEN": 0, "AMBER": 0, "RED": 0, "GRAY": 0}
_started_at = time.time()


def record(latency_ms: dict):
    with _lock:
        for stage in STAGES:
            value = latency_ms.get(stage)
            if value is not None:
                _samples[stage].append(float(value))
        status = latency_ms.get("status")
        if status in _status_counts:
            _status_counts[status] += 1


def _percentile(values, pct):
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(round((pct / 100.0) * (len(ordered) + 1)) - 1)))
    return round(ordered[index], 1)


def snapshot():
    with _lock:
        latencies = {
            stage: {
                "count": len(samples),
                "p50_ms": _percentile(samples, 50),
                "p95_ms": _percentile(samples, 95),
                "p99_ms": _percentile(samples, 99),
            }
            for stage, samples in _samples.items()
        }
        counts = dict(_status_counts)
    return {
        "latency": latencies,
        "inspection_status_counts": counts,
        "targets": {"inference_p95_ms": 2000, "full_flow_p95_ms": 3000},
        "uptime_seconds": round(time.time() - _started_at, 1),
    }


def prometheus_format():
    snap = snapshot()
    lines = ["# HELP mex_latency_ms Latency by stage", "# TYPE mex_latency_ms summary"]
    for stage, stats in snap["latency"].items():
        for pct in ("p50", "p95", "p99"):
            value = stats.get(f"{pct}_ms")
            if value is not None:
                lines.append(f'mex_latency_ms{{stage="{stage}",quantile="{pct[1:]}"}} {value}')
    lines.append("# HELP mex_inspections_total Inspections by status")
    lines.append("# TYPE mex_inspections_total counter")
    for status_name, count in snap["inspection_status_counts"].items():
        lines.append(f'mex_inspections_total{{status="{status_name}"}} {count}')
    return "\n".join(lines) + "\n"
