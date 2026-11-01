| Method (test, n=340) | Macro-F1 | Accuracy | Coverage | Acc. on answered | Off by 2+ levels | Under-called by 2+ |
|---|---|---|---|---|---|---|
| Baseline CLIP probe (official split) | 0.619 | 0.621 | 1.00 | 0.621 | 29 | 13 |
| Baseline CLIP probe (grouped split) | 0.580 | 0.591 | 1.00 | 0.591 | 35 | 19 |
| Spark zero-shot | 0.482 | 0.485 | 0.82 | 0.594 | 2 | 0 |
| Spark few-shot (1 read) | 0.603 | 0.541 | 0.83 | 0.655 | 5 | 3 |
| Spark few-shot x3 (majority) | 0.589 | 0.553 | 0.84 | 0.655 | 4 | 2 |
| Hybrid (baseline + Spark) | 0.647 | 0.641 | 1.00 | 0.641 | 17 | 9 |
| Learned stack (secondary, fit on val) | 0.658 | 0.659 | 1.00 | 0.659 | 17 | 7 |
