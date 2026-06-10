import torch

from paper10_geojepa_mpc.training.ranking import (
    pairwise_margin_ranking_loss,
    pairwise_rank_accuracy,
)


def test_pairwise_ranking_loss_is_zero_when_margin_is_satisfied():
    pred_i = torch.tensor([2.0, 0.0])
    pred_j = torch.tensor([0.0, 2.0])
    true_i = torch.tensor([3.0, 1.0])
    true_j = torch.tensor([1.0, 3.0])

    loss = pairwise_margin_ranking_loss(pred_i, pred_j, true_i, true_j, margin=0.1)

    assert loss.item() == 0.0


def test_pairwise_ranking_loss_zero_ties_preserves_backward_path():
    pred_i = torch.tensor([2.0, 0.0], requires_grad=True)
    pred_j = torch.tensor([1.0, 3.0], requires_grad=True)
    true_i = torch.tensor([5.0, 5.0])
    true_j = torch.tensor([5.0, 5.0])

    loss = pairwise_margin_ranking_loss(pred_i, pred_j, true_i, true_j, margin=0.1)

    assert loss.item() == 0.0
    loss.backward()
    assert pred_i.grad is not None
    assert pred_j.grad is not None


def test_pairwise_rank_accuracy_counts_correct_signs():
    pred_i = torch.tensor([2.0, 0.0, 1.0])
    pred_j = torch.tensor([0.0, 2.0, 1.0])
    true_i = torch.tensor([3.0, 1.0, 5.0])
    true_j = torch.tensor([1.0, 3.0, 5.0])

    acc = pairwise_rank_accuracy(pred_i, pred_j, true_i, true_j)

    assert acc == 1.0
