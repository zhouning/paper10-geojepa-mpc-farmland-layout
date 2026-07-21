import torch

from paper10_geojepa_mpc.models.pcc_paired_delta import PCCPairedDeltaMember


def _clone_parameters(module):
    return {
        name: parameter.detach().clone()
        for name, parameter in module.named_parameters()
    }


def _make_inputs(batch: int = 3, blocks: int = 7):
    torch.manual_seed(4)
    return {
        "block": torch.randn(batch, blocks, 17),
        "neighbour": torch.randn(batch, blocks, 17),
        "global_features": torch.randn(batch, 12),
        "candidate_actions": torch.tensor([1, 2, 3])[:batch],
        "reference_actions": torch.tensor([0, 0, 0])[:batch],
    }


def test_paired_delta_member_outputs_direct_horizon_delta_and_scale():
    model = PCCPairedDeltaMember(17, 12, hidden_dim=16)

    output = model(**_make_inputs())

    assert output.delta_mean.shape == (3, 3, 4)
    assert output.delta_log_scale.shape == (3, 3, 4)
    assert output.candidate_absolute_mean.shape == (3, 4)
    assert output.candidate_absolute_log_scale.shape == (3, 4)
    assert output.executable_logit.shape == (3,)
    assert output.candidate_latent.shape == output.reference_latent.shape
    assert torch.isfinite(output.delta_mean).all()
    assert torch.all(output.delta_log_scale >= -8.0)
    assert torch.all(output.delta_log_scale <= 5.0)


def test_reference_action_changes_delta_but_not_candidate_monitoring_heads():
    model = PCCPairedDeltaMember(17, 12, hidden_dim=16).eval()
    inputs = _make_inputs()
    changed = dict(inputs)
    changed["reference_actions"] = torch.tensor([4, 5, 6])

    original = model(**inputs)
    with_changed_reference = model(**changed)

    assert not torch.allclose(
        original.delta_mean,
        with_changed_reference.delta_mean,
    )
    torch.testing.assert_close(
        original.candidate_absolute_mean,
        with_changed_reference.candidate_absolute_mean,
    )
    torch.testing.assert_close(
        original.executable_logit,
        with_changed_reference.executable_logit,
    )


def test_model_uses_no_county_specific_action_embedding():
    model = PCCPairedDeltaMember(17, 12)
    assert not any("embedding" in name for name, _ in model.named_parameters())

    large_county = _make_inputs(blocks=11)
    model(**large_county)


def test_target_encoder_is_frozen_and_moves_only_by_ema():
    model = PCCPairedDeltaMember(17, 12, ema_decay=0.5)
    assert not any(
        parameter.requires_grad
        for parameter in model.target_encoder.parameters()
    )
    before = _clone_parameters(model.target_encoder)
    online_before = _clone_parameters(model.online_encoder)
    for name in before:
        torch.testing.assert_close(before[name], online_before[name])

    with torch.no_grad():
        next(model.online_encoder.parameters()).add_(2.0)
    model.update_target_encoder()

    after = _clone_parameters(model.target_encoder)
    online = dict(model.online_encoder.named_parameters())
    assert any(not torch.equal(before[name], after[name]) for name in before)
    for name, target in after.items():
        expected = 0.5 * before[name] + 0.5 * online[name]
        torch.testing.assert_close(target, expected)


def test_target_latent_has_stopped_gradient():
    model = PCCPairedDeltaMember(17, 12)
    inputs = _make_inputs()

    target = model.encode_target(
        inputs["block"],
        inputs["neighbour"],
        inputs["global_features"],
        inputs["candidate_actions"],
    )

    assert target.requires_grad is False


def test_direct_pair_is_invariant_to_consistent_block_permutation():
    model = PCCPairedDeltaMember(17, 12, hidden_dim=16).eval()
    inputs = _make_inputs(blocks=7)
    permutation = torch.tensor([4, 0, 6, 2, 1, 5, 3])
    inverse = torch.argsort(permutation)
    permuted = {
        "block": inputs["block"][:, permutation],
        "neighbour": inputs["neighbour"][:, permutation],
        "global_features": inputs["global_features"],
        "candidate_actions": inverse[inputs["candidate_actions"]],
        "reference_actions": inverse[inputs["reference_actions"]],
    }

    original_output = model(**inputs)
    permuted_output = model(**permuted)

    torch.testing.assert_close(
        original_output.delta_mean,
        permuted_output.delta_mean,
    )
    torch.testing.assert_close(
        original_output.delta_log_scale,
        permuted_output.delta_log_scale,
    )
    torch.testing.assert_close(
        original_output.candidate_absolute_mean,
        permuted_output.candidate_absolute_mean,
    )
    torch.testing.assert_close(
        original_output.executable_logit,
        permuted_output.executable_logit,
    )
