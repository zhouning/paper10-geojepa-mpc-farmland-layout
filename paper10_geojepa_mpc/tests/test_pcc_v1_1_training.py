import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import torch

from paper10_geojepa_mpc.models.geojepa_transition_model import (
    GeoJEPATransitionModel,
)
from paper10_geojepa_mpc.models.pcc_paired_delta import PCCPairedDeltaMember
from paper10_geojepa_mpc.experiments import run_pcc_v1_1_train as training_cli
from paper10_geojepa_mpc.experiments.pcc_value_labels import (
    write_label_manifest,
    write_trajectory_artifact,
)
from paper10_geojepa_mpc.training import pcc_v1_1_training as training
from paper10_geojepa_mpc.training.pcc_training import (
    heteroscedastic_objective_loss,
)

def _tiny_source_arrays() -> dict[str, np.ndarray]:
    candidate = np.arange(12, dtype=np.float32).reshape(1, 1, 3, 4)
    reference = np.full((1, 1, 3, 4), 2.0, dtype=np.float32)
    block = np.arange(6, dtype=np.float32).reshape(1, 3, 2)
    global_features = np.asarray([[0.25, -0.5]], dtype=np.float32)
    return {
        "states_bf": block,
        "states_neighbor_bf": block + 0.5,
        "states_gf": global_features,
        "actions": np.asarray([[2]], dtype=np.int64),
        "reference_actions": np.asarray([0], dtype=np.int64),
        "objective_returns": candidate,
        "reference_objective_returns": reference,
        "candidate_next_bf": block[:, None] + 0.1,
        "candidate_next_gf": global_features[:, None] + 0.1,
        "reference_next_bf": block[:, None] + 0.05,
        "reference_next_gf": global_features[:, None] + 0.05,
        "executable_targets": np.asarray([[1.0]], dtype=np.float32),
    }


def _write_tiny_e0_checkpoint(
    path: Path,
    *,
    block_feature_dim: int = 17,
    global_feature_dim: int = 12,
    hidden_dim: int = 32,
) -> Path:
    torch.manual_seed(19)
    model = GeoJEPATransitionModel(
        n_blocks=7,
        k_global=global_feature_dim,
        block_feature_dim=block_feature_dim,
        hidden_dim=hidden_dim,
    )
    torch.save(
        {
            "model_class": "GeoJEPATransitionModel",
            "model_kwargs": {
                "n_blocks": 7,
                "k_global": global_feature_dim,
                "block_feature_dim": block_feature_dim,
                "hidden_dim": hidden_dim,
            },
            "state_dict": model.state_dict(),
        },
        path,
    )
    return path


def test_batch_targets_are_direct_candidate_minus_reference():
    arrays = _tiny_source_arrays()

    batch = next(
        training.iter_paired_batches(
            arrays,
            batch_size=4,
            rng=np.random.default_rng(3),
        )
    )

    expected = (
        arrays["objective_returns"][0, 0]
        - arrays["reference_objective_returns"][0, 0]
    )
    np.testing.assert_allclose(batch["target_delta"][0], expected)
    np.testing.assert_allclose(
        batch["candidate_absolute_target"][0],
        arrays["objective_returns"][0, 0, 0],
    )
    assert batch["candidate_actions"].tolist() == [2]
    assert batch["reference_actions"].tolist() == [0]


def test_transfer_initialization_copies_only_compatible_encoders(tmp_path):
    source = _write_tiny_e0_checkpoint(tmp_path / "e0.pt")
    model = PCCPairedDeltaMember(17, 12, hidden_dim=32)
    paired_head_before = model.delta_head.weight.detach().clone()

    digest = training.initialize_from_paper9(model, source)
    checkpoint = torch.load(source, map_location="cpu", weights_only=False)

    assert digest == hashlib.sha256(source.read_bytes()).hexdigest()
    assert torch.equal(
        model.online_encoder.block_encoder[0].weight,
        checkpoint["state_dict"]["block_encoder.0.weight"],
    )
    assert torch.equal(
        model.online_encoder.neighbour_encoder[0].weight,
        checkpoint["state_dict"]["block_encoder.0.weight"],
    )
    assert torch.equal(
        model.online_encoder.global_encoder[0].weight,
        checkpoint["state_dict"]["global_encoder.0.weight"],
    )
    assert torch.equal(paired_head_before, model.delta_head.weight)
    for name, value in model.online_encoder.state_dict().items():
        assert torch.equal(value, model.target_encoder.state_dict()[name])
    assert not any("action_emb" in name for name, _ in model.named_parameters())


