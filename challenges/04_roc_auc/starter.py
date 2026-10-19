# Complete the functions below. Do not change the signatures.


def roc_auc(scores: list[float], labels: list[int]) -> float:
    """ROC AUC from scores and binary labels."""
    # The model ranks cells. ROC AUC is the probability that a random
    # presence gets a higher score than a random background point. It is not
    # accuracy, and it does not need a threshold.
    #
    # Labels are 1 for presence and 0 for background.
    #
    # Steps:
    # - Rank the points by score.
    # - Use average ranks when several points share a score. That matches
    #   the trapezoidal ROC curve.
    # - Turn those ranks into the area under the curve.
    #
    # Edge cases:
    # - A perfect ranking scores 1. roc_auc([0.1, 0.2, 0.8, 0.9], [0, 0, 1, 1])
    #   is 1.0.
    # - The reversed ranking scores 0.
    # - A tie scores 0.5. roc_auc([0.5, 0.5], [0, 1]) is 0.5.
    # - Raise ValueError when the sequences differ in length, when either
    #   class is missing, or when a label is not 0 or 1.
    #
    # Return value: the ROC AUC as a float.
    raise NotImplementedError
