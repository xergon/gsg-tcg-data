import scipy.io as sio, numpy as np, pyarrow as pa, pyarrow.parquet as pq
import glob, os, json, hashlib

def scal(a, cast):
    try:
        if a is None: return None
        arr=np.asarray(a).ravel()
        return cast(arr[0]) if arr.size else None
    except Exception: return None

def vec(a):
    try:
        if a is None: return []
        return np.asarray(a, dtype=np.float64).ravel().astype(np.float32).tolist()
    except Exception: return []

summary={}
for path in sorted(glob.glob('fs_extract/H*.mat')):
    rid=os.path.basename(path)[:-4]
    m=sio.loadmat(path, struct_as_record=False, squeeze_me=False)
    d=m['data'][0]
    n=len(d)
    cols={k:[] for k in ['rat_id','trial_idx','sessid','sessiondate','T','leftbups','rightbups',
                         'n_clicks_L','n_clicks_R','Delta','hit','gamma','pokedR','Hazard',
                         'genEndState','genSwitchTimes','n_switches','correctAnswer','evidenceRatio']}
    for i in range(n):
        o=d[i]
        L=vec(getattr(o,'leftbups',None)); R=vec(getattr(o,'rightbups',None))
        S=vec(getattr(o,'genSwitchTimes',None))
        sd=getattr(o,'sessiondate',None)
        try: sd=str(np.asarray(sd).ravel()[0])
        except Exception: sd=None
        cols['rat_id'].append(rid); cols['trial_idx'].append(i)
        cols['sessid'].append(scal(getattr(o,'sessid',None), int))
        cols['sessiondate'].append(sd)
        cols['T'].append(scal(getattr(o,'T',None), float))
        cols['leftbups'].append(L); cols['rightbups'].append(R)
        cols['n_clicks_L'].append(len(L)); cols['n_clicks_R'].append(len(R))
        cols['Delta'].append(scal(getattr(o,'Delta',None), int))
        cols['hit'].append(scal(getattr(o,'hit',None), int))
        cols['gamma'].append(scal(getattr(o,'gamma',None), float))
        cols['pokedR'].append(scal(getattr(o,'pokedR',None), int))
        cols['Hazard'].append(scal(getattr(o,'Hazard',None), int))
        cols['genEndState'].append(scal(getattr(o,'genEndState',None), int))
        cols['genSwitchTimes'].append(S); cols['n_switches'].append(len(S))
        cols['correctAnswer'].append(scal(getattr(o,'correctAnswer',None), int))
        cols['evidenceRatio'].append(scal(getattr(o,'evidenceRatio',None), float))
    schema=pa.schema([('rat_id',pa.string()),('trial_idx',pa.int32()),('sessid',pa.int32()),
        ('sessiondate',pa.string()),('T',pa.float32()),('leftbups',pa.list_(pa.float32())),
        ('rightbups',pa.list_(pa.float32())),('n_clicks_L',pa.int16()),('n_clicks_R',pa.int16()),
        ('Delta',pa.int16()),('hit',pa.int8()),('gamma',pa.float32()),('pokedR',pa.int8()),
        ('Hazard',pa.int8()),('genEndState',pa.int8()),('genSwitchTimes',pa.list_(pa.float32())),
        ('n_switches',pa.int16()),('correctAnswer',pa.int8()),('evidenceRatio',pa.float32())])
    tbl=pa.table({k:cols[k] for k in schema.names}, schema=schema)
    out=f'out/boydmeredith_piet_behaviour_{rid}.parquet'
    pq.write_table(tbl, out, compression='zstd', compression_level=9)
    sess=sorted(set(x for x in cols['sessid'] if x is not None))
    b=open(out,'rb').read()
    summary[rid]=dict(trials=n, sessions=len(sess),
        parquet_bytes=len(b), sha256=hashlib.sha256(b).hexdigest(),
        uncompressed_bytes=int(tbl.nbytes), file=os.path.basename(out))
    print(f'{rid}: trials={n:>7,} sessions={len(sess):>4} parquet={len(b):>12,} uncompressed={tbl.nbytes:>13,}')
json.dump(summary, open('out/_shards.json','w'), indent=1)
print('TOTAL trials:', sum(v['trials'] for v in summary.values()))
