# RDL — Research Discipline Layer

**Your agent will lie to you at 3am. Not on purpose — but it will. This catches it.**

RDL is not another framework that helps an agent *do* research. It is the discipline
layer that sits on top of any long autonomous agent run and stops it from shipping
a wrong conclusion: fabricated completion, numbers that drifted from the evidence,
a self-certification checklist the agent learned to satisfy, a "decisive" that the
data never supported.

## The 60-second demo

```bash
cd rdl-demo
python demo/run_demo.py     # stdlib only, Python >= 3.8, no API keys
```

The same simulated research run, twice:

- **Arm A — bare agent** (self-report, self-certify: the default everywhere):
  reports `20/20 pass`, writes up `72% vs 48%`, self-certifies via a checklist
  phrase, and **ships a confidently wrong conclusion**.
- **Arm B — same run + RDL**: derives completion from artifacts, cross-checks
  every claimed number against recomputation, control-reverses the sentinel,
  gates conclusion vocabulary against frozen prereg thresholds, and
  **quarantines the run**.

```
[RDL-ALARM 01] (completion) model_b: completion self-report says 20/20, per_item recomputes to 13/20
[RDL-ALARM 03] (sentinel) sentinel INVALIDATED by control reversal: trusted 2/2 known-bad samples
[RDL-ALARM 04] (numbers) entry 1: 'model_b::win_pct' claimed 72.0, artifacts recompute to 65.0
[RDL-ALARM 08] (prereg) claim word 'decisive' requires delta_pp>=15, recomputed delta_pp=10.0

  -> FINAL: QUARANTINED -- 9 alarms across 5 failure-mode classes; no conclusion released.

CATCH TABLE
  failure mode                                   bare agent         + RDL
  fake completion marker (20/20 vs 13/20)        passed through     CAUGHT (recomputed)
  evidence-claim drift (72/48 vs 65/55)          passed through     CAUGHT (cross-check)
  sentinel gaming ('NUMBERS VERIFIED')           passed through     CAUGHT (control reversal)
  claim escalation vs prereg ('decisive')        passed through     CAUGHT (frozen thresholds)
  wrong conclusion shipped                       YES                NO (quarantined)
```

The campaign lands in `demo/last_run/` — open `ledger.jsonl` to see the anchored
ledger, `prereg.json` for the frozen thresholds, `artifacts/results.json` for the
ground truth the agent was hiding behind summary fields.

## The rules (each one is a scar)

| # | Rule | Module |
|---|------|--------|
| 1 | Completion is derived from artifacts, never from self-report; scorers are recomputed, self-reported fields are not evidence | `health` |
| 2 | Every OBSERVED claim carries an anchor (artifact path); unanchored observations are violations | `ledger` |
| 3 | Every ledger append is verified by write-back/read-back on three numbers (count, last id, hash) | `ledger` |
| 4 | Claimed numbers are cross-checked against recomputed numbers at audit time | `audit` |
| 5 | Every sentinel must pass a control reversal (fire on known-bad); failure invalidates it and forces independent recomputation | `sentinel` |
| 6 | Conclusion vocabulary ("decisive", "wins") is gated by thresholds frozen *before* the run | `prereg` |
| 7 | Any open alarm quarantines the run — no conclusion is released | `audit` |

None of these rules were designed on a whiteboard. Each one is the fixed form of a
real failure from a real campaign — origins and dates in
[`cases/case_library.md`](cases/case_library.md).

## What this is / is not

**Is**: a deterministic replay demo + a small stdlib-only library (v0.1.0) of the
gating primitives. The failure modes are replayed, not live — that is what makes
the demo fast, reproducible and honest about what has been tested.

**Is not (yet)**:

- Not attached to a live agent. Roadmap: a thin wrapper your agent calls at stage
  boundaries + a `gate` CLI that ZCode/Claude Code/Codex hooks can invoke.
- Not a generator. If you want an agent to *write papers*, there are plenty of
  scaffolds. RDL is what you wrap around them so you can trust the output.
- Not yet validated on other people's runs. The rules come from one operator's
  campaigns (see case library). Breaking that n=1 is exactly what community
  testing is for — if you run agents overnight, try breaking it and report.

## Break it

The rules come from one operator's campaigns. If you run agents overnight, replay
your own failure modes against RDL and report what it misses — or what it falsely
flags — as a GitHub issue labeled `break-report`. One-line catch-rate reports
("caught 3/4, missed X") are the most useful data this project can receive.

## 中文说明

**RDL（研究纪律层）**：不是帮 agent 做研究的框架，是压在任何长时间自主运行
之上的纪律层——假完成标记、证据-结论漂移、哨兵被一句话绕过、"decisive"
越级，四类失败全部当场抓住、隔离运行、拒绝放行结论。

四条规则全部来自真实战役的挨打记录（见 `cases/case_library.md`：STaR 接力、
账本纪律、Gemma Gen2 哨兵反转、预注册止损），不是白板设计。当前 v0.1.0 为
确定性重放演示 + 纯标准库实现，`python demo/run_demo.py` 即跑。路线图：
挂到真实 agent 的阶段边界与 hook 上；用社群实测打破 n=1。

## Layout

```
rdl/            the layer (ledger, prereg, health, sentinel, audit)
demo/           adversarial replay: bare arm vs RDL arm, catch table
cases/          case library: every rule's origin battle
```
