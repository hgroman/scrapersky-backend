# ScraperSky Backend

A multi-tenant **FastAPI** service for large-scale web-metadata extraction, secured by Supabase and shipped in Docker.

---

## 🗺️ Knowledge Map & Prescribed Paths

This project utilizes a role-based knowledge system. To ensure focus and prevent context overload, every contributor **must** follow the prescribed path for their role.

**Legend:** `[Full]` = Mastery Required. `[Summary]` = High-Level Reading.

| Persona Type | Primary Objective | Prescribed Knowledge Path (Start Here) |
| :--- | :--- | :--- |
| 🏛️ **The Architect** | System-Wide Design & Orchestration | 1. [`ScraperSky_Development_Constitution.md`](./Docs/00_Constitution/ScraperSky_Development_Constitution.md) `[Full]` |
| 🔬 **The Layer Persona**<br>(Specialist) | Deep Domain Expertise & Compliance | 1. Your Specific `Layer-X-Blueprint.md`<br>2. [`Guardian_Operational_Manual.md`](./Docs/Docs_21_SeptaGram_Personas/Guardian_Operational_Manual.md) |
| ✈️ **The Workflow Persona**<br>(Operator) | End-to-End Process Execution | 1. Your Specific `WF-X_Truth_Document.md`<br>2. The `README_ADDENDUM.md` for operational commands |
| 🧑‍💻 **New Contributor**<br>(Human or AI) | General Onboarding & Orientation | 1. [`v_scrapersky-quickstart.md`](./v_scrapersky-quickstart.md)<br>2. [`Constitution_Summary_and_Guardrails.md`](./Docs/00_Constitution/Constitution_Summary_and_Guardrails.md) `[Summary]` |

**Constitutional Mandate:** All roles are governed by the [ScraperSky Development Constitution](./Docs/00_Constitution/ScraperSky_Development_Constitution.md). While specialists are not required to master it, they are expected to comply with articles cited by The Architect.

---

## ⚡ Quick-start

```bash
git clone <your-repo>
cd scraper-sky-backend
cp .env.example .env   # fill the five REQUIRED vars
docker compose up --build
open http://localhost:8000/docs
```
