"""flood-triage demo app (Gradio). Run: BASETEN_API_KEY=... python app.py
Tab 1: ward triage queue (worst first, map, duplicates, self-report check, ward-officer note drafted by Spark).
Tab 2: check one photo live with Muse Spark Open.
"""
import io, json, os
import gradio as gr
import plotly.graph_objects as go
from PIL import Image
from flood_triage import agent, overlay, prompts

DEMO = json.load(open("demo/demo_reports.json")) if os.path.exists("demo/demo_reports.json") else {"reports": []}
DATA_ROOT = os.environ.get("FLOOD_DATA", "data/upscaled_images")
COL = {0: "#2a9d8f", 1: "#8ab17d", 2: "#e9c46a", 3: "#f4a261", 4: "#e63946", None: "#6c757d"}

def badge(level, reason=None):
    if level is None:
        return (f"<div style='padding:14px;border-radius:12px;background:{COL[None]};color:white'>"
                f"<div style='font-size:28px;font-weight:700'>Can't tell</div><div>{reason or ''}</div>"
                "<div style='opacity:.8'>Sent to a human reviewer instead of guessing.</div></div>")
    return (f"<div style='padding:14px;border-radius:12px;background:{COL[level]};color:{'black' if level in (1,2) else 'white'}'>"
            f"<div style='font-size:28px;font-weight:700'>Level {level} · {prompts.LEVEL_NAMES[level]}</div>"
            f"<div>{prompts.LEVELS[level]}</div><div style='opacity:.8'>Relative to vehicle parts, not a depth in cm.</div></div>")

def evidence_md(a, check=None):
    votes = ", ".join("X" if v is None else str(v) for v in a["votes"])
    s = f"**Evidence:** {a.get('evidence') or '-'}  \n**Waterline touches:** {a.get('part') or '-'}  \n" \
        f"**Spark readings (3 samples):** {votes}  \n**Confidence:** {a.get('confidence') or '-'}"
    if check: s += f"  \n**Citizen's own estimate:** {check}"
    return s

def queue_rows():
    rs = sorted(DEMO["reports"], key=lambda r: (-(r["level"] if r["level"] is not None else 2.5), r["minute"]))
    return [[r["id"], r["place"], ("can't tell" if r["level"] is None else f"L{r['level']}"), r["self_report"], r["check"],
             r.get("dup_of") or "", f"{r['minute'] // 60:02d}:{r['minute'] % 60:02d}"] for r in rs]

def map_fig():
    fig = go.Figure()
    for r in DEMO["reports"]:
        fig.add_trace(go.Scattermap(lat=[r["lat"]], lon=[r["lon"]], mode="markers+text", text=[r["id"]], textposition="top right",
                                    marker=dict(size=12 + 4 * (r["level"] or 0), color=COL[r["level"]]), name=r["id"],
                                    hovertext=f"{r['place']}: {'can t tell' if r['level'] is None else 'L%d' % r['level']}"))
    if DEMO["reports"]:
        c = DEMO["reports"][0]
        fig.update_layout(map=dict(style="open-street-map", center=dict(lat=c["lat"], lon=c["lon"]), zoom=12.3))
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=False, height=380)
    return fig

def show_report(evt: gr.SelectData):
    rid = evt.row_value[0]; r = next(x for x in DEMO["reports"] if x["id"] == rid)
    b = open(os.path.join(DATA_ROOT, r["path"]), "rb").read()
    img = overlay.draw(b, r.get("loc") or {})
    a = {"votes": r["votes"], "evidence": r["evidence"], "part": r["part"], "confidence": r["confidence"]}
    return img, badge(r["level"], r.get("reason")), evidence_md(a, r["check"])

def draft_note():
    reps = []
    for r in sorted(DEMO["reports"], key=lambda r: (-(r["level"] if r["level"] is not None else 2.5), r["minute"])):
        reps.append({**r, "assessment": agent.Assessment(level=r["level"], votes=r["votes"], confidence=r["confidence"],
                                                           part=r["part"], evidence=r["evidence"], reason=r.get("reason"))})
    note, _ = agent.ward_note(reps, ward=DEMO.get("ward", "Demo ward"))
    return note + "\n\n(Draft by Muse Spark Open from the reports above. Review before sending.)"

def check_photo(img, self_report):
    if img is None:
        return None, "", "Upload a photo first."
    buf = io.BytesIO(); img.convert("RGB").save(buf, "JPEG", quality=90); b = buf.getvalue()
    a = agent.assess(b)
    loc = overlay.locate(b) if a.level is not None else {}
    chk = agent.self_report_check(self_report, a.level) if self_report else None
    return overlay.draw(b, loc), badge(a.level, a.reason), evidence_md(a.__dict__, chk)

with gr.Blocks(title="flood-triage") as demo:
    gr.Markdown("# flood-triage\nTriage for citizen flood reports with **Muse Spark Open** (Meta, open weights). "
                "Each photo gets a flood level relative to vehicle parts (L0-L4) or *can't tell*, with evidence. "
                "Decision support for a human ward officer: no depths in cm, no routes, no public warnings.")
    with gr.Tab("Ward triage queue"):
        gr.Markdown("Demo reports: dataset photos (STURM-FloodDepth, CC BY 4.0) with **synthetic** locations, times and citizen estimates.")
        with gr.Row():
            with gr.Column(scale=3):
                tbl = gr.Dataframe(queue_rows(), headers=["Report", "Place (synthetic)", "Level", "Citizen said", "Check", "Duplicate of", "Time"],
                                   interactive=False, wrap=True)
            with gr.Column(scale=2):
                gr.Plot(map_fig())
        with gr.Row():
            img_o = gr.Image(label="Photo + model-described waterline (red) and vehicle (blue)", height=320)
            with gr.Column():
                badge_o = gr.HTML(); ev_o = gr.Markdown()
        tbl.select(show_report, None, [img_o, badge_o, ev_o])
        btn = gr.Button("Draft note for ward officer (Spark)", variant="primary")
        note = gr.Textbox(label="Draft note", lines=8)
        btn.click(draft_note, None, note)
    with gr.Tab("Check a photo"):
        with gr.Row():
            with gr.Column():
                up = gr.Image(type="pil", label="Street photo with a vehicle")
                sr = gr.Dropdown(list(agent.SELF_REPORT_LEVELS), label="Citizen's own estimate (optional)")
                go_b = gr.Button("Assess", variant="primary")
                ex_paths = [os.path.join(DATA_ROOT, r["path"]) for r in DEMO["reports"][:4] if os.path.exists(os.path.join(DATA_ROOT, r["path"]))]
                if ex_paths: gr.Examples(ex_paths, up)
            with gr.Column():
                out_img = gr.Image(label="Evidence"); out_b = gr.HTML(); out_md = gr.Markdown()
        go_b.click(check_photo, [up, sr], [out_img, out_b, out_md])
    with gr.Tab("How it works"):
        gr.Markdown(open("docs/how_it_works.md").read() if os.path.exists("docs/how_it_works.md") else "See README.")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 7860)), theme=gr.themes.Soft())
