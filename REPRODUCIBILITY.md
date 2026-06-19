# Reproducibility Guide

This guide separates smoke verification, which runs from files included in the
repository, from full Bishan experiments, which require the external prepared
dataset described in `DATA_AVAILABILITY.md`.

## Environment

Tested locally with Python 3.13.7 on Windows. CPU execution is sufficient for
the smoke tests and short probes. CUDA or Colab Pro+ is recommended for longer
training sweeps.

Install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Smoke Verification Included in Git

For a reviewer-oriented command order, expected smoke outputs, and failure
interpretation, see:

```text
paper10_geojepa_mpc/experiments/results/e0_reviewer_smoke_replication_protocol_2026-06-09.md
```

For the latest tracked local execution log of that protocol, see:

```text
paper10_geojepa_mpc/experiments/results/e0_reviewer_smoke_verification_log_2026-06-10.md
```

Run all Paper10 tests:

```powershell
.\.venv\Scripts\python.exe -m pytest paper10_geojepa_mpc\tests -q -p no:cacheprovider
```

Run the smoke dataset header summary:

```powershell
.\.venv\Scripts\python.exe paper10_geojepa_mpc\experiments\run_e0_smoke.py
```

Run smoke-scale training:

```powershell
.\.venv\Scripts\python.exe paper10_geojepa_mpc\experiments\run_e0_train_smoke.py
```

Run the packaged value-label training smoke. This uses the included
`frontier_random050` value-label dataset and the included smoke transition file
only for transition sample-count metadata; the value-head-only path does not
train from transition MSE when `lambda_sig=0`.

```powershell
.\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_value_head_train --transition-path arcgis_toolbox_paper9\_scratch\tool1_smoke\prepared\tool2\transitions.npz --pairwise-path paper10_geojepa_mpc\experiments\results\e0_value_labels_frontier_random050_rank_seed2028_10x12_h5_seed43.npz --init-checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --checkpoint-path reviewer_outputs\value_head_smoke\value_head.pt --output reviewer_outputs\value_head_smoke\metrics.json --epochs 1 --batch-size 16 --transition-samples 500 --pairwise-states 10 --pairwise-subsample 10 --n-pairs 8 --candidate-top-k 4 --candidate-batch-states 1 --candidate-max-states 10 --checkpoint-metric auto --checkpoint-mode min --seed 3043 --device cpu
```

Run the submission preflight checks after editing manuscript, archive, or
availability files:

```powershell
.\.venv\Scripts\python.exe scripts/paper10/preflight_submission_checks.py
```

Generate draft integrated Dongxing Figure 4 and Figure 5 previews from tracked
CSV source data:

```powershell
.\.venv\Scripts\python.exe scripts/paper10/plot_integrated_dongxing_figures.py
```

Use the current generic figure/table numbering freeze before manuscript
conversion:

```text
paper10_geojepa_mpc/experiments/results/e0_integrated_figure_table_numbering_freeze_2026-06-11.md
```

Use the current no-go decision packet before creating a journal-specific
submission manuscript:

```text
paper10_geojepa_mpc/experiments/results/e0_submission_blocker_decision_packet_2026-06-11.md
```

Use the current with-Dongxing target-venue and manuscript-conversion checklist
before creating or formatting the final journal-specific manuscript:

```text
paper10_geojepa_mpc/experiments/results/e0_integrated_target_venue_and_manuscript_conversion_checklist_with_dongxing_2026-06-12.md
```

Use the current citation and statistical-reporting policy before final citation
formatting, table-caption editing, or inferential wording:

```text
paper10_geojepa_mpc/experiments/results/e0_integrated_citation_and_statistical_reporting_policy_2026-06-12.md
```

Use the current CEUS reviewer-improvement packet before converting Methods,
Discussion, Data Availability, or reviewer-response text:

```text
paper10_geojepa_mpc/experiments/results/e0_ceus_reviewer_improvement_packet_2026-06-12.md
```

Use the current CEUS Research Article candidate manuscript draft after checking
the blocker packet and CEUS reviewer-improvement packet:

```text
paper10_geojepa_mpc/experiments/results/e0_ceus_research_article_manuscript_draft_2026-06-12.md
```

Use the Stage 3 manuscript reframe before editing the CEUS draft title,
abstract, Results, Discussion, Conclusion, captions, or claim-evidence map:

```text
paper10_geojepa_mpc/experiments/results/e0_ceus_stage3_manuscript_reframe_2026-06-18.md
```

Use the current CEUS Stage 3 manuscript draft as the manuscript-facing output
after applying the Stage 3 claim boundary:

```text
paper10_geojepa_mpc/experiments/results/e0_ceus_stage3_manuscript_draft_2026-06-18.md
```

