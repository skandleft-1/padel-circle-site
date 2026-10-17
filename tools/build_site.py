"""Generate padel-circle-site pages from the legal .txt sources."""
import html, re, sys, pathlib

SRC = pathlib.Path(r"C:\Users\skand\IdeaProjects\padel-circle")
OUT = pathlib.Path(r"C:\Users\skand\IdeaProjects\padel-circle-site")

CSS = """
:root{--bg:#f7f8fa;--card:#fff;--fg:#14213d;--muted:#5b6475;--accent:#1f9d55;--line:#e3e6ec}
@media (prefers-color-scheme:dark){:root{--bg:#0d1526;--card:#14203a;--fg:#e8edf6;--muted:#9aa6bd;--accent:#3ddc84;--line:#24324f}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
main{max-width:760px;margin:0 auto;padding:32px 16px 64px}
header.top{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:24px}
.brand{font-weight:700;color:var(--fg);text-decoration:none;font-size:1.1rem}
.brand span{color:var(--accent)}
nav a{color:var(--muted);text-decoration:none;margin-left:14px;font-size:.95rem}
nav a:hover{color:var(--accent)}
h1{font-size:1.9rem;line-height:1.2;margin:0 0 4px}
h2{font-size:1.15rem;margin:32px 0 8px}
.meta{color:var(--muted);margin:0 0 24px}
a{color:var(--accent)}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px 22px;margin:16px 0}
ul{padding-left:22px}
footer{margin-top:48px;padding-top:16px;border-top:1px solid var(--line);color:var(--muted);font-size:.9rem}
footer a{color:var(--muted)}
"""

def page(title, lang, body, alt=None):
    alt_link = f'<a href="{alt[0]}">{alt[1]}</a>' if alt else ""
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} · Padel Circle</title>
<style>{CSS}</style>
</head>
<body>
<main>
<header class="top">
  <a class="brand" href="./">Padel <span>Circle</span></a>
  <nav>{alt_link}<a href="privacy.html">Privacy</a><a href="terms.html">Terms</a><a href="delete-account.html">Delete account</a></nav>
</header>
{body}
<footer>Padel Circle · Athens, Greece · <a href="mailto:padel.circle.app1@gmail.com">padel.circle.app1@gmail.com</a></footer>
</main>
</body>
</html>
"""

def linkify(s):
    s = html.escape(s)
    s = re.sub(r"(https://[^\s<]+[^\s<.,;)])", r'<a href="\1">\1</a>', s)
    s = re.sub(r"([\w.+-]+@[\w-]+\.[\w.]+\w)", r'<a href="mailto:\1">\1</a>', s)
    return s

def from_txt(name):
    lines = (SRC / name).read_text(encoding="utf-8").splitlines()
    assert lines[0].strip() == "PADEL CIRCLE", name
    title = {"PRIVACY POLICY": "Privacy Policy", "TERMS OF SERVICE": "Terms of Service",
             "ΠΟΛΙΤΙΚΗ ΑΠΟΡΡΗΤΟΥ": "Πολιτική Απορρήτου", "ΟΡΟΙ ΧΡΗΣΗΣ": "Όροι Χρήσης"}[lines[1].strip()]
    blocks, cur = [], []
    for ln in lines[2:]:
        if ln.strip():
            cur.append(ln.strip())
        elif cur:
            blocks.append(cur); cur = []
    if cur: blocks.append(cur)
    out = [f"<h1>{html.escape(title)}</h1>"]
    for b in blocks:
        first = b[0]
        if re.match(r"^\d+\.\s", first):
            out.append(f"<h2>{html.escape(first)}</h2>")
            b = b[1:]
            if not b: continue
        if len(blocks) and b is blocks[0] and re.match(r"^(Last updated|Τελευταία)", first):
            out.append(f'<p class="meta">{html.escape(first)}</p>')
            continue
        out.append("<p>" + "<br>".join(linkify(x) for x in b) + "</p>")
    return title, "\n".join(out)

for src, dst, lang, alt in [
    ("Padel_Circle_Privacy_EN.txt", "privacy.html", "en", ("privacy-gr.html", "Ελληνικά")),
    ("Padel_Circle_Privacy_GR.txt", "privacy-gr.html", "el", ("privacy.html", "English")),
    ("Padel_Circle_Terms_EN.txt", "terms.html", "en", ("terms-gr.html", "Ελληνικά")),
    ("Padel_Circle_Terms_GR.txt", "terms-gr.html", "el", ("terms.html", "English")),
]:
    t, body = from_txt(src)
    (OUT / dst).write_text(page(t, lang, body, alt), encoding="utf-8")

for name in ("index", "delete-account"):
    body = (pathlib.Path(__file__).parent / f"{name}.body.html").read_text(encoding="utf-8")
    title = "Padel Circle" if name == "index" else "Delete your account"
    (OUT / f"{name}.html").write_text(page(title, "en", body), encoding="utf-8")

print("built", sorted(p.name for p in OUT.glob("*.html")))
