# BitriX — HappyTuna Crisis Simulation

Agentic AI course project. An AI agent acts as CEO of HappyTuna — a fictional $250M canned tuna company — and must manage a salmonella crisis in one of its production lines.

## Our team's responsibility

- **Journalist Agent** — investigates and publishes news (LangChain + Chroma DB)
- **Regulator Agent** — enforces food safety laws (NeMo + Chroma DB)
- **NTP System** — shared simulation clock for all agents
- **News Website** — The Daily Catch, external news feed

---

## Quick start

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd bitrx

# 2. Copy and fill in your API keys
cp .env.example .env

# 3. Start all systems
docker compose up --build ntp news-website chroma

# 4. In a second terminal — run the journalist agent
py -m agents.journalist.main
```

---

## Services

| Service | URL | Description |
|---|---|---|
| NTP | http://localhost:8001 | Simulation clock — shared by all agents |
| News Website | http://localhost:8003 | The Daily Catch — live news feed UI + API |
| Chroma DB | http://localhost:8000 | Agent memory / RAG knowledge base |
| BrightTweets | http://localhost:3005 | Social network — other team |

### Useful endpoints
- `http://localhost:8001/time` — current simulation time
- `http://localhost:8001/docs` — NTP API docs
- `http://localhost:8003` — The Daily Catch news site
- `http://localhost:8003/docs` — News Website API docs

---

## Time model

- **Speed:** 60× real time (1 real minute = 1 simulated hour)
- **Sim start:** Monday 10 June 2024, 08:00 UTC
- A simulated week passes in ~2.5 real hours

---

## Project structure

```
bitrx/
├── base/
│   ├── agent_base.py        # Abstract agent interface
│   ├── tool_base.py         # Abstract tool interface
│   ├── tool_agent.py        # ReAct loop engine (LangChain)
│   ├── memory_base.py       # Abstract memory interface
│   └── retriever_base.py    # Abstract retriever interface
│
├── services/
│   ├── llm_client.py        # Google Gemini LLM wrapper
│   ├── tool_executor.py     # Tool runner with retry logic
│   ├── embedding_service.py # Google embedding model
│   ├── document_store.py    # Chroma DB document store
│   ├── rag_pipeline.py      # RAG pipeline
│   └── vector_memory_store.py # In-memory vector store
│
├── agents/
│   ├── journalist/
│   │   ├── journalist_agent.py  # Main agent class
│   │   ├── prompts.py           # Personality & system hint
│   │   ├── main.py              # Local run entrypoint
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   ├── knowledge/           # Chroma DB seed documents
│   │   │   ├── crisis_management_theory.txt
│   │   │   ├── food_recall_procedures.txt
│   │   │   ├── happytuna_background.txt
│   │   │   └── happytuna_world_reference.txt
│   │   └── tools/
│   │       ├── publish_article.py   # POST to News Website
│   │       ├── search_news.py       # Search News Website
│   │       ├── search_knowledge.py  # Query Chroma DB
│   │       ├── send_email.py        # Send email to sources
│   │       ├── read_email.py        # Read inbox replies
│   │       └── post_social.py       # Post to BrightTweets
│   │
│   └── regulator/
│       └── ...                  # Coming in Sprint 2
│
├── systems/
│   ├── ntp/                 # Simulation time service
│   └── news-website/        # The Daily Catch news site
│
├── docker-compose.yml
├── requirements.txt         # Root requirements for local dev
└── .env.example
```

---

## Environment variables

Copy `.env.example` to `.env` and fill in:

```dotenv
# Required
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_EMBEDDING_MODEL=models/text-embedding-004

# Local development URLs
NTP_URL=http://localhost:8001
NEWS_URL=http://localhost:8003
CHROMA_HOST=localhost
CHROMA_PORT=8000
SOCIAL_URL=http://localhost:3005

# Journalist agent config
JOURNALIST_MODEL=gemini-2.0-flash
JOURNALIST_TEMPERATURE=0.2
JOURNALIST_MAX_STEPS=12
```

---

## Running the Journalist agent locally

Make sure Docker systems are running first:

```bash
docker compose up ntp news-website chroma
```

Then in a second terminal:

```bash
py -m agents.journalist.main
```

Type a crisis event to trigger the agent:
```
salmonella detected at HappyTuna Production Line A
```

The agent will investigate, publish an article to The Daily Catch, and post to BrightTweets automatically.

---

## Tech stack

- **LangChain** — Journalist agent ReAct loop
- **NeMo** — Regulator agent (Sprint 2)
- **Google Gemini** — LLM and embeddings
- **Chroma DB** — Agent knowledge base (RAG)
- **FastAPI** — NTP and News Website systems
- **SQLite** — News Website article storage
- **Docker** — All services containerized