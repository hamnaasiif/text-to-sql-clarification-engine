# Text-to-SQL with an AI Clarification Engine

A natural-language-to-SQL system that **detects when a question is ambiguous and asks a clarifying question before generating SQL** — instead of silently guessing user intent like a typical text-to-SQL tool.

> **Typical text-to-SQL:** *"Show me the best customer"* → silently assumes "best" means highest revenue, runs the query, never mentions the assumption.
> **This system:** *"Show me the best customer"* → asks *"Do you mean highest revenue, most orders, or highest average order value?"* → generates SQL only once intent is clear.

---

## Table of Contents

- [Why This Project](#why-this-project)
- [How It Works](#how-it-works)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
- [Testing](#testing)
- [Evaluation](#evaluation)
- [Known Limitations & Future Work](#known-limitations--future-work)

---

## Why This Project

Most text-to-SQL demos optimize for "does it produce *a* query." This project instead treats ambiguity as a first-class problem: an LLM that confidently generates SQL for a vague question is worse than one that asks a question first, because a wrong-but-confident answer is harder to catch than an obviously missing one.

The project includes a full evaluation comparing a **baseline** (question → SQL, no clarification) against this **clarification-first system** on the same database and questions — see [Evaluation](#evaluation).

## How It Works

```
User Question
     │
     ▼
Schema Understanding (live introspection of the Postgres schema)
     │
     ▼
Ambiguity Engine ── is the question ambiguous, and in how many
     │                distinct ways (metric? time range? filter?)
     │
 ┌───┴────┐
 │        │
CLEAR   AMBIGUOUS ── ask one clarifying question per ambiguous
 │        │           aspect, collect all answers
 │        ▼
 │   Resolved Intent (original question + all clarifications merged)
 │        │
 └───┬────┘
     ▼
SQL Generation (schema + intent → SQL, via LLM structured output)
     │
     ▼
SQL Safety Validation (sqlglot parses the query — SELECT-only,
     │                  no string-matching)
     ▼
Query Execution ── on failure: send the error back to the LLM,
     │              regenerate, retry (max 2 retries)
     ▼
Natural Language Response
```

Each stage is a separate, single-responsibility component (`app/services/`), not one giant prompt — this made it possible to test, evaluate, and fix each stage independently (see the bug list under [Evaluation](#evaluation)).

### Key design decisions

- **Multi-dimensional ambiguity detection.** A single question can be ambiguous in more than one independent way (e.g. *"who made the most purchases last year"* is ambiguous in both *metric* and *time range*). The ambiguity engine returns a list of distinct `AmbiguityDimension` objects, each resolved with its own clarifying question, instead of merging everything into one confusing prompt.
- **Defense in depth on SQL safety.** The LLM is instructed to generate `SELECT`-only queries, but that instruction is never trusted alone — every query is parsed with `sqlglot` and rejected before execution if it isn't a `SELECT` statement, regardless of formatting or phrasing.
- **Schema includes sample values, not just column types.** For low-cardinality string columns (e.g. `order_status`), the schema sent to the LLM includes the actual distinct values stored (`['completed', 'pending', 'cancelled']`). Without this, the LLM guesses casing/spelling for filters (`'Completed'` vs. `'completed'`) and silently returns wrong results — this was a real bug found during evaluation.
- **Deterministic tie-breaking.** Any `ORDER BY ... LIMIT` query includes a secondary sort key (primary key) so that ranking queries return the same result set on every run, even when values tie — also a bug found during evaluation, not designed in from the start.

## Tech Stack

| Layer | Choice |
|---|---|
| Database | PostgreSQL |
| LLM provider | [Groq](https://console.groq.com) (free tier) — `openai/gpt-oss-120b` |
| Structured output validation | Pydantic |
| SQL parsing/safety | `sqlglot` |
| DB driver | `psycopg2` |
| Language | Python |

Groq was chosen specifically to keep the project's running cost at $0 — see [Setup](#setup--installation).

## Project Structure

```
text-to-sql-clarification-engine/
├── app/
│   ├── database/
│   │   ├── schema.sql          # 5-table schema (DDL)
│   │   ├── seed_data.sql       # base seed data
│   │   └── seed_v2.py          # additional data engineered to create
│   │                           # genuine ambiguity (revenue vs. order-count
│   │                           # conflicts, mixed categories, cancelled/
│   │                           # pending orders)
│   ├── models/
│   │   ├── ambiguity.py        # AmbiguityDimension, AmbiguityResult
│   │   └── sql.py              # SQLResult
│   └── services/
│       ├── schema_service.py       # live schema introspection
│       ├── ambiguity_service.py    # ambiguity detection
│       ├── conversation_service.py # resolves clarifications into intent
│       ├── sql_generator.py        # SQL generation + error-driven repair
│       ├── sql_validator.py        # SELECT-only enforcement (sqlglot)
│       ├── query_executor.py       # safe execution
│       └── response_generator.py   # natural-language final answer
├── evaluation/
│   ├── dataset.json             # 20 labeled questions (ambiguous/clear)
│   ├── evaluate_ambiguity.py    # accuracy / false-positive / false-negative
│   └── baseline.py              # no-clarification baseline, for comparison
├── tests/
│   ├── test_conversation_service.py
│   ├── test_error_recovery.py   # mocked failure + retry-loop tests
│   └── test_all_scenarios.py    # 8 end-to-end scenario tests
├── main.py                      # interactive CLI entry point
├── requirements.txt
└── .env                         # not committed — see Setup
```

## Setup & Installation

### Prerequisites

- Python 3.10+
- PostgreSQL installed and running locally

### 1. Clone and create a virtual environment

```bash
git clone <this-repo-url>
cd text-to-sql-clarification-engine
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt`:
```
fastapi
uvicorn[standard]
psycopg2-binary
sqlalchemy
pydantic
python-dotenv
groq
sqlglot
```

### 3. Create the database

```bash
psql -U postgres -c "CREATE DATABASE textsql_db;"
psql -U postgres -d textsql_db -f app/database/schema.sql
psql -U postgres -d textsql_db -f app/database/seed_data.sql
python app/database/seed_v2.py    # run exactly once — not idempotent
```

### 4. Get a free Groq API key

1. Sign up at [console.groq.com](https://console.groq.com) (no card required)
2. Go to **API Keys** → **Create API Key**
3. Copy the key immediately — it's only shown once

### 5. Configure environment variables

Create a `.env` file in the project root:

```
DATABASE_URL=postgresql://postgres:<your_password>@localhost:5432/textsql_db
GROQ_API_KEY=<your_groq_key>
```

## Usage

Run the interactive pipeline:

```bash
python main.py
```

Example session:

```
Ask a question about your data: What are our top selling products?

This question has 2 thing(s) to clarify:

Should the products be ranked by total quantity sold or by total revenue?
  1. quantity
  2. revenue
Your answer: 1

How many top products would you like to see?
  1. 5
  2. 10
  3. 20
  4. All
Your answer: 1

Final SQL used:
SELECT p.product_id, p.name, SUM(oi.quantity) AS total_quantity
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_id, p.name
ORDER BY total_quantity DESC, p.product_id ASC
LIMIT 5;

Answer: Your top-selling items by quantity are T-Shirt (6 units sold),
Mouse (2), Jeans (2), Laptop (1) and Mobile (1).
```

## Testing

```bash
# Unit tests
python -m unittest tests/test_conversation_service.py

# Error-recovery (mocked failure + retry loop), end-to-end
python -m tests.test_error_recovery

# 8 end-to-end scenarios (clear questions, single/multi-ambiguity,
# empty results, cross-table joins, a safety test, gibberish input)
python -m tests.test_all_scenarios
```

## Evaluation

The full methodology, results, and every bug found along the way are logged in [`evaluation/`](./evaluation), but the summary:

### Ambiguity detection accuracy

Run against 20 manually-labeled questions (`evaluation/dataset.json`):

| Metric | Result |
|---|---|
| Accuracy | 100% (20/20) |
| False negatives (missed real ambiguity — most dangerous) | 0 |
| False positives (flagged a clear question) | 0 |

**Caveat:** these questions were written with knowledge of the ambiguity prompt's design, so this likely overstates real-world generalization. A stronger version of this evaluation would run the same set 3× to check for consistency and add adversarial phrasing written independently of the prompt.

### Baseline vs. clarification system

The most informative result came from running the **baseline** (no clarification, raw question → SQL) on *"What are our top selling products?"* three times with identical input:

| Run | Behavior |
|---|---|
| 1, 2 | Ranked by quantity, `LIMIT 10`, Laptop excluded (tied at qty=1 with 9 others, no tie-breaker) |
| 3 | Ranked by quantity **and** computed revenue, no `LIMIT`, 13 products including Laptop — which by revenue ($1,200) actually ranks #1, but the baseline never surfaces this |

This single test exposed three separate silently-resolved ambiguities in the baseline: **which metric** defines "top," **how many** results count as "top," and **non-deterministic tie-breaking** — the same question returning different result *sets*, not just different order, across identical runs.

| | Baseline (no clarification) | This system |
|---|---|---|
| Ambiguity made explicit to user | No | Yes |
| Same question → same result, every run | No (tie-breaking was non-deterministic) | Yes (fixed) |
| Silent assumption bugs found | 3 | 0 (all surfaced as questions) |
| Case-sensitivity SQL bug (`'Completed'` vs `'completed'`) | Found — caused a silent $0 revenue result | Fixed via schema sample-value injection |

**Takeaway:** the risk with an un-clarified text-to-SQL system isn't only "wrong answers on hard questions" — it can return genuinely different results across identical runs of the same question, with no signal to the user that an assumption was ever made. Making ambiguity explicit trades a small amount of interaction friction for correctness and reproducibility.

## Known Limitations & Future Work

- **Conversation state is in-memory only** — fine for a single CLI session, would need persistence (DB/Redis) for a multi-user API.
- **LLM ambiguity detection is not perfectly consistent** — the same question can occasionally return a different number/wording of ambiguity dimensions across runs; a production version should sample multiple times or cache resolved intents per question pattern.
- **Seed scripts are not idempotent** — `seed_v2.py` must be run exactly once against a fresh database, or it duplicates rows.
- **Schema sample-value injection only covers low-cardinality columns** (≤10 distinct values) — free-text columns (names, emails) are intentionally excluded, but this means filters on other high-cardinality text fields could still hit similar casing issues.
- **Evaluation dataset is small (20 questions) and self-authored** — a stronger evaluation would include adversarial/edge-case questions written without knowledge of the prompt design, and multiple runs per question to measure consistency, not just single-shot accuracy.
- **No API layer yet** — currently a CLI (`main.py`); wrapping the pipeline in FastAPI would make it usable from a frontend.
### Phase 9 — API Layer, Step 1 & 2
- Built minimal FastAPI app (app/api/routes.py) with a POST /ask
  endpoint reusing check_ambiguity()
- Chose Postgres over Redis for session state (avoids adding a new
  external service) -- added conversation_sessions table using
  JSONB columns for ambiguities/resolutions
- Built session_service.py (create_session, get_session,
  add_resolution) using psycopg2.extras.Json for JSONB read/write
- Tested directly: session created, fetched, and resolution appended
  correctly, current_index incrementing as expected
  ### Phase 9 — API Layer ✅
- Built FastAPI app with session-based multi-turn clarification flow:
  POST /ask (starts flow, returns first ambiguity or final answer)
  and POST /answer (resolves current ambiguity, returns next one or
  final answer)
- Session state persisted in Postgres (conversation_sessions table,
  JSONB columns) instead of in-memory, so state survives server
  restarts
- Tested full multi-turn flow via /docs: "Show me the best customer"
  -> metric clarification -> time_range clarification -> final SQL
  + correct natural-language answer (Ahmed Khan, $1300)
  This demo runs against a single fixed dataset. Supporting user-uploaded data would require per-user database isolation and is out of scope for this demo.