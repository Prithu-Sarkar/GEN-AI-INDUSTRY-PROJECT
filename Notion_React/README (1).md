# 🤖 Notion ReAct Planner Agent

A reasoning-driven daily planner powered by a hand-rolled **ReAct loop**, **Groq LLaMA 3.3**, and the **Notion API** — served via FastAPI with an optional ngrok tunnel for public access.

---

## Architecture

```
User Query
    │
    ▼
ManualReActAgent  ←── llama-3.3-70b-versatile (Groq)
    │
    ├── Thought → Action → Observation loop
    │
    ├─ get_weather          (Open-Meteo API)
    ├─ get_notes            (Notion Notes DB)
    ├─ add_note             (Notion Notes DB)
    ├─ get_calendar_events  (Notion Calendar DB)
    └─ add_calendar_event   (Notion Calendar DB)
    │
    ▼
FastAPI  ──►  POST /chat  |  GET /health  |  GET /
    │
    ▼
ngrok public URL (Colab) / localhost:8000 (local)
```

---

## Stack

| Layer | Technology |
|---|---|
| LLM | `llama-3.3-70b-versatile` via Groq |
| Agent | Custom ReAct loop (`ManualReActAgent`) |
| LLM Framework | `langchain-groq`, `langchain-core` |
| Databases | Notion API (Calendar + Notes) |
| Weather | Open-Meteo (no auth required) |
| API Server | FastAPI + Uvicorn |
| Tunnel | pyngrok |
| Tracking | MLflow + DagsHub (optional) |

---

## Setup

### 1. Colab Secrets

Add the following keys via the 🔑 sidebar:

```
GROQ_API_KEY
NOTION_API_KEY
NOTION_CALENDAR_DB_ID
NOTION_NOTES_DB_ID
NGROK_AUTHTOKEN        # optional, for public URL
MLFLOW_TRACKING_URI    # optional, for experiment tracking
```

### 2. Create Notion Databases

Run **Section 9** once to auto-create the Calendar and Notes databases inside a parent Notion page. Copy the printed IDs into Colab Secrets, then re-run Section 1.

> The parent page must have your Notion integration connected:  
> `··· → Add connections → select your integration`

### 3. Run All Cells Top-to-Bottom

| Section | What it does |
|---|---|
| 1 | Load env vars from Colab Secrets |
| 2 | Install dependencies |
| 3 | Logger utility |
| 4 | Weather tool |
| 5 | Notion Notes tool |
| 6 | Notion Calendar tool |
| 7 | ReAct agent (`ManualReActAgent`) |
| 8 | FastAPI server |
| 9 | Notion DB setup (run once) |
| 10 | Agent tests |
| 11 | Start server + ngrok tunnel |
| 12 | MLflow tracking (optional) |

---

## API

### `POST /chat`
```json
// Request
{ "message": "What's the weather in Delhi?" }

// Response
{ "response": "The current temperature in Delhi is 34°C." }
```

### `GET /health`
```json
{ "status": "ok" }
```

### `GET /`
Serves the built-in HTML chat UI.

---

## Example Queries

```
"What is the current temperature in Mumbai?"
"Add a note: review project proposal before Friday"
"What are my pending notes?"
"Schedule a 30-minute walk at 7 AM tomorrow"
"Plan my morning — check weather, add reminders, schedule my workout"
```

---

## ReAct Loop (Custom Implementation)

Because `langchain.agents.AgentExecutor` and `create_react_agent` are absent in this LangChain build (v1.2.x), the agent is implemented manually:

```python
class ManualReActAgent:
    def invoke(self, inputs):
        # Thought → Action → Observation loop
        # Parses LLM output with regex
        # Calls tools by name
        # Appends observations and re-prompts
        # Returns {"output": final_answer}
```

The `.invoke({"input": "..."})` interface is identical to `AgentExecutor`, so all test cells work without changes.

---

## Project Structure (Full Repo)

```
├── tools/
│   ├── weather.py
│   ├── notion_notes.py
│   └── notion_calendar.py
├── agent/
│   └── bot.py
├── api/
│   └── server.py
├── scripts/
│   ├── setup_notion_databases.py
│   └── test_agent.py
├── main.py
└── Notion_ReAct_Planner_Agent.ipynb
```

---

## Experiment Tracking (Optional)

MLflow runs are logged to DagsHub with:
- **Params:** query, response
- **Metrics:** latency (ms)
- **Tags:** model name, agent type

Set `MLFLOW_TRACKING_URI`, `MLFLOW_TRACKING_USERNAME`, and `MLFLOW_TRACKING_PASSWORD` in Colab Secrets to enable.

---

## License

MIT
