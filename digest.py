import os, json, datetime, pathlib, html
import urllib.request

API_KEY = os.environ["ANTHROPIC_API_KEY"]

PROMPT = """Create a morning digest with two sections. Today's date is {today}.

Section 1 — Positive News (3 articles): Find 3 positive news articles published within the last 24-48 hours, one each from: (a) Arizona/Phoenix-area local news, (b) US national news, (c) world news. Each should center women, minorities, the LGBTQIA+ community, animals, or children, showcasing themes like determination, intellectual achievement, athleticism, kindness, or success. Exclude any story that centers a cisgender, white, heterosexual male as the main subject. For each: a 1-sentence summary, the source name, and the URL.

Section 2 — Personal Care (3 suggestions): Give 3 suggestions completable in 15 minutes or less, drawn from a mix of: mental or physical health, parenting, strengthening a relationship with a spouse, culture, science, gratitude, happiness, or philanthropy (secular only, no religious content). Vary the categories — do not use the same three categories every day.

Reader context: 50-year-old Asian-American woman, senior manager at a global medtech company, pursuing a master's in AI for Business. INTJ. Prefers concise, logically sequenced writing. Appreciates a clever metaphor and dry wit.

Search the web to find genuinely current articles. Do not fabricate URLs — only cite links you actually retrieved.

Output clean Markdown. Use ## for the two section headers. No preamble, no sign-off."""

def call_claude(prompt):
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        method="POST",
        headers={
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        data=json.dumps({
            "model": "claude-sonnet-4-6",
            "max_tokens": 3000,
            "messages": [{"role": "user", "content": prompt}],
            "tools": [{
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 12
            }],
        }).encode(),
    )
    with urllib.request.urlopen(req) as r:
        data = json.loads(r.read())
    return "".join(
        b["text"] for b in data["content"] if b.get("type") == "text"
    ).strip()

def to_html(md, today):
    body = html.escape(md)
    # minimal markdown -> html
    lines = []
    for ln in body.split("\n"):
        s = ln.strip()
        if s.startswith("## "):
            lines.append(f"<h2>{s[3:]}</h2>")
        elif s.startswith("# "):
            lines.append(f"<h2>{s[2:]}</h2>")
        elif s:
            lines.append(f"<p>{s}</p>")
    return TEMPLATE.format(today=today, content="\n".join(lines))

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Morning Digest</title>
<style>
  body {{ font-family: Georgia, serif; max-width: 640px; margin: 0 auto;
         padding: 2rem 1.25rem 4rem; line-height: 1.65; color: #1a1a1a;
         background: #fbfaf8; }}
  .date {{ font-family: -apple-system, sans-serif; font-size: .8rem;
           letter-spacing: .12em; text-transform: uppercase; color: #8a8378; }}
  h1 {{ font-size: 1.9rem; margin: .2rem 0 2rem; }}
  h2 {{ font-size: 1.15rem; margin: 2.5rem 0 .75rem;
        padding-bottom: .4rem; border-bottom: 1px solid #e3ded5; }}
  p {{ margin: .6rem 0; }}
  a {{ color: #7a5c2e; }}
</style>
</head>
<body>
<div class="date">{today}</div>
<h1>Morning Digest</h1>
{content}
</body>
</html>"""

if __name__ == "__main__":
    today = datetime.date.today().strftime("%A, %B %-d, %Y")
    md = call_claude(PROMPT.format(today=today))
    pathlib.Path("index.html").write_text(to_html(md, today), encoding="utf-8")
    print("wrote index.html")
