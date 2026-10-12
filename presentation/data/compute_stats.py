"""Read-only statistics for the course presentation.

Reads local runs, origin/hayati summaries (via git show) and the amber run ledger.
Writes stats.json and STATS.md into presentation/data/.
"""
import collections
import glob
import json
import os
import re
import statistics
import subprocess
from pathlib import Path

ROOT = Path(r"C:\Users\Admin\Desktop\Agentic AI in Modern Business (MGTHN0211)")
REPO = ROOT / "androidworld-gui-agent"
RUNS = REPO / "runs"
LEDGER = ROOT / "amber_agent_integration_20261008" / "evidence" / "RUN_LEDGER_20261008.md"
OUT = ROOT / "presentation" / "data"
FINAL_BATCHES = ["eval_batch_20261008T215129_132839Z", "eval_batch_20261008T223002_941777Z"]
# Markor + SMS was re-evaluated with v66 (Skill: Share > Plain Text instead of typing the text again);
# its three runs replace the v65 Markor runs in the final set. v66 changed only the Markor Skill.
MARKOR_BATCH = "eval_batch_20261009T125038_033286Z"
EUR_PER_MTOK = 0.045
REF_STEPS = {
    "SystemWifiTurnOn": 3, "ContactsAddContact": 5, "SimpleSmsSend": 6, "FilesMoveFile": 10,
    "SimpleCalendarAddOneEvent": 17, "MarkorCreateNoteAndSms": 9, "OsmAndTrack": 60,
}
TASK_ORDER = ["SystemWifiTurnOn", "ContactsAddContact", "SimpleSmsSend", "FilesMoveFile",
              "SimpleCalendarAddOneEvent", "MarkorCreateNoteAndSms", "OsmAndTrack"]
C = collections.Counter


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def vnum(version):
    if not version:
        return None
    m = re.search(r"_v(\d+)", version)
    return int(m.group(1)) if m else None


def vfamily(version):
    if not version:
        return None
    m = re.match(r"(.*?)_v\d+", version)
    return m.group(1) if m else version


def outcome3(verifier):
    return verifier if verifier in ("PASS", "FAIL") else "other"


def git(*args):
    r = subprocess.run(["git", *args], cwd=REPO, capture_output=True, encoding="utf-8")
    if r.returncode != 0:
        raise RuntimeError(r.stderr)
    return r.stdout


def rnd(x, n=2):
    return None if x is None else round(x, n)


# ---------------------------------------------------------------- local runs
local_dirs = sorted(p for p in RUNS.glob("trial_*") if p.is_dir())
local, local_nosummary = [], []
for d in local_dirs:
    task = d.name.split("_")[1]
    if (d / "summary.json").exists():
        s = load(d / "summary.json")
        s["_dir"] = d.name
        s["_task"] = task
        assert s.get("task") == task, d
        local.append(s)
    else:
        cfg = load(d / "config.json") if (d / "config.json").exists() else {}
        local_nosummary.append({"run": d.name, "task": task, "version": cfg.get("version")})


def run_model_files(run_dir):
    resp = sorted(run_dir.glob("step_*/*/response_*.json"))
    verr = sorted(run_dir.glob("step_*/*/validation_error_*.json"))
    return resp, verr


def token_stats(run_dir):
    resp, verr = run_model_files(run_dir)
    pt = ct = 0
    walls = []
    for f in resp:
        r = load(f)
        pt += r["usage"]["prompt_tokens"]
        ct += r["usage"]["completion_tokens"]
        walls.append(r["wall_seconds"])
    errs = [str(load(f).get("error")) for f in verr]
    return {"prompt": pt, "completion": ct, "responses": len(resp), "walls": walls, "verrs": errs}


# ---------------------------------------------------------------- hayati runs
hay_dirs = git("ls-tree", "-d", "--name-only", "origin/hayati", "runs/").split()
hay_pres = git("ls-tree", "-d", "--name-only", "origin/hayati", "runs/presentation/").split()
hay_files = set(git("ls-tree", "-r", "--name-only", "origin/hayati", "runs/").splitlines())
hay_raw = {}
for d in hay_dirs + hay_pres:
    p = d + "/summary.json"
    if p in hay_files:
        hay_raw[d] = json.loads(git("show", f"origin/hayati:{p}"))
