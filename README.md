# ScraperSky Backend

A multi-tenant **FastAPI** service for large-scale web-metadata extraction, secured by Supabase and shipped in Docker.

## ⚡ Quick-start

```bash
git clone <your-repo>
cd scraper-sky-backend
cp .env.example .env   # fill the five REQUIRED vars
docker compose up --build
open http://localhost:8000/docs
```

*(Need a demo JWT? See `README_ADDENDUM.md#environment`.)*

## Next steps

- **Build & test:** `pytest -q && ruff check .`
- **Deploy:** `render deploy` (uses `render.yaml`)

## Where is everything else?

Day-to-day reference material now lives in **`README_ADDENDUM.md`** — copy/paste any section into ChatGPT or Grep it when you need it.

Additional deep-dive docs live under `Docs/`.

---
