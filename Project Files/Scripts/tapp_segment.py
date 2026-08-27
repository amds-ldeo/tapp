import re
ABBR = [r'e\.g\.', r'i\.e\.', r'et al\.', r'cf\.', r'vs\.', r'approx\.', r'ca\.',
        r'Fig\.', r'Eq\.', r'No\.', r'wt\.', r'at\.', r'Dr\.', r'St\.', r'\bp\.']

def _protect(t):
    for i, a in enumerate(ABBR):
        t = re.sub(a, lambda m: m.group(0).replace('.', '\x00%d\x00' % i), t)
    return re.sub(r'(\d)\.(\d)', lambda m: m.group(1) + '\x00D\x00' + m.group(2), t)

def _restore(p):
    for i in range(len(ABBR)):
        p = p.replace('\x00%d\x00' % i, '.')
    return p.replace('\x00D\x00', '.')

_OPEN_BEFORE = " ([{-—/"          # what may precede an opening quote
_CLOSE_AFTER  = " .,;:)]}"        # what may follow a closing quote
QUOTE_OPENERS = "'‘\""           # what may open a quoted sentence

def sentences(t):
    """Split on . or ; followed by whitespace + a capital — but never inside
    parentheses or quotes, where semicolons separate list items, not sentences.

    An apostrophe only toggles quote state when it is acting as a quote
    delimiter.  A possessive or contraction ("the procedure's target") is
    preceded AND followed by a word character and is left alone; treating it
    as an opening quote used to suppress every later split in the cell.
    """
    t = _protect((t or "").strip())
    if not t:
        return []
    out, buf, depth, quote = [], [], 0, False
    i = 0
    n = len(t)
    while i < n:
        c = t[i]
        buf.append(c)
        if c in "([": depth += 1
        elif c in ")]": depth = max(0, depth - 1)
        elif c in "'‘’" and not depth:
            prev = t[i-1] if i else ''
            nxt = t[i+1] if i + 1 < n else ''
            if c == '‘':
                quote = True
            elif c == '’' and quote:
                quote = False
            elif not quote:
                # opening only at a word boundary, and not a possessive
                if (prev == '' or prev in _OPEN_BEFORE) and nxt not in ' ':
                    quote = True
            else:
                # closing only where a quote may legally end
                if nxt == '' or nxt in _CLOSE_AFTER:
                    quote = False
        if c in ".;" and depth == 0 and not quote:
            j = i + 1
            while j < n and t[j] == ' ':
                j += 1
            # A digit may begin a sentence ("0 indicates a focused beam", "1x1
            # indicates no binning") but only after a full stop: after a
            # semicolon a digit is the next item of a list ("; 200-600 nm for
            # XANES"), which must not be split.
            # As with digits, a sentence may open with a quoted term
            # ("'Standard SEM': dedicated electron-only column") — but only
            # after a full stop, never after a list-separating semicolon.
            if j > i + 1 and j < n and (t[j].isupper() or t[j] in "(—-"
                                        or ((t[j].isdigit() or t[j] in QUOTE_OPENERS)
                                            and c == ".")):
                out.append(_restore("".join(buf)).strip()); buf = []
        i += 1
    if buf:
        out.append(_restore("".join(buf)).strip())
    return [p for p in out if p]
