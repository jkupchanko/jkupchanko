"""Fetch the real numbers the stats strip renders, into build/data/stats.json.

Self-hosted on purpose. The popular hosted widgets are third-party services:
github-readme-stats was returning DEPLOYMENT_PAUSED and
github-readme-activity-graph Payment required on 2026-09-12, and a lapsed
service renders as a broken image on someone's profile.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

LOGIN = os.environ.get("PROFILE_LOGIN", "jkupchanko")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "stats.json")


def gh(*args):
    env = dict(os.environ)
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        env["GH_TOKEN"] = token
    res = subprocess.run(["gh", *args], capture_output=True, text=True, env=env)
    if res.returncode != 0:
        raise RuntimeError("gh %s failed: %s" % (" ".join(args), res.stderr.strip()))
    return json.loads(res.stdout) if res.stdout.strip() else None


YEAR_Q = """
query($login:String!,$from:DateTime!,$to:DateTime!){
  user(login:$login){
    contributionsCollection(from:$from,to:$to){
      contributionCalendar{
        totalContributions
        weeks{ contributionDays{ date contributionCount } }
      }
    }
  }
}
"""


def main():
    profile = gh("api", "users/%s" % LOGIN)
    created = datetime.fromisoformat(profile["created_at"].replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)

    total, days = 0, []
    for year in range(created.year, now.year + 1):
        data = gh("api", "graphql", "-f", "query=" + YEAR_Q, "-f", "login=" + LOGIN,
                  "-f", "from=%d-01-01T00:00:00Z" % year, "-f", "to=%d-12-31T23:59:59Z" % year)
        cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
        total += cal["totalContributions"]
        days.extend(d for w in cal["weeks"] for d in w["contributionDays"])

    days.sort(key=lambda d: d["date"])
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        longest = max(longest, run)

    try:
        repos = gh("api", "user/repos?per_page=100&affiliation=owner")
    except RuntimeError:
        repos = None
    if not repos:
        repos = gh("api", "users/%s/repos?per_page=100" % LOGIN)
    owned = [r for r in repos if not r.get("fork")]

    payload = {
        "contributions": total,
        "repositories": len(owned),
        "longest_streak": longest,
        "since": created.year,
        "active_days": sum(1 for d in days if d["contributionCount"] > 0),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(json.dumps(payload))
    print("wrote", os.path.relpath(OUT))


if __name__ == "__main__":
    sys.exit(main())
