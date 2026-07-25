#!/usr/bin/env python3
"""Recursively enumerate a public Google Drive folder via the server-rendered
embeddedfolderview endpoint (no API key, no Blob, read-only)."""
import re, sys, json, time, subprocess

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')


def fetch(fid):
    for attempt in range(3):
        p = subprocess.run(['curl', '-sSL', '--max-time', '60', '-A', UA,
                            'https://drive.google.com/embeddedfolderview?id=%s#list' % fid],
                           capture_output=True, text=True)
        if p.returncode == 0 and p.stdout:
            return p.stdout
        time.sleep(2)
    return ''


def entries(html_txt):
    """Return [(id, title, is_folder)] parsed from the flip-entry markup."""
    out = []
    for block in re.split(r'(?=<div class="flip-entry"[^>]*id="entry-)', html_txt):
        m = re.search(r'id="entry-([A-Za-z0-9_-]+)"', block)
        if not m:
            continue
        t = re.search(r'<div class="flip-entry-title">([^<]*)</div>', block)
        if not t:
            continue
        is_dir = 'folder' in (re.search(r'flip-entry-icon"[^>]*>', block) or [''])[0] or \
                 'application/vnd.google-apps.folder' in block or \
                 not re.search(r'\.[A-Za-z0-9]{2,5}$', t.group(1))
        out.append((m.group(1), t.group(1), is_dir))
    return out


def walk(fid, name, depth=0, maxdepth=4, acc=None, path=''):
    if acc is None:
        acc = []
    if depth > maxdepth:
        return acc
    for eid, title, is_dir in entries(fetch(fid)):
        p = path + '/' + title
        if is_dir:
            sys.stderr.write('DIR  %s\n' % p)
            walk(eid, title, depth + 1, maxdepth, acc, p)
        else:
            acc.append({'path': p, 'name': title, 'id': eid})
    return acc


if __name__ == '__main__':
    root_id, root_name = sys.argv[1], sys.argv[2]
    res = walk(root_id, root_name, path='/' + root_name)
    json.dump(res, open('%s_tree.json' % root_name, 'w'), indent=1)
    print('%s: %d files' % (root_name, len(res)))
