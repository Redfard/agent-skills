---
name: x-mem-top
description: Use when the question is how RAM is being used on this Linux machine — how much is free, whether it is swapping, or which processes are eating it. Runs one local script that prints a summary plus every process ranked by memory, largest first. Keywords — memory usage, RAM, free memory, out of memory, OOM, who is eating memory, top processes by memory, swap, memory leak.
---

# Memory report

## Overview

`mem-top.py` (next to this file) produces the whole report in one run: a header with
total / used / available / buff-cache / free plus swap, then processes ranked by memory from
largest to smallest, with an `other` row so the tail is never silently dropped.

Sizes follow one rule everywhere in the report: **under 1000 MB → printed in MB, from 1000 MB
up → printed in GB**. One rule means two numbers anywhere in the output are directly
comparable. Kilobytes come from `/proc`, so the base is 1024, same as `free -h`.

Local machine only — it reads `/proc` directly and has no remote mode.

## Run it

| Goal | Command |
|------|---------|
| Standard report (top 15, grouped by process name) | `<skill dir>/mem-top.py` — the script sits next to this file |
| Longer or shorter ranking | `... -n 40` |
| Rank by swap instead of resident memory | `... --sort swap` |
| One row per PID instead of grouped | `... --no-group` |
| Force the metric | `... --metric rss` / `--metric pss` |
| Machine-readable (kB, every row) | `... --json` |

## Reading the output

- **Metric.** The header names it. **PSS** splits shared pages between the processes sharing
  them and is what the run uses when `/proc/*/smaps_rollup` is readable for ~all userspace
  processes — usually root. **RSS** charges shared pages in full to every process, so groups of
  forked workers (php-fpm, apache2, chrome) read high under it. Same machine, two metrics, very
  different top rows: say which one produced the numbers being quoted.
- **Grouping.** A row is all processes sharing an executable name, `PROCS` is how many. Reach
  for `--no-group` when the question is which *instance* grew, not which program.
- **Processes never sum to `used`.** The footer states the gap in the direction it goes:
  `unaccounted` (kernel/slab, tmpfs, page tables — memory no process owns) or `overcount`
  (shared pages counted more than once, expected under RSS). A gap is normal; an unexplained
  one is a finding.
- **Swap.** The `SWAP` column is per process and appears whenever anything is swapped out;
  under PSS it is `SwapPss`, so shared swapped pages are split the same way resident ones are.
  A row with little `MEM` and a lot of `SWAP` was pushed out under past pressure and never came
  back — `--sort swap` puts exactly those on top. The footer says how much of the machine's
  swap living processes account for; the remainder is shmem/tmpfs or processes that have
  since exited. Heavy swap use alongside plenty of `available` means the pressure has passed,
  not that it is happening now.

## Done when

The reply to the user carries, in the reply itself and not only in the tool output:

1. which metric the run used, whenever the ranking is being quoted;
2. the summary line — total, used, available, and swap if any is in use;
3. the ranked rows down to where the remaining rows stop changing the answer;
4. a named cause for the process-total-vs-`used` gap, rather than the gap left unmentioned;
5. when swap is in use, who holds it — a machine-level swap figure with no owner named is half
   an answer;
6. the answer to what was actually asked, which is rarely "here is a table".
