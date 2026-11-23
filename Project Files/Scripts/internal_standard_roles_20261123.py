"""Give internal-standard masses their role (7.13; issue #23 follow-up, 2026-11-23).

The #23 reply of 2026-11-19 promised a validator check: every element named in `Internal Standard
Element` has a monitored mass with role `Internal standard` (or `Mass-bias monitor`, the MC-ICP-MS
case). `check_internal_standard_role` in validate_tapp.py is that check. Its first run found 9 masses
in 7 literature columns whose role cell had been filled without reading the same column's `Internal
Standard Element` cell: the bundle wrote `all: Target` where every member had a target species, and `N`
where a parentless member's role was not stated next to the mass list.

Each correction below is read from cells already in the same column, not from a fresh reading:
- Lu et al. 2007 (Solution SF): ISE `Nb (93Nb) — §2.1.2`; ⁹³Nb is parentless (→ none), so its role is
  Internal standard alone, for the Ti it is measured with.
- Lu et al. 2007 (Solution Q): ISE `the ID-determined Zr, Mo and Hf, as references for Nb and Ta (ID-IS)`;
  those masses are targets AND internal standards.
- Makishima et al. 2011 (Solution Q): ISE `Sm (149Sm) — the spike isotope (ID-IS)`; ¹⁴⁹Sm is parentless.
- Mittlefehldt 2024 (LA-SF, LA-SF_UPb): ISE `Mg (²⁵Mg)`; ²⁵Mg is a target and the internal standard.
- Chernonozhkin et al. 2021, the two-run column (LA-SF, LA-SF_UPb): ISE `run 2: Cr (concentration from
  run 1)`; ⁵³Cr is a target and, in run 2, the internal standard.

Literature cells only (Column H stamped on the two role rows). Recomposed, parked, register/mirror/spec
refreshed. Run without --apply for a dry run.
"""

import csv, io, json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-11-23"
ROLE, DETAIL, ISE = "Monitored Property Role", "Monitored Property Role Detail", "Internal Standard Element"

# stem -> [(header substring, ISE-cell prefix to disambiguate, {field: (old cell, new cell)})]
LU_Q_IS = "90Zr, 91Zr, 95Mo, 97Mo, 178Hf, 179Hf"
EDITS = {
    "Solution_SF-ICP-MS": [
        ("Lu+etal2007", "all: Nb", {
            ROLE: ("93Nb: N; other: Target — its role is not stated",
                   "93Nb: Internal standard; other: Target — Internal Standard Element, §2.1.2"),
            DETAIL: ("N — not stated", "93Nb: Ti")}),
    ],
    "Solution_Q-ICP-MS": [
        ("Lu+etal2007", "all: the ID-determined", {
            ROLE: ("all: Target",
                   "%s: Target, Internal standard; other: Target — the ID-determined Zr, Mo and Hf are the "
                   "references for Nb and Ta (ID-IS), §2.8, §3.5" % LU_Q_IS),
            DETAIL: ("N/A — every monitored property is a target", "%s: Nb and Ta" % LU_Q_IS)}),
        ("Makishima+etal2011", "all: Sm", {
            ROLE: ("95Mo: Interference monitor; 113Cd, 118Sn, 149Sm: N; other: Target — "
                   "'113Cd was not used for Cd determination'",
                   "95Mo: Interference monitor; 149Sm: Internal standard; 113Cd, 118Sn: N; other: Target — "
                   "'113Cd was not used for Cd determination'"),
            DETAIL: ("95Mo: MoO on Cd", "95Mo: MoO on Cd; 149Sm: all target species (ID-IS spike isotope)")}),
    ],
}
for stem in ("LA-SF-ICP-MS", "LA-SF-ICP-MS_UPb"):
    EDITS[stem] = [
        ("Mittlefehldt 2024", "all: Mg", {
            ROLE: ("all: Target", "²⁵Mg: Target, Internal standard; other: Target"),
            DETAIL: ("N/A — every monitored property is a target", "²⁵Mg: all target species")}),
        ("Chernonozhkin et al. 2021", "run 1: none", {
            ROLE: ("all: Target", "⁵³Cr: Target, Internal standard; other: Target — internal standard in run 2"),
            DETAIL: ("N/A — every monitored property is a target",
                     "⁵³Cr: the run-2 target species, with its concentration from run 1")}),
    ]


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


def main(apply=False):
    rp = os.path.join(ROOT, "composed_tapps.json")
    reg = json.load(io.open(rp, encoding="utf-8"))
    plan, n = [], 0
    for e in reg["composed"]:
        rel = e["tapp"]
        stem = os.path.basename(rel).rsplit("_TAPP_v", 1)[0]
        if stem not in EDITS:
            continue
        rows = rows_of(os.path.join(ROOT, rel))
        h = rows[0]
        by = {r[0].strip(): r for r in rows[1:] if r}
        for sub, ise_prefix, cells in EDITS[stem]:
            js = [j for j in range(len(h)) if sub in h[j] and by[ISE][j].startswith(ise_prefix)]
            assert len(js) == 1, (rel, sub, js)
            j = js[0]
            for field, (old, new) in cells.items():
                assert by[field][j] == old, (rel, sub, field, by[field][j])
                by[field][j] = new
                by[field][7] = DATE
                n += 1
            print("  %-34s %s" % (stem, sub))
        s, v = rel[:-4].rsplit("_v", 1)
        plan.append((e, rel, "%s_v%d.csv" % (s, int(v) + 1), rows))
    assert len(plan) == 4 and n == 14, (len(plan), n)
    if not apply:
        print("dry run: %d TAPPs, %d cells" % (len(plan), n))
        return 0

    sup = os.path.join(ROOT, "Superseded TAPPs", DATE)
    os.makedirs(sup, exist_ok=True)
    for e, rel, new, rows in plan:
        np_ = os.path.join(ROOT, new)
        write(np_, rows)
        q = subprocess.run([sys.executable, COMPOSE, "--source", np_] + flags(e["modules"]) + ["--out", np_],
                           cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (rel, q.stdout[-2000:], q.stderr[-800:]))
        if rows_of(np_) != rows:
            raise SystemExit("composition changed %s beyond the edit" % new)
        for f in (os.path.join(ROOT, rel), os.path.join(ROOT, rel)[:-4] + ".xlsx"):
            if os.path.exists(f):
                shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("xlsx failed %s\n%s" % (new, q.stderr[-700:]))
        e["tapp"] = new
        print("  composed %s" % os.path.basename(new))

    reg["generated"] = DATE
    with io.open(rp, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py", "build_schema_spec_counts.py"):
        q = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                           cwd=ROOT, capture_output=True, text=True)
        print("  %s: %s" % (s, (q.stdout.strip().splitlines() or ["ok"])[-1][:90]))
    return 0


sys.exit(main("--apply" in sys.argv))
