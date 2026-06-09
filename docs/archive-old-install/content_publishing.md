# Content Publishing Workflow (Updated)

## Overview
We now run a **research step** before any new post is created on our AI‑focused WordPress sites. This ensures fresh, non‑duplicate content and improves SEO relevance.

## How it works
1. **Research** – `_run_research(site_key)` is called at the start of `create_post`. It can be replaced with a real script (e.g. `scripts/research/research_aitoolalliance.sh`). The placeholder simply logs the step and returns success.
2. **Abort on failure** – If the research step returns `False`, the post creation is aborted and a warning is printed.
3. **Post creation** – After a successful research step, the usual WordPress REST API call creates the post.

## Files changed
- `scripts/publishing/wp_rest_api.py` – added `_run_research` and integrated it into `create_post`.

## Next steps for you
- Replace the placeholder `_run_research` with the actual research script you want to run (SEO keyword extraction, news scraping, etc.).
- Ensure any cron jobs or automation that calls `wp_rest_api.py create …` are unchanged; the new workflow runs automatically.
- Review the log output to confirm the research step runs before each publish.

## Sites covered
- `aitoolalliance.com`
- `aibusinessinsider.org`
- `aicofounderstack.com`
- `eveonion.com`

Feel free to adjust the research script or add site‑specific logic inside `_run_research`.
