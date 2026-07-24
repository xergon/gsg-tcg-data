#!/usr/bin/env python3
"""Independently reconstruct V150 from the frozen V149 ring tables."""

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr


ROOT = Path(__file__).resolve().parent
FREEZE = ROOT / "V149_TO_V150_THEORY_EVOLUTION_FREEZE.json"
PARENT = ROOT / "V149_NGC3521_TRANSFER_RESULT.json"
RESULT = ROOT / "V150_NGC3521_CONTINUOUS_FRONT_SHEET_RESULT.json"
TABLES = {
    "natural": ROOT / "V149_NGC3521_NATURAL_OCTANT_RING_VALUES.csv",
    "robust": ROOT / "V149_NGC3521_ROBUST_OCTANT_RING_VALUES.csv",
}
OUTPUT = ROOT / "INDEPENDENT_V150_NGC3521_VERIFICATION.json"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path):
    output = {}
    with path.open(newline="", encoding="ascii") as handle:
        for row in csv.DictReader(handle):
            output[(row["sector"], int(row["ring_index"]))] = (
                float(row["r_center_kpc"]),
                float(row["q_mol_to_hi"]),
                row["eligible"] == "True",
            )
    return output


def crossing(rows, sector, pair):
    left_radius, left_q, left_ok = rows[(sector, pair[0])]
    right_radius, right_q, right_ok = rows[(sector, pair[1])]
    if not (left_ok and right_ok and left_q > 1.0 and right_q < 1.0):
        return None
    return left_radius + (left_q - 1.0) / (left_q - right_q) * (
        right_radius - left_radius
    )


def main():
    if OUTPUT.exists():
        raise RuntimeError("independent V150 verification already exists")
    freeze = json.loads(FREEZE.read_text(encoding="ascii"))
    parent = json.loads(PARENT.read_text(encoding="ascii"))
    reported = json.loads(RESULT.read_text(encoding="ascii"))
    tables = {name: load(path) for name, path in TABLES.items()}
    sectors = sorted(parent["sector_states"]["natural"])
    radii = {
        name: {
            sector: crossing(
                tables[name],
                sector,
                parent["sector_states"][name][sector]["crossing_ring_pair"],
            )
            for sector in sectors
        }
        for name in ("natural", "robust")
    }
    beam = freeze["solver_conventions"]["common_beam_kpc"]
    shifts = np.array(
        [
            (radii["robust"][sector] - radii["natural"][sector]) / beam
            for sector in sectors
        ],
        dtype=float,
    )
    rho = float(
        spearmanr(
            [radii["natural"][sector] for sector in sectors],
            [radii["robust"][sector] for sector in sectors],
        ).statistic
    )
    metrics = {
        "valid_interpolations": sum(
            radii[name][sector] is not None
            for name in ("natural", "robust")
            for sector in sectors
        )
        // 2,
        "max_abs_shift_beam": float(np.max(np.abs(shifts))),
        "median_abs_shift_beam": float(np.median(np.abs(shifts))),
        "within_quarter_beam_count": int(np.sum(np.abs(shifts) <= 0.25)),
        "median_signed_shift_beam": float(np.median(shifts)),
        "spearman_rho_front": rho,
    }
    gates = {
        "P150_P1_all_eight_valid_interpolations": metrics["valid_interpolations"] == 8,
        "P150_P2_max_abs_shift_at_most_one_beam": metrics["max_abs_shift_beam"] <= 1.0,
        "P150_P3_concentrated_within_quarter_beam": (
            metrics["median_abs_shift_beam"] <= 0.25
            and metrics["within_quarter_beam_count"] >= 6
        ),
        "P150_P4_order_and_signed_bias": (
            rho >= 0.90 and abs(metrics["median_signed_shift_beam"]) <= 0.15
        ),
    }
    checks = {
        "freeze_hash_matches": sha256(FREEZE)
        == reported["input_sha256"]["evolution_freeze"],
        "parent_hash_matches": sha256(PARENT)
        == reported["input_sha256"]["parent_result"],
        "natural_hash_matches": sha256(TABLES["natural"])
        == reported["input_sha256"]["natural_table"],
        "robust_hash_matches": sha256(TABLES["robust"])
        == reported["input_sha256"]["robust_table"],
        "radii_match": all(
            abs(radii[name][sector] - reported["front_radii_kpc"][name][sector])
            < 1e-12
            for name in ("natural", "robust")
            for sector in sectors
        ),
        "metrics_match": all(
            abs(metrics[key] - reported["metrics"][key]) < 1e-12
            for key in metrics
        ),
        "gates_match": gates == reported["gates"],
        "joint_pass_matches": all(gates.values()) == reported["joint_pass"],
        "disposition_matches": reported["exact_v150_disposition"]
        == "V150_RETROSPECTIVE_FIRST_DISCRIMINATOR_PASSES__FRESH_TARGET_REQUIRED",
    }
    output = {
        "created_utc": "2026-07-24T05:54:00Z",
        "verifier": "independent direct-CSV continuous q=1 interpolation; no import from run_v150_continuous_front_sheet.py",
        "checks": checks,
        "pass_count": sum(checks.values()),
        "check_count": len(checks),
        "all_pass": all(checks.values()),
        "reconstructed_metrics": metrics,
        "reconstructed_gates": gates,
        "input_sha256": {
            "freeze": sha256(FREEZE),
            "parent": sha256(PARENT),
            "natural": sha256(TABLES["natural"]),
            "robust": sha256(TABLES["robust"]),
            "result": sha256(RESULT),
        },
    }
    OUTPUT.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
    )
    print(json.dumps(output, indent=2, sort_keys=True))
    if not output["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
