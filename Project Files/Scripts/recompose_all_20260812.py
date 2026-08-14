#!/usr/bin/env python3
"""Recompose (or --check) every TAPP listed in composed_tapps.json.

Reads the recorded module list and block selections per TAPP so the composition is driven by
the register rather than by hand-typed flags — a mistyped block selection silently adds or
drops fields, which `--check` does not catch (see the note in compose_tapp.compose_overlay).

  --check   report MATCH / DIFFERS per TAPP x module chain, write nothing
  --apply   recompose in place
"""
import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # library root: this script lives in "Project Files/Scripts/"
COMPOSE = os.path.join(ROOT, "Claude Skills for TAPP", "scripts", "compose_tapp.py")


def module_flags(mods):
    out = []
    for m in mods:
        spec = m["name"]
        if m.get("blocks"):
            spec += ":" + (m["blocks"] if isinstance(m["blocks"], str)
                           else ",".join(m["blocks"]))
        out += ["--module", spec]
    return out


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    reg = json.load(open(os.path.join(ROOT, "composed_tapps.json")))
    n_ok = n_diff = n_err = 0
    for entry in reg["composed"]:
        tapp = entry["tapp"]
        path = os.path.join(ROOT, tapp)
        if not os.path.exists(path):
            print(f"MISSING  {tapp}")
            n_err += 1
            continue
        cmd = [sys.executable, COMPOSE, "--source", path] + module_flags(entry["modules"])
        cmd += ["--check"] if args.check else ["--out", path]
        p = subprocess.run(cmd, capture_output=True, text=True)
        tail = [l for l in p.stdout.splitlines() if l.strip()]
        verdict = "MATCH" if p.returncode == 0 else "DIFFERS"
        if p.returncode not in (0, 1):
            verdict = "ERROR"
            n_err += 1
        elif p.returncode == 0:
            n_ok += 1
        else:
            n_diff += 1
        mods = ",".join(m["name"] for m in entry["modules"])
        print(f"{verdict:8s} {os.path.basename(tapp):36s} [{mods}]")
        if verdict != "MATCH":
            for l in tail[-14:]:
                print("         " + l)
            if p.stderr.strip():
                print("         STDERR " + p.stderr.strip().splitlines()[-1])

    print(f"\n{n_ok} MATCH, {n_diff} DIFFERS, {n_err} ERROR")
    sys.exit(1 if n_err else 0)


if __name__ == "__main__":
    main()