Use the current author-decision matrix before claiming the formal manuscript
package is ready:

```text
paper10_geojepa_mpc/experiments/results/e0_paper10_author_decision_matrix_2026-06-18.md
```

Use the current formal-manuscript assembly blueprint before replacing the Stage
3 draft with a journal-specific manuscript:

```text
paper10_geojepa_mpc/experiments/results/e0_paper10_formal_manuscript_assembly_blueprint_2026-06-18.md
```

Use the source-derived claim audit before editing Results, Discussion, or
Conclusion claim language:

```text
paper10_geojepa_mpc/experiments/results/e0_paper10_claim_source_consistency_audit_2026-06-18.md
```

Use the real-data availability audit before starting full-data reruns or
backfilling Data and Code Availability:

```text
paper10_geojepa_mpc/experiments/results/e0_paper10_real_data_availability_audit_2026-06-18.md
```

Use the real-data integrity smoke before long full-data experiments to confirm
metadata-level readability of the external NPZ, GeoPackage, directory, and JSON
inputs:

```text
paper10_geojepa_mpc/experiments/results/e0_paper10_real_data_integrity_smoke_2026-06-18.md
```

Use the five-step full-Bishan real-environment smoke after metadata checks when
you need to confirm the execution chain from a Paper10 checkpoint through the
Paper9 adapter, MPC selector, executable mask, and `CountyLevelEnv.step`. This
smoke is not a planning-quality result:

```text
paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_smoke_5step_h3_k20_seed0_2026-06-18.md
```

Use the five-step full-Bishan value-filter smoke to confirm that the 20x16/top5
checkpoint can run through the value-filter selector and full Bishan
`CountyLevelEnv.step`. This smoke records one negative reward step and is not
short-horizon performance evidence:

```text
paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_value_filter_smoke_5step_h5_k50_seed0_2026-06-19.md
```

Use the real-environment smoke boundary audit before interpreting the two
tracked full-Bishan smoke reports together. The audit records the different
checkpoint, selector, horizon, and top_k settings and keeps the two runs out of
short-horizon performance-comparison use:

```text
paper10_geojepa_mpc/experiments/results/e0_paper10_real_env_smoke_boundary_audit_2026-06-19.md
```

Use the anchor raw-rollout consistency audit before editing the Bishan
20x16/top5 anchor result. It recomputes the five seed rewards from tracked raw
step records and checks the packaged rollout summary and Stage 3 frozen-anchor
row without rerunning rollouts:

```text
paper10_geojepa_mpc/experiments/results/e0_paper10_anchor_raw_rollout_consistency_audit_2026-06-19.md
```

Use the manuscript result-table freeze before editing Results tables, captions,
or claim-evidence maps. It derives the Bishan anchor, Stage 3 boundary rows, and
claim-status table from tracked Stage 3, claim-source, and raw-rollout audit
JSON files without adding a new experimental claim:

```text
paper10_geojepa_mpc/experiments/results/e0_paper10_manuscript_result_tables_freeze_2026-06-19.md
```

- Original-vision validation design and registry:
  `docs/superpowers/specs/2026-06-17-paper10-original-vision-validation-design.md`
  and
  `paper10_geojepa_mpc/experiments/results/e0_original_vision_validation_registry_2026-06-17.md`.

## Full Bishan Dataset Setup

Place the full prepared data under the repository root:

```text
tool2/transitions.npz
tool2/pairwise.npz
dem_slope_analysis/output/DLTB_with_slope.shp
dem_slope_analysis/output/DLTB_with_slope.dbf
dem_slope_analysis/output/DLTB_with_slope.shx
dem_slope_analysis/output/DLTB_with_slope.prj
results_real/blocks/
townships.json
```

`DLTB_with_slope.gpkg` may be used instead of the shapefile set. The full
Tool2 files are intentionally not committed to Git because they are about
1.65 GB together.

## macOS Frontier-Random 50x24/h5 Continuation

This route is retained for reproducing or auditing the 50x24/h5 seed45
diagnostic. It is no longer the next training route: the macOS seed45 run
failed the default and post-hoc monitor gates, so do not continue it into
value-head training.

If Colab quota is unavailable and you need to reproduce that diagnostic, use
the macOS continuation package:

```text
docs/macos_frontier_random050_50x24_h5.md
scripts/macos/frontier_random050_50x24_h5.env.example
scripts/macos/run_frontier_random050_50x24_h5.sh
```

After `git pull`, create a Python virtual environment, copy the env template,
set `DATA_ROOT` to the full Bishan data root, and run:

```bash
bash scripts/macos/run_frontier_random050_50x24_h5.sh
```

