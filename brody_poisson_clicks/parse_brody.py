#!/usr/bin/env python3
"""
Stream-parse the 515 .mat files inside Brody Poisson-clicks zip -> per-trial parquet shards.
Does NOT extract zip to disk. Handles both scipy loadmat and HDF5 (v7.3) via h5py.
"""
import io
import os
import sys
import json
import time
import zipfile
import hashlib
import traceback
from datetime import datetime, timezone

import numpy as np
import scipy.io
import h5py
import pyarrow as pa
import pyarrow.parquet as pq
import inflate64


def _read_member_bytes(zf: zipfile.ZipFile, info: zipfile.ZipInfo) -> bytes:
    """Read a zip member's uncompressed bytes, handling DEFLATE64 (method 9) via inflate64."""
    if info.compress_type != 9:
        with zf.open(info, "r") as fh:
            return fh.read()
    # DEFLATE64: pull raw bytes from disk and inflate manually
    with open(zf.filename, "rb") as raw:
        raw.seek(info.header_offset)
        header = raw.read(30)  # local file header fixed part
        if header[:4] != b"PK\x03\x04":
            raise RuntimeError("bad local file header signature")
        fn_len = int.from_bytes(header[26:28], "little")
        ex_len = int.from_bytes(header[28:30], "little")
        raw.read(fn_len + ex_len)
        compressed = raw.read(info.compress_size)
    infl = inflate64.Inflater()
    out = infl.inflate(compressed)
    # ensure fully drained
    while not infl.eof:
        chunk = infl.inflate(b"")
        if not chunk:
            break
        out += chunk
    if len(out) != info.file_size:
        raise RuntimeError(
            f"inflate size mismatch: got {len(out)}, expected {info.file_size}"
        )
    return out

ZIP_PATH = sys.argv[1]
OUT_DIR = sys.argv[2]
os.makedirs(OUT_DIR, exist_ok=True)

LOG_PATH = os.path.join(OUT_DIR, "parse_log.txt")
SUMMARY_PATH = os.path.join(OUT_DIR, "SUMMARY.json")

SCHEMA = pa.schema([
    ("rat_id", pa.string()),
    ("trial_idx", pa.int32()),
    ("n_clicks_L", pa.int16()),
    ("n_clicks_R", pa.int16()),
    ("click_times_L", pa.list_(pa.float32())),
    ("click_times_R", pa.list_(pa.float32())),
    ("choice_R", pa.int8()),
    ("correct", pa.int8()),
    ("stim_duration_s", pa.float32()),
    ("gamma", pa.float32()),
    ("reward_rule", pa.int16()),
])

log_f = open(LOG_PATH, "w")
def log(msg):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    log_f.write(line + "\n")
    log_f.flush()


def _to_1d(x):
    """Coerce a matlab array/scalar to flat 1D python list of floats."""
    if x is None:
        return []
    a = np.asarray(x)
    if a.dtype == object:
        # cell array of arrays: each cell is per-trial click list
        return a
    a = a.squeeze()
    if a.ndim == 0:
        return np.array([a.item()], dtype=np.float32)
    return a.astype(np.float32, copy=False)


def _scalar(x):
    if x is None:
        return None
    a = np.asarray(x).squeeze()
    if a.ndim == 0:
        return a.item()
    if a.size == 1:
        return a.item()
    return a


def _cell_or_row(x, n_trials):
    """
    Turn per-trial click-times storage into a list of length n_trials of numpy arrays.
    Handles: (a) object array (cell) length n_trials, (b) numeric array (rare fallback).
    """
    if x is None:
        return [np.array([], dtype=np.float32)] * n_trials
    a = np.asarray(x)
    if a.dtype == object:
        a = a.squeeze()
        if a.ndim == 0:
            return [np.asarray(a.item(), dtype=np.float32).ravel()] * n_trials
        out = []
        for cell in a.ravel():
            if cell is None:
                out.append(np.array([], dtype=np.float32))
            else:
                arr = np.asarray(cell, dtype=np.float32).ravel()
                out.append(arr)
        return out
    # numeric: assume single-trial or already aggregated -- unlikely for this dataset
    a = a.squeeze()
    if a.ndim == 0:
        return [np.array([a.item()], dtype=np.float32)] * n_trials
    if a.ndim == 1:
        return [a.astype(np.float32, copy=False)]
    # 2D: treat rows as trials
    return [row.astype(np.float32, copy=False) for row in a]


