import torch


def pairwise_margin_ranking_loss(
    pred_i: torch.Tensor,
    pred_j: torch.Tensor,
    true_i: torch.Tensor,
    true_j: torch.Tensor,
    margin: float = 0.1,
) -> torch.Tensor:
    target = torch.sign(true_i - true_j)
    nonzero = target != 0
    if nonzero.sum() == 0:
        return pred_i.new_tensor(0.0)

    pred_diff = pred_i - pred_j
    per_pair = torch.clamp(-target * pred_diff + margin, min=0.0)
    return per_pair[nonzero].mean()


def pairwise_rank_accuracy(
    pred_i: torch.Tensor,
    pred_j: torch.Tensor,
    true_i: torch.Tensor,
    true_j: torch.Tensor,
) -> float:
    target = torch.sign(true_i - true_j)
    nonzero = target != 0
    if nonzero.sum() == 0:
        return 0.5

    pred_sign = torch.sign(pred_i - pred_j)
    correct = ((pred_sign == target) & nonzero).float().sum()
    return (correct / nonzero.float().sum()).item()
