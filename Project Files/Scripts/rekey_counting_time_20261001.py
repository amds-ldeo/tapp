#!/usr/bin/env python3
"""Peak and background counting times keyed per target material (2026-10-01).

    python3 "Project Files/Scripts/rekey_counting_time_20261001.py" [--apply] [--out-sim DIR]

`Peak Counting Time` and `Background Counting Time`: `monitored property` -> `target material x
monitored property`, in EPMA, SEM and SEM_Composition (TAPP-owned; Rule 2 keeps the three alike).

Why. Zega+2025 (EPMA) sets counting times per phase, with no element named: silicates, sulfides and
oxides 20 s peak and 10 s on each background; phosphates 20 s and 10 s; carbonates 10 s and 5 s. The
times change with the phase for the reason the beam current and diameter do, "to minimize possible beam
damage effects". A per-element key cannot hold it, so the cell was `N` with the times in commentary.
Gap 1 (2026-09-28) keyed the beam conditions `target material` and held the counting times "until a second
procedure attests them". The user decided on 2026-10-01 to re-key now. Only a procedure that analyses
several materials *and* states counting times can test a material axis. Ma+2017, Frank+2023 and Barnes+2025
state times but one set for all, which is consistent with either key; Zega is the one test, and it attests
the axis. This is the single-pass unfalsifiability argument, one axis over, and the same course as the
2026-09-29 standards re-key (McCoy+2025_UA, one paper).

Cells. EPMA's stated cells become two-level. Where the paper gives one set for every material, `all [ ... ]`
with the entries unchanged. Zega gets its per-phase statement, inner `all` because it names no element.
SEM and SEM_Composition have no stated cells. No description, tier, data type or Column F changes.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "Claude Skills for TAPP", "scripts"))
import keyed_cells as K

COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-10-01"
FIELDS  = ("Peak Counting Time", "Background Counting Time")
OLDKEY, NEWKEY = "monitored property", "target material x monitored property"
STEMS   = ("EPMA", "SEM", "SEM_Composition")
ZQ = ("'Quantitative analyses of silicates, sulfides and oxides were run using a focused beam at 15 kV, 20 nA, 20 s "
      "peak time and 10 s on each background ... Phosphate analyses were performed at 15 kV, 8 nA, 20 s peak and 10 s "
      "background; carbonates at 15 kV, 4 nA, 10 s peak and 5 s background' (Methods); no element is named")
ZEGA = {"Peak Counting Time": "silicates, sulfides, oxides [all: 20 s]; phosphates [all: 20 s]; carbonates [all: 10 s] — " + ZQ,
        "Background Counting Time": ("silicates, sulfides, oxides [all: 10 s on each background]; phosphates [all: 10 s background]; "
                                     "carbonates [all: 5 s background] — " + ZQ)}


def rows_of(p):
    return list(csv.reader(io.open(p, newline="", encoding="utf-8-sig")))


def write(p, rows):
    with io.open(p, "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(rows)


def flags(mods):
    o = []
    for m in mods:
        s = m["name"]
        if m.get("blocks"):
            s += ":" + (m["blocks"] if isinstance(m["blocks"], str) else ",".join(m["blocks"]))
        o += ["--module", s]
    return o


def edit(rr, stem, report):
    h = rr[0]; jI, jU = h.index("Keyed By"), h.index("Last Update"); s = h.index("Literature Assessment")
    for r in rr[1:]:
        if not r or r[0].strip() not in FIELDS:
            continue
        f = r[0].strip()
        if r[jI] not in (OLDKEY, NEWKEY):
            raise SystemExit("PREMISE: %s %s keyed %r" % (stem, f, r[jI]))
        if r[jI] != NEWKEY:
            report.append((stem, f, "Keyed By", r[jI], NEWKEY)); r[jI], r[jU] = NEWKEY, DATE
        for j in range(s + 1, len(h)):
            lab = h[j].replace("\n", " ").split("|")[0].strip(); v = r[j]
            if stem == "EPMA" and lab == "Zega+2025":
                new = ZEGA[f]
            elif K.is_marker(v) or v.lstrip().startswith("all [") or not v.strip():
                continue
            else:
                struct, comment = K.split_commentary(v)
                new = "all [%s]" % struct + (" — " + comment if comment else "")
            if new != v:
                report.append((stem, f, lab, v, new)); r[j] = new
    return rr


def main(apply=False):
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))
    sim = sys.argv[sys.argv.index("--out-sim") + 1] if "--out-sim" in sys.argv else None
    plan = []
    for e in reg["composed"]:
        stem = os.path.basename(e["tapp"]).rsplit("_TAPP_v", 1)[0]
        if stem in STEMS:
            plan.append((e, stem, re.sub(r"_v(\d+)\.csv$", lambda x: "_v%d.csv" % (int(x.group(1)) + 1), e["tapp"])))
    if sorted(s for _, s, _ in plan) != sorted(STEMS):
        raise SystemExit("PREMISE: expected %s, found %s" % (STEMS, [s for _, s, _ in plan]))
    for e, stem, new in plan:
        report = []
        rr = edit(rows_of(os.path.join(ROOT, e["tapp"])), stem, report)
        print("  %s -> %s: %d changes" % (os.path.basename(e["tapp"]), os.path.basename(new), len(report)))
        for x in report:
            print("     %s | %s | %s\n        was: %s\n        now: %s" % (x[0], x[1], x[2], x[3][:120], x[4][:160]))
        if sim:
            os.makedirs(sim, exist_ok=True); write(os.path.join(sim, os.path.basename(new)), rr)
    if not apply:
        print("\n(dry run — pass --apply to write; --out-sim DIR writes the edited CSVs for checking)"); return 0

    sup = os.path.join(ROOT, "Superseded TAPPs", DATE); os.makedirs(sup, exist_ok=True)
    for e, stem, new in plan:
        rel = e["tapp"]; np_ = os.path.join(ROOT, new)
        q = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)] + flags(e["modules"])
                           + ["--out", np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (rel, q.stdout[-1500:], q.stderr[-700:]))
        write(np_, edit(rows_of(np_), stem, []))
        for f in (os.path.join(ROOT, rel), os.path.join(ROOT, rel)[:-4] + ".xlsx"):
            dst = os.path.join(sup, os.path.basename(f))
            if os.path.exists(dst):
                raise SystemExit("PREMISE: %s already parked" % dst)
            shutil.move(f, dst)
        q = subprocess.run([sys.executable, XLSX, np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("xlsx failed %s\n%s" % (new, q.stderr[-700:]))
        rp = os.path.join(ROOT, "composed_tapps.json")
        reg = json.load(io.open(rp, encoding="utf-8"))
        for x in reg["composed"]:
            if x["tapp"] == rel:
                x["tapp"] = new
        with io.open(rp, "w", encoding="utf-8") as fh:
            json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py", "build_schema_spec_counts.py"):
        q = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                           cwd=ROOT, capture_output=True, text=True)
        print("  %s: %s" % (s, (q.stdout.strip().splitlines() or ["ok"])[-1][:90]))
    sys.path.insert(0, os.path.join(ROOT, "Project Files", "Scripts"))
    import superseded_readme
    superseded_readme.write_skeleton(ROOT, DATE)
    return 0


sys.exit(main("--apply" in sys.argv))