hay_nosummary = [d for d in hay_dirs if d not in hay_raw]
top_by_id = {s.get("run_id"): d for d, s in hay_raw.items() if not d.startswith("runs/presentation/") and s.get("run_id")}
pres_dups = []
for d in hay_pres:
    if d in hay_raw:
        rid = hay_raw[d].get("run_id")
        top = top_by_id.get(rid)
        pres_dups.append({"presentation_dir": d, "run_id": rid, "duplicate_of": top,
                          "identical_content": top is not None and hay_raw[top] == hay_raw[d]})
hay_nontrial = [d for d, s in hay_raw.items() if not d.startswith("runs/presentation/") and s.get("kind") != "learning_trial"]
hayati = []
for d, s in hay_raw.items():
    if d.startswith("runs/presentation/") or s.get("kind") != "learning_trial":
        continue
    s = dict(s)
    s["_dir"] = d.split("/")[-1]
    s["_task"] = s["_dir"].split("_")[1]
    assert s.get("task") == s["_task"], d
    hayati.append(s)
hay_ids = {s["_dir"] for s in hayati}
hay_renamed = sorted(s["_dir"] for s in hayati if not re.search(r"\d{8}T\d{6}", s["_dir"]))
hay_runid_counts = C(s.get("run_id") for s in hayati)
assert all(v == 1 for v in hay_runid_counts.values())
local_ids = {s["_dir"] for s in local} | {x["run"] for x in local_nosummary}

# ---------------------------------------------------------------- ledger
ledger_rows = []
text = LEDGER.read_text(encoding="utf-8")
section = text.split("## Every real attempt", 1)[1]
for line in section.splitlines():
    if not line.startswith("| ") or line.startswith("| Task") or line.startswith("| ---"):
        continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    task, runno, folder, _start, _model, _obs, _gr, steps_budget, result, fclass = cells[:10]
    res = re.sub(r"[*]", "", result).strip()
    outcome = res.split()[0]
    steps = int(steps_budget.split("/")[0].strip())
    ledger_rows.append({"task": task, "run": folder.strip("`"), "steps": steps, "result": outcome,
                        "failure_class": fclass})
led_ts = {re.search(r"(\d{8}T\d{6})", r["run"]).group(1) for r in ledger_rows}
other_ts = set()
for x in hay_ids | local_ids:
    m = re.search(r"(\d{8}T\d{6})", x)
    if m:
        other_ts.add(m.group(1))
    else:
        print("no timestamp in run id:", x)
ledger_overlap = sorted(led_ts & other_ts)


# ---------------------------------------------------------------- A. recorded runs
def tally(rows, key_outcome, key_task):
    by_task = collections.defaultdict(C)
    tot = C()
    for r in rows:
        o = key_outcome(r)
        by_task[key_task(r)][o] += 1
        tot[o] += 1
    return {"total": sum(tot.values()), "PASS": tot["PASS"], "FAIL": tot["FAIL"], "other": tot["other"],
            "per_task": {t: {"total": sum(c.values()), "PASS": c["PASS"], "FAIL": c["FAIL"], "other": c["other"]}
                         for t, c in sorted(by_task.items())}}


A_local = tally(local, lambda r: outcome3(r["verifier"]), lambda r: r["_task"])
A_hay = tally(hayati, lambda r: outcome3(r["verifier"]), lambda r: r["_task"])
A_led = tally(ledger_rows, lambda r: outcome3(r["result"]), lambda r: r["task"])
A_comb = tally(
    [{"o": outcome3(r["verifier"]), "t": r["_task"]} for r in local + hayati]
    + [{"o": outcome3(r["result"]), "t": r["task"]} for r in ledger_rows],
    lambda r: r["o"], lambda r: r["t"])
local_other = C(r["verifier"] for r in local if outcome3(r["verifier"]) == "other")
hay_other = C(r["verifier"] for r in hayati if outcome3(r["verifier"]) == "other")
led_other = C(r["result"] for r in ledger_rows if outcome3(r["result"]) == "other")


def version_info(rows):
    vers = [r.get("version") for r in rows]
    distinct = sorted({v for v in vers if v})
    fam = collections.defaultdict(set)
    for v in distinct:
        n = vnum(v)
        if n is not None:
            fam[vfamily(v)].add(n)
    return {"distinct_version_strings": len(distinct),
            "runs_without_version": sum(1 for v in vers if not v),
            "families": {f: {"distinct_strings": sum(1 for v in distinct if vfamily(v) == f),
                             "range": f"v{min(ns)}..v{max(ns)}"} for f, ns in sorted(fam.items())}}


