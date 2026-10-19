import pytest
from sklearn.metrics import roc_auc_score

from challenges.loader import load_challenge


def _auc(scores, labels):
    return load_challenge("04_roc_auc").roc_auc(scores, labels)


def test_perfect_reversed_and_tied_rankings():
    assert _auc([0.1, 0.2, 0.8, 0.9], [0, 0, 1, 1]) == pytest.approx(1.0)
    assert _auc([0.9, 0.8, 0.2, 0.1], [0, 0, 1, 1]) == pytest.approx(0.0)
    assert _auc([0.5, 0.5], [0, 1]) == pytest.approx(0.5)


def test_matches_sklearn_when_scores_tie():
    scores = [0.1, 0.4, 0.4, 0.8, 0.3, 0.8]
    labels = [0, 1, 0, 1, 0, 0]
    assert _auc(scores, labels) == pytest.approx(roc_auc_score(labels, scores))


def test_rejects_bad_inputs():
    with pytest.raises(ValueError):
        _auc([0.2, 0.8], [0])
    with pytest.raises(ValueError):
        _auc([0.2, 0.8], [1, 1])
    with pytest.raises(ValueError):
        _auc([0.2], [2])
