import time

_prev_cpu: tuple | None = None

def _read_cpu_times() -> tuple[int, int]:
    with open("/proc/stat") as f:
        fields = list(map(int, f.readline().split()[1:8]))
    # fields: user, nice, system, idle, iowait, irq, softirq
    idle  = fields[3] + fields[4]   # idle + iowait
    total = sum(fields)
    return idle, total

def _cpu_percent() -> float:
    global _prev_cpu
    idle, total = _read_cpu_times()
    if _prev_cpu is None:
        _prev_cpu = (idle, total)
        time.sleep(0.1)
        idle, total = _read_cpu_times()
    prev_idle, prev_total = _prev_cpu
    _prev_cpu = (idle, total)
    diff_total = total - prev_total
    if diff_total == 0:
        return 0.0
    return round((1 - (idle - prev_idle) / diff_total) * 100, 1)

def _memory_percent() -> float:
    mem: dict[str, int] = {}
    with open("/proc/meminfo") as f:
        for line in f:
            key, val = line.split(":", 1)
            mem[key.strip()] = int(val.strip().split()[0])
    used = mem["MemTotal"] - mem["MemAvailable"]
    return round(used / mem["MemTotal"] * 100, 1)

def get_system_stats() -> dict:
    return {
        "cpu":    _cpu_percent(),
        "memory": _memory_percent(),
    }