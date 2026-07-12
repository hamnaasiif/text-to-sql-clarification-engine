# Deployment Guide

This project uses three free-tier services for deployment. **Do not sign up or configure anything until you're ready** — this document just lists what needs to happen.

---

## 1. Database → Neon.tech (free tier)

1. Create a Neon account at [neon.tech](https://neon.tech).
2. Create a new project and database.
3. Run your `app/database/sessions_schema.sql` (and any other schema files) against the Neon database to create the required tables.
4. Copy the connection string — it will look like:
   ```
   postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require
   ```
5. You'll paste this as `DATABASE_URL` in both Render (step 2) and your local `.env` if you want to test against the remote DB.

> **Known trade-off:** The `conversation_sessions` table has no automatic cleanup — sessions persist forever. This is fine for a demo, but a production system would need a TTL/cron job to purge stale sessions.

---

## 2. Backend → Render (free tier)

1. Create a Render account at [render.com](https://render.com).
2. Create a new **Web Service**, connect your GitHub repo.
3. Configure:
   - **Root Directory:** (leave blank — the repo root, since `app/` is a Python package)
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.api.routes:app --host 0.0.0.0 --port $PORT`
   - **Environment:**
     - `DATABASE_URL` = your Neon connection string from step 1
     - `GROQ_API_KEY` = your Groq API key
4. After deploying, note your Render URL (e.g. `https://your-app.onrender.com`).
5. **Update CORS:** In `app/api/routes.py`, add your Vercel frontend URL to the `allow_origins` list (see the `# TODO` comment already in the code).

> **Note:** Render free-tier services spin down after 15 minutes of inactivity. The first request after idle will take ~30 seconds to cold-start. This is expected for a demo.

---

## 3. Frontend → Vercel (free tier)

1. Create a Vercel account at [vercel.com](https://vercel.com).
2. Import your GitHub repo.
3. Configure:
   - **Root Directory:** `frontend`
   - **Framework Preset:** Vite (should auto-detect)
   - **Build Command:** `npm run build` (auto-detected)
   - **Output Directory:** `dist` (auto-detected)
   - **Environment Variables:**
     - `VITE_API_URL` = your Render backend URL from step 2 (e.g. `https://your-app.onrender.com`)
4. Deploy. Your frontend will be live at `https://your-app.vercel.app`.
5. **Go back to step 2.5:** Add the Vercel URL to the CORS `allow_origins` in `routes.py` and redeploy the backend.

---

## Post-deployment checklist

- [ ] Neon database created and schema applied
- [ ] `DATABASE_URL` set in Render env vars
- [ ] `GROQ_API_KEY` set in Render env vars
- [ ] Backend deploying on Render with correct start command
- [ ] `VITE_API_URL` set in Vercel env vars pointing to Render URL
- [ ] CORS `allow_origins` updated with Vercel URL, backend redeployed
- [ ] End-to-end test: ask an ambiguous question from the Vercel frontend, go through clarification, get final answer

---

## Local development

```bash
# Terminal 1 — Backend
uvicorn app.api.routes:app --reload

# Terminal 2 — Frontend
cd frontend
cp .env.example .env   # if first time
npm run dev
```

Frontend runs on `http://localhost:5173`, backend on `http://127.0.0.1:8000`.
