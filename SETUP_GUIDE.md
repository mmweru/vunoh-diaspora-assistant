# 🚀 Vunoh Diaspora Assistant — Complete Setup Guide

This guide takes you from zero to a running application, step by step.
Written for beginners using VS Code on Windows or macOS.

---

## PART 1 — What You Need Installed First

Before anything else, install these tools. Click each link and follow the installer.

| Tool | Why | Download |
|------|-----|----------|
| Python 3.10+ | Runs the Django backend | https://python.org/downloads — tick "Add to PATH" during install |
| Git | Version control + GitHub | https://git-scm.com/downloads |
| VS Code | Your code editor | https://code.visualstudio.com |
| Live Server extension | Serves your frontend locally | Install inside VS Code (explained below) |

### Install the VS Code Live Server extension
1. Open VS Code
2. Press `Ctrl+Shift+X` (Windows) or `Cmd+Shift+X` (Mac) to open Extensions
3. Search for **"Live Server"** by Ritwick Dey
4. Click **Install**

### Verify Python is installed
Open a terminal (in VS Code: `Ctrl+`` ` or Terminal → New Terminal) and run:
```bash
python --version
# Should print: Python 3.10.x or higher

pip --version
# Should print a version number
```

---

## PART 2 — Get Your Free Gemini API Key

This is what powers the AI brain of the application.

1. Go to **https://aistudio.google.com/**
2. Sign in with a Google account
3. Click **"Get API Key"** → **"Create API Key"**
4. Copy the key — it starts with `AIza...`
5. Keep it safe. You'll paste it into your `.env` file in a moment.

> The free tier gives you 15 requests/minute and 1,500 requests/day — more than enough.

---

## PART 3 — Clone the Repository and Open in VS Code

```bash
# 1. Clone the repo (replace YOUR_USERNAME with your GitHub username)
git clone https://github.com/YOUR_USERNAME/vunoh-diaspora-assistant.git

# 2. Open the folder in VS Code
cd vunoh-diaspora-assistant
code .
```

VS Code will open the entire project folder.

---

## PART 4 — Set Up the Backend (Django)

Open a terminal inside VS Code (`Ctrl+`` ` ) and run these commands one by one.

### Step 4a — Create a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

You'll see `(venv)` at the start of your terminal line. This means it's active.
**Always activate the venv before running any Python/Django commands.**

### Step 4b — Install all dependencies
```bash
cd backend
pip install -r requirements.txt
```

This installs Django, Django REST Framework, CORS headers, Gemini AI, and everything else.
It takes about 1-2 minutes.

### Step 4c — Create your .env file
```bash
# Go back to the project root
cd ..

# Windows (copy the example file)
copy .env.example .env

# Mac / Linux
cp .env.example .env
```

Now open the `.env` file in VS Code and fill it in:

```env
SECRET_KEY=any-long-random-string-you-make-up-like-this-abc123xyz
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=
GEMINI_API_KEY=AIzaSy...your-actual-key-here
```

> Leave `DATABASE_URL` blank for now — it will use SQLite automatically (perfect for local dev).

### Step 4d — Set up the database
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

You'll see a list of "OK" messages. This creates the database file (`db.sqlite3`).

### Step 4e — Create a Django admin account (optional but useful)
```bash
python manage.py createsuperuser
```
Enter a username, email (can be fake), and password. You can use this to log into
`http://127.0.0.1:8000/admin` and inspect data directly.

### Step 4f — Load the 5 sample tasks
```bash
python manage.py seed_data
```

You should see:
```
🌱 Seeding database with sample tasks...
  ✅ Created task VNH-XXXXX — send_money
  ✅ Created task VNH-XXXXX — verify_document
  ✅ Created task VNH-XXXXX — hire_service
  ✅ Created task VNH-XXXXX — get_airport_transfer
  ✅ Created task VNH-XXXXX — send_money
🎉 Done! 5 sample tasks created.
```

### Step 4g — Start the backend server
```bash
python manage.py runserver
```

You should see:
```
System check identified no issues (0 silenced).
Django version 4.2.11, using settings 'vunoh.settings'
Starting development server at http://127.0.0.1:8000/
```

**Leave this terminal open.** The backend is now running.

---

## PART 5 — Run the Frontend

Open a **second terminal** in VS Code (`+` button in the terminal panel).

### Option A — Use Live Server (recommended)
1. In VS Code's file explorer, find `frontend/index.html`
2. Right-click it → **"Open with Live Server"**
3. Your browser opens at `http://127.0.0.1:5500/frontend/`

### Option B — Use Python's built-in server
```bash
# From the project root (not the backend folder)
python -m http.server 5500 --directory frontend
```
Then open `http://localhost:5500` in your browser.