The script executes the same `frontier_random050` 50x24/h5 sequence as the
Colab notebook, stores outputs under `RUN_ROOT`, and resumes by skipping any
step whose final artifact already exists. Treat any training step as valid only
when the monitor gate returns `continue`.

## Windows Frontier-Random 50-State Ablation

The Windows workstation has a CPU-only route for reproducing or editing the
Paper10 `frontier_random050` ablation grid:

```text
docs/windows_frontier_random050_ablation.md
scripts/windows/frontier_random050_ablation.env.example.ps1
scripts/windows/run_frontier_random050_ablation_grid.ps1
```

The runner uses `D:\test` as the full-data root by default, requires
`DLTB_with_slope.gpkg`, and runs label generation plus top-3/top-4/top-5 monitor
gates before any value-head training. Training remains disabled unless
`TrainOnPass = 1` is set in the local env file.

```powershell
Copy-Item scripts\windows\frontier_random050_ablation.env.example.ps1 scripts\windows\frontier_random050_ablation.env.ps1
powershell -ExecutionPolicy Bypass -File scripts\windows\run_frontier_random050_ablation_grid.ps1
```

Outputs are written under `D:\test\paper10_runs`, including
`frontier_random050_ablation_summary.md` and
`frontier_random050_ablation_summary.json`.

The packaged seed46 grid has already been run and all rows failed. For the
current continuation decision and a narrow seed-sensitivity override example,
see:

```text
docs/superpowers/notes/2026-06-09-paper10-50state-redesign-handoff.md
```

## Full Bishan Training Probe

```powershell
.\.venv\Scripts\python.exe paper10_geojepa_mpc\experiments\run_e0_train_bishan_probe.py --config rank --epochs 1 --batch-size 16 --transition-samples 6000 --pairwise-states 1000 --pairwise-subsample 16 --n-pairs 4 --device cpu
```

## Checkpoint Scoring

```powershell
.\.venv\Scripts\python.exe paper10_geojepa_mpc\experiments\run_e0_score_checkpoint.py --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --pairwise tool2\pairwise.npz --top-k 5 --batch-states 4 --max-states 1000 --device cpu --output reviewer_outputs\checkpoint_scoring.json
```

## Real-Environment Rollout

Short rollout:

```powershell
.\.venv\Scripts\python.exe paper10_geojepa_mpc\experiments\run_e0_env_rollout_smoke.py --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --prepared-dir . --rollout-steps 3 --horizon 3 --top-k 20 --seed 0 --device cpu --output reviewer_outputs\env_rollout_smoke_3step_h3_k20.json
```

Matched five-seed rollout:

```powershell
.\.venv\Scripts\python.exe paper10_geojepa_mpc\experiments\run_e0_env_rollout_smoke.py --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --prepared-dir . --rollout-steps 100 --horizon 5 --top-k 50 --seeds 0-4 --device cpu --mask-mode executable --output reviewer_outputs\env_rollout_5seed_h5_k50_executable_mask.json
```

## Packaged Frontier-Random Value-Head Pilot

The repository includes the 2026-06-08 `frontier_random050` pilot artifacts:

```text
paper10_geojepa_mpc/experiments/results/e0_frontier_random050_10x12_h5_seed43_pilot_report_2026-06-08.md
paper10_geojepa_mpc/experiments/results/e0_frontier_random050_value_head_10x12_h5_seed43_top4_rollout_summary.json
paper10_geojepa_mpc/experiments/checkpoints/e0_frontier_random050_value_head_10x12_h5_seed43_top4/value_head_seed3043.pt
```

Re-run the included value-head training step from the packaged label dataset:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_value_head_train --transition-path tool2\transitions.npz --pairwise-path paper10_geojepa_mpc\experiments\results\e0_value_labels_frontier_random050_rank_seed2028_10x12_h5_seed43.npz --init-checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --checkpoint-path reviewer_outputs\frontier_random050_value_head_top4\value_head.pt --output reviewer_outputs\frontier_random050_value_head_top4\metrics.json --epochs 3 --batch-size 16 --transition-samples 6000 --pairwise-states 10 --pairwise-subsample 10 --n-pairs 8 --candidate-top-k 4 --candidate-batch-states 1 --candidate-max-states 10 --checkpoint-metric auto --checkpoint-mode min --seed 3043 --device cpu
```

Expected key fields are `transition_loss_enabled=false`,
`ranking_acc` near `0.8143`, and `candidate_top4_regret` near `0.1109`.

Re-running the recorded 100-step rollout requires the full Bishan data:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_frontier_random050_value_head_10x12_h5_seed43_top4\value_head_seed3043.pt --prepared-dir . --rollout-steps 100 --horizon 5 --top-k 50 --seeds 0-4 --device cpu --mask-mode executable --selector value_filter --candidate-score-mode blend --candidate-value-weight 0.1 --output reviewer_outputs\frontier_random050_value_head_top4_5seed_rollout.json
```

