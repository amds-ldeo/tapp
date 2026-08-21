#!/usr/bin/env python3
"""Switch all 16 TAPPs from Module_Group1 to Module_Core, and retire Group1.

No TAPP file changes and no version bump: `compose_tapp.py --check` reports MATCH on all 16
against Module_Core, because the reconciliation was done before the module was built. This is
a pure bookkeeping swap — registers and the module folder only.

  --dry (default)   report
  --apply           write
"""
import argparse, csv, json, os, shutil, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
MODDIR = os.path.join(ROOT, "Claude Skills for TAPP", "modules")
REG = os.path.join(ROOT, "composed_tapps.json")
MREG = os.path.join(ROOT, "Project Files", "Registers & Planning", "TAPP_Module_Register.csv")
ARCH = os.path.join(ROOT, "Archive", "Superseded Modules")
DATE = "2026-08-14"
OLD, NEW, NEWVER = "Group1", "Core", "1"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    apply = a.apply and not a.dry

    # ---- guard: Core must already MATCH every consumer, or this swap is a lie ----
    reg = json.load(open(REG, encoding="utf-8"))
    consumers = [e for e in reg["composed"] if any(m["name"] == OLD for m in e["modules"])]
    print(f"{len(consumers)} TAPP(s) currently record {OLD}")
    bad = []
    for e in consumers:
        r = subprocess.run([sys.executable, os.path.join(ROOT, "Claude Skills for TAPP", "scripts",
                                                         "compose_tapp.py"),
                            "--source", e["tapp"], "--module", NEW, "--check"],
                           capture_output=True, text=True, cwd=ROOT)
        if r.returncode != 0:
            bad.append(os.path.basename(e["tapp"]))
    if bad:
        sys.exit(f"FATAL: {NEW} does not MATCH {len(bad)} consumer(s): {bad}. "
                 f"Compose them before swapping the register.")
    print(f"guard OK — {NEW} --check MATCHes all {len(consumers)} consumers; swap is pure bookkeeping")

    # ---- guard: nothing may 'requires' the retiring module ----
    needs = []
    for f in os.listdir(MODDIR):
        if f.endswith(".json") and f != f"Module_{OLD}.json":
            m = json.load(open(os.path.join(MODDIR, f), encoding="utf-8"))
            if OLD in (m.get("requires") or []):
                needs.append(m["module"])
    if needs:
        sys.exit(f"FATAL: {needs} still require {OLD}")
    print(f"guard OK — no module requires {OLD}")

    # ---- composed_tapps.json ----
    n = 0
    for e in reg["composed"]:
        for m in e["modules"]:
            if m["name"] == OLD:
                m["name"], m["version"] = NEW, NEWVER
                n += 1
    reg["generated"] = DATE
    print(f"\ncomposed_tapps.json: {n} entr(ies) {OLD} -> {NEW} v{NEWVER}")

    # ---- module register ----
    rows = list(csv.reader(open(MREG, newline="", encoding="utf-8-sig")))
    hdr = rows[0]
    core = json.load(open(os.path.join(MODDIR, "Module_Core.json"), encoding="utf-8"))
    nf = sum(len(b["fields"]) for b in core["blocks"])
    newrow = [NEW, "2", core["title"], str(nf), str(len(core["blocks"])), NEWVER,
              f"{len(consumers)} TAPP(s)", "active"]
    out = [hdr]
    for r in rows[1:]:
        if r and r[0].strip() == OLD:
            r[hdr.index("Consumers")] = "0 TAPP(s)"
            r[hdr.index("Status")] = f"retired {DATE} — superseded by {NEW}"
            print(f"module register: {OLD} -> retired")
        out.append(r)
    out.insert(1, newrow)
    out[1:] = sorted(out[1:], key=lambda r: r[0].lower())
    print(f"module register: + {NEW} (layer 2, {nf} fields, {len(core['blocks'])} blocks, "
          f"v{NEWVER}, {len(consumers)} consumers)")

    # ---- archive the retired module files ----
    moves = [(os.path.join(MODDIR, f"Module_{OLD}{ext}"), os.path.join(ARCH, f"Module_{OLD}{ext}"))
             for ext in (".csv", ".json")]
    for s, d in moves:
        print(f"archive: {os.path.relpath(s, ROOT)} -> {os.path.relpath(d, ROOT)}")

    if not apply:
        print("\n(dry run — pass --apply to write)")
        return

    with open(REG, "w", encoding="utf-8") as fh:
        json.dump(reg, fh, indent=2, ensure_ascii=False); fh.write("\n")
    with open(MREG, "w", newline="", encoding="utf-8-sig") as fh:
        csv.writer(fh).writerows(out)
    os.makedirs(ARCH, exist_ok=True)
    for s, d in moves:
        if os.path.exists(s):
            shutil.move(s, d)
    readme = os.path.join(ARCH, "README.md")
    if not os.path.exists(readme):
        open(readme, "w", encoding="utf-8").write(
            "# Superseded modules\n\nModules retired from `Claude Skills for TAPP/modules/`. Kept for "
            "provenance; **not live** and never composed. A TAPP version composed from one of these "
            "records it in `composed_tapps.json` under the name it had at the time.\n\n"
            f"- `Module_Group1` — retired {DATE}, superseded by `Module_Core`, which holds its 18 "
            "fields plus the 10 universals that belonged to no module. Retired rather than extended "
            "because Group1 used `replace_group` on Group 1, and the new fields sit in Groups 2-6.\n")
    print("\nwritten.")
    print("NEXT: re-run validate_tapp.py — expect 0 ERROR / 0 WARN")


if __name__ == "__main__":
    main()
