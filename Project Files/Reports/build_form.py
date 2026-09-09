#!/usr/bin/env python3
"""Generate a procedure-registration webform mockup from a TAPP CSV + one literature column."""
import csv, json, re, io, sys

ROOT = "/Users/ruolin/Documents/Astromat/TAPPs/Current TAPPs/"

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
        val, note = prefill(x[ci] if len(x) > ci else '')
        cur['fields'].append({
            'name': name, 'desc': x[1].strip(), 'tier': x[2].strip(), 'dtype': x[4].strip(),
            'unit': unit(x[4]), 'opts': opts(x[4], x[5]), 'ex': x[5].strip(), 'key': x[8].strip(),
            'modes': {m: (g.strip().upper() == 'Y') for m, g in zip(modes, x[10:sentinel])},
            'val': val, 'note': note,
            'warn': cfg.get('warn', {}).get(name, '')})
    data = {'groups': groups, 'modes': modes, 'excluded': excluded,
            'perMember': cfg.get('perMember', {}), 'meta': cfg['meta']}
    data['meta'].update({'defaultMode': cfg['defaultMode'], 'sourceMode': cfg['sourceMode']})
    html = (io.open('_head.html', encoding='utf-8').read()
            + io.open('_body.html', encoding='utf-8').read()
              .replace('/*__DATA__*/', json.dumps(data, ensure_ascii=False)))
    io.open(cfg['out'], 'w', encoding='utf-8').write(html)
    nf = sum(len(g['fields']) for g in groups)
    pf = sum(1 for g in groups for f in g['fields'] if f['val'])
    print(f"{cfg['out']}: {nf} procedure-level fields, {pf} prefilled, {len(excluded)} excluded, modes={modes}")
    return data

if __name__ == '__main__':
    for c in json.load(io.open(sys.argv[1], encoding='utf-8')):
        build(c)
