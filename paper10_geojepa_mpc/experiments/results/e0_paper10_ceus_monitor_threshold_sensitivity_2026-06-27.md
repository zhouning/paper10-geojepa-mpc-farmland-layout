# Monitor-threshold sensitivity audit

Status: monitor-threshold sensitivity audit.

This audit reruns gate classification only; it does not train models or add rollout results.

## Threshold sets

| name | candidate regret max | candidate overlap min | one-step regret min |
|---|---:|---:|---:|
| strict | 0.2000 | 0.5500 | 0.5000 |
| default | 0.2500 | 0.5000 | 0.2500 |
| lenient | 0.3000 | 0.4500 | 0.1000 |

## Monitor sensitivity rows

| monitor | current default pass | pass fraction | stability class |
|---|---|---:|---|
| bishan_10x12_top4 | no | 0.000 | robust_stop |
| bishan_20x16_top5 | yes | 1.000 | robust_pass |
| bishan_20x16_top4 | no | 0.000 | robust_stop |
| frontier_random050_50x16_h5_seed47_f050_top5 | no | 0.000 | robust_stop |
| frontier_random050_50x16_h5_seed47_f050_top6 | no | 0.000 | robust_stop |
| frontier_random050_50x16_h5_seed47_f050_top8 | no | 0.333 | threshold_sensitive_stop |
| frontier_random050_50x16_h5_seed47_f050_top10 | no | 0.333 | threshold_sensitive_stop |
| frontier_random050_50x16_h5_seed47_f050_top12 | no | 0.333 | threshold_sensitive_stop |
| frontier_random050_50x16_h5_seed48_f050_top5 | no | 0.333 | threshold_sensitive_stop |
| frontier_random050_50x16_h5_seed48_f050_top6 | yes | 0.667 | threshold_sensitive_pass |
| frontier_random050_50x16_h5_seed48_f050_top8 | no | 0.333 | threshold_sensitive_stop |
| frontier_random050_50x16_h5_seed48_f050_top10 | no | 0.333 | threshold_sensitive_stop |
| frontier_random050_50x16_h5_seed48_f050_top12 | no | 0.333 | threshold_sensitive_stop |
| frontier_random050_50x20_h5_seed47_f050_top5 | no | 0.000 | robust_stop |
| frontier_random050_50x20_h5_seed47_f050_top6 | no | 0.000 | robust_stop |
| frontier_random050_50x20_h5_seed47_f050_top8 | no | 0.333 | threshold_sensitive_stop |
| frontier_random050_50x20_h5_seed47_f050_top10 | no | 0.000 | robust_stop |
| frontier_random050_50x20_h5_seed47_f050_top12 | no | 0.000 | robust_stop |
| frontier_random050_50x20_h5_seed48_f050_top5 | no | 0.000 | robust_stop |
| frontier_random050_50x20_h5_seed48_f050_top6 | no | 0.000 | robust_stop |
| frontier_random050_50x20_h5_seed48_f050_top8 | no | 0.000 | robust_stop |
| frontier_random050_50x20_h5_seed48_f050_top10 | no | 0.000 | robust_stop |
| frontier_random050_50x20_h5_seed48_f050_top12 | no | 0.000 | robust_stop |
| frontier_random050_50x24_h5_seed47_f075_top5 | no | 0.000 | robust_stop |
| frontier_random050_50x24_h5_seed47_f075_top6 | no | 0.000 | robust_stop |
| frontier_random050_50x24_h5_seed47_f075_top8 | no | 0.000 | robust_stop |
| frontier_random050_50x24_h5_seed47_f075_top10 | no | 0.333 | threshold_sensitive_stop |
| frontier_random050_50x24_h5_seed47_f075_top12 | yes | 0.667 | threshold_sensitive_pass |
| frontier_random050_50x24_h5_seed48_f075_top5 | no | 0.000 | robust_stop |
| frontier_random050_50x24_h5_seed48_f075_top6 | no | 0.000 | robust_stop |
| frontier_random050_50x24_h5_seed48_f075_top8 | no | 0.000 | robust_stop |
| frontier_random050_50x24_h5_seed48_f075_top10 | no | 0.000 | robust_stop |
| frontier_random050_50x24_h5_seed48_f075_top12 | no | 0.333 | threshold_sensitive_stop |

## Recorded-decision provenance

| monitor | recorded decision | recorded-threshold pass | threshold provenance | decision alignment |
|---|---|---|---|---|
| bishan_10x12_top4 | continue | yes | historical_thresholds | recorded_continue_current_default_stop |
| bishan_20x16_top5 | continue | yes | default_thresholds | recorded_continue_current_default_pass |
| bishan_20x16_top4 | stop | no | default_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x16_h5_seed47_f050_top5 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x16_h5_seed47_f050_top6 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x16_h5_seed47_f050_top8 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x16_h5_seed47_f050_top10 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x16_h5_seed47_f050_top12 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x16_h5_seed48_f050_top5 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x16_h5_seed48_f050_top6 | continue | n/a | no_recorded_thresholds | recorded_continue_current_default_pass |
| frontier_random050_50x16_h5_seed48_f050_top8 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x16_h5_seed48_f050_top10 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x16_h5_seed48_f050_top12 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x20_h5_seed47_f050_top5 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x20_h5_seed47_f050_top6 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x20_h5_seed47_f050_top8 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x20_h5_seed47_f050_top10 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x20_h5_seed47_f050_top12 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x20_h5_seed48_f050_top5 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x20_h5_seed48_f050_top6 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x20_h5_seed48_f050_top8 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x20_h5_seed48_f050_top10 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x20_h5_seed48_f050_top12 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x24_h5_seed47_f075_top5 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x24_h5_seed47_f075_top6 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x24_h5_seed47_f075_top8 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x24_h5_seed47_f075_top10 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x24_h5_seed47_f075_top12 | continue | n/a | no_recorded_thresholds | recorded_continue_current_default_pass |
| frontier_random050_50x24_h5_seed48_f075_top5 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x24_h5_seed48_f075_top6 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x24_h5_seed48_f075_top8 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x24_h5_seed48_f075_top10 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |
| frontier_random050_50x24_h5_seed48_f075_top12 | stop | n/a | no_recorded_thresholds | recorded_stop_current_default_stop |

## Interpretation boundary

- `robust_pass` means the row passes strict, default and lenient thresholds.
- `threshold_sensitive_pass` means the row passes the default gate but not every stricter threshold.
- `robust_stop` means the row fails every tested threshold set.
- `historical_thresholds` means the recorded monitor used thresholds that differ from the current CEUS audit default; the recorded decision is preserved but not treated as a current-threshold pass.
- This audit supports threshold transparency only; it is not new training or rollout evidence.
