# Backend / Database implementation guide

This ZIP is an updated copy of the uploaded `aicareercoach-main` snapshot, with a new Django backend. It does not contain your teammates' unpublished branches and has not been pushed to GitHub. ASSIST was used only as a reference. Parser and matching source files are unchanged.

## What was converted

The five ASSIST course CRUD pages now manage each student's resumes. Use `data/templates/resumes/`, rather than keeping the misleading `courses/` directory. There are no course enrollment, teacher, CRN, or credit fields.

| Old page under `courses/` | New page under `resumes/` | Named route |
|---|---|---|
| `list.html` | `list.html` | `resume_list` |
| `detail.html` | `detail.html` | `resume_detail` |
| `new.html` | `new.html` | `resume_create` |
| `edit.html` | `edit.html` | `resume_edit` |
| `delete_confirm.html` | `delete_confirm.html` | `resume_delete` |

Your account page layout, template blocks, and CSS class names were retained in `data/templates/accounts/`. The base template now has real Resume, Job Matches, and Profile routes. Logout is a CSRF-protected POST and redirects to your logout page. The CSS is a small functional baseline for your UI teammate to restyle; external icon/CDN dependencies were removed.

## Which ideas belong to whom?

| Idea | Main owner | Your backend work implemented here | Still needed |
|---|---|---|---|
| 1. Major and minor | Resume + Job Matching | Editable major/minor on Resume; structured JSON storage | Parser extracts them, user confirms, matcher includes them in ranking |
| 2. Ask presentation visitors about layout and career suggestions | Frontend/UI + team | No new database required for live verbal feedback | UI teammate prepares alternative layouts; team collects feedback. Add survey storage later if an in-app survey is wanted. |
| 3. Grammar and buzzword corrections | Resume/AI | Typed feedback, evidence, suggestions, and review status storage | Analysis engine generates useful corrections and calls the storage contract |
| 4. Comments for organization | Everyone | Module docstrings and comments explaining ownership, authorization, throttling, and stale-result handling | Teammates document their parser, ranking, and UI decisions similarly |
| 5. Inconsistency review | Resume/AI, with Backend support | Consistency feedback with open/resolved/dismissed states | Evidence-based detection; do not label users dishonest or reject them because of employer prestige |
| 6. Account security | Backend/Database | Password hashing/validation, validated unique emails, authenticated sessions, private CRUD, CSRF, request throttling, and production HTTPS settings | Hosting configuration, email ownership verification, password recovery, monitoring, and operational protection |

A student can legitimately work at Whataburger, a gift shop, and NASA. Employer names alone are not an inconsistency. Ask the analysis teammate to flag specific evidence, such as an end date before a start date, and explain the suggested correction. Dismissing a flag must remain possible. Marking a flag corrected records a review decision; it does not independently verify the claim.

## Run locally (macOS/Linux)

Use Python 3.10+ (verified here with Python 3.12). From the extracted project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-backend.txt
export DJANGO_DEBUG=1
export DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(50))')"
python manage.py migrate
python manage.py test data
python manage.py runserver
```

Open http://127.0.0.1:8000/. Register, add a resume by pasting text, fill in major/minor, then view/edit/delete it. Another account cannot see it. No PDF upload or automatic AI processing is connected yet. Feedback and match pages show saved results only, with honest empty states until integration.

`requirements-backend.txt` installs only backend dependencies, not the parser's PDF library or the matching model. It uses the Django 5.2 LTS release series; keep security patches current. An optional admin account is created with `python manage.py createsuperuser`. Resumes are not registered in the generic admin UI.

`.env.example` is a variable reference. The application does not automatically load `.env`; export the variables or configure them through your host. SQLite is the default local database. Export `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, and optionally `POSTGRES_HOST` / `POSTGRES_PORT` to use PostgreSQL, then run migrations against that database. PostgreSQL and pgvector were not tested here. Vector indexing remains future matching-team integration.

## Files to merge into your backend branch

Add `manage.py`, `requirements-backend.txt`, `.env.example`, this guide, and the new files in `backend/` and `data/`. Review the `.gitignore` update. Leave your teammates' `resume_parser/`, `matching/`, `frontend/`, and existing `tests/` code in place. Replace your copied course pages with `data/templates/resumes/` and merge your account templates with the working versions here.

This snapshot has no Git history or branch metadata. Merge into your own checkout rather than treating the ZIP as a replacement for everyone's latest branch. If teammates already created Django settings, routes, or models, reconcile these before applying migrations.