---

## PART 6 — Test That Everything Works

### Quick smoke test — open your browser and visit:

| URL | What you should see |
|-----|---------------------|
| `http://127.0.0.1:8000/api/tasks/` | JSON list of your 5 sample tasks |
| `http://127.0.0.1:8000/api/tasks/stats/` | JSON with total, by_status, etc. |
| `http://127.0.0.1:8000/admin/` | Django admin login page |
| `http://127.0.0.1:5500/frontend/` | The Vunoh UI |

### Test the full AI pipeline in the UI
1. Open `http://127.0.0.1:5500/frontend/`
2. Type a request: `I need to send KES 15,000 to my mother in Kisumu urgently`
3. Click **Submit Request**
4. Watch the loading steps animate
5. You should see a result card with:
   - A task code like `VNH-XXXXX`
   - Intent: **Send Money**
   - Risk score and level
   - 5 fulfilment steps
   - 3 messages (WhatsApp, Email, SMS)
6. Click **Dashboard** in the nav — your new task should appear in the table
7. Change the status dropdown — it should update instantly

### Test the API directly (for debugging)
Open a new terminal and run:
```bash
# Test creating a task
curl -X POST http://127.0.0.1:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Please verify my land title deed for a plot in Karen, Nairobi"}'
```

On Windows (PowerShell):
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/tasks/" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"message": "Please verify my land title deed for a plot in Karen, Nairobi"}'
```

---

## PART 7 — Run the Automated Tests

```bash
# Make sure you're in the backend folder with venv active
cd backend
python manage.py test tasks -v 2
```

You should see **31 tests, all OK**:
```
Ran 31 tests in 0.089s
OK
```

### What each test group covers
| Group | Tests |
|-------|-------|
| `RiskScoringTests` | Urgent transfer = high risk, land title = high, score caps at 100 |
| `AssignmentTests` | Correct team for each intent |
| `AIMockTests` | Mock AI extracts intent correctly, steps/messages have right shape |
| `TaskModelTests` | Task code auto-generated, risk level auto-set from score |
| `TaskAPITests` | All API endpoints, status updates, history recording |

### How to know if the AI is working vs mock
- **Without GEMINI_API_KEY**: The app uses smart mock responses. It still works — great for testing.
- **With GEMINI_API_KEY**: Real Gemini calls. You'll see richer, more contextual responses.

To verify which mode you're in, check the terminal logs when you submit a request:
```
# Mock mode:
WARNING:tasks.ai_service:GEMINI_API_KEY not set — using fallback mock extraction

# Real AI mode:
INFO:tasks.ai_service:AI extraction succeeded: intent=send_money
```

---

## PART 8 — Deploy to Render (Free Hosting)

This makes your project live on the internet so you can submit a hosted link.

### Step 8a — Push your code to GitHub
```bash
# In the project root, with venv deactivated (type: deactivate)
git add .
git commit -m "feat: complete vunoh diaspora assistant"
git push origin main
```

### Step 8b — Deploy backend on Render

1. Go to **https://render.com** and sign up (free)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account and select `vunoh-diaspora-assistant`
4. Fill in the form:
   - **Name**: `vunoh-diaspora-assistant`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn vunoh.wsgi:application`
5. Scroll to **Environment Variables** and add:
   - `SECRET_KEY` → any long random string
   - `DEBUG` → `False`
   - `ALLOWED_HOSTS` → `.onrender.com`
   - `GEMINI_API_KEY` → your Gemini key
   - `DATABASE_URL` → leave blank for now (Render gives SQLite-equivalent)
6. Click **"Create Web Service"**
7. Wait ~3 minutes for the build. You'll get a URL like `https://vunoh-diaspora-assistant.onrender.com`

### Step 8c — Run migrations on Render
In the Render dashboard, go to your service → **"Shell"** tab:
```bash
python manage.py migrate
python manage.py seed_data
```

### Step 8d — Update the frontend API URL
Open `frontend/app.js` and change line 8:
```javascript
// Change this:
const API_BASE = 'http://127.0.0.1:8000/api';

// To your Render URL:
const API_BASE = 'https://vunoh-diaspora-assistant.onrender.com/api';
```

### Step 8e — Host the frontend on GitHub Pages
1. Push the updated `app.js` to GitHub
2. Go to your GitHub repo → **Settings** → **Pages**
3. Under "Source": select **main branch**, folder **`/frontend`**
4. Click Save. GitHub gives you a URL like `https://yourusername.github.io/vunoh-diaspora-assistant/`

> **CORS note**: Since frontend and backend are on different domains, Django's
> `CORS_ALLOW_ALL_ORIGINS = True` in settings.py handles this for you already.

