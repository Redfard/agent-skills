#!/usr/bin/env python3
"""RAM report for this Linux machine: summary + processes ranked by memory, largest first.

Sizes follow one rule everywhere: under 1000 MB -> printed in MB, from 1000 MB up -> printed
in GB. Kilobytes come from /proc, so the base is 1024 (same as `free -h`).
"""

import argparse
import json
import os
import re
import sys

PROC = "/proc"
PAGE_KB = os.sysconf("SC_PAGE_SIZE") // 1024


# --------------------------------------------------------------------------- formatting

def fmt(kb):
    """Format kilobytes: MB below 1000 MB, GB from 1000 MB up."""
    mb = kb / 1024.0
    if mb < 1000:
        return f"{mb:.1f} MB" if mb < 10 else f"{mb:.0f} MB"
    return f"{mb / 1024.0:.1f} GB"


def pct(part, whole):
    return 0.0 if whole <= 0 else part * 100.0 / whole


# --------------------------------------------------------------------------- collection

def read_meminfo():
    info = {}
    with open(f"{PROC}/meminfo") as fh:
        for line in fh:
            key, _, rest = line.partition(":")
            parts = rest.split()
            if parts:
                info[key] = int(parts[0])  # kB
    return info


MAX_NAME = 32
VERSIONISH = re.compile(r"^v?[0-9][0-9._-]*$")
GENERIC_DIRS = {"bin", "sbin", "libexec", "versions", "version", "current",
                "releases", "release", "dist", "build", "target", "opt", "usr", "local"}


def proc_name(argv0, comm):
    """Group key: 'php-fpm: pool www' -> php-fpm, '/usr/sbin/mysqld --daemonize' -> mysqld.

    Chrome and node rewrite argv[0] to their whole command line, so keep the first token only.
    A version-named binary (.../claude/versions/2.1.235) takes the nearest meaningful directory,
    otherwise the ranking is full of numbers nobody can read.
    """
    if not argv0:
        return f"[{comm}]"  # kernel thread
    token = argv0.split()[0].split(":")[0]
    name = os.path.basename(token) or comm
    if VERSIONISH.match(name):
        for part in reversed(os.path.dirname(token).split("/")):
            if part and part not in GENERIC_DIRS and not VERSIONISH.match(part):
                name = part
                break
    return name if len(name) <= MAX_NAME else name[:MAX_NAME - 1] + "…"


def read_rollup(pid):
    """(Pss, SwapPss) in kB — both proportional, both from one file. (None, None) if unreadable."""
    pss = swap = None
    try:
        with open(f"{PROC}/{pid}/smaps_rollup") as fh:
            for line in fh:
                if line.startswith("Pss:"):
                    pss = int(line.split()[1])
                elif line.startswith("SwapPss:"):
                    swap = int(line.split()[1])
    except (OSError, ValueError, IndexError):
        return None, None
    return pss, swap


def read_rss(pid):
    try:
        with open(f"{PROC}/{pid}/statm") as fh:
            return int(fh.read().split()[1]) * PAGE_KB
    except (OSError, ValueError, IndexError):
        return 0


def read_vmswap(pid):
    """Whole-process swap, the RSS-side counterpart of SwapPss."""
    try:
        with open(f"{PROC}/{pid}/status") as fh:
            for line in fh:
                if line.startswith("VmSwap:"):
                    return int(line.split()[1])
    except (OSError, ValueError, IndexError):
        pass
    return 0


def collect():
    procs = []
    for entry in os.listdir(PROC):
        if not entry.isdigit():
            continue
        pid = int(entry)
        base = f"{PROC}/{entry}"
        try:
            with open(f"{base}/cmdline", "rb") as fh:
                raw = fh.read().decode("utf-8", "replace")
            with open(f"{base}/comm") as fh:
                comm = fh.read().strip()
        except OSError:
            continue  # process exited mid-scan, or not ours to read
        argv = [a for a in raw.split("\0") if a]
        pss, swap_pss = read_rollup(pid)
        procs.append({
            "pid": pid,
            "name": proc_name(argv[0] if argv else "", comm),
            "cmdline": " ".join(argv) or f"[{comm}]",
            "rss_kb": read_rss(pid),
            "pss_kb": pss,
            "swap_pss_kb": swap_pss,
            "vmswap_kb": read_vmswap(pid),
            "userspace": bool(argv),
        })
    return procs


