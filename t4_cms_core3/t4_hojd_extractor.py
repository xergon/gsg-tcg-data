"""T4 canonical HOJD feature extractor — supplied verbatim by ChatGPT thread T4
(assistant turn 745799c9, 2026-07-24), reconstructed from the thread's code block.

The ONLY reconstructed fragment is the PFC-selection mask inside compute_pfc_features
(the browser content-scrubber blocked that ~180-char slice). T4 stated the selection
in plain English in the same message: "PFC selection: vertex == 0, pt >= 0.5 GeV.
No JEC on individual PFCs. weight_nb = raw jets_f['weight'], no EnergyFlow k-factor."
The v0.1 PARITY SELF-TEST (n_pfc_selected exact; e2/e3/D2 rtol<=1e-10 vs the delivered
v0.1 parquet) is the validator: if this reconstruction is wrong, parity fails loudly.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

import numpy as np


BETAS: tuple[tuple[float, str], ...] = (
    (0.5, "0p5"),
    (1.0, "1p0"),
    (2.0, "2p0"),
)


def _decode_name(value: Any) -> str:
    if isinstance(value, (bytes, np.bytes_)):
        return value.decode("utf-8")
    return str(value)


def _column_map(columns: Sequence[Any]) -> dict[str, int]:
    return {_decode_name(name): i for i, name in enumerate(columns)}


def _require_columns(
    column_map: dict[str, int],
    required: Sequence[str],
    array_name: str,
) -> None:
    missing = [name for name in required if name not in column_map]
    if missing:
        raise KeyError(f"{array_name} is missing required columns: {missing}")


def compute_pfc_features(
    jet_pfcs: np.ndarray,
    pfcs_cols: Sequence[Any],
) -> dict[str, float | int]:
    """
    Compute the frozen PFC-level HOJD features for one jet.

    `jet_pfcs` must be the PFC slice belonging to one jet, obtained from the
    MOD HDF5 `pfcs_index` information. Source row order is preserved.
    """
    cm = _column_map(pfcs_cols)
    _require_columns(cm, ("pt", "y", "phi", "m", "vertex"), "pfcs")

    particles = np.asarray(jet_pfcs, dtype=np.float64)

    if particles.ndim != 2:
        raise ValueError(f"jet_pfcs must be rank 2, got {particles.shape}")

    # ---- RECONSTRUCTED FROM T4 PLAIN-ENGLISH SPEC (scrubber-blocked slice) ----
    # PFC selection: vertex == 0 AND pt >= 0.5 GeV. No JEC applied to PFCs.
    if len(particles):
        selected = (
            (particles[:, cm["vertex"]] == 0)
            & (particles[:, cm["pt"]] >= 0.5)
        )
        particles = particles[selected]
    # ---------------------------------------------------------------------------

    n = int(len(particles))

    result: dict[str, float | int] = {
        "n_pfc_selected": n,
    }

    if n == 0:
        result["pfc_pt_sum_GeV"] = 0.0
        result["pfc_mass_GeV"] = 0.0
        for _, label in BETAS:
            result[f"e2_beta_{label}"] = np.nan
            result[f"e3_beta_{label}"] = np.nan
            result[f"D2_beta_{label}"] = np.nan
        return result

    pt = particles[:, cm["pt"]]
    rapidity = particles[:, cm["y"]]
    phi = particles[:, cm["phi"]]
    mass = particles[:, cm["m"]]

    pt_sum = float(np.sum(pt, dtype=np.float64))
    result["pfc_pt_sum_GeV"] = pt_sum

    # Invariant mass of the selected-PFC four-vector sum.
    transverse_mass = np.sqrt(pt * pt + mass * mass)
    energy = float(
        np.sum(transverse_mass * np.cosh(rapidity), dtype=np.float64)
    )
    px = float(np.sum(pt * np.cos(phi), dtype=np.float64))
    py = float(np.sum(pt * np.sin(phi), dtype=np.float64))
    pz = float(
        np.sum(transverse_mass * np.sinh(rapidity), dtype=np.float64)
    )

    mass_squared = energy * energy - px * px - py * py - pz * pz
    roundoff_scale = energy * energy + px * px + py * py + pz * pz

    if (
        mass_squared < 0.0
        and abs(mass_squared) <= 1.0e-12 * max(roundoff_scale, 1.0)
    ):
        mass_squared = 0.0
    elif mass_squared < 0.0:
        raise FloatingPointError(
            f"Materially negative PFC invariant mass squared: {mass_squared}"
        )

    result["pfc_mass_GeV"] = float(np.sqrt(mass_squared))

    # Preserve the existing v0.1 boundary convention.
    if n < 2 or not np.isfinite(pt_sum) or pt_sum <= 0.0:
        for _, label in BETAS:
            result[f"e2_beta_{label}"] = np.nan
            result[f"e3_beta_{label}"] = np.nan
            result[f"D2_beta_{label}"] = np.nan
        return result

    z = pt / pt_sum

    delta_y = rapidity[:, None] - rapidity[None, :]
    delta_phi = (
        phi[:, None] - phi[None, :] + np.pi
    ) % (2.0 * np.pi) - np.pi
    delta_r = np.hypot(delta_y, delta_phi)

    zz = z[:, None] * z[None, :]
    sqrt_zz = np.sqrt(zz)
    upper = np.triu_indices(n, k=1)

    for beta, label in BETAS:
        theta = np.power(delta_r, beta)

        e2 = float(
            np.sum(zz[upper] * theta[upper], dtype=np.float64)
        )

        # M_ij = sqrt(z_i z_j) * DeltaR_ij^beta, with zero diagonal.
        matrix = sqrt_zz * theta
        np.fill_diagonal(matrix, 0.0)

        # One GEMM:
        # e3 = trace(M^3)/6 = sum[(M @ M) * M.T]/6.
        matrix_squared = matrix @ matrix
        e3 = float(
            np.sum(matrix_squared * matrix.T, dtype=np.float64) / 6.0
        )

        if e3 < -1.0e-12:
            raise FloatingPointError(
                f"Materially negative e3 for beta={beta}: {e3}"
            )
        e3 = max(e3, 0.0)

        if e2 > 0.0:
            d2 = float(e3 / (e2 ** 3))
        else:
            d2 = np.nan

        result[f"e2_beta_{label}"] = e2
        result[f"e3_beta_{label}"] = e3
        result[f"D2_beta_{label}"] = d2

    return result


def extract_feature_row(
    *,
    sample: str,
    source_subdataset: str,
    source_hdf5_path: str | Path,
    source_file_sha256: str,
    jet_row_id: int,
    jets_f_row: np.ndarray,
    jets_i_row: np.ndarray,
    jet_pfcs: np.ndarray,
    jets_f_cols: Sequence[Any],
    jets_i_cols: Sequence[Any],
    pfcs_cols: Sequence[Any],
) -> dict[str, Any]:
    """Build one row of the exact 33-column v0.1 feature table."""
    jf = _column_map(jets_f_cols)
    ji = _column_map(jets_i_cols)

    _require_columns(
        jf,
        (
            "jet_pt",
            "jet_y",
            "jet_phi",
            "jet_m",
            "jet_eta",
            "jec",
            "jet_area",
            "jet_max_nef",
            "weight",
        ),
        "jets_f",
    )
    _require_columns(
        ji,
        ("fn", "rn", "lbn", "evn", "npv", "quality"),
        "jets_i",
    )

    jet_pt = float(jets_f_row[jf["jet_pt"]])
    jec = float(jets_f_row[jf["jec"]])

    row: dict[str, Any] = {
        "sample": sample,
        "source_subdataset": source_subdataset,
        # This is the MOD HDF5 container, not the original CMS AOD filename.
        "source_filename": Path(source_hdf5_path).name,
        "source_file_sha256": source_file_sha256,
        # Zero-based row in this MOD HDF5 file.
        "jet_row_id": int(jet_row_id),

        "fn": int(jets_i_row[ji["fn"]]),
        "rn": int(jets_i_row[ji["rn"]]),
        "lbn": int(jets_i_row[ji["lbn"]]),
        "evn": int(jets_i_row[ji["evn"]]),

        "corr_jet_pt_GeV": jet_pt * jec,
        "jet_pt_GeV": jet_pt,
        "jet_eta": float(jets_f_row[jf["jet_eta"]]),
        "jet_y": float(jets_f_row[jf["jet_y"]]),
        "jet_phi": float(jets_f_row[jf["jet_phi"]]),
        "jet_m_GeV": float(jets_f_row[jf["jet_m"]]),
        "jec": jec,
        "jet_area": float(jets_f_row[jf["jet_area"]]),
        "jet_max_nef": float(jets_f_row[jf["jet_max_nef"]]),
        "npv": int(jets_i_row[ji["npv"]]),
        "quality": int(jets_i_row[ji["quality"]]),

        # Raw MOD cross-section contribution in nanobarns.
        # No EnergyFlow k-factor is applied here.
        "weight_nb": float(jets_f_row[jf["weight"]]),
    }

    row.update(compute_pfc_features(jet_pfcs, pfcs_cols))
    return row
