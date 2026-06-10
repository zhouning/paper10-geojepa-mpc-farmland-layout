# Dongxing Real-Environment Rollout Checkpoint Family

Date: 2026-06-10

This note extends the single-checkpoint Dongxing rollout comparison to the full
set of already trained 1000-state pairwise-only all-parameter checkpoints:
three Bishan-initialized transfer checkpoints and three Dongxing scratch
checkpoints. Each checkpoint is evaluated with five 100-step real-environment
rollout seeds, for 15 episodes per mode.

## Scope

The goal is to test whether the previous seed3035 result is stable across
training seeds. No new model training was performed here. The experiment uses
the six checkpoints produced by the earlier pairwise-only diagnostic:

- `transfer_all_seed3035_1000s_3e.pt`
- `transfer_all_seed3036_1000s_3e.pt`
- `transfer_all_seed3037_1000s_3e.pt`
- `scratch_all_seed3035_1000s_3e.pt`
- `scratch_all_seed3036_1000s_3e.pt`
- `scratch_all_seed3037_1000s_3e.pt`

All rollout JSON outputs were written under:

- `reviewer_outputs\dongxing_rollout_compare\`

That directory is ignored by git. The committed source table for this note is:

- `paper10_geojepa_mpc/experiments/results/e0_dongxing_rollout_checkpoint_family_2026-06-10.csv`

## Rollout Protocol

All six evaluations used the same real Dongxing/Neijiang environment and the
same planner settings:

| setting | value |
|---|---:|
| environment source | `neijiang` |
| prepared dir | `D:\test\neijiang_cross_region` |
| rollout seeds | `0-4` |
| rollout steps | 100 |
| horizon | 5 |
| top-k | 50 |
| mask mode | `executable` |
| selector | `value_filter` |
| candidate score mode | `blend` |
| candidate value weight | 0.1 |
| device | `cpu` |

Command template:

```powershell
D:\adk\.venv\Scripts\python.exe -X utf8 -m paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke --env-source neijiang --checkpoint reviewer_outputs\dongxing_paper10_pairwise_all_compare\<mode>_all_seed<seed>_1000s_3e.pt --prepared-dir D:\test\neijiang_cross_region --rollout-steps 100 --horizon 5 --top-k 50 --seeds 0-4 --device cpu --mask-mode executable --selector value_filter --candidate-score-mode blend --candidate-value-weight 0.1 --progress-interval 25 --output reviewer_outputs\dongxing_rollout_compare\<mode>_all_seed<seed>_1000s_h5_k50_seeds0-4_100step.json
```

All six JSON files reported `complete=True` and `n_episodes=5`.

## Per-Checkpoint Results

Higher total reward and contiguity change are better. More negative slope
change means lower final average farmland slope. Baimu area change is measured
relative to the initial connected baimu-fang area.

| mode | train seed | mean total reward | reward sd | min reward | max reward | mean slope change pct | mean contiguity change | mean baimu area change ha |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| transfer | 3035 | 33.887593362870945 | 4.20111235969505 | 29.0438474218871 | 40.4284925509126 | -0.28770717053397393 | 0.010128132242970355 | -160.54935413917303 |
| transfer | 3036 | 29.048102448774028 | 7.41676836077866 | 21.8594603432674 | 41.067889805979 | -0.2639458570124734 | 0.01644290899549574 | 36.47001914041758 |
| transfer | 3037 | 21.80858357972548 | 3.3864913673574 | 17.3266016889803 | 26.6575857117609 | -0.2520297728299974 | 0.01602309004241942 | -76.43150013159037 |
| scratch | 3035 | 60.85876916823652 | 10.4159501927597 | 44.1107268772245 | 70.7277540677464 | -0.15595155384905524 | 0.007827874229238762 | -96.70650328375578 |
| scratch | 3036 | 34.38589441338785 | 6.80637749318255 | 25.1954792754554 | 42.0777426693849 | -0.14584970557922333 | 0.004154458389819471 | -171.02929424405337 |
| scratch | 3037 | 11.857508243129436 | 4.41537897531618 | 7.13375489766855 | 17.3422640910433 | -0.12569856720744627 | 0.01091529277998866 | -32.83568735643864 |

## Family-Level Results

Aggregating all 15 rollout episodes per mode:

| mode | episodes | mean total reward | reward sd | min reward | max reward | mean slope change pct | mean contiguity change | mean baimu area change ha |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| transfer | 15 | 28.2480931304568 | 7.10161345954682 | 17.3266016889803 | 41.067889805979 | -0.267894266792148 | 0.0141980437602952 | -66.8369450434486 |
| scratch | 15 | 35.7007239415846 | 21.897540980278 | 7.13375489766855 | 70.7277540677464 | -0.142499942211908 | 0.0076325417996823 | -100.190494961416 |

Across checkpoint-level mean rewards:

| mode | train seeds | mean of checkpoint mean rewards | sd of checkpoint mean rewards | checkpoint mean rewards |
|---|---:|---:|---:|---|
| transfer | 3 | 28.2480931304568 | 6.07911428724421 | 33.887593362870945, 29.048102448774028, 21.80858357972548 |
| scratch | 3 | 35.7007239415846 | 24.5270763765022 | 60.85876916823652, 34.38589441338785, 11.857508243129436 |

## Interpretation

The broader checkpoint-family evidence is mixed but still does not support a
clean cross-region transfer advantage.

Reward:

- Scratch has the higher 15-episode mean total reward:
  `35.7007` vs. `28.2481`.
- Scratch is much less stable across training seeds:
  checkpoint-mean reward sd `24.5271` vs. `6.0791`.
- Transfer wins the weakest scratch seed3037 comparison, but loses to scratch
  seed3035 and seed3036.

Final physical metrics:

- Transfer has larger final slope reduction:
  `-0.2679` vs. `-0.1425`.
- Transfer has larger final contiguity improvement:
  `0.0142` vs. `0.0076`.
- Transfer has less final baimu-fang area loss on average:
  `-66.8369 ha` vs. `-100.1905 ha`.

The important point is that final physical metrics and accumulated reward do
not rank the checkpoint families identically. The reward is path-dependent and
includes per-step baimu-fang area changes, baimu-fang count bonuses, and
penalties, not only the final metrics. Therefore the current result should be
reported as:

> Bishan-initialized transfer is feasible and more stable in this Dongxing
> stress test, with better final slope and contiguity metrics, but it does not
> yet improve the primary accumulated reward over Dongxing scratch training.

## Paper10 Implication

For Paper10, Dongxing should not be used as a positive transfer-performance
claim yet. It is better used as a rigorous external-region stress test showing:

1. the real-environment pipeline can move from Bishan to Dongxing;
2. the 3711-action adapter and rollout path work on real data;
3. naive pairwise-only transfer is not enough to guarantee reward improvement;
4. objective alignment matters because pairwise ranking quality, final physical
   metrics, and accumulated environment reward can disagree.

The next experiment should modify the adaptation target, not merely repeat the
same pairwise-only training. The most defensible next technical step is a
baimu-aware Dongxing value target or a Dongxing-specific planner weight sweep.
