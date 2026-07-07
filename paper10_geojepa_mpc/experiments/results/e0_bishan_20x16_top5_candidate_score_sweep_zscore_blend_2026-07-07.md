# Candidate score sweep diagnostic

This diagnostic compares candidate filter scoring modes on the same reward-top1 state path. It is not a confirmatory rollout.

- checkpoint: `paper10_geojepa_mpc\experiments\checkpoints\e0_frontier_random050_value_head_20x16_h5_seed44_top5\value_head_seed3044.pt`
- prepared_dir: `D:\test`
- seed: `0`
- steps: `10/10`
- top_k: `50`

| key | mode | value_weight | topk_overlap | top1_regret | topk_best_regret | spearman |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| blend_w0p10 | blend | 0.1000 | 0.9760 | 0.0018 | 0.0000 | 0.9998 |
| zscore_blend_w0p20 | zscore_blend | 0.2000 | 0.9460 | 0.0074 | 0.0000 | 0.9993 |
| zscore_blend_w0p50 | zscore_blend | 0.5000 | 0.8640 | 0.0389 | 0.0000 | 0.9955 |
| zscore_blend_w0p80 | zscore_blend | 0.8000 | 0.8220 | 0.0389 | 0.0000 | 0.9887 |
| value_w0p50 | value | 0.5000 | 0.7660 | 0.0389 | 0.0000 | 0.9824 |

## Recommendation

Promote `blend_w0p10` to short rollout first.

```powershell
python -m paper10_geojepa_mpc.experiments.run_e0_env_rollout_smoke --checkpoint paper10_geojepa_mpc\experiments\checkpoints\e0_frontier_random050_value_head_20x16_h5_seed44_top5\value_head_seed3044.pt --prepared-dir D:\test --selector value_filter --mask-mode executable --horizon 5 --top-k 50 --rollout-steps 10 --seed 0 --candidate-score-mode blend --candidate-value-weight 0.10
```

## Boundary

- No training was rerun.
- No confirmatory rollout was rerun inside this diagnostic.
- Escalate only if the short rollout improves or preserves reward with acceptable variance.
