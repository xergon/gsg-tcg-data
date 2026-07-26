import json, struct, subprocess, zlib, os, sys, hashlib
U="https://ndownloader.figshare.com/files/30913981"
ents={e['name']:e for e in json.load(open('fs_entries.json'))}
want=[n for n in ents if n.startswith('boydmeredith_piet_data/data/') and n.count('/')==2 and n.endswith('.mat')]
want+=[n for n in ents if n.startswith('boydmeredith_piet_data/results/fit_analytical_')]
want=sorted(want)
os.makedirs('fs_extract',exist_ok=True)
def rng(a,b):
    r=subprocess.run(['curl','-s','-L','-r',f'{a}-{b}',U],capture_output=True)
    return r.stdout
for n in want:
    e=ents[n]; out='fs_extract/'+os.path.basename(n)
    if os.path.exists(out) and os.path.getsize(out)==e['usize']:
        print('skip',n); continue
    lh=rng(e['lho'], e['lho']+29)
    assert lh[:4]==b'PK\x03\x04', (n, lh[:4])
    nlen,elen=struct.unpack('<HH', lh[26:30])
    data_off=e['lho']+30+nlen+elen
    raw=rng(data_off, data_off+e['csize']-1)
    if e['method']==8:
        d=zlib.decompressobj(-15); body=d.decompress(raw)+d.flush()
    else:
        body=raw
    crc=zlib.crc32(body)&0xffffffff
    ok = (crc==e['crc']) and (len(body)==e['usize'])
    open(out,'wb').write(body)
    print(f"{os.path.basename(n):32s} got={len(body):>11,} want={e['usize']:>11,} crc_ok={crc==e['crc']} OK={ok}")
