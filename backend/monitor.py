import time
import sys

# ── CPU ───────────────────────────────────────────────────────────────────────

_prev_cpu: tuple | None = None

if sys.platform == "win32":
    import ctypes
    import ctypes.wintypes

    class _FILETIME(ctypes.Structure):
        _fields_ = [("dwLowDateTime", ctypes.wintypes.DWORD),
                    ("dwHighDateTime", ctypes.wintypes.DWORD)]

    def _read_cpu_times() -> tuple[int, int]:
        """Return (idle_ticks, total_ticks) via GetSystemTimes()."""
        idle = _FILETIME()
        kernel = _FILETIME()
        user = _FILETIME()
        ctypes.windll.kernel32.GetSystemTimes(
            ctypes.byref(idle),
            ctypes.byref(kernel),
            ctypes.byref(user),
        )
        def to_int(ft):
            return (ft.dwHighDateTime << 32) | ft.dwLowDateTime

        idle_ticks   = to_int(idle)
        # kernel time includes idle time on Windows
        total_ticks  = to_int(kernel) + to_int(user)
        return idle_ticks, total_ticks

    def _memory_percent() -> float:
        """Return memory usage % via GlobalMemoryStatusEx()."""
        class _MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength",                ctypes.wintypes.DWORD),
                ("dwMemoryLoad",            ctypes.wintypes.DWORD),
                ("ullTotalPhys",            ctypes.c_uint64),
                ("ullAvailPhys",            ctypes.c_uint64),
                ("ullTotalPageFile",        ctypes.c_uint64),
                ("ullAvailPageFile",        ctypes.c_uint64),
                ("ullTotalVirtual",         ctypes.c_uint64),
                ("ullAvailVirtual",         ctypes.c_uint64),
                ("ullAvailExtendedVirtual", ctypes.c_uint64),
            ]
        stat = _MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(stat)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
        return float(stat.dwMemoryLoad)

else:
    # Linux / macOS fallback
    def _read_cpu_times() -> tuple[int, int]:
        with open("/proc/stat") as f:
            fields = list(map(int, f.readline().split()[1:8]))
        idle  = fields[3] + fields[4]
        total = sum(fields)
        return idle, total

    def _memory_percent() -> float:
        mem: dict[str, int] = {}
        with open("/proc/meminfo") as f:
            for line in f:
                key, val = line.split(":", 1)
                mem[key.strip()] = int(val.strip().split()[0])
        used = mem["MemTotal"] - mem["MemAvailable"]
        return round(used / mem["MemTotal"] * 100, 1)


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


# ── Public API ────────────────────────────────────────────────────────────────

def get_system_stats() -> dict:
    return {
        "cpu":    _cpu_percent(),
        "memory": _memory_percent(),
    }