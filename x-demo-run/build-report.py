#!/usr/bin/env python3
"""Builds a self-contained HTML demo-run report from a JSON description of the steps.

Usage: build-report.py <steps.json> <out.html>

Images are embedded in the file (base64); PNGs are re-encoded as JPEG when Pillow is present,
so the report opens anywhere and does not depend on the screenshot paths after the run.
The JSON shape is in SKILL.md, section "Run description and building the report".
Labels here are always English; text values come from the JSON in the report language
(its code in the optional "lang" key, default "en").
"""
import base64
import html
import io
import json
import sys
from pathlib import Path

STATUS = {
    "pass": ("✓", "passed", "pass"),
    "fail": ("✗", "failed", "fail"),
    "blocked": ("⚠", "not run", "blocked"),
}


def embed(path: str) -> str:
    raw = Path(path).read_bytes()
    try:
        from PIL import Image

        img = Image.open(io.BytesIO(raw))
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=82, optimize=True)
        raw, mime = buf.getvalue(), "image/jpeg"
    except Exception:
        mime = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(raw).decode()}"


def e(text) -> str:
    return html.escape(str(text or ""))


def figure(img: dict, cls: str = "", caption_html: str = "") -> str:
    cap_body = caption_html or e(img.get("caption"))
    cap = f"<figcaption>{cap_body}</figcaption>" if cap_body else ""
    return f'<figure class="{cls}"><img loading="lazy" src="{embed(img["path"])}" alt="{e(img.get("caption"))}">{cap}</figure>'


def step_card(step: dict) -> str:
    icon, label, cls = STATUS[step["status"]]
    before_shots = step.get("before_shots") or []
    if before_shots:
        was = "".join(figure(s, "was", f"<b>Before.</b> {e(s.get('caption'))}") for s in before_shots)
        now = "".join(figure(s, "now", f"<b>After.</b> {e(s.get('caption'))}") for s in step.get("shots", []))
        shots = f'<div class="pair">{was}{now}</div>'
    else:
        shots = "".join(figure(s) for s in step.get("shots", []))
    mockup = step.get("mockup") or {}
    mock_html = ""
    if mockup.get("path"):
        link = f' — <a href="{e(mockup["url"])}" target="_blank">open in Figma</a>' if mockup.get("url") else ""
        note = f'<br><span class="mocknote">{e(mockup["note"])}</span>' if mockup.get("note") else ""
        mock_html = figure({"path": mockup["path"], "caption": "Mockup"}, "mock", f"Mockup{link}{note}")
    elif mockup.get("url"):
        note = f' — {e(mockup["note"])}' if mockup.get("note") else ""
        mock_html = f'<p class="mocklink">Mockup: <a href="{e(mockup["url"])}" target="_blank">{e(mockup["url"])}</a>{note}</p>'

    rows = [f'<p class="action"><b>Action.</b> {e(step["action"])}</p>',
            f'<p class="expected"><b>Expected.</b> {e(step["expected"])}</p>']
    if step.get("look_at"):
        rows.append(f'<p class="look"><b>What to look at.</b> {e(step["look_at"])}</p>')
    if step.get("before"):
        rows.append(f'<p class="before"><i>Earlier: {e(step["before"])}</i></p>')
    for b in step.get("basis") or []:
        if b.get("missing"):
            link = f' <a href="{e(b["url"])}" target="_blank">{e(b["url"])}</a>' if b.get("url") else ""
            rows.append(f'<p class="basis missing"><b>Reason.</b> {e(b["missing"])}{link}</p>')
        else:
            basis_label = "Reason (follows from)" if b.get("inferred") else "Reason"
            rows.append(f'<p class="basis"><b>{basis_label}.</b> “{e(b["quote"])}” — <span class="src">{e(b["source"])}</span></p>')
    if step.get("before_actual"):
        rows.append(f'<p class="actual"><b>Actual before.</b> {e(step["before_actual"])}</p>')
    if step["status"] != "pass" and step.get("actual"):
        rows.append(f'<p class="actual"><b>Actual.</b> {e(step["actual"])}</p>')

    return f"""
<article class="step {cls}" id="step-{e(step['n'])}">
  <header><span class="badge {cls}">{icon} {label}</span><h3>Step {e(step['n'])}</h3></header>
  <div class="media">{shots}{mock_html}</div>
  <div class="text">{''.join(rows)}</div>
</article>"""