def parse_mat_scipy(buf):
    """Try scipy.io.loadmat (v5/v7). Returns dict `ratdata` or raises."""
    m = scipy.io.loadmat(buf, squeeze_me=False, struct_as_record=False)
    if "ratdata" not in m:
        raise KeyError("no ratdata in mat")
    rd = m["ratdata"]
    # scipy returns 1x1 object array of mat_struct
    if isinstance(rd, np.ndarray):
        rd = rd.flat[0]
    return rd


def parse_mat_h5(buf):
    """Fallback for v7.3 (HDF5) mat files."""
    # h5py needs a file-like with .read supporting seek; BytesIO is fine
    buf.seek(0)
    return h5py.File(buf, "r")


def extract_records_scipy(ratdata, rat_id):
    """Extract per-trial rows from ratdata.parsed[0,0]."""
    if not hasattr(ratdata, "_fieldnames") or "parsed" not in ratdata._fieldnames:
        raise KeyError("no ratdata.parsed")
    parsed_arr = getattr(ratdata, "parsed")
    if isinstance(parsed_arr, np.ndarray):
        parsed = parsed_arr.flat[0]
    else:
        parsed = parsed_arr
    fields = parsed._fieldnames if hasattr(parsed, "_fieldnames") else []

    def gf(name):
        return getattr(parsed, name, None) if name in fields else None

    bt_arr = gf("bt")  # object ndarray shape (1, N)
    if bt_arr is None:
        raise KeyError("no parsed.bt")
    bt_arr = np.asarray(bt_arr).ravel()  # length N of (1,1) object arrays

    gr = np.asarray(gf("gr")).ravel() if gf("gr") is not None else None
    hh = np.asarray(gf("hh")).ravel() if gf("hh") is not None else None
    sd = np.asarray(gf("sd")).ravel() if gf("sd") is not None else None
    nL = np.asarray(gf("nL")).ravel() if gf("nL") is not None else None
    nR = np.asarray(gf("nR")).ravel() if gf("nR") is not None else None
    ga = np.asarray(gf("ga")).ravel() if gf("ga") is not None else None
    rg = np.asarray(gf("rg")).ravel() if gf("rg") is not None else None

    n_trials = int(bt_arr.size)
    for arr in (gr, hh, sd, nL, nR):
        if arr is not None:
            n_trials = min(n_trials, int(arr.size))

    rows = {
        "rat_id": [rat_id] * n_trials,
        "trial_idx": np.arange(n_trials, dtype=np.int32),
        "n_clicks_L": np.zeros(n_trials, dtype=np.int16),
        "n_clicks_R": np.zeros(n_trials, dtype=np.int16),
        "click_times_L": [None] * n_trials,
        "click_times_R": [None] * n_trials,
        "choice_R": np.full(n_trials, -1, dtype=np.int8),
        "correct": np.full(n_trials, -1, dtype=np.int8),
        "stim_duration_s": np.full(n_trials, np.nan, dtype=np.float32),
        "gamma": np.full(n_trials, np.nan, dtype=np.float32),
        "reward_rule": np.full(n_trials, -1, dtype=np.int16),
    }

    def _sv(arr, i, default=np.nan):
        if arr is None or i >= arr.size:
            return default
        v = arr.flat[i]
        try:
            return float(v)
        except Exception:
            return default

    for i in range(n_trials):
        cell = bt_arr[i]
        # cell is (1,1) object ndarray wrapping a mat_struct with .left .right
        inner = cell.flat[0] if isinstance(cell, np.ndarray) else cell
        try:
            left = np.asarray(getattr(inner, "left"), dtype=np.float32).ravel()
        except AttributeError:
            left = np.array([], dtype=np.float32)
        try:
            right = np.asarray(getattr(inner, "right"), dtype=np.float32).ravel()
        except AttributeError:
            right = np.array([], dtype=np.float32)
        rows["click_times_L"][i] = left
        rows["click_times_R"][i] = right
        rows["n_clicks_L"][i] = int(nL.flat[i]) if nL is not None and i < nL.size else int(left.size)
        rows["n_clicks_R"][i] = int(nR.flat[i]) if nR is not None and i < nR.size else int(right.size)
        v = _sv(gr, i)
        rows["choice_R"][i] = int(v) if np.isfinite(v) else -1
        v = _sv(hh, i)
        rows["correct"][i] = int(v) if np.isfinite(v) else -1
        rows["stim_duration_s"][i] = _sv(sd, i)
        rows["gamma"][i] = _sv(ga, i)
        v = _sv(rg, i)
        rows["reward_rule"][i] = int(v) if np.isfinite(v) else -1

    return rows, n_trials


