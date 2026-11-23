"""Add `Mass-bias monitor` to the listed values of Monitored Property Role (issue #23 follow-up, 2026-11-23).

The #19/#22/#23 bundle (bundle_19_22_23_20261123.py) shipped the role list as four values plus N/A | None.
Filling the literature cells found a fifth role twice: masses monitored to correct instrumental mass bias
(Desem et al. 2022, Tl; Willbold 2005, Ti, Ru, Re). The list is open, so those cells already said
`Mass-bias monitor`; RD decided to list it, and the #23 reply to SMR promised it in the next bump.

Monitored Property Role is TAPP-owned (check_field_ownership.py), so the edit is to the 12 TAPP CSVs that
carry it: Column F gains the value, Column B gains one sentence defining it, Column H is stamped. One
vocabulary across all 12, as for the other four roles. Every TAPP is recomposed to confirm the edit
survives composition, the old version is parked, and the register, mirror and spec counts are refreshed.

Run without --apply for a dry run.
"""

import csv, io, json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE = "2026-11-23"
FIELD = "Monitored Property Role"

OLD_F = "Target | Interference monitor | Internal standard | Phase monitor | N/A | None"
NEW_F = "Target | Interference monitor | Internal standard | Phase monitor | Mass-bias monitor | N/A | None"
ANCHOR = "rather than to quantify or correct anything."
SENT = (" Mass-bias monitor: to correct instrumental mass bias, using an element of known isotopic "
        "composition measured with the others, such as Tl added to a Pb solution.")


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
    plan = []
    for e in reg["composed"]:
        rel = e["tapp"]
        rows = rows_of(os.path.join(ROOT, rel))
        hit = [r for r in rows[1:] if r and r[0].strip() == FIELD]
        if not hit:
            continue
        assert len(hit) == 1, rel
        r = hit[0]
        assert r[5] == OLD_F, (rel, r[5])
        assert ANCHOR in r[1] and "Mass-bias monitor" not in r[1], rel
        r[5] = NEW_F
        r[1] = r[1].replace(ANCHOR, ANCHOR + SENT, 1)
        r[7] = DATE
        stem, v = rel[:-4].rsplit("_v", 1)
        new = "%s_v%d.csv" % (stem, int(v) + 1)
        plan.append((e, rel, new, rows))
        print("  %-48s -> %s" % (rel, os.path.basename(new)))
    assert len(plan) == 12, len(plan)
    if not apply:
        print("dry run: %d TAPPs" % len(plan))
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
        after = rows_of(np_)
        if after != rows:
            raise SystemExit("composition changed %s beyond the edit" % new)
        for f in (os.path.join(ROOT, rel), os.path.join(ROOT, rel)[:-4] + ".xlsx"):
            if os.path.exists(f):
                shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, np_], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0:
            raise SystemExit("xlsx failed %s\n%s" % (new, q.stderr[-700:]))
        e["tapp"] = new

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
