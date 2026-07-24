"""STAGE 1 — stream the CMS-2011A SIM (detector-level) MOD HDF5 files and build the
CORE3 feature table with T4's canonical PtYPhiM extractor, used verbatim.

Zero accumulation: each raw .h5 is deleted as soon as its part parquet is written.
GEN* files are excluded by construction: they carry no `pfcs` dataset and no
jec/jet_area/jet_max_nef/npv/quality columns, so the frozen 33-column schema is
not computable from them (the extractor would raise KeyError).
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from t4_hojd_extractor import extract_feature_row  # noqa: E402

WORK = HERE / "work"
PARTS = HERE / "sim" / "parts"
WORK.mkdir(exist_ok=True)
PARTS.mkdir(parents=True, exist_ok=True)

RECORDS = {
    "3341498": dict(subdataset="QCD300to470", pthat_min=300.0, pthat_max=470.0,
                    doi="10.5281/zenodo.3341498"),
    "3341500": dict(subdataset="QCD170to300", pthat_min=170.0, pthat_max=300.0,
                    doi="10.5281/zenodo.3341500"),
}


def build_tasks() -> list[dict]:
    tasks = []
    for rid, meta in RECORDS.items():
        rec = json.loads((HERE / f"rec_{rid}.json").read_text())
        for f in rec["files"]:
            key = f["key"]
            if not key.startswith("SIM"):
                continue  # GEN files have no pfcs -> schema not computable
            tasks.append(dict(
                record_id=rid, key=key, size=f["size"],
                md5=f["checksum"].split(":", 1)[1],
                url=f["links"]["self"], **meta,
            ))
    tasks.sort(key=lambda t: (-t["size"], t["key"]))  # big files first
    return tasks


def sha256_md5(path: Path) -> tuple[str, str]:
    s, m = hashlib.sha256(), hashlib.md5()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(8 << 20)
            if not b:
                break
            s.update(b)
            m.update(b)
    return s.hexdigest(), m.hexdigest()


def process(task: dict) -> dict:
    t0 = time.time()
    raw = WORK / task["key"]
    part = PARTS / (task["key"].replace(".h5", "") + ".parquet")
    if part.exists():
        try:
            import pyarrow.parquet as _pq
            pf = _pq.ParquetFile(part)
            n_cached = pf.metadata.num_rows
            sha_cached = _pq.read_table(
                part, columns=["source_file_sha256"]
            )["source_file_sha256"][0].as_py()
            return dict(task, status="ok", n_jets=n_cached, sha256=sha_cached,
                        seconds=0.0, cached=True)
        except Exception:
            part.unlink()  # truncated/corrupt -> redo

    # ---- reuse an already-verified download if present, else fetch ----
    sha = None
    if raw.exists() and raw.stat().st_size == task["size"]:
        s_, m_ = sha256_md5(raw)
        if m_ == task["md5"]:
            sha = s_

    last = "not attempted"
    while sha is None:
        for _ in range(4):
            if raw.exists():
                raw.unlink()
            r = subprocess.run(
                ["curl", "-sSL", "--fail", "--retry", "3", "--retry-delay", "3",
                 "--connect-timeout", "30", "--max-time", "3600",
                 "-o", str(raw), task["url"]],
                capture_output=True, text=True,
            )
            if r.returncode != 0:
                last = f"curl rc={r.returncode} {r.stderr[:200]}"
                continue
            if raw.stat().st_size != task["size"]:
                last = f"size {raw.stat().st_size} != {task['size']}"
                continue
            s_, m_ = sha256_md5(raw)
            if m_ != task["md5"]:
                last = f"md5 {m_} != zenodo {task['md5']}"
                continue
            sha = s_
            break
        if sha is None:
            if raw.exists():
                raw.unlink()
            return dict(task, status="ERROR", error=last, n_jets=0,
                        seconds=time.time() - t0)

    dl = time.time() - t0

    # ---- extract ----
    try:
        with h5py.File(raw, "r") as f:
            jets_f = f["jets_f"][:]
            jets_i = f["jets_i"][:]
            pfcs = f["pfcs"][:]
            pidx = f["pfcs_index"][:]
            jfc = list(f["jets_f"].attrs["cols"])
            jic = list(f["jets_i"].attrs["cols"])
            pfc = list(f["pfcs"].attrs["cols"])

        n_jets = int(jets_f.shape[0])
        assert len(pidx) == n_jets + 1, "pfcs_index length"
        assert int(pidx[0]) == 0 and int(pidx[-1]) == pfcs.shape[0], "pfcs_index bounds"

        rows = []
        for i in range(n_jets):
            lo, hi = int(pidx[i]), int(pidx[i + 1])
            row = extract_feature_row(
                sample="sim",
                source_subdataset=task["subdataset"],
                source_hdf5_path=str(raw),
                source_file_sha256=sha,
                jet_row_id=i,
                jets_f_row=jets_f[i],
                jets_i_row=jets_i[i],
                jet_pfcs=pfcs[lo:hi],
                jets_f_cols=jfc,
                jets_i_cols=jic,
                pfcs_cols=pfc,
            )
            row["pthat_min_GeV"] = task["pthat_min"]
            row["pthat_max_GeV"] = task["pthat_max"]
            rows.append(row)

        del jets_f, jets_i, pfcs, pidx
        df = pd.DataFrame(rows)
        del rows
        df.to_parquet(part, engine="pyarrow", compression="snappy", index=False)
        n = len(df)
        del df
    except Exception as e:  # noqa: BLE001
        if raw.exists():
            raw.unlink()
        return dict(task, status="ERROR", error=f"{type(e).__name__}: {e}",
                    n_jets=0, seconds=time.time() - t0)
    finally:
        if raw.exists():
            raw.unlink()  # zero accumulation

    return dict(task, status="ok", n_jets=n, sha256=sha,
                seconds=time.time() - t0, dl_seconds=dl)


def main() -> int:
    tasks = build_tasks()
    total_bytes = sum(t["size"] for t in tasks)
    print(f"[stage1] {len(tasks)} SIM files, {total_bytes/1e9:.2f} GB", flush=True)

    log = HERE / "parse_log_sim.txt"
    results = []
    cum = 0
    t0 = time.time()
    with open(log, "w") as lg:
        lg.write("# STAGE 1 CORE3 SIM parse log (T4 PtYPhiM convention)\n")
        lg.write("# filename\tbytes\tn_jets\tcum_jets\tsha256\tseconds\n")
        lg.flush()
        with ProcessPoolExecutor(max_workers=10) as ex:
            futs = {ex.submit(process, t): t for t in tasks}
            for fut in as_completed(futs):
                r = fut.result()
                results.append(r)
                if r["status"] == "ok":
                    cum += r["n_jets"]
                    lg.write(f"{r['key']}\t{r['size']}\t{r['n_jets']}\t{cum}\t"
                             f"{r['sha256']}\t{r['seconds']:.1f}\n")
                    print(f"  ok {r['key']} n={r['n_jets']} cum={cum} "
                          f"({r['seconds']:.0f}s)", flush=True)
                else:
                    lg.write(f"{r['key']}\t{r['size']}\tERROR\t{cum}\t-\t"
                             f"{r.get('error','')}\n")
                    print(f"  ERR {r['key']}: {r.get('error')}", flush=True)
                lg.flush()

    errs = [r for r in results if r["status"] != "ok"]
    print(f"[stage1] done {cum} jets, {len(errs)} errors, {time.time()-t0:.0f}s", flush=True)
    (HERE / "stage1_results.json").write_text(json.dumps(
        [{k: v for k, v in r.items() if k != "url"} for r in results], indent=1))
    return 1 if errs else 0


if __name__ == "__main__":
    raise SystemExit(main())