def test_direct_delta_loss_does_not_sum_marginal_variances():
    mean = torch.zeros(2, 3, 4)
    log_scale = torch.zeros(2, 3, 4)
    target = torch.ones(2, 3, 4)

    loss = training.direct_delta_nll(target, mean, log_scale)
    expected = heteroscedastic_objective_loss(target, mean, log_scale)

    assert torch.equal(loss, expected)


def _valid_pcc_v1_1_checkpoint() -> dict[str, object]:
    model = PCCPairedDeltaMember(17, 12, hidden_dim=8)
    return {
        "model_class": "PCCPairedDeltaMember",
        "protocol_id": "pcc_v1_1",
        "source_protocol_id": "pcc_v1",
        "model_kwargs": model.model_kwargs(),
        "objective_names": [
            "reward",
            "slope_benefit",
            "contiguity_benefit",
            "connected_area_benefit",
        ],
        "horizons": [1, 3, 5],
        "delta_scaling": {
            "center": np.zeros((3, 4)).tolist(),
            "scale": np.ones((3, 4)).tolist(),
        },
        "absolute_scaling": {
            "center": np.zeros(4).tolist(),
            "scale": np.ones(4).tolist(),
        },
        "state_dict": {
            name: value.detach().cpu().clone()
            for name, value in model.state_dict().items()
        },
    }


def test_direct_and_absolute_scaling_use_separate_target_spaces():
    candidate = np.arange(6 * 3 * 4, dtype=np.float32).reshape(6, 3, 4)
    reference = np.full_like(candidate, 10.0)

    delta_scaling, absolute_scaling = training.compute_paired_scaling(
        candidate,
        reference,
    )

    assert np.asarray(delta_scaling["center"]).shape == (3, 4)
    assert np.asarray(delta_scaling["scale"]).shape == (3, 4)
    assert np.asarray(absolute_scaling["center"]).shape == (4,)
    assert np.asarray(absolute_scaling["scale"]).shape == (4,)
    np.testing.assert_allclose(
        delta_scaling["center"],
        np.median(candidate - reference, axis=0),
    )
    np.testing.assert_allclose(
        absolute_scaling["center"],
        np.median(candidate[:, 0], axis=0),
    )
    assert np.all(np.asarray(delta_scaling["scale"]) > 0.0)
    assert np.all(np.asarray(absolute_scaling["scale"]) > 0.0)


def test_pcc_v1_1_checkpoint_round_trip(tmp_path):
    path = tmp_path / "member_0.pt"
    torch.save(_valid_pcc_v1_1_checkpoint(), path)

    model, checkpoint = training.load_pcc_v1_1_checkpoint(path)

    assert checkpoint["protocol_id"] == "pcc_v1_1"
    output = model(
        torch.randn(1, 5, 17),
        torch.randn(1, 5, 17),
        torch.randn(1, 12),
        torch.tensor([4]),
        torch.tensor([0]),
    )
    assert output.delta_mean.shape == (1, 3, 4)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda row: row.update(protocol_id="pcc_v1"), "protocol"),
        (
            lambda row: row.update(objective_names=["reward"]),
            "objective order",
        ),
        (lambda row: row.update(horizons=[1, 5, 3]), "horizon"),
        (
            lambda row: row["delta_scaling"].update(
                scale=np.zeros((3, 4)).tolist()
            ),
            "delta_scaling",
        ),
        (
            lambda row: row["absolute_scaling"].update(
                center=[0.0, 0.0, float("nan"), 0.0]
            ),
            "absolute_scaling",
        ),
    ],
)
def test_pcc_v1_1_checkpoint_rejects_wrong_contract(
    tmp_path,
    mutation,
    message,
):
    checkpoint = _valid_pcc_v1_1_checkpoint()
    mutation(checkpoint)
    path = tmp_path / "invalid.pt"
    torch.save(checkpoint, path)

    with pytest.raises(ValueError, match=message):
        training.load_pcc_v1_1_checkpoint(path)


