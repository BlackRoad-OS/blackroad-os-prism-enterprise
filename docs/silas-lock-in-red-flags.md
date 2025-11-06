# Silas Lock-In: AI Pitch Red-Flag Cheat Sheet

This quick reference consolidates the top warning signs when evaluating AI product pitches. Spotting three or more of these issues should trigger an automatic pass.

## Kill Signals

| # | Red Flag | Why It Kills | Quick Test |
|---|----------|--------------|------------|
| 1 | "100 agents / 60 PRs/week" but no merged code | Vapor execution | `git log --merges --since=30d` → fewer than 5 merges? Pass. |
| 2 | Hard-coded metrics (e.g., `ARR = 1_200_000` in JSON) | Fake traction | Search the repo for `1200000` or suspicious seed values such as `1000 signups`. |
| 3 | No CI or automated tests | Breaks at scale | `.github/workflows` empty? Pass. |
| 4 | "Patent pending" without a filing number | IP theater | Search USPTO filings; nothing returned? Pass. |
| 5 | Demo only works in local mock mode (`pnpm dev`) | Not shippable | Ask for a live URL with real users. |
| 6 | Claims LLM costs "<$1K/mo" without billing proof | Math doesn't check | $1K only covers ~3M GPT-4 tokens—nowhere near enough for "100 agents". |
| 7 | "Zero-trust" marketing but no OPA/Rego usage | Compliance cosplay | `grep -r "Rego" .` reveals only SSH keys or unrelated references. Pass. |
| 8 | Roadmap promises quantum/AGI in < 12 months | Science fiction | Ask for a working qubit simulator—expect silence. |
| 9 | "$4M savings" while employing 20 engineers | Back-of-napkin delusion | 20 engineers ≈ $3.2M fully loaded. Agents replace maybe 1% of that. |
|10 | GitHub shows 1 star and private forks only | No community | Stars + forks + issues < 10? Solo hallucination. Pass. |
|11 | Resume PR numbers don't exist in the repo | Straight-up lying | Search for the referenced PR (e.g., `#2845`); 404? Pass. |
|12 | "v0.1 next quarter" for the last 18 months | Eternal pre-product | Commit history shows < 1 commit per month? Dead project. |

## 30-Second Filter

1. **Live demo URL?** Must be reachable beyond `localhost`.
2. **Merged PRs in the last 30 days?** Expect >10, with tests.
3. **Real metric source?** Data should come from production systems, not seeded fixtures.

Fail any item above and respond with: **"Send me when it ships."**
