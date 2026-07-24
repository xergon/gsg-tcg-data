#!/usr/bin/env python3
"""Execute the frozen V150 continuous front-sheet discriminator."""

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr


ROOT = Path(__file__).resolve().parent
FREEZE = ROOT / "V149_TO_V150_THEORY_EVOLUTION_FREEZE.json"
PARENT = ROOT / "V149_NGC3521_TRANSFER_RESULT.json"
TABLES = {
    "natural": ROOT / "V149_NGC3521_NATURAL_OCTANT_RING_VALUES.csv",
    "robust": ROOT / "V149_NGC3521_ROBUST_OCTANT_RING_VALUES.csv",
}
OUTPUT = ROOT / "V150_NGC3521_CONTINUOUS_FRONT_SHEET_RESULT.json"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_rows(path):
    rows = {}
    with path.open(newline="", encoding="ascii") as handle:
        for row in csv.DictReader(handle):
            rows[(row["sector"], int(row["ring_index"]))] = {
                "radius": float(row["r_center_kpc"]),
                "q": float(row["q_mol_to_hi"]),
                "eligible": row["eligible"] == "True",
            }
    return rows


def interpolate(rows, sector, pair):
    left = rows[(sector, pair[0])]
    right = rows[(sector, pair[1])]
    if not (
        left["eligible"]
        and right["eligible"]
        and left["q"] > 1.0
        and right["q"] < 1.0
        and left["radius"] < right["radius"]
    ):
        return None
    fraction = (left["q"] - 1.0) / (left["q"] - right["q"])
    return left["radius"] + fraction * (right["radius"] - left["radius"])


def main():
    if OUTPUT.exists():
        raise RuntimeError("V150 result already exists")
    freeze = json.loads(FREEZE.read_text(encoding="ascii"))
    parent = json.loads(PARENT.read_text(encoding="ascii"))
    rows = {name: load_rows(path) for name, path in TABLES.items()}
    sectors = sorted(parent["sector_states"]["natural"])
    radii = {"natural": {}, "robust": {}}
    valid = {}
    for sector in sectors:
        valid[sector] = True
        for name in ("natural", "robust"):
            pair = parent["sector_states"][name][sector]["crossing_ring_pair"]
            radius = interpolate(rows[name], sector, pair) if pair else None
            radii[name][sector] = radius
            valid[sector] = valid[sector] and radius is not None

    beam_kpc = freeze["solver_conventions"]["common_beam_kpc"]
    deltas = {
        sector: (
            (radii["robust"][sector] - radii["natural"][sector]) / beam_kpc
            if valid[sector]
            else None
        )
        for sector in sectors
    }
    finite_sectors = [sector for sector in sectors if deltas[sector] is not None]
    signed = np.array([deltas[sector] for sector in finite_sectors], dtype=float)
    absolute = np.abs(signed)
    rho = (
        float(
            spearmanr(
                [radii["natural"][sector] for sector in finite_sectors],
                [radii["robust"][sector] for sector in finite_sectors],
            ).statistic
        )
        if len(finite_sectors) == 8
        else None
    )
    metrics = {
        "valid_interpolations": len(finite_sectors),
        "max_abs_shift_beam": float(np.max(absolute)) if len(absolute) else None,
        "median_abs_shift_beam": float(np.median(absolute)) if len(absolute) else None,
        "within_quarter_beam_count": int(np.sum(absolute <= 0.25)),
        "median_signed_shift_beam": float(np.median(signed)) if len(signed) else None,
        "spearman_rho_front": rho,
    }
    gates = {
        "P150_P1_all_eight_valid_interpolations": len(finite_sectors) == 8,
        "P150_P2_max_abs_shift_at_most_one_beam": (
            metrics["max_abs_shift_beam"] is not None
            and metrics["max_abs_shift_beam"] <= 1.0
        ),
        "P150_P3_concentrated_within_quarter_beam": (
            metrics["median_abs_shift_beam"] is not None
            and metrics["median_abs_shift_beam"] <= 0.25
            and metrics["within_quarter_beam_count"] >= 6
        ),
        "P150_P4_order_and_signed_bias": (
            rho is not None
            and rho >= 0.90
            and abs(metrics["median_signed_shift_beam"]) <= 0.15
        ),
    }
    joint = all(gates.values())
    result = {
        "created_utc": "2026-07-24T05:52:00Z",
        "output_label": "THEORY_EVOLUTION",
        "parent_theory_id": "STAGE_E2_CENSORED_FRONT_STATE_TRANSPORT_V149",
        "successor_theory_id": "STAGE_E2_CONTINUOUS_FRONT_SHEET_TRANSPORT_V150",
        "target": "NGC3521",
        "front_radii_kpc": radii,
        "normalized_shifts_by_sector": deltas,
        "metrics": metrics,
        "gates": gates,
        "joint_pass": joint,
        "exact_v150_disposition": (
            "V150_RETROSPECTIVE_FIRST_DISCRIMINATOR_PASSES__FRESH_TARGET_REQUIRED"
            if joint
            else "KILL_EXACT_V150_ON_RETROSPECTIVE_NGC3521_DISCRIMINATOR__FURTHER_EVOLUTION_REQUIRED"
        ),
        "input_sha256": {
            "evolution_freeze": sha256(FREEZE),
            "parent_result": sha256(PARENT),
            "natural_table": sha256(TABLES["natural"]),
            "robust_table": sha256(TABLES["robust"]),
        },
        "credit": "Retrospective same-pulse first discriminator only; no prospective V150 credit.",
        "thread_status": "ACTIVE",
        "theory_lineage_status": "ACTIVE",
    }
    OUTPUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