V_local = version_info(local)
V_hay = version_info(hayati)
all_local_strings = {r.get("version") for r in local if r.get("version")}
all_hay_strings = {r.get("version") for r in hayati if r.get("version")}
V_comb_distinct = len(all_local_strings | all_hay_strings)
V_shared = sorted(all_local_strings & all_hay_strings)

# ---------------------------------------------------------------- B. final evaluation
final_entries = []
for b in FINAL_BATCHES:
    for e in load(RUNS / b / "results.json"):
        if e["task"] != "MarkorCreateNoteAndSms":
            final_entries.append((b, e))
for e in load(RUNS / MARKOR_BATCH / "results.json"):
    final_entries.append((MARKOR_BATCH, e))
assert len(final_entries) == 21, len(final_entries)
final_runs = []
for b, e in final_entries:
    rid = e["run_id"]
    s = load(RUNS / rid / "summary.json")
    ts = token_stats(RUNS / rid)
    assert s["verifier"] == e["verifier"], rid
    final_runs.append({"batch": b, "run_id": rid, "task": s["task"], "seed": e.get("task_seed"),
                       "verifier": s["verifier"], "agent_done": s["agent_done"], "steps": s["steps"],
                       "duration_s": s["duration_seconds"], "version": s["version"],
                       "model_calls": s.get("model_calls_attempted"), "responses": ts["responses"],
                       "prompt_tokens": ts["prompt"], "completion_tokens": ts["completion"],
                       "walls": ts["walls"], "validation_errors": ts["verrs"],
                       "stop_reason": s.get("stop_reason"), "error_class": s.get("error_class"),
                       "failure_class": s.get("failure_class")})


def verr_category(msg):
    m = msg
    if "Expected exactly one do(" in m:
        return "malformed reply (not exactly one do/finish)"
    if "Unsupported action" in m:
        return "unsupported action"
    if "Truncated model reply" in m:
        return "truncated model reply"
    if "No focused editable field" in m or "No text field is focused" in m:
        return "unfocused Type"
    if "Favorite" in m:
        return "OsmAnd: Add would save a Favorite"
    if "SHOW ON MAP" in m:
        return "OsmAnd: SHOW ON MAP"
    if "Type only the search term" in m:
        return "other: OsmAnd search term must stop before comma"
    if "This row is not the place itself" in m or "This row is a Building" in m:
        return "other: OsmAnd wrong search-result row"
    if m.startswith("Launch app"):
        return "other: unavailable Launch app name"
    if m.startswith("Coordinates must"):
        return "other: bad coordinates"
    return "other: OsmAnd route guard (Add/Route)" if ("map centre" in m or "Route opens" in m) else "other: misc"


final_by_task = {}
for t in TASK_ORDER:
    rs = [r for r in final_runs if r["task"] == t]
    if not rs:
        continue
    st = [r["steps"] for r in rs]
    final_by_task[t] = {
        "runs": len(rs), "PASS": sum(r["verifier"] == "PASS" for r in rs),
        "steps_mean": rnd(statistics.mean(st)), "steps_min": min(st), "steps_max": max(st),
        "duration_mean_s": rnd(statistics.mean(r["duration_s"] for r in rs), 1),
        "prompt_tokens": sum(r["prompt_tokens"] for r in rs),
        "completion_tokens": sum(r["completion_tokens"] for r in rs),
        "model_calls": sum(r["model_calls"] for r in rs),
        "validation_errors": sum(len(r["validation_errors"]) for r in rs),
    }
all_walls = [w for r in final_runs for w in r["walls"]]
fin_pt = sum(r["prompt_tokens"] for r in final_runs)
fin_ct = sum(r["completion_tokens"] for r in final_runs)
final_tot = {
    "runs": len(final_runs), "PASS": sum(r["verifier"] == "PASS" for r in final_runs),
    "steps_total": sum(r["steps"] for r in final_runs),
    "steps_mean": rnd(statistics.mean(r["steps"] for r in final_runs)),
    "duration_total_s": rnd(sum(r["duration_s"] for r in final_runs), 1),
    "duration_mean_s": rnd(statistics.mean(r["duration_s"] for r in final_runs), 1),
    "prompt_tokens": fin_pt, "completion_tokens": fin_ct, "total_tokens": fin_pt + fin_ct,
    "model_calls": sum(r["model_calls"] for r in final_runs),
    "response_files": sum(r["responses"] for r in final_runs),
    "cost_eur": round((fin_pt + fin_ct) / 1e6 * EUR_PER_MTOK, 4),
    "model_call_wall_s_median": rnd(statistics.median(all_walls), 3),
    "model_call_wall_s_mean": rnd(statistics.mean(all_walls), 3),
    "validation_error_files": sum(len(r["validation_errors"]) for r in final_runs),
}
refusal_cats = C(verr_category(m) for r in final_runs for m in r["validation_errors"])
refusals_per_run = [{"run_id": r["run_id"], "task": r["task"], "verifier": r["verifier"],
                     "validation_errors": len(r["validation_errors"])} for r in final_runs]