def pick_metric(requested, procs):
    """PSS splits shared pages between the processes sharing them; RSS charges each in full.

    Kernel threads have no usable smaps_rollup, so only userspace processes get a vote.
    """
    if requested in ("rss", "pss"):
        return requested
    votes = [p for p in procs if p["userspace"]]
    hits = sum(1 for p in votes if p["pss_kb"] is not None)
    return "pss" if votes and hits >= 0.9 * len(votes) else "rss"


def size_of(proc, metric):
    if metric == "pss" and proc["pss_kb"] is not None:
        return proc["pss_kb"]
    return proc["rss_kb"]


def swap_of(proc, metric):
    if metric == "pss" and proc["swap_pss_kb"] is not None:
        return proc["swap_pss_kb"]
    return proc["vmswap_kb"]


# --------------------------------------------------------------------------- report

def build(args):
    mi = read_meminfo()
    total = mi.get("MemTotal", 0)
    free = mi.get("MemFree", 0)
    buffcache = mi.get("Buffers", 0) + mi.get("Cached", 0) + mi.get("SReclaimable", 0)
    available = mi.get("MemAvailable", 0)
    used = max(total - free - buffcache, 0)
    swap_total = mi.get("SwapTotal", 0)
    swap_used = swap_total - mi.get("SwapFree", 0)

    procs = collect()
    metric = pick_metric(args.metric, procs)
    fallbacks = sum(1 for p in procs
                    if metric == "pss" and p["userspace"] and p["pss_kb"] is None)

    for p in procs:
        p["mem_kb"] = size_of(p, metric)
        p["swap_kb"] = swap_of(p, metric)

    if args.no_group:
        rows = [{
            "name": p["name"], "pid": p["pid"], "cmdline": p["cmdline"],
            "mem_kb": p["mem_kb"], "swap_kb": p["swap_kb"], "count": 1,
        } for p in procs]
    else:
        grouped = {}
        for p in procs:
            row = grouped.setdefault(p["name"], {
                "name": p["name"], "pid": None, "cmdline": p["cmdline"],
                "mem_kb": 0, "swap_kb": 0, "count": 0,
            })
            row["mem_kb"] += p["mem_kb"]
            row["swap_kb"] += p["swap_kb"]
            row["count"] += 1
        rows = list(grouped.values())

    key = "swap_kb" if args.sort == "swap" else "mem_kb"
    rows.sort(key=lambda r: (-r[key], r["name"]))
    proc_total = sum(r["mem_kb"] for r in rows)
    swap_by_procs = sum(r["swap_kb"] for r in rows)

    return {
        "host": os.uname().nodename,
        "metric": metric,
        "metric_fallbacks": fallbacks,
        "sorted_by": args.sort,
        "process_count": len(procs),
        "memory_kb": {
            "total": total, "used": used, "available": available,
            "free": free, "buff_cache": buffcache,
            "swap_total": swap_total, "swap_used": swap_used,
        },
        "processes_total_kb": proc_total,
        "processes_swap_kb": swap_by_procs,
        "unaccounted_kb": used - proc_total,
        "rows": rows,
    }


METRIC_NOTE = {
    "pss": "PSS (shared pages, swap included, split between the processes sharing them)",
    "rss": "RSS (shared pages charged in full to every process)",
}