def _h5_dataset(g, name):
    if name not in g:
        return None
    return g[name]


def _h5_load_refs_1d(h5file, ds):
    """Load a 1D object array of h5 references -> list of numpy float32 arrays."""
    out = []
    arr = ds[()]
    # arr shape may be (1, N) or (N, 1) or (N,)
    arr = np.asarray(arr).ravel()
    for ref in arr:
        if not ref:
            out.append(np.array([], dtype=np.float32))
            continue
        try:
            sub = h5file[ref][()]
            sub = np.asarray(sub, dtype=np.float32).ravel()
            out.append(sub)
        except Exception:
            out.append(np.array([], dtype=np.float32))
    return out


def _h5_flat_1d(ds):
    arr = np.asarray(ds[()]).ravel()
    return arr


def extract_records_h5(f, rat_id):
    """v7.3 HDF5 layout: /ratdata/parsed/{bt,gr,hh,sd,nL,nR,ga,rg}, bt has left/right refs per trial."""
    if "ratdata" not in f:
        raise KeyError("no ratdata")
    root = f["ratdata"]
    # In v7.3, ratdata is often stored as a group; parsed is a nested group or a ref array.
    if "parsed" in root:
        g = root["parsed"]
    else:
        g = root  # fallback: fields directly under ratdata
    if "bt" not in g:
        raise KeyError("no bt")
    bt = g["bt"]
    left_ds = _h5_dataset(bt, "left")
    right_ds = _h5_dataset(bt, "right")
    if left_ds is None or right_ds is None:
        raise KeyError("no bt.left/right")

    def _get(name):
        ds = _h5_dataset(g, name)
        return None if ds is None else _h5_flat_1d(ds)

    gr = _get("gr")
    hh = _get("hh")
    sd = _get("sd")
    nL = _get("nL")
    nR = _get("nR")
    ga = _get("ga")
    rg = _get("rg")

    left_list = _h5_load_refs_1d(f, left_ds)
    right_list = _h5_load_refs_1d(f, right_ds)
    n_trials = min(len(left_list), len(right_list))
    for arr in (gr, hh, sd, nL, nR):
        if arr is not None:
            n_trials = min(n_trials, arr.size)

    rows = {
        "rat_id": [rat_id] * n_trials,
        "trial_idx": np.arange(n_trials, dtype=np.int32),
        "n_clicks_L": np.zeros(n_trials, dtype=np.int16),
        "n_clicks_R": np.zeros(n_trials, dtype=np.int16),
        "click_times_L": [None] * n_trials,
        "click_times_R": [None] * n_trials,
        "choice_R": np.full(n_trials, -1, dtype=np.int8),
        "correct": np.full(n_trials, -1, dtype=np.int8),
        "stim_duration_s": np.full(n_trials, np.nan, dtype=np.float32),
        "gamma": np.full(n_trials, np.nan, dtype=np.float32),
        "reward_rule": np.full(n_trials, -1, dtype=np.int16),
    }
    def _sv(arr, i, default=np.nan):
        if arr is None or i >= arr.size:
            return default
        try:
            return float(arr.flat[i])
        except Exception:
            return default
    for i in range(n_trials):
        lt = np.asarray(left_list[i], dtype=np.float32).ravel()
        rt = np.asarray(right_list[i], dtype=np.float32).ravel()
        rows["click_times_L"][i] = lt
        rows["click_times_R"][i] = rt
        rows["n_clicks_L"][i] = int(nL.flat[i]) if nL is not None and i < nL.size else int(lt.size)
        rows["n_clicks_R"][i] = int(nR.flat[i]) if nR is not None and i < nR.size else int(rt.size)
        v = _sv(gr, i)
        rows["choice_R"][i] = int(v) if np.isfinite(v) else -1
        v = _sv(hh, i)
        rows["correct"][i] = int(v) if np.isfinite(v) else -1
        rows["stim_duration_s"][i] = _sv(sd, i)
        rows["gamma"][i] = _sv(ga, i)
        v = _sv(rg, i)
        rows["reward_rule"][i] = int(v) if np.isfinite(v) else -1

    return rows, n_trials


