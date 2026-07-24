# T3 gamma-stratified held-out entropy reduction -- NUMBERS ONLY

Cat is the compute arm. **No verdict is offered here; the kill/survive call is T3's.**

Data: `brody_poisson_clicks_trials.parquet`, sha256 `86b51a3e5747fd44ce2e02fd4178faf2acea4e393a9b50b1d3ec7b9c9520bd99` (verified), Zenodo 13352119, CC-BY-4.0.


## 1. Tercile cut points (frozen BEFORE any horizon was computed)

- `|gamma|` 33.3 pct cut = **1.500000**
- `|gamma|` 66.7 pct cut = **2.500000**
- assignment: T_low: |g| <= cut1 ; T_mid: cut1 < |g| <= cut2 ; T_high: |g| > cut2
- tercile trial counts: [5973677, 3300938, 4104207] (fractions [0.4465, 0.2467, 0.3068])
- per-tercile |gamma| range: [[0.0, 1.5], [1.5333333015441895, 2.5], [2.5333333015441895, 10.0]]
- per-tercile |gamma| mean: [0.9715, 2.3416, 3.5505]
- distinct |gamma| values in the corpus: 222

## 2. Sample

- `n_rats_in_release`: 515
- `n_trials_in_release`: 25562353
- `n_trials_with_20_informative_clicks_and_valid_choice_gamma`: 13378865
- `n_trials_dropped_fewer_than_20_informative_clicks`: 12183488
- `n_trials_with_simultaneous_first_pair_removed`: 23381913
- `n_qualifying_rats_ge200_qualifying_trials`: 514
- `n_qualifying_trials_in_qualifying_rats`: 13378822
- `n_rats_with_ge200_trials_in_every_tercile`: 506
- `qualifying_trials_per_rat`: {'min': 1042, 'median': 16781.5, 'max': 166810}
- `per_tercile_trial_counts`: [5973677, 3300938, 4104207]
- `per_tercile_rats_used`: {'lowgamma': 514, 'midgamma': 506, 'highgamma': 514, 'allgamma': 514}
- `per_tercile_trials_used`: {'lowgamma': 5973677.0, 'midgamma': 3300938.0, 'highgamma': 4104207.0, 'allgamma': 13378822.0}
- `min_trials_per_rat_in_tercile`: {'lowgamma': 249.0, 'midgamma': 203.0, 'highgamma': 319.0, 'allgamma': 1042.0}

## 3. Horizons (pooled across rats, symmetric odd/even 2-fold)

| stratum | H_clicks | 95% CI (rat bootstrap) | E(1) bits | E(20) bits | E(1)-E(20) | argmin_n | anchor band |
|---|---|---|---|---|---|---|---|
| lowgamma | 4.9163 | [4.8224, 5.0091] | 0.954162 | 0.837351 | 0.116811 | 20 | below_anchor_band |
| midgamma | 1.5464 | [1.5257, 1.5676] | 0.723747 | 0.589070 | 0.134676 | 20 | below_anchor_band |
| highgamma | 1.2003 | [1.1863, 1.2131] | 0.574956 | 0.512050 | 0.062906 | 20 | below_anchor_band |
| allgamma | 2.7318 | [2.6914, 2.7717] | 0.828942 | 0.675549 | 0.153393 | 20 | below_anchor_band |

### Per-rat median horizons

| stratum | median H | 95% CI | IQR | SD across rats | rats with finite H |
|---|---|---|---|---|---|
| lowgamma | 4.9004 | [4.8373, 4.9768] | [4.3331, 5.4489] | 1.3668 | 508 (0.988) |
| midgamma | 1.5016 | [1.4822, 1.5181] | [1.3997, 1.6353] | 0.3959 | 502 (0.992) |
| highgamma | 1.1940 | [1.1821, 1.2097] | [1.0629, 1.2851] | 0.7156 | 510 (0.992) |
| allgamma | 2.7258 | [2.6793, 2.7576] | [2.4147, 2.9490] | 0.4657 | 512 (0.996) |

## 4. Ratio and ordering

- pooled maxH/minH = **4.0958**, minH/maxH = **0.2442**
- pooled ordering (descending H): **low > mid > high**
- monotonic DECREASING in |gamma| (H_low > H_mid > H_high): **True**
- monotonic INCREASING in |gamma|: **False**
- per-rat-median maxH/minH = 4.1042, ordering low > mid > high
- joint rat bootstrap on the 506 rats with >=200 trials in every tercile: maxH/minH = 4.1037 CI95 [4.0174, 4.1886]; fraction of bootstrap draws monotonically decreasing = 1.000

### Position relative to the thresholds T3 stated (facts, not a ruling)

