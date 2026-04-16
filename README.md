# 🌍 Vunoh Diaspora Assistant

An AI-powered task management platform that helps Kenyans living abroad initiate and track services back home — including money transfers, local service hires, and document verification.

Built as part of the **Vunoh Global AI Internship Practical Test (2026)**.

---

## 📌 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Running the App](#running-the-app)
- [Database](#database)
- [API Endpoints](#api-endpoints)
- [Decisions I Made and Why](#decisions-i-made-and-why)
- [Known Limitations](#known-limitations)

---

## Overview

Kenyans in the diaspora often rely on informal channels — WhatsApp groups, phone calls to relatives, or word of mouth — to manage tasks back home. These channels are slow, unreliable, and leave no audit trail.

This application provides a structured AI-powered assistant that:
- Understands natural language requests from diaspora customers
- Extracts intent and key entities from those requests
- Calculates a contextual risk score
- Generates step-by-step fulfilment plans
- Produces confirmation messages in three formats (WhatsApp, Email, SMS)
- Assigns tasks to the appropriate internal team
- Tracks everything in a persistent database with a live dashboard

---

## Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | **User Input** | Plain-English text input for customer requests |
| 2 | **AI Intent Extraction** | Identifies intent (`send_money`, `hire_service`, `verify_document`, `get_airport_transfer`, `check_status`) and extracts entities |
| 3 | **Risk Scoring** | Contextual risk score (0–100) based on urgency, amount, recipient trust, and document type |
| 4 | **Task Creation** | Unique task code, stored intent + entities, status, timestamp |
| 5 | **Step Generation** | AI-generated fulfilment steps specific to each intent |
| 6 | **Three-Format Messages** | WhatsApp, Email, and SMS confirmation messages — all saved and displayed |
| 7 | **Employee Assignment** | Auto-assigns tasks to Finance, Operations, or Legal teams |
| 8 | **Task Dashboard** | View all tasks, update status (Pending → In Progress → Completed) in real time |
| 9 | **Database Persistence** | All data saved to PostgreSQL/SQLite including history |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python + Flask |
| Frontend | HTML, CSS, Vanilla JavaScript |
| Database | PostgreSQL (SQLite for local dev) |
| AI Brain | Google Gemini API (free tier) |
| Hosting | Render (backend) + GitHub Pages or Render static (frontend) |

---

## Project Structure

```
vunoh-diaspora-assistant/
├── backend/
│   ├── app.py                  # Flask app entry point
│   ├── config.py               # Configuration and env loading
│   ├── models.py               # SQLAlchemy models
│   ├── routes/
│   │   ├── tasks.py            # Task creation and retrieval endpoints
│   │   └── dashboard.py        # Dashboard and status update endpoints
│   ├── services/
│   │   ├── ai_service.py       # All LLM calls (intent, steps, messages)
│   │   ├── risk_service.py     # Risk scoring logic
│   │   └── assignment_service.py # Employee team assignment
│   ├── prompts/
│   │   └── system_prompt.txt   # Master system prompt for the AI
│   └── requirements.txt
├── frontend/
│   ├── index.html              # Main UI (input + dashboard)
│   ├── style.css               # Styling
│   └── app.js                  # API calls and DOM interactions
├── database/
│   └── dump.sql                # Schema + 5 sample tasks with full data
├── .env.example
├── .gitignore
└── README.md
```

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- pip
- PostgreSQL (or SQLite for local development)
- A free [Google Gemini API key](https://aistudio.google.com/) (or any supported LLM)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/vunoh-diaspora-assistant.git
cd vunoh-diaspora-assistant
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
# Then edit .env with your actual values
```

### 5. Initialise the database

```bash
cd backend
flask db init
flask db migrate -m "initial schema"
flask db upgrade
```

Or, to load the sample data directly:

```bash
psql -U your_user -d your_db < database/dump.sql
```

---

## Environment Variables

Create a `.env` file in the root directory based on `.env.example`:

```env
FLASK_APP=backend/app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/vunoh_db
# For SQLite (local dev only):
# DATABASE_URL=sqlite:///vunoh.db

# AI API
GEMINI_API_KEY=your-gemini-api-key-here
```

---

## Running the App

```bash
cd backend
flask run
```

The app will be available at `http://localhost:5000`.

Open `frontend/index.html` directly in a browser, or serve it with:

```bash
# From the project root
python -m http.server 8080 --directory frontend
```

Then visit `http://localhost:8080`.

---

## Database

The full schema and five sample tasks with complete data (entities, steps, all three messages, risk scores, employee assignments) are included in:

```
database/dump.sql
```

### Core Tables

| Table | Purpose |
|-------|---------|
| `tasks` | Core task record: code, intent, entities (JSON), status, risk score, team, timestamps |
| `task_steps` | Ordered fulfilment steps per task |
| `task_messages` | WhatsApp, Email, and SMS messages per task |
| `status_history` | Audit trail of every status change |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/tasks` | Submit a new request; returns full task object |
| `GET` | `/api/tasks` | Retrieve all tasks for the dashboard |
| `GET` | `/api/tasks/<task_code>` | Retrieve a single task by code |
| `PATCH` | `/api/tasks/<task_code>/status` | Update task status |

---

## Decisions I Made and Why

### AI Tools Used

| Tool | Used For |
|------|----------|
| Claude (Anthropic) | Initial architecture planning, system prompt design, debugging edge cases |
| GitHub Copilot | Boilerplate Flask routes and SQLAlchemy model scaffolding |
| Gemini API | Runtime AI brain for intent extraction, step generation, and message formatting |

---

### System Prompt Design

The system prompt is structured in three explicit sections:

1. **Role definition** — The AI is told it is a structured data extraction engine for a Kenyan diaspora services platform, not a conversational chatbot. This reduces hallucination and keeps outputs parseable.

2. **Output schema** — The prompt specifies an exact JSON schema the model must return, including field names, types, and allowed enum values for `intent`. This was the most important design decision. Early tests with looser prompts returned inconsistent field names (`service_type` vs `serviceType`) that broke the parser.

3. **Kenyan context anchoring** — The prompt includes brief context about Kenyan geography (Nairobi, Kisumu, Mombasa), common document types (title deeds, Huduma Namba), and common services (M-Pesa transfers, fundi, chokora errands). This significantly improved entity extraction accuracy for local inputs.

**What I excluded:** I deliberately left out few-shot examples in the main prompt to keep token usage low on the free tier. Instead, I validated outputs against the schema and re-prompted only on failure.

---

### Risk Scoring Logic

Risk is calculated as a composite score out of 100, grounded in real diaspora fraud and service failure patterns:

| Factor | Weight | Reasoning |
|--------|--------|-----------|
| Urgency flag | +20 | Urgency is a common social engineering trigger in wire fraud |
| Transfer amount > KES 50,000 | +25 | Large transfers carry higher regulatory and fraud risk |
| Transfer amount > KES 10,000 | +15 | Medium-value threshold |
| Unknown or first-time recipient | +20 | No prior relationship or verification on file |
| Land title verification | +20 | Land fraud is among the most common financial crimes in Kenya |
| General document (non-land) | +10 | Lower but non-zero verification risk |
| Service hire in unverified area | +10 | Operational risk without established provider network |

Scores above 70 are flagged as High Risk and surfaced prominently in the dashboard.

---

### One Decision Where I Changed What the AI Suggested

When designing the employee assignment logic, Claude initially suggested a more granular role system with individual employee records and load-balancing. I overrode this in favour of a simple three-team model (Finance, Operations, Legal) because:

- The spec explicitly says "a simple assignment model is fine"
- Adding individual employee records would require seeding realistic dummy data, increasing submission complexity without adding evaluation value
- It would be harder to explain and defend in an interview than a clean, deliberate simplification

The simpler model is also easier to extend later, which I noted in the README.

---

### One Thing That Did Not Work as Expected

The first version of the SMS message generator frequently exceeded 160 characters when the task code was long. The AI would summarise well but forget to account for the task code prefix eating ~15 characters.

I resolved this by adding an explicit character budget instruction to the SMS section of the system prompt: *"The SMS must be under 145 characters, excluding the task code which will be appended separately."* The task code is then appended in the backend, not by the AI. This made SMS outputs consistently compliant.

---

## Known Limitations

- No user authentication. All tasks are visible on the shared dashboard (appropriate for a prototype).
- Risk scoring does not yet incorporate historical customer data. A returning customer discount is scaffolded but not fully implemented.
- The Gemini free tier has rate limits. Under heavy use, the app will queue requests.


---

## Author

Built by **Maryann Mweru** for the Vunoh Global AI Internship 2026.
