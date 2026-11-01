# flood-triage

**Triage for citizen flood reports, built on Meta's open-weight Muse Spark Open.**
A citizen sends a street photo during urban flooding. flood-triage reads the water level against the vehicles in it (tyre, chassis, window: levels L0–L4) or says **can't tell**, shows the evidence it used, checks the citizen's own depth guess against the photo, flags likely duplicates, ranks the queue worst-first and drafts a short note for the ward officer.

It is decision support for the people who already run civic flood portals (for example the Gurugram MCG portal launched in June 2026, which asks citizens for a photo and a self-estimated depth). It does **not** measure depth in centimetres, plan routes, or issue warnings.

![architecture](docs/architecture.png)

## Results (STURM-FloodDepth test split, 340 crops, scored once)

{{TEST_TABLE}}

{{RESULTS_NOTES}}

![summary](results/charts/test_summary.png)

### Ablation (validation split, where every choice was made)

{{ABLATION_TABLE}}

### Robustness on real Indian monsoon photos
Qualitative only (no labels): 20 Wikimedia Commons street photos from Chennai, Mumbai, Kerala and Hyderabad floods. See [docs/robustness.md](docs/robustness.md) (licences and authors per photo; images not redistributed).

## Limitations and failure cases
{{LIMITATIONS}}

## Responsible use
- Output is a **triage hint for a human officer**, not a measurement, warning or instruction to the public.
- Levels are relative to vehicle parts; vehicle heights vary (two-wheelers, buses, SUVs).
- "Can't tell" is a feature: blurry, dark or vehicle-less photos go to a person instead of getting a guess.
- Demo locations, times and citizen estimates are synthetic. Do not use real citizens' photos or locations without consent; strip EXIF before storing.
- Model calls go to Baseten (zero data retention by default per Baseten); the open weights can also be self-hosted for a city that cannot send photos to a third party.

## How to run
```bash
pip install -r requirements.txt
bash scripts/download_data.sh             # dataset from Zenodo (not redistributed here)
export BASETEN_API_KEY=...                # Baseten Model API key
python scripts/run_spark.py --split test --prompt fewshot --samples 3 --out results/raw/spark_fewshot_test.jsonl
python scripts/embed.py --backbone clip && python scripts/baseline.py --backbone clip
python scripts/final_eval.py && python scripts/make_charts.py
python app.py                             # demo UI on http://localhost:7860
pytest -q                                 # parser + metric tests
```

## What I built during the hackathon (31 Oct – 4 Nov 2026)
Everything in this repository: the Spark client and prompts, the answer parser, the few-shot + self-consistency classifier, the CLIP linear-probe baseline, the hybrid decision rule, the evaluation and leakage analysis, the triage agent (self-report check, duplicate flags, worst-first ranking, ward note), the evidence overlay, the Gradio app, charts, tests and the demo video. No code predates the hackathon.

## Third-party
- **Model:** Muse Spark Open (Meta, open weights, Muse Model License), served by Baseten Model APIs (`meta-models/muse-spark-open-1026`).
- **Dataset:** STURM-FloodDepth Flooded Cars, N. Notarangelo / WEO, Zenodo doi:10.5281/zenodo.14833532, CC BY 4.0; derived from the flooded vehicle dataset of Wan et al. 2024 (github.com/ywszxdd/original_dataset, *Automatic detection of urban flood level with YOLOv8 using flooded vehicle dataset*, J. Hydrology). Level definitions from the STURM-FloodDepth paper.
- **Robustness photos:** Wikimedia Commons, authors and licences listed in docs/robustness.md.
- **SAM 3.1** (Meta): {{SAM_STATUS}}
- **Libraries:** OpenCLIP (CLIP ViT-B/16 OpenAI weights), PyTorch, scikit-learn, Gradio, Plotly, Pillow, matplotlib, edge-tts (video voiceover), ffmpeg.
- **Prior art (not novel claims):** STURM-FloodDepth ResNet50 classifier on the same data; FloodLlama (Mar 2026); GPT-4V flood-depth studies (2024). This project's contribution is the evidence + abstention + triage workflow around an open-weight model, and an honest comparison.

## License
MIT (code). Dataset and model under their own licences.
