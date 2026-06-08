from argparse import Namespace
import json

from paper10_geojepa_mpc.experiments import run_e0_value_head_train


def _args(**overrides):
    values = {
        "transition_path": "tool2/transitions.npz",
        "pairwise_path": "paper10_geojepa_mpc/experiments/results/value_labels.npz",
        "init_checkpoint": "paper10_geojepa_mpc/experiments/checkpoints/base.pt",
        "checkpoint_path": "paper10_geojepa_mpc/experiments/checkpoints/value.pt",
        "output": "paper10_geojepa_mpc/experiments/results/value_train.json",
        "n_blocks": 2600,
        "k_global": 12,
        "epochs": 7,
        "batch_size": 16,
        "lr": 0.001,
        "lambda_rank": 1.0,
        "lambda_sig": 0.0,
        "n_pairs": 8,
        "margin": 0.1,
        "pairwise_subsample": 32,
        "transition_samples": 2048,
        "pairwise_states": 128,
        "candidate_top_k": 3,
        "candidate_batch_states": 4,
        "candidate_max_states": 64,
        "checkpoint_metric": "auto",
        "checkpoint_mode": "min",
        "rank_value_weight": 0.5,
        "seed": 3035,
        "eval_seed": 12345,
        "device": "cpu",
    }
    values.update(overrides)
    return Namespace(**values)


def test_resolve_checkpoint_metric_uses_candidate_topk_regret_by_default():
    assert run_e0_value_head_train.resolve_checkpoint_metric("auto", 3) == (
        "candidate_top3_regret"
    )
    assert run_e0_value_head_train.resolve_checkpoint_metric("ranking_acc", 3) == (
        "ranking_acc"
    )


def test_build_train_kwargs_maps_cli_to_value_head_training_defaults():
    kwargs = run_e0_value_head_train.build_train_kwargs(_args())

    assert kwargs["transition_path"] == "tool2/transitions.npz"
    assert kwargs["pairwise_path"].endswith("value_labels.npz")
    assert kwargs["init_checkpoint_path"].endswith("base.pt")
    assert kwargs["checkpoint_path"].endswith("value.pt")
    assert kwargs["trainable_scope"] == "value_head"
    assert kwargs["rank_score_mode"] == "value"
    assert kwargs["compute_candidate_metrics"] is True
    assert kwargs["candidate_top_k"] == 3
    assert kwargs["checkpoint_metric"] == "candidate_top3_regret"
    assert kwargs["max_transition_samples"] == 2048
    assert kwargs["max_pairwise_states"] == 128


def test_run_training_writes_metrics_json(monkeypatch, tmp_path):
    output = tmp_path / "metrics.json"
    seen = {}

    def fake_train_e0_smoke_config(**kwargs):
        seen.update(kwargs)
        return {
            "final_loss": 1.25,
            "candidate_top3_regret": 0.0,
            "checkpoint_path": kwargs["checkpoint_path"],
        }

    monkeypatch.setattr(
        run_e0_value_head_train,
        "train_e0_smoke_config",
        fake_train_e0_smoke_config,
    )

    metrics = run_e0_value_head_train.run_training(
        _args(output=str(output), checkpoint_path=str(tmp_path / "value.pt"))
    )

    assert seen["trainable_scope"] == "value_head"
    assert metrics["final_loss"] == 1.25
    assert metrics["elapsed_sec"] >= 0.0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["candidate_top3_regret"] == 0.0
    assert payload["checkpoint_path"] == str(tmp_path / "value.pt")
