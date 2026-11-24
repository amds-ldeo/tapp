"""Split the Analysis-Level Tier: Column D keeps obligation, new Column K `Procedure Value` (2026-11-24).

Issues #9 and #13 (amds-ldeo/tapp). Column D carried two questions in one vocabulary: whether the session
record must carry a field (Basic / Advanced) and where the session value comes from (Read-Only /
Editable). SMR proposed separating them; the proposal posted on #13 on 2026-11-23 was approved on
2026-11-24 ("looks good — lets adopt it").

The mapping is lossless over the nine C/D combinations in use:

    D today              ->  D        K (Procedure Value)
    Read-Only            ->  = C      Fixed
    Editable             ->  = C      Adjustable
    Basic / Advanced     ->  as is    Not carried over

`Fixed` and `Adjustable` require C in {Basic, Advanced}, which the validator already guaranteed for
Read-Only and Editable (tier-inconsistent), so every inherited value has a C to copy.

Placement. The proposal said "directly after D". RD decided on 2026-11-24 to append the column after J
(`Purpose`) as Column K for now, so that no existing column letter changes: about 265 references in the
docs, scripts and module histories cite Columns E–J by letter, many of them dated history. This is the
same trade made for `Keyed By` (I) and `Purpose` (J). Whether to move it next to D is a later decision.

What this script does:
  1. Every module CSV (15): header gains `Procedure Value` at index 10; each field row gets D and K by
     the mapping. Each manifest takes K into `owned_columns` (tiers are module-owned), bumps its
     version and records a decision.
  2. Every current TAPP (16): the column is inserted at index 10 in every row, so the mode flags,
     sentinel and literature columns move one place right; each content row gets D and K by the mapping
     and Column H is stamped (every content row changed). The TAPP is then recomposed with the new
     modules and must come back identical.
  3. Old versions are parked in `Superseded TAPPs/2026-11-24/`, xlsx regenerated, register, mirror and
     schema counts refreshed, and the Superseded README skeleton written.

Run without --apply for a dry run, which prints the combination counts.
"""

import collections, csv, glob, io, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "Project Files", "Scripts"))
from superseded_readme import write_skeleton  # noqa: E402

MODULES = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-11-24"
AT = 10                      # Column K
HEADER = "Procedure Value"
GROUP_RE = re.compile(r"^\d+\.\s")

MAP = {"Read-Only": "Fixed", "Editable": "Adjustable"}
DECISION = ("{d} v{v}. Issues #9/#13: Column D split. D now holds Basic / Advanced only (the session record's "
            "obligation, worded as Column C); where the session value comes from moved to the new module-owned "
            "Column K `Procedure Value` (Fixed / Adjustable / Not carried over). Read-Only -> D = C, K = Fixed; "
            "Editable -> D = C, K = Adjustable; Basic / Advanced -> unchanged, K = Not carried over. `owned_columns` "
            "gains K. No field changed meaning.")


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


def is_field(r):
    return bool(r) and bool(r[0].strip()) and not GROUP_RE.match(r[0].strip()) and len(r) > 3 and r[2].strip()


def split(c, d, where):
    if d in MAP:
        assert c in ("Basic", "Advanced"), (where, c, d)
        return c, MAP[d]
    assert d in ("Basic", "Advanced"), (where, c, d)
    return d, "Not carried over"


def migrate(rows, where, insert, stamp, tally):
    """insert: TAPP (insert at AT, shifting what follows) vs module (append at AT, nothing follows)."""
    hdr = rows[0]
    assert hdr[9].strip() == "Purpose", (where, hdr[9])
    assert len(hdr) == 10 or hdr[AT].strip() != HEADER, (where, "already migrated")
    for r in rows:
        while len(r) < AT:
            r.append("")
        r.insert(AT, "") if insert else (r.append("") if len(r) == AT else None)
        if not insert:
            assert len(r) == AT + 1, (where, len(r))
    rows[0][AT] = HEADER
    for r in rows[1:]:
        if not is_field(r):
            continue
        c, d = r[2].strip(), r[3].strip()
        tally[(c, d)] += 1
        r[3], r[AT] = split(c, d, "%s / %s" % (where, r[0]))
        if stamp:
            r[7] = DATE
    return rows