---

## PART 9 — Common Errors and Fixes

### ❌ `ModuleNotFoundError: No module named 'django'`
**Fix**: Your virtual environment isn't active.
```bash
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### ❌ `django.db.utils.OperationalError: no such table`
**Fix**: You haven't run migrations.
```bash
python manage.py migrate
```

### ❌ Frontend shows "Failed to load tasks. Is the backend running?"
**Fix**: The Django server isn't running. Open a terminal and:
```bash
cd backend && python manage.py runserver
```

### ❌ CORS error in browser console
**Fix**: Make sure `corsheaders` is in `INSTALLED_APPS` and
`CorsMiddleware` is at the top of `MIDDLEWARE` in `settings.py` (it already is in this project).

### ❌ Gemini API error: `API_KEY_INVALID`
**Fix**: Check your `.env` file. Make sure there are no spaces around the `=` sign:
```env
GEMINI_API_KEY=AIzaSy...  ✅ correct
GEMINI_API_KEY = AIzaSy... ❌ wrong
```

### ❌ `Address already in use` when running `runserver`
**Fix**: Something is already on port 8000. Use a different port:
```bash
python manage.py runserver 8001
```
Then update `API_BASE` in `frontend/app.js` to `http://127.0.0.1:8001/api`.

### ❌ Tests fail with import errors
**Fix**: Run tests from inside the `backend` folder:
```bash
cd backend
python manage.py test tasks
```

---

## PART 10 — Project Folder Structure (Final)

```
vunoh-diaspora-assistant/
│
├── backend/
│   ├── manage.py                          ← Django entry point
│   ├── requirements.txt                   ← All Python dependencies
│   ├── db.sqlite3                         ← Local database (auto-created)
│   │
│   ├── vunoh/                             ← Django project config
│   │   ├── settings.py                    ← All settings
│   │   ├── urls.py                        ← Root URL routing
│   │   └── wsgi.py                        ← Production server entry
│   │
│   └── tasks/                             ← Main Django app
│       ├── models.py                      ← Task, TaskStep, TaskMessage, StatusHistory
│       ├── views.py                       ← API endpoints (all 4 views)
│       ├── serializers.py                 ← DRF serializers
│       ├── urls.py                        ← /api/tasks/ routes
│       ├── ai_service.py                  ← Gemini AI calls + mock fallbacks
│       ├── risk_service.py                ← Risk scoring logic
│       ├── assignment_service.py          ← Team assignment
│       ├── admin.py                       ← Django admin panel config
│       ├── tests.py                       ← 31 automated tests
│       └── management/commands/
│           └── seed_data.py               ← python manage.py seed_data
│
├── frontend/
│   ├── index.html                         ← Single-page application
│   ├── style.css                          ← Full UI styles
│   └── app.js                             ← All frontend logic (no frameworks)
│
├── database/
│   └── dump.sql                           ← Schema + 5 complete sample tasks
│
├── .env.example                           ← Copy this to .env
├── .gitignore                             ← Keeps secrets and venv out of Git
├── render.yaml                            ← Render deployment config
├── Procfile                               ← Gunicorn start command
└── README.md                              ← Project documentation
```

---

## PART 11 — Daily Dev Workflow

Every time you sit down to work:

```bash
# 1. Open VS Code in the project folder
code .

# 2. Activate virtual environment (ALWAYS do this first)
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Start Django backend
cd backend
python manage.py runserver

# 4. In a second terminal, open frontend with Live Server
# Right-click frontend/index.html → "Open with Live Server"

# 5. When done, commit your work
cd ..  # go back to project root
git add .
git commit -m "feat: describe what you changed"
git push origin main
```

---

## PART 12 — API Reference (Quick Reference Card)

```
POST   /api/tasks/                  Create a task from a message
GET    /api/tasks/                  List all tasks
GET    /api/tasks/stats/            Dashboard summary stats
GET    /api/tasks/{task_code}/      Get one task with all details
PATCH  /api/tasks/{task_code}/status/  Update task status
```

### POST /api/tasks/ — Request body
```json
{ "message": "Your plain English request here" }
```

### PATCH /api/tasks/{code}/status/ — Request body
```json
{ "status": "in_progress", "note": "Optional note" }
```
Valid status values: `pending`, `in_progress`, `completed`, `cancelled`

---

## You're all set! 🇰🇪

If something is still not working after following this guide, check:
1. Is the virtual environment active? (`(venv)` in terminal)
2. Is `python manage.py runserver` running in a terminal?
3. Is the frontend being served (Live Server or `python -m http.server`)?
4. Does your `.env` file exist and have the right values?

These four things fix 95% of beginner issues.
