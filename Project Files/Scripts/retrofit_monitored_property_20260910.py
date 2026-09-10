#!/usr/bin/env python3
"""Retrofit `monitored property`: migrate every field keyed `channel` onto the new key.

    python3 "Project Files/Scripts/retrofit_monitored_property_20260910.py" [--apply]

Executes the `monitored property` half of Proposal_Monitored_Property_2026-09-10.md, whose
§10 withdrew the `detector` half for want of a single attested consumer.

WHAT MOVES.  `channel` -> `monitored property` and
`defines: channel per target species` -> `defines: monitored property per target species`,
in 29 fields across 13 TAPPs. After this, no field in the library is keyed `channel`; the key
stays in the vocabulary for the swept-axis techniques not yet built (Rule 7.2, third note).

OWNERSHIP.  Column I is module-owned for 13 of the 29 fields, so those are edited in the
module and recomposed — Rule 6.6 forbids hand-editing a composed row:

    Module_CollisionCell v4 -> v5   5 fields   6 consumers
    Module_ICPMS        v12 -> v13  4 fields   9 consumers
    Module_MCICPMS       v8 -> v9   4 fields   3 consumers

The other 16 are TAPP-owned and edited directly in each technique CSV. Nine TAPPs are
recomposed (they consume a bumped module); four — EPMA, SEM, SEM_Composition, TEM — carry
only TAPP-owned affected fields and are bumped without recomposition.

NOT DONE HERE, and deliberately.

  * `Ion Counter Dead Time` stays uniform. The proposal wanted `(none)` in the six
    single-collector TAPPs, there being one detector and therefore one dead time. The field
    is Module_ICPMS-owned and Rule 6.5 forbids a module expressing two Column I values, so
    that fix needs the field taken out of the module first. Left at `monitored property`,
    which is no worse than the `channel` it replaces — the over-declaration is unchanged,
    not introduced. It has ZERO attestations in the whole corpus, so nothing decides it
    either way today.

  * The §4 restructure — demoting `Collector Configuration` and `WDS Spectrometer Channel`
    to per-monitored-property attributes and promoting `Monitored Masses` to definer — is
    NOT applied. It needs two new fields (`Monitored Masses` in Solution MC-ICP-MS,
    `Monitored Elements` in the three electron-beam TAPPs), which is a Rule 6 admission
    decision and its own pass. Until then `Monitored Masses` keeps its registered
    technique-dependent divergence and the four definers keep their `per target species`
    parent, so the mass-to-element binding is preserved exactly.

This is therefore a pure key rename: every Column I value changes name, none changes shape.
Column H is stamped — the key a field declares is part of its definition.
"""

import csv, io, json, os, re, shutil, subprocess, sys

ROOT    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODULES = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")
XLSX    = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "tapp_to_xlsx.py")
DATE    = "2026-09-10"
BUMP    = {"CollisionCell": "5", "ICPMS": "13", "MCICPMS": "9"}


def remap(v):
    v = v.strip()
    if v == "channel":
        return "monitored property"
    if v.startswith("defines: channel per "):
        return v.replace("defines: channel per ", "defines: monitored property per ")
    if v == "defines: channel":
        return "defines: monitored property"
    if "channel" in v:                     # compound, e.g. `channel x something`
        return re.sub(r"\bchannel\b", "monitored property", v)
    return v


def rekey(path, stamp=True):
    """Rewrite Column I in one CSV. Returns the field names changed."""
    rows = list(csv.reader(io.open(path, newline="", encoding="utf-8-sig")))
    h = rows[0]
    iI = h.index("Keyed By")
    iU = h.index("Last Update") if "Last Update" in h else None
    hit = []
    for r in rows[1:]:
        if len(r) <= iI or not r[0].strip():
            continue
        new = remap(r[iI])
        if new != r[iI].strip():
            r[iI] = new
            if stamp and iU is not None:
                while len(r) <= iU: r.append("")
                r[iU] = DATE
            hit.append(r[0].strip())
    if hit:
        with io.open(path, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)
    return hit


def flags(mods):
    out = []
    for m in mods:
        spec = m["name"]
        if m.get("blocks"):
            spec += ":" + (m["blocks"] if isinstance(m["blocks"], str) else ",".join(m["blocks"]))
        out += ["--module", spec]
    return out