**Important:** `AUTH_USER_MODEL = 'data.User'` is intended for a fresh database. The uploaded snapshot has no Django database. If your actual branch already has migrations/data using Django's default User, do not switch user models blindly; plan that migration before using this scaffold. `data/migrations/0001_initial.py` is included, so you normally run `migrate`, not `makemigrations`.

## How the backend connects to the AI work

`data.models.Resume` is a Django database model. `resume_parser.models.CandidateProfile` is a parser dataclass; keep them separate. Capture the resume's `updated_at` before processing, run the parser/feedback/matching code in a trusted worker, and then call:

```python
from data.services import store_analysis

store_analysis(
    owner=resume.owner,
    resume_id=resume.pk,
    expected_updated_at=version_captured_before_processing,
    structured_data=parsed_profile.to_dict(),
    feedback=[{
        'kind': 'consistency',  # grammar, wording, or consistency
        'message': 'The end date appears earlier than the start date.',
        'evidence': '2029 - 2025',
        'suggestion': 'Check these dates against your records.',
    }],
    matches=[{
        'external_id': 'provider:job-123',
        'title': 'Junior Engineer',
        'company': 'Example Company',
        'url': 'https://example.com/jobs/123',
        'score': 0.72,
        'explanation': 'Relevant engineering skills and academic background.',
    }],
)
```

This example demonstrates storage only; the sample feedback and job are not generated or inserted automatically. `store_analysis` is an internal Python function, not a public endpoint. Call it from Django's environment. Scores represent cosine similarity (-1 to 1), not a probability of getting hired. Validate/normalize real provider scores in the matching adapter.

The function verifies ownership, validates allowed result fields and HTTP(S) links, and replaces an analysis atomically. Invalid output rolls back the previous results. If the resume changed during analysis it raises `StaleAnalysis`. Editing a resume clears stale structured data, feedback, and matches. Deleting it cascades to its saved results.

Major/minor fields can be entered now; automatic extraction is not implemented. Your parser currently has no dedicated major/minor education fields. Agree with the parser teammate on structured education metadata and how to reconcile it with student-confirmed values. Likewise, agree on job provider identifiers before integrating storage. An AI provider key must stay server-side.

## Account security scope

This is application security, not a network firewall. Email syntax and case-insensitive uniqueness are enforced; address ownership is NOT verified, and accounts are immediately usable after registration. Add signed expiring email verification and configure an email provider if your team requires verified addresses. Password reset is not included.

Login POSTs are limited to 10 per direct peer IP per fixed minute, registration POSTs to 5 per fixed hour. Admin login has a separate 10/minute policy. Counters use keyed IP digests and atomic conditional database updates. Prune expired counters regularly with `python manage.py prune_auth_quotas`. Fixed windows permit bursts across a boundary. People on shared IPs can share a quota. This does not stop distributed abuse or replace a hosting firewall. Behind a proxy, configure a trusted peer/client-IP strategy; arbitrary `X-Forwarded-For` is deliberately not trusted. Use a stable secret across workers.

Production defaults require a secret key, turn DEBUG off, enforce HTTPS, and use secure cookies. Set real allowed hosts and trusted CSRF origins. Configure the reverse proxy's HTTPS behavior explicitly; Django does not assume forwarded headers are trustworthy. Run `python manage.py check --deploy` with production variables and `python manage.py collectstatic`. Use a production server and request-size limits, not `runserver`. Deploy-time checks are a baseline, not proof of security. See the [Django security overview](https://docs.djangoproject.com/en/5.2/topics/security/) and [deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/).

## Validation

The `data` integration suite checks auth, hashed passwords, email uniqueness, private CRUD, forged owner input, cross-user denial, POST-only logout/review, CSRF enforcement, escaped resume text, safe redirects, result validation/rollback, stale analysis, cascade deletion, rate limits, and template rendering. It does not exercise unpublished branches, live email, live AI, a browser layout, or PostgreSQL concurrency.

Validation in this session: all 13 backend integration tests passed; migrations applied on SQLite; Django system checks passed; migration drift check found no changes. The production check reported only W005/W021 for HSTS subdomains/preload. Those settings remain off until the team confirms that every affected domain supports HTTPS and decides on preload. Existing parser/matching source was byte-compared with the uploaded snapshot and left unchanged.