final_fail_detail = [{k: r[k] for k in ("run_id", "task", "seed", "verifier", "agent_done", "steps",
                                       "stop_reason", "error_class", "failure_class")}
                     for r in final_runs if r["verifier"] != "PASS"]

# ---------------------------------------------------------------- C. whole local project
c_pt = c_ct = c_resp = 0
c_walls = []
c_verr = 0
for d in local_dirs:
    ts = token_stats(d)
    c_pt += ts["prompt"]; c_ct += ts["completion"]; c_resp += ts["responses"]
    c_walls += ts["walls"]; c_verr += len(ts["verrs"])
C_local = {
    "run_folders": len(local_dirs), "runs_with_summary": len(local),
    "prompt_tokens": c_pt, "completion_tokens": c_ct, "total_tokens": c_pt + c_ct,
    "cost_eur": round((c_pt + c_ct) / 1e6 * EUR_PER_MTOK, 4),
    "model_response_files": c_resp,
    "model_calls_attempted_sum_from_summaries": sum(r.get("model_calls_attempted") or 0 for r in local),
    "steps_total_from_summaries": sum(r.get("steps") or 0 for r in local),
    "run_time_hours_from_summaries": round(sum(r["duration_seconds"] for r in local) / 3600, 2),
    "model_wall_hours": round(sum(c_walls) / 3600, 2),
    "validation_error_files": c_verr,
}


# ---------------------------------------------------------------- D. outcome categories
def categorize(r):
    if r.get("verifier") == "PASS":
        return "PASS"
    if r.get("agent_done") is True and r.get("verifier") == "FAIL":
        return "false completion (model finished, verifier FAIL)"
    ec = r.get("error_class")
    if ec == "control_no_progress":
        return "stopped by no-progress guard"
    if ec == "validation_error":
        return "validation_error stop"
    if r.get("stop_reason") == "step_budget":
        return "step budget exhausted"
    return "infrastructure/other"


def other_key(r):
    ec = r.get("error_class")
    if ec:
        return ec
    return f"no error_class, stop_reason={r.get('stop_reason')}"


def D_for(rows):
    cats = C(categorize(r) for r in rows)
    infra = C(other_key(r) for r in rows if categorize(r) == "infrastructure/other")
    infra_msgs = C()
    for r in rows:
        if categorize(r) == "infrastructure/other":
            e = (r.get("error") or r.get("recording_error") or "").strip()
            last = e.splitlines()[-1][:90] if e else ""
            infra_msgs[f"{other_key(r)} | {last}"] += 1
    pass_stops = C(f"stop_reason={r.get('stop_reason')}, agent_done={r.get('agent_done')}" for r in rows if r.get("verifier") == "PASS")
    return {"total": len(rows), "categories": dict(cats), "infrastructure_other_by_error_class": dict(infra),
            "infrastructure_other_by_message": dict(infra_msgs.most_common()),
            "PASS_by_stop": dict(pass_stops),
            "stop_reason_values": dict(C(str(r.get("stop_reason")) for r in rows)),
            "error_class_values": dict(C(str(r.get("error_class")) for r in rows))}


D_local = D_for(local)
D_hay = D_for(hayati)
hay_repeat_in_env = sum(1 for r in hayati if r.get("error_class") == "environment_or_execution_error"
                        and "Repeated action without visible effect" in (r.get("error") or "") and r.get("verifier") != "PASS")

# ---------------------------------------------------------------- E. OsmAnd history
RANGES = [(30, 42), (43, 48), (49, 58), (59, 62), (63, 65)]
osm = [r for r in local if r["_task"] == "OsmAndTrack"]
E_ranges = []
for lo, hi in RANGES:
    rs = [r for r in osm if vnum(r["version"]) is not None and lo <= vnum(r["version"]) <= hi]
    E_ranges.append({"range": f"v{lo}-v{hi}", "runs": len(rs), "PASS": sum(r["verifier"] == "PASS" for r in rs),
                     "versions": sorted({vnum(r["version"]) for r in rs})})
