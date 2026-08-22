# Architecture

```
                    ┌─────────────┐
        goal ──────►│   Planner   │──────► subtasks[]
                    └─────────────┘
                                          │
                     ┌────────────────────┘
                     ▼
              ┌─────────────┐   tool calls   ┌───────────┐
              │   Worker    │◄──────────────►│  tools.py │
              └─────────────┘                └───────────┘
                     │  (one call per subtask, in order,
                     │   each sees prior results as context)
                     ▼
              subtask results[]
                     │
                     ▼
              ┌─────────────┐
              │  Reviewer   │──── PASS ────► done
              └─────────────┘
                     │
                   REVISE
                     │
                     ▼
          Planner.revise(goal, subtasks, feedback)
                     │
                     └──── loop, up to MAX_REVISION_LOOPS times
```

## Roles

- **Planner** (`agents/planner.py`) — turns a natural-language goal into a short ordered
  list of concrete subtasks. On a REVISE verdict, it re-plans using the reviewer's
  feedback plus the previous subtask list.
- **Worker** (`agents/worker.py`) — executes one subtask at a time. It may call a tool
  (see `tools.py`) by returning a small JSON envelope naming the tool and its input; the
  orchestrator does not call tools directly, the Worker's LLM call decides. Each worker
  call receives the results of prior subtasks as context, so later steps can build on
  earlier ones.
- **Reviewer** (`agents/reviewer.py`) — looks at the goal plus every subtask's result and
  returns a verdict (`PASS`/`REVISE`) with feedback explaining any gap.
- **Orchestrator** (`orchestrator.py`) — drives the loop: plan → run all subtasks →
  review → (if REVISE) re-plan and repeat, up to `MAX_REVISION_LOOPS` (default 2, set in
  `.env`). Emits events (`plan`, `subtask_done`, `review`, `replan`) so the CLI — or any
  other frontend — can stream progress.

## Why this shape

- **Provider-agnostic LLM calls**: `llm_client.py` only assumes an OpenAI-compatible
  `/chat/completions` endpoint, which both Groq's and OpenRouter's free tiers implement.
  Swapping providers is a config change, not a code change.
- **Prompt-based JSON tool calls instead of native function-calling**: not every free
  model reliably supports OpenAI-style function calling, but every chat model can be
  asked to emit a small JSON object. This trades a bit of robustness (the client retries
  and validates JSON) for working across whichever free model is available.
- **Minimal dependencies** (`requests`, `python-dotenv` only): keeps install size and
  memory footprint small enough for a free VPS's smallest instance tier.
