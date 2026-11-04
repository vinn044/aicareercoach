# run the app

open two terminals.

```bash
# terminal 1: backend
cd ~/Desktop/projects/aicareercoach
source .venv/bin/activate
python -m uvicorn backend.main:app --reload
```

```bash
# terminal 2: website
cd ~/Desktop/projects/aicareercoach/frontend
npm run dev
```

open the vite link, usually `http://localhost:5173`.

# test it

pick a job type and location, upload a pdf resume, then click **analyze resume**.
the job cards and apply links show up below the results.

# don't waste adzuna calls

- opening, refreshing, and uploading use no calls.
- a new job type/location + **analyze resume** uses one call and gets up to 20 jobs.
- the same search again uses no extra call while the backend is still running.
- changing the job type/location, or restarting the backend, can use another call.

to use sample jobs instead, put this in `.env` and restart the backend:

```env
ADZUNA_ENABLED=false
```

set it back to `true` when you want live jobs again.