def build(data: dict) -> str:
    steps = [s for sec in data["sections"] for s in sec["steps"]]
    counts = {k: sum(1 for s in steps if s["status"] == k) for k in STATUS}
    problems = [s for s in steps if s["status"] != "pass"]
    problem_list = "".join(
        f'<li class="{s["status"]}"><a href="#step-{e(s["n"])}">Step {e(s["n"])}</a> — {e(s.get("actual") or s["expected"])}</li>'
        for s in problems
    ) or "<li class='pass'>All steps passed.</li>"

    logins = "".join(
        f"<tr><td>{e(l['who'])}</td><td><code>{e(l['email'])}</code></td><td>{e(l['role'])}</td></tr>"
        for l in data.get("logins", [])
    )
    data_list = "".join(f"<li>{e(d)}</li>" for d in data.get("data", []))
    sections = ""
    for sec in data["sections"]:
        meta = []
        if sec.get("who"):
            meta.append(f"User: {e(sec['who'])}")
        if sec.get("url"):
            meta.append(f'URL: <a href="{e(sec["url"])}" target="_blank">{e(sec["url"])}</a>')
        sections += f"<section><h2>{e(sec['title'])}</h2><p class='meta'>{' · '.join(meta)}</p>"
        sections += "".join(step_card(s) for s in sec["steps"]) + "</section>"
    tail = ""
    for key, title in (("not_checked", "Not checked"), ("leftover", "Left after the run")):
        if data.get(key):
            tail += f"<section><h2>{title}</h2><ul>{''.join(f'<li>{e(x)}</li>' for x in data[key])}</ul></section>"

    return f"""<!doctype html>
<html lang="{e(data.get('lang') or 'en')}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(data['title'])}</title>
<style>
:root{{--bg:#f6f7f9;--card:#fff;--text:#1d2330;--muted:#5f6b7a;--line:#e3e6eb;--pass:#1f9d55;--fail:#d64545;--blocked:#c98a00;--link:#2563eb}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#12151b;--card:#1b2029;--text:#e6e9ef;--muted:#9aa5b4;--line:#2a313d;--link:#7aa7ff}}}}
body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}}
main{{max-width:1180px;margin:0 auto;padding:24px 16px 64px}}
a{{color:var(--link)}} code{{font-size:13px}}
h1{{font-size:24px;margin:0 0 4px}} h2{{font-size:19px;margin:32px 0 4px}} h3{{margin:0;font-size:16px}}
.sub,.meta{{color:var(--muted);margin:0 0 12px}}
.summary{{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0}}
.pill{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px 14px;font-weight:600}}
.pill.pass{{color:var(--pass)}} .pill.fail{{color:var(--fail)}} .pill.blocked{{color:var(--blocked)}}
.box{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px 16px;margin:12px 0}}
.box li.fail a,.box li.blocked a{{font-weight:600}}
table{{border-collapse:collapse;width:100%}} td{{border-top:1px solid var(--line);padding:6px 8px;vertical-align:top}}
.step{{background:var(--card);border:1px solid var(--line);border-left:5px solid var(--pass);border-radius:12px;padding:14px 16px;margin:14px 0}}
.step.fail{{border-left-color:var(--fail)}} .step.blocked{{border-left-color:var(--blocked)}}
.step header{{display:flex;align-items:center;gap:10px;margin-bottom:10px}}
.badge{{font-size:13px;font-weight:700;padding:2px 10px;border-radius:999px;color:#fff;background:var(--pass)}}
.badge.fail{{background:var(--fail)}} .badge.blocked{{background:var(--blocked)}}
.media{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:12px}}
figure{{margin:0}} figure img{{width:100%;border:1px solid var(--line);border-radius:8px;cursor:zoom-in;display:block}}
figure.mock img{{outline:2px dashed var(--muted);outline-offset:-2px}}
.pair{{grid-column:1/-1;display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:12px}}
figure.was img{{border-color:#9aa5b4;filter:saturate(.85)}}
figcaption{{color:var(--muted);font-size:13px;margin-top:4px}}
.text p{{margin:6px 0}} .look{{background:rgba(214,69,69,.08);border-radius:6px;padding:4px 8px}}
.before{{color:var(--muted)}}
.basis{{border-left:3px solid var(--link);padding:2px 8px}} .basis .src{{color:var(--muted);white-space:nowrap}}
.basis.missing{{border-left-color:var(--blocked)}} .actual{{color:var(--fail)}} .mocknote{{color:var(--muted);font-size:13px}}
#zoom{{position:fixed;inset:0;background:rgba(0,0,0,.85);display:none;align-items:center;justify-content:center;cursor:zoom-out;z-index:9}}
#zoom img{{max-width:96vw;max-height:94vh}}
.filter{{margin-left:auto}} body.only-problems .step.pass{{display:none}}
</style></head><body><main>
<h1>{e(data['title'])}</h1>
<p class="sub">{e(data.get('task'))}<br>{e(data.get('stand'))} · {e(data.get('branch'))} · {e(data.get('date'))}{f"<br>{e(data['before_note'])}" if data.get('before_note') else ''}</p>
<div class="summary">
  <span class="pill pass">✓ {counts['pass']}</span><span class="pill fail">✗ {counts['fail']}</span>
  <span class="pill blocked">⚠ {counts['blocked']}</span>
  <label class="pill filter"><input type="checkbox" onchange="document.body.classList.toggle('only-problems',this.checked)"> only problems</label>
</div>
<div class="box"><b>Summary</b><ul>{problem_list}</ul></div>
<div class="box"><b>Logins</b>{f'<p class="meta">{e(data["password_note"])}</p>' if data.get('password_note') else ''}<table>{logins}</table></div>
<div class="box"><b>Data</b><ul>{data_list}</ul></div>
{sections}{tail}
</main>
<div id="zoom" onclick="this.style.display='none'"><img alt=""></div>
<script>
document.querySelectorAll('figure img').forEach(function(i){{i.addEventListener('click',function(){{
  var z=document.getElementById('zoom');z.querySelector('img').src=i.src;z.style.display='flex';}});}});
</script>
</body></html>"""


def main() -> None:
    src, out = sys.argv[1], sys.argv[2]
    data = json.loads(Path(src).read_text(encoding="utf-8"))
    Path(out).write_text(build(data), encoding="utf-8")
    steps = [s for sec in data["sections"] for s in sec["steps"]]
    print(f"{out}: {Path(out).stat().st_size // 1024} KB, {len(steps)} steps, "
          + ", ".join(f"{STATUS[k][0]} {sum(1 for s in steps if s['status'] == k)}" for k in STATUS))


if __name__ == "__main__":
    main()
