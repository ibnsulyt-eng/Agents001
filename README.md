# Agents001

A minimal multi-agent orchestration demo: a **Planner** breaks a goal into subtasks, a
**Worker** executes each one (with access to simple tools), and a **Reviewer** checks the
combined output and sends it back for revision if it falls short.

Runs entirely on **free** infrastructure:
- **LLM**: [Groq](https://console.groq.com/keys)'s free-tier API by default (fast, generous
  limits, OpenAI-compatible). [OpenRouter](https://openrouter.ai/keys) free models work as a
  drop-in alternative — see `.env.example`.
- **Hosting**: designed to run on a free VPS (e.g. Oracle Cloud Always Free) rather than
  locally — see [docs/DEPLOY_VPS.md](docs/DEPLOY_VPS.md). Also runs directly on an
  Android phone via Termux — see [docs/DEPLOY_TERMUX.md](docs/DEPLOY_TERMUX.md).

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for how the agents fit together.

Also includes **TikTok Live monitoring** (`monitor_main.py`): watches a list of accounts'
live rooms in real time (comments, gifts, joins, likes), logs everything, and flags
spam/harassment/scams via free rule-based filters plus an LLM Monitor agent for the
ambiguous cases — see [docs/MONITORING.md](docs/MONITORING.md).

## Setup

1. Get a free API key:
   - Groq: https://console.groq.com/keys (sign up, create a key — no card required)
2. Copy `.env.example` to `.env` and paste your key in.
3. Install dependencies (on whichever machine will actually run this — see note below):
   ```
   pip install -r requirements.txt
   ```
4. Run it:
   ```
   python main.py "Plan a 3-day beginner itinerary for Tokyo"
   ```

> **Note:** this repo was scaffolded on a machine with nothing installed but Git — no
> Python/Node were added locally on purpose. Install dependencies and run the actual agent
> on your free VPS instead of this machine; see the deploy guide.

## Project layout

```
main.py                    Planner/Worker/Reviewer entrypoint
monitor_main.py            TikTok Live monitoring entrypoint
src/agents001/
  config.py                loads provider/model/keys from .env
  llm_client.py             HTTP client for Groq/OpenRouter (OpenAI-compatible)
  tools.py                  tools the Worker can call (calculator, notes)
  orchestrator.py            runs the Planner -> Worker -> Reviewer loop
  cli.py                    command-line entrypoint
  agents/
    planner.py
    worker.py
    reviewer.py
  monitor/
    config.py               watchlist/alerting config
    watcher.py               per-room TikTokLive connection
    runner.py                 batches events, runs rules + LLM triage
    rules.py                 free keyword/spam filters
    agent.py                 LLM Monitor agent (batched comment review)
    alerts.py                 Discord/Telegram webhook senders
    store.py                  SQLite event log
docs/
  ARCHITECTURE.md
  MONITORING.md
  DEPLOY_VPS.md
```

## Switching providers

Change `LLM_PROVIDER` in `.env` to `groq` or `openrouter` — both use the same request
format, so no code changes are needed.

## Extending

Add a new tool in `src/agents001/tools.py` (a plain function taking/returning strings),
register it in the `TOOLS` dict, and mention it in `TOOL_DESCRIPTIONS` so the Worker knows
it exists.