def test_train_step_updates_online_model_and_ema_target():
    model = PCCPairedDeltaMember(2, 2, hidden_dim=8, ema_decay=0.5)
    optimizer = torch.optim.AdamW(
        [
            parameter
            for parameter in model.parameters()
            if parameter.requires_grad
        ],
        lr=1e-2,
    )
    batch = next(
        training.iter_paired_batches(
            _tiny_source_arrays(),
            batch_size=4,
            rng=np.random.default_rng(3),
        )
    )
    tensors = {
        key: torch.as_tensor(
            value,
            dtype=torch.long
            if key in {"candidate_actions", "reference_actions"}
            else torch.float32,
        )
        for key, value in batch.items()
    }
    target_before = {
        name: value.detach().clone()
        for name, value in model.target_encoder.named_parameters()
    }

    metrics = training.train_paired_batch(
        model,
        optimizer,
        tensors,
        delta_center=torch.zeros(3, 4),
        delta_scale=torch.ones(3, 4),
        absolute_center=torch.zeros(4),
        absolute_scale=torch.ones(4),
    )

    assert set(metrics) == {
        "loss",
        "delta_nll",
        "absolute_nll",
        "jepa_loss",
        "rank_loss",
        "executable_bce",
        "sigreg",
    }
    assert all(np.isfinite(value) for value in metrics.values())
    target_after = dict(model.target_encoder.named_parameters())
    assert any(
        not torch.equal(target_before[name], target_after[name])
        for name in target_before
    )


def test_delta_ranking_uses_raw_zero_boundary_after_normalization():
    raw_target = torch.tensor([[[1.0]]])
    center = torch.tensor([[2.0]])
    scale = torch.tensor([[1.0]])

    correct_side = training.zero_boundary_delta_ranking_loss(
        raw_target,
        predicted_normalized=torch.tensor([[[-1.0]]]),
        center=center,
        scale=scale,
    )
    wrong_side = training.zero_boundary_delta_ranking_loss(
        raw_target,
        predicted_normalized=torch.tensor([[[-3.0]]]),
        center=center,
        scale=scale,
    )

    assert correct_side < wrong_side


def test_delta_ranking_ignores_exact_zero_targets():
    loss = training.zero_boundary_delta_ranking_loss(
        torch.zeros(2, 3, 1),
        predicted_normalized=torch.randn(2, 3, 1),
        center=torch.ones(3, 1),
        scale=torch.ones(3, 1),
    )

    assert loss == 0.0


def _training_arrays(seed: int) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    n_states, n_candidates, n_blocks = 2, 2, 3
    block = rng.normal(size=(n_states, n_blocks, 2)).astype(np.float32)
    neighbour = rng.normal(size=(n_states, n_blocks, 2)).astype(np.float32)
    global_features = rng.normal(size=(n_states, 2)).astype(np.float32)
    actions = np.asarray([[0, 1], [1, 2]], dtype=np.int64)
    reference_actions = np.zeros(n_states, dtype=np.int64)
    candidate_next_block = np.repeat(block[:, None], n_candidates, axis=1)
    reference_next_block = np.repeat(block[:, None], n_candidates, axis=1)
    candidate_next_global = np.repeat(
        global_features[:, None],
        n_candidates,
        axis=1,
    )
    reference_next_global = candidate_next_global.copy()
    objective = rng.normal(
        size=(n_states, n_candidates, 3, 4)
    ).astype(np.float32)
    reference = rng.normal(
        size=(n_states, n_candidates, 3, 4)
    ).astype(np.float32)
    return {
        "states_bf": block,
        "states_neighbor_bf": neighbour,
        "states_gf": global_features,
        "actions": actions,
        "reference_actions": reference_actions,
        "objective_returns": objective,
        "reference_objective_returns": reference,
        "candidate_next_bf": candidate_next_block,
        "candidate_next_gf": candidate_next_global,
        "reference_next_bf": reference_next_block,
        "reference_next_gf": reference_next_global,
        "executable_targets": np.asarray(
            [[1.0, 0.0], [1.0, 1.0]],
            dtype=np.float32,
        ),
        "continuation_seeds": np.full(
            (n_states, n_candidates),
            seed,
            dtype=np.uint64,
        ),
        "trajectory_ids": np.full(n_states, seed, dtype=np.int64),
        "state_steps": np.arange(n_states, dtype=np.int64),
        "horizons": np.asarray([1, 3, 5], dtype=np.int64),
    }