osm_unranged = [r["_dir"] for r in osm if not any(lo <= (vnum(r["version"]) or -1) <= hi for lo, hi in RANGES)]
E_batches = []
for b in sorted(RUNS.glob("eval_batch_*")):
    res = load(b / "results.json")
    o = [e for e in res if e.get("task") == "OsmAndTrack"]
    if o:
        E_batches.append({"batch": b.name, "osmand_runs": len(o), "PASS": sum(e.get("verifier") == "PASS" for e in o),
                          "FAIL": sum(e.get("verifier") == "FAIL" for e in o),
                          "ERROR_or_other": sum(e.get("verifier") not in ("PASS", "FAIL") for e in o),
                          "versions": sorted({e.get("version") for e in o if e.get("version")})})

# ---------------------------------------------------------------- F. forwarder crash dialog
F_rows = []
for r in osm:
    n = vnum(r["version"])
    if n is None or n < 49:
        continue
    d = RUNS / r["_dir"]
    hit_keeps = hit_close = False
    steps_hit = set()
    for f in list(d.glob("step_*/*/response_0.json")) + list(d.glob("step_*/*/tree.json")):
        t = f.read_text(encoding="utf-8", errors="replace")
        if "keeps stopping" in t:
            hit_keeps = True
            steps_hit.add(f.parent.parent.name)
    for f in d.glob("step_*/*/response_*.json"):
        content = " ".join(ch.get("message", {}).get("content") or "" for ch in load(f).get("choices", []))
        if "close app" in content.lower():
            hit_close = True
            steps_hit.add(f.parent.parent.name)
    F_rows.append({"run": r["_dir"], "version": n, "verifier": r["verifier"], "keeps_stopping": hit_keeps,
                   "close_app_reply": hit_close, "steps_with_dialog": len(steps_hit)})
F_any = [x for x in F_rows if x["keeps_stopping"] or x["close_app_reply"]]
final_osm_ids = {r["run_id"] for r in final_runs if r["task"] == "OsmAndTrack"}
F_summary = {
    "osmand_runs_v49_plus": len(F_rows),
    "runs_with_dialog": len(F_any),
    "share": rnd(len(F_any) / len(F_rows), 3) if F_rows else None,
    "runs_with_keeps_stopping_text": sum(x["keeps_stopping"] for x in F_rows),
    "runs_with_close_app_reply": sum(x["close_app_reply"] for x in F_rows),
    "dialog_runs_PASS": sum(x["verifier"] == "PASS" for x in F_any),
    "no_dialog_runs_PASS": sum(x["verifier"] == "PASS" for x in F_rows if x not in F_any),
    "no_dialog_runs": len(F_rows) - len(F_any),
    "final_eval_osmand_runs_with_dialog": sum(1 for x in F_any if x["run"] in final_osm_ids),
}

# ---------------------------------------------------------------- G. steps vs reference
G = []
for t in TASK_ORDER:
    ps = [r["steps"] for r in final_runs if r["task"] == t and r["verifier"] == "PASS"]
    G.append({"task": t, "reference_steps": REF_STEPS[t], "pass_runs": len(ps),
              "mean_pass_steps": rnd(statistics.mean(ps)) if ps else None,
              "ratio": rnd(statistics.mean(ps) / REF_STEPS[t]) if ps else None})