def main(apply=False):
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))

    # ---- modules
    mtally, M, J = collections.Counter(), {}, {}
    for p in sorted(glob.glob(os.path.join(MODULES, "Module_*.csv"))):
        m = os.path.basename(p)[7:-4]
        M[m] = migrate(rows_of(p), "Module_" + m, insert=False, stamp=False, tally=mtally)
        J[m] = json.load(io.open(p[:-4] + ".json", encoding="utf-8"))
        assert "K" not in J[m]["owned_columns"], m
    assert len(M) == 15, len(M)

    # ---- TAPPs
    ttally, plan = collections.Counter(), []
    for e in reg["composed"]:
        rel = e["tapp"]
        rows = migrate(rows_of(os.path.join(ROOT, rel)), os.path.basename(rel), insert=True, stamp=True,
                       tally=ttally)
        s, v = rel[:-4].rsplit("_v", 1)
        plan.append((e, rel, "%s_v%d.csv" % (s, int(v) + 1), rows))
    assert len(plan) == 16

    print("TAPP rows by (C, D) -> (D, K):")
    for (c, d), n in sorted(ttally.items(), key=lambda x: -x[1]):
        print("  %-9s %-10s %5d  ->  D=%-9s K=%s" % (c, d, n, *split(c, d, "")))
    print("  total %d" % sum(ttally.values()))
    print("Module rows: %d, combinations %s" % (sum(mtally.values()), sorted(mtally)))
    assert sum(ttally.values()) == 1919, sum(ttally.values())
    if not apply:
        for e, rel, new, _ in plan:
            print("  %-48s -> %s" % (rel, os.path.basename(new)))
        print("dry run")
        return 0

    # ---- write modules
    newver = {}
    for m in M:
        p = os.path.join(MODULES, "Module_%s.csv" % m)
        write(p, M[m])
        jp = p[:-4] + ".json"
        ind = 4 if io.open(jp, encoding="utf-8").read().startswith("{\n    ") else 2
        newver[m] = str(int(J[m]["version"]) + 1)
        J[m]["version"] = newver[m]
        J[m]["owned_columns"] = J[m]["owned_columns"] + ["K"]
        if "tier_provenance" in J[m]:
            J[m]["tier_provenance"] = J[m]["tier_provenance"].replace(
                "Tier values (Columns C and D)", "Tier values (Columns C and D, and Procedure Value in K)")
        J[m]["decisions"].append(DECISION.format(d=DATE, v=newver[m]))
        with io.open(jp, "w", encoding="utf-8") as fh:
            json.dump(J[m], fh, indent=ind, ensure_ascii=False)
            fh.write("\n")

    # ---- write, recompose (must be identical), park, export
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE)
    os.makedirs(sup, exist_ok=True)
    for e, rel, new, rows in plan:
        for mm in e["modules"]:
            mm["version"] = newver[mm["name"]]
        np_ = os.path.join(ROOT, new)
        write(np_, rows)
        q = subprocess.run([sys.executable, COMPOSE, "--source", np_] + flags(e["modules"]) + ["--out", np_],
                           cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (rel, q.stdout[-2000:], q.stderr[-800:]))
        after = rows_of(np_)
        if after != rows:
            diff = [(i, j) for i, (a, b) in enumerate(zip(after, rows)) for j in range(max(len(a), len(b)))
                    if (a[j] if j < len(a) else "") != (b[j] if j < len(b) else "")]
            raise SystemExit("composition changed %s beyond the migration: %s" % (new, diff[:10]))
        for f in (os.path.join(ROOT, rel), os.path.join(ROOT, rel)[:-4] + ".xlsx"):
            if os.path.exists(f):
                shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("xlsx failed %s\n%s" % (new, q.stderr[-700:]))
        e["tapp"] = new
        print("  composed %s" % os.path.basename(new))

    reg["generated"] = DATE
    with io.open(os.path.join(ROOT, "composed_tapps.json"), "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    for s in ("build_module_register.py", "sync_current_tapps.py", "build_schema_spec_counts.py"):
        q = subprocess.run([sys.executable, os.path.join(ROOT, "Project Files", "Scripts", s), "--apply"],
                           cwd=ROOT, capture_output=True, text=True)
        print("  %s: %s" % (s, (q.stdout.strip().splitlines() or ["ok"])[-1][:90]))
    write_skeleton(ROOT, DATE)
    return 0


sys.exit(main("--apply" in sys.argv))