def _source_manifest(root: Path) -> tuple[Path, dict[str, object]]:
    artifacts = [
        write_trajectory_artifact(root, seed, _training_arrays(seed))
        for seed in (1000, 1001)
    ]
    payload = write_label_manifest(
        root,
        protocol_id="pcc_v1",
        partition="train",
        artifacts=artifacts,
        continuation_policy={"name": "paper9_mpc"},
        horizons=(1, 3, 5),
    )
    return root / "manifest.json", payload


def test_tiny_ensemble_training_saves_pcc_v1_1_lineage(tmp_path):
    manifest, source = _source_manifest(tmp_path / "labels")
    reference = _write_tiny_e0_checkpoint(
        tmp_path / "e0.pt",
        block_feature_dim=2,
        global_feature_dim=2,
        hidden_dim=8,
    )

    paths = training.train_pcc_v1_1_ensemble(
        labels_manifest=manifest,
        reference_checkpoint=reference,
        expected_source_manifest_digest=source["manifest_digest"],
        expected_transfer_checkpoint_sha256=hashlib.sha256(
            reference.read_bytes()
        ).hexdigest(),
        registry_digest="b" * 64,
        model_seed=5101,
        ensemble_size=2,
        epochs=1,
        batch_size=4,
        learning_rate=0.0,
        device="cpu",
        output_dir=tmp_path / "checkpoints",
        hidden_dim=8,
    )

    assert [path.name for path in paths] == ["member_0.pt", "member_1.pt"]
    loaded = [training.load_pcc_v1_1_checkpoint(path)[1] for path in paths]
    assert loaded[0]["member_seed"] != loaded[1]["member_seed"]
    assert all(row["protocol_id"] == "pcc_v1_1" for row in loaded)
    assert all(row["source_protocol_id"] == "pcc_v1" for row in loaded)
    assert all(
        row["source_manifest_digest"] == source["manifest_digest"]
        for row in loaded
    )
    assert all(
        row["transfer_checkpoint_sha256"]
        == hashlib.sha256(reference.read_bytes()).hexdigest()
        for row in loaded
    )
    assert all(len(row["bootstrap_trajectory_ids"]) == 2 for row in loaded)
    assert all(
        np.asarray(row["delta_scaling"]["center"]).shape == (3, 4)
        for row in loaded
    )
    assert all(
        np.asarray(row["absolute_scaling"]["center"]).shape == (4,)
        for row in loaded
    )
    assert all(row["metrics"]["n_updates"] > 0 for row in loaded)


def test_training_rejects_source_digest_before_creating_output(tmp_path):
    manifest, _ = _source_manifest(tmp_path / "labels")
    reference = _write_tiny_e0_checkpoint(
        tmp_path / "e0.pt",
        block_feature_dim=2,
        global_feature_dim=2,
        hidden_dim=8,
    )
    output_dir = tmp_path / "must_not_exist"

    with pytest.raises(ValueError, match="source manifest digest"):
        training.train_pcc_v1_1_ensemble(
            labels_manifest=manifest,
            reference_checkpoint=reference,
            expected_source_manifest_digest="a" * 64,
            expected_transfer_checkpoint_sha256=hashlib.sha256(
                reference.read_bytes()
            ).hexdigest(),
            registry_digest="b" * 64,
            model_seed=5101,
            ensemble_size=1,
            epochs=1,
            batch_size=4,
            learning_rate=0.0,
            device="cpu",
            output_dir=output_dir,
            hidden_dim=8,
        )

    assert not output_dir.exists()