# ---------------------------------------------------------------- write JSON
stats = {
    "generated_from": {
        "local": f"{RUNS}\\trial_*/summary.json (+ step response/validation files)",
        "hayati": "git show origin/hayati:runs/<dir>/summary.json",
        "ledger": str(LEDGER),
    },
    "dedup_notes": {
        "local_folders": len(local_dirs), "local_with_summary": len(local),
        "local_without_summary": local_nosummary,
        "hayati_top_level_dirs": len(hay_dirs), "hayati_dirs_without_summary": len(hay_nosummary),
        "hayati_non_trial_summaries_excluded": hay_nontrial,
        "hayati_presentation_duplicates_excluded": pres_dups,
        "hayati_learning_trials_counted": len(hayati),
        "hayati_renamed_trial_folders_kept": hay_renamed,
        "hayati_local_run_id_overlap": sorted(hay_ids & local_ids),
        "ledger_rows": len(ledger_rows), "ledger_timestamp_overlap_with_local_or_hayati": ledger_overlap,
    },
    "A_recorded_runs": {"combined": A_comb, "local": A_local, "hayati": A_hay, "ledger": A_led,
                        "other_breakdown": {"local": dict(local_other), "hayati": dict(hay_other), "ledger": dict(led_other)},
                        "versions": {"local": V_local, "hayati": V_hay, "ledger": "no version field in ledger",
                                     "combined_distinct_version_strings": V_comb_distinct,
                                     "strings_shared_local_hayati": V_shared}},
    "B_final_evaluation": {"batches": FINAL_BATCHES, "per_task": final_by_task, "totals": final_tot,
                           "refusal_categories": dict(refusal_cats.most_common()),
                           "refusals_per_run": refusals_per_run, "non_pass_runs": final_fail_detail,
                           "versions": sorted({r["version"] for r in final_runs})},
    "C_local_project": C_local,
    "D_outcome_categories": {"local": D_local, "hayati": D_hay,
                             "hayati_FAIL_with_repeated_action_message_under_env_error": hay_repeat_in_env},
    "E_osmand_history": {"local_osmand_summaries": len(osm), "by_version_range": E_ranges,
                         "unranged": osm_unranged, "eval_batches": E_batches},
    "F_forwarder_crash_dialog": {"summary": F_summary, "runs": F_rows},
    "G_steps_vs_reference": G,
}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")

# ---------------------------------------------------------------- write markdown
L = []
w = L.append
w("# Run statistics (computed from run files)")
w("")
w(f"Generated by a read-only script from local `runs/`, `origin/hayati` summaries and `RUN_LEDGER_20261008.md`. Full detail: `stats.json`.")
w("")
w("## A. All recorded runs")
w("")
w("Combined = local + hayati + ledger. `other` = NOT_RUN / ERROR (no valid verdict).")
w("")
w("| Task | Runs | PASS | FAIL | other |")
w("| --- | ---: | ---: | ---: | ---: |")
for t, c in sorted(A_comb["per_task"].items(), key=lambda x: -x[1]["total"]):
    w(f"| {t} | {c['total']} | {c['PASS']} | {c['FAIL']} | {c['other']} |")
w(f"| **Total** | **{A_comb['total']}** | **{A_comb['PASS']}** | **{A_comb['FAIL']}** | **{A_comb['other']}** |")
w("")
w("| Source | Runs | PASS | FAIL | other | Distinct versions | Version range |")
w("| --- | ---: | ---: | ---: | ---: | ---: | --- |")
def vr(V):
    return "; ".join(f"{f} {v['range']}" for f, v in V["families"].items())
w(f"| local (team-agent) | {A_local['total']} | {A_local['PASS']} | {A_local['FAIL']} | {A_local['other']} | {V_local['distinct_version_strings']} | {vr(V_local)} |")
hay_other_fams = ", ".join(f + " " + v["range"] for f, v in V_hay["families"].items() if f != "autoglm_api")
hay_api_range = V_hay["families"].get("autoglm_api", {}).get("range")
w(f"| hayati branch | {A_hay['total']} | {A_hay['PASS']} | {A_hay['FAIL']} | {A_hay['other']} | {V_hay['distinct_version_strings']} (+{V_hay['runs_without_version']} runs unversioned) | autoglm_api {hay_api_range}; other families: {hay_other_fams} |")
w(f"| amber ledger | {A_led['total']} | {A_led['PASS']} | {A_led['FAIL']} | {A_led['other']} | n/a | n/a (ledger has no version) |")
w("")
w("Per task and source:")
w("")
w("| Task | local P/F/o | hayati P/F/o | ledger P/F/o |")
w("| --- | --- | --- | --- |")
for t in sorted(A_comb["per_task"]):
    cells = []
    for A in (A_local, A_hay, A_led):
        c = A["per_task"].get(t)
        cells.append(f"{c['PASS']}/{c['FAIL']}/{c['other']}" if c else "-")
    w(f"| {t} | {' | '.join(cells)} |")
w("")
w(f"Distinct version strings across local+hayati: {V_comb_distinct} (no string shared; numbering restarts per branch, so v-numbers overlap but are different agents).")
w("")
w(f"Dedup: local = {len(local)} of {len(local_dirs)} folders (3 without summary.json skipped). "
  f"hayati = {len(hayati)} learning-trial summaries: {len(hay_nosummary)} dirs without summary skipped, "
  f"{len(pres_dups)} `runs/presentation/*` summaries dropped (each has the same run_id as a top-level trial dir; "
  f"identical content: {sum(p['identical_content'] for p in pres_dups)}/{len(pres_dups)}), "
  f"{len(hay_nontrial)} non-task probe summaries dropped; {len(hay_renamed)} renamed trial folders (e.g. `trial_FilesMoveFile_successful`) kept because their internal run_id is unique. "
  f"No run_id overlap local/hayati; no timestamp overlap of ledger with either. "
  f"`other` = local {dict(local_other)}, hayati {dict(hay_other)}, ledger {dict(led_other)}.")