def rows_to_table(rows):
    return pa.table(
        {
            "rat_id": pa.array(rows["rat_id"], type=pa.string()),
            "trial_idx": pa.array(rows["trial_idx"], type=pa.int32()),
            "n_clicks_L": pa.array(rows["n_clicks_L"], type=pa.int16()),
            "n_clicks_R": pa.array(rows["n_clicks_R"], type=pa.int16()),
            "click_times_L": pa.array(rows["click_times_L"], type=pa.list_(pa.float32())),
            "click_times_R": pa.array(rows["click_times_R"], type=pa.list_(pa.float32())),
            "choice_R": pa.array(rows["choice_R"], type=pa.int8()),
            "correct": pa.array(rows["correct"], type=pa.int8()),
            "stim_duration_s": pa.array(rows["stim_duration_s"], type=pa.float32()),
            "gamma": pa.array(rows["gamma"], type=pa.float32()),
            "reward_rule": pa.array(rows["reward_rule"], type=pa.int16()),
        },
        schema=SCHEMA,
    )


def main():
    t0 = time.time()
    total_rows = 0
    per_rat_trials = {}
    n_ok = 0
    n_err = 0

    # Single parquet writer, ZSTD-compressed
    parquet_path = os.path.join(OUT_DIR, "brody_poisson_clicks_trials.parquet")
    writer = pq.ParquetWriter(parquet_path, SCHEMA, compression="zstd", compression_level=9)

    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        infos = [i for i in zf.infolist() if i.filename.lower().endswith(".mat")]
        log(f"found {len(infos)} .mat members")
        for idx, info in enumerate(infos):
            m = info.filename
            rat_id = os.path.splitext(os.path.basename(m))[0]
            try:
                data = _read_member_bytes(zf, info)
                buf = io.BytesIO(data)
                # try scipy first
                try:
                    rd = parse_mat_scipy(buf)
                    rows, ntr = extract_records_scipy(rd, rat_id)
                except NotImplementedError:
                    # v7.3
                    buf2 = io.BytesIO(data)
                    with parse_mat_h5(buf2) as f:
                        rows, ntr = extract_records_h5(f, rat_id)
                except Exception as e:
                    # try h5 anyway
                    try:
                        buf2 = io.BytesIO(data)
                        with parse_mat_h5(buf2) as f:
                            rows, ntr = extract_records_h5(f, rat_id)
                    except Exception as e2:
                        raise RuntimeError(f"scipy_err={e!r}; h5_err={e2!r}")

                if ntr == 0:
                    log(f"WARN {rat_id}: 0 trials")
                tbl = rows_to_table(rows)
                writer.write_table(tbl)
                total_rows += ntr
                per_rat_trials[rat_id] = ntr
                n_ok += 1
                if (idx + 1) % 25 == 0 or idx < 3:
                    log(f"progress {idx+1}/{len(infos)} rat={rat_id} ntr={ntr} cum_rows={total_rows}")
            except Exception as e:
                n_err += 1
                log(f"ERR {rat_id}: {e}\n{traceback.format_exc().splitlines()[-1]}")

    writer.close()

    # sha256 + size
    h = hashlib.sha256()
    sz = 0
    with open(parquet_path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
            sz += len(chunk)

    trials = list(per_rat_trials.values())
    summary = {
        "n_rats_parsed": n_ok,
        "n_rats_failed": n_err,
        "n_trials_total": int(total_rows),
        "min_trials_per_rat": int(min(trials)) if trials else 0,
        "max_trials_per_rat": int(max(trials)) if trials else 0,
        "median_trials_per_rat": int(np.median(trials)) if trials else 0,
        "parquet_bytes": sz,
        "parquet_sha256": h.hexdigest(),
        "parquet_filename": os.path.basename(parquet_path),
        "parse_date_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": {
            "zenodo_record": "13352119",
            "zip_md5": "9bac21f991137ead56a0bc83ae62c49c",
            "zip_bytes": 8104686746,
            "license": "CC-BY-4.0",
        },
        "wall_seconds": round(time.time() - t0, 1),
    }
    with open(SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=2)
    log(f"DONE {json.dumps(summary)}")
    log_f.close()


if __name__ == "__main__":
    main()
