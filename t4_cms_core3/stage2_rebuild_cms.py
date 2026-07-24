"""STAGE 2 — rebuild the CMS real-data pfc_mass_GeV column under T4's canonical
PtYPhiM convention, leaving every other v0.1 column untouched.

Procedure:
  1. read the 18 MOD HDF5 containers named in v0.1's jet_row_id ("<container>:<idx>")
  2. re-stream each from Zenodo 3340205 and verify its sha256 against v0.1's
     source_file_sha256 for that container
  3. recompute the FULL feature row with the extractor (verbatim)
  4. match to v0.1 on jet_row_id
  5. assert the 27 recomputed non-mass columns still agree with v0.1 at the
     prior tolerances -- STOP if not
  6. emit v0.2 = v0.1 with ONLY pfc_mass_GeV replaced
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from t4_hojd_extractor import extract_feature_row  # noqa: E402

WORK = HERE / "work"
PARTS = HERE / "cms" / "parts"
PARTS.mkdir(parents=True, exist_ok=True)
V01 = HERE / "parity" / "v0_1.parquet"
RECORD = "3340205"

EXACT_COLS = ["fn", "rn", "lbn", "evn", "npv", "quality", "n_pfc_selected"]
RAW_COLS = ["jet_pt_GeV", "jet_eta", "jet_y", "jet_phi", "jet_m_GeV",
            "jec", "jet_area", "jet_max_nef", "weight_nb"]
PFC_COLS = ["pfc_pt_sum_GeV",
            "e2_beta_0p5", "e3_beta_0p5", "D2_beta_0p5",
            "e2_beta_1p0", "e3_beta_1p0", "D2_beta_1p0",
            "e2_beta_2p0", "e3_beta_2p0", "D2_beta_2p0"]


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
    """Recompute every jet of one CMS container; write a part parquet; delete raw."""
    t0 = time.time()
    raw = WORK / task["key"]
    part = PARTS / (task["key"].replace(".h5", "") + ".parquet")
    if part.exists():
        return dict(task, status="cached", n_jets=-1, seconds=0.0)

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

    # sha256 must match what v0.1 recorded for this container
    if sha != task["v01_sha256"]:
        raw.unlink()
        return dict(task, status="ERROR", n_jets=0, seconds=time.time() - t0,
                    error=f"sha256 {sha} != v0.1 {task['v01_sha256']}")

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
        assert len(pidx) == n_jets + 1
        assert int(pidx[0]) == 0 and int(pidx[-1]) == pfcs.shape[0]

        rows = []
        for i in range(n_jets):
            lo, hi = int(pidx[i]), int(pidx[i + 1])
            row = extract_feature_row(
                sample="CMS",
                source_subdataset="cms",
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
            row["jet_row_id"] = f"{task['key']}:{i}"  # v0.1 match key
            rows.append(row)

        del jets_f, jets_i, pfcs, pidx
        df = pd.DataFrame(rows)
        del rows
        keep = ["jet_row_id", "pfc_mass_GeV"] + EXACT_COLS + RAW_COLS + \
               ["corr_jet_pt_GeV"] + PFC_COLS
        df[keep].to_parquet(part, engine="pyarrow", compression="snappy", index=False)
        n = len(df)
        del df
    except Exception as e:  # noqa: BLE001
        return dict(task, status="ERROR", error=f"{type(e).__name__}: {e}",
                    n_jets=0, seconds=time.time() - t0)
    finally:
        if raw.exists():
            raw.unlink()

    return dict(task, status="ok", n_jets=n, sha256=sha, seconds=time.time() - t0)


def main() -> int:
    # ---- manifest from v0.1 itself ----
    man = pd.read_json(HERE / "cms_container_manifest.json")
    rec = json.loads((HERE / f"rec_{RECORD}.json").read_text())
    zfiles = {f["key"]: f for f in rec["files"]}

    tasks = []
    for _, r in man.iterrows():
        key = r["container"]
        if key not in zfiles:
            print(f"[stage2] FATAL: {key} not in Zenodo {RECORD}", flush=True)
            return 2
        zf = zfiles[key]
        tasks.append(dict(key=key, size=zf["size"],
                          md5=zf["checksum"].split(":", 1)[1],
                          url=zf["links"]["self"],
                          v01_sha256=r["source_file_sha256"],
                          v01_n_jets=int(r["n_jets"])))
    tasks.sort(key=lambda t: -t["size"])
    print(f"[stage2] {len(tasks)} CMS containers, "
          f"{sum(t['size'] for t in tasks)/1e9:.2f} GB", flush=True)

    results = []
    cum = 0
    t0 = time.time()
    with open(HERE / "parse_log_cms_v0_2.txt", "w") as lg:
        lg.write("# STAGE 2 CMS re-stream log (T4 PtYPhiM convention)\n")
        lg.write("# filename\tbytes\tn_jets\tcum_jets\tsha256\tsha256_matches_v0_1\tseconds\n")
        with ProcessPoolExecutor(max_workers=10) as ex:
            futs = {ex.submit(process, t): t for t in tasks}
            for fut in as_completed(futs):
                r = fut.result()
                results.append(r)
                if r["status"] == "ok":
                    cum += r["n_jets"]
                    lg.write(f"{r['key']}\t{r['size']}\t{r['n_jets']}\t{cum}\t"
                             f"{r['sha256']}\tTRUE\t{r['seconds']:.1f}\n")
                    print(f"  ok {r['key']} n={r['n_jets']} cum={cum}", flush=True)
                else:
                    lg.write(f"{r['key']}\t{r['size']}\tERROR\t{cum}\t-\t-\t"
                             f"{r.get('error','')}\n")
                    print(f"  ERR {r['key']}: {r.get('error')}", flush=True)
                lg.flush()

    errs = [r for r in results if r["status"] not in ("ok", "cached")]
    if errs:
        print(f"[stage2] STOP: {len(errs)} file errors", flush=True)
        return 2
    print(f"[stage2] re-stream done, {cum} jets, {time.time()-t0:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