def render(rep, limit, no_group):
    m = rep["memory_kb"]
    out = []
    note = METRIC_NOTE[rep["metric"]]
    if rep["metric_fallbacks"]:
        note += f", {rep['metric_fallbacks']} process(es) fell back to RSS"
    out.append(f"HOST  {rep['host']}   metric: {note}")
    out.append(
        f"RAM   {fmt(m['total'])} total | {fmt(m['used'])} used "
        f"({pct(m['used'], m['total']):.0f}%) | {fmt(m['available'])} available | "
        f"{fmt(m['buff_cache'])} buff/cache | {fmt(m['free'])} free"
    )
    if m["swap_total"]:
        out.append(
            f"SWAP  {fmt(m['swap_total'])} total | {fmt(m['swap_used'])} used "
            f"({pct(m['swap_used'], m['swap_total']):.0f}%)"
        )
    else:
        out.append("SWAP  none")
    if rep["sorted_by"] == "swap":
        out.append("      ranked by swap, largest first")
    out.append("")

    rows = rep["rows"][:limit]
    rest = rep["rows"][limit:]
    show_swap = any(r["swap_kb"] > 0 for r in rep["rows"])
    name_w = max([len(r["name"]) for r in rows] + [7])
    mem_w = max([len(fmt(r["mem_kb"])) for r in rows] + [3])
    swap_w = max([len(fmt(r["swap_kb"])) for r in rows] + [4]) if show_swap else 0

    head = f"{'#':>3}  "
    if no_group:
        head += f"{'PID':>7}  "
    head += f"{'PROCESS':<{name_w}}  {'MEM':>{mem_w}}  {'%RAM':>6}"
    if show_swap:
        head += f"  {'SWAP':>{swap_w}}"
    if not no_group:
        head += "  PROCS"
    out.append(head)

    def body(rank, label, mem_kb, swap_kb, count, pid=None):
        line = f"{rank:>3}  "
        if no_group:
            line += f"{pid if pid is not None else '':>7}  "
        line += f"{label:<{name_w}}  {fmt(mem_kb):>{mem_w}}  {pct(mem_kb, m['total']):>5.1f}%"
        if show_swap:
            line += f"  {(fmt(swap_kb) if swap_kb else '-'):>{swap_w}}"
        if not no_group:
            line += f"  {count:>5}"
        return line

    for i, r in enumerate(rows, 1):
        out.append(body(i, r["name"], r["mem_kb"], r["swap_kb"], r["count"], r["pid"]))

    if rest:
        out.append(body("", f"other ({len(rest)} rows)",
                        sum(r["mem_kb"] for r in rest), sum(r["swap_kb"] for r in rest),
                        sum(r["count"] for r in rest)))

    out.append("")
    out.append(
        f"processes: {fmt(rep['processes_total_kb'])} across {rep['process_count']} "
        f"processes ({pct(rep['processes_total_kb'], m['total']):.1f}% of RAM)"
    )
    gap = rep["unaccounted_kb"]
    if gap >= 0:
        out.append(f"unaccounted: {fmt(gap)} of 'used' sits outside processes "
                   f"(kernel/slab, tmpfs, page tables)")
    else:
        out.append(f"overcount: processes exceed 'used' by {fmt(-gap)} "
                   f"({'shared pages counted more than once' if rep['metric'] == 'rss' else 'tmpfs/shmem attributed to processes'})")

    if m["swap_used"]:
        held = rep["processes_swap_kb"]
        line = (f"swap: living processes hold {fmt(held)} of the {fmt(m['swap_used'])} in use "
                f"({pct(held, m['swap_used']):.0f}%)")
        if pct(held, m["swap_used"]) < 90:
            line += " — the rest belongs to shmem/tmpfs or to processes that have since exited"
        out.append(line)
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-n", "--limit", type=int, default=15, help="rows to show (default 15)")
    ap.add_argument("--no-group", action="store_true",
                    help="one row per PID instead of grouping by process name")
    ap.add_argument("--metric", choices=["auto", "pss", "rss"], default="auto",
                    help="auto (default) uses PSS when readable for ~all processes, else RSS")
    ap.add_argument("--sort", choices=["mem", "swap"], default="mem",
                    help="rank by resident memory (default) or by swapped-out memory")
    ap.add_argument("--json", action="store_true",
                    help="machine-readable output (sizes in kB, every row regardless of -n)")
    args = ap.parse_args()

    if not os.path.isdir(PROC):
        sys.exit("no /proc — this script only reads a live Linux machine")

    rep = build(args)
    if args.json:
        print(json.dumps(rep, indent=2))
    else:
        print(render(rep, args.limit, args.no_group))


if __name__ == "__main__":
    main()
