# Agent instructions: ChessDex on dextercarpenter.github.io

Handoff from the ChessDex repo. **Do not modify ChessDex** for this task unless Render deploy is still missing (see prerequisite). Work only in **DexterCarpenter.github.io**.

**User preference:** Do not add `Co-authored-by: Cursor` (or any Cursor attribution) to git commits. Use a plain commit message only. If the environment auto-appends co-author trailers, amend or recommit without them before pushing.

---

## Goal

Add a **live playable** ChessDex page on https://dextercarpenter.github.io/chessdex/ by embedding the hosted play UI in an iframe. Add nav + portfolio links.

---

## Prerequisite (ChessDex / Render)

The iframe target must be a **running** Python server (static UI + `/api/*`), not GitHub Pages alone.

1. Ensure [ChessDex](https://github.com/DexterCarpenter/ChessDex) `main` includes:
   - `.github/workflows/ci.yml`
   - `Dockerfile`, `render.yaml`
   - `src/ui/server.py` reading `HOST` / `PORT` from the environment
2. Deploy to [Render](https://render.com) per [docs/DEPLOY.md](../../docs/DEPLOY.md) (Docker, branch `main`, service name e.g. `chessdex`).
3. Confirm the public URL works, e.g.:
   ```bash
   curl -s https://chessdex.onrender.com/api/state | head -c 120
   ```
4. If the Render URL differs from `https://chessdex.onrender.com`, use the actual URL in `docs/chessdex.md` below.

---

## Repository setup

```bash
git clone https://github.com/DexterCarpenter/DexterCarpenter.github.io.git
cd DexterCarpenter.github.io
git checkout dark-theme   # GitHub Pages publishes from this branch (not main)
```

Local reference copies of intended content live in the ChessDex repo at:

`integration/personal-site/chessdex.md`  
`integration/personal-site/portfolio.patch.md`

---

## Task 1: Create `docs/chessdex.md`

Create **new file** `docs/chessdex.md` with this content (update iframe `src` if Render URL differs):

```markdown
---
layout: page
title: ChessDex
permalink: /chessdex/
published: true
---

Play against my chess engine in the browser. The game runs on a small Python server; on the free hosting tier it may take up to ~30 seconds to wake up after idle time.

<iframe
  src="https://chessdex.onrender.com/"
  title="ChessDex play UI"
  width="100%"
  height="820"
  style="border: 1px solid #444; border-radius: 6px; max-width: 1100px;"
  loading="lazy"
  allow="fullscreen"
></iframe>

[Source code on GitHub](https://github.com/DexterCarpenter/ChessDex)
```

---

## Task 2: Site navigation — `docs/_config.yml`

Add a `header_pages` block so the Minima theme shows **ChessDex** in the header (see `docs/_includes/header.html`).

**Merge** into existing `docs/_config.yml` (do not remove other settings). Place after `linkedin_username` (or equivalent site settings):

```yaml
header_pages:
  - index.markdown
  - portfolio.md
  - chessdex.md
  - resume.md
```

If `header_pages` already exists, add `- chessdex.md` in a sensible order (e.g. after `portfolio.md`).

---

## Task 3: Portfolio — `docs/portfolio.md`

### 3a. Sidebar

Inside `<div class="sidenav">`, add after the RingGame link:

```html
	<a href="#chessdex"                      >ChessDex</a>
```

### 3b. New section

At the **end** of the file (after the RingGame section), append:

```markdown
<hr>
# ChessDex
*2024 – present*

A chess engine and bitboard library written from scratch in Python, with a browser play UI. You can [play against the engine live](/chessdex/) on this site or browse the [ChessDex repository](https://github.com/DexterCarpenter/ChessDex).
```

---

## Task 4: Commit and push

```bash
git add docs/chessdex.md docs/_config.yml docs/portfolio.md
git status   # expect only these three files
git commit -m "Add ChessDex page with live play embed"
git log -1 --format=full   # confirm NO Co-authored-by: Cursor line; amend if present
git push origin dark-theme
```

---

## Task 5: Verify

1. Wait for GitHub Pages build on `dark-theme` (Actions tab on the github.io repo, if enabled).
2. Open https://dextercarpenter.github.io/chessdex/
3. Confirm header link **ChessDex** appears.
4. Confirm iframe loads the board (allow ~30s on first load if Render free tier was sleeping).
5. Play one move vs the engine in the iframe.
6. Open https://dextercarpenter.github.io/portfolio/ — confirm ChessDex sidebar link and section.

---

## Troubleshooting

| Issue | Action |
|--------|--------|
| iframe blank / “Cannot reach server” | Render service down or wrong URL in `chessdex.md`; redeploy ChessDex and fix `src`. |
| 404 on `/chessdex/` | Check `permalink: /chessdex/` and that Pages source is `docs/` on `dark-theme`. |
| ChessDex missing from header | `header_pages` must list `chessdex.md` exactly; restart Jekyll locally to test: `cd docs && bundle exec jekyll serve`. |
| Co-authored-by added on commit | Amend with message only: `git commit --amend -F /path/to/msg.txt` |

---

## Out of scope

- Copying ChessDex static assets into Jekyll (iframe embed is intentional).
- CORS / split API hosting.
- Changes to ChessDex engine code (unless deploying Render for the first time).

---

## Done when

- [ ] Render URL serves `/api/state` and playable UI
- [ ] `docs/chessdex.md` exists on `dark-theme`
- [ ] `header_pages` includes `chessdex.md`
- [ ] Portfolio sidebar + section updated
- [ ] Pushed to `origin/dark-theme` without Cursor co-author trailer
- [ ] Live site verified at `/chessdex/` and portfolio link works
