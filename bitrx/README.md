# BitriX — HappyTuna Crisis Simulation

Agentic AI course project. An AI agent acts as CEO of HappyTuna and must manage a salmonella crisis.

## Quick start

```bash
# 1. Clone & enter the repo
git clone <your-repo-url>
cd bitrx

# 2. Copy and fill in your API key
cp .env.example .env

# 3. Start all services
docker compose up --build
```

## Services (your team)

| Service | URL | Description |
|---|---|---|
| NTP | http://localhost:8001 | Simulation clock |
| CRM | http://localhost:8002 | Customer & case records |
| News Website | http://localhost:8003 | Live news feed UI + API |
| Chroma DB | http://localhost:8000 | Agent memory / RAG |

## Time model

- **Speed:** 60× real time (1 real minute = 1 simulated hour)
- **Sim start:** Monday 10 June 2024, 08:00 UTC
- A simulated week passes in ~2.5 real hours

## Project structure

```
bitrx/
├── agents/
│   ├── journalist/        # LangChain — your team
│   └── regulator/         # NeMo — your team
├── systems/
│   ├── ntp/               # Simulation clock — your team
│   ├── crm/               # Customer records — your team
│   └── news-website/      # News feed — your team
├── chroma/                # Chroma DB seed data
├── docker-compose.yml
└── .env.example
```

## Environment variables

Copy `.env.example` to `.env` and fill in:

```
ANTHROPIC_API_KEY=your_key_here
```
