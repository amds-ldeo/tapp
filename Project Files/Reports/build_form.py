#!/usr/bin/env python3
"""Generate a procedure-registration webform mockup from a TAPP CSV + one literature column."""
import csv, json, re, io, os, sys
from pathlib import Path

# Resolved from THIS FILE, never the working directory and never hardcoded to one
# machine: the same lesson as check_field_ownership.py, which exists because a
# relative glob silently matched nothing and printed a confident wrong answer.
HERE = Path(__file__).resolve().parent
ROOT = str(HERE.parents[1] / "Current TAPPs") + os.sep
# The keyed-value notation (conventions 7.3.4) is parsed by the one shared grammar, not re-implemented.
sys.path.insert(0, str(HERE.parents[1] / "Claude Skills for TAPP" / "scripts"))
import keyed_cells as K

def unit(E):
    m = re.search(r'Numeric(?: pair)?\s*\(([^)]+)\)', E)
    return m.group(1) if m else ''

def opts(E, F):
    if 'Controlled list' not in E: return []
    out = []
    for o in F.split('|'):
        o = o.strip()
        if not o or o.startswith('e.g.'): continue
        # Defensive: strip bracketing quotes from a vocabulary member. Analytical Mode
        # carried these until 2026-09-09 (harmonise_analytical_mode_colf); no live TAPP
        # does now, but a quoted list must still compare on the bare value.
        if len(o) > 1 and o[0] == o[-1] and o[0] in "'\"": o = o[1:-1].strip()
        out.append(o)
    return out

def prefill(raw):
    """Blank and 'N' mean different things: not yet assessed vs assessed and not stated."""
    v = raw.strip()
    if not v:            return '', 'not yet assessed against this source'
    if v == 'N':         return '', 'not stated in source'
    m = re.match(r'^N\s*[-(;]\s*(.*?)\)?$', v)
    if m:                return '', m.group(1).rstrip(')')
    return v, ''

def build(cfg):
    rows = list(csv.reader(io.open(ROOT + cfg['csv'], newline='', encoding='utf-8-sig')))
    hdr, ci = rows[0], cfg['litcol']
    sentinel = hdr.index('Literature Assessment')
    modes = [h.strip() for h in hdr[10:sentinel]]
    groups, cur, excluded = [], None, []
    for x in rows[1:]:
        if not x or not x[0].strip(): continue
        name = x[0].strip()
        if re.match(r'^\d+\.', name):
            cur = {'title': name, 'fields': []}; groups.append(cur); continue
        if x[2].strip() == 'N/A':
            excluded.append(name); continue
        raw = x[ci] if len(x) > ci else ''
        struct, comment = K.split_commentary(raw)
        val, note = prefill(struct)
        if comment:
            note = (note + ' — ' if note else '') + 'Source: ' + comment
        cur['fields'].append({
            'name': name, 'desc': x[1].strip(), 'tier': x[2].strip(), 'dtype': x[4].strip(),
            'unit': unit(x[4]), 'opts': opts(x[4], x[5]), 'ex': x[5].strip(), 'key': x[8].strip(),
            'modes': {m: (g.strip().upper() == 'Y') for m, g in zip(modes, x[10:sentinel])},
            'val': val, 'note': note,
            'warn': cfg.get('warn', {}).get(name, '')})
    # Definer members and per-member values, read from the cells (7.3.4) instead of a hand-typed map.
    fields = [f for g in groups for f in g['fields']]
    doms = {}
    for f in fields:
        kind, d = K.procedure_domains(f['key'])
        if kind in ('definer', 'definer_per') and f['val']:
            ms, errs = K.parse_definer(f['val'])
            if not errs:
                f['members'] = [m for m, _ in ms]
                doms[d[0]] = f['members']
    definer_of = {K.procedure_domains(f['key'])[1][0]: f['key'] for f in fields
                  if K.procedure_domains(f['key'])[0] in ('definer', 'definer_per')}
    for f in fields:
        kind, d = K.procedure_domains(f['key'])
        if kind == 'plain' and len(d) == 1 and f['val'] and d[0] in doms:
            allv, per = K.values_by_member(f['val'], doms[d[0]])
            if allv is not None:
                f['val'] = allv
            elif any(per.values()):          # nothing matched a member: keep the text as written
                f['per'] = per
                f['val'] = ''
        elif kind == 'plain' and len(d) == 2 and f['val'] and d[1] in doms:
            # A x B written `all [b: v; ...]`: the value does not vary over A, so show it per B.
            ents, errs = K.parse_keyed(f['val'], levels=2)
            if not errs and len(ents) == 1 and [K.norm(n) for n in ents[0][0]] == ['all']:
                inner = '; '.join('%s: %s' % (', '.join(ns), v) for ns, v in ents[0][1])
                allv, per = K.values_by_member(inner, doms[d[1]])
                if allv is not None:
                    f['val'] = allv
                elif any(per.values()):
                    f['per'], f['perKey'], f['val'] = per, d[1], ''
    data = {'groups': groups, 'modes': modes, 'excluded': excluded,
            'perMember': cfg.get('perMember', {}), 'definerOf': definer_of, 'meta': cfg['meta']}
    data['meta'].update({'defaultMode': cfg['defaultMode'], 'sourceMode': cfg['sourceMode']})
    html = (io.open(HERE / '_head.html', encoding='utf-8').read()
            + io.open(HERE / '_body.html', encoding='utf-8').read()
              .replace('/*__DATA__*/', json.dumps(data, ensure_ascii=False)))
    io.open(HERE / cfg['out'], 'w', encoding='utf-8').write(html)
    nf = sum(len(g['fields']) for g in groups)
    pf = sum(1 for g in groups for f in g['fields'] if f['val'] or f.get('per'))
    print(f"{cfg['out']}: {nf} procedure-level fields, {pf} prefilled, {len(excluded)} excluded, modes={modes}")
    return data

if __name__ == '__main__':
    for c in json.load(io.open(sys.argv[1], encoding='utf-8')):
        build(c)
