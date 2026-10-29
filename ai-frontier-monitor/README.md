# U.S.–China AI Frontier Monitor

A reproducible, source-linked interpretation of **Tim Fist, Georgia Adamson, and Konstantin Pilz**, [*How to Increase America's AI Lead Over China*](https://ifp.org/how-to-increase-americas-ai-lead-over-china/), Institute for Progress, published **October 19, 2026**.

**Status of public deployment:** GitHub Pages must be enabled in **Settings → Pages → Build and deployment → Source: GitHub Actions**. The first workflow successfully tested and refreshed Epoch data but correctly skipped the Pages deployment while Pages was disabled. Once enabled, manually rerun [the workflow](https://github.com/914ash/914ash/actions/workflows/ai-frontier-monitor.yml), or wait for the next daily run. The expected URL *after an actual successful deployment* is https://914ash.github.io/914ash/ . Do **not** assume that URL is active before seeing a successful Pages deployment.

## Components and why they should not be combined

| Indicator | Meaning | Source / refresh | Status |
|---|---|---|---|
| Observed capabilities lag (months) | Horizontal difference between fitted U.S. and Chinese ECI frontier trendlines at last China ECI record | [Epoch ECI model scores](https://epoch.ai/data/eci_scores.csv); scheduled daily | **Source-derived and reproducible** |
| National frontier slopes / R² | Months-to-ECI translation of record-setting releases since January 2024 | Same Epoch CSV, daily | **Source-derived** |
| 16× training-compute ratio | Physical training compute ratio for top five labs in U.S. vs China | Pilz 2026 forthcoming, cited in IFP | **Unpublished estimate, NOT live** |
| S = 50% distillation recovery | Fraction of the compute-related capability gap recovered through distillation | Anthropic executive estimate and a DeepSeek controlled experiment | **Very uncertain, NOT live** |
| Domestic/legal/smuggled/remote compute | Year-end 2026 estimated and 2027 projected chip access in H100 equivalents | IFP Appendices 3–7; range and private sources | **Projections, NOT live** |
| Scenario policy sliders | Counterfactual lead given reductions to chip pathways and to data available for distillation | Mathematical adaptation of Appendix 2 | **Hypothetical, NOT a forecast** |

## Observed ECI lag — precise transformation

1. Download all model rows, not the limited top-ten leaderboard.
2. Include models with **U.S.-headquartered or China-headquartered developers**, irrespective of open-weight status. Region assigned by Epoch’s `Country (of organization)` field. The country is *headquarters*, not training location, nationalized ownership, user population, or an intelligence classification.
3. Limit model release dates to **January 1, 2024 onward** and no later than the retrieval date. Validate dates, nonnegative bounded ECI scores, and source schema. Group by release date and developer country.
4. On each date, choose its highest ECI. Keep that date only when it sets a strictly higher score than all preceding dates for the same country (the **record/Pareto frontier**).
5. For each country separately, apply **ordinary least squares with equal observation weights, one per frontier-defining date**: `ECI = intercept + slope × months_since_2024-01-01`. Months are days / (365.25/12); no country weighting or benchmark weights are imposed here.
6. Let `E = latest Chinese record ECI`. **Lag** `= (E − intercept_CN)/slope_CN − (E − intercept_US)/slope_US` in months. This matches the IFP Appendix 1 approach; the minor difference in month representation and newly published/revised rows can shift the estimate.
7. Record the source retrieval UTC timestamp and raw CSV SHA-256; track the last change of CSV *content* separately. Failed source checks do not overwrite the previously good snapshot; front-end warns after 48h, then overdue after 96h. Unchanged CSV for 14+ days is highlighted for review and is *not* proof of stale scores.

IFP’s original October fit had **20 U.S.** and **17 Chinese** frontier records, slopes **1.31** and **1.18** ECI points/month, and horizontal lead **6.5 months**. The updated October 29 dataset used by this monitor had **22 U.S.** / **16 Chinese** defining dates, slopes roughly **1.35 / 1.17**, and **7.19 months**. The difference can arise entirely from updated model scores and model definitions; it is NOT necessarily a real change in the geopolitical lead during those ten days.

### What “weights” means here

* **IFP country regression:** equal weights for each national record-setting release date, as reconstructed; neither number of active labs nor market share is used to weight model frontier observations.
* **Epoch general ECI:** a *different, fitted statistical weighting*: scores are inferred across multiple benchmarks using model capability, benchmark difficulty, and discriminative slope; the benchmark mix and resulting fitted scores may change. The data are supplied by [Epoch's ECI](https://epoch.ai/eci) (39 benchmarks at the current site snapshot). Model-level 90% ECI confidence intervals are **not** the confidence interval for the horizontal U.S.–China lag. Fetch future versions of [model-by-benchmark scores and difficulty/slopes](https://epoch.ai/eci) to audit methodological drift. One should not pretend IFP “set” 39 fixed benchmark weights.
* **Compute-channel weights** in the structural model are sums of *H100-equivalent estimates*. Physical FP8 dense throughput conversion weights vary by GPU model. Other bottlenecks (GDDR/HBM bandwidth, interconnect, memory capacity, system utilization and network topology) mean these weights do **not** translate directly into frontier-training throughput.

### Why not make METR a second current score?

The IFP cross-check produces **6.6 months** with 50% METR task horizons, 14 U.S. frontier records vs six Chinese, log-linear doubling around 3.3 vs 3.7 months. The original METR dataset stopped being updated September 2026 and some next-generation methodologies are not commensurate. Keep it as an archived cross-check unless a separately justified new comparable panel is built.

## Structural compute / distillation model (Appendix 2)

```text
L = (1 - S) * K * log10(R)
L = U.S. lead in months
R = U.S. / Chinese physical compute used in frontier training, assumed 16x
S = share of the compute-generated gap recaptured by distillation, assumed 0.50
K = 13 / log10(16) = ~10.8 months per 10x training compute without distillation
=> Baseline = 6.5 months
```

The paper reasons S≈0.5 from (a) an Anthropic executive estimating 6–9 months with distillation vs 12–18 without, and (b) a DeepSeek-R1 distillation/student reinforcement-learning experiment in which ~3.35 of 6.55 ECI-equivalent gap points were recovered (S≈0.51). Neither proves a general causal constant. The 16× estimate is from a **forthcoming** Pilz study of total compute across top-five labs, treated as training compute after a further assumption. No underlying audited lab-by-lab panel is published in the paper.

IFP sanity-checks K against approximately **15.7 ECI points/year** progress and **14.1 ECI points per 10x compute**, of which **~9.2** are attributed to pretraining and **~4.9** to RL and other techniques. Do not interpret this as a measured model-by-model causal decomposition.

Distillation-data reduction: the fraction S changes to

`S' = max(0, S * [1 - 0.25 * log10(1/(1-c))])`

where `0<=c<1` is the fraction of harvestable data blocked. At 90% blocked this changes S to 37.5%; a 99% block changes S to 25%. The paper argues 90–99% reduction in harvested data might be feasible from safeguards, an uncertain transfer of results to all providers and attack strategies.

### Structural limitations explicitly stated in Appendix 2

1. **Equal algorithmic efficiency**: the same physical compute buys the same capability in each country.
2. **Constant distillation share**: the recovered *fraction* of the compute-generated lead is unchanged across capability levels, labs and time.
3. **Immediate access**: Chinese developers can distill a newly released U.S. model immediately.
4. **Comparable training mix**: U.S. and Chinese developers devote roughly equal portions of R&D compute to pretraining, reinforcement learning and post-training.
5. **Country-to-frontier proportionality**: a change in national chip stock translates proportionally to top labs' training-usable compute, with otherwise unchanged deployment and concentration.

These simplifying hypotheses fail when access, software efficiency, specialized training hardware, cloud account usage, confidential model weights, or frontier-lab concentration diverge.

## Compute channels, baselines and uncertainty

All values below in **millions of H100-equivalent FP8 units**; cumulative year-end access projections are not delivered or actively used training compute. Central IFP values:

| Source channel | 2026 | 2027 | Evidence limitations |
|---|---:|---:|---|
| Domestic production | 1.729 | 3.029 | Existing 2025 743K + 2026 ~986K new + 2027 ~1.3M new; constrained by HBM or DUV-i |
| Legal U.S.-chip imports | .846 | 1.346 | NVIDIA shipments and licensing, unknown RTX demand, conversion to H100e |
| Smuggled U.S. chip imports | 1.004 | 1.572 | Hidden flows, customs mismatch proxies, country-specific routes |
| Overseas remotely accessible compute | 1.054277 | 2.834351 | Unpublished SemiAnalysis leases, unverified clusters and power-to-GPU ratios |
| **Sum** | **4.633** | **8.781** | Approximate physical access, NOT effective frontier training |

Reported approximate uncertainty bounds: domestic end-2027 2.3–4.2M, legal end-2027 .986–2.04M, overseas end-2027 10th–90th percentile **1.967–3.905M**. Caution: not all bounds have the same statistical interpretation, are correlated, or can be added as if independent. Smuggling uncertainty and effective training-FLOP ratios are substantially less well identified.

### Appendix-by-appendix audit

* **Appendix 3, ASML DUV-immersion sales:** ASML DUV revenues and China mix, non-immersion “floor” and assumption that China takes less than half of global immersion-system sales “ceiling,” central ~62 systems sold to China in 2026 out of ~130 sold globally; installed 2026 capacity central ~324. Check quarterly ASML disclosures and accounting effects. This is a surrogate for fabrication capacity, not delivered accelerator counts.
* **Appendix 4, domestic:** production capacity from CTS DUV scenarios (2026 trend ~1M vs “AI push” ~4M; 2027 trend ~2M vs “AI push” ~11M H100e) and practical HBM bottleneck using domestic CXMT/XMC, imported stockpiles, smuggled foreign HBM and alternate memory. **Take the minimum** of lithography and HBM constraints, not the sum. Chinese 2026 new production central ~986K (662K–1.4M), 2027 ~1.3M (840K–2.1M). Existing 2025 stock ~743K. The modeled HBM measure could lower new domestic 2027 production by 9%.
* **Appendix 5, legal imports:** from Epoch owners and NVIDIA/AMD manufacturer data, baseline stock through 2025 ~402K H100e; 2026 incremental estimate H200 licensed 100K plus export-compliant RTX consumer/workstation ~344K; 2027 incremental H200 ~200K and RTX Pro ~300K, producing year-end total ~1.35M. Converter weights include A100/A800 .315 H100e, H800 1, H20 .15, MI308X .33; some workstation cards ~.3 H100e. FP8/GDDR/low interconnect may overstate training utility.
* **Appendix 6, smuggling:** identify atypical server trade flows via customs reports: imports >$100M, post-Oct-2023 value & price per server up at least 3×, mirrored import/export counts but Chinese declared value/server at least 2× exporter declaration. Malaysia and Singapore met heuristics; H1 2025 to H1 2026 values declined 80.7% and 83.1%, average 81.9%. **Warning:** abnormal trade-value proxies do not prove all shipments were illegal and are not direct chip counts; enforcement costs and rerouting matter.
* **Appendix 7, overseas remote access:** sum customer-attributed clusters sized by MW, count and chip power with SemiAnalysis overseas hyperscaler leasing estimates after avoiding overlaps. Central 2026 ~1.054M H100e (P10 .681–P90 1.455), 2027 ~2.834M (P10 1.967–P90 3.905). Method includes assumptions on lease timing, AI share, off-balance-sheet hardware, chip architecture mix (Hopper/Blackwell/Rubin), non-GPU infrastructure power and operational date. Much of source data and Monte Carlo detail are private or not directly auditable. Also evaluate memory-bandwidth-based equivalents (2026 ~1.049M, 2027 ~2.457M).

## What the interactive 2027 scenario does—and does not do

Each stock channel's **incremental 2027 stock** is reduced by the selected percentage and 2026 carryover is preserved. Remote overseas stock reduction applies to projected total remote capacity (including 2026 capacity). An adjusted China/U.S. ratio is calculated by holding U.S. effective compute unchanged and scaling the paper's 16× ratio inversely by `China_original_2027_stock / China_adjusted_2027_stock`. The distillation elasticity above changes S, and the resulting L is displayed.

This mimics the IFP *directional* high-level logic but **does not numerically reproduce IFP's original interactive policy package**, for which key 2027 no-policy country training-compute paths, dynamic concentration allocations and unpublished third-party sources are not all available. It is a transparent, deliberately conditional **sensitivity analysis**. The IFP headline “+6.6 months of added lead by 2027” is an unverified policy-case projection, not a new observed lead.

## Source freshness matrix & governance

| Data family | Primary public source | Auto or manual | Frequency | Interpretation |
|---|---|---|---|---|
| ECI model scores | [Epoch official downloadable CSV](https://epoch.ai/data/eci_scores.csv) | Automated | Daily | Recalculate measured frontier and hashes |
| ECI component weights & scores | [Epoch model/benchmark data and fitted difficulty-slopes](https://epoch.ai/eci) | Manual review | Monthly / change event | Score-series revision is measurement change, not new model progress |
| Chip sales, ownership & destination | [Epoch data library](https://epoch.ai/data) | Manual review | Monthly | Normalize units and destination; don't equate sales to stock |
| Legal controls and enforcement | [BIS Federal Register](https://www.federalregister.gov/agencies/bureau-of-industry-and-security) | Manual review | Rules and notices | Distinguish proposed vs effective controls and enforcement |
| NVIDIA shipments and export exposure | [NVIDIA filings](https://investor.nvidia.com/financial-info/sec-filings/default.aspx) | Manual review | Quarterly | Revenue not H100-equivalent chip count |
| Semiconductor equipment | [ASML investors](https://www.asml.com/en/investors) | Manual review | Quarterly | Revenue and machine units are different |
| Advanced logic/HBM and packaging | [TSMC investors](https://investor.tsmc.com/english), SK hynix, Micron | Manual review | Quarterly | Physical fab capacity ≠ finished eligible chips |
| Overseas Chinese leases | [SemiAnalysis](https://newsletter.semianalysis.com/) and disclosed contracts | Manual review, partial/private | Quarterly | Requires actual operational capacity plus customer identity |
| Distillation attacks/mitigations | Provider safety/security and NIST/CAISSI reports, peer-reviewed experiments | Manual review | Material new incident | Re-evaluate S, prompt-delivery dynamics and mitigation adaptation |
| METR original time horizon | [METR](https://metr.org/time-horizons/) | Archived cross-check | None for original series | Last original series updated September 2026, cannot serve as a live replacement |

A successful retrieval and a changed source are separate metadata fields. A changed input definition, calibration, objective, export rule, or supply-chain regime should cause a **versioned model revision** and an analyst check—not silently flow into an unqualified point estimate.

## Implications and methodological red-team

* The **headline 7.2-month lag** is a derived horizontal regression displacement, not a calendar prediction that any country will reach a particular system's capability at an exact future time. It depends on both slope and frontier-score revisions.
* Forecasting causality from frontier ECI change is invalid without separately observed changes in training compute and distillation; security outcomes, domestic economic spillovers, bargaining power and autonomous R&D rates are downstream hypotheses not measured by this dashboard.
* ECI benchmark coverage, contamination/gaming, selective API access, proprietary evaluations, slow model-score publication, and developer-headquarters assignment can distort the estimate.
* A reduction in available Chinese chips may be offset by higher utilization, improved efficiency, remote leasing, network architectures, alternative chips, model theft, cross-border relabeling, and shifts in training vs inference usage.
* Policies have possible costs and risks to U.S./allied supply chains, chip vendors, cloud and research openness. IFP argues supply is constrained enough to redirect rather than lose sales; that is a testable market hypothesis, not a guarantee.
* Operational intelligence analysis should carry additional **domain-specific** measures (cyber tasks, biological threats, long-horizon agent reliability, evaluations under secure conditions) rather than assume ECI captures all national-security relevant capability.

## Reproduce and deploy

Python standard library only; no API key.

```bash
python -m unittest discover -s ai-frontier-monitor/tests -v
python ai-frontier-monitor/scripts/refresh.py
cd ai-frontier-monitor
python -m http.server 8000
```

The workflow in `.github/workflows/ai-frontier-monitor.yml` executes daily at **12:17 UTC** and on selected pushes or manual dispatch, validates, fails closed on insufficient/bad source rows, preserves raw SHA-256 and audit parameters, commits the new JSON and then deploys **only if GitHub Pages is enabled**. Configure Pages to use **GitHub Actions** once in the repository Settings.

## Credit

The original research and all paper-based central estimates are the **Institute for Progress** research team's, not this dashboard's independent findings. Epoch ECI data are by **Epoch AI**, distributed under **CC BY 4.0**. This dashboard does not represent endorsement by IFP, Epoch, OpenAI, or the U.S. government.