The packaged five-seed summary reports mean total reward `65.2566` and sample
standard deviation `5.0037`.

## Packaged Frontier-Random Value-Head Scale-Up

The repository also includes the 2026-06-08 20x16/h5 scale-up artifacts:

```text
paper10_geojepa_mpc/experiments/results/e0_frontier_random050_20x16_h5_seed44_top5_report_2026-06-08.md
paper10_geojepa_mpc/experiments/results/e0_frontier_random050_value_head_20x16_h5_seed44_top5_rollout_summary.json
paper10_geojepa_mpc/experiments/results/e0_value_labels_frontier_random050_rank_seed2028_20x16_h5_seed44.npz
paper10_geojepa_mpc/experiments/checkpoints/e0_frontier_random050_value_head_20x16_h5_seed44_top5/value_head_seed3044.pt
```

Re-run value-label generation with the full Bishan data:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.value_label_generation --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --n-states 20 --candidate-actions 16 --label-horizon 5 --gamma 0.99 --seed 44 --mask-mode executable --candidate-mode frontier_random --frontier-fraction 0.5 --advance-policy random --continuation-policy random --progress-every 1 --partial-output reviewer_outputs\e0_value_labels_frontier_random050_rank_seed2028_20x16_h5_seed44.partial.npz --output reviewer_outputs\e0_value_labels_frontier_random050_rank_seed2028_20x16_h5_seed44.npz
```

Re-run the top-k monitor. In the packaged result, top-5 is the selected gate:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.value_label_monitor --input paper10_geojepa_mpc\experiments\results\e0_value_labels_frontier_random050_rank_seed2028_20x16_h5_seed44.npz --top-k 5 --output-json reviewer_outputs\e0_value_label_monitor_frontier_random050_20x16_h5_seed44_top5.json --output-md reviewer_outputs\e0_value_label_monitor_frontier_random050_20x16_h5_seed44_top5.md
```

Expected monitor fields are `decision=continue`,
`candidate_topk_regret` near `0.1877`, and `candidate_topk_overlap` near
`0.6300`.

Re-run the packaged value-head training step:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_value_head_train --transition-path tool2\transitions.npz --pairwise-path paper10_geojepa_mpc\experiments\results\e0_value_labels_frontier_random050_rank_seed2028_20x16_h5_seed44.npz --init-checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_bishan_rank_seed2028\rank_seed2028.pt --checkpoint-path reviewer_outputs\frontier_random050_value_head_20x16_top5\value_head.pt --output reviewer_outputs\frontier_random050_value_head_20x16_top5\metrics.json --epochs 3 --batch-size 16 --transition-samples 6000 --pairwise-states 20 --pairwise-subsample 16 --n-pairs 8 --candidate-top-k 5 --candidate-batch-states 1 --candidate-max-states 20 --checkpoint-metric auto --checkpoint-mode min --seed 3044 --device cpu
```

Expected key fields are `transition_loss_enabled=false`,
`candidate_top5_hit_rate` near `0.9000`, and `candidate_top5_regret` near
`0.1877`.

Re-run the recorded 100-step rollout with full Bishan data:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_frontier_random050_value_head_20x16_h5_seed44_top5\value_head_seed3044.pt --prepared-dir . --rollout-steps 100 --horizon 5 --top-k 50 --seeds 0-4 --device cpu --mask-mode executable --selector value_filter --candidate-score-mode blend --candidate-value-weight 0.1 --output reviewer_outputs\frontier_random050_value_head_20x16_top5_5seed_rollout.json
```

The packaged five-seed summary reports mean total reward `69.4705`, sample
standard deviation `1.0004`, and a `6.46%` mean-reward improvement over the
10x12/top4 pilot.

## Expected Packaged Evidence

The repository already includes the recorded Paper10 result artifacts under
`paper10_geojepa_mpc/experiments/results/` and checkpoints under
`paper10_geojepa_mpc/experiments/checkpoints/`. Re-running the full commands
with the same data should reproduce the reported result structure and metrics,
subject to normal CPU/GPU floating-point and library-version variation.

The reviewer smoke protocol verifies the packaged clone and smoke data only.
It should not be used as evidence for full Bishan reruns or for a passing
50-state result.

The 2026-06-10 smoke verification log records the current Windows execution of
the protocol at commit `534e0f8115a55d5c080bf21bb888657ccd9dd585`.
