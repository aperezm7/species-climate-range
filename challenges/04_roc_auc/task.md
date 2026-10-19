# 04 — ROC AUC

The model ranks cells. ROC AUC is the probability that a random presence gets a higher score than a random background point. It is not accuracy, and it does not need a threshold.

Implement `roc_auc(scores, labels)`.

Labels are `1` for presence and `0` for background. A perfect ranking scores 1. The reversed ranking scores 0. A tie scores 0.5. Use average ranks when several points share a score; that matches the trapezoidal ROC curve.

Raise `ValueError` when the sequences differ in length, when either class is missing, or when a label is not 0 or 1.

```python
roc_auc([0.1, 0.2, 0.8, 0.9], [0, 0, 1, 1])  # 1.0
roc_auc([0.5, 0.5], [0, 1])  # 0.5
```

```bash
pytest challenges/04_roc_auc
```
