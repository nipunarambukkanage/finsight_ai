# Assessment evidence map

| Requirement | Evidence |
|---|---|
| Task 1 two-year OHLCV and five indicators | `task1_financial/src/pipeline.py` |
| Task 1 structured sentiment and signal | `task1_financial/src/contracts.py`, `reasoning.py` |
| Task 1 report bonus | `task1_financial/src/render.py`, `run_pipeline.py` |
| Task 2 domain use case and teacher prompt | `task2_genai/src/prompts.py`, `contracts.py` |
| Task 2 dataset validation and split | `task2_genai/src/dataset.py` |
| Task 2 QLoRA and merge | `task2_genai/src/training.py` |
| Task 2 held-out metrics | `task2_genai/src/evaluation.py` |
| Task 3 five tools and role restrictions | `task3_agentic/src/tools.py` |
| Task 3 autonomous and coordinated runs | `task3_agentic/src/agent.py` |
| Task 3 cache and tool trace | `task3_agentic/src/tracing.py`, `task3_agentic/logs/agent_trace.jsonl` |
| Versioned application filing-risk and evaluation interfaces | `backend/app/api/v1/assessment.py` |
| Durable run idempotency, leases, replayable SSE | `backend/app/api/v1/runs.py`, `backend/app/persistence/runs.py` |
| AI and external-source citations | `CITATIONS.md` |
| Architectural reflection | `REFLECTION.md` |

The committed trace is a schema fixture. It must be regenerated from the executed notebook before submission so the reviewer sees real tool inputs, outputs, and durations.