def main(apply=False):
    reg = json.load(io.open(os.path.join(ROOT, "composed_tapps.json"), encoding="utf-8"))

    # which TAPPs are touched, and which need recomposition
    recompose, direct = [], []
    for e in reg["composed"]:
        rel = e["tapp"]
        cur = os.path.join(ROOT, rel)
        needs_mod = any(m["name"] in BUMP for m in e["modules"])
        has_ch = any(len(r) > 8 and r[0].strip() and "channel" in r[8]
                     for r in csv.reader(io.open(cur, newline="", encoding="utf-8-sig")))
        if not (needs_mod or has_ch):
            continue
        new = re.sub(r"_v(\d+)\.csv$", lambda m: "_v%d.csv" % (int(m.group(1)) + 1), rel)
        (recompose if needs_mod else direct).append((e, rel, new))

    print("  recompose (module-owned changes): %d" % len(recompose))
    for _, rel, new in recompose: print("      %-40s -> %s" % (os.path.basename(rel), os.path.basename(new)))
    print("  direct bump (TAPP-owned only)   : %d" % len(direct))
    for _, rel, new in direct: print("      %-40s -> %s" % (os.path.basename(rel), os.path.basename(new)))
    print("  modules bumped                  : %s" % ", ".join(f"{k}->v{v}" for k, v in BUMP.items()))
    if not apply:
        print("\n(dry run — pass --apply to write)")
        return 0

    # --- 1. modules: Column I, then the manifest version -----------------------
    for mod, ver in BUMP.items():
        mc = os.path.join(MODULES, "Module_%s.csv" % mod)
        hit = rekey(mc)
        mj = os.path.join(MODULES, "Module_%s.json" % mod)
        d = json.load(io.open(mj, encoding="utf-8"))
        d["version"] = ver
        with io.open(mj, "w", encoding="utf-8") as fh:
            json.dump(d, fh, indent=2, ensure_ascii=False); fh.write("\n")
        print("  Module_%s: %d field(s) re-keyed, manifest -> v%s" % (mod, len(hit), ver))

    # --- 2. TAPP-owned Column I, edited in the CURRENT file before composing ---
    for _, rel, _ in recompose + direct:
        hit = rekey(os.path.join(ROOT, rel))
        if hit: print("  %-40s %d TAPP-owned field(s)" % (os.path.basename(rel), len(hit)))

    # --- 3. compose the nine, copy the four ------------------------------------
    for e, rel, new in recompose:
        p = subprocess.run([sys.executable, COMPOSE, "--source", os.path.join(ROOT, rel)]
                           + flags(e["modules"]) + ["--out", os.path.join(ROOT, new)],
                           cwd=ROOT, capture_output=True, text=True)
        if p.returncode != 0:
            raise SystemExit("compose failed %s\n%s\n%s" % (rel, p.stdout[-1500:], p.stderr[-600:]))
        print("  composed %s" % os.path.basename(new))
    for e, rel, new in direct:
        shutil.copyfile(os.path.join(ROOT, rel), os.path.join(ROOT, new))
        print("  copied   %s" % os.path.basename(new))

    # --- 4. stamp Column H on the rows the module supplied, then park ----------
    sup = os.path.join(ROOT, "Superseded TAPPs", DATE)
    os.makedirs(sup, exist_ok=True)
    modfields = set()
    for mod in BUMP:
        for r in csv.reader(io.open(os.path.join(MODULES, "Module_%s.csv" % mod),
                                    newline="", encoding="utf-8-sig")):
            if r and r[0].strip(): modfields.add(r[0].strip())
    for e, rel, new in recompose + direct:
        np_ = os.path.join(ROOT, new)
        rows = list(csv.reader(io.open(np_, newline="", encoding="utf-8-sig")))
        h = rows[0]; iU = h.index("Last Update"); iI = h.index("Keyed By")
        for r in rows[1:]:
            if r and r[0].strip() in modfields and len(r) > iI and r[iI].strip().startswith(("monitored property", "defines: monitored property")):
                while len(r) <= iU: r.append("")
                r[iU] = DATE
        with io.open(np_, "w", newline="", encoding="utf-8-sig") as fh:
            csv.writer(fh).writerows(rows)
        old = os.path.join(ROOT, rel)
        for f in (old, old[:-4] + ".xlsx"):
            if os.path.exists(f): shutil.move(f, os.path.join(sup, os.path.basename(f)))
        q = subprocess.run([sys.executable, XLSX, new], cwd=ROOT, capture_output=True, text=True)
        if q.returncode != 0: raise SystemExit("xlsx failed %s\n%s" % (new, q.stderr[-600:]))
        e["tapp"] = new
        for m in e["modules"]:
            if m["name"] in BUMP: m["version"] = BUMP[m["name"]]

    reg["generated"] = DATE
    with io.open(os.path.join(ROOT, "composed_tapps.json"), "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    print("  registry: %d path(s) advanced" % len(recompose + direct))

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from superseded_readme import write_skeleton
    for s in (os.path.join(ROOT, "Project Files", "Scripts", "sync_current_tapps.py"),):
        subprocess.run([sys.executable, s, "--apply"], cwd=ROOT, capture_output=True, text=True)
    print("  mirror synced")
    write_skeleton(ROOT, DATE)
    return 0


sys.exit(main("--apply" in sys.argv))