- T3 raw-record expectation `maxH/minH <= 1.5`: observed pooled 4.0958
- T3 kill condition `maxH/minH > 3` AND monotonic decrease: observed ratio 4.0958, monotonic decrease True
- T3 anchor band `H_clicks in [6.04, 8.093]`: lowgamma=4.9163 (below_anchor_band); midgamma=1.5464 (below_anchor_band); highgamma=1.2003 (below_anchor_band); allgamma=2.7318 (below_anchor_band)

## 5. Controls

| control | stratum | H_pooled | E(1)-E(20) bits | rats with finite H |
|---|---|---|---|---|
| ctrl_choice_shuffle_s0 | allgamma | undefined | -0.001076 | 10 (0.019) |
| ctrl_choice_shuffle_s0 | lowgamma | undefined | -0.002346 | 5 (0.010) |
| ctrl_choice_shuffle_s0 | midgamma | undefined | -0.002888 | 15 (0.030) |
| ctrl_choice_shuffle_s0 | highgamma | undefined | -0.001500 | 42 (0.082) |
| ctrl_choice_shuffle_s1 | allgamma | undefined | -0.001042 | 7 (0.014) |
| ctrl_choice_shuffle_s1 | lowgamma | undefined | -0.002272 | 9 (0.018) |
| ctrl_choice_shuffle_s1 | midgamma | undefined | -0.002944 | 17 (0.034) |
| ctrl_choice_shuffle_s1 | highgamma | undefined | -0.001452 | 44 (0.086) |
| ctrl_choice_shuffle_s2 | allgamma | undefined | -0.001054 | 3 (0.006) |
| ctrl_choice_shuffle_s2 | lowgamma | undefined | -0.002285 | 7 (0.014) |
| ctrl_choice_shuffle_s2 | midgamma | undefined | -0.002951 | 21 (0.042) |
| ctrl_choice_shuffle_s2 | highgamma | undefined | -0.001531 | 35 (0.068) |
| ctrl_choice_shuffle_s3 | allgamma | undefined | -0.001065 | 5 (0.010) |
| ctrl_choice_shuffle_s3 | lowgamma | undefined | -0.002439 | 6 (0.012) |
| ctrl_choice_shuffle_s3 | midgamma | undefined | -0.002923 | 22 (0.043) |
| ctrl_choice_shuffle_s3 | highgamma | undefined | -0.001455 | 43 (0.084) |
| ctrl_choice_shuffle_s4 | allgamma | undefined | -0.001111 | 8 (0.016) |
| ctrl_choice_shuffle_s4 | lowgamma | undefined | -0.002444 | 5 (0.010) |
| ctrl_choice_shuffle_s4 | midgamma | undefined | -0.002872 | 17 (0.034) |
| ctrl_choice_shuffle_s4 | highgamma | undefined | -0.001499 | 41 (0.080) |
| ctrl_trial_mismatch | allgamma | undefined | -0.000154 | 131 (0.255) |
| ctrl_trial_mismatch | lowgamma | undefined | -0.000726 | 125 (0.243) |
| ctrl_trial_mismatch | midgamma | undefined | -0.002298 | 51 (0.101) |
| ctrl_trial_mismatch | highgamma | undefined | -0.001371 | 51 (0.099) |

- any control with a defined pooled horizon within a factor of three of the corresponding target: **False**

## 6. Method (as executed)

- Per-trial evidence: L click s=-1, R click s=+1; if |first_L - first_R| < 1e-7 s that simultaneous pair is removed; remaining clicks sorted by time (ties broken L before R, deterministic); first 20 informative clicks retained; D_n = sum_{k<=n} s_k for n=1..20.
- A trial qualifies if it has >=20 informative clicks after the stereo removal and has a valid `choice_R` and a finite `gamma`. Rats qualify at >=200 qualifying trials; >=30 qualifying rats required.
- Held-out curve: trials split by odd/even `trial_idx`; p(C=1|D_n=d) = (N_{d,1}+1/2)/(N_{d,.}+1) on the training half; E(n) = held-out conditional cross-entropy of the rat's choice given D_n, in bits.
- q(n) = (E(n)-E(20))/(E(1)-E(20)); H_clicks = n_{1/e} - 1 with n_{1/e} obtained by LINEAR interpolation in n on q at the FIRST n where q(n) <= 1/e.
- |gamma| terciles are GLOBAL over qualifying trials of qualifying rats, and the cut points were written to `tercile_cutpoints.json` before any horizon was computed.

### Cat judgement calls (T3 may overrule)

