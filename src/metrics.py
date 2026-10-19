"""ROC AUC for presence (1) versus background (0)."""

from __future__ import annotations

import math


def roc_auc(scores: list[float], labels: list[int]) -> float:
    """Area under the ROC curve from scores and binary labels.

    This is the probability that a random presence outranks a random
    background point. Ties use the average rank, which matches the
    trapezoidal ROC. Both classes are required.
    """
    if len(scores) != len(labels):
        raise ValueError("scores and labels must have the same length")
    if len(scores) == 0:
        raise ValueError("scores and labels are empty")
    parsed_scores: list[float] = []
    parsed_labels: list[int] = []
    for score, label in zip(scores, labels):
        parsed_scores.append(_as_score(score))
        parsed_labels.append(_as_label(label))
    n_pos = sum(parsed_labels)
    n_neg = len(parsed_labels) - n_pos
    if n_pos == 0 or n_neg == 0:
        raise ValueError("both classes are required")
    order = sorted(range(len(parsed_scores)), key=lambda index: parsed_scores[index])
    ranks = [0.0] * len(parsed_scores)
    start = 0
    while start < len(order):
        end = start
        while (
            end + 1 < len(order)
            and parsed_scores[order[end + 1]] == parsed_scores[order[start]]
        ):
            end += 1
        average_rank = (start + 1 + end + 1) / 2
        for position in range(start, end + 1):
            ranks[order[position]] = average_rank
        start = end + 1
    sum_positive_ranks = sum(
        ranks[index] for index, label in enumerate(parsed_labels) if label == 1
    )
    auc = (sum_positive_ranks - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)
    return float(auc)


def _as_score(value: object) -> float:
    if isinstance(value, bool) or isinstance(value, str):
        raise ValueError("scores must be finite numbers")
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise ValueError("scores must be finite numbers") from exc
    if not math.isfinite(number):
        raise ValueError("scores must be finite numbers")
    return number


def _as_label(value: object) -> int:
    if isinstance(value, bool) or isinstance(value, str):
        raise ValueError("labels must be 0 or 1")
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise ValueError("labels must be 0 or 1") from exc
    if number not in (0.0, 1.0):
        raise ValueError("labels must be 0 or 1")
    return int(number)
