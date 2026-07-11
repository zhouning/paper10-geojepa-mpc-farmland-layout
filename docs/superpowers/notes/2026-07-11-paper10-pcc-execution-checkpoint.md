# Paper10 PCC Execution Checkpoint — 2026-07-11

## Repository state

- Branch: `main`
- Last implementation commit before this checkpoint: `a9f4c95 feat: execute two-round pcc policy iteration`
- Remote: `origin` (`https://github.com/zhouning/paper10-geojepa-mpc-farmland-layout.git`)
- Governing plan: `docs/superpowers/plans/2026-07-10-paper10-pcc-geojepa-mpc-substantive-revision.md`
- Protocol: `paper10_geojepa_mpc/experiments/protocols/pcc_v1.json`
- Protocol status at checkpoint: `development`

The untracked `%SystemDrive%/` directory and `2503.05774v1.pdf` are deliberately
excluded from Git, as required by the governing plan.

## Validation completed

The label-job, PCC-training, and policy-iteration runner tests passed together:

```powershell
D:\adk\.venv\Scripts\python.exe -m pytest `
  paper10_geojepa_mpc\tests\test_pcc_label_jobs.py `
  paper10_geojepa_mpc\tests\test_pcc_training.py `
  paper10_geojepa_mpc\tests\test_pcc_policy_iteration.py -q
```

Observed result: `22 passed`.

## Task 13 execution state

### Round-0 Bishan training labels

- Status: complete
- Seeds: `1000-1007` (8/8)
- Root manifest:
  `paper10_runs/pcc_v1/labels/bishan_train/manifest.json`
- Each seed has a valid manifest and trajectory NPZ artifact.

### Round-0 Bishan calibration labels

Final state verified at `2026-07-11T14:38:03+08:00`:

- Status: complete
- Completed at: `2026-07-11T13:46:16+08:00`
- Seeds: `2000-2019` (20/20)
- Artifact count: 20
- Root manifest:
  `paper10_runs/pcc_v1/labels/bishan_calibration/manifest.json`
- Manifest digest:
  `18f04a375bc59598047342bc59e27c05f29aaac96bc92d2583407e51f14d647b`
- Continuation policy: locked `paper9_mpc`
- Launcher stderr size: 0 bytes

The preceding in-progress checkpoint, sampled at
`2026-07-11T12:50:59+08:00`, recorded:

- Completed: seeds `2000-2011` (12/20; 60%)
- Running: seeds `2012-2015`
- Queued: seeds `2016-2019`
- Launcher PID at checkpoint: `21452`
- Worker count: 4
- Output root:
  `paper10_runs/pcc_v1/labels/bishan_calibration/`

The completed launcher command was:

```powershell
D:\adk\.venv\Scripts\python.exe -m paper10_geojepa_mpc.experiments.run_pcc_label_jobs `
  --registry paper10_geojepa_mpc\experiments\protocols\pcc_v1.json `
  --partition calibration `
  --seeds 2000-2019 `
  --max-workers 4 `
  --env-source paper9 `
  --prepared-dir D:\test `
  --reference-horizon 5 `
  --reference-top-k 50 `
  --device cpu `
  --resume `
  --output-root paper10_runs\pcc_v1\labels\bishan_calibration
```

The launcher and all child workers exited after writing the merged manifest.
Seed `job.log` files were written after each subprocess finished. If later
integrity checks reject the merged manifest, rerun the same command with
`--resume`; completed seed manifests and NPZ hashes are checked before any seed
is scheduled.

## Resume checks

After the current launcher exits, verify that all 20 seeds and the merged root
manifest exist:

```powershell
$root = 'paper10_runs\pcc_v1\labels\bishan_calibration'
Get-ChildItem $root -Directory -Filter 'seed_*' |
  Where-Object { Test-Path (Join-Path $_.FullName 'manifest.json') } |
  Sort-Object Name
Get-Content -Raw "$root\manifest.json"
```

The merged manifest must declare partition `calibration`, seeds `2000-2019`, and
the locked `paper9_mpc` continuation policy.

## Next execution steps

As of `2026-07-11T14:38:03+08:00`, no ensemble-training or policy-iteration
process is active, and `paper10_runs/pcc_v1/checkpoints/` has not yet been
created.

1. Train all declared Bishan ensemble combinations for model seeds
   `5101,5102,5103` and ensemble sizes `3,5` using the completed training-label
   manifest. Expected total: 24 member checkpoints.
2. Run exactly two offline PCC policy-improvement rounds with
   `paper10_geojepa_mpc.experiments.run_pcc_policy_iteration`, using the completed
   round-0 train/calibration manifests and `paper10_runs/pcc_v1/checkpoints`.
3. Run the policy-iteration `--verify-only` command and require complete,
   digest-consistent round manifests.
4. Run bounded development and freeze `pcc_v1` only after development selection
   succeeds.
5. Do not run any confirmation seed (`4000-4019` or `8000-8019`) before the
   frozen registry digest has been committed.

The exact commands and success criteria remain in Task 13 of the governing plan.
