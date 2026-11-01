| Step (val, n=335) | Macro-F1 | Coverage | Acc. on answered | Off by 2+ | Under-called by 2+ |
|---|---|---|---|---|---|
| Baseline: CLIP ViT-B/16 linear probe | 0.604 | 1.00 | 0.612 | 24 | 13 |
| Spark zero-shot (own level wording) | 0.548 | 0.83 | 0.619 | 5 | 3 |
| + structured prompt, official level definitions | 0.512 | 0.74 | 0.633 | 6 | 3 |
| + self-consistency x3 (structured) | 0.524 | 0.73 | 0.646 | 5 | 2 |
| Spark few-shot (structured + 5 reference crops) | 0.559 | 0.83 | 0.649 | 1 | 1 |
| + self-consistency x3 (few-shot) | 0.591 | 0.85 | 0.655 | 2 | 2 |
| Hybrid: Spark decides when baseline p < 0.70 | 0.665 | 1.00 | 0.660 | 11 | 5 |
