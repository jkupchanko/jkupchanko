"""Pull the live numbers the panels render, into build/data/live.json.

Run by the scheduled workflow. Uses GH_TOKEN if present (the Action passes
one); falls back to the `gh` CLI locally.

Language mix is deliberately NOT raw byte counts. Two old repos here carry
~10 MB of vendored Move and generated HTML between them, which would render
a "Move developer" chart for someone who writes Python and TypeScript. Each
repo is reduced to its language *shares*, then weighted by how recently it
was pushed, so the chart answers "what is he working in" rather than "which
directory is biggest".
"""
import json
import math
import os
import subprocess
import sys
from datetime import datetime, timezone

LOGIN = os.environ.get("PROFILE_LOGIN", "jkupchanko")
HALF_LIFE_DAYS = 270.0          # a repo's weight halves every ~9 months
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "live.json")

# Generated or vendored output that says nothing about what someone writes.
IGNORE_LANGS = {"HTML", "CSS", "SCSS", "Makefile", "Dockerfile"}


def gh(*args):
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    env = dict(os.environ)
    if token:
        env["GH_TOKEN"] = token
    res = subprocess.run(["gh", *args], capture_output=True, text=True, env=env)
    if res.returncode != 0:
        raise RuntimeError("gh %s failed: %s" % (" ".join(args), res.stderr.strip()))
    return json.loads(res.stdout) if res.stdout.strip() else None


_repos_cache = []


def owned_repos():
    """Every non-fork repo we can see, private included when the token allows.

    A workflow's default GITHUB_TOKEN cannot list a user's private repos, so
    fall back to the public listing rather than failing the run. Set a
    PROFILE_TOKEN secret (a PAT with repo + read:user) to include private work.
    """
    if _repos_cache:
        return _repos_cache
    try:
        repos = gh("api", "user/repos?per_page=100&affiliation=owner")
    except RuntimeError:
        repos = None
    if not repos:
        repos = gh("api", "users/%s/repos?per_page=100" % LOGIN)
    _repos_cache.extend(r for r in (repos or []) if not r.get("fork"))
    return _repos_cache


CALENDAR_Q = """
query($login:String!){
  user(login:$login){
    contributionsCollection{
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      restrictedContributionsCount
      contributionCalendar{
        totalContributions
        weeks{ contributionDays{ date contributionCount } }
      }
    }
  }
}
"""


def calendar():
    data = gh("api", "graphql", "-f", "query=" + CALENDAR_Q, "-f", "login=" + LOGIN)
    cc = data["data"]["user"]["contributionsCollection"]
    cal = cc["contributionCalendar"]
    weeks = [[d["contributionCount"] for d in w["contributionDays"]] for w in cal["weeks"]]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]

    # longest and current run of days with at least one contribution
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        longest = max(longest, run)
    current = 0
    for d in reversed(days):
        if d["contributionCount"] == 0:
            break
        current += 1

    return {
        "weeks": weeks,
        "total": cal["totalContributions"],
        "commits": cc["totalCommitContributions"],
        "prs": cc["totalPullRequestContributions"],
        "issues": cc["totalIssueContributions"],
        "private": cc["restrictedContributionsCount"],
        "peak_day": max((d["contributionCount"] for d in days), default=0),
        "active_days": sum(1 for d in days if d["contributionCount"] > 0),
        "longest_streak": longest,
        "current_streak": current,
        "from": days[0]["date"] if days else None,
        "to": days[-1]["date"] if days else None,
    }


def languages():
    now = datetime.now(timezone.utc)

    scores, seen_repos = {}, 0
    for repo in owned_repos():
        if repo.get("archived"):
            continue
        try:
            langs = gh("api", "repos/%s/languages" % repo["full_name"])
        except RuntimeError:
            continue
        langs = {k: v for k, v in (langs or {}).items() if k not in IGNORE_LANGS}
        total = sum(langs.values())
        if not total:
            continue
        seen_repos += 1

        pushed = datetime.fromisoformat(repo["pushed_at"].replace("Z", "+00:00"))
        age_days = max(0.0, (now - pushed).total_seconds() / 86400.0)
        recency = 0.5 ** (age_days / HALF_LIFE_DAYS)
        # log-scaled so a big repo counts for more than a tiny one, but not 100x
        size = math.log10(1.0 + total / 1000.0)
        weight = recency * size

        for lang, byts in langs.items():
            scores[lang] = scores.get(lang, 0.0) + (byts / total) * weight

    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    grand = sum(v for _, v in ranked) or 1.0
    return {
        "repos_counted": seen_repos,
        "mix": [{"name": k, "share": round(v / grand, 5)} for k, v in ranked[:7]],
    }


def repos_summary():
    owned = owned_repos()
    return {
        "owned": len(owned),
        "public": sum(1 for r in owned if not r.get("private")),
        "stars": sum(r.get("stargazers_count", 0) for r in owned),
        "recent": [
            {"name": r["name"], "private": bool(r.get("private")),
             "pushed": r["pushed_at"][:10], "lang": r.get("language")}
            for r in sorted(owned, key=lambda r: r["pushed_at"], reverse=True)[:8]
        ],
    }


def main():
    payload = {
        "login": LOGIN,
        "calendar": calendar(),
        "languages": languages(),
        "repos": repos_summary(),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    cal, lang = payload["calendar"], payload["languages"]
    print("contributions %d over %d weeks (peak day %d, longest streak %d)"
          % (cal["total"], len(cal["weeks"]), cal["peak_day"], cal["longest_streak"]))
    print("languages from %d repos: %s" % (
        lang["repos_counted"],
        ", ".join("%s %.0f%%" % (m["name"], m["share"] * 100) for m in lang["mix"])))
    print("wrote", os.path.relpath(OUT))


if __name__ == "__main__":
    sys.exit(main())