w("")
w("## B. Final evaluation (21 runs, v65)")
w("")
w("| Task | Runs | PASS | Steps mean (min-max) | Mean dur. s | Prompt tok | Compl. tok | Model calls | Refusals |")
w("| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |")
for t, v in final_by_task.items():
    w(f"| {t} | {v['runs']} | {v['PASS']} | {v['steps_mean']} ({v['steps_min']}-{v['steps_max']}) | {v['duration_mean_s']} | {v['prompt_tokens']:,} | {v['completion_tokens']:,} | {v['model_calls']} | {v['validation_errors']} |")
ft = final_tot
w(f"| **Total** | **{ft['runs']}** | **{ft['PASS']}** | {ft['steps_mean']} (sum {ft['steps_total']}) | {ft['duration_mean_s']} | {ft['prompt_tokens']:,} | {ft['completion_tokens']:,} | {ft['model_calls']} | {ft['validation_error_files']} |")
w("")
w(f"- Tokens total {ft['total_tokens']:,} -> cost at EUR {EUR_PER_MTOK}/M tokens: **EUR {ft['cost_eur']}**")
w(f"- Model-call wall time (n={len(all_walls)} responses): median **{ft['model_call_wall_s_median']} s**, mean **{ft['model_call_wall_s_mean']} s**")
w(f"- Total run time of the 21 runs: {round(ft['duration_total_s']/60, 1)} min")
w("")
w("Refusals (validation_error files) by category:")
w("")
w("| Category | Count |")
w("| --- | ---: |")
for k, v in refusal_cats.most_common():
    w(f"| {k} | {v} |")
w("")
nz = [x for x in refusals_per_run if x["validation_errors"]]
w(f"Runs with >=1 refusal: {len(nz)} of 21 — " + ", ".join(f"{x['task']} {x['run_id'].split('_')[-2][-6:]}: {x['validation_errors']} ({x['verifier']})" for x in nz) + ".")
w("")
w("Non-PASS runs: " + "; ".join(f"{x['task']} seed {x['seed']}: {x['verifier']}, agent_done={x['agent_done']}, stop={x['stop_reason']}, error_class={x['error_class']}, failure_class={x['failure_class']}" for x in final_fail_detail) + ".")
w("")
w("## C. Whole local project (all local trial folders)")
w("")
w("| Metric | Value |")
w("| --- | ---: |")
w(f"| Prompt tokens | {c_pt:,} |")
w(f"| Completion tokens | {c_ct:,} |")
w(f"| Total tokens | {c_pt + c_ct:,} |")
w(f"| Cost at EUR {EUR_PER_MTOK}/M | EUR {C_local['cost_eur']} |")
w(f"| Model calls (response files) | {c_resp:,} |")
w(f"| Model calls attempted (sum of summaries) | {C_local['model_calls_attempted_sum_from_summaries']:,} |")
w(f"| Executed steps (sum of summaries) | {C_local['steps_total_from_summaries']:,} |")
w(f"| Run time (sum duration_seconds) | {C_local['run_time_hours_from_summaries']} h |")
w(f"| Model wall time (sum) | {C_local['model_wall_hours']} h |")
w("")
w("## D. Outcome categories (from summary fields)")
w("")
CAT_ORDER = ["PASS", "false completion (model finished, verifier FAIL)", "stopped by no-progress guard",
             "validation_error stop", "step budget exhausted", "infrastructure/other"]
w("| Category | local | hayati |")
w("| --- | ---: | ---: |")
for k in CAT_ORDER:
    w(f"| {k} | {D_local['categories'].get(k, 0)} | {D_hay['categories'].get(k, 0)} |")
w(f"| **Total** | **{D_local['total']}** | **{D_hay['total']}** |")
w("")
w("Rules (first match wins): verifier PASS; agent_done true and verifier FAIL; error_class control_no_progress; error_class validation_error; stop_reason step_budget; everything else.")
w(f"Local stop_reason values: {D_local['stop_reason_values']} (no local run reached its step budget). "
  f"Hayati PASS includes non-clean stops: {D_hay['PASS_by_stop']}.")