def _pilot_registry(source_digest: str, transfer_digest: str):
    return {
        "protocol_id": "pcc_v1_1",
        "status": "development",
        "model_seeds": [5101],
        "source_inputs": {
            "protocol_id": "pcc_v1",
            "train_manifest_digest": source_digest,
        },
        "model": {
            "class": "PCCPairedDeltaMember",
            "hidden_dim": 8,
            "ema_decay": 0.99,
            "transfer_checkpoint_sha256": transfer_digest,
        },
        "pilot_training": {
            "epochs": 1,
            "batch_size": 4,
            "learning_rate": 0.0,
        },
        "viability": {"ensemble_size": 1},
    }


def _training_cli_args(
    *,
    registry: Path,
    manifest: Path,
    reference: Path,
    output_dir: Path,
    learning_rate: float = 0.0,
) -> list[str]:
    return [
        "--registry",
        str(registry),
        "--labels-manifest",
        str(manifest),
        "--reference-checkpoint",
        str(reference),
        "--model-seed",
        "5101",
        "--ensemble-size",
        "1",
        "--epochs",
        "1",
        "--batch-size",
        "4",
        "--learning-rate",
        str(learning_rate),
        "--device",
        "cpu",
        "--output-dir",
        str(output_dir),
    ]


def test_training_cli_writes_reloadable_summary(tmp_path, monkeypatch):
    manifest, source = _source_manifest(tmp_path / "labels")
    reference = _write_tiny_e0_checkpoint(
        tmp_path / "e0.pt",
        block_feature_dim=2,
        global_feature_dim=2,
        hidden_dim=8,
    )
    registry_path = tmp_path / "pcc_v1_1.json"
    registry_path.write_text("{}\n", encoding="utf-8")
    registry = _pilot_registry(
        source["manifest_digest"],
        hashlib.sha256(reference.read_bytes()).hexdigest(),
    )
    monkeypatch.setattr(training_cli, "load_registry", lambda _: registry)
    monkeypatch.setattr(training_cli, "validate_registry", lambda _: None)
    output_dir = tmp_path / "checkpoints"

    summary = training_cli.main(
        _training_cli_args(
            registry=registry_path,
            manifest=manifest,
            reference=reference,
            output_dir=output_dir,
        )
    )

    saved = json.loads(
        (output_dir / "training_summary.json").read_text(encoding="utf-8")
    )
    assert saved == summary
    assert saved["protocol_id"] == "pcc_v1_1"
    assert len(saved["checkpoints"]) == 1
    checkpoint_path = Path(saved["checkpoints"][0]["path"])
    training.load_pcc_v1_1_checkpoint(checkpoint_path)
    assert saved["checkpoints"][0]["sha256"] == hashlib.sha256(
        checkpoint_path.read_bytes()
    ).hexdigest()


def test_training_cli_rejects_hyperparameter_change_before_output(
    tmp_path,
    monkeypatch,
):
    manifest, source = _source_manifest(tmp_path / "labels")
    reference = _write_tiny_e0_checkpoint(
        tmp_path / "e0.pt",
        block_feature_dim=2,
        global_feature_dim=2,
        hidden_dim=8,
    )
    registry_path = tmp_path / "pcc_v1_1.json"
    registry_path.write_text("{}\n", encoding="utf-8")
    registry = _pilot_registry(
        source["manifest_digest"],
        hashlib.sha256(reference.read_bytes()).hexdigest(),
    )
    monkeypatch.setattr(training_cli, "load_registry", lambda _: registry)
    monkeypatch.setattr(training_cli, "validate_registry", lambda _: None)
    output_dir = tmp_path / "must_not_exist"

    with pytest.raises(ValueError, match="pilot training hyperparameters"):
        training_cli.main(
            _training_cli_args(
                registry=registry_path,
                manifest=manifest,
                reference=reference,
                output_dir=output_dir,
                learning_rate=0.1,
            )
        )

    assert not output_dir.exists()
