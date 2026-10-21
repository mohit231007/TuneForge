import torch

from tuneforge.modeling import parameter_summary


def test_parameter_summary_counts_trainable_fraction():
    model = torch.nn.Sequential(
        torch.nn.Linear(2, 2),
        torch.nn.Linear(2, 1),
    )

    for parameter in model[1].parameters():
        parameter.requires_grad = False

    summary = parameter_summary(model)

    assert summary["total_parameters"] == 9
    assert summary["trainable_parameters"] == 6
    assert 0 < summary["trainable_percentage"] < 100
