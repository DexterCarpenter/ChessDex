# Deploy ChessDex play UI (Render)

The play UI is a single Python process that serves static files and `/api/*`. Use Docker on [Render](https://render.com) (free tier).

## One-time setup

1. Push `main` with `Dockerfile` and `render.yaml` to [ChessDex](https://github.com/DexterCarpenter/ChessDex).
2. In Render: **New → Blueprint** (or **Web Service → Docker**).
3. Connect the ChessDex GitHub repo, branch **main**.
4. Render sets `PORT` automatically; `HOST=0.0.0.0` is set in `render.yaml` / `Dockerfile`.
5. After deploy, note the service URL (e.g. `https://chessdex.onrender.com`).

## Verify

```bash
curl -s https://chessdex.onrender.com/api/state | head -c 120
```

Open the service URL in a browser; play a move vs the engine.

## Personal site embed

Point the iframe on [dextercarpenter.github.io](https://dextercarpenter.github.io/chessdex/) at this URL. Update `docs/chessdex.md` if the Render service name differs.

**Note:** Free tier sleeps after inactivity; the first request may take ~30 seconds.
