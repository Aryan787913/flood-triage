"""Minimal OpenAI-compatible client for Muse Spark Open on Baseten (stdlib only)."""
import base64, json, os, time, urllib.request

BASE_URL = os.environ.get("SPARK_BASE_URL", "https://inference.baseten.co/v1")
MODEL = os.environ.get("SPARK_MODEL", "meta-models/muse-spark-open-1026")


def _headers():
    h = {"Content-Type": "application/json"}
    key = os.environ.get("BASETEN_API_KEY")
    if key:
        h["Authorization"] = f"Bearer {key}"
    return h


def image_part(path_or_bytes, mime="image/jpeg"):
    b = path_or_bytes if isinstance(path_or_bytes, (bytes, bytearray)) else open(path_or_bytes, "rb").read()
    return {"type": "image_url", "image_url": {"url": f"data:{mime};base64," + base64.b64encode(b).decode()}}


def chat(messages, max_tokens=4000, temperature=None, retries=3, timeout=120):
    """Return dict(content, reasoning_tokens?, usage, latency_s). Spark always reasons: keep max_tokens >= 4000."""
    body = {"model": MODEL, "max_tokens": max_tokens, "messages": messages}
    if temperature is not None:
        body["temperature"] = temperature
    last = None
    for i in range(retries):
        t0 = time.time()
        try:
            req = urllib.request.Request(BASE_URL + "/chat/completions", json.dumps(body).encode(), _headers())
            d = json.load(urllib.request.urlopen(req, timeout=timeout))
            msg = d["choices"][0]["message"]
            return {"content": (msg.get("content") or "").strip(), "usage": d.get("usage", {}),
                    "finish_reason": d["choices"][0].get("finish_reason"), "latency_s": round(time.time() - t0, 2)}
        except Exception as e:  # network / 429 / 5xx
            last = e
            time.sleep(2 * (i + 1) ** 2)
    return {"content": "", "error": str(last)[:300], "usage": {}, "latency_s": None}


def classify(image, prompt, **kw):
    return chat([{"role": "user", "content": [{"type": "text", "text": prompt}, image_part(image)]}], **kw)