1. **"Qualifying trial" = >=20 informative clicks** (so every D_1..D_20 exists). T3's text names a qualifying trial without defining it; requiring the full 20-click prefix is the conservative reading. Trials dropped for this reason are counted above.
2. **Fold direction.** T3 says "training half"/"held-out half" without saying which parity is which. Primary numbers use the SYMMETRIC 2-fold (train even/test odd and train odd/test even, cross-entropies summed, every trial held out exactly once). Both single directions are reported separately.
3. **Per-rat inclusion inside a tercile** uses the same >=200-trial rule as the global cut. A no-cut variant (`H_allrats_in_cell`) and a common-rat variant (rats with >=200 trials in ALL three terciles) are both reported.
4. **Aggregation.** Each rat keeps its own p(C|D_n); the pooled E(n) is sum_rats CE_rat(n) / sum_rats N_rat. The per-rat median is reported alongside.
5. **Undefined horizons.** Where E(20) >= E(1) the T3 denominator is non-positive and no 1/e crossing exists; H is reported as undefined rather than forced. A supplementary variant anchored on min_n E(n) is given for information only.
6. **Entropy in bits.** q(n) and H are unit-invariant.
7. **Tercile tie rule.** `np.quantile` puts the 33.3/66.7 cuts exactly on the mass points |gamma| = 1.5 and 2.5. The primary numbers use inclusive upper bounds (|g| <= cut), which sends all of |gamma| = 1.5 to the low tercile and all of 2.5 to the mid tercile and makes the terciles unequal (44.7 / 24.7 / 30.7 % of trials). Section 8 reports the strict-`<` alternative and the value-by-value horizons so the choice can be inspected.

## 7. Does the >=20-informative-click trial cut depend on |gamma|?

Computed on ALL trials in the release (scalar columns only). The exact per-trial stereo removal is not available in this cheap pass, so both bounds are given.

| tercile | all trials | qualify rate (>=20 clicks) | qualify rate (>=22 clicks) | mean stim duration s |
|---|---|---|---|---|
| low | 11430172 | 0.5772 | 0.5177 | 0.5702 |
| mid | 6282903 | 0.5811 | 0.5207 | 0.5738 |
| high | 7849278 | 0.5793 | 0.5187 | 0.5727 |

## 8. |gamma| is discrete and BOTH cut points land on mass points

The 33.3 and 66.7 percentiles of |gamma| are exactly 1.5 and 2.5, and |gamma| = 0.5, 1.5, 2.5, 3.5 alone carry 9.52 M of the 13.38 M qualifying trials. Tercile membership of |gamma| = 1.5 and 2.5 is therefore decided by the tie rule. Both rules and the value-by-value resolution are reported.

**Alternative tie rule** (T_low: |g| < 1.5 ; T_mid: 1.5 <= |g| < 2.5 ; T_high: |g| >= 2.5), trial counts [3628879, 3320184, 6429759]:

| tercile | H_clicks | 95% CI | rats | trials |
|---|---|---|---|---|
| lowgamma | 6.9732 | [6.5854, 7.3999] | 514 | 3628879 |
| midgamma | 2.3844 | [2.3139, 2.4515] | 504 | 3320184 |
| highgamma | 1.3263 | [1.3165, 1.3353] | 514 | 6429759 |

- alt-tie maxH/minH = **5.2576**, monotonic decreasing = **True**

**Horizon at each dominant single |gamma| value** (no tie question at all):

| \|gamma\| | H_clicks | 95% CI | rats | trials |
|---|---|---|---|---|
| 0.5 | 8.8818 | [8.4832, 9.2348] | 449 | 2529230 |
| 1 | 4.4484 | [4.2645, 4.5936] | 163 | 851768 |
| 1.5 | 2.6310 | [2.5930, 2.6644] | 430 | 2343447 |
| 1.66667 | not computed (<30 rats with >=200 trials) | n/a | 17 | 96034 |
| 2 | 1.7552 | [1.7352, 1.7727] | 133 | 685982 |
| 2.5 | 1.4438 | [1.4322, 1.4550] | 434 | 2324332 |
| 3 | 1.2822 | [1.2550, 1.3071] | 136 | 638957 |
| 3.5 | 1.1616 | [1.1481, 1.1746] | 434 | 2321846 |
| 4 | 1.1121 | [1.0702, 1.1494] | 122 | 585216 |
| 5 | 1.0989 | [0.9957, 1.2200] | 39 | 171805 |
| other | 2.0025 | [1.8375, 2.2845] | 330 | 758898 |

### Provenance

- peak 1-min load average observed during the run: 7.93
- wall time: 304s pipeline (pass1 271s, pass2 26s) + 155s diagnostics; ~30 min data transfer
- BLAS thread pinning: OMP/OPENBLAS/MKL/VECLIB/NUMEXPR = 1; no multiprocessing.
- seed 20260724, 2000 rat-level bootstrap resamples, 5 choice-shuffle seeds.