w("")
w("Infrastructure/other breakdown:")
w("")
w("| Source | error_class / stop | Count |")
w("| --- | --- | ---: |")
for src, D in (("local", D_local), ("hayati", D_hay)):
    for k, v in sorted(D["infrastructure_other_by_error_class"].items(), key=lambda x: -x[1]):
        w(f"| {src} | {k} | {v} |")
w("")
w(f"Note: {hay_repeat_in_env} hayati FAIL runs carry the message 'Repeated action without visible effect' under error_class environment_or_execution_error (older label); counted as infrastructure/other per the error_class rule. "
  f"Local time_budget_or_recording_error runs all have recording_error 'Recording failed...' and durations far below the time budget.")
w("")
w("## E. OsmAndTrack history (local runs)")
w("")
w("| Versions | Runs | PASS | Versions present |")
w("| --- | ---: | ---: | --- |")
for x in E_ranges:
    w(f"| {x['range']} | {x['runs']} | {x['PASS']} | {', '.join('v'+str(n) for n in x['versions'])} |")
w(f"| **Total** | **{sum(x['runs'] for x in E_ranges)}** | **{sum(x['PASS'] for x in E_ranges)}** | |")
w("")
w("Evaluation batches containing OsmAndTrack:")
w("")
w("| Batch | OsmAnd runs | PASS | FAIL | ERROR | Version |")
w("| --- | ---: | ---: | ---: | ---: | --- |")
for x in E_batches:
    w(f"| {x['batch'].replace('eval_batch_', '')} | {x['osmand_runs']} | {x['PASS']} | {x['FAIL']} | {x['ERROR_or_other']} | {', '.join(v.replace('autoglm_api_', '') for v in x['versions'])} |")
w("")
w("## F. Accessibility-forwarder crash dialog (OsmAnd, v49+)")
w("")
fs = F_summary
w(f"Local OsmAndTrack runs with version >= v49: **{fs['osmand_runs_v49_plus']}**. Runs where a tree/response contains 'keeps stopping' or a model reply mentions 'Close app': **{fs['runs_with_dialog']}** ({round(100*fs['share'])}%). "
  f"('keeps stopping' text: {fs['runs_with_keeps_stopping_text']} runs; 'Close app' reply: {fs['runs_with_close_app_reply']} runs.) "
  f"PASS among dialog runs: {fs['dialog_runs_PASS']}/{fs['runs_with_dialog']}; among the others: {fs['no_dialog_runs_PASS']}/{fs['no_dialog_runs']}. "
  f"Final-eval OsmAnd runs with the dialog: {fs['final_eval_osmand_runs_with_dialog']}/3.")
w("")
w("## G. Steps vs course reference (final evaluation PASS runs)")
w("")
w("| Task | Reference steps | PASS runs | Mean steps (PASS) | Ratio |")
w("| --- | ---: | ---: | ---: | ---: |")
for g in G:
    w(f"| {g['task']} | {g['reference_steps']} | {g['pass_runs']} | {g['mean_pass_steps']} | {g['ratio']}x |")
w("")
w("## Not computed / caveats")
w("")
w("- Ledger: no agent version, tokens, durations, error_class or stop_reason, so it is only in section A (D not computed for it). "
  f"Its own failure-class column: {dict(C(r['failure_class'] for r in ledger_rows if r['result'] != 'PASS'))}.")
w("- Hayati PASS (60) counts verifier PASS only; 8 of them did not end with the agent's own finish (4 step_budget, 4 error stops).")
w("- Crash-dialog detection (F) is a text search of saved trees/replies; a dialog seen only on an unsaved frame would be missed.")
w("- Hayati: tokens, durations of model calls and refusals not computed (only summary.json was read). 3 hayati runs have no version field.")
w(f"- {len(local_nosummary)} local folders without summary.json ({', '.join(x['task'] + ' ' + str(x['version']).replace('autoglm_api_', '') for x in local_nosummary)}) are excluded from A, D, E; their {sum(len(run_model_files(RUNS / x['run'])[0]) for x in local_nosummary)} response files are included in C token totals.")
w("- Step-budget exhaustion: no local run has stop_reason step_budget (value 0 is real, not missing).")
(OUT / "STATS.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print(json.dumps({k: stats[k] for k in ["dedup_notes"]}, indent=1, ensure_ascii=False)[:3000])
print("\n".join(L))
