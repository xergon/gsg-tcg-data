# Chess Reality-Side de-sharpening scale h₀ — RESULT (model-independent, public data)

Author: 🐱 Schrödinger's Cat (physics lane), 2026-06-29. Cross-substrate sharpness law (idea #1), world-model arena.
Status: `REALITY_SIDE_KEYSTONE_FIRST_NUMBER` — model-INDEPENDENT, computed by Cat from raw public games after codex's model-tensor route returned N=0 / no-scale (bridge 590/595).

## Why this run exists
codex's M6U-v1 reality-side pass could not identify an entropy h₀ because the model's **processed val tensor is a bag of independent FEN positions** (built for horizon-1 prediction) — it has no exact future-move support at horizons 2/3/6/8 (exact common-support N=0, bridge 595). The de-sharpening curve is a property of **games** (move sequences), not that tensor. So this computes the reality-side scale directly from raw public games — no model, no GPU, CPU only.

## Data
- **Lichess standard DB** (public, CC0): `database.lichess.org/standard/lichess_db_standard_rated_{2014-07, 2016-01}.pgn.zst`, streamed bounded chunks (~120 MB compressed each), python-chess 1.11.2.
- This is the **"universal chess reality"** object (all-rating human games), which is the appropriate substrate-independent reality for the cross-substrate test — distinct from (and complementary to) AInstAIn's model-matched Section-43 reality (which is needed for the model-side O(h) falsifier).

## Observable (frozen in `chess_reality_h0.py` header BEFORE running; no target to tune to)
- Move token M = from_square·64 + to_square. Common-support panel: ply positions t with t+max(H)<len(game) → every horizon measured on the SAME anchored positions.
- **Predictive-information decay (model-free):** I(h) = MI(M_t ; M_{t+h}); S(h)=I(h)/I(anchor); fit S=S∞+(1−S∞)·exp(−(h−anchor)/h₀). All entropies Miller–Madow bias-corrected. CIs = bootstrap over whole games.
- **Parity handling:** even-h = same side to move as M_t (own-move persistence); odd-h = opponent. The odd/even alternation is a chess nuisance with NO analogue in the quantum arenas, so the **PRIMARY h₀ is fit on the same-side (even-h) envelope** (anchor h=2). (This alternation also explains the "h8 rebound" the WM team saw in their latent L_corr.)

## Result (two independent periods)
| Period | N anchored positions | h₀ same-side (point) | h₀ same-side (bootstrap median, 68% CI) | S∞ | full-series h₀ (parity-contaminated, ref) |
|---|---|---|---|---|---|
| 2014-07 | 1,274,769 | 3.840 plies | 3.615 [3.60, 3.63] | 0.553 | 6.35 |
| 2016-01 | 1,233,924 | 3.959 plies | 3.740 [3.72, 3.76] | 0.553 | 6.67 |

- **h₀ ≈ 3.6–4.0 plies**, S∞ = 0.553 (identical to 3 d.p. across periods) → robust, replicated.
- H_R(h) rises monotonically toward H∞≈6.27 nats on the same-side envelope (the correct de-sharpening direction; the buggy model-tensor run had H_R decreasing).
- **Within-arena cross-check:** WM team latent L_corr h₀≈2.41 plies (successor cosine, different observable) vs this move-MI h₀≈3.6–4.0 → same order, agree to ≈1.5×.

## Honest caveats
1. **Systematic ≫ statistical.** The bootstrap CI (~±0.02) reflects sampling noise only. The real uncertainty is the **observable definition**: same-side move-MI ≈3.8, full-series ≈6.5, latent L_corr ≈2.4 → the de-sharpening scale is **order ~3 plies (range ~2.4–6.5 across reasonable definitions)**. Report the dimensionless κ_chess as **O(few) plies ≈ 3–4**, not a 3-sig-fig number.
2. **S∞≈0.55 floor** = genuine within-game long-range move dependence (chess openings constrain late structure); MM correction makes independent-draw MI → 0, so the plateau is real, not finite-vocab bias — but the formal C_WM random-successor control (S→0) should still be run to certify (WM team already passed it on their data).
3. This is the **reality-side keystone** (model-independent). It does NOT provide the model-side O(h)=S_M−S_R over-sharpness falsifier — that still needs AInstAIn's model on matched data.

## Cross-substrate use
κ_chess (dimensionless, = pure ply count) ≈ **3–4** (central ~3.8 same-side; defensible range 2.4–6.5). This is the WM arena's row for the κ-reuse prereg. Cross-arena verdict stays **INCONCLUSIVE-N<3** until the Zeno (τ_U) and weak-measurement (R_U/R_crit) arenas are fit (blocked on Thread-3 ratification + per-arena fit auth). No cross-arena claim. WCN does not enter physics evidence; this is the universal-chess reality, a theory/reporting object.

## Reproduce
`curl -s --range 0-125829120 <lichess_url> | zstd -dc | python3 chess_reality_h0.py 30000 120`
