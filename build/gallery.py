"""Build a gallery of REAL profile READMEs so the look can be picked, not described.

Pulls the curated awesome-profile list, fetches each person's profile README,
extracts the images it actually renders, and lays them out as a contact sheet
with a link to the live profile.
"""
import os
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "preview", "gallery.html")

# Image hosts that are decoration rather than design: shields/badges and the
# stat-card services. Showing 40 badge rows teaches nothing.
SKIP = re.compile(
    r"(shields\.io|badgen|forthebadge|badge\.fury|visitor-badge|komarev\.com|"
    r"profile-counter|badges\.pufler|hits\.dwyl|starchart|activity-graph|"
    r"github-readme-stats|github-profile-trophy|streak-stats|spotify|"
    r"lastfm|wakatime|leetcode|holopin|buymeacoffee|ko-fi|paypal|"
    r"flaticon|slackmojis|simple-icons|devicon|jsdelivr|unpkg|"
    r"gpvc\.|badge\.svg|/badges?/|icons?/|logos?/|emoji)", re.I)

MIN_BYTES = 24_000        # a designed banner is heavy; an icon is not

IMG = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']|!\[[^\]]*\]\(([^)\s]+)', re.I)


BRANCHES = ("main", "master")
UA = {"User-Agent": "Mozilla/5.0 (profile-gallery)"}


def fetch(url, timeout=20):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "replace"), r.url
    except Exception:
        return None, None


def profile_readme(user):
    """Raw HTTP, not the gh CLI: subprocess startup here costs ~6s a call,
    which turned 70 profiles into a seven-minute run that timed out."""
    for branch in BRANCHES:
        for name in ("README.md", "readme.md"):
            body, _ = fetch("https://raw.githubusercontent.com/%s/%s/%s/%s"
                            % (user, user, branch, name))
            if body:
                return body, branch
    return None, None


BLOB = re.compile(r"^https://github\.com/([^/]+)/([^/]+)/blob/(.+)$", re.I)


def head_size(url):
    """Content-length via HEAD. Used to drop icons and keep real artwork."""
    try:
        req = urllib.request.Request(url, headers=UA, method="HEAD")
        with urllib.request.urlopen(req, timeout=12) as r:
            return int(r.headers.get("Content-Length") or 0)
    except Exception:
        return 0


def absolutize(url, user, branch):
    url = url.strip()
    m = BLOB.match(url)
    if m:
        # a blob link renders the HTML page, not the image
        url = "https://raw.githubusercontent.com/%s/%s/%s" % (m.group(1), m.group(2), m.group(3))
        return url.split("?")[0]
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("http"):
        return url
    return ("https://raw.githubusercontent.com/%s/%s/%s/%s"
            % (user, user, branch, url.lstrip("./")))


def images_for(user):
    md, branch = profile_readme(user)
    if not md:
        return None
    cands, seen = [], set()
    for m in IMG.finditer(md):
        u = m.group(1) or m.group(2)
        if not u or SKIP.search(u):
            continue
        u = absolutize(u, user, branch)
        if u in seen:
            continue
        seen.add(u)
        cands.append(u)
        if len(cands) >= 8:
            break

    keep = []
    for u in cands:
        if head_size(u) >= MIN_BYTES:
            keep.append(u)
        if len(keep) >= 2:
            break
    if not keep:
        return None
    return {"user": user, "images": keep, "chars": len(md)}


def main(users):
    with ThreadPoolExecutor(max_workers=12) as pool:
        rows = [r for r in pool.map(images_for, users) if r and r["images"]]

    cards = []
    for r in rows:
        imgs = "".join(
            '<img loading="lazy" src="%s" alt="">' % u for u in r["images"])
        cards.append(
            '<figure><figcaption><a href="https://github.com/%s" target="_blank">%s</a>'
            '<span>%s</span></figcaption><div class="shot">%s</div></figure>'
            % (r["user"], r["user"], "%d chars" % r["chars"], imgs))

    html = HTML % {"cards": "\n".join(cards), "n": len(rows)}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote %s with %d profiles" % (os.path.relpath(OUT), len(rows)))


HTML = """<!doctype html>
<meta charset="utf-8"><title>Real profile READMEs</title>
<style>
 :root{color-scheme:dark}
 body{margin:0;background:#0d1117;color:#e6edf3;
      font:15px/1.5 -apple-system,"Segoe UI",system-ui,sans-serif;padding:26px 0 100px}
 .col{max-width:1180px;margin:0 auto;padding:0 20px}
 h1{font-size:21px;margin:0 0 4px;font-weight:600}
 .lede{color:#8b949e;font-size:13.5px;margin:0 0 24px}
 .grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}
 figure{margin:0;border:1px solid #30363d;border-radius:8px;overflow:hidden;background:#161b22}
 figcaption{display:flex;align-items:baseline;gap:10px;padding:9px 13px;border-bottom:1px solid #30363d;
            font:12px ui-monospace,Consolas,monospace}
 figcaption a{color:#4493f8;text-decoration:none;font-weight:700}
 figcaption span{color:#6e7681;margin-left:auto}
 .shot{background:#fff;padding:10px;display:flex;flex-direction:column;gap:8px;
       max-height:340px;overflow:hidden}
 .shot img{max-width:100%%;display:block}
</style>
<div class="col">
 <h1>%(n)d real profile READMEs</h1>
 <p class="lede">Pulled live from each person's own repo. Badge rows and stat-card
    services are filtered out, so this is the designed part only. Click a name to open
    the real profile. Tell me which numbers you like.</p>
 <div class="grid">
%(cards)s
 </div>
</div>
"""


if __name__ == "__main__":
    main(sys.argv[1:])
